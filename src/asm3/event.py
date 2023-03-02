import asm3.additional
import asm3.movement

from asm3.i18n import _


def get_event_query(dbo):
    return "SELECT ev.*, owner.OwnerName AS EventOwnerName, " \
           "(SELECT COUNT(*) FROM adoption a WHERE a.EventID = ev.ID) AS adoptions " \
           "FROM event ev " \
           "LEFT OUTER JOIN owner ON ev.EventOwnerID = owner.ID "

def get_event_animal_query(dbo):
    return "SELECT ea.ID, owner.OwnerName AS EventOwnerName, ea.ArrivalDate, ea.Comments, " \
           "a.id AS AnimalID, a.animalname, a.SHORTCODE, a.SHELTERCODE, a.MOSTRECENTENTRYDATE, a.LASTCHANGEDDATE, a.LASTCHANGEDBY,  a.AcceptanceNumber AS LitterID, a.AnimalAge, " \
           "a.Sex, s.SpeciesName, a.DisplayLocation, a.AgeGroup, " \
           "bc.BaseColour AS BaseColourName, " \
           "sx.Sex AS SexName, " \
           "bd.BreedName AS BreedName, " \
           "ma.MediaName AS WebsiteMediaName, ma.Date AS WebsiteMediaDate, " \
           "CASE WHEN EXISTS (SELECT * FROM adoption ad WHERE ad.eventid = ea.eventid AND ad.movementtype = 1 AND ad.animalid = ea.animalid) THEN 1 ELSE 0 END AS Adopted, " \
           "lastfosterer.ownerid as LastFostererID, lastfosterer.ownername AS LastFostererName, lastfosterer.returndate AS LastFostererReturnDate, lastfosterer.mobiletelephone AS LastFostererMobileTelephone, lastfosterer.hometelephone AS LastFostererHomeTelephone, lastfosterer.worktelephone  AS LastFostererWorkTelephone " \
           "FROM eventanimal ea " \
           "INNER JOIN animal a ON ea.animalid = a.id " \
           "INNER JOIN event ev ON ev.id = ea.eventid " \
           "LEFT OUTER JOIN media ma ON ma.LinkID = a.ID AND ma.LinkTypeID = 0 AND ma.WebsitePhoto = 1 " \
           "LEFT OUTER JOIN breed bd ON bd.ID = a.BreedID " \
           "LEFT OUTER JOIN species s ON a.SpeciesID = s.ID " \
           "LEFT OUTER JOIN lksex sx ON sx.ID = a.Sex " \
           "LEFT OUTER JOIN owner ON ev.EventOwnerID = owner.ID " \
           "LEFT OUTER JOIN basecolour bc ON bc.ID = a.BaseColourID " \
           "LEFT JOIN (SELECT * FROM (SELECT m.ownerid, m.animalid, row_number() OVER (PARTITION BY m.animalid ORDER BY CASE WHEN m.returndate IS NULL THEN 0 ELSE 1 END, m.returndate DESC) AS rn, m.returndate, o.ownername, o.mobiletelephone, o.hometelephone, o.worktelephone FROM adoption m INNER JOIN owner o ON m.ownerid = o.id WHERE m.movementtype=2) t WHERE rn = 1) lastfosterer ON lastfosterer.animalid = ea.animalid"

def get_event(dbo, eventid):
    """
    Returns a complete event row by id
    """
    return dbo.first_row(dbo.query(get_event_query(dbo) + "WHERE ev.ID = ?", [eventid]))

def get_events_by_animal(dbo, animalid):
    """
    Returns all events for animalid
    """
    return dbo.query(get_event_animal_query(dbo) + " WHERE ea.animalid = ?", [animalid])

