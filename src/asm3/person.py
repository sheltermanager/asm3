
import asm3.additional
import asm3.al
import asm3.animal
import asm3.asynctask
import asm3.audit
import asm3.cachedisk
import asm3.configuration
import asm3.dbfs
import asm3.diary
import asm3.geo
import asm3.log
import asm3.media
import asm3.reports
import asm3.users
import asm3.utils
from asm3.i18n import _, add_days, date_diff_days, format_time, python2display, subtract_years, now
from asm3.sitedefs import GEO_BATCH, GEO_LIMIT

import datetime

ASCENDING = 0
DESCENDING = 1

def get_homechecked(dbo, personid):
    """
    Returns a list of people homechecked by personid
    """
    return dbo.query("SELECT ID, OwnerName, DateLastHomeChecked, Comments FROM owner " \
        "WHERE HomeCheckedBy = ?", [personid])

def get_person_query(dbo):
    """
    Returns the SELECT and JOIN commands necessary for selecting
    person rows with resolved lookups.
    """
    return "SELECT o.*, o.ID AS PersonID, " \
        "ho.OwnerName AS HomeCheckedByName, ho.HomeTelephone AS HomeCheckedByHomeTelephone, " \
        "ho.MobileTelephone AS HomeCheckedByMobileTelephone, ho.EmailAddress AS HomeCheckedByEmail, " \
        "lfa.ID AS LatestFosterID, lfa.AnimalName AS LatestFosterName, lfa.ShelterCode AS LatestFosterShelterCode, " \
        "lma.ID AS LatestMoveAnimalID, lma.AnimalName AS LatestMoveAnimalName, lma.ShelterCode AS LatestMoveShelterCode, " \
        "lmat.MovementType AS LatestMoveTypeName, " \
        "j.JurisdictionName, si.SiteName, " \
        "web.ID AS WebsiteMediaID, " \
        "web.MediaName AS WebsiteMediaName, " \
        "web.Date AS WebsiteMediaDate, " \
        "web.MediaNotes AS WebsiteMediaNotes, " \
        "doc.ID AS DocMediaID, " \
        "doc.MediaName AS DocMediaName, " \
        "doc.Date AS DocMediaDate, " \
        "(SELECT MatchSummary FROM ownerlookingfor olf WHERE olf.OwnerID = o.ID GROUP BY MatchSummary) AS LookingForSummary " \
        "FROM owner o " \
        "LEFT OUTER JOIN owner ho ON ho.ID = o.HomeCheckedBy " \
        "LEFT OUTER JOIN adoption lf ON lf.ID = " \
            "(SELECT MAX(ID) FROM adoption slf WHERE slf.OwnerID = o.ID AND slf.MovementType = 2 AND (slf.ReturnDate Is Null OR slf.ReturnDate > %s )) " \
        "LEFT OUTER JOIN animal lfa ON lfa.ID = lf.AnimalID " \
        "LEFT OUTER JOIN adoption lm ON lm.ID = " \
            "(SELECT MAX(ID) FROM adoption slm WHERE slm.OwnerID = o.ID AND MovementType > 0 AND (slm.ReturnDate Is Null OR slm.ReturnDate > %s )) " \
        "LEFT OUTER JOIN animal lma ON lma.ID = lm.AnimalID " \
        "LEFT OUTER JOIN lksmovementtype lmat ON lmat.ID = lm.MovementType " \
        "LEFT OUTER JOIN media web ON web.LinkID = o.ID AND web.LinkTypeID = 3 AND web.WebsitePhoto = 1 " \
        "LEFT OUTER JOIN media doc ON doc.LinkID = o.ID AND doc.LinkTypeID = 3 AND doc.DocPhoto = 1 " \
        "LEFT OUTER JOIN site si ON o.SiteID = si.ID " \
        "LEFT OUTER JOIN jurisdiction j ON j.ID = o.JurisdictionID " % ( dbo.sql_today(), dbo.sql_today() )

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
    p = dbo.first_row( dbo.query(get_person_query(dbo) + "WHERE o.ID = %d" % personid) )
    p = embellish_latest_movement(dbo, p)
    return p

def get_person_embedded(dbo, personid):
    """ Returns a person record for the person chooser widget, uses a read-through cache for performance """
    return dbo.first_row( dbo.query_cache(get_person_query(dbo) + " WHERE o.ID = ?", [personid], age=120) )

def embellish_adoption_warnings(dbo, p):
    """ Adds the adoption warning columns to a person record p and returns it """
    warn = dbo.first_row(dbo.query("SELECT (SELECT COUNT(*) FROM ownerinvestigation oi WHERE oi.OwnerID = o.ID) AS Investigation, " \
        "(SELECT COUNT(*) FROM animalcontrol ac WHERE ac.OwnerID = o.ID OR ac.Owner2ID = o.ID OR ac.Owner3ID = o.ID) AS Incident, " \
        "(SELECT COUNT(*) FROM animal bib WHERE NonShelterAnimal = 0 AND IsTransfer = 0 AND IsPickup = 0 AND bib.OriginalOwnerID = o.ID) AS Surrender, " \
        "(SELECT COUNT(*) FROM owner bo WHERE bo.OwnerAddress <> '' AND bo.OwnerAddress LIKE o.OwnerAddress AND bo.IsBanned=1) AS BannedAddress " \
        "FROM owner o " \
        "WHERE o.ID = ?", [p.ID]))
    if warn is not None:
        p.INVESTIGATION = warn.INVESTIGATION
        p.SURRENDER = warn.SURRENDER
        p.INCIDENT = warn.INCIDENT
        p.BANNEDADDRESS = warn.BANNEDADDRESS
    return p

def embellish_latest_movement(dbo, p):
    """ Adds the latest movement info to a person record p and returns it.
        The query already does this and 99% of the time it will work fine and makes these columns available
        in v_person for the query builder. BUT if we have a data import where the movements were created out of
        order, MAX(ID) will fail and return the wrong movement. """
    if p is None: return p
    lm = dbo.first_row(dbo.query("SELECT m.ID AS LatestMoveAnimalID, a.ID AS LatestMoveAnimalID, a.AnimalName AS LatestMoveAnimalName, " \
        "a.ShelterCode AS LatestMoveShelterCode, mt.MovementType AS LatestMoveTypeName " \
        "FROM adoption m "
        "INNER JOIN animal a ON m.AnimalID = a.ID " \
        "INNER JOIN lksmovementtype mt ON mt.ID = m.MovementType " \
        "WHERE m.MovementType > 0 AND m.OwnerID = ? AND (ReturnDate Is Null OR ReturnDate > ?)" \
        "ORDER BY m.MovementDate DESC", [p.ID, dbo.today()]))
    if lm is not None:
        p.LATESTMOVEANIMALID = lm.LATESTMOVEANIMALID
        p.LATESTMOVEANIMALNAME = lm.LATESTMOVEANIMALNAME
        p.LATESTMOVESHELTERCODE = lm.LATESTMOVESHELTERCODE
        p.LATESTMOVETYPENAME = lm.LATESTMOVETYPENAME
    return p

def get_person_similar(dbo, email = "", mobile = "", surname = "", forenames = "", address = "", siteid = 0):
    """
    Returns people with similar email, mobile, names and addresses to those supplied.
    If siteid is non-zero, only people with that site will be checked
    """
    # Consider the first word rather than first address line - typically house
    # number/name and unlikely to be the same for different people
    siteclause = ""
    if siteid != 0: siteclause = "o.SiteID=%s AND " % siteid
    if address.find(" ") != -1: address = address[0:address.find(" ")]
    if address.find("\n") != -1: address = address[0:address.find("\n")]
    if address.find(",") != -1: address = address[0:address.find(",")]
    address = address.replace("'", "`").lower().strip()
    forenames = forenames.replace("'", "`").lower().strip()
    if forenames.find(" ") != -1: forenames = forenames[0:forenames.find(" ")]
    surname = surname.replace("'", "`").lower().strip()
    email = email.replace("'", "`").lower().strip()
    eq = []
    hq = []
    mq = []
    per = []
    if email != "" and email.find("@") != -1 and email.find(".") != -1 and len(email) > 6:
        eq = dbo.query(get_person_query(dbo) + " WHERE %s LOWER(o.EmailAddress) LIKE ?" % siteclause, [email])
    if mobile != "" and asm3.utils.atoi(mobile)> 9999: # at least 5 digits to constitute a valid number
        mq = dbo.query(get_person_query(dbo) + " WHERE %s %s LIKE ?" % (siteclause, dbo.sql_atoi("o.MobileTelephone")) , [asm3.utils.digits_only(mobile)])
        hq = dbo.query(get_person_query(dbo) + " WHERE %s %s LIKE ?" % (siteclause, dbo.sql_atoi("o.HomeTelephone")) , [asm3.utils.digits_only(mobile)])
    if address != "":
        per = dbo.query(get_person_query(dbo) + " WHERE %s LOWER(o.OwnerSurname) LIKE ? AND " \
         "LOWER(o.OwnerForeNames) LIKE ? AND LOWER(o.OwnerAddress) LIKE ?" % siteclause, (surname, forenames + "%", address + "%"))
    return eq + mq + hq + per

def get_person_name(dbo, personid):
    """
    Returns the full person name for an id
    """
    return dbo.query_string("SELECT OwnerName FROM owner WHERE ID = ?", [ asm3.utils.cint(personid) ])

def get_person_name_code(dbo, personid):
    """
    Returns the person name and code for an id
    """
    r = dbo.first_row(dbo.query("SELECT o.OwnerName, o.OwnerCode FROM owner o WHERE o.ID = ?", [personid]))
    if r is None: return ""
    return "%s - %s" % (r.OWNERNAME, r.OWNERCODE)

def get_person_name_addresses(dbo):
    """
    Returns the person name and address for everyone on file
    """
    return dbo.query("SELECT o.ID, o.OwnerName, o.OwnerAddress FROM owner o ORDER BY o.OwnerName")

def get_fosterers(dbo):
    """
    Returns all fosterers
    """
    return dbo.query(get_person_query(dbo) + " WHERE o.IsFosterer = 1 ORDER BY o.OwnerName")

def get_shelterview_fosterers(dbo, siteid = 0):
    """
    Returns all fosterers with the just the minimum info required for shelterview
    """
    sitefilter = ""
    if siteid is not None and siteid != 0: sitefilter = "AND o.SiteID = %s" % siteid
    return dbo.query("SELECT o.ID, o.OwnerName, o.FosterCapacity, o.AdditionalFlags FROM owner o WHERE o.IsFosterer = 1 %s ORDER BY o.OwnerName" % sitefilter)

def get_staff_volunteers(dbo, siteid = 0):
    """
    Returns all staff and volunteers
    """
    sitefilter = ""
    if siteid is not None and siteid != 0: sitefilter = "AND o.SiteID = %s" % siteid
    return dbo.query(get_person_query(dbo) + " WHERE o.IsStaff = 1 OR o.IsVolunteer = 1 %s ORDER BY o.IsStaff DESC, o.OwnerSurname, o.OwnerForeNames" % sitefilter)

def get_towns(dbo):
    """
    Returns a list of all towns
    """
    rows = dbo.query("SELECT DISTINCT OwnerTown FROM owner ORDER BY OwnerTown")
    if rows is None: return []
    towns = []
    for r in rows:
        towns.append(str(r.OWNERTOWN))
    return towns

def get_town_to_county(dbo):
    """
    Returns a lookup of which county towns belong in
    """
    rows = dbo.query("SELECT DISTINCT OwnerTown, OwnerCounty FROM owner ORDER BY OwnerCounty")
    if rows is None: return []
    tc = {}
    for r in rows:
        tc[r.OWNERTOWN] = r.OWNERCOUNTY
    return tc

