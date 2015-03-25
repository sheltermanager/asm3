#!/usr/bin/python

import additional
import al
import animal
import audit
import configuration
import dbfs
import diary
import db
import geo
import log
import media
import reports
import users
import utils
from i18n import _, subtract_years, now
from sitedefs import BULK_GEO_BATCH

ASCENDING = 0
DESCENDING = 1

def get_homechecked(dbo, personid):
    """
    Returns a list of people homechecked by personid
    """
    return db.query(dbo, "SELECT ID, OwnerName, DateLastHomeChecked, Comments FROM owner " \
        "WHERE HomeCheckedBy = %d" % int(personid))

def get_person_code_query(dbo):
    if dbo.dbtype == "MYSQL": 
        return "CONCAT(SUBSTR(UPPER(o.OwnerSurname), 1, 2), LPAD(o.ID, 6, '0'))"
    if dbo.dbtype == "POSTGRESQL": 
        return "SUBSTRING(UPPER((XPATH('/z/text()', ('<z>' || replace(replace(replace(o.OwnerSurname, '&', ''), '<', ''), '>', '') || '</z>')::xml))[1]::text) FROM 0 FOR 3) || TO_CHAR(o.ID, 'FM000000')"
    if dbo.dbtype == "SQLITE": 
        return "SUBSTR(UPPER(o.OwnerSurname), 1, 2) || o.ID"

def get_person_query(dbo):
    """
    Returns the SELECT and JOIN commands necessary for selecting
    person rows with resolved lookups.
    """
    ownercode = get_person_code_query(dbo)
    return "SELECT DISTINCT o.*, o.ID AS PersonID, " \
        "ho.OwnerName AS HomeCheckedByName, ho.HomeTelephone AS HomeCheckedByHomeTelephone, " \
        "ho.MobileTelephone AS HomeCheckedByMobileTelephone, ho.EmailAddress AS HomeCheckedByEmail, " \
        "web.MediaName AS WebsiteMediaName, " \
        "web.Date AS WebsiteMediaDate, " \
        "web.MediaNotes AS WebsiteMediaNotes, " \
        "(SELECT COUNT(oi.ID) FROM ownerinvestigation oi WHERE oi.OwnerID = o.ID) AS Investigation, " \
        "(SELECT COUNT(ac.ID) FROM animalcontrol ac WHERE ac.OwnerID = o.ID OR ac.Owner2ID = o.ID or ac.Owner3ID = o.ID) AS Incident, " \
        "%s AS OwnerCode " \
        "FROM owner o " \
        "LEFT OUTER JOIN owner ho ON ho.ID = o.HomeCheckedBy " \
        "LEFT OUTER JOIN media web ON web.LinkID = o.ID AND web.LinkTypeID = 3 AND web.WebsitePhoto = 1 " % ownercode

def get_rota_query(dbo):
    """
    Returns the SELECT and JOIN commands necessary for selecting from rota hours
    """
    return "SELECT r.*, o.OwnerName, rt.RotaType AS RotaTypeName " \
        "FROM ownerrota r " \
        "LEFT OUTER JOIN lksrotatype rt ON rt.ID = r.RotaTypeID " \
        "INNER JOIN owner o ON o.ID = r.OwnerID "

def get_person(dbo, personid):
    """
    Returns a complete person row by id, or None if not found
    (int) personid: The person to get
    """
    rows = db.query(dbo, get_person_query(dbo) + "WHERE o.ID = %d" % int(personid))
    if len(rows) == 0:
        return None
    else:
        return rows[0]

def get_person_similar(dbo, surname = "", forenames = "", address = ""):
    """
    Returns people with similar names and addresses to those supplied.
    """
    # Consider the first word rather than first address line - typically house
    # number/name and unlikely to be the same for different people
    if address.find(" ") != -1: address = address[0:address.find(" ")]
    if address.find("\n") != -1: address = address[0:address.find("\n")]
    if address.find(",") != -1: address = address[0:address.find(",")]
    address = address.replace("'", "`").lower()
    forenames = forenames.replace("'", "`").lower()
    if forenames.find(" ") != -1: forenames = forenames[0:forenames.find(" ")]
    surname = surname.replace("'", "`").lower()
    return db.query(dbo, get_person_query(dbo) + "WHERE LOWER(o.OwnerSurname) LIKE '%s' AND " \
        "LOWER(o.OwnerForeNames) LIKE '%s%%' AND LOWER(o.OwnerAddress) Like '%s%%'" % (surname, forenames, address))

def get_person_name(dbo, personid):
    """
    Returns the full person name for an id
    """
    return db.query_string(dbo, "SELECT OwnerName FROM owner WHERE ID = %d" % int(personid))

def get_person_name_code(dbo, personid):
    """
    Returns the person name and code for an id
    """
    r = db.query(dbo, "SELECT o.OwnerName, %s AS OwnerCode FROM owner o WHERE o.ID = %d" % (get_person_code_query(dbo), int(personid)))
    if len(r) == 0: return ""
    return "%s - %s" % (r[0]["OWNERNAME"], r[0]["OWNERCODE"])

def get_staff_volunteers(dbo):
    """
    Returns all staff and volunteers
    """
    return db.query(dbo, get_person_query(dbo) + " WHERE o.IsStaff = 1 OR o.IsVolunteer = 1 ORDER BY OwnerName")

def get_towns(dbo):
    """
    Returns a list of all towns
    """
    rows = db.query(dbo, "SELECT DISTINCT OwnerTown FROM owner")
    if rows is None: return []
    towns = []
    for r in rows:
        towns.append(str(r["OWNERTOWN"]))
    return towns

def get_town_to_county(dbo):
    """
    Returns a lookup of which county towns belong in
    """
    rows = db.query(dbo, "SELECT DISTINCT OwnerTown, OwnerCounty FROM owner")
    if rows is None: return []
    tc = []
    for r in rows:
        tc.append(str(r["OWNERTOWN"]) + "^^" + str(r["OWNERCOUNTY"]))
    return tc

def get_counties(dbo):
    """
    Returns a list of counties
    """
    rows = db.query(dbo, "SELECT DISTINCT OwnerCounty FROM owner")
    if rows is None: return []
    counties = []
    for r in rows:
        counties.append(str(r["OWNERCOUNTY"]))
    return counties

