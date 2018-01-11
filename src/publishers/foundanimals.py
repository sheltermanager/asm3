#!/usr/bin/python

import configuration
import i18n
import os, sys
import utils

from base import FTPPublisher, get_microchip_data
from sitedefs import FOUNDANIMALS_FTP_HOST, FOUNDANIMALS_FTP_USER, FOUNDANIMALS_FTP_PASSWORD

class FoundAnimalsPublisher(FTPPublisher):
    """
    Handles publishing to foundanimals.org
    """
    def __init__(self, dbo, publishCriteria):
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        FTPPublisher.__init__(self, dbo, publishCriteria, 
            FOUNDANIMALS_FTP_HOST, FOUNDANIMALS_FTP_USER, FOUNDANIMALS_FTP_PASSWORD)
        self.initLog("foundanimals", "FoundAnimals Publisher")

    def run(self):
        
        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        org = configuration.organisation(self.dbo)
        folder = configuration.foundanimals_folder(self.dbo)
        if folder == "":
            self.setLastError("No FoundAnimals folder has been set.")
            self.cleanup()
            return

        animals = get_microchip_data(self.dbo, ["9", "0"], "foundanimals")
        if len(animals) == 0:
            self.setLastError("No animals found to publish.")
            self.cleanup(save_log=False)
            return

        if not self.openFTPSocket(): 
            self.setLastError("Failed to open FTP socket.")
            if self.logSearch("530 Login") != -1:
                self.log("Found 530 Login incorrect: disabling FoundAnimals publisher.")
                configuration.publishers_enabled_disable(self.dbo, "fa")
            self.cleanup()
            return

        # foundanimals.org want data files called mmddyyyy_HHMMSS.csv in the shelter's own folder
        dateportion = i18n.format_date("%m%d%Y_%H%M%S", i18n.now(self.dbo.timezone))
        outputfile = "%s.csv" % dateportion
        self.mkdir(folder)
        self.chdir(folder)

        csv = []

        anCount = 0
        success = []
        for an in animals:
            try:
                line = []
                anCount += 1
                self.log("Processing: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                self.updatePublisherProgress(self.getProgress(anCount, len(animals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.log("User cancelled publish. Stopping.")
                    self.resetPublisherProgress()
                    self.cleanup()
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

                # First Name
                line.append("\"%s\"" % an["CURRENTOWNERFORENAMES"])
                # Last Name
                line.append("\"%s\"" % an["CURRENTOWNERSURNAME"])
                # Email Address
                line.append("\"%s\"" % an["CURRENTOWNEREMAILADDRESS"])
                # Address 1
                line.append("\"%s\"" % an["CURRENTOWNERADDRESS"])
                # Address 2
                line.append("\"\"")
                # City
                line.append("\"%s\"" % an["CURRENTOWNERTOWN"])
                # State
                line.append("\"%s\"" % an["CURRENTOWNERCOUNTY"])
                # Zip Code
                line.append("\"%s\"" % an["CURRENTOWNERPOSTCODE"])
                # Home Phone
                line.append("\"%s\"" % an["CURRENTOWNERHOMETELEPHONE"])
                # Work Phone
                line.append("\"%s\"" % an["CURRENTOWNERWORKTELEPHONE"])
                # Cell Phone
                line.append("\"%s\"" % an["CURRENTOWNERMOBILETELEPHONE"])
                # Pet Name
                line.append("\"%s\"" % an["ANIMALNAME"])
                # Microchip Number
                line.append("\"%s\"" % an["IDENTICHIPNUMBER"])
                # Service Date
                line.append("\"%s\"" % i18n.format_date("%m/%d/%Y", an["ACTIVEMOVEMENTDATE"] or an["MOSTRECENTENTRYDATE"]))
                # Date of Birth
                line.append("\"%s\"" % i18n.format_date("%m/%d/%Y", an["DATEOFBIRTH"]))
                # Species
                line.append("\"%s\"" % an["PETFINDERSPECIES"])
                # Sex
                line.append("\"%s\"" % an["SEXNAME"])
                # Spayed/Neutered
                line.append("\"%s\"" % utils.iif(an["NEUTERED"] == 1, "Yes", "No"))
                # Primary Breed
                line.append("\"%s\"" % an["PETFINDERBREED"])
                # Secondary Breed
                line.append("\"%s\"" % an["PETFINDERBREED2"])
                # Color
                line.append("\"%s\"" % an["BASECOLOURNAME"])
                # Implanting Organization
                line.append("\"%s\"" % org)
                # Rescue Group Email
                line.append("\"%s\"" % configuration.foundanimals_email(self.dbo))
                # Add to our CSV file
                csv.append(",".join(line))
                # Mark success in the log
                self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))
                success.append(an)
            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Bail if we didn't have anything to do
        if len(csv) == 0:
            self.log("No data left to send to foundanimals")
            self.cleanup()
            return

        # Mark published
        self.markAnimalsPublished(success)

        header = "First Name,Last Name,Email Address,Address 1,Address 2,City,State,Zip Code," \
            "Home Phone,Work Phone,Cell Phone,Pet Name,Microchip Number,Service Date," \
            "Date of Birth,Species,Sex,Spayed/Neutered,Primary Breed,Secondary Breed," \
            "Color,Implanting Organization,Rescue Group Email\n"
        self.saveFile(os.path.join(self.publishDir, outputfile), header + "\n".join(csv))
        self.log("Uploading datafile %s" % outputfile)
        self.upload(outputfile)
        self.log("Uploaded %s" % outputfile)
        self.log("-- FILE DATA --")
        self.log(header + "\n".join(csv))
        self.cleanup()