def get_counties(dbo):
    """
    Returns a list of counties
    """
    rows = dbo.query("SELECT DISTINCT OwnerCounty FROM owner")
    if rows is None: return []
    counties = []
    for r in rows:
        counties.append("%s" % r.OWNERCOUNTY)
    return counties

def get_satellite_counts(dbo, personid):
    """
    Returns a resultset containing the number of each type of satellite
    record that a person has.
    """
    return dbo.query("SELECT o.ID, " \
        "(SELECT COUNT(*) FROM media me WHERE me.LinkID = o.ID AND me.LinkTypeID = ?) AS media, " \
        "(SELECT COUNT(*) FROM diary di WHERE di.LinkID = o.ID AND di.LinkType = ?) AS diary, " \
        "(SELECT COUNT(*) FROM adoption ad WHERE ad.OwnerID = o.ID) AS movements, " \
        "(SELECT COUNT(*) FROM clinicappointment ca WHERE ca.OwnerID = o.ID) AS clinic, " \
        "(SELECT COUNT(*) FROM log WHERE log.LinkID = o.ID AND log.LinkType = ?) AS logs, " \
        "(SELECT COUNT(*) FROM ownerdonation od WHERE od.OwnerID = o.ID) AS donations, " \
        "(SELECT COUNT(*) FROM ownercitation oc WHERE oc.OwnerID = o.ID) AS citation, " \
        "(SELECT COUNT(*) FROM ownerinvestigation oi WHERE oi.OwnerID = o.ID) AS investigation, " \
        "(SELECT COUNT(*) FROM ownerlicence ol WHERE ol.OwnerID = o.ID) AS licence, " \
        "(SELECT COUNT(*) FROM ownerrota r WHERE r.OwnerID = o.ID) AS rota, " \
        "(SELECT COUNT(*) FROM ownertraploan ot WHERE ot.OwnerID = o.ID) AS traploan, " \
        "(SELECT COUNT(*) FROM ownervoucher ov WHERE ov.OwnerID = o.ID) AS vouchers, " \
        "((SELECT COUNT(*) FROM animal WHERE AdoptionCoordinatorID = o.ID OR BroughtInByOwnerID = o.ID OR OriginalOwnerID = o.ID OR CurrentVetID = o.ID OR OwnersVetID = o.ID OR NeuteredByVetID = o.ID) + " \
        "(SELECT COUNT(*) FROM animal INNER JOIN adoption ON adoption.ID = animal.ActiveMovementID WHERE animal.OwnerID = o.ID AND animal.OwnerID <> adoption.OwnerID) + " \
        "(SELECT COUNT(*) FROM adoption WHERE ReturnedByOwnerID = o.ID) + " \
        "(SELECT COUNT(*) FROM animalwaitinglist WHERE OwnerID = o.ID) + " \
        "(SELECT COUNT(*) FROM animalfound WHERE OwnerID = o.ID) + " \
        "(SELECT COUNT(*) FROM animallost WHERE OwnerID = o.ID) + " \
        "(SELECT COUNT(*) FROM animaltransport WHERE DriverOwnerID = o.ID) + " \
        "(SELECT COUNT(*) FROM animalcontrol WHERE CallerID = o.ID OR VictimID = o.ID " \
        "OR OwnerID = o.ID OR Owner2ID = o.ID or Owner3ID = o.ID) + " \
        "(SELECT COUNT(*) FROM additional af INNER JOIN additionalfield aff ON aff.ID = af.AdditionalFieldID " \
        "WHERE aff.FieldType = ? AND af.Value = ?) " \
        ") AS links " \
        "FROM owner o WHERE o.ID = ?", (asm3.media.PERSON, asm3.diary.PERSON, asm3.log.PERSON, asm3.additional.PERSON_LOOKUP, str(personid), personid))

def get_reserves_without_homechecks(dbo):
    """
    Returns owners that have a reservation but aren't homechecked
    """
    return dbo.query(get_person_query(dbo) + " INNER JOIN adoption a ON a.OwnerID = o.ID " \
        "WHERE a.MovementType = 0 AND a.ReservationDate Is Not Null AND a.ReservationCancelledDate Is Null AND o.IDCheck = 0")

def get_open_adoption_checkout(dbo, cutoff=7):
    """
    Returns owners with adoption checkout initiated, but not complete in the last cutoff days
    """
    cutoffdate = dbo.today(cutoff * -1)
    rows = dbo.query("SELECT l.LinkID AS ID FROM log l " \
        "WHERE l.LinkType=1 AND l.Date >= ? AND l.Comments LIKE 'AC01%%' " \
        "AND (SELECT COUNT(*) FROM log WHERE LinkID=l.LinkID AND LinkType=1 AND Date >= ? AND Comments LIKE 'AC01%%') " \
        " > (SELECT COUNT(*) FROM log WHERE LinkID=l.LinkID AND LinkType=1 AND Date >= ? AND Comments LIKE 'AC03%%') ", \
        [cutoffdate, cutoffdate, cutoffdate], distincton="ID")
    return dbo.query(get_person_query(dbo) + "WHERE o.ID IN (%s)" % dbo.sql_in(rows))

def get_overdue_donations(dbo):
    """
    Returns owners that have an overdue regular donation
    """
    return dbo.query(get_person_query(dbo) + " INNER JOIN ownerdonation od ON od.OwnerID = o.ID " \
        "WHERE od.Date Is Null AND od.DateDue Is Not Null AND od.DateDue <= ?", [dbo.today()])

def get_signed_requests(dbo, cutoff=7):
    """
    Returns owners that have a fulfilled a signing request in the last cutoff days
    """
    cutoffdate = dbo.today(cutoff * -1)
    rows = dbo.query("SELECT l.LinkID AS ID FROM log l " \
        "WHERE l.LinkType=1 AND l.Date >= ? AND l.Comments LIKE 'ES02%%'", [cutoffdate], distincton="ID")
    return dbo.query(get_person_query(dbo) + "WHERE o.ID IN (%s)" % dbo.sql_in(rows))

def get_unsigned_requests(dbo, cutoff=31):
    """
    Returns owners that have more signing requests in the last cutoff days than signed
    """
    cutoffdate = dbo.today(cutoff * -1)
    rows = dbo.query("SELECT l.LinkID AS ID FROM log l " \
        "WHERE l.LinkType=1 AND l.Date >= ? AND l.Comments LIKE 'ES01%%' " \
        "AND (SELECT COUNT(*) FROM log WHERE LinkID=l.LinkID AND LinkType=1 AND Date >= ? AND Comments LIKE 'ES01%%') " \
        " > (SELECT COUNT(*) FROM log WHERE LinkID=l.LinkID AND LinkType=1 AND Date >= ? AND Comments LIKE 'ES02%%') ", \
        [cutoffdate, cutoffdate, cutoffdate], distincton="ID")
    return dbo.query(get_person_query(dbo) + "WHERE o.ID IN (%s)" % dbo.sql_in(rows))

