import asm3.al
import asm3.audit
import asm3.cachedisk
import asm3.i18n

import os

from asm3.sitedefs import LOCALE, TIMEZONE, WATERMARK_FONT_BASEDIRECTORY

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
    "AutoRemoveDocumentMedia": "No",
    "AutoRemoveDMYears": "0",
    "AutoRemoveHoldDays": "0",
    "AutoRemoveIncomingFormsDays": "28",
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
    "LongTermMonths": "6",
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
    "JSWindowPrint": "Yes",
    "OnlineFormSpamHoneyTrap": "Yes",
    "OnlineFormSpamUACheck": "No",
    "OnlineFormSpamFirstnameMixCase": "Yes",
    "Organisation": "Organisation",
    "OrganisationAddress": "Address",
    "OrganisationTelephone": "Telephone",
    "OwnerAddressCheck": "Yes",
    "OwnerNameCheck": "Yes",
    "OwnerNameFormat": "{ownertitle} {ownerforenames} {ownersurname}",
    "OwnerNameCoupleFormat": "{ownername1} & {ownername2}",
    "OwnerSearchColumns": "OwnerCode,OwnerName,OwnerSurname," \
        "MembershipNumber,AdditionalFlags,OwnerAddress," \
        "OwnerTown,OwnerCounty,OwnerPostcode,HomeTelephone,WorkTelephone," \
        "MobileTelephone,EmailAddress",
    "PetsLocatedIncludeShelter": "No",
    "PetsLocatedAnimalFlag": "",
    "PicturesInBooks": "Yes",
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

def cstring(dbo, key, default = ""):
    cmap = get_map(dbo)
    if key not in cmap:
        return default
    return cmap[key]

def cboolean(dbo, key, default = False):
    defstring = "No"
    if default: defstring = "Yes"
    v = cstring(dbo, key, defstring)
    return v == "Yes" or v == "True"

def cint(dbo, key, default = 0):
    defstring = str(default)
    v = cstring(dbo, key, defstring)
    try:
        return int(v)
    except:
        return int(0)

def cfloat(dbo, key, default = 0.0):
    defstring = str(default)
    v = cstring(dbo, key, defstring)
    try:
        return float(v)
    except:
        return float(0)

def cset(dbo, key, value = "", ignoreDBLock = False, sanitiseXSS = True, invalidateConfigCache = True):
    """
    Update a configuration item in the table.
    """
    dbo.execute("DELETE FROM configuration WHERE ItemName LIKE ?", [key], override_lock=ignoreDBLock)
    if sanitiseXSS: value = dbo.escape_xss(value)
    dbo.execute("INSERT INTO configuration (ItemName, ItemValue) VALUES (?, ?)", (key, value), override_lock=ignoreDBLock)
    if invalidateConfigCache: invalidate_config_cache(dbo)

def cset_db(dbo, key, value = ""):
    """
    Updates a configuration entry that could take place during a
    database update, so needs to ignore the locked flag.
    """
    cset(dbo, key, value, ignoreDBLock = True)

def csave(dbo, username, post):
    """
    Takes configuration data passed as a web post and saves it to the database.
    """
    def valid_code(s):
        """
        Returns True if s has a valid code portion in it
        """
        VALID_CODES = ("OO", "OOO", "XX", "XXX", "NN", "NNN", "UUUU", "UUUUUUUUUU")
        for v in VALID_CODES:
            if s.find(v) != -1:
                return True
        return False

    cmap = get_map(dbo)

    def put(k, v, sanitiseXSS = True):
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

def get_map(dbo):
    """ Returns a map of the config items, using a read-through cache to save database calls """
    cmap = asm3.cachedisk.get("config", dbo.database, expectedtype=dict)
    if cmap is None:
        rows = dbo.query("SELECT ItemName, ItemValue FROM configuration ORDER BY ItemName")
        cmap = DEFAULTS.copy()
        for r in rows:
            cmap[r.itemname] = r.itemvalue
        asm3.cachedisk.put("config", dbo.database, cmap, 3600) # one hour cache means direct database updates show up eventually
    return cmap

def invalidate_config_cache(dbo):
    asm3.cachedisk.delete("config", dbo.database)

def account_period_totals(dbo):
    return cboolean(dbo, "AccountPeriodTotals")

def accounting_period(dbo):
    return cstring(dbo, "AccountingPeriod")

def add_animals_show_time_brought_in(dbo):
    return cboolean(dbo, "AddAnimalsShowTimeBroughtIn", DEFAULTS["AddAnimalsShowTimeBroughtIn"] == "Yes")

def adoptapet_user(dbo):
    return cstring(dbo, "SaveAPetFTPUser")

def adoptapet_password(dbo):
    return cstring(dbo, "SaveAPetFTPPassword")

def adoption_checkout_donation_msg(dbo):
    return cstring(dbo, "AdoptionCheckoutDonationMsg", DEFAULTS["AdoptionCheckoutDonationMsg"])

def adoption_checkout_donationid(dbo):
    return cint(dbo, "AdoptionCheckoutDonationID")

def adoption_checkout_donation_tiers(dbo):
    return cstring(dbo, "AdoptionCheckoutDonationTiers", DEFAULTS["AdoptionCheckoutDonationTiers"])

def adoption_checkout_feeid(dbo):
    return cint(dbo, "AdoptionCheckoutFeeID")

def adoption_checkout_payment_method(dbo):
    return cint(dbo, "AdoptionCheckoutPaymentMethod")

def adoption_checkout_processor(dbo):
    return cstring(dbo, "AdoptionCheckoutProcessor")

def adoption_checkout_templateid(dbo):
    return cint(dbo, "AdoptionCheckoutTemplateID")

def advanced_find_animal(dbo):
    return cboolean(dbo, "AdvancedFindAnimal")

def advanced_find_animal_on_shelter(dbo):
    return cboolean(dbo, "AdvancedFindAnimalOnShelter", DEFAULTS["AdvancedFindAnimalOnShelter"] == "Yes")

