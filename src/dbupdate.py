#!/usr/bin/python

import al
import animal, animalcontrol, financial, lostfound, medical, movement, onlineform, person, waitinglist
import configuration, db, dbfs, utils
import os, sys
from i18n import _, BUILD
from sitedefs import DB_PK_STRATEGY

LATEST_VERSION = 33803
VERSIONS = ( 
    2870, 3000, 3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3009, 3010, 3050,
    3051, 3081, 3091, 3092, 3093, 3094, 3110, 3111, 3120, 3121, 3122, 3123, 3200,
    3201, 3202, 3203, 3204, 3210, 3211, 3212, 3213, 3214, 3215, 3216, 3217, 3218,
    3220, 3221, 3222, 3223, 3224, 3225, 3300, 3301, 3302, 3303, 3304, 3305, 3306,
    3307, 3308, 3309, 33010, 33011, 33012, 33013, 33014, 33015, 33016, 33017, 33018,
    33019, 33101, 33102, 33104, 33105, 33106, 33201, 33202, 33203, 33204, 33205,
    33206, 33300, 33301, 33302, 33303, 33304, 33305, 33306, 33307, 33308, 33309,
    33310, 33311, 33312, 33313, 33314, 33315, 33316, 33401, 33402, 33501, 33502,
    33503, 33504, 33505, 33506, 33507, 33508, 33600, 33601, 33602, 33603, 33604,
    33605, 33606, 33607, 33608, 33609, 33700, 33701, 33702, 33703, 33704, 33705,
    33706, 33707, 33708, 33709, 33710, 33711, 33712, 33713, 33714, 33715, 33716,
    33717, 33718, 33800, 33801, 33802, 33803
)

# All ASM3 tables
TABLES = ( "accounts", "accountsrole", "accountstrx", "additional", "additionalfield",
    "adoption", "animal", "animalcontrol", "animalcost", "animaldiet", "animalfigures", "animalfiguresannual", 
    "animalfiguresasilomar", "animalfiguresmonthlyasilomar", "animalfound", "animalcontrolanimal", "animallitter", 
    "animallost", "animalmedical", "animalmedicaltreatment", "animalname", "animalpublished", "animaltype", 
    "animaltest", "animaltransport", "animalvaccination", "animalwaitinglist", "audittrail", "basecolour", 
    "breed", "citationtype", "configuration", "costtype", "customreport", "customreportrole", "dbfs", 
    "deathreason", "diary", "diarytaskdetail", "diarytaskhead", "diet", "donationpayment", "donationtype", 
    "entryreason", "incidentcompleted", "incidenttype", "internallocation", "licencetype", "lkanimalflags", "lkcoattype", 
    "lkownerflags", "lksaccounttype", "lksdiarylink", "lksdonationfreq", "lksex", "lksfieldlink", "lksfieldtype", 
    "lksize", "lksloglink", "lksmedialink", "lksmediatype", "lksmovementtype", "lksposneg", "lksrotatype", 
    "lksyesno", "lksynun", "lkurgency", "log", "logtype", "media", "medicalprofile", "messages", "onlineform", 
    "onlineformfield", "onlineformincoming", "owner", "ownercitation", "ownerdonation", "ownerinvestigation", 
    "ownerlicence", "ownerrota", "ownertraploan", "ownervoucher", "pickuplocation", 
    "reservationstatus", "role", "species", "stocklevel", "stocklocation", "stockusage", "stockusagetype", 
    "testtype", "testresult", "traptype", "userrole", "users", "vaccinationtype", "voucher" )

# ASM2_COMPATIBILITY This is used for dumping tables in ASM2/HSQLDB format. 
# These are the tables present in ASM2.
TABLES_ASM2 = ( "accounts", "accountsrole", "accountstrx", "additional", "additionalfield",
    "adoption", "animal", "animalcost", "animaldiet", "animalfound", "animallitter", "animallost", 
    "animalmedical", "animalmedicaltreatment", "animalname", "animaltype", "animaltest", "animalvaccination", 
    "animalwaitinglist", "audittrail", "basecolour", "breed", "configuration", "costtype", 
    "customreport", "dbfs", "deathreason", "diary", "diarytaskdetail", "diarytaskhead", "diet", 
    "donationtype", "entryreason", "internallocation", "lkcoattype", "lksaccounttype", "lksdiarylink", 
    "lksdonationfreq", "lksex", "lksfieldlink", "lksfieldtype", "lksize", "lksloglink", "lksmedialink", 
    "lksmediatype", "lksmovementtype", "lksposneg", "lksyesno", "lksynun", "lkurgency", "log", 
    "logtype", "media", "medicalprofile", "owner", "ownerdonation", "ownervoucher", "primarykey", 
    "species", "users", "vaccinationtype", "voucher" )

# Tables that don't have an ID column (we don't create PostgreSQL sequences for them for pseq pk)
TABLES_NO_ID_COLUMN = ( "accountsrole", "additional", "audittrail", "animalcontrolanimal", 
    "animalpublished", "configuration", "customreportrole", "onlineformincoming", "userrole" )

VIEWS = ( "v_adoption", "v_animal", "v_animalcontrol", "v_animalfound", "v_animallost", 
    "v_animalmedicaltreatment", "v_animaltest", "v_animalvaccination", "v_animalwaitinglist", 
    "v_owner", "v_ownercitation", "v_ownerdonation", "v_ownerlicence", "v_ownertraploan", 
    "v_ownervoucher" )

def sql_structure(dbo):
    """
    Returns the SQL necessary to create the database for the type specified
    """
    SHORTTEXT = "VARCHAR(1024)"
    LONGTEXT = "TEXT"
    CLOB = "TEXT"
    DATETIME = "TIMESTAMP"
    INTEGER = "INTEGER"
    FLOAT = "REAL"
    if dbo.dbtype == "MYSQL":
        CLOB = "LONGTEXT"
        SHORTTEXT = "VARCHAR(255)" # MySQL max key length is 767 bytes for multi-byte charsets
        LONGTEXT = "LONGTEXT"
        DATETIME = "DATETIME"
        FLOAT = "DOUBLE"
    if dbo.dbtype == "HSQLDB":
        LONGTEXT = "VARCHAR(2000000)"
        CLOB = LONGTEXT
        FLOAT = "DOUBLE"
    def table(name, fields, includechange = True):
        createtable = "CREATE TABLE "
        if dbo.dbtype == "HSQLDB":
            createtable = "DROP TABLE %s IF EXISTS;\nCREATE MEMORY TABLE " % name
        if includechange:
            cf = (fint("RecordVersion", True),
                fstr("CreatedBy", True),
                fdate("CreatedDate", True),
                fstr("LastChangedBy", True),
                fdate("LastChangedDate", True))
            return "%s%s (%s);\n" % (createtable, name, ",".join(fields + cf))
        return "%s%s (%s);\n" % (createtable, name, ",".join(fields) )
    def index(name, table, fieldlist, unique = False):
        uniquestr = ""
        if unique: uniquestr = "UNIQUE "
        return "CREATE %sINDEX %s ON %s (%s);\n" % ( uniquestr, name, table, fieldlist)
    def field(name, ftype = INTEGER, nullable = True, pk = False):
        nullstr = "NOT NULL"
        if nullable: nullstr = "NULL"
        pkstr = ""
        if pk: pkstr = " PRIMARY KEY"
        if dbo.dbtype == "HSQLDB": name = name.upper()
        return "%s %s %s%s" % ( name, ftype, nullstr, pkstr )
    def fid():
        return field("ID", INTEGER, False, True)
    def fint(name, nullable = False):
        return field(name, INTEGER, nullable, False)
    def ffloat(name, nullable = False):
        return field(name, FLOAT, nullable, False)
    def fdate(name, nullable = False):
        return field(name, DATETIME, nullable, False)
    def fstr(name, nullable = False):
        return field(name, SHORTTEXT, nullable, False)
    def flongstr(name, nullable = True):
        return field(name, LONGTEXT, nullable, False)
    def fclob(name, nullable = True):
        return field(name, CLOB, nullable, False)

    sql = ""
    sql += table("accounts", (
        fid(),
        fstr("Code"),
        fstr("Description"),
        fint("Archived", True),
        fint("AccountType"),
        fint("CostTypeID", True),
        fint("DonationTypeID", True) ))
    sql += index("accounts_Code", "accounts", "Code", False)
    sql += index("accounts_Archived", "accounts", "Archived")
    sql += index("accounts_CostTypeID", "accounts", "CostTypeID")
    sql += index("accounts_DonationTypeID", "accounts", "DonationTypeID")
 
    sql += table("accountsrole", (
        fint("AccountID"),
        fint("RoleID"),
        fint("CanView"),
        fint("CanEdit") ))
    sql += index("accountsrole_AccountIDRoleID", "accountsrole", "AccountID, RoleID")

    sql += table("accountstrx", (
        fid(),
        fdate("TrxDate"),
        fstr("Description"),
        fint("Reconciled"),
        fint("Amount"),
        fint("SourceAccountID"),
        fint("DestinationAccountID"),
        fint("AnimalCostID", True), 
        fint("OwnerDonationID", True) ))
    sql += index("accountstrx_TrxDate", "accountstrx", "TrxDate")
    sql += index("accountstrx_Source", "accountstrx", "SourceAccountID")
    sql += index("accountstrx_Dest", "accountstrx", "DestinationAccountID")
    sql += index("accountstrx_Cost", "accountstrx", "AnimalCostID")
    sql += index("accountstrx_Donation", "accountstrx", "OwnerDonationID")

    sql += table("additionalfield", (
        fid(),
        fint("LinkType"),
        fstr("FieldName"),
        fstr("FieldLabel"),
        fstr("ToolTip"),
        flongstr("LookupValues"),
        flongstr("DefaultValue", True),
        fint("FieldType"),
        fint("DisplayIndex"),
        fint("Mandatory"),
        fint("Searchable", True) ), False)
    sql += index("additionalfield_LinkType", "additionalfield", "LinkType")

    sql += table("additional", (
        fint("LinkType"),
        fint("LinkID"),
        fint("AdditionalFieldID"),
        flongstr("Value") ), False)
    sql += index("additional_LinkTypeIDAdd", "additional", "LinkType, LinkID, AdditionalFieldID", True)
    sql += index("additional_LinkTypeID", "additional", "LinkType, LinkID")

    sql += table("adoption", (
        fid(),
        fstr("AdoptionNumber"),
        fint("AnimalID"),
        fint("OwnerID", True),
        fint("RetailerID", True),
        fint("OriginalRetailerMovementID", True),
        fdate("MovementDate", True),
        fint("MovementType"),
        fdate("ReturnDate", True),
        fint("ReturnedReasonID"),
        fstr("InsuranceNumber", True),
        flongstr("ReasonForReturn"),
        fdate("ReservationDate", True),
        fdate("ReservationCancelledDate", True),
        fint("ReservationStatusID", True),
        fint("Donation", True),
        fint("IsTrial", True),
        fint("IsPermanentFoster", True),
        fdate("TrialEndDate", True),
        flongstr("Comments") ))
    sql += index("adoption_AdoptionNumber", "adoption", "AdoptionNumber", True)
    sql += index("adoption_AnimalID", "adoption", "AnimalID")
    sql += index("adoption_CreatedBy", "adoption", "CreatedBy")
    sql += index("adoption_IsPermanentFoster", "adoption", "IsPermanentFoster")
    sql += index("adoption_IsTrial", "adoption", "IsTrial")
    sql += index("adoption_OwnerID", "adoption", "OwnerID")
    sql += index("adoption_RetailerID", "adoption", "RetailerID")
    sql += index("adoption_MovementDate", "adoption", "MovementDate")
    sql += index("adoption_MovementType", "adoption", "MovementType")
    sql += index("adoption_ReservationDate", "adoption", "ReservationDate")
    sql += index("adoption_ReservationCancelledDate", "adoption", "ReservationCancelledDate")
    sql += index("adoption_ReservationStatusID", "adoption", "ReservationStatusID")
    sql += index("adoption_ReturnDate", "adoption", "ReturnDate")
    sql += index("adoption_ReturnedReasonID", "adoption", "ReturnedReasonID")
    sql += index("adoption_TrialEndDate", "adoption", "TrialEndDate")

    sql += table("animal", (
        fid(),
        fint("AnimalTypeID"),
        fstr("AnimalName"),
        fint("NonShelterAnimal"),
        fint("CrueltyCase"),
        fint("BondedAnimalID"),
        fint("BondedAnimal2ID"),
        fint("BaseColourID"),
        fint("SpeciesID"),
        fint("BreedID"),
        fint("Breed2ID"),
        fstr("BreedName", True),
        fint("CrossBreed"),
        fint("CoatType"),
        flongstr("Markings"),
        fstr("ShelterCode"),
        fstr("ShortCode"),
        fint("UniqueCodeID"),
        fint("YearCodeID"),
        fstr("AcceptanceNumber"),
        fdate("DateOfBirth"),
        fint("EstimatedDOB"),
        fstr("AgeGroup", True),
        fdate("DeceasedDate", True),
        fint("Sex"),
        fint("Fee", True),
        fint("Identichipped"),
        fstr("IdentichipNumber"),
        fdate("IdentichipDate", True),
        fint("Tattoo"),
        fstr("TattooNumber"),
        fdate("TattooDate", True),
        fint("SmartTag"),
        fstr("SmartTagNumber", True),
        fdate("SmartTagDate", True),
        # ASM2_COMPATIBILITY
        fdate("SmartTagSentDate", True),
        fint("SmartTagType"),
        fint("Neutered"),
        fdate("NeuteredDate", True),
        fint("CombiTested"),
        fdate("CombiTestDate", True),
        fint("CombiTestResult"),
        fint("HeartwormTested"),
        fdate("HeartwormTestDate", True),
        fint("HeartwormTestResult"),
        fint("FLVResult"),
        fint("Declawed"),
        flongstr("HiddenAnimalDetails"),
        flongstr("AnimalComments"),
        fint("OwnersVetID"),
        fint("CurrentVetID"),
        fint("OriginalOwnerID"),
        fint("BroughtInByOwnerID"),
        flongstr("ReasonForEntry"),
        flongstr("ReasonNO"),
        fdate("DateBroughtIn"),
        fint("EntryReasonID"),
        fint("AsilomarIsTransferExternal", True),
        fint("AsilomarIntakeCategory", True),
        fint("AsilomarOwnerRequestedEuthanasia", True),
        fint("IsPickup", True),
        fint("PickupLocationID", True),
        fstr("PickupAddress", True),
        flongstr("HealthProblems"),
        fint("PutToSleep"),
        flongstr("PTSReason"),
        fint("PTSReasonID"),
        fint("IsCourtesy", True),
        fint("IsDOA"),
        fint("IsTransfer"),
        fint("IsGoodWithCats"),
        fint("IsGoodWithDogs"),
        fint("IsGoodWithChildren"),
        fint("IsHouseTrained"),
        fint("IsNotAvailableForAdoption"),
        fint("IsHold", True),
        fdate("HoldUntilDate", True),
        fint("IsQuarantine", True),
        fint("HasSpecialNeeds"),
        flongstr("AdditionalFlags", True),
        fint("ShelterLocation"),
        fstr("ShelterLocationUnit", True),
        fint("DiedOffShelter"),
        fint("Size"),
        ffloat("Weight", True),
        fstr("RabiesTag", True),
        fint("Archived"),
        fint("ActiveMovementID"),
        fint("ActiveMovementType", True),
        fdate("ActiveMovementDate", True),
        fdate("ActiveMovementReturn", True),
        fint("HasActiveReserve", True),
        fint("HasTrialAdoption", True),
        fint("HasPermanentFoster", True),
        fstr("DisplayLocation", True),
        fdate("MostRecentEntryDate"),
        fstr("TimeOnShelter", True),
        fstr("TotalTimeOnShelter", True),
        fint("DaysOnShelter", True),
        fint("TotalDaysOnShelter", True),
        fint("DailyBoardingCost", True),
        fstr("AnimalAge", True) ))
    sql += index("animal_AnimalShelterCode", "animal", "ShelterCode", True)
    sql += index("animal_AnimalTypeID", "animal", "AnimalTypeID")
    sql += index("animal_AnimalName", "animal", "AnimalName")
    sql += index("animal_AnimalSpecies", "animal", "SpeciesID")
    sql += index("animal_Archived", "animal", "Archived")
    sql += index("animal_ActiveMovementID", "animal", "ActiveMovementID")
    sql += index("animal_ActiveMovementDate", "animal", "ActiveMovementDate")
    sql += index("animal_ActiveMovementReturn", "animal", "ActiveMovementReturn")
    sql += index("animal_AcceptanceNumber", "animal", "AcceptanceNumber")
    sql += index("animal_ActiveMovementType", "animal", "ActiveMovementType")
    sql += index("animal_AgeGroup", "animal", "AgeGroup")
    sql += index("animal_BaseColourID", "animal", "BaseColourID")
    sql += index("animal_BondedAnimalID", "animal", "BondedAnimalID")
    sql += index("animal_BondedAnimal2ID", "animal", "BondedAnimal2ID")
    sql += index("animal_BreedID", "animal", "BreedID")
    sql += index("animal_Breed2ID", "animal", "Breed2ID")
    sql += index("animal_BreedName", "animal", "BreedName")
    sql += index("animal_BroughtInByOwnerID", "animal", "BroughtInByOwnerID")
    sql += index("animal_CoatType", "animal", "CoatType")
    sql += index("animal_CurrentVetID", "animal", "CurrentVetID")
    sql += index("animal_DateBroughtIn", "animal", "DateBroughtIn")
    sql += index("animal_DeceasedDate", "animal", "DeceasedDate")
    sql += index("animal_EntryReasonID", "animal", "EntryReasonID")
    sql += index("animal_IdentichipNumber", "animal", "IdentichipNumber")
    sql += index("animal_LastChangedDate", "animal", "LastChangedDate")
    sql += index("animal_MostRecentEntryDate", "animal", "MostRecentEntryDate")
    sql += index("animal_OriginalOwnerID", "animal", "OriginalOwnerID")
    sql += index("animal_OwnersVetID", "animal", "OwnersVetID")
    sql += index("animal_PickupLocationID", "animal", "PickupLocationID")
    sql += index("animal_PickupAddress", "animal", "PickupAddress")
    sql += index("animal_PutToSleep", "animal", "PutToSleep")
    sql += index("animal_PTSReasonID", "animal", "PTSReasonID")
    sql += index("animal_RabiesTag", "animal", "RabiesTag")
    sql += index("animal_Sex", "animal", "Sex")
    sql += index("animal_Size", "animal", "Size")
    sql += index("animal_ShelterLocation", "animal", "ShelterLocation")
    sql += index("animal_ShelterLocationUnit", "animal", "ShelterLocationUnit")
    sql += index("animal_ShortCode", "animal", "ShortCode")
    sql += index("animal_TattooNumber", "animal", "TattooNumber")
    sql += index("animal_UniqueCodeID", "animal", "UniqueCodeID")
    sql += index("animal_Weight", "animal", "Weight")
    sql += index("animal_YearCodeID", "animal", "YearCodeID")

    sql += table("animalcontrol", (
        fid(),
        fdate("IncidentDateTime"),
        fint("IncidentTypeID"),
        fdate("CallDateTime", True),
        flongstr("CallNotes", True),
        fstr("CallTaker", True),
        fint("CallerID", True),
        fint("VictimID", True),
        fstr("DispatchAddress", True),
        fstr("DispatchTown", True),
        fstr("DispatchCounty", True),
        fstr("DispatchPostcode", True),
        fstr("DispatchLatLong", True),
        fstr("DispatchedACO", True),
        fint("PickupLocationID", True),
        fdate("DispatchDateTime", True),
        fdate("RespondedDateTime", True),
        fdate("FollowupDateTime", True),
        fint("FollowupComplete", True),
        fdate("FollowupDateTime2", True),
        fint("FollowupComplete2", True),
        fdate("FollowupDateTime3", True),
        fint("FollowupComplete3", True),
        fdate("CompletedDate", True),
        fint("IncidentCompletedID", True),
        fint("OwnerID", True),
        fint("Owner2ID", True),
        fint("Owner3ID", True),
        fint("AnimalID", True),
        flongstr("AnimalDescription", True),
        fint("SpeciesID", True),
        fint("Sex", True),
        fstr("AgeGroup", True) ))
    sql += index("animalcontrol_IncidentDateTime", "animalcontrol", "IncidentDateTime")
    sql += index("animalcontrol_IncidentTypeID", "animalcontrol", "IncidentTypeID")
    sql += index("animalcontrol_CallDateTime", "animalcontrol", "CallDateTime")
    sql += index("animalcontrol_CallerID", "animalcontrol", "CallerID")
    sql += index("animalcontrol_DispatchAddress", "animalcontrol", "DispatchAddress")
    sql += index("animalcontrol_DispatchPostcode", "animalcontrol", "DispatchPostcode")
    sql += index("animalcontrol_DispatchedACO", "animalcontrol", "DispatchedACO")
    sql += index("animalcontrol_DispatchDateTime", "animalcontrol", "DispatchDateTime")
    sql += index("animalcontrol_FollowupDateTime", "animalcontrol", "FollowupDateTime")
    sql += index("animalcontrol_FollowupComplete", "animalcontrol", "FollowupComplete")
    sql += index("animalcontrol_FollowupDateTime2", "animalcontrol", "FollowupDateTime2")
    sql += index("animalcontrol_FollowupComplete2", "animalcontrol", "FollowupComplete2")
    sql += index("animalcontrol_FollowupDateTime3", "animalcontrol", "FollowupDateTime3")
    sql += index("animalcontrol_FollowupComplete3", "animalcontrol", "FollowupComplete3")
    sql += index("animalcontrol_CompletedDate", "animalcontrol", "CompletedDate")
    sql += index("animalcontrol_IncidentCompletedID", "animalcontrol", "IncidentCompletedID")
    sql += index("animalcontrol_PickupLocationID", "animalcontrol", "PickupLocationID")
    sql += index("animalcontrol_AnimalID", "animalcontrol", "AnimalID")
    sql += index("animalcontrol_OwnerID", "animalcontrol", "OwnerID")
    sql += index("animalcontrol_Owner2ID", "animalcontrol", "Owner2ID")
    sql += index("animalcontrol_Owner3ID", "animalcontrol", "Owner3ID")
    sql += index("animalcontrol_VictimID", "animalcontrol", "VictimID")

    sql += table("animalcost", (
        fid(),
        fint("AnimalID"),
        fint("CostTypeID"),
        fdate("CostDate"),
        fdate("CostPaidDate", True),
        fint("CostAmount"),
        flongstr("Description", False) ))
    sql += index("animalcost_AnimalID", "animalcost", "AnimalID")
    sql += index("animalcost_CostTypeID", "animalcost", "CostTypeID")
    sql += index("animalcost_CostDate", "animalcost", "CostDate")
    sql += index("animalcost_CostPaidDate", "animalcost", "CostPaidDate")

    sql += table("animaldiet", (
        fid(),
        fint("AnimalID"),
        fint("DietID"),
        fdate("DateStarted"),
        flongstr("Comments") ))
    sql += index("animaldiet_AnimalID", "animaldiet", "AnimalID")
    sql += index("animaldiet_DietID", "animaldiet", "DietID")

    sql += table("animalfigures", (
        fid(),
        fint("Month"),
        fint("Year"),
        fint("OrderIndex"),
        fstr("Code"),
        fint("AnimalTypeID"),
        fint("SpeciesID"),
        fint("MaxDaysInMonth"),
        fstr("Heading"),
        fint("Bold"),
        fint("D1"), fint("D2"), fint("D3"), fint("D4"), fint("D5"), fint("D6"), fint("D7"), fint("D8"),
        fint("D9"), fint("D10"), fint("D11"), fint("D12"), fint("D13"), fint("D14"), fint("D15"),
        fint("D16"), fint("D17"), fint("D18"), fint("D19"), fint("D20"), fint("D21"), fint("D22"),
        fint("D23"), fint("D24"), fint("D25"), fint("D26"), fint("D27"), fint("D28"), fint("D29"),
        fint("D30"), fint("D31"), fstr("TOTAL"), ffloat("AVERAGE")), False)
    sql += index("animalfigures_AnimalTypeID", "animalfigures", "AnimalTypeID")
    sql += index("animalfigures_SpeciesID", "animalfigures", "SpeciesID")
    sql += index("animalfigures_Month", "animalfigures", "Month")
    sql += index("animalfigures_Year", "animalfigures", "Year")

    sql += table("animalfiguresannual", (
        fid(),
        fint("Year"),
        fint("OrderIndex"),
        fstr("Code"),
        fint("AnimalTypeID"),
        fint("SpeciesID"),
        fint("EntryReasonID"),
        fstr("GroupHeading"),
        fstr("Heading"),
        fint("Bold"),
        fint("M1"), fint("M2"), fint("M3"), fint("M4"), fint("M5"), fint("M6"),
        fint("M7"), fint("M8"), fint("M9"), fint("M10"), fint("M11"), fint("M12"),
        fint("Total")), False)
    sql += index("animalfiguresannual_AnimalTypeID", "animalfiguresannual", "AnimalTypeID")
    sql += index("animalfiguresannual_SpeciesID", "animalfiguresannual", "SpeciesID")
    sql += index("animalfiguresannual_EntryReasonID", "animalfiguresannual", "EntryReasonID")
    sql += index("animalfiguresannual_Year", "animalfiguresannual", "Year")

    sql += table("animalfiguresasilomar", (
        fid(),
        fint("Year"),
        fint("OrderIndex"),
        fstr("Code"),
        fstr("Heading"),
        fint("Bold"),
        fint("Cat"),
        fint("Dog"),
        fint("Total")), False)
    sql += index("animalfiguresasilomar_Year", "animalfiguresasilomar", "Year")

    sql += table("animalfiguresmonthlyasilomar", (
        fid(),
        fint("Month"),
        fint("Year"),
        fint("OrderIndex"),
        fstr("Code"),
        fstr("Heading"),
        fint("Bold"),
        fint("Cat"),
        fint("Dog"),
        fint("Total")), False)
    sql += index("animalfiguresmonthlyasilomar_Year", "animalfiguresmonthlyasilomar", "Year")
    sql += index("animalfiguresmonthlyasilomar_Month", "animalfiguresmonthlyasilomar", "Month")

    sql += table("animalfound", (
        fid(),
        fint("AnimalTypeID"),
        fdate("DateReported"),
        fdate("DateFound"),
        fint("Sex"),
        fint("BreedID"),
        fstr("AgeGroup", True),
        fint("BaseColourID"),
        flongstr("DistFeat", False),
        fstr("AreaFound"),
        fstr("AreaPostcode"),
        fint("OwnerID"),
        fdate("ReturnToOwnerDate", True),
        flongstr("Comments") ))
    sql += index("animalfound_ReturnToOwnerDate", "animalfound", "ReturnToOwnerDate")
    sql += index("animalfound_AnimalTypeID", "animalfound", "AnimalTypeID")
    sql += index("animalfound_AreaFound", "animalfound", "AreaFound")
    sql += index("animalfound_AreaPostcode", "animalfound", "AreaPostcode")

    sql += table("animalcontrolanimal", (
        fint("AnimalControlID"),
        fint("AnimalID") ), False)
    sql += index("animalcontrolanimal_AnimalControlIDAnimalID", "animalcontrolanimal", "AnimalControlID, AnimalID", True)

    sql += table("animallitter", (
        fid(),
        fint("ParentAnimalID"),
        fint("SpeciesID"),
        fdate("Date"),
        fstr("AcceptanceNumber", True),
        fint("CachedAnimalsLeft"),
        fdate("InvalidDate", True),
        fint("NumberInLitter"),
        flongstr("Comments") ))

    sql += table("animallost", (
        fid(),
        fint("AnimalTypeID"),
        fdate("DateReported"),
        fdate("DateLost"),
        fdate("DateFound", True),
        fint("Sex"),
        fint("BreedID"),
        fstr("AgeGroup", True),
        fint("BaseColourID"),
        flongstr("DistFeat", False),
        fstr("AreaLost"),
        fstr("AreaPostcode"),
        fint("OwnerID"),
        flongstr("Comments") ))
    sql += index("animallost_DateFound", "animallost", "DateFound")
    sql += index("animallost_AnimalTypeID", "animallost", "AnimalTypeID")
    sql += index("animallost_AreaLost", "animallost", "AreaLost")
    sql += index("animallost_AreaPostcode", "animallost", "AreaPostcode")

    sql += table("animalmedical", (
        fid(),
        fint("AnimalID"),
        fint("MedicalProfileID"),
        fstr("TreatmentName"),
        fdate("StartDate"),
        fstr("Dosage", True),
        fint("Cost"),
        fdate("CostPaidDate", True),
        fint("TimingRule"),
        fint("TimingRuleFrequency"),
        fint("TimingRuleNoFrequencies"),
        fint("TreatmentRule"),
        fint("TotalNumberOfTreatments"),
        fint("TreatmentsGiven"),
        fint("TreatmentsRemaining"),
        fint("Status"),
        flongstr("Comments") ))
    sql += index("animalmedical_AnimalID", "animalmedical", "AnimalID")
    sql += index("animalmedical_MedicalProfileID", "animalmedical", "MedicalProfileID")
    sql += index("animalmedical_CostPaidDate", "animalmedical", "CostPaidDate")

    sql += table("animalmedicaltreatment", (
        fid(),
        fint("AnimalID"),
        fint("AnimalMedicalID"),
        fint("AdministeringVetID", True),
        fdate("DateRequired"),
        fdate("DateGiven", True),
        fint("TreatmentNumber"),
        fint("TotalTreatments"),
        fstr("GivenBy"),
        flongstr("Comments") ))
    sql += index("animalmedicaltreatment_AnimalID", "animalmedicaltreatment", "AnimalID")
    sql += index("animalmedicaltreatment_AnimalMedicalID", "animalmedicaltreatment", "AnimalMedicalID")
    sql += index("animalmedicaltreatment_AdministeringVetID", "animalmedicaltreatment", "AdministeringVetID")
    sql += index("animalmedicaltreatment_DateRequired", "animalmedicaltreatment", "DateRequired")

    sql += table("animalname", (
        fid(),
        fstr("Name"),
        fint("Sex") ), False)

    sql += table("animalpublished", (
        fint("AnimalID"),
        fstr("PublishedTo"),
        fdate("SentDate"),
        fstr("Extra", True) ), False)
    sql += index("animalpublished_AnimalIDPublishedTo", "animalpublished", "AnimalID,PublishedTo", True)
    sql += index("animalpublished_SentDate", "animalpublished", "SentDate")

    sql += table("animaltest", (
        fid(),
        fint("AnimalID"),
        fint("TestTypeID"),
        fint("TestResultID"),
        fdate("DateOfTest", True),
        fdate("DateRequired"),
        fint("Cost"),
        fdate("CostPaidDate", True),
        flongstr("Comments") ))
    sql += index("animaltest_AnimalID", "animaltest", "AnimalID")
    sql += index("animaltest_DateRequired", "animaltest", "DateRequired")
    sql += index("animaltest_CostPaidDate", "animaltest", "CostPaidDate")

    sql += table("animaltransport", (
        fid(),
        fint("AnimalID"),
        fint("DriverOwnerID"),
        fint("PickupOwnerID"),
        fstr("PickupAddress", True),
        fstr("PickupTown", True),
        fstr("PickupCounty", True),
        fstr("PickupPostcode", True),
        fdate("PickupDateTime"),
        fint("DropoffOwnerID"),
        fstr("DropoffAddress", True),
        fstr("DropoffTown", True),
        fstr("DropoffCounty", True),
        fstr("DropoffPostcode", True),
        fdate("DropoffDateTime"),
        fint("Status"),
        fint("Miles", True),
        fint("Cost"),
        fdate("CostPaidDate", True),
        flongstr("Comments") ))
    sql += index("animaltransport_AnimalID", "animaltransport", "AnimalID")
    sql += index("animaltransport_DriverOwnerID", "animaltransport", "DriverOwnerID")
    sql += index("animaltransport_PickupOwnerID", "animaltransport", "PickupOwnerID")
    sql += index("animaltransport_PickupAddress", "animaltransport", "PickupAddress")
    sql += index("animaltransport_DropoffOwnerID", "animaltransport", "DropoffOwnerID")
    sql += index("animaltransport_DropoffAddress", "animaltransport", "DropoffAddress")
    sql += index("animaltransport_PickupDateTime", "animaltransport", "PickupDateTime")
    sql += index("animaltransport_DropoffDateTime", "animaltransport", "DropoffDateTime")
    sql += index("animaltransport_Status", "animaltransport", "Status")

    sql += table("animaltype", (
        fid(),
        fstr("AnimalType"),
        fstr("AnimalDescription", True),
        fint("IsRetired", True) ), False)

    sql += table("animalvaccination", (
        fid(),
        fint("AnimalID"),
        fint("VaccinationID"),
        fint("AdministeringVetID", True),
        fdate("DateOfVaccination", True),
        fdate("DateRequired"),
        fdate("DateExpires", True),
        fstr("BatchNumber", True),
        fstr("Manufacturer", True),
        fint("Cost"),
        fdate("CostPaidDate", True),
        flongstr("Comments") ))
    sql += index("animalvaccination_AnimalID", "animalvaccination", "AnimalID")
    sql += index("animalvaccination_AdministeringVetID", "animalvaccination", "AdministeringVetID")
    sql += index("animalvaccination_DateRequired", "animalvaccination", "DateRequired")
    sql += index("animalvaccination_CostPaidDate", "animalvaccination", "CostPaidDate")
    sql += index("animalvaccination_Manufacturer", "animalvaccination", "Manufacturer")

    sql += table("animalwaitinglist", (
        fid(),
        fint("SpeciesID"),
        fint("Size", True),
        fdate("DatePutOnList"),
        fint("OwnerID"),
        fstr("AnimalDescription"),
        flongstr("ReasonForWantingToPart"),
        fint("CanAffordDonation"),
        fint("Urgency"),
        fdate("DateRemovedFromList", True),
        fint("AutoRemovePolicy"),
        fdate("DateOfLastOwnerContact", True),
        flongstr("ReasonForRemoval"),
        flongstr("Comments"),
        fdate("UrgencyUpdateDate", True),
        fdate("UrgencyLastUpdatedDate", True) ))
    sql += index("animalwaitinglist_AnimalDescription", "animalwaitinglist", "AnimalDescription")
    sql += index("animalwaitinglist_OwnerID", "animalwaitinglist", "OwnerID")
    sql += index("animalwaitinglist_SpeciesID", "animalwaitinglist", "SpeciesID")
    sql += index("animalwaitinglist_Size", "animalwaitinglist", "Size")
    sql += index("animalwaitinglist_Urgency", "animalwaitinglist", "Urgency")
    sql += index("animalwaitinglist_DatePutOnList", "animalwaitinglist", "DatePutOnList")

    sql += table("audittrail", (
        fint("Action"),
        fdate("AuditDate"),
        fstr("UserName"),
        fstr("TableName"),
        flongstr("Description", False) ), False)
    sql += index("audittrail_Action", "audittrail", "Action")
    sql += index("audittrail_AuditDate", "audittrail", "AuditDate")
    sql += index("audittrail_UserName", "audittrail", "UserName")
    sql += index("audittrail_TableName", "audittrail", "TableName")

    sql += table("basecolour", (
        fid(),
        fstr("BaseColour"),
        fstr("BaseColourDescription", True),
        fstr("AdoptAPetColour", True),
        fint("IsRetired", True) ), False)

    sql += table("breed", (
        fid(),
        fstr("BreedName"),
        fstr("BreedDescription", True),
        fstr("PetFinderBreed", True),
        fint("SpeciesID", True),
        fint("IsRetired", True) ), False)

    sql += table("citationtype", (
        fid(),
        fstr("CitationName"),
        fstr("CitationDescription", True),
        fint("DefaultCost", True),
        fint("IsRetired", True) ), False)

    sql += table("configuration", (
        fstr("ItemName"),
        flongstr("ItemValue", False) ), False)
    sql += index("configuration_ItemName", "configuration", "ItemName")

    sql += table("costtype", (
        fid(),
        fstr("CostTypeName"),
        fstr("CostTypeDescription", True),
        fint("DefaultCost", True),
        fint("IsRetired", True) ), False)

    sql += table("customreport", (
        fid(),
        fstr("Title"),
        fstr("Category"),
        flongstr("DailyEmail", True),
        fint("DailyEmailHour", True),
        flongstr("SQLCommand", False),
        flongstr("HTMLBody", False),
        flongstr("Description"),
        fint("OmitHeaderFooter"),
        fint("OmitCriteria") ))
    sql += index("customreport_Title", "customreport", "Title")

    sql += table("customreportrole", (
        fint("ReportID"),
        fint("RoleID"),
        fint("CanView") ))
    sql += index("customreportrole_ReportIDRoleID", "customreportrole", "ReportID, RoleID")

    sql += table("dbfs", (
        fid(),
        fstr("Path"),
        fstr("Name"),
        fclob("Content", True) ), False)
    sql += index("dbfs_Path", "dbfs", "Path")
    sql += index("dbfs_Name", "dbfs", "Name")

    sql += table("deathreason", (
        fid(),
        fstr("ReasonName"),
        fstr("ReasonDescription", True),
        fint("IsRetired", True) ), False)

    sql += table("diary", (
        fid(),
        fint("LinkID"),
        fint("LinkType"),
        fdate("DiaryDateTime"),
        fstr("DiaryForName"),
        flongstr("Subject"),
        flongstr("Note"),
        flongstr("Comments", True),
        fdate("DateCompleted", True),
        fstr("LinkInfo", True) ))
    sql += index("diary_DiaryForName", "diary", "DiaryForName")

    sql += table("diarytaskdetail", (
        fid(),
        fint("DiaryTaskHeadID"),
        fint("DayPivot"),
        fstr("WhoFor"),
        flongstr("Subject"),
        flongstr("Note"),
        fint("RecordVersion", True) ), False)
    sql += index("diarytaskdetail_DiaryTaskHeadID", "diarytaskdetail", "DiaryTaskHeadID")

    sql += table("diarytaskhead", (
        fid(),
        fstr("Name"),
        fint("RecordType"),
        fint("RecordVersion", True)), False)

    sql += table("diet", (
        fid(),
        fstr("DietName"),
        fstr("DietDescription", True),
        fint("IsRetired", True) ), False)

    sql += table("donationtype", (
        fid(),
        fstr("DonationName"),
        fstr("DonationDescription", True),
        fint("DefaultCost", True),
        fint("IsRetired", True) ), False)

    sql += table("donationpayment", (
        fid(),
        fstr("PaymentName"),
        fstr("PaymentDescription", True),
        fint("IsRetired", True) ), False)

    sql += table("entryreason", (
        fid(),
        fstr("ReasonName"),
        fstr("ReasonDescription", True),
        fint("IsRetired", True) ), False)

    sql += table("incidentcompleted", (
        fid(),
        fstr("CompletedName"),
        fstr("CompletedDescription", True),
        fint("IsRetired", True) ), False)

    sql += table("incidenttype", (
        fid(),
        fstr("IncidentName"),
        fstr("IncidentDescription", True),
        fint("IsRetired", True) ), False)

    sql += table("internallocation", (
        fid(),
        fstr("LocationName"),
        fstr("LocationDescription", True),
        flongstr("Units", True),
        fint("IsRetired", True) ), False)

    sql += table("licencetype", (
        fid(),
        fstr("LicenceTypeName"),
        fstr("LicenceTypeDescription", True),
        fint("DefaultCost", True),
        fint("IsRetired", True) ), False)

    sql += table("lksaccounttype", (
        fid(), fstr("AccountType") ), False)

    sql += table("lkanimalflags", (
        fid(), fstr("Flag") ), False)

    sql += table("lkownerflags", (
        fid(), fstr("Flag") ), False)

    sql += table("lkcoattype", (
        fid(), fstr("CoatType") ), False)

    sql += table("lksex", (
        fid(), fstr("Sex") ), False)

    sql += table("lksize", (
        fid(), fstr("Size") ), False)

    sql += table("lksmovementtype", (
        fid(), fstr("MovementType") ), False)

    sql += table("lksfieldlink", (
        fid(), fstr("LinkType") ), False)

    sql += table("lksfieldtype", (
        fid(), fstr("FieldType") ), False)

    sql += table("lksmedialink", (
        fid(), fstr("LinkType") ), False)

    sql += table("lksmediatype", (
        fid(), fstr("MediaType") ), False)

    sql += table("lksdiarylink", (
        fid(), fstr("LinkType") ), False)

    sql += table("lksdonationfreq", (
        fid(), fstr("Frequency") ), False)

    sql += table("lksloglink", (
        fid(), fstr("LinkType") ), False)

    sql += table("lksrotatype", (
        fid(), fstr("RotaType") ), False)

    sql += table("lkurgency", ( 
        fid(), fstr("Urgency") ), False)

    sql += table("lksyesno", (
        fid(), fstr("Name") ), False)

    sql += table("lksynun", (
        fid(), fstr("Name") ), False)

    sql += table("lksposneg", (
        fid(), fstr("Name") ), False)

    sql += table("log", (
        fid(),
        fint("LogTypeID"),
        fint("LinkID"),
        fint("LinkType"),
        fdate("Date"),
        flongstr("Comments") ))
    sql += index("log_LogTypeID", "log", "LogTypeID")
    sql += index("log_LinkID", "log", "LinkID")

    sql += table("logtype", (
        fid(),
        fstr("LogTypeName"),
        fstr("LogTypeDescription", True),
        fint("IsRetired", True) ), False)

    sql += table("media", (
        fid(),
        fint("MediaType", True),
        fstr("MediaName"),
        flongstr("MediaNotes"),
        fint("WebsitePhoto"),
        fint("WebsiteVideo", True),
        fint("DocPhoto"),
        fint("ExcludeFromPublish", True),
        fstr("SignatureHash", True),
        # ASM2_COMPATIBILITY
        fint("NewSinceLastPublish"),
        fint("UpdatedSinceLastPublish"),
        fdate("LastPublished", True),
        fdate("LastPublishedPF", True),
        fdate("LastPublishedAP", True),
        fdate("LastPublishedP911", True),
        fdate("LastPublishedRG", True),
        # ASM2_COMPATIBILITY
        fint("LinkID"),
        fint("LinkTypeID"),
        fint("RecordVersion", True),
        fdate("Date") ), False)
    sql += index("media_LinkID", "media", "LinkID")
    sql += index("media_LinkTypeID", "media", "LinkTypeID")
    sql += index("media_WebsitePhoto", "media", "WebsitePhoto")
    sql += index("media_WebsiteVideo", "media", "WebsiteVideo")
    sql += index("media_DocPhoto", "media", "DocPhoto")

    sql += table("medicalprofile", (
        fid(),
        fstr("ProfileName"),
        fstr("TreatmentName"),
        fstr("Dosage"),
        fint("Cost"),
        fint("TimingRule"),
        fint("TimingRuleFrequency"),
        fint("TimingRuleNoFrequencies"),
        fint("TreatmentRule"),
        fint("TotalNumberOfTreatments"),
        flongstr("Comments") ))

    sql += table("messages", (
        fid(),
        fdate("Added"),
        fdate("Expires"),
        fstr("CreatedBy"),
        fstr("ForName"),
        fint("Priority"),
        flongstr("Message")), False)
    sql += index("messages_Expires", "messages", "Expires")

    sql += table("onlineform", (
        fid(),
        fstr("Name"),
        fstr("RedirectUrlAfterPOST", True),
        fstr("SetOwnerFlags", True),
        flongstr("EmailAddress", True),
        flongstr("Header", True),
        flongstr("Footer", True),
        flongstr("Description", True)), False)
    sql += index("onlineform_Name", "onlineform", "Name")

    sql += table("onlineformfield", (
        fid(),
        fint("OnlineFormID"),
        fstr("FieldName"),
        fint("FieldType"),
        fint("DisplayIndex", True),
        fint("Mandatory", True),
        fstr("Label"),
        flongstr("Lookups", True),
        flongstr("Tooltip", True)), False)
    sql += index("onlineformfield_OnlineFormID", "onlineformfield", "OnlineFormID")

    sql += table("onlineformincoming", (
        fint("CollationID"),
        fstr("FormName"),
        fdate("PostedDate"),
        fstr("Flags", True),
        fstr("FieldName"),
        fstr("Label", True),
        fint("DisplayIndex", True),
        fstr("Host", True),
        flongstr("Preview", True),
        flongstr("Value", True)), False)
    sql += index("onlineformincoming_CollationID", "onlineformincoming", "CollationID")

    sql += table("owner", (
        fid(),
        fint("OwnerType", True),
        fstr("OwnerTitle", True),
        fstr("OwnerInitials", True),
        fstr("OwnerForeNames", True),
        fstr("OwnerSurname"),
        fstr("OwnerName"),
        fint("IsDeceased", True),
        fstr("OwnerAddress", True),
        fstr("OwnerTown", True),
        fstr("OwnerCounty", True),
        fstr("OwnerPostcode", True),
        fstr("LatLong", True),
        fstr("HomeTelephone", True),
        fstr("WorkTelephone", True),
        fstr("MobileTelephone", True),
        fstr("EmailAddress", True),
        fint("ExcludeFromBulkEmail", True),
        fint("IDCheck", True),
        flongstr("Comments", True),
        fint("IsBanned", True),
        fint("IsVolunteer", True),
        fint("IsHomeChecker", True),
        fint("IsMember", True),
        fdate("MembershipExpiryDate", True),
        fstr("MembershipNumber", True),
        fint("IsDonor", True),
        fint("IsDriver", True),
        fint("IsShelter", True),
        fint("IsACO", True), 
        fint("IsStaff", True),
        fint("IsFosterer", True),
        fint("FosterCapacity", True),
        fint("IsRetailer", True),
        fint("IsVet", True),
        fint("IsGiftAid", True),
        flongstr("AdditionalFlags", True),
        flongstr("HomeCheckAreas", True),
        fdate("DateLastHomeChecked", True),
        fint("HomeCheckedBy", True),
        fdate("MatchAdded", True),
        fdate("MatchExpires", True),
        fint("MatchActive", True),
        fint("MatchSex", True),
        fint("MatchSize", True),
        fint("MatchColour", True),
        ffloat("MatchAgeFrom", True),
        ffloat("MatchAgeTo", True),
        fint("MatchAnimalType", True),
        fint("MatchSpecies", True),
        fint("MatchBreed", True),
        fint("MatchBreed2", True),
        fint("MatchGoodWithCats", True),
        fint("MatchGoodWithDogs", True),
        fint("MatchGoodWithChildren", True),
        fint("MatchHouseTrained", True),
        fstr("MatchCommentsContain", True) ))
    sql += index("owner_MembershipNumber", "owner", "MembershipNumber")
    sql += index("owner_OwnerName", "owner", "OwnerName")
    sql += index("owner_OwnerAddress", "owner", "OwnerAddress")
    sql += index("owner_OwnerCounty", "owner", "OwnerCounty")
    sql += index("owner_EmailAddress", "owner", "EmailAddress")
    sql += index("owner_OwnerForeNames", "owner", "OwnerForeNames")
    sql += index("owner_HomeTelephone", "owner", "HomeTelephone")
    sql += index("owner_MobileTelephone", "owner", "MobileTelephone")
    sql += index("owner_WorkTelephone", "owner", "WorkTelephone")
    sql += index("owner_OwnerInitials", "owner", "OwnerInitials")
    sql += index("owner_OwnerPostcode", "owner", "OwnerPostcode")
    sql += index("owner_OwnerSurname", "owner", "OwnerSurname")
    sql += index("owner_OwnerTitle", "owner", "OwnerTitle")
    sql += index("owner_OwnerTown", "owner", "OwnerTown")

    sql += table("ownercitation", (
        fid(),
        fint("OwnerID"),
        fint("AnimalControlID", True),
        fint("CitationTypeID"),
        fdate("CitationDate"),
        fint("FineAmount", True),
        fdate("FineDueDate", True),
        fdate("FinePaidDate", True),
        flongstr("Comments", True) ))
    sql += index("ownercitation_OwnerID", "ownercitation", "OwnerID")
    sql += index("ownercitation_CitationTypeID", "ownercitation", "CitationTypeID")
    sql += index("ownercitation_CitationDate", "ownercitation", "CitationDate")
    sql += index("ownercitation_FineDueDate", "ownercitation", "FineDueDate")
    sql += index("ownercitation_FinePaidDate", "ownercitation", "FinePaidDate")

    sql += table("ownerdonation", (
        fid(),
        fint("AnimalID", True),
        fint("OwnerID"),
        fint("MovementID", True),
        fint("DonationTypeID"),
        fint("DonationPaymentID", True),
        fdate("Date", True),
        fdate("DateDue", True),
        fint("Donation"),
        fint("IsGiftAid"),
        fint("IsVAT", True),
        ffloat("VATRate", True),
        fint("VATAmount", True),
        fint("Frequency"),
        fint("NextCreated", True),
        fstr("ReceiptNumber", True),
        flongstr("Comments") ))
    sql += index("ownerdonation_OwnerID", "ownerdonation", "OwnerID")
    sql += index("ownerdonation_ReceiptNumber", "ownerdonation", "ReceiptNumber")
    sql += index("ownerdonation_Date", "ownerdonation", "Date")
    sql += index("ownerdonation_IsVAT", "ownerdonation", "IsVAT")

    sql += table("ownerinvestigation", (
        fid(),
        fint("OwnerID"),
        fdate("Date"),
        flongstr("Notes") ))
    sql += index("ownerinvestigation_OwnerID", "ownerinvestigation", "OwnerID")

    sql += table("ownerlicence", (
        fid(),
        fint("OwnerID"),
        fint("AnimalID"),
        fint("LicenceTypeID"),
        fstr("LicenceNumber"),
        fint("LicenceFee", True),
        fdate("IssueDate"),
        fdate("ExpiryDate"),
        flongstr("Comments", True) ))
    sql += index("ownerlicence_OwnerID", "ownerlicence", "OwnerID")
    sql += index("ownerlicence_AnimalID", "ownerlicence", "AnimalID")
    sql += index("ownerlicence_LicenceTypeID", "ownerlicence", "LicenceTypeID")
    sql += index("ownerlicence_LicenceNumber", "ownerlicence", "LicenceNumber", True)
    sql += index("ownerlicence_IssueDate", "ownerlicence", "IssueDate")
    sql += index("ownerlicence_ExpiryDate", "ownerlicence", "ExpiryDate")

    sql += table("ownerrota", (
        fid(),
        fint("OwnerID"),
        fdate("StartDateTime"),
        fdate("EndDateTime"),
        fint("RotaTypeID"),
        flongstr("Comments", True) ))
    sql += index("ownerrota_OwnerID", "ownerrota", "OwnerID")
    sql += index("ownerrota_StartDateTime", "ownerrota", "StartDateTime")
    sql += index("ownerrota_EndDateTime", "ownerrota", "EndDateTime")
    sql += index("ownerrota_RotaTypeID", "ownerrota", "RotaTypeID")

    sql += table("ownertraploan", (
        fid(),
        fint("OwnerID"),
        fint("TrapTypeID"),
        fdate("LoanDate"),
        fint("DepositAmount", True),
        fdate("DepositReturnDate", True),
        fstr("TrapNumber", True),
        fdate("ReturnDueDate", True),
        fdate("ReturnDate", True),
        flongstr("Comments") ))
    sql += index("ownertraploan_OwnerID", "ownertraploan", "OwnerID")
    sql += index("ownertraploan_TrapTypeID", "ownertraploan", "TrapTypeID")
    sql += index("ownertraploan_ReturnDueDate", "ownertraploan", "ReturnDueDate")
    sql += index("ownertraploan_ReturnDate", "ownertraploan", "ReturnDate")

    sql += table("ownervoucher", (
        fid(),
        fint("OwnerID"),
        fint("VoucherID"),
        fdate("DateIssued"),
        fdate("DateExpired"),
        fint("Value"),
        flongstr("Comments", True) ))
    sql += index("ownervoucher_OwnerID", "ownervoucher", "OwnerID")
    sql += index("ownervoucher_VoucherID", "ownervoucher", "VoucherID")
    sql += index("ownervoucher_DateExpired", "ownervoucher", "DateExpired")

    sql += table("pickuplocation", (
        fid(),
        fstr("LocationName"),
        fstr("LocationDescription", True),
        fint("IsRetired", True) ), False)

    sql += table("primarykey", (
        fstr("TableName"),
        fint("NextID") ), False)
    sql += index("primarykey_TableName", "primarykey", "TableName")

    sql += table("reservationstatus", (
        fid(),
        fstr("StatusName"),
        flongstr("StatusDescription", True),
        fint("IsRetired", True) ), False)

    sql += table("role", (
        fid(),
        fstr("Rolename"),
        flongstr("SecurityMap")), False)
    sql += index("role_Rolename", "role", "Rolename")

    sql += table("species", (
        fid(),
        fstr("SpeciesName"),
        fstr("SpeciesDescription", True),
        fstr("PetFinderSpecies", True),
        fint("IsRetired", True) ), False)

    sql += table("stocklevel", (
        fid(),
        fstr("Name"),
        flongstr("Description", True),
        fint("StockLocationID"),
        fstr("UnitName"),
        ffloat("Total", True),
        ffloat("Balance"),
        fdate("Expiry", True),
        fstr("BatchNumber", True),
        fdate("CreatedDate")
        ), False)
    sql += index("stocklevel_Name", "stocklevel", "Name")
    sql += index("stocklevel_UnitName", "stocklevel", "UnitName")
    sql += index("stocklevel_StockLocationID", "stocklevel", "StockLocationID")
    sql += index("stocklevel_Expiry", "stocklevel", "Expiry")
    sql += index("stocklevel_BatchNumber", "stocklevel", "BatchNumber")

    sql += table("stocklocation", (
        fid(),
        fstr("LocationName"),
        flongstr("LocationDescription", True),
        fint("IsRetired", True) ), False)
    sql += index("stocklocation_LocationName", "stocklocation", "LocationName", True)

    sql += table("stockusage", (
        fid(),
        fint("StockUsageTypeID"), 
        fint("StockLevelID"),
        fdate("UsageDate"),
        ffloat("Quantity"),
        flongstr("Comments") ))
    sql += index("stockusage_StockUsageTypeID", "stockusage", "StockUsageTypeID")
    sql += index("stockusage_StockLevelID", "stockusage", "StockLevelID")
    sql += index("stockusage_UsageDate", "stockusage", "UsageDate")

    sql += table("stockusagetype", (
        fid(),
        fstr("UsageTypeName"),
        flongstr("UsageTypeDescription", True),
        fint("IsRetired", True) ), False)
    sql += index("stockusagetype_UsageTypeName", "stockusagetype", "UsageTypeName")

    sql += table("testtype", (
        fid(),
        fstr("TestName"),
        fstr("TestDescription", True),
        fint("DefaultCost", True),
        fint("IsRetired", True) ), False)

    sql += table("testresult", (
        fid(),
        fstr("ResultName"),
        fstr("ResultDescription", True),
        fint("IsRetired", True) ), False)

    sql += table("traptype", (
        fid(),
        fstr("TrapTypeName"),
        fstr("TrapTypeDescription", True),
        fint("DefaultCost", True),
        fint("IsRetired", True) ), False)

    sql += table("users", (
        fid(),
        fstr("UserName"),
        fstr("RealName", True),
        fstr("EmailAddress", True),
        fstr("Password"),
        fint("SuperUser"),
        fint("OwnerID", True),
        flongstr("SecurityMap", True),
        flongstr("IPRestriction", True),
        flongstr("Signature", True),
        fstr("LocaleOverride", True),
        fstr("ThemeOverride", True),
        fstr("LocationFilter", True),
        fint("RecordVersion", True)), False)
    sql += index("users_UserName", "users", "UserName")

    sql += table("userrole", (
        fint("UserID"),
        fint("RoleID")), False)
    sql += index("userrole_UserIDRoleID", "userrole", "UserID, RoleID", True)

    sql += table("voucher", (
        fid(),
        fstr("VoucherName"),
        fstr("VoucherDescription", True),
        fint("DefaultCost", True),
        fint("IsRetired", True) ), False)

    sql += table("vaccinationtype", (
        fid(),
        fstr("VaccinationType"),
        fstr("VaccinationDescription", True),
        fint("DefaultCost", True),
        fint("IsRetired", True) ), False)
    return sql

