
import asm3.al
import asm3.animal
import asm3.configuration
import asm3.utils
from asm3.i18n import _, add_days
from asm3.typehints import datetime, Database, List, LocationFilter, PostedData, ResultRow, Results

# Medical treatment rules
FIXED_LENGTH = 0
UNSPECIFIED_LENGTH = 1

# Medical statuses
ACTIVE = 0
HELD = 1
COMPLETED = 2

# Medical frequencies
ONEOFF = 0
DAILY = 0
WEEKDAILY = 4
WEEKLY = 1
MONTHLY = 2
YEARLY = 3

# Sort ordering
ASCENDING_REQUIRED = 0
ASCENDING_NAME = 0
DESCENDING_NAME = 1
DESCENDING_REQUIRED = 1
DESCENDING_GIVEN = 2

def get_medicaltreatment_query(dbo: Database) -> str:
    return "SELECT " \
        f"{asm3.animal.get_animal_emblem_query(dbo)}, " \
        "CASE " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 8 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=8) " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 2 AND a.HasPermanentFoster = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=12) " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 2 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 1 AND a.HasTrialAdoption = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=11) " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Not Null AND a.ActiveMovementID = 0 THEN " \
        "(SELECT ReasonName FROM deathreason WHERE ID = a.PTSReasonID) " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Not Null AND a.ActiveMovementID <> 0 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Null AND a.ActiveMovementID <> 0 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
        "ELSE " \
        "(SELECT LocationName FROM internallocation WHERE ID=a.ShelterLocation) " \
        "END AS DisplayLocationName, " \
        "co.ID AS CurrentOwnerID, co.OwnerName AS CurrentOwnerName, " \
        "am.*, amt.DateRequired, amt.CustomTreatmentName, amt.DateGiven, amt.Comments AS TreatmentComments, " \
        "amt.TreatmentNumber, amt.TotalTreatments, ma.MediaName AS WebsiteMediaName, " \
        "am.ID AS RegimenID, amt.ID AS TreatmentID, " \
        "amt.GivenBy, amt.AdministeringVetID, adv.OwnerName AS AdministeringVetName, " \
        "adv.OwnerAddress AS AdministeringVetAddress, adv.OwnerTown AS AdministeringVetTown, adv.OwnerCounty AS AdministeringVetCounty, " \
        "adv.OwnerPostcode AS AdministeringVetPostcode, adv.EmailAddress AS AdministeringVetEmail, adv.MembershipNumber AS AdministeringVetLicence, " \
        "am.Comments AS RegimenComments, " \
        "CASE WHEN a.ActiveMovementType Is Not Null AND a.ActiveMovementType > 0 THEN " \
        "(SELECT mt.MovementType FROM lksmovementtype mt WHERE mt.ID = a.ActiveMovementType) " \
        "ELSE il.LocationName END AS LocationName, " \
        "CASE WHEN a.ActiveMovementType Is Not Null AND a.ActiveMovementType > 0 THEN " \
        "'' ELSE a.ShelterLocationUnit END AS LocationUnit, " \
        "%(compositeid)s AS CompositeID, " \
        "%(givenremaining)s AS NamedGivenRemaining, " \
        "CASE " \
        "WHEN am.TimingRule = 0 THEN 'One Off' " \
        "WHEN am.TimingRuleFrequency = 0 THEN %(daily)s " \
        "WHEN am.TimingRuleFrequency = 1 THEN %(weekly)s " \
        "WHEN am.TimingRuleFrequency = 2 THEN %(monthly)s " \
        "WHEN am.TimingRuleFrequency = 3 THEN %(yearly)s " \
        "END AS NamedFrequency, " \
        "CASE " \
        "WHEN am.TimingRule = 0 THEN '1 treatment' " \
        "WHEN am.TreatmentRule = 1 THEN 'Unspecified' " \
        "ELSE %(numbertreatments)s END AS NamedNumberOfTreatments, " \
        "CASE " \
        "WHEN am.Status = 0 THEN 'Active' " \
        "WHEN am.Status = 1 THEN 'Held' " \
        "WHEN am.Status = 2 THEN 'Completed' END AS NamedStatus " \
        "FROM animal a " \
        "LEFT OUTER JOIN adoption ad ON ad.ID = a.ActiveMovementID " \
        "LEFT OUTER JOIN owner co ON co.ID = ad.OwnerID " \
        "LEFT OUTER JOIN media ma ON ma.LinkID = a.ID AND ma.LinkTypeID = 0 AND ma.WebsitePhoto = 1 " \
        "INNER JOIN animalmedical am ON a.ID = am.AnimalID " \
        "INNER JOIN animalmedicaltreatment amt ON amt.AnimalMedicalID = am.ID " \
        "LEFT OUTER JOIN owner adv ON adv.ID = amt.AdministeringVetID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation " % \
            { 
                "compositeid": dbo.sql_concat(["am.ID", "'_'", "amt.ID"]),
                "givenremaining": dbo.sql_concat(["am.TreatmentsGiven", "' / '", "am.TreatmentsRemaining"]),
                "daily": dbo.sql_concat(["am.TimingRule", "' treatments every '", "am.TimingRuleNoFrequencies", "' days'"]),
                "weekly": dbo.sql_concat(["am.TimingRule", "' treatments every '", "am.TimingRuleNoFrequencies", "' weeks'"]),
                "monthly": dbo.sql_concat(["am.TimingRule", "' treatments every '", "am.TimingRuleNoFrequencies", "' months'"]),
                "yearly": dbo.sql_concat(["am.TimingRule", "' treatments every '", "am.TimingRuleNoFrequencies", "' years'"]),
                "numbertreatments": dbo.sql_concat(["(am.TimingRule * am.TotalNumberOfTreatments)", "' treatments'"])
            }

def get_medicalcombined_query(dbo: Database) -> str:
    return "SELECT * FROM (" \
        "SELECT " \
        f"{asm3.animal.get_animal_emblem_query(dbo)}, " \
        "co.ID AS CurrentOwnerID, co.OwnerName AS CurrentOwnerName, " \
        "ma.MediaName AS WebsiteMediaName, ma.ID as WebsiteMediaID, " \
        "adv.OwnerName AS AdministeringVetName, " \
        "adv.OwnerAddress AS AdministeringVetAddress, adv.OwnerTown AS AdministeringVetTown, adv.OwnerCounty AS AdministeringVetCounty, " \
        "adv.OwnerPostcode AS AdministeringVetPostcode, adv.EmailAddress AS AdministeringVetEmail, adv.MembershipNumber AS AdministeringVetLicence, " \
        "am.TreatmentName, '' AS TreatmentResult, am.Dosage, amt.TreatmentNumber, " \
        "amt.TotalTreatments, amt.DateRequired, amt.DateGiven, NULL AS DateExpires, am.Comments " \
        "FROM animal a " \
        "INNER JOIN animalmedical am ON a.ID = am.AnimalID " \
        "INNER JOIN animalmedicaltreatment amt ON amt.AnimalMedicalID = am.ID " \
        "LEFT OUTER JOIN adoption ad ON ad.ID = a.ActiveMovementID " \
        "LEFT OUTER JOIN owner adv ON adv.ID = amt.AdministeringVetID " \
        "LEFT OUTER JOIN owner co ON co.ID = ad.OwnerID " \
        "LEFT OUTER JOIN media ma ON ma.LinkID = a.ID AND ma.LinkTypeID = 0 AND ma.WebsitePhoto = 1 " \
        "" \
        "UNION SELECT " \
        f"{asm3.animal.get_animal_emblem_query(dbo)}, " \
        "co.ID AS CurrentOwnerID, co.OwnerName AS CurrentOwnerName, " \
        "ma.MediaName AS WebsiteMediaName, ma.ID as WebsiteMediaID, " \
        "adv.OwnerName AS AdministeringVetName, " \
        "adv.OwnerAddress AS AdministeringVetAddress, adv.OwnerTown AS AdministeringVetTown, adv.OwnerCounty AS AdministeringVetCounty, " \
        "adv.OwnerPostcode AS AdministeringVetPostcode, adv.EmailAddress AS AdministeringVetEmail, adv.MembershipNumber AS AdministeringVetLicence, " \
        "v.VaccinationType AS TreatmentName, '' AS TreatmentResult, '1' AS Dosage, '1' AS TreatmentNumber, " \
        "'1' AS TotalTreatments, av.DateRequired, av.DateOfVaccination AS DateGiven, av.DateExpires, av.Comments " \
        "FROM animal a " \
        "INNER JOIN animalvaccination av ON a.ID = av.AnimalID " \
        "INNER JOIN vaccinationtype v ON av.VaccinationID = v.ID " \
        "LEFT OUTER JOIN adoption ad ON ad.ID = a.ActiveMovementID " \
        "LEFT OUTER JOIN owner adv ON adv.ID = av.AdministeringVetID " \
        "LEFT OUTER JOIN owner co ON co.ID = ad.OwnerID " \
        "LEFT OUTER JOIN media ma ON ma.LinkID = a.ID AND ma.LinkTypeID = 0 AND ma.WebsitePhoto = 1 " \
        "" \
        "UNION SELECT " \
        f"{asm3.animal.get_animal_emblem_query(dbo)}, " \
        "co.ID AS CurrentOwnerID, co.OwnerName AS CurrentOwnerName, " \
        "ma.MediaName AS WebsiteMediaName, ma.ID as WebsiteMediaID, " \
        "adv.OwnerName AS AdministeringVetName, " \
        "adv.OwnerAddress AS AdministeringVetAddress, adv.OwnerTown AS AdministeringVetTown, adv.OwnerCounty AS AdministeringVetCounty, " \
        "adv.OwnerPostcode AS AdministeringVetPostcode, adv.EmailAddress AS AdministeringVetEmail, adv.MembershipNumber AS AdministeringVetLicence, " \
        "tt.TestName AS TreatmentName, tr.ResultName AS TreatmentResult, '1' AS Dosage, '1' AS TreatmentNumber, " \
        "'1' AS TotalTreatments, at.DateRequired, at.DateOfTest AS DateGiven, NULL AS DateExpires, at.Comments " \
        "FROM animal a " \
        "INNER JOIN animaltest at ON a.ID = at.AnimalID " \
        "INNER JOIN testtype tt ON at.TestTypeID = tt.ID " \
        "LEFT OUTER JOIN testresult tr ON tr.ID = at.TestResultID " \
        "LEFT OUTER JOIN adoption ad ON ad.ID = a.ActiveMovementID " \
        "LEFT OUTER JOIN owner adv ON adv.ID = at.AdministeringVetID " \
        "LEFT OUTER JOIN owner co ON co.ID = ad.OwnerID " \
        "LEFT OUTER JOIN media ma ON ma.LinkID = a.ID AND ma.LinkTypeID = 0 AND ma.WebsitePhoto = 1 " \
        ") dummy " 

