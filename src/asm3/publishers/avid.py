
import asm3.configuration
import asm3.i18n
import asm3.utils

from .base import AbstractPublisher, get_microchip_data

from asm3.sitedefs import AVID_US_BASE_URL
from asm3.typehints import Database, Dict, PublishCriteria, ResultRow

import sys

class AVIDUSPublisher(AbstractPublisher):
    """
    Handles updating animal microchips with AVID US
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("avidus", "AVID US Publisher")
        self.dbo = dbo
    
    def run(self) -> None:
        
        self.log("AVID US Publisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        avidusername = asm3.configuration.avidus_username(self.dbo)
        avidpassword = asm3.configuration.avidus_password(self.dbo)
        avidkey = asm3.configuration.avidus_apikey(self.dbo)

        #
        # Authentication Header
        #
        basic_auth_str = f"{avidusername}:{avidpassword}"
        basic_auth_header = asm3.utils.base64encode(basic_auth_str)
        config = {
            'headers': {
                'authorization': 'Basic ' + basic_auth_header,
                'x-api-key': avidkey
            }
        }
        chipprefix = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        animals = get_microchip_data(self.dbo, chipprefix, "avidus", allowintake=False)
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
                jsondata = asm3.utils.json(fields)
                url = f"{AVID_US_BASE_URL}/registrations"
                self.log("Sending POST to %s: %s" % (url, jsondata))
                r = asm3.utils.post_json(url, jsondata, config["headers"])
                if r["response"] and asm3.utils.json_parse(r["response"])["status"] == 'COMPLETE':
                    self.log("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                    processed_animals.append(an)
                else:
                    self.logError("status != COMPLETE: HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))

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

        address = an["CURRENTOWNERADDRESS"].split("\n")[0].split(" ")
        premise = " ".join(address[:-1])
        thoroughfare = address[-1]

        firstname = an["CURRENTOWNERFORENAMES"].split(" ")[0]
        middlenames = ""
        if " " in an["CURRENTOWNERFORENAMES"]:
            middlenames = " ".join(an["CURRENTOWNERFORENAMES"].split(" ")[1:])
        
        phones = []
        for phone in (an["CURRENTOWNERHOMETELEPHONE"], an["CURRENTOWNERWORKTELEPHONE"], an["CURRENTOWNERMOBILETELEPHONE"]):
            if phone:
                phones.append(
                    {
                        "extension": "",
                        "number": phone.replace(" ", ""),
                        "type": "UNKNOWN"
                    }
                )
        
        sex = an["SEXNAME"].upper()
        if sex == "UNKNOWN":
            sex = "OTHER"
        
        weight = 0
        if an["WEIGHT"]:
            weight = an["WEIGHT"]

        # Build the POST data
        ro = {
            "registrations": [
                {
                    "pets": [
                        {
                            "breeds": [ breed ],
                            "color": an["BASECOLOURNAME"],
                            "dob": asm3.i18n.format_date(an["DATEOFBIRTH"], "%m-%d-%Y"),
                            "fixed": an["NEUTERED"] == 1 and "true" or "false",
                            "marking": "",
                            "medication": "",
                            "microchips": [
                                {
                                    "number": an["IDENTICHIPNUMBER"],
                                    "protocol": "ISO"
                                }
                            ],
                            "name": an["ANIMALNAME"],
                            "sex": sex,
                            "species": species.upper(),
                            "status": "HOME",
                            "weight": weight
                        }
                    ],
                    "contacts": [
                        {
                            "firstName": firstname,
                            "middleName": middlenames,
                            "lastName": an["CURRENTOWNERSURNAME"],
                            "addresses": [
                                {
                                    "administrativeArea": an["CURRENTOWNERCOUNTY"],
                                    "country": "US",
                                    "locality": an["CURRENTOWNERTOWN"],
                                    "premise": premise,
                                    "thoroughfare": thoroughfare,
                                    "postalCode": an["CURRENTOWNERPOSTCODE"],
                                    "type": "HOME"
                                }
                            ],
                            "emails": [
                                {
                                    "address": an["CURRENTOWNEREMAILADDRESS"],
                                    "type": "PERSONAL"
                                }
                            ],
                            "phones": phones,
                            "type": "PRIMARY"

                        }
                    ],
                    "facility": asm3.configuration.organisation(self.dbo),
                    "registrationDatetime": self.dbo.now().isoformat()
                }
            ]
        }

        return ro
    
    def validate(self, an: ResultRow) -> bool:
        """ Validate an animal record is ok to send """
        # Validate certain items aren't blank so we aren't registering bogus data
        if asm3.utils.nulltostr(an.CURRENTOWNERADDRESS).strip() == "":
            self.logError("Address for the new owner is blank, cannot process")
            return False 

        if asm3.utils.nulltostr(an.CURRENTOWNERPOSTCODE).strip() == "":
            self.logError("Postal code for the new owner is blank, cannot process")
            return False
        
        if asm3.utils.nulltostr(an.CURRENTOWNEREMAILADDRESS).strip() == "":
            self.logError("Email address for the new owner is blank, cannot process")
            return False

        # Make sure the length is actually suitable
        if not len(an.IDENTICHIPNUMBER) in (9, 10, 15):
            self.logError("Microchip length is not 9, 10 or 15, cannot process")
            return False
    
        return True

