
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
    """
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
        fname = f"{self.dbo.installpath}static/publishers/petrescue/{sname}.json"
        prbreeds = asm3.utils.json_parse(asm3.utils.read_text_file(fname))
        for d in prbreeds:
            if d["name"] == bname:
                return bname
        self.log(f"'{bname}' is not a valid PetRescue breed, using default '{default_breed}'")
        return default_breed

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
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    self.cleanup()
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
                    url = PETRESCUE_URL + "listings/%s/SM%s" % (an.ID, self.dbo.database)

                    self.log("Sending PATCH to %s to update existing listing: %s" % (url, jsondata))
                    r = asm3.utils.patch_json(url, jsondata, headers=headers)

                    if r["status"] == 200 or (r["status"] == 401 and r["response"].find("not_found") != -1):
                        self.log("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                        self.logSuccess("%s - %s: Marked with new status %s" % (an.SHELTERCODE, an.ANIMALNAME, status))
                        # Update animalpublished for this animal with the status we just sent in the Extra field
                        # so that it can be picked up next time.
                        self.markAnimalPublished(an.ID, extra = status)
                    else:
                        self.logError("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))

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

        origin = ""
        if an.ISTRANSFER == 1 and str(an.BROUGHTINBYOWNERNAME).lower().find("pound") == -1: origin = "shelter_transfer"
        elif an.ISTRANSFER == 1 and str(an.BROUGHTINBYOWNERNAME).lower().find("pound") != -1: origin = "pound_transfer"
        elif an.ORIGINALOWNERID > 0: origin = "owner_surrender"
        else: origin = "community_cat"

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
            "remote_source":            "SM%s" % self.dbo.database, # system/database identifier
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
            "intake_origin":            asm3.utils.iif(iscat, origin, ""), # cats only, community_cat | owner_surrender | pound_transfer | shelter_transfer
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


# These breed lists were retrieved by doing:
# curl -H "Content-Type: application/json"  "https://special.petrescue.com.au/api/v2/breeds?species_name=X&token=Y" > cats.json

# We use a directive to prevent flake8 choking on the long lines - # noqa: E501

DOG_BREEDS = [{"id":1,"name":"Affenpinscher"},{"id":2,"name":"Afghan Hound"},{"id":3,"name":"Airedale"},{"id":4,"name":"Akita Inu"},{"id":5,"name":"Alaskan Malamute"},{"id":6,"name":"Alsatian"},{"id":7,"name":"American Bulldog"},{"id":8,"name":"American Eskimo Dog"},{"id":9,"name":"American Staffordshire Terrier"},{"id":10,"name":"American Water Spaniel"},{"id":11,"name":"Amstaff"},{"id":12,"name":"Anatolian Shepherd"},{"id":13,"name":"Appenzell Mountain Dog"},{"id":14,"name":"Australian Bulldog"},{"id":15,"name":"Australian Cattle Dog"},{"id":16,"name":"Australian Shepherd"},{"id":17,"name":"Australian Stumpy Tail Cattle Dog"},{"id":18,"name":"Australian terrier"},{"id":19,"name":"Azawakh (Tuareg Sloughi)"},{"id":20,"name":"Basenji"},{"id":21,"name":"Basset Fauve De Bretagne"},{"id":22,"name":"Basset Hound"},{"id":23,"name":"Beagle"},{"id":24,"name":"Bearded Collie"},{"id":25,"name":"Bedlington Terrier"},{"id":26,"name":"Belgian Shepherd - Groenendael"},{"id":27,"name":"Belgian Shepherd - Laekenois"},{"id":28,"name":"Belgian Shepherd - Malinois"},{"id":29,"name":"Belgian Shepherd - Tervueren"},{"id":30,"name":"Belgium Griffon"},{"id":31,"name":"Bergamasco Shepherd Dog"},{"id":32,"name":"Bernese Mountain Dog"},{"id":33,"name":"Bichon Frise"},{"id":34,"name":"Black Russian Terrier"},{"id":35,"name":"Bloodhound"},{"id":36,"name":"Blue Heeler"},{"id":37,"name":"Border Collie"},{"id":38,"name":"Border Terrier"},{"id":39,"name":"Borzoi (Russian Wolfhound)"},{"id":40,"name":"Boston Terrier"},{"id":41,"name":"Bouvier Des Flandres"},{"id":42,"name":"Boxer"},{"id":43,"name":"Bracco Italiano"},{"id":44,"name":"Briard"},{"id":45,"name":"British Bulldog"},{"id":46,"name":"Brittany Spaniel"},{"id":47,"name":"Brussels Griffon"},{"id":48,"name":"Bull Arab"},{"id":49,"name":"Bull Terrier"},{"id":50,"name":"Bullmastiff"},{"id":51,"name":"Cairn Terrier"},{"id":52,"name":"Canaan Dog (Kelev K'naani)"},{"id":53,"name":"Canadian Eskimo Dog"},{"id":54,"name":"Catahoula"},{"id":55,"name":"Cavalier King Charles Spaniel"},{"id":56,"name":"Central Asian Shepherd Dog"},{"id":57,"name":"Cesky Terrier"},{"id":58,"name":"Chesapeake Bay Retriever"},{"id":59,"name":"Chihuahua"},{"id":60,"name":"Chinese Crested"},{"id":61,"name":"Chow Chow"},{"id":62,"name":"Clumber Spaniel"},{"id":63,"name":"Cocker Spaniel, American"},{"id":64,"name":"Cocker Spaniel, English"},{"id":65,"name":"Collie Rough"},{"id":66,"name":"Collie Smooth"},{"id":67,"name":"Coonhound"},{"id":68,"name":"Corgi, Cardigan"},{"id":69,"name":"Corgi, Pembroke"},{"id":70,"name":"Cross breed"},{"id":71,"name":"Curly Coated Retriever"},{"id":72,"name":"Dachshund"},{"id":73,"name":"Dalmatian"},{"id":74,"name":"Dandie Dinmont Terrier"},{"id":75,"name":"Deer Hound"},{"id":76,"name":"Dingo"},{"id":77,"name":"Doberman"},{"id":78,"name":"Dogue De Bordeaux"},{"id":79,"name":"Dutch Shepherd"},{"id":80,"name":"English Setter"},{"id":81,"name":"English Springer Spaniel"},{"id":82,"name":"Eurasier"},{"id":83,"name":"Field Spaniel"},{"id":84,"name":"Finnish Lapphund"},{"id":85,"name":"Finnish Spitz"},{"id":86,"name":"Flat Coated Retriever"},{"id":87,"name":"Fox Terrier"},{"id":88,"name":"Foxhound, American"},{"id":89,"name":"Foxhound, English"},{"id":90,"name":"French Bulldog"},{"id":91,"name":"German Hunting Terrier"},{"id":92,"name":"German Pinscher"},{"id":93,"name":"German Shepherd"},{"id":94,"name":"German Shorthaired Pointer"},{"id":95,"name":"German Spitz"},{"id":96,"name":"German Wirehaired Pointer"},{"id":97,"name":"Glen of Imaal Terrier"},{"id":98,"name":"Golden Retriever"},{"id":99,"name":"Gordon Setter"},{"id":100,"name":"Great Dane"},{"id":101,"name":"Greyhound"},{"id":102,"name":"Griffon"},{"id":103,"name":"Hamiltonstovare"},{"id":104,"name":"Harrier"},{"id":105,"name":"Havanese"},{"id":106,"name":"Hungarian Puli"},{"id":107,"name":"Hungarian Vizsla"},{"id":108,"name":"Huntaway"},{"id":109,"name":"Husky"},{"id":110,"name":"Ibizan Hound"},{"id":111,"name":"Irish Setter"},{"id":112,"name":"Irish Terrier"},{"id":113,"name":"Irish Water Spaniel"},{"id":114,"name":"Irish Wolfhound"},{"id":115,"name":"Italian Corso Dog"},{"id":116,"name":"Italian Greyhound"},{"id":117,"name":"Italian Spinone"},{"id":118,"name":"Jack Russell Terrier"},{"id":119,"name":"Japanese Chin"},{"id":120,"name":"Japanese Tosa"},{"id":121,"name":"Johnson Bulldog"},{"id":122,"name":"Kangal Dog"},{"id":123,"name":"Keeshond"},{"id":124,"name":"Kelpie"},{"id":125,"name":"Kerry Blue Terrier"},{"id":126,"name":"King Charles Spaniel"},{"id":127,"name":"Komondor (Hungarian Sheepdog)"},{"id":128,"name":"Koolie"},{"id":129,"name":"Kuvasz"},{"id":130,"name":"Labradoodle"},{"id":131,"name":"Labrador"},{"id":132,"name":"Lagotto Romagnolo"},{"id":133,"name":"Lakeland Terrier"},{"id":134,"name":"Large Munsterlander"},{"id":135,"name":"Leonberger"},{"id":136,"name":"Lhasa Apso"},{"id":137,"name":"Lowchen"},{"id":138,"name":"Maltese"},{"id":139,"name":"Manchester Terrier"},{"id":140,"name":"Maremma Sheepdog"},{"id":141,"name":"Mastiff"},{"id":142,"name":"Min Pin"},{"id":143,"name":"Mini Pinscher"},{"id":144,"name":"Miniature Fox Terrier"},{"id":146,"name":"Neapolitan Mastiff"},{"id":147,"name":"Newfoundland"},{"id":148,"name":"Norfolk Terrier"},{"id":149,"name":"Norwegian Buhund"},{"id":150,"name":"Norwegian Elkhound"},{"id":151,"name":"Norwich Terrier"},{"id":152,"name":"Nova Scotia Duck Tolling Retriever"},{"id":153,"name":"Old English Sheepdog"},{"id":154,"name":"Otterhound"},{"id":155,"name":"Papillion"},{"id":156,"name":"Parsons Jack Russell Terrier"},{"id":157,"name":"Patterdale Terrier"},{"id":158,"name":"Pekingese"},{"id":159,"name":"Peruvian Hairless Dog"},{"id":160,"name":"Petit Basset Griffon Vendeen"},{"id":161,"name":"Pharoah Hound"},{"id":163,"name":"Pointer"},{"id":164,"name":"Polish Lowland Sheepdog"},{"id":165,"name":"Pomeranian"},{"id":166,"name":"Poodle"},{"id":167,"name":"Portuguese Podengo"},{"id":168,"name":"Portuguese Water Dog"},{"id":169,"name":"Pug"},{"id":170,"name":"Pumi"},{"id":171,"name":"Pyrenean Mastiff"},{"id":172,"name":"Pyrenean Mountain Dog"},{"id":173,"name":"Rat Terrier"},{"id":174,"name":"Red Heeler"},{"id":175,"name":"Red Setter"},{"id":176,"name":"Rhodesian Ridgeback"},{"id":177,"name":"Rottweiler"},{"id":178,"name":"Saint Bernard"},{"id":179,"name":"Saluki"},{"id":180,"name":"Samoyed"},{"id":181,"name":"Schipperke"},{"id":182,"name":"Schnauzer, Giant"},{"id":183,"name":"Schnauzer, Miniature"},{"id":184,"name":"Schnauzer, Standard"},{"id":185,"name":"Scottish Terrier"},{"id":186,"name":"Sealyham Terrier"},{"id":187,"name":"Shar-Pei"},{"id":188,"name":"Shetland Sheepdog"},{"id":189,"name":"Shiba Inu"},{"id":190,"name":"Shih Tzu"},{"id":191,"name":"Siberian Husky"},{"id":192,"name":"Silky Terrier"},{"id":193,"name":"Skye Terrier"},{"id":194,"name":"Sloughi"},{"id":195,"name":"Smithfield Cattle Dog"},{"id":196,"name":"Spanish Mastiff"},{"id":197,"name":"Spitz"},{"id":198,"name":"Staffordshire Bull Terrier"},{"id":199,"name":"Staffy"},{"id":200,"name":"Staghound"},{"id":201,"name":"Sussex Spaniel"},{"id":202,"name":"Swedish Lapphund"},{"id":203,"name":"Swedish Vallhund"},{"id":204,"name":"Swiss Mountain Dog"},{"id":205,"name":"Tenterfield Terrier"},{"id":206,"name":"Tibetan Mastiff"},{"id":207,"name":"Tibetan Spaniel"},{"id":208,"name":"Tibetan Terrier"},{"id":209,"name":"Timber Shepherd"},{"id":210,"name":"Weimaraner"},{"id":211,"name":"Welsh Springer Spaniel"},{"id":212,"name":"Welsh Terrier"},{"id":213,"name":"West Highland White Terrier"},{"id":214,"name":"Wheaten Terrier"},{"id":215,"name":"Whippet"},{"id":216,"name":"White Shepherd Dog"},{"id":217,"name":"Yorkshire Terrier"},{"id":344,"name":"Terrier"},{"id":352,"name":"Wolfhound"},{"id":382,"name":"Ridgeback"},{"id":443,"name":"Sheltie"},{"id":460,"name":"English"},{"id":473,"name":"Mixed"},{"id":591,"name":"Papillon"},{"id":1414,"name":"Welsh Corgi"},{"id":2118,"name":"Tan"},{"id":2508,"name":"Hairless"},{"id":2625,"name":"American"},{"id":3991,"name":"Bull Terrier (Miniature)"},{"id":4006,"name":"Crested"},{"id":4266,"name":"Fox"},{"id":4534,"name":"Silver"},{"id":6748,"name":"Harlequin"},{"id":6781,"name":"Rex"},{"id":7843,"name":"Turkish Kangal"},{"id":8265,"name":"Mixed Breed"},{"id":8505,"name":"American Staffordshire Bull Terrier"},{"id":124069,"name":"Prague Ratter"},{"id":165093,"name":"Sarplaninac"},{"id":180330,"name":"English Toy Terrier"}] # noqa: E501

CAT_BREEDS = [{"id":218,"name":"Abyssinian"},{"id":219,"name":"American Curl"},{"id":220,"name":"American Shorthair"},{"id":221,"name":"Angora"},{"id":222,"name":"Asian"},{"id":223,"name":"Australian Mist"},{"id":224,"name":"Balinese"},{"id":225,"name":"Bengal"},{"id":226,"name":"Birman"},{"id":227,"name":"Bombay"},{"id":228,"name":"British Blue"},{"id":229,"name":"British Longhair"},{"id":230,"name":"British Shorthair"},{"id":231,"name":"Burmese"},{"id":232,"name":"Burmilla"},{"id":233,"name":"Chartreux"},{"id":234,"name":"Chinchilla"},{"id":235,"name":"Cornish Rex"},{"id":236,"name":"Cymric"},{"id":237,"name":"Devon Rex"},{"id":238,"name":"Domestic Long Hair"},{"id":240,"name":"Domestic Short Hair"},{"id":241,"name":"Egyptian Mau"},{"id":242,"name":"European Shorthair"},{"id":243,"name":"Exotic Shorthair"},{"id":244,"name":"Foreign White"},{"id":245,"name":"German Rex"},{"id":246,"name":"Havana"},{"id":247,"name":"Himalayan"},{"id":248,"name":"Japanese Bobtail"},{"id":249,"name":"Javanese"},{"id":250,"name":"Korat (Si-Sawat)"},{"id":251,"name":"LaPerm"},{"id":252,"name":"Layanese"},{"id":253,"name":"Maine Coon"},{"id":254,"name":"Manx"},{"id":255,"name":"Moggie"},{"id":256,"name":"Munchkin"},{"id":257,"name":"Nebelung"},{"id":258,"name":"Norwegian Forest Cat"},{"id":259,"name":"Ocicat"},{"id":260,"name":"Oriental"},{"id":261,"name":"Persian"},{"id":262,"name":"Polydactyl Cat"},{"id":263,"name":"Ragdoll"},{"id":264,"name":"Russian Blue"},{"id":265,"name":"Savannah Cat"},{"id":266,"name":"Scottish Fold"},{"id":267,"name":"Scottish Shorthair"},{"id":268,"name":"Selkirk Rex"},{"id":269,"name":"Siamese"},{"id":270,"name":"Siberian Cat"},{"id":271,"name":"Singapura"},{"id":272,"name":"Snowshoe"},{"id":273,"name":"Somali"},{"id":274,"name":"Sphynx"},{"id":275,"name":"Tonkinese"},{"id":276,"name":"Toyger"},{"id":277,"name":"Turkish Van"},{"id":4506,"name":"Lilac"},{"id":8247,"name":"Domestic Medium Hair"},{"id":8431,"name":"Ragamuffin"},{"id":22453,"name":"Australian Tiffanie"}] # noqa: E501

RABBIT_BREEDS = [{"id":295,"name":"American"},{"id":296,"name":"American Fuzzy Lop"},{"id":297,"name":"American Sable"},{"id":298,"name":"Angora"},{"id":299,"name":"Belgian Hare"},{"id":300,"name":"Beveren"},{"id":301,"name":"Britannia Petit"},{"id":302,"name":"British Giant"},{"id":303,"name":"Bunny"},{"id":304,"name":"Californian"},{"id":305,"name":"Californian Dwarf"},{"id":306,"name":"Cashmere"},{"id":307,"name":"Champagne D'argent"},{"id":308,"name":"Checkered Giant"},{"id":309,"name":"Cinnamon"},{"id":310,"name":"Dutch"},{"id":311,"name":"Dwarf"},{"id":312,"name":"Dwarf lop"},{"id":313,"name":"English"},{"id":314,"name":"English Lop"},{"id":315,"name":"English Spot"},{"id":316,"name":"Flemish Giant"},{"id":317,"name":"Florida White"},{"id":318,"name":"Fox"},{"id":319,"name":"French Angora"},{"id":320,"name":"French Lop"},{"id":321,"name":"Harlequin"},{"id":322,"name":"Havana"},{"id":323,"name":"Himalayan Dwarf"},{"id":324,"name":"Holland Lop"},{"id":325,"name":"Hotot"},{"id":326,"name":"Jersey Wooly"},{"id":327,"name":"Lilac"},{"id":328,"name":"Lop Eared"},{"id":329,"name":"Mini Lop"},{"id":330,"name":"Mini Rex"},{"id":331,"name":"Netherland Dwarf"},{"id":332,"name":"New Zealand White"},{"id":333,"name":"Palomino"},{"id":334,"name":"Papillon"},{"id":335,"name":"Polish"},{"id":336,"name":"Polish Dwarf"},{"id":337,"name":"Rex"},{"id":338,"name":"Rhinelander"},{"id":339,"name":"Satin"},{"id":340,"name":"Silver"},{"id":341,"name":"Silver Fox"},{"id":342,"name":"Silver Marten"},{"id":343,"name":"Tan"},{"id":8670,"name":"Domestic"},{"id":29250,"name":"Dutch giants"}] # noqa: E501

HORSE_BREEDS = [{"id":93986,"name":"Andalusian"},{"id":93987,"name":"Appaloosa"},{"id":93988,"name":"Arab"},{"id":93989,"name":"Australian Miniture Horse"},{"id":93990,"name":"Australian Pony Studbook"},{"id":93991,"name":"Australian Stock Horse"},{"id":93992,"name":"Brumby"},{"id":93993,"name":"Cleveland Bay Horse"},{"id":93994,"name":"Clydesdale"},{"id":93995,"name":"Connemara"},{"id":93996,"name":"Dartmoor Pony"},{"id":93997,"name":"Donkey"},{"id":93998,"name":"Draught"},{"id":93999,"name":"Fjord"},{"id":94000,"name":"Friesian"},{"id":94001,"name":"Gaited"},{"id":94002,"name":"Grade"},{"id":94003,"name":"Hackney"},{"id":94004,"name":"Haflinger"},{"id":94005,"name":"Hanovarian"},{"id":94006,"name":"Highland Pony"},{"id":94007,"name":"Holsteiner"},{"id":94008,"name":"Horse"},{"id":94009,"name":"Irish Draught Horse"},{"id":94010,"name":"Lippizaner"},{"id":94011,"name":"Missouri Foxtrotter"},{"id":94012,"name":"Morgan"},{"id":94013,"name":"Mustang"},{"id":94014,"name":"New Forest Pony"},{"id":94015,"name":"Paint/Pinto"},{"id":94016,"name":"Palamino"},{"id":94017,"name":"Paso Fino"},{"id":94018,"name":"Percheron"},{"id":94019,"name":"Peruvian Paso"},{"id":94020,"name":"Pony"},{"id":94021,"name":"Quarter Horse"},{"id":94022,"name":"Saddlebred"},{"id":94023,"name":"Shetland Pony"},{"id":94024,"name":"Shire"},{"id":94025,"name":"Standardbred"},{"id":94026,"name":"Tennessee Walker"},{"id":94027,"name":"Thoroughbred"},{"id":94028,"name":"Trakehner"},{"id":94029,"name":"Waler"},{"id":94030,"name":"Warmblood"},{"id":94031,"name":"Welsh Mountain Pony"}] # noqa: E501