def get_links(dbo, pid):
    """
    Gets a list of all records that link to this person
    """
    linkdisplay = dbo.sql_concat(("a.ShelterCode", "' - '", "a.AnimalName"))
    animalextra = dbo.sql_concat(("a.BreedName", "' '", "s.SpeciesName", "' ('", 
        "CASE WHEN a.Archived = 0 AND a.ActiveMovementType = 2 THEN mt.MovementType " \
        "WHEN a.NonShelterAnimal = 1 THEN '' " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Not Null AND a.ActiveMovementID = 0 THEN dr.ReasonName " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Null AND a.ActiveMovementID <> 0 THEN mt.MovementType " \
        "ELSE il.LocationName END", "')'"))
    # Current Owner (shown for non-shelter matches or where owner <> current movement person)
    sql = "SELECT 'CO' AS TYPE, " \
        "'' AS TYPEDISPLAY, a.LastChangedDate AS DDATE, a.ID AS LINKID, " \
        "%s AS LINKDISPLAY, " \
        "%s AS FIELD2, " \
        "CASE WHEN a.DeceasedDate Is Not Null THEN 'D' ELSE '' END AS DMOD " \
        "FROM animal a " \
        "LEFT OUTER JOIN adoption ad ON ad.ID = a.ActiveMovementID " \
        "LEFT OUTER JOIN lksmovementtype mt ON mt.ID = a.ActiveMovementType " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "WHERE (a.OwnerID = %d AND (a.NonShelterAnimal=1 OR a.OwnerID <> ad.OwnerID)) " \
        "OR (a.OriginalOwnerID = %d AND a.NonShelterAnimal=1)" % (linkdisplay, animalextra, int(pid), int(pid))
    # Original Owner (shelter animals only)
    sql += "UNION SELECT 'OO' AS TYPE, " \
        "'' AS TYPEDISPLAY, a.DateBroughtIn AS DDATE, a.ID AS LINKID, " \
        "%s AS LINKDISPLAY, " \
        "%s AS FIELD2, " \
        "CASE WHEN a.DeceasedDate Is Not Null THEN 'D' ELSE '' END AS DMOD " \
        "FROM animal a " \
        "LEFT OUTER JOIN lksmovementtype mt ON mt.ID = a.ActiveMovementType " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "WHERE NonShelterAnimal = 0 AND OriginalOwnerID = %d " % (linkdisplay, animalextra, int(pid))
    # Brought In By
    sql += "UNION SELECT 'BI' AS TYPE, " \
        "'' AS TYPEDISPLAY, a.DateBroughtIn AS DDATE, a.ID AS LINKID, " \
        "%s AS LINKDISPLAY, " \
        "%s AS FIELD2, " \
        "CASE WHEN a.DeceasedDate Is Not Null THEN 'D' ELSE '' END AS DMOD " \
        "FROM animal a " \
        "LEFT OUTER JOIN lksmovementtype mt ON mt.ID = a.ActiveMovementType " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "WHERE BroughtInByOwnerID = %d " % (linkdisplay, animalextra, int(pid))
    # Returned By
    sql += "UNION SELECT 'RO' AS TYPE, " \
        "'' AS TYPEDISPLAY, m.ReturnDate AS DDATE, a.ID AS LINKID, " \
        "%s AS LINKDISPLAY, " \
        "%s AS FIELD2, " \
        "CASE WHEN a.DeceasedDate Is Not Null THEN 'D' ELSE '' END AS DMOD " \
        "FROM adoption m " \
        "INNER JOIN animal a ON m.AnimalID = a.ID " \
        "LEFT OUTER JOIN lksmovementtype mt ON mt.ID = m.MovementType " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "WHERE m.ReturnedByOwnerID = %d " % (linkdisplay, animalextra, int(pid))
    # Adoption Coordinator
    sql += "UNION SELECT 'AO' AS TYPE, " \
        "'' AS TYPEDISPLAY, a.DateBroughtIn AS DDATE, a.ID AS LINKID, " \
        "%s AS LINKDISPLAY, " \
        "%s AS FIELD2, " \
        "CASE WHEN a.DeceasedDate Is Not Null THEN 'D' ELSE '' END AS DMOD " \
        "FROM animal a " \
        "LEFT OUTER JOIN lksmovementtype mt ON mt.ID = a.ActiveMovementType " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "WHERE AdoptionCoordinatorID = %d " % (linkdisplay, animalextra, int(pid))
    # Owner Vet
    sql += "UNION SELECT 'OV' AS TYPE, " \
        "'' AS TYPEDISPLAY, a.DateBroughtIn AS DDATE, a.ID AS LINKID, " \
        "%s AS LINKDISPLAY, " \
        "%s AS FIELD2, " \
        "CASE WHEN a.DeceasedDate Is Not Null THEN 'D' ELSE '' END AS DMOD " \
        "FROM animal a " \
        "LEFT OUTER JOIN lksmovementtype mt ON mt.ID = a.ActiveMovementType " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "WHERE OwnersVetID = %d " % (linkdisplay, animalextra, int(pid))
    # Current Vet
    sql += "UNION SELECT 'CV' AS TYPE, " \
        "'' AS TYPEDISPLAY, a.DateBroughtIn AS DDATE, a.ID AS LINKID, " \
        "%s AS LINKDISPLAY, " \
        "%s AS FIELD2, " \
        "CASE WHEN a.DeceasedDate Is Not Null THEN 'D' ELSE '' END AS DMOD " \
        "FROM animal a " \
        "LEFT OUTER JOIN lksmovementtype mt ON mt.ID = a.ActiveMovementType " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "WHERE CurrentVetID = %d " % (linkdisplay, animalextra, int(pid))
    # Altering Vet
    sql += "UNION SELECT 'AV' AS TYPE, " \
        "'' AS TYPEDISPLAY, a.DateBroughtIn AS DDATE, a.ID AS LINKID, " \
        "%s AS LINKDISPLAY, " \
        "%s AS FIELD2, " \
        "CASE WHEN a.DeceasedDate Is Not Null THEN 'D' ELSE '' END AS DMOD " \
        "FROM animal a " \
        "LEFT OUTER JOIN lksmovementtype mt ON mt.ID = a.ActiveMovementType " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "WHERE NeuteredByVetID = %d " % (linkdisplay, animalextra, int(pid))
    # Waiting List
    sql += "UNION SELECT 'WL' AS TYPE, " \
        "'' AS TYPEDISPLAY, a.DatePutOnList AS DDATE, a.ID AS LINKID, " \
        "s.SpeciesName AS LINKDISPLAY, " \
        "a.AnimalDescription AS FIELD2, '' AS DMOD FROM animalwaitinglist a " \
        "INNER JOIN species s ON s.ID = a.SpeciesID WHERE a.OwnerID = %d " % (int(pid))
    # Lost Animal
    sql += "UNION SELECT 'LA' AS TYPE, " \
        "'' AS TYPEDISPLAY, a.DateLost AS DDATE, a.ID AS LINKID, " \
        "s.SpeciesName AS LINKDISPLAY, " \
        "a.DistFeat AS FIELD2, '' AS DMOD FROM animallost a " \
        "INNER JOIN species s ON s.ID = a.AnimalTypeID WHERE a.OwnerID = %d " % (int(pid))
    # Found Animal
    sql += "UNION SELECT 'FA' AS TYPE, " \
        "'' AS TYPEDISPLAY, a.DateFound AS DDATE, a.ID AS LINKID, " \
        "s.SpeciesName AS LINKDISPLAY, " \
        "a.DistFeat AS FIELD2, '' AS DMOD FROM animalfound a " \
        "INNER JOIN species s ON s.ID = a.AnimalTypeID WHERE a.OwnerID = %d " % (int(pid))
    # Incident Suspect
    sql += "UNION SELECT 'ACS' AS TYPE, " \
        "'' AS TYPEDISPLAY, a.IncidentDateTime AS DDATE, a.ID AS LINKID, " \
        "ti.IncidentName AS LINKDISPLAY, " \
        "a.CallNotes AS FIELD2, '' AS DMOD FROM animalcontrol a " \
        "INNER JOIN incidenttype ti ON ti.ID = a.IncidentTypeID WHERE a.OwnerID = %d OR a.Owner2ID = %d OR a.Owner3ID = %d " % \
            (int(pid), int(pid), int(pid))
    # Incident Caller
    sql += "UNION SELECT 'ACC' AS TYPE, " \
        "'' AS TYPEDISPLAY, a.IncidentDateTime AS DDATE, a.ID AS LINKID, " \
        "ti.IncidentName AS LINKDISPLAY, " \
        "a.CallNotes AS FIELD2, '' AS DMOD FROM animalcontrol a " \
        "INNER JOIN incidenttype ti ON ti.ID = a.IncidentTypeID WHERE a.CallerID = %d " % \
        (int(pid))
    # Incident Victim
    sql += "UNION SELECT 'ACV' AS TYPE, " \
        "'' AS TYPEDISPLAY, a.IncidentDateTime AS DDATE, a.ID AS LINKID, " \
        "ti.IncidentName AS LINKDISPLAY, " \
        "a.CallNotes AS FIELD2, '' AS DMOD FROM animalcontrol a " \
        "INNER JOIN incidenttype ti ON ti.ID = a.IncidentTypeID WHERE a.VictimID = %d " % \
        (int(pid))
    # Transport Driver
    sql += "UNION SELECT 'ATD' AS TYPE, " \
        "'' AS TYPEDISPLAY, t.PickupDateTime AS DDATE, t.AnimalID AS LINKID, " \
        "%s LINKDISPLAY, " \
        "t.DropOffAddress AS FIELD2, '' AS DMOD FROM animaltransport t " \
        "INNER JOIN animal a ON a.ID = t.AnimalID " \
        "WHERE t.DriverOwnerID = %d " % (linkdisplay, int(pid))
    # Transport Pickup
    sql += "UNION SELECT 'ATP' AS TYPE, " \
        "'' AS TYPEDISPLAY, t.PickupDateTime AS DDATE, t.AnimalID AS LINKID, " \
        "%s LINKDISPLAY, " \
        "t.PickupAddress AS FIELD2, '' AS DMOD FROM animaltransport t " \
        "INNER JOIN animal a ON a.ID = t.AnimalID " \
        "WHERE t.PickupOwnerID = %d " % (linkdisplay, int(pid))
    # Transport Dropoff
    sql += "UNION SELECT 'ATR' AS TYPE, " \
        "'' AS TYPEDISPLAY, t.DropoffDateTime AS DDATE, t.AnimalID AS LINKID, " \
        "%s LINKDISPLAY, " \
        "t.DropoffAddress AS FIELD2, '' AS DMOD FROM animaltransport t " \
        "INNER JOIN animal a ON a.ID = t.AnimalID " \
        "WHERE t.DropoffOwnerID = %d " % (linkdisplay, int(pid))
    # Additional field (link from animal)
    sql += "UNION SELECT 'AFA' AS TYPE, " \
        "aff.FieldLabel AS TYPEDISPLAY, a.LastChangedDate AS DDATE, a.ID AS LINKID, " \
        "%s AS LINKDISPLAY, " \
        "%s AS FIELD2, " \
        "CASE WHEN a.DeceasedDate Is Not Null THEN 'D' ELSE '' END AS DMOD " \
        "FROM additional af " \
        "INNER JOIN additionalfield aff ON aff.ID = af.AdditionalFieldID " \
        "INNER JOIN animal a ON a.ID = af.LinkID " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN lksmovementtype mt ON mt.ID = a.ActiveMovementType " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "WHERE af.Value = '%d' AND aff.FieldType = %s AND aff.LinkType IN (%s) " % \
            ( linkdisplay, animalextra, int(pid), asm3.additional.PERSON_LOOKUP, asm3.additional.clause_for_linktype("animal") ) 
    # Additional field (link from person)
    sql += "UNION SELECT 'AFP' AS TYPE, " \
        "aff.FieldLabel AS TYPEDISPLAY, o.LastChangedDate AS DDATE, o.ID AS LINKID, " \
        "o.OwnerName AS LINKDISPLAY, " \
        "o.OwnerAddress AS FIELD2, " \
        "CASE WHEN o.IsDeceased=1 THEN 'D' ELSE '' END AS DMOD " \
        "FROM additional af " \
        "INNER JOIN additionalfield aff ON aff.ID = af.AdditionalFieldID " \
        "INNER JOIN owner o ON o.ID = af.LinkID " \
        "WHERE af.Value = '%d' AND aff.FieldType = %s AND aff.LinkType IN (%s) " % ( int(pid), asm3.additional.PERSON_LOOKUP, asm3.additional.clause_for_linktype("person") ) 
    # Additional field (link from incident)
    sql += "UNION SELECT 'AFI' AS TYPE, " \
        "aff.FieldLabel AS TYPEDISPLAY, ac.LastChangedDate AS DDATE, ac.ID AS LINKID, " \
        "t.IncidentName AS LINKDISPLAY, " \
        "ac.DispatchAddress AS FIELD2, " \
        "'' AS DMOD " \
        "FROM additional af " \
        "INNER JOIN additionalfield aff ON aff.ID = af.AdditionalFieldID " \
        "INNER JOIN animalcontrol ac ON ac.ID = af.LinkID " \
        "INNER JOIN incidenttype t ON ac.IncidentTypeID = t.ID " \
        "WHERE af.Value = '%d' AND aff.FieldType = %s AND aff.LinkType IN (%s) " % ( int(pid), asm3.additional.PERSON_LOOKUP, asm3.additional.clause_for_linktype("incident") ) 
    # Sort and done
    sql += "ORDER BY DDATE DESC, LINKDISPLAY "
    return dbo.query(sql)

def get_investigation(dbo, personid, sort = ASCENDING):
    """
    Returns investigation records for the given person:
    OWNERID, DATE, NOTES
    """
    sql = "SELECT o.* FROM ownerinvestigation o WHERE o.OwnerID = ? "
    if sort == ASCENDING:
        sql += "ORDER BY o.Date"
    else:
        sql += "ORDER BY o.Date DESC"
    return dbo.query(sql, [personid])

def get_person_find_simple(dbo, query, username="", classfilter="all", includeStaff = False, includeVolunteers = False, limit = 0, siteid = 0):
    """
    Returns rows for simple person searches.
    query: The search criteria
    classfilter: One of all, vet, retailer, staff, fosterer, volunteer, shelter, 
                 aco, banned, homechecked, homechecker, member, donor, driver, volunteerandstaff
    """
    ss = asm3.utils.SimpleSearchBuilder(dbo, query)
    ss.add_words("o.OwnerName")
    ss.add_fields([ "o.OwnerCode", "o.OwnerAddress", "o.OwnerTown", "o.OwnerCounty", "o.OwnerPostcode",
        "o.EmailAddress", "o.HomeTelephone", "o.WorkTelephone", "o.MobileTelephone", "o.MembershipNumber" ])
    ss.add_clause("EXISTS(SELECT ad.Value FROM additional ad " \
        "INNER JOIN additionalfield af ON af.ID = ad.AdditionalFieldID AND af.Searchable = 1 " \
        "WHERE ad.LinkID=o.ID AND ad.LinkType IN (%s) AND LOWER(ad.Value) LIKE ?)" % asm3.additional.PERSON_IN)
    classfilters = {
        "all":              "",
        "coordinator":      " AND o.IsAdoptionCoordinator = 1",
        "vet":              " AND o.IsVet = 1",
        "retailer":         " AND o.IsRetailer = 1",
        "staff":            " AND o.IsStaff = 1",
        "fosterer":         " AND o.IsFosterer = 1",
        "volunteer":        " AND o.IsVolunteer = 1",
        "volunteerandstaff": " AND (o.IsVolunteer = 1 OR o.IsStaff = 1)",
        "shelter":          " AND o.IsShelter = 1",
        "aco":              " AND o.IsACO = 1",
        "banned":           " AND o.IsBanned = 1",
        "dangerous":        " AND o.IsDangerous = 1",
        "homechecked":      " AND o.IDCheck = 1",
        "homechecker":      " AND o.IsHomeChecker = 1",
        "member":           " AND o.IsMember = 1",
        "donor":            " AND o.IsDonor = 1",
        "driver":           " AND o.IsDriver = 1",
        "sponsor":          " AND o.IsSponsor = 1"
    }
    cf = classfilters[classfilter]
    if not includeStaff: cf += " AND o.IsStaff = 0"
    if not includeVolunteers: cf += " AND o.IsVolunteer = 0"
    if siteid != 0: cf += " AND (o.SiteID = 0 OR o.SiteID = %d)" % siteid
    sql = get_person_query(dbo) + " WHERE (" + " OR ".join(ss.ors) + ")" + cf + " ORDER BY o.OwnerName"
    return dbo.query(sql, ss.values, limit=limit, distincton="ID")

