
import asm3.al
import asm3.animal
import asm3.animalcontrol
import asm3.financial
import asm3.lostfound
import asm3.medical
import asm3.movement
import asm3.onlineform
import asm3.person
import asm3.waitinglist
import asm3.configuration
import asm3.db
import asm3.dbfs
import asm3.reports
import asm3.smcom
import asm3.utils
from asm3.i18n import _
from asm3.typehints import Database, Dict, Generator, List, Tuple

import os, sys

VERSIONS = ( 
    2870, 3000, 3001, 3002, 3003, 3004, 3005, 3006, 3007, 3008, 3009, 3010, 3050,
    3051, 3081, 3091, 3092, 3093, 3094, 3110, 3111, 3120, 3121, 3122, 3123, 3200,
    3201, 3202, 3203, 3204, 3210, 3211, 3212, 3213, 3214, 3215, 3216, 3217, 
    3220, 3221, 3222, 3223, 3224, 3225, 3300, 3301, 3302, 3303, 3304, 3305, 3306,
    3307, 3308, 3309, 
    33010, 33011, 33012, 33013, 33014, 33015, 33016, 33017, 33018, 33019, 33101, 
    33102, 33104, 33105, 33106, 33201, 33202, 33203, 33204, 33205, 33206, 33300, 
    33301, 33302, 33303, 33304, 33305, 33306, 33307, 33308, 33309, 33310, 33311, 
    33312, 33313, 33314, 33315, 33316, 33401, 33402, 33501, 33502, 33503, 33504, 
    33505, 33506, 33507, 33508, 33600, 33601, 33602, 33603, 33604, 33605, 33606, 
    33607, 33608, 33609, 33700, 33701, 33702, 33703, 33704, 33705, 33706, 33707, 
    33708, 33709, 33710, 33711, 33712, 33713, 33714, 33715, 33716, 33717, 33718, 
    33800, 33801, 33802, 33803, 33900, 33901, 33902, 33903, 33904, 33905, 33906, 
    33907, 33908, 33909, 33911, 33912, 33913, 33914, 33915, 33916, 34000, 34001, 
    34002, 34003, 34004, 34005, 34006, 34007, 34008, 34009, 34010, 34011, 34012,
    34013, 34014, 34015, 34016, 34017, 34018, 34019, 34020, 34021, 34022, 34100,
    34101, 34102, 34103, 34104, 34105, 34106, 34107, 34108, 34109, 34110, 34111,
    34112, 34200, 34201, 34202, 34203, 34204, 34300, 34301, 34302, 34303, 34304,
    34305, 34306, 34400, 34401, 34402, 34403, 34404, 34405, 34406, 34407, 34408,
    34409, 34410, 34411, 34500, 34501, 34502, 34503, 34504, 34505, 34506, 34507,
    34508, 34509, 34510, 34511, 34512, 34600, 34601, 34602, 34603, 34604, 34605,
    34606, 34607, 34608, 34609, 34611, 34700, 34701, 34702, 34703, 34704, 34705,
    34706, 34707, 34708, 34709, 34800, 34801, 34802, 34803, 34804, 34805, 34806,
    34807, 34808, 34809, 34810, 34811, 34812, 34813, 34900, 34901, 34902, 34903,
    34904, 34905, 34906, 34907
)

LATEST_VERSION = VERSIONS[-1]

# All ASM3 tables
TABLES = ( "accounts", "accountsrole", "accountstrx", "additional", "additionalfield",
    "adoption", "animal", "animalboarding", "animalcontrol", "animalcontrolanimal", "animalcontrolrole", "animalcost",
    "animaldiet", "animalentry", "animalfigures", "animalfiguresannual",  
    "animalfound", "animalcontrolanimal", "animallitter", "animallocation", "animallost", "animallostfoundmatch", 
    "animalmedical", "animalmedicaltreatment", "animalname", "animalpublished", 
    "animaltype", "animaltest", "animaltransport", "animalvaccination", "animalwaitinglist", "audittrail", 
    "basecolour", "breed", "citationtype", "clinicappointment", "clinicinvoiceitem", "configuration", 
    "costtype", "customreport", "customreportrole", "dbfs", "deathreason", "deletion", "diary", 
    "diarytaskdetail", "diarytaskhead", "diet", "donationpayment", "donationtype", 
    "entryreason", "event", "eventanimal", "incidentcompleted", "incidenttype", "internallocation", 
    "jurisdiction", "licencetype", "lkanimalflags", "lkboardingtype", "lkclinictype", "lkcoattype", "lkmediaflags", 
    "lkownerflags", "lksaccounttype", "lksclinicstatus", "lksdiarylink", "lksdonationfreq", "lksentrytype",
    "lksex", "lksfieldlink", "lksfieldtype", "lksize", "lksloglink", "lksmedialink", "lksmediatype", "lksmovementtype", 
    "lksoutcome", "lksposneg", "lksrotatype", "lksyesno", "lksynun", "lksynunk", "lkstransportstatus", "lkurgency", 
    "lkwaitinglistremoval", "lkworktype", 
    "log", "logtype", "media", "medicalprofile", "messages", "onlineform", 
    "onlineformfield", "onlineformincoming", "owner", "ownercitation", "ownerdonation", "ownerinvestigation", 
    "ownerlicence", "ownerlookingfor", "ownerrole", "ownerrota", "ownertraploan", "ownervoucher", "pickuplocation", "publishlog", 
    "reservationstatus", "role", "site", "species", "stocklevel", "stocklocation", "stockusage", "stockusagetype", 
    "templatedocument", "templatehtml", "testtype", "testresult", "transporttype", "traptype", "userrole", "users", 
    "vaccinationtype", "voucher" )

# ASM2_COMPATIBILITY This is used for dumping tables in ASM2/HSQLDB format. 
# These are the tables present in ASM2. users is not included due to the
# difference in password formats.
TABLES_ASM2 = ( "accounts", "accountstrx", "additional", "additionalfield",
    "adoption", "animal", "animalcost", "animaldiet", "animalfound", "animallitter", "animallost", 
    "animalmedical", "animalmedicaltreatment", "animalname", "animaltype", "animaltest", "animalvaccination", 
    "animalwaitinglist", "audittrail", "basecolour", "breed", "configuration", "costtype", 
    "customreport", "dbfs", "deathreason", "diary", "diarytaskdetail", "diarytaskhead", "diet", 
    "donationtype", "entryreason", "internallocation", "lkcoattype", "lksaccounttype", "lksdiarylink", 
    "lksdonationfreq", "lksex", "lksfieldlink", "lksfieldtype", "lksize", "lksloglink", "lksmedialink", 
    "lksmediatype", "lksmovementtype", "lksposneg", "lksyesno", "lksynun", "lkurgency", "log", 
    "logtype", "media", "medicalprofile", "owner", "ownerdonation", "ownervoucher", "primarykey", 
    "species", "vaccinationtype", "voucher" )

# Tables that don't have an ID column (we don't create sequences for these tables for supporting dbs like postgres)
TABLES_NO_ID_COLUMN = ( "accountsrole", "additional", "audittrail", "animalcontrolanimal", 
    "animalcontrolrole", "animallostfoundmatch", "animalpublished", "configuration", "customreportrole", 
    "deletion", "onlineformincoming", "ownerlookingfor", "ownerrole", "userrole" )

# Tables that contain data rather than lookups - used by reset_db
# to determine which tables to delete data from
TABLES_DATA = ( "accountsrole", "accountstrx", "additional", "adoption", 
    "animal", "animalboarding", "animalcontrol", "animalcontrolanimal","animalcontrolrole", 
    "animallocation", "animallostfoundmatch", "animalpublished", 
    "animalcost", "animaldiet", "animalentry", "animalfigures", "animalfiguresannual", 
    "animalfound", "animallitter", "animallost", "animalmedical", "animalmedicaltreatment", "animalname",
    "animaltest", "animaltransport", "animalvaccination", "animalwaitinglist", "audittrail", 
    "clinicappointment", "clinicinvoiceitem", "deletion", "diary", "event", "eventanimal", 
    "log", "ownerlookingfor", "publishlog", "media", "messages", "owner", "ownercitation", 
    "ownerdonation", "ownerinvestigation", "ownerlicence", "ownerrole", "ownerrota", "ownertraploan", "ownervoucher", 
    "stocklevel", "stockusage" )

# Tables that contain lookup data. used by dump with includeLookups
TABLES_LOOKUP = ( "accounts", "additionalfield", "animaltype", "basecolour", "breed", "citationtype", 
    "costtype", "deathreason", "diarytaskdetail", "diarytaskhead", "diet", "donationpayment", 
    "donationtype", "entryreason", "incidentcompleted", "incidenttype", "internallocation", "jurisdiction", 
    "licencetype", "lkanimalflags", "lkboardingtype", "lkclinictype", "lkcoattype", "lkmediaflags", "lkownerflags", 
    "lksaccounttype", "lksclinicstatus", "lksdiarylink", "lksdonationfreq", "lksentrytype", "lksex", "lksfieldlink", 
    "lksfieldtype", "lksize", "lksloglink", "lksmedialink", "lksmediatype", "lksmovementtype", "lksoutcome", 
    "lksposneg", "lksrotatype", "lksyesno", "lksynun", "lksynunk", "lkstransportstatus", "lkurgency", 
    "lkwaitinglistremoval", "lkworktype", 
    "logtype", "medicalprofile", "onlineform", "onlineformfield", "pickuplocation", "reservationstatus", "site", 
    "stocklocation", "stockusagetype", "species", "templatedocument", "templatehtml", "testtype", "testresult", 
    "transporttype", "traptype", "vaccinationtype", "voucher" )

VIEWS = ( "v_adoption", "v_animal", "v_animalcontrol", "v_animalfound", "v_animallost", 
    "v_animalmedicalcombined", "v_animalmedicaltreatment", "v_animaltest", "v_animalvaccination", 
    "v_animalwaitinglist", "v_owner", "v_ownercitation", "v_ownerdonation", "v_ownerlicence", 
    "v_ownertraploan", "v_ownervoucher" )

