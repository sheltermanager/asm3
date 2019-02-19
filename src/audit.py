#!/usr/bin/python

import al
import i18n

ADD = 0
EDIT = 1
DELETE = 2
MOVE = 3
LOGIN = 4
LOGOUT = 5

def get_audit_for_link(dbo, tablename, linkid):
    """ Returns the audit records for a particular link and table """
    parentlinks = "%%%s=%s %%" % (tablename, linkid)
    return dbo.query("SELECT * FROM audittrail WHERE (tablename = ? AND linkid = ?) OR parentlinks LIKE ? ORDER BY AuditDate DESC", (tablename, linkid, parentlinks))

def get_parent_links(v):
    """ Reads a dict of values (insert/update values or delete resultrow) and 
        turns foreign keys from certain tables into values for the audittrail.ParentLinks 
        field (eg: AnimalID, OwnerID for an output of 'animal=X owner=Y ') """
    pl = []
    for k, v in v.iteritems():
        if k.lower() in ( "animalid", "ownerid", "animalcontrolid" ):
            pl.append( "%s=%s " % ( k.lower().replace("id", ""), v ))
    return "".join(pl)

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
    return str(dbo.query("SELECT * FROM %s WHERE %s" % (tablename, condition)))

def create(dbo, username, tablename, linkid, parentlinks, description):
    action(dbo, ADD, username, tablename, linkid, parentlinks, description)

def edit(dbo, username, tablename, linkid, parentlinks, description):
    action(dbo, EDIT, username, tablename, linkid, parentlinks, description)

def delete(dbo, username, tablename, linkid, parentlinks, description):
    action(dbo, DELETE, username, tablename, linkid, parentlinks, description)

def delete_rows(dbo, username, tablename, condition):
    rows = dbo.query("SELECT * FROM %s WHERE %s" % (tablename, condition))
    # If there's an ID column, log an audited delete for each row
    if len(rows) > 0 and "ID" in rows[0]:
        for r in dbo.query("SELECT * FROM %s WHERE %s" % (tablename, condition)):
            action(dbo, DELETE, username, tablename, r["ID"], get_parent_links(r), dump_row(dbo, tablename, r["ID"]))
    else:
        # otherwise, stuff all the deleted rows into one delete action
        action(dbo, DELETE, username, tablename, 0, "", str(rows))

def move(dbo, username, tablename, linkid, parentlinks, description):
    action(dbo, MOVE, username, tablename, linkid, parentlinks, description)

def login(dbo, username, remoteip = ""):
    action(dbo, LOGIN, username, "users", 0, "", "login from %s" % remoteip)

def logout(dbo, username, remoteip = ""):
    action(dbo, LOGOUT, username, "users", 0, "", "logout from %s" % remoteip)

def action(dbo, action, username, tablename, linkid, parentlinks, description):
    """
    Adds an audit record
    """
    # Truncate description field to 16k if it's very long
    if len(description) > 16384:
        description = description[0:16384]

    dbo.insert("audittrail", {
        "Action":       action,
        "AuditDate":    dbo.now(),
        "UserName":     username,
        "TableName":    tablename,
        "LinkID":       linkid,
        "ParentLinks":  parentlinks,
        "Description":  description
    }, generateID=False, writeAudit=False)

def clean(dbo):
    """
    Deletes audit trail records older than three months
    """
    d = i18n.subtract_days(i18n.now(), 93)
    count = dbo.query_int("SELECT COUNT(*) FROM audittrail WHERE AuditDate < ?", [ d ])
    al.debug("removing %d audit records older than 93 days." % count, "audit.clean", dbo)
    dbo.execute("DELETE FROM audittrail WHERE AuditDate < ?", [ d ])