def get_satellite_counts(dbo, personid):
    """
    Returns a resultset containing the number of each type of satellite
    record that a person has.
    """
    sql = "SELECT o.ID, " \
        "(SELECT COUNT(*) FROM media me WHERE me.LinkID = o.ID AND me.LinkTypeID = %d) AS media, " \
        "(SELECT COUNT(*) FROM diary di WHERE di.LinkID = o.ID AND di.LinkType = %d) AS diary, " \
        "(SELECT COUNT(*) FROM adoption ad WHERE ad.OwnerID = o.ID) AS movements, " \
        "(SELECT COUNT(*) FROM log WHERE log.LinkID = o.ID AND log.LinkType = %d) AS logs, " \
        "(SELECT COUNT(*) FROM ownerdonation od WHERE od.OwnerID = o.ID) AS donations, " \
        "(SELECT COUNT(*) FROM ownercitation oc WHERE oc.OwnerID = o.ID) AS citation, " \
        "(SELECT COUNT(*) FROM ownerinvestigation oi WHERE oi.OwnerID = o.ID) AS investigation, " \
        "(SELECT COUNT(*) FROM ownerlicence ol WHERE ol.OwnerID = o.ID) AS licence, " \
        "(SELECT COUNT(*) FROM ownerrota r WHERE r.OwnerID = o.ID) AS rota, " \
        "(SELECT COUNT(*) FROM ownertraploan ot WHERE ot.OwnerID = o.ID) AS traploan, " \
        "(SELECT COUNT(*) FROM ownervoucher ov WHERE ov.OwnerID = o.ID) AS vouchers, " \
        "((SELECT COUNT(*) FROM animal WHERE BroughtInByOwnerID = o.ID OR OriginalOwnerID = o.ID OR CurrentVETID = o.ID OR OwnersVetID = o.ID OR PickedUpByOwnerID = o.ID) + " \
        "(SELECT COUNT(*) FROM animalwaitinglist WHERE OwnerID = o.ID) + " \
        "(SELECT COUNT(*) FROM animalfound WHERE OwnerID = o.ID) + " \
        "(SELECT COUNT(*) FROM animallost WHERE OwnerID = o.ID) + " \
        "(SELECT COUNT(*) FROM animalcontrol WHERE CallerID = o.ID OR VictimID = o.ID " \
        "OR OwnerID = o.ID OR Owner2ID = o.ID or Owner3ID = o.ID)) AS links " \
        "FROM owner o WHERE o.ID = %d" \
        % (media.PERSON, diary.PERSON, log.PERSON, int(personid))
    return db.query(dbo, sql)

def get_reserves_without_homechecks(dbo):
    """
    Returns owners that have a reservation but aren't homechecked
    """
    sql = get_person_query(dbo)
    sql += "INNER JOIN adoption a ON a.OwnerID = o.ID " \
        "WHERE a.MovementType = 0 AND a.ReservationDate Is Not Null AND a.ReservationCancelledDate Is Null AND o.IDCheck = 0"
    return db.query(dbo, sql)

def get_overdue_donations(dbo):
    """
    Returns owners that have an overdue regular donation
    """
    sql = get_person_query(dbo)
    sql += " INNER JOIN ownerdonation od ON od.OwnerID = o.ID " \
        "WHERE od.Date Is Null AND od.DateDue Is Not Null AND od.DateDue <= %s" % (db.dd(now(dbo.timezone)))
    return db.query(dbo, sql)

def get_links(dbo, pid):
    """
    Gets a list of all records that link to this person
    """
    l = dbo.locale
    linkdisplay = db.concat(dbo, ("a.ShelterCode", "' - '", "a.AnimalName"))
    animalextra = db.concat(dbo, ("a.BreedName", "' '", "s.SpeciesName", "' ('", 
        "CASE WHEN a.Archived = 0 AND a.ActiveMovementType = 2 THEN mt.MovementType " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Not Null AND a.ActiveMovementID = 0 THEN dr.ReasonName " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Null AND a.ActiveMovementID <> 0 THEN mt.MovementType " \
        "ELSE il.LocationName END", "')'"))
    sql = "SELECT 'OO' AS TYPE, " \
        "%s AS TYPEDISPLAY, a.DateBroughtIn AS DDATE, a.ID AS LINKID, " \
        "%s AS LINKDISPLAY, " \
        "%s AS FIELD2, " \
        "CASE WHEN a.DeceasedDate Is Not Null THEN 'D' ELSE '' END AS DMOD " \
        "FROM animal a " \
        "LEFT OUTER JOIN lksmovementtype mt ON mt.ID = a.ActiveMovementType " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "INNER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "WHERE OriginalOwnerID = %d " \
        "UNION SELECT 'BI' AS TYPE, " \
        "%s AS TYPEDISPLAY, a.DateBroughtIn AS DDATE, a.ID AS LINKID, " \
        "%s AS LINKDISPLAY, " \
        "%s AS FIELD2, " \
        "CASE WHEN a.DeceasedDate Is Not Null THEN 'D' ELSE '' END AS DMOD " \
        "FROM animal a " \
        "LEFT OUTER JOIN lksmovementtype mt ON mt.ID = a.ActiveMovementType " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "INNER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "WHERE BroughtInByOwnerID = %d " \
        "UNION SELECT 'PB' AS TYPE, " \
        "%s AS TYPEDISPLAY, a.DateBroughtIn AS DDATE, a.ID AS LINKID, " \
        "%s AS LINKDISPLAY, " \
        "%s AS FIELD2, " \
        "CASE WHEN a.DeceasedDate Is Not Null THEN 'D' ELSE '' END AS DMOD " \
        "FROM animal a " \
        "LEFT OUTER JOIN lksmovementtype mt ON mt.ID = a.ActiveMovementType " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "INNER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "WHERE PickedUpByOwnerID = %d " \
        "UNION SELECT 'OV' AS TYPE, " \
        "%s AS TYPEDISPLAY, a.DateBroughtIn AS DDATE, a.ID AS LINKID, " \
        "%s AS LINKDISPLAY, " \
        "'' AS FIELD2, '' AS DMOD FROM animal a WHERE OwnersVetID = %d " \
        "UNION SELECT 'CV' AS TYPE, " \
        "%s AS TYPEDISPLAY, a.DateBroughtIn AS DDATE, a.ID AS LINKID, " \
        "%s AS LINKDISPLAY, " \
        "'' AS FIELD2, '' AS DMOD FROM animal a WHERE CurrentVetID = %d " \
        "UNION SELECT 'WL' AS TYPE, " \
        "%s AS TYPEDISPLAY, a.DatePutOnList AS DDATE, a.ID AS LINKID, " \
        "s.SpeciesName AS LINKDISPLAY, " \
        "a.AnimalDescription AS FIELD2, '' AS DMOD FROM animalwaitinglist a " \
        "INNER JOIN species s ON s.ID = a.SpeciesID WHERE a.OwnerID = %d " \
        "UNION SELECT 'LA' AS TYPE, " \
        "%s AS TYPEDISPLAY, a.DateLost AS DDATE, a.ID AS LINKID, " \
        "s.SpeciesName AS LINKDISPLAY, " \
        "a.DistFeat AS FIELD2, '' AS DMOD FROM animallost a " \
        "INNER JOIN species s ON s.ID = a.AnimalTypeID WHERE a.OwnerID = %d " \
        "UNION SELECT 'FA' AS TYPE, " \
        "%s AS TYPEDISPLAY, a.DateFound AS DDATE, a.ID AS LINKID, " \
        "s.SpeciesName AS LINKDISPLAY, " \
        "a.DistFeat AS FIELD2, '' AS DMOD FROM animalfound a " \
        "INNER JOIN species s ON s.ID = a.AnimalTypeID WHERE a.OwnerID = %d " \
        "UNION SELECT 'AC' AS TYPE, " \
        "%s AS TYPEDISPLAY, a.IncidentDateTime AS DDATE, a.ID AS LINKID, " \
        "ti.IncidentName AS LINKDISPLAY, " \
        "a.CallNotes AS FIELD2, '' AS DMOD FROM animalcontrol a " \
        "INNER JOIN incidenttype ti ON ti.ID = a.IncidentTypeID WHERE a.OwnerID = %d OR a.Owner2ID = %d OR a.Owner3ID = %d " \
        "UNION SELECT 'AC' AS TYPE, " \
        "%s AS TYPEDISPLAY, a.IncidentDateTime AS DDATE, a.ID AS LINKID, " \
        "ti.IncidentName AS LINKDISPLAY, " \
        "a.CallNotes AS FIELD2, '' AS DMOD FROM animalcontrol a " \
        "INNER JOIN incidenttype ti ON ti.ID = a.IncidentTypeID WHERE a.CallerID = %d " \
        "UNION SELECT 'AC' AS TYPE, " \
        "%s AS TYPEDISPLAY, a.IncidentDateTime AS DDATE, a.ID AS LINKID, " \
        "ti.IncidentName AS LINKDISPLAY, " \
        "a.CallNotes AS FIELD2, '' AS DMOD FROM animalcontrol a " \
        "INNER JOIN incidenttype ti ON ti.ID = a.IncidentTypeID WHERE a.VictimID = %d " \
        "ORDER BY DDATE DESC, LINKDISPLAY" \
        % ( db.ds(_("Original Owner", l)), linkdisplay, animalextra, int(pid), 
        db.ds(_("Brought In By", l)), linkdisplay, animalextra, int(pid),
        db.ds(_("Picked Up By", l)), linkdisplay, animalextra, int(pid),
        db.ds(_("Owner Vet", l)), linkdisplay, int(pid), 
        db.ds(_("Current Vet", l)), linkdisplay, int(pid),
        db.ds(_("Waiting List Contact", l)), int(pid), 
        db.ds(_("Lost Animal Contact", l)), int(pid),
        db.ds(_("Found Animal Contact", l)), int(pid),
        db.ds(_("Animal Control Incident", l)), int(pid), int(pid), int(pid), 
        db.ds(_("Animal Control Caller", l)), int(pid), 
        db.ds(_("Animal Control Victim", l)), int(pid) )
    return db.query(dbo, sql)

