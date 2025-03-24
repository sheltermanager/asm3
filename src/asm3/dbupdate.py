
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
import asm3.stock
import asm3.utils
from asm3.i18n import _
from asm3.typehints import Database, Dict, Generator, List, Tuple

import os, sys

# All ASM3 tables
TABLES = ( "accounts", "accountsrole", "accountstrx", "additional", "additionalfield",
    "adoption", "animal", "animalboarding", "animalcontrol", "animalcontrolanimal", "animalcontrolrole", "animalcost",
    "animaldiet", "animalentry", "animalfigures", "animalfiguresannual",  
    "animalfound", "animallitter", "animallocation", "animallost", "animallostfoundmatch", 
    "animalmedical", "animalmedicaltreatment", "animalname", "animalpublished", 
    "animaltype", "animaltest", "animaltransport", "animalvaccination", "animalwaitinglist", "audittrail", 
    "basecolour", "breed", "citationtype", "clinicappointment", "clinicinvoiceitem", "configuration", 
    "costtype", "customreport", "customreportrole", "dbfs", "deathreason", "deletion", "diary", 
    "diarytaskdetail", "diarytaskhead", "diet", "donationpayment", "donationtype", 
    "entryreason", "event", "eventanimal", "incidentcompleted", "incidenttype", "internallocation", 
    "jurisdiction", "licencetype", "lkanimalflags", "lkboardingtype", "lkclinictype", "lkcoattype", "lkmediaflags", 
    "lkownerflags", "lkproducttype", "lksaccounttype", "lksclinicstatus", "lksdiarylink", "lksdonationfreq", "lksentrytype",
    "lksex", "lksfieldlink", "lksfieldtype", "lksize", "lktaxrate", "lksloglink", "lksmedialink", "lksmediatype", "lksmovementtype", 
    "lksoutcome", "lksposneg", "lksrotatype", "lksunittype", "lksyesno", "lksynun", "lksynunk", "lkstransportstatus", "lkurgency", 
    "lkwaitinglistremoval", "lkworktype", 
    "log", "logtype", "media", "medicalprofile", "messages", "onlineform", 
    "onlineformfield", "onlineformincoming", "owner", "ownercitation", "ownerdonation", "ownerinvestigation", 
"ownerlicence", "ownerlookingfor", "ownerrole", "ownerrota", "ownertraploan", "ownervoucher", "pickuplocation", "product", "publishlog", 
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
    "licencetype", "lkanimalflags", "lkboardingtype", "lkclinictype", "lkcoattype", "lkmediaflags", "lkownerflags", "lkproducttype", "lktaxrate", 
    "lksaccounttype", "lksclinicstatus", "lksdiarylink", "lksdonationfreq", "lksentrytype", "lksex", "lksfieldlink", 
    "lksfieldtype", "lksize", "lksloglink", "lksmedialink", "lksmediatype", "lksmovementtype", "lksoutcome", 
    "lksposneg", "lksrotatype", "lksyesno", "lksynun", "lksynunk", "lkstransportstatus", "lkproductunittype", "lkurgency", 
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
        fstr("FollowupACO", True),
        fdate("FollowupDateTime2", True),
        fint("FollowupComplete2", True),
        fstr("FollowupACO2", True),
        fdate("FollowupDateTime3", True),
        fint("FollowupComplete3", True),
        fstr("FollowupACO3", True),
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
    
    sql += table("lkproducttype", (
        fid(),
        fstr("ProductTypeName"),
        fstr("Description", True),
        fint("IsRetired") ), False)

    sql += table("lktaxrate", (
        fid(),
        fstr("TaxRateName"),
        fstr("Description"),
        ffloat("TaxRate"),
        fint("IsRetired") ), False)
    
    sql += table("lksunittype", (
        fid(),
        fstr("UnitName"),
        fstr("Description"),
        fint("IsRetired") ), False)

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
        fstr("SignatureIP", True),
        fstr("SignatureDevice", True),
        fdate("SignatureDate", True),
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
        fint("IsSupplier", True),
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
        fint("MatchGoodWithElderly", True),
        fint("MatchGoodTraveller", True),
        fint("MatchGoodOnLead", True),
        fint("MatchEnergyLevel", True),
        fint("MatchHouseTrained", True),
        fint("MatchCrateTrained", True),
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
    sql += index("owner_IsSupplier", "owner", "IsSupplier")

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

    sql += table("product", (
        fid(),
        fstr("ProductName"),
        fstr("Description"),
        fint("ProductTypeID"),
        fint("SupplierID"),
        fint("UnitTypeID"),
        fstr("CustomUnit"),
        fint("PurchaseUnitTypeID"),
        fstr("CustomPurchaseUnit"),
        fint("CostPrice"),
        fint("RetailPrice"),
        fint("UnitRatio"),
        fint("TaxRateID"),
        fstr("Barcode"),
        fstr("PLU"),
        fint("GlobalMinimum"),
        fint("IsRetired") ), True)
    sql += index("product_SupplierID", "product", "SupplierID")
    sql += index("product_ProductName", "product", "ProductName")
    sql += index("product_ProductTypeID", "product", "ProductTypeID")
    sql += index("product_Barcode", "product", "Barcode")
    sql += index("product_PLU", "product", "PLU")
    sql += index("product_TaxRateID", "product", "TaxRateID")

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
        fint("ProductID", True),
        fstr("UnitName"),
        ffloat("Total", True),
        ffloat("Balance"),
        ffloat("Low", True),
        fdate("Expiry", True),
        fstr("BatchNumber", True),
        fstr("Barcode", True),
        fint("Cost", True),
        fint("UnitPrice", True),
        fdate("CreatedDate") ), False)
    sql += index("stocklevel_Name", "stocklevel", "Name")
    sql += index("stocklevel_UnitName", "stocklevel", "UnitName")
    sql += index("stocklevel_ProductID", "stocklevel", "ProductID")
    sql += index("stocklevel_Barcode", "stocklevel", "Barcode")
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
    
    def taxrate(tid: int, name: str, taxrate: float) -> str:
        return "INSERT INTO lktaxrate (ID, TaxRateName, Description, TaxRate, IsRetired) VALUES (%s, '%s', '', %f, 0)|=\n" % ( tid, name, taxrate )

    def unittype(tid: int, name: str) -> str:
        return "INSERT INTO lksunittype (ID, UnitName, Description, IsRetired) VALUES (%s, '%s', '', 0)|=\n" % ( tid, name )
    
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
        sql += config("DBV", str(_dbupdates_latest_ver(dbo)))
        sql += config("DatabaseVersion", str(_dbupdates_latest_ver(dbo)))
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
    sql += lookup2("lkproducttype", "ProductTypeName", 1, _("General", l))
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
    sql += lookup2("stockusagetype", "UsageTypeName", 8, _("Movement", l))
    sql += taxrate(1, _("Tax Free", l), 0.0)
    sql += unittype(1, _("kg", l))
    sql += unittype(2, _("g", l))
    sql += unittype(3, _("lb", l))
    sql += unittype(4, _("oz", l))
    sql += unittype(5, _("l", l))
    sql += unittype(6, _("ml", l))
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
            execute(dbo, s.strip())