def sql_default_data(dbo, skip_config = False):
    """
    Returns the SQL for the default data set
    """
    def config(key, value):
        return "INSERT INTO configuration (ItemName, ItemValue) VALUES ('%s', '%s')|=\n" % ( db.escape(key), db.escape(value) )
    def lookup1(tablename, fieldname, tid, name):
        return "INSERT INTO %s (ID, %s) VALUES (%s, '%s')|=\n" % ( tablename, fieldname, str(tid), db.escape(name) )
    def lookup2(tablename, fieldname, tid, name):
        return "INSERT INTO %s (ID, %s, IsRetired) VALUES (%s, '%s', 0)|=\n" % ( tablename, fieldname, str(tid), db.escape(name) )
    def lookup2money(tablename, fieldname, tid, name, money = 0):
        return "INSERT INTO %s (ID, %s, DefaultCost, IsRetired) VALUES (%s, '%s', %d, 0)|=\n" % ( tablename, fieldname, str(tid), db.escape(name), money)
    def account(tid, code, desc, atype, dtype, ctype):
        return "INSERT INTO accounts VALUES (%s, '%s', '%s', 0, %s, %s, %s, 0, '%s', %s, '%s', %s)|=\n" % ( str(tid), db.escape(code), db.escape(desc), str(atype), str(ctype), str(dtype), 'default', db.todaysql(), 'default', db.todaysql())
    def breed(tid, name, petfinder, speciesid):
        return "INSERT INTO breed (ID, BreedName, BreedDescription, PetFinderBreed, SpeciesID, IsRetired) VALUES (%s, '%s', '', '%s', %s, 0)|=\n" % ( str(tid), db.escape(name), petfinder, str(speciesid) )
    def basecolour(tid, name, adoptapet):
        return "INSERT INTO basecolour (ID, BaseColour, BaseColourDescription, AdoptAPetColour, IsRetired) VALUES (%s, '%s', '', '%s', 0)|=\n" % (str(tid), db.escape(name), adoptapet)
    def internallocation(lid, name):
        return "INSERT INTO internallocation (ID, LocationName, LocationDescription, Units, IsRetired) VALUES (%s, '%s', '', '', 0)|=\n" % ( str(lid), db.escape(name) )
    def species(tid, name, petfinder):
        return "INSERT INTO species (ID, SpeciesName, SpeciesDescription, PetFinderSpecies, IsRetired) VALUES (%s, '%s', '', '%s', 0)|=\n" % ( str(tid), db.escape(name), petfinder )

    l = dbo.locale
    sql = ""
    if not skip_config:
        sql += "INSERT INTO users VALUES (1,'user','Default system user', '', 'plain:letmein', 1, 0,'', '', '', '', '', '', 0)|=\n"
        sql += "INSERT INTO users VALUES (2,'guest','Default guest user', '', 'plain:guest', 0, 0,'', '', '', '', '', '', 0)|=\n"
        sql += "INSERT INTO role VALUES (1, '" + _("Other Organisation", l) + "', 'vac *va *vavet *vav *mvam *dvad *cvad *vamv *vo *volk *vle *vvov *vdn *vla *vfa *vwl *vcr *vll *')|=\n"
        sql += "INSERT INTO role VALUES (2, '" + _("Staff", l) + "', 'aa *ca *va *vavet *da *cloa *gaf *aam *cam *dam *vam *mand *aav *vav *cav *dav *bcav *maam *mcam *mdam *mvam *bcam *daad *dcad *ddad *dvad *caad *cdad *cvad *aamv *camv *vamv *damv *ao *co *vo *do *emo *mo *volk *ale *cle *dle *vle *vaov *vcov *vvov *oaod *ocod *odod *ovod *vdn *edt *adn *eadn *emdn *ecdn *bcn *ddn *pdn *pvd *ala *cla *dla *vla *afa *cfa *dfa *vfa *mlaf *vwl *awl *cwl *dwl *bcwl *all *cll *vll *dll *excr *vcr *')|=\n"
        sql += "INSERT INTO role VALUES (3, '" + _("Accountant", l) + "', 'aac *vac *cac *ctrx *dac *vaov *vcov *vdov *vvov *oaod *ocod *odod *ovod *')|=\n"
        sql += "INSERT INTO role VALUES (4, '" + _("Vet", l) + "', 'va *vavet *aav *vav *cav *dav *bcav *maam *mcam *mdam *mvam *bcam *daad *dcad *ddad *dvad * ')|=\n"
        sql += "INSERT INTO role VALUES (5, '" + _("Publisher", l) + "', 'uipb *')|=\n"
        sql += "INSERT INTO role VALUES (6, '" + _("System Admin", l) + "', 'asm *cso *cpo *maf *mdt *ml *usi *rdbu *rdbd *asu *esu *ccr *vcr *hcr *dcr *tbp *excr *')|=\n"
        sql += "INSERT INTO role VALUES (7, '" + _("Marketer", l) + "', 'uipb *mmeo *emo *mmea *')|=\n"
        sql += "INSERT INTO role VALUES (8, '" + _("Investigator", l) + "', 'aoi *coi *doi *voi *')|=\n"
        sql += "INSERT INTO role VALUES (9, '" + _("Animal Control Officer", l) + "', 'aaci *caci *daci *vaci *aacc *cacc *dacc *vacc *emo *')|=\n"
        sql += "INSERT INTO userrole VALUES (2, 1)|=\n"
        sql += config("DBV", str(LATEST_VERSION))
        sql += config("DatabaseVersion", str(LATEST_VERSION))
        sql += config("Organisation", _("Organisation", l))
        sql += config("OrganisationAddress", _("Address", l))
        sql += config("OrganisationTelephone", _("Telephone", l))
        sql += config("CodingFormat", "TYYYYNNN")
        sql += config("ShortCodingFormat", "NNNT")
        sql += config("UseShortShelterCodes", "Yes")
        sql += config("AutoDefaultShelterCode", "Yes")
        sql += config("IncomingMediaScaling", "640x640")
        sql += config("MaxMediaFileSize", "1000")
        sql += config("RecordSearchLimit", "1000")
        sql += config("SearchSort", "3")
        sql += config("AgeGroup1", "0.5")
        sql += config("AgeGroup1Name", _("Baby", l))
        sql += config("AgeGroup2", "2")
        sql += config("AgeGroup2Name", _("Young Adult", l))
        sql += config("AgeGroup3", "7")
        sql += config("AgeGroup3Name", _("Adult", l))
        sql += config("AgeGroup4", "50")
        sql += config("AgeGroup4Name", _("Senior", l))
    sql += account(1, _("Income::Donation", l), _("Incoming donations (misc)", l), 5, 1, 0)
    sql += account(2, _("Income::Adoption", l), _("Adoption fee donations", l), 5, 2, 0)
    sql += account(3, _("Income::WaitingList", l), _("Waiting list donations", l), 5, 3, 0)
    sql += account(4, _("Income::EntryDonation", l), _("Donations for animals entering the shelter", l), 5, 4, 0)
    sql += account(5, _("Income::Sponsorship", l), _("Sponsorship donations", l), 5, 5, 0)
    sql += account(6, _("Income::Shop", l), _("Income from an on-site shop", l), 5, 0, 0)
    sql += account(7, _("Income::Interest", l), _("Bank account interest", l), 5, 0, 0)
    sql += account(8, _("Income::OpeningBalances", l), _("Opening balances", l), 5, 0, 0)
    sql += account(9, _("Bank::Current", l), _("Bank current account", l), 1, 0, 0)
    sql += account(10, _("Bank::Deposit", l), _("Bank deposit account", l), 1, 0, 0)
    sql += account(11, _("Bank::Savings", l), _("Bank savings account", l), 1, 0, 0)
    sql += account(12, _("Asset::Premises", l), _("Premises", l), 8, 0, 0)
    sql += account(13, _("Expenses::Phone", l), _("Telephone Bills", l), 4, 0, 0)
    sql += account(14, _("Expenses::Electricity", l), _("Electricity Bills", l), 4, 0, 0)
    sql += account(15, _("Expenses::Water", l), _("Water Bills", l), 4, 0, 0)
    sql += account(16, _("Expenses::Gas", l), _("Gas Bills", l), 4, 0, 0)
    sql += account(17, _("Expenses::Postage", l), _("Postage costs", l), 4, 0, 0)
    sql += account(18, _("Expenses::Stationary", l), _("Stationary costs", l), 4, 0, 0)
    sql += account(19, _("Expenses::Food", l), _("Animal food costs"), 4, 0, 0)
    sql += account(20, _("Expenses::Board", l), _("Animal board costs"), 4, 0, 1)
    sql += lookup2("animaltype", "AnimalType", 2, _("D (Dog)", l))
    sql += lookup2("animaltype", "AnimalType", 10, _("A (Stray Dog)", l))
    sql += lookup2("animaltype", "AnimalType", 11, _("U (Unwanted Cat)", l))
    sql += lookup2("animaltype", "AnimalType", 12, _("S (Stray Cat)", l))
    sql += lookup2("animaltype", "AnimalType", 20, _("F (Feral Cat)", l))
    sql += lookup2("animaltype", "AnimalType", 13, _("M (Miscellaneous)", l))
    sql += lookup2("animaltype", "AnimalType", 40, _("N (Non-Shelter Animal)", l))
    sql += lookup2("animaltype", "AnimalType", 41, _("B (Boarding Animal)", l))
    sql += basecolour(1, _("Black", l), "Black")
    sql += basecolour(2, _("White", l), "White")
    sql += basecolour(3, _("Black and White", l), "Black - with White")
    sql += basecolour(4, _("Ginger", l), "Red/Golden/Orange/Chestnut")
    sql += basecolour(5, _("White and Black", l), "White - with Black")
    sql += basecolour(6, _("Tortie", l), "Tortoiseshell")
    sql += basecolour(7, _("Tabby", l), "Brown Tabby")
    sql += basecolour(8, _("Tan", l), "Tan/Yellow/Fawn")
    sql += basecolour(9, _("Black and Tan", l), "Black - with Tan, Yellow or Fawn")
    sql += basecolour(10, _("Tan and Black", l), "Black - with Tan, Yellow or Fawn")
    sql += basecolour(11, _("Brown", l), "Brown/Chocolate")
    sql += basecolour(12, _("Brown and Black", l), "Brown/Chocolate - with Black")
    sql += basecolour(13, _("Black and Brown", l), "Brown/Chocolate - with White")
    sql += basecolour(14, _("Brindle", l), "Brindle")
    sql += basecolour(15, _("Brindle and Black", l), "Brindle")
    sql += basecolour(16, _("Brindle and White", l), "Brindle - with White")
    sql += basecolour(17, _("Black and Brindle", l), "Black - with Tan, Yellow or Fawn")
    sql += basecolour(18, _("White and Brindle", l), "White - with Tan, Yelow or Fawn")
    sql += basecolour(19, _("Tricolour", l), "Tricolor (Tan/Brown & Black & White)")
    sql += basecolour(20, _("Liver", l), "Brown/Chocolate")
    sql += basecolour(21, _("Liver and White", l), "Brown/Chocolate - with White")
    sql += basecolour(22, _("White and Liver", l), "Brown/Chocolate - with White")
    sql += basecolour(23, _("Cream", l), "White")
    sql += basecolour(24, _("Tan and White", l), "White - with Tan, Yellow or Fawn")
    sql += basecolour(26, _("White and Tan", l), "White - with Tan, Yellow or Fawn")
    sql += basecolour(27, _("Tortie and White", l), "Tortoiseshell")
    sql += basecolour(28, _("Tabby and White", l), "Brown Tabby")
    sql += basecolour(29, _("Ginger and White", l), "Red/Golden/Orange/Chestnut - with White")
    sql += basecolour(30, _("Grey", l), "Gray/Blue/Silver/Salt & Pepper")
    sql += basecolour(31, _("Grey and White", l), "Gray/Silver/Salt & Pepper - with White")
    sql += basecolour(32, _("White and Grey", l), "Gray/Silver/Salt & Pepper - with White")
    sql += basecolour(33, _("White and Torti", l), "Tortoiseshell")
    sql += basecolour(35, _("Brown and White", l), "Brown/Chocolate - with White")
    sql += basecolour(36, _("Blue", l), "Gray or Blue")
    sql += basecolour(37, _("White and Tabby", l), "White")
    sql += basecolour(38, _("Yellow and Grey", l), "Tan/Yellow/Fawn")
    sql += basecolour(39, _("Various", l), "Tan/Yellow/Fawn")
    sql += basecolour(40, _("White and Brown", l), "Brown/Chocolate - with White")
    sql += basecolour(41, _("Green", l), "Green")
    sql += basecolour(42, _("Amber", l), "Red/Golden/Orange/Chestnut")
    sql += basecolour(43, _("Black Tortie", l), "Tortoiseshell")
    sql += basecolour(44, _("Blue Tortie", l), "Tortoiseshell")
    sql += basecolour(45, _("Chocolate", l), "Brown/Chocolate")
    sql += basecolour(46, _("Chocolate Tortie", l), "Tortoiseshell")
    sql += basecolour(47, _("Cinnamon", l), "Red/Golden/Orange/Chestnut")
    sql += basecolour(48, _("Cinnamon Tortoiseshell", l), "Tortoiseshell")
    sql += basecolour(49, _("Fawn", l), "Tan/Yellow/Fawn")
    sql += basecolour(50, _("Fawn Tortoiseshell", l), "Tortoiseshell")
    sql += basecolour(51, _("Golden", l), "Red/Golden/Orange/Chestnut")
    sql += basecolour(52, _("Light Amber", l), "Red/Golden/Orange/Chestnut")
    sql += basecolour(53, _("Lilac", l), "Gray/Blue/Silver/Salt & Pepper")
    sql += basecolour(54, _("Lilac Tortie", l), "Tortoiseshell")
    sql += basecolour(55, _("Ruddy", l), "Red/Golden/Orange/Chestnut")
    sql += basecolour(56, _("Seal", l), "Tan/Yellow/Fawn")
    sql += basecolour(57, _("Silver", l), "Gray/Blue/Silver/Salt & Pepper")
    sql += basecolour(58, _("Sorrel", l), "Red/Golden/Orange/Chestnut")
    sql += basecolour(59, _("Sorrel Tortoiseshell", l), "Tortoiseshell")
    sql += breed(1, _("Affenpinscher", l), "Affenpinscher", 1)
    sql += breed(2, _("Afghan Hound", l), "Afghan Hound", 1)
    sql += breed(3, _("Airedale Terrier", l), "Airedale Terrier", 1)
    sql += breed(4, _("Akbash", l), "Akbash", 1)
    sql += breed(5, _("Akita", l), "Akita", 1)
    sql += breed(6, _("Alaskan Malamute", l), "Alaskan Malamute", 1)
    sql += breed(7, _("American Bulldog", l), "American Bulldog", 1)
    sql += breed(8, _("American Eskimo Dog", l), "American Eskimo Dog", 1)
    sql += breed(9, _("American Staffordshire Terrier", l), "American Staffordshire Terrier", 1)
    sql += breed(10, _("American Water Spaniel", l), "American Water Spaniel", 1)
    sql += breed(11, _("Anatolian Shepherd", l), "Anatolian Shepherd", 1)
    sql += breed(12, _("Appenzell Mountain Dog", l), "Appenzell Mountain Dog", 1)
    sql += breed(13, _("Australian Cattle Dog/Blue Heeler", l), "Australian Cattle Dog/Blue Heeler", 1)
    sql += breed(14, _("Australian Kelpie", l), "Australian Kelpie", 1)
    sql += breed(15, _("Australian Shepherd", l), "Australian Shepherd", 1)
    sql += breed(16, _("Australian Terrier", l), "Australian Terrier", 1)
    sql += breed(17, _("Basenji", l), "Basenji", 1)
    sql += breed(18, _("Basset Hound", l), "Basset Hound", 1)
    sql += breed(19, _("Beagle", l), "Beagle", 1)
    sql += breed(20, _("Bearded Collie", l), "Bearded Collie", 1)
    sql += breed(21, _("Beauceron", l), "Beauceron", 1)
    sql += breed(22, _("Bedlington Terrier", l), "Bedlington Terrier", 1)
    sql += breed(23, _("Belgian Shepherd Dog Sheepdog", l), "Belgian Shepherd Dog Sheepdog", 1)
    sql += breed(24, _("Belgian Shepherd Laekenois", l), "Belgian Shepherd Laekenois", 1)
    sql += breed(25, _("Belgian Shepherd Malinois", l), "Belgian Shepherd Malinois", 1)
    sql += breed(26, _("Belgian Shepherd Tervuren", l), "Belgian Shepherd Tervuren", 1)
    sql += breed(27, _("Bernese Mountain Dog", l), "Bernese Mountain Dog", 1)
    sql += breed(28, _("Bichon Frise", l), "Bichon Frise", 1)
    sql += breed(29, _("Black and Tan Coonhound", l), "Black and Tan Coonhound", 1)
    sql += breed(30, _("Black Labrador Retriever", l), "Black Labrador Retriever", 1)
    sql += breed(31, _("Black Mouth Cur", l), "Black Mouth Cur", 1)
    sql += breed(32, _("Bloodhound", l), "Bloodhound", 1)
    sql += breed(33, _("Bluetick Coonhound", l), "Bluetick Coonhound", 1)
    sql += breed(34, _("Border Collie", l), "Border Collie", 1)
    sql += breed(35, _("Border Terrier", l), "Border Terrier", 1)
    sql += breed(36, _("Borzoi", l), "Borzoi", 1)
    sql += breed(37, _("Boston Terrier", l), "Boston Terrier", 1)
    sql += breed(38, _("Bouvier des Flanders", l), "Bouvier des Flanders", 1)
    sql += breed(39, _("Boykin Spaniel", l), "Boykin Spaniel", 1)
    sql += breed(40, _("Boxer", l), "Boxer", 1)
    sql += breed(41, _("Briard", l), "Briard", 1)
    sql += breed(42, _("Brittany Spaniel", l), "Brittany Spaniel", 1)
    sql += breed(43, _("Brussels Griffon", l), "Brussels Griffon", 1)
    sql += breed(44, _("Bull Terrier", l), "Bull Terrier", 1)
    sql += breed(45, _("Bullmastiff", l), "Bullmastiff", 1)
    sql += breed(46, _("Cairn Terrier", l), "Cairn Terrier", 1)
    sql += breed(47, _("Canaan Dog", l), "Canaan Dog", 1)
    sql += breed(48, _("Cane Corso Mastiff", l), "Cane Corso Mastiff", 1)
    sql += breed(49, _("Carolina Dog", l), "Carolina Dog", 1)
    sql += breed(50, _("Catahoula Leopard Dog", l), "Catahoula Leopard Dog", 1)
    sql += breed(51, _("Cattle Dog", l), "Cattle Dog", 1)
    sql += breed(52, _("Cavalier King Charles Spaniel", l), "Cavalier King Charles Spaniel", 1)
    sql += breed(53, _("Chesapeake Bay Retriever", l), "Chesapeake Bay Retriever", 1)
    sql += breed(54, _("Chihuahua", l), "Chihuahua", 1)
    sql += breed(55, _("Chinese Crested Dog", l), "Chinese Crested Dog", 1)
    sql += breed(56, _("Chinese Foo Dog", l), "Chinese Foo Dog", 1)
    sql += breed(57, _("Chocolate Labrador Retriever", l), "Chocolate Labrador Retriever", 1)
    sql += breed(58, _("Chow Chow", l), "Chow Chow", 1)
    sql += breed(59, _("Clumber Spaniel", l), "Clumber Spaniel", 1)
    sql += breed(60, _("Cockapoo", l), "Cockapoo", 1)
    sql += breed(61, _("Cocker Spaniel", l), "Cocker Spaniel", 1)
    sql += breed(62, _("Collie", l), "Collie", 1)
    sql += breed(63, _("Coonhound", l), "Coonhound", 1)
    sql += breed(64, _("Corgi", l), "Corgi", 1)
    sql += breed(65, _("Coton de Tulear", l), "Coton de Tulear", 1)
    sql += breed(66, _("Dachshund", l), "Dachshund", 1)
    sql += breed(67, _("Dalmatian", l), "Dalmatian", 1)
    sql += breed(68, _("Dandi Dinmont Terrier", l), "Dandi Dinmont Terrier", 1)
    sql += breed(69, _("Doberman Pinscher", l), "Doberman Pinscher", 1)
    sql += breed(70, _("Dogo Argentino", l), "Dogo Argentino", 1)
    sql += breed(71, _("Dogue de Bordeaux", l), "Dogue de Bordeaux", 1)
    sql += breed(72, _("Dutch Shepherd", l), "Dutch Shepherd", 1)
    sql += breed(73, _("English Bulldog", l), "English Bulldog", 1)
    sql += breed(74, _("English Cocker Spaniel", l), "English Cocker Spaniel", 1)
    sql += breed(75, _("English Coonhound", l), "English Coonhound", 1)
    sql += breed(76, _("English Pointer", l), "English Pointer", 1)
    sql += breed(77, _("English Setter", l), "English Setter", 1)
    sql += breed(78, _("English Shepherd", l), "English Shepherd", 1)
    sql += breed(79, _("English Springer Spaniel", l), "English Springer Spaniel", 1)
    sql += breed(80, _("English Toy Spaniel", l), "English Toy Spaniel", 1)
    sql += breed(81, _("Entlebucher", l), "Entlebucher", 1)
    sql += breed(82, _("Eskimo Dog", l), "Eskimo Dog", 1)
    sql += breed(83, _("Field Spaniel", l), "Field Spaniel", 1)
    sql += breed(84, _("Fila Brasileiro", l), "Fila Brasileiro", 1)
    sql += breed(85, _("Finnish Lapphund", l), "Finnish Lapphund", 1)
    sql += breed(86, _("Finnish Spitz", l), "Finnish Spitz", 1)
    sql += breed(87, _("Flat-coated Retriever", l), "Flat-coated Retriever", 1)
    sql += breed(88, _("Fox Terrier", l), "Fox Terrier", 1)
    sql += breed(89, _("Foxhound", l), "Foxhound", 1)
    sql += breed(90, _("French Bulldog", l), "French Bulldog", 1)
    sql += breed(91, _("German Pinscher", l), "German Pinscher", 1)
    sql += breed(92, _("German Shepherd Dog", l), "German Shepherd Dog", 1)
    sql += breed(93, _("German Shorthaired Pointer", l), "German Shorthaired Pointer", 1)
    sql += breed(94, _("German Wirehaired Pointer", l), "German Wirehaired Pointer", 1)
    sql += breed(95, _("Glen of Imaal Terrier", l), "Glen of Imaal Terrier", 1)
    sql += breed(96, _("Golden Retriever", l), "Golden Retriever", 1)
    sql += breed(97, _("Gordon Setter", l), "Gordon Setter", 1)
    sql += breed(98, _("Great Dane", l), "Great Dane", 1)
    sql += breed(99, _("Great Pyrenees", l), "Great Pyrenees", 1)
    sql += breed(100, _("Greater Swiss Mountain Dog", l), "Greater Swiss Mountain Dog", 1)
    sql += breed(101, _("Greyhound", l), "Greyhound", 1)
    sql += breed(102, _("Havanese", l), "Havanese", 1)
    sql += breed(103, _("Hound", l), "Hound", 1)
    sql += breed(104, _("Hovawart", l), "Hovawart", 1)
    sql += breed(105, _("Husky", l), "Husky", 1)
    sql += breed(106, _("Ibizan Hound", l), "Ibizan Hound", 1)
    sql += breed(107, _("Illyrian Sheepdog", l), "Illyrian Sheepdog", 1)
    sql += breed(108, _("Irish Setter", l), "Irish Setter", 1)
    sql += breed(109, _("Irish Terrier", l), "Irish Terrier", 1)
    sql += breed(110, _("Irish Water Spaniel", l), "Irish Water Spaniel", 1)
    sql += breed(111, _("Irish Wolfhound", l), "Irish Wolfhound", 1)
    sql += breed(112, _("Italian Greyhound", l), "Italian Greyhound", 1)
    sql += breed(113, _("Italian Spinone", l), "Italian Spinone", 1)
    sql += breed(114, _("Jack Russell Terrier", l), "Jack Russell Terrier", 1)
    sql += breed(115, _("Japanese Chin", l), "Japanese Chin", 1)
    sql += breed(116, _("Jindo", l), "Jindo", 1)
    sql += breed(117, _("Kai Dog", l), "Kai Dog", 1)
    sql += breed(118, _("Karelian Bear Dog", l), "Karelian Bear Dog", 1)
    sql += breed(119, _("Keeshond", l), "Keeshond", 1)
    sql += breed(120, _("Kerry Blue Terrier", l), "Kerry Blue Terrier", 1)
    sql += breed(121, _("Kishu", l), "Kishu", 1)
    sql += breed(122, _("Komondor", l), "Komondor", 1)
    sql += breed(123, _("Kuvasz", l), "Kuvasz", 1)
    sql += breed(124, _("Kyi Leo", l), "Kyi Leo", 1)
    sql += breed(125, _("Labrador Retriever", l), "Labrador Retriever", 1)
    sql += breed(126, _("Lakeland Terrier", l), "Lakeland Terrier", 1)
    sql += breed(127, _("Lancashire Heeler", l), "Lancashire Heeler", 1)
    sql += breed(128, _("Lhasa Apso", l), "Lhasa Apso", 1)
    sql += breed(129, _("Leonberger", l), "Leonberger", 1)
    sql += breed(130, _("Lowchen", l), "Lowchen", 1)
    sql += breed(131, _("Maltese", l), "Maltese", 1)
    sql += breed(132, _("Manchester Terrier", l), "Manchester Terrier", 1)
    sql += breed(133, _("Maremma Sheepdog", l), "Maremma Sheepdog", 1)
    sql += breed(134, _("Mastiff", l), "Mastiff", 1)
    sql += breed(135, _("McNab", l), "McNab", 1)
    sql += breed(136, _("Miniature Pinscher", l), "Miniature Pinscher", 1)
    sql += breed(137, _("Mountain Cur", l), "Mountain Cur", 1)
    sql += breed(138, _("Mountain Dog", l), "Mountain Dog", 1)
    sql += breed(139, _("Munsterlander", l), "Munsterlander", 1)
    sql += breed(140, _("Neapolitan Mastiff", l), "Neapolitan Mastiff", 1)
    sql += breed(141, _("New Guinea Singing Dog", l), "New Guinea Singing Dog", 1)
    sql += breed(142, _("Newfoundland Dog", l), "Newfoundland Dog", 1)
    sql += breed(143, _("Norfolk Terrier", l), "Norfolk Terrier", 1)
    sql += breed(144, _("Norwich Terrier", l), "Norwich Terrier", 1)
    sql += breed(145, _("Norwegian Buhund", l), "Norwegian Buhund", 1)
    sql += breed(146, _("Norwegian Elkhound", l), "Norwegian Elkhound", 1)
    sql += breed(147, _("Norwegian Lundehund", l), "Norwegian Lundehund", 1)
    sql += breed(148, _("Nova Scotia Duck-Tolling Retriever", l), "Nova Scotia Duck-Tolling Retriever", 1)
    sql += breed(149, _("Old English Sheepdog", l), "Old English Sheepdog", 1)
    sql += breed(150, _("Otterhound", l), "Otterhound", 1)
    sql += breed(151, _("Papillon", l), "Papillon", 1)
    sql += breed(152, _("Patterdale Terrier (Fell Terrier)", l), "Patterdale Terrier (Fell Terrier)", 1)
    sql += breed(153, _("Pekingese", l), "Pekingese", 1)
    sql += breed(154, _("Peruvian Inca Orchid", l), "Peruvian Inca Orchid", 1)
    sql += breed(155, _("Petit Basset Griffon Vendeen", l), "Petit Basset Griffon Vendeen", 1)
    sql += breed(156, _("Pharaoh Hound", l), "Pharaoh Hound", 1)
    sql += breed(157, _("Pit Bull Terrier", l), "Pit Bull Terrier", 1)
    sql += breed(158, _("Plott Hound", l), "Plott Hound", 1)
    sql += breed(159, _("Portugese Podengo", l), "Podengo Portugueso", 1)
    sql += breed(160, _("Pointer", l), "Pointer", 1)
    sql += breed(161, _("Polish Lowland Sheepdog", l), "Polish Lowland Sheepdog", 1)
    sql += breed(162, _("Pomeranian", l), "Pomeranian", 1)
    sql += breed(163, _("Poodle", l), "Poodle", 1)
    sql += breed(164, _("Portuguese Water Dog", l), "Portuguese Water Dog", 1)
    sql += breed(165, _("Presa Canario", l), "Presa Canario", 1)
    sql += breed(166, _("Pug", l), "Pug", 1)
    sql += breed(167, _("Puli", l), "Puli", 1)
    sql += breed(168, _("Pumi", l), "Pumi", 1)
    sql += breed(169, _("Rat Terrier", l), "Rat Terrier", 1)
    sql += breed(170, _("Redbone Coonhound", l), "Redbone Coonhound", 1)
    sql += breed(171, _("Retriever", l), "Retriever", 1)
    sql += breed(172, _("Rhodesian Ridgeback", l), "Rhodesian Ridgeback", 1)
    sql += breed(173, _("Rottweiler", l), "Rottweiler", 1)
    sql += breed(174, _("Saluki", l), "Saluki", 1)
    sql += breed(175, _("Saint Bernard St. Bernard", l), "Saint Bernard St. Bernard", 1)
    sql += breed(176, _("Samoyed", l), "Samoyed", 1)
    sql += breed(177, _("Schipperke", l), "Schipperke", 1)
    sql += breed(178, _("Schnauzer", l), "Schnauzer", 1)
    sql += breed(179, _("Scottish Deerhound", l), "Scottish Deerhound", 1)
    sql += breed(180, _("Scottish Terrier Scottie", l), "Scottish Terrier Scottie", 1)
    sql += breed(181, _("Sealyham Terrier", l), "Sealyham Terrier", 1)
    sql += breed(182, _("Setter", l), "Setter", 1)
    sql += breed(183, _("Shar Pei", l), "Shar Pei", 1)
    sql += breed(184, _("Sheep Dog", l), "Sheep Dog", 1)
    sql += breed(185, _("Shepherd", l), "Shepherd", 1)
    sql += breed(186, _("Shetland Sheepdog Sheltie", l), "Shetland Sheepdog Sheltie", 1)
    sql += breed(187, _("Shiba Inu", l), "Shiba Inu", 1)
    sql += breed(188, _("Shih Tzu", l), "Shih Tzu", 1)
    sql += breed(189, _("Siberian Husky", l), "Siberian Husky", 1)
    sql += breed(190, _("Silky Terrier", l), "Silky Terrier", 1)
    sql += breed(191, _("Skye Terrier", l), "Skye Terrier", 1)
    sql += breed(192, _("Sloughi", l), "Sloughi", 1)
    sql += breed(193, _("Smooth Fox Terrier", l), "Smooth Fox Terrier", 1)
    sql += breed(194, _("Spaniel", l), "Spaniel", 1)
    sql += breed(195, _("Spitz", l), "Spitz", 1)
    sql += breed(196, _("Staffordshire Bull Terrier", l), "Staffordshire Bull Terrier", 1)
    sql += breed(197, _("South Russian Ovcharka", l), "South Russian Ovcharka", 1)
    sql += breed(198, _("Swedish Vallhund", l), "Swedish Vallhund", 1)
    sql += breed(199, _("Terrier", l), "Terrier", 1)
    sql += breed(200, _("Thai Ridgeback", l), "Thai Ridgeback", 1)
    sql += breed(201, _("Tibetan Mastiff", l), "Tibetan Mastiff", 1)
    sql += breed(202, _("Tibetan Spaniel", l), "Tibetan Spaniel", 1)
    sql += breed(203, _("Tibetan Terrier", l), "Tibetan Terrier", 1)
    sql += breed(204, _("Tosa Inu", l), "Tosa Inu", 1)
    sql += breed(205, _("Toy Fox Terrier", l), "Toy Fox Terrier", 1)
    sql += breed(206, _("Treeing Walker Coonhound", l), "Treeing Walker Coonhound", 1)
    sql += breed(207, _("Vizsla", l), "Vizsla", 1)
    sql += breed(208, _("Weimaraner", l), "Weimaraner", 1)
    sql += breed(209, _("Welsh Corgi", l), "Welsh Corgi", 1)
    sql += breed(210, _("Welsh Terrier", l), "Welsh Terrier", 1)
    sql += breed(211, _("Welsh Springer Spaniel", l), "Welsh Springer Spaniel", 1)
    sql += breed(212, _("West Highland White Terrier Westie", l), "West Highland White Terrier Westie", 1)
    sql += breed(213, _("Wheaten Terrier", l), "Wheaten Terrier", 1)
    sql += breed(214, _("Whippet", l), "Whippet", 1)
    sql += breed(215, _("White German Shepherd", l), "White German Shepherd", 1)
    sql += breed(216, _("Wire-haired Pointing Griffon", l), "Wire-haired Pointing Griffon", 1)
    sql += breed(217, _("Wirehaired Terrier", l), "Wirehaired Terrier", 1)
    sql += breed(218, _("Yellow Labrador Retriever", l), "Yellow Labrador Retriever", 1)
    sql += breed(219, _("Yorkshire Terrier Yorkie", l), "Yorkshire Terrier Yorkie", 1)
    sql += breed(220, _("Xoloitzcuintle/Mexican Hairless", l), "Xoloitzcuintle/Mexican Hairless", 1)
    sql += breed(221, _("Abyssinian", l), "Abyssinian", 2)
    sql += breed(222, _("American Curl", l), "American Curl", 2)
    sql += breed(223, _("American Shorthair", l), "American Shorthair", 2)
    sql += breed(224, _("American Wirehair", l), "American Wirehair", 2)
    sql += breed(225, _("Applehead Siamese", l), "Applehead Siamese", 2)
    sql += breed(226, _("Balinese", l), "Balinese", 2)
    sql += breed(227, _("Bengal", l), "Bengal", 2)
    sql += breed(228, _("Birman", l), "Birman", 2)
    sql += breed(229, _("Bobtail", l), "Bobtail", 2)
    sql += breed(230, _("Bombay", l), "Bombay", 2)
    sql += breed(231, _("British Shorthair", l), "British Shorthair", 2)
    sql += breed(232, _("Burmese", l), "Burmese", 2)
    sql += breed(233, _("Burmilla", l), "Burmilla", 2)
    sql += breed(234, _("Calico", l), "Calico", 2)
    sql += breed(235, _("Canadian Hairless", l), "Canadian Hairless", 2)
    sql += breed(236, _("Chartreux", l), "Chartreux", 2)
    sql += breed(237, _("Chinchilla", l), "Chinchilla", 2)
    sql += breed(238, _("Cornish Rex", l), "Cornish Rex", 2)
    sql += breed(239, _("Cymric", l), "Cymric", 2)
    sql += breed(240, _("Devon Rex", l), "Devon Rex", 2)
    sql += breed(243, _("Domestic Long Hair", l), "Domestic Long Hair", 2)
    sql += breed(252, _("Domestic Medium Hair", l), "Domestic Medium Hair", 2)
    sql += breed(261, _("Domestic Short Hair", l), "Domestic Short Hair", 2)
    sql += breed(271, _("Egyptian Mau", l), "Egyptian Mau", 2)
    sql += breed(272, _("Exotic Shorthair", l), "Exotic Shorthair", 2)
    sql += breed(273, _("Extra-Toes Cat (Hemingway Polydactyl)", l), "Extra-Toes Cat (Hemingway Polydactyl)", 2)
    sql += breed(274, _("Havana", l), "Havana", 2)
    sql += breed(275, _("Himalayan", l), "Himalayan", 2)
    sql += breed(276, _("Japanese Bobtail", l), "Japanese Bobtail", 2)
    sql += breed(277, _("Javanese", l), "Javanese", 2)
    sql += breed(278, _("Korat", l), "Korat", 2)
    sql += breed(279, _("Maine Coon", l), "Maine Coon", 2)
    sql += breed(280, _("Manx", l), "Manx", 2)
    sql += breed(281, _("Munchkin", l), "Munchkin", 2)
    sql += breed(282, _("Norwegian Forest Cat", l), "Norwegian Forest Cat", 2)
    sql += breed(283, _("Ocicat", l), "Ocicat", 2)
    sql += breed(284, _("Oriental Long Hair", l), "Oriental Long Hair", 2)
    sql += breed(285, _("Oriental Short Hair", l), "Oriental Short Hair", 2)
    sql += breed(286, _("Oriental Tabby", l), "Oriental Tabby", 2)
    sql += breed(287, _("Persian", l), "Persian", 2)
    sql += breed(288, _("Pixie-Bob", l), "Pixie-Bob", 2)
    sql += breed(289, _("Ragamuffin", l), "Ragamuffin", 2)
    sql += breed(290, _("Ragdoll", l), "Ragdoll", 2)
    sql += breed(291, _("Russian Blue", l), "Russian Blue", 2)
    sql += breed(292, _("Scottish Fold", l), "Scottish Fold", 2)
    sql += breed(293, _("Selkirk Rex", l), "Selkirk Rex", 2)
    sql += breed(294, _("Siamese", l), "Siamese", 2)
    sql += breed(295, _("Siberian", l), "Siberian", 2)
    sql += breed(296, _("Singapura", l), "Singapura", 2)
    sql += breed(297, _("Snowshoe", l), "Snowshoe", 2)
    sql += breed(298, _("Somali", l), "Somali", 2)
    sql += breed(299, _("Sphynx (hairless cat)", l), "Sphynx (hairless cat)", 2)
    sql += breed(307, _("Tiger", l), "Tiger", 2)
    sql += breed(308, _("Tonkinese", l), "Tonkinese", 2)
    sql += breed(311, _("Turkish Angora", l), "Turkish Angora", 2)
    sql += breed(312, _("Turkish Van", l), "Turkish Van", 2)
    sql += breed(314, _("American", l), "American", 7)
    sql += breed(315, _("American Fuzzy Lop", l), "American Fuzzy Lop", 7)
    sql += breed(316, _("American Sable", l), "American Sable", 7)
    sql += breed(317, _("Angora Rabbit", l), "Angora Rabbit", 7)
    sql += breed(318, _("Belgian Hare", l), "Belgian Hare", 7)
    sql += breed(319, _("Beveren", l), "Beveren", 7)
    sql += breed(320, _("Britannia Petite", l), "Britannia Petite", 7)
    sql += breed(321, _("Bunny Rabbit", l), "Bunny Rabbit", 7)
    sql += breed(322, _("Californian", l), "Californian", 7)
    sql += breed(323, _("Champagne DArgent", l), "Champagne DArgent", 7)
    sql += breed(324, _("Checkered Giant", l), "Checkered Giant", 7)
    sql += breed(325, _("Chinchilla", l), "Chinchilla", 7)
    sql += breed(326, _("Cinnamon", l), "Cinnamon", 7)
    sql += breed(327, _("Creme DArgent", l), "Creme DArgent", 7)
    sql += breed(328, _("Dutch", l), "Dutch", 7)
    sql += breed(329, _("Dwarf", l), "Dwarf", 7)
    sql += breed(330, _("Dwarf Eared", l), "Dwarf Eared", 7)
    sql += breed(331, _("English Lop", l), "English Lop", 7)
    sql += breed(332, _("English Spot", l), "English Spot", 7)
    sql += breed(333, _("Flemish Giant", l), "Flemish Giant", 7)
    sql += breed(334, _("Florida White", l), "Florida White", 7)
    sql += breed(335, _("French-Lop", l), "French-Lop", 7)
    sql += breed(336, _("Harlequin", l), "Harlequin", 7)
    sql += breed(337, _("Havana", l), "Havana", 7)
    sql += breed(338, _("Himalayan", l), "Himalayan", 7)
    sql += breed(339, _("Holland Lop", l), "Holland Lop", 7)
    sql += breed(340, _("Hotot", l), "Hotot", 7)
    sql += breed(341, _("Jersey Wooly", l), "Jersey Wooly", 7)
    sql += breed(342, _("Lilac", l), "Lilac", 7)
    sql += breed(343, _("Lop Eared", l), "Lop Eared", 7)
    sql += breed(344, _("Mini-Lop", l), "Mini-Lop", 7)
    sql += breed(345, _("Mini Rex", l), "Mini Rex", 7)
    sql += breed(346, _("Netherland Dwarf", l), "Netherland Dwarf", 7)
    sql += breed(347, _("New Zealand", l), "New Zealand", 7)
    sql += breed(348, _("Palomino", l), "Palomino", 7)
    sql += breed(349, _("Polish", l), "Polish", 7)
    sql += breed(350, _("Rex", l), "Rex", 7)
    sql += breed(351, _("Rhinelander", l), "Rhinelander", 7)
    sql += breed(352, _("Satin", l), "Satin", 7)
    sql += breed(353, _("Silver", l), "Silver", 7)
    sql += breed(354, _("Silver Fox", l), "Silver Fox", 7)
    sql += breed(355, _("Silver Marten", l), "Silver Marten", 7)
    sql += breed(356, _("Tan", l), "Tan", 7)
    sql += breed(357, _("Appaloosa", l), "Appaloosa", 24)
    sql += breed(358, _("Arabian", l), "Arabian", 24)
    sql += breed(359, _("Clydesdale", l), "Clydesdale", 24)
    sql += breed(360, _("Donkey/Mule", l), "Donkey/Mule", 26)
    sql += breed(361, _("Draft", l), "Draft", 24)
    sql += breed(362, _("Gaited", l), "Gaited", 24)
    sql += breed(363, _("Grade", l), "Grade", 24)
    sql += breed(364, _("Missouri Foxtrotter", l), "Missouri Foxtrotter", 24)
    sql += breed(365, _("Morgan", l), "Morgan", 24)
    sql += breed(366, _("Mustang", l), "Mustang", 24)
    sql += breed(367, _("Paint/Pinto", l), "Paint/Pinto", 24)
    sql += breed(368, _("Palomino", l), "Palomino", 24)
    sql += breed(369, _("Paso Fino", l), "Paso Fino", 24)
    sql += breed(370, _("Percheron", l), "Percheron", 24)
    sql += breed(371, _("Peruvian Paso", l), "Peruvian Paso", 24)
    sql += breed(372, _("Pony", l), "Pony", 25)
    sql += breed(373, _("Quarterhorse", l), "Quarterhorse", 25)
    sql += breed(374, _("Saddlebred", l), "Saddlebred", 24)
    sql += breed(375, _("Standardbred", l), "Standardbred", 24)
    sql += breed(376, _("Thoroughbred", l), "Thoroughbred", 24)
    sql += breed(377, _("Tennessee Walker", l), "Tennessee Walker", 24)
    sql += breed(378, _("Warmblood", l), "Warmblood", 24)
    sql += breed(379, _("Chinchilla", l), "Chinchilla", 10)
    sql += breed(380, _("Ferret", l), "Ferret", 9)
    sql += breed(381, _("Gerbil", l), "Gerbil", 18)
    sql += breed(382, _("Guinea Pig", l), "Guinea Pig", 20)
    sql += breed(383, _("Hamster", l), "Hamster", 22)
    sql += breed(384, _("Hedgehog", l), "Hedgehog", 6)
    sql += breed(385, _("Mouse", l), "Mouse", 4)
    sql += breed(386, _("Prairie Dog", l), "Prairie Dog", 5)
    sql += breed(387, _("Rat", l), "Rat", 5)
    sql += breed(388, _("Skunk", l), "Skunk", 5)
    sql += breed(389, _("Sugar Glider", l), "Sugar Glider", 5)
    sql += breed(390, _("Pot Bellied", l), "Pot Bellied", 28)
    sql += breed(391, _("Vietnamese Pot Bellied", l), "Vietnamese Pot Bellied", 28)
    sql += breed(392, _("Gecko", l), "Gecko", 13)
    sql += breed(393, _("Iguana", l), "Iguana", 13)
    sql += breed(394, _("Lizard", l), "Lizard", 13)
    sql += breed(395, _("Snake", l), "Snake", 13)
    sql += breed(396, _("Turtle", l), "Turtle", 13)
    sql += breed(397, _("Fish", l), "Fish", 21)
    sql += breed(398, _("African Grey", l), "African Grey", 3)
    sql += breed(399, _("Amazon", l), "Amazon", 3)
    sql += breed(400, _("Brotogeris", l), "Brotogeris", 3)
    sql += breed(401, _("Budgie/Budgerigar", l), "Budgie/Budgerigar", 3)
    sql += breed(402, _("Caique", l), "Caique", 3)
    sql += breed(403, _("Canary", l), "Canary", 3)
    sql += breed(404, _("Chicken", l), "Chicken", 3)
    sql += breed(405, _("Cockatiel", l), "Cockatiel", 3)
    sql += breed(406, _("Cockatoo", l), "Cockatoo", 3)
    sql += breed(407, _("Conure", l), "Conure", 3)
    sql += breed(408, _("Dove", l), "Dove", 3)
    sql += breed(409, _("Duck", l), "Duck", 3)
    sql += breed(410, _("Eclectus", l), "Eclectus", 3)
    sql += breed(411, _("Emu", l), "Emu", 3)
    sql += breed(412, _("Finch", l), "Finch", 3)
    sql += breed(413, _("Goose", l), "Goose", 3)
    sql += breed(414, _("Guinea fowl", l), "Guinea fowl", 3)
    sql += breed(415, _("Kakariki", l), "Kakariki", 3)
    sql += breed(416, _("Lory/Lorikeet", l), "Lory/Lorikeet", 3)
    sql += breed(417, _("Lovebird", l), "Lovebird", 3)
    sql += breed(418, _("Macaw", l), "Macaw", 3)
    sql += breed(419, _("Mynah", l), "Mynah", 3)
    sql += breed(420, _("Ostrich", l), "Ostrich", 3)
    sql += breed(421, _("Parakeet (Other)", l), "Parakeet (Other)", 3)
    sql += breed(422, _("Parrot (Other)", l), "Parrot (Other)", 3)
    sql += breed(423, _("Parrotlet", l), "Parrotlet", 3)
    sql += breed(424, _("Peacock/Pea fowl", l), "Peacock/Pea fowl", 3)
    sql += breed(425, _("Pheasant", l), "Pheasant", 3)
    sql += breed(426, _("Pigeon", l), "Pigeon", 3)
    sql += breed(427, _("Pionus", l), "Pionus", 3)
    sql += breed(428, _("Poicephalus/Senegal", l), "Poicephalus/Senegal", 3)
    sql += breed(429, _("Quaker Parakeet", l), "Quaker Parakeet", 3)
    sql += breed(430, _("Rhea", l), "Rhea", 3)
    sql += breed(431, _("Ringneck/Psittacula", l), "Ringneck/Psittacula", 3)
    sql += breed(432, _("Rosella", l), "Rosella", 3)
    sql += breed(433, _("Softbill (Other)", l), "Softbill (Other)", 3)
    sql += breed(434, _("Swan", l), "Swan", 3)
    sql += breed(435, _("Toucan", l), "Toucan", 3)
    sql += breed(436, _("Turkey", l), "Turkey", 3)
    sql += breed(437, _("Cow", l), "Cow", 16)
    sql += breed(438, _("Goat", l), "Goat", 16)
    sql += breed(439, _("Sheep", l), "Sheep", 16)
    sql += breed(440, _("Llama", l), "Llama", 16)
    sql += breed(441, _("Pig (Farm)", l), "Pig (Farm)", 28)
    sql += breed(442, _("Crossbreed", l), "Terrier", 1)
    sql += lookup2money("citationtype", "CitationName", 1, _("First offence", l))
    sql += lookup2money("citationtype", "CitationName", 2, _("Second offence", l))
    sql += lookup2money("citationtype", "CitationName", 3, _("Third offence", l))
    sql += lookup2money("costtype", "CostTypeName", 1, _("Board and Food", l))
    sql += lookup2("deathreason", "ReasonName", 1, _("Dead On Arrival", l))
    sql += lookup2("deathreason", "ReasonName", 2, _("Died", l))
    sql += lookup2("deathreason", "ReasonName", 3, _("Healthy", l))
    sql += lookup2("deathreason", "ReasonName", 4, _("Sick/Injured", l))
    sql += lookup2("deathreason", "ReasonName", 5, _("Requested", l))
    sql += lookup2("deathreason", "ReasonName", 6, _("Culling", l))
    sql += lookup2("deathreason", "ReasonName", 7, _("Feral", l))
    sql += lookup2("deathreason", "ReasonName", 8, _("Biting", l))
    sql += lookup2("diet", "DietName", 1, _("Standard", l))
    sql += lookup2("donationpayment", "PaymentName", 1, _("Cash", l))
    sql += lookup2("donationpayment", "PaymentName", 2, _("Cheque", l))
    sql += lookup2("donationpayment", "PaymentName", 3, _("Credit Card", l))
    sql += lookup2("donationpayment", "PaymentName", 4, _("Debit Card", l))
    sql += lookup2money("donationtype", "DonationName", 1, _("Donation", l))
    sql += lookup2money("donationtype", "DonationName", 2, _("Adoption Fee", l))
    sql += lookup2money("donationtype", "DonationName", 3, _("Waiting List Donation", l))
    sql += lookup2money("donationtype", "DonationName", 4, _("Entry Donation", l))
    sql += lookup2money("donationtype", "DonationName", 5, _("Animal Sponsorship", l))
    sql += lookup2("entryreason", "ReasonName", 1, _("Marriage/Relationship split", l))
    sql += lookup2("entryreason", "ReasonName", 2, _("Allergies", l))
    sql += lookup2("entryreason", "ReasonName", 3, _("Biting", l))
    sql += lookup2("entryreason", "ReasonName", 4, _("Unable to Cope", l))
    sql += lookup2("entryreason", "ReasonName", 5, _("Unsuitable Accomodation", l))
    sql += lookup2("entryreason", "ReasonName", 6, _("Died", l))
    sql += lookup2("entryreason", "ReasonName", 7, _("Stray", l))
    sql += lookup2("entryreason", "ReasonName", 8, _("Sick/Injured", l))
    sql += lookup2("entryreason", "ReasonName", 9, _("Unable to Afford", l))
    sql += lookup2("entryreason", "ReasonName", 10, _("Abuse", l))
    sql += lookup2("entryreason", "ReasonName", 11, _("Abandoned", l))
    sql += lookup2("entryreason", "ReasonName", 12, _("Boarding", l))
    sql += lookup2("entryreason", "ReasonName", 13, _("Born in Shelter", l))
    sql += lookup2("entryreason", "ReasonName", 14, _("TNR - Trap/Neuter/Release", l))
    sql += lookup2("entryreason", "ReasonName", 15, _("Transfer from Other Shelter", l))
    sql += lookup2("entryreason", "ReasonName", 16, _("Transfer from Municipal Shelter", l))
    sql += lookup2("incidentcompleted", "CompletedName", 1, _("Animal destroyed", l))
    sql += lookup2("incidentcompleted", "CompletedName", 2, _("Animal picked up", l))
    sql += lookup2("incidentcompleted", "CompletedName", 3, _("Owner given citation", l))
    sql += lookup2("incidenttype", "IncidentName", 1, _("Aggression", l))
    sql += lookup2("incidenttype", "IncidentName", 2, _("Animal defecation", l))
    sql += lookup2("incidenttype", "IncidentName", 3, _("Animals at large", l))
    sql += lookup2("incidenttype", "IncidentName", 4, _("Animals left in vehicle", l))
    sql += lookup2("incidenttype", "IncidentName", 5, _("Bite", l))
    sql += lookup2("incidenttype", "IncidentName", 6, _("Dead animal", l))
    sql += lookup2("incidenttype", "IncidentName", 7, _("Neglect", l))
    sql += lookup2("incidenttype", "IncidentName", 8, _("Noise", l))
    sql += lookup2("incidenttype", "IncidentName", 9, _("Number of pets", l))
    sql += lookup2("incidenttype", "IncidentName", 10, _("Sick/injured animal", l))
    sql += internallocation(1, _("Shelter", l))
    sql += lookup2money("licencetype", "LicenceTypeName", 1, _("Altered Dog - 1 year", l))
    sql += lookup2money("licencetype", "LicenceTypeName", 2, _("Unaltered Dog - 1 year", l))
    sql += lookup2money("licencetype", "LicenceTypeName", 3, _("Altered Dog - 3 year", l))
    sql += lookup2money("licencetype", "LicenceTypeName", 4, _("Unaltered Dog - 3 year", l))
    sql += lookup1("lksex", "Sex", 0, _("Female", l))
    sql += lookup1("lksex", "Sex", 1, _("Male", l))
    sql += lookup1("lksex", "Sex", 2, _("Unknown", l))
    sql += lookup1("lksize", "Size", 0, _("Very Large", l))
    sql += lookup1("lksize", "Size", 1, _("Large", l))
    sql += lookup1("lksize", "Size", 2, _("Medium", l))
    sql += lookup1("lksize", "Size", 3, _("Small", l))
    sql += lookup1("lkcoattype", "CoatType", 0, _("Short", l))
    sql += lookup1("lkcoattype", "CoatType", 1, _("Long", l))
    sql += lookup1("lkcoattype", "CoatType", 2, _("Rough", l))
    sql += lookup1("lkcoattype", "CoatType", 3, _("Curly", l))
    sql += lookup1("lkcoattype", "CoatType", 4, _("Corded", l))
    sql += lookup1("lkcoattype", "CoatType", 5, _("Hairless", l))
    sql += lookup1("lksaccounttype", "AccountType", 1, _("Bank", l))
    sql += lookup1("lksaccounttype", "AccountType", 2, _("Credit Card", l))
    sql += lookup1("lksaccounttype", "AccountType", 3, _("Loan", l))
    sql += lookup1("lksaccounttype", "AccountType", 4, _("Expense", l))
    sql += lookup1("lksaccounttype", "AccountType", 5, _("Income", l))
    sql += lookup1("lksaccounttype", "AccountType", 6, _("Pension", l))
    sql += lookup1("lksaccounttype", "AccountType", 7, _("Shares", l))
    sql += lookup1("lksaccounttype", "AccountType", 8, _("Asset", l))
    sql += lookup1("lksaccounttype", "AccountType", 9, _("Liability", l))
    sql += lookup1("lksmovementtype", "MovementType", 0, _("None", l))
    sql += lookup1("lksmovementtype", "MovementType", 1, _("Adoption", l))
    sql += lookup1("lksmovementtype", "MovementType", 2, _("Foster", l))
    sql += lookup1("lksmovementtype", "MovementType", 3, _("Transfer", l))
    sql += lookup1("lksmovementtype", "MovementType", 4, _("Escaped", l))
    sql += lookup1("lksmovementtype", "MovementType", 5, _("Reclaimed", l))
    sql += lookup1("lksmovementtype", "MovementType", 6, _("Stolen", l))
    sql += lookup1("lksmovementtype", "MovementType", 7, _("Released To Wild", l))
    sql += lookup1("lksmovementtype", "MovementType", 8, _("Retailer", l))
    sql += lookup1("lksmovementtype", "MovementType", 9, _("Reservation", l))
    sql += lookup1("lksmovementtype", "MovementType", 10, _("Cancelled Reservation", l))
    sql += lookup1("lksmovementtype", "MovementType", 11, _("Trial Adoption", l))
    sql += lookup1("lksmovementtype", "MovementType", 12, _("Permanent Foster", l))
    sql += lookup1("lksmedialink", "LinkType", 0, _("Animal", l))
    sql += lookup1("lksmedialink", "LinkType", 1, _("Lost Animal", l))
    sql += lookup1("lksmedialink", "LinkType", 2, _("Found Animal", l))
    sql += lookup1("lksmedialink", "LinkType", 3, _("Owner", l))
    sql += lookup1("lksmedialink", "LinkType", 4, _("Movement", l))
    sql += lookup1("lksmedialink", "LinkType", 5, _("Incident", l))
    sql += lookup1("lksmediatype", "MediaType", 0, _("File", l))
    sql += lookup1("lksmediatype", "MediaType", 1, _("Document Link", l))
    sql += lookup1("lksmediatype", "MediaType", 2, _("Video Link", l))
    sql += lookup1("lksdiarylink", "LinkType", 0, _("None", l))
    sql += lookup1("lksdiarylink", "LinkType", 1, _("Animal", l))
    sql += lookup1("lksdiarylink", "LinkType", 2, _("Owner", l))
    sql += lookup1("lksdiarylink", "LinkType", 3, _("Lost Animal", l))
    sql += lookup1("lksdiarylink", "LinkType", 4, _("Found Animal", l))
    sql += lookup1("lksdiarylink", "LinkType", 5, _("Waiting List", l))
    sql += lookup1("lksdiarylink", "LinkType", 6, _("Movement", l))
    sql += lookup1("lksdiarylink", "LinkType", 7, _("Incident", l))
    sql += lookup1("lksdonationfreq", "Frequency", 0, _("One-Off", l))
    sql += lookup1("lksdonationfreq", "Frequency", 1, _("Weekly", l))
    sql += lookup1("lksdonationfreq", "Frequency", 2, _("Monthly", l))
    sql += lookup1("lksdonationfreq", "Frequency", 3, _("Quarterly", l))
    sql += lookup1("lksdonationfreq", "Frequency", 4, _("Half-Yearly", l))
    sql += lookup1("lksdonationfreq", "Frequency", 5, _("Annually", l))
    sql += lookup1("lksfieldlink", "LinkType", 0, _("Animal - Additional", l))
    sql += lookup1("lksfieldlink", "LinkType", 2, _("Animal - Details", l))
    sql += lookup1("lksfieldlink", "LinkType", 3, _("Animal - Notes", l))
    sql += lookup1("lksfieldlink", "LinkType", 4, _("Animal - Entry", l))
    sql += lookup1("lksfieldlink", "LinkType", 5, _("Animal - Health and Identification", l))
    sql += lookup1("lksfieldlink", "LinkType", 6, _("Animal - Death", l))
    sql += lookup1("lksfieldlink", "LinkType", 1, _("Person - Additional", l))
    sql += lookup1("lksfieldlink", "LinkType", 7, _("Person - Name and Address", l))
    sql += lookup1("lksfieldlink", "LinkType", 8, _("Person - Type", l))
    sql += lookup1("lksfieldlink", "LinkType", 9, _("Lost Animal - Additional", l))
    sql += lookup1("lksfieldlink", "LinkType", 10, _("Lost Animal - Details", l))
    sql += lookup1("lksfieldlink", "LinkType", 11, _("Found Animal - Additional", l))
    sql += lookup1("lksfieldlink", "LinkType", 12, _("Found Animal - Details", l))
    sql += lookup1("lksfieldlink", "LinkType", 13, _("Waiting List - Additional", l))
    sql += lookup1("lksfieldlink", "LinkType", 14, _("Waiting List - Details", l))
    sql += lookup1("lksfieldlink", "LinkType", 15, _("Waiting List - Removal", l))
    sql += lookup1("lksfieldlink", "LinkType", 16, _("Incident - Details", l))
    sql += lookup1("lksfieldlink", "LinkType", 17, _("Incident - Dispatch", l))
    sql += lookup1("lksfieldlink", "LinkType", 18, _("Incident - Owner", l))
    sql += lookup1("lksfieldlink", "LinkType", 19, _("Incident - Citation", l))
    sql += lookup1("lksfieldlink", "LinkType", 20, _("Incident - Additional", l))
    sql += lookup1("lksfieldtype", "FieldType", 0, _("Yes/No", l))
    sql += lookup1("lksfieldtype", "FieldType", 1, _("Text", l))
    sql += lookup1("lksfieldtype", "FieldType", 2, _("Notes", l))
    sql += lookup1("lksfieldtype", "FieldType", 3, _("Number", l))
    sql += lookup1("lksfieldtype", "FieldType", 4, _("Date", l))
    sql += lookup1("lksfieldtype", "FieldType", 5, _("Money", l))
    sql += lookup1("lksfieldtype", "FieldType", 6, _("Lookup", l))
    sql += lookup1("lksfieldtype", "FieldType", 7, _("Multi-Lookup", l))
    sql += lookup1("lksfieldtype", "FieldType", 8, _("Animal", l))
    sql += lookup1("lksfieldtype", "FieldType", 9, _("Person", l))
    sql += lookup1("lksloglink", "LinkType", 0, _("Animal", l))
    sql += lookup1("lksloglink", "LinkType", 1, _("Owner", l))
    sql += lookup1("lksloglink", "LinkType", 2, _("Lost Animal", l))
    sql += lookup1("lksloglink", "LinkType", 3, _("Found Animal", l))
    sql += lookup1("lksloglink", "LinkType", 4, _("Waiting List", l))
    sql += lookup1("lksloglink", "LinkType", 5, _("Movement", l))
    sql += lookup1("lksloglink", "LinkType", 6, _("Incident", l))
    sql += lookup1("lksyesno", "Name", 0, _("No", l))
    sql += lookup1("lksyesno", "Name", 1, _("Yes", l))
    sql += lookup1("lksynun", "Name", 0, _("Yes", l))
    sql += lookup1("lksynun", "Name", 1, _("No", l))
    sql += lookup1("lksynun", "Name", 2, _("Unknown", l))
    sql += lookup1("lksposneg", "Name", 0, _("Unknown", l))
    sql += lookup1("lksposneg", "Name", 1, _("Negative", l))
    sql += lookup1("lksposneg", "Name", 2, _("Positive", l))
    sql += lookup1("lksrotatype", "RotaType", 1, _("Shift", l))
    sql += lookup1("lksrotatype", "RotaType", 2, _("Overtime", l))
    sql += lookup1("lksrotatype", "RotaType", 11, _("Public Holiday", l))
    sql += lookup1("lksrotatype", "RotaType", 12, _("Vacation", l))
    sql += lookup1("lksrotatype", "RotaType", 13, _("Leave of absence", l))
    sql += lookup1("lksrotatype", "RotaType", 14, _("Maternity", l))
    sql += lookup1("lksrotatype", "RotaType", 15, _("Personal", l))
    sql += lookup1("lksrotatype", "RotaType", 16, _("Rostered day off", l))
    sql += lookup1("lksrotatype", "RotaType", 17, _("Sick leave", l))
    sql += lookup1("lksrotatype", "RotaType", 18, _("Training", l))
    sql += lookup1("lksrotatype", "RotaType", 19, _("Unavailable", l))
    sql += lookup1("lkurgency", "Urgency", 1, _("Urgent", l))
    sql += lookup1("lkurgency", "Urgency", 2, _("High", l))
    sql += lookup1("lkurgency", "Urgency", 3, _("Medium", l))
    sql += lookup1("lkurgency", "Urgency", 4, _("Low", l))
    sql += lookup1("lkurgency", "Urgency", 5, _("Lowest", l))
    sql += lookup2("logtype", "LogTypeName", 1, _("Bite", l))
    sql += lookup2("logtype", "LogTypeName", 2, _("Complaint", l))
    sql += lookup2("logtype", "LogTypeName", 3, _("History", l))
    sql += lookup2("logtype", "LogTypeName", 4, _("Weight", l))
    sql += lookup2("logtype", "LogTypeName", 5, _("Document", l))
    sql += lookup2("pickuplocation", "LocationName", 1, _("Shelter", l))
    sql += lookup2("reservationstatus", "StatusName", 1, _("More Info Needed", l))
    sql += lookup2("reservationstatus", "StatusName", 2, _("Pending Vet Check", l))
    sql += lookup2("reservationstatus", "StatusName", 3, _("Pending Apartment Verification", l))
    sql += lookup2("reservationstatus", "StatusName", 4, _("Pending Home Visit", l))
    sql += lookup2("reservationstatus", "StatusName", 5, _("Pending Adoption", l))
    sql += lookup2("reservationstatus", "StatusName", 6, _("Changed Mind", l))
    sql += lookup2("reservationstatus", "StatusName", 7, _("Denied", l))
    sql += lookup2("reservationstatus", "StatusName", 8, _("Approved", l))
    sql += species(1, _("Dog", l), "Dog")
    sql += species(2, _("Cat", l), "Cat")
    sql += species(3, _("Bird", l), "Bird")
    sql += species(4, _("Mouse", l), "Small&Furry")
    sql += species(5, _("Rat", l), "Small&Furry")
    sql += species(6, _("Hedgehog", l), "Small&Furry")
    sql += species(7, _("Rabbit", l), "Rabbit")
    sql += species(8, _("Dove", l), "Bird")
    sql += species(9, _("Ferret", l), "Small&Furry")
    sql += species(10, _("Chinchilla", l), "Small&Furry")
    sql += species(11, _("Snake", l), "Reptile")
    sql += species(12, _("Tortoise", l), "Reptile")
    sql += species(13, _("Terrapin", l), "Reptile")
    sql += species(14, _("Chicken", l), "Barnyard")
    sql += species(15, _("Owl", l), "Bird")
    sql += species(16, _("Goat", l), "Barnyard")
    sql += species(17, _("Goose", l), "Bird")
    sql += species(18, _("Gerbil", l), "Small&Furry")
    sql += species(19, _("Cockatiel", l), "Bird")
    sql += species(20, _("Guinea Pig", l), "Small&Furry")
    sql += species(21, _("Goldfish", l), "Reptile")
    sql += species(22, _("Hamster", l), "Small&Furry")
    sql += species(23, _("Camel", l), "Horse")
    sql += species(24, _("Horse", l), "Horse")
    sql += species(25, _("Pony", l), "Horse")
    sql += species(26, _("Donkey", l), "Horse")
    sql += species(27, _("Llama", l), "Horse")
    sql += species(28, _("Pig", l), "Barnyard")
    sql += lookup2("stocklocation", "LocationName", 1, _("Stores", l))
    sql += lookup2("stockusagetype", "UsageTypeName", 1, _("Administered", l))
    sql += lookup2("stockusagetype", "UsageTypeName", 2, _("Consumed", l))
    sql += lookup2("stockusagetype", "UsageTypeName", 3, _("Donated", l))
    sql += lookup2("stockusagetype", "UsageTypeName", 4, _("Purchased", l))
    sql += lookup2("stockusagetype", "UsageTypeName", 5, _("Sold", l))
    sql += lookup2("stockusagetype", "UsageTypeName", 6, _("Stocktake", l))
    sql += lookup2("stockusagetype", "UsageTypeName", 7, _("Wasted", l))
    sql += lookup2("testresult", "ResultName", 1, _("Unknown", l))
    sql += lookup2("testresult", "ResultName", 2, _("Negative", l))
    sql += lookup2("testresult", "ResultName", 3, _("Positive", l))
    sql += lookup2money("testtype", "TestName", 1, _("FIV", l))
    sql += lookup2money("testtype", "TestName", 2, _("FLV", l))
    sql += lookup2money("testtype", "TestName", 3, _("Heartworm", l))
    sql += lookup2money("traptype", "TrapTypeName", 1, _("Cat", l))
    sql += lookup2money("voucher", "VoucherName", 1, _("Neuter/Spay", l))
    sql += lookup2money("vaccinationtype", "VaccinationType", 1, _("Distemper", l))
    sql += lookup2money("vaccinationtype", "VaccinationType", 2, _("Hepatitis", l))
    sql += lookup2money("vaccinationtype", "VaccinationType", 3, _("Leptospirosis", l))
    sql += lookup2money("vaccinationtype", "VaccinationType", 4, _("Rabies", l))
    sql += lookup2money("vaccinationtype", "VaccinationType", 5, _("Parainfluenza", l))
    sql += lookup2money("vaccinationtype", "VaccinationType", 6, _("Bordetella", l))
    sql += lookup2money("vaccinationtype", "VaccinationType", 7, _("Parvovirus", l))
    sql += lookup2money("vaccinationtype", "VaccinationType", 8, _("DHLPP", l))
    sql += lookup2money("vaccinationtype", "VaccinationType", 9, _("FVRCP", l))
    sql += lookup2money("vaccinationtype", "VaccinationType", 10, _("Chlamydophila", l))
    sql += lookup2money("vaccinationtype", "VaccinationType", 11, _("FIV", l))
    sql += lookup2money("vaccinationtype", "VaccinationType", 12, _("FeLV", l))
    sql += lookup2money("vaccinationtype", "VaccinationType", 13, _("FIPV", l))
    sql += lookup2money("vaccinationtype", "VaccinationType", 14, _("FECV/FeCoV", l))
    return sql

