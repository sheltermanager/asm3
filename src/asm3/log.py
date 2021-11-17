
import asm3.i18n
import asm3.utils

# Log links
ANIMAL = 0
PERSON = 1
LOSTANIMAL = 2
FOUNDANIMAL = 3
WAITINGLIST = 4
MOVEMENT = 5
ANIMALCONTROL = 6

ASCENDING = 0
DESCENDING = 1

def add_log(dbo, username, linktype, linkid, logtypeid, logtext, logdatetime = None):
    """
    Adds a log entry. If logdatetime is blank, the date/time now is used.
    """
    if logdatetime is None: logdatetime = dbo.now()
    return dbo.insert("log", {
        "LogTypeID":        logtypeid,
        "LinkID":           linkid,
        "LinkType":         linktype,
        "Date":             logdatetime,
        "Comments":         logtext
    }, username)

def add_log_email(dbo, username, linktype, linkid, logtypeid, to, subject, body):
    """
    Adds a log entry for recording a sent email.
    body is converted to plain text if necessary before storing in the log.
    """
    if body.find("<p") != -1: body = asm3.utils.html_to_text(body)
    add_log(dbo, username, linktype, linkid, logtypeid,
        "[%s] %s ::\n%s" % ( to, subject, body ))

def get_log_find_simple(dbo, q, limit = 0):
    """
    Searches log notes for the term q
    Will return no results if the search term is less than 4 chars 
    """
    if len(q) < 4: return []
    q = "%%%s%%" % q.lower()
    sep = "' - '"
    query = "SELECT Comments, LogTypeName, LinkID, LastChangedDate, " \
        "CASE " \
        "WHEN LinkType=0 THEN 'animal' " \
        "WHEN LinkType=1 THEN 'person' " \
        "WHEN LinkType=2 THEN 'lostanimal' " \
        "WHEN LinkType=3 THEN 'foundanimal' " \
        "WHEN LinkType=4 THEN 'waitinglist' " \
        "WHEN LinkType=6 THEN 'incident' ELSE '' END AS RecordType, " \
        "CASE " \
        "WHEN LinkType=0 THEN " \
        f"(SELECT {dbo.sql_concat(['AnimalName', sep, 'ShelterCode'])} FROM animal WHERE animal.ID=log.LinkID) " \
        "WHEN LinkType=1 THEN " \
        f"(SELECT {dbo.sql_concat(['OwnerName', sep,'OwnerCode'])} FROM owner WHERE owner.ID=log.LinkID) " \
        "WHEN LinkType=2 THEN " \
        f"(SELECT {dbo.sql_concat(['OwnerName', sep, 'animallost.ID'])} FROM animallost " \
            "INNER JOIN owner ON owner.ID=animallost.OwnerID WHERE animallost.ID=log.LinkID) " \
        "WHEN LinkType=3 THEN " \
        f"(SELECT {dbo.sql_concat(['OwnerName', sep, 'animalfound.ID'])} FROM animalfound " \
            "INNER JOIN owner ON owner.ID=animalfound.OwnerID WHERE animalfound.ID=log.LinkID) " \
        "WHEN LinkType=4 THEN " \
        f"(SELECT {dbo.sql_concat(['OwnerName', sep, 'animalwaitinglist.ID'])} FROM animalwaitinglist " \
            "INNER JOIN owner ON owner.ID=animalwaitinglist.OwnerID WHERE animalwaitinglist.ID=log.LinkID) " \
        "WHEN LinkType=6 THEN " \
        f"(SELECT {dbo.sql_concat(['OwnerName', sep, 'animalcontrol.ID'])} FROM animalcontrol " \
            "INNER JOIN owner ON owner.ID=animalcontrol.OwnerID WHERE animalcontrol.ID=log.LinkID) " \
        "ELSE '' END AS RecordDetail " \
        "from log " \
        "INNER JOIN logtype ON logtype.ID = log.LogTypeID " \
        "WHERE LOWER(Comments) LIKE ?"
    return dbo.query(query, [q], limit=limit)

def get_logs(dbo, linktypeid, linkid, logtype = 0, sort = DESCENDING):
    """
    Gets a list of logs. <= 0 = all types.
    """
    sql = "SELECT l.*, lt.LogTypeName FROM log l " \
        "INNER JOIN logtype lt ON lt.ID = l.LogTypeID " \
        "WHERE LinkType = %d AND LinkID = %d " % (linktypeid, linkid)
    if logtype > 0:
        sql += "AND l.LogTypeID = %d " % logtype
    if sort == ASCENDING:
        sql += "ORDER BY l.Date"
    if sort == DESCENDING:
        sql += "ORDER BY l.Date DESC"
    return dbo.query(sql)

def insert_log_from_form(dbo, username, linktype, linkid, post):
    """
    Creates a log from the form data
    username: User creating the diary
    linktypeid, linkid: The link
    data: The web.py form object
    """
    l = dbo.locale
    if post.date("logdate") is None:
        raise asm3.utils.ASMValidationError(asm3.i18n._("Log date must be a valid date", l))

    return dbo.insert("log", {
        "LogTypeID":        post.integer("type"),
        "LinkID":           linkid,
        "LinkType":         linktype,
        "Date":             post.datetime("logdate", "logtime"),
        "Comments":         post["entry"]
    }, username)

def update_log_from_form(dbo, username, post):
    """
    Updates a log from form data
    """
    l = dbo.locale
    if post.date("logdate") is None:
        raise asm3.utils.ASMValidationError(asm3.i18n._("Log date must be a valid date", l))

    dbo.update("log", post.integer("logid"), {
        "LogTypeID":    post.integer("type"),
        "Date":         post.datetime("logdate", "logtime"),
        "Comments":     post["entry"]
    }, username)

def delete_log(dbo, username, logid):
    """
    Deletes a log
    """
    dbo.delete("log", logid, username)

