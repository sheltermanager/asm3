#!/usr/bin/python

import logging
import logging.handlers
import traceback
import utils
from sitedefs import LOG_LOCATION, LOG_DEBUG

logger = logging.getLogger("ASM3")
logger.setLevel(logging.DEBUG)

if LOG_LOCATION == "stderr":
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
elif LOG_LOCATION == "syslog":
    handler = logging.handlers.SysLogHandler(address = "/dev/log", facility = logging.handlers.SysLogHandler.LOG_USER)
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

def fixed_chars(s, chars=10):
    # Forces a string to be chars in length by padding or truncating
    if len(s) > chars:
        return utils.truncate(s, chars)
    if len(s) < chars:
        return utils.spaceright(s, chars)
    return s

def debug(msg, location = "[]", dbo = None):
    if LOG_DEBUG:
        logmsg(0, msg, location, dbo)

def info(msg, location = "[]", dbo = None):
    logmsg(1, msg, location, dbo)

def warn(msg, location = "[]", dbo = None):
    logmsg(2, msg, location, dbo)

def error(msg, location = "[]", dbo = None, ei=None):
    """
    Log an error
    ei: Exception info from sys.exc_info() for stacktrace
    """
    lines = []
    if ei != None:
        lines = traceback.format_exception(*ei)
        if ei[2]: 
            lines[1:1] = traceback.format_stack(ei[2].tb_frame.f_back)
    msg += " " + "".join(lines)
    logmsg(3, msg, location, dbo)

def logmsg(mtype, msg, location, dbo):
    msg = str(msg)
    # Prepend location
    msg = fixed_chars(location, 30) + " " + msg
    # If we have a dbo, prepend the database name to the message
    if dbo != None:
        msg = fixed_chars(dbo.database, 6) + " " + msg
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
        print msg


