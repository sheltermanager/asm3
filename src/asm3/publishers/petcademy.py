
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
        FTPPublisher.__init__(self, dbo, publishCriteria,
            PETCADEMY_FTP_HOST, PETCADEMY_FTP_USER, 
            PETCADEMY_FTP_PASSWORD)
        self.initLog("petcademy", "Petcademy Publisher")

    def getAge(self, dob, speciesid):
        """ Returns an age banding based on date of birth and species """
        # Kitten (0-8 weeks) = 1, Kitten/Juvenile (9 weeks- 5 months) = 2, Adult Cat (6 months - 8 years) =3,
        # Senior Cat (9 years) = 4, Puppy (0-8 weeks) = 5, Puppy/Juvenile (9 weeks 11-months) =6, Adult Dog (1
        # year - 7 years) =7, Senior Dog (8 years) = 8
        ageinyears = asm3.i18n.date_diff_days(dob, asm3.i18n.now())
        ageinyears /= 365.0
        age = 0
        # Cats
        if speciesid == 2:
            if ageinyears < 0.15: age = 1
            elif ageinyears < 0.5: age = 2
            elif ageinyears < 8: age = 3
            else: age = 4
        # Dogs
        elif speciesid == 1:
            if ageinyears < 0.15: age = 5
            elif ageinyears < 0.9: age = 6
            elif ageinyears < 8: age = 7
            else: age = 8
        return age

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
        # (we use lastchangeddate instead of sent date because MPA want an update when a number of key
        #  animal fields change, such as neuter status, microchip info, rabies tag, etc)
        cutoff = asm3.i18n.subtract_days(asm3.i18n.now(self.dbo.timezone), periodindays)
        sql = "%s WHERE a.ActiveMovementType IN (1,2) " \
            "AND a.ActiveMovementDate >= ? AND a.DeceasedDate Is Null AND a.NonShelterAnimal = 0 " \
            "AND NOT EXISTS(SELECT AnimalID FROM animalpublished WHERE AnimalID = a.ID AND PublishedTo = 'maddiesfund' AND SentDate >= %s) " \
            "ORDER BY a.ID" % (asm3.animal.get_animal_query(self.dbo), self.dbo.sql_greatest(["a.ActiveMovementDate", "a.LastChangedDate"]))
        animals = self.dbo.query(sql, [cutoff], distincton="ID")

        # Now find animals who have been sent previously and are now deceased (using sent date against deceased to prevent re-sends) 
        sql = "%s WHERE a.DeceasedDate Is Not Null AND a.DeceasedDate >= ? AND " \
            "EXISTS(SELECT AnimalID FROM animalpublished WHERE AnimalID = a.ID AND " \
            "PublishedTo = 'maddiesfund' AND SentDate <= a.DeceasedDate)" % asm3.animal.get_animal_query(self.dbo)
        animals += self.dbo.query(sql, [cutoff], distincton="ID")

        # Now find shelter animals who have been sent previously and are back (using sent date against return to prevent re-sends)
        sql = "%s WHERE a.Archived = 0 AND " \
            "EXISTS(SELECT AnimalID FROM animalpublished WHERE AnimalID = a.ID AND " \
            "PublishedTo = 'maddiesfund' AND SentDate < " \
            "(SELECT MAX(ReturnDate) FROM adoption WHERE AnimalID = a.ID AND MovementType IN (1,2) AND ReturnDate Is Not Null))" % asm3.animal.get_animal_query(self.dbo)
        animals += self.dbo.query(sql, distincton="ID")

        # Now find animals who have been sent previously and have a new/changed vaccination since then
        sql = "%s WHERE a.Archived = 0 AND " \
            "EXISTS(SELECT p.AnimalID FROM animalpublished p INNER JOIN animalvaccination av ON av.AnimalID = a.ID WHERE p.AnimalID = a.ID AND " \
            "p.PublishedTo = 'maddiesfund' AND (p.SentDate < av.CreatedDate OR p.SentDate < av.LastChangedDate))" % asm3.animal.get_animal_query(self.dbo)
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

        csv = [ "FirstName,Lastname,EmailAddress,City,State,Street,Apartment,Zipcode," \
            "ContactNumber,PetName,PetSpecies,PetSex,Breed,FosterCareDate,FosterEndDate," \
            "Organization,Color,Photo,DateofBirth" ]

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

        fname = "%s_%s.csv" % ( token, asm3.i18n.format_date("%Y%m%d%H%M%S", asm3.i18n.now()) )
        # Upload the datafile
        self.saveFile(os.path.join(self.publishDir, fname), "\n".join(csv))
        self.log("Uploading datafile, %s" % fname)
        self.upload(fname)
        self.log("Uploaded %s" % fname)
        self.log("-- FILE DATA -- (csv)")
        self.log("\n".join(csv))
        self.cleanup()

    def processAnimal(self, an):
        """ Builds a CSV row """
        l = self.dbo.locale
        # FirstName,Lastname,EmailAddress,Street,City,State,Zipcode,ContactNumber,
        # PetID,PetName,PetSpecies,PetSex,Breed,DateofBirth,Color,
        # Status,EventDate,EventType,Organization,Photo
        line = [
            an.CURRENTOWNERFORENAMES,
            an.CURRENTOWNERSURNAME,
            an.CURRENTOWNEREMAILADDRESS,
            an.CURRENTOWNERADDRESS,
            an.CURRENTOWNERTOWN,
            an.CURRENTOWNERCOUNTY,
            an.CURRENTOWNERPOSTCODE,
            an.CURRENTOWNERMOBILETELEPHONE,
            an.SHELTERCODE,
            an.ANIMALNAME,
            an.SPECIESNAME,
            an.SEXNAME,
            an.BREEDNAME,
            asm3.i18n.python2display(l, an.DATEOFBIRTH),
            an.BASECOLOURNAME,
            self.getPetStatus(an),
            asm3.i18n.python2display(l, an.ACTIVEMOVEMENTDATE),
            self.getEventType(an),
            asm3.configuration.organisation(self.dbo),
            "%s?method=animal_image&account=%s&animalid=%s" % (SERVICE_URL, self.dbo.database, an.ID)
        ]
        return self.csvLine(line)
