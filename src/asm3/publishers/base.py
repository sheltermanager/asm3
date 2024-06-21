
import asm3.additional
import asm3.al
import asm3.animal
import asm3.asynctask
import asm3.configuration
import asm3.dbfs
import asm3.i18n
import asm3.media
import asm3.movement
import asm3.utils
import asm3.wordprocessor
from asm3.sitedefs import SERVICE_URL, FTP_CONNECTION_TIMEOUT
from asm3.typehints import Any, datetime, Database, Dict, List, ResultRow, Results

import ftplib
import glob
import os
import shutil
import sys
import tempfile
import threading

def quietcallback(x: Any) -> None:
    """ ftplib callback that does nothing instead of dumping messages to stdout """
    pass

class PublishCriteria(object):
    """
    Class containing publishing criteria. Has functions to 
    convert to and from a command line string
    """
    includeCaseAnimals = False
    includeNonNeutered = False
    includeNonMicrochipped = False
    includeReservedAnimals = False
    includeRetailerAnimals = False
    includeFosterAnimals = False
    includeQuarantine = False
    includeTrial = False
    includeHold = False
    includeWithoutDescription = False
    includeWithoutImage = False
    includeColours = False
    bondedAsSingle = False
    clearExisting = False
    uploadAllImages = False
    uploadDirectly = False
    forceReupload = False
    noImportFile = False # If a 3rd party has a seperate import disable upload
    generateJavascriptDB = False
    thumbnails = False
    thumbnailSize = "70x70"
    checkSocket = False
    order = 1 # 0 = Ascending entry, 1 = Descending entry, 2 = Ascending name
    excludeUnderWeeks = 12
    excludeReserves = 0
    animalsPerPage = 10
    htmlByChildAdult = False # True if html pages should be prefixed baby/adult_ and split
    childAdultSplit=26 # Number of weeks before an animal is treated as an adult by the child adult publisher
    htmlBySpecies = False # True if html pages should be output with species name and possibly split by age
    htmlByType = False # True if html pages should be output with type name
    outputAdopted = False # True if html publisher should output an adopted.html page
    outputAdoptedDays = 30 # The number of days to go back when considering adopted animals
    outputDeceased = False # True if html publisher should output a deceased.html page
    outputForms = False # True if html publisher should output a forms.html page
    outputRSS = False # True if html publisher should output an rss.xml page
    style = "."
    extension = "html"
    scaleImages = "" # A resize spec or old values of: 1 = None, 2 = 320x200, 3=640x480, 4=800x600, 5=1024x768, 6=300x300, 7=95x95
    internalLocations = [] # List of either location IDs, or LIKE comparisons
    publishDirectory = None # None = use temp directory for publishing
    ignoreLock = False # Force the publisher to run even if another publisher is running

    def get_int(self, s: str) -> int:
        """
        Returns the val portion of key=val as an int
        """
        return asm3.utils.cint(s.split("=")[1])

    def get_str(self, s: str) -> str:
        """
        Returns the val portion of key=val as a string
        """
        return s.split("=")[1]

    def __init__(self, fromstring: str = "") -> None:
        """
        Initialises the publishing criteria from a string if given
        """
        if fromstring == "": return
        for s in fromstring.split(" "):
            if s == "includecase": self.includeCaseAnimals = True
            if s == "includenonneutered": self.includeNonNeutered = True
            if s == "includenonmicrochip": self.includeNonMicrochipped = True
            if s == "includereserved": self.includeReservedAnimals = True
            if s == "includeretailer": self.includeRetailerAnimals = True
            if s == "includefosters": self.includeFosterAnimals = True
            if s == "includehold": self.includeHold = True
            if s == "includequarantine": self.includeQuarantine = True
            if s == "includetrial": self.includeTrial = True
            if s == "includewithoutdescription": self.includeWithoutDescription = True
            if s == "includewithoutimage": self.includeWithoutImage = True
            if s == "includecolours": self.includeColours = True
            if s == "bondedassingle": self.bondedAsSingle = True
            if s == "noimportfile": self.noImportFile = True
            if s == "clearexisting": self.clearExisting = True
            if s == "uploadall": self.uploadAllImages = True
            if s == "forcereupload": self.forceReupload = True
            if s == "generatejavascriptdb": self.generateJavascriptDB = True
            if s == "thumbnails": self.thumbnails = True
            if s == "checksocket": self.checkSocket = True
            if s == "uploaddirectly": self.uploadDirectly = True
            if s == "htmlbychildadult": self.htmlByChildAdult = True
            if s == "htmlbyspecies": self.htmlBySpecies = True
            if s == "htmlbytype": self.htmlByType = True
            if s == "outputadopted": self.outputAdopted = True
            if s == "outputdeceased": self.outputDeceased = True
            if s == "outputforms": self.outputForms = True
            if s == "outputrss": self.outputRSS = True
            if s.startswith("outputadopteddays"): self.outputAdoptedDays = self.get_int(s)
            if s.startswith("order"): self.order = self.get_int(s)
            if s.startswith("excludeunder"): self.excludeUnderWeeks = self.get_int(s)
            if s.startswith("excludereserves"): self.excludeReserves = self.get_int(s)
            if s.startswith("animalsperpage"): self.animalsPerPage = self.get_int(s)
            if s.startswith("style"): self.style = self.get_str(s)
            if s.startswith("extension"): self.extension = self.get_str(s)
            if s.startswith("scaleimages"): self.scaleImages = self.get_str(s)
            if s.startswith("thumbnailsize"): self.thumbnailSize = self.get_str(s)
            if s.startswith("includelocations") and len(self.get_str(s)) > 0 and self.get_str(s) != "null": self.internalLocations = self.get_str(s).split(",")
            if s.startswith("publishdirectory"): self.publishDirectory = self.get_str(s)
            if s.startswith("childadultsplit"): self.childAdultSplit = self.get_int(s)

    def __str__(self) -> str:
        """
        Returns a string representation of the criteria (which corresponds
        exactly to an ASM 2.x command line string to a publisher and is how
        we store the defaults in the database)
        """
        s = ""
        if self.includeCaseAnimals: s += " includecase"
        if self.includeNonNeutered: s += " includenonneutered"
        if self.includeNonMicrochipped: s += " includenonmicrochip"
        if self.includeReservedAnimals: s += " includereserved"
        if self.includeRetailerAnimals: s += " includeretailer"
        if self.includeFosterAnimals: s += " includefosters"
        if self.includeHold: s += " includehold"
        if self.includeQuarantine: s += " includequarantine"
        if self.includeTrial: s += " includetrial"
        if self.includeWithoutDescription: s += " includewithoutdescription"
        if self.includeWithoutImage: s += " includewithoutimage"
        if self.includeColours: s += " includecolours"
        if self.bondedAsSingle: s += " bondedassingle"
        if self.noImportFile: s += " noimportfile"
        if self.clearExisting: s += " clearexisting"
        if self.uploadAllImages: s += " uploadall"
        if self.forceReupload: s += " forcereupload"
        if self.generateJavascriptDB: s += " generatejavascriptdb"
        if self.thumbnails: s += " thumbnails"
        if self.checkSocket: s += " checksocket"
        if self.uploadDirectly: s += " uploaddirectly"
        if self.htmlBySpecies: s += " htmlbyspecies"
        if self.htmlByType: s += " htmlbytype"
        if self.htmlByChildAdult: s += " htmlbychildadult"
        if self.outputAdopted: s += " outputadopted"
        if self.outputDeceased: s += " outputdeceased"
        if self.outputForms: s += " outputforms"
        if self.outputRSS: s += " outputrss"
        s += " order=" + str(self.order)
        s += " excludeunder=" + str(self.excludeUnderWeeks)
        s += " excludereserves=" + str(self.excludeReserves)
        s += " animalsperpage=" + str(self.animalsPerPage)
        s += " style=" + str(self.style)
        s += " extension=" + str(self.extension)
        s += " scaleimages=" + str(self.scaleImages)
        s += " thumbnailsize=" + str(self.thumbnailSize)
        s += " childadultsplit=" + str(self.childAdultSplit)
        s += " outputadopteddays=" + str(self.outputAdoptedDays)
        if len(self.internalLocations) > 0: s += " includelocations=" + ",".join(self.internalLocations)
        if self.publishDirectory is not None: s += " publishdirectory=" + self.publishDirectory
        return s.strip()

