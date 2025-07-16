
import asm3.configuration
import asm3.i18n
import asm3.utils

from .base import AbstractPublisher, get_microchip_data
from asm3.sitedefs import PETLINK_BASE_URL
from asm3.typehints import Database, PublishCriteria, ResultRow

import sys

UPLOAD_URL = PETLINK_BASE_URL + "api/restapi/signup/mass-import?filename=import.csv&mediumId=sheltermanager"

VALIDATE_YES = 0
VALIDATE_NO = 1
VALIDATE_FAIL = 2

class PetLinkPublisher(AbstractPublisher):
    """
    Handles publishing of updated microchip info to PetLink.net
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("petlink", "PetLink Publisher")

    def plYesNo(self, condition: bool) -> str:
        """
        Returns yes or no for a condition.
        """
        if condition:
            return "y"
        else:
            return "n"

    def plBreed(self, breedname: str, speciesname: str, iscross: int) -> str:
        """
        Returns a PetLink breed of either the breed name,
        "Mixed Breed" if iscross == 1 or "Other" if the species
        is not Cat or Dog.
        """
        if speciesname.lower().find("cat") != -1 and speciesname.lower().find("dog") != -1:
            return "Other"
        if iscross == 1:
            return "Mixed Breed"
        return breedname

    def run(self) -> None:
        
        self.log("PetLinkPublisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        plemail = asm3.configuration.petlink_email(self.dbo)
        plowneremail = asm3.configuration.petlink_owner_email(self.dbo)
        password = asm3.configuration.petlink_password(self.dbo)

        if plemail == "" or password == "":
            self.setLastError("No PetLink login has been set.")
            return

        chipprefix = ["98102"]
        if asm3.configuration.petlink_register_all(self.dbo):
            chipprefix = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

        animals = get_microchip_data(self.dbo, chipprefix, "petlink", organisation_email = plowneremail)
        if len(animals) == 0:
            self.setLastError("No microchips found to register.")
            return
        
        # Make sure we don't try to register too many chips
        if self.checkMicrochipLimit(animals): return

        cutoffdays = asm3.configuration.petlink_cutoff_days(self.dbo)
        if cutoffdays == 0: cutoffdays = -1095 # default cutoff is 3 years, note that it's a negative number

        anCount = 0
        csv = []
        processed_animals = []
        failed_animals = []

        csv.append("Software,TransactionType,MicrochipID,FirstName,LastName,Address,City,State,ZipCode,Country," \
            "Phone1,Phone2,Phone3,Email,Password,Date_of_Implant,submitDate,PetName,Species,Breed,Gender," \
            "Spayed_Neutered,ColorMarkings")

        for an in animals:
            try:
                anCount += 1
                self.log("Processing: %s: %s (%d of %d) - %s %s" % \
                    ( an.SHELTERCODE, an.ANIMALNAME, anCount, len(animals), an.IDENTICHIPNUMBER, an.CURRENTOWNERNAME ))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return

                v = self.validate(an, cutoffdays)
                if v == VALIDATE_NO: 
                    continue
                elif v == VALIDATE_YES:
                    csv.append( self.processAnimal(an) )
                    processed_animals.append(an)
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( \
                        an.SHELTERCODE, an.ANIMALNAME, anCount, len(animals)))
                elif v == VALIDATE_FAIL:
                    failed_animals.append(an)

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # If we excluded our only animals and have nothing to send, stop now
        if len(csv) == 1:
            self.log("No animals left to send to PetLink.")
            self.cleanup()
            return

        # POST the csv data
        headers = {
            "Authorization": "Basic %s" % asm3.utils.base64encode("%s:%s" % (plemail, password)),
            "Content-Type":  "text/csv"
        }
        self.log("Uploading data file (%d csv lines) to %s..." % (len(csv), UPLOAD_URL))
        try:
            r = asm3.utils.post_data(UPLOAD_URL, "\n".join(csv), headers=headers)
            response = r["response"]

            self.log("req hdr: %s, \nreq data: %s" % (r["requestheaders"], r["requestbody"]))
            self.log("resp hdr: %s, \nresp body: %s" % (r["headers"], response))

            # If we got back an empty response body, that means the username
            # and password were wrong. We save a new log that just contains the
            # error instead so that the user does not see success messages.
            if len(response) == 0:
                self.initLog("petlink", "PetLink Publisher")
                self.logError("Received empty response body, username and password must be incorrect.")
                self.successes = 0
                self.alerts = 1
                self.saveLog()
                self.setLastError("Incorrect username and password.")
                return

            jresp = asm3.utils.json_parse(response)
            
            # Look for remote exceptions
            if "exception" in jresp and jresp["exception"] != "":
                self.successes = 0
                self.logError("PetLink remote exception received, abandoning: %s" % jresp["exception"])
                self.saveLog()
                self.setPublisherComplete()
                return

            # Parse any errors in the JSON response
            for e in jresp["errors"]:
                chip = ""
                message = ""
                try:
                    # Prefer microchip= in location column, then fall back to id=/microchip= in column
                    # PetLink now also have an Animal/Chip/Person format in column too
                    if e["location"].find("microchip=") != -1:
                        chip = e["location"]
                        chip = chip[chip.find("microchip=")+10:]
                    elif e["column"].find("id=") != -1:
                        chip = e["column"].replace("id=", "")
                    elif e["column"].find("microchip=") != -1:
                        chip = e["column"].replace("microchip=", "")
                    elif e["column"].count("/") == 2:
                        chip = e["column"].split("/")[1]
                    message = e["message"]
                except Exception as erj:
                    try:
                        self.logError("Failed unpacking error message (message=%s) from '%s'" % (erj, e))
                    except:
                        self.logError("Failed decoding error message from PetLink")
                    continue

                # Iterate over a copy of the processed list so we can remove animals from it
                # that have error emssages.
                for an in processed_animals[:]:

                    if an.IDENTICHIPNUMBER == chip:
                        processed_animals.remove(an)
                        try:
                            self.logError("%s: %s (%s) - Received error message from PetLink: %s" % \
                                (an.SHELTERCODE, an.ANIMALNAME, an.IDENTICHIPNUMBER, message))
                        except:
                            self.logError("%s: %s (%s) - Error decoding message from PetLink" % \
                                (an.SHELTERCODE, an.ANIMALNAME, an.IDENTICHIPNUMBER))
                            continue

                        # If the message was that the chip is already registered,
                        # mark this animal as published but on the intake date -
                        # this will force this publisher to put it through as a transfer
                        # next time since we'll find a previous published record.
                        if message.find("has already been registered") != -1:
                            self.markAnimalPublished(an.ID, an.DATEBROUGHTIN, "chip already registered, sending as transfer on next publish")
                            self.log("%s: %s (%s) - Already registered, marking as PetLink TRANSFER for next publish" % \
                                (an.SHELTERCODE, an.ANIMALNAME, an.IDENTICHIPNUMBER))
                            continue

                        # If the message is one of PetLink's permanent failure conditons, 
                        # mark the chip failed so that we stop trying.
                        # Any other error message we treat as transient and do nothing 
                        # (which means we'll attempt to register the chip the next time this publisher is run).
                        PERMANENT_FAILURES = [ 
                            "has an existing PetLink account and their contact information is already on file",
                            "Not a prepaid microchip",
                            "This is a Found Animals Registry chip",
                            "cannot be transferred - the account is locked.",
                            "Microchip number has already been registered in the database"
                        ]
                        for m in PERMANENT_FAILURES:
                            if message.find(m) != -1:
                                an.FAILMESSAGE = message
                                failed_animals.append(an)

            if len(processed_animals) > 0:
                self.markAnimalsPublished(processed_animals)

            if len(failed_animals) > 0:
                self.markAnimalsPublishFailed(failed_animals)

        except Exception as err:
            self.logError("Failed uploading data file: %s" % err)

        self.cleanup()

    def processAnimal(self, an: ResultRow) -> str:
        """ Process an animal record and return a CSV line """
        
        email = asm3.utils.nulltostr(an.CURRENTOWNEREMAILADDRESS).strip()
        homephone = asm3.utils.nulltostr(an.CURRENTOWNERHOMETELEPHONE).strip()
        workphone = asm3.utils.nulltostr(an.CURRENTOWNERWORKTELEPHONE).strip()
        mobilephone = asm3.utils.nulltostr(an.CURRENTOWNERMOBILETELEPHONE).strip()
        address = self.splitAddress(an.CURRENTOWNERADDRESS)

        # Get the non-blank phone number and strip it of non-numeric data
        phone = homephone or mobilephone or workphone
        phone = "".join(c for c in phone if c.isdigit())

        # If we don't have an email address, use phone@petlink.tmp
        if email == "":
            email = "%s@petlink.tmp" % phone

        # If the email contains more than one address, throw the extra away
        if email.find(",") != -1 and email.count("@") > 1:
            email = email[0:email.find(",")].strip()

        # Date of the event that triggered registration
        submitdate = an.ACTIVEMOVEMENTDATE or an.MOSTRECENTENTRYDATE
        if an.NONSHELTERANIMAL == 1: submitdate = an.IDENTICHIPDATE

        line = []
        # Software
        line.append("ASM")
        # TransactionType
        line.append(self.getLastPublishedDate(an.ID) is None and 'N' or 'T' )
        # MicrochipID
        line.append(an.IDENTICHIPNUMBER)
        # FirstName
        line.append(an.CURRENTOWNERFORENAMES)
        # LastName
        line.append(an.CURRENTOWNERSURNAME)
        # Address
        line.append(address["csv"])
        # City
        line.append(an.CURRENTOWNERTOWN)
        # State
        line.append(an.CURRENTOWNERCOUNTY)
        # ZipCode
        line.append(an.CURRENTOWNERPOSTCODE)
        # Country
        line.append(self.getLocaleForCountry(an.CURRENTOWNERCOUNTRY))
        # Phone1
        line.append(homephone)
        # Phone2
        line.append(workphone)
        # Phone3
        line.append(mobilephone)
        # Email (mandatory)
        line.append( email )
        # Chip Password (stripped phone number)
        line.append(phone)
        # Date_of_Implant (mm/dd/yyyy)
        line.append(asm3.i18n.format_date(an.IDENTICHIPDATE, "%m/%d/%Y"))
        # submitDate (mm/dd/yyyy)
        line.append(asm3.i18n.format_date(submitdate, "%m/%d/%Y"))
        # PetName
        line.append(an.ANIMALNAME)
        # Species
        line.append(an.SPECIESNAME)
        # Breed (or "Mixed Breed" for crossbreeds, Other for animals not cats and dogs)
        line.append(self.plBreed(an.BREEDNAME1, an.SPECIESNAME, an.CROSSBREED))
        # Gender
        line.append(an.SEXNAME)
        # Spayed_Neutered (y or n)
        line.append(self.plYesNo(an.NEUTERED))
        # ColorMarkings (our BaseColour field)
        line.append(an.BASECOLOURNAME)
        return self.csvLine(line)

    def validate(self, an: ResultRow, cutoffdays: int) -> bool:
        """ Validate an animal record is ok to send.
            an: The record
            cutoffdays: Negative number of days to check against service date
        """
        # If the microchip number isn't 15 digits, skip it
        if not asm3.configuration.petlink_register_all(self.dbo) and len(an.IDENTICHIPNUMBER.strip()) != 15:
            self.logError("Chip number failed validation (%s not 15 digits), skipping." % an.IDENTICHIPNUMBER)
            return VALIDATE_NO

        # Validate certain items aren't blank so we aren't trying to register
        # things that PetLink will bounce back anyway
        if asm3.utils.nulltostr(an.CURRENTOWNERTOWN).strip() == "":
            self.logError("City for the new owner is blank, cannot process")
            return VALIDATE_NO 

        if asm3.utils.nulltostr(an.CURRENTOWNERCOUNTY).strip() == "":
            self.logError("State for the new owner is blank, cannot process")
            return VALIDATE_NO 

        if asm3.utils.nulltostr(an.CURRENTOWNERPOSTCODE).strip() == "":
            self.logError("Zipcode for the new owner is blank, cannot process")
            return VALIDATE_NO

        # If there's no email or phone, PetLink won't accept it
        email = asm3.utils.nulltostr(an.CURRENTOWNEREMAILADDRESS).strip()
        homephone = asm3.utils.nulltostr(an.CURRENTOWNERHOMETELEPHONE).strip()
        workphone = asm3.utils.nulltostr(an.CURRENTOWNERWORKTELEPHONE).strip()
        mobilephone = asm3.utils.nulltostr(an.CURRENTOWNERMOBILETELEPHONE).strip()
        if email == "" and homephone == "" and workphone == "" and mobilephone == "":
            self.logError("No email address or phone number for owner, skipping.")
            return VALIDATE_NO
       
        # If there's no phone, we can't set the chip password so skip it
        if homephone == "" and workphone == "" and mobilephone == "":
            self.logError("No phone number for owner, skipping.")
            return VALIDATE_NO

        # If the action triggering this registration is older than our cutoff, 
        # not only fail validation, but return a value of FAIL so that this record
        # is marked with the error and we won't try again until something changes
        # (prevents old records continually being checked)
        servicedate = an.ACTIVEMOVEMENTDATE or an.MOSTRECENTENTRYDATE
        if an.NONSHELTERANIMAL == 1: servicedate = an.IDENTICHIPDATE
        if servicedate < self.dbo.today(offset=cutoffdays):
            an.FAILMESSAGE = "Service date is older than %s days, marking failed" % cutoffdays
            self.logError(an.FAILMESSAGE)
            return VALIDATE_FAIL

        return VALIDATE_YES



