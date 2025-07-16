
import asm3.configuration
import asm3.i18n
import asm3.lostfound

from .base import FTPPublisher
from asm3.sitedefs import PETFBI_FTP_HOST
from asm3.typehints import Database, PublishCriteria, ResultRow, Results

import os
import sys

class PetFBIPublisher(FTPPublisher):
    """
    Handles publishing to petfbi.org
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        l = dbo.locale
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        publishCriteria.checkSocket = True
        publishCriteria.scaleImages = 1
        FTPPublisher.__init__(self, dbo, publishCriteria, 
            PETFBI_FTP_HOST, asm3.configuration.petfbi_user(dbo), 
            asm3.configuration.petfbi_password(dbo), ftptls=True)
        self.initLog("petfbi", asm3.i18n._("PetFBI Publisher", l))

    def fbiGetFound(self) -> Results:
        return asm3.lostfound.get_foundanimal_find_simple(self.dbo)
    
    def fbiGetLost(self) -> Results:
        return asm3.lostfound.get_lostanimal_find_simple(self.dbo)
    
    def fbiGetStrayHold(self) -> Results:

        return self.dbo.query(f"{self.fbiQuery()} WHERE a.Archived=0 AND a.CrueltyCase=0 AND a.HasPermanentFoster=0 " \
            "AND a.HasTrialAdoption=0 AND a.EntryTypeID=2 AND a.IsHold=1")

    def fbiQuery(self) -> str:
        return "SELECT a.ID, a.ShelterCode, a.AnimalName, a.BreedID, a.Breed2ID, a.CrossBreed, x.Sex AS SexName, a.Size, " \
            "a.DateOfBirth, a.MostRecentEntryDate, a.Fee, a.PickupAddress, a.LastChangedDate, " \
            "b1.BreedName AS BreedName1, b2.BreedName AS BreedName2, s.SpeciesName, c.BaseColour AS BaseColourName, " \
            "a.EntryTypeID, et.EntryTypeName AS EntryTypeName, er.ReasonName AS EntryReasonName, " \
            "a.AnimalComments, a.AnimalComments AS WebsiteMediaNotes, a.HealthProblems, a.IsNotAvailableForAdoption, " \
            "a.Neutered, a.IsGoodWithDogs, a.IsGoodWithCats, a.IsGoodWithChildren, a.IsHouseTrained, a.IsCourtesy, a.Declawed, a.CrueltyCase, a.HasSpecialNeeds, " \
            "web.ID AS WebsiteMediaID, web.MediaName AS WebsiteMediaName, web.Date AS WebsiteMediaDate, " \
            "1 AS RecentlyChangedImages " \
            "FROM animal a " \
            "INNER JOIN breed b1 ON a.BreedID = b1.ID " \
            "INNER JOIN breed b2 ON a.Breed2ID = b2.ID " \
            "INNER JOIN species s ON a.SpeciesID = s.ID " \
            "INNER JOIN basecolour c ON a.BaseColourID = c.ID " \
            "INNER JOIN lksex x ON a.Sex = x.ID " \
            "LEFT OUTER JOIN lksentrytype et ON a.EntryTypeID = et.ID " \
            "LEFT OUTER JOIN entryreason er ON a.EntryReasonID = er.ID " \
            "LEFT OUTER JOIN media web ON web.ID = (SELECT MAX(ID) FROM media sweb WHERE sweb.LinkID = a.ID AND sweb.LinkTypeID = 0 AND sweb.WebsitePhoto = 1) "

    def fbiYesNo(self, condition: bool) -> str:
        """
        Returns a CSV entry for yes or no based on the condition
        """
        if condition:
            return "\"Yes\""
        else:
            return "\"No\""

    def run(self) -> None:
        
        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        shelterid = asm3.configuration.petfbi_orgid(self.dbo)
        if shelterid == "":
            self.setLastError("No petfbi.org organisation ID has been set.")
            return
        
        animals = self.fbiGetStrayHold()
        foundanimals = self.fbiGetFound()
        lostanimals = self.fbiGetLost()

        if len(animals) == 0 and len(foundanimals) == 0:
            self.logSuccess("No animals found to publish.")
            self.setLastError("No animals found to publish.", log_error = False)
            self.cleanup()
            return

        if not self.openFTPSocket(): 
            self.setLastError("Failed opening FTP socket.")
            if self.logSearch("530 Login") != -1:
                self.log("Found 530 Login incorrect: disabling PetFBI publisher.")
                asm3.configuration.publishers_enabled_disable(self.dbo, "hlp")
            self.cleanup()
            return

        csv = []

        # Lost Animals
        anCount = 0
        for an in lostanimals:
            try:
                anCount += 1
                self.log("Processing Lost Animal: %d: %s (%d of %d)" % ( an["ID"], an["COMMENTS"], anCount, len(lostanimals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return
                
                # Upload one image for this animal
                self.uploadImage(an, an["WEBSITEMEDIAID"], an["WEBSITEMEDIANAME"], "LOST" + an["ID"] + ".jpg")

                csv.append( self.processLostAnimal(an, shelterid) )

                # Mark success in the log
                self.logSuccess("Processed Lost Animal: %d: %s (%d of %d)" % ( an["ID"], an["COMMENTS"], anCount, len(lostanimals)))

            except Exception as err:
                self.logError("Failed processing lost animal: %s, %s" % (str(an["ID"]), err), sys.exc_info())

        # Found Animals
        anCount = 0
        for an in foundanimals:
            try:
                anCount += 1
                self.log("Processing Found Animal: %d: %s (%d of %d)" % ( an["ID"], an["COMMENTS"], anCount, len(foundanimals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return
                
                # Upload one image for this animal
                self.uploadImage(an, an["WEBSITEMEDIAID"], an["WEBSITEMEDIANAME"], "FOUND" + an["ID"] + ".jpg")

                csv.append( self.processFoundAnimal(an, shelterid) )

                # Mark success in the log
                self.logSuccess("Processed Found Animal: %d: %s (%d of %d)" % ( an["ID"], an["COMMENTS"], anCount, len(foundanimals)))

            except Exception as err:
                self.logError("Failed processing found animal: %s, %s" % (str(an["ID"]), err), sys.exc_info())

        # Animals
        anCount = 0
        for an in animals:
            try:
                anCount += 1
                self.log("Processing Stray/Hold: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return

                # Upload one image for this animal
                self.uploadImage(an, an["WEBSITEMEDIAID"], an["WEBSITEMEDIANAME"], an["SHELTERCODE"] + ".jpg")

                csv.append( self.processAnimal(an, shelterid) )

                # Mark success in the log
                self.logSuccess("Processed Stray/Hold: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals)

        header = "OrgID,PetID,Status,Name,Species,Sex,PrimaryBreed,SecondaryBreed,Age,Altered,Size,ZipPostal,Description,Photo,Colour,MedicalConditions,IntakeDate,PickupAddress,LastUpdated\n"
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

    def processFoundAnimal(self, an: ResultRow, shelterid: str = "") -> str:
        """
        Processes a found animal and returns a CSV line
        """
        line = []
        # OrgID
        line.append(shelterid)
        # PetID
        line.append("F%s" % an.ID)
        # Status
        line.append("Found")
        # Name
        line.append(str(an.ID))
        # Species
        line.append(an.SPECIESNAME)
        # Sex
        line.append(an.SEXNAME)
        # PrimaryBreed
        line.append(an.BREEDNAME)
        # SecondaryBreed
        line.append("")
        # Age, one of Baby, Young, Adult, Senior - just happens to match our default age groups
        line.append(an.AGEGROUP)
        # Altered - don't have
        line.append("")
        # Size, one of Small, Medium or Large or X-Large - also don't have
        line.append("")
        # ZipPostal
        line.append(an.AREAPOSTCODE)
        # Description
        notes = str(an.DISTFEAT) + "\n" + str(an.COMMENTS)
        # Strip carriage returns
        notes = notes.replace("\r\n", "<br />")
        notes = notes.replace("\r", "<br />")
        notes = notes.replace("\n", "<br />")
        notes = notes.replace("\"", "&ldquo;")
        notes = notes.replace("'", "&lsquo;")
        notes = notes.replace("`", "&lsquo;")
        line.append(notes)
        # Photo
        line.append("")
        # Colour
        line.append(an.BASECOLOURNAME)
        # MedicalConditions
        line.append("")
        # IntakeDate
        line.append(str(asm3.i18n.python2unix(an.DATEFOUND)))
        # PickupAddress
        line.append(an.AREAFOUND)
        # LastUpdated
        line.append(str(asm3.i18n.python2unix(an.LASTCHANGEDDATE)))
        return self.csvLine(line)
    
    def processLostAnimal(self, an: ResultRow, shelterid: str = "") -> str:
        """
        Processes a lost animal and returns a CSV line
        """
        line = []
        # OrgID
        line.append(shelterid)
        # PetID
        line.append("L%s" % an.ID)
        # Status
        line.append("Lost")
        # Name
        line.append(str(an.ID))
        # Species
        line.append(an.SPECIESNAME)
        # Sex
        line.append(an.SEXNAME)
        # PrimaryBreed
        line.append(an.BREEDNAME)
        # SecondaryBreed
        line.append("")
        # Age, one of Baby, Young, Adult, Senior - just happens to match our default age groups
        line.append(an.AGEGROUP)
        # Altered - don't have
        line.append("")
        # Size, one of Small, Medium or Large or X-Large - also don't have
        line.append("")
        # ZipPostal
        line.append(an.AREAPOSTCODE)
        # Description
        notes = str(an.DISTFEAT) + "\n" + str(an.COMMENTS)
        # Strip carriage returns
        notes = notes.replace("\r\n", "<br />")
        notes = notes.replace("\r", "<br />")
        notes = notes.replace("\n", "<br />")
        notes = notes.replace("\"", "&ldquo;")
        notes = notes.replace("'", "&lsquo;")
        notes = notes.replace("`", "&lsquo;")
        line.append(notes)
        # Photo
        line.append("")
        # Colour
        line.append(an.BASECOLOURNAME)
        # MedicalConditions
        line.append("")
        # IntakeDate
        line.append(str(asm3.i18n.python2unix(an.DATELOST)))
        # PickupAddress
        line.append(an.AREALOST)
        # LastUpdated
        line.append(str(asm3.i18n.python2unix(an.LASTCHANGEDDATE)))
        return self.csvLine(line)

    def processAnimal(self, an: ResultRow, shelterid: str = "") -> str:
        """ Process an animal record and return a CSV line """
        line = []
        # OrgID
        line.append(shelterid)
        # PetID
        line.append("A%s" % an.ID)
        # Status
        line.append("Stray")
        # Name
        line.append(an.ANIMALNAME)
        # Species
        line.append(an.SPECIESNAME)
        # Sex
        line.append(an.SEXNAME)
        # PrimaryBreed
        line.append(an.BREEDNAME1)
        # SecondaryBreed
        if an.CROSSBREED == 1:
            line.append(an.BREEDNAME2)
        else:
            line.append("")
        # Age, one of Baby, Young, Adult, Senior
        ageinyears = asm3.i18n.date_diff_days(an.DATEOFBIRTH, asm3.i18n.now(self.dbo.timezone))
        ageinyears /= 365.0
        agename = "Adult"
        if ageinyears < 0.5: agename = "Baby"
        elif ageinyears < 2: agename = "Young"
        elif ageinyears < 9: agename = "Adult"
        else: agename = "Senior"
        line.append(agename)
        # Altered
        line.append(self.fbiYesNo(an.NEUTERED == 1))
        # Size, one of Small, Medium or Large or X-Large
        ansize = "Medium"
        if an.SIZE == 0 : ansize = "X-Large"
        elif an.SIZE == 1: ansize = "Large"
        elif an.SIZE == 2: ansize = "Medium"
        elif an.SIZE == 3: ansize = "Small"
        line.append(ansize)
        # ZipPostal
        line.append(asm3.configuration.organisation_postcode(self.dbo))
        # Description
        line.append(self.getDescription(an, True))
        # Photo
        line.append(an.SHELTERCODE)
        # Colour
        line.append(an.BASECOLOURNAME)
        # MedicalConditions
        line.append(an.HEALTHPROBLEMS)
        # IntakeDate
        line.append(str(asm3.i18n.python2unix(an.MOSTRECENTENTRYDATE)))
        # PickupAddress
        line.append(an.PICKUPADDRESS)
        # LastUpdated
        line.append(str(asm3.i18n.python2unix(an.LASTCHANGEDDATE)))
        return self.csvLine(line)

