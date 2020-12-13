
import asm3.al
import asm3.audit
import asm3.cachedisk
import asm3.i18n

from asm3.sitedefs import LOCALE, TIMEZONE

QUICKLINKS_SET = {
    1: ("animal_find", "asm-icon-animal-find", asm3.i18n._("Find animal")),
    2: ("animal_new", "asm-icon-animal-add", asm3.i18n._("Add a new animal")),
    3: ("log_new?mode=animal", "asm-icon-log", asm3.i18n._("Add a log entry")),
    4: ("litters", "asm-icon-litter", asm3.i18n._("Edit litters")),
    5: ("person_find", "asm-icon-person-find", asm3.i18n._("Find person")),
    6: ("person_new", "asm-icon-person-add", asm3.i18n._("Add a new person")),
    7: ("lostanimal_find", "asm-icon-animal-lost-find", asm3.i18n._("Find a lost animal")),
    8: ("foundanimal_find", "asm-icon-animal-found-find", asm3.i18n._("Find a found animal")),
    9: ("lostanimal_new", "asm-icon-animal-lost-add", asm3.i18n._("Add a lost animal")),
    10: ("foundanimal_new", "asm-icon-animal-found-add", asm3.i18n._("Add a found animal")),
    11: ("lostfound_match", "asm-icon-match", asm3.i18n._("Match lost and found animals")),
    12: ("diary_edit_my?newnote=1", "asm-icon-diary", asm3.i18n._("Add a diary note")),
    13: ("diary_edit_my", "asm-icon-diary", asm3.i18n._("My diary notes")),
    14: ("diary_edit", "asm-icon-diary", asm3.i18n._("All diary notes")),
    15: ("diarytasks", "asm-icon-diary-task", asm3.i18n._("Edit diary tasks")),
    16: ("waitinglist_new", "asm-icon-waitinglist", asm3.i18n._("Add an animal to the waiting list")),
    17: ("waitinglist_results", "asm-icon-waitinglist", asm3.i18n._("Edit the current waiting list")),
    18: ("move_reserve", "asm-icon-reservation", asm3.i18n._("Reserve an animal")),
    19: ("move_foster", "", asm3.i18n._("Foster an animal")),
    20: ("move_adopt", "asm-icon-person", asm3.i18n._("Adopt an animal")),
    21: ("move_deceased", "asm-icon-death", asm3.i18n._("Mark an animal deceased")),
    22: ("move_book_recent_adoption", "", asm3.i18n._("Return an animal from adoption")),
    23: ("move_book_recent_other", "", asm3.i18n._("Return an animal from another movement")),
    24: ("move_book_reservation", "asm-icon-reservation", asm3.i18n._("Reservation book")),
    25: ("move_book_foster", "asm-icon-book", asm3.i18n._("Foster book")),
    26: ("move_book_retailer", "asm-icon-book", asm3.i18n._("Retailer book")),
    27: ("vaccination?newvacc=1", "", asm3.i18n._("Add a vaccination")),
    28: ("vaccination", "asm-icon-vaccination", asm3.i18n._("Vaccination book")),
    29: ("medical?newmed=1", "", asm3.i18n._("Add a medical regimen")),
    30: ("medical", "asm-icon-medical", asm3.i18n._("Medical book")),
    32: ("publish_options", "asm-icon-settings", asm3.i18n._("Set publishing options")),
    31: ("search?q=forpublish", "asm-icon-animal", asm3.i18n._("Up for adoption")),
    33: ("search?q=deceased", "asm-icon-death", asm3.i18n._("Recently deceased")),
    34: ("search?q=notforadoption", "", asm3.i18n._("Not for adoption")),
    35: ("search?q=onshelter", "asm-icon-animal", asm3.i18n._("Shelter animals")),
    36: ("accounts", "asm-icon-accounts", asm3.i18n._("Accounts")),
    37: ("donation_receive", "asm-icon-donation", asm3.i18n._("Receive a payment")),
    38: ("move_transfer", "", asm3.i18n._("Transfer an animal")),
    39: ("medicalprofile", "", asm3.i18n._("Medical profiles")),
    40: ("shelterview", "asm-icon-location", asm3.i18n._("Shelter view")),
    41: ("move_book_trial_adoption", "asm-icon-trial", asm3.i18n._("Trial adoption book")),
    42: ("incident_new", "asm-icon-call", asm3.i18n._("Report a new incident")),
    43: ("incident_find", "asm-icon-call", asm3.i18n._("Find an incident")),
    44: ("incident_map", "asm-icon-map", asm3.i18n._("Map of active incidents")),
    45: ("traploan?filter=active", "asm-icon-traploan", asm3.i18n._("Trap loans")),
    46: ("calendarview", "asm-icon-calendar", asm3.i18n._("Calendar view")),
    47: ("calendarview?ev=d", "asm-icon-calendar", asm3.i18n._("Diary calendar")),
    48: ("calendarview?ev=vmt", "asm-icon-calendar", asm3.i18n._("Medical calendar")),
    49: ("calendarview?ev=p", "asm-icon-calendar", asm3.i18n._("Payment calendar")),
    50: ("calendarview?ev=ol", "asm-icon-calendar", asm3.i18n._("Animal control calendar")),
    51: ("stocklevel", "asm-icon-stock", asm3.i18n._("Stock Levels")),
    52: ("transport", "asm-icon-transport", asm3.i18n._("Transport Book")),
    53: ("timeline", "asm-icon-calendar", asm3.i18n._("Timeline")),
    54: ("staff_rota", "asm-icon-rota", asm3.i18n._("Staff Rota")),
    55: ("move_reclaim", "", asm3.i18n._("Reclaim an animal")),
    56: ("donation", "asm-icon-donation", asm3.i18n._("Payment book")),
    57: ("calendarview?ev=c", "asm-icon-calendar", asm3.i18n._("Clinic Calendar")),
    58: ("move_book_soft_release", "", asm3.i18n._("Soft release book"))
}

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
    "AddAnimalsShowSize": "No",
    "AddAnimalsShowTattoo": "No",
    "AddAnimalsShowTimeBroughtIn": "No",
    "AddAnimalsShowWeight": "No",
    "AnimalFiguresSplitEntryReason": "No",
    "AnnualFiguresShowBabies": "Yes",
    "AnnualFiguresShowBabiesType": "Yes",
    "AnnualFiguresBabyMonths" : "6",
    "AnnualFiguresSplitAdoptions": "Yes",
    "AnonymisePersonalData": "No",
    "AnonymiseAfterYears": "0",
    "AuditOnViewRecord": "Yes",
    "AuditOnViewReport": "Yes",
    "AuditOnSendEmail": "Yes",
    "AutoCancelReservesDays": "14",
    "AutoDefaultShelterCode": "Yes",
    "AutoDefaultVaccBatch": "Yes",
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
    "AlertSpeciesMicrochip": "1,2",
    "AlertSpeciesNeuter": "1,2",
    "AlertSpeciesRabies": "1,2",
    "AvidReRegistration": "No", 
    "AvidRegisterOverseas": "No",
    "AvidOverseasOriginCountry": "",
    "BoardingCostType": "1",
    "CancelReservesOnAdoption": "Yes",
    "CloneAnimalIncludeLogs": "Yes",
    "CollationIDNext": "0",
    "CostSourceAccount": "9",
    "CreateBoardingCostOnAdoption": "Yes",
    "CreateCostTrx": "No",
    "CreateDonationTrx": "Yes",
    "CodingFormat": "TYYYYNNN",
    "CurrencyCode": "USD",
    "ShortCodingFormat": "NNT",
    "DefaultAnimalAge": "1.0", 
    "DefaultDailyBoardingCost": "2000",
    "DefaultDateBroughtIn": "Yes",
    "DefaultIncidentType": "1",
    "DefaultJurisdiction": "1",
    "DefaultMediaNotesFromFile": "Yes",
    "DefaultShiftStart": "09:00",
    "DefaultShiftEnd": "17:00",
    "DisableAnimalControl": "No",
    "DisableClinic": "No",
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
    "EmailDiaryNotes": "Yes", 
    "EmailDiaryOnChange": "No",
    "EmailDiaryOnComplete": "No",
    "EmailEmptyReports": "Yes",
    "EmailMessages": "Yes", 
    "EmblemAlwaysLocation": "No",
    "EmblemBonded": "Yes",
    "EmblemCrueltyCase": "Yes",
    "EmblemDeceased": "Yes",
    "EmblemHold": "Yes",
    "EmblemLongTerm": "Yes",
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
    "FancyTooltips": "No",
    "FirstDayOfWeek": "1",
    "FosterOnShelter": "Yes",
    "FostererEmails": "No", 
    "FostererEmailOverdueDays": "-30",
    "ShowGDPRContactOptIn": "No",
    "GDPRContactChangeLog": "No",
    "GDPRContactChangeLogType": "6",
    "GeocodeWithPostcodeOnly": "No",
    "GenerateDocumentLog": "No",
    "GenerateDocumentLogType": "5",
    "HideCountry": "Yes",
    "HideHomeCheckedNoFlag": "Yes",
    "HoldChangeLog": "Yes",
    "HoldChangeLogType": "3",
    "IncidentPermissions": "No",
    "InactivityTimer": "No",
    "InactivityTimeout": "20", 
    "IncludeIncompleteMedicalDoc": "Yes",
    "IncludeOffShelterMedical": "No",
    "Locale": "en",
    "LocationChangeLog": "Yes",
    "LocationChangeLogType": "3",
    "LocationFiltersEnabled": "No",
    "LongTermMonths": "6",
    "MailMergeMaxEmails": "2000",
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
    "MedicalItemDisplayLimit": "500",
    "MicrochipRegisterMovements": "1,5",
    "MovementDonationsDefaultDue": "No",
    "MovementNumberOverride": "No",
    "MovementPersonOnlyReserves": "Yes",
    "MultiSiteEnabled": "No", 
    "JSWindowPrint": "Yes",
    "OnlineFormVerifyJSKey": "Yes",
    "Organisation": "Organisation",
    "OrganisationAddress": "Address",
    "OrganisationTelephone": "Telephone",
    "OwnerAddressCheck": "Yes",
    "OwnerNameCheck": "Yes",
    "OwnerNameFormat": "{ownertitle} {ownerforenames} {ownersurname}",
    "OwnerSearchColumns": "OwnerCode,OwnerName,OwnerSurname," \
        "MembershipNumber,AdditionalFlags,OwnerAddress," \
        "OwnerTown,OwnerCounty,OwnerPostcode,HomeTelephone,WorkTelephone," \
        "MobileTelephone,EmailAddress",
    "PetsLocatedIncludeShelter": "No",
    "PetsLocatedAnimalFlag": "",
    "PicturesInBooks": "Yes",
    "PDFInline": "Yes",
    "PublisherUseComments": "Yes",
    "PublisherIgnoreFTPOverride": "No",
    "PublisherPresets": "includefosters excludeunder=12",
    "PublisherSub24Frequency": "0",
    "QuicklinksID": "40,46,25,31,34,19,20",
    "QuicklinksHomeScreen": "Yes",
    "QuicklinksAllScreens": "No",
    "ReceiptNumberNext": "0",
    "RecordSearchLimit": "1000",
    "ReloadMedical": "Yes",
    "ReservesOverdueDays": "7",
    "RetailerOnShelter": "Yes",
    "ReturnFostersOnAdoption": "Yes",
    "ReturnFostersOnTransfer": "Yes",
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
    "SMTPPort": "25",
    "SoftReleases": "No",
    "SoftReleaseOnShelter": "No",
    "StickyTableHeaders": "Yes",
    "TableHeadersVisible": "Yes",
    "TemplatesForNonShelter": "No",
    "ThumbnailSize": "150x150",
    "Timezone": "-5",
    "TimezoneDST": "Yes",
    "TrialAdoptions": "No",
    "TrialOnShelter": "No",
    "UniqueLicenceNumbers": "Yes",
    "UseAutoInsurance": "No",
    "UseShortShelterCodes": "Yes", 
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
    "WarnBannedOwner": "Yes",
    "WarnOOPostcode": "Yes",
    "WarnSimilarAnimalName": "Yes",
    "WeightChangeLog": "Yes",
    "WeightChangeLogType": "4"
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
        VALID_CODES = ("XX", "XXX", "NN", "NNN", "UUUU", "UUUUUUUUUU")
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
        if k in ("EmailSignature", "FostererEmailsMsg"):
            # It's HTML - don't XSS escape it
            put(k, v, sanitiseXSS = False)
        elif k == "CodingFormat":
            # If there's no valid N, X or U tokens in there, it's not valid so reset to
            # the default.
            if not valid_code(v):
                put(k, "TYYYYNNN")
            else:
                put(k, v)
        elif k == "ShortCodingFormat":
            # If there's no N, X or U in there, it's not valid so reset to
            # the default.
            if not valid_code(v):
                put(k, "NNT")
            else:
                put(k, v)
        elif k == "DefaultDailyBoardingCost":
            # Need to handle currency fields differently
            put(k, str(post.integer(k)))
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