def age_group_bands(dbo):
    bands = []
    for i in range(1, 9):
        groupname = cstring(dbo, "AgeGroup%dName" % i)
        if groupname.strip() != "":
            bands.append( ( groupname, cfloat(dbo, "AgeGroup%d" % i) ) )
    return bands

def age_group_for_name(dbo, name):
    for group, years in age_group_bands(dbo):
        if group == name:
            return years
    return 0

def age_groups(dbo):
    groups = []
    for i in range(1, 9):
        groupname = cstring(dbo, "AgeGroup%dName" % i)
        if groupname.strip() != "":
            groups.append(groupname)
    return groups

def age_group(dbo, band):
    return cfloat(dbo, "AgeGroup%d" % band)

def age_group_name(dbo, band):
    return cstring(dbo, "AgeGroup%dName" % band)

def akc_enrollmentsourceid(dbo):
    return cstring(dbo, "AKCEnrollmentSourceID")

def akc_register_all(dbo):
    return cboolean(dbo, "AKCRegisterAll")

def alert_species_microchip(dbo):
    s = cstring(dbo, "AlertSpeciesMicrochip", DEFAULTS["AlertSpeciesMicrochip"])
    if s == "": return "0" # Always return something due to IN clauses of queries
    return s

def alert_species_never_vacc(dbo):
    s = cstring(dbo, "AlertSpeciesNeverVacc", DEFAULTS["AlertSpeciesNeverVacc"])
    if s == "": return "0" # Always return something due to IN clauses of queries
    return s

def alert_species_neuter(dbo):
    s = cstring(dbo, "AlertSpeciesNeuter", DEFAULTS["AlertSpeciesNeuter"])
    if s == "": return "0" # Always return something due to IN clauses of queries
    return s

def alert_species_rabies(dbo):
    s = cstring(dbo, "AlertSpeciesRabies", DEFAULTS["AlertSpeciesRabies"])
    if s == "": return "0" # Always return something due to IN clauses of queries
    return s

def all_diary_home_page(dbo):
    return cboolean(dbo, "AllDiaryHomePage")

def allow_duplicate_microchip(dbo):
    return cboolean(dbo, "AllowDuplicateMicrochip", DEFAULTS["AllowDuplicateMicrochip"] == "Yes")

def allow_odt_document_templates(dbo):
    return cboolean(dbo, "AllowODTDocumentTemplates", DEFAULTS["AllowODTDocumentTemplates"] == "Yes")

def anibase_practice_id(dbo):
    return cstring(dbo, "AnibasePracticeID")

def anibase_pin_no(dbo):
    return cstring(dbo, "AnibasePinNo")

def animal_figures_split_entryreason(dbo):
    return cboolean(dbo, "AnimalFiguresSplitEntryReason", DEFAULTS["AnimalFiguresSplitEntryReason"] == "Yes")

def animal_search_columns(dbo):
    return cstring(dbo, "SearchColumns", DEFAULTS["SearchColumns"])

def annual_figures_show_babies(dbo):
    return cboolean(dbo, "AnnualFiguresShowBabies", DEFAULTS["AnnualFiguresShowBabies"] == "Yes")

def annual_figures_show_babies_type(dbo):
    return cboolean(dbo, "AnnualFiguresShowBabiesType", DEFAULTS["AnnualFiguresShowBabiesType"] == "Yes")

def annual_figures_baby_months(dbo):
    return cint(dbo, "AnnualFiguresBabyMonths", int(DEFAULTS["AnnualFiguresBabyMonths"]))

def annual_figures_split_adoptions(dbo):
    return cboolean(dbo, "AnnualFiguresSplitAdoptions", DEFAULTS["AnnualFiguresSplitAdoptions"] == "Yes")

def anonymise_adopters(dbo):
    return cboolean(dbo, "AnonymiseAdopters", DEFAULTS["AnonymiseAdopters"] == "Yes")

def anonymise_personal_data(dbo):
    return cboolean(dbo, "AnonymisePersonalData", DEFAULTS["AnonymisePersonalData"] == "Yes")

def anonymise_after_years(dbo):
    return cint(dbo, "AnonymiseAfterYears", DEFAULTS["AnonymiseAfterYears"])

def audit_on_view_record(dbo):
    return cboolean(dbo, "AuditOnViewRecord", DEFAULTS["AuditOnViewRecord"] == "Yes")

def audit_on_view_report(dbo):
    return cboolean(dbo, "AuditOnViewReport", DEFAULTS["AuditOnViewReport"] == "Yes")

def audit_on_send_email(dbo):
    return cboolean(dbo, "AuditOnSendEmail", DEFAULTS["AuditOnSendEmail"] == "Yes")

def auto_cancel_reserves_days(dbo):
    return cint(dbo, "AutoCancelReservesDays", int(DEFAULTS["AutoCancelReservesDays"]))

def auto_cancel_hold_days(dbo):
    return cint(dbo, "AutoCancelHoldDays", int(DEFAULTS["AutoCancelHoldDays"]))

def auto_default_vacc_batch(dbo):
    return cboolean(dbo, "AutoDefaultVaccBatch", DEFAULTS["AutoDefaultVaccBatch"] == "Yes")

def auto_hash_processed_forms(dbo):
    return cboolean(dbo, "AutoHashProcessedForms", DEFAULTS["AutoHashProcessedForms"] == "Yes")

def auto_insurance_next(dbo, newins = 0):
    if newins == 0:
        return cint(dbo, "AutoInsuranceNext")
    else:
        cset(dbo, "AutoInsuranceNext", str(newins))

def auto_media_notes(dbo):
    return cboolean(dbo, "AutoMediaNotes")

def auto_new_images_not_for_publish(dbo):
    return cboolean(dbo, "AutoNewImagesNotForPublish", DEFAULTS["AutoNewImagesNotForPublish"] == "Yes")

def auto_not_for_adoption(dbo):
    return cboolean(dbo, "AutoNotForAdoption", DEFAULTS["AutoNotForAdoption"] == "Yes")

