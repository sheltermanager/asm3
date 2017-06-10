#!/usr/bin/python

"""
    Module containing all functions/classes for internet publishing
"""

import al
import animal
import configuration
import db
import dbfs
import html
import i18n
import smcom
import utils
import wordprocessor

import publishers.adoptapet, publishers.anibaseuk, publishers.foundanimals, publishers.helpinglostpets, publishers.html, publishers.maddiesfund, publishers.petfinder, publishers.petlink, publishers.petrescue, publishers.petslocateduk, publishers.pettracuk, publishers.rescuegroups, publishers.smarttag, publishers.vetenvoy

from publishers.base import PublishCriteria, get_animal_data
from sitedefs import BASE_URL, SERVICE_URL

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


