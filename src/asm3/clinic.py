
import asm3.al
import asm3.financial
import asm3.i18n
import asm3.utils

SCHEDULED = 0
INVOICE_ONLY = 1
NOT_ARRIVED = 2
WAITING = 3
WITH_VET = 4
COMPLETE = 5
CANCELLED = 6

ASCENDING = 0
DESCENDING = 1

def get_clinic_appointment_query(dbo):
    return "SELECT ca.*, o.OwnerTitle, o.OwnerInitials, o.OwnerSurname, o.OwnerForenames, o.OwnerName, " \
        "o.OwnerAddress, o.OwnerTown, o.OwnerCounty, o.OwnerPostcode, o.HomeTelephone, o.WorkTelephone, o.MobileTelephone, " \
        "cs.Status AS ClinicStatusName, " \
        "a.ShelterCode, a.ShortCode, a.AnimalAge, a.AgeGroup, a.AnimalName, a.BreedName, a.Neutered, a.DeceasedDate, a.HasActiveReserve, " \
        "a.HasTrialAdoption, a.IsHold, a.IsQuarantine, a.HoldUntilDate, a.CrueltyCase, a.NonShelterAnimal, " \
        "a.ActiveMovementType, a.Archived, a.IsNotAvailableForAdoption, " \
        "a.CombiTestResult, a.FLVResult, a.HeartwormTestResult, " \
        "ma.MediaName AS WebsiteMediaName, ma.Date AS WebsiteMediaDate, " \
        "sx.Sex, s.SpeciesName " \
        "FROM clinicappointment ca " \
        "LEFT OUTER JOIN lksclinicstatus cs ON cs.ID = ca.Status " \
        "LEFT OUTER JOIN animal a ON ca.AnimalID = a.ID " \
        "LEFT OUTER JOIN internallocation il ON a.ShelterLocation = il.ID " \
        "LEFT OUTER JOIN media ma ON ma.LinkID = a.ID AND ma.LinkTypeID = 0 AND ma.WebsitePhoto = 1 " \
        "LEFT OUTER JOIN species s ON a.SpeciesID = s.ID " \
        "LEFT OUTER JOIN lksex sx ON sx.ID = a.Sex " \
        "LEFT OUTER JOIN owner o ON ca.OwnerID = o.ID "

def get_clinic_invoice_query(dbo):
    return "SELECT ci.* " \
        "FROM clinicinvoiceitem ci "

def get_site_filter(siteid = 0):
    """ 
    Returns a site filter for use with appointment queries.
    Filters on people, so if the user has a non-zero siteid, only people with the matching site id are shown
    """
    if siteid == 0: return ""
    return " AND o.SiteID = %d" % siteid

def get_appointment(dbo, appointmentid):
    """
    Returns an appointment by ID
    """
    return dbo.first_row(dbo.query("%s WHERE ca.ID = ?" % get_clinic_appointment_query(dbo), [appointmentid]))

def get_animal_appointments(dbo, animalid):
    """
    Returns all appointments for an animal
    """
    return dbo.query("%s WHERE ca.AnimalID = ?" % get_clinic_appointment_query(dbo), [animalid])

def get_animal_appointments_due(dbo, animalid, start, end):
    """
    Returns all appointments for an animal between start and end (dates)
    """
    return dbo.query("%s WHERE ca.Status = 0 AND ca.AnimalID = ? AND ca.DateTime >= ? AND ca.DateTime <= ? ORDER BY ca.DateTime" % \
        get_clinic_appointment_query(dbo), [animalid, start, end])

def get_person_appointments(dbo, personid):
    """
    Returns all appointments for a person
    """
    return dbo.query("%s WHERE ca.OwnerID = ?" % get_clinic_appointment_query(dbo), [personid])

def get_appointments_today(dbo, sort=DESCENDING, statusfilter=-1, userfilter="", siteid=0):
    """
    Gets all appointments that are due today
    """
    order = "ca.DateTime"
    if sort == DESCENDING: order += " DESC"
    sf = ""
    if statusfilter != -1: sf = "AND ca.Status = %d" % statusfilter
    uf = ""
    if userfilter != "": uf = "AND ca.ApptFor = %s" % dbo.sql_value(userfilter)
    tf = ""
    if siteid != 0: tf = get_site_filter(siteid)
    sql = "%s WHERE ca.DateTime >= ? AND ca.DateTime <= ? %s %s %s ORDER BY %s" % (get_clinic_appointment_query(dbo), sf, uf, tf, order)
    return dbo.query(sql, [ dbo.today(), dbo.today(settime="23:59:59") ])