def get_test_query(dbo: Database) -> str:
    return "SELECT at.*, " \
        f"{asm3.animal.get_animal_emblem_query(dbo)}, " \
        "CASE " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 8 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=8) " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 2 AND a.HasPermanentFoster = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=12) " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 2 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 1 AND a.HasTrialAdoption = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=11) " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Not Null AND a.ActiveMovementID = 0 THEN " \
        "(SELECT ReasonName FROM deathreason WHERE ID = a.PTSReasonID) " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Not Null AND a.ActiveMovementID <> 0 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Null AND a.ActiveMovementID <> 0 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
        "ELSE " \
        "(SELECT LocationName FROM internallocation WHERE ID=a.ShelterLocation) " \
        "END AS DisplayLocationName, " \
        "co.ID AS CurrentOwnerID, co.OwnerName AS CurrentOwnerName, " \
        "a.AnimalName, ma.MediaName AS WebsiteMediaName, tt.TestName, tt.TestDescription, " \
        "tr.ResultName, " \
        "CASE WHEN a.ActiveMovementType Is Not Null AND a.ActiveMovementType > 0 THEN " \
        "(SELECT mt.MovementType FROM lksmovementtype mt WHERE mt.ID = a.ActiveMovementType) " \
        "ELSE il.LocationName END AS LocationName, " \
        "CASE WHEN a.ActiveMovementType Is Not Null AND a.ActiveMovementType > 0 THEN " \
        "'' ELSE a.ShelterLocationUnit END AS LocationUnit, " \
        "adv.OwnerName AS AdministeringVetName, " \
        "adv.OwnerAddress AS AdministeringVetAddress, adv.OwnerTown AS AdministeringVetTown, adv.OwnerCounty AS AdministeringVetCounty, " \
        "adv.OwnerPostcode AS AdministeringVetPostcode, adv.EmailAddress AS AdministeringVetEmail, adv.MembershipNumber AS AdministeringVetLicence " \
        "FROM animal a " \
        "LEFT OUTER JOIN adoption ad ON ad.ID = a.ActiveMovementID " \
        "LEFT OUTER JOIN owner co ON co.ID = ad.OwnerID " \
        "LEFT OUTER JOIN media ma ON ma.LinkID = a.ID AND ma.LinkTypeID = 0 AND ma.WebsitePhoto = 1 " \
        "INNER JOIN animaltest at ON a.ID = at.AnimalID " \
        "INNER JOIN testtype tt ON tt.ID = at.TestTypeID " \
        "LEFT OUTER JOIN testresult tr ON tr.ID = at.TestResultID " \
        "LEFT OUTER JOIN owner adv ON adv.ID = at.AdministeringVetID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation "

def get_vaccination_query(dbo: Database) -> str:
    return "SELECT av.*, " \
        f"{asm3.animal.get_animal_emblem_query(dbo)}, " \
        "CASE " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 8 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=8) " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 2 AND a.HasPermanentFoster = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=12) " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 2 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
        "WHEN a.Archived = 0 AND a.ActiveMovementType = 1 AND a.HasTrialAdoption = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=11) " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Not Null AND a.ActiveMovementID = 0 THEN " \
        "(SELECT ReasonName FROM deathreason WHERE ID = a.PTSReasonID) " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Not Null AND a.ActiveMovementID <> 0 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
        "WHEN a.Archived = 1 AND a.DeceasedDate Is Null AND a.ActiveMovementID <> 0 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=a.ActiveMovementType) " \
        "ELSE " \
        "(SELECT LocationName FROM internallocation WHERE ID=a.ShelterLocation) " \
        "END AS DisplayLocationName, " \
        "co.ID AS CurrentOwnerID, co.OwnerName AS CurrentOwnerName, " \
        "a.AnimalName, ma.MediaName AS WebsiteMediaName, vt.VaccinationType, vt.VaccinationDescription, " \
        "CASE WHEN a.ActiveMovementType Is Not Null AND a.ActiveMovementType > 0 THEN " \
        "(SELECT mt.MovementType FROM lksmovementtype mt WHERE mt.ID = a.ActiveMovementType) " \
        "ELSE il.LocationName END AS LocationName, " \
        "CASE WHEN a.ActiveMovementType Is Not Null AND a.ActiveMovementType > 0 THEN " \
        "'' ELSE a.ShelterLocationUnit END AS LocationUnit, " \
        "adv.OwnerName AS AdministeringVetName, " \
        "adv.OwnerAddress AS AdministeringVetAddress, adv.OwnerTown AS AdministeringVetTown, adv.OwnerCounty AS AdministeringVetCounty, " \
        "adv.OwnerPostcode AS AdministeringVetPostcode, adv.EmailAddress AS AdministeringVetEmail, adv.MembershipNumber AS AdministeringVetLicence " \
        "FROM animal a " \
        "LEFT OUTER JOIN adoption ad ON ad.ID = a.ActiveMovementID " \
        "LEFT OUTER JOIN owner co ON co.ID = ad.OwnerID " \
        "LEFT OUTER JOIN media ma ON ma.LinkID = a.ID AND ma.LinkTypeID = 0 AND ma.WebsitePhoto = 1 " \
        "INNER JOIN animalvaccination av ON a.ID = av.AnimalID " \
        "LEFT OUTER JOIN owner adv ON adv.ID = av.AdministeringVetID " \
        "LEFT OUTER JOIN vaccinationtype vt ON vt.ID = av.VaccinationID " \
        "LEFT OUTER JOIN internallocation il ON il.ID = a.ShelterLocation "

def get_vaccinations(dbo: Database, animalid: int, onlygiven: bool = False, onlydue: bool = False, sort: int = ASCENDING_REQUIRED) -> Results:
    """
    Returns a recordset of vaccinations for an animal:
    VACCINATIONTYPE, DATEREQUIRED, DATEOFVACCINATION, COMMENTS, COST
    """
    dg = ""
    if onlygiven:
        dg = "av.DateOfVaccination Is Not Null AND "
    if onlydue:
        dg += "av.DateOfVaccination Is Null AND "
    sql = get_vaccination_query(dbo) + \
        "WHERE %s av.AnimalID = %d " % (dg, animalid)
    if sort == ASCENDING_REQUIRED:
        sql += " ORDER BY av.DateRequired"
    elif sort == DESCENDING_REQUIRED:
        sql += " ORDER BY av.DateRequired DESC"
    return dbo.query(sql)

def get_vaccinated(dbo: Database, animalid: int) -> bool:
    """
    Returns true if:
        1. The animal has had at least one vaccination given
        2. There are no outstanding vaccinations due before today
    """
    given = dbo.query_int("SELECT COUNT(ID) FROM animalvaccination " \
        "WHERE AnimalID = ? AND DateOfVaccination Is Not Null ", [animalid])
    outstanding = dbo.query_int("SELECT COUNT(ID) FROM animalvaccination " \
        "WHERE AnimalID = ? AND DateOfVaccination Is Null AND DateRequired < ?", (animalid, dbo.today()))
    return outstanding == 0 and given > 0

def get_batch_for_vaccination_types(dbo: Database) -> Results:
    """
    Returns vaccination types and last non-empty batch number and manufacturer 
        we saw for that type in the last month.
        Uses our distincton to throw away everything but the first row for 
        each vaccinationid (aliased to id)
    Does nothing if the option for inserting the last batch/manufacturer is disabled.
    """
    if not asm3.configuration.auto_default_vacc_batch(dbo): return []
    return dbo.query("SELECT VaccinationID AS ID, BatchNumber, Manufacturer " \
        "FROM animalvaccination " \
        "WHERE BatchNumber <> '' AND Manufacturer <> '' " \
        "AND DateOfVaccination Is Not Null AND DateOfVaccination >= ? " \
        "ORDER BY animalvaccination.ID DESC, VaccinationID", [ dbo.today(offset=-31) ], distincton="ID")

def get_medical_types(dbo: Database, animalid: int) -> Results:
    """
    Returns a recordset of medicaltypes for an animal:
    MEDICALTYPE, DATEREQUIRED, LASTGIVEN
    """

    sql = "SELECT mt.MedicalTypeName, " \
        "(" \
            "SELECT DateRequired " \
            "FROM animalmedicaltreatment " \
            "INNER JOIN animalmedical ON animalmedicaltreatment.AnimalMedicalID = animalmedical.ID " \
            "INNER JOIN lksmedicaltype ON animalmedical.MedicalTypeID  = lksmedicaltype.ID " \
            "WHERE animalmedicaltreatment.AnimalID = ? AND animalmedicaltreatment.DateRequired >= ? AND animalmedical.MedicalTypeID = mt.ID " \
            "ORDER BY DateRequired desc " \
            "LIMIT 1" \
        ") AS DateRequired," \
        "(" \
            "SELECT DateGiven " \
            "FROM animalmedicaltreatment " \
            "INNER JOIN animalmedical ON animalmedicaltreatment.AnimalMedicalID = animalmedical.ID " \
            "INNER JOIN lksmedicaltype ON animalmedical.MedicalTypeID  = lksmedicaltype.ID " \
            "WHERE animalmedicaltreatment.AnimalID = ? AND animalmedical.MedicalTypeID = mt.ID ORDER BY DateGiven desc LIMIT 1" \
        ") AS DateGiven " \
        "FROM lksmedicaltype mt"
    return dbo.query(sql, [animalid, dbo.today(), animalid ])

