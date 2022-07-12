
import asm3.animal
import asm3.configuration
import asm3.i18n
import asm3.medical
import asm3.movement
import asm3.lookups
import asm3.utils

from .base import FTPPublisher
from asm3.sitedefs import PETCADEMY_FTP_HOST, PETCADEMY_FTP_USER, PETCADEMY_FTP_PASSWORD, SERVICE_URL

import os, sys

class PetcademyPublisher(FTPPublisher):
    """
    Handles updating recent adoptions with Petcademy via their API
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        FTPPublisher.__init__(self, dbo, publishCriteria,
            PETCADEMY_FTP_HOST, PETCADEMY_FTP_USER, 
            PETCADEMY_FTP_PASSWORD)
        self.initLog("petcademy", "Petcademy Publisher")

    def getDate(self, d):
        """ Returns a date in their preferred format of mm/dd/yyyy """
        return asm3.i18n.format_date(d, "%m/%d/%Y")

    def getEmail(self, s):
        """ Returns only the first email if more than one is specified """
        if s is None: return ""
        if s.strip() == "": return ""
        return s.split(",")[0].strip()

    def getPetStatus(self, an):
        """ Returns the pet status - Deceased, Active (on shelter), Inactive (foster/adopted) """
        if an["DECEASEDDATE"] is not None:
            return "Deceased"
        elif an["ACTIVEMOVEMENTTYPE"] == 0:
            return "Active"
        else:
            return "Inactive"

    def getEventType(self, an):
        """ Returns the relationship type - adopted, fostered or blank for on shelter """
        if an["ACTIVEMOVEMENTTYPE"] == 1:
            return "Adoption"
        elif an["ACTIVEMOVEMENTTYPE"] == 2:
            return "Foster"
        else:
            return ""

    def getData(self, periodindays):
        """ Returns the animal data for periodindays """
        # Send all fosters and adoptions for the period that haven't been sent since they last had a change.
        # (we use lastchangeddate instead of sent date because Petcademy want an update when a number of key
        #  animal fields change, such as neuter status, microchip info, rabies tag, etc)
        cutoff = asm3.i18n.subtract_days(asm3.i18n.now(self.dbo.timezone), periodindays)
        sql = "%s WHERE a.ActiveMovementType IN (1,2) " \
            "AND a.ActiveMovementDate >= ? AND a.DeceasedDate Is Null AND a.NonShelterAnimal = 0 " \
            "AND NOT EXISTS(SELECT AnimalID FROM animalpublished WHERE AnimalID = a.ID AND PublishedTo = 'petcademy' AND SentDate >= %s) " \
            "ORDER BY a.ID" % (asm3.animal.get_animal_query(self.dbo), self.dbo.sql_greatest(["a.ActiveMovementDate", "a.LastChangedDate"]))
        animals = self.dbo.query(sql, [cutoff], distincton="ID")

        # Now find animals who have been sent previously and are now deceased (using sent date against deceased to prevent re-sends) 
        sql = "%s WHERE a.DeceasedDate Is Not Null AND a.DeceasedDate >= ? AND " \
            "EXISTS(SELECT AnimalID FROM animalpublished WHERE AnimalID = a.ID AND " \
            "PublishedTo = 'petcademy' AND SentDate <= a.DeceasedDate)" % asm3.animal.get_animal_query(self.dbo)
        animals += self.dbo.query(sql, [cutoff], distincton="ID")

        # Now find shelter animals who have been sent previously and are back (using sent date against return to prevent re-sends)
        sql = "%s WHERE a.Archived = 0 AND " \
            "EXISTS(SELECT AnimalID FROM animalpublished WHERE AnimalID = a.ID AND " \
            "PublishedTo = 'petcademy' AND SentDate < " \
            "(SELECT MAX(ReturnDate) FROM adoption WHERE AnimalID = a.ID AND MovementType IN (1,2) AND ReturnDate Is Not Null))" % asm3.animal.get_animal_query(self.dbo)
        animals += self.dbo.query(sql, distincton="ID")

        return animals

    def run(self):
        
        self.log("Petcademy Publisher starting...")

        PERIOD = 214 # How many days to go back when checking for fosters and adoptions (7 months * 30.5 = 214 days)

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        token = asm3.configuration.petcademy_token(self.dbo)

        if token  == "":
            self.setLastError("token needs to be set for Petcademy Publisher")
            self.cleanup()
            return

        animals = self.getData(PERIOD)

        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            return

        if not self.openFTPSocket(ssl=True): 
            self.setLastError("Failed opening FTP socket.")
            self.cleanup()
            return

        csv = [ "FirstName,Lastname,EmailAddress,Street,City,State,Zipcode,ContactNumber," \
                "EmailOptOut,PetID,PetName,PetSpecies,PetSex,Breed,DateofBirth,Color," \
                "Status,EventDate,EventType,Organization,Photo" ]
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
                    return

                csv.append( self.processAnimal(an) )

                self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (an["SHELTERCODE"], err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals, first=True)

        fname = "%s_%s.csv" % ( token, asm3.i18n.format_date(asm3.i18n.now(), "%Y%m%d%H%M%S") )
        # Upload the datafile to a sheltermanager folder
        self.chdir("sheltermanager", "sheltermanager")
        self.saveFile(os.path.join(self.publishDir, fname), "\n".join(csv))
        self.log("Uploading datafile %s" % fname)
        self.upload(fname)
        self.log("Uploaded %s" % fname)
        self.log("-- FILE DATA -- (csv)")
        self.log("\n".join(csv))
        self.cleanup()

    def processAnimal(self, an):
        """ Builds a CSV row """
        # FirstName,Lastname,EmailAddress,Street,City,State,Zipcode,ContactNumber,
        # EmailOptOut,PetID,PetName,PetSpecies,PetSex,Breed,DateofBirth,Color,
        # Status,EventDate,EventType,Organization,Photo
        line = [
            an.CURRENTOWNERFORENAMES,
            an.CURRENTOWNERSURNAME,
            self.getEmail(an.CURRENTOWNEREMAILADDRESS),
            an.CURRENTOWNERADDRESS,
            an.CURRENTOWNERTOWN,
            an.CURRENTOWNERCOUNTY,
            an.CURRENTOWNERPOSTCODE,
            an.CURRENTOWNERMOBILETELEPHONE,
            str(an.CURRENTOWNEREXCLUDEEMAIL),
            an.SHELTERCODE,
            an.ANIMALNAME,
            an.SPECIESNAME,
            an.SEXNAME,
            an.BREEDNAME,
            self.getDate(an.DATEOFBIRTH),
            an.BASECOLOURNAME,
            self.getPetStatus(an),
            self.getDate(an.ACTIVEMOVEMENTDATE),
            self.getEventType(an),
            asm3.configuration.organisation(self.dbo),
            "%s?method=animal_image&account=%s&animalid=%s" % (SERVICE_URL, self.dbo.database, an.ID)
        ]
        return self.csvLine(line)