def get_investigation(dbo, personid, sort = ASCENDING):
    """
    Returns investigation records for the given person:
    OWNERID, DATE, NOTES
    """
    sql = "SELECT o.* FROM ownerinvestigation o WHERE o.OwnerID = %d" % personid
    if sort == ASCENDING:
        sql += " ORDER BY o.Date"
    else:
        sql += " ORDER BY o.Date DESC"
    return db.query(dbo, sql)

def get_person_find_simple(dbo, query, classfilter="all", includeStaff = False, limit = 0):
    """
    Returns rows for simple person searches.
    query: The search criteria
    classfilter: One of all, vet, retailer, staff, fosterer, volunteer, shelter, 
                 aco, homechecked, homechecker, member, donor, driver
    """
    ors = []
    query = query.replace("'", "`")
    words = query.split(" ")
    def add(field):
        return utils.where_text_filter(dbo, field, query)
    onac = []
    for w in words:
        onac.append("(%s)" % utils.where_text_filter(dbo, "o.OwnerName", w))
    ors.append("(%s)" % " AND ".join(onac))
    ors.append(add("o.OwnerAddress"))
    ors.append(add("o.OwnerTown"))
    ors.append(add("o.OwnerCounty"))
    ors.append(add("o.OwnerPostcode"))
    ors.append(add("o.EmailAddress"))
    ors.append(add("o.HomeTelephone"))
    ors.append(add("o.WorkTelephone"))
    ors.append(add("o.MobileTelephone"))
    ors.append(add("o.MembershipNumber"))
    ors.append(u"EXISTS(SELECT ad.Value FROM additional ad " \
        "INNER JOIN additionalfield af ON af.ID = ad.AdditionalFieldID AND af.Searchable = 1 " \
        "WHERE ad.LinkID=o.ID AND ad.LinkType IN (%s) AND LOWER(ad.Value) LIKE '%%%s%%')" % (additional.PERSON_IN, query.lower()))
    if not dbo.is_large_db:
        ors.append(add(get_person_code_query(dbo)))
    cf = ""
    sf = ""
    if classfilter == "all":
        pass
    elif classfilter == "vet":
        cf = " AND o.IsVet = 1"
    elif classfilter == "retailer":
        cf = " AND o.IsRetailer = 1"
    elif classfilter == "staff":
        cf = " AND o.IsStaff = 1"
    elif classfilter == "fosterer":
        cf = " AND o.IsFosterer = 1"
    elif classfilter == "volunteer":
        cf = " AND o.IsVolunteer = 1"
    elif classfilter == "shelter":
        cf = " AND o.IsShelter = 1"
    elif classfilter == "aco":
        cf = " AND o.IsACO = 1"
    elif classfilter == "homechecked":
        cf = " AND o.IDCheck = 1"
    elif classfilter == "homechecker":
        cf = " AND o.IsHomeChecker = 1"
    elif classfilter == "member":
        cf = " AND o.IsMember = 1"
    elif classfilter == "donor":
        cf = " AND o.IsDonor = 1"
    elif classfilter == "driver":
        cf = " AND o.IsDriver = 1"
    if not includeStaff:
        sf = " AND o.IsStaff = 0"
    sql = unicode(get_person_query(dbo)) + " WHERE (" + u" OR ".join(ors) + ")" + cf + sf + " ORDER BY o.OwnerName"
    if limit > 0: sql += " LIMIT " + str(limit)
    return db.query(dbo, sql)

def get_person_find_advanced(dbo, criteria, includeStaff = False, limit = 0):
    """
    Returns rows for advanced person searches.
    criteria: A dictionary of criteria
       name - string partial pattern
       address - string partial pattern
       town - string partial pattern
       county - string partial pattern
       postcode - string partial pattern
       homecheck - string partial pattern
       comments - string partial pattern
       email - string partial pattern
       medianotes - string partial pattern
       filter - "all" "aco" "banned" "donor" "driver", "fosterer" "homechecked"
            "homechecker" "member" "retailer" "shelter" "staff" "giftaid"
            "vet" "volunteer"
    """
    c = []
    l = dbo.locale
    post = utils.PostedData(criteria, l)

    def hk(cfield):
        return post[cfield] != ""

    def crit(cfield):
        return post[cfield]

    def addstr(cfield, field): 
        if hk(cfield) and criteria[cfield] != "": 
            c.append("(LOWER(%s) LIKE '%%%s%%' OR LOWER(%s) LIKE '%%%s%%')" % ( 
                field, crit(cfield).lower().replace("'", "`"),
                field, utils.decode_html(crit(cfield).lower().replace(";", "`").replace("'", "`")) 
            ))

    def addwords(cfield, field):
        if hk(cfield) and crit(cfield) != "":
            words = crit(cfield).split(" ")
            for w in words:
                c.append("(LOWER(%s) LIKE '%%%s%%' OR LOWER(%s) LIKE '%%%s%%')" % (
                    field, w.lower(),
                    field, utils.decode_html(w.lower())
                ))

    addstr("code", get_person_code_query(dbo))
    addstr("name", "o.OwnerName")
    addstr("address", "o.OwnerAddress")
    addstr("town", "o.OwnerTown")
    addstr("county", "o.OwnerCounty")
    addstr("postcode", "o.OwnerPostcode")
    addstr("email", "o.EmailAddress")
    addwords("homecheck", "o.HomeCheckAreas")
    addwords("comments", "o.Comments")
    addwords("medianotes", "web.MediaNotes")
    if crit("filter") != "":
        for flag in crit("filter").split(","):
            if flag == "aco": c.append("o.IsACO=1")
            elif flag == "banned": c.append("o.IsBanned=1")
            elif flag == "deceased": c.append("o.IsDeceased=1")
            elif flag == "donor": c.append("o.IsDonor=1")
            elif flag == "driver": c.append("o.IsDriver=1")
            elif flag == "fosterer": c.append("o.IsFosterer=1")
            elif flag == "homechecked": c.append("o.IDCheck=1")
            elif flag == "homechecker": c.append("o.IsHomeChecker=1")
            elif flag == "member": c.append("o.IsMember=1")
            elif flag == "retailer": c.append("o.IsRetailer=1")
            elif flag == "shelter": c.append("o.IsShelter=1")
            elif flag == "staff": c.append("o.IsStaff=1")
            elif flag == "giftaid": c.append("o.IsGiftAid=1")
            elif flag == "vet": c.append("o.IsVet=1")
            elif flag == "volunteer": c.append("o.IsVolunteer=1")
            else: c.append("LOWER(o.AdditionalFlags) LIKE '%%%s%%'" % str(flag).lower())
    if not includeStaff:
        c.append("o.IsStaff = 0")
    if len(c) == 0:
        sql = get_person_query(dbo) + " ORDER BY o.OwnerName"
    else:
        sql = get_person_query(dbo) + " WHERE " + " AND ".join(c) + " ORDER BY o.OwnerName"
    if limit > 0: sql += " LIMIT " + str(limit)
    return db.query(dbo, sql)

