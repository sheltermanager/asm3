
import asm3.additional
import asm3.animal
import asm3.configuration
import asm3.medical
import asm3.utils

from .base import AbstractPublisher
from asm3.sitedefs import SAVOURLIFE_URL
from asm3.typehints import Database, Dict, PublishCriteria, ResultRow

import sys

# ID type keys used in the ExtraIDs column
IDTYPE_SAVOURLIFE = "savourlife"

# Endpoints
ENDPOINT_SET = f"{SAVOURLIFE_URL}SetAnimal"
ENDPOINT_ADOPTED = f"{SAVOURLIFE_URL}SetAnimalAdopted"
ENDPOINT_DELETE = f"{SAVOURLIFE_URL}DeleteAnimal"
ENDPOINT_TOKEN = f"{SAVOURLIFE_URL}GetAnimalAdminByToken"

class SavourLifePublisher(AbstractPublisher):
    """
    Handles publishing to savourlife.com.au
    Note: They ONLY deal with dogs and cats.
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        publishCriteria.bondedAsSingle = True
        publishCriteria.includeWithoutImage = False # SL do not want listings without images
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("savourlife", "SavourLife Publisher")
    
    def load_breeds(self):
        """ Loads SavourLife breeds from static json files into a dictionary for get_breed_id 
            The static files were downloaded from the SavourLife API with Curl:
            curl -H "Content-Type: application/json" https://www.savour-life.com.au/umbraco/api/sheltermanager/GetBreeds?animalType=Cat > Cat.json
            curl -H "Content-Type: application/json" https://www.savour-life.com.au/umbraco/api/sheltermanager/GetBreeds?animalType=Dog > Dog.json
        """
        self.breeds = {}
        for sp in [ "Cat", "Dog" ]:
            fname = f"{self.dbo.installpath}static/publishers/savourlife/{sp}.json"
            self.breeds[sp] = asm3.utils.json_parse(asm3.utils.read_text_file(fname))

    def get_breed_id(self, speciesname: str, breedname: str, crossbreed: bool = False) -> int:
        """
        Returns a savourlife breed for a given breedname
        """
        default_breeds = {
            "Cat":  "422", # DSH
            "Dog":  "305"  # Crossbreed
        }
        if speciesname not in default_breeds: 
            self.logError(f"Invalid species '{speciesname}', cannot load breed data")
            return 305
        breeddata = self.breeds[speciesname]
        breed = asm3.utils.nulltostr(breedname).lower()
        breed = " ".join(breed.split()) # this suppresses whitespace, eg: "    foo    bar" becomes "foo bar"
        breedid = -1
        if crossbreed and speciesname == "Dog":
            breed = "%s cross" % breed
        for k, v in breeddata.items():
            v = v.lower()
            v = " ".join(v.split()) # suppress whitespace
            if v == breed:
                breedid = int(k)
                break
        if breedid == -1:
            breedid = default_breeds[speciesname]
            self.log(f"Could not find matching breed for '{breedname}', using default breed {breedid}")
        return int(breedid)

    def get_state(self, s: str) -> str:
        """
        Returns an Australian state abbreviation or empty string if a state name could not be found in s.
        If s is already a 2 or 3 letter code, we just return it.
        """
        if len(s) == 2 or len(s) == 3: return s.upper()
        states = {
            "NSW":  [ "New South Wales", "ales" ],
            "QLD":  [ "Queensland", "ueen" ],
            "SA":   [ "South Australia", "outh" ],
            "TAS":  [ "Tasmania", "mania" ],
            "VIC":  [ "Victoria", "oria" ],
            "WA":   [ "Western Australia", "ester" ],
            "ACT":  [ "Australian Capital Territory", "apital" ],
            "JBT":  [ "Jervis Bay Territory", "ervis" ],
            "NT":   [ "Northern Territory", "orther" ]
        }
        for k, v in states.items():
            for p in v:
                if s.find(p) != -1:
                    return k
        return ""

    def good_with(self, x: int) -> str:
        """
        Translates our good with fields Selective/Unknown/No/Yes to SOL's NULL/False/True
        """
        if x == 0: return True # yes
        elif x == 1: return False # no
        elif x == 3: return True # selective
        else: return None # unknown or other

    def good_with_over5(self, x: int) -> bool:
        """ Calculates good with children over 5 """
        if x == 0 or x == 5: return True # Yes or Over 5
        if x == 2: return None # Unknown
        return False

    def good_with_under5(self, x: int) -> bool:
        """ Calculates good with children under 5 """
        if x == 0: return True # Yes
        if x == 2: return None # Unknown
        return False

    def run(self) -> None:
        
        self.log("SavourLifePublisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        token = asm3.configuration.savourlife_token(self.dbo)
        interstate = asm3.configuration.savourlife_interstate(self.dbo)
        all_microchips = asm3.configuration.savourlife_all_microchips(self.dbo)
        radius = asm3.configuration.savourlife_radius(self.dbo)
        postcode = asm3.configuration.organisation_postcode(self.dbo)
        suburb = asm3.configuration.organisation_town(self.dbo)
        state = asm3.configuration.organisation_county(self.dbo)

        if token == "":
            self.setLastError("No SavourLife token has been set.")
            self.cleanup()
            return

        if postcode == "" or suburb == "" or state == "":
            self.setLastError("You need to set your organisation address and postcode under Settings->Options->Shelter Details")
            self.cleanup()
            return

        if not self.isChangedSinceLastPublish():
            self.logSuccess("No animal/movement changes have been made since last publish")
            self.setLastError("No animal/movement changes have been made since last publish", log_error = False)
            return

        self.load_breeds()

        preanimals = self.getMatchingAnimals(includeAdditionalFields=True)
        animals = [ x for x in preanimals if x.SPECIESID == 1 or x.SPECIESID == 2 ] # We only want dogs and cats
        processed = []

        # Log that there were no animals, we still need to check
        # previously sent listings
        if len(animals) == 0:
            self.log("No animals found to publish.")

        # Redundant code, we used to have to pass a username and password to get a token, but as of Feb 2022, the token itself should be configured
        """
        username = asm3.configuration.savourlife_username(self.dbo)
        password = asm3.configuration.savourlife_password(self.dbo)
        # Authenticate first to get our token
        url = ENDPOINT_TOKEN
        jsondata = '{ "Username": "%s", "Password": "%s", "Key": "%s" }' % ( username, password, SAVOURLIFE_API_KEY )
        self.log("Token request to %s: %s" % ( url, jsondata)) 
        try:
            r = asm3.utils.post_json(url, jsondata)
            if r["status"] != 200:
                self.setLastError("Authentication failed.")
                self.logError("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                self.cleanup()
                return
            token = r["response"].replace("\"", "")
            self.log("Token received: %s" % token)
        except Exception as err:
            self.setLastError("Authentication failed.")
            self.logError("Failed getting token: %s" % err, sys.exc_info())
            self.cleanup()
            return
        """
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

                # Do we already have a SavourLife ID for this animal?
                # This function returns empty string for no dogid
                dogid = asm3.animal.get_extra_id(self.dbo, an, IDTYPE_SAVOURLIFE)

                data = self.processAnimal(an, dogid, postcode, state, suburb, token, radius, interstate, all_microchips)

                # SavourLife will insert/update accordingly based on whether DogId is null or not
                url = ENDPOINT_SET
                jsondata = asm3.utils.json(data)
                self.log("Sending POST to %s to create/update listing: %s" % (url, jsondata))
                r = asm3.utils.post_json(url, jsondata)

                if r["status"] != 200:
                    self.logError("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                else:
                    self.log("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                    processed.append(an)

                    # If we didn't have a dogid, extract it from the response and store it
                    # so future postings will update this dog's listing.
                    if dogid == "":
                        dogid = r["response"]
                        asm3.animal.set_extra_id(self.dbo, "pub::savourlife", an, IDTYPE_SAVOURLIFE, dogid)  

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        try:
            # Get a list of all animals that we sent to SOL recently (6 months)
            prevsent = self.dbo.query("SELECT AnimalID FROM animalpublished WHERE SentDate>=? AND PublishedTo='savourlife'", [self.dbo.today(offset=-182)])
            
            # Build a list of IDs we just sent, along with a list of ids for animals
            # that we previously sent and are not in the current sent list.
            # This identifies the listings we need to cancel
            animalids_just_sent = set([ x.ID for x in animals ])
            animalids_to_cancel = set([ str(x.ANIMALID) for x in prevsent if x.ANIMALID not in animalids_just_sent])

            # Get the animal records for the ones we need to mark saved or remove
            if len(animalids_to_cancel) > 0:

                animals = self.dbo.query(asm3.animal.get_animal_query(self.dbo) + "WHERE a.ID IN (%s)" % ",".join(animalids_to_cancel))

                # Append the additional fields so we can get the enquiry number
                asm3.additional.append_to_results(self.dbo, animals, "animal")

                # Cancel the inactive listings - we can either mark a dog as adopted, held, or we can delete the listing.
                anCount = 0
                for an in animals:
                    anCount += 1
                    try:
                        status = "removed"
                        # this will pick up trials as well as full adoptions
                        if an.ACTIVEMOVEMENTDATE is not None and an.ACTIVEMOVEMENTTYPE == 1:
                            status = "adopted"
                        elif an.ARCHIVED == 0: # animal is still in care but not adoptable
                            status = "held"

                        # Get the previous status for this animal from animalpublished.Extra
                        # Don't send the same update again.
                        laststatus = self.dbo.query_string("SELECT Extra FROM animalpublished WHERE AnimalID=? AND PublishedTo='savourlife'", [an.ID])
                        if laststatus == status: continue

                        # The savourlife dogid field that they returned when we first sent the record
                        dogid = asm3.animal.get_extra_id(self.dbo, an, IDTYPE_SAVOURLIFE)

                        # If there isn't a dogid, stop now because we can't do anything
                        if dogid == "": continue

                        data = {}
                        url = ""
                        if status == "adopted":
                            # The enquiry number is given by the savourlife website to the potential adopter,
                            # they pass it on to the shelter (who should add it to the animal record) so
                            # that it's set when we mark the animal adopted with savourlife. This gets the
                            # new adopter free food.
                            enquirynumber = None
                            if "ENQUIRYNUMBER" in an and an.ENQUIRYNUMBER != "":
                                enquirynumber = an.ENQUIRYNUMBER
                            data = {
                                "Token":        token,
                                "DogId":        dogid,
                                "EnquiryNumber": enquirynumber
                            }
                            url = ENDPOINT_ADOPTED
                            # Clear the dogId on adoption, so if the animal returns it gets a new listing
                            asm3.animal.set_extra_id(self.dbo, "pub::savourlife", an, IDTYPE_SAVOURLIFE, "")
                        elif status == "held":
                            # We're marking the listing as held. We can't just send the held flag, we have to send
                            # the entire listing again.
                            data = self.processAnimal(an, dogid, postcode, state, suburb, token, radius, interstate, all_microchips, hold=True)
                            url = ENDPOINT_SET
                        else:
                            # We're deleting the listing
                            data = {
                                "Token":        token,
                                "DogId":        dogid
                            }
                            url = ENDPOINT_DELETE

                        jsondata = asm3.utils.json(data)
                        self.log("Sending POST to %s to mark animal '%s - %s' %s: %s" % (url, an.SHELTERCODE, an.ANIMALNAME, status, jsondata))
                        
                        r = asm3.utils.post_json(url, jsondata)

                        if r["status"] != 200:
                            self.logError("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                        else:
                            if url == ENDPOINT_DELETE:
                                # Clear the dogId since the listing has been deleted
                                asm3.animal.set_extra_id(self.dbo, "pub::savourlife", an, IDTYPE_SAVOURLIFE, "")
                            self.log("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                            self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))

                            # Update animalpublished for this animal with the status we just sent in the Extra field
                            # so that it can be picked up next time and we won't do this again.
                            self.markAnimalPublished(an.ID, extra = status)

                    except Exception as err:
                        self.logError("Failed updating listing for %s - %s: %s" % (an.SHELTERCODE, an.ANIMALNAME, err), sys.exc_info())

        except Exception as err:
            self.logError("Failed finding potential dogs to mark adopted: %s" % err, sys.exc_info())

        # Mark sent animals published
        self.markAnimalsPublished(processed, first=True)

        self.cleanup()

    def processAnimal(self, an: ResultRow, dogid="", postcode="", state="", suburb="", token="", radius=0, interstate=False, all_microchips=False, hold=False) -> Dict:
        """ Processes an animal record and returns a data dictionary for upload as JSON """
        # Size is 10 = small, 20 = medium, 30 = large, 40 = x large
        size = ""
        if an.SIZE == 2: size = 20
        elif an.SIZE < 2: size = 30
        else: size = 10

        # They're probably going to need this at some point, but current API doesn't have it
        # and they've set a global breeder number value for the whole organisation
        #breeder_id = ""
        #if "BREEDERID" in an and an.BREEDERID != "":
        #    breeder_id = an.BREEDERID

        # The enquiry number is given by the savourlife website to the potential adopter,
        # they pass it on to the shelter (who should add it to the animal record) so
        # that it's set when we mark the animal adopted with savourlife. This gets the
        # new adopter free food.
        # It's unlikely that there will be an enquirynumber while the animal is still adoptable
        # but it's possible so we check it here just in case.
        enquirynumber = None
        if "ENQUIRYNUMBER" in an and an.ENQUIRYNUMBER:
            enquirynumber = an.ENQUIRYNUMBER

        needs_foster = False
        if "NEEDSFOSTER" in an and an.NEEDSFOSTER and an.NEEDSFOSTER != "0":
            needs_foster = True
        
        indoor_only = False
        if "INDOORONLY" in an and an.INDOORONLY and an.INDOORONLY != "0":
            indoor_only = True

        medical_issues = ""
        if "MEDICALISSUES" in an and an.MEDICALISSUES:
            medical_issues = an.MEDICALISSUES

        # We have a config option for interstate adoptable. If this DB has an additional
        # field for interstateadoptable on the animal with a value then we use that instead:
        if "INTERSTATEADOPTABLE" in an and an.INTERSTATEADOPTABLE:
            interstate = an.INTERSTATEADOPTABLE != "0"

        # Check whether we've been vaccinated, wormed and hw treated
        vaccinated = asm3.medical.get_vaccinated(self.dbo, an.ID)
        sixmonths = self.dbo.today(offset=-182)
        hwtreated = self.dbo.query_int("SELECT COUNT(*) FROM animalmedical WHERE LOWER(TreatmentName) LIKE ? " \
            "AND LOWER(TreatmentName) LIKE ? AND StartDate>? AND AnimalID=?", ("%heart%", "%worm%", sixmonths, an.ID)) > 0
        wormed = self.dbo.query_int("SELECT COUNT(*) FROM animalmedical WHERE LOWER(TreatmentName) LIKE ? " \
            "AND LOWER(TreatmentName) NOT LIKE ? AND StartDate>? AND AnimalID=?", ("%worm%", "%heart%", sixmonths, an.ID)) > 0
        # PR want a null value to hide never-treated animals, so we
        # turn False into a null.
        if not hwtreated: hwtreated = None
        if not wormed: wormed = None

        # Use the fosterer or retailer postcode, state and suburb if available
        location_postcode = postcode
        location_state_abbr = self.get_state(state)
        location_suburb = suburb
        if an.ACTIVEMOVEMENTID and an.ACTIVEMOVEMENTTYPE in (2, 8):
            fr = self.dbo.first_row(self.dbo.query("SELECT OwnerTown, OwnerCounty, OwnerPostcode FROM adoption m " \
                "INNER JOIN owner o ON m.OwnerID = o.ID WHERE m.ID=?", [ an.ACTIVEMOVEMENTID ]))
            if fr is not None and fr.OWNERPOSTCODE: location_postcode = fr.OWNERPOSTCODE
            if fr is not None and fr.OWNERCOUNTY: location_state_abbr = self.get_state(fr.OWNERCOUNTY)
            if fr is not None and fr.OWNERTOWN: location_suburb = fr.OWNERTOWN

        # MicrochipDetails should be "No" if we don't have one, 
        # the actual number if all_microchips is set or we're in VIC or NSW (2XXX or 3XXX postcode)
        # or "Yes" for others.
        microchipdetails = "No"
        if an.IDENTICHIPNUMBER != "":
            if all_microchips or (location_postcode.startswith("2") or location_postcode.startswith("3")):
                microchipdetails = an.IDENTICHIPNUMBER
            else:
                microchipdetails = "Yes"
        
        coatlength = "Medium"
        if an.COATTYPENAME == "Short" or an.COATTYPENAME == "Long":
            coatlength = an.COATTYPENAME

        # Construct a dictionary of info for this animal
        d = {
            "Token":                    token,
            "DogId":                    asm3.utils.iif(dogid == "", None, dogid), # SL expect a null in this field for no dogid
            "Description":              self.getDescription(an, replaceSmart=True),
            "DogName":                  an.ANIMALNAME.title(),
            "AnimalType":               an.SPECIESNAME,
            "Images":                   self.getPhotoUrls(an.ID),
            "BreedId":                  self.get_breed_id(an.SPECIESNAME, an.BREEDNAME1, an.CROSSBREED == 1),
            "Suburb":                   location_suburb,
            "State":                    location_state_abbr,
            "Postcode":                 location_postcode,
            "DOB":                      an.DATEOFBIRTH, # json handler should translate this to ISO
            "enquiryNo":                enquirynumber, # valid enquiry number or null if we don't have one
            "AdoptionFee":              asm3.utils.cint(an.FEE) / 100.0,
            "IsDesexed":                an.Neutered == 1,
            "IsWormed":                 wormed,
            "IsVaccinated":             vaccinated,
            "IsHeartWormed":            hwtreated,
            "Code":                     an.SHELTERCODE,
            "IsMale":                   an.SEX == 1,
            "RequirementOtherDogs":     self.good_with(an.ISGOODWITHDOGS),
            #"RequirementOtherAnimals":  None, # Removed at SL request as it overrides values from their UI
            "RequirementOtherCats":     self.good_with(an.ISGOODWITHCATS),
            "RequirementKidsOver5":     self.good_with_over5(an.ISGOODWITHCHILDREN), 
            "RequirementKidsUnder5":    self.good_with_under5(an.ISGOODWITHCHILDREN),
            "SpecialNeeds":             "",
            "MedicalIssues":            self.replaceSmartQuotes(medical_issues),
            "InterstateAdoptionAvaliable": interstate, # NOTE: This attribute is deliberately spelled wrong due to mispelling at SL side
            "DistanceRestriction":      asm3.utils.iif(radius == 0, None, radius),
            "FosterCareRequired":       needs_foster,
            "IndoorOnly":               indoor_only,
            "BondedPair":               an.BONDEDANIMALID is not None and an.BONDEDANIMALID > 0,
            "SizeWhenAdult":            size,
            "IsSaved":                  an.ACTIVEMOVEMENTTYPE == 1,
            "MicrochipDetails":         microchipdetails,
            "IsOnHold":                 hold, # Typically false, but the change status code will do this
            "CoatLength":               coatlength
        }

        # If this animal is bonded, override its name back to the original value
        # and add info for the bonded animal
        if "BONDEDNAME1" in an:
            d["DogName"] = an.BONDEDNAME1.title()
            d["DogName2"] = an.BONDEDNAME2.title()
            d["IsMale2"] = an.BONDEDSEX == 1
            d["BreedId2"] = self.get_breed_id(an.SPECIESNAME, an.BONDEDBREEDNAME, an.CROSSBREED == 1)
            d["DOB2"] = an.BONDEDDATEOFBIRTH

            # MicrochipDetails2 should be "No" if we don't have one, 
            # the actual number if all_microchips is set or we're in VIC or NSW (2XXX or 3XXX postcode)
            # or "Yes" for others.
            microchipdetails2 = "No"
            if an.BONDEDMICROCHIPNUMBER != "":
                if all_microchips or (location_postcode.startswith("2") or location_postcode.startswith("3")):
                    microchipdetails2 = an.BONDEDMICROCHIPNUMBER
                else:
                    microchipdetails2 = "Yes"
            d["MicrochipDetails2"] = microchipdetails2

            # Size is 10 = small, 20 = medium, 30 = large, 40 = x large
            size2 = ""
            if an.BONDEDSIZE == 2: size2 = 20
            elif an.BONDEDSIZE < 2: size2 = 30
            else: size2 = 10
            d["SizeWhenAdult2"] = size2

        # If the dataset came from get_animal_query rather than the publisher, because we were doing a held/status
        # update, then we need to set DogName2 as SavourLife have validation that will prevent the update without it.
        elif "BONDEDANIMAL1NAME" in an and an.BONDEDANIMAL1NAME is not None:
            d["DogName2"] = an.BONDEDANIMAL1NAME

        return d
