
import asm3.additional
import asm3.al
import asm3.animalname
import asm3.asynctask
import asm3.audit
import asm3.configuration
import asm3.diary
import asm3.dbfs
import asm3.financial
import asm3.log
import asm3.lookups
import asm3.media
import asm3.movement
import asm3.publishers.base
import asm3.utils
import asm3.users

from asm3.i18n import _, date_diff, date_diff_days, format_diff, display2python, python2display, remove_time, subtract_years, subtract_months
from asm3.i18n import add_days, subtract_days, monday_of_week, first_of_month, last_of_month, first_of_year
from asm3.typehints import Database, List, PostedData, ResultRow, Results, Tuple

from datetime import datetime
from random import choice

# Sorts for functions
ASCENDING = 0
DESCENDING = 1

class LocationFilter(object):
    locationfilter = ""
    siteid = 0
    visibleanimalids = ""
    
    def __init__(self, locationfilter: str, siteid: int, visibleanimalids: str):
        self.locationfilter = locationfilter
        self.siteid = siteid
        self.visibleanimalids = visibleanimalids
    
    def clause(self, tablequalifier: str = "", 
            whereprefix: bool = False, andprefix: bool = False, andsuffix: bool = False) -> str:
        """
        Returns a where clause that excludes animals not in the locationfilter
        locationfilter: comma separated list of internallocation IDs and special values
            -1: animals on a trial/full adoption
            -2: animals in a foster home
            -3: animals transferred away
            -4: animals escaped
            -5: animals reclaimed
            -6: animals stolen
            -7: animals released to wild/tnr
            -8: animals in a retailer
            -9: non-shelter animals (excluded from this functionality)
            -12: has set visibleanimalids for "My fosters"
            -13: has set visibleanimalids for "My coordinated animals"
            -21: died on shelter
            -22: doa
            -23: euthanised
            -24: died off shelter
            -31: only dogs
            -32: only cats
        siteid: The animal's site, as linked to internallocation
        visibleanimalids: comma separated list of animal ids this user is allowed to view (-12 must be present in filter)
        tablequalifier: The animal table name in the query
        """
        locationfilter = self.locationfilter
        if locationfilter is None: locationfilter = ""
        siteid = self.siteid
        visibleanimalids = self.visibleanimalids
        if locationfilter == "" and siteid == 0 and visibleanimalids == "": return ""
        if tablequalifier == "": tablequalifier = "animal"
        clauses = []
        if locationfilter != "":
            internallocs = []
            movetypes = []
            locs = locationfilter.split(",")
            # Extract movement types and internal locations from the filter first
            for l in locs:
                if l in ( "-1", "-2", "-3", "-4", "-5", "-6", "-7", "-8"):
                    movetypes.append(l.replace("-", ""))
                elif l.find("-") == -1:
                    internallocs.append(l)
            # Internal locations
            if len(internallocs) > 0:
                clauses.append(f'({tablequalifier}.Archived=0 AND {tablequalifier}.ShelterLocation IN ({",".join(internallocs)}) ' \
                    f'AND ({tablequalifier}.ActiveMovementType Is Null OR {tablequalifier}.ActiveMovementType=0))') 
            # Active movement types
            if len(movetypes) > 0:
                clauses.append(f'{tablequalifier}.ActiveMovementType IN ({",".join(movetypes)})')
            # Non-shelter
            if "-9" in locs:
                clauses.append(f"{tablequalifier}.NonShelterAnimal=1")
            # My Fosters, My Coordinated Animals
            if "-12" in locs or "-13" in locs:
                if visibleanimalids == "": visibleanimalids = "0"
                clauses.append(f"{tablequalifier}.ID IN ({visibleanimalids})")
            # Died on shelter
            if "-21" in locs:
                clauses.append(f"({tablequalifier}.DeceasedDate Is Not Null AND {tablequalifier}.PutToSleep=0 AND {tablequalifier}.IsDOA=0 AND {tablequalifier}.DiedOffShelter=0)")
            # DOA
            if "-22" in locs:
                clauses.append(f"({tablequalifier}.DeceasedDate Is Not Null AND {tablequalifier}.PutToSleep=0 AND {tablequalifier}.IsDOA=1 AND {tablequalifier}.DiedOffShelter=0)")
            # Euthanised
            if "-23" in locs:
                clauses.append(f"({tablequalifier}.DeceasedDate Is Not Null AND {tablequalifier}.PutToSleep=1 AND {tablequalifier}.IsDOA=0 AND {tablequalifier}.DiedOffShelter=0)")
            # Died Off Shelter
            if "-24" in locs:
                clauses.append(f"({tablequalifier}.DeceasedDate Is Not Null AND {tablequalifier}.DiedOffShelter=1)")
            # All Dogs
            if "-31" in locs:
                clauses.append(f"({tablequalifier}.SpeciesID = 1 AND {tablequalifier}.Archived=0)")
            # All Cats
            if "-32" in locs:
                clauses.append(f"({tablequalifier}.SpeciesID = 2 AND {tablequalifier}.Archived=0)")
        if siteid != 0:
            clauses.append("il.SiteID = %s" % siteid)
        c = "(" + " OR ".join(clauses) + ")"
        # If we've got nothing left by this point, don't add a prefix/suffix/where
        if c == "": return ""
        if andprefix:
            c = " AND %s" % c
        if andsuffix:
            c = "%s AND " % c
        if whereprefix:
            c = " WHERE %s" % c
        return c

    def __contains__(self, key: ResultRow) -> bool:
        return self.match(key)

    def match(self, a: ResultRow) -> bool:
        """
        Returns True if the animal a matches the locationfilter
        """
        locationfilter = self.locationfilter
        siteid = self.siteid
        visibleanimalids = self.visibleanimalids
        if locationfilter == "" and siteid == 0: return True
        if siteid != 0:
            if a.siteid == 0 or a.siteid == siteid: return True
        if locationfilter != "":
            locs = locationfilter.split(",")
            if a.activemovementtype == 1 and "-1" in locs: return True 
            if a.activemovementtype == 2 and "-2" in locs: return True
            if a.activemovementtype == 3 and "-3" in locs: return True
            if a.activemovementtype == 4 and "-4" in locs: return True
            if a.activemovementtype == 5 and "-5" in locs: return True
            if a.activemovementtype == 6 and "-6" in locs: return True
            if a.activemovementtype == 7 and "-7" in locs: return True
            if a.activemovementtype == 8 and "-8" in locs: return True
            if a.nonshelteranimal == 1 and "-9" in locs: return True
            if a.deceaseddate and a.isdoa == 0 and a.puttosleep == 0 and a.diedoffshelter == 0 and "-21" in locs: return True
            if a.deceaseddate and a.isdoa == 1 and a.puttosleep == 0 and a.diedoffshelter == 0 and "-22" in locs: return True
            if a.deceaseddate and a.isdoa == 0 and a.puttosleep == 1 and a.diedoffshelter == 0 and "-23" in locs: return True
            if a.deceaseddate and a.diedoffshelter == 1 and "-24" in locs: return True
            if a.archived == 0 and a.speciesid == 1 and "-31" in locs: return True
            if a.archived == 0 and a.speciesid == 2 and "-32" in locs: return True
            if a.archived == 0 and str(a.shelterlocation) in locs: return True
        if visibleanimalids != "":
            if str(a.ID) in visibleanimalids.split(","): return True
        return False

    def reduce(self, rows: Results, animalidcolumn: str = "ANIMALID") -> Results:
        """
        Given a resultset of rows, removes all rows that are no present in visibleanimalids.
        """
        if self.visibleanimalids == "": return rows
        rowsout = []
        for r in rows:
            if str(r[animalidcolumn]) in self.visibleanimalids.split(","):
                rowsout.append(r)
        return rowsout

def get_animal_query(dbo: Database) -> str:
    """
    Returns a select for animal rows with resolved lookups
    """
    today = dbo.sql_today()
    endoftoday = dbo.sql_date(dbo.today(settime="23:59:59"))
    twodaysago = dbo.sql_date(dbo.today(offset=-2))
    return "SELECT a.*, " \
        "at.AnimalType AS AnimalTypeName, " \
        "ba1.AnimalName AS BondedAnimal1Name, " \
        "ba1.ShelterCode AS BondedAnimal1Code, " \
        "ba1.Archived AS BondedAnimal1Archived, " \
        "ba1.IdentichipNumber AS BondedAnimal1IdentichipNumber, " \
        "ba2.AnimalName AS BondedAnimal2Name, " \
        "ba2.ShelterCode AS BondedAnimal2Code, " \
        "ba2.Archived AS BondedAnimal2Archived, " \
        "ba2.IdentichipNumber AS BondedAnimal2IdentichipNumber, " \
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
        "o.OwnerName AS OwnerName, " \
        "ov.OwnerName AS OwnersVetName, " \
        "ov.OwnerAddress AS OwnersVetAddress, " \
        "ov.OwnerTown AS OwnersVetTown, " \
        "ov.OwnerCounty AS OwnersVetCounty, " \
        "ov.OwnerPostcode AS OwnersVetPostcode, " \
        "ov.WorkTelephone AS OwnersVetWorkTelephone, " \
        "ov.EmailAddress AS OwnersVetEmailAddress, " \
        "ov.MembershipNumber AS OwnersVetLicenceNumber, " \
        "cv.OwnerName AS CurrentVetName, " \
        "cv.OwnerForeNames AS CurrentVetForeNames, " \
        "cv.OwnerSurname AS CurrentVetSurname, " \
        "cv.OwnerAddress AS CurrentVetAddress, " \
        "cv.OwnerTown AS CurrentVetTown, " \
        "cv.OwnerCounty AS CurrentVetCounty, " \
        "cv.OwnerPostcode AS CurrentVetPostcode, " \
        "cv.WorkTelephone AS CurrentVetWorkTelephone, " \
        "cv.EmailAddress AS CurrentVetEmailAddress, " \
        "cv.MembershipNumber AS CurrentVetLicenceNumber, " \
        "nv.OwnerName AS NeuteringVetName, " \
        "nv.OwnerAddress AS NeuteringVetAddress, " \
        "nv.OwnerTown AS NeuteringVetTown, " \
        "nv.OwnerCounty AS NeuteringVetCounty, " \
        "nv.OwnerPostcode AS NeuteringVetPostcode, " \
        "nv.WorkTelephone AS NeuteringVetWorkTelephone, " \
        "nv.EmailAddress AS NeuteringVetEmailAddress, " \
        "nv.MembershipNumber AS NeuteringVetLicenceNumber, " \
        "oo.OwnerName AS OriginalOwnerName, " \
        "oo.OwnerTitle AS OriginalOwnerTitle, " \
        "oo.OwnerInitials AS OriginalOwnerInitials, " \
        "oo.OwnerForeNames AS OriginalOwnerForeNames, " \
        "oo.OwnerSurname AS OriginalOwnerSurname, " \
        "oo.OwnerAddress AS OriginalOwnerAddress, " \
        "oo.OwnerTown AS OriginalOwnerTown, " \
        "oo.OwnerCounty AS OriginalOwnerCounty, " \
        "oo.OwnerPostcode AS OriginalOwnerPostcode, " \
        "oo.OwnerCountry AS OriginalOwnerCountry, " \
        "oo.HomeTelephone AS OriginalOwnerHomeTelephone, " \
        "oo.WorkTelephone AS OriginalOwnerWorkTelephone, " \
        "oo.MobileTelephone AS OriginalOwnerMobileTelephone, " \
        "oo.EmailAddress AS OriginalOwnerEmailAddress, " \
        "oo.IdentificationNumber AS OriginalOwnerIDNumber, " \
        "oo.LatLong AS OriginalOwnerLatLong, " \
        "oo.PopupWarning AS OriginalOwnerPopupWarning, " \
        "oj.JurisdictionName AS OriginalOwnerJurisdiction, " \
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
        "co.OwnerCountry AS CurrentOwnerCountry, " \
        "co.HomeTelephone AS CurrentOwnerHomeTelephone, " \
        "co.WorkTelephone AS CurrentOwnerWorkTelephone, " \
        "co.MobileTelephone AS CurrentOwnerMobileTelephone, " \
        "co.EmailAddress AS CurrentOwnerEmailAddress, " \
        "co.EmailAddress2 AS CurrentOwnerEmailAddress2, " \
        "co.IdentificationNumber AS CurrentOwnerIDNumber, " \
        "co.AdditionalFlags AS CurrentOwnerAdditionalFlags, " \
        "co.Comments AS CurrentOwnerComments, " \
        "co.PopupWarning AS CurrentOwnerPopupWarning, " \
        "co.LatLong AS CurrentOwnerLatLong, " \
        "cj.JurisdictionName AS CurrentOwnerJurisdiction, " \
        "bo.OwnerName AS BroughtInByOwnerName, " \
        "bo.OwnerAddress AS BroughtInByOwnerAddress, " \
        "bo.OwnerTown AS BroughtInByOwnerTown, " \
        "bo.OwnerCounty AS BroughtInByOwnerCounty, " \
        "bo.OwnerPostcode AS BroughtInByOwnerPostcode, " \
        "bo.HomeTelephone AS BroughtInByHomeTelephone, " \
        "bo.WorkTelephone AS BroughtInByWorkTelephone, " \
        "bo.MobileTelephone AS BroughtInByMobileTelephone, " \
        "bo.EmailAddress AS BroughtInByEmailAddress, " \
        "bo.LatLong AS BroughtInByLatLong, " \
        "bo.IdentificationNumber AS BroughtInByIDNumber, " \
        "bj.JurisdictionName AS BroughtInByJurisdiction, " \
        "ro.ID AS ReservedOwnerID, " \
        "ro.OwnerName AS ReservedOwnerName, " \
        "ro.OwnerTitle AS ReservedOwnerTitle, " \
        "ro.OwnerInitials AS ReservedOwnerInitials, " \
        "ro.OwnerForeNames AS ReservedOwnerForeNames, " \
        "ro.OwnerSurname AS ReservedOwnerSurname, " \
        "ro.OwnerAddress AS ReservedOwnerAddress, " \
        "ro.OwnerTown AS ReservedOwnerTown, " \
        "ro.OwnerCounty AS ReservedOwnerCounty, " \
        "ro.OwnerPostcode AS ReservedOwnerPostcode, " \
        "ro.HomeTelephone AS ReservedOwnerHomeTelephone, " \
        "ro.WorkTelephone AS ReservedOwnerWorkTelephone, " \
        "ro.MobileTelephone AS ReservedOwnerMobileTelephone, " \
        "ro.EmailAddress AS ReservedOwnerEmailAddress, " \
        "ro.IdentificationNumber AS ReservedOwnerIDNumber, " \
        "ro.LatLong AS ReservedOwnerLatLong, " \
        "rj.JurisdictionName AS ReservedOwnerJurisdiction, " \
        "ar.ReservationDate AS ReservationDate, " \
        "ars.StatusName AS ReservationStatusName, " \
        "ao.OwnerName AS AdoptionCoordinatorName, " \
        "ao.OwnerForeNames AS AdoptionCoordinatorForenames, " \
        "ao.OwnerSurname AS AdoptionCoordinatorSurname, " \
        "ao.HomeTelephone AS AdoptionCoordinatorHomeTelephone, " \
        "ao.WorkTelephone AS AdoptionCoordinatorWorkTelephone, " \
        "ao.MobileTelephone AS AdoptionCoordinatorMobileTelephone, " \
        "ao.EmailAddress AS AdoptionCoordinatorEmailAddress, " \
        "er.ReasonName AS EntryReasonName, " \
        "et.EntryTypeName AS EntryTypeName, " \
        "dr.ReasonName AS PTSReasonName, " \
        "il.LocationName AS ShelterLocationName, " \
        "il.LocationDescription AS ShelterLocationDescription, " \
        "il.SiteID AS SiteID, " \
        "se.SiteName AS SiteName, " \
        "pl.LocationName AS PickupLocationName, " \
        "j.JurisdictionName, " \
        "ac.ID AS AnimalControlIncidentID, " \
        "itn.IncidentName AS AnimalControlIncidentName, " \
        "ac.IncidentDateTime AS AnimalControlIncidentDate, " \
        "diet.DietName AS ActiveDietName, " \
        "diet.DietDescription AS ActiveDietDescription, " \
        "adi.DateStarted AS ActiveDietStartDate, " \
        "adi.Comments AS ActiveDietComments, " \
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
            "WHEN a.Archived = 1 AND a.ActiveMovementType = 7 AND a.SpeciesID = 2 THEN " \
            "(SELECT MovementType FROM lksmovementtype WHERE ID=13) " \
            "WHEN a.Archived = 0 AND a.ActiveMovementType IN (2, 8) THEN " \
            "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
            "WHEN a.Archived = 1 AND a.DeceasedDate Is Not Null THEN " \
            "(SELECT ReasonName FROM deathreason WHERE ID = a.PTSReasonID) " \
            "WHEN a.Archived = 1 AND a.DeceasedDate Is Null AND a.ActiveMovementID <> 0 THEN " \
            "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
            "ELSE " \
            "(SELECT LocationName FROM internallocation WHERE ID=a.ShelterLocation) " \
        "END AS DisplayLocationName, " \
        "CASE WHEN a.DeceasedDate Is Not Null AND a.PutToSleep = 0 AND a.IsDOA = 0 THEN " \
                "(SELECT Outcome FROM lksoutcome WHERE ID = 2) " \
            "WHEN a.DeceasedDate Is Not Null AND a.IsDOA = 1 THEN " \
                "(SELECT Outcome FROM lksoutcome WHERE ID = 3) " \
            "WHEN a.DeceasedDate Is Not Null AND a.PutToSleep = 1 THEN " \
                "(SELECT Outcome FROM lksoutcome WHERE ID = 4) " \
            "WHEN a.ActiveMovementDate Is Not Null THEN " \
                "(SELECT Outcome FROM lksoutcome WHERE ID = a.ActiveMovementType + 10) " \
            "ELSE " \
                "(SELECT Outcome FROM lksoutcome WHERE ID = 1) " \
        "END AS OutcomeName, " \
        "CASE WHEN a.DeceasedDate Is Not Null THEN a.DeceasedDate " \
            "WHEN a.ActiveMovementDate Is Not Null THEN a.ActiveMovementDate " \
            "ELSE Null " \
        "END AS OutcomeDate, " \
        "CASE WHEN a.DeceasedDate Is Not Null THEN " \
                "(SELECT ReasonName FROM deathreason WHERE ID = a.PTSReasonID) " \
            "WHEN a.ActiveMovementDate Is Not Null THEN co.OwnerName " \
            "ELSE '' " \
        "END AS OutcomeQualifier, " \
        "web.ID AS WebsiteMediaID, " \
        "web.MediaName AS WebsiteMediaName, " \
        "web.Date AS WebsiteMediaDate, " \
        "web.MediaNotes AS WebsiteMediaNotes, " \
        "(SELECT COUNT(*) FROM media mtc WHERE MediaMimeType = 'image/jpeg' AND mtc.LinkTypeID = 0 AND mtc.LinkID = a.ID " \
            "AND ExcludeFromPublish = 0) AS WebsiteImageCount, " \
        "doc.ID AS DocMediaID, " \
        "doc.MediaName AS DocMediaName, " \
        "doc.Date AS DocMediaDate, " \
        "vid.MediaName AS WebsiteVideoURL, " \
        "vid.MediaNotes AS WebsiteVideoNotes, " \
        f"CASE WHEN EXISTS(SELECT ID FROM adoption WHERE AnimalID = a.ID AND MovementType = 1 AND MovementDate > {today}) THEN 1 ELSE 0 END AS HasFutureAdoption, " \
        "fo.OwnerName AS FutureOwnerName, " \
        "fo.EmailAddress AS FutureOwnerEmailAddress, " \
        "(SELECT COUNT(*) FROM adoption WHERE AnimalID = a.ID AND MovementType = 0 AND ReservationCancelledDate Is Null) AS ActiveReservations, " \
        f"(SELECT COUNT(*) FROM media WHERE MediaMimeType = 'image/jpeg' AND Date >= {twodaysago} AND LinkID = a.ID AND LinkTypeID = 0) AS RecentlyChangedImages, " \
        f"CASE WHEN EXISTS(SELECT amt.DateRequired FROM animalmedicaltreatment amt INNER JOIN animalmedical am ON am.ID=amt.AnimalMedicalID WHERE amt.AnimalID=a.ID AND amt.DateRequired <= {today} AND amt.DateGiven Is Null AND am.Status=0) THEN 1 ELSE 0 END AS HasOutstandingMedical, " \
        "CASE WHEN ab.ID Is Not Null THEN 1 ELSE 0 END AS HasActiveBoarding, " \
        "ab.InDateTime AS ActiveBoardingInDate, " \
        "ab.OutDateTime AS ActiveBoardingOutDate, " \
        "(SELECT COUNT(*) FROM animalvaccination WHERE AnimalID = a.ID AND DateOfVaccination Is Not Null) AS VaccGivenCount, " \
        f"(SELECT COUNT(*) FROM animalvaccination WHERE AnimalID = a.ID AND DateOfVaccination Is Null AND DateRequired < {today}) AS VaccOutstandingCount, " \
        "rvac.DateOfVaccination AS VaccRabiesDate, " \
        "rvact.VaccinationType AS VaccRabiesName, " \
        "rvac.RabiesTag AS VaccRabiesTag, " \
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
        "(SELECT Name FROM lksynunk l WHERE l.ID = a.IsGoodWithChildren) AS IsGoodWithChildrenName, " \
        "(SELECT Name FROM lksynun l WHERE l.ID = a.IsGoodWithCats) AS IsGoodWithCatsName, " \
        "(SELECT Name FROM lksynun l WHERE l.ID = a.IsGoodWithDogs) AS IsGoodWithDogsName, " \
        "(SELECT Name FROM lksynun l WHERE l.ID = a.IsGoodWithElderly) AS IsGoodWithElderlyName, " \
        "(SELECT Name FROM lksynun l WHERE l.ID = a.IsHouseTrained) AS IsHouseTrainedName, " \
        "(SELECT Name FROM lksynun l WHERE l.ID = a.IsCrateTrained) AS IsCrateTrainedName, " \
        "(SELECT Name FROM lksynun l WHERE l.ID = a.IsGoodTraveller) AS IsGoodTravellerName, " \
        "(SELECT Name FROM lksynun l WHERE l.ID = a.IsGoodOnLead) AS IsGoodOnLeadName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.IsNotAvailableForAdoption) AS IsNotAvailableForAdoptionName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.IsNotForRegistration) AS IsNotForRegistrationName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.HasSpecialNeeds) AS HasSpecialNeedsName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.DiedOffShelter) AS DiedOffShelterName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.HasActiveReserve) AS HasActiveReserveName, " \
        "(SELECT Name FROM lksyesno l WHERE l.ID = a.HasTrialAdoption) AS HasTrialAdoptionName, " \
        "(SELECT SentDate FROM animalpublished WHERE PublishedTo='first' AND AnimalID=a.ID) AS DateAvailableForAdoption " \
        "FROM animal a " \
        "LEFT OUTER JOIN animal ba1 ON ba1.ID = a.BondedAnimalID " \
        "LEFT OUTER JOIN animalvaccination rvac ON rvac.ID = (SELECT MAX(ID) FROM animalvaccination rvaci WHERE rvaci.AnimalID = a.ID AND " \
            "rvaci.RabiesTag Is Not Null AND rvaci.RabiesTag <> '' AND rvaci.DateOfVaccination Is Not Null) " \
        "LEFT OUTER JOIN vaccinationtype rvact ON rvact.ID = rvac.VaccinationID " \
        "LEFT OUTER JOIN animal ba2 ON ba2.ID = a.BondedAnimal2ID " \
        "LEFT OUTER JOIN animaltype at ON at.ID = a.AnimalTypeID " \
        "LEFT OUTER JOIN basecolour bc ON bc.ID = a.BaseColourID " \
        "LEFT OUTER JOIN species sp ON sp.ID = a.SpeciesID " \
        "LEFT OUTER JOIN lksex sx ON sx.ID = a.Sex " \
        "LEFT OUTER JOIN lksize sz ON sz.ID = a.Size " \
        "LEFT OUTER JOIN entryreason er ON er.ID = a.EntryReasonID " \
        "LEFT OUTER JOIN lksentrytype et ON et.ID = a.EntryTypeID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN site se ON se.ID = il.SiteID " \
        "LEFT OUTER JOIN pickuplocation pl ON pl.ID = a.PickupLocationID " \
        "LEFT OUTER JOIN jurisdiction j ON j.ID = a.JurisdictionID " \
        "LEFT OUTER JOIN media web ON web.ID = (SELECT MAX(ID) FROM media sweb WHERE sweb.LinkID = a.ID AND sweb.LinkTypeID = 0 AND sweb.WebsitePhoto = 1) " \
        "LEFT OUTER JOIN media vid ON vid.ID = (SELECT MAX(ID) FROM media svid WHERE svid.LinkID = a.ID AND svid.LinkTypeID = 0 AND svid.WebsiteVideo = 1) " \
        "LEFT OUTER JOIN media doc ON doc.ID = (SELECT MAX(ID) FROM media sdoc WHERE sdoc.LinkID = a.ID AND sdoc.LinkTypeID = 0 AND sdoc.DocPhoto = 1) " \
        "LEFT OUTER JOIN breed bd ON bd.ID = a.BreedID " \
        "LEFT OUTER JOIN breed bd2 ON bd2.ID = a.Breed2ID " \
        "LEFT OUTER JOIN lkcoattype ct ON ct.ID = a.CoatType " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "LEFT OUTER JOIN lksmovementtype mt ON mt.ID = a.ActiveMovementType " \
        "LEFT OUTER JOIN owner o ON o.ID = a.OwnerID " \
        "LEFT OUTER JOIN owner ov ON ov.ID = a.OwnersVetID " \
        "LEFT OUTER JOIN owner cv ON cv.ID = a.CurrentVetID " \
        "LEFT OUTER JOIN owner nv ON nv.ID = a.NeuteredByVetID " \
        "LEFT OUTER JOIN owner oo ON oo.ID = a.OriginalOwnerID " \
        "LEFT OUTER JOIN jurisdiction oj ON oj.ID = oo.JurisdictionID " \
        "LEFT OUTER JOIN owner bo ON bo.ID = a.BroughtInByOwnerID " \
        "LEFT OUTER JOIN jurisdiction bj ON bj.ID = bo.JurisdictionID " \
        "LEFT OUTER JOIN owner ao ON ao.ID = a.AdoptionCoordinatorID " \
        "LEFT OUTER JOIN adoption am ON am.ID = a.ActiveMovementID " \
        "LEFT OUTER JOIN users au ON au.UserName = am.CreatedBy " \
        "LEFT OUTER JOIN owner co ON co.ID = am.OwnerID " \
        "LEFT OUTER JOIN jurisdiction cj ON cj.ID = co.JurisdictionID " \
        f"LEFT OUTER JOIN animalboarding ab ON ab.ID = (SELECT MAX(ID) FROM animalboarding abi WHERE abi.AnimalID = a.ID AND InDateTime <= {endoftoday} AND OutDateTime >= {today}) " \
        "LEFT OUTER JOIN animaldiet adi ON adi.ID = (SELECT MAX(ID) FROM animaldiet sadi WHERE sadi.AnimalID = a.ID) " \
        "LEFT OUTER JOIN diet ON diet.ID = adi.DietID " \
        "LEFT OUTER JOIN animalcontrolanimal aca ON a.ID=aca.AnimalID and aca.AnimalControlID = (SELECT MAX(saca.AnimalControlID) FROM animalcontrolanimal saca WHERE saca.AnimalID = a.ID) " \
        "LEFT OUTER JOIN animalcontrol ac ON ac.ID = aca.AnimalControlID " \
        "LEFT OUTER JOIN incidenttype itn ON itn.ID = ac.IncidentTypeID " \
        "LEFT OUTER JOIN adoption ar ON ar.ID = (SELECT MAX(sar.ID) FROM adoption sar WHERE sar.AnimalID = a.ID AND sar.MovementType = 0 AND sar.MovementDate Is Null AND sar.ReservationDate Is Not Null AND sar.ReservationCancelledDate Is Null) " \
        "LEFT OUTER JOIN reservationstatus ars ON ars.ID = ar.ReservationStatusID " \
        "LEFT OUTER JOIN owner ro ON ro.ID = ar.OwnerID " \
        f"LEFT OUTER JOIN adoption fa ON fa.ID = (SELECT MAX(far.ID) FROM adoption far WHERE far.AnimalID = a.ID AND far.MovementType = 1 AND far.MovementDate Is Not Null AND far.MovementDate > {today} AND far.ReturnDate Is Null) " \
        "LEFT OUTER JOIN owner fo ON fo.ID = fa.OwnerID " \
        "LEFT OUTER JOIN jurisdiction rj ON rj.ID = ro.JurisdictionID "

def get_animal_brief_query(dbo: Database) -> str:
    today = dbo.sql_today()
    endoftoday = dbo.sql_date(dbo.today(settime="23:59:59"))
    return "SELECT a.AcceptanceNumber, a.ActiveMovementID, a.ActiveMovementType, " \
        "(SELECT COUNT(*) FROM adoption WHERE AnimalID = a.ID AND MovementType = 0 AND ReservationCancelledDate Is Null) AS ActiveReservations, " \
        "a.AdditionalFlags, " \
        "a.Adoptable, " \
        "a.AdoptionCoordinatorID, " \
        "ao.OwnerName AS AdoptionCoordinatorName, " \
        "a.AgeGroup, " \
        "a.AnimalComments, " \
        "a.AnimalAge, " \
        "a.AnimalName, " \
        "t.AnimalType AS AnimalTypeName, " \
        "a.Archived, " \
        "bc.BaseColour AS BaseColourName, " \
        "a.BondedAnimalID, " \
        "a.BondedAnimal2ID, " \
        "a.BreedName, " \
        "CASE " \
            "WHEN EXISTS(SELECT ItemValue FROM configuration WHERE ItemName Like 'UseShortShelterCodes' AND ItemValue = 'Yes') " \
            "THEN a.ShortCode ELSE a.ShelterCode " \
        "END AS Code, " \
        "a.CombiTested, " \
        "a.CombiTestResult, " \
        "a.CrueltyCase, " \
        "co.ID AS CurrentOwnerID, " \
        "co.OwnerName AS CurrentOwnerName, " \
        "a.DateOfBirth, " \
        "a.DaysOnShelter, " \
        "a.DeceasedDate, " \
        "a.DisplayLocation, " \
        "CASE " \
            "WHEN a.Archived = 0 AND a.ActiveMovementType = 1 AND a.HasTrialAdoption = 1 THEN " \
            "(SELECT MovementType FROM lksmovementtype WHERE ID=11) " \
            "WHEN a.Archived = 0 AND a.ActiveMovementType = 2 AND a.HasPermanentFoster = 1 THEN " \
            "(SELECT MovementType FROM lksmovementtype WHERE ID=12) " \
            "WHEN a.Archived = 1 AND a.ActiveMovementType = 7 AND a.SpeciesID = 2 THEN " \
            "(SELECT MovementType FROM lksmovementtype WHERE ID=13) " \
            "WHEN a.Archived = 0 AND a.ActiveMovementType IN (2, 8) THEN " \
            "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
            "WHEN a.Archived = 1 AND a.DeceasedDate Is Not Null THEN " \
            "(SELECT ReasonName FROM deathreason WHERE ID = a.PTSReasonID) " \
            "WHEN a.Archived = 1 AND a.DeceasedDate Is Null AND a.ActiveMovementID <> 0 THEN " \
            "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
            "ELSE " \
            "(SELECT LocationName FROM internallocation WHERE ID=a.ShelterLocation) " \
        "END AS DisplayLocationName, " \
        "er.ReasonName AS EntryReasonName, " \
        "et.EntryTypeName AS EntryTypeName, " \
        "a.FLVResult, " \
        "CASE WHEN ab.ID Is Not Null THEN 1 ELSE 0 END AS HasActiveBoarding, " \
        "a.HasActiveReserve, " \
        f"CASE WHEN EXISTS(SELECT ID FROM adoption WHERE AnimalID = a.ID AND MovementType = 1 AND MovementDate > {today}) THEN 1 ELSE 0 END AS HasFutureAdoption, " \
        "a.HasSpecialNeeds, " \
        "a.HasTrialAdoption, " \
        "a.HasPermanentFoster, " \
        "a.HeartwormTested, " \
        "a.HeartwormTestResult, " \
        "a.HiddenAnimalDetails, " \
        "a.HoldUntilDate, " \
        "a.ID, " \
        "a.Identichipped, " \
        "a.IdentichipNumber, " \
        "a.IsCourtesy, " \
        "a.IsGoodWithCats, " \
        "a.IsGoodWithChildren, " \
        "a.IsGoodWithDogs, " \
        "a.IsGoodWithElderly, " \
        "a.IsGoodOnLead, " \
        "a.IsGoodTraveller, " \
        "a.IsCrateTrained, " \
        "a.IsHouseTrained, " \
        "a.EnergyLevel, " \
        "a.IsHold, " \
        "a.IsNotAvailableForAdoption, " \
        "a.IsPickup, " \
        "a.IsQuarantine, " \
        "j.JurisdictionName, " \
        "a.LastChangedDate, " \
        "a.LastChangedBy, " \
        "a.Markings, " \
        "a.MostRecentEntryDate, " \
        "a.Neutered, " \
        "a.NonShelterAnimal, " \
        "a.OriginalOwnerID, " \
        "oo.OwnerName AS OriginalOwnerName, " \
        "a.OwnerID, " \
        "co.OwnerName, " \
        "pl.LocationName AS PickupLocationName, " \
        "a.PopupWarning, " \
        "a.RabiesTag, " \
        "a.Sex, " \
        "sx.Sex AS SexName, " \
        "a.ShelterCode, " \
        "a.ShelterLocation, " \
        "il.LocationName AS ShelterLocationName, " \
        "a.ShelterLocationUnit, " \
        "a.ShortCode, " \
        "se.SiteName, " \
        "a.SpeciesID, " \
        "sp.SpeciesName, " \
        "(SELECT COUNT(*) FROM animalvaccination WHERE AnimalID = a.ID AND DateOfVaccination Is Not Null) AS VaccGivenCount, " \
        "web.ID AS WebsiteMediaID, " \
        "web.MediaName AS WebsiteMediaName, " \
        "web.Date AS WebsiteMediaDate, " \
        "web.MediaNotes AS WebsiteMediaNotes " \
        "FROM animal a " \
        "LEFT OUTER JOIN animaltype t ON t.ID = a.AnimalTypeID " \
        "LEFT OUTER JOIN basecolour bc ON bc.ID = a.BaseColourID " \
        "LEFT OUTER JOIN species sp ON sp.ID = a.SpeciesID " \
        "LEFT OUTER JOIN lksex sx ON sx.ID = a.Sex " \
        "LEFT OUTER JOIN entryreason er ON er.ID = a.EntryReasonID " \
        "LEFT OUTER JOIN lksentrytype et ON et.ID = a.EntryTypeID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "LEFT OUTER JOIN site se ON se.ID = il.SiteID " \
        "LEFT OUTER JOIN pickuplocation pl ON pl.ID = a.PickupLocationID " \
        "LEFT OUTER JOIN jurisdiction j ON j.ID = a.JurisdictionID " \
        "LEFT OUTER JOIN media web ON web.ID = (SELECT MAX(ID) FROM media WHERE LinkID = a.ID AND LinkTypeID = 0 AND WebsitePhoto = 1) " \
        "LEFT OUTER JOIN owner ao ON ao.ID = a.AdoptionCoordinatorID " \
        "LEFT OUTER JOIN owner oo ON oo.ID = a.OriginalOwnerID " \
        "LEFT OUTER JOIN owner o ON o.ID = a.OwnerID " \
        "LEFT OUTER JOIN adoption am ON am.ID = a.ActiveMovementID " \
        "LEFT OUTER JOIN owner co ON co.ID = am.OwnerID " \
        f"LEFT OUTER JOIN animalboarding ab ON ab.ID = (SELECT MAX(ID) FROM animalboarding WHERE AnimalID = a.ID AND InDateTime <= {endoftoday} AND OutDateTime >= {today}) "

