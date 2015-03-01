#!/usr/bin/python

import al
import datetime
import db
import os
import re
from sitedefs import MULTIPLE_DATABASES, MULTIPLE_DATABASES_TYPE

# Regex to remove invalid chars from an entered database
INVALID_REMOVE = re.compile('[\/\.\*\?]')

def active():
    """
    Returns true if we're sheltermanager.com
    """
    return MULTIPLE_DATABASES and MULTIPLE_DATABASES_TYPE == "smcom"

def get_database_info(alias):
    """
    Returns the dbo object for a sheltermanager.com account or alias.  
    Also returns a dbo with a database property of "DISABLED" for a 
    disabled account, or "FAIL" for a problem.
    """
    alias = re.sub(INVALID_REMOVE, '', alias)
    dbo = db.DatabaseInfo()
    dbo.host = "localhost"
    dbo.port = 6432
    dbo.dbtype = "POSTGRESQL"
    dbo.alias = alias
    dbo.database = resolve_alias(alias)
    # Make sure we have the matching sm.com account
    info = _get_account_info(alias)
    if info is None:
        # We didn't find the database they specified
        dbo.database = "FAIL"
        return dbo
    for l in info:
        if l.startswith("User:"): dbo.username = l.split(":")[1].strip()
        if l.startswith("Pass:"): dbo.password = l.split(":")[1].strip()
        # They're using ASM2 as well, the primarykey table needs
        # updating and we can't store pk values in memcache
        if l.startswith("ThreeOnly:") and l.find("No") != -1:
            dbo.has_asm2_pk_table = True
        # Is this sm.com account disabled?
        if l.startswith("Expired:") and l.find("Yes") != -1: 
            dbo.database = "DISABLED"
    return dbo

def get_expiry_date(dbo):
    """
    Returns the account expiry date or None for a problem.
    """
    info = _get_account_info(dbo.database)
    for l in info:
        if l.startswith("Expiry:"): 
            exp = l.split(":")[1].strip()
            try:
                return datetime.datetime.strptime(exp, "%Y-%m-%d")
            except:
                return None
    return None

def _get_account_info(alias):
    """
    Returns the account file info as a list of strings.
    Returns None if the account doesn't exist.
    """
    alias = re.sub(INVALID_REMOVE, '', alias)
    alias = resolve_alias(alias)
    if os.path.exists("/root/pg_users/%s" % alias):
        f = open("/root/pg_users/%s" % alias)
        lines = f.readlines()
        f.close()
        return lines
    return None

def resolve_alias(alias):
    """
    Resolves a sheltermanager alias to an account
    (eg: mycatrescue -> cr0215). 
    If the alias isn't found, we just return the alias, 
    assuming it to already be the account number.
    """
    s = os.popen("grep -li 'Alias: %s$' /root/pg_users/*" % alias).read().strip()
    if s == "": return alias
    if s.find("\n") != -1: s = s[0:s.find("\n")]
    return s[s.rfind("/")+1:]

def set_last_connected(dbo):
    """
    Sets the last connected date on a database to today
    """
    al.debug("Setting last connected to now for %s" % dbo.database, "users.web_login", dbo)
    os.system("sudo /root/sheltermanager_setlastconnected.py %s &" % dbo.database)


