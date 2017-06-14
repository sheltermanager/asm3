#!/usr/bin/python

import additional
import al
import animalname
import async
import audit
import configuration
import datetime
import diary
import db
import dbfs
import extension
import financial
import log
import lookups
import media
import movement
import utils
from i18n import _, date_diff, date_diff_days, format_diff, now, today, python2display, subtract_years, subtract_months, add_days, subtract_days, monday_of_week, first_of_month, last_of_month, first_of_year
from random import choice

ASCENDING = 0
DESCENDING = 1

def get_animal_query(dbo):
    """
    Returns a select for animal rows with resolved lookups
    """
    return "SELECT a.*, " \
        "at.AnimalType AS AnimalTypeName, " \
        "ba1.AnimalName AS BondedAnimal1Name, " \
        "ba1.ShelterCode AS BondedAnimal1Code, " \
        "ba1.Archived AS BondedAnimal1Archived, " \
        "ba2.AnimalName AS BondedAnimal2Name, " \
        "ba2.ShelterCode AS BondedAnimal2Code, " \
        "ba2.Archived AS BondedAnimal2Archived, " \
        "bc.BaseColour AS BaseColourName, " \
        "bc.AdoptAPetColour, " \
        "sp.SpeciesName AS SpeciesName, " \
        "sp.PetFinderSpecies, " \
        "bd.BreedName AS BreedName1, "\
        "bd2.BreedName AS BreedName2, "\
        "bd.PetFinderBreed, " \
        "bd2.PetFinderBreed AS PetFinderBreed2, " \
        "ct.CoatType AS CoatTypeName, " \
        "sx.Sex AS SexName, " \
        "sz.Size AS SizeName, " \
        "ov.OwnerName AS OwnersVetName, " \
        "ov.OwnerAddress AS OwnersVetAddress, " \
        "ov.OwnerTown AS OwnersVetTown, " \
        "ov.OwnerCounty AS OwnersVetCounty, " \
        "ov.OwnerPostcode AS OwnersVetPostcode, " \
        "ov.WorkTelephone AS OwnersVetWorkTelephone, " \
        "ov.EmailAddress AS OwnersVetEmailAddress, " \
        "ov.MembershipNumber AS OwnersVetLicenceNumber, " \
        "cv.OwnerName AS CurrentVetName, " \
        "cv.OwnerAddress AS CurrentVetAddress, " \
        "cv.OwnerTown AS CurrentVetTown, " \
        "cv.OwnerCounty AS CurrentVetCounty, " \
        "cv.OwnerPostcode AS CurrentVetPostcode, " \
        "cv.WorkTelephone AS CurrentVetWorkTelephone, " \
        "cv.EmailAddress AS CurrentVetEmailAddress, " \
        "cv.MembershipNumber AS CurrentVetLicenceNumber, " \
        "oo.OwnerName AS OriginalOwnerName, " \
        "oo.OwnerTitle AS OriginalOwnerTitle, " \
        "oo.OwnerInitials AS OriginalOwnerInitials, " \
        "oo.OwnerForeNames AS OriginalOwnerForeNames, " \
        "oo.OwnerSurname AS OriginalOwnerSurname, " \
        "oo.OwnerAddress AS OriginalOwnerAddress, " \
        "oo.OwnerTown AS OriginalOwnerTown, " \
        "oo.OwnerCounty AS OriginalOwnerCounty, " \
        "oo.OwnerPostcode AS OriginalOwnerPostcode, " \
        "oo.HomeTelephone AS OriginalOwnerHomeTelephone, " \
        "oo.WorkTelephone AS OriginalOwnerWorkTelephone, " \
        "oo.MobileTelephone AS OriginalOwnerMobileTelephone, " \
        "oo.EmailAddress AS OriginalOwnerEmailAddress, " \
        "co.ID AS CurrentOwnerID, " \
        "co.OwnerName AS CurrentOwnerName, " \
        "co.OwnerTitle AS CurrentOwnerTitle, " \
        "co.OwnerInitials AS CurrentOwnerInitials, " \
        "co.OwnerForeNames AS CurrentOwnerForeNames, " \
        "co.OwnerSurname AS CurrentOwnerSurname, " \
        "co.OwnerAddress AS CurrentOwnerAddress, " \
        "co.OwnerTown AS CurrentOwnerTown, " \
        "co.OwnerCounty AS CurrentOwnerCounty, " \
        "co.OwnerPostcode AS CurrentOwnerPostcode, " \
        "co.HomeTelephone AS CurrentOwnerHomeTelephone, " \
        "co.WorkTelephone AS CurrentOwnerWorkTelephone, " \
        "co.MobileTelephone AS CurrentOwnerMobileTelephone, " \
        "co.EmailAddress AS CurrentOwnerEmailAddress, " \
        "bo.OwnerName AS BroughtInByOwnerName, " \
        "bo.OwnerAddress AS BroughtInByOwnerAddress, " \
        "bo.OwnerTown AS BroughtInByOwnerTown, " \
        "bo.OwnerCounty AS BroughtInByOwnerCounty, " \
        "bo.OwnerPostcode AS BroughtInByOwnerPostcode, " \
        "bo.HomeTelephone AS BroughtInByHomeTelephone, " \
        "bo.WorkTelephone AS BroughtInByWorkTelephone, " \
        "bo.MobileTelephone AS BroughtInByMobileTelephone, " \
        "bo.EmailAddress AS BroughtInByEmailAddress, " \
        "ro.ID AS ReservedOwnerID, " \
        "ro.OwnerName AS ReservedOwnerName, " \
        "ro.OwnerAddress AS ReservedOwnerAddress, " \
        "ro.OwnerTown AS ReservedOwnerTown, " \
        "ro.OwnerCounty AS ReservedOwnerCounty, " \
        "ro.OwnerPostcode AS ReservedOwnerPostcode, " \
        "ro.HomeTelephone AS ReservedOwnerHomeTelephone, " \
        "ro.WorkTelephone AS ReservedOwnerWorkTelephone, " \
        "ro.MobileTelephone AS ReservedOwnerMobileTelephone, " \
        "ro.EmailAddress AS ReservedOwnerEmailAddress, " \
        "ao.OwnerName AS AdoptionCoordinatorName, " \
        "ao.HomeTelephone AS AdoptionCoordinatorHomeTelephone, " \
        "ao.WorkTelephone AS AdoptionCoordinatorWorkTelephone, " \
        "ao.MobileTelephone AS AdoptionCoordinatorMobileTelephone, " \
        "ao.EmailAddress AS AdoptionCoordinatorEmailAddress, " \
        "ars.StatusName AS ReservationStatusName, " \
        "er.ReasonName AS EntryReasonName, " \
        "dr.ReasonName AS PTSReasonName, " \
        "il.LocationName AS ShelterLocationName, " \
        "il.LocationDescription AS ShelterLocationDescription, " \
        "il.SiteID AS SiteID, " \
        "se.SiteName AS SiteName, " \
        "pl.LocationName AS PickupLocationName, " \
        "ac.ID AS AnimalControlIncidentID, " \
        "itn.IncidentName AS AnimalControlIncidentName, " \
        "ac.IncidentDateTime AS AnimalControlIncidentDate, " \
        "mt.MovementType AS ActiveMovementTypeName, " \
        "am.AdoptionNumber AS ActiveMovementAdoptionNumber, " \
        "am.ReturnDate AS ActiveMovementReturnDate, " \
        "am.InsuranceNumber AS ActiveMovementInsuranceNumber, " \
        "am.ReasonForReturn AS ActiveMovementReasonForReturn, " \
        "am.TrialEndDate AS ActiveMovementTrialEndDate, " \
        "am.Comments AS ActiveMovementComments, " \
        "am.ReservationDate AS ActiveMovementReservationDate, " \
        "am.Donation AS ActiveMovementDonation, " \
        "am.CreatedBy AS ActiveMovementCreatedBy, " \
        "au.RealName AS ActiveMovementCreatedByName, " \
        "am.CreatedDate AS ActiveMovementCreatedDate, " \
        "am.LastChangedBy AS ActiveMovementLastChangedBy, " \
        "am.LastChangedDate AS ActiveMovementLastChangedDate, " \
        "CASE " \
        "WHEN EXISTS(SELECT ItemValue FROM configuration WHERE ItemName Like 'UseShortShelterCodes' AND ItemValue = 'Yes') " \
        "THEN a.ShortCode ELSE a.ShelterCode " \
        "END AS Code, " \
        "CASE " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 1 AND a.HasTrialAdoption = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=11) " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 2 AND a.HasPermanentFoster = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=12) " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType IN (2, 8, 13) THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Not Null THEN " \
        "(SELECT ReasonName FROM deathreason WHERE ID = a.PTSReasonID) " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Null AND a.ActiveMovementID <> 0 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
        "ELSE " \
        "(SELECT LocationName FROM internallocation WHERE ID=a.ShelterLocation) " \
        "END AS DisplayLocationName, " \
        "web.MediaName AS WebsiteMediaName, " \
        "web.Date AS WebsiteMediaDate, " \
        "web.MediaNotes AS WebsiteMediaNotes, " \
        "(SELECT COUNT(*) FROM media mtc WHERE MediaMimeType = 'image/jpeg' AND mtc.LinkTypeID = 0 AND mtc.LinkID = a.ID AND ExcludeFromPublish = 0) AS WebsiteImageCount, " \
        "doc.MediaName AS DocMediaName, " \
        "vid.MediaName AS WebsiteVideoURL, " \
        "vid.MediaNotes AS WebsiteVideoNotes, " \
        "CASE WHEN EXISTS(SELECT ID FROM adoption WHERE AnimalID = a.ID AND MovementType = 1 AND MovementDate > %(today)s) THEN 1 ELSE 0 END AS HasFutureAdoption, " \
        "(SELECT COUNT(*) FROM media WHERE MediaMimeType = 'image/jpeg' AND Date >= %(twodaysago)s AND LinkID = a.ID AND LinkTypeID = 0) AS RecentlyChangedImages, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.NonShelterAnimal) AS NonShelterAnimalName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.CrueltyCase) AS CrueltyCaseName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.CrossBreed) AS CrossBreedName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.EstimatedDOB) AS EstimatedDOBName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.Identichipped) AS IdentichippedName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.Tattoo) AS TattooName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.Neutered) AS NeuteredName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.CombiTested) AS CombiTestedName, " \
        "(SELECT Name FROM lksposneg l WHERE l.ID = a.CombiTestResult) AS CombiTestResultName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.HeartwormTested) AS HeartwormTestedName, " \
        "(SELECT Name FROM lksposneg l WHERE l.ID = a.HeartwormTestResult) AS HeartwormTestResultName, " \
        "(SELECT Name FROM lksposneg l WHERE l.ID = a.FLVResult) AS FLVResultName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.Declawed) AS DeclawedName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.PutToSleep) AS PutToSleepName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.IsDOA) AS IsDOAName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.IsTransfer) AS IsTransferName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.IsPickup) AS IsPickupName, " \
        "(SELECT Name FROM lksynun l WHERE l.ID = a.IsGoodWithChildren) AS IsGoodWithChildrenName, " \
        "(SELECT Name FROM lksynun l WHERE l.ID = a.IsGoodWithCats) AS IsGoodWithCatsName, " \
        "(SELECT Name FROM lksynun l WHERE l.ID = a.IsGoodWithDogs) AS IsGoodWithDogsName, " \
        "(SELECT Name FROM lksynun l WHERE l.ID = a.IsHouseTrained) AS IsHouseTrainedName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.IsNotAvailableForAdoption) AS IsNotAvailableForAdoptionName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.HasSpecialNeeds) AS HasSpecialNeedsName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.DiedOffShelter) AS DiedOffShelterName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.HasActiveReserve) AS HasActiveReserveName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.HasTrialAdoption) AS HasTrialAdoptionName " \
        "FROM animal a " \
        "LEFT OUTER JOIN animal ba1 ON ba1.ID = a.BondedAnimalID " \
        "LEFT OUTER JOIN animal ba2 ON ba2.ID = a.BondedAnimal2ID " \
        "LEFT OUTER JOIN animaltype at ON at.ID = a.AnimalTypeID " \
        "LEFT OUTER JOIN basecolour bc ON bc.ID = a.BaseColourID " \
        "LEFT OUTER JOIN species sp ON sp.ID = a.SpeciesID " \
        "LEFT OUTER JOIN lksex sx ON sx.ID = a.Sex " \
        "LEFT OUTER JOIN lksize sz ON sz.ID = a.Size " \
        "LEFT OUTER JOIN entryreason er ON er.ID = a.EntryReasonID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN site se ON se.ID = il.SiteID " \
        "LEFT OUTER JOIN pickuplocation pl ON pl.ID = a.PickupLocationID " \
        "LEFT OUTER JOIN media web ON web.LinkID = a.ID AND web.LinkTypeID = 0 AND web.WebsitePhoto = 1 " \
        "LEFT OUTER JOIN media vid ON vid.LinkID = a.ID AND vid.LinkTypeID = 0 AND vid.WebsiteVideo = 1 " \
        "LEFT OUTER JOIN media doc ON doc.LinkID = a.ID AND doc.LinkTypeID = 0 AND doc.DocPhoto = 1 " \
        "LEFT OUTER JOIN breed bd ON bd.ID = a.BreedID " \
        "LEFT OUTER JOIN breed bd2 ON bd2.ID = a.Breed2ID " \
        "LEFT OUTER JOIN lkcoattype ct ON ct.ID = a.CoatType " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "LEFT OUTER JOIN lksmovementtype mt ON mt.ID = a.ActiveMovementType " \
        "LEFT OUTER JOIN owner ov ON ov.ID = a.OwnersVetID " \
        "LEFT OUTER JOIN owner cv ON cv.ID = a.CurrentVetID " \
        "LEFT OUTER JOIN owner oo ON oo.ID = a.OriginalOwnerID " \
        "LEFT OUTER JOIN owner bo ON bo.ID = a.BroughtInByOwnerID " \
        "LEFT OUTER JOIN owner ao ON ao.ID = a.AdoptionCoordinatorID " \
        "LEFT OUTER JOIN adoption am ON am.ID = a.ActiveMovementID " \
        "LEFT OUTER JOIN users au ON au.UserName = am.CreatedBy " \
        "LEFT OUTER JOIN owner co ON co.ID = am.OwnerID " \
        "LEFT OUTER JOIN animalcontrolanimal aca ON aca.AnimalControlID = (SELECT MAX(saca.AnimalControlID) FROM animalcontrolanimal saca WHERE saca.AnimalID = a.ID) " \
        "LEFT OUTER JOIN animalcontrol ac ON ac.ID = aca.AnimalControlID " \
        "LEFT OUTER JOIN incidenttype itn ON itn.ID = ac.IncidentTypeID " \
        "LEFT OUTER JOIN adoption ar ON ar.AnimalID = a.ID AND ar.MovementType = 0 AND ar.MovementDate Is Null AND ar.ReservationDate Is Not Null AND ar.ReservationCancelledDate Is Null AND ar.ID = (SELECT MAX(sar.ID) FROM adoption sar WHERE sar.AnimalID = a.ID AND sar.MovementType = 0 AND sar.MovementDate Is Null AND sar.ReservationDate Is Not Null AND sar.ReservationCancelledDate Is Null) " \
        "LEFT OUTER JOIN reservationstatus ars ON ars.ID = ar.ReservationStatusID " \
        "LEFT OUTER JOIN owner ro ON ro.ID = ar.OwnerID" % {
            "today": db.dd(now(dbo.timezone)),
            "twodaysago":  db.dd(subtract_days(now(dbo.timezone), 2))
        }

def get_animal_status_query(dbo):
    return "SELECT a.ID, a.ShelterCode, a.ShortCode, a.AnimalName, a.DeceasedDate, a.DiedOffShelter, a.PutToSleep, " \
        "dr.ReasonName AS PTSReasonName, " \
        "il.LocationName AS ShelterLocationName, " \
        "a.ShelterLocationUnit, " \
        "a.NonShelterAnimal, a.DateBroughtIn, a.Archived, " \
        "a.ActiveMovementID, a.ActiveMovementDate, a.ActiveMovementType, a.ActiveMovementReturn, " \
        "a.HasActiveReserve, a.HasTrialAdoption, a.HasPermanentFoster, a.MostRecentEntryDate, a.DisplayLocation " \
        "FROM animal a " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation "

def get_animal_movement_status_query(dbo):
    return "SELECT m.ID, m.MovementType, m.MovementDate, m.ReturnDate, " \
        "mt.MovementType AS MovementTypeName, " \
        "m.ReservationDate, m.ReservationCancelledDate, m.IsTrial, m.IsPermanentFoster, " \
        "m.AnimalID, m.OwnerID, o.OwnerName " \
        "FROM adoption m " \
        "INNER JOIN lksmovementtype mt ON mt.ID = m.MovementType " \
        "LEFT OUTER JOIN owner o ON m.OwnerID = o.ID "

def get_animal(dbo, animalid):
    """
    Returns a complete animal row by id, or None if not found
    (int) animalid: The animal to get
    """
    if animalid is None or animalid == 0: return None
    rows = dbo.query(get_animal_query(dbo) + " WHERE a.ID = ?", [animalid])
    if rows is None or len(rows) == 0:
        return None
    else:
        return rows[0]

def get_animal_sheltercode(dbo, code):
    """
    Returns a complete animal row by ShelterCode
    """
    if code is None or code == "": return None
    rows = db.query(dbo, get_animal_query(dbo) + " WHERE a.ShelterCode = ?", [code])
    if rows is None or len(rows) == 0:
        return None
    else:
        return rows[0]

def get_animals_ids(dbo, sort, q, limit = 5, cachetime = 60):
    """
    Given a recordset of animal IDs, goes and gets the
    full records.
    The idea is that we write the simplest possible animal queries to get the
    ID before feeding the list of IDs into the full animal_query. This performs
    a lot better than doing the full SELECT with ORDER BY/LIMIT
    """
    init = dbo.query(q, limit=limit)
    aids = []
    for aid in init:
        aids.append(str(aid["ID"]))
    if len(aids) == 0: return aids # Return empty set if no results
    return dbo.query_cache(get_animal_query(dbo) + " WHERE a.ID IN (%s) ORDER BY %s" % (dbo.sql_placeholders(aids), sort), aids, age=cachetime)

def get_animals_brief(animals):
    """
    For any method that returns a list of animals from the get_animal_query 
    selector, this will strip them down and return shorter records for passing
    as json to things like search, shelterview and animal links screens.
    """
    r = []
    for a in animals:
        r.append({ 
            "ACTIVEMOVEMENTID": a["ACTIVEMOVEMENTID"],
            "ACTIVEMOVEMENTTYPE": a["ACTIVEMOVEMENTTYPE"],
            "ADDITIONALFLAGS": a["ADDITIONALFLAGS"],
            "ADOPTIONCOORDINATORID": a["ADOPTIONCOORDINATORID"],
            "ADOPTIONCOORDINATORNAME": a["ADOPTIONCOORDINATORNAME"],
            "AGEGROUP": a["AGEGROUP"],
            "ANIMALCOMMENTS": a["ANIMALCOMMENTS"],
            "ANIMALAGE": a["ANIMALAGE"],
            "ANIMALNAME" : a["ANIMALNAME"],
            "ANIMALTYPENAME" : a["ANIMALTYPENAME"],
            "ARCHIVED" : a["ARCHIVED"],
            "BONDEDANIMALID": a["BONDEDANIMALID"],
            "BONDEDANIMAL2ID": a["BONDEDANIMAL2ID"],
            "BREEDNAME": a["BREEDNAME"],
            "CODE": a["CODE"],
            "COMBITESTED": a["COMBITESTED"],
            "COMBITESTRESULT": a["COMBITESTRESULT"],
            "CRUELTYCASE": a["CRUELTYCASE"],
            "CURRENTOWNERID": a["CURRENTOWNERID"],
            "CURRENTOWNERNAME": a["CURRENTOWNERNAME"],
            "DATEOFBIRTH": a["DATEOFBIRTH"],
            "DAYSONSHELTER": a["DAYSONSHELTER"],
            "DECEASEDDATE": a["DECEASEDDATE"],
            "DISPLAYLOCATIONNAME": a["DISPLAYLOCATIONNAME"],
            "ENTRYREASONNAME": a["ENTRYREASONNAME"],
            "FLVRESULT": a["FLVRESULT"],
            "HASACTIVERESERVE": a["HASACTIVERESERVE"],
            "HASFUTUREADOPTION": a["HASFUTUREADOPTION"],
            "HASSPECIALNEEDS": a["HASSPECIALNEEDS"],
            "HASTRIALADOPTION": a["HASTRIALADOPTION"],
            "HASPERMANENTFOSTER": a["HASPERMANENTFOSTER"],
            "HEARTWORMTESTED": a["HEARTWORMTESTED"],
            "HEARTWORMTESTRESULT": a["HEARTWORMTESTRESULT"],
            "HIDDENANIMALDETAILS": a["HIDDENANIMALDETAILS"],
            "HOLDUNTILDATE": a["HOLDUNTILDATE"],
            "ID": a["ID"], 
            "IDENTICHIPPED": a["IDENTICHIPPED"],
            "ISHOLD": a["ISHOLD"],
            "ISNOTAVAILABLEFORADOPTION": a["ISNOTAVAILABLEFORADOPTION"],
            "ISPICKUP": a["ISPICKUP"], 
            "ISQUARANTINE": a["ISQUARANTINE"],
            "LASTCHANGEDDATE": a["LASTCHANGEDDATE"],
            "LASTCHANGEDBY": a["LASTCHANGEDBY"],
            "MARKINGS": a["MARKINGS"],
            "MOSTRECENTENTRYDATE" : a["MOSTRECENTENTRYDATE"],
            "NEUTERED" : a["NEUTERED"],
            "NONSHELTERANIMAL": a["NONSHELTERANIMAL"],
            "ORIGINALOWNERID": a["ORIGINALOWNERID"],
            "ORIGINALOWNERNAME": a["ORIGINALOWNERNAME"],
            "PICKUPLOCATIONNAME": a["PICKUPLOCATIONNAME"],
            "SEX" : a["SEX"],
            "SEXNAME" : a["SEXNAME"],
            "SHELTERCODE" : a["SHELTERCODE"],
            "SHELTERLOCATION": a["SHELTERLOCATION"],
            "SHELTERLOCATIONNAME": a["SHELTERLOCATIONNAME"],
            "SHELTERLOCATIONUNIT": a["SHELTERLOCATIONUNIT"],
            "SHORTCODE": a["SHORTCODE"],
            "SPECIESID": a["SPECIESID"],
            "SPECIESNAME": a["SPECIESNAME"],
            "WEBSITEMEDIANAME": a["WEBSITEMEDIANAME"],
            "WEBSITEMEDIADATE": a["WEBSITEMEDIADATE"],
            "WEBSITEMEDIANOTES": a["WEBSITEMEDIANOTES"] 
        })
    return r

def get_animal_find_simple(dbo, query, classfilter = "all", limit = 0, locationfilter = "", siteid = 0):
    """
    Returns rows for simple animal searches.
    query: The search criteria
    classfilter: all, shelter, female
    locationfilter: IN clause of locations to search
    """
    # If no query has been given and we have a filter of shelter or all, 
    # do an on-shelter search instead
    if query == "" and (classfilter == "all" or classfilter == "shelter"):
        locationfilter = get_location_filter_clause(locationfilter=locationfilter, tablequalifier="a", siteid=siteid, andprefix=True)
        sql = "%s WHERE a.Archived=0 %s ORDER BY a.AnimalName" % (get_animal_query(dbo), locationfilter)
        return dbo.query(sql, limit=limit)
    ors = []
    values = []
    query = query.replace("'", "`")
    querylike = "%%%s%%" % query.lower()
    def add(field):
        ors.append("LOWER(%s) LIKE ?" % field)
        values.append(querylike)
    def addclause(clause):
        ors.append(clause)
        values.append(querylike)
    add("a.AnimalName")
    add("a.ShelterCode")
    add("a.ShortCode")
    add("a.AcceptanceNumber")
    add("a.BreedName")
    add("a.IdentichipNumber")
    add("a.TattooNumber")
    add("a.RabiesTag")
    add("il.LocationName")
    add("a.ShelterLocationUnit")
    add("a.PickupAddress")
    addclause("EXISTS(SELECT ad.Value FROM additional ad " \
        "INNER JOIN additionalfield af ON af.ID = ad.AdditionalFieldID AND af.Searchable = 1 " \
        "WHERE ad.LinkID=a.ID AND ad.LinkType IN (%s) AND LOWER(ad.Value) LIKE ?)" % additional.ANIMAL_IN)
    if not dbo.is_large_db: 
        add("a.Markings")
        add("a.HiddenAnimalDetails")
        add("a.AnimalComments")
        add("a.ReasonNO")
        add("a.HealthProblems")
        add("a.PTSReason")
        add("oo.OwnerName")
        add("oo.OwnerAddress")
        add("oo.HomeTelephone")
        add("oo.WorkTelephone")
        add("oo.MobileTelephone")
        add("co.OwnerName")
        add("co.OwnerAddress")
        add("co.HomeTelephone")
        add("co.WorkTelephone")
        add("co.MobileTelephone")
        add("bo.OwnerName")
        add("bo.OwnerAddress")
        add("bo.HomeTelephone")
        add("bo.WorkTelephone")
        add("bo.MobileTelephone")
        add("ro.OwnerName")
        add("ro.OwnerAddress")
        add("ro.HomeTelephone")
        add("ro.WorkTelephone")
        add("ro.MobileTelephone")
        add("cv.OwnerName")
        add("cv.OwnerAddress")
        add("cv.WorkTelephone")
        add("at.AnimalType")
        add("sp.SpeciesName")
        add("sx.Sex")
        add("sz.Size")
        add("bc.BaseColour")
        add("ct.CoatType")
    if classfilter == "shelter":
        classfilter = "a.Archived = 0 AND "
    elif classfilter == "female":
        classfilter = "a.Sex = 0 AND "
    else:
        classfilter = ""
    sql = "%s WHERE %s %s (%s) ORDER BY a.Archived, a.AnimalName" % ( \
        get_animal_query(dbo),
        classfilter,
        get_location_filter_clause(locationfilter=locationfilter, tablequalifier="a", siteid=siteid, andsuffix=True),
        " OR ".join(ors))
    return dbo.query(sql, values, limit=limit)