def get_animal_data(dbo: Database, pc: PublishCriteria = None, animalid: int = 0, 
                    include_additional_fields: bool = False, recalc_age_groups: bool = True, strip_personal_data: bool = False, 
                    publisher_key: str = "", limit: int = 0) -> Results:
    """
    Returns a resultset containing the animal info for the criteria given.
    pc: The publish criteria (if None, default is used)
    animalid: If non-zero only returns the animal given (if it is adoptable)
    include_additional_fields: Load additional fields for each result
    strip_personal_data: Remove any personal data such as surrenderer, brought in by, etc.
    publisher_key: The publisher calling this function
    limit: Only return limit rows.
    """
    if pc is None:
        pc = PublishCriteria(asm3.configuration.publisher_presets(dbo))
    
    sql = get_animal_data_query(dbo, pc, animalid, publisher_key=publisher_key)
    rows = dbo.query(sql, distincton="ID")
    asm3.al.debug("get_animal_data_query returned %d rows" % len(rows), "publishers.base.get_animal_data", dbo)

    # If the sheltercode format has a slash in it, convert it to prevent
    # creating images with broken paths.
    if len(rows) > 0 and rows[0]["SHELTERCODE"].find("/") != -1:
        asm3.al.debug("discovered forward slashes in code, repairing", "publishers.base.get_animal_data", dbo)
        for r in rows:
            r.SHORTCODE = r.SHORTCODE.replace("/", "-").replace(" ", "")
            r.SHELTERCODE = r.SHELTERCODE.replace("/", "-").replace(" ", "")

    # If we're using animal comments, override the websitemedianotes field
    # with animalcomments for compatibility with service users and other
    # third parties who were used to the old way of doing things
    if asm3.configuration.publisher_use_comments(dbo):
        for r in rows:
            r.WEBSITEMEDIANOTES = r.ANIMALCOMMENTS

    # If we aren't including animals with blank descriptions, remove them now
    # (but don't let it override the courtesy flag, which should always make animals appear)
    if not pc.includeWithoutDescription:
        oldcount = len(rows)
        rows = [r for r in rows if r.ISCOURTESY == 1 or asm3.utils.nulltostr(r.WEBSITEMEDIANOTES).strip() != "" ]
        asm3.al.debug("removed %d rows without descriptions" % (oldcount - len(rows)), "publishers.base.get_animal_data", dbo)

    # Embellish additional fields if requested
    if include_additional_fields:
        asm3.additional.append_to_results(dbo, rows, "animal")

    # Strip any personal data if requested
    if strip_personal_data:
        personal = ["ADOPTIONCOORDINATOR", "ORIGINALOWNER", "BROUGHTINBY", 
            "CURRENTOWNER", "OWNERNAME", "RESERVEDOWNER", 
            "CURRENTVET", "NEUTERINGVET", "OWNERSVET"]
        for r in rows:
            for k in r.keys():
                for p in personal:
                    if k.startswith(p):
                        r[k] = ""

    # Recalculate age groups
    if recalc_age_groups:
        asm3.animal.calc_age_group_rows(dbo, rows)
    
    # Generate the sponsor column
    unitextra = asm3.configuration.unit_extra(dbo)
    if unitextra.strip() != "":
        for r in rows:
            if r.ACTIVEMOVEMENTTYPE is not None and r.ACTIVEMOVEMENTTYPE > 0: continue # animal must be in the location
            r.UNITSPONSOR = asm3.configuration.unit_extra_get(dbo, r.SHELTERLOCATION, r.SHELTERLOCATIONUNIT)[0]

    # If bondedAsSingle is on, go through the the set of animals and merge
    # the bonded animals into a single record
    def merge_animal(a, aid):
        """
        Find the animal in rows with animalid, merge it into a and
        then remove it from the set.
        """
        for r in rows:
            if r.ID == aid:
                # Add some useful values for publishers that can accept bonded animal info
                a.BONDEDNAME1 = a.ANIMALNAME
                a.BONDEDNAME2 = r.ANIMALNAME
                a.BONDEDSEX = r.SEX
                a.BONDEDMICROCHIPNUMBER = r.IDENTICHIPNUMBER
                a.BONDEDBREEDNAME = r.BREEDNAME
                a.BONDEDSIZE = r.SIZE
                a.BONDEDDATEOFBIRTH = r.DATEOFBIRTH
                a.ANIMALNAME = "%s / %s" % (a.ANIMALNAME, r.ANIMALNAME)
                r.REMOVE = True # Flag this row for removal
                asm3.al.debug("merged animal %d into %d" % (aid, a.ID), "publishers.base.get_animal_data", dbo)
                break
    
    def check_bonding(r):
        """ Verifies if this row is bonded to another animal and handles 
            the merge. Returns TRUE if this row should be added to the set """
        if "REMOVE" in r and r.REMOVE: 
            return False
        if r.BONDEDANIMALID is not None and r.BONDEDANIMALID != 0:
            merge_animal(r, r.BONDEDANIMALID)
        if r.BONDEDANIMAL2ID is not None and r.BONDEDANIMAL2ID != 0:
            merge_animal(r, r.BONDEDANIMAL2ID)
        return True

    if pc.bondedAsSingle:
        # Sort the list by the Animal ID so that the first entered bonded animal
        # always "wins" and becomes the first to be output
        rows = [ r for r in sorted(rows, key=lambda k: k.ID) if check_bonding(r) ]

    # If animalid was set, only return that row or an empty set if it wasn't present
    if animalid != 0:
        for r in rows:
            if r.ID == animalid:
                return [ r ]
        return []

    # Ordering
    if pc.order == 0:
        rows = sorted(rows, key=lambda k: k.MOSTRECENTENTRYDATE)
    elif pc.order == 1:
        rows = list(reversed(sorted(rows, key=lambda k: k.MOSTRECENTENTRYDATE)))
    elif pc.order == 2:
        rows = sorted(rows, key=lambda k: k.ANIMALNAME)
    else:
        rows = sorted(rows, key=lambda k: k.MOSTRECENTENTRYDATE)

    # If a limit was set, throw away extra rows
    # (we do it here instead of a LIMIT clause as there's extra logic that throws
    #  away rows above).
    if limit > 0 and len(rows) > limit:
        rows = rows[0:limit]

    return rows

def get_animal_data_query(dbo: Database, pc: PublishCriteria, animalid: int = 0, publisher_key: str = "") -> str:
    """
    Generate the adoptable animal query.
    publisher_key is used to generate an exclusion to remove animals who have 
        a flag called "Exclude from publisher_key" - this prevents animals
        eg: being sent to PetFinder (Exclude from petfinder)
    """
    sql = asm3.animal.get_animal_query(dbo)
    # Always include non-dead courtesy listings
    sql += " WHERE (a.DeceasedDate Is Null AND a.IsCourtesy = 1) OR (a.ID > 0"
    if animalid != 0:
        sql += " AND a.ID = " + str(animalid)
    if not pc.includeCaseAnimals: 
        sql += " AND a.CrueltyCase = 0"
    if not pc.includeNonNeutered:
        sql += " AND (a.Neutered = 1 OR a.SpeciesID NOT IN (%s))" % asm3.configuration.alert_species_neuter(dbo)
    if not pc.includeNonMicrochipped:
        sql += " AND (a.Identichipped = 1 OR a.SpeciesID NOT IN (%s))" % asm3.configuration.alert_species_microchip(dbo)
    if not pc.includeWithoutImage: 
        sql += " AND EXISTS(SELECT ID FROM media WHERE WebsitePhoto = 1 AND ExcludeFromPublish = 0 AND LinkID = a.ID AND LinkTypeID = 0)"
    if not pc.includeReservedAnimals: 
        sql += " AND a.HasActiveReserve = 0"
    if not pc.includeHold: 
        sql += " AND (a.IsHold = 0 OR a.IsHold Is Null)"
    if not pc.includeQuarantine:
        sql += " AND (a.IsQuarantine = 0 OR a.IsQuarantine Is Null)"
    if not pc.includeTrial:
        sql += " AND a.HasTrialAdoption = 0"
    if publisher_key != "":
        sql += " AND LOWER(a.AdditionalFlags) NOT LIKE LOWER('%%Exclude from %s|%%')" % publisher_key
    # Doesn't have too many active reserves
    if pc.excludeReserves > 0:
        sql += " AND (SELECT COUNT(*) FROM adoption WHERE AnimalID = a.ID AND MovementType = 0 AND ReservationCancelledDate Is Null) <= %s" % pc.excludeReserves
    # Make sure animal is old enough
    sql += " AND a.DateOfBirth <= " + dbo.sql_value(dbo.today(offset = pc.excludeUnderWeeks * -7))
    # Filter out dead and unadoptable animals
    sql += " AND a.DeceasedDate Is Null AND a.IsNotAvailableForAdoption = 0"
    # Filter out permanent fosters
    sql += " AND a.HasPermanentFoster = 0"
    # Filter out animals with a future adoption
    sql += " AND NOT EXISTS(SELECT ID FROM adoption WHERE MovementType = 1 AND AnimalID = a.ID AND MovementDate > %s)" % dbo.sql_value(dbo.today())
    # Filter out active boarders
    sql += " AND ab.ID IS NULL"
    # Build a set of OR clauses based on any movements/locations
    moveor = []
    if len(pc.internalLocations) > 0 and pc.internalLocations[0].strip() != "null" and "".join(pc.internalLocations) != "":
        moveor.append("(a.Archived = 0 AND a.ActiveMovementID = 0 AND a.ShelterLocation IN (%s))" % ",".join(pc.internalLocations))
    else:
        moveor.append("(a.Archived = 0 AND a.ActiveMovementID = 0)")
    if pc.includeRetailerAnimals:
        moveor.append("(a.ActiveMovementType = %d)" % asm3.movement.RETAILER)
    if pc.includeFosterAnimals:
        moveor.append("(a.ActiveMovementType = %d)" % asm3.movement.FOSTER)
    if pc.includeTrial:
        moveor.append("(a.ActiveMovementType = %d AND a.HasTrialAdoption = 1)" % asm3.movement.ADOPTION)
    sql += " AND (" + " OR ".join(moveor) + ")) ORDER BY a.ID"
    return sql

