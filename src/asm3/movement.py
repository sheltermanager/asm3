
import asm3.al
import asm3.animal
import asm3.audit
import asm3.cachedisk
import asm3.configuration
import asm3.financial
import asm3.log
import asm3.medical
import asm3.i18n
import asm3.person
import asm3.utils
import asm3.wordprocessor

from asm3.sitedefs import SERVICE_URL
from asm3.typehints import datetime, Database, List, PostedData, ResultRow, Results

# Valid values for MovementType (0-8 only)
NO_MOVEMENT = 0
ADOPTION = 1
FOSTER = 2
TRANSFER = 3
ESCAPED = 4
RECLAIMED = 5
STOLEN = 6
RELEASED = 7
RETAILER = 8
# The values below only exist in lksmovementtype so that reports and queries can 
# retrieve the translated text for valid movements that have modifiers.
RESERVATION_TEXT = 9            # NO_MOVEMENT + ReservationDate set
CANCELLED_RESERVATION_TEXT = 10 # NO_MOVEMENT + ReservationCancelledDate set
TRIAL_ADOPTION_TEXT = 11        # ADOPTION + IsTrial=1
PERMANENT_FOSTER_TEXT = 12      # FOSTER + IsPermanentFoster=1
TNR_TEXT = 13                   # RELEASED + animal.SpeciesID IN (1,2) (Dog,Cat)

def bulk_update_movement_statuses(dbo: Database, username: str, movementids: list, movementstatus: int):
    for mid in movementids:
        movementdata = asm3.movement.get_movement(dbo, mid)
        animalid = movementdata["ANIMALID"]
        ownerid = movementdata["OWNERID"]
        dbo.update("adoption", mid, { "ReservationStatusID": movementstatus, "AnimalID": animalid, "OwnerID": ownerid }, username)
    return len(movementids)

def get_movement_query(dbo: Database) -> str:
    return "SELECT m.*, o.OwnerTitle, o.OwnerInitials, o.OwnerSurname, o.OwnerForenames, o.OwnerName, " \
        "o.OwnerAddress, o.OwnerTown, o.OwnerCounty, o.OwnerPostcode, " \
        "o.HomeTelephone, o.WorkTelephone, o.MobileTelephone, o.EmailAddress, o.SiteID AS OwnerSiteID, " \
        "o.AdditionalFlags AS OwnerFlags, " \
        "rs.StatusName AS ReservationStatusName, " \
        f"{asm3.animal.get_animal_emblem_query(dbo)}, " \
        "sz.Size, er.ReasonName AS EntryReasonName, et.EntryTypeName, " \
        "r.OwnerName AS RetailerName, " \
        "ma.MediaName AS WebsiteMediaName, ma.Date AS WebsiteMediaDate, " \
        "a.Sex, bc.BaseColour, rr.ReasonName AS ReturnedReasonName, " \
        "CASE WHEN m.MovementType = 0 AND m.MovementDate Is Null THEN " \
        "m.ReservationDate ELSE m.MovementDate END AS ActiveDate, " \
        "CASE WHEN m.EventID > 0 THEN 1 ELSE 0 END AS IsEventLinked, " \
        "CASE " \
        "WHEN m.MovementType = 7 AND a.SpeciesID IN (1,2) THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=13) " \
        "WHEN m.MovementType = 2 AND m.IsPermanentFoster = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=12) " \
        "WHEN m.MovementType = 1 AND m.IsTrial = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=11) " \
        "WHEN m.MovementDate Is Null AND m.ReservationDate Is Not Null AND m.ReservationCancelledDate Is Not Null AND m.ReservationCancelledDate < %(now)s THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=10) " \
        "WHEN m.MovementDate Is Null AND m.ReservationDate Is Not Null THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=9) " \
        "ELSE l.MovementType END AS MovementName, " \
        "CASE " \
        "WHEN m.MovementType = 7 AND a.SpeciesID IN (1,2) THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=13) " \
        "WHEN m.MovementType = 2 AND m.IsPermanentFoster = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=12) " \
        "WHEN m.MovementType = 1 AND m.IsTrial = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=11) " \
        "WHEN m.MovementDate Is Null AND m.ReservationDate Is Not Null AND m.ReservationCancelledDate Is Not Null AND m.ReservationCancelledDate < %(now)s THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=10) " \
        "WHEN m.MovementDate Is Null AND m.ReservationDate Is Not Null THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=9) " \
        "ELSE l.MovementType END AS DisplayLocationName, " \
        "co.OwnerName AS CurrentOwnerName, " \
        "rb.OwnerName AS ReturnedByOwnerName, rb.OwnerForeNames AS ReturnedByOwnerForenames, " \
        "rb.OwnerSurname AS ReturnedByOwnerSurname, rb.OwnerAddress AS ReturnedByOwnerAddress, " \
        "rb.OwnerTown AS ReturnedByOwnerTown, rb.OwnerCounty AS ReturnedByOwnerCounty, " \
        "rb.OwnerPostcode AS ReturnedByOwnerPostcode, rb.HomeTelephone AS ReturnedByHomeTelephone, " \
        "rb.WorkTelephone AS ReturnedByWorkTelephone, rb.MobileTelephone AS ReturnedByMobileTelephone, " \
        "rb.EmailAddress AS ReturnedByEmailAddress, " \
        "rb.IdentificationNumber AS ReturnedByIDNumber, " \
        "a.AdoptionCoordinatorID, ac.OwnerName AS AdoptionCoordinatorName, " \
        "o.HomeCheckedBy AS HomeCheckedByID, hc.OwnerName AS HomeCheckedByName, o.DateLastHomeChecked " \
        "FROM adoption m " \
        "LEFT OUTER JOIN reservationstatus rs ON rs.ID = m.ReservationStatusID " \
        "LEFT OUTER JOIN lksmovementtype l ON l.ID = m.MovementType " \
        "LEFT OUTER JOIN animal a ON m.AnimalID = a.ID " \
        "LEFT OUTER JOIN adoption ad ON a.ActiveMovementID = ad.ID " \
        "LEFT OUTER JOIN basecolour bc ON a.BaseColourID = bc.ID " \
        "LEFT OUTER JOIN owner co ON co.ID = ad.OwnerID " \
        "LEFT OUTER JOIN owner ac ON ac.ID = a.AdoptionCoordinatorID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN media ma ON ma.LinkID = a.ID AND ma.LinkTypeID = 0 AND ma.WebsitePhoto = 1 " \
        "LEFT OUTER JOIN entryreason er ON a.EntryReasonID = er.ID " \
        "LEFT OUTER JOIN lksentrytype et ON a.EntryTypeID = et.ID " \
        "LEFT OUTER JOIN entryreason rr ON m.ReturnedReasonID = rr.ID " \
        "LEFT OUTER JOIN species s ON a.SpeciesID = s.ID " \
        "LEFT OUTER JOIN lksex sx ON sx.ID = a.Sex " \
        "LEFT OUTER JOIN lksize sz ON sz.ID = a.Size " \
        "LEFT OUTER JOIN owner o ON m.OwnerID = o.ID " \
        "LEFT OUTER JOIN owner hc ON hc.ID = o.HomeCheckedBy " \
        "LEFT OUTER JOIN owner r ON m.RetailerID = r.ID " \
        "LEFT OUTER JOIN owner rb ON m.ReturnedByOwnerID = rb.ID " % { "now": dbo.sql_now() }