def get_animal_find_advanced(dbo, criteria, limit = 0, locationfilter = "", siteid = 0):
    """
    Returns rows for advanced animal searches.
    criteria: A dictionary of criteria
       animalname - string partial pattern
       sheltercode - string partial pattern
       createdby - string partial pattern
       litterid - string partial pattern
       animaltypeid - -1 for all or ID
       breedid - -1 for all or ID
       speciesid - -1 for all or ID
       shelterlocation - -1 for all internal locations or ID
       size - -1 for all sizes or ID
       colour - -1 for all colours or ID
       comments - string partial pattern
       sex - -1 for all sexes or ID
       hasactivereserve - "both" "reserved" "unreserved"
       logicallocation - "all" "onshelter" "adoptable" "adopted" 
            "fostered" "permanentfoster" "transferred" "escaped" "stolen" "releasedtowild" 
            "reclaimed" "retailer" "deceased", "hold", "quarantine"
       inbetweenfrom - date string in current locale display format
       inbetweento - date string in current locale display format
       features - partial word/string match
       outbetweenfrom - date string in current locale display format
       outbetweento - date string in current locale display format
       adoptionno - string partial pattern
       agedbetweenfrom - string containing floating point number
       agedbetweento - string containing floating point number
       agegroup - contains an agegroup name
       microchip - string partial pattern
       insuranceno - string partial pattern
       rabiestag - string partial pattern
       pickupaddress - string partial pattern
       hiddencomments - partial word/string pattern
       originalowner - string partial pattern
       medianotes - partial word/string pattern
       filter - one or more of:
           showtransfersonly
           showpickupsonly
           showspecialneedsonly
           goodwithchildren
           goodwithcats
           goodwithdogs
           housetrained
           fivplus
           flvplus
           heartwormplus
        flag - one or more of (plus custom):
            courtesy
            crueltycase
            nonshelter
            notforadoption
            quarantine
    locationfilter: IN clause of locations to search
    """
    ands = []
    values = []
    l = dbo.locale
    post = utils.PostedData(criteria, l)

    def addid(cfield, field): 
        if post.integer(cfield) > 0: 
            ands.append("%s = ?" % field)
            values.append(post.integer(cfield))

    def addidpair(cfield, field, field2): 
        if post.integer(cfield) > 0: 
            ands.append("(%s = ? OR %s = ?)" % (field, field2))
            values.append(post.integer(cfield))
            values.append(post.integer(cfield))

    def addstr(cfield, field): 
        if post[cfield] != "":
            x = post[cfield].lower().replace("'", "`")
            x = "%%%s%%" % x
            ands.append("(LOWER(%s) LIKE ? OR LOWER(%s) LIKE ?)" % (field, field))
            values.append(x)
            values.append(utils.decode_html(x))

    def adddate(cfieldfrom, cfieldto, field): 
        if post[cfieldfrom] != "" and post[cfieldto] != "":
            post.data["dayend"] = "23:59:59"
            ands.append("%s >= ? AND %s <= ?" % (field, field))
            values.append(post.date(cfieldfrom))
            values.append(post.datetime(cfieldto, "dayend"))

    def addfilter(f, condition):
        if post["filter"].find(f) != -1: ands.append(condition)

    def addcomp(cfield, value, condition):
        if post[cfield] == value: ands.append(condition)

    def addwords(cfield, field):
        if post[cfield] != "":
            words = post[cfield].split(" ")
            for w in words:
                x = w.lower().replace("'", "`")
                ands.append("(LOWER(%s) LIKE ? OR LOWER(%s) LIKE ?)" % (field, field))
                values.append(x)
                values.append(utils.decode_html(x))

    addstr("animalname", "a.AnimalName")
    addid("animaltypeid", "a.AnimalTypeID")
    addid("speciesid", "a.SpeciesID")
    addidpair("breedid", "a.BreedID", "a.Breed2ID")
    addid("shelterlocation", "a.ShelterLocation")
    # If we have a location filter and no location has been given, use the filter
    if locationfilter != "" and post.integer("shelterlocation") == -1:
        ands.append(get_location_filter_clause(locationfilter=locationfilter, tablequalifier="a", siteid=siteid))
    addstr("microchip", "a.IdentichipNumber")
    addstr("rabiestag", "a.RabiesTag")
    addstr("pickupaddress", "a.PickupAddress")
    addid("sex", "a.Sex")
    addid("size", "a.Size")
    addid("colour", "a.BaseColourID")
    addstr("sheltercode", "a.ShelterCode")
    addstr("litterid", "a.AcceptanceNumber")
    adddate("inbetweenfrom", "inbetweento", "a.MostRecentEntryDate")
    addfilter("goodwithchildren", "a.IsGoodWithChildren = 0")
    addfilter("goodwithdogs", "a.IsGoodWithDogs = 0")
    addfilter("goodwithcats", "a.IsGoodWithCats = 0")
    addfilter("housetrained", "a.IsHouseTrained = 0")
    addfilter("showtransfersonly", "a.IsTransfer = 1")
    addfilter("showpickupsonly", "a.IsPickup = 1")
    addfilter("showspecialneedsonly", "a.HasSpecialNeeds = 1")
    addfilter("fivplus", "a.CombiTested = 1 AND a.CombiTestResult = 2")
    addfilter("flvplus", "a.CombiTested = 1 AND a.FLVResult = 2")
    addfilter("heartwormplus", "a.HeartwormTested = 1 AND a.HeartwormTestResult = 2")
    addwords("comments", "a.AnimalComments")
    addwords("hiddencomments", "a.HiddenAnimalDetails")
    addwords("features", "a.Markings")
    addstr("originalowner", "oo.OwnerName")
    if post.integer("agegroup") != -1:
        addstr("agegroup", "a.AgeGroup")
    adddate("outbetweenfrom", "outbetweento", "a.ActiveMovementDate")
    addwords("medianotes", "web.MediaNotes")
    addstr("createdby", "a.CreatedBy")

    if post["agedbetweenfrom"] != "" and post["agedbetweento"] != "":
        ands.append("a.DateOfBirth >= ? AND a.DateOfBirth <= ?")
        values.append(subtract_years(now(), post.floating("agedbetweento")))
        values.append(subtract_years(now(), post.floating("agedbetweenfrom")))

    if post["insuranceno"] != "":
        ands.append("EXISTS (SELECT InsuranceNumber FROM adoption WHERE " \
            "LOWER(InsuranceNumber) LIKE ? AND AnimalID = a.ID)")
        values.append( "%%%s%%" % post["insuranceno"] )

    if post["adoptionno"] != "":
        ands.append("EXISTS (SELECT AdoptionNumber FROM adoption WHERE " \
            "LOWER(AdoptionNumber) LIKE ? AND AnimalID = a.ID)")
        values.append( "%%%s%%" % post["adoptionno"] )

    addcomp("reserved", "reserved", "a.HasActiveReserve = 1")
    addcomp("reserved", "unreserved", "a.HasActiveReserve = 0")
    addcomp("logicallocation", "onshelter", "a.Archived = 0")
    addcomp("logicallocation", "adoptable", "a.Archived = 0 AND a.IsNotAvailableForAdoption = 0 AND a.HasTrialAdoption = 0")
    addcomp("logicallocation", "reserved", "a.Archived = 0 AND a.HasActiveReserve = 1 AND a.HasTrialAdoption = 0")
    addcomp("logicallocation", "hold", "a.IsHold = 1 AND a.Archived = 0")
    addcomp("logicallocation", "fostered", "a.ActiveMovementType = %d" % movement.FOSTER)
    addcomp("logicallocation", "permanentfoster", "a.ActiveMovementType = %d AND a.HasPermanentFoster = 1" % movement.FOSTER)
    addcomp("logicallocation", "adopted", "a.ActiveMovementType = %d" % movement.ADOPTION)
    addcomp("logicallocation", "transferred", "a.ActiveMovementType = %d" % movement.TRANSFER)
    addcomp("logicallocation", "escaped", "a.ActiveMovementType = %d" % movement.ESCAPED)
    addcomp("logicallocation", "stolen", "a.ActiveMovementType = %d" % movement.STOLEN)
    addcomp("logicallocation", "releasedtowild", "a.ActiveMovementType = %d" % movement.RELEASED)
    addcomp("logicallocation", "reclaimed", "a.ActiveMovementType = %d" % movement.RECLAIMED)
    addcomp("logicallocation", "retailer", "a.ActiveMovementType = %d" % movement.RETAILER)
    addcomp("logicallocation", "deceased", "a.DeceasedDate Is Not Null")
    if post["flags"] != "":
        for flag in post["flags"].split(","):
            if flag == "courtesy": ands.append("a.IsCourtesy=1")
            elif flag == "crueltycase": ands.append("a.CrueltyCase=1")
            elif flag == "nonshelter": ands.append("a.NonShelterAnimal=1")
            elif flag == "notforadoption": ands.append("a.IsNotAvailableForAdoption=1")
            elif flag == "quarantine": ands.append("a.IsQuarantine=1")
            else: 
                ands.append("LOWER(a.AdditionalFlags) LIKE ?")
                values.append("%%%s%%" % flag.lower())
    where = ""
    if len(ands) > 0:
        where = "WHERE " + " AND ".join(ands)
    sql = "%s %s ORDER BY a.AnimalName" % (get_animal_query(dbo), where)
    return dbo.query(sql, values, limit=limit)

def get_animals_not_for_adoption(dbo):
    """
    Returns all shelter animals who have the not for adoption flag set
    """
    return dbo.query(get_animal_query(dbo) + " WHERE a.IsNotAvailableForAdoption = 1 AND a.Archived = 0")

def get_animals_not_microchipped(dbo):
    """
    Returns all shelter animals who have not been microchipped
    """
    return dbo.query(get_animal_query(dbo) + " WHERE a.Identichipped = 0 AND a.Archived = 0")

def get_animals_hold(dbo):
    """
    Returns all shelter animals who have the hold flag set
    """
    return dbo.query(get_animal_query(dbo) + " WHERE a.IsHold = 1 AND a.Archived = 0")

def get_animals_hold_today(dbo):
    """
    Returns all shelter animals who have the hold flag set and the hold ends today
    """
    return dbo.query(get_animal_query(dbo) + " WHERE a.IsHold = 1 AND a.HoldUntilDate = ? AND a.Archived = 0", [dbo.now()])

def get_animals_long_term(dbo):
    """
    Returns all shelter animals who have been on the shelter for 6 months or more
    """
    return dbo.query("%s WHERE a.DaysOnShelter > ? AND a.Archived = 0" % get_animal_query(dbo), [configuration.long_term_months(dbo) * 30])

def get_animals_quarantine(dbo):
    """
    Returns all shelter animals who have the quarantine flag set
    """
    return dbo.query(get_animal_query(dbo) + " WHERE a.IsQuarantine = 1 AND a.Archived = 0")

def get_animals_recently_deceased(dbo):
    """
    Returns all shelter animals who are recently deceased
    """
    recent = subtract_days(now(), 30)
    return dbo.query(get_animal_query(dbo) + " " \
        "WHERE a.DeceasedDate Is Not Null " \
        "AND (a.ActiveMovementType Is Null OR a.ActiveMovementType = 0 " \
        "OR a.ActiveMovementType = 2) " \
        "AND a.DeceasedDate > ?", [recent])

def get_alerts(dbo, locationfilter = "", siteid = 0):
    """
    Returns the alert totals for the main screen.
    """
    futuremonth = db.dd(add_days(now(dbo.timezone), 31))
    oneyear = db.dd(subtract_days(now(dbo.timezone), 365))
    onemonth = db.dd(subtract_days(now(dbo.timezone), 31))
    oneweek = db.dd(subtract_days(now(dbo.timezone), 7))
    today = db.dd(now(dbo.timezone))
    endoftoday = now(dbo.timezone)
    endoftoday = db.ddt(endoftoday.replace(hour = 23, minute = 59, second = 59))
    locationfilter = get_location_filter_clause(locationfilter=locationfilter, siteid=siteid, andprefix=True)
    shelterfilter = ""
    if not configuration.include_off_shelter_medical(dbo):
        shelterfilter = " AND (Archived = 0 OR ActiveMovementType = 2)"
    sql = "SELECT " \
        "(SELECT COUNT(*) FROM animalvaccination INNER JOIN animal ON animal.ID = animalvaccination.AnimalID " \
            "LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation WHERE " \
            "DateOfVaccination Is Null AND DeceasedDate Is Null %(shelterfilter)s AND " \
            "DateRequired  >= %(oneyear)s AND DateRequired <= %(today)s %(locfilter)s) AS duevacc," \
        "(SELECT COUNT(*) FROM animalvaccination av1 INNER JOIN animal ON animal.ID = av1.AnimalID " \
            "LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation WHERE " \
            "av1.DateOfVaccination Is Not Null AND DeceasedDate Is Null %(shelterfilter)s AND " \
            "av1.DateExpires  >= %(oneyear)s AND av1.DateExpires <= %(today)s %(locfilter)s AND " \
            "0 = (SELECT COUNT(*) FROM animalvaccination av2 WHERE av2.AnimalID = av1.AnimalID AND " \
            "av2.ID <> av1.ID AND av2.DateRequired >= av1.DateOfVaccination AND av2.VaccinationID = av1.VaccinationID)) AS expvacc," \
        "(SELECT COUNT(*) FROM animaltest INNER JOIN animal ON animal.ID = animaltest.AnimalID " \
            "LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation WHERE " \
            "DateOfTest Is Null AND DeceasedDate Is Null %(shelterfilter)s AND " \
            "DateRequired >= %(oneyear)s AND DateRequired <= %(today)s %(locfilter)s) AS duetest," \
        "(SELECT COUNT(*) FROM animalmedicaltreatment INNER JOIN animal ON animal.ID = animalmedicaltreatment.AnimalID " \
            "INNER JOIN animalmedical ON animalmedicaltreatment.AnimalMedicalID = animalmedical.ID " \
            "LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation WHERE " \
            "DateGiven Is Null AND DeceasedDate Is Null %(shelterfilter)s AND " \
            "Status = 0 AND DateRequired  >= %(oneyear)s AND DateRequired <= %(today)s %(locfilter)s) AS duemed," \
        "(SELECT COUNT(*) FROM animalwaitinglist INNER JOIN owner ON owner.ID = animalwaitinglist.OwnerID " \
            "WHERE Urgency = 1 AND DateRemovedFromList Is Null) AS urgentwl," \
        "(SELECT COUNT(*) FROM adoption INNER JOIN owner ON owner.ID = adoption.OwnerID WHERE " \
            "MovementType = 0 AND ReservationDate Is Not Null AND ReservationCancelledDate Is Null AND IDCheck = 0) AS rsvhck," \
        "(SELECT COUNT(DISTINCT OwnerID) FROM ownerdonation WHERE DateDue <= %(today)s AND Date Is Null) AS duedon," \
        "(SELECT COUNT(*) FROM adoption WHERE IsTrial = 1 AND ReturnDate Is Null AND MovementType = 1 AND TrialEndDate <= %(oneweek)s) AS endtrial," \
        "(SELECT COUNT(*) FROM adoption INNER JOIN animal ON adoption.AnimalID = animal.ID WHERE " \
            "Archived = 0 AND DeceasedDate Is Null AND ReservationDate Is Not Null AND ReservationDate <= %(oneweek)s " \
            "AND ReservationCancelledDate Is Null AND MovementType = 0 AND MovementDate Is Null) AS longrsv," \
        "(SELECT COUNT(*) FROM animal LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation " \
            "WHERE Neutered = 0 AND ActiveMovementType = 1 AND " \
            "ActiveMovementDate > %(onemonth)s %(locfilter)s) AS notneu," \
        "(SELECT COUNT(*) FROM animal LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation " \
            "WHERE Identichipped = 0 AND Archived = 0 %(locfilter)s) AS notchip, " \
        "(SELECT COUNT(*) FROM animal LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation " \
            "WHERE Archived = 0 AND IsNotAvailableForAdoption = 1 %(locfilter)s) AS notadopt, " \
        "(SELECT COUNT(*) FROM animal WHERE Archived = 0 AND IsHold = 1 AND HoldUntilDate = %(today)s) AS holdtoday, " \
        "(SELECT COUNT(DISTINCT CollationID) FROM onlineformincoming) AS inform, " \
        "(SELECT COUNT(*) FROM ownercitation WHERE FineDueDate Is Not Null AND FineDueDate <= %(today)s AND FinePaidDate Is Null) AS acunfine, " \
        "(SELECT COUNT(*) FROM animalcontrol WHERE CompletedDate Is Null AND DispatchDateTime Is Null AND CallDateTime Is Not Null) AS acundisp, " \
        "(SELECT COUNT(*) FROM animalcontrol WHERE CompletedDate Is Null) AS acuncomp, " \
        "(SELECT COUNT(*) FROM animalcontrol WHERE (" \
            "(FollowupDateTime Is Not Null AND FollowupDateTime <= %(endoftoday)s AND NOT FollowupComplete = 1) OR " \
            "(FollowupDateTime2 Is Not Null AND FollowupDateTime2 <= %(endoftoday)s AND NOT FollowupComplete2 = 1) OR " \
            "(FollowupDateTime3 Is Not Null AND FollowupDateTime3 <= %(endoftoday)s) AND NOT FollowupComplete3 = 1)) AS acfoll, " \
        "(SELECT COUNT(*) FROM ownertraploan WHERE ReturnDueDate Is Not Null AND ReturnDueDate <= %(today)s AND ReturnDate Is Null) AS tlover, " \
        "(SELECT COUNT(*) FROM stocklevel WHERE Balance > 0 AND Expiry Is Not Null AND Expiry > %(today)s AND Expiry <= %(futuremonth)s) AS stexpsoon, " \
        "(SELECT COUNT(*) FROM stocklevel WHERE Balance > 0 AND Expiry Is Not Null AND Expiry <= %(today)s) AS stexp, " \
        "(SELECT COUNT(*) FROM animaltransport WHERE (DriverOwnerID = 0 OR DriverOwnerID Is Null) AND Status < 10) AS trnodrv, " \
        "(SELECT COUNT(*) FROM animal WHERE Archived = 0 AND DaysOnShelter > 182) AS lngterm, " \
        "(SELECT SUM(Alerts) FROM publishlog WHERE PublishDateTime >= %(today)s) AS publish " \
        "FROM lksmovementtype WHERE ID=1" \
            % { "today": today, "endoftoday": endoftoday, "oneweek": oneweek, "oneyear": oneyear, "onemonth": onemonth, 
                "futuremonth": futuremonth, "locfilter": locationfilter, "shelterfilter": shelterfilter }
    return dbo.query_cache(sql, age=120)

def get_stats(dbo):
    """
    Returns the stats figures for the main screen.
    """
    statperiod = configuration.show_stats_home_page(dbo)
    statdate = now(dbo.timezone) # defaulting to today
    if statperiod == "thisweek": statdate = monday_of_week(statdate)
    if statperiod == "thismonth": statdate = first_of_month(statdate)
    if statperiod == "thisyear": statdate = first_of_year(statdate)
    if statperiod == "alltime": statdate = datetime.datetime(1900, 1, 1)
    countfrom = db.dd(statdate)
    return dbo.query_named_params("SELECT " \
        "(SELECT COUNT(*) FROM animal WHERE NonShelterAnimal = 0 AND DateBroughtIn >= :from) AS Entered," \
        "(SELECT COUNT(*) FROM adoption WHERE MovementDate >= :from AND MovementType = :adoption) AS Adopted," \
        "(SELECT COUNT(*) FROM adoption WHERE MovementDate >= :from AND MovementType = :reclaimed) AS Reclaimed, " \
        "(SELECT COUNT(*) FROM adoption WHERE MovementDate >= :from AND MovementType = :transfer) AS Transferred, " \
        "(SELECT COUNT(*) FROM animal WHERE NonShelterAnimal = 0 AND DiedOffShelter = 0 AND DeceasedDate >= :from AND PutToSleep = 1) AS PTS, " \
        "(SELECT COUNT(*) FROM animal WHERE NonShelterAnimal = 0 AND DiedOffShelter = 0 AND DeceasedDate >= :from AND PutToSleep = 0 AND IsDOA = 0) AS Died, " \
        "(SELECT COUNT(*) FROM animal WHERE NonShelterAnimal = 0 AND DiedOffShelter = 0 AND DeceasedDate >= :from AND PutToSleep = 0 AND IsDOA = 1) AS DOA, " \
        "(SELECT SUM(Donation) FROM ownerdonation WHERE Date >= :from) AS Donations, " \
        "(SELECT SUM(CostAmount) FROM animalcost WHERE CostDate >= :from) + " \
            "(SELECT SUM(Cost) FROM animalvaccination WHERE DateOfVaccination >= :from) + " \
            "(SELECT SUM(Cost) FROM animaltest WHERE DateOfTest >= :from) + " \
            "(SELECT SUM(Cost) FROM animalmedical WHERE StartDate >= :from) + " \
            "(SELECT SUM(Cost) FROM animaltransport WHERE PickupDateTime >= :from) AS Costs " \
        "FROM lksmovementtype WHERE ID=1", 
        { "from": countfrom, "adoption": movement.ADOPTION, "reclaimed": movement.RECLAIMED, "transfer": movement.TRANSFER },
        age=120)

def embellish_timeline(l, rows):
    """
    Adds human readable description and icon fields to rows from get_timeline
    """
    td = { "ENTERED": ( _("{0} {1}: entered the shelter", l), "animal" ),
          "MICROCHIP": ( _("{0} {1}: microchipped", l), "microchip" ),
          "NEUTERED": ( _("{0} {1}: altered", l), "health" ),
          "RESERVED": ( _("{0} {1}: reserved by {2}", l), "reservation" ),
          "ADOPTED": ( _("{0} {1}: adopted by {2}", l), "movement" ),
          "FOSTERED": ( _("{0} {1}: fostered to {2}", l), "movement" ),
          "TRANSFER": ( _("{0} {1}: transferred to {2}", l), "movement" ),
          "ESCAPED": ( _("{0} {1}: escaped", l), "movement" ),
          "STOLEN": ( _("{0} {1}: stolen", l), "movement" ),
          "RELEASED": (_("{0} {1}: released", l) , "movement" ),
          "RECLAIMED": ( _("{0} {1}: reclaimed by {2}", l), "movement" ),
          "RETAILER": ( _("{0} {1}: sent to retailer {2}", l), "movement" ),
          "RETURNED": ( _("{0} {1}: returned by {2}", l), "movement" ),
          "DIED": ( _("{0} {1}: died ({2})", l), "death" ),
          "EUTHANISED": ( _("{0} {1}: euthanised ({2})", l), "death" ),
          "FIVP": ( _("{0} {1}: tested positive for FIV", l), "positivetest" ),
          "FLVP": ( _("{0} {1}: tested positive for FeLV", l), "positivetest" ),
          "HWP": ( _("{0} {1}: tested positive for Heartworm", l), "positivetest" ),
          "QUARANTINE": ( _("{0} {1}: quarantined", l), "quarantine" ),
          "HOLD": ( _("{0} {1}: held", l), "hold" ),
          "NOTADOPT": ( _("{0} {1}: not available for adoption", l), "notforadoption" ),
          "AVAILABLE": ( _("{0} {1}: available for adoption", l), "notforadoption" ),
          "VACC": ( _("{0} {1}: received {2}", l), "vaccination" ),
          "TEST": ( _("{0} {1}: received {2}", l), "test" ),
          "MEDICAL": ( _("{0} {1}: received {2}", l), "medical" ),
          "INCIDENTOPEN": ( _("{0}: opened {1}", l), "call" ),
          "INCIDENTCLOSE": ( _("{0}: closed {1} ({2})", l), "call" ),
          "LOST": ( _("{2}: lost in {1}: {0}", l), "animal-lost" ),
          "FOUND": ( _("{2}: found in {1}: {0}", l), "animal-found" ),
          "WAITINGLIST": ( _("{0}: waiting list - {1}", l), "waitinglist" )
    }
    for r in rows:
        desc, icon = td[r["CATEGORY"]]
        desc = desc.format(r["TEXT1"], r["TEXT2"], r["TEXT3"])
        r["ICON"] = icon
        r["DESCRIPTION"] = desc
    return rows

def get_timeline(dbo, limit = 500):
    """
    Returns a list of recent events at the shelter.
    """
    sql = "SELECT * FROM (" \
        "(SELECT 'animal' AS LinkTarget, 'ENTERED' AS Category, DateBroughtIn AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 " \
            "ORDER BY DateBroughtIn DESC, ID %(limit)s) " \
        "UNION ALL (SELECT 'animal' AS LinkTarget, 'MICROCHIP' AS Category, IdentichipDate AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND IdentichipDate Is Not Null " \
            "ORDER BY IdentichipDate DESC, ID %(limit)s) " \
        "UNION ALL (SELECT 'animal' AS LinkTarget, 'NEUTERED' AS Category, NeuteredDate AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND NeuteredDate Is Not Null " \
            "ORDER BY NeuteredDate DESC, ID %(limit)s) " \
        "UNION ALL (SELECT 'animal_movements' AS LinkTarget, 'RESERVED' AS Category, ReservationDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, owner.OwnerName AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "INNER JOIN owner ON adoption.OwnerID = owner.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Null AND ReservationDate Is Not Null " \
            "ORDER BY ReservationDate DESC, animal.ID %(limit)s) " \
        "UNION ALL (SELECT 'animal_movements' AS LinkTarget, 'ADOPTED' AS Category, MovementDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, owner.OwnerName AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "INNER JOIN owner ON adoption.OwnerID = owner.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND MovementType = 1 " \
            "ORDER BY MovementDate DESC, animal.ID %(limit)s) " \
        "UNION ALL (SELECT 'animal_movements' AS LinkTarget, 'FOSTERED' AS Category, MovementDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, owner.OwnerName AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "INNER JOIN owner ON adoption.OwnerID = owner.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND MovementType = 2 " \
            "ORDER BY MovementDate DESC, animal.ID %(limit)s) " \
        "UNION ALL (SELECT 'animal_movements' AS LinkTarget, 'TRANSFER' AS Category, MovementDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, owner.OwnerName AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "INNER JOIN owner ON adoption.OwnerID = owner.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND MovementType = 3 " \
            "ORDER BY MovementDate DESC, animal.ID %(limit)s) " \
        "UNION ALL (SELECT 'animal_movements' AS LinkTarget, 'ESCAPED' AS Category, MovementDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND MovementType = 4 " \
            "ORDER BY MovementDate DESC, animal.ID %(limit)s) " \
        "UNION ALL (SELECT 'animal_movements' AS LinkTarget, 'RECLAIMED' AS Category, MovementDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, owner.OwnerName AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "INNER JOIN owner ON adoption.OwnerID = owner.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND MovementType = 5 " \
            "ORDER BY MovementDate DESC, animal.ID %(limit)s) " \
        "UNION ALL (SELECT 'animal_movements' AS LinkTarget, 'STOLEN' AS Category, MovementDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND MovementType = 6 " \
            "ORDER BY MovementDate DESC, animal.ID %(limit)s) " \
        "UNION ALL (SELECT 'animal_movements' AS LinkTarget, 'RELEASED' AS Category, MovementDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND MovementType = 7 " \
            "ORDER BY MovementDate DESC, animal.ID %(limit)s) " \
        "UNION ALL (SELECT 'animal_movements' AS LinkTarget, 'RETAILER' AS Category, MovementDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, owner.OwnerName AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "INNER JOIN owner ON adoption.OwnerID = owner.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND MovementType = 8 " \
            "ORDER BY MovementDate DESC, animal.ID %(limit)s) " \
        "UNION ALL (SELECT 'animal_movements' AS LinkTarget, 'RETURNED' AS Category, ReturnDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, owner.OwnerName AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "LEFT OUTER JOIN owner ON adoption.OwnerID = owner.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND ReturnDate Is Not Null " \
            "ORDER BY ReturnDate DESC, animal.ID %(limit)s) " \
        "UNION ALL (SELECT 'animal' AS LinkTarget, 'DIED' AS Category, DeceasedDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, ReasonName AS Text3, animal.LastChangedBy FROM animal " \
            "INNER JOIN deathreason ON animal.PTSReasonID = deathreason.ID " \
            "WHERE NonShelterAnimal = 0 AND DiedOffShelter = 0 AND PutToSleep = 0 AND DeceasedDate Is Not Null " \
            "ORDER BY DeceasedDate DESC, animal.ID %(limit)s) " \
        "UNION ALL (SELECT 'animal' AS LinkTarget, 'EUTHANISED' AS Category, DeceasedDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, ReasonName AS Text3, animal.LastChangedBy FROM animal " \
            "INNER JOIN deathreason ON animal.PTSReasonID = deathreason.ID " \
            "WHERE NonShelterAnimal = 0 AND DiedOffShelter = 0 AND PutToSleep = 1 AND DeceasedDate Is Not Null " \
            "ORDER BY DeceasedDate DESC, animal.ID %(limit)s) " \
        "UNION ALL (SELECT 'animal' AS LinkTarget, 'FIVP' AS Category, CombiTestDate AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND CombiTested = 1 AND CombiTestDate Is Not Null AND CombiTestResult = 2 " \
            "ORDER BY CombiTestDate DESC, ID %(limit)s) " \
        "UNION ALL (SELECT 'animal' AS LinkTarget, 'FLVP' AS Category, CombiTestDate AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND CombiTested = 1 AND CombiTestDate Is Not Null AND FLVResult = 2 " \
            "ORDER BY CombiTestDate DESC, ID %(limit)s) " \
        "UNION ALL (SELECT 'animal' AS LinkTarget, 'HWP' AS Category, CombiTestDate AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND HeartwormTested = 1 AND HeartwormTestDate Is Not Null AND HeartwormTestResult = 2 " \
            "ORDER BY HeartwormTestDate DESC, ID %(limit)s) " \
        "UNION ALL (SELECT 'animal' AS LinkTarget, 'QUARANTINE' AS Category, LastChangedDate AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND IsQuarantine = 1 " \
            "ORDER BY LastChangedDate DESC, ID %(limit)s) " \
        "UNION ALL (SELECT 'animal' AS LinkTarget, 'HOLD' AS Category, DateBroughtIn AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND IsHold = 1 " \
            "ORDER BY DateBroughtIn DESC, ID %(limit)s) " \
        "UNION ALL (SELECT 'animal' AS LinkTarget, 'NOTADOPT' AS Category, DateBroughtIn AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND IsNotAvailableForAdoption = 1 " \
            "ORDER BY DateBroughtIn DESC, ID %(limit)s) " \
        "UNION ALL (SELECT 'animal' AS LinkTarget, 'AVAILABLE' AS Category, ActiveMovementReturn AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND ActiveMovementReturn Is Not Null AND IsNotAvailableForAdoption = 0 " \
            "ORDER BY ActiveMovementReturn DESC, ID %(limit)s) " \
        "UNION ALL (SELECT 'animal_vaccination' AS LinkTarget, 'VACC' AS Category, DateOfVaccination AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, VaccinationType AS Text3, animalvaccination.LastChangedBy FROM animal " \
            "INNER JOIN animalvaccination ON animalvaccination.AnimalID = animal.ID " \
            "INNER JOIN vaccinationtype ON vaccinationtype.ID = animalvaccination.VaccinationID " \
            "WHERE NonShelterAnimal = 0 AND DateOfVaccination Is Not Null " \
            "ORDER BY DateOfVaccination DESC, animal.ID %(limit)s) " \
        "UNION ALL (SELECT 'animal_test' AS LinkTarget, 'TEST' AS Category, DateOfTest AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, TestName AS Text3, animaltest.LastChangedBy FROM animal " \
            "INNER JOIN animaltest ON animaltest.AnimalID = animal.ID " \
            "INNER JOIN testtype ON testtype.ID = animaltest.TestTypeID " \
            "WHERE NonShelterAnimal = 0 AND DateOfTest Is Not Null " \
            "ORDER BY DateOfTest DESC, animal.ID %(limit)s) " \
        "UNION ALL (SELECT 'animal_medical' AS LinkTarget, 'MEDICAL' AS Category, DateGiven AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, TreatmentName AS Text3, animalmedicaltreatment.LastChangedBy FROM animal " \
            "INNER JOIN animalmedicaltreatment ON animalmedicaltreatment.AnimalID = animal.ID " \
            "INNER JOIN animalmedical ON animalmedicaltreatment.AnimalMedicalID = animalmedical.ID " \
            "WHERE NonShelterAnimal = 0 AND DateGiven Is Not Null " \
            "ORDER BY DateGiven DESC, animal.ID %(limit)s) " \
        "UNION ALL (SELECT 'incident' AS LinkTarget, 'INCIDENTOPEN' AS Category, IncidentDateTime AS EventDate, animalcontrol.ID, " \
            "IncidentName AS Text1, DispatchAddress AS Text2, '' AS Text3, LastChangedBy FROM animalcontrol " \
            "INNER JOIN incidenttype ON incidenttype.ID = animalcontrol.IncidentTypeID " \
            "ORDER BY IncidentDateTime DESC, animalcontrol.ID %(limit)s) " \
        "UNION ALL (SELECT 'incident' AS LinkTarget, 'INCIDENTCLOSE' AS Category, CompletedDate AS EventDate, animalcontrol.ID, " \
            "IncidentName AS Text1, DispatchAddress AS Text2, CompletedName AS Text3, LastChangedBy FROM animalcontrol " \
            "INNER JOIN incidenttype ON incidenttype.ID = animalcontrol.IncidentTypeID " \
            "INNER JOIN incidentcompleted ON incidentcompleted.ID = animalcontrol.IncidentCompletedID " \
            "ORDER BY CompletedDate DESC, animalcontrol.ID %(limit)s) " \
        "UNION ALL (SELECT 'lostanimal' AS LinkTarget, 'LOST' AS Category, DateLost AS EventDate, animallost.ID, " \
            "DistFeat AS Text1, AreaLost AS Text2, SpeciesName AS Text3, LastChangedBy FROM animallost " \
            "INNER JOIN species ON animallost.AnimalTypeID = species.ID " \
            "ORDER BY DateLost DESC, animallost.ID %(limit)s) " \
        "UNION ALL (SELECT 'foundanimal' AS LinkTarget, 'FOUND' AS Category, DateFound AS EventDate, animalfound.ID, " \
            "DistFeat AS Text1, AreaFound AS Text2, SpeciesName AS Text3, LastChangedBy FROM animalfound " \
            "INNER JOIN species ON animalfound.AnimalTypeID = species.ID " \
            "ORDER BY DateFound DESC, animalfound.ID %(limit)s) " \
        "UNION ALL (SELECT 'waitinglist' AS LinkTarget, 'WAITINGLIST' AS Category, DatePutOnList AS EventDate, animalwaitinglist.ID, " \
            "AnimalDescription AS Text1, lkurgency.Urgency AS Text2, '' AS Text3, LastChangedBy FROM animalwaitinglist " \
            "INNER JOIN lkurgency ON lkurgency.ID = animalwaitinglist.Urgency " \
            "ORDER BY DatePutOnList DESC, animalwaitinglist.ID %(limit)s) " \
        ") dummy " \
        "WHERE EventDate <= ? " \
        "ORDER BY EventDate DESC, ID " \
        "%(limit)s" % { "limit": dbo.sql_limit(limit) }
    if dbo.dbtype == "SQLITE":
        # SQLITE can't support the subquery LIMIT clauses and breaks, give SQLite users
        # a simpler timeline with just entering animals
        sql = "SELECT 'animal' AS LinkTarget, 'ENTERED' AS Category, DateBroughtIn AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND DateBroughtIn <= ? " \
            "ORDER BY DateBroughtIn DESC, ID %(limit)s" % \
            { "limit": dbo.sql_limit(limit) }
    return embellish_timeline(dbo.locale, dbo.query_cache(sql, [dbo.now()], age=120))