def get_microchip_data(dbo: Database, patterns: List[str], publishername: str, 
                       allowintake: bool = True, organisation_email: str = "") -> Results:
    """
    Returns a list of animals with unpublished microchips.
    patterns:      A list of either microchip prefixes or SQL clauses to OR together
                   together in the preamble, eg: [ '977', "a.SmartTag = 1 AND a.SmartTagNumber <> ''" ]
    publishername: The name of the microchip registration publisher, eg: pettracuk
    allowintake:   True if the provider is ok with registering to the shelter's details on intake
    organisation_email: The org email to set for intake animals (if blank, uses asm3.configuration.email())
    """
    movementtypes = asm3.configuration.microchip_register_movements(dbo)
    registerfrom = asm3.i18n.display2python(dbo.locale, asm3.configuration.microchip_register_from(dbo))

    try:
        rows = dbo.query(get_microchip_data_query(dbo, patterns, publishername, movementtypes, registerfrom, allowintake), distincton="ID")
    except Exception as err:
        asm3.al.error(str(err), "publisher.get_microchip_data", dbo, sys.exc_info())

    organisation = asm3.configuration.organisation(dbo)
    orgaddress = asm3.configuration.organisation_address(dbo)
    orgtown = asm3.configuration.organisation_town(dbo)
    orgcounty = asm3.configuration.organisation_county(dbo)
    orgpostcode = asm3.configuration.organisation_postcode(dbo)
    orgcountry = asm3.configuration.organisation_country(dbo)
    orgtelephone = asm3.configuration.organisation_telephone(dbo)
    email = asm3.configuration.email(dbo)
    if organisation_email != "": email = organisation_email
    extras = []

    for r in rows:
        use_original_owner_info = False
        use_shelter_info = False

        # If this is a non-shelter animal, use the original owner info
        if r.NONSHELTERANIMAL == 1 and r.ORIGINALOWNERNAME is not None and r.ORIGINALOWNERNAME != "":
            use_original_owner_info = True

        # If this is an on-shelter animal with no active movement, use the shelter info
        elif r.ARCHIVED == 0 and r.ACTIVEMOVEMENTID == 0:
            use_shelter_info = True

        # If this is a shelter animal on foster, but register on intake is set and foster is not, use the shelter info
        elif r.ARCHIVED == 0 and r.ACTIVEMOVEMENTTYPE == 2 and movementtypes.find("0") != -1 and movementtypes.find("2") == -1:
            use_shelter_info = True

        # Otherwise, leave CURRENTOWNER* fields as they are for active movement
        if use_original_owner_info:
            r.CURRENTOWNERNAME = r.ORIGINALOWNERNAME
            r.CURRENTOWNERTITLE = r.ORIGINALOWNERTITLE
            r.CURRENTOWNERINITIALS = r.ORIGINALOWNERINITIALS
            r.CURRENTOWNERFORENAMES = r.ORIGINALOWNERFORENAMES
            r.CURRENTOWNERSURNAME = r.ORIGINALOWNERSURNAME
            r.CURRENTOWNERADDRESS = r.ORIGINALOWNERADDRESS
            r.CURRENTOWNERTOWN = r.ORIGINALOWNERTOWN
            r.CURRENTOWNERCOUNTY = r.ORIGINALOWNERCOUNTY
            r.CURRENTOWNERPOSTCODE = r.ORIGINALOWNERPOSTCODE
            r.CURRENTOWNERCOUNTRY = r.ORIGINALOWNERCOUNTRY
            r.CURRENTOWNERCITY = r.ORIGINALOWNERTOWN
            r.CURRENTOWNERSTATE = r.ORIGINALOWNERCOUNTY
            r.CURRENTOWNERZIPCODE = r.ORIGINALOWNERPOSTCODE
            r.CURRENTOWNERHOMETELEPHONE = r.ORIGINALOWNERHOMETELEPHONE
            r.CURRENTOWNERPHONE = r.ORIGINALOWNERHOMETELEPHONE
            r.CURRENTOWNERWORKTELEPHONE = r.ORIGINALOWNERWORKTELEPHONE
            r.CURRENTOWNERMOBILETELEPHONE = r.ORIGINALOWNERMOBILETELEPHONE
            r.CURRENTOWNERCELLPHONE = r.ORIGINALOWNERMOBILETELEPHONE
            r.CURRENTOWNEREMAILADDRESS = r.ORIGINALOWNEREMAILADDRESS

        if use_shelter_info:
            r.CURRENTOWNERNAME = organisation
            r.CURRENTOWNERTITLE = ""
            r.CURRENTOWNERINITIALS = ""
            r.CURRENTOWNERFORENAMES = "org." # Some providers validate against empty first names
            r.CURRENTOWNERSURNAME = organisation
            r.CURRENTOWNERADDRESS = orgaddress
            r.CURRENTOWNERTOWN = orgtown
            r.CURRENTOWNERCOUNTY = orgcounty
            r.CURRENTOWNERPOSTCODE = orgpostcode
            r.CURRENTOWNERCOUNTRY = orgcountry
            r.CURRENTOWNERCITY = orgtown
            r.CURRENTOWNERSTATE = orgcounty
            r.CURRENTOWNERZIPCODE = orgpostcode
            r.CURRENTOWNERHOMETELEPHONE = orgtelephone
            r.CURRENTOWNERPHONE = orgtelephone
            r.CURRENTOWNERWORKTELEPHONE = orgtelephone
            r.CURRENTOWNERMOBILETELEPHONE = orgtelephone
            r.CURRENTOWNERCELLPHONE = orgtelephone
            r.CURRENTOWNEREMAILADDRESS = email

        # If this row has IDENTICHIP2NUMBER and IDENTICHIP2DATE populated, clone the 
        # row and move the values to IDENTICHIPNUMBER and IDENTICHIPDATE for publishing
        if r.IDENTICHIP2NUMBER and r.IDENTICHIP2NUMBER != "":
            x = r.copy()
            x.IDENTICHIPNUMBER = x.IDENTICHIP2NUMBER
            x.IDENTICHIPDATE = x.IDENTICHIP2DATE
            extras.append(x)

    return rows + extras

