
import asm3.configuration
import asm3.i18n
import asm3.utils
import datetime

from .base import AbstractPublisher

from asm3.sitedefs import PETCO_LOVELOST_BASE_URL, PETCO_LOVELOST_API_KEY
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
        self.initLog("petcolovelost", "Petcolovelost Publisher")
        self.dbo = dbo
    
    def getAnimalData(self) -> str:
        return self.dbo.query(
            "SELECT a.ID, a.ShelterCode, a.AnimalName, a.BreedID, a.Breed2ID, a.CrossBreed, " \
            "x.Sex, a.Size, a.DateOfBirth, a.MostRecentEntryDate, a.Fee, a.Weight, " \
            "b1.BreedName AS BreedName1, b2.BreedName AS BreedName2, " \
            "a.EntryTypeID, et.EntryTypeName AS EntryTypeName, er.ReasonName AS EntryReasonName, " \
            "a.AnimalComments, a.AnimalComments AS WebsiteMediaNotes, a.IsNotAvailableForAdoption, " \
            "a.Neutered, a.IsGoodWithDogs, a.IsGoodWithCats, a.IsGoodWithChildren, a.IsHouseTrained, " \
            "a.IsCourtesy, a.Declawed, a.CrueltyCase, a.HasSpecialNeeds, " \
            "a.IdentichipNumber, s.SpeciesName, z.Size " \
            "FROM animal a " \
            "INNER JOIN lksex x ON a.Sex = x.ID " \
            "INNER JOIN breed b1 ON a.BreedID = b1.ID " \
            "INNER JOIN breed b2 ON a.Breed2ID = b2.ID " \
            "INNER JOIN species s ON a.SpeciesID = s.ID " \
            "INNER JOIN lksize z ON a.Size = z.ID " \
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

        # petcolovelostusername = asm3.configuration.petcolovelost_email(self.dbo)
        # petcolovelostpassword = asm3.configuration.petcolovelost_password(self.dbo)

        petcolovelostusername = "help@sheltermanager.com"
        petcolovelostpassword = "7e2c0f71-e5a4-4693-a03b-af0c8238156b"

        ## Get Auth token
        #conn = http.client.HTTPSConnection("{{base-partner-url}}")
        payload = {
            "email": petcolovelostusername,
            "password": petcolovelostpassword
        }
        headers = {
            'x-api-key': PETCO_LOVELOST_API_KEY,
            'Content-Type': 'application/json'
        }

        response = asm3.utils.post_json(PETCO_LOVELOST_BASE_URL + '/v2/auth/login', asm3.utils.json(payload), headers)

        responsejson = asm3.utils.json_parse(response["response"])
        accesstoken = responsejson["accessToken"]

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
                # jsondata = asm3.utils.json(fields)
                url = f"{PETCO_LOVELOST_BASE_URL}/animals"
                # self.log("Sending POST to %s: %s" % (url, jsondata))
                headers = {
                    'x-api-key': PETCO_LOVELOST_API_KEY,
                    'Authorization': 'Bearer ' + accesstoken
                }
                payload = self.processAnimal(an)
                r = asm3.utils.post_json(url, asm3.utils.json(payload), headers)

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
        
        sex = an["SEX"].lower()
        if sex == "unknown":
            sex = "other"
        
        weight = 0
        if an["WEIGHT"]:
            weight = an["WEIGHT"]

        # Build the POST data
        ro = {
            "externalId": an["SHELTERCODE"],
            "birthDate": an["DATEOFBIRTH"],
            "description": "", ## Do we have a field that we can inject here without risking giving out private information??
            "intakeDate": an["MOSTRECENTENTRYDATE"],
            "name": an["ANIMALNAME"],
            # "metadata": {
            #     "custom_key": "custom_value",
            #     "system_animal_id": 456723
            # },
            "microchip": an["IDENTICHIPNUMBER"], ## Add support for multiple chips??
            "sex": sex,
            "shelterId": "{{shelter-id}}", ## Insert our shelter id
            "species": an["SPECIESNAME"],
            "status": "found",
            "size": an["SIZE"],
            "declawed": an["DECLAWED"],
            "altered": an["NEUTERED"],
            "breed": an["BREEDNAME1"], ## Add support for multiple breeds
            "weight": weight,
            "kennelId": "12345" ## Add internal location support??
        }

        return ro
    
    def validate(self, an: ResultRow) -> bool:
        """ Validate an animal record is ok to send """
    
        return True