def alert_species_microchip(dbo):
    s = cstring(dbo, "AlertSpeciesMicrochip", DEFAULTS["AlertSpeciesMicrochip"])
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

def anonymise_personal_data(dbo):
    return cboolean(dbo, "AnonymisePersonalData", DEFAULTS["AnonymisePersonalData"])

def anonymise_after_years(dbo):
    return cint(dbo, "AnonymiseAfterYears", DEFAULTS["AnonymiseAfterYears"])

def audit_on_view_record(dbo):
    return cboolean(dbo, "AuditOnViewRecord", DEFAULTS["AuditOnViewRecord"])

def audit_on_view_report(dbo):
    return cboolean(dbo, "AuditOnViewReport", DEFAULTS["AuditOnViewReport"])

def audit_on_send_email(dbo):
    return cboolean(dbo, "AuditOnSendEmail", DEFAULTS["AuditOnSendEmail"])

def auto_cancel_reserves_days(dbo):
    return cint(dbo, "AutoCancelReservesDays", int(DEFAULTS["AutoCancelReservesDays"]))

def auto_cancel_hold_days(dbo):
    return cint(dbo, "AutoCancelHoldDays", int(DEFAULTS["AutoCancelHoldDays"]))

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

def clone_animal_include_logs(dbo):
    return cboolean(dbo, "CloneAnimalIncludeLogs", DEFAULTS["CloneAnimalIncludeLogs"] == "Yes")

