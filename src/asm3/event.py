import asm3.additional


def get_event_query(dbo):
    return "SELECT ev.*, owner.OwnerName AS EventOwnerName " \
           "FROM event ev " \
           "LEFT OUTER JOIN owner ON ev.EventOwnerID = owner.ID "


def get_event(dbo, eventid):
    """
    Returns a complete event row by id
    (int) eventid: The event to get
    """
    e = dbo.first_row(dbo.query(get_event_query(dbo) + " WHERE ev.ID = %d" % eventid))
    return e


def insert_event_from_form(dbo, post, username):
    l = dbo.locale
    pid = dbo.get_id("event")

    dbo.insert("event", {
        "ID": pid,
        "StartDateTime": post.date("startdate"),
        "EndDateTime": post.date("enddate"),
        "EventName": post["eventname"],
        "EventOwnerID": post["ownerid"],
        "EventAddress": post["address"],
        "EventTown": post["town"],
        "EventCounty": post["county"],
        "EventPostCode": post["postcode"],
        "EventCountry": post["country"]
    }, user=username, generateID=False)

    # Save any additional field values given
    asm3.additional.save_values_for_link(dbo, post, username, pid, "event", True)
    return pid
