#!/usr/bin/python

import al
import animal
import audit
import configuration
import db
import financial
import i18n
import utils

NO_MOVEMENT = 0
ADOPTION = 1
FOSTER = 2
TRANSFER = 3
ESCAPED = 4
RECLAIMED = 5
STOLEN = 6
RELEASED = 7
RETAILER = 8
RESERVATION = 9
CANCELLED_RESERVATION = 10
TRIAL_ADOPTION = 11
PERMANENT_FOSTER = 12

def get_movement_query(dbo):
    return "SELECT DISTINCT m.*, o.OwnerTitle, o.OwnerInitials, o.OwnerSurname, o.OwnerForenames, o.OwnerName, " \
        "o.OwnerAddress, o.HomeTelephone, o.WorkTelephone, o.MobileTelephone, " \
        "rs.StatusName AS ReservationStatusName, " \
        "a.ShelterCode, a.ShortCode, a.AgeGroup, a.AnimalName, a.Neutered, a.DeceasedDate, a.HasActiveReserve, " \
        "a.HasTrialAdoption, a.IsHold, a.IsQuarantine, a.HoldUntilDate, a.CrueltyCase, a.NonShelterAnimal, " \
        "a.ActiveMovementType, a.Archived, a.IsNotAvailableForAdoption, " \
        "a.CombiTestResult, a.FLVResult, a.HeartwormTestResult, " \
        "il.LocationName AS ShelterLocationName, a.ShelterLocationUnit, " \
        "r.OwnerName AS RetailerName, " \
        "ma.MediaName AS WebsiteMediaName, ma.Date AS WebsiteMediaDate, " \
        "sx.Sex, s.SpeciesName, rr.ReasonName AS ReturnedReasonName, " \
        "CASE WHEN m.MovementType = 2 AND m.IsPermanentFoster = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=12) " \
        "WHEN m.MovementType = 1 AND m.IsTrial = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=11) " \
        "WHEN m.MovementDate Is Null AND m.ReservationDate Is Not Null AND m.ReservationCancelledDate Is Not Null THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=10) " \
        "WHEN m.MovementDate Is Null AND m.ReservationDate Is Not Null THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=9) " \
        "ELSE l.MovementType END AS MovementName, " \
        "CASE WHEN m.MovementType = 2 AND m.IsPermanentFoster = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=12) " \
        "WHEN m.MovementType = 1 AND m.IsTrial = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=11) " \
        "WHEN m.MovementDate Is Null AND m.ReservationDate Is Not Null AND m.ReservationCancelledDate Is Not Null THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=10) " \
        "WHEN m.MovementDate Is Null AND m.ReservationDate Is Not Null THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=9) " \
        "ELSE l.MovementType END AS DisplayLocationName, co.OwnerName AS CurrentOwnerName " \
        "FROM adoption m " \
        "LEFT OUTER JOIN reservationstatus rs ON rs.ID = m.ReservationStatusID " \
        "LEFT OUTER JOIN lksmovementtype l ON l.ID = m.MovementType " \
        "INNER JOIN animal a ON m.AnimalID = a.ID " \
        "LEFT OUTER JOIN adoption ad ON a.ActiveMovementID = ad.ID " \
        "LEFT OUTER JOIN owner co ON co.ID = ad.OwnerID " \
        "INNER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN media ma ON ma.LinkID = a.ID AND ma.LinkTypeID = 0 AND ma.WebsitePhoto = 1 " \
        "LEFT OUTER JOIN entryreason rr ON m.ReturnedReasonID = rr.ID " \
        "INNER JOIN species s ON a.SpeciesID = s.ID " \
        "INNER JOIN lksex sx ON sx.ID = a.Sex " \
        "LEFT OUTER JOIN owner o ON m.OwnerID = o.ID " \
        "LEFT OUTER JOIN owner r ON m.RetailerID = r.ID "

def get_transport_query(dbo):
    return "SELECT DISTINCT t.*, d.OwnerName AS DriverOwnerName, p.OwnerName AS PickupOwnerName, dr.OwnerName AS DropoffOwnerName, " \
        "d.OwnerAddress AS DriverOwnerAddress, p.OwnerAddress AS PickupOwnerAddress, dr.OwnerAddress AS DropoffOwnerAddress, " \
        "d.OwnerTown AS DriverOwnerTown, p.OwnerTown AS PickupOwnerTown, dr.OwnerTown AS DropoffOwnerTown, " \
        "d.OwnerCounty AS DriverOwnerCounty, p.OwnerCounty AS PickupOwnerCounty, dr.OwnerCounty AS DropoffOwnerCounty, " \
        "d.OwnerPostcode AS DriverOwnerPostcode, p.OwnerPostcode AS PickupOwnerPostcode, dr.OwnerPostcode AS DropoffOwnerPostcode, " \
        "a.AnimalName, a.ShelterCode " \
        "FROM animaltransport t " \
        "LEFT OUTER JOIN animal a ON t.AnimalID = a.ID " \
        "LEFT OUTER JOIN owner d ON t.DriverOwnerID = d.ID " \
        "LEFT OUTER JOIN owner p ON t.PickupOwnerID = p.ID " \
        "LEFT OUTER JOIN owner dr ON t.DropoffOwnerID = dr.ID "

def get_movements(dbo, movementtype):
    """
    Gets the list of movements of a particular type 
    (unreturned or returned after today and for animals who aren't deceased)
    """
    return db.query(dbo, get_movement_query(dbo) + \
        "WHERE m.MovementType = %d AND " \
        "(m.ReturnDate Is Null OR m.ReturnDate > %s) " \
        "AND a.DeceasedDate Is Null " \
        "ORDER BY m.MovementDate DESC" % (int(movementtype), db.dd(i18n.now(dbo.timezone))))

def get_active_reservations(dbo, age = 0):
    """
    Gets the list of uncancelled reservation movements.
    age: The age of the reservation in days, or 0 for all
    """
    where = ""
    if age > 0:
        where = "AND m.ReservationDate <= %s" % db.dd(i18n.subtract_days(i18n.now(dbo.timezone), age))
    return db.query(dbo, get_movement_query(dbo) + \
        "WHERE m.ReservationDate Is Not Null AND m.MovementDate Is Null AND m.MovementType = 0 AND m.ReturnDate Is Null " \
        "AND m.ReservationCancelledDate Is Null %s ORDER BY m.ReservationDate" % where)

