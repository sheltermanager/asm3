#!/usr/bin/python

"""
    Module containing all functions/classes for internet publishing
"""

import al
import configuration
import db
import i18n

import publishers.adoptapet, publishers.anibaseuk, publishers.foundanimals, publishers.helpinglostpets, publishers.html, publishers.maddiesfund, publishers.petfinder, publishers.petlink, publishers.petrescue, publishers.petslocateduk, publishers.pettracuk, publishers.rescuegroups, publishers.smarttag, publishers.vetenvoy

from publishers.base import PublishCriteria

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
    p = None
    if code == "html":   p = publishers.html.HTMLPublisher(dbo, pc, user)
    elif code == "pf":   p = publishers.petfinder.PetFinderPublisher(dbo, pc)
    elif code == "ap":   p = publishers.adoptapet.AdoptAPetPublisher(dbo, pc)
    elif code == "rg":   p = publishers.rescuegroups.RescueGroupsPublisher(dbo, pc)
    elif code == "mf":   p = publishers.maddiesfund.MaddiesFundPublisher(dbo, pc)
    elif code == "hlp":  p = publishers.helpinglostpets.HelpingLostPetsPublisher(dbo, pc)
    elif code == "pl":   p = publishers.petlink.PetLinkPublisher(dbo, pc)
    elif code == "pr":   p = publishers.petrescue.PetRescuePublisher(dbo, pc)
    elif code == "st":   p = publishers.smarttag.SmartTagPublisher(dbo, pc)
    elif code == "abuk": p = publishers.anibaseuk.AnibaseUKPublisher(dbo, pc)
    elif code == "fa":   p = publishers.foundanimals.FoundAnimalsPublisher(dbo, pc)
    elif code == "pcuk": p = publishers.petslocateduk.PetsLocatedUKPublisher(dbo, pc)
    elif code == "ptuk": p = publishers.pettracuk.PETtracUKPublisher(dbo, pc)
    elif code == "ve":   p = publishers.vetenvoy.AllVetEnvoyPublisher(dbo, pc)
    elif code == "veha": p = publishers.vetenvoy.HomeAgainPublisher(dbo, pc)
    elif code == "vear": p = publishers.vetenvoy.AKCReunitePublisher(dbo, pc)
    else: 
        al.error("invalid publisher code '%s'" % code, "publish.start_publisher", dbo)
        return
    if async:
        p.start()
    else:
        p.run()


