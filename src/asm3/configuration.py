import asm3.al
import asm3.audit
import asm3.cachedisk
import asm3.i18n

import os

from asm3.sitedefs import LOCALE, TIMEZONE, WATERMARK_FONT_BASEDIRECTORY
from asm3.typehints import Any, Database, Dict, List, PostedData, Tuple

# Default configuration values for unset items. This is so they
# still get shown correctly in the options screens.
DEFAULTS = {
    "AdvancedFindAnimalOnShelter": "Yes",
    "AgeGroup1": "0.5",
    "AgeGroup1Name": "Baby",
    "AgeGroup2": "2",
    "AgeGroup2Name": "Young Adult",
    "AgeGroup3": "7",
    "AgeGroup3Name": "Adult",
    "AgeGroup4": "50",
    "AgeGroup4Name": "Senior",
    "AllowDuplicateMicrochip": "No",
    "AllowNonANMicrochip": "No",
    "AllowODTDocumentTemplates": "No",
    "AddAnimalsShowAcceptance": "No",
    "AddAnimalsShowBreed": "Yes",
    "AddAnimalsShowBroughtInBy": "No",
    "AddAnimalsShowColour": "No",
    "AddAnimalsShowCoordinator": "No",
    "AddAnimalsShowDateBroughtIn": "Yes",
    "AddAnimalsShowEntryCategory": "Yes",
    "AddAnimalsShowFosterer": "Yes",
    "AddAnimalsShowHold": "Yes",
    "AddAnimalsShowLocation": "Yes",
    "AddAnimalsShowLocationUnit": "Yes",
    "AddAnimalsShowMicrochip": "No",
    "AddAnimalsShowNeutered": "No",
    "AddAnimalsShowOriginalOwner": "No",
    "AddAnimalsShowPickup": "No",
    "AddAnimalsShowSize": "No",
    "AddAnimalsShowTattoo": "No",
    "AddAnimalsShowTimeBroughtIn": "No",
    "AddAnimalsShowWeight": "No",
    "AdoptionCheckoutDonationMsg": "Our organization depends on the kind donations of individuals to provide animals with medical care, food and shelter.\n<br/><br/><b>We need your help!</b>",
    "AdoptionCheckoutDonationTiers": "$0=No thanks\n$10=Microchip one pet\n$25=One week of milk for a litter of kittens\n$50=Vaccinate a litter of puppies\n$100=Spay/neuter and vaccinate one pet\n$200=Contribute to surgery for pets in need",
    "AnimalFiguresSplitEntryReason": "No",
    "AnnualFiguresShowBabies": "Yes",
    "AnnualFiguresShowBabiesType": "Yes",
    "AnnualFiguresBabyMonths" : "6",
    "AnnualFiguresSplitAdoptions": "No",
    "AnonymiseAdopters": "Yes",
    "AnonymisePersonalData": "No",
    "AnonymiseAfterYears": "0",
    "AuditOnViewRecord": "Yes",
    "AuditOnViewReport": "Yes",
    "AuditOnSendEmail": "Yes",
    "AutoCancelReservesDays": "14",
    "AutoDefaultShelterCode": "Yes",
    "AutoDefaultVaccBatch": "Yes",
    "AutoHashProcessedForms": "Yes",
    "AutoInsuranceStart": "0",
    "AutoInsuranceEnd": "0",
    "AutoInsuranceNext": "0",
    "AutoNewImagesNotForPublish": "No",
    "AutoNotForAdoption": "No",
    "AutoRemoveAnimalMediaExit": "No",
    "AutoRemoveAMExitYears": "0",
    "AutoRemoveDocumentMedia": "No",
    "AutoRemoveDMYears": "0",
    "AutoRemoveHoldDays": "0",
    "AutoRemoveIncomingFormsDays": "28",
    "AutoRemovePeopleCancResv": "No",
    "AutoRemovePeopleCRYears": "0",
    "AFDefaultBreed": "221",
    "AFDefaultCoatType": "0",
    "AFDefaultColour": "1",
    "AFDefaultDeathReason": "1",
    "AFDefaultDiaryPerson": "",
    "AFDefaultDonationType": "1",
    "AFDefaultPaymentMethod": "1",
    "AFDefaultEntryReason": "4",
    "AFDefaultLocation": "1",
    "AFDefaultLogFilter": "-1",
    "AFDefaultLogType": "1",
    "AFDefaultReservationStatus": "1", 
    "AFDefaultReturnReason": "4",
    "AFDefaultSize": "1",
    "AFDefaultSpecies": "2",
    "AFDefaultType": "11",
    "AFDefaultTestType": "1",
    "AFDefaultVaccinationType": "1",
    "AFNonShelterType": "40",
    "AKCRegisterAll": "No",
    "AlertSpeciesMicrochip": "1,2",
    "AlertSpeciesNeuter": "1,2",
    "AlertSpeciesNeverVacc": "1,2",
    "AlertSpeciesRabies": "1,2",
    "AvidReRegistration": "No", 
    "AvidRegisterOverseas": "No",
    "AvidOverseasOriginCountry": "",
    "BehaveLogType": "3",
    "Behave1Name": "Eaten",
    "Behave1Values": "None|Minimal|Half|Majority|All",
    "Behave2Name": "Drunk",
    "Behave2Values": "None|Minimal|Half|Majority|All",
    "Behave3Name": "Toilet",
    "Behave3Values": "Urine|Faeces|Urine + Faeces|None",
    "Behave4Name": "Exercise/Contact",
    "Behave4Values": "",
    "Behave5Name": "Unusual Symptoms",
    "Behave5Values": "",
    "BoardingCostType": "1",
    "BoardingPaymentType": "7",
    "CancelReservesOnAdoption": "Yes",
    "CardcomSuccessURL": "https://secure.cardcom.solutions/DealWasSuccessful.aspx",
    "CardcomErrorURL": "https://secure.cardcom.solutions/DealWasUnSuccessful.aspx",
    "CardcomDocumentType": "3",
    "CardcomMaxInstallments": "6",
    "CardcomPaymentMethodMapping": '{"1":{"action":"receipt","method":"cash"},"2":{"action":"receipt","method":"cheque"},"3":{"action":"cc_charge"},"4":{"action":"cc_charge"},"5":{"action":"receipt","method":"custom","tx_id":32},"7":{"action":"receipt","method":"custom","tx_id":30},"default":{"action":"error"}}',
    "CardcomPaymentTypeMapping": '{"1":{"InvoiceType":405},"3":{"InvoiceType":405},"4":{"InvoiceType":405},"5":{"InvoiceType":405},"default":{"InvoiceType":3}}',
    "CardcomHandleNonCCPayments": "No",
    "CloneAnimalIncludeLogs": "Yes",
    "CostSourceAccount": "9",
    "CreateBoardingCostOnAdoption": "Yes",
    "CreateCostTrx": "No",
    "CreateDonationTrx": "Yes",
    "CodingFormat": "TYYYYNNN",
    "CurrencyCode": "USD",
    "ShortCodingFormat": "NNT",
    "DateBroughtInFutureLimit": "30",
    "DateDiffCutoffs": "7|182|365",
    "DefaultAnimalAge": "1.0", 
    "DefaultDailyBoardingCost": "2000",
    "DefaultDateBroughtIn": "Yes",
    "DefaultIncidentType": "1",
    "DefaultJurisdiction": "1",
    "DefaultMediaNotesFromFile": "Yes",
    "DefaultShiftStart": "09:00",
    "DefaultShiftEnd": "17:00",
    "DefaultTrialLength": "30",
    "DiaryCompleteOnDeath": "Yes",
    "DisableAnimalControl": "No",
    "DisableBoarding": "Yes",
    "DisableClinic": "No",
    "DisableEntryHistory": "Yes",
    "DisableEvents": "Yes",
    "DisableStockControl": "No",
    "DisableTransport": "No",
    "DisableTrapLoan": "No",
    "DisableAsilomar": "No",
    "DisableDocumentRepo": "No",
    "DisableOnlineForms": "No",
    "DisableRetailer": "No",
    "DocumentWordProcessor": "HTML",
    "DonationDateOverride": "No",
    "DonationFees": "Yes",
    "DonationQuantities": "No",
    "DonationFeeAccount": "21",
    "DonationTargetAccount": "9",
    "DonationTrxOverride": "No",
    "DonationVATAccount": "22",
    "DonationOnMoveReserve": "Yes",
    "DontShowRabies": "Yes",
    "DontShowSize": "No",
    "EmailDiaryNotes": "Yes", 
    "EmailDiaryOnChange": "No",
    "EmailDiaryOnComplete": "No",
    "EmailEmptyReports": "Yes",
    "EmailMessages": "Yes", 
    "EmblemAdoptable": "Yes",
    "EmblemAlwaysLocation": "No",
    "EmblemBoarding": "Yes",
    "EmblemBonded": "Yes",
    "EmblemCourtesy": "Yes",
    "EmblemCrueltyCase": "Yes",
    "EmblemDeceased": "Yes",
    "EmblemFutureAdoption": "Yes",
    "EmblemHold": "Yes",
    "EmblemLongTerm": "Yes",
    "EmblemNeverVacc": "No",
    "EmblemNonShelter": "Yes",
    "EmblemNotForAdoption": "Yes",
    "EmblemNotMicrochipped": "Yes",
    "EmblemPositiveTest": "Yes",
    "EmblemQuarantine": "Yes",
    "EmblemRabies": "No",
    "EmblemReserved": "Yes",
    "EmblemSpecialNeeds": "Yes",
    "EmblemTrialAdoption": "Yes",
    "EmblemUnneutered": "Yes",
    "EventSearchColumns": "StartDateTime,EndDateTime,EventName,EventOwnerName,EventAddress,EventTown",
    "EventExcludeAnimalsWithFlags": "",
    "EventExcludeAnimalsInLocations": "",
    "FancyTooltips": "No",
    "FirstDayOfWeek": "1",
    "FlagChangeLog": "Yes",
    "FlagChangeLogType": "3",
    "FormatPhoneNumbers": "Yes",
    "FosterOnShelter": "Yes",
    "FostererEmails": "No", 
    "FostererEmailOverdueDays": "-30",
    "FostererEmailSkipNoMedical": "No",
    "FoundAnimalSearchColumns": "LostFoundID,Owner,MicrochipNumber,AreaFound,"
        "AreaPostCode,DateFound,AgeGroup,SexName,SpeciesName,BreedName,"
        "BaseColourName,DistFeat",
    "FutureOnShelter": "Yes",
    "ShowGDPRContactOptIn": "No",
    "GDPRContactChangeLog": "No",
    "GDPRContactChangeLogType": "6",
    "GeocodeWithPostcodeOnly": "No",
    "GenerateDocumentLog": "No",
    "GenerateDocumentLogType": "5",
    "HideCountry": "Yes",
    "HideHomeCheckedNoFlag": "Yes",
    "HideLookingFor": "No",
    "HoldChangeLog": "Yes",
    "HoldChangeLogType": "3",
    "IncidentPermissions": "No",
    "IncidentSearchColumns": "IncidentNumber,IncidentType,IncidentDateTime,"
        "DispatchAddress,DispatchTown,DispatchPostcode,JurisdictionName,"
        "LocationName,Suspect,DispatchDateTime,RespondedDateTime,"
        "DispatchedACO,FollowupDateTime,CompletedDate,CompletedName,"
        "CallNotes",
    "InactivityTimer": "No",
    "InactivityTimeout": "20", 
    "IncludeIncompleteMedicalDoc": "Yes",
    "IncludeOffShelterMedical": "No",
    "Locale": "en",
    "LocationChangeLog": "Yes",
    "LocationChangeLogType": "3",
    "LocationFiltersEnabled": "No",
    "LongTermDays": "182",
    "LostAnimalSearchColumns": "LostFoundID,Owner,MicrochipNumber,AreaLost,"
        "AreaPostCode,DateLost,AgeGroup,SexName,SpeciesName,BreedName,"
        "BaseColourName,DistFeat",
    "MailMergeMaxEmails": "3000",
    "MainScreenAnimalLinkMode": "recentlychanged",
    "MainScreenAnimalLinkMax": "9",
    "ManualCodes": "No",
    "MatchSpecies": "5",
    "MatchBreed": "5",
    "MatchAge": "5",
    "MatchSex": "5",
    "MatchAreaLost": "5",
    "MatchFeatures": "5",
    "MatchMicrochip": "50",
    "MatchPostcode": "5",
    "MatchColour": "5",
    "MatchIncludeShelter": "Yes",
    "MatchWithin2Weeks": "5",
    "MatchPointFloor": "20",
    "MaxMediaFileSize": "1000",
    "MediaAllowJPG": "Yes",
    "MediaAllowPDF": "Yes",
    "MediaTableMode": "No",
    "MedicalItemDisplayLimit": "500",
    "MedicalPrecreateTreatments": "No",
    "MicrochipRegisterMovements": "1,5",
    "MovementDonationsDefaultDue": "No",
    "MovementNumberOverride": "No",
    "MovementPersonOnlyReserves": "Yes",
    "MultiSiteEnabled": "No", 
    "MoveAdoptGeneratePaperwork": "Yes",
    "MoveAdoptDonationsEnabled": "No",
    "JSWindowPrint": "Yes",
    "OnlineFormSpamHoneyTrap": "Yes",
    "OnlineFormSpamUACheck": "No",
    "OnlineFormSpamFirstnameMixCase": "Yes",
    "OnlineFormDeleteOnProcess": "No",
    "Organisation": "Organisation",
    "OrganisationAddress": "Address",
    "OrganisationTelephone": "Telephone",
    "OwnerAddressCheck": "Yes",
    "OwnerNameCheck": "Yes",
    "OwnerNameFormat": "{ownertitle} {ownerforenames} {ownersurname}",
    "OwnerNameCoupleFormat": "{ownername1} & {ownername2}",
    "OwnerNameMarriedFormat": "{ownerforenames1} & {ownerforenames2} {ownersurname}",
    "OwnerSearchColumns": "OwnerCode,OwnerName,OwnerSurname," \
        "MembershipNumber,AdditionalFlags,OwnerAddress," \
        "OwnerTown,OwnerCounty,OwnerPostcode,HomeTelephone,WorkTelephone," \
        "MobileTelephone,EmailAddress",
    "PetsLocatedIncludeShelter": "No",
    "PetsLocatedAnimalFlag": "",
    "PicturesInBooks": "Yes",
    "PicturesInBooksClinic": "No",
    "PDFInline": "Yes",
    "PDFZoom": "100",
    "PublisherUseComments": "Yes",
    "PublisherPresets": "includefosters excludeunder=12",
    "PublisherSub24Frequency": "0",
    "QuicklinksID": "40,46,25,31,34,19,20",
    "QuicklinksHomeScreen": "Yes",
    "QuicklinksAllScreens": "No",
    "RecordSearchLimit": "1000",
    "ReloadMedical": "Yes",
    "ReportToolbar": "Yes",
    "ReservesOverdueDays": "7",
    "RetailerOnShelter": "Yes",
    "ReturnFostersOnAdoption": "Yes",
    "ReturnFostersOnTransfer": "Yes",
    "ReturnRetailerOnAdoption": "Yes",
    "ScalePDFs": "Yes", 
    "SearchColumns": "AnimalName,Image,ShelterCode,ShelterLocation,SpeciesID,BreedName," \
        "Sex, AnimalAge, Size, BaseColourID, Markings, IdentichipNumber, DateBroughtIn",
    "SearchSort": "6",
    "ServiceEnabled": "Yes",
    "ServiceAuthEnabled": "Yes", 
    "ShelterViewDefault": "location",
    "ShelterViewDragDrop": "Yes",
    "ShelterViewShowCodes": "No",
    "ShowCostAmount": "Yes",
    "ShowCostPaid": "No",
    "ShowDeceasedHomePage": "Yes",
    "ShowFinancialHomePage": "Yes",
    "ShowFullCommentsInTables": "No",
    "ShowAlertsHomePage": "Yes", 
    "ShowLatLong": "No",
    "ShowLookupDataID": "No",
    "ShowSexBorder": "Yes",
    "ShowTimelineHomePage": "Yes", 
    "ShowOverviewHomePage": "Yes", 
    "ShowStatsHomePage": "thismonth", 
    "ShowFirstTime": "Yes",
    "ShowILOffShelter": "Yes",
    "ShowPersonMiniMap": "Yes",
    "ShowSearchGo": "No", 
    "ShowWeightInLbs": "Yes",
    "ShowWeightInLbsFraction": "No",
    "ShowWeightUnitsInLog": "Yes",
    "SMTPOverride": "No",
    "SMTPPort": "25",
    "SoftReleases": "No",
    "SoftReleaseOnShelter": "No",
    "StickyTableHeaders": "Yes",
    "SACStrayCategory": "7",
    "SACSurrenderCategory": "17",
    "SACTNRCategory": "14",
    "SystemLogType": "3",
    "TableHeadersVisible": "Yes",
    "TemplatesForNonShelter": "No",
    "ThumbnailSize": "150x150",
    "Timezone": "-5",
    "TimezoneDST": "Yes",
    "TrialAdoptions": "No",
    "TrialOnShelter": "No",
    "UniqueLicenceNumbers": "Yes",
    "UpdateAnimalTestFields": "Yes",
    "UseAutoInsurance": "No",
    "UseShortShelterCodes": "Yes", 
    "USStateCodes": "No",
    "VATEnabled": "Yes",
    "VATExclusive": "No",
    "VATRate": "20",
    "VetEnvoyHomeAgainEnabled": "Yes",
    "VetEnvoyAKCReuniteEnabled": "Yes",
    "WaitingListViewColumns": "Rank,OwnerName,OwnerAddress," \
        "HomeTelephone,EmailAddress,DatePutOnList,TimeOnList," \
        "DateRemovedFromList,Urgency,SpeciesID,Size,AnimalDescription",
    "WaitingListDefaultUrgency": "3",
    "WaitingListUrgencyUpdatePeriod": "14",
    "WaitingListUseMultipleHighlights": "No",
    "WarnACTypeChange": "Yes",
    "WarnBroughtIn": "Yes",
    "WarnMultipleReserves": "Yes", 
    "WarnUnaltered": "Yes",
    "WarnNoMicrochip": "Yes",
    "WarnNoPendingVacc": "Yes",
    "WarnNoHomeCheck": "Yes",
    "WarnNoReserve": "Yes",
    "WarnBannedAddress": "Yes",
    "WarnBannedOwner": "Yes",
    "WarnOOPostcode": "Yes",
    "WarnOSMedical": "Yes",
    "WarnSimilarAnimalName": "Yes",
    "WatermarkFontFile": "dejavu/DejaVuSans-Bold.ttf",
    "WatermarkFontFillColor": "white",
    "WatermarkFontMaxSize": "180",
    "WatermarkFontOffset": "20",
    "WatermarkFontShadowColor": "black",
    "WatermarkFontStroke": "3",
    "WatermarkXOffset": "10",
    "WatermarkYOffset": "10",
    "WeightChangeLog": "Yes",
    "WeightChangeLogType": "4",
}