def install_db_structure(dbo):
    """
    Creates the db structure in the target database
    """
    al.info("creating default database schema", "dbupdate.install_default_data", dbo)
    sql = sql_structure(dbo)
    for s in sql.split(";"):
        if (s.strip() != ""):
            print s.strip()
            db.execute_dbupdate(dbo, s.strip())

def install_db_views(dbo):
    """
    Installs all the database views.
    """
    def create_view(viewname, sql):
        try:
            db.execute_dbupdate(dbo, "DROP VIEW IF EXISTS %s" % viewname)
            db.execute_dbupdate(dbo, "CREATE VIEW %s AS %s" % (viewname, sql))
        except Exception,err:
            al.error("error creating view %s: %s" % (viewname, err), "dbupdate.install_db_views", dbo)

    # Set us upto date to stop race condition/other clients trying
    # to install
    configuration.db_view_seq_version(dbo, BUILD)
    create_view("v_adoption", movement.get_movement_query(dbo))
    create_view("v_animal", animal.get_animal_query(dbo))
    create_view("v_animalcontrol", animalcontrol.get_animalcontrol_query(dbo))
    create_view("v_animalfound", lostfound.get_foundanimal_query(dbo))
    create_view("v_animallost", lostfound.get_lostanimal_query(dbo))
    create_view("v_animalmedicaltreatment", medical.get_medicaltreatment_query(dbo))
    create_view("v_animaltest", medical.get_test_query(dbo))
    create_view("v_animalvaccination", medical.get_vaccination_query(dbo))
    create_view("v_animalwaitinglist", waitinglist.get_waitinglist_query(dbo))
    create_view("v_owner", person.get_person_query(dbo))
    create_view("v_ownercitation", financial.get_citation_query(dbo))
    create_view("v_ownerdonation", financial.get_donation_query(dbo))
    create_view("v_ownerlicence", financial.get_licence_query(dbo))
    create_view("v_ownertraploan", animalcontrol.get_traploan_query(dbo))
    create_view("v_ownervoucher", financial.get_voucher_query(dbo))

