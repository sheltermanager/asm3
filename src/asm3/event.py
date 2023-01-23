import asm3.additional

from asm3.i18n import _


def get_event_query(dbo):
    return "SELECT ev.*, owner.OwnerName AS EventOwnerName, " \
           "(SELECT COUNT(*) FROM adoption a WHERE a.EventID = ev.ID) AS adoptions " \
           "FROM event ev " \
           "LEFT OUTER JOIN owner ON ev.EventOwnerID = owner.ID "

def get_event(dbo, eventid):
    """
    Returns a complete event row by id
    (int) eventid: The event to get
    """
    return dbo.first_row(dbo.query(get_event_query(dbo) + "WHERE ev.ID = ?", [eventid]))

def get_event_date(dbo, movementdate):
    """
    Returns events that match movementdate
    """
    return dbo.query(get_event_query(dbo) + "WHERE (ev.StartDateTime <= ? AND ? <= ev.EndDateTime) ORDER BY ev.StartDateTime", [movementdate, movementdate])

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