def calc_time_on_shelter(dbo, animalid, a = None):
    """
    Returns the length of time the animal has been on the shelter as a 
    formatted string, eg: "6 weeks and 3 days"
    (int) animalid: The animal to calculate time on shelter for
    """
    l = dbo.locale
    return format_diff(l, calc_days_on_shelter(dbo, animalid, a))

def calc_total_time_on_shelter(dbo, animalid, a = None, movements = None):
    """
    Returns the length of time the animal has been on the shelter as a 
    formatted string, eg: "6 weeks and 3 days"
    (int) animalid: The animal to calculate time on shelter for
    """
    l = dbo.locale
    return format_diff(l, calc_total_days_on_shelter(dbo, animalid, a, movements))

def calc_days_on_shelter(dbo, animalid, a = None):
    """
    Returns the number of days an animal has been on the shelter as an int
    (int) animalid: The animal to get the number of days on shelter for
    """
    stop = now()
    if a is None:
        a = db.query(dbo, "SELECT Archived, MostRecentEntryDate, DeceasedDate, DiedOffShelter, ActiveMovementDate FROM animal WHERE ID = %d" % animalid)
        if len(a) == 0: return
        a = a[0]

    mre = a["MOSTRECENTENTRYDATE"] 

    # If the animal is dead, or has left the shelter
    # use that date as our cutoff instead
    if a["DECEASEDDATE"] is not None and a["DIEDOFFSHELTER"] == 0:
        stop = a["DECEASEDDATE"]
    elif a["ACTIVEMOVEMENTDATE"] is not None and a["ARCHIVED"] == 1:
        stop = a["ACTIVEMOVEMENTDATE"]

    return date_diff_days(mre, stop)

def calc_total_days_on_shelter(dbo, animalid, a = None, movements = None):
    """
    Returns the total number of days an animal has been on the shelter (counting all stays) as an int
    (int) animalid: The animal to get the number of days on shelter for
    a: The animal already loaded, needs Archived, DateBroughtIn, DeceasedDate, ActiveMovementDate
    movements: A list of movements that includes MovementDate and ReturnDate for this (and possibly other) animal(s) ordered by animalid
    """
    stop = now()
    if a is None:
        a = db.query(dbo, "SELECT Archived, DateBroughtIn, DeceasedDate, DiedOffShelter, ActiveMovementDate FROM animal WHERE ID = %d" % animalid)
        if len(a) == 0: return 0
        a = a[0]

    start = a["DATEBROUGHTIN"]

    # If the animal is dead, or is off the shelter
    # use that date as our final date instead
    if a["DECEASEDDATE"] is not None and a["DIEDOFFSHELTER"] == 0:
        stop = a["DECEASEDDATE"]
    elif a["ACTIVEMOVEMENTDATE"] is not None and a["ARCHIVED"] == 1:
        stop = a["ACTIVEMOVEMENTDATE"]
    daysonshelter = date_diff_days(start, stop)

    # Now, go through historic movements for this animal and deduct
    # all the time the animal has been off the shelter
    if movements is None:
        movements = db.query(dbo, "SELECT AnimalID, MovementDate, ReturnDate " \
            "FROM adoption " \
            "WHERE AnimalID = %d AND MovementType <> 2 " \
            "AND MovementDate Is Not Null AND ReturnDate Is Not Null " \
            "ORDER BY AnimalID" % animalid)
    seen = False
    for m in movements:
        if m["ANIMALID"] == animalid:
            seen = True
            if m["MOVEMENTDATE"] is not None and m["RETURNDATE"] is not None:
                daysonshelter -= date_diff_days(m["MOVEMENTDATE"], m["RETURNDATE"])
        else:
            # Stop iterating the list if we don't have a match and we previously
            # saw our animal id. Any movement list passed in should order by animalid
            if seen:
                break

    return daysonshelter

def calc_age_group(dbo, animalid, a = None, bands = None):
    """
    Returns the age group the animal fits into based on its
    date of birth.
    (int) animalid: The animal to calculate the age group for
    """
    def bv(item, bands):
        for b in bands:
            if b["ITEMNAME"] == item:
                return b["ITEMVALUE"]
        return ""
    # Calculate animal's age in days
    dob = None
    if a is None:
        dob = get_date_of_birth(dbo, animalid)
    else:
        dob = a["DATEOFBIRTH"]
    days = date_diff_days(dob, now())
    # Load age group bands if they weren't passed
    if bands is None:
        bands = db.query(dbo, "SELECT ItemName, ItemValue FROM configuration WHERE ItemName LIKE 'AgeGroup%' ORDER BY ItemName")
    # Loop through the bands until we find one that the age in days fits into
    for i in range(0, 20):
        band = bv("AgeGroup%d" % i, bands)
        years = utils.cfloat(band)
        if days <= years * 365:
            return bv("AgeGroup%dName" % i, bands)
    # Out of bands and none matched
    return ""

def calc_age(dbo, animalid, a = None):
    """
    Returns an animal's age as a readable string
     (int) animalid: The animal to calculate time on shelter for
    """
    l = dbo.locale
    dob = None
    deceased = None
    if a is not None:
        dob = a["DATEOFBIRTH"]
        deceased = a["DECEASEDDATE"]
    else:
        dob = get_date_of_birth(dbo, animalid)
        deceased = get_deceased_date(dbo, animalid)
    stop = now()

    # If the animal is dead, stop there
    if deceased is not None:
        stop = deceased

    # Format it as time period
    return date_diff(l, dob, stop)

def calc_shelter_code(dbo, animaltypeid, entryreasonid, speciesid, datebroughtin):
    """
    Creates a new shelter code using the configured format
    animaltypeid: The integer animal type id to use when creating the code
    datebroughtin: The date the animal was brought in as a python date
    Returns a tuple of sheltercode, shortcode, unique and year for an animal record
    Format tokens include:
        T - First char of animal type
        TT - First two chars of animal type
        E - First char of entry category
        EE - First two chars of entry category
        S - First char of species
        SS - First two chars of species
        YYYY - 4 digit brought in year
        YY - 2 digit brought in year
        MM - 2 digit brought in month
        DD - 2 digit brought in day
        UUUUUUUUUU - 10 digit padded code for next animal of all time
        UUUU - 4 digit padded code for next animal of all time
        XXX - 3 digit padded code for next animal for year
        XX - unpadded code for next animal for year
        NNN - 3 digit padded code for next animal of type for year
        NN - unpadded code for next animal of type for year
    """
    al.debug("sheltercode: generating for type %d, entry %d, species %d, datebroughtin %s" % \
        (int(animaltypeid), int(entryreasonid), int(speciesid), datebroughtin),
        "animal.calc_shelter_code", dbo)

    def clean_lookup(s):
        """ Removes whitespace and punctuation from the beginning of a lookup name """
        s = s.replace("(", "").replace("[", "").replace("{", "")
        s = s.replace(".", "").replace(",", "").replace("!", "")
        s = s.replace("\"", "").replace("'", "").replace("`", "")
        s = s.strip()
        return s

    def substitute_tokens(fmt, year, tyear, ever, datebroughtin, animaltype, species, entryreason):
        code = fmt
        code = code.replace("YYYY", "%04d" % datebroughtin.year)
        code = code.replace("YY", "%02d" % (int(datebroughtin.year) - 2000))
        code = code.replace("MM", "%02d" % datebroughtin.month)
        code = code.replace("DD", "%02d" % datebroughtin.day)
        code = code.replace("UUUUUUUUUU", "%010d" % ever)
        code = code.replace("UUUU", "%04d" % ever)
        code = code.replace("NNN", "%03d" % tyear)
        code = code.replace("NN", str(tyear))
        code = code.replace("XXX", "%03d" % year)
        code = code.replace("XX", str(year))
        # The following tokens all substitute to letters that could
        # then be substituted themselves - wrap delimiters around
        # those tokens before substituting them so that doesn't happen
        code = code.replace("TT", "{YY}")
        code = code.replace("T", "{T}")
        code = code.replace("SS", "{PP}")
        code = code.replace("S", "{S}")
        code = code.replace("EE", "{NN}")
        code = code.replace("E", "{E}")
        code = code.replace("{YY}", utils.substring(animaltype, 0, 2))
        code = code.replace("{T}", utils.substring(animaltype, 0, 1))
        code = code.replace("{PP}", utils.substring(species, 0, 2))
        code = code.replace("{S}", utils.substring(species, 0, 1))
        code = code.replace("{NN}", utils.substring(entryreason, 0, 2))
        code = code.replace("{E}", utils.substring(entryreason, 0, 1))
        return code

    if datebroughtin is None:
        datebroughtin = now()

    codeformat = configuration.coding_format(dbo)
    shortformat = configuration.coding_format_short(dbo)
    animaltype = clean_lookup(lookups.get_animaltype_name(dbo, animaltypeid))
    entryreason = clean_lookup(lookups.get_entryreason_name(dbo, entryreasonid))
    species = clean_lookup(lookups.get_species_name(dbo, speciesid))
    beginningofyear = datetime.datetime(datebroughtin.year, 1, 1, 0, 0, 0)
    endofyear = datetime.datetime(datebroughtin.year, 12, 31, 23, 59, 59)
    oneyearago = subtract_years(now(), 1.0)
    highesttyear = 0
    highestyear = 0
    highestever = 0

    # If our code uses N, calculate the highest code seen for this type this year
    if codeformat.find("N") != -1 or shortformat.find("N") != -1:
        highesttyear = dbo.query_int("SELECT MAX(YearCodeID) FROM animal WHERE " \
            "DateBroughtIn >= ? AND " \
            "DateBroughtIn <= ? AND " \
            "AnimalTypeID = ?", ( beginningofyear, endofyear, animaltypeid))
        highesttyear += 1

    # If our code uses X, calculate the highest code seen this year
    if codeformat.find("X") != -1 or shortformat.find("X") != -1:
        highestyear = dbo.query_int("SELECT COUNT(ID) FROM animal WHERE " \
            "DateBroughtIn >= ? AND " \
            "DateBroughtIn <= ?", (beginningofyear, endofyear))
        highestyear += 1

    # If our code uses U, calculate the highest code ever seen
    if codeformat.find("U") != -1 or shortformat.find("U") != -1:
        highestever = dbo.query_int("SELECT MAX(UniqueCodeID) FROM animal WHERE " \
            "CreatedDate >= ?", [oneyearago])
        highestever += 1

    unique = False
    code = ""
    shortcode = ""
    while not unique:

        # Generate the codes
        code = substitute_tokens(codeformat, highestyear, highesttyear, highestever, datebroughtin, animaltype, species, entryreason)
        shortcode = substitute_tokens(shortformat, highestyear, highesttyear, highestever, datebroughtin, animaltype, species, entryreason)

        # Verify the code is unique
        unique = 0 == dbo.query_int("SELECT COUNT(*) FROM animal WHERE ShelterCode LIKE ?", [code])

        # If it's not, increment and try again
        if not unique:
            if codeformat.find("U") != -1: highestever += 1
            if codeformat.find("N") != -1: highesttyear += 1
            if codeformat.find("X") != -1: highestyear += 1

    al.debug("sheltercode: code=%s, short=%s for type %s, entry %s, species %s, datebroughtin %s" % \
        (code, shortcode, animaltype, entryreason, species, datebroughtin),
        "animal.calc_shelter_code", dbo)
    return (code, shortcode, highestever, highesttyear)

def get_is_on_shelter(dbo, animalid):
    """
    Returns true if the animal is on shelter
    """
    return 0 == db.query_int(dbo, "SELECT Archived FROM animal WHERE ID = %d" % animalid)

def get_comments(dbo, animalid):
    """
    Returns an animal's comments
    (int) animalid: The animal to get the comments from
    """
    return db.query_string(dbo, "SELECT AnimalComments FROM animal WHERE ID = %d" % animalid)

def get_date_of_birth(dbo, animalid):
    """
    Returns an animal's date of birth
    (int) animalid: The animal to get the dob
    """
    return db.query_date(dbo, "SELECT DateOfBirth FROM animal WHERE ID = %d" % animalid)

def get_days_on_shelter(dbo, animalid):
    """
    Returns the number of days on the shelter
    """
    return dbo.query_int("SELECT DaysOnShelter FROM animal WHERE ID = ?", [animalid])

def get_daily_boarding_cost(dbo, animalid):
    """
    Returns the daily boarding cost
    """
    return dbo.query_int("SELECT DailyBoardingCost FROM animal WHERE ID = ?", [animalid])

def get_deceased_date(dbo, animalid):
    """
    Returns an animal's deceased date
    (int) animalid: The animal to get the deceased date
    """
    return dbo.query_date("SELECT DeceasedDate FROM animal WHERE ID = ?", [animalid])

def get_date_brought_in(dbo, animalid):
    """
    Returns the date an animal was brought in
    (int) animalid: The animal to get the brought in date from
    """
    return dbo.query_date("SELECT DateBroughtIn FROM animal WHERE ID = ?", [animalid])

def get_code(dbo, animalid):
    """
    Returns the appropriate animal code for display
    """
    rv = ""
    if configuration.use_short_shelter_codes(dbo):
        rv = get_short_code(dbo, animalid)
    else:
        rv = get_shelter_code(dbo, animalid)
    return rv

def get_short_code(dbo, animalid):
    """
    Returns the short code for animalid
    """
    return dbo.query_string("SELECT ShortCode FROM animal WHERE ID = ?", [animalid])

def get_shelter_code(dbo, animalid):
    """
    Returns the shelter code for animalid
    """
    return dbo.query_string("SELECT ShelterCode FROM animal WHERE ID = ?", [animalid])

def get_animal_namecode(dbo, animalid):
    """
    Returns an animal's name and code or an empty
    string if the id is not valid.
    """
    r = dbo.query("SELECT AnimalName, ShelterCode, ShortCode " \
        "FROM animal WHERE ID = ?", [animalid])
    if len(r) == 0:
        return ""
    if configuration.use_short_shelter_codes(dbo):
        rv = "%s - %s" % (r[0]["SHORTCODE"], r[0]["ANIMALNAME"])
    else:
        rv = "%s - %s" % (r[0]["SHELTERCODE"], r[0]["ANIMALNAME"])
    return rv

def get_animals_namecode(dbo):
    """
    Returns a resultset containing the ID, name and code
    of all animals.
    """
    return dbo.query("SELECT ID, AnimalName, ShelterCode, ShortCode " \
        "FROM animal ORDER BY AnimalName, ShelterCode")

def get_animals_on_shelter_namecode(dbo):
    """
    Returns a resultset containing the ID, name and code
    of all on shelter animals.
    """
    return dbo.query("SELECT animal.ID, AnimalName, ShelterCode, ShortCode, SpeciesName, " \
        "CASE WHEN EXISTS(SELECT ItemValue FROM configuration WHERE ItemName Like 'UseShortShelterCodes' AND ItemValue = 'Yes') " \
        "THEN ShortCode ELSE ShelterCode END AS Code " \
        "FROM animal " \
        "LEFT OUTER JOIN species ON species.ID = animal.SpeciesID " \
        "WHERE Archived = 0 ORDER BY AnimalName, ShelterCode")

def get_animals_on_shelter_foster_namecode(dbo):
    """
    Returns a resultset containing the ID, name and code
    of all on shelter and foster animals.
    """
    return dbo.query("SELECT animal.ID, AnimalName, ShelterCode, ShortCode, SpeciesName, " \
        "CASE WHEN EXISTS(SELECT ItemValue FROM configuration WHERE ItemName Like 'UseShortShelterCodes' AND ItemValue = 'Yes') " \
        "THEN ShortCode ELSE ShelterCode END AS Code " \
        "FROM animal " \
        "LEFT OUTER JOIN species ON species.ID = animal.SpeciesID " \
        "WHERE (Archived = 0 OR ActiveMovementType = 2) ORDER BY AnimalName, ShelterCode")

def get_breedname(dbo, breed1id, breed2id):
    """
    Returns the name of a breed from the primary and secondary breed
    breed1id: The first breed
    breed2id: The second breed
    """
    if breed1id == 0: return ""
    if breed1id == breed2id or breed2id == 0:
        return lookups.get_breed_name(dbo, breed1id)
    return lookups.get_breed_name(dbo, breed1id) + "/" + lookups.get_breed_name(dbo, breed2id)

def get_costs(dbo, animalid, sort = ASCENDING):
    """
    Returns cost records for the given animal:
    COSTTYPEID, COSTTYPENAME, COSTDATE, DESCRIPTION
    """
    sql = "SELECT a.ID, a.CostTypeID, a.CostAmount, a.CostDate, a.CostPaidDate, c.CostTypeName, a.Description, " \
        "a.CreatedBy, a.CreatedDate, a.LastChangedBy, a.LastChangedDate " \
        "FROM animalcost a INNER JOIN costtype c ON c.ID = a.CostTypeID " \
        "WHERE a.AnimalID = ?"
    if sort == ASCENDING:
        sql += " ORDER BY a.CostDate"
    else:
        sql += " ORDER BY a.CostDate DESC"
    return dbo.query(sql, [animalid])

def get_cost_totals(dbo, animalid):
    """
    Returns a resultset containing totals of all cost values for an animal.
    DAILYBOARDINGCOST, DAYSONSHELTER, TV, TM, TC, TD
    """
    q = "SELECT DailyBoardingCost, DaysOnShelter, " \
        "(SELECT SUM(Cost) FROM animalvaccination WHERE AnimalID = animal.ID AND DateOfVaccination Is Not Null) AS tv, " \
        "(SELECT SUM(Cost) FROM animaltest WHERE AnimalID = animal.ID AND DateOfTest Is Not Null) AS tt, " \
        "(SELECT SUM(Cost) FROM animalmedical WHERE AnimalID = animal.ID) AS tm, " \
        "(SELECT SUM(Cost) FROM animaltransport WHERE AnimalID = animal.ID) AS tr, " \
        "(SELECT SUM(CostAmount) FROM animalcost WHERE AnimalID = animal.ID) AS tc, " \
        "(SELECT SUM(Donation) FROM ownerdonation WHERE AnimalID = animal.ID) AS td " \
        "FROM animal WHERE ID = ?"
    return dbo.query(q, [animalid])[0]

def get_diets(dbo, animalid, sort = ASCENDING):
    """
    Returns diet records for the given animal:
    DIETNAME, DIETDESCRIPTION, DATESTARTED, COMMENTS
    """
    sql = "SELECT a.ID, a.DietID, d.DietName, d.DietDescription, a.DateStarted, a.Comments, " \
        "a.CreatedBy, a.CreatedDate, a.LastChangedBy, a.LastChangedDate " \
        "FROM animaldiet a INNER JOIN diet d ON d.ID = a.DietID " \
        "WHERE a.AnimalID = ?"
    if sort == ASCENDING:
        sql += " ORDER BY a.DateStarted"
    else:
        sql += " ORDER BY a.DateStarted DESC"
    return dbo.query(sql, [animalid] )

def get_display_location(dbo, animalid):
    """ Returns an animal's current display location """
    return dbo.query_string("SELECT DisplayLocation FROM animal WHERE ID = ?", [animalid])

def get_display_location_noq(dbo, animalid, loc = ""):
    """ Returns an animal's current display location without
        the :: qualifier if present 
        animalid: The animal id
        loc:      The display location if the caller can supply it
    """
    if loc == "":
        loc = dbo.query_string("SELECT DisplayLocation FROM animal WHERE ID = ?", [animalid])
    if loc is None:
        return ""
    if loc.find("::") != -1:
        loc = loc[0:loc.find("::")]
    return loc

def get_has_animals(dbo):
    """
    Returns True if there is at least one animal in the database
    """
    return dbo.query_int("SELECT COUNT(ID) FROM animal") > 0

def get_has_animal_on_shelter(dbo):
    """
    Returns True if there is at least one animal on the shelter
    """
    return dbo.query_int("SELECT COUNT(ID) FROM animal a WHERE a.Archived = 0") > 0

def get_links_recently_adopted(dbo, limit = 5, locationfilter = "", siteid = 0):
    """
    Returns link info for animals who were recently adopted
    """
    locationfilter = get_location_filter_clause(locationfilter=locationfilter, siteid=siteid, andprefix=True)
    return get_animals_ids(dbo, "a.ActiveMovementDate DESC", "SELECT animal.ID FROM animal LEFT OUTER JOIN internallocation il ON il.ID = ShelterLocation WHERE ActiveMovementType = 1 %s ORDER BY ActiveMovementDate DESC" % locationfilter, limit=limit, cachetime=120)

def get_links_recently_fostered(dbo, limit = 5, locationfilter = "", siteid = 0):
    """
    Returns link info for animals who were recently fostered
    """
    locationfilter = get_location_filter_clause(locationfilter=locationfilter, siteid=siteid, andprefix=True)
    return get_animals_ids(dbo, "a.ActiveMovementDate DESC", "SELECT animal.ID FROM animal LEFT OUTER JOIN internallocation il ON il.ID = ShelterLocation WHERE ActiveMovementType = 2 %s ORDER BY ActiveMovementDate DESC" % locationfilter, limit=limit, cachetime=120)

def get_links_recently_changed(dbo, limit = 5, locationfilter = "", siteid = 0):
    """
    Returns link info for animals who have recently been changed.
    """
    locationfilter = get_location_filter_clause(locationfilter=locationfilter, siteid=siteid, whereprefix=True)
    return get_animals_ids(dbo, "a.LastChangedDate DESC", "SELECT animal.ID FROM animal LEFT OUTER JOIN internallocation il ON il.ID = ShelterLocation %s ORDER BY LastChangedDate DESC" % locationfilter, limit=limit, cachetime=120)

def get_links_recently_entered(dbo, limit = 5, locationfilter = "", siteid = 0):
    """
    Returns link info for animals who recently entered the shelter.
    """
    locationfilter = get_location_filter_clause(locationfilter=locationfilter, siteid=siteid, andprefix=True)
    return get_animals_ids(dbo, "a.MostRecentEntryDate DESC", "SELECT animal.ID FROM animal LEFT OUTER JOIN internallocation il ON il.ID = ShelterLocation WHERE Archived = 0 %s ORDER BY MostRecentEntryDate DESC" % locationfilter, limit=limit, cachetime=120)

def get_links_longest_on_shelter(dbo, limit = 5, locationfilter = "", siteid = 0):
    """
    Returns link info for animals who have been on the shelter the longest
    """
    locationfilter = get_location_filter_clause(locationfilter=locationfilter, siteid=siteid, andprefix=True)
    return get_animals_ids(dbo, "a.MostRecentEntryDate", "SELECT animal.ID FROM animal LEFT OUTER JOIN internallocation il ON il.ID = ShelterLocation WHERE Archived = 0 %s ORDER BY MostRecentEntryDate" % locationfilter, limit=limit, cachetime=120)

def get_location_filter_clause(locationfilter = "", tablequalifier = "", siteid = 0, whereprefix = False, andprefix = False, andsuffix = False):
    """
    Returns a where clause that excludes animals not in the locationfilter
    locationfilter: comma separated list of internallocation IDs and special values
        -1: animals on a trial/full adoption
        -2: animals in a foster home
        -8: animals in a retailer
        -9: non-shelter animals (excluded from this functionality)
    tablequalifier: The animal table name
    siteid: The animal's site, as linked to internallocation
    andprefix: If true, add a prefix of " AND " to any filter
    """
    # Don't do anything if there's no filter
    if locationfilter == "" and siteid == 0: return ""
    if tablequalifier != "" and not tablequalifier.endswith("."): tablequalifier += "."
    clauses = []
    if locationfilter != "":
        # If movement types are included in the filter, build another in clause
        locs = locationfilter.split(",")
        mtfilter = "0"
        if "-1" in locs: mtfilter += ",1"
        if "-2" in locs: mtfilter += ",2"
        if "-8" in locs: mtfilter += ",8"
        clauses.append("(%(tq)sShelterLocation IN (%(lf)s) OR %(tq)sActiveMovementType IN (%(mt)s))" % { "tq": tablequalifier, "lf": locationfilter, "mt": mtfilter })
    if siteid != 0:
        clauses.append("il.SiteID = %s" % siteid)
    c = " AND ".join(clauses)
    if andprefix:
        c = " AND %s" % c
    if andsuffix:
        c = "%s AND " % c
    if whereprefix:
        c = " WHERE %s" % c
    return c

def is_animal_in_location_filter(a, locationfilter, siteid = 0):
    """
    Returns True if the animal a is included in the locationfilter
    """
    if locationfilter == "" and siteid == 0: return True
    if siteid != 0:
        if a["SITEID"] != siteid: 
            return False
    if locationfilter != "":
        locs = locationfilter.split(",")
        if a["ACTIVEMOVEMENTTYPE"] == 1 and "-1" not in locs: return False
        if a["ACTIVEMOVEMENTTYPE"] == 2 and "-2" not in locs: return False
        if a["ACTIVEMOVEMENTTYPE"] == 8 and "-8" not in locs: return False
        if a["NONSHELTERANIMAL"] == 1 and "-9" not in locs: return False
        if str(a["SHELTERLOCATION"]) not in locs: return False
    return True

def get_number_animals_on_file(dbo):
    """
    Returns the number of animals on the system
    """
    return dbo.query_int("SELECT COUNT(ID) FROM animal")

def get_number_animals_on_shelter_now(dbo):
    """
    Returns the number of animals on shelter
    """
    return dbo.query_int("SELECT COUNT(ID) FROM animal WHERE Archived = 0")

def update_active_litters(dbo):
    """
    Goes through all litters on the system that haven't expired
    and recalculates the number of animals aged under six months
    left on the shelter. If it reaches zero, the litter is cancelled 
    with today's date. The field CachedAnimalsLeft is updated as well 
    if it differs.
    """
    active = dbo.query("SELECT l.*, " \
        "(SELECT COUNT(*) FROM animal a WHERE a.Archived = 0 " \
        "AND a.AcceptanceNumber Like l.AcceptanceNumber AND a.DateOfBirth >= ?) AS dbcount " \
        "FROM animallitter l " \
        "WHERE l.CachedAnimalsLeft Is Not Null AND " \
        "(l.InvalidDate Is Null OR l.InvalidDate > ?) ", ( subtract_months(dbo.now(), 6), dbo.now() ))
    for a in active:
        remaining = a["CACHEDANIMALSLEFT"]
        newremaining = a["DBCOUNT"]
        if newremaining == 0 and remaining > 0:
            al.debug("litter '%s' has no animals left, expiring." % a["ACCEPTANCENUMBER"], "animal.update_active_litters", dbo)
            dbo.execute("UPDATE animallitter SET InvalidDate=? WHERE ID=?", (dbo.now(), a["ID"]))
        if newremaining != remaining:
            dbo.execute("UPDATE animallitter SET CachedAnimalsLeft=? WHERE ID=?", (newremaining, a["ID"]))
            al.debug("litter '%s' has fewer animals, setting remaining to %d." % (a["ACCEPTANCENUMBER"], int(newremaining)), "animal.update_active_litters", dbo)

def get_active_litters(dbo, speciesid = -1):
    """
    Returns all active animal litters in descending order of age
    speciesid: A species filter or -1 for all
    """
    sql = "SELECT l.*, a.AnimalName AS MotherName, " \
        "a.ShelterCode AS Mothercode, s.SpeciesName AS SpeciesName " \
        "FROM animallitter l " \
        "LEFT OUTER JOIN animal a ON l.ParentAnimalID = a.ID " \
        "INNER JOIN species s ON l.SpeciesID = s.ID " \
        "WHERE InvalidDate < ? %s" \
        "ORDER BY l.Date DESC" 
    values = [ dbo.now() ]
    if speciesid != -1: 
        sql = sql % "AND SpeciesID = ? "
        values.append(speciesid)
    else:
        sql = sql % ""
    return dbo.query(sql, values)