def get_person_find_advanced(dbo, criteria, username, includeStaff = False, includeVolunteers = False, limit = 0, siteid = 0):
    """
    Returns rows for advanced person searches.
    criteria: A dictionary of criteria
       code - string partial pattern
       createdby - string partial pattern
       createdsince - date
       name - string partial pattern
       address - string partial pattern
       town - string partial pattern
       county - string partial pattern
       postcode - string partial pattern
       phone - string partial pattern
       jurisdiction - -1 for all or jurisdiction
       homecheck - string partial pattern
       comments - string partial pattern
       email - string partial pattern
       medianotes - string partial pattern
       filter - built in or additional flags, ANDed
       gdpr - one or more gdpr contact values ANDed
    """
    post = asm3.utils.PostedData(criteria, dbo.locale)
    ss = asm3.utils.AdvancedSearchBuilder(dbo, post)
    ss.add_words("name", "o.OwnerName")
    ss.add_str("code", "o.OwnerCode")
    ss.add_str("createdby", "o.CreatedBy")
    ss.add_date_since("createdsince", "o.CreatedDate")
    ss.add_str("address", "o.OwnerAddress")
    ss.add_str("town", "o.OwnerTown")
    ss.add_str("county", "o.OwnerCounty")
    ss.add_str("postcode", "o.OwnerPostcode")
    ss.add_phone_triplet("phone", "o.HomeTelephone", "o.WorkTelephone", "o.MobileTelephone")
    ss.add_id("jurisdiction", "o.JurisdictionID")
    ss.add_str("email", "o.EmailAddress")
    ss.add_words("homecheck", "o.HomeCheckAreas")
    ss.add_words("comments", "o.Comments")
    ss.add_words("medianotes", "web.MediaNotes")

    if "filter" in post and post["filter"].strip() != "":
        for flag in post["filter"].split(","):
            if flag == "aco": ss.ands.append("o.IsACO=1")
            elif flag == "adopter": ss.ands.append("o.IsAdopter=1")
            elif flag == "banned": ss.ands.append("o.IsBanned=1")
            elif flag == "dangerous": ss.ands.append("o.IsDangerous=1")
            elif flag == "coordinator": ss.ands.append("o.IsAdoptionCoordinator=1")
            elif flag == "deceased": ss.ands.append("o.IsDeceased=1")
            elif flag == "donor": ss.ands.append("o.IsDonor=1")
            elif flag == "driver": ss.ands.append("o.IsDriver=1")
            elif flag == "excludefrombulkemail": ss.ands.append("o.ExcludeFromBulkEmail=1")
            elif flag == "fosterer": ss.ands.append("o.IsFosterer=1")
            elif flag == "homechecked": ss.ands.append("o.IDCheck=1")
            elif flag == "homechecker": ss.ands.append("o.IsHomeChecker=1")
            elif flag == "member": ss.ands.append("o.IsMember=1")
            elif flag == "retailer": ss.ands.append("o.IsRetailer=1")
            elif flag == "shelter": ss.ands.append("o.IsShelter=1")
            elif flag == "sponsor": ss.ands.append("o.IsSponsor=1")
            elif flag == "staff": ss.ands.append("o.IsStaff=1")
            elif flag == "giftaid": ss.ands.append("o.IsGiftAid=1")
            elif flag == "vet": ss.ands.append("o.IsVet=1")
            elif flag == "volunteer": ss.ands.append("o.IsVolunteer=1")
            elif flag == "padopter": ss.ands.append("EXISTS(SELECT OwnerID FROM adoption WHERE OwnerID = o.ID AND MovementType=1)")
            else: 
                ss.ands.append("LOWER(o.AdditionalFlags) LIKE ?")
                ss.values.append("%%%s|%%" % flag.lower())

    if "gdpr" in post and post["gdpr"].strip() != "":
        for g in post["gdpr"].split(","):
            ss.ands.append("o.GDPRContactOptIn LIKE ?")
            ss.values.append("%%%s%%" % g)

    if not includeStaff:
        ss.ands.append("o.IsStaff = 0")

    if not includeVolunteers:
        ss.ands.append("o.IsVolunteer = 0")

    if siteid != 0:
        ss.ands.append("(o.SiteID = 0 OR o.SiteID = ?)")
        ss.values.append(siteid)

    if len(ss.ands) == 0:
        sql = get_person_query(dbo) + " ORDER BY o.OwnerName"
    else:
        sql = get_person_query(dbo) + " WHERE " + " AND ".join(ss.ands) + " ORDER BY o.OwnerName"
    return dbo.query(sql, ss.values, limit=limit, distincton="ID")

def get_person_rota(dbo, personid):
    return dbo.query(get_rota_query(dbo) + " WHERE r.OwnerID = ? ORDER BY r.StartDateTime DESC", [personid])

def get_rota(dbo, startdate, enddate):
    """ Returns rota records that apply between the two dates given """
    return dbo.query(get_rota_query(dbo) + \
        " WHERE (r.StartDateTime >= ? AND r.StartDateTime < ?)" \
        " OR (r.EndDateTime >= ? AND r.EndDateTime < ?)" \
        " OR (r.StartDateTime < ? AND r.EndDateTime >= ?) " \
        " ORDER BY r.StartDateTime", (startdate, enddate, startdate, enddate, startdate, startdate))

def clone_rota_week(dbo, username, startdate, newdate, flags):
    """ Copies a weeks worth of rota records from startdate to newdate """
    l = dbo.locale
    if startdate is None or newdate is None:
        raise asm3.utils.ASMValidationError("startdate and newdate cannot be blank")
    if newdate.weekday() != 0 or startdate.weekday() != 0:
        raise asm3.utils.ASMValidationError("startdate and newdate should both be a Monday")
    enddate = add_days(startdate, 7)
    rows = dbo.query(get_rota_query(dbo) + " WHERE StartDateTime >= ? AND StartDateTime <= ?", (startdate, enddate))
    for r in rows:
        # Were some flags set? If so, does the current person for this rota element have those flags?
        if flags is not None and flags != "":
            if not asm3.utils.list_overlap(flags.split("|"), asm3.utils.nulltostr(r.ADDITIONALFLAGS).split("|")):
                # The element doesn't have the right flags, skip to the next
                continue
        # Calculate how far from the start date this rec is so we can apply that
        # diff to the newdate
        sdiff = date_diff_days(startdate, r.STARTDATETIME)
        ediff = date_diff_days(startdate, r.ENDDATETIME)
        sd = add_days(newdate, sdiff)
        ed = add_days(newdate, ediff)
        sd = datetime.datetime(sd.year, sd.month, sd.day, r.STARTDATETIME.hour, r.STARTDATETIME.minute, 0)
        ed = datetime.datetime(ed.year, ed.month, ed.day, r.ENDDATETIME.hour, r.ENDDATETIME.minute, 0)
        insert_rota_from_form(dbo, username, asm3.utils.PostedData({
            "person":    str(r.OWNERID),
            "startdate": python2display(l, sd),
            "starttime": format_time(sd),
            "enddate":   python2display(l, ed),
            "endtime":   format_time(ed),
            "type":      str(r.ROTATYPEID),
            "worktype":  str(r.WORKTYPEID),
            "comments":  r.COMMENTS
        }, l))

def get_extra_id(dbo, p, idtype):
    """
    Retrieves a value from the ExtraIDs field, which is stored
    in the form:  key1=value1|key2=value2 ...
    p: A person result from get_person_query containing ExtraIDs
    idtype: A string key
    Returns the extra ID (string) or None if there was no match
    """
    if "EXTRAIDS" in p and p.EXTRAIDS is not None:
        for x in p.EXTRAIDS.split("|"):
            if x.find("=") != -1:
                k, v = x.split("=")
                if k == idtype:
                    return v
    return None

def set_extra_id(dbo, user, p, idtype, idvalue):
    """
    Stores a value in the ExtraIDs field for a person, which is stored
    in the form:  key1=value1|key2=value2 ...
    p: A person result from get_person_query containing ExtraIDs and ID
    idtype: A string key
    idvalue: The value of the key (will be coerced to string).
    """
    ids = []
    ids.append( "%s=%s" % (idtype, idvalue) ) 
    extraids = p.EXTRAIDS 
    if extraids is None: extraids = ""
    for x in extraids.split("|"):
        if x.find("=") != -1:
            k, v = x.split("=")
            if k != idtype: ids.append( "%s=%s" % (k, v))
    extraids = "|".join(ids)
    p.EXTRAIDS = extraids
    dbo.update("owner", p.ID, { "ExtraIDs": extraids }, user)
    return extraids

def calculate_owner_code(pid, surname):
    """
    Calculates the owner code field in the format SU000000
    pid: The person ID
    surname: The person's surname
    """
    prefix = "XX"
    REMOVE = set(" !\"'.,$()")
    surname = "".join(x for x in surname if x not in REMOVE)
    if len(surname) >= 2 and not surname.startswith("&"):
        prefix = surname[0:2].upper()
    return "%s%s" % (prefix, asm3.utils.padleft(pid, 6))