def get_active_transports(dbo):
    return db.query(dbo, get_transport_query(dbo) + \
        "WHERE t.Status < 10 OR DropoffDateTime > %s ORDER BY DropoffDateTime" % db.dd(i18n.now(dbo.timezone)))

def get_animal_transports(dbo, animalid):
    return db.query(dbo, get_transport_query(dbo) + \
        "WHERE t.AnimalID = %d ORDER BY DropoffDateTime" % animalid)

def get_transport_two_dates(dbo, dbstart, dbend): 
    return db.query(dbo, get_transport_query(dbo) + \
        "WHERE t.PickupDateTime >= '%s' AND t.PickupDateTime <= '%s' ORDER BY t.PickupDateTime" % (dbstart, dbend))

def get_recent_adoptions(dbo, months = 1):
    """
    Returns a list of adoptions in the last "months" months.
    """
    return db.query(dbo, get_movement_query(dbo) + \
        "WHERE m.MovementType = 1 AND m.MovementDate Is Not Null AND m.ReturnDate Is Null " \
        "AND m.MovementDate > %s " \
        "ORDER BY m.MovementDate DESC" % db.dd(i18n.subtract_days(i18n.now(dbo.timezone), months * 31)))

def get_recent_nonfosteradoption(dbo, months = 1):
    """
    Returns a list of active movements that aren't reserves,
    fosters, adoptions or transfers in the last "months" months.
    """
    return db.query(dbo, get_movement_query(dbo) + \
        "WHERE m.MovementType > 3 AND m.MovementDate Is Not Null AND m.ReturnDate Is Null " \
        "AND m.MovementDate > %s " \
        "ORDER BY m.MovementDate DESC" % db.dd(i18n.subtract_days(i18n.now(dbo.timezone), months * 31)))

def get_recent_transfers(dbo, months = 1):
    """
    Returns a list of transfers in the last "months" months.
    """
    return db.query(dbo, get_movement_query(dbo) + \
        "WHERE m.MovementType = 3 AND m.MovementDate Is Not Null AND m.ReturnDate Is Null " \
        "AND m.MovementDate > %s " \
        "ORDER BY m.MovementDate DESC" % db.dd(i18n.subtract_days(i18n.now(dbo.timezone), months * 31)))

def get_recent_unneutered_adoptions(dbo, months = 1):
    """
    Returns a list of adoptions in the last "months" months where the
    animal remains unneutered.
    """
    return db.query(dbo, get_movement_query(dbo) + \
        "WHERE m.MovementType = 1 AND m.MovementDate Is Not Null AND m.ReturnDate Is Null " \
        "AND m.MovementDate > %s AND a.Neutered = 0 " \
        "ORDER BY m.MovementDate DESC" % db.dd(i18n.subtract_days(i18n.now(dbo.timezone), months * 31)))

def get_trial_adoptions(dbo, mode = "ALL"):
    """
    Returns a list of trial adoption movements. 
    If mode is EXPIRING, shows trials that end today or before.
    If mode is ACTIVE, shows trials that end after today.
    If mode is ALL, returns all trials.
    """
    where = ""
    if mode == "ALL":
        where = ""
    elif mode == "EXPIRING":
        where = "AND m.TrialEndDate <= %s " % db.dd(i18n.now(dbo.timezone))
    elif mode == "ACTIVE":
        where = "AND m.TrialEndDate > %s " % db.dd(i18n.now(dbo.timezone))
    return db.query(dbo, get_movement_query(dbo) + \
        "WHERE m.IsTrial = 1 AND m.MovementType = 1 AND (m.ReturnDate Is Null OR m.ReturnDate > %s) %s" \
        "ORDER BY m.TrialEndDate" % (db.dd(i18n.now(dbo.timezone)), where))

def get_animal_movements(dbo, aid):
    """
    Gets the list of movements for a particular animal
    """
    return db.query(dbo, get_movement_query(dbo) + \
        "WHERE m.AnimalID = %d ORDER BY m.MovementDate DESC" % int(aid))

def get_person_movements(dbo, pid):
    """
    Gets the list of movements for a particular person
    """
    return db.query(dbo, get_movement_query(dbo) + \
        "WHERE m.OwnerID = %d ORDER BY m.MovementDate DESC" % int(pid))