def install_db_sequences(dbo):
    """
    Installs database sequences and sets their initial values
    (only valid for PostgreSQL and if DB_PK_STRATEGY is 'pseq' ).
    """
    if DB_PK_STRATEGY != "pseq" or dbo.dbtype != "POSTGRESQL": return
    for table in TABLES:
        if table in TABLES_NO_ID_COLUMN: continue
        initialvalue = db._get_id_max(dbo, table)
        db.execute_dbupdate(dbo, "DROP SEQUENCE IF EXISTS seq_%s" % table)
        db.execute_dbupdate(dbo, "CREATE SEQUENCE seq_%s START %d" % (table, initialvalue))

def install_db_stored_procedures(dbo):
    """
    Creates any special stored procedures we need in the target database
    """
    if dbo.dbtype == "POSTGRESQL":
        db.execute_dbupdate(dbo, \
            "CREATE OR REPLACE FUNCTION asm_to_date(p_date TEXT, p_format TEXT, OUT r_date DATE)\n" \
            "LANGUAGE plpgsql\n" \
            "AS $$\n" \
            "BEGIN\n" \
            "r_date = TO_DATE(p_date, p_format);\n" \
            "EXCEPTION\n" \
            "WHEN OTHERS THEN r_date = NULL;\n" \
            "END;\n" \
            "$$")
        db.execute_dbupdate(dbo, \
            "CREATE OR REPLACE FUNCTION asm_to_integer(p_int TEXT, OUT r_int INTEGER)\n" \
            "LANGUAGE plpgsql\n" \
            "AS $$\n" \
            "BEGIN\n" \
            "r_int = p_int::integer;\n" \
            "EXCEPTION\n" \
            "WHEN OTHERS THEN r_int = 0;\n" \
            "END;\n" \
            "$$")

def install_default_data(dbo, skip_config = False):
    """
    Installs the default dataset into the database.
    skip_config: If true, does not generate config data.
    """
    al.info("creating default data", "dbupdate.install_default_data", dbo)
    sql = sql_default_data(dbo, skip_config)
    for s in sql.split("|="):
        if s.strip() != "":
            print s.strip()
            db.execute_dbupdate(dbo, s.strip())

def reinstall_default_data(dbo):
    """
    Reinstalls all default data for the current locale. It wipes the
    database first, but leaves the configuration and dbfs tables intact.
    """
    for table in TABLES:
        if table != "dbfs" and table != "configuration" and table != "users" and table != "role" and table != "userrole":
            print "DELETE FROM %s" % table
            db.execute_dbupdate(dbo, "DELETE FROM %s" % table)
    install_default_data(dbo, True)

def install_default_onlineforms(dbo):
    """
    Installs the default online forms into the database
    """
    path = dbo.installpath + "media/onlineform/"
    al.info("creating default online forms", "dbupdate.install_default_onlineforms", dbo)
    for o in os.listdir(path):
        if o.endswith(".json"):
            try:
                onlineform.import_onlineform_json(dbo, utils.read_text_file(path + o))
            except Exception,err:
                al.error("error importing form: %s" % str(err), "dbupdate.install_default_onlineformms", dbo)