def get_active_litters_brief(dbo):
    """ Returns the active litters in brief form for use by autocomplete """
    l = dbo.locale
    al = get_litters(dbo)
    rv = []
    for i in al:
        disp = ""
        if i["PARENTANIMALID"] is not None and i["PARENTANIMALID"] > 0:
            disp = _("{0}: {1} {2} - {3} {4}", l).format(
                i["MOTHERCODE"], i["MOTHERNAME"],
                i["ACCEPTANCENUMBER"], i["SPECIESNAME"],
                i["COMMENTS"][:40])
        else:
            disp = _("{0} - {1} {2}", l).format(
                i["ACCEPTANCENUMBER"], i["SPECIESNAME"],
                i["COMMENTS"][:40])
        rv.append( { "label": disp, "value": i["ACCEPTANCENUMBER"] } )
    return rv

def get_litters(dbo):
    """
    Returns all animal litters in descending order of age. Litters
    over a year old are ignored.
    """
    return dbo.query("SELECT l.*, a.AnimalName AS MotherName, " \
        "a.ShelterCode AS Mothercode, s.SpeciesName AS SpeciesName " \
        "FROM animallitter l " \
        "LEFT OUTER JOIN animal a ON l.ParentAnimalID = a.ID " \
        "INNER JOIN species s ON l.SpeciesID = s.ID " \
        "WHERE l.Date >= ? " \
        "ORDER BY l.Date DESC", [ subtract_years(now(), 1) ])

def get_satellite_counts(dbo, animalid):
    """
    Returns a resultset containing the number of each type of satellite
    record that an animal has.
    """
    return dbo.query("SELECT a.ID, " \
        "(SELECT COUNT(*) FROM animalvaccination av WHERE av.AnimalID = a.ID) AS vaccination, " \
        "(SELECT COUNT(*) FROM animaltest at WHERE at.AnimalID = a.ID) AS test, " \
        "(SELECT COUNT(*) FROM animalmedical am WHERE am.AnimalID = a.ID) AS medical, " \
        "(SELECT COUNT(*) FROM animaldiet ad WHERE ad.AnimalID = a.ID) AS diet, " \
        "(SELECT COUNT(*) FROM animaltransport tr WHERE tr.AnimalID = a.ID) AS transport, " \
        "(SELECT COUNT(*) FROM media me WHERE me.LinkID = a.ID AND me.LinkTypeID = ?) AS media, " \
        "(SELECT COUNT(*) FROM diary di WHERE di.LinkID = a.ID AND di.LinkType = ?) AS diary, " \
        "(SELECT COUNT(*) FROM adoption ad WHERE ad.AnimalID = a.ID) AS movements, " \
        "(SELECT COUNT(*) FROM log WHERE log.LinkID = a.ID AND log.LinkType = ?) AS logs, " \
        "(SELECT COUNT(*) FROM ownerdonation od WHERE od.AnimalID = a.ID) AS donations, " \
        "(SELECT COUNT(*) FROM ownerlicence ol WHERE ol.AnimalID = a.ID) AS licence, " \
        "(SELECT COUNT(*) FROM animalcost ac WHERE ac.AnimalID = a.ID) AS costs " \
        "FROM animal a WHERE a.ID = ?", \
        (media.ANIMAL, diary.ANIMAL, log.ANIMAL, animalid))

def get_preferred_web_media_name(dbo, animalid):
    """
    Returns the name of the preferred media image for publishing to the
    web. If no preferred is found, returns the first image available for
    the animal. If the animal has no images, an empty string is returned.
    """
    mrec = dbo.query("SELECT * FROM media WHERE LinkID = ? AND LinkTypeID = 0 AND MediaMimeType = 'image/jpeg'", [animalid])
    for m in mrec:
        if m["WEBSITEPHOTO"] == 1:
            return m["MEDIANAME"]
    if len(mrec) > 0:
        return mrec[0]["MEDIANAME"]
    else:
        return ""

def get_random_name(dbo, sex = 0):
    """
    Returns a random animal name from the database. It will ignore names
    that end with numbers and try to prefer less well used names.
    sex: A sex from lksex - 0 = Female, 1 = Male, 2 = Unknown
    """
    names = dbo.query("SELECT AnimalName, COUNT(AnimalName) AS Total " \
        "FROM animal " \
        "WHERE Sex = ? " \
        "AND AnimalName Not Like '%%0' "\
        "AND AnimalName Not Like '%%1' "\
        "AND AnimalName Not Like '%%2' "\
        "AND AnimalName Not Like '%%3' "\
        "AND AnimalName Not Like '%%4' "\
        "AND AnimalName Not Like '%%5' "\
        "AND AnimalName Not Like '%%6' "\
        "AND AnimalName Not Like '%%7' "\
        "AND AnimalName Not Like '%%8' "\
        "AND AnimalName Not Like '%%9' "\
        "GROUP BY AnimalName " \
        "ORDER BY COUNT(AnimalName)", [sex])
    # We have less than a hundred animals, use one of our random set
    if len(names) < 100: return animalname.get_random_name()
    # Build a separate list of the lesser used names
    leastused = []
    for n in names:
        if n["TOTAL"] < 3:
            leastused.append(n)
    # Choose whether we're going to use our set, one of the lesser
    # used or something from the overall pool. We prefer our set, then
    # the lesser used names, then anything
    decide = choice((1, 2, 3, 4, 5, 6))
    if decide < 4:
        return animalname.get_random_name()
    elif decide == 4 or decide == 5:
        return choice(leastused)["ANIMALNAME"]
    else:
        return choice(names)["ANIMALNAME"]

def get_recent_with_name(dbo, name):
    """
    Returns a list of animals who have a brought in date in the last 3 weeks
    with the name given.
    """
    return dbo.query("SELECT ID, ID AS ANIMALID, SHELTERCODE, ANIMALNAME FROM animal " \
        "WHERE DateBroughtIn >= ? AND LOWER(AnimalName) LIKE ?", (subtract_days(dbo.now(), 21), name.lower()))

def get_units_with_availability(dbo, locationid):
    """
    Returns a list of location units for location id.
    The layout of each element is unit|occupant
    Blank occupant means a free unit
    """
    a = []
    units = dbo.query_string("SELECT Units FROM internallocation WHERE ID = ?", [locationid]).split(",")
    animals = dbo.query("SELECT a.AnimalName, a.ShortCode, a.ShelterCode, a.ShelterLocationUnit " \
        "FROM animal a WHERE a.Archived = 0 AND ActiveMovementID = 0 AND ShelterLocation = ?", [locationid])
    useshortcodes = configuration.use_short_shelter_codes(dbo)
    for u in units:
        if u == "": continue
        uname = u.strip().replace("'", "`")
        occupant = ""
        for n in animals:
            if utils.nulltostr(n["SHELTERLOCATIONUNIT"]).strip().lower() == uname.strip().lower():
                if occupant != "": occupant += ", "
                occupant += useshortcodes and n["SHORTCODE"] or n["SHELTERCODE"]
                occupant += " %s" % n["ANIMALNAME"]
        a.append( "%s|%s" % (uname, occupant) )
    return a

def get_publish_history(dbo, animalid):
    """
    Returns a list of services and the date the animal was last registered with them.
    """
    return dbo.query("SELECT PublishedTo, SentDate, Extra FROM animalpublished WHERE AnimalID = ? ORDER BY SentDate DESC", [animalid])

def insert_publish_history(dbo, animalid, service):
    """
    Marks an animal as published to a particular service now
    """
    dbo.execute("DELETE FROM animalpublished WHERE AnimalID = ? AND PublishedTo = ?", (animalid, service))
    dbo.execute("INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) VALUES (?, ?, ?)", \
        (animalid, service, dbo.now()))

def delete_publish_history(dbo, animalid, service):
    """
    Forgets an animal has been published to a particular service.
    """
    dbo.execute("DELETE FROM animalpublished WHERE AnimalID = ? AND PublishedTo = ?", (animalid, service))

def get_shelterview_animals(dbo, locationfilter = "", siteid = 0):
    """
    Returns all available animals for shelterview
    """
    limit = configuration.record_search_limit(dbo)
    locationfilter = get_location_filter_clause(locationfilter=locationfilter, siteid=siteid, andprefix=True)
    return get_animals_ids(dbo, "a.AnimalName", "SELECT animal.ID FROM animal LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation WHERE Archived = 0 %s ORDER BY HasPermanentFoster, animal.ID DESC" % locationfilter, limit=limit)

def insert_animal_from_form(dbo, post, username):
    """
    Creates an animal record from the new animal screen
    data: The webpy data object containing form parameters
    Returns a tuple containing the newly created animal id and code
    """
    if not extension.route(dbo, "before", "insert_animal_from_form", post):
        return
    l = dbo.locale
    nextid = db.get_id(dbo, "animal")
    post.data["id"] = nextid
    def c(field):
        return post.db_boolean(field)
    def t(field):
        return post.db_string(field)
    def s(field):
        return post.db_integer(field)
    def kd(field):
        return post.date(field)
    def kdt(datefield, timefield):
        return post.datetime(datefield, timefield)
    def ki(field):
        return post.integer(field)
    def kf(field):
        return post.floating(field)
    def ks(field):
        return post.string(field)

    if ks("dateofbirth") == "" or kd("dateofbirth") is None:
        estimateddob = 1
        dob = subtract_years(now(), kf("estimatedage"))
    else:
        estimateddob = 0
        dob = kd("dateofbirth")

    # Set brought in by date
    datebroughtin = kdt("datebroughtin", "timebroughtin")
    if datebroughtin is None:
        if configuration.add_animals_show_time_brought_in(dbo):
            datebroughtin = now()
        else:
            datebroughtin = today()

    # Set the code manually if we were given a code, or the option was turned on
    if configuration.manual_codes(dbo) or ks("sheltercode") != "":
        sheltercode = ks("sheltercode")
        shortcode = ks("shortcode")
        unique = 0
        year = 0
        if sheltercode.strip() == "":
            raise utils.ASMValidationError(_("You must supply a code.", l))
        if 0 != db.query_int(dbo, "SELECT COUNT(ID) FROM animal WHERE ShelterCode = '%s'" % sheltercode.replace("'", "`")):
            raise utils.ASMValidationError(_("This code has already been used.", l))
    else:
        # Generate a new code
        sheltercode, shortcode, unique, year = calc_shelter_code(dbo, ki("animaltype"), ki("entryreason"), ki("species"), datebroughtin)

    # Default good with
    goodwithcats = 2
    if "goodwithcats" in post: goodwithcats = ki("goodwithcats")
    goodwithdogs = 2
    if "goodwithdogs" in post: goodwithdogs = ki("goodwithdogs")
    goodwithkids = 2
    if "goodwithkids" in post: goodwithkids = ki("goodwithkids")
    housetrained = 2
    if "housetrained" in post: housetrained = ki("housetrained")
    unknown = 0

    # Validate form fields
    if ks("animalname") == "":
        raise utils.ASMValidationError(_("Name cannot be blank", l))
    if ks("microchipnumber").strip() != "" and not configuration.allow_duplicate_microchip(dbo):
        if db.query_int(dbo, "SELECT COUNT(ID) FROM animal WHERE IdentichipNumber Like %s AND ID <> %d" % (post.db_string("microchipnumber"), ki("id"))) > 0:
            raise utils.ASMValidationError(_("Microchip number {0} has already been allocated to another animal.", l).format(ks("microchipnumber")))
    if dob > now(dbo.timezone):
        raise utils.ASMValidationError(_("Date of birth cannot be in the future.", l))

    # Set default brought in by if we have one and none was set
    dbb = ki("broughtinby")
    if dbb == 0:
        dbb = configuration.default_broughtinby(dbo)

    # If we have nsowner, use that over originalowner for non-shelter animals
    originalowner = ki("originalowner")
    if ki("nsowner") != 0:
        originalowner = ki("nsowner")

    # Set not for adoption if the option is on
    notforadoption = 0
    if "notforadoption" in post:
        notforadoption = ki("notforadoption")
    elif configuration.auto_not_for_adoption(dbo):
        notforadoption = 1        

    sql = db.make_insert_user_sql(dbo, "animal", username, (
        ( "ID", db.di(nextid)),
        ( "AnimalName", t("animalname")),
        ( "ShelterCode", db.ds(sheltercode)),
        ( "ShortCode", db.ds(shortcode)),
        ( "UniqueCodeID", db.di(unique)),
        ( "YearCodeID", db.di(year)),
        ( "DateOfBirth", db.dd(dob)),
        ( "DailyBoardingCost", db.di(configuration.default_daily_boarding_cost(dbo))),
        ( "Sex", s("sex")),
        ( "AnimalTypeID", s("animaltype")),
        ( "SpeciesID", s("species")),
        ( "BreedID", s("breed1")),
        ( "Breed2ID", s("breed2")),
        ( "BreedName", db.ds(get_breedname(dbo, ki("breed1"), ki("breed2")))),
        ( "Crossbreed", c("crossbreed")),
        ( "AcceptanceNumber", t("litterid")),
        ( "BaseColourID", s("basecolour")),
        ( "ShelterLocation", s("internallocation")),
        ( "ShelterLocationUnit", t("unit")),
        ( "NonShelterAnimal", c("nonshelter")),
        ( "CrueltyCase", db.di(0)),
        ( "BondedAnimalID", db.di(0)),
        ( "BondedAnimal2ID", db.di(0)),
        ( "CoatType", db.di(configuration.default_coattype(dbo))),
        ( "EstimatedDOB", db.di(estimateddob)),
        ( "Fee", s("fee")),
        ( "Identichipped", c("microchipped")),
        ( "IdentichipNumber", t("microchipnumber")),
        ( "IdentichipDate", db.dd(kd("microchipdate"))),
        ( "Tattoo", c("tattoo")),
        ( "TattooNumber", t("tattoonumber")),
        ( "TattooDate", db.dd(kd("tattoodate"))),
        ( "SmartTag", db.di(0)),
        ( "SmartTagNumber", db.ds("")),
        ( "SmartTagType", db.di(0)),
        ( "Neutered", c("neutered")),
        ( "NeuteredDate", db.dd(kd("neutereddate"))),
        ( "Declawed", db.di(0)),
        # ASM2_COMPATIBILITY
        ( "HeartwormTested", db.di(0)),
        ( "HeartwormTestDate", db.dd(None)),
        ( "HeartwormTestResult", db.di(unknown)),
        ( "CombiTested", db.di(0)),
        ( "CombiTestDate", db.dd(None)),
        ( "CombiTestResult", db.di(unknown)),
        ( "FLVResult", db.di(unknown)),
        # ASM2_COMPATIBILITY
        ( "Markings", t("markings")),
        ( "HiddenAnimalDetails", t("hiddenanimaldetails")),
        ( "AnimalComments", t("comments")),
        ( "IsGoodWithCats", db.di(goodwithcats)),
        ( "IsGoodWithDogs", db.di(goodwithdogs)),
        ( "IsGoodWithChildren", db.di(goodwithkids)),
        ( "IsHouseTrained", db.di(housetrained)),
        ( "OriginalOwnerID", db.di(originalowner)),
        ( "BroughtInByOwnerID", db.di(dbb) ),
        ( "AdoptionCoordinatorID", s("adoptioncoordinator") ),
        ( "ReasonNO", db.ds("")),
        ( "ReasonForEntry", t("reasonforentry")),
        ( "EntryReasonID", s("entryreason")),
        ( "IsTransfer", c("transferin")),
        ( "IsPickup", c("pickedup")),
        ( "PickupLocationID", s("pickuplocation")),
        ( "PickupAddress", t("pickupaddress")),
        ( "IsHold", c("hold")),
        ( "HoldUntilDate", db.dd(kd("holduntil"))),
        ( "IsCourtesy", db.di(0)),
        ( "IsQuarantine", db.di(0)),
        ( "AdditionalFlags", db.ds("")),
        ( "DateBroughtIn", db.ddt(datebroughtin)),
        ( "AsilomarIntakeCategory", db.di(0)),
        ( "AsilomarIsTransferExternal", db.di(0)),
        ( "AsilomarOwnerRequestedEuthanasia", db.di(0)),
        ( "HealthProblems", t("healthproblems")),
        ( "HasSpecialNeeds", db.di(0)),
        ( "RabiesTag", db.ds("")),
        ( "CurrentVetID", db.di(0)),
        ( "OwnersVetID", db.di(0)),
        ( "DeceasedDate", db.dd(kd("deceaseddate"))),
        ( "PTSReasonID", db.di(configuration.default_death_reason(dbo))),
        ( "PutToSleep", db.di(0)),
        ( "IsDOA", db.di(0)),
        ( "DiedOffShelter", db.di(0)),
        ( "PTSReason", db.ds("")),
        ( "IsNotAvailableForAdoption", db.di(notforadoption)),
        ( "Size", s("size")),
        ( "Weight", post.db_floating("weight")),
        ( "Archived", db.di(0)),
        ( "ActiveMovementID", db.di(0)),
        ( "HasActiveReserve", db.di(0)),
        ( "MostRecentEntryDate", db.ddt(now()))
    ))
    db.execute(dbo, sql)
    audit.create(dbo, username, "animal", nextid, audit.dump_row(dbo, "animal", nextid))

    # Save any additional field values given
    additional.save_values_for_link(dbo, post, nextid, "animal")

    # Update denormalised fields after the insert
    update_animal_check_bonds(dbo, nextid)
    update_animal_status(dbo, nextid)
    update_variable_animal_data(dbo, nextid)

    # If a fosterer was specified, foster the animal
    if post.integer("fosterer") > 0:
        move_dict = {
            "person"                : post["fosterer"],
            "animal"                : str(nextid),
            "movementdate"          : python2display(l, datebroughtin),
            "type"                  : str(movement.FOSTER),
            "returncategory"        : configuration.default_return_reason(dbo)
        }
        movement.insert_movement_from_form(dbo, username, utils.PostedData(move_dict, l))

    # If a weight was specified and we're logging, mark it in the log
    if configuration.weight_change_log(dbo) and kf("weight") > 0:
        weight = str(kf("weight"))
        units = ""
        if configuration.show_weight_units_in_log(dbo):
            units = configuration.show_weight_in_lbs(dbo) and " lb" or " kg"
        log.add_log(dbo, username, log.ANIMAL, nextid, configuration.weight_change_log_type(dbo),
            "%s%s" % (weight, units))

    # Do we have a matching template animal we can copy some satellite info from?
    clone_from_template(dbo, username, nextid, dob, ki("animaltype"), ki("species"))

    extension.route(dbo, "after", "insert_animal_from_form", post)
    return (nextid, get_code(dbo, nextid))

def update_animal_from_form(dbo, post, username):
    """
    Updates an animal record from the edit animal screen
    data: The webpy data object containing form parameters
    """
    if not extension.route(dbo, "before", "update_animal_from_form", post):
        return
    l = dbo.locale
    def c(field):
        return post.db_boolean(field)
    def t(field):
        return post.db_string(field)
    def s(field):
        return post.db_integer(field)
    def d(field):
        return post.db_date(field)
    def dt(datefield, timefield):
        return post.db_datetime(datefield, timefield)
    def kd(field):
        return post.date(field)
    def kdt(datefield, timefield):
        return post.datetime(datefield, timefield)
    def kf(field):
        return post.floating(field)
    def ki(field):
        return post.integer(field)
    def ks(field):
        return post.string(field)

    # Optimistic lock check
    if not dbo.optimistic_check("animal", ki("id"), ki("recordversion")):
        raise utils.ASMValidationError(_("This record has been changed by another user, please reload.", l))

    # Validate form fields
    if ks("animalname") == "":
        raise utils.ASMValidationError(_("Name cannot be blank", l))
    if ks("dateofbirth") == "":
        raise utils.ASMValidationError(_("Date of birth cannot be blank", l))
    if kd("dateofbirth") is None:
        raise utils.ASMValidationError(_("Date of birth is not valid", l))
    if kd("dateofbirth") > now(dbo.timezone):
        raise utils.ASMValidationError(_("Date of birth cannot be in the future.", l))
    if ks("datebroughtin") == "":
        raise utils.ASMValidationError(_("Date brought in cannot be blank", l))
    if kdt("datebroughtin", "timebroughtin") is None:
        raise utils.ASMValidationError(_("Date brought in is not valid", l))
    if ks("sheltercode") == "":
        raise utils.ASMValidationError(_("Shelter code cannot be blank", l))
    if db.query_int(dbo, "SELECT COUNT(ID) FROM animal WHERE ShelterCode Like '%s' AND ID <> %d" % (ks("sheltercode").replace("'", "`"), ki("id"))) > 0:
        raise utils.ASMValidationError(_("Shelter code {0} has already been allocated to another animal.", l).format(ks("sheltercode")))
    if ks("microchipnumber").strip() != "" and not configuration.allow_duplicate_microchip(dbo):
        if db.query_int(dbo, "SELECT COUNT(ID) FROM animal WHERE IdentichipNumber Like %s AND ID <> %d" % (post.db_string("microchipnumber"), ki("id"))) > 0:
            raise utils.ASMValidationError(_("Microchip number {0} has already been allocated to another animal.", l).format(ks("microchipnumber")))
    if ks("deceaseddate") != "":
        deceaseddate = d("deceaseddate")
        datebroughtin = d("datebroughtin")
        if deceaseddate is not None and datebroughtin is not None and deceaseddate < datebroughtin:
            raise utils.ASMValidationError(_("Animal cannot be deceased before it was brought to the shelter", l))

    # If the option is on and the internal location or unit has changed, log it
    if configuration.location_change_log(dbo):
        oldloc = db.query(dbo, "SELECT ShelterLocation, ShelterLocationUnit FROM animal WHERE ID=%d" % ki("id"))
        if len(oldloc) > 0:
            oldlocid = oldloc[0]["SHELTERLOCATION"]
            oldlocunit = oldloc[0]["SHELTERLOCATIONUNIT"]
            if ki("location") != oldlocid or ks("unit") != oldlocunit:
                oldlocation = db.query_string(dbo, "SELECT LocationName FROM internallocation WHERE ID = %d" % oldlocid)
                if oldlocunit is not None and oldlocunit != "":
                    oldlocation += "-" + oldlocunit
                newlocation = db.query_string(dbo, "SELECT LocationName FROM internallocation WHERE ID = %d" % ki("location"))
                if ks("unit") != "":
                    newlocation += "-" + ks("unit")
                log.add_log(dbo, username, log.ANIMAL, ki("id"), configuration.location_change_log_type(dbo), 
                    _("{0} {1}: Moved from {2} to {3}", l).format(ks("sheltercode"), ks("animalname"), oldlocation, newlocation))

    # If the option is on and the weight has changed, log it
    if configuration.weight_change_log(dbo):
        oldweight = db.query_float(dbo, "SELECT Weight FROM animal WHERE ID=%d" % ki("id"))
        if kf("weight") != oldweight:
            weight = str(kf("weight"))
            units = ""
            if configuration.show_weight_units_in_log(dbo):
                units = configuration.show_weight_in_lbs(dbo) and " lb" or " kg"
            log.add_log(dbo, username, log.ANIMAL, ki("id"), configuration.weight_change_log_type(dbo),
                "%s%s" % (weight, units))

    # Sort out any flags
    def bi(b): 
        return b and 1 or 0

    flags = post["flags"].split(",")
    courtesy = bi("courtesy" in flags)
    crueltycase = bi("crueltycase" in flags)
    notforadoption = bi("notforadoption" in flags)
    nonshelter = bi("nonshelter" in flags)
    quarantine = bi("quarantine" in flags)
    flagstr = "|".join(flags) + "|"

    # If the animal is non-shelter, make sure that any movements are returned on the same
    # day. Non shelter animals don't have visible movements and this prevents a bug where
    # an open foster/retailer movement on a non-shelter animal can make it publish for adoption
    # when the "include fosters/retailers" publishing options are on.
    if nonshelter == 1:
        db.execute(dbo, "UPDATE adoption SET ReturnDate = MovementDate WHERE MovementType IN (2,8) AND AnimalID = %d" % ki("id"))

    preaudit = db.query(dbo, "SELECT * FROM animal WHERE ID = %d" % ki("id"))
    db.execute(dbo, db.make_update_user_sql(dbo, "animal", username, "ID=%d" % ki("id"), (
        ( "NonShelterAnimal", db.di(nonshelter)),
        ( "IsNotAvailableForAdoption", db.di(notforadoption)),
        ( "IsHold", c("hold")),
        ( "HoldUntilDate", d("holduntil")),
        ( "IsQuarantine", db.di(quarantine)),
        ( "IsCourtesy", db.di(courtesy)),
        ( "CrueltyCase", db.di(crueltycase)),
        ( "AdditionalFlags", db.ds(flagstr)),
        ( "ShelterCode", t("sheltercode")),
        ( "ShortCode", t("shortcode")),
        ( "UniqueCodeID", s("uniquecode")),
        ( "YearCodeID", s("yearcode")),
        ( "AcceptanceNumber", t("litterid")),
        ( "AnimalName", t("animalname")),
        ( "Sex", s("sex")),
        ( "AnimalTypeID", s("animaltype")),
        ( "BaseColourID", s("basecolour")),
        ( "CoatType", s("coattype")),
        ( "Size", s("size")),
        ( "Weight", post.db_floating("weight")),
        ( "SpeciesID", s("species")),
        ( "BreedID", s("breed1")),
        ( "Breed2ID", s("breed2")),
        ( "BreedName", db.ds(get_breedname(dbo, ki("breed1"), ki("breed2")))),
        ( "Crossbreed", c("crossbreed")),
        ( "ShelterLocation", s("location")),
        ( "ShelterLocationUnit", t("unit")),
        ( "DateOfBirth", d("dateofbirth")),
        ( "EstimatedDOB", c("estimateddob")),
        ( "Fee", s("fee")),
        ( "Identichipped", c("microchipped")),
        ( "IdentichipDate", d("microchipdate")),
        ( "IdentichipNumber", t("microchipnumber")),
        ( "Tattoo", c("tattoo")),
        ( "TattooDate", d("tattoodate")),
        ( "TattooNumber", t("tattoonumber")),
        ( "SmartTag", c("smarttag")),
        ( "SmartTagNumber", t("smarttagnumber")),
        ( "SmartTagType", s("smarttagtype")),
        ( "Neutered", c("neutered")),
        ( "NeuteredDate", d("neutereddate")),
        ( "Declawed", c("declawed")),
        # ASM2_COMPATIBILITY
        ( "HeartwormTested", c("heartwormtested")),
        ( "HeartwormTestDate", d("heartwormtestdate")),
        ( "HeartwormTestResult", s("heartwormtestresult")),
        ( "CombiTested", c("fivltested")),
        ( "CombiTestDate", d("fivltestdate")),
        ( "CombiTestResult", s("fivresult")),
        ( "FLVResult", s("flvresult")),
        # ASM2_COMPATIBILITY
        ( "Markings", t("markings")),
        ( "HiddenAnimalDetails", t("hiddencomments")),
        ( "AnimalComments", t("comments")),
        ( "IsGoodWithCats", s("goodwithcats")),
        ( "IsGoodWithDogs", s("goodwithdogs")),
        ( "IsGoodWithChildren", s("goodwithkids")),
        ( "IsHouseTrained", s("housetrained")),
        ( "OriginalOwnerID", s("originalowner")),
        ( "BroughtInByOwnerID", s("broughtinby")),
        ( "AdoptionCoordinatorID", s("adoptioncoordinator") ),
        ( "BondedAnimalID", s("bonded1")),
        ( "BondedAnimal2ID", s("bonded2")),
        ( "ReasonNO", t("reasonnotfromowner")),
        ( "ReasonForEntry", t("reasonforentry")),
        ( "EntryReasonID", s("entryreason")),
        ( "IsTransfer", c("transferin")),
        ( "IsPickup", c("pickedup")),
        ( "PickupLocationID", s("pickuplocation")),
        ( "PickupAddress", t("pickupaddress")),
        ( "DateBroughtIn", dt("datebroughtin", "timebroughtin")),
        ( "AsilomarIntakeCategory", s("asilomarintakecategory")),
        ( "AsilomarIsTransferExternal", c("asilomartransferexternal")),
        ( "AsilomarOwnerRequestedEuthanasia", c("asilomarownerrequested")),
        ( "HealthProblems", t("healthproblems")),
        ( "HasSpecialNeeds", c("specialneeds")),
        ( "RabiesTag", t("rabiestag")),
        ( "CurrentVetID", s("currentvet")),
        ( "OwnersVetID", s("ownersvet")),
        ( "DeceasedDate", d("deceaseddate")),
        ( "PTSReasonID", s("deathcategory")),
        ( "PutToSleep", c("puttosleep")),
        ( "IsDOA", c("deadonarrival")),
        ( "PTSReason", t("ptsreason"))
    )))
    postaudit = db.query(dbo, "SELECT * FROM animal WHERE ID = %d" % ki("id"))
    audit.edit(dbo, username, "animal", ki("id"), audit.map_diff(preaudit, postaudit, [ "SHELTERCODE", "ANIMALNAME" ]))

    # Save any additional field values given
    additional.save_values_for_link(dbo, post, ki("id"), "animal")

    # Update denormalised fields after the change
    update_animal_check_bonds(dbo, ki("id"))
    update_animal_status(dbo, ki("id"))
    update_variable_animal_data(dbo, ki("id"))

    # Update any diary notes linked to this animal
    update_diary_linkinfo(dbo, ki("id"))
    extension.route(dbo, "after", "update_animal_from_form", post)

