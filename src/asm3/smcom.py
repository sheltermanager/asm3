
import asm3.al
import asm3.cachedisk
import asm3.db

from asm3.sitedefs import MULTIPLE_DATABASES, MULTIPLE_DATABASES_TYPE
from asm3.typehints import Database, Dict

from datetime import datetime
import re
import os, sys

import web062 as web

# The maximum number of emails allowed to be sent over a period (ttl)
# through the the sheltermanager.com email server
MAX_EMAILS_CACHE_KEY = "emails_sent"
MAX_EMAILS_TTL = 3600 * 12 # Use a 12 hour reset period
MAX_EMAILS = 3000

# Regex to remove invalid chars from an entered database
INVALID_REMOVE = re.compile(r'[\/\.\*\?\ ]')

try:
    sys.path.append("/root/asmdb")
    import smcom_client
except:
    # sys.stderr.write("warn: no smcom_client\n")
    pass

def active() -> bool:
    """
    Returns true if we're sheltermanager.com
    """
    return MULTIPLE_DATABASES and MULTIPLE_DATABASES_TYPE == "smcom"

def is_master_user(user: str, dbname: str) -> bool:
    """
    Returns True if user is the master user 
    """
    if not active(): return False
    return user == dbname

def get_account(alias: str) -> Dict:
    """
    Returns the smcom account object for alias/db
    Uses a read through 24 hour cache to save unnecessary calls
    """
    # Attackers have tried to overflow alias in the past, we'll never use more than 20 chars
    # fail fast and save us a load of processing.
    if len(alias) > 20: return None     
    TTL = 86400
    cachekey = "smcom_dbinfo_%s" % alias
    a = asm3.cachedisk.get(cachekey, "smcom")
    if a is None:
        a = smcom_client.get_account(alias)
        if a is not None and "user" in a:
            asm3.cachedisk.put(cachekey, "smcom", a, TTL)
    return a

def get_database_info(alias: str) -> Database:
    """
    Returns the dbo object for a sheltermanager.com account or alias.  
    Also returns a dbo with a database property of "DISABLED" for a 
    disabled account, "FAIL" for a problem or "WRONGSERVER" to indicate
    that the database does not exist on this server.
    """
    alias = re.sub(INVALID_REMOVE, '', alias).lower()
    dbo = asm3.db.get_dbo("POSTGRESQL")
    dbo.host = "/var/run/postgresql/" # use socket dir to use UNIX sockets to connect to local pgbouncer /var/run/postgresql/
    dbo.port = 6432
    dbo.dbtype = "POSTGRESQL"
    dbo.alias = alias

    a = get_account(alias)
    if a is None:
        dbo.database = "FAIL"
        return dbo

    dbo.database = a["user"]
    dbo.username = dbo.database
    dbo.password = dbo.database

    # dbo.alias is used in particular when sending emails to make a friendlier
    # bounce address. If the account has one, set it here. We used to just set
    # this on login above, but if they logged in with their account number the 
    # alias was not set.
    if a["alias"] != "":
        dbo.alias = a["alias"]

    # Is this sm.com account disabled or removed from the server?
    if a["expired"] or a["archived"]:
        dbo.database = "DISABLED"

    # Is this the wrong server?
    if smcom_client.get_this_server() != a["server"]: 
        dbo.database = "WRONGSERVER"
        asm3.al.error("failed login, wrong server: %s not present in %s" % (a["server"], smcom_client.get_this_server()))

    return dbo

def check_bulk_email(dbo: Database, count: int) -> None:
    """
    Call before sending a bulk email (mail merge)
    count: The number of emails that are about to be sent.
    Checks how many emails have been sent in the period along with how many are about to be sent.
    If the limit would be crossed, an exception is raised, otherwise returns nothing.
    The count is added to the number of emails sent for next time.
    """
    sent = get_emails_sent(dbo)
    if (sent + count) > MAX_EMAILS:
        raise SmcomError(f"{sent} emails have been sent in the last {MAX_EMAILS_TTL/3600} hours. " \
            f"The limit for the period is {MAX_EMAILS}. Cannot send a further {count} emails.")
    else:
        add_emails_sent(dbo, count)

def get_emails_sent(dbo: Database) -> int:
    """
    Returns the number of emails sent in the ttl period
    """
    count = asm3.cachedisk.get(MAX_EMAILS_CACHE_KEY, dbo.name(), int)
    if count is None: count = 0
    return count

def add_emails_sent(dbo: Database, sent: int) -> int:
    """
    sent: Add to our running count of emails sent 
    returns the total emails sent in the ttl period
    """
    count = asm3.cachedisk.get(MAX_EMAILS_CACHE_KEY, dbo.name(), int)
    if count is None: count = 0
    count = count + sent
    asm3.cachedisk.put(MAX_EMAILS_CACHE_KEY, dbo.name(), count, MAX_EMAILS_TTL)
    return count

def clear_emails_sent(dbo: Database) -> None:
    """
    Removes the cached value of emails sent. Used by unit tests.
    """
    asm3.cachedisk.delete(MAX_EMAILS_CACHE_KEY, dbo.name())

def get_expiry_date(dbo: Database) -> datetime:
    """
    Returns the account expiry date or None for a problem.
    """
    a = get_account(dbo.database)
    try:
        expiry = datetime.strptime(a["expiry"], "%Y-%m-%d")
        asm3.al.debug("retrieved account expiry date: %s" % expiry, "smcom.get_expiry_date", dbo)
        return expiry
    except:
        return None

def get_login_url(dbo: Database) -> str:
    """
    Returns the login url for this account
    """
    return "https://sheltermanager.com/login/%s" % dbo.alias or dbo.database

def get_payments_url() -> str:
    """
    Returns the url to use for callbacks from payment processors
    """
    return "https://service.sheltermanager.com/asmpayment"

def go_smcom_my(dbo: Database) -> None:
    """
    Goes to the my account page for this database
    """
    raise web.seeother(smcom_client.get_my_url(dbo.database))

def iptables_rules() -> str:
    try:
        return asm3.utils.bytes2str(asm3.utils.cmd("/root/asmdb/iptables_rules", shell=True)[1])
    except:
        return ""

def vacuum_full(dbo: Database) -> None:
    """ Performs a full vacuum on the database via command line (transaction problems via db.py) """
    os.system("psql -U %s -c \"VACUUM FULL;\"" % dbo.database)

class SmcomError(web.HTTPError):
    """
    Custom error thrown by data modules 
    """
    msg = ""
    def __init__(self, msg: str) -> None:
        self.msg = msg
        status = '500 Internal Server Error'
        headers = { 'Content-Type': "text/html" }
        data = "<h1>Error</h1><p>%s</p>" % msg
        if "headers" not in web.ctx: web.ctx.headers = []
        web.HTTPError.__init__(self, status, headers, data)