def get_animal_entry_query(dbo: Database) -> str:
    return "SELECT ae.*, " \
        "e.ReasonName AS EntryReasonName, " \
        "t.EntryTypeName AS EntryTypeName, " \
        "j.JurisdictionName, " \
        "pl.LocationName AS PickupLocationName, " \
        "oo.OwnerName AS OriginalOwnerName, " \
        "oo.OwnerAddress AS OriginalOwnerAddress, " \
        "oo.OwnerTown AS OriginalOwnerTown, " \
        "oo.OwnerCounty AS OriginalOwnerCounty, " \
        "oo.OwnerPostcode AS OriginalOwnerPostcode, " \
        "oo.EmailAddress AS OriginalOwnerEmail, " \
        "oo.HomeTelephone AS OriginalOwnerHomePhone, " \
        "oo.WorkTelephone AS OriginalOwnerWorkPhone, " \
        "oo.MobileTelephone AS OriginalOwnerMobilePhone, " \
        "bo.OwnerName AS BroughtInByOwnerName, " \
        "bo.OwnerAddress AS BroughtInByOwnerAddress, " \
        "bo.OwnerTown AS BroughtInByOwnerTown, " \
        "bo.OwnerCounty AS BroughtInByOwnerCounty, " \
        "bo.OwnerPostcode AS BroughtInByOwnerPostcode, " \
        "bo.EmailAddress AS BroughtInByOwnerEmail, " \
        "bo.HomeTelephone AS BroughtInByOwnerHomePhone, " \
        "bo.WorkTelephone AS BroughtInByOwnerWorkPhone, " \
        "bo.MobileTelephone AS BroughtInByOwnerMobilePhone, " \
        "ac.OwnerName AS CoordinatorOwnerName, " \
        "ac.OwnerAddress AS CoordinatorOwnerAddress, " \
        "ac.OwnerTown AS CoordinatorOwnerTown, " \
        "ac.OwnerCounty AS CoordinatorOwnerCounty, " \
        "ac.OwnerPostcode AS CoordinatorOwnerPostcode, " \
        "ac.EmailAddress AS CoordinatorOwnerEmail, " \
        "ac.HomeTelephone AS CoordinatorOwnerHomePhone, " \
        "ac.WorkTelephone AS CoordinatorOwnerWorkPhone, " \
        "ac.MobileTelephone AS CoordinatorOwnerMobilePhone " \
        "FROM animalentry ae " \
        "LEFT OUTER JOIN entryreason e ON e.ID = ae.EntryReasonID " \
        "LEFT OUTER JOIN lksentrytype t ON t.ID = ae.EntryTypeID " \
        "LEFT OUTER JOIN jurisdiction j ON j.ID = ae.JurisdictionID " \
        "LEFT OUTER JOIN pickuplocation pl ON pl.ID = ae.PickupLocationID " \
        "LEFT OUTER JOIN owner oo ON oo.ID = ae.OriginalOwnerID " \
        "LEFT OUTER JOIN owner bo ON bo.ID = ae.BroughtInByOwnerID " \
        "LEFT OUTER JOIN owner ac ON ac.ID = ae.AdoptionCoordinatorID "

def get_animal_status_query(dbo: Database) -> str:
    today = dbo.sql_today()
    endoftoday = dbo.sql_date(dbo.today(settime="23:59:59"))
    return "SELECT a.ID, a.ShelterCode, a.ShortCode, a.AnimalName, a.AnimalComments, " \
        "a.DeceasedDate, a.DateOfBirth, a.DiedOffShelter, a.PutToSleep, a.Neutered, a.Identichipped, a.SpeciesID, " \
        "dr.ReasonName AS PTSReasonName, " \
        "il.LocationName AS ShelterLocationName, " \
        "a.ShelterLocation, a.ShelterLocationUnit, " \
        "a.IsCourtesy, a.Adoptable, a.IsNotAvailableForAdoption, a.HasPermanentFoster, " \
        "a.CrueltyCase, a.NonShelterAnimal, a.IsHold, a.IsQuarantine, " \
        "a.DateBroughtIn, a.OriginalOwnerID, a.Archived, a.OwnerID, " \
        "a.ActiveMovementID, a.ActiveMovementDate, a.ActiveMovementType, a.ActiveMovementReturn, " \
        "a.HasActiveReserve, a.HasTrialAdoption, a.HasPermanentFoster, a.MostRecentEntryDate, a.DisplayLocation, " \
        "(SELECT COUNT(*) FROM adoption WHERE AnimalID = a.ID AND MovementType = 0 AND ReservationCancelledDate Is Null) AS ActiveReservations, " \
        f"CASE WHEN EXISTS(SELECT ID FROM adoption WHERE AnimalID = a.ID AND MovementType = 1 AND MovementDate > {today}) THEN 1 ELSE 0 END AS HasFutureAdoption, " \
        f"CASE WHEN EXISTS(SELECT ID FROM animalboarding WHERE AnimalID = a.ID AND InDateTime <= {endoftoday} AND OutDateTime >= {endoftoday}) THEN 1 ELSE 0 END AS HasActiveBoarding, " \
        "web.MediaName AS WebsiteMediaName, " \
        "web.MediaNotes AS WebsiteMediaNotes " \
        "FROM animal a " \
        "LEFT OUTER JOIN media web ON web.ID = (SELECT MAX(ID) FROM media sweb WHERE sweb.LinkID = a.ID AND sweb.LinkTypeID = 0 AND sweb.WebsitePhoto = 1) " \
        "LEFT OUTER JOIN deathreason dr ON dr.ID = a.PTSReasonID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation "

def get_animal_movement_status_query(dbo: Database) -> str:
    return "SELECT m.ID, m.MovementType, m.MovementDate, m.ReturnDate, " \
        "mt.MovementType AS MovementTypeName, " \
        "m.ReservationDate, m.ReservationCancelledDate, m.IsTrial, m.IsPermanentFoster, " \
        "m.AnimalID, m.OwnerID, o.OwnerName " \
        "FROM adoption m " \
        "INNER JOIN lksmovementtype mt ON mt.ID = m.MovementType " \
        "LEFT OUTER JOIN owner o ON m.OwnerID = o.ID "

def get_animal_emblem_query(dbo: Database) ->str:
    """ These are the fields that other queries can include when they want animal data with working emblems """
    return "a.ShelterCode, a.ShortCode, a.AnimalAge, a.DateOfBirth, a.AgeGroup, a.Fee, " \
        "a.AnimalName, a.BreedName, a.Sex, a.Neutered, a.DeceasedDate, a.SpeciesID, a.HasActiveReserve, " \
        "a.HasTrialAdoption, a.IsHold, a.IsQuarantine, a.HoldUntilDate, a.CrueltyCase, a.NonShelterAnimal, " \
        "a.ShelterLocation, a.ShelterLocationUnit, a.DisplayLocation, a.Adoptable, a.HasSpecialNeeds, " \
        "a.ActiveMovementID, a.ActiveMovementType, a.Archived, a.DaysOnShelter, a.IsNotAvailableForAdoption, " \
        "a.AdditionalFlags AS AnimalFlags, " \
        "a.CombiTested, a.HeartwormTested, a.CombiTestResult, a.FLVResult, a.HeartwormTestResult, " \
        "a.Identichipped, a.IdentichipNumber, " \
        "a.AcceptanceNumber AS LitterID, a.Weight, " \
        "(SELECT AnimalType FROM animaltype WHERE ID = a.AnimalTypeID) AS AnimalTypeName, " \
        "(SELECT SpeciesName FROM species WHERE ID=a.SpeciesID) AS SpeciesName, " \
        "(SELECT LocationName FROM internallocation WHERE ID=a.ShelterLocation) AS ShelterLocationName "

def get_animal(dbo: Database, animalid: int) -> ResultRow:
    """
    Returns a complete animal row by id, or None if not found
    (int) animalid: The animal to get
    """
    if animalid is None or animalid == 0: return None
    a = dbo.first_row( dbo.query(get_animal_query(dbo) + " WHERE a.ID = ?", [animalid]) )
    calc_ages(dbo, [a])
    embellish_mother(dbo, a)
    return a

def get_animal_sheltercode(dbo: Database, code: str) -> ResultRow:
    """
    Returns a complete animal row by ShelterCode
    """
    if code is None or code == "": return None
    a = dbo.first_row( dbo.query(get_animal_query(dbo) + " WHERE a.ShelterCode = ?", [code]) )
    calc_ages(dbo, [a])
    embellish_mother(dbo, a)
    return a

def embellish_mother(dbo: Database, a: ResultRow) -> ResultRow:
    """
    Adds the following litter-related fields to an animal result.
    MOTHERID, MOTHERCODE, MOTHERNAME
    """
    if a is None: return
    l = dbo.first_row(dbo.query("SELECT a.ID, a.ShelterCode, a.ShortCode, a.AnimalName " \
        "FROM animal a " \
        "INNER JOIN animallitter al ON al.ParentAnimalID = a.ID " \
        "WHERE al.AcceptanceNumber = ? " \
        "ORDER BY al.ID DESC", [a.ACCEPTANCENUMBER]))
    if l is not None:
        a.MOTHERID = l.ID
        a.MOTHERCODE = asm3.configuration.use_short_shelter_codes(dbo) and l.SHORTCODE or l.SHELTERCODE
        a.MOTHERNAME = l.ANIMALNAME
    else:
        a.MOTHERID = 0
        a.MOTHERCODE = ""
        a.MOTHERNAME = ""
    return a

def get_animals_ids(dbo: Database, sort: str, q: str, limit: int = 5, cachetime: int = 60) -> Results:
    """
    Given a recordset of animal IDs, goes and gets the
    full records.
    The idea is that we write the simplest possible animal queries to get the
    ID before feeding the list of IDs into the full animal_query. This performs
    a lot better than doing the full SELECT with ORDER BY/LIMIT
    """
    aids = []
    for aid in dbo.query(q, limit=limit):
        aids.append(aid["ID"])
    if len(aids) == 0: return [] # Return empty recordset if no results
    rows = dbo.query_cache(get_animal_query(dbo) + " WHERE a.ID IN (%s) ORDER BY %s" % (dbo.sql_placeholders(aids), sort), aids, age=cachetime, distincton="ID")
    return calc_ages(dbo, rows)

def get_animals_ids_brief(dbo: Database, sort: str, q: str, limit: int = 5, cachetime: int = 60) -> Results:
    """
    Given a recordset of animal IDs, goes and gets the brief animal records (eg: for shelterview or animal links).
    The idea is that we write the simplest possible animal queries to get the
    ID before feeding the list of IDs into the full animal_query. This performs
    a lot better than doing the full SELECT with ORDER BY/LIMIT
    """
    aids = []
    for aid in dbo.query(q, limit=limit):
        aids.append(aid["ID"])
    if len(aids) == 0: return [] # Return empty recordset if no results
    rows = dbo.query_cache(get_animal_brief_query(dbo) + " WHERE a.ID IN (%s) ORDER BY %s" % (dbo.sql_placeholders(aids), sort), aids, age=cachetime, distincton="ID")
    return calc_ages(dbo, rows)

def get_animals_brief(animals: Results) -> Results:
    """
    For any method that returns a list of animals from the get_animal_query 
    selector, this will strip them down and return shorter records for passing
    as json to things like search, shelterview and animal links on the homepage.
    There is a get_animal_brief_query that is quicker and better for large datasets.
    """
    r = []
    for a in animals:
        r.append({ 
            "ACCEPTANCENUMBER": a["ACCEPTANCENUMBER"],
            "ACTIVEMOVEMENTID": a["ACTIVEMOVEMENTID"],
            "ACTIVEMOVEMENTTYPE": a["ACTIVEMOVEMENTTYPE"],
            "ACTIVERESERVATIONS": a["ACTIVERESERVATIONS"],
            "ADDITIONALFLAGS": a["ADDITIONALFLAGS"],
            "ADOPTIONCOORDINATORID": a["ADOPTIONCOORDINATORID"],
            "ADOPTIONCOORDINATORNAME": a["ADOPTIONCOORDINATORNAME"],
            "AGEGROUP": a["AGEGROUP"],
            "ANIMALCOMMENTS": a["ANIMALCOMMENTS"],
            "ANIMALAGE": a["ANIMALAGE"],
            "ANIMALNAME" : a["ANIMALNAME"],
            "ANIMALTYPENAME" : a["ANIMALTYPENAME"],
            "ARCHIVED" : a["ARCHIVED"],
            "BASECOLOURNAME": a["BASECOLOURNAME"],
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
            "DISPLAYLOCATION": a["DISPLAYLOCATION"],
            "DISPLAYLOCATIONNAME": a["DISPLAYLOCATIONNAME"],
            "ENTRYREASONNAME": a["ENTRYREASONNAME"],
            "ENTRYTYPENAME": a["ENTRYTYPENAME"],
            "FLVRESULT": a["FLVRESULT"],
            "HASACTIVEBOARDING": a["HASACTIVEBOARDING"],
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
            "IDENTICHIPNUMBER": a["IDENTICHIPNUMBER"],
            "ISCOURTESY": a["ISCOURTESY"],
            "ISGOODWITHCATS": a["ISGOODWITHCATS"],
            "ISGOODWITHCHILDREN": a["ISGOODWITHCHILDREN"],
            "ISGOODWITHDOGS": a["ISGOODWITHDOGS"],
            "ISHOUSETRAINED": a["ISHOUSETRAINED"],
            "ISHOLD": a["ISHOLD"],
            "ISNOTAVAILABLEFORADOPTION": a["ISNOTAVAILABLEFORADOPTION"],
            "ISPICKUP": a["ISPICKUP"], 
            "ISQUARANTINE": a["ISQUARANTINE"],
            "JURISDICTIONNAME": a["JURISDICTIONNAME"],
            "LASTCHANGEDDATE": a["LASTCHANGEDDATE"],
            "LASTCHANGEDBY": a["LASTCHANGEDBY"],
            "MARKINGS": a["MARKINGS"],
            "MOSTRECENTENTRYDATE" : a["MOSTRECENTENTRYDATE"],
            "NEUTERED" : a["NEUTERED"],
            "NONSHELTERANIMAL": a["NONSHELTERANIMAL"],
            "ORIGINALOWNERID": a["ORIGINALOWNERID"],
            "ORIGINALOWNERNAME": a["ORIGINALOWNERNAME"],
            "OWNERID": a["OWNERID"],
            "OWNERNAME": a["OWNERNAME"],
            "PICKUPLOCATIONNAME": a["PICKUPLOCATIONNAME"],
            "POPUPWARNING": a["POPUPWARNING"],
            "RABIESTAG": a["RABIESTAG"],
            "SEX" : a["SEX"],
            "SEXNAME" : a["SEXNAME"],
            "SHELTERCODE" : a["SHELTERCODE"],
            "SHELTERLOCATION": a["SHELTERLOCATION"],
            "SHELTERLOCATIONNAME": a["SHELTERLOCATIONNAME"],
            "SHELTERLOCATIONUNIT": a["SHELTERLOCATIONUNIT"],
            "SHORTCODE": a["SHORTCODE"],
            "SITENAME": a["SITENAME"],
            "SPECIESID": a["SPECIESID"],
            "SPECIESNAME": a["SPECIESNAME"],
            "VACCGIVENCOUNT": a["VACCGIVENCOUNT"],
            "WEBSITEMEDIANAME": a["WEBSITEMEDIANAME"],
            "WEBSITEMEDIADATE": a["WEBSITEMEDIADATE"],
            "WEBSITEMEDIANOTES": a["WEBSITEMEDIANOTES"] 
        })
    return r

def get_animal_find_simple(dbo: Database, query: str, classfilter: str = "all", limit: int = 0, lf: LocationFilter = None, brief: bool = False) -> Results:
    """
    Returns rows for simple animal searches.
    query: The search criteria
    classfilter: all, shelter, female
    locationfilter: IN clause of locations to search
    """
    # If no query has been given and we have a filter of shelter or all, 
    # do an on-shelter search instead
    if query == "" and (classfilter == "all" or classfilter == "shelter"):
        locationfilter = ""
        if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
        sql = brief and get_animal_brief_query(dbo) or get_animal_query(dbo)
        sql = f"{sql} WHERE a.Archived=0 {locationfilter} ORDER BY a.AnimalName"
        return calc_ages(dbo, dbo.query(sql, limit=limit, distincton="ID"))
    ss = asm3.utils.SimpleSearchBuilder(dbo, query)
    ss.add_fields([ "a.AnimalName", "a.ShelterCode", "a.ShortCode", "a.AcceptanceNumber", "a.BreedName",
        "a.IdentichipNumber", "a.Identichip2Number", "a.TattooNumber", "a.RabiesTag", "il.LocationName", 
        "a.ShelterLocationUnit", "a.PickupAddress" ])
    ss.add_clause("EXISTS(SELECT ad.Value FROM additional ad " \
        "INNER JOIN additionalfield af ON af.ID = ad.AdditionalFieldID AND af.Searchable = 1 " \
        "WHERE ad.LinkID=a.ID AND ad.LinkType IN (%s) AND LOWER(ad.Value) LIKE ?)" % asm3.additional.ANIMAL_IN)
    ss.add_large_text_fields([ "a.Markings", "a.HiddenAnimalDetails", "a.AnimalComments", "a.ReasonNO", 
        "a.HealthProblems", "a.PTSReason" ])
    if asm3.utils.is_numeric(query) and len(query) > 4:
        ss.add_clause("EXISTS(SELECT ID FROM animalvaccination av WHERE av.AnimalID = a.ID AND av.RabiesTag LIKE ?)")
    if classfilter == "shelter":
        classfilter = "a.Archived = 0 AND "
    elif classfilter == "female":
        classfilter = "a.Sex = 0 AND "
    else:
        classfilter = ""
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andsuffix=True)
    # run the query to retrieve the list of rows with matching IDs
    ors = " OR ".join(ss.ors)
    idsql = 'SELECT DISTINCT a.ID FROM animal a LEFT OUTER JOIN internallocation il ON il.ID = ShelterLocation WHERE ' \
        f"{classfilter} {locationfilter} ({ors})"
    idrows = dbo.query_list(idsql, ss.values, limit=limit)
    idrows = [ "0" ] + dbo.query_list(idsql, ss.values, limit=limit)
    idin = ",".join([ str(x) for x in idrows ])
    # then get them
    sql = brief and get_animal_brief_query(dbo) or get_animal_query(dbo)
    sql = f"{sql} WHERE a.ID IN ({idin}) ORDER BY a.Archived, a.AnimalName" 
    rows = dbo.query(sql, limit=limit, distincton="ID")
    rows = calc_ages(dbo, rows)
    return rows

def get_animal_find_advanced(dbo: Database, criteria: dict, limit: int = 0, lf: LocationFilter = None) -> Results:
    """
    Returns rows for advanced animal searches.
    criteria: A dictionary of criteria
       animalname - string partial pattern
       sheltercode - string partial pattern
       createdby - string partial pattern
       litterid - string partial pattern
       animaltypeid - -1 for all or ID
       breedid - -1 for all or ID
       diet - -1 for all or diet ID
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
       tattoo - string partial pattern
       insuranceno - string partial pattern
       rabiestag - string partial pattern
       entryreason - -1 for all entry reasons or ID
       entrytype - -1 for all entry types or ID
       pickuplocation - -1 for all pickup locations or ID
       pickupaddress - string partial pattern
       jurisdiction - -1 for all jurisdictions or ID
       hiddencomments - partial word/string pattern
       reasonforentry - partial word/string pattern
       originalowner - string partial pattern
       medianotes - partial word/string pattern
       filter - one or more of:
           showtransfersonly
           showpickupsonly
           showspecialneedsonly
           showdeclawedonly
           goodwithchildren
           goodwithcats
           goodwithdogs
           housetrained
           fivplus
           flvplus
           heartwormplus
           heartwormneg
           includedeceased
           includenonshelter
           unaltered
        flag - one or more of (plus custom):
            courtesy
            crueltycase
            nonshelter
            notforadoption
            notforregistration
            quarantine
        af_X - additional field with ID X
    """
    post = asm3.utils.PostedData(criteria, dbo.locale)
    ss = asm3.utils.AdvancedSearchBuilder(dbo, post)
    ss.add_str("animalname", "a.AnimalName")
    ss.add_id("animaltypeid", "a.AnimalTypeID")
    ss.add_id("speciesid", "a.SpeciesID")
    ss.add_id_pair("breedid", "a.BreedID", "a.Breed2ID")
    ss.add_id("shelterlocation", "a.ShelterLocation")
    # If we have a location filter and no location has been given, use the filter
    if lf is not None and lf.locationfilter != "" and post.integer("shelterlocation") == -1:
        ss.ands.append(lf.clause(tablequalifier="a"))
    ss.add_str_pair("microchip", "a.IdentichipNumber", "a.Identichip2Number")
    ss.add_str("tattoo", "a.TattooNumber")
    ss.add_str("pickupaddress", "a.PickupAddress")
    ss.add_id("sex", "a.Sex")
    ss.add_id("size", "a.Size")
    ss.add_id("colour", "a.BaseColourID")
    ss.add_id("entryreason", "a.EntryReasonID")
    ss.add_id("entrytype", "a.EntryTypeID")
    ss.add_id("pickuplocation", "a.PickupLocationID")
    ss.add_id("jurisdiction", "a.JurisdictionID")
    ss.add_str("litterid", "a.AcceptanceNumber")
    ss.add_date_pair("inbetweenfrom", "inbetweento", "a.DateBroughtIn", "a.MostRecentEntryDate")
    ss.add_filter("goodwithchildren", "a.IsGoodWithChildren = 0")
    ss.add_filter("goodwithdogs", "a.IsGoodWithDogs = 0")
    ss.add_filter("goodwithcats", "a.IsGoodWithCats = 0")
    ss.add_filter("housetrained", "a.IsHouseTrained = 0")
    ss.add_filter("showtransfersonly", "a.IsTransfer = 1")
    ss.add_filter("showpickupsonly", "a.IsPickup = 1")
    ss.add_filter("showspecialneedsonly", "a.HasSpecialNeeds = 1")
    ss.add_filter("showdeclawedonly", "a.Declawed = 1")
    ss.add_filter("fivplus", "a.CombiTested = 1 AND a.CombiTestResult = 2")
    ss.add_filter("flvplus", "a.CombiTested = 1 AND a.FLVResult = 2")
    ss.add_filter("heartwormplus", "a.HeartwormTested = 1 AND a.HeartwormTestResult = 2")
    ss.add_filter("heartwormneg", "a.HeartwormTested = 1 AND a.HeartwormTestResult = 1")
    ss.add_filter("unaltered", "a.Neutered = 0")
    ss.add_words("comments", "a.AnimalComments")
    ss.add_words("hiddencomments", "a.HiddenAnimalDetails")
    ss.add_words("features", "a.Markings")
    ss.add_words("reasonforentry", "a.ReasonForEntry")
    if post.integer("agegroup") != -1:
        ss.add_str("agegroup", "a.AgeGroup")
    ss.add_date("outbetweenfrom", "outbetweento", "a.ActiveMovementDate")
    ss.add_str("createdby", "a.CreatedBy")

    if post["rabiestag"] != "":
        ilike = dbo.sql_ilike("a.RabiesTag", "?")
        ilike2 = dbo.sql_ilike("animalvaccination.RabiesTag", "?")
        ss.ands.append(f"({ilike} OR EXISTS (SELECT ID FROM animalvaccination WHERE {ilike2} AND AnimalID = a.ID))")
        ss.values.append("%%%s%%" % post["rabiestag"].lower( ))
        ss.values.append("%%%s%%" % post["rabiestag"].lower( ))

    if post["agedbetweenfrom"] != "" and post["agedbetweento"] != "":
        ss.ands.append("a.DateOfBirth >= ? AND a.DateOfBirth <= ?")
        ss.values.append(subtract_years(dbo.now(), post.floating("agedbetweento")))
        ss.values.append(subtract_years(dbo.now(), post.floating("agedbetweenfrom")))

    if post["diet"] != "-1" and post["diet"] != "":
        dietid = post["diet"]
        ss.ands.append(f"EXISTS (SELECT ID FROM animaldiet WHERE DietID={dietid} AND AnimalID = a.ID)")

    if post["sheltercode"] != "":
        ilike1 = dbo.sql_ilike("a.ShelterCode", "?")
        ilike2 = dbo.sql_ilike("ShelterCode", "?")
        ss.ands.append(f"({ilike1} OR EXISTS (SELECT ShelterCode FROM animalentry WHERE {ilike2} AND AnimalID = a.ID))")
        ss.values.append("%%%s%%" % post["sheltercode"].lower() )
        ss.values.append("%%%s%%" % post["sheltercode"].lower() )

    if post["insuranceno"] != "":
        ilike = dbo.sql_ilike("InsuranceNumber", "?")
        ss.ands.append(f"EXISTS (SELECT InsuranceNumber FROM adoption WHERE {ilike} AND AnimalID = a.ID)")
        ss.values.append( "%%%s%%" % post["insuranceno"].lower() )

    if post["medianotes"] != "":
        ilike = dbo.sql_ilike("MediaNotes", "?")
        ss.ands.append(f"EXISTS (SELECT ID FROM media WHERE {ilike} AND LinkID = a.ID AND LinkTypeID = 0)")
        ss.values.append( "%%%s%%" % post["medianotes"].lower() )

    if post["originalowner"] != "":
        ilike = dbo.sql_ilike("OwnerName", "?")
        ss.ands.append(f"EXISTS (SELECT ID FROM owner WHERE {ilike} AND ID = a.OriginalOwnerID)")
        ss.values.append( "%%%s%%" % post["originalowner"].lower() )

    if post["adoptionno"] != "":
        ilike = dbo.sql_ilike("AdoptionNumber", "?")
        ss.ands.append(f"EXISTS (SELECT AdoptionNumber FROM adoption WHERE {ilike} AND AnimalID = a.ID)")
        ss.values.append( "%%%s%%" % post["adoptionno"].lower() )

    if post["filter"].find("includedeceased") == -1 and post["logicallocation"] != "deceased":
        ss.ands.append("a.DeceasedDate Is Null")

    if post["filter"].find("includenonshelter") == -1 and post["flags"].find("nonshelter") == -1:
        ss.ands.append("a.NonShelterAnimal = 0")

    ss.add_comp("reserved", "reserved", "a.HasActiveReserve = 1")
    ss.add_comp("reserved", "unreserved", "a.HasActiveReserve = 0")
    ss.add_comp("logicallocation", "onshelter", "a.Archived = 0")
    ss.add_comp("logicallocation", "adoptable", "a.Archived = 0 AND a.IsNotAvailableForAdoption = 0 AND " \
        "a.HasTrialAdoption = 0 AND a.IsHold = 0 AND a.IsQuarantine = 0 AND a.CrueltyCase = 0")
    ss.add_comp("logicallocation", "reserved", "a.Archived = 0 AND a.HasActiveReserve = 1 AND a.HasTrialAdoption = 0")
    ss.add_comp("logicallocation", "hold", "a.IsHold = 1 AND a.Archived = 0")
    ss.add_comp("logicallocation", "fostered", "a.ActiveMovementType = %d" % asm3.movement.FOSTER)
    ss.add_comp("logicallocation", "permanentfoster", "a.ActiveMovementType = %d AND a.HasPermanentFoster = 1" % asm3.movement.FOSTER)
    ss.add_comp("logicallocation", "adopted", "a.ActiveMovementType = %d" % asm3.movement.ADOPTION)
    ss.add_comp("logicallocation", "transferred", "a.ActiveMovementType = %d" % asm3.movement.TRANSFER)
    ss.add_comp("logicallocation", "escaped", "a.ActiveMovementType = %d" % asm3.movement.ESCAPED)
    ss.add_comp("logicallocation", "stolen", "a.ActiveMovementType = %d" % asm3.movement.STOLEN)
    ss.add_comp("logicallocation", "releasedtowild", "a.ActiveMovementType = %d" % asm3.movement.RELEASED)
    ss.add_comp("logicallocation", "reclaimed", "a.ActiveMovementType = %d" % asm3.movement.RECLAIMED)
    ss.add_comp("logicallocation", "retailer", "a.ActiveMovementType = %d" % asm3.movement.RETAILER)
    ss.add_comp("logicallocation", "deceased", "a.DeceasedDate Is Not Null")

    if post["flags"] != "":
        for flag in post["flags"].split(","):
            if flag == "courtesy": ss.ands.append("a.IsCourtesy=1")
            elif flag == "crueltycase": ss.ands.append("a.CrueltyCase=1")
            elif flag == "nonshelter": ss.ands.append("a.NonShelterAnimal=1")
            elif flag == "notforadoption": ss.ands.append("a.IsNotAvailableForAdoption=1")
            elif flag == "notforregistration": ss.ands.append("a.IsNotForRegistration=1")
            elif flag == "quarantine": ss.ands.append("a.IsQuarantine=1")
            else: 
                ss.ands.append("LOWER(a.AdditionalFlags) LIKE ?")
                ss.values.append("%%%s|%%" % flag.lower())

    for k, v in post.data.items():
        if k.startswith("af_") and v != "":
            afid = asm3.utils.atoi(k)
            ilike = dbo.sql_ilike("Value", "?")
            ss.ands.append(f"EXISTS (SELECT Value FROM additional WHERE LinkID=a.ID AND AdditionalFieldID={afid} AND {ilike})")
            ss.values.append( "%%%s%%" % v.strip().lower() )

    where = ""
    if len(ss.ands) > 0: where = "WHERE " + " AND ".join(ss.ands)
    # run the query to retrieve the list of rows with matching IDs
    idsql = f"SELECT DISTINCT a.ID FROM animal a LEFT OUTER JOIN internallocation il ON il.ID = ShelterLocation {where}"
    idrows = [ "0" ] + dbo.query_list(idsql, ss.values, limit=limit)
    idin = ",".join([ str(x) for x in idrows ])
    # then get them
    sql = f"{get_animal_query(dbo)} WHERE a.ID IN ({idin}) ORDER BY a.Archived, a.AnimalName" 
    rows = dbo.query(sql, limit=limit, distincton="ID")
    rows = calc_ages(dbo, rows)
    return rows

def get_animals_adoptable(dbo: Database) -> Results:
    """
    Returns all adoptable animals
    """
    query = get_animal_brief_query(dbo)
    sql = f"{query} WHERE a.Adoptable=1 ORDER BY AnimalName"
    return dbo.query(sql)

def get_animals_never_vacc(dbo: Database, lf: LocationFilter = None) -> Results:
    """
    Returns all shelter animals who have never received a vacc of any type
    """
    query = get_animal_brief_query(dbo)
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    speciesin = asm3.configuration.alert_species_never_vacc(dbo)
    sql = f"{query} WHERE a.Archived=0 {locationfilter} " \
        f"AND a.SpeciesID IN ({speciesin})" \
        "AND NOT EXISTS(SELECT ID FROM animalvaccination WHERE AnimalID=a.ID AND DateOfVaccination Is Not Null)"
    return dbo.query(sql)

def get_animals_no_rabies(dbo: Database, lf: LocationFilter = None) -> Results:
    """
    Returns all shelter animals who have no rabies tag
    """
    query = get_animal_brief_query(dbo)
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    speciesin = asm3.configuration.alert_species_rabies(dbo)
    sql = f"{query} WHERE a.RabiesTag = '' AND a.Archived=0 {locationfilter} AND a.SpeciesID IN ({speciesin})"
    return dbo.query(sql)

def get_animals_not_for_adoption(dbo: Database, lf: LocationFilter = None) -> Results:
    """
    Returns all shelter animals who have the not for adoption flag set
    """
    query = get_animal_brief_query(dbo)
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    sql = f"{query} WHERE a.IsNotAvailableForAdoption = 1 AND a.Archived=0 {locationfilter}"
    return dbo.query(sql)

def get_animals_not_microchipped(dbo: Database, lf: LocationFilter = None) -> Results:
    """
    Returns all shelter animals who have not been microchipped
    """
    query = get_animal_brief_query(dbo)
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    speciesin = asm3.configuration.alert_species_microchip(dbo)
    sql = f"{query} WHERE a.Identichipped=0 AND a.Archived=0 {locationfilter} AND a.SpeciesID IN ({speciesin})"
    return dbo.query(sql)

def get_animals_hold(dbo: Database, lf: LocationFilter = None) -> Results:
    """
    Returns all shelter animals who have the hold flag set
    """
    query = get_animal_query(dbo)
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    sql = f"{query} WHERE a.IsHold=1 AND a.Archived=0 {locationfilter} ORDER BY DateBroughtIn"
    return dbo.query(sql)

def get_animals_hold_today(dbo: Database, lf: LocationFilter = None) -> Results:
    """
    Returns all shelter animals who have the hold flag set and the hold ends tomorrow (ie. this is the last day of hold)
    """
    query = get_animal_brief_query(dbo)
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    sql = f"{query} WHERE a.IsHold=1 AND a.HoldUntilDate=? AND a.Archived=0 {locationfilter}"
    return dbo.query(sql, [dbo.today(offset=1)], distincton="ID")

def get_animals_long_term(dbo: Database, lf: LocationFilter = None) -> Results:
    """
    Returns all shelter animals who have been on the shelter for 6 months or more
    """
    query = get_animal_brief_query(dbo)
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    sql = f"{query} WHERE a.DaysOnShelter>? AND a.Archived = 0 {locationfilter}"
    return dbo.query(sql, [asm3.configuration.long_term_days(dbo)])

def get_animals_owned_by(dbo: Database, personid: int) -> Results:
    """
    Returns all animals who are owned by personid
    1. Animals that have an open adoption, foster, transter, reclaim or retailer movement to this person (nonshelter=0)
    2. Animals where originalownerid = personid (nonshelter=1)
    """
    sa = dbo.query(get_animal_brief_query(dbo) + " WHERE a.NonShelterAnimal = 0 AND a.ActiveMovementType IN (1,2,3,5,8) AND a.DeceasedDate Is Null " \
        "AND EXISTS(SELECT ID FROM adoption WHERE AnimalID = a.ID AND OwnerID = ? AND MovementType IN (1,2,3,5,8) AND ReturnDate Is Null)", [personid])
    nsa = dbo.query(get_animal_brief_query(dbo) + " WHERE a.NonShelterAnimal = 1 AND a.DeceasedDate Is Null AND a.OriginalOwnerID = ?", [personid])
    return sa + nsa

def get_animals_quarantine(dbo: Database, lf: LocationFilter = None) -> Results:
    """
    Returns all shelter animals who have the quarantine flag set
    """
    query = get_animal_brief_query(dbo)
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    sql = f"{query} WHERE a.IsQuarantine=1 AND a.Archived=0 {locationfilter}"
    return dbo.query(sql)

def get_animals_recently_adopted(dbo: Database, lf: LocationFilter = None) -> Results:
    """
    Returns all recently adopted animals
    """
    query = get_animal_brief_query(dbo)
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    sql = f"{query} WHERE a.ActiveMovementType=1 AND a.NonShelterAnimal=0 AND a.ActiveMovementDate>? {locationfilter}"
    return dbo.query(sql, [dbo.today(offset=-30)])

def get_animals_recently_deceased(dbo: Database, lf: LocationFilter = None) -> Results:
    """
    Returns all shelter animals who are recently deceased
    """
    query = get_animal_brief_query(dbo)
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    sql = f"{query} WHERE a.DeceasedDate Is Not Null AND a.NonShelterAnimal=0 AND a.DiedOffShelter=0 AND a.DeceasedDate>? {locationfilter}"
    return dbo.query(sql, [dbo.today(offset=-30)])

def get_animals_recently_entered(dbo: Database, lf: LocationFilter = None) -> Results:
    """
    Returns all recently entered animals
    """
    query = get_animal_brief_query(dbo)
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    sql = f"{query} WHERE a.NonShelterAnimal=0 AND a.MostRecentEntryDate>? {locationfilter}"
    return dbo.query(sql, [dbo.today(offset=-30)])

def get_animals_stray(dbo: Database, lf: LocationFilter = None) -> Results:
    """
    Returns all shelter animals who are strays
    """
    query = get_animal_query(dbo)
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    sql = f"{query} WHERE a.EntryTypeID=2 AND a.Archived=0 {locationfilter} ORDER BY DateBroughtIn"
    return dbo.query(sql)