def update_animals_from_form(dbo, post, username):
    """
    Batch updates multiple animal records from the bulk form
    """
    if len(post.integer_list("animals")) == 0: return 0
    aud = []
    if post["litterid"] != "":
        db.execute(dbo, "UPDATE animal SET AcceptanceNumber = %s WHERE ID IN (%s)" % (post.db_string("litterid"), post["animals"]))
        aud.append("LitterID = %s" % post["litterid"])
    if post.integer("animaltype") != -1:
        db.execute(dbo, "UPDATE animal SET AnimalTypeID = %d WHERE ID IN (%s)" % (post.integer("animaltype"), post["animals"]))
        aud.append("AnimalTypeID = %s" % post["animaltype"])
    if post.integer("location") != -1:
        db.execute(dbo, "UPDATE animal SET ShelterLocation = %d WHERE ID IN (%s)" % (post.integer("location"), post["animals"]))
        aud.append("ShelterLocation = %s" % post["location"])
    if post.integer("fee") > 0:
        db.execute(dbo, "UPDATE animal SET Fee = %d WHERE ID IN (%s)" % (post.integer("fee"), post["animals"]))
        aud.append("Fee = %s" % post["fee"])
    if post.integer("boardingcost") > 0:
        db.execute(dbo, "UPDATE animal SET DailyBoardingCost = %d WHERE ID IN (%s)" % (post.integer("boardingcost"), post["animals"]))
        aud.append("DailyBoardingCost = %s" % post["boardingcost"])
    if post.integer("notforadoption") != -1:
        db.execute(dbo, "UPDATE animal SET IsNotAvailableForAdoption = %d WHERE ID IN (%s)" % (post.integer("notforadoption"), post["animals"]))
        aud.append("IsNotAvailableForAdoption = %s" % post["notforadoption"])
    if post["holduntil"] != "":
        db.execute(dbo, "UPDATE animal SET IsHold = 1, HoldUntilDate = %s WHERE ID IN (%s)" % (post.db_date("holduntil"), post["animals"]))
        aud.append("HoldUntilDate = %s" % post["holduntil"])
    if post.integer("goodwithcats") != -1:
        db.execute(dbo, "UPDATE animal SET IsGoodWithCats = %d WHERE ID IN (%s)" % (post.integer("goodwithcats"), post["animals"]))
        aud.append("IsGoodWithCats = %s" % post["goodwithcats"])
    if post.integer("goodwithdogs") != -1:
        db.execute(dbo, "UPDATE animal SET IsGoodWithDogs = %d WHERE ID IN (%s)" % (post.integer("goodwithdogs"), post["animals"]))
        aud.append("IsGoodWithDogs = %s" % post["goodwithdogs"])
    if post.integer("goodwithkids") != -1:
        db.execute(dbo, "UPDATE animal SET IsGoodWithChildren = %d WHERE ID IN (%s)" % (post.integer("goodwithkids"), post["animals"]))
        aud.append("IsGoodWithChildren = %s" % post["goodwithkids"])
    if post.integer("housetrained") != -1:
        db.execute(dbo, "UPDATE animal SET IsHouseTrained = %d WHERE ID IN (%s)" % (post.integer("housetrained"), post["animals"]))
        aud.append("IsHouseTrained = %s" % post["housetrained"])
    if post["neutereddate"] != "":
        db.execute(dbo, "UPDATE animal SET Neutered = 1, NeuteredDate = %s WHERE ID IN (%s)" % (post.db_date("neutereddate"), post["animals"]))
        aud.append("NeuteredDate = %s" % post["neutereddate"])
    if post["currentvet"] != "" and post["currentvet"] != "0":
        db.execute(dbo, "UPDATE animal SET CurrentVetID = %d WHERE ID IN (%s)" % (post.integer("currentvet"), post["animals"]))
        aud.append("CurrentVetID = %s" % post["currentvet"])
    if post["ownersvet"] != "" and post["ownersvet"] != "0":
        db.execute(dbo, "UPDATE animal SET OwnersVetID = %d WHERE ID IN (%s)" % (post.integer("ownersvet"), post["animals"]))
        aud.append("OwnersVetID = %s" % post["ownersvet"])
    if post["adoptioncoordinator"] != "" and post["adoptioncoordinator"] != "0":
        db.execute(dbo, "UPDATE animal SET AdoptionCoordinatorID = %d WHERE ID IN (%s)" % (post.integer("adoptioncoordinator"), post["animals"]))
        aud.append("AdoptionCoordinatorID = %s" % post["adoptioncoordinator"])
    if post["addflag"] != "":
        animals = db.query(dbo, "SELECT ID, AdditionalFlags FROM animal WHERE ID IN (%s)" % post["animals"])
        for a in animals:
            if a["ADDITIONALFLAGS"] is None: a["ADDITIONALFLAGS"] = ""
            if a["ADDITIONALFLAGS"].find("%s|" % post["addflag"]) == -1:
                newflags = "%s%s|" % (a["ADDITIONALFLAGS"], post["addflag"])
                db.execute(dbo, "UPDATE animal SET AdditionalFlags = %s WHERE ID = %d" % ( db.ds(newflags), a["ID"] ))
                aud.append("AdditionalFlags %s --> %s" % (a["ADDITIONALFLAGS"], newflags))
    if post.integer("movementtype") != -1:
        default_return_reason = configuration.default_return_reason(dbo)
        for animalid in post.integer_list("animals"):
            # Is this animal already on foster? If so, return that foster first
            fm = movement.get_animal_movements(dbo, animalid)
            for m in fm:
                if m["MOVEMENTTYPE"] == movement.FOSTER and m["RETURNDATE"] is None:
                    movement.return_movement(dbo, m["ID"], animalid, post.date("movementdate"))
            move_dict = {
                "person"                : post["moveto"],
                "animal"                : str(animalid),
                "movementdate"          : post["movementdate"],
                "permanentfoster"       : "0",
                "adoptionno"            : "",
                "returndate"            : "",
                "type"                  : post["movementtype"],
                "donation"              : 0,
                "returncategory"        : str(default_return_reason)
            }
            movement.insert_movement_from_form(dbo, username, utils.PostedData(move_dict, dbo.locale))
    # Record the user as making the last change to this record and create audit records for the changes
    db.execute(dbo, "UPDATE animal SET LastChangedBy = %s, LastChangedDate = %s WHERE ID IN (%s)" % (db.ds(username), db.ddt(now(dbo.timezone)), post["animals"]))
    if len(aud) > 0:
        for animalid in post.integer_list("animals"):
            audit.edit(dbo, username, "animal", animalid, ", ".join(aud))
    return len(post.integer_list("animals"))

def update_deceased_from_form(dbo, username, post):
    """
    Sets an animal's deceased information from the move_deceased form
    """
    animalid = post.integer("animal")
    sql = db.make_update_user_sql(dbo, "animal", username, "ID=%s" % db.di(animalid), (
        ( "DeceasedDate", post.db_date("deceaseddate")),
        ( "PTSReasonID", post.db_integer("deathcategory")),
        ( "PutToSleep", post.db_boolean("puttosleep")),
        ( "IsDOA", post.db_boolean("deadonarrival")),
        ( "PTSReason", post.db_string("ptsreason"))
    ))
    preaudit = db.query(dbo, "SELECT * FROM animal WHERE ID = %d" % animalid)
    db.execute(dbo, sql)
    postaudit = db.query(dbo, "SELECT * FROM animal WHERE ID = %d" % animalid)
    audit.edit(dbo, username, "animal", animalid, audit.map_diff(preaudit, postaudit, [ "ANIMALNAME", ]))
    # Update denormalised fields after the deceased change
    update_animal_status(dbo, animalid)
    update_variable_animal_data(dbo, animalid)

def update_diary_linkinfo(dbo, animalid, a = None, diaryupdatebatch = None):
    """
    Updates the linkinfo on diary notes for an animal.
    animalid: The animal's ID
    a: An animal resultset (if none, will be loaded)
    diaryupdatebatch: a batch of diary records to update, the three
                      params are linkinfo, linktype and id. If blank, an update
                      query will be done immediately
    """
    if a is None:
        a = get_animal(dbo, animalid)
    diaryloc = "%s - %s [%s]" % ( a["SHELTERCODE"], a["ANIMALNAME"], get_display_location_noq(dbo, animalid, a["DISPLAYLOCATION"]))
    if diaryupdatebatch is not None:
        diaryupdatebatch.append( (diaryloc, diary.ANIMAL, animalid) )
    else:
        db.execute(dbo, "UPDATE diary SET LinkInfo = %s WHERE LinkType = %d AND LinkID = %d" % (
            db.ds(diaryloc), diary.ANIMAL, animalid ))

def update_location_unit(dbo, username, animalid, newlocationid, newunit = ""):
    """
    Updates the shelterlocation and shelterlocationunit fields of the animal given.
    """
    # If the option is on and the internal location has changed, log it
    l = dbo.locale
    if configuration.location_change_log(dbo):
        oldloc = db.query(dbo, "SELECT ShelterCode, AnimalName, ShelterLocation, ShelterLocationUnit FROM animal WHERE ID=%d" % animalid)
        if len(oldloc) > 0:
            animalname = oldloc[0]["ANIMALNAME"]
            sheltercode = oldloc[0]["SHELTERCODE"]
            oldlocid = oldloc[0]["SHELTERLOCATION"]
            oldlocunit = oldloc[0]["SHELTERLOCATIONUNIT"]
            if newlocationid != oldlocid or newunit != oldlocunit:
                oldlocation = db.query_string(dbo, "SELECT LocationName FROM internallocation WHERE ID = %d" % oldlocid)
                if oldlocunit is not None and oldlocunit != "":
                    oldlocation += "-" + oldlocunit
                newlocation = db.query_string(dbo, "SELECT LocationName FROM internallocation WHERE ID = %d" % newlocationid)
                if newunit != "":
                    newlocation += "-" + newunit
                log.add_log(dbo, username, log.ANIMAL, animalid, configuration.location_change_log_type(dbo), 
                    _("{0} {1}: Moved from {2} to {3}", l).format(sheltercode, animalname, oldlocation, newlocation))
    # Change the location
    db.execute(dbo, "UPDATE animal SET ShelterLocation = %s, ShelterLocationUnit = %s WHERE ID = %s" % (db.di(newlocationid), db.ds(newunit), db.di(animalid)))
    audit.edit(dbo, username, "animal", animalid, "%s: moved to location: %s, unit: %s" % ( animalid, newlocationid, newunit ))
    update_animal_status(dbo, animalid)

def clone_animal(dbo, username, animalid):
    """
    Clones an animal and its satellite records.
    """
    l = dbo.locale
    a = get_animal(dbo, animalid)
    nid = db.get_id(dbo, "animal")
    sheltercode, shortcode, unique, year = calc_shelter_code(dbo, a["ANIMALTYPEID"], a["ENTRYREASONID"], a["SPECIESID"], a["DATEBROUGHTIN"])
    sql = db.make_insert_user_sql(dbo, "animal", username, (
        ( "ID", db.di(nid) ),
        ( "AnimalTypeID", db.di(a["ANIMALTYPEID"]) ),
        ( "ShelterCode", db.ds(sheltercode)),
        ( "ShortCode", db.ds(shortcode)),
        ( "UniqueCodeID", db.di(unique)),
        ( "YearCodeID", db.di(year)),
        ( "AnimalName", db.ds( _("Copy of {0}", l).format(a["ANIMALNAME"]))),
        ( "NonShelterAnimal", db.di(a["NONSHELTERANIMAL"])),
        ( "CrueltyCase", db.di(a["CRUELTYCASE"])),
        ( "BaseColourID", db.di(a["BASECOLOURID"])),
        ( "SpeciesID", db.di(a["SPECIESID"])),
        ( "BreedID", db.di(a["BREEDID"])),
        ( "Breed2ID", db.di(a["BREED2ID"])),
        ( "BreedName", db.ds(a["BREEDNAME"])),
        ( "CrossBreed", db.di(a["CROSSBREED"])),
        ( "CoatType", db.di(a["COATTYPE"])),
        ( "Markings", db.ds(a["MARKINGS"])),
        ( "AcceptanceNumber", db.ds(a["ACCEPTANCENUMBER"])),
        ( "DateOfBirth", db.dd(a["DATEOFBIRTH"])),
        ( "EstimatedDOB", db.di(a["ESTIMATEDDOB"])),
        ( "Fee", db.di(a["FEE"])),
        ( "AgeGroup", db.ds(a["AGEGROUP"])),
        ( "DeceasedDate", db.dd(a["DECEASEDDATE"])),
        ( "Sex", db.di(a["SEX"])),
        ( "Identichipped", db.di(a["IDENTICHIPPED"])),
        ( "IdentichipNumber", db.ds("")),
        ( "Tattoo", db.di(a["TATTOO"])),
        ( "TattooNumber", db.ds("")),
        ( "Neutered", db.di(a["NEUTERED"])),
        ( "NeuteredDate", db.dd(a["NEUTEREDDATE"])),
        # ASM2_COMPATIBILITY
        ( "CombiTested", db.di(a["COMBITESTED"])),
        ( "CombiTestDate", db.dd(a["COMBITESTDATE"])),
        ( "CombiTestResult", db.di(a["COMBITESTRESULT"])),
        ( "HeartwormTested", db.di(a["HEARTWORMTESTED"])),
        ( "HeartwormTestDate", db.dd(a["HEARTWORMTESTDATE"])),
        ( "HeartwormTestResult", db.di(a["HEARTWORMTESTRESULT"])),
        ( "FLVResult", db.di(a["FLVRESULT"])),
        # ASM2_COMPATIBILITY
        ( "SmartTag", db.di(0)),
        ( "SmartTagNumber", db.ds("")),
        ( "SmartTagType", db.di(0)),
        ( "Declawed", db.di(a["DECLAWED"])),
        ( "HiddenAnimalDetails", db.ds(a["HIDDENANIMALDETAILS"])),
        ( "AnimalComments", db.ds(a["ANIMALCOMMENTS"])),
        ( "OwnersVetID", db.di(a["OWNERSVETID"])),
        ( "CurrentVetID",  db.di(a["CURRENTVETID"])),
        ( "OriginalOwnerID", db.di(a["ORIGINALOWNERID"])),
        ( "BroughtInByOwnerID", db.di(a["BROUGHTINBYOWNERID"])),
        ( "AdoptionCoordinatorID", db.di(a["ADOPTIONCOORDINATORID"])),
        ( "ReasonForEntry", db.ds(a["REASONFORENTRY"])),
        ( "ReasonNO", db.ds(a["REASONNO"])),
        ( "DateBroughtIn", db.ddt(a["DATEBROUGHTIN"])),
        ( "EntryReasonID", db.di(a["ENTRYREASONID"])),
        ( "AsilomarIsTransferExternal", db.di(a["ASILOMARISTRANSFEREXTERNAL"])),
        ( "AsilomarIntakeCategory", db.di(a["ASILOMARINTAKECATEGORY"])),
        ( "AsilomarOwnerRequestedEuthanasia", db.di(a["ASILOMAROWNERREQUESTEDEUTHANASIA"])),
        ( "HealthProblems", db.ds(a["HEALTHPROBLEMS"])),
        ( "PutToSleep", db.di(a["PUTTOSLEEP"])),
        ( "PTSReason", db.ds(a["PTSREASON"])),
        ( "PTSReasonID", db.di(a["PTSREASONID"])),
        ( "IsDOA", db.di(a["ISDOA"])),
        ( "IsTransfer", db.di(a["ISTRANSFER"])),
        ( "IsPickup", db.di(a["ISPICKUP"])),
        ( "PickupLocationID", db.di(a["PICKUPLOCATIONID"])),
        ( "IsGoodWithCats", db.di(a["ISGOODWITHCATS"])),
        ( "IsGoodWithDogs", db.di(a["ISGOODWITHDOGS"])),
        ( "IsGoodWithChildren", db.di(a["ISGOODWITHCHILDREN"])),
        ( "IsHouseTrained", db.di(a["ISHOUSETRAINED"])),
        ( "IsNotAvailableForAdoption", db.di(a["ISNOTAVAILABLEFORADOPTION"])),
        ( "IsHold", db.di(a["ISHOLD"])),
        ( "HoldUntilDate", db.dd(a["HOLDUNTILDATE"])),
        ( "IsQuarantine", db.di(a["ISQUARANTINE"])),
        ( "HasSpecialNeeds", db.di(a["HASSPECIALNEEDS"])),
        ( "ShelterLocation", db.di(a["SHELTERLOCATION"])),
        ( "ShelterLocationUnit", db.ds(a["SHELTERLOCATIONUNIT"])),
        ( "Size", db.di(a["SIZE"])),
        ( "RabiesTag", db.ds(a["RABIESTAG"])),
        ( "BondedAnimalID", db.di(0)),
        ( "BondedAnimal2ID", db.di(0)),
        ( "Archived", db.di(0)),
        ( "ActiveMovementID", db.di(0)),
        ( "ActiveMovementType", db.di(0)),
        ( "DiedOffShelter", db.di(a["DIEDOFFSHELTER"]) ),
        ( "HasActiveReserve", db.di(0)),
        ( "MostRecentEntryDate", db.ddt(a["MOSTRECENTENTRYDATE"]))
        ))
    db.execute(dbo, sql)
    # Additional Fields
    for af in db.query(dbo, "SELECT * FROM additional WHERE LinkID = %d AND LinkType IN (%s)" % (animalid, additional.ANIMAL_IN)):
        sql = db.make_insert_sql("additional", (
            ( "LinkType", db.di(af["LINKTYPE"]) ),
            ( "LinkID", db.di(nid) ),
            ( "AdditionalFieldID", db.di(af["ADDITIONALFIELDID"]) ),
            ( "Value", db.ds(af["VALUE"])) ))
        db.execute(dbo, sql)
    # Vaccinations
    for v in db.query(dbo, "SELECT * FROM animalvaccination WHERE AnimalID = %d" % animalid):
        sql = db.make_insert_user_sql(dbo, "animalvaccination", username, (
            ( "ID", db.di(db.get_id(dbo, "animalvaccination")) ),
            ( "AnimalID", db.di(nid) ),
            ( "VaccinationID", db.di(v["VACCINATIONID"]) ),
            ( "DateOfVaccination", db.dd(v["DATEOFVACCINATION"]) ),
            ( "DateRequired", db.dd(v["DATEREQUIRED"]) ),
            ( "DateExpires", db.dd(v["DATEEXPIRES"]) ),
            ( "BatchNumber", db.ds(v["BATCHNUMBER"]) ),
            ( "AdministeringVetID", db.di(v["ADMINISTERINGVETID"]) ),
            ( "Manufacturer", db.ds(v["MANUFACTURER"]) ),
            ( "Cost", db.di(v["COST"]) ),
            ( "Comments", db.ds(v["COMMENTS"]) )
            ))
        db.execute(dbo, sql)
    # Tests
    for t in db.query(dbo, "SELECT * FROM animaltest WHERE AnimalID = %d" % animalid):
        sql = db.make_insert_user_sql(dbo, "animaltest", username, ( 
            ( "ID", db.di(db.get_id(dbo, "animaltest")) ),
            ( "AnimalID", db.di(nid)),
            ( "TestTypeID", db.di(t["TESTTYPEID"]) ),
            ( "TestResultID", db.di(t["TESTRESULTID"]) ),
            ( "DateOfTest", db.dd(t["DATEOFTEST"]) ),
            ( "DateRequired", db.dd(t["DATEREQUIRED"]) ),
            ( "AdministeringVetID", db.di(t["ADMINISTERINGVETID"]) ),
            ( "Cost", db.di(t["COST"]) ),
            ( "Comments", db.ds(t["COMMENTS"]) )
            ))
        db.execute(dbo, sql)
    # Medical
    for am in db.query(dbo, "SELECT * FROM animalmedical WHERE AnimalID = %d" % animalid):
        namid = db.get_id(dbo, "animalmedical")
        sql = db.make_insert_user_sql(dbo, "animalmedical", username, (
            ( "ID", db.di(namid)),
            ( "AnimalID", db.di(nid) ),
            ( "MedicalProfileID", db.di(am["MEDICALPROFILEID"]) ),
            ( "TreatmentName", db.ds(am["TREATMENTNAME"]) ),
            ( "StartDate", db.ds(am["STARTDATE"]) ),
            ( "Dosage", db.ds(am["DOSAGE"]) ),
            ( "Cost", db.di(am["COST"]) ),
            ( "TimingRule", db.di(am["TIMINGRULE"]) ),
            ( "TimingRuleFrequency", db.di(am["TIMINGRULEFREQUENCY"]) ),
            ( "TimingRuleNoFrequencies", db.di(am["TIMINGRULENOFREQUENCIES"]) ),
            ( "TreatmentRule", db.di(am["TREATMENTRULE"]) ),
            ( "TotalNumberOfTreatments", db.di(am["TOTALNUMBEROFTREATMENTS"]) ),
            ( "TreatmentsGiven", db.di(am["TREATMENTSGIVEN"]) ),
            ( "TreatmentsRemaining", db.di(am["TREATMENTSREMAINING"]) ),
            ( "Status", db.di(am["STATUS"]) ),
            ( "Comments", db.ds(am["COMMENTS"]) )
            ))
        db.execute(dbo, sql)
        for amt in db.query(dbo, "SELECT * FROM animalmedicaltreatment WHERE AnimalMedicalID = %d" % int(am["ID"])):
            sql = db.make_insert_user_sql(dbo, "animalmedicaltreatment", username, (
                ( "ID", db.di(db.get_id(dbo, "animalmedicaltreatment")) ),
                ( "AnimalID", db.di(nid) ),
                ( "AnimalMedicalID", db.di(namid) ),
                ( "DateRequired", db.dd(amt["DATEREQUIRED"])),
                ( "DateGiven", db.dd(amt["DATEGIVEN"])),
                ( "TreatmentNumber", db.di(amt["TREATMENTNUMBER"])),
                ( "TotalTreatments", db.di(amt["TOTALTREATMENTS"])),
                ( "AdministeringVetID", db.di(amt["ADMINISTERINGVETID"]) ),
                ( "GivenBy", db.ds(amt["GIVENBY"])),
                ( "Comments", db.ds(amt["COMMENTS"]))
                ))
            db.execute(dbo, sql)
    # Diet
    for d in db.query(dbo, "SELECT * FROM animaldiet WHERE AnimalID = %d" % animalid):
        sql = db.make_insert_user_sql(dbo, "animaldiet", username, (
            ( "ID", db.di(db.get_id(dbo, "animaldiet")) ),
            ( "AnimalID", db.di(nid) ),
            ( "DietID", db.di(d["DIETID"]) ),
            ( "DateStarted", db.dd(d["DATESTARTED"])),
            ( "Comments", db.ds(d["COMMENTS"]))
        ))
        db.execute(dbo, sql)
    # Costs
    for c in db.query(dbo, "SELECT * FROM animalcost WHERE AnimalID = %d" % animalid):
        sql = db.make_insert_user_sql(dbo, "animalcost", username, (
            ( "ID", db.di(db.get_id(dbo, "animalcost")) ),
            ( "AnimalID", db.di(nid) ),
            ( "CostTypeID", db.di(c["COSTTYPEID"])),
            ( "CostDate", db.dd(c["COSTDATE"])),
            ( "CostAmount", db.di(c["COSTAMOUNT"])),
            ( "Description", db.ds(c["DESCRIPTION"]))
        ))
        db.execute(dbo, sql)
    # Donations
    for dt in db.query(dbo, "SELECT * FROM ownerdonation WHERE AnimalID = %d" % animalid):
        sql = db.make_insert_user_sql(dbo, "ownerdonation", username, (
            ( "ID", db.di(db.get_id(dbo, "ownerdonation")) ),
            ( "AnimalID", db.di(nid) ),
            ( "OwnerID", db.di(dt["OWNERID"])),
            ( "MovementID", db.di(0)),
            ( "DonationTypeID", db.di(dt["DONATIONTYPEID"])),
            ( "DonationPaymentID", db.di(dt["DONATIONPAYMENTID"])),
            ( "Date", db.dd(dt["DATE"])),
            ( "DateDue", db.dd(dt["DATEDUE"])),
            ( "Donation", db.di(dt["DONATION"])),
            ( "IsGiftAid", db.di(dt["ISGIFTAID"])),
            ( "Frequency", db.di(dt["FREQUENCY"])),
            ( "NextCreated", db.di(dt["NEXTCREATED"])),
            ( "Comments", db.ds(dt["COMMENTS"]))
        ))
        db.execute(dbo, sql)
    # Diary
    for di in db.query(dbo, "SELECT * FROM diary WHERE LinkType = 1 AND LinkID = %d" % animalid):
        sql = db.make_insert_user_sql(dbo, "diary", username, (
            ( "ID", db.di(db.get_id(dbo, "diary")) ),
            ( "LinkID", db.di(nid) ),
            ( "LinkType", db.di(1) ),
            ( "DiaryDateTime", db.ddt(di["DIARYDATETIME"])),
            ( "DiaryForName", db.ds(di["DIARYFORNAME"])),
            ( "Subject", db.ds(di["SUBJECT"])),
            ( "Note", db.ds(di["NOTE"])),
            ( "DateCompleted", db.dd(di["DATECOMPLETED"])),
            ( "LinkInfo", db.ds(diary.get_link_info(dbo, 1, nid)))
        ))
        db.execute(dbo, sql)
    # Media
    for me in db.query(dbo, "SELECT * FROM media WHERE LinkTypeID = %d AND LinkID = %d" % (media.ANIMAL, animalid)):
        ext = me["MEDIANAME"]
        ext = ext[ext.rfind("."):].lower()
        mediaid = db.get_id(dbo, "media")
        medianame = "%d%s" % ( mediaid, ext )
        sql = db.make_insert_sql("media", (
            ( "ID", db.di(mediaid) ),
            ( "MediaName", db.ds(medianame) ),
            ( "MediaType", db.di(me["MEDIATYPE"]) ),
            ( "MediaNotes", db.ds(me["MEDIANOTES"]) ),
            ( "WebsitePhoto", db.di(me["WEBSITEPHOTO"]) ),
            ( "WebsiteVideo", db.di(me["WEBSITEVIDEO"]) ),
            ( "DocPhoto", db.di(me["DOCPHOTO"]) ),
            ( "ExcludeFromPublish", db.di(0) ),
            # ASM2_COMPATIBILITY
            ( "NewSinceLastPublish", db.di(1) ),
            ( "UpdatedSinceLastPublish", db.di(0) ),
            # ASM2_COMPATIBILITY
            ( "LinkID", db.di(nid) ),
            ( "LinkTypeID", db.di(media.ANIMAL) ),
            ( "Date", db.dd(me["DATE"]))
            ))
        db.execute(dbo, sql)
        # Now clone the dbfs item pointed to by this media item if it's a file
        if me["MEDIATYPE"] == media.MEDIATYPE_FILE:
            filedata = dbfs.get_string(dbo, me["MEDIANAME"])
            dbfs.put_string(dbo, medianame, "/animal/%d" % animalid, filedata)
    # Movements
    for mv in db.query(dbo, "SELECT * FROM adoption WHERE AnimalID = %d" % animalid):
        nadid = db.get_id(dbo, "adoption")
        sql = db.make_insert_user_sql(dbo, "adoption", username, (
            ( "ID", db.di(nadid) ),
            ( "AnimalID", db.di(nid) ),
            ( "OwnerID", db.di(mv["OWNERID"])),
            ( "RetailerID", db.di(mv["RETAILERID"])),
            ( "AdoptionNumber", db.ds(utils.padleft(nadid, 6))),
            ( "OriginalRetailerMovementID", db.di(0)),
            ( "MovementDate", db.dd(mv["MOVEMENTDATE"])),
            ( "MovementType", db.di(mv["MOVEMENTTYPE"])),
            ( "ReturnDate", db.dd(mv["RETURNDATE"])),
            ( "ReturnedReasonID", db.di(mv["RETURNEDREASONID"])),
            ( "InsuranceNumber", db.ds(mv["INSURANCENUMBER"])),
            ( "ReasonForReturn", db.ds(mv["REASONFORRETURN"])),
            ( "ReservationDate", db.dd(mv["RESERVATIONDATE"])),
            ( "Donation", db.di(mv["DONATION"])),
            ( "ReservationCancelledDate", db.dd(mv["RESERVATIONCANCELLEDDATE"])),
            ( "Comments", db.ds(mv["COMMENTS"]))
        ))
        db.execute(dbo, sql)
    # Log
    for lo in db.query(dbo, "SELECT * FROM log WHERE LinkType = %d AND LinkID = %d" % (log.ANIMAL, animalid)):
        sql = db.make_insert_user_sql(dbo, "log", username, (
            ( "ID", db.di(db.get_id(dbo, "log")) ),
            ( "LinkID", db.di(nid) ),
            ( "LinkType", db.di(log.ANIMAL) ),
            ( "LogTypeID", db.di(lo["LOGTYPEID"])),
            ( "Date", db.ddt(lo["DATE"])),
            ( "Comments", db.ds(lo["COMMENTS"]))
        ))
        db.execute(dbo, sql)
    audit.create(dbo, username, "animal", nid, audit.dump_row(dbo, "animal", nid))
    update_animal_status(dbo, nid)
    update_variable_animal_data(dbo, nid)
    return nid