def validate_movement_form_data(dbo, post):
    """
    Verifies that form data is valid for a movement
    """
    l = dbo.locale
    movementid = post.integer("movementid")
    movement = None
    if movementid != 0: movement = db.query(dbo, "SELECT * FROM adoption WHERE ID = %d" % movementid)[0]
    adoptionno = post["adoptionno"]
    movementtype = post.integer("type")
    movementdate = post.date("movementdate")
    returndate = post.date("returndate")
    reservationdate = post.date("reservationdate")
    reservationcancelled = post.date("reservationcancelled")
    personid = post.integer("person")
    animalid = post.integer("animal")
    retailerid = post.integer("retailer")
    al.debug("validating saved movement %d for animal %d" % (movementid, animalid), "movement.validate_movement_form_data", dbo)
    # If we have a date but no type, get rid of it
    if movementdate is not None and movementtype == 0:
        post.data["movementdate"] = ""
        al.debug("blank date and type", "movement.validate_movement_form_data", dbo)
    # If we've got a type, but no date, default today
    if movementtype > 0 and movementdate is None:
        movementdate = i18n.now()
        post.data["movementdate"] = i18n.python2display(l, movementdate)
        al.debug("type set and no date, defaulting today", "movement.validate_movement_form_data", dbo)
    # If we've got a reserve cancellation without a reserve, remove it
    if reservationdate is None and reservationcancelled is not None:
        post.data["reservationdate"] = ""
        al.debug("movement has no reserve or cancelled date", "movement.validate_movement_form_data", dbo)
    # Animals are always required
    if animalid == 0:
        al.debug("movement has no animal", "movement.validate_movement_form_data", dbo)
        raise utils.ASMValidationError(i18n._("Movements require an animal", l))
    # Owners are required unless type is escaped, stolen or released
    if personid == 0 and movementtype != ESCAPED and movementtype != STOLEN and movementtype != RELEASED:
        al.debug("movement has no person and is not ESCAPED|STOLEN|RELEASED|TRANSPORT", "movement.validate_movement_form_data", dbo)
        raise utils.ASMValidationError(i18n._("A person is required for this movement type.", l))
    # Is the movement number unique?
    if 0 != db.query_int(dbo, "SELECT COUNT(*) FROM adoption WHERE AdoptionNumber LIKE '%s' AND ID <> %d" % (adoptionno, movementid)):
        raise utils.ASMValidationError(i18n._("Movement numbers must be unique.", l))
    # If we're updating an existing record, we only need to continue validation
    # if one of the important fields has changed (movement date/type, return date, reservation, animal)
    if movement is not None:
        if movementtype == movement["MOVEMENTTYPE"] and movementdate == movement["MOVEMENTDATE"] and returndate == movement["RETURNDATE"] and reservationdate == movement["RESERVATIONDATE"] and animalid == movement["ANIMALID"]:
            al.debug("movement type, dates and animalid have not changed. Abandoning further validation", "movement.validate_movement_form_data", dbo)
            return
    # If the animal is held in case of reclaim, it can't be adopted
    if movementtype == ADOPTION:
        if 1 == db.query_int(dbo, "SELECT IsHold FROM animal WHERE ID = %d" % animalid):
            al.debug("movement is adoption and the animal is on hold", "movement.validate_movement_form_data", dbo)
            raise utils.ASMValidationError(i18n._("This animal is currently held and cannot be adopted.", l))
    # If it's a foster movement, make sure the owner is a fosterer
    if movementtype == FOSTER:
        if 0 == db.query_int(dbo, "SELECT IsFosterer FROM owner WHERE ID = %d" % personid):
            al.debug("movement is a foster and the person is not a fosterer.", "movement.validate_movement_form_data", dbo)
            raise utils.ASMValidationError(i18n._("This person is not flagged as a fosterer and cannot foster animals.", l))
    # If it's a retailer movement, make sure the owner is a retailer
    if movementtype == RETAILER:
        if 0 == db.query_int(dbo, "SELECT IsRetailer FROM owner WHERE ID = %d" % personid):
            al.debug("movement is a retailer and the person is not a retailer.", "movement.validate_movement_form_data", dbo)
            raise utils.ASMValidationError(i18n._("This person is not flagged as a retailer and cannot handle retailer movements.", l))
    # If a retailer is selected, make sure it's an adoption
    if retailerid != 0 and movementtype != ADOPTION:
        al.debug("movement has a retailerid set and this is not an adoption.", "movement.validate_movement_form_data", dbo)
        raise utils.ASMValidationError(i18n._("From retailer is only valid on adoption movements.", l))
    # If a retailer is selected, make sure there's been a retailer movement in this animal's history
    if retailerid != 0:
        if 0 == db.query_int(dbo, "SELECT COUNT(*) FROM adoption WHERE AnimalID = %d AND MovementType = %d" % ( animalid, RETAILER )):
            al.debug("movement has a retailerid set but has never been to a retailer.", "movement.validate_movement_form_data", dbo)
            raise utils.ASMValidationError(i18n._("This movement cannot be from a retailer when the animal has no prior retailer movements.", l))
    # You can't have a return without a movement
    if movementdate is None and returndate is not None:
        al.debug("movement is returned without a movement date.", "movement.validate_movement_form_data", dbo)
        raise utils.ASMValidationError(i18n._("You can't have a return without a movement.", l))
    # Return should be after or same day as movement
    if movementdate is not None and returndate != None and movementdate > returndate:
        al.debug("movement return date is before the movement date.", "movement.validate_movement_form_data", dbo)
        raise utils.ASMValidationError(i18n._("Return date cannot be before the movement date.", l))
    # If the option to return fosters on adoption is set, return any outstanding fosters for the animal
    if movementtype == ADOPTION and configuration.return_fosters_on_adoption(dbo):
        sql = "UPDATE adoption SET ReturnDate = %s " \
            "WHERE ReturnDate Is Null AND MovementType = 2 " \
            "AND AnimalID = %d AND ID <> %d" % ( db.dd(i18n.now(dbo.timezone)), animalid, int(movementid) )
        changed = db.execute(dbo, sql)
        al.debug("movement is an adoption, returning outstanding fosters (%d)." % changed, "movement.validate_movement_form_data", dbo)
    # Can't have multiple open movements
    if movementdate is not None:
        existingopen = db.query_int(dbo, "SELECT COUNT(*) FROM adoption WHERE MovementDate Is Not Null AND " \
            "ReturnDate Is Null AND AnimalID = %d AND ID <> %d" % (animalid, movementid))
        if existingopen > 0:
            al.debug("movement is open and animal already has another open movement.", "movement.validate_movement_form_data", dbo)
            raise utils.ASMValidationError(i18n._("An animal cannot have multiple open movements.", l))
    # If we have a movement and return, is there another movement with a 
    # movementdate between the movement and return date on this one?
    if movementdate is not None and returndate != None:
        clash = db.query_int(dbo, "SELECT COUNT(*) FROM adoption WHERE " \
        "AnimalID = %d AND ID <> %d AND ((ReturnDate > %s AND ReturnDate < %s) " \
        "OR (MovementDate < %s AND MovementDate > %s))" % ( animalid, movementid, 
        db.dd(movementdate), db.dd(returndate), db.dd(returndate), db.dd(movementdate) ))
        if clash > 0:
            al.debug("movement dates overlap an existing movement.", "movement.validate_movement_form_data", dbo)
            raise utils.ASMValidationError(i18n._("Movement dates clash with an existing movement.", l))
    # Does this movement date fall within the date range of an already
    # returned movement for the same animal?
    if movementdate is not None and returndate is None:
        clash = db.query_int(dbo, "SELECT COUNT(*) FROM adoption WHERE AnimalID = %d AND ID <> %d AND " \
        "MovementDate Is Not Null AND ReturnDate Is Not Null AND " \
        "%s > MovementDate AND %s < ReturnDate" % ( animalid, movementid, db.dd(movementdate), db.dd(movementdate)))
        if clash > 0:
            al.debug("movement dates overlap an existing movement.", "movement.validate_movement_form_data", dbo)
            raise utils.ASMValidationError(i18n._("Movement dates clash with an existing movement.", l))
    # If there's a cancelled reservation, make sure it's after the reserve date
    if reservationdate is not None and reservationcancelled != None and reservationcancelled < reservationdate:
        al.debug("reserve date is after cancelled date.", "movement.validate_movement_form_data", dbo)
        raise utils.ASMValidationError(i18n._("Reservation date cannot be after cancellation date.", l))
    # If this is a new reservation, make sure there's no open movement (fosters do not count)
    if movementid == 0 and movementtype == 0 and movementdate is None and reservationdate is not None:
        om = db.query_int(dbo, "SELECT COUNT(*) FROM adoption WHERE AnimalID = %d AND " \
            "MovementDate Is Not Null AND ReturnDate Is Null AND MovementType <> 2" % animalid)
        if om > 0:
            al.debug("movement is a reservation but animal has active movement.", "movement.validate_movement_form_data", dbo)
            raise utils.ASMValidationError(i18n._("Can't reserve an animal that has an active movement.", l))
    # Make sure the adoption number is unique
    an = db.query_int(dbo, "SELECT COUNT(*) FROM adoption WHERE ID <> %d AND " \
        "AdoptionNumber LIKE %s" % ( movementid, post.db_string("adoptionno")))
    if an > 0:
        al.debug("movement number is not unique.", "movement.validate_movement_form_data", dbo)
        raise utils.ASMValidationError(i18n._("The movement number '{0}' is not unique.", l).format(post["adoptionno"]))
    # If this is an adoption and the owner had some criteria, expire them
    if movementtype == ADOPTION and personid > 0:
        sql = "UPDATE owner SET MatchActive = 0, MatchExpires = %s WHERE ID = %d" % ( db.dd(i18n.now(dbo.timezone)), int(personid) )
        changed = db.execute(dbo, sql)
        al.debug("movement is an adoption, expiring person criteria (%d)." % changed, "movement.validate_movement_form_data", dbo)
    # If the option to cancel reserves on adoption is set, cancel any outstanding reserves for the animal
    if movementtype == ADOPTION and configuration.cancel_reserves_on_adoption(dbo):
        sql = "UPDATE adoption SET ReservationCancelledDate = %s " \
            "WHERE ReservationCancelledDate Is Null AND MovementDate Is Null " \
            "AND AnimalID = %d AND ID <> %d" % ( db.dd(i18n.now(dbo.timezone)), animalid, int(movementid) )
        changed = db.execute(dbo, sql)
        al.debug("movement is an adoption, cancelling outstanding reserves (%d)." % changed, "movement.validate_movement_form_data", dbo)

