
import asm3.al
import asm3.configuration
import asm3.i18n
import asm3.utils

from .base import AbstractPublisher, get_microchip_data
from asm3.sitedefs import HOMEAGAIN_BASE_URL

import sys

class HomeAgainPublisher(AbstractPublisher):
    """
    Handles updating HomeAgain animal microchips
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("homeagain", "HomeAgain Publisher")
        self.microchipPatterns = [ '985' ]

    def getHeader(self, headers, header):
        """ Returns a header from the headers list of a get_url call """
        for h in headers:
            if h.startswith(header):
                return h.strip()
        return ""

    def get_homeagain_species(self, asmspeciesid):
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
       
        self.log(self.publisherName + " starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        userid = asm3.configuration.homeagain_user_id(self.dbo)
        userpassword = asm3.configuration.homeagain_user_password(self.dbo)

        if userid == "" or userpassword == "":
            self.setLastError("HomeAgain userid and userpassword must be set")
            return

        animals = get_microchip_data(self.dbo, self.microchipPatterns, self.publisherKey)
        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            return

        anCount = 0
        processed_animals = []
        failed_animals = []
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

                # Construct the XML document
                if not self.validate(an): continue
                x = self.processAnimal(an, userid)
                                
                # Build our auth headers
                authheaders = {
                    "UserId": userid,
                    "UserPassword": userpassword
                }

                url = HOMEAGAIN_BASE_URL + "/Chip/conversation"
                try:
                    # Post our VetXML document
                    self.log("Posting microchip registration document to %s: %s" % (url, x))
                    r = asm3.utils.post_xml(url, x, authheaders)
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

                    # If we saw an account not found message, there's no point sending 
                    # anything else as they will all trigger the same error
                    if str(r["headers"]).find("54101") != -1:
                        self.logError("received HomeAgain 54101 'account not found' response header - abandoning run and disabling publisher")
                        asm3.configuration.publishers_enabled_disable(self.dbo, "veha")
                        break
                    
                    if not wassuccess:
                        self.logError("no successful response header %s received" % str(SUCCESS))
                        an["FAILMESSAGE"] = "%s: %s" % (self.getHeader(r["headers"], "ResultCode"), self.getHeader(r["headers"], "ResultDetails"))
                        failed_animals.append(an)

                except Exception as err:
                    em = str(err)
                    self.logError("Failed registering microchip: %s" % em, sys.exc_info())
                    continue

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark success/failures
        if len(processed_animals) > 0:
            self.log("successfully processed %d animals, marking sent" % len(processed_animals))
            self.markAnimalsPublished(processed_animals)
        if len(failed_animals) > 0:
            self.log("failed processing %d animals, marking failed" % len(failed_animals))
            self.markAnimalsPublishFailed(failed_animals)

        self.saveLog()
        self.setPublisherComplete()

    def processAnimal(self, an, userid=""):
        """ Returns a VetXML document from an animal """
        def xe(s): 
            if s is None: return ""
            return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        reccountry = an.CURRENTOWNERCOUNTRY
        if reccountry is None or reccountry == "": reccountry = "USA"
        return '<?xml version="1.0" encoding="UTF-8"?>\n' \
            '<MicrochipRegistration ' \
            'version="1.32" ' \
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
            'xsi:schemaLocation="https://www.vetenvoytest.com/partner/files/Chip%201.32.xsd">' \
            '<Identification>' \
            ' <PracticeID>' + userid + '</PracticeID>' \
            ' <PinNo></PinNo>' \
            ' <Source></Source>' \
            '</Identification>' \
            '<OwnerDetails>' \
            ' <Salutation>' + xe(an["CURRENTOWNERTITLE"]) + '</Salutation>' \
            ' <Initials>' + xe(an["CURRENTOWNERINITIALS"]) + '</Initials>' \
            ' <Forenames>' + xe(an["CURRENTOWNERFORENAMES"]) + '</Forenames>' \
            ' <Surname>' + xe(an["CURRENTOWNERSURNAME"]) + '</Surname>' \
            ' <Address>' \
            '  <Line1>'+ xe(an["CURRENTOWNERADDRESS"]) + '</Line1>' \
            '  <TownCity>'+ xe(an["CURRENTOWNERTOWN"]) + '</TownCity>' \
            '  <County_State>'+ xe(an["CURRENTOWNERCOUNTY"]) + '</County_State>' \
            '  <PostalCode>' + xe(an["CURRENTOWNERPOSTCODE"]) + '</PostalCode>' \
            '  <Country>' + reccountry + '</Country>' \
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
            '  <Species>' + self.get_homeagain_species(an["SPECIESID"]) + '</Species>' \
            '  <Breed><FreeText>' + xe(an["BREEDNAME"]) + '</FreeText><Code/></Breed>' \
            '  <DateOfBirth>' + asm3.i18n.format_date(an["DATEOFBIRTH"], "%m/%d/%Y") + '</DateOfBirth>' \
            '  <Gender>' + an["SEXNAME"][0:1] + '</Gender>' \
            '  <Colour>' + xe(an["BASECOLOURNAME"]) + '</Colour>' \
            '  <Markings>' + xe(an["MARKINGS"]) + '</Markings>' \
            '  <Neutered>' + (an["NEUTERED"] == 1 and "true" or "false") + '</Neutered>' \
            '  <NotableConditions>' + xe(an["HEALTHPROBLEMS"]) + '</NotableConditions>' \
            '</PetDetails>' \
            '<MicrochipDetails>' \
            '  <MicrochipNumber>' + xe(an["IDENTICHIPNUMBER"]) + '</MicrochipNumber>' \
            '  <ImplantDate>' + asm3.i18n.format_date(an["IDENTICHIPDATE"], "%m/%d/%Y") + '</ImplantDate>' \
            '  <ImplanterName>' + xe(an["CREATEDBY"]) + '</ImplanterName>' \
            '</MicrochipDetails>' \
            '<ThirdPartyDisclosure>true</ThirdPartyDisclosure>' \
            '<ReceiveMail>true</ReceiveMail>' \
            '<ReceiveEmail>true</ReceiveEmail>' \
            '<Authorisation>true</Authorisation>' \
            '</MicrochipRegistration>'

    def validate(self, an):
        """ Validates an animal record is ok to send """
        # Validate certain items aren't blank so we aren't registering bogus data
        if asm3.utils.nulltostr(an["CURRENTOWNERADDRESS"]).strip() == "":
            self.logError("Address for the new owner is blank, cannot process")
            return False 

        if asm3.utils.nulltostr(an["CURRENTOWNERPOSTCODE"]).strip() == "":
            self.logError("Postal code for the new owner is blank, cannot process")
            return False

        if an["IDENTICHIPDATE"] is None:
            self.logError("Microchip date cannot be blank, cannot process")
            return False

        # Make sure the length is actually suitable
        if not len(an["IDENTICHIPNUMBER"]) in (9, 10, 15):
            self.logError("Microchip length is not 9, 10 or 15, cannot process")
            return False

        return True