def get_transport_query(dbo: Database) -> str:
    return "SELECT t.*, tt.TransportTypeName, " \
        "d.OwnerName AS DriverOwnerName, p.OwnerName AS PickupOwnerName, dr.OwnerName AS DropoffOwnerName, " \
        "d.OwnerAddress AS DriverOwnerAddress, p.OwnerAddress AS PickupOwnerAddress, dr.OwnerAddress AS DropoffOwnerAddress, " \
        "d.OwnerTown AS DriverOwnerTown, p.OwnerTown AS PickupOwnerTown, dr.OwnerTown AS DropoffOwnerTown, " \
        "d.OwnerCounty AS DriverOwnerCounty, p.OwnerCounty AS PickupOwnerCounty, dr.OwnerCounty AS DropoffOwnerCounty, " \
        "d.OwnerPostcode AS DriverOwnerPostcode, p.OwnerPostcode AS PickupOwnerPostcode, dr.OwnerPostcode AS DropoffOwnerPostcode, " \
        "d.OwnerCountry AS DriverOwnerCountry, p.OwnerCountry AS PickupOwnerCountry, dr.OwnerCountry AS DropoffOwnerCountry, " \
        "d.EmailAddress AS DriverEmailAddress, p.EmailAddress AS PickupEmailAddress, dr.EmailAddress AS DropoffEmailAddress, " \
        "d.HomeTelephone AS DriverHomeTelephone, p.HomeTelephone AS PickupHomeTelephone, dr.HomeTelephone AS DropoffHomeTelephone, " \
        "d.WorkTelephone AS DriverWorkTelephone, p.WorkTelephone AS PickupWorkTelephone, dr.WorkTelephone AS DropoffWorkTelephone, " \
        "d.MobileTelephone AS DriverMobileTelephone, p.MobileTelephone AS PickupMobileTelephone, dr.MobileTelephone AS DropoffMobileTelephone, " \
        "t.PickupAddress, t.PickupTown, t.PickupCounty, t.PickupPostcode, t.PickupCountry, " \
        "t.DropoffAddress, t.DropoffTown, t.DropoffCounty, t.DropoffPostcode, t.DropoffCountry, " \
        "ma.MediaName AS WebsiteMediaName, ma.Date AS WebsiteMediaDate, " \
        "a.AnimalName, a.ShelterCode, a.ShortCode, s.SpeciesName, a.BreedName, a.Sex, " \
        "st.Name AS StatusName " \
        "FROM animaltransport t " \
        "LEFT OUTER JOIN transporttype tt ON tt.ID = t.TransportTypeID " \
        "LEFT OUTER JOIN lkstransportstatus st ON st.ID = t.Status " \
        "LEFT OUTER JOIN animal a ON t.AnimalID = a.ID " \
        "LEFT OUTER JOIN species s ON s.ID = a.SpeciesID " \
        "LEFT OUTER JOIN media ma ON ma.LinkID = a.ID AND ma.LinkTypeID = 0 AND ma.WebsitePhoto = 1 " \
        "LEFT OUTER JOIN owner d ON t.DriverOwnerID = d.ID " \
        "LEFT OUTER JOIN owner p ON t.PickupOwnerID = p.ID " \
        "LEFT OUTER JOIN owner dr ON t.DropoffOwnerID = dr.ID "

def get_movement(dbo: Database, movementid: int) -> ResultRow:
    """
    Returns a single movement by id. Returns None if it does not exist.
    """
    return dbo.first_row(dbo.query(get_movement_query(dbo) + " WHERE m.ID = ?", [movementid]))

def get_movements_two_dates(dbo: Database, fromdate: datetime, todate: datetime, movementtype: int = -1, limit: int = 0):
    """
    Return all movements of movementtype between two dates.
    If movementtype == -1, all movement types are returned.
    """
    typeclause = ""
    if movementtype > -1: typeclause = f"m.MovementType = {movementtype} AND "
    rows = dbo.query(get_movement_query(dbo) + \
        f"WHERE {typeclause}" \
        "m.MovementDate >= ? AND m.MovementDate <= ? " \
        "AND a.DeceasedDate Is Null " \
        "ORDER BY m.MovementDate DESC", (fromdate, todate), limit=limit)
    return rows

def get_active_movements(dbo: Database, movementtype: int) -> Results:
    """
    Gets the list of active movements of a particular type 
    (unreturned or returned after today and for animals who aren't deceased)
    Includes additional fields linked to movements.
    """
    rows = dbo.query(get_movement_query(dbo) + \
        "WHERE m.MovementType = ? AND " \
        "(m.ReturnDate Is Null OR m.ReturnDate > ?) " \
        "AND a.DeceasedDate Is Null " \
        "ORDER BY m.MovementDate DESC", (movementtype, dbo.today()))
    return asm3.additional.append_to_results(dbo, rows , "movement")

def get_active_reservations(dbo: Database, age: int = 0) -> Results:
    """
    Gets the list of uncancelled reservation movements.
    age: The age of the reservation in days, or 0 for all
    """
    rows = []
    if age > 0:
        rows = dbo.query(get_movement_query(dbo) + \
            " WHERE m.ReservationDate Is Not Null AND m.MovementDate Is Null AND m.MovementType = 0 AND m.ReturnDate Is Null " \
            "AND m.ReservationCancelledDate Is Null AND m.ReservationDate <= ? ORDER BY m.ReservationDate", [dbo.today(offset=age*-1)])
    else:
        rows = dbo.query(get_movement_query(dbo) + \
            " WHERE m.ReservationDate Is Not Null AND m.MovementDate Is Null AND m.MovementType = 0 AND m.ReturnDate Is Null " \
            "AND m.ReservationCancelledDate Is Null ORDER BY m.ReservationDate")
    return asm3.additional.append_to_results(dbo, rows , "movement")

def get_active_transports(dbo: Database) -> Results:
    return dbo.query(get_transport_query(dbo) + " WHERE t.Status < 10 OR DropoffDateTime > ? ORDER BY DropoffDateTime", [dbo.today()])

def get_animal_transports(dbo: Database, animalid: int) -> Results:
    return dbo.query(get_transport_query(dbo) + " WHERE t.AnimalID = ? ORDER BY DropoffDateTime", [animalid])

def get_transport(dbo: Database, transportid: int) -> Results:
    return dbo.first_row(dbo.query(get_transport_query(dbo) + " WHERE t.ID = ?", [transportid]))

def get_transports_by_ids(dbo: Database, transportids: List[int]) -> Results:
    return dbo.query(get_transport_query(dbo) + "WHERE t.ID IN (%s) ORDER BY DropoffDateTime" % ",".join(str(x) for x in transportids))

def get_transport_two_dates(dbo: Database, start: datetime, end: datetime) -> Results: 
    return dbo.query(get_transport_query(dbo) + " WHERE t.PickupDateTime >= ? AND t.PickupDateTime <= ? ORDER BY t.PickupDateTime", (start, end))

def get_recent_adoptions(dbo: Database, months: int = 1) -> Results:
    """
    Returns a list of adoptions in the last "months" months.
    """
    return dbo.query(get_movement_query(dbo) + \
        "WHERE m.MovementType = 1 AND m.MovementDate Is Not Null AND m.ReturnDate Is Null " \
        "AND m.MovementDate > ? " \
        "ORDER BY m.MovementDate DESC", [dbo.today(offset=months*-31)])

def get_recent_nonfosteradoption(dbo: Database, months: int = 1) -> Results:
    """
    Returns a list of active movements that aren't reserves,
    fosters, adoptions or transfers in the last "months" months.
    """
    return dbo.query(get_movement_query(dbo) + \
        "WHERE m.MovementType > 3 AND m.MovementDate Is Not Null AND m.ReturnDate Is Null " \
        "AND m.MovementDate > ? " \
        "ORDER BY m.MovementDate DESC", [dbo.today(offset=months*-31)])

def get_recent_transfers(dbo: Database, months: int = 1) -> Results:
    """
    Returns a list of transfers in the last "months" months.
    """
    return dbo.query(get_movement_query(dbo) + \
        "WHERE m.MovementType = 3 AND m.MovementDate Is Not Null AND m.ReturnDate Is Null " \
        "AND m.MovementDate > ? " \
        "ORDER BY m.MovementDate DESC", [dbo.today(offset=months*-31)])

def get_recent_unneutered_adoptions(dbo: Database, months: int = 1) -> Results:
    """
    Returns a list of adoptions in the last "months" months where the
    animal remains unneutered.
    """
    return dbo.query(get_movement_query(dbo) + \
        "WHERE m.MovementType = 1 AND m.MovementDate Is Not Null AND m.ReturnDate Is Null " \
        "AND m.MovementDate > ? AND a.Neutered = 0 AND a.SpeciesID IN ( " + asm3.configuration.alert_species_neuter(dbo) + ") " \
        "ORDER BY m.MovementDate DESC" , [dbo.today(offset=months*-31)])

