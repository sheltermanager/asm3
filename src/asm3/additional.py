
import asm3.al
import asm3.audit
import asm3.utils

from asm3.i18n import python2display

import sys

# Links
ANIMAL = 0
ANIMAL_DETAILS = 2
ANIMAL_NOTES = 3
ANIMAL_ENTRY = 4
ANIMAL_HEALTH = 5
ANIMAL_DEATH = 6
INCIDENT_DETAILS = 16
INCIDENT_DISPATCH = 17
INCIDENT_OWNER = 18
INCIDENT_CITATION = 19
INCIDENT_ADDITIONAL = 20
PERSON = 1
PERSON_NAME = 7
PERSON_TYPE = 8
LOSTANIMAL = 9
LOSTANIMAL_DETAILS = 10
FOUNDANIMAL = 11
FOUNDANIMAL_DETAILS = 12
WAITINGLIST = 13
WAITINGLIST_DETAILS = 14
WAITINGLIST_REMOVAL = 15
EVENT = 21

# IN clauses
ANIMAL_IN = "0, 2, 3, 4, 5, 6"
PERSON_IN = "1, 7, 8"
INCIDENT_IN = "16, 17, 18, 19, 20"
LOSTANIMAL_IN = "9, 10"
FOUNDANIMAL_IN = "11, 12"
WAITINGLIST_IN = "13, 14, 15"
EVENT_IN = "21"

# Field types
YESNO = 0
TEXT = 1
NOTES = 2
NUMBER = 3
DATE = 4
MONEY = 5
LOOKUP = 6
MULTI_LOOKUP = 7
ANIMAL_LOOKUP = 8
PERSON_LOOKUP = 9
TIME = 10
SPONSOR = 11
VET = 12

def clause_for_linktype(linktype):
    """ Returns the appropriate clause for a link type """
    inclause = ANIMAL_IN
    if linktype == "person":
        inclause = PERSON_IN
    elif linktype == "incident":
        inclause = INCIDENT_IN
    elif linktype == "event":
        inclause = EVENT_IN
    elif linktype == "lostanimal":
        inclause = LOSTANIMAL_IN
    elif linktype == "foundanimal":
        inclause = FOUNDANIMAL_IN
    elif linktype == "waitinglist":
        inclause = WAITINGLIST_IN
    return inclause

def table_for_linktype(linktype):
    """ Returns the parent table for an additional link type """
    if linktype == "incident":
        return "animalcontrol"
    elif linktype == "lostanimal":
        return "animallost"
    elif linktype == "foundanimal":
        return "animalfound"
    return linktype

def get_additional_fields(dbo, linkid, linktype = "animal"):
    """
    Returns a list of additional fields for the link
    the list contains all the fields from additionalfield and additional,
    including VALUE, FIELDNAME, FIELDLABEL, LOOKUPVALUES, FIELDTYPE and
    TOOLTIP.  If there isn't an appropriate additional row for the animal, null
    values will be returned for all fields.
    """
    inclause = clause_for_linktype(linktype)
    return dbo.query("SELECT af.*, a.Value, " \
        "CASE WHEN af.FieldType = 8 AND a.Value <> '' AND a.Value <> '0' THEN (SELECT AnimalName FROM animal WHERE %s = a.Value) ELSE '' END AS AnimalName, " \
        "CASE WHEN af.FieldType = 9 OR af.FieldType = 11 OR af.FieldType = 12 AND a.Value <> '' AND a.Value <> '0' " \
                     "THEN (SELECT OwnerName FROM owner WHERE %s = a.Value) ELSE '' END AS OwnerName " \
        "FROM additionalfield af LEFT OUTER JOIN additional a ON af.ID = a.AdditionalFieldID " \
        "AND a.LinkID = %d " \
        "WHERE af.LinkType IN (%s) " \
        "ORDER BY af.DisplayIndex" % ( dbo.sql_cast_char("animal.ID"), dbo.sql_cast_char("owner.ID"), linkid, inclause ))

def get_additional_fields_ids(dbo, rows, linktype = "animal"):
    """
    Returns a list of additional fields for the linktype and for
    every single ID field in rows. Useful for getting additional
    fields for lists of animals
    """
    inclause = clause_for_linktype(linktype)
    links = []
    for r in rows:
        links.append(str(r.id))
    if len(links) == 0:
        links.append("0")
    return dbo.query("SELECT af.*, a.LinkID, a.Value, " \
        "CASE WHEN af.FieldType = 8 AND a.Value <> '' AND a.Value <> '0' THEN (SELECT AnimalName FROM animal WHERE %s = a.Value) ELSE '' END AS AnimalName, " \
        "CASE WHEN af.FieldType = 9 AND a.Value <> '' AND a.Value <> '0' THEN (SELECT OwnerName FROM owner WHERE %s = a.Value) ELSE '' END AS OwnerName " \
        "FROM additional a INNER JOIN additionalfield af ON af.ID = a.AdditionalFieldID " \
        "WHERE a.LinkType IN (%s) AND a.LinkID IN (%s) " \
        "ORDER BY af.DisplayIndex" % ( dbo.sql_cast_char("animal.ID"), dbo.sql_cast_char("owner.ID"), inclause, ",".join(links)))

