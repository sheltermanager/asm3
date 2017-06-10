#!/usr/bin/python

import configuration
import i18n
import sys
import users
import utils

from base import AbstractPublisher
from publish import get_microchip_data
from sitedefs import PETTRAC_UK_POST_URL

class PETtracUKPublisher(AbstractPublisher):
    """
    Handles updating animal microchips with AVID PETtrac UK
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("pettracuk", "PETtrac UK Publisher")

    def reregistrationPDF(self, fields, sig, realname, orgname, orgaddress, orgtown, orgcounty, orgpostcode):
        """
        Generates a reregistration PDF document containing the authorised user's
        electronic signature.
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
        h += "<p>Date: %s</p>\n" % i18n.python2display(self.dbo.locale, i18n.now(self.dbo.timezone))
        h += "<p>Authorisation: I understand that the information I have given on this form will be retained by PETtrac and " \
            "hereby agree that it may be disclosed to any person or persons who may be involved in securing the welfare of the " \
            "pet above. PETtrac reserves the right to amend any microchip record in the event that we are subsequently " \
            "provided with additional information.</p>\n"
        return utils.html_to_pdf(h)

    def run(self):
        
        self.log("PETtrac UK Publisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        orgpostcode = configuration.avid_org_postcode(self.dbo)
        orgname = configuration.avid_org_name(self.dbo)
        orgserial = configuration.avid_org_serial(self.dbo)
        orgpassword = configuration.avid_org_password(self.dbo)
        avidrereg = configuration.avid_reregistration(self.dbo)

        orgaddress = configuration.organisation_address(self.dbo)
        orgtown = configuration.organisation_town(self.dbo)
        orgcounty = configuration.organisation_county(self.dbo)

        registeroverseas = configuration.avid_register_overseas(self.dbo)
        overseasorigin = configuration.avid_overseas_origin_country(self.dbo)

        if orgpostcode == "" or orgname == "" or orgserial == "" or orgpassword == "":
            self.setLastError("orgpostcode, orgname, orgserial and orgpassword all need to be set for AVID publisher")
            return

        authuser = configuration.avid_auth_user(self.dbo)
        user = users.get_users(self.dbo, authuser)
        if avidrereg and len(user) == 0:
            self.setLastError("no authorised user is set, cannot re-register chips")
            return

        if avidrereg and utils.nulltostr(user[0]["SIGNATURE"]) == "":
            self.setLastError("authorised user '%s' does not have an electronic signature on file" % authuser)
            return

        chipprefix = "977%" # AVID Europe
        if registeroverseas: 
            chipprefix = "a.IdentichipNumber LIKE '%'" # If overseas registration is on, send all chips to AVID

        animals = get_microchip_data(self.dbo, [chipprefix,], "pettracuk", allowintake = False)
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

                # Make sure the length is actually suitable
                if not len(an["IDENTICHIPNUMBER"]) in (9, 10, 15):
                    self.logError("Microchip length is not 9, 10 or 15, cannot process")
                    continue

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
                    "implantdate": i18n.format_date("%Y%m%d", an["IDENTICHIPDATE"]),
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
                    "petdob": i18n.format_date("%Y%m%d", an["DATEOFBIRTH"]),
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

                self.log("HTTP POST request %s: %s" % (PETTRAC_UK_POST_URL, str(fields)))
                r = utils.post_form(PETTRAC_UK_POST_URL, fields)
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

                        pdfname = "%s-%s-%s.pdf" % (i18n.format_date("%Y%m%d", i18n.now(self.dbo.timezone)), orgserial, an["IDENTICHIPNUMBER"])
                        fields["filenameupload"] = pdfname
                        pdf = self.reregistrationPDF(fields, user[0]["SIGNATURE"], user[0]["REALNAME"], orgname, orgaddress, orgtown, orgcounty, orgpostcode)
                        self.log("generated re-registration PDF %s (%d bytes)" % (pdfname, len(pdf)))

                        reregurl = PETTRAC_UK_POST_URL.replace("onlineregistration", "onlinereregistration")
                        self.log("HTTP multipart POST request %s: %s" % (reregurl, str(fields)))
                        r = utils.post_multipart(reregurl, fields, { pdfname: (pdfname, pdf, "application/pdf" )} )
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