def get_soft_releases(dbo: Database) -> Results:
    """
    Returns a list of soft release movements. 
    """
    return dbo.query(get_movement_query(dbo) + \
        "WHERE m.IsTrial = 1 AND m.MovementType = 7 AND (m.ReturnDate Is Null OR m.ReturnDate > ?) " \
        "ORDER BY m.TrialEndDate", [dbo.today()])

def get_trial_adoptions(dbo: Database) -> Results:
    """
    Returns a list of trial adoption movements. 
    """
    return dbo.query(get_movement_query(dbo) + \
        "WHERE m.IsTrial = 1 AND m.MovementType = 1 AND (m.ReturnDate Is Null OR m.ReturnDate > ?) " \
        "ORDER BY m.TrialEndDate", [dbo.today()])

def get_animal_movements(dbo: Database, aid: int) -> Results:
    """
    Gets the list of movements for a particular animal
    """
    rows = dbo.query(get_movement_query(dbo) + " WHERE m.AnimalID = ? ORDER BY ActiveDate DESC", [aid])
    return asm3.additional.append_to_results(dbo, rows, "movement")

def get_person_movements(dbo: Database, pid: int) -> Results:
    """
    Gets the list of movements for a particular person
    """
    rows = dbo.query(get_movement_query(dbo) + " WHERE m.OwnerID = ? ORDER BY ActiveDate DESC", [pid])
    return asm3.additional.append_to_results(dbo, rows, "movement")