def install_db_views(dbo: Database) -> None:
    """
    Installs all the database views.
    """
    def create_view(viewname: str, sql: str) -> None:
        try:
            execute(dbo, dbo.ddl_drop_view(viewname) )
            execute(dbo, dbo.ddl_add_view(viewname, sql) )
        except Exception as err:
            asm3.al.error("error creating view %s: %s" % (viewname, err), "dbupdate.install_db_views", dbo)

    # Set us upto date to stop race condition/other clients trying to install
    asm3.configuration.db_view_seq_version(dbo, str(_dbupdates_latest_ver(dbo)))
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
    create_view("v_product", asm3.stock.get_product_query(dbo))
    create_view("v_stock", asm3.stock.get_stocklevel_query(dbo))

def install_db_sequences(dbo: Database) -> None:
    """
    Installs database sequences if supported and sets their initial values
    """
    for table in TABLES:
        if table in TABLES_NO_ID_COLUMN: continue
        initialvalue = dbo.get_id_max(table)
        execute(dbo, dbo.ddl_drop_sequence(table) )
        execute(dbo, dbo.ddl_add_sequence(table, initialvalue) )

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
            execute(dbo, s.strip())

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
        execute(dbo, "DELETE FROM %s" % table)
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
        execute(dbo, "DELETE FROM onlineform")
        execute(dbo, "DELETE FROM onlineformfield")
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
        execute(dbo, "DELETE FROM templatedocument")
        execute(dbo, "DELETE FROM templatehtml")
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
        execute(dbo, "DELETE FROM templatehtml WHERE Name = ?", [name])
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
            execute(dbo, "DELETE FROM %s WHERE %s IN " \
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
    dbo.execute("UPDATE media SET WebsitePhoto=0, DocPhoto=0")
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
    Returns true if there are database updates that need to run.
    """
    return _dbupdates_check(dbo)

def check_for_view_seq_changes(dbo: Database) -> bool:
    """
    Checks to see whether we need to recreate our views and
    sequences by looking to see if the current database version is 
    different. 
    Returns True if we need to update.
    """
    return asm3.configuration.db_view_seq_version(dbo) != str(_dbupdates_latest_ver(dbo))

def reset_db(dbo: Database) -> None:
    """
    Resets a database by removing all data from non-lookup tables.
    """
    for t in TABLES_DATA:
        execute(dbo, "DELETE FROM %s" % t)
    install_db_sequences(dbo)

def _dbupdates_check(dbo: Database) -> bool:
    """
    Returns true if there are any database updates that have not yet run
    """
    _dbupdates_checktable(dbo, asm3.configuration.dbv(dbo))
    alreadyrun = dbo.query_list("SELECT * FROM dbupdates")
    for i in _dbupdates_list(dbo):
        if i not in alreadyrun:
            return True
    return False

def _dbupdates_checktable(dbo: Database, dbv: int = 0) -> None:
    """
    Creates the dbupdates table in the database if it doesn't already exist.
    If after creation, we have a DBV value, we will automatically set
    dbupdates as done for everything upto and including DBV.
    If it does exist, does nothing.
    dbv: The current dbv value rom the database
    """
    if column_exists(dbo, "dbupdates", "ID"): return
    fields = ",".join([
        dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
        dbo.ddl_add_table_column("Date", dbo.type_datetime, False)
    ])
    execute(dbo, dbo.ddl_add_table("dbupdates", fields) )
    if dbv >= 3000:
        for i in _dbupdates_list(dbo):
            if i <= dbv:
                execute(dbo, "INSERT INTO dbupdates (ID, Date) VALUES (?, ?)", [ i, dbo.now() ])

def _dbupdates_exec(dbo: Database, stdout = False, stoponexception = False) -> int:
    """
    Executes any updates that have not been run.
    Returns the highest number of any update that was run so that the caller can update DBV if necessary.
    """
    maxdbv = 0
    alreadyrun = dbo.query_list("SELECT * FROM dbupdates")
    for i in _dbupdates_list(dbo):
        if i not in alreadyrun:
            try:
                msg = f"applying database update {i}"
                if stdout:
                    print(msg)
                else:
                    asm3.al.info(msg, "dbupdate._dbupdates_exec", dbo)
                src = asm3.utils.read_text_file(f"{dbo.installpath}/asm3/dbupdates/{i}.py")
                exec(src)
                alreadyrun.append(i)
                execute(dbo, "INSERT INTO dbupdates (ID, Date) VALUES (?, ?)", [i, dbo.now()])
                if i > maxdbv: maxdbv = i
            except Exception as err:
                import traceback
                msg = f"ERROR: {err}\n{traceback.format_exc()}"
                if stdout:
                    print(msg)
                    if stoponexception: return
                else:
                    asm3.al.error(msg, "dbupdate._dbupdates_exec", dbo, sys.exc_info())
    return maxdbv

def _dbupdates_latest_ver(dbo: Database) -> int:
    """
    Returns the highest available dbupdate from the set.
    """
    updates = _dbupdates_list(dbo)
    return updates[-1]

def _dbupdates_list(dbo: Database) -> List[int]:
    """ 
    Returns the list of available dbupdates to run as a list of ints,
    ordered from oldest to newest.
    """
    updates = []
    for i in asm3.utils.listdir(f"{dbo.installpath}/asm3/dbupdates/"):
        if i.endswith(".py"): updates.append(asm3.utils.atoi(i))
    updates = sorted(updates)
    return updates

def perform_updates(dbo: Database) -> int:
    """
    Performs any updates that need to be run against the database. 
    Returns the new database version.
    """
    ver = asm3.configuration.dbv(dbo)
    _dbupdates_checktable(dbo, ver)
    v = _dbupdates_exec(dbo)
    if v > ver:
        asm3.configuration.dbv(dbo, v)
    return asm3.configuration.dbv(dbo)

def perform_updates_stdout(dbo: Database, stoponexc = False) -> None:
    """
    Performs any updates that need to be run against the database. 
    Intended to be called by testing functions as this outputs to stdout.
    """
    ver = asm3.configuration.dbv(dbo)
    _dbupdates_checktable(dbo, ver)
    v = _dbupdates_exec(dbo, stdout=True, stoponexception = stoponexc)
    if v > ver:
        asm3.configuration.dbv(dbo, v)

def add_column(dbo: Database, table: str, column: str, coltype: str) -> None:
    execute(dbo, dbo.ddl_add_column(table, column, coltype) )

def add_index(dbo: Database, indexname: str, tablename: str, fieldname: str, unique: bool = False, partial: bool = False, ignore_errors = False) -> None:
    try:
        execute(dbo, dbo.ddl_add_index(indexname, tablename, fieldname, unique, partial) )
    except Exception as err:
        if not ignore_errors: raise err

def drop_column(dbo: Database, table: str, column: str) -> None:
    execute(dbo, dbo.ddl_drop_column(table, column) )

def drop_index(dbo: Database, indexname: str, tablename: str) -> None:
    try:
        execute(dbo, dbo.ddl_drop_index(indexname, tablename) )
    except:
        pass

def execute(dbo: Database, q: str, params: List = None) -> int:
    return dbo.execute_dbupdate( q, params )

def modify_column(dbo: Database, table: str, column: str, newtype: str, using: str = "") -> None:
    execute(dbo, dbo.ddl_modify_column(table, column, newtype, using) )

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
    drop_column(dbo, "users", "SecurityMap")
    drop_column(dbo, "animal", "SmartTagSentDate")
    drop_column(dbo, "media", "LastPublished")
    drop_column(dbo, "media", "LastPublishedPF")
    drop_column(dbo, "media", "LastPublishedAP")
    drop_column(dbo, "media", "LastPublishedP911")
    drop_column(dbo, "media", "LastPublishedRG")

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