def get_appointments_two_dates(dbo, start, end, apptfor = "", siteid = 0):
    """
    Returns appointments due between two dates:
    start, end: dates 
    siteid: only show people with the matching siteid if non-zero
    """
    if apptfor != "":
        return dbo.query(get_clinic_appointment_query(dbo) + \
            "WHERE ca.Status NOT IN (?, ?) " \
            "AND ca.ApptFor = ? " \
            "AND ca.DateTime >= ? AND ca.DateTime <= ? %s " \
            "ORDER BY ca.DateTime" % (get_site_filter(siteid)), (COMPLETE, CANCELLED, apptfor, start, end))
    else:
        return dbo.query(get_clinic_appointment_query(dbo) + \
            "WHERE ca.Status NOT IN (?, ?) " \
            "AND ca.DateTime >= ? AND ca.DateTime <= ? %s " \
            "ORDER BY ca.DateTime" % (get_site_filter(siteid)), (COMPLETE, CANCELLED, start, end))

def get_invoice_items(dbo, appointmentid):
    """
    Gets all invoice items for an appointment
    """
    return dbo.query(get_clinic_invoice_query(dbo) + " WHERE ClinicAppointmentID = ? ORDER BY ID", [appointmentid])

def insert_appointment_from_form(dbo, username, post):
    """
    Creates a clinic appointment from posted form data
    """
    l = dbo.locale
    if post.datetime("apptdate", "appttime") is None:
        raise asm3.utils.ASMValidationError(asm3.i18n._("Appointment date must be a valid date", l))

    return dbo.insert("clinicappointment", {
        "AnimalID":             post.integer("personanimal") or post.integer("animal"),
        "OwnerID":              post.integer("person"),
        "ApptFor":              post["for"],
        "DateTime":             post.datetime("apptdate", "appttime"),
        "Status":               post.integer("status"),
        "ArrivedDateTime":      post.datetime("arriveddate", "arrivedtime"),
        "WithVetDateTime":      post.datetime("withvetdate", "withvettime"),
        "CompletedDateTime":    post.datetime("completedate", "completetime"),
        "ReasonForAppointment": post["reason"],
        "Comments":             post["comments"],
        "Amount":               post.integer("amount"),
        "IsVAT":                post.boolean("vat"),
        "VATRate":              post.floating("vatrate"),
        "VATAmount":            post.integer("vatamount")
    }, username)

def update_appointment_from_form(dbo, username, post):
    """
    Updates an appointment from form data
    """
    l = dbo.locale
    if post.datetime("apptdate", "appttime") is None:
        raise asm3.utils.ASMValidationError(asm3.i18n._("Appointment date must be a valid date", l))

    dbo.update("clinicappointment", post.integer("appointmentid"), {
        "AnimalID":             post.integer("personanimal") or post.integer("animal"),
        "OwnerID":              post.integer("person"),
        "ApptFor":              post["for"],
        "DateTime":             post.datetime("apptdate", "appttime"),
        "Status":               post.integer("status"),
        "ArrivedDateTime":      post.datetime("arriveddate", "arrivedtime"),
        "WithVetDateTime":      post.datetime("withvetdate", "withvettime"),
        "CompletedDateTime":    post.datetime("completedate", "completetime"),
        "ReasonForAppointment": post["reason"],
        "Comments":             post["comments"],
        "Amount":               post.integer("amount"),
        "IsVAT":                post.boolean("vat"),
        "VATRate":              post.floating("vatrate"),
        "VATAmount":            post.integer("vatamount")
    }, username)

def delete_appointment(dbo, username, appointmentid):
    """
    Deletes an appointment
    """
    dbo.delete("clinicinvoiceitem", "ClinicAppointmentID=%d" % appointmentid, username)
    dbo.delete("clinicappointment", appointmentid, username)

def update_appointment_to_waiting(dbo, username, appointmentid, datetime=None):
    """
    Moves an appointment to the waiting status
    """
    if datetime is None: datetime = dbo.now()
    dbo.update("clinicappointment", appointmentid, {
        "Status":           WAITING,
        "ArrivedDateTime":  datetime
    }, username)