def auto_remove_document_media(dbo):
    return cboolean(dbo, "AutoRemoveDocumentMedia", DEFAULTS["AutoRemoveDocumentMedia"] == "Yes")

def auto_remove_document_media_years(dbo):
    return cint(dbo, "AutoRemoveDMYears", int(DEFAULTS["AutoRemoveDMYears"]))

def auto_remove_hold_days(dbo):
    return cint(dbo, "AutoRemoveHoldDays", int(DEFAULTS["AutoRemoveHoldDays"]))

def auto_remove_incoming_forms_days(dbo):
    return cint(dbo, "AutoRemoveIncomingFormsDays", int(DEFAULTS["AutoRemoveIncomingFormsDays"]))

def avid_auth_user(dbo):
    return cstring(dbo, "AvidAuthUser")

def avid_org_postcode(dbo):
    return cstring(dbo, "AvidOrgPostcode")

def avid_org_name(dbo):
    return cstring(dbo, "AvidOrgName")

def avid_org_serial(dbo):
    return cstring(dbo, "AvidOrgSerial")

def avid_org_password(dbo):
    return cstring(dbo, "AvidOrgPassword")

def avid_register_overseas(dbo):
    return cboolean(dbo, "AvidRegisterOverseas", DEFAULTS["AvidRegisterOverseas"] == "Yes")

def avid_overseas_origin_country(dbo):
    return cstring(dbo, "AvidOverseasOriginCountry", DEFAULTS["AvidOverseasOriginCountry"])

def avid_reregistration(dbo):
    return cboolean(dbo, "AvidReRegistration", DEFAULTS["AvidReRegistration"] == "Yes")

def cancel_reserves_on_adoption(dbo):
    return cboolean(dbo, "CancelReservesOnAdoption", DEFAULTS["CancelReservesOnAdoption"] == "Yes")

def cardcom_terminalnumber(dbo):
    return cstring(dbo, "CardcomTerminalNumber")

def cardcom_username(dbo):
    return cstring(dbo, "CardcomUserName")

def cardcom_documenttype(dbo):
    return cstring(dbo, "CardcomDocumentType")

def cardcom_usetoken(dbo):
    return cboolean(dbo,"CardcomUseToken", DEFAULTS["CardcomUseToken"] == "Yes")

def cardom_maxinstallments(dbo):
    return cint(dbo,'CardcomMaxInstallments')

def cardcom_successurl(dbo):
    return cstring(dbo, "CardcomSuccessURL")

def cardcom_errorurl(dbo):
    return cstring(dbo, "CardcomErrorURL")

def cardcom_paymentmethodmapping(dbo):
    return cstring(dbo, "CardcomPaymentMethodMapping")

def cardcom_paymenttypemapping(dbo):
    return cstring(dbo, "CardcomPaymentTypeMapping")

def cardcom_handlenonccpayments(dbo):
    return cboolean(dbo, "CardcomHandleNonCCPayments", DEFAULTS["CardcomHandleNonCCPayments"] == "Yes")

def clone_animal_include_logs(dbo):
    return cboolean(dbo, "CloneAnimalIncludeLogs", DEFAULTS["CloneAnimalIncludeLogs"] == "Yes")

def coding_format(dbo):
    return cstring(dbo, "CodingFormat", DEFAULTS["CodingFormat"])

def coding_format_short(dbo):
    return cstring(dbo, "ShortCodingFormat", DEFAULTS["ShortCodingFormat"])

def cost_source_account(dbo):
    return cint(dbo, "CostSourceAccount", DEFAULTS["CostSourceAccount"])

def create_cost_trx(dbo):
    return cboolean(dbo, "CreateCostTrx")

def create_donation_trx(dbo):
    return cboolean(dbo, "CreateDonationTrx")

def currency_code(dbo):
    return cstring(dbo, "CurrencyCode", DEFAULTS["CurrencyCode"])

def date_brought_in_future_limit(dbo):
    return cint(dbo, "DateBroughtInFutureLimit", DEFAULTS["DateBroughtInFutureLimit"])

def date_diff_cutoffs(dbo):
    return cstring(dbo, "DateDiffCutoffs", DEFAULTS["DateDiffCutoffs"])

def dbv(dbo, v = None):
    if v is None:
        return cstring(dbo, "DBV", "2870")
    else:
        cset_db(dbo, "DBV", v)

def db_lock(dbo):
    """
    Locks the database for updates, returns True if the lock was
    successful.
    """
    if asm3.cachedisk.get("db_update_lock", dbo.database): return False
    asm3.cachedisk.put("db_update_lock", dbo.database, "YES", 60 * 5)
    return True

def db_unlock(dbo):
    """
    Marks the database as unlocked for updates
    """
    asm3.cachedisk.delete("db_update_lock", dbo.database)

def db_view_seq_version(dbo, newval = None):
    if newval is None:
        return cstring(dbo, "DBViewSeqVersion")
    else:
        cset(dbo, "DBViewSeqVersion", newval)

def default_account_view_period(dbo):
    return cint(dbo, "DefaultAccountViewPeriod")

def default_breed(dbo):
    return cint(dbo, "AFDefaultBreed", 1)

def default_broughtinby(dbo):
    return cint(dbo, "DefaultBroughtInBy", 0)

def default_coattype(dbo):
    return cint(dbo, "AFDefaultCoatType", 1)

def default_colour(dbo):
    return cint(dbo, "AFDefaultColour", 1)

def default_daily_boarding_cost(dbo):
    return cint(dbo, "DefaultDailyBoardingCost", int(DEFAULTS["DefaultDailyBoardingCost"]))

def default_death_reason(dbo):
    return cint(dbo, "AFDefaultDeathReason", 1)

def default_donation_type(dbo):
    return cint(dbo, "AFDefaultDonationType", 1)

def default_entry_reason(dbo):
    return cint(dbo, "AFDefaultEntryReason", 4)

def default_incident(dbo):
    return cint(dbo, "DefaultIncidentType", 1)