def install_default_media(dbo, removeFirst = False):
    """
    Installs the default media files into the dbfs
    """
    path = dbo.installpath
    if removeFirst:
        al.info("removing /internet, /templates and /report", "dbupdate.install_default_media", dbo)
        db.execute_dbupdate(dbo, "DELETE FROM dbfs WHERE Path Like '/internet%' OR Path Like '/report%' OR Path Like '/template%'")
    al.info("creating default media", "dbupdate.install_default_media", dbo)
    dbfs.create_path(dbo, "/", "internet")
    dbfs.create_path(dbo, "/internet", "animalview")
    dbfs.put_file(dbo, "body.html", "/internet/animalview", path + "media/internet/animalview/body.html")
    dbfs.put_file(dbo, "foot.html", "/internet/animalview", path + "media/internet/animalview/foot.html")
    dbfs.put_file(dbo, "head.html", "/internet/animalview", path + "media/internet/animalview/head.html")
    dbfs.create_path(dbo, "/internet", "littlebox")
    dbfs.put_file(dbo, "body.html", "/internet/littlebox", path + "media/internet/littlebox/body.html")
    dbfs.put_file(dbo, "foot.html", "/internet/littlebox", path + "media/internet/littlebox/foot.html")
    dbfs.put_file(dbo, "head.html", "/internet/littlebox", path + "media/internet/littlebox/head.html")
    dbfs.create_path(dbo, "/internet", "responsive")
    dbfs.put_file(dbo, "body.html", "/internet/responsive", path + "media/internet/responsive/body.html")
    dbfs.put_file(dbo, "foot.html", "/internet/responsive", path + "media/internet/responsive/foot.html")
    dbfs.put_file(dbo, "head.html", "/internet/responsive", path + "media/internet/responsive/head.html")
    dbfs.create_path(dbo, "/internet", "plain")
    dbfs.put_file(dbo, "body.html", "/internet/plain", path + "media/internet/plain/body.html")
    dbfs.put_file(dbo, "foot.html", "/internet/plain", path + "media/internet/plain/foot.html")
    dbfs.put_file(dbo, "head.html", "/internet/plain", path + "media/internet/plain/head.html")
    dbfs.put_file(dbo, "redirector.html", "/internet/plain", path + "media/internet/plain/redirector.html")
    dbfs.put_file(dbo, "search.html", "/internet/plain", path + "media/internet/plain/search.html")
    dbfs.create_path(dbo, "/internet", "rss")
    dbfs.put_file(dbo, "body.html", "/internet/rss", path + "media/internet/rss/body.html")
    dbfs.put_file(dbo, "foot.html", "/internet/rss", path + "media/internet/rss/foot.html")
    dbfs.put_file(dbo, "head.html", "/internet/rss", path + "media/internet/rss/head.html")
    dbfs.create_path(dbo, "/internet", "sm.com")
    dbfs.put_file(dbo, "body.html", "/internet/sm.com", path + "media/internet/sm.com/body.html")
    dbfs.put_file(dbo, "foot.html", "/internet/sm.com", path + "media/internet/sm.com/foot.html")
    dbfs.put_file(dbo, "head.html", "/internet/sm.com", path + "media/internet/sm.com/head.html")
    dbfs.put_file(dbo, "back1.png", "/internet/sm.com", path + "media/internet/sm.com/back1.png")
    dbfs.put_file(dbo, "cat_no.png", "/internet/sm.com", path + "media/internet/sm.com/cat_no.png")
    dbfs.put_file(dbo, "cat.png", "/internet/sm.com", path + "media/internet/sm.com/cat.png")
    dbfs.put_file(dbo, "dog_no.png", "/internet/sm.com", path + "media/internet/sm.com/dog_no.png")
    dbfs.put_file(dbo, "dog.png", "/internet/sm.com", path + "media/internet/sm.com/dog.png")
    dbfs.put_file(dbo, "housetrained.png", "/internet/sm.com", path + "media/internet/sm.com/housetrained.png")
    dbfs.put_file(dbo, "kids_no.png", "/internet/sm.com", path + "media/internet/sm.com/kids_no.png")
    dbfs.put_file(dbo, "kids.png", "/internet/sm.com", path + "media/internet/sm.com/kids.png")
    dbfs.put_file(dbo, "neutered.png", "/internet/sm.com", path + "media/internet/sm.com/neutered.png")
    dbfs.put_file(dbo, "new.png", "/internet/sm.com", path + "media/internet/sm.com/new.png")
    dbfs.put_file(dbo, "updated.png", "/internet/sm.com", path + "media/internet/sm.com/updated.png")
    dbfs.put_file(dbo, "vaccinated.png", "/internet/sm.com", path + "media/internet/sm.com/vaccinated.png")
    dbfs.create_path(dbo, "/", "reports")
    dbfs.put_file(dbo, "foot.html", "/reports", path + "media/reports/foot.html")
    dbfs.put_file(dbo, "head.html", "/reports", path + "media/reports/head.html")
    dbfs.put_file(dbo, "nopic.jpg", "/reports", path + "media/reports/nopic.jpg")
    dbfs.create_path(dbo, "/", "templates")
    dbfs.put_file(dbo, "adoption_form.html", "/templates", path + "media/templates/adoption_form.html")
    dbfs.put_file(dbo, "cat_assessment_form.html", "/templates", path + "media/templates/cat_assessment_form.html")
    dbfs.put_file(dbo, "cat_cage_card.html", "/templates", path + "media/templates/cat_cage_card.html")
    dbfs.put_file(dbo, "cat_information.html", "/templates", path + "media/templates/cat_information.html")
    dbfs.put_file(dbo, "dog_assessment_form.html", "/templates", path + "media/templates/dog_assessment_form.html")
    dbfs.put_file(dbo, "dog_cage_card.html", "/templates", path + "media/templates/dog_cage_card.html")
    dbfs.put_file(dbo, "dog_information.html", "/templates", path + "media/templates/dog_information.html")
    dbfs.put_file(dbo, "dog_license.html", "/templates", path + "media/templates/dog_license.html")
    dbfs.put_file(dbo, "fancy_cage_card.html", "/templates", path + "media/templates/fancy_cage_card.html")
    dbfs.put_file(dbo, "half_a4_cage_card.html", "/templates", path + "media/templates/half_a4_cage_card.html")
    dbfs.put_file(dbo, "homecheck_form.html", "/templates", path + "media/templates/homecheck_form.html")
    dbfs.put_file(dbo, "incident_information.html", "/templates", path + "media/templates/incident_information.html")
    dbfs.put_file(dbo, "invoice.html", "/templates", path + "media/templates/invoice.html")
    dbfs.put_file(dbo, "microchip_form.html", "/templates", path + "media/templates/microchip_form.html")
    dbfs.put_file(dbo, "petplan.html", "/templates", path + "media/templates/petplan.html")
    dbfs.put_file(dbo, "rabies_certificate.html", "/templates", path + "media/templates/rabies_certificate.html")
    dbfs.put_file(dbo, "receipt.html", "/templates", path + "media/templates/receipt.html")
    dbfs.put_file(dbo, "receipt_tax.html", "/templates", path + "media/templates/receipt_tax.html")
    dbfs.put_file(dbo, "reserved.html", "/templates", path + "media/templates/reserved.html")
    dbfs.create_path(dbo, "/templates", "rspca")
    dbfs.put_file(dbo, "rspca_adoption.html", "/templates/rspca", path + "media/templates/rspca/rspca_adoption.html")
    dbfs.put_file(dbo, "rspca_behaviour_observations_cat.html", "/templates/rspca", path + "media/templates/rspca/rspca_behaviour_observations_cat.html")
    dbfs.put_file(dbo, "rspca_behaviour_observations_dog.html", "/templates/rspca", path + "media/templates/rspca/rspca_behaviour_observations_dog.html")
    dbfs.put_file(dbo, "rspca_behaviour_observations_rabbit.html", "/templates/rspca", path + "media/templates/rspca/rspca_behaviour_observations_rabbit.html")
    dbfs.put_file(dbo, "rspca_dog_advice_leaflet.html", "/templates/rspca", path + "media/templates/rspca/rspca_dog_advice_leaflet.html")
    dbfs.put_file(dbo, "rspca_post_home_visit.html", "/templates/rspca", path + "media/templates/rspca/rspca_post_home_visit.html")
    dbfs.put_file(dbo, "rspca_transfer_of_ownership.html", "/templates/rspca", path + "media/templates/rspca/rspca_transfer_of_ownership.html")
    dbfs.put_file(dbo, "rspca_transfer_of_title.html", "/templates/rspca", path + "media/templates/rspca/rspca_transfer_of_title.html")

def install(dbo):
    """
    Handles the install of the database
    path: The path to the current directory containing the asm source
    """
    install_db_structure(dbo)
    install_db_views(dbo)
    install_default_data(dbo)
    install_db_sequences(dbo)
    install_db_stored_procedures(dbo)
    install_default_media(dbo)
    install_default_onlineforms(dbo)

def dump(dbo, includeConfig = True, includeDBFS = True, includeCustomReport = True, \
        includeNonASM2 = True, includeUsers = True, deleteDBV = False, deleteFirst = True, deleteViewSeq = False, \
        escapeCR = "", uppernames = False, wrapTransaction = True):
    """
    Dumps all of the data in the database as DELETE/INSERT statements.
    includeConfig - include the config table
    includeDBFS - include the dbfs table
    includeCustomReport - include the custom report table
    includeUsers - include user and role tables
    deleteDBV - issue DELETE DBV from config after dump to force update/checks
    deleteFirst - issue DELETE FROM statements before INSERTs
    deleteViewSeq - issue DELETE DBViewSeqVersion from config after dump
    escapeCR - A substitute for any \n characters found in values
    uppernames - upper case table names in the output
    wrapTransaction - wrap a transaction around the dump

    This is a generator function to save memory.
    """
    if wrapTransaction: yield "BEGIN;\n"
    for t in TABLES:
        if not includeDBFS and t == "dbfs": continue
        if not includeCustomReport and t == "customreport": continue
        if not includeConfig and t == "configuration": continue
        if not includeUsers and (t == "users" or t == "userrole" or t == "role" or t == "accountsrole" or t == "customreportrole"): continue
        # ASM2_COMPATIBILITY
        if not includeNonASM2 and t not in TABLES_ASM2 : continue
        outtable = t
        if uppernames: outtable = t.upper()
        if deleteFirst: 
            yield "DELETE FROM %s;\n" % outtable
        try:
            sys.stderr.write("dumping %s.., \n" % t)
            for x in db.query_to_insert_sql(dbo, "SELECT * FROM %s" % t, outtable, escapeCR):
                yield x
        except:
            em = str(sys.exc_info()[0])
            sys.stderr.write("%s: WARN: %s\n" % (t, em))
    if deleteViewSeq: yield "DELETE FROM configuration WHERE ItemName LIKE 'DBViewSeqVersion';\n"
    if deleteDBV: yield "DELETE FROM configuration WHERE ItemName LIKE 'DBV';\n"
    if wrapTransaction: yield "COMMIT;\n"

def dump_dbfs_stdout(dbo):
    """
    Dumps the DBFS table to stdout. For use with very large dbfs tables.
    """
    print "DELETE FROM dbfs;"
    rows = db.query(dbo, "SELECT ID, Name, Path FROM dbfs")
    for r in rows:
        content = db.query_string(dbo, "SELECT Content FROM dbfs WHERE ID=%d" % r["ID"])
        print "INSERT INTO dbfs (ID, Name, Path, Content) VALUES (%d, '%s', '%s', '%s');" % (r["ID"], r["NAME"], r["PATH"], content)
        del content

def dump_hsqldb(dbo, includeDBFS = True):
    """
    Produces a dump in hsqldb format for use with ASM2
    generator function.
    """
    # ASM2_COMPATIBILITY
    hdbo = db.DatabaseInfo()
    hdbo.dbtype = "HSQLDB"
    yield sql_structure(hdbo)
    for x in dump(dbo, includeNonASM2 = False, includeDBFS = includeDBFS, escapeCR = " ", wrapTransaction = False):
        yield x

def dump_smcom(dbo):
    """
    Dumps the database in a convenient format for import to sheltermanager.com
    generator function.
    """
    yield dump(dbo, includeConfig = False, includeUsers = False, deleteDBV = True, deleteViewSeq = True)

def dump_merge(dbo, deleteViewSeq = True):
    """
    Produces a special type of dump - it renumbers the IDs into a higher range 
    so that they can be inserted into another database.
    """
    ID_OFFSET = 100000
    s = []
    def fix_and_dump(table, fields):
        rows = db.query(dbo, "SELECT * FROM %s" % table)
        for r in rows:
            for f in fields:
                f = f.upper()
                if f == "ADOPTIONNUMBER" or f == "SHELTERCODE":
                    r[f] = "MG" + r[f]
                elif r[f] is not None:
                    r[f] += ID_OFFSET
        s.append(db.rows_to_insert_sql(table, rows, ""))
    fix_and_dump("adoption", [ "ID", "AnimalID", "AdoptionNumber", "OwnerID", "RetailerID", "OriginalRetailerMovementID" ])
    fix_and_dump("animal", [ "ID", "AnimalTypeID", "ShelterLocation", "ShelterCode", "BondedAnimalID", "BondedAnimal2ID", "OwnersVetID", "CurrentVetID", "OriginalOwnerID", "BroughtInByOwnerID", "ActiveMovementID" ])
    fix_and_dump("animalcontrol", [ "ID", "CallerID", "VictimID", "OwnerID", "Owner2ID", "Owner3ID", "AnimalID" ])
    fix_and_dump("animalcost", [ "ID", "AnimalID", "CostTypeID" ])
    fix_and_dump("costtype", [ "ID", ])
    fix_and_dump("animaldiet", [ "ID", "AnimalID" ])
    fix_and_dump("animalfound", [ "ID", "OwnerID" ])
    fix_and_dump("animallitter", [ "ID", "ParentAnimalID" ])
    fix_and_dump("animallost", [ "ID", "OwnerID" ])
    fix_and_dump("animalmedical", [ "ID", "AnimalID" ])
    fix_and_dump("animalmedicaltreatment", [ "ID", "AnimalID", "AnimalMedicalID" ])
    fix_and_dump("animaltest", [ "ID", "AnimalID", "TestTypeID", "TestResultID" ])
    fix_and_dump("animaltype", [ "ID", ])
    fix_and_dump("animaltransport", [ "ID", "AnimalID", "DriverOwnerID", "PickupOwnerID", "DropoffOwnerID" ])
    fix_and_dump("animalvaccination", [ "ID", "AnimalID", "VaccinationID" ])
    fix_and_dump("diary", [ "ID", "LinkID" ])
    fix_and_dump("internallocation", [ "ID", ])
    fix_and_dump("lkanimalflags", [ "ID", ])
    fix_and_dump("lkownerflags", [ "ID", ])
    fix_and_dump("log", [ "ID", "LinkID" ])
    fix_and_dump("owner", [ "ID", "HomeCheckedBy" ])
    fix_and_dump("ownercitation", [ "ID", "OwnerID", "AnimalControlID" ])
    fix_and_dump("ownerdonation", [ "ID", "AnimalID", "OwnerID", "MovementID", "DonationTypeID" ])
    fix_and_dump("donationtype", [ "ID", ])
    fix_and_dump("ownerinvestigation", [ "ID", "OwnerID" ])
    fix_and_dump("ownerlicence", [ "ID", "OwnerID", "AnimalID", "LicenceTypeID" ])
    fix_and_dump("licencetype", [ "ID", ])
    fix_and_dump("ownerrota", [ "ID", "OwnerID" ])
    fix_and_dump("ownertraploan", [ "ID", "OwnerID" ])
    fix_and_dump("ownervoucher", [ "ID", "OwnerID", "VoucherID" ])
    fix_and_dump("stocklevel", [ "ID", "StockLocationID" ])
    fix_and_dump("stocklocation", [ "ID", ])
    fix_and_dump("stockusage", [ "ID", "StockLevelID" ])
    fix_and_dump("testtype", [ "ID", ])
    fix_and_dump("testresult", [ "ID", ])
    fix_and_dump("vaccinationtype", [ "ID", ])
    fix_and_dump("voucher", [ "ID", ])
    if deleteViewSeq: s.append("DELETE FROM configuration WHERE ItemName LIKE 'DBViewSeqVersion';\n")
    return "".join(s)

def diagnostic(dbo):
    """
    1. Checks for and removes orphaned records (of some types)
    2. Checks for and fixes animal records with too many web or doc preferred images
    """
    def orphan(table, linktable, leftfield, rightfield):
        count = db.query_int(dbo, "SELECT COUNT(*) FROM %s LEFT OUTER JOIN %s ON %s = %s " \
            "WHERE %s Is Null" % (table, linktable, leftfield, rightfield, rightfield))
        if count > 0:
            db.execute_dbupdate(dbo, "DELETE FROM %s WHERE %s IN " \
                "(SELECT %s FROM %s LEFT OUTER JOIN %s ON %s = %s WHERE %s Is Null)" % (
                table, leftfield, leftfield, table, linktable, leftfield, rightfield, rightfield))
        return count

    def mediapref():
        duplicatepic = 0
        for a in db.query(dbo, "SELECT ID, " \
            "(SELECT COUNT(*) FROM media WHERE LinkID = animal.ID AND LinkTypeID = 0) AS TotalMedia, " \
            "(SELECT COUNT(*) FROM media WHERE LinkID = animal.ID AND LinkTypeID = 0 AND WebsitePhoto = 1) AS TotalWeb, " \
            "(SELECT COUNT(*) FROM media WHERE LinkID = animal.ID AND LinkTypeID = 0 AND DocPhoto = 1) AS TotalDoc, " \
            "(SELECT ID FROM media WHERE LinkID = animal.ID AND LinkTypeID = 0 AND MediaName LIKE '%.jpg' LIMIT 1) AS FirstImage " \
            "FROM animal"):
            if a["TOTALMEDIA"] > 0 and a["TOTALWEB"] > 1:
                # Too many web preferreds
                db.execute(dbo, "UPDATE media SET WebsitePhoto = 0 WHERE LinkID = %d AND LinkTypeID = 0 AND ID <> %d" % (a["ID"], a["FIRSTIMAGE"]))
                duplicatepic += 1
            if a["TOTALMEDIA"] > 0 and a["TOTALDOC"] > 1:
                # Too many doc preferreds
                db.execute(dbo, "UPDATE media SET DocPhoto = 0 WHERE LinkID = %d AND LinkTypeID = 0 AND ID <> %d" % (a["ID"], a["FIRSTIMAGE"]))
                duplicatepic += 1
        return duplicatepic

    return {
        "orphaned adoptions": orphan("adoption", "animal", "adoption.AnimalID", "animal.ID"),
        "orphaned found animals": orphan("animalfound", "owner", "animalfound.OwnerID", "owner.ID"),
        "orphaned lost animals": orphan("animallost", "owner", "animallost.OwnerID", "owner.ID"),
        "orphaned medical": orphan("animalmedical", "animal", "animalmedical.AnimalID", "animal.ID"),
        "orphaned payments": orphan("ownerdonation", "owner", "ownerdonation.OwnerID", "owner.ID"),
        "orphaned tests": orphan("animaltest", "animal", "animaltest.AnimalID", "animal.ID"),
        "orphaned treatments": orphan("animalmedicaltreatment", "animal", "animalmedicaltreatment.AnimalID", "animal.ID"),
        "orphaned vacc": orphan("animalvaccination", "animal", "animalvaccination.AnimalID", "animal.ID"),
        "orphaned waiting list animals": orphan("animalwaitinglist", "owner", "animalwaitinglist.OwnerID", "owner.ID"),
        "duplicate preferred images": mediapref()
    }

def check_for_updates(dbo):
    """
    Checks to see what version the database is on and whether or
    not it needs to be upgraded. Returns true if it needs
    upgrading.
    """
    dbv = int(configuration.dbv(dbo))
    return dbv < LATEST_VERSION

def check_for_view_seq_changes(dbo):
    """
    Checks to see whether we need to recreate our views and
    sequences by looking to see if BUILD is different. Returns 
    True if we need to update.
    """
    return configuration.db_view_seq_version(dbo) != BUILD

def reset_db(dbo):
    """
    Resets a database by removing all data from non-lookup tables.
    """
    deltables = [ "accountstrx", "additional", "adoption", "animal", "animalcontrol", "animalcost",
        "animaldiet", "animalfigures", "animalfiguresannual", "animalfiguresasilomar", "animalfiguresmonthlyasilomar",
        "animalfound", "animallitter", "animallost", "animalmedical", "animalmedicaltreatment", "animalname",
        "animaltest", "animaltransport", "animalvaccination", "animalwaitinglist", "diary", "log",
        "media", "messages", "onlineform", "onlineformfield", "onlineformincoming", "owner", "ownercitation",
        "ownerdonation", "ownerinvestigation", "ownerlicence", "ownertraploan", "ownervoucher", "stocklevel",
        "stockusage" ]
    for t in deltables:
        db.execute_dbupdate(dbo, "DELETE FROM %s" % t)
    db.execute_dbupdate(dbo, "DELETE FROM dbfs WHERE Path LIKE '/animal%' OR Path LIKE '/owner%'")
    install_db_sequences(dbo)

def perform_updates(dbo):
    """
    Performs any updates that need to be performed against the 
    database. Returns the new database version.
    """
    # Lock the database - fail silently if we couldn't lock it
    if not configuration.db_lock(dbo): return ""

    try:
        # Go through our updates to see if any need running
        ver = int(configuration.dbv(dbo))
        for v in VERSIONS:
            if ver < v:
                al.info("updating database to version %d" % v, "dbupdate.perform_updates", dbo)
                # Current db version is below this update, run it
                try:
                    globals()["update_" + str(v)](dbo)
                except:
                    al.error("DB Update Error: %s" % str(sys.exc_info()[0]), "dbupdate.perform_updates", dbo, sys.exc_info())
                # Update the version
                configuration.dbv(dbo, str(v))
                ver = v
        
        # Return the new db version
        configuration.db_unlock(dbo)
        return configuration.dbv(dbo)
    finally:
        # Unlock the database for updates before we leave
        configuration.db_unlock(dbo)

def floattype(dbo):
    if dbo.dbtype == "MYSQL":
        return "DOUBLE"
    else:
        return "REAL"

def datetype(dbo):
    if dbo.dbtype == "MYSQL": 
        return "DATETIME" 
    else:
        return "TIMESTAMP"

def longtext(dbo):
    if dbo.dbtype == "MYSQL":
        return "LONGTEXT"
    else:
        return "TEXT"

def shorttext(dbo):
    if dbo.dbtype == "MYSQL":
        return "VARCHAR(255)"
    else:
        return "VARCHAR(1024)"

def add_column(dbo, table, column, coltype):
    db.execute_dbupdate(dbo, "ALTER TABLE %s ADD %s %s" % (table, column, coltype))

def add_index(dbo, indexname, tablename, fieldname, unique = False):
    try:
        u = ""
        if unique: u = "UNIQUE "
        db.execute_dbupdate(dbo, "CREATE %sINDEX %s ON %s (%s)" % (u, indexname, tablename, fieldname))
    except:
        pass

def drop_column(dbo, table, column):
    cascade = ""
    if dbo.dbtype == "POSTGRESQL":
        cascade = " CASCADE"
    db.execute_dbupdate(dbo, "ALTER TABLE %s DROP COLUMN %s%s" % (table, column, cascade))

def modify_column(dbo, table, column, newtype, using =  ""):
    if dbo.dbtype == "MYSQL":
        db.execute_dbupdate(dbo, "ALTER TABLE %s MODIFY %s %s" % (table, column, newtype))
    elif dbo.dbtype == "POSTGRESQL":
        if using != "": using = " USING %s" % using # if cast is required to change type, eg: (colname::integer)
        db.execute_dbupdate(dbo, "ALTER TABLE %s ALTER %s TYPE %s%s" % (table, column, newtype, using))

def column_exists(dbo, table, column):
    """ Returns True if the column exists for the table given """
    try:
        db.query(dbo, "SELECT %s FROM %s LIMIT 1" % (column, table))
        return True
    except:
        return False

def remove_asm2_compatibility(dbo):
    """
    These are fields that we only include for compatibility with ASM2.
    ASM3 doesn't read or write to them any more.
    One day, when we have no more ASM2 users on sheltermanager.com,
    we will be able to remove these.
    """
    # ASM2_COMPATIBILITY
    db.execute_dbupdate(dbo, "ALTER TABLE users DROP COLUMN SecurityMap")
    db.execute_dbupdate(dbo, "ALTER TABLE animal DROP COLUMN SmartTagSentDate")
    db.execute_dbupdate(dbo, "ALTER TABLE media DROP COLUMN LastPublished")
    db.execute_dbupdate(dbo, "ALTER TABLE media DROP COLUMN LastPublishedPF")
    db.execute_dbupdate(dbo, "ALTER TABLE media DROP COLUMN LastPublishedAP")
    db.execute_dbupdate(dbo, "ALTER TABLE media DROP COLUMN LastPublishedP911")
    db.execute_dbupdate(dbo, "ALTER TABLE media DROP COLUMN LastPublishedRG")
    db.execute_dbupdate(dbo, "ALTER TABLE media DROP COLUMN NewSinceLastPublish")
    db.execute_dbupdate(dbo, "ALTER TABLE media DROP COLUMN UpdatedSinceLastPublish")

def update_3000(dbo):
    path = dbo.installpath
    dbfs.put_file(dbo, "adoption_form.html", "/templates", path + "media/templates/adoption_form.html")
    dbfs.put_file(dbo, "cat_assessment_form.html", "/templates", path + "media/templates/cat_assessment_form.html")
    dbfs.put_file(dbo, "cat_cage_card.html", "/templates", path + "media/templates/cat_cage_card.html")
    dbfs.put_file(dbo, "cat_information.html", "/templates", path + "media/templates/cat_information.html")
    dbfs.put_file(dbo, "dog_assessment_form.html", "/templates", path + "media/templates/dog_assessment_form.html")
    dbfs.put_file(dbo, "dog_cage_card.html", "/templates", path + "media/templates/dog_cage_card.html")
    dbfs.put_file(dbo, "dog_information.html", "/templates", path + "media/templates/dog_information.html")
    dbfs.put_file(dbo, "dog_license.html", "/templates", path + "media/templates/dog_license.html")
    dbfs.put_file(dbo, "fancy_cage_card.html", "/templates", path + "media/templates/fancy_cage_card.html")
    dbfs.put_file(dbo, "half_a4_cage_card.html", "/templates", path + "media/templates/half_a4_cage_card.html")
    dbfs.put_file(dbo, "homecheck_form.html", "/templates", path + "media/templates/homecheck_form.html")
    dbfs.put_file(dbo, "incident_information.html", "/templates", path + "media/templates/incident_information.html")
    dbfs.put_file(dbo, "invoice.html", "/templates", path + "media/templates/invoice.html")
    dbfs.put_file(dbo, "microchip_form.html", "/templates", path + "media/templates/microchip_form.html")
    dbfs.put_file(dbo, "petplan.html", "/templates", path + "media/templates/petplan.html")
    dbfs.put_file(dbo, "rabies_certificate.html", "/templates", path + "media/templates/rabies_certificate.html")
    dbfs.put_file(dbo, "receipt.html", "/templates", path + "media/templates/receipt.html")
    dbfs.put_file(dbo, "receipt_tax.html", "/templates", path + "media/templates/receipt_tax.html")
    dbfs.put_file(dbo, "reserved.html", "/templates", path + "media/templates/reserved.html")
    dbfs.create_path(dbo, "/templates", "rspca")
    dbfs.put_file(dbo, "rspca_adoption.html", "/templates/rspca", path + "media/templates/rspca/rspca_adoption.html")
    dbfs.put_file(dbo, "rspca_behaviour_observations_cat.html", "/templates/rspca", path + "media/templates/rspca/rspca_behaviour_observations_cat.html")
    dbfs.put_file(dbo, "rspca_behaviour_observations_dog.html", "/templates/rspca", path + "media/templates/rspca/rspca_behaviour_observations_dog.html")
    dbfs.put_file(dbo, "rspca_behaviour_observations_rabbit.html", "/templates/rspca", path + "media/templates/rspca/rspca_behaviour_observations_rabbit.html")
    dbfs.put_file(dbo, "rspca_dog_advice_leaflet.html", "/templates/rspca", path + "media/templates/rspca/rspca_dog_advice_leaflet.html")
    dbfs.put_file(dbo, "rspca_post_home_visit.html", "/templates/rspca", path + "media/templates/rspca/rspca_post_home_visit.html")
    dbfs.put_file(dbo, "rspca_transfer_of_ownership.html", "/templates/rspca", path + "media/templates/rspca/rspca_transfer_of_ownership.html")
    dbfs.put_file(dbo, "rspca_transfer_of_title.html", "/templates/rspca", path + "media/templates/rspca/rspca_transfer_of_title.html")
    if not dbfs.has_nopic(dbo):
        dbfs.put_file(dbo, "nopic.jpg", "/reports", path + "media/reports/nopic.jpg")
    db.execute_dbupdate(dbo, "CREATE TABLE messages ( ID INTEGER NOT NULL, Added %s NOT NULL, Expires %s NOT NULL, " \
        "CreatedBy %s NOT NULL, Priority INTEGER NOT NULL, Message %s NOT NULL )" % ( datetype(dbo), datetype(dbo), shorttext(dbo), longtext(dbo) ))
    db.execute_dbupdate(dbo, "CREATE UNIQUE INDEX messages_ID ON messages(ID)")
    add_index(dbo, "messages_Expires", "messages", "Expires")

def update_3001(dbo):
    db.execute_dbupdate(dbo, "DELETE FROM configuration WHERE ItemName LIKE 'MappingService%'")
    db.execute_dbupdate(dbo, "INSERT INTO configuration VALUES ('%s', '%s')" % ( "MappingServiceLinkURL", "http://maps.google.com/maps?q={0}" ))
    db.execute_dbupdate(dbo, "INSERT INTO configuration VALUES ('%s', '%s')" % ( "MappingServiceEmbeddedURL", "https://maps.googleapis.com/maps/api/staticmap?center={0}&size=250x250&maptype=roadmap&sensor=false"))
    if 0 == db.query_int(dbo, "SELECT COUNT(ItemName) FROM configuration WHERE ItemName LIKE 'SystemTheme'"):
        db.execute_dbupdate(dbo, "DELETE FROM configuration WHERE ItemName LIKE 'SystemTheme'")
        db.execute_dbupdate(dbo, "INSERT INTO configuration VALUES ('%s', '%s')" % ( "SystemTheme", "smoothness" ))
    if 0 == db.query_int(dbo, "SELECT COUNT(ItemName) FROM configuration WHERE ItemName LIKE 'Timezone'"):
        db.execute_dbupdate(dbo, "DELETE FROM configuration WHERE ItemName LIKE 'Timezone'")
        db.execute_dbupdate(dbo, "INSERT INTO configuration VALUES ('%s', '%s')" % ( "Timezone", "0" ))

def update_3002(dbo):
    add_column(dbo, "users", "IPRestriction", longtext(dbo))
    db.execute_dbupdate(dbo, "CREATE TABLE role (ID INTEGER NOT NULL PRIMARY KEY, " \
        "Rolename %s NOT NULL, SecurityMap %s NOT NULL)" % (shorttext(dbo), longtext(dbo)))
    add_index(dbo, "role_Rolename", "role", "Rolename")
    db.execute_dbupdate(dbo, "CREATE TABLE userrole (UserID INTEGER NOT NULL, " \
        "RoleID INTEGER NOT NULL)")
    add_index(dbo, "userrole_UserIDRoleID", "userrole", "UserID, RoleID")
    # Create default roles
    db.execute_dbupdate(dbo, "INSERT INTO role VALUES (1, 'Other Organisation', 'va *vavet *vav *mvam *dvad *cvad *vamv *vo *volk *vle *vvov *vdn *vla *vfa *vwl *vcr *vll *')")
    db.execute_dbupdate(dbo, "INSERT INTO role VALUES (2, 'Staff', 'aa *ca *va *vavet *da *cloa *gaf *aam *cam *dam *vam *mand *aav *vav *cav *dav *bcav *maam *mcam *mdam *mvam *bcam *daad *dcad *ddad *dvad *caad *cdad *cvad *aamv *camv *vamv *damv *ao *co *vo *do *mo *volk *ale *cle *dle *vle *vaov *vcov *vvov *oaod *ocod *odod *ovod *vdn *edt *adn *eadn *emdn *ecdn *bcn *ddn *pdn *pvd *ala *cla *dla *vla *afa *cfa *dfa *vfa *mlaf *vwl *awl *cwl *dwl *bcwl *all *cll *vll *dll *vcr *')")
    db.execute_dbupdate(dbo, "INSERT INTO role VALUES (3, 'Accountant', 'aac *vac *cac *ctrx *dac *vaov *vcov *vdov *vvov *oaod *ocod *odod *ovod *')")
    db.execute_dbupdate(dbo, "INSERT INTO role VALUES (4, 'Vet', 'va *vavet *aav *vav *cav *dav *bcav *maam *mcam *mdam *mvam *bcam *daad *dcad *ddad *dvad * ')")
    db.execute_dbupdate(dbo, "INSERT INTO role VALUES (5, 'Publisher', 'uipb *')")
    db.execute_dbupdate(dbo, "INSERT INTO role VALUES (6, 'System Admin', 'asm *cso *ml *usi *rdbu *rdbd *asu *esu *ccr *vcr *hcr *dcr *')")
    db.execute_dbupdate(dbo, "INSERT INTO role VALUES (7, 'Marketer', 'uipb *mmeo *mmea *')")
    db.execute_dbupdate(dbo, "INSERT INTO role VALUES (8, 'Investigator', 'aoi *coi *doi *voi *')")
    # Find any existing users that aren't superusers and create a
    # matching role for them
    users = db.query(dbo, "SELECT ID, UserName, SecurityMap FROM users " \
        "WHERE SuperUser = 0")
    for u in users:
        roleid = db._get_id_max(dbo, "role") 
        # If it's the guest user, use the view animals/people role
        if u["USERNAME"] == "guest":
            roleid = 1
        else:
            db.execute_dbupdate(dbo, "INSERT INTO role VALUES (%d, '%s', '%s')" % \
                ( roleid, u["USERNAME"], u["SECURITYMAP"]))
        db.execute_dbupdate(dbo, "INSERT INTO userrole VALUES (%d, %d)" % \
            ( u["ID"], roleid))

