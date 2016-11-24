#!/usr/bin/python

"""
    Module containing all functions/classes for internet publishing
"""

import al
import additional
import animal
import async
import configuration
import datetime, time
import db
import dbfs
import ftplib
import html
import i18n
import lookups
import lostfound
import math
import media
import medical
import movement
import onlineform
import os, glob
import re
import shutil
import smcom
import sys
import tempfile
import threading
import users
import utils
import wordprocessor
from sitedefs import BASE_URL, MULTIPLE_DATABASES_PUBLISH_DIR, MULTIPLE_DATABASES_PUBLISH_FTP, MULTIPLE_DATABASES_PUBLISH_URL, ADOPTAPET_FTP_HOST, ANIBASE_BASE_URL, ANIBASE_API_USER, ANIBASE_API_KEY, FOUNDANIMALS_FTP_HOST, FOUNDANIMALS_FTP_USER, FOUNDANIMALS_FTP_PASSWORD, HELPINGLOSTPETS_FTP_HOST, PETFINDER_FTP_HOST, PETRESCUE_FTP_HOST, PETSLOCATED_FTP_HOST, PETSLOCATED_FTP_USER, PETSLOCATED_FTP_PASSWORD, RESCUEGROUPS_FTP_HOST, SMARTTAG_FTP_HOST, SMARTTAG_FTP_USER, SMARTTAG_FTP_PASSWORD, PETTRAC_UK_POST_URL, MEETAPET_BASE_URL, PETLINK_BASE_URL, SERVICE_URL, VETENVOY_US_VENDOR_USERID, VETENVOY_US_VENDOR_PASSWORD, VETENVOY_US_HOMEAGAIN_RECIPIENTID, VETENVOY_US_AKC_REUNITE_RECIPIENTID, VETENVOY_US_BASE_URL, VETENVOY_US_SYSTEM_ID

class PublishCriteria:
    """
    Class containing publishing criteria. Has functions to 
    convert to and from a command line string
    """
    includeCaseAnimals = False
    includeReservedAnimals = False
    includeRetailerAnimals = False
    includeFosterAnimals = False
    includeQuarantine = False
    includeTrial = False
    includeHold = False
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
    limit = 0
    style = "."
    extension = "html"
    scaleImages = "" # A resize spec or old values of: 1 = None, 2 = 320x200, 3=640x480, 4=800x600, 5=1024x768, 6=300x300, 7=95x95
    internalLocations = [] # List of either location IDs, or LIKE comparisons
    publishDirectory = None # None = use temp directory for publishing
    ignoreLock = False # Force the publisher to run even if another publisher is running

    def get_int(self, s):
        """
        Returns the val portion of key=val as an int
        """
        return utils.cint(s.split("=")[1])

    def get_str(self, s):
        """
        Returns the val portion of key=val as a string
        """
        return s.split("=")[1]

    def __init__(self, fromstring = ""):
        """
        Initialises the publishing criteria from a string if given
        """
        if fromstring == "": return
        for s in fromstring.split(" "):
            if s == "includecase": self.includeCaseAnimals = True
            if s == "includereserved": self.includeReservedAnimals = True
            if s == "includeretailer": self.includeRetailerAnimals = True
            if s == "includefosters": self.includeFosterAnimals = True
            if s == "includehold": self.includeHold = True
            if s == "includequarantine": self.includeQuarantine = True
            if s == "includetrial": self.includeTrial = True
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
            if s.startswith("animalsperpage"): self.animalsPerPage = self.get_int(s)
            if s.startswith("limit"): self.limit = self.get_int(s)
            if s.startswith("style"): self.style = self.get_str(s)
            if s.startswith("extension"): self.extension = self.get_str(s)
            if s.startswith("scaleimages"): self.scaleImages = self.get_str(s)
            if s.startswith("thumbnailsize"): self.thumbnailSize = self.get_str(s)
            if s.startswith("includelocations"): self.internalLocations = self.get_str(s).split(",")
            if s.startswith("publishdirectory"): self.publishDirectory = self.get_str(s)
            if s.startswith("childadultsplit"): self.childAdultSplit = self.get_int(s)

    def __str__(self):
        """
        Returns a string representation of the criteria (which corresponds
        exactly to an ASM 2.x command line string to a publisher)
        """
        s = ""
        if self.includeCaseAnimals: s += " includecase"
        if self.includeReservedAnimals: s += " includereserved"
        if self.includeRetailerAnimals: s += " includeretailer"
        if self.includeFosterAnimals: s += " includefosters"
        if self.includeHold: s += " includehold"
        if self.includeQuarantine: s += " includequarantine"
        if self.includeTrial: s += " includetrial"
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
        s += " animalsperpage=" + str(self.animalsPerPage)
        s += " limit=" + str(self.limit)
        s += " style=" + str(self.style)
        s += " extension=" + str(self.extension)
        s += " scaleimages=" + str(self.scaleImages)
        s += " thumbnailsize=" + str(self.thumbnailSize)
        s += " childadultsplit=" + str(self.childAdultSplit)
        s += " outputadopteddays=" + str(self.outputAdoptedDays)
        if len(self.internalLocations) > 0: s += " includelocations=" + ",".join(self.internalLocations)
        if self.publishDirectory is not None: s += " publishdirectory=" + self.publishDirectory
        return s.strip()

def quietcallback(x):
    """ ftplib callback that does nothing instead of dumping to stdout """
    pass

def get_animal_data(dbo, pc, include_additional_fields = False):
    """
    Returns a resultset containing the animal info for the criteria given. 
    """
    sql = get_animal_data_query(dbo, pc)
    rows = db.query(dbo, sql)
    # If the sheltercode format has a slash in it, convert it to prevent
    # creating images with broken paths.
    if len(rows) > 0 and rows[0]["SHELTERCODE"].find("/") != -1:
        for r in rows:
            r["SHORTCODE"] = r["SHORTCODE"].replace("/", "-").replace(" ", "")
            r["SHELTERCODE"] = r["SHELTERCODE"].replace("/", "-").replace(" ", "")
    # If we're using animal comments, override the websitemedianotes field
    # with animalcomments for compatibility with service users and other
    # third parties who were used to the old way of doing things
    if configuration.publisher_use_comments(dbo):
        for r in rows:
            r["WEBSITEMEDIANOTES"] = r["ANIMALCOMMENTS"]
    # Embellish additional fields if requested
    if include_additional_fields:
        for r in rows:
            add = additional.get_additional_fields(dbo, int(r["ID"]), "animal")
            for af in add:
                if af["FIELDNAME"].find("&") != -1:
                    # We've got unicode chars for the tag name - not allowed
                    r["ADD" + str(af["ID"])] = af["VALUE"]
                else:
                    r[af["FIELDNAME"]] = af["VALUE"]
    # If bondedAsSingle is on, go through the the set of animals and merge
    # the bonded animals into a single record
    def merge_animal(a, animalid):
        """
        Find the animal in rows with animalid, merge it into a and
        then remove it from the set.
        """
        for r in rows:
            if r["ID"] == animalid:
                a["ANIMALNAME"] = "%s, %s" % (a["ANIMALNAME"], r["ANIMALNAME"])
                rows.remove(r)
                break
    if pc.bondedAsSingle:
        for r in rows:
            if r["BONDEDANIMALID"] is not None and r["BONDEDANIMALID"] != 0:
                merge_animal(r, r["BONDEDANIMALID"])
            if r["BONDEDANIMAL2ID"] is not None and r["BONDEDANIMAL2ID"] != 0:
                merge_animal(r, r["BONDEDANIMAL2ID"])
    return rows

def get_animal_data_query(dbo, pc, animalid = 0):
    """
    Generate the adoptable animal query. If animalid is supplied, only runs the
    query for a single animal (useful for determining if one animal is on the
    adoptable list).
    """
    sql = animal.get_animal_query(dbo)
    if animalid == 0:
        sql += " WHERE a.ID > 0"
    else:
        sql += " WHERE a.ID = %d" % animalid
    if not pc.includeCaseAnimals: 
        sql += " AND a.CrueltyCase = 0"
    if not pc.includeWithoutImage: 
        sql += " AND EXISTS(SELECT ID FROM media WHERE WebsitePhoto = 1 AND LinkID = a.ID AND LinkTypeID = 0)"
    if not pc.includeReservedAnimals: 
        sql += " AND a.HasActiveReserve = 0"
    if not pc.includeHold: 
        sql += " AND (a.IsHold = 0 OR a.IsHold Is Null)"
    if not pc.includeQuarantine:
        sql += " AND (a.IsQuarantine = 0 OR a.IsQuarantine Is Null)"
    if not pc.includeTrial:
        sql += " AND a.HasTrialAdoption = 0"
    # Make sure animal is old enough
    exclude = i18n.now()
    exclude -= datetime.timedelta(days=pc.excludeUnderWeeks * 7)
    sql += " AND a.DateOfBirth <= " + db.dd(exclude)
    # Filter out dead and unadoptable animals
    sql += " AND a.DeceasedDate Is Null AND a.IsNotAvailableForAdoption = 0"
    # Filter out permanent fosters
    sql += " AND a.HasPermanentFoster = 0"
    # Build a set of OR clauses based on any movements/locations
    moveor = []
    # Always include courtesy post animals
    moveor.append("(a.IsCourtesy = 1)")
    if len(pc.internalLocations) > 0 and pc.internalLocations[0].strip() != "null":
        moveor.append("(a.Archived = 0 AND a.ActiveMovementID = 0 AND a.ShelterLocation IN (%s))" % ",".join(pc.internalLocations))
    else:
        moveor.append("(a.Archived = 0 AND a.ActiveMovementID = 0)")
    if pc.includeRetailerAnimals:
        moveor.append("(a.ActiveMovementType = %d)" % movement.RETAILER)
    if pc.includeFosterAnimals:
        moveor.append("(a.ActiveMovementType = %d)" % movement.FOSTER)
    if pc.includeTrial:
        moveor.append("(a.ActiveMovementType = %d AND a.HasTrialAdoption = 1)" % movement.ADOPTION)
    sql += " AND (" + " OR ".join(moveor) + ")"
    # Ordering
    if pc.order == 0:
        sql += " ORDER BY a.MostRecentEntryDate"
    elif pc.order == 1:
        sql += " ORDER BY a.MostRecentEntryDate DESC"
    elif pc.order == 2:
        sql += " ORDER BY a.AnimalName"
    else:
        sql += " ORDER BY a.MostRecentEntryDate"
    # Limit
    if pc.limit > 0:
        sql += " LIMIT %d" % pc.limit
    return sql

def get_microchip_data(dbo, patterns, publishername, allowintake = True):
    """
    Returns a list of animals with unpublished microchips.
    patterns:      A list of either microchip prefixes or SQL clauses to OR together
                   together in the preamble, eg: [ '977', "a.SmartTag = 1 AND a.SmartTagNumber <> ''" ]
    publishername: The name of the microchip registration publisher, eg: pettracuk
    allowintake:   True if the provider is ok with registering to the shelter's details on intake
    """
    movementtypes = configuration.microchip_register_movements(dbo)
    try:
        rows = db.query(dbo, get_microchip_data_query(dbo, patterns, publishername, movementtypes, allowintake))
    except Exception,err:
        al.error(str(err), "publisher.get_microchip_data", dbo, sys.exc_info())
    organisation = configuration.organisation(dbo)
    orgaddress = configuration.organisation_address(dbo)
    orgtown = configuration.organisation_town(dbo)
    orgcounty = configuration.organisation_county(dbo)
    orgpostcode = configuration.organisation_postcode(dbo)
    orgtelephone = configuration.organisation_telephone(dbo)
    email = configuration.email(dbo)
    for r in rows:
        use_original_owner_info = False
        use_shelter_info = False
        # If this is a non-shelter animal, use the original owner info
        if r["NONSHELTERANIMAL"] == 1 and r["ORIGINALOWNERNAME"] is not None and r["ORIGINALOWNERNAME"] != "":
            use_original_owner_info = True
        # If this is an on-shelter animal with no active movement, use the shelter info
        elif r["ARCHIVED"] == 0 and r["ACTIVEMOVEMENTID"] == 0:
            use_shelter_info = True
        # If this is a shelter animal on foster, but register on intake is set and foster is not, use the shelter info
        elif r["ARCHIVED"] == 0 and r["ACTIVEMOVEMENTTYPE"] == 2 and movementtypes.find("0") != -1 and movementtypes.find("2") == -1:
            use_shelter_info = True
        # Otherwise, leave CURRENTOWNER* fields as they are for active movement
        if use_original_owner_info:
            r["CURRENTOWNERNAME"] = r["ORIGINALOWNERNAME"]
            r["CURRENTOWNERTITLE"] = r["ORIGINALOWNERTITLE"]
            r["CURRENTOWNERINITIALS"] = r["ORIGINALOWNERINITIALS"]
            r["CURRENTOWNERFORENAMES"] = r["ORIGINALOWNERFORENAMES"]
            r["CURRENTOWNERSURNAME"] = r["ORIGINALOWNERSURNAME"]
            r["CURRENTOWNERADDRESS"] = r["ORIGINALOWNERADDRESS"]
            r["CURRENTOWNERTOWN"] = r["ORIGINALOWNERTOWN"]
            r["CURRENTOWNERCOUNTY"] = r["ORIGINALOWNERCOUNTY"]
            r["CURRENTOWNERPOSTCODE"] = r["ORIGINALOWNERPOSTCODE"]
            r["CURRENTOWNERCITY"] = r["ORIGINALOWNERTOWN"]
            r["CURRENTOWNERSTATE"] = r["ORIGINALOWNERCOUNTY"]
            r["CURRENTOWNERZIPCODE"] = r["ORIGINALOWNERPOSTCODE"]
            r["CURRENTOWNERHOMETELEPHONE"] = r["ORIGINALOWNERHOMETELEPHONE"]
            r["CURRENTOWNERPHONE"] = r["ORIGINALOWNERHOMETELEPHONE"]
            r["CURRENTOWNERWORKPHONE"] = r["ORIGINALOWNERWORKTELEPHONE"]
            r["CURRENTOWNERMOBILEPHONE"] = r["ORIGINALOWNERMOBILETELEPHONE"]
            r["CURRENTOWNERCELLPHONE"] = r["ORIGINALOWNERMOBILETELEPHONE"]
            r["CURRENTOWNEREMAILADDRESS"] = r["ORIGINALOWNEREMAILADDRESS"]
        if use_shelter_info:
            r["CURRENTOWNERNAME"] = organisation
            r["CURRENTOWNERTITLE"] = ""
            r["CURRENTOWNERINITIALS"] = ""
            r["CURRENTOWNERFORENAMES"] = ""
            r["CURRENTOWNERSURNAME"] = organisation
            r["CURRENTOWNERADDRESS"] = orgaddress
            r["CURRENTOWNERTOWN"] = orgtown
            r["CURRENTOWNERCOUNTY"] = orgcounty
            r["CURRENTOWNERPOSTCODE"] = orgpostcode
            r["CURRENTOWNERCITY"] = orgtown
            r["CURRENTOWNERSTATE"] = orgcounty
            r["CURRENTOWNERZIPCODE"] = orgpostcode
            r["CURRENTOWNERHOMETELEPHONE"] = orgtelephone
            r["CURRENTOWNERPHONE"] = orgtelephone
            r["CURRENTOWNERWORKPHONE"] = orgtelephone
            r["CURRENTOWNERMOBILEPHONE"] = orgtelephone
            r["CURRENTOWNERCELLPHONE"] = orgtelephone
            r["CURRENTOWNEREMAILADDRESS"] = email
    return rows

