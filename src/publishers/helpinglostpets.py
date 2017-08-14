#!/usr/bin/python

import configuration
import i18n
import lostfound
import os
import sys

from base import FTPPublisher
from sitedefs import HELPINGLOSTPETS_FTP_HOST

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
        self.initLog("helpinglostpets", i18n._("HelpingLostPets Publisher", l))

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
            if self.logSearch("530 Login") != -1:
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
            except Exception as err:
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
            except Exception as err:
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


