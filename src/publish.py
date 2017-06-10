#!/usr/bin/python

"""
    Module containing all functions/classes for internet publishing
"""

import al
import additional
import animal
import configuration
import db
import dbfs
import html
import i18n
import movement
import smcom
import sys
import utils
import wordprocessor

import publishers.adoptapet, publishers.anibaseuk, publishers.foundanimals, publishers.helpinglostpets, publishers.html, publishers.maddiesfund, publishers.petfinder, publishers.petlink, publishers.petrescue, publishers.petslocateduk, publishers.pettracuk, publishers.rescuegroups, publishers.smarttag, publishers.vetenvoy

from publishers.base import PublishCriteria
from sitedefs import BASE_URL, SERVICE_URL

def get_animal_data(dbo, pc = None, animalid = 0, include_additional_fields = False, strip_personal_data = False):
    """
    Returns a resultset containing the animal info for the criteria given.
    pc: The publish criteria (if None, default is used)
    animalid: If non-zero only returns the animal given (if it is adoptable)
    include_additional_fields: Load additional fields for each result
    strip_personal_data: Remove any personal data such as surrenderer, brought in by, etc.
    """
    if pc is None:
        pc = PublishCriteria(configuration.publisher_presets(dbo))
    sql = get_animal_data_query(dbo, pc, animalid)
    rows = db.query(dbo, sql, limit=pc.limit)
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
    # If we aren't including animals with blank descriptions, remove them now
    if not pc.includeWithoutDescription:
        rows = [r for r in rows if utils.nulltostr(r["WEBSITEMEDIANOTES"]).strip() != ""]
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
    # Strip any personal data if requested
    if strip_personal_data:
        for r in rows:
            for k in r.iterkeys():
                if k.startswith("ORIGINALOWNER") or k.startswith("BROUGHTINBY") or k.startswith("CURRENTOWNER") or k.startswith("RESERVEDOWNER"):
                    r[k] = ""
    # If bondedAsSingle is on, go through the the set of animals and merge
    # the bonded animals into a single record
    def merge_animal(a, aid):
        """
        Find the animal in rows with animalid, merge it into a and
        then remove it from the set.
        """
        for r in rows:
            if r["ID"] == aid:
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
    if not pc.includeNonNeutered:
        sql += " AND a.Neutered = 1"
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
    exclude = i18n.subtract_days(i18n.now(), pc.excludeUnderWeeks * 7)
    sql += " AND a.DateOfBirth <= " + db.dd(exclude)
    # Filter out dead and unadoptable animals
    sql += " AND a.DeceasedDate Is Null AND a.IsNotAvailableForAdoption = 0"
    # Filter out permanent fosters
    sql += " AND a.HasPermanentFoster = 0"
    # Filter out animals with a future adoption
    sql += " AND NOT EXISTS(SELECT ID FROM adoption WHERE MovementType = 1 AND AnimalID = a.ID AND MovementDate > %s)" % db.dd(i18n.now(dbo.timezone))
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
    except Exception as err:
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
    """ Constructs the animal view page to the template. """
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
    # Add extra tags for websitemedianame2-4 if they exist
    if a["WEBSITEIMAGECOUNT"] > 1: 
        tags["WEBMEDIAFILENAME2"] = "%s&seq=2" % a["WEBSITEMEDIANAME"]
    if a["WEBSITEIMAGECOUNT"] > 2: 
        tags["WEBMEDIAFILENAME3"] = "%s&seq=3" % a["WEBSITEMEDIANAME"]
    if a["WEBSITEIMAGECOUNT"] > 3: 
        tags["WEBMEDIAFILENAME4"] = "%s&seq=4" % a["WEBSITEMEDIANAME"]
    # Add extra publishing text, preserving the line endings
    notes = utils.nulltostr(a["WEBSITEMEDIANOTES"])
    notes += configuration.third_party_publisher_sig(dbo)
    notes = notes.replace("\n", "**le**")
    tags["WEBMEDIANOTES"] = notes 
    s = wordprocessor.substitute_tags(s, tags, True, "$$", "$$")
    s = s.replace("**le**", "<br />")
    return s

def get_animal_view_adoptable_js(dbo):
    """ Returns js that outputs adoptable animals into a host div """
    js = utils.read_text_file("%s/static/js/animal_view_adoptable.js" % dbo.installpath)
    # inject adoptable animals, account and base url
    pc = PublishCriteria(configuration.publisher_presets(dbo))
    js = js.replace("{TOKEN_ACCOUNT}", dbo.database)
    js = js.replace("{TOKEN_BASE_URL}", BASE_URL)
    js = js.replace("\"{TOKEN_ADOPTABLES}\"", html.json(get_animal_data(dbo, pc, include_additional_fields = True, strip_personal_data = True)))
    return js

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
    return len(get_animal_data(dbo, pc, animalid)) > 0