def get_regimens(dbo: Database, animalid: int, onlycomplete: bool = False, onlyactive: bool = False, sort: int = ASCENDING_REQUIRED) -> Results:
    """
    Returns a recordset of medical regimens for an animal:
    TREATMENTNAME, COST, COMMENTS, NAMEDFREQUENCY, NAMEDNUMBEROFTREATMENTS,
    NAMEDSTATUS, DOSAGE, STARTDATE, TREATMENTSGIVEN, TREATMENTSREMAINING,
    TIMINGRULE, TIMINGRULEFREQUENCY, TIMINGRULENOFREQUENCIES, TREATMENTRULE
    TOTALNUMBEROFTREATMENTS, NEXTTREATMENTDUE, LASTTREATMENTGIVEN
    """
    l = dbo.locale
    sc = ""
    if onlycomplete:
        sc = f"AND am.Status = {COMPLETED}"
    elif onlyactive:
        sc = f"AND am.Status = {ACTIVE}"
    limit1 = dbo.sql_limit(1)
    sql = "SELECT am.*, " \
        "(SELECT amt.DateRequired FROM animalmedicaltreatment amt WHERE amt.AnimalMedicalID = am.ID AND amt.DateGiven Is Null " \
        f"ORDER BY amt.DateRequired DESC {limit1}) AS NextTreatmentDue, " \
        "(SELECT amt.DateGiven FROM animalmedicaltreatment amt WHERE amt.AnimalMedicalID = am.ID AND amt.DateGiven Is Not Null " \
        f"ORDER BY amt.DateGiven DESC {limit1}) AS LastTreatmentGiven, " \
        "(SELECT amt.Comments FROM animalmedicaltreatment amt WHERE amt.AnimalMedicalID = am.ID AND amt.DateGiven Is Not Null " \
        f"ORDER BY amt.DateGiven DESC {limit1}) AS LastTreatmentComments, " \
        "(SELECT adv.OwnerName FROM animalmedicaltreatment amt INNER JOIN owner adv ON adv.ID=amt.AdministeringVetID " \
        "WHERE amt.AnimalMedicalID = am.ID AND amt.DateGiven Is Not Null " \
        f"ORDER BY amt.DateGiven DESC {limit1}) AS LastTreatmentVetName " \
        f"FROM animalmedical am WHERE am.AnimalID = {animalid} {sc} "
    if sort == ASCENDING_REQUIRED:
        sql += " ORDER BY am.StartDate"
    elif sort == DESCENDING_REQUIRED:
        sql += " ORDER BY am.StartDate DESC"
    rows = dbo.query(sql)
    # Now add our extra named fields
    return embellish_regimen(l, rows)

def get_regimen_id(dbo: Database, medicalid: int) -> ResultRow:
    """
    Returns a single medical regimen from its id.
    """
    return dbo.first_row(get_regimens_ids(dbo, [medicalid]))

def get_regimens_ids(dbo: Database, ids: List[int]) -> Results:
    """
    Returns a recordset of medical regimens for a list of medical ids:
    TREATMENTNAME, COST, COMMENTS, NAMEDFREQUENCY, NAMEDNUMBEROFTREATMENTS,
    NAMEDSTATUS, DOSAGE, STARTDATE, TREATMENTSGIVEN, TREATMENTSREMAINING,
    TIMINGRULE, TIMINGRULEFREQUENCY, TIMINGRULENOFREQUENCIES, TREATMENTRULE
    TOTALNUMBEROFTREATMENTS, NEXTTREATMENTDUE, LASTTREATMENTGIVEN
    """
    l = dbo.locale
    idin = ",".join([ str(x) for x in ids ])
    limit1 = dbo.sql_limit(1)
    sql = "SELECT am.*, " \
        "(SELECT amt.DateRequired FROM animalmedicaltreatment amt WHERE amt.AnimalMedicalID = am.ID AND amt.DateGiven Is Null " \
        f"ORDER BY amt.DateRequired DESC {limit1}) AS NextTreatmentDue, " \
        "(SELECT amt.DateGiven FROM animalmedicaltreatment amt WHERE amt.AnimalMedicalID = am.ID AND amt.DateGiven Is Not Null " \
        f"ORDER BY amt.DateGiven DESC {limit1}) AS LastTreatmentGiven, " \
        "(SELECT amt.Comments FROM animalmedicaltreatment amt WHERE amt.AnimalMedicalID = am.ID AND amt.DateGiven Is Not Null " \
        f"ORDER BY amt.DateGiven DESC {limit1}) AS LastTreatmentComments, " \
        "(SELECT adv.OwnerName FROM animalmedicaltreatment amt INNER JOIN owner adv ON adv.ID=amt.AdministeringVetID " \
        "WHERE amt.AnimalMedicalID = am.ID AND amt.DateGiven Is Not Null " \
        f"ORDER BY amt.DateGiven DESC {limit1}) AS LastTreatmentVetName " \
        f"FROM animalmedical am WHERE am.ID IN ({idin}) ORDER BY am.ID"
    rows = dbo.query(sql)
    # Now add our extra named fields
    return embellish_regimen(l, rows)

def get_regimens_treatments(dbo: Database, animalid: int, sort: int = DESCENDING_REQUIRED, limit: int = 0) -> Results:
    """
    Returns a recordset of medical regimens and treatments for an animal:
    TREATMENTNAME, COST, COMMENTS, NAMEDFREQUENCY, NAMEDNUMBEROFTREATMENTS,
    NAMEDSTATUS, DOSAGE, STARTDATE, TREATMENTSGIVEN, TREATMENTSREMAINING,
    TIMINGRULE, TIMINGRULEFREQUENCY, TIMINGRULENOFREQUENCIES, TREATMENTRULE
    TOTALNUMBEROFTREATMENTS, DATEREQUIRED, DATEGIVEN, TREATMENTCOMMENTS,
    TREATMENTNUMBER, TOTALTREATMENTS, GIVENBY, REGIMENID, TREATMENTID
    """
    l = dbo.locale
    sql = get_medicaltreatment_query(dbo) + \
        "WHERE am.AnimalID = %d " % animalid
    if sort == ASCENDING_REQUIRED:
        sql += "ORDER BY amt.DateRequired"
    elif sort == DESCENDING_REQUIRED:
        sql += "ORDER BY amt.DateRequired DESC"
    elif sort == DESCENDING_GIVEN:
        sql += "ORDER BY amt.DateGiven DESC"
    rows = dbo.query(sql, limit=limit)
    # Now add our extra named fields
        
    return embellish_regimen(l, rows)

def get_medical_export(dbo: Database) -> Results:
    """
    Produces a dataset of basic animal info with all medical items for export
    """
    return dbo.query("SELECT * FROM " \
        "(" \
        "SELECT " \
        "'Medical' AS mtype, a.ShelterCode, a.AnimalName, a.ID AS AID, " \
        "t.AnimalType, s.SpeciesName, a.DisplayLocation, " \
        "am.TreatmentName, am.Dosage, amt.TreatmentNumber, " \
        "amt.TotalTreatments, amt.DateRequired, amt.DateGiven, am.Comments " \
        "FROM animal a " \
        "INNER JOIN animaltype t ON t.ID = a.AnimalTypeID " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "INNER JOIN animalmedical am ON a.ID = am.AnimalID " \
        "INNER JOIN animalmedicaltreatment amt ON amt.AnimalMedicalID = am.ID " \
        "UNION SELECT " \
        "'Vaccination' AS mtype, a.ShelterCode, a.AnimalName, a.ID AS AID, " \
        "t.AnimalType, sp.SpeciesName, a.DisplayLocation, " \
        "v.VaccinationType AS TreatmentName, '1' AS Dosage, '1' AS TreatmentNumber, " \
        "'1' AS TotalTreatments, av.DateRequired, av.DateOfVaccination AS DateGiven, av.Comments " \
        "FROM animal a " \
        "INNER JOIN animaltype t ON t.ID = a.AnimalTypeID " \
        "INNER JOIN animalvaccination av ON a.ID = av.AnimalID " \
        "INNER JOIN species sp ON sp.ID = a.SpeciesID " \
        "INNER JOIN vaccinationtype v ON av.VaccinationID = v.ID " \
        "UNION SELECT " \
        "'Test' AS mtype, a.ShelterCode, a.AnimalName, a.ID AS AID, " \
        "t.AnimalType, sp.SpeciesName, a.DisplayLocation, " \
        "tt.TestName AS TreatmentName, '1' AS Dosage, '1' AS TreatmentNumber, " \
        "'1' AS TotalTreatments, at.DateRequired, at.DateOfTest AS DateGiven, at.Comments " \
        "FROM animal a " \
        "INNER JOIN animaltype t ON t.ID = a.AnimalTypeID " \
        "INNER JOIN animaltest at ON a.ID = at.AnimalID " \
        "INNER JOIN species sp ON sp.ID = a.SpeciesID " \
        "INNER JOIN testtype tt ON at.TestTypeID = tt.ID " \
     ") dummy " \
     "ORDER BY DateRequired")

def get_profile(dbo: Database, pfid: int) -> ResultRow:
    """
    Returns a single medical profile by id.
    TREATMENTNAME, COST, COMMENTS, NAMEDFREQUENCY, NAMEDNUMBEROFTREATMENTS, DOSAGE,
    TIMINGRULE, TIMINGRULEFREQUENCY, TIMINGRULENOFREQUENCIES, TREATMENTRULE, TOTALNUMBEROFTREATMENTS
    """
    l = dbo.locale
    rows = dbo.query("SELECT m.* FROM medicalprofile m WHERE m.ID = ?", [pfid])
    rows = embellish_regimen(l, rows)
    return dbo.first_row(rows)

def get_profiles(dbo: Database, sort: int = ASCENDING_NAME) -> Results:
    """
    Returns a recordset of medical profiles:
    TREATMENTNAME, COST, COMMENTS, NAMEDFREQUENCY, NAMEDNUMBEROFTREATMENTS, DOSAGE,
    TIMINGRULE, TIMINGRULEFREQUENCY, TIMINGRULENOFREQUENCIES, TREATMENTRULE, TOTALNUMBEROFTREATMENTS
    """
    l = dbo.locale
    sql = "SELECT m.*, t.MedicalTypeName FROM medicalprofile m LEFT JOIN lksmedicaltype t ON m.MedicalTypeID = t.ID "
    if sort == ASCENDING_NAME:
        sql += "ORDER BY ProfileName"
    elif sort == DESCENDING_NAME:
        sql += "ORDER BY ProfileName DESC"
    rows = dbo.query(sql)
    # Now add our extra named fields
    return embellish_regimen(l, rows)