def cstring(dbo, key: str, default: str = "") -> str:
    cmap = get_map(dbo)
    if key not in cmap:
        return default
    return cmap[key]

def cboolean(dbo, key: str, default: bool = False) -> bool:
    defstring = "No"
    if default: defstring = "Yes"
    v = cstring(dbo, key, defstring)
    return v == "Yes" or v == "True"

def cint(dbo, key: str, default: int = 0) -> int:
    defstring = str(default)
    v = cstring(dbo, key, defstring)
    try:
        return int(v)
    except:
        return int(0)

def cfloat(dbo, key: str, default: float = 0.0) -> float:
    defstring = str(default)
    v = cstring(dbo, key, defstring)
    try:
        return float(v)
    except:
        return float(0)

def cset(dbo, key: str, value: str = "", ignoreDBLock: bool = False, sanitiseXSS: bool = True, invalidateConfigCache: bool = True) -> None:
    """
    Update a configuration item in the table.
    """
    dbo.execute("DELETE FROM configuration WHERE ItemName LIKE ?", [key], override_lock=ignoreDBLock)
    if sanitiseXSS: value = dbo.escape_xss(value)
    dbo.execute("INSERT INTO configuration (ItemName, ItemValue) VALUES (?, ?)", (key, value), override_lock=ignoreDBLock)
    if invalidateConfigCache: invalidate_config_cache(dbo)

