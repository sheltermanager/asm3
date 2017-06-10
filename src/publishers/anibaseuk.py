#!/usr/bin/python

import configuration
import i18n
import sys
import utils

from base import AbstractPublisher, get_microchip_data
from sitedefs import ANIBASE_BASE_URL, ANIBASE_API_USER, ANIBASE_API_KEY

class AnibaseUKPublisher(AbstractPublisher):
    """
    Handles updating UK Identichip microchips with the Anibase web service
    (which uses VetXML)
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("anibaseuk", "Anibase UK Publisher")

    def get_vetxml_species(self, asmspeciesid):
        SPECIES_MAP = {
            1:  "Canine",
            2:  "Feline",
            3:  "Avian",
            4:  "Rodent",
            5:  "Rodent",
            7:  "Rabbit",
            9:  "Polecat",
            11: "Reptilian",
            12: "Tortoise",
            13: "Reptilian",
            14: "Avian",
            15: "Avian",
            16: "Goat",
            10: "Rodent",
            18: "Rodent",
            20: "Rodent",
            21: "Fish",
            22: "Rodent",
            23: "Camelid",
            24: "Equine",
            25: "Equine",
            26: "Donkey"
        }
        if asmspeciesid in SPECIES_MAP:
            return SPECIES_MAP[asmspeciesid]
        return "Miscellaneous"

    def run(self):
        def xe(s): 
            if s is None: return ""
            return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        self.log(self.publisherName + " starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        practiceid = configuration.anibase_practice_id(self.dbo)
        pinno = configuration.anibase_pin_no(self.dbo)

        if pinno == "":
            self.setLastError("Anibase vet code must be set")
            return

        animals = get_microchip_data(self.dbo, ['9851', '9861'], "anibaseuk")
        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            return

        anCount = 0
        processed_animals = []
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

                # Validate certain items aren't blank so we aren't registering bogus data
                if utils.nulltostr(an["CURRENTOWNERADDRESS"].strip()) == "":
                    self.logError("Address for the new owner is blank, cannot process")
                    continue 

                if utils.nulltostr(an["CURRENTOWNERPOSTCODE"].strip()) == "":
                    self.logError("Postal code for the new owner is blank, cannot process")
                    continue

                if an["IDENTICHIPDATE"] is None:
                    self.logError("Microchip date cannot be blank, cannot process")
                    continue

                # Make sure the length is actually suitable
                if not len(an["IDENTICHIPNUMBER"]) in (9, 10, 15):
                    self.logError("Microchip length is not 9, 10 or 15, cannot process")
                    continue

                # Construct the XML document
                x = '<?xml version="1.0" encoding="UTF-8"?>\n' \
                    '<MicrochipRegistration>' \
                    '<Identification>' \
                    ' <PracticeID>' + practiceid + '</PracticeID>' \
                    ' <PinNo>' + pinno + '</PinNo>' \
                    ' <Source></Source>' \
                    '</Identification>' \
                    '<OwnerDetails>' \
                    ' <Salutation>' + xe(an["CURRENTOWNERTITLE"]) + '</Salutation>' \
                    ' <Initials>' + xe(an["CURRENTOWNERINITIALS"]) + '</Initials>' \
                    ' <Forenames>' + xe(an["CURRENTOWNERFORENAMES"]) + '</Forenames>' \
                    ' <Surname>' + xe(an["CURRENTOWNERSURNAME"]) + '</Surname>' \
                    ' <Address>' \
                    '  <Line1>'+ xe(an["CURRENTOWNERADDRESS"]) + '</Line1>' \
                    '  <LineOther>'+ xe(an["CURRENTOWNERTOWN"]) + '</LineOther>' \
                    '  <PostalCode>' + xe(an["CURRENTOWNERPOSTCODE"]) + '</PostalCode>' \
                    '  <County_State>'+ xe(an["CURRENTOWNERCOUNTY"]) + '</County_State>' \
                    '  <Country>USA</Country>' \
                    ' </Address>' \
                    ' <DaytimePhone><Number>' + xe(an["CURRENTOWNERWORKTELEPHONE"]) + '</Number><Note/></DaytimePhone>' \
                    ' <EveningPhone><Number>' + xe(an["CURRENTOWNERHOMETELEPHONE"]) + '</Number><Note/></EveningPhone>' \
                    ' <MobilePhone><Number>' + xe(an["CURRENTOWNERMOBILETELEPHONE"]) + '</Number><Note/></MobilePhone>' \
                    ' <EmergencyPhone><Number/><Note/></EmergencyPhone>' \
                    ' <OtherPhone><Number/><Note/></OtherPhone>' \
                    ' <EmailAddress>' + xe(an["CURRENTOWNEREMAILADDRESS"]) + '</EmailAddress>' \
                    ' <Fax />' \
                    '</OwnerDetails>' \
                    '<PetDetails>' \
                    '  <Name>' + xe(an["ANIMALNAME"]) + '</Name>' \
                    '  <Species>' + self.get_vetxml_species(an["SPECIESID"]) + '</Species>' \
                    '  <Breed><FreeText>' + xe(an["BREEDNAME"]) + '</FreeText><Code/></Breed>' \
                    '  <DateOfBirth>' + i18n.format_date("%m/%d/%Y", an["DATEOFBIRTH"]) + '</DateOfBirth>' \
                    '  <Gender>' + an["SEXNAME"][0:1] + '</Gender>' \
                    '  <Colour>' + xe(an["BASECOLOURNAME"]) + '</Colour>' \
                    '  <Markings>' + xe(an["MARKINGS"]) + '</Markings>' \
                    '  <Neutered>' + (an["NEUTERED"] == 1 and "true" or "false") + '</Neutered>' \
                    '  <NotableConditions>' + xe(an["HEALTHPROBLEMS"]) + '</NotableConditions>' \
                    '</PetDetails>' \
                    '<MicrochipDetails>' \
                    '  <MicrochipNumber>' + xe(an["IDENTICHIPNUMBER"]) + '</MicrochipNumber>' \
                    '  <ImplantDate>' + i18n.format_date("%m/%d/%Y", an["IDENTICHIPDATE"]) + '</ImplantDate>' \
                    '  <ImplanterName>' + xe(an["CREATEDBY"]) + '</ImplanterName>' \
                    '</MicrochipDetails>' \
                    '<ThirdPartyDisclosure>true</ThirdPartyDisclosure>' \
                    '<ReceiveMail>true</ReceiveMail>' \
                    '<ReceiveEmail>true</ReceiveEmail>' \
                    '<Authorisation>true</Authorisation>' \
                    '</MicrochipRegistration>'

                # Build our auth headers
                authheaders = {
                    "APIUSER": ANIBASE_API_USER,
                    "APIKEY": ANIBASE_API_KEY
                }

                try:
                    # Post the VetXML document
                    self.log("Posting microchip registration document to %s \n%s\n" % (ANIBASE_BASE_URL, x))
                    r = utils.post_xml(ANIBASE_BASE_URL, x, authheaders)
                    self.log("Response %d, HTTP headers: %s, body: %s" % (r["status"], r["headers"], r["response"]))
                    if r["status"] != 200: raise Exception(r["response"])

                    # Look in the headers for successful results
                    wassuccess = False
                    SUCCESS = ( "54000", "54100", "54108" )
                    for code in SUCCESS:
                        if str(r["headers"]).find(code) != -1:
                            self.log("successful %s response header found, marking processed" % code)
                            processed_animals.append(an)
                            # Mark success in the log
                            self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                            wassuccess = True
                            break

                    # If we got a chipfound=false message, mark the chip as processed and a success
                    # so we don't try and register it in future
                    if str(r["response"]).find("<chipFound>false</chipFound>") != -1:
                        self.log("chipFound=false response found, marking chip processed to prevent future sending")
                        processed_animals.append(an)
                        wassuccess = True

                    # If we saw an account not found message, there's no point sending 
                    # anything else as they will all trigger the same error
                    if str(r["headers"]).find("54101") != -1:
                        self.logError("received Anibase 54101 'sender not recognised' response header - abandoning run")
                        break

                    if not wassuccess:
                        self.logError("no successful response header %s received" % str(SUCCESS))

                except Exception as err:
                    em = str(err)
                    self.logError("Failed registering microchip: %s" % em, sys.exc_info())
                    continue

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Only mark processed if we aren't using Anibase test URL
        if len(processed_animals) > 0 and ANIBASE_BASE_URL.find("test") == -1:
            self.log("successfully processed %d animals, marking sent" % len(processed_animals))
            self.markAnimalsPublished(processed_animals)

        if ANIBASE_BASE_URL.find("test") != -1:
            self.log("Anibase test mode, not marking animals published")

        self.saveLog()
        self.setPublisherComplete()