def update_3003(dbo):
    # Extend the length of configuration items
    modify_column(dbo, "configuration", "ItemValue", longtext(dbo))
        
def update_3004(dbo):
    unused = dbo
    # Broken, disregard.

def update_3005(dbo):
    # 3004 was broken and deleted the mapping service by accident, so we reinstate it
    db.execute_dbupdate(dbo, "DELETE FROM configuration WHERE ItemName LIKE 'MappingService%'")
    db.execute_dbupdate(dbo, "INSERT INTO configuration VALUES ('%s', '%s')" % ( "MappingServiceLinkURL", "http://maps.google.com/maps?q={0}" ))
    db.execute_dbupdate(dbo, "INSERT INTO configuration VALUES ('%s', '%s')" % ( "MappingServiceEmbeddedURL", "https://maps.googleapis.com/maps/api/staticmap?center={0}&size=250x250&maptype=roadmap&sensor=false"))
    # Set default search sort to last changed/relevance
    db.execute_dbupdate(dbo, "DELETE FROM configuration WHERE ItemName LIKE 'RecordSearchLimit' OR ItemName Like 'SearchSort'")
    db.execute_dbupdate(dbo, "INSERT INTO configuration VALUES ('%s', '%s')" % ( "RecordSearchLimit", "1000" ))
    db.execute_dbupdate(dbo, "INSERT INTO configuration VALUES ('%s', '%s')" % ( "SearchSort", "3" ))

def update_3006(dbo):
    # Add ForName field to messages
    add_column(dbo, "messages", "ForName", shorttext(dbo))
    db.execute_dbupdate(dbo, "UPDATE messages SET ForName = '*'")

def update_3007(dbo):
    # Add default quicklinks
    db.execute_dbupdate(dbo, "DELETE FROM configuration WHERE ItemName Like 'QuicklinksID'")
    db.execute_dbupdate(dbo, "INSERT INTO configuration VALUES ('%s', '%s')" % ( "QuicklinksID", "35,25,33,31,34,19,20"))

def update_3008(dbo):
    # Add facility for users to override the system locale
    add_column(dbo, "users", "LocaleOverride", shorttext(dbo))

def update_3009(dbo):
    # Create animalfigures table to be updated each night
    sql = "CREATE TABLE animalfigures ( ID INTEGER NOT NULL, " \
        "Month INTEGER NOT NULL, " \
        "Year INTEGER NOT NULL, " \
        "OrderIndex INTEGER NOT NULL, " \
        "Code %s NOT NULL, " \
        "AnimalTypeID INTEGER NOT NULL, " \
        "SpeciesID INTEGER NOT NULL, " \
        "MaxDaysInMonth INTEGER NOT NULL, " \
        "Heading %s NOT NULL, " \
        "Bold INTEGER NOT NULL, " \
        "D1 INTEGER NOT NULL, " \
        "D2 INTEGER NOT NULL, " \
        "D3 INTEGER NOT NULL, " \
        "D4 INTEGER NOT NULL, " \
        "D5 INTEGER NOT NULL, " \
        "D6 INTEGER NOT NULL, " \
        "D7 INTEGER NOT NULL, " \
        "D8 INTEGER NOT NULL, " \
        "D9 INTEGER NOT NULL, " \
        "D10 INTEGER NOT NULL, " \
        "D11 INTEGER NOT NULL, " \
        "D12 INTEGER NOT NULL, " \
        "D13 INTEGER NOT NULL, " \
        "D14 INTEGER NOT NULL, " \
        "D15 INTEGER NOT NULL, " \
        "D16 INTEGER NOT NULL, " \
        "D17 INTEGER NOT NULL, " \
        "D18 INTEGER NOT NULL, " \
        "D19 INTEGER NOT NULL, " \
        "D20 INTEGER NOT NULL, " \
        "D21 INTEGER NOT NULL, " \
        "D22 INTEGER NOT NULL, " \
        "D23 INTEGER NOT NULL, " \
        "D24 INTEGER NOT NULL, " \
        "D25 INTEGER NOT NULL, " \
        "D26 INTEGER NOT NULL, " \
        "D27 INTEGER NOT NULL, " \
        "D28 INTEGER NOT NULL, " \
        "D29 INTEGER NOT NULL, " \
        "D30 INTEGER NOT NULL, " \
        "D31 INTEGER NOT NULL, " \
        "AVG %s NOT NULL)" % (shorttext(dbo), shorttext(dbo), floattype(dbo))
    db.execute_dbupdate(dbo, sql)
    db.execute_dbupdate(dbo, "CREATE UNIQUE INDEX animalfigures_ID ON animalfigures(ID)")
    add_index(dbo, "animalfigures_AnimalTypeID", "animalfigures", "AnimalTypeID")
    add_index(dbo, "animalfigures_SpeciesID", "animalfigures", "SpeciesID")
    add_index(dbo, "animalfigures_Month", "animalfigures", "Month")
    add_index(dbo, "animalfigures_Year", "animalfigures", "Year")

def update_3010(dbo):
    # Create person flags table
    sql = "CREATE TABLE lkownerflags ( ID INTEGER NOT NULL, " \
        "Flag %s NOT NULL)" % shorttext(dbo)
    db.execute_dbupdate(dbo, sql)
    # Add additionalflags field to person
    add_column(dbo, "owner", "AdditionalFlags", longtext(dbo))

def update_3050(dbo):
    # Add default cost for vaccinations
    add_column(dbo, "vaccinationtype", "DefaultCost", "INTEGER")
    # Add default adoption fee per species
    add_column(dbo, "species", "AdoptionFee", "INTEGER")

def update_3051(dbo):
    # Fix incorrect field name from ASM3 initial install (it was listed
    # as TimingRuleNoFrequency instead of TimingRuleFrequency)
    add_column(dbo, "medicalprofile", "TimingRuleFrequency", "INTEGER")
    drop_column(dbo, "medicalprofile", "TimingRuleNoFrequency")

def update_3081(dbo):
    # Remove AdoptionFee field - it was a stupid idea to have with species
    # put a defaultcost on donation type instead
    drop_column(dbo, "species", "AdoptionFee")
    add_column(dbo, "donationtype", "DefaultCost", "INTEGER")

def update_3091(dbo):
    # Reinstated map url in 3005 did not use SSL for embedded link
    db.execute_dbupdate(dbo, "DELETE FROM configuration WHERE ItemName LIKE 'MappingService%'")
    db.execute_dbupdate(dbo, "INSERT INTO configuration VALUES ('%s', '%s')" % ( "MappingServiceLinkURL", "http://maps.google.com/maps?q={0}" ))
    db.execute_dbupdate(dbo, "INSERT INTO configuration VALUES ('%s', '%s')" % ( "MappingServiceEmbeddedURL", "https://maps.googleapis.com/maps/api/staticmap?center={0}&size=250x250&maptype=roadmap&sensor=false"))
    # Add ExcludeFromPublish field to media
    add_column(dbo, "media", "ExcludeFromPublish", "INTEGER")
    db.execute_dbupdate(dbo, "UPDATE media SET ExcludeFromPublish = 0")

def update_3092(dbo):
    # Added last publish date for meetapet.com
    add_column(dbo, "media", "LastPublishedMP", datetype(dbo))

def update_3093(dbo):
    # Create animalfiguresannual table to be updated each night
    sql = "CREATE TABLE animalfiguresannual ( ID INTEGER NOT NULL, " \
        "Year INTEGER NOT NULL, " \
        "OrderIndex INTEGER NOT NULL, " \
        "Code %s NOT NULL, " \
        "AnimalTypeID INTEGER NOT NULL, " \
        "SpeciesID INTEGER NOT NULL, " \
        "GroupHeading %s NOT NULL, " \
        "Heading %s NOT NULL, " \
        "Bold INTEGER NOT NULL, " \
        "M1 INTEGER NOT NULL, " \
        "M2 INTEGER NOT NULL, " \
        "M3 INTEGER NOT NULL, " \
        "M4 INTEGER NOT NULL, " \
        "M5 INTEGER NOT NULL, " \
        "M6 INTEGER NOT NULL, " \
        "M7 INTEGER NOT NULL, " \
        "M8 INTEGER NOT NULL, " \
        "M9 INTEGER NOT NULL, " \
        "M10 INTEGER NOT NULL, " \
        "M11 INTEGER NOT NULL, " \
        "M12 INTEGER NOT NULL, " \
        "Total INTEGER NOT NULL)" % (shorttext(dbo), shorttext(dbo), shorttext(dbo))
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "animalfiguresannual_ID", "animalfiguresannual", "ID", True)
    add_index(dbo, "animalfiguresannual_AnimalTypeID", "animalfiguresannual", "AnimalTypeID")
    add_index(dbo, "animalfiguresannual_SpeciesID", "animalfiguresannual", "SpeciesID")
    add_index(dbo, "animalfiguresannual_Year", "animalfiguresannual", "Year")

def update_3094(dbo):
    # Added last publish date for helpinglostpets.com
    add_column(dbo, "media", "LastPublishedHLP", datetype(dbo))

def update_3110(dbo):
    # Add PetLinkSentDate
    add_column(dbo, "animal", "PetLinkSentDate", datetype(dbo))

def update_3111(dbo):
    l = dbo.locale
    # New additional field types to indicate location
    db.execute_dbupdate(dbo, "UPDATE lksfieldlink SET LinkType = '%s' WHERE ID = 0" % _("Animal - Additional", l))
    db.execute_dbupdate(dbo, "UPDATE lksfieldlink SET LinkType = '%s' WHERE ID = 1" % _("Person - Additional", l))
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink VALUES (2, '%s')" % _("Animal - Details", l))
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink VALUES (3, '%s')" % _("Animal - Notes", l))
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink VALUES (4, '%s')" % _("Animal - Entry", l))
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink VALUES (5, '%s')" % _("Animal - Health and Identification", l))
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink VALUES (6, '%s')" % _("Animal - Death", l))
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink VALUES (7, '%s')" % _("Person - Name and Address", l))
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink VALUES (8, '%s')" % _("Person - Type", l))

def update_3120(dbo):
    # This stuff only applies to MySQL databases - we have to import a lot of these
    # and if they were created by ASM3 they don't quite match our 2870 upgrade schemas
    # as I accidentally had createdby/lastchangedby fields in 3 tables that shouldn't
    # have been there and there was a typo in the lastpublishedp911 field (missing the p)
    if dbo.dbtype != "MYSQL": 
        return
    if column_exists(dbo, "diarytaskdetail", "createdby"):
        drop_column(dbo, "diarytaskdetail", "createdby")
        drop_column(dbo, "diarytaskdetail", "createddate")
        drop_column(dbo, "diarytaskdetail", "lastchangedby")
        drop_column(dbo, "diarytaskdetail", "lastchangeddate")
    if column_exists(dbo, "diarytaskhead", "createdby"):
        drop_column(dbo, "diarytaskhead", "createdby")
        drop_column(dbo, "diarytaskhead", "createddate")
        drop_column(dbo, "diarytaskhead", "lastchangedby")
        drop_column(dbo, "diarytaskhead", "lastchangeddate")
    if column_exists(dbo, "media", "createdby"):
        drop_column(dbo, "media", "createdby")
        drop_column(dbo, "media", "createddate")
        drop_column(dbo, "media", "lastchangedby")
        drop_column(dbo, "media", "lastchangeddate")
    if column_exists(dbo, "media", "lastpublished911"):
        db.execute_dbupdate(dbo, "ALTER TABLE media CHANGE COLUMN lastpublished911 lastpublishedp911 DATETIME")

def update_3121(dbo):
    # Added user email address
    add_column(dbo, "users", "EmailAddress", shorttext(dbo))

def update_3122(dbo):
    # Switch shelter animals quicklink for shelter view
    # This will fail on locked databases, but shouldn't be an issue.
    links = configuration.quicklinks_id(dbo)
    links = links.replace("35", "40")
    configuration.quicklinks_id(dbo, links)

def update_3123(dbo):
    # Add the monthly animal figures total column
    add_column(dbo, "animalfigures", "Total", shorttext(dbo))

def update_3200(dbo):
    # Add the trial adoption fields to the adoption table
    add_column(dbo, "adoption", "IsTrial", "INTEGER")
    add_column(dbo, "adoption", "TrialEndDate", datetype(dbo))
    add_index(dbo, "adoption_TrialEndDate", "adoption", "TrialEndDate")

def update_3201(dbo):
    # Add the has trial adoption denormalised field to the animal table and update it
    add_column(dbo, "animal", "HasTrialAdoption", "INTEGER")
    db.execute_dbupdate(dbo, "UPDATE animal SET HasTrialAdoption = 0")
    db.execute_dbupdate(dbo, "UPDATE adoption SET IsTrial = 0 WHERE IsTrial Is Null")

def update_3202(dbo):
    # Set default value for HasTrialAdoption
    db.execute_dbupdate(dbo, "UPDATE animal SET HasTrialAdoption = 1 WHERE EXISTS(SELECT ID FROM adoption ad WHERE ad.IsTrial = 1 AND ad.AnimalID = animal.ID)")

def update_3203(dbo):
    l = dbo.locale
    # Add Trial Adoption movement type
    db.execute_dbupdate(dbo, "INSERT INTO lksmovementtype (ID, MovementType) VALUES (11, %s)" % db.ds(_("Trial Adoption", l)))

def update_3204(dbo):
    # Quicklinks format has changed, regenerate them
    links = configuration.quicklinks_id(dbo)
    configuration.quicklinks_id(dbo, links)

def update_3210(dbo):
    # Anyone using MySQL who created their database with the db
    # initialiser here will have some short columns as CLOB
    # wasn't mapped properly
    if dbo.dbtype == "MYSQL":
        db.execute_dbupdate(dbo, "ALTER TABLE dbfs MODIFY Content LONGTEXT")
        db.execute_dbupdate(dbo, "ALTER TABLE media MODIFY MediaNotes LONGTEXT NOT NULL")
        db.execute_dbupdate(dbo, "ALTER TABLE log MODIFY Comments LONGTEXT NOT NULL")

def update_3211(dbo):
    # People who upgraded from ASM2 will find that some of their address fields
    # are a bit short - particularly if they are using unicode chars
    fields = [ "OwnerTitle", "OwnerInitials", "OwnerForeNames", "OwnerSurname", 
        "OwnerName", "OwnerAddress", "OwnerTown", "OwnerCounty", "OwnerPostcode", 
        "HomeTelephone", "WorkTelephone", "MobileTelephone", "EmailAddress" ]
    for f in fields:
        if dbo.dbtype == "MYSQL":
            db.execute_dbupdate(dbo, "ALTER TABLE owner MODIFY %s %s NOT NULL" % (f, shorttext(dbo)))
        elif dbo.dbtype == "POSTGRESQL":
            db.execute_dbupdate(dbo, "ALTER TABLE owner ALTER %s TYPE %s" % (f, shorttext(dbo)))

def update_3212(dbo):
    # Many of our lookup fields are too short for foreign languages
    fields = [ "animaltype.AnimalType", "animaltype.AnimalDescription", "basecolour.BaseColour", "basecolour.BaseColourDescription",
        "breed.BreedName", "breed.BreedDescription", "lkcoattype.CoatType", "costtype.CostTypeName", "costtype.CostTypeDescription",
        "deathreason.ReasonName", "deathreason.ReasonDescription", "diet.DietName", "diet.DietDescription", 
        "donationtype.DonationName", "donationtype.DonationDescription", "entryreason.ReasonName", "entryreason.ReasonDescription",
        "internallocation.LocationName", "internallocation.LocationDescription", "logtype.LogTypeName", "logtype.LogTypeDescription",
        "lksmovementtype.MovementType",  "lkownerflags.Flag", "lksex.Sex", "lksize.Size", "lksyesno.Name", "lksynun.Name", 
        "lksposneg.Name", "species.SpeciesName", "species.SpeciesDescription", "lkurgency.Urgency", 
        "vaccinationtype.VaccinationType", "vaccinationtype.VaccinationDescription", "voucher.VoucherName", "voucher.VoucherDescription",
        "accounts.Code", "accounts.Description", "accountstrx.Description",
        "animal.TimeOnShelter", "animal.AnimalAge", "animalfigures.Heading", "animalfiguresannual.Heading", 
        "animalfiguresannual.GroupHeading", "animalwaitinglist.AnimalDescription",
        "animalmedical.TreatmentName", "animalmedical.Dosage", "diary.Subject", "diary.LinkInfo",
        "medicalprofile.TreatmentName", "medicalprofile.Dosage", "medicalprofile.ProfileName" ]
    for f in fields:
        table, field = f.split(".")
        try:
            modify_column(dbo, table, field, shorttext(dbo))
        except Exception,err:
            al.error("failed extending %s: %s" % (f, str(err)), "dbupdate.update_3212", dbo)

def update_3213(dbo):
    try:
        # Make displaylocationname and displaylocationstring denormalised fields
        db.execute_dbupdate(dbo, "ALTER TABLE animal ADD DisplayLocationName %s" % shorttext(dbo))
        db.execute_dbupdate(dbo, "ALTER TABLE animal ADD DisplayLocationString %s" % shorttext(dbo))
    except Exception,err:
        al.error("failed creating animal.DisplayLocationName/String: %s" % str(err), "dbupdate.update_3213", dbo)

    # Default the values for them
    db.execute_dbupdate(dbo, "UPDATE animal SET DisplayLocationName = " \
        "CASE " \
        "WHEN animal.Archived = 0 AND animal.ActiveMovementType = 2 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=animal.ActiveMovementType) " \
        "WHEN animal.Archived = 0 AND animal.ActiveMovementType = 1 AND animal.HasTrialAdoption = 1 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=11) " \
        "WHEN animal.Archived = 1 AND animal.DeceasedDate Is Not Null AND animal.ActiveMovementID = 0 THEN " \
        "(SELECT ReasonName FROM deathreason WHERE ID = animal.PTSReasonID) " \
        "WHEN animal.Archived = 1 AND animal.DeceasedDate Is Not Null AND animal.ActiveMovementID <> 0 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=animal.ActiveMovementType) " \
        "WHEN animal.Archived = 1 AND animal.DeceasedDate Is Null AND animal.ActiveMovementID <> 0 THEN " \
        "(SELECT MovementType FROM lksmovementtype WHERE ID=animal.ActiveMovementType) " \
        "ELSE " \
        "(SELECT LocationName FROM internallocation WHERE ID=animal.ShelterLocation) " \
        "END")
    db.execute_dbupdate(dbo, "UPDATE animal SET DisplayLocationString = DisplayLocationName")

def update_3214(dbo):
    # More short fields
    fields = [ "diarytaskhead.Name", "diarytaskdetail.Subject", "diarytaskdetail.WhoFor", "lksdonationfreq.Frequency",
        "lksloglink.LinkType", "lksdiarylink.LinkType", "lksfieldlink.LinkType", "lksfieldtype.FieldType",
        "lksmedialink.LinkType", "lksdiarylink.LinkType" ]
    for f in fields:
        table, field = f.split(".")
        try:
            if dbo.dbtype == "MYSQL":
                db.execute_dbupdate(dbo, "ALTER TABLE %s MODIFY %s %s NOT NULL" % (table, field, shorttext(dbo)))
            elif dbo.dbtype == "POSTGRESQL":
                db.execute_dbupdate(dbo, "ALTER TABLE %s ALTER %s TYPE %s" % (table, field, shorttext(dbo)))
        except Exception,err:
            al.error("failed extending %s: %s" % (f, str(err)), "dbupdate.update_3214", dbo)

def update_3215(dbo):
    # Rename DisplayLocationString column to just DisplayLocation and ditch DisplayLocationName - it should be calculated
    try:
        db.execute_dbupdate(dbo, "ALTER TABLE animal ADD DisplayLocation %s" % shorttext(dbo))
    except:
        al.error("failed creating animal.DisplayLocation.", "dbupdate.update_3215", dbo)
    try:
        db.execute_dbupdate(dbo, "UPDATE animal SET DisplayLocation = DisplayLocationString")
    except:
        al.error("failed copying DisplayLocationString->DisplayLocation", "dbupdate.update_3215", dbo)
    try:
        db.execute_dbupdate(dbo, "ALTER TABLE animal DROP COLUMN DisplayLocationName")
        db.execute_dbupdate(dbo, "ALTER TABLE animal DROP COLUMN DisplayLocationString")
    except:
        al.error("failed removing DisplayLocationName and DisplayLocationString", "dbupdate.update_3215", dbo)

def update_3216(dbo):
    l = dbo.locale
    # Add the new mediatype field to media and create the link table
    db.execute_dbupdate(dbo, "ALTER TABLE media ADD MediaType INTEGER")
    db.execute_dbupdate(dbo, "ALTER TABLE media ADD WebsiteVideo INTEGER")
    db.execute_dbupdate(dbo, "UPDATE media SET MediaType = 0, WebsiteVideo = 0")
    db.execute_dbupdate(dbo, "CREATE TABLE lksmediatype ( ID INTEGER NOT NULL, MediaType %s NOT NULL )" % ( shorttext(dbo)))
    db.execute_dbupdate(dbo, "CREATE UNIQUE INDEX lksmediatype_ID ON lksmediatype(ID)")
    db.execute_dbupdate(dbo, "INSERT INTO lksmediatype (ID, MediaType) VALUES (%d, '%s')" % (0, _("File", l)))
    db.execute_dbupdate(dbo, "INSERT INTO lksmediatype (ID, MediaType) VALUES (%d, '%s')" % (1, _("Document Link", l)))
    db.execute_dbupdate(dbo, "INSERT INTO lksmediatype (ID, MediaType) VALUES (%d, '%s')" % (2, _("Video Link", l)))

def update_3217(dbo):
    # Add asilomar fields for US users
    db.execute_dbupdate(dbo, "ALTER TABLE animal ADD AsilomarIsTransferExternal INTEGER")
    db.execute_dbupdate(dbo, "ALTER TABLE animal ADD AsilomarIntakeCategory INTEGER")
    db.execute_dbupdate(dbo, "ALTER TABLE animal ADD AsilomarOwnerRequestedEuthanasia INTEGER")
    db.execute_dbupdate(dbo, "UPDATE animal SET AsilomarIsTransferExternal = 0, AsilomarIntakeCategory = 0, AsilomarOwnerRequestedEuthanasia = 0")

def update_3220(dbo):
    # Create animalfiguresasilomar table to be updated each night
    # for US shelters with the option on
    sql = "CREATE TABLE animalfiguresasilomar ( ID INTEGER NOT NULL, " \
        "Year INTEGER NOT NULL, " \
        "OrderIndex INTEGER NOT NULL, " \
        "Code %s NOT NULL, " \
        "Heading %s NOT NULL, " \
        "Bold INTEGER NOT NULL, " \
        "Cat INTEGER NOT NULL, " \
        "Dog INTEGER NOT NULL, " \
        "Total INTEGER NOT NULL)" % (shorttext(dbo), shorttext(dbo))
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "animalfiguresasilomar_ID", "animalfiguresasilomar", "ID", True)
    add_index(dbo, "animalfiguresasilomar_Year", "animalfiguresasilomar", "Year")

def update_3221(dbo):
    # More short fields
    fields = [ "activeuser.UserName", "customreport.Title", "customreport.Category" ]
    for f in fields:
        table, field = f.split(".")
        try:
            if dbo.dbtype == "MYSQL":
                db.execute_dbupdate(dbo, "ALTER TABLE %s MODIFY %s %s NOT NULL" % (table, field, shorttext(dbo)))
            elif dbo.dbtype == "POSTGRESQL":
                db.execute_dbupdate(dbo, "ALTER TABLE %s ALTER %s TYPE %s" % (table, field, shorttext(dbo)))
        except Exception,err:
            al.error("failed extending %s: %s" % (f, str(err)), "dbupdate.update_3221", dbo)

def update_3222(dbo):
    # Person investigation table
    db.execute_dbupdate(dbo, "CREATE TABLE ownerinvestigation ( ID INTEGER NOT NULL, " \
        "OwnerID INTEGER NOT NULL, Date %s NOT NULL, Notes %s NOT NULL, " \
        "RecordVersion INTEGER, CreatedBy %s, CreatedDate %s, " \
        "LastChangedBy %s, LastChangedDate %s)" % \
        (datetype(dbo), longtext(dbo), shorttext(dbo), datetype(dbo), shorttext(dbo), datetype(dbo)))
    add_index(dbo, "ownerinvestigation_ID", "ownerinvestigation", "ID", True)
    add_index(dbo, "ownerinvestigation_Date", "ownerinvestigation", "Date")

def update_3223(dbo):
    # PostgreSQL databases have been using VARCHAR(16384) as longtext when
    # they really shouldn't. Let's switch those fields to be TEXT instead.
    if dbo.dbtype != "POSTGRESQL": return
    fields = [ "activeuser.Messages", "additionalfield.LookupValues", "additional.Value", "adoption.ReasonForReturn", "adoption.Comments", "animal.Markings", "animal.HiddenAnimalDetails", "animal.AnimalComments", "animal.ReasonForEntry", "animal.ReasonNO", "animal.HealthProblems", "animal.PTSReason", "animalcost.Description", "animal.AnimalComments", "animalfound.DistFeat", "animalfound.Comments", "animallitter.Comments", "animallost.DistFeat", "animallost.Comments", "animalmedical.Comments", "animalmedicaltreatment.Comments", "animalvaccination.Comments", "animalwaitinglist.ReasonForWantingToPart", "animalwaitinglist.ReasonForRemoval", "animalwaitinglist.Comments", "audittrail.Description", "customreport.Description", "diary.Subject", "diary.Note", "diarytaskdetail.Subject", "diarytaskdetail.Note", "log.Comments", "media.MediaNotes", "medicalprofile.Comments", "messages.Message", "owner.Comments", "owner.AdditionalFlags", "owner.HomeCheckAreas", "ownerdonation.Comments", "ownerinvestigation.Notes", "ownervoucher.Comments", "role.SecurityMap", "users.SecurityMap", "users.IPRestriction", "configuration.ItemValue", "customreport.SQLCommand", "customreport.HTMLBody" ]
    for f in fields:
        table, field = f.split(".")
        try:
            db.execute_dbupdate(dbo, "ALTER TABLE %s ALTER %s TYPE %s" % (table, field, longtext(dbo)))
        except Exception,err:
            al.error("failed switching to TEXT %s: %s" % (f, str(err)), "dbupdate.update_3223", dbo)

def update_3224(dbo):
    # AVG is a reserved keyword in some SQL dialects, change that field
    try:
        if dbo.dbtype == "MYSQL":
            db.execute_dbupdate(dbo, "ALTER TABLE animalfigures CHANGE AVG AVERAGE %s NOT NULL" % floattype(dbo))
        elif dbo.dbtype == "POSTGRESQL":
            db.execute_dbupdate(dbo, "ALTER TABLE animalfigures RENAME COLUMN AVG TO AVERAGE")
        elif dbo.dbtype == "SQLITE":
            db.execute_dbupdate(dbo, "ALTER TABLE animalfigures ADD AVERAGE %s" % floattype(dbo))
    except Exception,err:
        al.error("failed renaming AVG to AVERAGE: %s" % str(err), "dbupdate.update_3224", dbo)

def update_3225(dbo):
    # Make sure the ADOPTIONFEE mistake is really gone
    db.execute_dbupdate(dbo, "ALTER TABLE species DROP COLUMN AdoptionFee")

def update_3300(dbo):
    # Add diary comments field
    add_column(dbo, "diary", "Comments", longtext(dbo))

def update_3301(dbo):
    # Add the accountsrole table
    db.execute_dbupdate(dbo, "CREATE TABLE accountsrole (AccountID INTEGER NOT NULL, " \
        "RoleID INTEGER NOT NULL, CanView INTEGER NOT NULL, CanEdit INTEGER NOT NULL)")
    db.execute_dbupdate(dbo, "CREATE UNIQUE INDEX accountsrole_AccountIDRoleID ON accountsrole(AccountID, RoleID)")

def update_3302(dbo):
    # Add default cost fields to costtype and voucher
    add_column(dbo, "costtype", "DefaultCost", "INTEGER")
    add_column(dbo, "voucher", "DefaultCost", "INTEGER")

def update_3303(dbo):
    # Add theme override to users
    add_column(dbo, "users", "ThemeOverride", shorttext(dbo))

def update_3304(dbo):
    # Add index to configuration ItemName field
    add_index(dbo, "configuration_ItemName", "configuration", "ItemName")

def update_3305(dbo):
    # Add IsHold and IsQuarantine fields
    add_column(dbo, "animal", "IsHold", "INTEGER")
    add_column(dbo, "animal", "IsQuarantine", "INTEGER")
    db.execute_dbupdate(dbo, "UPDATE animal SET IsHold = 0, IsQuarantine = 0")

def update_3306(dbo):
    # Add HoldUntilDate
    add_column(dbo, "animal", "HoldUntilDate", datetype(dbo))

def update_3307(dbo):
    # Create new animaltest tables
    sql = "CREATE TABLE animaltest (ID INTEGER NOT NULL PRIMARY KEY, " \
        "AnimalID INTEGER NOT NULL, " \
        "TestTypeID INTEGER NOT NULL, " \
        "TestResultID INTEGER NOT NULL, " \
        "DateOfTest %(date)s, " \
        "DateRequired %(date)s NOT NULL, " \
        "Cost INTEGER, " \
        "Comments %(long)s, " \
        "RecordVersion INTEGER, " \
        "CreatedBy %(short)s, " \
        "CreatedDate %(date)s, " \
        "LastChangedBy %(short)s, " \
        "LastChangedDate %(date)s)" % { "date": datetype(dbo), "long": longtext(dbo), "short": shorttext(dbo)}
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "animaltest_AnimalID", "animaltest", "AnimalID")
    sql = "CREATE TABLE testtype (ID INTEGER NOT NULL PRIMARY KEY, " \
        "TestName %(short)s NOT NULL, " \
        "TestDescription %(long)s, " \
            "DefaultCost INTEGER)" % { "short": shorttext(dbo), "long": longtext(dbo) }
    db.execute_dbupdate(dbo, sql)
    sql = "CREATE TABLE testresult (ID INTEGER NOT NULL PRIMARY KEY, " \
        "ResultName %(short)s NOT NULL, " \
        "ResultDescription %(long)s)" % { "short": shorttext(dbo), "long": longtext(dbo) }
    db.execute_dbupdate(dbo, sql)

def update_3308(dbo):
    # Create intial data for testtype and testresult tables
    l = dbo.locale
    db.execute_dbupdate(dbo, "INSERT INTO testresult (ID, ResultName) VALUES (1, '" + _("Unknown", l) + "')")
    db.execute_dbupdate(dbo, "INSERT INTO testresult (ID, ResultName) VALUES (2, '" + _("Negative", l) + "')")
    db.execute_dbupdate(dbo, "INSERT INTO testresult (ID, ResultName) VALUES (3, '" + _("Positive", l) + "')")
    db.execute_dbupdate(dbo, "INSERT INTO testtype (ID, TestName, DefaultCost) VALUES (1, '" + _("FIV", l) + "', 0)")
    db.execute_dbupdate(dbo, "INSERT INTO testtype (ID, TestName, DefaultCost) VALUES (2, '" + _("FLV", l) + "', 0)")
    db.execute_dbupdate(dbo, "INSERT INTO testtype (ID, TestName, DefaultCost) VALUES (3, '" + _("Heartworm", l) + "', 0)")