def embellish_regimen(l: str, rows: Results) -> Results:
    """
    Adds the following fields to a resultset containing
    regimen rows:
    NAMEDFREQUENCY, NAMEDNUMBEROFTREATMENTS, NAMEDSTATUS, NAMEDGIVENREMAINING, COMPOSITEID
    """
    for r in rows:
        st = 0
        if "REGIMENID" in r: r.COMPOSITEID = "%d_%d" % (r.REGIMENID, r.TREATMENTID)
        if "STATUS" in r: st = r.STATUS
        tr = int(r.TIMINGRULE)
        trr = int(r.TREATMENTRULE)
        trf = int(r.TIMINGRULEFREQUENCY)
        trnf = int(r.TIMINGRULENOFREQUENCIES)
        tnt = int(r.TOTALNUMBEROFTREATMENTS)
        # NAMEDFREQUENCY - pulls together timing rule
        # information to produce a string, like "One Off"
        # or "1 treatment every 5 weeks"
        tp = _("days", l)
        if tr == ONEOFF:
            r.NAMEDFREQUENCY = _("One Off", l)
        else:
            if trf == DAILY:
                r.NAMEDFREQUENCY = _("{0} treatments every {1} days", l).format(tr, trnf)
                tp = _("days", l)
            elif trf == WEEKDAILY:
                r.NAMEDFREQUENCY = _("{0} treatments every {1} weekdays", l).format(tr, trnf)
                tp = _("weekdays", l)
            elif trf == WEEKLY:
                r.NAMEDFREQUENCY = _("{0} treatments every {1} weeks", l).format(tr, trnf)
                tp = _("weeks", l)
            elif trf == MONTHLY:
                r.NAMEDFREQUENCY = _("{0} treatments every {1} months", l).format(tr, trnf)
                tp = _("months", l)
            elif trf == YEARLY:
                r.NAMEDFREQUENCY = _("{0} treatments every {1} years", l).format(tr, trnf)
                tp = _("years", l)
        # NAMEDNUMBEROFTREATMENTS - pulls together the treatment
        # rule information to return a string like "Unspecified" or
        # "21 treatment periods (52 treatments)" or "1 treatment" for one-offs
        if tr == ONEOFF:
            r.NAMEDNUMBEROFTREATMENTS = _("1 treatment", l)
        elif trr == UNSPECIFIED_LENGTH:
            r.NAMEDNUMBEROFTREATMENTS = _("Unspecified", l)
        else:
            r.NAMEDNUMBEROFTREATMENTS = str(_("{0} {1} ({2} treatments)", l)).format(tnt, tp, tr * tnt)
        # NAMEDGIVENREMAINING - shows how many treatments 
        # have been given and how many are remaining. This is also called
        # by get_profiles, which does not have treatmentsgiven or treatmentsremaining
        if "TREATMENTSREMAINING" in r:
            if r.TREATMENTSREMAINING > 0:
                r.NAMEDGIVENREMAINING = _("({0} given, {1} remaining)", l).format(r.TREATMENTSGIVEN, r.TREATMENTSREMAINING)
            else:
                r.NAMEDGIVENREMAINING = _("({0} given)", l).format(r.TREATMENTSGIVEN)
        # NAMEDSTATUS
        if st == ACTIVE:
            r.NAMEDSTATUS = _("Active", l)
        elif st == COMPLETED:
            r.NAMEDSTATUS = _("Completed", l)
        elif st == HELD:
            r.NAMEDSTATUS = _("Held", l)
    return rows

def get_tests(dbo: Database, animalid: int, onlygiven: bool = False, sort: int = ASCENDING_REQUIRED) -> Results:
    """
    Returns a recordset of tests for an animal:
    TESTNAME, RESULTNAME, DATEREQUIRED, DATEOFTEST, COMMENTS, COST
    """
    dg = ""
    if onlygiven:
        dg = "DateOfTest Is Not Null AND "
    sql = get_test_query(dbo) + \
        "WHERE %s at.AnimalID = %d " % (dg, animalid)
    if sort == ASCENDING_REQUIRED:
        sql += "ORDER BY at.DateRequired"
    elif sort == DESCENDING_REQUIRED:
        sql += "ORDER BY at.DateRequired DESC"
    return dbo.query(sql)

def get_vaccinations_outstanding(dbo: Database, offset: str = "m31", lf: LocationFilter = None) -> Results:
    """
    Returns a recordset of animals awaiting vaccinations:
    offset is m to go backwards, or p to go forwards with a number of days.
    xp and xm go backwards and forwards based on expiry date instead.
    g will go backwards on given date instead of required.
    locationfilter, siteid: restrictions on visible locations/site
    ID, ANIMALID, SHELTERCODE, ANIMALNAME, LOCATIONNAME, WEBSITEMEDIANAME, DATEREQUIRED, DATEOFVACCINATION, COMMENTS, VACCINATIONTYPE, VACCINATIONID
    """
    ec = ""
    offsetdays = asm3.utils.atoi(offset)
    if offset.startswith("m"):
        ec = " AND av.DateRequired >= %s AND av.DateRequired <= %s AND av.DateOfVaccination Is Null" % (dbo.sql_date(dbo.today(offset=offsetdays*-1)), dbo.sql_date(dbo.today()))
    if offset.startswith("p"):
        ec = " AND av.DateRequired >= %s AND av.DateRequired <= %s AND av.DateOfVaccination Is Null" % (dbo.sql_date(dbo.today()), dbo.sql_date(dbo.today(offset=offsetdays)))
    if offset.startswith("g"):
        ec = " AND av.DateOfVaccination >= %s AND av.DateOfVaccination <= %s" % (dbo.sql_date(dbo.today(offset=offsetdays*-1)), dbo.sql_date(dbo.today()))
    if offset.startswith("xm"):
        ec = " AND av.DateExpires >= %s AND av.DateExpires <= %s AND av.DateOfVaccination Is Not Null " \
            "AND NOT EXISTS(SELECT av2.ID FROM animalvaccination av2 WHERE av2.ID <> av.ID " \
            "AND av2.AnimalID = av.AnimalID AND av2.VaccinationID = av.VaccinationID " \
            "AND av2.ID <> av.ID AND av2.DateRequired >= av.DateOfVaccination)" \
                % (dbo.sql_date(dbo.today(offset=offsetdays*-1)), dbo.sql_date(dbo.today()))
    if offset.startswith("xp"):
        ec = " AND av.DateExpires >= %s AND av.DateExpires <= %s AND av.DateOfVaccination Is Not Null " \
            "AND NOT EXISTS(SELECT av2.ID FROM animalvaccination av2 WHERE av2.ID <> av.ID " \
            "AND av2.AnimalID = av.AnimalID AND av2.VaccinationID = av.VaccinationID " \
            "AND av2.ID <> av.ID AND av2.DateRequired >= av.DateOfVaccination)" \
                % (dbo.sql_date(dbo.today()), dbo.sql_date(dbo.today(offset=offsetdays)))
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    shelterfilter = ""
    if not asm3.configuration.include_off_shelter_medical(dbo):
        shelterfilter = " AND (a.Archived = 0 OR a.ActiveMovementType = 2)"
    return dbo.query(get_vaccination_query(dbo) + \
        "WHERE av.DateRequired Is Not Null " \
        "AND a.DeceasedDate Is Null %s %s %s " \
        "ORDER BY av.DateRequired, a.AnimalName" % (shelterfilter, ec, locationfilter))

def get_vaccinations_two_dates(dbo: Database, start: datetime, end: datetime, lf: LocationFilter = None) -> Results:
    """
    Returns vaccinations due between two dates:
    start, end: dates
    locationfilter, siteid: restrictions on visible locations/site
    ID, ANIMALID, SHELTERCODE, ANIMALNAME, LOCATIONNAME, WEBSITEMEDIANAME, DATEREQUIRED, DATEOFVACCINATION, COMMENTS, VACCINATIONTYPE, VACCINATIONID
    """
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    shelterfilter = ""
    if not asm3.configuration.include_off_shelter_medical(dbo):
        shelterfilter = " AND (a.Archived = 0 OR a.ActiveMovementType = 2)"
    return dbo.query(get_vaccination_query(dbo) + \
        "WHERE av.DateRequired Is Not Null AND av.DateOfVaccination Is Null " \
        "AND av.DateRequired >= ? AND av.DateRequired <= ? " \
        "AND a.DeceasedDate Is Null %s %s " \
        "ORDER BY av.DateRequired, a.AnimalName" % (shelterfilter, locationfilter), (start, end))

def get_vaccinations_expiring_two_dates(dbo: Database, start: Database, end: Database, lf: LocationFilter = None) -> Results:
    """
    Returns vaccinations expiring between two dates. 
    A vacc is only considered truly expired if there isn't another vacc of the 
    same type for the same animal with a newer required date.
    start, end: dates
    locationfilter, siteid: restrictions on visible locations/site
    ID, ANIMALID, SHELTERCODE, ANIMALNAME, LOCATIONNAME, WEBSITEMEDIANAME, DATEREQUIRED, DATEOFVACCINATION, COMMENTS, VACCINATIONTYPE, VACCINATIONID
    """
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    shelterfilter = ""
    if not asm3.configuration.include_off_shelter_medical(dbo):
        shelterfilter = " AND (a.Archived = 0 OR a.ActiveMovementType = 2)"
    return dbo.query(get_vaccination_query(dbo) + \
        "WHERE av.DateExpires Is Not Null AND av.DateOfVaccination Is Not Null " \
        "AND NOT EXISTS(SELECT av2.ID FROM animalvaccination av2 WHERE av2.ID <> av.ID " \
            "AND av2.AnimalID = av.AnimalID AND av2.VaccinationID = av.VaccinationID " \
            "AND av2.ID <> av.ID AND av2.DateRequired >= av.DateOfVaccination) " \
        "AND av.DateExpires >= ? AND av.DateExpires <= ? " \
        "AND a.DeceasedDate Is Null %s %s " \
        "ORDER BY av.DateExpires, a.AnimalName" % (shelterfilter, locationfilter), (start, end))