def validate_movement_form_data(dbo: Database, username: str, post: PostedData) -> None:
    """
    Verifies that form data is valid for a movement. 
    Throws an appropriate Exception with message if not. Returns no value.
    """
    l = dbo.locale
    movementid = post.integer("movementid")
    movement = None
    if movementid != 0: movement = dbo.first_row(dbo.query("SELECT * FROM adoption WHERE ID = ?", [movementid]))
    adoptionno = post["adoptionno"]
    movementtype = post.integer("type")
    movementdate = post.date("movementdate")
    returndate = post.date("returndate")
    reservationdate = post.date("reservationdate")
    reservationcancelled = post.date("reservationcancelled")
    personid = post.integer("person")
    animalid = post.integer("animal")
    retailerid = post.integer("retailer")
    datebroughtin = dbo.query_date("SELECT DateBroughtIn FROM animal WHERE ID = ?", [animalid])
    if datebroughtin is not None: datebroughtin = datebroughtin.replace(hour=0, minute=0, second=0, microsecond=0)
    asm3.al.debug("validating saved movement %d for animal %d" % (movementid, animalid), "movement.validate_movement_form_data", dbo)
    # If we have a date but no type, get rid of it
    if movementdate is not None and movementtype == 0:
        post.data["movementdate"] = ""
        asm3.al.debug("blank date and type", "movement.validate_movement_form_data", dbo)
    # If we've got a type, but no date, default today
    if movementtype > 0 and movementdate is None:
        movementdate = dbo.today()
        post.data["movementdate"] = asm3.i18n.python2display(l, movementdate)
        asm3.al.debug("type set and no date, defaulting today", "movement.validate_movement_form_data", dbo)
    # If we've got a reserve cancellation without a reserve, remove it
    if reservationdate is None and reservationcancelled is not None:
        post.data["reservationdate"] = ""
        asm3.al.debug("movement has no reserve or cancelled date", "movement.validate_movement_form_data", dbo)
    # Animals are always required, except for reservations with the right option
    if animalid == 0:
        if movementtype > 0 or not asm3.configuration.movement_person_only_reserves(dbo):
            asm3.al.debug("movement has no animal", "movement.validate_movement_form_data", dbo)
            raise asm3.utils.ASMValidationError(asm3.i18n._("Movements require an animal", l))
    # Owners are required unless type is escaped, stolen or released
    if personid == 0 and movementtype != ESCAPED and movementtype != STOLEN and movementtype != RELEASED:
        asm3.al.debug("movement has no person and is not ESCAPED|STOLEN|RELEASED|TRANSPORT", "movement.validate_movement_form_data", dbo)
        raise asm3.utils.ASMValidationError(asm3.i18n._("A person is required for this movement type.", l))
    # Is the movement number unique?
    if 0 != dbo.query_int("SELECT COUNT(*) FROM adoption WHERE AdoptionNumber LIKE ? AND ID <> ?", (adoptionno, movementid)):
        raise asm3.utils.ASMValidationError(asm3.i18n._("Movement numbers must be unique.", l))
    # If we're updating an existing record, we only need to continue validation
    # if one of the important fields has changed (movement date/type, return date, reservation, animal)
    if movement is not None:
        if movementtype == movement["MOVEMENTTYPE"] and movementdate == movement["MOVEMENTDATE"] and returndate == movement["RETURNDATE"] and reservationdate == movement["RESERVATIONDATE"] and animalid == movement["ANIMALID"]:
            asm3.al.debug("movement type, dates and animalid have not changed. Abandoning further validation", "movement.validate_movement_form_data", dbo)
            return
    # If the animal is held in case of reclaim, it can't be adopted
    if movementtype == ADOPTION:
        if 1 == dbo.query_int("SELECT IsHold FROM animal WHERE ID = ?", [animalid]):
            asm3.al.debug("movement is adoption and the animal is on hold", "movement.validate_movement_form_data", dbo)
            raise asm3.utils.ASMValidationError(asm3.i18n._("This animal is currently held and cannot be adopted.", l))
    # If it's a foster movement, make sure the owner is a fosterer
    if movementtype == FOSTER:
        if 0 == dbo.query_int("SELECT IsFosterer FROM owner WHERE ID = ?", [personid]):
            asm3.al.debug("movement is a foster and the person is not a fosterer.", "movement.validate_movement_form_data", dbo)
            raise asm3.utils.ASMValidationError(asm3.i18n._("This person is not flagged as a fosterer and cannot foster animals.", l))
    # If it's a retailer movement, make sure the owner is a retailer
    if movementtype == RETAILER:
        if 0 == dbo.query_int("SELECT IsRetailer FROM owner WHERE ID = ?", [personid]):
            asm3.al.debug("movement is a retailer and the person is not a retailer.", "movement.validate_movement_form_data", dbo)
            raise asm3.utils.ASMValidationError(asm3.i18n._("This person is not flagged as a retailer and cannot handle retailer movements.", l))
    # If a retailer is selected, make sure it's an adoption
    if retailerid != 0 and movementtype != ADOPTION:
        asm3.al.debug("movement has a retailerid set and this is not an adoption.", "movement.validate_movement_form_data", dbo)
        raise asm3.utils.ASMValidationError(asm3.i18n._("From retailer is only valid on adoption movements.", l))
    # If a retailer is selected, make sure there's been a retailer movement in this animal's history
    if retailerid != 0:
        if 0 == dbo.query_int("SELECT COUNT(*) FROM adoption WHERE AnimalID = ? AND MovementType = ?", ( animalid, RETAILER )):
            asm3.al.debug("movement has a retailerid set but has never been to a retailer.", "movement.validate_movement_form_data", dbo)
            raise asm3.utils.ASMValidationError(asm3.i18n._("This movement cannot be from a retailer when the animal has no prior retailer movements.", l))
    # Movement date cannot be before brought in date
    if movementdate is not None and datebroughtin is not None and movementdate < datebroughtin:
        asm3.al.debug("movement date is before date brought in", "movement.validate_movement_form_data", dbo)
        raise asm3.utils.ASMValidationError(asm3.i18n._("Movement date cannot be before brought in date.", l))
    # You can't have a return without a movement
    if movementdate is None and returndate is not None:
        asm3.al.debug("movement is returned without a movement date.", "movement.validate_movement_form_data", dbo)
        raise asm3.utils.ASMValidationError(asm3.i18n._("You can't have a return without a movement.", l))
    # Return should be after or same day as movement
    if movementdate is not None and returndate is not None and movementdate > returndate:
        asm3.al.debug("movement return date is before the movement date.", "movement.validate_movement_form_data", dbo)
        raise asm3.utils.ASMValidationError(asm3.i18n._("Return date cannot be before the movement date.", l))
    # If the option to return fosters on adoption is set, return any outstanding fosters for the animal
    if movementtype == ADOPTION and returndate is None and asm3.configuration.return_fosters_on_adoption(dbo):
        fosterrow = dbo.first_row(dbo.query("SELECT ID, AnimalID, OwnerID FROM adoption WHERE ReturnDate Is Null AND " \
            "MovementType=2 AND AnimalID=? AND ID<>?", (animalid, movementid)))
        if fosterrow is not None:
            dbo.update("adoption", fosterrow.ID, { 
                "AnimalID": fosterrow.ANIMALID,
                "OwnerID": fosterrow.OWNERID, 
                "ReturnDate": movementdate }, username)
            asm3.al.debug(f"movement is an adoption, returning outstanding foster (id={fosterrow.ID}).", "movement.validate_movement_form_data", dbo)
    # If the option to return fosters on transfer is set, return any outstanding fosters for the animal
    if movementtype == TRANSFER and returndate is None and asm3.configuration.return_fosters_on_transfer(dbo):
        fosterrow = dbo.first_row(dbo.query("SELECT ID, AnimalID, OwnerID FROM adoption WHERE ReturnDate Is Null AND " \
            "MovementType=2 AND AnimalID=? AND ID<>?", (animalid, movementid)))
        if fosterrow is not None:
            dbo.update("adoption", fosterrow.ID, { 
                "AnimalID": fosterrow.ANIMALID,
                "OwnerID": fosterrow.OWNERID, 
                "ReturnDate": movementdate }, username)
            asm3.al.debug(f"movement is a transfer, returning outstanding foster (id={fosterrow.ID}).", "movement.validate_movement_form_data", dbo)
    # If the option to return retailers on adoption is set, return any outstanding retailer moves for the animal
    if movementtype == ADOPTION and returndate is None and asm3.configuration.return_retailer_on_adoption(dbo):
        retailerrow = dbo.first_row(dbo.query("SELECT ID, AnimalID, OwnerID FROM adoption WHERE " \
            "ReturnDate Is Null AND MovementType=8 AND AnimalID=? AND ID<>?", (animalid, movementid)))
        if retailerrow is not None:
            dbo.update("adoption", retailerrow.ID, { 
                "AnimalID": retailerrow.ANIMALID, 
                "OwnerID": retailerrow.OWNERID, 
                "ReturnDate": movementdate }, username)
            asm3.al.debug(f"movement is an adoption, returning outstanding retailer (id={retailerrow.ID}).", "movement.validate_movement_form_data", dbo)
            post["originalretailermovement"] = str(retailerrow.ID)
            post["retailer"] = str(retailerrow.OWNERID)
    # Can't have multiple open movements
    if movementdate is not None and returndate is None:
        existingopen = dbo.query_int("SELECT COUNT(*) FROM adoption WHERE MovementDate Is Not Null AND " \
            "ReturnDate Is Null AND AnimalID = ? AND ID <> ?", (animalid, movementid))
        if existingopen > 0:
            asm3.al.debug("movement is open and animal already has another open movement.", "movement.validate_movement_form_data", dbo)
            raise asm3.utils.ASMValidationError(asm3.i18n._("An animal cannot have multiple open movements.", l))
    # If we have a movement and return, is there another movement with a 
    # movementdate between the movement and return date on this one?
    if movementdate is not None and returndate is not None:
        clash = dbo.query_int("SELECT COUNT(*) FROM adoption WHERE " \
        "AnimalID = ? AND ID <> ? AND ((ReturnDate > ? AND ReturnDate < ?) " \
        "OR (MovementDate < ? AND MovementDate > ?))", ( animalid, movementid, movementdate, returndate, returndate, movementdate ))
        if clash > 0:
            asm3.al.debug("movement dates overlap an existing movement.", "movement.validate_movement_form_data", dbo)
            raise asm3.utils.ASMValidationError(asm3.i18n._("Movement dates clash with an existing movement.", l))
    # Does this movement date fall within the date range of an already
    # returned movement for the same animal?
    if movementdate is not None and returndate is None:
        clash = dbo.query_int("SELECT COUNT(*) FROM adoption WHERE AnimalID = ? AND ID <> ? AND " \
        "MovementDate Is Not Null AND ReturnDate Is Not Null AND " \
        "? > MovementDate AND ? < ReturnDate", ( animalid, movementid, movementdate, movementdate))
        if clash > 0:
            asm3.al.debug("movement dates overlap an existing movement.", "movement.validate_movement_form_data", dbo)
            raise asm3.utils.ASMValidationError(asm3.i18n._("Movement dates clash with an existing movement.", l))
    # If there's a cancelled reservation, make sure it's after the reserve date
    if reservationdate is not None and reservationcancelled is not None and reservationcancelled < reservationdate:
        asm3.al.debug("reserve date is after cancelled date.", "movement.validate_movement_form_data", dbo)
        raise asm3.utils.ASMValidationError(asm3.i18n._("Reservation date cannot be after cancellation date.", l))
    # If this is a new reservation, make sure there's no open movement (fosters do not count)
    if movementid == 0 and movementtype == 0 and movementdate is None and reservationdate is not None:
        om = dbo.query_int("SELECT COUNT(*) FROM adoption WHERE AnimalID = ? AND " \
            "MovementDate Is Not Null AND ReturnDate Is Null AND MovementType <> 2 AND MovementType <> 8", [animalid])
        if om > 0:
            asm3.al.debug("movement is a reservation but animal has active movement.", "movement.validate_movement_form_data", dbo)
            raise asm3.utils.ASMValidationError(asm3.i18n._("Can't reserve an animal that has an active movement.", l))
    # Make sure the adoption number is unique
    an = dbo.query_int("SELECT COUNT(*) FROM adoption WHERE ID <> ? AND " \
        "AdoptionNumber LIKE ?", (movementid, adoptionno))
    if an > 0:
        asm3.al.debug("movement number is not unique.", "movement.validate_movement_form_data", dbo)
        raise asm3.utils.ASMValidationError(asm3.i18n._("The movement number '{0}' is not unique.", l).format(post["adoptionno"]))
    # If this is an adoption and the owner had some criteria, expire them
    if movementtype == ADOPTION and personid > 0:
        dbo.update("owner", personid, { "MatchActive": 0, "MatchExpires": dbo.today() }, username)
        asm3.al.debug(f"movement is an adoption, expiring person criteria (id={personid}).", "movement.validate_movement_form_data", dbo)
    # If the option to cancel reserves on adoption is set, cancel any outstanding reserves for the animal
    if movementtype == ADOPTION and asm3.configuration.cancel_reserves_on_adoption(dbo):
        reserves = dbo.query("SELECT ID FROM adoption WHERE ReservationCancelledDate Is Null AND MovementDate Is Null AND AnimalID=? AND ID<>?", (animalid, movementid))
        if len(reserves) > 0:
            cancids = []
            for r in reserves:
                cancids.append(str(r.ID))
                dbo.update("adoption", r.ID, { "ReservationCancelledDate": dbo.today() }, username)
            asm3.al.debug(f"movement is an adoption, cancelling outstanding reserves (ids={cancids}).", "movement.validate_movement_form_data", dbo)

