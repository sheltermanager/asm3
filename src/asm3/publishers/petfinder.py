
import asm3.cachedisk
import asm3.configuration
import asm3.i18n
import asm3.medical

from .base import FTPPublisher
from asm3.sitedefs import PETFINDER_FTP_HOST, PETFINDER_SEND_PHOTOS_BY_FTP
from asm3.typehints import datetime, Database, Dict, List, PublishCriteria, ResultRow, Results

import os
import sys

class PetFinderPublisher(FTPPublisher):
    """
    Handles publishing to PetFinder.com
    """
    cache_invalidation_keys = {}

    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.forceReupload = True
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        publishCriteria.checkSocket = True
        publishCriteria.scaleImages = 1
        publishCriteria.uploadAllImages = True
        FTPPublisher.__init__(self, dbo, publishCriteria, 
            PETFINDER_FTP_HOST, asm3.configuration.petfinder_user(dbo), 
            asm3.configuration.petfinder_password(dbo))
        self.initLog("petfinder", "PetFinder Publisher")

    def pfAnimalQuery(self) -> str:
        return "SELECT a.ID, a.ShelterCode, a.AnimalName, a.BreedID, a.Breed2ID, a.CrossBreed, a.Sex, a.Size, a.DateOfBirth, a.MostRecentEntryDate, a.Fee, " \
            "b1.BreedName AS BreedName1, b2.BreedName AS BreedName2, " \
            "b1.PetFinderBreed, b2.PetFinderBreed AS PetFinderBreed2, s.PetFinderSpecies, " \
            "a.EntryTypeID, et.EntryTypeName AS EntryTypeName, er.ReasonName AS EntryReasonName, " \
            "a.AnimalComments, a.AnimalComments AS WebsiteMediaNotes, a.IsNotAvailableForAdoption, " \
            "a.Neutered, a.IsGoodWithDogs, a.IsGoodWithCats, a.IsGoodWithChildren, a.IsHouseTrained, a.IsCourtesy, a.Declawed, a.CrueltyCase, a.HasSpecialNeeds " \
            "FROM animal a " \
            "INNER JOIN breed b1 ON a.BreedID = b1.ID " \
            "INNER JOIN breed b2 ON a.Breed2ID = b2.ID " \
            "INNER JOIN species s ON a.SpeciesID = s.ID " \
            "LEFT OUTER JOIN lksentrytype et ON a.EntryTypeID = et.ID " \
            "LEFT OUTER JOIN entryreason er ON a.EntryReasonID = er.ID "

    def pfDate(self, d: datetime) -> str:
        """ Returns a CSV entry for a date in YYYY-MM-DD """
        return "\"%s\"" % asm3.i18n.format_date(d, "%Y-%m-%d")

    def pfYesNo(self, condition: bool) -> str:
        """
        Returns a CSV entry for yes or no based on the condition
        """
        if condition:
            return "\"1\""
        else:
            return "\"\""

    def pfNotGoodWith(self, v: int) -> str:
        """
        Returns a CSV entry for yes, no, unknown based on the value.
        In our scheme v is one of Yes=0, No=1, Unknown=2, Selective=3
        In their scheme since it's notGood, Yes=0, No=1, Unknown="", Selective=""
        """
        if v >= 2:
            return "\"\""
        elif v == 1:
            return "\"1\""
        else:
            return "\"0\""

    def pfImageUrl(self, animalid: int, urls: List[str], index: int) -> str:
        """
        Returns image URL index from urls, returning an empty string if it does not exist.
        """
        try:
            key = ""
            if animalid in self.cache_invalidation_keys: 
                key = "&key=%s" % self.cache_invalidation_keys[animalid]
            return "%s%s" % (urls[index], key)
        except IndexError:
            return ""

    def pfRecordIn(self, animals: Results, aid: int) -> bool:
        """
        Returns true if aid exists in the ID field of all the rows in animals.
        """
        for a in animals:
            if a.ID == aid:
                return True
        return False
    
    def pfGetCacheInvalidationKeys(self) -> Dict[int, str]:
        """ Returns the list of cache invalidation keys - a dictionary with animal ID as the key """
        cik = asm3.cachedisk.get("pfcikeys", self.dbo.database, dict)
        if cik is None:
            return {}
        return cik
    
    def pfUpdateCacheInvalidationKeys(self, animals) -> Dict[int, str]:
        """
        PetFinder have a broken cache implementation. They record photo URLs that they've seen before
        and will not retrieve them again. When they delete a listing though, they do not remove URLs 
        from this seen list, which means if an animal is not published in a run and then published
        later, it will not have any images.
        We could have gotten around this by setting a timestamp of today's date or something, but that
        would not only fill their cache, it will invalidate any CDN we are using (but not the file
        cache backing our service call).
        This function uses a dictionary that we persist to the disk cache, it contains a list of all
        currently adoptable animals and a unique key to send with their photo URLs.
        This function will strip anyone from the list that does not appear in the adoptable set animals,
        and it will add anyone who doesn't appear in the list with a new key.
        What this effectively does is make sure that animals who are published continually have the same
        key, but the moment an animal is not published, its key is removed so that it will get a new
        one if it is published again - invalidating PetFinder's cache for them.
        """
        cik = self.pfGetCacheInvalidationKeys()
        adoptable_ids = set([a.ID for a in animals])
        # Remove anyone from the dict who is not adoptable
        for k, v in cik.copy().items():
            if k not in adoptable_ids:
                del cik[k]
        # Add any new animals to the list and generate a key for them
        for a in animals:
            if a.ID in cik: continue
            cik[a.ID] = asm3.utils.epoch_b32()
        # Persist the dictionary
        asm3.cachedisk.put("pfcikeys", self.dbo.database, cik, 86400*7)
        return cik

    def run(self) -> None:

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
        if not self.isChangedSinceLastPublish():
            self.logSuccess("No animal/movement changes have been made since last publish")
            self.setLastError("No animal/movement changes have been made since last publish", log_error = False)
            self.cleanup()
            return

        shelterid = asm3.configuration.petfinder_user(self.dbo)
        if shelterid == "":
            self.setLastError("No PetFinder.com shelter id has been set.")
            self.cleanup()
            return

        # NOTE: We still publish even if there are no adoptable animals. 
        # This prevents situations where the last animal can't be removed 
        # from PetFinder because the shelterhas no animals to send.
        animals = self.getMatchingAnimals(includeAdditionalFields=True)
        if len(animals) == 0:
            self.log("No animals found to publish, sending empty file.")

        if not self.openFTPSocket(): 
            self.setLastError("Failed opening FTP socket.")
            if self.logSearch("530 Login") != -1:
                self.log("Found 530 Login incorrect: disabling PetFinder publisher.")
                asm3.configuration.publishers_enabled_disable(self.dbo, "pf")
            self.cleanup()
            return

        # Make sure necessary folders exist
        self.mkdir("import")
        self.chdir("import", "import")
        self.mkdir("photos")
        self.chdir("photos", "import/photos")

        # Build a list of age bands for petfinder ages. It's
        # a list of integers in days for each band.
        # The defaults are 6 months, 2 years and 9 years. 
        agebands = asm3.configuration.petfinder_age_bands(self.dbo)
        if agebands == "" or len(agebands.split(",")) != 3:
            agebands = "182,730,3285"
        agebands = [ int(i) for i in agebands.split(",") ]

        # It's part of PetFinder's TOS that they will not list animals that
        # are either unaltered, or the shelter will not pre-pay the cost
        # of sterilisation after adoption.
        # At least one of our customers cannot offer this, using a deposit
        # scheme instead which is not covered. They still want to display 
        # unaltered animals on their own website, so the single "Include unaltered" 
        # publishing option is not enough for them. We need an extra
        # config switch to prevent sending unaltered animals to PetFinder
        # in these cases.
        hide_unaltered = asm3.configuration.petfinder_hide_unaltered(self.dbo)

        # If the size field has been hidden, just send "M" to PetFinder because
        # it's mandatory for them, but the user can't see the value in their
        # data and if they picked an unusual default size it will look weird.
        hide_size = asm3.configuration.dont_show_size(self.dbo)

        # set/prune the cache invalidation keys for the photo urls we are going
        # to send to PetFinder for our adoptable animals
        self.cache_invalidation_keys = self.pfUpdateCacheInvalidationKeys(animals)

        csv = [ "ID,Internal,AnimalName,PrimaryBreed,SecondaryBreed,Sex,Size,Age,Desc,Type,Status," \
            "Shots,Altered,NoDogs,NoCats,NoKids,Housetrained,Declawed,specialNeeds,Mix," \
            "photo1,photo2,photo3,photo4,photo5,photo6,arrival_date,birth_date," \
            "primaryColor,secondaryColor,tertiaryColor,coat_length," \
            "adoption_fee,display_adoption_fee,adoption_fee_waived," \
            "special_needs_notes,no_other,no_other_note,tags" ]

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

                if PETFINDER_SEND_PHOTOS_BY_FTP:
                    self.uploadImages(an, False, 3)

                if hide_unaltered and an.NEUTERED == 0:
                    self.log("%s is unaltered and petfinder_hide_unaltered == true" % an["ANIMALNAME"])
                    continue

                csv.append( self.processAnimal(an, agebands, hide_size = hide_size) )

                # Mark success in the log
                self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals, first=True)

        # Is the option to send strays on?
        if asm3.configuration.petfinder_send_strays(self.dbo):
            rows = self.dbo.query("%s WHERE a.Archived=0 AND a.HasPermanentFoster=0 AND a.HasTrialAdoption=0 AND a.EntryTypeID=2" % self.pfAnimalQuery())
            for an in rows:
                if self.pfRecordIn(animals, an.ID): continue # do not re-send adoptable animals
                csv.append( self.processAnimal(an, agebands, status = "F", hide_size = hide_size) )

        # Is the option to send holds on?
        if asm3.configuration.petfinder_send_holds(self.dbo):
            rows = self.dbo.query("%s WHERE a.Archived=0 AND a.IsHold=1" % self.pfAnimalQuery())
            for an in rows:
                if self.pfRecordIn(animals, an.ID): continue # do not re-send adoptable animals
                # TODO: Do we need to exclude animals we just sent as strays?
                csv.append( self.processAnimal(an, agebands, status = "H", hide_size = hide_size ) )

        # Is the option to send previous adoptions on?
        if asm3.configuration.petfinder_send_adopted(self.dbo):
            rows = self.dbo.query("%s WHERE a.Archived=1 AND a.ActiveMovementType=1" % self.pfAnimalQuery())
            for an in rows:
                csv.append( self.processAnimal(an, agebands, status = "X", hide_size = hide_size ) )

        # Upload the datafile
        self.chdir("..", "import")
        self.saveFile(os.path.join(self.publishDir, shelterid), "\n".join(csv))
        self.log("Uploading datafile, %s" % shelterid)
        self.upload(shelterid)
        self.log("Uploaded %s" % shelterid)
        self.log("-- FILE DATA -- (csv)")
        self.log("\n".join(csv))
        self.cleanup()

    def processAnimal(self, an: ResultRow, agebands: List[int] = [ 182, 730, 3285 ], status: str = "A", hide_size: bool = False) -> str:
        """ Processes an animal and returns a CSV line """
        primary_color = ""
        secondary_color = ""
        tertiary_color = ""
        coat_length = ""
        adoption_fee_waived = ""
        special_needs_notes = ""
        if "PFPRIMARYCOLOR" in an: primary_color = an.PFPRIMARYCOLOR
        if "PFSECONDARYCOLOR" in an: secondary_color = an.PFSECONDARYCOLOR
        if "PFTERTIARYCOLOR" in an: tertiary_color = an.PFTERTIARYCOLOR
        if "PFCOATLENGTH" in an: coat_length = an.PFCOATLENGTH
        if "PFADOPTIONFEEWAIVED" in an: adoption_fee_waived = an.PFADOPTIONFEEWAIVED
        if "PFSPECIALNEEDSNOTES" in an: special_needs_notes = an.PFSPECIALNEEDSNOTES
        line = []
        # This specific CSV ordering has been mandated by PetFinder in their import docs of August 2019
        # ID
        line.append(an.SHELTERCODE)
        # Internal
        line.append(an.SHELTERCODE)
        # AnimalName
        line.append(an.ANIMALNAME)
        # PrimaryBreed
        line.append(an.PETFINDERBREED)
        # SecondaryBreed
        line.append(self.getPublisherBreed(an, 2))
        # Sex, one of M or F
        sexname = "M"
        if an.SEX == 0: sexname = "F"
        line.append(sexname)
        # Size, one of S, M, L, XL
        ansize = "M"
        if hide_size: ansize = "M"
        elif an.SIZE == 0: ansize = "XL"
        elif an.SIZE == 1: ansize = "L"
        elif an.SIZE == 2: ansize = "M"
        elif an.SIZE == 3: ansize = "S"
        line.append(ansize)
        # Age, one of Adult, Baby, Senior and Young
        ageindays = asm3.i18n.date_diff_days(an.DATEOFBIRTH, asm3.i18n.now(self.dbo.timezone))
        agename = "Adult"
        if ageindays < agebands[0]: agename = "Baby"
        elif ageindays < agebands[1]: agename = "Young"
        elif ageindays < agebands[2]: agename = "Adult"
        else: agename = "Senior"
        line.append(agename)
        # Description
        line.append(self.getDescription(an, crToHE=True, replaceSmart=True))
        # Type (Species)
        line.append(an.PETFINDERSPECIES)
        # Status
        line.append(status)
        # Shots
        if status != "X":
            # Only look up this value and send it for non-adopted animals (status==X is adopted)
            # so that the quickest possible query hitting the fewest tables can be run to get that data
            line.append(self.pfYesNo(asm3.medical.get_vaccinated(self.dbo, int(an.ID))))
        else:
            line.append("")
        # Altered
        line.append(self.pfYesNo(an.NEUTERED == 1))
        # No Dogs
        line.append(self.pfNotGoodWith(an.ISGOODWITHDOGS))
        # No Cats
        line.append(self.pfNotGoodWith(an.ISGOODWITHCATS))
        # No Kids
        line.append(self.pfNotGoodWith(an.ISGOODWITHCHILDREN))
        # Housetrained
        line.append(self.pfYesNo(an.ISHOUSETRAINED == 0))
        # Declawed
        line.append(self.pfYesNo(an.DECLAWED == 1))
        # Special needs
        if an.CRUELTYCASE == 1:
            line.append("1")
        elif an.HASSPECIALNEEDS == 1:
            line.append("1")
        else:
            line.append("")
        # Mix
        line.append(self.pfYesNo(an.CROSSBREED == 1))
        # photo1-6
        if PETFINDER_SEND_PHOTOS_BY_FTP:
            # Send blanks for the 6 images if we already sent them by FTP
            line.append("")
            line.append("")
            line.append("")
            line.append("")
            line.append("")
            line.append("")
        elif status == "X":
            # Only send the preferred image for adopted animals
            line.append(self.getPhotoUrl(an.ID))
            line.append("")
            line.append("")
            line.append("")
            line.append("")
            line.append("")
        else:
            urls = self.getPhotoUrls(an.ID)
            line.append(self.pfImageUrl(an.ID, urls, 0)) # photo1
            line.append(self.pfImageUrl(an.ID, urls, 1)) # photo2
            line.append(self.pfImageUrl(an.ID, urls, 2)) # photo3
            line.append(self.pfImageUrl(an.ID, urls, 3)) # photo4
            line.append(self.pfImageUrl(an.ID, urls, 4)) # photo5
            line.append(self.pfImageUrl(an.ID, urls, 5)) # photo6
        # Arrival Date
        line.append(self.pfDate(an.MOSTRECENTENTRYDATE))
        # Birth Date
        line.append(self.pfDate(an.DATEOFBIRTH))
        # primaryColor
        line.append(primary_color)
        # secondaryColor
        line.append(secondary_color)
        # tertiaryColor
        line.append(tertiary_color)
        # coat_length
        line.append(coat_length)
        # Adoption Fee
        adoptionfee = asm3.utils.cint(an.FEE)
        if adoptionfee > 0:
            line.append("%0.2f" % (adoptionfee / 100))
        else:
            line.append("") # send 0 fees as a blank as PF seem to ignore their own display adoption fee flag below
        # Display adoption fee?
        line.append(self.pfYesNo(an.FEE is not None and an.FEE > 0))
        # Adoption fee waived
        line.append(adoption_fee_waived)
        # Special Needs Notes 
        line.append(special_needs_notes)
        # No Other pets?
        line.append((self.pfYesNo(False)))
        # No Other Note
        line.append("")
        # Tags
        line.append("")
        return self.csvLine(line)

    def clearListings(self) -> str:
        """
        We've had many issues in the past caused by people sending the wrong images and
        then finding they can't update them. This process sends a blank file to PetFinder
        to remove all the existing listings (so any existing images are forgotten). It
        then touches the access date on all the publishable images for adoptable animals
        so that PetFinder will get a new URL for them and download them again.
        The return value is the publishing log.
        """
                
        self.log("PetFinderPublisher clearing listings ...")

        shelterid = asm3.configuration.petfinder_user(self.dbo)
        if shelterid == "":
            raise Exception("No PetFinder.com shelter id has been set.")

        if not self.openFTPSocket(): 
            raise Exception("Failed opening FTP socket.")

        # Touch all the date fields of publishable media for adoptable animals 
        # so that they get a different photo URL due to the timestamp so PetFinder will 
        # retrieve them again
        self.dbo.execute("UPDATE media SET Date=? WHERE LinkTypeID=0 AND LinkID IN (SELECT ID FROM animal WHERE Adoptable=1) AND ExcludeFromPublish=0", 
            [ self.dbo.now() ])

        csv = [ "ID,Internal,AnimalName,PrimaryBreed,SecondaryBreed,Sex,Size,Age,Desc,Type,Status," \
            "Shots,Altered,NoDogs,NoCats,NoKids,Housetrained,Declawed,specialNeeds,Mix," \
            "photo1,photo2,photo3,photo4,photo5,photo6,arrival_date,birth_date," \
            "primaryColor,secondaryColor,tertiaryColor,coat_length," \
            "adoption_fee,display_adoption_fee,adoption_fee_waived," \
            "special_needs_notes,no_other,no_other_note,tags" ]

        # Upload the empty datafile
        self.chdir("import", "import")
        self.saveFile(os.path.join(self.publishDir, shelterid), "\n".join(csv))
        self.log("Uploading datafile, %s" % shelterid)
        self.upload(shelterid)
        self.log("Uploaded %s" % shelterid)
        self.log("-- FILE DATA -- (csv)")
        self.log("\n".join(csv))
        self.cleanup()
        return "\n".join(self.logBuffer)


