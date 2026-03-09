
import asm3.configuration
import asm3.i18n
import asm3.utils
import datetime

from .base import AbstractPublisher

from asm3.sitedefs import PETCO_LOVELOST_BASE_URL, PETCO_LOVELOST_API_KEY, BASE_URL
from asm3.typehints import Database, Dict, PublishCriteria, ResultRow, List

import sys

def create_shelter(dbo: Database) -> int:
    auth = getAuthDetails(dbo)

    headers = {
        'x-api-key': auth["apikey"],
        'Authorization': 'Bearer ' + auth["accesstoken"]
    }
    payload = {
        "address": {
            "city": asm3.configuration.organisation_town(dbo),
            "country": asm3.configuration.organisation_country(dbo),
            "line1": asm3.configuration.organisation_address(dbo),
            "line2": "",
            "postalCode": asm3.configuration.organisation_postcode(dbo),
            "state": asm3.configuration.organisation_county(dbo)
        },
        "contact": {
            "email": asm3.configuration.email(dbo),
            "phone": asm3.configuration.organisation_telephone(dbo)
        },
        "name": asm3.configuration.organisation(dbo),
        "website": asm3.configuration.organisation_website(dbo)
    }
    response = asm3.utils.post_json(f"{auth["url"]}/v2/shelters", asm3.utils.json(payload), headers)
    return response["response"]

def getAnimalDataQuery() -> str:
    return "SELECT a.ID, a.ShelterCode, a.AnimalName, a.BreedID, a.Breed2ID, a.CrossBreed, " \
        "a.Sex, a.Size, a.DateOfBirth, a.DateBroughtIn, a.Weight, a.PickupAddress, " \
        "b1.BreedName AS BreedName1, b2.BreedName AS BreedName2, " \
        "a.AnimalComments, a.AnimalComments AS WebsiteMediaNotes, " \
        "a.Neutered, a.Declawed, a.IdentichipNumber, a.Identichip2Number, s.SpeciesName, z.Size, " \
        "o.OwnerTown, o.OwnerCountry, o.OwnerAddress, o.OwnerPostcode, o.OwnerCounty " \
        "FROM animal a " \
        "INNER JOIN breed b1 ON a.BreedID = b1.ID " \
        "INNER JOIN breed b2 ON a.Breed2ID = b2.ID " \
        "INNER JOIN species s ON a.SpeciesID = s.ID " \
        "INNER JOIN lksize z ON a.Size = z.ID " \
        "LEFT OUTER JOIN lksentrytype et ON a.EntryTypeID = et.ID " \
        "LEFT OUTER JOIN entryreason er ON a.EntryReasonID = er.ID " \
        "LEFT JOIN owner o ON a.OriginalOwnerID = o.ID "

def getAuthDetails(dbo: Database, testing: bool = False) -> Dict:
    auth = {}
    if testing:
        username = "help@sheltermanager.com"
        password = "7e2c0f71-e5a4-4693-a03b-af0c8238156b"
        apikey = "DyTGYV6egOasrRIDLUcUs2FCP5kNIPjp23tVAPr9"
        url = "https://api-dev.petcolove.org"
        shelterid = "66113416-090e-468b-b484-043cd4d8413d"
    else:
        username = asm3.configuration.petcolovelost_email(dbo)
        password = asm3.configuration.petcolovelost_password(dbo)
        apikey = PETCO_LOVELOST_API_KEY
        url = PETCO_LOVELOST_BASE_URL
        shelterid = asm3.configuration.petcolovelost_shelterid(dbo)

    payload = {
        "email": username,
        "password": password
    }
    headers = {
        'x-api-key': apikey,
        'Content-Type': 'application/json'
    }

    response = asm3.utils.post_json(url + '/v2/auth/login', asm3.utils.json(payload), headers)
    responsejson = asm3.utils.json_parse(response["response"])

    return {
        "username": username,
        "password": password,
        "apikey": apikey,
        "url": url,
        "shelterid": shelterid,
        "accesstoken": responsejson["accessToken"]
    }

def getPublishedAnimals(auth) -> Dict:
    headers = {
        'x-api-key': auth["apikey"],
        'Authorization': 'Bearer ' + auth["accesstoken"]
    }
    response = asm3.utils.get_url(f'{auth["url"]}/v2/animals/?limit=25&offset=0', headers)
    return response["response"]

def purge(auth):
    animals = getPublishedAnimals(auth)
    animalsjson = asm3.utils.json_parse(animals)
    for animal in animalsjson["pets"]:
        removeAnimal(auth, animal["id"])

