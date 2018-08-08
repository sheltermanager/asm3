#!/usr/bin/python

import configuration
import i18n
import medical
import sys
import utils

from base import AbstractPublisher
from sitedefs import SERVICE_URL, PETRESCUE_URL, PETRESCUE_AUTH_TOKEN

class PetRescuePublisher(AbstractPublisher):
    """
    Handles publishing to petrescue.com.au
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("petrescue", "PetRescue Publisher")

    def run(self):
        
        self.log("PetRescuePublisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        # TODO: Is the Auth Token for all of ASM or per organisation? Assuming ASM.

        animals = self.getMatchingAnimals()
        processed = []

        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            self.cleanup()
            return

        postcode = configuration.organisation_postcode(self.dbo)
        contact_name = configuration.organisation(self.dbo)
        contact_email = configuration.email(self.dbo)
        contact_number = configuration.organisation_telephone(self.dbo)


        headers = { "Authorization": "Token token=%s" % PETRESCUE_AUTH_TOKEN }

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
       
                isdog = an.SPECIESID == 1
                iscat = an.SPECIESID == 2

                ageinyears = i18n.date_diff_days(an.DATEOFBIRTH, i18n.now())

                vaccinated = medical.get_vaccinated(self.dbo, an.ID)
                
                size = ""
                if an.SIZE == 2: size = "medium"
                elif an.SIZE < 2: size = "high"
                else: size = "small"

                coat = ""
                if an.COATTYPE == 0: coat = "short"
                elif an.COATTYPE == 1: coat = "long"
                else: coat = "medium_coat"

                origin = ""
                if an.ORIGINALOWNERID > 0: origin = "owner_surrender"
                elif an.ISTRANSFER == 1: origin = "shelter_transfer"

                photo_url = "%s?account=%s&method=animal_image&animalid=%d" % (SERVICE_URL, self.dbo.database, an.ID)

                # Construct a dictionary of info for this animal
                data = {
                    "remote_id":                str(an.ID), # animal identifier in ASM
                    "remote_source":            "SM%s" % self.dbo.database, # system/database identifier
                    "name":                     an.ANIMALNAME, # animal name
                    "adoption_fee":             str(an.FEE * 100),
                    "species_name":             an.SPECIESNAME,
                    "breed_names":              "%s,%s" % (an.BREEDNAME1, an.BREEDNAME2), # breed1,breed2
                    "mix":                      utils.iif(an.CROSSBREED == 1, "true", "false"), # true | false
                    "date_of_birth":            i18n.format_date("%Y-%m-%d", an.DATEOFBIRTH), # iso
                    "gender":                   an.SEXNAME.lower(), # male | female
                    "personality":              "", # 20-4000 chars of free type
                    "postcode":                 postcode, # shelter postcode
                    "microchip_number":         an.IDENTICHIPNUMBER, 
                    "desexed":                  utils.iif(an.NEUTERED == 1, "true", "false"), # true | false, validates to always true according to docs
                    "contact_method":           "email", # email | phone
                    "size":                     utils.iif(isdog, size, ""), # dogs only - small | medium | high
                    "senior":                   utils.iif(isdog and ageinyears > 7, "true", "false"), # dogs only, true | false
                    "vaccinated":               utils.iif(vaccinated, "true", "false"), # cats, dogs, rabbits, true | false
                    "wormed":                   utils.iif(vaccinated, "true", "false"), # cats & dogs, true | false
                    "heart_worm_treated":       utils.iif(vaccinated, "true", "false"), # dogs only, true | false
                    "coat":                     utils.iif(iscat, coat, ""), # cats only, short | medium_coat | long
                    "intake_origin":            utils.iif(iscat, origin, ""), # cats only, community_cat | owner_surrender | pound_transfer | shelter_transfer
                    "adoption_process":         "", # 4,000 chars how to adopt
                    "contact_details_source":   "self", # self | user | group
                    "contact_preferred_method": "email", # email | phone
                    "contact_name":             contact_name, # name of contact details owner
                    "contact_number":           contact_number, # number to enquire about adoption
                    "contact_email":            contact_email, # email to enquire about adoption
                    "foster_needed":            "false", # true | false
                    "interstate":               "true", # true | false - can the animal be adopted to another state
                    "medical_notes":            an.HEALTHPROBLEMS, # 4,000 characters medical notes
                    "multiple_animals":         "false", # More than one animal included in listing true | false
                    "photo_urls":               photo_url, # Comma separated photo URL strings
                    "status":                   "active" # active | removed | on_hold | rehomed | suspended | group_suspended
                }

                # Has this animal been sent previously? 
                lastsent = self.dbo.query_date("SELECT SentDate FROM animalpublished WHERE AnimalID=? AND PublishedTo='petrescue'", [an.ID])

                # No - send a new listing
                if lastsent is None:

                    r = utils.post_json(PETRESCUE_URL + "listings", utils.json(data), headers=headers)

                    if r["status"] != 200:
                        self.logError("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                    else:
                        self.log("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                        self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                        processed.append(an)

                # Yes - send a PATCH to the existing listing TODO: disabled for now
                else:
                    self.log("Nothing to do, listing already sent.")
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Next, identify animals we've previously sent who:
        # 1. Have an active exit movement in the last month or died in the last month
        # 2. Have an entry in animalpublished/petrescue where the sent date is older than the active movement
        # 3. Have an entry in animalpublished/petrescue where the sent date is older than the deceased date

        animals = self.dbo.query("SELECT a.ID, a.ShelterCode, a.AnimalName, p.SentDate, a.ActiveMovementDate, a.DeceasedDate FROM animal a " \
            "INNER JOIN animalpublished p ON p.ID = a.AnimalID AND p.PublishedTo='petrescue' " \
            "WHERE Archived = 1 AND ((DeceasedDate Is Not Null AND DeceasedDate >= ?) OR (ActiveMovementDate Is Not Null AND ActiveMovementType NOT IN (2,8))) " \
            "ORDER BY a.ID", [self.dbo.today(offset=-30)])

        for an in animals:
            if an.SENTDATE < an.ACTIVEMOVEMENT or an.SENTDATE < an.DECEASEDDATE:
                
                status = utils.iif(an.DECEASEDDATE is not None, "removed", "rehomed")
                self.logSuccess("%s - %s: Marking with new status %s" % (an.SHELTERCODE, an.ANIMALNAME, status))

                r = utils.patch_json(PETRESCUE_URL + "listings/%s/SM%s" % (an.ID, self.dbo.database), utils.json({ "status": status }), headers=headers)

                if r["status"] != 200:
                    self.logError("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                else:
                    self.log("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                    # By marking these animals in the processed list again, their SentDate
                    # will become today, which should exclude them from sending these status
                    # updates in future
                    processed.append(an)

        # Mark sent animals published
        self.markAnimalsPublished(processed, first=True)

        self.cleanup()


