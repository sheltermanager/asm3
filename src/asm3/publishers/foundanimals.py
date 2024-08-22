
import asm3.configuration
import asm3.i18n
import asm3.utils

from .base import FTPPublisher, get_microchip_data
from asm3.sitedefs import FOUNDANIMALS_FTP_HOST, FOUNDANIMALS_FTP_USER, FOUNDANIMALS_FTP_PASSWORD
from asm3.typehints import Database, PublishCriteria, ResultRow

import os, sys

VALIDATE_YES = 0
VALIDATE_NO = 1
VALIDATE_FAIL = 2

class FoundAnimalsPublisher(FTPPublisher):
    """
    Handles publishing to foundanimals (now 24pet/foundanimals)
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        FTPPublisher.__init__(self, dbo, publishCriteria, 
            FOUNDANIMALS_FTP_HOST, FOUNDANIMALS_FTP_USER, FOUNDANIMALS_FTP_PASSWORD, ftptls=True)
        self.initLog("foundanimals", "FoundAnimals/24Pet Publisher")

    def run(self) -> None:
        
        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        org = asm3.configuration.organisation(self.dbo)
        folder = asm3.configuration.foundanimals_folder(self.dbo)
        cutoffdays = asm3.configuration.foundanimals_cutoff_days(self.dbo)
        if cutoffdays == 0: cutoffdays = -1095 # default cutoff is 3 years, note that it's a negative number

        if folder == "":
            self.setLastError("No FoundAnimals/24Pet folder has been set.")
            self.cleanup()
            return
        
        email = asm3.configuration.foundanimals_email(self.dbo)
        if email == "":
            self.setLastError("No FoundAnimals/24Pet group email has been set.")
            self.cleanup()
            return

        animals = get_microchip_data(self.dbo, ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], "foundanimals", allowintake=True, organisation_email=email)
        if len(animals) == 0:
            self.setLastError("No microchips found to register.")
            self.cleanup(save_log=False)
            return

        if not self.openFTPSocket(): 
            self.setLastError("Failed to open FTP socket.")
            # INFO: This makes no sense as the user is not in control of the FTP
            # credentials to found. Their FTP service failed recently and as a 
            # result all customers stopped sending to found
            # if self.logSearch("530 Login") != -1:
            #    self.log("Found 530 Login incorrect: disabling FoundAnimals publisher.")
            #    asm3.configuration.publishers_enabled_disable(self.dbo, "fa")
            self.cleanup()
            return

        # foundanimals.org want data files called mmddyyyy_HHMMSS.csv in the shelter's own folder
        dateportion = asm3.i18n.format_date(asm3.i18n.now(self.dbo.timezone), "%m%d%Y_%H%M%S")
        outputfile = "%s.csv" % dateportion

        folder = folder.strip() # Users frequently put spaces at the beginning when entering the folder name
        self.mkdir(folder)
        if not self.chdir(folder, folder):
            self.setLastError("Failed issuing chdir to '%s'" % folder)
            self.cleanup()
            return

        csv = []

        anCount = 0
        success = []
        fail = []
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

                v = self.validate(an, cutoffdays)
                if v == VALIDATE_NO: 
                    continue
                elif v == VALIDATE_YES:
                    csv.append( self.processAnimal(an, org, email) )
                    success.append(an)
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( \
                        an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                elif v == VALIDATE_FAIL:
                    fail.append(an)

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(success)
        self.markAnimalsPublishFailed(fail)

        # Bail if we didn't have anything to do
        if len(csv) == 0:
            self.log("No data left to send to foundanimals")
            self.cleanup()
            return

        header = "First Name,Last Name,Email Address,Address 1,Address 2,City,State,Zip Code," \
            "Home Phone,Work Phone,Cell Phone,Pet Name,Microchip Number,Service Date," \
            "Date of Birth,Species,Sex,Spayed/Neutered,Primary Breed,Secondary Breed," \
            "Color,Implanting Organization,Rescue Group Email\n"
        self.saveFile(os.path.join(self.publishDir, outputfile), header + "\n".join(csv))
        self.log("Uploading datafile %s" % outputfile)
        self.upload(outputfile)
        self.log("Uploaded %s" % outputfile)
        self.log("-- FILE DATA --")
        self.log(header + "\n".join(csv))
        self.cleanup()

    def processAnimal(self, an: ResultRow, org: str = "", email: str = "") -> str:
        """
        Return an animal as a line of the CSV to be submitted
        """
        line = []
        servicedate = an["ACTIVEMOVEMENTDATE"] or an["MOSTRECENTENTRYDATE"]
        if an["NONSHELTERANIMAL"] == 1: servicedate = an["IDENTICHIPDATE"]
        address = self.splitAddress(an.CURRENTOWNERADDRESS)

        # First Name
        line.append(an.CURRENTOWNERFORENAMES)
        # Last Name
        line.append(an.CURRENTOWNERSURNAME)
        # Email Address
        line.append(an.CURRENTOWNEREMAILADDRESS)
        # Address 1
        line.append(address["line1"])
        # Address 2
        line.append(address["line2"])
        # City
        line.append(an.CURRENTOWNERTOWN)
        # State
        line.append(an.CURRENTOWNERCOUNTY)
        # Zip Code
        line.append(an.CURRENTOWNERPOSTCODE)
        # Home Phone
        line.append(an.CURRENTOWNERHOMETELEPHONE)
        # Work Phone
        line.append(an.CURRENTOWNERWORKTELEPHONE)
        # Cell Phone
        line.append(an.CURRENTOWNERMOBILETELEPHONE)
        # Pet Name
        line.append(an.ANIMALNAME)
        # Microchip Number
        line.append(an.IDENTICHIPNUMBER)
        # Service Date
        line.append(asm3.i18n.format_date(servicedate, "%m/%d/%Y"))
        # Date of Birth
        line.append(asm3.i18n.format_date(an.DATEOFBIRTH, "%m/%d/%Y"))
        # Species
        line.append(an.PETFINDERSPECIES)
        # Sex
        line.append(an.SEXNAME)
        # Spayed/Neutered
        line.append(asm3.utils.iif(an.NEUTERED == 1, "Yes", "No"))
        # Primary Breed
        line.append(an.PETFINDERBREED)
        # Secondary Breed
        line.append(an.PETFINDERBREED2)
        # Color
        line.append(an.BASECOLOURNAME)
        # Implanting Organization
        line.append(org)
        # Rescue Group Email
        line.append(email)
        return self.csvLine(line)

    def validate(self, an: ResultRow, cutoffdays: int) -> bool:
        """ Validate an animal record is ok to send.
            an: The record
            cutoffdays: Negative number of days to check against service date
        """
        # Validate certain items aren't blank so we aren't registering bogus data
        if asm3.utils.nulltostr(an["CURRENTOWNERADDRESS"]).strip() == "":
            self.logError("Address for the new owner is blank, cannot process")
            return VALIDATE_NO 

        if asm3.utils.nulltostr(an["CURRENTOWNERPOSTCODE"]).strip() == "":
            self.logError("Postal code for the new owner is blank, cannot process")
            return VALIDATE_NO

        # Make sure the length is actually suitable
        if not len(an["IDENTICHIPNUMBER"]) in (9, 10, 15):
            self.logError("Microchip length is not 9, 10 or 15, cannot process")
            return VALIDATE_NO

        # If the action triggering this registration is older than our cutoff, 
        # not only fail validation, but return a value of FAIL so that this record
        # is marked with the error and we won't try again until something changes
        # (prevents old records continually being checked)
        servicedate = an["ACTIVEMOVEMENTDATE"] or an["MOSTRECENTENTRYDATE"]
        if an["NONSHELTERANIMAL"] == 1: servicedate = an["IDENTICHIPDATE"]
        if servicedate < self.dbo.today(offset=cutoffdays):
            an["FAILMESSAGE"] = "Service date is older than %s days, marking failed" % cutoffdays
            self.logError(an["FAILMESSAGE"])
            return VALIDATE_FAIL

        return VALIDATE_YES