def get_alerts(dbo: Database, lf: LocationFilter = None, age: int = 120) -> Results:
    """
    Returns the alert totals for the main screen.
    """
    futuremonth = dbo.sql_date(dbo.today(offset=31))
    oneyear = dbo.sql_date(dbo.today(offset=-365))
    onemonth = dbo.sql_date(dbo.today(offset=-31))
    oneweek = dbo.sql_date(dbo.today(offset=-7))
    today = dbo.sql_date(dbo.today())
    tomorrow = dbo.sql_date(dbo.today(offset=1))
    endoftoday = dbo.sql_date(dbo.today(settime="23:59:59"))
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(andprefix=True)
    shelterfilter = ""
    longterm = asm3.configuration.long_term_days(dbo)
    alertchip = asm3.configuration.alert_species_microchip(dbo)
    alertneuter = asm3.configuration.alert_species_neuter(dbo)
    alertnevervacc = asm3.configuration.alert_species_never_vacc(dbo)
    alertrabies = asm3.configuration.alert_species_rabies(dbo)
    if not asm3.configuration.include_off_shelter_medical(dbo):
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
        "(SELECT COUNT(*) FROM animal LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation " \
            "WHERE Archived=0 %(locfilter)s AND SpeciesID IN ( %(alertnevervacc)s ) AND " \
            "NOT EXISTS(SELECT ID FROM animalvaccination WHERE AnimalID=animal.ID AND DateOfVaccination Is Not Null)) AS nevervacc," \
        "(SELECT COUNT(*) FROM animaltest INNER JOIN animal ON animal.ID = animaltest.AnimalID " \
            "LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation WHERE " \
            "DateOfTest Is Null AND DeceasedDate Is Null %(shelterfilter)s AND " \
            "DateRequired >= %(oneyear)s AND DateRequired <= %(today)s %(locfilter)s) AS duetest," \
        "(SELECT COUNT(*) FROM animalmedicaltreatment INNER JOIN animal ON animal.ID = animalmedicaltreatment.AnimalID " \
            "INNER JOIN animalmedical ON animalmedicaltreatment.AnimalMedicalID = animalmedical.ID " \
            "LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation WHERE " \
            "DateGiven Is Null AND DeceasedDate Is Null %(shelterfilter)s AND " \
            "Status = 0 AND DateRequired  >= %(oneyear)s AND DateRequired <= %(today)s %(locfilter)s) AS duemed," \
        "(SELECT COUNT(*) FROM animalboarding WHERE InDateTime >= %(today)s AND InDateTime < %(tomorrow)s) AS boardintoday, " \
        "(SELECT COUNT(*) FROM animalboarding WHERE OutDateTime >= %(today)s AND OutDateTime < %(tomorrow)s) AS boardouttoday, " \
        "(SELECT COUNT(*) FROM clinicappointment WHERE DateTime >= %(today)s AND DateTime < %(tomorrow)s) AS dueclinic," \
        "(SELECT COUNT(*) FROM animalwaitinglist INNER JOIN owner ON owner.ID = animalwaitinglist.OwnerID " \
            "WHERE Urgency = 1 AND DateRemovedFromList Is Null) AS urgentwl," \
        "(SELECT COUNT(*) FROM adoption INNER JOIN owner ON owner.ID = adoption.OwnerID WHERE " \
            "MovementType = 0 AND ReservationDate Is Not Null AND ReservationCancelledDate Is Null AND IDCheck = 0) AS rsvhck," \
        "(SELECT COUNT(DISTINCT OwnerID) FROM ownerdonation WHERE DateDue <= %(today)s AND Date Is Null) AS duedon," \
        "(SELECT COUNT(*) FROM adoption INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "DeceasedDate Is Null AND IsTrial = 1 AND ReturnDate Is Null AND MovementType = 1 AND TrialEndDate <= %(today)s) AS endtrial," \
        "(SELECT COUNT(*) FROM log WHERE LinkType IN (0,1) AND Date >= %(onemonth)s AND Comments LIKE 'ES01%%') - " \
        "(SELECT COUNT(*) FROM log WHERE LinkType IN (0,1) AND Date >= %(onemonth)s AND Comments LIKE 'ES02%%') AS docunsigned, " \
        "(SELECT COUNT(*) FROM log WHERE LinkType IN (0,1) AND Date >= %(oneweek)s AND Comments LIKE 'ES02%%') AS docsigned, " \
        "(SELECT COUNT(*) FROM log WHERE LinkType IN (0,1) AND Date >= %(oneweek)s AND Comments LIKE 'AC01%%') - " \
        "(SELECT COUNT(*) FROM log WHERE LinkType IN (0,1) AND Date >= %(oneweek)s AND Comments LIKE 'AC02%%') AS opencheckout, " \
        "(SELECT COUNT(*) FROM adoption INNER JOIN animal ON adoption.AnimalID = animal.ID WHERE " \
            "Archived = 0 AND DeceasedDate Is Null AND ReservationDate Is Not Null AND ReservationDate <= %(oneweek)s " \
            "AND ReservationCancelledDate Is Null AND MovementType = 0 AND MovementDate Is Null) AS longrsv," \
        "(SELECT COUNT(*) FROM animal LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation " \
            "WHERE Neutered = 0 AND ActiveMovementType = 1 AND " \
            "ActiveMovementDate > %(onemonth)s %(locfilter)s AND SpeciesID IN ( %(alertneuter)s ) ) AS notneu," \
        "(SELECT COUNT(*) FROM animal LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation " \
            "WHERE Archived = 0 %(locfilter)s AND RabiesTag = '' AND SpeciesID IN ( %(alertrabies)s ) ) AS notrab," \
        "(SELECT COUNT(*) FROM animal LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation " \
            "WHERE Identichipped = 0 AND Archived = 0 %(locfilter)s AND SpeciesID IN ( %(alertchip)s ) ) AS notchip, " \
        "(SELECT COUNT(*) FROM animal LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation " \
            "WHERE Archived = 0 AND IsNotAvailableForAdoption = 1 %(locfilter)s) AS notadopt, " \
        "(SELECT COUNT(*) FROM animal LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation " \
            "WHERE Archived = 0 %(locfilter)s AND IsHold = 1 AND HoldUntilDate = %(tomorrow)s) AS holdtoday, " \
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
        "(SELECT COUNT(*) FROM stocklevel WHERE Balance < Low) AS stlowbal, " \
        "(SELECT COUNT(*) FROM product WHERE (SELECT SUM(stocklevel.Balance) FROM stocklevel WHERE stocklevel.ProductID = product.ID) <= product.GlobalMinimum) AS globallows, " \
        "(SELECT COUNT(*) FROM animaltransport WHERE (DriverOwnerID = 0 OR DriverOwnerID Is Null) AND Status < 10) AS trnodrv, " \
        "(SELECT COUNT(*) FROM animal LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation " \
            "WHERE Archived = 0 AND HasPermanentFoster = 0 AND DaysOnShelter > %(longterm)s %(locfilter)s) AS lngterm, " \
        "(SELECT COUNT(*) FROM publishlog WHERE Alerts > 0 AND PublishDateTime >= %(today)s) AS publish " \
        "FROM lksmovementtype WHERE ID=1" \
            % { "today": today, "endoftoday": endoftoday, "tomorrow": tomorrow, 
                "oneweek": oneweek, "oneyear": oneyear, "onemonth": onemonth, 
                "futuremonth": futuremonth, "locfilter": locationfilter, "shelterfilter": shelterfilter, 
                "alertchip": alertchip, "longterm": longterm, "alertneuter": alertneuter, 
                "alertnevervacc": alertnevervacc, "alertrabies": alertrabies }
    return dbo.query_cache(sql, age=age)

def get_overview(dbo: Database, age: int = 120) -> Results:
    """
    Returns the overview figures for the main screen.
    """
    sql = "SELECT " \
        "(SELECT COUNT(*) FROM animal WHERE Archived=0 AND (ActiveMovementType Is Null OR ActiveMovementType = 0)) AS OnShelter, " \
        "(SELECT COUNT(*) FROM animal WHERE ActiveMovementType=2 AND DeceasedDate Is Null) AS OnFoster, " \
        "(SELECT COUNT(*) FROM animal WHERE Archived=0 AND IsHold=1) AS OnHold, " \
        "(SELECT COUNT(*) FROM animal WHERE Archived=0 AND HasActiveReserve=1) AS Reserved, " \
        "(SELECT COUNT(*) FROM animal WHERE ActiveMovementType=8 AND DeceasedDate Is Null) AS Retailer, " \
        "(SELECT COUNT(*) FROM animal WHERE Archived=0 AND HasTrialAdoption=1) AS TrialAdoption, " \
        "(SELECT COUNT(*) FROM animal WHERE Archived=0 AND Adoptable=1) AS Adoptable " \
        "FROM lksmovementtype WHERE ID=1"
    return dbo.first_row(dbo.query_cache(sql, age=age))

def get_stats(dbo: Database, age: int = 120) -> Results:
    """
    Returns the stats figures for the main screen.
    """
    statperiod = asm3.configuration.show_stats_home_page(dbo)
    statdate = dbo.today() # defaulting to today
    if statperiod == "thisweek": statdate = monday_of_week(statdate)
    if statperiod == "thismonth": statdate = first_of_month(statdate)
    if statperiod == "thisyear": statdate = first_of_year(statdate)
    if statperiod == "alltime": statdate = datetime(1900, 1, 1)
    return dbo.query_named_params("SELECT " \
        "(SELECT COUNT(*) FROM animal WHERE NonShelterAnimal = 0 AND MostRecentEntryDate >= :from) AS Entered," \
        "(SELECT COUNT(*) FROM adoption WHERE MovementDate >= :from AND MovementType = 1) AS Adopted," \
        "(SELECT COUNT(*) FROM adoption WHERE MovementDate >= :from AND MovementType = 5) AS Reclaimed, " \
        "(SELECT COUNT(*) FROM adoption WHERE MovementDate >= :from AND MovementType = 3) AS Transferred, " \
        "(SELECT COUNT(*) FROM adoption WHERE MovementDate >= :from AND MovementType IN (1,3,5,7)) AS LiveRelease, " \
        "(SELECT COUNT(*) FROM adoption WHERE MovementDate >= :from AND MovementType IN (4,6)) AS LostStolen, " \
        "(SELECT COUNT(*) FROM adoption INNER JOIN animal ON animal.ID=adoption.AnimalID WHERE SpeciesID NOT IN (1,2) AND MovementDate >= :from AND MovementType = 7) AS Released, " \
        "(SELECT COUNT(*) FROM adoption INNER JOIN animal ON animal.ID=adoption.AnimalID WHERE SpeciesID IN (1,2) AND MovementDate >= :from AND MovementType = 7) AS TNR, " \
        "(SELECT COUNT(*) FROM animal WHERE NonShelterAnimal = 0 AND DiedOffShelter = 0 AND DeceasedDate >= :from AND PutToSleep = 1) AS PTS, " \
        "(SELECT COUNT(*) FROM animal WHERE NonShelterAnimal = 0 AND DiedOffShelter = 0 AND DeceasedDate >= :from AND PutToSleep = 0 AND IsDOA = 0) AS Died, " \
        "(SELECT COUNT(*) FROM animal WHERE NonShelterAnimal = 0 AND DiedOffShelter = 0 AND DeceasedDate >= :from AND PutToSleep = 0 AND IsDOA = 1) AS DOA, " \
        "(SELECT COUNT(*) FROM animal WHERE NonShelterAnimal = 0 AND IsDOA = 0 AND DateBroughtIn < :from AND " \
            "NOT EXISTS(SELECT MovementDate FROM adoption WHERE MovementDate < :from AND " \
            "(ReturnDate Is Null OR ReturnDate >= :from) AND MovementType NOT IN (2,8) AND AnimalID = animal.ID)) AS BeginCount, " \
        "(SELECT SUM(Donation) - COALESCE(SUM(VATAmount), 0) - COALESCE(SUM(Fee), 0) FROM ownerdonation WHERE Date >= :from) AS Donations, " \
        "(SELECT SUM(CostAmount) FROM animalcost WHERE CostDate >= :from) + " \
            "(SELECT SUM(Cost) FROM animalvaccination WHERE DateOfVaccination >= :from) + " \
            "(SELECT SUM(Cost) FROM animaltest WHERE DateOfTest >= :from) + " \
            "(SELECT SUM(Cost) FROM animalmedical WHERE StartDate >= :from) + " \
            "(SELECT SUM(Cost) FROM animaltransport WHERE PickupDateTime >= :from) AS Costs " \
        "FROM lksmovementtype WHERE ID=1", 
        { "from": statdate },
        age=age)

def embellish_timeline(l: str, rows: Results) -> Results:
    """
    Adds human readable description and icon fields to rows from get_timeline
    """
    td = { "ENTERED": ( _("{0} {1}: entered the shelter", l), "animal" ),
          "MICROCHIP": ( _("{0} {1}: microchipped", l), "microchip" ),
          "NEUTERED": ( _("{0} {1}: altered", l), "unneutered" ),
          "RESERVED": ( _("{0} {1}: reserved by {2}", l), "reservation" ),
          "CANCRESERVE": ( _("{0} {1}: cancelled reservation to {2}", l), "reservation"),
          "TRIALSTART": ( _("{0} {1}: trial adoption to {2}", l), "movement"),
          "TRIALEND": (_("{0} {1}: end of trial adoption to {2}", l), "movement"),
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
          "HOLDON": ( _("{0} {1}: held", l), "hold" ),
          "HOLDOFF": ( _("{0} {1}: hold ended", l), "hold" ),
          "NOTADOPT": ( _("{0} {1}: not available for adoption", l), "notforadoption" ),
          "AVAILABLE": ( _("{0} {1}: available for adoption", l), "notforadoption" ),
          "BOARDIN": ( _("{0} {1}: boarding started ({2})", l), "boarding" ),
          "BOARDOUT": ( _("{0} {1}: boarding ended ({2})", l), "boarding" ),
          "VACC": ( _("{0} {1}: received {2}", l), "vaccination" ),
          "TEST": ( _("{0} {1}: received {2}", l), "test" ),
          "MEDICAL": ( _("{0} {1}: received {2}", l), "medical" ),
          "INCIDENTOPEN": ( _("{0}: opened {1}", l), "call" ),
          "INCIDENTCLOSE": ( _("{0}: closed {1} ({2})", l), "call" ),
          "TRANSPORT": ( _("{0} {1}: transport ({2})", l), "transport" ),
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

def get_timeline(dbo: Database, limit: int = 500, age: int = 120) -> Results:
    """
    Returns a list of recent events at the shelter.
    """
    queries = [
        "SELECT 'animal' AS LinkTarget, 'ENTERED' AS Category, DateBroughtIn AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 " \
            "ORDER BY DateBroughtIn DESC, ID",
        "SELECT 'animal' AS LinkTarget, 'MICROCHIP' AS Category, IdentichipDate AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND IdentichipDate Is Not Null " \
            "ORDER BY IdentichipDate DESC, ID",
        "SELECT 'animal' AS LinkTarget, 'NEUTERED' AS Category, NeuteredDate AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND NeuteredDate Is Not Null " \
            "ORDER BY NeuteredDate DESC, ID",
        "SELECT 'animal_movements' AS LinkTarget, 'RESERVED' AS Category, ReservationDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, owner.OwnerName AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "INNER JOIN owner ON adoption.OwnerID = owner.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Null AND ReservationDate Is Not Null " \
            "ORDER BY ReservationDate DESC, animal.ID",
        "SELECT 'animal_movements' AS LinkTarget, 'CANCRESERVE' AS Category, ReservationCancelledDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, owner.OwnerName AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "INNER JOIN owner ON adoption.OwnerID = owner.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Null AND ReservationDate Is Not Null AND ReservationCancelledDate Is Not Null " \
            "ORDER BY ReservationCancelledDate DESC, animal.ID",
        "SELECT 'animal_movements' AS LinkTarget, 'ADOPTED' AS Category, MovementDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, owner.OwnerName AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "INNER JOIN owner ON adoption.OwnerID = owner.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND MovementType = 1 AND IsTrial = 0 " \
            "ORDER BY MovementDate DESC, animal.ID",
        "SELECT 'animal_movements' AS LinkTarget, 'TRIALSTART' AS Category, MovementDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, owner.OwnerName AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "INNER JOIN owner ON adoption.OwnerID = owner.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND MovementType = 1 AND IsTrial = 1 " \
            "ORDER BY MovementDate DESC, animal.ID",
        "SELECT 'animal_movements' AS LinkTarget, 'TRIALEND' AS Category, TrialEndDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, owner.OwnerName AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "INNER JOIN owner ON adoption.OwnerID = owner.ID " \
            "WHERE NonShelterAnimal = 0 AND TrialEndDate Is Not Null AND MovementType = 1 AND IsTrial = 1 " \
            "ORDER BY MovementDate DESC, animal.ID",
        "SELECT 'animal_movements' AS LinkTarget, 'FOSTERED' AS Category, MovementDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, owner.OwnerName AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "INNER JOIN owner ON adoption.OwnerID = owner.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND MovementType = 2 " \
            "ORDER BY MovementDate DESC, animal.ID",
        "SELECT 'animal_movements' AS LinkTarget, 'TRANSFER' AS Category, MovementDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, owner.OwnerName AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "INNER JOIN owner ON adoption.OwnerID = owner.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND MovementType = 3 " \
            "ORDER BY MovementDate DESC, animal.ID",
        "SELECT 'animal_movements' AS LinkTarget, 'ESCAPED' AS Category, MovementDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND MovementType = 4 " \
            "ORDER BY MovementDate DESC, animal.ID",
        "SELECT 'animal_movements' AS LinkTarget, 'RECLAIMED' AS Category, MovementDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, owner.OwnerName AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "INNER JOIN owner ON adoption.OwnerID = owner.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND MovementType = 5 " \
            "ORDER BY MovementDate DESC, animal.ID",
        "SELECT 'animal_movements' AS LinkTarget, 'STOLEN' AS Category, MovementDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND MovementType = 6 " \
            "ORDER BY MovementDate DESC, animal.ID",
        "SELECT 'animal_movements' AS LinkTarget, 'RELEASED' AS Category, MovementDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND MovementType = 7 " \
            "ORDER BY MovementDate DESC, animal.ID",
        "SELECT 'animal_movements' AS LinkTarget, 'RETAILER' AS Category, MovementDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, owner.OwnerName AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "INNER JOIN owner ON adoption.OwnerID = owner.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND MovementType = 8 " \
            "ORDER BY MovementDate DESC, animal.ID",
        "SELECT 'animal_movements' AS LinkTarget, 'RETURNED' AS Category, ReturnDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, owner.OwnerName AS Text3, adoption.LastChangedBy FROM animal " \
            "INNER JOIN adoption ON adoption.AnimalID = animal.ID " \
            "LEFT OUTER JOIN owner ON adoption.OwnerID = owner.ID " \
            "WHERE NonShelterAnimal = 0 AND MovementDate Is Not Null AND ReturnDate Is Not Null " \
            "ORDER BY ReturnDate DESC, animal.ID",
        "SELECT 'animal' AS LinkTarget, 'DIED' AS Category, DeceasedDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, ReasonName AS Text3, animal.LastChangedBy FROM animal " \
            "INNER JOIN deathreason ON animal.PTSReasonID = deathreason.ID " \
            "WHERE NonShelterAnimal = 0 AND DiedOffShelter = 0 AND PutToSleep = 0 AND DeceasedDate Is Not Null " \
            "ORDER BY DeceasedDate DESC, animal.ID",
        "SELECT 'animal' AS LinkTarget, 'EUTHANISED' AS Category, DeceasedDate AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, ReasonName AS Text3, animal.LastChangedBy FROM animal " \
            "INNER JOIN deathreason ON animal.PTSReasonID = deathreason.ID " \
            "WHERE NonShelterAnimal = 0 AND DiedOffShelter = 0 AND PutToSleep = 1 AND DeceasedDate Is Not Null " \
            "ORDER BY DeceasedDate DESC, animal.ID",
        "SELECT 'animal' AS LinkTarget, 'FIVP' AS Category, CombiTestDate AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND CombiTested = 1 AND CombiTestDate Is Not Null AND CombiTestResult = 2 " \
            "ORDER BY CombiTestDate DESC, ID",
        "SELECT 'animal' AS LinkTarget, 'FLVP' AS Category, CombiTestDate AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND CombiTested = 1 AND CombiTestDate Is Not Null AND FLVResult = 2 " \
            "ORDER BY CombiTestDate DESC, ID",
        "SELECT 'animal' AS LinkTarget, 'HWP' AS Category, CombiTestDate AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND HeartwormTested = 1 AND HeartwormTestDate Is Not Null AND HeartwormTestResult = 2 " \
            "ORDER BY HeartwormTestDate DESC, ID",
        "SELECT 'animal' AS LinkTarget, 'QUARANTINE' AS Category, LastChangedDate AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND IsQuarantine = 1 " \
            "ORDER BY LastChangedDate DESC, ID",
        "SELECT 'animal' AS LinkTarget, 'HOLDON' AS Category, DateBroughtIn AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND IsHold = 1 " \
            "ORDER BY DateBroughtIn DESC, ID",
        "SELECT 'animal' AS LinkTarget, 'HOLDOFF' AS Category, HoldUntilDate AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND HoldUntilDate Is Not Null " \
            "ORDER BY DateBroughtIn DESC, ID",
        "SELECT 'animal' AS LinkTarget, 'NOTADOPT' AS Category, DateBroughtIn AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND IsNotAvailableForAdoption = 1 " \
            "ORDER BY DateBroughtIn DESC, ID",
        "SELECT 'animal' AS LinkTarget, 'AVAILABLE' AS Category, ActiveMovementReturn AS EventDate, ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, '' AS Text3, LastChangedBy FROM animal " \
            "WHERE NonShelterAnimal = 0 AND ActiveMovementReturn Is Not Null AND IsNotAvailableForAdoption = 0 " \
            "ORDER BY ActiveMovementReturn DESC, ID",
        "SELECT 'animal_vaccination' AS LinkTarget, 'VACC' AS Category, DateOfVaccination AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, VaccinationType AS Text3, animalvaccination.LastChangedBy FROM animal " \
            "INNER JOIN animalvaccination ON animalvaccination.AnimalID = animal.ID " \
            "INNER JOIN vaccinationtype ON vaccinationtype.ID = animalvaccination.VaccinationID " \
            "WHERE NonShelterAnimal = 0 AND DateOfVaccination Is Not Null " \
            "ORDER BY DateOfVaccination DESC, animal.ID",
        "SELECT 'animal_test' AS LinkTarget, 'TEST' AS Category, DateOfTest AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, TestName AS Text3, animaltest.LastChangedBy FROM animal " \
            "INNER JOIN animaltest ON animaltest.AnimalID = animal.ID " \
            "INNER JOIN testtype ON testtype.ID = animaltest.TestTypeID " \
            "WHERE NonShelterAnimal = 0 AND DateOfTest Is Not Null " \
            "ORDER BY DateOfTest DESC, animal.ID",
        "SELECT 'animal_medical' AS LinkTarget, 'MEDICAL' AS Category, DateGiven AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, TreatmentName AS Text3, animalmedicaltreatment.LastChangedBy FROM animal " \
            "INNER JOIN animalmedicaltreatment ON animalmedicaltreatment.AnimalID = animal.ID " \
            "INNER JOIN animalmedical ON animalmedicaltreatment.AnimalMedicalID = animalmedical.ID " \
            "WHERE NonShelterAnimal = 0 AND DateGiven Is Not Null " \
            "ORDER BY DateGiven DESC, animal.ID",
        "SELECT 'animal_boarding' AS LinkTarget, 'BOARDIN' AS Category, InDateTime AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, BoardingName AS Text3, animalboarding.LastChangedBy FROM animalboarding " \
            "INNER JOIN lkboardingtype ON lkboardingtype.ID = animalboarding.BoardingTypeID " \
            "INNER JOIN animal ON animalboarding.AnimalID = animal.ID " \
            "ORDER BY InDateTime DESC, animal.ID",
        "SELECT 'animal_boarding' AS LinkTarget, 'BOARDOUT' AS Category, OutDateTime AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, BoardingName AS Text3, animalboarding.LastChangedBy FROM animalboarding " \
            "INNER JOIN lkboardingtype ON lkboardingtype.ID = animalboarding.BoardingTypeID " \
            "INNER JOIN animal ON animalboarding.AnimalID = animal.ID " \
            "ORDER BY OutDateTime DESC, animal.ID",
        "SELECT 'incident' AS LinkTarget, 'INCIDENTOPEN' AS Category, IncidentDateTime AS EventDate, animalcontrol.ID, " \
            "IncidentName AS Text1, DispatchAddress AS Text2, '' AS Text3, LastChangedBy FROM animalcontrol " \
            "INNER JOIN incidenttype ON incidenttype.ID = animalcontrol.IncidentTypeID " \
            "ORDER BY IncidentDateTime DESC, animalcontrol.ID",
        "SELECT 'incident' AS LinkTarget, 'INCIDENTCLOSE' AS Category, CompletedDate AS EventDate, animalcontrol.ID, " \
            "IncidentName AS Text1, DispatchAddress AS Text2, CompletedName AS Text3, LastChangedBy FROM animalcontrol " \
            "INNER JOIN incidenttype ON incidenttype.ID = animalcontrol.IncidentTypeID " \
            "INNER JOIN incidentcompleted ON incidentcompleted.ID = animalcontrol.IncidentCompletedID " \
            "ORDER BY CompletedDate DESC, animalcontrol.ID",
        "SELECT 'animal_transport' AS LinkTarget, 'TRANSPORT' AS Category, PickupDateTime AS EventDate, animal.ID, " \
            "ShelterCode AS Text1, AnimalName AS Text2, TransportTypeName AS Text3, animaltransport.LastChangedBy FROM animaltransport " \
            "INNER JOIN transporttype ON transporttype.ID = animaltransport.TransportTypeID " \
            "INNER JOIN animal ON animaltransport.AnimalID = animal.ID " \
            "ORDER BY PickupDateTime DESC, animal.ID",
        "SELECT 'lostanimal' AS LinkTarget, 'LOST' AS Category, DateLost AS EventDate, animallost.ID, " \
            "DistFeat AS Text1, AreaLost AS Text2, SpeciesName AS Text3, LastChangedBy FROM animallost " \
            "INNER JOIN species ON animallost.AnimalTypeID = species.ID " \
            "ORDER BY DateLost DESC, animallost.ID",
        "SELECT 'foundanimal' AS LinkTarget, 'FOUND' AS Category, DateFound AS EventDate, animalfound.ID, " \
            "DistFeat AS Text1, AreaFound AS Text2, SpeciesName AS Text3, LastChangedBy FROM animalfound " \
            "INNER JOIN species ON animalfound.AnimalTypeID = species.ID " \
            "ORDER BY DateFound DESC, animalfound.ID",
        "SELECT 'waitinglist' AS LinkTarget, 'WAITINGLIST' AS Category, DatePutOnList AS EventDate, animalwaitinglist.ID, " \
            "AnimalDescription AS Text1, lkurgency.Urgency AS Text2, '' AS Text3, LastChangedBy FROM animalwaitinglist " \
            "INNER JOIN lkurgency ON lkurgency.ID = animalwaitinglist.Urgency " \
            "ORDER BY DatePutOnList DESC, animalwaitinglist.ID"
    ]
    if dbo.dbtype == "SQLITE":
        # SQLITE can't support UNION with subqueries so construct a regular UNION
        # query and order/limit at the end (much less efficient with larger datasets)
        sql = ""
        for i, q in enumerate(queries):
            q = q[0:q.find("ORDER BY")]
            if i > 0 and i < len(queries): sql += " UNION ALL "
            sql += q
        sql += " ORDER BY EventDate DESC, ID " + dbo.sql_limit(limit)
        rows = dbo.query_cache(sql, age=age)
        return embellish_timeline(dbo.locale, [x for x in rows if x.EVENTDATE <= dbo.today(settime="23:59:59")])
    else:
        # Use nested subqueries with their own order by and limits for dbs that can support it
        # (performs better as the server is only having to collate smaller result sets)
        sql = "SELECT * FROM ("
        for i, q in enumerate(queries):
            q = "(%s %s)" % (q, dbo.sql_limit(limit))
            if i > 0 and i < len(queries): sql += " UNION ALL "
            sql += q
        sql += ") dummy WHERE EventDate <= ? ORDER BY EventDate DESC, ID " + dbo.sql_limit(limit)
        # We use end of today rather than now() for 2 reasons - 
        # 1. so it picks up all items for today and 2. now() would invalidate query_cache
        return embellish_timeline(dbo.locale, dbo.query_cache(sql, [dbo.today(settime="23:59:59")], age=age))

def calc_time_on_shelter(dbo: Database, animalid: int, a: ResultRow = None) -> str:
    """
    Returns the length of time the animal has been on the shelter as a 
    formatted string, eg: "6 weeks and 3 days"
    (int) animalid: The animal to calculate time on shelter for
    """
    l = dbo.locale
    return format_diff(l, calc_days_on_shelter(dbo, animalid, a), asm3.configuration.date_diff_cutoffs(dbo))

def calc_total_time_on_shelter(dbo: Database, animalid: int, a: ResultRow = None, movements: Results = None) -> str:
    """
    Returns the length of time the animal has been on the shelter as a 
    formatted string, eg: "6 weeks and 3 days"
    (int) animalid: The animal to calculate time on shelter for
    """
    l = dbo.locale
    return format_diff(l, calc_total_days_on_shelter(dbo, animalid, a, movements), asm3.configuration.date_diff_cutoffs(dbo))

def calc_days_on_shelter(dbo: Database, animalid: int, a: ResultRow = None) -> int:
    """
    Returns the number of days an animal has been on the shelter as an int
    (int) animalid: The animal to get the number of days on shelter for
    """
    stop = dbo.now()
    if a is None:
        a = dbo.query("SELECT Archived, MostRecentEntryDate, DeceasedDate, DiedOffShelter, ActiveMovementDate FROM animal WHERE ID = ?", [animalid])
        if len(a) == 0: return
        a = a[0]

    mre = remove_time(a.mostrecententrydate)

    # If the animal is dead, or has left the shelter
    # use that date as our cutoff instead
    if a.deceaseddate and a.diedoffshelter == 0:
        stop = a.deceaseddate
    elif a.activemovementdate and a.archived == 1:
        stop = a.activemovementdate

    return date_diff_days(mre, stop)

def calc_total_days_on_shelter(dbo: Database, animalid: int, a: ResultRow = None, movements: Results = None) -> int:
    """
    Returns the total number of days an animal has been on the shelter (counting all stays) as an int
    (int) animalid: The animal to get the number of days on shelter for
    a: The animal already loaded, needs Archived, DateBroughtIn, DeceasedDate, ActiveMovementDate
    movements: A list of movements that includes MovementDate and ReturnDate for this (and possibly other) animal(s) ordered by animalid
    """
    stop = dbo.now()
    if a is None:
        a = dbo.query("SELECT Archived, DateBroughtIn, DeceasedDate, DiedOffShelter, ActiveMovementDate FROM animal WHERE ID = ?", [animalid])
        if len(a) == 0: return 0
        a = a[0]

    start = remove_time(a.datebroughtin)

    # If the animal is dead, or is off the shelter
    # use that date as our final date instead
    if a.deceaseddate and a.diedoffshelter == 0:
        stop = a.deceaseddate
    elif a.activemovementdate and a.archived == 1:
        stop = a.activemovementdate
    daysonshelter = date_diff_days(start, stop)

    # Now, go through historic movements for this animal and deduct
    # all the time the animal has been off the shelter
    if movements is None:
        movements = dbo.query("SELECT AnimalID, MovementDate, ReturnDate " \
            "FROM adoption " \
            "WHERE AnimalID = ? AND MovementType <> 2 " \
            "AND MovementDate Is Not Null AND ReturnDate Is Not Null " \
            "ORDER BY AnimalID", [animalid])
    seen = False
    for m in movements:
        if m.animalid == animalid:
            seen = True
            if m.movementdate and m.returndate:
                daysonshelter -= date_diff_days(m.movementdate, m.returndate)
        else:
            # Stop iterating the list if we don't have a match and we previously
            # saw our animal id. Any movement list passed in should order by animalid
            if seen:
                break

    return daysonshelter

def calc_age_group(dbo: Database, animalid: int, a: ResultRow = None, bands: List[Tuple[str, float]] = None, todate: datetime = None) -> str:
    """
    Returns the age group the animal fits into based on its
    date of birth.
    (int) animalid: The animal to calculate the age group for
    a:              An animal record
    bands:          The age group bands for calculating groups (list of tuples containing groupname, yearcutoff)
    todate:         Calculate the agegroup at this date if supplied
    """
    # Calculate animal's age in days
    dob = None
    if a is None:
        dob = get_date_of_birth(dbo, animalid)
    else:
        dob = a.dateofbirth
    if todate is None: todate = dbo.now()
    days = date_diff_days(dob, todate)
    # Load age group bands if they weren't passed
    if bands is None:
        bands = asm3.configuration.age_group_bands(dbo)
    # Loop through the bands until we find one that the age in days fits into
    for group, years in bands:
        if days <= years * 365:
            return group
    # Out of bands and none matched
    return ""

def calc_age_group_rows(dbo: Database, rows: Results, todate: datetime = None) -> str:
    """
    Given a set of animal results, recalculates all the age groups on those rows at todate
    """
    bands = asm3.configuration.age_group_bands(dbo)
    for r in rows:
        r.AGEGROUP = calc_age_group(dbo, r.ID, r, bands, todate) 
    return rows

def calc_age(dbo: Database, animalid: int, a: ResultRow = None) -> str:
    """
    Returns an animal's age as a readable string
     (int) animalid: The animal to calculate time on shelter for
    """
    l = dbo.locale
    dob = None
    deceased = None
    if a is not None:
        dob = a.dateofbirth
        deceased = a.deceaseddate
    else:
        dob = get_date_of_birth(dbo, animalid)
        deceased = get_deceased_date(dbo, animalid)
    stop = dbo.now()

    # If the animal is dead, stop there
    if deceased is not None:
        stop = deceased

    # Format it as time period
    return date_diff(l, dob, stop, asm3.configuration.date_diff_cutoffs(dbo))

def calc_ages(dbo: Database, rows: Results) -> Results:
    """
    Updates the ANIMALAGE column on every result in rows
    """
    for a in rows:
        if a is None: continue
        a.ANIMALAGE = calc_age(dbo, a.ID, a)
    return rows

def calc_shelter_code(dbo: Database, animaltypeid: int, entryreasonid: int, speciesid: int, datebroughtin: datetime) -> Tuple[str, str, int, int]:
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
        XXXX - 4 digit padded code for next animal for year
        XXX - 3 digit padded code for next animal for year
        XX - unpadded code for next animal for year
        OOO - 3 digit padded code for next animal for month
        OO - unpadded code for next animal for month
        NNNN - 4 digit padded code for next animal of type for year
        NNN - 3 digit padded code for next animal of type for year
        NN - unpadded code for next animal of type for year
        PPPP - 4 digit padded code for next animal of species for year
        PPP - 3 digit padded code for next animal of species for year
        PP - unpadded code for next animal of species for year

    """
    asm3.al.debug("sheltercode: generating for type %d, entry %d, species %d, datebroughtin %s" % \
        (int(animaltypeid), int(entryreasonid), int(speciesid), datebroughtin),
        "animal.calc_shelter_code", dbo)

    def clean_lookup(s: str) -> str:
        """ Removes whitespace and punctuation from the beginning of a lookup name """
        s = s.replace("(", "").replace("[", "").replace("{", "")
        s = s.replace(".", "").replace(",", "").replace("!", "")
        s = s.replace("\"", "").replace("'", "").replace("`", "")
        s = s.strip()
        return s

    def substitute_tokens(fmt: str, year: int, month: int, syear: int, tyear: int, ever: int, datebroughtin: datetime, animaltype: str, species: str, entryreason: str) -> str:
        """
        Produces a code by switching tokens in the code format fmt.
        The format is parsed to left to right, testing for tokens. Anything
        not recognised as a token is added. Anything preceded by a backslash is added.
        """
        code = []
        x = 0
        while x < len(fmt):
            # Add the next character if we encounter a backslash to effectively escape it
            if fmt[x:x+1] == "\\":
                x += 1
                code.append(fmt[x:x+1])
                x += 1
            elif fmt[x:x+4] == "YYYY": 
                code.append("%04d" % datebroughtin.year)
                x += 4
            elif fmt[x:x+2] == "YY":   
                code.append("%02d" % (int(datebroughtin.year) - 2000))
                x += 2
            elif fmt[x:x+2] == "MM":   
                code.append("%02d" % datebroughtin.month)
                x += 2
            elif fmt[x:x+2] == "DD":   
                code.append("%02d" % datebroughtin.day)
                x += 2
            elif fmt[x:x+10] == "UUUUUUUUUU": 
                code.append("%010d" % ever)
                x += 10
            elif fmt[x:x+4] == "UUUU": 
                code.append("%04d" % ever)
                x += 4
            elif fmt[x:x+4] == "NNNN":  
                code.append("%04d" % tyear)
                x += 4
            elif fmt[x:x+3] == "NNN":  
                code.append("%03d" % tyear)
                x += 3
            elif fmt[x:x+2] == "NN":   
                code.append(str(tyear))
                x += 2
            elif fmt[x:x+4] == "PPPP":  
                code.append("%04d" % syear)
                x += 4
            elif fmt[x:x+3] == "PPP":  
                code.append("%03d" % syear)
                x += 3
            elif fmt[x:x+2] == "PP":   
                code.append(str(syear))
                x += 2
            elif fmt[x:x+4] == "XXXX":  
                code.append("%04d" % year)
                x += 4
            elif fmt[x:x+3] == "XXX":  
                code.append("%03d" % year)
                x += 3
            elif fmt[x:x+2] == "XX":   
                code.append(str(year))
                x += 2
            elif fmt[x:x+3] == "OOO":  
                code.append("%03d" % month)
                x += 3
            elif fmt[x:x+2] == "OO":   
                code.append(str(month))
                x += 2
            elif fmt[x:x+2] == "TT":   
                code.append(animaltype[:2])
                x += 2
            elif fmt[x:x+1] == "T":    
                code.append(animaltype[:1])
                x += 1
            elif fmt[x:x+2] == "SS":   
                code.append(species[:2])
                x += 2
            elif fmt[x:x+1] == "S":    
                code.append(species[:1])
                x += 1
            elif fmt[x:x+2] == "EE":   
                code.append(entryreason[:2])
                x += 2
            elif fmt[x:x+1] == "E":    
                code.append(entryreason[:1])
                x += 1
            else:
                code.append(fmt[x:x+1])
                x += 1
        return "".join(code)

    if datebroughtin is None:
        datebroughtin = dbo.today()

    codeformat = asm3.configuration.coding_format(dbo)
    shortformat = asm3.configuration.coding_format_short(dbo)
    animaltype = clean_lookup(asm3.lookups.get_animaltype_name(dbo, animaltypeid))
    entryreason = clean_lookup(asm3.lookups.get_entryreason_name(dbo, entryreasonid))
    species = clean_lookup(asm3.lookups.get_species_name(dbo, speciesid))
    beginningofyear = datetime(datebroughtin.year, 1, 1, 0, 0, 0)
    endofyear = datetime(datebroughtin.year, 12, 31, 23, 59, 59)
    beginningofmonth = asm3.i18n.first_of_month(datebroughtin)
    endofmonth = asm3.i18n.last_of_month(datebroughtin)
    oneyearago = subtract_years(dbo.today(), 1.0)
    highesttyear = 0
    highestsyear = 0
    highestyear = 0
    highestmonth = 0
    highestever = 0

    # If our code uses N, calculate the highest code seen for this type this year
    if codeformat.find("N") != -1 or shortformat.find("N") != -1:
        highesttyear = dbo.query_int("SELECT MAX(YearCodeID) FROM animal WHERE " \
            "DateBroughtIn >= ? AND " \
            "DateBroughtIn <= ? AND " \
            "AnimalTypeID = ?", ( beginningofyear, endofyear, animaltypeid))
        highesttyear += 1
    
    # If our code uses P, calculate the highest code seen for this species this year
    if codeformat.find("P") != -1 or shortformat.find("P") != -1:
        highestsyear = dbo.query_int("SELECT COUNT(ID) FROM animal WHERE " \
            "DateBroughtIn >= ? AND " \
            "DateBroughtIn <= ? AND " \
            "SpeciesID = ?", ( beginningofyear, endofyear, speciesid))
        highestsyear += 1

    # If our code uses X, calculate the highest code seen this year
    if codeformat.find("X") != -1 or shortformat.find("X") != -1:
        highestyear = dbo.query_int("SELECT COUNT(ID) FROM animal WHERE " \
            "DateBroughtIn >= ? AND " \
            "DateBroughtIn <= ?", (beginningofyear, endofyear))
        highestyear += 1

    # If our code uses O, calculate the highest code seen this month
    if codeformat.find("O") != -1 or shortformat.find("O") != -1:
        highestmonth = dbo.query_int("SELECT COUNT(ID) FROM animal WHERE " \
            "DateBroughtIn >= ? AND " \
            "DateBroughtIn <= ?", (beginningofmonth, endofmonth))
        highestmonth += 1

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
        code = substitute_tokens(codeformat, highestyear, highestmonth, highestsyear, highesttyear, highestever, datebroughtin, animaltype, species, entryreason)
        shortcode = substitute_tokens(shortformat, highestyear, highestmonth, highestsyear, highesttyear, highestever, datebroughtin, animaltype, species, entryreason)

        # Verify the code is unique
        unique = 0 == dbo.query_int("SELECT COUNT(*) FROM animal WHERE ShelterCode LIKE ?", [code])

        # If it's not, increment and try again
        if not unique:
            if codeformat.find("U") != -1: highestever += 1
            if codeformat.find("N") != -1: highesttyear += 1
            if codeformat.find("X") != -1: highestyear += 1
            if codeformat.find("P") != -1: highestsyear += 1
            if codeformat.find("O") != -1: highestmonth += 1

    asm3.al.debug("sheltercode: code=%s, short=%s for type %s, entry %s, species %s, datebroughtin %s" % \
        (code, shortcode, animaltype, entryreason, species, datebroughtin),
        "animal.calc_shelter_code", dbo)
    return (code, shortcode, highestever, highesttyear)

def get_is_on_shelter(dbo: Database, animalid: int) -> bool:
    """
    Returns true if the animal is on shelter
    """
    return 0 == dbo.query_int("SELECT Archived FROM animal WHERE ID = ?", [animalid])

def get_comments(dbo: Database, animalid: int) -> str:
    """
    Returns an animal's comments
    (int) animalid: The animal to get the comments from
    """
    return dbo.query_string("SELECT AnimalComments FROM animal WHERE ID = ?", [animalid])

def get_date_of_birth(dbo: Database, animalid: int) -> datetime:
    """
    Returns an animal's date of birth
    (int) animalid: The animal to get the dob
    """
    return dbo.query_date("SELECT DateOfBirth FROM animal WHERE ID = ?", [animalid])

def get_days_on_shelter(dbo: Database, animalid: int) -> int:
    """
    Returns the number of days on the shelter
    """
    return dbo.query_int("SELECT DaysOnShelter FROM animal WHERE ID = ?", [animalid])

def get_daily_boarding_cost(dbo: Database, animalid: int) -> int:
    """
    Returns the daily boarding cost
    """
    return dbo.query_int("SELECT DailyBoardingCost FROM animal WHERE ID = ?", [animalid])

def get_deceased_date(dbo: Database, animalid: int) -> datetime:
    """
    Returns an animal's deceased date
    (int) animalid: The animal to get the deceased date
    """
    return dbo.query_date("SELECT DeceasedDate FROM animal WHERE ID = ?", [animalid])

def get_date_brought_in(dbo: Database, animalid: int) -> datetime:
    """
    Returns the date an animal was brought in
    (int) animalid: The animal to get the brought in date from
    """
    return dbo.query_date("SELECT DateBroughtIn FROM animal WHERE ID = ?", [animalid])

def get_code(dbo: Database, animalid: int) -> str:
    """
    Returns the appropriate animal code for display
    """
    rv = ""
    if asm3.configuration.use_short_shelter_codes(dbo):
        rv = get_short_code(dbo, animalid)
    else:
        rv = get_shelter_code(dbo, animalid)
    return rv

def get_short_code(dbo: Database, animalid: int) -> str:
    """
    Returns the short code for animalid
    """
    return dbo.query_string("SELECT ShortCode FROM animal WHERE ID = ?", [animalid])

def get_shelter_code(dbo: Database, animalid: int) -> str:
    """
    Returns the shelter code for animalid
    """
    return dbo.query_string("SELECT ShelterCode FROM animal WHERE ID = ?", [animalid])

def get_extra_id(dbo: Database, a: ResultRow, idtype: str) -> str:
    """
    Retrieves a value from the ExtraIDs field, which is stored
    in the form:  key1=value1|key2=value2 ...
    a: An animal result from get_animal_query containing ExtraIDs
    idtype: A string key
    Returns the extra ID (string) or empty string if there was no match
    """
    if "EXTRAIDS" in a and a.EXTRAIDS is not None:
        for x in a.EXTRAIDS.split("|"):
            if x.find("=") != -1:
                k, v = x.split("=")
                if k == idtype:
                    return v
    return ""

def set_extra_id(dbo: Database, user: str, a: ResultRow, idtype: str, idvalue: str) -> str:
    """
    Stores a value in the ExtraIDs field for an animal, which is stored
    in the form:  key1=value1|key2=value2 ...
    a: An animal result from get_animal_query containing ExtraIDs and ID
    idtype: A string key
    idvalue: The value of the key (will be coerced to string).
    """
    ids = []
    ids.append( "%s=%s" % (idtype, idvalue) ) 
    extraids = a.EXTRAIDS 
    if extraids is None: extraids = ""
    for x in extraids.split("|"):
        if x.find("=") != -1:
            k, v = x.split("=")
            if k != idtype: ids.append( "%s=%s" % (k, v))
    extraids = "|".join(ids)
    a.EXTRAIDS = extraids
    dbo.update("animal", a.ID, { "ExtraIDs": extraids }, user)
    return extraids

def get_animal_id_and_bonds(dbo: Database, animalid: int) -> List[int]:
    """
    Returns a list containing animalid and the ids of other animals that
    animalid is bonded to.
    """
    animalids = [ animalid ]
    bonded = dbo.first_row(dbo.query("SELECT BondedAnimalID, BondedAnimal2ID FROM animal WHERE ID=?", [animalid]))
    if bonded is None: return animalids
    if bonded.BONDEDANIMALID is not None and bonded.BONDEDANIMALID > 0: animalids.append(bonded.BONDEDANIMALID)
    if bonded.BONDEDANIMAL2ID is not None and bonded.BONDEDANIMAL2ID > 0: animalids.append(bonded.BONDEDANIMAL2ID)
    return animalids

def get_animal_name(dbo: Database, animalid: int) -> str:
    """ Returns an animal's name alone or empty string if the id is not valid """
    return dbo.query_string("SELECT AnimalName FROM animal WHERE ID = ?", [asm3.utils.cint(animalid)])

def get_animal_namecode(dbo: Database, animalid: int) -> str:
    """
    Returns an animal's name and code or an empty
    string if the id is not valid.
    """
    r = dbo.query("SELECT AnimalName, ShelterCode, ShortCode " \
        "FROM animal WHERE ID = ?", [ asm3.utils.cint(animalid) ])
    if len(r) == 0:
        return ""
    if asm3.configuration.use_short_shelter_codes(dbo):
        rv = "%s - %s" % (r[0]["SHORTCODE"], r[0]["ANIMALNAME"])
    else:
        rv = "%s - %s" % (r[0]["SHELTERCODE"], r[0]["ANIMALNAME"])
    return rv

def get_animals_namecode(dbo: Database) -> Results:
    """
    Returns a resultset containing the ID, name and code
    of all animals.
    """
    return dbo.query("SELECT ID, AnimalName, ShelterCode, ShortCode " \
        "FROM animal ORDER BY AnimalName, ShelterCode")

def get_animals_on_shelter_namecode(dbo: Database, remove_units: bool = False, remove_fosterer: bool = False,
                                    lf: LocationFilter = None) -> Results:
    """
    Returns a resultset containing the ID, Name, Code and DisplayLocation of all shelter animals.
    remove_units: Strip location units from DisplayLocation
    remove_fosterer: Strip fosterer from DisplayLocation
    """
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(andprefix=True)
    rows = dbo.query("SELECT animal.ID, AnimalName, ShelterCode, ShortCode, SpeciesID, s.SpeciesName, ActiveMovementType, DisplayLocation, " \
        "CASE WHEN EXISTS(SELECT ItemValue FROM configuration WHERE ItemName Like 'UseShortShelterCodes' AND ItemValue = 'Yes') " \
        "THEN ShortCode ELSE ShelterCode END AS Code " \
        "FROM animal " \
        "LEFT OUTER JOIN species s ON s.ID = animal.SpeciesID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation " \
        f"WHERE Archived = 0 {locationfilter} " \
        "ORDER BY AnimalName, ShelterCode")
    for r in rows:
        if r.DISPLAYLOCATION is None: r.DISPLAYLOCATION = ""
        if remove_units and r.ACTIVEMOVEMENTTYPE != 2 and r.DISPLAYLOCATION.find("::") != -1: r.DISPLAYLOCATION = r.DISPLAYLOCATION[:r.DISPLAYLOCATION.find("::")]
        if remove_fosterer and r.ACTIVEMOVEMENTTYPE == 2 and r.DISPLAYLOCATION.find("::") != -1: r.DISPLAYLOCATION = r.DISPLAYLOCATION[:r.DISPLAYLOCATION.find("::")]
    return rows

def get_animals_on_foster_namecode(dbo: Database) -> Results:
    """
    Returns a resultset containing the ID, Name, Code of all foster animals.
    """
    rows = dbo.query("SELECT animal.ID, AnimalName, ShelterCode, ShortCode, SpeciesID, s.SpeciesName, " \
        "CASE WHEN EXISTS(SELECT ItemValue FROM configuration WHERE ItemName Like 'UseShortShelterCodes' AND ItemValue = 'Yes') " \
        "THEN ShortCode ELSE ShelterCode END AS Code " \
        "FROM animal " \
        "LEFT OUTER JOIN species s ON s.ID = animal.SpeciesID " \
        "WHERE ActiveMovementType = 2 AND DeceasedDate Is Null " \
        "ORDER BY AnimalName, ShelterCode")
    return rows

def get_animals_adoptable_namecode(dbo: Database) -> Results:
    """
    Returns a resultset containing the ID, Name and Code of all adoptable animals.
    """
    rows = dbo.query("SELECT animal.ID, AnimalName, ShelterCode, ShortCode, SpeciesID, s.SpeciesName, " \
        "CASE WHEN EXISTS(SELECT ItemValue FROM configuration WHERE ItemName Like 'UseShortShelterCodes' AND ItemValue = 'Yes') " \
        "THEN ShortCode ELSE ShelterCode END AS Code " \
        "FROM animal " \
        "LEFT OUTER JOIN species s ON s.ID = animal.SpeciesID " \
        "WHERE Adoptable=1 " \
        "ORDER BY AnimalName, ShelterCode")
    return rows

def get_animals_adopted_namecode(dbo: Database, days: int = 30, remove_adopter: bool = False) -> Results:
    """
    Returns a resultset containing the ID, Name, Code and DisplayLocation of all animals who were recently adopted.
    remove_adopter: Strip adopter's name from DisplayLocation
    """
    cutoffdate = dbo.today(offset=days*-1)
    rows = dbo.query("SELECT animal.ID, AnimalName, ShelterCode, ShortCode, SpeciesID, SpeciesName, ActiveMovementType, DisplayLocation, " \
        "CASE WHEN EXISTS(SELECT ItemValue FROM configuration WHERE ItemName Like 'UseShortShelterCodes' AND ItemValue = 'Yes') " \
        "THEN ShortCode ELSE ShelterCode END AS Code " \
        "FROM animal " \
        "LEFT OUTER JOIN species ON species.ID = animal.SpeciesID " \
        "WHERE ActiveMovementType=1 AND ActiveMovementDate > ? AND DeceasedDate Is Null ORDER BY AnimalName, ShelterCode", [cutoffdate])
    for r in rows:
        if r.DISPLAYLOCATION is None: r.DISPLAYLOCATION = ""
        if remove_adopter and r.ACTIVEMOVEMENTTYPE != 2 and r.DISPLAYLOCATION.find("::") != -1: r.DISPLAYLOCATION = r.DISPLAYLOCATION[:r.DISPLAYLOCATION.find("::")]
    return rows

def get_animals_on_shelter_foster_namecode(dbo: Database) -> Results:
    """
    Returns a resultset containing the ID, name and code
    of all on shelter and foster animals.
    """
    return dbo.query("SELECT animal.ID, AnimalName, ShelterCode, ShortCode, SpeciesName, DisplayLocation, " \
        "CASE WHEN EXISTS(SELECT ItemValue FROM configuration WHERE ItemName Like 'UseShortShelterCodes' AND ItemValue = 'Yes') " \
        "THEN ShortCode ELSE ShelterCode END AS Code " \
        "FROM animal " \
        "LEFT OUTER JOIN species ON species.ID = animal.SpeciesID " \
        "WHERE (Archived = 0 OR ActiveMovementType = 2) ORDER BY AnimalName, ShelterCode")

def get_breedname(dbo: Database, breed1id: int, breed2id: int) -> str:
    """
    Returns the name of a breed from the primary and secondary breed
    breed1id: The first breed
    breed2id: The second breed
    """
    if breed1id == 0: return ""
    if breed1id == breed2id or breed2id == 0:
        return asm3.lookups.get_breed_name(dbo, breed1id)
    return asm3.lookups.get_breed_name(dbo, breed1id) + "/" + asm3.lookups.get_breed_name(dbo, breed2id)

def get_costs(dbo: Database, animalid: int, sort: int = ASCENDING) -> Results:
    """
    Returns cost records for the given animal:
    COSTTYPEID, COSTTYPENAME, COSTDATE, DESCRIPTION, OWNERID, INVOICENUMBER
    """
    sql = "SELECT a.ID, a.CostTypeID, a.CostAmount, a.CostDate, a.CostPaidDate, c.CostTypeName, a.Description, " \
        "a.CreatedBy, a.CreatedDate, a.LastChangedBy, a.LastChangedDate, a.OwnerID, a.InvoiceNumber, o.OwnerName " \
        "FROM animalcost a INNER JOIN costtype c ON c.ID = a.CostTypeID " \
        "LEFT JOIN owner o ON a.OwnerID = o.ID " \
        "WHERE a.AnimalID = ?"
    if sort == ASCENDING:
        sql += " ORDER BY a.CostDate"
    else:
        sql += " ORDER BY a.CostDate DESC"
    return dbo.query(sql, [animalid])

def get_cost_totals(dbo: Database, animalid: int) -> ResultRow:
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
    return dbo.first_row( dbo.query(q, [animalid]) )

def get_diets(dbo: Database, animalid: int, sort: int = ASCENDING) -> Results:
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

def get_display_location(dbo: Database, animalid: int) -> str:
    """ Returns an animal's current display location """
    return dbo.query_string("SELECT DisplayLocation FROM animal WHERE ID = ?", [animalid])

def get_display_location_noq(dbo: Database, animalid: int, loc: str = "") -> str:
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

def get_animal_entries(dbo: Database, animalid: int) -> Results:
    """
    Returns the list of entry histories for an animal
    """
    return dbo.query( get_animal_entry_query(dbo) + " WHERE ae.AnimalID = ?", [animalid] )

def delete_animal_entry(dbo: Database, username: str, aeid: int) -> int:
    """ Deletes the animal entry history item aeid """
    return dbo.delete("animalentry", aeid, username)

def insert_animal_entry(dbo: Database, username: str, animalid: int) -> int:
    """
    Copies the current values from the entry fields in the animal table to the animalentry table.
    Updates the entry fields to values from the latest returned movement (if available) and generates a new shelter code.
    The UI should reload after any process that calls this.
    """
    a = get_animal(dbo, animalid)
    rxm = get_returned_exit_movements(dbo, animalid)
    # The entry date for our new record is going to be first intake or the 2nd most recent return if available
    entrydate = a.DATEBROUGHTIN
    if len(rxm) > 1: entrydate = rxm[1].RETURNDATE
    ae = dbo.insert("animalentry", {
        "AnimalID":                 animalid,
        "ShelterCode":              a.SHELTERCODE,
        "ShortCode":                a.SHORTCODE,
        "EntryDate":                entrydate,
        "EntryReasonID":            a.ENTRYREASONID,
        "EntryTypeID":              a.ENTRYTYPEID,
        "AdoptionCoordinatorID":    a.ADOPTIONCOORDINATORID,
        "BroughtInByOwnerID":       a.BROUGHTINBYOWNERID,
        "OriginalOwnerID":          a.ORIGINALOWNERID,
        "AsilomarIntakeCategory":   a.ASILOMARINTAKECATEGORY,
        "JurisdictionID":           a.JURISDICTIONID,
        "IsTransfer":               a.ISTRANSFER,
        "AsilomarIsTransferExternal": a.ASILOMARISTRANSFEREXTERNAL,
        "HoldUntilDate":            a.HOLDUNTILDATE,
        "IsPickup":                 a.ISPICKUP,
        "PickupLocationID":         a.PICKUPLOCATIONID,
        "PickupAddress":            a.PICKUPADDRESS,
        "ReasonNO":                 a.REASONNO,
        "ReasonForEntry":           a.REASONFORENTRY
    }, username)
    # Reset the animal entry fields, copying values from the last 
    # returned exit movement if one is available.
    entryreasonid = asm3.configuration.default_entry_reason(dbo)
    broughtinbyownerid = 0
    originalownerid = 0
    istransfer = 0
    ispickup = 0
    if len(rxm) > 0:
        entryreasonid = rxm[0].RETURNEDREASONID
        broughtinbyownerid = rxm[0].RETURNEDBYOWNERID
        originalownerid = rxm[0].OWNERID
        istransfer = asm3.utils.iif(rxm[0].MOVEMENTTYPE == 3, 1, 0)
        ispickup = asm3.utils.iif(rxm[0].MOVEMENTTYPE == 5, 1, 0)
    # Generate a new code for the animal
    code, shortcode, unique, year = calc_shelter_code(dbo, a.ANIMALTYPEID, entryreasonid, a.SPECIESID, a.MOSTRECENTENTRYDATE)
    dbo.update("animal", animalid, {
        "ShelterCode":          code,
        "ShortCode":            shortcode,
        "UniqueCodeID":         unique,
        "YearCodeID":           year,
        # NOTE: DateBroughtIn is never touched, 
        # MostRecentEntryDate is updated by update_animal_status before this code ever runs
        "EntryTypeID":          1, # Usually a return of some type so default to surrender
        "EntryReasonID":        entryreasonid,
        "AdoptionCoordinatorID": 0,
        "BroughtInByOwnerID":   broughtinbyownerid,
        "OriginalOwnerID":      originalownerid,
        "IsTransfer":           istransfer,
        "HoldUntilDate":        None,
        "IsPickup":             ispickup,
        "PickupAddress":        "",
        "ReasonNO":             "",
        "ReasonForEntry":       ""
    }, username)
    return ae

def get_has_animals(dbo: Database) -> bool:
    """
    Returns True if there is at least one animal in the database
    """
    return dbo.query_int("SELECT COUNT(ID) FROM animal") > 0

def get_has_animal_on_shelter(dbo: Database) -> bool:
    """
    Returns True if there is at least one animal on the shelter
    """
    return dbo.query_int("SELECT COUNT(ID) FROM animal a WHERE a.Archived = 0") > 0

def get_exit_movement_types(dbo: Database) -> str:
    """
    Returns a string IN clause of the movement types that constitute an exit.
    Typically all of them but reservations, fostering and retailers.
    """
    exit_movements = "1,3,4,5,6,7"
    if not asm3.configuration.foster_on_shelter(dbo): 
        exit_movements += ",2"
    if not asm3.configuration.retailer_on_shelter(dbo):
        exit_movements += ",8"
    return exit_movements

def get_returned_exit_movements(dbo: Database, animalid: int) -> Results:
    """
    Returns a list of returned exit movements for animalid, ordered by movementdate descending
    """
    exit_movements = get_exit_movement_types(dbo)
    return dbo.query("SELECT * FROM adoption WHERE AnimalID=? AND " \
        f"MovementType IN ({exit_movements}) AND " \
        "MovementDate Is Not Null AND ReturnDate Is Not Null " \
        "ORDER BY MovementDate DESC", [animalid])

def get_links_adoptable(dbo: Database, lf: LocationFilter = None, limit: int = 5, cachetime: int = 120) -> Results:
    """
    Returns link info for animals who are adoptable
    """
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(andprefix=True)
    return get_animals_ids_brief(dbo, "a.AnimalName", 
        "SELECT animal.ID FROM animal LEFT OUTER JOIN internallocation il ON il.ID = ShelterLocation WHERE Adoptable = 1 %s ORDER BY AnimalName" % \
        locationfilter, limit=limit, cachetime=cachetime)

def get_links_recently_adopted(dbo: Database, lf: LocationFilter = None, limit: int = 5, cachetime: int = 120) -> Results:
    """
    Returns link info for animals who were recently adopted
    """
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(andprefix=True)
    return get_animals_ids_brief(dbo, "a.ActiveMovementDate DESC", 
        "SELECT animal.ID FROM animal LEFT OUTER JOIN internallocation il ON il.ID = ShelterLocation WHERE ActiveMovementType = 1 %s ORDER BY ActiveMovementDate DESC" % \
        locationfilter, limit=limit, cachetime=cachetime)

def get_links_recently_fostered(dbo: Database, lf: LocationFilter = None, limit: int = 5, cachetime: int = 120) -> Results:
    """
    Returns link info for animals who were recently fostered
    """
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(andprefix=True)
    return get_animals_ids_brief(dbo, "a.ActiveMovementDate DESC", 
        "SELECT animal.ID FROM animal LEFT OUTER JOIN internallocation il ON il.ID = ShelterLocation WHERE ActiveMovementType = 2 %s ORDER BY ActiveMovementDate DESC" % \
        locationfilter, limit=limit, cachetime=cachetime)

def get_links_recently_changed(dbo: Database, lf: LocationFilter = None, limit: int = 5, cachetime: int = 120) -> Results:
    """
    Returns link info for animals who have recently been changed.
    """
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(whereprefix=True)
    return get_animals_ids_brief(dbo, "a.LastChangedDate DESC", 
        "SELECT animal.ID FROM animal LEFT OUTER JOIN internallocation il ON il.ID = ShelterLocation %s ORDER BY LastChangedDate DESC" % \
        locationfilter, limit=limit, cachetime=cachetime)

def get_links_recently_entered(dbo: Database, lf: LocationFilter = None, limit: int = 5, cachetime: int = 120) -> Results:
    """
    Returns link info for animals who recently entered the shelter.
    """
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(andprefix=True)
    return get_animals_ids_brief(dbo, "a.MostRecentEntryDate DESC", 
        "SELECT animal.ID FROM animal LEFT OUTER JOIN internallocation il ON il.ID = ShelterLocation WHERE Archived = 0 %s ORDER BY MostRecentEntryDate DESC" % \
        locationfilter, limit=limit, cachetime=cachetime)

def get_links_longest_on_shelter(dbo: Database, lf: LocationFilter = None, limit: int = 5, cachetime: int = 120) -> Results:
    """
    Returns link info for animals who have been on the shelter the longest
    """
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(andprefix=True)
    return get_animals_ids_brief(dbo, "a.MostRecentEntryDate", 
        "SELECT animal.ID FROM animal LEFT OUTER JOIN internallocation il ON il.ID = ShelterLocation WHERE Archived = 0 %s ORDER BY MostRecentEntryDate" % \
        locationfilter, limit=limit, cachetime=cachetime)

def get_number_animals_on_file(dbo: Database) -> int:
    """
    Returns the number of animals on the system
    """
    return dbo.query_int("SELECT COUNT(ID) FROM animal")

def get_number_animals_on_shelter_now(dbo: Database) -> int:
    """
    Returns the number of animals on shelter
    """
    return dbo.query_int("SELECT COUNT(ID) FROM animal WHERE Archived = 0")

def update_active_litters(dbo: Database) -> None:
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
        "(l.InvalidDate Is Null OR l.InvalidDate > ?) ", ( subtract_months(dbo.today(), 6), dbo.today() ))
    for a in active:
        remaining = a.cachedanimalsleft
        newremaining = a.dbcount
        if newremaining == 0:
            asm3.al.debug("litter '%s' has no animals left, expiring." % a.acceptancenumber, "animal.update_active_litters", dbo)
            dbo.execute("UPDATE animallitter SET InvalidDate=? WHERE ID=?", (dbo.today(), a.id))
        if newremaining != remaining:
            dbo.execute("UPDATE animallitter SET CachedAnimalsLeft=? WHERE ID=?", (newremaining, a.id))
            asm3.al.debug("litter '%s' change, setting remaining to %d." % (a.acceptancenumber, int(newremaining)), "animal.update_active_litters", dbo)

