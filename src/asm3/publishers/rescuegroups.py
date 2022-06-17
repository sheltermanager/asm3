
import asm3.configuration
import asm3.i18n
import asm3.medical

from .base import FTPPublisher
from asm3.sitedefs import RESCUEGROUPS_FTP_HOST

import os
import sys
import time

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
            RESCUEGROUPS_FTP_HOST, asm3.configuration.rescuegroups_user(dbo), 
            asm3.configuration.rescuegroups_password(dbo), 21, "", False)
        self.initLog("rescuegroups", "RescueGroups Publisher")

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
        Returns 0 == Yes, 1 == No, 2 or 3 == Empty string
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
        shelterid = asm3.configuration.rescuegroups_user(self.dbo)
        if shelterid == "":
            self.setLastError("No RescueGroups.org shelter id has been set.")
            self.cleanup()
            return

        # NOTE: We still publish even if there are no animals. This prevents situations
        # where the last animal can't be removed from rescuegroups because the shelter
        # has no animals to send.
        animals = self.getMatchingAnimals()
        if len(animals) == 0:
            self.logError("No animals found to publish, sending empty file.")

        if not self.openFTPSocket(): 
            self.setLastError("Failed opening FTP socket.")
            # NOTE: RescueGroups started returning transient 530 errors June 2022
            #       Disabled this to stop the publisher repeatedly getting disabled
            #if self.logSearch("530 Login") != -1:
            #    self.log("Found 530 Login incorrect: disabling RescueGroups publisher.")
            #    asm3.configuration.publishers_enabled_disable(self.dbo, "rg")
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
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    self.cleanup()
                    return

                # Upload images for this animal
                totalimages = self.uploadImages(an, False, 4)

                csv.append( self.processAnimal(an, totalimages, shelterid) )

                # Mark success in the log
                self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals, first=True)

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

    def processAnimal(self, an, totalimages=0, shelterid=""):
        """ Process an animal and return a CSV line. totalimages = the number of images we uploaded for this animal """
        line = []
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
        line.append("\"%s\"" % an["ANIMALNAME"])
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
        ageinyears = asm3.i18n.date_diff_days(an["DATEOFBIRTH"], asm3.i18n.now(self.dbo.timezone))
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
        line.append("\"%s\"" % self.rgYesNo(asm3.medical.get_vaccinated(self.dbo, int(an["ID"]))))
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
        return self.csvLine(line)