def calculate_owner_name(dbo, personclass= 0, title = "", initials = "", first = "", last = "", nameformat = ""):
    """
    Calculates the owner name field based on the current format.
    """
    if personclass == 2: return last # for organisations, just return the org name
    if nameformat == "": nameformat = asm3.configuration.owner_name_format(dbo)
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
    Regenerates all owner code and name fields based on the current values.
    """
    asm3.al.debug("regenerating owner names and codes...", "person.update_owner_names", dbo)
    own = dbo.query("SELECT ID, OwnerCode, OwnerType, OwnerTitle, OwnerInitials, OwnerForeNames, OwnerSurname FROM owner")
    nameformat = asm3.configuration.owner_name_format(dbo)
    asm3.asynctask.set_progress_max(dbo, len(own))
    for o in own:
        if o.ownercode is None or o.ownercode == "":
            dbo.update("owner", o.id, { 
                "OwnerCode": calculate_owner_code(o.id, o.ownersurname),
                "OwnerName": calculate_owner_name(dbo, o.ownertype, o.ownertitle, o.ownerinitials, o.ownerforenames, o.ownersurname, nameformat)
            }, setRecordVersion=False, setLastChanged=False, writeAudit=False)
        else:
            dbo.update("owner", o.id, { 
                "OwnerName": calculate_owner_name(dbo, o.ownertype, o.ownertitle, o.ownerinitials, o.ownerforenames, o.ownersurname, nameformat)
            }, setRecordVersion=False, setLastChanged=False, writeAudit=False)
        asm3.asynctask.increment_progress_value(dbo)
    asm3.al.debug("regenerated %d owner names and codes" % len(own), "person.update_owner_names", dbo)
    return "OK %d" % len(own)

def insert_person_from_form(dbo, post, username, geocode=True):
    """
    Creates a new person record from incoming form data
    Returns the ID of the new record
    """
    l = dbo.locale
    if post["surname"].strip() == "":
        raise asm3.utils.ASMValidationError(_("Person must have a surname.", l))

    pid = dbo.get_id("owner")
    dbo.insert("owner", {
        "ID":               pid,
        "OwnerType":        post.integer("ownertype"),
        "OwnerCode":        calculate_owner_code(pid, post["surname"]),
        "OwnerName":        calculate_owner_name(dbo, post.integer("ownertype"), post["title"], post["initials"], post["forenames"], post["surname"] ),
        "OwnerTitle":       post["title"],
        "OwnerInitials":    post["initials"],
        "OwnerForenames":   post["forenames"],
        "OwnerSurname":     post["surname"],
        "OwnerAddress":     post["address"],
        "OwnerTown":        post["town"],
        "OwnerCounty":      post["county"],
        "OwnerPostcode":    post["postcode"],
        "OwnerCountry":     post["country"],
        "LatLong":          post["latlong"],
        "HomeTelephone":    post["hometelephone"],
        "WorkTelephone":    post["worktelephone"],
        "MobileTelephone":  post["mobiletelephone"],
        "EmailAddress":     post["emailaddress"],
        "GDPRContactOptIn": post["gdprcontactoptin"],
        "JurisdictionID":   post.integer("jurisdiction"),
        "Comments":         post["comments"],
        "PopupWarning":     post["popupwarning"],
        "SiteID":           post.integer("site"),
        "MembershipExpiryDate": post.date("membershipexpires"),
        "MembershipNumber": post["membershipnumber"],
        "FosterCapacity":   post.integer("fostercapacity"),
        "HomeCheckAreas":   post["areas"],
        "DateLastHomeChecked": post.date("homechecked"),
        "HomeCheckedBy":    post.integer("homecheckedby"),
        "MatchActive":      post.integer("matchactive"),
        "MatchAdded":       post.date("matchadded"),
        "MatchExpires":     post.date("matchexpires"),
        "MatchSex":         post.integer("matchsex", -1),
        "MatchSize":        post.integer("matchsize", -1),
        "MatchColour":      post.integer("matchcolour", -1),
        "MatchAgeFrom":     post.floating("agedfrom"),
        "MatchAgeTo":       post.floating("agedto"),
        "MatchAnimalType":  post.integer("matchtype", -1),
        "MatchSpecies":     post.integer("matchspecies", -1),
        "MatchBreed":       post.integer("matchbreed1", -1),
        "MatchBreed2":      post.integer("matchbreed2", -1),
        "MatchGoodWithCats": post.integer("matchgoodwithcats", -1),
        "MatchGoodWithDogs": post.integer("matchgoodwithdogs", -1),
        "MatchGoodWithChildren": post.integer("matchgoodwithchildren", -1),
        "MatchHouseTrained": post.integer("matchhousetrained", -1),
        "MatchCommentsContain": post["commentscontain"],
        # Flags are updated afterwards, but cannot be null
        "IDCheck":                  0,
        "ExcludeFromBulkEmail":     0,
        "IsAdopter":                0,
        "IsAdoptionCoordinator":    0,
        "IsBanned":                 0,
        "IsDangerous":              0,
        "IsVolunteer":              0,
        "IsMember":                 0,
        "IsHomeChecker":            0,
        "IsDeceased":               0,
        "IsDonor":                  0,
        "IsDriver":                 0,
        "IsShelter":                0,
        "IsACO":                    0,
        "IsStaff":                  0,
        "IsFosterer":               0,
        "IsRetailer":               0,
        "IsVet":                    0,
        "IsGiftAid":                0,
        "IsSponsor":                0,
        "AdditionalFlags":          ""
    }, username, generateID=False)

    # If we're using GDPR contact options and email is not set, set the exclude from bulk email flag
    if asm3.configuration.show_gdpr_contact_optin(dbo):
        if post["gdprcontactoptin"].find("email") == -1:
            post["flags"] += ",excludefrombulkemail"

    # Update the flags
    update_flags(dbo, username, pid, post["flags"].split(","))

    # Save any asm3.additional.field values given
    asm3.additional.save_values_for_link(dbo, post, username, pid, "person", True)

    # If the option is on, record any GDPR contact options in the log
    if asm3.configuration.show_gdpr_contact_optin(dbo) and asm3.configuration.gdpr_contact_change_log(dbo) and post["gdprcontactoptin"] != "":
        newvalue = post["gdprcontactoptin"]
        asm3.log.add_log(dbo, username, asm3.log.PERSON, pid, asm3.configuration.gdpr_contact_change_log_type(dbo),
            "%s" % (newvalue))

    # Look up a geocode for the person's address
    if geocode: update_geocode(dbo, pid, "", post["address"], post["town"], post["county"], post["postcode"], post["country"])

    return pid

def update_person_from_form(dbo, post, username, geocode=True):
    """
    Updates an existing person record from incoming form data
    """

    l = dbo.locale
    if not dbo.optimistic_check("owner", post.integer("id"), post.integer("recordversion")):
        raise asm3.utils.ASMValidationError(_("This record has been changed by another user, please reload.", l))

    if post["surname"].strip() == "":
        raise asm3.utils.ASMValidationError(_("Person must have a surname.", l))

    pid = post.integer("id")

    # If the option is on and the gdpr contact info has changed, log it
    if asm3.configuration.show_gdpr_contact_optin(dbo) and asm3.configuration.gdpr_contact_change_log(dbo):
        oldvalue = dbo.query_string("SELECT GDPRContactOptIn FROM owner WHERE ID=?", [pid])
        if post["gdprcontactoptin"] != oldvalue:
            newvalue = post["gdprcontactoptin"]
            asm3.log.add_log(dbo, username, asm3.log.PERSON, pid, asm3.configuration.gdpr_contact_change_log_type(dbo),
                "%s" % (newvalue))

    # If we're using GDPR contact options and email is not set, set the exclude from bulk email flag
    if asm3.configuration.show_gdpr_contact_optin(dbo):
        if post["gdprcontactoptin"].find("email") == -1 and post["flags"].find("excludefrombulkemail") == -1:
            post["flags"] += ",excludefrombulkemail"

    dbo.update("owner", pid, {
        "OwnerType":        post.integer("ownertype"),
        "OwnerCode":        calculate_owner_code(pid, post["surname"]),
        "OwnerName":        calculate_owner_name(dbo, post.integer("ownertype"), post["title"], post["initials"], post["forenames"], post["surname"] ),
        "OwnerTitle":       post["title"],
        "OwnerInitials":    post["initials"],
        "OwnerForenames":   post["forenames"],
        "OwnerSurname":     post["surname"],
        "OwnerAddress":     post["address"],
        "OwnerTown":        post["town"],
        "OwnerCounty":      post["county"],
        "OwnerPostcode":    post["postcode"],
        "OwnerCountry":     post["country"],
        "LatLong":          post["latlong"],
        "HomeTelephone":    post["hometelephone"],
        "WorkTelephone":    post["worktelephone"],
        "MobileTelephone":  post["mobiletelephone"],
        "EmailAddress":     post["emailaddress"],
        "GDPRContactOptIn": post["gdprcontactoptin"],
        "JurisdictionID":   post.integer("jurisdiction"),
        "Comments":         post["comments"],
        "PopupWarning":     post["popupwarning"],
        "SiteID":           post.integer("site"),
        "MembershipExpiryDate": post.date("membershipexpires"),
        "MembershipNumber": post["membershipnumber"],
        "FosterCapacity":   post.integer("fostercapacity"),
        "HomeCheckAreas":   post["areas"],
        "DateLastHomeChecked": post.date("homechecked"),
        "HomeCheckedBy":    post.integer("homecheckedby"),
        "MatchActive":      post.integer("matchactive"),
        "MatchAdded":       post.date("matchadded"),
        "MatchExpires":     post.date("matchexpires"),
        "MatchSex":         post.integer("matchsex"),
        "MatchSize":        post.integer("matchsize"),
        "MatchColour":      post.integer("matchcolour"),
        "MatchAgeFrom":     post.floating("agedfrom"),
        "MatchAgeTo":       post.floating("agedto"),
        "MatchAnimalType":  post.integer("matchtype"),
        "MatchSpecies":     post.integer("matchspecies"),
        "MatchBreed":       post.integer("matchbreed1"),
        "MatchBreed2":      post.integer("matchbreed2"),
        "MatchGoodWithCats": post.integer("matchgoodwithcats"),
        "MatchGoodWithDogs": post.integer("matchgoodwithdogs"),
        "MatchGoodWithChildren": post.integer("matchgoodwithchildren"),
        "MatchHouseTrained": post.integer("matchhousetrained"),
        "MatchCommentsContain": post["commentscontain"]
    }, username)

    # Update the flags
    update_flags(dbo, username, pid, post["flags"].split(","))

    # Save any asm3.additional.field values given
    asm3.additional.save_values_for_link(dbo, post, username, pid, "person")

    # Update diary link info
    asm3.diary.update_link_info(dbo, username, asm3.diary.PERSON, pid)

    # Check/update the geocode for the person's address
    if geocode: update_geocode(dbo, pid, post["latlong"], post["address"], post["town"], post["county"], post["postcode"], post["country"])

def update_remove_flag(dbo, username, personid, flag):
    """
    Removes flag from personid. Does nothing if the person does not have the flag.
    """
    flags = dbo.query_string("SELECT AdditionalFlags FROM owner WHERE ID = ?", [personid])
    if flags.find("%s|" % flag) != -1:
        update_flags(dbo, username, personid, flags.replace("%s|" % flag, "").split("|"))

def update_flags(dbo, username, personid, flags):
    """
    Updates the flags on a person record from a list of flags
    """
    def bi(b): 
        return b and 1 or 0

    l = dbo.locale

    homechecked = bi("homechecked" in flags)
    banned = bi("banned" in flags)
    dangerous = bi("dangerous" in flags)
    adopter = bi("adopter" in flags)
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
    excludefrombulkemail = bi("excludefrombulkemail" in flags)
    sponsor = bi("sponsor" in flags)
    flagstr = "|".join(sorted(flags)) + "|"

    # If the option is on and the flags have changed, log it
    if asm3.configuration.flag_change_log(dbo):
        oldflags = dbo.query_string("SELECT AdditionalFlags FROM owner WHERE ID=?", [personid])
        if oldflags != flagstr:
            asm3.log.add_log(dbo, username, asm3.log.PERSON, personid, asm3.configuration.flag_change_log_type(dbo),
                _("Flags changed from '{0}' to '{1}'", l).format(oldflags, flagstr))

    dbo.update("owner", personid, {
        "IDCheck":                  homechecked,
        "ExcludeFromBulkEmail":     excludefrombulkemail,
        "IsAdopter":                adopter,
        "IsAdoptionCoordinator":    coordinator,
        "IsBanned":                 banned,
        "IsDangerous":              dangerous,
        "IsVolunteer":              volunteer,
        "IsMember":                 member,
        "IsHomeChecker":            homechecker,
        "IsDeceased":               deceased,
        "IsDonor":                  donor,
        "IsDriver":                 driver,
        "IsShelter":                shelter,
        "IsACO":                    aco,
        "IsStaff":                  staff,
        "IsFosterer":               fosterer,
        "IsRetailer":               retailer,
        "IsVet":                    vet,
        "IsSponsor":                sponsor,
        "IsGiftAid":                giftaid,
        "AdditionalFlags":          flagstr
    }, username)

def update_adopter_flag(dbo, username, personid):
    """
    Sets or removes the adopter flag on personid if it has any open adoption movements.
    Only makes the change if necessary to avoid audits/lastchange updates.
    """
    if personid is None or personid == 0: return
    openadoptions = dbo.query_int("SELECT COUNT(*) FROM adoption WHERE MovementType=1 AND " \
        "MovementDate Is Not Null AND ReturnDate Is Null AND OwnerID=?", [personid])
    hasadopter = dbo.query_int("SELECT IsAdopter FROM owner WHERE ID=?", [personid]) == 1
    if openadoptions > 0 and not hasadopter:
        merge_flags(dbo, username, personid, "adopter")
    elif openadoptions == 0 and hasadopter:
        update_remove_flag(dbo, username, personid, "adopter")

def merge_person_details(dbo, username, personid, d, force=False):
    """
    Merges person details in data dictionary d (the same dictionary that
    would be fed to insert_person_from_form and update_person_from_form)
    to person with personid.
    If any of the contact fields on the person record are blank and available
    in the dictionary, the ones from the dictionary are used instead and updated on the record.
    personid: The person we're merging details into
    d: The dictionary of values to merge
    force: If True, forces overwrite of the details with values from d if they are present
    """
    p = get_person(dbo, personid)
    if p is None: return
    def merge(dictfield, fieldname):
        if dictfield not in d or d[dictfield] == "": return
        if p[fieldname] is None or p[fieldname] == "" or force:
            dbo.update("owner", personid, { fieldname: d[dictfield] }, username)
    merge("address", "OWNERADDRESS")
    merge("town", "OWNERTOWN")
    merge("county", "OWNERCOUNTY")
    merge("postcode", "OWNERPOSTCODE")
    merge("country", "OWNERCOUNTRY")
    merge("hometelephone", "HOMETELEPHONE")
    merge("worktelephone", "WORKTELEPHONE")
    merge("mobiletelephone", "MOBILETELEPHONE")
    merge("emailaddress", "EMAILADDRESS")
    merge("comments", "COMMENTS")

def merge_gdpr_flags(dbo, username, personid, flags):
    """
    Merges the delimited string flags with those on personid.gdprcontactoptin
    The original person record is updated and the new list of GDPR flags is returned 
    as a pipe delimited string.
    """
    if flags is None or flags == "": return ""
    fgs = flags.split(",")
    p = dbo.first_row(dbo.query("SELECT ExcludeFromBulkEmail, GDPRContactOptIn FROM owner WHERE ID = ?", [personid]))
    if p is None: return flags # Can't do anything without a person
    fgs += asm3.utils.nulltostr(p.GDPRCONTACTOPTIN).split(",") # Merge the existing GDPR flags into one list
    v = { "GDPRContactOptIn": ",".join(fgs) }
    # If email is part of the flags, but ExcludeFromBulkEmail has been set, clear it
    if "email" in fgs and p.EXCLUDEFROMBULKEMAIL == 1: v["ExcludeFromBulkEmail"] = 0
    dbo.update("owner", personid, v, username)
    return ",".join(fgs)

def merge_flags(dbo, username, personid, flags):
    """
    Merges the delimited string flags with those on personid
    flags can be delimited with either pipes or commas.
    The original person record is updated and the new list of flags is returned 
    as a pipe delimited string.
    """
    fgs = []
    if flags is None or flags == "": 
        return ""
    elif flags.find("|") != -1: 
        fgs = flags.split("|")
    elif flags.find(",") != -1: 
        fgs = flags.split(",")
    else:
        fgs.append(flags)
    epf = dbo.query_string("SELECT AdditionalFlags FROM owner WHERE ID = ?", [personid]).split("|")
    merged = set([x for x in epf+fgs if x != ""]) # Add together our existing+new, remove dups and blanks
    update_flags(dbo, username, personid, merged)
    return "|".join(merged) + "|"

def merge_person(dbo, username, personid, mergepersonid):
    """
    Reparents all satellite records of mergepersonid onto
    personid, merges any missing flags or details and then 
    deletes it.
    """
    l = dbo.locale

    if personid == mergepersonid:
        raise asm3.utils.ASMValidationError(_("The person record to merge must be different from the original.", l))

    if personid == 0 or mergepersonid == 0:
        raise asm3.utils.ASMValidationError("Internal error: Cannot merge ID 0")

    def reparent(table, field, linktypefield = "", linktype = -1, haslastchanged = True):
        try:
            if linktype >= 0:
                dbo.update(table, "%s=%s AND %s=%s" % (field, mergepersonid, linktypefield, linktype), 
                    { field: personid }, username, 
                    setLastChanged=False, setRecordVersion=haslastchanged)
            else:
                dbo.update(table, "%s=%s" % (field, mergepersonid), 
                    { field: personid }, username, setLastChanged=False, setRecordVersion=haslastchanged)
        except Exception as err:
            asm3.al.error("error reparenting: %s -> %s, table=%s, field=%s, linktypefield=%s, linktype=%s, error=%s" % \
                (mergepersonid, personid, table, field, linktypefield, linktype, err), "person.merge_person", dbo)


    # Merge any contact info
    mp = get_person(dbo, mergepersonid)
    mp["address"] = mp.OWNERADDRESS
    mp["town"] = mp.OWNERTOWN
    mp["county"] = mp.OWNERCOUNTY
    mp["postcode"] = mp.OWNERPOSTCODE
    mp["country"] = mp.OWNERCOUNTRY
    mp["hometelephone"] = mp.HOMETELEPHONE
    mp["worktelephone"] = mp.WORKTELEPHONE
    mp["mobiletelephone"] = mp.MOBILETELEPHONE
    mp["emailaddress"] = mp.EMAILADDRESS
    merge_person_details(dbo, username, personid, mp)

    # Merge any flags from the target
    merge_flags(dbo, username, personid, mp.ADDITIONALFLAGS)

    # Merge any GDPR flags from the target
    merge_gdpr_flags(dbo, username, personid, mp.GDPRCONTACTOPTIN)

    # Reparent all satellite records
    reparent("adoption", "OwnerID")
    reparent("adoption", "RetailerID")
    reparent("adoption", "ReturnedByOwnerID")
    reparent("animal", "OriginalOwnerID")
    reparent("animal", "OwnerID")
    reparent("animal", "BroughtInByOwnerID")
    reparent("animal", "AdoptionCoordinatorID")
    reparent("animal", "OwnersVetID")
    reparent("animal", "CurrentVetID")
    reparent("animal", "NeuteredByVetID")
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
    reparent("clinicappointment", "OwnerID")
    reparent("ownercitation", "OwnerID")
    reparent("ownerdonation", "OwnerID")
    reparent("ownerinvestigation", "OwnerID")
    reparent("ownerlicence", "OwnerID")
    reparent("ownerlookingfor", "OwnerID", haslastchanged=False)
    reparent("ownertraploan", "OwnerID")
    reparent("ownervoucher", "OwnerID")
    reparent("users", "OwnerID")
    reparent("additional", "LinkID", asm3.additional.PERSON_IN, haslastchanged=False)
    reparent("media", "LinkID", "LinkTypeID", asm3.media.PERSON, haslastchanged=False)
    reparent("diary", "LinkID", "LinkType", asm3.diary.PERSON)
    reparent("log", "LinkID", "LinkType", asm3.log.PERSON, haslastchanged=False)
              
    # Change any additional field links pointing to the merge person
    asm3.additional.update_merge_person(dbo, mergepersonid, personid)

    # Assign the adopter flag if we brought in new open adoption movements
    update_adopter_flag(dbo, username, personid)

    # Reparent the audit records for the reparented records in the audit log
    # by switching ParentLinks to the new ID.
    dbo.execute("UPDATE audittrail SET ParentLinks = %s WHERE ParentLinks LIKE '%%owner=%s %%'" % \
        ( dbo.sql_replace("ParentLinks", "owner=%s " % mergepersonid, "owner=%s " % personid), mergepersonid))

    dbo.delete("owner", mergepersonid, username)
    asm3.audit.move(dbo, username, "owner", personid, "", "Merged owner %d -> %d" % (mergepersonid, personid))

def merge_duplicate_people(dbo, username):
    """
    Runs through every person in the database and attempts to find other people
    with the same first name, last name and address. If any are found, they are
    merged into this person via a call to merge_person
    """
    merged = 0
    removed = [] # track people we've already merged and removed so we can skip them
    people = dbo.query("SELECT ID, OwnerForeNames, OwnerSurname, OwnerAddress FROM owner ORDER BY ID")

    asm3.al.info("Checking for duplicate people (%d records)" % len(people), "person.merge_duplicate_people", dbo)

    for i, p in enumerate(people):

        if p.ID in removed: continue

        rows = dbo.query("SELECT ID FROM owner WHERE ID > ? AND OwnerForeNames = ? AND OwnerSurname = ? AND OwnerAddress = ?",
            (p.ID, p.OWNERFORENAMES, p.OWNERSURNAME, p.OWNERADDRESS))

        for mp in rows:

            merged += 1

            asm3.al.debug("found duplicate %s %s (%d of %d) id=%d, dupid=%d, merging" % \
                (p.OWNERFORENAMES, p.OWNERSURNAME, i, len(people), p.ID, mp.ID), \
                "person.merge_duplicate_people", dbo)

            merge_person(dbo, username, p.ID, mp.ID)
            removed.append(mp.ID)

    asm3.al.info("Merged %d duplicate people records" % merged, "person.merge_duplicate_people", dbo)

def update_pass_homecheck(dbo, user, personid, comments):
    """
    Marks a person as homechecked and appends any comments supplied to their record.
    """
    by = asm3.users.get_personid(dbo, user)

    if by != 0: 
        dbo.update("owner", personid, { "HomeCheckedBy": by }, user)

    dbo.update("owner", personid, { "IDCheck": 1, "DateLastHomeChecked": dbo.today() }, user)

    if comments != "":
        com = dbo.query_string("SELECT Comments FROM owner WHERE ID = ?", [personid])
        com += "\n" + comments
        dbo.update("owner", personid, { "Comments": "%s\n%s" % (com, comments) }, user)

def update_geocode(dbo, personid, latlon="", address="", town="", county="", postcode="", country=""):
    """
    Looks up the geocode for this person with the address info given.
    If latlon is already set to a value, checks the address hash to see if it
    matches and does not do the geocode if it does.
    """
    # If an address hasn't been specified, look it up from the personid given
    if address == "":
        row = dbo.first_row(dbo.query("SELECT OwnerAddress, OwnerTown, OwnerCounty, OwnerPostcode, OwnerCountry FROM owner WHERE ID=?", [personid]))
        address = row.OWNERADDRESS
        town = row.OWNERTOWN
        county = row.OWNERCOUNTY
        postcode = row.OWNERPOSTCODE
        country = row.OWNERCOUNTRY
    # If we're allowing manual entry of latlon values and we have a non-empty
    # value, do nothing so that changes to address don't overwrite it
    # If someone has deleted the values, a latlon of ,,HASH is returned so
    # we allow the geocode to be regenerated in that case.
    if asm3.configuration.show_lat_long(dbo) and latlon is not None and latlon != "" and not latlon.startswith(",,"):
        return latlon
    # If a latlon has been passed and it contains a hash of the address elements,
    # then the address hasn't changed since the last geocode was done - do nothing
    if latlon is not None and latlon != "":
        if latlon.find(asm3.geo.address_hash(address, town, county, postcode, country)) != -1:
            return latlon
    # Do the geocode
    latlon = asm3.geo.get_lat_long(dbo, address, town, county, postcode, country)
    update_latlong(dbo, personid, latlon)
    return latlon

def update_latlong(dbo, personid, latlong):
    """
    Updates the latlong field.
    """
    dbo.update("owner", personid, { "LatLong": latlong })

def delete_person(dbo, username, personid):
    """
    Deletes a person and all its satellite records.
    """
    l = dbo.locale
    if dbo.query_int("SELECT COUNT(ID) FROM adoption WHERE OwnerID=? OR RetailerID=? OR ReturnedByOwnerID=?", (personid, personid, personid)):
        raise asm3.utils.ASMValidationError(_("This person has movements and cannot be removed.", l))
    if dbo.query_int("SELECT COUNT(ID) FROM animal WHERE AdoptionCoordinatorID=? OR BroughtInByOwnerID=? OR OriginalOwnerID=? OR CurrentVetID=? OR OwnersVetID=? OR NeuteredByVetID = ?", (personid, personid, personid, personid, personid, personid)):
        raise asm3.utils.ASMValidationError(_("This person is linked to an animal and cannot be removed.", l))
    if dbo.query_int("SELECT COUNT(ID) FROM ownerdonation WHERE OwnerID=?", [personid]):
        raise asm3.utils.ASMValidationError(_("This person has payments and cannot be removed.", l))
    if dbo.query_int("SELECT COUNT(ID) FROM animallost WHERE OwnerID=?", [personid]):
        raise asm3.utils.ASMValidationError(_("This person is linked to lost animals and cannot be removed.", l))
    if dbo.query_int("SELECT COUNT(ID) FROM animalfound WHERE OwnerID=?", [personid]):
        raise asm3.utils.ASMValidationError(_("This person is linked to found animals and cannot be removed.", l))
    if dbo.query_int("SELECT COUNT(ID) FROM animalwaitinglist WHERE OwnerID=?", [personid]):
        raise asm3.utils.ASMValidationError(_("This person is linked to a waiting list record and cannot be removed.", l))
    if dbo.query_int("SELECT COUNT(ID) FROM ownercitation WHERE OwnerID=?", [personid]):
        raise asm3.utils.ASMValidationError(_("This person is linked to citations and cannot be removed.", l))
    if dbo.query_int("SELECT COUNT(ID) FROM ownertraploan WHERE OwnerID=?", [personid]):
        raise asm3.utils.ASMValidationError(_("This person is linked to trap loans and cannot be removed.", l))
    if dbo.query_int("SELECT COUNT(ID) FROM ownerinvestigation WHERE OwnerID=?", [personid]):
        raise asm3.utils.ASMValidationError(_("This person is linked to an investigation and cannot be removed.", l))
    if dbo.query_int("SELECT COUNT(ID) FROM ownerlicence WHERE OwnerID=?", [personid]):
        raise asm3.utils.ASMValidationError(_("This person is linked to animal licenses and cannot be removed.", l))
    if dbo.query_int("SELECT COUNT(ID) FROM animalcontrol WHERE OwnerID=? OR Owner2ID=? OR Owner3ID = ? OR CallerID=? OR VictimID=?", (personid, personid, personid, personid, personid)):
        raise asm3.utils.ASMValidationError(_("This person is linked to animal control and cannot be removed.", l))
    if dbo.query_int("SELECT COUNT(ID) FROM animaltransport WHERE DriverOwnerID=? OR PickupOwnerID=? OR DropoffOwnerID=?", (personid, personid, personid)):
        raise asm3.utils.ASMValidationError(_("This person is linked to animal transportation and cannot be removed.", l))
    dbo.delete("media", "LinkID=%d AND LinkTypeID=%d" % (personid, asm3.media.PERSON), username)
    dbo.delete("diary", "LinkID=%d AND LinkType=%d" % (personid, asm3.diary.PERSON), username)
    dbo.delete("log", "LinkID=%d AND LinkType=%d" % (personid, asm3.log.PERSON), username)
    dbo.execute("DELETE FROM additional WHERE LinkID = %d AND LinkType IN (%s)" % (personid, asm3.additional.PERSON_IN))
    for t in [ "adoption", "clinicappointment", "ownercitation", "ownerdonation", "ownerlicence", "ownertraploan", "ownervoucher" ]:
        dbo.delete(t, "OwnerID=%d" % personid, username)
    dbo.delete("owner", personid, username)
    # asm3.dbfs.delete_path(dbo, "/owner/%d" % personid) # Use maint_db_delete_orphaned_media to remove dbfs later if needed

def insert_rota_from_form(dbo, username, post):
    """
    Creates a rota record from posted form data
    """
    return dbo.insert("ownerrota", {
        "OwnerID":          post.integer("person"),
        "StartDateTime":    post.datetime("startdate", "starttime"),
        "EndDateTime":      post.datetime("enddate", "endtime"),
        "RotaTypeID":       post.integer("type"),
        "WorkTypeID":       post.integer("worktype"),
        "Comments":         post["comments"]
    }, username)

def update_rota_from_form(dbo, username, post):
    """
    Updates a rota record from posted form data
    """
    return dbo.update("ownerrota", post.integer("rotaid"), {
        "OwnerID":          post.integer("person"),
        "StartDateTime":    post.datetime("startdate", "starttime"),
        "EndDateTime":      post.datetime("enddate", "endtime"),
        "RotaTypeID":       post.integer("type"),
        "WorkTypeID":       post.integer("worktype"),
        "Comments":         post["comments"]
    }, username)

def delete_rota(dbo, username, rid):
    """
    Deletes the selected rota record
    """
    dbo.delete("ownerrota", rid, username)

def delete_rota_week(dbo, username, startdate):
    """
    Deletes all rota records beginning at startdate and ending at
    startdate+7
    startdate: A python date representing the start of the week
    """
    enddate = add_days(startdate, 7)
    dbo.delete("ownerrota", "StartDateTime>=%s AND StartDateTime<=%s" % (dbo.sql_date(startdate), dbo.sql_date(enddate)), username)

def insert_investigation_from_form(dbo, username, post):
    """
    Creates an investigation record from posted form data
    """
    return dbo.insert("ownerinvestigation", {
        "OwnerID":      post.integer("personid"),
        "Date":         post.date("date"),
        "Notes":        post["notes"]
    }, username)

def update_investigation_from_form(dbo, username, post):
    """
    Updates an investigation record from posted form data
    """
    dbo.update("ownerinvestigation", post.integer("investigationid"), {
        "Date":         post.date("date"),
        "Notes":        post["notes"]
    }, username)

def delete_investigation(dbo, username, iid):
    """
    Deletes the selected investigation record
    """
    dbo.delete("ownerinvestigation", iid, username)

def send_email_from_form(dbo, username, post):
    """
    Sends an email to a person from a posted form. Attaches it as
    a log entry if specified.
    """
    emailfrom = post["from"]
    emailto = post["to"]
    emailcc = post["cc"]
    emailbcc = post["bcc"]
    subject = post["subject"]
    addtolog = post.boolean("addtolog")
    logtype = post.integer("logtype")
    body = post["body"]
    rv = asm3.utils.send_email(dbo, emailfrom, emailto, emailcc, emailbcc, subject, body, "html")
    if asm3.configuration.audit_on_send_email(dbo): 
        asm3.audit.email(dbo, username, emailfrom, emailto, emailcc, emailbcc, subject, body)
    if addtolog == 1:
        asm3.log.add_log_email(dbo, username, asm3.log.PERSON, post.integer("personid"), logtype, emailto, subject, body)
    return rv

def lookingfor_summary(dbo, personid, p = None):
    """
    Generates the summary text for the type of animal a person is looking for. 
    personid: The person to generate for OR 
    p:        A person record with key fields for MATCH*NAME present to save looking up the record
    """
    l = dbo.locale
    if p is None:
        p = dbo.first_row(dbo.query("SELECT owner.*, " \
            "(SELECT Size FROM lksize WHERE ID = owner.MatchSize) AS MatchSizeName, " \
            "(SELECT BaseColour FROM basecolour WHERE ID = owner.MatchColour) AS MatchColourName, " \
            "(SELECT Sex FROM lksex WHERE ID = owner.MatchSex) AS MatchSexName, " \
            "(SELECT BreedName FROM breed WHERE ID = owner.MatchBreed) AS MatchBreedName, " \
            "(SELECT AnimalType FROM animaltype WHERE ID = owner.MatchAnimalType) AS MatchAnimalTypeName, " \
            "(SELECT SpeciesName FROM species WHERE ID = owner.MatchSpecies) AS MatchSpeciesName " \
            "FROM owner WHERE owner.ID = ?", [personid]))
    c = []
    if p.MATCHANIMALTYPE != -1: 
        c.append(p.MATCHANIMALTYPENAME)
    if p.MATCHSPECIES != -1: 
        c.append(p.MATCHSPECIESNAME)
    if p.MATCHBREED != -1: 
        c.append(p.MATCHBREEDNAME)
    if p.MATCHSEX != -1: 
        c.append(p.MATCHSEXNAME)
    if p.MATCHSIZE != -1: 
        c.append(p.MATCHSIZENAME)
    if p.MATCHCOLOUR != -1: 
        c.append(p.MATCHCOLOURNAME)
    if p.MATCHGOODWITHCHILDREN == 0: 
        c.append(_("Good with kids", l))
    if p.MATCHGOODWITHCATS == 0: 
        c.append(_("Good with cats", l))
    if p.MATCHGOODWITHDOGS == 0: 
        c.append(_("Good with dogs", l))
    if p.MATCHHOUSETRAINED == 0: 
        c.append(_("Housetrained", l))
    if p.MATCHAGEFROM and p.MATCHAGETO and p.MATCHAGEFROM >= 0 and p.MATCHAGETO > 0: 
        c.append(_("Age", l) + (" %0.2f - %0.2f" % (p.MATCHAGEFROM, p.MATCHAGETO)))
    if p.MATCHCOMMENTSCONTAIN is not None and p.MATCHCOMMENTSCONTAIN != "":
        c.append(_("Comments Contain", l) + ": " + p.MATCHCOMMENTSCONTAIN)
    summary = ""
    if len(c) > 0:
        summary = ", ".join(x for x in c if x is not None)
    return summary

def lookingfor_report(dbo, username = "system", personid = 0, limit = 0):
    """
    Generates the person looking for report
    """
    l = dbo.locale
    title = _("People Looking For", l)
    h = []
    batch = []
    h.append(asm3.reports.get_report_header(dbo, title, username))
    if limit > 0:
        h.append("<p>(" + _("Limited to {0} matches", l).format(limit) + ")</p>")
    def td(s): 
        return "<td>%s</td>" % s
    def hr(): 
        return "<hr />"

    idclause = ""
    if personid != 0:
        idclause = " AND owner.ID=%d" % personid
  
    people = dbo.query("SELECT owner.*, " \
        "(SELECT Size FROM lksize WHERE ID = owner.MatchSize) AS MatchSizeName, " \
        "(SELECT BaseColour FROM basecolour WHERE ID = owner.MatchColour) AS MatchColourName, " \
        "(SELECT Sex FROM lksex WHERE ID = owner.MatchSex) AS MatchSexName, " \
        "(SELECT BreedName FROM breed WHERE ID = owner.MatchBreed) AS MatchBreedName, " \
        "(SELECT AnimalType FROM animaltype WHERE ID = owner.MatchAnimalType) AS MatchAnimalTypeName, " \
        "(SELECT SpeciesName FROM species WHERE ID = owner.MatchSpecies) AS MatchSpeciesName " \
        "FROM owner WHERE MatchActive = 1 AND " \
        "(MatchExpires Is Null OR MatchExpires > %s)%s " \
        "ORDER BY OwnerName" % (dbo.sql_today(), idclause))

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
    asm3.asynctask.set_progress_max(dbo, len(people))
    for p in people:
        asm3.asynctask.increment_progress_value(dbo)
        ands = [ "a.Archived=0", "a.IsNotAvailableForAdoption=0", "a.HasActiveReserve=0", "a.CrueltyCase=0", "a.DeceasedDate Is Null" ]
        v = [] # query values
        if p.MATCHANIMALTYPE != -1: 
            ands.append("a.AnimalTypeID=?")
            v.append(p.MATCHANIMALTYPE)
        if p.MATCHSPECIES != -1: 
            ands.append("a.SpeciesID=?")
            v.append(p.MATCHSPECIES)
        if p.MATCHBREED != -1: 
            ands.append("(a.BreedID=? OR a.Breed2ID=?)")
            v.append(p.MATCHBREED)
            v.append(p.MATCHBREED)
        if p.MATCHSEX != -1: 
            ands.append("a.Sex=?")
            v.append(p.MATCHSEX)
        if p.MATCHSIZE != -1: 
            ands.append("a.Size=?")
            v.append(p.MATCHSIZE)
        if p.MATCHCOLOUR != -1: 
            ands.append("a.BaseColourID=?")
            v.append(p.MATCHCOLOUR)
        if p.MATCHGOODWITHCHILDREN == 0: 
            ands.append("a.IsGoodWithChildren=0")
        if p.MATCHGOODWITHCATS == 0: 
            ands.append("a.IsGoodWithCats=0")
        if p.MATCHGOODWITHDOGS == 0: 
            ands.append("a.IsGoodWithDogs=0")
        if p.MATCHHOUSETRAINED == 0: 
            ands.append("a.IsHouseTrained=0")
        if p.MATCHAGEFROM >= 0 and p.MATCHAGETO > 0: 
            ands.append("a.DateOfBirth BETWEEN ? AND ?")
            v.append(subtract_years(now(dbo.timezone), p.MATCHAGETO))
            v.append(subtract_years(now(dbo.timezone), p.MATCHAGEFROM))
        if p.MATCHCOMMENTSCONTAIN is not None and p.MATCHCOMMENTSCONTAIN != "":
            for w in str(p.MATCHCOMMENTSCONTAIN).split(" "):
                ands.append("(a.AnimalComments LIKE ? OR a.HiddenAnimalDetails LIKE ?)")
                v.append("%%%s%%" % w)
                v.append("%%%s%%" % w)

        animals = dbo.query(asm3.animal.get_animal_query(dbo) + " WHERE " + " AND ".join(ands) + " ORDER BY a.LastChangedDate DESC", v)

        # Output owner info
        h.append("<h2><a target='_blank' href='person?id=%s'>%s</a> (%s) %s %s</h2>" % (p.ID, p.OWNERNAME, p.OWNERADDRESS, p.HOMETELEPHONE, p.MOBILETELEPHONE))
        if p.MATCHADDED is not None or p.MATCHEXPIRES is not None:
            h.append( "<p style='font-size: 8pt'>%s - %s</p>" % (python2display(l, p.MATCHADDED), python2display(l, p.MATCHEXPIRES)) )
        if p.COMMENTS != "" and p.COMMENTS is not None: 
            h.append( "<p style='font-size: 8pt'>%s</p>" % p.COMMENTS)

        # Summary of owner criteria
        summary = lookingfor_summary(dbo, p.ID, p)
        h.append( "<p style='font-size: 8pt'>(%s: %s)</p>" % (_("Looking for", l), summary) )

        # Match info
        outputheader = False
        for a in animals:
            if not outputheader:
                outputheader = True
                h.append("".join(ah))
            h.append( "<tr>")
            h.append( td(a.CODE))
            h.append( td("<a target='_blank' href='animal?id=%s'>%s</a>" % (a.ID, a.ANIMALNAME)) )
            h.append( td(a.ANIMALAGE))
            h.append( td(a.SEXNAME))
            h.append( td(a.SIZENAME))
            h.append( td(a.BASECOLOURNAME))
            h.append( td(a.SPECIESNAME))
            h.append( td(a.BREEDNAME))
            h.append( td(a.ISGOODWITHCATSNAME))
            h.append( td(a.ISGOODWITHDOGSNAME))
            h.append( td(a.ISGOODWITHCHILDRENNAME))
            h.append( td(a.ISHOUSETRAINEDNAME))
            h.append( td(a.ANIMALCOMMENTS + " " + a.HIDDENANIMALDETAILS))
            h.append( "</tr>")

            # Add an entry to ownerlookingfor for other reports
            if personid == 0:
                batch.append( ( a.ID, p.ID, summary ) )

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

    h.append( asm3.reports.get_report_footer(dbo, title, username))

    # Update ownerlookingfor table
    if personid == 0:
        dbo.execute("DELETE FROM ownerlookingfor")
        if len(batch) > 0:
            dbo.execute_many("INSERT INTO ownerlookingfor (AnimalID, OwnerID, MatchSummary) VALUES (?,?,?)", batch)

    return "".join(h)

def lookingfor_last_match_count(dbo):
    """
    Returns the number of matches the last time lookingfor was run
    """
    return dbo.query_int("SELECT COUNT(*) FROM ownerlookingfor")

def update_check_flags(dbo):
    """
    Goes through all people records and verifies that if they have one of
    the IsX flag columns set that the builtin value is present in the
    AdditionalFlags column.
    This is needed because many of the IsX values pre-date the AdditionalFlags
    column, but there are many reports that use it solely as the method of
    determining flags.
    This will also re-order the additional flags into alphabetical order
    and remove any flags that no longer exist in lkownerflags.
    """
    builtins = {
        "excludefrombulkemail": "ExcludeFromBulkEmail",
        "homechecked": "IDCheck",
        "banned": "IsBanned",
        "dangerous": "IsDangerous",
        "volunteer": "IsVolunteer",
        "homechecker": "IsHomeChecker",
        "member": "IsMember",
        "adopter": "IsAdopter",
        "coordinator": "IsAdoptionCoordinator",
        "donor": "IsDonor",
        "driver": "IsDriver",
        "shelter": "IsShelter",
        "aco": "IsACO",
        "staff": "IsStaff",
        "fosterer": "IsFosterer",
        "retailer": "IsRetailer",
        "vet": "IsVet",
        "giftaid": "IsGiftAid"
    }
    people = dbo.query("SELECT ID, AdditionalFlags, ExcludeFromBulkEmail, IDCheck, IsBanned, IsDangerous, IsVolunteer, " \
        "IsHomeChecker, IsMember, IsAdopter, IsAdoptionCoordinator, IsDonor, IsDriver, " \
        "IsShelter, IsACO, IsStaff, IsFosterer, IsRetailer, IsVet, IsGiftAid, IsSponsor FROM owner ORDER BY ID")
    lookupflags = [x["FLAG"] for x in dbo.query("SELECT Flag from lkownerflags ORDER BY Flag")]
    batch = []
    asm3.asynctask.set_progress_max(dbo, len(people))
    for p in people:
        asm3.asynctask.increment_progress_value(dbo)
        pflags = asm3.utils.nulltostr(p.ADDITIONALFLAGS).split("|")
        # Add any missing builtins
        for flag, column in builtins.items():
            if p[column.upper()] == 1 and flag not in pflags:
                pflags.append(flag)
        # Throw away flags that are not built ins or in our lookup set
        pflags = [x for x in pflags if x != "" and (x in lookupflags or x in builtins)]
        # Sort and reconstruct
        newval = "|".join(sorted(pflags, key = lambda x: x.lower())) + "|"
        if newval != p.ADDITIONALFLAGS:
            batch.append([ newval, p.ID ])
    if len(batch) > 0:
        dbo.execute_many("UPDATE owner SET AdditionalFlags=? WHERE ID=?", batch)
    asm3.al.debug("updated %d person flags" % len(batch), "person.update_missing_builtin_flags", dbo)
    return "OK %d" % len(batch)

def update_missing_geocodes(dbo):
    """
    Goes through all people records without geocodes and completes
    the missing ones, using our configured bulk geocoding service.
    We limit this to LIMIT geocode requests per call so that databases with
    a lot of historical data don't end up tying up the daily
    batch for a long time, they'll just slowly complete over time.
    """
    if not GEO_BATCH:
        asm3.al.warn("GEO_BATCH is False, skipping", "update_missing_geocodes", dbo)
        return
    people = dbo.query("SELECT ID, OwnerAddress, OwnerTown, OwnerCounty, OwnerPostcode " \
        "FROM owner WHERE LatLong Is Null OR LatLong = '' ORDER BY CreatedDate DESC", limit=GEO_LIMIT)
    batch = []
    for p in people:
        latlong = asm3.geo.get_lat_long(dbo, p.OWNERADDRESS, p.OWNERTOWN, p.OWNERCOUNTY, p.OWNERPOSTCODE)
        batch.append((latlong, p.ID))
    dbo.execute_many("UPDATE owner SET LatLong = ? WHERE ID = ?", batch)
    asm3.al.debug("updated %d person geocodes" % len(batch), "person.update_missing_geocodes", dbo)

def update_lookingfor_report(dbo):
    """
    Updates the latest version of the looking for report in the cache
    """
    asm3.al.debug("updating lookingfor report", "person.update_lookingfor_report", dbo)
    s = lookingfor_report(dbo, limit=5000)
    count = lookingfor_last_match_count(dbo)
    asm3.cachedisk.put("lookingfor_report", dbo.database, s, 86400)
    asm3.cachedisk.put("lookingfor_lastmatchcount", dbo.database, count, 86400)
    return "OK %d" % count

def update_anonymise_personal_data(dbo, overrideretainyears = None):
    """
    Anonymises personal data once the retention period in years is up.
    A cutoff date is calculated from today - retentionyears. If the person was
    created before this date and has no movements, payments or logs more recent than that date, 
    they are considered expired.
    The name, address, email and phone fields are blanked, the surname is set to a fixed string
    and the town/county/postcode fields are left alone for statistics and reporting purposes.
    Setting overrideretainyears allows the caller to set the retention period (None uses the config values)
    People with the following flags are NOT anonymised due to a presumed ongoing relationship -  
        aco, adoptioncoordinator, retailer, homechecker, member, shelter, foster, staff, vet, volunteer
    """
    l = dbo.locale
    anonymised = _("No longer retained", l)
    enabled = asm3.configuration.anonymise_personal_data(dbo)
    retainyears = asm3.configuration.anonymise_after_years(dbo)
    if overrideretainyears:
        enabled = True
        retainyears = overrideretainyears
    if not enabled or retainyears == 0:
        asm3.al.debug("set to retain personal data indefinitely, abandoning.", "person.update_anonymise_personal_data", dbo)
        return
    cutoff = dbo.today(offset = -365 * retainyears)
    affected = dbo.execute("UPDATE owner SET OwnerTitle = '', OwnerInitials = '', OwnerForeNames = '', " \
        "OwnerSurname = ?, OwnerName = ?, OwnerAddress = '', EmailAddress = '', " \
        "HomeTelephone = '', WorkTelephone = '', MobileTelephone = '', " \
        "LastChangedDate = ?, LastChangedBy = ? " \
        "WHERE OwnerSurname <> ? AND CreatedDate <= ? " \
        "AND IsACO=0 AND IsAdoptionCoordinator=0 AND IsRetailer=0 AND IsHomeChecker=0 AND IsMember=0 " \
        "AND IsShelter=0 AND IsFosterer=0 AND IsStaff=0 AND IsVet=0 AND IsVolunteer=0 " \
        "AND NOT EXISTS(SELECT ID FROM animal WHERE (OriginalOwnerID = owner.ID OR BroughtInByOwnerID = owner.ID) AND DateBroughtIn > ?) " \
        "AND NOT EXISTS(SELECT ID FROM clinicappointment WHERE OwnerID = owner.ID AND DateTime > ?) " \
        "AND NOT EXISTS(SELECT ID FROM ownerdonation WHERE OwnerID = owner.ID AND Date > ?) " \
        "AND NOT EXISTS(SELECT ID FROM adoption WHERE OwnerID = owner.ID AND MovementDate > ?) " \
        "AND NOT EXISTS(SELECT ID FROM log WHERE LinkID = owner.ID AND LogTypeID = 1 AND Date > ?) ", 
        ( anonymised, anonymised, dbo.now(), "system", anonymised, cutoff, cutoff, cutoff, cutoff, cutoff, cutoff ))
    asm3.al.debug("anonymised %s expired person records outside of retention period (%s years)." % (affected, retainyears), "person.update_anonymise_personal_data", dbo)
    return "OK %d" % affected

