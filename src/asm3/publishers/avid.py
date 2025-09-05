
import asm3.configuration
import asm3.i18n
import asm3.utils
import base64
import requests

from .base import AbstractPublisher, get_microchip_data
from asm3.sitedefs import AVID_US_POST_URL
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
    
        APIKEY = "LnmJUQ0xA38H9rSCH8MWO4K7IsF0kEAl8w13bD2m"

        #
        # Shelter username and password
        #
        USERNAME = "help@sheltermanager.com"
        PASSWORD = "gEa&MXem7za%c5vLkTQbC4wkLEQWScAV"

        #
        # Authentication Header
        #
        basic_auth_str = f'{USERNAME}:{PASSWORD}'
        basic_auth_header = base64.b64encode(basic_auth_str.encode()).decode()
        config = {
            'headers': {
                'authorization': 'Basic ' + basic_auth_header,
                'x-api-key': APIKEY
            }
        }
        #####
        self.log("Auth: " + basic_auth_header)
        self.log("AVID_US_POST_URL = " + AVID_US_POST_URL)
        chipprefix = ["977%"] # AVID Europe - # To do - confirm that this prefix also applies to AVID US, a quick google search suggested it does (it was an AI result so I'm not convinced yet) - Adam.
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
                r = asm3.utils.post_json(AVID_US_POST_URL, asm3.utils.json(fields), config['headers'])
                if r['response'] and asm3.utils.json_parse(r["response"])["status"] == 'COMPLETE':
                    self.log("Successful response, marking processed")
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
                        "number": phone,#.replace(" ", ""),
                        "type": "UNKNOWN"
                    }
                )
        
        sex = an["SEXNAME"].upper()
        if sex == "UNKNOWN":
            sex = "OTHER"

        # Build the POST data
        ro = {
            "registrations": [
                {
                    "pets": [
                        {
                            "breeds": [
                                breed
                            ],
                            "color": an["BASECOLOURNAME"],
                            "dob": asm3.i18n.format_date(an["DATEOFBIRTH"], "%m-%d-%Y"),
                            "fixed": an["NEUTERED"] == 1 and "true" or "false",
                            "marking": "",
                            "medication": "",
                            "microchips": [
                                {
                                    "number": an["IDENTICHIPNUMBER"],# To do - add second microchip if exists?
                                    "protocol": "ISO"
                                }
                            ],
                            "name": an["ANIMALNAME"],
                            "sex": sex,
                            "species": species.upper(),
                            "status": "HOME",# To do - find out if this can be excluded - Adam.
                            # Have excluded weight as must be in pounds, could add it if required
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
                                    "type": "HOME"# To do - find out if this can be excluded - Adam.
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

        # Make sure the length is actually suitable
        if not len(an.IDENTICHIPNUMBER) in (9, 10, 15):
            self.logError("Microchip length is not 9, 10 or 15, cannot process")
            return False
    
        return True