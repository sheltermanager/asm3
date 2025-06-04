
import asm3.al
import asm3.audit
import asm3.utils
import asm3.movement

from asm3.i18n import _, python2display
from asm3.typehints import Database, PostedData, Results

import sys

# Links
ANIMAL = 0
ANIMAL_DETAILS = 2
ANIMAL_NOTES = 3
ANIMAL_ENTRY = 4
ANIMAL_HEALTH = 5
ANIMAL_DEATH = 6
EVENT = 21
INCIDENT_DETAILS = 16
INCIDENT_DISPATCH = 17
INCIDENT_OWNER = 18
INCIDENT_CITATION = 19
INCIDENT_ADDITIONAL = 20
MOVEMENT_ADOPTION = 22
MOVEMENT_FOSTER = 23
MOVEMENT_TRANSFER = 24
MOVEMENT_ESCAPED = 25
MOVEMENT_RECLAIMED = 26
MOVEMENT_STOLEN = 27
MOVEMENT_RELEASED = 28
MOVEMENT_RETAILER = 29
MOVEMENT_RESERVATION = 30
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
CITATION_IN = "19"
EVENT_IN = "21"
FOUNDANIMAL_IN = "11, 12"
INCIDENT_IN = "16, 17, 18, 20"
LOSTANIMAL_IN = "9, 10"
MOVEMENT_IN = '22, 23, 24, 25, 26, 27, 28, 29, 30'
PERSON_IN = "1, 7, 8"
WAITINGLIST_IN = "13, 14, 15"

# Movement mapping 

MOVEMENT_MAPPING = {
    asm3.movement.ADOPTION: MOVEMENT_ADOPTION,
    asm3.movement.FOSTER: MOVEMENT_FOSTER,
    asm3.movement.TRANSFER: MOVEMENT_TRANSFER,
    asm3.movement.ESCAPED: MOVEMENT_ESCAPED,
    asm3.movement.RECLAIMED: MOVEMENT_RECLAIMED,
    asm3.movement.STOLEN: MOVEMENT_STOLEN,
    asm3.movement.RELEASED: MOVEMENT_RELEASED,
    asm3.movement.RETAILER: MOVEMENT_RETAILER,
    0: MOVEMENT_RESERVATION
}

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
PERSON_SPONSOR = 11
PERSON_VET = 12
PERSON_ADOPTIONCOORDINATOR = 13
TELEPHONE = 14

def clause_for_linktype(linktype: str) -> str:
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
    elif linktype == "movement":
        inclause = MOVEMENT_IN
    elif linktype == "citation":
        inclause = CITATION_IN
    return inclause

def table_for_linktype(linktype: str) -> str:
    """ Returns the parent table for an additional link type """
    if linktype == "incident":
        return "animalcontrol"
    elif linktype == "lostanimal":
        return "animallost"
    elif linktype == "foundanimal":
        return "animalfound"
    elif linktype == "movement":
        return "adoption"
    return linktype

def is_person_fieldtype(fieldtype: int) -> bool:
    """ Returns true if the field type given is a person """
    return fieldtype in (PERSON_LOOKUP, PERSON_SPONSOR, PERSON_VET, PERSON_ADOPTIONCOORDINATOR)

def get_additional_fields(dbo: Database, linkid: int, linktype: str = "animal", linktypeid: int = -1) -> Results:
    """
    Returns a list of additional fields for the link
    the list contains all the fields from additionalfield and additional,
    including VALUE, FIELDNAME, FIELDLABEL, LOOKUPVALUES, FIELDTYPE and
    TOOLTIP.  If there isn't an appropriate additional row for the animal, null
    values will be returned for all fields.
    """
    if linkid is None: return []
    if linktypeid != -1:
        inclause = f"({linktypeid})"
    else:
        inclause = clause_for_linktype(linktype)
    return dbo.query("SELECT af.*, a.Value, " \
        "CASE WHEN af.FieldType = 8 AND a.Value <> '' AND a.Value <> '0' THEN (SELECT AnimalName FROM animal WHERE %s = a.Value) ELSE '' END AS AnimalName, " \
        "CASE WHEN af.FieldType IN (9, 11, 12) AND a.Value <> '' AND a.Value <> '0' " \
            "THEN (SELECT OwnerName FROM owner WHERE %s = a.Value) ELSE '' END AS OwnerName " \
        "FROM additionalfield af " \
        "LEFT OUTER JOIN additional a ON af.ID = a.AdditionalFieldID " \
        "AND a.LinkID = %d " \
        "WHERE af.LinkType IN (%s) " \
        "ORDER BY af.DisplayIndex" % ( dbo.sql_cast_char("animal.ID"), dbo.sql_cast_char("owner.ID"), linkid, inclause ))