def get_microchip_data_query(dbo, patterns, publishername, movementtypes = "1", allowintake = True):
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
    """
    pclauses = []
    for p in patterns:
        if p.startswith("9") or p.startswith("0"):
            pclauses.append("a.IdentichipNumber LIKE '%s%%'" % p)
        else:
            pclauses.append("(%s)" % p)
    trialclause = ""
    if movementtypes.find("11") == -1:
        trialclause = "AND a.HasTrialAdoption = 0"
    intakeclause = ""
    if movementtypes.find("0") != -1 and allowintake:
        # Note: Use of MostRecentEntryDate will pick up returns as well as intake
        intakeclause = "OR (a.NonShelterAnimal = 0 AND a.IsHold = 0 AND a.Archived = 0 AND (a.ActiveMovementID = 0 OR a.ActiveMovementType = 2) " \
            "AND NOT EXISTS(SELECT SentDate FROM animalpublished WHERE PublishedTo = '%(publishername)s' " \
            "AND AnimalID = a.ID AND SentDate >= a.MostRecentEntryDate))" % { "publishername": publishername }
    nonshelterclause = "OR (a.NonShelterAnimal = 1 AND a.OriginalOwnerID Is Not Null AND a.OriginalOwnerID > 0 AND a.IdentichipDate Is Not Null " \
        "AND NOT EXISTS(SELECT SentDate FROM animalpublished WHERE PublishedTo = '%(publishername)s' " \
        "AND AnimalID = a.ID AND SentDate >= a.IdentichipDate))" % { "publishername": publishername }
    where = " WHERE (%(patterns)s) AND a.DeceasedDate Is Null AND (" \
        "(a.ActiveMovementID > 0 AND a.ActiveMovementType > 0 AND (a.ActiveMovementType IN (%(movementtypes)s)) %(trialclause)s " \
        "AND NOT EXISTS(SELECT SentDate FROM animalpublished WHERE PublishedTo = '%(publishername)s' " \
        "AND AnimalID = a.ID AND SentDate >= a.ActiveMovementDate)) " \
        "%(nonshelterclause)s " \
        "%(intakeclause)s " \
        ")" % { 
            "patterns": " OR ".join(pclauses),
            "movementtypes": movementtypes, 
            "intakeclause": intakeclause,
            "nonshelterclause": nonshelterclause,
            "trialclause": trialclause,
            "publishername": publishername }
    sql = animal.get_animal_query(dbo) + where
    return sql

def get_animal_view(dbo, animalid):
    """
    Constructs the animal view page to the template.
    """
    # If the animal is not adoptable, bail out
    if not is_adoptable(dbo, animalid):
        raise utils.ASMPermissionError("animal is not adoptable")
    # If the option is on, use animal comments as the notes
    a = animal.get_animal(dbo, animalid)
    if configuration.publisher_use_comments(dbo):
        a["WEBSITEMEDIANOTES"] = a["ANIMALCOMMENTS"]
    head = dbfs.get_string(dbo, "head.html", "/internet/animalview")
    body = dbfs.get_string(dbo, "body.html", "/internet/animalview")
    foot = dbfs.get_string(dbo, "foot.html", "/internet/animalview")
    if smcom.active():
        a["WEBSITEMEDIANAME"] = "%s?account=%s&method=animal_image&animalid=%d" % (SERVICE_URL, dbo.database, animalid)
    else:
        a["WEBSITEMEDIANAME"] = "%s?method=animal_image&animalid=%d" % (SERVICE_URL, animalid)
    if head == "":
        head = "<!DOCTYPE html>\n<html>\n<head>\n<title>$$SHELTERCODE$$ - $$ANIMALNAME$$</title></head>\n<body>"
    if body == "":
        body = "<h2>$$SHELTERCODE$$ - $$ANIMALNAME$$</h2><p><img src='$$WEBMEDIAFILENAME$$'/></p><p>$$WEBMEDIANOTES$$</p>"
    if foot == "":
        foot = "</body>\n</html>"
    s = head + body + foot
    tags = wordprocessor.animal_tags(dbo, a)
    tags = wordprocessor.append_tags(tags, wordprocessor.org_tags(dbo, "system"))
    # Add extra publishing text, preserving the line endings
    notes = utils.nulltostr(a["WEBSITEMEDIANOTES"])
    notes += configuration.third_party_publisher_sig(dbo)
    notes = notes.replace("\n", "**le**")
    tags["WEBMEDIANOTES"] = notes 
    s = wordprocessor.substitute_tags(s, tags, True, "$$", "$$")
    s = s.replace("**le**", "<br />")
    return s

def get_adoption_status(dbo, a):
    """
    Returns a string representing the animal's current adoption 
    status.
    """
    l = dbo.locale
    if a["ARCHIVED"] == 0 and a["CRUELTYCASE"] == 1: return i18n._("Cruelty Case", l)
    if a["ARCHIVED"] == 0 and a["ISQUARANTINE"] == 1: return i18n._("Quarantine", l)
    if a["ARCHIVED"] == 0 and a["ISHOLD"] == 1: return i18n._("Hold", l)
    if a["ARCHIVED"] == 0 and a["HASACTIVERESERVE"] == 1: return i18n._("Reserved", l)
    if a["ARCHIVED"] == 0 and a["HASPERMANENTFOSTER"] == 1: return i18n._("Permanent Foster", l)
    if is_adoptable(dbo, a["ID"]): return i18n._("Adoptable", l)
    return i18n._("Not For Adoption", l)

def is_adoptable(dbo, animalid):
    """
    Returns true if the animal is adoptable
    """
    pc = PublishCriteria(configuration.publisher_presets(dbo))
    sql = get_animal_data_query(dbo, pc, animalid)
    rows = db.query(dbo, sql)
    return len(rows) > 0

class AbstractPublisher(threading.Thread):
    """
    Base class for all publishers
    """
    dbo = None
    pc = None
    totalAnimals = 0
    publisherName = ""
    publisherKey = ""
    publishDir = ""
    tempPublishDir = True
    locale = "en"
    lastError = ""
    logBuffer = ""
    logName = ""

    def __init__(self, dbo, publishCriteria):
        threading.Thread.__init__(self)
        self.dbo = dbo
        self.locale = configuration.locale(dbo)
        self.pc = publishCriteria
        self.makePublishDirectory()

    def checkMappedSpecies(self):
        """
        Returns True if all species have been mapped for publishers
        """
        return 0 == db.query_int(self.dbo, "SELECT COUNT(*) FROM species " + \
            "WHERE PetFinderSpecies Is Null OR PetFinderSpecies = ''")

    def checkMappedBreeds(self):
        """
        Returns True if all breeds have been mapped for publishers
        """
        return 0 == db.query_int(self.dbo, "SELECT COUNT(*) FROM breed " + \
            "WHERE PetFinderBreed Is Null OR PetFinderBreed = ''")

    def checkMappedColours(self):
        """
        Returns True if all colours have been mapped for publishers
        """
        return 0 == db.query_int(self.dbo, "SELECT COUNT(*) FROM basecolour " + \
            "WHERE AdoptAPetColour Is Null OR AdoptAPetColour = ''")

    def getPublisherBreed(self, an, b1or2 = 1):
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
        b = utils.nulltostr(breedname).lower()
        if b == "mix" or b == "cross" or b == "unknown" or b == "crossbreed" or breed1id == breed2id:
            return ""
        return publisherbreed

    def isPublisherExecuting(self):
        """
        Returns True if a publisher is already currently running against
        this database. If the ignoreLock publishCriteria option has been
        set, always returns false.
        """
        if self.pc.ignoreLock: return False
        return async.is_task_running(self.dbo)

    def updatePublisherProgress(self, progress):
        """
        Updates the publisher progress in the database
        """
        async.set_task_name(self.dbo, self.publisherName)
        async.set_progress_max(self.dbo, 100)
        async.set_progress_value(self.dbo, progress)

    def replaceMDBTokens(self, dbo, s):
        """
        Replace MULTIPLE_DATABASE tokens in the string given.
        """
        s = s.replace("{alias}", dbo.alias)
        s = s.replace("{database}", dbo.database)
        s = s.replace("{username}", dbo.username)
        return s

    def replaceAnimalTags(self, a, s):
        """
        Replace any $$Tag$$ tags in s, using animal a
        """
        tags = wordprocessor.animal_tags(self.dbo, a)
        return wordprocessor.substitute_tags(s, tags, True, "$$", "$$")

    def resetPublisherProgress(self):
        """
        Resets the publisher progress and stops blocking for other 
        publishers
        """
        async.reset(self.dbo)

    def setPublisherComplete(self):
        """
        Mark the current publisher as complete
        """
        async.set_progress_value(self.dbo, 100)

    def getProgress(self, i, n):
        """
        Returns a progress percentage
        i: Current position
        n: Total elements
        """
        return int((float(i) / float(n)) * 100)

    def shouldStopPublishing(self):
        """
        Returns True if we need to stop publishing
        """
        return async.get_cancel(self.dbo)

    def setStartPublishing(self):
        """
        Clears the stop publishing flag so we can carry on publishing.
        """
        async.set_cancel(self.dbo, False)

    def setLastError(self, msg):
        """
        Sets the last error message and clears the publisher lock
        """
        async.set_last_error(self.dbo, msg)
        self.lastError = msg
        if msg != "": self.logError(self.lastError)
        self.resetPublisherProgress()

    def makePublishDirectory(self):
        """
        Creates a temporary publish directory if one isn't set, or uses
        the one set in the criteria.
        """
        if self.logName.endswith("html.txt"):
            # It's HTML publishing - we have some special rules
            # If the publishing directory has been overridden, set it
            if MULTIPLE_DATABASES_PUBLISH_DIR != "":
                self.publishDir = MULTIPLE_DATABASES_PUBLISH_DIR
                # Replace any tokens
                self.publishDir = self.replaceMDBTokens(self.dbo, self.publishDir)
                self.pc.ignoreLock = True
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

    def deletePublishDirectory(self):
        """
        Removes the publish directory if it was temporary
        """
        if self.tempPublishDir:
            shutil.rmtree(self.publishDir, True)

    def getDescription(self, an, crToBr = False, crToHE = False):
        """
        Returns the description/bio for an animal.
        an: The animal record
        crToBr: Convert line breaks to <br /> tags
        crToHE: Convert line breaks to html entity &#10;
        """
        # Note: WEBSITEMEDIANOTES becomes ANIMALCOMMENTS in get_animal_data when publisher_use_comments is on
        notes = utils.nulltostr(an["WEBSITEMEDIANOTES"])
        # Add any extra text as long as this isn't a courtesy listing
        if an["ISCOURTESY"] != 1: notes += configuration.third_party_publisher_sig(self.dbo)
        # Replace any wp tags used in the notes
        notes = self.replaceAnimalTags(an, notes)
        # Escape carriage returns
        cr = ""
        if crToBr: 
            cr = "<br />"
        if crToHE:
            cr = "&#10;"
        notes = notes.replace("\r\n", cr)
        notes = notes.replace("\r", cr)
        notes = notes.replace("\n", cr)
        # Escape speechmarks
        notes = notes.replace("\"", "\"\"")
        return notes

    def getLastPublishedDate(self, animalid):
        """
        Returns the last date animalid was sent to the current publisher
        """
        return db.query_date(self.dbo, "SELECT SentDate FROM animalpublished WHERE AnimalID = %d AND PublishedTo = '%s'" % (animalid, self.publisherKey))

    def markAnimalPublished(self, animalid, datevalue = None):
        """
        Marks an animal published at the current date/time for this publisher
        animalid:    The animal id to update
        """
        if datevalue is None: datevalue = i18n.now(self.dbo.timezone)
        self.markAnimalUnpublished(animalid)
        db.execute(self.dbo, "INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) VALUES (%d, '%s', %s)" %
            (animalid, self.publisherKey, db.dd(datevalue)))

    def markAnimalUnpublished(self, animalid):
        """
        Marks an animal as not published for the current publisher
        """
        db.execute(self.dbo, "DELETE FROM animalpublished WHERE AnimalID = %d AND PublishedTo = '%s'" % (animalid, self.publisherKey))

    def markAnimalsPublished(self, animals):
        """
        Marks all animals in the set as published at the current date/time
        for the current publisher
        """
        batch = []
        inclause = []
        # build a list of IDs and deduplicate them
        for a in animals:
            inclause.append( str(a["ID"]) )
        inclause = set(inclause)
        # build a batch for inserting animalpublished entries into the table
        for i in inclause:
            batch.append( ( int(i), self.publisherKey, i18n.now(self.dbo.timezone) ) )
        if len(inclause) == 0: return
        db.execute(self.dbo, "DELETE FROM animalpublished WHERE PublishedTo = '%s' AND AnimalID IN (%s)" % (self.publisherKey, ",".join(inclause)))
        db.execute_many(self.dbo, "INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate) VALUES (%s, %s, %s)", batch)

    def markAnimalsPublishFailed(self, animals):
        """
        Marks all animals in the set as published at the current date/time
        for the current publisher but with an extra failure message
        """
        batch = []
        inclause = {}
        # build a list of IDs and deduplicate them
        for a in animals:
            m = ""
            if a.has_key("FAILMESSAGE"):
                m = a["FAILMESSAGE"]
            inclause[str(a["ID"])] = m
        # build a batch for inserting animalpublished entries into the table
        for k, v in inclause.iteritems():
            batch.append( ( int(k), self.publisherKey, i18n.now(self.dbo.timezone), v ) )
        if len(inclause) == 0: return
        db.execute(self.dbo, "DELETE FROM animalpublished WHERE PublishedTo = '%s' AND AnimalID IN (%s)" % (self.publisherKey, ",".join(inclause)))
        db.execute_many(self.dbo, "INSERT INTO animalpublished (AnimalID, PublishedTo, SentDate, Extra) VALUES (%s, %s, %s, %s)", batch)

    def getMatchingAnimals(self):
        a = get_animal_data(self.dbo, self.pc)
        self.log("Got %d matching animals for publishing." % len(a))
        return a

    def saveFile(self, path, contents):
        try:
            f = open(path, "wb")
            f.write(contents)
            f.flush()
            f.close()
        except Exception,err:
            self.logError(str(err), sys.exc_info())

    def log(self, msg):
        """
        Logs a message
        """
        self.logBuffer += msg + "\n"
        al.debug(utils.truncate(msg, 1023), self.publisherName, self.dbo)

    def logError(self, msg, ie=None):
        """
        Logs a message to our logger and dumps a stacktrace.
        ie = error info object from sys.exc_info() if available
        """
        self.log("ALERT: %s" % msg)
        al.error(msg, self.publisherName, self.dbo, ie)

    def logSuccess(self, msg):
        """
        Logs a success message to our logger
        """
        self.log("SUCCESS: %s" % msg)
        al.info(msg, self.publisherName, self.dbo)

    def setLogName(self, publisherKey):
        """
        Sets the logname based on the publisher type given and
        the current date/time.
        """
        self.publisherKey = publisherKey
        d = i18n.now(self.dbo.timezone)
        s = "%d-%02d-%02d_%02d:%02d_%s.txt" % ( d.year, d.month, d.day, d.hour, d.minute, publisherKey )
        self.logName = s

    def saveLog(self):
        """
        Saves the log to the dbfs
        """
        dbfs.put_string_filepath(self.dbo, "/logs/publish/%s" % self.logName, self.logBuffer)

    def isImage(self, path):
        """
        Returns True if the path given has a valid image extension
        """
        return path.lower().endswith("jpg") or path.lower().endswith("jpeg")

    def generateThumbnail(self, image, thumbnail):
        """
        Generates a thumbnail 
        image: Path to the image to generate a thumbnail from
        thumbnail: Path to the target thumbnail image
        """
        self.log("generating thumbnail %s -> %s" % ( image, thumbnail ))
        try:
            media.scale_image_file(image, thumbnail, self.pc.thumbnailSize)
        except Exception,err:
            self.logError("Failed scaling thumbnail: %s" % err, sys.exc_info())

    def scaleImage(self, image, scalesize):
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
            return media.scale_image_file(image, image, sizespec)
        except Exception,err:
            self.logError("Failed scaling image: %s" % err, sys.exc_info())

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
    currentDir = ""
    passive = True
    existingImageList = None

    def __init__(self, dbo, publishCriteria, ftphost, ftpuser, ftppassword, ftpport = 21, ftproot = "", passive = True):
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.ftphost = ftphost
        self.ftpuser = ftpuser
        self.ftppassword = self.unxssPass(ftppassword)
        self.ftpport = ftpport
        self.ftproot = ftproot
        self.passive = passive

    def unxssPass(self, s):
        """
        Passwords stored in the config table are subject to XSS escaping, so
        any >, < or & in the password will have been escaped - turn them back again
        """
        s = s.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        s = s.replace("&amp;", "&")
        return s

    def openFTPSocket(self):
        """
        Opens an FTP socket to the server and changes to the
        root FTP directory. Returns True if all was well or
        uploading is disabled.
        """
        if not self.pc.uploadDirectly: return True
        if self.ftphost.strip() == "": raise ValueError("No FTP host set")
        self.log("Connecting to %s as %s" % (self.ftphost, self.ftpuser))
        
        try:
            # open it and login
            self.socket = ftplib.FTP(host=self.ftphost, timeout=15)
            self.socket.login(self.ftpuser, self.ftppassword)
            self.socket.set_pasv(self.passive)

            if self.ftproot is not None and self.ftproot != "":
                # If we had an FTP override, try and create the directory
                # before we change to it.
                if MULTIPLE_DATABASES_PUBLISH_FTP is not None:
                    self.mkdir(self.ftproot)
                self.chdir(self.ftproot)

            return True
        except Exception,err:
            self.logError("Failed opening FTP socket (%s->%s): %s" % (self.dbo.database, self.ftphost, err), sys.exc_info())
            return False

    def closeFTPSocket(self):
        if not self.pc.uploadDirectly: return
        try:
            self.socket.quit()
        except:
            pass

    def reconnectFTPSocket(self):
        """
        Reconnects to the FTP server, changing back to the current directory.
        """
        self.closeFTPSocket()
        self.openFTPSocket()
        if not self.currentDir == "":
            self.chdir(self.currentDir)

    def checkFTPSocket(self):
        """
        Called before each upload if publishCriteria.checkSocket is
        set to true. It verifies that the socket is still active
        by running a command. If the command fails, the socket is
        reopened and the current FTP directory is returned to.
        """
        if not self.pc.uploadDirectly: return
        try:
            self.socket.retrlines("LIST", quietcallback)
        except Exception,err:
            self.log("Dead socket (%s), reconnecting" % err)
            self.reconnectFTPSocket()

    def upload(self, filename):
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
        except Exception, err:
            self.logError("Failed uploading %s: %s" % (filename, err), sys.exc_info())
            self.log("reconnecting FTP socket to reset state")
            self.reconnectFTPSocket()

    def lsdir(self):
        if not self.pc.uploadDirectly: return []
        try:
            return self.socket.nlst()
        except Exception,err:
            self.logError("list: %s" % err)

    def mkdir(self, newdir):
        if not self.pc.uploadDirectly: return
        self.log("FTP mkdir %s" % newdir)
        try:
            self.socket.mkd(newdir)
        except Exception,err:
            self.log("mkdir %s: already exists (%s)" % (newdir, err))

    def chdir(self, newdir, fromroot = ""):
        if not self.pc.uploadDirectly: return
        self.log("FTP chdir to %s" % newdir)
        try:
            self.socket.cwd(newdir)
            if fromroot == "":
                self.currentDir = newdir
            else:
                self.currentDir = fromroot
        except Exception, err:
            self.logError("chdir %s: %s" % (newdir, err), sys.exc_info())

    def delete(self, filename):
        try:
            self.socket.delete(filename)
        except Exception,err:
            self.log("delete %s: %s" % (filename, err))

    def clearExistingHTML(self):
        try:
            oldfiles = glob.glob(os.path.join(self.publishDir, "*." + self.pc.extension))
            for f in oldfiles:
                os.remove(f)
        except Exception, err:
            self.logError("warning: failed removing %s from filesystem: %s" % (oldfiles, err), sys.exc_info())
        if not self.pc.uploadDirectly: return
        try:
            for f in self.socket.nlst("*.%s" % self.pc.extension):
                if not f.startswith("search"):
                    self.socket.delete(f)
        except Exception, err:
            self.logError("warning: failed deleting from FTP server: %s" % err, sys.exc_info())

    def clearExistingImages(self):
        try:
            oldfiles = glob.glob(os.path.join(self.publishDir, "*.jpg"))
            for f in oldfiles:
                os.remove(f)
        except Exception, err:
            self.logError("warning: failed removing %s from filesystem: %s" % (oldfiles, err), sys.exc_info())
        if not self.pc.uploadDirectly: return
        try:
            for f in self.socket.nlst("*.jpg"):
                self.socket.delete(f)
        except Exception, err:
            self.logError("warning: failed deleting from FTP server: %s" % err, sys.exc_info())

    def cleanup(self):
        """
        Call when the publisher has completed to tidy up.
        """
        self.closeFTPSocket()
        self.deletePublishDirectory()
        self.saveLog()
        self.setPublisherComplete()

    def uploadImage(self, a, medianame, imagename):
        """
        Retrieves image with medianame from the DBFS to the publish
        folder and uploads it via FTP with imagename
        """
        try:
            # Check if the image is already on the server if 
            # forceReupload is off and the animal doesn't
            # have any recently changed images
            if not self.pc.forceReupload and a["RECENTLYCHANGEDIMAGES"] == 0:
                if self.existingImageList is None:
                    self.existingImageList = self.lsdir()
                elif imagename in self.existingImageList:
                    self.log("%s: skipping, already on server" % imagename)
                    return
            imagefile = os.path.join(self.publishDir, imagename)
            thumbnail = os.path.join(self.publishDir, "tn_" + imagename)
            dbfs.get_file(self.dbo, medianame, "", imagefile)
            self.log("Retrieved image: %d::%s::%s" % ( a["ID"], medianame, imagename ))
            # If scaling is on, do it
            if self.pc.scaleImages > 1:
                self.scaleImage(imagefile, self.pc.scaleImages)
            # If thumbnails are on, do it
            if self.pc.thumbnails:
                self.generateThumbnail(imagefile, thumbnail)
            # Upload
            if self.pc.uploadDirectly:
                self.upload(imagefile)
                if self.pc.thumbnails:
                    self.upload(thumbnail)
        except Exception, err:
            self.logError("Failed uploading image %s: %s" % (medianame, err), sys.exc_info())
            return 0

    def uploadImages(self, a, copyWithMediaIDAsName = False, limit = 0):
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
        animalcode = a["SHELTERCODE"]
        animalweb = a["WEBSITEMEDIANAME"]
        if animalweb is None or animalweb == "": return totalimages
        # If we've got HTML entities in our sheltercode, it's going to
        # mess up filenames. Use the animalid instead.
        if animalcode.find("&#") != -1:
            animalcode = str(a["ID"])
        # Name it sheltercode-1.jpg or sheltercode.jpg if uploadall is off
        imagename = animalcode + ".jpg"
        if self.pc.uploadAllImages:
            imagename = animalcode + "-1.jpg"
        # If we're forcing reupload or the animal has
        # some recently changed images, remove all the images
        # for this animal before doing anything.
        if self.pc.forceReupload or a["RECENTLYCHANGEDIMAGES"] > 0:
            if self.existingImageList is None:
                self.existingImageList = self.lsdir()
            for ei in self.existingImageList:
                if ei.startswith(animalcode):
                    self.log("delete: %s" % ei)
                    self.delete(ei)
        # Save it to the publish directory
        totalimages = 1
        self.uploadImage(a, animalweb, imagename)
        # If we're saving a copy with the media ID, do that too
        if copyWithMediaIDAsName:
            self.uploadImage(a, animalweb, animalweb)
        # If upload all is set, we need to grab the rest of
        # the animal's images upto the limit. If the limit is
        # zero, we upload everything.
        if self.pc.uploadAllImages:
            mrecs = media.get_image_media(self.dbo, media.ANIMAL, a["ID"], True)
            self.log("Animal has %d media files (%d recently changed)" % (len(mrecs), a["RECENTLYCHANGEDIMAGES"]))
            for m in mrecs:
                # Ignore the main media since we used that
                if m["MEDIANAME"] == animalweb:
                    continue
                # Have we hit our limit?
                if totalimages == limit:
                    return totalimages
                totalimages += 1
                # Get the image
                otherpic = m["MEDIANAME"]
                imagename = "%s-%d.jpg" % ( animalcode, totalimages )
                self.uploadImage(a, otherpic, imagename)
        return totalimages

class AdoptAPetPublisher(FTPPublisher):
    """
    Handles publishing to AdoptAPet.com
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.forceReupload = False
        publishCriteria.checkSocket = True
        publishCriteria.scaleImages = 1
        publishCriteria.thumbnails = False
        FTPPublisher.__init__(self, dbo, publishCriteria, 
            ADOPTAPET_FTP_HOST, configuration.adoptapet_user(dbo), 
            configuration.adoptapet_password(dbo))
        self.publisherName = "AdoptAPet Publisher"
        self.setLogName("adoptapet")

    def apYesNo(self, condition):
        """
        Returns a CSV entry for yes or no based on the condition
        """
        if condition:
            return "\"1\""
        else:
            return "\"0\""

    def apYesNoUnknown(self, ourval):
        """
        Returns a CSV entry for yes or no based on our yes/no/unknown.
        In our scheme 0 = yes, 1 = no, 2 = unknown
        Their scheme 0 = no, 1 = yes, blank = unknown
        """
        if ourval == 0:
            return "\"1\""
        elif ourval == 1:
            return "\"0\""
        else:
            return "\"\""

    def apHairLength(self, a):
        """
        Returns a valid hair length entry for adoptapet.
        For species "Cat", values are "Short", "Medium" or "Long"
        For species "Rabbit", values are "Short" or "Long"
        For species "Small Animal", values are "Hairless", "Short", "Medium" or "Long"
        """
        s = a["PETFINDERSPECIES"]
        c = a["COATTYPENAME"]
        if s == "Cat":
            if c in ("Short", "Medium", "Long"):
                return c
            return "Short"
        elif s == "Rabbit":
            if c in ("Short", "Long"):
                return c
            return "Short"
        elif s == "Small Animal":
            if c in ("Hairless", "Short", "Medium", "Long"):
                return c
            return "Short"
        return ""

    def apMapFile(self, includecolours):
        defmap = "; AdoptAPet.com import map. This file was autogenerated by\n" \
            "; Animal Shelter Manager. http://sheltermanager.com\n" \
            "; The FREE, open source solution for animal sanctuaries and rescue shelters.\n\n" \
            "#1:Id=Id\n" \
            "#2:Animal=Animal\n" \
            "Sugar Glider=Small Animal\n" \
            "Mouse=Small Animal\n" \
            "Rat=Small Animal\n" \
            "Hedgehog=Small Animal\n" \
            "Dove=Bird\n" \
            "Ferret=Small Animal\n" \
            "Chinchilla=Small Animal\n" \
            "Snake=Reptile\n" \
            "Tortoise=Reptile\n" \
            "Terrapin=Reptile\n" \
            "Chicken=Farm Animal\n" \
            "Owl=Bird\n" \
            "Goat=Farm Animal\n" \
            "Goose=Bird\n" \
            "Gerbil=Small Animal\n" \
            "Cockatiel=Bird\n" \
            "Guinea Pig=Small Animal\n" \
            "Hamster=Small Animal\n" \
            "Camel=Horse\n" \
            "Pony=Horse\n" \
            "Donkey=Horse\n" \
            "Llama=Horse\n" \
            "Pig=Farm Animal\n" \
            "Barnyard=Farm Animal\n" \
            "Small&Furry=Small Animal\n" \
            "#3:Breed=Breed\n" \
            "Appenzell Mountain Dog=Shepherd (Unknown Type)\n" \
            "Australian Cattle Dog/Blue Heeler=Australian Cattle Dog\n" \
            "Belgian Shepherd Dog Sheepdog=Belgian Shepherd\n" \
            "Belgian Shepherd Tervuren=Belgian Tervuren\n" \
            "Belgian Shepherd Malinois=Belgian Malinois\n" \
            "Black Labrador Retriever=Labrador Retriever\n" \
            "Brittany Spaniel=Brittany\n" \
            "Cane Corso Mastiff=Cane Corso\n" \
            "Chinese Crested Dog=Chinese Crested\n" \
            "Chinese Foo Dog=Shepherd (Unknown Type)\n" \
            "Cow=Cow or Bull\n" \
            "Dandi Dinmont Terrier=Dandie Dinmont Terrier\n" \
            "English Cocker Spaniel=Cocker Spaniel\n" \
            "English Coonhound=English (Redtick) Coonhound\n" \
            "Flat-coated Retriever=Flat-Coated Retriever\n" \
            "Fox Terrier=Fox Terrier (Smooth)\n" \
            "Hound=Hound (Unknown Type)\n" \
            "Illyrian Sheepdog=Shepherd (Unknown Type)\n" \
            "McNab =Shepherd (Unknown Type)\n" \
            "New Guinea Singing Dog=Shepherd (Unknown Type)\n" \
            "Newfoundland Dog=Newfoundland\n" \
            "Norweigan Lundehund=Shepherd (Unknown Type)\n" \
            "Peruvian Inca Orchid=Shepherd (Unknown Type)\n" \
            "Poodle=Poodle (Standard)\n" \
            "Retriever=Retriever (Unknown Type)\n" \
            "Saint Bernard St. Bernard=St. Bernard\n" \
            "Schipperkev=Schipperke\n" \
            "Schnauzer=Schnauzer (Standard)\n" \
            "Scottish Terrier Scottie=Scottie, Scottish Terrier\n" \
            "Setter=Setter (Unknown Type)\n" \
            "Sheep Dog=Old English Sheepdog\n" \
            "Shepherd=Shepherd (Unknown Type)\n" \
            "Shetland Sheepdog Sheltie=Sheltie, Shetland Sheepdog\n" \
            "Spaniel=Spaniel (Unknown Type)\n" \
            "Spitz=Spitz (Unknown Type, Medium)\n" \
            "South Russian Ovcharka=Shepherd (Unknown Type)\n" \
            "Terrier=Terrier (Unknown Type, Small)\n" \
            "West Highland White Terrier Westie=Westie, West Highland White Terrier\n" \
            "White German Shepherd=German Shepherd Dog\n" \
            "Wire-haired Pointing Griffon=Wirehaired Pointing Griffon\n" \
            "Wirehaired Terrier=Terrier (Unknown Type, Medium)\n" \
            "Yellow Labrador Retriever=Labrador Retriever\n" \
            "Yorkshire Terrier Yorkie=Yorkie, Yorkshire Terrier\n" \
            "American Siamese=Siamese\n" \
            "Bobtail=American Bobtail\n" \
            "Burmilla=Burmese\n" \
            "Canadian Hairless=Sphynx\n" \
            "Dilute Calico=Calico\n" \
            "Dilute Tortoiseshell=Domestic Shorthair\n" \
            "Domestic Long Hair=Domestic Longhair\n" \
            "Domestic Long Hair-black=Domestic Longhair\n" \
            "Domestic Long Hair - buff=Domestic Longhair\n" \
            "Domestic Long Hair-gray=Domestic Longhair\n" \
            "Domestic Long Hair - orange=Domestic Longhair\n" \
            "Domestic Long Hair - orange and white=Domestic Longhair\n" \
            "Domestic Long Hair - gray and white=Domestic Longhair\n" \
            "Domestic Long Hair-white=Domestic Longhair\n" \
            "Domestic Long Hair-black and white=Domestic Longhair\n" \
            "Domestic Medium Hair=Domestic Mediumhair\n" \
            "Domestic Medium Hair - buff=Domestic Mediumhair\n" \
            "Domestic Medium Hair - gray and white=Domestic Mediumhair\n" \
            "Domestic Medium Hair-white=Domestic Mediumhair\n" \
            "Domestic Medium Hair-orange=Domestic Mediumhair\n" \
            "Domestic Medium Hair - orange and white=Domestic Mediumhair\n" \
            "Domestic Medium Hair -black and white=Domestic Mediumhair\n" \
            "Domestic Short Hair=Domestic Shorthair\n" \
            "Domestic Short Hair - buff=Domestic Shorthair\n" \
            "Domestic Short Hair - gray and white=Domestic Shorthair\n" \
            "Domestic Short Hair-white=Domestic Shorthair\n" \
            "Domestic Short Hair-orange=Domestic Shorthair\n" \
            "Domestic Short Hair - orange and white=Domestic Shorthair\n" \
            "Domestic Short Hair -black and white=Domestic Shorthair\n" \
            "Exotic Shorthair=Exotic\n" \
            "Extra-Toes Cat (Hemingway Polydactyl)=Hemingway/Polydactyl\n" \
            "Oriental Long Hair=Oriental\n" \
            "Oriental Short Hair=Oriental\n" \
            "Oriental Tabby=Oriental\n" \
            "Pixie-Bob=Domestic Shorthair\n" \
            "Sphynx (hairless cat)=Sphynx\n" \
            "Tabby=Domestic Shorthair\n" \
            "Tabby - Orange=Domestic Shorthair\n" \
            "Tabby - Grey=Domestic Shorthair\n" \
            "Tabby - Brown=Domestic Shorthair\n" \
            "Tabby - white=Domestic Shorthair\n" \
            "Tabby - buff=Domestic Shorthair\n" \
            "Tabby - black=Domestic Shorthair\n" \
            "Tiger=Domestic Shorthair\n" \
            "Torbie=Domestic Shorthair\n" \
            "Tortoiseshell=Domestic Shorthair\n" \
            "Tuxedo=Domestic Shorthair\n" \
            "Angora Rabbit=Angora, English\n" \
            "Chinchilla=Chinchilla, Standard\n" \
            "English Lop=Lop, English\n" \
            "French-Lop=Lop, French\n" \
            "Hotot=Blanc de Hotot\n" \
            "Holland Lop=Lop, Holland\n" \
            "Lop Eared=Lop-Eared\n" \
            "Mini-Lop=Mini Lop\n" \
            "Bunny Rabbit=Other/Unknown\n" \
            "Pot Bellied=Pig (Potbellied)\n" \
            "#4:Breed2=Breed2\n" \
            "Appenzell Mountain Dog=Shepherd (Unknown Type)\n" \
            "Australian Cattle Dog/Blue Heeler=Australian Cattle Dog\n" \
            "Belgian Shepherd Dog Sheepdog=Belgian Shepherd\n" \
            "Belgian Shepherd Tervuren=Belgian Tervuren\n" \
            "Belgian Shepherd Malinois=Belgian Malinois\n" \
            "Black Labrador Retriever=Labrador Retriever\n" \
            "Brittany Spaniel=Brittany\n" \
            "Cane Corso Mastiff=Cane Corso\n" \
            "Chinese Crested Dog=Chinese Crested\n" \
            "Chinese Foo Dog=Shepherd (Unknown Type)\n" \
            "Dandi Dinmont Terrier=Dandie Dinmont Terrier\n" \
            "English Cocker Spaniel=Cocker Spaniel\n" \
            "English Coonhound=English (Redtick) Coonhound\n" \
            "Flat-coated Retriever=Flat-Coated Retriever\n" \
            "Fox Terrier=Fox Terrier (Smooth)\n" \
            "Hound=Hound (Unknown Type)\n" \
            "Illyrian Sheepdog=Shepherd (Unknown Type)\n" \
            "McNab =Shepherd (Unknown Type)\n" \
            "New Guinea Singing Dog=Shepherd (Unknown Type)\n" \
            "Newfoundland Dog=Newfoundland\n" \
            "Norweigan Lundehund=Shepherd (Unknown Type)\n" \
            "Peruvian Inca Orchid=Shepherd (Unknown Type)\n" \
            "Poodle=Poodle (Standard)\n" \
            "Retriever=Retriever (Unknown Type)\n" \
            "Saint Bernard St. Bernard=St. Bernard\n" \
            "Schipperkev=Schipperke\n" \
            "Schnauzer=Schnauzer (Standard)\n" \
            "Scottish Terrier Scottie=Scottie, Scottish Terrier\n" \
            "Setter=Setter (Unknown Type)\n" \
            "Sheep Dog=Old English Sheepdog\n" \
            "Shepherd=Shepherd (Unknown Type)\n" \
            "Shetland Sheepdog Sheltie=Sheltie, Shetland Sheepdog\n" \
            "Spaniel=Spaniel (Unknown Type)\n" \
            "Spitz=Spitz (Unknown Type, Medium)\n" \
            "South Russian Ovcharka=Shepherd (Unknown Type)\n" \
            "Terrier=Terrier (Unknown Type, Small)\n" \
            "West Highland White Terrier Westie=Westie, West Highland White Terrier\n" \
            "White German Shepherd=German Shepherd Dog\n" \
            "Wire-haired Pointing Griffon=Wirehaired Pointing Griffon\n" \
            "Wirehaired Terrier=Terrier (Unknown Type, Medium)\n" \
            "Yellow Labrador Retriever=Labrador Retriever\n" \
            "Yorkshire Terrier Yorkie=Yorkie, Yorkshire Terrier\n" \
            "American Siamese=Siamese\n" \
            "Bobtail=American Bobtail\n" \
            "Burmilla=Burmese\n" \
            "Canadian Hairless=Sphynx\n" \
            "Dilute Calico=Calico\n" \
            "Dilute Tortoiseshell=Domestic Shorthair\n" \
            "Domestic Long Hair=Domestic Longhair\n" \
            "Domestic Long Hair-black=Domestic Longhair\n" \
            "Domestic Long Hair - buff=Domestic Longhair\n" \
            "Domestic Long Hair-gray=Domestic Longhair\n" \
            "Domestic Long Hair - orange=Domestic Longhair\n" \
            "Domestic Long Hair - orange and white=Domestic Longhair\n" \
            "Domestic Long Hair - gray and white=Domestic Longhair\n" \
            "Domestic Long Hair-white=Domestic Longhair\n" \
            "Domestic Long Hair-black and white=Domestic Longhair\n" \
            "Domestic Medium Hair=Domestic Mediumhair\n" \
            "Domestic Medium Hair - buff=Domestic Mediumhair\n" \
            "Domestic Medium Hair - gray and white=Domestic Mediumhair\n" \
            "Domestic Medium Hair-white=Domestic Mediumhair\n" \
            "Domestic Medium Hair-orange=Domestic Mediumhair\n" \
            "Domestic Medium Hair - orange and white=Domestic Mediumhair\n" \
            "Domestic Medium Hair-black and white=Domestic Mediumhair\n" \
            "Domestic Short Hair=Domestic Shorthair\n" \
            "Domestic Short Hair - buff=Domestic Shorthair\n" \
            "Domestic Short Hair - gray and white=Domestic Shorthair\n" \
            "Domestic Short Hair-white=Domestic Shorthair\n" \
            "Domestic Short Hair-orange=Domestic Shorthair\n" \
            "Domestic Short Hair - orange and white=Domestic Shorthair\n" \
            "Domestic Short Hair-black and white=Domestic Shorthair\n" \
            "Exotic Shorthair=Exotic\n" \
            "Extra-Toes Cat (Hemingway Polydactyl)=Hemingway/Polydactyl\n" \
            "Oriental Long Hair=Oriental\n" \
            "Oriental Short Hair=Oriental\n" \
            "Oriental Tabby=Oriental\n" \
            "Pixie-Bob=Domestic Shorthair\n" \
            "Sphynx (hairless cat)=Sphynx\n" \
            "Tabby=Domestic Shorthair\n" \
            "Tabby - Orange=Domestic Shorthair\n" \
            "Tabby - Grey=Domestic Shorthair\n" \
            "Tabby - Brown=Domestic Shorthair\n" \
            "Tabby - white=Domestic Shorthair\n" \
            "Tabby - buff=Domestic Shorthair\n" \
            "Tabby - black=Domestic Shorthair\n" \
            "Tiger=Domestic Shorthair\n" \
            "Torbie=Domestic Shorthair\n" \
            "Tortoiseshell=Domestic Shorthair\n" \
            "Tuxedo=Domestic Shorthair\n" \
            "Angora Rabbit=Angora, English\n" \
            "Chinchilla=Chinchilla, Standard\n" \
            "English Lop=Lop, English\n" \
            "French-Lop=Lop, French\n" \
            "Hotot=Blanc de Hotot\n" \
            "Holland Lop=Lop, Holland\n" \
            "Lop Eared=Lop-Eared\n" \
            "Mini-Lop=Mini Lop\n" \
            "Bunny Rabbit=Other/Unknown\n" \
            "Pot Bellied=Pig (Potbellied)\n" \
            "#5:Purebred=Purebred\n" \
            "#6:Age=Age\n" \
            "#7:Name=Name\n" \
            "#8:Size=Size\n" \
            "#9:Sex=Sex\n"
        if not includecolours:
            defmap += "#10:Description=Description\n" \
            "#11:Status=Status\n" \
            "#12:GoodWKids=GoodWKids\n" \
            "#13:GoodWCats=GoodWCats\n" \
            "#14:GoodWDogs=GoodWDogs\n" \
            "#15:SpayedNeutered=SpayedNeutered\n" \
            "#16:ShotsCurrent=ShotsCurrent\n" \
            "#17:Housetrained=Housetrained\n" \
            "#18:Declawed=Declawed\n" \
            "#19:SpecialNeeds=SpecialNeeds\n" \
            "#20:HairLength=HairLength\n" \
            "#21:YouTubeVideoURL=YouTubeVideoURL" 
        else:
            defmap += "#10:Color=Color\n" \
            "#11:Description=Description\n" \
            "#12:Status=Status\n" \
            "#13:GoodWKids=GoodWKids\n" \
            "#14:GoodWCats=GoodWCats\n" \
            "#15:GoodWDogs=GoodWDogs\n" \
            "#16:SpayedNeutered=SpayedNeutered\n" \
            "#17:ShotsCurrent=ShotsCurrent\n" \
            "#18:Housetrained=Housetrained\n" \
            "#19:Declawed=Declawed\n" \
            "#20:SpecialNeeds=SpecialNeeds\n" \
            "#21:HairLength=HairLength\n" \
            "#22:YouTubeVideoURL=YouTubeVideoURL" 
        return defmap

    def apYouTubeURL(self, u):
        """
        Returns a YouTube URL in the format adoptapet want - https://www.youtube.com/watch?v=X
        returns a blank if u is not a youtube URL
        """
        if u is None: return ""
        if u.find("youtube") == -1 and u.find("youtu.be") == -1: return ""
        watch = ""
        if u.find("watch?v=") != -1:
            watch = u[u.rfind("v=")+2:]
        if u.find("youtu.be/") != -1:
            watch = u[u.rfind("/")+1:]
        if watch == "":
            return ""
        return "https://www.youtube.com/watch?v=%s" % watch

    def run(self):
        
        self.log("AdoptAPetPublisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        if not self.checkMappedSpecies():
            self.setLastError("Not all species have been mapped.")
            self.cleanup()
            return
        if not self.checkMappedBreeds():
            self.setLastError("Not all breeds have been mapped.")
            self.cleanup()
            return
        if self.pc.includeColours and not self.checkMappedColours():
            self.setLastError("Not all colours have been mapped and sending colours is enabled")
            self.cleanup()
            return

        shelterid = configuration.adoptapet_user(self.dbo)
        if shelterid == "":
            self.setLastError("No AdoptAPet.com shelter id has been set.")
            self.cleanup()
            return
        animals = self.getMatchingAnimals()
        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            self.cleanup()
            return

        if not self.openFTPSocket(): 
            self.setLastError("Failed opening FTP socket.")
            if self.logBuffer.find("530 Login") != -1:
                self.log("Found 530 Login incorrect: disabling AdoptAPet publisher.")
                configuration.publishers_enabled_disable(self.dbo, "ap")
            self.cleanup()
            return

        # Do the images first
        self.mkdir("photos")
        self.chdir("photos")

        csv = []

        anCount = 0
        for an in animals:
            try:
                line = []
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    self.cleanup()
                    return

                # If a limit was set, stop now
                if self.pc.limit > 0 and anCount > self.pc.limit:
                    self.log("Hit publishing limit of %d animals. Stopping." % self.pc.limit)
                    break

                # Upload images for this animal
                self.uploadImages(an)
                # Id
                line.append("\"%s\"" % an["SHELTERCODE"])
                # Species
                line.append("\"%s\"" % an["PETFINDERSPECIES"])
                # Breed 1
                line.append("\"%s\"" % an["PETFINDERBREED"])
                # Breed 2
                line.append("\"%s\"" % self.getPublisherBreed(an, 2))
                # Purebred
                line.append(self.apYesNo(an["CROSSBREED"] == 0))
                # Age, one of Adult, Baby, Senior and Young
                ageinyears = i18n.date_diff_days(an["DATEOFBIRTH"], i18n.now(self.dbo.timezone))
                ageinyears /= 365.0
                agename = "Adult"
                if ageinyears < 0.5: agename = "Baby"
                elif ageinyears < 2: agename = "Young"
                elif ageinyears < 9: agename = "Adult"
                else: agename = "Senior"
                line.append("\"%s\"" % agename)
                # Name
                line.append("\"%s\"" % an["ANIMALNAME"].replace("\"", "\"\""))
                # Size, one of S, M, L, XL
                ansize = "M"
                if an["SIZE"] == 0: ansize = "XL"
                elif an["SIZE"] == 1: ansize = "L"
                elif an["SIZE"] == 2: ansize = "M"
                elif an["SIZE"] == 3: ansize = "S"
                # If the animal is not a dog or cat, leave size blank as
                # adoptapet will throw errors otherwise
                if an["PETFINDERSPECIES"] != "Dog" and an["PETFINDERSPECIES"] != "Cat":
                    ansize = ""
                line.append("\"%s\"" % ansize)
                # Sex, one of M or F
                sexname = "M"
                if an["SEX"] == 0: sexname = "F"
                line.append("\"%s\"" % sexname)
                # Colour
                if self.pc.includeColours: line.append("\"%s\"" % an["ADOPTAPETCOLOUR"])
                # Description
                line.append("\"%s\"" % self.getDescription(an, crToBr=True))
                # Status, one of Available, Adopted or Delete
                line.append("\"Available\"")
                # Good with Kids
                line.append(self.apYesNoUnknown(an["ISGOODWITHCHILDREN"]))
                # Good with Cats
                line.append(self.apYesNoUnknown(an["ISGOODWITHCATS"]))
                # Good with Dogs
                line.append(self.apYesNoUnknown(an["ISGOODWITHDOGS"]))
                # Spayed/Neutered
                line.append(self.apYesNo(an["NEUTERED"] == 1))
                # Shots current
                line.append(self.apYesNo(medical.get_vaccinated(self.dbo, int(an["ID"]))))
                # Housetrained
                line.append(self.apYesNoUnknown(an["ISHOUSETRAINED"]))
                # Declawed
                line.append(self.apYesNo(an["DECLAWED"] == 1))
                # Special needs
                line.append(self.apYesNo(an["CRUELTYCASE"] == 1 or an["HASSPECIALNEEDS"] == 1))
                # Hair Length
                line.append(self.apHairLength(an))
                # YouTube Video URL
                line.append(self.apYouTubeURL(an["WEBSITEVIDEOURL"]))
                # Add to our CSV file
                csv.append(",".join(line))
                # Mark success in the log
                self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals)

        # Upload the datafiles
        mapfile = self.apMapFile(self.pc.includeColours)
        self.saveFile(os.path.join(self.publishDir, "import.cfg"), mapfile)
        self.saveFile(os.path.join(self.publishDir, "pets.csv"), "\n".join(csv))
        self.log("Saving datafile and map, %s %s" % ("pets.csv", "import.cfg"))
        self.chdir("..", "")
        self.log("Uploading pets.csv")
        self.upload("pets.csv")
        if not self.pc.noImportFile:
            self.log("Uploading import.cfg")
            self.upload("import.cfg")
        else:
            self.log("import.cfg upload is DISABLED")
        self.log("-- FILE DATA --(csv)")
        self.log("\n".join(csv))
        self.log("-- FILE DATA --(map)")
        self.log(mapfile)
        self.cleanup()

