#!/usr/bin/python

import al
import audit
import db
import sys
import utils
from i18n import _, python2display

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

# IN clauses
ANIMAL_IN = "0, 2, 3, 4, 5, 6"
PERSON_IN = "1, 7, 8"
INCIDENT_IN = "16, 17, 18, 19, 20"
LOSTANIMAL_IN = "9, 10"
FOUNDANIMAL_IN = "11, 12"
WAITINGLIST_IN = "13, 14, 15"

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

def clause_for_linktype(linktype):
    """ Returns the appropriate clause for a link type """
    inclause = ANIMAL_IN
    if linktype == "person":
        inclause = PERSON_IN
    elif linktype == "incident":
        inclause = INCIDENT_IN
    elif linktype == "lostanimal":
        inclause = LOSTANIMAL_IN
    elif linktype == "foundanimal":
        inclause = FOUNDANIMAL_IN
    elif linktype == "waitinglist":
        inclause = WAITINGLIST_IN
    return inclause

def get_additional_fields(dbo, linkid, linktype = "animal"):
    """
    Returns a list of additional fields for the link
    the list contains all the fields from additionalfield and additional,
    including VALUE, FIELDNAME, FIELDLABEL, LOOKUPVALUES, FIELDTYPE and
    TOOLTIP.  If there isn't an appropriate additional row for the animal, null
    values will be returned for all fields.
    """
    inclause = clause_for_linktype(linktype)
    avalue = "a.Value"
    if dbo.dbtype == "POSTGRESQL": avalue = "asm_to_integer(a.Value)"
    return db.query(dbo, "SELECT af.ID, af.FieldName, af.FieldLabel, af.ToolTip, " \
        "af.LookupValues, af.DefaultValue, af.LinkType, af.FieldType, af.DisplayIndex, af.Mandatory, a.Value, " \
        "CASE WHEN af.FieldType = 8 AND a.Value <> '' AND a.Value <> '0' THEN (SELECT AnimalName FROM animal WHERE animal.ID = %s) ELSE '' END AS AnimalName, " \
        "CASE WHEN af.FieldType = 9 AND a.Value <> '' AND a.Value <> '0' THEN (SELECT OwnerName FROM owner WHERE owner.ID = %s) ELSE '' END AS OwnerName " \
        "FROM additionalfield af LEFT OUTER JOIN additional a ON af.ID = a.AdditionalFieldID " \
        "AND a.LinkID = %d " \
        "WHERE af.LinkType IN (%s) " \
        "ORDER BY af.DisplayIndex" % ( avalue, avalue, linkid, inclause ))

def get_additional_fields_ids(dbo, rows, linktype = "animal"):
    """
    Returns a list of additional fields for the linktype and for
    every single ID field in rows. Useful for getting additional
    fields for lists of animals
    """
    inclause = clause_for_linktype(linktype)
    avalue = "a.Value"
    if dbo.dbtype == "POSTGRESQL": avalue = "asm_to_integer(a.Value)"
    links = []
    for r in rows:
        links.append(str(r["ID"]))
    if len(links) == 0:
        links.append("0")
    return db.query(dbo, "SELECT a.LinkID, af.ID, af.FieldName, af.FieldLabel, af.ToolTip, " \
        "af.LookupValues, af.DefaultValue, af.FieldType, af.DisplayIndex, af.Mandatory, a.Value, " \
        "CASE WHEN af.FieldType = 8 AND a.Value <> '' AND a.Value <> '0' THEN (SELECT AnimalName FROM animal WHERE animal.ID = %s) ELSE '' END AS AnimalName, " \
        "CASE WHEN af.FieldType = 9 AND a.Value <> '' AND a.Value <> '0' THEN (SELECT OwnerName FROM owner WHERE owner.ID = %s) ELSE '' END AS OwnerName " \
        "FROM additional a INNER JOIN additionalfield af ON af.ID = a.AdditionalFieldID " \
        "WHERE a.LinkType IN (%s) AND a.LinkID IN (%s) " \
        "ORDER BY af.DisplayIndex" % ( avalue, avalue, inclause, ",".join(links)))

def get_field_definitions(dbo, linktype = "animal"):
    """
    Returns the field definition info for the linktype given,
    FIELDNAME, FIELDLABEL, LOOKUPVALUES, FIELDTYPE, TOOLTIP, SEARCHABLE, MANDATORY
    """
    inclause = clause_for_linktype(linktype)
    return db.query(dbo, "SELECT * FROM additionalfield WHERE LinkType IN (%s) ORDER BY DisplayIndex" % inclause)

