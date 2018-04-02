#!/usr/bin/python

import i18n
import utils

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

def add_log(dbo, username, linktype, linkid, logtypeid, logtext):
    return dbo.insert("log", {
        "LogTypeID":        logtypeid,
        "LinkID":           linkid,
        "LinkType":         linktype,
        "Date":             dbo.now(),
        "Comments":         logtext
    }, username)

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
        raise utils.ASMValidationError(i18n._("Log date must be a valid date", l))

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
        raise utils.ASMValidationError(i18n._("Log date must be a valid date", l))

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