def cset_db(dbo: Database, key: str, value: str = "") -> None:
    """
    Updates a configuration entry that could take place during a
    database update, so needs to ignore the locked flag.
    """
    cset(dbo, key, value, ignoreDBLock = True)

def csave(dbo: Database, username: str, post: PostedData) -> None:
    """
    Takes configuration data passed as a web post and saves it to the database.
    """
    def valid_code(s: str) -> bool:
        """
        Returns True if s has a valid code portion in it
        """
        VALID_CODES = ("OO", "OOO", "XX", "XXX", "NN", "NNN", "UUUU", "UUUUUUUUUU")
        for v in VALID_CODES:
            if s.find(v) != -1:
                return True
        return False

    cmap = get_map(dbo)

    def put(k: str, v: str, sanitiseXSS: bool = True) -> None:
        # Only update the value in the database if it's new or changed
        if k not in cmap or cmap[k] != v: cset(dbo, k, v, sanitiseXSS = sanitiseXSS, invalidateConfigCache = False)

    for k in post.data.keys():
        if k == "mode" or k == "filechooser": continue
        v = post.string(k, False)
        if k in ("AdoptionCheckoutDonationMsg", "EmailSignature", "FostererEmailsMsg"):
            # It's HTML - don't XSS escape it
            put(k, v, sanitiseXSS = False)
        elif k == "CodingFormat":
            # If there's no valid N, X, O or U tokens in there, it's not valid so reset to
            # the default.
            if not valid_code(v):
                put(k, "TYYYYNNN")
            else:
                put(k, v)
        elif k == "ShortCodingFormat":
            # If there's no N, X, O or U in there, it's not valid so reset to
            # the default.
            if not valid_code(v):
                put(k, "NNT")
            else:
                put(k, v)
        elif k == "DefaultDailyBoardingCost":
            # Need to handle currency fields differently
            put(k, str(post.integer(k)))
        elif k == "WatermarkFontFile":
            validFiles = watermark_get_valid_font_files()
            if v not in validFiles:
                put(k, DEFAULTS[k])
            else:
                put(k, v, sanitiseXSS = False)
        elif k.startswith("rc:"):
            # It's a NOT check
            if v == "checked": v = "No"
            if v == "off": v = "Yes"
            put(k[3:], v)
        elif v == "checked" or v == "off":
            # It's a checkbox
            if v == "checked": v = "Yes"
            if v == "off": v = "No"
            put(k, v)
        else:
            # Plain string value
            put(k, v)
    asm3.audit.edit(dbo, username, "configuration", 0, "", str(post))
    invalidate_config_cache(dbo)

def get_map(dbo: Database) -> Dict[str, str]:
    """ Returns a map of the config items, using a read-through cache to save database calls """
    cmap = asm3.cachedisk.get("config", dbo.database, expectedtype=dict)
    if cmap is None:
        rows = dbo.query("SELECT ItemName, ItemValue FROM configuration ORDER BY ItemName")
        cmap = DEFAULTS.copy()
        for r in rows:
            cmap[r.itemname] = r.itemvalue
        asm3.cachedisk.put("config", dbo.database, cmap, 3600) # one hour cache means direct database updates show up eventually
    return cmap

def invalidate_config_cache(dbo: Database) -> None:
    asm3.cachedisk.delete("config", dbo.database)

def account_period_totals(dbo: Database) -> bool:
    return cboolean(dbo, "AccountPeriodTotals")

def accounting_period(dbo: Database) -> str:
    return cstring(dbo, "AccountingPeriod")

def add_animals_show_time_brought_in(dbo: Database) -> bool:
    return cboolean(dbo, "AddAnimalsShowTimeBroughtIn", DEFAULTS["AddAnimalsShowTimeBroughtIn"] == "Yes")

def adoptapet_user(dbo: Database) -> str:
    return cstring(dbo, "SaveAPetFTPUser")

def adoptapet_password(dbo: Database) -> str:
    return cstring(dbo, "SaveAPetFTPPassword")

def adoption_checkout_donation_msg(dbo: Database) -> str:
    return cstring(dbo, "AdoptionCheckoutDonationMsg", DEFAULTS["AdoptionCheckoutDonationMsg"])

def adoption_checkout_donationid(dbo: Database) -> int:
    return cint(dbo, "AdoptionCheckoutDonationID")

def adoption_checkout_donation_tiers(dbo: Database) -> str:
    return cstring(dbo, "AdoptionCheckoutDonationTiers", DEFAULTS["AdoptionCheckoutDonationTiers"])

def adoption_checkout_feeid(dbo: Database) -> int:
    return cint(dbo, "AdoptionCheckoutFeeID")

def adoption_checkout_payment_method(dbo: Database) -> int:
    return cint(dbo, "AdoptionCheckoutPaymentMethod")

def adoption_checkout_processor(dbo: Database) -> str:
    return cstring(dbo, "AdoptionCheckoutProcessor")

def adoption_checkout_templateid(dbo: Database) -> int:
    return cint(dbo, "AdoptionCheckoutTemplateID")

def advanced_find_animal(dbo: Database) -> bool:
    return cboolean(dbo, "AdvancedFindAnimal")

def advanced_find_animal_on_shelter(dbo: Database) -> bool:
    return cboolean(dbo, "AdvancedFindAnimalOnShelter", DEFAULTS["AdvancedFindAnimalOnShelter"] == "Yes")

def age_group_bands(dbo: Database) -> List[Tuple[str, float]]:
    bands = []
    for i in range(1, 9):
        groupname = cstring(dbo, "AgeGroup%dName" % i)
        if groupname.strip() != "":
            bands.append( ( groupname, cfloat(dbo, "AgeGroup%d" % i) ) )
    return bands

def age_group_for_name(dbo: Database, name: str) -> float:
    for group, years in age_group_bands(dbo):
        if group == name:
            return years
    return 0.0

def age_groups(dbo: Database) -> List[str]:
    groups = []
    for i in range(1, 9):
        groupname = cstring(dbo, "AgeGroup%dName" % i)
        if groupname.strip() != "":
            groups.append(groupname)
    return groups

def age_group(dbo: Database, band) -> float:
    return cfloat(dbo, "AgeGroup%d" % band)

def age_group_name(dbo: Database, band) -> str:
    return cstring(dbo, "AgeGroup%dName" % band)

def akc_enrollmentsourceid(dbo: Database) -> str:
    return cstring(dbo, "AKCEnrollmentSourceID")

def akc_register_all(dbo: Database) -> bool:
    return cboolean(dbo, "AKCRegisterAll")

def alert_species_microchip(dbo: Database) -> str:
    s = cstring(dbo, "AlertSpeciesMicrochip", DEFAULTS["AlertSpeciesMicrochip"])
    if s == "": return "0" # Always return something due to IN clauses of queries
    return s

def alert_species_never_vacc(dbo: Database) -> str:
    s = cstring(dbo, "AlertSpeciesNeverVacc", DEFAULTS["AlertSpeciesNeverVacc"])
    if s == "": return "0" # Always return something due to IN clauses of queries
    return s

def alert_species_neuter(dbo: Database) -> str:
    s = cstring(dbo, "AlertSpeciesNeuter", DEFAULTS["AlertSpeciesNeuter"])
    if s == "": return "0" # Always return something due to IN clauses of queries
    return s

def alert_species_rabies(dbo: Database) -> str:
    s = cstring(dbo, "AlertSpeciesRabies", DEFAULTS["AlertSpeciesRabies"])
    if s == "": return "0" # Always return something due to IN clauses of queries
    return s

def all_diary_home_page(dbo: Database) -> bool:
    return cboolean(dbo, "AllDiaryHomePage")

def allow_duplicate_microchip(dbo: Database) -> bool:
    return cboolean(dbo, "AllowDuplicateMicrochip", DEFAULTS["AllowDuplicateMicrochip"] == "Yes")

