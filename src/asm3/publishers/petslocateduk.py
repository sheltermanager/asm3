
import asm3.animal
import asm3.configuration
import asm3.i18n
import asm3.lostfound
import asm3.utils

from .base import FTPPublisher
from asm3.sitedefs import PETSLOCATED_FTP_HOST, PETSLOCATED_FTP_USER, PETSLOCATED_FTP_PASSWORD
from asm3.typehints import Any, datetime, Database, PublishCriteria, ResultRow

import os
import sys


class PetsLocatedUKPublisher(FTPPublisher):
    """
    Handles publishing to petslocated.com in the UK
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.uploadDirectly = True
        publishCriteria.thumbnails = False
        publishCriteria.checkSocket = True
        publishCriteria.includeColours = True
        publishCriteria.scaleImages = 1
        FTPPublisher.__init__(self, dbo, publishCriteria, 
            PETSLOCATED_FTP_HOST, PETSLOCATED_FTP_USER, PETSLOCATED_FTP_PASSWORD)
        self.initLog("petslocated", "PetsLocated UK Publisher")

    def plcAge(self, agegroup: str) -> str:
        if agegroup is None: return "Older"
        if agegroup == "Baby": return "Very Young"
        elif agegroup.startswith("Young"): return "Young"
        elif agegroup.find("Adult") != -1: return "Average"
        else:
            return "Older"

    def plcAgeYears(self, agegroup: str = "", dob: datetime = None) -> str:
        """
        Returns an age in years as a float/string from either an agegroup
        or a date of birth.
        """
        years = 1
        if dob is not None:
            days = asm3.i18n.date_diff_days( dob, asm3.i18n.now(self.dbo.timezone) )
            years = days / 365.0
        else:
            years = asm3.configuration.age_group_for_name(self.dbo, agegroup) 
            if years == 0: years = 1
        return "%0.1f" % years

    def plcChipChecked(self, chipped: int) -> int:
        if chipped == 1:
            return 2
        return 3

    def plcNeutered(self, neutered: Any) -> str:
        """ 
        Handles neuter/spay from a comments field or the neutered column depending 
        on whether the source is animallost or animal
        """
        if asm3.utils.is_str(neutered):
            if neutered.find("payed") != -1 or neutered.find("eutered") != -1:
                return "y"
        elif asm3.utils.is_numeric(neutered):
            if neutered == 1:
                return "y"
            return "n"
        return "u"

    def plcPostcode(self, postcode1: str, postcode2: str = "", postcode3: str = "") -> str:
        """ Returns the postcode prefix of the first non-blank value given """
        postcode = postcode1
        if postcode is None or postcode == "": postcode = postcode2
        if postcode is None or postcode == "": postcode = postcode3
        if postcode.find(" ") == -1: return postcode
        return postcode[0:postcode.find(" ")]

    def plcSex(self, sexID: int) -> str:
        if sexID == 0: return "f"
        if sexID == 1: return "m"
        return "u"

    def plcHairType(self, an: ResultRow) -> str:
        HAIRLESS = [ "Bird", "Reptile", "Fish", "Snake", "Hedgehog", "Tortoise", "Terrapin", 
            "Lizard", "Chicken", "Owl", "Cockatiel", "Goose", "Goldfish" ]
        # Dogs
        speciesname = an["SPECIESNAME"]
        if speciesname == "Dog":
            if "COATTYPENAME" in an and an["COATTYPENAME"] == "Long": return "Long"
            elif "COATTYPENAME" in an and an["COATTYPENAME"] == "Hairless": return "Not Applicable"
            else: return "Short"
        # Cats
        elif speciesname == "Cat":
            if an["BREEDNAME"].find("Short") != -1 or an["BREEDNAME"].find("DSH") != -1: return "Short"
            elif an["BREEDNAME"].find("Medium") != -1 or an["BREEDNAME"].find("DMH") != -1: return "Medium"
            elif an["BREEDNAME"].find("Long") != -1 or an["BREEDNAME"].find("DLH") != -1: return "Long"
            else: return "Short"
        # Species that don't have hair
        elif speciesname in HAIRLESS: return "Not Applicable"
        else:
            return "Short"

    def plcColour(self, s: str) -> str:
        colourmap = {
            "Black": "Mainly/All Black",
            "Black - with Tan, Yellow or Fawn": "Mainly/All Black",
            "Black - with White": "Black and White",
            "Brindle": "Brindle",
            "Brindle - with White": "Brindle",
            "Brown/Chocolate": "Brown/Chocolate",
            "Brown/Chocolate - with Black": "Brown/Chocolate",
            "Brown/Chocolate - with White": "Brown/Chocolate",
            "Red/Golden/Orange/Chestnut": "Golden/Sandy/Apricot",
            "Red/Golden/Orange/Chestnut - with Black": "Golden/Sandy/Apricot",
            "Red/Golden/Orange/Chestnut - with White": "Golden/Sandy/Apricot",
            "Silver & Tan (Yorkie colors)": "Tri-colour",
            "Tan/Yellow/Fawn": "Golden/Sandy/Apricot",
            "Tan/Yellow/Fawn - with White": "Golden/Sandy/Apricot",
            "Tricolor (Tan/Brown & Black & White)": "Tri-colour",
            "White": "White",
            "White - with Black": "Mainly/All White",
            "White - with Brown or Chocolate": "Mainly/All White",
            "Black - with Brown, Red, Golden, Orange or Chestnut": "Mainly/All Black",
            "Black - with Gray or Silver": "Mainly/All Black",
            "Brown/Chocolate - with Tan": "Brown/Tan",
            "Gray/Blue/Silver/Salt & Pepper": "Grey/Silver/Blue",
            "Gray/Silver/Salt & Pepper - with White": "Grey/Silver/Blue",
            "Gray/Silver/Salt & Pepper - with Black": "Grey/Silver/Blue",
            "Merle": "Mainly/All White",
            "Tan/Yellow/Fawn - with Black": "Brown/Tan",
            "White - with Tan, Yellow or Fawn": "Mainly/All White",
            "White - with Red, Golden, Orange or Chestnut": "Mainly/All White",
            "White - with Gray or Silver": "Mainly/All White",
            "Black (All)": "Mainly/All Black",
            "Cream or Ivory": "Beige/Cream",
            "Cream or Ivory (Mostly)": "Beige/Cream",
            "Spotted Tabby/Leopard Spotted": "Spotted",
            "Black (Mostly)": "Mainly/All Black",
            "Black & White or Tuxedo": "Black and White",
            "Brown or Chocolate": "Brown/Chocolate",
            "Brown or Chocolate (Mostly)": "Brown/Chocolate",
            "Brown Tabby": "Tabby",
            "Calico or Dilute Calico": "Calico",
            "Gray or Blue ": "Blue",
            "Gray or Blue (Mostly)": "Blue",
            "Gray, Blue or Silver Tabby": "Tabby",
            "Orange or Red": "Ginger/Orange",
            "Orange or Red (Mostly)": "Ginger/Orange",
            "Orange or Red Tabby": "Ginger/Orange",
            "Tan or Fawn ": "Beige/Cream",
            "Tan or Fawn (Mostly)": "Beige/Cream",
            "Tan or Fawn Tabby": "Tabby",
            "Tiger Striped": "Tabby",
            "Tortoiseshell": "Tortoiseshell",
            "White": "White",
            "White (Mostly)": "Mainly/All White",
            "Palomino": "White",
            "Gray": "White",
            "Dun": "White",
            "Cremello": "White",
            "Chestnut/Sorrel": "Brown",
            "Champagne": "White",
            "Buckskin": "Brown",
            "Bay": "Brown",
            "Appy": "Brown",
            "Grullo": "Brown",
            "White": "White",
            "Roan": "White",
            "Perlino": "White",
            "Paint": "White",
            "Green": "Green",
            "Olive": "Green",
            "Orange": "Red",
            "Pink": "Pink",
            "Purple/Violet": "Pink",
            "Red": "Red",
            "Rust": "Red",
            "Tan": "Brown",
            "Buff": "Brown",
            "Yellow": "Gold/Yellow",
            "White": "White",
            "Blue": "Blue",
            "Brown": "Brown",
            "Sable": "White",
            "Albino or Red-Eyed White": "White",
            "Blond/Golden": "Gold",
            "Chinchilla": "Brown",
            "Chocolate": "Brown",
            "Cinnamon": "Brown",
            "Copper": "Brown",
            "Cream": "White",
            "Dutch": "White",
            "Fawn": "Brown",
            "Grey/Silver": "Grey/Seilver",
            "Harlequin": "White",
            "Lilac": "Grey/Silver",
            "Multi": "Multi-Coloured",
            "Agouti": "Ginger",
            "Siamese": "Black",
            "Tan": "Brown",
            "Tortoise": "Multi-Coloured",
            "Tri-color": "Multi-Coloured",
            "White": "White",
            "Tan or Beige": "Brown",
            "Silver or Gray": "Grey/Silver",
            "Sable": "White",
            "Multi": "Multi-Coloured",
            "Golden": "Gold",
            "Cream": "White",
            "Calico": "Multi-Coloured",
            "Blonde": "Gold",
            "Albino or Red-Eyed White": "White"
        }
        if s in colourmap: return colourmap[s]
        return "Black"

    def plcSpecies(self, s: str, ps: str) -> str:
        speciesmap = {
            "Barnyard": "Goat", 
            "Bird": "Bird", 
            "Cat": "Cat",
            "Chinchilla": "Chinchilla",
            "Degu": "Degu",
            "Dog": "Dog",
            "Ferret": "Ferret",
            "Goat": "Goat",
            "Guinea Pig": "Guinea Pig",
            "Hamster": "Hamster",
            "Horse": "Horse", 
            "Pig": "Pig",
            "Rabbit": "Rabbit",
            "Reptile": "Snake/Reptile",
            "Snake": "Snake/Reptile",
            "Spider": "Spider",
            "Terrapin": "Tortoise/Terrapin/Turtle",
            "Tortoise": "Tortoise/Terrapin/Turtle",
            "Turtle": "Tortoise/Terrapin/Turtle",
            "Small&Furry": "Mouse/Rat"
        }
        if s in speciesmap: return speciesmap[s]
        if ps in speciesmap: return speciesmap[ps]
        return "Cat"

    def run(self) -> None:
        
        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

        customerid = asm3.configuration.petslocated_customerid(self.dbo)
        if customerid == "":
            self.setLastError("No petslocated.com customer ID has been set.")
            return

        if not self.checkMappedSpecies():
            self.setLastError("Not all species have been mapped.")
            self.cleanup()
            return
        if not self.checkMappedBreeds():
            self.setLastError("Not all breeds have been mapped.")
            self.cleanup()
            return
        if self.pc.includeColours and not self.checkMappedColours():
            self.setLastError("Not all colours have been mapped and sending colours is enabled")
            self.cleanup()
            return

        includelost = False # Don't publish lost animals - losers pay 12 pounds to post for 12 months
        includeshelter = asm3.configuration.petslocated_includeshelter(self.dbo)
        shelterwithflag = asm3.configuration.petslocated_animalflag(self.dbo)

        if shelterwithflag == "" and includeshelter:
            self.setLastError("Include shelter animals set, but no flag chosen")
            self.cleanup()
            return

        lostanimals = asm3.lostfound.get_lostanimal_find_advanced(self.dbo, {})
        foundanimals = asm3.lostfound.get_foundanimal_last_days(self.dbo, 90)
        animals = []

        if includeshelter:
            animals = self.dbo.query(asm3.animal.get_animal_query(self.dbo) + " WHERE a.Archived = 0 AND " \
                "a.AdditionalFlags LIKE ?", ["%%%s|%%" % shelterwithflag])

        if len(animals) == 0 and len(foundanimals) == 0 and len(lostanimals) == 0:
            self.setLastError("No animals found to publish.")
            self.cleanup()
            return

        if not self.openFTPSocket(): 
            self.setLastError("Failed opening FTP socket.")
            if self.logSearch("530 Login") != -1:
                self.log("Found 530 Login incorrect: disabling PetsLocated UK publisher.")
                asm3.configuration.publishers_enabled_disable(self.dbo, "pcuk")
            self.cleanup()
            return

        csv = []
        header = "customerurn,importkey,asm3.lostfound.pettype,breed,sexofpet,neutered,petname,internalref,petage,hairtype,petcoloursall,chipchecked,chipno,petfeatures,lastlocationst,lastlocation,locationpostcode,datelostfound,otherdetails,privatenotes,showonsite,rawpettype,rawbreed,rawcolour,rawcoat,rawageyears\n"

        # Lost Animals
        if includelost:
            anCount = 0
            for an in lostanimals:
                try:
                    anCount += 1
                    self.log("Processing Lost Animal: %d: %s (%d of %d)" % ( an["ID"], an["COMMENTS"], anCount, len(foundanimals)))

                    # If the user cancelled, stop now
                    if self.shouldStopPublishing(): 
                        self.stopPublishing()
                        return

                    csv.append( self.processLostAnimal(an, customerid) )

                    # Mark success in the log
                    self.logSuccess("Processed Lost Animal: %d: %s (%d of %d)" % ( an["ID"], an["COMMENTS"], anCount, len(foundanimals)))

                except Exception as err:
                    self.logError("Failed processing lost animal: %s, %s" % (str(an["ID"]), err), sys.exc_info())

        # Found Animals
        anCount = 0
        for an in foundanimals:
            try:
                anCount += 1
                self.log("Processing Found Animal: %d: %s (%d of %d)" % ( an["ID"], an["COMMENTS"], anCount, len(foundanimals)))

                # If the user cancelled, stop now
                if self.shouldStopPublishing(): 
                    self.stopPublishing()
                    return

                csv.append( self.processFoundAnimal(an, customerid) )

                # Mark success in the log
                self.logSuccess("Processed Found Animal: %d: %s (%d of %d)" % ( an["ID"], an["COMMENTS"], anCount, len(foundanimals)))

            except Exception as err:
                self.logError("Failed processing found animal: %s, %s" % (str(an["ID"]), err), sys.exc_info())

        # Shelter animals
        if includeshelter:
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

                    # Upload one image for this animal
                    # self.uploadImage(an, an["WEBSITEMEDIANAME"], an["SHELTERCODE"] + ".jpg")

                    csv.append( self.processAnimal(an, customerid) )

                    # Mark success in the log
                    self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))

                except Exception as err:
                    self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

            # Mark published
            self.markAnimalsPublished(animals, first=True)

        filename = "%s_%s.csv" % (customerid, self.dbo.database)
        self.saveFile(os.path.join(self.publishDir, filename), header + "\n".join(csv))
        self.log("Uploading datafile %s" % filename)
        self.upload(filename)
        self.log("Uploaded %s" % filename)
        self.log("-- FILE DATA --")
        self.log(header + "\n".join(csv))
        # Clean up
        self.closeFTPSocket()
        self.deletePublishDirectory()
        self.saveLog()
        self.setPublisherComplete()

    def processLostAnimal(self, an: ResultRow, customerid: str = "") -> str:
        """ Process a lost animal record and return a CSV line """
        line = []
        # customerurn
        line.append("\"%s\"" % customerid)
        # importkey
        line.append("\"L%s\"" % an["ID"])
        # lostfound
        line.append("\"L\"")
        # pettype
        line.append("\"%s\"" % self.plcSpecies(an["SPECIESNAME"], an["SPECIESNAME"]))
        # breed
        line.append("\"%s\"" % an["BREEDNAME"])
        # sexofpet
        line.append("\"%s\"" % self.plcSex(an["SEX"]))
        # neutered
        line.append("\"%s\"" % (self.plcNeutered(an["DISTFEAT"])))
        # petname
        line.append("\"\"")
        # internalref
        line.append("\"L%s\"" % an["ID"])
        # petage
        line.append("\"%s\"" % self.plcAge(an["AGEGROUP"]))
        # hairtype
        line.append("\"%s\"" % self.plcHairType(an))
        # petcoloursall
        line.append("\"%s\"" % self.plcColour(an["ADOPTAPETCOLOUR"]))
        # chipchecked
        line.append("\"1\"")
        # chipno
        line.append("\"\"")
        # petfeatures
        line.append("\"%s\"" % an["DISTFEAT"])
        # lastlocationst
        line.append("\"\"")
        # lastlocation
        line.append("\"%s\"" % an["AREALOST"])
        # locationpostcode
        line.append("\"%s\"" % self.plcPostcode(an["AREAPOSTCODE"], an["OWNERPOSTCODE"]))
        # datelostfound
        line.append("\"%s\"" % asm3.i18n.python2display(self.locale, an["DATELOST"]))
        # otherdetails
        line.append("\"\"")
        # privatenotes
        line.append("\"%s\"" % an["COMMENTS"])
        # showonsite
        line.append("\"1\"")
        # rawpettype
        line.append("\"%s\"" % an["SPECIESNAME"])
        # rawbreed
        line.append("\"%s\"" % an["BREEDNAME"])
        # rawcolour
        line.append("\"%s\"" % an["BASECOLOURNAME"])
        # rawcoat
        line.append("\"\"")
        # rawageyears
        line.append("\"%s\"" % self.plcAgeYears(agegroup=an["AGEGROUP"]))
        return self.csvLine(line)

    def processFoundAnimal(self, an: ResultRow, customerid: str = "") -> str:
        """ Process a found animal record and return a CSV line """
        line = []
        # customerurn
        line.append("\"%s\"" % customerid)
        # importkey
        line.append("\"F%s\"" % an["ID"])
        # lostfound
        line.append("\"F\"")
        # pettype
        line.append("\"%s\"" % self.plcSpecies(an["SPECIESNAME"], an["SPECIESNAME"]))
        # breed
        line.append("\"%s\"" % an["BREEDNAME"])
        # sexofpet
        line.append("\"%s\"" % self.plcSex(an["SEX"]))
        # neutered
        line.append("\"%s\"" % (self.plcNeutered(an["DISTFEAT"])))
        # petname
        line.append("\"\"")
        # internalref
        line.append("\"F%s\"" % an["ID"])
        # petage
        line.append("\"%s\"" % self.plcAge(an["AGEGROUP"]))
        # hairtype
        line.append("\"%s\"" % self.plcHairType(an))
        # petcoloursall
        line.append("\"%s\"" % self.plcColour(an["ADOPTAPETCOLOUR"]))
        # chipchecked
        line.append("\"1\"")
        # chipno
        line.append("\"\"")
        # petfeatures
        line.append("\"%s\"" % an["DISTFEAT"])
        # lastlocationst
        line.append("\"\"")
        # lastlocation
        line.append("\"%s\"" % an["AREAFOUND"])
        # locationpostcode
        line.append("\"%s\"" % self.plcPostcode(an["AREAPOSTCODE"], an["OWNERPOSTCODE"]))
        # datelostfound
        line.append("\"%s\"" % asm3.i18n.python2display(self.locale, an["DATEFOUND"]))
        # otherdetails
        line.append("\"\"")
        # privatenotes
        line.append("\"%s\"" % an["COMMENTS"])
        # showonsite
        line.append("\"1\"")
        # rawpettype
        line.append("\"%s\"" % an["SPECIESNAME"])
        # rawbreed
        line.append("\"%s\"" % an["BREEDNAME"])
        # rawcolour
        line.append("\"%s\"" % an["BASECOLOURNAME"])
        # rawcoat
        line.append("\"\"")
        # rawageyears
        line.append("\"%s\"" % self.plcAgeYears(agegroup=an["AGEGROUP"]))
        return self.csvLine(line)

    def processAnimal(self, an: ResultRow, customerid: str = "") -> str:
        """ Process an animal record and return a CSV line """
        line = []
        # customerurn
        line.append("\"%s\"" % customerid)
        # importkey
        line.append("\"A%s\"" % an["ID"])
        # lostfound
        line.append("\"F\"")
        # pettype
        line.append("\"%s\"" % self.plcSpecies(an["SPECIESNAME"], an["PETFINDERSPECIES"]))
        # breed
        line.append("\"%s\"" % an["BREEDNAME"])
        # sexofpet
        line.append("\"%s\"" % self.plcSex(an["SEX"]))
        # neutered
        line.append("\"%s\"" % self.plcNeutered(an["NEUTERED"]))
        # petname
        line.append("\"%s\"" % an["ANIMALNAME"])
        # internalref
        line.append("\"A%s\"" % an["ID"])
        # petage
        line.append("\"%s\"" % self.plcAge(an["AGEGROUP"]))
        # hairtype
        line.append("\"%s\"" % self.plcHairType(an))
        # petcoloursall
        line.append("\"%s\"" % self.plcColour(an["ADOPTAPETCOLOUR"]))
        # chipchecked
        line.append("\"%d\"" % self.plcChipChecked(an["IDENTICHIPPED"]))
        # chipno
        line.append("\"%s\"" % an["IDENTICHIPNUMBER"])
        # petfeatures
        line.append("\"%s\"" % an["MARKINGS"])
        # lastlocationst
        line.append("\"\"")
        # lastlocation
        line.append("\"\"")
        # locationpostcode
        line.append("\"%s\"" % self.plcPostcode(an["ORIGINALOWNERPOSTCODE"]))
        # datelostfound
        line.append("\"%s\"" % asm3.i18n.python2display(self.locale, an["DATEBROUGHTIN"]))
        # otherdetails
        line.append("\"%s\"" % an["ANIMALCOMMENTS"])
        # privatenotes
        line.append("\"%s\"" % an["HIDDENANIMALDETAILS"])
        # showonsite
        line.append("\"1\"")
        # rawpettype
        line.append("\"%s\"" % an["SPECIESNAME"])
        # rawbreed
        line.append("\"%s\"" % an["BREEDNAME"])
        # rawcolour
        line.append("\"%s\"" % an["BASECOLOURNAME"])
        # rawcoat
        line.append("\"%s\"" % an["COATTYPENAME"])
        # rawageyears
        line.append("\"%s\"" % self.plcAgeYears(dob=an["DATEOFBIRTH"]))
        return self.csvLine(line)