def clone_from_template(dbo, username, animalid, dob, animaltypeid, speciesid):
    """
    Tries to locate a non-shelter animal called "TemplateType" with animaltypeid,
    if it doesn't find one, it looks for a non-shelter animal called "TemplateSpecies"
    with speciesid. If one is not found, does nothing.
    If the animal is deemed to be a baby according to the baby split defined for the
    annual figures report, will check for "TemplateTypeBaby" or "TemplateTypeSpecies" first.
    Clones appropriate medical, cost and diet info from the template animal.
    """
    babyqueries = [
        "SELECT ID FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatetypebaby' AND AnimalTypeID = %d" % animaltypeid,
        "SELECT ID FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatespeciesbaby' AND SpeciesID = %d" % speciesid,
        "SELECT ID FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatetype' AND AnimalTypeID = %d" % animaltypeid,
        "SELECT ID FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatespecies' AND SpeciesID = %d" % speciesid
    ]
    adultqueries = [ 
        "SELECT ID FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatetype' AND AnimalTypeID = %d" % animaltypeid,
        "SELECT ID FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatespecies' AND SpeciesID = %d" % speciesid
    ]
    queries = adultqueries
    # If this is a baby animal as defined by its age, use the babyqueries to look for a template
    babymonths = configuration.annual_figures_baby_months(dbo)
    babydays = babymonths * 30.5
    # 12 * 30.5 = 366 so it's one day out for a year
    if babymonths == 12: babydays = 365
    if date_diff_days(dob, now()) < babydays:
        queries = babyqueries
    # Use our queries to find a potential template
    for q in queries:
        cloneanimalid = db.query_int(dbo, q)
        if cloneanimalid != 0: break
    # Give up if we didn't find a template animal
    if cloneanimalid == 0:
        return
    # Any animal fields that should be copied to the new record
    broughtin = db.query_date(dbo, "SELECT DateBroughtIn FROM animal WHERE ID = %d" % cloneanimalid)
    copyfrom = db.query(dbo, "SELECT Fee, AnimalComments FROM animal WHERE ID = %d" % cloneanimalid)
    sql = db.make_update_user_sql(dbo, "animal", username, "ID=%d" % animalid, (
        ( "Fee", db.di(copyfrom[0]["FEE"]) ),
        ( "AnimalComments", db.ds(copyfrom[0]["ANIMALCOMMENTS"]) )
        ))
    db.execute(dbo, sql)
    # Helper function to work out the difference between intake and a date and add that
    # difference to today to get a new date
    def adjust_date(d):
        dayoffset = date_diff_days(broughtin, d)
        return db.dd(add_days(now(dbo.timezone), dayoffset))
    # Additional Fields (don't include mandatory ones as they are already set by new animal screen)
    for af in db.query(dbo, "SELECT a.* FROM additional a INNER JOIN additionalfield af ON af.ID = a.AdditionalFieldID WHERE af.Mandatory <> 1 AND a.LinkID = %d AND a.LinkType IN (%s)" % (cloneanimalid, additional.ANIMAL_IN)):
        sql = db.make_insert_sql("additional", (
            ( "LinkType", db.di(af["LINKTYPE"]) ),
            ( "LinkID", db.di(animalid) ),
            ( "AdditionalFieldID", db.di(af["ADDITIONALFIELDID"]) ),
            ( "Value", db.ds(af["VALUE"])) ))
        db.execute(dbo, sql)
    # Vaccinations
    for v in db.query(dbo, "SELECT * FROM animalvaccination WHERE AnimalID = %d" % cloneanimalid):
        newdate = adjust_date(v["DATEREQUIRED"])
        sql = db.make_insert_user_sql(dbo, "animalvaccination", username, (
            ( "ID", db.di(db.get_id(dbo, "animalvaccination")) ),
            ( "AnimalID", db.di(animalid) ),
            ( "VaccinationID", db.di(v["VACCINATIONID"]) ),
            ( "DateOfVaccination", db.dd(None) ),
            ( "DateRequired", newdate ),
            ( "DateExpires", db.dd(None) ),
            ( "AdministeringVetID", db.di(v["ADMINISTERINGVETID"]) ),
            ( "BatchNumber", db.ds(v["BATCHNUMBER"]) ),
            ( "Manufacturer", db.ds(v["MANUFACTURER"]) ),
            ( "Cost", db.di(v["COST"]) ),
            ( "Comments", db.ds(v["COMMENTS"]) )
            ))
        db.execute(dbo, sql)
    # Tests
    for t in db.query(dbo, "SELECT * FROM animaltest WHERE AnimalID = %d" % cloneanimalid):
        newdate = adjust_date(t["DATEREQUIRED"])
        sql = db.make_insert_user_sql(dbo, "animaltest", username, ( 
            ( "ID", db.di(db.get_id(dbo, "animaltest")) ),
            ( "AnimalID", db.di(animalid)),
            ( "TestTypeID", db.di(t["TESTTYPEID"]) ),
            ( "TestResultID", db.di(t["TESTRESULTID"]) ),
            ( "DateOfTest", db.dd(None) ),
            ( "DateRequired", newdate ),
            ( "AdministeringVetID", db.di(t["ADMINISTERINGVETID"]) ),
            ( "Cost", db.di(t["COST"]) ),
            ( "Comments", db.ds(t["COMMENTS"]) )
            ))
        db.execute(dbo, sql)
    # Medical
    for am in db.query(dbo, "SELECT * FROM animalmedical WHERE AnimalID = %d" % cloneanimalid):
        namid = db.get_id(dbo, "animalmedical")
        newdate = adjust_date(am["STARTDATE"])
        sql = db.make_insert_user_sql(dbo, "animalmedical", username, (
            ( "ID", db.di(namid)),
            ( "AnimalID", db.di(animalid) ),
            ( "MedicalProfileID", db.di(am["MEDICALPROFILEID"]) ),
            ( "TreatmentName", db.ds(am["TREATMENTNAME"]) ),
            ( "StartDate", newdate ),
            ( "Dosage", db.ds(am["DOSAGE"]) ),
            ( "Cost", db.di(am["COST"]) ),
            ( "TimingRule", db.di(am["TIMINGRULE"]) ),
            ( "TimingRuleFrequency", db.di(am["TIMINGRULEFREQUENCY"]) ),
            ( "TimingRuleNoFrequencies", db.di(am["TIMINGRULENOFREQUENCIES"]) ),
            ( "TreatmentRule", db.di(am["TREATMENTRULE"]) ),
            ( "TotalNumberOfTreatments", db.di(am["TOTALNUMBEROFTREATMENTS"]) ),
            ( "TreatmentsGiven", db.di(am["TREATMENTSGIVEN"]) ),
            ( "TreatmentsRemaining", db.di(am["TREATMENTSREMAINING"]) ),
            ( "Status", db.di(am["STATUS"]) ),
            ( "Comments", db.ds(am["COMMENTS"]) )
            ))
        db.execute(dbo, sql)
        for amt in db.query(dbo, "SELECT * FROM animalmedicaltreatment WHERE AnimalMedicalID = %d" % int(am["ID"])):
            sql = db.make_insert_user_sql(dbo, "animalmedicaltreatment", username, (
                ( "ID", db.di(db.get_id(dbo, "animalmedicaltreatment")) ),
                ( "AnimalID", db.di(animalid) ),
                ( "AnimalMedicalID", db.di(namid) ),
                ( "DateRequired", newdate ),
                ( "DateGiven", db.dd(None) ),
                ( "TreatmentNumber", db.di(amt["TREATMENTNUMBER"])),
                ( "TotalTreatments", db.di(amt["TOTALTREATMENTS"])),
                ( "AdministeringVetID", db.di(amt["ADMINISTERINGVETID"]) ),
                ( "GivenBy", db.ds(amt["GIVENBY"])),
                ( "Comments", db.ds(amt["COMMENTS"]))
                ))
            db.execute(dbo, sql)
    # Diet
    for d in db.query(dbo, "SELECT * FROM animaldiet WHERE AnimalID = %d" % cloneanimalid):
        newdate = adjust_date(d["DATESTARTED"])
        sql = db.make_insert_user_sql(dbo, "animaldiet", username, (
            ( "ID", db.di(db.get_id(dbo, "animaldiet")) ),
            ( "AnimalID", db.di(animalid) ),
            ( "DietID", db.di(d["DIETID"]) ),
            ( "DateStarted", newdate ),
            ( "Comments", db.ds(d["COMMENTS"]))
        ))
        db.execute(dbo, sql)
    # Costs
    for c in db.query(dbo, "SELECT * FROM animalcost WHERE AnimalID = %d" % cloneanimalid):
        newdate = adjust_date(c["COSTDATE"])
        sql = db.make_insert_user_sql(dbo, "animalcost", username, (
            ( "ID", db.di(db.get_id(dbo, "animalcost")) ),
            ( "AnimalID", db.di(animalid) ),
            ( "CostTypeID", db.di(c["COSTTYPEID"])),
            ( "CostDate", newdate ),
            ( "CostAmount", db.di(c["COSTAMOUNT"])),
            ( "Description", db.ds(c["DESCRIPTION"]))
        ))
        db.execute(dbo, sql)

def delete_animal(dbo, username, animalid):
    """
    Deletes an animal and all its satellite records.
    """
    l = dbo.locale
    if db.query_int(dbo, "SELECT COUNT(ID) FROM adoption WHERE AnimalID=%d" % animalid):
        raise utils.ASMValidationError(_("This animal has movements and cannot be removed.", l))
    audit.delete_rows(dbo, username, "media", "LinkID = %d AND LinkTypeID = %d" % (animalid, media.ANIMAL))
    db.execute(dbo, "DELETE FROM media WHERE LinkID = %d AND LinkTypeID = %d" % (animalid, media.ANIMAL))
    audit.delete_rows(dbo, username, "diary", "LinkID = %d AND LinkType = %d" % (animalid, diary.ANIMAL))
    db.execute(dbo, "DELETE FROM diary WHERE LinkID = %d AND LinkType = %d" % (animalid, diary.ANIMAL))
    audit.delete_rows(dbo, username, "log", "LinkID = %d AND LinkType = %d" % (animalid, log.ANIMAL))
    db.execute(dbo, "DELETE FROM log WHERE LinkID = %d AND LinkType = %d" % (animalid, log.ANIMAL))
    db.execute(dbo, "DELETE FROM additional WHERE LinkID = %d AND LinkType IN (%s)" % (animalid, additional.ANIMAL_IN))
    db.execute(dbo, "DELETE FROM animalcontrolanimal WHERE AnimalID = %d" % animalid)
    db.execute(dbo, "DELETE FROM animalpublished WHERE AnimalID = %d" % animalid)
    for t in [ "adoption", "animalmedical", "animalmedicaltreatment", "animaltest", "animaltransport", "animalvaccination" ]:
        audit.delete_rows(dbo, username, t, "AnimalID = %d" % animalid)
        db.execute(dbo, "DELETE FROM %s WHERE AnimalID = %d" % (t, animalid))
    dbfs.delete_path(dbo, "/animal/%d" % animalid)
    audit.delete(dbo, username, "animal", animalid, audit.dump_row(dbo, "animal", animalid))
    db.execute(dbo, "DELETE FROM animal WHERE ID = %d" % animalid)

def update_daily_boarding_cost(dbo, username, animalid, cost):
    """
    Updates the daily boarding cost amount for an animal. The
    cost parameter should have already been turned into an integer.
    """
    oldcost = db.query_string(dbo, "SELECT DailyBoardingCost FROM animal WHERE ID = %d" % int(animalid) )
    db.execute(dbo, "UPDATE animal SET DailyBoardingCost = %s WHERE ID = %d" % ( str(cost), int(animalid) ))
    audit.edit(dbo, username, "animal", animalid, "%s: DailyBoardingCost %s ==> %s" % ( str(animalid), oldcost, str(cost) ))

def update_preferred_web_media_notes(dbo, username, animalid, newnotes):
    """
    Updates the preferred web media notes for an animal.
    """
    mediaid = db.query_int(dbo, "SELECT ID FROM media WHERE " \
        "WebsitePhoto = 1 AND LinkID = %d AND LinkTypeID = %d" % \
        (int(animalid), media.ANIMAL))
    if mediaid > 0:
        db.execute(dbo, "UPDATE media SET MediaNotes = '%s', UpdatedSinceLastPublish = 1 WHERE " \
            "ID = %d" % (db.escape(newnotes), mediaid))
        audit.edit(dbo, username, "media", mediaid, str(mediaid) + "notes => " + newnotes)
 
def insert_diet_from_form(dbo, username, post):
    """
    Creates a diet record from posted form data
    """
    return dbo.insert("animaldiet", {
        "AnimalID":     post.integer("animalid"),
        "DietID":       post.integer("type"),
        "DateStarted":  post.date("startdate"),
        "Comments":     post["comments"]
    }, username)

def update_diet_from_form(dbo, username, post):
    """
    Updates a diet record from posted form data
    """
    dbo.update("animaldiet", post.integer("dietid"), {
        "DietID":       post.integer("type"),
        "DateStarted":  post.date("startdate"),
        "Comments":     post["comments"]
    }, username)

def delete_diet(dbo, username, did):
    """
    Deletes the selected diet
    """
    dbo.delete("animaldiet", did, username)

def insert_cost_from_form(dbo, username, post):
    """
    Creates a cost record from posted form data
    """
    l = dbo.locale
    ncostid = db.get_id(dbo, "animalcost")
    if post.date("costdate") is None:
        raise utils.ASMValidationError(_("Cost date must be a valid date", l))
    sql = db.make_insert_user_sql(dbo, "animalcost", username, ( 
        ( "ID", db.di(ncostid)),
        ( "AnimalID", post.db_integer("animalid")),
        ( "CostTypeID", post.db_integer("type")),
        ( "CostDate", post.db_date("costdate")),
        ( "CostPaidDate", post.db_date("costpaid")),
        ( "CostAmount", post.db_integer("cost")),
        ( "Description", post.db_string("description"))
        ))
    db.execute(dbo, sql)
    audit.create(dbo, username, "animalcost", ncostid, audit.dump_row(dbo, "animalcost", ncostid))
    financial.update_matching_cost_transaction(dbo, username, ncostid)
    return ncostid

def update_cost_from_form(dbo, username, post):
    """
    Updates a cost record from posted form data
    """
    costid = post.integer("costid")
    sql = db.make_update_user_sql(dbo, "animalcost", username, "ID=%d" % costid, ( 
        ( "CostTypeID", post.db_integer("type")),
        ( "CostDate", post.db_date("costdate")),
        ( "CostPaidDate", post.db_date("costpaid")),
        ( "CostAmount", post.db_integer("cost")),
        ( "Description", post.db_string("description"))
        ))
    preaudit = db.query(dbo, "SELECT * FROM animalcost WHERE ID = %d" % costid)
    db.execute(dbo, sql)
    postaudit = db.query(dbo, "SELECT * FROM animalcost WHERE ID = %d" % costid)
    audit.edit(dbo, username, "animalcost", costid, audit.map_diff(preaudit, postaudit))
    financial.update_matching_cost_transaction(dbo, username, costid)

def delete_cost(dbo, username, cid):
    """
    Deletes a cost record
    """
    audit.delete(dbo, username, "animalcost", cid, audit.dump_row(dbo, "animalcost", cid))
    db.execute(dbo, "DELETE FROM animalcost WHERE ID = %d" % cid)

def insert_litter_from_form(dbo, username, post):
    """
    Creates a litter record from posted form data
    """
    nid = db.get_id(dbo, "animallitter")
    sql = db.make_insert_sql("animallitter", ( 
        ( "ID", db.di(nid)),
        ( "ParentAnimalID", post.db_integer("animal")),
        ( "SpeciesID", post.db_integer("species")),
        ( "Date", post.db_date("startdate")),
        ( "AcceptanceNumber", post.db_string("litterref")),
        ( "CachedAnimalsLeft", db.di(0)),
        ( "InvalidDate", post.db_date("expirydate")),
        ( "NumberInLitter", post.db_integer("numberinlitter")),
        ( "Comments", post.db_string("comments")),
        ( "RecordVersion", db.di(0))
        ))
    db.execute(dbo, sql)
    audit.create(dbo, username, nid, "animallitter", audit.dump_row(dbo, "animallitter", nid))
    update_active_litters(dbo)
    # if a list of littermates were given, set the litterid on those animal records
    for i in post.integer_list("animals"):
        db.execute(dbo, "UPDATE animal SET AcceptanceNumber = %s WHERE ID = %d" % (post.db_string("litterref"), i))
    return nid

def update_litter_from_form(dbo, username, post):
    """
    Updates a litter record from posted form data
    """
    litterid = post.integer("litterid")
    sql = db.make_update_sql("animallitter", "ID=%d" % litterid, ( 
        ( "ParentAnimalID", post.db_integer("animal")),
        ( "SpeciesID", post.db_integer("species")),
        ( "Date", post.db_date("startdate")),
        ( "AcceptanceNumber", post.db_string("litterref")),
        ( "CachedAnimalsLeft", db.di(0)),
        ( "InvalidDate", post.db_date("expirydate")),
        ( "NumberInLitter", post.db_integer("numberinlitter")),
        ( "Comments", post.db_string("comments")),
        ( "RecordVersion", db.di(0))
        ))
    preaudit = db.query(dbo, "SELECT * FROM animallitter WHERE ID = %d" % litterid)
    db.execute(dbo, sql)
    postaudit = db.query(dbo, "SELECT * FROM animallitter WHERE ID = %d" % litterid)
    audit.edit(dbo, username, "animallitter", litterid, audit.map_diff(preaudit, postaudit))
    update_active_litters(dbo)

def delete_litter(dbo, username, lid):
    """
    Deletes the selected litter
    """
    audit.delete(dbo, username, "animallitter", lid, audit.dump_row(dbo, "animallitter", lid))
    db.execute(dbo, "DELETE FROM animallitter WHERE ID = %d" % int(lid))

def update_animal_check_bonds(dbo, animalid):
    """
    Checks the bonds on animalid and if necessary, creates
    links back to animalid from the bonded animals
    """

    def addbond(tanimalid, bondid):
        tbond = db.query(dbo, "SELECT BondedAnimalID, BondedAnimal2ID FROM animal WHERE ID = %d" % int(tanimalid))
        if len(tbond) == 0: return
        # If a bond already exists, don't do anything
        if tbond[0]["BONDEDANIMALID"] == bondid: return
        if tbond[0]["BONDEDANIMAL2ID"] == bondid: return
        # Add a bond if we have a free slot
        if tbond[0]["BONDEDANIMALID"] == 0:
            db.execute(dbo, "UPDATE animal SET BondedAnimalID = %d WHERE ID = %d" % ( int(bondid), int(tanimalid) ))
            return
        if tbond[0]["BONDEDANIMAL2ID"] == 0:
            db.execute(dbo, "UPDATE animal SET BondedAnimal2ID = %d WHERE ID = %d" % ( int(bondid), int(tanimalid) ))

    bonds = db.query(dbo, "SELECT BondedAnimalID, BondedAnimal2ID FROM animal WHERE ID = %d" % int(animalid))
    if len(bonds) == 0: return
    bond1 = bonds[0]["BONDEDANIMALID"]
    bond2 = bonds[0]["BONDEDANIMAL2ID"]
    if bond1 != 0: addbond(bond1, animalid)
    if bond2 != 0: addbond(bond2, animalid)

def update_variable_animal_data(dbo, animalid, a = None, animalupdatebatch = None, bands = None, movements = None):
    """
    Updates the variable data animal fields,
    MostRecentEntryDate, TimeOnShelter, DaysOnShelter, AgeGroup, AnimalAge,
    TotalTimeOnShelter, TotalDaysOnShelter
    (int) animalid: The animal to update
    a: An animal result to use instead of looking it up from the id
    animalupdatebatch: A batch of update parameters
    bands: List of loaded age group bands
    movements: List of loaded movements
    """
    if animalupdatebatch is not None:
        animalupdatebatch.append((
            calc_time_on_shelter(dbo, animalid, a),
            calc_age_group(dbo, animalid, a, bands),
            calc_age(dbo, animalid, a),
            calc_days_on_shelter(dbo, animalid, a),
            calc_total_time_on_shelter(dbo, animalid, a, movements),
            calc_total_days_on_shelter(dbo, animalid, a, movements),
            animalid
        ))
    else:
        s = db.make_update_sql("animal", "ID = %d" % animalid, (
            ( "TimeOnShelter", db.ds(calc_time_on_shelter(dbo, animalid, a))),
            ( "AgeGroup", db.ds(calc_age_group(dbo, animalid, a))),
            ( "AnimalAge", db.ds(calc_age(dbo, animalid, a))),
            ( "DaysOnShelter", db.di(calc_days_on_shelter(dbo, animalid, a))),
            ( "TotalTimeOnShelter", db.ds(calc_total_time_on_shelter(dbo, animalid, a))),
            ( "TotalDaysOnShelter", db.di(calc_total_days_on_shelter(dbo, animalid, a)))
        ))
        db.execute(dbo, s)

def update_all_variable_animal_data(dbo):
    """
    Updates variable animal data for all animals. This is a big memory heavy routine is you've
    got a lot of animal and movement records as loads sections of both complete tables into RAM.
    """
    l = dbo.locale
    
    animalupdatebatch = []

    # Load age group bands now to save repeated looped lookups
    bands = db.query(dbo, "SELECT ItemName, ItemValue FROM configuration WHERE ItemName LIKE 'AgeGroup%' ORDER BY ItemName")

    # Relevant fields
    animals = db.query(dbo, "SELECT ID, DateBroughtIn, DeceasedDate, DiedOffShelter, Archived, ActiveMovementDate, " \
        "MostRecentEntryDate, DateOfBirth FROM animal")

    # Get a single lookup of movement histories for our animals
    movements = db.query(dbo, "SELECT ad.AnimalID, ad.MovementDate, ad.ReturnDate " \
        "FROM adoption ad INNER JOIN animal a ON a.ID = ad.AnimalID " \
        "WHERE ad.MovementType NOT IN (2,8) AND ad.MovementDate Is Not Null AND ad.ReturnDate Is Not Null " \
        "ORDER BY AnimalID")

    for a in animals:
        update_variable_animal_data(dbo, int(a["ID"]), a, animalupdatebatch, bands, movements)

    dbo.execute_many("UPDATE animal SET " \
        "TimeOnShelter = ?, " \
        "AgeGroup = ?, " \
        "AnimalAge = ?, " \
        "DaysOnShelter = ?, " \
        "TotalTimeOnShelter = ?, " \
        "TotalDaysOnShelter = ? " \
        "WHERE ID = ?", animalupdatebatch)

    al.debug("updated variable data for %d animals (locale %s)" % (len(animals), l), "animal.update_all_variable_animal_data", dbo)
    return "OK %d" % len(animals)

def update_on_shelter_variable_animal_data(dbo):
    """
    Updates variable animal data for all shelter animals.
    """
    l = dbo.locale
    
    animalupdatebatch = []

    # Load age group bands now to save repeated looped lookups
    bands = db.query(dbo, "SELECT ItemName, ItemValue FROM configuration WHERE ItemName LIKE 'AgeGroup%' ORDER BY ItemName")

    # Relevant on shelter animal fields
    animals = db.query(dbo, "SELECT ID, DateBroughtIn, DeceasedDate, DiedOffShelter, Archived, ActiveMovementDate, " \
        "MostRecentEntryDate, DateOfBirth FROM animal WHERE Archived = 0")

    # Get a single lookup of movement histories for our on shelter animals
    movements = db.query(dbo, "SELECT ad.AnimalID, ad.MovementDate, ad.ReturnDate " \
        "FROM animal a " \
        "INNER JOIN adoption ad ON a.ID = ad.AnimalID " \
        "WHERE a.Archived = 0 AND ad.MovementType NOT IN (2,8) " \
        "AND ad.MovementDate Is Not Null AND ad.ReturnDate Is Not Null " \
        "ORDER BY a.ID")

    for a in animals:
        update_variable_animal_data(dbo, int(a["ID"]), a, animalupdatebatch, bands, movements)

    dbo.execute_many("UPDATE animal SET " \
        "TimeOnShelter = ?, " \
        "AgeGroup = ?, " \
        "AnimalAge = ?, " \
        "DaysOnShelter = ?, " \
        "TotalTimeOnShelter = ?, " \
        "TotalDaysOnShelter = ? " \
        "WHERE ID = ?", animalupdatebatch)

    al.debug("updated variable data for %d animals (locale %s)" % (len(animals), l), "animal.update_on_shelter_variable_animal_data", dbo)
    return "OK %d" % len(animals)

def update_all_animal_statuses(dbo):
    """
    Updates statuses for all animals
    """
    animals = db.query(dbo, get_animal_status_query(dbo))
    movements = db.query(dbo, get_animal_movement_status_query(dbo) + " ORDER BY MovementDate DESC")
    animalupdatebatch = []
    diaryupdatebatch = []
    cfg = {
        "foster_on_shelter": configuration.foster_on_shelter(dbo),
        "retailer_on_shelter": configuration.retailer_on_shelter(dbo),
        "trial_on_shelter": configuration.trial_on_shelter(dbo)
    }

    async.set_progress_max(dbo, len(animals))
    for a in animals:
        update_animal_status(dbo, int(a["ID"]), a, movements, animalupdatebatch, diaryupdatebatch, cfg)
        async.increment_progress_value(dbo)

    aff = dbo.execute_many("UPDATE animal SET " \
        "Archived = ?, " \
        "ActiveMovementID = ?, " \
        "ActiveMovementDate = ?, " \
        "ActiveMovementType = ?, " \
        "ActiveMovementReturn = ?, " \
        "DiedOffShelter = ?, " \
        "DisplayLocation = ?, " \
        "HasActiveReserve = ?, " \
        "HasTrialAdoption = ?, " \
        "HasPermanentFoster = ?, " \
        "MostRecentEntryDate = ? " \
        "WHERE ID = ?", animalupdatebatch)
    dbo.execute_many("UPDATE diary SET LinkInfo = ? WHERE LinkType = ? AND LinkID = ?", diaryupdatebatch)
    al.debug("updated %d animal statuses (%d)" % (aff, len(animals)), "animal.update_all_animal_statuses", dbo)
    return "OK %d" % len(animals)

def update_foster_animal_statuses(dbo):
    """
    Updates statuses for all animals on foster. 
    This function is redundant if foster_on_shelter is set as they 
    will already be updated by update_on_shelter_animal_statuses.
    To counter that, this function only considers fosters/off shelter
    """
    animals = db.query(dbo, get_animal_status_query(dbo) + " WHERE a.ActiveMovementType = 2 AND a.Archived = 1")
    movements = db.query(dbo, get_animal_movement_status_query(dbo) + \
        " WHERE AnimalID IN (SELECT ID FROM animal WHERE ActiveMovementType = 2) ORDER BY MovementDate DESC")
    animalupdatebatch = []
    diaryupdatebatch = []
    cfg = {
        "foster_on_shelter": configuration.foster_on_shelter(dbo),
        "retailer_on_shelter": configuration.retailer_on_shelter(dbo),
        "trial_on_shelter": configuration.trial_on_shelter(dbo)
    }

    for a in animals:
        update_animal_status(dbo, int(a["ID"]), a, movements, animalupdatebatch, diaryupdatebatch, cfg)

    aff = dbo.execute_many("UPDATE animal SET " \
        "Archived = ?, " \
        "ActiveMovementID = ?, " \
        "ActiveMovementDate = ?, " \
        "ActiveMovementType = ?, " \
        "ActiveMovementReturn = ?, " \
        "DiedOffShelter = ?, " \
        "DisplayLocation = ?, " \
        "HasActiveReserve = ?, " \
        "HasTrialAdoption = ?, " \
        "HasPermanentFoster = ?, " \
        "MostRecentEntryDate = ? " \
        "WHERE ID = ?", animalupdatebatch)
    dbo.execute_many("UPDATE diary SET LinkInfo = ? WHERE LinkType = ? AND LinkID = ?", diaryupdatebatch)
    al.debug("updated %d fostered animal statuses (%d)" % (aff, len(animals)), "animal.update_foster_animal_statuses", dbo)
    return "OK %d" % len(animals)

def update_on_shelter_animal_statuses(dbo):
    """
    Updates statuses for all animals currently on shelter 
    or scheduled for return from yesterday or newer.
    """
    cutoff = subtract_days(now(dbo.timezone), 1)
    animals = db.query(dbo, get_animal_status_query(dbo) + " WHERE a.Archived = 0 OR (a.Archived = 1 AND a.ActiveMovementReturn > %s)" % db.dd(cutoff))
    movements = db.query(dbo, get_animal_movement_status_query(dbo) + \
        " WHERE AnimalID IN (SELECT ID FROM animal WHERE Archived = 0 OR (Archived = 1 AND ActiveMovementReturn > %s)) ORDER BY MovementDate DESC" % db.dd(cutoff))
    animalupdatebatch = []
    diaryupdatebatch = []
    cfg = {
        "foster_on_shelter": configuration.foster_on_shelter(dbo),
        "retailer_on_shelter": configuration.retailer_on_shelter(dbo),
        "trial_on_shelter": configuration.trial_on_shelter(dbo)
    }

    async.set_progress_max(dbo, len(animals))
    for a in animals:
        update_animal_status(dbo, int(a["ID"]), a, movements, animalupdatebatch, diaryupdatebatch, cfg)
        async.increment_progress_value(dbo)

    aff = dbo.execute_many("UPDATE animal SET " \
        "Archived = ?, " \
        "ActiveMovementID = ?, " \
        "ActiveMovementDate = ?, " \
        "ActiveMovementType = ?, " \
        "ActiveMovementReturn = ?, " \
        "DiedOffShelter = ?, " \
        "DisplayLocation = ?, " \
        "HasActiveReserve = ?, " \
        "HasTrialAdoption = ?, " \
        "HasPermanentFoster = ?, " \
        "MostRecentEntryDate = ? " \
        "WHERE ID = ?", animalupdatebatch)
    dbo.execute_many("UPDATE diary SET LinkInfo = ? WHERE LinkType = ? AND LinkID = ?", diaryupdatebatch)
    al.debug("updated %d on shelter animal statuses (%d)" % (aff, len(animals)), "animal.update_on_shelter_animal_statuses", dbo)
    return "OK %d" % len(animals)