def get_microchip_data_query(dbo: Database, patterns: List[str], publishername: str, movementtypes: str = "1", 
                             registerfrom: datetime = None, allowintake: bool = True) -> str:
    """
    Generates a query for unpublished microchips.
    It does this by looking for animals who have microchips matching the pattern where
        they either have an activemovement of a type with a date newer than sent in the published table
        OR they have a datebroughtin with a date newer than sent in the published table and they're a non-shelter animal
        (if intake is selected as movementtype 0)
        OR they have a datebroughtin with a date newer than sent in the published table, they're currently on shelter/not held
    patterns:      A list of either microchip prefixes or SQL clauses to OR
                   together in the preamble, eg: [ '977', "a.SmartTag = 1 AND a.SmartTagNumber <> ''" ]
    publishername: The name of the microchip registration publisher, eg: pettracuk
    movementtypes: An IN clause of movement types to include. 11 can be used for trial adoptions
    registerfrom: None for all, or a cut off date to only register chips where the event triggering reg was after this date
    """
    pclauses = []
    for p in patterns:
        if len(p) > 0 and p[0] in [ "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
            pclauses.append("(a.IdentichipNumber IS NOT NULL AND a.IdentichipNumber LIKE '%s%%')" % p)
            pclauses.append("(a.Identichip2Number IS NOT NULL AND a.Identichip2Number LIKE '%s%%')" % p)
        else:
            pclauses.append("(%s)" % p)
    if registerfrom is None:
        registerfrom = dbo.today(offset=-365*20) # No register from date set, go back 20 years
    trialclause = ""
    if movementtypes.find("11") == -1:
        trialclause = "AND a.HasTrialAdoption = 0"
    intakeclause = ""
    if movementtypes.find("0") != -1 and allowintake:
        # Note: Use of MostRecentEntryDate will pick up returns as well as intake
        intakeclause = "OR (a.NonShelterAnimal = 0 AND a.IsHold = 0 AND a.Archived = 0 " \
            "AND (a.ActiveMovementID = 0 OR a.ActiveMovementType = 2) " \
            "AND NOT EXISTS(SELECT SentDate FROM animalpublished WHERE PublishedTo = '%(publishername)s' " \
            "AND AnimalID = a.ID AND SentDate >= a.MostRecentEntryDate) " \
            "AND a.MostRecentEntryDate > %(regfrom)s " \
            ")" % { "publishername": publishername, "regfrom": dbo.sql_value(registerfrom) }
    nonshelterclause = "OR (a.NonShelterAnimal = 1 AND a.OriginalOwnerID Is Not Null " \
        "AND a.OriginalOwnerID > 0 AND a.IdentichipDate Is Not Null " \
        "AND NOT EXISTS(SELECT SentDate FROM animalpublished WHERE PublishedTo = '%(publishername)s' " \
        "AND AnimalID = a.ID AND SentDate >= a.IdentichipDate) " \
        "AND a.IdentichipDate > %(regfrom)s " \
        ")" % { "publishername": publishername, "regfrom": dbo.sql_value(registerfrom) }
    where = " WHERE (%(patterns)s) " \
        "AND a.DeceasedDate Is Null " \
        "AND a.Identichipped=1 " \
        "AND (a.IsNotForRegistration Is Null OR a.IsNotForRegistration=0) " \
        "AND (" \
        "(a.ActiveMovementID > 0 AND a.ActiveMovementType > 0 AND a.ActiveMovementType IN (%(movementtypes)s) %(trialclause)s " \
        "AND NOT EXISTS(SELECT SentDate FROM animalpublished WHERE PublishedTo = '%(publishername)s' " \
        "AND AnimalID = a.ID AND SentDate >= %(movementdate)s ) AND a.ActiveMovementDate > %(regfrom)s ) " \
        "%(nonshelterclause)s " \
        "%(intakeclause)s " \
        ")" % { 
            "patterns": " OR ".join(pclauses),
            # Using max of movementdate/movement.lastchanged prevents registration on intake 
            # on the same day preventing adopter registration
            "movementdate": dbo.sql_greatest([ "a.ActiveMovementDate", "am.LastChangedDate" ]), 
            "movementtypes": movementtypes, 
            "intakeclause": intakeclause,
            "nonshelterclause": nonshelterclause,
            "regfrom": dbo.sql_value(registerfrom), 
            "trialclause": trialclause,
            "publishername": publishername }
    sql = asm3.animal.get_animal_query(dbo) + where
    return sql

def get_adoption_status(dbo: Database, a: ResultRow) -> str:
    """
    Returns a string representing the animal's current adoption 
    status.
    """
    l = dbo.locale
    if a.ARCHIVED == 0 and a.CRUELTYCASE == 1: return asm3.i18n._("Cruelty Case", l)
    if a.ARCHIVED == 0 and a.ISQUARANTINE == 1: return asm3.i18n._("Quarantine", l)
    if a.ARCHIVED == 0 and a.ISHOLD == 1: return asm3.i18n._("Hold", l)
    if a.ARCHIVED == 0 and a.HASACTIVERESERVE == 1: return asm3.i18n._("Reserved", l)
    if a.ARCHIVED == 0 and a.HASPERMANENTFOSTER == 1: return asm3.i18n._("Permanent Foster", l)
    if is_animal_adoptable(dbo, a): return asm3.i18n._("Adoptable", l)
    return asm3.i18n._("Not available for adoption", l)

def is_animal_adoptable(dbo: Database, a: ResultRow) -> bool:
    """
    Returns True if the animal a is adoptable. This should match exactly the code in common.js / html.is_animal_adoptable
    """
    p = PublishCriteria(asm3.configuration.publisher_presets(dbo))
    if a.ISCOURTESY == 1: return True
    if a.ISNOTAVAILABLEFORADOPTION == 1: return False
    if a.NONSHELTERANIMAL == 1: return False
    if a.DECEASEDDATE is not None: return False
    if a.HASFUTUREADOPTION == 1: return False
    if a.HASACTIVEBOARDING == 1: return False
    if a.HASPERMANENTFOSTER == 1: return False
    if a.CRUELTYCASE == 1 and not p.includeCaseAnimals: return False
    if a.NEUTERED == 0 and not p.includeNonNeutered and str(a.SPECIESID) in asm3.configuration.alert_species_neuter(dbo).split(","): return False
    if a.IDENTICHIPPED == 0 and not p.includeNonMicrochipped and str(a.SPECIESID) in asm3.configuration.alert_species_microchip(dbo).split(","): return False
    if a.HASACTIVERESERVE == 1 and not p.includeReservedAnimals: return False
    if a.ISHOLD == 1 and not p.includeHold: return False
    if a.ISQUARANTINE == 1 and not p.includeQuarantine: return False
    if a.ACTIVEMOVEMENTTYPE == 2 and not p.includeFosterAnimals: return False
    if a.ACTIVEMOVEMENTTYPE == 8 and not p.includeRetailerAnimals: return False
    if a.ACTIVEMOVEMENTTYPE == 1 and a.HASTRIALADOPTION == 1 and not p.includeTrial: return False
    if a.ACTIVEMOVEMENTTYPE == 1 and a.HASTRIALADOPTION == 0: return False
    if a.ACTIVEMOVEMENTTYPE and a.ACTIVEMOVEMENTTYPE >= 3 and a.ACTIVEMOVEMENTTYPE <= 7: return False
    if not p.includeWithoutImage and a.WEBSITEMEDIANAME is None: return False
    if not p.includeWithoutDescription and asm3.configuration.publisher_use_comments(dbo) and a.ANIMALCOMMENTS == "": return False
    if not p.includeWithoutDescription and not asm3.configuration.publisher_use_comments(dbo) and a.WEBSITEMEDIANOTES == "": return False
    if p.excludeUnderWeeks > 0 and asm3.i18n.add_days(a.DATEOFBIRTH, 7 * p.excludeUnderWeeks) > dbo.today(): return False
    if p.excludeReserves > 0 and a.ACTIVERESERVATIONS > p.excludeReserves: return False
    if len(p.internalLocations) > 0 and a.ACTIVEMOVEMENTTYPE is None and str(a.SHELTERLOCATION) not in p.internalLocations: return False
    return True

class AbstractPublisher(threading.Thread):
    """
    Base class for all publishers
    """
    dbo = None
    pc = None
    totalAnimals = 0
    publisherName = ""
    publisherKey = ""
    publishDateTime = None
    successes = 0
    alerts = 0
    publishDir = ""
    tempPublishDir = True
    locale = "en"
    lastError = ""
    logBuffer = []

    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        threading.Thread.__init__(self)
        self.dbo = dbo
        self.locale = asm3.configuration.locale(dbo)
        self.pc = publishCriteria
        self.makePublishDirectory()

    def checkMappedSpecies(self) -> bool:
        """
        Returns True if all shelter animal species have been mapped for publishers.
        """
        return 0 == self.dbo.query_int("SELECT COUNT(*) FROM species " \
            "WHERE ID IN (SELECT SpeciesID FROM animal WHERE Archived=0) " \
            "AND (PetFinderSpecies Is Null OR PetFinderSpecies = '')")

    def checkMappedBreeds(self) -> bool:
        """
        Returns True if all shelter animal breeds have been mapped for publishers
        """
        return 0 == self.dbo.query_int("SELECT COUNT(*) FROM breed " + \
            "WHERE ID IN (SELECT BreedID FROM animal WHERE Archived=0 UNION SELECT Breed2ID FROM animal WHERE Archived=0) " \
            "AND (PetFinderBreed Is Null OR PetFinderBreed = '')")

    def checkMappedColours(self) -> bool:
        """
        Returns True if all shelter animal colours have been mapped for publishers
        """
        return 0 == self.dbo.query_int("SELECT COUNT(*) FROM basecolour " \
            "WHERE ID IN (SELECT BaseColourID FROM animal WHERE Archived=0) AND " \
            "(AdoptAPetColour Is Null OR AdoptAPetColour = '')")

    def csvLine(self, items: List[str]) -> str:
        """
        Takes a list of CSV line items and returns them as a comma 
        separated string, appropriately quoted and escaped.
        If any items are quoted, the quoting is removed before doing any escaping.
        """
        l = []
        for i in items:
            if i is None: i = ""
            # Remove start/end quotes if present
            if i.startswith("\""): i = i[1:]
            if i.endswith("\""): i = i[0:-1]
            # Escape any quotes in the value
            i = i.replace("\"", "\"\"")
            # Add quoting
            l.append("\"%s\"" % i)
        return ",".join(l)
    
    def getPhotoUrl(self, animalid: int) -> str:
        """
        Returns the URL for the preferred photo for animalid.
        """
        return f"{SERVICE_URL}?account={self.dbo.database}&method=animal_image&animalid={animalid}"

    def getPhotoUrls(self, animalid: int) -> List[str]:
        """
        Returns a list of photo URLs for animalid. The preferred is always first.
        """
        photo_urls = []
        photos = self.dbo.query("SELECT ID, Date FROM media " \
            "WHERE LinkTypeID = 0 AND LinkID = ? AND MediaMimeType = 'image/jpeg' " \
            "AND (ExcludeFromPublish = 0 OR ExcludeFromPublish Is Null) " \
            "ORDER BY WebsitePhoto DESC, ID", [animalid])
        for m in photos:
            ts = asm3.i18n.python2unix(m.DATE)
            photo_urls.append(f"{SERVICE_URL}?account={self.dbo.database}&method=media_image&mediaid={m.ID}&ts={ts}")
        return photo_urls

    def getPublisherBreed(self, an: ResultRow, b1or2: int = 1) -> str:
        """
        Encapsulates logic for reading publisher breed fields.
        an: The animal row
        b1or2: Whether to get breed 1 or 2
        return value is the publisher breed for datafiles/posts. It can be a blank
        based on whether the animal is a crossbreed or not.
        """
        crossbreed = an["CROSSBREED"]
        breed1id = an["BREEDID"]
        breed2id = an["BREED2ID"]
        breedname = an["BREEDNAME1"]
        publisherbreed = an["PETFINDERBREED"]
        # We're dealing with the first breed field. Always send the mapped
        # publisher breed if it isn't a crossbreed animal
        if b1or2 == 1:
            if crossbreed == 0: 
                return publisherbreed
        # We're dealing with the second breed field. Always send that as a blank
        # if this isn't a crossbreed animal
        elif b1or2 == 2:
            breedname = an["BREEDNAME2"]
            publisherbreed = an["PETFINDERBREED2"]
            if crossbreed == 0: 
                return ""
        # If one of our magic words is found, or both breeds are the
        # same, return a blank. By the time we get here, crossbreed must == 1
        b = asm3.utils.nulltostr(breedname).lower()
        if b == "mix" or b == "cross" or b == "unknown" or b == "crossbreed" or breed1id == breed2id:
            return ""
        # Don't return null
        if publisherbreed is None:
            return ""
        return publisherbreed

    def isPublisherExecuting(self) -> bool:
        """
        Returns True if a publisher is already currently running against
        this database. If the ignoreLock publishCriteria option has been
        set, always returns false.
        """
        if self.pc.ignoreLock: return False
        return asm3.asynctask.is_task_running(self.dbo)

    def updatePublisherProgress(self, progress: int) -> None:
        """
        Updates the publisher progress in the database
        """
        asm3.asynctask.set_task_name(self.dbo, self.publisherName)
        asm3.asynctask.set_progress_max(self.dbo, 100)
        asm3.asynctask.set_progress_value(self.dbo, progress)

    def replaceMDBTokens(self, dbo: Database, s: str) -> str:
        """
        Replace MULTIPLE_DATABASE tokens in the string given (redundant)
        """
        s = s.replace("{alias}", dbo.alias)
        s = s.replace("{database}", dbo.database)
        s = s.replace("{username}", dbo.username)
        return s

    def replaceAnimalTags(self, a: ResultRow, s: str) -> str:
        """
        Replace any $$Tag$$ tags in s, using animal a
        """
        tags = asm3.wordprocessor.animal_tags_publisher(self.dbo, a)
        return asm3.wordprocessor.substitute_tags(s, tags, True, "$$", "$$", cr_to_br = False)

    def resetPublisherProgress(self) -> None:
        """
        Resets the publisher progress and stops blocking for other 
        publishers
        """
        asm3.asynctask.reset(self.dbo)

    def setPublisherComplete(self) -> None:
        """
        Mark the current publisher as complete
        """
        asm3.asynctask.set_progress_value(self.dbo, 100)

    def getProgress(self, i: int, n: int) -> int:
        """
        Returns a progress percentage
        i: Current position
        n: Total elements
        """
        return int((float(i) / float(n)) * 100)

    def shouldStopPublishing(self) -> bool:
        """
        Returns True if we need to stop publishing
        """
        return asm3.asynctask.get_cancel(self.dbo)

    def setStartPublishing(self) -> None:
        """
        Clears the stop publishing flag so we can carry on publishing.
        """
        asm3.asynctask.set_cancel(self.dbo, False)

    def setLastError(self, msg: str, log_error: bool = True) -> None:
        """
        Sets the last error message and clears the publisher lock
        """
        asm3.asynctask.set_last_error(self.dbo, msg)
        self.lastError = msg
        if msg != "" and log_error: self.logError(self.lastError)
        self.resetPublisherProgress()

    def cleanup(self, save_log: bool = True) -> None:
        """
        Call when the publisher has completed to tidy up.
        """
        if save_log: self.saveLog()
        self.setPublisherComplete()

    def splitAddress(self, address: str) -> Dict[str, str]:
        """
        Splits the OWNERADDRESS column and returns a dict of address elements.
        """
        o = { "houseno": "", "streetname": "", "line1": "", "line2": "", "csv": ""}
        if address is None: address = ""
        address = address.strip()
        o["csv"] = address.replace("\n", ", ")
        b = address.split("\n")
        if len(b) > 0: o["line1"] = b[0]
        if len(b) > 1: o["line2"] = b[1]
        b = o["line1"].split(" ", 1)
        if len(b) == 2 and asm3.utils.is_numeric(b[0]):
            o["houseno"] = b[0]
            o["streetname"] = b[1]
        return o

    def makePublishDirectory(self) -> None:
        """
        Creates a temporary publish directory if one isn't set, or uses
        the one set in the criteria.
        """
        if self.publisherKey == "html":
            if self.pc.publishDirectory is not None and self.pc.publishDirectory.strip() != "":
                # The user has set a target directory for their HTML publishing, use that
                self.publishDir = self.pc.publishDirectory
                # Fix any Windows path backslashes that could have been doubled up
                if self.publishDir.find("\\\\") != -1:
                    self.publishDir = self.publishDir.replace("\\\\", "\\")
                # Validate that the directory exists
                if not os.path.exists(self.publishDir):
                    self.setLastError("publishDir does not exist: %s" % self.publishDir)
                    return
                # If they've set the option to reupload animal images, clear down
                # any existing images first
                if self.pc.forceReupload:
                    for f in os.listdir(self.publishDir):
                        if f.lower().endswith(".jpg"):
                            os.unlink(os.path.join(self.publishDir, f))
                # Clear out any existing HTML pages
                for f in os.listdir(self.publishDir):
                    if f.lower().endswith(".html"):
                        os.unlink(os.path.join(self.publishDir, f))
                self.tempPublishDir = False
                return
        # Use a temporary folder for publishing
        self.tempPublishDir = True
        self.publishDir = tempfile.mkdtemp()

    def deletePublishDirectory(self) -> None:
        """
        Removes the publish directory if it was temporary
        """
        if self.tempPublishDir:
            shutil.rmtree(self.publishDir, True)

    def replaceSmartQuotes(self, s: str) -> str:
        """
        Replaces well known "smart" quotes/points with ASCII characters (mainly aimed at smartquotes)
        """
        ENTITIES = {
            "\u00b4": "'",  # spacing acute
            "\u2013": "-",  # endash
            "\u2014": "--", # emdash
            "\u2018": "'",  # left single quote
            "\u2019": "'",  # right single quote
            "\u201a": ",",  # single low quote (comma)
            "\u201c": "\"", # left double quotes
            "\u201d": "\"", # right double quotes
            "\u201e": ",,", # double low quote (comma comma)
            "\u2022": "*",  # bullet
            "\u2026": "...",# ellipsis
            "\u2032": "'",  # prime (stopwatch)
            "\u2033": "\"", # double prime,
            "\u2713": "/",  # check
            "\u2714": "/",  # heavy check
            "\u2715": "x",  # multiplication x
            "\u2716": "x",  # heavy multiplication x
            "\u2717": "x",  # ballot x
            "\u2718": "x"   # heavy ballot x
        }
        for k, v in ENTITIES.items():
            s = s.replace(k, v)
        return s

    def getLocaleForCountry(self, c: str) -> str:
        """
        Some third party sites only accept a locale in their country field rather than
        a name. This is most common in the US where some shelters have dealings with
        people over the border in Mexico and Canada.
        """
        c2l = {
            "United States of America": "US",
            "United States":            "US",
            "USA":                      "US",
            "Mexico":                   "MX",
            "Canada":                   "CA"
        }
        if c is None or c == "": return "US" # Assume US as this is only really used by US publishers
        if len(c) == 2: return c # Already a country code
        for k in c2l.keys():
            if c.lower() == k.lower():
                return c2l[k]
        return "US" # Fall back to US if no match

    def getDescription(self, an: ResultRow, crToBr = False, crToHE = False, crToLF = True, replaceSmart = False) -> str:
        """
        Returns the description/bio for an asm3.animal.
        an: The animal record
        crToBr: Convert line breaks to <br /> tags
        crToHE: Convert line breaks to html entity &#10;
        crToLF: Convert line breaks to LF
        replaceSmart: Replace smart quotes (mainly apostrophes and quotes) with regular ASCII
        """
        # Note: WEBSITEMEDIANOTES becomes ANIMALCOMMENTS in get_animal_data when publisher_use_comments is on
        notes = asm3.utils.nulltostr(an["WEBSITEMEDIANOTES"])
        # Add any extra text as long as this isn't a courtesy listing
        if an["ISCOURTESY"] != 1: 
            sig = asm3.configuration.third_party_publisher_sig(self.dbo)
            # If publisher tokens are present, replace them
            if sig.find("$$") != -1: sig = self.replaceAnimalTags(an, sig)
            notes += sig
        # Escape carriage returns
        cr = ""
        if crToBr: cr = "<br>"
        elif crToHE: cr = "&#10;"
        elif crToLF: cr = "\n"
        notes = notes.replace("\r\n", cr)
        notes = notes.replace("\r", cr)
        notes = notes.replace("\n", cr)
        # Smart quotes and apostrophes
        if replaceSmart:
            notes = self.replaceSmartQuotes(notes)
        # Escape speechmarks - disabled 27/12/2023, why were we doing this? Where is a double double-quote the escape method?
        # notes = notes.replace("\"", "\"\"")
        return notes

    def getLastPublishedDate(self, animalid: int) -> datetime:
        """
        Returns the last date animalid was sent to the current publisher
        """
        return self.dbo.query_date("SELECT SentDate FROM animalpublished WHERE AnimalID = ? AND PublishedTo = ?", (animalid, self.publisherKey))

    def isChangedSinceLastPublish(self) -> bool:
        """
        Returns True if there have been relevant changes since the last time this publisher ran. 
        Publishers can use this call to decide to do nothing if there have been no changes.
        Relevant changes are: 
            Changes to an animal, movement or media record.
            The system configuration has changed.
        """
        lastpublished = self.dbo.query_date("SELECT MAX(SentDate) FROM animalpublished WHERE PublishedTo = ?", [self.publisherKey])
        if lastpublished is None: return True # publisher has never run
        changes = self.dbo.query_named_params("SELECT ID FROM animal WHERE LastChangedDate > :lp " \
            "UNION SELECT ID FROM adoption WHERE LastChangedDate > :lp " \
            "UNION SELECT ID FROM media WHERE Date > :lp " \
            "UNION SELECT LinkID FROM audittrail WHERE TableName='configuration' AND Action=1 AND AuditDate > :lp ", \
            { "lp": self.dbo.sql_value(lastpublished) })
        return len(changes) > 0

    def markAnimalPublished(self, animalid: int, datevalue: datetime = None, extra: str = "") -> None:
        """
        Marks an animal published at the current date/time for this publisher
        animalid:    The animal id to update
        extra:       The extra text field to set
        """
        if datevalue is None: datevalue = self.dbo.now()
        self.markAnimalUnpublished(animalid)
        self.dbo.insert("animalpublished", {
            "AnimalID":     animalid,
            "PublishedTo":  self.publisherKey,
            "SentDate":     datevalue,
            "Extra":        extra
        }, generateID=False)

    def markAnimalFirstPublished(self, animalid: int) -> None:
        """
        Marks an animal as published to a special "first" publisher - but only if it 
        hasn't been already. This allows the Publishing History to show not only the last
        but the very first time an animal has been published anywhere and effectively
        the date the animal was first made adoptable.
        """
        FIRST_PUBLISHER = "first"
        if 0 == self.dbo.query_int("SELECT COUNT(SentDate) FROM animalpublished WHERE AnimalID = ? AND PUblishedTo = ?",(animalid, FIRST_PUBLISHER)):
            self.dbo.insert("animalpublished", {
                "AnimalID":     animalid,
                "PublishedTo":  FIRST_PUBLISHER,
                "SentDate":     self.dbo.now()
            }, generateID=False)

    def markAnimalUnpublished(self, animalid: int) -> None:
        """
        Marks an animal as not published for the current publisher
        """
        self.dbo.delete("animalpublished", "AnimalID=%d AND PublishedTo='%s'" % (animalid, self.publisherKey))

    def markAnimalsPublished(self, animals: Results, first: bool = False) -> None:
        """
        Marks all animals in the set as published at the current date/time
        for the current publisher.
        first: This is an adoptable animal publisher, mark the animal first published for adoption
        """
        batch = []
        inclause = []
        # build a list of IDs and deduplicate them
        for a in animals:
            inclause.append( str(a["ID"]) )
        inclause = set(inclause)
        # build a batch for inserting animalpublished entries into the table
        # and check/mark animals first published
        for i in inclause:
            batch.append( ( int(i), self.publisherKey, self.dbo.now() ) )
            if first: self.markAnimalFirstPublished(int(i))
        if len(inclause) == 0: return
        self.dbo.execute("DELETE FROM animalpublished WHERE PublishedTo = '%s' AND AnimalID IN (%s)" % (self.publisherKey, ",".join(inclause)))
        self.dbo.execute_many("INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) VALUES (?,?,?)", batch)

    def markAnimalsPublishFailed(self, animals: Results) -> None:
        """
        Marks all animals in the set as published at the current date/time
        for the current publisher but with an extra failure message
        """
        batch = []
        inclause = {}
        # build a list of IDs and deduplicate them
        for a in animals:
            m = ""
            if "FAILMESSAGE" in a:
                m = a["FAILMESSAGE"]
            inclause[str(a["ID"])] = m
        # build a batch for inserting animalpublished entries into the table
        for k, v in inclause.items():
            batch.append( ( int(k), self.publisherKey, self.dbo.now(), v ) )
        if len(inclause) == 0: return
        self.dbo.execute("DELETE FROM animalpublished WHERE PublishedTo = '%s' AND AnimalID IN (%s)" % (self.publisherKey, ",".join(inclause)))
        self.dbo.execute_many("INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate, Extra) VALUES (?,?,?,?)", batch)

    def getMatchingAnimals(self, includeAdditionalFields: bool = False) -> Results:
        a = get_animal_data(self.dbo, self.pc, include_additional_fields=includeAdditionalFields, publisher_key=self.publisherKey)
        self.log("Got %d matching animals for publishing." % len(a))
        return a
    
    def isCrossBreed(self, a: ResultRow) -> bool:
        """ Returns True if the animal a is a crossbreed. """
        cross = a.CROSSBREED == 0
        if a.BREEDID in asm3.configuration.publish_as_crossbreed(self.dbo):
            cross = True
        return cross

    def saveFile(self, path: str, contents: str) -> None:
        try:
            asm3.utils.write_text_file(path, contents)
        except Exception as err:
            self.logError(str(err), sys.exc_info())

    def initLog(self, publisherKey: str, publisherName: str) -> None:
        """
        Initialises the log 
        """
        self.publisherKey = publisherKey
        self.publishDateTime = self.dbo.now()
        self.publisherName = publisherName
        self.logBuffer = []

    def log(self, msg: str) -> None:
        """
        Logs a message
        """
        self.logBuffer.append(msg)

    def logError(self, msg: str, ie: Any = None) -> None:
        """
        Logs a message to our logger and dumps a stacktrace.
        ie = error info object from sys.exc_info() if available
        """
        self.log("ALERT: %s" % msg)
        asm3.al.error(msg, self.publisherName, self.dbo, ie)
        self.alerts += 1

    def logSearch(self, needle: str) -> str:
        """ Does a find on logBuffer """
        return "\n".join(self.logBuffer).find(needle)

    def logSuccess(self, msg: str) -> None:
        """
        Logs a success message to our logger
        """
        self.log("SUCCESS: %s" % msg)
        asm3.al.info(msg, self.publisherName, self.dbo)
        self.successes += 1

    def saveLog(self) -> None:
        """
        Saves the log to the publishlog table
        """
        self.dbo.insert("publishlog", {
            "PublishDateTime":      self.publishDateTime,
            "Name":                 self.publisherKey,
            "Success":              self.successes,
            "Alerts":               self.alerts,
            "*LogData":              "\n".join(self.logBuffer)
        })

    def isImage(self, path: str) -> bool:
        """
        Returns True if the path given has a valid image extension
        """
        return path.lower().endswith("jpg") or path.lower().endswith("jpeg")

    def generateThumbnail(self, image: str, thumbnail: str) -> None:
        """
        Generates a thumbnail 
        image: Path to the image to generate a thumbnail from
        thumbnail: Path to the target thumbnail image
        """
        self.log("generating thumbnail %s -> %s" % ( image, thumbnail ))
        try:
            asm3.media.scale_image_file(image, thumbnail, self.pc.thumbnailSize)
        except Exception as err:
            self.logError("Failed scaling thumbnail: %s" % err, sys.exc_info())

    def scaleImage(self, image: bytes, scalesize: str) -> None:
        """
        Scales an image. scalesize is the scaleImage publish criteria and
        can either be a resize spec, or it can be one of our old ASM2
        fixed numbers.
        image: The image file
        Empty string = No scaling
        1 = No scaling
        2 = 320x200
        3 = 640x400
        4 = 800x600
        5 = 1024x768
        6 = 300x300
        7 = 95x95
        """
        sizespec = ""
        if scalesize == "" or scalesize == "1": return image
        elif scalesize == "2": sizespec = "320x200"
        elif scalesize == "3": sizespec = "640x400"
        elif scalesize == "4": sizespec = "800x600"
        elif scalesize == "5": sizespec = "1024x768"
        elif scalesize == "6": sizespec = "300x300"
        elif scalesize == "7": sizespec = "95x95"
        else: sizespec = scalesize
        self.log("scaling %s to %s" % ( image, scalesize ))
        try:
            return asm3.media.scale_image_file(image, image, sizespec)
        except Exception as err:
            self.logError("Failed scaling image: %s" % err, sys.exc_info())

class FTP_TLS_REUSE(ftplib.FTP_TLS):
    """A subclass of FTP_TLS that forces reuse of the socket that already did
       TLS. Needed for some instances of vsftpd """
    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            conn = self.context.wrap_socket(conn,
                                            server_hostname=self.host,
                                            session=self.sock.session)  # this is the fix
        return conn, size

class FTPPublisher(AbstractPublisher):
    """
    Base class for publishers that rely on FTP
    """
    socket = None
    ftphost = ""
    ftpuser = ""
    ftppassword = ""
    ftpport = 21
    ftproot = ""
    ftptls = False
    currentDir = ""
    passive = True
    existingImageList = None

    def __init__(self, dbo: Database, publishCriteria: PublishCriteria, 
                 ftphost: str, ftpuser: str, ftppassword: str, ftptls: bool = False, 
                 ftpport: int = 21, ftproot: str = "", passive: bool = True) -> None:
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.ftphost = ftphost.strip()
        self.ftpuser = ftpuser.strip()
        self.ftppassword = self.unxssPass(ftppassword)
        self.ftpport = ftpport
        self.ftproot = ftproot
        self.ftptls = ftptls
        self.passive = passive

    def unxssPass(self, s: str) -> str:
        """
        Passwords stored in the config table are subject to XSS escaping, so
        any >, < or & in the password will have been escaped - turn them back again.
        Also, many people copy and paste FTP passwords for PetFinder and AdoptAPet
        and include extra spaces on the end, so strip it.
        """
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        s = s.replace("&amp;", "&")
        s = s.strip()
        return s

    def openFTPSocket(self) -> bool:
        """
        Opens an FTP socket to the server and changes to the
        root FTP directory. Returns True if all was well or
        uploading is disabled.
        """
        if not self.pc.uploadDirectly: return True
        if self.ftphost == "": raise ValueError("No FTP host set")
        self.log("Connecting to %s as %s" % (self.ftphost, self.ftpuser))
        
        try:
            # open it and login
            if self.ftptls:
                self.socket = FTP_TLS_REUSE(host=self.ftphost, timeout=FTP_CONNECTION_TIMEOUT)
            else:
                self.socket = ftplib.FTP(host=self.ftphost, timeout=FTP_CONNECTION_TIMEOUT)
            self.socket.login(self.ftpuser, self.ftppassword)
            if self.ftptls: 
                self.socket.prot_p()
            self.socket.set_pasv(self.passive)

            if self.ftproot is not None and self.ftproot != "":
                self.chdir(self.ftproot)

            return True
        except Exception as err:
            self.logError("Failed opening FTP socket (%s->%s): %s" % (self.dbo.database, self.ftphost, err), sys.exc_info())
            return False

    def closeFTPSocket(self) -> None:
        if not self.pc.uploadDirectly: return
        try:
            self.socket.quit()
        except:
            pass

    def reconnectFTPSocket(self) -> None:
        """
        Reconnects to the FTP server, changing back to the current directory.
        """
        self.closeFTPSocket()
        self.openFTPSocket()
        if not self.currentDir == "":
            self.chdir(self.currentDir)

    def checkFTPSocket(self) -> None:
        """
        Called before each upload if publishCriteria.checkSocket is
        set to true. It verifies that the socket is still active
        by running a command. If the command fails, the socket is
        reopened and the current FTP directory is returned to.
        """
        if not self.pc.uploadDirectly: return
        try:
            self.socket.retrlines("LIST", quietcallback)
        except Exception as err:
            self.log("Dead socket (%s), reconnecting" % err)
            self.reconnectFTPSocket()

    def upload(self, filename: str) -> None:
        """
        Uploads a file to the current FTP directory. If a full path
        is given, this throws it away and just uses the name with
        the temporary publishing directory.
        """
        if filename.find(os.sep) != -1: filename = filename[filename.rfind(os.sep) + 1:]
        if not self.pc.uploadDirectly: return
        if not os.path.exists(os.path.join(self.publishDir, filename)): return
        self.log("Uploading: %s" % filename)
        try:
            if self.pc.checkSocket: self.checkFTPSocket()
            # Store the file
            f = open(os.path.join(self.publishDir, filename), "rb")
            self.socket.storbinary("STOR %s" % filename, f, callback=quietcallback)
            f.close()
        except Exception as err:
            self.logError("Failed uploading %s: %s" % (filename, err), sys.exc_info())
            self.log("reconnecting FTP socket to reset state")
            self.reconnectFTPSocket()

    def lsdir(self) -> List[str]:
        if not self.pc.uploadDirectly: return []
        try:
            return self.socket.nlst()
        except Exception as err:
            self.logError("list: %s" % err)

    def mkdir(self, newdir: str) -> None:
        if not self.pc.uploadDirectly: return
        self.log("FTP mkdir %s" % newdir)
        try:
            self.socket.mkd(newdir)
        except Exception as err:
            self.log("mkdir %s: already exists (%s)" % (newdir, err))

    def chdir(self, newdir: str, fromroot: str) -> bool:
        """ Changes FTP folder. 
            newdir: The folder to change into
            fromroot: The path to this folder from the root for recovery/reconnection
            Returns True on success, False for failure """
        if not self.pc.uploadDirectly: return True
        self.log("FTP chdir to %s" % newdir)
        try:
            self.socket.cwd(newdir)
            self.currentDir = fromroot
            return True
        except Exception as err:
            self.logError("chdir %s: %s" % (newdir, err), sys.exc_info())
            return False

    def delete(self, filename: str) -> None:
        try:
            self.socket.delete(filename)
        except Exception as err:
            self.log("delete %s: %s" % (filename, err))

    def clearExistingHTML(self) -> None:
        try:
            oldfiles = glob.glob(os.path.join(self.publishDir, "*." + self.pc.extension))
            for f in oldfiles:
                os.remove(f)
        except Exception as err:
            self.logError("warning: failed removing %s from filesystem: %s" % (oldfiles, err), sys.exc_info())
        if not self.pc.uploadDirectly: return
        try:
            for f in self.socket.nlst("*.%s" % self.pc.extension):
                if not f.startswith("search"):
                    self.socket.delete(f)
        except Exception as err:
            self.logError("warning: failed deleting from FTP server: %s" % err, sys.exc_info())

    def clearExistingImages(self) -> None:
        try:
            oldfiles = glob.glob(os.path.join(self.publishDir, "*.jpg"))
            for f in oldfiles:
                os.remove(f)
        except Exception as err:
            self.logError("warning: failed removing %s from filesystem: %s" % (oldfiles, err), sys.exc_info())
        if not self.pc.uploadDirectly: return
        try:
            for f in self.socket.nlst("*.jpg"):
                self.socket.delete(f)
        except Exception as err:
            self.logError("warning: failed deleting from FTP server: %s" % err, sys.exc_info())

    def clearUnusedFTPImages(self, animals: Results) -> None:
        """ given a set of animals, removes images from the current FTP folder that do not
            start with a sheltercode that is in the list of animals """
        sheltercodes = [x.SHELTERCODE for x in animals]
        # self.log("removing unused images (valid prefixes = %s)" % sheltercodes)
        try:
            nlst = self.socket.nlst("*.jpg")
            # self.log("NLST: %s" % nlst)
            for f in nlst:
                c = f[:f.find("-")]
                if c not in sheltercodes: 
                    self.log("delete unreferenced image: %s" % f)
                    self.socket.delete(f)
        except Exception as err:
            self.logError("warning: failed deleting from FTP server: %s" % err, sys.exc_info())

    def cleanup(self, save_log: bool = True) -> None:
        """
        Call when the publisher has completed to tidy up.
        """
        self.closeFTPSocket()
        self.deletePublishDirectory()
        if save_log: self.saveLog()
        self.setPublisherComplete()

    def uploadImage(self, a: ResultRow, mediaid: int, medianame: str, imagename: str) -> None:
        """
        Retrieves image with mediaid from the DBFS to the publish
        folder and uploads it via FTP with imagename
        """
        try:
            # Check if the image is already on the server if 
            # forceReupload is off and the animal doesn't
            # have any recently changed images
            if not self.pc.forceReupload and a.RECENTLYCHANGEDIMAGES == 0:
                if self.existingImageList is None:
                    self.existingImageList = self.lsdir()
                elif imagename in self.existingImageList:
                    self.log("%s: skipping, already on server" % imagename)
                    return
            dbfsid = self.dbo.query_int("SELECT DBFSID FROM media WHERE ID=?", [mediaid])
            if dbfsid == 0:
                self.log("%s: skipping, no DBFSID link for media id %s" % (imagename, mediaid))
                return
            imagefile = os.path.join(self.publishDir, imagename)
            thumbnail = os.path.join(self.publishDir, "tn_" + imagename)
            asm3.dbfs.get_file_id(self.dbo, dbfsid, imagefile)
            self.log("Retrieved image: %d::%s::%s" % ( a["ID"], medianame, imagename ))
            # If scaling is on, do it
            if str(self.pc.scaleImages) in ( "2", "3", "4", "5", "6", "7" ) or str(self.pc.scaleImages).find("x") > -1:
                self.scaleImage(imagefile, self.pc.scaleImages)
            # If thumbnails are on, do it
            if self.pc.thumbnails:
                self.generateThumbnail(imagefile, thumbnail)
            # Upload
            if self.pc.uploadDirectly:
                self.upload(imagefile)
                if self.pc.thumbnails:
                    self.upload(thumbnail)
        except Exception as err:
            self.logError("Failed uploading image %s: %s" % (medianame, err), sys.exc_info())
            return 0

    def uploadImages(self, a: ResultRow, copyWithMediaIDAsName: bool = False, limit: int = 0) -> None:
        """
        Uploads all the images for an animal as sheltercode-X.jpg if
        upload all is on, or just sheltercode.jpg if upload all is off.
        If copyWithMediaIDAsName is on, it uploads the preferred
        image again and calls it mediaID.jpg (for compatibility with
        older templates).
        Even if uploadDirectly is off, we still pull the images to the
        publish folder.
        If limit is set to zero and uploadAll is on, all images
        are uploaded. If uploadAll is off, only the preferred
        image is uploaded.
        Images with the ExcludeFromPublish flag set are ignored.
        """
        # The first image is always the preferred
        totalimages = 0
        animalcode = a.SHELTERCODE
        animalweb = a.WEBSITEMEDIANAME
        animalwebid = a.WEBSITEMEDIAID
        if animalweb is None or animalweb == "": return totalimages
        # If we've got HTML entities in our sheltercode, it's going to
        # mess up filenames. Use the animalid instead.
        if animalcode.find("&#") != -1:
            animalcode = str(a.ID)
        # Name it sheltercode-1.jpg or sheltercode.jpg if uploadall is off
        imagename = animalcode + ".jpg"
        if self.pc.uploadAllImages:
            imagename = animalcode + "-1.jpg"
        # If we're forcing reupload or the animal has
        # some recently changed images, remove all the images
        # for this animal before doing anything.
        if self.pc.forceReupload or a.RECENTLYCHANGEDIMAGES > 0:
            if self.existingImageList is None:
                self.existingImageList = self.lsdir()
            for ei in self.existingImageList:
                if ei.startswith(animalcode):
                    self.log("delete: %s" % ei)
                    self.delete(ei)
        # Save it to the publish directory
        totalimages = 1
        self.uploadImage(a, animalwebid, animalweb, imagename)
        # If we're saving a copy with the media ID, do that too
        if copyWithMediaIDAsName:
            self.uploadImage(a, animalwebid, animalweb, animalweb)
        # If upload all is set, we need to grab the rest of
        # the animal's images upto the limit. If the limit is
        # zero, we upload everything.
        if self.pc.uploadAllImages:
            mrecs = asm3.media.get_image_media(self.dbo, asm3.media.ANIMAL, a["ID"], True)
            self.log("Animal has %d media files (%d recently changed)" % (len(mrecs), a["RECENTLYCHANGEDIMAGES"]))
            for m in mrecs:
                # Ignore the main media since we used that
                if m.ID == animalwebid:
                    continue
                # Have we hit our limit?
                if totalimages == limit:
                    return totalimages
                totalimages += 1
                # Get the image
                otherpic = m.MEDIANAME
                otherpicid = m.ID
                imagename = "%s-%d.jpg" % ( animalcode, totalimages )
                self.uploadImage(a, otherpicid, otherpic, imagename)
        return totalimages


