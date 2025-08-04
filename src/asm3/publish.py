
"""
    Module containing all functions/classes for internet publishing
"""

import asm3.al
import asm3.configuration

import asm3.publishers.adoptapet
import asm3.publishers.akcreunite
import asm3.publishers.anibaseuk
import asm3.publishers.buddyid
import asm3.publishers.findpet
import asm3.publishers.foundanimals
import asm3.publishers.homeagain
import asm3.publishers.petfbi
import asm3.publishers.html
import asm3.publishers.maddiesfund
import asm3.publishers.mypetuk
import asm3.publishers.petcademy 
import asm3.publishers.petfinder
import asm3.publishers.petlink
import asm3.publishers.petrescue
import asm3.publishers.petslocateduk
import asm3.publishers.pettracuk
import asm3.publishers.rescuegroups
import asm3.publishers.sacmetrics
import asm3.publishers.savourlife
import asm3.publishers.smarttag

from asm3.publishers.base import PublishCriteria
from asm3.typehints import Database, Results

import collections

PUBLISHER_LIST = collections.OrderedDict()
PUBLISHER_LIST["html"] = {
    "label":    "Publish HTML via FTP",
    "class":    asm3.publishers.html.HTMLPublisher,
    "locales":  "",
    "sub24hour": False
}
PUBLISHER_LIST["ap"] = {
    "label":    "Publish to AdoptAPet.com",
    "class":    asm3.publishers.adoptapet.AdoptAPetPublisher,
    "locales":  "en en_CA fr_CA en_MX es_MX",
    "sub24hour": True
}
PUBLISHER_LIST["fbi"] = {
    "label":    "Publish to PetFBI.org",
    "class":    asm3.publishers.petfbi.PetFBIPublisher,
    "locales":  "en en_CA fr_CA",
    "sub24hour": False
}
PUBLISHER_LIST["mf"] = {
    "label":    "Publish to Maddie's Pet Assistant",
    "class":    asm3.publishers.maddiesfund.MaddiesFundPublisher,
    "locales":  "en en_GB en_CA fr_CA en_AU",
    "sub24hour": True
}
PUBLISHER_LIST["pc"] = {
    "label":    "Publish to Petcademy",
    "class":    asm3.publishers.petcademy.PetcademyPublisher,
    "locales":  "en en_GB en_CA fr_CA en_AU",
    "sub24hour": True
}
PUBLISHER_LIST["pf"] = {
    "label":    "Publish to PetFinder.com",
    "class":    asm3.publishers.petfinder.PetFinderPublisher,
    "locales":  "en en_CA fr_CA en_MX es_MX",
    "sub24hour": True
}
PUBLISHER_LIST["pr"] = {
    "label":    "Publish to PetRescue.com.au",
    "class":    asm3.publishers.petrescue.PetRescuePublisher,
    "locales":  "en_AU",
    "sub24hour": True
}
PUBLISHER_LIST["sac"] = {
    "label":    "Publish to shelteranimalscount.org",
    "class":    asm3.publishers.sacmetrics.SACMetricsPublisher,
    "locales":  "en",
    "sub24hour": False
}
PUBLISHER_LIST["sl"] = {
    "label":    "Publish to Savour-Life.com.au",
    "class":    asm3.publishers.savourlife.SavourLifePublisher,
    "locales":  "en_AU",
    "sub24hour": True
}
PUBLISHER_LIST["pcuk"] = {
    "label":    "Publish to PetsLocated.com",
    "class":    asm3.publishers.petslocateduk.PetsLocatedUKPublisher,
    "locales":  "en_GB",
    "sub24hour": False
}
PUBLISHER_LIST["rg"] = {
    "label":    "Publish to RescueGroups.org",
    "class":    asm3.publishers.rescuegroups.RescueGroupsPublisher,
    "locales":  "en",
    "sub24hour": True
}
PUBLISHER_LIST["ak"] = {
    "label":    "Register microchips with AKC Reunite",
    "class":    asm3.publishers.akcreunite.AKCReunitePublisher,
    "locales":  "en",
    "sub24hour": False
}
PUBLISHER_LIST["bd"] = {
    "label":    "Register microchips with BuddyID",
    "class":    asm3.publishers.buddyid.BuddyIDPublisher,
    "locales":  "en",
    "sub24hour": False
}
PUBLISHER_LIST["fip"] = {
    "label":    "Register found pets and microchips with FindPet.com",
    "class":    asm3.publishers.findpet.FindPetPublisher,
    "locales":  "en",
    "sub24hour": False
}
PUBLISHER_LIST["abuk"] = {
    "label":    "Register microchips with Identibase UK",
    "class":    asm3.publishers.anibaseuk.AnibaseUKPublisher,
    "locales":  "en_GB",
    "sub24hour": False
}
PUBLISHER_LIST["mpuk"] = {
    "label":    "Register microchips with MyPet UK",
    "class":    asm3.publishers.mypetuk.MyPetUKPublisher,
    "locales":  "en_GB",
    "sub24hour": False
}
PUBLISHER_LIST["ptuk"] = {
    "label":    "Register microchips with AVID UK",
    "class":    asm3.publishers.pettracuk.PETtracUKPublisher,
    "locales":  "en_GB",
    "sub24hour": False
}
PUBLISHER_LIST["fa"] = {
    "label":    "Register microchips with FoundAnimals/24Pet",
    "class":    asm3.publishers.foundanimals.FoundAnimalsPublisher,
    "locales":  "en en_CA fr_CA",
    "sub24hour": False
}
PUBLISHER_LIST["ha"] = {
    "label":    "Register microchips with HomeAgain",
    "class":    asm3.publishers.homeagain.HomeAgainPublisher,
    "locales":  "en",
    "sub24hour": False
}
PUBLISHER_LIST["pl"] = {
    "label":    "Register microchips with PetLink",
    "class":    asm3.publishers.petlink.PetLinkPublisher,
    "locales":  "en en_CA fr_CA en_MX es_MX",
    "sub24hour": False
}
PUBLISHER_LIST["st"] = {
    "label":    "Register microchips with SmartTag Pet ID",
    "class":    asm3.publishers.smarttag.SmartTagPublisher,
    "locales":  "en",
    "sub24hour": False
}

def delete_old_publish_logs(dbo: Database) -> None:
    """ Deletes all publishing logs older than 3 months """
    KEEP_DAYS = 93
    cutoff = dbo.today(offset=KEEP_DAYS*-1)
    count = dbo.query_int("SELECT COUNT(*) FROM publishlog WHERE PublishDateTime < ?", [cutoff])
    asm3.al.debug("removing %d publishing logs (keep for %d days)." % (count, KEEP_DAYS), "publish.delete_old_publish_logs", dbo)
    dbo.execute("DELETE FROM publishlog WHERE PublishDateTime < ?", [cutoff])

def get_publish_logs(dbo: Database) -> Results:
    """ Returns all publishing logs """
    return dbo.query("SELECT ID, PublishDateTime, Name, Success, Alerts FROM publishlog ORDER BY PublishDateTime DESC")

def get_publish_log(dbo: Database, plid: int) -> str:
    """ Returns the log for a publish log ID """
    return dbo.query_string("SELECT LogData FROM publishlog WHERE ID = ?", [plid])

def start_publisher(dbo: Database, code: str, user: str = "", newthread: bool = True) -> None:
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