def coding_format(dbo):
    return cstring(dbo, "CodingFormat", DEFAULTS["CodingFormat"])

def coding_format_short(dbo):
    return cstring(dbo, "ShortCodingFormat", DEFAULTS["ShortCodingFormat"])

def collation_id_next(dbo):
    """ Returns the CollationIDNext value and increments it """
    nrn = cint(dbo, "CollationIDNext", 0)
    if nrn == 0:
        nrn = 1 + dbo.query_int("SELECT MAX(CollationID) FROM onlineformincoming")
    cset(dbo, "CollationIDNext", str(nrn + 1))
    return nrn

def cost_source_account(dbo):
    return cint(dbo, "CostSourceAccount", DEFAULTS["CostSourceAccount"])

def create_cost_trx(dbo):
    return cboolean(dbo, "CreateCostTrx")

def create_donation_trx(dbo):
    return cboolean(dbo, "CreateDonationTrx")

def currency_code(dbo):
    return cstring(dbo, "CurrencyCode", DEFAULTS["CurrencyCode"])

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

def foster_on_shelter(dbo):
    return cboolean(dbo, "FosterOnShelter", DEFAULTS["FosterOnShelter"] == "Yes")

def fosterer_email_overdue_days(dbo):
    return cint(dbo, "FostererEmailOverdueDays", DEFAULTS["FostererEmailOverdueDays"])