def get_vacc_manufacturers(dbo: Database) -> List[str]:
    rows = dbo.query("SELECT DISTINCT Manufacturer FROM animalvaccination WHERE Manufacturer Is Not Null AND Manufacturer <> '' ORDER BY Manufacturer")
    mf = []
    for r in rows:
        mf.append(r.MANUFACTURER)
    return mf

def get_tests_outstanding(dbo: Database, offset: str = "m31", lf: LocationFilter = None) -> Results:
    """
    Returns a recordset of animals awaiting tests:
    offset is m to go backwards, or p to go forwards with a number of days.
    g will go backwards on administered date instead of required.
    ID, ANIMALID, SHELTERCODE, ANIMALNAME, LOCATIONNAME, WEBSITEMEDIANAME, DATEREQUIRED, DATEOFTEST, COMMENTS, TESTNAME, RESULTNAME, TESTTYPEID
    """
    ec = ""
    offsetdays = asm3.utils.atoi(offset)
    if offset.startswith("m"):
        ec = " AND at.DateRequired >= %s AND at.DateRequired <= %s AND at.DateOfTest Is Null" % (dbo.sql_date(dbo.today(offset=offsetdays*-1)), dbo.sql_date(dbo.today()))
    if offset.startswith("p"):
        ec = " AND at.DateRequired >= %s AND at.DateRequired <= %s AND at.DateOfTest Is Null" % (dbo.sql_date(dbo.today()), dbo.sql_date(dbo.today(offset=offsetdays)))
    if offset.startswith("g"):
        ec = " AND at.DateOfTest >= %s AND at.DateOfTest <= %s" % (dbo.sql_date(dbo.today(offset=offsetdays*-1)), dbo.sql_date(dbo.today()))
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    shelterfilter = ""
    if not asm3.configuration.include_off_shelter_medical(dbo):
        shelterfilter = " AND (a.Archived = 0 OR a.ActiveMovementType = 2)"
    return dbo.query(get_test_query(dbo) + \
        "WHERE at.DateRequired Is Not Null " \
        "AND a.DeceasedDate Is Null %s %s %s " \
        "ORDER BY at.DateRequired, a.AnimalName" % (shelterfilter, ec, locationfilter))

def get_tests_two_dates(dbo: Database, start: datetime, end: datetime, lf: LocationFilter = None) -> Results:
    """
    Returns a recordset of animals awaiting tests between two dates
    start, end: dates
    ID, ANIMALID, SHELTERCODE, ANIMALNAME, LOCATIONNAME, WEBSITEMEDIANAME, DATEREQUIRED, DATEOFTEST, COMMENTS, TESTNAME, RESULTNAME, TESTTYPEID
    """
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    shelterfilter = ""
    if not asm3.configuration.include_off_shelter_medical(dbo):
        shelterfilter = " AND (a.Archived = 0 OR a.ActiveMovementType = 2)"
    return dbo.query(get_test_query(dbo) + \
        "WHERE at.DateRequired Is Not Null AND at.DateOfTest Is Null " \
        "AND at.DateRequired >= ? AND at.DateRequired <= ? " \
        "AND a.DeceasedDate Is Null %s %s " \
        "ORDER BY at.DateRequired, a.AnimalName" % (shelterfilter, locationfilter), (start, end))

def get_treatments_outstanding(dbo: Database, offset: str = "m31", lf: LocationFilter = None) -> Results:
    """
    Returns a recordset of shelter animals awaiting medical treatments:
    offset is m to go backwards, or p to go forwards with a number of days.
    g will go backwards on given date instead of required.
    ANIMALID, SHELTERCODE, ANIMALNAME, LOCATIONNAME, WEBSITEMEDIANAME,
    TREATMENTNAME, COST, COMMENTS, NAMEDFREQUENCY, NAMEDNUMBEROFTREATMENTS,
    NAMEDSTATUS, DOSAGE, STARTDATE, TREATMENTSGIVEN, TREATMENTSREMAINING,
    TIMINGRULE, TIMINGRULEFREQUENCY, TIMINGRULENOFREQUENCIES, TREATMENTRULE
    TOTALNUMBEROFTREATMENTS, DATEREQUIRED, DATEGIVEN, TREATMENTCOMMENTS,
    TREATMENTNUMBER, TOTALTREATMENTS, GIVENBY, REGIMENID, TREATMENTID
    """
    ec = ""
    offsetdays = asm3.utils.atoi(offset)
    if offset.startswith("m"):
        ec = " AND amt.DateRequired >= %s AND amt.DateRequired <= %s AND amt.DateGiven Is Null AND am.Status=0" % (dbo.sql_date(dbo.today(offset=offsetdays*-1)), dbo.sql_date(dbo.today()))
    if offset.startswith("p"):
        ec = " AND amt.DateRequired >= %s AND amt.DateRequired <= %s AND amt.DateGiven Is Null AND am.Status=0" % (dbo.sql_date(dbo.today()), dbo.sql_date(dbo.today(offset=offsetdays)))
    if offset.startswith("g"):
        ec = " AND amt.DateGiven >= %s AND amt.DateGiven <= %s" % (dbo.sql_date(dbo.today(offset=offsetdays*-1)), dbo.sql_date(dbo.today()))
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    shelterfilter = ""
    if not asm3.configuration.include_off_shelter_medical(dbo):
        shelterfilter = " AND (a.Archived = 0 OR a.ActiveMovementType = 2)"
    return embellish_regimen(dbo.locale, dbo.query(get_medicaltreatment_query(dbo) + \
        "WHERE amt.DateRequired Is Not Null " \
        "AND a.DeceasedDate Is Null %s %s %s " \
        "ORDER BY amt.DateRequired, a.AnimalName" % (shelterfilter, ec, locationfilter)))

def get_treatments_two_dates(dbo: Database, start: datetime, end: datetime, lf: LocationFilter = None) -> Results:
    """
    Returns a recordset of shelter animals awaiting medical treatments between two dates.
    ANIMALID, SHELTERCODE, ANIMALNAME, LOCATIONNAME, WEBSITEMEDIANAME,
    TREATMENTNAME, COST, COMMENTS, NAMEDFREQUENCY, NAMEDNUMBEROFTREATMENTS,
    NAMEDSTATUS, DOSAGE, STARTDATE, TREATMENTSGIVEN, TREATMENTSREMAINING,
    TIMINGRULE, TIMINGRULEFREQUENCY, TIMINGRULENOFREQUENCIES, TREATMENTRULE
    TOTALNUMBEROFTREATMENTS, DATEREQUIRED, DATEGIVEN, TREATMENTCOMMENTS,
    TREATMENTNUMBER, TOTALTREATMENTS, GIVENBY, REGIMENID, TREATMENTID
    """
    locationfilter = ""
    if lf is not None: locationfilter = lf.clause(tablequalifier="a", andprefix=True)
    shelterfilter = ""
    if not asm3.configuration.include_off_shelter_medical(dbo):
        shelterfilter = " AND (a.Archived = 0 OR a.ActiveMovementType = 2)"
    return embellish_regimen(dbo.locale, dbo.query(get_medicaltreatment_query(dbo) + \
        "WHERE amt.DateRequired Is Not Null AND amt.DateGiven Is Null " \
        "AND am.Status = 0 " \
        "AND amt.DateRequired >= ? AND amt.DateRequired <= ? " \
        "AND a.DeceasedDate Is Null %s %s " \
        "ORDER BY amt.DateRequired, a.AnimalName" % (shelterfilter, locationfilter), (start, end)))

def get_combined_due(dbo: Database, animalid: int, start: datetime, end: datetime) -> Results:
    """
    Returns a combined recordset of medical, vacc and test items for animalid
    that are due between start and end.
    animalid: int The animal ID to consider
    start: python date, due from
    end: pythond ate, due to
    """
    rows = dbo.query("SELECT * FROM (" \
        "SELECT " \
        "am.TreatmentName, am.Dosage, amt.TreatmentNumber, " \
        "amt.TotalTreatments, amt.DateRequired, am.Comments " \
        "FROM animal a " \
        "INNER JOIN animaltype t ON t.ID = a.AnimalTypeID " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "INNER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "INNER JOIN animalmedical am ON a.ID = am.AnimalID " \
        "INNER JOIN animalmedicaltreatment amt ON amt.AnimalMedicalID = am.ID " \
        "WHERE am.Status = 0 AND amt.DateGiven Is Null " \
        "AND (amt.DateRequired >= ? AND amt.DateRequired <= ?) AND a.ID = ? " \
        "UNION SELECT " \
        "v.VaccinationType AS TreatmentName, '1' AS Dosage, '1' AS TreatmentNumber, " \
        "'1' AS TotalTreatments, av.DateRequired, av.Comments " \
        "FROM animal a " \
        "INNER JOIN animaltype t ON t.ID = a.AnimalTypeID " \
        "INNER JOIN animalvaccination av ON a.ID = av.AnimalID " \
        "INNER JOIN species sp ON sp.ID = a.SpeciesID " \
        "INNER JOIN vaccinationtype v ON av.VaccinationID = v.ID " \
        "INNER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "WHERE av.DateOfVaccination Is Null " \
        "AND (av.DateRequired >= ? AND av.DateRequired <= ?) AND a.ID = ? " \
        "UNION SELECT " \
        "tt.TestName AS TreatmentName, '1' AS Dosage, '1' AS TreatmentNumber, " \
        "'1' AS TotalTreatments, at.DateRequired, at.Comments " \
        "FROM animal a " \
        "INNER JOIN animaltype t ON t.ID = a.AnimalTypeID " \
        "INNER JOIN animaltest at ON a.ID = at.AnimalID " \
        "INNER JOIN species sp ON sp.ID = a.SpeciesID " \
        "INNER JOIN testtype tt ON at.TestTypeID = tt.ID " \
        "INNER JOIN internallocation il ON il.ID = a.ShelterLocation " \
        "WHERE at.DateOfTest Is Null " \
        "AND (at.DateRequired >= ? AND at.DateRequired <= ?) AND a.ID = ? " \
        ") dummy " \
        "ORDER BY DateRequired", ( start, end, animalid, start, end, animalid, start, end, animalid ))
    return rows

