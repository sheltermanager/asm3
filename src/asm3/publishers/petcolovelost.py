
import asm3.configuration
import asm3.i18n
import asm3.utils
import datetime

from .base import AbstractPublisher

from asm3.sitedefs import PETCO_LOVELOST_BASE_URL, PETCO_LOVELOST_API_KEY, BASE_URL
from asm3.typehints import Database, Dict, PublishCriteria, ResultRow, Results, List

import sys

# ID type keys used in the ExtraIDs column
IDTYPE_PETCOLOVELOST = "petcolovelost"

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
        "b1.BreedName AS BreedName1, b2.BreedName AS BreedName2, a.ExtraIds, " \
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

def getAuthDetails(dbo: Database) -> Dict:
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

def getActualPublishedAnimals(auth: Dict) -> Dict:
    ## This is hidden from public, just useful for testing/debugging
    headers = {
        'x-api-key': auth["apikey"],
        'Authorization': 'Bearer ' + auth["accesstoken"]
    }
    response = asm3.utils.get_url(f'{auth["url"]}/v2/animals/?limit=100&offset=0', headers)
    return response["response"]

def getRecordedPublishedAnimals(dbo: Database) -> Results:
    return dbo.query(
        getAnimalDataQuery() +
        f"INNER JOIN animalpublished ap ON ap.AnimalID = a.ID WHERE ap.PublishedTo = '{IDTYPE_PETCOLOVELOST}'"
    )

def purgeActualPublished(auth: Dict):
    animals = getActualPublishedAnimals(auth)
    animalsjson = asm3.utils.json_parse(animals)
    for animal in animalsjson["pets"]:
        removeAnimal(auth, animal["id"])

def purgeImages(auth: Dict, pcllaid: str):
    headers = {
        'x-api-key': auth["apikey"],
        'Authorization': 'Bearer ' + auth["accesstoken"]
    }
    asm3.utils.post_data(f"{auth["url"]}/v2/animals/{pcllaid}/photos", "", httpmethod="DELETE", headers=headers)

def purgeRecordedPublished(publisher: AbstractPublisher):
    for publishedanimal in getRecordedPublishedAnimals(publisher.dbo):
        publisher.markAnimalUnpublished(publishedanimal["ID"])
    for an in publisher.dbo.query(getAnimalDataQuery() + f"WHERE a.ExtraIDs LIKE '%{IDTYPE_PETCOLOVELOST}%'"):
        asm3.animal.remove_extra_id(publisher.dbo, "pub::petcolovelost", an, IDTYPE_PETCOLOVELOST)

def removeAnimal(auth: Dict, pcllaid: str) -> Dict:
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
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("petcolovelost", "Petcolovelost Publisher")
        self.dbo = dbo
    
    def getAnimalData(self) -> str:
        return self.dbo.query(
            getAnimalDataQuery() +
            "WHERE a.Archived = 0 AND ( s.SpeciesName = 'Dog' OR s.SpeciesName = 'Cat' ) AND et.ID = 2 AND CrueltyCase = 0" ## Include only archived, non case stray, cats and dogs
        )

    
    def run(self) -> None:
        
        self.log("Petco Love Lost Publisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()
        
        auth = getAuthDetails(self.dbo)
        
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
            try:
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return

                headers = {
                    'x-api-key': auth["apikey"],
                    'Authorization': 'Bearer ' + auth["accesstoken"]
                }
                payload = self.processAnimal(an, auth["shelterid"], weightunit)

                # Do we already have a PetcoLoveLost ID for this animal?
                # This function returns empty string for no animalid
                pcllid = asm3.animal.get_extra_id(self.dbo, an, IDTYPE_PETCOLOVELOST)

                if pcllid:
                    # Update existing post
                    self.log("Updating: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                    del payload["shelterId"]
                    del payload["species"]
                    r = asm3.utils.patch_json(f"{auth["url"]}/v2/animals/{pcllid}", asm3.utils.json(payload), headers)
                else:
                    # Create new post
                    self.log("Creating: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                    r = asm3.utils.post_json(f"{auth["url"]}/v2/animals", asm3.utils.json(payload), headers)

                if r["status"] in (200, 201):
                    responsejson = asm3.utils.json_parse(r["response"])
                    if not pcllid:
                        pcllid = responsejson["id"]
                    asm3.animal.set_extra_id(self.dbo, "pub::petcolovelost", an, IDTYPE_PETCOLOVELOST, pcllid)
                    purgeImages(auth, pcllid)
                    photourls = self.getPhotoUrls(an["ID"])
                    if len(photourls):
                        imagepayload = {"photos": []}
                        for photourl in photourls:

                            ## Tweak to allow photos through to Petco Love Lost on dev server, may be swapped for line below when live
                            imagepayload["photos"].append({"url": photourl.replace("sheltermanager.com/service", "sheltermanager.com/dev/service")}) 
                            # imagepayload["photos"].append({"url": photourl})

                        pr = asm3.utils.post_json(f"{auth["url"]}/v2/animals/{pcllid}/photos", asm3.utils.json(imagepayload), headers)
                        prjson = asm3.utils.json_parse(pr["response"])
                        if "id" in prjson.keys():
                            self.log(f"Successfully processed {len(photourls)} x photo")
                        else:
                            self.log(f"Error processing photo(s): {prjson["message"]}")
                    else:
                        self.log(f"No photos found")
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                    processed_animals.append(an)
                else:
                    self.logError("Error: HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        if len(processed_animals) > 0:
            self.log("successfully published %d animals, marking sent" % len(processed_animals))
            self.markAnimalsPublished(processed_animals)
        
        # animalids_to_cancel = set([ str(x.ID) for x in published_animals if x.ID not in processed_animals])
        removalcount = 0
        animals_to_remove = set([ an for an in getRecordedPublishedAnimals(self.dbo) if an not in processed_animals])
        for an in animals_to_remove:
            pcllid = asm3.animal.get_extra_id(self.dbo, an, IDTYPE_PETCOLOVELOST)
            if pcllid:
                removeAnimal(auth, pcllid)
            asm3.animal.remove_extra_id(self.dbo, "pub::petcolovelost", an, IDTYPE_PETCOLOVELOST)
            removalcount += 1
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