def allow_odt_document_templates(dbo: Database) -> bool:
    return cboolean(dbo, "AllowODTDocumentTemplates", DEFAULTS["AllowODTDocumentTemplates"] == "Yes")

def anibase_practice_id(dbo: Database) -> str:
    return cstring(dbo, "AnibasePracticeID")

def anibase_pin_no(dbo: Database) -> str:
    return cstring(dbo, "AnibasePinNo")

def animal_figures_split_entryreason(dbo: Database) -> bool:
    return cboolean(dbo, "AnimalFiguresSplitEntryReason", DEFAULTS["AnimalFiguresSplitEntryReason"] == "Yes")

def animal_search_columns(dbo: Database) -> str:
    return cstring(dbo, "SearchColumns", DEFAULTS["SearchColumns"])

def annual_figures_show_babies(dbo: Database) -> bool:
    return cboolean(dbo, "AnnualFiguresShowBabies", DEFAULTS["AnnualFiguresShowBabies"] == "Yes")

def annual_figures_show_babies_type(dbo: Database) -> bool:
    return cboolean(dbo, "AnnualFiguresShowBabiesType", DEFAULTS["AnnualFiguresShowBabiesType"] == "Yes")

def annual_figures_baby_months(dbo: Database) -> int:
    return cint(dbo, "AnnualFiguresBabyMonths", int(DEFAULTS["AnnualFiguresBabyMonths"]))

def annual_figures_split_adoptions(dbo: Database) -> bool:
    return cboolean(dbo, "AnnualFiguresSplitAdoptions", DEFAULTS["AnnualFiguresSplitAdoptions"] == "Yes")

def anonymise_adopters(dbo: Database) -> bool:
    return cboolean(dbo, "AnonymiseAdopters", DEFAULTS["AnonymiseAdopters"] == "Yes")

def anonymise_personal_data(dbo: Database) -> bool:
    return cboolean(dbo, "AnonymisePersonalData", DEFAULTS["AnonymisePersonalData"] == "Yes")

def anonymise_after_years(dbo: Database) -> int:
    return cint(dbo, "AnonymiseAfterYears", DEFAULTS["AnonymiseAfterYears"])

def audit_on_view_record(dbo: Database) -> bool:
    return cboolean(dbo, "AuditOnViewRecord", DEFAULTS["AuditOnViewRecord"] == "Yes")

def audit_on_view_report(dbo: Database) -> bool:
    return cboolean(dbo, "AuditOnViewReport", DEFAULTS["AuditOnViewReport"] == "Yes")

def audit_on_send_email(dbo: Database) -> bool:
    return cboolean(dbo, "AuditOnSendEmail", DEFAULTS["AuditOnSendEmail"] == "Yes")

def auto_cancel_reserves_days(dbo: Database) -> int:
    return cint(dbo, "AutoCancelReservesDays", int(DEFAULTS["AutoCancelReservesDays"]))

def auto_cancel_hold_days(dbo: Database) -> int:
    return cint(dbo, "AutoCancelHoldDays", int(DEFAULTS["AutoCancelHoldDays"]))

def auto_default_vacc_batch(dbo: Database) -> bool:
    return cboolean(dbo, "AutoDefaultVaccBatch", DEFAULTS["AutoDefaultVaccBatch"] == "Yes")

def auto_hash_processed_forms(dbo: Database) -> bool:
    return cboolean(dbo, "AutoHashProcessedForms", DEFAULTS["AutoHashProcessedForms"] == "Yes")

def auto_insurance_next(dbo: Database, newins = 0) -> Any:
    if newins == 0:
        return cint(dbo, "AutoInsuranceNext")
    else:
        cset(dbo, "AutoInsuranceNext", str(newins))

def auto_media_notes(dbo: Database) -> bool:
    return cboolean(dbo, "AutoMediaNotes")

def auto_new_images_not_for_publish(dbo: Database) -> bool:
    return cboolean(dbo, "AutoNewImagesNotForPublish", DEFAULTS["AutoNewImagesNotForPublish"] == "Yes")

def auto_not_for_adoption(dbo: Database) -> bool:
    return cboolean(dbo, "AutoNotForAdoption", DEFAULTS["AutoNotForAdoption"] == "Yes")

def auto_remove_animal_media_exit(dbo: Database) -> bool:
    return cboolean(dbo, "AutoRemoveAnimalMediaExit", DEFAULTS["AutoRemoveAnimalMediaExit"] == "Yes")

def auto_remove_animal_media_exit_years(dbo: Database) -> int:
    return cint(dbo, "AutoRemoveAMExitYears", int(DEFAULTS["AutoRemoveAMExitYears"]))

def auto_remove_document_media(dbo: Database) -> bool:
    return cboolean(dbo, "AutoRemoveDocumentMedia", DEFAULTS["AutoRemoveDocumentMedia"] == "Yes")

def auto_remove_document_media_years(dbo: Database) -> int:
    return cint(dbo, "AutoRemoveDMYears", int(DEFAULTS["AutoRemoveDMYears"]))

def auto_remove_people_canc_resv(dbo: Database) -> bool:
    return cboolean(dbo, "AutoRemovePeopleCancResv", DEFAULTS["AutoRemovePeopleCancResv"] == "Yes")

def auto_remove_people_canc_resv_years(dbo: Database) -> int:
    return cint(dbo, "AutoRemovePeopleCRYears", int(DEFAULTS["AutoRemovePeopleCRYears"]))

def auto_remove_hold_days(dbo: Database) -> int:
    return cint(dbo, "AutoRemoveHoldDays", int(DEFAULTS["AutoRemoveHoldDays"]))

def auto_remove_incoming_forms_days(dbo: Database) -> int:
    return cint(dbo, "AutoRemoveIncomingFormsDays", int(DEFAULTS["AutoRemoveIncomingFormsDays"]))

def avid_auth_user(dbo: Database) -> str:
    return cstring(dbo, "AvidAuthUser")

def avid_org_postcode(dbo: Database) -> str:
    return cstring(dbo, "AvidOrgPostcode")

def avid_org_name(dbo: Database) -> str:
    return cstring(dbo, "AvidOrgName")

def avid_org_serial(dbo: Database) -> str:
    return cstring(dbo, "AvidOrgSerial")

def avid_org_password(dbo: Database) -> str:
    return cstring(dbo, "AvidOrgPassword")

def avid_register_overseas(dbo: Database) -> bool:
    return cboolean(dbo, "AvidRegisterOverseas", DEFAULTS["AvidRegisterOverseas"] == "Yes")

def avid_overseas_origin_country(dbo: Database) -> str:
    return cstring(dbo, "AvidOverseasOriginCountry", DEFAULTS["AvidOverseasOriginCountry"])

def avid_reregistration(dbo: Database) -> bool:
    return cboolean(dbo, "AvidReRegistration", DEFAULTS["AvidReRegistration"] == "Yes")

def buddyid_provider_code(dbo: Database) -> str:
    return cstring(dbo, "BuddyIDProviderCode")

def cancel_reserves_on_adoption(dbo: Database) -> bool:
    return cboolean(dbo, "CancelReservesOnAdoption", DEFAULTS["CancelReservesOnAdoption"] == "Yes")

def cardcom_terminalnumber(dbo: Database) -> str:
    return cstring(dbo, "CardcomTerminalNumber")

def cardcom_username(dbo: Database) -> str:
    return cstring(dbo, "CardcomUserName")

def cardcom_documenttype(dbo: Database) -> str:
    return cstring(dbo, "CardcomDocumentType")

def cardcom_usetoken(dbo: Database) -> bool:
    return cboolean(dbo,"CardcomUseToken", DEFAULTS["CardcomUseToken"] == "Yes")

def cardom_maxinstallments(dbo: Database) -> int:
    return cint(dbo,'CardcomMaxInstallments')

def cardcom_successurl(dbo: Database) -> str:
    return cstring(dbo, "CardcomSuccessURL")

def cardcom_errorurl(dbo: Database) -> str:
    return cstring(dbo, "CardcomErrorURL")

def cardcom_paymentmethodmapping(dbo: Database) -> str:
    return cstring(dbo, "CardcomPaymentMethodMapping")

def cardcom_paymenttypemapping(dbo: Database) -> str:
    return cstring(dbo, "CardcomPaymentTypeMapping")

def cardcom_handlenonccpayments(dbo: Database) -> bool:
    return cboolean(dbo, "CardcomHandleNonCCPayments", DEFAULTS["CardcomHandleNonCCPayments"] == "Yes")

def clone_animal_include_logs(dbo: Database) -> bool:
    return cboolean(dbo, "CloneAnimalIncludeLogs", DEFAULTS["CloneAnimalIncludeLogs"] == "Yes")

def coding_format(dbo: Database) -> str:
    return cstring(dbo, "CodingFormat", DEFAULTS["CodingFormat"])

def coding_format_short(dbo: Database) -> str:
    return cstring(dbo, "ShortCodingFormat", DEFAULTS["ShortCodingFormat"])

def cost_source_account(dbo: Database) -> int:
    return cint(dbo, "CostSourceAccount", DEFAULTS["CostSourceAccount"])

def create_cost_trx(dbo: Database) -> bool:
    return cboolean(dbo, "CreateCostTrx")

def create_donation_trx(dbo: Database) -> bool:
    return cboolean(dbo, "CreateDonationTrx")

def currency_code(dbo: Database) -> str:
    return cstring(dbo, "CurrencyCode", DEFAULTS["CurrencyCode"])

