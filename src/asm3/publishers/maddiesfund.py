
import asm3.animal
import asm3.configuration
import asm3.i18n
import asm3.medical
import asm3.movement
import asm3.lookups
import asm3.utils

from .base import AbstractPublisher
from asm3.sitedefs import MADDIES_FUND_TOKEN_URL, MADDIES_FUND_UPLOAD_URL, SERVICE_URL
from asm3.typehints import datetime, Database, Dict, PublishCriteria, ResultRow, Results

import sys

class MaddiesFundPublisher(AbstractPublisher):
    """
    Handles updating recent adoptions with Maddies Fund via their API
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("maddiesfund", "Maddies Fund Publisher")

    def getAge(self, dob: datetime, speciesid: int) -> int:
        """ Returns an age banding based on date of birth and species """
        # Kitten (0-8 weeks) = 1, Kitten/Juvenile (9 weeks- 5 months) = 2, Adult Cat (6 months - 8 years) =3,
        # Senior Cat (9 years) = 4, Puppy (0-8 weeks) = 5, Puppy/Juvenile (9 weeks 11-months) =6, Adult Dog (1
        # year - 7 years) =7, Senior Dog (8 years) = 8
        ageinyears = asm3.i18n.date_diff_days(dob, asm3.i18n.now())
        ageinyears /= 365.0
        age = 0
        # Cats
        if speciesid == 2:
            if ageinyears < 0.15: age = 1
            elif ageinyears < 0.5: age = 2
            elif ageinyears < 8: age = 3
            else: age = 4
        # Dogs
        elif speciesid == 1:
            if ageinyears < 0.15: age = 5
            elif ageinyears < 0.9: age = 6
            elif ageinyears < 8: age = 7
            else: age = 8
        return age

    def getDate(self, d: datetime) -> str:
        """ Returns a date in their preferred format of mm/dd/yyyy """
        return asm3.i18n.format_date(d, "%m/%d/%Y")

    def getEmail(self, s: str) -> str:
        """ Returns only the first email if more than one is specified """
        if s is None: return ""
        if s.strip() == "": return ""
        return s.split(",")[0].strip()

    def getPetStatus(self, an: ResultRow) -> str:
        """ Returns the pet status - Deceased, Active (on shelter), Inactive (foster/adopted) """
        if an["DECEASEDDATE"] is not None:
            return "Deceased"
        elif an["ACTIVEMOVEMENTTYPE"] == 0:
            return "Active"
        else:
            return "Inactive"

    def getRelationshipType(self, an: ResultRow) -> str:
        """ Returns the relationship type - adopted, fostered or blank for on shelter """
        if an["ACTIVEMOVEMENTTYPE"] == 1:
            return "Adoption"
        elif an["ACTIVEMOVEMENTTYPE"] == 2:
            return "Foster"
        else:
            return ""

    def getData(self, periodindays: int) -> Results:
        """ Returns the animal data for periodindays """
        # Send all fosters and adoptions for the period that haven't been sent since they last had a change.
        # (we use lastchangeddate instead of sent date because MPA want an update when a number of key
        #  animal fields change, such as neuter status, microchip info, rabies tag, etc)
        cutoff = asm3.i18n.subtract_days(asm3.i18n.now(self.dbo.timezone), periodindays)
        sql = "%s WHERE a.ActiveMovementType IN (1,2) " \
            "AND a.ActiveMovementDate >= ? AND a.DeceasedDate Is Null AND a.NonShelterAnimal = 0 " \
            "AND NOT EXISTS(SELECT AnimalID FROM animalpublished WHERE AnimalID = a.ID AND PublishedTo = 'maddiesfund' AND SentDate >= %s) " \
            "ORDER BY a.ID" % (asm3.animal.get_animal_query(self.dbo), self.dbo.sql_greatest(["a.ActiveMovementDate", "a.LastChangedDate"]))
        animals = self.dbo.query(sql, [cutoff], distincton="ID")

        # Now find animals who have been sent previously and are now deceased (using sent date against deceased to prevent re-sends) 
        sql = "%s WHERE a.DeceasedDate Is Not Null AND a.DeceasedDate >= ? AND " \
            "EXISTS(SELECT AnimalID FROM animalpublished WHERE AnimalID = a.ID AND " \
            "PublishedTo = 'maddiesfund' AND SentDate <= a.DeceasedDate)" % asm3.animal.get_animal_query(self.dbo)
        animals += self.dbo.query(sql, [cutoff], distincton="ID")

        # Now find shelter animals who have been sent previously and are back (using sent date against return to prevent re-sends)
        sql = "%s WHERE a.Archived = 0 AND " \
            "EXISTS(SELECT AnimalID FROM animalpublished WHERE AnimalID = a.ID AND " \
            "PublishedTo = 'maddiesfund' AND SentDate < " \
            "(SELECT MAX(ReturnDate) FROM adoption WHERE AnimalID = a.ID AND MovementType IN (1,2) AND ReturnDate Is Not Null))" % asm3.animal.get_animal_query(self.dbo)
        animals += self.dbo.query(sql, distincton="ID")

        # Now find animals who have been sent previously and have a new/changed vaccination since then
        sql = "%s WHERE a.Archived = 0 AND " \
            "EXISTS(SELECT p.AnimalID FROM animalpublished p INNER JOIN animalvaccination av ON av.AnimalID = a.ID WHERE p.AnimalID = a.ID AND " \
            "p.PublishedTo = 'maddiesfund' AND (p.SentDate < av.CreatedDate OR p.SentDate < av.LastChangedDate))" % asm3.animal.get_animal_query(self.dbo)
        animals += self.dbo.query(sql, distincton="ID")
        return animals

    def run(self) -> None:
        
        self.log("Maddies Fund Publisher starting...")

        BATCH_SIZE = 250 # How many animals to send in one POST
        PERIOD = 214 # How many days to go back when checking for fosters and adoptions (7 months * 30.5 = 214 days)

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        username = asm3.configuration.maddies_fund_username(self.dbo)
        password = asm3.configuration.maddies_fund_password(self.dbo)
        organisation = asm3.configuration.organisation(self.dbo)

        if username == "" or password == "":
            self.setLastError("username and password all need to be set for Maddies Fund Publisher")
            self.cleanup()
            return

        animals = self.getData(PERIOD)

        if len(animals) == 0:
            self.log("No animals found to publish.")
            self.cleanup()
            return

        if not self.isChangedSinceLastPublish():
            self.logSuccess("No animal/movement changes have been made since last publish")
            self.setLastError("No animal/movement changes have been made since last publish", log_error = False)
            self.cleanup()
            return

        # Get an authentication token
        token = ""
        try:
            fields = {
                "username": username,
                "password": password,
                "grant_type": "password"
            }
            r = asm3.utils.post_form(MADDIES_FUND_TOKEN_URL, fields)
            token = asm3.utils.json_parse(r["response"])["access_token"]
            self.log("got access token: %s (%s)" % (token, r["response"]))
        except Exception as err:
            self.setLastError("failed to get access token: %s (request: '%s') (response: '%s')" % (err, r["requestbody"], r["response"]))
            self.cleanup()
            return

        anCount = 0
        thisbatch = []
        processed = []
        for an in animals:
            try:
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    return

                a = self.processAnimal(an, organisation)

                thisbatch.append(a)
                processed.append(an)
                self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))

                # If we have hit our batch size, or this is the
                # last animal then send what we have.
                if len(thisbatch) == BATCH_SIZE or anCount == len(animals):
                    j = asm3.utils.json({ "Animals": thisbatch })
                    headers = { "Authorization": "Bearer %s" % token }
                    self.log("HTTP POST request %s: headers: '%s', body: '%s'" % (MADDIES_FUND_UPLOAD_URL, headers, j))
                    r = asm3.utils.post_json(MADDIES_FUND_UPLOAD_URL, j, headers)
                    if r["status"] != 200:
                        self.logError("HTTP %d response: %s" % (r["status"], r["response"]))
                    else:
                        self.log("HTTP %d response: %s" % (r["status"], r["response"]))
                        self.markAnimalsPublished(processed)
                    # start counting again
                    thisbatch = []
                    processed = []

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (an["SHELTERCODE"], err), sys.exc_info())

        self.cleanup()

    def processAnimal(self, an: ResultRow, organisation: str = "") -> Dict:
        """ Builds an adoption object (dict) containing the adopter and animal """
        a = {
            "PetID": an["ID"],
            "PetCode": an["SHELTERCODE"],
            "Site": organisation,
            "PetName": an["ANIMALNAME"],
            "PetStatus": self.getPetStatus(an),
            "PetLitterID": an["ACCEPTANCENUMBER"],
            "GroupType": asm3.utils.iif(asm3.utils.nulltostr(an["ACCEPTANCENUMBER"]) != "", "Litter", ""),
            "PetSpecies": an["SPECIESNAME"],
            "PetSex": an["SEXNAME"],
            "DateofBirth": self.getDate(an["DATEOFBIRTH"]), 
            "SpayNeuterStatus": asm3.utils.iif(an["NEUTERED"] == 1, "Spayed/Neutered", ""),
            "Breed": an["BREEDNAME"],
            "Color": an["BASECOLOURNAME"],
            "SecondaryColor": "",
            "Pattern": "",
            "HealthStatus": an["ASILOMARINTAKECATEGORY"] + 1, # We're zero based, they use 1-base
            "PetBiography": an["ANIMALCOMMENTS"],
            "Photo": "%s?method=animal_image&account=%s&animalid=%s" % (SERVICE_URL, self.dbo.database, an["ID"]),
            "Microchip": an["IDENTICHIPNUMBER"],
            "MicrochipIssuer": asm3.lookups.get_microchip_manufacturer(self.dbo.locale, an["IDENTICHIPNUMBER"]),
            "RelationshipType": self.getRelationshipType(an),
            "FosterCareDate": self.getDate(an["ACTIVEMOVEMENTDATE"]),
            "FosterEndDate": "",
            "RabiesTag": an["RABIESTAG"],

            "ID": an["CURRENTOWNERID"],
            "Firstname": an["CURRENTOWNERFORENAMES"],
            "Lastname": an["CURRENTOWNERSURNAME"],
            "EmailAddress": self.getEmail(an["CURRENTOWNEREMAILADDRESS"]),
            "Street": an["CURRENTOWNERADDRESS"],
            "Apartment": "",
            "City": an["CURRENTOWNERTOWN"],
            "State": an["CURRENTOWNERCOUNTY"],
            "Zipcode": an["CURRENTOWNERPOSTCODE"],
            "ContactNumber": an["CURRENTOWNERHOMETELEPHONE"],
            "Organization": organisation,
        }

        # Build a list of intake histories - use the initial one first
        ph = [
            {
                "IntakeType": an["ENTRYREASONNAME"],
                "IntakeDate": self.getDate(an["DATEBROUGHTIN"]),
                "City": asm3.utils.nulltostr(an["BROUGHTINBYOWNERTOWN"]),
                "State": asm3.utils.nulltostr(an["BROUGHTINBYOWNERCOUNTY"]),
                "LengthOwned": ""
            }
        ]
        # Then any exit movements where the animal was returned
        for ra in asm3.movement.get_animal_movements(self.dbo, an["ID"]):
            if ra["MOVEMENTTYPE"] > 0 and ra["MOVEMENTTYPE"] not in (2, 8) and ra["RETURNDATE"] is not None:
                ph.append({
                    "IntakeType": ra["RETURNEDREASONNAME"],
                    "IntakeDate": self.getDate(ra["RETURNDATE"]),
                    "City": asm3.utils.nulltostr(ra["OWNERTOWN"]),
                    "State": asm3.utils.nulltostr(ra["OWNERCOUNTY"]),
                    "LengthOwned": "" # We don't have this info
                })
        a["PetHistoryDetails"] = ph
        
        # Next add vaccination histories
        vh = []
        for v in asm3.medical.get_vaccinations(self.dbo, an["ID"]):
            vh.append({
                "VaccinationRecordNumber": str(v["ID"]),
                "VaccinationStatus": asm3.utils.iif(v["DATEOFVACCINATION"] is not None, "Completed", "Scheduled"),
                "VaccinationStatusDateTime": self.getDate(v["DATEREQUIRED"]),
                "Vaccine": v["VACCINATIONTYPE"],
                "Type": "", # Live/Killed - we don't keep this info yet, see issue #281
                "Manufacturer": asm3.utils.nulltostr(v["MANUFACTURER"]),
                "VaccineLot": asm3.utils.nulltostr(v["BATCHNUMBER"]),
                "VaccinationNotes": v["COMMENTS"],
                "Length": "", # Not sure what this value is for - advised to ignore by MPA devs
                "RevaccinationDate": self.getDate(v["DATEEXPIRES"])
            })
        a["PetVaccinationDetails"] = vh
        return a