def update_test_today(dbo: Database, username: str, testid: int, resultid: int) -> None:
    """
    Marks a test record as performed today. 
    """
    animalid = dbo.query_int("SELECT AnimalID FROM animaltest WHERE ID = ?", [testid])
    dbo.update("animaltest", testid, {
        "AnimalID":     animalid,
        "DateOfTest":   dbo.today(),
        "TestResultID": resultid
    }, username)
    update_animal_tests(dbo, username, testid)

def update_vaccination_today(dbo: Database, username: str, vaccid: int) -> None:
    """
    Marks a vaccination record as given today. 
    """
    animalid = dbo.query_int("SELECT AnimalID FROM animalvaccination WHERE ID = ?", [vaccid])
    dbo.update("animalvaccination", vaccid, {
        "AnimalID":             animalid,
        "DateOfVaccination":    dbo.today(),
        "GivenBy":              username
    }, username)

def calculate_given_remaining(dbo: Database, amid: int) -> None:
    """
    Calculates the number of treatments given and remaining
    """
    given = dbo.query_int("SELECT COUNT(*) FROM animalmedicaltreatment " +
        "WHERE AnimalMedicalID = ? AND DateGiven Is Not Null", [amid]) 
    cpt = dbo.query_int("SELECT CostPerTreatment FROM animalmedical WHERE ID=?", [amid])
    dbo.execute("UPDATE animalmedical SET " \
        "TreatmentsGiven = ?, " \
        "TreatmentsRemaining = ((TotalNumberOfTreatments * TimingRule) - ?) " \
        "WHERE ID = ?", (given, given, amid))
    if cpt > 0 and given > 0:
        dbo.execute("UPDATE animalmedical SET Cost = ? WHERE ID = ?", [ cpt * given, amid ])

def complete_vaccination(dbo: Database, username: str, vaccinationid: int, newdate: datetime, 
                         givenby: str = "", vetid: int = 0, dateexpires: datetime = None, 
                         batchnumber: str = "", manufacturer: str = "", cost: int = 0, rabiestag: str = "") -> None:
    """
    Marks a vaccination given/completed on newdate
    """
    animalid = dbo.query_int("SELECT AnimalID FROM animalvaccination WHERE ID = ?", [vaccinationid])
    dbo.update("animalvaccination", vaccinationid, {
        "AnimalID":             animalid,
        "DateOfVaccination":    newdate,
        "DateExpires":          dateexpires,
        "GivenBy":              asm3.utils.iif(givenby == "", username, givenby),
        "AdministeringVetID":   vetid,
        "Cost":                 cost,
        "BatchNumber":          batchnumber,
        "Manufacturer":         manufacturer,
        "RabiesTag":            rabiestag
    }, username)
    update_rabies_tag(dbo, username, animalid)

def complete_test(dbo: Database, username: str, testid: int, newdate: datetime, testresult: int, vetid: int = 0, cost: int = 0) -> None:
    """
    Marks a test performed on newdate with testresult
    """
    animalid = dbo.query_int("SELECT AnimalID FROM animaltest WHERE ID = ?", [testid])
    dbo.update("animaltest", testid, {
        "AnimalID":             animalid,
        "DateOfTest":           newdate,
        "Cost":                 cost,
        "TestResultID":         testresult,
        "AdministeringVetID":   vetid
    }, username)
    update_animal_tests(dbo, username, testid)

def reschedule_test(dbo: Database, username: str, testid: int, newdate: datetime, comments: str) -> None:
    """
    Reschedules a test for a new date, copying data from the existing one.
    Comments are appended on the existing test.
    """
    av = dbo.first_row(dbo.query("SELECT * FROM animaltest WHERE ID = ?", [testid]))
    if av.COMMENTS != "": comments = "%s\n%s" % (av.COMMENTS, comments)
    dbo.update("animaltest", testid, { "Comments": comments }, username)
    dbo.insert("animaltest", {
        "AnimalID":             av.ANIMALID,
        "TestTypeID":           av.TESTTYPEID,
        "TestResultID":         0,
        "DateOfTest":           None,
        "DateRequired":         newdate,
        "Comments":             "",
        "Cost":                 av.COST
    }, username)

def reschedule_vaccination(dbo: Database, username: str, vaccinationid: int, newdate: datetime, comments: str) -> None:
    """
    Reschedules a vaccination for a new date by copying it.
    Comments are appended to any existing comments on the existing vacc.
    """
    av = dbo.first_row(dbo.query("SELECT * FROM animalvaccination WHERE ID = ?", [vaccinationid]))
    if av.COMMENTS != "": comments = "%s\n%s" % (av.COMMENTS, comments)
    dbo.update("animalvaccination", vaccinationid, { "Comments": comments }, username)
    dbo.insert("animalvaccination", {
        "AnimalID":             av.ANIMALID,
        "VaccinationID":        av.VACCINATIONID,
        "DateOfVaccination":    None,
        "DateRequired":         newdate,
        "Manufacturer":         "",
        "BatchNumber":          "",
        "Cost":                 av.COST,
        "CostPaidDate":         None,
        "Comments":             "" 
    }, username)

def update_medical_treatments(dbo: Database, username: str, amid: int) -> None:
    """
    Called on creation of an animalmedical record and after the saving
    of a treatment record. This handles creating the next treatment
    in the sequence.

    1. Check if the record is still active, but has all treatments
       given, mark it complete if true
    2. Ignore completed records
    3. If the record has no treatments, generate one from the master
    4. If the record has no outstanding treatment records, generate
       one from the last administered record
    """
    am = dbo.first_row(dbo.query("SELECT * FROM animalmedical WHERE ID = ?", [amid]))
    amt = dbo.query("SELECT * FROM animalmedicaltreatment " \
        "WHERE AnimalMedicalID = ? ORDER BY DateRequired DESC", [amid])
    ost = dbo.query_int("SELECT COUNT(ID) FROM animalmedicaltreatment " \
        "WHERE AnimalMedicalID = ? AND DateGiven Is Null", [amid])

    # Drop out if it's inactive
    if am is None or am.STATUS != ACTIVE:
        return

    # If it's a one-off treatment and we've given it, mark complete
    if am.TIMINGRULE == ONEOFF:
        if len(amt) > 0 and ost == 0:
            dbo.execute("UPDATE animalmedical SET Status = ? WHERE ID = ?", ( COMPLETED, amid ))
            return

    # If it's a fixed length treatment, check to see if it's 
    # complete
    if am.TREATMENTRULE == FIXED_LENGTH:
        
        # Do we have any outstanding treatments? 
        # Drop out if we do
        if ost > 0: return

        # Does the number of treatments given match the total? 
        # Mark the record complete if so and we're done
        if am.TIMINGRULE == ONEOFF:
            if am.TREATMENTSGIVEN == 1:
                dbo.execute("UPDATE animalmedical SET Status = ? WHERE ID = ?", ( COMPLETED, amid ))
                return
        else:
            if am.TREATMENTSGIVEN >= (am.TOTALNUMBEROFTREATMENTS * am.TIMINGRULE):
                dbo.execute("UPDATE animalmedical SET Status = ? WHERE ID = ?", ( COMPLETED, amid ))
                return

    # If there aren't any treatment records at all, create one now
    if len(amt) == 0:
        insert_treatments(dbo, username, amid, am.STARTDATE, True)
    else:
        # We've still got some outstanding treatments. Bail out
        if ost > 0: return

        # Otherwise, create new treatments, using the latest available date given for this medical
        ldg = dbo.query_date("SELECT DateGiven FROM animalmedicaltreatment WHERE AnimalMedicalID=? ORDER BY DateGiven DESC", [amid])
        insert_treatments(dbo, username, amid, ldg, False)

def insert_treatments(dbo: Database, username: str, amid: int, requireddate: datetime, isstart: bool = True, customlabel: str = "") -> datetime:
    """
    Creates new treatment records for the given medical record
    with the required date given. isstart says that the date passed
    is the real start date, so don't look at the timing rule to 
    calculate the next date.
    Returns the requireddate of the treatment(s) we just created.
    """
    am = dbo.first_row(dbo.query("SELECT * FROM animalmedical WHERE ID = ?", [amid]))
    nofreq = am.TIMINGRULENOFREQUENCIES
    if not isstart:
        if am.TIMINGRULEFREQUENCY == DAILY:   requireddate = add_days(requireddate, nofreq)
        if am.TIMINGRULEFREQUENCY == WEEKLY:  requireddate = add_days(requireddate, nofreq*7)
        if am.TIMINGRULEFREQUENCY == MONTHLY: requireddate = add_days(requireddate, nofreq*31)
        if am.TIMINGRULEFREQUENCY == YEARLY:  requireddate = add_days(requireddate, nofreq*365)
        if am.TIMINGRULEFREQUENCY == WEEKDAILY: 
            requireddate = add_days(requireddate, nofreq)
            # For python weekday, 0 == Monday, 6 == Sunday
            while requireddate.weekday() == 5 or requireddate.weekday() == 6: requireddate = add_days(requireddate, 1)

    # Create correct number of records
    norecs = am.TIMINGRULE
    if norecs == 0: norecs = 1

    for x in range(1, norecs+1):
        dbo.insert("animalmedicaltreatment", {
            "AnimalID":             am.ANIMALID,
            "AnimalMedicalID":      amid,
            "CustomTreatmentName":  customlabel,
            "DateRequired":         requireddate,
            "DateGiven":            None,
            "GivenBy":              "",
            "TreatmentNumber":      x,
            "TotalTreatments":      norecs,
            "Comments":             ""
        }, username)

    # Update the number of treatments given and remaining
    calculate_given_remaining(dbo, amid)
    return requireddate