def insert_movement_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Creates a movement record from posted form data 
    """
    movementid = dbo.get_id("adoption")
    adoptionno = post["adoptionno"]
    animalid = post.integer("animal")

    if adoptionno == "": 
        # No adoption number was supplied, generate a
        # unique number from the movementid
        idx = movementid
        while True:
            adoptionno = asm3.utils.padleft(idx, 6)
            post.data["adoptionno"] = adoptionno
            if 0 == dbo.query_int("SELECT COUNT(*) FROM adoption WHERE AdoptionNumber LIKE ?", [adoptionno]):
                break
            else:
                idx += 1

    validate_movement_form_data(dbo, username, post)

    dbo.insert("adoption", {
        "ID":                           movementid,
        "AdoptionNumber":               adoptionno,
        "OwnerID":                      post.integer("person"),
        "RetailerID":                   post.integer("retailer"),
        "AnimalID":                     post.integer("animal"),
        "OriginalRetailerMovementID":   post.integer("originalretailermovement"),
        "EventID":                      post.integer("event"),
        "MovementDate":                 post.date("movementdate"),
        "MovementType":                 post.integer("type"),
        "ReturnDate":                   post.date("returndate"),
        "ReturnedReasonID":             post.integer("returncategory"),
        "Donation":                     post.integer("donation"),
        "InsuranceNumber":              post["insurance"],
        "ReasonForReturn":              post["reason"],
        "ReturnedByOwnerID":            post.integer("returnedby"),
        "ReservationDate":              post.datetime("reservationdate", "reservationtime"),
        "ReservationCancelledDate":     post.date("reservationcancelled"),
        "ReservationStatusID":          post.integer("reservationstatus"),
        "IsTrial":                      post.boolean("trial"),
        "IsPermanentFoster":            post.boolean("permanentfoster"),
        "TrialEndDate":                 post.date("trialenddate"),
        "Comments":                     post["comments"]
    }, username, generateID=False)
    asm3.additional.save_values_for_link(dbo, post, username, movementid, "movement")

    if animalid > 0:
        asm3.animal.update_current_owner(dbo, username, animalid)
        asm3.animal.update_animal_status(dbo, animalid)
        asm3.animal.update_variable_animal_data(dbo, animalid)
        update_movement_donation(dbo, movementid)
        asm3.person.update_adopter_flag(dbo, username, post.integer("person"))
    return movementid

def update_movement_from_form(dbo: Database, username: str, post: PostedData) -> None:
    """
    Updates a movement record from posted form data
    """
    validate_movement_form_data(dbo, username, post)
    movementid = post.integer("movementid")
    oanimalid = dbo.query_int("SELECT AnimalID FROM adoption WHERE ID=?", [movementid])
    dbo.update("adoption", movementid, {
        "AdoptionNumber":               post["adoptionno"],
        "OwnerID":                      post.integer("person"),
        "RetailerID":                   post.integer("retailer"),
        "AnimalID":                     post.integer("animal"),
        "OriginalRetailerMovementID":   post.integer("originalretailermovement"),
        "EventID":                      post.integer("event"),
        "MovementDate":                 post.date("movementdate"),
        "MovementType":                 post.integer("type"),
        "ReturnDate":                   post.date("returndate"),
        "ReturnedReasonID":             post.integer("returncategory"),
        "Donation":                     post.integer("donation"),
        "InsuranceNumber":              post["insurance"],
        "ReasonForReturn":              post["reason"],
        "ReturnedByOwnerID":            post.integer("returnedby"),
        "ReservationDate":              post.datetime("reservationdate", "reservationtime"),
        "ReservationCancelledDate":     post.date("reservationcancelled"),
        "ReservationStatusID":          post.integer("reservationstatus"),
        "IsTrial":                      post.boolean("trial"),
        "IsPermanentFoster":            post.boolean("permanentfoster"),
        "TrialEndDate":                 post.date("trialenddate"),
        "Comments":                     post["comments"]
    }, username)

    asm3.additional.save_values_for_link(dbo, post, username, movementid, "movement")

    # If the animal ID has been changed, update the previous animal to prevent
    # its active movement being left pointing at this movement
    if oanimalid > 0 and post.integer("animal") != oanimalid:
        asm3.animal.update_animal_status(dbo, oanimalid)

    if post.integer("animal") > 0:
        asm3.animal.update_current_owner(dbo, username, post.integer("animal"))
        asm3.animal.update_animal_status(dbo, post.integer("animal"))
        asm3.animal.update_variable_animal_data(dbo, post.integer("animal"))
        update_movement_donation(dbo, movementid)
        asm3.person.update_adopter_flag(dbo, username, post.integer("person"))

def delete_movement(dbo: Database, username: str, mid: int) -> None:
    """
    Deletes a movement record
    """
    m = dbo.first_row(dbo.query("SELECT * FROM adoption WHERE ID = ?", [mid]))
    if m is None:
        raise asm3.utils.ASMError("Trying to delete a movement that does not exist")
    dbo.execute("UPDATE ownerdonation SET MovementID = 0 WHERE MovementID = ?", [mid])
    dbo.delete("adoption", mid, username)
    if m.ANIMALID > 0:
        asm3.animal.update_current_owner(dbo, username, m.ANIMALID)
        asm3.animal.update_animal_status(dbo, m.ANIMALID)
        asm3.animal.update_variable_animal_data(dbo, m.ANIMALID)
        asm3.person.update_adopter_flag(dbo, username, m.OWNERID)

def cancel_reservation(dbo: Database, username: str, movementid: int) -> None:
    """
    Cancels the reservation with movementid
    """
    m = dbo.first_row(dbo.query("SELECT AnimalID, OwnerID, ReservationDate, ReservationCancelledDate FROM adoption WHERE ID=?", [movementid]))
    if m.RESERVATIONDATE is not None and m.RESERVATIONCANCELLEDDATE is None:
        dbo.update("adoption", movementid, { "ReservationCancelledDate": dbo.today() }, username)
        asm3.animal.update_animal_status(dbo, m.ANIMALID)

def return_movement(dbo: Database, movementid: int, username: str, animalid: int = 0, returndate: datetime = None) -> None:
    """
    Returns a movement with the date given. If animalid is not supplied, it
    will be looked up from the movement given. If returndate is not supplied,
    now() will be used.
    """
    if returndate is None: returndate = dbo.today()
    if animalid == 0: animalid = dbo.query_int("SELECT AnimalID FROM adoption WHERE ID = ?", [movementid])
    personid = dbo.query_int("SELECT OwnerID FROM adoption WHERE ID = ?", [movementid])
    dbo.update("adoption", movementid, { "ReturnDate": returndate })
    asm3.animal.update_animal_status(dbo, animalid)
    asm3.person.update_adopter_flag(dbo, username, personid)

def trial_to_full_adoption(dbo: Database, username: str, movementid: int) -> None:
    """
    Removes the trial flag from movementid
    If the trial end date on the record is blank, sets it to today
    """
    m = dbo.first_row(dbo.query("SELECT AnimalID, OwnerID, TrialEndDate FROM adoption WHERE ID=?", [movementid]))
    ud = { "IsTrial": 0 }
    if m.TRIALENDDATE is None: ud["TrialEndDate"] = dbo.today()
    dbo.update("adoption", movementid, ud, username)
    asm3.animal.update_animal_status(dbo, m.ANIMALID)
    asm3.person.update_adopter_flag(dbo, username, m.OWNERID)

def insert_adoption_from_form(dbo: Database, username: str, post: PostedData, creating: List[int] = [], create_payments: bool = True) -> int:
    """
    Inserts a movement from the workflow adopt an animal screen.
    Returns the new movement id
    creating is an ongoing list of animals we're already going to
    create adoptions for. It prevents a never ending recursive loop
    of animal1 being bonded to animal2 that's bonded to animal1, etc.
    create_payments is True if we should create payments - don't do this
    for bonded animals or we'll double up all the payments.
    """
    l = dbo.locale
    # Validate that we have a movement date before doing anthing
    if None is post.date("movementdate"):
        raise asm3.utils.ASMValidationError(asm3.i18n._("Adoption movements must have a valid adoption date.", l))
    # Get the animal record for this adoption
    a = asm3.animal.get_animal(dbo, post.integer("animal"))
    if a is None:
        raise asm3.utils.ASMValidationError("Adoption POST has an invalid animal ID: %d" % post.integer("animal"))
    asm3.al.debug("Creating adoption for %d (%s - %s)" % (a["ID"], a["SHELTERCODE"], a["ANIMALNAME"]), "movement.insert_adoption_from_form", dbo)
    creating.append(a.ID)
    # If the animal is bonded to other animals, we call this function
    # again with a copy of the data and the bonded animal substituted
    # so we can create their adoption records too. We only do this if
    # the other animals are still on shelter (therefore alive).
    if a.BONDEDANIMALID is not None and a.BONDEDANIMALID != 0 and a.BONDEDANIMAL1ARCHIVED == 0 and a.BONDEDANIMALID not in creating:
        asm3.al.debug("Found bond to animal %d, creating adoption..." % a.BONDEDANIMALID, "movement.insert_adoption_from_form", dbo)
        newdata = dict(post.data)
        newdata["animal"] = str(a.BONDEDANIMALID)
        insert_adoption_from_form(dbo, username, asm3.utils.PostedData(newdata, dbo.locale), creating, create_payments = False)
    if a.BONDEDANIMAL2ID is not None and a.BONDEDANIMAL2ID != 0 and a.BONDEDANIMAL2ARCHIVED == 0 and a.BONDEDANIMAL2ID not in creating:
        asm3.al.debug("Found bond to animal %d, creating adoption..." % a.BONDEDANIMAL2ID, "movement.insert_adoption_from_form", dbo)
        newdata = dict(post.data)
        newdata["animal"] = str(a.BONDEDANIMAL2ID)
        insert_adoption_from_form(dbo, username, asm3.utils.PostedData(newdata, dbo.locale), creating, create_payments = False)
    cancel_reserves = asm3.configuration.cancel_reserves_on_adoption(dbo)
    # Prepare a dictionary of data for the movement table via insert_movement_from_form
    move_dict = {
        "person"                : post["person"],
        "animal"                : post["animal"],
        "adoptionno"            : post["movementnumber"],
        "movementdate"          : post["movementdate"],
        "type"                  : str(ADOPTION),
        "donation"              : post["amount"],
        "insurance"             : post["insurance"],
        "returncategory"        : asm3.configuration.default_return_reason(dbo),
        "trial"                 : post["trial"],
        "trialenddate"          : post["trialenddate"],
        "comments"              : post["comments"],
        "event"                 : post["event"]
    }
    move_dict.update(asm3.additional.get_additional_fields_dict(dbo, post, 'movement'))
    # Is this animal currently on foster? If so, return the foster
    fm = get_animal_movements(dbo, post.integer("animal"))
    for m in fm:
        if m.MOVEMENTTYPE == FOSTER and m.RETURNDATE is None:
            return_movement(dbo, m["ID"], username, post.integer("animal"), post.date("movementdate"))
    # Is this animal current at a retailer? If so, return it from the
    # retailer and set the originalretailermovement and retailerid fields
    # on our new adoption movement so it can be linked back
    for m in fm:
        if m.MOVEMENTTYPE == RETAILER and m.RETURNDATE is None:
            return_movement(dbo, m.ID, username, post.integer("animal"), post.date("movementdate"))
            move_dict["originalretailermovement"] = str(m.ID)
            move_dict["retailer"] = str(m["OWNERID"])
    # Did we say we'd like to flag the owner as homechecked?
    if post.boolean("homechecked") == 1:
        dbo.update("owner", post.integer("person"), { "IDCheck": 1, "DateLastHomeChecked": dbo.today() }, username)
    # If the animal was flagged as not available for adoption, then it
    # shouldn't be since we've just adopted it.
    dbo.update("animal", a.ID, { "IsNotAvailableForAdoption": 0 })
    # Is the animal reserved to the person adopting? 
    movementid = 0
    for m in fm:
        if m.MOVEMENTTYPE == NO_MOVEMENT and m.RESERVATIONDATE is not None \
            and m.RESERVATIONCANCELLEDDATE is None and m.ANIMALID == post.integer("animal") \
            and m.OWNERID == post.integer("person"):
            # yes - update the existing movement
            movementid = m.ID
            move_dict["movementid"] = str(movementid)
            move_dict["adoptionno"] = asm3.utils.padleft(movementid, 6)
            move_dict["reservationdate"] = str(asm3.i18n.python2display(l, m.RESERVATIONDATE))
            move_dict["comments"] = asm3.utils.nulltostr(m.COMMENTS)
            break
        elif cancel_reserves and m.MOVEMENTTYPE == NO_MOVEMENT and m.RESERVATIONDATE is not None \
            and m.RESERVATIONCANCELLEDDATE is None:
            # no, but it's reserved to someone else and we're cancelling
            # reserves on adoption
            dbo.update("adoption", m.ID, { "ReservationCancelledDate": post.date("movementdate") }, username)
    if movementid != 0:
        update_movement_from_form(dbo, username, asm3.utils.PostedData(move_dict, l))
    else:
        movementid = insert_movement_from_form(dbo, username, asm3.utils.PostedData(move_dict, l))
    # Create any payments
    if create_payments:
        asm3.financial.insert_donations_from_form(dbo, username, post, post["movementdate"], False, post["person"], post["animal"], movementid) 
    # Then any boarding cost record
    cost_amount = post.integer("costamount")
    cost_type = post["costtype"]
    cost_create = post.boolean("costcreate")
    if cost_amount > 0 and cost_type != "" and cost_create:
        boc_dict = {
            "animalid"          : post["animal"],
            "type"              : cost_type,
            "costdate"          : post["movementdate"],
            "costpaid"          : post["movementdate"],
            "cost"              : post["costamount"]
        }
        asm3.animal.insert_cost_from_form(dbo, username, asm3.utils.PostedData(boc_dict, l))
    return movementid

def insert_foster_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Inserts a movement from the workflow foster an animal screen.
    Returns the new movement id
    """
    # Validate that we have a movement date before doing anthing
    l = dbo.locale
    if None is post.date("fosterdate"):
        raise asm3.utils.ASMValidationError(asm3.i18n._("Foster movements must have a valid foster date.", l))
    # Is this animal already on foster? If so, return that foster first
    fm = get_animal_movements(dbo, post.integer("animal"))
    for m in fm:
        if m.MOVEMENTTYPE == FOSTER and m.RETURNDATE is None:
            # if the existing foster is to this person, bail
            if m.OWNERID == post.integer("person"):
                raise asm3.utils.ASMValidationError(asm3.i18n._("Already fostered to this person.", l))
            else:
                return_movement(dbo, m.ID, username, post.integer("animal"), post.date("fosterdate"))
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
        "returncategory"        : asm3.configuration.default_return_reason(dbo),
        "comments"              : post["comments"]
    }
    move_dict.update(asm3.additional.get_additional_fields_dict(dbo, post, 'movement'))
    movementid = insert_movement_from_form(dbo, username, asm3.utils.PostedData(move_dict, l))
    return movementid