def update_animal_status(dbo, animalid, a = None, movements = None, animalupdatebatch = None, diaryupdatebatch = None, cfg = None):
    """
    Updates the movement status fields on an animal record: 
        ActiveMovement*, HasActiveReserve, HasTrialAdoption, MostRecentEntryDate, 
        DiedOffShelter, Archived and DisplayLocation.

    a can be an already loaded animal record
    movements is a list of movements for this animal (and can be for other animals too)
    animalupdatebatch and diaryupdatebatch are lists of parameters that can be passed to
    db.execute_many to do all updates in one hit where necessary. If they are passed, we'll
    append our changes to them. If they aren't passed, then we do any database updates now.
    """

    l = dbo.locale
    onshelter = True
    diedoffshelter = False
    hasreserve = False
    hastrial = False
    haspermanentfoster = False
    lastreturn = None
    mostrecententrydate = None
    activemovementid = 0
    activemovementdate = None
    activemovementtype = None
    activemovementtypename = None
    activemovementreturn = None
    currentownerid = None
    currentownername = None
    today = now(dbo.timezone)
    
    def b2i(x):
        return x and 1 or 0

    if a is None:
        a = get_animal(dbo, animalid)
        if a is None: return

    if movements is None: 
        movements = db.query(dbo, get_animal_movement_status_query(dbo) + \
            " WHERE AnimalID = %d ORDER BY MovementDate DESC" % animalid)

    # Start at first intake for most recent entry date
    mostrecententrydate = a["DATEBROUGHTIN"]

    # Just look these up once
    if cfg is None:
        cfg_foster_on_shelter = configuration.foster_on_shelter(dbo)
        cfg_retailer_on_shelter = configuration.retailer_on_shelter(dbo)
        cfg_trial_on_shelter = configuration.trial_on_shelter(dbo)
    else:
        cfg_foster_on_shelter = cfg["foster_on_shelter"]
        cfg_retailer_on_shelter = cfg["retailer_on_shelter"]
        cfg_trial_on_shelter = cfg["trial_on_shelter"]

    for m in movements:

        # Ignore movements that aren't for this animal
        if m["ANIMALID"] != animalid: continue

        # Is this an "exit" type movement? ie. A movement that could take the
        # animal out of the care of the shelter? Depending on what system options
        # are set, some movement types do or don't
        exitmovement = False
        if m["MOVEMENTTYPE"] > 0: exitmovement = True
        if m["MOVEMENTTYPE"] == movement.FOSTER and cfg_foster_on_shelter: exitmovement = False
        elif m["MOVEMENTTYPE"] == movement.RETAILER and cfg_retailer_on_shelter: exitmovement = False
        elif m["MOVEMENTTYPE"] == movement.ADOPTION and m["ISTRIAL"] == 1 and cfg_trial_on_shelter: exitmovement = False

        # Is this movement active right now?
        if (m["MOVEMENTDATE"] is not None and m["MOVEMENTDATE"] <= today and m["RETURNDATE"] is None) or \
            (m["MOVEMENTDATE"] is not None and m["MOVEMENTDATE"] <= today and m["RETURNDATE"] > today):

            activemovementid = m["ID"]
            activemovementdate = m["MOVEMENTDATE"]
            activemovementtype = m["MOVEMENTTYPE"]
            activemovementtypename = m["MOVEMENTTYPENAME"]
            activemovementreturn = m["RETURNDATE"]
            currentownerid = m["OWNERID"]
            currentownername = m["OWNERNAME"]

            # If this is an exit movement, take the animal off shelter
            # If this active movement is not an exit movement, keep the animal onshelter
            if exitmovement: onshelter = False

            # Is this an active trial adoption?
            if m["MOVEMENTTYPE"] == movement.ADOPTION and m["ISTRIAL"] == 1:
                hastrial = True

            # Is this a permanent foster?
            if m["MOVEMENTTYPE"] == movement.FOSTER and m["ISPERMANENTFOSTER"] == 1:
                haspermanentfoster = True

            # If the animal is dead, and this is an open exit movement,
            # set the diedoffshelter flag for reports
            if a["DECEASEDDATE"] is not None and exitmovement:
                diedoffshelter = True

        # Is this movement an active reservation?
        if m["RETURNDATE"] is None and m["MOVEMENTTYPE"] == movement.NO_MOVEMENT \
            and m["MOVEMENTDATE"] is None and m["RESERVATIONCANCELLEDDATE"] is None and \
            m["RESERVATIONDATE"] is not None and m["RESERVATIONDATE"] <= today:
            hasreserve = True

        # Update the last time the animal was returned
        if m["RETURNDATE"] is not None:
            if lastreturn is None: lastreturn = m["RETURNDATE"]
            if m["RETURNDATE"] > lastreturn: lastreturn = m["RETURNDATE"]

        # Update the mostrecententrydate if this is a returned exit movement
        # that is returned later than the current date we have
        if exitmovement and m["RETURNDATE"] is not None and m["RETURNDATE"] > mostrecententrydate and m["RETURNDATE"] <= today:
            mostrecententrydate = m["RETURNDATE"]

    # Override the other flags if this animal is dead or non-shelter
    if a["DECEASEDDATE"] is not None or a["NONSHELTERANIMAL"] == 1:
        onshelter = False
        hastrial = False
        hasreserve = False
        haspermanentfoster = False

    # Calculate location and qualified display location
    loc = ""
    qlocname = ""
    if a["DECEASEDDATE"] is not None:
        loc = _("Deceased", l)
        qlocname = loc
        if a["PUTTOSLEEP"] == 1:
            qlocname = "%s::%s" % (qlocname, a["PTSREASONNAME"])
    elif activemovementdate is not None:
        loc = activemovementtypename
        qlocname = loc
        if currentownerid is not None and currentownername is not None:
            qlocname = "%s::%s" % (loc, currentownername)
    else:
        if a["SHELTERLOCATIONUNIT"] is not None and a["SHELTERLOCATIONUNIT"] != "":
            loc = "%s::%s" % (a["SHELTERLOCATIONNAME"], a["SHELTERLOCATIONUNIT"])
        else:
            loc = a["SHELTERLOCATIONNAME"]
        qlocname = loc

    # Has anything actually changed?
    if a["ARCHIVED"] == b2i(not onshelter) and \
       a["ACTIVEMOVEMENTID"] == activemovementid and \
       a["ACTIVEMOVEMENTDATE"] == activemovementdate and \
       a["ACTIVEMOVEMENTTYPE"] == activemovementtype and \
       a["ACTIVEMOVEMENTRETURN"] == activemovementreturn and \
       a["DIEDOFFSHELTER"] == b2i(diedoffshelter) and \
       a["HASACTIVERESERVE"] == b2i(hasreserve) and \
       a["HASTRIALADOPTION"] == b2i(hastrial) and \
       a["HASPERMANENTFOSTER"] == b2i(haspermanentfoster) and \
       a["MOSTRECENTENTRYDATE"] == mostrecententrydate and \
       a["DISPLAYLOCATION"] == qlocname:
        # No - don't do anything
        return

    # Update our in memory animal
    a["ARCHIVED"] = b2i(not onshelter)
    a["ACTIVEMOVEMENTID"] = activemovementid
    a["ACTIVEMOVEMENTDATE"] = activemovementdate
    a["ACTIVEMOVEMENTTYPE"] = activemovementtype
    a["ACTIVEMOVEMENTRETURN"] = activemovementreturn
    a["DIEDOFFSHELTER"] = b2i(diedoffshelter)
    a["HASACTIVERESERVE"] = b2i(hasreserve)
    a["HASTRIALADOPTION"] = b2i(hastrial)
    a["HASPERMANENTFOSTER"] = b2i(haspermanentfoster)
    a["MOSTRECENTENTRYDATE"] = mostrecententrydate
    a["DISPLAYLOCATION"] = qlocname

    # Update the location on any diary notes for this animal
    update_diary_linkinfo(dbo, animalid, a, diaryupdatebatch)
  
    # If we have an animal batch going, append to it
    if animalupdatebatch is not None:
        animalupdatebatch.append((
            b2i(not onshelter),
            activemovementid,
            activemovementdate,
            activemovementtype,
            activemovementreturn,
            b2i(diedoffshelter),
            qlocname,
            b2i(hasreserve),
            b2i(hastrial),
            b2i(haspermanentfoster),
            mostrecententrydate,
            animalid
        ))
    else:
        # Just do the DB update now
        db.execute(dbo, db.make_update_sql("animal", "ID=%d" % animalid, (
            ( "Archived", db.di(b2i(not onshelter)) ),
            ( "ActiveMovementID", db.di(activemovementid) ),
            ( "ActiveMovementDate", db.dd(activemovementdate) ),
            ( "ActiveMovementType", db.di(activemovementtype) ),
            ( "ActiveMovementReturn", db.dd(activemovementreturn) ),
            ( "DiedOffShelter", db.di(b2i(diedoffshelter)) ),
            ( "DisplayLocation", db.ds(qlocname) ),
            ( "HasActiveReserve", db.di(b2i(hasreserve)) ),
            ( "HasTrialAdoption", db.di(b2i(hastrial)) ),
            ( "HasPermanentFoster", db.di(b2i(haspermanentfoster)) ),
            ( "MostRecentEntryDate", db.ddt(mostrecententrydate) )
            )))

def get_number_animals_on_shelter(dbo, date, speciesid = 0, animaltypeid = 0, internallocationid = 0, ageselection = 0, startofday = False):
    """
    Returns the number of animals on shelter at the end of a given date for a species, type,
    location and optionally for an ageselection - 0 = allages, 1 = under six months, 2 = over six months
    startofday: movements and intake that took place on date are not counted if true
    """
    sdate = db.dd(date)
    if not startofday:
        sdate = db.ddt(date.replace(hour=23,minute=59,second=59))
    sixmonthsago = db.dd(subtract_days(date, 182))
    sql = "SELECT COUNT(ID) FROM animal WHERE "
    if speciesid != 0:
        sql += "SpeciesID = %d" % speciesid
    else:
        sql += "AnimalTypeID = %d" % animaltypeid
    if startofday:
        sql += " AND DateBroughtIn < %s AND NonShelterAnimal = 0" % sdate # intake today excluded
        sql += " AND (DeceasedDate Is Null OR DeceasedDate > %s)" % sdate # deaths today excluded
        movementclause = "MovementDate < %s" % db.dd(date) # movements today excluded
        returnclause = "ReturnDate > %s" % db.dd(date) # returns today excluded
    else:
        sql += " AND DateBroughtIn <= %s AND NonShelterAnimal = 0" % sdate # intakes today included
        sql += " AND (DeceasedDate Is Null OR DeceasedDate >= %s)" % sdate # deaths today included
        movementclause = "MovementDate <= %s" % sdate # movements today included
        returnclause = "ReturnDate >= %s" % sdate # returns today included
    if internallocationid != 0:
        sql += " AND ShelterLocation = %d" % internallocationid
    if ageselection == 1:
        sql += " AND DateOfBirth >= %s" % sixmonthsago
    if ageselection == 2:
        sql += " AND DateOfBirth < %s" % sixmonthsago
    sql += " AND NOT EXISTS (SELECT adoption.ID FROM adoption " \
        "WHERE AnimalID = animal.ID AND MovementType <> 2 AND MovementDate Is Not Null AND " \
        "%s AND (ReturnDate Is Null OR %s))" % (movementclause, returnclause)
    return db.query_int(dbo, sql)

def get_number_litters_on_shelter(dbo, date, speciesid = 0):
    """
    Returns the number of active litters at a given date, optionally
    for a single species.
    """
    sdate = db.ddt(date)
    sql = "SELECT COUNT(a.ID) FROM animallitter a " \
        "WHERE a.Date <= %s " % sdate
    if speciesid != 0:
        sql += "AND SpeciesID = %d " % speciesid
    sql += "AND (InvalidDate Is Null OR InvalidDate > %s)" % sdate
    return db.query_int(dbo, sql)

def get_number_animals_on_foster(dbo, date, speciesid = 0, animaltypeid = 0):
    """
    Returns the number of animals on foster at the end of a given date for a species or type
    """
    sdate = db.dd(date)
    sql = "SELECT COUNT(ID) FROM animal " \
        "WHERE "
    if speciesid != 0:
        sql += "SpeciesID = %d" % speciesid
    else:
        sql += "AnimalTypeID = %d" % animaltypeid
    sql += " AND DateBroughtIn <= %s" % sdate
    sql += " AND NonShelterAnimal = 0"
    sql += " AND (DeceasedDate > %s OR DeceasedDate Is Null)" % sdate
    sql += " AND EXISTS(SELECT AdoptionNumber FROM adoption WHERE "
    sql += " MovementType = %d" % movement.FOSTER
    sql += " AND MovementDate <= %s" % sdate
    sql += " AND AnimalID = animal.ID"
    sql += " AND (ReturnDate > %s OR ReturnDate Is Null))" % sdate
    return db.query_int(dbo, sql)

def update_animal_figures(dbo, month = 0, year = 0):
    """
    Updates the animal figures table for the month and year given.
    If month and year aren't given, defaults to this month, unless today is
    the first day of the month in which case we do last month.
    """
    async.set_progress_max(dbo, 3)
    batch = []
    nid = dbo.get_id_max("animalfigures")

    def sql_days(sql):
        """ Returns a query with THEDATE and TOTAL as a dictionary for add_row """
        d = {}
        for i in range(1, 32):
            d["D%d" % i] = "0"
        rows = db.query(dbo, sql)
        for r in rows:
            dk = "D%d" % r["THEDATE"].day
            d[dk] = r["TOTAL"]
        return d

    def add_days(listdays):
        """ Adds up a list of day dictionaries """
        d = {}
        for i in range(1, 32):
            d["D%d" % i] = 0
        for cd in listdays:
            if "D29" not in cd: cd["D29"] = 0
            if "D30" not in cd: cd["D30"] = 0
            if "D31" not in cd: cd["D31"] = 0
            for i in range(1, 32):
                dk = "D%d" % i
                if dk in cd:
                    d[dk] = int(d[dk]) + int(cd[dk])
        return d

    def is_zero_days(days):
        """ Returns true if a map of day counts is all zero """
        for i in range(1, 32):
            dk = "D%d" % i
            if dk in days and int(days[dk]) > 0:
                return False
        return True

    def sub_days(initdic, subdic):
        """ Subtracts day dictionary subdic from initdic """
        d = initdic.copy()
        cd = subdic
        if "D29" not in d: d["D29"] = 0
        if "D30" not in d: d["D30"] = 0
        if "D31" not in d: d["D31"] = 0
        if "D29" not in cd: cd["D29"] = 0
        if "D30" not in cd: cd["D30"] = 0
        if "D31" not in cd: cd["D31"] = 0
        for i in range(1, 32):
            dk = "D%d" % i
            d[dk] = int(d[dk]) - int(cd[dk])
        return d

    def add_row(orderindex, code, animaltypeid, speciesid, maxdaysinmonth, heading, bold, calctotal, days):
        """ Adds a row to the animalfigures table """
        if "D29" not in days: days["D29"] = 0
        if "D30" not in days: days["D30"] = 0
        if "D31" not in days: days["D31"] = 0
        avg = 0.0
        tot = 0
        total = ""
        for i in range(1, maxdaysinmonth + 1):
            avg += int(days["D%d" % i])
            tot += int(days["D%d" % i])
        avg = round(float(float(avg) / float(maxdaysinmonth)), 1)
        if calctotal: 
            total = str(tot)
        batch.append((
            nid + len(batch),
            month,
            year,
            orderindex,
            code,
            animaltypeid,
            speciesid,
            maxdaysinmonth,
            heading,
            bold,
            days["D1"],
            days["D2"],
            days["D3"],
            days["D4"],
            days["D5"],
            days["D6"],
            days["D7"],
            days["D8"],
            days["D9"],
            days["D10"],
            days["D11"],
            days["D12"],
            days["D13"],
            days["D14"],
            days["D15"],
            days["D16"],
            days["D17"],
            days["D18"],
            days["D19"],
            days["D20"],
            days["D21"],
            days["D22"],
            days["D23"],
            days["D24"],
            days["D25"],
            days["D26"],
            days["D27"],
            days["D28"],
            days["D29"],
            days["D30"],
            days["D31"],
            total,
            avg
        ))

    def update_db(month, year):
        """ Writes all of our figures to the database """
        db.execute(dbo, "DELETE FROM animalfigures WHERE Month = %d AND Year = %d" % (month, year))
        sql = "INSERT INTO animalfigures (ID, Month, Year, OrderIndex, Code, AnimalTypeID, " \
            "SpeciesID, MaxDaysInMonth, Heading, Bold, D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, " \
            "D11, D12, D13, D14, D15, D16, D17, D18, D19, D20, D21, D22, D23, D24, D25, D26, " \
            "D27, D28, D29, D30, D31, Total, Average) VALUES (?,?,?,?,?,?," \
            "?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, "\
            "?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, "\
            "?,?,?,?,?,?,?)"
        dbo.execute_many(sql, batch)
        al.debug("wrote %d figures records" % len(batch), "animal.update_animal_figures", dbo)

    # If month and year are zero, figure out which one we're going
    # to generate for. We use this month, unless today is the first
    # of the month, in which case we do last month
    if month == 0 and year == 0:
        today = now()
        if today.day == 1: today = subtract_months(today, 1)
        month = today.month
        year = today.year
    al.debug("Generating animal figures for month=%d, year=%d" % (month, year), "animal.update_animal_figures", dbo)

    l = dbo.locale
    fom = datetime.datetime(year, month, 1)
    lom = last_of_month(fom)
    lom = lom.replace(hour=23, minute=59, second=59)
    firstofmonth = db.dd(fom)
    lastofmonth = db.ddt(lom)
    daysinmonth = lom.day
    loopdays = daysinmonth + 1

    # Species =====================================
    allspecies = lookups.get_species(dbo)
    for sp in allspecies:

        speciesid = int(sp["ID"])

        # If we never had anything for this species, skip it
        if 0 == db.query_int(dbo, "SELECT COUNT(*) FROM animal WHERE SpeciesID = %d" % speciesid):
            continue

        # On Shelter
        onshelter = {}
        for i in range(1, loopdays):
            d = datetime.datetime(year, month, i)
            dk = "D%d" % i
            onshelter[dk] = get_number_animals_on_shelter(dbo, d, speciesid)
        add_row(1, "SP_ONSHELTER", 0, speciesid, daysinmonth, _("On Shelter", l), 0, False, onshelter)

        # On Foster (if foster on shelter set)
        if configuration.foster_on_shelter(dbo):
            onfoster = {}
            for i in range(1, loopdays):
                d = datetime.datetime(year, month, i)
                dk = "D%d" % i
                onfoster[dk] = get_number_animals_on_foster(dbo, d, speciesid)
            add_row(2, "SP_ONFOSTER", 0, speciesid, daysinmonth, _("On Foster (in figures)", l), 0, False, onfoster)
            #sheltertotal = add_days((onshelter, onfoster)) double count
            sheltertotal = onshelter
        else:
            sheltertotal = onshelter

        # Litters
        litters = {}
        for i in range(1, loopdays):
            d = datetime.datetime(year, month, i)
            dk = "D%d" % i
            litters[dk] = get_number_litters_on_shelter(dbo, d, speciesid)
        add_row(3, "SP_LITTERS", 0, speciesid, daysinmonth, _("Litters", l), 0, False, litters)

        # Start of day total - handled at the end.

        # Brought In
        # If the config option is on, output a row for each entry
        # category or a single line for brought in.
        if configuration.animal_figures_split_entryreason(dbo):
            reasons = lookups.get_entryreasons(dbo)
            idx = 5
            broughtin = {}
            for er in reasons:
                erline = sql_days("SELECT DateBroughtIn AS TheDate, COUNT(ID) AS Total FROM animal WHERE " \
                    "SpeciesID = %d AND DateBroughtIn >= %s AND DateBroughtIn <= %s " \
                    "AND IsTransfer = 0 AND NonShelterAnimal = 0 AND EntryReasonID = %d " \
                    "GROUP BY DateBroughtIn" % (speciesid, firstofmonth, lastofmonth, er["ID"]))
                if not is_zero_days(erline):
                    add_row(idx, "SP_ER_%d" % er["ID"], 0, speciesid, daysinmonth, er["REASONNAME"], 0, True, erline)
                    idx += 1
                    broughtin = add_days((broughtin, erline))
        else:
            broughtin = sql_days("SELECT DateBroughtIn AS TheDate, COUNT(ID) AS Total FROM animal WHERE " \
                "SpeciesID = %d AND DateBroughtIn >= %s AND DateBroughtIn <= %s " \
                "AND IsTransfer = 0 AND NonShelterAnimal = 0 " \
                "GROUP BY DateBroughtIn" % (speciesid, firstofmonth, lastofmonth))
            add_row(5, "SP_BROUGHTIN", 0, speciesid, daysinmonth, _("Incoming", l), 0, True, broughtin)

        # Returned
        returned = sql_days("SELECT ReturnDate AS TheDate, COUNT(animal.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON adoption.AnimalID = animal.ID " \
            "WHERE SpeciesID = %d AND ReturnDate >= %s AND ReturnDate <= %s " \
            "AND MovementType = %d " \
            "GROUP BY ReturnDate" % (speciesid, firstofmonth, lastofmonth, movement.ADOPTION))
        add_row(106, "SP_RETURNED", 0, speciesid, daysinmonth, _("Returned", l), 0, True, returned)

        # Transferred In
        transferin = sql_days("SELECT DateBroughtIn AS TheDate, COUNT(ID) AS Total FROM animal WHERE " \
            "SpeciesID = %d AND DateBroughtIn >= %s AND DateBroughtIn <= %s " \
            "AND IsTransfer <> 0 AND NonShelterAnimal = 0 " \
            "GROUP BY DateBroughtIn" % (speciesid, firstofmonth, lastofmonth))
        add_row(107, "SP_TRANSFERIN", 0, speciesid, daysinmonth, _("Transferred In", l), 0, True, transferin)

        # Returned From Fostering
        returnedfoster = sql_days("SELECT ReturnDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType = %d " \
            "AND ReturnDate >= %s AND ReturnDate <= %s " \
            "GROUP BY ReturnDate" % (speciesid, movement.FOSTER, firstofmonth, lastofmonth))
        add_row(108, "SP_RETURNEDFOSTER", 0, speciesid, daysinmonth, _("From Fostering", l), 0, True, returnedfoster)

        # Returned From Other
        returnedother = sql_days("SELECT ReturnDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType <> %d AND MovementType <> %d " \
            "AND ReturnDate >= %s AND ReturnDate <= %s " \
            "GROUP BY ReturnDate" % (speciesid, movement.FOSTER, movement.ADOPTION, firstofmonth, lastofmonth))
        add_row(109, "SP_RETURNEDOTHER", 0, speciesid, daysinmonth, _("From Other", l), 0, True, returnedother)

        # In subtotal
        insubtotal = add_days((broughtin, returned, transferin, returnedfoster, returnedother))
        add_row(110, "SP_INTOTAL", 0, speciesid, daysinmonth, _("In SubTotal", l), 1, False, insubtotal)

        # Adopted
        adopted = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (speciesid, movement.ADOPTION, firstofmonth, lastofmonth))
        add_row(111, "SP_ADOPTED", 0, speciesid, daysinmonth, _("Adopted", l), 0, True, adopted)

        # Reclaimed
        reclaimed = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (speciesid, movement.RECLAIMED, firstofmonth, lastofmonth))
        add_row(112, "SP_RECLAIMED", 0, speciesid, daysinmonth, _("Returned To Owner", l), 0, True, reclaimed)

        # Escaped
        escaped = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (speciesid, movement.ESCAPED, firstofmonth, lastofmonth))
        add_row(113, "SP_ESCAPED", 0, speciesid, daysinmonth, _("Escaped", l), 0, True, escaped)

        # Stolen
        stolen = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (speciesid, movement.STOLEN, firstofmonth, lastofmonth))
        add_row(114, "SP_STOLEN", 0, speciesid, daysinmonth, _("Stolen", l), 0, True, stolen)

        # Released
        released = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (speciesid, movement.RELEASED, firstofmonth, lastofmonth))
        add_row(115, "SP_RELEASED", 0, speciesid, daysinmonth, _("Released To Wild", l), 0, True, released)

        # Transferred
        transferred = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (speciesid, movement.TRANSFER, firstofmonth, lastofmonth))
        add_row(116, "SP_TRANSFERRED", 0, speciesid, daysinmonth, _("Transferred Out", l), 0, True, transferred)

        # Fostered
        fostered = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (speciesid, movement.FOSTER, firstofmonth, lastofmonth))
        add_row(117, "SP_FOSTERED", 0, speciesid, daysinmonth, _("To Fostering", l), 0, True, fostered)

        # Retailer
        retailer = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (speciesid, movement.RETAILER, firstofmonth, lastofmonth))
        add_row(118, "SP_RETAILER", 0, speciesid, daysinmonth, _("To Retailer", l), 0, True, retailer)

        # Died
        died = sql_days("SELECT DeceasedDate AS TheDate, COUNT(animal.ID) AS Total FROM animal WHERE " \
            "SpeciesID = %d AND DeceasedDate >= %s AND DeceasedDate <= %s " \
            "AND PutToSleep = 0 AND DiedOffShelter = 0 AND NonShelterAnimal = 0 " \
            "GROUP BY DeceasedDate" % (speciesid, firstofmonth, lastofmonth))
        add_row(119, "SP_DIED", 0, speciesid, daysinmonth, _("Died", l), 0, True, died)

        # PTS
        pts = sql_days("SELECT DeceasedDate AS TheDate, COUNT(animal.ID) AS Total FROM animal WHERE " \
            "SpeciesID = %d AND DeceasedDate >= %s AND DeceasedDate <= %s " \
            "AND PutToSleep <> 0 AND DiedOffShelter = 0 AND NonShelterAnimal = 0 " \
            "GROUP BY DeceasedDate" % (speciesid, firstofmonth, lastofmonth))
        add_row(120, "SP_PTS", 0, speciesid, daysinmonth, _("Euthanized", l), 0, True, pts)

        # Other
        toother = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType NOT IN (1, 2, 3, 4, 5, 6, 7, 8) " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (speciesid, firstofmonth, lastofmonth))
        add_row(121, "SP_OUTOTHER", 0, speciesid, daysinmonth, _("To Other", l), 0, True, toother)

        # Out subtotal
        outsubtotal = add_days((adopted, reclaimed, escaped, stolen, released, transferred, fostered, retailer, died, pts, toother))
        add_row(122, "SP_OUTTOTAL", 0, speciesid, daysinmonth, _("Out SubTotal", l), 1, False, outsubtotal)

        # Start of day total
        starttotal = sub_days(sheltertotal, insubtotal)
        starttotal = add_days((starttotal, outsubtotal))
        add_row(4, "SP_STARTTOTAL", 0, speciesid, daysinmonth, _("Start Of Day", l), 1, False, starttotal)

        # End of day
        add_row(123, "SP_TOTAL", 0, speciesid, daysinmonth, _("End Of Day", l), 1, False, sheltertotal)

    async.set_progress_value(dbo, 1)

    # Animal Types =====================================
    alltypes = lookups.get_animal_types(dbo)
    for at in alltypes:

        typeid = int(at["ID"])

        # If we never had anything for this type, skip it
        if 0 == db.query_int(dbo, "SELECT COUNT(*) FROM animal WHERE AnimalTypeID = %d" % typeid):
            continue

        # On Shelter
        onshelter = {}
        for i in range(1, loopdays):
            d = datetime.datetime(year, month, i)
            dk = "D%d" % i
            onshelter[dk] = get_number_animals_on_shelter(dbo, d, 0, typeid)
        add_row(1, "AT_ONSHELTER", typeid, 0, daysinmonth, _("On Shelter", l), 0, False, onshelter)

        # On Foster (if foster on shelter set)
        if configuration.foster_on_shelter(dbo):
            onfoster = {}
            for i in range(1, loopdays):
                d = datetime.datetime(year, month, i)
                dk = "D%d" % i
                onfoster[dk] = get_number_animals_on_foster(dbo, d, 0, typeid)
            add_row(2, "AT_ONFOSTER", typeid, 0, daysinmonth, _("On Foster (in figures)", l), 0, False, onfoster)
            #sheltertotal = add_days((onshelter, onfoster)) double count
            sheltertotal = onshelter
        else:
            sheltertotal = onshelter

        # Start of day - handled later

        # Brought In
        # If the config option is on, output a row for each entry
        # category or a single line for brought in.
        if configuration.animal_figures_split_entryreason(dbo):
            reasons = lookups.get_entryreasons(dbo)
            broughtin = {}
            idx = 5
            for er in reasons:
                erline = sql_days("SELECT DateBroughtIn AS TheDate, COUNT(ID) AS Total FROM animal WHERE " \
                    "AnimalTypeID = %d AND DateBroughtIn >= %s AND DateBroughtIn <= %s " \
                    "AND IsTransfer = 0 AND NonShelterAnimal = 0 AND EntryReasonID = %d " \
                    "GROUP BY DateBroughtIn" % (typeid, firstofmonth, lastofmonth, er["ID"]))
                if not is_zero_days(erline):
                    add_row(idx, "AT_ER_%d" % er["ID"], typeid, 0, daysinmonth, er["REASONNAME"], 0, True, erline)
                    broughtin = add_days((broughtin, erline))
                    idx += 1
        else:
            # Brought In
            broughtin = sql_days("SELECT DateBroughtIn AS TheDate, COUNT(ID) AS Total FROM animal WHERE " \
                "AnimalTypeID = %d AND DateBroughtIn >= %s AND DateBroughtIn <= %s " \
                "AND IsTransfer = 0 AND NonShelterAnimal = 0 " \
                "GROUP BY DateBroughtIn" % (typeid, firstofmonth, lastofmonth))
            add_row(5, "AT_BROUGHTIN", typeid, 0, daysinmonth, _("Incoming", l), 0, True, broughtin)

        # Returned
        returned = sql_days("SELECT ReturnDate AS TheDate, COUNT(animal.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON adoption.AnimalID = animal.ID " \
            "WHERE AnimalTypeID = %d AND ReturnDate >= %s AND ReturnDate <= %s " \
            "AND MovementType = %d " \
            "GROUP BY ReturnDate" % (typeid, firstofmonth, lastofmonth, movement.ADOPTION))
        add_row(6, "AT_RETURNED", typeid, 0, daysinmonth, _("Returned", l), 0, True, returned)

        # Transferred In
        transferin = sql_days("SELECT DateBroughtIn AS TheDate, COUNT(ID) AS Total FROM animal WHERE " \
            "AnimalTypeID = %d AND DateBroughtIn >= %s AND DateBroughtIn <= %s " \
            "AND IsTransfer <> 0 AND NonShelterAnimal = 0 " \
            "GROUP BY DateBroughtIn" % (typeid, firstofmonth, lastofmonth))
        add_row(7, "AT_TRANSFERIN", typeid, 0, daysinmonth, _("Transferred In", l), 0, True, transferin)

        # Returned From Fostering
        returnedfoster = sql_days("SELECT ReturnDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType = %d " \
            "AND ReturnDate >= %s AND ReturnDate <= %s " \
            "GROUP BY ReturnDate" % (typeid, movement.FOSTER, firstofmonth, lastofmonth))
        add_row(8, "AT_RETURNEDFOSTER", typeid, 0, daysinmonth, _("From Fostering", l), 0, True, returnedfoster)

        # Returned From Other
        returnedother = sql_days("SELECT ReturnDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType <> %d AND MovementType <> %d " \
            "AND ReturnDate >= %s AND ReturnDate <= %s " \
            "GROUP BY ReturnDate" % (typeid, movement.FOSTER, movement.ADOPTION, firstofmonth, lastofmonth))
        add_row(9, "AT_RETURNEDOTHER", typeid, 0, daysinmonth, _("From Other", l), 0, True, returnedother)

        # In subtotal
        insubtotal = add_days((broughtin, returned, transferin, returnedfoster, returnedother))
        add_row(10, "AT_INTOTAL", typeid, 0, daysinmonth, _("SubTotal", l), 1, False, insubtotal)

        # Adopted
        adopted = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (typeid, movement.ADOPTION, firstofmonth, lastofmonth))
        add_row(11, "AT_ADOPTED", typeid, 0, daysinmonth, _("Adopted", l), 0, True, adopted)

        # Reclaimed
        reclaimed = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (typeid, movement.RECLAIMED, firstofmonth, lastofmonth))
        add_row(12, "AT_RECLAIMED", typeid, 0, daysinmonth, _("Returned To Owner", l), 0, True, reclaimed)

        # Escaped
        escaped = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (typeid, movement.ESCAPED, firstofmonth, lastofmonth))
        add_row(13, "AT_ESCAPED", typeid, 0, daysinmonth, _("Escaped", l), 0, True, escaped)

        # Stolen
        stolen = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (typeid, movement.STOLEN, firstofmonth, lastofmonth))
        add_row(14, "AT_STOLEN", typeid, 0, daysinmonth, _("Stolen", l), 0, True, stolen)

        # Released
        released = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (typeid, movement.RELEASED, firstofmonth, lastofmonth))
        add_row(15, "AT_RELEASED", typeid, 0, daysinmonth, _("Released To Wild", l), 0, True, released)

        # Transferred
        transferred = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (typeid, movement.TRANSFER, firstofmonth, lastofmonth))
        add_row(16, "AT_TRANSFERRED", typeid, 0, daysinmonth, _("Transferred Out", l), 0, True, transferred)

        # Fostered
        fostered = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (typeid, movement.FOSTER, firstofmonth, lastofmonth))
        add_row(17, "AT_FOSTERED", typeid, 0, daysinmonth, _("To Fostering", l), 0, True, fostered)

        # Retailer
        retailer = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (typeid, movement.RETAILER, firstofmonth, lastofmonth))
        add_row(18, "AT_RETAILER", typeid, 0, daysinmonth, _("To Retailer", l), 0, True, retailer)

        # Died
        died = sql_days("SELECT DeceasedDate AS TheDate, COUNT(animal.ID) AS Total FROM animal WHERE " \
            "AnimalTypeID = %d AND DeceasedDate >= %s AND DeceasedDate <= %s " \
            "AND PutToSleep = 0 AND DiedOffShelter = 0 AND NonShelterAnimal = 0 " \
            "GROUP BY DeceasedDate" % (typeid, firstofmonth, lastofmonth))
        add_row(19, "AT_DIED", typeid, 0, daysinmonth, _("Died", l), 0, True, died)

        # PTS
        pts = sql_days("SELECT DeceasedDate AS TheDate, COUNT(animal.ID) AS Total FROM animal WHERE " \
            "AnimalTypeID = %d AND DeceasedDate >= %s AND DeceasedDate <= %s " \
            "AND PutToSleep <> 0 AND DiedOffShelter = 0 AND NonShelterAnimal = 0 " \
            "GROUP BY DeceasedDate" % (typeid, firstofmonth, lastofmonth))
        add_row(20, "AT_PTS", typeid, 0, daysinmonth, _("Euthanized", l), 0, True, pts)

        # Other
        toother = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType NOT IN (1, 2, 3, 4, 5, 6, 7, 8) " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (typeid, firstofmonth, lastofmonth))
        add_row(21, "AT_OUTOTHER", typeid, 0, daysinmonth, _("To Other", l), 0, True, toother)

        # Out subtotal
        outsubtotal = add_days((adopted, reclaimed, escaped, stolen, released, transferred, fostered, retailer, died, pts, toother))
        add_row(22, "AT_OUTTOTAL", typeid, 0, daysinmonth, _("SubTotal", l), 1, False, outsubtotal)

        # Start of day total
        starttotal = sub_days(sheltertotal, insubtotal)
        starttotal = add_days((starttotal, outsubtotal))
        add_row(4, "AT_STARTTOTAL", typeid, 0, daysinmonth, _("Start Of Day", l), 1, False, starttotal)

        # End of day
        add_row(50, "AT_TOTAL", typeid, 0, daysinmonth, _("End Of Day", l), 1, False, sheltertotal)

    async.set_progress_value(dbo, 2)

    # Write out our db changes
    update_db(month, year)
    return "OK"