def get_additional_fields_ids(dbo: Database, rows: Results, linktype: str = "animal") -> Results:
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
        "CASE WHEN af.FieldType IN (9, 11, 12) AND a.Value <> '' AND a.Value <> '0' THEN (SELECT OwnerName FROM owner WHERE %s = a.Value) ELSE '' END AS OwnerName " \
        "FROM additional a INNER JOIN additionalfield af ON af.ID = a.AdditionalFieldID " \
        "WHERE a.LinkType IN (%s) AND a.LinkID IN (%s) " \
        "ORDER BY af.DisplayIndex" % ( dbo.sql_cast_char("animal.ID"), dbo.sql_cast_char("owner.ID"), inclause, ",".join(links)))

def get_additional_fields_dict(dbo: Database, post: PostedData, linktype: str) -> dict:
    """
        Returns a dictionary with keys from input post that match additional field key patterns 
    """
    ret = {}
    for f in get_field_definitions(dbo, linktype):
        key = "a.%s.%s" % (f.mandatory, f.id)
        key2 = "additional%s" % f.fieldname
        if key in post:
            ret[key] = post[key]
        elif key2 in post:
            ret[key] = post[key]
    return ret

def get_field_definitions(dbo: Database, linktype: str = "animal") -> Results:
    """
    Returns the field definition info for the linktype given,
    FIELDNAME, FIELDLABEL, LOOKUPVALUES, FIELDTYPE, TOOLTIP, SEARCHABLE, MANDATORY
    """
    inclause = clause_for_linktype(linktype)
    return dbo.query("SELECT * FROM additionalfield WHERE LinkType IN (%s) ORDER BY DisplayIndex" % inclause)

def get_ids_for_fieldtype(dbo: Database, fieldtype: int) -> list:
    """
    Returns a list of ID numbers for additional field definitions of a particular field type 
    (used by the update_merge functions below)
    """
    rows = dbo.query("SELECT ID FROM additionalfield WHERE FieldType=%s" % fieldtype)
    out = []
    for r in rows:
        out.append(str(r.ID))
    return out

def get_fields(dbo: Database) -> Results:
    """
    Returns all additional fields 
    """
    return dbo.query("SELECT a.*, ft.FieldType AS FieldTypeName, " \
        "lt.LinkType AS LinkTypeName, m.Name AS MandatoryName, " \
        "n.Name AS NewRecordName, " \
        "(SELECT COUNT(*) FROM additional WHERE AdditionalFieldID=a.ID) AS RecordCount " \
        "FROM additionalfield a " \
        "INNER JOIN lksfieldtype ft ON ft.ID = a.FieldType " \
        "INNER JOIN lksfieldlink lt ON lt.ID = a.LinkType " \
        "INNER JOIN lksyesno m ON m.ID = a.Mandatory " \
        "INNER JOIN lksyesno n ON n.ID = a.NewRecord " \
        "ORDER BY a.LinkType, a.DisplayIndex")