def get_person_rota(dbo, personid):
    return db.query(dbo, get_rota_query(dbo) + " WHERE r.OwnerID = %d ORDER BY r.StartDateTime DESC LIMIT 100" % personid)

def get_rota(dbo, startdate, enddate):
    """ Returns rota records where start >= startdate and end < enddate """
    return db.query(dbo, get_rota_query(dbo) + \
        " WHERE r.StartDateTime >= %s AND r.EndDateTime < %s ORDER BY r.StartDateTime" % (db.dd(startdate), db.dd(enddate)))

def calculate_owner_name(dbo, title = "", initials = "", first = "", last = "", nameformat = ""):
    """
    Calculates the owner name field based on the current format.
    """
    if nameformat == "": nameformat = configuration.owner_name_format(dbo)
    # If something went wrong and we have a broken format for any reason, substitute our default
    if nameformat is None or nameformat == "" or nameformat == "null": nameformat = "{ownertitle} {ownerforenames} {ownersurname}",
    nameformat = nameformat.replace("{ownername}", "{ownertitle} {ownerforenames} {ownersurname}") # Compatibility with old versions
    nameformat = nameformat.replace("{ownertitle}", title)
    nameformat = nameformat.replace("{ownerinitials}", initials)
    nameformat = nameformat.replace("{ownerforenames}", first)
    nameformat = nameformat.replace("{ownersurname}", last)
    return nameformat.strip()

def update_owner_names(dbo):
    """
    Regenerates all owner name fields based on the current format.
    """
    al.debug("regenerating owner names...", "person.update_owner_names", dbo)
    own = db.query(dbo, "SELECT ID, OwnerTitle, OwnerInitials, OwnerForeNames, OwnerSurname FROM owner")
    nameformat = configuration.owner_name_format(dbo)
    for o in own:
        db.execute(dbo, "UPDATE owner SET OwnerName = %s WHERE ID = %d" % \
            (db.ds(calculate_owner_name(dbo, o["OWNERTITLE"], o["OWNERINITIALS"], o["OWNERFORENAMES"], o["OWNERSURNAME"], nameformat)), o["ID"]))
    al.debug("regenerated %d owner names" % len(own), "person.update_owner_names", dbo)

def update_person_from_form(dbo, post, username):
    """
    Updates an existing person record from incoming form data
    """
    pid = post.integer("id")
    flags = post["flags"].split(",")
    def bi(b): return b and 1 or 0
    homechecked = bi("homechecked" in flags)
    banned = bi("banned" in flags)
    volunteer = bi("volunteer" in flags)
    member = bi("member" in flags)
    homechecker = bi("homechecker" in flags)
    deceased = bi("deceased" in flags)
    donor = bi("donor" in flags)
    driver = bi("driver" in flags)
    shelter = bi("shelter" in flags)
    aco = bi("aco" in flags)
    staff = bi("staff" in flags)
    fosterer = bi("fosterer" in flags)
    retailer = bi("retailer" in flags)
    vet = bi("vet" in flags)
    giftaid = bi("giftaid" in flags)
    flagstr = "|".join(flags) + "|"
    sql = db.make_update_user_sql(dbo, "owner", username, "ID=%d" % pid, (
        ( "OwnerType", post.db_integer("ownertype") ),
        ( "OwnerName", db.ds(calculate_owner_name(dbo, post["title"], post["initials"], post["forenames"], post["surname"] ))),
        ( "OwnerTitle", post.db_string("title")),
        ( "OwnerInitials", post.db_string("initials")),
        ( "OwnerForenames", post.db_string("forenames")),
        ( "OwnerSurname", post.db_string("surname")),
        ( "OwnerAddress", post.db_string("address")),
        ( "OwnerTown", post.db_string("town")),
        ( "OwnerCounty", post.db_string("county")),
        ( "OwnerPostcode", post.db_string("postcode")),
        ( "LatLong", post.db_string("latlong")),
        ( "HomeTelephone", post.db_string("hometelephone")),
        ( "WorkTelephone", post.db_string("worktelephone")),
        ( "MobileTelephone", post.db_string("mobiletelephone")),
        ( "EmailAddress", post.db_string("email")),
        ( "ExcludeFromBulkEmail", post.db_boolean("excludefrombulkemail")),
        ( "IDCheck", db.di(homechecked) ),
        ( "Comments", post.db_string("comments")),
        ( "IsBanned", db.di(banned)),
        ( "IsVolunteer", db.di(volunteer)),
        ( "IsMember", db.di(member)),
        ( "MembershipExpiryDate", post.db_date("membershipexpires")),
        ( "MembershipNumber", post.db_string("membershipnumber")),
        ( "IsHomeChecker", db.di(homechecker)),
        ( "IsDeceased", db.di(deceased)),
        ( "IsDonor", db.di(donor)),
        ( "IsDriver", db.di(driver)),
        ( "IsShelter", db.di(shelter)),
        ( "IsACO", db.di(aco)),
        ( "IsStaff", db.di(staff)),
        ( "IsFosterer", db.di(fosterer)),
        ( "IsRetailer", db.di(retailer)),
        ( "IsVet", db.di(vet)),
        ( "IsGiftAid", db.di(giftaid)),
        ( "AdditionalFlags", db.ds(flagstr)),
        ( "HomeCheckAreas", post.db_string("areas")),
        ( "DateLastHomeChecked", post.db_date("homechecked")),
        ( "HomeCheckedBy", post.db_integer("homecheckedby")),
        ( "MatchActive", post.db_integer("matchactive")),
        ( "MatchAdded", post.db_date("matchadded")),
        ( "MatchExpires", post.db_date("matchexpires")),
        ( "MatchSex", post.db_integer("matchsex")),
        ( "MatchSize", post.db_integer("matchsize")),
        ( "MatchColour", post.db_integer("matchcolour")),
        ( "MatchAgeFrom", post.db_floating("agedfrom")),
        ( "MatchAgeTo", post.db_floating("agedto")),
        ( "MatchAnimalType", post.db_integer("matchtype")),
        ( "MatchSpecies", post.db_integer("matchspecies")),
        ( "MatchBreed", post.db_integer("matchbreed1")),
        ( "MatchBreed2", post.db_integer("matchbreed2")),
        ( "MatchGoodWithCats", post.db_integer("matchgoodwithcats")),
        ( "MatchGoodWithDogs", post.db_integer("matchgoodwithdogs")),
        ( "MatchGoodWithChildren", post.db_integer("matchgoodwithchildren")),
        ( "MatchHouseTrained", post.db_integer("matchhousetrained")),
        ( "MatchCommentsContain", post.db_string("commentscontain"))
    ))
    preaudit = db.query(dbo, "SELECT * FROM owner WHERE ID=%d" % pid)
    db.execute(dbo, sql)
    postaudit = db.query(dbo, "SELECT * FROM owner WHERE ID=%d" % pid)
    audit.edit(dbo, username, "owner", audit.map_diff(preaudit, postaudit, [ "OWNERNAME", ]))

    # Save any additional field values given
    additional.save_values_for_link(dbo, post, pid, "person")