def fosterer_emails(dbo):
    return cboolean(dbo, "FostererEmails", DEFAULTS["FostererEmails"] == "Yes")

def fosterer_emails_reply_to(dbo):
    return cstring(dbo, "FostererEmailsReplyTo")

def fosterer_emails_msg(dbo):
    return cstring(dbo, "FostererEmailsMsg")

def foundanimals_cutoff_days(dbo):
    return cint(dbo, "FoundAnimalsCutoffDays")

def foundanimals_email(dbo):
    return cstring(dbo, "FoundAnimalsEmail")

def foundanimals_folder(dbo):
    return cstring(dbo, "FoundAnimalsFolder")

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
    return cboolean(dbo, "GenerateDocumentLog", False)

def generate_document_log_type(dbo):
    return cint(dbo, "GenerateDocumentLogType", 0)

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

def microchip_register_movements(dbo):
    return cstring(dbo, "MicrochipRegisterMovements", DEFAULTS["MicrochipRegisterMovements"])

def movement_donations_default_due(dbo):
    return cboolean(dbo, "MovementDonationsDefaultDue", DEFAULTS["MovementDonationsDefaultDue"] == "Yes")

def movement_person_only_reserves(dbo):
    return cboolean(dbo, "MovementPersonOnlyReserves", DEFAULTS["MovementPersonOnlyReserves"] == "Yes")