def get_field_definitions(dbo, linktype = "animal"):
    """
    Returns the field definition info for the linktype given,
    FIELDNAME, FIELDLABEL, LOOKUPVALUES, FIELDTYPE, TOOLTIP, SEARCHABLE, MANDATORY
    """
    inclause = clause_for_linktype(linktype)
    return dbo.query("SELECT * FROM additionalfield WHERE LinkType IN (%s) ORDER BY DisplayIndex" % inclause)

def get_ids_for_fieldtype(dbo, fieldtype):
    """
    Returns a list of ID numbers for additional field definitions of a particular field type 
    (used by the update_merge functions below)
    """
    rows = dbo.query("SELECT ID FROM additionalfield WHERE FieldType=%s" % fieldtype)
    out = []
    for r in rows:
        out.append(str(r.ID))
    return out

def get_fields(dbo):
    """
    Returns all additional fields 
    """
    return dbo.query("SELECT a.*, ft.FieldType AS FieldTypeName, " \
        "lt.LinkType AS LinkTypeName, m.Name AS MandatoryName, " \
        "n.Name AS NewRecordName " \
        "FROM additionalfield a " \
        "INNER JOIN lksfieldtype ft ON ft.ID = a.FieldType " \
        "INNER JOIN lksfieldlink lt ON lt.ID = a.LinkType " \
        "INNER JOIN lksyesno m ON m.ID = a.Mandatory " \
        "INNER JOIN lksyesno n ON n.ID = a.NewRecord " \
        "ORDER BY a.LinkType, a.DisplayIndex")

def append_to_results(dbo, rows, linktype = "animal"):
    """
    Goes through each row in rows and adds any additional fields to the resultset.
    Requires an ID column in the rows.
    """
    for r in rows:
        add = get_additional_fields(dbo, r.id, linktype)
        for af in add:
            tn = af.fieldname.upper()
            if tn.find("&") != -1:
                # We've got unicode chars for the tag name - not allowed
                r["ADD" + str(af.id)] = af.value
            elif tn in r:
                # This key already exists - do not allow a collision. 
                # This happened where a user named a field ID and it broke animal_view_adoptable_js
                r["ADD%s" % tn] = af.value
            else:
                r[tn] = af.value
    return rows

def insert_field_from_form(dbo, username, post):
    """
    Creates an additional field
    """
    return dbo.insert("additionalfield", {
        "FieldName":        post["name"],
        "FieldLabel":       post["label"],
        "ToolTip":          post["tooltip"],
        "LookupValues":     post["lookupvalues"],
        "DefaultValue":     post["defaultvalue"],
        "Mandatory":        post.boolean("mandatory"),
        "NewRecord":        post.boolean("newrecord"),
        "Searchable":       post.boolean("searchable"),
        "FieldType":        post.integer("type"),
        "LinkType":         post.integer("link"),
        "DisplayIndex":     post.integer("displayindex")
    })

def update_field_from_form(dbo, username, post):
    """
    Updates an additional field record. All aspects of an additional
    field can be changed after creation since only the ID ties things 
    together.
    """
    dbo.update("additionalfield", post.integer("id"), {
        "FieldName":        post["name"],
        "FieldLabel":       post["label"],
        "ToolTip":          post["tooltip"],
        "LookupValues":     post["lookupvalues"],
        "DefaultValue":     post["defaultvalue"],
        "Mandatory":        post.boolean("mandatory"),
        "NewRecord":        post.boolean("newrecord"),
        "Searchable":       post.boolean("searchable"),
        "FieldType":        post.integer("type"),
        "LinkType":         post.integer("link"),
        "DisplayIndex":     post.integer("displayindex")
    })

def update_merge_animal(dbo, oldanimalid, newanimalid):
    """
    When we merge an animal record, we want to update all additional fields that are 
    of type ANIMAL_LOOKUP and have a value matching oldanimalid to newanimalid.
    """
    afs = get_ids_for_fieldtype(dbo, ANIMAL_LOOKUP)
    if len(afs) == 0: afs = [ "0" ]
    dbo.execute("UPDATE additional SET Value='%s' WHERE Value='%s' AND AdditionalFieldID IN (%s)" % (newanimalid, oldanimalid, ",".join(afs)))