def insert_person_from_form(dbo, post, username):
    """
    Creates a new person record from incoming form data
    Returns the ID of the new record
    """
    def d(key, default = None): 
        if post.data.has_key(key):
            return post[key]
        else:
            return default

    flags = post["flags"].split(",")
    def bi(b): return b and 1 or 0
    homechecked = bi("homechecked" in flags)
    banned = bi("banned" in flags)
    volunteer = bi("volunteer" in flags)
    member = bi("member" in flags)
    homechecker = bi("homechecker" in flags)
    donor = bi("donor" in flags)
    driver = bi("driver" in flags)
    deceased = bi("deceased" in flags)
    shelter = bi("shelter" in flags)
    aco = bi("aco" in flags)
    staff = bi("staff" in flags)
    fosterer = bi("fosterer" in flags)
    retailer = bi("retailer" in flags)
    vet = bi("vet" in flags)
    giftaid = bi("giftaid" in flags)
    flagstr = "|".join(flags) + "|"

    pid = db.get_id(dbo, "owner")
    sql = db.make_insert_user_sql(dbo, "owner", username, (
        ( "ID", db.di(pid) ),
        ( "OwnerName", db.ds(calculate_owner_name(dbo, post["title"], post["initials"], post["forenames"], post["surname"] ))),
        ( "OwnerType", post.db_integer("ownertype") ),
        ( "OwnerTitle", db.ds(d("title", "") )),
        ( "OwnerInitials", db.ds(d("initials", "") )),
        ( "OwnerForenames", db.ds(d("forenames", "") )),
        ( "OwnerSurname", db.ds(d("surname", "") )),
        ( "OwnerAddress", db.ds(d("address", "") )),
        ( "OwnerTown", db.ds(d("town", "") )),
        ( "OwnerCounty", db.ds(d("county", "") )),
        ( "OwnerPostcode", db.ds(d("postcode", "") )),
        ( "LatLong", db.ds(d("latlong", "") )),
        ( "HomeTelephone", db.ds(d("hometelephone", "") )),
        ( "WorkTelephone", db.ds(d("worktelephone", "") )),
        ( "MobileTelephone", db.ds(d("mobiletelephone", "") )),
        ( "EmailAddress", db.ds(d("emailaddress", "") )),
        ( "ExcludeFromBulkEmail", post.db_boolean("excludefrombulkemail")),
        ( "IDCheck", db.di(homechecked) ),
        ( "Comments", db.ds(d("comments") )),
        ( "IsBanned", db.di(banned)),
        ( "IsVolunteer", db.di(volunteer)),
        ( "IsMember", db.di(member)),
        ( "MembershipExpiryDate", db.dd(d("membershipexpires") )),
        ( "MembershipNumber", db.ds(d("membershipnumber"))),
        ( "IsHomeChecker", db.di(homechecker)),
        ( "IsDeceased", db.di(deceased)),
        ( "IsDonor", db.di(donor)),
        ( "IsDriver", db.di(driver)),
        ( "IsShelter", db.di(shelter)),
        ( "IsACO", db.di(aco)),
        ( "IsStaff", db.di(staff)),
        ( "IsFosterer", db.di(fosterer)),
        ( "IsRetailer", db.di(retailer)),
        ( "IsVet", db.di(vet)),
        ( "IsGiftAid", db.di(giftaid)),
        ( "AdditionalFlags", db.ds(flagstr)),
        ( "HomeCheckAreas", db.ds(d("homecheckareas", "") )),
        ( "DateLastHomeChecked", db.dd(d("datelasthomechecked") )),
        ( "HomeCheckedBy", db.di(d("homecheckedby", 0) )),
        ( "MatchAdded", db.dd(d("matchadded") )),
        ( "MatchExpires", db.dd(d("matchexpires") )),
        ( "MatchActive", db.di(d("matchactive", 0) )),
        ( "MatchSex", db.di(d("matchsex", -1) )),
        ( "MatchSize", db.di(d("matchsize", -1) )),
        ( "MatchColour", db.di(d("matchcolour", -1) )),
        ( "MatchAgeFrom", db.di(d("matchagefrom", 0) )),
        ( "MatchAgeTo", db.di(d("matchageto", 0) )),
        ( "MatchAnimalType", db.di(d("matchanimaltype", -1) )),
        ( "MatchSpecies", db.di(d("matchspecies", -1) )),
        ( "MatchBreed", db.di(d("matchbreed", -1) )),
        ( "MatchBreed2", db.di(d("matchbreed2", -1) )),
        ( "MatchGoodWithCats", db.di(d("matchgoodwithcats", -1) )),
        ( "MatchGoodWithDogs", db.di(d("matchgoodwithdogs", -1) )),
        ( "MatchGoodWithChildren", db.di(d("matchgoodwithchildren", -1) )),
        ( "MatchHouseTrained", db.di(d("matchhousetrained", -1) )),
        ( "MatchCommentsContain", db.ds(d("matchcommentscontain") )
    )))
    db.execute(dbo, sql)
    audit.create(dbo, username, "owner", str(pid) + " %s %s %s" % (d("title"), d("forenames"), d("surname")))
    return pid