def update_3309(dbo):
    fiv = db.query(dbo, "SELECT ID, CombiTestDate, CombiTestResult FROM animal WHERE CombiTested = 1")
    al.debug("found %d fiv results to convert" % len(fiv), "update_3309", dbo)
    for f in fiv:
        ntestid = db._get_id_max(dbo, "animaltest")
        sql = db.make_insert_user_sql(dbo, "animaltest", "update", ( 
            ( "ID", db.di(ntestid)),
            ( "AnimalID", db.di(f["ID"])),
            ( "TestTypeID", db.di(1)),
            ( "TestResultID", db.di(f["COMBITESTRESULT"] + 1)),
            ( "DateOfTest", db.dd(f["COMBITESTDATE"])),
            ( "DateRequired", db.dd(f["COMBITESTDATE"])),
            ( "Cost", db.di(0)),
            ( "Comments", db.ds(""))
            ))
        try:
            db.execute_dbupdate(dbo, sql)
        except Exception,err:
            al.error("fiv: " + str(err), "dbupdate.update_3309", dbo)
    flv = db.query(dbo, "SELECT ID, CombiTestDate, FLVResult FROM animal WHERE CombiTested = 1")
    al.debug("found %d flv results to convert" % len(flv), "update_3309", dbo)
    for f in flv:
        ntestid = db._get_id_max(dbo, "animaltest")
        sql = db.make_insert_user_sql(dbo, "animaltest", "update", ( 
            ( "ID", db.di(ntestid)),
            ( "AnimalID", db.di(f["ID"])),
            ( "TestTypeID", db.di(2)),
            ( "TestResultID", db.di(f["FLVRESULT"] + 1)),
            ( "DateOfTest", db.dd(f["COMBITESTDATE"])),
            ( "DateRequired", db.dd(f["COMBITESTDATE"])),
            ( "Cost", db.di(0)),
            ( "Comments", db.ds(""))
            ))
        try:
            db.execute_dbupdate(dbo, sql)
        except Exception,err:
            al.error("flv: " + str(err), "dbupdate.update_3309", dbo)

    hw = db.query(dbo, "SELECT ID, HeartwormTestDate, HeartwormTestResult FROM animal WHERE HeartwormTested = 1")
    al.debug("found %d heartworm results to convert" % len(hw), "update_3309", dbo)
    for f in hw:
        ntestid = db._get_id_max(dbo, "animaltest")
        sql = db.make_insert_user_sql(dbo, "animaltest", "update", ( 
            ( "ID", db.di(ntestid)),
            ( "AnimalID", db.di(f["ID"])),
            ( "TestTypeID", db.di(3)),
            ( "TestResultID", db.di(f["HEARTWORMTESTRESULT"] + 1)),
            ( "DateOfTest", db.dd(f["HEARTWORMTESTDATE"])),
            ( "DateRequired", db.dd(f["HEARTWORMTESTDATE"])),
            ( "Cost", db.di(0)),
            ( "Comments", db.ds(""))
            ))
        try:
            db.execute_dbupdate(dbo, sql)
        except Exception,err:
            al.error("hw: " + str(err), "dbupdate.update_3309", dbo)

def update_33010(dbo):
    # Add new additional field types and locations
    l = dbo.locale
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldtype (ID, FieldType) VALUES (7, '" + _("Multi-Lookup", l) + "')")
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldtype (ID, FieldType) VALUES (8, '" + _("Animal", l) + "')")
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldtype (ID, FieldType) VALUES (9, '" + _("Person", l) + "')")
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink (ID, LinkType) VALUES (9, '" + _("Lost Animal - Additional", l) + "')")
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink (ID, LinkType) VALUES (10, '" + _("Lost Animal - Details", l) + "')")
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink (ID, LinkType) VALUES (11, '" + _("Found Animal - Additional", l) + "')")
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink (ID, LinkType) VALUES (12, '" + _("Found Animal - Details", l) + "')")
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink (ID, LinkType) VALUES (13, '" + _("Waiting List - Additional", l) + "')")
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink (ID, LinkType) VALUES (14, '" + _("Waiting List - Details", l) + "')")
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink (ID, LinkType) VALUES (15, '" + _("Waiting List - Removal", l) + "')")

def update_33011(dbo):
    # Add donationpayment table and data
    l = dbo.locale
    sql = "CREATE TABLE donationpayment (ID INTEGER NOT NULL PRIMARY KEY, " \
        "PaymentName %(short)s NOT NULL, " \
        "PaymentDescription %(long)s ) " % { "short": shorttext(dbo), "long": longtext(dbo) }
    db.execute_dbupdate(dbo, sql)
    db.execute_dbupdate(dbo, "INSERT INTO donationpayment (ID, PaymentName) VALUES (1, '" + _("Cash", l) + "')")
    db.execute_dbupdate(dbo, "INSERT INTO donationpayment (ID, PaymentName) VALUES (2, '" + _("Cheque", l) + "')")
    db.execute_dbupdate(dbo, "INSERT INTO donationpayment (ID, PaymentName) VALUES (3, '" + _("Credit Card", l) + "')")
    db.execute_dbupdate(dbo, "INSERT INTO donationpayment (ID, PaymentName) VALUES (4, '" + _("Debit Card", l) + "')")
    # Add donationpaymentid field to donations
    db.execute_dbupdate(dbo, "ALTER TABLE ownerdonation ADD DonationPaymentID INTEGER")
    db.execute_dbupdate(dbo, "UPDATE ownerdonation SET DonationPaymentID = 1")

def update_33012(dbo):
    # Add ShelterLocationUnit
    add_column(dbo, "animal", "ShelterLocationUnit", shorttext(dbo))
    db.execute_dbupdate(dbo, "UPDATE animal SET ShelterLocationUnit = ''")

def update_33013(dbo):
    # Add online form tables
    sql = "CREATE TABLE onlineform (ID INTEGER NOT NULL PRIMARY KEY, " \
        "Name %(short)s NOT NULL, " \
        "RedirectUrlAfterPOST %(short)s, " \
        "SetOwnerFlags %(short)s, " \
        "Description %(long)s )" % { "short": shorttext(dbo), "long": longtext(dbo) }
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "onlineform_Name", "onlineform", "Name")
    sql = "CREATE TABLE onlineformfield(ID INTEGER NOT NULL PRIMARY KEY, " \
        "OnlineFormID INTEGER NOT NULL, " \
        "FieldName %(short)s NOT NULL, " \
        "FieldType INTEGER NOT NULL, " \
        "Label %(short)s NOT NULL, " \
        "Lookups %(long)s, " \
        "Tooltip %(long)s )" % { "short": shorttext(dbo), "long": longtext(dbo) }
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "onlineformfield_OnlineFormID", "onlineformfield", "OnlineFormID")
    sql = "CREATE TABLE onlineformincoming(CollationID INTEGER NOT NULL, " \
        "FormName %(short)s NOT NULL, " \
        "PostedDate %(date)s NOT NULL, " \
        "Flags %(short)s, " \
        "FieldName %(short)s NOT NULL, " \
        "Value %(long)s )" % { "date": datetype(dbo), "short": shorttext(dbo), "long": longtext(dbo) }
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "onlineformincoming_CollationID", "onlineformincoming", "CollationID")

def update_33014(dbo):
    # Add a display index field to onlineformfield
    add_column(dbo, "onlineformfield", "DisplayIndex", "INTEGER")
    # Add a label field to onlineformincoming
    add_column(dbo, "onlineformincoming", "Label", shorttext(dbo))

def update_33015(dbo):
    # Add a host field to onlineformincoming
    add_column(dbo, "onlineformincoming", "Host", shorttext(dbo))

def update_33016(dbo):
    # Add a DisplayIndex and Preview field to onlineformincoming
    add_column(dbo, "onlineformincoming", "DisplayIndex", "INTEGER")
    add_column(dbo, "onlineformincoming", "Preview", longtext(dbo))

def update_33017(dbo):
    # Add the customreportrole table
    db.execute_dbupdate(dbo, "CREATE TABLE customreportrole (ReportID INTEGER NOT NULL, " \
        "RoleID INTEGER NOT NULL, CanView INTEGER NOT NULL)")
    db.execute_dbupdate(dbo, "CREATE UNIQUE INDEX customreportrole_ReportIDRoleID ON customreportrole(ReportID, RoleID)")

def update_33018(dbo):
    l = dbo.locale
    # Add IsPermanentFoster and HasPermanentFoster fields
    add_column(dbo, "adoption", "IsPermanentFoster", "INTEGER")
    add_column(dbo, "animal", "HasPermanentFoster", "INTEGER")
    # Add Permanent Foster movement type
    db.execute_dbupdate(dbo, "INSERT INTO lksmovementtype (ID, MovementType) VALUES (12, %s)" % db.ds(_("Permanent Foster", l)))

def update_33019(dbo):
    # Set initial value for those flags
    db.execute_dbupdate(dbo, "UPDATE adoption SET IsPermanentFoster = 0 WHERE IsPermanentFoster Is Null")
    db.execute_dbupdate(dbo, "UPDATE animal SET HasPermanentFoster = 0 WHERE HasPermanentFoster Is Null")

def update_33101(dbo):
    # Many indexes we should have
    add_index(dbo, "owner_OwnerAddress", "owner", "OwnerAddress")
    add_index(dbo, "owner_OwnerCounty", "owner", "OwnerCounty")
    add_index(dbo, "owner_EmailAddress", "owner", "EmailAddress")
    add_index(dbo, "owner_OwnerForeNames", "owner", "OwnerForeNames")
    add_index(dbo, "owner_HomeTelephone", "owner", "HomeTelephone")
    add_index(dbo, "owner_MobileTelephone", "owner", "MobileTelephone")
    add_index(dbo, "owner_WorkTelephone", "owner", "WorkTelephone")
    add_index(dbo, "owner_OwnerInitials", "owner", "OwnerInitials")
    add_index(dbo, "owner_OwnerPostcode", "owner", "OwnerPostcode")
    add_index(dbo, "owner_OwnerSurname", "owner", "OwnerSurname")
    add_index(dbo, "owner_OwnerTitle", "owner", "OwnerTitle")
    add_index(dbo, "owner_OwnerTown", "owner", "OwnerTown")
    add_index(dbo, "animal_AcceptanceNumber", "animal", "AcceptanceNumber")
    add_index(dbo, "animal_ActiveMovementType", "animal", "ActiveMovementType")
    add_index(dbo, "animal_AnimalTypeID", "animal", "AnimalTypeID")
    add_index(dbo, "animal_BaseColourID", "animal", "BaseColourID")
    add_index(dbo, "animal_BondedAnimalID", "animal", "BondedAnimalID")
    add_index(dbo, "animal_BondedAnimal2ID", "animal", "BondedAnimal2ID")
    add_index(dbo, "animal_BreedID", "animal", "BreedID")
    add_index(dbo, "animal_Breed2ID", "animal", "Breed2ID")
    add_index(dbo, "animal_BroughtInByOwnerID", "animal", "BroughtInByOwnerID")
    add_index(dbo, "animal_CoatType", "animal", "CoatType")
    add_index(dbo, "animal_CurrentVetID", "animal", "CurrentVetID")
    add_index(dbo, "animal_DeceasedDate", "animal", "DeceasedDate")
    add_index(dbo, "animal_EntryReasonID", "animal", "EntryReasonID")
    add_index(dbo, "animal_IdentichipNumber", "animal", "IdentichipNumber")
    add_index(dbo, "animal_OriginalOwnerID", "animal", "OriginalOwnerID")
    add_index(dbo, "animal_OwnersVetID", "animal", "OwnersVetID")
    add_index(dbo, "animal_PutToSleep", "animal", "PutToSleep")
    add_index(dbo, "animal_PTSReasonID", "animal", "PTSReasonID")
    add_index(dbo, "animal_Sex", "animal", "Sex")
    add_index(dbo, "animal_Size", "animal", "Size")
    add_index(dbo, "animal_ShelterLocation", "animal", "ShelterLocation")
    add_index(dbo, "animal_ShelterLocationUnit", "animal", "ShelterLocationUnit")
    add_index(dbo, "animal_ShortCode", "animal", "ShortCode")
    add_index(dbo, "animal_SpeciesID", "animal", "SpeciesID")
    add_index(dbo, "adoption_CreatedBy", "adoption", "CreatedBy")
    add_index(dbo, "adoption_IsPermanentFoster", "adoption", "IsPermanentFoster")
    add_index(dbo, "adoption_IsTrial", "adoption", "IsTrial")
    add_index(dbo, "adoption_ReturnedReasonID", "adoption", "ReturnedReasonID")

def update_33102(dbo):
    # More indexes we should have
    add_index(dbo, "animal_AgeGroup", "animal", "AgeGroup")
    add_index(dbo, "animal_BreedName", "animal", "BreedName")
    add_index(dbo, "animal_RabiesTag", "animal", "RabiesTag")
    add_index(dbo, "animal_TattooNumber", "animal", "TattooNumber")
    add_index(dbo, "owner_MembershipNumber", "owner", "MembershipNumber")
    add_index(dbo, "animallost_AreaLost", "animallost", "AreaLost")
    add_index(dbo, "animallost_AreaPostcode", "animallost", "AreaPostcode")
    add_index(dbo, "animalfound_AreaFound", "animalfound", "AreaFound")
    add_index(dbo, "animalfound_AreaPostcode", "animalfound", "AreaPostcode")
    add_index(dbo, "animalwaitinglist_AnimalDescription", "animalwaitinglist", "AnimalDescription")
    add_index(dbo, "animalwaitinglist_OwnerID", "animalwaitinglist", "OwnerID")
    add_index(dbo, "animalfound_AnimalTypeID", "animalfound", "AnimalTypeID")
    add_index(dbo, "animallost_AnimalTypeID", "animallost", "AnimalTypeID")
    add_index(dbo, "media_LinkTypeID", "media", "LinkTypeID")
    add_index(dbo, "media_WebsitePhoto", "media", "WebsitePhoto")
    add_index(dbo, "media_WebsiteVideo", "media", "WebsiteVideo")
    add_index(dbo, "media_DocPhoto", "media", "DocPhoto")
    add_index(dbo, "adoption_MovementType", "adoption", "MovementType")
    add_index(dbo, "adoption_ReservationDate", "adoption", "ReservationDate")
    add_index(dbo, "adoption_ReservationCancelledDate", "adoption", "ReservationCancelledDate")

def update_33103(dbo):
    add_index(dbo, "owner_HomeTelephone", "owner", "HomeTelephone")
    add_index(dbo, "owner_MobileTelephone", "owner", "MobileTelephone")
    add_index(dbo, "owner_WorkTelephone", "owner", "WorkTelephone")
    add_index(dbo, "owner_EmailAddress", "owner", "EmailAddress")
    add_index(dbo, "animal_BroughtInByOwnerID", "animal", "BroughtInByOwnerID")

def update_33104(dbo):
    # Add LatLong
    add_column(dbo, "owner", "LatLong", shorttext(dbo))

def update_33105(dbo):
    # Add LocationFilter
    add_column(dbo, "users", "LocationFilter", shorttext(dbo))

def update_33106(dbo):
    # Add MatchColour
    add_column(dbo, "owner", "MatchColour", "INTEGER")
    db.execute_dbupdate(dbo, "UPDATE owner SET MatchColour = -1")

def update_33201(dbo):
    # Add Fee column
    add_column(dbo, "animal", "Fee", "INTEGER")

def update_33202(dbo):
    # Add the animalpublished table to track what was sent to which
    # publisher and when
    sql = "CREATE TABLE animalpublished (" \
        "AnimalID INTEGER NOT NULL, " \
        "PublishedTo %s NOT NULL, " \
        "SentDate %s NOT NULL, " \
        "Extra %s)" % (shorttext(dbo), datetype(dbo), shorttext(dbo))
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "animalpublished_AnimalIDPublishedTo", "animalpublished", "AnimalID, PublishedTo", True)
    add_index(dbo, "animalpublished_SentDate", "animalpublished", "SentDate")
    # Copy existing values into the new table
    db.execute_dbupdate(dbo, "INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT a.ID, 'smarttag', a.SmartTagSentDate FROM animal a WHERE a.SmartTagSentDate Is Not Null")
    db.execute_dbupdate(dbo, "INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT a.ID, 'petlink', a.PetLinkSentDate FROM animal a WHERE a.PetLinkSentDate Is Not Null")
    db.execute_dbupdate(dbo, "INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT DISTINCT m.LinkID, 'html', m.LastPublished FROM media m WHERE m.LastPublished Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
    db.execute_dbupdate(dbo, "INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT DISTINCT m.LinkID, 'petfinder', m.LastPublishedPF FROM media m WHERE m.LastPublishedPF Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
    db.execute_dbupdate(dbo, "INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT DISTINCT m.LinkID, 'adoptapet', m.LastPublishedAP FROM media m WHERE m.LastPublishedAP Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
    db.execute_dbupdate(dbo, "INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT DISTINCT m.LinkID, 'pets911', m.LastPublishedP911 FROM media m WHERE m.LastPublishedP911 Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
    db.execute_dbupdate(dbo, "INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT DISTINCT m.LinkID, 'rescuegroups', m.LastPublishedRG FROM media m WHERE m.LastPublishedRG Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
    db.execute_dbupdate(dbo, "INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT DISTINCT m.LinkID, 'meetapet', m.LastPublishedMP FROM media m WHERE m.LastPublishedMP Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
    db.execute_dbupdate(dbo, "INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT DISTINCT m.LinkID, 'helpinglostpets', m.LastPublishedHLP FROM media m WHERE m.LastPublishedHLP Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")

def update_33203(dbo):
    # Assume all already adopted animals with PETtrac UK chips have been sent to them
    db.execute_dbupdate(dbo, "INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT a.ID, 'pettracuk', a.ActiveMovementDate FROM animal a " \
        "WHERE ActiveMovementDate Is Not Null " \
        "AND ActiveMovementType = 1 AND IdentichipNumber LIKE '977%'");

def update_33204(dbo):
    # Remove last published fields added since ASM3 - we're only retaining
    # the ASM2 ones for compatibility and everything else is going to
    # the animalpublished table
    drop_column(dbo, "media", "LastPublishedHLP")
    drop_column(dbo, "media", "LastPublishedMP")
    drop_column(dbo, "animal", "PetLinkSentDate")

def update_33205(dbo):
    # Add mandatory column to online form fields
    add_column(dbo, "onlineformfield", "Mandatory", "INTEGER")
    db.execute_dbupdate(dbo, "UPDATE onlineformfield SET Mandatory = 0")

def update_33206(dbo):
    # Add cost paid date fields
    add_column(dbo, "animalcost", "CostPaidDate", datetype(dbo))
    add_column(dbo, "animalmedical", "CostPaidDate", datetype(dbo))
    add_column(dbo, "animaltest", "CostPaidDate", datetype(dbo))
    add_column(dbo, "animalvaccination", "CostPaidDate", datetype(dbo))
    add_index(dbo, "animalcost_CostPaidDate", "animalcost", "CostPaidDate")
    add_index(dbo, "animalmedical_CostPaidDate", "animalmedical", "CostPaidDate")
    add_index(dbo, "animaltest_CostPaidDate", "animaltest", "CostPaidDate")
    add_index(dbo, "animalvaccination_CostPaidDate", "animalvaccination", "CostPaidDate")

def update_33300(dbo):
    # Add animalcontrol table
    sql = "CREATE TABLE animalcontrol (" \
        "ID INTEGER NOT NULL PRIMARY KEY, " \
        "IncidentDateTime %(date)s NOT NULL, " \
        "IncidentTypeID INTEGER NOT NULL, " \
        "CallDateTime %(date)s, " \
        "CallNotes %(long)s, " \
        "CallTaker %(short)s, " \
        "CallerID INTEGER, " \
        "VictimID INTEGER, " \
        "DispatchAddress %(short)s, " \
        "DispatchTown %(short)s, " \
        "DispatchCounty %(short)s, " \
        "DispatchPostcode %(short)s, " \
        "DispatchLatLong %(short)s, " \
        "DispatchedACO %(short)s, " \
        "DispatchDateTime %(date)s, " \
        "RespondedDateTime %(date)s, " \
        "FollowupDateTime %(date)s, " \
        "CompletedDate %(date)s, " \
        "IncidentCompletedID INTEGER, " \
        "OwnerID INTEGER, " \
        "AnimalDescription %(long)s, " \
        "SpeciesID INTEGER, " \
        "Sex INTEGER, " \
        "AgeGroup %(short)s, " \
        "RecordVersion INTEGER, " \
        "CreatedBy %(short)s, " \
        "CreatedDate %(date)s, " \
        "LastChangedBy %(short)s, " \
        "LastChangedDate %(date)s)" % { "short": shorttext(dbo), "long": longtext(dbo), "date": datetype(dbo) }
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "animalcontrol_IncidentDateTime", "animalcontrol", "IncidentDateTime")
    add_index(dbo, "animalcontrol_IncidentTypeID", "animalcontrol", "IncidentTypeID")
    add_index(dbo, "animalcontrol_CallDateTime", "animalcontrol", "CallDateTime")
    add_index(dbo, "animalcontrol_CallerID", "animalcontrol", "CallerID")
    add_index(dbo, "animalcontrol_DispatchAddress", "animalcontrol", "DispatchAddress")
    add_index(dbo, "animalcontrol_DispatchPostcode", "animalcontrol", "DispatchPostcode")
    add_index(dbo, "animalcontrol_DispatchedACO", "animalcontrol", "DispatchedACO")
    add_index(dbo, "animalcontrol_DispatchDateTime", "animalcontrol", "DispatchDateTime")
    add_index(dbo, "animalcontrol_CompletedDate", "animalcontrol", "CompletedDate")
    add_index(dbo, "animalcontrol_IncidentCompletedID", "animalcontrol", "IncidentCompletedID")
    add_index(dbo, "animalcontrol_OwnerID", "animalcontrol", "OwnerID")
    add_index(dbo, "animalcontrol_VictimID", "animalcontrol", "VictimID")

def update_33301(dbo):
    # ownercitation table
    sql = "CREATE TABLE ownercitation (" \
        "ID INTEGER NOT NULL PRIMARY KEY, " \
        "OwnerID INTEGER NOT NULL, " \
        "AnimalControlID INTEGER, " \
        "CitationTypeID INTEGER NOT NULL, " \
        "CitationDate %(date)s NOT NULL, " \
        "FineAmount INTEGER, " \
        "FineDueDate %(date)s, " \
        "FinePaidDate %(date)s, " \
        "Comments %(long)s, " \
        "RecordVersion INTEGER, " \
        "CreatedBy %(short)s, " \
        "CreatedDate %(date)s, " \
        "LastChangedBy %(short)s, " \
        "LastChangedDate %(date)s)" % { "short": shorttext(dbo), "long": longtext(dbo), "date": datetype(dbo) }
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "ownercitation_OwnerID", "ownercitation", "OwnerID")
    add_index(dbo, "ownercitation_CitationTypeID", "ownercitation", "CitationTypeID")
    add_index(dbo, "ownercitation_CitationDate", "ownercitation", "CitationDate")
    add_index(dbo, "ownercitation_FineDueDate", "ownercitation", "FineDueDate")
    add_index(dbo, "ownercitation_FinePaidDate", "ownercitation", "FinePaidDate")

def update_33302(dbo):
    l = dbo.locale
    # Lookup tables
    sql = "CREATE TABLE citationtype (ID INTEGER NOT NULL PRIMARY KEY, " \
        "CitationName %s NOT NULL, CitationDescription %s, DefaultCost INTEGER)" % (shorttext(dbo), longtext(dbo))
    db.execute_dbupdate(dbo, sql)
    sql = "CREATE TABLE incidenttype (ID INTEGER NOT NULL PRIMARY KEY, " \
        "IncidentName %s NOT NULL, IncidentDescription %s)" % (shorttext(dbo), longtext(dbo))
    db.execute_dbupdate(dbo, sql)
    sql = "CREATE TABLE incidentcompleted (ID INTEGER NOT NULL PRIMARY KEY, " \
        "CompletedName %s NOT NULL, CompletedDescription %s)" % (shorttext(dbo), longtext(dbo))
    db.execute_dbupdate(dbo, sql)
    # Default lookup data
    db.execute_dbupdate(dbo, "INSERT INTO citationtype VALUES (1, '%s', '', 0)" % _("First offence", l))
    db.execute_dbupdate(dbo, "INSERT INTO citationtype VALUES (2, '%s', '', 0)" % _("Second offence", l))
    db.execute_dbupdate(dbo, "INSERT INTO citationtype VALUES (3, '%s', '', 0)" % _("Third offence", l))
    db.execute_dbupdate(dbo, "INSERT INTO incidenttype VALUES (1, '%s', '')" % _("Aggression", l))
    db.execute_dbupdate(dbo, "INSERT INTO incidenttype VALUES (2, '%s', '')" % _("Animal defecation", l))
    db.execute_dbupdate(dbo, "INSERT INTO incidenttype VALUES (3, '%s', '')" % _("Animals at large", l))
    db.execute_dbupdate(dbo, "INSERT INTO incidenttype VALUES (4, '%s', '')" % _("Animals left in vehicle", l))
    db.execute_dbupdate(dbo, "INSERT INTO incidenttype VALUES (5, '%s', '')" % _("Bite", l))
    db.execute_dbupdate(dbo, "INSERT INTO incidenttype VALUES (6, '%s', '')" % _("Dead animal", l))
    db.execute_dbupdate(dbo, "INSERT INTO incidenttype VALUES (7, '%s', '')" % _("Neglect", l))
    db.execute_dbupdate(dbo, "INSERT INTO incidenttype VALUES (8, '%s', '')" % _("Noise", l))
    db.execute_dbupdate(dbo, "INSERT INTO incidenttype VALUES (9, '%s', '')" % _("Number of pets", l))
    db.execute_dbupdate(dbo, "INSERT INTO incidenttype VALUES (10, '%s', '')" % _("Sick/injured animal", l))
    db.execute_dbupdate(dbo, "INSERT INTO incidentcompleted VALUES (1, '%s', '')" % _("Animal destroyed", l))
    db.execute_dbupdate(dbo, "INSERT INTO incidentcompleted VALUES (2, '%s', '')" % _("Animal picked up", l))
    db.execute_dbupdate(dbo, "INSERT INTO incidentcompleted VALUES (3, '%s', '')" % _("Owner given citation", l))

def update_33303(dbo):
    # Add new incident link types
    l = dbo.locale
    db.execute_dbupdate(dbo, "INSERT INTO lksloglink (ID, LinkType) VALUES (%d, '%s')" % (6, _("Incident", l)))
    db.execute_dbupdate(dbo, "INSERT INTO lksmedialink (ID, LinkType) VALUES (%d, '%s')" % (5, _("Incident", l)))
    db.execute_dbupdate(dbo, "INSERT INTO lksdiarylink (ID, LinkType) VALUES (%d, '%s')" % (7, _("Incident", l)))
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink VALUES (16, '%s')" % _("Incident - Details", l))
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink VALUES (17, '%s')" % _("Incident - Dispatch", l))
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink VALUES (18, '%s')" % _("Incident - Owner", l))
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink VALUES (19, '%s')" % _("Incident - Citation", l))
    db.execute_dbupdate(dbo, "INSERT INTO lksfieldlink VALUES (20, '%s')" % _("Incident - Additional", l))

def update_33304(dbo):
    # Add trap loan table
    sql = "CREATE TABLE ownertraploan (" \
        "ID INTEGER NOT NULL PRIMARY KEY, " \
        "OwnerID INTEGER NOT NULL, " \
        "TrapTypeID INTEGER NOT NULL, " \
        "LoanDate %(date)s NOT NULL, " \
        "DepositAmount INTEGER, " \
        "DepositReturnDate %(date)s, " \
        "TrapNumber %(short)s, " \
        "ReturnDueDate %(date)s, " \
        "ReturnDate %(date)s, " \
        "Comments %(long)s, " \
        "RecordVersion INTEGER, " \
        "CreatedBy %(short)s, " \
        "CreatedDate %(date)s, " \
        "LastChangedBy %(short)s, " \
        "LastChangedDate %(date)s)" % { "short": shorttext(dbo), "long": longtext(dbo), "date": datetype(dbo) }
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "ownertraploan_OwnerID", "ownertraploan", "OwnerID")
    add_index(dbo, "ownertraploan_TrapTypeID", "ownertraploan", "TrapTypeID")
    add_index(dbo, "ownertraploan_ReturnDueDate", "ownertraploan", "ReturnDueDate")
    add_index(dbo, "ownertraploan_ReturnDate", "ownertraploan", "ReturnDate")

def update_33305(dbo):
    # Add traptype lookup
    l = dbo.locale
    sql = "CREATE TABLE traptype (ID INTEGER NOT NULL PRIMARY KEY, " \
        "TrapTypeName %s NOT NULL, TrapTypeDescription %s, DefaultCost INTEGER)" % (shorttext(dbo), longtext(dbo))
    db.execute_dbupdate(dbo, sql)
    db.execute_dbupdate(dbo, "INSERT INTO traptype VALUES (1, '%s', '', 0)" % _("Cat", l))

def update_33306(dbo):
    # Add licence table
    sql = "CREATE TABLE ownerlicence (" \
        "ID INTEGER NOT NULL PRIMARY KEY, " \
        "OwnerID INTEGER NOT NULL, " \
        "AnimalID INTEGER NOT NULL, " \
        "LicenceTypeID INTEGER NOT NULL, " \
        "LicenceNumber %(short)s, " \
        "LicenceFee INTEGER, " \
        "IssueDate %(date)s, " \
        "ExpiryDate %(date)s, " \
        "Comments %(long)s, " \
        "RecordVersion INTEGER, " \
        "CreatedBy %(short)s, " \
        "CreatedDate %(date)s, " \
        "LastChangedBy %(short)s, " \
        "LastChangedDate %(date)s)" % { "short": shorttext(dbo), "long": longtext(dbo), "date": datetype(dbo) }
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "ownerlicence_OwnerID", "ownerlicence", "OwnerID")
    add_index(dbo, "ownerlicence_AnimalID", "ownerlicence", "AnimalID")
    add_index(dbo, "ownerlicence_LicenceTypeID", "ownerlicence", "LicenceTypeID")
    add_index(dbo, "ownerlicence_LicenceNumber", "ownerlicence", "LicenceNumber", True)
    add_index(dbo, "ownerlicence_IssueDate", "ownerlicence", "IssueDate")
    add_index(dbo, "ownerlicence_ExpiryDate", "ownerlicence", "ExpiryDate")

def update_33307(dbo):
    # Add licencetype lookup
    l = dbo.locale
    sql = "CREATE TABLE licencetype (ID INTEGER NOT NULL PRIMARY KEY, " \
        "LicenceTypeName %s NOT NULL, LicenceTypeDescription %s, DefaultCost INTEGER)" % (shorttext(dbo), longtext(dbo))
    db.execute_dbupdate(dbo, sql)
    db.execute_dbupdate(dbo, "INSERT INTO licencetype VALUES (1, '%s', '', 0)" % _("Altered Dog - 1 year", l))
    db.execute_dbupdate(dbo, "INSERT INTO licencetype VALUES (2, '%s', '', 0)" % _("Unaltered Dog - 1 year", l))
    db.execute_dbupdate(dbo, "INSERT INTO licencetype VALUES (3, '%s', '', 0)" % _("Altered Dog - 3 year", l))
    db.execute_dbupdate(dbo, "INSERT INTO licencetype VALUES (4, '%s', '', 0)" % _("Unaltered Dog - 3 year", l))

def update_33308(dbo):
    # broken
    dummy = dbo
    pass

def update_33309(dbo):
    # Create animalfiguresmonthlyasilomar table to be updated each night
    # for US shelters with the option on
    sql = "CREATE TABLE animalfiguresmonthlyasilomar ( ID INTEGER NOT NULL, " \
        "Month INTEGER NOT NULL, " \
        "Year INTEGER NOT NULL, " \
        "OrderIndex INTEGER NOT NULL, " \
        "Code %s NOT NULL, " \
        "Heading %s NOT NULL, " \
        "Bold INTEGER NOT NULL, " \
        "Cat INTEGER NOT NULL, " \
        "Dog INTEGER NOT NULL, " \
        "Total INTEGER NOT NULL)" % (shorttext(dbo), shorttext(dbo))
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "animalfiguresmonthlyasilomar_ID", "animalfiguresmonthlyasilomar", "ID", True)
    add_index(dbo, "animalfiguresmonthlyasilomar_Year", "animalfiguresmonthlyasilomar", "Year")
    add_index(dbo, "animalfiguresmonthlyasilomar_Month", "animalfiguresmonthlyasilomar", "Month")

def update_33310(dbo):
    dummy = dbo
    pass # broken

def update_33311(dbo):
    # Add exclude from bulk email field to owner
    add_column(dbo, "owner", "ExcludeFromBulkEmail", "INTEGER")
    db.execute_dbupdate(dbo, "UPDATE owner SET ExcludeFromBulkEmail = 0")

def update_33312(dbo):
    # Add header/footer to onlineform fields
    add_column(dbo, "onlineform", "Header", longtext(dbo))
    add_column(dbo, "onlineform", "Footer", longtext(dbo))

def update_33313(dbo):
    # onlineformincoming.DisplayIndex should have been an integer,
    # but the new db created it accidentally as a str in some
    # databases - switch it to integer
    modify_column(dbo, "onlineformincoming", "DisplayIndex", "INTEGER", "(DisplayIndex::integer)")

def update_33314(dbo):
    # Add extra followup and suspect fields to animal control
    add_column(dbo, "animalcontrol", "FollowupDateTime2", datetype(dbo))
    add_column(dbo, "animalcontrol", "FollowupDateTime3", datetype(dbo))
    add_column(dbo, "animalcontrol", "Owner2ID", "INTEGER")
    add_column(dbo, "animalcontrol", "Owner3ID", "INTEGER")
    add_column(dbo, "animalcontrol", "AnimalID", "INTEGER")
    add_index(dbo, "animalcontrol_FollowupDateTime", "animalcontrol", "FollowupDateTime")
    add_index(dbo, "animalcontrol_FollowupDateTime2", "animalcontrol", "FollowupDateTime2")
    add_index(dbo, "animalcontrol_FollowupDateTime3", "animalcontrol", "FollowupDateTime3")
    add_index(dbo, "animalcontrol_Owner2ID", "animalcontrol", "Owner2ID")
    add_index(dbo, "animalcontrol_Owner3ID", "animalcontrol", "Owner3ID")
    add_index(dbo, "animalcontrol_AnimalID", "animalcontrol", "AnimalID")

def update_33315(dbo):
    # Add size field to waiting list
    add_column(dbo, "animalwaitinglist", "Size", "INTEGER")
    add_index(dbo, "animalwaitinglist_Size", "animalwaitinglist", "Size")
    db.execute_dbupdate(dbo, "UPDATE animalwaitinglist SET Size = 2")

def update_33316(dbo):
    # Add emailaddress field to onlineform
    add_column(dbo, "onlineform", "EmailAddress", longtext(dbo))

def update_33401(dbo):
    # Add OwnerType and IsDeceased flags to owner
    add_column(dbo, "owner", "OwnerType", "INTEGER")
    add_column(dbo, "owner", "IsDeceased", "INTEGER")
    db.execute_dbupdate(dbo, "UPDATE owner SET OwnerType = 1")
    db.execute_dbupdate(dbo, "UPDATE owner SET OwnerType = 2 WHERE IsShelter = 1")
    db.execute_dbupdate(dbo, "UPDATE owner SET IsDeceased = 0")

def update_33402(dbo):
    l = dbo.locale
    # Add stock tables
    sql = "CREATE TABLE stocklevel ( ID INTEGER NOT NULL, " \
        "Name %(short)s NOT NULL, " \
        "Description %(long)s, " \
        "StockLocationID INTEGER NOT NULL, " \
        "UnitName %(short)s NOT NULL, " \
        "Total INTEGER, " \
        "Balance INTEGER NOT NULL, " \
        "Expiry %(date)s, " \
        "BatchNumber %(short)s, " \
        "CreatedDate %(date)s NOT NULL)" % { "short": shorttext(dbo), "long": longtext(dbo), "date": datetype(dbo) }
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "stocklevel_ID", "stocklevel", "ID", True)
    add_index(dbo, "stocklevel_Name", "stocklevel", "Name")
    add_index(dbo, "stocklevel_UnitName", "stocklevel", "UnitName")
    add_index(dbo, "stocklevel_StockLocationID", "stocklevel", "StockLocationID")
    add_index(dbo, "stocklevel_Expiry", "stocklevel", "Expiry")
    add_index(dbo, "stocklevel_BatchNumber", "stocklevel", "BatchNumber")
    sql = "CREATE TABLE stocklocation ( ID INTEGER NOT NULL, " \
        "LocationName %(short)s NOT NULL, " \
        "LocationDescription %(long)s )" % { "short": shorttext(dbo), "long": longtext(dbo) }
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "stocklocation_ID", "stocklocation", "ID", True)
    add_index(dbo, "stocklocation_LocationName", "stocklocation", "LocationName", True)
    db.execute_dbupdate(dbo, "INSERT INTO stocklocation VALUES (1, '%s', '')" % _("Stores", l))
    sql = "CREATE TABLE stockusage ( ID INTEGER NOT NULL, " \
        "StockUsageTypeID INTEGER NOT NULL, " \
        "StockLevelID INTEGER NOT NULL, " \
        "UsageDate %(date)s NOT NULL, " \
        "Quantity INTEGER NOT NULL, " \
        "Comments %(long)s, " \
        "RecordVersion INTEGER, " \
        "CreatedBy %(short)s, " \
        "CreatedDate %(date)s, " \
        "LastChangedBy %(short)s, " \
        "LastChangedDate %(date)s)" % { "short": shorttext(dbo), "long": longtext(dbo), "date": datetype(dbo) }
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "stockusage_ID", "stockusage", "ID", True)
    add_index(dbo, "stockusage_StockUsageTypeID", "stockusage", "StockUsageTypeID")
    add_index(dbo, "stockusage_StockLevelID", "stockusage", "StockLevelID")
    add_index(dbo, "stockusage_UsageDate", "stockusage", "UsageDate")
    sql = "CREATE TABLE stockusagetype ( ID INTEGER NOT NULL, " \
        "UsageTypeName %(short)s NOT NULL, " \
        "UsageTypeDescription %(long)s )" % { "short": shorttext(dbo), "long": longtext(dbo) }
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "stockusagetype_ID", "stockusagetype", "ID", True)
    add_index(dbo, "stockusagetype_UsageTypeName", "stockusagetype", "UsageTypeName")
    db.execute_dbupdate(dbo, "INSERT INTO stockusagetype VALUES (1, '%s', '')" % _("Administered", l))
    db.execute_dbupdate(dbo, "INSERT INTO stockusagetype VALUES (2, '%s', '')" % _("Consumed", l))
    db.execute_dbupdate(dbo, "INSERT INTO stockusagetype VALUES (3, '%s', '')" % _("Donated", l))
    db.execute_dbupdate(dbo, "INSERT INTO stockusagetype VALUES (4, '%s', '')" % _("Purchased", l))
    db.execute_dbupdate(dbo, "INSERT INTO stockusagetype VALUES (5, '%s', '')" % _("Sold", l))
    db.execute_dbupdate(dbo, "INSERT INTO stockusagetype VALUES (6, '%s', '')" % _("Stocktake", l))
    db.execute_dbupdate(dbo, "INSERT INTO stockusagetype VALUES (7, '%s', '')" % _("Wasted", l))