def date_brought_in_future_limit(dbo: Database) -> int:
    return cint(dbo, "DateBroughtInFutureLimit", DEFAULTS["DateBroughtInFutureLimit"])

def date_diff_cutoffs(dbo: Database) -> str:
    return cstring(dbo, "DateDiffCutoffs", DEFAULTS["DateDiffCutoffs"])

def dbv(dbo: Database, v: str = None) -> Any:
    if v is None:
        return cstring(dbo, "DBV", "2870")
    else:
        cset_db(dbo, "DBV", v)

def db_lock(dbo: Database) -> bool:
    """
    Locks the database for updates, returns True if the lock was
    successful.
    """
    if asm3.cachedisk.get("db_update_lock", dbo.database): return False
    asm3.cachedisk.put("db_update_lock", dbo.database, "YES", 60 * 5)
    return True

def db_unlock(dbo: Database) -> None:
    """
    Marks the database as unlocked for updates
    """
    asm3.cachedisk.delete("db_update_lock", dbo.database)

def db_view_seq_version(dbo: Database, newval: str = None) -> Any:
    if newval is None:
        return cstring(dbo, "DBViewSeqVersion")
    else:
        cset(dbo, "DBViewSeqVersion", newval)

def default_account_view_period(dbo: Database) -> int:
    return cint(dbo, "DefaultAccountViewPeriod")

def default_breed(dbo: Database) -> int:
    return cint(dbo, "AFDefaultBreed", 1)

def default_broughtinby(dbo: Database) -> int:
    return cint(dbo, "DefaultBroughtInBy", 0)

def default_coattype(dbo: Database) -> int:
    return cint(dbo, "AFDefaultCoatType", 1)

def default_colour(dbo: Database) -> int:
    return cint(dbo, "AFDefaultColour", 1)

def default_daily_boarding_cost(dbo: Database) -> int:
    return cint(dbo, "DefaultDailyBoardingCost", int(DEFAULTS["DefaultDailyBoardingCost"]))

def default_death_reason(dbo: Database) -> int:
    return cint(dbo, "AFDefaultDeathReason", 1)

def default_donation_type(dbo: Database) -> int:
    return cint(dbo, "AFDefaultDonationType", 1)

def default_entry_reason(dbo: Database) -> int:
    return cint(dbo, "AFDefaultEntryReason", 4)

def default_incident(dbo: Database) -> int:
    return cint(dbo, "DefaultIncidentType", 1)

def default_jurisdiction(dbo: Database) -> int:
    return cint(dbo, "DefaultJurisdiction", 1)

def default_location(dbo: Database) -> int:
    return cint(dbo, "AFDefaultLocation", 1)

def default_log_filter(dbo: Database) -> int:
    return cint(dbo, "AFDefaultLogFilter", 0)

def default_media_notes_from_file(dbo: Database) -> bool:
    return cboolean(dbo, "DefaultMediaNotesFromFile", DEFAULTS["DefaultMediaNotesFromFile"] == "Yes")

def default_nonsheltertype(dbo: Database) -> int:
    return cint(dbo, "AFNonShelterType", 40)

def default_payment_method(dbo: Database) -> int:
    return cint(dbo, "AFDefaultPaymentMethod", int(DEFAULTS["AFDefaultPaymentMethod"]))

def default_reservation_status(dbo: Database) -> int:
    return cint(dbo, "AFDefaultReservationStatus", 1)

def default_return_reason(dbo: Database) -> int:
    return cint(dbo, "AFDefaultReturnReason", 4)

def default_size(dbo: Database) -> int:
    return cint(dbo, "AFDefaultSize", 1)

def default_species(dbo: Database) -> int:
    return cint(dbo, "AFDefaultSpecies", 2)

def default_type(dbo: Database) -> int:
    return cint(dbo, "AFDefaultType", 11)

def default_vaccination_type(dbo: Database) -> int:
    return cint(dbo, "AFDefaultVaccinationType", 1)

def diary_complete_on_death(dbo: Database) -> bool:
    return cboolean(dbo, "DiaryCompleteOnDeath", DEFAULTS["DiaryCompleteOnDeath"] == "Yes")

def disable_asilomar(dbo: Database) -> bool:
    return cboolean(dbo, "DisableAsilomar", DEFAULTS["DisableAsilomar"] == "Yes")

def disable_investigation(dbo: Database) -> bool:
    return cboolean(dbo, "DisableInvestigation", DEFAULTS["DisableInvestigation"] == "Yes")

def donation_target_account(dbo: Database) -> int:
    return cint(dbo, "DonationTargetAccount", DEFAULTS["DonationTargetAccount"])

def donation_account_mappings(dbo: Database) -> Dict[str, str]:
    m = {}
    cm = cstring(dbo, "DonationAccountMappings")
    sm = cm.split(",")
    for x in sm:
        if x.find("=") != -1:
            bt = x.split("=")
            donationtypeid = bt[0]
            accountid = bt[1]
            m[donationtypeid] = accountid
    return m

def donation_fee_account(dbo: Database) -> int:
    return cint(dbo, "DonationFeeAccount", DEFAULTS["DonationFeeAccount"])

def donation_trx_override(dbo: Database) -> bool:
    return cboolean(dbo, "DonationTrxOverride", DEFAULTS["DonationTrxOverride"] == "Yes")

def donation_vat_account(dbo: Database) -> int:
    return cint(dbo, "DonationVATAccount", DEFAULTS["DonationVATAccount"])

def dont_show_size(dbo: Database) -> bool:
    return cboolean(dbo, "DontShowSize", DEFAULTS["DontShowSize"] == "Yes")

def email(dbo: Database) -> str:
    return cstring(dbo, "EmailAddress")

def email_diary_notes(dbo: Database) -> bool:
    return cboolean(dbo, "EmailDiaryNotes", DEFAULTS["EmailDiaryNotes"] == "Yes")

def email_diary_on_change(dbo: Database) -> bool:
    return cboolean(dbo, "EmailDiaryOnChange", DEFAULTS["EmailDiaryOnChange"] == "Yes")

def email_diary_on_complete(dbo: Database) -> bool:
    return cboolean(dbo, "EmailDiaryOnComplete", DEFAULTS["EmailDiaryOnComplete"] == "Yes")

def email_empty_reports(dbo: Database) -> bool:
    return cboolean(dbo, "EmailEmptyReports", DEFAULTS["EmailEmptyReports"] == "Yes")

def email_messages(dbo: Database) -> bool:
    return cboolean(dbo, "EmailMessages", DEFAULTS["EmailMessages"] == "Yes")

def flag_change_log(dbo: Database) -> bool:
    return cboolean(dbo, "FlagChangeLog", DEFAULTS["FlagChangeLog"] == "Yes")

def flag_change_log_type(dbo: Database) -> int:
    return cint(dbo, "FlagChangeLogType", DEFAULTS["FlagChangeLogType"])

def foster_on_shelter(dbo: Database) -> bool:
    return cboolean(dbo, "FosterOnShelter", DEFAULTS["FosterOnShelter"] == "Yes")

def fosterer_email_overdue_days(dbo: Database) -> int:
    return cint(dbo, "FostererEmailOverdueDays", DEFAULTS["FostererEmailOverdueDays"])

def fosterer_email_skip_no_medical(dbo: Database) -> bool:
    return cboolean(dbo, "FostererEmailSkipNoMedical", DEFAULTS["FostererEmailSkipNoMedical"] == "Yes")

def fosterer_emails(dbo: Database) -> bool:
    return cboolean(dbo, "FostererEmails", DEFAULTS["FostererEmails"] == "Yes")

def fosterer_emails_reply_to(dbo: Database) -> str:
    return cstring(dbo, "FostererEmailsReplyTo")

def fosterer_emails_msg(dbo: Database) -> str:
    return cstring(dbo, "FostererEmailsMsg")

def foundanimal_search_columns(dbo: Database) -> str:
    return cstring(dbo, "FoundAnimalSearchColumns", DEFAULTS["FoundAnimalSearchColumns"])

def foundanimals_cutoff_days(dbo: Database) -> int:
    return cint(dbo, "FoundAnimalsCutoffDays")

def foundanimals_email(dbo: Database) -> str:
    return cstring(dbo, "FoundAnimalsEmail")

def foundanimals_folder(dbo: Database) -> str:
    return cstring(dbo, "FoundAnimalsFolder")

def future_on_shelter(dbo: Database) -> bool:
    return cboolean(dbo, "FutureOnShelter", DEFAULTS["FutureOnShelter"] == "Yes")

def ftp_host(dbo: Database) -> str:
    return cstring(dbo, "FTPURL")

def ftp_user(dbo: Database) -> str:
    return cstring(dbo, "FTPUser")

def ftp_passive(dbo: Database) -> bool:
    return cboolean(dbo, "FTPPassive", True)

def ftp_password(dbo: Database) -> str:
    return cstring(dbo, "FTPPassword")

def ftp_port(dbo: Database) -> int:
    return cint(dbo, "FTPPort", 21)

def ftp_root(dbo: Database) -> str:
    return cstring(dbo, "FTPRootDirectory")

def generate_document_log(dbo: Database) -> bool:
    return cboolean(dbo, "GenerateDocumentLog", DEFAULTS["GenerateDocumentLog"] == "Yes")

def generate_document_log_type(dbo: Database) -> int:
    return cint(dbo, "GenerateDocumentLogType", DEFAULTS["GenerateDocumentLogType"])

def gdpr_contact_change_log(dbo: Database) -> bool:
    return cboolean(dbo, "GDPRContactChangeLog", DEFAULTS["GDPRContactChangeLog"] == "Yes")

