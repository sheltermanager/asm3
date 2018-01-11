#!/usr/bin/python

import al
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
    return dbo.query("SELECT af.ID, af.FieldName, af.FieldLabel, af.ToolTip, " \
        "af.LookupValues, af.DefaultValue, af.LinkType, af.FieldType, af.DisplayIndex, af.Mandatory, a.Value, " \
        "CASE WHEN af.FieldType = 8 AND a.Value <> '' AND a.Value <> '0' THEN (SELECT AnimalName FROM animal WHERE %s = a.Value) ELSE '' END AS AnimalName, " \
        "CASE WHEN af.FieldType = 9 AND a.Value <> '' AND a.Value <> '0' THEN (SELECT OwnerName FROM owner WHERE %s = a.Value) ELSE '' END AS OwnerName " \
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
    return dbo.query("SELECT a.LinkID, af.ID, af.FieldName, af.FieldLabel, af.ToolTip, " \
        "af.LookupValues, af.DefaultValue, af.FieldType, af.DisplayIndex, af.Mandatory, a.Value, " \
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

def get_fields(dbo):
    """
    Returns all additional fields 
    """
    return dbo.query("SELECT a.*, ft.FieldType AS FieldTypeName, " \
        "lt.LinkType AS LinkTypeName, m.Name AS MandatoryName " \
        "FROM additionalfield a " \
        "INNER JOIN lksfieldtype ft ON ft.ID = a.FieldType " \
        "INNER JOIN lksfieldlink lt ON lt.ID = a.LinkType " \
        "INNER JOIN lksyesno m ON m.ID = a.Mandatory " \
        "ORDER BY a.LinkType, a.DisplayIndex")

def append_to_results(dbo, rows, linktype = "animal"):
    """
    Goes through each row in rows and adds any additional fields to the resultset.
    Requires an ID column in the rows.
    """
    for r in rows:
        add = get_additional_fields(dbo, r.id, linktype)
        for af in add:
            if af.fieldname.find("&") != -1:
                # We've got unicode chars for the tag name - not allowed
                r["ADD" + str(af.id)] = af.value
            else:
                r[af.fieldname] = af.value
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
        "Searchable":       post.boolean("searchable"),
        "FieldType":        post.integer("type"),
        "LinkType":         post.integer("link"),
        "DisplayIndex":     post.integer("displayindex")
    })

def delete_field(dbo, username, fid):
    """
    Deletes the selected additional field, along with all data held by it.
    """
    dbo.delete("additionalfield", fid, username)
    dbo.execute("DELETE FROM additional WHERE AdditionalFieldID = ?", [fid] )

def delete_values_for_link(dbo, linkid, linktype = "animal"):
    """
    Deletes all additional field values stored for a link.
    """
    inclause = clause_for_linktype(linktype)
    dbo.execute("DELETE FROM additional WHERE LinkType IN (%s) AND LinkID = %d" % (inclause, linkid))

def save_values_for_link(dbo, post, linkid, linktype = "animal"):
    """
    Saves incoming additional field values from a form, clearing any
    existing values first.
    """
    delete_values_for_link(dbo, linkid, linktype)
    af = get_field_definitions(dbo, linktype)
    l = dbo.locale
    for f in af:
        key = "a.%s.%s" % (f.mandatory, f.id)
        if key in post:
            val = post[key]
            if f.fieldtype == YESNO:
                val = str(post.boolean(key))
            elif f.fieldtype == MONEY:
                val = str(post.integer(key))
            elif f.fieldtype == DATE:
                if len(val.strip()) > 0 and post.date(key) is None:
                    raise utils.ASMValidationError(_("Additional date field '{0}' contains an invalid date.", l).format(f.fieldname))
                val = python2display(dbo.locale, post.date(key))
            try:
                dbo.insert("additional", {
                    "LinkType":             f.linktype,
                    "LinkID":               linkid,
                    "AdditionalFieldID":    f.id,
                    "Value":                val
                }, generateID=False, writeAudit=False)
            except Exception as err:
                al.error("Failed saving additional field: %s" % err, "additional.save_values_for_link", dbo, sys.exc_info())