class AnibaseUKPublisher(AbstractPublisher):
    """
    Handles updating UK Identichip microchips with the Anibase web service
    (which uses VetXML)
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.publisherName = "Anibase UK Publisher"
        self.setLogName("anibaseuk")

    def get_vetxml_species(self, asmspeciesid):
        SPECIES_MAP = {
            1:  "Canine",
            2:  "Feline",
            3:  "Avian",
            4:  "Rodent",
            5:  "Rodent",
            7:  "Rabbit",
            9:  "Polecat",
            11: "Reptilian",
            12: "Tortoise",
            13: "Reptilian",
            14: "Avian",
            15: "Avian",
            16: "Goat",
            10: "Rodent",
            18: "Rodent",
            20: "Rodent",
            21: "Fish",
            22: "Rodent",
            23: "Camelid",
            24: "Equine",
            25: "Equine",
            26: "Donkey"
        }
        if SPECIES_MAP.has_key(asmspeciesid):
            return SPECIES_MAP[asmspeciesid]
        return "Miscellaneous"

    def run(self):
        def xe(s): 
            if s is None: return ""
            return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        self.log(self.publisherName + " starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        practiceid = configuration.anibase_practice_id(self.dbo)
        pinno = configuration.anibase_pin_no(self.dbo)

        if pinno == "":
            self.setLastError("Anibase vet code must be set")
            return

        # TODO: Remove 999 pattern - not a live chip prefix and just being
        #       used during testing.
        animals = get_microchip_data(self.dbo, ['9851', '9861', '999'], "anibaseuk")
        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            return

        anCount = 0
        processed_animals = []
        for an in animals:
            try:
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    return

                # Validate certain items aren't blank so we aren't registering bogus data
                if utils.nulltostr(an["CURRENTOWNERADDRESS"].strip()) == "":
                    self.logError("Address for the new owner is blank, cannot process")
                    continue 

                if utils.nulltostr(an["CURRENTOWNERPOSTCODE"].strip()) == "":
                    self.logError("Postal code for the new owner is blank, cannot process")
                    continue

                if an["IDENTICHIPDATE"] is None:
                    self.logError("Microchip date cannot be blank, cannot process")
                    continue

                # Make sure the length is actually suitable
                if not len(an["IDENTICHIPNUMBER"]) in (9, 10, 15):
                    self.logError("Microchip length is not 9, 10 or 15, cannot process")
                    continue

                # Construct the XML document
                x = '<?xml version="1.0" encoding="UTF-8"?>\n' \
                    '<MicrochipRegistration>' \
                    '<Identification>' \
                    ' <PracticeID>' + practiceid + '</PracticeID>' \
                    ' <PinNo>' + pinno + '</PinNo>' \
                    ' <Source></Source>' \
                    '</Identification>' \
                    '<OwnerDetails>' \
                    ' <Salutation>' + xe(an["CURRENTOWNERTITLE"]) + '</Salutation>' \
                    ' <Initials>' + xe(an["CURRENTOWNERINITIALS"]) + '</Initials>' \
                    ' <Forenames>' + xe(an["CURRENTOWNERFORENAMES"]) + '</Forenames>' \
                    ' <Surname>' + xe(an["CURRENTOWNERSURNAME"]) + '</Surname>' \
                    ' <Address>' \
                    '  <Line1>'+ xe(an["CURRENTOWNERADDRESS"]) + '</Line1>' \
                    '  <LineOther>'+ xe(an["CURRENTOWNERTOWN"]) + '</LineOther>' \
                    '  <PostalCode>' + xe(an["CURRENTOWNERPOSTCODE"]) + '</PostalCode>' \
                    '  <County_State>'+ xe(an["CURRENTOWNERCOUNTY"]) + '</County_State>' \
                    '  <Country>USA</Country>' \
                    ' </Address>' \
                    ' <DaytimePhone><Number>' + xe(an["CURRENTOWNERWORKTELEPHONE"]) + '</Number><Note/></DaytimePhone>' \
                    ' <EveningPhone><Number>' + xe(an["CURRENTOWNERHOMETELEPHONE"]) + '</Number><Note/></EveningPhone>' \
                    ' <MobilePhone><Number>' + xe(an["CURRENTOWNERMOBILETELEPHONE"]) + '</Number><Note/></MobilePhone>' \
                    ' <EmergencyPhone><Number/><Note/></EmergencyPhone>' \
                    ' <OtherPhone><Number/><Note/></OtherPhone>' \
                    ' <EmailAddress>' + xe(an["CURRENTOWNEREMAILADDRESS"]) + '</EmailAddress>' \
                    ' <Fax />' \
                    '</OwnerDetails>' \
                    '<PetDetails>' \
                    '  <Name>' + xe(an["ANIMALNAME"]) + '</Name>' \
                    '  <Species>' + self.get_vetxml_species(an["SPECIESID"]) + '</Species>' \
                    '  <Breed><FreeText>' + xe(an["BREEDNAME"]) + '</FreeText><Code/></Breed>' \
                    '  <DateOfBirth>' + i18n.format_date("%m/%d/%Y", an["DATEOFBIRTH"]) + '</DateOfBirth>' \
                    '  <Gender>' + an["SEXNAME"][0:1] + '</Gender>' \
                    '  <Colour>' + xe(an["BASECOLOURNAME"]) + '</Colour>' \
                    '  <Markings>' + xe(an["MARKINGS"]) + '</Markings>' \
                    '  <Neutered>' + (an["NEUTERED"] == 1 and "true" or "false") + '</Neutered>' \
                    '  <NotableConditions>' + xe(an["HEALTHPROBLEMS"]) + '</NotableConditions>' \
                    '</PetDetails>' \
                    '<MicrochipDetails>' \
                    '  <MicrochipNumber>' + xe(an["IDENTICHIPNUMBER"]) + '</MicrochipNumber>' \
                    '  <ImplantDate>' + i18n.format_date("%m/%d/%Y", an["IDENTICHIPDATE"]) + '</ImplantDate>' \
                    '  <ImplanterName>' + xe(an["CREATEDBY"]) + '</ImplanterName>' \
                    '</MicrochipDetails>' \
                    '<ThirdPartyDisclosure>true</ThirdPartyDisclosure>' \
                    '<ReceiveMail>true</ReceiveMail>' \
                    '<ReceiveEmail>true</ReceiveEmail>' \
                    '<Authorisation>true</Authorisation>' \
                    '</MicrochipRegistration>'

                # Build our auth headers
                authheaders = {
                    "APIUSER": ANIBASE_API_USER,
                    "APIKEY": ANIBASE_API_KEY
                }

                try:
                    # Post the VetXML document
                    self.log("Posting microchip registration document to %s \n%s\n" % (ANIBASE_BASE_URL, x))
                    r = utils.post_xml(ANIBASE_BASE_URL, x, authheaders)
                    self.log("HTTP response headers: %s" % r["headers"])
                    self.log("HTTP response body: %s" % r["response"])

                    # Look in the headers for successful results
                    wassuccess = False
                    SUCCESS = ( "54000", "54100", "54108" )
                    for code in SUCCESS:
                        if str(r["headers"]).find(code) != -1:
                            self.log("successful %s response header found, marking processed" % code)
                            processed_animals.append(an)
                            # Mark success in the log
                            self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                            wassuccess = True
                            break

                    # If we got a chipfound=false message, mark the chip as processed and a success
                    # so we don't try and register it in future
                    if str(r["response"]).find("<chipFound>false</chipFound>") != -1:
                        self.log("chipFound=false response found, marking chip processed to prevent future sending")
                        processed_animals.append(an)
                        wassuccess = True

                    # If we saw an account not found message, there's no point sending 
                    # anything else as they will all trigger the same error
                    if str(r["headers"]).find("54101") != -1:
                        self.logError("received Anibase 54101 'sender not recognised' response header - abandoning run")
                        break

                    if not wassuccess:
                        self.logError("no successful response header %s received" % str(SUCCESS))

                except Exception,err:
                    em = str(err)
                    self.logError("Failed registering microchip: %s" % em, sys.exc_info())
                    continue

            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Only mark processed if we aren't using Anibase test URL
        if len(processed_animals) > 0 and ANIBASE_BASE_URL.find("test") == -1:
            self.log("successfully processed %d animals, marking sent" % len(processed_animals))
            self.markAnimalsPublished(processed_animals)

        if ANIBASE_BASE_URL.find("test") != -1:
            self.log("Anibase test mode, not marking animals published")

        self.saveLog()
        self.setPublisherComplete()

class FoundAnimalsPublisher(FTPPublisher):
    """
    Handles publishing to foundanimals.org
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        FTPPublisher.__init__(self, dbo, publishCriteria, 
            FOUNDANIMALS_FTP_HOST, FOUNDANIMALS_FTP_USER, FOUNDANIMALS_FTP_PASSWORD)
        self.publisherName = "FoundAnimals Publisher"
        self.setLogName("foundanimals")

    def run(self):
        
        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        org = configuration.organisation(self.dbo)
        folder = configuration.foundanimals_folder(self.dbo)
        if folder == "":
            self.setLastError("No FoundAnimals folder has been set.")
            self.cleanup()
            return

        animals = get_microchip_data(self.dbo, ["9", "0"], "foundanimals")
        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            self.cleanup()
            return

        if not self.openFTPSocket(): 
            self.setLastError("Failed to open FTP socket.")
            if self.logBuffer.find("530 Login") != -1:
                self.log("Found 530 Login incorrect: disabling FoundAnimals publisher.")
                configuration.publishers_enabled_disable(self.dbo, "fa")
            self.cleanup()
            return

        # foundanimals.org want data files called mmddyyyy_HHMMSS.csv in the shelter's own folder
        dateportion = i18n.format_date("%m%d%Y_%H%M%S", i18n.now(self.dbo.timezone))
        outputfile = "%s.csv" % dateportion
        self.mkdir(folder)
        self.chdir(folder)

        csv = []

        anCount = 0
        success = []
        for an in animals:
            try:
                line = []
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    self.cleanup()
                    return

                # Validate certain items aren't blank so we aren't registering bogus data
                if utils.nulltostr(an["CURRENTOWNERADDRESS"].strip()) == "":
                    self.logError("Address for the new owner is blank, cannot process")
                    continue 

                if utils.nulltostr(an["CURRENTOWNERPOSTCODE"].strip()) == "":
                    self.logError("Postal code for the new owner is blank, cannot process")
                    continue

                # Make sure the length is actually suitable
                if not len(an["IDENTICHIPNUMBER"]) in (9, 10, 15):
                    self.logError("Microchip length is not 9, 10 or 15, cannot process")
                    continue

                # First Name
                line.append("\"%s\"" % an["CURRENTOWNERFORENAMES"])
                # Last Name
                line.append("\"%s\"" % an["CURRENTOWNERSURNAME"])
                # Email Address
                line.append("\"%s\"" % an["CURRENTOWNEREMAILADDRESS"])
                # Address 1
                line.append("\"%s\"" % an["CURRENTOWNERADDRESS"])
                # Address 2
                line.append("\"\"")
                # City
                line.append("\"%s\"" % an["CURRENTOWNERTOWN"])
                # State
                line.append("\"%s\"" % an["CURRENTOWNERCOUNTY"])
                # Zip Code
                line.append("\"%s\"" % an["CURRENTOWNERPOSTCODE"])
                # Home Phone
                line.append("\"%s\"" % an["CURRENTOWNERHOMETELEPHONE"])
                # Work Phone
                line.append("\"%s\"" % an["CURRENTOWNERWORKTELEPHONE"])
                # Cell Phone
                line.append("\"%s\"" % an["CURRENTOWNERMOBILETELEPHONE"])
                # Pet Name
                line.append("\"%s\"" % an["ANIMALNAME"])
                # Microchip Number
                line.append("\"%s\"" % an["IDENTICHIPNUMBER"])
                # Service Date
                line.append("\"%s\"" % i18n.format_date("%m/%d/%Y", an["ACTIVEMOVEMENTDATE"]))
                # Date of Birth
                line.append("\"%s\"" % i18n.format_date("%m/%d/%Y", an["DATEOFBIRTH"]))
                # Species
                line.append("\"%s\"" % an["PETFINDERSPECIES"])
                # Sex
                line.append("\"%s\"" % an["SEXNAME"])
                # Spayed/Neutered
                line.append("\"%s\"" % an["NEUTERED"] == 1 and "Yes" or "No")
                # Primary Breed
                line.append("\"%s\"" % an["PETFINDERBREED"])
                # Secondary Breed
                line.append("\"%s\"" % an["PETFINDERBREED2"])
                # Color
                line.append("\"%s\"" % an["BASECOLOURNAME"])
                # Implanting Organization
                line.append("\"%s\"" % org)
                # Rescue Group Email
                line.append("\"%s\"" % configuration.foundanimals_email(self.dbo))
                # Add to our CSV file
                csv.append(",".join(line))
                # Mark success in the log
                self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                success.append(an)
            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(success)

        header = "First Name,Last Name,Email Address,Address 1,Address 2,City,State,Zip Code," \
            "Home Phone,Work Phone,Cell Phone,Pet Name,Microchip Number,Service Date," \
            "Date of Birth,Species,Sex,Spayed/Neutered,Primary Breed,Secondary Breed," \
            "Color,Implanting Organization,Rescue Group Email\n"
        self.saveFile(os.path.join(self.publishDir, outputfile), header + "\n".join(csv))
        self.log("Uploading datafile %s" % outputfile)
        self.upload(outputfile)
        self.log("Uploaded %s" % outputfile)
        self.log("-- FILE DATA --")
        self.log(header + "\n".join(csv))
        self.cleanup()

