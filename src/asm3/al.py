
from asm3.sitedefs import LOG_LOCATION, LOG_DEBUG

import logging
import logging.handlers
import traceback

logger = logging.getLogger("ASM3")
logger.setLevel(logging.DEBUG)

if LOG_LOCATION == "stderr":
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
elif LOG_LOCATION == "syslog":
    handler = logging.handlers.SysLogHandler(address = "/dev/log", facility = logging.handlers.SysLogHandler.LOG_LOCAL3)
    formatter = logging.Formatter("%(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
elif LOG_LOCATION == "ntevent":
    handler = logging.handlers.NTEventLogHandler("ASM3")
    logger.addHandler(handler)
else: 
    handler = logging.FileHandler(LOG_LOCATION, mode="a")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def fixed_chars(s: str, chars: int = 10):
    # Forces a string to be chars in length by padding or truncating
    if len(s) > chars:
        s = s[0:chars]
    elif len(s) < chars:
        s = s + " " * (chars-len(s))
    return s

def debug(msg: str, location: str = "[]", dbo = None):
    if LOG_DEBUG:
        logmsg(0, msg, location, dbo)

def info(msg: str, location: str = "[]", dbo = None):
    logmsg(1, msg, location, dbo)

def warn(msg: str, location: str = "[]", dbo = None):
    logmsg(2, msg, location, dbo)

def error(msg: str, location: str = "[]", dbo = None, ei = None):
    """
    Log an error
    ei: Exception info from sys.exc_info() for stacktrace
    """
    lines = []
    if ei is not None and len(ei) == 3:
        lines = traceback.format_exception(ei[0], ei[1], ei[2])
        if lines[0].startswith("Traceback"): lines = lines[1:] # Remove redundant first line if present
        msg += " " + " ".join(x.strip() for x in lines)
    logmsg(3, msg, location, dbo)

def logmsg(mtype: str, msg: str, location: str, dbo):
    # Prepend location
    msg = "%s %s" % (fixed_chars(location, 30), msg)
    # If we have a dbo, prepend the database name to the message
    if dbo is not None:
        dbname = ""
        if type(dbo) == str: 
            dbname = dbo
        else: 
            dbname = dbo.database
        msg = "%s %s" % (fixed_chars(dbname, 6), msg)
    # Restrict message to a max of 1024 chars to prevent "Message too long" exceptions
    if len(msg) > 1024: msg = msg[0:1024]
    try:
        if mtype == 0:
            logger.debug(msg)
        elif mtype == 1:
            logger.info(msg)
        elif mtype == 2:
            logger.warn(msg)
        elif mtype == 3:
            logger.critical(msg)
    except:
        print(msg)