def insert_reclaim_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """f
    Inserts a movement from the workflow adopt an animal screen.
    Returns the new movement id
    """
    l = dbo.locale
    # Validate that we have a movement date before doing anthing
    if None is post.date("movementdate"):
        raise asm3.utils.ASMValidationError(asm3.i18n._("Reclaim movements must have a valid reclaim date.", l))
    # Get the animal record for this reclaim
    a = asm3.animal.get_animal(dbo, post.integer("animal"))
    if a is None:
        raise asm3.utils.ASMValidationError("Reclaim POST has an invalid animal ID: %d" % post.integer("animal"))
    asm3.al.debug("Creating reclaim for %d (%s - %s)" % (a.ID, a.SHELTERCODE, a.ANIMALNAME), "movement.insert_reclaim_from_form", dbo)
    # Prepare a dictionary of data for the movement table via insert_movement_from_form
    move_dict = {
        "person"                : post["person"],
        "animal"                : post["animal"],
        "adoptionno"            : post["movementnumber"],
        "movementdate"          : post["movementdate"],
        "type"                  : str(RECLAIMED),
        "donation"              : post["amount"],
        "returncategory"        : asm3.configuration.default_return_reason(dbo),
        "comments"              : post["comments"]
    }
    move_dict.update(asm3.additional.get_additional_fields_dict(dbo, post, 'movement'))
    # Is this animal currently on foster? If so, return the foster
    fm = get_animal_movements(dbo, post.integer("animal"))
    for m in fm:
        if m.MOVEMENTTYPE == FOSTER and m.RETURNDATE is None:
            return_movement(dbo, m.ID, username, post.integer("animal"), post.date("movementdate"))
    # Is this animal current at a retailer? If so, return it from the
    # retailer and set the originalretailermovement and retailerid fields
    # on our new adoption movement so it can be linked back
    for m in fm:
        if m.MOVEMENTTYPE == RETAILER and m.RETURNDATE is None:
            return_movement(dbo, m["ID"], username, post.integer("animal"), post.date("movementdate"))
            move_dict["originalretailermovement"] = str(m.ID)
            move_dict["retailer"] = str(m.OWNERID)
    # Is the animal reserved? Should clear it if so
    cancel_reserves = asm3.configuration.cancel_reserves_on_adoption(dbo)
    for m in fm:
        if cancel_reserves and m.MOVEMENTTYPE == NO_MOVEMENT and m.RESERVATIONDATE is not None \
            and m.RESERVATIONCANCELLEDDATE is None:
            dbo.update("adoption", m.ID, { "ReservationCancelledDate": post.date("movementdate") }, username)
    movementid = insert_movement_from_form(dbo, username, asm3.utils.PostedData(move_dict, l))
    # Create any payments
    asm3.financial.insert_donations_from_form(dbo, username, post, post["movementdate"], False, post["person"], post["animal"], movementid) 
    # Then any boarding cost record
    cost_amount = post.integer("costamount")
    cost_type = post["costtype"]
    cost_create = post.boolean("costcreate")
    if cost_amount > 0 and cost_type != "" and cost_create:
        boc_dict = {
            "animalid"          : post["animal"],
            "type"              : cost_type,
            "costdate"          : post["movementdate"],
            "costpaid"          : post["movementdate"],
            "cost"              : post["costamount"]
        }
        asm3.animal.insert_cost_from_form(dbo, username, asm3.utils.PostedData(boc_dict, l))
    return movementid

