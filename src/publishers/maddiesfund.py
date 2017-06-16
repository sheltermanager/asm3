#!/usr/bin/python

import animal
import configuration
import db
import i18n
import lookups
import sys
import utils

from base import AbstractPublisher
from sitedefs import MADDIES_FUND_TOKEN_URL, MADDIES_FUND_UPLOAD_URL, SERVICE_URL

class MaddiesFundPublisher(AbstractPublisher):
    """
    Handles updating recent adoptions with Maddies Fund via their API
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("maddiesfund", "Maddies Fund Publisher")

    def getAge(self, dob, speciesid):
        """ Returns an age banding based on date of birth and species """
        # Kitten (0-8 weeks) = 1, Kitten/Juvenile (9 weeks- 5 months) = 2, Adult Cat (6 months - 8 years) =3,
        # Senior Cat (9 years) = 4, Puppy (0-8 weeks) = 5, Puppy/Juvenile (9 weeks 11-months) =6, Adult Dog (1
        # year - 7 years) =7, Senior Dog (8 years) = 8
        ageinyears = i18n.date_diff_days(dob, i18n.now())
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

    def getDate(self, d):
        """ Returns a date in their preferred format of mm/dd/yyyy """
        return i18n.format_date("%m/%d/%Y", d)

    def run(self):
        
        self.log("Maddies Fund Publisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        email = configuration.maddies_fund_email(self.dbo)
        password = configuration.maddies_fund_password(self.dbo)
        organisation = configuration.organisation(self.dbo)

        if email == "" or password == "":
            self.setLastError("email and password all need to be set for Maddies Fund Publisher")
            self.cleanup()
            return

        cutoff = i18n.subtract_days(i18n.now(self.dbo.timezone), 31)
        animals = db.query(self.dbo, animal.get_animal_query(self.dbo) + " WHERE a.ActiveMovementType IN (1,2) AND " \
            "a.ActiveMovementDate >= %s AND a.DeceasedDate Is Null AND a.NonShelterAnimal = 0 "
            "ORDER BY a.ID" % db.dd(cutoff))
        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            return

        # Get an authentication token
        token = ""
        try:
            fields = {
                "username": email,
                "password": password,
                "grant_type": "password"
            }
            r = utils.post_form(MADDIES_FUND_TOKEN_URL, fields)
            token = utils.json_parse(r["response"])["access_token"]
            self.log("got access token: %s (%s)" % (token, r["response"]))
        except Exception as err:
            self.setLastError("failed to get access token: %s (request: '%s') (response: '%s')" % (err, r["requestbody"], r["response"]))
            self.cleanup()
            return

        anCount = 0
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

                # Build an adoption JSON object containing the adopter and animal
                a = {
                    "PetID": an["ID"],
                    "Site": organisation,
                    "PetName": an["ANIMALNAME"],
                    "PetStatus": utils.iif(an["ACTIVEMOVEMENTTYPE"] == 1, "Adopted", "Active"),
                    "PetLitterID": an["ACCEPTANCENUMBER"],
                    "GroupType": an["ACCEPTANCENUMBER"] is not None or "",
                    "PetSpecies": an["SPECIESNAME"],
                    "PetSex": an["SEXNAME"],
                    "DateofBirth": self.getDate(an["DATEOFBIRTH"]), 
                    "SpayNeuterStatus": utils.iif(an["NEUTERED"] == 1, "Spayed/Neutered", ""),
                    "Breed": an["BREEDNAME"],
                    "Color": an["BASECOLOURNAME"],
                    "SecondaryColor": "",
                    "Pattern": "",
                    "HealthStatus": an["ASILOMARINTAKECATEGORY"] + 1, # We're zero based, they use 1-base
                    "PetBiography": an["ANIMALCOMMENTS"],
                    "Photo": "%s?method=animal_image&account=%s&animalid=%s" % (SERVICE_URL, self.dbo.database, an["ID"]),
                    "Microchip": an["IDENTICHIPNUMBER"],
                    "MicrochipIssuer": lookups.get_microchip_manufacturer(self.dbo.locale, an["IDENTICHIPNUMBER"]),
                    "RelationshipType": utils.iif(an["ACTIVEMOVEMENTTYPE"] == 1, "Adoption", "Foster"),
                    "FosterCareDate": self.getDate(an["ACTIVEMOVEMENTDATE"]),
                    "FosterEndDate": "",
                    "RabiesTag": an["RABIESTAG"],

                    "ID": an["CURRENTOWNERID"],
                    "Firstname": an["CURRENTOWNERFORENAMES"],
                    "Lastname": an["CURRENTOWNERSURNAME"],
                    "EmailAddress": an["CURRENTOWNEREMAILADDRESS"],
                    "Street": an["CURRENTOWNERADDRESS"],
                    "Apartment": "",
                    "City": an["CURRENTOWNERTOWN"],
                    "State": an["CURRENTOWNERCOUNTY"],
                    "Zipcode": an["CURRENTOWNERPOSTCODE"],
                    "ContactNumber": an["CURRENTOWNERHOMETELEPHONE"],
                    "Organization": organisation,
                }

                # Send the animal as a json document. We're doing them one at a time as 
                # its better for error reporting and their endpoint times out with large
                # volumes of data.
                j = utils.json({ "Animals": [ a ] })
                headers = { "Authorization": "Bearer %s" % token }
                self.log("HTTP POST request %s: headers: '%s', body: '%s'" % (MADDIES_FUND_UPLOAD_URL, headers, j))
                r = utils.post_json(MADDIES_FUND_UPLOAD_URL, j, headers)
                if r["status"] != 200:
                    self.logError("HTTP %d response: %s" % (r["status"], r["response"]))
                else:
                    self.log("HTTP %d response: %s" % (r["status"], r["response"]))
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                    processed.append(an)

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (an["SHELTERCODE"], err), sys.exc_info())

        self.markAnimalsPublished(processed)
        self.saveLog()
        self.setPublisherComplete()