def insert_movement_from_form(dbo, username, post):
    """
    Creates a movement record from posted form data 
    """
    movementid = db.get_id(dbo, "adoption")
    adoptionno = post["adoptionno"]
    animalid = post.integer("animal")
    if adoptionno == "": 
        # No adoption number was supplied, generate a
        # unique number from the movementid
        idx = movementid
        while True:
            adoptionno = utils.padleft(idx, 6)
            post.data["adoptionno"] = adoptionno
            if 0 == db.query_int(dbo, "SELECT COUNT(*) FROM adoption WHERE AdoptionNumber LIKE '%s'" % adoptionno):
                break
            else:
                idx += 1

    validate_movement_form_data(dbo, post)
    sql = db.make_insert_user_sql(dbo, "adoption", username, ( 
        ( "ID", db.di(movementid)),
        ( "AdoptionNumber", db.ds(adoptionno)),
        ( "OwnerID", post.db_integer("person")),
        ( "RetailerID", post.db_integer("retailer")),
        ( "AnimalID", post.db_integer("animal")),
        ( "OriginalRetailerMovementID", post.db_integer("originalretailermovement")),
        ( "MovementDate", post.db_date("movementdate")),
        ( "MovementType", post.db_integer("type")),
        ( "ReturnDate", post.db_date("returndate")),
        ( "ReturnedReasonID", post.db_integer("returncategory")),
        ( "Donation", post.db_integer("donation")),
        ( "InsuranceNumber", post.db_string("insurance")),
        ( "ReasonForReturn", post.db_string("reason")),
        ( "ReservationDate", post.db_date("reservationdate")),
        ( "ReservationCancelledDate", post.db_date("reservationcancelled")),
        ( "ReservationStatusID", post.db_integer("reservationstatus")),
        ( "IsTrial", post.db_boolean("trial")),
        ( "IsPermanentFoster", post.db_boolean("permanentfoster")),
        ( "TrialEndDate", post.db_date("trialenddate")),
        ( "Comments", post.db_string("comments"))
        ))
    db.execute(dbo, sql)
    audit.create(dbo, username, "adoption", str(movementid))
    animal.update_animal_status(dbo, animalid)
    animal.update_variable_animal_data(dbo, animalid)
    update_movement_donation(dbo, movementid)
    return movementid

def update_movement_from_form(dbo, username, post):
    """
    Updates a movement record from posted form data
    """
    validate_movement_form_data(dbo, post)
    movementid = post.integer("movementid")
    sql = db.make_update_user_sql(dbo, "adoption", username, "ID=%d" % movementid, ( 
        ( "AdoptionNumber", post.db_string("adoptionno")),
        ( "OwnerID", post.db_integer("person")),
        ( "RetailerID", post.db_integer("retailer")),
        ( "AnimalID", post.db_integer("animal")),
        ( "OriginalRetailerMovementID", post.db_integer("originalretailermovement")),
        ( "MovementDate", post.db_date("movementdate")),
        ( "MovementType", post.db_integer("type")),
        ( "ReturnDate", post.db_date("returndate")),
        ( "ReturnedReasonID", post.db_integer("returncategory")),
        ( "Donation", post.db_integer("donation")),
        ( "InsuranceNumber", post.db_string("insurance")),
        ( "ReasonForReturn", post.db_string("reason")),
        ( "ReservationDate", post.db_date("reservationdate")),
        ( "ReservationCancelledDate", post.db_date("reservationcancelled")),
        ( "ReservationStatusID", post.db_integer("reservationstatus")),
        ( "IsTrial", post.db_boolean("trial")),
        ( "IsPermanentFoster", post.db_boolean("permanentfoster")),
        ( "TrialEndDate", post.db_date("trialenddate")),
        ( "Comments", post.db_string("comments"))
        ))
    preaudit = db.query(dbo, "SELECT * FROM adoption WHERE ID = %d" % movementid)
    db.execute(dbo, sql)
    postaudit = db.query(dbo, "SELECT * FROM adoption WHERE ID = %d" % movementid)
    audit.edit(dbo, username, "adoption", audit.map_diff(preaudit, postaudit))
    animal.update_animal_status(dbo, post.integer("animal"))
    animal.update_variable_animal_data(dbo, post.integer("animal"))
    update_movement_donation(dbo, movementid)