def removeAnimal(auth: Dict, pcllaid: str):
    headers = {
        'x-api-key': auth["apikey"],
        'Authorization': 'Bearer ' + auth["accesstoken"]
    }
    response = asm3.utils.post_data(f"{auth["url"]}/v2/animals/" + pcllaid, "", httpmethod="DELETE", headers=headers)
    return response

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
        # sql = getAnimalDataQuery() + "WHERE a.Archived = 0 AND ( s.SpeciesName = 'Dog' OR s.SpeciesName = 'Cat' ) AND et.ID = 2"
        return self.dbo.query(
            getAnimalDataQuery() +
            "WHERE a.Archived = 0 AND ( s.SpeciesName = 'Dog' OR s.SpeciesName = 'Cat' ) AND et.ID = 2 AND CrueltyCase = 0" ## Include only archived, non case stray, cats and dogs
        )

    
    def run(self, animallist: List[ResultRow] = []) -> None:
        
        self.log("Petco Love Lost Publisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        testing = False
        if animallist:
            testing = True
        
        auth = getAuthDetails(self.dbo, testing)

        cheaders = {
            'x-api-key': auth["apikey"],
            'Authorization': 'Bearer ' + auth["accesstoken"]
        }
        c = asm3.utils.get_url(f'{auth["url"]}/v2/animals/?limit=25&offset=0', cheaders)
        cjson = asm3.utils.json_parse(c["response"])
        publishedanimalids = []
        for pa in cjson["pets"]:
            publishedanimalids.append((pa["metadata"]["system_animal_id"], pa["id"]))

        if animallist:
            animals = animallist
        else:
            animals = self.getAnimalData()

        weightunit = "kg"
        if asm3.configuration.show_weight_in_lbs(self.dbo):
            weightunit = "lb"
        if asm3.configuration.show_weight_in_lbs_fraction(self.dbo):
            weightunit = "lb"

        anCount = 0
        processed_animals = []
        for an in animals:
            anCount += 1
            published = False
            for paid in publishedanimalids:
                if an["ID"] == paid[0]:
                    self.logSuccess("Skipping already published: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                    processed_animals.append(an)
                    published = True
                    continue
            if published: continue
            try:
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))
                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return
                if not self.validate(an): continue
                headers = {
                    'x-api-key': auth["apikey"],
                    'Authorization': 'Bearer ' + auth["accesstoken"]
                }
                payload = self.processAnimal(an, auth["shelterid"], weightunit)
                r = asm3.utils.post_json(f"{auth["url"]}/v2/animals", asm3.utils.json(payload), headers)

                if r["status"] == 201:
                    responsejson = asm3.utils.json_parse(r["response"])
                    pcllid = responsejson["id"]
                    # testing = True
                    if testing:
                        # Won't accept imageurls from non https connections so using a placeholder when testing
                        photourls = ["https://sheltermanager.com/images/bg-hero-pets.png",]
                        
                    else:
                        photourls = self.getPhotoUrls(an["ID"])
                    imagepayload = {"photos": []}
                    for photourl in photourls:
                        imagepayload["photos"].append({"url": photourl.replace("sheltermanager.com/service", "sheltermanager.com/dev/service")}) ## Tweak to allow photos through to Petco Love Lost on dev server
                        # imagepayload["photos"].append({"url": photourl})
                    pr = asm3.utils.post_json(f"{auth["url"]}/v2/animals/{pcllid}/photos", asm3.utils.json(imagepayload), headers)
                    self.log("pr = " + str(pr))
                    self.log("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                    processed_animals.append(an)
                else:
                    self.logError("status != 201: HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        if len(processed_animals) > 0:
            self.log("successfully published %d animals, marking sent" % len(processed_animals))
            self.markAnimalsPublished(processed_animals)
        
        ## Unpublish animals that were not in animallist
        removalcount = 0
        for p in publishedanimalids:
            pvalid = False
            for an in animals:
                if p[0] == an["ID"]:
                    pvalid = True
            if not pvalid:
                removeAnimal(auth, p[1])
                removalcount = removalcount + 1
        self.log("Removed %s obsolete animals" % ( str(removalcount)))

        self.saveLog()
        self.setPublisherComplete()
    
    def processAnimal(self, an: ResultRow, shelterid: str, weightunit: str) -> Dict:
        """ Generate a dictionary of data to post from an animal record """
        
        ## Weight must be an integer number of ounces
        weight = 0
        if weightunit == "kg":
            weight = an["WEIGHT"] * 35.274
            weight = int(round(weight, 0))
        else:
            weight = an["WEIGHT"] * 16
        
        breed = an["BREEDNAME1"]
        if an["BREEDNAME2"]:
            breed = breed + " " + an["BREEDNAME2"]
        
        chip = an["IDENTICHIPNUMBER"]
        if an["IDENTICHIP2NUMBER"]:
            chip = chip + " " + an["IDENTICHIP2NUMBER"]
        
        description = an["ANIMALCOMMENTS"]

        if not an["PICKUPADDRESS"]:
            an["PICKUPADDRESS"] = ", ".join(
                (asm3.configuration.organisation_address(self.dbo), asm3.configuration.organisation_postcode(self.dbo))
            )

        # Build the POST data
        ro = {
            "externalId": an["SHELTERCODE"],
            "displayId": an["SHELTERCODE"],
            "birthDate": asm3.i18n.format_date(an["DATEOFBIRTH"]),
            "description": description,
            "address": {
                "city": "",
                "country": "",
                "line1": an["PICKUPADDRESS"],
                "line2": "",
                "postalCode": "",
                "state": ""
            },
            "intakeDate": asm3.i18n.format_date(an["DATEBROUGHTIN"]),
            "name": an["ANIMALNAME"],
            "metadata": {
                "system_animal_id": an["ID"]
            },
            "microchip": chip,
            "shelterId": shelterid,
            "species": an["SPECIESNAME"].lower(),
            "status": "found",
            "size": an["SIZE"].upper(),
            "altered": an["NEUTERED"] == 1, 
            "breed": breed,
            "weight": weight
        }

        if an["SPECIESNAME"].lower() == "cat":
            ro["declawed"] = an["DECLAWED"] == 1
        
        if an["SEX"] == 0:
            ro["sex"] = "female"
        else:
            ro["sex"] = "male"

        return ro
    
    def validate(self, an: ResultRow) -> bool:
        """ Validate an animal record is ok to send """
    
        return True