def gdpr_contact_change_log_type(dbo: Database) -> int:
    return cint(dbo, "GDPRContactChangeLogType", DEFAULTS["GDPRContactChangeLogType"])

def geo_provider_override(dbo: Database) -> str:
    return cstring(dbo, "GeoProviderOverride")

def geo_provider_key_override(dbo: Database) -> str:
    return cstring(dbo, "GeoProviderKeyOverride")

def hold_change_log(dbo: Database) -> bool:
    return cboolean(dbo, "HoldChangeLog", DEFAULTS["HoldChangeLog"] == "Yes")

def hold_change_log_type(dbo: Database) -> int:
    return cint(dbo, "HoldChangeLogType", DEFAULTS["HoldChangeLogType"])

def homeagain_user_id(dbo: Database) -> str:
    return cstring(dbo, "HomeAgainUserId")

def homeagain_user_password(dbo: Database) -> str:
    return cstring(dbo, "HomeAgainUserPassword")

def include_incomplete_medical_doc(dbo: Database) -> bool:
    return cboolean(dbo, "IncludeIncompleteMedicalDoc", DEFAULTS["IncludeIncompleteMedicalDoc"] == "Yes")

def include_off_shelter_medical(dbo: Database) -> bool:
    return cboolean(dbo, "IncludeOffShelterMedical", DEFAULTS["IncludeOffShelterMedical"] == "Yes")

def js_injection(dbo: Database) -> str:
    return cstring(dbo, "JSInjection")

def js_window_print(dbo: Database) -> bool:
    return cboolean(dbo, "JSWindowPrint", DEFAULTS["JSWindowPrint"] == "Yes")

def locale(dbo: Database) -> str:
    return cstring(dbo, "Locale", LOCALE)

def location_change_log(dbo: Database) -> bool:
    return cboolean(dbo, "LocationChangeLog", DEFAULTS["LocationChangeLog"] == "Yes")

def location_change_log_type(dbo: Database) -> int:
    return cint(dbo, "LocationChangeLogType", DEFAULTS["LocationChangeLogType"])

def location_filters_enabled(dbo: Database) -> bool:
    return cboolean(dbo, "LocationFiltersEnabled", DEFAULTS["LocationFiltersEnabled"])

def long_term_days(dbo: Database) -> int:
    return cint(dbo, "LongTermDays", DEFAULTS["LongTermDays"])

def maddies_fund_username(dbo: Database) -> str:
    return cstring(dbo, "MaddiesFundUsername")

def maddies_fund_password(dbo: Database) -> str:
    return cstring(dbo, "MaddiesFundPassword")

def mail_merge_max_emails(dbo: Database) -> int:
    return cint(dbo, "MailMergeMaxEmails", int(DEFAULTS["MailMergeMaxEmails"]))

def main_screen_animal_link_mode(dbo: Database) -> str:
    return cstring(dbo, "MainScreenAnimalLinkMode", DEFAULTS["MainScreenAnimalLinkMode"])

def main_screen_animal_link_max(dbo: Database) -> int:
    maxlinks = cint(dbo, "MainScreenAnimalLinkMax", int(DEFAULTS["MainScreenAnimalLinkMax"]))
    maxlinks = min(maxlinks, 1000)
    return maxlinks

def manual_codes(dbo: Database) -> bool:
    return cboolean(dbo, "ManualCodes", DEFAULTS["ManualCodes"] == "Yes")

def map_link_override(dbo: Database) -> str:
    return cstring(dbo, "MapLinkOverride")

def map_provider_override(dbo: Database) -> str:
    return cstring(dbo, "MapProviderOverride")

def map_provider_key_override(dbo: Database) -> str:
    return cstring(dbo, "MapProviderKeyOverride")

def match_species(dbo: Database) -> int:
    return cint(dbo, "MatchSpecies", DEFAULTS["MatchSpecies"])

def match_breed(dbo: Database) -> int:
    return cint(dbo, "MatchBreed", DEFAULTS["MatchBreed"])

def match_age(dbo: Database) -> int:
    return cint(dbo, "MatchAge", DEFAULTS["MatchAge"])

def match_sex(dbo: Database) -> int:
    return cint(dbo, "MatchSex", DEFAULTS["MatchSex"])

def match_area_lost(dbo: Database) -> int:
    return cint(dbo, "MatchAreaLost", DEFAULTS["MatchAreaLost"])

def match_features(dbo: Database) -> int:
    return cint(dbo, "MatchFeatures", DEFAULTS["MatchFeatures"])

def match_microchip(dbo: Database) -> int:
    return cint(dbo, "MatchMicrochip", DEFAULTS["MatchMicrochip"])

def match_postcode(dbo: Database) -> int:
    return cint(dbo, "MatchPostcode", DEFAULTS["MatchPostcode"])

def match_colour(dbo: Database) -> int:
    return cint(dbo, "MatchColour", DEFAULTS["MatchColour"])

def match_include_shelter(dbo: Database) -> bool:
    return cboolean(dbo, "MatchIncludeShelter", True)

def match_within2weeks(dbo: Database) -> int:
    return cint(dbo, "MatchWithin2Weeks", DEFAULTS["MatchWithin2Weeks"])

def match_point_floor(dbo: Database) -> int:
    return cint(dbo, "MatchPointFloor", DEFAULTS["MatchPointFloor"])

def media_allow_jpg(dbo: Database) -> bool:
    return cboolean(dbo, "MediaAllowJPG", DEFAULTS["MediaAllowJPG"] == "Yes")

def media_allow_pdf(dbo: Database) -> bool:
    return cboolean(dbo, "MediaAllowPDF", DEFAULTS["MediaAllowPDF"] == "Yes")

def medical_item_display_limit(dbo: Database) -> int:
    return cint(dbo, "MedicalItemDisplayLimit", DEFAULTS["MedicalItemDisplayLimit"])

def medical_precreate_treatments(dbo: Database) -> bool:
    return cboolean(dbo, "MedicalPrecreateTreatments", DEFAULTS["MedicalPrecreateTreatments"] == "Yes")

def microchip_register_movements(dbo: Database) -> str:
    return cstring(dbo, "MicrochipRegisterMovements", DEFAULTS["MicrochipRegisterMovements"])

def microchip_register_from(dbo: Database) -> str:
    return cstring(dbo, "MicrochipRegisterFrom", "")

def movement_donations_default_due(dbo: Database) -> bool:
    return cboolean(dbo, "MovementDonationsDefaultDue", DEFAULTS["MovementDonationsDefaultDue"] == "Yes")

def movement_person_only_reserves(dbo: Database) -> bool:
    return cboolean(dbo, "MovementPersonOnlyReserves", DEFAULTS["MovementPersonOnlyReserves"] == "Yes")

def multi_site_enabled(dbo: Database) -> bool:
    return cboolean(dbo, "MultiSiteEnabled", DEFAULTS["MultiSiteEnabled"] == "Yes")

def non_shelter_type(dbo: Database) -> int:
    return cint(dbo, "AFNonShelterType", 40)

def onlineform_delete_on_process(dbo: Database) -> bool:
    return cboolean(dbo, "OnlineFormDeleteOnProcess", DEFAULTS["OnlineFormDeleteOnProcess"] == "Yes")

def onlineform_spam_honeytrap(dbo: Database) -> bool:
    return cboolean(dbo, "OnlineFormSpamHoneyTrap", DEFAULTS["OnlineFormSpamHoneyTrap"] == "Yes")

def onlineform_spam_ua_check(dbo: Database) -> bool:
    return cboolean(dbo, "OnlineFormSpamUACheck", DEFAULTS["OnlineFormSpamUACheck"] == "Yes")

def onlineform_spam_firstname_mixcase(dbo: Database) -> bool:
    return cboolean(dbo, "OnlineFormSpamFirstnameMixCase", DEFAULTS["OnlineFormSpamFirstnameMixCase"] == "Yes")

def organisation(dbo: Database) -> str:
    return cstring(dbo, "Organisation", DEFAULTS["Organisation"])

def organisation_address(dbo: Database) -> str:
    return cstring(dbo, "OrganisationAddress", DEFAULTS["OrganisationAddress"])

def organisation_town(dbo: Database) -> str:
    return cstring(dbo, "OrganisationTown")

def organisation_county(dbo: Database) -> str:
    return cstring(dbo, "OrganisationCounty")

def organisation_postcode(dbo: Database) -> str:
    return cstring(dbo, "OrganisationPostcode")

def organisation_country(dbo: Database) -> str:
    return cstring(dbo, "OrganisationCountry")

def organisation_telephone(dbo: Database) -> str:
    return cstring(dbo, "OrganisationTelephone", DEFAULTS["OrganisationTelephone"])

def osm_map_tiles_override(dbo: Database) -> str:
    return cstring(dbo, "OSMMapTilesOverride")

def owner_name_couple_format(dbo: Database) -> str:
    return cstring(dbo, "OwnerNameCoupleFormat", DEFAULTS["OwnerNameCoupleFormat"])

def owner_name_married_format(dbo: Database) -> str:
    return cstring(dbo, "OwnerNameMarriedFormat", DEFAULTS["OwnerNameMarriedFormat"])

def owner_name_format(dbo: Database) -> str:
    return cstring(dbo, "OwnerNameFormat", DEFAULTS["OwnerNameFormat"])

def paypal_email(dbo: Database) -> str:
    return cstring(dbo, "PayPalEmail")

