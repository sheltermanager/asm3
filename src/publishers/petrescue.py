#!/usr/bin/python

import configuration
import i18n
import os
import sys
import utils

from base import FTPPublisher
from sitedefs import PETRESCUE_FTP_HOST

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
        self.initLog("petrescue", "PetRescue Publisher")

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
            if self.logSearch("530 Login") != -1:
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
            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals, first=True)

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