def multi_site_enabled(dbo):
    return cboolean(dbo, "MultiSiteEnabled", DEFAULTS["MultiSiteEnabled"] == "Yes")

def non_shelter_type(dbo):
    return cint(dbo, "AFNonShelterType", 40)

def online_form_verify_jskey(dbo):
    return cboolean(dbo, "OnlineFormVerifyJSKey", DEFAULTS["OnlineFormVerifyJSKey"] == "Yes")

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

def person_search_columns(dbo):
    return cstring(dbo, "OwnerSearchColumns", DEFAULTS["OwnerSearchColumns"])

def petcademy_token(dbo):
    return cstring(dbo, "PetcademyToken")

def petfinder_age_bands(dbo):
    return cstring(dbo, "PetFinderAgeBands")

def petfinder_hide_unaltered(dbo):
    return cboolean(dbo, "PetFinderHideUnaltered", False)

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

def smarttag_accountid(dbo):
    return cstring(dbo, "SmartTagFTPUser")

def publisher_presets(dbo):
    return cstring(dbo, "PublisherPresets", DEFAULTS["PublisherPresets"])

def publisher_ignore_ftp_override(dbo):
    return cboolean(dbo, "PublisherIgnoreFTPOverride", DEFAULTS["PublisherIgnoreFTPOverride"] == "Yes")

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

def receipt_number_next(dbo):
    """ Returns the ReceiptNumberNext value and increments it """
    nrn = cint(dbo, "ReceiptNumberNext", 0)
    if nrn == 0:
        nrn = 1 + dbo.query_int("SELECT MAX(ID) FROM ownerdonation")
    cset(dbo, "ReceiptNumberNext", str(nrn + 1))
    return nrn

def rescuegroups_user(dbo):
    return cstring(dbo, "RescueGroupsFTPUser")

def rescuegroups_password(dbo):
    return cstring(dbo, "RescueGroupsFTPPassword")

def retailer_on_shelter(dbo):
    return cboolean(dbo, "RetailerOnShelter", DEFAULTS["RetailerOnShelter"] == "Yes")

def savourlife_username(dbo):
    return cstring(dbo, "SavourLifeUsername")

def savourlife_password(dbo):
    return cstring(dbo, "SavourLifePassword")

def savourlife_interstate(dbo):
    return cboolean(dbo, "SavourLifeInterstate")

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

def smtp_server(dbo):
    return cstring(dbo, "SMTPServer")

def smtp_port(dbo):
    return cint(dbo, "SMTPPort", DEFAULTS["SMTPPort"])

def smtp_server_username(dbo):
    return cstring(dbo, "SMTPServerUsername")

def smtp_server_password(dbo):
    return cstring(dbo, "SMTPServerPassword")

def smtp_server_tls(dbo):
    return cboolean(dbo, "SMTPServerUseTLS")

def softrelease_on_shelter(dbo):
    return cboolean(dbo, "SoftReleaseOnShelter", DEFAULTS["SoftReleaseOnShelter"] == "Yes")

def stripe_key(dbo):
    return cstring(dbo, "StripeKey")

def stripe_secret_key(dbo):
    return cstring(dbo, "StripeSecretKey")

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

def weight_change_log(dbo):
    return cboolean(dbo, "WeightChangeLog", DEFAULTS["WeightChangeLog"] == "Yes")

def weight_change_log_type(dbo):
    return cint(dbo, "WeightChangeLogType", DEFAULTS["WeightChangeLogType"])