def payment_return_url(dbo: Database) -> str:
    return cstring(dbo, "PaymentReturnUrl")

def petrescue_adoptable_in(dbo: Database) -> str:
    return cstring(dbo, "PetRescueAdoptableIn")

def petrescue_all_desexed(dbo: Database) -> bool:
    return cboolean(dbo, "PetRescueAllDesexed")

def petrescue_all_microchips(dbo: Database) -> bool:
    return cboolean(dbo, "PetRescueAllMicrochips")

def petrescue_email(dbo: Database) -> str:
    return cstring(dbo, "PetRescueEmail")

def petrescue_phone_number(dbo: Database) -> str:
    return cstring(dbo, "PetRescuePhoneNumber")

def petrescue_phone_type(dbo: Database) -> str:
    return cstring(dbo, "PetRescuePhoneType")

def petrescue_token(dbo: Database) -> str:
    return cstring(dbo, "PetRescueToken")

def petrescue_nsw_rehoming_org_id(dbo: Database) -> str:
    return cstring(dbo, "PetRescueNSWRehomingOrgID")

def petrescue_breederid(dbo: Database) -> str:
    return cstring(dbo, "PetRescueBreederID")

def petrescue_vic_sourcenumber(dbo: Database) -> str:
    return cstring(dbo, "PetRescueVICSourceNumber")

def petrescue_vic_picnumber(dbo: Database) -> str:
    return cstring(dbo, "PetRescueVICPICNumber")

def petrescue_use_coordinator(dbo: Database) -> bool:
    return cboolean(dbo, "PetRescueUseCoordinator")

def pdf_inline(dbo: Database) -> bool:
    return cboolean(dbo, "PDFInline", DEFAULTS["PDFInline"] == "Yes")

def pdf_zoom(dbo: Database) -> int:
    return cint(dbo, "PDFZoom", DEFAULTS["PDFZoom"])

def person_search_columns(dbo: Database) -> str:
    return cstring(dbo, "OwnerSearchColumns", DEFAULTS["OwnerSearchColumns"])

def event_excludeanimalswithflags(dbo: Database) -> str:
    return cstring(dbo, "EventExcludeAnimalsWithFlags", DEFAULTS["EventExcludeAnimalsWithFlags"])

def event_excludeanimalswithlocations(dbo: Database) -> str:
    return cstring(dbo, "EventExcludeAnimalsInLocations", DEFAULTS["EventExcludeAnimalsInLocations"])

def event_search_columns(dbo: Database) -> str:
    return cstring(dbo, "EventSearchColumns", DEFAULTS["EventSearchColumns"])

def incident_search_columns(dbo: Database) -> str:
    return cstring(dbo, "IncidentSearchColumns", DEFAULTS["IncidentSearchColumns"])

def lostanimal_search_columns(dbo: Database) -> str:
    return cstring(dbo, "LostAnimalSearchColumns", DEFAULTS["LostAnimalSearchColumns"])

def petcademy_token(dbo: Database) -> str:
    return cstring(dbo, "PetcademyToken")

def petfinder_age_bands(dbo: Database) -> str:
    return cstring(dbo, "PetFinderAgeBands")

def petfinder_hide_unaltered(dbo: Database) -> bool:
    return cboolean(dbo, "PetFinderHideUnaltered", False)

def petfinder_send_adopted(dbo: Database) -> bool:
    return cboolean(dbo, "PetFinderSendAdopted", False)

def petfinder_send_holds(dbo: Database) -> bool:
    return cboolean(dbo, "PetFinderSendHolds", False)

def petfinder_send_strays(dbo: Database) -> bool:
    return cboolean(dbo, "PetFinderSendStrays", False)

def petfinder_user(dbo: Database) -> str:
    return cstring(dbo, "PetFinderFTPUser")

def petfinder_password(dbo: Database) -> str:
    return cstring(dbo, "PetFinderFTPPassword")

def helpinglostpets_orgid(dbo: Database) -> str:
    return cstring(dbo, "HelpingLostPetsOrgID")

def helpinglostpets_user(dbo: Database) -> str:
    return cstring(dbo, "HelpingLostPetsFTPUser")

def helpinglostpets_password(dbo: Database) -> str:
    return cstring(dbo, "HelpingLostPetsFTPPassword")

def helpinglostpets_postal(dbo: Database) -> str:
    return cstring(dbo, "HelpingLostPetsPostal")

def petlink_cutoff_days(dbo: Database) -> int:
    return cint(dbo, "PetLinkCutoffDays")

def petlink_email(dbo: Database) -> str:
    return cstring(dbo, "PetLinkEmail")

def petlink_owner_email(dbo: Database) -> str:
    return cstring(dbo, "PetLinkOwnerEmail")

def petlink_password(dbo: Database) -> str:
    return cstring(dbo, "PetLinkPassword")

def petrescue_user(dbo: Database) -> str:
    return cstring(dbo, "PetRescueFTPUser")

def petrescue_password(dbo: Database) -> str:
    return cstring(dbo, "PetRescueFTPPassword")

def petrescue_location_regionid(dbo: Database) -> bool:
    return cboolean(dbo, "PetRescueLocationRegionID", "No")

def pets911_user(dbo: Database) -> str:
    return cstring(dbo, "Pets911FTPUser")

def pets911_password(dbo: Database) -> str:
    return cstring(dbo, "Pets911FTPPassword")

def pets911_source(dbo: Database) -> str:
    return cstring(dbo, "Pets911FTPSourceID")

def petslocated_customerid(dbo: Database) -> str:
    return cstring(dbo, "PetsLocatedCustomerID")

def petslocated_includeshelter(dbo: Database) -> bool:
    return cboolean(dbo, "PetsLocatedIncludeShelter", DEFAULTS["PetsLocatedIncludeShelter"] == "Yes")

def petslocated_animalflag(dbo: Database) -> str:
    return cstring(dbo, "PetsLocatedAnimalFlag", DEFAULTS["PetsLocatedAnimalFlag"])

def publisher_use_comments(dbo: Database) -> bool:
    return cboolean(dbo, "PublisherUseComments", DEFAULTS["PublisherUseComments"] == "Yes")

def record_search_limit(dbo: Database) -> int:
    return cint(dbo, "RecordSearchLimit", DEFAULTS["RecordSearchLimit"])

def return_fosters_on_adoption(dbo: Database) -> bool:
    return cboolean(dbo, "ReturnFostersOnAdoption", DEFAULTS["ReturnFostersOnAdoption"] == "Yes")

def return_fosters_on_transfer(dbo: Database) -> bool:
    return cboolean(dbo, "ReturnFostersOnTransfer", DEFAULTS["ReturnFostersOnTransfer"] == "Yes")

def return_retailer_on_adoption(dbo: Database) -> bool:
    return cboolean(dbo, "ReturnRetailerOnAdoption", DEFAULTS["ReturnRetailerOnAdoption"] == "Yes")

def smarttag_accountid(dbo: Database) -> str:
    return cstring(dbo, "SmartTagFTPUser")

def publisher_presets(dbo: Database) -> str:
    return cstring(dbo, "PublisherPresets", DEFAULTS["PublisherPresets"])

def publisher_sub24_frequency(dbo: Database) -> int:
    return cint(dbo, "PublisherSub24Frequency", DEFAULTS["PublisherSub24Frequency"])

def publishers_enabled(dbo: Database) -> str:
    return cstring(dbo, "PublishersEnabled")

def publishers_enabled_disable(dbo: Database, publishertodisable: str) -> None:
    """ Disables a publisher by removing it from the PublishersEnabled config """
    pe = cstring(dbo, "PublishersEnabled")
    pe = pe.replace(" " + publishertodisable, "")
    cset(dbo, "PublishersEnabled", pe)

def quicklinks_id(dbo: Database, newval = None) -> Any:
    if newval is None:
        return cstring(dbo, "QuicklinksID", DEFAULTS["QuicklinksID"])
    else:
        cset(dbo, "QuicklinksID", newval)

def report_toolbar(dbo: Database) -> bool:
    return cboolean(dbo, "ReportToolbar", DEFAULTS["ReportToolbar"] == "Yes")

def rescuegroups_user(dbo: Database) -> str:
    return cstring(dbo, "RescueGroupsFTPUser")

def rescuegroups_password(dbo: Database) -> str:
    return cstring(dbo, "RescueGroupsFTPPassword")

def retailer_on_shelter(dbo: Database) -> bool:
    return cboolean(dbo, "RetailerOnShelter", DEFAULTS["RetailerOnShelter"] == "Yes")

def sac_stray_category(dbo: Database) -> str:
    return cstring(dbo, "SACStrayCategory", DEFAULTS["SACStrayCategory"])

def sac_surrender_category(dbo: Database) -> str:
    return cstring(dbo, "SACSurrenderCategory", DEFAULTS["SACSurrenderCategory"])

def sac_tnr_category(dbo: Database) -> str:
    return cstring(dbo, "SACTNRCategory", DEFAULTS["SACTNRCategory"])

def savourlife_token(dbo: Database) -> str:
    return cstring(dbo, "SavourLifeToken")

def savourlife_all_microchips(dbo: Database) -> bool:
    return cboolean(dbo, "SavourLifeAllMicrochips")

def savourlife_interstate(dbo: Database) -> bool:
    return cboolean(dbo, "SavourLifeInterstate")

def savourlife_radius(dbo: Database) -> int:
    return cint(dbo, "SavourLifeRadius")

