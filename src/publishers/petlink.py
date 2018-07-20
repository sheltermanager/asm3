#!/usr/bin/python

import base64
import configuration
import i18n
import sys
import utils

from base import AbstractPublisher, get_microchip_data
from sitedefs import PETLINK_BASE_URL

UPLOAD_URL = PETLINK_BASE_URL + "api/restapi/signup/mass-import?filename=import.csv&mediumId=sheltermanager"

class PetLinkPublisher(AbstractPublisher):
    """
    Handles publishing of updated microchip info to PetLink.net
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        AbstractPublisher.__init__(self, dbo, publishCriteria)
        self.initLog("petlink", "PetLink Publisher")

    def plYesNo(self, condition):
        """
        Returns yes or no for a condition.
        """
        if condition:
            return "y"
        else:
            return "n"

    def plBreed(self, breedname, speciesname, iscross):
        """
        Returns a PetLink breed of either the breed name,
        "Mixed Breed" if iscross == 1 or "Other" if the species
        is not Cat or Dog.
        """
        if speciesname.lower().find("cat") != -1 and speciesname.lower().find("dog") != -1:
            return "Other"
        if iscross == 1:
            return "Mixed Breed"
        return breedname

    def run(self):
        
        self.log("PetLinkPublisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        plemail = configuration.petlink_email(self.dbo)
        plowneremail = configuration.petlink_owner_email(self.dbo)
        password = configuration.petlink_password(self.dbo)

        if plemail == "" or password == "":
            self.setLastError("No PetLink login has been set.")
            return

        animals = get_microchip_data(self.dbo, ['98102',], "petlink", organisation_email = plowneremail)
        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            return

        anCount = 0
        csv = []
        processed_animals = []
        failed_animals = []

        csv.append("Software,TransactionType,MicrochipID,FirstName,LastName,Address,City,State,ZipCode,Country," \
            "Phone1,Phone2,Phone3,Email,Password,Date_of_Implant,PetName,Species,Breed,Gender," \
            "Spayed_Neutered,ColorMarkings")

        for an in animals:
            try:
                line = []
                anCount += 1
                self.log("Processing: %s: %s (%d of %d) - %s %s" % \
                    ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals), an["IDENTICHIPNUMBER"], an["CURRENTOWNERNAME"] ))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    return

                # If the microchip number isn't 15 digits, skip it
                if len(an["IDENTICHIPNUMBER"].strip()) != 15:
                    self.logError("Chip number failed validation (%s not 15 digits), skipping." % an["IDENTICHIPNUMBER"])
                    continue

                # Validate certain items aren't blank so we aren't trying to register
                # things that PetLink will bounce back anyway
                if utils.nulltostr(an["CURRENTOWNERTOWN"]).strip() == "":
                    self.logError("City for the new owner is blank, cannot process")
                    continue 

                if utils.nulltostr(an["CURRENTOWNERCOUNTY"]).strip() == "":
                    self.logError("State for the new owner is blank, cannot process")
                    continue 

                if utils.nulltostr(an["CURRENTOWNERPOSTCODE"]).strip() == "":
                    self.logError("Zipcode for the new owner is blank, cannot process")
                    continue

                # If there's no email or phone, PetLink won't accept it
                email = utils.nulltostr(an["CURRENTOWNEREMAILADDRESS"]).strip()
                homephone = utils.nulltostr(an["CURRENTOWNERHOMETELEPHONE"]).strip()
                workphone = utils.nulltostr(an["CURRENTOWNERWORKTELEPHONE"]).strip()
                mobilephone = utils.nulltostr(an["CURRENTOWNERMOBILETELEPHONE"]).strip()
                if email == "" and homephone == "" and workphone == "" and mobilephone == "":
                    self.logError("No email address or phone number for owner, skipping.")
                    continue
               
                # If there's no phone, we can't set the chip password so skip it
                if homephone == "" and workphone == "" and mobilephone == "":
                    self.logError("No phone number for owner, skipping.")
                    continue

                # Get the phone number and strip it of non-numeric data
                phone = homephone or mobilephone or workphone
                phone = "".join(c for c in phone if c.isdigit())

                # If we don't have an email address, use phone@petlink.tmp
                if email == "":
                    email = "%s@petlink.tmp" % phone

                # Software
                line.append("\"ASM\"")
                # TransactionType
                line.append("\"%s\"" % ( self.getLastPublishedDate(an["ID"]) is None and 'N' or 'T' ))
                # MicrochipID
                line.append("\"%s\"" % ( an["IDENTICHIPNUMBER"] ))
                # FirstName
                line.append("\"%s\"" % ( an["CURRENTOWNERFORENAMES"] ))
                # LastName
                line.append("\"%s\"" % ( an["CURRENTOWNERSURNAME"] ))
                # Address
                line.append("\"%s\"" % ( an["CURRENTOWNERADDRESS"] ))
                # City
                line.append("\"%s\"" % ( an["CURRENTOWNERTOWN"] ))
                # State
                line.append("\"%s\"" % ( an["CURRENTOWNERCOUNTY"] ))
                # ZipCode
                line.append("\"%s\"" % ( an["CURRENTOWNERPOSTCODE"] ))
                # Country
                line.append("\"USA\"")
                # Phone1
                line.append("\"%s\"" % ( an["CURRENTOWNERHOMETELEPHONE"] ))
                # Phone2
                line.append("\"%s\"" % ( an["CURRENTOWNERWORKTELEPHONE"] ))
                # Phone3
                line.append("\"%s\"" % ( an["CURRENTOWNERMOBILETELEPHONE"] ))
                # Email (mandatory)
                line.append("\"%s\"" % ( email ))
                # Chip Password (stripped phone number)
                line.append("\"%s\"" % phone)
                # Date_of_Implant (yy-mm-dd)
                line.append("\"%s\"" % i18n.format_date("%y-%m-%d", an["IDENTICHIPDATE"]))
                # PetName
                line.append("\"%s\"" % an["ANIMALNAME"])
                # Species
                line.append("\"%s\"" % an["SPECIESNAME"])
                # Breed (or "Mixed Breed" for crossbreeds, Other for animals not cats and dogs)
                line.append("\"%s\"" % self.plBreed(an["BREEDNAME1"], an["SPECIESNAME"], an["CROSSBREED"]))
                # Gender
                line.append("\"%s\"" % an["SEXNAME"])
                # Spayed_Neutered (y or n)
                line.append("\"%s\"" % self.plYesNo(an["NEUTERED"]))
                # ColorMarkings (our BaseColour field)
                line.append("\"%s\"" % an["BASECOLOURNAME"])
                # Add to our data file.  
                csv.append(",".join(line))
                # Remember we included this one
                processed_animals.append(an)
                # Mark success in the log
                self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # If we excluded our only animals and have nothing to send, stop now
        if len(csv) == 1:
            self.log("No animals left to send to PetLink.")
            self.saveLog()
            self.setPublisherComplete()
            return

        # POST the csv data
        headers = {
            "Authorization": "Basic %s" % base64.b64encode("%s:%s" % (plemail, password)),
            "Content-Type":  "text/csv"
        }
        self.log("Uploading data file (%d csv lines) to %s..." % (len(csv), UPLOAD_URL))
        try:
            r = utils.post_data(UPLOAD_URL, "\n".join(csv), headers=headers)
            response = r["response"].decode("utf-8").encode("ascii", "xmlcharrefreplace")

            self.log("req hdr: %s, \nreq data: %s" % (r["requestheaders"], r["requestbody"]))
            self.log("resp hdr: %s, \nresp body: %s" % (r["headers"], response))

            jresp = utils.json_parse(response)
            
            # Look for remote exceptions
            if "exception" in jresp and jresp["exception"] != "":
                self.successes = 0
                self.logError("PetLink remote exception received, abandoning: %s" % jresp["exception"])
                self.saveLog()
                self.setPublisherComplete()
                return

            # Parse any errors in the JSON response
            for e in jresp["errors"]:
                chip = ""
                message = ""
                try:
                    # Prefer microchip= in location column, then fall back to id=/microchip= in column
                    if e["location"].find("microchip=") != -1:
                        chip = e["location"]
                        chip = chip[chip.find("microchip=")+10:]
                    elif e["column"].find("id=") != -1:
                        chip = e["column"].replace("id=", "")
                    elif e["column"].find("microchip=") != -1:
                        chip = e["column"].replace("microchip=", "")
                    message = e["message"]
                except Exception as erj:
                    try:
                        self.logError("Failed unpacking error message (message=%s) from '%s'" % (erj, e))
                    except:
                        self.logError("Failed decoding error message from PetLink")
                    continue

                # Iterate over a copy of the processed list so we can remove animals from it
                # that have error emssages.
                for an in processed_animals[:]:

                    if an["IDENTICHIPNUMBER"] == chip:
                        processed_animals.remove(an)
                        try:
                            self.logError("%s: %s (%s) - Received error message from PetLink: %s" % \
                                (an["SHELTERCODE"], an["ANIMALNAME"], an["IDENTICHIPNUMBER"], message))
                        except Exception as erm:
                            self.logError("%s: %s (%s) - Error decoding message from PetLink" % \
                                (an["SHELTERCODE"], an["ANIMALNAME"], an["IDENTICHIPNUMBER"]))
                            continue

                        # If the message was that the chip is already registered,
                        # mark this animal as published but on the intake date -
                        # this will force this publisher to put it through as a transfer
                        # next time since we'll find a previous published record.
                        if message.find("has already been registered") != -1:
                            self.markAnimalPublished(an["ID"], an["DATEBROUGHTIN"])
                            self.log("%s: %s (%s) - Already registered, marking as PetLink TRANSFER for next publish" % \
                                (an["SHELTERCODE"], an["ANIMALNAME"], an["IDENTICHIPNUMBER"]))
                            continue

                        # If the message is one of PetLink's permanent failure conditons, 
                        # mark the chip failed so that we stop trying.
                        # Any other error message we treat as transient and do nothing 
                        # (which means we'll attempt to register the chip the next time this publisher is run).
                        PERMANENT_FAILURES = [ 
                            "has an existing PetLink account and their contact information is already on file",
                            "Not a prepaid microchip",
                            "This is a Found Animals Registry chip",
                            "cannot be transferred - the account is locked."
                        ]
                        for m in PERMANENT_FAILURES:
                            if message.find(m) != -1:
                                an["FAILMESSAGE"] = message
                                failed_animals.append(an)

            if len(processed_animals) > 0:
                self.markAnimalsPublished(processed_animals)

            if len(failed_animals) > 0:
                self.markAnimalsPublishFailed(failed_animals)

        except Exception as err:
            self.logError("Failed uploading data file: %s" % err)

        self.saveLog()
        self.setPublisherComplete()