def get_active_litters(dbo: Database, speciesid: int = -1) -> Results:
    """
    Returns all active animal litters in descending order of age
    speciesid: A species filter or -1 for all
    """
    sql = "SELECT l.*, a.AnimalName AS MotherName, " \
        "a.ShelterCode AS Mothercode, s.SpeciesName AS SpeciesName " \
        "FROM animallitter l " \
        "LEFT OUTER JOIN animal a ON l.ParentAnimalID = a.ID " \
        "INNER JOIN species s ON l.SpeciesID = s.ID " \
        "WHERE (InvalidDate Is Null OR InvalidDate > ?) %s" \
        "ORDER BY l.Date DESC" 
    values = [ dbo.today() ]
    if speciesid != -1: 
        sql = sql % "AND SpeciesID = ? "
        values.append(speciesid)
    else:
        sql = sql % ""
    return dbo.query(sql, values)

def get_active_litters_brief(dbo: Database) -> List[dict]:
    """ Returns the active litters in brief form for use by autocomplete """
    l = dbo.locale
    al = get_litters(dbo)
    rv = []
    for i in al:
        disp = ""
        if i.parentanimalid and i.parentanimalid > 0:
            disp = _("{0}: {1} {2} - {3} {4}", l).format(
                i.mothercode, i.mothername,
                i.acceptancenumber, i.speciesname,
                asm3.utils.truncate(i.comments, 40))
        else:
            disp = _("{0} - {1} {2}", l).format(
                i.acceptancenumber, i.speciesname,
                asm3.utils.truncate(i.comments, 40))
        rv.append( { "label": disp, "value": i.acceptancenumber } )
    return rv

def get_litters(dbo: Database, offset: str = "m365") -> Results:
    """
    Returns all animal litters in descending order of age. 
    offset is m to go backwards days, or a for all time
    """
    offsetdays = asm3.utils.atoi(offset)
    where = ""
    v = []
    if offset.startswith("m"): 
        where = "WHERE Date >= ? "
        v.append( dbo.today(offsetdays*-1) )
    return dbo.query("SELECT l.*, a.AnimalName AS MotherName, " \
        "a.ShelterCode AS Mothercode, s.SpeciesName AS SpeciesName " \
        "FROM animallitter l " \
        "LEFT OUTER JOIN animal a ON l.ParentAnimalID = a.ID " \
        "INNER JOIN species s ON l.SpeciesID = s.ID " \
        "%s" \
        "ORDER BY l.Date DESC" % where, v)

def get_litter_animals_by_id(dbo: Database, litterid: str) -> Results:
    """ Returns all animals who have litterid """
    return dbo.query(get_animal_brief_query(dbo) + " WHERE a.AcceptanceNumber = ?", [litterid])

def get_litter_animals(dbo: Database, litters: Results = []) -> Results:
    """ Returns all animals who have a litter ID in set litters """
    litterids = []
    for l in litters:
        litterids.append(dbo.sql_value(l.ACCEPTANCENUMBER.replace("'", "`")))
    if len(litterids) == 0: return []
    return dbo.query(get_animal_brief_query(dbo) + " WHERE a.AcceptanceNumber IN ( " + ",".join(litterids) + ") ORDER BY a.ID")

def get_litter_mothers(dbo: Database, litters: Results = []) -> Results:
    """ Returns all mothers from the active litters """
    motherids = []
    for l in litters:
        motherids.append(dbo.sql_value(l.PARENTANIMALID))
    if len(motherids) == 0: return []
    return dbo.query(get_animal_brief_query(dbo) + " WHERE a.ID IN ( " + ",".join(motherids) + ") ORDER BY a.ID")

def get_satellite_counts(dbo: Database, animalid: int) -> Results:
    """
    Returns a resultset containing the number of each type of satellite
    record that an animal has.
    """
    return dbo.query("SELECT a.ID, " \
        "(SELECT COUNT(*) FROM animalvaccination av WHERE av.AnimalID = a.ID) AS vaccination, " \
        "(SELECT COUNT(*) FROM animaltest at WHERE at.AnimalID = a.ID) AS test, " \
        "(SELECT COUNT(*) FROM animalmedical am WHERE am.AnimalID = a.ID) AS medical, " \
        "(SELECT COUNT(*) FROM animalboarding ab WHERE ab.AnimalID = a.ID) AS boarding, " \
        "(SELECT COUNT(*) FROM clinicappointment ca WHERE ca.AnimalID = a.ID) AS clinic, " \
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
        (asm3.media.ANIMAL, asm3.diary.ANIMAL, asm3.log.ANIMAL, animalid))

def get_random_name(dbo: Database, sex: int = 0) -> str:
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
    if len(names) < 100: return asm3.animalname.get_random_name()
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
        return asm3.animalname.get_random_name()
    elif decide == 4 or decide == 5:
        return choice(leastused)["ANIMALNAME"]
    else:
        return choice(names)["ANIMALNAME"]

def get_recent_with_name(dbo: Database, name: str) -> Results:
    """
    Returns a list of animals who have a brought in date in the last 3 weeks OR are on shelter
    and have the name given.
    """
    return dbo.query("SELECT ID, ID AS ANIMALID, SHELTERCODE, ANIMALNAME FROM animal " \
        "WHERE (DateBroughtIn >= ? OR Archived=0) AND LOWER(AnimalName) LIKE ?", (dbo.today(offset=-21), name.lower()))

def get_recent_changes(dbo: Database, months: int = 1, include_additional_fields: bool = True) -> Results:
    """ Returns all animal records that were changed in the last months """
    rows = dbo.query(get_animal_query(dbo) + \
        " WHERE a.LastChangedDate > ? " \
        "ORDER BY a.LastChangedDate DESC", [dbo.today(offset=months*31*-1)])
    if include_additional_fields: 
        rows = asm3.additional.append_to_results(dbo, rows, "animal")
    return rows

def get_shelter_animals(dbo: Database, include_additional_fields: bool = True) -> Results:
    """ Return full animal records for all shelter animals """
    rows = dbo.query(get_animal_query(dbo) + \
        " WHERE a.Archived = 0 " \
        "ORDER BY a.AnimalName")
    if include_additional_fields: 
        rows = asm3.additional.append_to_results(dbo, rows, "animal")
    return rows

def get_signed_requests(dbo: Database, cutoff: int = 7) -> Results:
    """
    Returns animals that have a fulfilled a signing request in the last cutoff days
    """
    cutoffdate = dbo.today(cutoff * -1)
    rows = dbo.query("SELECT l.LinkID AS ID FROM log l " \
        "WHERE l.LinkType=0 AND l.Date >= ? AND l.Comments LIKE 'ES02%%'", [cutoffdate], distincton="ID")
    return dbo.query(get_animal_query(dbo) + "WHERE a.ID IN (%s)" % dbo.sql_in(rows))

def get_unsigned_requests(dbo: Database, cutoff: int = 31) -> Results:
    """
    Returns animals that have more signing requests in the last cutoff days than signed
    """
    cutoffdate = dbo.today(cutoff * -1)
    rows = dbo.query("SELECT l.LinkID AS ID FROM log l " \
        "WHERE l.LinkType=0 AND l.Date >= ? AND l.Comments LIKE 'ES01%%' " \
        "AND (SELECT COUNT(*) FROM log WHERE LinkID=l.LinkID AND LinkType=0 AND Date >= ? AND Comments LIKE 'ES01%%') " \
        " > (SELECT COUNT(*) FROM log WHERE LinkID=l.LinkID AND LinkType=0 AND Date >= ? AND Comments LIKE 'ES02%%') ", \
        [cutoffdate, cutoffdate, cutoffdate], distincton="ID")
    return dbo.query(get_animal_query(dbo) + "WHERE a.ID IN (%s)" % dbo.sql_in(rows))

def get_units_with_availability(dbo: Database, locationid: int) -> List[str]:
    """
    Returns a list of location units for location id.
    The layout of each element is unit|occupant
    Blank occupant means a free unit
    """
    l = dbo.locale
    a = []
    units = dbo.query_string("SELECT Units FROM internallocation WHERE ID = ?", [locationid]).replace("|", ",").split(",")
    animals = dbo.query("SELECT a.AnimalName, a.ShortCode, a.ShelterCode, a.ShelterLocationUnit " \
        "FROM animal a WHERE a.Archived = 0 AND ActiveMovementID = 0 AND ShelterLocation = ?", [locationid])
    useshortcodes = asm3.configuration.use_short_shelter_codes(dbo)
    for u in units:
        if u == "": continue
        uname = u.strip()
        unamec = uname.replace("'", "`").lower()
        occupant = ""
        # Check for an animal in the unit
        for n in animals:
            if asm3.utils.nulltostr(n.shelterlocationunit).strip().lower() == unamec:
                if occupant != "": occupant += ", "
                occupant += useshortcodes and n.shortcode or n.sheltercode
                occupant += " %s" % n.animalname
                break
        # Check if the unit is reserved
        if occupant == "":
            for ux in asm3.configuration.unit_extra(dbo).split("&&"):
                if ux.count("|") < 6: continue
                v = ux.split("||")
                if v[0] == str(locationid) and v[1] == uname and v[3] != "":
                    occupant = _("Reserved for {0}", l).replace("{0}", v[3])
                    break
        a.append( "%s|%s" % (uname, occupant) )
    return a

def get_publish_history(dbo: Database, animalid: int) -> Results:
    """
    Returns a list of services and the date the animal was last registered with them.
    """
    return dbo.query("SELECT PublishedTo, SentDate, Extra FROM animalpublished WHERE AnimalID = ? ORDER BY SentDate DESC", [animalid])

def insert_publish_history(dbo: Database, animalid: int, service: str) -> None:
    """
    Marks an animal as published to a particular service now
    """
    dbo.execute("DELETE FROM animalpublished WHERE AnimalID = ? AND PublishedTo = ?", (animalid, service))
    dbo.execute("INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) VALUES (?, ?, ?)", \
        (animalid, service, dbo.now()))

def delete_publish_history(dbo: Database, animalid: int, service: str) -> None:
    """
    Forgets an animal has been published to a particular service.
    """
    dbo.execute("DELETE FROM animalpublished WHERE AnimalID = ? AND PublishedTo = ?", (animalid, service))

def get_shelterview_animals(dbo: Database, lf: LocationFilter = None) -> Results:
    """
    Returns all available animals for shelterview.
    Age groups are recalculated to today for display.
    """
    limit = asm3.configuration.record_search_limit(dbo)
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(andprefix=True)
    animals = get_animals_ids_brief(dbo, "a.AnimalName", "SELECT animal.ID FROM animal " \
        "LEFT OUTER JOIN internallocation il ON il.ID = animal.ShelterLocation " \
        f"WHERE Archived = 0 {locationfilter} ORDER BY HasPermanentFoster, animal.ID DESC", limit=limit)
    return calc_age_group_rows(dbo, animals)