def default_jurisdiction(dbo):
    return cint(dbo, "DefaultJurisdiction", 1)

def default_location(dbo):
    return cint(dbo, "AFDefaultLocation", 1)

def default_log_filter(dbo):
    return cint(dbo, "AFDefaultLogFilter", 0)

def default_media_notes_from_file(dbo):
    return cboolean(dbo, "DefaultMediaNotesFromFile", DEFAULTS["DefaultMediaNotesFromFile"] == "Yes")

def default_nonsheltertype(dbo):
    return cint(dbo, "AFNonShelterType", 40)

def default_reservation_status(dbo):
    return cint(dbo, "AFDefaultReservationStatus", 1)

def default_return_reason(dbo):
    return cint(dbo, "AFDefaultReturnReason", 4)

def default_size(dbo):
    return cint(dbo, "AFDefaultSize", 1)

def default_species(dbo):
    return cint(dbo, "AFDefaultSpecies", 2)

def default_type(dbo):
    return cint(dbo, "AFDefaultType", 11)

def default_vaccination_type(dbo):
    return cint(dbo, "AFDefaultVaccinationType", 1)

def diary_complete_on_death(dbo):
    return cboolean(dbo, "DiaryCompleteOnDeath", DEFAULTS["DiaryCompleteOnDeath"] == "Yes")

def disable_asilomar(dbo):
    return cboolean(dbo, "DisableAsilomar", DEFAULTS["DisableAsilomar"] == "Yes")

def disable_investigation(dbo):
    return cboolean(dbo, "DisableInvestigation", DEFAULTS["DisableInvestigation"] == "Yes")

def donation_target_account(dbo):
    return cint(dbo, "DonationTargetAccount", DEFAULTS["DonationTargetAccount"])

def donation_account_mappings(dbo):
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

def donation_fee_account(dbo):
    return cint(dbo, "DonationFeeAccount", DEFAULTS["DonationFeeAccount"])

def donation_trx_override(dbo):
    return cboolean(dbo, "DonationTrxOverride", DEFAULTS["DonationTrxOverride"] == "Yes")

def donation_vat_account(dbo):
    return cint(dbo, "DonationVATAccount", DEFAULTS["DonationVATAccount"])

def dont_show_size(dbo):
    return cboolean(dbo, "DontShowSize", DEFAULTS["DontShowSize"] == "Yes")

def email(dbo):
    return cstring(dbo, "EmailAddress")

def email_diary_notes(dbo):
    return cboolean(dbo, "EmailDiaryNotes", DEFAULTS["EmailDiaryNotes"] == "Yes")

def email_diary_on_change(dbo):
    return cboolean(dbo, "EmailDiaryOnChange", DEFAULTS["EmailDiaryOnChange"] == "Yes")

def email_diary_on_complete(dbo):
    return cboolean(dbo, "EmailDiaryOnComplete", DEFAULTS["EmailDiaryOnComplete"] == "Yes")

def email_empty_reports(dbo):
    return cboolean(dbo, "EmailEmptyReports", DEFAULTS["EmailEmptyReports"] == "Yes")

def email_messages(dbo):
    return cboolean(dbo, "EmailMessages", DEFAULTS["EmailMessages"] == "Yes")

def flag_change_log(dbo):
    return cboolean(dbo, "FlagChangeLog", DEFAULTS["FlagChangeLog"] == "Yes")

def flag_change_log_type(dbo):
    return cint(dbo, "FlagChangeLogType", DEFAULTS["FlagChangeLogType"])

def foster_on_shelter(dbo):
    return cboolean(dbo, "FosterOnShelter", DEFAULTS["FosterOnShelter"] == "Yes")

def fosterer_email_overdue_days(dbo):
    return cint(dbo, "FostererEmailOverdueDays", DEFAULTS["FostererEmailOverdueDays"])

def fosterer_email_skip_no_medical(dbo):
    return cboolean(dbo, "FostererEmailSkipNoMedical", DEFAULTS["FostererEmailSkipNoMedical"] == "Yes")

def fosterer_emails(dbo):
    return cboolean(dbo, "FostererEmails", DEFAULTS["FostererEmails"] == "Yes")

def fosterer_emails_reply_to(dbo):
    return cstring(dbo, "FostererEmailsReplyTo")

def fosterer_emails_msg(dbo):
    return cstring(dbo, "FostererEmailsMsg")

def foundanimal_search_columns(dbo):
    return cstring(dbo, "FoundAnimalSearchColumns", DEFAULTS["FoundAnimalSearchColumns"])

def foundanimals_cutoff_days(dbo):
    return cint(dbo, "FoundAnimalsCutoffDays")

def foundanimals_email(dbo):
    return cstring(dbo, "FoundAnimalsEmail")

def foundanimals_folder(dbo):
    return cstring(dbo, "FoundAnimalsFolder")

def future_on_shelter(dbo):
    return cboolean(dbo, "FutureOnShelter", DEFAULTS["FutureOnShelter"] == "Yes")

def ftp_host(dbo):
    return cstring(dbo, "FTPURL")

def ftp_user(dbo):
    return cstring(dbo, "FTPUser")

def ftp_passive(dbo):
    return cboolean(dbo, "FTPPassive", True)

def ftp_password(dbo):
    return cstring(dbo, "FTPPassword")

def ftp_port(dbo):
    return cint(dbo, "FTPPort", 21)

def ftp_root(dbo):
    return cstring(dbo, "FTPRootDirectory")

def generate_document_log(dbo):
    return cboolean(dbo, "GenerateDocumentLog", DEFAULTS["GenerateDocumentLog"] == "Yes")

def generate_document_log_type(dbo):
    return cint(dbo, "GenerateDocumentLogType", DEFAULTS["GenerateDocumentLogType"])

def gdpr_contact_change_log(dbo):
    return cboolean(dbo, "GDPRContactChangeLog", DEFAULTS["GDPRContactChangeLog"] == "Yes")