class HelpingLostPetsPublisher(FTPPublisher):
    """
    Handles publishing to helpinglostpets.com
    """
    def __init__(self, dbo, publishCriteria):
        l = dbo.locale
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        publishCriteria.checkSocket = True
        publishCriteria.scaleImages = 1
        FTPPublisher.__init__(self, dbo, publishCriteria, 
            HELPINGLOSTPETS_FTP_HOST, configuration.helpinglostpets_user(dbo), 
            configuration.helpinglostpets_password(dbo))
        self.publisherName = i18n._("HelpingLostPets Publisher", l)
        self.setLogName("helpinglostpets")

    def hlpYesNo(self, condition):
        """
        Returns a CSV entry for yes or no based on the condition
        """
        if condition:
            return "\"Yes\""
        else:
            return "\"No\""

    def run(self):
        
        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        shelterid = configuration.helpinglostpets_orgid(self.dbo)
        if shelterid == "":
            self.setLastError("No helpinglostpets.com organisation ID has been set.")
            return
        foundanimals = lostfound.get_foundanimal_find_simple(self.dbo)
        animals = self.getMatchingAnimals()
        if len(animals) == 0 and len(foundanimals) == 0:
            self.setLastError("No animals found to publish.")
            self.cleanup()
            return

        if not self.openFTPSocket(): 
            self.setLastError("Failed opening FTP socket.")
            if self.logBuffer.find("530 Login") != -1:
                self.log("Found 530 Login incorrect: disabling HelpingLostPets publisher.")
                configuration.publishers_enabled_disable(self.dbo, "hlp")
            self.cleanup()
            return

        csv = []

        # Found Animals
        anCount = 0
        for an in foundanimals:
            try:
                line = []
                anCount += 1
                self.log("Processing Found Animal: %d: %s (%d of %d)" % ( an["ID"], an["COMMENTS"], anCount, len(foundanimals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    return

                # If a limit was set, stop now
                if self.pc.limit > 0 and anCount > self.pc.limit:
                    self.log("Hit publishing limit of %d animals. Stopping." % self.pc.limit)
                    break

                # OrgID
                line.append("\"%s\"" % shelterid)
                # PetID
                line.append("\"F%d\"" % an["ID"])
                # Status
                line.append("\"Found\"")
                # Name
                line.append("\"%d\"" % an["ID"])
                # Species
                line.append("\"%s\"" % an["SPECIESNAME"])
                # Sex
                line.append("\"%s\"" % an["SEXNAME"])
                # PrimaryBreed
                line.append("\"%s\"" % an["BREEDNAME"])
                # SecondaryBreed
                line.append("\"\"")
                # Age, one of Baby, Young, Adult, Senior - just happens to match our default age groups
                line.append("\"%s\"" % an["AGEGROUP"])
                # Altered - don't have
                line.append("\"\"")
                # Size, one of Small, Medium or Large or X-Large - also don't have
                line.append("\"\"")
                # ZipPostal
                line.append("\"%s\"" % an["AREAPOSTCODE"])
                # Description
                notes = str(an["DISTFEAT"]) + "\n" + str(an["COMMENTS"]) + "\n" + str(an["AREAFOUND"])
                # Strip carriage returns
                notes = notes.replace("\r\n", "<br />")
                notes = notes.replace("\r", "<br />")
                notes = notes.replace("\n", "<br />")
                notes = notes.replace("\"", "&ldquo;")
                notes = notes.replace("\'", "&lsquo;")
                notes = notes.replace("\`", "&lsquo;")
                line.append("\"%s\"" % notes)
                # Photo
                line.append("\"\"")
                # Colour
                line.append("\"%s\"" % an["BASECOLOURNAME"])
                # MedicalConditions
                line.append("\"\"")
                # LastUpdated
                line.append("\"%s\"" % i18n.python2unix(an["LASTCHANGEDDATE"]))
                # Add to our CSV file
                csv.append(",".join(line))
                # Mark success in the log
                self.logSuccess("Processed Found Animal: %d: %s (%d of %d)" % ( an["ID"], an["COMMENTS"], anCount, len(foundanimals)))
            except Exception,err:
                self.logError("Failed processing found animal: %s, %s" % (str(an["ID"]), err), sys.exc_info())

        # Animals
        anCount = 0
        for an in animals:
            try:
                line = []
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    return

                # If a limit was set, stop now
                if self.pc.limit > 0 and anCount > self.pc.limit:
                    self.log("Hit publishing limit of %d animals. Stopping." % self.pc.limit)
                    break

                # Upload one image for this animal
                self.uploadImage(an, an["WEBSITEMEDIANAME"], an["SHELTERCODE"] + ".jpg")
                # OrgID
                line.append("\"%s\"" % shelterid)
                # PetID
                line.append("\"A%d\"" % an["ID"])
                # Status
                line.append("\"Adoptable\"")
                # Name
                line.append("\"%s\"" % an["ANIMALNAME"])
                # Species
                line.append("\"%s\"" % an["SPECIESNAME"])
                # Sex
                line.append("\"%s\"" % an["SEXNAME"])
                # PrimaryBreed
                line.append("\"%s\"" % an["BREEDNAME1"])
                # SecondaryBreed
                if an["CROSSBREED"] == 1:
                    line.append("\"%s\"" % an["BREEDNAME2"])
                else:
                    line.append("\"\"")
                # Age, one of Baby, Young, Adult, Senior
                ageinyears = i18n.date_diff_days(an["DATEOFBIRTH"], i18n.now(self.dbo.timezone))
                ageinyears /= 365.0
                agename = "Adult"
                if ageinyears < 0.5: agename = "Baby"
                elif ageinyears < 2: agename = "Young"
                elif ageinyears < 9: agename = "Adult"
                else: agename = "Senior"
                line.append("\"%s\"" % agename)
                # Altered
                line.append("%s" % self.hlpYesNo(an["NEUTERED"] == 1))
                # Size, one of Small, Medium or Large or X-Large
                ansize = "Medium"
                if an["SIZE"] == 0 : ansize = "X-Large"
                elif an["SIZE"] == 1: ansize = "Large"
                elif an["SIZE"] == 2: ansize = "Medium"
                elif an["SIZE"] == 3: ansize = "Small"
                line.append("\"%s\"" % ansize)
                # ZipPostal
                line.append("\"%s\"" % configuration.helpinglostpets_postal(self.dbo))
                # Description
                line.append("\"%s\"" % self.getDescription(an, True))
                # Photo
                line.append("\"%s.jpg\"" % an["SHELTERCODE"])
                # Colour
                line.append("\"%s\"" % an["BASECOLOURNAME"])
                # MedicalConditions
                line.append("\"%s\"" % an["HEALTHPROBLEMS"])
                # LastUpdated
                line.append("\"%s\"" % i18n.python2unix(an["LASTCHANGEDDATE"]))
                # Add to our CSV file
                csv.append(",".join(line))
                # Mark success in the log
                self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals)

        header = "OrgID, PetID, Status, Name, Species, Sex, PrimaryBreed, SecondaryBreed, Age, Altered, Size, ZipPostal, Description, Photo, Colour, MedicalConditions, LastUpdated\n"
        filename = shelterid + ".txt"
        self.saveFile(os.path.join(self.publishDir, filename), header + "\n".join(csv))
        self.log("Uploading datafile %s" % filename)
        self.upload(filename)
        self.log("Uploaded %s" % filename)
        self.log("-- FILE DATA --")
        self.log(header + "\n".join(csv))
        # Clean up
        self.closeFTPSocket()
        self.deletePublishDirectory()
        self.saveLog()
        self.setPublisherComplete()

class HTMLPublisher(FTPPublisher):
    """
    Handles publishing to the internet via static HTML files to 
    an FTP server.
    """
    navbar = ""
    totalAnimals = 0
    user = "cron"

    def __init__(self, dbo, publishCriteria, user):
        l = dbo.locale
        # If we have a database override and it's not been ignored, use it
        if MULTIPLE_DATABASES_PUBLISH_FTP is not None and not configuration.publisher_ignore_ftp_override(dbo):
            c = MULTIPLE_DATABASES_PUBLISH_FTP
            publishCriteria.uploadDirectly = True
            publishCriteria.clearExisting = True
            FTPPublisher.__init__(self, dbo, publishCriteria,
                self.replaceMDBTokens(dbo, c["host"]),
                self.replaceMDBTokens(dbo, c["user"]),
                self.replaceMDBTokens(dbo, c["pass"]),
                c["port"], 
                self.replaceMDBTokens(dbo, c["chdir"]),
                c["passive"])
        else:                
            FTPPublisher.__init__(self, dbo, publishCriteria, 
                configuration.ftp_host(dbo), configuration.ftp_user(dbo), configuration.ftp_password(dbo),
                configuration.ftp_port(dbo), configuration.ftp_root(dbo), configuration.ftp_passive(dbo))
        self.user = user
        self.publisherName = i18n._("HTML/FTP Publisher", l)
        self.setLogName("html")

    def escapePageName(self, s):
        suppress = [ " ", "(", ")", "/", "\\", "!", "?", "*" ]
        for x in suppress:
            s = s.replace(x, "_")
        return s

    def getPathFromStyle(self):
        """
        Looks at the publishing criteria and returns a DBFS path to get
        the template files from
        """
        if self.pc.style == ".": return "/internet"
        return "/internet/" + self.pc.style

    def getHeader(self):
        path = self.getPathFromStyle()
        self.log("Getting header style from: %s" % path)
        header = dbfs.get_string(self.dbo, "head.html", path)
        if header == "": header = dbfs.get_string(self.dbo, "pih.dat", path)
        if header == "":
            header = """<html>
            <head>
            <title>Animals Available For Adoption</title>
            </head>
            <body>
            <p>$$NAV$$</p>
            <table width="100%%">
            """
        return header

    def getFooter(self):
        path = self.getPathFromStyle()
        self.log("Getting footer style from: %s" % path)
        footer = dbfs.get_string(self.dbo, "foot.html", path)
        if footer == "": footer = dbfs.get_string(self.dbo, "pif.dat", path)
        if footer == "":
            footer = "</table></body></html>"
        return footer

    def getBody(self):
        path = self.getPathFromStyle()
        body = dbfs.get_string(self.dbo, "body.html", path)
        if body == "": body = dbfs.get_string(self.dbo, "pib.dat", path)
        if body == "":
            body = "<tr><td><img height=200 width=320 src=$$IMAGE$$></td>" \
                "<td><b>$$ShelterCode$$ - $$AnimalName$$</b><br>" \
                "$$BreedName$$ $$SpeciesName$$ aged $$Age$$<br><br>" \
                "<b>Details</b><br><br>$$WebMediaNotes$$<hr></td></tr>"
        return body

    def saveTemplateImages(self):
        """
        Saves all image files in the template folder to the publish directory
        """
        dbfs.get_files(self.dbo, "%.jp%g", self.getPathFromStyle(), self.publishDir)
        dbfs.get_files(self.dbo, "%.png", self.getPathFromStyle(), self.publishDir)
        dbfs.get_files(self.dbo, "%.gif", self.getPathFromStyle(), self.publishDir)
        # TODO: Upload these via FTP

    def substituteHFTag(self, searchin, page, user, title = ""):
        """
        Substitutes special header and footer tokens in searchin. page
        contains the current page number.
        """
        output = searchin
        nav = self.navbar.replace("<a href=\"%d.%s\">%d</a>" % (page, self.pc.extension, page), str(page))
        dateportion = i18n.python2display(self.locale, i18n.now(self.dbo.timezone))
        timeportion = time.strftime("%H:%M:%S", i18n.now(self.dbo.timezone).timetuple())
        if page != -1:
            output = output.replace("$$NAV$$", nav)
        else:
            output = output.replace("$$NAV$$", "")
        output = output.replace("$$TITLE$$", title)
        output = output.replace("$$TOTAL$$", str(self.totalAnimals))
        output = output.replace("$$DATE$$", dateportion)
        output = output.replace("$$TIME$$", timeportion)
        output = output.replace("$$DATETIME$$", "%s %s" % (dateportion, timeportion))
        output = output.replace("$$VERSION$$", i18n.get_version())
        output = output.replace("$$REGISTEREDTO$$", configuration.organisation(self.dbo))
        output = output.replace("$$USER$$", "%s (%s)" % (user, users.get_real_name(self.dbo, user)))
        output = output.replace("$$ORGNAME$$", configuration.organisation(self.dbo))
        output = output.replace("$$ORGADDRESS$$", configuration.organisation_address(self.dbo))
        output = output.replace("$$ORGTEL$$", configuration.organisation_telephone(self.dbo))
        output = output.replace("$$ORGEMAIL$$", configuration.email(self.dbo))
        return output

    def substituteBodyTags(self, searchin, a):
        """
        Substitutes any tags in the body for animal data
        """
        tags = wordprocessor.animal_tags(self.dbo, a)
        tags["TotalAnimals"] = str(self.totalAnimals)
        tags["IMAGE"] = str(a["WEBSITEMEDIANAME"])
        # Note: WEBSITEMEDIANOTES becomes ANIMALCOMMENTS in get_animal_data when publisher_use_comments is on
        notes = utils.nulltostr(a["WEBSITEMEDIANOTES"])
        # Add any extra text
        notes += configuration.third_party_publisher_sig(self.dbo)
        # Preserve line endings in the bio
        notes = notes.replace("\n", "**le**")
        tags["WEBMEDIANOTES"] = notes 
        output = wordprocessor.substitute_tags(searchin, tags, True, "$$", "$$")
        output = output.replace("**le**", "<br />")
        return output

    def writeJavaScript(self, animals):
        # Remove original owner and other sensitive info from javascript database
        # before saving it
        for a in animals:
            for k in a.iterkeys():
                if k.startswith("ORIGINALOWNER") or k.startswith("BROUGHTINBY") \
                    or k.startswith("RESERVEDOWNER") or k.startswith("CURRENTOWNER") \
                    or k == "DISPLAYLOCATION":
                    a[k] = ""
        self.saveFile(os.path.join(self.publishDir, "db.js"), "publishDate='%s';animals=%s;" % (
            i18n.python2display(self.locale, i18n.now(self.dbo.timezone)), html.json(animals)))
        if self.pc.uploadDirectly:
            self.log("Uploading javascript database...")
            self.upload("db.js")
            self.log("Uploaded javascript database.")

    def run(self):
        self.setLastError("")
        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setStartPublishing()
        self.executePages()
        if self.pc.htmlByChildAdult or self.pc.htmlBySpecies:
            self.executeAgeSpecies(self.user, self.pc.htmlByChildAdult, self.pc.htmlBySpecies)
        if self.pc.htmlByType:
            self.executeType(self.user)
        if self.pc.outputAdopted:
            self.executeAdoptedPage()
        if self.pc.outputDeceased:
            self.executeDeceasedPage()
        if self.pc.outputForms:
            self.executeFormsPage()
        if self.pc.outputRSS:
            self.executeRSS()
        self.cleanup()
        self.resetPublisherProgress()

    def executeAdoptedPage(self):
        """
        Generates and uploads the page of recently adopted animals
        """
        self.log("Generating adopted animals page...")

        user = self.user
        thisPage = ""
        thisPageName = "adopted.%s" % self.pc.extension
        totalAnimals = 0
        l = self.dbo.locale

        try:
            cutoff = i18n.subtract_days(i18n.now(self.dbo.timezone), self.pc.outputAdoptedDays)
            orderby = "a.AnimalName"
            if self.pc.order == 0: orderby = "a.ActiveMovementDate"
            elif self.pc.order == 1: orderby = "a.ActiveMovementDate DESC"
            elif self.pc.order == 2: orderby = "a.AnimalName"
            animals = db.query(self.dbo, animal.get_animal_query(self.dbo) + " WHERE a.ActiveMovementType = 1 AND " \
                "a.ActiveMovementDate >= %s AND a.DeceasedDate Is Null AND a.NonShelterAnimal = 0 "
                "ORDER BY %s" % (db.dd(cutoff), orderby))
            totalAnimals = len(animals)
            header = self.substituteHFTag(self.getHeader(), -1, user, i18n._("Recently adopted", l))
            footer = self.substituteHFTag(self.getFooter(), -1, user, i18n._("Recently adopted", l))
            body = self.getBody()
            thisPage = header
        except Exception, err:
            self.setLastError("Error setting up adopted page: %s" % err)
            self.logError("Error setting up adopted page: %s" % err, sys.exc_info())
            return

        anCount = 0
        for an in animals:
            try:
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, totalAnimals))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    self.cleanup()
                    return

                # upload images for this animal to our current FTP
                self.uploadImages(an, True)

                # Add to the page
                thisPage += self.substituteBodyTags(body, an)
                self.log("Finished processing: %s" % an["SHELTERCODE"])

            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Append the footer, flush and upload the page
        thisPage += footer
        self.log("Saving page to disk: %s (%d bytes)" % (thisPageName, len(thisPage)))
        self.saveFile(os.path.join(self.publishDir, thisPageName), thisPage)
        self.log("Saved page to disk: %s" % thisPageName)
        if self.pc.uploadDirectly:
            self.log("Uploading page: %s" % thisPageName)
            self.upload(thisPageName)
            self.log("Uploaded page: %s" % thisPageName)

    def executeDeceasedPage(self):
        """
        Generates and uploads the page of recently deceased animals
        """
        self.log("Generating deceased animals page...")

        user = self.user
        thisPage = ""
        thisPageName = "deceased.%s" % self.pc.extension
        totalAnimals = 0
        l = self.dbo.locale

        try:
            cutoff = i18n.subtract_days(i18n.now(self.dbo.timezone), self.pc.outputAdoptedDays)
            orderby = "a.AnimalName"
            if self.pc.order == 0: orderby = "a.DeceasedDate"
            elif self.pc.order == 1: orderby = "a.DeceasedDate DESC"
            elif self.pc.order == 2: orderby = "a.AnimalName"
            animals = db.query(self.dbo, animal.get_animal_query(self.dbo) + " WHERE a.DeceasedDate Is Not Null AND " \
                "a.DeceasedDate >= %s AND a.NonShelterAnimal = 0 AND a.DiedOffShelter = 0 " \
                "ORDER BY %s" % (db.dd(cutoff), orderby))
            totalAnimals = len(animals)
            header = self.substituteHFTag(self.getHeader(), -1, user, i18n._("Recently deceased", l))
            footer = self.substituteHFTag(self.getFooter(), -1, user, i18n._("Recently deceased", l))
            body = self.getBody()
            thisPage = header
        except Exception, err:
            self.setLastError("Error setting up deceased page: %s" % err)
            self.logError("Error setting up deceased page: %s" % err, sys.exc_info())
            return

        anCount = 0
        for an in animals:
            try:
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, totalAnimals))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    self.cleanup()
                    return

                # upload images for this animal to our current FTP
                self.uploadImages(an, True)

                # Add to the page
                thisPage += self.substituteBodyTags(body, an)
                self.log("Finished processing: %s" % an["SHELTERCODE"])

            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Append the footer, flush and upload the page
        thisPage += footer
        self.log("Saving page to disk: %s (%d bytes)" % (thisPageName, len(thisPage)))
        self.saveFile(os.path.join(self.publishDir, thisPageName), thisPage)
        self.log("Saved page to disk: %s" % thisPageName)
        if self.pc.uploadDirectly:
            self.log("Uploading page: %s" % thisPageName)
            self.upload(thisPageName)
            self.log("Uploaded page: %s" % thisPageName)

    def executeFormsPage(self):
        """
        Generates and uploads the page of online forms
        """
        self.log("Generating online forms page...")

        thisPageName = "forms.%s" % self.pc.extension
        thisPage = ""

        try:
            forms = onlineform.get_onlineforms(self.dbo)
            thisPage = "<html><head><title>Online Forms</title></head><body>"
            thisPage += "<h2>Online Forms</h2>"
            account = ""
            if smcom.active():
                account = "account=%s&" % self.dbo.database 
            for f in forms:
                thisPage += "<p><a target='_blank' href='%s?%smethod=online_form_html&formid=%d'>%s</a></p>" % (SERVICE_URL, account, f["ID"], f["NAME"])
            thisPage += "</body></html>"
        except Exception, err:
            self.setLastError("Error creating forms page: %s" % err)
            self.logError("Error creating forms page: %s" % err, sys.exc_info())
            return

        # Flush and upload the page
        self.log("Saving page to disk: %s (%d bytes)" % (thisPageName, len(thisPage)))
        self.saveFile(os.path.join(self.publishDir, thisPageName), thisPage)
        self.log("Saved page to disk: %s" % thisPageName)
        if self.pc.uploadDirectly:
            self.log("Uploading page: %s" % thisPageName)
            self.upload(thisPageName)
            self.log("Uploaded page: %s" % thisPageName)

    def executeAgeSpecies(self, user, childadult = True, species = True):
        """
        Publisher that puts animals on pages by age and species
        childadult: True if we should split up pages by animals under/over 6 months 
        species: True if we should split up pages by species
        """
        self.log("HTMLPublisher (age/species pages) starting...")

        l = self.dbo.locale
        normHeader = self.getHeader()
        normFooter = self.getFooter()
        body = self.getBody()
        header = self.substituteHFTag(normHeader, 0, user, i18n._("Available for adoption", l))
        footer = self.substituteHFTag(normFooter, 0, user, i18n._("Available for adoption", l))

        # Calculate the number of days old an animal has to be to
        # count as an adult
        childAdultSplitDays = self.pc.childAdultSplit * 7

        # Open FTP socket, bail if it fails
        if not self.openFTPSocket():
            self.setLastError("Failed opening FTP socket.")
            return

        try:
            animals = self.getMatchingAnimals()
            self.totalAnimals = len(animals)

            anCount = 0
            pages = {}

            # Create default pages for every possible permutation
            defaultpages = []
            if childadult and species:
                spec = lookups.get_species(self.dbo)
                for sp in spec:
                    defaultpages.append("adult%s" % sp["SPECIESNAME"])
                    defaultpages.append("baby%s" % sp["SPECIESNAME"])
            elif childadult:
                defaultpages = [ "adult", "baby" ]
            elif species:
                spec = lookups.get_species(self.dbo)
                for sp in spec:
                    defaultpages.append(sp["SPECIESNAME"])
            for dp in defaultpages:
                pages["%s.%s" % (dp, self.pc.extension)] = header

            # Create an all page
            allpage = "all.%s" % self.pc.extension
            pages[allpage] = header

        except Exception, err:
            self.logError("Error setting up page: %s" % err, sys.exc_info())
            self.setLastError("Error setting up page: %s" % err)
            return

        for an in animals:
            try:
                anCount += 1

                # If a limit was set, stop now
                if self.pc.limit > 0 and anCount > self.pc.limit:
                    self.log("Hit publishing limit of %d animals. Stopping." % self.pc.limit)
                    break

                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, self.totalAnimals))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    self.cleanup()
                    return

                # upload all images for this animal to our current FTP
                self.uploadImages(an, True)
                
                # Calculate the new page name
                pagename = ".%s" % self.pc.extension
                if species:
                    pagename = "%s%s" % (an["SPECIESNAME"], pagename)
                if childadult:
                    days = i18n.date_diff_days(an["DATEOFBIRTH"], i18n.now(self.dbo.timezone))
                    if days < childAdultSplitDays:
                        pagename = "baby%s" % pagename
                    else:
                        pagename = "adult%s" % pagename

                # Does this page exist?
                if not pages.has_key(pagename):
                    # No, create it and add the header
                    page = header
                else:
                    page = pages[pagename]

                # Add this item to the page
                page += self.substituteBodyTags(body, an)
                pages[pagename] = page
                self.log("%s -> %s" % (an["SHELTERCODE"], pagename))

                # Add this item to our magic "all" page
                page = pages[allpage]
                page += self.substituteBodyTags(body, an)
                pages[allpage] = page
                
                # Mark success in the log
                self.log("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))

            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals)

        # Upload the pages
        for k, v in pages.iteritems():
            self.log("Saving page to disk: %s (%d bytes)" % (k, len(v + footer)))
            self.saveFile(os.path.join(self.publishDir, self.escapePageName(k)), v + footer)
            self.log("Saved page to disk: %s" % k)
            if self.pc.uploadDirectly:
                self.log("Uploading page: %s" % k)
                self.upload(self.escapePageName(k))
                self.log("Uploaded page: %s" % k)

    def executePages(self):
        """
        Publisher based on assigning animals to pages.
        """

        self.log("HTMLPublisher (numbered pages) starting...")

        user = self.user
        normHeader = self.getHeader()
        normFooter = self.getFooter()
        body = self.getBody()
        l = self.dbo.locale

        # Open FTP socket, bail if it fails
        if not self.openFTPSocket():
            self.setLastError("Failed opening FTP socket.")
            return

        try:
            animals = self.getMatchingAnimals()
            self.totalAnimals = len(animals)
            noPages = 0
            animalsPerPage = self.pc.animalsPerPage
            pages = {}

            # Calculate pages required
            if self.totalAnimals <= animalsPerPage:
                noPages = 1
            else:
                noPages = math.ceil(float(self.totalAnimals) / float(animalsPerPage))

            # Page navigation bar
            if noPages > 1:
                self.navbar = ""
                for i in range(1, int(noPages + 1)):
                    self.navbar += "<a href=\"%d.%s\">%d</a>&nbsp;" % ( i, self.pc.extension, i )

            # Start a new page with a header
            thisPageName = "1.%s" % self.pc.extension
            currentPage = 1
            itemsOnPage = 0

            # Substitute tags in the header and footer
            header = self.substituteHFTag(normHeader, currentPage, user, i18n._("Available for adoption", l))
            footer = self.substituteHFTag(normFooter, currentPage, user, i18n._("Available for adoption", l))
            thisPage = header
            anCount = 0

            # Clear any existing uploaded images
            if self.pc.forceReupload:
                self.clearExistingImages()

        except Exception, err:
            self.setLastError("Error setting up page: %s" % err)
            self.logError("Error setting up page: %s" % err, sys.exc_info())
            return

        for an in animals:
            try:
                anCount += 1

                # If a limit was set, stop now
                if self.pc.limit > 0 and anCount > self.pc.limit:
                    self.log("Hit publishing limit of %d animals. Stopping." % self.pc.limit)
                    break

                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, self.totalAnimals))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    self.cleanup()
                    return

                # upload all images for this animal to our current FTP
                self.uploadImages(an, True)
                
                # Slot free on this page?
                if itemsOnPage < animalsPerPage:
                    thisPage += self.substituteBodyTags(body, an)
                    itemsOnPage += 1
                    self.log("%s -> %s" % (an["SHELTERCODE"], thisPageName))
                else:
                    self.log("Current page complete.")
                    # No, append the footer, store the page
                    thisPage += footer
                    pages[thisPageName] = thisPage
                    # New page
                    currentPage += 1
                    thisPageName = "%d.%s" % ( currentPage, self.pc.extension )
                    header = self.substituteHFTag(normHeader, currentPage, user, i18n._("Available for adoption", l))
                    footer = self.substituteHFTag(normFooter, currentPage, user, i18n._("Available for adoption", l))
                    thisPage = header
                    # Append this animal
                    thisPage += self.substituteBodyTags(body, an)
                    itemsOnPage = 1
                    self.log("%s -> %s" % (an["SHELTERCODE"], thisPageName))
                
                # Mark success in the log
                self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))

            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals)

        # Done with animals, store the final page
        thisPage += footer
        pages[thisPageName] = thisPage

        # Clear any existing uploaded pages
        if self.pc.clearExisting: 
            self.clearExistingHTML()

        # Upload the new pages
        for k, v in pages.iteritems():
            self.log("Saving page to disk: %s (%d bytes)" % (k, len(v)))
            self.saveFile(os.path.join(self.publishDir, k), v)
            self.log("Saved page to disk: %s" % k)
            if self.pc.uploadDirectly:
                self.log("Uploading page: %s" % k)
                self.upload(k)
                self.log("Uploaded page: %s" % k)

        # Handle javascript db
        if self.pc.generateJavascriptDB:
            self.writeJavaScript(animals)

        # Save any additional images required by the template
        self.saveTemplateImages()

    def executeRSS(self):
        """
        Generates and uploads the rss.xml page
        """
        def rss_header():
            return """<?xml version="1.0" encoding="UTF-8"?>
                <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/" >
                <channel rdf:about="http://www.mydomain.com">
                <title>Animals for Adoption at $$ORGNAME$$</title>
                <description></description>
                <link>RDFLINK</link>
                </channel>"""
        def rss_body():
            return """<item rdf:about="RDFLINK">
                <title>$$ShelterCode$$ - $$AnimalName$$ ($$BreedName$$ $$SpeciesName$$ aged $$Age$$)</title>
                <link>RDFLINK</link>
                <description>
                &lt;img src="$$WebMediaFilename$$" align="left" /&gt;
                $$WebMediaNotes$$
                </description>
                </item>"""
        def rss_footer():
            return """</rdf:RDF>"""

        self.log("Generating rss.xml page...")

        user = self.user
        thisPage = ""
        thisPageName = "rss.xml"
        totalAnimals = 0
        link = MULTIPLE_DATABASES_PUBLISH_URL
        link = self.replaceMDBTokens(self.dbo, link)
        if link == "": link = BASE_URL

        try:
            animals = self.getMatchingAnimals()
            totalAnimals = len(animals)
            header = dbfs.get_string(self.dbo, "head.html", "/internet/rss")
            footer = dbfs.get_string(self.dbo, "foot.html", "/internet/rss")
            body = dbfs.get_string(self.dbo, "body.html", "/internet/rss")
            if header == "": header = rss_header()
            if footer == "": footer = rss_footer()
            if body == "": body = rss_body()
            header = self.substituteHFTag(header, 1, user)
            footer = self.substituteHFTag(footer, 1, user)
            thisPage = header
        except Exception, err:
            self.setLastError("Error setting up rss.xml: %s" % err)
            self.logError("Error setting up rss.xml: %s" % err, sys.exc_info())
            return

        anCount = 0
        for an in animals:
            try:
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, totalAnimals))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    self.cleanup()
                    return

                # Images already uploaded by Page/Species publisher

                # Add to the page
                thisPage += self.substituteBodyTags(body, an)
                self.log("Finished processing: %s" % an["SHELTERCODE"])

            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Append the footer, flush and upload the page
        thisPage += footer
        thisPage = thisPage.replace("RDFLINK", link)
        self.log("Saving page to disk: %s (%d bytes)" % (thisPageName, len(thisPage)))
        self.saveFile(os.path.join(self.publishDir, thisPageName), thisPage)
        self.log("Saved page to disk: %s" % thisPageName)
        if self.pc.uploadDirectly:
            self.log("Uploading page: %s" % thisPageName)
            self.upload(thisPageName)
            self.log("Uploaded page: %s" % thisPageName)

    def executeType(self, user):
        """
        Publisher that puts animals on pages by type
        """
        self.log("HTMLPublisher (type) starting...")

        l = self.dbo.locale
        normHeader = self.getHeader()
        normFooter = self.getFooter()
        body = self.getBody()
        header = self.substituteHFTag(normHeader, 0, user, i18n._("Available for adoption", l))
        footer = self.substituteHFTag(normFooter, 0, user, i18n._("Available for adoption", l))

        # Open FTP socket, bail if it fails
        if not self.openFTPSocket():
            self.setLastError("Failed opening FTP socket.")
            return

        try:
            animals = self.getMatchingAnimals()
            self.totalAnimals = len(animals)

            anCount = 0
            pages = {}

            # Create default pages for every possible permutation
            defaultpages = []
            atype = lookups.get_animal_types(self.dbo)
            for atype in lookups.get_animal_types(self.dbo):
                defaultpages.append(atype["ANIMALTYPE"])
            for dp in defaultpages:
                pages["%s.%s" % (dp, self.pc.extension)] = header

            # Create an all page
            allpage = "all.%s" % self.pc.extension
            pages[allpage] = header

        except Exception, err:
            self.logError("Error setting up page: %s" % err, sys.exc_info())
            self.setLastError("Error setting up page: %s" % err)
            return

        for an in animals:
            try:
                anCount += 1

                # If a limit was set, stop now
                if self.pc.limit > 0 and anCount > self.pc.limit:
                    self.log("Hit publishing limit of %d animals. Stopping." % self.pc.limit)
                    break

                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, self.totalAnimals))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    self.cleanup()
                    return

                # upload all images for this animal to our current FTP
                self.uploadImages(an, True)
                
                # Calculate the new page name
                pagename = "%s.%s" % (an["ANIMALTYPENAME"], self.pc.extension)

                # Does this page exist?
                if not pages.has_key(pagename):
                    # No, create it and add the header
                    page = header
                else:
                    page = pages[pagename]

                # Add this item to the page
                page += self.substituteBodyTags(body, an)
                pages[pagename] = page
                self.log("%s -> %s" % (an["SHELTERCODE"], pagename))

                # Add this item to our magic "all" page
                page = pages[allpage]
                page += self.substituteBodyTags(body, an)
                pages[allpage] = page
                
                # Mark success in the log
                self.log("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))

            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals)

        # Upload the pages
        for k, v in pages.iteritems():
            self.log("Saving page to disk: %s (%d bytes)" % (k, len(v + footer)))
            self.saveFile(os.path.join(self.publishDir, self.escapePageName(k)), v + footer)
            self.log("Saved page to disk: %s" % k)
            if self.pc.uploadDirectly:
                self.log("Uploading page: %s" % k)
                self.upload(self.escapePageName(k))
                self.log("Uploaded page: %s" % k)

