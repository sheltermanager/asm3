
import asm3.configuration
import asm3.i18n
import asm3.users
import asm3.utils

from .base import AbstractPublisher, get_microchip_data
from asm3.sitedefs import PETTRAC_UK_POST_URL
from asm3.typehints import Database, Dict, PublishCriteria, ResultRow

import sys

class PETtracUKPublisher(AbstractPublisher):
    """
    Handles updating animal microchips with AVID PETtrac UK
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("pettracuk", "PETtrac UK Publisher")

    def reregistrationPDF(self, fields: Dict, sig: str, realname: str, 
                          orgname: str, orgaddress: str, orgtown: str, orgcounty: str, orgpostcode: str) -> bytes:
        """
        Generates a reregistration PDF document containing the authorised user's
        electronic signature (sig is data uri)
        """
        gender = fields["petgender"]
        if gender == "M": gender = "Male"
        elif gender == "F": gender = "Female"
        h = "<p align=\"right\"><b>%s</b><br />%s<br />%s, %s<br />%s</p>" % (orgname, orgaddress, orgtown, orgcounty, orgpostcode)
        h += "<h2>Change of Registered Owner/Keeper</h2>"
        h += "<table border=\"1\">"
        h += "<tr><td>Chip:</td><td><b>%s</b></td></tr>" % fields["microchip"]
        h += "<tr><td>Implanted:</td><td>%s</td></tr>" % fields["implantdate"]
        h += "<tr><td>Animal:</td><td>%s</td></tr>" % fields["petname"]
        h += "<tr><td>DOB:</td><td>%s</td></tr>" % fields["petdob"]
        h += "<tr><td>Type:</td><td>%s %s %s</td></tr>" % (gender, fields["petbreed"], fields["petspecies"])
        h += "<tr><td>Colour:</td><td>%s</td></tr>" % fields["petcolour"]
        h += "<tr><td>Neutered:</td><td>%s</td></tr>" % fields["petneutered"]
        h += "<tr><td>New Owner:</td><td>%s %s %s</td></tr>" % (fields["prefix"], fields["firstname"], fields["surname"])
        h += "<tr><td>Address:</td><td>%s<br/>%s<br/>%s %s</td></tr>" % (fields["address1"], fields["city"], fields["county"], fields["postcode"])
        h += "<tr><td>Telephone:</td><td>H: %s<br/>W: %s<br/>M: %s</td></tr>" % (fields["telhome"], fields["telwork"], fields["telmobile"])
        h += "<tr><td>Email:</td><td>%s</td></tr>" % fields["email"]
        h += "</table>"
        h += "<p>I/We confirm that every effort has been made to reunite the animal with its owner/keeper, or that the previous " \
            "owner has relinquished ownership/keepership.</p>\n"
        h += "<p>If the animal was a stray then the animal has been in our care for the minimum required time period before " \
            "rehoming took place.</p>\n"
        h += "<p>Authorised Signature: <br /><img src=\"%s\" /><br />%s</p>\n" % (sig, realname)
        h += "<p>Date: %s</p>\n" % asm3.i18n.python2display(self.dbo.locale, asm3.i18n.now(self.dbo.timezone))
        h += "<p>Authorisation: I understand that the information I have given on this form will be retained by PETtrac and " \
            "hereby agree that it may be disclosed to any person or persons who may be involved in securing the welfare of the " \
            "pet above. PETtrac reserves the right to amend any microchip record in the event that we are subsequently " \
            "provided with additional information.</p>\n"
        return asm3.utils.html_to_pdf(self.dbo, h)

    def run(self) -> None:
        
        self.log("PETtrac UK Publisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        orgpostcode = asm3.configuration.avid_org_postcode(self.dbo)
        orgname = asm3.configuration.avid_org_name(self.dbo)
        orgserial = asm3.configuration.avid_org_serial(self.dbo)
        orgpassword = asm3.configuration.avid_org_password(self.dbo)
        avidrereg = asm3.configuration.avid_reregistration(self.dbo)

        orgaddress = asm3.configuration.organisation_address(self.dbo)
        orgtown = asm3.configuration.organisation_town(self.dbo)
        orgcounty = asm3.configuration.organisation_county(self.dbo)

        registeroverseas = asm3.configuration.avid_register_overseas(self.dbo)
        overseasorigin = asm3.configuration.avid_overseas_origin_country(self.dbo)

        if orgpostcode == "" or orgname == "" or orgserial == "" or orgpassword == "":
            self.setLastError("orgpostcode, orgname, orgserial and orgpassword all need to be set for AVID publisher")
            return

        authuser = asm3.configuration.avid_auth_user(self.dbo)
        user = asm3.users.get_users(self.dbo, authuser)
        if avidrereg and len(user) == 0:
            self.setLastError("no authorised user is set, cannot re-register chips")
            return

        if avidrereg and asm3.utils.nulltostr(user[0]["SIGNATURE"]) == "":
            self.setLastError("authorised user '%s' does not have an electronic signature on file" % authuser)
            return

        chipprefix = "977%" # AVID Europe
        if registeroverseas: 
            chipprefix = "a.IdentichipNumber LIKE '%'" # If overseas registration is on, send all chips to AVID

        animals = get_microchip_data(self.dbo, [chipprefix,], "pettracuk", allowintake = False or registeroverseas)
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

                if not self.validate(an): continue
                fields = self.processAnimal(an, orgname, orgserial, orgpostcode, orgpassword, registeroverseas, overseasorigin)

                self.log("HTTP POST request %s: %s" % (PETTRAC_UK_POST_URL, str(fields)))
                r = asm3.utils.post_form(PETTRAC_UK_POST_URL, fields)
                self.log("HTTP response: %s" % r["response"])

                # Return value is an XML fragment, look for "Registration completed successfully"
                if r["response"].find("successfully") != -1:
                    self.log("successful response, marking processed")
                    processed_animals.append(an)
                    # Mark success in the log
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))

                # If AVID tell us the microchip is already registered, attempt to re-register
                elif r["response"].find("already registered") != -1:
                    if avidrereg:
                        self.log("microchip already registered response, re-registering")

                        pdfname = "%s-%s-%s.pdf" % (asm3.i18n.format_date(asm3.i18n.now(self.dbo.timezone), "%Y%m%d"), orgserial, an["IDENTICHIPNUMBER"])
                        fields["filenameupload"] = pdfname
                        pdf = self.reregistrationPDF(fields, user[0]["SIGNATURE"], user[0]["REALNAME"], orgname, orgaddress, orgtown, orgcounty, orgpostcode)
                        self.log("generated re-registration PDF %s (%d bytes)" % (pdfname, len(pdf)))

                        reregurl = PETTRAC_UK_POST_URL.replace("onlineregistration", "onlinereregistration")
                        self.log("HTTP multipart POST request %s: %s" % (reregurl, str(fields)))
                        r = asm3.utils.post_multipart(reregurl, fields, { pdfname: (pdfname, pdf, "application/pdf" )} )
                        self.log("HTTP response: %s" % r["response"])

                        if r["response"].find("successfully") != -1:
                            self.log("successful re-registration response, marking processed")
                            processed_animals.append(an)
                            # Mark success in the log
                            self.logSuccess("Processed: %s: %s (%d of %d) (rereg)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                        else:
                            self.logError("Problem with data encountered, not marking processed")
                    else:
                        self.logError("re-registration support is disabled, marking processed for compatibility")
                        processed_animals.append(an)
                # There's a problem with the data we sent, flag it
                else:
                    self.logError("Problem with data encountered, not marking processed")

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        if len(processed_animals) > 0:
            self.log("successfully processed %d animals, marking sent" % len(processed_animals))
            self.markAnimalsPublished(processed_animals)

        self.saveLog()
        self.setPublisherComplete()

    def processAnimal(self, an: ResultRow, orgname="", orgserial="", orgpostcode="", orgpassword="", registeroverseas=False, overseasorigin="") -> Dict:
        """ Generate a dictionary of data to post from an animal record """
        # Sort out breed
        breed = an["BREEDNAME"]
        if breed.find("Domestic Long") != -1: breed = "DLH"
        if breed.find("Domestic Short") != -1: breed = "DSH"
        if breed.find("Domestic Medium") != -1: breed = "DSLH"

        # Sort out species
        species = an["SPECIESNAME"]
        if species.find("Dog") != -1: species = "Canine"
        elif species.find("Cat") != -1: species = "Feline"
        elif species.find("Bird") != -1: species = "Avian"
        elif species.find("Horse") != -1: species = "Equine"
        elif species.find("Reptile") != -1: species = "Reptilian"
        else: species = "Other"

        # Build the animal POST data
        fields = {
            "orgpostcode": orgpostcode,
            "orgname": orgname, 
            "orgserial": orgserial,
            "orgpassword": orgpassword,
            "version": "1.1",
            "microchip": an["IDENTICHIPNUMBER"],
            "implantdate": asm3.i18n.format_date(an["IDENTICHIPDATE"], "%Y%m%d"),
            "prefix": an["CURRENTOWNERTITLE"],
            "surname": an["CURRENTOWNERSURNAME"],
            "firstname": an["CURRENTOWNERFORENAMES"],
            "address1": an["CURRENTOWNERADDRESS"],
            "city": an["CURRENTOWNERTOWN"],
            "county": an["CURRENTOWNERCOUNTY"],
            "postcode": an["CURRENTOWNERPOSTCODE"],
            "telhome": an["CURRENTOWNERHOMETELEPHONE"],
            "telwork": an["CURRENTOWNERWORKTELEPHONE"],
            "telmobile": an["CURRENTOWNERMOBILETELEPHONE"],
            "telalternative": "",
            "email": an["CURRENTOWNEREMAILADDRESS"],
            "petname": an["ANIMALNAME"],
            "petgender": an["SEXNAME"][0:1],
            "petdob": asm3.i18n.format_date(an["DATEOFBIRTH"], "%Y%m%d"),
            "petspecies": species,
            "petbreed": breed,
            "petneutered": an["NEUTERED"] == 1 and "true" or "false",
            "petcolour": an["BASECOLOURNAME"],
            "selfreg": "true", # register the shelter as alternative contact
            "test": "false" # if true, tells avid not to make any data changes
        }

        # If we're registering overseas chips and this chip isn't an AVID
        # one, set the origincountry parameter
        if registeroverseas and not an["IDENTICHIPNUMBER"].startswith("977"):
            fields["origincountry"] = overseasorigin

        return fields

    def validate(self, an: ResultRow) -> bool:
        """ Validate an animal record is ok to send """
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


