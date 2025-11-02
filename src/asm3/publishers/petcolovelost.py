
import asm3.configuration
import asm3.i18n
import asm3.utils
import datetime

from .base import AbstractPublisher, get_microchip_data

from asm3.sitedefs import PETCO_LOVELOST_BASE_URL
from asm3.typehints import Database, Dict, PublishCriteria, ResultRow

import sys

class PetcoLoveLostPublisher(AbstractPublisher):
    """
    Handles sending found animal data to Petco Love Lost
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("avidus", "AVID US Publisher")
        self.dbo = dbo
    
    def getAnimalData(self) -> str:
        return self.dbo.query(
            "SELECT a.ID, a.ShelterCode, a.AnimalName, a.BreedID, a.Breed2ID, a.CrossBreed, a.Sex, a.Size, a.DateOfBirth, a.MostRecentEntryDate, a.Fee, " \
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
            "LEFT OUTER JOIN entryreason er ON a.EntryReasonID = er.ID " \
            "WHERE a.Archived = 0 AND ( s.SpeciesName = 'Dog' OR s.SpeciesName = 'Cat' )"
        )

    
    def run(self) -> None:
        
        self.log("Petco Love Lost Publisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        petcolovelostusername = asm3.configuration.petcolovelost_email(self.dbo)
        petcolovelostpassword = asm3.configuration.petcolovelost_password(self.dbo)
        petcolovelostkey = asm3.configuration.petcolovelost_apikey(self.dbo)

        #
        # Authentication Header
        #
        basic_auth_str = f"{petcolovelostusername}:{petcolovelostpassword}"
        basic_auth_header = asm3.utils.base64encode(basic_auth_str)
        config = {
            'headers': {
                'authorization': 'Basic ' + basic_auth_header,
                'x-api-key': petcolovelostkey
            }
        }

        animals = self.getAnimalData()

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
                url = f"{PETCO_LOVELOST_BASE_URL}/registrations"
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
                    "id": "6f9dcf96-11e8-4042-90ab-fdb842cad53c",
                    "created_at": datetime.datetime.today().isoformat(),
                    "intake_date": an["MOSTRECENTENTRYDATE"],
                    "shelter_id": "2c4c07cf-be91-4188-a515-34e985dbb2e3",
                    "species": an["SPECIESNAME"].lower(),
                    "status": "found",
                    "external_id": str(an["ID"])
                }
            ]
        }

        return ro
    
    def validate(self, an: ResultRow) -> bool:
        """ Validate an animal record is ok to send """
    
        return True