def scale_pdfs(dbo: Database) -> bool:
    return cboolean(dbo, "ScalePDFs", DEFAULTS["ScalePDFs"] == "Yes")

def search_sort(dbo: Database) -> int:
    return cint(dbo, "SearchSort", 3)

def service_enabled(dbo: Database) -> bool:
    return cboolean(dbo, "ServiceEnabled", DEFAULTS["ServiceEnabled"] == "Yes")

def service_auth_enabled(dbo: Database) -> bool:
    return cboolean(dbo, "ServiceAuthEnabled", DEFAULTS["ServiceAuthEnabled"] == "Yes")

def show_first_time_screen(dbo: Database, change = False, newvalue = False) -> Any:
    if not change:
        return cboolean(dbo, "ShowFirstTime", DEFAULTS["ShowFirstTime"] == "Yes")
    else:
        cset(dbo, "ShowFirstTime", newvalue and "Yes" or "No")

def show_alerts_home_page(dbo: Database) -> bool:
    return cboolean(dbo, "ShowAlertsHomePage", DEFAULTS["ShowAlertsHomePage"] == "Yes")

def show_cost_paid(dbo: Database) -> bool:
    return cboolean(dbo, "ShowCostPaid", DEFAULTS["ShowCostPaid"] == "Yes")

def show_gdpr_contact_optin(dbo: Database) -> bool:
    return cboolean(dbo, "ShowGDPRContactOptIn", DEFAULTS["ShowGDPRContactOptIn"] == "Yes")

def show_lat_long(dbo: Database) -> bool:
    return cboolean(dbo, "ShowLatLong", DEFAULTS["ShowLatLong"] == "Yes")

def show_overview_home_page(dbo: Database) -> str:
    return cstring(dbo, "ShowOverviewHomePage", DEFAULTS["ShowOverviewHomePage"])

def show_stats_home_page(dbo: Database) -> str:
    return cstring(dbo, "ShowStatsHomePage", DEFAULTS["ShowStatsHomePage"])

def show_timeline_home_page(dbo: Database) -> bool:
    return cboolean(dbo, "ShowTimelineHomePage", DEFAULTS["ShowTimelineHomePage"] == "Yes")

def show_weight_in_lbs(dbo: Database) -> bool:
    return cboolean(dbo, "ShowWeightInLbs", DEFAULTS["ShowWeightInLbs"] == "Yes")

def show_weight_in_lbs_fraction(dbo: Database) -> bool:
    return cboolean(dbo, "ShowWeightInLbsFraction", DEFAULTS["ShowWeightInLbsFraction"] == "Yes")

def show_weight_units_in_log(dbo: Database) -> bool:
    return cboolean(dbo, "ShowWeightUnitsInLog", DEFAULTS["ShowWeightUnitsInLog"] == "Yes")

def signpad_ids(dbo: Database, user, newval = None) -> Any:
    if newval is None:
        return cstring(dbo, "SignpadIds%s" % user, "")
    else:
        cset(dbo, "SignpadIds%s" % user, newval)

def smdb_locked(dbo: Database) -> bool:
    return cboolean(dbo, "SMDBLocked")

def smtp_override(dbo: Database) -> bool:
    return cboolean(dbo, "SMTPOverride", DEFAULTS["SMTPOverride"] == "Yes")

def smtp_server(dbo: Database) -> str:
    return cstring(dbo, "SMTPServer")

def smtp_port(dbo: Database) -> int:
    return cint(dbo, "SMTPPort", DEFAULTS["SMTPPort"])

def smtp_username(dbo: Database) -> str:
    return cstring(dbo, "SMTPUsername")

def smtp_password(dbo: Database) -> str:
    return cstring(dbo, "SMTPPassword")

def smtp_use_tls(dbo: Database) -> bool:
    return cboolean(dbo, "SMTPUseTLS")

def softrelease_on_shelter(dbo: Database) -> bool:
    return cboolean(dbo, "SoftReleaseOnShelter", DEFAULTS["SoftReleaseOnShelter"] == "Yes")

def stripe_key(dbo: Database) -> str:
    return cstring(dbo, "StripeKey")

def stripe_secret_key(dbo: Database) -> str:
    return cstring(dbo, "StripeSecretKey")

def system_log_type(dbo: Database) -> int:
    return cint(dbo, "SystemLogType", DEFAULTS["SystemLogType"])

def use_short_shelter_codes(dbo: Database) -> bool:
    return cboolean(dbo, "UseShortShelterCodes")

def third_party_publisher_sig(dbo: Database) -> str:
    return cstring(dbo, "TPPublisherSig")

def templates_for_nonshelter(dbo: Database) -> bool:
    return cboolean(dbo, "TemplatesForNonShelter", DEFAULTS["TemplatesForNonShelter"] == "Yes")

def thumbnail_size(dbo: Database) -> str:
    return cstring(dbo, "ThumbnailSize", DEFAULTS["ThumbnailSize"])

def timezone(dbo: Database) -> float:
    return cfloat(dbo, "Timezone", TIMEZONE)

def timezone_dst(dbo: Database) -> bool:
    return cboolean(dbo, "TimezoneDST", DEFAULTS["TimezoneDST"])

def trial_adoptions(dbo: Database) -> bool:
    return cboolean(dbo, "TrialAdoptions", DEFAULTS["TrialAdoptions"] == "Yes")

def trial_on_shelter(dbo: Database) -> bool:
    return cboolean(dbo, "TrialOnShelter", DEFAULTS["TrialOnShelter"] == "Yes")

def unique_licence_numbers(dbo: Database) -> bool:
    return cboolean(dbo, "UniqueLicenceNumbers", DEFAULTS["UniqueLicenceNumbers"] == "Yes")

def update_animal_test_fields(dbo: Database) -> bool:
    return cboolean(dbo, "UpdateAnimalTestFields", DEFAULTS["UpdateAnimalTestFields"] == "Yes")

def vetenvoy_user_id(dbo: Database) -> str:
    return cstring(dbo, "VetEnvoyUserId")

def vetenvoy_user_password(dbo: Database) -> str:
    return cstring(dbo, "VetEnvoyUserPassword")

def vetenvoy_homeagain_enabled(dbo: Database) -> bool:
    return cboolean(dbo, "VetEnvoyHomeAgainEnabled", DEFAULTS["VetEnvoyHomeAgainEnabled"] == "Yes")

def vetenvoy_akcreunite_enabled(dbo: Database) -> bool:
    return cboolean(dbo, "VetEnvoyAKCReuniteEnabled", DEFAULTS["VetEnvoyAKCReuniteEnabled"] == "Yes")

def waiting_list_default_urgency(dbo: Database) -> int:
    return cint(dbo, "WaitingListDefaultUrgency", DEFAULTS["WaitingListDefaultUrgency"])

def waiting_list_rank_by_species(dbo: Database) -> bool:
    return cboolean(dbo, "WaitingListRankBySpecies")

def waiting_list_highlights(dbo: Database, newhighlights: str = "READ") -> Any:
    if newhighlights == "READ":
        return cstring(dbo, "WaitingListHighlights")
    else:
        cset(dbo, "WaitingListHighlights", newhighlights + " ")

def waiting_list_view_columns(dbo: Database) -> str:
    return cstring(dbo, "WaitingListViewColumns", DEFAULTS["WaitingListViewColumns"])

def waiting_list_urgency_update_period(dbo: Database) -> int:
    return cint(dbo, "WaitingListUrgencyUpdatePeriod", 14)

def warn_no_homecheck(dbo: Database) -> bool:
    return cboolean(dbo, "WarnNoHomeCheck", DEFAULTS["WarnNoHomeCheck"] == "Yes")

def watermark_x_offset(dbo: Database) -> int:
    return cint(dbo, "WatermarkXOffset", DEFAULTS["WatermarkXOffset"])

def watermark_y_offset(dbo: Database) -> int:
    return cint(dbo, "WatermarkYOffset", DEFAULTS["WatermarkYOffset"])

def watermark_font_stroke(dbo: Database) -> int:
    return cint(dbo, "WatermarkFontStroke", DEFAULTS["WatermarkFontStroke"])

def watermark_font_fill_color(dbo: Database) -> str:
    return cstring(dbo, "WatermarkFontFillColor", DEFAULTS["WatermarkFontFillColor"])

def watermark_font_shadow_color(dbo: Database) -> str:
    return cstring(dbo, "WatermarkFontShadowColor", DEFAULTS["WatermarkFontShadowColor"])

def watermark_font_offset(dbo: Database) -> int:
    return cint(dbo, "WatermarkFontOffset", DEFAULTS["WatermarkFontOffset"])

def watermark_font_file(dbo: Database) -> str:
    return cstring(dbo, "WatermarkFontFile", DEFAULTS["WatermarkFontFile"])

def watermark_font_max_size(dbo: Database) -> int:
    return cint(dbo, "WatermarkFontMaxSize", DEFAULTS["WatermarkFontMaxSize"])

def watermark_get_valid_font_files() -> str:
    basePath = WATERMARK_FONT_BASEDIRECTORY
    fileList = []
    for root,_,files in os.walk(basePath):
        for f in files:
            if f.endswith('.ttf'):
                fileList.append(os.path.join(root, f)[len(basePath):])
    return sorted(fileList)

def weight_change_log(dbo: Database) -> bool:
    return cboolean(dbo, "WeightChangeLog", DEFAULTS["WeightChangeLog"] == "Yes")

def weight_change_log_type(dbo: Database) -> int:
    return cint(dbo, "WeightChangeLogType", DEFAULTS["WeightChangeLogType"])