def gdpr_contact_change_log_type(dbo):
    return cint(dbo, "GDPRContactChangeLogType", DEFAULTS["GDPRContactChangeLogType"])

def geo_provider_override(dbo):
    return cstring(dbo, "GeoProviderOverride")

def geo_provider_key_override(dbo):
    return cstring(dbo, "GeoProviderKeyOverride")

def hold_change_log(dbo):
    return cboolean(dbo, "HoldChangeLog", DEFAULTS["HoldChangeLog"] == "Yes")

def hold_change_log_type(dbo):
    return cint(dbo, "HoldChangeLogType", DEFAULTS["HoldChangeLogType"])

def homeagain_user_id(dbo):
    return cstring(dbo, "HomeAgainUserId")

def homeagain_user_password(dbo):
    return cstring(dbo, "HomeAgainUserPassword")

def include_incomplete_medical_doc(dbo):
    return cboolean(dbo, "IncludeIncompleteMedicalDoc", DEFAULTS["IncludeIncompleteMedicalDoc"] == "Yes")

def include_off_shelter_medical(dbo):
    return cboolean(dbo, "IncludeOffShelterMedical", DEFAULTS["IncludeOffShelterMedical"] == "Yes")

def js_injection(dbo):
    return cstring(dbo, "JSInjection")

def js_window_print(dbo):
    return cboolean(dbo, "JSWindowPrint", DEFAULTS["JSWindowPrint"] == "Yes")

def locale(dbo):
    return cstring(dbo, "Locale", LOCALE)

def location_change_log(dbo):
    return cboolean(dbo, "LocationChangeLog", DEFAULTS["LocationChangeLog"] == "Yes")

def location_change_log_type(dbo):
    return cint(dbo, "LocationChangeLogType", DEFAULTS["LocationChangeLogType"])

def location_filters_enabled(dbo):
    return cboolean(dbo, "LocationFiltersEnabled", DEFAULTS["LocationFiltersEnabled"])

def long_term_months(dbo):
    return cint(dbo, "LongTermMonths", DEFAULTS["LongTermMonths"])

def maddies_fund_username(dbo):
    return cstring(dbo, "MaddiesFundUsername")

def maddies_fund_password(dbo):
    return cstring(dbo, "MaddiesFundPassword")

def mail_merge_max_emails(dbo):
    return cint(dbo, "MailMergeMaxEmails", int(DEFAULTS["MailMergeMaxEmails"]))

def main_screen_animal_link_mode(dbo):
    return cstring(dbo, "MainScreenAnimalLinkMode", DEFAULTS["MainScreenAnimalLinkMode"])

def main_screen_animal_link_max(dbo):
    maxlinks = cint(dbo, "MainScreenAnimalLinkMax", int(DEFAULTS["MainScreenAnimalLinkMax"]))
    maxlinks = min(maxlinks, 1000)
    return maxlinks

def manual_codes(dbo):
    return cboolean(dbo, "ManualCodes", DEFAULTS["ManualCodes"] == "Yes")

def map_link_override(dbo):
    return cstring(dbo, "MapLinkOverride")

def map_provider_override(dbo):
    return cstring(dbo, "MapProviderOverride")

def map_provider_key_override(dbo):
    return cstring(dbo, "MapProviderKeyOverride")

def match_species(dbo):
    return cint(dbo, "MatchSpecies", DEFAULTS["MatchSpecies"])

def match_breed(dbo):
    return cint(dbo, "MatchBreed", DEFAULTS["MatchBreed"])

def match_age(dbo):
    return cint(dbo, "MatchAge", DEFAULTS["MatchAge"])

def match_sex(dbo):
    return cint(dbo, "MatchSex", DEFAULTS["MatchSex"])

def match_area_lost(dbo):
    return cint(dbo, "MatchAreaLost", DEFAULTS["MatchAreaLost"])

def match_features(dbo):
    return cint(dbo, "MatchFeatures", DEFAULTS["MatchFeatures"])

def match_microchip(dbo):
    return cint(dbo, "MatchMicrochip", DEFAULTS["MatchMicrochip"])

def match_postcode(dbo):
    return cint(dbo, "MatchPostcode", DEFAULTS["MatchPostcode"])

def match_colour(dbo):
    return cint(dbo, "MatchColour", DEFAULTS["MatchColour"])

def match_include_shelter(dbo):
    return cboolean(dbo, "MatchIncludeShelter", True)

def match_within2weeks(dbo):
    return cint(dbo, "MatchWithin2Weeks", DEFAULTS["MatchWithin2Weeks"])

def match_point_floor(dbo):
    return cint(dbo, "MatchPointFloor", DEFAULTS["MatchPointFloor"])

def media_allow_jpg(dbo):
    return cboolean(dbo, "MediaAllowJPG", DEFAULTS["MediaAllowJPG"] == "Yes")

def media_allow_pdf(dbo):
    return cboolean(dbo, "MediaAllowPDF", DEFAULTS["MediaAllowPDF"] == "Yes")

def medical_item_display_limit(dbo):
    return cint(dbo, "MedicalItemDisplayLimit", DEFAULTS["MedicalItemDisplayLimit"])

def medical_precreate_treatments(dbo):
    return cboolean(dbo, "MedicalPrecreateTreatments", DEFAULTS["MedicalPrecreateTreatments"] == "Yes")

def microchip_register_movements(dbo):
    return cstring(dbo, "MicrochipRegisterMovements", DEFAULTS["MicrochipRegisterMovements"])

def microchip_register_from(dbo):
    return cstring(dbo, "MicrochipRegisterFrom", "")

def movement_donations_default_due(dbo):
    return cboolean(dbo, "MovementDonationsDefaultDue", DEFAULTS["MovementDonationsDefaultDue"] == "Yes")

def movement_person_only_reserves(dbo):
    return cboolean(dbo, "MovementPersonOnlyReserves", DEFAULTS["MovementPersonOnlyReserves"] == "Yes")

def multi_site_enabled(dbo):
    return cboolean(dbo, "MultiSiteEnabled", DEFAULTS["MultiSiteEnabled"] == "Yes")