def update_merge_person(dbo, oldpersonid, newpersonid):
    """
    When we merge a person record, we want to update all additional fields that are 
    of type PERSON_LOOKUP and have a value matching oldpersonid to newpersonid.
    """
    afs = get_ids_for_fieldtype(dbo, PERSON_LOOKUP)
    if len(afs) == 0: afs = [ "0" ]
    dbo.execute("UPDATE additional SET Value='%s' WHERE Value='%s' AND AdditionalFieldID IN (%s)" % (newpersonid, oldpersonid, ",".join(afs)))

def delete_field(dbo, username, fid):
    """
    Deletes the selected additional field, along with all data held by it.
    """
    dbo.delete("additionalfield", fid, username)
    dbo.delete("additional", "AdditionalFieldID=%d" % fid)

def insert_additional(dbo, linktype, linkid, additionalfieldid, value):
    """ Inserts an additional field record """
    try:
        dbo.delete("additional", "LinkType=%s AND LinkID=%s AND AdditionalFieldID=%s" % (linktype, linkid, additionalfieldid))
        dbo.insert("additional", {
            "LinkType":             linktype,
            "LinkID":               linkid,
            "AdditionalFieldID":    additionalfieldid,
            "Value":                value
        }, generateID=False, writeAudit=False)
    except Exception as err:
        asm3.al.error("Failed saving additional field: %s" % err, "additional.insert_additional", dbo, sys.exc_info())

def save_values_for_link(dbo, post, username, linkid, linktype = "animal", setdefaults=False):
    """
    Saves incoming additional field values from a record.
    Clears existing additional field values before saving (this is because forms
        don't send blank values)
    linkid: The link to the parent record
    linktype: The class of parent record
    setdefaults: If True, will set default values for any keys not supplied
        (Should be True for calls from insert_X_from_form methods)
    Keys of either a.MANDATORY.ID can be used (ASM internal forms)
        or keys of the form additionalFIELDNAME (ASM online forms)
    """
    dbo.delete("additional", "LinkType IN (%s) AND LinkID=%s" % (clause_for_linktype(linktype), linkid))
    audits = []

    for f in get_field_definitions(dbo, linktype):

        key = "a.%s.%s" % (f.mandatory, f.id)
        key2 = "additional%s" % f.fieldname

        if key not in post and key2 not in post:
            if setdefaults and f.DEFAULTVALUE and f.DEFAULTVALUE != "": 
                insert_additional(dbo, f.LINKTYPE, linkid, f.ID, f.DEFAULTVALUE)
                audits.append("%s='%s'" % (f.FIELDNAME, f.DEFAULTVALUE))
            continue

        elif key not in post: key = key2

        val = post[key]
        if f.fieldtype == YESNO:
            val = str(post.boolean(key))
        elif f.fieldtype == MONEY:
            val = str(post.integer(key))
        elif f.fieldtype == DATE:
            val = python2display(dbo.locale, post.date(key))
        audits.append("%s='%s'" % (f.FIELDNAME, val))
        insert_additional(dbo, f.LINKTYPE, linkid, f.ID, val)

    if len(audits) > 0:
        asm3.audit.edit(dbo, username, "additional", 0, "%s=%s " % (table_for_linktype(linktype), linkid), ", ".join(audits))

def merge_values_for_link(dbo, post, username, linkid, linktype = "animal"):
    """
    Saves incoming additional field values. Only updates the 
    additional fields that are present in the post object and leaves the rest alone. 
    It will only update a field if it has a value. This function is aimed
    at areas that merge into existing records, such as online forms and CSV imports.
    linkid: The link to the parent record
    linktype: The class of parent record
    Keys of either a.MANDATORY.ID can be used (ASM internal forms)
        or keys of the form additionalFIELDNAME (ASM online forms)
    """
    audits = []
    for f in get_field_definitions(dbo, linktype):

        key = "a.%s.%s" % (f.mandatory, f.id)
        key2 = "additional%s" % f.fieldname

        if key2 in post: key = key2
        if key in post:
            val = post[key]
            if val == "": continue
            if f.fieldtype == YESNO:
                val = str(post.boolean(key))
            elif f.fieldtype == MONEY:
                val = str(post.integer(key))
            elif f.fieldtype == DATE:
                val = python2display(dbo.locale, post.date(key))
            dbo.delete("additional", "LinkID=%s AND AdditionalFieldID=%s" % (linkid, f.ID))
            insert_additional(dbo, f.LINKTYPE, linkid, f.ID, val)
            audits.append("%s='%s'" % (f.FIELDNAME, val))

    if len(audits) > 0:
        asm3.audit.edit(dbo, username, "additional", 0, "%s=%s " % (table_for_linktype(linktype), linkid), ", ".join(audits))

