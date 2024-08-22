
import asm3.al
import asm3.configuration
import asm3.i18n
import asm3.utils

# NO LONGER USED AS WE HAVE DIRECT INTEGRATION WITH AKC REUNITE AND HOMEAGAIN
# THIS CODE LEFT HERE IN CASE WE USE THEM FOR OTHER SERVICES IN FUTURE.
# ============================================================================

from .base import AbstractPublisher, get_microchip_data
from asm3.sitedefs import VETENVOY_US_VENDOR_USERID, VETENVOY_US_VENDOR_PASSWORD, VETENVOY_US_HOMEAGAIN_RECIPIENTID, VETENVOY_US_AKC_REUNITE_RECIPIENTID, VETENVOY_US_BASE_URL, VETENVOY_US_SYSTEM_ID
from asm3.typehints import Database, List, PostedData, PublishCriteria, ResultRow, Tuple

import re
import sys

class VetEnvoyUSMicrochipPublisher(AbstractPublisher):
    """
    Handles updating animal microchips via recipients of
    the VetEnvoy system in the US
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria, 
                 publisherName: str, publisherKey: str, recipientId: str, microchipPatterns: List[str]) -> None:
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog(publisherKey, publisherName)
        self.recipientId = recipientId
        self.microchipPatterns = microchipPatterns

    def getHeader(self, headers: List[str], header: str) -> str:
        """ Returns a header from the headers list of a get_url call """
        for h in headers:
            if h.startswith(header):
                return h.strip()
        return ""

    def get_vetenvoy_species(self, asmspeciesid: int) -> str:
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

    def run(self) -> None:
       
        self.log(self.publisherName + " starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        userid = asm3.configuration.vetenvoy_user_id(self.dbo)
        userpassword = asm3.configuration.vetenvoy_user_password(self.dbo)

        if userid == "" or userpassword == "":
            self.setLastError("VetEnvoy userid and userpassword must be set")
            return

        animals = get_microchip_data(self.dbo, self.microchipPatterns, self.publisherKey)
        if len(animals) == 0:
            self.setLastError("No microchips found to register.")
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
                    "UserPassword": userpassword,
                    "VendorPassword": VETENVOY_US_VENDOR_PASSWORD,
                    "RecipientId": self.recipientId
                }

                # Start a new conversation with VetEnvoy's microchip handler
                url = VETENVOY_US_BASE_URL + "Chip/NewConversationId"
                self.log("Contacting vetenvoy to start a new conversation: %s" % url)
                try:
                    r = asm3.utils.get_url(url, authheaders)
                    self.log("Got response: %s" % r["response"])
                    conversationid = re.findall('c id="(.+?)"', r["response"])
                    if len(conversationid) == 0:
                        self.log("Could not parse conversation id, abandoning run")
                        break
                    conversationid = conversationid[0]
                    self.log("Got conversationid: %s" % conversationid)

                    # Now post the XML document
                    self.log("Posting microchip registration document: %s" % x)
                    r = asm3.utils.post_xml(VETENVOY_US_BASE_URL + "Chip/" + conversationid, x, authheaders)
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

                    # If we saw an account not found message, there's no point sending 
                    # anything else as they will all trigger the same error
                    if str(r["headers"]).find("54101") != -1 and str(r["headers"]).find("Account Not Found") != -1:
                        self.logError("received HomeAgain 54101 'account not found' response header - abandoning run and disabling publisher")
                        asm3.configuration.publishers_enabled_disable(self.dbo, "veha")
                        break
                    if str(r["headers"]).find("54101") != -1 and str(r["headers"]).find("sender not recognized") != -1:
                        self.logError("received AKC Reunite 54101 'sender not recognized' response header - abandoning run and disabling publisher")
                        asm3.configuration.publishers_enabled_disable(self.dbo, "vear")
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

        # Only mark processed if we aren't using VetEnvoy's test URL
        if len(processed_animals) > 0 and VETENVOY_US_BASE_URL.find("test") == -1:
            self.log("successfully processed %d animals, marking sent" % len(processed_animals))
            self.markAnimalsPublished(processed_animals)
        if len(failed_animals) > 0 and VETENVOY_US_BASE_URL.find("test") == -1:
            self.log("failed processing %d animals, marking failed" % len(failed_animals))
            self.markAnimalsPublishFailed(failed_animals)

        if VETENVOY_US_BASE_URL.find("test") != -1:
            self.log("VetEnvoy test mode, not marking animals published")

        self.saveLog()
        self.setPublisherComplete()

    def processAnimal(self, an: ResultRow, userid: str = "") -> str:
        """ Returns an VetXML document from an animal """
        def xe(s): 
            if s is None: return ""
            return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        reccountry = an["CURRENTOWNERCOUNTRY"]
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
            '  <LineOther>'+ xe(an["CURRENTOWNERTOWN"]) + '</LineOther>' \
            '  <PostalCode>' + xe(an["CURRENTOWNERPOSTCODE"]) + '</PostalCode>' \
            '  <County_State>'+ xe(an["CURRENTOWNERCOUNTY"]) + '</County_State>' \
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
            '  <Species>' + self.get_vetenvoy_species(an["SPECIESID"]) + '</Species>' \
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

    def validate(self, an: ResultRow) -> bool:
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

    @staticmethod
    def signup(dbo, post: PostedData) -> Tuple[str, str]:
        """
        Handle automatically signing up for VetEnvoy's services.
        Return value on success is a tuple of userid, userpassword
        Errors are thrown to the caller
        """
        def xe(s: str) -> str: 
            if s is None: return ""
            return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        x = '<?xml version="1.0" encoding="UTF-8"?>\n' \
            '<Signup xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
            'xmlns:xsd="http://www.w3.org/2001/XMLSchema" ' \
            'xmlns="http://www.vetenvoy.com/schemas/signup" version="1.01">' \
            '<GeneralContact>' \
            '<Title>' + xe(post["title"]) + '</Title>' \
            '<FirstName>' + xe(post["firstname"]) + '</FirstName>' \
            '<LastName>' + xe(post["lastname"]) + '</LastName>' \
            '<Phone>' + xe(post["phone"]) + '</Phone>' \
            '<Email>' + xe(post["email"]) + '</Email>' \
            '<PositionInPractice>' + xe(post["position"]) + '</PositionInPractice>' \
            '</GeneralContact>' \
            '<PracticeDetails>' \
            '<PracticeName>' + xe(post["practicename"]) + '</PracticeName>' \
            '<Address>' + xe(post["address"]) + '</Address>' \
            '<PostalCode>' + xe(post["zipcode"]) + '</PostalCode>' \
            '<SystemId>' + VETENVOY_US_SYSTEM_ID + '</SystemId>' \
            '</PracticeDetails>' \
            '</Signup>'
        # Build our auth headers
        authheaders = {
            "UserId": VETENVOY_US_VENDOR_USERID,
            "UserPassword": VETENVOY_US_VENDOR_PASSWORD,
            "VendorPassword": VETENVOY_US_VENDOR_PASSWORD
        }
        # Start a new conversation with VetEnvoy's signup handler
        url = VETENVOY_US_BASE_URL + "AutoSignup/NewConversationId"
        asm3.al.debug("Contacting VetEnvoy to start a new signup conversation: %s" % url, "VetEnvoyMicrochipPublisher.signup", dbo)
        try:

            r = asm3.utils.get_url(url, authheaders)
            asm3.al.debug("Got response: %s" % r["response"], "VetEnvoyMicrochipPublisher.signup", dbo)
            conversationid = re.findall('c id="(.+?)"', r["response"])
            if len(conversationid) == 0:
                raise Exception("Could not parse conversation id, abandoning")
            conversationid = conversationid[0]
            asm3.al.debug("Got conversationid: %s" % conversationid, "VetEnvoyMicrochipPublisher.signup", dbo)

            # Now post the XML signup document
            asm3.al.debug("Posting signup document: %s" % x, "VetEnvoyMicrochipPublisher.signup", dbo)
            r = asm3.utils.post_xml(VETENVOY_US_BASE_URL + "AutoSignup/" + conversationid, asm3.utils.str2bytes(x), authheaders)
            asm3.al.debug("Response %d, HTTP headers: %s, body: %s" % (r["status"], r["headers"], r["response"]), "VetEnvoyMicrochipPublisher.signup", dbo)
            if r["status"] != 200: raise Exception(r["response"])

            # Extract the id and pwd attributes
            userid = re.findall('u id="(.+?)"', r["response"])
            userpwd = re.findall('pwd="(.+?)"', r["response"])
            if len(userid) == 0 or len(userpwd) == 0:
                raise Exception("Could not parse id and pwd from body, abandoning")
            userid = userid[0]
            userpwd = userpwd[0]
            return (userid, userpwd)

        except Exception as err:
            em = str(err)
            asm3.al.error("Failed during autosignup: %s" % em, "VetEnvoyMicrochipPublisher.signup", dbo, sys.exc_info())
            raise asm3.utils.ASMValidationError("Failed during autosignup")

class AllVetEnvoyPublisher(AbstractPublisher):
    """ Publisher class that runs all VetEnvoy publishers in one go. This is needed because
        all of VetEnvoy is enabled at once rather than individuals publishers """
    homeagain = None
    akcreunite = None

    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        self.homeagain = VEHomeAgainPublisher(dbo, publishCriteria)
        self.akcreunite = VEAKCReunitePublisher(dbo, publishCriteria)

    def run(self) -> None:
        self.homeagain.run()
        self.akcreunite.run()

class VEHomeAgainPublisher(VetEnvoyUSMicrochipPublisher):
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        if not asm3.configuration.vetenvoy_homeagain_enabled(dbo): return
        VetEnvoyUSMicrochipPublisher.__init__(self, dbo, publishCriteria, "HomeAgain Publisher", "homeagain", VETENVOY_US_HOMEAGAIN_RECIPIENTID, 
            ['985',])

class VEAKCReunitePublisher(VetEnvoyUSMicrochipPublisher):
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        if not asm3.configuration.vetenvoy_akcreunite_enabled(dbo): return
        VetEnvoyUSMicrochipPublisher.__init__(self, dbo, publishCriteria, "AKC Reunite Publisher", "akcreunite", VETENVOY_US_AKC_REUNITE_RECIPIENTID, 
            ['0006', '0007', '956', '9910010'])