def delete_movement(dbo, username, mid):
    """
    Deletes a movement record
    """
    animalid = db.query_int(dbo, "SELECT AnimalID FROM adoption WHERE ID = %d" % int(mid))
    if animalid == 0:
        raise utils.ASMError("Trying to delete a movement that does not exist")
    db.execute(dbo, "UPDATE ownerdonation SET MovementID = 0 WHERE MovementID = %d" % int(mid))
    audit.delete(dbo, username, "adoption", str(db.query(dbo, "SELECT * FROM adoption WHERE ID=%d" % int(mid))))
    db.execute(dbo, "DELETE FROM adoption WHERE ID = %d" % int(mid))
    animal.update_animal_status(dbo, animalid)
    animal.update_variable_animal_data(dbo, animalid)

def return_movement(dbo, movementid, animalid, returndate):
    """
    Returns a movement with the date given
    """
    db.execute(dbo, "UPDATE adoption SET ReturnDate = %s WHERE ID = %d" % (db.dd(returndate), int(movementid)))
    animal.update_animal_status(dbo, int(animalid))

def insert_adoption_from_form(dbo, username, post, creating = []):
    """
    Inserts a movement from the workflow adopt an animal screen.
    Returns the new movement id
    creating is an ongoing list of animals we're already going to
    create adoptions for. It prevents a never ending recursive loop
    of animal1 being bonded to animal2 that's bonded to animal1, etc.
    """
    l = dbo.locale
    # Validate that we have a movement date before doing anthing
    if None == post.date("movementdate"):
        raise utils.ASMValidationError(i18n._("Adoption movements must have a valid adoption date.", l))
    # Get the animal record for this adoption
    a = animal.get_animal(dbo, post.integer("animal"))
    if a is None:
        raise utils.ASMValidationError("Adoption POST has an invalid animal ID: %d" % post.integer("animal"))
    al.debug("Creating adoption for %d (%s - %s)" % (a["ID"], a["SHELTERCODE"], a["ANIMALNAME"]), "movement.insert_adoption_from_form", dbo)
    creating.append(a["ID"])
    # If the animal is bonded to other animals, we call this function
    # again with a copy of the data and the bonded animal substituted
    # so we can create their adoption records too.
    if a["BONDEDANIMALID"] is not None and a["BONDEDANIMALID"] != 0 and a["BONDEDANIMALID"] not in creating:
        al.debug("Found bond to animal %d, creating adoption..." % a["BONDEDANIMALID"], "movement.insert_adoption_from_form", dbo)
        newdata = dict(post.data)
        newdata["animal"] = str(a["BONDEDANIMALID"])
        insert_adoption_from_form(dbo, username, utils.PostedData(newdata, dbo.locale), creating)
    if a["BONDEDANIMAL2ID"] is not None and a["BONDEDANIMAL2ID"] != 0 and a["BONDEDANIMAL2ID"] not in creating:
        al.debug("Found bond to animal %d, creating adoption..." % a["BONDEDANIMAL2ID"], "movement.insert_adoption_from_form", dbo)
        newdata = dict(post.data)
        newdata["animal"] = str(a["BONDEDANIMAL2ID"])
        insert_adoption_from_form(dbo, username, utils.PostedData(newdata, dbo.locale), creating)
    cancel_reserves = configuration.cancel_reserves_on_adoption(dbo)
    # Prepare a dictionary of data for the movement table via insert_movement_from_form
    move_dict = {
        "person"                : post["person"],
        "animal"                : post["animal"],
        "adoptionno"            : post["movementnumber"],
        "movementdate"          : post["movementdate"],
        "type"                  : str(ADOPTION),
        "donation"              : post["amount"],
        "insurance"             : post["insurance"],
        "returncategory"        : configuration.default_return_reason(dbo),
        "trial"                 : post["trial"],
        "trialenddate"          : post["trialenddate"]
    }
    # Is this animal currently on foster? If so, return the foster
    fm = get_animal_movements(dbo, post.integer("animal"))
    for m in fm:
        if m["MOVEMENTTYPE"] == FOSTER and m["RETURNDATE"] is None:
            return_movement(dbo, m["ID"], post.integer("animal"), post.date("movementdate"))
    # Is this animal current at a retailer? If so, return it from the
    # retailer and set the originalretailermovement and retailerid fields
    # on our new adoption movement so it can be linked back
    for m in fm:
        if m["MOVEMENTTYPE"] == RETAILER and m["RETURNDATE"] is None:
            return_movement(dbo, m["ID"], post.integer("animal"), post.date("movementdate"))
            move_dict["originalretailermovement"] = str(m["ID"])
            move_dict["retailer"] = str(m["OWNERID"])
    # Did we say we'd like to flag the owner as homechecked?
    if post.boolean("homechecked") == 1:
        db.execute(dbo, "UPDATE owner SET IDCheck = 1, DateLastHomeChecked = %s WHERE ID = %d" % \
            ( db.dd(i18n.now(dbo.timezone)), post.integer("person")))
    # If the animal was flagged as not available for adoption, then it
    # shouldn't be since we've just adopted it.
    db.execute(dbo, "UPDATE animal SET IsNotAvailableForAdoption = 0 WHERE ID = %s" % post["animal"])
    # Is the animal reserved to the person adopting? 
    movementid = 0
    for m in fm:
        if m["MOVEMENTTYPE"] == NO_MOVEMENT and m["RESERVATIONDATE"] is not None \
            and m["RESERVATIONCANCELLEDDATE"] is None and m["ANIMALID"] == post.integer("animal") \
            and m["OWNERID"] == post.integer("person"):
            # yes - update the existing movement
            movementid = m["ID"]
            move_dict["movementid"] = str(movementid)
            move_dict["adoptionno"] = utils.padleft(movementid, 6)
            move_dict["reservationdate"] = str(i18n.python2display(l, m["RESERVATIONDATE"]))
            move_dict["comments"] = utils.nulltostr(m["COMMENTS"])
            break
        elif cancel_reserves and m["MOVEMENTTYPE"] == NO_MOVEMENT and m["RESERVATIONDATE"] is not None \
            and m["RESERVATIONCANCELLEDDATE"] is None:
            # no, but it's reserved to someone else and we're cancelling
            # reserves on adoption
            db.execute(dbo, "UPDATE adoption SET ReservationCancelledDate = %s WHERE ID = %d" % \
                ( post.db_date("movementdate"), m["ID"] ))
    if movementid != 0:
        update_movement_from_form(dbo, username, utils.PostedData(move_dict, l))
    else:
        movementid = insert_movement_from_form(dbo, username, utils.PostedData(move_dict, l))
    # Create the donation if there is one
    donation_amount = post.integer("amount")
    if donation_amount > 0:
        due = ""
        received = post["movementdate"]
        if configuration.movement_donations_default_due(dbo):
            due = post["movementdate"]
            received = ""
        don_dict = {
            "person"                : post["person"],
            "animal"                : post["animal"],
            "movement"              : str(movementid),
            "type"                  : post["donationtype"],
            "payment"               : post["payment"],
            "destaccount"           : post["destaccount"],
            "frequency"             : "0",
            "amount"                : post["amount"],
            "due"                   : due,
            "received"              : received,
            "giftaid"               : post["giftaid"]
        }
        financial.insert_donation_from_form(dbo, username, utils.PostedData(don_dict, l))
    # And a second donation if there is one
    donation_amount = post.integer("amount2")
    if donation_amount > 0:
        due = ""
        received = post["movementdate"]
        if configuration.movement_donations_default_due(dbo):
            due = post["movementdate"]
            received = ""
        don_dict = {
            "person"                : post["person"],
            "animal"                : post["animal"],
            "movement"              : str(movementid),
            "type"                  : post["donationtype2"],
            "payment"               : post["payment2"],
            "destaccount"           : post["destaccount2"],
            "frequency"             : "0",
            "amount"                : post["amount2"],
            "due"                   : due,
            "received"              : received,
            "giftaid"               : post["giftaid"]
        }
        financial.insert_donation_from_form(dbo, username, utils.PostedData(don_dict, l))
    # Then any boarding cost record
    cost_amount = post.integer("costamount")
    cost_type = post["costtype"]
    cost_create = post.integer("costcreate")
    if cost_amount > 0 and cost_type != "" and cost_create == 1:
        boc_dict = {
            "animalid"          : post["animal"],
            "type"              : cost_type,
            "costdate"          : post["movementdate"],
            "costpaid"          : post["movementdate"],
            "cost"              : post["costamount"]
        }
        animal.insert_cost_from_form(dbo, username, utils.PostedData(boc_dict, l))
    return movementid