def update_33501(dbo):
    l = dbo.locale
    add_column(dbo, "animal", "IsPickup", "INTEGER")
    add_column(dbo, "animal", "PickupLocationID", "INTEGER")
    add_index(dbo, "animal_PickupLocationID", "animal", "PickupLocationID")
    sql = "CREATE TABLE pickuplocation ( ID INTEGER NOT NULL, " \
        "LocationName %(short)s NOT NULL, " \
        "LocationDescription %(long)s )" % { "short": shorttext(dbo), "long": longtext(dbo) }
    db.execute_dbupdate(dbo, sql)
    db.execute_dbupdate(dbo, "INSERT INTO pickuplocation VALUES (1, '%s', '')" % _("Shelter", l))

def update_33502(dbo):
    l = dbo.locale
    # Add Transport movement type
    db.execute_dbupdate(dbo, "INSERT INTO lksmovementtype (ID, MovementType) VALUES (13, %s)" % db.ds(_("Transport", l)))

def update_33503(dbo):
    # Add extra vaccination fields and some missing indexes
    add_column(dbo, "animalvaccination", "DateExpires", datetype(dbo))
    add_column(dbo, "animalvaccination", "BatchNumber", shorttext(dbo))
    add_column(dbo, "animalvaccination", "Manufacturer", shorttext(dbo))
    add_index(dbo, "animalvaccination_DateExpires", "animalvaccination", "DateExpires")
    add_index(dbo, "animalvaccination_DateRequired", "animalvaccination", "DateRequired")
    add_index(dbo, "animalvaccination_Manufacturer", "animalvaccination", "Manufacturer")
    add_index(dbo, "animaltest_DateRequired", "animaltest", "DateRequired")

def update_33504(dbo):
    # Add daily email field to reports so they can be emailed to users
    add_column(dbo, "customreport", "DailyEmail", longtext(dbo))
    db.execute_dbupdate(dbo, "UPDATE customreport SET DailyEmail = ''")

def update_33505(dbo):
    # Add daily email hour field to reports
    add_column(dbo, "customreport", "DailyEmailHour", "INTEGER")
    db.execute_dbupdate(dbo, "UPDATE customreport SET DailyEmailHour = -1")

def update_33506(dbo):
    # Add location units field
    add_column(dbo, "internallocation", "Units", longtext(dbo))

def update_33507(dbo):
    l = dbo.locale
    # Add reservation status
    add_column(dbo, "adoption", "ReservationStatusID", "INTEGER")
    add_index(dbo, "adoption_ReservationStatusID", "adoption", "ReservationStatusID")
    sql = "CREATE TABLE reservationstatus ( ID INTEGER NOT NULL, " \
        "StatusName %(short)s NOT NULL, " \
        "StatusDescription %(long)s )" % { "short": shorttext(dbo), "long": longtext(dbo) }
    db.execute_dbupdate(dbo, sql)
    db.execute_dbupdate(dbo, "INSERT INTO reservationstatus VALUES (1, '%s', '')" % _("More Info Needed", l))
    db.execute_dbupdate(dbo, "INSERT INTO reservationstatus VALUES (2, '%s', '')" % _("Pending Vet Check", l))
    db.execute_dbupdate(dbo, "INSERT INTO reservationstatus VALUES (3, '%s', '')" % _("Pending Apartment Verification", l))
    db.execute_dbupdate(dbo, "INSERT INTO reservationstatus VALUES (4, '%s', '')" % _("Pending Home Visit", l))
    db.execute_dbupdate(dbo, "INSERT INTO reservationstatus VALUES (5, '%s', '')" % _("Pending Adoption", l))
    db.execute_dbupdate(dbo, "INSERT INTO reservationstatus VALUES (6, '%s', '')" % _("Changed Mind", l))
    db.execute_dbupdate(dbo, "INSERT INTO reservationstatus VALUES (7, '%s', '')" % _("Denied", l))
    db.execute_dbupdate(dbo, "INSERT INTO reservationstatus VALUES (8, '%s', '')" % _("Approved", l))

def update_33508(dbo):
    # Increase the size of the onlineformfield tooltip as it was short text by mistake
    modify_column(dbo, "onlineformfield", "Tooltip", longtext(dbo))

def update_33600(dbo):
    # Add additionalfield.IsSearchable
    add_column(dbo, "additionalfield", "Searchable", "INTEGER")

def update_33601(dbo):
    # Add animaltransport table
    sql = "CREATE TABLE animaltransport ( ID INTEGER NOT NULL PRIMARY KEY, " \
        "AnimalID INTEGER NOT NULL, " \
        "DriverOwnerID INTEGER NOT NULL, " \
        "PickupOwnerID INTEGER NOT NULL, " \
        "DropoffOwnerID INTEGER NOT NULL, " \
        "PickupDateTime %(date)s NOT NULL, " \
        "DropoffDateTime %(date)s NOT NULL, " \
        "Status INTEGER NOT NULL, " \
        "Miles INTEGER, " \
        "Cost INTEGER NOT NULL, " \
        "CostPaidDate %(date)s NULL, " \
        "Comments %(long)s, " \
        "RecordVersion INTEGER, " \
        "CreatedBy %(short)s, " \
        "CreatedDate %(date)s, " \
        "LastChangedBy %(short)s, " \
        "LastChangedDate %(date)s)" % { "short": shorttext(dbo), "long": longtext(dbo), "date": datetype(dbo) }
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "animaltransport_AnimalID", "animaltransport", "AnimalID")
    add_index(dbo, "animaltransport_DriverOwnerID", "animaltransport", "DriverOwnerID")
    add_index(dbo, "animaltransport_PickupOwnerID", "animaltransport", "PickupOwnerID")
    add_index(dbo, "animaltransport_DropoffOwnerID", "animaltransport", "DropoffOwnerID")
    add_index(dbo, "animaltransport_PickupDateTime", "animaltransport", "PickupDateTime")
    add_index(dbo, "animaltransport_DropoffDateTime", "animaltransport", "DropoffDateTime")
    add_index(dbo, "animaltransport_Status", "animaltransport", "Status")
    # Add the IsDriver column
    add_column(dbo, "owner", "IsDriver", "INTEGER")
    # Convert any existing transport movements to the new format
    tr = db.query(dbo, "SELECT * FROM adoption WHERE MovementType = 13")
    tid = 1
    for m in tr:
        sql = "INSERT INTO animaltransport (ID, AnimalID, DriverOwnerID, PickupOwnerID, DropoffOwnerID, " \
            "PickupDateTime, DropoffDateTime, Status, Miles, Cost, Comments, RecordVersion, CreatedBy, " \
            "CreatedDate, LastChangedBy, LastChangedDate) VALUES ( " \
            "%d, %d, 0, 0, 0, %s, %s, 3, 0, 0, %s, 1, 'update', %s, 'update', %s) " % \
            ( tid, m["ANIMALID"], db.dd(m["MOVEMENTDATE"]), db.dd(m["MOVEMENTDATE"]), db.ds(m["COMMENTS"]), 
              db.dd(m["CREATEDDATE"]), db.dd(m["LASTCHANGEDDATE"]))
        try:
            db.execute_dbupdate(dbo, sql)
            tid += 1
        except Exception,err:
            al.error("failed creating animaltransport row %s: %s" % (str(err), sql), "dbupdate.update_33601", dbo)
    # Remove old transport records and the type
    db.execute_dbupdate(dbo, "DELETE FROM adoption WHERE MovementType = 13")
    db.execute_dbupdate(dbo, "DELETE FROM lksmovementtype WHERE ID = 13")

def update_33602(dbo):
    # Add animalfiguresannual.EntryReasonID
    add_column(dbo, "animalfiguresannual", "EntryReasonID", "INTEGER")
    add_index(dbo, "animalfiguresannual_EntryReasonID", "animalfiguresannual", "EntryReasonID")

def update_33603(dbo):
    # Add additional.DefaultValue
    add_column(dbo, "additionalfield", "DefaultValue", longtext(dbo))

def update_33604(dbo):
    # Add weight field
    add_column(dbo, "animal", "Weight", floattype(dbo))
    add_index(dbo, "animal_Weight", "animal", "Weight")
    # Add followupcomplete fields to animalcontrol
    add_column(dbo, "animalcontrol", "FollowupComplete", "INTEGER")
    add_column(dbo, "animalcontrol", "FollowupComplete2", "INTEGER")
    add_column(dbo, "animalcontrol", "FollowupComplete3", "INTEGER")
    add_index(dbo, "animalcontrol_FollowupComplete", "animalcontrol", "FollowupComplete")
    add_index(dbo, "animalcontrol_FollowupComplete2", "animalcontrol", "FollowupComplete2")
    add_index(dbo, "animalcontrol_FollowupComplete3", "animalcontrol", "FollowupComplete3")
    db.execute_dbupdate(dbo, "UPDATE animalcontrol SET FollowupComplete = 0, FollowupComplete2 = 0, FollowupComplete3 = 0")
    db.execute_dbupdate(dbo, "UPDATE animal SET Weight = 0")

def update_33605(dbo):
    # Add accounts archived flag
    add_column(dbo, "accounts", "Archived", "INTEGER")
    add_index(dbo, "accounts_Archived", "accounts", "ARCHIVED")
    db.execute_dbupdate(dbo, "UPDATE accounts SET Archived = 0")

def update_33606(dbo):
    # Add new transport address fields
    add_column(dbo, "animaltransport", "PickupAddress", shorttext(dbo))
    add_column(dbo, "animaltransport", "PickupTown", shorttext(dbo))
    add_column(dbo, "animaltransport", "PickupCounty", shorttext(dbo))
    add_column(dbo, "animaltransport", "PickupPostcode", shorttext(dbo))
    add_column(dbo, "animaltransport", "DropoffAddress", shorttext(dbo))
    add_column(dbo, "animaltransport", "DropoffTown", shorttext(dbo))
    add_column(dbo, "animaltransport", "DropoffCounty", shorttext(dbo))
    add_column(dbo, "animaltransport", "DropoffPostcode", shorttext(dbo))
    add_index(dbo, "animaltransport_PickupAddress", "animaltransport", "PickupAddress")
    add_index(dbo, "animaltransport_DropoffAddress", "animaltransport", "DropoffAddress")

def update_33607(dbo):
    # Copy addresses from any existing transport records to the new fields
    # (only acts on transport records with blank addresses)
    tr = db.query(dbo, "SELECT animaltransport.ID, " \
        "dro.OwnerAddress AS DRA, dro.OwnerTown AS DRT, dro.OwnerCounty AS DRC, dro.OwnerPostcode AS DRP, " \
        "po.OwnerAddress AS POA, po.OwnerTown AS POT, po.OwnerCounty AS POC, po.OwnerPostcode AS POD " \
        "FROM animaltransport " \
        "INNER JOIN owner dro ON animaltransport.DropoffOwnerID = dro.ID " \
        "INNER JOIN owner po ON animaltransport.PickupOwnerID = po.ID "\
        "WHERE PickupAddress Is Null OR DropoffAddress Is Null")
    for t in tr:
        db.execute_dbupdate(dbo, "UPDATE animaltransport SET " \
            "PickupAddress = %s, PickupTown = %s, PickupCounty = %s, PickupPostcode = %s,  " \
            "DropoffAddress = %s, DropoffTown = %s, DropoffCounty = %s, DropoffPostcode = %s " \
            "WHERE ID = %d" % ( \
            db.ds(t["POA"]), db.ds(t["POT"]), db.ds(t["POC"]), db.ds(t["POD"]), 
            db.ds(t["DRA"]), db.ds(t["DRT"]), db.ds(t["DRC"]), db.ds(t["DRP"]),
            t["ID"] ))

def update_33608(dbo):
    # Add pickuplocationid to incidents
    add_column(dbo, "animalcontrol", "PickupLocationID", "INTEGER")
    add_index(dbo, "animalcontrol_PickupLocationID", "animalcontrol", "PickupLocationID")
    db.execute_dbupdate(dbo, "UPDATE animalcontrol SET PickupLocationID = 0")

def update_33609(dbo):
    l = dbo.locale
    # Add ownerrota table
    sql = "CREATE TABLE ownerrota ( ID INTEGER NOT NULL PRIMARY KEY, " \
        "OwnerID INTEGER NOT NULL, " \
        "StartDateTime %(date)s NOT NULL, " \
        "EndDateTime %(date)s NOT NULL, " \
        "RotaTypeID INTEGER NOT NULL, " \
        "Comments %(long)s, " \
        "RecordVersion INTEGER, " \
        "CreatedBy %(short)s, " \
        "CreatedDate %(date)s, " \
        "LastChangedBy %(short)s, " \
        "LastChangedDate %(date)s)" % { "short": shorttext(dbo), "long": longtext(dbo), "date": datetype(dbo) }
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "ownerrota_OwnerID", "ownerrota", "OwnerID")
    add_index(dbo, "ownerrota_StartDateTime", "ownerrota", "StartDateTime")
    add_index(dbo, "ownerrota_EndDateTime", "ownerrota", "EndDateTime")
    add_index(dbo, "ownerrota_RotaTypeID", "ownerrota", "RotaTypeID")
    # Add lksrotatype table
    sql = "CREATE TABLE lksrotatype ( ID INTEGER NOT NULL PRIMARY KEY, " \
        "RotaType %(short)s NOT NULL)" % { "short": shorttext(dbo) }
    db.execute_dbupdate(dbo, sql)
    db.execute_dbupdate(dbo, "INSERT INTO lksrotatype VALUES (1, %s)" % db.ds(_("Shift", l)))
    db.execute_dbupdate(dbo, "INSERT INTO lksrotatype VALUES (2, %s)" % db.ds(_("Vacation", l)))
    db.execute_dbupdate(dbo, "INSERT INTO lksrotatype VALUES (3, %s)" % db.ds(_("Leave of absence", l)))
    db.execute_dbupdate(dbo, "INSERT INTO lksrotatype VALUES (4, %s)" % db.ds(_("Maternity", l)))
    db.execute_dbupdate(dbo, "INSERT INTO lksrotatype VALUES (5, %s)" % db.ds(_("Personal", l)))
    db.execute_dbupdate(dbo, "INSERT INTO lksrotatype VALUES (6, %s)" % db.ds(_("Rostered day off", l)))
    db.execute_dbupdate(dbo, "INSERT INTO lksrotatype VALUES (7, %s)" % db.ds(_("Sick leave", l)))
    db.execute_dbupdate(dbo, "INSERT INTO lksrotatype VALUES (8, %s)" % db.ds(_("Training", l)))
    db.execute_dbupdate(dbo, "INSERT INTO lksrotatype VALUES (9, %s)" % db.ds(_("Unavailable", l)))

def update_33700(dbo):
    # Add account.CostTypeID
    add_column(dbo, "accounts", "CostTypeID", "INTEGER")
    add_index(dbo, "accounts_CostTypeID", "accounts", "CostTypeID")
    # Add accountstrx.AnimalCostID
    add_column(dbo, "accountstrx", "AnimalCostID", "INTEGER")
    add_index(dbo, "accountstrx_AnimalCostID", "accountstrx", "AnimalCostID")
    # Default values
    db.execute_dbupdate(dbo, "UPDATE accounts SET CostTypeID = 0")
    db.execute_dbupdate(dbo, "UPDATE accountstrx SET AnimalCostID = 0")

def update_33701(dbo):
    # If the user has no online forms, install the default set
    if 0 == db.query_int(dbo, "SELECT COUNT(*) FROM onlineform"):
        install_default_onlineforms(dbo)

def update_33702(dbo):
    # Add media.SignatureHash
    add_column(dbo, "media", "SignatureHash", shorttext(dbo))

def update_33703(dbo):
    # Make stock levels floating point numbers instead
    modify_column(dbo, "stocklevel", "Total", floattype(dbo), "Total::real") 
    modify_column(dbo, "stocklevel", "Balance", floattype(dbo), "Balance::real") 
    modify_column(dbo, "stockusage", "Quantity", floattype(dbo), "Quantity::real") 

def update_33704(dbo):
    # Add the default animalview template
    path = dbo.installpath
    dbfs.create_path(dbo, "/internet", "animalview")
    dbfs.put_file(dbo, "body.html", "/internet/animalview", path + "media/internet/animalview/body.html")
    dbfs.put_file(dbo, "foot.html", "/internet/animalview", path + "media/internet/animalview/foot.html")
    dbfs.put_file(dbo, "head.html", "/internet/animalview", path + "media/internet/animalview/head.html")

def update_33705(dbo):
    # Fix the animalview template to have OpenGraph meta tags
    dbfs.replace_string(dbo, utils.read_text_file(dbo.installpath + "media/internet/animalview/head.html") , "head.html", "/internet/animalview")

def update_33706(dbo):
    # Add users.Signature
    add_column(dbo, "users", "Signature", longtext(dbo))

def update_33707(dbo):
    # Add animalincident table
    sql = "CREATE TABLE animalcontrolanimal (" \
        "AnimalControlID INTEGER NOT NULL, " \
        "AnimalID INTEGER NOT NULL)"
    db.execute_dbupdate(dbo, sql)
    add_index(dbo, "animalcontrolanimal_AnimalControlIDAnimalID", "animalcontrolanimal", "AnimalControlID, AnimalID", True)
    # Copy the existing links from animalcontrol.AnimalID
    for ac in db.query(dbo, "SELECT ID, AnimalID FROM animalcontrol WHERE AnimalID Is Not Null AND AnimalID <> 0"):
        db.execute_dbupdate(dbo, "INSERT INTO animalcontrolanimal (AnimalControlID, AnimalID) VALUES (%d, %d)" % (ac["ID"], ac["ANIMALID"]))
    # Remove the animalid field from animalcontrol
    drop_column(dbo, "animalcontrol", "AnimalID")

def update_33708(dbo):
    # Add basecolour.AdoptAPetColour
    add_column(dbo, "basecolour", "AdoptAPetColour", shorttext(dbo))

def update_33709(dbo):
    l = dbo.locale
    # Move all rota types above shift up 2 places
    db.execute_dbupdate(dbo, "UPDATE lksrotatype SET ID = ID + 10 WHERE ID > 1")
    db.execute_dbupdate(dbo, "UPDATE ownerrota SET RotaTypeID = RotaTypeID + 10 WHERE RotaTypeID > 1")
    # Insert two new types
    db.execute_dbupdate(dbo, "INSERT INTO lksrotatype (ID, RotaType) VALUES (2, %s)" % db.ds(_("Overtime", l)))
    db.execute_dbupdate(dbo, "INSERT INTO lksrotatype (ID, RotaType) VALUES (11, %s)" % db.ds(_("Public Holiday", l)))

def update_33710(dbo):
    # Turn off forcereupload as it should no longer be needed
    p = db.query_string(dbo, "SELECT ItemValue FROM configuration WHERE ItemName LIKE 'PublisherPresets'")
    s = []
    for x in p.split(" "):
        if x != "forcereupload": s.append(x)
    db.execute_dbupdate(dbo, "UPDATE configuration SET ItemValue = '%s' WHERE ItemName LIKE 'PublisherPresets'" % " ".join(s))

def update_33711(dbo):
    # Add ownerdonation.ReceiptNumber
    add_column(dbo, "ownerdonation", "ReceiptNumber", shorttext(dbo))
    add_index(dbo, "ownerdonation_ReceiptNumber", "ownerdonation", "ReceiptNumber")
    # Use ID to prepopulate existing records
    if dbo.dbtype == "POSTGRESQL":
        db.execute_dbupdate(dbo, "UPDATE ownerdonation SET ReceiptNumber = LPAD(ID::text, 8, '0')")
    elif dbo.dbtype == "MYSQL":
        db.execute_dbupdate(dbo, "UPDATE ownerdonation SET ReceiptNumber = LPAD(ID, 8, '0')")
    else:
        db.execute_dbupdate(dbo, "UPDATE ownerdonation SET ReceiptNumber = ID")

def update_33712(dbo):
    # Add ownerdonation Sales Tax/VAT fields
    add_column(dbo, "ownerdonation", "IsVAT", "INTEGER")
    add_column(dbo, "ownerdonation", "VATRate", floattype(dbo))
    add_column(dbo, "ownerdonation", "VATAmount", "INTEGER")
    add_index(dbo, "ownerdonation_IsVAT", "ownerdonation", "IsVAT")
    db.execute_dbupdate(dbo, "UPDATE ownerdonation SET IsVAT=0, VATRate=0, VATAmount=0")

def update_33713(dbo):
    # Create animal flags table
    sql = "CREATE TABLE lkanimalflags ( ID INTEGER NOT NULL, " \
        "Flag %s NOT NULL)" % shorttext(dbo)
    db.execute_dbupdate(dbo, sql)
    # Add additionalflags field to animal
    add_column(dbo, "animal", "AdditionalFlags", longtext(dbo))
    # Add IsCourtesy to animal
    add_column(dbo, "animal", "IsCourtesy", "INTEGER")
    db.execute_dbupdate(dbo, "UPDATE animal SET IsCourtesy=0, AdditionalFlags=''")

def update_33714(dbo):
    # Remove activeuser table (superceded by memcache)
    db.execute_dbupdate(dbo, "DROP TABLE activeuser")

def update_33715(dbo):
    # Add owner.FosterCapacity field
    add_column(dbo, "owner", "FosterCapacity", "INTEGER")
    db.execute_dbupdate(dbo, "UPDATE owner SET FosterCapacity=0")
    db.execute_dbupdate(dbo, "UPDATE owner SET FosterCapacity=1 WHERE IsFosterer=1")

def update_33716(dbo):
    # Switch ui-lightness and smoothness to the new asm replacement theme
    db.execute_dbupdate(dbo, "UPDATE configuration SET itemvalue='asm' WHERE itemvalue = 'smoothness' OR itemvalue = 'ui-lightness'")

def update_33717(dbo):
    # Add default colour mappings to existing colours if they
    # have not been mapped already
    defmap = {
        1: "Black",
        2: "White",
        3: "Black - with White",
        4: "Red/Golden/Orange/Chestnut",
        5: "White - with Black",
        6: "Tortoiseshell",
        7: "Brown Tabby",
        8: "Tan/Yellow/Fawn",
        9: "Black - with Tan, Yellow or Fawn",
        10: "Black - with Tan, Yellow or Fawn",
        11: "Brown/Chocolate",
        12: "Brown/Chocolate - with Black",
        13: "Brown/Chocolate - with White",
        14: "Brindle",
        15: "Brindle",
        16: "Brindle - with White",
        17: "Black - with Tan, Yellow or Fawn",
        18: "White - with Tan, Yelow or Fawn",
        19: "Tricolor (Tan/Brown & Black & White)",
        20: "Brown/Chocolate",
        21: "Brown/Chocolate - with White",
        22: "Brown/Chocolate - with White",
        23: "White",
        24: "White - with Tan, Yellow or Fawn",
        26: "White - with Tan, Yellow or Fawn",
        27: "Tortoiseshell",
        28: "Brown Tabby",
        29: "Red/Golden/Orange/Chestnut - with White",
        30: "Gray/Blue/Silver/Salt & Pepper",
        31: "Gray/Silver/Salt & Pepper - with White",
        32: "Gray/Silver/Salt & Pepper - with White",
        33: "Tortoiseshell",
        35: "Brown/Chocolate - with White",
        36: "Gray or Blue",
        37: "White",
        38: "Tan/Yellow/Fawn",
        39: "Tan/Yellow/Fawn",
        40: "Brown/Chocolate - with White",
        41: "Green",
        42: "Red/Golden/Orange/Chestnut",
        43: "Tortoiseshell",
        44: "Tortoiseshell",
        45: "Brown/Chocolate",
        46: "Tortoiseshell",
        47: "Red/Golden/Orange/Chestnut",
        48: "Tortoiseshell",
        49: "Tan/Yellow/Fawn",
        50: "Tortoiseshell",
        51: "Red/Golden/Orange/Chestnut",
        52: "Red/Golden/Orange/Chestnut",
        53: "Gray/Blue/Silver/Salt & Pepper",
        54: "Tortoiseshell",
        55: "Red/Golden/Orange/Chestnut",
        56: "Tan/Yellow/Fawn",
        57: "Gray/Blue/Silver/Salt & Pepper",
        58: "Red/Golden/Orange/Chestnut",
        59: "Tortoiseshell",
    }
    for c in db.query(dbo, "SELECT ID FROM basecolour WHERE ID <= 59 AND (AdoptAPetColour Is Null OR AdoptAPetColour = '')"):
        if defmap.has_key(c["ID"]):
            db.execute_dbupdate(dbo, "UPDATE basecolour SET AdoptAPetColour=%s WHERE ID=%d" % (db.ds(defmap[c["ID"]]), c["ID"]))

def update_33718(dbo):
    # Add TotalTimeOnShelter, TotalDaysOnShelter
    add_column(dbo, "animal", "TotalDaysOnShelter", "INTEGER")
    add_column(dbo, "animal", "TotalTimeOnShelter", shorttext(dbo))
    db.execute_dbupdate(dbo, "UPDATE animal SET TotalDaysOnShelter=0, TotalTimeOnShelter=''")

def update_33800(dbo):
    # Add IsRetired field to lookups
    retirablelookups = [ "animaltype", "basecolour", "breed", "citationtype", "costtype", 
        "deathreason", "diet", "donationpayment", "donationtype", "entryreason", "incidentcompleted", 
        "incidenttype", "internallocation", "licencetype", "logtype", "pickuplocation", 
        "reservationstatus", "species", "stocklocation", "stockusagetype", "testtype", 
        "testresult", "traptype", "vaccinationtype", "voucher" ]
    for t in retirablelookups:
        add_column(dbo, t, "IsRetired", "INTEGER")
        db.execute_dbupdate(dbo, "UPDATE %s SET IsRetired = 0" % t)

def update_33801(dbo):
    # Add animal.PickupAddress, animalvaccination.AdministeringVetID and animalmedicaltreatment.AdministeringVetID
    add_column(dbo, "animal", "PickupAddress", shorttext(dbo))
    add_column(dbo, "animalmedicaltreatment", "AdministeringVetID", "INTEGER")
    add_column(dbo, "animalvaccination", "AdministeringVetID", "INTEGER")
    add_index(dbo, "animal_PickupAddress", "animal", "PickupAddress")
    add_index(dbo, "animalmedicaltreatment_AdministeringVetID", "animalmedicaltreatment", "AdministeringVetID")
    add_index(dbo, "animalvaccination_AdministeringVetID", "animalvaccination", "AdministeringVetID")
    db.execute_dbupdate(dbo, "UPDATE animal SET PickupAddress = ''")
    db.execute_dbupdate(dbo, "UPDATE animalmedicaltreatment SET AdministeringVetID = 0")
    db.execute_dbupdate(dbo, "UPDATE animalvaccination SET AdministeringVetID = 0")

def update_33802(dbo):
    # Remove the Incident - Citation link from additional fields as it's no longer valid
    db.execute_dbupdate(dbo, "DELETE FROM lksfieldlink WHERE ID = 19")
    # Move PickedUpByOwnerID to BroughtInByOwnerID and remove it
    db.execute_dbupdate(dbo, "UPDATE animal SET BroughtInByOwnerID = PickedUpByOwnerID WHERE BroughtInByOwnerID = 0 AND PickedUpByOwnerID <> 0")
    drop_column(dbo, "animal", "PickedUpByOwnerID")

def update_33803(dbo):
    # Install new incident information template
    path = dbo.installpath
    dbfs.put_file(dbo, "incident_information.html", "/templates", path + "media/templates/incident_information.html")