def insert_transfer_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Inserts a movement from the workflow transfer an animal screen.
    Returns the new movement id
    """
    # Validate that we have a movement date before doing anthing
    l = dbo.locale
    if None is post.date("transferdate"):
        raise asm3.utils.ASMValidationError(asm3.i18n._("Transfers must have a valid transfer date.", l))

    # Is this animal already on foster? If so, return that foster first
    fm = get_animal_movements(dbo, post.integer("animal"))
    for m in fm:
        if m.MOVEMENTTYPE == FOSTER and m.RETURNDATE is None:
            return_movement(dbo, m["ID"], username, post.integer("animal"), post.date("transferdate"))
    # Create the transfer movement
    move_dict = {
        "person"                : post["person"],
        "animal"                : post["animal"],
        "adoptionno"            : post["movementnumber"],
        "movementdate"          : post["transferdate"],
        "type"                  : str(TRANSFER),
        "donation"              : post["amount"],
        "returncategory"        : asm3.configuration.default_return_reason(dbo),
        "comments"              : post["comments"]
    }
    move_dict.update(asm3.additional.get_additional_fields_dict(dbo, post, 'movement'))
    movementid = insert_movement_from_form(dbo, username, asm3.utils.PostedData(move_dict, l))
    return movementid

def insert_reserve(dbo: Database, username: str, personid: int, animalid: int, reservationdate: datetime) -> List[int]:
    """
    Creates a reservation for the animalid to personid.
    If the person is banned from adopting animals, an exception is raised.
    If the animal is bonded to other animals, a reserve is placed on the bonded animals too.
    If an open reservation already exists for this animal/person combo, does nothing.
    """
    l = dbo.locale
    if 1 == dbo.query_int("SELECT IsBanned FROM owner WHERE ID=?", [personid]):
        raise asm3.utils.ASMValidationError("owner %s is banned from adopting animals - not creating reserve")
    if animalid == 0 and not asm3.configuration.movement_person_only_reserves(dbo): 
        raise asm3.utils.ASMValidationError("no animal given, option is off to create person only reserves")
    exq = "SELECT COUNT(*) FROM adoption WHERE AnimalID=? AND OwnerID=? AND ReservationDate Is Not Null " \
        "AND ReservationCancelledDate Is Null AND MovementType=0"
    if dbo.query_int(exq, [animalid, personid]) > 0:
        raise asm3.utils.ASMValidationError("a reservation for this person and animal already exists")
    if reservationdate is None: reservationdate = dbo.now()
    moveids = []
    for aid in asm3.animal.get_animal_id_and_bonds(dbo, animalid):
        move_dict = {
            "person"                : str(personid),
            "animal"                : str(aid),
            "reservationdate"       : asm3.i18n.python2display(l, reservationdate),
            "reservationtime"       : asm3.i18n.format_time(reservationdate),
            "reservationstatus"     : asm3.configuration.default_reservation_status(dbo),
            "movementdate"          : "",
            "type"                  : str(NO_MOVEMENT),
            "returncategory"        : asm3.configuration.default_return_reason(dbo)
        }
        moveids.append(insert_movement_from_form(dbo, username, asm3.utils.PostedData(move_dict, l)))
    return moveids

def insert_reserve_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Inserts a movement from the workflow reserve an animal screen.
    Returns the new movement id
    """
    # Validate that we have a date before doing anthing
    l = dbo.locale
    if None is post.date("reservationdate"):
        raise asm3.utils.ASMValidationError(asm3.i18n._("Reservations must have a valid reservation date.", l))

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
        "returncategory"        : asm3.configuration.default_return_reason(dbo),
        "comments"              : post["comments"]
    }
    move_dict.update(asm3.additional.get_additional_fields_dict(dbo, post, 'movement'))
    movementid = insert_movement_from_form(dbo, username, asm3.utils.PostedData(move_dict, l))
    # Create any payments
    asm3.financial.insert_donations_from_form(dbo, username, post, post["reservationdate"], False, post["person"], post["animal"], movementid) 
    return movementid

def insert_retailer_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Inserts a retailer from the workflow move to retailer screen.
    Returns the new movement id
    """
    # Validate that we have a movement date before doing anthing
    l = dbo.locale
    if None is post.date("retailerdate"):
        raise asm3.utils.ASMValidationError(asm3.i18n._("Retailer movements must have a valid movement date.", l))

    # Is this animal already at a foster? If so, return that foster first
    fm = get_animal_movements(dbo, post.integer("animal"))
    for m in fm:
        if m.MOVEMENTTYPE == FOSTER and m.RETURNDATE is None:
            return_movement(dbo, m.ID, username, post.integer("animal"), post.date("retailerdate"))
    # Create the retailer movement
    move_dict = {
        "person"                : post["person"],
        "animal"                : post["animal"],
        "movementdate"          : post["retailerdate"],
        "adoptionno"            : post["movementnumber"],
        "type"                  : str(RETAILER),
        "donation"              : post["amount"],
        "returncategory"        : asm3.configuration.default_return_reason(dbo),
        "comments"              : post["comments"]
    }
    move_dict.update(asm3.additional.get_additional_fields_dict(dbo, post, 'movement'))
    movementid = insert_movement_from_form(dbo, username, asm3.utils.PostedData(move_dict, l))
    return movementid

def update_movement_donation(dbo: Database, movementid: int) -> None:
    """
    Goes through all donations attached to a particular movement and updates
    the denormalised movement total.
    """
    if asm3.utils.cint(movementid) == 0: return
    dbo.execute("UPDATE adoption SET Donation = " \
        "(SELECT SUM(Donation) FROM ownerdonation WHERE MovementID = ?) WHERE ID = ?", (movementid, movementid))

def insert_transport_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Creates a transport record from posted form data 
    """
    l = dbo.locale
    if post.integer("animal") == 0:
        raise asm3.utils.ASMValidationError(asm3.i18n._("Transport requires an animal", l))
    if None is post.date("pickupdate") or None is post.date("dropoffdate"):
        raise asm3.utils.ASMValidationError(asm3.i18n._("Transports must have valid pickup and dropoff dates and times.", l))
    if post.date("pickupdate") > post.date("dropoffdate"):
        raise asm3.utils.ASMValidationError(asm3.i18n._("Pickup date cannot be later than dropoff date.", l))

    return dbo.insert("animaltransport", {
        "TransportReference":   post["reference"],
        "AnimalID":             post.integer("animal"),
        "TransportTypeID":      post.integer("type"),
        "DriverOwnerID":        post.integer("driver"),
        "PickupOwnerID":        post.integer("pickup"),
        "PickupAddress":        post["pickupaddress"],
        "PickupTown":           post["pickuptown"],
        "PickupCounty":         post["pickupcounty"],
        "PickupPostcode":       post["pickuppostcode"],
        "PickupCountry":        post["pickupcountry"],
        "PickupDateTime":       post.datetime("pickupdate", "pickuptime"),
        "DropoffOwnerID":       post.integer("dropoff"),
        "DropoffAddress":       post["dropoffaddress"],
        "DropoffTown":          post["dropofftown"],
        "DropoffCounty":        post["dropoffcounty"],
        "DropoffPostcode":      post["dropoffpostcode"],
        "DropoffCountry":       post["dropoffcountry"],
        "DropoffDateTime":      post.datetime("dropoffdate", "dropofftime"),
        "Status":               post.integer("status"),
        "Miles":                post.integer("miles"),
        "Cost":                 post.integer("cost"),
        "CostPaidDate":         post.date("costpaid"),
        "Comments":             post["comments"]
    }, username)

