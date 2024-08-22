
import asm3.additional
import asm3.animal
import asm3.configuration
import asm3.medical
import asm3.utils

from .base import AbstractPublisher, get_microchip_data
from asm3.sitedefs import BUDDYID_BASE_URL, BUDDYID_EMAIL, BUDDYID_PASSWORD
from asm3.typehints import Database, PublishCriteria, ResultRow

import sys

# ID type keys used in the ExtraIDs column
IDTYPE_BUDDYID = "buddyid"

class BuddyIDPublisher(AbstractPublisher):
    """
    Handles microchip registrations to buddyid.com
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.uploadDirectly = True
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("buddyid", "BuddyID Publisher")

    def run(self) -> None:
        
        self.log("BuddyIDPublisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        provider_code = asm3.configuration.buddyid_provider_code(self.dbo)

        if provider_code == "":
            self.setLastError("No BuddyID Provider Code has been set.")
            self.cleanup()
            return

        animals = get_microchip_data(self.dbo, ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], "buddyid", allowintake=True)
        if len(animals) == 0:
            self.setLastError("No microchips found to register.")
            return

        # Authenticate to get our bearer token
        url = f"{BUDDYID_BASE_URL}/login"
        data = { "email": BUDDYID_EMAIL, "password": BUDDYID_PASSWORD }
        self.log("Token request to %s: %s" % ( url, data)) 
        try:
            r = asm3.utils.post_form(url, data)
            if r["status"] != 200:
                self.setLastError("Authentication failed.")
                self.logError("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                self.cleanup()
                return
            self.log("Response: %s" % r["response"])
            token = asm3.utils.json_parse(r["response"])["access_token"]
            # Create the HTTP headers we're going to send with each request
            authheaders = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            self.log("Token received: %s" % token)
        except Exception as err:
            self.setLastError("Authentication failed.")
            self.logError("Failed getting token: %s" % err, sys.exc_info())
            self.cleanup()
            return

        processed_animals = []
        failed_animals = []

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

                # Do we already have an ID for this registration?
                registration_id = asm3.animal.get_extra_id(self.dbo, an, IDTYPE_BUDDYID)

                if not self.validate(an): continue
                data = self.processAnimal(an, provider_code)
                jsondata = asm3.utils.json(data)

                # If we had a registration_id, update the existing registration, otherwise create a new one.
                if registration_id == "":
                    url = f"{BUDDYID_BASE_URL}/v1/registry"
                    self.log("Sending POST to %s to create listing: %s" % (url, jsondata))
                    r = asm3.utils.post_json(url, jsondata, authheaders)
                else:
                    url = f"{BUDDYID_BASE_URL}/v1/registry/{registration_id}"
                    self.log("Sending PUT to %s to update listing: %s" % (url, jsondata))
                    r = asm3.utils.put_json(url, jsondata, authheaders)

                # Check for responses that are returned with a success code, but are really failures
                already_registered = r["response"].find("Microchip Already Registered") != -1

                # They return the following codes:
                # 200 Successful PUT (update)
                # 201 Successful POST (new)
                # 422 Validation failed
                if r["status"] >= 400 or already_registered:
                    self.logError("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                    # Already registered is a permanent failure
                    if already_registered:
                        self.log("Microchip already registered: permanent failure")
                        an.FAILMESSAGE = "Microchip already registered"
                        failed_animals.append(an)
                else:
                    self.log("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                    processed_animals.append(an)

                    # If we didn't have a registration_id, extract it from the response and store it
                    # so future postings will update this registration
                    if registration_id == "":
                        registration_id = asm3.utils.json_parse(r["response"])["data"]["id"]
                        asm3.animal.set_extra_id(self.dbo, "pub::buddyid", an, IDTYPE_BUDDYID, registration_id)  

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark sent animals published
        if len(processed_animals) > 0:
            self.markAnimalsPublished(processed_animals)
        if len(failed_animals) > 0:
            self.markAnimalsPublishFailed(failed_animals)

        self.cleanup()

    def processAnimal(self, an: ResultRow, provider_code: str) -> str:
        """ Processes an animal record and returns a data dictionary for upload as JSON """
        d = {}
        address = self.splitAddress(an.CURRENTOWNERADDRESS)
        d["account"] = { "emailAddress": an.CURRENTOWNEREMAILADDRESS }
        d["primaryContact"] = {
            "nameFirst": an.CURRENTOWNERFORENAMES,
            "nameLast": an.CURRENTOWNERSURNAME,
            "address": {
                "streetLine1": address["line1"],
                "streetLine2": address["line2"],
                "city": an.CURRENTOWNERTOWN,
                "stateProvince": an.CURRENTOWNERCOUNTY,
                "postalCode": an.CURRENTOWNERPOSTCODE,
                "country": "USA"
            },
            "marketing": { "optIn": True },
            "phonePrimary": { "number": an.CURRENTOWNERMOBILETELEPHONE, "optIn": True },
            "phoneSecondary": { "number": an.CURRENTOWNERHOMETELEPHONE, "optIn": True }
        }
        d["alternateContact"] = {
            "nameFirst": "",
            "nameLast": "",
            "phonePrimary": "",
            "phoneSecondary": ""
        }
        d["pet"] = {
            "name": an.ANIMALNAME,
            "species": an.SPECIESNAME,
            "breed": an.BREEDNAME,
            "gender": an.SEXNAME,
            "birthDate": asm3.i18n.python2display(self.dbo.locale, an.DATEOFBIRTH),
            "colorMarkings": an.BASECOLOURNAME
        }
        d["microchipNumber"] = an.IDENTICHIPNUMBER
        d["providerCode"] = provider_code
        return d

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