class MeetAPetPublisher(AbstractPublisher):
    """
    Handles publishing to MeetAPet.com
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.publisherName = "MeetAPet Publisher"
        self.setLogName("meetapet")

    def mpYesNo(self, condition):
        """
        Returns yes or no for a condition.
        """
        if condition:
            return "yes"
        else:
            return "no"

    def mpYesNoBlank(self, v):
        """
        Returns 0 == Yes, 1 == No, 2 == Empty string
        """
        if v == 0: return "yes"
        elif v == 1: return "no"
        else: return ""

    def mpAverageWeight(self, species, breed):
        """
        Returns an average weight in pounds (as a string) for some
        known species.
        """
        weights = (
            ( "dog", "chihuah", "5" ),
            ( "dog", "pekingese", "7" ),
            ( "dog", "labrador", "65" ),
            ( "dog", "cocker", "25" ),
            ( "dog", "springer", "25" ),
            ( "dog", "shepherd", "75" ),
            ( "dog", "yorkshire", "7" ),
            ( "dog", "terrier", "15" ),
            ( "dog", "mastiff", "150" ),
            ( "dog", "retriever", "65" ),
            ( "dog", "beagle", "20" ),
            ( "dog", "boxer", "50" ),
            ( "dog", "bulldog", "40" ),
            ( "dog", "dachshund", "8" ),
            ( "dog", "poodle", "13" ),
            ( "dog", "shih", "10" ),
            ( "cat", "dom", "9" ),
            ( "cat", "siamese", "7" ),
            ( "cat", "maine", "15" )
        )
        species = str(species).lower()
        breed = str(breed).lower()
        for ws, wb, ww in weights:
            if species.find(ws) != -1 and breed.find(wb) != -1:
                return ww
        if species.find("dog") != -1:
            return "20"
        elif species.find("cat") != -1:
            return "9"
        else:
            return "0"

    def run(self):
        
        self.log("MeetAPetPublisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        key = configuration.meetapet_key(self.dbo)
        secret = configuration.meetapet_secret(self.dbo)
        userkey = configuration.meetapet_userkey(self.dbo)
        baseurl = MEETAPET_BASE_URL

        # Organisation prefix used to make pet urls unique
        org = configuration.organisation(self.dbo)
        org = org.replace(" ", "").replace("'", "_").lower() + "_"
        if len(org) > 10: org = org[0:10] 
       
        CREATE_URL = baseurl + "pet_create"
        UPDATE_URL = baseurl + "pet_update"
        DELETE_URL = baseurl + "pet_delete"

        if key == "" or secret == "" or userkey == "" or baseurl == "":
            self.setLastError("baseurl, key, secret and userkey all need to be set for meetapet.com publisher")
            return

        animals = self.getMatchingAnimals()
        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            return

        anCount = 0
        sentIds = []
        for an in animals:
            try:
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    return

                # If a limit was set, stop now
                if self.pc.limit > 0 and anCount > self.pc.limit:
                    self.log("Hit publishing limit of %d animals. Stopping." % self.pc.limit)
                    break

                # Sort out the pet bio
                notes = self.getDescription(an)

                # Sort out size
                ansize = "m"
                if an["SIZE"] == 0: ansize = "xl"
                elif an["SIZE"] == 1: ansize = "l"
                elif an["SIZE"] == 2: ansize = "m"
                elif an["SIZE"] == 3: ansize = "s"

                # Gender
                gender = "m"
                if an["SEX"] == 0: gender = "f"

                # Has shots
                shots = self.mpYesNo(medical.get_vaccinated(self.dbo, int(an["ID"])))

                # Build the animal POST data
                fields = {
                    "key": key,
                    "secret": secret, 
                    "shelter_key": userkey,
                    "pet_display": "yes",
                    "pet_available": "yes",
                    "pet_name": an["ANIMALNAME"],
                    "pet_url": org + str(an["SHELTERCODE"]),
                    "pet_type": an["SPECIESNAME"],
                    "pet_breed": an["BREEDNAME1"],
                    "pet_breed2": an["BREEDNAME2"],
                    "pet_size": ansize,
                    "pet_weight": self.mpAverageWeight(an["SPECIESNAME"], an["BREEDNAME"]),
                    "pet_gender": gender,
                    "pet_birthdate": i18n.format_date("%Y-%m-%d", an["DATEOFBIRTH"]),
                    "pet_bio": notes,
                    "pet_neutered": self.mpYesNoBlank(an["NEUTERED"]),
                    "pet_shots": shots,
                    "pet_special_needs": self.mpYesNoBlank(an["HASSPECIALNEEDS"])
                }

                files = {
                    "pet_image": ( an["WEBSITEMEDIANAME"], dbfs.get_string(self.dbo, an["WEBSITEMEDIANAME"]), "image/jpeg")
                }

                # Do we need to create or update this record?
                if self.getLastPublishedDate(an["ID"]) is None:
                    self.log("Using HTTP CREATE %s... %s" % (CREATE_URL, str(fields)))
                    r = utils.post_multipart(CREATE_URL, fields, files)
                    self.log("response: %s %s" % (r["headers"], r["response"]))
                    if r["response"].find("success") != -1:
                        self.markAnimalPublished(an["ID"])
                        sentIds.append(str(an["ID"]))
                        # Mark success in the log
                        self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                    else:
                        self.log("Found errors, not marking as published.")
                else:
                    self.log("Using HTTP UPDATE %s ... %s" % (UPDATE_URL, str(fields)))
                    r = utils.post_multipart(UPDATE_URL, fields, files)
                    self.log("response: %s %s" % (r["headers"], r["response"]))

            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Now, have a look back through our animals for anything we've already sent to
        # meetapet.com that's left the shelter so it can be deleted.
        try:
            ewc = ""
            if len(sentIds) != 0:
                ewc = " AND a.ID NOT IN (%s)" % ",".join(sentIds)
            toremove = db.query(self.dbo, "SELECT a.ID, a.AnimalName, a.ShelterCode FROM animal a " \
                "INNER JOIN animalpublished ap ON ap.AnimalID = a.ID " \
                "WHERE ap.PublishedTo = 'meetapet' AND ap.SentDate Is Not Null%s" % ewc)
            self.log("Found %d previously published animals to remove." % len(toremove))
            for an in toremove:
                fields = {
                    "key": key,
                    "secret": secret,
                    "shelter_key": userkey,
                    "pet_url": an["SHELTERCODE"]
                }
                self.log("Removing %s - %s via HTTP DELETE... %s" % (org + an["SHELTERCODE"], an["ANIMALNAME"], str(fields)))
                r = utils.post_form(DELETE_URL, fields)
                self.log("response: %s" % r["response"])
                if r["response"].find("success") != -1:
                    self.markAnimalUnpublished(an["ID"])
                else:
                    self.log("Found errors, not marking unpublished.")
        except Exception,err:
            self.logError("Failed removing adopted animals: %s" % err, sys.exc_info())

        self.saveLog()
        self.setPublisherComplete()

class PetFinderPublisher(FTPPublisher):
    """
    Handles publishing to PetFinder.com
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        publishCriteria.checkSocket = True
        publishCriteria.scaleImages = 1
        publishCriteria.uploadAllImages = True
        FTPPublisher.__init__(self, dbo, publishCriteria, 
            PETFINDER_FTP_HOST, configuration.petfinder_user(dbo), 
            configuration.petfinder_password(dbo))
        self.publisherName = "PetFinder Publisher"
        self.setLogName("petfinder")

    def pfYesNo(self, condition):
        """
        Returns a CSV entry for yes or no based on the condition
        """
        if condition:
            return "\"1\""
        else:
            return "\"\""

    def run(self):

        self.log("PetFinderPublisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        if not self.checkMappedSpecies():
            self.setLastError("Not all species have been mapped.")
            self.cleanup()
            return
        if not self.checkMappedBreeds():
            self.setLastError("Not all breeds have been mapped.")
            self.cleanup()
            return
        shelterid = configuration.petfinder_user(self.dbo)
        if shelterid == "":
            self.setLastError("No PetFinder.com shelter id has been set.")
            self.cleanup()
            return
        animals = self.getMatchingAnimals()
        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            self.cleanup()
            return

        if not self.openFTPSocket(): 
            self.setLastError("Failed opening FTP socket.")
            if self.logBuffer.find("530 Login") != -1:
                self.log("Found 530 Login incorrect: disabling PetFinder publisher.")
                configuration.publishers_enabled_disable(self.dbo, "pf")
            self.cleanup()
            return

        # Do the images first
        self.mkdir("import")
        self.chdir("import")
        self.mkdir("photos")
        self.chdir("photos", "import/photos")

        csv = []

        anCount = 0
        for an in animals:
            try:
                line = []
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    self.cleanup()
                    return

                # If a limit was set, stop now
                if self.pc.limit > 0 and anCount > self.pc.limit:
                    self.log("Hit publishing limit of %d animals. Stopping." % self.pc.limit)
                    break

                # Upload images for this animal
                self.uploadImages(an, False, 3)
                # Mapped species
                line.append("\"%s\"" % an["PETFINDERSPECIES"])
                # Breed 1
                line.append("\"%s\"" % an["PETFINDERBREED"])
                # Age, one of Adult, Baby, Senior and Young
                ageinyears = i18n.date_diff_days(an["DATEOFBIRTH"], i18n.now(self.dbo.timezone))
                ageinyears /= 365.0
                agename = "Adult"
                if ageinyears < 0.5: agename = "Baby"
                elif ageinyears < 2: agename = "Young"
                elif ageinyears < 9: agename = "Adult"
                else: agename = "Senior"
                line.append("\"%s\"" % agename)
                # Name
                line.append("\"%s\"" % an["ANIMALNAME"].replace("\"", "\"\""))
                # Size, one of S, M, L, XL
                ansize = "M"
                if an["SIZE"] == 0: ansize = "XL"
                elif an["SIZE"] == 1: ansize = "L"
                elif an["SIZE"] == 2: ansize = "M"
                elif an["SIZE"] == 3: ansize = "S"
                line.append("\"%s\"" % ansize)
                # Sex, one of M or F
                sexname = "M"
                if an["SEX"] == 0: sexname = "F"
                line.append("\"%s\"" % sexname)
                # Description
                line.append("\"%s\"" % self.getDescription(an, False, True))
                # Special needs
                if an["CRUELTYCASE"] == 1:
                    line.append("\"1\"")
                elif an["HASSPECIALNEEDS"] == 1:
                    line.append("\"1\"")
                else:
                    line.append("\"\"")
                # Has shots
                line.append(self.pfYesNo(medical.get_vaccinated(self.dbo, int(an["ID"]))))
                # Altered
                line.append(self.pfYesNo(an["NEUTERED"] == 1))
                # No Dogs
                line.append(self.pfYesNo(an["ISGOODWITHDOGS"] == 1))
                # No Cats
                line.append(self.pfYesNo(an["ISGOODWITHCATS"] == 1))
                # No Kids
                line.append(self.pfYesNo(an["ISGOODWITHCHILDREN"] == 1))
                # No Claws
                line.append(self.pfYesNo(an["DECLAWED"] == 1))
                # Housebroken
                line.append(self.pfYesNo(an["ISHOUSETRAINED"] == 0))
                # ID
                line.append("\"%s\"" % an["SHELTERCODE"])
                # Breed 2
                line.append("\"%s\"" % self.getPublisherBreed(an, 2))
                # Mix
                line.append(self.pfYesNo(an["CROSSBREED"] == 1))
                # Add to our CSV file
                csv.append(",".join(line))
                # Mark success in the log
                self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals)

        # Upload the datafiles
        mapfile = "; PetFinder import map. This file was autogenerated by\n" \
            "; Animal Shelter Manager. http://sheltermanager.com\n" \
            "; The FREE, open source solution for animal sanctuaries and rescue shelters.\n\n" \
            "#SHELTERID:%s\n" \
            "#0:Animal=Animal\n" \
            "#1:Breed=Breed\n" \
            "#2:Age=Age\n" \
            "#3:Name=Name\n" \
            "#4:Size=Size\n" \
            "#5:Sex=Sex\n" \
            "Female=F\n" \
            "Male=M\n" \
            "#6:Description=Dsc\n" \
            "#7:SpecialNeeds=SpecialNeeds\n" \
            "#8:HasShots=HasShots\n" \
            "#9:Altered=Altered\n" \
            "#10:NoDogs=NoDogs\n" \
            "#11:NoCats=NoCats\n" \
            "#12:NoKids=NoKids\n" \
            "#13:Declawed=Declawed\n" \
            "#14:HouseBroken=HouseBroken\n" \
            "#15:Id=Id\n" \
            "#16:Breed2=Breed2\n" \
            "#ALLOWUPDATE:Y\n" \
            "#HEADER:N" % shelterid
        self.saveFile(os.path.join(self.publishDir, shelterid + "import.cfg"), mapfile)
        self.saveFile(os.path.join(self.publishDir, shelterid), "\n".join(csv))
        self.log("Uploading datafile and map, %s %s" % (shelterid, shelterid + "import.cfg"))
        self.chdir("..", "import")
        self.upload(shelterid)
        self.upload(shelterid + "import.cfg")
        self.log("Uploaded %s %s" % ( shelterid, shelterid + "import.cfg"))
        self.log("-- FILE DATA -- (csv)")
        self.log("\n".join(csv))
        self.log("-- FILE DATA -- (map)")
        self.log(mapfile)
        self.cleanup()

