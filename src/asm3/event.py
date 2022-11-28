import datetime

import asm3.additional

from asm3.i18n import _



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

    pid = dbo.insert("event", {
        "StartDateTime": post.date("startdate"),
        "EndDateTime": post.date("enddate"),
        "EventName": post["eventname"],
        "EventOwnerID": ownerid,
        "EventAddress": post["address"],
        "EventTown": post["town"],
        "EventCounty": post["county"],
        "EventPostCode": post["postcode"],
        "EventCountry": post["country"]
    }, user=username)

    # Save any additional field values given
    asm3.additional.save_values_for_link(dbo, post, username, pid, "event", True)
    return pid
