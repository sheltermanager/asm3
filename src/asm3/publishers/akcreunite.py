
import asm3.al
import asm3.configuration
import asm3.i18n
import asm3.utils

from .base import AbstractPublisher, get_microchip_data
from asm3.sitedefs import AKC_REUNITE_BASE_URL, AKC_REUNITE_USER, AKC_REUNITE_PASSWORD
from asm3.typehints import Database, PublishCriteria, ResultRow

import sys

class AKCReunitePublisher(AbstractPublisher):
    """
    Handles updating AKC Reunite animal microchips
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("akcreunite", "AKC Reunite Publisher")
        self.microchipPatterns = ['0006', '0007', '956', '9910010']

    def get_akc_species(self, asmspeciesid: int) -> str:
        if asmspeciesid == 1: return "DOG"
        elif asmspeciesid == 2: return "CAT"
        else: 
            return "OTHR"

    def run(self) -> None:
       
        self.log(self.publisherName + " starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        enrollmentsourceid = asm3.configuration.akc_enrollmentsourceid(self.dbo)

        if enrollmentsourceid == "":
            self.setLastError("AKC enrollment source ID must be set")
            return

        orgname = asm3.configuration.organisation(self.dbo)
        orgtel = asm3.configuration.organisation_telephone(self.dbo)
        orgemail = asm3.configuration.email(self.dbo)
        orgaddress = asm3.configuration.organisation_address(self.dbo)
        orgtown = asm3.configuration.organisation_town(self.dbo)
        orgcounty = asm3.configuration.organisation_county(self.dbo)
        orgpostcode = asm3.configuration.organisation_postcode(self.dbo)

        if asm3.configuration.akc_register_all(self.dbo):
            self.microchipPatterns = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

        animals = get_microchip_data(self.dbo, self.microchipPatterns, self.publisherKey)
        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            return

        anCount = 0
        processed_animals = []
        failed_animals = []
        for an in animals:
            try:
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an.SHELTERCODE, an.ANIMALNAME, anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    return

                # Construct the JSON document
                if not self.validate(an): continue
                j = self.processAnimal(an, enrollmentsourceid, orgname, orgtel, orgemail, orgaddress, orgtown, orgcounty, orgpostcode)
                                
                # Build our Basic AUTH and other headers
                authheaders = {
                    "Authorization": "Basic %s" % asm3.utils.base64encode("%s:%s" % (AKC_REUNITE_USER, AKC_REUNITE_PASSWORD)),
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                }

                url = AKC_REUNITE_BASE_URL + "/cares-ws/services/prs/enrollment"
                try:
                    # Post our document
                    self.log("Posting microchip registration document to %s: %s" % (url, j))
                    r = asm3.utils.post_json(url, j, authheaders)
                    self.log("Response %d, HTTP headers: %s, body: %s" % (r["status"], r["headers"], r["response"]))

                    # AKC return 202 Accepted for new registrations and
                    # 400 Forbidden status codes for already registered.
                    if r["status"] >= 500: raise Exception(r["response"])

                    # Examine the response for return codes
                    jr = asm3.utils.json_parse(r["response"])
                    wassuccess = False
                    if jr["responseCode"] in ( 54000, 54100, 54108 ):
                        self.log("successful %s response found, marking processed" % jr["responseCode"])
                        processed_animals.append(an)
                        # Mark success in the log
                        self.logSuccess("Processed: %s: %s (%d of %d)" % ( an.SHELTERCODE, an.ANIMALNAME, anCount, len(animals)))
                        wassuccess = True

                    # If we got a sender not recognised message, there's no point sending 
                    # anything else as they will all trigger the same error
                    if jr["responseCode"] == 54101:
                        self.logError("received 54101 'sender not recognized' response - abandoning run and disabling publisher")
                        asm3.configuration.publishers_enabled_disable(self.dbo, "ak")
                        break

                    # Temporary or data errors - do nothing so we try again next time
                    # 54103 = Data failed validation
                    # 54107 = Database unavailable, try later
                    if jr["responseCode"] == 54103 or jr["responseCode"] == 54107:
                        continue
                    
                    if not wassuccess:
                        self.logError("no successful 54000, 54100, 54108 response received")
                        an.FAILMESSAGE = "%s" % jr["responseMessage"]
                        failed_animals.append(an)

                except Exception as err:
                    em = str(err)
                    self.logError("Failed registering microchip: %s" % em, sys.exc_info())
                    continue

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an.SHELTERCODE), err), sys.exc_info())

        # Mark success/failures
        if len(processed_animals) > 0:
            self.log("successfully processed %d animals, marking sent" % len(processed_animals))
            self.markAnimalsPublished(processed_animals)
        if len(failed_animals) > 0:
            self.log("failed processing %d animals, marking failed" % len(failed_animals))
            self.markAnimalsPublishFailed(failed_animals)

        self.saveLog()
        self.setPublisherComplete()

    def processAnimal(self, an: ResultRow, enrollmentsourceid="", orgname="", orgtel="", orgemail="", orgaddress="", orgtown="", orgcounty="", orgpostcode="") -> str:
        """ Returns a JSON document from an animal """
        reccountry = an.CURRENTOWNERCOUNTRY
        if reccountry is None or reccountry == "": reccountry = "USA"
        address = self.splitAddress(an.CURRENTOWNERADDRESS)
        o = {
            "enrollmentSourceId": enrollmentsourceid,
            "pet": {
                "name":         an.ANIMALNAME,
                "speciesCode":  self.get_akc_species(an.SPECIESID),
                "breedCode":    an.BREEDNAME,
                "colorMarkings": an.MARKINGS,
                "genderCode":   an.SEXNAME[0:1],
                "spayedNeutered": an.NEUTERED == 1,
                "birthDate":    asm3.i18n.format_date(an.DATEOFBIRTH, "%m-%d-%Y"),
            },
            "primaryContact": {
                "firstName":    an.CURRENTOWNERFORENAMES,
                "lastName":     an.CURRENTOWNERSURNAME,
                "phone": {
                    "number":   an.CURRENTOWNERMOBILETELEPHONE or an.CURRENTOWNERHOMETELEPHONE or an.CURRENTOWNERWORKTELEPHONE,
                    "extension": "",
                    "country":  reccountry
                },
                "emailAddress": an.CURRENTOWNEREMAILADDRESS,
                "emailOptIn":   True,
                "address": {
                    "street":   address["csv"],
                    "streetExtra": "",
                    "city":     an.CURRENTOWNERTOWN,
                    "stateProvince": an.CURRENTOWNERCOUNTY,
                    "postalCode": an.CURRENTOWNERPOSTCODE,
                    "country":  reccountry
                },
                "mailOptIn":    False
            },
            "vetPractice": {
                "businessName": orgname,
                "phone": {
                    "number":   orgtel,
                    "extension": "",
                    "country":  "USA"
                },
                "emailAddress": orgemail,
                "address": {
                    "street":   orgaddress,
                    "streetExtra": "",
                    "city":     orgtown,
                    "stateProvince": orgcounty,
                    "postalCode": orgpostcode,
                    "country":  "USA"
                }
            },
            "microchipId":      an.IDENTICHIPNUMBER
        }
        # If we don't have a first name, set one.
        if o["primaryContact"]["firstName"] == "":
            o["primaryContact"]["firstName"] = "org"
        return asm3.utils.json(o)

    def validate(self, an: ResultRow) -> bool:
        """ Validates an animal record is ok to send """
        # Validate certain items aren't blank so we aren't registering bogus data
        if asm3.utils.nulltostr(an.CURRENTOWNERADDRESS).strip() == "":
            self.logError("Address for the new owner is blank, cannot process")
            return False 

        if asm3.utils.nulltostr(an.CURRENTOWNERPOSTCODE).strip() == "":
            self.logError("Postal code for the new owner is blank, cannot process")
            return False

        # Make sure the length is actually suitable
        if not len(an.IDENTICHIPNUMBER) in (9, 10, 15):
            self.logError("Microchip length is not 9, 10 or 15, cannot process")
            return False

        return True