def append_to_results(dbo: Database, rows: Results, linktype: str = "animal") -> Results:
    """
    Goes through each row in rows and adds any additional fields to the resultset.
    Requires an ID column in the rows.
    """
    add = get_additional_fields_ids(dbo, rows, linktype)
    for r in rows:
        for af in add:
            if r.ID != add.LINKID: continue
            tn = af.FIELDNAME.upper()
            if tn.find("&") != -1:
                # We've got unicode chars for the tag name - not allowed
                r["ADD" + str(af.id)] = af.VALUE
            elif tn in r:
                # This key already exists - do not allow a collision. 
                # This happened where a user named a field ID and it broke animal_view_adoptable_js
                r["ADD%s" % tn] = af.VALUE
            else:
                r[tn] = af.VALUE
    return rows

def sanitise_lookup_values(s):
    """ Remove unwanted chars from lookup values """
    s = s.replace(",", " ")
    s = s.replace("\n", " ")
    s = s.replace(" |", "|")
    s = s.replace("| ", "|")
    s = asm3.utils.strip_duplicate_spaces(s)
    return s

def insert_field_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Creates an additional field
    """
    validate_field(dbo, post)
    return dbo.insert("additionalfield", {
        "FieldName":        post["name"],
        "FieldLabel":       post["label"],
        "ToolTip":          post["tooltip"],
        "LookupValues":     sanitise_lookup_values(post["lookupvalues"]),
        "DefaultValue":     post["defaultvalue"],
        "Mandatory":        post.boolean("mandatory"),
        "NewRecord":        post.boolean("newrecord"),
        "Searchable":       post.boolean("searchable"),
        "Hidden":           post.boolean("hidden"),
        "FieldType":        post.integer("type"),
        "LinkType":         post.integer("link"),
        "DisplayIndex":     post.integer("displayindex")
    }, username, setRecordVersion=False, setCreated=False)

def update_field_from_form(dbo: Database, username: str, post: PostedData) -> None:
    """
    Updates an additional field record. All aspects of an additional
    field can be changed after creation since only the ID ties things 
    together.
    """
    validate_field(dbo, post)
    dbo.update("additionalfield", post.integer("id"), {
        "FieldName":        post["name"],
        "FieldLabel":       post["label"],
        "ToolTip":          post["tooltip"],
        "LookupValues":     sanitise_lookup_values(post["lookupvalues"]),
        "DefaultValue":     post["defaultvalue"],
        "Mandatory":        post.boolean("mandatory"),
        "NewRecord":        post.boolean("newrecord"),
        "Searchable":       post.boolean("searchable"),
        "Hidden":           post.boolean("hidden"),
        "FieldType":        post.integer("type"),
        "LinkType":         post.integer("link"),
        "DisplayIndex":     post.integer("displayindex")
    }, username, setRecordVersion=False, setLastChanged=False)

def validate_field(dbo: Database, post: PostedData) -> None:
    """
    Checks that an additional field is valid/correct. An exception is raised for validation failures.
    """
    l = dbo.locale
    # Make sure that we don't have another field with the same name (id will resolve to 0 for insert, so still works)
    if 0 != dbo.query_int("SELECT COUNT(ID) FROM additionalfield WHERE ID <> ? AND LOWER(FieldName) = ?", ( post.integer("id"), post["name"].lower() )):
        raise asm3.utils.ASMValidationError(_("Additional fields must have unique names", l))
    # Make sure there are no spaces or punctuation in the name
    name = post["name"]
    if asm3.utils.strip_punctuation(name.replace(" ", "")) != name:
        raise asm3.utils.ASMValidationError(_("Additional field names cannot contain spaces or punctuation", l))
    # Make sure the name is not one of our reserved words that can break document or web templates
    # by masking critical built-in fields
    RESERVED = [ "id", "animalid", "personid" ]
    if name.lower() in RESERVED:
        raise asm3.utils.ASMValidationError(_("'{0}' is a reserved name and cannot be used for an additional field", l).format(name))

def update_merge_animal(dbo: Database, oldanimalid: int, newanimalid: int) -> None:
    """
    When we merge an animal record, we want to update all additional fields that are 
    of type ANIMAL_LOOKUP and have a value matching oldanimalid to newanimalid.
    """
    afs = get_ids_for_fieldtype(dbo, ANIMAL_LOOKUP)
    if len(afs) == 0: afs = [ "0" ]
    dbo.execute("UPDATE additional SET Value='%s' WHERE Value='%s' AND AdditionalFieldID IN (%s)" % (newanimalid, oldanimalid, ",".join(afs)))

def update_merge_person(dbo: Database, oldpersonid: int, newpersonid: int) -> None:
    """
    When we merge a person record, we want to update all additional fields that are 
    of type PERSON_LOOKUP and have a value matching oldpersonid to newpersonid.
    """
    afs = get_ids_for_fieldtype(dbo, PERSON_LOOKUP)
    if len(afs) == 0: afs = [ "0" ]
    dbo.execute("UPDATE additional SET Value='%s' WHERE Value='%s' AND AdditionalFieldID IN (%s)" % (newpersonid, oldpersonid, ",".join(afs)))

def delete_field(dbo: Database, username: str, fid: int) -> None:
    """
    Deletes the selected additional field, along with all data held by it.
    """
    dbo.delete("additionalfield", fid, username)
    dbo.delete("additional", "AdditionalFieldID=%d" % fid)

def insert_additional(dbo: Database, linktype: int, linkid: int, additionalfieldid: int, value: str) -> int:
    """ Inserts an additional field record """
    try:
        dbo.delete("additional", "LinkType=%s AND LinkID=%s AND AdditionalFieldID=%s" % (linktype, linkid, additionalfieldid))
        return dbo.insert("additional", {
            "LinkType":             linktype,
            "LinkID":               linkid,
            "AdditionalFieldID":    additionalfieldid,
            "Value":                value
        }, generateID=False, writeAudit=False)
    except Exception as err:
        asm3.al.error("Failed saving additional field: %s" % err, "additional.insert_additional", dbo, sys.exc_info())

def save_values_for_link(dbo: Database, post: PostedData, username: str, linkid: int, linktype: str = "animal", setdefaults: bool = False) -> None:
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

def merge_values_for_link(dbo: Database, post: PostedData, username: str, linkid: int, linktype: str = "animal") -> None:
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

def merge_values(dbo: Database, username: str, sourceid: int, targetid: int, linktype: str = "animal") -> None:
    """
    Copies all the additional field values from sourceid to targetid. 
    Only copies a value if it is not present on targetid or is an empty string.
    """
    audits = []
    clause = clause_for_linktype(linktype)
    sourcevalues = dbo.query("SELECT a.Value, a.AdditionalFieldID, af.FieldName, af.LinkType FROM additional a " \
        "INNER JOIN additionalfield af ON af.ID = a.AdditionalFieldID " \
        f"WHERE af.LinkType IN ({clause}) AND a.LinkID=?", [sourceid])
    targetvalues = dbo.query("SELECT a.Value, a.AdditionalFieldID, af.FieldName, af.LinkType FROM additional a " \
        "INNER JOIN additionalfield af ON af.ID = a.AdditionalFieldID " \
        f"WHERE af.LinkType IN ({clause}) AND a.LinkID=?", [targetid])
    for sv in sourcevalues:
        # Check if this field exists in the target and has a value
        hasvalue = False
        for tv in targetvalues:
            if sv.ADDITIONALFIELDID == tv.ADDITIONALFIELDID and tv.VALUE:
                hasvalue = True
                break
        # If it doesn't, we can copy it to the target
        if not hasvalue:
            dbo.delete("additional", "LinkID=%s AND AdditionalFieldID=%s" % (targetid, sv.ADDITIONALFIELDID))
            insert_additional(dbo, sv.LINKTYPE, targetid, sv.ADDITIONALFIELDID, sv.VALUE)
            audits.append("%s='%s'" % (sv.FIELDNAME, sv.VALUE))

    if len(audits) > 0:
        asm3.audit.edit(dbo, username, "additional", 0, "%s=%s " % (table_for_linktype(linktype), targetid), ", ".join(audits))