def delete_old_publish_logs(dbo):
    """ Deletes all publishing logs older than 14 days """
    KEEP_DAYS = 14
    where = "WHERE PublishDateTime < %s" % db.dd(i18n.subtract_days(i18n.now(dbo.timezone), KEEP_DAYS))
    count = db.query_int(dbo, "SELECT COUNT(*) FROM publishlog %s" % where)
    al.debug("removing %d publishing logs (keep for %d days)." % (count, KEEP_DAYS), "publish.delete_old_publish_logs", dbo)
    db.execute(dbo, "DELETE FROM publishlog %s" % where)

def get_publish_logs(dbo):
    """ Returns all publishing logs """
    return db.query(dbo, "SELECT ID, PublishDateTime, Name, Success, Alerts FROM publishlog ORDER BY PublishDateTime DESC")

def get_publish_log(dbo, plid):
    """ Returns the log for a publish log ID """
    return db.query_string(dbo, "SELECT LogData FROM publishlog WHERE ID = %d" % plid)

def start_publisher(dbo, code, user = "", async = True):
    """ Starts the publisher with code on a background thread """
    pc = PublishCriteria(configuration.publisher_presets(dbo))
    if async:
        if code == "ftp":    publishers.html.HTMLPublisher(dbo, pc, user).start()
        elif code == "pf":   publishers.petfinder.PetFinderPublisher(dbo, pc).start()
        elif code == "ap":   publishers.adoptapet.AdoptAPetPublisher(dbo, pc).start()
        elif code == "rg":   publishers.rescuegroups.RescueGroupsPublisher(dbo, pc).start()
        elif code == "mf":   publishers.maddiesfund.MaddiesFundPublisher(dbo, pc).start()
        elif code == "hlp":  publishers.helpinglostpets.HelpingLostPetsPublisher(dbo, pc).start()
        elif code == "pl":   publishers.petlink.PetLinkPublisher(dbo, pc).start()
        elif code == "pr":   publishers.petrescue.PetRescuePublisher(dbo, pc).start()
        elif code == "st":   publishers.smarttag.SmartTagPublisher(dbo, pc).start()
        elif code == "abuk": publishers.anibaseuk.AnibaseUKPublisher(dbo, pc).start()
        elif code == "fa":   publishers.foundanimals.FoundAnimalsPublisher(dbo, pc).start()
        elif code == "pcuk": publishers.petslocateduk.PetsLocatedUKPublisher(dbo, pc).start()
        elif code == "ptuk": publishers.pettracuk.PETtracUKPublisher(dbo, pc).start()
        elif code == "veha": publishers.vetenvoy.HomeAgainPublisher(dbo, pc).start()
        elif code == "vear": publishers.vetenvoy.AKCReunitePublisher(dbo, pc).start()
    else:
        if code == "ftp":    publishers.html.HTMLPublisher(dbo, pc, user).run()
        elif code == "pf":   publishers.petfinder.PetFinderPublisher(dbo, pc).run()
        elif code == "ap":   publishers.adoptapet.AdoptAPetPublisher(dbo, pc).run()
        elif code == "rg":   publishers.rescuegroups.RescueGroupsPublisher(dbo, pc).run()
        elif code == "mf":   publishers.maddiesfund.MaddiesFundPublisher(dbo, pc).run()
        elif code == "hlp":  publishers.helpinglostpets.HelpingLostPetsPublisher(dbo, pc).run()
        elif code == "pl":   publishers.petlink.PetLinkPublisher(dbo, pc).run()
        elif code == "pr":   publishers.petrescue.PetRescuePublisher(dbo, pc).run()
        elif code == "st":   publishers.smarttag.SmartTagPublisher(dbo, pc).run()
        elif code == "abuk": publishers.anibaseuk.AnibaseUKPublisher(dbo, pc).run()
        elif code == "fa":   publishers.foundanimals.FoundAnimalsPublisher(dbo, pc).run()
        elif code == "pcuk": publishers.petslocateduk.PetsLocatedUKPublisher(dbo, pc).run()
        elif code == "ptuk": publishers.pettracuk.PETtracUKPublisher(dbo, pc).run()
        elif code == "veha": publishers.vetenvoy.HomeAgainPublisher(dbo, pc).run()
        elif code == "vear": publishers.vetenvoy.AKCReunitePublisher(dbo, pc).run()


