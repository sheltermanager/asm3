#!/usr/bin/python

"""
    Module containing all functions/classes for internet publishing
"""

import al
import configuration

import publishers.adoptapet, publishers.anibaseuk, publishers.foundanimals, publishers.helpinglostpets, publishers.html, publishers.maddiesfund, publishers.petfinder, publishers.petlink, publishers.petrescue, publishers.petslocateduk, publishers.pettracuk, publishers.rescuegroups, publishers.smarttag, publishers.vetenvoy

from publishers.base import PublishCriteria

def delete_old_publish_logs(dbo):
    """ Deletes all publishing logs older than 14 days """
    KEEP_DAYS = 14
    cutoff = dbo.today(offset=KEEP_DAYS*-1)
    count = dbo.query_int("SELECT COUNT(*) FROM publishlog WHERE PublishDateTime < ?", [cutoff])
    al.debug("removing %d publishing logs (keep for %d days)." % (count, KEEP_DAYS), "publish.delete_old_publish_logs", dbo)
    dbo.execute("DELETE FROM publishlog WHERE PublishDateTime < ?", [cutoff])

def get_publish_logs(dbo):
    """ Returns all publishing logs """
    return dbo.query("SELECT ID, PublishDateTime, Name, Success, Alerts FROM publishlog ORDER BY PublishDateTime DESC")

def get_publish_log(dbo, plid):
    """ Returns the log for a publish log ID """
    return dbo.query_string("SELECT LogData FROM publishlog WHERE ID = ?", [plid])

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