def insert_regimen_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Creates a regimen record from posted form data
    """
    l = dbo.locale
    if post.date("startdate") is None:
        raise asm3.utils.ASMValidationError(_("Start date must be a valid date", l))
    if post["treatmentname"] == "":
        raise asm3.utils.ASMValidationError(_("Treatment name cannot be blank", l))

    timingrule = post.integer("timingrule")
    timingrulenofrequencies = post.integer("timingrulenofrequencies")
    timingrulefrequency = post.integer("timingrulefrequency")
    customtimingrule = post["customtiming"].strip()

    # Remove trailing comma if it exists
    if len(customtimingrule) > 0:
        while customtimingrule[-1] == ",":
            customtimingrule = customtimingrule[:-1]

    totalnumberoftreatments = post.integer("totalnumberoftreatments")
    treatmentsremaining = int(totalnumberoftreatments) * int(timingrule)
    treatmentrule = post.integer("treatmentrule")
    singlemulti = post.integer("singlemulti")
    if singlemulti == 0:
        timingrule = 0
        timingrulenofrequencies = 0
        timingrulefrequency = 0
        treatmentsremaining = 1
        totalnumberoftreatments = 1
    if totalnumberoftreatments == 0:
        totalnumberoftreatments = 1
    if treatmentrule != 0:
        totalnumberoftreatments = 0
        treatmentsremaining = 0

    nregid = dbo.insert("animalmedical", {
        "AnimalID":                 post.integer("animal"),
        "MedicalProfileID":         post.integer("profileid"),
        "TreatmentName":            post["treatmentname"],
        "MedicalTypeID":            post.integer("medicaltype"), 
        "Dosage":                   post["dosage"],
        "StartDate":                post.date("startdate"),
        "Status":                   ACTIVE,
        "Cost":                     post.integer("cost"),
        "CostPerTreatment":         post.integer("costpertreatment"),
        "CostPaidDate":             post.date("costpaid"),
        "TimingRule":               timingrule,
        "TimingRuleFrequency":      timingrulefrequency,
        "TimingRuleNoFrequencies":  timingrulenofrequencies,
        "TreatmentRule":            post.integer("treatmentrule"),
        "CustomTimingRule":         post["customtiming"],
        "TotalNumberOfTreatments":  totalnumberoftreatments,
        "TreatmentsGiven":          0,
        "TreatmentsRemaining":      treatmentsremaining,
        "Comments":                 post["comments"]
    }, username)

    # If the option to pre-create all fixed-length treatments up-front is on, do that
    if asm3.configuration.medical_precreate_treatments(dbo) and treatmentrule == FIXED_LENGTH:
        if timingrule == ONEOFF:
            insert_treatments(dbo, username, nregid, post.date("startdate"), isstart = True)
        else:
            if post["customtiming"] != "":
                startdate = post.date("startdate")
                customtiming = post["customtiming"].strip()
                if customtiming[-1] == ",":
                    customtiming = customtiming[:-1]
                for a in customtiming.split(","):
                    if "=" in a:
                        label = a.split("=")[0].strip()
                        value = int(a.split("=")[1].strip())
                    else:
                        label = ""
                        value = int(a.strip())
                    reqdate = add_days(startdate, value)
                    print(str(reqdate))
                    insert_treatments(dbo, username, nregid, reqdate, True, label)
                    
            else:
                created = 1
                reqdate = post.date("startdate")
                insert_treatments(dbo, username, nregid, reqdate, isstart = True)
                while created < totalnumberoftreatments:
                    reqdate = insert_treatments(dbo, username, nregid, reqdate, isstart = False)
                    created += 1
    else:
        # We aren't pre-creating, or we have an unspecified length regimen,
        # just create the first treatment(s).
        update_medical_treatments(dbo, username, nregid)

    # If the user chose a completed status, mark the regimen completed
    # and mark any treatments we created as given on the start date
    if post.integer("status") == COMPLETED:
        dbo.execute("UPDATE animalmedical SET Status = ? WHERE ID = ?", [COMPLETED, nregid])
        for t in dbo.query("SELECT ID FROM animalmedicaltreatment WHERE AnimalMedicalID = ?", [nregid]):
            update_treatment_given(dbo, username, t.ID, post.date("startdate"))

    # If they picked a held status, we've still created the first treatment, 
    # set the status so we don't create any more
    elif post.integer("status") == HELD:
        dbo.execute("UPDATE animalmedical SET Status = ? WHERE ID = ?", [HELD, nregid])

    return nregid

def update_regimen_from_form(dbo: Database, username: str, post: PostedData) -> None:
    """
    Updates a regimen record from posted form data
    """
    l = dbo.locale
    regimenid = post.integer("regimenid")
    if post.date("startdate") is None:
        raise asm3.utils.ASMValidationError(_("Start date must be a valid date", l))
    if post["treatmentname"] == "":
        raise asm3.utils.ASMValidationError(_("Treatment name cannot be blank", l))

    dbo.update("animalmedical", regimenid, {
        "AnimalID":         post.integer("animal"),
        "TreatmentName":    post["treatmentname"],
        "MedicalTypeID":    post.integer("medicaltype"), 
        "Dosage":           post["dosage"],
        "StartDate":        post.date("startdate"),
        "Status":           post.integer("status"),
        "Cost":             post.integer("cost"),
        "CostPerTreatment": post.integer("costpertreatment"),
        "CostPaidDate":     post.date("costpaid"),
        "Comments":         post["comments"]
    }, username)

    update_medical_treatments(dbo, username, post.integer("regimenid"))

def insert_vaccination_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Creates a vaccination record from posted form data
    """
    l = dbo.locale
    if post.integer("animal") == 0:
        raise asm3.utils.ASMValidationError(_("Vaccinations require an animal", l))

    if post.date("required") is None:
        raise asm3.utils.ASMValidationError(_("Required date must be a valid date", l))

    vaccid = dbo.insert("animalvaccination", {
        "AnimalID":             post.integer("animal"),
        "VaccinationID":        post.integer("type"),
        "AdministeringVetID":   post.integer("administeringvet"),
        "GivenBy":              post["by"],
        "DateOfVaccination":    post.date("given"),
        "DateRequired":         post.date("required"),
        "DateExpires":          post.date("expires"),
        "BatchNumber":          post["batchnumber"],
        "Manufacturer":         post["manufacturer"],
        "RabiesTag":            post["rabiestag"],
        "Cost":                 post.integer("cost"),
        "CostPaidDate":         post.date("costpaid"),
        "Comments":             post["comments"]
    }, username)

    update_rabies_tag(dbo, username, post.integer("animal"))
    return vaccid

def update_vaccination_from_form(dbo: Database, username: str, post: PostedData) -> None:
    """
    Updates a vaccination record from posted form data
    """
    l = dbo.locale
    vaccid = post.integer("vaccid")
    if post.date("required") is None:
        raise asm3.utils.ASMValidationError(_("Required date must be a valid date", l))

    dbo.update("animalvaccination", vaccid, {
        "AnimalID":             post.integer("animal"),
        "VaccinationID":        post.integer("type"),
        "AdministeringVetID":   post.integer("administeringvet"),
        "GivenBy":              post["by"],
        "DateOfVaccination":    post.date("given"),
        "DateRequired":         post.date("required"),
        "DateExpires":          post.date("expires"),
        "BatchNumber":          post["batchnumber"],
        "Manufacturer":         post["manufacturer"],
        "RabiesTag":            post["rabiestag"],
        "Cost":                 post.integer("cost"),
        "CostPaidDate":         post.date("costpaid"),
        "Comments":             post["comments"]
    }, username)

    update_rabies_tag(dbo, username, post.integer("animal"))

def update_rabies_tag(dbo: Database, username: str, animalid: int) -> None:
    """
    Updates the rabies tag field on an animal record to the
    latest from its vaccinations
    """
    rabiestag = dbo.query_string("SELECT RabiesTag FROM animalvaccination " \
        "WHERE AnimalID=? AND DateOfVaccination Is Not Null AND RabiesTag Is Not Null " \
        "AND RabiesTag <> '' ORDER BY DateOfVaccination DESC", [animalid])
    if rabiestag != "": dbo.update("animal", animalid, { "RabiesTag": rabiestag }, username)

