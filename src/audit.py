#!/usr/bin/python

import al
import db
import i18n

ADD = 0
EDIT = 1
DELETE = 2
MOVE = 3
LOGIN = 4
LOGOUT = 5

def get_audit_for_link(dbo, tablename, linkid):
    """ Returns the audit records for a particular link and table """
    return db.query(dbo, "SELECT * FROM audittrail WHERE tablename = %s AND linkid = %s ORDER BY AuditDate DESC" % (db.ds(tablename), db.di(linkid)))

def map_diff(row1, row2, ref = []):
    """
    For two maps, return a string containing the differences. Useful for 
    showing what changed when auditing.
    If the passed in values are not dictionaries, it will assume they are
    lists and that the first element contains a dictionary. If the list
    is empty, an empty dict will be used for comparison.
    if ref is set, output those fields (if available) from row1
    """
    if type(row1) is not dict:
        if len(row1) > 0: 
            row1 = row1[0]
        else:
            row1 = {}
    if type(row2) is not dict:
        if len(row2) > 0:
            row2 = row2[0]
        else:
            row2 = {}
    s = ""
    if "ID" in row1:
        s = "(ID %d) " % row1["ID"]
    for rv in ref:
        if rv in row1:
            s += str(row1[rv]) + " "
    s += ">>> "
    for k, v in row1.iteritems():
        if k in row2:
            if str(row1[k]) != str(row2[k]):
                s += k + ": " + str(row1[k]) + " ==> " + str(row2[k]) + ", "
        else:
            s += k + " removed, "
    return s

def dump_row(dbo, tablename, rowid):
    return dump_rows(dbo, tablename, "ID = %s" % rowid)

def dump_rows(dbo, tablename, condition):
    return str(db.query(dbo, "SELECT * FROM %s WHERE %s" % (tablename, condition)))

def create(dbo, username, tablename, linkid, description):
    action(dbo, ADD, username, tablename, linkid, description)

def edit(dbo, username, tablename, linkid, description):
    action(dbo, EDIT, username, tablename, linkid, description)

def delete(dbo, username, tablename, linkid, description):
    action(dbo, DELETE, username, tablename, linkid, description)

def delete_rows(dbo, username, tablename, condition):
    for r in db.query(dbo, "SELECT * FROM %s WHERE %s" % (tablename, condition)):
        action(dbo, DELETE, username, tablename, r["ID"], dump_row(dbo, tablename, r["ID"]))

def move(dbo, username, tablename, linkid, description):
    action(dbo, MOVE, username, tablename, linkid, description)

def login(dbo, username, remoteip = ""):
    action(dbo, LOGIN, username, "users", 0, "login from %s" % remoteip)

def logout(dbo, username, remoteip = ""):
    action(dbo, LOGOUT, username, "users", 0, "logout from %s" % remoteip)

def action(dbo, action, username, tablename, linkid, description):
    """
    Adds an audit record
    """
    # Truncate description field to 16k if it's very long
    if len(description) > 16384:
        description = description[0:16384]

    sql = db.make_insert_sql("audittrail", (
        ( "Action", db.ds(action) ),
        ( "AuditDate", db.ddt(i18n.now(dbo.timezone)) ),
        ( "UserName", db.ds(username) ),
        ( "TableName", db.ds(tablename) ),
        ( "LinkID", db.di(linkid) ),
        ( "Description", db.ds(description) )
    ))
    db.execute(dbo, sql)

def clean(dbo):
    """
    Deletes audit trail records older than three months
    """
    d = db.today()
    d = i18n.subtract_days(d, 93)
    count = db.query_int(dbo, "SELECT COUNT(*) FROM audittrail WHERE AuditDate< %s" % db.dd(d))
    al.debug("removing %d audit records older than 93 days." % count, "audit.clean", dbo)
    db.execute(dbo, "DELETE FROM audittrail WHERE AuditDate < %s" % db.dd(d))

