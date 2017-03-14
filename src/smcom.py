#!/usr/bin/python

import al
import datetime
import db
import re
import utils
import os, sys
import web
from sitedefs import MULTIPLE_DATABASES, MULTIPLE_DATABASES_TYPE

# Regex to remove invalid chars from an entered database
INVALID_REMOVE = re.compile('[\/\.\*\?]')

sys.path.append("/root/asmdb")
try:
    import smcom_client
except:
    # sys.stderr.write("warn: no smcom_client\n")
    pass

def active():
    """
    Returns true if we're sheltermanager.com
    """
    return MULTIPLE_DATABASES and MULTIPLE_DATABASES_TYPE == "smcom"

def get_database_info(alias):
    """
    Returns the dbo object for a sheltermanager.com account or alias.  
    Also returns a dbo with a database property of "DISABLED" for a 
    disabled account, "FAIL" for a problem or "WRONGSERVER" to indicate
    that the database does not exist on this server.
    """
    alias = re.sub(INVALID_REMOVE, '', alias).lower()
    dbo = db.DatabaseInfo()
    dbo.host = "/var/run/postgresql/" # use socket dir to use UNIX sockets to connect to local pgbouncer /var/run/postgresql/
    dbo.port = 6432
    dbo.dbtype = "POSTGRESQL"
    dbo.alias = alias
    a = _get_account_info(alias)
    if a is None or "user" not in a:
        dbo.database = "FAIL"
        return dbo
    dbo.database = str(a["user"])
    dbo.username = dbo.database
    dbo.password = dbo.database
    # Is this sm.com account disabled?
    if a["expired"]:
        dbo.database = "DISABLED"
    # Is this the wrong server?
    if smcom_client.get_this_server() != a["server"]: 
        dbo.database = "WRONGSERVER"
        al.error("failed login, wrong server: %s not present in %s" % (a["server"], smcom_client.get_this_server()))
    return dbo

def get_expiry_date(dbo):
    """
    Returns the account expiry date or None for a problem.
    """
    a = _get_account_info(dbo.database)
    try:
        expiry = datetime.datetime.strptime(a["expiry"], "%Y-%m-%d")
        al.debug("retrieved account expiry date: %s" % expiry, "smcom.get_expiry_date", dbo)
        return expiry
    except:
        return None

def _get_account_info(alias):
    """
    Returns the account file info as a dictionary.
    Returns None if the account doesn't exist.
    """
    return smcom_client.get_account(alias)

def go_smcom_my(dbo):
    """
    Goes to the my account page for this database
    """
    raise web.seeother(smcom_client.get_my_url(dbo.database))

def set_last_connected(dbo):
    """
    Sets the last connected date on a database to today
    """
    al.debug("Setting last connected to now for %s" % dbo.database, "smcom.set_last_connected", dbo)
    response = smcom_client.update_last_connected(dbo.database)
    if response != "OK":
        al.error("Failed setting last connection: %s" % response, "smcom.set_last_connected", dbo)

def vacuum_full(dbo):
    """ Performs a full vacuum on the database via command line (transaction problems via db.py) """
    os.system("psql -U %s -c \"VACUUM FULL;\"" % dbo.database)

def route_customer_extension(dbo, when, caller, post):
    target = dbo.database + "_" + when + "_" + caller
    method = globals().get(target)
    if method:
        return method(dbo, post)
    else:
        return True

# -- Everything below are extensions for specific customers
def rp0282_before_insert_animal_from_form(dbo, post):
    if post.integer("originalowner") == 0 or post.integer("broughtinby") == 0:
        raise utils.ASMValidationError("Original Owner and Brought In By must be set")
    return True