def insert_animal_from_form(dbo: Database, post: PostedData, username: str) -> int:
    """
    Creates an animal record from the new animal screen
    data: The webpy data object containing form parameters
    Returns a tuple containing the newly created animal id and code
    """
    l = dbo.locale
    nextid = dbo.get_id("animal")
    post.data["id"] = nextid

    if post["dateofbirth"] == "" or post.date("dateofbirth") is None:
        estimatedage = post.floating("estimatedage")
        if estimatedage <= 0 or estimatedage > 100:
            raise asm3.utils.ASMValidationError(_("Estimated age '{0}' is not valid.", l).format(estimatedage))
        estimateddob = 1
        dob = subtract_years(dbo.today(), estimatedage)
    else:
        estimateddob = 0
        dob = post.date("dateofbirth")

    # Set brought in by date
    datebroughtin = post.datetime("datebroughtin", "timebroughtin")
    if datebroughtin is None:
        if asm3.configuration.add_animals_show_time_brought_in(dbo):
            datebroughtin = dbo.now()
        else:
            datebroughtin = dbo.today()

    # Set the code manually if we were given a code, or the option was turned on
    if asm3.configuration.manual_codes(dbo) or post["sheltercode"] != "":
        sheltercode = post["sheltercode"]
        shortcode = post["shortcode"]
        unique = 0
        year = 0
        if sheltercode.strip() == "":
            raise asm3.utils.ASMValidationError(_("You must supply a code.", l))
        if 0 != dbo.query_int("SELECT COUNT(ID) FROM animal WHERE LOWER(ShelterCode) = LOWER(?)", [sheltercode]):
            raise asm3.utils.ASMValidationError(_("This code has already been used.", l))
    else:
        # Generate a new code
        sheltercode, shortcode, unique, year = calc_shelter_code(dbo, post.integer("animaltype"), post.integer("entryreason"), post.integer("species"), datebroughtin)

    # Default good with to unknown
    goodwithcats = 2
    if "goodwithcats" in post: goodwithcats = post.integer("goodwithcats")
    goodwithdogs = 2
    if "goodwithdogs" in post: goodwithdogs = post.integer("goodwithdogs")
    goodwithkids = 2
    if "goodwithkids" in post: goodwithkids = post.integer("goodwithkids")
    housetrained = 2
    if "housetrained" in post: housetrained = post.integer("housetrained")
    cratetrained = 2
    if "cratetrained" in post: cratetrained = post.integer("cratetrained")
    goodwithelderly = 2
    if "goodwithelderly" in post: goodwithelderly = post.integer("goodwithelderly")
    goodtraveller = 2
    if "goodtraveller" in post: goodtraveller = post.integer("goodtraveller")
    goodonlead = 2
    if "goodonlead" in post: goodonlead = post.integer("goodonlead")
    energylevel = 0
    if "energylevel" in post: energylevel = post.integer("energylevel")

    unknown = 0

    # Validate form fields
    if post["animalname"] == "":
        raise asm3.utils.ASMValidationError(_("Name cannot be blank", l))
    if post["microchipnumber"].strip() != "" and not asm3.configuration.allow_duplicate_microchip(dbo):
        if dbo.query_int("SELECT COUNT(ID) FROM animal WHERE IdentichipNumber Like ? AND ID <> ?", (post["microchipnumber"], nextid)) > 0:
            raise asm3.utils.ASMValidationError(_("Microchip number {0} has already been allocated to another animal.", l).format(post["microchipnumber"]))
    if dob > dbo.today():
        raise asm3.utils.ASMValidationError(_("Date of birth cannot be in the future.", l))
    # Enforce a limit on the number of days in the future that brought in date can be
    futurelimit = asm3.configuration.date_brought_in_future_limit(dbo) 
    if futurelimit and datebroughtin > dbo.today(offset=futurelimit):
        raise asm3.utils.ASMValidationError(_("Date brought in cannot be in the future.", l))

    # Set default brought in by if we have one and none was set
    dbb = post.integer("broughtinby")
    if dbb == 0:
        dbb = asm3.configuration.default_broughtinby(dbo)

    # If we have nsowner, use that over originalowner for non-shelter animals
    originalowner = post.integer("originalowner")
    if post.integer("nsowner") != 0:
        originalowner = post.integer("nsowner")

    # Set not for adoption if the option is on
    notforadoption = 0
    if "notforadoption" in post:
        notforadoption = post.integer("notforadoption")
    elif asm3.configuration.auto_not_for_adoption(dbo):
        notforadoption = 1        

    # Set not for register if the option is on
    notforregistration = 0
    if "notforregistration" in post:
        notforregistration = post.integer("notforregistration")

    # Handle deceased date and doa being set via entry type
    deceaseddate = post.date("deceaseddate")
    deadonarrival = post.integer("deadonarrival")
    deathcategory = post.integer("deathcategory")
    if post.integer("entrytype") == 9:
        deceaseddate = dbo.today()
        deadonarrival = 1
        deathcategory = asm3.configuration.default_death_reason(dbo)

    # If this user is in a site, make sure that the location
    # chosen is in their site. If it isn't, override the location
    # to the first one in their site to make sure they can see
    # the animal after creation.
    shelterlocation = post.integer("internallocation")
    usite = asm3.users.get_site(dbo, username)
    if usite > 0:
        lsite = dbo.query_int("SELECT SiteID FROM internallocation WHERE ID=?", [shelterlocation])
        # If location site doesn't match user site, swap to the first location in the user's site
        if lsite != usite:
            shelterlocation = dbo.query_int("SELECT ID FROM internallocation WHERE SiteID=? ORDER BY ID", [usite])

    # Record the initial location 
    insert_animallocation(dbo, username, nextid, post["animalname"], sheltercode, 0, "*", shelterlocation, post["unit"])

    dbo.insert("animal", {
        "ID":               nextid,
        "AnimalName":       post["animalname"],
        "ShelterCode":      sheltercode,
        "ShortCode":        shortcode,
        "UniqueCodeID":     unique,
        "YearCodeID":       year,
        "DateOfBirth":      dob,
        "DailyBoardingCost": asm3.configuration.default_daily_boarding_cost(dbo),
        "Sex":              post.integer("sex"),
        "AnimalTypeID":     post.integer("animaltype"),
        "SpeciesID":        post.integer("species"),
        "BreedID":          post.integer("breed1"),
        "Breed2ID":         post.integer("breed2"),
        "BreedName":        get_breedname(dbo, post.integer("breed1"), post.integer("breed2")),
        "Crossbreed":       post.boolean("crossbreed"),
        "AcceptanceNumber": post["litterid"],
        "BaseColourID":     post.integer("basecolour"),
        "ShelterLocation":  shelterlocation,
        "ShelterLocationUnit": post["unit"],
        "NonShelterAnimal": post.boolean("nonshelter"),
        "CrueltyCase":      0,
        "BondedAnimalID":   0,
        "BondedAnimal2ID":  0,
        "CoatType":         post.integer("coattype"),
        "EstimatedDOB":     estimateddob,
        "Fee":              post.integer("fee"),
        "Identichipped":    post.boolean("microchipped"),
        "IdentichipNumber": post["microchipnumber"],
        "IdentichipDate":   post.date("microchipdate"),
        "IdentichipStatus": post.integer("microchipstatus"),
        "Identichip2Number":post["microchipnumber2"],
        "Identichip2Date":  post.date("microchipdate2"),
        "Identichip2Status": post.integer("microchipstatus2"),
        "Tattoo":           post.boolean("tattoo"),
        "TattooNumber":     post["tattoonumber"],
        "TattooDate":       post.date("tattoodate"),
        "SmartTag":         0,
        "SmartTagNumber":   "",
        "SmartTagType":     0,
        "Neutered":         post.boolean("neutered"),
        "NeuteredDate":     post.date("neutereddate"),
        "NeuteredByVetID":  post.integer("neuteringvet"),
        "Declawed":         post.boolean("declawed"),
        # ASM2_COMPATIBILITY
        "IsTransfer":       asm3.utils.iif(post.integer("entrytype") == 3, 1, 0),
        "HeartwormTested":  0,
        "HeartwormTestDate": None,
        "HeartwormTestResult": unknown,
        "CombiTested":      0,
        "CombiTestDate":    None,
        "CombiTestResult":  unknown,
        "FLVResult":        unknown,
        # ASM2_COMPATIBILITY
        "Markings":         post["markings"],
        "HiddenAnimalDetails": post["hiddenanimaldetails"],
        "PopupWarning":     post["popupwarning"],
        "AnimalComments":   post["comments"],
        "IsGoodWithCats":   goodwithcats,
        "IsGoodWithDogs":   goodwithdogs,
        "IsGoodWithChildren": goodwithkids,
        "IsHouseTrained":   housetrained,
        "IsCrateTrained":   cratetrained,
        "IsGoodWithElderly": goodwithelderly,
        "IsGoodTraveller":  goodtraveller,
        "IsGoodOnLead":     goodonlead,
        "EnergyLevel":      energylevel,
        "OwnerID":          post.integer("nsowner"), # only set for non-shelter
        "OriginalOwnerID":  originalowner,
        "BroughtInByOwnerID": dbb,
        "AdoptionCoordinatorID": post.integer("coordinator"),
        "ReasonNO":         "",
        "ReasonForEntry":   post["reasonforentry"],
        "EntryReasonID":    post.integer("entryreason"),
        "EntryTypeID":      post.integer("entrytype"),
        "IsPickup":         post.boolean("pickedup"),
        "PickupLocationID": post.integer("pickuplocation"),
        "PickupAddress":    post["pickupaddress"],
        "JurisdictionID":   post.integer("jurisdiction"),
        "IsHold":           post.boolean("hold"),
        "HoldUntilDate":    post.date("holduntil"),
        "IsCourtesy":       0,
        "IsQuarantine":     0,
        "AdditionalFlags":  "|",
        "DateBroughtIn":    datebroughtin,
        "AsilomarIntakeCategory": 0,
        "AsilomarIsTransferExternal": 0,
        "AsilomarOwnerRequestedEuthanasia": asm3.utils.iif(post.integer("entrytype") == 10, 1, 0),
        "HealthProblems":   post["healthproblems"],
        "HasSpecialNeeds":  post.boolean("specialneeds"),
        "RabiesTag":        "",
        "CurrentVetID":     post.integer("currentvet",0),
        "OwnersVetID":      0,
        "DeceasedDate":     deceaseddate,
        "PTSReasonID":      deathcategory,
        "PutToSleep":       post.boolean("puttosleep"),
        "IsDOA":            deadonarrival, 
        "DiedOffShelter":   0,
        "PTSReason":        post["ptsreason"],
        "IsNotAvailableForAdoption": notforadoption,
        "IsNotForRegistration": notforregistration,
        "Size":             post.integer("size"),
        "Weight":           post.floating("weight"),
        "Archived":         0,
        "ActiveMovementID": 0,
        "HasActiveReserve": 0,
        "MostRecentEntryDate": dbo.today()
    }, username, generateID=False)

    # Save any additional field values given
    asm3.additional.save_values_for_link(dbo, post, username, nextid, "animal", True)

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
            "type"                  : str(asm3.movement.FOSTER),
            "returncategory"        : asm3.configuration.default_return_reason(dbo)
        }
        asm3.movement.insert_movement_from_form(dbo, username, asm3.utils.PostedData(move_dict, l))

    # If a weight was specified and we're logging, mark it in the log
    insert_weight_log(dbo, username, nextid, post.floating("weight"), 0)

    # If the animal is held and we're logging it, mark it in the log
    if asm3.configuration.hold_change_log(dbo) and post.boolean("hold"):
        asm3.log.add_log(dbo, username, asm3.log.ANIMAL, nextid, asm3.configuration.hold_change_log_type(dbo),
            _("Hold until {0}", l).format(post["holduntil"]))

    # Do we have a matching template animal we can copy some satellite info from?
    # Only do it if this animal is a shelter animal or if the override is on to force
    # templates for non-shelter animals.
    if not post.boolean("nonshelter") or asm3.configuration.templates_for_nonshelter(dbo):
        clone_from_template(dbo, username, nextid, datebroughtin, dob, post.integer("animaltype"), post.integer("species"), post.boolean("nonshelter"))

    return (nextid, get_code(dbo, nextid))

def update_animal_from_form(dbo: Database, post: PostedData, username: str) -> None:
    """
    Updates an animal record from the edit animal screen
    data: The webpy data object containing form parameters
    """
    l = dbo.locale
    aid = post.integer("id")

    # Optimistic lock check
    if not dbo.optimistic_check("animal", aid, post.integer("recordversion")):
        raise asm3.utils.ASMValidationError(_("This record has been changed by another user, please reload.", l))

    # Validate form fields
    if post["animalname"] == "":
        raise asm3.utils.ASMValidationError(_("Name cannot be blank", l))
    if post["dateofbirth"] == "":
        raise asm3.utils.ASMValidationError(_("Date of birth cannot be blank", l))
    if post.date("dateofbirth") is None:
        raise asm3.utils.ASMValidationError(_("Date of birth is not valid", l))
    if post.date("dateofbirth") > dbo.today():
        raise asm3.utils.ASMValidationError(_("Date of birth cannot be in the future.", l))
    if post["datebroughtin"] == "":
        raise asm3.utils.ASMValidationError(_("Date brought in cannot be blank", l))
    if post.datetime("datebroughtin", "timebroughtin") is None:
        raise asm3.utils.ASMValidationError(_("Date brought in is not valid", l))
    if post.datetime("datebroughtin", "timebroughtin") > dbo.today(offset=30):
        raise asm3.utils.ASMValidationError(_("Date brought in cannot be in the future.", l))
    if post["sheltercode"] == "":
        raise asm3.utils.ASMValidationError(_("Shelter code cannot be blank", l))
    if dbo.query_int("SELECT COUNT(ID) FROM animal WHERE ShelterCode Like ? AND ID <> ?", (post["sheltercode"], aid)) > 0:
        raise asm3.utils.ASMValidationError(_("Shelter code {0} has already been allocated to another animal.", l).format(post["sheltercode"]))
    if post["microchipnumber"].strip() != "" and not asm3.configuration.allow_duplicate_microchip(dbo):
        if dbo.query_int("SELECT COUNT(ID) FROM animal WHERE IdentichipNumber Like ? AND ID <> ?", (post["microchipnumber"], aid)) > 0:
            raise asm3.utils.ASMValidationError(_("Microchip number {0} has already been allocated to another animal.", l).format(post["microchipnumber"]))
    if post["deceaseddate"] != "" and "nonshelter" not in post["flags"].split(","):
        deceaseddate = post.date("deceaseddate")
        datebroughtin = post.date("datebroughtin")
        if deceaseddate is not None and datebroughtin is not None and deceaseddate < datebroughtin:
            raise asm3.utils.ASMValidationError(_("Animal cannot be deceased before it was brought to the shelter", l))

    # Look up the row pre-change so that we can see if any log messages need to be triggered
    prerow = dbo.first_row(dbo.query("SELECT DeceasedDate, ShelterLocation, ShelterLocationUnit, Weight, IsHold, AdditionalFlags, AnimalName FROM animal WHERE ID=?", [aid]))

    # Record the location if it has changed
    insert_animallocation(dbo, username, aid, post["animalname"], post["sheltercode"], prerow.shelterlocation, prerow.shelterlocationunit, post.integer("location"), post["unit"])

    # If the option is on and the hold status has changed, log it
    if asm3.configuration.hold_change_log(dbo):
        if prerow.ISHOLD == 0 and post.boolean("hold"):
            asm3.log.add_log(dbo, username, asm3.log.ANIMAL, aid, asm3.configuration.hold_change_log_type(dbo),
                _("Hold until {0}", l).format(post["holduntil"]))

    # If the option is on and the name has changed, log it
    insert_namechange_log(dbo, username, aid, post["animalname"], prerow.ANIMALNAME)

    # If the option is on and the weight has changed, log it
    insert_weight_log(dbo, username, aid, post.floating("weight"), prerow.WEIGHT)

    # If the animal is newly deceased, mark any diary notes completed
    if post.date("deceaseddate") is not None and asm3.configuration.diary_complete_on_death(dbo):
        if prerow.DECEASEDDATE != post.date("deceaseddate"):
            asm3.diary.complete_diary_notes_for_animal(dbo, username, aid)

    # Sort out any flags
    def bi(b): 
        return b and 1 or 0

    flags = post["flags"].split(",")
    courtesy = bi("courtesy" in flags)
    crueltycase = bi("crueltycase" in flags)
    notforadoption = bi("notforadoption" in flags)
    notforregistration = bi("notforregistration" in flags)
    nonshelter = bi("nonshelter" in flags)
    quarantine = bi("quarantine" in flags)
    flagstr = "|".join(flags) + "|"

    # If the option is on and the flags have changed, log it
    if asm3.configuration.animal_flag_change_log(dbo):
        if flagstr != prerow.ADDITIONALFLAGS:
            asm3.log.add_log(dbo, username, asm3.log.ANIMAL, aid, asm3.configuration.animal_flag_change_log_type(dbo),
                _("Flags changed from '{0}' to '{1}'", l).format(prerow.ADDITIONALFLAGS, flagstr))

    # If the animal is non-shelter, make sure that any movements are returned on the same
    # day. Non shelter animals don't have visible movements and this prevents a bug where
    # an open foster/retailer movement on a non-shelter animal can make it publish for adoption
    # when the "include fosters/retailers" publishing options are on.
    if nonshelter == 1:
        dbo.execute("UPDATE adoption SET ReturnDate = MovementDate WHERE MovementType IN (2,8) AND AnimalID = ?", [aid])

    dbo.update("animal", aid, {
        "NonShelterAnimal":     nonshelter,
        "IsNotAvailableForAdoption": notforadoption,
        "IsNotForRegistration": notforregistration,
        "IsQuarantine":         quarantine,
        "IsCourtesy":           courtesy,
        "CrueltyCase":          crueltycase,
        "AdditionalFlags":      flagstr,
        "ShelterCode":          post["sheltercode"],
        "ShortCode":            post["shortcode"],
        "UniqueCodeID":         post.integer("uniquecode"),
        "YearCodeID":           post.integer("yearcode"),
        "AcceptanceNumber":     post["litterid"],
        "AnimalName":           post["animalname"],
        "Sex":                  post.integer("sex"),
        "AnimalTypeID":         post.integer("animaltype"),
        "BaseColourID":         post.integer("basecolour"),
        "CoatType":             post.integer("coattype"),
        "Size":                 post.integer("size"),
        "Weight":               post.floating("weight"),
        "SpeciesID":            post.integer("species"),
        "BreedID":              post.integer("breed1"),
        "Breed2ID":             post.integer("breed2"),
        "BreedName":            get_breedname(dbo, post.integer("breed1"), post.integer("breed2")),
        "Crossbreed":           post.boolean("crossbreed"),
        "ShelterLocation":      post.integer("location"),
        "ShelterLocationUnit":  post["unit"],
        "DateOfBirth":          post.date("dateofbirth"),
        "EstimatedDOB":         post.boolean("estimateddob"),
        "Fee":                  post.integer("fee"),
        "Identichipped":        post.boolean("microchipped"),
        "IdentichipDate":       post.date("microchipdate"),
        "IdentichipStatus":     post.integer("microchipstatus"),
        "IdentichipNumber":     post["microchipnumber"],
        "Identichip2Date":      post.date("microchipdate2"),
        "Identichip2Status":    post.integer("microchipstatus2"),
        "Identichip2Number":    post["microchipnumber2"],
        "Tattoo":               post.boolean("tattoo"),
        "TattooDate":           post.date("tattoodate"),
        "TattooNumber":         post["tattoonumber"],
        "SmartTag":             post.boolean("smarttag"),
        "SmartTagNumber":       post["smarttagnumber"],
        "SmartTagType":         post.integer("smarttagtype"),
        "Neutered":             post.boolean("neutered"),
        "NeuteredDate":         post.date("neutereddate"),
        "NeuteredByVetID":      post.integer("neuteringvet"),
        "Declawed":             post.boolean("declawed"),
        # ASM2_COMPATIBILITY
        "IsTransfer":           asm3.utils.iif(post.integer("entrytype") == 3, 1, 0),
        "HeartwormTested":      post.boolean("heartwormtested"),
        "HeartwormTestDate":    post.date("heartwormtestdate"),
        "HeartwormTestResult":  post.integer("heartwormtestresult"),
        "CombiTested":          post.boolean("fivltested"),
        "CombiTestDate":        post.date("fivltestdate"),
        "CombiTestResult":      post.integer("fivresult"),
        "FLVResult":            post.integer("flvresult"),
        # ASM2_COMPATIBILITY
        "Markings":             post["markings"],
        "HiddenAnimalDetails":  post["hiddencomments"],
        "PopupWarning":         post["popupwarning"],
        "AnimalComments":       post["comments"],
        "IsGoodWithCats":       post.integer("goodwithcats"),
        "IsGoodWithDogs":       post.integer("goodwithdogs"),
        "IsGoodWithChildren":   post.integer("goodwithkids"),
        "IsHouseTrained":       post.integer("housetrained"),
        "IsCrateTrained":       post.integer("cratetrained"),
        "IsGoodWithElderly":    post.integer("goodwithelderly"),
        "IsGoodTraveller":      post.integer("goodtraveller"),
        "IsGoodOnLead":         post.integer("goodonlead"),
        "EnergyLevel":          post.integer("energylevel"),
        "OwnerID":              post.integer("owner"),
        "OriginalOwnerID":      post.integer("originalowner"),
        "BroughtInByOwnerID":   post.integer("broughtinby"),
        "AdoptionCoordinatorID": post.integer("adoptioncoordinator"),
        "BondedAnimalID":       post.integer("bonded1"),
        "BondedAnimal2ID":      post.integer("bonded2"),
        "ReasonNO":             post["reasonnotfromowner"],
        "ReasonForEntry":       post["reasonforentry"],
        "EntryReasonID":        post.integer("entryreason"),
        "EntryTypeID":          post.integer("entrytype"),
        "IsHold":               post.boolean("hold"),
        "HoldUntilDate":        post.date("holduntil"),
        "IsPickup":             post.boolean("pickedup"),
        "PickupLocationID":     post.integer("pickuplocation"),
        "PickupAddress":        post["pickupaddress"],
        "JurisdictionID":       post.integer("jurisdiction"),
        "DateBroughtIn":        post.datetime("datebroughtin", "timebroughtin"),
        "AsilomarIntakeCategory": post.integer("asilomarintakecategory"),
        "AsilomarIsTransferExternal": post.boolean("asilomartransferexternal"),
        "AsilomarOwnerRequestedEuthanasia": asm3.utils.iif(post.integer("entrytype") == 10, 1, 0),
        "HealthProblems":       post["healthproblems"],
        "HasSpecialNeeds":      post.boolean("specialneeds"),
        "RabiesTag":            post["rabiestag"],
        "CurrentVetID":         post.integer("currentvet"),
        "OwnersVetID":          post.integer("ownersvet"),
        "DeceasedDate":         post.date("deceaseddate"),
        "PTSReasonID":          post.integer("deathcategory"),
        "PutToSleep":           post.boolean("puttosleep"),
        "IsDOA":                post.boolean("deadonarrival"),
        "PTSReason":            post["ptsreason"]
    }, username)

    # Save any additional field values given
    asm3.additional.save_values_for_link(dbo, post, username, aid, "animal")

    # Update denormalised fields after the change
    update_animal_check_bonds(dbo, aid)
    update_animal_status(dbo, aid)
    update_variable_animal_data(dbo, aid)

    # Update any diary notes linked to this animal
    update_diary_linkinfo(dbo, aid)

    # If this animal is part of a litter, update its counts
    if post["litterid"] != "":
        update_litter_count(dbo, post["litterid"])

def update_flags(dbo: Database, username: str, animalid: int, flags: List[str]) -> None:
    """
    Updates the animal flags from a list of flags
    """
    def bi(b): 
        return b and 1 or 0

    courtesy = bi("courtesy" in flags)
    crueltycase = bi("crueltycase" in flags)
    notforadoption = bi("notforadoption" in flags)
    notforregistration = bi("notforregistration" in flags)
    nonshelter = bi("nonshelter" in flags)
    quarantine = bi("quarantine" in flags)
    flagstr = "|".join(flags) + "|"

    dbo.update("animal", animalid, {
        "NonShelterAnimal":             nonshelter,
        "IsNotAvailableForAdoption":    notforadoption,
        "IsNotForRegistration":         notforregistration,
        "IsQuarantine":                 quarantine,
        "IsCourtesy":                   courtesy,
        "CrueltyCase":                  crueltycase,
        "AdditionalFlags":              flagstr
    }, username)

def update_animals_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Batch updates multiple animal records from the bulk form.
    Returns number of animals affected.
    """
    if len(post.integer_list("animals")) == 0: return 0
    aud = []
    if post["litterid"] != "":
        dbo.execute("UPDATE animal SET AcceptanceNumber = %s WHERE ID IN (%s)" % (dbo.sql_value(post["litterid"]), post["animals"]))
        aud.append("LitterID = %s" % post["litterid"])
    if post.integer("animaltype") != -1:
        dbo.execute("UPDATE animal SET AnimalTypeID = %d WHERE ID IN (%s)" % (post.integer("animaltype"), post["animals"]))
        aud.append("AnimalTypeID = %s" % post["animaltype"])
    if post.integer("location") != -1 and post["unit"] != "-1":
        for animalid in post.integer_list("animals"):
            update_location_unit(dbo, username, animalid, post.integer("location"), post["unit"])
    elif post.integer("location") != -1:
        dbo.execute("UPDATE animal SET ShelterLocation = %d WHERE ID IN (%s)" % (post.integer("location"), post["animals"]))
        aud.append("ShelterLocation = %s" % post["location"])
    elif post["unit"] != "-1":
        dbo.execute("UPDATE animal SET ShelterLocationUnit = %s WHERE ID IN (%s)" % (dbo.sql_value(post["unit"]), post["animals"]))
        aud.append("ShelterLocationUnit = %s" % post["unit"])
    if post.integer("entryreason") != -1:
        dbo.execute("UPDATE animal SET EntryReasonID = %d WHERE ID IN (%s)" % (post.integer("entryreason"), post["animals"]))
        aud.append("EntryReasonID = %s" % post["entryreason"])
    if post.integer("fee") > 0:
        dbo.execute("UPDATE animal SET Fee = %d WHERE ID IN (%s)" % (post.integer("fee"), post["animals"]))
        aud.append("Fee = %s" % post["fee"])
    if post.integer("boardingcost") > 0:
        dbo.execute("UPDATE animal SET DailyBoardingCost = %d WHERE ID IN (%s)" % (post.integer("boardingcost"), post["animals"]))
        aud.append("DailyBoardingCost = %s" % post["boardingcost"])
    if post.integer("notforadoption") != -1:
        dbo.execute("UPDATE animal SET IsNotAvailableForAdoption = %d WHERE ID IN (%s)" % (post.integer("notforadoption"), post["animals"]))
        aud.append("IsNotAvailableForAdoption = %s" % post["notforadoption"])
    if post.integer("notforregistration") != -1:
        dbo.execute("UPDATE animal SET IsNotForRegistration = %d WHERE ID IN (%s)" % (post.integer("notforregistration"), post["animals"]))
        aud.append("IsNotForRegistration = %s" % post["notforregistration"])
    if post["holduntil"] != "":
        dbo.execute("UPDATE animal SET IsHold = 1, HoldUntilDate = %s WHERE ID IN (%s)" % (dbo.sql_date(post.date("holduntil")), post["animals"]))
        aud.append("HoldUntilDate = %s" % post["holduntil"])
    if post.integer("goodwithcats") != -1:
        dbo.execute("UPDATE animal SET IsGoodWithCats = %d WHERE ID IN (%s)" % (post.integer("goodwithcats"), post["animals"]))
        aud.append("IsGoodWithCats = %s" % post["goodwithcats"])
    if post.integer("goodwithdogs") != -1:
        dbo.execute("UPDATE animal SET IsGoodWithDogs = %d WHERE ID IN (%s)" % (post.integer("goodwithdogs"), post["animals"]))
        aud.append("IsGoodWithDogs = %s" % post["goodwithdogs"])
    if post.integer("goodwithkids") != -1:
        dbo.execute("UPDATE animal SET IsGoodWithChildren = %d WHERE ID IN (%s)" % (post.integer("goodwithkids"), post["animals"]))
        aud.append("IsGoodWithChildren = %s" % post["goodwithkids"])
    if post.integer("goodwithelderly") != -1:
        dbo.execute("UPDATE animal SET IsGoodWithElderly = %d WHERE ID IN (%s)" % (post.integer("goodwithelderly"), post["animals"]))
        aud.append("IsGoodWithElderly = %s" % post["goodwithelderly"])
    if post.integer("goodonlead") != -1:
        dbo.execute("UPDATE animal SET IsGoodOnLead = %d WHERE ID IN (%s)" % (post.integer("goodonlead"), post["animals"]))
        aud.append("IsGoodOnLead = %s" % post["goodonlead"])
    if post.integer("goodtraveller") != -1:
        dbo.execute("UPDATE animal SET IsGoodTraveller = %d WHERE ID IN (%s)" % (post.integer("goodtraveller"), post["animals"]))
        aud.append("IsGoodTraveller = %s" % post["goodtraveller"])
    if post.integer("housetrained") != -1:
        dbo.execute("UPDATE animal SET IsHouseTrained = %d WHERE ID IN (%s)" % (post.integer("housetrained"), post["animals"]))
        aud.append("IsHouseTrained = %s" % post["housetrained"])
    if post.integer("cratetrained") != -1:
        dbo.execute("UPDATE animal SET IsCrateTrained = %d WHERE ID IN (%s)" % (post.integer("cratetrained"), post["animals"]))
        aud.append("IsCrateTrained = %s" % post["cratetrained"])
    if post.integer("energylevel") != -1:
        dbo.execute("UPDATE animal SET EnergyLevel = %d WHERE ID IN (%s)" % (post.integer("energylevel"), post["animals"]))
        aud.append("EnergyLevel = %s" % post["energylevel"])
    if post["neutereddate"] != "":
        dbo.execute("UPDATE animal SET Neutered = 1, NeuteredDate = %s WHERE ID IN (%s)" % (dbo.sql_date(post.date("neutereddate")), post["animals"]))
        aud.append("NeuteredDate = %s" % post["neutereddate"])
    if post["neuteringvet"] != "" and post["neuteringvet"] != "0":
        dbo.execute("UPDATE animal SET NeuteredByVetID = %d WHERE ID IN (%s)" % (post.integer("neuteringvet"), post["animals"]))
        aud.append("NeuteredByVetID = %s" % post["neuteringvet"])
    if post["currentvet"] != "" and post["currentvet"] != "0":
        dbo.execute("UPDATE animal SET CurrentVetID = %d WHERE ID IN (%s)" % (post.integer("currentvet"), post["animals"]))
        aud.append("CurrentVetID = %s" % post["currentvet"])
    if post["ownersvet"] != "" and post["ownersvet"] != "0":
        dbo.execute("UPDATE animal SET OwnersVetID = %d WHERE ID IN (%s)" % (post.integer("ownersvet"), post["animals"]))
        aud.append("OwnersVetID = %s" % post["ownersvet"])
    if post["coordinator"] != "" and post["coordinator"] != "0":
        dbo.execute("UPDATE animal SET AdoptionCoordinatorID = %d WHERE ID IN (%s)" % (post.integer("coordinator"), post["animals"]))
        aud.append("AdoptionCoordinatorID = %s" % post["coordinator"])
    if post["addflag"] != "":
        animals = dbo.query("SELECT ID, AdditionalFlags FROM animal WHERE ID IN (%s)" % post["animals"])
        for a in animals:
            if not a.additionalflags: a.additionalflags = ""
            if a.additionalflags.find("%s|" % post["addflag"]) == -1:
                newflags = "%s%s|" % (a.additionalflags, post["addflag"])
                dbo.update("animal", a["ID"], { "AdditionalFlags": newflags })
                aud.append("AdditionalFlags %s --> %s" % (a.additionalflags, newflags))
    if post["removeflag"] != "":
        animals = dbo.query("SELECT ID, AdditionalFlags FROM animal WHERE ID IN (%s)" % post["animals"])
        for a in animals:
            if not a.additionalflags: a.additionalflags = ""
            fs = "%s|" % post["removeflag"]
            if a.additionalflags.find(fs) != -1:
                newflags = a.additionalflags.replace(fs, "")
                dbo.update("animal", a["ID"], { "AdditionalFlags": newflags })
                aud.append("AdditionalFlags %s --> %s" % (a.additionalflags, newflags))
    if post["diaryfor"] != "" and post.date("diarydate") is not None and post["diarysubject"] != "":
        for animalid in post.integer_list("animals"):
            asm3.diary.insert_diary(dbo, username, asm3.diary.ANIMAL, animalid, post.datetime("diarydate", "diarytime"), 
                post["diaryfor"], post["diarysubject"], post["diarynotes"])
    if post.integer("logtype") != -1:
        for animalid in post.integer_list("animals"):
            asm3.log.add_log(dbo, username, asm3.log.ANIMAL, animalid, post.integer("logtype"), post["lognotes"], post.date("logdate") )
    if post.integer("movementtype") != -1:
        default_return_reason = asm3.configuration.default_return_reason(dbo)
        for animalid in post.integer_list("animals"):
            move_dict = {
                "person"                : post["moveto"],
                "animal"                : str(animalid),
                "adoptionno"            : "",
                "returndate"            : "",
                "type"                  : post["movementtype"],
                "donation"              : "0",
                "returncategory"        : str(default_return_reason)
            }
            # If this is a non-reserve, return any existing foster first
            if post.integer("movementtype") > 0:
                fm = asm3.movement.get_animal_movements(dbo, animalid)
                for m in fm:
                    if m.movementtype == asm3.movement.FOSTER and not m.returndate:
                        asm3.movement.return_movement(dbo, m["ID"], username, animalid, post.date("movementdate"))
                move_dict["movementdate"] = post["movementdate"]
            else:
                move_dict["reservationstatus"] = asm3.configuration.default_reservation_status(dbo)
                move_dict["reservationdate"] = post["movementdate"]
            asm3.movement.insert_movement_from_form(dbo, username, asm3.utils.PostedData(move_dict, dbo.locale))
    
    if post.integer("additionalfield") != -1:
        for animalid in post.integer_list("animals"):
            asm3.additional.insert_additional(dbo, asm3.additional.ANIMAL, animalid, post.integer("additionalfield"), post["additionalvalue"])
    
    # Record the user as making the last change to this record and create audit records for the changes
    dbo.execute("UPDATE animal SET LastChangedBy = %s, LastChangedDate = %s WHERE ID IN (%s)" % (dbo.sql_value(username), dbo.sql_now(), post["animals"]))
    if len(aud) > 0:
        for animalid in post.integer_list("animals"):
            asm3.audit.edit(dbo, username, "animal", animalid, "", ", ".join(aud))
    return len(post.integer_list("animals"))

def update_deceased_from_form(dbo: Database, username: str, post: PostedData) -> None:
    """
    Sets an animal's deceased information from the move_deceased form
    """
    animalid = post.integer("animal")
    dbo.update("animal", animalid, {
        "DeceasedDate":     post.date("deceaseddate"),
        "PTSReasonID":      post.integer("deathcategory"),
        "PutToSleep":       post.boolean("puttosleep"),
        "IsDOA":            post.boolean("deadonarrival"),
        "PTSReason":        post["ptsreason"]
    }, username)
    # Update denormalised fields after the deceased change
    update_animal_status(dbo, animalid)
    update_variable_animal_data(dbo, animalid)
    # Close any diary notes related to this animal
    asm3.diary.complete_diary_notes_for_animal(dbo, username, animalid)

def send_email_from_form(dbo: Database, username: str, post: PostedData) -> bool:
    """
    Sends an email related to an animal from a posted form. 
    Attaches it as a log entry if specified.
    Returns the bool value from send_email (True for success)
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
        asm3.log.add_log_email(dbo, username, asm3.log.ANIMAL, post.integer("animalid"), logtype, emailto, subject, body)
    return rv

def update_diary_linkinfo(dbo: Database, animalid: int, a: ResultRow = None, diaryupdatebatch: List[Tuple] = None) -> None:
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
    diaryloc = "%s - %s [%s]" % ( a.sheltercode, a.animalname, get_display_location_noq(dbo, animalid, a.displaylocation))
    if diaryupdatebatch is not None:
        diaryupdatebatch.append( (diaryloc, asm3.diary.ANIMAL, animalid) )
    else:
        dbo.execute("UPDATE diary SET LinkInfo = ? WHERE LinkType = ? AND LinkID = ?", (diaryloc, asm3.diary.ANIMAL, animalid))

def insert_animallocation(dbo: Database, username: str, animalid: int, animalname: str, sheltercode: str, 
                          fromid: int, fromunit: str, toid: int, tounit: str) -> int:
    """
    Adds a new entry to the animallocation table when an animal changes internal location.
    Also handles writing to the log if the option is on.
    """
    l = dbo.locale
    # Squash nulls. Shouldn't really get these, but old ASM2 imports can sometimes have them
    if fromunit is None: fromunit = ""
    if tounit is None: tounit = ""
    # If the location hasn't changed, don't do anything
    if fromid == toid and fromunit == tounit: return
    fromlocation = dbo.query_string("SELECT LocationName FROM internallocation WHERE ID = ?", [fromid])
    tolocation = dbo.query_string("SELECT LocationName FROM internallocation WHERE ID = ?", [toid])
    if fromunit != "":
        fromlocation += "-" + fromunit
    if tounit != "":
        tolocation += "-" + tounit
    prevlocationid = dbo.query_int("SELECT ID FROM animallocation WHERE AnimalID=? " \
        "AND ToLocationID=? AND ToUnit=? ORDER BY Date DESC", [ animalid, fromid, fromunit])
    msg = _("{0} {1}: Moved from {2} to {3}", l).format(sheltercode, animalname, fromlocation, tolocation)
    alid = dbo.insert("animallocation", {
        "AnimalID":         animalid,
        "Date":             dbo.now(),
        "FromLocationID":   fromid,
        "FromUnit":         fromunit,
        "ToLocationID":     toid,
        "ToUnit":           tounit,
        "PrevAnimalLocationID": prevlocationid,
        "MovedBy":          username,
        "Description":      msg
    }, username, setCreated = False)
    if asm3.configuration.location_change_log(dbo):
        asm3.log.add_log(dbo, username, asm3.log.ANIMAL, animalid, asm3.configuration.location_change_log_type(dbo), msg)
    return alid

def insert_namechange_log(dbo: Database, username: str, animalid: int, newname: str, oldname: str) -> None:
    """ Writes an entry to the log when an animal's name changes."""
    # If the option is on and the name has changed, log it
    l = dbo.locale
    if asm3.configuration.animalname_change_log(dbo):
        if newname != oldname:
            asm3.log.add_log(dbo, username, asm3.log.ANIMAL, animalid, asm3.configuration.animalname_change_log_type(dbo),
                _("Name changed from '%s' to '%s'", l) % (oldname, newname))

def insert_weight_log(dbo: Database, username: str, animalid: int, newweight: float = 0, oldweight: float = -1) -> None:
    """ Writes an entry to the log when an animal's weight changes. 
        This should be called before the weight on the animal record is updated so it can check if the weight changed. """
    # If the option is on and the weight has changed, log it
    if asm3.configuration.weight_change_log(dbo) and newweight > 0:
        if oldweight < 0: 
            oldweight = dbo.query_float("SELECT Weight FROM animal WHERE ID = ?", [animalid])
        if newweight != oldweight:
            units = ""
            if asm3.configuration.show_weight_units_in_log(dbo):
                units = (asm3.configuration.show_weight_in_lbs(dbo) or asm3.configuration.show_weight_in_lbs_fraction(dbo)) and " lb" or " kg"
            asm3.log.add_log(dbo, username, asm3.log.ANIMAL, animalid, asm3.configuration.weight_change_log_type(dbo),
                "%s%s" % (newweight, units))

