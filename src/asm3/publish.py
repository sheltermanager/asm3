#!/usr/bin/python

"""
    Module containing all functions/classes for internet publishing
"""

import asm3.al
import asm3.configuration

import asm3.publishers.adoptapet, asm3.publishers.anibaseuk, asm3.publishers.foundanimals, asm3.publishers.helpinglostpets, asm3.publishers.html, asm3.publishers.maddiesfund, asm3.publishers.petfinder, asm3.publishers.petlink, asm3.publishers.petrescue, asm3.publishers.petslocateduk, asm3.publishers.pettracuk, asm3.publishers.rescuegroups, asm3.publishers.savourlife, asm3.publishers.smarttag, asm3.publishers.vetenvoy

from asm3.publishers.base import PublishCriteria

import collections

PUBLISHER_LIST = collections.OrderedDict()
PUBLISHER_LIST["html"] = {
    "label":    "Publish HTML via FTP",
    "class":    asm3.publishers.html.HTMLPublisher,
    "locales":  ""
}
PUBLISHER_LIST["ap"] = {
    "label":    "Publish to AdoptAPet.com",
    "class":    asm3.publishers.adoptapet.AdoptAPetPublisher,
    "locales":  "en en_CA fr_CA en_MX es_MX"
}
PUBLISHER_LIST["hlp"] = {
    "label":    "Publish to HelpingLostPets.com",
    "class":    asm3.publishers.helpinglostpets.HelpingLostPetsPublisher,
    "locales":  ""
}
PUBLISHER_LIST["mf"] = {
    "label":    "Publish to Maddie's Pet Assistant",
    "class":    asm3.publishers.maddiesfund.MaddiesFundPublisher,
    "locales":  "en en_CA en_AU"
}
PUBLISHER_LIST["pf"] = {
    "label":    "Publish to PetFinder.com",
    "class":    asm3.publishers.petfinder.PetFinderPublisher,
    "locales":  "en en_CA en_MX es_MX"
}
PUBLISHER_LIST["pr"] = {
    "label":    "Publish to PetRescue.com.au",
    "class":    asm3.publishers.petrescue.PetRescuePublisher,
    "locales":  "en_AU"
}
PUBLISHER_LIST["sl"] = {
    "label":    "Publish to Savour-Life.com.au",
    "class":    asm3.publishers.savourlife.SavourLifePublisher,
    "locales":  "en_AU"
}
PUBLISHER_LIST["pcuk"] = {
    "label":    "Publish to PetsLocated.com",
    "class":    asm3.publishers.petslocateduk.PetsLocatedUKPublisher,
    "locales":  "en_GB"
}
PUBLISHER_LIST["rg"] = {
    "label":    "Publish to RescueGroups.org",
    "class":    asm3.publishers.rescuegroups.RescueGroupsPublisher,
    "locales":  "en"
}
PUBLISHER_LIST["vear"] = {
    "label":    "Register animals with AKC Reunite Microchips (via VetEnvoy)",
    "class":    asm3.publishers.vetenvoy.AKCReunitePublisher,
    "locales":  "en"
}
PUBLISHER_LIST["abuk"] = {
    "label":    "Register animals with Identibase UK Microchips",
    "class":    asm3.publishers.anibaseuk.AnibaseUKPublisher,
    "locales":  "en_GB"
}
PUBLISHER_LIST["ptuk"] = {
    "label":    "Register animals with AVID UK Microchips",
    "class":    asm3.publishers.pettracuk.PETtracUKPublisher,
    "locales":  "en_GB"
}
PUBLISHER_LIST["fa"] = {
    "label":    "Register animal microchips with FoundAnimals.org",
    "class":    asm3.publishers.foundanimals.FoundAnimalsPublisher,
    "locales":  "en"
}
PUBLISHER_LIST["veha"] = {
    "label":    "Register animals with HomeAgain Microchips (via VetEnvoy)",
    "class":    asm3.publishers.vetenvoy.HomeAgainPublisher,
    "locales":  "en"
}
PUBLISHER_LIST["pl"] = {
    "label":    "Register animals with PetLink Microchips",
    "class":    asm3.publishers.petlink.PetLinkPublisher,
    "locales":  "en en_CA en_MX es_MX"
}
PUBLISHER_LIST["st"] = {
    "label":    "Register animals with SmartTag Pet ID",
    "class":    asm3.publishers.smarttag.SmartTagPublisher,
    "locales":  "en"
}

def delete_old_publish_logs(dbo):
    """ Deletes all publishing logs older than 14 days """
    KEEP_DAYS = 14
    cutoff = dbo.today(offset=KEEP_DAYS*-1)
    count = dbo.query_int("SELECT COUNT(*) FROM publishlog WHERE PublishDateTime < ?", [cutoff])
    asm3.al.debug("removing %d publishing logs (keep for %d days)." % (count, KEEP_DAYS), "publish.delete_old_publish_logs", dbo)
    dbo.execute("DELETE FROM publishlog WHERE PublishDateTime < ?", [cutoff])

def get_publish_logs(dbo):
    """ Returns all publishing logs """
    return dbo.query("SELECT ID, PublishDateTime, Name, Success, Alerts FROM publishlog ORDER BY PublishDateTime DESC")

def get_publish_log(dbo, plid):
    """ Returns the log for a publish log ID """
    return dbo.query_string("SELECT LogData FROM publishlog WHERE ID = ?", [plid])

def start_publisher(dbo, code, user = "", newthread = True):
    """ Starts the publisher with code """
    pc = PublishCriteria(asm3.configuration.publisher_presets(dbo))
    p = None

    if code == "html":
        # HTML has a different signature to the other publishers so we handle it separately
        p = asm3.publishers.html.HTMLPublisher(dbo, pc, user)

    elif code not in PUBLISHER_LIST:
        asm3.al.error("invalid publisher code '%s'" % code, "publish.start_publisher", dbo)
        return

    else:
        p = PUBLISHER_LIST[code]["class"](dbo, pc)

    if newthread:
        p.start()
    else:
        p.run()