def update_appointment_to_with_vet(dbo, username, appointmentid, datetime=None):
    """
    Moves an appointment to the with vet status
    """
    if datetime is None: datetime = dbo.now()
    dbo.update("clinicappointment", appointmentid, {
        "Status":           WITH_VET,
        "WithVetDateTime":  datetime
    }, username)

def update_appointment_to_complete(dbo, username, appointmentid, datetime=None):
    """
    Moves an appointment to the complete status
    """
    if datetime is None: datetime = dbo.now()
    dbo.update("clinicappointment", appointmentid, {
        "Status":             COMPLETE,
        "CompletedDateTime":  datetime
    }, username)

def update_appointment_total(dbo, appointmentid):
    """
    Calculates the amount and VAT on an appointment/invoice
    """
    a = get_appointment(dbo, appointmentid)
    total = dbo.query_int("SELECT SUM(Amount) FROM clinicinvoiceitem WHERE ClinicAppointmentID = ? AND Amount Is Not Null AND Amount > 0", [appointmentid])
    vatamount = 0
    if a.ISVAT == 1 and a.VATRATE > 0:
        vatamount = asm3.utils.cint(total * (a.VATRATE / 100.0))
    dbo.update("clinicappointment", appointmentid, {
        "Amount":       total,
        "VATAmount":    vatamount
    })

def insert_invoice_from_form(dbo, username, post):
    """
    Creates an invoice item from posted form data
    """
    nid = dbo.insert("clinicinvoiceitem", {
        "ClinicAppointmentID":      post.integer("appointmentid"),
        "Description":              post["description"],
        "Amount":                   post.integer("amount")
    }, username)
    update_appointment_total(dbo, post.integer("appointmentid"))
    return nid

def update_invoice_from_form(dbo, username, post):
    """
    Creates an invoice item from posted form data
    """
    dbo.update("clinicinvoiceitem", post.integer("itemid"), {
        "ClinicAppointmentID":      post.integer("appointmentid"),
        "Description":              post["description"],
        "Amount":                   post.integer("amount")
    }, username)
    update_appointment_total(dbo, post.integer("appointmentid"))

def delete_invoice(dbo, username, itemid):
    """
    Deletes an invoice item
    """
    appointmentid = dbo.query_int("SELECT ClinicAppointmentID FROM clinicinvoiceitem WHERE ID = ?", [itemid])
    dbo.delete("clinicinvoiceitem", itemid, username)
    update_appointment_total(dbo, appointmentid)

def insert_payment_from_appointment(dbo, username, appointmentid, post):
    """
    Creates a payment record from an appointment via the create payment dialog.
    """
    l = dbo.locale
    c = get_appointment(dbo, appointmentid)
    d = {
        "person":   str(c.OwnerID),
        "animal":   str(c.AnimalID),
        "type":     post["paymenttype"],
        "payment":  post["paymentmethod"],
        "amount":   str(c.Amount),
        "due":      post["due"],
        "received": post["received"],
        "vat":      asm3.utils.iif(c.IsVAT == 1, "on", ""),
        "vatrate":  str(c.VATRate),
        "vatamount": str(c.VATAmount),
        "comments": asm3.i18n._("Appointment {0}. {1} on {2} for {3}").format( asm3.utils.padleft(c.ID, 6), c.OWNERNAME, asm3.i18n.python2display(l, c.DATETIME), c.ANIMALNAME )
    }
    return asm3.financial.insert_donation_from_form(dbo, username, asm3.utils.PostedData(d, l))

def auto_update_statuses(dbo):
    """
    Moves on waiting list statuses where appropriate.
    1. For appointments due in the next 20 hours with a status of scheduled, moves them on to "Not Arrived"
    2. TODO: Auto cancel? Better to leave as not arrived so the difference can be seen between didn't show up and cancelled?
    """
    cutoff = asm3.i18n.add_hours(dbo.now(), 20)
    affected = dbo.execute("UPDATE clinicappointment SET Status = ? WHERE Status = ? AND DateTime >= ? AND DateTime <= ?", (NOT_ARRIVED, SCHEDULED, dbo.now(), cutoff))
    asm3.al.debug("advanced %d appointments from SCHEDULED to NOT_ARRIVED" % affected, "clinic.auto_update_statuses", dbo)
    return "OK %d" % affected

