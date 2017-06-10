#!/usr/bin/python

import configuration
import i18n
import medical
import os
import sys

from base import FTPPublisher
from sitedefs import PETFINDER_FTP_HOST

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
        self.initLog("petfinder", "PetFinder Publisher")

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
            if self.logSearch("530 Login") != -1:
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
            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals, first=True)

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