def merge_person(dbo, username, personid, mergepersonid):
    """
    Reparents all satellite records of mergepersonid onto
    personid and then deletes it.
    """
    l = dbo.locale
    if personid == mergepersonid:
        raise utils.ASMValidationError(_("The person record to merge must be different from the original.", l))
    if personid == 0 or mergepersonid == 0:
        raise utils.ASMValidationError("Internal error: Cannot merge ID 0")
    def reparent(table, field, linktypefield = "", linktype = -1):
        if linktype >= 0:
            db.execute(dbo, "UPDATE %s SET %s = %d WHERE %s = %d AND %s = %d" % (table, field, personid, field, mergepersonid, linktypefield, linktype))
        else:
            db.execute(dbo, "UPDATE %s SET %s = %d WHERE %s = %d" % (table, field, personid, field, mergepersonid))
    reparent("adoption", "OwnerID")
    reparent("adoption", "RetailerID")
    reparent("animal", "OriginalOwnerID")
    reparent("animal", "BroughtInByOwnerID")
    reparent("animal", "OwnersVetID")
    reparent("animal", "CurrentVetID")
    reparent("animalcontrol", "CallerID")
    reparent("animalcontrol", "OwnerID")
    reparent("animalcontrol", "Owner2ID")
    reparent("animalcontrol", "Owner3ID")
    reparent("animalcontrol", "VictimID")
    reparent("animaltransport", "DriverOwnerID")
    reparent("animaltransport", "PickupOwnerID")
    reparent("animaltransport", "DropoffOwnerID")
    reparent("animallost", "OwnerID")
    reparent("animalfound", "OwnerID")
    reparent("animalwaitinglist", "OwnerID")
    reparent("ownercitation", "OwnerID")
    reparent("ownerdonation", "OwnerID")
    reparent("ownerinvestigation", "OwnerID")
    reparent("ownerlicence", "OwnerID")
    reparent("ownertraploan", "OwnerID")
    reparent("ownervoucher", "OwnerID")
    reparent("users", "OwnerID")
    reparent("media", "LinkID", "LinkTypeID", media.PERSON)
    reparent("diary", "LinkID", "LinkType", diary.PERSON)
    reparent("log", "LinkID", "LinkType", log.PERSON)
    audit.delete(dbo, username, "owner", str(db.query(dbo, "SELECT * FROM owner WHERE ID=%d" % mergepersonid)))
    db.execute(dbo, "DELETE FROM owner WHERE ID = %d" % mergepersonid)

def update_pass_homecheck(dbo, user, personid, comments):
    """
    Marks a person as homechecked and appends any comments supplied to their record.
    """
    by = users.get_personid(dbo, user)
    if by != 0: 
        db.execute(dbo, "UPDATE owner SET HomeCheckedBy = %d WHERE ID = %d" % (by, personid))
    db.execute(dbo, "UPDATE owner SET IDCheck = 1, DateLastHomeChecked = %s WHERE ID = %d" % ( db.dd(now(dbo.timezone)), personid ))
    if comments != "":
        com = db.query_string(dbo, "SELECT Comments FROM owner WHERE ID = %d" % personid)
        com += "\n" + comments
        db.execute(dbo, "UPDATE owner SET Comments = %s WHERE ID = %d" % ( db.ds(com), personid ))
  
def update_latlong(dbo, personid, latlong):
    """
    Updates the latlong field.
    """
    db.execute(dbo, "UPDATE owner SET LatLong = %s WHERE ID = %d" % (db.ds(latlong), int(personid)))

def delete_person(dbo, username, personid):
    """
    Deletes a person and all its satellite records.
    """
    l = dbo.locale
    if db.query_int(dbo, "SELECT COUNT(ID) FROM adoption WHERE OwnerID=%d OR RetailerID=%d" % (personid, personid)):
        raise utils.ASMValidationError(_("This person has movements and cannot be removed.", l))
    if db.query_int(dbo, "SELECT COUNT(ID) FROM animal WHERE BroughtInByOwnerID=%d OR OriginalOwnerID=%d OR CurrentVetID=%d OR OwnersVetID=%d" % (personid, personid, personid, personid)):
        raise utils.ASMValidationError(_("This person is linked to an animal and cannot be removed.", l))
    if db.query_int(dbo, "SELECT COUNT(ID) FROM ownerdonation WHERE OwnerID=%d" % personid):
        raise utils.ASMValidationError(_("This person has payments and cannot be removed.", l))
    if db.query_int(dbo, "SELECT COUNT(ID) FROM animallost WHERE OwnerID=%d" % personid):
        raise utils.ASMValidationError(_("This person is linked to lost animals and cannot be removed.", l))
    if db.query_int(dbo, "SELECT COUNT(ID) FROM animalfound WHERE OwnerID=%d" % personid):
        raise utils.ASMValidationError(_("This person is linked to found animals and cannot be removed.", l))
    if db.query_int(dbo, "SELECT COUNT(ID) FROM animalwaitinglist WHERE OwnerID=%d" % personid):
        raise utils.ASMValidationError(_("This person is linked to a waiting list record and cannot be removed.", l))
    if db.query_int(dbo, "SELECT COUNT(ID) FROM ownercitation WHERE OwnerID=%d" % personid):
        raise utils.ASMValidationError(_("This person is linked to citations and cannot be removed.", l))
    if db.query_int(dbo, "SELECT COUNT(ID) FROM ownertraploan WHERE OwnerID=%d" % personid):
        raise utils.ASMValidationError(_("This person is linked to trap loans and cannot be removed.", l))
    if db.query_int(dbo, "SELECT COUNT(ID) FROM ownerinvestigation WHERE OwnerID=%d" % personid):
        raise utils.ASMValidationError(_("This person is linked to an investigation and cannot be removed.", l))
    if db.query_int(dbo, "SELECT COUNT(ID) FROM ownerlicence WHERE OwnerID=%d" % personid):
        raise utils.ASMValidationError(_("This person is linked to animal licenses and cannot be removed.", l))
    if db.query_int(dbo, "SELECT COUNT(ID) FROM animalcontrol WHERE OwnerID=%d OR Owner2ID=%d OR Owner3ID = %d OR CallerID=%d OR VictimID=%d" % (personid, personid, personid, personid, personid)):
        raise utils.ASMValidationError(_("This person is linked to animal control and cannot be removed.", l))
    if db.query_int(dbo, "SELECT COUNT(ID) FROM animaltransport WHERE DriverOwnerID=%d OR PickupOwnerID=%d OR DropoffOwnerID=%d" % (personid, personid, personid)):
        raise utils.ASMValidationError(_("This person is linked to animal transportation and cannot be removed.", l))
    animals = db.query(dbo, "SELECT AnimalID FROM adoption WHERE OwnerID = %d" % personid)
    audit.delete(dbo, username, "owner", str(db.query(dbo, "SELECT * FROM owner WHERE ID=%d" % personid)))
    db.execute(dbo, "DELETE FROM media WHERE LinkID = %d AND LinkTypeID = %d" % (personid, 1))
    db.execute(dbo, "DELETE FROM diary WHERE LinkID = %d AND LinkType = %d" % (personid, 2))
    db.execute(dbo, "DELETE FROM log WHERE LinkID = %d AND LinkType = %d" % (personid, 1))
    db.execute(dbo, "DELETE FROM additional WHERE LinkID = %d AND LinkType IN (%s)" % (personid, additional.PERSON_IN))
    db.execute(dbo, "DELETE FROM adoption WHERE OwnerID = %d" % personid)
    db.execute(dbo, "DELETE FROM ownerdonation WHERE OwnerID = %d" % personid)
    db.execute(dbo, "DELETE FROM ownervoucher WHERE OwnerID = %d" % personid)
    dbfs.delete_path(dbo, "/owner/%d" % personid)
    db.execute(dbo, "DELETE FROM owner WHERE ID = %d" % personid)
    # Now that we've removed the person, update any animals that were previously
    # attached to it so that they return to the shelter.
    for a in animals:
        animal.update_animal_status(dbo, int(a["ANIMALID"]))
        animal.update_variable_animal_data(dbo, int(a["ANIMALID"]))