def update_animal_figures_annual(dbo, year = 0):
    """
    Updates the animal figures annual table for the year given.
    If year isn't given, defaults to this year, unless today is the
    first of the year in which case we do last year.
    """
    async.set_progress_max(dbo, 3)
    batch = []
    nid = dbo.get_id_max("animalfiguresannual")

    def add_row(orderindex, code, animaltypeid, speciesid, entryreasonid, group, heading, bold, months):
        """ Adds a row to the animalfiguresannual table, unless it's all 0 """
        if months[12] == 0: return
        batch.append((
            nid + len(batch),
            year,
            orderindex,
            code,
            animaltypeid,
            speciesid,
            entryreasonid,
            group,
            heading,
            bold,
            months[0],
            months[1],
            months[2],
            months[3],
            months[4],
            months[5],
            months[6],
            months[7],
            months[8],
            months[9],
            months[10],
            months[11],
            months[12]
        ))

    def sql_months(sql, babysplit = False, babymonths = 4):
        """ 
            Executes a query and returns two sets of months based on the
            results. 
            Query should have three columns - THEDATE, DOB and TOTAL.
            If babysplit is True, then babymonths is used to figure out
            whether the animal was a baby at the date in the result and
            if so, returns it in the second set.
            It will calculate the horizontal totals as well.
        """
        d = [0] * 13
        d2 = [0] * 13
        rows = db.query(dbo, sql)
        for r in rows:
            dk = r["THEDATE"].month - 1
            if not babysplit:
                d[dk] += r["TOTAL"]
            else:
                if date_diff_days(r["DOB"], r["THEDATE"]) > (babymonths * 31):
                    d[dk] += r["TOTAL"]
                else:
                    d2[dk] += r["TOTAL"]
        total = 0
        for v in d:
            total += v
        d[12] = total
        total = 0
        for v in d2:
            total += v
        d2[12] = total
        return d, d2

    def entryreason_line(sql, entryreasonid, reasonname, code, group, orderindex, showbabies, babymonths):
        """
        Adds a line for a particular entry reason.
        sql: The query to run
        """
        babyname = _("{0} (under {1} months)", l).format(reasonname, babymonths)
        lines = sql_months(sql, showbabies, babymonths)
        add_row(orderindex, code, 0, 0, entryreasonid, group, reasonname, 0, lines[0])
        if showbabies: add_row(orderindex, code + "_BABY", 0, 0, entryreasonid, group, babyname, 0, lines[1])

    def species_line(sql, speciesid, speciesname, code, group, orderindex, showbabies, babymonths):
        """
        Adds a line for a particular species.
        sql: The query to run
        """
        babyname = ""
        if speciesid == 1: babyname = _("Puppies (under {0} months)", l).format(babymonths)
        if speciesid == 2: babyname = _("Kittens (under {0} months)", l).format(babymonths)
        babysplit = babyname != "" and showbabies
        lines = sql_months(sql, babysplit, babymonths)
        add_row(orderindex, code, 0, speciesid, 0, group, speciesname, 0, lines[0])
        if babysplit: add_row(orderindex, code + "_BABY", 0, speciesid, 0, group, babyname, 0, lines[1])

    def type_line(sql, typeid, typename, code, group, orderindex, showbabies, babymonths):
        """
        Adds a line for a particular type.
        sql: The query to run
        """
        babyname = _("{0} (under {1} months)", l).format(typename, babymonths)
        lines = sql_months(sql, showbabies, babymonths)
        add_row(orderindex, code, typeid, 0, 0, group, typename, 0, lines[0])
        if showbabies: add_row(orderindex, code + "_BABY", typeid, 0, 0, group, babyname, 0, lines[1])

    def update_db(year):
        """ Writes all of our figures to the database """
        db.execute(dbo, "DELETE FROM animalfiguresannual WHERE Year = %d" % year)
        sql = "INSERT INTO animalfiguresannual (ID, Year, OrderIndex, Code, AnimalTypeID, " \
            "SpeciesID, EntryReasonID, GroupHeading, Heading, Bold, M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, " \
            "M11, M12, Total) VALUES (?,?,?,?,?,?," \
            "?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        dbo.execute_many(sql, batch)
        al.debug("wrote %d annual figures records" % len(batch), "animal.update_animal_figures_annual", dbo)

    # If year is zero, figure out which one we're going
    # to generate for. We use this year, unless today is the first
    # of the year, in which case we do last year.
    l = dbo.locale
    if year == 0:
        today = now(dbo.timezone)
        if today.day == 1 and today.month == 1: today = subtract_years(today, 1)
        year = today.year
    al.debug("Generating animal figures annual for year=%d" % year, "animal.update_animal_figures_annual", dbo)

    # Work out the full year
    foy = datetime.datetime(year, 1, 1)
    loy = datetime.datetime(year, 12, 31, 23, 59, 59)
    firstofyear = db.dd(foy)
    lastofyear = db.dd(loy)

    # Are we splitting between baby and adult animals?
    showbabies = configuration.annual_figures_show_babies(dbo)
    showbabiestype = configuration.annual_figures_show_babies_type(dbo)
    babymonths = configuration.annual_figures_baby_months(dbo)
    splitadoptions = configuration.annual_figures_split_adoptions(dbo)

    # Species =====================================
    allspecies = lookups.get_species(dbo)
    group = _("Intakes {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND a.IsTransfer = 0 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_BROUGHTIN", group, 10, showbabies, babymonths)

    group = _("Born on Shelter {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND a.NonShelterAnimal = 0 AND a.DateBroughtIn = a.DateOfBirth " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_BORNSHELTER", group, 20, showbabies, babymonths)

    group = _("Born on Foster {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND a.NonShelterAnimal = 0 AND a.DateBroughtIn = a.DateOfBirth " \
            "AND EXISTS(SELECT m.ID FROM adoption m WHERE m.MovementDate = a.DateBroughtIn AND " \
                "m.AnimalID = a.ID AND m.MovementType = 2) " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_BORNFOSTER", group, 30, showbabies, babymonths)

    group = _("Returns {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT ad.ReturnDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.SpeciesID = %d AND ad.ReturnDate Is Not Null AND ad.ReturnDate >= %s AND ad.ReturnDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType NOT IN (2, 8) " \
            "GROUP BY ad.ReturnDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_RETURN", group, 40, showbabies, babymonths)

    group = _("Adoptions {0}", l).format(year)
    for sp in allspecies:
        adoptionsplittransferclause = splitadoptions and "AND IsTransfer = 0 " or ""
        species_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.SpeciesID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "%sAND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear, adoptionsplittransferclause, movement.ADOPTION),
            sp["ID"], sp["SPECIESNAME"], "SP_ADOPTED", group, 50, showbabies, babymonths)

    group = _("Euthanized {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT a.DeceasedDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.DeceasedDate >= %s AND a.DeceasedDate <= %s " \
            "AND a.DiedOffShelter = 0 AND a.PutToSleep = 1 AND a.IsDOA = 0 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DeceasedDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_EUTHANIZED", group, 60, showbabies, babymonths)

    group = _("Died {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT a.DeceasedDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.DeceasedDate >= %s AND a.DeceasedDate <= %s " \
            "AND a.DiedOffShelter = 0 AND a.PutToSleep = 0 AND a.IsDOA = 0 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DeceasedDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_DIED", group, 70, showbabies, babymonths)

    group = _("DOA {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT a.DeceasedDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.DeceasedDate >= %s AND a.DeceasedDate <= %s " \
            "AND a.DiedOffShelter = 0 AND a.PutToSleep = 0 AND a.IsDOA = 1 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DeceasedDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_DOA", group, 80, showbabies, babymonths)

    group = _("Returned to Owner {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.SpeciesID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear, movement.RECLAIMED),
            sp["ID"], sp["SPECIESNAME"], "SP_RECLAIMED", group, 90, showbabies, babymonths)

    group = _("Transferred Out {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.SpeciesID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear, movement.TRANSFER),
            sp["ID"], sp["SPECIESNAME"], "SP_TRANSFEROUT", group, 100, showbabies, babymonths)

    group = _("Escaped {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.SpeciesID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear, movement.ESCAPED),
            sp["ID"], sp["SPECIESNAME"], "SP_ESCAPED", group, 110, showbabies, babymonths)

    group = _("Stolen {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.SpeciesID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear, movement.STOLEN),
            sp["ID"], sp["SPECIESNAME"], "SP_STOLEN", group, 120, showbabies, babymonths)

    group = _("Released To Wild {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.SpeciesID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear, movement.RELEASED),
            sp["ID"], sp["SPECIESNAME"], "SP_STOLEN", group, 130, showbabies, babymonths)

    group = _("Transferred In {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND a.IsTransfer = 1 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_TRANSFERIN", group, 140, showbabies, babymonths)

    if splitadoptions:
        group = _("Adopted Transferred In {0}", l).format(year)
        for sp in allspecies:
            species_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
                "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
                "a.SpeciesID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
                "AND a.IsTransfer = 1 AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
                "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear, movement.ADOPTION),
                sp["ID"], sp["SPECIESNAME"], "SP_TRANSFERINADOPTED", group, 150, showbabies, babymonths)

    group = _("Neutered/Spayed Shelter Animals In {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT a.NeuteredDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.NeuteredDate >= %s AND a.NeuteredDate <= %s " \
            "AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.NeuteredDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_NEUTERSPAYSA", group, 160, showbabies, babymonths)

    group = _("Neutered/Spayed Non-Shelter Animals In {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT a.NeuteredDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.NeuteredDate >= %s AND a.NeuteredDate <= %s " \
            "AND a.NonShelterAnimal = 1 " \
            "GROUP BY a.NeuteredDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_NEUTERSPAYNS", group, 170, showbabies, babymonths)

    async.set_progress_value(dbo, 1)

    # Types =====================================
    alltypes = lookups.get_animal_types(dbo)
    for at in alltypes:
        # Find the last species this type referred to. If it was a dog or cat
        # species and we're splitting types for puppies/kittens, then mark the
        # type as appropriate for splitting.
        at["SPECIESID"] = db.query_int(dbo, "SELECT SpeciesID FROM animal WHERE AnimalTypeID = %d ORDER BY ID DESC %s" % (at["ID"], dbo.sql_limit(1)))
        at["SHOWSPLIT"] = False
        if showbabiestype and (at["SPECIESID"] == 1 or at["SPECIESID"] == 2):
            at["SHOWSPLIT"] = True
    group = _("Intakes {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.AnimalTypeID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND a.IsTransfer = 0 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_BROUGHTIN", group, 10, at["SHOWSPLIT"], babymonths)

    group = _("Born on Shelter {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.AnimalTypeID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND a.NonShelterAnimal = 0 AND a.DateBroughtIn = a.DateOfBirth " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_BORNSHELTER", group, 20, at["SHOWSPLIT"], babymonths)

    group = _("Born on Foster {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.AnimalTypeID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND a.NonShelterAnimal = 0 AND a.DateBroughtIn = a.DateOfBirth " \
            "AND EXISTS(SELECT m.ID FROM adoption m WHERE m.MovementDate = a.DateBroughtIn AND " \
                "m.AnimalID = a.ID AND m.MovementType = 2) " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_BORNFOSTER", group, 30, at["SHOWSPLIT"], babymonths)

    group = _("Returns {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT ad.ReturnDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.AnimalTypeID = %d AND ad.ReturnDate Is Not Null AND ad.ReturnDate >= %s AND ad.ReturnDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType NOT IN (2, 8) " \
            "GROUP BY ad.ReturnDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_RETURN", group, 40, at["SHOWSPLIT"], babymonths)

    group = _("Adoptions {0}", l).format(year)
    for at in alltypes:
        adoptionsplittransferclause = splitadoptions and "AND IsTransfer = 0 " or ""
        type_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.AnimalTypeID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "%sAND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear, adoptionsplittransferclause, movement.ADOPTION),
            at["ID"], at["ANIMALTYPE"], "AT_ADOPTED", group, 50, at["SHOWSPLIT"], babymonths)

    group = _("Euthanized {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT a.DeceasedDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.AnimalTypeID = %d AND a.DeceasedDate >= %s AND a.DeceasedDate <= %s " \
            "AND a.DiedOffShelter = 0 AND a.PutToSleep = 1 AND a.IsDOA = 0 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DeceasedDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_EUTHANIZED", group, 60, at["SHOWSPLIT"], babymonths)

    group = _("Died {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT a.DeceasedDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.AnimalTypeID = %d AND a.DeceasedDate >= %s AND a.DeceasedDate <= %s " \
            "AND a.DiedOffShelter = 0 AND a.PutToSleep = 0 AND a.IsDOA = 0 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DeceasedDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_DIED", group, 70, at["SHOWSPLIT"], babymonths)

    group = _("DOA {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT a.DeceasedDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.AnimalTypeID = %d AND a.DeceasedDate >= %s AND a.DeceasedDate <= %s " \
            "AND a.DiedOffShelter = 0 AND a.PutToSleep = 0 AND a.IsDOA = 1 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DeceasedDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_DOA", group, 80, at["SHOWSPLIT"], babymonths)

    group = _("Returned to Owner {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.AnimalTypeID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.IsTransfer = 0 AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear, movement.RECLAIMED),
            at["ID"], at["ANIMALTYPE"], "AT_RECLAIMED", group, 90, at["SHOWSPLIT"], babymonths)

    group = _("Transferred Out {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.AnimalTypeID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear, movement.TRANSFER),
            at["ID"], at["ANIMALTYPE"], "AT_TRANSFEROUT", group, 100, at["SHOWSPLIT"], babymonths)

    group = _("Escaped {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.AnimalTypeID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear, movement.ESCAPED),
            at["ID"], at["ANIMALTYPE"], "AT_ESCAPED", group, 110, at["SHOWSPLIT"], babymonths)

    group = _("Stolen {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.AnimalTypeID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear, movement.STOLEN),
            at["ID"], at["ANIMALTYPE"], "AT_STOLEN", group, 120, at["SHOWSPLIT"], babymonths)

    group = _("Released To Wild {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.AnimalTypeID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear, movement.RELEASED),
            at["ID"], at["ANIMALTYPE"], "AT_STOLEN", group, 130, at["SHOWSPLIT"], babymonths)

    group = _("Transferred In {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.AnimalTypeID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND a.IsTransfer = 1 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_TRANSFERIN", group, 140, at["SHOWSPLIT"], babymonths)

    if splitadoptions:
        group = _("Adopted Transferred In {0}", l).format(year)
        for at in alltypes:
            type_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
                "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
                "a.AnimalTypeID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
                "AND a.IsTransfer = 1 AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
                "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear, movement.ADOPTION),
                at["ID"], at["ANIMALTYPE"], "AT_TRANSFERINADOPTED", group, 150, at["SHOWSPLIT"], babymonths)

    async.set_progress_value(dbo, 2)

    # Entry Reasons =====================================
    allreasons = lookups.get_entryreasons(dbo)
    for er in allreasons:
        # Find the last species this reason referred to. If it was a dog or cat
        # species and we're splitting types for puppies/kittens, then mark the
        # reason as appropriate for splitting.
        er["SPECIESID"] = db.query_int(dbo, "SELECT SpeciesID FROM animal WHERE EntryReasonID = %d ORDER BY ID DESC %s" % (er["ID"], dbo.sql_limit(1)))
        er["SHOWSPLIT"] = False
        if showbabiestype and (er["SPECIESID"] == 1 or er["SPECIESID"] == 2):
            er["SHOWSPLIT"] = True
    group = _("Intakes {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.EntryReasonID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND a.IsTransfer = 0 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear),
            er["ID"], er["REASONNAME"], "ER_BROUGHTIN", group, 10, er["SHOWSPLIT"], babymonths)

    group = _("Born on Shelter {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.EntryReasonID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND a.NonShelterAnimal = 0 AND a.DateBroughtIn = a.DateOfBirth " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear),
            er["ID"], er["REASONNAME"], "ER_BORNSHELTER", group, 20, er["SHOWSPLIT"], babymonths)

    group = _("Born on Foster {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.EntryReasonID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND a.NonShelterAnimal = 0 AND a.DateBroughtIn = a.DateOfBirth " \
            "AND EXISTS(SELECT m.ID FROM adoption m WHERE m.MovementDate = a.DateBroughtIn AND " \
                "m.AnimalID = a.ID AND m.MovementType = 2) " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear),
            er["ID"], er["REASONNAME"], "ER_BORNFOSTER", group, 30, er["SHOWSPLIT"], babymonths)

    group = _("Returns {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT ad.ReturnDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.EntryReasonID = %d AND ad.ReturnDate Is Not Null AND ad.ReturnDate >= %s AND ad.ReturnDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType NOT IN (2, 8) " \
            "GROUP BY ad.ReturnDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear),
            er["ID"], er["REASONNAME"], "ER_RETURN", group, 40, er["SHOWSPLIT"], babymonths)

    group = _("Adoptions {0}", l).format(year)
    for er in allreasons:
        adoptionsplittransferclause = splitadoptions and "AND IsTransfer = 0 " or ""
        entryreason_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.EntryReasonID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "%sAND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear, adoptionsplittransferclause, movement.ADOPTION),
            er["ID"], er["REASONNAME"], "ER_ADOPTED", group, 50, er["SHOWSPLIT"], babymonths)

    group = _("Euthanized {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT a.DeceasedDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.EntryReasonID = %d AND a.DeceasedDate >= %s AND a.DeceasedDate <= %s " \
            "AND a.DiedOffShelter = 0 AND a.PutToSleep = 1 AND a.IsDOA = 0 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DeceasedDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear),
            er["ID"], er["REASONNAME"], "ER_EUTHANIZED", group, 60, er["SHOWSPLIT"], babymonths)

    group = _("Died {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT a.DeceasedDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.EntryReasonID = %d AND a.DeceasedDate >= %s AND a.DeceasedDate <= %s " \
            "AND a.DiedOffShelter = 0 AND a.PutToSleep = 0 AND a.IsDOA = 0 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DeceasedDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear),
            er["ID"], er["REASONNAME"], "ER_DIED", group, 70, er["SHOWSPLIT"], babymonths)

    group = _("DOA {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT a.DeceasedDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.EntryReasonID = %d AND a.DeceasedDate >= %s AND a.DeceasedDate <= %s " \
            "AND a.DiedOffShelter = 0 AND a.PutToSleep = 0 AND a.IsDOA = 1 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DeceasedDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear),
            er["ID"], er["REASONNAME"], "ER_DOA", group, 80, er["SHOWSPLIT"], babymonths)

    group = _("Returned to Owner {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.EntryReasonID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear, movement.RECLAIMED),
            er["ID"], er["REASONNAME"], "ER_RECLAIMED", group, 90, er["SHOWSPLIT"], babymonths)

    group = _("Transferred Out {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.EntryReasonID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear, movement.TRANSFER),
            er["ID"], er["REASONNAME"], "ER_TRANSFEROUT", group, 100, er["SHOWSPLIT"], babymonths)

    group = _("Escaped {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.EntryReasonID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear, movement.ESCAPED),
            er["ID"], er["REASONNAME"], "ER_ESCAPED", group, 110, er["SHOWSPLIT"], babymonths)

    group = _("Stolen {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.EntryReasonID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear, movement.STOLEN),
            er["ID"], er["REASONNAME"], "ER_STOLEN", group, 120, er["SHOWSPLIT"], babymonths)

    group = _("Released To Wild {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.EntryReasonID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear, movement.RELEASED),
            er["ID"], er["REASONNAME"], "ER_STOLEN", group, 130, er["SHOWSPLIT"], babymonths)

    group = _("Transferred In {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.EntryReasonID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND a.IsTransfer = 1 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear),
            er["ID"], er["REASONNAME"], "ER_TRANSFERIN", group, 140, er["SHOWSPLIT"], babymonths)

    if splitadoptions:
        group = _("Adopted Transferred In {0}", l).format(year)
        for er in allreasons:
            entryreason_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
                "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
                "a.EntryReasonID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
                "AND a.IsTransfer = 1 AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
                "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear, movement.ADOPTION),
                er["ID"], er["REASONNAME"], "ER_TRANSFERINADOPTED", group, 150, er["SHOWSPLIT"], babymonths)
    
    async.set_progress_value(dbo, 3)

    # Write out all our changes in one go
    update_db(year)
    return "OK"

def auto_cancel_holds(dbo):
    """
    Automatically cancels holds after the hold until date value set
    """
    sql = "UPDATE animal SET IsHold = 0 WHERE IsHold = 1 AND " \
        "HoldUntilDate Is Not Null AND " \
        "HoldUntilDate <= %s" % db.dd(now(dbo.timezone))
    count = db.execute(dbo, sql)
    al.debug("cancelled %d holds" % (count), "animal.auto_cancel_holds", dbo)

def maintenance_reassign_all_codes(dbo):
    """
    Goes through all animals in the system and regenerates their 
    shelter codes.
    """
    db.execute(dbo, "UPDATE animal SET YearCodeID = 0, UniqueCodeID = 0, " \
        "ShelterCode = ID, ShortCode = ID")
    animals = db.query(dbo, "SELECT ID, AnimalTypeID, DateBroughtIn, AnimalName " \
        "FROM animal ORDER BY ID")
    for a in animals:
        sheltercode, shortcode, unique, year = calc_shelter_code(dbo, a["ANIMALTYPEID"], a["ENTRYREASONID"], a["SPECIESID"], a["DATEBROUGHTIN"])
        sql = "UPDATE animal SET ShelterCode = '%s', ShortCode = '%s', " \
            "UniqueCodeID = %d, YearCodeID = %d WHERE ID = %d" % ( \
            sheltercode, shortcode, unique, year, a["ID"])
        al.debug("RECODE: %s -> %s" % (a["ANIMALNAME"], sheltercode), "animal.maintenance_reassign_all_codes", dbo)
        db.execute(dbo, sql)

def maintenance_reassign_shelter_codes(dbo):
    """
    Goes through all animals on the shelter and regenerates their 
    shelter codes.
    """
    db.execute(dbo, "UPDATE animal SET YearCodeID = 0, UniqueCodeID = 0, " \
        "ShelterCode = ID, ShortCode = ID WHERE Archived = 0 ORDER BY ID")
    animals = db.query(dbo, "SELECT ID, AnimalTypeID, DateBroughtIn, AnimalName " \
        "FROM animal WHERE Archived = 0")
    for a in animals:
        sheltercode, shortcode, unique, year = calc_shelter_code(dbo, a["ANIMALTYPEID"], a["ENTRYREASONID"], a["SPECIESID"], a["DATEBROUGHTIN"])
        sql = "UPDATE animal SET ShelterCode = '%s', ShortCode = '%s', " \
            "UniqueCodeID = %d, YearCodeID = %d WHERE ID = %d" % ( \
            sheltercode, shortcode, unique, year, a["ID"])
        al.debug("RECODE: %s -> %s" % (a["ANIMALNAME"], sheltercode), "animal.maintenance_reassign_shelter_codes", dbo)
        db.execute(dbo, sql)

def maintenance_animal_figures(dbo, includeMonths = True, includeAnnual = True):
    """
    Finds all months/years the system has animal data for and generates 
    figures reporting data for them.
    """
    if dbo.dbtype == "POSTGRESQL":
        monthsyears = db.query(dbo, "SELECT DISTINCT CAST(EXTRACT(YEAR FROM DATEBROUGHTIN) AS INTEGER) AS TheYear, CAST(EXTRACT(MONTH FROM DATEBROUGHTIN) AS INTEGER) AS TheMonth FROM animal")
        years = db.query(dbo, "SELECT DISTINCT CAST(EXTRACT(YEAR FROM DATEBROUGHTIN) AS INTEGER) AS TheYear FROM animal")
    else:
        monthsyears = db.query(dbo, "SELECT DISTINCT MONTH(DateBroughtIn) AS TheMonth, YEAR(DateBroughtIn) AS TheYear FROM animal")
        years = db.query(dbo, "SELECT DISTINCT YEAR(DateBroughtIn) AS TheYear FROM animal")
    if includeMonths:
        for my in monthsyears:
            al.debug("update_animal_figures: month=%d, year=%d" % (my["THEMONTH"], my["THEYEAR"]), "animal.maintenance_animal_figures", dbo)
            update_animal_figures(dbo, int(my["THEMONTH"]), int(my["THEYEAR"]))
    if includeAnnual:
        for y in years:
            al.debug("update_animal_figures_annual: year=%d" % y["THEYEAR"], "animal.maintenance_animal_figures", dbo)
            update_animal_figures_annual(dbo, int(y["THEYEAR"]))

