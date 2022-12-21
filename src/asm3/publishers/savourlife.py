
import asm3.additional
import asm3.animal
import asm3.configuration
import asm3.medical
import asm3.utils

from .base import AbstractPublisher
from asm3.sitedefs import SAVOURLIFE_URL
# from asm3.sitedefs import SAVOURLIFE_API_KEY - is this actually needed any more?

import sys

# ID type keys used in the ExtraIDs column
IDTYPE_SAVOURLIFE = "savourlife"

class SavourLifePublisher(AbstractPublisher):
    """
    Handles publishing to savourlife.com.au
    Note: They ONLY deal with dogs.
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        publishCriteria.bondedAsSingle = True
        publishCriteria.includeWithoutImage = False # SL do not want listings without images
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("savourlife", "SavourLife Publisher")

    def get_breed_id(self, breedname, crossbreed = False):
        """
        Returns a savourlife breed for a given breedname
        """
        breed = asm3.utils.nulltostr(breedname)
        if crossbreed:
            breed = "%s cross" % breed
        for k, v in DOG_BREEDS.items():
            if v.lower() == breed.lower():
                return int(k)
        self.log("'%s' is not a valid SavourLife breed, using default 'Cross Breed'" % breedname)
        return 305

    def get_state(self, s):
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

    def good_with(self, x):
        """
        Translates our good with fields Selective/Unknown/No/Yes to SOL's NULL/False/True
        """
        if x == 0: return True
        elif x == 1: return False
        else: return None

    def run(self):
        
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
            self.log("No animal/movement changes made since last publish")
            self.cleanup()
            return

        preanimals = self.getMatchingAnimals(includeAdditionalFields=True)
        animals = [ x for x in preanimals if x.SPECIESID == 1 ] # We only want dogs
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
        url = SAVOURLIFE_URL + "getToken"
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
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    self.cleanup()
                    return

                # Do we already have a SavourLife ID for this animal?
                # This function returns empty string for no dogid
                dogid = asm3.animal.get_extra_id(self.dbo, an, IDTYPE_SAVOURLIFE)

                data = self.processAnimal(an, dogid, postcode, state, suburb, token, radius, interstate, all_microchips)

                # SavourLife will insert/update accordingly based on whether DogId is null or not
                url = SAVOURLIFE_URL + "setDog"
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
                            url = SAVOURLIFE_URL + "setDogAdopted"
                            # Clear the dogId on adoption, so if the animal returns it gets a new listing
                            asm3.animal.set_extra_id(self.dbo, "pub::savourlife", an, IDTYPE_SAVOURLIFE, "")
                        elif status == "held":
                            # We're marking the listing as held. We can't just send the held flag, we have to send
                            # the entire listing again.
                            data = self.processAnimal(an, dogid, postcode, state, suburb, token, radius, interstate, all_microchips, hold=True)
                            url = SAVOURLIFE_URL + "setDog"
                        else:
                            # We're deleting the listing
                            data = {
                                "Token":        token,
                                "DogId":        dogid
                            }
                            url = SAVOURLIFE_URL + "DeleteDog"
                            # Clear the dogId since the listing has been deleted
                            asm3.animal.set_extra_id(self.dbo, "pub::savourlife", an, IDTYPE_SAVOURLIFE, "")

                        jsondata = asm3.utils.json(data)
                        self.log("Sending POST to %s to mark animal '%s - %s' %s: %s" % (url, an.SHELTERCODE, an.ANIMALNAME, status, jsondata))
                        r = asm3.utils.post_json(url, jsondata)

                        if r["status"] != 200:
                            self.logError("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
                        else:
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

    def processAnimal(self, an, dogid="", postcode="", state="", suburb="", token="", radius=0, interstate=False, all_microchips=False, hold=False):
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
        if "ENQUIRYNUMBER" in an and an.ENQUIRYNUMBER != "":
            enquirynumber = an.ENQUIRYNUMBER

        needs_foster = False
        if "NEEDSFOSTER" in an and an.NEEDSFOSTER != "" and an.NEEDSFOSTER != "0":
            needs_foster = True

        # We have a config option for interstate adoptable. If this DB has an additional
        # field for interstateadoptable on the animal with a value then we use that instead:
        if "INTERSTATEADOPTABLE" in an and an.INTERSTATEADOPTABLE != "":
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

        # Construct a dictionary of info for this animal
        d = {
            "Token":                    token,
            "DogId":                    asm3.utils.iif(dogid == "", None, dogid), # SL expect a null in this field for no dogid
            "Description":              self.getDescription(an, replaceSmart=True),
            "DogName":                  an.ANIMALNAME.title(),
            "Images":                   self.getPhotoUrls(an.ID),
            "BreedId":                  self.get_breed_id(an.BREEDNAME1, an.CROSSBREED == 1),
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
            "RequirementOtherAnimals":  None,
            "RequirementOtherCats":     self.good_with(an.ISGOODWITHCATS),
            "RequirementKidsOver5":     self.good_with(an.ISGOODWITHCHILDREN),
            "RequirementKidsUnder5":    self.good_with(an.ISGOODWITHCHILDREN),
            "SpecialNeeds":             "",
            "MedicalIssues":            self.replaceSmartQuotes(an.HEALTHPROBLEMS),
            "InterstateAdoptionAvaliable": interstate, # NB: This attribute is deliberately spelled wrong due to mispelling at SL side
            "DistanceRestriction":      asm3.utils.iif(radius == 0, None, radius),
            "FosterCareRequired":       needs_foster,
            "BondedPair":               an.BONDEDANIMALID is not None and an.BONDEDANIMALID > 0,
            "SizeWhenAdult":            size,
            "IsSaved":                  an.ACTIVEMOVEMENTTYPE == 1,
            "MicrochipDetails":         microchipdetails,
            "IsOnHold":                 hold # Typically false, but the change status code will do this
        }

        # If this animal is bonded, override its name back to the original value
        # and add info for the bonded animal
        if "BONDEDNAME1" in an:
            d["DogName"] = an.BONDEDNAME1.title()
            d["DogName2"] = an.BONDEDNAME2.title()
            d["IsMale2"] = an.BONDEDSEX == 1
            d["BreedId2"] = self.get_breed_id(an.BONDEDBREEDNAME, an.CROSSBREED == 1)
            d["DOB2"] = an.DATEOFBIRTH

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

        return d



# These breed lists were retrieved by doing:
# curl -H "Content-Type: application/json"  "https://www.savour-life.com.au/umbraco/api/sheltermanager/GetBreeds" > dogs.json

# We use a directive to prevent flake8 choking on the long lines - # noqa: E501

DOG_BREEDS = {"1":"Affenpinscher","2":"Affenpinscher cross","3":"Afghan Hound","4":"Afghan Hound cross","5":"Airedale Terrier","6":"Airedale Terrier cross","7":"Akita","8":"Akita cross","9":"Alaskan Malamute","10":"Alaskan Malamute cross","11":"Am Staff","12":"Am Staff cross","281":"American bulldogs","282":"American bulldogs Cross","300":"American Staffordshire Bull Terrier","339":"American Staffordshire Bull Terrier cross","299":"Amstaff","338":"Amstaff cross","19":"Anatolian Shepherd Dog","20":"Anatolian Shepherd Dog cross","271":"Australian Bulldog","272":"Australian Bulldog cross","21":"Australian Cattle Dog","22":"Australian Cattle Dog cross","23":"Australian Shepherd","24":"Australian Shepherd cross","25":"Australian Terrier","26":"Australian Terrier cross","377":"Bandog","378":"Bandog cross","27":"Basenji","28":"Basenji cross","29":"Basset Hound","30":"Basset Hound cross","31":"Beagle","32":"Beagle cross","33":"Bearded Collie","34":"Bearded Collie cross","35":"Beauceron","36":"Beauceron cross","37":"Bedlington Terrier","38":"Bedlington Terrier cross","39":"Belgian Malinois","40":"Belgian Malinois cross","41":"Belgian Sheepdog","42":"Belgian Sheepdog cross","302":"Belgian Shepherd","341":"Belgian Shepherd cross","43":"Belgian Tervuren","44":"Belgian Tervuren cross","45":"Bernese Mountain Dog","46":"Bernese Mountain Dog cross","47":"Bichon Frise","48":"Bichon Frise cross","49":"Biewer Terrier","50":"Biewer Terrier cross","313":"Black Mouth Cur","352":"Black Mouth Cur cross","53":"Black Russian Terrier","54":"Black Russian Terrier cross","55":"Bloodhound","56":"Bloodhound cross","51":"Boerboel","52":"Boerboel cross","57":"Border Collie","58":"Border Collie cross","59":"Border Terrier","60":"Border Terrier cross","61":"Borzoi","62":"Borzoi cross","63":"Boston Terrier","64":"Boston Terrier cross","65":"Boxer","66":"Boxer cross","67":"Briard","68":"Briard cross","73":"Brittany","74":"Brittany cross","69":"Brussels Griffon","70":"Brussels Griffon cross","273":"Bull Arab","274":"Bull Arab Cross","71":"Bull Terrier","72":"Bull Terrier cross","75":"Bulldog","76":"Bulldog cross","77":"Bullmastiff","78":"Bullmastiff cross","81":"Cairn Terrier","82":"Cairn Terrier cross","83":"Canaan Dog","84":"Canaan Dog cross","298":"Cane Corso","337":"Cane Corso cross","89":"Carolina Dog","90":"Carolina Dog cross","295":"Catahoula","304":"Catahoula","343":"Catahoula cross","296":"Catahoula cross","87":"Cavalier King Charles","88":"Cavalier King Charles cross","91":"Chesapeake Bay Retriever","92":"Chesapeake Bay Retriever cross","93":"Chihuahua","94":"Chihuahua cross","95":"Chinese Crested","96":"Chinese Crested cross","97":"Chinese Shar-Pei","98":"Chinese Shar-Pei cross","99":"Chinook","100":"Chinook cross","101":"Chow Chow","102":"Chow Chow cross","314":"Clumber Spaniel","353":"Clumber Spaniel cross","103":"Cocker spaniel","104":"Cocker spaniel cross","105":"Collie","106":"Collie cross","79":"Coonhound","80":"Coonhound cross","85":"Corgi","86":"Corgi cross","305":"Cross Breed","344":"Cross Breed cross","107":"Curly-Coated Retriever","108":"Curly-Coated Retriever cross","109":"Dachshund","110":"Dachshund cross","111":"Dalmatian","112":"Dalmatian cross","315":"Dandie Dinmont Terrier","354":"Dandie Dinmont Terrier cross","297":"Deer Hound","336":"Deer Hound cross","287":"Dingo","288":"Dingo cross","113":"Doberman Pinscher","114":"Doberman Pinscher cross","291":"Dogue De Bordeaux","292":"Dogue De Bordeaux cross","185":"Duck Retreiver","186":"Duck Retreiver cross","316":"Dutch Shepherd","355":"Dutch Shepherd cross","325":"Elkhound","364":"Elkhound cross","117":"English Bulldog","118":"English Bulldog cross","119":"English Foxhound","120":"English Foxhound cross","121":"English Pointer","122":"English Pointer cross","123":"English Setter","124":"English Setter cross","317":"Finnish Lapphund","356":"Finnish Lapphund cross","127":"Flat Coated Retriever","128":"Flat Coated Retriever cross","283":"Fox Terrier","284":"Fox Terrier cross","13":"Foxhound","14":"Foxhound cross","129":"French Bulldog","130":"French Bulldog cross","293":"French Mastiff","294":"French Mastiff cross","131":"German Pinscher","132":"German Pinscher cross","133":"German Shepherd","134":"German Shepherd cross","289":"German Shorthaired Pointer","306":"German shorthaired pointer","345":"German shorthaired pointer cross","290":"German Shorthaired Pointer Cross","385":"German Spitz","386":"German Spitz cross","387":"German Wirehaired pointer","388":"German Wirehaired pointer cross","135":"Giant Schnauzer","136":"Giant Schnauzer cross","137":"Golden Retriever","138":"Golden Retriever cross","139":"Goldendoodle","140":"Goldendoodle cross","141":"Gordon Setter","142":"Gordon Setter cross","143":"Great Dane","144":"Great Dane cross","145":"Great Pyrenees","146":"Great Pyrenees cross","147":"Greater Swiss Mountain Dog","148":"Greater Swiss Mountain Dog cross","149":"Greyhound","150":"Greyhound cross","318":"Harrier","357":"Harrier cross","151":"Havanese","115":"Havanese","116":"Havanese cross","152":"Havanese cross","312":"Heinz 57","351":"Heinz 57 cross","335":"Huntaway","374":"Huntaway cross","153":"Irish Setter","154":"Irish Setter cross","155":"Irish Terrier","156":"Irish Terrier cross","159":"Italian Greyhound","160":"Italian Greyhound cross","301":"Italian Mastiff","340":"Italian Mastiff cross","161":"Jack Russell Terrier","162":"Jack Russell Terrier cross","163":"Japanese Chin","164":"Japanese Chin cross","307":"Japanese spitz","346":"Japanese spitz cross","165":"Keeshond","166":"Keeshond cross","269":"Kelpie","270":"Kelpie cross","319":"Komondor","358":"Komondor cross","309":"Koolie","277":"Koolie","278":"Koolie cross","348":"Koolie cross","167":"Labradoodle","168":"Labradoodle cross","169":"Labrador Retriever","170":"Labrador Retriever cross","320":"Lagotto Romagnolo","359":"Lagotto Romagnolo cross","125":"Lapphund","126":"Lapphund cross","321":"Leonberger","360":"Leonberger cross","171":"Lhasa Apso","172":"Lhasa Apso cross","322":"Lowchen","361":"Lowchen cross","175":"Maltese","176":"Maltese cross","323":"Manchester Terrier","362":"Manchester Terrier cross","279":"Maremma Sheepdog ","280":"Maremma Sheepdog  Cross","177":"Mastiff","178":"Mastiff cross","285":"Mini Fox Terrier","286":"Mini Fox Terrier Cross","179":"Miniature Bull Terrier","180":"Miniature Bull Terrier cross","181":"Miniature Pinscher","182":"Miniature Pinscher cross","383":"Miniature Poodle","384":"Miniature Poodle cross","183":"Miniature Schnauzer","184":"Miniature Schnauzer cross","265":"Mixed Breed","266":"Mixed Breed cross","308":"Murray Valley CC Retreiver","347":"Murray Valley CC Retreiver cross","275":"Neopolitan Mastiff ","276":"Neopolitan Mastiff cross","375":"Neopolitan Mastiff","376":"Neopolitan Mastiff cross","187":"Newfoundland","188":"Newfoundland cross","324":"Norfolk Terrier","363":"Norfolk Terrier cross","326":"Norwich Terrier","365":"Norwich Terrier cross","189":"Old English Sheepdog","190":"Old English Sheepdog cross","191":"Otterhound","192":"Otterhound cross","193":"Papillon","194":"Papillon cross","195":"Pekingese","196":"Pekingese cross","197":"Pharaoh Hound","198":"Pharaoh Hound cross","15":"Pit Bull Terrier","16":"Pit Bull Terrier cross","199":"Pointer","200":"Pointer cross","203":"Pomeranian","204":"Pomeranian cross","201":"Poodle","205":"Poodle - Standard","206":"Poodle - Standard cross","207":"Poodle - Toy","208":"Poodle - Toy cross","202":"Poodle cross","209":"Portuguese Water Dog","210":"Portuguese Water Dog cross","211":"Pug","212":"Pug cross","213":"Puli","214":"Puli cross","219":"Rat Terrier","220":"Rat Terrier cross","267":"Rescued (our favourite breed)","268":"Rescued (our favourite breed) cross","215":"Rhodesian Ridgeback","216":"Rhodesian Ridgeback cross","217":"Rottweiler","218":"Rottweiler cross","379":"Rough Collie","380":"Rough Collie cross","221":"Saint Bernard","222":"Saint Bernard cross","327":"Saluki","366":"Saluki cross","223":"Samoyed","224":"Samoyed cross","311":"Sarplaninac","350":"Sarplaninac cross","328":"Schipperke","367":"Schipperke cross","381":"Scotch Collie","382":"Scotch Collie cross","225":"Scottish Terrier","226":"Scottish Terrier cross","227":"Sealyham Terrier","228":"Sealyham Terrier cross","229":"Sheltie","230":"Sheltie cross","231":"Shetland Sheepdog","232":"Shetland Sheepdog cross","329":"Shiba Inu","368":"Shiba Inu cross","233":"Shih Tzu","234":"Shih Tzu cross","235":"Siberian Husky","236":"Siberian Husky cross","330":"Silky Terrier","369":"Silky Terrier cross","241":"Skye Terrier","242":"Skye Terrier cross","310":"Smithfield","349":"Smithfield cross","239":"Spitz","240":"Spitz cross","243":"Springer Spaniel","244":"Springer Spaniel cross","245":"Staffordshire Bull Terrier","246":"Staffordshire Bull Terrier cross","334":"Staghound","373":"Staghound cross","247":"Standard Schnauzer","248":"Standard Schnauzer cross","237":"Terrier","173":"Terrier","303":"Terrier","342":"Terrier cross","332":"Terrier Cross","174":"Terrier cross","238":"Terrier cross","371":"Terrier Cross cross","251":"Tibetan Mastiff","252":"Tibetan Mastiff cross","249":"Tibetan Spaniel","250":"Tibetan Spaniel cross","253":"Vizsla","254":"Vizsla cross","17":"Water spaniel","18":"Water spaniel cross","255":"Weimaraner","256":"Weimaraner cross","257":"Welsh Terrier","258":"Welsh Terrier cross","259":"West Highland White Terrier","260":"West Highland White Terrier cross","331":"Wheaten Terrier","370":"Wheaten Terrier cross","261":"Whippet","262":"Whippet cross","333":"White swiss shepherd","372":"White swiss shepherd cross","157":"Wolfhound","158":"Wolfhound cross","263":"Yorkshire Terrier","264":"Yorkshire Terrier cross"} # noqa: E501