class PetLinkPublisher(AbstractPublisher):
    """
    Handles publishing of updated microchip info to PetLink.net
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.publisherName = "PetLink Publisher"
        self.setLogName("petlink")

    def plYesNo(self, condition):
        """
        Returns yes or no for a condition.
        """
        if condition:
            return "y"
        else:
            return "n"

    def plBreed(self, breedname, speciesname, iscross):
        """
        Returns a PetLink breed of either the breed name,
        "Mixed Breed" if iscross == 1 or "Other" if the species
        is not Cat or Dog.
        """
        if speciesname.lower().find("cat") != -1 and speciesname.lower().find("dog") != -1:
            return "Other"
        if iscross == 1:
            return "Mixed Breed"
        return breedname

    def run(self):
        
        self.log("PetLinkPublisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        email = configuration.petlink_email(self.dbo)
        password = configuration.petlink_password(self.dbo)
        chippass = configuration.petlink_chippassword(self.dbo)
        baseurl = PETLINK_BASE_URL

        if email == "" or password == "":
            self.setLastError("No PetLink login has been set.")
            return

        if chippass == "" or baseurl == "":
            self.setLastError("baseurl and chippass need to be set for petlink.com publisher")
            return

        animals = get_microchip_data(self.dbo, ['98102',], "petlink")
        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            return

        LOGIN_URL = baseurl + "j_acegi_security_check"
        UPLOAD_URL = baseurl + "animalprofessional/massImportUpload.spring"
        WELCOME_URL = baseurl + "cms2.spring?path=/welcome.html"

        # Login via HTTP
        fields = {
            "j_username": email,
            "j_password": password
        }
        try:
            self.log("Getting PetLink welcome page...")
            r = utils.get_url(WELCOME_URL)
            try:
                rcookies = r["cookies"]
                sessionid = rcookies["JSESSIONID"]
            except KeyError:
                self.setLastError("Login failed (no JSESSIONID cookie).")
                self.saveLog()
                return
            self.log("Homepage returned headers: %s" % r["headers"])
            self.log("Found session cookie: %s" % sessionid)
            self.log("Logging in to PetLink.net... ")
            r = utils.post_form(LOGIN_URL, fields, cookies = rcookies)
            if r["response"].find("incorrect user name or password") != -1:
                self.setLastError("Login failed (invalid username or password)")
                self.saveLog()
                return
            elif r["response"].find("Hello") == -1:
                self.setLastError("Login failed (no Hello found).")
                self.log("response: headers=%s, body=%s" % (r["headers"], r["response"]))
                self.saveLog()
                return
            else:
                self.log("Login to PetLink successful.")
        except Exception,err:
            self.logError("Failed logging in: %s" % err, sys.exc_info())
            self.setLastError("Login failed (error during HTTP request).")
            self.saveLog()
            return

        anCount = 0
        csv = []
        processed_animals = []
        csv.append("Software,TransactionType,MicrochipID,FirstName,LastName,Address,City,State,ZipCode,Country," \
            "Phone1,Phone2,Phone3,Email,Password,Date_of_Implant,PetName,Species,Breed,Gender," \
            "Spayed_Neutered,ColorMarkings")
        for an in animals:
            try:
                line = []
                anCount += 1
                self.log("Processing: %s: %s (%d of %d) - %s" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals), an["IDENTICHIPNUMBER"]))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    return

                # If the microchip number isn't 15 digits, skip it
                if len(an["IDENTICHIPNUMBER"].strip()) != 15:
                    self.logError("Chip number failed validation (%s not 15 digits), skipping." % an["IDENTICHIPNUMBER"])
                    continue

                # Validate certain items aren't blank so we aren't registering bogus data
                if utils.nulltostr(an["CURRENTOWNERADDRESS"].strip()) == "":
                    self.logError("Address for the new owner is blank, cannot process")
                    continue 

                if utils.nulltostr(an["CURRENTOWNERPOSTCODE"].strip()) == "":
                    self.logError("Postal code for the new owner is blank, cannot process")
                    continue

                # If there's no email or home phone, PetLink won't accept it
                email = utils.nulltostr(an["CURRENTOWNEREMAILADDRESS"]).strip()
                homephone = utils.nulltostr(an["CURRENTOWNERHOMETELEPHONE"]).strip()
                if email == "" and homephone == "":
                    self.logError("No email address or home telephone for owner, skipping.")
                    continue
                
                # If we don't have an email address, use the owner's
                # phone number @petlink.tmp
                if email == "":
                    email = "".join(c for c in homephone if c.isdigit())
                    email = email + "@petlink.tmp"

                # Software
                line.append("\"ASM\"")
                # TransactionType
                line.append("\"%s\"" % ( self.getLastPublishedDate(an["ID"]) is None and 'N' or 'T' ))
                # MicrochipID
                line.append("\"%s\"" % ( an["IDENTICHIPNUMBER"] ))
                # FirstName
                line.append("\"%s\"" % ( an["CURRENTOWNERFORENAMES"] ))
                # LastName
                line.append("\"%s\"" % ( an["CURRENTOWNERSURNAME"] ))
                # Address
                line.append("\"%s\"" % ( an["CURRENTOWNERADDRESS"] ))
                # City
                line.append("\"%s\"" % ( an["CURRENTOWNERTOWN"] ))
                # State
                line.append("\"%s\"" % ( an["CURRENTOWNERCOUNTY"] ))
                # ZipCode
                line.append("\"%s\"" % ( an["CURRENTOWNERPOSTCODE"] ))
                # Country
                line.append("\"USA\"")
                # Phone1
                line.append("\"%s\"" % ( an["CURRENTOWNERHOMETELEPHONE"] ))
                # Phone2
                line.append("\"%s\"" % ( an["CURRENTOWNERWORKTELEPHONE"] ))
                # Phone3
                line.append("\"%s\"" % ( an["CURRENTOWNERMOBILETELEPHONE"] ))
                # Email (mandatory)
                line.append("\"%s\"" % ( email ))
                # Password (config item, unique to each shelter)
                line.append("\"%s\"" % chippass)
                # Date_of_Implant (yy-mm-dd)
                line.append("\"%s\"" % i18n.format_date("%y-%m-%d", an["IDENTICHIPDATE"]))
                # PetName
                line.append("\"%s\"" % an["ANIMALNAME"])
                # Species
                line.append("\"%s\"" % an["SPECIESNAME"])
                # Breed (or "Mixed Breed" for crossbreeds, Other for animals not cats and dogs)
                line.append("\"%s\"" % self.plBreed(an["BREEDNAME1"], an["SPECIESNAME"], an["CROSSBREED"]))
                # Gender
                line.append("\"%s\"" % an["SEXNAME"])
                # Spayed_Neutered (y or n)
                line.append("\"%s\"" % self.plYesNo(an["NEUTERED"]))
                # ColorMarkings (our BaseColour field)
                line.append("\"%s\"" % an["BASECOLOURNAME"])
                # Add to our data file.  
                csv.append(",".join(line))
                # Remember we included this one
                processed_animals.append(an)
                # Mark success in the log
                self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # If we excluded our only animals and have nothing to send, stop now
        if len(csv) == 1:
            self.log("No animals left to send to PetLink.")
            self.saveLog()
            self.setPublisherComplete()
            return

        # POST the csv file
        files = {
            "file": ( "import.csv", "\n".join(csv), "text/csv")
        }
        self.log("Uploading data file (%d csv lines) to %s..." % (len(csv), UPLOAD_URL))
        try:
            r = utils.post_multipart(url=UPLOAD_URL, files=files, cookies=rcookies)
            self.log("(%s redirects) req hdr: %s, \nreq data: %s" % (r["redirects"], r["requestheaders"], r["requestbody"]))

            # Look for any errors in the response
            for e in utils.regex_multi("id=(\d+?), transponder: (.+?)</li>", r["response"]):
                chip = e[0]
                message = e[1]

                # Iterate over a copy of the processed list so we can remove this animal from it
                for an in processed_animals[:]:
                    if an["IDENTICHIPNUMBER"] == chip:
                        # Remove this animal from the processed list
                        processed_animals.remove(an)
                        self.logError("%s: %s (%s) - Received error message from PetLink: %s" % \
                            (an["SHELTERCODE"], an["ANIMALNAME"], an["IDENTICHIPNUMBER"], message))
                        # If the message was that the chip is already registered,
                        # mark the animal as published but at the intake date -
                        # this will force this publisher to put it through as a transfer
                        # next time
                        if message.startswith("This microchip code has already been registered"):
                            self.markAnimalPublished(an["ID"], an["DATEBROUGHTIN"])
                            self.log("%s: %s (%s) - Already registered, marking as PetLink TRANSFER for next publish" % \
                                (an["SHELTERCODE"], an["ANIMALNAME"], an["IDENTICHIPNUMBER"]))

            if r["response"].find("Upload Completed") != -1:
                # Mark published
                self.log("Got successful upload response, marking processed animals as sent to petlink")
                self.markAnimalsPublished(processed_animals)
            else:
                self.logError("didn't find successful response, abandoning.")
                self.log("response hdr: %s, \nresponse: %s" % (r["headers"], r["response"]))
        except Exception,err:
            self.logError("Failed uploading data file: %s" % err)

        self.saveLog()
        self.setPublisherComplete()

class PetRescuePublisher(FTPPublisher):
    """
    Handles publishing to petrescue.com.au
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        publishCriteria.checkSocket = True
        publishCriteria.scaleImages = 1
        FTPPublisher.__init__(self, dbo, publishCriteria, 
            PETRESCUE_FTP_HOST, configuration.petrescue_user(dbo), 
            configuration.petrescue_password(dbo), 21, "", True)
        self.publisherName = "PetRescue Publisher"
        self.setLogName("petrescue")

    def prTrueFalse(self, condition):
        """
        Returns a CSV entry for TRUE or FALSE based on the condition
        """
        if condition:
            return "TRUE"
        else:
            return "FALSE"

    def prYesNo(self, condition):
        """
        Returns a CSV entry for Yes or No based on the condition
        """
        if condition:
            return "Yes"
        else:
            return "No"


    def prGoodWith(self, v):
        """
        Returns 0 == Yes, 1 == No, 2 == Empty string
        """
        if v == 0: return "Yes"
        elif v == 1: return "No"
        else: return ""

    def run(self):
        
        self.log("PetRescuePublisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        if not self.checkMappedSpecies():
            self.setLastError("Not all species have been mapped.")
            self.cleanup()
            return
        if not self.checkMappedBreeds():
            self.setLastError("Not all breeds have been mapped.")
            self.cleanup()
            return
        accountid = configuration.petrescue_user(self.dbo)
        if accountid == "":
            self.setLastError("No petrescue.com.au account id has been set.")
            self.cleanup()
            return
        animals = self.getMatchingAnimals()
        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            self.cleanup()
            return

        if not self.openFTPSocket(): 
            self.setLastError("Failed opening FTP socket.")
            if self.logBuffer.find("530 Login") != -1:
                self.log("Found 530 Login incorrect: disabling PetRescue.com.au publisher.")
                configuration.publishers_enabled_disable(self.dbo, "pr")
            self.cleanup()
            return

        csv = []

        anCount = 0
        for an in animals:
            try:
                line = []
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    self.cleanup()
                    return

                # If a limit was set, stop now
                if self.pc.limit > 0 and anCount > self.pc.limit:
                    self.log("Hit publishing limit of %d animals. Stopping." % self.pc.limit)
                    break

                # Upload the image for this animal
                self.uploadImage(an, an["WEBSITEMEDIANAME"], str(an["ID"]) + ".jpg")
                # AccountID
                line.append("\"%s\"" % accountid)
                # RegionID
                regionid = "1"
                # If the option is on, look for a region id in the location name
                # and if one can't be found, fall back to ASM's internal location id
                if configuration.petrescue_location_regionid(self.dbo):
                    regionid = utils.atoi(an["SHELTERLOCATIONNAME"])
                    if regionid == 0:
                        regionid = an["SHELTERLOCATION"]
                line.append("\"%s\"" % regionid)
                # ID
                line.append("\"%d\"" % an["ID"])
                # Name
                line.append("\"%s\"" % an["ANIMALNAME"].replace("\"", "\"\""))
                # Type
                line.append("\"%s\"" % an["PETFINDERSPECIES"])
                # Breed
                line.append("\"%s\"" % self.getPublisherBreed(an, 1))
                # Breed2
                line.append("\"%s\"" % self.getPublisherBreed(an, 2))
                # Size
                line.append("\"%s\"" % an["SIZENAME"])
                # Description
                line.append("\"%s\"" % self.getDescription(an))
                # Sex
                line.append("\"%s\"" % an["SEXNAME"][0:1])
                # CoatLength (not implemented)
                line.append("\"\"")
                # Mixed
                line.append("\"%s\"" % self.prTrueFalse(an["CROSSBREED"] == 1))
                # GoodWKids
                line.append("\"%s\"" % self.prGoodWith(an["ISGOODWITHCHILDREN"]))
                # GoodWCats
                line.append("\"%s\"" % self.prGoodWith(an["ISGOODWITHCATS"]))
                # GoodWDogs
                line.append("\"%s\"" % self.prGoodWith(an["ISGOODWITHDOGS"]))
                # Housetrained
                line.append("\"%s\"" % an["ISHOUSETRAINED"] == 0 and "1" or "0")
                # Special needs
                if an["CRUELTYCASE"] == 1:
                    line.append("\"1\"")
                elif an["HASSPECIALNEEDS"] == 1:
                    line.append("\"1\"")
                else:
                    line.append("\"0\"")
                # SpayedNeutered
                line.append("\"%s\"" % self.prYesNo(an["NEUTERED"] == 1))
                # Declawed
                line.append("\"%s\"" % self.prTrueFalse(an["DECLAWED"] == 1))
                # DOB
                line.append("\"%s\"" % i18n.format_date("%d-%b-%y", an["DATEOFBIRTH"]))
                # colour
                line.append("\"\"")
                # secondaryColour
                line.append("\"\"")
                # weight
                line.append("\"\"")
                # lastUpdated
                line.append("\"%s\"" % i18n.format_date("%d-%b-%y", an["LASTCHANGEDDATE"]))
                # heartWormTest
                line.append("\"%s\"" % an["HEARTWORMTESTED"])
                # BasicTraining
                line.append("\"\"")
                # BreederRegistration
                line.append("\"\"")
                # AdoptionFee
                line.append("\"%s\"" % i18n.format_currency(self.dbo.locale, an["FEE"]))
                # Add to our CSV file
                csv.append(",".join(line))
                # Mark success in the log
                self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals)

        header = "AccountID,RegionID,ID,Name,type,Breed,Breed2,Size,Description,Sex,CoatLength,Mixed," \
            "GoodWKids,GoodWCats,GoodWDogs,Housetrained,SpecialNeeds,SpayedNeutered,Declawed," \
            "DOB,colour,secondaryColour,weight,LastUpdated,heartwormTest,BasicTraining," \
            "BreederRegistration,AdoptionFee\n"
        self.saveFile(os.path.join(self.publishDir, "pets.csv"), header + "\n".join(csv))
        self.log("Uploading datafile %s" % "pets.csv")
        self.upload("pets.csv")
        self.log("Uploaded %s" % "pets.csv")
        self.log("-- FILE DATA --")
        self.log(header + "\n".join(csv))
        self.cleanup()