def sql_structure(dbo: Database) -> str:
    """
    Returns the SQL necessary to create the database for the type specified
    """
    def table(name: str, fields: Tuple[str], includechange: bool = True, changenullable: bool = False) -> str:
        if includechange:
            cf = (fint("RecordVersion", True),
                fstr("CreatedBy", changenullable),
                fdate("CreatedDate", changenullable),
                fstr("LastChangedBy", changenullable),
                fdate("LastChangedDate", changenullable))
            return "%s;\n" % dbo.ddl_add_table(name, ",".join(fields + cf))
        return "%s;\n" % dbo.ddl_add_table(name, ",".join(fields))
    def index(name: str, table: str, fieldlist: Tuple[str], unique: bool = False, partial: bool = False) -> str:
        return "%s;\n" % dbo.ddl_add_index(name, table, fieldlist, unique, partial)
    def field(name: str, ftype: str = dbo.type_integer, nullable: bool = True, pk: bool = False) -> str:
        return dbo.ddl_add_table_column(name, ftype, nullable, pk)
    def fid() -> str:
        return field("ID", dbo.type_integer, False, True)
    def fint(name: str, nullable: bool = False) -> str:
        return field(name, dbo.type_integer, nullable, False)
    def ffloat(name: str, nullable: bool = False) -> str:
        return field(name, dbo.type_float, nullable, False)
    def fdate(name: str, nullable: bool = False) -> str:
        return field(name, dbo.type_datetime, nullable, False)
    def fstr(name: str, nullable: bool = False) -> str:
        return field(name, dbo.type_shorttext, nullable, False)
    def flongstr(name: str, nullable: bool = True) -> str:
        return field(name, dbo.type_longtext, nullable, False)
    def fclob(name: str, nullable: bool = True) -> str:
        return field(name, dbo.type_clob, nullable, False)

    sql = ""
    sql += table("accounts", (
        fid(),
        fstr("Code"),
        fstr("Description"),
        fint("Archived", True),
        fint("AccountType"),
        fint("CostTypeID", True), # ASM2_COMPATIBILITY - replaced by costtype.AccountID
        fint("DonationTypeID", True) )) # ASM2_COMPATIBILITY - replaced by donationtype.AccountID
    sql += index("accounts_Code", "accounts", "Code", False)
    sql += index("accounts_Archived", "accounts", "Archived")
 
    sql += table("accountsrole", (
        fint("AccountID"),
        fint("RoleID"),
        fint("CanView"),
        fint("CanEdit") ), False)
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
        fint("NewRecord"),
        fint("Searchable", True),
        fint("Hidden", True) ), False)
    sql += index("additionalfield_LinkType", "additionalfield", "LinkType")

    sql += table("additional", (
        fint("LinkType"),
        fint("LinkID"),
        fint("AdditionalFieldID"),
        flongstr("Value") ), False)
    sql += index("additional_LinkTypeIDAdd", "additional", "LinkType, LinkID, AdditionalFieldID", True)
    sql += index("additional_LinkTypeID", "additional", "LinkType, LinkID")
    sql += index("additional_LinkID", "additional", "LinkID")

    sql += table("adoption", (
        fid(),
        fstr("AdoptionNumber"),
        fint("AnimalID"),
        fint("OwnerID", True),
        fint("RetailerID", True),
        fint("OriginalRetailerMovementID", True),
        fint("EventID", True),
        fdate("MovementDate", True),
        fint("MovementType"),
        fdate("ReturnDate", True),
        fint("ReturnedReasonID"),
        fstr("InsuranceNumber", True),
        flongstr("ReasonForReturn"),
        fint("ReturnedByOwnerID", True),
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
    sql += index("adoption_ReturnedByOwnerID", "adoption", "ReturnedByOwnerID")
    sql += index("adoption_TrialEndDate", "adoption", "TrialEndDate")
    sql += index("adoption_EventID", "adoption", "EventID")

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
        fstr("ExtraIDs", True),
        fint("UniqueCodeID", True),
        fint("YearCodeID", True),
        fdate("SmartTagSentDate", True), # ASM2_COMPATIBILITY
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
        fstr("Identichip2Number", True),
        fdate("Identichip2Date", True),
        fint("Tattoo"),
        fstr("TattooNumber"),
        fdate("TattooDate", True),
        fint("SmartTag"),
        fstr("SmartTagNumber", True),
        fdate("SmartTagDate", True),
        fint("SmartTagType"),
        fint("Neutered"),
        fdate("NeuteredDate", True),
        fint("NeuteredByVetID", True), 
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
        flongstr("PopupWarning", True),
        fint("OwnersVetID"),
        fint("CurrentVetID"),
        fint("OwnerID", True),
        fint("OriginalOwnerID"),
        fint("BroughtInByOwnerID"),
        fint("AdoptionCoordinatorID", True),
        flongstr("ReasonForEntry"),
        flongstr("ReasonNO"),
        fdate("DateBroughtIn"),
        fint("EntryTypeID", True),
        fint("EntryReasonID"),
        fint("AsilomarIsTransferExternal", True),
        fint("AsilomarIntakeCategory", True),
        fint("AsilomarOwnerRequestedEuthanasia", True),
        fint("IsPickup", True),
        fint("PickupLocationID", True),
        fstr("PickupAddress", True),
        fint("JurisdictionID", True),
        flongstr("HealthProblems"),
        fint("PutToSleep"),
        flongstr("PTSReason"),
        fint("PTSReasonID"),
        fint("IsCourtesy", True),
        fint("IsDOA"),
        fint("IsTransfer"), # ASM2_COMPATIBILITY
        fint("IsGoodWithCats"),
        fint("IsGoodWithDogs"),
        fint("IsGoodWithChildren"),
        fint("IsHouseTrained"),
        fint("IsCrateTrained", True),
        fint("IsGoodWithElderly", True),
        fint("IsGoodTraveller", True),
        fint("IsGoodOnLead", True),
        fint("EnergyLevel", True),
        fint("IsNotAvailableForAdoption"),
        fint("IsNotForRegistration", True),
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
        fint("Adoptable", True),
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
        fstr("AgeGroupActiveMovement", True),
        fint("DailyBoardingCost", True),
        fstr("AnimalAge", True) ))
    sql += index("animal_AnimalShelterCode", "animal", "ShelterCode", True)
    sql += index("animal_AnimalExtraIDs", "animal", "ExtraIDs")
    sql += index("animal_AnimalTypeID", "animal", "AnimalTypeID")
    sql += index("animal_AnimalName", "animal", "AnimalName")
    sql += index("animal_AnimalSpecies", "animal", "SpeciesID")
    sql += index("animal_Archived", "animal", "Archived")
    sql += index("animal_ActiveMovementID", "animal", "ActiveMovementID")
    sql += index("animal_ActiveMovementDate", "animal", "ActiveMovementDate")
    sql += index("animal_ActiveMovementReturn", "animal", "ActiveMovementReturn")
    sql += index("animal_AcceptanceNumber", "animal", "AcceptanceNumber")
    sql += index("animal_ActiveMovementType", "animal", "ActiveMovementType")
    sql += index("animal_Adoptable", "animal", "Adoptable")
    sql += index("animal_AdoptionCoordinatorID", "animal", "AdoptionCoordinatorID")
    sql += index("animal_AgeGroup", "animal", "AgeGroup")
    sql += index("animal_BaseColourID", "animal", "BaseColourID")
    sql += index("animal_BondedAnimalID", "animal", "BondedAnimalID")
    sql += index("animal_BondedAnimal2ID", "animal", "BondedAnimal2ID")
    sql += index("animal_BreedID", "animal", "BreedID")
    sql += index("animal_Breed2ID", "animal", "Breed2ID")
    sql += index("animal_BreedName", "animal", "BreedName")
    sql += index("animal_BroughtInByOwnerID", "animal", "BroughtInByOwnerID")
    sql += index("animal_CoatType", "animal", "CoatType")
    sql += index("animal_CreatedBy", "animal", "CreatedBy")
    sql += index("animal_CreatedDate", "animal", "CreatedDate")
    sql += index("animal_OwnerID", "animal", "OwnerID")
    sql += index("animal_CurrentVetID", "animal", "CurrentVetID")
    sql += index("animal_DateBroughtIn", "animal", "DateBroughtIn")
    sql += index("animal_DeceasedDate", "animal", "DeceasedDate")
    sql += index("animal_DiedOffShelter", "animal", "DiedOffShelter")
    sql += index("animal_EntryReasonID", "animal", "EntryReasonID")
    sql += index("animal_EntryTypeID", "animal", "EntryTypeID")
    sql += index("animal_IdentichipNumber", "animal", "IdentichipNumber")
    sql += index("animal_Identichip2Number", "animal", "Identichip2Number")
    sql += index("animal_JurisdictionID", "animal", "JurisdictionID")
    sql += index("animal_LastChangedDate", "animal", "LastChangedDate")
    sql += index("animal_MostRecentEntryDate", "animal", "MostRecentEntryDate")
    sql += index("animal_Neutered", "animal", "Neutered")
    sql += index("animal_NeuteredByVetID", "animal", "NeuteredByVetID")
    sql += index("animal_NonShelterAnimal", "animal", "NonShelterAnimal")
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

    sql += table("animalboarding", (
        fid(),
        fint("AnimalID"),
        fint("OwnerID", True),
        fint("BoardingTypeID"),
        fdate("InDateTime"),
        fdate("OutDateTime"),
        fint("Days", True),
        fint("DailyFee", True),
        fint("ShelterLocation"),
        fstr("ShelterLocationUnit"),
        flongstr("Comments", True) ))
    sql += index("animalboarding_AnimalID", "animalboarding", "AnimalID")
    sql += index("animalboarding_OwnerID", "animalboarding", "OwnerID")
    sql += index("animalboarding_BoardingTypeID", "animalboarding", "BoardingTypeID")
    sql += index("animalboarding_InDateTime", "animalboarding", "InDateTime")
    sql += index("animalboarding_OutDateTime", "animalboarding", "OutDateTime")

    sql += table("animalcontrol", (
        fid(),
        fstr("IncidentCode", True),
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
        fint("JurisdictionID", True),
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
        fint("SiteID", True),
        fint("OwnerID", True),
        fint("Owner2ID", True),
        fint("Owner3ID", True),
        fint("AnimalID", True),
        flongstr("AnimalDescription", True),
        fint("SpeciesID", True),
        fint("Sex", True),
        fstr("AgeGroup", True) ))
    sql += index("animalcontrol_IncidentCode", "animalcontrol", "IncidentCode")
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
    sql += index("animalcontrol_JurisdictionID", "animalcontrol", "JurisdictionID")
    sql += index("animalcontrol_PickupLocationID", "animalcontrol", "PickupLocationID")
    sql += index("animalcontrol_AnimalID", "animalcontrol", "AnimalID")
    sql += index("animalcontrol_OwnerID", "animalcontrol", "OwnerID")
    sql += index("animalcontrol_Owner2ID", "animalcontrol", "Owner2ID")
    sql += index("animalcontrol_Owner3ID", "animalcontrol", "Owner3ID")
    sql += index("animalcontrol_SiteID", "animalcontrol", "SiteID")
    sql += index("animalcontrol_VictimID", "animalcontrol", "VictimID")

    sql += table("animalcontrolanimal", (
        fint("AnimalControlID"),
        fint("AnimalID") ), False)
    sql += index("animalcontrolanimal_AnimalControlIDAnimalID", "animalcontrolanimal", "AnimalControlID, AnimalID", True)

    sql += table("animalcontrolrole", (
        fint("AnimalControlID"),
        fint("RoleID"),
        fint("CanView"),
        fint("CanEdit") ), False)
    sql += index("animalcontrolrole_AnimalControlIDRoleID", "animalcontrolrole", "AnimalControlID, RoleID", True)

    sql += table("animalcost", (
        fid(),
        fint("AnimalID"),
        fint("CostTypeID"),
        fdate("CostDate"),
        fdate("CostPaidDate", True),
        fint("CostAmount"),
        fint("OwnerID", True),
        fstr("InvoiceNumber", True),
        flongstr("Description", False) ))
    sql += index("animalcost_AnimalID", "animalcost", "AnimalID")
    sql += index("animalcost_CostTypeID", "animalcost", "CostTypeID")
    sql += index("animalcost_CostDate", "animalcost", "CostDate")
    sql += index("animalcost_CostPaidDate", "animalcost", "CostPaidDate")
    sql += index("animalcost_OwnerID", "animalcost", "OwnerID")
    sql += index("animalcost_InvoiceNumber", "animalcost", "InvoiceNumber")

    sql += table("animaldiet", (
        fid(),
        fint("AnimalID"),
        fint("DietID"),
        fdate("DateStarted"),
        flongstr("Comments") ))
    sql += index("animaldiet_AnimalID", "animaldiet", "AnimalID")
    sql += index("animaldiet_DietID", "animaldiet", "DietID")

    sql += table("animalentry", (
        fid(),
        fint("AnimalID"),
        fstr("ShelterCode"),
        fstr("ShortCode"),
        fdate("EntryDate"),
        fint("EntryTypeID"),
        fint("EntryReasonID"),
        fint("AdoptionCoordinatorID", True),
        fint("BroughtInByOwnerID", True),
        fint("OriginalOwnerID", True),
        fint("AsilomarIntakeCategory", True),
        fint("JurisdictionID", True),
        fint("IsTransfer"),
        fint("AsilomarIsTransferExternal", True),
        fdate("HoldUntilDate", True),
        fint("IsPickup"),
        fint("PickupLocationID", True),
        fstr("PickupAddress", True),
        flongstr("ReasonNO", True),
        flongstr("ReasonForEntry", True) ))
    sql += index("animalentry_AnimalID", "animalentry", "AnimalID")

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
        fstr("MicrochipNumber", True),
        fint("OwnerID"),
        fdate("ReturnToOwnerDate", True),
        flongstr("Comments") ))
    sql += index("animalfound_ReturnToOwnerDate", "animalfound", "ReturnToOwnerDate")
    sql += index("animalfound_AnimalTypeID", "animalfound", "AnimalTypeID")
    sql += index("animalfound_AreaFound", "animalfound", "AreaFound")
    sql += index("animalfound_AreaPostcode", "animalfound", "AreaPostcode")
    sql += index("animalfound_MicrochipNumber", "animalfound", "MicrochipNumber")

    sql += table("animallitter", (
        fid(),
        fint("ParentAnimalID"),
        fint("SpeciesID"),
        fdate("Date"),
        fstr("AcceptanceNumber", True),
        fint("CachedAnimalsLeft"),
        fdate("InvalidDate", True),
        fint("NumberInLitter"),
        flongstr("Comments")), True, True)
    
    sql += table("animallocation", (
        fid(),
        fint("AnimalID"),
        fdate("Date"),
        fint("FromLocationID"),
        fstr("FromUnit"), 
        fint("ToLocationID"),
        fstr("ToUnit"), 
        fint("PrevAnimalLocationID", True),
        fstr("MovedBy"),
        fstr("Description")), False)
    sql += index("animallocation_AnimalID", "animallocation", "AnimalID")
    sql += index("animallocation_FromLocationID", "animallocation", "FromLocationID")
    sql += index("animallocation_ToLocationID", "animallocation", "ToLocationID")
    sql += index("animallocation_PrevAnimalLocationID", "animallocation", "PrevAnimalLocationID")

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
        fstr("MicrochipNumber", True),
        fint("OwnerID"),
        flongstr("Comments") ))
    sql += index("animallost_DateFound", "animallost", "DateFound")
    sql += index("animallost_AnimalTypeID", "animallost", "AnimalTypeID")
    sql += index("animallost_AreaLost", "animallost", "AreaLost")
    sql += index("animallost_AreaPostcode", "animallost", "AreaPostcode")
    sql += index("animallost_MicrochipNumber", "animallost", "MicrochipNumber")

    sql += table("animallostfoundmatch", (
        fint("AnimalLostID"),
        fint("AnimalFoundID", True),
        fint("AnimalID", True),
        fstr("LostContactName", True),
        fstr("LostContactNumber", True),
        fstr("LostArea", True),
        fstr("LostPostcode", True),
        fstr("LostAgeGroup", True),
        fint("LostSex", True),
        fint("LostSpeciesID", True),
        fint("LostBreedID", True),
        fstr("LostMicrochipNumber", True),
        flongstr("LostFeatures", True),
        fint("LostBaseColourID", True),
        fdate("LostDate", True),
        fstr("FoundContactName", True),
        fstr("FoundContactNumber", True),
        fstr("FoundArea", True),
        fstr("FoundPostcode", True),
        fstr("FoundAgeGroup", True),
        fint("FoundSex", True),
        fint("FoundSpeciesID", True),
        fint("FoundBreedID", True),
        fstr("FoundMicrochipNumber", True),
        flongstr("FoundFeatures", True),
        fint("FoundBaseColourID", True),
        fdate("FoundDate", True),
        fint("MatchPoints") ), False)

    sql += index("animallostfoundmatch_AnimalLostID", "animallostfoundmatch", "AnimalLostID")
    sql += index("animallostfoundmatch_AnimalFoundID", "animallostfoundmatch", "AnimalFoundID")
    sql += index("animallostfoundmatch_AnimalID", "animallostfoundmatch", "AnimalID")

    sql += table("animalmedical", (
        fid(),
        fint("AnimalID"),
        fint("MedicalProfileID"),
        fstr("TreatmentName"),
        fdate("StartDate"),
        fstr("Dosage", True),
        fint("Cost"),
        fint("CostPerTreatment", True),
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
        fint("AdministeringVetID", True),
        fdate("DateOfTest", True),
        fdate("DateRequired"),
        fint("Cost"),
        fdate("CostPaidDate", True),
        flongstr("Comments") ))
    sql += index("animaltest_AdministeringVetID", "animaltest", "AdministeringVetID")
    sql += index("animaltest_AnimalID", "animaltest", "AnimalID")
    sql += index("animaltest_DateRequired", "animaltest", "DateRequired")
    sql += index("animaltest_CostPaidDate", "animaltest", "CostPaidDate")

    sql += table("animaltransport", (
        fid(),
        fstr("TransportReference", True),
        fint("AnimalID"),
        fint("TransportTypeID"),
        fint("DriverOwnerID"),
        fint("PickupOwnerID"),
        fstr("PickupAddress", True),
        fstr("PickupTown", True),
        fstr("PickupCounty", True),
        fstr("PickupPostcode", True),
        fstr("PickupCountry", True),
        fdate("PickupDateTime"),
        fint("DropoffOwnerID"),
        fstr("DropoffAddress", True),
        fstr("DropoffTown", True),
        fstr("DropoffCounty", True),
        fstr("DropoffPostcode", True),
        fstr("DropoffCountry", True),
        fdate("DropoffDateTime"),
        fint("Status"),
        fint("Miles", True),
        fint("Cost"),
        fdate("CostPaidDate", True),
        flongstr("Comments") ))
    sql += index("animaltransport_TransportReference", "animaltransport", "TransportReference")
    sql += index("animaltransport_AnimalID", "animaltransport", "AnimalID")
    sql += index("animaltransport_DriverOwnerID", "animaltransport", "DriverOwnerID")
    sql += index("animaltransport_PickupOwnerID", "animaltransport", "PickupOwnerID")
    sql += index("animaltransport_PickupAddress", "animaltransport", "PickupAddress")
    sql += index("animaltransport_DropoffOwnerID", "animaltransport", "DropoffOwnerID")
    sql += index("animaltransport_DropoffAddress", "animaltransport", "DropoffAddress")
    sql += index("animaltransport_PickupDateTime", "animaltransport", "PickupDateTime")
    sql += index("animaltransport_DropoffDateTime", "animaltransport", "DropoffDateTime")
    sql += index("animaltransport_Status", "animaltransport", "Status")
    sql += index("animaltransport_TransportTypeID", "animaltransport", "TransportTypeID")

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
        fstr("GivenBy", True),
        fdate("DateRequired"),
        fdate("DateExpires", True),
        fstr("BatchNumber", True),
        fstr("Manufacturer", True),
        fstr("RabiesTag", True),
        fint("Cost"),
        fdate("CostPaidDate", True),
        flongstr("Comments") ))
    sql += index("animalvaccination_AnimalID", "animalvaccination", "AnimalID")
    sql += index("animalvaccination_AdministeringVetID", "animalvaccination", "AdministeringVetID")
    sql += index("animalvaccination_DateExpires", "animalvaccination", "DateExpires")
    sql += index("animalvaccination_DateRequired", "animalvaccination", "DateRequired")
    sql += index("animalvaccination_GivenBy", "animalvaccination", "GivenBy")
    sql += index("animalvaccination_CostPaidDate", "animalvaccination", "CostPaidDate")
    sql += index("animalvaccination_Manufacturer", "animalvaccination", "Manufacturer")
    sql += index("animalvaccination_RabiesTag", "animalvaccination", "RabiesTag")

    sql += table("animalwaitinglist", (
        fid(),
        fint("SpeciesID"),
        fint("BreedID", True),
        fint("Neutered", True),
        fint("Sex", True),
        fint("Size", True),
        fdate("DateOfBirth", True),
        fdate("DatePutOnList"),
        fint("OwnerID"),
        fstr("AnimalName", True),
        flongstr("AnimalDescription"),
        fstr("MicrochipNumber", True),
        flongstr("ReasonForWantingToPart"),
        fint("CanAffordDonation"),
        fint("Urgency"),
        fdate("DateRemovedFromList", True),
        fint("WaitingListRemovalID", True),
        fint("AutoRemovePolicy"),
        fdate("DateOfLastOwnerContact", True),
        flongstr("ReasonForRemoval"),
        flongstr("Comments"),
        fdate("UrgencyUpdateDate", True),
        fdate("UrgencyLastUpdatedDate", True) ))
    sql += index("animalwaitinglist_AnimalDescription", "animalwaitinglist", "AnimalDescription", partial = True)
    sql += index("animalwaitinglist_AnimalName", "animalwaitinglist", "AnimalName")
    sql += index("animalwaitinglist_MicrochipNumber", "animalwaitinglist", "MicrochipNumber")
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
        fint("LinkID", True),
        fstr("ParentLinks", True),
        flongstr("Description", False) ), False)
    sql += index("audittrail_Action", "audittrail", "Action")
    sql += index("audittrail_AuditDate", "audittrail", "AuditDate")
    sql += index("audittrail_UserName", "audittrail", "UserName")
    sql += index("audittrail_TableName", "audittrail", "TableName")
    sql += index("audittrail_LinkID", "audittrail", "LinkID")
    sql += index("audittrail_ParentLinks", "audittrail", "ParentLinks")

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

    sql += table("clinicappointment", (
        fid(),
        fint("AnimalID"),
        fint("OwnerID"),
        fstr("ApptFor"),
        fdate("DateTime"),
        fint("Status"),
        fdate("ArrivedDateTime", True),
        fdate("WithVetDateTime", True),
        fdate("CompletedDateTime", True),
        fint("ClinicTypeID", True),
        flongstr("ReasonForAppointment", True),
        flongstr("Comments", True),
        fint("Amount"),
        fint("IsVAT"),
        ffloat("VATRate"),
        fint("VATAmount") ))
    sql += index("clinicappointment_AnimalID", "clinicappointment", "AnimalID")
    sql += index("clinicappointment_OwnerID", "clinicappointment", "OwnerID")
    sql += index("clinicappointment_Status", "clinicappointment", "Status")
    sql += index("clinicappointment_ApptFor", "clinicappointment", "ApptFor")
    sql += index("clinicappointment_ClinicTypeID", "clinicappointment", "ClinicTypeID")

    sql += table("clinicinvoiceitem", (
        fid(),
        fint("ClinicAppointmentID"),
        flongstr("Description"),
        fint("Amount") ))
    sql += index("clinicinvoiceitem_ClinicAppointmentID", "clinicinvoiceitem", "ClinicAppointmentID")

    sql += table("configuration", (
        fstr("ItemName"),
        flongstr("ItemValue", False) ), False)
    sql += index("configuration_ItemName", "configuration", "ItemName")

    sql += table("costtype", (
        fid(),
        fstr("CostTypeName"),
        fstr("CostTypeDescription", True),
        fint("DefaultCost", True),
        fint("AccountID", True),
        fint("IsRetired", True) ), False)

    sql += table("customreport", (
        fid(),
        fstr("Title"),
        fstr("Category"),
        flongstr("DailyEmail", True),
        fint("DailyEmailHour", True),
        fint("DailyEmailFrequency", True),
        flongstr("SQLCommand", False),
        flongstr("HTMLBody", False),
        flongstr("Description"),
        fint("OmitHeaderFooter"),
        fint("OmitCriteria"),
        fint("Revision", True) ))
    sql += index("customreport_Title", "customreport", "Title")

    sql += table("customreportrole", (
        fint("ReportID"),
        fint("RoleID"),
        fint("CanView") ), False)
    sql += index("customreportrole_ReportIDRoleID", "customreportrole", "ReportID, RoleID")

    sql += table("dbfs", (
        fid(),
        fstr("Path"),
        fstr("Name"),
        fstr("URL", True),
        fclob("Content", True) ), False)
    sql += index("dbfs_Path", "dbfs", "Path")
    sql += index("dbfs_Name", "dbfs", "Name")
    sql += index("dbfs_URL", "dbfs", "URL")

    sql += table("deathreason", (
        fid(),
        fstr("ReasonName"),
        fstr("ReasonDescription", True),
        fint("IsRetired", True) ), False)

    sql += table("deletion", (
        fint("ID"),
        fstr("TableName"),
        fstr("DeletedBy"),
        fdate("Date"),
        fstr("IDList"),
        flongstr("RestoreSQL") ), False)
    sql += index("deletion_IDTablename", "deletion", "ID,Tablename")

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
        fint("OrderIndex", True),
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
        fint("AccountID", True),
        fint("IsVAT", True),
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

    sql += table("event", (
        fid(),
        fdate("StartDateTime"),
        fdate("EndDateTime"),
        fstr("EventName"),
        flongstr("EventDescription", True),
        fint("EventOwnerID", True),
        fstr("EventAddress", True),
        fstr("EventTown", True),
        fstr("EventCounty", True),
        fstr("EventPostCode", True),
        fstr("EventCountry", True) ))
    sql += index("event_StartDateTime", "event", "StartDateTime")
    sql += index("event_EndDateTime", "event", "EndDateTime")
    sql += index("event_EventName", "event", "EventName")
    sql += index("event_EventOwnerID", "event", "EventOwnerID")
    sql += index("event_EventAddress", "event", "EventAddress")

    sql += table("eventanimal", (
        fid(),
        fint("EventID"),
        fint("AnimalID"),
        fdate("ArrivalDate", True),
        flongstr("Comments", True) ))
    sql += index("eventanimal_EventAnimalID", "eventanimal", "EventID,AnimalID", True)
    sql += index("eventanimal_ArrivalDate", "eventanimal", "ArrivalDate")

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
        fint("SiteID", True), 
        fint("IsRetired", True) ), False)

    sql += table("jurisdiction", (
        fid(),
        fstr("JurisdictionName"),
        fstr("JurisdictionDescription", True),
        fint("IsRetired", True) ), False)

    sql += table("licencetype", (
        fid(),
        fstr("LicenceTypeName"),
        fstr("LicenceTypeDescription", True),
        fint("DefaultCost", True),
        fint("RescheduleDays", True),
        fint("IsRetired", True) ), False)

    sql += table("lksaccounttype", (
        fid(), fstr("AccountType") ), False)

    sql += table("lkanimalflags", (
        fid(), fstr("Flag"), fint("IsRetired", True) ), False)

    sql += table("lkmediaflags", (
        fid(), fstr("Flag"), fint("IsRetired", True) ), False)

    sql += table("lkownerflags", (
        fid(), fstr("Flag"), fint("IsRetired", True) ), False)

    sql += table("lkboardingtype", (
        fid(),
        fstr("BoardingName"),
        fstr("BoardingDescription", True),
        fint("DefaultCost", True),
        fint("IsRetired", True) ), False)

    sql += table("lkclinictype", (
        fid(),
        fstr("ClinicTypeName"),
        fstr("ClinicTypeDescription", True),
        fint("IsRetired", True) ), False)

    sql += table("lksclinicstatus", (
        fid(), fstr("Status") ), False)

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

    sql += table("lksentrytype", (
        fid(), fstr("EntryTypeName") ), False)

    sql += table("lksloglink", (
        fid(), fstr("LinkType") ), False)

    sql += table("lksoutcome", (
        fid(), fstr("Outcome") ), False)

    sql += table("lksrotatype", (
        fid(), fstr("RotaType"),
        fint("IsRetired", True) ), False)

    sql += table("lkstransportstatus", (
        fid(), fstr("Name") ), False)

    sql += table("lkurgency", ( 
        fid(), fstr("Urgency") ), False)

    sql += table("lksyesno", (
        fid(), fstr("Name") ), False)

    sql += table("lksynun", (
        fid(), fstr("Name") ), False)

    sql += table("lksynunk", (
        fid(), fstr("Name") ), False)

    sql += table("lksposneg", (
        fid(), fstr("Name") ), False)

    sql += table("lkwaitinglistremoval", (
        fid(), fstr("RemovalName") ), False)

    sql += table("lkworktype", (
        fid(), fstr("WorkType"),
        fint("IsRetired", True) ), False)

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
        fint("DBFSID", True),
        fint("MediaSize", True),
        fint("MediaSource", True),
        fstr("MediaFlags", True),
        fint("MediaType", True),
        fstr("MediaName"),
        fstr("MediaMimeType", True),
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
        fdate("Date"),
        fdate("RetainUntil", True) ), True, True)
    sql += index("media_DBFSID", "media", "DBFSID")
    sql += index("media_MediaFlags", "media", "MediaFlags")
    sql += index("media_MediaMimeType", "media", "MediaMimeType")
    sql += index("media_MediaSource", "media", "MediaSource")
    sql += index("media_LinkID", "media", "LinkID")
    sql += index("media_LinkTypeID", "media", "LinkTypeID")
    sql += index("media_WebsitePhoto", "media", "WebsitePhoto")
    sql += index("media_WebsiteVideo", "media", "WebsiteVideo")
    sql += index("media_DocPhoto", "media", "DocPhoto")
    sql += index("media_CreatedDate", "media", "CreatedDate")
    sql += index("media_Date", "media", "Date")
    sql += index("media_RetainUntil", "media", "RetainUntil")

    sql += table("medicalprofile", (
        fid(),
        fstr("ProfileName"),
        fstr("TreatmentName"),
        fstr("Dosage"),
        fint("Cost"),
        fint("CostPerTreatment", True),
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
        fint("AutoProcess", True),
        fint("RetainFor", True),
        fint("EmailSubmitter", True),
        fint("EmailCoordinator", True),
        fint("EmailFosterer", True),
        flongstr("EmailAddress", True),
        flongstr("EmailMessage", True),
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
        fint("SpeciesID", True),
        fstr("VisibleIf", True),
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
        fstr("OwnerCode", True),
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
        fstr("OwnerCountry", True),
        fstr("LatLong", True),
        fstr("HomeTelephone", True),
        fstr("WorkTelephone", True),
        fstr("MobileTelephone", True),
        fstr("EmailAddress", True),
        fdate("DateOfBirth", True),
        fstr("IdentificationNumber", True),
        fstr("OwnerTitle2", True),
        fstr("OwnerInitials2", True),
        fstr("OwnerForeNames2", True),
        fstr("OwnerSurname2", True),
        fstr("WorkTelephone2", True),
        fstr("MobileTelephone2", True),
        fstr("EmailAddress2", True),
        fdate("DateOfBirth2", True),
        fstr("IdentificationNumber2", True),
        fint("ExcludeFromBulkEmail", True),
        fstr("GDPRContactOptIn", True),
        fint("JurisdictionID", True),
        fint("IDCheck", True),
        flongstr("Comments", True),
        flongstr("PopupWarning", True),
        fint("SiteID", True),
        fint("IsBanned", True),
        fint("IsDangerous", True),
        fint("IsVolunteer", True),
        fint("IsHomeChecker", True),
        fint("IsMember", True),
        fdate("MembershipExpiryDate", True),
        fstr("MembershipNumber", True),
        fint("IsAdopter", True),
        fint("IsAdoptionCoordinator", True),
        fint("IsDonor", True),
        fint("IsDriver", True),
        fint("IsShelter", True),
        fint("IsACO", True), 
        fint("IsStaff", True),
        fint("IsFosterer", True),
        fint("IsSponsor", True),
        fint("FosterCapacity", True),
        fint("IsRetailer", True),
        fint("IsVet", True),
        fint("IsGiftAid", True),
        fstr("ExtraIDs", True),
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
        fstr("MatchFlags", True),
        fstr("MatchCommentsContain", True) ))
    sql += index("owner_CreatedBy", "owner", "CreatedBy")
    sql += index("owner_CreatedDate", "owner", "CreatedDate")
    sql += index("owner_GDPRContactOptIn", "owner", "GDPRContactOptIn")
    sql += index("owner_MembershipNumber", "owner", "MembershipNumber")
    sql += index("owner_OwnerCode", "owner", "OwnerCode")
    sql += index("owner_OwnerName", "owner", "OwnerName")
    sql += index("owner_OwnerAddress", "owner", "OwnerAddress")
    sql += index("owner_OwnerCounty", "owner", "OwnerCounty")
    sql += index("owner_EmailAddress", "owner", "EmailAddress")
    sql += index("owner_OwnerForeNames", "owner", "OwnerForeNames")
    sql += index("owner_HomeTelephone", "owner", "HomeTelephone")
    sql += index("owner_MobileTelephone", "owner", "MobileTelephone")
    sql += index("owner_WorkTelephone", "owner", "WorkTelephone")
    sql += index("owner_JurisdictionID", "owner", "JurisdictionID")
    sql += index("owner_OwnerInitials", "owner", "OwnerInitials")
    sql += index("owner_OwnerPostcode", "owner", "OwnerPostcode")
    sql += index("owner_OwnerCountry", "owner", "OwnerCountry")
    sql += index("owner_OwnerSurname", "owner", "OwnerSurname")
    sql += index("owner_OwnerTitle", "owner", "OwnerTitle")
    sql += index("owner_OwnerTown", "owner", "OwnerTown")
    sql += index("owner_IdentificationNumber", "owner", "IdentificationNumber")
    sql += index("owner_OwnerTitle2", "owner", "OwnerTitle2")
    sql += index("owner_OwnerInitials2", "owner", "OwnerInitials2")
    sql += index("owner_OwnerForeNames2", "owner", "OwnerForeNames2")
    sql += index("owner_OwnerSurname2", "owner", "OwnerSurname2")
    sql += index("owner_MobileTelephone2", "owner", "MobileTelephone2")
    sql += index("owner_WorkTelephone2", "owner", "WorkTelephone2")
    sql += index("owner_EmailAddress2", "owner", "EmailAddress2")
    sql += index("owner_IdentificationNumber2", "owner", "IdentificationNumber2")
    sql += index("owner_SiteID", "owner", "SiteID")
    sql += index("owner_IDCheck", "owner", "IDCheck")
    sql += index("owner_IsACO", "owner", "IsACO")
    sql += index("owner_IsAdopter", "owner", "IsAdopter")
    sql += index("owner_IsAdoptionCoordinator", "owner", "IsAdoptionCoordinator")
    sql += index("owner_IsFosterer", "owner", "IsFosterer")
    sql += index("owner_IsRetailer", "owner", "IsRetailer")
    sql += index("owner_IsStaff", "owner", "IsStaff")
    sql += index("owner_IsVet", "owner", "IsVet")
    sql += index("owner_IsVolunteer", "owner", "IsVolunteer")
    sql += index("owner_ExtraIDs", "owner", "ExtraIDs")
    sql += index("owner_IsSponsor", "owner", "IsSponsor")

    sql += table("ownercitation", (
        fid(),
        fint("OwnerID"),
        fint("AnimalControlID", True),
        fint("CitationTypeID"),
        fdate("CitationDate"),
        fstr("CitationNumber", True),
        fint("FineAmount", True),
        fdate("FineDueDate", True),
        fdate("FinePaidDate", True),
        flongstr("Comments", True) ))
    sql += index("ownercitation_OwnerID", "ownercitation", "OwnerID")
    sql += index("ownercitation_CitationTypeID", "ownercitation", "CitationTypeID")
    sql += index("ownercitation_CitationDate", "ownercitation", "CitationDate")
    sql += index("ownercitation_CitationNumber", "ownercitation", "CitationNumber")
    sql += index("ownercitation_FineDueDate", "ownercitation", "FineDueDate")
    sql += index("ownercitation_FinePaidDate", "ownercitation", "FinePaidDate")

    sql += table("ownerdonation", (
        fid(),
        fint("AnimalID", True),
        fint("OwnerID"),
        fint("MovementID", True),
        fint("DonationTypeID"),
        fint("DonationPaymentID", True),
        fstr("ReceiptNumber", True),
        fstr("ChequeNumber", True),
        flongstr("PaymentProcessorData", True),
        fdate("Date", True),
        fdate("DateDue", True),
        fint("Donation"),
        fint("Quantity", True),
        fint("UnitPrice", True),
        fint("IsGiftAid"),
        fint("Fee", True), 
        fint("IsVAT", True),
        ffloat("VATRate", True),
        fint("VATAmount", True),
        fint("Frequency"),
        fint("NextCreated", True),
        flongstr("Comments") ))
    sql += index("ownerdonation_OwnerID", "ownerdonation", "OwnerID")
    sql += index("ownerdonation_ReceiptNumber", "ownerdonation", "ReceiptNumber")
    sql += index("ownerdonation_ChequeNumber", "ownerdonation", "ChequeNumber")
    sql += index("ownerdonation_Date", "ownerdonation", "Date")
    sql += index("ownerdonation_DateDue", "ownerdonation", "DateDue")
    sql += index("ownerdonation_IsVAT", "ownerdonation", "IsVAT")

    sql += table("ownerlookingfor", (
        fint("OwnerID"),
        fint("AnimalID"),
        flongstr("MatchSummary") ), False)

    sql += index("ownerlookingfor_OwnerID", "ownerlookingfor", "OwnerID")
    sql += index("ownerlookingfor_AnimalID", "ownerlookingfor", "AnimalID")

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
        fint("Renewed", True),
        fstr("Token", True),
        fstr("PaymentReference", True),
        fdate("IssueDate"),
        fdate("ExpiryDate"),
        flongstr("Comments", True) ))
    sql += index("ownerlicence_OwnerID", "ownerlicence", "OwnerID")
    sql += index("ownerlicence_AnimalID", "ownerlicence", "AnimalID")
    sql += index("ownerlicence_LicenceTypeID", "ownerlicence", "LicenceTypeID")
    sql += index("ownerlicence_LicenceNumber", "ownerlicence", "LicenceNumber")
    sql += index("ownerlicence_Renewed", "ownerlicence", "Renewed")
    sql += index("ownerlicence_Token", "ownerlicence", "Token")
    sql += index("ownerlicence_PaymentReference", "ownerlicence", "PaymentReference")
    sql += index("ownerlicence_IssueDate", "ownerlicence", "IssueDate")
    sql += index("ownerlicence_ExpiryDate", "ownerlicence", "ExpiryDate")

    sql += table("ownerrole", (
        fint("OwnerID"),
        fint("RoleID"),
        fint("CanView"),
        fint("CanEdit") ), False)
    sql += index("ownerrole_OwnerRoleID", "ownerrole", "OwnerID, RoleID", True)

    sql += table("ownerrota", (
        fid(),
        fint("OwnerID"),
        fdate("StartDateTime"),
        fdate("EndDateTime"),
        fint("RotaTypeID"),
        fint("WorkTypeID", True),
        flongstr("Comments", True) ))
    sql += index("ownerrota_OwnerID", "ownerrota", "OwnerID")
    sql += index("ownerrota_StartDateTime", "ownerrota", "StartDateTime")
    sql += index("ownerrota_EndDateTime", "ownerrota", "EndDateTime")
    sql += index("ownerrota_RotaTypeID", "ownerrota", "RotaTypeID")
    sql += index("ownerrota_WorkTypeID", "ownerrota", "WorkTypeID")

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
        fint("AnimalID", True),
        fstr("VoucherCode", True),
        fdate("DateIssued"),
        fdate("DateExpired"),
        fdate("DatePresented", True),
        fint("VetID", True),
        fint("Value"),
        flongstr("Comments", True) ))
    sql += index("ownervoucher_AnimalID", "ownervoucher", "AnimalID")
    sql += index("ownervoucher_OwnerID", "ownervoucher", "OwnerID")
    sql += index("ownervoucher_VoucherID", "ownervoucher", "VoucherID")
    sql += index("ownervoucher_VoucherCode", "ownervoucher", "VoucherCode")
    sql += index("ownervoucher_DateExpired", "ownervoucher", "DateExpired")
    sql += index("ownervoucher_DatePresented", "ownervoucher", "DatePresented")
    sql += index("ownervoucher_VetID", "ownervoucher", "VetID")

    sql += table("pickuplocation", (
        fid(),
        fstr("LocationName"),
        fstr("LocationDescription", True),
        fint("IsRetired", True) ), False)

    sql += table("primarykey", (
        fstr("TableName"),
        fint("NextID") ), False)
    sql += index("primarykey_TableName", "primarykey", "TableName")

    sql += table("publishlog", (
        fid(),
        fdate("PublishDateTime"),
        fstr("Name"),
        fint("Success"),
        fint("Alerts"),
        flongstr("LogData") ), False)
    sql += index("publishlog_PublishDateTime", "publishlog", "PublishDateTime")
    sql += index("publishlog_Name", "publishlog", "Name")

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

    sql += table("site", (
        fid(),
        fstr("SiteName") ), False)

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
        ffloat("Low", True),
        fdate("Expiry", True),
        fstr("BatchNumber", True),
        fint("Cost", True),
        fint("UnitPrice", True),
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

    sql += table("templatedocument", (
        fid(),
        fstr("Name"),
        fstr("Path"),
        fstr("ShowAt", True),
        flongstr("Content") ), False)
    sql += index("templatedocument_NamePath", "templatedocument", "Name,Path", True)

    sql += table("templatehtml", (
        fid(),
        fstr("Name"),
        flongstr("Header"),
        flongstr("Body", True),
        flongstr("Footer", True),
        fint("IsBuiltIn") ), False)
    sql += index("templatehtml_Name", "templatehtml", "Name", True)

    sql += table("testtype", (
        fid(),
        fstr("TestName"),
        fstr("TestDescription", True),
        fint("DefaultCost", True),
        fint("RescheduleDays", True),
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

    sql += table("transporttype", (
        fid(),
        fstr("TransportTypeName"),
        fstr("TransportTypeDescription", True),
        fint("IsRetired", True) ), False)

    sql += table("users", (
        fid(),
        fstr("UserName"),
        fstr("RealName", True),
        fstr("EmailAddress", True),
        fstr("Password"),
        fint("EnableTOTP", True),
        fstr("OTPSecret", True),
        fint("SuperUser"),
        fint("OwnerID", True),
        flongstr("SecurityMap", True),
        flongstr("IPRestriction", True),
        flongstr("Signature", True),
        fstr("LocaleOverride", True),
        fstr("ThemeOverride", True),
        fint("SiteID", True), 
        fint("DisableLogin", True),
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
        fint("RescheduleDays", True),
        fint("DefaultCost", True),
        fint("IsRetired", True) ), False)
    return sql

def sql_default_data(dbo: Database, skip_config: bool = False) -> str:
    """
    Returns the SQL for the default data set.
    skip_config: if set, does not insert default data for tables: configuration, roles, userrole and users.
    """
    def config(key: str, value: str) -> str:
        return "INSERT INTO configuration (ItemName, ItemValue) VALUES ('%s', '%s')|=\n" % ( dbo.escape(key), dbo.escape(value) )
    def lookup1(tablename: str, fieldname: str, tid: int, name: str) -> str:
        return "INSERT INTO %s (ID, %s) VALUES (%s, '%s')|=\n" % ( tablename, fieldname, tid, dbo.escape(name) )
    def lookup2(tablename: str, fieldname: str, tid: int, name: str) -> str:
        return "INSERT INTO %s (ID, %s, IsRetired) VALUES (%s, '%s', 0)|=\n" % ( tablename, fieldname, tid, dbo.escape(name) )
    def lookup2money(tablename: str, fieldname: str, tid: int, name: str, money: int = 0) -> str:
        return "INSERT INTO %s (ID, %s, DefaultCost, IsRetired) VALUES (%s, '%s', %d, 0)|=\n" % ( tablename, fieldname, tid, dbo.escape(name), money)
    def lookup2moneyaccount(tablename: str, fieldname: str, tid: int, name: str, accountid: int = 0, money: int = 0) -> str:
        return "INSERT INTO %s (ID, %s, AccountID, DefaultCost, IsRetired) VALUES (%s, '%s', %d, %d, 0)|=\n" % \
            ( tablename, fieldname, tid, dbo.escape(name), accountid, money)
    def account(tid: int, code: str, desc: str, atype: int, dtype: int, ctype: int) -> str:
        return "INSERT INTO accounts (ID, Code, Description, Archived, AccountType, CostTypeID, DonationTypeID, RecordVersion, CreatedBy, CreatedDate, LastChangedBy, LastChangedDate) VALUES (%s, '%s', '%s', 0, %s, %s, %s, 0, '%s', %s, '%s', %s)|=\n" % ( tid, dbo.escape(code), dbo.escape(desc), atype, ctype, dtype, 'default', dbo.sql_now(), 'default', dbo.sql_now() ) 
    def breed(tid: int, name: str, petfinder: str, speciesid: int) -> str:
        return "INSERT INTO breed (ID, BreedName, BreedDescription, PetFinderBreed, SpeciesID, IsRetired) VALUES (%s, '%s', '', '%s', %s, 0)|=\n" % ( tid, dbo.escape(name), dbo.escape(petfinder), str(speciesid) )
    def basecolour(tid: int, name: str, adoptapet: str) -> str:
        return "INSERT INTO basecolour (ID, BaseColour, BaseColourDescription, AdoptAPetColour, IsRetired) VALUES (%s, '%s', '', '%s', 0)|=\n" % (tid, dbo.escape(name), adoptapet)
    def internallocation(lid: int, name: str) -> str:
        return "INSERT INTO internallocation (ID, LocationName, LocationDescription, Units, SiteID, IsRetired) VALUES (%s, '%s', '', '', 1, 0)|=\n" % ( lid, dbo.escape(name) )
    def medicalprofile(pid: int, name: str, dosage: str) -> str:
        return "INSERT INTO medicalprofile (ID, Comments, Cost, CostPerTreatment, CreatedBy, CreatedDate, Dosage, LastChangedDate, LastChangedBy, " \
            "ProfileName, RecordVersion, TimingRule, TimingRuleFrequency, TimingRuleNoFrequencies, TotalNumberOfTreatments, " \
            f"TreatmentName, TreatmentRule) VALUES ({str(pid)}, '', 0, 0, 'system', {dbo.sql_now()}, '{dbo.escape(dosage)}', {dbo.sql_now()}, 'system', " \
            f"'{dbo.escape(name)}', 0, 0, 0, 0, 1, '{dbo.escape(name)}', 0)|=\n"
    def role(tid: int, name: str, perms: str) -> str:
        return "INSERT INTO role (ID, Rolename, SecurityMap) VALUES (%s, '%s', '%s')|=\n" % (tid, dbo.escape(name), perms)
    def species(tid: int, name: str, petfinder: str) -> str:
        return "INSERT INTO species (ID, SpeciesName, SpeciesDescription, PetFinderSpecies, IsRetired) VALUES (%s, '%s', '', '%s', 0)|=\n" % ( tid, dbo.escape(name), petfinder )
    def user(tid: int, username: str, realname: str, password: str, superuser: bool) -> str:
        return "INSERT INTO users (ID, UserName, RealName, EmailAddress, Password, SuperUser, OwnerID, SecurityMap, IPRestriction, Signature, LocaleOverride, ThemeOverride, SiteID, DisableLogin, LocationFilter, RecordVersion) VALUES (%s,'%s','%s', '', 'plain:%s', %s, 0,'', '', '', '', '', 0, 0, '', 0)|=\n" % (tid, username, realname, password, superuser and 1 or 0)

    l = dbo.locale
    sql = ""
    if not skip_config:
        sql += user(1, "user", "Default system user", "letmein", True)
        sql += user(2, "guest", "Default guest user", "guest", False)
        sql += role(1, _("Other Organisation", l), "vac *va *vavet *vav *mvam *dvad *cvad *vamv *vo *volk *vle *vvov *vdn *vla *vfa *vwl *vcr *vll *vof *")
        sql += role(2, _("Staff", l), "aa *ca *va *ma *rsu *vavet *cloa *gaf *aam *cam *dam *vam *mand *aav *vav *cav *dav *bcav *maam *mcam *mdam *mvam *bcam *daad *dcad *ddad *dvad *caad *cdad *cvad *aamv *camv *vamv *ao *co *vo *emo *mo *volk *ale *cle *dle *vle *vaov *vcov *vvov *oaod *ocod *odod *ovod *vdn *edt *adn *eadn *emdn *ecdn *bcn *ddn *pdn *pvd *ala *cla *vla *afa *cfa *vfa *mlaf *vwl *awl *cwl *bcwl *all *cll *vll *dll *excr *vcr *vvo *vof *vti *")
        sql += role(3, _("Accountant", l), "aac *vac *cac *ctrx *dac *vaov *vcov *vdov *vvov *oaod *ocod *odod *ovod *")
        sql += role(4, _("Vet", l), "va *vavet *aav *vav *cav *dav *bcav *maam *mcam *mdam *mvam *bcam *daad *dcad *ddad *dvad *")
        sql += role(5, _("Publisher", l), "uipb *aof *vof *eof *")
        sql += role(6, _("System Admin", l), "asm *cso *cpo *maf *mdt *ml *usi *rdbu *rdbd *asu *esu *ccr *vcr *hcr *dcr *tbp *excr *eav *icv *")
        sql += role(7, _("Marketer", l), "uipb *mmeo *emo *mmea *eof *vof *")
        sql += role(8, _("Investigator", l), "aoi *coi *doi *voi *")
        sql += role(9, _("Animal Control Officer", l), "aaci *caci *vaci *aacc *cacc *dacc *vacc *emo *cacd *cacr *")
        sql += "INSERT INTO userrole VALUES (2, 1)|=\n"
        sql += config("DBV", str(LATEST_VERSION))
        sql += config("DatabaseVersion", str(LATEST_VERSION))
        sql += config("Organisation", _("Organisation", l))
        sql += config("OrganisationAddress", _("Address", l))
        sql += config("OrganisationTelephone", _("Telephone", l))
        sql += config("AgeGroup1Name", _("Baby", l))
        sql += config("AgeGroup2Name", _("Young Adult", l))
        sql += config("AgeGroup3Name", _("Adult", l))
        sql += config("AgeGroup4Name", _("Senior", l))
    sql += account(1, _("Income::Donation", l), _("Incoming donations (misc)", l), 5, 1, 0)
    sql += account(2, _("Income::Adoption", l), _("Adoption fee donations", l), 5, 2, 0)
    sql += account(3, _("Income::WaitingList", l), _("Waiting list donations", l), 5, 3, 0)
    sql += account(4, _("Income::EntryDonation", l), _("Donations for animals entering the shelter", l), 5, 4, 0)
    sql += account(5, _("Income::Sponsorship", l), _("Sponsorship donations", l), 5, 5, 0)
    sql += account(7, _("Income::BoardingFee", l), _("Boarding fees", l), 5, 7, 0)
    sql += account(8, _("Income::InMemoryOf", l), _("In Memory Of donations", l), 5, 8, 0)
    sql += account(9, _("Income::LicenseFee", l), _("License fees", l), 5, 9, 0)
    sql += account(10, _("Income::SalesTax", l), _("Sales Tax", l), 5, 0, 0)
    sql += account(20, _("Income::Shop", l), _("Income from an on-site shop", l), 5, 0, 0)
    sql += account(21, _("Income::Interest", l), _("Bank account interest", l), 5, 0, 0)
    sql += account(22, _("Income::OpeningBalances", l), _("Opening balances", l), 5, 0, 0)
    sql += account(30, _("Bank::Current", l), _("Bank current account", l), 1, 0, 0)
    sql += account(31, _("Bank::Deposit", l), _("Bank deposit account", l), 1, 0, 0)
    sql += account(32, _("Bank::Savings", l), _("Bank savings account", l), 1, 0, 0)
    sql += account(33, _("Asset::Premises", l), _("Premises", l), 8, 0, 0)
    sql += account(40, _("Expenses::Phone", l), _("Telephone Bills", l), 4, 0, 0)
    sql += account(41, _("Expenses::Electricity", l), _("Electricity Bills", l), 4, 0, 0)
    sql += account(42, _("Expenses::Water", l), _("Water Bills", l), 4, 0, 0)
    sql += account(43, _("Expenses::Gas", l), _("Gas Bills", l), 4, 0, 0)
    sql += account(44, _("Expenses::Postage", l), _("Postage costs", l), 4, 0, 0)
    sql += account(45, _("Expenses::Stationary", l), _("Stationary costs", l), 4, 0, 0)
    sql += account(46, _("Expenses::Food", l), _("Animal food costs", l), 4, 0, 0)
    sql += account(47, _("Expenses::Board", l), _("Animal board costs", l), 4, 0, 1)
    sql += account(48, _("Expenses::TransactionFee", l), _("Transaction fees", l), 4, 0, 0)
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
    sql += breed(274, _("Havana", l), "Havana Brown", 2)
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
    sql += breed(323, _("Champagne D'Argent", l), "Champagne D'Argent", 7)
    sql += breed(324, _("Checkered Giant", l), "Checkered Giant", 7)
    sql += breed(325, _("Chinchilla", l), "Chinchilla", 7)
    sql += breed(326, _("Cinnamon", l), "Cinnamon", 7)
    sql += breed(327, _("Creme D'Argent", l), "Creme D'Argent", 7)
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
    sql += breed(442, _("Mixed Breed", l), "Mixed Breed", 1)
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
    sql += lookup2("donationpayment", "PaymentName", 2, _("Check", l))
    sql += lookup2("donationpayment", "PaymentName", 3, _("Credit Card", l))
    sql += lookup2("donationpayment", "PaymentName", 4, _("Debit Card", l))
    sql += lookup2("donationpayment", "PaymentName", 5, _("PayPal", l))
    sql += lookup2("donationpayment", "PaymentName", 6, _("Stripe", l))
    sql += lookup2moneyaccount("donationtype", "DonationName", 1, _("Donation", l), 1)
    sql += lookup2moneyaccount("donationtype", "DonationName", 2, _("Adoption Fee", l), 2)
    sql += lookup2moneyaccount("donationtype", "DonationName", 3, _("Waiting List Donation", l), 3)
    sql += lookup2moneyaccount("donationtype", "DonationName", 4, _("Entry Donation", l), 4)
    sql += lookup2moneyaccount("donationtype", "DonationName", 5, _("Animal Sponsorship", l), 5)
    sql += lookup2moneyaccount("donationtype", "DonationName", 6, _("In-Kind Donation", l))
    sql += lookup2moneyaccount("donationtype", "DonationName", 7, _("Boarding Fee", l), 7)
    sql += lookup2moneyaccount("donationtype", "DonationName", 8, _("In Memory Of", l), 8)
    sql += lookup2moneyaccount("donationtype", "DonationName", 9, _("License Fee", l), 9)
    sql += lookup2("entryreason", "ReasonName", 1, _("Marriage/Relationship split", l))
    sql += lookup2("entryreason", "ReasonName", 2, _("Allergies", l))
    sql += lookup2("entryreason", "ReasonName", 3, _("Biting", l))
    sql += lookup2("entryreason", "ReasonName", 4, _("Unable to Cope", l))
    sql += lookup2("entryreason", "ReasonName", 5, _("Unsuitable Accomodation", l))
    sql += lookup2("entryreason", "ReasonName", 6, _("Death of Owner", l))
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
    sql += lookup2("entryreason", "ReasonName", 17, _("Surrender", l))
    sql += lookup2("entryreason", "ReasonName", 18, _("Too Many Animals", l))
    sql += lookup2("incidentcompleted", "CompletedName", 1, _("Animal destroyed", l))
    sql += lookup2("incidentcompleted", "CompletedName", 2, _("Animal picked up", l))
    sql += lookup2("incidentcompleted", "CompletedName", 3, _("Owner given citation", l))
    sql += lookup2("incidentcompleted", "CompletedName", 4, _("Animal not found", l))
    sql += lookup2("incidentcompleted", "CompletedName", 5, _("Other", l))
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
    sql += lookup2("jurisdiction", "JurisdictionName", 1, _("Local", l))
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
    sql += lookup2money("lkboardingtype", "BoardingName", 1, _("Boarding", l))
    sql += lookup2("lkclinictype", "ClinicTypeName", 1, _("Consultation", l))
    sql += lookup2("lkclinictype", "ClinicTypeName", 2, _("Followup", l))
    sql += lookup2("lkclinictype", "ClinicTypeName", 3, _("Prescription", l))
    sql += lookup2("lkclinictype", "ClinicTypeName", 4, _("Surgery", l))
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
    sql += lookup1("lksclinicstatus", "Status", 0, _("Scheduled", l))
    sql += lookup1("lksclinicstatus", "Status", 1, _("Invoice Only", l))
    sql += lookup1("lksclinicstatus", "Status", 2, _("Not Arrived", l))
    sql += lookup1("lksclinicstatus", "Status", 3, _("Waiting", l))
    sql += lookup1("lksclinicstatus", "Status", 4, _("With Vet", l))
    sql += lookup1("lksclinicstatus", "Status", 5, _("Complete", l))
    sql += lookup1("lksclinicstatus", "Status", 6, _("Cancelled", l))
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
    sql += lookup1("lksmovementtype", "MovementType", 13, _("TNR", l))
    sql += lookup1("lksmedialink", "LinkType", 0, _("Animal", l))
    sql += lookup1("lksmedialink", "LinkType", 1, _("Lost Animal", l))
    sql += lookup1("lksmedialink", "LinkType", 2, _("Found Animal", l))
    sql += lookup1("lksmedialink", "LinkType", 3, _("Owner", l))
    sql += lookup1("lksmedialink", "LinkType", 4, _("Movement", l))
    sql += lookup1("lksmedialink", "LinkType", 5, _("Waiting List", l))
    sql += lookup1("lksmedialink", "LinkType", 6, _("Incident", l))
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
    sql += lookup1("lksdonationfreq", "Frequency", 2, _("Fortnightly", l))
    sql += lookup1("lksdonationfreq", "Frequency", 3, _("Monthly", l))
    sql += lookup1("lksdonationfreq", "Frequency", 4, _("Quarterly", l))
    sql += lookup1("lksdonationfreq", "Frequency", 5, _("Half-Yearly", l))
    sql += lookup1("lksdonationfreq", "Frequency", 6, _("Annually", l))
    sql += lookup1("lksentrytype", "EntryTypeName", 1, _("Surrender", l))
    sql += lookup1("lksentrytype", "EntryTypeName", 2, _("Stray", l))
    sql += lookup1("lksentrytype", "EntryTypeName", 3, _("Transfer In", l))
    sql += lookup1("lksentrytype", "EntryTypeName", 4, _("TNR", l))
    sql += lookup1("lksentrytype", "EntryTypeName", 5, _("Born in care", l))
    sql += lookup1("lksentrytype", "EntryTypeName", 6, _("Wildlife", l))
    sql += lookup1("lksentrytype", "EntryTypeName", 7, _("Seized", l))
    sql += lookup1("lksentrytype", "EntryTypeName", 8, _("Abandoned", l))
    sql += lookup1("lksentrytype", "EntryTypeName", 9, _("Dead on arrival", l))
    sql += lookup1("lksentrytype", "EntryTypeName", 10, _("Owner requested euthanasia", l))
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
    sql += lookup1("lksfieldlink", "LinkType", 21, _("Event - Details", l))
    sql += lookup1("lksfieldlink", "LinkType", 22, _("Movement - Adoption", l))
    sql += lookup1("lksfieldlink", "LinkType", 23, _("Movement - Foster", l))
    sql += lookup1("lksfieldlink", "LinkType", 24, _("Movement - Transfer", l))
    sql += lookup1("lksfieldlink", "LinkType", 25, _("Movement - Escaped", l))
    sql += lookup1("lksfieldlink", "LinkType", 26, _("Movement - Reclaimed", l))
    sql += lookup1("lksfieldlink", "LinkType", 27, _("Movement - Stolen", l))
    sql += lookup1("lksfieldlink", "LinkType", 28, _("Movement - Released", l))
    sql += lookup1("lksfieldlink", "LinkType", 29, _("Movement - Retailer", l))
    sql += lookup1("lksfieldlink", "LinkType", 30, _("Movement - Reservation", l))
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
    sql += lookup1("lksfieldtype", "FieldType", 10, _("Time", l))
    sql += lookup1("lksfieldtype", "FieldType", 11, _("Sponsor", l))
    sql += lookup1("lksfieldtype", "FieldType", 12, _("Vet"))
    sql += lookup1("lksfieldtype", "FieldType", 13, _("Adoption Coordinator"))
    sql += lookup1("lksloglink", "LinkType", 0, _("Animal", l))
    sql += lookup1("lksloglink", "LinkType", 1, _("Owner", l))
    sql += lookup1("lksloglink", "LinkType", 2, _("Lost Animal", l))
    sql += lookup1("lksloglink", "LinkType", 3, _("Found Animal", l))
    sql += lookup1("lksloglink", "LinkType", 4, _("Waiting List", l))
    sql += lookup1("lksloglink", "LinkType", 5, _("Movement", l))
    sql += lookup1("lksloglink", "LinkType", 6, _("Incident", l))
    sql += lookup1("lksoutcome", "Outcome", 1, _("On Shelter", l))
    sql += lookup1("lksoutcome", "Outcome", 2, _("Died", l))
    sql += lookup1("lksoutcome", "Outcome", 3, _("DOA", l))
    sql += lookup1("lksoutcome", "Outcome", 4, _("Euthanized", l))
    sql += lookup1("lksoutcome", "Outcome", 11, _("Adopted", l))
    sql += lookup1("lksoutcome", "Outcome", 12, _("Fostered", l))
    sql += lookup1("lksoutcome", "Outcome", 13, _("Transferred", l))
    sql += lookup1("lksoutcome", "Outcome", 14, _("Escaped", l))
    sql += lookup1("lksoutcome", "Outcome", 15, _("Reclaimed", l))
    sql += lookup1("lksoutcome", "Outcome", 16, _("Stolen", l))
    sql += lookup1("lksoutcome", "Outcome", 17, _("Released to Wild", l))
    sql += lookup1("lksoutcome", "Outcome", 18, _("Retailer", l))
    sql += lookup1("lksoutcome", "Outcome", 19, _("TNR", l))
    sql += lookup1("lksyesno", "Name", 0, _("No", l))
    sql += lookup1("lksyesno", "Name", 1, _("Yes", l))
    sql += lookup1("lksynun", "Name", 0, _("Yes", l))
    sql += lookup1("lksynun", "Name", 1, _("No", l))
    sql += lookup1("lksynun", "Name", 2, _("Unknown", l))
    sql += lookup1("lksynun", "Name", 3, _("Selective", l))
    sql += lookup1("lksynunk", "Name", 0, _("Yes", l))
    sql += lookup1("lksynunk", "Name", 1, _("No", l))
    sql += lookup1("lksynunk", "Name", 2, _("Unknown", l))
    sql += lookup1("lksynunk", "Name", 5, _("Over 5", l))
    sql += lookup1("lksynunk", "Name", 12, _("Over 12", l))
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
    sql += lookup1("lkstransportstatus", "Name", 1, _("New", l))
    sql += lookup1("lkstransportstatus", "Name", 2, _("Confirmed", l))
    sql += lookup1("lkstransportstatus", "Name", 3, _("Hold", l))
    sql += lookup1("lkstransportstatus", "Name", 4, _("Scheduled", l))
    sql += lookup1("lkstransportstatus", "Name", 10, _("Cancelled", l))
    sql += lookup1("lkstransportstatus", "Name", 11, _("Completed", l))
    sql += lookup1("lkurgency", "Urgency", 1, _("Urgent", l))
    sql += lookup1("lkurgency", "Urgency", 2, _("High", l))
    sql += lookup1("lkurgency", "Urgency", 3, _("Medium", l))
    sql += lookup1("lkurgency", "Urgency", 4, _("Low", l))
    sql += lookup1("lkurgency", "Urgency", 5, _("Lowest", l))
    sql += lookup1("lkwaitinglistremoval", "RemovalName", 1, _("Entered shelter", l))
    sql += lookup1("lkwaitinglistremoval", "RemovalName", 2, _("Owner kept", l))
    sql += lookup1("lkwaitinglistremoval", "RemovalName", 3, _("Owner took to another shelter", l))
    sql += lookup1("lkwaitinglistremoval", "RemovalName", 4, _("Unknown", l))
    sql += lookup1("lkworktype", "WorkType", 1, _("General", l))
    sql += lookup1("lkworktype", "WorkType", 2, _("Kennel", l))
    sql += lookup1("lkworktype", "WorkType", 3, _("Cattery", l))
    sql += lookup1("lkworktype", "WorkType", 4, _("Reception", l))
    sql += lookup1("lkworktype", "WorkType", 5, _("Office", l))
    sql += lookup2("logtype", "LogTypeName", 1, _("Bite", l))
    sql += lookup2("logtype", "LogTypeName", 2, _("Complaint", l))
    sql += lookup2("logtype", "LogTypeName", 3, _("History", l))
    sql += lookup2("logtype", "LogTypeName", 4, _("Weight", l))
    sql += lookup2("logtype", "LogTypeName", 5, _("Document", l))
    sql += lookup2("logtype", "LogTypeName", 6, _("GDPR Contact Opt-In", l))
    sql += lookup2("logtype", "LogTypeName", 7, _("Daily Observations", l))
    sql += medicalprofile(1, _("Examination", l), _("N/A"))
    sql += medicalprofile(2, _("Surgery", l), _("N/A"))
    sql += medicalprofile(3, _("Deflea", l), _("{0} Pipette", l).format(1))
    sql += medicalprofile(4, _("Wormer", l), _("{0} Tablet", l).format(1))
    sql += lookup2("pickuplocation", "LocationName", 1, _("Shelter", l))
    sql += lookup2("reservationstatus", "StatusName", 1, _("More Info Needed", l))
    sql += lookup2("reservationstatus", "StatusName", 2, _("Pending Vet Check", l))
    sql += lookup2("reservationstatus", "StatusName", 3, _("Pending Apartment Verification", l))
    sql += lookup2("reservationstatus", "StatusName", 4, _("Pending Home Visit", l))
    sql += lookup2("reservationstatus", "StatusName", 5, _("Pending Adoption", l))
    sql += lookup2("reservationstatus", "StatusName", 6, _("Changed Mind", l))
    sql += lookup2("reservationstatus", "StatusName", 7, _("Denied", l))
    sql += lookup2("reservationstatus", "StatusName", 8, _("Approved", l))
    sql += lookup1("site", "SiteName", 1, "main")
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
    sql += lookup2("transporttype", "TransportTypeName", 1, _("Adoption Event", l))
    sql += lookup2("transporttype", "TransportTypeName", 2, _("Foster Transfer", l))
    sql += lookup2("transporttype", "TransportTypeName", 3, _("Surrender Pickup", l))
    sql += lookup2("transporttype", "TransportTypeName", 4, _("Vet Visit", l))
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

def install_db_structure(dbo: Database) -> None:
    """
    Creates the db structure in the target database
    """
    asm3.al.info("creating default database schema", "dbupdate.install_default_data", dbo)
    sql = sql_structure(dbo)
    for s in sql.split(";"):
        if (s.strip() != ""):
            dbo.execute_dbupdate(s.strip())

def install_db_views(dbo: Database) -> None:
    """
    Installs all the database views.
    """
    def create_view(viewname: str, sql: str) -> None:
        try:
            dbo.execute_dbupdate( dbo.ddl_drop_view(viewname) )
            dbo.execute_dbupdate( dbo.ddl_add_view(viewname, sql) )
        except Exception as err:
            asm3.al.error("error creating view %s: %s" % (viewname, err), "dbupdate.install_db_views", dbo)

    # Set us upto date to stop race condition/other clients trying to install
    asm3.configuration.db_view_seq_version(dbo, str(LATEST_VERSION))
    create_view("v_adoption", asm3.movement.get_movement_query(dbo))
    create_view("v_animal", asm3.animal.get_animal_query(dbo))
    create_view("v_animalcontrol", asm3.animalcontrol.get_animalcontrol_query(dbo))
    create_view("v_animalfound", asm3.lostfound.get_foundanimal_query(dbo))
    create_view("v_animallost", asm3.lostfound.get_lostanimal_query(dbo))
    create_view("v_animalmedicaltreatment", asm3.medical.get_medicaltreatment_query(dbo))
    create_view("v_animalmedicalcombined", asm3.medical.get_medicalcombined_query(dbo))
    create_view("v_animaltest", asm3.medical.get_test_query(dbo))
    create_view("v_animalvaccination", asm3.medical.get_vaccination_query(dbo))
    create_view("v_animalwaitinglist", asm3.waitinglist.get_waitinglist_query(dbo))
    create_view("v_owner", asm3.person.get_person_query(dbo))
    create_view("v_ownercitation", asm3.financial.get_citation_query(dbo))
    create_view("v_ownerdonation", asm3.financial.get_donation_query(dbo))
    create_view("v_ownerlicence", asm3.financial.get_licence_query(dbo))
    create_view("v_ownertraploan", asm3.animalcontrol.get_traploan_query(dbo))
    create_view("v_ownervoucher", asm3.financial.get_voucher_query(dbo))

def install_db_sequences(dbo: Database) -> None:
    """
    Installs database sequences if supported and sets their initial values
    """
    for table in TABLES:
        if table in TABLES_NO_ID_COLUMN: continue
        initialvalue = dbo.get_id_max(table)
        dbo.execute_dbupdate(dbo.ddl_drop_sequence(table) )
        dbo.execute_dbupdate(dbo.ddl_add_sequence(table, initialvalue) )

def install_db_stored_procedures(dbo: Database) -> None:
    """
    Creates any special stored procedures we need in the target database
    """
    dbo.install_stored_procedures()

def install_default_data(dbo: Database, skip_config: bool = False) -> None:
    """
    Installs the default dataset into the database.
    skip_config: If true, does not insert default data into: configuration, role, userrole, users 
    """
    asm3.al.info("creating default data", "dbupdate.install_default_data", dbo)
    sql = sql_default_data(dbo, skip_config)
    for s in sql.split("|="):
        if s.strip() != "":
            dbo.execute_dbupdate(s.strip())

def install_default_reports(dbo: Database) -> None:
    """
    Installs the recommended/default reports
    """
    asm3.al.info("installing recommended reports", "dbupdate.install_default_reports", dbo)
    asm3.reports.install_recommended_smcom_reports(dbo, "install")

def reinstall_default_data(dbo: Database) -> None:
    """
    Reinstalls all default data for the current locale.  
    """
    for table in TABLES_LOOKUP:
        dbo.execute_dbupdate("DELETE FROM %s" % table)
    install_default_data(dbo, True)
    install_default_templates(dbo)
    install_default_onlineforms(dbo)
    install_default_reports(dbo)

def install_default_onlineforms(dbo: Database, removeFirst: bool = False) -> None:
    """
    Installs the default online forms into the database.
    removeFirst: if True, deletes existing online forms first.
    """
    path = dbo.installpath + "media/onlineform/"
    asm3.al.info("creating default online forms", "dbupdate.install_default_onlineforms", dbo)
    if removeFirst:
        asm3.al.info("removing existing forms from onlineform, onlineformfield", "dbupdate.install_default_onlineforms", dbo)
        dbo.execute_dbupdate("DELETE FROM onlineform")
        dbo.execute_dbupdate("DELETE FROM onlineformfield")
    for o in os.listdir(path):
        if o.endswith(".json"):
            try:
                asm3.onlineform.import_onlineform_json(dbo, asm3.utils.read_text_file(path + o))
            except Exception as err:
                asm3.al.error("error importing form: %s" % str(err), "dbupdate.install_default_onlineformms", dbo)

def install_default_templates(dbo: Database, removeFirst: bool = False) -> None:
    """
    Installs the default templates files into the db.
    removeFirst: if True, deletes all from templatedocument/templatehtml first.
    """
    def add_document_template_from_file(show, name, path, filename):
        install_document_template(dbo, show, name, path, filename)
    def add_html_template_from_files(name):
        install_html_template(dbo, name)
    path = dbo.installpath
    if removeFirst:
        asm3.al.info("removing templates from templatehtml and templatedocument", "dbupdate.install_default_templates", dbo)
        dbo.execute_dbupdate("DELETE FROM templatedocument")
        dbo.execute_dbupdate("DELETE FROM templatehtml")
    asm3.al.info("creating default templates", "dbupdate.install_default_templates", dbo)
    add_html_template_from_files("animalview")
    add_html_template_from_files("lostanimalview")
    add_html_template_from_files("foundanimalview")
    add_html_template_from_files("animalviewadoptable")
    add_html_template_from_files("animalviewcarousel")
    add_html_template_from_files("littlebox")
    add_html_template_from_files("responsive")
    add_html_template_from_files("plain")
    add_html_template_from_files("rss")
    add_html_template_from_files("slideshow")
    add_document_template_from_file("animal,movement", "adoption_form.html", "/templates", path + "media/templates/adoption_form.html")
    add_document_template_from_file("animal", "cat_assessment_form.html", "/templates", path + "media/templates/cat_assessment_form.html")
    add_document_template_from_file("animal", "cat_cage_card_report.html", "/templates", path + "media/templates/cat_cage_card_report.html")
    add_document_template_from_file("animal", "cat_information.html", "/templates", path + "media/templates/cat_information.html")
    add_document_template_from_file("animal", "dog_assessment_form.html", "/templates", path + "media/templates/dog_assessment_form.html")
    add_document_template_from_file("animal", "dog_cage_card_report.html", "/templates", path + "media/templates/dog_cage_card_report.html")
    add_document_template_from_file("animal", "dog_information.html", "/templates", path + "media/templates/dog_information.html")
    add_document_template_from_file("licence", "dog_license.html", "/templates", path + "media/templates/dog_license.html")
    add_document_template_from_file("animal", "fancy_cage_card.html", "/templates", path + "media/templates/fancy_cage_card.html")
    add_document_template_from_file("animal", "half_a4_cage_card.html", "/templates", path + "media/templates/half_a4_cage_card.html")
    add_document_template_from_file("movement", "homecheck_form.html", "/templates", path + "media/templates/homecheck_form.html")
    add_document_template_from_file("incident", "incident_information.html", "/templates", path + "media/templates/incident_information.html")
    add_document_template_from_file("payment", "invoice.html", "/templates", path + "media/templates/invoice.html")
    add_document_template_from_file("animal,movement", "microchip_form.html", "/templates", path + "media/templates/microchip_form.html")
    add_document_template_from_file("animal,movement", "petplan.html", "/templates", path + "media/templates/petplan.html")
    add_document_template_from_file("animal,movement", "rabies_certificate.html", "/templates", path + "media/templates/rabies_certificate.html")
    add_document_template_from_file("payment", "receipt.html", "/templates", path + "media/templates/receipt.html")
    add_document_template_from_file("payment", "receipt_tax.html", "/templates", path + "media/templates/receipt_tax.html")
    add_document_template_from_file("movement", "reclaim_release.html", "/templates", path + "media/templates/reclaim_release.html")
    add_document_template_from_file("movement", "reserved.html", "/templates", path + "media/templates/reserved.html")
    add_document_template_from_file("voucher", "spay_neuter_voucher.html", "/templates", path + "media/templates/spay_neuter_voucher.html")
    add_document_template_from_file("animal,movement", "rspca_adoption.html", "/templates/rspca", path + "media/templates/rspca/rspca_adoption.html")
    add_document_template_from_file("animal", "rspca_behaviour_observations_cat.html", "/templates/rspca", path + "media/templates/rspca/rspca_behaviour_observations_cat.html")
    add_document_template_from_file("animal", "rspca_behaviour_observations_dog.html", "/templates/rspca", path + "media/templates/rspca/rspca_behaviour_observations_dog.html")
    add_document_template_from_file("animal", "rspca_behaviour_observations_rabbit.html", "/templates/rspca", path + "media/templates/rspca/rspca_behaviour_observations_rabbit.html")
    add_document_template_from_file("animal", "rspca_dog_advice_leaflet.html", "/templates/rspca", path + "media/templates/rspca/rspca_dog_advice_leaflet.html")
    add_document_template_from_file("animal", "rspca_post_home_visit.html", "/templates/rspca", path + "media/templates/rspca/rspca_post_home_visit.html")
    add_document_template_from_file("animal", "rspca_transfer_of_ownership.html", "/templates/rspca", path + "media/templates/rspca/rspca_transfer_of_ownership.html")
    add_document_template_from_file("animal", "rspca_transfer_of_title.html", "/templates/rspca", path + "media/templates/rspca/rspca_transfer_of_title.html")

def install_document_template(dbo: Database, show: str, name: str, path: str, filename: str, use_max_id: bool = False):
    """ Install a document template """
    try:
        content = asm3.utils.read_binary_file(filename)
        dbo.insert("templatedocument", {
            "ID":       use_max_id and dbo.get_id_max("templatedocument") or dbo.get_id("templatedocument"),
            "Name":     name,
            "Path":     path,
            "ShowAt":   show,
            "Content":  asm3.utils.base64encode(content)
        }, generateID = False)
    except FileNotFoundError:
        asm3.al.warn(f"FileNotFound: {filename}", "dbupdate.install_document_template")

def install_html_template(dbo: Database, name: str, use_max_id: bool = False) -> None:
    """ Install an HTML template from a folder """
    try:
        head = asm3.utils.read_text_file(dbo.installpath + "media/internet/%s/head.html" % name)
        foot = asm3.utils.read_text_file(dbo.installpath + "media/internet/%s/foot.html" % name)
        body = asm3.utils.read_text_file(dbo.installpath + "media/internet/%s/body.html" % name)
        dbo.execute_dbupdate("DELETE FROM templatehtml WHERE Name = ?", [name])
        dbo.insert("templatehtml", {
            "ID":       use_max_id and dbo.get_id_max("templatehtml") or dbo.get_id("templatehtml"),
            "Name":     name,
            "*Header":  head,
            "*Body":    body,
            "*Footer":  foot,
            "IsBuiltIn": 0
        }, generateID = False)
    except FileNotFoundError:
        asm3.al.warn(f"FileNotFound: {name}", "dbupdate.install_html_template")

def install(dbo: Database) -> None:
    """
    Handles the install of the database
    path: The path to the current directory containing the asm source
    """
    install_db_structure(dbo)
    install_db_views(dbo)
    install_default_data(dbo)
    install_db_sequences(dbo)
    install_db_stored_procedures(dbo)
    install_default_templates(dbo)
    install_default_onlineforms(dbo)
    install_default_reports(dbo)

def dump(dbo: Database, includeConfig = True, includeDBFS = True, includeCustomReport = True, 
        includeData = True, includeNonASM2 = True, includeUsers = True, includeLKS = True, 
        includeLookups = True, deleteDBV = False, deleteFirst = True, deleteViewSeq = False, 
        escapeCR = "", uppernames = False, excludeDBFSTemplates=False, wrapTransaction = True) -> Generator[str, None, None]:
    """
    Dumps all of the data in the database as DELETE/INSERT statements.
    includeConfig - include the config table
    includeDBFS - include the dbfs table
    includeCustomReport - include the custom report table
    includeData - include data tables (animal, owner, etc)
    includeLookups - include lookup tables
    includeLKS - include static lks tables
    includeUsers - include user and role tables
    deleteDBV - issue DELETE DBV from config after dump to force update/checks
    deleteFirst - issue DELETE FROM statements before INSERTs
    deleteViewSeq - issue DELETE DBViewSeqVersion from config after dump
    escapeCR - A substitute for any \n characters found in values
    excludeDBFSTemplates - Throw away dbfs lines where the path is internet or template
    uppernames - upper case table names in the output
    wrapTransaction - wrap a transaction around the dump

    This is a generator function to save memory.
    """
    if wrapTransaction: yield "BEGIN;\n"
    for t in TABLES:
        if not includeDBFS and t == "dbfs": continue
        if not includeCustomReport and t == "customreport": continue
        if not includeConfig and t == "configuration": continue
        if not includeData and t in TABLES_DATA: continue
        if not includeUsers and (t == "users" or t == "userrole" or t == "role" or t == "accountsrole" or t == "customreportrole"): continue
        if not includeLKS and t.startswith("lks"): continue
        if not includeLookups and t in TABLES_LOOKUP: continue
        # ASM2_COMPATIBILITY
        if not includeNonASM2 and t not in TABLES_ASM2 : continue
        outtable = t
        if uppernames: outtable = t.upper()
        if deleteFirst: 
            yield "DELETE FROM %s;\n" % outtable
        try:
            sys.stderr.write("dumping %s.., \n" % t)
            for x in dbo.query_to_insert_sql("SELECT * FROM %s" % t, outtable, escapeCR):
                if excludeDBFSTemplates and t == "dbfs" and \
                    (x.find("template") != -1 or x.find("internet") != -1 or x.find("report") != -1): 
                    continue
                yield x
        except:
            em = str(sys.exc_info())
            sys.stderr.write("%s: WARN: %s\n" % (t, em))
    if deleteViewSeq: yield "DELETE FROM configuration WHERE ItemName LIKE 'DBViewSeqVersion';\n"
    if deleteDBV: yield "DELETE FROM configuration WHERE ItemName LIKE 'DBV';\n"
    if wrapTransaction: yield "COMMIT;\n"

def dump_dbfs_base64(dbo: Database) -> Generator[str, None, None]:
    """
    Generator function that dumps the DBFS table, reading every single
    file and including it as old style base64 in the Content column.
    This can be used to get an old style dbfs from newer storage mechanisms for export.
    """
    yield "DELETE FROM dbfs;\n"
    rows = dbo.query("SELECT ID, Name, Path FROM dbfs ORDER BY ID")
    for r in rows:
        content = ""
        url = ""
        # Only try and read the dbfs file if it has an extension and is actually a file
        if r["NAME"].find(".") != -1:
            try:
                content = asm3.dbfs.get_string_id(dbo, r["ID"])
            except:
                # Ignore if we couldn't read, leaving content blank
                pass
        if content != "":
            url = "base64:"
            content = asm3.utils.base64encode(content)
        yield "INSERT INTO dbfs (ID, Name, Path, URL, Content) VALUES (%d, '%s', '%s', '%s', '%s');\n" % (r["ID"], r["NAME"], r["PATH"], url, content)
        del content

def dump_dbfs_files(dbo: Database) -> Generator[str, None, None]:
    """
    Generator function that dumps the DBFS table, reading every single
    file and outputting it to /tmp/dump_dbfs_files. 
    The content column output will be null and the URL updated to
    file:[DBFSID].[Extension]
    This can be used to extract large dbfs tables to files and get a copy
    without changing the original table. It's easy to switch file for s3
    post insert if necessary.
    """
    yield "DELETE FROM dbfs;\n"
    rows = dbo.query("SELECT ID, Name, Path FROM dbfs ORDER BY ID")
    for r in rows:
        name = r.NAME
        content = ""
        url = ""
        # Only try and read the dbfs file if it has an extension and is actually a file
        if name.find(".") != -1:
            try:
                content = asm3.dbfs.get_string_id(dbo, r.ID)
            except:
                # Ignore if we couldn't read, leaving content blank
                pass
        if content != "":
            filename = "%s.%s" % (r.ID, name[name.rfind(".")+1:])
            url = "file:%s" % filename
            asm3.utils.write_binary_file("/tmp/dump_dbfs_files/%s" % filename, content)
        yield "INSERT INTO dbfs (ID, Name, Path, URL, Content) VALUES (%d, '%s', '%s', '%s', NULL);\n" % (r.ID, r.NAME, r.PATH, url)
        del content

def dump_hsqldb(dbo: Database, includeDBFS: bool = True) -> Generator[str, None, None]:
    """
    Produces a dump in hsqldb format for use with ASM2
    generator function.
    """
    # ASM2_COMPATIBILITY
    hdbo = asm3.db.get_dbo("HSQLDB")
    yield sql_structure(hdbo)
    for x in dump(dbo, includeNonASM2 = False, includeDBFS = includeDBFS, escapeCR = " ", includeUsers = False, wrapTransaction = False):
        yield x
    yield "DELETE FROM users;\n"
    yield "INSERT INTO users (ID, UserName, RealName, Password, SuperUser, OwnerID, SecurityMap, RecordVersion) VALUES " \
        "(1, 'user', 'Default', 'd107d09f5bbe40cade3de5c71e9e9b7', 1, 0, '', 0);\n"
    yield "DELETE FROM configuration WHERE ItemName LIKE 'DatabaseVersion' OR ItemName LIKE 'SMDBLocked';\n"
    yield "INSERT INTO configuration (ItemName, ItemValue) VALUES ('DatabaseVersion', '2870');\n"

def dump_lookups(dbo: Database) -> Generator[str, None, None]:
    """
    Dumps only the lookup tables. Useful for smcom where we get people requesting a 
    new account with lookups from another account
    """
    for x in dump(dbo, includeDBFS = False, includeConfig = False, includeData = False, includeUsers = False, deleteDBV = True, deleteViewSeq = True, wrapTransaction = True):
        yield x

def dump_smcom(dbo: Database) -> Generator[str, None, None]:
    """
    Dumps the database in a convenient format for import to sheltermanager.com
    generator function.
    For dumps that came from ASM2, may also want to:
        1. Remove the DELETE FROM dbfs line manually from the output.
        2. Remove the userrole and users tables from the output.
    """
    # For ASM2 sources, we remove some constraints that were added in ASM3 to make import easy
    yield "\\set ON_ERROR_STOP\n"
    yield "ALTER TABLE animal ALTER AcceptanceNumber DROP NOT NULL;\n"
    yield "ALTER TABLE animal ALTER IdentichipNumber DROP NOT NULL;\n"
    yield "ALTER TABLE animal ALTER TattooNumber DROP NOT NULL;\n"
    yield "ALTER TABLE animal ALTER BondedAnimalID DROP NOT NULL;\n"
    yield "ALTER TABLE animal ALTER BondedAnimal2ID DROP NOT NULL;\n"
    yield "ALTER TABLE animalvaccination ALTER Cost DROP NOT NULL;\n"
    for x in dump(dbo, includeDBFS = True, includeConfig = False, includeUsers = True, includeLKS = False, deleteDBV = True, deleteViewSeq = True, excludeDBFSTemplates = True, wrapTransaction = True):
        yield x

def dump_merge(dbo: Database, deleteViewSeq: bool = True) -> Generator[str, None, None]:
    """
    Produces a special type of dump - it renumbers the IDs into a higher range 
    so that they can be inserted into another database.
    deleteViewSeq: if True, deletes the view/seq version from the configuration table after.
    """
    ID_OFFSET = 100000
    def fix_and_dump(table: str, fields: List[str]) -> str:
        rows = dbo.query("SELECT * FROM %s" % table)
        s = []
        for r in rows:
            # Add ID_OFFSET to all ID fields in the rows
            for f in fields:
                f = f.upper()
                # Don't add anything to these two, but prefix them so merging is obvious
                if f == "ADOPTIONNUMBER" or f == "SHELTERCODE":
                    r[f] = "MG" + r[f]
                # DBFS URLs prefixed with file: or s3:
                # (note that files will have to be renamed manually)
                elif f == "URL":
                    if r[f] and (r[f].startswith("file:") or r[f].startswith("s3:")):
                        v = r[f]
                        prefix = "file"
                        if v.startswith("s3:"): prefix = "s3"
                        ext = v[v.rfind(".")+1:]
                        num = asm3.utils.atoi(v) + ID_OFFSET
                        r[f] = "%s:%s.%s" % ( prefix, num, ext )
                elif r[f] is not None:
                    r[f] += ID_OFFSET
            # Make any lookup values we copy over inactive
            if "ISRETIRED" in r: 
                r.ISRETIRED = 1 
            s.append(dbo.row_to_insert_sql(table, r, escapeCR = ""))
        return "\n".join(s)

    yield fix_and_dump("additional", [ "AdditionalFieldID", "LinkID" ])
    yield fix_and_dump("additionalfield", [ "ID" ])
    yield fix_and_dump("adoption", [ "ID", "AnimalID", "AdoptionNumber", "OwnerID", "RetailerID", "OriginalRetailerMovementID" ])
    yield fix_and_dump("animal", [ "ID", "AnimalTypeID", "BreedID", "Breed2ID", "SpeciesID", "ShelterLocation", "ShelterCode", "BondedAnimalID", "BondedAnimal2ID", "PickupLocationID", "JurisdictionID", "OwnersVetID", "CurrentVetID", "OriginalOwnerID", "BroughtInByOwnerID", "ActiveMovementID" ])
    yield fix_and_dump("animalcontrol", [ "ID", "CallerID", "VictimID", "PickupLocationID", "JurisdictionID", "OwnerID", "Owner2ID", "Owner3ID" ])
    yield fix_and_dump("animalcontrolanimal", [ "AnimalID", "AnimalControlID" ])
    yield fix_and_dump("animalcost", [ "ID", "AnimalID", "CostTypeID" ])
    yield fix_and_dump("breed", [ "ID" ])
    yield fix_and_dump("costtype", [ "ID" ])
    yield fix_and_dump("animaldiet", [ "ID", "AnimalID" ])
    yield fix_and_dump("animalfound", [ "ID", "OwnerID", "AnimalTypeID", "BreedID" ])
    yield fix_and_dump("animallitter", [ "ID", "ParentAnimalID" ])
    yield fix_and_dump("animallost", [ "ID", "OwnerID", "AnimalTypeID", "BreedID" ])
    yield fix_and_dump("animalmedical", [ "ID", "AnimalID", "MedicalProfileID" ])
    yield fix_and_dump("animalmedicaltreatment", [ "ID", "AnimalID", "AnimalMedicalID" ])
    yield fix_and_dump("animalpublished", [ "AnimalID" ])
    yield fix_and_dump("animaltest", [ "ID", "AnimalID", "TestTypeID", "TestResultID" ])
    yield fix_and_dump("animaltype", [ "ID", ])
    yield fix_and_dump("animaltransport", [ "ID", "AnimalID", "DriverOwnerID", "PickupOwnerID", "DropoffOwnerID" ])
    yield fix_and_dump("animalvaccination", [ "ID", "AnimalID", "VaccinationID" ])
    yield fix_and_dump("animalwaitinglist", [ "ID", "OwnerID" ])
    yield fix_and_dump("diary", [ "ID", "LinkID" ])
    yield fix_and_dump("internallocation", [ "ID", ])
    yield fix_and_dump("jurisdiction", [ "ID", ])
    yield fix_and_dump("lkanimalflags", [ "ID", ])
    yield fix_and_dump("lkownerflags", [ "ID", ])
    yield fix_and_dump("lkworktype", [ "ID", ])
    yield fix_and_dump("log", [ "ID", "LinkID" ])
    yield fix_and_dump("media", [ "ID", "DBFSID", "LinkID" ])
    yield fix_and_dump("medicalprofile", [ "ID" ])
    yield fix_and_dump("owner", [ "ID", "HomeCheckedBy", "JurisdictionID" ])
    yield fix_and_dump("ownercitation", [ "ID", "OwnerID", "AnimalControlID" ])
    yield fix_and_dump("ownerdonation", [ "ID", "AnimalID", "OwnerID", "MovementID", "DonationTypeID" ])
    yield fix_and_dump("donationtype", [ "ID", ])
    yield fix_and_dump("ownerinvestigation", [ "ID", "OwnerID" ])
    yield fix_and_dump("ownerlicence", [ "ID", "OwnerID", "AnimalID", "LicenceTypeID" ])
    yield fix_and_dump("licencetype", [ "ID", ])
    yield fix_and_dump("ownerrota", [ "ID", "OwnerID" ])
    yield fix_and_dump("ownertraploan", [ "ID", "OwnerID" ])
    yield fix_and_dump("ownervoucher", [ "ID", "OwnerID", "VoucherID" ])
    yield fix_and_dump("pickuplocation", [ "ID" ])
    yield fix_and_dump("species", [ "ID" ])
    yield fix_and_dump("stocklevel", [ "ID", "StockLocationID" ])
    yield fix_and_dump("stocklocation", [ "ID", ])
    yield fix_and_dump("stockusage", [ "ID", "StockLevelID" ])
    yield fix_and_dump("templatedocument", [ "ID", ])
    yield fix_and_dump("templatehtml", [ "ID", ])
    yield fix_and_dump("testtype", [ "ID", ])
    yield fix_and_dump("testresult", [ "ID", ])
    yield fix_and_dump("vaccinationtype", [ "ID", ])
    yield fix_and_dump("voucher", [ "ID", ])
    yield fix_and_dump("dbfs", [ "ID", "URL" ])
    if deleteViewSeq: yield "DELETE FROM configuration WHERE ItemName LIKE 'DBViewSeqVersion';\n"

def diagnostic(dbo: Database) -> Dict[str, int]:
    """
    1. Checks for and removes orphaned records (of some types)
    2. Checks for and fixes animal records with too many web or doc preferred images
    """
    def orphan(table: str, linktable: str, leftfield: str, rightfield: str) -> int:
        count = dbo.query_int("SELECT COUNT(*) FROM %s LEFT OUTER JOIN %s ON %s = %s " \
            "WHERE %s Is Null" % (table, linktable, leftfield, rightfield, rightfield))
        if count > 0:
            dbo.execute_dbupdate("DELETE FROM %s WHERE %s IN " \
                "(SELECT %s FROM %s LEFT OUTER JOIN %s ON %s = %s WHERE %s Is Null)" % (
                table, leftfield, leftfield, table, linktable, leftfield, rightfield, rightfield))
        return count

    def mediapref() -> int:
        duplicatepic = 0
        for a in dbo.query("SELECT ID, " \
            "(SELECT COUNT(*) FROM media WHERE LinkID = animal.ID AND LinkTypeID = 0) AS TotalMedia, " \
            "(SELECT COUNT(*) FROM media WHERE LinkID = animal.ID AND LinkTypeID = 0 AND WebsitePhoto = 1) AS TotalWeb, " \
            "(SELECT COUNT(*) FROM media WHERE LinkID = animal.ID AND LinkTypeID = 0 AND DocPhoto = 1) AS TotalDoc, " \
            "(SELECT MAX(ID) FROM media WHERE LinkID = animal.ID AND LinkTypeID = 0 AND ExcludeFromPublish = 0 AND MediaName LIKE '%.jpg') AS LatestImage " \
            "FROM animal"):
            if a["TOTALMEDIA"] > 0 and a["TOTALWEB"] > 1:
                # Too many preferred images
                dbo.execute("UPDATE media SET DocPhoto=0, WebsitePhoto=0 WHERE LinkID = ? AND LinkTypeID = 0 AND ID <> ?", (a.ID, a.LATESTIMAGE))
                dbo.execute("UPDATE media SET DocPhoto=1, WebsitePhoto=1 WHERE ID = ?", [a.LATESTIMAGE])
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

def fix_preferred_photos(dbo: Database) -> int:
    """
    Resets the web and doc preferred flags on all photos to the latest one for all media records.
    This is useful in situations where users have borked them by running queries in the past.
    This should only be used as a last resort as all previous preferred photo info will be deleted.
    """
    rows = dbo.query("SELECT LinkID, LinkTypeID, ID FROM media ORDER BY LinkID, LinkTypeID, ID DESC")
    batch = []
    lastlinkid = 0
    lastlinktypeid = 0
    for r in rows:
        if lastlinkid != r.linkid and lastlinktypeid != r.linktypeid:
            batch.append([r.id])
            lastlinkid = r.linkid
            lastlinktypeid = r.linktypeid
    dbo.execute_dbupdate("UPDATE media SET WebsitePhoto=0, DocPhoto=0")
    dbo.execute_many("UPDATE media SET WebsitePhoto=1, DocPhoto=1 WHERE ID=?", batch, override_lock=True) 
    return len(batch)

def replace_html_entities(dbo: Database) -> None:
    """
    Substitutes HTML entities in every text field in the database with their appropriate unicode codepoint.
    Used for the transition between v44 and v45 where we stopped storing unicode as HTML entities and an
    existing database needs to be switched. 
    Only really needs to be run for non-English databases (ie. NOT en, en_GB, and en_AU)
    """
    cols = {
        "accounts": [ "Code", "Description" ],
        "accountstrx": [ "Description" ],
        #"additional": [ "Value" ], # Handled separately due to lack of ID field
        "additionalfield": [ "FieldName", "FieldLabel", "Tooltip", "LookupValues", "DefaultValue" ],
        "adoption": [ "Comments", "ReasonForReturn" ],
        "animal": [ "AnimalName", "BreedName", "Markings", "AgeGroup", "HiddenAnimalDetails", "AnimalComments", 
            "ReasonForEntry", "ReasonNO", "HealthProblems", "PTSReason", "AdditionalFlags", "ShelterLocationUnit", 
            "TimeOnShelter", "TotalTimeOnShelter", "AgeGroupActiveMovement", "AnimalAge" ],
        "animalcontrol": [ "CallNotes", "DispatchAddress", "DispatchTown", "DispatchCounty", "DispatchPostcode",
                "DispatchLatLong", "DispatchedACO", "AnimalDescription", "AgeGroup"],
        "animalcost": [ "Description" ],
        "animaldiet": [ "Comments" ],
        "animalfound": [ "AgeGroup", "DistFeat", "AreaFound", "AreaPostcode", "Comments" ],
        "animallitter": [ "Comments" ],
        "animallost": [ "AgeGroup", "DistFeat", "AreaLost", "AreaPostcode", "Comments" ],
        "animalmedical": [ "TreatmentName", "Dosage", "Comments" ],
        "animalmedicaltreatment": [ "GivenBy", "Comments" ],
        "animaltest": [ "Comments" ],
        "animaltransport": [ "TransportReference", "PickupAddress", "PickupTown", "PickupCounty", "PickupPostcode", 
                "PickupCountry", "DropoffAddress", "DropoffTown", "DropoffCounty", "DropoffPostcode", "DropoffCountry", 
                "Comments" ],
        "animaltype": [ "AnimalType", "AnimalDescription" ],
        "animalvaccination": [ "GivenBy", "Manufacturer", "Comments" ],
        "animalwaitinglist": [ "AnimalDescription", "ReasonForWantingToPart", "ReasonForRemoval", "Comments" ],
        "basecolour": [ "BaseColour", "BaseColourDescription" ],
        "breed": [ "BreedName", "BreedDescription" ],
        "citationtype": [ "CitationName", "CitationDescription" ],
        "clinicappointment": [ "ApptFor", "ReasonForAppointment", "Comments" ],
        "clinicinvoiceitem": [ "Description" ],
        "costtype": [ "CostTypeName" ],
        "customreport": [ "Title", "Category", "SQLCommand", "HTMLBody", "Description" ],
        "deathreason": [ "ReasonName", "ReasonDescription" ],
        "diary": [ "DiaryForName", "Subject", "Note", "Comments" ],
        "diarytaskdetail": [ "WhoFor", "Subject", "Note" ],
        "diarytaskhead": [ "Name" ],
        "diet": [ "DietName", "DietDescription" ],
        "donationtype": [ "DonationName", "DonationDescription" ],
        "donationpayment": [ "PaymentName", "PaymentDescription" ],
        "entryreason": [ "ReasonName", "ReasonDescription" ],
        "incidentcompleted": [ "CompletedName", "CompletedDescription" ],
        "incidenttype": [ "IncidentName", "IncidentDescription" ],
        "internallocation": [ "LocationName", "LocationDescription", "Units" ],
        "jurisdiction": [ "JurisdictionName", "JurisdictionDescription" ],
        "licencetype": [ "LicenceTypeName", "LicenceTypeDescription" ],
        "lksaccounttype": [ "AccountType" ],
        "lkanimalflags": [ "Flag" ],
        "lkownerflags": [ "Flag" ],
        "lksclinicstatus": [ "Status" ],
        "lkcoattype": [ "CoatType" ],
        "lksex": [ "Sex" ],
        "lksize": [ "Size" ],
        "lksmovementtype": [ "MovementType" ],
        "lksfieldlink": [ "LinkType" ],
        "lksfieldtype": [ "FieldType" ],
        "lksmedialink": [ "LinkType" ],
        "lksmediatype": [ "MediaType" ],
        "lksdiarylink": [ "LinkType" ],
        "lksdonationfreq": [ "Frequency" ],
        "lksloglink": [ "LinkType" ],
        "lksrotatype": [ "RotaType" ],
        "lkstransportstatus": [ "Name" ],
        "lkurgency": [ "Urgency" ],
        "lksyesno": [ "Name" ],
        "lksynun": [ "Name" ],
        "lksynunk": [ "Name" ],
        "lksposneg": [ "Name" ],
        "lkworktype": [ "WorkType" ],
        "log": [ "Comments" ],
        "logtype": [ "LogTypeName", "LogTypeDescription" ],
        "media": [ "MediaNotes" ],
        "medicalprofile": [ "ProfileName", "TreatmentName", "Dosage", "Comments" ],
        "messages": [ "ForName", "Message" ],
        "onlineform": [ "Name", "Description" ],
        "onlineformfield": [ "Label", "Lookups" ],
        "owner": [ "OwnerCode", "OwnerTitle", "OwnerInitials", "OwnerForeNames", "OwnerSurname", "OwnerName", 
            "OwnerAddress", "OwnerTown", "OwnerCounty", "OwnerPostcode", "OwnerCountry", "LatLong", "HomeTelephone",
            "WorkTelephone", "MobileTelephone", "EmailAddress", "Comments", "MembershipNumber", "AdditionalFlags",
            "HomeCheckAreas", "MatchCommentsContain" ],
        "ownercitation": [ "Comments" ],
        "ownerdonation": [ "ChequeNumber", "Comments" ],
        "ownerinvestigation": [ "Notes" ],
        "ownerlicence": [ "LicenceNumber", "Comments" ],
        "ownerrota": [ "Comments" ],
        "ownertraploan": [ "TrapNumber", "Comments" ],
        "ownervoucher": [ "VoucherCode", "Comments" ],
        "pickuplocation": [ "LocationName", "LocationDescription" ],
        "reservationstatus": [ "StatusName", "StatusDescription" ],
        "role": [ "Rolename" ],
        "site": [ "SiteName" ],
        "species": [ "SpeciesName", "SpeciesDescription" ],
        "stocklevel": [ "Name", "UnitName", "Description" ],
        "stocklocation": [ "LocationName", "LocationDescription" ],
        "stockusage": [ "Comments" ],
        "stockusagetype": [ "UsageTypeName", "UsageTypeDescription" ], 
        "templatedocument": [ "Name", "Path" ],
        "templatehtml": [ "Name" ],
        "testtype": [ "TestName", "TestDescription" ],
        "testresult": [ "ResultName", "ResultDescription" ],
        "traptype": [ "TrapTypeName", "TrapTypeDescription" ],
        "transporttype": [ "TransportTypeName", "TransportTypeDescription" ],
        "users": [ "UserName", "RealName" ],
        "voucher": [ "VoucherName", "VoucherDescription" ],
        "vaccinationtype": [ "VaccinationType", "VaccinationDescription" ]
    }
    # Handle additional fields separately due to their lack of ID field
    batch = []
    for r in dbo.query("SELECT LinkType, LinkID, AdditionalFieldID, Value FROM additional WHERE Value LIKE '%&#%'"):
        batch.append(( asm3.utils.decode_html(r.VALUE), r.LINKTYPE, r.LINKID, r.ADDITIONALFIELDID ))
    asm3.al.info(f"additional ({len(batch)} rows)", "dbupdate.replace_html_entities", dbo)
    dbo.execute_many("UPDATE additional SET Value=? WHERE LinkType=? AND LinkID=? AND AdditionalFieldID=?", batch)
    for table, fields in cols.items():
        batch = []
        rows = dbo.query(f"SELECT ID, {','.join(fields)} FROM {table} ORDER BY ID")
        batchq = f"UPDATE {table} SET {','.join([ f + '=?' for f in fields ])} WHERE ID=?"
        for r in rows:
            ibatch = []
            for f in fields:
                ibatch.append(asm3.utils.decode_html(r[f.upper()]))
            ibatch.append(r.ID)
            batch.append(ibatch)
        dbo.execute_many(batchq, batch)
        asm3.al.info(f"{table} ({len(batch)} rows)", "dbupdate.replace_html_entities", dbo)
    if asm3.smcom.active(): asm3.smcom.vacuum_full(dbo)

def check_for_updates(dbo: Database) -> bool:
    """
    Checks to see what version the database is on and whether or
    not it needs to be upgraded. 
    Returns true if the database needs upgrading.
    """
    dbv = int(asm3.configuration.dbv(dbo))
    return dbv < LATEST_VERSION

def check_for_view_seq_changes(dbo: Database) -> bool:
    """
    Checks to see whether we need to recreate our views and
    sequences by looking to see if the current database version is 
    different. 
    Returns True if we need to update.
    """
    return asm3.configuration.db_view_seq_version(dbo) != str(LATEST_VERSION)

def reset_db(dbo: Database) -> None:
    """
    Resets a database by removing all data from non-lookup tables.
    """
    for t in TABLES_DATA:
        dbo.execute_dbupdate("DELETE FROM %s" % t)
    install_db_sequences(dbo)

def perform_updates(dbo: Database) -> str:
    """
    Performs any updates that need to be run against the database. 
    Returns the new database version.
    """
    # Lock the database - fail silently if we couldn't lock it
    if not asm3.configuration.db_lock(dbo): return ""

    try:
        # Go through our updates to see if any need running
        ver = int(asm3.configuration.dbv(dbo))
        for v in VERSIONS:
            if ver < v:
                asm3.al.info("updating database to version %d" % v, "dbupdate.perform_updates", dbo)
                # Current db version is below this update, run it
                try:
                    globals()["update_" + str(v)](dbo)
                except:
                    asm3.al.error("DB Update Error: %s" % str(sys.exc_info()[0]), "dbupdate.perform_updates", dbo, sys.exc_info())
                # Update the version
                asm3.configuration.dbv(dbo, str(v))
                ver = v
        
        # Return the new db version
        asm3.configuration.db_unlock(dbo)
        return asm3.configuration.dbv(dbo)
    finally:
        # Unlock the database for updates before we leave
        asm3.configuration.db_unlock(dbo)

def perform_updates_stdout(dbo: Database, stoponexc = False) -> None:
    """
    Performs any updates that need to be run against the database. 
    Intended to be called by testing functions as this outputs to stdout.
    """
    # Go through our updates to see if any need running
    ver = int(asm3.configuration.dbv(dbo))
    for v in VERSIONS:
        if ver < v:
            print("update_%s" % v)
            try:
                globals()["update_%s" % v](dbo)
            except Exception as err:
                import traceback
                print("ERROR: %s" % err)
                print(traceback.format_exc())
                if stoponexc: return
            asm3.configuration.dbv(dbo, str(v))
            ver = v

def add_column(dbo: Database, table: str, column: str, coltype: str) -> None:
    dbo.execute_dbupdate( dbo.ddl_add_column(table, column, coltype) )

def add_index(dbo: Database, indexname: str, tablename: str, fieldname: str, unique: bool = False, partial: bool = False) -> None:
    dbo.execute_dbupdate( dbo.ddl_add_index(indexname, tablename, fieldname, unique, partial) )

def drop_column(dbo: Database, table: str, column: str) -> None:
    dbo.execute_dbupdate( dbo.ddl_drop_column(table, column) )

def drop_index(dbo: Database, indexname: str, tablename: str) -> None:
    try:
        dbo.execute_dbupdate( dbo.ddl_drop_index(indexname, tablename) )
    except:
        pass

def modify_column(dbo: Database, table: str, column: str, newtype: str, using: str = "") -> None:
    dbo.execute_dbupdate( dbo.ddl_modify_column(table, column, newtype, using) )

def column_exists(dbo: Database, table: str, column: str) -> bool:
    """ Returns True if the column exists for the table given """
    try:
        dbo.query("SELECT %s FROM %s" % (column, table), limit=1)
        return True
    except:
        return False

def remove_asm2_compatibility(dbo: Database) -> None:
    """
    These are fields that we only include for compatibility with ASM2.
    ASM3 doesn't read or write to them any more.
    One day, when we have no more ASM2 users on sheltermanager.com,
    and we never need to import from ASM2, we will be able to remove these.
    """
    # ASM2_COMPATIBILITY
    dbo.execute_dbupdate("ALTER TABLE users DROP COLUMN SecurityMap")
    dbo.execute_dbupdate("ALTER TABLE animal DROP COLUMN SmartTagSentDate")
    dbo.execute_dbupdate("ALTER TABLE media DROP COLUMN LastPublished")
    dbo.execute_dbupdate("ALTER TABLE media DROP COLUMN LastPublishedPF")
    dbo.execute_dbupdate("ALTER TABLE media DROP COLUMN LastPublishedAP")
    dbo.execute_dbupdate("ALTER TABLE media DROP COLUMN LastPublishedP911")
    dbo.execute_dbupdate("ALTER TABLE media DROP COLUMN LastPublishedRG")

def asm2_dbfs_put_file(dbo: Database, name: str, path: str, filename: str):
    """ A version of asm3.dbfs.put_file that is compatible with asm2 databases with no URL column """
    # NOTE: This doesn't create the empty name/path elements because asm3 does not need them,
    # asm2 only used them for visualising the files as a tree.
    return dbo.insert("dbfs", {
        "ID": dbo.get_id_max("dbfs"),
        "Name": name,
        "Path": path,
        "Content": asm3.utils.base64encode(asm3.utils.read_binary_file(filename))
    }, generateID=False)

def update_3000(dbo: Database) -> None:
    path = dbo.installpath
    asm2_dbfs_put_file(dbo, "adoption_form.html", "/templates", path + "media/templates/adoption_form.html")
    asm2_dbfs_put_file(dbo, "cat_assessment_form.html", "/templates", path + "media/templates/cat_assessment_form.html")
    asm2_dbfs_put_file(dbo, "cat_cage_card.html", "/templates", path + "media/templates/cat_cage_card.html")
    asm2_dbfs_put_file(dbo, "cat_information.html", "/templates", path + "media/templates/cat_information.html")
    asm2_dbfs_put_file(dbo, "dog_assessment_form.html", "/templates", path + "media/templates/dog_assessment_form.html")
    asm2_dbfs_put_file(dbo, "dog_cage_card.html", "/templates", path + "media/templates/dog_cage_card.html")
    asm2_dbfs_put_file(dbo, "dog_information.html", "/templates", path + "media/templates/dog_information.html")
    asm2_dbfs_put_file(dbo, "dog_license.html", "/templates", path + "media/templates/dog_license.html")
    asm2_dbfs_put_file(dbo, "fancy_cage_card.html", "/templates", path + "media/templates/fancy_cage_card.html")
    asm2_dbfs_put_file(dbo, "half_a4_cage_card.html", "/templates", path + "media/templates/half_a4_cage_card.html")
    asm2_dbfs_put_file(dbo, "homecheck_form.html", "/templates", path + "media/templates/homecheck_form.html")
    asm2_dbfs_put_file(dbo, "invoice.html", "/templates", path + "media/templates/invoice.html")
    asm2_dbfs_put_file(dbo, "microchip_form.html", "/templates", path + "media/templates/microchip_form.html")
    asm2_dbfs_put_file(dbo, "petplan.html", "/templates", path + "media/templates/petplan.html")
    asm2_dbfs_put_file(dbo, "rabies_certificate.html", "/templates", path + "media/templates/rabies_certificate.html")
    asm2_dbfs_put_file(dbo, "receipt.html", "/templates", path + "media/templates/receipt.html")
    asm2_dbfs_put_file(dbo, "receipt_tax.html", "/templates", path + "media/templates/receipt_tax.html")
    asm2_dbfs_put_file(dbo, "reserved.html", "/templates", path + "media/templates/reserved.html")
    asm2_dbfs_put_file(dbo, "spay_neuter_voucher.html", "/templates", path + "media/templates/spay_neuter_voucher.html")
    asm2_dbfs_put_file(dbo, "rspca_adoption.html", "/templates/rspca", path + "media/templates/rspca/rspca_adoption.html")
    asm2_dbfs_put_file(dbo, "rspca_behaviour_observations_cat.html", "/templates/rspca", path + "media/templates/rspca/rspca_behaviour_observations_cat.html")
    asm2_dbfs_put_file(dbo, "rspca_behaviour_observations_dog.html", "/templates/rspca", path + "media/templates/rspca/rspca_behaviour_observations_dog.html")
    asm2_dbfs_put_file(dbo, "rspca_behaviour_observations_rabbit.html", "/templates/rspca", path + "media/templates/rspca/rspca_behaviour_observations_rabbit.html")
    asm2_dbfs_put_file(dbo, "rspca_dog_advice_leaflet.html", "/templates/rspca", path + "media/templates/rspca/rspca_dog_advice_leaflet.html")
    asm2_dbfs_put_file(dbo, "rspca_post_home_visit.html", "/templates/rspca", path + "media/templates/rspca/rspca_post_home_visit.html")
    asm2_dbfs_put_file(dbo, "rspca_transfer_of_ownership.html", "/templates/rspca", path + "media/templates/rspca/rspca_transfer_of_ownership.html")
    asm2_dbfs_put_file(dbo, "rspca_transfer_of_title.html", "/templates/rspca", path + "media/templates/rspca/rspca_transfer_of_title.html")
    asm2_dbfs_put_file(dbo, "nopic.jpg", "/reports", path + "media/reports/nopic.jpg")
    fields = ",".join([
        dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
        dbo.ddl_add_table_column("Added", dbo.type_datetime, False),
        dbo.ddl_add_table_column("Expires", dbo.type_datetime, False),
        dbo.ddl_add_table_column("CreatedBy", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("Priority", dbo.type_integer, False),
        dbo.ddl_add_table_column("Message", dbo.type_longtext, False)
    ])
    dbo.execute_dbupdate( dbo.ddl_add_table("messages", fields) )
    add_index(dbo, "messages_Expires", "messages", "Expires")

def update_3001(dbo: Database) -> None:
    dbo.execute_dbupdate("DELETE FROM configuration WHERE ItemName LIKE 'MappingService%'")
    dbo.execute_dbupdate("INSERT INTO configuration VALUES ('%s', '%s')" % ( "MappingServiceLinkURL", "http://maps.google.com/maps?q={0}" ))
    dbo.execute_dbupdate("INSERT INTO configuration VALUES ('%s', '%s')" % ( "MappingServiceEmbeddedURL", "https://maps.googleapis.com/maps/api/staticmap?center={0}&size=250x250&maptype=roadmap&sensor=false"))
    if 0 == dbo.query_int("SELECT COUNT(ItemName) FROM configuration WHERE ItemName LIKE 'SystemTheme'"):
        dbo.execute_dbupdate("DELETE FROM configuration WHERE ItemName LIKE 'SystemTheme'")
        dbo.execute_dbupdate("INSERT INTO configuration VALUES ('%s', '%s')" % ( "SystemTheme", "smoothness" ))
    if 0 == dbo.query_int("SELECT COUNT(ItemName) FROM configuration WHERE ItemName LIKE 'Timezone'"):
        dbo.execute_dbupdate("DELETE FROM configuration WHERE ItemName LIKE 'Timezone'")
        dbo.execute_dbupdate("INSERT INTO configuration VALUES ('%s', '%s')" % ( "Timezone", "0" ))

def update_3002(dbo: Database) -> None:
    add_column(dbo, "users", "IPRestriction", dbo.type_longtext)
    dbo.execute_dbupdate("CREATE TABLE role (ID INTEGER NOT NULL PRIMARY KEY, " \
        "Rolename %s NOT NULL, SecurityMap %s NOT NULL)" % (dbo.type_shorttext, dbo.type_longtext))
    add_index(dbo, "role_Rolename", "role", "Rolename")
    dbo.execute_dbupdate("CREATE TABLE userrole (UserID INTEGER NOT NULL, " \
        "RoleID INTEGER NOT NULL)")
    add_index(dbo, "userrole_UserIDRoleID", "userrole", "UserID, RoleID")
    # Create default roles
    dbo.execute_dbupdate("INSERT INTO role VALUES (1, 'Other Organisation', 'va *vavet *vav *mvam *dvad *cvad *vamv *vo *volk *vle *vvov *vdn *vla *vfa *vwl *vcr *vll *')")
    dbo.execute_dbupdate("INSERT INTO role VALUES (2, 'Staff', 'aa *ca *va *vavet *da *cloa *gaf *aam *cam *dam *vam *mand *aav *vav *cav *dav *bcav *maam *mcam *mdam *mvam *bcam *daad *dcad *ddad *dvad *caad *cdad *cvad *aamv *camv *vamv *damv *ao *co *vo *do *mo *volk *ale *cle *dle *vle *vaov *vcov *vvov *oaod *ocod *odod *ovod *vdn *edt *adn *eadn *emdn *ecdn *bcn *ddn *pdn *pvd *ala *cla *dla *vla *afa *cfa *dfa *vfa *mlaf *vwl *awl *cwl *dwl *bcwl *all *cll *vll *dll *vcr *')")
    dbo.execute_dbupdate("INSERT INTO role VALUES (3, 'Accountant', 'aac *vac *cac *ctrx *dac *vaov *vcov *vdov *vvov *oaod *ocod *odod *ovod *')")
    dbo.execute_dbupdate("INSERT INTO role VALUES (4, 'Vet', 'va *vavet *aav *vav *cav *dav *bcav *maam *mcam *mdam *mvam *bcam *daad *dcad *ddad *dvad * ')")
    dbo.execute_dbupdate("INSERT INTO role VALUES (5, 'Publisher', 'uipb *')")
    dbo.execute_dbupdate("INSERT INTO role VALUES (6, 'System Admin', 'asm *cso *ml *usi *rdbu *rdbd *asu *esu *ccr *vcr *hcr *dcr *')")
    dbo.execute_dbupdate("INSERT INTO role VALUES (7, 'Marketer', 'uipb *mmeo *mmea *')")
    dbo.execute_dbupdate("INSERT INTO role VALUES (8, 'Investigator', 'aoi *coi *doi *voi *')")
    # Find any existing users that aren't superusers and create a
    # matching role for them
    users = dbo.query("SELECT ID, UserName, SecurityMap FROM users " \
        "WHERE SuperUser = 0")
    for u in users:
        roleid = dbo.get_id_max("role") 
        # If it's the guest user, use the view animals/people role
        if u["USERNAME"] == "guest":
            roleid = 1
        else:
            dbo.execute_dbupdate("INSERT INTO role VALUES (%d, '%s', '%s')" % \
                ( roleid, u["USERNAME"], u["SECURITYMAP"]))
        dbo.execute_dbupdate("INSERT INTO userrole VALUES (%d, %d)" % \
            ( u["ID"], roleid))

def update_3003(dbo: Database) -> None:
    # Extend the length of configuration items
    modify_column(dbo, "configuration", "ItemValue", dbo.type_longtext)
        
def update_3004(dbo: Database) -> None:
    # Broken, disregard.
    pass

def update_3005(dbo: Database) -> None:
    # 3004 was broken and deleted the mapping service by accident, so we reinstate it
    dbo.execute_dbupdate("DELETE FROM configuration WHERE ItemName LIKE 'MappingService%'")
    dbo.execute_dbupdate("INSERT INTO configuration VALUES ('%s', '%s')" % ( "MappingServiceLinkURL", "http://maps.google.com/maps?q={0}" ))
    dbo.execute_dbupdate("INSERT INTO configuration VALUES ('%s', '%s')" % ( "MappingServiceEmbeddedURL", "https://maps.googleapis.com/maps/api/staticmap?center={0}&size=250x250&maptype=roadmap&sensor=false"))
    # Set default search sort to last changed/relevance
    dbo.execute_dbupdate("DELETE FROM configuration WHERE ItemName LIKE 'RecordSearchLimit' OR ItemName Like 'SearchSort'")
    dbo.execute_dbupdate("INSERT INTO configuration VALUES ('%s', '%s')" % ( "RecordSearchLimit", "1000" ))
    dbo.execute_dbupdate("INSERT INTO configuration VALUES ('%s', '%s')" % ( "SearchSort", "3" ))

def update_3006(dbo: Database) -> None:
    # Add ForName field to messages
    add_column(dbo, "messages", "ForName", dbo.type_shorttext)
    dbo.execute_dbupdate("UPDATE messages SET ForName = '*'")

def update_3007(dbo: Database) -> None:
    # Add default quicklinks
    dbo.execute_dbupdate("DELETE FROM configuration WHERE ItemName Like 'QuicklinksID'")
    dbo.execute_dbupdate("INSERT INTO configuration VALUES ('%s', '%s')" % ( "QuicklinksID", "35,25,33,31,34,19,20"))

def update_3008(dbo: Database) -> None:
    # Add facility for users to override the system locale
    add_column(dbo, "users", "LocaleOverride", dbo.type_shorttext)

def update_3009(dbo: Database) -> None:
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
        "AVG %s NOT NULL)" % (dbo.type_shorttext, dbo.type_shorttext, dbo.type_float)
    dbo.execute_dbupdate(sql)
    dbo.execute_dbupdate("CREATE UNIQUE INDEX animalfigures_ID ON animalfigures(ID)")
    add_index(dbo, "animalfigures_AnimalTypeID", "animalfigures", "AnimalTypeID")
    add_index(dbo, "animalfigures_SpeciesID", "animalfigures", "SpeciesID")
    add_index(dbo, "animalfigures_Month", "animalfigures", "Month")
    add_index(dbo, "animalfigures_Year", "animalfigures", "Year")

def update_3010(dbo: Database) -> None:
    # Create person flags table
    sql = "CREATE TABLE lkownerflags ( ID INTEGER NOT NULL, " \
        "Flag %s NOT NULL)" % dbo.type_shorttext
    dbo.execute_dbupdate(sql)
    # Add additionalflags field to person
    add_column(dbo, "owner", "AdditionalFlags", dbo.type_longtext)
    # Populate it with existing flags
    dbo.execute_dbupdate("UPDATE owner SET AdditionalFlags = ''")
    flags = ( 
        ("IDCheck", "homechecked"), 
        ("IsBanned", "banned"),
        ("IsVolunteer", "volunteer"),
        ("IsMember", "member"),
        ("IsHomeChecker", "homechecker"),
        ("IsDonor", "donor"),
        ("IsShelter", "shelter"),
        ("IsACO", "aco"), 
        ("IsStaff", "staff"), 
        ("IsFosterer", "fosterer"), 
        ("IsRetailer", "retailer"), 
        ("IsVet", "vet"), 
        ("IsGiftAid", "giftaid")
    )
    for field, flag in flags:
        concat = dbo.sql_concat(["AdditionalFlags", "'%s|'" % flag])
        dbo.execute_dbupdate("UPDATE owner SET AdditionalFlags=%s WHERE %s=1" % (concat, field) )

def update_3050(dbo: Database) -> None:
    # Add default cost for vaccinations
    add_column(dbo, "vaccinationtype", "DefaultCost", "INTEGER")
    # Add default adoption fee per species
    add_column(dbo, "species", "AdoptionFee", "INTEGER")

def update_3051(dbo: Database) -> None:
    # Fix incorrect field name from ASM3 initial install (it was listed
    # as TimingRuleNoFrequency instead of TimingRuleFrequency)
    if column_exists(dbo, "medicalprofile", "TimingRuleNoFrequency"):
        add_column(dbo, "medicalprofile", "TimingRuleFrequency", "INTEGER")
        drop_column(dbo, "medicalprofile", "TimingRuleNoFrequency")

def update_3081(dbo: Database) -> None:
    # Remove AdoptionFee field - it was a stupid idea to have with species
    # put a defaultcost on donation type instead
    drop_column(dbo, "species", "AdoptionFee")
    add_column(dbo, "donationtype", "DefaultCost", "INTEGER")

def update_3091(dbo: Database) -> None:
    # Reinstated map url in 3005 did not use SSL for embedded link
    dbo.execute_dbupdate("DELETE FROM configuration WHERE ItemName LIKE 'MappingService%'")
    dbo.execute_dbupdate("INSERT INTO configuration VALUES ('%s', '%s')" % ( "MappingServiceLinkURL", "http://maps.google.com/maps?q={0}" ))
    dbo.execute_dbupdate("INSERT INTO configuration VALUES ('%s', '%s')" % ( "MappingServiceEmbeddedURL", "https://maps.googleapis.com/maps/api/staticmap?center={0}&size=250x250&maptype=roadmap&sensor=false"))
    # Add ExcludeFromPublish field to media
    add_column(dbo, "media", "ExcludeFromPublish", "INTEGER")
    dbo.execute_dbupdate("UPDATE media SET ExcludeFromPublish = 0")

def update_3092(dbo: Database) -> None:
    # Added last publish date for meetapet.com
    add_column(dbo, "media", "LastPublishedMP", dbo.type_datetime)

def update_3093(dbo: Database) -> None:
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
        "Total INTEGER NOT NULL)" % (dbo.type_shorttext, dbo.type_shorttext, dbo.type_shorttext)
    dbo.execute_dbupdate(sql)
    add_index(dbo, "animalfiguresannual_ID", "animalfiguresannual", "ID", True)
    add_index(dbo, "animalfiguresannual_AnimalTypeID", "animalfiguresannual", "AnimalTypeID")
    add_index(dbo, "animalfiguresannual_SpeciesID", "animalfiguresannual", "SpeciesID")
    add_index(dbo, "animalfiguresannual_Year", "animalfiguresannual", "Year")

def update_3094(dbo: Database) -> None:
    # Added last publish date for helpinglostpets.com
    add_column(dbo, "media", "LastPublishedHLP", dbo.type_datetime)

def update_3110(dbo: Database) -> None:
    # Add PetLinkSentDate
    add_column(dbo, "animal", "PetLinkSentDate", dbo.type_datetime)

def update_3111(dbo: Database) -> None:
    l = dbo.locale
    # New additional field types to indicate location
    dbo.execute_dbupdate("UPDATE lksfieldlink SET LinkType = '%s' WHERE ID = 0" % _("Animal - Additional", l))
    dbo.execute_dbupdate("UPDATE lksfieldlink SET LinkType = '%s' WHERE ID = 1" % _("Person - Additional", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (2, '%s')" % _("Animal - Details", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (3, '%s')" % _("Animal - Notes", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (4, '%s')" % _("Animal - Entry", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (5, '%s')" % _("Animal - Health and Identification", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (6, '%s')" % _("Animal - Death", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (7, '%s')" % _("Person - Name and Address", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (8, '%s')" % _("Person - Type", l))

def update_3120(dbo: Database) -> None:
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
        dbo.execute_dbupdate("ALTER TABLE media CHANGE COLUMN lastpublished911 lastpublishedp911 DATETIME")

def update_3121(dbo: Database) -> None:
    # Added user email address
    add_column(dbo, "users", "EmailAddress", dbo.type_shorttext)

def update_3122(dbo: Database) -> None:
    # Switch shelter animals quicklink for shelter view
    # This will fail on locked databases, but shouldn't be an issue.
    links = asm3.configuration.quicklinks_id(dbo)
    links = links.replace("35", "40")
    asm3.configuration.quicklinks_id(dbo, links)

def update_3123(dbo: Database) -> None:
    # Add the monthly animal figures total column
    add_column(dbo, "animalfigures", "Total", dbo.type_shorttext)

def update_3200(dbo: Database) -> None:
    # Add the trial adoption fields to the adoption table
    add_column(dbo, "adoption", "IsTrial", "INTEGER")
    add_column(dbo, "adoption", "TrialEndDate", dbo.type_datetime)
    add_index(dbo, "adoption_TrialEndDate", "adoption", "TrialEndDate")

def update_3201(dbo: Database) -> None:
    # Add the has trial adoption denormalised field to the animal table and update it
    add_column(dbo, "animal", "HasTrialAdoption", "INTEGER")
    dbo.execute_dbupdate("UPDATE animal SET HasTrialAdoption = 0")
    dbo.execute_dbupdate("UPDATE adoption SET IsTrial = 0 WHERE IsTrial Is Null")

def update_3202(dbo: Database) -> None:
    # Set default value for HasTrialAdoption
    dbo.execute_dbupdate("UPDATE animal SET HasTrialAdoption = 1 WHERE EXISTS(SELECT ID FROM adoption ad WHERE ad.IsTrial = 1 AND ad.AnimalID = animal.ID)")

def update_3203(dbo: Database) -> None:
    l = dbo.locale
    # Add Trial Adoption movement type
    dbo.execute_dbupdate("INSERT INTO lksmovementtype (ID, MovementType) VALUES (11, ?)", [ _("Trial Adoption", l) ] )

def update_3204(dbo: Database) -> None:
    # Quicklinks format has changed, regenerate them
    links = asm3.configuration.quicklinks_id(dbo)
    asm3.configuration.quicklinks_id(dbo, links)

def update_3210(dbo: Database) -> None:
    # Anyone using MySQL who created their database with the db
    # initialiser here will have some short columns as CLOB
    # wasn't mapped properly
    if dbo.dbtype == "MYSQL":
        dbo.execute_dbupdate("ALTER TABLE dbfs MODIFY Content LONGTEXT")
        dbo.execute_dbupdate("ALTER TABLE media MODIFY MediaNotes LONGTEXT NOT NULL")
        dbo.execute_dbupdate("ALTER TABLE log MODIFY Comments LONGTEXT NOT NULL")

def update_3211(dbo: Database) -> None:
    # People who upgraded from ASM2 will find that some of their address fields
    # are a bit short - particularly if they are using unicode chars
    fields = [ "OwnerTitle", "OwnerInitials", "OwnerForeNames", "OwnerSurname", 
        "OwnerName", "OwnerAddress", "OwnerTown", "OwnerCounty", "OwnerPostcode", 
        "HomeTelephone", "WorkTelephone", "MobileTelephone", "EmailAddress" ]
    for f in fields:
        modify_column(dbo, "owner", f, dbo.type_shorttext)

def update_3212(dbo: Database) -> None:
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
            modify_column(dbo, table, field, dbo.type_shorttext)
        except Exception as err:
            asm3.al.error("failed extending %s: %s" % (f, str(err)), "dbupdate.update_3212", dbo)

def update_3213(dbo: Database) -> None:
    try:
        # Make displaylocationname and displaylocationstring denormalised fields
        dbo.execute_dbupdate("ALTER TABLE animal ADD DisplayLocationName %s" % dbo.type_shorttext)
        dbo.execute_dbupdate("ALTER TABLE animal ADD DisplayLocationString %s" % dbo.type_shorttext)
    except Exception as err:
        asm3.al.error("failed creating animal.DisplayLocationName/String: %s" % str(err), "dbupdate.update_3213", dbo)

    # Default the values for them
    dbo.execute_dbupdate("UPDATE animal SET DisplayLocationName = " \
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
    dbo.execute_dbupdate("UPDATE animal SET DisplayLocationString = DisplayLocationName")

def update_3214(dbo: Database) -> None:
    # More short fields
    fields = [ "diarytaskhead.Name", "diarytaskdetail.Subject", "diarytaskdetail.WhoFor", "lksdonationfreq.Frequency",
        "lksloglink.LinkType", "lksdiarylink.LinkType", "lksfieldlink.LinkType", "lksfieldtype.FieldType",
        "lksmedialink.LinkType", "lksdiarylink.LinkType" ]
    for f in fields:
        table, field = f.split(".")
        modify_column(dbo, table, field, dbo.type_shorttext)

def update_3215(dbo: Database) -> None:
    # Rename DisplayLocationString column to just DisplayLocation and ditch DisplayLocationName - it should be calculated
    try:
        add_column(dbo, "animal", "DisplayLocation", dbo.type_shorttext)
    except:
        asm3.al.error("failed creating animal.DisplayLocation.", "dbupdate.update_3215", dbo)
    try:
        dbo.execute_dbupdate("UPDATE animal SET DisplayLocation = DisplayLocationString")
    except:
        asm3.al.error("failed copying DisplayLocationString->DisplayLocation", "dbupdate.update_3215", dbo)
    try:
        drop_column(dbo, "animal", "DisplayLocationName")
        drop_column(dbo, "animal", "DisplayLocationString")
    except:
        asm3.al.error("failed removing DisplayLocationName and DisplayLocationString", "dbupdate.update_3215", dbo)

def update_3216(dbo: Database) -> None:
    l = dbo.locale
    # Add the new mediatype field to media and create the link table
    dbo.execute_dbupdate("ALTER TABLE media ADD MediaType INTEGER")
    dbo.execute_dbupdate("ALTER TABLE media ADD WebsiteVideo INTEGER")
    dbo.execute_dbupdate("UPDATE media SET MediaType = 0, WebsiteVideo = 0")
    dbo.execute_dbupdate("CREATE TABLE lksmediatype ( ID INTEGER NOT NULL, MediaType %s NOT NULL )" % ( dbo.type_shorttext))
    dbo.execute_dbupdate("CREATE UNIQUE INDEX lksmediatype_ID ON lksmediatype(ID)")
    dbo.execute_dbupdate("INSERT INTO lksmediatype (ID, MediaType) VALUES (%d, '%s')" % (0, _("File", l)))
    dbo.execute_dbupdate("INSERT INTO lksmediatype (ID, MediaType) VALUES (%d, '%s')" % (1, _("Document Link", l)))
    dbo.execute_dbupdate("INSERT INTO lksmediatype (ID, MediaType) VALUES (%d, '%s')" % (2, _("Video Link", l)))

def update_3217(dbo: Database) -> None:
    # Add asilomar fields for US users
    dbo.execute_dbupdate("ALTER TABLE animal ADD AsilomarIsTransferExternal INTEGER")
    dbo.execute_dbupdate("ALTER TABLE animal ADD AsilomarIntakeCategory INTEGER")
    dbo.execute_dbupdate("ALTER TABLE animal ADD AsilomarOwnerRequestedEuthanasia INTEGER")
    dbo.execute_dbupdate("UPDATE animal SET AsilomarIsTransferExternal = 0, AsilomarIntakeCategory = 0, AsilomarOwnerRequestedEuthanasia = 0")

def update_3220(dbo: Database) -> None:
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
        "Total INTEGER NOT NULL)" % (dbo.type_shorttext, dbo.type_shorttext)
    dbo.execute_dbupdate(sql)
    add_index(dbo, "animalfiguresasilomar_ID", "animalfiguresasilomar", "ID", True)
    add_index(dbo, "animalfiguresasilomar_Year", "animalfiguresasilomar", "Year")

def update_3221(dbo: Database) -> None:
    # More short fields
    fields = [ "activeuser.UserName", "customreport.Title", "customreport.Category" ]
    for f in fields:
        table, field = f.split(".")
        modify_column(dbo, table, field, dbo.type_shorttext)

def update_3222(dbo: Database) -> None:
    # Person investigation table
    dbo.execute_dbupdate("CREATE TABLE ownerinvestigation ( ID INTEGER NOT NULL, " \
        "OwnerID INTEGER NOT NULL, Date %s NOT NULL, Notes %s NOT NULL, " \
        "RecordVersion INTEGER, CreatedBy %s, CreatedDate %s, " \
        "LastChangedBy %s, LastChangedDate %s)" % \
        (dbo.type_datetime, dbo.type_longtext, dbo.type_shorttext, dbo.type_datetime, dbo.type_shorttext, dbo.type_datetime))
    add_index(dbo, "ownerinvestigation_ID", "ownerinvestigation", "ID", True)
    add_index(dbo, "ownerinvestigation_Date", "ownerinvestigation", "Date")

def update_3223(dbo: Database) -> None:
    # PostgreSQL databases have been using VARCHAR(16384) as longtext when
    # they really shouldn't. Let's switch those fields to be TEXT instead.
    if dbo.dbtype != "POSTGRESQL": return
    fields = [ "activeuser.Messages", "additionalfield.LookupValues", "additional.Value", "adoption.ReasonForReturn", 
        "adoption.Comments", "animal.Markings", "animal.HiddenAnimalDetails", "animal.AnimalComments", "animal.ReasonForEntry", 
        "animal.ReasonNO", "animal.HealthProblems", "animal.PTSReason", "animalcost.Description", "animal.AnimalComments", 
        "animalfound.DistFeat", "animalfound.Comments", "animallitter.Comments", "animallost.DistFeat", "animallost.Comments", 
        "animalmedical.Comments", "animalmedicaltreatment.Comments", "animalvaccination.Comments", "animalwaitinglist.ReasonForWantingToPart", 
        "animalwaitinglist.ReasonForRemoval", "animalwaitinglist.Comments", "audittrail.Description", "customreport.Description", 
        "diary.Subject", "diary.Note", "diarytaskdetail.Subject", "diarytaskdetail.Note", "log.Comments", "media.MediaNotes", 
        "medicalprofile.Comments", "messages.Message", "owner.Comments", "owner.AdditionalFlags", "owner.HomeCheckAreas", 
        "ownerdonation.Comments", "ownerinvestigation.Notes", "ownervoucher.Comments", "role.SecurityMap", "users.SecurityMap", 
        "users.IPRestriction", "configuration.ItemValue", "customreport.SQLCommand", "customreport.HTMLBody" ]
    for f in fields:
        table, field = f.split(".")
        try:
            dbo.execute_dbupdate("ALTER TABLE %s ALTER %s TYPE %s" % (table, field, dbo.type_longtext))
        except Exception as err:
            asm3.al.error("failed switching to TEXT %s: %s" % (f, str(err)), "dbupdate.update_3223", dbo)

def update_3224(dbo: Database) -> None:
    # AVG is a reserved keyword in some SQL dialects, change that field
    try:
        if dbo.dbtype == "MYSQL":
            dbo.execute_dbupdate("ALTER TABLE animalfigures CHANGE AVG AVERAGE %s NOT NULL" % dbo.type_float)
        elif dbo.dbtype == "POSTGRESQL":
            dbo.execute_dbupdate("ALTER TABLE animalfigures RENAME COLUMN AVG TO AVERAGE")
        elif dbo.dbtype == "SQLITE":
            dbo.execute_dbupdate("ALTER TABLE animalfigures ADD AVERAGE %s" % dbo.type_float)
    except Exception as err:
        asm3.al.error("failed renaming AVG to AVERAGE: %s" % str(err), "dbupdate.update_3224", dbo)

def update_3225(dbo: Database) -> None:
    # Make sure the ADOPTIONFEE mistake is really gone
    if column_exists(dbo, "species", "AdoptionFee"):
        dbo.execute_dbupdate("ALTER TABLE species DROP COLUMN AdoptionFee")

def update_3300(dbo: Database) -> None:
    # Add diary comments field
    add_column(dbo, "diary", "Comments", dbo.type_longtext)

def update_3301(dbo: Database) -> None:
    # Add the accountsrole table
    dbo.execute_dbupdate("CREATE TABLE accountsrole (AccountID INTEGER NOT NULL, " \
        "RoleID INTEGER NOT NULL, CanView INTEGER NOT NULL, CanEdit INTEGER NOT NULL)")
    dbo.execute_dbupdate("CREATE UNIQUE INDEX accountsrole_AccountIDRoleID ON accountsrole(AccountID, RoleID)")

def update_3302(dbo: Database) -> None:
    # Add default cost fields to costtype and voucher
    add_column(dbo, "costtype", "DefaultCost", "INTEGER")
    add_column(dbo, "voucher", "DefaultCost", "INTEGER")

def update_3303(dbo: Database) -> None:
    # Add theme override to users
    add_column(dbo, "users", "ThemeOverride", dbo.type_shorttext)

def update_3304(dbo: Database) -> None:
    # Add index to configuration ItemName field
    add_index(dbo, "configuration_ItemName", "configuration", "ItemName")

def update_3305(dbo: Database) -> None:
    # Add IsHold and IsQuarantine fields
    add_column(dbo, "animal", "IsHold", "INTEGER")
    add_column(dbo, "animal", "IsQuarantine", "INTEGER")
    dbo.execute_dbupdate("UPDATE animal SET IsHold = 0, IsQuarantine = 0")

def update_3306(dbo: Database) -> None:
    # Add HoldUntilDate
    add_column(dbo, "animal", "HoldUntilDate", dbo.type_datetime)

def update_3307(dbo: Database) -> None:
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
        "LastChangedDate %(date)s)" % { "date": dbo.type_datetime, "long": dbo.type_longtext, "short": dbo.type_shorttext}
    dbo.execute_dbupdate(sql)
    add_index(dbo, "animaltest_AnimalID", "animaltest", "AnimalID")
    sql = "CREATE TABLE testtype (ID INTEGER NOT NULL PRIMARY KEY, " \
        "TestName %(short)s NOT NULL, " \
        "TestDescription %(long)s, " \
        "DefaultCost INTEGER)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
    dbo.execute_dbupdate(sql)
    sql = "CREATE TABLE testresult (ID INTEGER NOT NULL PRIMARY KEY, " \
        "ResultName %(short)s NOT NULL, " \
        "ResultDescription %(long)s)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
    dbo.execute_dbupdate(sql)

def update_3308(dbo: Database) -> None:
    # Create initial data for testtype and testresult tables
    if dbo.query_int("SELECT COUNT(*) FROM testtype") > 0: return
    l = dbo.locale
    dbo.execute_dbupdate("INSERT INTO testresult (ID, ResultName) VALUES (1, '" + _("Unknown", l) + "')")
    dbo.execute_dbupdate("INSERT INTO testresult (ID, ResultName) VALUES (2, '" + _("Negative", l) + "')")
    dbo.execute_dbupdate("INSERT INTO testresult (ID, ResultName) VALUES (3, '" + _("Positive", l) + "')")
    dbo.execute_dbupdate("INSERT INTO testtype (ID, TestName, DefaultCost) VALUES (1, '" + _("FIV", l) + "', 0)")
    dbo.execute_dbupdate("INSERT INTO testtype (ID, TestName, DefaultCost) VALUES (2, '" + _("FLV", l) + "', 0)")
    dbo.execute_dbupdate("INSERT INTO testtype (ID, TestName, DefaultCost) VALUES (3, '" + _("Heartworm", l) + "', 0)")

def update_3309(dbo: Database) -> None:
    if dbo.query_int("SELECT COUNT(*) FROM animaltest") > 0: return
    fiv = dbo.query("SELECT ID, CombiTestDate, CombiTestResult FROM animal WHERE CombiTested = 1 AND CombiTestDate Is Not Null")
    asm3.al.debug("found %d fiv results to convert" % len(fiv), "update_3309", dbo)
    for f in fiv:
        try:
            dbo.insert("animaltest", {
                "ID": dbo.get_id_max("animaltest"),
                "AnimalID": f["ID"],
                "TestTypeID": 1,
                "TestResultID": f["COMBITESTRESULT"] + 1,
                "DateOfTest": f["COMBITESTDATE"],
                "DateRequired": f["COMBITESTDATE"],
                "Cost": 0,
                "Comments": ""
            }, user="dbupdate", generateID=False, writeAudit=False)
        except Exception as err:
            asm3.al.error("fiv: " + str(err), "dbupdate.update_3309", dbo)
    flv = dbo.query("SELECT ID, CombiTestDate, FLVResult FROM animal WHERE CombiTested = 1 AND CombiTestDate Is Not Null")
    asm3.al.debug("found %d flv results to convert" % len(flv), "update_3309", dbo)
    for f in flv:
        try:
            dbo.insert("animaltest", {
                "ID": dbo.get_id_max("animaltest"),
                "AnimalID": f["ID"],
                "TestTypeID": 2,
                "TestResultID": f["FLVRESULT"] + 1,
                "DateOfTest": f["COMBITESTDATE"],
                "DateRequired": f["COMBITESTDATE"],
                "Cost": 0,
                "Comments": ""
            }, user="dbupdate", generateID=False, writeAudit=False)
        except Exception as err:
            asm3.al.error("flv: " + str(err), "dbupdate.update_3309", dbo)
    hw = dbo.query("SELECT ID, HeartwormTestDate, HeartwormTestResult FROM animal WHERE HeartwormTested = 1 AND HeartwormTestDate Is Not Null")
    asm3.al.debug("found %d heartworm results to convert" % len(hw), "update_3309", dbo)
    for f in hw:
        try:
            dbo.insert("animaltest", {
                "ID": dbo.get_id_max("animaltest"),
                "AnimalID": f["ID"],
                "TestTypeID": 3,
                "TestResultID": f["HEARTWORMTESTRESULT"] + 1,
                "DateOfTest": f["HEARTWORMTESTDATE"],
                "DateRequired": f["HEARTWORMTESTDATE"],
                "Cost": 0,
                "Comments": ""
            }, user="dbupdate", generateID=False, writeAudit=False)
        except Exception as err:
            asm3.al.error("hw: " + str(err), "dbupdate.update_3309", dbo)

def update_33010(dbo: Database) -> None:
    # Add new additional field types and locations
    l = dbo.locale
    dbo.execute_dbupdate("INSERT INTO lksfieldtype (ID, FieldType) VALUES (7, '" + _("Multi-Lookup", l) + "')")
    dbo.execute_dbupdate("INSERT INTO lksfieldtype (ID, FieldType) VALUES (8, '" + _("Animal", l) + "')")
    dbo.execute_dbupdate("INSERT INTO lksfieldtype (ID, FieldType) VALUES (9, '" + _("Person", l) + "')")
    dbo.execute_dbupdate("INSERT INTO lksfieldlink (ID, LinkType) VALUES (9, '" + _("Lost Animal - Additional", l) + "')")
    dbo.execute_dbupdate("INSERT INTO lksfieldlink (ID, LinkType) VALUES (10, '" + _("Lost Animal - Details", l) + "')")
    dbo.execute_dbupdate("INSERT INTO lksfieldlink (ID, LinkType) VALUES (11, '" + _("Found Animal - Additional", l) + "')")
    dbo.execute_dbupdate("INSERT INTO lksfieldlink (ID, LinkType) VALUES (12, '" + _("Found Animal - Details", l) + "')")
    dbo.execute_dbupdate("INSERT INTO lksfieldlink (ID, LinkType) VALUES (13, '" + _("Waiting List - Additional", l) + "')")
    dbo.execute_dbupdate("INSERT INTO lksfieldlink (ID, LinkType) VALUES (14, '" + _("Waiting List - Details", l) + "')")
    dbo.execute_dbupdate("INSERT INTO lksfieldlink (ID, LinkType) VALUES (15, '" + _("Waiting List - Removal", l) + "')")

def update_33011(dbo: Database) -> None:
    # Add donationpayment table and data
    l = dbo.locale
    sql = "CREATE TABLE donationpayment (ID INTEGER NOT NULL PRIMARY KEY, " \
        "PaymentName %(short)s NOT NULL, " \
        "PaymentDescription %(long)s ) " % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
    dbo.execute_dbupdate(sql)
    dbo.execute_dbupdate("INSERT INTO donationpayment (ID, PaymentName) VALUES (1, '" + _("Cash", l) + "')")
    dbo.execute_dbupdate("INSERT INTO donationpayment (ID, PaymentName) VALUES (2, '" + _("Check", l) + "')")
    dbo.execute_dbupdate("INSERT INTO donationpayment (ID, PaymentName) VALUES (3, '" + _("Credit Card", l) + "')")
    dbo.execute_dbupdate("INSERT INTO donationpayment (ID, PaymentName) VALUES (4, '" + _("Debit Card", l) + "')")
    # Add donationpaymentid field to donations
    dbo.execute_dbupdate("ALTER TABLE ownerdonation ADD DonationPaymentID INTEGER")
    dbo.execute_dbupdate("UPDATE ownerdonation SET DonationPaymentID = 1")

def update_33012(dbo: Database) -> None:
    # Add ShelterLocationUnit
    add_column(dbo, "animal", "ShelterLocationUnit", dbo.type_shorttext)
    dbo.execute_dbupdate("UPDATE animal SET ShelterLocationUnit = ''")

def update_33013(dbo: Database) -> None:
    # Add online form tables
    sql = "CREATE TABLE onlineform (ID INTEGER NOT NULL PRIMARY KEY, " \
        "Name %(short)s NOT NULL, " \
        "RedirectUrlAfterPOST %(short)s, " \
        "SetOwnerFlags %(short)s, " \
        "Description %(long)s )" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
    dbo.execute_dbupdate(sql)
    add_index(dbo, "onlineform_Name", "onlineform", "Name")
    sql = "CREATE TABLE onlineformfield(ID INTEGER NOT NULL PRIMARY KEY, " \
        "OnlineFormID INTEGER NOT NULL, " \
        "FieldName %(short)s NOT NULL, " \
        "FieldType INTEGER NOT NULL, " \
        "Label %(short)s NOT NULL, " \
        "Lookups %(long)s, " \
        "Tooltip %(long)s )" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
    dbo.execute_dbupdate(sql)
    add_index(dbo, "onlineformfield_OnlineFormID", "onlineformfield", "OnlineFormID")
    sql = "CREATE TABLE onlineformincoming(CollationID INTEGER NOT NULL, " \
        "FormName %(short)s NOT NULL, " \
        "PostedDate %(date)s NOT NULL, " \
        "Flags %(short)s, " \
        "FieldName %(short)s NOT NULL, " \
        "Value %(long)s )" % { "date": dbo.type_datetime, "short": dbo.type_shorttext, "long": dbo.type_longtext }
    dbo.execute_dbupdate(sql)
    add_index(dbo, "onlineformincoming_CollationID", "onlineformincoming", "CollationID")

def update_33014(dbo: Database) -> None:
    # Add a display index field to onlineformfield
    add_column(dbo, "onlineformfield", "DisplayIndex", "INTEGER")
    # Add a label field to onlineformincoming
    add_column(dbo, "onlineformincoming", "Label", dbo.type_shorttext)

def update_33015(dbo: Database) -> None:
    # Add a host field to onlineformincoming
    add_column(dbo, "onlineformincoming", "Host", dbo.type_shorttext)

def update_33016(dbo: Database) -> None:
    # Add a DisplayIndex and Preview field to onlineformincoming
    add_column(dbo, "onlineformincoming", "DisplayIndex", "INTEGER")
    add_column(dbo, "onlineformincoming", "Preview", dbo.type_longtext)

def update_33017(dbo: Database) -> None:
    # Add the customreportrole table
    dbo.execute_dbupdate("CREATE TABLE customreportrole (ReportID INTEGER NOT NULL, " \
        "RoleID INTEGER NOT NULL, CanView INTEGER NOT NULL)")
    dbo.execute_dbupdate("CREATE UNIQUE INDEX customreportrole_ReportIDRoleID ON customreportrole(ReportID, RoleID)")

def update_33018(dbo: Database) -> None:
    l = dbo.locale
    # Add IsPermanentFoster and HasPermanentFoster fields
    add_column(dbo, "adoption", "IsPermanentFoster", "INTEGER")
    add_column(dbo, "animal", "HasPermanentFoster", "INTEGER")
    # Add Permanent Foster movement type
    dbo.execute_dbupdate("INSERT INTO lksmovementtype (ID, MovementType) VALUES (12, ?)",  [ _("Permanent Foster", l)] )

def update_33019(dbo: Database) -> None:
    # Set initial value for those flags
    dbo.execute_dbupdate("UPDATE adoption SET IsPermanentFoster = 0 WHERE IsPermanentFoster Is Null")
    dbo.execute_dbupdate("UPDATE animal SET HasPermanentFoster = 0 WHERE HasPermanentFoster Is Null")

def update_33101(dbo: Database) -> None:
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
    #add_index(dbo, "animal_AnimalTypeID", "animal", "AnimalTypeID")
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

def update_33102(dbo: Database) -> None:
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
    add_index(dbo, "animalwaitinglist_AnimalDescription", "animalwaitinglist", "AnimalDescription", partial = True)
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

def update_33103(dbo: Database) -> None:
    add_index(dbo, "owner_HomeTelephone", "owner", "HomeTelephone")
    add_index(dbo, "owner_MobileTelephone", "owner", "MobileTelephone")
    add_index(dbo, "owner_WorkTelephone", "owner", "WorkTelephone")
    add_index(dbo, "owner_EmailAddress", "owner", "EmailAddress")
    add_index(dbo, "animal_BroughtInByOwnerID", "animal", "BroughtInByOwnerID")

def update_33104(dbo: Database) -> None:
    # Add LatLong
    add_column(dbo, "owner", "LatLong", dbo.type_shorttext)

def update_33105(dbo: Database) -> None:
    # Add LocationFilter
    add_column(dbo, "users", "LocationFilter", dbo.type_shorttext)

def update_33106(dbo: Database) -> None:
    # Add MatchColour
    add_column(dbo, "owner", "MatchColour", "INTEGER")
    dbo.execute_dbupdate("UPDATE owner SET MatchColour = -1")

def update_33201(dbo: Database) -> None:
    # Add Fee column
    add_column(dbo, "animal", "Fee", "INTEGER")

def update_33202(dbo: Database) -> None:
    # Add the animalpublished table to track what was sent to which
    # publisher and when
    sql = "CREATE TABLE animalpublished (" \
        "AnimalID INTEGER NOT NULL, " \
        "PublishedTo %s NOT NULL, " \
        "SentDate %s NOT NULL, " \
        "Extra %s)" % (dbo.type_shorttext, dbo.type_datetime, dbo.type_shorttext)
    dbo.execute_dbupdate(sql)
    add_index(dbo, "animalpublished_AnimalIDPublishedTo", "animalpublished", "AnimalID, PublishedTo", True)
    add_index(dbo, "animalpublished_SentDate", "animalpublished", "SentDate")
    # Copy existing values into the new table
    dbo.execute_dbupdate("INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT a.ID, 'smarttag', a.SmartTagSentDate FROM animal a WHERE a.SmartTagSentDate Is Not Null")
    dbo.execute_dbupdate("INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT a.ID, 'petlink', a.PetLinkSentDate FROM animal a WHERE a.PetLinkSentDate Is Not Null")
    dbo.execute_dbupdate("INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT DISTINCT m.LinkID, 'html', m.LastPublished FROM media m WHERE m.LastPublished Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
    dbo.execute_dbupdate("INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT DISTINCT m.LinkID, 'petfinder', m.LastPublishedPF FROM media m WHERE m.LastPublishedPF Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
    dbo.execute_dbupdate("INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT DISTINCT m.LinkID, 'adoptapet', m.LastPublishedAP FROM media m WHERE m.LastPublishedAP Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
    dbo.execute_dbupdate("INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT DISTINCT m.LinkID, 'pets911', m.LastPublishedP911 FROM media m WHERE m.LastPublishedP911 Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
    dbo.execute_dbupdate("INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT DISTINCT m.LinkID, 'rescuegroups', m.LastPublishedRG FROM media m WHERE m.LastPublishedRG Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
    dbo.execute_dbupdate("INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT DISTINCT m.LinkID, 'meetapet', m.LastPublishedMP FROM media m WHERE m.LastPublishedMP Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")
    dbo.execute_dbupdate("INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT DISTINCT m.LinkID, 'helpinglostpets', m.LastPublishedHLP FROM media m WHERE m.LastPublishedHLP Is Not Null AND m.LinkTypeID = 0 AND m.WebsitePhoto = 1")

def update_33203(dbo: Database) -> None:
    # Assume all already adopted animals with PETtrac UK chips have been sent to them
    dbo.execute_dbupdate("INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) " \
        "SELECT a.ID, 'pettracuk', a.ActiveMovementDate FROM animal a " \
        "WHERE ActiveMovementDate Is Not Null " \
        "AND ActiveMovementType = 1 AND IdentichipNumber LIKE '977%'")

def update_33204(dbo: Database) -> None:
    # Remove last published fields added since ASM3 - we're only retaining
    # the ASM2 ones for compatibility and everything else is going to
    # the animalpublished table
    drop_column(dbo, "media", "LastPublishedHLP")
    drop_column(dbo, "media", "LastPublishedMP")
    drop_column(dbo, "animal", "PetLinkSentDate")

def update_33205(dbo: Database) -> None:
    # Add mandatory column to online form fields
    add_column(dbo, "onlineformfield", "Mandatory", "INTEGER")
    dbo.execute_dbupdate("UPDATE onlineformfield SET Mandatory = 0")

def update_33206(dbo: Database) -> None:
    # Add cost paid date fields
    add_column(dbo, "animalcost", "CostPaidDate", dbo.type_datetime)
    add_column(dbo, "animalmedical", "CostPaidDate", dbo.type_datetime)
    add_column(dbo, "animaltest", "CostPaidDate", dbo.type_datetime)
    add_column(dbo, "animalvaccination", "CostPaidDate", dbo.type_datetime)
    add_index(dbo, "animalcost_CostPaidDate", "animalcost", "CostPaidDate")
    add_index(dbo, "animalmedical_CostPaidDate", "animalmedical", "CostPaidDate")
    add_index(dbo, "animaltest_CostPaidDate", "animaltest", "CostPaidDate")
    add_index(dbo, "animalvaccination_CostPaidDate", "animalvaccination", "CostPaidDate")

def update_33300(dbo: Database) -> None:
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
        "LastChangedDate %(date)s)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
    dbo.execute_dbupdate(sql)
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

def update_33301(dbo: Database) -> None:
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
        "LastChangedDate %(date)s)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
    dbo.execute_dbupdate(sql)
    add_index(dbo, "ownercitation_OwnerID", "ownercitation", "OwnerID")
    add_index(dbo, "ownercitation_CitationTypeID", "ownercitation", "CitationTypeID")
    add_index(dbo, "ownercitation_CitationDate", "ownercitation", "CitationDate")
    add_index(dbo, "ownercitation_FineDueDate", "ownercitation", "FineDueDate")
    add_index(dbo, "ownercitation_FinePaidDate", "ownercitation", "FinePaidDate")

def update_33302(dbo: Database) -> None:
    l = dbo.locale
    # Lookup tables
    sql = "CREATE TABLE citationtype (ID INTEGER NOT NULL PRIMARY KEY, " \
        "CitationName %s NOT NULL, CitationDescription %s, DefaultCost INTEGER)" % (dbo.type_shorttext, dbo.type_longtext)
    dbo.execute_dbupdate(sql)
    sql = "CREATE TABLE incidenttype (ID INTEGER NOT NULL PRIMARY KEY, " \
        "IncidentName %s NOT NULL, IncidentDescription %s)" % (dbo.type_shorttext, dbo.type_longtext)
    dbo.execute_dbupdate(sql)
    sql = "CREATE TABLE incidentcompleted (ID INTEGER NOT NULL PRIMARY KEY, " \
        "CompletedName %s NOT NULL, CompletedDescription %s)" % (dbo.type_shorttext, dbo.type_longtext)
    dbo.execute_dbupdate(sql)
    # Default lookup data
    dbo.execute_dbupdate("INSERT INTO citationtype VALUES (1, '%s', '', 0)" % _("First offence", l))
    dbo.execute_dbupdate("INSERT INTO citationtype VALUES (2, '%s', '', 0)" % _("Second offence", l))
    dbo.execute_dbupdate("INSERT INTO citationtype VALUES (3, '%s', '', 0)" % _("Third offence", l))
    dbo.execute_dbupdate("INSERT INTO incidenttype VALUES (1, '%s', '')" % _("Aggression", l))
    dbo.execute_dbupdate("INSERT INTO incidenttype VALUES (2, '%s', '')" % _("Animal defecation", l))
    dbo.execute_dbupdate("INSERT INTO incidenttype VALUES (3, '%s', '')" % _("Animals at large", l))
    dbo.execute_dbupdate("INSERT INTO incidenttype VALUES (4, '%s', '')" % _("Animals left in vehicle", l))
    dbo.execute_dbupdate("INSERT INTO incidenttype VALUES (5, '%s', '')" % _("Bite", l))
    dbo.execute_dbupdate("INSERT INTO incidenttype VALUES (6, '%s', '')" % _("Dead animal", l))
    dbo.execute_dbupdate("INSERT INTO incidenttype VALUES (7, '%s', '')" % _("Neglect", l))
    dbo.execute_dbupdate("INSERT INTO incidenttype VALUES (8, '%s', '')" % _("Noise", l))
    dbo.execute_dbupdate("INSERT INTO incidenttype VALUES (9, '%s', '')" % _("Number of pets", l))
    dbo.execute_dbupdate("INSERT INTO incidenttype VALUES (10, '%s', '')" % _("Sick/injured animal", l))
    dbo.execute_dbupdate("INSERT INTO incidentcompleted VALUES (1, '%s', '')" % _("Animal destroyed", l))
    dbo.execute_dbupdate("INSERT INTO incidentcompleted VALUES (2, '%s', '')" % _("Animal picked up", l))
    dbo.execute_dbupdate("INSERT INTO incidentcompleted VALUES (3, '%s', '')" % _("Owner given citation", l))

def update_33303(dbo: Database) -> None:
    # Add new incident link types
    l = dbo.locale
    dbo.execute_dbupdate("INSERT INTO lksloglink (ID, LinkType) VALUES (%d, '%s')" % (6, _("Incident", l)))
    dbo.execute_dbupdate("INSERT INTO lksmedialink (ID, LinkType) VALUES (%d, '%s')" % (6, _("Incident", l)))
    dbo.execute_dbupdate("INSERT INTO lksdiarylink (ID, LinkType) VALUES (%d, '%s')" % (7, _("Incident", l)))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (16, '%s')" % _("Incident - Details", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (17, '%s')" % _("Incident - Dispatch", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (18, '%s')" % _("Incident - Owner", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (19, '%s')" % _("Incident - Citation", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (20, '%s')" % _("Incident - Additional", l))

def update_33304(dbo: Database) -> None:
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
        "LastChangedDate %(date)s)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
    dbo.execute_dbupdate(sql)
    add_index(dbo, "ownertraploan_OwnerID", "ownertraploan", "OwnerID")
    add_index(dbo, "ownertraploan_TrapTypeID", "ownertraploan", "TrapTypeID")
    add_index(dbo, "ownertraploan_ReturnDueDate", "ownertraploan", "ReturnDueDate")
    add_index(dbo, "ownertraploan_ReturnDate", "ownertraploan", "ReturnDate")

def update_33305(dbo: Database) -> None:
    # Add traptype lookup
    l = dbo.locale
    sql = "CREATE TABLE traptype (ID INTEGER NOT NULL PRIMARY KEY, " \
        "TrapTypeName %s NOT NULL, TrapTypeDescription %s, DefaultCost INTEGER)" % (dbo.type_shorttext, dbo.type_longtext)
    dbo.execute_dbupdate(sql)
    dbo.execute_dbupdate("INSERT INTO traptype VALUES (1, '%s', '', 0)" % _("Cat", l))

def update_33306(dbo: Database) -> None:
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
        "LastChangedDate %(date)s)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
    dbo.execute_dbupdate(sql)
    add_index(dbo, "ownerlicence_OwnerID", "ownerlicence", "OwnerID")
    add_index(dbo, "ownerlicence_AnimalID", "ownerlicence", "AnimalID")
    add_index(dbo, "ownerlicence_LicenceTypeID", "ownerlicence", "LicenceTypeID")
    add_index(dbo, "ownerlicence_LicenceNumber", "ownerlicence", "LicenceNumber", True)
    add_index(dbo, "ownerlicence_IssueDate", "ownerlicence", "IssueDate")
    add_index(dbo, "ownerlicence_ExpiryDate", "ownerlicence", "ExpiryDate")

def update_33307(dbo: Database) -> None:
    # Add licencetype lookup
    l = dbo.locale
    sql = "CREATE TABLE licencetype (ID INTEGER NOT NULL PRIMARY KEY, " \
        "LicenceTypeName %s NOT NULL, LicenceTypeDescription %s, DefaultCost INTEGER)" % (dbo.type_shorttext, dbo.type_longtext)
    dbo.execute_dbupdate(sql)
    dbo.execute_dbupdate("INSERT INTO licencetype VALUES (1, '%s', '', 0)" % _("Altered Dog - 1 year", l))
    dbo.execute_dbupdate("INSERT INTO licencetype VALUES (2, '%s', '', 0)" % _("Unaltered Dog - 1 year", l))
    dbo.execute_dbupdate("INSERT INTO licencetype VALUES (3, '%s', '', 0)" % _("Altered Dog - 3 year", l))
    dbo.execute_dbupdate("INSERT INTO licencetype VALUES (4, '%s', '', 0)" % _("Unaltered Dog - 3 year", l))

def update_33308(dbo: Database) -> None:
    # broken
    pass

def update_33309(dbo: Database) -> None:
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
        "Total INTEGER NOT NULL)" % (dbo.type_shorttext, dbo.type_shorttext)
    dbo.execute_dbupdate(sql)
    add_index(dbo, "animalfiguresmonthlyasilomar_ID", "animalfiguresmonthlyasilomar", "ID", True)
    add_index(dbo, "animalfiguresmonthlyasilomar_Year", "animalfiguresmonthlyasilomar", "Year")
    add_index(dbo, "animalfiguresmonthlyasilomar_Month", "animalfiguresmonthlyasilomar", "Month")

def update_33310(dbo: Database) -> None:
    pass # broken

def update_33311(dbo: Database) -> None:
    # Add exclude from bulk email field to owner
    add_column(dbo, "owner", "ExcludeFromBulkEmail", "INTEGER")
    dbo.execute_dbupdate("UPDATE owner SET ExcludeFromBulkEmail = 0")

def update_33312(dbo: Database) -> None:
    # Add header/footer to onlineform fields
    add_column(dbo, "onlineform", "Header", dbo.type_longtext)
    add_column(dbo, "onlineform", "Footer", dbo.type_longtext)

def update_33313(dbo: Database) -> None:
    # onlineformincoming.DisplayIndex should have been an integer,
    # but the new db created it accidentally as a str in some
    # databases - switch it to integer
    modify_column(dbo, "onlineformincoming", "DisplayIndex", "INTEGER", "(DisplayIndex::integer)")

def update_33314(dbo: Database) -> None:
    # Add extra followup and suspect fields to animal control
    add_column(dbo, "animalcontrol", "FollowupDateTime2", dbo.type_datetime)
    add_column(dbo, "animalcontrol", "FollowupDateTime3", dbo.type_datetime)
    add_column(dbo, "animalcontrol", "Owner2ID", "INTEGER")
    add_column(dbo, "animalcontrol", "Owner3ID", "INTEGER")
    add_column(dbo, "animalcontrol", "AnimalID", "INTEGER")
    add_index(dbo, "animalcontrol_FollowupDateTime", "animalcontrol", "FollowupDateTime")
    add_index(dbo, "animalcontrol_FollowupDateTime2", "animalcontrol", "FollowupDateTime2")
    add_index(dbo, "animalcontrol_FollowupDateTime3", "animalcontrol", "FollowupDateTime3")
    add_index(dbo, "animalcontrol_Owner2ID", "animalcontrol", "Owner2ID")
    add_index(dbo, "animalcontrol_Owner3ID", "animalcontrol", "Owner3ID")
    add_index(dbo, "animalcontrol_AnimalID", "animalcontrol", "AnimalID")

def update_33315(dbo: Database) -> None:
    # Add size field to waiting list
    add_column(dbo, "animalwaitinglist", "Size", "INTEGER")
    add_index(dbo, "animalwaitinglist_Size", "animalwaitinglist", "Size")
    dbo.execute_dbupdate("UPDATE animalwaitinglist SET Size = 2")

def update_33316(dbo: Database) -> None:
    # Add emailaddress field to onlineform
    add_column(dbo, "onlineform", "EmailAddress", dbo.type_longtext)

def update_33401(dbo: Database) -> None:
    # Add OwnerType and IsDeceased flags to owner
    add_column(dbo, "owner", "OwnerType", "INTEGER")
    add_column(dbo, "owner", "IsDeceased", "INTEGER")
    dbo.execute_dbupdate("UPDATE owner SET OwnerType = 1")
    dbo.execute_dbupdate("UPDATE owner SET OwnerType = 2 WHERE IsShelter = 1")
    dbo.execute_dbupdate("UPDATE owner SET IsDeceased = 0")

def update_33402(dbo: Database) -> None:
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
        "CreatedDate %(date)s NOT NULL)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
    dbo.execute_dbupdate(sql)
    add_index(dbo, "stocklevel_ID", "stocklevel", "ID", True)
    add_index(dbo, "stocklevel_Name", "stocklevel", "Name")
    add_index(dbo, "stocklevel_UnitName", "stocklevel", "UnitName")
    add_index(dbo, "stocklevel_StockLocationID", "stocklevel", "StockLocationID")
    add_index(dbo, "stocklevel_Expiry", "stocklevel", "Expiry")
    add_index(dbo, "stocklevel_BatchNumber", "stocklevel", "BatchNumber")
    sql = "CREATE TABLE stocklocation ( ID INTEGER NOT NULL, " \
        "LocationName %(short)s NOT NULL, " \
        "LocationDescription %(long)s )" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
    dbo.execute_dbupdate(sql)
    add_index(dbo, "stocklocation_ID", "stocklocation", "ID", True)
    add_index(dbo, "stocklocation_LocationName", "stocklocation", "LocationName", True)
    dbo.execute_dbupdate("INSERT INTO stocklocation VALUES (1, '%s', '')" % _("Stores", l))
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
        "LastChangedDate %(date)s)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
    dbo.execute_dbupdate(sql)
    add_index(dbo, "stockusage_ID", "stockusage", "ID", True)
    add_index(dbo, "stockusage_StockUsageTypeID", "stockusage", "StockUsageTypeID")
    add_index(dbo, "stockusage_StockLevelID", "stockusage", "StockLevelID")
    add_index(dbo, "stockusage_UsageDate", "stockusage", "UsageDate")
    sql = "CREATE TABLE stockusagetype ( ID INTEGER NOT NULL, " \
        "UsageTypeName %(short)s NOT NULL, " \
        "UsageTypeDescription %(long)s )" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
    dbo.execute_dbupdate(sql)
    add_index(dbo, "stockusagetype_ID", "stockusagetype", "ID", True)
    add_index(dbo, "stockusagetype_UsageTypeName", "stockusagetype", "UsageTypeName")
    dbo.execute_dbupdate("INSERT INTO stockusagetype VALUES (1, '%s', '')" % _("Administered", l))
    dbo.execute_dbupdate("INSERT INTO stockusagetype VALUES (2, '%s', '')" % _("Consumed", l))
    dbo.execute_dbupdate("INSERT INTO stockusagetype VALUES (3, '%s', '')" % _("Donated", l))
    dbo.execute_dbupdate("INSERT INTO stockusagetype VALUES (4, '%s', '')" % _("Purchased", l))
    dbo.execute_dbupdate("INSERT INTO stockusagetype VALUES (5, '%s', '')" % _("Sold", l))
    dbo.execute_dbupdate("INSERT INTO stockusagetype VALUES (6, '%s', '')" % _("Stocktake", l))
    dbo.execute_dbupdate("INSERT INTO stockusagetype VALUES (7, '%s', '')" % _("Wasted", l))

def update_33501(dbo: Database) -> None:
    l = dbo.locale
    add_column(dbo, "animal", "IsPickup", "INTEGER")
    add_column(dbo, "animal", "PickupLocationID", "INTEGER")
    add_index(dbo, "animal_PickupLocationID", "animal", "PickupLocationID")
    sql = "CREATE TABLE pickuplocation ( ID INTEGER NOT NULL, " \
        "LocationName %(short)s NOT NULL, " \
        "LocationDescription %(long)s )" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
    dbo.execute_dbupdate(sql)
    dbo.execute_dbupdate("INSERT INTO pickuplocation VALUES (1, '%s', '')" % _("Shelter", l))

def update_33502(dbo: Database) -> None:
    l = dbo.locale
    # Add Transport movement type
    dbo.execute_dbupdate("INSERT INTO lksmovementtype (ID, MovementType) VALUES (13, ?)", [ _("Transport", l) ])

def update_33503(dbo: Database) -> None:
    # Add extra vaccination fields and some missing indexes
    add_column(dbo, "animalvaccination", "DateExpires", dbo.type_datetime)
    add_column(dbo, "animalvaccination", "BatchNumber", dbo.type_shorttext)
    add_column(dbo, "animalvaccination", "Manufacturer", dbo.type_shorttext)
    add_index(dbo, "animalvaccination_DateExpires", "animalvaccination", "DateExpires")
    add_index(dbo, "animalvaccination_DateRequired", "animalvaccination", "DateRequired")
    add_index(dbo, "animalvaccination_Manufacturer", "animalvaccination", "Manufacturer")
    add_index(dbo, "animaltest_DateRequired", "animaltest", "DateRequired")

def update_33504(dbo: Database) -> None:
    # Add daily email field to reports so they can be emailed to users
    add_column(dbo, "customreport", "DailyEmail", dbo.type_longtext)
    dbo.execute_dbupdate("UPDATE customreport SET DailyEmail = ''")

def update_33505(dbo: Database) -> None:
    # Add daily email hour field to reports
    add_column(dbo, "customreport", "DailyEmailHour", "INTEGER")
    dbo.execute_dbupdate("UPDATE customreport SET DailyEmailHour = -1")

def update_33506(dbo: Database) -> None:
    # Add location units field
    add_column(dbo, "internallocation", "Units", dbo.type_longtext)

def update_33507(dbo: Database) -> None:
    l = dbo.locale
    # Add reservation status
    add_column(dbo, "adoption", "ReservationStatusID", "INTEGER")
    add_index(dbo, "adoption_ReservationStatusID", "adoption", "ReservationStatusID")
    sql = "CREATE TABLE reservationstatus ( ID INTEGER NOT NULL, " \
        "StatusName %(short)s NOT NULL, " \
        "StatusDescription %(long)s )" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
    dbo.execute_dbupdate(sql)
    dbo.execute_dbupdate("INSERT INTO reservationstatus VALUES (1, '%s', '')" % _("More Info Needed", l))
    dbo.execute_dbupdate("INSERT INTO reservationstatus VALUES (2, '%s', '')" % _("Pending Vet Check", l))
    dbo.execute_dbupdate("INSERT INTO reservationstatus VALUES (3, '%s', '')" % _("Pending Apartment Verification", l))
    dbo.execute_dbupdate("INSERT INTO reservationstatus VALUES (4, '%s', '')" % _("Pending Home Visit", l))
    dbo.execute_dbupdate("INSERT INTO reservationstatus VALUES (5, '%s', '')" % _("Pending Adoption", l))
    dbo.execute_dbupdate("INSERT INTO reservationstatus VALUES (6, '%s', '')" % _("Changed Mind", l))
    dbo.execute_dbupdate("INSERT INTO reservationstatus VALUES (7, '%s', '')" % _("Denied", l))
    dbo.execute_dbupdate("INSERT INTO reservationstatus VALUES (8, '%s', '')" % _("Approved", l))

def update_33508(dbo: Database) -> None:
    # Increase the size of the onlineformfield tooltip as it was short text by mistake
    modify_column(dbo, "onlineformfield", "Tooltip", dbo.type_longtext)

def update_33600(dbo: Database) -> None:
    # Add additionalfield.IsSearchable
    add_column(dbo, "additionalfield", "Searchable", "INTEGER")

def update_33601(dbo: Database) -> None:
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
        "LastChangedDate %(date)s)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
    dbo.execute_dbupdate(sql)
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
    tr = dbo.query("SELECT * FROM adoption WHERE MovementType = 13")
    tid = 1
    for m in tr:
        try:
            dbo.execute_dbupdate("INSERT INTO animaltransport (ID, AnimalID, DriverOwnerID, PickupOwnerID, DropoffOwnerID, " \
            "PickupDateTime, DropoffDateTime, Status, Miles, Cost, Comments, RecordVersion, CreatedBy, " \
            "CreatedDate, LastChangedBy, LastChangedDate) VALUES ( " \
            "?, ?, 0, 0, 0, ?, ?, 3, 0, 0, ?, 1, 'update', ?, 'update', ?) ", \
            ( tid, m["ANIMALID"], m["MOVEMENTDATE"], m["MOVEMENTDATE"], m["COMMENTS"], 
              m["CREATEDDATE"], m["LASTCHANGEDDATE"] ) )
            tid += 1
        except Exception as err:
            asm3.al.error("failed creating animaltransport row %s: %s" % (tid, str(err)), "dbupdate.update_33601", dbo)
    # Remove old transport records and the type
    dbo.execute_dbupdate("DELETE FROM adoption WHERE MovementType = 13")
    dbo.execute_dbupdate("DELETE FROM lksmovementtype WHERE ID = 13")

def update_33602(dbo: Database) -> None:
    # Add animalfiguresannual.EntryReasonID
    add_column(dbo, "animalfiguresannual", "EntryReasonID", "INTEGER")
    add_index(dbo, "animalfiguresannual_EntryReasonID", "animalfiguresannual", "EntryReasonID")

def update_33603(dbo: Database) -> None:
    # Add additional.DefaultValue
    add_column(dbo, "additionalfield", "DefaultValue", dbo.type_longtext)

def update_33604(dbo: Database) -> None:
    # Add weight field
    add_column(dbo, "animal", "Weight", dbo.type_float)
    add_index(dbo, "animal_Weight", "animal", "Weight")
    # Add followupcomplete fields to animalcontrol
    add_column(dbo, "animalcontrol", "FollowupComplete", "INTEGER")
    add_column(dbo, "animalcontrol", "FollowupComplete2", "INTEGER")
    add_column(dbo, "animalcontrol", "FollowupComplete3", "INTEGER")
    add_index(dbo, "animalcontrol_FollowupComplete", "animalcontrol", "FollowupComplete")
    add_index(dbo, "animalcontrol_FollowupComplete2", "animalcontrol", "FollowupComplete2")
    add_index(dbo, "animalcontrol_FollowupComplete3", "animalcontrol", "FollowupComplete3")
    dbo.execute_dbupdate("UPDATE animalcontrol SET FollowupComplete = 0, FollowupComplete2 = 0, FollowupComplete3 = 0")
    dbo.execute_dbupdate("UPDATE animal SET Weight = 0")

def update_33605(dbo: Database) -> None:
    # Add accounts archived flag
    add_column(dbo, "accounts", "Archived", "INTEGER")
    add_index(dbo, "accounts_Archived", "accounts", "ARCHIVED")
    dbo.execute_dbupdate("UPDATE accounts SET Archived = 0")

def update_33606(dbo: Database) -> None:
    # Add new transport address fields
    add_column(dbo, "animaltransport", "PickupAddress", dbo.type_shorttext)
    add_column(dbo, "animaltransport", "PickupTown", dbo.type_shorttext)
    add_column(dbo, "animaltransport", "PickupCounty", dbo.type_shorttext)
    add_column(dbo, "animaltransport", "PickupPostcode", dbo.type_shorttext)
    add_column(dbo, "animaltransport", "DropoffAddress", dbo.type_shorttext)
    add_column(dbo, "animaltransport", "DropoffTown", dbo.type_shorttext)
    add_column(dbo, "animaltransport", "DropoffCounty", dbo.type_shorttext)
    add_column(dbo, "animaltransport", "DropoffPostcode", dbo.type_shorttext)
    add_index(dbo, "animaltransport_PickupAddress", "animaltransport", "PickupAddress")
    add_index(dbo, "animaltransport_DropoffAddress", "animaltransport", "DropoffAddress")

def update_33607(dbo: Database) -> None:
    # Copy addresses from any existing transport records to the new fields
    # (only acts on transport records with blank addresses)
    tr = dbo.query("SELECT animaltransport.ID, " \
        "dro.OwnerAddress AS DRA, dro.OwnerTown AS DRT, dro.OwnerCounty AS DRC, dro.OwnerPostcode AS DRP, " \
        "po.OwnerAddress AS POA, po.OwnerTown AS POT, po.OwnerCounty AS POC, po.OwnerPostcode AS POD " \
        "FROM animaltransport " \
        "INNER JOIN owner dro ON animaltransport.DropoffOwnerID = dro.ID " \
        "INNER JOIN owner po ON animaltransport.PickupOwnerID = po.ID "\
        "WHERE PickupAddress Is Null OR DropoffAddress Is Null")
    for t in tr:
        dbo.execute_dbupdate("UPDATE animaltransport SET " \
            "PickupAddress = ?, PickupTown = ?, PickupCounty = ?, PickupPostcode = ?,  " \
            "DropoffAddress = ?, DropoffTown = ?, DropoffCounty = ?, DropoffPostcode = ? " \
            "WHERE ID = ?", ( \
            t["POA"], t["POT"], t["POC"], t["POD"], 
            t["DRA"], t["DRT"], t["DRC"], t["DRP"],
            t["ID"] ))

def update_33608(dbo: Database) -> None:
    # Add pickuplocationid to incidents
    add_column(dbo, "animalcontrol", "PickupLocationID", "INTEGER")
    add_index(dbo, "animalcontrol_PickupLocationID", "animalcontrol", "PickupLocationID")
    dbo.execute_dbupdate("UPDATE animalcontrol SET PickupLocationID = 0")

def update_33609(dbo: Database) -> None:
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
        "LastChangedDate %(date)s)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
    dbo.execute_dbupdate(sql)
    add_index(dbo, "ownerrota_OwnerID", "ownerrota", "OwnerID")
    add_index(dbo, "ownerrota_StartDateTime", "ownerrota", "StartDateTime")
    add_index(dbo, "ownerrota_EndDateTime", "ownerrota", "EndDateTime")
    add_index(dbo, "ownerrota_RotaTypeID", "ownerrota", "RotaTypeID")
    # Add lksrotatype table
    sql = "CREATE TABLE lksrotatype ( ID INTEGER NOT NULL PRIMARY KEY, " \
        "RotaType %(short)s NOT NULL)" % { "short": dbo.type_shorttext }
    dbo.execute_dbupdate(sql)
    dbo.execute_dbupdate("INSERT INTO lksrotatype VALUES (1, ?)", [ _("Shift", l) ])
    dbo.execute_dbupdate("INSERT INTO lksrotatype VALUES (2, ?)", [ _("Vacation", l) ])
    dbo.execute_dbupdate("INSERT INTO lksrotatype VALUES (3, ?)", [_("Leave of absence", l) ])
    dbo.execute_dbupdate("INSERT INTO lksrotatype VALUES (4, ?)", [_("Maternity", l) ])
    dbo.execute_dbupdate("INSERT INTO lksrotatype VALUES (5, ?)", [_("Personal", l) ])
    dbo.execute_dbupdate("INSERT INTO lksrotatype VALUES (6, ?)", [_("Rostered day off", l) ])
    dbo.execute_dbupdate("INSERT INTO lksrotatype VALUES (7, ?)", [_("Sick leave", l) ])
    dbo.execute_dbupdate("INSERT INTO lksrotatype VALUES (8, ?)", [_("Training", l) ])
    dbo.execute_dbupdate("INSERT INTO lksrotatype VALUES (9, ?)", [_("Unavailable", l) ])

def update_33700(dbo: Database) -> None:
    # Add account.CostTypeID
    add_column(dbo, "accounts", "CostTypeID", "INTEGER")
    add_index(dbo, "accounts_CostTypeID", "accounts", "CostTypeID")
    # Add accountstrx.AnimalCostID
    add_column(dbo, "accountstrx", "AnimalCostID", "INTEGER")
    add_index(dbo, "accountstrx_AnimalCostID", "accountstrx", "AnimalCostID")
    # Default values
    dbo.execute_dbupdate("UPDATE accounts SET CostTypeID = 0")
    dbo.execute_dbupdate("UPDATE accountstrx SET AnimalCostID = 0")

def update_33701(dbo: Database) -> None:
    # If the user has no online forms, install the default set
    if 0 == dbo.query_int("SELECT COUNT(*) FROM onlineform"):
        install_default_onlineforms(dbo)

def update_33702(dbo: Database) -> None:
    # Add media.SignatureHash
    add_column(dbo, "media", "SignatureHash", dbo.type_shorttext)

def update_33703(dbo: Database) -> None:
    # Make stock levels floating point numbers instead
    modify_column(dbo, "stocklevel", "Total", dbo.type_float, "Total::real") 
    modify_column(dbo, "stocklevel", "Balance", dbo.type_float, "Balance::real") 
    modify_column(dbo, "stockusage", "Quantity", dbo.type_float, "Quantity::real") 

def update_33704(dbo: Database) -> None:
    # Add the default animalview template
    path = dbo.installpath
    asm2_dbfs_put_file(dbo, "body.html", "/internet/animalview", path + "media/internet/animalview/body.html")
    asm2_dbfs_put_file(dbo, "foot.html", "/internet/animalview", path + "media/internet/animalview/foot.html")
    asm2_dbfs_put_file(dbo, "head.html", "/internet/animalview", path + "media/internet/animalview/head.html")
    pass

def update_33705(dbo: Database) -> None:
    # Fix the animalview template to have OpenGraph meta tags
    # NOTE: Removed since the file has already been updated, this was a temporary fix
    # asm3.dbfs.replace_string(dbo, asm3.utils.read_text_file(dbo.installpath + "media/internet/animalview/head.html") , "head.html", "/internet/animalview")
    pass

def update_33706(dbo: Database) -> None:
    # Add users.Signature
    add_column(dbo, "users", "Signature", dbo.type_longtext)

def update_33707(dbo: Database) -> None:
    # Add animal links table
    fields = ",".join([
        dbo.ddl_add_table_column("AnimalControlID", dbo.type_integer, False),
        dbo.ddl_add_table_column("AnimalID", dbo.type_integer, False)
    ])
    dbo.execute_dbupdate( dbo.ddl_add_table("animalcontrolanimal", fields) )
    dbo.execute_dbupdate( dbo.ddl_add_index("animalcontrolanimal_AnimalControlIDAnimalID", "animalcontrolanimal", "AnimalControlID,AnimalID", True) )
    # Copy the existing links from animalcontrol.AnimalID
    for ac in dbo.query("SELECT ID, AnimalID FROM animalcontrol WHERE AnimalID Is Not Null AND AnimalID <> 0"):
        dbo.execute_dbupdate("INSERT INTO animalcontrolanimal (AnimalControlID, AnimalID) VALUES (%d, %d)" % (ac["ID"], ac["ANIMALID"]))
    # Remove the animalid field from animalcontrol
    if column_exists(dbo, "animalcontrol", "AnimalID"):
        drop_index(dbo, "animalcontrol_AnimalID", "animalcontrol")
        drop_column(dbo, "animalcontrol", "AnimalID")

def update_33708(dbo: Database) -> None:
    # Add basecolour.AdoptAPetColour
    add_column(dbo, "basecolour", "AdoptAPetColour", dbo.type_shorttext)

def update_33709(dbo: Database) -> None:
    l = dbo.locale
    # Move all rota types above shift up 2 places
    dbo.execute_dbupdate("UPDATE lksrotatype SET ID = ID + 10 WHERE ID > 1")
    dbo.execute_dbupdate("UPDATE ownerrota SET RotaTypeID = RotaTypeID + 10 WHERE RotaTypeID > 1")
    # Insert two new types
    dbo.execute_dbupdate("INSERT INTO lksrotatype (ID, RotaType) VALUES (2, ?)",  [ _("Overtime", l) ])
    dbo.execute_dbupdate("INSERT INTO lksrotatype (ID, RotaType) VALUES (11, ?)", [ _("Public Holiday", l) ])

def update_33710(dbo: Database) -> None:
    # Turn off forcereupload as it should no longer be needed
    p = dbo.query_string("SELECT ItemValue FROM configuration WHERE ItemName LIKE 'PublisherPresets'")
    s = []
    for x in p.split(" "):
        if x != "forcereupload": s.append(x)
    dbo.execute_dbupdate("UPDATE configuration SET ItemValue = '%s' WHERE ItemName LIKE 'PublisherPresets'" % " ".join(s))

def update_33711(dbo: Database) -> None:
    # Add ownerdonation.ReceiptNumber
    add_column(dbo, "ownerdonation", "ReceiptNumber", dbo.type_shorttext)
    add_index(dbo, "ownerdonation_ReceiptNumber", "ownerdonation", "ReceiptNumber")
    # Use ID to prepopulate existing records
    dbo.execute_dbupdate("UPDATE ownerdonation SET ReceiptNumber = %s" % dbo.sql_zero_pad_left("ID", 8))

def update_33712(dbo: Database) -> None:
    # Add ownerdonation Sales Tax/VAT fields
    add_column(dbo, "ownerdonation", "IsVAT", "INTEGER")
    add_column(dbo, "ownerdonation", "VATRate", dbo.type_float)
    add_column(dbo, "ownerdonation", "VATAmount", "INTEGER")
    add_index(dbo, "ownerdonation_IsVAT", "ownerdonation", "IsVAT")
    dbo.execute_dbupdate("UPDATE ownerdonation SET IsVAT=0, VATRate=0, VATAmount=0")

def update_33713(dbo: Database) -> None:
    # Create animal flags table
    sql = "CREATE TABLE lkanimalflags ( ID INTEGER NOT NULL, " \
        "Flag %s NOT NULL)" % dbo.type_shorttext
    dbo.execute_dbupdate(sql)
    # Add additionalflags field to animal
    add_column(dbo, "animal", "AdditionalFlags", dbo.type_longtext)
    # Add IsCourtesy to animal
    add_column(dbo, "animal", "IsCourtesy", "INTEGER")
    dbo.execute_dbupdate("UPDATE animal SET IsCourtesy=0, AdditionalFlags=''")

def update_33714(dbo: Database) -> None:
    # ASM3 requires a nonzero value for RecordSearchLimit where ASM2 does not
    dbo.execute_dbupdate("UPDATE configuration SET ItemValue = '1000' WHERE ItemName LIKE 'RecordSearchLimit'")

def update_33715(dbo: Database) -> None:
    # Add owner.FosterCapacity field
    add_column(dbo, "owner", "FosterCapacity", "INTEGER")
    dbo.execute_dbupdate("UPDATE owner SET FosterCapacity=0")
    dbo.execute_dbupdate("UPDATE owner SET FosterCapacity=1 WHERE IsFosterer=1")

def update_33716(dbo: Database) -> None:
    # Switch ui-lightness and smoothness to the new asm replacement theme
    dbo.execute_dbupdate("UPDATE configuration SET itemvalue='asm' WHERE itemvalue = 'smoothness' OR itemvalue = 'ui-lightness'")

def update_33717(dbo: Database) -> None:
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
    for c in dbo.query("SELECT ID FROM basecolour WHERE ID <= 59 AND (AdoptAPetColour Is Null OR AdoptAPetColour = '')"):
        if c["ID"] in defmap:
            dbo.execute_dbupdate("UPDATE basecolour SET AdoptAPetColour=? WHERE ID=?", [ defmap[c["ID"]], c["ID"] ])

def update_33718(dbo: Database) -> None:
    # Add TotalTimeOnShelter, TotalDaysOnShelter
    add_column(dbo, "animal", "TotalDaysOnShelter", "INTEGER")
    add_column(dbo, "animal", "TotalTimeOnShelter", dbo.type_shorttext)
    dbo.execute_dbupdate("UPDATE animal SET TotalDaysOnShelter=0, TotalTimeOnShelter=''")

def update_33800(dbo: Database) -> None:
    # Add IsRetired field to lookups
    retirablelookups = [ "animaltype", "basecolour", "breed", "citationtype", "costtype", 
        "deathreason", "diet", "donationpayment", "donationtype", "entryreason", "incidentcompleted", 
        "incidenttype", "internallocation", "licencetype", "logtype", "pickuplocation", 
        "reservationstatus", "species", "stocklocation", "stockusagetype", "testtype", 
        "testresult", "traptype", "vaccinationtype", "voucher" ]
    for t in retirablelookups:
        add_column(dbo, t, "IsRetired", "INTEGER")
        dbo.execute_dbupdate("UPDATE %s SET IsRetired = 0" % t)

def update_33801(dbo: Database) -> None:
    # Add animal.PickupAddress, animalvaccination.AdministeringVetID and animalmedicaltreatment.AdministeringVetID
    add_column(dbo, "animal", "PickupAddress", dbo.type_shorttext)
    add_column(dbo, "animalmedicaltreatment", "AdministeringVetID", "INTEGER")
    add_column(dbo, "animalvaccination", "AdministeringVetID", "INTEGER")
    add_index(dbo, "animal_PickupAddress", "animal", "PickupAddress")
    add_index(dbo, "animalmedicaltreatment_AdministeringVetID", "animalmedicaltreatment", "AdministeringVetID")
    add_index(dbo, "animalvaccination_AdministeringVetID", "animalvaccination", "AdministeringVetID")
    dbo.execute_dbupdate("UPDATE animal SET PickupAddress = ''")
    dbo.execute_dbupdate("UPDATE animalmedicaltreatment SET AdministeringVetID = 0")
    dbo.execute_dbupdate("UPDATE animalvaccination SET AdministeringVetID = 0")

def update_33802(dbo: Database) -> None:
    # Remove the Incident - Citation link from additional fields as it's no longer valid
    dbo.execute_dbupdate("DELETE FROM lksfieldlink WHERE ID = 19")

def update_33803(dbo: Database) -> None:
    # Install new incident information template
    path = dbo.installpath
    asm2_dbfs_put_file(dbo, "incident_information.html", "/templates", path + "media/templates/incident_information.html")

def update_33900(dbo: Database) -> None:
    # Add extra payment fields
    add_column(dbo, "ownerdonation", "Quantity", "INTEGER")
    add_column(dbo, "ownerdonation", "UnitPrice", "INTEGER")
    add_column(dbo, "ownerdonation", "ChequeNumber", dbo.type_shorttext)
    add_index(dbo, "ownerdonation_ChequeNumber", "ownerdonation", "ChequeNumber")
    dbo.execute_dbupdate("UPDATE ownerdonation SET Quantity = 1, UnitPrice = Donation, ChequeNumber = ''")

def update_33901(dbo: Database) -> None:
    # Add audittrail.LinkID field
    add_column(dbo, "audittrail", "LinkID", "INTEGER")
    add_index(dbo, "audittrail_LinkID", "audittrail", "LinkID")
    dbo.execute_dbupdate("UPDATE audittrail SET LinkID = 0")

def update_33902(dbo: Database) -> None:
    # Add asm3.onlineform.EmailSubmitter field
    add_column(dbo, "onlineform", "EmailSubmitter", "INTEGER")
    dbo.execute_dbupdate("UPDATE onlineform SET EmailSubmitter = 1")

def update_33903(dbo: Database) -> None:
    # Add customreport.DailyEmailFrequency
    add_column(dbo, "customreport", "DailyEmailFrequency", "INTEGER")
    dbo.execute_dbupdate("UPDATE customreport SET DailyEmailFrequency = 0")

def update_33904(dbo: Database) -> None:
    # Add ownerlookingfor table
    sql = "CREATE TABLE ownerlookingfor ( " \
        "OwnerID INTEGER NOT NULL, " \
        "AnimalID INTEGER NOT NULL, " \
        "MatchSummary %s NOT NULL)" % dbo.type_longtext
    dbo.execute_dbupdate(sql)
    add_index(dbo, "ownerlookingfor_OwnerID", "ownerlookingfor", "OwnerID")
    add_index(dbo, "ownerlookingfor_AnimalID", "ownerlookingfor", "AnimalID")
    # Add animallostfoundmatch table
    sql = "CREATE TABLE animallostfoundmatch ( " \
        "AnimalLostID INTEGER NOT NULL, " \
        "AnimalFoundID INTEGER, " \
        "AnimalID INTEGER, " \
        "LostContactName %(short)s, " \
        "LostContactNumber %(short)s, " \
        "LostArea %(short)s, " \
        "LostPostcode %(short)s, " \
        "LostAgeGroup %(short)s, " \
        "LostSex INTEGER, " \
        "LostSpeciesID INTEGER, " \
        "LostBreedID INTEGER, " \
        "LostFeatures %(long)s, " \
        "LostBaseColourID INTEGER, " \
        "LostDate %(date)s, " \
        "FoundContactName %(short)s, " \
        "FoundContactNumber %(short)s, " \
        "FoundArea %(short)s, " \
        "FoundPostcode %(short)s, " \
        "FoundAgeGroup %(short)s, " \
        "FoundSex INTEGER, " \
        "FoundSpeciesID INTEGER, " \
        "FoundBreedID INTEGER, " \
        "FoundFeatures %(long)s, " \
        "FoundBaseColourID INTEGER, " \
        "FoundDate %(date)s, " \
        "MatchPoints INTEGER NOT NULL)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
    dbo.execute_dbupdate(sql)
    add_index(dbo, "animallostfoundmatch_AnimalLostID", "animallostfoundmatch", "AnimalLostID")
    add_index(dbo, "animallostfoundmatch_AnimalFoundID", "animallostfoundmatch", "AnimalFoundID")
    add_index(dbo, "animallostfoundmatch_AnimalID", "animallostfoundmatch", "AnimalID")

def update_33905(dbo: Database) -> None:
    # Add PurchasePrice/SalePrice fields to stocklevel
    add_column(dbo, "stocklevel", "Cost", "INTEGER")
    add_column(dbo, "stocklevel", "UnitPrice", "INTEGER")
    dbo.execute_dbupdate("UPDATE stocklevel SET Cost = 0, UnitPrice = 0")

def update_33906(dbo: Database) -> None:
    l = dbo.locale
    # Add ownerrota.WorkTypeID
    add_column(dbo, "ownerrota", "WorkTypeID", "INTEGER")
    add_index(dbo, "ownerrota_WorkTypeID", "ownerrota", "WorkTypeID")
    dbo.execute_dbupdate("UPDATE ownerrota SET WorkTypeID = 1")
    # Add lkworktype
    sql = "CREATE TABLE lkworktype ( ID INTEGER NOT NULL PRIMARY KEY, " \
        "WorkType %(short)s NOT NULL)" % { "short": dbo.type_shorttext }
    dbo.execute_dbupdate(sql)
    dbo.execute_dbupdate("INSERT INTO lkworktype (ID, WorkType) VALUES (?, ?)", [1, _("General", l)] )
    dbo.execute_dbupdate("INSERT INTO lkworktype (ID, WorkType) VALUES (?, ?)", [2, _("Kennel", l)] )
    dbo.execute_dbupdate("INSERT INTO lkworktype (ID, WorkType) VALUES (?, ?)", [3, _("Cattery", l)] )
    dbo.execute_dbupdate("INSERT INTO lkworktype (ID, WorkType) VALUES (?, ?)", [4, _("Reception", l)] )
    dbo.execute_dbupdate("INSERT INTO lkworktype (ID, WorkType) VALUES (?, ?)", [5, _("Office", l)] )

def update_33907(dbo: Database) -> None:
    # Add animaltest.AdministeringVetID
    add_column(dbo, "animaltest", "AdministeringVetID", "INTEGER")
    add_index(dbo, "animaltest_AdministeringVetID", "animaltest", "AdministeringVetID")
    dbo.execute_dbupdate("UPDATE animaltest SET AdministeringVetID = 0")

def update_33908(dbo: Database) -> None:
    # Add site table
    sql = "CREATE TABLE site (ID INTEGER NOT NULL PRIMARY KEY, " \
        "SiteName %s NOT NULL)" % dbo.type_shorttext
    dbo.execute_dbupdate(sql)
    dbo.execute_dbupdate("INSERT INTO site VALUES (1, 'main')")
    # Add internallocation.SiteID
    add_column(dbo, "internallocation", "SiteID", "INTEGER")
    dbo.execute_dbupdate("UPDATE internallocation SET SiteID = 1")
    # Add users.SiteID
    add_column(dbo, "users", "SiteID", "INTEGER")
    dbo.execute_dbupdate("UPDATE users SET SiteID = 0")

def update_33909(dbo: Database) -> None:
    # Add adoption coordinator
    add_column(dbo, "animal", "AdoptionCoordinatorID", "INTEGER")
    add_index(dbo, "animal_AdoptionCoordinatorID", "animal", "AdoptionCoordinatorID")
    dbo.execute_dbupdate("UPDATE animal SET AdoptionCoordinatorID = 0")

def update_33911(dbo: Database) -> None:
    # NB: 33910 was broken so moved to 33911 and fixed
    # Cannot usually modify a column that a view depends on in Postgres
    if dbo.dbtype == "POSTGRESQL": dbo.execute_dbupdate("DROP VIEW v_animalwaitinglist")
    # Extend animalasm3.waitinglist.AnimalDescription
    modify_column(dbo, "animalwaitinglist", "AnimalDescription", dbo.type_longtext)

def update_33912(dbo: Database) -> None:
    # Add EmailConfirmationMessage
    add_column(dbo, "onlineform", "EmailMessage", dbo.type_longtext)
    dbo.execute_dbupdate("UPDATE onlineform SET EmailMessage = ''")

def update_33913(dbo: Database) -> None:
    # Add owner.OwnerCode
    add_column(dbo, "owner", "OwnerCode", dbo.type_shorttext)
    add_index(dbo, "owner_OwnerCode", "owner", "OwnerCode")
    dbo.execute_dbupdate("UPDATE owner SET OwnerCode = %s" % dbo.sql_concat([ dbo.sql_substring("UPPER(OwnerSurname)", 1, 2), dbo.sql_zero_pad_left("ID", 6) ]))

def update_33914(dbo: Database) -> None:
    # Add owner.IsAdoptionCoordinator
    add_column(dbo, "owner", "IsAdoptionCoordinator", "INTEGER")
    dbo.execute_dbupdate("UPDATE owner SET IsAdoptionCoordinator = 0")

def update_33915(dbo: Database) -> None:
    # Add the animalcontrolrole table
    dbo.execute_dbupdate("CREATE TABLE animalcontrolrole (AnimalControlID INTEGER NOT NULL, " \
        "RoleID INTEGER NOT NULL, CanView INTEGER NOT NULL, CanEdit INTEGER NOT NULL)")
    dbo.execute_dbupdate("CREATE UNIQUE INDEX animalcontrolrole_AnimalControlIDRoleID ON animalcontrolrole(AnimalControlID, RoleID)")

def update_33916(dbo: Database) -> None:
    # Add SiteID to people and incidents
    add_column(dbo, "owner", "SiteID", "INTEGER")
    add_index(dbo, "owner_SiteID", "owner", "SiteID")
    add_column(dbo, "animalcontrol", "SiteID", "INTEGER")
    add_index(dbo, "animalcontrol_SiteID", "animalcontrol", "SiteID")
    dbo.execute_dbupdate("UPDATE owner SET SiteID = 0")
    dbo.execute_dbupdate("UPDATE animalcontrol SET SiteID = 0")

def update_34000(dbo: Database) -> None:
    # Add missing LostArea and FoundArea fields due to broken schema
    if not column_exists(dbo, "animallostfoundmatch", "LostArea"):
        add_column(dbo, "animallostfoundmatch", "LostArea", dbo.type_shorttext)
    if not column_exists(dbo, "animallostfoundmatch", "FoundArea"):
        add_column(dbo, "animallostfoundmatch", "FoundArea", dbo.type_shorttext)

def update_34001(dbo: Database) -> None:
    # Remove the unique index on LicenceNumber and make it non-unique (optionally enforced by backend code)
    drop_index(dbo, "ownerlicence_LicenceNumber", "ownerlicence")
    add_index(dbo, "ownerlicence_LicenceNumber", "ownerlicence", "LicenceNumber")

def update_34002(dbo: Database) -> None:
    # Add asm3.dbfs.URL field and index
    add_column(dbo, "dbfs", "URL", dbo.type_shorttext)
    add_index(dbo, "dbfs_URL", "dbfs", "URL")
    dbo.execute_dbupdate("UPDATE dbfs SET URL = 'base64:'")

def update_34003(dbo: Database) -> None:
    # Add indexes to animal and owner created for find animal/person
    add_index(dbo, "animal_CreatedBy", "animal", "CreatedBy")
    add_index(dbo, "animal_CreatedDate", "animal", "CreatedDate")
    add_index(dbo, "owner_CreatedBy", "owner", "CreatedBy")
    add_index(dbo, "owner_CreatedDate", "owner", "CreatedDate")

def update_34004(dbo: Database) -> None:
    l = dbo.locale
    # Add the TransportTypeID column
    add_column(dbo, "animaltransport", "TransportTypeID", "INTEGER")
    add_index(dbo, "animaltransport_TransportTypeID", "animaltransport", "TransportTypeID")
    dbo.execute_dbupdate("UPDATE animaltransport SET TransportTypeID = 4") # Vet Visit
    # Add the transporttype lookup table
    sql = "CREATE TABLE transporttype ( ID INTEGER NOT NULL, " \
        "TransportTypeName %(short)s NOT NULL, " \
        "TransportTypeDescription %(long)s, " \
        "IsRetired INTEGER)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
    dbo.execute_dbupdate(sql)
    dbo.execute_dbupdate("INSERT INTO transporttype VALUES (1, '%s', '', 0)" % _("Adoption Event", l))
    dbo.execute_dbupdate("INSERT INTO transporttype VALUES (2, '%s', '', 0)" % _("Foster Transfer", l))
    dbo.execute_dbupdate("INSERT INTO transporttype VALUES (3, '%s', '', 0)" % _("Surrender Pickup", l))
    dbo.execute_dbupdate("INSERT INTO transporttype VALUES (4, '%s', '', 0)" % _("Vet Visit", l))

def update_34005(dbo: Database) -> None:
    # Add the publishlog table
    sql = "CREATE TABLE publishlog ( ID INTEGER NOT NULL, " \
        "PublishDateTime %(date)s NOT NULL, " \
        "Name %(short)s NOT NULL, " \
        "Success INTEGER NOT NULL, " \
        "Alerts INTEGER NOT NULL, " \
        "LogData %(long)s NOT NULL)" % { "date": dbo.type_datetime, "short": dbo.type_shorttext, "long": dbo.type_longtext }
    dbo.execute_dbupdate(sql)
    add_index(dbo, "publishlog_PublishDateTime", "publishlog", "PublishDateTime")
    add_index(dbo, "publishlog_Name", "publishlog", "Name")
    # Remove old publish logs, reports and asm news from the dbfs
    dbo.execute_dbupdate("DELETE FROM dbfs WHERE Path LIKE '/logs%'")
    dbo.execute_dbupdate("DELETE FROM dbfs WHERE Path LIKE '/reports/daily%'")
    dbo.execute_dbupdate("DELETE FROM dbfs WHERE Name LIKE 'asm.news'")

def update_34006(dbo: Database) -> None:
    # Set includenonneutered in the publishing presets
    s = asm3.configuration.publisher_presets(dbo)
    s += " includenonneutered"
    dbo.execute_dbupdate("UPDATE configuration SET ItemValue = ? WHERE ItemName = 'PublisherPresets'", [ s ])

def update_34007(dbo: Database) -> None:
    # Add missing indexes to DiedOffShelter / NonShelterAnimal
    add_index(dbo, "animal_DiedOffShelter", "animal", "DiedOffShelter")
    add_index(dbo, "animal_NonShelterAnimal", "animal", "NonShelterAnimal")

def update_34008(dbo: Database) -> None:
    # Remove the old asilomar figures report if it exists
    dbo.execute_dbupdate("DELETE FROM customreport WHERE Title = 'Asilomar Figures'")
    # Remove the asilomar tables as they're no longer needed
    dbo.execute_dbupdate("DROP TABLE animalfiguresasilomar")
    dbo.execute_dbupdate("DROP TABLE animalfiguresmonthlyasilomar")

def update_34009(dbo: Database) -> None:
    # Set includewithoutdescription in the publishing presets
    s = asm3.configuration.publisher_presets(dbo)
    s += " includewithoutdescription"
    dbo.execute_dbupdate("UPDATE configuration SET ItemValue = ? WHERE ItemName = 'PublisherPresets'", [ s ])

def update_34010(dbo: Database) -> None:
    # Add an index on additional.linkid for performance
    add_index(dbo, "additional_LinkID", "additional", "LinkID")

def update_34011(dbo: Database) -> None:
    # Add users.DisableLogin
    add_column(dbo, "users", "DisableLogin", "INTEGER")
    dbo.execute_dbupdate("UPDATE users SET DisableLogin = 0")

def update_34012(dbo: Database) -> None:
    # Add diarytaskdetail.OrderIndex
    add_column(dbo, "diarytaskdetail", "OrderIndex", "INTEGER")
    dbo.execute_dbupdate("UPDATE diarytaskdetail SET OrderIndex = ID")

def update_34013(dbo: Database) -> None:
    # More indexes to speed up get_alerts
    add_index(dbo, "animal_Neutered", "animal", "Neutered")
    add_index(dbo, "owner_IDCheck", "owner", "IDCheck")
    add_index(dbo, "owner_IsACO", "owner", "IsACO")
    add_index(dbo, "owner_IsAdoptionCoordinator", "owner", "IsAdoptionCoordinator")
    add_index(dbo, "owner_IsFosterer", "owner", "IsFosterer")
    add_index(dbo, "owner_IsRetailer", "owner", "IsRetailer")
    add_index(dbo, "owner_IsStaff", "owner", "IsStaff")
    add_index(dbo, "owner_IsVet", "owner", "IsVet")
    add_index(dbo, "owner_IsVolunteer", "owner", "IsVolunteer")
    add_index(dbo, "ownerdonation_DateDue", "ownerdonation", "DateDue")

def update_34014(dbo: Database) -> None:
    # Add a new MediaMimeType column
    add_column(dbo, "media", "MediaMimeType", dbo.type_shorttext)
    add_index(dbo, "media_MediaMimeType", "media", "MediaMimeType")
    types = {
        "%jpg"           : "image/jpeg",
        "%jpeg"          : "image/jpeg",
        "%odt"           : "application/vnd.oasis.opendocument.text",
        "%pdf"           : "application/pdf",
        "%html"          : "text/html",
        "http%"          : "text/url"
    }
    for k, v in types.items():
        dbo.execute_dbupdate("UPDATE media SET MediaMimeType = ? WHERE LOWER(MediaName) LIKE ?", (v, k))
    dbo.execute_dbupdate("UPDATE media SET MediaMimeType = 'application/octet-stream' WHERE MediaMimeType Is Null")

def update_34015(dbo: Database) -> None:
    # Add new MediaSize and DBFSID columns
    add_column(dbo, "media", "MediaSize", dbo.type_integer)
    add_column(dbo, "media", "DBFSID", dbo.type_integer)
    add_index(dbo, "media_DBFSID", "media", "DBFSID")
    # Set sizes to 0 they'll be updated by another process later 
    dbo.execute_dbupdate("UPDATE media SET MediaSize = 0")
    # Find the right DBFS element for each media item
    dbo.execute_dbupdate("UPDATE media SET DBFSID = (SELECT MAX(ID) FROM dbfs WHERE Name LIKE media.MediaName) WHERE MediaType=0")
    dbo.execute_dbupdate("UPDATE media SET DBFSID = 0 WHERE DBFSID Is Null")
    # Remove any _scaled component of names from both media and dbfs
    dbo.execute_dbupdate("UPDATE media SET MediaName = %s WHERE MediaName LIKE '%%_scaled%%'" % dbo.sql_replace("MediaName", "_scaled", ""))
    dbo.execute_dbupdate("UPDATE dbfs SET Name = %s WHERE Name LIKE '%%_scaled%%'" % dbo.sql_replace("Name", "_scaled", ""))

def update_34016(dbo: Database) -> None:
    l = dbo.locale
    # Add JurisdictionID
    add_column(dbo, "owner", "JurisdictionID", dbo.type_integer)
    add_column(dbo, "animalcontrol", "JurisdictionID", dbo.type_integer)
    add_index(dbo, "owner_JurisdictionID", "owner", "JurisdictionID")
    add_index(dbo, "animalcontrol_JurisdictionID", "animalcontrol", "JurisdictionID")
    sql = "CREATE TABLE jurisdiction ( ID INTEGER NOT NULL, " \
        "JurisdictionName %(short)s NOT NULL, " \
        "JurisdictionDescription %(long)s, " \
        "IsRetired INTEGER)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
    dbo.execute_dbupdate(sql)
    dbo.execute_dbupdate("UPDATE owner SET JurisdictionID = 0")
    dbo.execute_dbupdate("UPDATE animalcontrol SET JurisdictionID = 0")
    dbo.execute_dbupdate("INSERT INTO jurisdiction VALUES (1, '%s', '', 0)" % _("Local", l))

def update_34017(dbo: Database) -> None:
    # Add extra microchip fields
    add_column(dbo, "animal", "Identichip2Number", dbo.type_shorttext)
    add_column(dbo, "animal", "Identichip2Date", dbo.type_datetime)
    add_index(dbo, "animal_Identichip2Number", "animal", "Identichip2Number")

def update_34018(dbo: Database) -> None:
    # Add ReturnedByOwnerID
    add_column(dbo, "adoption", "ReturnedByOwnerID", dbo.type_integer)
    add_index(dbo, "adoption_ReturnedByOwnerID", "adoption", "ReturnedByOwnerID")
    dbo.execute_dbupdate("UPDATE adoption SET ReturnedByOwnerID = 0")

def update_34019(dbo: Database) -> None:
    # Add NeuteredByVetID
    add_column(dbo, "animal", "NeuteredByVetID", dbo.type_integer)
    add_index(dbo, "animal_NeuteredByVetID", "animal", "NeuteredByVetID")
    dbo.execute_dbupdate("UPDATE animal SET NeuteredByVetID = 0")

def update_34020(dbo: Database) -> None:
    # Add IsNotForRegistration
    add_column(dbo, "animal", "IsNotForRegistration", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE animal SET IsNotForRegistration = 0")

def update_34021(dbo: Database) -> None:
    # Add RetainUntil to expire media on a set date
    add_column(dbo, "media", "RetainUntil", dbo.type_datetime)
    add_index(dbo, "media_RetainUntil", "media", "RetainUntil")
    add_index(dbo, "media_Date", "media", "Date") # seemed to be missing previously

def update_34022(dbo: Database) -> None:
    # Add AgeGroupActiveMovement
    add_column(dbo, "animal", "AgeGroupActiveMovement", dbo.type_shorttext)

def update_34100(dbo: Database) -> None:
    # Add templatehtml table
    fields = ",".join([
        dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
        dbo.ddl_add_table_column("Name", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("Header", dbo.type_longtext, False),
        dbo.ddl_add_table_column("Body", dbo.type_longtext, True),
        dbo.ddl_add_table_column("Footer", dbo.type_longtext, True),
        dbo.ddl_add_table_column("IsBuiltIn", dbo.type_integer, False) ])
    dbo.execute_dbupdate( dbo.ddl_add_table("templatehtml", fields) )
    dbo.execute_dbupdate( dbo.ddl_add_index("templatehtml_Name", "templatehtml", "Name", True) )
    # Copy HTML templates from DBFS - we track ID manually as the sequence won't be created yet
    nextid = 1
    for row in dbo.query("SELECT Name, Path FROM dbfs WHERE Path Like '/internet' AND Name NOT LIKE '%.%' ORDER BY Name"):
        head = asm3.dbfs.get_string(dbo, "head.html", "/internet/%s" % row.name)
        foot = asm3.dbfs.get_string(dbo, "foot.html", "/internet/%s" % row.name)
        body = asm3.dbfs.get_string(dbo, "body.html", "/internet/%s" % row.name)
        dbo.insert("templatehtml", {
            "ID":       nextid,
            "Name":     row.name,
            "*Header":  asm3.utils.bytes2str(head),
            "*Body":    asm3.utils.bytes2str(body),
            "*Footer":  asm3.utils.bytes2str(foot),
            "IsBuiltIn":  0
        }, generateID=False, setOverrideDBLock=True)
        nextid += 1
    # Copy fixed templates for report header/footer and online form header/footer
    if asm3.dbfs.file_exists(dbo, "head.html", "/reports") and asm3.dbfs.file_exists(dbo, "foot.html"):
        reporthead = asm3.dbfs.get_string(dbo, "head.html", "/reports")
        reportfoot = asm3.dbfs.get_string(dbo, "foot.html", "/reports")
        if reporthead != "":
            dbo.insert("templatehtml", {
                "ID":       nextid,
                "Name":     "report",
                "*Header":  asm3.utils.bytes2str(reporthead),
                "*Body":    "",
                "*Footer":  asm3.utils.bytes2str(reportfoot),
                "IsBuiltIn":  1
            }, generateID=False, setOverrideDBLock=True)
            nextid += 1
    if asm3.dbfs.file_exists(dbo, "head.html", "/onlineform") and asm3.dbfs.file_exists(dbo, "foot.html", "/onlineform"):
        ofhead = asm3.dbfs.get_string(dbo, "head.html", "/onlineform")
        offoot = asm3.dbfs.get_string(dbo, "foot.html", "/onlineform")
        if ofhead != "":
            dbo.insert("templatehtml", {
                "ID":       nextid,
                "Name":     "onlineform",
                "*Header":  asm3.utils.bytes2str(ofhead),
                "*Body":    "",
                "*Footer":  asm3.utils.bytes2str(offoot),
                "IsBuiltIn":  1
            }, generateID=False, setOverrideDBLock=True)

def update_34101(dbo: Database) -> None:
    # Add templatedocument table and copy templates from DBFS
    fields = ",".join([
        dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
        dbo.ddl_add_table_column("Name", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("Path", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("Content", dbo.type_longtext, False) ])
    dbo.execute_dbupdate( dbo.ddl_add_table("templatedocument", fields) )
    dbo.execute_dbupdate( dbo.ddl_add_index("templatedocument_NamePath", "templatedocument", "Name,Path", True) )
    # Copy document templates from DBFS - we track ID manually as the sequence won't be created yet
    nextid = 1
    for row in dbo.query("SELECT ID, Name, Path FROM dbfs WHERE Path Like '/templates%' AND (Name LIKE '%.html' OR Name LIKE '%.odt') ORDER BY Name"):
        content = asm3.dbfs.get_string_id(dbo, row.id)
        dbo.insert("templatedocument", {
            "ID":       nextid,
            "Name":     row.name,
            "Path":     row.path,
            "Content":  asm3.utils.base64encode(content)
        }, generateID=False, setOverrideDBLock=True)
        nextid += 1

def update_34102(dbo: Database) -> None:
    if asm3.smcom.active():
        # sheltermanager.com only: calculate media file sizes for existing databases
        # ===
        # Reapply update 34015 where necessary as it was botched on some smcom databases
        dbo.execute_dbupdate("UPDATE media SET DBFSID = (SELECT MAX(ID) FROM dbfs WHERE Name LIKE media.MediaName) WHERE DBFSID Is Null OR DBFSID = 0")
        dbo.execute_dbupdate("UPDATE media SET DBFSID = 0 WHERE DBFSID Is Null")
        # Remove any _scaled component of names from both media and dbfs
        dbo.execute_dbupdate("UPDATE media SET MediaName = %s WHERE MediaName LIKE '%%_scaled%%'" % dbo.sql_replace("MediaName", "_scaled", ""))
        dbo.execute_dbupdate("UPDATE dbfs SET Name = %s WHERE Name LIKE '%%_scaled%%'" % dbo.sql_replace("Name", "_scaled", ""))
        # Read the file size of all media files that are not set and update the media table
        batch = []
        for r in dbo.query("SELECT ID, DBFSID, MediaName FROM media WHERE (MediaSize Is Null OR MediaSize = 0) AND (DBFSID Is Not Null AND DBFSID > 0)"):
            ext = r.medianame[r.medianame.rfind("."):]
            fname = "/root/media/%s/%s%s" % (dbo.name(), r.dbfsid, ext)
            try:
                fsize = os.path.getsize(fname)
                batch.append( (fsize, r.id) )
            except:
                pass # Ignore attempts to read non-existent files
        dbo.execute_many("UPDATE media SET MediaSize = ? WHERE ID = ?", batch, override_lock=True) 

def update_34103(dbo: Database) -> None:
    if asm3.smcom.active():
        # sheltermanager.com only: Final switch over to access old media from S3 instead of filesystem
        dbo.execute_dbupdate("UPDATE dbfs SET url = replace(url, 'file:', 's3:') where url like 'file:%'")

def update_34104(dbo: Database) -> None:
    l = dbo.locale
    # Add owner.GDPRContactOptIn
    add_column(dbo, "owner", "GDPRContactOptIn", dbo.type_shorttext)
    add_index(dbo, "owner_GDPRContactOptIn", "owner", "GDPRContactOptIn")
    dbo.execute_dbupdate("UPDATE owner SET GDPRContactOptIn = ''")
    # Add a new GDPR contact opt-in log type
    ltid = dbo.get_id_max("logtype")
    dbo.insert("logtype", { "ID": ltid, "LogTypeName": _("GDPR Contact Opt-In", l), "IsRetired": 0 }, setOverrideDBLock=True)
    asm3.configuration.cset(dbo, "GDPRContactChangeLogType", str(ltid), ignoreDBLock=True)

def update_34105(dbo: Database) -> None:
    # Add deletion table
    fields = ",".join([
        dbo.ddl_add_table_column("ID", dbo.type_integer, False),
        dbo.ddl_add_table_column("TableName", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("DeletedBy", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("Date", dbo.type_datetime, False),
        dbo.ddl_add_table_column("IDList", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("RestoreSQL", dbo.type_longtext, False) ])
    dbo.execute_dbupdate( dbo.ddl_add_table("deletion", fields) )
    dbo.execute_dbupdate( dbo.ddl_add_index("deletion_IDTablename", "deletion", "ID,Tablename") )

def update_34106(dbo: Database) -> None:
    # Remove recordversion and created/lastchanged columns from role tables - should never have been there
    # and has been erroneously added to these tables for new databases (nullable change is the serious cause)
    for t in ( "accountsrole", "animalcontrolrole", "customreportrole" ):
        try:
            dbo.execute_dbupdate( dbo.ddl_drop_column(t, "CreatedBy") )
            dbo.execute_dbupdate( dbo.ddl_drop_column(t, "CreatedDate") )
            dbo.execute_dbupdate( dbo.ddl_drop_column(t, "LastChangedDate") )
            dbo.execute_dbupdate( dbo.ddl_drop_column(t, "LastChangedBy") )
            dbo.execute_dbupdate( dbo.ddl_drop_column(t, "RecordVersion") )
        except:
            pass

def update_34107(dbo: Database) -> None:
    # Add clinic tables
    l = dbo.locale
    fields = ",".join([
        dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
        dbo.ddl_add_table_column("AnimalID", dbo.type_integer, False),
        dbo.ddl_add_table_column("OwnerID", dbo.type_integer, False),
        dbo.ddl_add_table_column("ApptFor", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("DateTime", dbo.type_datetime, False),
        dbo.ddl_add_table_column("Status", dbo.type_integer, False),
        dbo.ddl_add_table_column("ArrivedDateTime", dbo.type_datetime, True),
        dbo.ddl_add_table_column("WithVetDateTime", dbo.type_datetime, True),
        dbo.ddl_add_table_column("CompletedDateTime", dbo.type_datetime, True),
        dbo.ddl_add_table_column("ReasonForAppointment", dbo.type_longtext, True),
        dbo.ddl_add_table_column("Comments", dbo.type_longtext, True),
        dbo.ddl_add_table_column("Amount", dbo.type_integer, False),
        dbo.ddl_add_table_column("IsVAT", dbo.type_integer, False),
        dbo.ddl_add_table_column("VATRate", dbo.type_float, False),
        dbo.ddl_add_table_column("VATAmount", dbo.type_integer, False),
        dbo.ddl_add_table_column("RecordVersion", dbo.type_integer, True),
        dbo.ddl_add_table_column("CreatedBy", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("CreatedDate", dbo.type_datetime, False),
        dbo.ddl_add_table_column("LastChangedBy", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("LastChangedDate", dbo.type_datetime, False)
    ])
    dbo.execute_dbupdate( dbo.ddl_add_table("clinicappointment", fields) )
    dbo.execute_dbupdate( dbo.ddl_add_index("clinicappointment_AnimalID", "clinicappointment", "AnimalID") )
    dbo.execute_dbupdate( dbo.ddl_add_index("clinicappointment_OwnerID", "clinicappointment", "OwnerID") )
    dbo.execute_dbupdate( dbo.ddl_add_index("clinicappointment_ApptFor", "clinicappointment", "ApptFor") )
    dbo.execute_dbupdate( dbo.ddl_add_index("clinicappointment_Status", "clinicappointment", "Status") )
    fields = ",".join([
        dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
        dbo.ddl_add_table_column("ClinicAppointmentID", dbo.type_integer, False),
        dbo.ddl_add_table_column("Description", dbo.type_longtext, False),
        dbo.ddl_add_table_column("Amount", dbo.type_integer, False),
        dbo.ddl_add_table_column("RecordVersion", dbo.type_integer, True),
        dbo.ddl_add_table_column("CreatedBy", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("CreatedDate", dbo.type_datetime, False),
        dbo.ddl_add_table_column("LastChangedBy", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("LastChangedDate", dbo.type_datetime, False)
    ])
    dbo.execute_dbupdate( dbo.ddl_add_table("clinicinvoiceitem", fields) )
    dbo.execute_dbupdate( dbo.ddl_add_index("clinicinvoiceitem_ClinicAppointmentID", "clinicinvoiceitem", "ClinicAppointmentID") )
    fields = ",".join([
        dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
        dbo.ddl_add_table_column("Status", dbo.type_shorttext, False)
    ])
    dbo.execute_dbupdate( dbo.ddl_add_table("lksclinicstatus", fields) )
    dbo.insert("lksclinicstatus", { "ID": 0, "Status": _("Scheduled", l) }, setOverrideDBLock=True, generateID=False)
    dbo.insert("lksclinicstatus", { "ID": 1, "Status": _("Invoice Only", l) }, setOverrideDBLock=True, generateID=False)
    dbo.insert("lksclinicstatus", { "ID": 2, "Status": _("Not Arrived", l) }, setOverrideDBLock=True, generateID=False)
    dbo.insert("lksclinicstatus", { "ID": 3, "Status": _("Waiting", l) }, setOverrideDBLock=True, generateID=False)
    dbo.insert("lksclinicstatus", { "ID": 4, "Status": _("With Vet", l) }, setOverrideDBLock=True, generateID=False)
    dbo.insert("lksclinicstatus", { "ID": 5, "Status": _("Complete", l) }, setOverrideDBLock=True, generateID=False)
    dbo.insert("lksclinicstatus", { "ID": 6, "Status": _("Cancelled", l) }, setOverrideDBLock=True, generateID=False)

def update_34108(dbo: Database) -> None:
    # Install new clinic_invoice template
    dbo.insert("templatedocument", {
        "ID":       dbo.get_id_max("templatedocument"), 
        "Name":     "clinic_invoice.html",
        "Path":     "/templates",
        "Content":  asm3.utils.base64encode( asm3.utils.read_text_file( dbo.installpath + "media/templates/clinic_invoice.html" ) )
    }, generateID=False)

def update_34109(dbo: Database) -> None:
    # Remove recordversion and created/lastchanged columns from ownerlookingfor - should never have been there
    # and has been erroneously added to these tables for new databases (nullable change is the serious cause)
    tables = [ "ownerlookingfor" ]
    cols = [ "CreatedBy", "CreatedDate", "LastChangedBy", "LastChangedDate", "RecordVersion" ]
    for t in tables:
        for c in cols:
            if column_exists(dbo, t, c): drop_column(dbo, t, c)

def update_34110(dbo: Database) -> None:
    # Add additionalfield.NewRecord
    add_column(dbo, "additionalfield", "NewRecord", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE additionalfield SET NewRecord = Mandatory")

def update_34111(dbo: Database) -> None:
    # Add animalvaccination.GivenBy
    add_column(dbo, "animalvaccination", "GivenBy", dbo.type_shorttext)
    add_index(dbo, "animalvaccination_GivenBy", "animalvaccination", "GivenBy")
    dbo.execute_dbupdate("UPDATE animalvaccination SET GivenBy = LastChangedBy WHERE DateOfVaccination Is Not Null")

def update_34112(dbo: Database) -> None:
    # Add a new time additional field type
    l = dbo.locale
    dbo.execute_dbupdate("INSERT INTO lksfieldtype (ID, FieldType) VALUES (10, ?)", [ _("Time", l) ])

def update_34200(dbo: Database) -> None:
    # Add audittrail.ParentLinks
    add_column(dbo, "audittrail", "ParentLinks", dbo.type_shorttext)
    add_index(dbo, "audittrail_ParentLinks", "audittrail", "ParentLinks")

def update_34201(dbo: Database) -> None:
    # Add owner.OwnerCountry, animaltransport.PickupCountry, animaltransport.DropoffCountry
    add_column(dbo, "owner", "OwnerCountry", dbo.type_shorttext)
    add_index(dbo, "owner_OwnerCountry", "owner", "OwnerCountry")
    add_column(dbo, "animaltransport", "PickupCountry", dbo.type_shorttext)
    add_column(dbo, "animaltransport", "DropoffCountry", dbo.type_shorttext)
    dbo.execute_dbupdate("UPDATE owner SET OwnerCountry=''")
    dbo.execute_dbupdate("UPDATE animaltransport SET PickupCountry='', DropoffCountry=''")

def update_34202(dbo: Database) -> None:
    # Add animaltransport.TransportReference
    add_column(dbo, "animaltransport", "TransportReference", dbo.type_shorttext)
    add_index(dbo, "animaltransport_TransportReference", "animaltransport", "TransportReference")
    dbo.execute_dbupdate("UPDATE animaltransport SET TransportReference=''")

def update_34203(dbo: Database) -> None:
    # Add donationtype.IsVAT
    add_column(dbo, "donationtype", "IsVAT", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE donationtype SET IsVAT = 0")

def update_34204(dbo: Database) -> None:
    # Add ownerdonation.Fee
    add_column(dbo, "ownerdonation", "Fee", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE ownerdonation SET Fee = 0")

def update_34300(dbo: Database) -> None:
    # Add animal.ExtraIDs
    add_column(dbo, "animal", "ExtraIDs", dbo.type_shorttext)
    add_index(dbo, "animal_ExtraIDs", "animal", "ExtraIDs")
    dbo.execute_dbupdate("UPDATE animal SET ExtraIDs = ''")

def update_34301(dbo: Database) -> None:
    # Add onlineformfield.SpeciesID
    add_column(dbo, "onlineformfield", "SpeciesID", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE onlineformfield SET SpeciesID = -1")

def update_34302(dbo: Database) -> None:
    # Add lksynunk
    l = dbo.locale
    sql = "CREATE TABLE lksynunk ( ID INTEGER NOT NULL PRIMARY KEY, " \
        "Name %(short)s NOT NULL)" % { "short": dbo.type_shorttext }
    dbo.execute_dbupdate(sql)
    dbo.execute_dbupdate("INSERT INTO lksynunk VALUES (0, ?)", [ _("Yes", l) ])
    dbo.execute_dbupdate("INSERT INTO lksynunk VALUES (1, ?)", [ _("No", l) ])
    dbo.execute_dbupdate("INSERT INTO lksynunk VALUES (2, ?)", [ _("Unknown", l) ])
    dbo.execute_dbupdate("INSERT INTO lksynunk VALUES (5, ?)", [ _("Over 5", l) ])
    dbo.execute_dbupdate("INSERT INTO lksynunk VALUES (12, ?)", [ _("Over 12", l) ])

def update_34303(dbo: Database) -> None:
    # Add lkstransportstatus
    l = dbo.locale
    sql = "CREATE TABLE lkstransportstatus ( ID INTEGER NOT NULL PRIMARY KEY, " \
        "Name %(short)s NOT NULL)" % { "short": dbo.type_shorttext }
    dbo.execute_dbupdate(sql)
    dbo.execute_dbupdate("INSERT INTO lkstransportstatus VALUES (1, ?)", [ _("New", l) ])
    dbo.execute_dbupdate("INSERT INTO lkstransportstatus VALUES (2, ?)", [ _("Confirmed", l) ])
    dbo.execute_dbupdate("INSERT INTO lkstransportstatus VALUES (3, ?)", [ _("Hold", l) ])
    dbo.execute_dbupdate("INSERT INTO lkstransportstatus VALUES (4, ?)", [ _("Scheduled", l) ])
    dbo.execute_dbupdate("INSERT INTO lkstransportstatus VALUES (10, ?)", [ _("Cancelled", l) ])
    dbo.execute_dbupdate("INSERT INTO lkstransportstatus VALUES (11, ?)", [ _("Completed", l) ])

def update_34304(dbo: Database) -> None:
    # Add new ownervoucher columns
    add_column(dbo, "ownervoucher", "AnimalID", dbo.type_integer)
    add_column(dbo, "ownervoucher", "DatePresented", dbo.type_datetime)
    add_column(dbo, "ownervoucher", "VoucherCode", dbo.type_shorttext)
    add_index(dbo, "ownervoucher_AnimalID", "ownervoucher", "AnimalID")
    add_index(dbo, "ownervoucher_DatePresented", "ownervoucher", "DatePresented")
    add_index(dbo, "ownervoucher_VoucherCode", "ownervoucher", "VoucherCode")
    # Set the default vouchercode to ID padded to 6 digits
    dbo.execute_dbupdate("UPDATE ownervoucher SET VoucherCode = %s" % dbo.sql_zero_pad_left("ID", 6))

def update_34305(dbo: Database) -> None:
    # Add vaccinationtype.RescheduleDays
    add_column(dbo, "vaccinationtype", "RescheduleDays", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE vaccinationtype SET RescheduleDays = 0 WHERE RescheduleDays Is Null")
    # Add animallost.MicrochipNumber and animalfound.MicrochipNumber
    add_column(dbo, "animallost", "MicrochipNumber", dbo.type_shorttext)
    add_column(dbo, "animalfound", "MicrochipNumber", dbo.type_shorttext)
    add_index(dbo, "animallost_MicrochipNumber", "animallost", "MicrochipNumber")
    add_index(dbo, "animalfound_MicrochipNumber", "animalfound", "MicrochipNumber")
    # Add animallostfoundmatch.LostMicrochipNumber/FoundMicrochipNumber
    add_column(dbo, "animallostfoundmatch", "LostMicrochipNumber", dbo.type_shorttext)
    add_column(dbo, "animallostfoundmatch", "FoundMicrochipNumber", dbo.type_shorttext)

def update_34306(dbo: Database) -> None:
    # Add owner.IsAdopter flag
    add_column(dbo, "owner", "IsAdopter", dbo.type_integer)
    add_index(dbo, "owner_IsAdopter", "owner", "IsAdopter")
    dbo.execute_dbupdate("UPDATE owner SET IsAdopter = (SELECT COUNT(*) FROM adoption WHERE OwnerID = owner.ID AND MovementType=1 AND MovementDate Is Not Null AND ReturnDate Is Null)")
    dbo.execute_dbupdate("UPDATE owner SET IsAdopter = 1 WHERE IsAdopter > 0")

def update_34400(dbo: Database) -> None:
    # Add new lksdonationfreq for fortnightly with ID 2
    # This requires renumbering the existing frequencies up one as there was no spare slot
    if dbo.query_int("SELECT MAX(ID) FROM lksdonationfreq") == 6: return # We already did this
    l = dbo.locale
    dbo.execute_dbupdate("UPDATE lksdonationfreq SET ID=6 WHERE ID=5")
    dbo.execute_dbupdate("UPDATE lksdonationfreq SET ID=5 WHERE ID=4")
    dbo.execute_dbupdate("UPDATE lksdonationfreq SET ID=4 WHERE ID=3")
    dbo.execute_dbupdate("UPDATE lksdonationfreq SET ID=3 WHERE ID=2")
    dbo.execute_dbupdate("UPDATE ownerdonation SET Frequency=Frequency+1 WHERE Frequency IN (2,3,4,5)")
    dbo.execute_dbupdate("INSERT INTO lksdonationfreq (ID, Frequency) VALUES (2, ?)", [ _("Fortnightly", l) ])

def update_34401(dbo: Database) -> None:
    # Add ownerdonation.PaymentProcessorData
    add_column(dbo, "ownerdonation", "PaymentProcessorData", dbo.type_longtext)

def update_34402(dbo: Database) -> None:
    # Add media.CreatedDate
    add_column(dbo, "media", "CreatedDate", dbo.type_datetime)
    add_index(dbo, "media_CreatedDate", "media", "CreatedDate")
    dbo.execute_dbupdate("UPDATE media SET CreatedDate=Date")

def update_34403(dbo: Database) -> None:
    # Add onlineformfield.VisibleIf
    add_column(dbo, "onlineformfield", "VisibleIf", dbo.type_shorttext)
    dbo.execute_dbupdate("UPDATE onlineformfield SET VisibleIf=''")

def update_34404(dbo: Database) -> None:
    # Add animal.OwnerID
    add_column(dbo, "animal", "OwnerID", dbo.type_integer)
    add_index(dbo, "animal_OwnerID", "animal", "OwnerID")
    # Set currentownerid for non-shelter animals
    dbo.execute_dbupdate("UPDATE animal SET OwnerID = OriginalOwnerID WHERE NonShelterAnimal=1")
    # Set currentownerid for animals with an active exit movement
    dbo.execute_dbupdate("UPDATE animal SET OwnerID = " \
        "(SELECT OwnerID FROM adoption WHERE ID = animal.ActiveMovementID) " \
        "WHERE Archived = 1 AND ActiveMovementType IN (1, 3, 5)")
    # Remove nulls
    dbo.execute_dbupdate("UPDATE animal SET OwnerID = 0 WHERE OwnerID Is Null")

def update_34405(dbo: Database) -> None:
    # Correct payment amounts to gross where sales tax exists.
    # This query only updates the amount if the tax value matches
    # an exclusive of tax calculation.
    # Eg: amount = 100, vat = 6, rate = 6 - will update amount to 106 because 100 * 0.06 == 6.0
    #     amount = 106, vat = 6, rate = 6 - will not update as 106 * 0.06 == 6.35
    dbo.execute_dbupdate("UPDATE ownerdonation SET donation = donation + vatamount, " \
        "LastChangedBy = %s " \
        "WHERE isvat = 1 and vatamount > 0 and vatrate > 0 and vatamount = ((donation / 100.0) * vatrate)" % 
        dbo.sql_concat(["LastChangedBy", "'+dbupdate34405'"]))

def update_34406(dbo: Database) -> None:
    # Remove bloated items from the config table that now live in the disk cache
    dbo.execute_dbupdate("DELETE FROM configuration WHERE ItemName IN " \
        "('ASMNews', 'LookingForReport', 'LookingForLastMatchCount', 'LostFoundReport', 'LostFoundLastMatchCount')")

def update_34407(dbo: Database) -> None:
    # Add animal.JurisdictionID
    add_column(dbo, "animal", "JurisdictionID", dbo.type_integer)
    add_index(dbo, "animal_JurisdictionID", "animal", "JurisdictionID")
    # Set it on existing animals based on original owner, then brought in by jurisdiction
    dbo.execute_dbupdate("UPDATE animal SET JurisdictionID = " \
        "(SELECT JurisdictionID FROM owner WHERE ID = animal.OriginalOwnerID) WHERE JurisdictionID Is Null")
    dbo.execute_dbupdate("UPDATE animal SET JurisdictionID = " \
        "(SELECT JurisdictionID FROM owner WHERE ID = animal.BroughtInByOwnerID) WHERE JurisdictionID Is Null")
    dbo.execute_dbupdate("UPDATE animal SET JurisdictionID = 0 WHERE JurisdictionID Is Null")

def update_34408(dbo: Database) -> None:
    # Add TNR movement type
    l = dbo.locale
    dbo.execute_dbupdate("INSERT INTO lksmovementtype (ID, MovementType) VALUES (13, ?)", [ _("TNR", l) ])

def update_34409(dbo: Database) -> None:
    # Add animalvaccination.RabiesTag
    add_column(dbo, "animalvaccination", "RabiesTag", dbo.type_shorttext)
    add_index(dbo, "animalvaccination_RabiesTag", "animalvaccination", "RabiesTag")
    dbo.execute_dbupdate("UPDATE animalvaccination SET RabiesTag='' WHERE RabiesTag Is Null")

def update_34410(dbo: Database) -> None:
    # Add owner.ExtraIDs
    add_column(dbo, "owner", "ExtraIDs", dbo.type_shorttext)
    add_index(dbo, "owner_ExtraIDs", "owner", "ExtraIDs")
    dbo.execute_dbupdate("UPDATE owner SET ExtraIDs = ''")

def update_34411(dbo: Database) -> None:
    # Add animal.PopupWarning
    add_column(dbo, "animal", "PopupWarning", dbo.type_longtext)
    dbo.execute_dbupdate("UPDATE animal SET PopupWarning = ''")

def update_34500(dbo: Database) -> None:
    # Add testtype.RescheduleDays
    add_column(dbo, "testtype", "RescheduleDays", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE testtype SET RescheduleDays = 0 WHERE RescheduleDays Is Null")

def update_34501(dbo: Database) -> None:
    # Add animal.Adoptable
    add_column(dbo, "animal", "Adoptable", dbo.type_integer)
    add_index(dbo, "animal_Adoptable", "animal", "Adoptable")
    dbo.execute_dbupdate("UPDATE animal SET Adoptable = 0")
    # Add onlineform.EmailCoordinator
    add_column(dbo, "onlineform", "EmailCoordinator", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE onlineform SET EmailCoordinator = 0")

def update_34502(dbo: Database) -> None:
    # Replace HTML entities in the database with unicode code points now
    # that they are no longer needed.
    if dbo.locale not in ( "en", "en_GB", "en_AU" ):
        replace_html_entities(dbo)

def update_34503(dbo: Database) -> None:
    # add lkworktype.IsRetired
    add_column(dbo, "lkworktype", "IsRetired", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE lkworktype SET IsRetired = 0")

def update_34504(dbo: Database) -> None:
    # add onlineform.AutoProcess
    add_column(dbo, "onlineform", "AutoProcess", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE onlineform SET AutoProcess=0")

def update_34505(dbo: Database) -> None:
    # add extra row for Selective to good with
    l = dbo.locale
    dbo.execute_dbupdate("INSERT INTO lksynun VALUES (3, ?)", [ _("Selective", l) ])

def update_34506(dbo: Database) -> None:
    # add customreport.Revision
    add_column(dbo, "customreport", "Revision", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE customreport SET Revision=0")

def update_34507(dbo: Database) -> None:
    # add costtype.AccountID, donationtype.AccountID
    add_column(dbo, "costtype", "AccountID", dbo.type_integer)
    add_column(dbo, "donationtype", "AccountID", dbo.type_integer)
    # Copy the values from the redundant columns in accounts
    for a in dbo.query("SELECT ID, CostTypeID, DonationTypeID FROM accounts"):
        if a.COSTTYPEID is not None and a.COSTTYPEID > 0:
            dbo.execute_dbupdate("UPDATE costtype SET AccountID=? WHERE ID=?", (a.ID, a.COSTTYPEID))
        if a.DONATIONTYPEID is not None and a.DONATIONTYPEID > 0:
            dbo.execute_dbupdate("UPDATE donationtype SET AccountID=? WHERE ID=?", (a.ID, a.DONATIONTYPEID))

def update_34508(dbo: Database) -> None:
    # Replace old JQUI themes with light or dark
    dbo.execute_dbupdate("UPDATE users SET ThemeOverride='asm' WHERE ThemeOverride IN ('base','cupertino'," \
        "'dot-luv','excite-bike','flick','hot-sneaks','humanity','le-frog','overcast','pepper-grinder','redmond'," \
        "'smoothness','south-street','start','sunny','swanky-purse','ui-lightness')")
    dbo.execute_dbupdate("UPDATE users SET ThemeOverride='asm-dark' WHERE ThemeOverride IN ('black-tie','blitzer'," \
        "'dark-hive','eggplant','mint-choc','trontastic','ui-darkness','vader')")

def update_34509(dbo: Database) -> None:
    # This update broke MYSQL because Show is a reserved word. 
    # it is superceded by update_34511
    # add_column(dbo, "templatedocument", "Show", dbo.type_shorttext)
    # dbo.execute_dbupdate("UPDATE templatedocument SET Show='everywhere'")
    pass

def update_34510(dbo: Database) -> None:
    add_column(dbo, "onlineform", "RetainFor", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE onlineform SET RetainFor=0")

def update_34511(dbo: Database) -> None:
    add_column(dbo, "templatedocument", "ShowAt", dbo.type_shorttext)
    dbo.execute_dbupdate("UPDATE templatedocument SET ShowAt='everywhere'")

def update_34512(dbo: Database) -> None:
    add_column(dbo, "owner", "PopupWarning", dbo.type_longtext)
    add_column(dbo, "owner", "IsDangerous", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE owner SET PopupWarning = '', IsDangerous = 0")

def update_34600(dbo: Database) -> None:
    # Remove the old ASM2 report definitions as they break versioning on them if present
    dbo.execute_dbupdate("DELETE FROM customreport WHERE SQLCommand LIKE '0%'")

def update_34601(dbo: Database) -> None:
    # Add cost per treatment fields
    add_column(dbo, "animalmedical", "CostPerTreatment", dbo.type_integer)
    add_column(dbo, "medicalprofile", "CostPerTreatment", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE animalmedical SET CostPerTreatment=0")
    dbo.execute_dbupdate("UPDATE medicalprofile SET CostPerTreatment=0")

def update_34602(dbo: Database) -> None:
    # Add time fieldtype - this seems to be a duplicate of update_34112 ?
    #l = dbo.locale
    #dbo.execute_dbupdate("INSERT INTO lksfieldtype (ID, FieldType) VALUES (10, ?)", [ _("Time", l) ])
    pass

def update_34603(dbo: Database) -> None:
    l = dbo.locale
    # create event tables
    dbo.execute_dbupdate("CREATE TABLE event (ID %(int)s NOT NULL PRIMARY KEY, StartDateTime %(date)s, EndDateTime %(date)s, " \
                       "EventName %(short)s NOT NULL, EventDescription %(long)s NOT NULL," \
                       "RecordVersion %(int)s, CreatedBy %(short)s, CreatedDate %(date)s, LastChangedBy %(short)s, LastChangedDate %(date)s)" \
                        % { "int": dbo.type_integer, "date": dbo.type_datetime, "short": dbo.type_shorttext, "long": dbo.type_longtext })
    dbo.execute_dbupdate("CREATE TABLE eventanimal (ID %(int)s NOT NULL PRIMARY KEY, EventID %(int)s NOT NULL, AnimalID %(int)s NOT NULL, "\
                       "ArrivalDate %(date)s, " \
                       "RecordVersion %(int)s, CreatedBy %(short)s, CreatedDate %(date)s, LastChangedBy %(short)s, LastChangedDate %(date)s)" \
                        % { "int": dbo.type_integer, "date": dbo.type_datetime, "short": dbo.type_shorttext })
    add_index(dbo, "event_StartDateTime", "event", "StartDateTime")
    add_index(dbo, "event_EndDateTime", "event", "EndDateTime")
    add_index(dbo, "event_EventName", "event", "EventName")
    add_index(dbo, "eventanimal_EventAnimalID", "eventanimal", "EventID,AnimalID", True)
    add_index(dbo, "eventanimal_ArrivalDate", "eventanimal", "ArrivalDate")
    # add events to the additional field links
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (21, '%s')" % _("Event - Details", l))

def update_34604(dbo: Database) -> None:
    # add eventid column to movements
    add_column(dbo, "adoption", "EventID", dbo.type_integer)
    add_index(dbo, "adoption_EventID", "adoption", "EventID")

def update_34605(dbo: Database) -> None:
    l = dbo.locale
    # add sponsor flag column, and sponsor/vet as additional field types
    add_column(dbo, "owner", "IsSponsor", dbo.type_integer)
    add_index(dbo, "owner_IsSponsor", "owner", "IsSponsor")
    dbo.execute_dbupdate("UPDATE owner SET IsSponsor=0")
    dbo.execute_dbupdate("INSERT INTO lksfieldtype (ID, FieldType) VALUES (11, '" + _("Sponsor", l) + "')")
    dbo.execute_dbupdate("INSERT INTO lksfieldtype (ID, FieldType) VALUES (12, '" + _("Vet", l) + "')")

def update_34606(dbo: Database) -> None:
    # add location columns to event table
    add_column(dbo, "event", "EventOwnerID", dbo.type_integer)
    add_column(dbo, "event", "EventAddress", dbo.type_shorttext)
    add_column(dbo, "event", "EventTown", dbo.type_shorttext)
    add_column(dbo, "event", "EventCounty", dbo.type_shorttext)
    add_column(dbo, "event", "EventPostCode", dbo.type_shorttext)
    add_column(dbo, "event", "EventCountry", dbo.type_shorttext)
    add_index(dbo, "event_EventOwnerID", "event", "EventOwnerID")
    add_index(dbo, "event_EventAddress", "event", "EventAddress")

def update_34607(dbo: Database) -> None:
    # add 2FA columns to users table
    add_column(dbo, "users", "EnableTOTP", dbo.type_integer)
    add_column(dbo, "users", "OTPSecret", dbo.type_shorttext)
    dbo.execute_dbupdate("UPDATE users SET EnableTOTP=0, OTPSecret=''")

def update_34608(dbo: Database) -> None:
    # change column eventownerid to nullable
    dbo.execute_dbupdate(dbo.ddl_drop_notnull("event", "EventOwnerID", dbo.type_integer))

def update_34609(dbo: Database) -> None:
    # add animalentry table
    fields = ",".join([
        dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
        dbo.ddl_add_table_column("AnimalID", dbo.type_integer, False),
        dbo.ddl_add_table_column("ShelterCode", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("ShortCode", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("EntryDate", dbo.type_datetime, False),
        dbo.ddl_add_table_column("EntryReasonID", dbo.type_integer, False),
        dbo.ddl_add_table_column("AdoptionCoordinatorID", dbo.type_integer, True),
        dbo.ddl_add_table_column("BroughtInByOwnerID", dbo.type_integer, True),
        dbo.ddl_add_table_column("OriginalOwnerID", dbo.type_integer, True),
        dbo.ddl_add_table_column("AsilomarIntakeCategory", dbo.type_integer, True),
        dbo.ddl_add_table_column("JurisdictionID", dbo.type_integer, True),
        dbo.ddl_add_table_column("IsTransfer", dbo.type_integer, False),
        dbo.ddl_add_table_column("AsilomarIsTransferExternal", dbo.type_integer, True),
        dbo.ddl_add_table_column("HoldUntilDate", dbo.type_datetime, True),
        dbo.ddl_add_table_column("IsPickup", dbo.type_integer, False),
        dbo.ddl_add_table_column("PickupLocationID", dbo.type_integer, True),
        dbo.ddl_add_table_column("PickupAddress", dbo.type_shorttext, True),
        dbo.ddl_add_table_column("ReasonNO", dbo.type_longtext, True),
        dbo.ddl_add_table_column("ReasonForEntry", dbo.type_longtext, True),
        dbo.ddl_add_table_column("RecordVersion", dbo.type_integer, False),
        dbo.ddl_add_table_column("CreatedBy", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("CreatedDate", dbo.type_datetime, False),
        dbo.ddl_add_table_column("LastChangedBy", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("LastChangedDate", dbo.type_datetime, False)
    ])
    dbo.execute_dbupdate( dbo.ddl_add_table("animalentry", fields) )
    dbo.execute_dbupdate( dbo.ddl_add_index("animalentry_AnimalID", "animalentry", "AnimalID") )

def update_34611(dbo: Database) -> None:
    # add eventanimal.Comments
    add_column(dbo, "eventanimal", "Comments", dbo.type_longtext)
    dbo.execute_dbupdate(dbo.ddl_drop_notnull("eventanimal", "ArrivalDate", dbo.type_datetime))

def update_34700(dbo: Database) -> None:
    # add outcome table (mainly for string translations, used by v_animal view)
    l = dbo.locale
    fields = ",".join([
        dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
        dbo.ddl_add_table_column("Outcome", dbo.type_shorttext, False)
    ])
    dbo.execute_dbupdate( dbo.ddl_add_table("lksoutcome", fields) )
    dbo.execute_dbupdate("INSERT INTO lksoutcome VALUES (1, ?)", [ _("On Shelter", l) ])
    dbo.execute_dbupdate("INSERT INTO lksoutcome VALUES (2, ?)", [ _("Died", l) ])
    dbo.execute_dbupdate("INSERT INTO lksoutcome VALUES (3, ?)", [ _("DOA", l) ])
    dbo.execute_dbupdate("INSERT INTO lksoutcome VALUES (4, ?)", [ _("Euthanized", l) ])
    dbo.execute_dbupdate("INSERT INTO lksoutcome VALUES (11, ?)", [ _("Adopted", l) ])
    dbo.execute_dbupdate("INSERT INTO lksoutcome VALUES (12, ?)", [ _("Fostered", l) ])
    dbo.execute_dbupdate("INSERT INTO lksoutcome VALUES (13, ?)", [ _("Transferred", l) ])
    dbo.execute_dbupdate("INSERT INTO lksoutcome VALUES (14, ?)", [ _("Escaped", l) ])
    dbo.execute_dbupdate("INSERT INTO lksoutcome VALUES (15, ?)", [ _("Reclaimed", l) ])
    dbo.execute_dbupdate("INSERT INTO lksoutcome VALUES (16, ?)", [ _("Stolen", l) ])
    dbo.execute_dbupdate("INSERT INTO lksoutcome VALUES (17, ?)", [ _("Released to Wild", l) ])
    dbo.execute_dbupdate("INSERT INTO lksoutcome VALUES (18, ?)", [ _("Retailer", l) ])
    dbo.execute_dbupdate("INSERT INTO lksoutcome VALUES (19, ?)", [ _("TNR", l) ])

def update_34701(dbo: Database) -> None:
    # add second contact fields to owner table
    add_column(dbo, "owner", "OwnerTitle2", dbo.type_shorttext)
    add_column(dbo, "owner", "OwnerInitials2", dbo.type_shorttext)
    add_column(dbo, "owner", "OwnerForeNames2", dbo.type_shorttext)
    add_column(dbo, "owner", "OwnerSurname2", dbo.type_shorttext)
    add_column(dbo, "owner", "WorkTelephone2", dbo.type_shorttext)
    add_column(dbo, "owner", "MobileTelephone2", dbo.type_shorttext)
    add_column(dbo, "owner", "EmailAddress2", dbo.type_shorttext)
    add_index(dbo, "owner_OwnerTitle2", "owner", "OwnerTitle2")
    add_index(dbo, "owner_OwnerInitials2", "owner", "OwnerInitials2")
    add_index(dbo, "owner_OwnerForeNames2", "owner", "OwnerForeNames2")
    add_index(dbo, "owner_OwnerSurname2", "owner", "OwnerSurname2")
    add_index(dbo, "owner_WorkTelephone2", "owner", "WorkTelephone2")
    add_index(dbo, "owner_MobileTelephone2", "owner", "MobileTelephone2")
    add_index(dbo, "owner_EmailAddress2", "owner", "EmailAddress2")
    dbo.execute_dbupdate("UPDATE owner SET OwnerTitle2='', OwnerInitials2='', OwnerForeNames2='', OwnerSurname2='', WorkTelephone2='', MobileTelephone2='', EmailAddress2=''")

def update_34702(dbo: Database) -> None:
    add_column(dbo, "owner", "DateOfBirth", dbo.type_datetime)
    add_column(dbo, "owner", "DateOfBirth2", dbo.type_datetime)
    add_column(dbo, "owner", "IdentificationNumber", dbo.type_shorttext)
    add_column(dbo, "owner", "IdentificationNumber2", dbo.type_shorttext)
    add_column(dbo, "owner", "MatchFlags", dbo.type_shorttext)
    add_index(dbo, "owner_IdentificationNumber", "owner", "IdentificationNumber")
    add_index(dbo, "owner_IdentificationNumber2", "owner", "IdentificationNumber2")
    dbo.execute_dbupdate("UPDATE owner SET IdentificationNumber='', IdentificationNumber2='', MatchFlags='' ")

def update_34703(dbo: Database) -> None:
    # NOTE: This doesn't seem to do anything that 34702 didn't and must have been added for a short term fix
    #add_index(dbo, "owner_IdentificationNumber", "owner", "IdentificationNumber")
    #add_index(dbo, "owner_IdentificationNumber2", "owner", "IdentificationNumber2")
    #dbo.execute_dbupdate("UPDATE owner SET IdentificationNumber='' WHERE IdentificationNumber Is Null") 
    #dbo.execute_dbupdate("UPDATE owner SET IdentificationNumber2='' WHERE IdentificationNumber2 Is Null") 
    #dbo.execute_dbupdate("UPDATE owner SET MatchFlags='' WHERE MatchFlags Is Null") 
    pass

def update_34704(dbo: Database) -> None:
    fields = ",".join([
        dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
        dbo.ddl_add_table_column("AnimalID", dbo.type_integer, False),
        dbo.ddl_add_table_column("OwnerID", dbo.type_integer, True),
        dbo.ddl_add_table_column("InDateTime", dbo.type_datetime, False),
        dbo.ddl_add_table_column("OutDateTime", dbo.type_datetime, False),
        dbo.ddl_add_table_column("Days", dbo.type_integer, True),
        dbo.ddl_add_table_column("DailyFee", dbo.type_integer, True),
        dbo.ddl_add_table_column("ShelterLocation", dbo.type_integer, False),
        dbo.ddl_add_table_column("ShelterLocationUnit", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("Comments", dbo.type_longtext, True),
        dbo.ddl_add_table_column("RecordVersion", dbo.type_integer, False),
        dbo.ddl_add_table_column("CreatedBy", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("CreatedDate", dbo.type_datetime, False),
        dbo.ddl_add_table_column("LastChangedBy", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("LastChangedDate", dbo.type_datetime, False)
    ])
    dbo.execute_dbupdate( dbo.ddl_add_table("animalboarding", fields) )
    dbo.execute_dbupdate( dbo.ddl_add_index("animalboarding_AnimalID", "animalboarding", "AnimalID") )
    dbo.execute_dbupdate( dbo.ddl_add_index("animalboarding_OwnerID", "animalboarding", "OwnerID") )
    dbo.execute_dbupdate( dbo.ddl_add_index("animalboarding_InDateTime", "animalboarding", "InDateTime") )
    dbo.execute_dbupdate( dbo.ddl_add_index("animalboarding_OutDateTime", "animalboarding", "OutDateTime") )

def update_34705(dbo: Database) -> None:
    # add movement type to additional fields
    l = dbo.locale
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (22, '%s')" % _("Movement - Adoption", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (23, '%s')" % _("Movement - Foster", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (24, '%s')" % _("Movement - Transfer", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (25, '%s')" % _("Movement - Escaped", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (26, '%s')" % _("Movement - Reclaimed", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (27, '%s')" % _("Movement - Stolen", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (28, '%s')" % _("Movement - Released", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (29, '%s')" % _("Movement - Retailer", l))
    dbo.execute_dbupdate("INSERT INTO lksfieldlink VALUES (30, '%s')" % _("Movement - Reservation", l))

def update_34706(dbo: Database) -> None:
    # Add animalboarding.BoardingTypeID and table
    l = dbo.locale
    add_column(dbo, "animalboarding", "BoardingTypeID", dbo.type_integer)
    add_index(dbo, "animalboarding_BoardingTypeID", "animalboarding", "BoardingTypeID")
    fields = ",".join([
        dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
        dbo.ddl_add_table_column("BoardingName", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("BoardingDescription", dbo.type_shorttext, True),
        dbo.ddl_add_table_column("DefaultCost", dbo.type_integer, True),
        dbo.ddl_add_table_column("IsRetired", dbo.type_integer, True)
    ])
    dbo.execute_dbupdate( dbo.ddl_add_table("lkboardingtype", fields) )
    dbo.execute_dbupdate("INSERT INTO lkboardingtype VALUES (1, ?, '', 0, 0)", [ _("Boarding", l) ])

def update_34707(dbo: Database) -> None:
    # Add the new animalviewcarousel and slideshow HTML templates
    install_html_template(dbo, "animalviewcarousel", use_max_id = True)
    install_html_template(dbo, "slideshow", use_max_id = True)

def update_34708(dbo: Database) -> None:
    # Add onlineform.EmailFosterer
    add_column(dbo, "onlineform", "EmailFosterer", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE onlineform SET EmailFosterer = 0")

def update_34709(dbo: Database) -> None:
    # Add stocklevel.Low
    add_column(dbo, "stocklevel", "Low", dbo.type_float)
    dbo.execute_dbupdate("UPDATE stocklevel SET Low=0")
    # Add additionalfield.Hidden
    add_column(dbo, "additionalfield", "Hidden", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE additionalfield SET Hidden=0")

def update_34800(dbo: Database) -> None:
    # Add ownerlicence.Token and ownerlicence.Renewed
    add_column(dbo, "ownerlicence", "Token", dbo.type_shorttext)
    add_column(dbo, "ownerlicence", "Renewed", dbo.type_integer)
    add_index(dbo, "ownerlicence_Token", "ownerlicence", "Token") 
    add_index(dbo, "ownerlicence_Renewed", "ownerlicence", "Renewed")
    add_column(dbo, "licencetype", "RescheduleDays", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE licencetype SET RescheduleDays=365")
    dbo.execute_dbupdate("UPDATE ownerlicence SET Renewed = 0")
    dbo.execute_dbupdate("UPDATE ownerlicence SET Renewed = 1 " \
        "WHERE EXISTS(SELECT oli.ID FROM ownerlicence oli WHERE oli.LicenceTypeID = ownerlicence.LicenceTypeID "
        "AND oli.OwnerID = ownerlicence.OwnerID AND oli.AnimalID = ownerlicence.AnimalID AND oli.IssueDate > ownerlicence.IssueDate)")
    # Use MD5 hashes of the ID for old tokens for speed (we use UUIDs for new ones)
    dbo.execute_dbupdate("UPDATE ownerlicence SET Token = %s" % (dbo.sql_md5("ID")))

def update_34801(dbo: Database) -> None:
    l = dbo.locale
    # Add animal.EntryTypeID and lksentrytype
    add_column(dbo, "animal", "EntryTypeID", dbo.type_integer)
    add_index(dbo, "animal_EntryTypeID", "animal", "EntryTypeID")
    add_column(dbo, "animalentry", "EntryTypeID", dbo.type_integer)
    fields = ",".join([
        dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
        dbo.ddl_add_table_column("EntryTypeName", dbo.type_shorttext, False),
    ])
    dbo.execute_dbupdate( dbo.ddl_add_table("lksentrytype", fields) )
    dbo.execute_dbupdate("INSERT INTO lksentrytype VALUES (1, ?)", [ _("Surrender", l) ])
    dbo.execute_dbupdate("INSERT INTO lksentrytype VALUES (2, ?)", [ _("Stray", l) ])
    dbo.execute_dbupdate("INSERT INTO lksentrytype VALUES (3, ?)", [ _("Transfer In", l) ])
    dbo.execute_dbupdate("INSERT INTO lksentrytype VALUES (4, ?)", [ _("TNR", l) ])
    dbo.execute_dbupdate("INSERT INTO lksentrytype VALUES (5, ?)", [ _("Born in care", l) ])
    dbo.execute_dbupdate("INSERT INTO lksentrytype VALUES (6, ?)", [ _("Wildlife", l) ])
    dbo.execute_dbupdate("INSERT INTO lksentrytype VALUES (7, ?)", [ _("Seized", l) ])
    dbo.execute_dbupdate("INSERT INTO lksentrytype VALUES (8, ?)", [ _("Abandoned", l) ])
    # Set the default value for animal.EntryTypeID based on existing data
    strayid = dbo.query_int("SELECT ID FROM entryreason WHERE LOWER(ReasonName) LIKE '%stray%'")
    tnrid = dbo.query_int("SELECT ID FROM entryreason WHERE LOWER(ReasonName) LIKE '%tnr%'")
    dbo.execute_dbupdate("UPDATE animal SET EntryTypeID = 0")
    dbo.execute_dbupdate("UPDATE animalentry SET EntryTypeID = 0")
    dbo.execute_dbupdate("UPDATE animal SET EntryTypeID=3 WHERE IsTransfer=1")
    dbo.execute_dbupdate("UPDATE animal SET EntryTypeID=7 WHERE CrueltyCase=1")
    if strayid > 0: dbo.execute_dbupdate("UPDATE animal SET EntryTypeID=2 WHERE EntryReasonID=%s AND NonShelterAnimal=0 AND EntryTypeID=0" % strayid)
    if tnrid > 0: dbo.execute_dbupdate("UPDATE animal SET EntryTypeID=4 WHERE EntryReasonID=%s AND NonShelterAnimal=0 AND EntryTypeID=0" % tnrid)
    dbo.execute_dbupdate("UPDATE animal SET EntryTypeID=5 WHERE DateBroughtIn=DateOfBirth AND NonShelterAnimal=0 AND EntryTypeID=0")
    dbo.execute_dbupdate("UPDATE animal SET EntryTypeID=1 WHERE NonShelterAnimal=0 AND EntryTypeID=0")

def update_34802(dbo: Database) -> None:
    # Switching to use primarykey/cache combo for receipt numbers and online forms, and
    # possibly for future PK depending on performance. Clear any old junk out.
    dbo.execute_dbupdate("DELETE FROM primarykey")

def update_34803(dbo: Database) -> None:
    # Add animallocation table
    fields = ",".join([
        dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
        dbo.ddl_add_table_column("AnimalID", dbo.type_integer, False),
        dbo.ddl_add_table_column("Date", dbo.type_datetime, False),
        dbo.ddl_add_table_column("FromLocationID", dbo.type_integer, False),
        dbo.ddl_add_table_column("FromUnit", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("ToLocationID", dbo.type_integer, False),
        dbo.ddl_add_table_column("ToUnit", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("MovedBy", dbo.type_shorttext, False), # 2024-08-01 changed By to MovedBy as it breaks the update path for MySQL
        dbo.ddl_add_table_column("Description", dbo.type_shorttext, False)
    ])
    dbo.execute_dbupdate( dbo.ddl_add_table("animallocation", fields) )
    add_index(dbo, "animallocation_AnimalID", "animallocation", "AnimalID") 
    add_index(dbo, "animallocation_FromLocationID", "animallocation", "FromLocationID") 
    add_index(dbo, "animallocation_ToLocationID", "animallocation", "ToLocationID") 

def update_34804(dbo: Database) -> None:
    l = dbo.locale
    # add adoption coordinator as additional field types
    dbo.execute_dbupdate("INSERT INTO lksfieldtype (ID, FieldType) VALUES (13, '" + _("Adoption Coordinator", l) + "')")

def update_34805(dbo: Database) -> None:
    l = dbo.locale
    # add DOA entry type
    dbo.execute_dbupdate("INSERT INTO lksentrytype (ID, EntryTypeName) VALUES (9, '" + _("Dead on arrival", l) + "')")

def update_34806(dbo: Database) -> None:
    # Add IncidentCode column
    add_column(dbo, "animalcontrol", "IncidentCode", dbo.type_shorttext)
    add_index(dbo, "animalcontrol_IncidentCode", "animalcontrol", "IncidentCode")
    batch = []
    for r in dbo.query("SELECT ID FROM animalcontrol"):
        batch.append([ asm3.utils.padleft(r.ID, 6), r.ID ])
    dbo.execute_many("UPDATE animalcontrol SET IncidentCode = ? WHERE ID = ?", batch, override_lock=True) 

def update_34807(dbo: Database) -> None:
    # Add IsRetired to animal and person flags
    add_column(dbo, "lkanimalflags", "IsRetired", dbo.type_integer)
    add_column(dbo, "lkownerflags", "IsRetired", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE lkanimalflags SET IsRetired=0")
    dbo.execute_dbupdate("UPDATE lkownerflags SET IsRetired=0")

def update_34808(dbo: Database) -> None:
    l = dbo.locale
    # Add clinictype table and field to clinicappointment
    add_column(dbo, "clinicappointment", "ClinicTypeID", dbo.type_integer)
    add_index(dbo, "clinicappointment_ClinicTypeID", "clinicappointment", "ClinicTypeID")
    dbo.execute_dbupdate("UPDATE clinicappointment SET ClinicTypeID=1")
    fields = ",".join([
        dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
        dbo.ddl_add_table_column("ClinicTypeName", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("ClinicTypeDescription", dbo.type_shorttext, True),
        dbo.ddl_add_table_column("IsRetired", dbo.type_integer, True)
    ])
    dbo.execute_dbupdate( dbo.ddl_add_table("lkclinictype", fields) )
    dbo.execute_dbupdate("INSERT INTO lkclinictype VALUES (1, ?, '', 0)", [ _("Consultation", l) ])
    dbo.execute_dbupdate("INSERT INTO lkclinictype VALUES (2, ?, '', 0)", [ _("Followup", l) ])
    dbo.execute_dbupdate("INSERT INTO lkclinictype VALUES (3, ?, '', 0)", [ _("Prescription", l) ])
    dbo.execute_dbupdate("INSERT INTO lkclinictype VALUES (4, ?, '', 0)", [ _("Surgery", l) ])

def update_34809(dbo: Database) -> None:
    # Add ownerlicence.PaymentReference
    add_column(dbo, "ownerlicence", "PaymentReference", dbo.type_shorttext)
    add_index(dbo, "ownerlicence_PaymentReference", "ownerlicence", "PaymentReference") 
    dbo.execute_dbupdate("UPDATE ownerlicence SET PaymentReference = ''")

def update_34810(dbo: Database) -> None:
    l = dbo.locale
    # Add entry type for owner requested euth and set it from the old field
    dbo.execute_dbupdate("INSERT INTO lksentrytype VALUES (10, ?)", [ _("Owner requested euthanasia", l) ])
    dbo.execute_dbupdate("UPDATE animal SET EntryTypeID=10 WHERE AsilomarOwnerRequestedEuthanasia=1")

def update_34811(dbo: Database) -> None:
    l = dbo.locale
    # Add new fields to animalwaitinglist
    add_column(dbo, "animalwaitinglist", "BreedID", dbo.type_integer)
    add_column(dbo, "animalwaitinglist", "DateOfBirth", dbo.type_datetime)
    add_column(dbo, "animalwaitinglist", "Sex", dbo.type_integer)
    add_column(dbo, "animalwaitinglist", "Neutered", dbo.type_integer)
    add_column(dbo, "animalwaitinglist", "MicrochipNumber", dbo.type_shorttext)
    add_column(dbo, "animalwaitinglist", "AnimalName", dbo.type_shorttext)
    add_column(dbo, "animalwaitinglist", "WaitingListRemovalID", dbo.type_integer)
    add_index(dbo, "animalwaitinglist_AnimalName", "animalwaitinglist", "AnimalName")
    add_index(dbo, "animalwaitinglist_MicrochipNumber", "animalwaitinglist", "MicrochipNumber")
    dbo.execute_dbupdate("UPDATE animalwaitinglist SET BreedID=0, Sex=2, Neutered=0, MicrochipNumber='', AnimalName='', WaitingListRemovalID=0")
    fields = ",".join([
        dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
        dbo.ddl_add_table_column("RemovalName", dbo.type_shorttext, False)
    ])
    dbo.execute_dbupdate( dbo.ddl_add_table("lkwaitinglistremoval", fields) )
    dbo.execute_dbupdate("INSERT INTO lkwaitinglistremoval VALUES (1, ?)", [ _("Entered shelter", l) ])
    dbo.execute_dbupdate("INSERT INTO lkwaitinglistremoval VALUES (2, ?)", [ _("Owner kept", l) ])
    dbo.execute_dbupdate("INSERT INTO lkwaitinglistremoval VALUES (3, ?)", [ _("Owner took to another shelter", l) ])
    dbo.execute_dbupdate("INSERT INTO lkwaitinglistremoval VALUES (4, ?)", [ _("Unknown", l) ])

def update_34812(dbo: Database) -> None:
    # Add ownervoucher.VetID
    add_column(dbo, "ownervoucher", "VetID", dbo.type_integer)
    add_index(dbo, "ownervoucher_VetID", "ownervoucher", "VetID")

def update_34813(dbo: Database) -> None:
    # rename animallocation.By to animallocation.MovedBy (By is a MySQL reserved word)
    if column_exists(dbo, "animallocation", "By"):
        add_column(dbo, "animallocation", "MovedBy", dbo.type_shorttext)
        dbo.execute_dbupdate("UPDATE animallocation SET MovedBy=By")
        drop_column(dbo, "animallocation", "By")

def update_34900(dbo: Database) -> None:
    # ClinicTypeDescription was mispelled in the create code above (but not the update for existing databases) 
    # as ClinicTypeDescripton - fix this.
    if column_exists(dbo, "lkclinictype", "ClinicTypeDescripton"):
        add_column(dbo, "lkclinictype", "ClinicTypeDescription", dbo.type_longtext)
        drop_column(dbo, "lkclinictype", "ClinicTypeDescripton")

def update_34901(dbo: Database) -> None:
    # Add animallocation.PrevAnimalLocationID
    add_column(dbo, "animallocation", "PrevAnimalLocationID", dbo.type_integer)
    add_index(dbo, "animallocation_PrevAnimalLocationID", "animallocation", "PrevAnimalLocationID")
    # Default the previous location record to 0
    dbo.execute_dbupdate("UPDATE animallocation SET PrevAnimalLocationID = 0")
    # Calculate the previous location record for each existing location record
    batch = []
    rows = dbo.query("SELECT ID, AnimalID, FromLocationID, ToLocationID, FromUnit, ToUnit FROM animallocation ORDER BY Date DESC")
    for i, r in enumerate(rows):
        # Iterate the rows after this one, which will have lower dates because we ordered date desc
        for x in range(i, len(rows)):
            # If this is the row previous to this one (ie. moved from this one to the current row r)
            # then set the PrevAnimalLocationID
            if rows[x].ANIMALID == r.ANIMALID and rows[x].TOLOCATIONID == r.FROMLOCATIONID and rows[x].TOUNIT == r.FROMUNIT:
                batch.append( (rows[x].ID, r.ID) )
                break
    # Run the batch update
    dbo.execute_many("UPDATE animallocation SET PrevAnimalLocationID=? WHERE ID=?", batch, override_lock=True)

def update_34902(dbo: Database) -> None:
    # Add extra audit fields to media table to match other tables
    # (CreatedDate already existed from update 34402)
    add_column(dbo, "media", "CreatedBy", dbo.type_shorttext)
    add_column(dbo, "media", "LastChangedBy", dbo.type_shorttext)
    add_column(dbo, "media", "LastChangedDate", dbo.type_datetime)
    # Add MediaSource column to identify where media came from
    add_column(dbo, "media", "MediaSource", dbo.type_integer)
    add_index(dbo, "media_MediaSource", "media", "MediaSource")
    # 0 = attach file, 4 = online form, 5 = document template
    dbo.execute_dbupdate("UPDATE media SET MediaSource = CASE " \
        "WHEN SignatureHash LIKE 'online%' THEN 4 " \
        "WHEN MediaName LIKE '%.html' THEN 5 " \
        "ELSE 0 END")
    # Add MediaFlags column to allow users to tag media
    add_column(dbo, "media", "MediaFlags", dbo.type_shorttext)
    add_index(dbo, "media_MediaFlags", "media", "MediaFlags")
    dbo.execute_dbupdate("UPDATE media SET MediaFlags = ''")
    # Add lkmediaflags table
    fields = ",".join([
        dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
        dbo.ddl_add_table_column("Flag", dbo.type_shorttext, False),
        dbo.ddl_add_table_column("IsRetired", dbo.type_integer, True)
    ])
    dbo.execute_dbupdate( dbo.ddl_add_table("lkmediaflags", fields) )

def update_34903(dbo: Database) -> None:
    # Add extra fields to facilitate invoice tracking to animalcost table
    add_column(dbo, "animalcost", "OwnerID", dbo.type_integer)
    add_index(dbo, "animalcost_OwnerID", "animalcost", "OwnerID")
    add_column(dbo, "animalcost", "InvoiceNumber", dbo.type_shorttext)
    add_index(dbo, "animalcost_InvoiceNumber", "animalcost", "InvoiceNumber")

def update_34904(dbo: Database) -> None:
    # Add extra fields to animal notes
    add_column(dbo, "animal", "IsCrateTrained", dbo.type_integer)
    add_column(dbo, "animal", "IsGoodWithElderly", dbo.type_integer)
    add_column(dbo, "animal", "IsGoodTraveller", dbo.type_integer)
    add_column(dbo, "animal", "IsGoodOnLead", dbo.type_integer)
    add_column(dbo, "animal", "EnergyLevel", dbo.type_integer)
    dbo.execute_dbupdate("UPDATE animal SET IsCrateTrained=2, IsGoodWithElderly=2, IsGoodTraveller=2, IsGoodOnLead=2, EnergyLevel=0")

def update_34905(dbo: Database) -> None:
    # Add the ownerrole table
    fields = ",".join([
        dbo.ddl_add_table_column("OwnerID", dbo.type_integer, False),
        dbo.ddl_add_table_column("RoleID", dbo.type_integer, False),
        dbo.ddl_add_table_column("CanView", dbo.type_integer, False),
        dbo.ddl_add_table_column("CanEdit", dbo.type_integer, False)
    ])
    dbo.execute_dbupdate( dbo.ddl_add_table("ownerrole", fields) )
    add_index(dbo, "ownerrole_OwnerIDRoleID", "ownerrole", "OwnerID,RoleID", unique=True)

def update_34906(dbo: Database) -> None:
    # Add the new lostanimalview and foundanimal view HTML templates
    install_html_template(dbo, "lostanimalview", use_max_id=True)
    install_html_template(dbo, "foundanimalview", use_max_id=True)

def update_34907(dbo: Database) -> None:
    # Add extra column to ownercitation
    add_column(dbo, "ownercitation", "CitationNumber", dbo.type_shorttext)
    add_index(dbo, "ownercitation_CitationNumber", "ownercitation", "CitationNumber")
    dbo.execute_dbupdate("UPDATE ownercitation SET CitationNumber=%s" % dbo.sql_zero_pad_left("ID", 6))