def insert_rota_from_form(dbo, username, post):
    """
    Creates a rota record from posted form data
    """
    nrota = db.get_id(dbo, "ownerrota")
    sql = db.make_insert_user_sql(dbo, "ownerrota", username, ( 
        ( "ID", db.di(nrota)),
        ( "OwnerID", post.db_integer("person")),
        ( "StartDateTime", post.db_datetime("startdate", "starttime")),
        ( "EndDateTime", post.db_datetime("enddate", "endtime")),
        ( "RotaTypeID", post.db_integer("type")),
        ( "Comments", post.db_string("comments"))
        ))
    db.execute(dbo, sql)
    audit.create(dbo, username, "ownerrota", str(nrota))
    return nrota

def update_rota_from_form(dbo, username, post):
    """
    Updates a rota record from posted form data
    """
    rotaid = post.integer("rotaid")
    sql = db.make_update_user_sql(dbo, "ownerrota", username, "ID=%d" % rotaid, ( 
        ( "OwnerID", post.db_integer("person")),
        ( "StartDateTime", post.db_datetime("startdate", "starttime")),
        ( "EndDateTime", post.db_datetime("enddate", "endtime")),
        ( "RotaTypeID", post.db_integer("type")),
        ( "Comments", post.db_string("comments"))
        ))
    preaudit = db.query(dbo, "SELECT * FROM ownerrota WHERE ID = %d" % rotaid)
    db.execute(dbo, sql)
    postaudit = db.query(dbo, "SELECT * FROM ownerrota WHERE ID = %d" % rotaid)
    audit.edit(dbo, username, "ownerrota", audit.map_diff(preaudit, postaudit))

def delete_rota(dbo, username, rid):
    """
    Deletes the selected rota record
    """
    audit.delete(dbo, username, "ownerrota", str(db.query(dbo, "SELECT * FROM ownerrota WHERE ID=%d" % int(rid))))
    db.execute(dbo, "DELETE FROM ownerrota WHERE ID = %d" % int(rid))

def insert_investigation_from_form(dbo, username, post):
    """
    Creates an investigation record from posted form data
    """
    ninv = db.get_id(dbo, "ownerinvestigation")
    sql = db.make_insert_user_sql(dbo, "ownerinvestigation", username, ( 
        ( "ID", db.di(ninv)),
        ( "OwnerID", post.db_integer("personid")),
        ( "Date", post.db_date("date")),
        ( "Notes", post.db_string("notes"))
        ))
    db.execute(dbo, sql)
    audit.create(dbo, username, "ownerinvestigation", str(ninv))
    return ninv

def update_investigation_from_form(dbo, username, post):
    """
    Updates an investigation record from posted form data
    """
    investigationid = post.integer("investigationid")
    sql = db.make_update_user_sql(dbo, "ownerinvestigation", username, "ID=%d" % investigationid, ( 
        ( "Date", post.db_date("date")),
        ( "Notes", post.db_string("notes"))
        ))
    preaudit = db.query(dbo, "SELECT * FROM ownerinvestigation WHERE ID = %d" % investigationid)
    db.execute(dbo, sql)
    postaudit = db.query(dbo, "SELECT * FROM ownerinvestigation WHERE ID = %d" % investigationid)
    audit.edit(dbo, username, "ownerinvestigation", audit.map_diff(preaudit, postaudit))

def delete_investigation(dbo, username, iid):
    """
    Deletes the selected investigation record
    """
    audit.delete(dbo, username, "ownerinvestigation", str(db.query(dbo, "SELECT * FROM ownerinvestigation WHERE ID=%d" % int(iid))))
    db.execute(dbo, "DELETE FROM ownerinvestigation WHERE ID = %d" % int(iid))

def send_email_from_form(dbo, username, post):
    """
    Sends an email to a person from a posted form. Attaches it as
    a log entry if specified.
    """
    emailfrom = post["from"]
    emailto = post["to"]
    emailcc = post["cc"]
    subject = post["subject"]
    ishtml = post.boolean("html")
    addtolog = post.boolean("addtolog")
    logtype = post.integer("logtype")
    body = post["body"]
    rv = utils.send_email(dbo, emailfrom, emailto, emailcc, subject, body, ishtml == 1 and "html" or "plain")
    if addtolog == 1:
        log.add_log(dbo, username, log.PERSON, post.integer("personid"), logtype, body)
    return rv