def non_shelter_type(dbo):
    return cint(dbo, "AFNonShelterType", 40)

def onlineform_spam_honeytrap(dbo):
    return cboolean(dbo, "OnlineFormSpamHoneyTrap", DEFAULTS["OnlineFormSpamHoneyTrap"] == "Yes")

def onlineform_spam_ua_check(dbo):
    return cboolean(dbo, "OnlineFormSpamUACheck", DEFAULTS["OnlineFormSpamUACheck"] == "Yes")

def onlineform_spam_firstname_mixcase(dbo):
    return cboolean(dbo, "OnlineFormSpamFirstnameMixCase", DEFAULTS["OnlineFormSpamFirstnameMixCase"] == "Yes")

def organisation(dbo):
    return cstring(dbo, "Organisation", DEFAULTS["Organisation"])

def organisation_address(dbo):
    return cstring(dbo, "OrganisationAddress", DEFAULTS["OrganisationAddress"])

def organisation_town(dbo):
    return cstring(dbo, "OrganisationTown")

def organisation_county(dbo):
    return cstring(dbo, "OrganisationCounty")

def organisation_postcode(dbo):
    return cstring(dbo, "OrganisationPostcode")

def organisation_country(dbo):
    return cstring(dbo, "OrganisationCountry")

def organisation_telephone(dbo):
    return cstring(dbo, "OrganisationTelephone", DEFAULTS["OrganisationTelephone"])

def osm_map_tiles_override(dbo):
    return cstring(dbo, "OSMMapTilesOverride")

def owner_name_couple_format(dbo):
    return cstring(dbo, "OwnerNameCoupleFormat", DEFAULTS["OwnerNameCoupleFormat"])

def owner_name_format(dbo):
    return cstring(dbo, "OwnerNameFormat", DEFAULTS["OwnerNameFormat"])

def paypal_email(dbo):
    return cstring(dbo, "PayPalEmail")

def payment_return_url(dbo):
    return cstring(dbo, "PaymentReturnUrl")

def petrescue_adoptable_in(dbo):
    return cstring(dbo, "PetRescueAdoptableIn")

def petrescue_all_desexed(dbo):
    return cboolean(dbo, "PetRescueAllDesexed")

def petrescue_all_microchips(dbo):
    return cboolean(dbo, "PetRescueAllMicrochips")

def petrescue_email(dbo):
    return cstring(dbo, "PetRescueEmail")

def petrescue_phone_number(dbo):
    return cstring(dbo, "PetRescuePhoneNumber")

def petrescue_phone_type(dbo):
    return cstring(dbo, "PetRescuePhoneType")

def petrescue_token(dbo):
    return cstring(dbo, "PetRescueToken")

def pdf_inline(dbo):
    return cboolean(dbo, "PDFInline", DEFAULTS["PDFInline"] == "Yes")

def pdf_zoom(dbo):
    return cint(dbo, "PDFZoom", DEFAULTS["PDFZoom"])

def person_search_columns(dbo):
    return cstring(dbo, "OwnerSearchColumns", DEFAULTS["OwnerSearchColumns"])

def event_excludeanimalswithflags(dbo):
    return cstring(dbo, "EventExcludeAnimalsWithFlags", DEFAULTS["EventExcludeAnimalsWithFlags"])

def event_excludeanimalswithlocations(dbo):
    return cstring(dbo, "EventExcludeAnimalsInLocations", DEFAULTS["EventExcludeAnimalsInLocations"])

def event_search_columns(dbo):
    return cstring(dbo, "EventSearchColumns", DEFAULTS["EventSearchColumns"])

def incident_search_columns(dbo):
    return cstring(dbo, "IncidentSearchColumns", DEFAULTS["IncidentSearchColumns"])

def lostanimal_search_columns(dbo):
    return cstring(dbo, "LostAnimalSearchColumns", DEFAULTS["LostAnimalSearchColumns"])

def petcademy_token(dbo):
    return cstring(dbo, "PetcademyToken")

def petfinder_age_bands(dbo):
    return cstring(dbo, "PetFinderAgeBands")

def petfinder_hide_unaltered(dbo):
    return cboolean(dbo, "PetFinderHideUnaltered", False)

def petfinder_send_holds(dbo):
    return cboolean(dbo, "PetFinderSendHolds", False)

def petfinder_send_strays(dbo):
    return cboolean(dbo, "PetFinderSendStrays", False)

def petfinder_user(dbo):
    return cstring(dbo, "PetFinderFTPUser")

def petfinder_password(dbo):
    return cstring(dbo, "PetFinderFTPPassword")

def helpinglostpets_orgid(dbo):
    return cstring(dbo, "HelpingLostPetsOrgID")

def helpinglostpets_user(dbo):
    return cstring(dbo, "HelpingLostPetsFTPUser")

def helpinglostpets_password(dbo):
    return cstring(dbo, "HelpingLostPetsFTPPassword")

def helpinglostpets_postal(dbo):
    return cstring(dbo, "HelpingLostPetsPostal")

def petlink_cutoff_days(dbo):
    return cint(dbo, "PetLinkCutoffDays")

def petlink_email(dbo):
    return cstring(dbo, "PetLinkEmail")

def petlink_owner_email(dbo):
    return cstring(dbo, "PetLinkOwnerEmail")

def petlink_password(dbo):
    return cstring(dbo, "PetLinkPassword")

def petrescue_user(dbo):
    return cstring(dbo, "PetRescueFTPUser")

def petrescue_password(dbo):
    return cstring(dbo, "PetRescueFTPPassword")

def petrescue_location_regionid(dbo):
    return cboolean(dbo, "PetRescueLocationRegionID", "No")

def pets911_user(dbo):
    return cstring(dbo, "Pets911FTPUser")

def pets911_password(dbo):
    return cstring(dbo, "Pets911FTPPassword")

def pets911_source(dbo):
    return cstring(dbo, "Pets911FTPSourceID")