def insert_test_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Creates a test record from posted form data
    """
    l = dbo.locale
    if post.date("required") is None:
        raise asm3.utils.ASMValidationError(_("Required date must be a valid date", l))

    ntestid = dbo.insert("animaltest", {
        "AnimalID":         post.integer("animal"),
        "TestTypeID":       post.integer("type"),
        "TestResultID":     post.integer("result"),
        "AdministeringVetID": post.integer("administeringvet"),
        "DateOfTest":       post.date("given"),
        "DateRequired":     post.date("required"),
        "Cost":             post.integer("cost"),
        "CostPaidDate":     post.date("costpaid"),
        "Comments":         post["comments"]
    }, username)

    update_animal_tests(dbo, username, ntestid, "insert")
    return ntestid

def update_test_from_form(dbo: Database, username: str, post: PostedData) -> None:
    """
    Updates a test record from posted form data
    """
    l = dbo.locale
    testid = post.integer("testid")
    if post.date("required") is None:
        raise asm3.utils.ASMValidationError(_("Required date must be a valid date", l))

    dbo.update("animaltest", testid, {
        "AnimalID":         post.integer("animal"),
        "TestTypeID":       post.integer("type"),
        "TestResultID":     post.integer("result"),
        "AdministeringVetID": post.integer("administeringvet"),
        "DateOfTest":       post.date("given"),
        "DateRequired":     post.date("required"),
        "Cost":             post.integer("cost"),
        "CostPaidDate":     post.date("costpaid"),
        "Comments":         post["comments"]
    }, username)

    update_animal_tests(dbo, username, testid, "update")

def update_animal_tests(dbo: Database, username: str, testid: int, action: str = "insert") -> None:
    """
    Checks the test with testid and if it's a FIV, FLV or Heartworm 
    test updates the denormalised animal test fields.
    """
    if not asm3.configuration.update_animal_test_fields(dbo): return # Do nothing if disabled
    t = dbo.first_row(dbo.query("SELECT AnimalID, TestName, DateOfTest, ResultName FROM animaltest " \
        "INNER JOIN testtype ON testtype.ID = animaltest.TestTypeID " \
        "INNER JOIN testresult ON testresult.ID = animaltest.TestResultID " \
        "WHERE animaltest.ID=?", [testid]))
    if t is None:
        return
    # If there's no date, forget it
    if t.DATEOFTEST is None: return
    # Get an old style result
    result = 0
    if t.RESULTNAME.find("egativ") != -1: result = 1
    if t.RESULTNAME.find("ositiv") != -1: result = 2
    # Update for the correct test if it's one we know about and this is 
    # an insert or update operation
    if action == "insert" or action == "update":
        if t.TESTNAME.find("FIV") != -1: 
            dbo.update("animal", t.ANIMALID, { "CombiTested": 1, "CombiTestDate": t.DATEOFTEST, "CombiTestResult": result }, username)
        if t.TESTNAME.find("FLV") != -1 or t.TESTNAME.find("FeLV") != -1: 
            dbo.update("animal", t.ANIMALID, { "CombiTested": 1, "CombiTestDate": t.DATEOFTEST, "FLVResult": result }, username)
        if t.TESTNAME.find("eartworm") != -1: 
            dbo.update("animal", t.ANIMALID, { "HeartwormTested": 1, "HeartwormTestDate": t.DATEOFTEST, "HeartwormTestResult": result }, username)
    # If we were deleting a test, check if it's for one of our standard
    # tests and if the test result was the same, reset it back to unknown
    elif action == "delete":
        if t.TESTNAME.find("FIV") != -1:
            dbo.update("animal", t.ANIMALID, { "CombiTestResult": 0 }, username)
        if t.TESTNAME.find("FLV") != -1 or t.TESTNAME.find("FeLV") != -1:
            dbo.update("animal", t.ANIMALID, { "FLVResult": 0 }, username)
        if t.TESTNAME.find("eartworm") != -1:
            dbo.update("animal", t.ANIMALID, { "HeartwormTested": 0, "HeartwormTestDate": None, "HeartwormTestResult": 0 }, username)

def delete_regimen(dbo: Database, username: str, amid: int) -> None:
    """
    Deletes a regimen
    """
    dbo.delete("animalmedicaltreatment", "AnimalMedicalID=%d" % amid, username)
    dbo.delete("animalmedical", amid, username)

def delete_treatment(dbo: Database, username: str, amtid: int) -> None:
    """
    Deletes a treatment record
    """
    amid = dbo.query_int("SELECT AnimalMedicalID FROM animalmedicaltreatment WHERE ID = ?", [amtid])
    dbo.delete("animalmedicaltreatment", amtid, username)
    # Was that the last treatment for the regimen? If so, remove the regimen as well
    if 0 == dbo.query_int("SELECT COUNT(*) FROM animalmedicaltreatment WHERE AnimalMedicalID = ?", [amid]):
        delete_regimen(dbo, username, amid)
    else:
        calculate_given_remaining(dbo, amid)
        update_medical_treatments(dbo, username, amid)

def delete_test(dbo: Database, username: str, testid: int) -> None:
    """
    Deletes a test record
    """
    update_animal_tests(dbo, username, testid, "delete")
    dbo.delete("animaltest", testid, username)

def delete_vaccination(dbo: Database, username: str, vaccinationid: int) -> None:
    """
    Deletes a vaccination record
    """
    animalid = dbo.query_int("SELECT AnimalID FROM animalvaccination WHERE ID = ?", [vaccinationid])
    dbo.delete("animalvaccination", vaccinationid, username)
    update_rabies_tag(dbo, username, animalid)

def insert_profile_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Creates a profile record from posted form data
    """
    l = dbo.locale
    if post["treatmentname"] == "":
        raise asm3.utils.ASMValidationError(_("Treatment name cannot be blank", l))
    if post["profilename"] == "":
        raise asm3.utils.ASMValidationError(_("Profile name cannot be blank", l))

    timingrule = post.integer("timingrule")
    timingrulenofrequencies = post.integer("timingrulenofrequencies")
    timingrulefrequency = post.integer("timingrulefrequency")
    customtimingrule = post["customtiming"].strip()

    # Remove trailing comma if it exists
    if len(customtimingrule) > 0:
        while customtimingrule[-1] == ",":
            customtimingrule = customtimingrule[:-1]
    
    if post.integer("singlemulti") == 2:
        totalnumberoftreatments = len(customtimingrule.split(","))
    else:
        totalnumberoftreatments = post.integer("totalnumberoftreatments")

        treatmentrule = post.integer("treatmentrule")
        singlemulti = post.integer("singlemulti")
        if singlemulti == 0:
            timingrule = 0
            timingrulenofrequencies = 0
            timingrulefrequency = 0
            totalnumberoftreatments = 1
        if totalnumberoftreatments == 0:
            totalnumberoftreatments = 1
        if treatmentrule != 0:
            totalnumberoftreatments = 0

    return dbo.insert("medicalprofile", {
        "ProfileName":              post["profilename"],
        "TreatmentName":            post["treatmentname"],
        "Dosage":                   post["dosage"],
        "Cost":                     post.integer("cost"),
        "CostPerTreatment":         post.integer("costpertreatment"),
        "MedicalTypeID":            post.integer("medicaltype"),
        "TimingRule":               timingrule,
        "TimingRuleFrequency":      timingrulefrequency,
        "TimingRuleNoFrequencies":  timingrulenofrequencies,
        "CustomTimingRule":         customtimingrule,
        "TreatmentRule":            post.integer("treatmentrule"),
        "TotalNumberOfTreatments":  totalnumberoftreatments,
        "Comments":                 post["comments"]
    }, username)

def update_profile_from_form(dbo: Database, username: str, post: PostedData) -> None:
    """
    Updates a profile record from posted form data
    """
    l = dbo.locale
    profileid = post.integer("profileid")
    if post["treatmentname"] == "":
        raise asm3.utils.ASMValidationError(_("Treatment name cannot be blank", l))
    if post["profilename"] == "":
        raise asm3.utils.ASMValidationError(_("Profile name cannot be blank", l))

    timingrule = post.integer("timingrule")
    timingrulenofrequencies = post.integer("timingrulenofrequencies")
    timingrulefrequency = post.integer("timingrulefrequency")
    customtimingrule = post["customtiming"].strip()

    # Remove trailing comma if it exists
    if len(customtimingrule) > 0:
        while customtimingrule[-1] == ",":
            customtimingrule = customtimingrule[:-1]
    
    if post.integer("singlemulti") == 2:
        totalnumberoftreatments = len(customtimingrule.split(","))
    else:
        totalnumberoftreatments = post.integer("totalnumberoftreatments")
        
        treatmentrule = post.integer("treatmentrule")
        singlemulti = post.integer("singlemulti")
        if singlemulti == 0:
            timingrule = 0
            timingrulenofrequencies = 0
            timingrulefrequency = 0
        if treatmentrule != 0:
            totalnumberoftreatments = 0

    dbo.update("medicalprofile", profileid, {
        "ProfileName":              post["profilename"],
        "TreatmentName":            post["treatmentname"],
        "Dosage":                   post["dosage"],
        "Cost":                     post.integer("cost"),
        "CostPerTreatment":         post.integer("costpertreatment"),
        "MedicalTypeID":            post.integer("medicaltype"),
        "TimingRule":               timingrule,
        "TimingRuleFrequency":      timingrulefrequency,
        "TimingRuleNoFrequencies":  timingrulenofrequencies,
        "CustomTimingRule":         customtimingrule,
        "TreatmentRule":            post.integer("treatmentrule"),
        "TotalNumberOfTreatments":  totalnumberoftreatments,
        "Comments":                 post["comments"]
    }, username)

def delete_profile(dbo: Database, username: str, pfid: int) -> None:
    """
    Deletes a profile
    """
    dbo.delete("medicalprofile", pfid, username)

def update_treatment_today(dbo: Database, username: str, amtid: int) -> None:
    """
    Marks a treatment record as given today. 
    """
    amid = dbo.query_int("SELECT AnimalMedicalID FROM animalmedicaltreatment WHERE ID = ?", [amtid])
    animalid = dbo.query_int("SELECT AnimalID FROM animalmedicaltreatment WHERE ID=?", [amtid])
    dbo.update("animalmedicaltreatment", amtid, {
        "AnimalID":     animalid,
        "DateGiven":    dbo.today(),
        "GivenBy":      username
    }, username)

    # Update number of treatments given and remaining
    calculate_given_remaining(dbo, amid)

    # Generate next treatments in sequence or complete the
    # medical record appropriately
    update_medical_treatments(dbo, username, amid)

def update_treatment_given(dbo: Database, username: str, amtid: int, newdate: datetime, by: str = "", vetid: int = 0, comments: str = "") -> None:
    """
    Marks a treatment record as given on newdate, assuming that newdate is valid.
    """
    amid = dbo.query_int("SELECT AnimalMedicalID FROM animalmedicaltreatment WHERE ID = ?", [amtid])
    animalid = dbo.query_int("SELECT AnimalID FROM animalmedicaltreatment WHERE ID=?", [amtid])
    dbo.update("animalmedicaltreatment", amtid, {
        "AnimalID":             animalid,
        "AdministeringVetID":   vetid,
        "DateGiven":            newdate,
        "GivenBy":              by,
        "Comments":             comments
    }, username)

    # Update number of treatments given and remaining
    calculate_given_remaining(dbo, amid)

    # Generate next treatments in sequence or complete the
    # medical record appropriately
    update_medical_treatments(dbo, username, amid)

def update_treatment_required(dbo: Database, username: str, amtid: int, newdate: datetime) -> None:
    """
    Marks a treatment record as required on newdate, assuming
    that newdate is valid.
    """
    animalid = dbo.query_int("SELECT AnimalID FROM animalmedicaltreatment WHERE ID=?", [amtid])
    dbo.update("animalmedicaltreatment", amtid, {
        "AnimalID":         animalid,
        "DateRequired":     newdate
    }, username)

def update_vaccination_required(dbo: Database, username: str, vaccid: int, newdate: datetime) -> None:
    """
    Gives a vaccination record a required date of newdate, assuming
    that newdate is valid.
    """
    animalid = dbo.query_int("SELECT AnimalID FROM animalvaccination WHERE ID=?", [vaccid])
    dbo.update("animalvaccination", vaccid, {
        "AnimalID":         animalid,
        "DateRequired":     newdate
    }, username)

