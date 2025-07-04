
import asm3.configuration
import asm3.i18n
import asm3.users
import asm3.utils

from .base import AbstractPublisher, get_microchip_data
from asm3.sitedefs import SMARTTAG_HOST
from asm3.typehints import Database, Dict, PublishCriteria, ResultRow

import sys

class SmartTagPublisher(AbstractPublisher):
    """
    Handles updating animal microchips with SmartTag
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("smarttag", "SmartTag Publisher")
    
    def run(self) -> None:
        
        self.log("Smart Tag Publisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        smarttagapikey = asm3.configuration.smarttag_api_key(self.dbo)

        if smarttagapikey == "":
            self.setLastError("api key needs to be set for SmartTag publisher")
            return

        headers = {
            "x-api-key": smarttagapikey
        }

        chipprefix = ["987%", "900139%", "900141%", "900074%"]

        animals = get_microchip_data(self.dbo, chipprefix, "smarttag", allowintake = False)
        if len(animals) == 0:
            self.setLastError("No microchips found to register.")
            return
        
        # Make sure we don't try to register too many chips
        if self.checkMicrochipLimit(animals): return

        anCount = 0
        processed_animals = []
        for an in animals:
            try:
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return

                if not self.validate(an): continue
                fields = self.processAnimal(an)
                j = asm3.utils.json(fields)
                self.log("HTTP POST request %s: %s" % (SMARTTAG_HOST, j))
                r = asm3.utils.post_json(SMARTTAG_HOST, j, headers=headers)
                self.log("HTTP response: %s" % r["response"])

                # Return value is an XML fragment, look for "Registration completed successfully"
                if r["response"].find("success") != -1:
                    self.log("successful response, marking processed")
                    processed_animals.append(an)
                    # Mark success in the log
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                else:
                    self.logError("Problem with data encountered, not marking processed")

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        if len(processed_animals) > 0:
            self.log("successfully processed %d animals, marking sent" % len(processed_animals))
            self.markAnimalsPublished(processed_animals)

        self.saveLog()
        self.setPublisherComplete()
    
    def processAnimal(self, an: ResultRow) -> Dict:
        """ Generate a dictionary of data to post from an animal record """
        # Sort out breed
        breed = an["BREEDNAME"]
        if breed.find("Domestic Long") != -1: breed = "DLH"
        if breed.find("Domestic Short") != -1: breed = "DSH"
        if breed.find("Domestic Medium") != -1: breed = "DSLH"

        # Sort out species
        species = an["SPECIESNAME"]
        if species.find("Dog") != -1: species = "Canine"
        elif species.find("Cat") != -1: species = "Feline"
        elif species.find("Bird") != -1: species = "Avian"
        elif species.find("Horse") != -1: species = "Equine"
        elif species.find("Reptile") != -1: species = "Reptilian"
        else: species = "Other"

        address1 = an["CURRENTOWNERADDRESS"].split("\n")[0]
        address2 = ""
        if "\n" in an["CURRENTOWNERADDRESS"]:
            address2 = an["CURRENTOWNERADDRESS"].split("\n")[1]

        firstname = an["CURRENTOWNERFORENAMES"].split(" ")[0]
        
        phones = []
        for phone in (an["CURRENTOWNERHOMETELEPHONE"], an["CURRENTOWNERWORKTELEPHONE"], an["CURRENTOWNERMOBILETELEPHONE"]):
            if phone:
                phones.append(
                    {
                        "extension": "",
                        "number": phone,
                        "type": "UNKNOWN"
                    }
                )
        
        neutered = "No"
        if an["NEUTERED"] == 1: neutered = "Yes"

        # Build the POST data
        ro = {
            "pets": [
                {
                    "microchip_number": an["IDENTICHIPNUMBER"],
                    "pet_name": an["ANIMALNAME"],
                    "pet_type": species,
                    "pet_breed": breed,
                    "pet_sec_breed": "",
                    "pet_color": an["BASECOLOURNAME"],
                    "pet_sec_color": "",
                    "pet_gender": an["SEXNAME"],
                    "pet_weight": "",
                    "pet_dob": asm3.i18n.format_date(an["IDENTICHIPDATE"], "%Y-%m-%d"),
                    "pet_neutered": neutered,
                    "pet_allergies": "",
                    "pet_unique_features": "",
                    "pet_special_needs": "",
                    "pet_images": [],
                    "pet_owner": {
                        "email": an["CURRENTOWNEREMAILADDRESS"],
                        "first_name": firstname,
                        "last_name": an["CURRENTOWNERSURNAME"],
                        "address_1": address1,
                        "address_2": address2,
                        "city": an["CURRENTOWNERTOWN"],
                        "state": an["CURRENTOWNERCOUNTY"],
                        "zip": an["CURRENTOWNERPOSTCODE"],
                        "country": "US",
                        "phone": an["CURRENTOWNERHOMETELEPHONE"],
                        "mobile_phone": an["CURRENTOWNERMOBILETELEPHONE"]
                    }
                    #Can add a secondary and/or vet contact here - Adam.
                }
            ]
        }

        return ro
    
    def validate(self, an: ResultRow) -> bool:
        """ Validate an animal record is ok to send """
        # Validate certain items aren't blank so we aren't registering bogus data
        if asm3.utils.nulltostr(an["CURRENTOWNERADDRESS"]).strip() == "":
            self.logError("Address for the new owner is blank, cannot process")
            return False 

        if asm3.utils.nulltostr(an["CURRENTOWNERPOSTCODE"]).strip() == "":
            self.logError("Postal code for the new owner is blank, cannot process")
            return False

        # Make sure the length is actually suitable
        if len(an.IDENTICHIPNUMBER) != 15:
            self.logError("Microchip length is not 15, cannot process")
            return False
    
        return True