def update_transport_from_form(dbo: Database, username: str, post: PostedData) -> None:
    """
    Updates a movement record from posted form data
    """
    l = dbo.locale
    if post.integer("animal") == 0:
        raise asm3.utils.ASMValidationError(asm3.i18n._("Transport requires an animal", l))
    if None is post.date("pickupdate") or None is post.date("dropoffdate"):
        raise asm3.utils.ASMValidationError(asm3.i18n._("Transports must have valid pickup and dropoff dates and times.", l))
    if post.date("pickupdate") > post.date("dropoffdate"):
        raise asm3.utils.ASMValidationError(asm3.i18n._("Pickup date cannot be later than dropoff date.", l))
    transportid = post.integer("transportid")

    dbo.update("animaltransport", transportid, {
        "TransportReference":   post["reference"],
        "AnimalID":             post.integer("animal"),
        "TransportTypeID":      post.integer("type"),
        "DriverOwnerID":        post.integer("driver"),
        "PickupOwnerID":        post.integer("pickup"),
        "PickupAddress":        post["pickupaddress"],
        "PickupTown":           post["pickuptown"],
        "PickupCounty":         post["pickupcounty"],
        "PickupPostcode":       post["pickuppostcode"],
        "PickupCountry":        post["pickupcountry"],
        "PickupDateTime":       post.datetime("pickupdate", "pickuptime"),
        "DropoffOwnerID":       post.integer("dropoff"),
        "DropoffAddress":       post["dropoffaddress"],
        "DropoffTown":          post["dropofftown"],
        "DropoffCounty":        post["dropoffcounty"],
        "DropoffPostcode":      post["dropoffpostcode"],
        "DropoffCountry":       post["dropoffcountry"],
        "DropoffDateTime":      post.datetime("dropoffdate", "dropofftime"),
        "Status":               post.integer("status"),
        "Miles":                post.integer("miles"),
        "Cost":                 post.integer("cost"),
        "CostPaidDate":         post.date("costpaid"),
        "Comments":             post["comments"]
    }, username)

def update_transport_statuses(dbo: Database, username: str, ids: List[int], newstatus: int) -> None:
    """ Updates all transports in list ids to newstatus """
    for i in ids:
        dbo.update("animaltransport", i, { "Status": newstatus }, username)

def delete_transport(dbo: Database, username: str, tid: int) -> None:
    """
    Deletes a transport record
    """
    dbo.delete("animaltransport", tid, username)

def generate_insurance_number(dbo: Database) -> int:
    """
    Returns the next insurance number in the sequence
    """
    ins = asm3.configuration.auto_insurance_next(dbo)
    nextins = ins + 1
    asm3.configuration.auto_insurance_next(dbo, nextins)
    return ins

def auto_cancel_reservations(dbo: Database) -> None:
    """
    Automatically cancels reservations after the daily amount set
    """
    cancelafter = asm3.configuration.auto_cancel_reserves_days(dbo)
    if cancelafter <= 0:
        asm3.al.debug("auto reserve cancel is off.", "movement.auto_cancel_reservations", dbo)
        return
    cancelcutoff = dbo.today(offset=cancelafter*-1)
    asm3.al.debug("cutoff date: reservations < %s" % cancelcutoff, "movement.auto_cancel_reservations", dbo)
    count = dbo.execute("UPDATE adoption SET ReservationCancelledDate = ?, LastChangedDate = ?, LastChangedBy = 'system' " \
        "WHERE MovementDate Is Null AND ReservationCancelledDate Is Null AND " \
        "MovementType = 0 AND ReservationDate < ?", (dbo.today(), dbo.now(), cancelcutoff))
    asm3.al.debug("cancelled %d reservations older than %s days" % (count, cancelafter), "movement.auto_cancel_reservations", dbo)

def send_adoption_checkout(dbo: Database, username: str, post: PostedData) -> None:
    """
    Sets up an adoption checkout cache object and sends the email 
    with the checkout link to the adopter.
    """
    l = dbo.locale
    aid = post.integer("animalid")
    pid = post.integer("personid")
    # Use a hash of animal/person as cache/state key so that it's always the same for
    # the same animal/person.
    # NOTE: we don't check here for an existing cache entry. This means that shelter
    # staff can effectively start the checkout again for the same customer/animal 
    # with a new document to sign and new payment records by sending out a new email. 
    key = asm3.utils.md5_hash_hex("a=%s|p=%s" % (aid, pid))
    a = asm3.animal.get_animal(dbo, aid)
    p = asm3.person.get_person(dbo, pid)
    # template id for paperwork - can be passed or fall back to option
    templateid = post.integer("templateid")
    if templateid == 0: templateid = asm3.configuration.adoption_checkout_templateid(dbo)
    # payment type id for the fee
    feetypeid = post.integer("feetypeid")
    if feetypeid == 0: feetypeid = asm3.configuration.adoption_checkout_feeid(dbo)
    co = {
        "database":     dbo.name(),
        "movementid":   post.integer("id"),
        "templateid":   templateid, 
        "mediaid":      0, # paperwork mediaid, generated in the next step
        "mediacontent": "", # a copy of the generated paperwork with fixed urls for viewing
        "animalid":     post.integer("animalid"),
        "animalname":   a.ANIMALNAME,
        "speciesname":  a.SPECIESNAME,
        "sex":          a.SEXNAME,
        "age":          a.ANIMALAGE,
        "fee":          a.FEE,
        "formatfee":    asm3.i18n.format_currency(l, a.FEE),
        "personid":     post.integer("personid"),
        "personcode":   p.OWNERCODE,
        "personname":   p.OWNERNAME,
        "address":      p.OWNERADDRESS,
        "town":         p.OWNERTOWN,
        "county":       p.OWNERCOUNTY,
        "postcode":     p.OWNERPOSTCODE,
        "email":        p.EMAILADDRESS,
        "giftaid":      p.ISGIFTAID,
        "feetypeid":    feetypeid, 
        "paymentfeeid": 0, # payment for fee, generated in the next step
        "paymentdonid": 0, # payment for donation, generated in the next step
        "receiptnumber": "", # receiptnumber for all payments, generated in next step
        "payref":       "" # payref for the payment processor, generated in next step
    }
    asm3.cachedisk.put(key, dbo.name(), co, 86400 * 2) # persist for 2 days
    # Send the email to the adopter
    body = post["body"]
    url = "%s?account=%s&method=checkout_adoption&token=%s" % (SERVICE_URL, dbo.name(), key)
    body = asm3.utils.replace_url_token(body, url, asm3.i18n._("Adoption Checkout", l))
    asm3.utils.send_email(dbo, post["from"], post["to"], post["cc"], post["bcc"], post["subject"], body, "html")
    # Record that the checkout email was sent in the log
    logtypeid = asm3.configuration.system_log_type(dbo)
    logmsg = "AC01:%s:%s(%s)-->%s(%s)" % (co["movementid"], co["animalname"], co["animalid"], co["personname"], co["personid"])
    asm3.log.add_log(dbo, username, asm3.log.PERSON, co["personid"], logtypeid, logmsg)
    # (this is if checkout was initiated from the movement tab with a custom email)
    if post.boolean("addtolog"):
        asm3.log.add_log_email(dbo, username, asm3.log.PERSON, pid, post.integer("logtype"), 
            post["to"], post["subject"], body)
    if asm3.configuration.audit_on_send_email(dbo): 
        asm3.audit.email(dbo, username, post["from"], post["to"], post["cc"], post["bcc"], post["subject"], body)

def send_movement_emails(dbo: Database, username: str, post: PostedData) -> bool:
    """
    Sends an email to multiple people from a movement book screen. 
    Attaches it as a log entry to the people with IDs listed in personids if specified
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
        for pid in post.integer_list("personids"):
            asm3.log.add_log_email(dbo, username, asm3.log.PERSON, pid, logtype, emailto, subject, body)
    return rv