def get_animals_by_event(dbo, eventid, queryfilter="all"):
    """
    Returns all events for animalid.
    if queryfilter is provided, add conditions
    """
    filters = {
        "all": "",
        "arrived": " AND ea.ArrivalDate is not null",
        "noshow": " AND ea.ArrivalDate is null",
        "neednewfoster": " AND lastfosterer.returndate IS NOT NULL",
        "dontneednewfoster": " AND lastfosterer.returndate IS NULL",
        "adopted": " AND ad.id IS NOT NULL",
        "notadopted": " AND ad.id IS NULL",
    }
    whereclause = " WHERE ev.id=? " + (filters[queryfilter] if queryfilter in filters else "")
    return dbo.query(get_event_animal_query(dbo) + whereclause, [eventid])


def get_events_by_date(dbo, date):
    """
    Returns all events that match date
    """
    return dbo.query(get_event_query(dbo) + "WHERE (ev.StartDateTime <= ? AND ? <= ev.EndDateTime) ORDER BY ev.StartDateTime", [date, date])

def insert_event_from_form(dbo, post, username):
    l = dbo.locale
    ownerid = post["ownerid"]
    if ownerid == "" or ownerid == "0":
        ownerid = None

    if post["startdate"].strip() == "":
        raise asm3.utils.ASMValidationError(_("Event must have a start date.", l))
    if post["enddate"].strip() == "":
        raise asm3.utils.ASMValidationError(_("Event must have an end date.", l))
    if post["address"].strip() == "":
        raise asm3.utils.ASMValidationError(_("Event must have an address.", l))
    if post.date("startdate") > post.date("enddate"):
        raise asm3.utils.ASMValidationError(_("End date must be equal to or later than start date.", l))

    eid = dbo.insert("event", {
        "StartDateTime": post.date("startdate"),
        "EndDateTime": post.date("enddate"),
        "EventName": post["eventname"],
        "EventDescription": post["description"],
        "EventOwnerID": ownerid,
        "EventAddress": post["address"],
        "EventTown": post["town"],
        "EventCounty": post["county"],
        "EventPostCode": post["postcode"],
        "EventCountry": post["country"]
    }, username)

    # Save any additional field values given
    asm3.additional.save_values_for_link(dbo, post, username, eid, "event", True)
    return eid

def update_event_from_form(dbo, post, username):
    """
    Updates an existing event record from incoming form data
    """

    l = dbo.locale
    if not dbo.optimistic_check("event", post.integer("id"), post.integer("recordversion")):
        raise asm3.utils.ASMValidationError(_("This record has been changed by another user, please reload.", l))

    if post["startdate"].strip() == "":
        raise asm3.utils.ASMValidationError(_("Event must have a start date.", l))
    if post["enddate"].strip() == "":
        raise asm3.utils.ASMValidationError(_("Event must have an end date.", l))
    if post["address"].strip() == "":
        raise asm3.utils.ASMValidationError(_("Event must have an address.", l))
    if post.date("startdate") > post.date("enddate"):
        raise asm3.utils.ASMValidationError(_("End date must be equal to or later than start date.", l))

    eid = post.integer("id")

    dbo.update("event", eid, {
        "StartDateTime": post.date("startdate"),
        "EndDateTime": post.date("enddate"),
        "EventName": post["eventname"],
        "EventDescription": post["description"],
        "EventOwnerID": post.integer("ownerid"),
        "EventAddress": post["address"],
        "EventTown": post["town"],
        "EventCounty": post["county"],
        "EventPostCode": post["postcode"],
        "EventCountry": post["country"]
    }, username)

    # Save any asm3.additional.field values given
    asm3.additional.save_values_for_link(dbo, post, username, eid, "event")

def delete_event(dbo, username, eventid):
    """
    Deletes a person and all its satellite records.
    """
    l = dbo.locale
    if dbo.query_int("SELECT COUNT(ID) FROM adoption WHERE EventID=?", [eventid]):
        raise asm3.utils.ASMValidationError(_("This event is linked to an adoption and cannot be removed.", l))

    dbo.execute("DELETE FROM additional WHERE LinkID = %d AND LinkType IN (%s)" % (eventid, asm3.additional.EVENT_IN))
    dbo.delete("event", eventid, username)

