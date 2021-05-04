
import asm3.al

ADD = 0
EDIT = 1
DELETE = 2
MOVE = 3
LOGIN = 4
LOGOUT = 5
VIEW_RECORD = 6
VIEW_REPORT = 7
EMAIL = 8

# How many days to retain records in the audittrail table before removing them
RETAIN_AUDIT_RECORDS = -182

# How many days to retain records in the deletion table before removing them
RETAIN_DELETION_RECORDS = -182

# The columns from these tables that are human readable references so
# that when map_diff is called we can show something more legible than
# just the record's ID number to help the user identify it.
READABLE_FIELDS = {
    "accounts":     [ "CODE", "DESCRIPTION" ],
    "accountstrx":  [ "DESCRIPTION" ],
    "additionalfield": [ "FIELDNAME" ],
    "animal":       [ "ANIMALNAME", "SHELTERCODE", "SHORTCODE" ],
    "customreport": [ "TITLE" ],
    "owner":        [ "OWNERNAME" ],
    "role":         [ "ROLENAME" ],
    "users":        [ "USERNAME", "REALNAME" ]
}

def get_audit_for_link(dbo, tablename, linkid):
    """ Returns the audit records for a particular link and table """
    parentlinks = "%%%s=%s %%" % (tablename, linkid)
    return dbo.query("SELECT * FROM audittrail WHERE (tablename = ? AND linkid = ?) OR parentlinks LIKE ? ORDER BY AuditDate DESC", (tablename, linkid, parentlinks))

def get_parent_links(row, tablename = ""):
    """ Reads a dict of values (insert/update values or delete resultrow) and 
        turns foreign keys from certain tables into values for the audittrail.ParentLinks 
        field (eg: AnimalID, OwnerID for an output of 'animal=X owner=Y ') """
    pl = []
    # Make values an upper-case key copy of row, since query values can be
    # camel case and result rows are upper case
    values = dict( (k.upper(),v) for k,v in row.items())
    for k, v in values.items():
        if k in ( "ANIMALID", "OWNERID", "ANIMALCONTROLID" ):
            pl.append( "%s=%s " % ( k.lower().replace("id", ""), v ))
    if tablename == "media" and "LINKTYPEID" in values and "LINKID" in values:
        if values["LINKTYPEID"] == 0: pl.append( "animal=%s " % values["LINKID"])
        elif values["LINKTYPEID"] == 3: pl.append( "owner=%s " % values["LINKID"])
        elif values["LINKTYPEID"] == 6: pl.append( "animalcontrol=%s " % values["LINKID"])
    elif tablename == "diary" and "LINKTYPE" in values and "LINKID" in values:
        if values["LINKTYPE"] == 1: pl.append( "animal=%s " % values["LINKID"])
        elif values["LINKTYPE"] == 2: pl.append( "owner=%s " % values["LINKID"])
        elif values["LINKTYPE"] == 7: pl.append( "animalcontrol=%s " % values["LINKID"])
    elif tablename == "log" and "LINKTYPE" in values and "LINKID" in values:
        if values["LINKTYPE"] == 0: pl.append( "animal=%s " % values["LINKID"])
        elif values["LINKTYPE"] == 1: pl.append( "owner=%s " % values["LINKID"])
        elif values["LINKTYPE"] == 6: pl.append( "animalcontrol=%s " % values["LINKID"])
    return "".join(pl)

def get_readable_fields_for_table(tablename):
    """
    Given a tablename, returns the list of fields that are human readable and can
    be supplied to the ref argument of map_diff
    """
    if tablename in READABLE_FIELDS:
        return READABLE_FIELDS[tablename]
    return []

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
    for k in row1.keys():
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
            parentlinks = get_parent_links(r, tablename)
            action(dbo, DELETE, username, tablename, r.ID, parentlinks, dump_row(dbo, tablename, r.ID))
    else:
        # otherwise, stuff all the deleted rows into one delete action
        action(dbo, DELETE, username, tablename, 0, "", str(rows))