def update_location_unit(dbo: Database, username: str, animalid: int, newlocationid: int, newunit: str = "", returnactivemovement: bool = True) -> None:
    """
    Updates the shelterlocation and shelterlocationunit fields of the animal given.
    This is typically called in response to drag and drop events on shelterview and
    means that the animal should be on shelter rather than with a fosterer, etc.
    If the animal has an activemovement, it will be returned before the location is changed.
    """
    # Record the internal location change if necessary
    oldloc = dbo.first_row( dbo.query("SELECT ShelterCode, AnimalName, ShelterLocation, ShelterLocationUnit FROM animal WHERE ID=?", [animalid]) )
    if oldloc:
        insert_animallocation(dbo, username, animalid, oldloc.animalname, oldloc.sheltercode, 
                              oldloc.shelterlocation, oldloc.shelterlocationunit, newlocationid, newunit)
    # If this animal has an active movement at today's date or older, return it first
    # (the date check is to make sure we don't accidentally return future adoptions)
    if returnactivemovement:
        activemovementid = dbo.query_int("SELECT ActiveMovementID FROM animal WHERE ID = ? AND ActiveMovementID > 0 AND ActiveMovementDate <= ?", (animalid, dbo.today()))
        if activemovementid > 0:
            asm3.movement.return_movement(dbo, activemovementid, username, animalid)
    # Change the location
    dbo.execute("UPDATE animal SET ShelterLocation = ?, ShelterLocationUnit = ? WHERE ID = ?", (newlocationid, newunit, animalid))
    asm3.audit.edit(dbo, username, "animal", animalid, "", "%s: moved to location: %s, unit: %s" % ( animalid, newlocationid, newunit ))
    update_animal_status(dbo, animalid)

def clone_animal(dbo: Database, username: str, animalid: int) -> int:
    """
    Clones an animal and its satellite records.
    Returns the ID of the new animal.
    """
    l = dbo.locale
    a = get_animal(dbo, animalid)
    sheltercode, shortcode, unique, year = calc_shelter_code(dbo, a.animaltypeid, a.entryreasonid, a.speciesid, a.datebroughtin)
    nid = dbo.insert("animal", {
        "AnimalTypeID":     a.animaltypeid,
        "ShelterCode":      sheltercode,
        "ShortCode":        shortcode,
        "UniqueCodeID":     unique,
        "YearCodeID":       year,
        "AnimalName":       _("Copy of {0}", l).format(a.animalname),
        "NonShelterAnimal": a.nonshelteranimal,
        "CrueltyCase":      a.crueltycase,
        "BaseColourID":     a.basecolourid,
        "SpeciesID":        a.speciesid,
        "BreedID":          a.breedid, 
        "Breed2ID":         a.breed2id, 
        "BreedName":        a.breedname,
        "CrossBreed":       a.crossbreed,
        "CoatType":         a.coattype,
        "Markings":         a.markings,
        "AcceptanceNumber": a.acceptancenumber,
        "DateOfBirth":      a.dateofbirth,
        "EstimatedDOB":     a.estimateddob,
        "Fee":              a.fee,
        "AgeGroup":         a.agegroup,
        "DeceasedDate":     a.deceaseddate, 
        "Sex":              a.sex,
        "Identichipped":    a.identichipped,
        "IdentichipNumber": asm3.configuration.allow_duplicate_microchip(dbo) and a.identichipnumber or "",
        "Identichip2Number": asm3.configuration.allow_duplicate_microchip(dbo) and a.identichip2number or "",
        "Tattoo":           a.tattoo,
        "TattooNumber":     "",
        "Neutered":         a.neutered, 
        "NeuteredDate":     a.neutereddate,
        # ASM2_COMPATIBILITY
        "CombiTested":      a.combitested,
        "CombiTestDate":    a.combitestdate,
        "CombiTestResult":  a.combitestresult,
        "FLVResult":        a.flvresult,
        "HeartwormTested":  a.heartwormtested,
        "HeartwormTestDate": a.heartwormtestdate,
        "HeartwormTestResult": a.heartwormtestresult,
        # ASM2_COMPATIBILITY
        "SmartTag":         0,
        "SmartTagNumber":   "",
        "SmartTagType":     0,
        "Declawed":         a.declawed,
        "HiddenAnimalDetails": a.hiddenanimaldetails,
        "PopupWarning":     a.popupwarning,
        "AnimalComments":   a.animalcomments,
        "OwnersVetID":      a.ownersvetid,
        "CurrentVetID":     a.currentvetid,
        "OriginalOwnerID":  a.originalownerid,
        "BroughtInByOwnerID": a.broughtinbyownerid,
        "AdoptionCoordinatorID": a.adoptioncoordinatorid,
        "ReasonForEntry":   a.reasonforentry,
        "ReasonNO":         a.reasonno,
        "DateBroughtIn":    a.datebroughtin,
        "EntryReasonID":    a.entryreasonid,
        "EntryTypeID":      a.entrytypeid,
        "AsilomarIsTransferExternal": a.asilomaristransferexternal,
        "AsilomarIntakeCategory": a.asilomarintakecategory,
        "AsilomarOwnerRequestedEuthanasia": a.asilomarownerrequestedeuthanasia,
        "HealthProblems":   a.healthproblems, 
        "PutToSleep":       a.puttosleep,
        "PTSReason":        a.ptsreason, 
        "PTSReasonID":      a.ptsreasonid, 
        "IsDOA":            a.isdoa, 
        "IsTransfer":       a.istransfer,
        "IsPickup":         a.ispickup,
        "PickupLocationID": a.pickuplocationid,
        "PickupAddress":    a.pickupaddress,
        "JurisdictionID":   a.jurisdictionid,
        "IsGoodWithCats":   a.isgoodwithcats,
        "IsGoodWithDogs":   a.isgoodwithdogs,
        "IsGoodWithChildren": a.isgoodwithchildren,
        "IsHouseTrained":   a.ishousetrained,
        "IsCrateTrained":   a.iscratetrained,
        "IsGoodWithElderly": a.isgoodwithelderly,
        "IsGoodTraveller":  a.isgoodtraveller,
        "IsGoodOnLead":     a.isgoodonlead,
        "EnergyLevel":      a.energylevel,
        "IsNotAvailableForAdoption": a.isnotavailableforadoption,
        "IsHold":           a.ishold,
        "AdditionalFlags":  a.additionalflags, 
        "HoldUntilDate":    a.holduntildate,
        "IsQuarantine":     a.isquarantine,
        "HasSpecialNeeds":  a.hasspecialneeds,
        "ShelterLocation":  a.shelterlocation,
        "ShelterLocationUnit": a.shelterlocationunit,
        "Size":             a.size,
        "Weight":           0,
        "RabiesTag":        a.rabiestag,
        "BondedAnimalID":   0,
        "BondedAnimal2ID":  0,
        "Archived":         0,
        "ActiveMovementID": 0,
        "ActiveMovementType": 0,
        "DiedOffShelter":   a.diedoffshelter,
        "HasActiveReserve": 0,
        "MostRecentEntryDate": a.mostrecententrydate
    }, username, writeAudit=False)
    # Additional Fields
    for af in dbo.query("SELECT * FROM additional WHERE LinkID = %d AND LinkType IN (%s)" % (animalid, asm3.additional.ANIMAL_IN)):
        asm3.additional.insert_additional(dbo, af.linktype, nid, af.additionalfieldid, af.value)
    # Vaccinations
    for v in dbo.query("SELECT * FROM animalvaccination WHERE AnimalID = ?", [animalid]):
        dbo.insert("animalvaccination", {
            "AnimalID":             nid,
            "VaccinationID":        v.vaccinationid,
            "DateOfVaccination":    v.dateofvaccination,
            "DateRequired":         v.daterequired,
            "DateExpires":          v.dateexpires,
            "BatchNumber":          v.batchnumber,
            "AdministeringVetID":   v.administeringvetid,
            "Manufacturer":         v.manufacturer,
            "Cost":                 v.cost,
            "Comments":             v.comments
        }, username, writeAudit=False)
    # Tests
    for t in dbo.query("SELECT * FROM animaltest WHERE AnimalID = ?", [animalid]):
        dbo.insert("animaltest", {
            "AnimalID":             nid,
            "TestTypeID":           t.testtypeid,
            "TestResultID":         t.testresultid,
            "DateOfTest":           t.dateoftest,
            "DateRequired":         t.daterequired,
            "AdministeringVetID":   t.administeringvetid,
            "Cost":                 t.cost,
            "Comments":             t.comments
        }, username, writeAudit=False)
    # Medical
    for am in dbo.query("SELECT * FROM animalmedical WHERE AnimalID = ?", [animalid]):
        namid = dbo.insert("animalmedical", {
            "AnimalID":             nid,
            "MedicalProfileID":     am.medicalprofileid,
            "TreatmentName":        am.treatmentname,
            "StartDate":            am.startdate,
            "Dosage":               am.dosage,
            "Cost":                 am.cost,
            "CostPerTreatment":     am.costpertreatment,
            "TimingRule":           am.timingrule,
            "TimingRuleFrequency":  am.timingrulefrequency,
            "TimingRuleNoFrequencies": am.timingrulenofrequencies,
            "TreatmentRule":        am.treatmentrule,
            "TotalNumberOfTreatments": am.totalnumberoftreatments,
            "TreatmentsGiven":      am.treatmentsgiven,
            "TreatmentsRemaining":  am.treatmentsremaining,
            "Status":               am.status,
            "Comments":             am.comments
        }, username, writeAudit=False)
        for amt in dbo.query("SELECT * FROM animalmedicaltreatment WHERE AnimalMedicalID = ?", [am.id]):
            dbo.insert("animalmedicaltreatment", {
                "AnimalID":         nid,
                "AnimalMedicalID":  namid,
                "DateRequired":     amt.daterequired,
                "DateGiven":        amt.dategiven,
                "TreatmentNumber":  amt.treatmentnumber,
                "TotalTreatments":  amt.totaltreatments,
                "AdministeringVetID": amt.administeringvetid,
                "GivenBy":          amt.givenby,
                "Comments":         amt.comments
            }, username, writeAudit=False)
    # Diet
    for d in dbo.query("SELECT * FROM animaldiet WHERE AnimalID = ?", [animalid]):
        dbo.insert("animaldiet", {
            "AnimalID":             nid,
            "DietID":               d.dietid,
            "DateStarted":          d.datestarted,
            "Comments":             d.comments
        }, username, writeAudit=False)
    # Costs
    for c in dbo.query("SELECT * FROM animalcost WHERE AnimalID = ?", [animalid]):
        dbo.insert("animalcost", {
            "AnimalID":             nid,
            "OwnerID":              c.ownerid,
            "InvoiceNumber":        c.invoicenumber,
            "CostTypeID":           c.costtypeid,
            "CostDate":             c.costdate,
            "CostAmount":           c.costamount,
            "Description":          c.description
        }, username, writeAudit=False)
    # Donations
    for dt in dbo.query("SELECT * FROM ownerdonation WHERE AnimalID = ?", [animalid]):
        dbo.insert("ownerdonation", {
            "AnimalID":             nid,
            "OwnerID":              dt.ownerid,
            "MovementID":           0,
            "DonationTypeID":       dt.donationtypeid,
            "DonationPaymentID":    dt.donationpaymentid,
            "Date":                 dt.date,
            "DateDue":              dt.datedue,
            "Donation":             dt.donation,
            "ChequeNumber":         dt.chequenumber,
            "ReceiptNumber":        asm3.financial.get_next_receipt_number(dbo),
            "IsGiftAid":            dt.isgiftaid,
            "Frequency":            dt.frequency,
            "NextCreated":          dt.nextcreated,
            "IsVAT":                dt.isvat,
            "VATRate":              dt.vatrate,
            "VATAmount":            dt.vatamount,
            "Comments":             dt.comments
        }, username, writeAudit=False)
    # Diary
    for di in dbo.query("SELECT * FROM diary WHERE LinkType = 1 AND LinkID = ?", [animalid]):
        dbo.insert("diary", {
            "LinkID":               nid,
            "LinkType":             asm3.diary.ANIMAL,
            "DiaryDateTime":        di.diarydatetime,
            "DiaryForName":         di.diaryforname,
            "Subject":              di.subject,
            "Note":                 di.note,
            "DateCompleted":        di.datecompleted,
            "LinkInfo":             asm3.diary.get_link_info(dbo, asm3.diary.ANIMAL, nid)
        }, username, writeAudit=False)
    # Media
    for me in dbo.query("SELECT * FROM media WHERE LinkTypeID = ? AND LinkID = ?", (asm3.media.ANIMAL, animalid)):
        ext = me.medianame
        ext = ext[ext.rfind("."):].lower()
        mediaid = dbo.get_id("media")
        medianame = "%d%s" % ( mediaid, ext )
        dbo.insert("media", {
            "ID":                   mediaid,
            "DBFSID":               0,
            "MediaSize":            0,
            "MediaName":            medianame,
            "MediaMimeType":        asm3.media.mime_type(medianame),
            "MediaType":            me.mediatype,
            "MediaNotes":           me.medianotes,
            "WebsitePhoto":         me.websitephoto,
            "WebsiteVideo":         me.websitevideo,
            "DocPhoto":             me.docphoto,
            "ExcludeFromPublish":   me.excludefrompublish,
            # ASM2_COMPATIBILITY
            "NewSinceLastPublish":  1,
            "UpdatedSinceLastPublish": 0,
            # ASM2_COMPATIBILITY
            "LinkID":               nid,
            "LinkTypeID":           asm3.media.ANIMAL,
            "Date":                 me.date,
            "CreatedDate":          me.createddate,
            "RetainUntil":          me.retainuntil
        }, generateID=False)
        # Now clone the dbfs item pointed to by this media item if it's a file
        if me.mediatype == asm3.media.MEDIATYPE_FILE:
            filedata = asm3.dbfs.get_string_id(dbo, me.DBFSID)
            dbfsid = asm3.dbfs.put_string(dbo, medianame, "/animal/%d" % nid, filedata)
            dbo.update("media", mediaid, { "DBFSID": dbfsid, "MediaSize": len(filedata) })
    # Movements
    for mv in dbo.query("SELECT * FROM adoption WHERE AnimalID = ?", [animalid]):
        nadid = dbo.get_id("adoption")
        dbo.insert("adoption", {
            "ID":                   nadid,
            "AnimalID":             nid,
            "OwnerID":              mv.ownerid,
            "RetailerID":           mv.retailerid,
            "AdoptionNumber":       asm3.utils.padleft(nadid, 6),
            "OriginalRetailerMovementID": 0,
            "MovementDate":         mv.movementdate,
            "MovementType":         mv.movementtype,
            "ReturnDate":           mv.returndate,
            "ReturnedReasonID":     mv.returnedreasonid,
            "Donation":             mv.donation,
            "InsuranceNumber":      mv.insurancenumber,
            "ReasonForReturn":      mv.reasonforreturn,
            "ReservationDate":      mv.reservationdate,
            "ReservationCancelledDate": mv.reservationcancelleddate,
            "ReservationStatusID":  mv.reservationstatusid,
            "IsTrial":              mv.istrial,
            "IsPermanentFoster":    mv.ispermanentfoster,
            "TrialEndDate":         mv.trialenddate,
            "Comments":             mv.comments
        }, username, generateID=False, writeAudit=False)
    # Log
    if asm3.configuration.clone_animal_include_logs(dbo):
        # Only clone logs if the hidden config switch is on
        for lo in dbo.query("SELECT * FROM log WHERE LinkType = ? AND LinkID = ?", (asm3.log.ANIMAL, animalid)):
            dbo.insert("log", {
                "LinkID":           nid,
                "LinkType":         asm3.log.ANIMAL,
                "LogTypeID":        lo.logtypeid,
                "Date":             lo.date,
                "Comments":         lo.comments
            }, username, writeAudit=False)

    asm3.audit.create(dbo, username, "animal", nid, "", asm3.audit.dump_row(dbo, "animal", nid))
    update_animal_status(dbo, nid)
    update_variable_animal_data(dbo, nid)
    return nid

def clone_from_template(dbo: Database, username: str, animalid: int, datebroughtin: datetime, dob: datetime, animaltypeid: int, speciesid: int, nonshelter: int) -> None:
    """
    Tries to locate a non-shelter animal called "TemplateType" with animaltypeid,
    if it doesn't find one, it looks for a non-shelter animal called "TemplateSpecies"
    with speciesid. If one is not found, does nothing.
    If the animal is deemed to be a baby according to the baby split defined for the
    annual figures report, will check for "TemplateTypeBaby" or "TemplateTypeSpecies" first.
    Clones appropriate medical, cost and diet info from the template animal.
    """
    babyqueries = [
        "SELECT MIN(ID) FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatetypebabydob' AND AnimalTypeID = %d" % animaltypeid,
        "SELECT MIN(ID) FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatespeciesbabydob' AND SpeciesID = %d" % speciesid,
        "SELECT MIN(ID) FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatetypebaby' AND AnimalTypeID = %d" % animaltypeid,
        "SELECT MIN(ID) FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatespeciesbaby' AND SpeciesID = %d" % speciesid,
        "SELECT MIN(ID) FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatetypedob' AND AnimalTypeID = %d" % animaltypeid,
        "SELECT MIN(ID) FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatespeciesdob' AND SpeciesID = %d" % speciesid,
        "SELECT MIN(ID) FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatetype' AND AnimalTypeID = %d" % animaltypeid,
        "SELECT MIN(ID) FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatespecies' AND SpeciesID = %d" % speciesid
    ]
    adultqueries = [ 
        "SELECT MIN(ID) FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatetypedob' AND AnimalTypeID = %d" % animaltypeid,
        "SELECT MIN(ID) FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatespeciesdob' AND SpeciesID = %d" % speciesid,
        "SELECT MIN(ID) FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatetype' AND AnimalTypeID = %d" % animaltypeid,
        "SELECT MIN(ID) FROM animal WHERE NonShelterAnimal = 1 AND LOWER(AnimalName) LIKE 'templatespecies' AND SpeciesID = %d" % speciesid
    ]
    queries = adultqueries
    # If this is a baby animal as defined by its age, use the babyqueries to look for a template
    babymonths = asm3.configuration.annual_figures_baby_months(dbo)
    babydays = babymonths * 30.5
    # 12 * 30.5 = 366 so it's one day out for a year
    if babymonths == 12: babydays = 365
    if date_diff_days(dob, dbo.today()) < babydays:
        queries = babyqueries
    # Use our queries to find a potential template
    for q in queries:
        cloneanimalid = dbo.query_int(q)
        if cloneanimalid != 0: break
    # Give up if we didn't find a template animal
    if cloneanimalid == 0:
        return
    # Any animal fields that should be copied to the new record
    copyfrom = dbo.first_row( dbo.query("SELECT AnimalName, IsNotAvailableForAdoption, IsNotForRegistration, IsHold, AdditionalFlags, " \
        "DateBroughtIn, DateOfBirth, Fee, HoldUntilDate, CurrentVetID, AnimalComments FROM animal WHERE ID = ?", [cloneanimalid]) )
    # Use datebroughtin for calculating date offsets
    templatedate = copyfrom.DATEBROUGHTIN
    newrecorddate = datebroughtin
    # Unless the selected template that we're using specified date of birth
    if copyfrom.ANIMALNAME.lower().endswith("dob"):
        templatedate = copyfrom.DATEOFBIRTH
        newrecorddate = dob
    def adjust_date(d: datetime) -> str:
        """
        Helper function to adjust the date on a template record when copying it to a new record.
        Does this by working out the offset in days between the dates on the template record and 
        applying that offset to the base date on the new record.
        Normally the template date and new record date are datebroughtin, but if
        this template is set to operate on DOB, then dateofbirth is used instead.
        If the calculated date is before the intake date, intake date is returned instead.
        """
        if d is None: return None
        dayoffset = date_diff_days(templatedate, d)
        if dayoffset < 0:
            adjdate = subtract_days(newrecorddate, dayoffset)
        else:
            adjdate = add_days(newrecorddate, dayoffset)
        adjdate = adjdate.replace(hour=0, minute=0, second=0, microsecond=0) # throw away any time info that might have been on the original date
        if adjdate < datebroughtin: adjdate = datebroughtin
        return adjdate
    # Copy the flags from the template to the new record. Do not copy the non-shelter flag
    # from the template as templates generally only apply to shelter animals.
    newflags = [ x for x in copyfrom.additionalflags.split("|") if x != "nonshelter" ]
    # If the animal we are applying the template is actually non-shelter 
    # (can only happen if the hidden option TemplatesForNonShelter == Yes has been manually set)
    # then we re-add the non-shelter flag.
    if nonshelter == 1: newflags.append("nonshelter")
    # If the option has been turned on to make new animals not for adoption, set that too
    if asm3.configuration.auto_not_for_adoption(dbo): newflags.append("notforadoption")
    update_flags(dbo, username, animalid, newflags)
    # Deal with other selected animal fields from the template
    p = {
        "Fee":                      copyfrom.fee,
        "CurrentVetID":             copyfrom.currentvetid,
        "AnimalComments":           copyfrom.animalcomments
    }
    if copyfrom.ishold == 1:
        p["IsHold"] = 1
        if copyfrom.holduntildate is not None:
            p["HoldUntilDate"] = adjust_date(copyfrom.holduntildate)
        else:
            # Use the hold for X days configuration option if there's no hold until date
            p["HoldUntilDate"] = add_days(templatedate, asm3.configuration.auto_remove_hold_days(dbo))
    dbo.update("animal", animalid, p)
    # Additional Fields (don't include newrecord ones or ones with default values as they are already set by the new animal screen)
    for af in dbo.query("SELECT a.* FROM additional a INNER JOIN additionalfield af ON af.ID = a.AdditionalFieldID " \
        "WHERE af.NewRecord <> 1 AND af.DefaultValue = '' AND a.LinkID = %d AND a.LinkType IN (%s)" % (cloneanimalid, asm3.additional.ANIMAL_IN)):
        asm3.additional.insert_additional(dbo, af.linktype, animalid, af.additionalfieldid, af.value)
    # Vaccinations
    for v in dbo.query("SELECT * FROM animalvaccination WHERE AnimalID = ?", [cloneanimalid]):
        newdate = adjust_date(v.daterequired)
        dbo.insert("animalvaccination", {
            "AnimalID":             animalid,
            "VaccinationID":        v.vaccinationid,
            "DateRequired":         newdate,
            "DateOfVaccination":    None,
            "DateExpires":          None,
            "AdministeringVetID":   v.administeringvetid,
            "BatchNumber":          v.batchnumber,
            "Manufacturer":         v.manufacturer,
            "Cost":                 v.cost,
            "Comments":             v.comments
        }, username)
    # Tests
    for t in dbo.query("SELECT * FROM animaltest WHERE AnimalID = ?", [cloneanimalid]):
        newdate = adjust_date(t.daterequired)
        dbo.insert("animaltest", {
            "AnimalID":             animalid,
            "TestTypeID":           t.testtypeid,
            "TestResultID":         t.testresultid,
            "DateOfTest":           None,
            "DateRequired":         newdate,
            "AdministeringVetID":   t.administeringvetid,
            "Cost":                 t.cost,
            "Comments":             t.comments
        }, username)
    # Medical
    for am in dbo.query("SELECT * FROM animalmedical WHERE AnimalID = ?", [cloneanimalid]):
        newdate = adjust_date(am.startdate)
        namid = dbo.insert("animalmedical", {
            "AnimalID":             animalid,
            "MedicalProfileID":     am.medicalprofileid,
            "TreatmentName":        am.treatmentname,
            "StartDate":            newdate,
            "Dosage":               am.dosage,
            "Cost":                 am.cost,
            "CostPerTreatment":     am.costpertreatment,
            "TimingRule":           am.timingrule,
            "TimingRuleFrequency":  am.timingrulefrequency,
            "TimingRuleNoFrequencies": am.timingrulenofrequencies,
            "TreatmentRule":        am.treatmentrule,
            "TotalNumberOfTreatments": am.totalnumberoftreatments,
            "TreatmentsGiven":      am.treatmentsgiven,
            "TreatmentsRemaining":  am.treatmentsremaining,
            "Status":               am.status,
            "Comments":             am.comments
        }, username)
        for amt in dbo.query("SELECT * FROM animalmedicaltreatment WHERE AnimalMedicalID = ?", [am.id]):
            dbo.insert("animalmedicaltreatment", {
                "AnimalID":         animalid,
                "AnimalMedicalID":  namid,
                "DateRequired":     newdate,
                "DateGiven":        None,
                "TreatmentNumber":  amt.treatmentnumber,
                "TotalTreatments":  amt.totaltreatments,
                "AdministeringVetID": amt.administeringvetid,
                "GivenBy":          amt.givenby,
                "Comments":         amt.comments
            }, username)
    # Diet
    for d in dbo.query("SELECT * FROM animaldiet WHERE AnimalID = ?", [cloneanimalid]):
        newdate = adjust_date(d.datestarted)
        dbo.insert("animaldiet", {
            "AnimalID":             animalid,
            "DietID":               d.dietid,
            "DateStarted":          newdate,
            "Comments":             d.comments
        }, username)
    # Costs
    for c in dbo.query("SELECT * FROM animalcost WHERE AnimalID = ?", [cloneanimalid]):
        newdate = adjust_date(c.costdate)
        dbo.insert("animalcost", {
            "AnimalID":             animalid,
            "CostTypeID":           c.costtypeid,
            "CostDate":             newdate,
            "CostAmount":           c.costamount,
            "Description":          c.description
        }, username)
    # Diary
    for di in dbo.query("SELECT * FROM diary WHERE LinkType = 1 AND LinkID = ?", [cloneanimalid]):
        newdate = adjust_date(di.diarydatetime)
        dbo.insert("diary", {
            "LinkID":               animalid,
            "LinkType":             asm3.diary.ANIMAL,
            "DiaryDateTime":        newdate,
            "DiaryForName":         di.diaryforname,
            "Subject":              di.subject,
            "Note":                 di.note,
            "DateCompleted":        None,
            "LinkInfo":             asm3.diary.get_link_info(dbo, asm3.diary.ANIMAL, animalid)
        }, username)

def delete_animal(dbo: Database, username: str, animalid: int, ignore_movements: bool = False) -> None:
    """
    Deletes an animal and all its satellite records.
    """
    l = dbo.locale
    if not ignore_movements and dbo.query_int("SELECT COUNT(ID) FROM adoption WHERE AnimalID=?", [animalid]):
        raise asm3.utils.ASMValidationError(_("This animal has movements and cannot be removed.", l))
    dbo.delete("media", "LinkID=%d AND LinkTypeID=%d" % (animalid, asm3.media.ANIMAL), username)
    dbo.delete("diary", "LinkID=%d AND LinkType=%d" % (animalid, asm3.diary.ANIMAL), username)
    dbo.delete("log", "LinkID=%d AND LinkType=%d" % (animalid, asm3.log.ANIMAL), username)
    dbo.execute("DELETE FROM additional WHERE LinkID = %d AND LinkType IN (%s)" % (animalid, asm3.additional.ANIMAL_IN))
    dbo.execute("DELETE FROM animalcontrolanimal WHERE AnimalID = ?", [animalid])
    dbo.execute("DELETE FROM animalpublished WHERE AnimalID = ?", [animalid])
    for t in [ "adoption", "animalentry", "animalmedical", "animalmedicaltreatment", "animaltest", "animaltransport", "animalvaccination", "clinicappointment" ]:
        dbo.delete(t, "AnimalID=%d" % animalid, username)
    dbo.delete("animal", animalid, username)
    # asm3.dbfs.delete_path(dbo, "/animal/%d" % animalid) # Use maint_db_delete_orphaned_media to remove dbfs later if needed

def delete_animals_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Batch deletes animals from the bulk form.
    Returns the number of affected records.
    """
    for animalid in post.integer_list("animals"):
        delete_animal(dbo, username, animalid, ignore_movements=True)
    return len(post.integer_list("animals"))

def merge_animal(dbo: Database, username: str, animalid: int, mergeanimalid: int) -> None:
    """
    Reparents all satellite records of mergeanimalid onto
    animalid.
    """
    l = dbo.locale

    if animalid == mergeanimalid:
        raise asm3.utils.ASMValidationError(_("The animal record to merge must be different from the original.", l))

    if animalid == 0 or mergeanimalid == 0:
        raise asm3.utils.ASMValidationError("Internal error: Cannot merge ID 0")
    
    if dbo.query_int("SELECT COUNT(ID) FROM animal WHERE ID IN (?, ?)", [animalid, mergeanimalid]) != 2:
        raise asm3.utils.ASMValidationError("Internal error: Record has been deleted")

    def reparent(table, field, linktypefield = "", linktype = -1, haslastchanged = True):
        try:
            if table == "media":
                dbo.execute("UPDATE media SET LinkID=?, WebsitePhoto=0, WebsiteVideo=0, DocPhoto=0 WHERE LinkID=? AND LinkTypeID=?", (animalid, mergeanimalid, linktype))
            if linktype >= 0:
                dbo.update(table, "%s=%s AND %s=%s" % (field, mergeanimalid, linktypefield, linktype), 
                    { field: animalid }, username, 
                    setLastChanged=False, setRecordVersion=haslastchanged)
            else:
                dbo.update(table, "%s=%s" % (field, mergeanimalid), 
                    { field: animalid }, username, setLastChanged=False, setRecordVersion=haslastchanged)
        except Exception as err:
            asm3.al.error("error reparenting: %s -> %s, table=%s, field=%s, linktypefield=%s, linktype=%s, error=%s" % \
                (mergeanimalid, animalid, table, field, linktypefield, linktype, err), "animal.merge_animal", dbo)

    # Reparent all satellite records
    reparent("adoption", "AnimalID")
    reparent("animal", "BondedAnimalID")
    reparent("animal", "BondedAnimal2ID")
    reparent("animalcontrolanimal", "AnimalID", haslastchanged=False)
    reparent("animalcost", "AnimalID")
    reparent("animaldiet", "AnimalID")
    reparent("animallitter", "ParentAnimalID", haslastchanged=False)
    reparent("animallostfoundmatch", "AnimalID", haslastchanged=False)
    reparent("animalmedical", "AnimalID")
    reparent("animalmedicaltreatment", "AnimalID")
    reparent("animalpublished", "AnimalID", haslastchanged=False)
    reparent("animaltest", "AnimalID")
    reparent("animaltransport", "AnimalID")
    reparent("animalvaccination", "AnimalID")
    reparent("clinicappointment", "AnimalID")
    reparent("ownerdonation", "AnimalID")
    reparent("ownerlookingfor", "AnimalID", haslastchanged=False)
    reparent("ownerlicence", "AnimalID")
    reparent("media", "LinkID", "LinkTypeID", asm3.media.ANIMAL, haslastchanged=False)
    reparent("diary", "LinkID", "LinkType", asm3.diary.ANIMAL)
    reparent("log", "LinkID", "LinkType", asm3.log.ANIMAL, haslastchanged=False)

    # Merge fields
    ma = get_animal(dbo, mergeanimalid)
    d = {}
    d["comments"] = ma.ANIMALCOMMENTS
    d["healthproblems"] = ma.HEALTHPROBLEMS
    d["microchipnumber"] = ma.IDENTICHIPNUMBER
    d["microchipdate"] = python2display(dbo.locale, ma.IDENTICHIPDATE)
    d["neutered"] = ma.NEUTERED == 1 and "on" or ""
    d["neutereddate"] = python2display(dbo.locale, ma.NEUTEREDDATE)
    d["weight"] = str(ma.WEIGHT)
    d["internallocation"] = str(ma.SHELTERLOCATION)
    d["unit"] = str(ma.SHELTERLOCATIONUNIT)
    d["pickuplocation"] = str(ma.PICKUPLOCATIONID)
    d["pickupaddress"] = ma.PICKUPADDRESS
    merge_animal_details(dbo, username, animalid, d)

    # Change any additional field links pointing to the merge animal
    asm3.additional.update_merge_animal(dbo, mergeanimalid, animalid)

    # Copy additional field values from mergeanimal to animal
    asm3.additional.merge_values(dbo, username, mergeanimalid, animalid, "animal")

    # Delete the old additional field values from mergeanimal
    dbo.execute("DELETE FROM additional WHERE LinkID = %d AND LinkType IN (%s)" % (mergeanimalid, asm3.additional.ANIMAL_IN))

    # Reparent the audit records for the reparented records in the audit log
    # by switching ParentLinks to the new ID.
    dbo.execute("UPDATE audittrail SET ParentLinks = %s WHERE ParentLinks LIKE '%%animal=%s %%'" % \
        ( dbo.sql_replace("ParentLinks", "animal=%s " % mergeanimalid, "animal=%s " % animalid), mergeanimalid))

    dbo.delete("animal", mergeanimalid, username)
    asm3.audit.move(dbo, username, "animal", animalid, "", "Merged animal %d -> %d" % (mergeanimalid, animalid))

def merge_animal_details(dbo: Database, username: str, animalid: int, d: dict, force: bool = False) -> None:
    """
    Merges animal details in data dictionary d (the same dictionary that
    would be fed to insert_animal_from_form and update_person_from_form)
    to animal with animalid.
    If any of the fields on the animal record are blank and available
    in the dictionary, the ones from the dictionary are used instead and updated on the record.
    animalid: The animal we're merging details into
    d: The dictionary of values to merge
    force: If True, forces overwrite of the details with values from d if they are present
    """
    uv = {}
    a = get_animal(dbo, animalid)
    if a is None: return
    def merge(dictfield, fieldname):
        if dictfield not in d or d[dictfield] == "": return
        if a[fieldname] is None or a[fieldname] == "" or force:
            uv[fieldname] = d[dictfield]
            a[fieldname] = uv[fieldname]
    def merge_date(dictfield, fieldname):
        if dictfield not in d or display2python(dbo.locale, d[dictfield]) is None: return
        if a[fieldname] is None or force:
            uv[fieldname] = display2python(dbo.locale, d[dictfield])
            a[fieldname] = uv[fieldname]
    def merge_float(dictfield, fieldname):
        if dictfield not in d or not asm3.utils.is_numeric(d[dictfield]): return
        if a[fieldname] is None or a[fieldname] == 0 or force:
            uv[fieldname] = asm3.utils.cfloat(d[dictfield])
            a[fieldname] = uv[fieldname]
    def merge_int(dictfield, fieldname):
        if dictfield not in d or not asm3.utils.is_numeric(d[dictfield]): return
        if a[fieldname] is None or a[fieldname] == 0 or force:
            uv[fieldname] = asm3.utils.cint(d[dictfield])
            a[fieldname] = uv[fieldname]
    def merge_ref(dictfield, fieldname):
        if dictfield not in d or asm3.utils.cint(d[dictfield]) == 0: return
        if a[fieldname] is None or a[fieldname] == 0 or force:
            uv[fieldname] = asm3.utils.cint(d[dictfield])
            a[fieldname] = uv[fieldname]
    def merge_bool(dictfield, fieldname):
        if dictfield not in d or d[dictfield] == "": return
        if a[fieldname] is None or a[fieldname] == 0 or force:
            if d[dictfield] == "on": 
                uv[fieldname] = 1
                a[fieldname] = 1
    merge("comments", "ANIMALCOMMENTS")
    merge("healthproblems", "HEALTHPROBLEMS")
    merge("microchipnumber", "IDENTICHIPNUMBER")
    merge_date("microchipdate", "IDENTICHIPDATE")
    if "microchipnumber" in d and "IDENTICHIPNUMBER" in uv and d["microchipnumber"] == uv["IDENTICHIPNUMBER"]: uv["IDENTICHIPPED"] = 1
    if "neutered" in d and d["neutered"] == "on" and a.NEUTERED == 0: uv["NEUTERED"] = 1
    merge_date("neutereddate", "NEUTEREDDATE")
    merge_ref("neuteringvet", "NEUTEREDBYVETID")
    merge_date("dateofbirth", "DATEOFBIRTH")
    merge_date("deceaseddate", "DECEASEDDATE")
    merge_bool("puttosleep", "PUTTOSLEEP")
    merge_ref("deathcategory", "PTSREASONID")
    merge("ptsreason", "PTSREASON")
    merge_float("weight", "WEIGHT")
    merge_ref("internallocation", "SHELTERLOCATION")
    merge("unit", "SHELTERLOCATIONUNIT")
    merge_ref("pickuplocation", "PICKUPLOCATIONID")
    merge("pickupaddress", "PICKUPADDRESS")
    merge_int("housetrained", "ISHOUSETRAINED")
    merge_int("cratetrained", "ISCRATETRAINED")
    merge_int("goodwithcats", "ISGOODWITHCATS")
    merge_int("goodwithdogs", "ISGOODWITHDOGS")
    merge_int("goodwithkids", "ISGOODWITHCHILDREN")
    merge_int("goodwithelderly", "ISGOODWITHELDERLY")
    merge_int("energylevel", "ENERGYLEVEL")
    merge_int("goodonlead", "ISGOODONLEAD")
    merge_int("goodtraveller", "ISGOODTRAVELLER")
    
    if len(uv) > 0:
        dbo.update("animal", animalid, uv, username)

def update_current_owner(dbo: Database, username: str, animalid: int) -> None:
    """
    Updates the current owner for an animal from the available movements.
    """
    exit_movements = get_exit_movement_types(dbo)

    # The current owner for this animal
    animalownerid = dbo.query_int("SELECT OwnerID FROM animal WHERE ID=?", [animalid])

    # The latest exit movement for this animal (can't rely on denormalised)
    latestexitmoveid = dbo.query_int("SELECT ID FROM adoption WHERE AnimalID=? " \
        f"AND MovementType IN ({exit_movements}) AND MovementDate Is Not Null " \
        "AND MovementDate <= ? AND (ReturnDate Is Null OR ReturnDate > ?) " \
        "ORDER BY MovementDate DESC", [animalid, dbo.today(), dbo.today()])

    # The person from the latest exit movement on this animal
    latestexitmoveownerid = dbo.query_int("SELECT OwnerID FROM adoption WHERE ID=?", [latestexitmoveid])

    # The latest movement for this animal linked to the current owner that is not the latest
    # exit movement (ie. if this is >0 we know the current owner is from an old exit movement)
    lastownermoveid = dbo.query_int("SELECT ID FROM adoption WHERE AnimalID=? " \
        f"AND MovementType IN ({exit_movements}) AND OwnerID=? AND ID<>? " \
        "ORDER BY MovementDate DESC", [animalid, animalownerid, latestexitmoveid])

    # Set the current owner if the animal doesn't already have one 
    # or the current owner was present on a previous exit movement that is not the latest
    if animalownerid == 0 or lastownermoveid > 0:
        # Only set if we actually have a latest exit movement and person
        if latestexitmoveownerid > 0:
            dbo.update("animal", animalid, { "OwnerID" : latestexitmoveownerid }, username)

def update_daily_boarding_cost(dbo: Database, username: str, animalid: int, cost: int) -> None:
    """
    Updates the daily boarding cost amount for an animal. The
    cost parameter should have already been turned into an integer.
    """
    oldcost = dbo.query_string("SELECT DailyBoardingCost FROM animal WHERE ID = ?", [animalid])
    dbo.execute("UPDATE animal SET DailyBoardingCost = ? WHERE ID = ?", (cost, animalid) )
    asm3.audit.edit(dbo, username, "animal", animalid, "", "%s: DailyBoardingCost %s ==> %s" % ( str(animalid), oldcost, str(cost) ))

def update_preferred_web_media_notes(dbo: Database, username: str, animalid: int, newnotes: str) -> None:
    """
    Updates the preferred web media notes for an animal.
    """
    mediaid = dbo.query_int("SELECT ID FROM media WHERE WebsitePhoto = 1 AND LinkID = ? AND LinkTypeID = ?", (animalid, asm3.media.ANIMAL))
    if mediaid > 0:
        dbo.update("media", mediaid, {
            "MediaNotes": newnotes,
            "UpdatedSinceLastPublish": 1
        })
        asm3.audit.edit(dbo, username, "media", mediaid, "", str(mediaid) + "notes => " + newnotes)
 
def insert_diet_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Creates a diet record from posted form data
    """
    return dbo.insert("animaldiet", {
        "AnimalID":     post.integer("animalid"),
        "DietID":       post.integer("type"),
        "DateStarted":  post.date("startdate"),
        "Comments":     post["comments"]
    }, username)

