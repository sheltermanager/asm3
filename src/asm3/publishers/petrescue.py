
import asm3.configuration
import asm3.i18n
import asm3.medical
import asm3.utils

from .base import AbstractPublisher
from asm3.sitedefs import PETRESCUE_URL
from asm3.typehints import Database, Dict, List, PublishCriteria, ResultRow

import sys

class PetRescuePublisher(AbstractPublisher):
    """
    Handles publishing to petrescue.com.au

    Note: Requires json files of breeds that are stored in static/publishers/petrescue
    """
    breeds = None
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("petrescue", "PetRescue Publisher")

    def get_breed_names(self, an: ResultRow) -> List[str]:
        """
        Returns a list of breeds for the animal.
        """
        if an.CROSSBREED == 1:
            return [self.get_breed_name(an.SPECIESNAME, an.BREEDNAME1), self.get_breed_name(an.SPECIESNAME, an.BREEDNAME2)]
        else:
            return [self.get_breed_name(an.SPECIESNAME, an.BREEDNAME1)]

    def get_breed_name(self, sname: str, bname: str) -> str:
        """
        Ensures that if sname == "Cat" or "Dog" that the bname is one from our
        list 
        """
        default_breeds = {
            "Cat":  "Domestic Short Hair (DSH)",
            "Dog":  "Mixed breed",
            "Horse": "Standardbred",
            "Rabbit": "Bunny Rabbit"
        }
        if sname not in default_breeds: 
            self.log("No mappings for species '%s'" % sname)
            return bname
        default_breed = default_breeds[sname]
        for d in self.breeds[sname]:
            if d["name"] == bname:
                return bname
        self.log(f"'{bname}' is not a valid PetRescue breed, using default '{default_breed}'")
        return default_breed
    
    def load_breeds(self):
        """ Loads PetRescue breeds from static json files into a dictionary for get_breed_name """
        self.breeds = {}
        for sp in [ "Cat", "Dog", "Horse", "Rabbit" ]:
            fname = f"{self.dbo.installpath}static/publishers/petrescue/{sp}.json"
            self.breeds[sp] = asm3.utils.json_parse(asm3.utils.read_text_file(fname))

    def run(self) -> None:
        
        self.log("PetRescuePublisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        token = asm3.configuration.petrescue_token(self.dbo)
        all_desexed = asm3.configuration.petrescue_all_desexed(self.dbo)
        #all_microchips = asm3.configuration.petrescue_all_microchips(self.dbo)
        all_microchips = True # PetRescue have an option to hide them at their end now, so we always send them
        adoptable_in = asm3.configuration.petrescue_adoptable_in(self.dbo)
        postcode = asm3.configuration.organisation_postcode(self.dbo)
        suburb = asm3.configuration.organisation_town(self.dbo)
        state = asm3.configuration.organisation_county(self.dbo)
        contact_name = asm3.configuration.organisation(self.dbo)
        contact_email = asm3.configuration.petrescue_email(self.dbo)
        if contact_email == "": contact_email = asm3.configuration.email(self.dbo)
        use_coordinator = asm3.configuration.petrescue_use_coordinator(self.dbo)
        breederid = asm3.configuration.petrescue_breederid(self.dbo)
        nswrehomingorganisationid = asm3.configuration.petrescue_nsw_rehoming_org_id(self.dbo)
        vicsourcenumber = asm3.configuration.petrescue_vic_sourcenumber(self.dbo)
        vicpicnumber = asm3.configuration.petrescue_vic_picnumber(self.dbo)
        phone_type = asm3.configuration.petrescue_phone_type(self.dbo)
        contact_number = asm3.configuration.petrescue_phone_number(self.dbo)
        if phone_type == "" or phone_type == "org": contact_number = asm3.configuration.organisation_telephone(self.dbo)
        elif phone_type == "none": contact_number = ""

        if token == "":
            self.setLastError("No PetRescue auth token has been set.")
            self.cleanup()
            return

        if postcode == "" or contact_email == "":
            self.setLastError("You need to set your organisation postcode and contact email under Settings->Options->Shelter Details->Email")
            self.cleanup()
            return

        if not self.isChangedSinceLastPublish():
            self.logSuccess("No animal/movement changes have been made since last publish")
            self.setLastError("No animal/movement changes have been made since last publish", log_error = False)
            self.cleanup()
            return

        self.load_breeds()

        animals = self.getMatchingAnimals(includeAdditionalFields=True)
        processed = []

        # Log that there were no animals, we still need to check
        # previously sent listings
        if len(animals) == 0:
            self.log("No animals found to publish.")

        headers = { "Authorization": "Token token=%s" % token, "Accept": "*/*" }

        anCount = 0
        for an in animals:
            try:
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return
      
                data = self.processAnimal(an, all_desexed, adoptable_in, suburb, state, postcode, 
                                          contact_name, contact_number, contact_email, all_microchips, use_coordinator,
                                          nswrehomingorganisationid, breederid, vicpicnumber, vicsourcenumber)

                # PetRescue will insert/update accordingly based on whether remote_id/remote_source exists
                url = PETRESCUE_URL + "listings"
                jsondata = asm3.utils.json(data)
                self.log("Sending POST to %s to create/update listing: %s" % (url, jsondata))
                r = asm3.utils.post_json(url, jsondata, headers=headers)

                if r["status"] != 200:
                    self.logError("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                    # Update animalpublished for this animal with the error code so that it's visible in the UI
                    # that we tried and what the error was.
                    errormsg = str(r["response"])
                    self.markAnimalPublished(an.ID, extra = errormsg)
                else:
                    self.log("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                    processed.append(an)

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        try:
            # Get a list of all animals that we sent to PR recently (6 months)
            prevsent = self.dbo.query("SELECT AnimalID FROM animalpublished WHERE SentDate>=? AND PublishedTo='petrescue'", [self.dbo.today(offset=-182)])
            
            # Build a list of IDs we just sent, along with a list of ids for animals
            # that we previously sent and are not in the current sent list.
            # This identifies the listings we potentially need to cancel
            animalids_just_sent = set([ x.ID for x in animals ])
            animalids_to_cancel = set([ str(x.ANIMALID) for x in prevsent if x.ANIMALID not in animalids_just_sent])

            # Get the animal records for the ones we need to cancel
            if len(animalids_to_cancel) == 0:
                animals = []
            else:
                animals = self.dbo.query("SELECT ID, ShelterCode, AnimalName, ActiveMovementDate, ActiveMovementType, DeceasedDate, " \
                    "(SELECT Extra FROM animalpublished WHERE AnimalID=a.ID AND PublishedTo='petrescue') AS LastStatus " \
                    "FROM animal a WHERE ID IN (%s)" % ",".join(animalids_to_cancel))

        except Exception as err:
            self.logError("Failed finding listings to cancel: %s" % err, sys.exc_info())

        # Cancel the inactive listings
        for an in animals:
            try:
                status = "on_hold"
                if an.ACTIVEMOVEMENTDATE is not None and an.ACTIVEMOVEMENTTYPE == 1: status = "rehomed"
                elif an.DECEASEDDATE is not None or (an.ACTIVEMOVEMENTDATE is not None and an.ACTIVEMOVEMENTTYPE != 2): status = "removed"

                # We have the last status update in the LastStatus field (which is animalpublished.Extra for this animal)
                # Don't send the same update again.
                if an.LASTSTATUS != status:

                    data = { "status": status }
                    jsondata = asm3.utils.json(data)
                    url = PETRESCUE_URL + "listings/%s/SM%s" % (an.ID, self.dbo.name())

                    self.log("Sending PATCH to %s to update existing listing: %s" % (url, jsondata))
                    r = asm3.utils.patch_json(url, jsondata, headers=headers)

                    if r["status"] == 200 or (r["status"] == 401 and r["response"].find("not_found") != -1):
                        self.log("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                        self.logSuccess("%s - %s: Marked with new status %s" % (an.SHELTERCODE, an.ANIMALNAME, status))
                        # Update animalpublished for this animal with the status we just sent in the Extra field
                        # so that it can be picked up next time.
                        self.markAnimalPublished(an.ID, extra = status)
                    else:
                        self.log("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                        self.logError("%s - %s: Error updating status to %s" % (an.SHELTERCODE, an.ANIMALNAME, status))

            except Exception as err:
                self.logError("Failed closing listing for %s - %s: %s" % (an.SHELTERCODE, an.ANIMALNAME, err), sys.exc_info())

        # Mark sent animals published
        self.markAnimalsPublished(processed, first=True)

        self.cleanup()

    def processAnimal(self, an: ResultRow, all_desexed=False, adoptable_in="", 
                      suburb="", state="", postcode="", contact_name="", contact_number="", contact_email="", 
                      all_microchips=False, use_coordinator=0,
                      nswrehomingorganisationid="", breederid="", vicpicnumber="", vicsourcenumber="") -> Dict:
        """ Processes an animal record and returns a data dictionary to upload as JSON """
        isdog = an.SPECIESID == 1
        iscat = an.SPECIESID == 2

        ageinyears = asm3.i18n.date_diff_days(an.DATEOFBIRTH, asm3.i18n.now())
       
        size = ""
        if an.SIZE == 2: size = "medium"
        elif an.SIZE < 2: size = "large"
        else: size = "small"

        coat = ""
        if an.COATTYPE == 0: coat = "short"
        elif an.COATTYPE == 1: coat = "long"
        else: coat = "medium_coat"

        origin = "owner_surrender"
        if an.ENTRYTYPEID == 3 and str(an.BROUGHTINBYOWNERNAME).lower().find("pound") == -1: origin = "shelter_transfer"
        elif an.ENTRYTYPEID == 3 and str(an.BROUGHTINBYOWNERNAME).lower().find("pound") != -1: origin = "pound_transfer"
        # Surrender, Seized, Abandoned or Born in Care
        elif an.ENTRYTYPEID in (1, 7, 8, 5): origin = "owner_surrender"
        # Stray, TNR or non-shelter cat
        elif an.ENTRYTYPEID in (2, 4) or (an.NONSHELTERANIMAL == 1 and an.SPECIESID == 2): origin = "community_cat"

        best_feature = "Looking for love"
        if "BESTFEATURE" in an and an.BESTFEATURE:
            best_feature = an.BESTFEATURE

        needs_constant_care = False
        if "NEEDSCONSTANTCARE" in an and an.NEEDSCONSTANTCARE and an.NEEDSCONSTANTCARE != "0":
            needs_constant_care = True

        bred_in_care_of_group = False
        if "BREDINCAREOFGROUP" in an and an.BREDINCAREOFGROUP and an.BREDINCAREOFGROUP != "0":
            bred_in_care_of_group = True

        needs_foster = False
        if "NEEDSFOSTER" in an and an.NEEDSFOSTER and an.NEEDSFOSTER != "0":
            needs_foster = True

        # Check whether we've been vaccinated, wormed and hw treated
        vaccinated = asm3.medical.get_vaccinated(self.dbo, an.ID)
        sixmonths = self.dbo.today(offset=-182)
        hwtreated = isdog and self.dbo.query_int("SELECT COUNT(*) FROM animalmedical WHERE LOWER(TreatmentName) LIKE ? " \
            "AND LOWER(TreatmentName) LIKE ? AND StartDate>? AND AnimalID=?", ("%heart%", "%worm%", sixmonths, an.ID)) > 0
        wormed = (isdog or iscat) and self.dbo.query_int("SELECT COUNT(*) FROM animalmedical WHERE LOWER(TreatmentName) LIKE ? " \
            "AND LOWER(TreatmentName) NOT LIKE ? AND StartDate>? AND AnimalID=?", ("%worm%", "%heart%", sixmonths, an.ID)) > 0
        # PR want a null value to hide never-treated animals, so we
        # turn False into a null.
        if not hwtreated: hwtreated = None
        if not wormed: wormed = None

        # Use the fosterer or retailer postcode, state and suburb if available
        location_postcode = postcode
        location_state_abbr = state
        location_suburb = suburb
        if an.ACTIVEMOVEMENTID and an.ACTIVEMOVEMENTTYPE in (2, 8):
            fr = self.dbo.first_row(self.dbo.query("SELECT OwnerTown, OwnerCounty, OwnerPostcode FROM adoption m " \
                "INNER JOIN owner o ON m.OwnerID = o.ID WHERE m.ID=?", [ an.ACTIVEMOVEMENTID ]))
            if fr is not None and fr.OWNERPOSTCODE: location_postcode = fr.OWNERPOSTCODE
            if fr is not None and fr.OWNERCOUNTY: location_state_abbr = fr.OWNERCOUNTY
            if fr is not None and fr.OWNERTOWN: location_suburb = fr.OWNERTOWN

        # If the option is on to use the adoption coordinator contact info, and this animal
        # has an adoption coordinator, set them. 0 = do not use, 1 = use email and phone, 2 = use email only
        if use_coordinator > 0 and an.ADOPTIONCOORDINATORNAME and an.ADOPTIONCOORDINATOREMAILADDRESS:
            contact_name = an.ADOPTIONCOORDINATORNAME
            contact_email = an.ADOPTIONCOORDINATOREMAILADDRESS
            contact_number = ""
            if use_coordinator == 1:
                contact_number = an.ADOPTIONCOORDINATORWORKTELEPHONE or an.ADOPTIONCOORDINATORMOBILETELEPHONE

        # Only send microchip_number if all_microchips is turned on, or for animals listed in or 
        # located in Victoria or New South Wales.
        # Since people can enter any old rubbish in the state field, we use postcode to figure out
        # location - 2XXX = NSW, 3XXX = VIC
        microchip_number = ""
        adoptable_in_list = adoptable_in.split(",")
        if all_microchips or ("VIC" in adoptable_in_list or "NSW" in adoptable_in_list or \
            location_postcode.startswith("2") or location_postcode.startswith("3")):
            microchip_number = asm3.utils.iif(an.IDENTICHIPPED == 1, an.IDENTICHIPNUMBER, "")

        # Construct and return a dictionary of info for this animal
        return {
            "remote_id":                str(an.ID), # animal identifier in ASM
            "remote_source":            "SM%s" % self.dbo.name(), # system/database identifier
            "name":                     an.ANIMALNAME.title(), # animal name (title case, they validate against caps)
            "shelter_code":             an.SHELTERCODE,
            "adoption_fee":             asm3.i18n.format_currency_no_symbol(self.locale, an.FEE),
            "species_name":             an.SPECIESNAME,
            "breed_names":              self.get_breed_names(an), # [breed1,breed2] or [breed1]
            "breeder_id":               breederid, # mandatory for QLD dogs born after 2017-05-26 or South Aus where bred_in_care_of_group==true after 2018-07-01
            "pic_number":               vicpicnumber, # mandatory for Victoria livestock (horses etc)
            "source_number":            vicsourcenumber, # mandatory for Victoria cats and dogs
            "rehoming_organisation_id": nswrehomingorganisationid, # required for NSW, this OR microchip or breeder_id is mandatory
            "bred_in_care_of_group":    bred_in_care_of_group, 
            "mix":                      self.isCrossBreed(an), # true | false
            "date_of_birth":            asm3.i18n.format_date(an.DATEOFBIRTH, "%Y-%m-%d"), # iso
            "gender":                   an.SEXNAME.lower(), # male | female
            "personality":              self.getDescription(an), # 20-4000 chars of free type
            "best_feature":             best_feature, # 25 chars free type, defaults to "Looking for love" requires BESTFEATURE additional field
            "location_postcode":        location_postcode, # shelter/fosterer postcode
            "location_state_abbr":      location_state_abbr, # shelter/fosterer state
            "location_suburb":          location_suburb, # shelter/fosterer suburb
            "microchip_number":         microchip_number, 
            "desexed":                  an.NEUTERED == 1 or all_desexed, # true | false, validates to always true according to docs
            "size":                     asm3.utils.iif(isdog, size, ""), # dogs only - small | medium | high
            "senior":                   isdog and ageinyears > (7 * 365), # dogs only, true | false
            "vaccinated":               vaccinated, # cats, dogs, rabbits, true | false
            "wormed":                   wormed, # cats & dogs, true | false
            "heart_worm_treated":       hwtreated, # dogs only, true | false
            "coat":                     coat, # Only applies to cats and guinea pigs, but we send for everything: short | medium_coat | long
            "intake_origin":            origin, # community_cat | owner_surrender | pound_transfer | shelter_transfer
            "incompatible_with_cats":   an.ISGOODWITHCATS == 1,
            "incompatible_with_dogs":   an.ISGOODWITHDOGS == 1,
            "incompatible_with_kids_under_5": an.ISGOODWITHCHILDREN == 1 or an.ISGOODWITHCHILDREN >= 5,
            "incompatible_with_kids_6_to_12": an.ISGOODWITHCHILDREN == 1 or an.ISGOODWITHCHILDREN == 12,
            "needs_constant_care":      needs_constant_care,
            "adoption_process":         "", # 4,000 chars how to adopt
            "contact_details_source":   "self", # self | user | group
            "contact_preferred_method": "email", # email | phone
            "display_contact_preferred_method_only": contact_number == "",
            "contact_name":             contact_name, # name of contact details owner
            "contact_number":           contact_number, # number to enquire about adoption
            "contact_email":            contact_email, # email to enquire about adoption
            "foster_needed":            needs_foster, # true | false
            "adoptable_in_abbrs":       adoptable_in_list, # array of states for adoption in: ACT NSW NT QLD SA TAS VIC WA 
            "medical_notes":            "", # DISABLED an.HEALTHPROBLEMS, # 4,000 characters medical notes
            "multiple_animals":         an.BONDEDANIMALID > 0 or an.BONDEDANIMAL2ID > 0, # More than one animal included in listing true | false
            "photo_urls":               self.getPhotoUrls(an.ID), # List of photo URL strings
            "status":                   "active" # active | removed | on_hold | rehomed 
        }