def get_fields(dbo):
    """
    Returns all additional fields 
    """
    return db.query(dbo, "SELECT a.*, ft.FieldType AS FieldTypeName, " \
        "lt.LinkType AS LinkTypeName, m.Name AS MandatoryName " \
        "FROM additionalfield a " \
        "INNER JOIN lksfieldtype ft ON ft.ID = a.FieldType " \
        "INNER JOIN lksfieldlink lt ON lt.ID = a.LinkType " \
        "INNER JOIN lksyesno m ON m.ID = a.Mandatory " \
        "ORDER BY a.LinkType, a.DisplayIndex")

def insert_field_from_form(dbo, username, post):
    """
    Creates an additional field
    """
    nid = db.get_id(dbo, "additionalfield")
    sql = db.make_insert_sql("additionalfield", ( 
        ( "ID", db.di(nid)),
        ( "FieldName", post.db_string("name")),
        ( "FieldLabel", post.db_string("label")),
        ( "ToolTip", post.db_string("tooltip")),
        ( "LookupValues", post.db_string("lookupvalues")),
        ( "DefaultValue", post.db_string("defaultvalue")),
        ( "Mandatory", post.db_boolean("mandatory")),
        ( "Searchable", post.db_boolean("searchable")),
        ( "FieldType", post.db_integer("type")),
        ( "LinkType", post.db_integer("link")),
        ( "DisplayIndex", post.db_integer("displayindex"))
        ))
    db.execute(dbo, sql)
    audit.create(dbo, username, "additionalfield", nid, audit.dump_row(dbo, "additionalfield", nid))
    return nid

def update_field_from_form(dbo, username, post):
    """
    Updates an additional field record. All aspects of an additional
    field can be changed after creation since only the ID ties things 
    together.
    """
    aid = post.integer("id")
    sql = db.make_update_sql("additionalfield", "ID=%d" % aid, ( 
        ( "FieldName", post.db_string("name")),
        ( "FieldLabel", post.db_string("label")),
        ( "ToolTip", post.db_string("tooltip")),
        ( "LookupValues", post.db_string("lookupvalues")),
        ( "DefaultValue", post.db_string("defaultvalue")),
        ( "Mandatory", post.db_boolean("mandatory")),
        ( "Searchable", post.db_boolean("searchable")),
        ( "FieldType", post.db_integer("type")),
        ( "LinkType", post.db_integer("link")),
        ( "DisplayIndex", post.db_integer("displayindex"))
        ))
    preaudit = db.query(dbo, "SELECT * FROM additionalfield WHERE ID = %d" % aid)
    db.execute(dbo, sql)
    postaudit = db.query(dbo, "SELECT * FROM additionalfield WHERE ID = %d" % aid)
    audit.edit(dbo, username, "additionalfield", aid, audit.map_diff(preaudit, postaudit))

def delete_field(dbo, username, fid):
    """
    Deletes the selected additional field, along with all data held by it.
    """
    audit.delete(dbo, username, "additionalfield", fid, audit.dump_row(dbo, "additionalfield", fid))
    db.execute(dbo, "DELETE FROM additionalfield WHERE ID = %d" % int(fid))
    db.execute(dbo, "DELETE FROM additional WHERE AdditionalFieldID = %d" % int(fid))

def delete_values_for_link(dbo, linkid, linktype = "animal"):
    """
    Deletes all additional field values stored for a link.
    """
    inclause = clause_for_linktype(linktype)
    db.execute(dbo, "DELETE FROM additional WHERE LinkType IN (%s) AND LinkID = %d" % (inclause, linkid))

def save_values_for_link(dbo, post, linkid, linktype = "animal"):
    """
    Saves incoming additional field values from a form, clearing any
    existing values first.
    """
    delete_values_for_link(dbo, linkid, linktype)
    af = get_field_definitions(dbo, linktype)
    l = dbo.locale
    for f in af:
        key = "a." + str(f["MANDATORY"]) + "." + str(f["ID"])
        if post.has_key(key):
            val = post[key]
            if f["FIELDTYPE"] == YESNO:
                val = str(post.boolean(key))
            elif f["FIELDTYPE"] == MONEY:
                val = str(post.integer(key))
            elif f["FIELDTYPE"] == DATE:
                if len(val.strip()) > 0 and post.date(key) == None:
                    raise utils.ASMValidationError(_("Additional date field '{0}' contains an invalid date.", l).format(f["FIELDNAME"]))
                val = python2display(dbo.locale, post.date(key))
            sql = db.make_insert_sql("additional", (
                ( "LinkType", db.di(f["LINKTYPE"]) ),
                ( "LinkID", db.di(int(linkid)) ),
                ( "AdditionalFieldID", db.di(f["ID"]) ),
                ( "Value", db.ds(val) ) ))
            try:
                db.execute(dbo, sql)
            except Exception,err:
                al.error("Failed saving additional field: %s" % str(err), "animal.update_animal_from_form", dbo, sys.exc_info())