def insert_foster_from_form(dbo, username, post):
    """
    Inserts a movement from the workflow foster an animal screen.
    Returns the new movement id
    """
    # Validate that we have a movement date before doing anthing
    l = dbo.locale
    if None == post.date("fosterdate"):
        raise utils.ASMValidationError(i18n._("Foster movements must have a valid foster date.", l))

    # Is this animal already on foster? If so, return that foster first
    fm = get_animal_movements(dbo, post.integer("animal"))
    for m in fm:
        if m["MOVEMENTTYPE"] == FOSTER and m["RETURNDATE"] is None:
            return_movement(dbo, m["ID"], post.integer("animal"), post.date("fosterdate"))
    # Create the foster movement
    move_dict = {
        "person"                : post["person"],
        "animal"                : post["animal"],
        "movementdate"          : post["fosterdate"],
        "permanentfoster"       : post["permanentfoster"],
        "adoptionno"            : post["movementnumber"],
        "returndate"            : post["returndate"],
        "type"                  : str(FOSTER),
        "donation"              : post["amount"],
        "returncategory"        : configuration.default_return_reason(dbo)
    }
    movementid = insert_movement_from_form(dbo, username, utils.PostedData(move_dict, l))
    return movementid

def insert_reclaim_from_form(dbo, username, post):
    """
    Inserts a movement from the workflow adopt an animal screen.
    Returns the new movement id
    """
    l = dbo.locale
    # Validate that we have a movement date before doing anthing
    if None == post.date("movementdate"):
        raise utils.ASMValidationError(i18n._("Reclaim movements must have a valid reclaim date.", l))
    # Get the animal record for this reclaim
    a = animal.get_animal(dbo, post.integer("animal"))
    if a is None:
        raise utils.ASMValidationError("Reclaim POST has an invalid animal ID: %d" % post.integer("animal"))
    al.debug("Creating reclaim for %d (%s - %s)" % (a["ID"], a["SHELTERCODE"], a["ANIMALNAME"]), "movement.insert_reclaim_from_form", dbo)
    # Prepare a dictionary of data for the movement table via insert_movement_from_form
    move_dict = {
        "person"                : post["person"],
        "animal"                : post["animal"],
        "adoptionno"            : post["movementnumber"],
        "movementdate"          : post["movementdate"],
        "type"                  : str(RECLAIMED),
        "donation"              : post["amount"],
        "returncategory"        : configuration.default_return_reason(dbo)
    }
    # Is this animal currently on foster? If so, return the foster
    fm = get_animal_movements(dbo, post.integer("animal"))
    for m in fm:
        if m["MOVEMENTTYPE"] == FOSTER and m["RETURNDATE"] is None:
            return_movement(dbo, m["ID"], post.integer("animal"), post.date("movementdate"))
    # Is this animal current at a retailer? If so, return it from the
    # retailer and set the originalretailermovement and retailerid fields
    # on our new adoption movement so it can be linked back
    for m in fm:
        if m["MOVEMENTTYPE"] == RETAILER and m["RETURNDATE"] is None:
            return_movement(dbo, m["ID"], post.integer("animal"), post.date("movementdate"))
            move_dict["originalretailermovement"] = str(m["ID"])
            move_dict["retailer"] = str(m["OWNERID"])
    # If the animal was flagged as not available for adoption, then it
    # shouldn't be since we've just reclaimed it.
    db.execute(dbo, "UPDATE animal SET IsNotAvailableForAdoption = 0 WHERE ID = %s" % post["animal"])
    # Is the animal reserved? Should clear it if so
    cancel_reserves = configuration.cancel_reserves_on_adoption(dbo)
    for m in fm:
        if cancel_reserves and m["MOVEMENTTYPE"] == NO_MOVEMENT and m["RESERVATIONDATE"] is not None \
            and m["RESERVATIONCANCELLEDDATE"] is None:
            db.execute(dbo, "UPDATE adoption SET ReservationCancelledDate = %s WHERE ID = %d" % \
                ( post.db_date("movementdate"), m["ID"] ))
    movementid = insert_movement_from_form(dbo, username, utils.PostedData(move_dict, l))
    # Create the donation if there is one
    donation_amount = post.integer("amount")
    if donation_amount > 0:
        due = ""
        received = post["movementdate"]
        if configuration.movement_donations_default_due(dbo):
            due = post["movementdate"]
            received = ""
        don_dict = {
            "person"                : post["person"],
            "animal"                : post["animal"],
            "movement"              : str(movementid),
            "type"                  : post["donationtype"],
            "payment"               : post["payment"],
            "destaccount"           : post["destaccount"],
            "frequency"             : "0",
            "amount"                : post["amount"],
            "due"                   : due,
            "received"              : received,
            "giftaid"               : post["giftaid"]
        }
        financial.insert_donation_from_form(dbo, username, utils.PostedData(don_dict, l))
    # Then any boarding cost record
    cost_amount = post.integer("costamount")
    cost_type = post["costtype"]
    cost_create = post.integer("costcreate")
    if cost_amount > 0 and cost_type != "" and cost_create == 1:
        boc_dict = {
            "animalid"          : post["animal"],
            "type"              : cost_type,
            "costdate"          : post["movementdate"],
            "costpaid"          : post["movementdate"],
            "cost"              : post["costamount"]
        }
        animal.insert_cost_from_form(dbo, username, utils.PostedData(boc_dict, l))
    return movementid