class PetsLocatedUKPublisher(FTPPublisher):
    """
    Handles publishing to petslocated.com in the UK
    """
    def __init__(self, dbo, publishCriteria):
        l = dbo.locale
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        publishCriteria.checkSocket = True
        publishCriteria.includeColours = True
        publishCriteria.scaleImages = 1
        FTPPublisher.__init__(self, dbo, publishCriteria, 
            PETSLOCATED_FTP_HOST, PETSLOCATED_FTP_USER, PETSLOCATED_FTP_PASSWORD)
        self.publisherName = i18n._("PetsLocated UK Publisher", l)
        self.setLogName("petslocated")

    def plcAge(self, agegroup):
        if agegroup is None: return "Older"
        if agegroup == "Baby": return "Very Young"
        elif agegroup.startswith("Young"): return "Young"
        elif agegroup.find("Adult") != -1: return "Average"
        else:
            return "Older"

    def plcAgeYears(self, agegroup = "", dob = None):
        """
        Returns an age in years as a float/string from either an agegroup
        or a date of birth.
        """
        years = 1
        if dob is not None:
            td = i18n.now(self.dbo.timezone) - dob
            if type(td) == datetime.timedelta:
                years = td.days / 365.0
        else:
           years = configuration.age_group_for_name(self.dbo, agegroup) 
           if years == 0: years = 1
        return "%0.1f" % years

    def plcChipChecked(self, chipped):
        if chipped == 1:
            return 2
        return 3

    def plcNeutered(self, neutered):
        if type(neutered) == str:
            if neutered.find("payed") != -1 or neutered.find("eutered") != -1:
                return "y"
        elif type(neutered) == int:
            if neutered == 1:
                return "y"
            return "n"
        return "u"

    def plcPostcode(self, postcode1, postcode2 = "", postcode3 = ""):
        """ Returns the postcode prefix of the first non-blank value given """
        postcode = postcode1
        if postcode is None or postcode == "": postcode = postcode2
        if postcode is None or postcode == "": postcode = postcode3
        if postcode.find(" ") == -1: return postcode
        return postcode[0:postcode.find(" ")]

    def plcSex(self, sexID):
        if sexID == 0: return "f"
        if sexID == 1: return "m"
        return "u"

    def plcHairType(self, an):
        HAIRLESS = [ "Bird", "Reptile", "Fish", "Snake", "Hedgehog", "Tortoise", "Terrapin", 
            "Lizard", "Chicken", "Owl", "Cockatiel", "Goose", "Goldfish" ]
        # Dogs
        speciesname = an["SPECIESNAME"]
        if speciesname == "Dog":
            if an.has_key("COATTYPENAME") and an["COATTYPENAME"] == "Long": return "Long"
            elif an.has_key("COATTYPENAME") and an["COATTYPENAME"] == "Hairless": return "Not Applicable"
            else: return "Short"
        # Cats
        elif speciesname == "Cat":
            if an["BREEDNAME"].find("Short") != -1 or an["BREEDNAME"].find("DSH") != -1: return "Short"
            elif an["BREEDNAME"].find("Medium") != -1 or an["BREEDNAME"].find("DMH") != -1: return "Medium"
            elif an["BREEDNAME"].find("Long") != -1 or an["BREEDNAME"].find("DLH") != -1: return "Long"
            else: return "Short"
        # Species that don't have hair
        elif speciesname in HAIRLESS: return "Not Applicable"
        else:
            return "Short"

    def plcColour(self, s):
        colourmap = {
            "Black": "Mainly/All Black",
            "Black - with Tan, Yellow or Fawn": "Mainly/All Black",
            "Black - with White": "Black and White",
            "Brindle": "Brindle",
            "Brindle - with White": "Brindle",
            "Brown/Chocolate": "Brown/Chocolate",
            "Brown/Chocolate - with Black": "Brown/Chocolate",
            "Brown/Chocolate - with White": "Brown/Chocolate",
            "Red/Golden/Orange/Chestnut": "Golden/Sandy/Apricot",
            "Red/Golden/Orange/Chestnut - with Black": "Golden/Sandy/Apricot",
            "Red/Golden/Orange/Chestnut - with White": "Golden/Sandy/Apricot",
            "Silver & Tan (Yorkie colors)": "Tri-colour",
            "Tan/Yellow/Fawn": "Golden/Sandy/Apricot",
            "Tan/Yellow/Fawn - with White": "Golden/Sandy/Apricot",
            "Tricolor (Tan/Brown & Black & White)": "Tri-colour",
            "White": "White",
            "White - with Black": "Mainly/All White",
            "White - with Brown or Chocolate": "Mainly/All White",
            "Black - with Brown, Red, Golden, Orange or Chestnut": "Mainly/All Black",
            "Black - with Gray or Silver": "Mainly/All Black",
            "Brown/Chocolate - with Tan": "Brown/Tan",
            "Gray/Blue/Silver/Salt & Pepper": "Grey/Silver/Blue",
            "Gray/Silver/Salt & Pepper - with White": "Grey/Silver/Blue",
            "Gray/Silver/Salt & Pepper - with Black": "Grey/Silver/Blue",
            "Merle": "Mainly/All White",
            "Tan/Yellow/Fawn - with Black": "Brown/Tan",
            "White - with Tan, Yellow or Fawn": "Mainly/All White",
            "White - with Red, Golden, Orange or Chestnut": "Mainly/All White",
            "White - with Gray or Silver": "Mainly/All White",
            "Black (All)": "Mainly/All Black",
            "Cream or Ivory": "Beige/Cream",
            "Cream or Ivory (Mostly)": "Beige/Cream",
            "Spotted Tabby/Leopard Spotted": "Spotted",
            "Black (Mostly)": "Mainly/All Black",
            "Black & White or Tuxedo": "Black and White",
            "Brown or Chocolate": "Brown/Chocolate",
            "Brown or Chocolate (Mostly)": "Brown/Chocolate",
            "Brown Tabby": "Tabby",
            "Calico or Dilute Calico": "Calico",
            "Gray or Blue ": "Blue",
            "Gray or Blue (Mostly)": "Blue",
            "Gray, Blue or Silver Tabby": "Tabby",
            "Orange or Red": "Ginger/Orange",
            "Orange or Red (Mostly)": "Ginger/Orange",
            "Orange or Red Tabby": "Ginger/Orange",
            "Tan or Fawn ": "Beige/Cream",
            "Tan or Fawn (Mostly)": "Beige/Cream",
            "Tan or Fawn Tabby": "Tabby",
            "Tiger Striped": "Tabby",
            "Tortoiseshell": "Tortoiseshell",
            "White": "White",
            "White (Mostly)": "Mainly/All White",
            "Palomino": "White",
            "Gray": "White",
            "Dun": "White",
            "Cremello": "White",
            "Chestnut/Sorrel": "Brown",
            "Champagne": "White",
            "Buckskin": "Brown",
            "Black": "Black",
            "Bay": "Brown",
            "Appy": "Brown",
            "Grullo": "Brown",
            "White": "White",
            "Roan": "White",
            "Perlino": "White",
            "Paint": "White",
            "Gray": "Grey/Silver",
            "Green": "Green",
            "Olive": "Green",
            "Orange": "Red",
            "Pink": "Pink",
            "Purple/Violet": "Pink",
            "Red": "Red",
            "Rust": "Red",
            "Tan": "Brown",
            "Buff": "Brown",
            "Yellow": "Gold/Yellow",
            "White": "White",
            "Black": "Black",
            "Blue": "Blue",
            "Brown": "Brown",
            "Sable": "White",
            "Albino or Red-Eyed White": "White",
            "Blue": "Grey/Silver",
            "Black": "Black",
            "Blond/Golden": "Gold",
            "Chinchilla": "Brown",
            "Chocolate": "Brown",
            "Cinnamon": "Brown",
            "Copper": "Brown",
            "Cream": "White",
            "Dutch": "White",
            "Fawn": "Brown",
            "Grey/Silver": "Grey/Seilver",
            "Harlequin": "White",
            "Lilac": "Grey/Silver",
            "Multi": "Multi-Coloured",
            "Orange": "Ginger",
            "Red": "Ginger",
            "Agouti": "Ginger",
            "Siamese": "Black",
            "Tan": "Brown",
            "Tortoise": "Multi-Coloured",
            "Tri-color": "Multi-Coloured",
            "White": "White",
            "Yellow": "Gold",
            "White": "White",
            "Tortoiseshell": "Multi-Coloured",
            "Tan or Beige": "Brown",
            "Silver or Gray": "Grey/Silver",
            "Sable": "White",
            "Red": "Ginger", 
            "Orange": "Ginger",
            "Multi": "Multi-Coloured",
            "Lilac": "White",
            "Golden": "Gold",
            "Cream": "White",
            "Calico": "Multi-Coloured",
            "Buff": "White",
            "Brown or Chocolate": "Black",
            "Blonde": "Gold",
            "Black": "Black",
            "Albino or Red-Eyed White": "White"
        }
        if colourmap.has_key(s): return colourmap[s]
        return "Black"

    def plcSpecies(self, s, ps):
        speciesmap = {
            "Barnyard": "Goat", 
            "Bird": "Bird", 
            "Cat": "Cat",
            "Chinchilla": "Chinchilla",
            "Degu": "Degu",
            "Dog": "Dog",
            "Ferret": "Ferret",
            "Goat": "Goat",
            "Guinea Pig": "Guinea Pig",
            "Hamster": "Hamster",
            "Horse": "Horse", 
            "Pig": "Pig",
            "Rabbit": "Rabbit",
            "Reptile": "Snake/Reptile",
            "Snake": "Snake/Reptile",
            "Spider": "Spider",
            "Terrapin": "Tortoise/Terrapin/Turtle",
            "Tortoise": "Tortoise/Terrapin/Turtle",
            "Turtle": "Tortoise/Terrapin/Turtle",
            "Small&Furry": "Mouse/Rat"
        }
        if speciesmap.has_key(s): return speciesmap[s]
        if speciesmap.has_key(ps): return speciesmap[ps]
        return "Cat"

    def run(self):
        
        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        customerid = configuration.petslocated_customerid(self.dbo)
        if customerid == "":
            self.setLastError("No petslocated.com customer ID has been set.")
            return

        if not self.checkMappedSpecies():
            self.setLastError("Not all species have been mapped.")
            self.cleanup()
            return
        if not self.checkMappedBreeds():
            self.setLastError("Not all breeds have been mapped.")
            self.cleanup()
            return
        if self.pc.includeColours and not self.checkMappedColours():
            self.setLastError("Not all colours have been mapped and sending colours is enabled")
            self.cleanup()
            return

        includelost = False # Don't publish lost animals - losers pay 12 pounds to post for 12 months
        includeshelter = configuration.petslocated_includeshelter(self.dbo)
        shelterwithflag = configuration.petslocated_animalflag(self.dbo)

        if shelterwithflag == "" and includeshelter:
            self.setLastError("Include shelter animals set, but no flag chosen")
            self.cleanup()
            return

        lostanimals = lostfound.get_lostanimal_find_advanced(self.dbo, {})
        foundanimals = lostfound.get_foundanimal_last_days(self.dbo, 90)
        animals = []

        if includeshelter:
            animals = db.query(self.dbo, animal.get_animal_query(self.dbo) + " WHERE a.Archived = 0 AND " \
                "a.AdditionalFlags LIKE '%%%s|%%'" % (shelterwithflag))

        if len(animals) == 0 and len(foundanimals) == 0 and len(lostanimals) == 0:
            self.setLastError("No animals found to publish.")
            self.cleanup()
            return

        if not self.openFTPSocket(): 
            self.setLastError("Failed opening FTP socket.")
            if self.logBuffer.find("530 Login") != -1:
                self.log("Found 530 Login incorrect: disabling PetsLocated UK publisher.")
                configuration.publishers_enabled_disable(self.dbo, "pcuk")
            self.cleanup()
            return

        csv = []
        header = "customerurn,importkey,lostfound,pettype,breed,sexofpet,neutered,petname,internalref,petage,hairtype,petcoloursall,chipchecked,chipno,petfeatures,lastlocationst,lastlocation,locationpostcode,datelostfound,otherdetails,privatenotes,showonsite,rawpettype,rawbreed,rawcolour,rawcoat,rawageyears\n"

        # Lost Animals
        if includelost:
            anCount = 0
            for an in lostanimals:
                try:
                    line = []
                    anCount += 1
                    self.log("Processing Lost Animal: %d: %s (%d of %d)" % ( an["ID"], an["COMMENTS"], anCount, len(foundanimals)))

                    # If the user cancelled, stop now
                    if self.shouldStopPublishing(): 
                        self.log("User cancelled publish. Stopping.")
                        self.resetPublisherProgress()
                        return

                    # customerurn
                    line.append("\"%s\"" % customerid)
                    # importkey
                    line.append("\"L%s\"" % an["ID"])
                    # lostfound
                    line.append("\"L\"")
                    # pettype
                    line.append("\"%s\"" % self.plcSpecies(an["SPECIESNAME"], an["SPECIESNAME"]))
                    # breed
                    line.append("\"%s\"" % an["BREEDNAME"])
                    # sexofpet
                    line.append("\"%s\"" % self.plcSex(an["SEX"]))
                    # neutered
                    line.append("\"%s\"" % (self.plcNeutered(an["DISTFEAT"])))
                    # petname
                    line.append("\"\"")
                    # internalref
                    line.append("\"L%s\"" % an["ID"])
                    # petage
                    line.append("\"%s\"" % self.plcAge(an["AGEGROUP"]))
                    # hairtype
                    line.append("\"%s\"" % self.plcHairType(an))
                    # petcoloursall
                    line.append("\"%s\"" % self.plcColour(an["ADOPTAPETCOLOUR"]))
                    # chipchecked
                    line.append("\"1\"")
                    # chipno
                    line.append("\"\"")
                    # petfeatures
                    line.append("\"%s\"" % an["DISTFEAT"])
                    # lastlocationst
                    line.append("\"\"")
                    # lastlocation
                    line.append("\"%s\"" % an["AREALOST"])
                    # locationpostcode
                    line.append("\"%s\"" % self.plcPostcode(an["AREAPOSTCODE"], an["OWNERPOSTCODE"]))
                    # datelostfound
                    line.append("\"%s\"" % i18n.python2display(self.locale, an["DATELOST"]))
                    # otherdetails
                    line.append("\"\"")
                    # privatenotes
                    line.append("\"%s\"" % an["COMMENTS"])
                    # showonsite
                    line.append("\"1\"")
                    # rawpettype
                    line.append("\"%s\"" % an["SPECIESNAME"])
                    # rawbreed
                    line.append("\"%s\"" % an["BREEDNAME"])
                    # rawcolour
                    line.append("\"%s\"" % an["BASECOLOURNAME"])
                    # rawcoat
                    line.append("\"\"")
                    # rawageyears
                    line.append("\"%s\"" % self.plcAgeYears(agegroup=an["AGEGROUP"]))
                    # Add to our CSV file
                    csv.append(",".join(line))
                    # Mark success in the log
                    self.logSuccess("Processed Lost Animal: %d: %s (%d of %d)" % ( an["ID"], an["COMMENTS"], anCount, len(foundanimals)))
                except Exception,err:
                    self.logError("Failed processing lost animal: %s, %s" % (str(an["ID"]), err), sys.exc_info())

        # Found Animals
        anCount = 0
        for an in foundanimals:
            try:
                line = []
                anCount += 1
                self.log("Processing Found Animal: %d: %s (%d of %d)" % ( an["ID"], an["COMMENTS"], anCount, len(foundanimals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    return

                # customerurn
                line.append("\"%s\"" % customerid)
                # importkey
                line.append("\"F%s\"" % an["ID"])
                # lostfound
                line.append("\"F\"")
                # pettype
                line.append("\"%s\"" % self.plcSpecies(an["SPECIESNAME"], an["SPECIESNAME"]))
                # breed
                line.append("\"%s\"" % an["BREEDNAME"])
                # sexofpet
                line.append("\"%s\"" % self.plcSex(an["SEX"]))
                # neutered
                line.append("\"%s\"" % (self.plcNeutered(an["DISTFEAT"])))
                # petname
                line.append("\"\"")
                # internalref
                line.append("\"F%s\"" % an["ID"])
                # petage
                line.append("\"%s\"" % self.plcAge(an["AGEGROUP"]))
                # hairtype
                line.append("\"%s\"" % self.plcHairType(an))
                # petcoloursall
                line.append("\"%s\"" % self.plcColour(an["ADOPTAPETCOLOUR"]))
                # chipchecked
                line.append("\"1\"")
                # chipno
                line.append("\"\"")
                # petfeatures
                line.append("\"%s\"" % an["DISTFEAT"])
                # lastlocationst
                line.append("\"\"")
                # lastlocation
                line.append("\"%s\"" % an["AREAFOUND"])
                # locationpostcode
                line.append("\"%s\"" % self.plcPostcode(an["AREAPOSTCODE"], an["OWNERPOSTCODE"]))
                # datelostfound
                line.append("\"%s\"" % i18n.python2display(self.locale, an["DATEFOUND"]))
                # otherdetails
                line.append("\"\"")
                # privatenotes
                line.append("\"%s\"" % an["COMMENTS"])
                # showonsite
                line.append("\"1\"")
                # rawpettype
                line.append("\"%s\"" % an["SPECIESNAME"])
                # rawbreed
                line.append("\"%s\"" % an["BREEDNAME"])
                # rawcolour
                line.append("\"%s\"" % an["BASECOLOURNAME"])
                # rawcoat
                line.append("\"\"")
                # rawageyears
                line.append("\"%s\"" % self.plcAgeYears(agegroup=an["AGEGROUP"]))
                # Add to our CSV file
                csv.append(",".join(line))
                # Mark success in the log
                self.logSuccess("Processed Found Animal: %d: %s (%d of %d)" % ( an["ID"], an["COMMENTS"], anCount, len(foundanimals)))
            except Exception,err:
                self.logError("Failed processing found animal: %s, %s" % (str(an["ID"]), err), sys.exc_info())

        # Shelter animals
        if includeshelter:
            anCount = 0
            for an in animals:
                try:
                    line = []
                    anCount += 1
                    self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                    self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                    # If the user cancelled, stop now
                    if self.shouldStopPublishing(): 
                        self.log("User cancelled publish. Stopping.")
                        self.resetPublisherProgress()
                        return

                    # Upload one image for this animal
                    # self.uploadImage(an, an["WEBSITEMEDIANAME"], an["SHELTERCODE"] + ".jpg")

                    # customerurn
                    line.append("\"%s\"" % customerid)
                    # importkey
                    line.append("\"A%s\"" % an["ID"])
                    # lostfound
                    line.append("\"F\"")
                    # pettype
                    line.append("\"%s\"" % self.plcSpecies(an["SPECIESNAME"], an["PETFINDERSPECIES"]))
                    # breed
                    line.append("\"%s\"" % an["BREEDNAME"])
                    # sexofpet
                    line.append("\"%s\"" % self.plcSex(an["SEX"]))
                    # neutered
                    line.append("\"%s\"" % self.plcNeutered(an["NEUTERED"]))
                    # petname
                    line.append("\"%s\"" % an["ANIMALNAME"])
                    # internalref
                    line.append("\"A%s\"" % an["ID"])
                    # petage
                    line.append("\"%s\"" % self.plcAge(an["AGEGROUP"]))
                    # hairtype
                    line.append("\"%s\"" % self.plcHairType(an))
                    # petcoloursall
                    line.append("\"%s\"" % self.plcColour(an["ADOPTAPETCOLOUR"]))
                    # chipchecked
                    line.append("\"%d\"" % self.plcChipChecked(an["IDENTICHIPPED"]))
                    # chipno
                    line.append("\"%s\"" % an["IDENTICHIPNUMBER"])
                    # petfeatures
                    line.append("\"%s\"" % an["MARKINGS"])
                    # lastlocationst
                    line.append("\"\"")
                    # lastlocation
                    line.append("\"\"")
                    # locationpostcode
                    line.append("\"%s\"" % self.plcPostcode(an["ORIGINALOWNERPOSTCODE"]))
                    # datelostfound
                    line.append("\"%s\"" % i18n.python2display(self.locale, an["DATEBROUGHTIN"]))
                    # otherdetails
                    line.append("\"%s\"" % an["ANIMALCOMMENTS"])
                    # privatenotes
                    line.append("\"%s\"" % an["HIDDENANIMALDETAILS"])
                    # showonsite
                    line.append("\"1\"")
                    # rawpettype
                    line.append("\"%s\"" % an["SPECIESNAME"])
                    # rawbreed
                    line.append("\"%s\"" % an["BREEDNAME"])
                    # rawcolour
                    line.append("\"%s\"" % an["BASECOLOURNAME"])
                    # rawcoat
                    line.append("\"%s\"" % an["COATTYPENAME"])
                    # rawageyears
                    line.append("\"%s\"" % self.plcAgeYears(dob=an["DATEOFBIRTH"]))
                    # Add to our CSV file
                    csv.append(",".join(line))
                    # Mark success in the log
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                except Exception,err:
                    self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

            # Mark published
            self.markAnimalsPublished(animals)

        filename = "%s_%s.csv" % (customerid, self.dbo.database)
        self.saveFile(os.path.join(self.publishDir, filename), header + "\n".join(csv))
        self.log("Uploading datafile %s" % filename)
        self.upload(filename)
        self.log("Uploaded %s" % filename)
        self.log("-- FILE DATA --")
        self.log(header + "\n".join(csv))
        # Clean up
        self.closeFTPSocket()
        self.deletePublishDirectory()
        self.saveLog()
        self.setPublisherComplete()

class PETtracUKPublisher(AbstractPublisher):
    """
    Handles updating animal microchips with AVID PETtrac UK
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.publisherName = "PETtrac UK Publisher"
        self.setLogName("pettracuk")

    def reregistrationPDF(self, fields, sig, realname, orgname, orgaddress, orgtown, orgcounty, orgpostcode):
        """
        Generates a reregistration PDF document containing the authorised user's
        electronic signature.
        """
        gender = fields["petgender"]
        if gender == "M": gender = "Male"
        elif gender == "F": gender = "Female"
        h = "<p align=\"right\"><b>%s</b><br />%s<br />%s, %s<br />%s</p>" % (orgname, orgaddress, orgtown, orgcounty, orgpostcode)
        h += "<h2>Change of Registered Owner/Keeper</h2>"
        h += "<table border=\"1\">"
        h += "<tr><td>Chip:</td><td><b>%s</b></td></tr>" % fields["microchip"]
        h += "<tr><td>Implanted:</td><td>%s</td></tr>" % fields["implantdate"]
        h += "<tr><td>Animal:</td><td>%s</td></tr>" % fields["petname"]
        h += "<tr><td>DOB:</td><td>%s</td></tr>" % fields["petdob"]
        h += "<tr><td>Type:</td><td>%s %s %s</td></tr>" % (gender, fields["petbreed"], fields["petspecies"])
        h += "<tr><td>Colour:</td><td>%s</td></tr>" % fields["petcolour"]
        h += "<tr><td>Neutered:</td><td>%s</td></tr>" % fields["petneutered"]
        h += "<tr><td>New Owner:</td><td>%s %s %s</td></tr>" % (fields["prefix"], fields["firstname"], fields["surname"])
        h += "<tr><td>Address:</td><td>%s<br/>%s<br/>%s %s</td></tr>" % (fields["address1"], fields["city"], fields["county"], fields["postcode"])
        h += "<tr><td>Telephone:</td><td>H: %s<br/>W: %s<br/>M: %s</td></tr>" % (fields["telhome"], fields["telwork"], fields["telmobile"])
        h += "<tr><td>Email:</td><td>%s</td></tr>" % fields["email"]
        h += "</table>"
        h += "<p>I/We confirm that every effort has been made to reunite the animal with its owner/keeper, or that the previous " \
            "owner has relinquished ownership/keepership.</p>\n"
        h += "<p>If the animal was a stray then the animal has been in our care for the minimum required time period before " \
            "rehoming took place.</p>\n"
        h += "<p>Authorised Signature: <br /><img src=\"%s\" /><br />%s</p>\n" % (sig, realname)
        h += "<p>Date: %s</p>\n" % i18n.python2display(self.dbo.locale, i18n.now(self.dbo.timezone))
        h += "<p>Authorisation: I understand that the information I have given on this form will be retained by PETtrac and " \
            "hereby agree that it may be disclosed to any person or persons who may be involved in securing the welfare of the " \
            "pet above. PETtrac reserves the right to amend any microchip record in the event that we are subsequently " \
            "provided with additional information.</p>\n"
        return utils.html_to_pdf(h)

    def run(self):
        
        self.log("PETtrac UK Publisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        orgpostcode = configuration.avid_org_postcode(self.dbo)
        orgname = configuration.avid_org_name(self.dbo)
        orgserial = configuration.avid_org_serial(self.dbo)
        orgpassword = configuration.avid_org_password(self.dbo)
        avidrereg = configuration.avid_reregistration(self.dbo)

        orgaddress = configuration.organisation_address(self.dbo)
        orgtown = configuration.organisation_town(self.dbo)
        orgcounty = configuration.organisation_county(self.dbo)

        if orgpostcode == "" or orgname == "" or orgserial == "" or orgpassword == "":
            self.setLastError("orgpostcode, orgname, orgserial and orgpassword all need to be set for AVID publisher")
            return

        authuser = configuration.avid_auth_user(self.dbo)
        user = users.get_users(self.dbo, authuser)
        if avidrereg and len(user) == 0:
            self.setLastError("no authorised user is set, cannot re-register chips")
            return

        if avidrereg and utils.nulltostr(user[0]["SIGNATURE"]) == "":
            self.setLastError("authorised user '%s' does not have an electronic signature on file" % authuser)
            return

        animals = get_microchip_data(self.dbo, ['977%',], "pettracuk", allowintake = False)
        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            return

        anCount = 0
        processed_animals = []
        for an in animals:
            try:
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    return

                # Validate certain items aren't blank so we aren't registering bogus data
                if utils.nulltostr(an["CURRENTOWNERADDRESS"].strip()) == "":
                    self.logError("Address for the new owner is blank, cannot process")
                    continue 

                if utils.nulltostr(an["CURRENTOWNERPOSTCODE"].strip()) == "":
                    self.logError("Postal code for the new owner is blank, cannot process")
                    continue

                # Make sure the length is actually suitable
                if not len(an["IDENTICHIPNUMBER"]) in (9, 10, 15):
                    self.logError("Microchip length is not 9, 10 or 15, cannot process")
                    continue

                # Sort out breed
                breed = an["BREEDNAME"]
                if breed.find("Domestic Long") != -1: breed = "DLH"
                if breed.find("Domestic Short") != -1: breed = "DSH"
                if breed.find("Domestic Medium") != -1: breed = "DSLH"

                # Sort out species
                species = an["SPECIESNAME"]
                if species.find("Dog") != -1: species = "Canine"
                elif species.find("Cat") != -1: species = "Feline"
                elif species.find("Bird") != -1: species = "Avian"
                elif species.find("Horse") != -1: species = "Equine"
                elif species.find("Reptile") != -1: species = "Reptilian"
                else: species = "Other"

                # Build the animal POST data
                fields = {
                    "orgpostcode": orgpostcode,
                    "orgname": orgname, 
                    "orgserial": orgserial,
                    "orgpassword": orgpassword,
                    "version": "1.1",
                    "microchip": an["IDENTICHIPNUMBER"],
                    "implantdate": i18n.format_date("%Y%m%d", an["IDENTICHIPDATE"]),
                    "prefix": an["CURRENTOWNERTITLE"],
                    "surname": an["CURRENTOWNERSURNAME"],
                    "firstname": an["CURRENTOWNERFORENAMES"],
                    "address1": an["CURRENTOWNERADDRESS"],
                    "city": an["CURRENTOWNERTOWN"],
                    "county": an["CURRENTOWNERCOUNTY"],
                    "postcode": an["CURRENTOWNERPOSTCODE"],
                    "telhome": an["CURRENTOWNERHOMETELEPHONE"],
                    "telwork": an["CURRENTOWNERWORKTELEPHONE"],
                    "telmobile": an["CURRENTOWNERMOBILETELEPHONE"],
                    "telalternative": "",
                    "email": an["CURRENTOWNEREMAILADDRESS"],
                    "petname": an["ANIMALNAME"],
                    "petgender": an["SEXNAME"][0:1],
                    "petdob": i18n.format_date("%Y%m%d", an["DATEOFBIRTH"]),
                    "petspecies": species,
                    "petbreed": breed,
                    "petneutered": an["NEUTERED"] == 1 and "true" or "false",
                    "petcolour": an["BASECOLOURNAME"],
                    "selfreg": "true", # register the shelter as alternative contact
                    "test": "false" # if true, tells avid not to make any data changes
                }

                self.log("HTTP POST request %s: %s" % (PETTRAC_UK_POST_URL, str(fields)))
                r = utils.post_form(PETTRAC_UK_POST_URL, fields)
                self.log("HTTP response: %s" % r["response"])

                # Return value is an XML fragment, look for "Registration completed successfully"
                if r["response"].find("successfully") != -1:
                    self.log("successful response, marking processed")
                    processed_animals.append(an)
                    # Mark success in the log
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))

                # If AVID tell us the microchip is already registered, attempt to re-register
                elif r["response"].find("already registered") != -1:
                    if avidrereg:
                        self.log("microchip already registered response, re-registering")

                        pdfname = "%s-%s-%s.pdf" % (i18n.format_date("%Y%m%d", i18n.now(self.dbo.timezone)), orgserial, an["IDENTICHIPNUMBER"])
                        fields["filenameupload"] = pdfname
                        pdf = self.reregistrationPDF(fields, user[0]["SIGNATURE"], user[0]["REALNAME"], orgname, orgaddress, orgtown, orgcounty, orgpostcode)
                        self.log("generated re-registration PDF %s (%d bytes)" % (pdfname, len(pdf)))

                        reregurl = PETTRAC_UK_POST_URL.replace("onlineregistration", "onlinereregistration")
                        self.log("HTTP multipart POST request %s: %s" % (reregurl, str(fields)))
                        r = utils.post_multipart(reregurl, fields, { pdfname: (pdfname, pdf, "application/pdf" )} )
                        self.log("HTTP response: %s" % r["response"])

                        if r["response"].find("successfully") != -1:
                            self.log("successful re-registration response, marking processed")
                            processed_animals.append(an)
                            # Mark success in the log
                            self.logSuccess("Processed: %s: %s (%d of %d) (rereg)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                        else:
                            self.logError("Problem with data encountered, not marking processed")
                    else:
                        self.logError("re-registration support is disabled, marking processed for compatibility")
                        processed_animals.append(an)
                # There's a problem with the data we sent, flag it
                else:
                    self.logError("Problem with data encountered, not marking processed")

            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        if len(processed_animals) > 0:
            self.log("successfully processed %d animals, marking sent" % len(processed_animals))
            self.markAnimalsPublished(processed_animals)

        self.saveLog()
        self.setPublisherComplete()

class RescueGroupsPublisher(FTPPublisher):
    """
    Handles publishing to PetAdoptionPortal.com/RescueGroups.org
    Note: RG only accept Active FTP connections
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        publishCriteria.checkSocket = True
        publishCriteria.uploadAllImages = True
        publishCriteria.forceReupload = False
        publishCriteria.scaleImages = 1
        FTPPublisher.__init__(self, dbo, publishCriteria, 
            RESCUEGROUPS_FTP_HOST, configuration.rescuegroups_user(dbo), 
            configuration.rescuegroups_password(dbo), 21, "", False)
        self.publisherName = "RescueGroups Publisher"
        self.setLogName("rescuegroups")

    def rgYesNo(self, condition):
        """
        Returns a CSV entry for yes or no based on the condition
        """
        if condition:
            return "Yes"
        else:
            return "No"

    def rgYesNoBlank(self, v):
        """
        Returns 0 == Yes, 1 == No, 2 == Empty string
        """
        if v == 0: return "Yes"
        elif v == 1: return "No"
        else: return ""

    def run(self):
        
        self.log("RescueGroupsPublisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        if not self.checkMappedSpecies():
            self.setLastError("Not all species have been mapped.")
            self.cleanup()
            return
        if not self.checkMappedBreeds():
            self.setLastError("Not all breeds have been mapped.")
            self.cleanup()
            return
        shelterid = configuration.rescuegroups_user(self.dbo)
        if shelterid == "":
            self.setLastError("No RescueGroups.org shelter id has been set.")
            self.cleanup()
            return
        animals = self.getMatchingAnimals()
        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            self.cleanup()
            return

        if not self.openFTPSocket(): 
            self.setLastError("Failed opening FTP socket.")
            if self.logBuffer.find("530 Login") != -1:
                self.log("Found 530 Login incorrect: disabling RescueGroups publisher.")
                configuration.publishers_enabled_disable(self.dbo, "rg")
            self.cleanup()
            return

        # Do the images first
        self.mkdir("import")
        self.chdir("import")
        self.mkdir("pictures")
        self.chdir("pictures", "import/pictures")

        csv = []

        anCount = 0
        for an in animals:
            try:
                line = []
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    self.cleanup()
                    return

                # If a limit was set, stop now
                if self.pc.limit > 0 and anCount > self.pc.limit:
                    self.log("Hit publishing limit of %d animals. Stopping." % self.pc.limit)
                    break

                # Upload images for this animal
                totalimages = self.uploadImages(an, False, 4)
                # orgID
                line.append("\"%s\"" % shelterid)
                # ID
                line.append("\"%s\"" % str(an["ID"]))
                # Status
                line.append("\"Available\"")
                # Last updated (Unix timestamp)
                line.append("\"%s\"" % str(time.mktime(an["LASTCHANGEDDATE"].timetuple())))
                # rescue ID (ID of animal at the rescue)
                line.append("\"%s\"" % an["SHELTERCODE"])
                # Name
                line.append("\"%s\"" % an["ANIMALNAME"].replace("\"", "\"\""))
                # Summary (no idea what this is for)
                line.append("\"\"")
                # Species
                line.append("\"%s\"" % an["PETFINDERSPECIES"])
                # Readable breed
                line.append("\"%s\"" % an["BREEDNAME"])
                # Primary breed
                line.append("\"%s\"" % an["PETFINDERBREED"])
                # Secondary breed
                line.append("\"%s\"" % self.getPublisherBreed(an, 2))
                # Sex
                line.append("\"%s\"" % an["SEXNAME"])
                # Mixed
                line.append("\"%s\"" % self.rgYesNo(an["CROSSBREED"] == 1))
                # dogs (good with)
                line.append("\"%s\"" % self.rgYesNoBlank(an["ISGOODWITHDOGS"]))
                # cats (good with)
                line.append("\"%s\"" % self.rgYesNoBlank(an["ISGOODWITHCATS"]))
                # kids (good with)
                line.append("\"%s\"" % self.rgYesNoBlank(an["ISGOODWITHCHILDREN"]))
                # declawed
                line.append("\"%s\"" % self.rgYesNo(an["DECLAWED"] == 1))
                # housetrained
                line.append("\"%s\"" % self.rgYesNoBlank(an["ISHOUSETRAINED"]))
                # Age, one of Adult, Baby, Senior and Young
                ageinyears = i18n.date_diff_days(an["DATEOFBIRTH"], i18n.now(self.dbo.timezone))
                ageinyears /= 365.0
                agename = "Adult"
                if ageinyears < 0.5: agename = "Baby"
                elif ageinyears < 2: agename = "Young"
                elif ageinyears < 9: agename = "Adult"
                else: agename = "Senior"
                line.append("\"%s\"" % agename)
                # Special needs
                if an["CRUELTYCASE"] == 1:
                    line.append("\"1\"")
                elif an["HASSPECIALNEEDS"] == 1:
                    line.append("\"1\"")
                else:
                    line.append("\"\"")
                # Altered
                line.append("\"%s\"" % self.rgYesNo(an["NEUTERED"] == 1))
                # Size, one of S, M, L, XL
                ansize = "M"
                if an["SIZE"] == 0: ansize = "XL"
                elif an["SIZE"] == 1: ansize = "L"
                elif an["SIZE"] == 2: ansize = "M"
                elif an["SIZE"] == 3: ansize = "S"
                line.append("\"%s\"" % ansize)
                # uptodate (Has shots)
                line.append("\"%s\"" % self.rgYesNo(medical.get_vaccinated(self.dbo, int(an["ID"]))))
                # colour
                line.append("\"%s\"" % an["BASECOLOURNAME"])
                # coatLength (not implemented)
                line.append("\"\"")
                # pattern (not implemented)
                line.append("\"\"")
                # courtesy
                if an["ISCOURTESY"] == 1:
                    line.append("\"Yes\"")
                else:
                    line.append("\"\"")
                # Description
                line.append("\"%s\"" % self.getDescription(an, crToBr=True))
                # pic1-pic4
                if totalimages > 0:
                    # UploadAll isn't on, there was just one image with sheltercode == name
                    if not self.pc.uploadAllImages:
                        line.append("\"%s.jpg\",\"\",\"\",\"\"" % an["SHELTERCODE"])
                    else:
                        # Output an entry for each image we uploaded,
                        # upto a maximum of 4
                        for i in range(1, 5):
                            if totalimages >= i:
                                line.append("\"%s-%d.jpg\"" % (an["SHELTERCODE"], i))
                            else:
                                line.append("\"\"")
                else:
                    line.append("\"\",\"\",\"\",\"\"")
                # Add to our CSV file
                csv.append(",".join(line))
                # Mark success in the log
                self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals)

        header = "orgID, animalID, status, lastUpdated, rescueID, name, summary, species, breed, " \
            "primaryBreed, secondaryBreed, sex, mixed, dogs, cats, kids, declawed, housetrained, age, " \
            "specialNeeds, altered, size, uptodate, color, coatLength, pattern, courtesy, description, pic1, " \
            "pic2, pic3, pic4\n"
        self.saveFile(os.path.join(self.publishDir, "pets.csv"), header + "\n".join(csv))
        self.log("Uploading datafile %s" % "pets.csv")
        self.chdir("..", "import")
        self.upload("pets.csv")
        self.log("Uploaded %s" % "pets.csv")
        self.log("-- FILE DATA --")
        self.log(header + "\n".join(csv))
        self.cleanup()

class SmartTagPublisher(FTPPublisher):
    """
    Handles publishing to SmartTag PETID
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        FTPPublisher.__init__(self, dbo, publishCriteria, 
            SMARTTAG_FTP_HOST, SMARTTAG_FTP_USER, SMARTTAG_FTP_PASSWORD)
        self.publisherName = "SmartTag Publisher"
        self.setLogName("smarttag")

    def stYesNo(self, condition):
        """
        Returns a CSV entry for yes or no based on the condition
        """
        if condition:
            return "\"Y\""
        else:
            return "\"N\""

    def run(self):
        
        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        shelterid = configuration.smarttag_accountid(self.dbo)
        if shelterid == "":
            self.setLastError("No SmartTag Account id has been set.")
            self.cleanup()
            return

        animals = get_microchip_data(self.dbo, ["a.SmartTag = 1 AND a.SmartTagNumber <> ''", '90007400'], "smarttag")
        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            self.cleanup()
            return

        if not self.openFTPSocket(): 
            self.setLastError("Failed to open FTP socket.")
            if self.logBuffer.find("530 Login") != -1:
                self.log("Found 530 Login incorrect: disabling SmartTag publisher.")
                configuration.publishers_enabled_disable(self.dbo, "st")
            self.cleanup()
            return

        # SmartTag want data files called shelterid_mmddyyyy_HHMMSS.csv in a folder
        # called shelterid_mmddyyyy_HHMMSS
        dateportion = i18n.format_date("%m%d%Y_%H%M%S", i18n.now(self.dbo.timezone))
        folder = "%s_%s" % (shelterid, dateportion)
        outputfile = "%s_%s.csv" % (shelterid, dateportion)
        self.mkdir(folder)
        self.chdir(folder)

        csv = []

        anCount = 0
        for an in animals:
            try:
                line = []
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    self.cleanup()
                    return

                # Upload one image for this animal with the name shelterid_animalid-1.jpg
                self.uploadImage(an, an["WEBSITEMEDIANAME"], "%s_%d-1.jpg" % (shelterid, an["ID"]))
                # accountid
                line.append("\"%s\"" % shelterid)
                # sourcesystem
                line.append("\"ASM\"")
                # sourcesystemanimalkey (corresponds to image name)
                line.append("\"%d\"" % an["ID"])
                # sourcesystemownerkey
                line.append("\"%s\"" % str(an["CURRENTOWNERID"]))
                # signupidassigned, signuptype
                if an["IDENTICHIPNUMBER"].startswith("90007400"):
                    # if we have a smarttag microchip number, use that instead of the tag
                    # since it's unlikely someone will want both
                    line.append("\"%s\"" % an["IDENTICHIPNUMBER"])
                    line.append("\"IDTAG-LIFETIME\"")
                else:
                    line.append("\"%s\"" % an["SMARTTAGNUMBER"])
                    sttype = "IDTAG-ANNUAL"
                    if an["SMARTTAGTYPE"] == 1: sttype = "IDTAG-5 YEAR"
                    if an["SMARTTAGTYPE"] == 2: sttype = "IDTAG-LIFETIME"
                    line.append("\"%s\"" % sttype)
                # signupeffectivedate
                line.append("\"" + i18n.python2display(self.locale, an["SMARTTAGDATE"]) + "\"")
                # signupbatchpostdt - only used by resending mechanism and we don't do that
                line.append("\"\"")
                # feecharged
                line.append("\"\"")
                # feecollected
                line.append("\"\"")
                # owner related stuff
                address = an["CURRENTOWNERADDRESS"]
                houseno = utils.address_house_number(address)
                streetname = utils.address_street_name(address)
                # ownerfname
                line.append("\"%s\"" % an["CURRENTOWNERFORENAMES"])
                # ownermname
                line.append("\"\"")
                #ownerlname
                line.append("\"%s\"" % an["CURRENTOWNERSURNAME"])
                # addressstreetnumber
                line.append("\"%s\"" % houseno)
                # addressstreetdir
                line.append("\"\"")
                # addressstreetname
                line.append("\"%s\"" % streetname)
                # addressstreettype
                line.append("\"\"")
                # addresscity
                line.append("\"%s\"" % an["CURRENTOWNERTOWN"])
                # addressstate
                line.append("\"%s\"" % an["CURRENTOWNERCOUNTY"])
                # addresspostal
                line.append("\"%s\"" % an["CURRENTOWNERPOSTCODE"])
                # addressctry
                line.append("\"USA\"")
                # owneremail
                line.append("\"%s\"" % an["CURRENTOWNEREMAILADDRESS"])
                # owneremail2
                line.append("\"\"")
                # owneremail3
                line.append("\"\"")
                # ownerhomephone
                line.append("\"%s\"" % an["CURRENTOWNERHOMETELEPHONE"])
                # ownerworkphone
                line.append("\"%s\"" % an["CURRENTOWNERWORKTELEPHONE"])
                # ownerthirdphone
                line.append("\"%s\"" % an["CURRENTOWNERMOBILETELEPHONE"])
                # petname
                line.append("\"%s\"" % an["ANIMALNAME"].replace("\"", "\"\""))
                # species
                line.append("\"%s\"" % an["SPECIESNAME"])
                # primarybreed
                line.append("\"%s\"" % an["BREEDNAME1"])
                # crossbreed (second breed)
                if an["CROSSBREED"] == 1:
                    line.append("\"%s\"" % an["BREEDNAME2"])
                else:
                    line.append("\"\"")
                # purebred
                line.append("\"%s\"" % self.stYesNo(an["CROSSBREED"] == 0))
                # gender
                line.append("\"%s\"" % an["SEXNAME"])
                # sterilized
                line.append("\"%s\"" % self.stYesNo(an["NEUTERED"] == 1))
                # primarycolor
                line.append("\"%s\"" % an["BASECOLOURNAME"])
                # secondcolor
                line.append("\"\"")
                # sizecategory
                line.append("\"%s\"" % an["SIZENAME"])
                # agecategory
                line.append("\"%s\"" % an["AGEGROUP"])
                # declawed
                line.append("\"%s\"" % self.stYesNo(an["DECLAWED"] == 1))
                # animalstatus (blank or D for Deceased)
                if an["DECEASEDDATE"] is not None:
                    line.append("\"D\"")
                else:
                    line.append("\"\"")
                # Add to our CSV file
                csv.append(",".join(line))
                # Mark success in the log
                self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals)

        header = "accountid,sourcesystem,sourcesystemanimalkey," \
            "sourcesystemownerkey,signupidassigned,signuptype,signupeffectivedate," \
            "signupbatchpostdt,feecharged,feecollected,ownerfname,ownermname," \
            "ownerlname,addressstreetnumber,addressstreetdir,addressstreetname," \
            "addressstreettype,addresscity,addressstate,addresspostal,addressctry," \
            "owneremail,owneremail2,owneremail3,ownerhomephone,ownerworkphone," \
            "ownerthirdphone,petname,species,primarybreed,crossbreed,purebred,gender," \
            "sterilized,primarycolor,secondcolor,sizecategory,agecategory,declawed," \
            "animalstatus\n" 
        self.saveFile(os.path.join(self.publishDir, outputfile), header + "\n".join(csv))
        self.log("Uploading datafile %s" % outputfile)
        self.upload(outputfile)
        self.log("Uploaded %s" % outputfile)
        self.log("-- FILE DATA --")
        self.log(header + "\n".join(csv))
        self.cleanup()

class VetEnvoyUSMicrochipPublisher(AbstractPublisher):
    """
    Handles updating animal microchips via recipients of
    the VetEnvoy system in the US
    """
    def __init__(self, dbo, publishCriteria, publisherName, publisherKey, recipientId, microchipPatterns):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.publisherName = publisherName
        self.setLogName(publisherKey)
        self.recipientId = recipientId
        self.microchipPatterns = microchipPatterns

    def getHeader(self, headers, header):
        """ Returns a header from the headers list of a get_url call """
        for h in headers:
            if h.startswith(header):
                return h.strip()
        return ""

    def get_vetenvoy_species(self, asmspeciesid):
        SPECIES_MAP = {
            1:  "Canine",
            2:  "Feline",
            3:  "Avian",
            4:  "Rodent",
            5:  "Rodent",
            7:  "Rabbit",
            9:  "Polecat",
            11: "Reptilian",
            12: "Tortoise",
            13: "Reptilian",
            14: "Avian",
            15: "Avian",
            16: "Goat",
            10: "Rodent",
            18: "Rodent",
            20: "Rodent",
            21: "Fish",
            22: "Rodent",
            23: "Camelid",
            24: "Equine",
            25: "Equine",
            26: "Donkey"
        }
        if SPECIES_MAP.has_key(asmspeciesid):
            return SPECIES_MAP[asmspeciesid]
        return "Miscellaneous"

    def run(self):
        def xe(s): 
            if s is None: return ""
            return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        self.log(self.publisherName + " starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        userid = configuration.vetenvoy_user_id(self.dbo)
        userpassword = configuration.vetenvoy_user_password(self.dbo)

        if userid == "" or userpassword == "":
            self.setLastError("VetEnvoy userid and userpassword must be set")
            return

        animals = get_microchip_data(self.dbo, self.microchipPatterns, self.publisherKey)
        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            return

        anCount = 0
        processed_animals = []
        failed_animals = []
        for an in animals:
            try:
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    return

                # Validate certain items aren't blank so we aren't registering bogus data
                if utils.nulltostr(an["CURRENTOWNERADDRESS"].strip()) == "":
                    self.logError("Address for the new owner is blank, cannot process")
                    continue 

                if utils.nulltostr(an["CURRENTOWNERPOSTCODE"].strip()) == "":
                    self.logError("Postal code for the new owner is blank, cannot process")
                    continue

                if an["IDENTICHIPDATE"] is None:
                    self.logError("Microchip date cannot be blank, cannot process")
                    continue

                # Make sure the length is actually suitable
                if not len(an["IDENTICHIPNUMBER"]) in (9, 10, 15):
                    self.logError("Microchip length is not 9, 10 or 15, cannot process")
                    continue

                # Construct the XML document
                x = '<?xml version="1.0" encoding="UTF-8"?>\n' \
                    '<MicrochipRegistration ' \
                    'version="1.32" ' \
                    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                    'xsi:schemaLocation="https://www.vetenvoytest.com/partner/files/Chip%201.32.xsd">' \
                    '<Identification>' \
                    ' <PracticeID>' + userid + '</PracticeID>' \
                    ' <PinNo></PinNo>' \
                    ' <Source></Source>' \
                    '</Identification>' \
                    '<OwnerDetails>' \
                    ' <Salutation>' + xe(an["CURRENTOWNERTITLE"]) + '</Salutation>' \
                    ' <Initials>' + xe(an["CURRENTOWNERINITIALS"]) + '</Initials>' \
                    ' <Forenames>' + xe(an["CURRENTOWNERFORENAMES"]) + '</Forenames>' \
                    ' <Surname>' + xe(an["CURRENTOWNERSURNAME"]) + '</Surname>' \
                    ' <Address>' \
                    '  <Line1>'+ xe(an["CURRENTOWNERADDRESS"]) + '</Line1>' \
                    '  <LineOther>'+ xe(an["CURRENTOWNERTOWN"]) + '</LineOther>' \
                    '  <PostalCode>' + xe(an["CURRENTOWNERPOSTCODE"]) + '</PostalCode>' \
                    '  <County_State>'+ xe(an["CURRENTOWNERCOUNTY"]) + '</County_State>' \
                    '  <Country>USA</Country>' \
                    ' </Address>' \
                    ' <DaytimePhone><Number>' + xe(an["CURRENTOWNERWORKTELEPHONE"]) + '</Number><Note/></DaytimePhone>' \
                    ' <EveningPhone><Number>' + xe(an["CURRENTOWNERHOMETELEPHONE"]) + '</Number><Note/></EveningPhone>' \
                    ' <MobilePhone><Number>' + xe(an["CURRENTOWNERMOBILETELEPHONE"]) + '</Number><Note/></MobilePhone>' \
                    ' <EmergencyPhone><Number/><Note/></EmergencyPhone>' \
                    ' <OtherPhone><Number/><Note/></OtherPhone>' \
                    ' <EmailAddress>' + xe(an["CURRENTOWNEREMAILADDRESS"]) + '</EmailAddress>' \
                    ' <Fax />' \
                    '</OwnerDetails>' \
                    '<PetDetails>' \
                    '  <Name>' + xe(an["ANIMALNAME"]) + '</Name>' \
                    '  <Species>' + self.get_vetenvoy_species(an["SPECIESID"]) + '</Species>' \
                    '  <Breed><FreeText>' + xe(an["BREEDNAME"]) + '</FreeText><Code/></Breed>' \
                    '  <DateOfBirth>' + i18n.format_date("%m/%d/%Y", an["DATEOFBIRTH"]) + '</DateOfBirth>' \
                    '  <Gender>' + an["SEXNAME"][0:1] + '</Gender>' \
                    '  <Colour>' + xe(an["BASECOLOURNAME"]) + '</Colour>' \
                    '  <Markings>' + xe(an["MARKINGS"]) + '</Markings>' \
                    '  <Neutered>' + (an["NEUTERED"] == 1 and "true" or "false") + '</Neutered>' \
                    '  <NotableConditions>' + xe(an["HEALTHPROBLEMS"]) + '</NotableConditions>' \
                    '</PetDetails>' \
                    '<MicrochipDetails>' \
                    '  <MicrochipNumber>' + xe(an["IDENTICHIPNUMBER"]) + '</MicrochipNumber>' \
                    '  <ImplantDate>' + i18n.format_date("%m/%d/%Y", an["IDENTICHIPDATE"]) + '</ImplantDate>' \
                    '  <ImplanterName>' + xe(an["CREATEDBY"]) + '</ImplanterName>' \
                    '</MicrochipDetails>' \
                    '<ThirdPartyDisclosure>true</ThirdPartyDisclosure>' \
                    '<ReceiveMail>true</ReceiveMail>' \
                    '<ReceiveEmail>true</ReceiveEmail>' \
                    '<Authorisation>true</Authorisation>' \
                    '</MicrochipRegistration>'

                # Build our auth headers
                authheaders = {
                    "UserId": userid,
                    "UserPassword": userpassword,
                    "VendorPassword": VETENVOY_US_VENDOR_PASSWORD,
                    "RecipientId": self.recipientId
                }

                # Start a new conversation with VetEnvoy's microchip handler
                url = VETENVOY_US_BASE_URL + "Chip/NewConversationId"
                self.log("Contacting vetenvoy to start a new conversation: %s" % url)
                try:
                    r = utils.get_url(url, authheaders)
                    self.log("Got response: %s" % r["response"])
                    conversationid = re.findall('c id="(.+?)"', r["response"])
                    if len(conversationid) == 0:
                        self.log("Could not parse conversation id, abandoning run")
                        break
                    conversationid = conversationid[0]
                    self.log("Got conversationid: %s" % conversationid)

                    # Now post the XML document
                    self.log("Posting microchip registration document: %s" % x)
                    r = utils.post_xml(VETENVOY_US_BASE_URL + "Chip/" + conversationid, x, authheaders)
                    self.log("HTTP headers: %s" % r["headers"])
                    self.log("response body: %s" % r["response"])

                    # Look in the headers for successful results
                    wassuccess = False
                    SUCCESS = ( "54000", "54100", "54108" )
                    for code in SUCCESS:
                        if str(r["headers"]).find(code) != -1:
                            self.log("successful %s response header found, marking processed" % code)
                            processed_animals.append(an)
                            # Mark success in the log
                            self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                            wassuccess = True
                            break

                    # If we saw an account not found message, there's no point sending 
                    # anything else as they will all trigger the same error
                    if str(r["headers"]).find("54101") != -1 and str(r["headers"]).find("Account Not Found") != -1:
                        self.logError("received HomeAgain 54101 'account not found' response header - abandoning run and disabling publisher")
                        configuration.publishers_enabled_disable(self.dbo, "veha")
                        break
                    if str(r["headers"]).find("54101") != -1 and str(r["headers"]).find("sender not recognized") != -1:
                        self.logError("received AKC Reunite 54101 'sender not recognized' response header - abandoning run and disabling publisher")
                        configuration.publishers_enabled_disable(self.dbo, "vear")
                        break
                    
                    if not wassuccess:
                        self.logError("no successful response header %s received" % str(SUCCESS))
                        an["FAILMESSAGE"] = "%s: %s" % (self.getHeader(r["headers"], "ResultCode"), self.getHeader(r["headers"], "ResultDetails"))
                        failed_animals.append(an)

                except Exception,err:
                    em = str(err)
                    self.logError("Failed registering microchip: %s" % em, sys.exc_info())
                    continue

            except Exception,err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Only mark processed if we aren't using VetEnvoy's test URL
        if len(processed_animals) > 0 and VETENVOY_US_BASE_URL.find("test") == -1:
            self.log("successfully processed %d animals, marking sent" % len(processed_animals))
            self.markAnimalsPublished(processed_animals)
        if len(failed_animals) > 0 and VETENVOY_US_BASE_URL.find("test") == -1:
            self.log("failed processing %d animals, marking failed" % len(failed_animals))
            self.markAnimalsPublishFailed(failed_animals)

        if VETENVOY_US_BASE_URL.find("test") != -1:
            self.log("VetEnvoy test mode, not marking animals published")

        self.saveLog()
        self.setPublisherComplete()

    @staticmethod
    def signup(dbo, post):
        """
        Handle automatically signing up for VetEnvoy's services.
        Return value on success is a tuple of userid, userpassword
        Errors are thrown to the caller
        """
        def xe(s): 
            if s is None: return ""
            return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        x = '<?xml version="1.0" encoding="UTF-8"?>\n' \
            '<Signup xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
            'xmlns:xsd="http://www.w3.org/2001/XMLSchema" ' \
            'xmlns="http://www.vetenvoy.com/schemas/signup" version="1.01">' \
            '<GeneralContact>' \
            '<Title>' + xe(post["title"]) + '</Title>' \
            '<FirstName>' + xe(post["firstname"]) + '</FirstName>' \
            '<LastName>' + xe(post["lastname"]) + '</LastName>' \
            '<Phone>' + xe(post["phone"]) + '</Phone>' \
            '<Email>' + xe(post["email"]) + '</Email>' \
            '<PositionInPractice>' + xe(post["position"]) + '</PositionInPractice>' \
            '</GeneralContact>' \
            '<PracticeDetails>' \
            '<PracticeName>' + xe(post["practicename"]) + '</PracticeName>' \
            '<Address>' + xe(post["address"]) + '</Address>' \
            '<PostalCode>' + xe(post["zipcode"]) + '</PostalCode>' \
            '<SystemId>' + VETENVOY_US_SYSTEM_ID + '</SystemId>' \
            '</PracticeDetails>' \
            '</Signup>'
        # Build our auth headers
        authheaders = {
            "UserId": VETENVOY_US_VENDOR_USERID,
            "UserPassword": VETENVOY_US_VENDOR_PASSWORD,
            "VendorPassword": VETENVOY_US_VENDOR_PASSWORD
        }
        # Start a new conversation with VetEnvoy's signup handler
        url = VETENVOY_US_BASE_URL + "AutoSignup/NewConversationId"
        al.debug("Contacting VetEnvoy to start a new signup conversation: %s" % url, "VetEnvoyMicrochipPublisher.signup", dbo)
        try:

            r = utils.get_url(url, authheaders)
            al.debug("Got response: %s" % r["response"], "VetEnvoyMicrochipPublisher.signup", dbo)
            conversationid = re.findall('c id="(.+?)"', r["response"])
            if len(conversationid) == 0:
                raise Exception("Could not parse conversation id, abandoning")
            conversationid = conversationid[0]
            al.debug("Got conversationid: %s" % conversationid, "VetEnvoyMicrochipPublisher.signup", dbo)

            # Now post the XML signup document
            al.debug("Posting signup document: %s" % x, "VetEnvoyMicrochipPublisher.signup", dbo)
            r = utils.post_xml(VETENVOY_US_BASE_URL + "AutoSignup/" + conversationid, x, authheaders)
            al.debug("Got headers: %s" % r["headers"], "VetEnvoyMicrochipPublisher.signup", dbo)
            al.debug("Got body: %s" % r["response"], "VetEnvoyMicrochipPublisher.signup", dbo)

            # Extract the id and pwd attributes
            userid = re.findall('u id="(.+?)"', r["response"])
            userpwd = re.findall('pwd="(.+?)"', r["response"])
            if len(userid) == 0 or len(userpwd) == 0:
                raise Exception("Could not parse id and pwd from body, abandoning")
            userid = userid[0]
            userpwd = userpwd[0]
            return (userid, userpwd)

        except Exception,err:
            em = str(err)
            al.error("Failed during autosignup: %s" % em, "VetEnvoyMicrochipPublisher.signup", dbo, sys.exc_info())
            raise utils.ASMValidationError("Failed during autosignup")

class HomeAgainPublisher(VetEnvoyUSMicrochipPublisher):
    def __init__(self, dbo, publishCriteria):
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        if not configuration.vetenvoy_homeagain_enabled(dbo): return
        VetEnvoyUSMicrochipPublisher.__init__(self, dbo, publishCriteria, "HomeAgain Publisher", "homeagain", VETENVOY_US_HOMEAGAIN_RECIPIENTID, 
            ['985',])

class AKCReunitePublisher(VetEnvoyUSMicrochipPublisher):
    def __init__(self, dbo, publishCriteria):
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        if not configuration.vetenvoy_akcreunite_enabled(dbo): return
        VetEnvoyUSMicrochipPublisher.__init__(self, dbo, publishCriteria, "AKC Reunite Publisher", "akcreunite", VETENVOY_US_AKC_REUNITE_RECIPIENTID, 
            ['0006', '0007', '956'])