def get_event_find_advanced(dbo, criteria, limit = 0, siteid = 0):
    """
    Returns rows for advanced animal control searches.
    criteria: A dictionary of criteria
       name - string partial pattern
       eventfrom - event start range from in current display locale format
       eventto - event end range from in current display locale format
       location - string partial pattern
       address - string partial pattern
       town - string partial pattern
       county - string partial pattern
       postcode - string partial pattern
       country - string partial pattern
    """
    post = asm3.utils.PostedData(criteria, dbo.locale)
    ss = asm3.utils.AdvancedSearchBuilder(dbo, post)

    ss.ands.append("ev.ID > 0")
    ss.add_str("name", "ev.eventname")
    ss.add_str("location", "owner.OwnerName")
    ss.add_str("address", "ev.eventaddress")
    ss.add_str("city", "ev.eventtown")
    ss.add_str("county", "ev.eventcounty")
    ss.add_str("postcode", "ev.eventpostcode")
    ss.add_str("country", "ev.eventcountry")
    ss.add_daterange("eventfrom", "eventto", "ev.startdatetime", "ev.enddatetime")

    sql = "%s WHERE %s ORDER BY ev.ID DESC" % (get_event_query(dbo), " AND ".join(ss.ands))
    rows = dbo.query(sql, ss.values, limit=limit, distincton="ID")
    return rows


def insert_event_animal(dbo, username, post):
    """
    Creates an eventanimal record from posted form data
    """
    eventid = post.integer("eventid")
    animalid = post.integer("animalid")
    sql = "SELECT id FROM eventanimal WHERE eventid = ? and animalid = ?"
    eventanimalid = dbo.query_int(sql, [eventid, animalid])
    if eventanimalid == 0:
        eventanimalid = dbo.insert("eventanimal", {
            "EventID":              eventid,
            "AnimalID":             animalid,
        }, username)
    return eventanimalid

def update_event_animal(dbo, username, post):
    """
    Updates an eventanimal record from posted form data
    """
    eventanimalid = post.integer("eventanimalid")

    kvp = {}
    if "animal" in post: kvp["AnimalID"] = post.integer("animal"),
    if "arrivaldate" in post and "arrivaltime" in post: kvp["ArrivalDate"] = post.datetime("arrivaldate", "arrivaltime")
    if "comments" in post: kvp["Comments"] = post["comments"]
    dbo.update("eventanimal", eventanimalid, kvp, username)

def update_event_animal_arrived(dbo, username, eaid):
    sql = "SELECT id FROM eventanimal WHERE id = ? AND ArrivalDate IS NULL"
    eventanimalid = dbo.query_int(sql, [eaid])
    if eventanimalid != 0:
        dbo.update("eventanimal", eventanimalid, {"ArrivalDate": dbo.now()})


def delete_event_animal(dbo, username, id):
    """
    Deletes an eventanimal record
    """
    dbo.delete("animalvaccination", id, username)

def end_active_foster(dbo, username, id):
    """
    Set return date for an active foster for animal(s) in event
    """
    sql = """SELECT ev.startdatetime, ea.animalid, m.id as movementid
             FROM event ev 
             INNER JOIN eventanimal ea ON ev.id = ea.eventid
             INNER JOIN adoption m ON m.animalid = ea.animalid 
             WHERE ea.id = ?
             AND m.movementtype=2
             AND m.returndate IS NULL;
    """
    rows = dbo.query(sql, [id])
    if len(rows) > 0: # there is an active foster movement
        animalid = rows[0]["ANIMALID"]
        eventstartdate = rows[0]["STARTDATETIME"]
        movementid = rows[0]["MOVEMENTID"]
        #return from foster at event start or today, whichever is latest
        asm3.movement.return_movement(dbo, movementid, username, animalid, returndate = max(eventstartdate, dbo.today()))

