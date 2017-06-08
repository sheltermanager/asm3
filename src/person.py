#!/usr/bin/python

import additional
import al
import animal
import async
import audit
import configuration
import datetime
import dbfs
import diary
import db
import geo
import log
import media
import reports
import users
import utils
from i18n import _, add_days, date_diff_days, format_time, python2display, subtract_years, now
from sitedefs import BULK_GEO_BATCH, BULK_GEO_LIMIT

ASCENDING = 0
DESCENDING = 1

def get_homechecked(dbo, personid):
    """
    Returns a list of people homechecked by personid
    """
    return db.query(dbo, "SELECT ID, OwnerName, DateLastHomeChecked, Comments FROM owner " \
        "WHERE HomeCheckedBy = %d" % int(personid))

def get_person_query(dbo):
    """
    Returns the SELECT and JOIN commands necessary for selecting
    person rows with resolved lookups.
    """
    return "SELECT o.*, o.ID AS PersonID, " \
        "ho.OwnerName AS HomeCheckedByName, ho.HomeTelephone AS HomeCheckedByHomeTelephone, " \
        "ho.MobileTelephone AS HomeCheckedByMobileTelephone, ho.EmailAddress AS HomeCheckedByEmail, " \
        "web.MediaName AS WebsiteMediaName, " \
        "web.Date AS WebsiteMediaDate, " \
        "web.MediaNotes AS WebsiteMediaNotes, " \
        "(SELECT COUNT(oi.ID) FROM ownerinvestigation oi WHERE oi.OwnerID = o.ID) AS Investigation, " \
        "(SELECT COUNT(ac.ID) FROM animalcontrol ac WHERE ac.OwnerID = o.ID OR ac.Owner2ID = o.ID or ac.Owner3ID = o.ID) AS Incident " \
        "FROM owner o " \
        "LEFT OUTER JOIN owner ho ON ho.ID = o.HomeCheckedBy " \
        "LEFT OUTER JOIN media web ON web.LinkID = o.ID AND web.LinkTypeID = 3 AND web.WebsitePhoto = 1 "

def get_rota_query(dbo):
    """
    Returns the SELECT and JOIN commands necessary for selecting from rota hours
    """
    return "SELECT r.*, o.OwnerName, o.AdditionalFlags, rt.RotaType AS RotaTypeName, wt.WorkType AS WorkTypeName " \
        "FROM ownerrota r " \
        "LEFT OUTER JOIN lksrotatype rt ON rt.ID = r.RotaTypeID " \
        "LEFT OUTER JOIN lkworktype wt ON wt.ID = r.WorkTypeID " \
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

def get_person_similar(dbo, email = "", surname = "", forenames = "", address = ""):
    """
    Returns people with similar email, names and addresses to those supplied.
    """
    # Consider the first word rather than first address line - typically house
    # number/name and unlikely to be the same for different people
    if address.find(" ") != -1: address = address[0:address.find(" ")]
    if address.find("\n") != -1: address = address[0:address.find("\n")]
    if address.find(",") != -1: address = address[0:address.find(",")]
    address = address.replace("'", "`").lower().strip()
    forenames = forenames.replace("'", "`").lower().strip()
    if forenames.find(" ") != -1: forenames = forenames[0:forenames.find(" ")]
    surname = surname.replace("'", "`").lower().strip()
    email = email.replace("'", "`").lower().strip()
    eq = []
    if email != "" and email.find("@") != -1 and email.find(".") != -1:
        eq = db.query(dbo, get_person_query(dbo) + "WHERE LOWER(o.EmailAddress) LIKE '%s'" % email)
    per = db.query(dbo, get_person_query(dbo) + "WHERE LOWER(o.OwnerSurname) LIKE '%s' AND " \
        "LOWER(o.OwnerForeNames) LIKE '%s%%' AND LOWER(o.OwnerAddress) Like '%s%%'" % (surname, forenames, address))
    return eq + per

def get_person_name(dbo, personid):
    """
    Returns the full person name for an id
    """
    return db.query_string(dbo, "SELECT OwnerName FROM owner WHERE ID = %d" % int(personid))

def get_person_name_code(dbo, personid):
    """
    Returns the person name and code for an id
    """
    r = db.query(dbo, "SELECT o.OwnerName, o.OwnerCode FROM owner o WHERE o.ID = %d" % int(personid))
    if len(r) == 0: return ""
    return "%s - %s" % (r[0]["OWNERNAME"], r[0]["OWNERCODE"])

def get_person_name_addresses(dbo):
    """
    Returns the person name and address for everyone on file
    """
    return db.query(dbo, "SELECT o.ID, o.OwnerName, o.OwnerAddress FROM owner o ORDER BY o.OwnerName")