def petslocated_customerid(dbo):
    return cstring(dbo, "PetsLocatedCustomerID")

def petslocated_includeshelter(dbo):
    return cboolean(dbo, "PetsLocatedIncludeShelter", DEFAULTS["PetsLocatedIncludeShelter"] == "Yes")

def petslocated_animalflag(dbo):
    return cstring(dbo, "PetsLocatedAnimalFlag", DEFAULTS["PetsLocatedAnimalFlag"])

def publisher_use_comments(dbo):
    return cboolean(dbo, "PublisherUseComments", DEFAULTS["PublisherUseComments"] == "Yes")

def record_search_limit(dbo):
    return cint(dbo, "RecordSearchLimit", DEFAULTS["RecordSearchLimit"])

def return_fosters_on_adoption(dbo):
    return cboolean(dbo, "ReturnFostersOnAdoption", DEFAULTS["ReturnFostersOnAdoption"] == "Yes")

def return_fosters_on_transfer(dbo):
    return cboolean(dbo, "ReturnFostersOnTransfer", DEFAULTS["ReturnFostersOnTransfer"] == "Yes")

def return_retailer_on_adoption(dbo):
    return cboolean(dbo, "ReturnRetailerOnAdoption", DEFAULTS["ReturnRetailerOnAdoption"] == "Yes")

def smarttag_accountid(dbo):
    return cstring(dbo, "SmartTagFTPUser")

def publisher_presets(dbo):
    return cstring(dbo, "PublisherPresets", DEFAULTS["PublisherPresets"])

def publisher_sub24_frequency(dbo):
    return cint(dbo, "PublisherSub24Frequency", DEFAULTS["PublisherSub24Frequency"])

def publishers_enabled(dbo):
    return cstring(dbo, "PublishersEnabled")

def publishers_enabled_disable(dbo, publishertodisable):
    """ Disables a publisher by removing it from the PublishersEnabled config """
    pe = cstring(dbo, "PublishersEnabled")
    pe = pe.replace(" " + publishertodisable, "")
    cset(dbo, "PublishersEnabled", pe)

def quicklinks_id(dbo, newval = None):
    if newval is None:
        return cstring(dbo, "QuicklinksID", DEFAULTS["QuicklinksID"])
    else:
        cset(dbo, "QuicklinksID", newval)

def report_toolbar(dbo):
    return cboolean(dbo, "ReportToolbar", DEFAULTS["ReportToolbar"] == "Yes")

def rescuegroups_user(dbo):
    return cstring(dbo, "RescueGroupsFTPUser")

def rescuegroups_password(dbo):
    return cstring(dbo, "RescueGroupsFTPPassword")

def retailer_on_shelter(dbo):
    return cboolean(dbo, "RetailerOnShelter", DEFAULTS["RetailerOnShelter"] == "Yes")

def sac_stray_category(dbo):
    return cstring(dbo, "SACStrayCategory", DEFAULTS["SACStrayCategory"])

def sac_surrender_category(dbo):
    return cstring(dbo, "SACSurrenderCategory", DEFAULTS["SACSurrenderCategory"])

def sac_tnr_category(dbo):
    return cstring(dbo, "SACTNRCategory", DEFAULTS["SACTNRCategory"])

def savourlife_token(dbo):
    return cstring(dbo, "SavourLifeToken")

def savourlife_all_microchips(dbo):
    return cboolean(dbo, "SavourLifeAllMicrochips")

def savourlife_interstate(dbo):
    return cboolean(dbo, "SavourLifeInterstate")

def savourlife_radius(dbo):
    return cint(dbo, "SavourLifeRadius")

def scale_pdfs(dbo):
    return cboolean(dbo, "ScalePDFs", DEFAULTS["ScalePDFs"] == "Yes")

def search_sort(dbo):
    return cint(dbo, "SearchSort", 3)

def service_enabled(dbo):
    return cboolean(dbo, "ServiceEnabled", DEFAULTS["ServiceEnabled"] == "Yes")

def service_auth_enabled(dbo):
    return cboolean(dbo, "ServiceAuthEnabled", DEFAULTS["ServiceAuthEnabled"] == "Yes")

def show_first_time_screen(dbo, change = False, newvalue = False):
    if not change:
        return cboolean(dbo, "ShowFirstTime", DEFAULTS["ShowFirstTime"] == "Yes")
    else:
        cset(dbo, "ShowFirstTime", newvalue and "Yes" or "No")

def show_alerts_home_page(dbo):
    return cboolean(dbo, "ShowAlertsHomePage", DEFAULTS["ShowAlertsHomePage"] == "Yes")

def show_cost_paid(dbo):
    return cboolean(dbo, "ShowCostPaid", DEFAULTS["ShowCostPaid"] == "Yes")

def show_gdpr_contact_optin(dbo):
    return cboolean(dbo, "ShowGDPRContactOptIn", DEFAULTS["ShowGDPRContactOptIn"] == "Yes")

def show_lat_long(dbo):
    return cboolean(dbo, "ShowLatLong", DEFAULTS["ShowLatLong"] == "Yes")

def show_stats_home_page(dbo):
    return cstring(dbo, "ShowStatsHomePage", DEFAULTS["ShowStatsHomePage"])

def show_timeline_home_page(dbo):
    return cboolean(dbo, "ShowTimelineHomePage", DEFAULTS["ShowTimelineHomePage"] == "Yes")

def show_weight_in_lbs(dbo):
    return cboolean(dbo, "ShowWeightInLbs", DEFAULTS["ShowWeightInLbs"] == "Yes")

def show_weight_in_lbs_fraction(dbo):
    return cboolean(dbo, "ShowWeightInLbsFraction", DEFAULTS["ShowWeightInLbsFraction"] == "Yes")

def show_weight_units_in_log(dbo):
    return cboolean(dbo, "ShowWeightUnitsInLog", DEFAULTS["ShowWeightUnitsInLog"] == "Yes")

def signpad_ids(dbo, user, newval = None):
    if newval is None:
        return cstring(dbo, "SignpadIds%s" % user, "")
    else:
        cset(dbo, "SignpadIds%s" % user, newval)