def update_diet_from_form(dbo: Database, username: str, post: PostedData) -> None:
    """
    Updates a diet record from posted form data
    """
    dbo.update("animaldiet", post.integer("dietid"), {
        "DietID":       post.integer("type"),
        "DateStarted":  post.date("startdate"),
        "Comments":     post["comments"]
    }, username)

def delete_diet(dbo: Database, username: str, did: int) -> None:
    """
    Deletes the selected diet
    """
    dbo.delete("animaldiet", did, username)

def insert_cost_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Creates a cost record from posted form data
    """
    l = dbo.locale
    if post.date("costdate") is None:
        raise asm3.utils.ASMValidationError(_("Cost date must be a valid date", l))
    ncostid = dbo.insert("animalcost", {
        "AnimalID":         post.integer("animalid"),
        "CostTypeID":       post.integer("type"),
        "CostDate":         post.date("costdate"),
        "CostPaidDate":     post.date("costpaid"),
        "CostAmount":       post.integer("cost"),
        "Description":      post["description"],
        "OwnerID":          post.integer("person"),
        "InvoiceNumber":    post["invoicenumber"]
    }, username)
    asm3.financial.update_matching_cost_transaction(dbo, username, ncostid)
    return ncostid

def update_cost_from_form(dbo: Database, username: str, post: PostedData) -> None:
    """
    Updates a cost record from posted form data
    """
    costid = post.integer("costid")
    dbo.update("animalcost", costid, {
        "CostTypeID":       post.integer("type"),
        "CostDate":         post.date("costdate"),
        "CostPaidDate":     post.date("costpaid"),
        "CostAmount":       post.integer("cost"),
        "Description":      post["description"],
        "OwnerID":          post.integer("person"),
        "InvoiceNumber":    post["invoicenumber"]
    }, username)
    asm3.financial.update_matching_cost_transaction(dbo, username, costid)

def delete_cost(dbo: Database, username: str, cid: int) -> None:
    """
    Deletes a cost record
    """
    dbo.delete("animalcost", cid, username)

def insert_litter_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Creates a litter record from posted form data
    """
    nid = dbo.insert("animallitter", {
        "ParentAnimalID":   post.integer("animal"),
        "SpeciesID":        post.integer("species"),
        "Date":             post.date("startdate"),
        "AcceptanceNumber": post["litterref"],
        "CachedAnimalsLeft": 0,
        "InvalidDate":      post.date("expirydate"),
        "NumberInLitter":   post.integer("numberinlitter"),
        "Comments":         post["comments"],
        "RecordVersion":    dbo.get_recordversion()
    }, username, setCreated = False)
    
    # if a list of littermates were given, set the litterid on those animal records
    for i in post.integer_list("animals"):
        dbo.update("animal", i, { "AcceptanceNumber": post["litterref"] })

    update_litter_count(dbo, post["litterref"])
    return nid

def update_litter_from_form(dbo: Database, username: str, post: PostedData) -> None:
    """
    Updates a litter record from posted form data
    """
    dbo.update("animallitter", post.integer("litterid"), {
        "ParentAnimalID":   post.integer("animal"),
        "SpeciesID":        post.integer("species"),
        "Date":             post.date("startdate"),
        "AcceptanceNumber": post["litterref"],
        "InvalidDate":      post.date("expirydate"),
        "NumberInLitter":   post.integer("numberinlitter"),
        "Comments":         post["comments"],
        "RecordVersion":    dbo.get_recordversion()
    }, username, setLastChanged = False)

    update_litter_count(dbo, post.integer("litterref"))

def update_litter_count(dbo: Database, litterref: str) -> None:
    """
    Updates the CachedAnimalsLeft field for litterref
    """
    litterref = str(litterref)
    l = dbo.first_row(dbo.query("SELECT l.*, " \
        "(SELECT COUNT(*) FROM animal a WHERE a.Archived = 0 " \
        "AND a.AcceptanceNumber = l.AcceptanceNumber AND a.DateOfBirth >= ?) AS dbcount " \
        "FROM animallitter l " \
        "WHERE l.AcceptanceNumber = ?", ( subtract_months(dbo.today(), 6), litterref )))
    if l is not None:
        dbo.execute("UPDATE animallitter SET CachedAnimalsLeft=? WHERE AcceptanceNumber = ?", [l.dbcount, litterref])

def delete_litter(dbo: Database, username: str, lid: int) -> None:
    """
    Deletes the selected litter
    """
    dbo.delete("animallitter", lid, username)

def update_animal_check_bonds(dbo: Database, animalid: int) -> None:
    """
    Checks the bonds on animalid and if necessary, creates
    links back to animalid from the bonded animals
    """

    def addbond(tanimalid, bondid):
        tbond = dbo.first_row( dbo.query("SELECT BondedAnimalID, BondedAnimal2ID FROM animal WHERE ID = ?", [tanimalid]) )
        if not tbond: return
        # If a bond already exists, don't do anything
        if tbond.bondedanimalid == bondid: return
        if tbond.bondedanimal2id == bondid: return
        # Add a bond if we have a free slot
        if tbond.bondedanimalid == 0:
            dbo.execute("UPDATE animal SET BondedAnimalID = ? WHERE ID = ?", (bondid, tanimalid))
            return
        if tbond.bondedanimal2id == 0:
            dbo.execute("UPDATE animal SET BondedAnimal2ID = ? WHERE ID = ?",  (bondid, tanimalid))

    bonds = dbo.first_row( dbo.query("SELECT BondedAnimalID, BondedAnimal2ID FROM animal WHERE ID = ?", [animalid]) )
    if not bonds: return
    bond1 = bonds.bondedanimalid
    bond2 = bonds.bondedanimal2id
    if bond1 != 0: addbond(bond1, animalid)
    if bond2 != 0: addbond(bond2, animalid)

def update_animal_breeds(dbo: Database, breedid: int = 0) -> str:
    """
    Regenerates the breedname field for all animals.
    breedid: If non zero, only updates animals who have this breed
    """
    where = ""
    if breedid > 0:
        where = f"WHERE BreedID={breedid} OR Breed2ID={breedid}"
    batch = []
    animals = dbo.query(f"SELECT ID, BreedID, Breed2ID FROM animal {where}")
    breeds = dbo.query("SELECT ID, BreedName FROM breed")
    def bname(bid):
        for b in breeds:
            if b.ID == bid: return b.BREEDNAME
        return "Invalid"
    for a in animals:
        if a.BREEDID == a.BREED2ID or a.BREED2ID == 0:
            breedname = bname(a.BREEDID)
        else:
            breedname = "%s / %s" % ( bname(a.BREEDID), bname(a.BREED2ID) )
        batch.append(( breedname, a.ID ))
    dbo.execute_many("UPDATE animal SET " \
        "BreedName = ? " \
        "WHERE ID = ?", batch)
    asm3.al.debug(f"breedid={breedid}: updated breeds for {len(batch)} animal records", "update_animal_breeds", dbo)
    return "OK %d" % len(batch)

def update_variable_animal_data(dbo: Database, animalid: int, a: ResultRow = None, animalupdatebatch: List[Tuple] = None, bands: List[Tuple[str, float]] = None, movements: Results = None) -> None:
    """
    Updates the variable data animal fields,
    MostRecentEntryDate, TimeOnShelter, DaysOnShelter, AgeGroup, AnimalAge,
    TotalTimeOnShelter, TotalDaysOnShelter
    AgeGroup holds the animal's current age group, but resets to last entry when they leave the shelter.
    (int) animalid: The animal to update
    a: An animal result to use instead of looking it up from the id
    animalupdatebatch: A batch of update parameters
    bands: List of loaded age group bands
    movements: List of loaded movements
    """
    if animalupdatebatch is not None:
        animalupdatebatch.append((
            calc_time_on_shelter(dbo, animalid, a),
            calc_age_group(dbo, animalid, a, bands, asm3.utils.iif(a.archived==1, a.mostrecententrydate, None)),
            calc_age_group(dbo, animalid, a, bands, a.activemovementdate),
            calc_age(dbo, animalid, a),
            calc_days_on_shelter(dbo, animalid, a),
            calc_total_time_on_shelter(dbo, animalid, a, movements),
            calc_total_days_on_shelter(dbo, animalid, a, movements),
            animalid
        ))
    else:
        a = dbo.first_row(dbo.query("SELECT ID, DateBroughtIn, DeceasedDate, DiedOffShelter, Archived, ActiveMovementDate, " \
            "MostRecentEntryDate, DateOfBirth FROM animal WHERE ID=?", [animalid]))
        movements = dbo.query("SELECT AnimalID, MovementDate, ReturnDate FROM adoption " \
            "WHERE AnimalID = ? AND MovementType NOT IN (2,8) AND MovementDate Is Not Null AND ReturnDate Is Not Null " \
            "ORDER BY AnimalID", [animalid])
        dbo.update("animal", animalid, {
            "TimeOnShelter":        calc_time_on_shelter(dbo, animalid, a),
            "AgeGroup":             calc_age_group(dbo, animalid, a, todate = asm3.utils.iif(a.archived==1, a.mostrecententrydate, None)),
            "AgeGroupActiveMovement": calc_age_group(dbo, animalid, a, todate = a.activemovementdate),
            "AnimalAge":            calc_age(dbo, animalid, a),
            "DaysOnShelter":        calc_days_on_shelter(dbo, animalid, a),
            "TotalTimeOnShelter":   calc_total_time_on_shelter(dbo, animalid, a),
            "TotalDaysOnShelter":   calc_total_days_on_shelter(dbo, animalid, a)
        }, setRecordVersion=False, writeAudit=False)

def update_all_variable_animal_data(dbo: Database) -> str:
    """
    Updates variable animal data for all animals. This is a big memory heavy routine if you've
    got a lot of animal and movement records as loads sections of both complete tables into RAM.
    """
    l = dbo.locale
    
    animalupdatebatch = []

    # Load age group bands now to save repeated looped lookups
    bands = asm3.configuration.age_group_bands(dbo)

    # Relevant fields
    animals = dbo.query("SELECT ID, DateBroughtIn, DeceasedDate, DiedOffShelter, Archived, ActiveMovementDate, " \
        "MostRecentEntryDate, DateOfBirth FROM animal")

    # Get a single lookup of movement histories for our animals
    movements = dbo.query("SELECT AnimalID, MovementDate, ReturnDate FROM adoption " \
        "WHERE MovementType NOT IN (2,8) AND MovementDate Is Not Null AND ReturnDate Is Not Null " \
        "ORDER BY AnimalID")

    asm3.asynctask.set_progress_max(dbo, len(animals))
    for a in animals:
        update_variable_animal_data(dbo, a.id, a, animalupdatebatch, bands, movements)
        asm3.asynctask.increment_progress_value(dbo)

    dbo.execute_many("UPDATE animal SET " \
        "TimeOnShelter = ?, " \
        "AgeGroup = ?, " \
        "AgeGroupActiveMovement = ?, " \
        "AnimalAge = ?, " \
        "DaysOnShelter = ?, " \
        "TotalTimeOnShelter = ?, " \
        "TotalDaysOnShelter = ? " \
        "WHERE ID = ?", animalupdatebatch)

    asm3.al.debug("updated variable data for %d animals (locale %s)" % (len(animals), l), "animal.update_all_variable_animal_data", dbo)
    return "OK %d" % len(animals)

def update_foster_variable_animal_data(dbo: Database) -> str:
    """
    Updates variable animal data for all foster animals.
    This wouldn't do anything if foster on shelter is true, so explicitly looks for off-shelter fostered.
    """
    l = dbo.locale
    
    animalupdatebatch = []

    # Load age group bands now to save repeated looped lookups
    bands = asm3.configuration.age_group_bands(dbo)

    # Relevant on shelter animal fields
    animals = dbo.query("SELECT ID, DateBroughtIn, DeceasedDate, DiedOffShelter, Archived, ActiveMovementDate, " \
        "MostRecentEntryDate, DateOfBirth FROM animal WHERE Archived = 1 AND ActiveMovementType = 2")

    # Get a single lookup of movement histories for our on shelter animals
    movements = dbo.query("SELECT ad.AnimalID, ad.MovementDate, ad.ReturnDate " \
        "FROM animal a " \
        "INNER JOIN adoption ad ON a.ID = ad.AnimalID " \
        "WHERE a.Archived = 0 AND ad.MovementType NOT IN (2,8) " \
        "AND ad.MovementDate Is Not Null AND ad.ReturnDate Is Not Null " \
        "ORDER BY a.ID")

    for a in animals:
        update_variable_animal_data(dbo, a.id, a, animalupdatebatch, bands, movements)

    dbo.execute_many("UPDATE animal SET " \
        "TimeOnShelter = ?, " \
        "AgeGroup = ?, " \
        "AgeGroupActiveMovement = ?, " \
        "AnimalAge = ?, " \
        "DaysOnShelter = ?, " \
        "TotalTimeOnShelter = ?, " \
        "TotalDaysOnShelter = ? " \
        "WHERE ID = ?", animalupdatebatch)

    asm3.al.debug("updated variable data for %d animals (locale %s)" % (len(animals), l), "animal.update_foster_variable_animal_data", dbo)
    return "OK %d" % len(animals)

def update_on_shelter_variable_animal_data(dbo: Database) -> str:
    """
    Updates variable animal data for all shelter and foster animals.
    """
    l = dbo.locale
    
    animalupdatebatch = []

    # Load age group bands now to save repeated looped lookups
    bands = asm3.configuration.age_group_bands(dbo)

    # Relevant on shelter animal fields
    animals = dbo.query("SELECT ID, DateBroughtIn, DeceasedDate, DiedOffShelter, Archived, ActiveMovementDate, " \
        "MostRecentEntryDate, DateOfBirth FROM animal WHERE Archived = 0")

    # Get a single lookup of movement histories for our on shelter animals
    movements = dbo.query("SELECT ad.AnimalID, ad.MovementDate, ad.ReturnDate " \
        "FROM animal a " \
        "INNER JOIN adoption ad ON a.ID = ad.AnimalID " \
        "WHERE a.Archived = 0 AND ad.MovementType NOT IN (2,8) " \
        "AND ad.MovementDate Is Not Null AND ad.ReturnDate Is Not Null " \
        "ORDER BY a.ID")

    for a in animals:
        update_variable_animal_data(dbo, a.id, a, animalupdatebatch, bands, movements)

    dbo.execute_many("UPDATE animal SET " \
        "TimeOnShelter = ?, " \
        "AgeGroup = ?, " \
        "AgeGroupActiveMovement = ?, " \
        "AnimalAge = ?, " \
        "DaysOnShelter = ?, " \
        "TotalTimeOnShelter = ?, " \
        "TotalDaysOnShelter = ? " \
        "WHERE ID = ?", animalupdatebatch)

    asm3.al.debug("updated variable data for %d animals (locale %s)" % (len(animals), l), "animal.update_on_shelter_variable_animal_data", dbo)
    return "OK %d" % len(animals)

def update_offshelter_young_variable_animal_data(dbo: Database) -> str:
    """
    Updates variable animal data for all off-shelter animal 
    records where they are under 9 months old. 
    This is to prevent situations where adopted animal reports
    are showing the stored age for puppies/kittens and shelters 
    are relying on it to decide when to book in a spay/neuter.
    """
    l = dbo.locale
    
    animalupdatebatch = []

    # Load age group bands now to save repeated looped lookups
    bands = asm3.configuration.age_group_bands(dbo)

    # Relevant on shelter animal fields
    animals = dbo.query("SELECT ID, DateBroughtIn, DeceasedDate, DiedOffShelter, Archived, ActiveMovementDate, " \
        "MostRecentEntryDate, DateOfBirth FROM animal WHERE DateOfBirth > ? AND DeceasedDate Is Null AND Archived = 1", [ dbo.today(offset=-274) ])

    # Get a single lookup of movement histories for our on shelter animals
    movements = dbo.query("SELECT ad.AnimalID, ad.MovementDate, ad.ReturnDate " \
        "FROM animal a " \
        "INNER JOIN adoption ad ON a.ID = ad.AnimalID " \
        "WHERE a.Archived = 0 AND ad.MovementType NOT IN (2,8) " \
        "AND ad.MovementDate Is Not Null AND ad.ReturnDate Is Not Null " \
        "ORDER BY a.ID")

    for a in animals:
        update_variable_animal_data(dbo, a.id, a, animalupdatebatch, bands, movements)

    dbo.execute_many("UPDATE animal SET " \
        "TimeOnShelter = ?, " \
        "AgeGroup = ?, " \
        "AgeGroupActiveMovement = ?, " \
        "AnimalAge = ?, " \
        "DaysOnShelter = ?, " \
        "TotalTimeOnShelter = ?, " \
        "TotalDaysOnShelter = ? " \
        "WHERE ID = ?", animalupdatebatch)

    asm3.al.debug("updated variable data for %d animals (locale %s)" % (len(animals), l), "animal.update_offshelter_young_variable_animal_data", dbo)
    return "OK %d" % len(animals)

def update_all_animal_statuses(dbo: Database) -> str:
    """
    Updates statuses for all animals
    """
    animals = dbo.query(get_animal_status_query(dbo))
    movements = dbo.query(get_animal_movement_status_query(dbo) + " ORDER BY MovementDate DESC")
    animalupdatebatch = []
    diaryupdatebatch = []

    asm3.asynctask.set_progress_max(dbo, len(animals))
    for a in animals:
        update_animal_status(dbo, a.id, a, movements, animalupdatebatch, diaryupdatebatch)
        asm3.asynctask.increment_progress_value(dbo)

    aff = dbo.execute_many("UPDATE animal SET " \
        "Archived = ?, " \
        "Adoptable = ?, " \
        "OwnerID = ?, " \
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
    asm3.al.debug("updated %d animal statuses (%d)" % (aff, len(animals)), "animal.update_all_animal_statuses", dbo)
    return "OK %d" % len(animals)

def update_boarding_animal_statuses(dbo: Database) -> str:
    """
    Updates statuses for all animals who are actively boarding. 
    """
    animals = dbo.query(get_animal_status_query(dbo) + \
        " WHERE a.ID IN (SELECT AnimalID FROM animalboarding WHERE InDateTime <= ? AND OutDateTime >= ?)", ( dbo.today(), dbo.today() ))
    movements = dbo.query(get_animal_movement_status_query(dbo) + " WHERE m.AnimalID IN " \
        "(SELECT AnimalID FROM animalboarding WHERE InDateTime <= ? AND OutDateTime >= ?) ORDER BY MovementDate DESC", ( dbo.today(), dbo.today() ))
    animalupdatebatch = []
    diaryupdatebatch = []
    asm3.asynctask.set_progress_max(dbo, len(animals))
    for a in animals:
        update_animal_status(dbo, a.id, a, movements, animalupdatebatch, diaryupdatebatch)
        asm3.asynctask.increment_progress_value(dbo)

    aff = dbo.execute_many("UPDATE animal SET " \
        "Archived = ?, " \
        "Adoptable = ?, " \
        "OwnerID = ?, " \
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
    asm3.al.debug("updated %d on shelter animal statuses (%d)" % (aff, len(animals)), "animal.update_on_shelter_animal_statuses", dbo)
    return "OK %d" % len(animals)

def update_foster_animal_statuses(dbo: Database) -> str:
    """
    Updates statuses for all animals on foster. 
    This function is redundant if foster_on_shelter is set as they 
    will already be updated by update_on_shelter_animal_statuses.
    To counter that, this function only considers fosters/off shelter
    """
    animals = dbo.query(get_animal_status_query(dbo) + " WHERE a.ActiveMovementType = 2 AND a.Archived = 1")
    movements = dbo.query(get_animal_movement_status_query(dbo) + \
        " WHERE AnimalID IN (SELECT ID FROM animal WHERE ActiveMovementType = 2) ORDER BY MovementDate DESC")
    animalupdatebatch = []
    diaryupdatebatch = []

    for a in animals:
        update_animal_status(dbo, a.id, a, movements, animalupdatebatch, diaryupdatebatch)

    aff = dbo.execute_many("UPDATE animal SET " \
        "Archived = ?, " \
        "Adoptable = ?, " \
        "OwnerID = ?, " \
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
    asm3.al.debug("updated %d fostered animal statuses (%d)" % (aff, len(animals)), "animal.update_foster_animal_statuses", dbo)
    return "OK %d" % len(animals)

def update_on_shelter_animal_statuses(dbo: Database) -> str:
    """
    Updates statuses for all animals currently on shelter 
    or scheduled for return from yesterday or newer.
    """
    cutoff = dbo.today(offset=-1)
    animals = dbo.query(get_animal_status_query(dbo) + " WHERE a.Archived = 0 OR (a.Archived = 1 AND a.ActiveMovementReturn > ?)", [cutoff])
    movements = dbo.query(get_animal_movement_status_query(dbo) + \
        " WHERE AnimalID IN (SELECT ID FROM animal WHERE Archived = 0 OR (Archived = 1 AND ActiveMovementReturn > ?)) ORDER BY MovementDate DESC", [cutoff])
    animalupdatebatch = []
    diaryupdatebatch = []
    asm3.asynctask.set_progress_max(dbo, len(animals))
    for a in animals:
        update_animal_status(dbo, a.id, a, movements, animalupdatebatch, diaryupdatebatch)
        asm3.asynctask.increment_progress_value(dbo)

    aff = dbo.execute_many("UPDATE animal SET " \
        "Archived = ?, " \
        "Adoptable = ?, " \
        "OwnerID = ?, " \
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
    asm3.al.debug("updated %d on shelter animal statuses (%d)" % (aff, len(animals)), "animal.update_on_shelter_animal_statuses", dbo)
    return "OK %d" % len(animals)

def update_animal_status(dbo: Database, animalid: int, a: ResultRow = None, movements: Results = None, animalupdatebatch: List[Tuple] = None, diaryupdatebatch: List[Tuple] = None) -> None:
    """
    Updates the movement status fields on an animal record: 
        ActiveMovement*, HasActiveReserve, HasTrialAdoption, MostRecentEntryDate, 
        DiedOffShelter, Adoptable, Archived and DisplayLocation.

    a can be an already loaded animal record with a result from get_animal_status_query
    movements is a list of movements for this animal (and can be for other animals too)
    animalupdatebatch and diaryupdatebatch are lists of parameters that can be passed to
    dbo.execute_many to do all updates in one hit where necessary. If they are passed, we'll
    append our changes to them. If they aren't passed, then we do any database updates now.
    """

    l = dbo.locale
    onshelter = True
    adoptable = False
    diedoffshelter = False
    hasreserve = False
    hastrialadoption = False
    haspermanentfoster = False
    lastreturn = None
    mostrecententrydate = None
    ownerid = 0
    activemovementid = 0
    activemovementdate = None
    activemovementtype = None
    activemovementtypename = None
    activemovementreturn = None
    currentownerid = None
    currentownername = None
    today = dbo.today()
    
    def b2i(x):
        return x and 1 or 0

    if a is None:
        a = get_animal(dbo, animalid)
        if a is None: return

    if movements is None: 
        movements = dbo.query(get_animal_movement_status_query(dbo) + \
            " WHERE AnimalID = ? ORDER BY MovementDate DESC", [animalid])

    # Start at first intake for most recent entry date
    mostrecententrydate = remove_time(a.datebroughtin)

    # Start with the existing value for the current owner
    ownerid = a.ownerid

    cfg_foster_on_shelter = asm3.configuration.foster_on_shelter(dbo)
    cfg_future_on_shelter = asm3.configuration.future_on_shelter(dbo)
    cfg_retailer_on_shelter = asm3.configuration.retailer_on_shelter(dbo)
    cfg_trial_on_shelter = asm3.configuration.trial_on_shelter(dbo)
    cfg_softrelease_on_shelter = asm3.configuration.softrelease_on_shelter(dbo)

    # onshelter defaults to true, which means animals start as onshelter
    # until a movement later takes them off shelter. Animals with an intake
    # date in the future will stay onshelter.
    # If this database has turned off the option to show future intakes as on shelter,
    # then we check the intake date against today and set onshelter accordingly
    if not cfg_future_on_shelter:
        onshelter = today >= remove_time(a.datebroughtin)

    for m in movements:

        # Ignore movements that aren't for this animal
        if m.animalid != animalid: continue

        # Is this an "exit" type movement? ie. A movement that could take the
        # animal out of the care of the shelter? Depending on what system options
        # are set, some movement types do or don't
        exitmovement = False
        if m.movementtype > 0: exitmovement = True
        if m.movementtype == asm3.movement.FOSTER and cfg_foster_on_shelter: exitmovement = False
        elif m.movementtype == asm3.movement.RETAILER and cfg_retailer_on_shelter: exitmovement = False
        elif m.movementtype == asm3.movement.ADOPTION and m.istrial == 1 and cfg_trial_on_shelter: exitmovement = False
        elif m.movementtype == asm3.movement.RELEASED and m.istrial == 1 and cfg_softrelease_on_shelter: exitmovement = False

        # Is this movement active right now?
        if (m.movementdate and m.movementdate <= today and not m.returndate or \
            m.movementdate and m.movementdate <= today and m.returndate > today):

            activemovementid = m.id
            activemovementdate = m.movementdate
            activemovementtype = m.movementtype
            activemovementtypename = m.movementtypename
            activemovementreturn = m.returndate
            currentownerid = m.ownerid
            currentownername = m.ownername

            # Does the animal have a current ownerid? Set it if not and this is an exit movement
            if exitmovement and ownerid is None or ownerid == 0:
                ownerid = currentownerid

            # If this is an exit movement, take the animal off shelter
            # If this active movement is not an exit movement, keep the animal onshelter
            if exitmovement: onshelter = False

            # Is this an active trial adoption?
            if m.movementtype == asm3.movement.ADOPTION and m.istrial == 1:
                hastrialadoption = True

            # Is this a permanent foster?
            if m.movementtype == asm3.movement.FOSTER and m.ispermanentfoster == 1:
                haspermanentfoster = True

            # If the animal is dead, and this is an open exit movement,
            # set the diedoffshelter flag for reports
            if a.deceaseddate and exitmovement:
                diedoffshelter = True

        # Is this movement an active reservation?
        if not m.returndate and m.movementtype == asm3.movement.NO_MOVEMENT \
            and not m.movementdate and m.reservationdate and \
            m.reservationdate <= dbo.today(settime="23:59:59") and \
            (not m.reservationcancelleddate or m.reservationcancelleddate > dbo.today(settime="23:59:59")):
            hasreserve = True

        # Update the last time the animal was returned
        if m.returndate:
            if lastreturn is None: lastreturn = m.returndate
            if m.returndate > lastreturn: lastreturn = m.returndate

        # Update the mostrecententrydate if this is a returned exit movement
        # that is returned later than the current date we have
        if exitmovement and m.returndate and m.returndate > mostrecententrydate and m.returndate <= today:
            mostrecententrydate = m.returndate

    # Override the other flags if this animal is dead or non-shelter
    if a.deceaseddate or a.nonshelteranimal == 1:
        onshelter = False
        hastrialadoption = False
        hasreserve = False
        haspermanentfoster = False

    # On shelter animals cannot have an ownerid
    if onshelter:
        ownerid = 0

    # Non-shelter owner should always match original owner since the user can only change original owner
    if a.nonshelteranimal == 1:
        ownerid = a.originalownerid

    # Non-shelter animals who are deceased have by definition died off the shelter
    if a.nonshelteranimal == 1 and a.deceaseddate:
        diedoffshelter = True

    # Override the onshelter flag if the animal is actively boarding right now and not dead
    if a.hasactiveboarding == 1 and not a.deceaseddate:
        onshelter = True

    # Calculate location and qualified display location
    loc = ""
    qlocname = ""
    if a.deceaseddate:
        loc = _("Deceased", l)
        qlocname = loc
        if a.puttosleep == 1:
            qlocname = "%s::%s" % (qlocname, a.ptsreasonname)
    elif activemovementdate is not None:
        loc = activemovementtypename
        qlocname = loc
        if currentownerid is not None and currentownername is not None:
            qlocname = "%s::%s" % (loc, currentownername)
    else:
        if a.shelterlocationunit and a.shelterlocationunit != "":
            loc = "%s::%s" % (a.shelterlocationname, a.shelterlocationunit)
        else:
            loc = a.shelterlocationname
        qlocname = loc

    # Take a snapshot of our in memory animal
    old = a.copy()

    # Update our in memory animal
    a.archived = b2i(not onshelter)
    a.ownerid = ownerid
    a.activemovementid = activemovementid
    a.activemovementdate = activemovementdate
    a.activemovementtype = activemovementtype
    a.activemovementreturn = activemovementreturn
    a.diedoffshelter = b2i(diedoffshelter)
    a.hasactivereserve = b2i(hasreserve)
    a.hastrialadoption = b2i(hastrialadoption)
    a.haspermanentfoster = b2i(haspermanentfoster)
    a.mostrecententrydate = mostrecententrydate
    a.displaylocation = qlocname

    # Update the adoptable flag (requires a to be updated)
    adoptable = asm3.publishers.base.is_animal_adoptable(dbo, a)
    a.adoptable = b2i(adoptable)

    # Has anything actually changed?
    if old.archived == a.archived and \
        old.adoptable == a.adoptable and \
        old.ownerid == a.ownerid and \
        old.activemovementid == a.activemovementid and \
        old.activemovementdate == a.activemovementdate and \
        old.activemovementtype == a.activemovementtype and \
        old.activemovementreturn == a.activemovementreturn and \
        old.diedoffshelter == a.diedoffshelter and \
        old.hasactivereserve == a.hasactivereserve and \
        old.hastrialadoption == a.hastrialadoption and \
        old.haspermanentfoster == a.haspermanentfoster and \
        old.mostrecententrydate == a.mostrecententrydate and \
        old.displaylocation == a.displaylocation:
        # No - don't do anything
        return

    # Update the location on any diary notes for this animal
    update_diary_linkinfo(dbo, animalid, a, diaryupdatebatch)
  
    # If we have an animal batch going, append to it
    if animalupdatebatch is not None:
        animalupdatebatch.append((
            b2i(not onshelter),
            b2i(adoptable),
            ownerid,
            activemovementid,
            activemovementdate,
            activemovementtype,
            activemovementreturn,
            b2i(diedoffshelter),
            qlocname,
            b2i(hasreserve),
            b2i(hastrialadoption),
            b2i(haspermanentfoster),
            mostrecententrydate,
            animalid
        ))
    else:
        # Just do the DB update now
        dbo.update("animal", animalid, {
            "Archived":             b2i(not onshelter),
            "Adoptable":            b2i(adoptable),
            "OwnerID":              ownerid,
            "ActiveMovementID":     activemovementid,
            "ActiveMovementDate":   activemovementdate,
            "ActiveMovementType":   activemovementtype,
            "ActiveMovementReturn": activemovementreturn,
            "DiedOffShelter":       b2i(diedoffshelter),
            "DisplayLocation":      qlocname,
            "HasActiveReserve":     b2i(hasreserve),
            "HasTrialAdoption":     b2i(hastrialadoption),
            "HasPermanentFoster":   b2i(haspermanentfoster),
            "MostRecentEntryDate":  mostrecententrydate
        })

def get_number_animals_on_shelter(dbo: Database, date: datetime, speciesid: int = 0, animaltypeid: int = 0, internallocationid: int = 0, ageselection: int = 0, startofday: bool = False) -> int:
    """
    Returns the number of animals on shelter. 
    Because this is used for figures reporting only, it does not obey any of the "treat as on shelter"
    config flags and all movements (apart from reservations) are treated as exit movements. This
    is so that the figures report can show intakes and outcomes for foster/retail without double counting.

    date: The date to calculate the inventory for
    animaltypeid: Only for this animal type (0 for all)
    internallocationid: Only for this location (0 for all) 
    ageselection: 0 = allages, 1 = under six months, 2 = over six months
    startofday: True to calculate at the start of the day (intake and outcomes on that day don't count)
    """
    sdate = dbo.sql_date(date, includeTime=False)
    if not startofday:
        sdate = dbo.sql_date(date.replace(hour=23,minute=59,second=59), includeTime=True)
    sixmonthsago = dbo.sql_date(subtract_days(date, 182), includeTime=False)
    sql = "SELECT COUNT(ID) FROM animal WHERE "
    if speciesid != 0:
        sql += "SpeciesID = %d" % speciesid
    else:
        sql += "AnimalTypeID = %d" % animaltypeid
    if startofday:
        sql += " AND DateBroughtIn < %s AND NonShelterAnimal = 0" % sdate # intake today excluded
        sql += " AND (DeceasedDate Is Null OR DeceasedDate > %s)" % sdate # deaths today excluded
        movementclause = "MovementDate < %s" % sdate # movements today excluded
        returnclause = "ReturnDate > %s" % sdate # returns today excluded
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
        "WHERE AnimalID = animal.ID AND MovementType > 0 AND MovementDate Is Not Null AND " \
        "%s AND (ReturnDate Is Null OR %s))" % (movementclause, returnclause)
    return dbo.query_int(sql)

def get_number_litters_on_shelter(dbo: Database, date: datetime, speciesid: int = 0) -> int:
    """
    Returns the number of active litters at a given date, optionally
    for a single species.
    """
    sdate = dbo.sql_date(date, includeTime=False)
    sql = "SELECT COUNT(a.ID) FROM animallitter a " \
        "WHERE a.Date <= %s " % sdate
    if speciesid != 0:
        sql += "AND SpeciesID = %d " % speciesid
    sql += "AND (InvalidDate Is Null OR InvalidDate > %s)" % sdate
    return dbo.query_int(sql)

def get_number_animals_on_foster(dbo: Database, date: datetime, speciesid: int = 0, animaltypeid: int = 0) -> int:
    """
    Returns the number of animals on foster at the end of a given date for a species or type
    """
    sdate = dbo.sql_date(date, includeTime=False)
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
    sql += " MovementType = %d" % asm3.movement.FOSTER
    sql += " AND MovementDate <= %s" % sdate
    sql += " AND AnimalID = animal.ID"
    sql += " AND (ReturnDate > %s OR ReturnDate Is Null))" % sdate
    return dbo.query_int(sql)

def update_animal_figures(dbo: Database, month: int = 0, year: int = 0) -> str:
    """
    Updates the animal figures table for the month and year given.
    If month and year aren't given, defaults to this month, unless today is
    the first day of the month in which case we do last month.
    """
    asm3.asynctask.set_progress_max(dbo, 3)
    batch = []
    nid = dbo.get_id_max("animalfigures")

    def sql_days(sql: str) -> dict:
        """ Returns a query with THEDATE and TOTAL as a dictionary for add_row """
        d = {}
        for i in range(1, 32):
            d["D%d" % i] = 0
        rows = dbo.query(sql)
        for r in rows:
            dk = "D%d" % r["THEDATE"].day
            if dk not in d: d[dk] = 0
            d[dk] += int(r["TOTAL"])
        return d

    def add_days(listdays: List[dict]) -> dict:
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

    def is_zero_days(days: dict) -> bool:
        """ Returns true if a map of day counts is all zero """
        for i in range(1, 32):
            dk = "D%d" % i
            if dk in days and int(days[dk]) > 0:
                return False
        return True

    def sub_days(initdic: dict, subdic: dict) -> dict:
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

    def add_row(orderindex: int, code: str, animaltypeid: int, speciesid: int, maxdaysinmonth: int, heading: str, bold: int, calctotal: int, days: dict) -> None:
        """ Adds a row to the animalfigures table """
        if "D29" not in days: days["D29"] = 0
        if "D30" not in days: days["D30"] = 0
        if "D31" not in days: days["D31"] = 0
        avg = 0.0
        tot = 0
        total = ""
        for i in range(1, maxdaysinmonth + 1):
            tot += int(days["D%d" % i])
        if calctotal:
            total = str(tot)
        avg = round(float(float(tot) / float(maxdaysinmonth)), 1)
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
                
    def update_db(month: int, year: int) -> None:
        """ Writes all of our figures to the database """
        dbo.execute("DELETE FROM animalfigures WHERE Month = ? AND Year = ?", (month, year))
        sql = "INSERT INTO animalfigures (ID, Month, Year, OrderIndex, Code, AnimalTypeID, " \
            "SpeciesID, MaxDaysInMonth, Heading, Bold, D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, " \
            "D11, D12, D13, D14, D15, D16, D17, D18, D19, D20, D21, D22, D23, D24, D25, D26, " \
            "D27, D28, D29, D30, D31, Total, Average) VALUES (?,?,?,?,?,?," \
            "?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, "\
            "?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, "\
            "?,?,?,?,?,?,?)"
        dbo.execute_many(sql, batch)
        asm3.al.debug("wrote %d figures records" % len(batch), "animal.update_animal_figures", dbo)

    # If month and year are zero, figure out which one we're going
    # to generate for. We use this month, unless today is the first
    # of the month, in which case we do last month
    if month == 0 and year == 0:
        today = dbo.today()
        if today.day == 1: today = subtract_months(today, 1)
        month = today.month
        year = today.year
    asm3.al.debug("Generating animal figures for month=%d, year=%d" % (month, year), "animal.update_animal_figures", dbo)

    l = dbo.locale
    fom = datetime(year, month, 1)
    lom = last_of_month(fom)
    lom = lom.replace(hour=23, minute=59, second=59)
    firstofmonth = dbo.sql_date(fom)
    lastofmonth = dbo.sql_date(lom)
    daysinmonth = lom.day
    loopdays = daysinmonth + 1

    # Species =====================================
    allspecies = asm3.lookups.get_species(dbo)
    for sp in allspecies:

        speciesid = int(sp["ID"])

        # If we never had anything for this species, skip it
        if 0 == dbo.query_int("SELECT COUNT(*) FROM animal WHERE SpeciesID = ?", [speciesid]):
            continue

        # On Shelter
        onshelter = {}
        for i in range(1, loopdays):
            d = datetime(year, month, i)
            dk = "D%d" % i
            onshelter[dk] = get_number_animals_on_shelter(dbo, d, speciesid)
        add_row(1, "SP_ONSHELTER", 0, speciesid, daysinmonth, _("On Shelter", l), 0, False, onshelter)

        # On Foster
        onfoster = {}
        for i in range(1, loopdays):
            d = datetime(year, month, i)
            dk = "D%d" % i
            onfoster[dk] = get_number_animals_on_foster(dbo, d, speciesid)
        add_row(2, "SP_ONFOSTER", 0, speciesid, daysinmonth, _("On Foster", l), 0, False, onfoster)
        # NOTE: On Foster counts are not added to the day counts deliberately.
        # Start/End of day counts only track on shelter animals.
        # If fosters were added, then fosters moving in and out of the shelter would be double counted.
        #sheltertotal = add_days((onshelter, onfoster))
        sheltertotal = onshelter

        # Litters
        litters = {}
        for i in range(1, loopdays):
            d = datetime(year, month, i)
            dk = "D%d" % i
            litters[dk] = get_number_litters_on_shelter(dbo, d, speciesid)
        add_row(3, "SP_LITTERS", 0, speciesid, daysinmonth, _("Litters", l), 0, False, litters)

        # Start of day total - handled at the end.

        # Brought In
        # If the config option is on, output a row for each entry
        # category or a single line for brought in.
        if asm3.configuration.animal_figures_split_entryreason(dbo):
            reasons = asm3.lookups.get_entryreasons(dbo)
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
            "GROUP BY ReturnDate" % (speciesid, firstofmonth, lastofmonth, asm3.movement.ADOPTION))
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
            "GROUP BY ReturnDate" % (speciesid, asm3.movement.FOSTER, firstofmonth, lastofmonth))
        add_row(108, "SP_RETURNEDFOSTER", 0, speciesid, daysinmonth, _("From Fostering", l), 0, True, returnedfoster)

        # Returned From Other
        returnedother = sql_days("SELECT ReturnDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType <> %d AND MovementType <> %d " \
            "AND ReturnDate >= %s AND ReturnDate <= %s " \
            "GROUP BY ReturnDate" % (speciesid, asm3.movement.FOSTER, asm3.movement.ADOPTION, firstofmonth, lastofmonth))
        add_row(109, "SP_RETURNEDOTHER", 0, speciesid, daysinmonth, _("From Other", l), 0, True, returnedother)

        # In subtotal
        insubtotal = add_days((broughtin, returned, transferin, returnedfoster, returnedother))
        add_row(110, "SP_INTOTAL", 0, speciesid, daysinmonth, _("In SubTotal", l), 1, False, insubtotal)

        # Adopted
        adopted = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (speciesid, asm3.movement.ADOPTION, firstofmonth, lastofmonth))
        add_row(111, "SP_ADOPTED", 0, speciesid, daysinmonth, _("Adopted", l), 0, True, adopted)

        # Reclaimed
        reclaimed = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (speciesid, asm3.movement.RECLAIMED, firstofmonth, lastofmonth))
        add_row(112, "SP_RECLAIMED", 0, speciesid, daysinmonth, _("Returned To Owner", l), 0, True, reclaimed)

        # Escaped
        escaped = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (speciesid, asm3.movement.ESCAPED, firstofmonth, lastofmonth))
        add_row(113, "SP_ESCAPED", 0, speciesid, daysinmonth, _("Escaped", l), 0, True, escaped)

        # Stolen
        stolen = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (speciesid, asm3.movement.STOLEN, firstofmonth, lastofmonth))
        add_row(114, "SP_STOLEN", 0, speciesid, daysinmonth, _("Stolen", l), 0, True, stolen)

        # Released
        released = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (speciesid, asm3.movement.RELEASED, firstofmonth, lastofmonth))
        add_row(115, "SP_RELEASED", 0, speciesid, daysinmonth, _("Released To Wild", l), 0, True, released)

        # Transferred
        transferred = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (speciesid, asm3.movement.TRANSFER, firstofmonth, lastofmonth))
        add_row(116, "SP_TRANSFERRED", 0, speciesid, daysinmonth, _("Transferred Out", l), 0, True, transferred)

        # Fostered
        fostered = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (speciesid, asm3.movement.FOSTER, firstofmonth, lastofmonth))
        add_row(117, "SP_FOSTERED", 0, speciesid, daysinmonth, _("To Fostering", l), 0, True, fostered)

        # Retailer
        retailer = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "SpeciesID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (speciesid, asm3.movement.RETAILER, firstofmonth, lastofmonth))
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

    asm3.asynctask.set_progress_value(dbo, 1)

    # Animal Types =====================================
    alltypes = asm3.lookups.get_animal_types(dbo)
    for at in alltypes:

        typeid = at.id

        # If we never had anything for this type, skip it
        if 0 == dbo.query_int("SELECT COUNT(*) FROM animal WHERE AnimalTypeID = ?", [typeid]):
            continue

        # On Shelter
        onshelter = {}
        for i in range(1, loopdays):
            d = datetime(year, month, i)
            dk = "D%d" % i
            onshelter[dk] = get_number_animals_on_shelter(dbo, d, 0, typeid)
        add_row(1, "AT_ONSHELTER", typeid, 0, daysinmonth, _("On Shelter", l), 0, False, onshelter)

        # On Foster
        onfoster = {}
        for i in range(1, loopdays):
            d = datetime(year, month, i)
            dk = "D%d" % i
            onfoster[dk] = get_number_animals_on_foster(dbo, d, 0, typeid)
        add_row(2, "AT_ONFOSTER", typeid, 0, daysinmonth, _("On Foster", l), 0, False, onfoster)
        #sheltertotal = add_days((onshelter, onfoster))
        sheltertotal = onshelter

        # Start of day - handled later

        # Brought In
        # If the config option is on, output a row for each entry
        # category or a single line for brought in.
        if asm3.configuration.animal_figures_split_entryreason(dbo):
            reasons = asm3.lookups.get_entryreasons(dbo)
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
            "GROUP BY ReturnDate" % (typeid, firstofmonth, lastofmonth, asm3.movement.ADOPTION))
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
            "GROUP BY ReturnDate" % (typeid, asm3.movement.FOSTER, firstofmonth, lastofmonth))
        add_row(8, "AT_RETURNEDFOSTER", typeid, 0, daysinmonth, _("From Fostering", l), 0, True, returnedfoster)

        # Returned From Other
        returnedother = sql_days("SELECT ReturnDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType <> %d AND MovementType <> %d " \
            "AND ReturnDate >= %s AND ReturnDate <= %s " \
            "GROUP BY ReturnDate" % (typeid, asm3.movement.FOSTER, asm3.movement.ADOPTION, firstofmonth, lastofmonth))
        add_row(9, "AT_RETURNEDOTHER", typeid, 0, daysinmonth, _("From Other", l), 0, True, returnedother)

        # In subtotal
        insubtotal = add_days((broughtin, returned, transferin, returnedfoster, returnedother))
        add_row(10, "AT_INTOTAL", typeid, 0, daysinmonth, _("SubTotal", l), 1, False, insubtotal)

        # Adopted
        adopted = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (typeid, asm3.movement.ADOPTION, firstofmonth, lastofmonth))
        add_row(11, "AT_ADOPTED", typeid, 0, daysinmonth, _("Adopted", l), 0, True, adopted)

        # Reclaimed
        reclaimed = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (typeid, asm3.movement.RECLAIMED, firstofmonth, lastofmonth))
        add_row(12, "AT_RECLAIMED", typeid, 0, daysinmonth, _("Returned To Owner", l), 0, True, reclaimed)

        # Escaped
        escaped = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (typeid, asm3.movement.ESCAPED, firstofmonth, lastofmonth))
        add_row(13, "AT_ESCAPED", typeid, 0, daysinmonth, _("Escaped", l), 0, True, escaped)

        # Stolen
        stolen = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (typeid, asm3.movement.STOLEN, firstofmonth, lastofmonth))
        add_row(14, "AT_STOLEN", typeid, 0, daysinmonth, _("Stolen", l), 0, True, stolen)

        # Released
        released = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (typeid, asm3.movement.RELEASED, firstofmonth, lastofmonth))
        add_row(15, "AT_RELEASED", typeid, 0, daysinmonth, _("Released To Wild", l), 0, True, released)

        # Transferred
        transferred = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (typeid, asm3.movement.TRANSFER, firstofmonth, lastofmonth))
        add_row(16, "AT_TRANSFERRED", typeid, 0, daysinmonth, _("Transferred Out", l), 0, True, transferred)

        # Fostered
        fostered = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (typeid, asm3.movement.FOSTER, firstofmonth, lastofmonth))
        add_row(17, "AT_FOSTERED", typeid, 0, daysinmonth, _("To Fostering", l), 0, True, fostered)

        # Retailer
        retailer = sql_days("SELECT MovementDate AS TheDate, COUNT(adoption.ID) AS Total FROM adoption " \
            "INNER JOIN animal ON animal.ID = adoption.AnimalID WHERE " \
            "AnimalTypeID = %d AND MovementType = %d " \
            "AND MovementDate >= %s AND MovementDate <= %s " \
            "GROUP BY MovementDate" % (typeid, asm3.movement.RETAILER, firstofmonth, lastofmonth))
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

    asm3.asynctask.set_progress_value(dbo, 2)

    # Write out our db changes
    update_db(month, year)
    return "OK"