def get_fosterers(dbo):
    """
    Returns all fosterers
    """
    return db.query(dbo, get_person_query(dbo) + " WHERE o.IsFosterer = 1 ORDER BY o.OwnerName")

def get_shelterview_fosterers(dbo):
    """
    Returns all fosterers with the just the minimum info required for shelterview
    """
    return db.query(dbo, "SELECT o.ID, o.OwnerName, o.FosterCapacity FROM owner o WHERE o.IsFosterer = 1 ORDER BY o.OwnerName")

def get_staff_volunteers(dbo):
    """
    Returns all staff and volunteers
    """
    return db.query(dbo, get_person_query(dbo) + " WHERE o.IsStaff = 1 OR o.IsVolunteer = 1 ORDER BY o.IsStaff DESC, o.OwnerName")

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
        tc.append("%s^^%s" % (r["OWNERTOWN"], r["OWNERCOUNTY"]))
    return tc

def get_counties(dbo):
    """
    Returns a list of counties
    """
    rows = db.query(dbo, "SELECT DISTINCT OwnerCounty FROM owner")
    if rows is None: return []
    counties = []
    for r in rows:
        counties.append("%s" % r["OWNERCOUNTY"])
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
        "((SELECT COUNT(*) FROM animal WHERE AdoptionCoordinatorID = o.ID OR BroughtInByOwnerID = o.ID OR OriginalOwnerID = o.ID OR CurrentVETID = o.ID OR OwnersVetID = o.ID) + " \
        "(SELECT COUNT(*) FROM animalwaitinglist WHERE OwnerID = o.ID) + " \
        "(SELECT COUNT(*) FROM animalfound WHERE OwnerID = o.ID) + " \
        "(SELECT COUNT(*) FROM animallost WHERE OwnerID = o.ID) + " \
        "(SELECT COUNT(*) FROM animaltransport WHERE DriverOwnerID = o.ID) + " \
        "(SELECT COUNT(*) FROM animalcontrol WHERE CallerID = o.ID OR VictimID = o.ID " \
        "OR OwnerID = o.ID OR Owner2ID = o.ID or Owner3ID = o.ID) + " \
        "(SELECT COUNT(*) FROM additional af INNER JOIN additionalfield aff ON aff.ID = af.AdditionalFieldID " \
        "WHERE aff.FieldType = %d AND af.Value = '%d') " \
        ") AS links " \
        "FROM owner o WHERE o.ID = %d" \
        % (media.PERSON, diary.PERSON, log.PERSON, additional.PERSON_LOOKUP, int(personid), int(personid))
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
    linkdisplay = dbo.sql_concat(("a.ShelterCode", "' - '", "a.AnimalName"))
    animalextra = dbo.sql_concat(("a.BreedName", "' '", "s.SpeciesName", "' ('", 
        "CASE WHEN a.Archived = 0 AND a.ActiveMovementType = 2 THEN mt.MovementType " \
        "WHEN a.NonShelterAnimal = 1 THEN '' " \
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
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " \
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
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "WHERE BroughtInByOwnerID = %d " \
        "UNION SELECT 'AO' AS TYPE, " \
        "%s AS TYPEDISPLAY, a.DateBroughtIn AS DDATE, a.ID AS LINKID, " \
        "%s AS LINKDISPLAY, " \
        "%s AS FIELD2, " \
        "CASE WHEN a.DeceasedDate Is Not Null THEN 'D' ELSE '' END AS DMOD " \
        "FROM animal a " \
        "LEFT OUTER JOIN lksmovementtype mt ON mt.ID = a.ActiveMovementType " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "WHERE AdoptionCoordinatorID = %d " \
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
        "UNION SELECT 'AT' AS TYPE, " \
        "%s AS TYPEDISPLAY, t.PickupDateTime AS DDATE, t.AnimalID AS LINKID, " \
        "%s LINKDISPLAY, " \
        "t.DropOffAddress AS FIELD2, '' AS DMOD FROM animaltransport t " \
        "INNER JOIN animal a ON a.ID = t.AnimalID " \
        "WHERE t.DriverOwnerID = %d " \
        "UNION SELECT 'AP' AS TYPE, " \
        "aff.FieldLabel AS TYPEDISPLAY, a.LastChangedDate AS DDATE, a.ID AS LINKID, " \
        "%s LINKDISPLAY, " \
        "%s AS FIELD2, " \
        "CASE WHEN a.DeceasedDate Is Not Null THEN 'D' ELSE '' END AS DMOD " \
        "FROM additional af " \
        "INNER JOIN additionalfield aff ON aff.ID = af.AdditionalFieldID " \
        "INNER JOIN animal a ON a.ID = af.LinkID " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN lksmovementtype mt ON mt.ID = a.ActiveMovementType " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "WHERE af.Value = '%d' AND aff.FieldType = %s AND aff.LinkType IN (%s) " \
        "ORDER BY DDATE DESC, LINKDISPLAY" \
        % ( db.ds(_("Original Owner", l)), linkdisplay, animalextra, int(pid), 
        db.ds(_("Brought In By", l)), linkdisplay, animalextra, int(pid),
        db.ds(_("Adoption Coordinator", l)), linkdisplay, animalextra, int(pid),
        db.ds(_("Owner Vet", l)), linkdisplay, int(pid), 
        db.ds(_("Current Vet", l)), linkdisplay, int(pid),
        db.ds(_("Waiting List Contact", l)), int(pid), 
        db.ds(_("Lost Animal Contact", l)), int(pid),
        db.ds(_("Found Animal Contact", l)), int(pid),
        db.ds(_("Animal Control Incident", l)), int(pid), int(pid), int(pid), 
        db.ds(_("Animal Control Caller", l)), int(pid), 
        db.ds(_("Animal Control Victim", l)), int(pid),
        db.ds(_("Driver", l)), linkdisplay, int(pid),
        linkdisplay, animalextra, int(pid), additional.PERSON_LOOKUP, additional.clause_for_linktype("animal") ) 
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

def get_person_find_simple(dbo, query, username="", classfilter="all", includeStaff = False, includeVolunteers = False, limit = 0):
    """
    Returns rows for simple person searches.
    query: The search criteria
    classfilter: One of all, vet, retailer, staff, fosterer, volunteer, shelter, 
                 aco, banned, homechecked, homechecker, member, donor, driver, volunteerandstaff
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
    ors.append(add("o.OwnerCode"))
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
    cf = ""
    if classfilter == "all":
        pass
    elif classfilter == "coordinator":
        cf = " AND o.IsAdoptionCoordinator = 1"
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
    elif classfilter == "volunteerandstaff":
        cf = " AND (o.IsVolunteer = 1 OR o.IsStaff = 1)"
    elif classfilter == "shelter":
        cf = " AND o.IsShelter = 1"
    elif classfilter == "aco":
        cf = " AND o.IsACO = 1"
    elif classfilter == "banned":
        cf = " AND o.IsBanned = 1"
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
        cf = " AND o.IsStaff = 0"
    if not includeVolunteers:
        cf = " AND o.IsVolunteer = 0"
    sql = utils.cunicode(get_person_query(dbo)) + " WHERE (" + u" OR ".join(ors) + ")" + cf + " ORDER BY o.OwnerName"
    return reduce_find_results(dbo, username, db.query(dbo, sql, limit=limit))

def get_person_find_advanced(dbo, criteria, username, includeStaff = False, limit = 0):
    """
    Returns rows for advanced person searches.
    criteria: A dictionary of criteria
       code - string partial pattern
       createdby - string partial pattern
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
            x = crit(cfield).lower().replace("'", "`")
            c.append("(LOWER(%s) LIKE '%%%s%%' OR LOWER(%s) LIKE '%%%s%%')" % ( 
                field, x,
                field, utils.decode_html(x) 
            ))

    def addwords(cfield, field):
        if hk(cfield) and crit(cfield) != "":
            words = crit(cfield).split(" ")
            for w in words:
                x = w.lower().replace("'", "`")
                c.append("(LOWER(%s) LIKE '%%%s%%' OR LOWER(%s) LIKE '%%%s%%')" % (
                    field, x,
                    field, utils.decode_html(x)
                ))

    addstr("code", "o.OwnerCode")
    addstr("createdby", "o.CreatedBy")
    addwords("name", "o.OwnerName")
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
            elif flag == "coordinator": c.append("o.IsAdoptionCoordinator=1")
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
            else: c.append("LOWER(o.AdditionalFlags) LIKE %s" % db.ds("%%%s%%" % flag.lower()))
    if not includeStaff:
        c.append("o.IsStaff = 0")
    if len(c) == 0:
        sql = get_person_query(dbo) + " ORDER BY o.OwnerName"
    else:
        sql = get_person_query(dbo) + " WHERE " + " AND ".join(c) + " ORDER BY o.OwnerName"
    return reduce_find_results(dbo, username, db.query(dbo, sql, limit=limit))

def reduce_find_results(dbo, username, rows):
    """
    Given the results of a find operation, goes through the results and removes 
    any results which the user does not have permission to view. So far, this is because:
    1. Multi-site is on, there's a site on the person that is not the current users
    """
    # Do nothing if there are no results
    if len(rows) == 0: return rows
    u = db.query(dbo, "SELECT * FROM users WHERE UserName = %s" % db.ds(username))
    # Do nothing if we can't find the user
    if len(u) == 0: return rows
    # Do nothing if the user has no site
    u = u[0]
    if u["SITEID"] == 0: return rows
    # Remove rows where the user doesn't have that site
    results = []
    for r in rows:
        # Compare the site ID on the  person to our user - to exclude the record,
        # both user and person must have a site ID and they must be different
        if r["SITEID"] != 0 and r["SITEID"] != u["SITEID"]: continue
        results.append(r)
    return results

def get_person_rota(dbo, personid):
    return db.query(dbo, get_rota_query(dbo) + " WHERE r.OwnerID = %d ORDER BY r.StartDateTime DESC" % personid, limit=100)

def get_rota(dbo, startdate, enddate):
    """ Returns rota records that apply between the two dates given """
    return db.query(dbo, get_rota_query(dbo) + \
        " WHERE (r.StartDateTime >= %(start)s AND r.StartDateTime < %(end)s)" \
        " OR (r.EndDateTime >= %(start)s AND r.EndDateTime < %(end)s)" \
        " OR (r.StartDateTime < %(start)s AND r.EndDateTime >= %(start)s) " \
        " ORDER BY r.StartDateTime" % { "start": db.dd(startdate), "end": db.dd(enddate) })

def clone_rota_week(dbo, username, startdate, newdate, flags):
    """ Copies a weeks worth of rota records from startdate to newdate """
    l = dbo.locale
    if startdate is None or newdate is None:
        raise utils.ASMValidationError("startdate and newdate cannot be blank")
    if newdate.weekday() != 0 or startdate.weekday() != 0:
        raise utils.ASMValidationError("startdate and newdate should both be a Monday")
    enddate = add_days(startdate, 7)
    rows = db.query(dbo, get_rota_query(dbo) + " WHERE StartDateTime >= %s AND StartDateTime <= %s" % (db.dd(startdate), db.dd(enddate)))
    for r in rows:
        # Were some flags set? If so, does the current person for this rota element have those flags?
        if flags is not None and flags != "":
            if not utils.list_overlap(flags.split("|"), utils.nulltostr(r["ADDITIONALFLAGS"]).split("|")):
                # The element doesn't have the right flags, skip to the next
                continue
        # Calculate how far from the start date this rec is so we can apply that
        # diff to the newdate
        sdiff = date_diff_days(startdate, r["STARTDATETIME"])
        ediff = date_diff_days(startdate, r["ENDDATETIME"])
        sd = add_days(newdate, sdiff)
        ed = add_days(newdate, ediff)
        sd = datetime.datetime(sd.year, sd.month, sd.day, r["STARTDATETIME"].hour, r["STARTDATETIME"].minute, 0)
        ed = datetime.datetime(ed.year, ed.month, ed.day, r["ENDDATETIME"].hour, r["ENDDATETIME"].minute, 0)
        insert_rota_from_form(dbo, username, utils.PostedData({
            "person":    str(r["OWNERID"]),
            "startdate": python2display(l, sd),
            "starttime": format_time(sd),
            "enddate":   python2display(l, ed),
            "endtime":   format_time(ed),
            "type":      str(r["ROTATYPEID"]),
            "worktype":  str(r["WORKTYPEID"]),
            "comments":  r["COMMENTS"]
        }, l))

def calculate_owner_code(pid, surname):
    """
    Calculates the owner code field in the format SU000000
    pid: The person ID
    surname: The person's surname
    """
    prefix = "XX"
    if len(surname) >= 2 and not surname.startswith("&"):
        prefix = surname[0:2].upper()
    return "%s%s" % (prefix, utils.padleft(pid, 6))

def calculate_owner_name(dbo, personclass= 0, title = "", initials = "", first = "", last = "", nameformat = ""):
    """
    Calculates the owner name field based on the current format.
    """
    if personclass == 2: return last # for organisations, just return the org name
    if nameformat == "": nameformat = configuration.owner_name_format(dbo)
    # If something went wrong and we have a broken format for any reason, substitute our default
    if nameformat is None or nameformat == "" or nameformat == "null": nameformat = "{ownertitle} {ownerforenames} {ownersurname}"
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
    own = db.query(dbo, "SELECT ID, OwnerType, OwnerTitle, OwnerInitials, OwnerForeNames, OwnerSurname FROM owner")
    nameformat = configuration.owner_name_format(dbo)
    async.set_progress_max(dbo, len(own))
    for o in own:
        db.execute(dbo, "UPDATE owner SET OwnerName = %s WHERE ID = %d" % \
            (db.ds(calculate_owner_name(dbo, o["OWNERTYPE"], o["OWNERTITLE"], o["OWNERINITIALS"], o["OWNERFORENAMES"], o["OWNERSURNAME"], nameformat)), o["ID"]))
        async.increment_progress_value(dbo)
    al.debug("regenerated %d owner names" % len(own), "person.update_owner_names", dbo)
    return "OK %d" % len(own)

def update_person_from_form(dbo, post, username):
    """
    Updates an existing person record from incoming form data
    """

    l = dbo.locale
    if not db.check_recordversion(dbo, "owner", post.integer("id"), post.integer("recordversion")):
        raise utils.ASMValidationError(_("This record has been changed by another user, please reload.", l))

    pid = post.integer("id")

    def bi(b): 
        return b and 1 or 0

    flags = post["flags"].split(",")
    homechecked = bi("homechecked" in flags)
    banned = bi("banned" in flags)
    coordinator = bi("coordinator" in flags)
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
        ( "OwnerCode", db.ds(calculate_owner_code(pid, post["surname"]))),
        ( "OwnerName", db.ds(calculate_owner_name(dbo, post.integer("ownertype"), post["title"], post["initials"], post["forenames"], post["surname"] ))),
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
        ( "SiteID", post.db_integer("site")),
        ( "IsBanned", db.di(banned)),
        ( "IsVolunteer", db.di(volunteer)),
        ( "IsMember", db.di(member)),
        ( "MembershipExpiryDate", post.db_date("membershipexpires")),
        ( "MembershipNumber", post.db_string("membershipnumber")),
        ( "IsAdoptionCoordinator", db.di(coordinator)),
        ( "IsHomeChecker", db.di(homechecker)),
        ( "IsDeceased", db.di(deceased)),
        ( "IsDonor", db.di(donor)),
        ( "IsDriver", db.di(driver)),
        ( "IsShelter", db.di(shelter)),
        ( "IsACO", db.di(aco)),
        ( "IsStaff", db.di(staff)),
        ( "IsFosterer", db.di(fosterer)),
        ( "FosterCapacity", post.db_integer("fostercapacity")),
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
    audit.edit(dbo, username, "owner", pid, audit.map_diff(preaudit, postaudit, [ "OWNERNAME", ]))

    # Save any additional field values given
    additional.save_values_for_link(dbo, post, pid, "person")

def update_flags(dbo, username, personid, flags):
    """
    Updates the flags on a person record from a list of flags
    """
    def bi(b): 
        return b and 1 or 0

    homechecked = bi("homechecked" in flags)
    banned = bi("banned" in flags)
    coordinator = bi("coordinator" in flags)
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
    sql = db.make_update_user_sql(dbo, "owner", username, "ID=%d" % personid, (
        ( "IDCheck", db.di(homechecked) ),
        ( "IsAdoptionCoordinator", db.di(coordinator)), 
        ( "IsBanned", db.di(banned)),
        ( "IsVolunteer", db.di(volunteer)),
        ( "IsMember", db.di(member)),
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
        ( "AdditionalFlags", db.ds(flagstr))
    ))
    db.execute(dbo, sql)

def insert_person_from_form(dbo, post, username):
    """
    Creates a new person record from incoming form data
    Returns the ID of the new record
    """
    def d(key, default = None): 
        if key in post.data:
            return post[key]
        else:
            return default

    def bi(b): 
        return b and 1 or 0

    flags = post["flags"].split(",")
    homechecked = bi("homechecked" in flags)
    banned = bi("banned" in flags)
    volunteer = bi("volunteer" in flags)
    member = bi("member" in flags)
    homechecker = bi("homechecker" in flags)
    coordinator = bi("coordinator" in flags)
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
        ( "OwnerCode", db.ds(calculate_owner_code(pid, post["surname"]))),
        ( "OwnerName", db.ds(calculate_owner_name(dbo, post.integer("ownertype"), post["title"], post["initials"], post["forenames"], post["surname"] ))),
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
        ( "SiteID", post.db_integer("site")),
        ( "IsAdoptionCoordinator", db.di(coordinator)),
        ( "IsBanned", db.di(banned)),
        ( "IsVolunteer", db.di(volunteer)),
        ( "IsMember", db.di(member)),
        ( "MembershipExpiryDate", post.db_date("membershipexpires")),
        ( "MembershipNumber", db.ds(d("membershipnumber"))),
        ( "IsHomeChecker", db.di(homechecker)),
        ( "IsDeceased", db.di(deceased)),
        ( "IsDonor", db.di(donor)),
        ( "IsDriver", db.di(driver)),
        ( "IsShelter", db.di(shelter)),
        ( "IsACO", db.di(aco)),
        ( "IsStaff", db.di(staff)),
        ( "IsFosterer", db.di(fosterer)),
        ( "FosterCapacity", db.di(d("fostercapacity"))),
        ( "IsRetailer", db.di(retailer)),
        ( "IsVet", db.di(vet)),
        ( "IsGiftAid", db.di(giftaid)),
        ( "AdditionalFlags", db.ds(flagstr)),
        ( "HomeCheckAreas", db.ds(d("homecheckareas", "") )),
        ( "DateLastHomeChecked", post.db_date("datelasthomechecked")),
        ( "HomeCheckedBy", db.di(d("homecheckedby", 0) )),
        ( "MatchAdded", post.db_date("matchadded")),
        ( "MatchExpires", post.db_date("matchexpires")),
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
    audit.create(dbo, username, "owner", pid, audit.dump_row(dbo, "owner", pid))

    # Save any additional field values given
    additional.save_values_for_link(dbo, post, pid, "person")

    return pid

def merge_person_details(dbo, username, personid, d):
    """
    Merges person details in data dictionary d (the same dictionary that
    would be fed to insert_person_from_form and update_person_from_form)
    to person with personid.
    If any of the contact fields on the person record are blank, the ones
    from the dictionary are used instead and updated on the record.
    """
    p = get_person(dbo, personid)
    if p is None: return
    def merge(dictfield, fieldname):
        if dictfield not in d: return
        if p[fieldname] is None or p[fieldname] == "":
            db.execute(dbo, "UPDATE owner SET %s = %s, LastChangedBy = %s, LastChangedDate = %s WHERE ID = %d" % \
                (fieldname, db.ds(d[dictfield]), db.ds(username), db.ddt(now(dbo.timezone)), personid))
    merge("address", "OWNERADDRESS")
    merge("town", "OWNERTOWN")
    merge("county", "OWNERCOUNTY")
    merge("postcode", "OWNERPOSTCODE")
    merge("hometelephone", "HOMETELEPHONE")
    merge("worktelephone", "WORKTELEPHONE")
    merge("mobiletelephone", "MOBILETELEPHONE")
    merge("emailaddress", "EMAILADDRESS")

def merge_flags(dbo, username, personid, flags):
    """
    Merges the delimited string flags with those on personid
    flags can be delimited with either pipes or commas.
    The original person record is updated and the new list of flags is returned 
    as a pipe delimited string.
    """
    fgs = []
    if flags is None or flags == "": return
    if flags.find("|"): fgs = flags.split("|")
    if flags.find(","): fgs = flags.split(",")
    epf = db.query_string(dbo, "SELECT AdditionalFlags FROM owner WHERE ID = %d" % personid)
    epfb = epf.split("|")
    for x in fgs:
        if x not in epfb and not x == "":
            epf += "%s|" % x
    update_flags(dbo, username, personid, epf.split("|"))
    return epf

def merge_person(dbo, username, personid, mergepersonid):
    """
    Reparents all satellite records of mergepersonid onto
    personid, merges any missing flags or details and then 
    deletes it.
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
    # Merge any contact info
    mp = get_person(dbo, mergepersonid)
    mp["address"] = mp["OWNERADDRESS"]
    mp["town"] = mp["OWNERTOWN"]
    mp["county"] = mp["OWNERCOUNTY"]
    mp["postcode"] = mp["OWNERPOSTCODE"]
    mp["hometelephone"] = mp["HOMETELEPHONE"]
    mp["worktelephone"] = mp["WORKTELEPHONE"]
    mp["mobiletelephone"] = mp["MOBILETELEPHONE"]
    mp["emailaddress"] = mp["EMAILADDRESS"]
    merge_person_details(dbo, username, personid, mp)
    # Merge any flags from the target
    merge_flags(dbo, username, personid, mp["ADDITIONALFLAGS"])
    # Reparent all satellite records
    reparent("adoption", "OwnerID")
    reparent("adoption", "RetailerID")
    reparent("animal", "OriginalOwnerID")
    reparent("animal", "BroughtInByOwnerID")
    reparent("animal", "AdoptionCoordinatorID")
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
    reparent("animalmedicaltreatment", "AdministeringVetID")
    reparent("animaltest", "AdministeringVetID")
    reparent("animalvaccination", "AdministeringVetID")
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
    audit.delete(dbo, username, "owner", mergepersonid, audit.dump_row(dbo, "owner", mergepersonid))
    db.execute(dbo, "DELETE FROM owner WHERE ID = %d" % mergepersonid)

def merge_duplicate_people(dbo, username):
    """
    Runs through every person in the database and attempts to find other people
    with the same first name, last name and address. If any are found, they are
    merged into this person via a call to merge_person
    """
    merged = 0
    removed = [] # track people we've already merged and removed so we can skip them
    people = db.query(dbo, "SELECT ID, OwnerForeNames, OwnerSurname, OwnerAddress FROM owner ORDER BY ID")
    al.info("Checking for duplicate people (%d records)" % len(people), "person.merge_duplicate_people", dbo)
    for i, p in enumerate(people):
        if p["ID"] in removed: continue
        dupsql = "SELECT ID FROM owner WHERE ID > %d AND OwnerForeNames = %s AND OwnerSurname = %s AND OwnerAddress = %s" % \
            (p["ID"], db.ds(p["OWNERFORENAMES"]), db.ds(p["OWNERSURNAME"]), db.ds(p["OWNERADDRESS"]))
        for mp in db.query(dbo, dupsql):
            merged += 1
            al.debug("found duplicate %s %s (%d of %d) id=%d, dupid=%d, merging" % \
                (p["OWNERFORENAMES"], p["OWNERSURNAME"], i, len(people), p["ID"], mp["ID"]), \
                "person.merge_duplicate_people", dbo)
            merge_person(dbo, username, p["ID"], mp["ID"])
            removed.append(mp["ID"])
    al.info("Merged %d duplicate people records" % merged, "person.merge_duplicate_people", dbo)

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
    if db.query_int(dbo, "SELECT COUNT(ID) FROM animal WHERE AdoptionCoordinatorID=%d OR BroughtInByOwnerID=%d OR OriginalOwnerID=%d OR CurrentVetID=%d OR OwnersVetID=%d" % (personid, personid, personid, personid, personid)):
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
    audit.delete_rows(dbo, username, "media", "LinkID = %d AND LinkTypeID = %d" % (personid, media.PERSON))
    db.execute(dbo, "DELETE FROM media WHERE LinkID = %d AND LinkTypeID = %d" % (personid, media.PERSON))
    audit.delete_rows(dbo, username, "diary", "LinkID = %d AND LinkType = %d" % (personid, diary.PERSON))
    db.execute(dbo, "DELETE FROM diary WHERE LinkID = %d AND LinkType = %d" % (personid, diary.PERSON))
    audit.delete_rows(dbo, username, "log", "LinkID = %d AND LinkType = %d" % (personid, log.PERSON))
    db.execute(dbo, "DELETE FROM log WHERE LinkID = %d AND LinkType = %d" % (personid, log.PERSON))
    db.execute(dbo, "DELETE FROM additional WHERE LinkID = %d AND LinkType IN (%s)" % (personid, additional.PERSON_IN))
    for t in [ "adoption", "ownercitation", "ownerdonation", "ownerlicence", "ownertraploan", "ownervoucher" ]:
        audit.delete_rows(dbo, username, t, "OwnerID = %d" % personid)
        db.execute(dbo, "DELETE FROM %s WHERE OwnerID = %d" % (t, personid))
    dbfs.delete_path(dbo, "/owner/%d" % personid)
    audit.delete(dbo, username, "owner", personid, audit.dump_row(dbo, "owner", personid))
    db.execute(dbo, "DELETE FROM owner WHERE ID = %d" % personid)
    # Now that we've removed the person, update any animals that were previously
    # attached to it so that they return to the shelter if necessary.
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
        ( "WorkTypeID", post.db_integer("worktype")),
        ( "Comments", post.db_string("comments"))
        ))
    db.execute(dbo, sql)
    audit.create(dbo, username, "ownerrota", nrota, audit.dump_row(dbo, "ownerrota", nrota))
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
        ( "WorkTypeID", post.db_integer("worktype")),
        ( "Comments", post.db_string("comments"))
        ))
    preaudit = db.query(dbo, "SELECT * FROM ownerrota WHERE ID = %d" % rotaid)
    db.execute(dbo, sql)
    postaudit = db.query(dbo, "SELECT * FROM ownerrota WHERE ID = %d" % rotaid)
    audit.edit(dbo, username, "ownerrota", rotaid, audit.map_diff(preaudit, postaudit))

def delete_rota(dbo, username, rid):
    """
    Deletes the selected rota record
    """
    audit.delete(dbo, username, "ownerrota", rid, audit.dump_row(dbo, "ownerrota", rid))
    db.execute(dbo, "DELETE FROM ownerrota WHERE ID = %d" % int(rid))

def delete_rota_week(dbo, username, startdate):
    """
    Deletes all rota records beginning at startdate and ending at
    startdate+7
    startdate: A python date representing the start of the week
    """
    enddate = add_days(startdate, 7)
    audit.delete(dbo, username, "ownerrota", 0,  \
        str(db.query(dbo, "SELECT * FROM ownerrota " \
        "WHERE StartDateTime >= %s AND StartDateTime <= %s" % (db.dd(startdate), db.dd(enddate)))))
    db.execute(dbo, "DELETE FROM ownerrota WHERE " \
        "StartDateTime >= %s AND StartDateTime <= %s" % (db.dd(startdate), db.dd(enddate)))

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
    audit.create(dbo, username, "ownerinvestigation", ninv, audit.dump_row(dbo, "ownerinvestigation", ninv))
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
    audit.edit(dbo, username, "ownerinvestigation", investigationid, audit.map_diff(preaudit, postaudit))

def delete_investigation(dbo, username, iid):
    """
    Deletes the selected investigation record
    """
    audit.delete(dbo, username, "ownerinvestigation", iid, audit.dump_row(dbo, "ownerinvestigation", iid))
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
    addtolog = post.boolean("addtolog")
    logtype = post.integer("logtype")
    body = post["body"]
    rv = utils.send_email(dbo, emailfrom, emailto, emailcc, subject, body, "html")
    if addtolog == 1:
        log.add_log(dbo, username, log.PERSON, post.integer("personid"), logtype, utils.html_email_to_plain(body))
    return rv

def lookingfor_report(dbo, username = "system", personid = 0, limit = 0):
    """
    Generates the person looking for report
    """
    l = dbo.locale
    title = _("People Looking For", l)
    h = []
    batch = []
    h.append(reports.get_report_header(dbo, title, username))
    if limit > 0:
        h.append("<p>(" + _("Limited to {0} matches", l).format(limit) + ")</p>")
    def td(s): 
        return "<td>%s</td>" % s
    def hr(): 
        return "<hr />"

    idclause = ""
    if personid != 0:
        idclause = " AND owner.ID=%d" % personid
  
    people = db.query(dbo, "SELECT owner.*, " \
        "(SELECT Size FROM lksize WHERE ID = owner.MatchSize) AS MatchSizeName, " \
        "(SELECT BaseColour FROM basecolour WHERE ID = owner.MatchColour) AS MatchColourName, " \
        "(SELECT Sex FROM lksex WHERE ID = owner.MatchSex) AS MatchSexName, " \
        "(SELECT BreedName FROM breed WHERE ID = owner.MatchBreed) AS MatchBreedName, " \
        "(SELECT AnimalType FROM animaltype WHERE ID = owner.MatchAnimalType) AS MatchAnimalTypeName, " \
        "(SELECT SpeciesName FROM species WHERE ID = owner.MatchSpecies) AS MatchSpeciesName " \
        "FROM owner WHERE MatchActive = 1 AND " \
        "(MatchExpires Is Null OR MatchExpires > %s)%s " \
        "ORDER BY OwnerName" % (db.dd(now(dbo.timezone)), idclause))

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
    async.set_progress_max(dbo, len(people))
    for p in people:
        async.increment_progress_value(dbo)
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
        summary = ""
        if len(c) > 0:
            summary = ", ".join(x for x in c if x is not None)
            h.append( "<p style='font-size: 8pt'>(%s: %s)</p>" % (_("Looking for", l), summary) )

        outputheader = False
        for a in animals:
            if not outputheader:
                outputheader = True
                h.append("".join(ah))
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

            # Add an entry to ownerlookingfor for other reports
            if personid == 0:
                batch.append( ( a["ID"], p["ID"], summary ) )

            totalmatches += 1
            if limit > 0 and totalmatches >= limit:
                break

        if outputheader:
            h.append( "</table>")
        h.append( hr())

        if limit > 0 and totalmatches >= limit:
            break

    if len(people) == 0:
        h.append( "<p>%s</p>" % _("No matches found.", l) )

    h.append( reports.get_report_footer(dbo, title, username))

    # Update ownerlookingfor table
    if personid == 0:
        db.execute(dbo, "DELETE FROM ownerlookingfor")
        if len(batch) > 0:
            db.execute_many(dbo, "INSERT INTO ownerlookingfor (AnimalID, OwnerID, MatchSummary) VALUES (%s, %s, %s)", batch)

    return "".join(h)

def lookingfor_last_match_count(dbo):
    """
    Returns the number of matches the last time lookingfor was run
    """
    return db.query_int(dbo, "SELECT COUNT(*) FROM ownerlookingfor")

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
    people = db.query(dbo, "SELECT ID, OwnerAddress, OwnerTown, OwnerCounty, OwnerPostcode " \
        "FROM owner WHERE LatLong Is Null OR LatLong = '' ORDER BY CreatedDate DESC", limit=BULK_GEO_LIMIT)
    batch = []
    for p in people:
        latlong = geo.get_lat_long(dbo, p["OWNERADDRESS"], p["OWNERTOWN"], p["OWNERCOUNTY"], p["OWNERPOSTCODE"])
        batch.append((latlong, p["ID"]))
    db.execute_many(dbo, "UPDATE owner SET LatLong = %s WHERE ID = %s", batch)
    al.debug("updated %d person geocodes" % len(batch), "person.update_missing_geocodes", dbo)

def update_lookingfor_report(dbo):
    """
    Updates the latest version of the looking for report 
    """
    al.debug("updating lookingfor report", "person.update_lookingfor_report", dbo)
    configuration.lookingfor_report(dbo, lookingfor_report(dbo, limit = 1000))
    configuration.lookingfor_last_match_count(dbo, lookingfor_last_match_count(dbo))
    return "OK %d" % lookingfor_last_match_count(dbo)