def insert_transfer_from_form(dbo, username, post):
    """
    Inserts a movement from the workflow transfer an animal screen.
    Returns the new movement id
    """
    # Validate that we have a movement date before doing anthing
    l = dbo.locale
    if None == post.date("transferdate"):
        raise utils.ASMValidationError(i18n._("Transfers must have a valid transfer date.", l))

    # Is this animal already on foster? If so, return that foster first
    fm = get_animal_movements(dbo, post.integer("animal"))
    for m in fm:
        if m["MOVEMENTTYPE"] == FOSTER and m["RETURNDATE"] is None:
            return_movement(dbo, m["ID"], post.integer("animal"), post.date("transferdate"))
    # Create the transfer movement
    move_dict = {
        "person"                : post["person"],
        "animal"                : post["animal"],
        "adoptionno"            : post["movementnumber"],
        "movementdate"          : post["transferdate"],
        "type"                  : str(TRANSFER),
        "donation"              : post["amount"],
        "returncategory"        : configuration.default_return_reason(dbo)
    }
    movementid = insert_movement_from_form(dbo, username, utils.PostedData(move_dict, l))
    return movementid

def insert_reserve_for_animal_name(dbo, username, personid, animalname):
    """
    Creates a reservation for the animal with animalname to personid.
    animalname can either be just the name of a shelter animal, or it
    can be in the form name::code. If a code is present, that will be
    used to locate the animal.
    """
    l = dbo.locale
    if animalname.find("::") != -1:
        animalcode = animalname.split("::")[1]
        aid = db.query_int(dbo, "SELECT ID FROM animal WHERE ShelterCode = %s ORDER BY ID DESC" % db.ds(animalcode))
    else:
        aid = db.query_int(dbo, "SELECT ID FROM animal WHERE LOWER(AnimalName) LIKE '%s' ORDER BY ID DESC" % animalname.lower())
    # Bail out if we couldn't find a matching animal
    if aid == 0: return
    move_dict = {
        "person"                : str(personid),
        "animal"                : str(aid),
        "reservationdate"       : i18n.python2display(l, i18n.now(dbo.timezone)),
        "reservationstatus"     : configuration.default_reservation_status(dbo),
        "movementdate"          : "",
        "type"                  : str(NO_MOVEMENT),
        "returncategory"        : configuration.default_return_reason(dbo)
    }
    return insert_movement_from_form(dbo, username, utils.PostedData(move_dict, l))

def insert_reserve_from_form(dbo, username, post):
    """
    Inserts a movement from the workflow reserve an animal screen.
    Returns the new movement id
    """
    # Validate that we have a date before doing anthing
    l = dbo.locale
    if None == post.date("reservationdate"):
        raise utils.ASMValidationError(i18n._("Reservations must have a valid reservation date.", l))

    # Do the movement itself first
    move_dict = {
        "person"                : post["person"],
        "animal"                : post["animal"],
        "reservationdate"       : post["reservationdate"],
        "reservationstatus"     : post["reservationstatus"],
        "adoptionno"            : post["movementnumber"],
        "movementdate"          : "",
        "type"                  : str(NO_MOVEMENT),
        "donation"              : post["amount"],
        "returncategory"        : configuration.default_return_reason(dbo)
    }
    movementid = insert_movement_from_form(dbo, username, utils.PostedData(move_dict, l))
    # Then the donation if we have one
    donation_amount = post.integer("amount")
    if donation_amount > 0:
        due = ""
        received = post["reservationdate"]
        if configuration.movement_donations_default_due(dbo):
            due = post["reservationdate"]
            received = ""
        don_dict = {
            "person"                : post["person"],
            "animal"                : post["animal"],
            "movement"              : str(movementid),
            "type"                  : post["donationtype"],
            "payment"               : post["payment"],
            "destaccount"           : post["destaccount"],
            "frequency"             : "0",
            "amount"                : post["amount"],
            "due"                   : due,
            "received"              : received,
            "giftaid"               : post["giftaid"]
        }
        financial.insert_donation_from_form(dbo, username, utils.PostedData(don_dict, l))
    # And a second donation if there is one
    donation_amount = post.integer("amount2")
    if donation_amount > 0:
        due = ""
        received = post["movementdate"]
        if configuration.movement_donations_default_due(dbo):
            due = post["movementdate"]
            received = ""
        don_dict = {
            "person"                : post["person"],
            "animal"                : post["animal"],
            "movement"              : str(movementid),
            "type"                  : post["donationtype2"],
            "payment"               : post["payment2"],
            "destaccount"           : post["destaccount2"],
            "frequency"             : "0",
            "amount"                : post["amount2"],
            "due"                   : due,
            "received"              : received,
            "giftaid"               : post["giftaid"]
        }
        financial.insert_donation_from_form(dbo, username, utils.PostedData(don_dict, l))
    return movementid