def get_deletions(dbo):
    """ Returns all available records for undeleting """
    return dbo.query("SELECT ID, TableName, DeletedBy, Date, IDList FROM deletion WHERE TableName IN " \
        "('animal', 'owner', 'animalcontrol', 'customreport', 'dbfs', 'onlineformincoming', 'waitinglist', " \
        "'animallost', 'animalfound', 'templatedocument', 'templatehtml')")

def insert_deletions(dbo, username, tablename, condition):
    rows = dbo.query("SELECT * FROM %s WHERE %s" % (tablename, condition))
    if len(rows) > 0 and "ID" in rows[0]:
        for r in dbo.query("SELECT * FROM %s WHERE %s" % (tablename, condition)):
            parentlinks = get_parent_links(r, tablename)
            insert_deletion(dbo, username, tablename, r.ID, parentlinks, dbo.row_to_insert_sql(tablename, r))

def insert_deletion(dbo, username, tablename, linkid, parentlinks, restoresql):
    """
    Adds a row to the deletions table so that an item can be undeleted later
    """
    dbo.insert("deletion", {
        "ID":           linkid,
        "TableName":    tablename,
        "DeletedBy":    username,
        "Date":         dbo.now(),
        "IDList":       parentlinks,
        "*RestoreSQL":   restoresql
    }, generateID=False, writeAudit=False)

def undelete(dbo, did, tablename):
    """ Undeletes a top level record with deletion ID did from tablename """
    d = dbo.first_row(dbo.query("SELECT * FROM deletion WHERE ID=? AND TableName=?", [did, tablename]))
    if d is None: raise KeyError("Deletion ID %s.%s does not exist" % (tablename, did))
    # Undelete any associated rows first
    for x in dbo.query("SELECT * FROM deletion WHERE IDList LIKE ?", [ "%%%s=%s%%" % (d.TABLENAME, d.ID) ]):
        asm3.al.debug("undelete ID %s from %s: %s" % (x.ID, x.TABLENAME, x.RESTORESQL), "audit.undelete", dbo)
        dbo.execute(x.RESTORESQL)
    # Now the main record
    asm3.al.debug("undelete ID %s from %s: %s" % (d.ID, d.TABLENAME, d.RESTORESQL), "audit.undelete", dbo)
    dbo.execute(d.RESTORESQL)

def move(dbo, username, tablename, linkid, parentlinks, description):
    action(dbo, MOVE, username, tablename, linkid, parentlinks, description)

def login(dbo, username, remoteip = "", useragent = ""):
    action(dbo, LOGIN, username, "users", 0, "", "login from %s [%s]" % (remoteip, useragent))

def logout(dbo, username, remoteip = "", useragent = ""):
    action(dbo, LOGOUT, username, "users", 0, "", "logout from %s [%s]" % (remoteip, useragent))

def view_record(dbo, username, tablename, linkid, description):
    action(dbo, VIEW_RECORD, username, tablename, linkid, "", description)

def view_report(dbo, username, reportname, criteria):
    action(dbo, VIEW_REPORT, username, "customreport", 0, "", "%s - %s" % (reportname, criteria))

def email(dbo, username, fromadd, toadd, ccadd, bccadd, subject, body):
    action(dbo, EMAIL, username, "email", 0, "", "from: %s, to: %s, cc: %s, bcc: %s, subject: %s - %s" % (fromadd, toadd, ccadd, bccadd, subject, body))

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
    Deletes audit trail records older than six months
    Deletes deletion records older than six months
    """
    # Audit records
    d = dbo.today(offset=RETAIN_AUDIT_RECORDS)
    count = dbo.query_int("SELECT COUNT(*) FROM audittrail WHERE AuditDate < ?", [ d ])
    asm3.al.debug("removing %d audit records older than %d days." % (count, RETAIN_AUDIT_RECORDS), "audit.clean", dbo)
    dbo.execute("DELETE FROM audittrail WHERE AuditDate < ?", [ d ])
    # Deletion records
    d = dbo.today(offset=RETAIN_DELETION_RECORDS)
    count = dbo.query_int("SELECT COUNT(*) FROM deletion WHERE Date < ?", [ d ])
    asm3.al.debug("removing %d deletion records older than %d days." % (count, RETAIN_DELETION_RECORDS), "audit.clean", dbo)
    dbo.execute("DELETE FROM deletion WHERE Date < ?", [ d ])

