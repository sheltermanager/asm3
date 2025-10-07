
import asm3.animal
import asm3.configuration
import asm3.i18n
import asm3.utils

from .base import AbstractPublisher, calc_microchip_data, get_microchip_data
from asm3.sitedefs import FINDPET_BASE_URL, FINDPET_API_KEY
from asm3.typehints import Database, PublishCriteria, ResultRow

import sys

# ID type keys used in the ExtraIDs column
IDTYPE_FINDPET = "findpet"

# TODO: Make this the base class and have two publishers, one for found pets fpf, one for microchips fpc
# We also need to get a geocode for the shelter address as part of the base publisher
# and store it in the config so it can be set by the code that switches currentowner for the
# shelter
class FindPetPublisher(AbstractPublisher):
    """
    Handles sending found pets and microchip registrations to findpet.com
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.uploadDirectly = True
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("findpet", "FindPet Publisher")

    def fpDate(self, d):
        """ Returns a date in the format FindPet want """
        if d is None: return ""
        return asm3.i18n.format_date(d, "%Y-%m-%d %H:%M:%S")

    def fpLonLat(self, an):
        """ Returns a FindPet [ Lon, Lat ] value """
        latlon = asm3.utils.nulltostr(an.CURRENTOWNERLATLONG).split(",")
        lat = 0
        lon = 0
        if len(latlon) > 1: 
            lat = asm3.utils.cfloat(latlon[0])
            lon = asm3.utils.cfloat(latlon[1])
        return [ lon, lat ]
    
    def fpE164(self, pn):
        """ Makes sure a US phone number is formatted to E164 +1XXXYYYZZZZ """
        if pn is None: return ""
        return "+1%s" % asm3.utils.atoi(pn)
    
    def fpPOST(self, url, jsondata):
        """ Sends the jsondata to url and returns the parsed json response or None for a failure """
        r = asm3.utils.post_json(url, jsondata)
        j = {}
        try:
            j = asm3.utils.json_parse(r["response"])
            self.log("HTTP %d, headers: %s, response: %s" % (r["status"], r["headers"], r["response"]))
            return (r["status"], j)
        except Exception as jerr:
            self.logError("Could not parse JSON response '%s' (%s), HTTP %s, headers: %s" % (r["response"], jerr, r["status"], r["headers"]))
            return (r["status"], None)

    def run(self) -> None:
        
        self.log("FindPetPublisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        orgid = asm3.configuration.findpet_org_id(self.dbo)

        if orgid == "":
            self.setLastError("No FindPet Organization ID has been set.")
            self.cleanup()
            return
        
        # Get the list of stray/hold animals
        shanimals = self.dbo.query(asm3.animal.get_animal_query(self.dbo) + " WHERE " \
            "a.Archived=0 AND (a.EntryTypeID=2 OR a.IsHold=1) ORDER BY a.MostRecentEntryDate")
        shanimals = calc_microchip_data(self.dbo, shanimals) # We do this so that we have the shelter address for reports

        # Get the list of animals that need their chips transferring
        tranimals = []
        if asm3.configuration.findpet_int_level(self.dbo) == 0:
            tranimals = get_microchip_data(self.dbo, ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], "findpet", allowintake=False)

        # Make sure we don't try to register too many chips
        if self.checkMicrochipLimit(tranimals): return

        # send any shelter animals or animals that need their chip transferring that
        # that have a microchip number, but don't already have a FindPet report_id
        self.log("Processing animal reports ...")
        anCount = 0
        processed_animals = []

        for an in shanimals + tranimals:

            anCount += 1
            self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(shanimals + tranimals)))

            # If the user cancelled, stop now
            if self.shouldStopPublishing(): 
                self.stopPublishing()
                return

            findpet_report_id = asm3.animal.get_extra_id(self.dbo, an, IDTYPE_FINDPET)
            if findpet_report_id != "": 
                self.log(f"Skipping {an.SHELTERCODE} {an.ANIMALNAME} - already reported to FindPet")
                continue

            if an.IDENTICHIPNUMBER == "": 
                self.log(f"Skipping {an.SHELTERCODE} {an.ANIMALNAME} - No microchip number")
                continue

            if not self.validate(an): 
                self.log(f"Skipping {an.SHELTERCODE} {an.ANIMALNAME} - Failed validation")
                continue

            # initiate /report with the shelter animal
            try:
                jsondata = asm3.utils.json(self.processReport(an, orgid))
                url = f"{FINDPET_BASE_URL}/api/report"
                self.log(f"Reporting {an.SHELTERCODE} {an.ANIMALNAME} to FindPet.com as \"Adopt\"")
                self.log("Sending POST to %s to create listing: %s" % (url, jsondata))

                status, j = self.fpPOST(url, jsondata)
                if status > 400 or j is None: 
                    self.logError("Validation or other errors found, skipping")
                    continue

                if j["result"].find(" ") != -1 or j["result"].find("Wrong") != -1:
                    self.logError("Got invalid report_id value '%s', skipping" % j["result"])
                    continue

                # store the report_id
                asm3.animal.set_extra_id(self.dbo, "system", an, IDTYPE_FINDPET, j["result"])
                processed_animals.append(an)

            except Exception as err:
                self.logError("Failed sending /report for animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark the reports processed but with a different publisher code so
        # that the report can be displayed/managed separately from the microchip
        self.markAnimalsPublished(processed_animals, publisherkey = "findpetr")

        processed_animals = []
        failed_animals = []
        
        # We reload the list of animals to transfer so that the extra IDs have been set above
        if asm3.configuration.findpet_int_level(self.dbo) == 0:
            tranimals = get_microchip_data(self.dbo, ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], "findpet", allowintake=False)
            # Now, we can go through the list of microchips that need to be registered
            self.log("Processing microchip registrations ...")

        anCount = 0
        for an in tranimals:
            try:
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(tranimals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(tranimals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return

                # This shouldn't happen, since we register transfer animals for a report_id above
                # if they don't have one. But if that process failed, we can't do anything here
                findpet_report_id = asm3.animal.get_extra_id(self.dbo, an, IDTYPE_FINDPET)
                if findpet_report_id == "":
                    self.logError(f"No findpet_report_id for {an.SHELTERCODE}, cannot send pet-transfer")
                    continue

                if not self.validate(an): continue
                data = self.processTransfer(an)
                jsondata = asm3.utils.json(data)

                # Send the transfer
                url = f"{FINDPET_BASE_URL}/api/pet-transfer"
                self.log("Sending POST to %s to create transfer: %s" % (url, jsondata))
                status, j = self.fpPOST(url, jsondata)
                if j is None: continue

                # Success is returned as { "result": { "status": "Passed", details: {transfer_id} } }
                # Validation/fail returned as { "result": { "status": "Failed", details: "error message" } }
                # Error codes are supposed to be returned as { "reason": "message", "details": {transfer_id} }
                if "result" in j and "status" in j["result"] and j["result"]["status"] in ("Registered", "Passed"):
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(tranimals)))
                    processed_animals.append(an)
                elif "result" in j and "status" in j["result"] and j["result"]["status"] == "Failed":
                    # If the error message is relating to the pet already being transferred,
                    # we need to put through a "cancel transfer" or "transfer back" depending on whether
                    # the owner accepted the transfer.
                    if j["result"]["details"].startswith("Report type does not support transfer"):
                        # Send both cancel and transfer back post to undo the previous registration
                        # regardless of whether the transfer was accepted or not.
                        self.log("Found 'Report type does not support transfer', cancelling previous transfer for next publisher run")
                        jsondata = asm3.utils.json({ "token": FINDPET_API_KEY, "report_id": findpet_report_id })
                        url = f"{FINDPET_BASE_URL}/api/transfer-back"
                        status, j = self.fpPOST(url, jsondata)
                        url = f"{FINDPET_BASE_URL}/api/cancel-back"
                        status, j = self.fpPOST(url, jsondata)
                    else:
                        an.FAILMESSAGE = j["result"]["details"]
                        failed_animals.append(an)
                elif "result" not in j and "reason" in j:
                    an.FAILMESSAGE = j["reason"]
                    failed_animals.append(an)
                else:
                    self.logError("did not understand the response (no { \"result\": or { \"reason\": ")

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Get a list of all animals that we sent to FindPet recently (last 6 months)
        prevsent = self.dbo.query("SELECT AnimalID FROM animalpublished WHERE SentDate>=? AND PublishedTo='findpet'", [self.dbo.today(offset=-182)])
        
        # Build a list of IDs we just sent, along with a list of ids for animals
        # that we previously sent and are not in the current sent list.
        # This identifies the listings we need to cancel
        animalids_just_sent = set([ x.ID for x in tranimals + shanimals ])
        animalids_to_cancel = set([ str(x.ANIMALID) for x in prevsent if x.ANIMALID not in animalids_just_sent])

        # Get the animal records for listings that we need to consider for removal
        # (or report deactivation as FindPet call it)
        if len(animalids_to_cancel) > 0:

            self.log("Processing listing removals ...")
            deanimals = self.dbo.query(asm3.animal.get_animal_query(self.dbo) + "WHERE a.ID IN (%s)" % ",".join(animalids_to_cancel))
            
            anCount = 0
            for an in deanimals:
                anCount += 1

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return

                try:
                    # We only remove the listing for dead animals, and those that left via 
                    # any movement that wasn't an adoption. So if the animal is alive, or is adopted, do nothing.
                    # The latter is only if we are registering microchips, if we aren't we should delete the
                    # listings for adopted animals too.
                    if an.DECEASEDDATE is None: continue
                    if an.ACTIVEMOVEMENTTYPE == 1 and asm3.configuration.findpet_int_level(self.dbo) == 0: continue

                    # If we already deactivated this report, don't do anything
                    laststatus = self.dbo.query_string("SELECT Extra FROM animalpublished WHERE AnimalID=? AND PublishedTo='findpet'", [an.ID])
                    if laststatus == "Deactivated Report": continue
                    
                    # The findpet reportid
                    findpet_report_id = asm3.animal.get_extra_id(self.dbo, an, IDTYPE_FINDPET)

                    # If there isn't a reportid, stop now because we can't do anything
                    if findpet_report_id == "": continue

                    # Send the Delete
                    jsondata = asm3.utils.json({ "token": FINDPET_API_KEY, "report_id": findpet_report_id })
                    url = f"{FINDPET_BASE_URL}/api/deactivate_report"
                    self.log("Sending POST to %s to remove report: %s" % (url, jsondata))
                    jsondata = asm3.utils.json({ "token": FINDPET_API_KEY, "report_id": findpet_report_id })
                    status, j = self.fpPOST(url, jsondata)
                    if j is None: continue

                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(deanimals)))

                    # Update animalpublished for this animal with the status we just sent in the Extra field
                    # so that it can be picked up next time and we won't do this again.
                    self.markAnimalPublished(an.ID, extra = "Deactivated Report")

                    # Clear the report_id since the listing has been deleted
                    asm3.animal.set_extra_id(self.dbo, "pub::findpet", an, IDTYPE_FINDPET, "")

                except Exception as err:
                    self.logError("Failed updating listing for %s - %s: %s" % (an.SHELTERCODE, an.ANIMALNAME, err), sys.exc_info())

        # Mark sent animals published
        if len(processed_animals) > 0:
            self.markAnimalsPublished(processed_animals)
        if len(failed_animals) > 0:
            self.markAnimalsPublishFailed(failed_animals)

        self.cleanup()

    def processReport(self, an: ResultRow, orgid: str) -> str:
        """ Processes an animal record and returns a data dictionary for upload to /api/report as JSON """
        return {
            "token": FINDPET_API_KEY,
            "report_type": "Adopt", # seems to be the value they want irrespective of whether it's nonshelter or not
            "photos": self.getPhotoUrls(an.ID),
            "videos": [],  # not used
            "adt_markings": [], # not used 
            "breeds": [ an.BREEDNAME1, an.BREEDNAME2 ], 
            "colors": [ an.BASECOLOURNAME ],
            "address": {
                "full": f"{an.CURRENTOWNERADDRESS}, {an.CURRENTOWNERTOWN}, {an.CURRENTOWNERCOUNTY}, US",
                "addressline_1": an.CURRENTOWNERADDRESS,
                "addressline_2": "",
                "city": an.CURRENTOWNERTOWN,
                "county": "",
                "state": an.CURRENTOWNERCOUNTY,
                "country": "US",
                "postal_code": an.CURRENTOWNERPOSTCODE
            },
            "location": {
                "type": "Point",
                "coordinates": self.fpLonLat(an),
            },
            "org_id": orgid, 
            "pet_name": an.ANIMALNAME,
            "pet_org_id": an.SHELTERCODE,
            "pet_type": an.SPECIESNAME,
            "contact_name": an.CURRENTOWNERNAME, 
            "email": an.CURRENTOWNEREMAILADDRESS,
            "phone": self.fpE164(an.CURRENTOWNERMOBILETELEPHONE), # e164 format
            "sms_alerts": self.fpE164(an.CURRENTOWNERMOBILETELEPHONE), # strictly e164 format
            "microchip_id": an.IDENTICHIPNUMBER,
            "event_date": self.fpDate(an.MOSTRECENTENTRYDATE),
            "date_of_birth": self.fpDate(an.DATEOFBIRTH),
            "size": an.SIZENAME,
            "gender": an.SEXNAME,
            "coat_type": an.COATTYPENAME,
            # "coat_length": "Short", # we don't have a coat length field to map so omit it
            "description": self.getDescription(an, crToBr=True),
            "show_phone": 0
        }
    
    def processTransfer(self, an: ResultRow) -> str:
        """ Processes a transfer """
        return {
            "token": FINDPET_API_KEY,
            "address": {   
                "full": f"{an.CURRENTOWNERADDRESS}, {an.CURRENTOWNERTOWN}, {an.CURRENTOWNERCOUNTY}, US",
                "addressline_1": an.CURRENTOWNERADDRESS,
                "addressline_2": "",
                "city": an.CURRENTOWNERTOWN,
                "county": "",
                "state": an.CURRENTOWNERCOUNTY,
                "country": "US",
                "postal_code": an.CURRENTOWNERPOSTCODE
            },
            "location": {
                "type": "Point",
                "coordinates": self.fpLonLat(an),
            },
            "report_id": asm3.animal.get_extra_id(self.dbo, an, IDTYPE_FINDPET),
            "name": an.CURRENTOWNERNAME, 
            "family_name": an.CURRENTOWNERSURNAME,
            "email": an.CURRENTOWNEREMAILADDRESS,
            "phone": self.fpE164(an.CURRENTOWNERMOBILETELEPHONE) 
        }

    def validate(self, an: ResultRow) -> bool:
        """ Validates a report or transfer record is ok to send """
        # Validate certain items aren't blank so we aren't registering bogus data
        if asm3.utils.nulltostr(an.CURRENTOWNERADDRESS).strip() == "":
            self.logError("Address for the new owner is blank, cannot process")
            return False 
        if asm3.utils.nulltostr(an.CURRENTOWNERPOSTCODE).strip() == "":
            self.logError("Postal code for the new owner is blank, cannot process")
            return False
        # Make sure the length is actually suitable
        if not len(an.IDENTICHIPNUMBER) in (9, 10, 15):
            self.logError("Microchip length is not 9, 10 or 15, cannot process")
            return False
        return True