def lookingfor_report(dbo, username = "system"):
    """
    Generates the person looking for report
    """
    l = dbo.locale
    title = _("People Looking For", l)
    h = []
    h.append(reports.get_report_header(dbo, title, username))
    def p(s): return "<p>%s</p>" % s
    def td(s): return "<td>%s</td>" % s
    def hr(): return "<hr />"
  
    people = db.query(dbo, "SELECT owner.*, " \
        "(SELECT Size FROM lksize WHERE ID = owner.MatchSize) AS MatchSizeName, " \
        "(SELECT BaseColour FROM basecolour WHERE ID = owner.MatchColour) AS MatchColourName, " \
        "(SELECT Sex FROM lksex WHERE ID = owner.MatchSex) AS MatchSexName, " \
        "(SELECT BreedName FROM breed WHERE ID = owner.MatchBreed) AS MatchBreedName, " \
        "(SELECT AnimalType FROM animaltype WHERE ID = owner.MatchAnimalType) AS MatchAnimalTypeName, " \
        "(SELECT SpeciesName FROM species WHERE ID = owner.MatchSpecies) AS MatchSpeciesName " \
        "FROM owner WHERE MatchActive = 1 AND " \
        "(MatchExpires Is Null OR MatchExpires > %s)" \
        "ORDER BY OwnerName" % db.dd(now(dbo.timezone)))

    ah = []
    ah.append(hr())
    ah.append("<table border=\"1\" width=\"100%\"><tr>")
    ah.append( "<th>%s</th>" % _("Code", l))
    ah.append( "<th>%s</th>" % _("Name", l))
    ah.append( "<th>%s</th>" % _("Age", l))
    ah.append( "<th>%s</th>" % _("Sex", l))
    ah.append( "<th>%s</th>" % _("Size", l))
    ah.append( "<th>%s</th>" % _("Color", l))
    ah.append( "<th>%s</th>" % _("Species", l))
    ah.append( "<th>%s</th>" % _("Breed", l))
    ah.append( "<th>%s</th>" % _("Good with cats", l))
    ah.append( "<th>%s</th>" % _("Good with dogs", l))
    ah.append( "<th>%s</th>" % _("Good with children", l))
    ah.append( "<th>%s</th>" % _("Housetrained", l))
    ah.append( "<th>%s</th>" % _("Comments", l))
    ah.append( "</tr>")

    totalmatches = 0
    for p in people:
        sql = []
        if p["MATCHANIMALTYPE"] > 0: sql.append(" AND a.AnimalTypeID = %d" % int(p["MATCHANIMALTYPE"]))
        if p["MATCHSPECIES"] > 0: sql.append(" AND a.SpeciesID = %d" % int(p["MATCHSPECIES"]))
        if p["MATCHBREED"] > 0: sql.append(" AND (a.BreedID = %d OR a.Breed2ID = %d)" % (int(p["MATCHBREED"]), int(p["MATCHBREED"])))
        if p["MATCHSEX"] > -1: sql.append(" AND a.Sex = %d" % int(p["MATCHSEX"]))
        if p["MATCHSIZE"] > -1: sql.append(" AND a.Size = %d" % int(p["MATCHSIZE"]))
        if p["MATCHCOLOUR"] > -1: sql.append(" AND a.BaseColourID = %d" % int(p["MATCHCOLOUR"]))
        if p["MATCHGOODWITHCHILDREN"] == 0: sql.append(" AND a.IsGoodWithChildren = 0")
        if p["MATCHGOODWITHCATS"] == 0: sql.append(" AND a.IsGoodWithCats = 0")
        if p["MATCHGOODWITHDOGS"] == 0: sql.append(" AND a.IsGoodWithDogs = 0")
        if p["MATCHHOUSETRAINED"] == 0: sql.append(" AND a.IsHouseTrained = 0")
        if p["MATCHAGEFROM"] >= 0 and p["MATCHAGETO"] > 0: 
            sql.append(" AND a.DateOfBirth BETWEEN %s AND %s" % (db.dd(subtract_years(now(dbo.timezone), p["MATCHAGETO"])), \
                db.dd(subtract_years(now(dbo.timezone), p["MATCHAGEFROM"]))))
        if p["MATCHCOMMENTSCONTAIN"] is not None and p["MATCHCOMMENTSCONTAIN"] != "":
            for w in str(p["MATCHCOMMENTSCONTAIN"]).split(" "):
                sql.append(" AND a.AnimalComments Like '%%%s%%'" % w.replace("'", "`"))
        animals = db.query(dbo, animal.get_animal_query(dbo) + " WHERE a.Archived=0 AND a.IsNotAvailableForAdoption=0 AND a.HasActiveReserve=0 AND a.CrueltyCase=0 AND a.DeceasedDate Is Null" + "".join(sql))

        h.append("<h2>%s (%s) %s %s</h2>" % (p["OWNERNAME"], p["OWNERADDRESS"], p["HOMETELEPHONE"], p["MOBILETELEPHONE"]))
        c = []
        if p["MATCHSIZE"] != -1: c.append(p["MATCHSIZENAME"])
        if p["MATCHCOLOUR"] != -1: c.append(p["MATCHCOLOURNAME"])
        if p["MATCHSEX"] != -1: c.append(p["MATCHSEXNAME"])
        if p["MATCHBREED"] != -1: c.append(p["MATCHBREEDNAME"])
        if p["MATCHSPECIES"] != -1: c.append(p["MATCHSPECIESNAME"])
        if p["MATCHANIMALTYPE"] != -1: c.append(p["MATCHANIMALTYPENAME"])
        if p["MATCHGOODWITHCHILDREN"] == 0: c.append(_("Good with kids", l))
        if p["MATCHGOODWITHCATS"] == 0: c.append(_("Good with cats", l))
        if p["MATCHGOODWITHDOGS"] == 0: c.append(_("Good with dogs", l))
        if p["MATCHHOUSETRAINED"] == 0: c.append(_("Housetrained", l))
        if p["MATCHAGEFROM"] >= 0 and p["MATCHAGETO"] > 0: c.append(_("Age", l) + (" %0.2f - %0.2f" % (p["MATCHAGEFROM"], p["MATCHAGETO"])))
        if p["MATCHCOMMENTSCONTAIN"] is not None and p["MATCHCOMMENTSCONTAIN"] != "": c.append(_("Comments Contain", l) + ": " + p["MATCHCOMMENTSCONTAIN"])
        if p["COMMENTS"] != "" and p["COMMENTS"] is not None: 
            h.append( "<p style='font-size: 8pt'>%s</p>" % p["COMMENTS"])
        if len(c) > 0:
            h.append( "<p style='font-size: 8pt'>(%s: %s)</p>" % (_("Looking for", l), ", ".join(x for x in c if x is not None)))

        outputheader = False
        for a in animals:
            if not outputheader:
                outputheader = True
                h.append("".join(ah))
            totalmatches += 1
            h.append( "<tr>")
            h.append( td(a["CODE"]))
            h.append( td(a["ANIMALNAME"]))
            h.append( td(a["ANIMALAGE"]))
            h.append( td(a["SEXNAME"]))
            h.append( td(a["SIZENAME"]))
            h.append( td(a["BASECOLOURNAME"]))
            h.append( td(a["SPECIESNAME"]))
            h.append( td(a["BREEDNAME"]))
            h.append( td(a["ISGOODWITHCATSNAME"]))
            h.append( td(a["ISGOODWITHDOGSNAME"]))
            h.append( td(a["ISGOODWITHCHILDRENNAME"]))
            h.append( td(a["ISHOUSETRAINEDNAME"]))
            h.append( td(a["ANIMALCOMMENTS"]))

        if outputheader:
            h.append( "</table>")
        h.append( hr())

    if len(people) == 0:
        h.append( p(_("No matches found.", l)))

    h.append( "<!-- $AM%d^ animal matches -->" % totalmatches)
    h.append( reports.get_report_footer(dbo, title, username))
    return "".join(h)

def lookingfor_last_match_count(dbo):
    """
    Inspects the cached version of the looking for report and
    returns the number of animal matches.
    """
    s = dbfs.get_string_filepath(dbo, "/reports/daily/lookingfor.html")
    sp = s.find("$AM")
    if sp == -1: return 0
    return utils.cint(s[sp+3:s.find("^", sp)])

def update_missing_geocodes(dbo):
    """
    Goes through all people records without geocodes and completes
    the missing ones, using our configured bulk geocoding service.
    We limit this to LIMIT geocode requests per call so that databases with
    a lot of historical data don't end up tying up the daily
    batch for a long time, they'll just slowly complete over time.
    """
    if not BULK_GEO_BATCH:
        al.warn("BULK_GEO_BATCH is False, skipping", "update_missing_geocodes", dbo)
        return
    LIMIT = 50
    people = db.query(dbo, "SELECT ID, OwnerAddress, OwnerTown, OwnerCounty, OwnerPostcode " \
        "FROM owner WHERE LatLong Is Null OR LatLong = '' LIMIT %d" % LIMIT)
    batch = []
    for p in people:
        latlong = geo.get_lat_long(dbo, p["OWNERADDRESS"], p["OWNERTOWN"], p["OWNERCOUNTY"], p["OWNERPOSTCODE"])
        if latlong is not None:
            batch.append((latlong, p["ID"]))
    db.execute_many(dbo, "UPDATE owner SET LatLong = %s WHERE ID = %s", batch)
    al.debug("updated %d person geocodes" % len(batch), "person.update_missing_geocodes", dbo)

def update_lookingfor_report(dbo):
    """
    Updates the latest version of the looking for report in the dbfs
    """
    al.debug("updating lookingfor report", "person.update_lookingfor_report", dbo)
    s = lookingfor_report(dbo)
    dbfs.put_string_filepath(dbo, "/reports/daily/lookingfor.html", s)
    configuration.lookingfor_last_match_count(dbo, lookingfor_last_match_count(dbo))