def smdb_locked(dbo):
    return cboolean(dbo, "SMDBLocked")

def smtp_override(dbo):
    return cboolean(dbo, "SMTPOverride", DEFAULTS["SMTPOverride"] == "Yes")

def smtp_server(dbo):
    return cstring(dbo, "SMTPServer")

def smtp_port(dbo):
    return cint(dbo, "SMTPPort", DEFAULTS["SMTPPort"])

def smtp_username(dbo):
    return cstring(dbo, "SMTPUsername")

def smtp_password(dbo):
    return cstring(dbo, "SMTPPassword")

def smtp_use_tls(dbo):
    return cboolean(dbo, "SMTPUseTLS")

def softrelease_on_shelter(dbo):
    return cboolean(dbo, "SoftReleaseOnShelter", DEFAULTS["SoftReleaseOnShelter"] == "Yes")

def stripe_key(dbo):
    return cstring(dbo, "StripeKey")

def stripe_secret_key(dbo):
    return cstring(dbo, "StripeSecretKey")

def system_log_type(dbo):
    return cint(dbo, "SystemLogType", DEFAULTS["SystemLogType"])

def use_short_shelter_codes(dbo):
    return cboolean(dbo, "UseShortShelterCodes")

def third_party_publisher_sig(dbo):
    return cstring(dbo, "TPPublisherSig")

def templates_for_nonshelter(dbo):
    return cboolean(dbo, "TemplatesForNonShelter", DEFAULTS["TemplatesForNonShelter"] == "Yes")

def thumbnail_size(dbo):
    return cstring(dbo, "ThumbnailSize", DEFAULTS["ThumbnailSize"])

def timezone(dbo):
    return cfloat(dbo, "Timezone", TIMEZONE)

def timezone_dst(dbo):
    return cboolean(dbo, "TimezoneDST", DEFAULTS["TimezoneDST"])

def trial_adoptions(dbo):
    return cboolean(dbo, "TrialAdoptions", DEFAULTS["TrialAdoptions"] == "Yes")

def trial_on_shelter(dbo):
    return cboolean(dbo, "TrialOnShelter", DEFAULTS["TrialOnShelter"] == "Yes")

def unique_licence_numbers(dbo):
    return cboolean(dbo, "UniqueLicenceNumbers", DEFAULTS["UniqueLicenceNumbers"] == "Yes")

def update_animal_test_fields(dbo):
    return cboolean(dbo, "UpdateAnimalTestFields", DEFAULTS["UpdateAnimalTestFields"] == "Yes")

def vetenvoy_user_id(dbo):
    return cstring(dbo, "VetEnvoyUserId")

def vetenvoy_user_password(dbo):
    return cstring(dbo, "VetEnvoyUserPassword")

def vetenvoy_homeagain_enabled(dbo):
    return cboolean(dbo, "VetEnvoyHomeAgainEnabled", DEFAULTS["VetEnvoyHomeAgainEnabled"] == "Yes")

def vetenvoy_akcreunite_enabled(dbo):
    return cboolean(dbo, "VetEnvoyAKCReuniteEnabled", DEFAULTS["VetEnvoyAKCReuniteEnabled"] == "Yes")

def waiting_list_default_urgency(dbo):
    return cint(dbo, "WaitingListDefaultUrgency", DEFAULTS["WaitingListDefaultUrgency"])

def waiting_list_rank_by_species(dbo):
    return cboolean(dbo, "WaitingListRankBySpecies")

def waiting_list_highlights(dbo, newhighlights = "READ"):
    if newhighlights == "READ":
        return cstring(dbo, "WaitingListHighlights")
    else:
        cset(dbo, "WaitingListHighlights", newhighlights + " ")

def waiting_list_view_columns(dbo):
    return cstring(dbo, "WaitingListViewColumns", DEFAULTS["WaitingListViewColumns"])

def waiting_list_urgency_update_period(dbo):
    return cint(dbo, "WaitingListUrgencyUpdatePeriod", 14)

def warn_no_homecheck(dbo):
    return cboolean(dbo, "WarnNoHomeCheck", DEFAULTS["WarnNoHomeCheck"] == "Yes")

def watermark_x_offset(dbo):
    return cint(dbo, "WatermarkXOffset", DEFAULTS["WatermarkXOffset"])

def watermark_y_offset(dbo):
    return cint(dbo, "WatermarkYOffset", DEFAULTS["WatermarkYOffset"])

def watermark_font_stroke(dbo):
    return cint(dbo, "WatermarkFontStroke", DEFAULTS["WatermarkFontStroke"])

def watermark_font_fill_color(dbo):
    return cstring(dbo, "WatermarkFontFillColor", DEFAULTS["WatermarkFontFillColor"])

def watermark_font_shadow_color(dbo):
    return cstring(dbo, "WatermarkFontShadowColor", DEFAULTS["WatermarkFontShadowColor"])

def watermark_font_offset(dbo):
    return cint(dbo, "WatermarkFontOffset", DEFAULTS["WatermarkFontOffset"])

def watermark_font_file(dbo):
    return cstring(dbo, "WatermarkFontFile", DEFAULTS["WatermarkFontFile"])

def watermark_font_max_size(dbo):
    return cint(dbo, "WatermarkFontMaxSize", DEFAULTS["WatermarkFontMaxSize"])

def watermark_get_valid_font_files():
    basePath = WATERMARK_FONT_BASEDIRECTORY
    fileList = []
    for root,_,files in os.walk(basePath):
        for f in files:
            if f.endswith('.ttf'):
                fileList.append(os.path.join(root, f)[len(basePath):])
    return sorted(fileList)

def weight_change_log(dbo):
    return cboolean(dbo, "WeightChangeLog", DEFAULTS["WeightChangeLog"] == "Yes")

def weight_change_log_type(dbo):
    return cint(dbo, "WeightChangeLogType", DEFAULTS["WeightChangeLogType"])