def insert_retailer_from_form(dbo, username, post):
    """
    Inserts a retailer from the workflow move to retailer screen.
    Returns the new movement id
    """
    # Validate that we have a movement date before doing anthing
    l = dbo.locale
    if None == post.date("retailerdate"):
        raise utils.ASMValidationError(i18n._("Retailer movements must have a valid movement date.", l))

    # Is this animal already at a foster? If so, return that foster first
    fm = get_animal_movements(dbo, post.integer("animal"))
    for m in fm:
        if m["MOVEMENTTYPE"] == FOSTER and m["RETURNDATE"] is None:
            return_movement(dbo, m["ID"], post.integer("animal"), post.date("retailerdate"))
    # Create the retailer movement
    move_dict = {
        "person"                : post["person"],
        "animal"                : post["animal"],
        "movementdate"          : post["retailerdate"],
        "adoptionno"            : post["movementnumber"],
        "type"                  : str(RETAILER),
        "donation"              : post["amount"],
        "returncategory"        : configuration.default_return_reason(dbo)
    }
    movementid = insert_movement_from_form(dbo, username, utils.PostedData(move_dict, l))
    return movementid

def update_movement_donation(dbo, movementid):
    """
    Goes through all donations attached to a particular movement and updates
    the denormalised movement total.
    """
    if utils.cint(movementid) == 0: return
    db.execute(dbo, "UPDATE adoption SET Donation = " \
        "(SELECT SUM(Donation) FROM ownerdonation WHERE MovementID = %d) WHERE ID = %d" % \
        (int(movementid), int(movementid)))

def insert_transport_from_form(dbo, username, post):
    """
    Creates a transport record from posted form data 
    """
    l = dbo.locale
    if post.integer("animal") == 0:
        raise utils.ASMValidationError(i18n._("Transport requires an animal", l))

    transportid = db.get_id(dbo, "animaltransport")
    sql = db.make_insert_user_sql(dbo, "animaltransport", username, ( 
        ( "ID", db.di(transportid)),
        ( "AnimalID", post.db_integer("animal")),
        ( "DriverOwnerID", post.db_integer("driver")),
        ( "PickupOwnerID", post.db_integer("pickup")),
        ( "DropoffOwnerID", post.db_integer("dropoff")),
        ( "PickupDateTime", post.db_datetime("pickupdate", "pickuptime")),
        ( "DropoffDateTime", post.db_datetime("dropoffdate", "dropofftime")),
        ( "Status", post.db_integer("status")),
        ( "Miles", post.db_integer("miles")),
        ( "Cost", post.db_integer("cost")),
        ( "CostPaidDate", post.db_date("costpaid")),
        ( "Comments", post.db_string("comments"))
        ))
    db.execute(dbo, sql)
    audit.create(dbo, username, "animaltransport", str(transportid))
    return transportid

def update_transport_from_form(dbo, username, post):
    """
    Updates a movement record from posted form data
    """
    transportid = post.integer("transportid")
    sql = db.make_update_user_sql(dbo, "animaltransport", username, "ID=%d" % transportid, ( 
        ( "AnimalID", post.db_integer("animal")),
        ( "DriverOwnerID", post.db_integer("driver")),
        ( "PickupOwnerID", post.db_integer("pickup")),
        ( "DropoffOwnerID", post.db_integer("dropoff")),
        ( "PickupDateTime", post.db_datetime("pickupdate", "pickuptime")),
        ( "DropoffDateTime", post.db_datetime("dropoffdate", "dropofftime")),
        ( "Status", post.db_integer("status")),
        ( "Miles", post.db_integer("miles")),
        ( "Cost", post.db_integer("cost")),
        ( "CostPaidDate", post.db_date("costpaid")),
        ( "Comments", post.db_string("comments"))
        ))
    preaudit = db.query(dbo, "SELECT * FROM animaltransport WHERE ID = %d" % transportid)
    db.execute(dbo, sql)
    postaudit = db.query(dbo, "SELECT * FROM animaltransport WHERE ID = %d" % transportid)
    audit.edit(dbo, username, "animaltransport", audit.map_diff(preaudit, postaudit))

def delete_transport(dbo, username, tid):
    """
    Deletes a transport record
    """
    animalid = db.query_int(dbo, "SELECT AnimalID FROM animaltransport WHERE ID = %d" % int(tid))
    if animalid == 0:
        raise utils.ASMError("Trying to delete a transport that does not exist")
    audit.delete(dbo, username, "animaltransport", str(db.query(dbo, "SELECT * FROM animaltransport WHERE ID=%d" % int(tid))))
    db.execute(dbo, "DELETE FROM animaltransport WHERE ID = %d" % int(tid))

def generate_insurance_number(dbo):
    """
    Returns the next insurance number in the sequence
    """
    ins = configuration.auto_insurance_next(dbo)
    nextins = ins + 1
    configuration.auto_insurance_next(dbo, nextins)
    return ins

def auto_cancel_reservations(dbo):
    """
    Automatically cancels reservations after the daily amount set
    """
    cancelafter = configuration.auto_cancel_reserves_days(dbo)
    if cancelafter <= 0:
        al.debug("auto reserve cancel is off.", "movement.auto_cancel_reservations")
        return
    cancelcutoff = i18n.subtract_days(i18n.now(dbo.timezone), cancelafter)
    al.debug("cutoff date: reservations < %s" % db.dd(cancelcutoff), "movement.auto_cancel_reservations")
    sql = "UPDATE adoption SET ReservationCancelledDate = %s, LastChangedBy = 'system' " \
        "WHERE MovementDate Is Null AND ReservationCancelledDate Is Null AND " \
        "MovementType = 0 AND ReservationDate < %s" % ( db.dd(i18n.now(dbo.timezone)), db.dd(cancelcutoff))
    count = db.execute(dbo, sql)
    al.debug("cancelled %d reservations older than %d days" % (count, int(cancelafter)), "movement.auto_cancel_reservations", dbo)

    