def update_animal_figures_annual(dbo: Database, year: int = 0) -> str:
    """
    Updates the animal figures annual table for the year given.
    If year isn't given, defaults to this year, unless today is the
    first of the year in which case we do last year.
    """
    asm3.asynctask.set_progress_max(dbo, 3)
    batch = []
    nid = dbo.get_id_max("animalfiguresannual")

    def add_row(orderindex: int, code: str, animaltypeid: int, speciesid: int, entryreasonid: int, group: str, heading: str, bold: int, months: List[int]) -> None:
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

    def sql_months(sql: str, babysplit: bool = False, babymonths: int = 4) -> Tuple[List[int], List[int]]:
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
        rows = dbo.query(sql)
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

    def entryreason_line(sql: str, entryreasonid: int, reasonname: str, code: str, group: str, orderindex: int, showbabies: bool, babymonths: int) -> None:
        """
        Adds a line for a particular entry reason.
        sql: The query to run
        """
        babyname = _("{0} (under {1} months)", l).format(reasonname, babymonths)
        lines = sql_months(sql, showbabies, babymonths)
        add_row(orderindex, code, 0, 0, entryreasonid, group, reasonname, 0, lines[0])
        if showbabies: add_row(orderindex, code + "_BABY", 0, 0, entryreasonid, group, babyname, 0, lines[1])

    def species_line(sql: str, speciesid: int, speciesname: str, code: str, group: str, orderindex: int, showbabies: bool, babymonths: int) -> None:
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

    def type_line(sql: str, typeid: int, typename: str, code: str, group: str, orderindex: int, showbabies: bool, babymonths: int) -> None:
        """
        Adds a line for a particular type.
        sql: The query to run
        """
        babyname = _("{0} (under {1} months)", l).format(typename, babymonths)
        lines = sql_months(sql, showbabies, babymonths)
        add_row(orderindex, code, typeid, 0, 0, group, typename, 0, lines[0])
        if showbabies: add_row(orderindex, code + "_BABY", typeid, 0, 0, group, babyname, 0, lines[1])

    def update_db(year: int) -> None:
        """ Writes all of our figures to the database """
        dbo.execute("DELETE FROM animalfiguresannual WHERE Year = ?", [year])
        sql = "INSERT INTO animalfiguresannual (ID, Year, OrderIndex, Code, AnimalTypeID, " \
            "SpeciesID, EntryReasonID, GroupHeading, Heading, Bold, M1, M2, M3, M4, M5, M6, M7, M8, M9, M10, " \
            "M11, M12, Total) VALUES (?,?,?,?,?,?," \
            "?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        dbo.execute_many(sql, batch)
        asm3.al.debug("wrote %d annual figures records" % len(batch), "animal.update_animal_figures_annual", dbo)

    # If year is zero, figure out which one we're going
    # to generate for. We use this year, unless today is the first
    # of the year, in which case we do last year.
    l = dbo.locale
    if year == 0:
        today = dbo.today()
        if today.day == 1 and today.month == 1: today = subtract_years(today, 1)
        year = today.year
    asm3.al.debug("Generating animal figures annual for year=%d" % year, "animal.update_animal_figures_annual", dbo)

    # Work out the full year
    foy = datetime(year, 1, 1)
    loy = datetime(year, 12, 31, 23, 59, 59)
    firstofyear = dbo.sql_date(foy)
    lastofyear = dbo.sql_date(loy)

    # Are we splitting between baby and adult animals?
    showbabies = asm3.configuration.annual_figures_show_babies(dbo)
    showbabiestype = asm3.configuration.annual_figures_show_babies_type(dbo)
    babymonths = asm3.configuration.annual_figures_baby_months(dbo)
    splitadoptions = asm3.configuration.annual_figures_split_adoptions(dbo)

    # Species =====================================
    allspecies = asm3.lookups.get_species(dbo)
    group = _("Intakes {0}", l).format(year)
    for sp in allspecies:
        exclude_tnr = ""
        # Not sure why we were doing this - it means TNR intakes were excluded for no reason that makes any sense
        # if sp["ID"] == 2: exclude_tnr = "AND NOT EXISTS(SELECT ID FROM adoption WHERE AnimalID=a.ID AND MovementType=7)"
        species_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND a.IsTransfer = 0 AND a.NonShelterAnimal = 0 %s " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear, exclude_tnr),
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

    group = _("Returns (Adoption) {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT ad.ReturnDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.SpeciesID = %d AND ad.ReturnDate Is Not Null AND ad.ReturnDate >= %s AND ad.ReturnDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = 1 AND ad.IsTrial = 0 " \
            "GROUP BY ad.ReturnDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_RETURNADOPT", group, 40, showbabies, babymonths)
        
    group = _("Returns (Reclaim) {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT ad.ReturnDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.SpeciesID = %d AND ad.ReturnDate Is Not Null AND ad.ReturnDate >= %s AND ad.ReturnDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = 5 " \
            "GROUP BY ad.ReturnDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_RETURNRECLAIM", group, 43, showbabies, babymonths)

    group = _("Transferred In {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND a.IsTransfer = 1 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_TRANSFERIN", group, 45, showbabies, babymonths)

    if splitadoptions:
        group = _("Adopted Transferred In {0}", l).format(year)
        for sp in allspecies:
            species_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
                "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
                "a.SpeciesID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
                "AND a.IsTransfer = 1 AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
                "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear, asm3.movement.ADOPTION),
                sp["ID"], sp["SPECIESNAME"], "SP_TRANSFERINADOPTED", group, 47, showbabies, babymonths)

    group = _("Adoptions {0}", l).format(year)
    for sp in allspecies:
        adoptionsplittransferclause = splitadoptions and "AND IsTransfer = 0 " or ""
        species_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.SpeciesID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "%sAND a.NonShelterAnimal = 0 AND ad.MovementType = %d AND ad.IsTrial = 0 " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear, adoptionsplittransferclause, asm3.movement.ADOPTION),
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
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear, asm3.movement.RECLAIMED),
            sp["ID"], sp["SPECIESNAME"], "SP_RECLAIMED", group, 90, showbabies, babymonths)

    group = _("Transferred Out {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.SpeciesID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear, asm3.movement.TRANSFER),
            sp["ID"], sp["SPECIESNAME"], "SP_TRANSFEROUT", group, 100, showbabies, babymonths)

    group = _("Escaped {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.SpeciesID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear, asm3.movement.ESCAPED),
            sp["ID"], sp["SPECIESNAME"], "SP_ESCAPED", group, 110, showbabies, babymonths)

    group = _("Stolen {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.SpeciesID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear, asm3.movement.STOLEN),
            sp["ID"], sp["SPECIESNAME"], "SP_STOLEN", group, 120, showbabies, babymonths)

    group = _("Released To Wild {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.SpeciesID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear, asm3.movement.RELEASED),
            sp["ID"], sp["SPECIESNAME"], "SP_STOLEN", group, 130, showbabies, babymonths)

    group = _("Live Outcomes {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.SpeciesID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType IN (%d, %d,  %d) " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear, asm3.movement.ADOPTION, asm3.movement.TRANSFER, asm3.movement.RECLAIMED),
            sp["ID"], sp["SPECIESNAME"], "SP_LIVERELEASE", group, 160, showbabies, babymonths)

    group = _("Neutered/Spayed Shelter Animals In {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT a.NeuteredDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.NeuteredDate >= %s AND a.NeuteredDate <= %s " \
            "AND a.NeuteredDate >= a.DateBroughtIn " \
            "AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.NeuteredDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_NEUTERSPAYSA", group, 170, showbabies, babymonths)

    group = _("Neutered/Spayed Non-Shelter Animals In {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT a.NeuteredDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.NeuteredDate >= %s AND a.NeuteredDate <= %s " \
            "AND a.NonShelterAnimal = 1 " \
            "GROUP BY a.NeuteredDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_NEUTERSPAYNS", group, 180, showbabies, babymonths)

    group = _("Microchipped Shelter Animals In {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT a.IdentichipDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.IdentichipDate >= %s AND a.IdentichipDate <= %s " \
            "AND a.Identichipped = 1 " \
            "AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.IdentichipDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_MICROCHIPS", group, 190, showbabies, babymonths)

    group = _("Microchipped Non-Shelter Animals In {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT a.IdentichipDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.IdentichipDate >= %s AND a.IdentichipDate <= %s " \
            "AND a.Identichipped = 1 " \
            "AND a.NonShelterAnimal = 1 " \
            "GROUP BY a.IdentichipDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_MICROCHIPSNS", group, 192, showbabies, babymonths)

    group = _("Euthanized Non-Shelter Animals in {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT a.DeceasedDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.DeceasedDate >= %s AND a.DeceasedDate <= %s " \
            "AND a.PutToSleep = 1 AND a.NonShelterAnimal = 1 " \
            "GROUP BY a.DeceasedDate, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_EUTHNS", group, 195, showbabies, babymonths)

    group = _("Vaccinated Shelter Animals In {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND EXISTS(SELECT ID FROM animalvaccination WHERE AnimalID=a.ID AND DateOfVaccination Is Not Null) " \
            "AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_VACCSA", group, 200, showbabies, babymonths)

    group = _("Vaccinated Non-Shelter Animals In {0}", l).format(year)
    for sp in allspecies:
        species_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.SpeciesID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND EXISTS(SELECT ID FROM animalvaccination WHERE AnimalID=a.ID AND DateOfVaccination Is Not Null) " \
            "AND a.NonShelterAnimal = 1 " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(sp["ID"]), firstofyear, lastofyear),
            sp["ID"], sp["SPECIESNAME"], "SP_VACCNS", group, 210, showbabies, babymonths)

    asm3.asynctask.set_progress_value(dbo, 1)

    # Types =====================================
    alltypes = asm3.lookups.get_animal_types(dbo)
    for at in alltypes:
        # Find the last species this type referred to. If it was a dog or cat
        # species and we're splitting types for puppies/kittens, then mark the
        # type as appropriate for splitting.
        at["SPECIESID"] = dbo.query_int("SELECT SpeciesID FROM animal WHERE AnimalTypeID = %d ORDER BY ID DESC %s" % (at.id, dbo.sql_limit(1)))
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

    group = _("Returns (Adoption) {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT ad.ReturnDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.AnimalTypeID = %d AND ad.ReturnDate Is Not Null AND ad.ReturnDate >= %s AND ad.ReturnDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = 1 AND ad.IsTrial = 0 " \
            "GROUP BY ad.ReturnDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_RETURNADOPT", group, 40, at["SHOWSPLIT"], babymonths)

    group = _("Returns (Reclaim) {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT ad.ReturnDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.AnimalTypeID = %d AND ad.ReturnDate Is Not Null AND ad.ReturnDate >= %s AND ad.ReturnDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = 5 " \
            "GROUP BY ad.ReturnDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_RETURNRECLAIM", group, 43, at["SHOWSPLIT"], babymonths)

    group = _("Transferred In {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.AnimalTypeID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND a.IsTransfer = 1 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_TRANSFERIN", group, 45, at["SHOWSPLIT"], babymonths)

    if splitadoptions:
        group = _("Adopted Transferred In {0}", l).format(year)
        for at in alltypes:
            type_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
                "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
                "a.AnimalTypeID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
                "AND a.IsTransfer = 1 AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
                "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear, asm3.movement.ADOPTION),
                at["ID"], at["ANIMALTYPE"], "AT_TRANSFERINADOPTED", group, 47, at["SHOWSPLIT"], babymonths)

    group = _("Adoptions {0}", l).format(year)
    for at in alltypes:
        adoptionsplittransferclause = splitadoptions and "AND IsTransfer = 0 " or ""
        type_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.AnimalTypeID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "%sAND a.NonShelterAnimal = 0 AND ad.MovementType = %d AND ad.IsTrial = 0 " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear, adoptionsplittransferclause, asm3.movement.ADOPTION),
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
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear, asm3.movement.RECLAIMED),
            at["ID"], at["ANIMALTYPE"], "AT_RECLAIMED", group, 90, at["SHOWSPLIT"], babymonths)

    group = _("Transferred Out {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.AnimalTypeID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear, asm3.movement.TRANSFER),
            at["ID"], at["ANIMALTYPE"], "AT_TRANSFEROUT", group, 100, at["SHOWSPLIT"], babymonths)

    group = _("Escaped {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.AnimalTypeID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear, asm3.movement.ESCAPED),
            at["ID"], at["ANIMALTYPE"], "AT_ESCAPED", group, 110, at["SHOWSPLIT"], babymonths)

    group = _("Stolen {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.AnimalTypeID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear, asm3.movement.STOLEN),
            at["ID"], at["ANIMALTYPE"], "AT_STOLEN", group, 120, at["SHOWSPLIT"], babymonths)

    group = _("Released To Wild {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.AnimalTypeID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear, asm3.movement.RELEASED),
            at["ID"], at["ANIMALTYPE"], "AT_STOLEN", group, 130, at["SHOWSPLIT"], babymonths)

    group = _("Live Outcomes {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.AnimalTypeID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType in (%d, %d, %d) " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear, asm3.movement.ADOPTION, asm3.movement.TRANSFER, asm3.movement.RECLAIMED),
            at["ID"], at["ANIMALTYPE"], "AT_LIVERELEASE", group, 160, at["SHOWSPLIT"], babymonths)

    group = _("Neutered/Spayed Shelter Animals In {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT a.NeuteredDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.AnimalTypeID = %d AND a.NeuteredDate >= %s AND a.NeuteredDate <= %s " \
            "AND a.NeuteredDate >= a.DateBroughtIn " \
            "AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.NeuteredDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_NEUTERSPAYSA", group, 170, at["SHOWSPLIT"], babymonths)

    group = _("Neutered/Spayed Non-Shelter Animals In {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT a.NeuteredDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.AnimalTypeID = %d AND a.NeuteredDate >= %s AND a.NeuteredDate <= %s " \
            "AND a.NonShelterAnimal = 1 " \
            "GROUP BY a.NeuteredDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_NEUTERSPAYNS", group, 180, at["SHOWSPLIT"], babymonths)

    group = _("Microchipped Shelter Animals In {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT a.IdentichipDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.AnimalTypeID = %d AND a.IdentichipDate >= %s AND a.IdentichipDate <= %s " \
            "AND a.Identichipped = 1 " \
            "AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.IdentichipDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_MICROCHIPS", group, 190, at["SHOWSPLIT"], babymonths)

    group = _("Microchipped Non-Shelter Animals In {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT a.IdentichipDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.AnimalTypeID = %d AND a.IdentichipDate >= %s AND a.IdentichipDate <= %s " \
            "AND a.Identichipped = 1 " \
            "AND a.NonShelterAnimal = 1 " \
            "GROUP BY a.IdentichipDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_MICROCHIPSNS", group, 192, at["SHOWSPLIT"], babymonths)

    group = _("Euthanized Non-Shelter Animals in {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT a.DeceasedDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.AnimalTypeID = %d AND a.DeceasedDate >= %s AND a.DeceasedDate <= %s " \
            "AND a.PutToSleep = 1 AND a.NonShelterAnimal = 1 " \
            "GROUP BY a.DeceasedDate, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_EUTHNS", group, 195, at["SHOWSPLIT"], babymonths)

    group = _("Vaccinated Shelter Animals In {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.AnimalTypeID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND EXISTS(SELECT ID FROM animalvaccination WHERE AnimalID=a.ID AND DateOfVaccination Is Not Null) " \
            "AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_VACCSA", group, 200, at["SHOWSPLIT"], babymonths)

    group = _("Vaccinated Non-Shelter Animals In {0}", l).format(year)
    for at in alltypes:
        type_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.AnimalTypeID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND EXISTS(SELECT ID FROM animalvaccination WHERE AnimalID=a.ID AND DateOfVaccination Is Not Null) " \
            "AND a.NonShelterAnimal = 1 " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(at["ID"]), firstofyear, lastofyear),
            at["ID"], at["ANIMALTYPE"], "AT_VACCNS", group, 210, at["SHOWSPLIT"], babymonths)

    asm3.asynctask.set_progress_value(dbo, 2)

    # Entry Reasons =====================================
    allreasons = asm3.lookups.get_entryreasons(dbo)
    for er in allreasons:
        # Find the last species this reason referred to. If it was a dog or cat
        # species and we're splitting types for puppies/kittens, then mark the
        # reason as appropriate for splitting.
        er["SPECIESID"] = dbo.query_int("SELECT SpeciesID FROM animal WHERE EntryReasonID = %d ORDER BY ID DESC %s" % (er.id, dbo.sql_limit(1)))
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

    group = _("Returns (Adoption) {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT ad.ReturnDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.EntryReasonID = %d AND ad.ReturnDate Is Not Null AND ad.ReturnDate >= %s AND ad.ReturnDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = 1 AND ad.IsTrial = 0 " \
            "GROUP BY ad.ReturnDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear),
            er["ID"], er["REASONNAME"], "ER_RETURNADOPT", group, 40, er["SHOWSPLIT"], babymonths)
        
    group = _("Returns (Reclaim) {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT ad.ReturnDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.EntryReasonID = %d AND ad.ReturnDate Is Not Null AND ad.ReturnDate >= %s AND ad.ReturnDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = 5 " \
            "GROUP BY ad.ReturnDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear),
            er["ID"], er["REASONNAME"], "ER_RETURNRECLAIM", group, 43, er["SHOWSPLIT"], babymonths)

    group = _("Transferred In {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT a.DateBroughtIn AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(a.ID) AS Total FROM animal a WHERE " \
            "a.EntryReasonID = %d AND a.DateBroughtIn >= %s AND a.DateBroughtIn <= %s " \
            "AND a.IsTransfer = 1 AND a.NonShelterAnimal = 0 " \
            "GROUP BY a.DateBroughtIn, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear),
            er["ID"], er["REASONNAME"], "ER_TRANSFERIN", group, 45, er["SHOWSPLIT"], babymonths)

    if splitadoptions:
        group = _("Adopted Transferred In {0}", l).format(year)
        for er in allreasons:
            entryreason_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
                "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
                "a.EntryReasonID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
                "AND a.IsTransfer = 1 AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
                "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear, asm3.movement.ADOPTION),
                er["ID"], er["REASONNAME"], "ER_TRANSFERINADOPTED", group, 47, er["SHOWSPLIT"], babymonths)

    group = _("Adoptions {0}", l).format(year)
    for er in allreasons:
        adoptionsplittransferclause = splitadoptions and "AND IsTransfer = 0 " or ""
        entryreason_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.EntryReasonID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "%sAND a.NonShelterAnimal = 0 AND ad.MovementType = %d AND ad.IsTrial = 0 " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear, adoptionsplittransferclause, asm3.movement.ADOPTION),
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
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear, asm3.movement.RECLAIMED),
            er["ID"], er["REASONNAME"], "ER_RECLAIMED", group, 90, er["SHOWSPLIT"], babymonths)

    group = _("Transferred Out {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.EntryReasonID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear, asm3.movement.TRANSFER),
            er["ID"], er["REASONNAME"], "ER_TRANSFEROUT", group, 100, er["SHOWSPLIT"], babymonths)

    group = _("Escaped {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.EntryReasonID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear, asm3.movement.ESCAPED),
            er["ID"], er["REASONNAME"], "ER_ESCAPED", group, 110, er["SHOWSPLIT"], babymonths)

    group = _("Stolen {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.EntryReasonID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear, asm3.movement.STOLEN),
            er["ID"], er["REASONNAME"], "ER_STOLEN", group, 120, er["SHOWSPLIT"], babymonths)

    group = _("Released To Wild {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.EntryReasonID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType = %d " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear, asm3.movement.RELEASED),
            er["ID"], er["REASONNAME"], "ER_STOLEN", group, 130, er["SHOWSPLIT"], babymonths)

    group = _("Live Outcomes {0}", l).format(year)
    for er in allreasons:
        entryreason_line("SELECT ad.MovementDate AS TheDate, a.DateOfBirth AS DOB, " \
            "COUNT(ad.ID) AS Total FROM animal a INNER JOIN adoption ad ON ad.AnimalID = a.ID WHERE " \
            "a.EntryReasonID = %d AND ad.MovementDate >= %s AND ad.MovementDate <= %s " \
            "AND a.NonShelterAnimal = 0 AND ad.MovementType IN (%d, %d, %d) " \
            "GROUP BY ad.MovementDate, a.DateOfBirth" % (int(er["ID"]), firstofyear, lastofyear, asm3.movement.ADOPTION, asm3.movement.TRANSFER, asm3.movement.RECLAIMED),
            er["ID"], er["REASONNAME"], "ER_LIVERELEASE", group, 160, er["SHOWSPLIT"], babymonths)
    
    asm3.asynctask.set_progress_value(dbo, 3)

    # Write out all our changes in one go
    update_db(year)
    return "OK"

def auto_cancel_holds(dbo: Database) -> None:
    """
    Automatically cancels holds after the hold until date value set
    """
    sql = "UPDATE animal SET IsHold = 0 WHERE IsHold = 1 AND " \
        "HoldUntilDate Is Not Null AND " \
        "HoldUntilDate <= ?"
    count = dbo.execute(sql, [dbo.today()])
    asm3.al.debug("cancelled %d holds" % (count), "animal.auto_cancel_holds", dbo)

def maintenance_reset_nnn_codes(dbo: Database) -> str:
    """
    Resets the NNN shelter codes for this year.
    """
    changed = dbo.execute("UPDATE animal SET YearCodeID = 0 WHERE DateBroughtIn >= ?", [ first_of_year(dbo.today()) ] )
    asm3.al.debug("Reset %d NNN codes" % changed, "animal.maintenance_reset_nnn_codes", dbo)
    return "OK %d" % changed

def maintenance_reassign_all_codes(dbo: Database) -> None:
    """
    Goes through all animals in the system and regenerates their 
    shelter codes.
    """
    dbo.execute("UPDATE animal SET YearCodeID = 0, UniqueCodeID = 0, " \
        "ShelterCode = ID, ShortCode = ID")
    animals = dbo.query("SELECT ID, AnimalTypeID, DateBroughtIn, AnimalName " \
        "FROM animal ORDER BY ID")
    for a in animals:
        sheltercode, shortcode, unique, year = calc_shelter_code(dbo, a.animaltypeid, a.entryreasonid, a.speciesid, a.datebroughtin)
        dbo.update("animal", a.id, {
            "ShelterCode":      sheltercode,
            "ShortCode":        shortcode,
            "UniqueCodeID":     unique,
            "YearCodeID":       year
        })
        asm3.al.debug("RECODE: %s -> %s" % (a.animalname, sheltercode), "animal.maintenance_reassign_all_codes", dbo)

def maintenance_reassign_shelter_codes(dbo: Database) -> None:
    """
    Goes through all animals on the shelter and regenerates their 
    shelter codes.
    """
    dbo.execute("UPDATE animal SET YearCodeID = 0, UniqueCodeID = 0, " \
        "ShelterCode = ID, ShortCode = ID")
    animals = dbo.query("SELECT ID, AnimalTypeID, DateBroughtIn, AnimalName " \
        "FROM animal WHERE Archived = 0 ORDER BY ID")
    for a in animals:
        sheltercode, shortcode, unique, year = calc_shelter_code(dbo, a.animaltypeid, a.entryreasonid, a.speciesid, a.datebroughtin)
        dbo.update("animal", a.id, {
            "ShelterCode":      sheltercode,
            "ShortCode":        shortcode,
            "UniqueCodeID":     unique,
            "YearCodeID":       year
        })
        asm3.al.debug("RECODE: %s -> %s" % (a.animalname, sheltercode), "animal.maintenance_reassign_all_codes", dbo)

def maintenance_animal_figures(dbo: Database, includeMonths: bool = True, includeAnnual: bool = True) -> None:
    """
    Finds all months/years the system has animal data for and generates 
    figures reporting data for them.
    """
    if dbo.dbtype == "POSTGRESQL":
        monthsyears = dbo.query("SELECT DISTINCT CAST(EXTRACT(YEAR FROM DATEBROUGHTIN) AS INTEGER) AS TheYear, CAST(EXTRACT(MONTH FROM DATEBROUGHTIN) AS INTEGER) AS TheMonth FROM animal")
        years = dbo.query("SELECT DISTINCT CAST(EXTRACT(YEAR FROM DATEBROUGHTIN) AS INTEGER) AS TheYear FROM animal")
    else:
        monthsyears = dbo.query("SELECT DISTINCT MONTH(DateBroughtIn) AS TheMonth, YEAR(DateBroughtIn) AS TheYear FROM animal")
        years = dbo.query("SELECT DISTINCT YEAR(DateBroughtIn) AS TheYear FROM animal")
    if includeMonths:
        for my in monthsyears:
            asm3.al.debug("update_animal_figures: month=%d, year=%d" % (my.themonth, my.theyear), "animal.maintenance_animal_figures", dbo)
            update_animal_figures(dbo, my.themonth, my.theyear)
    if includeAnnual:
        for y in years:
            asm3.al.debug("update_animal_figures_annual: year=%d" % y.theyear, "animal.maintenance_animal_figures", dbo)
            update_animal_figures_annual(dbo, y.theyear)

