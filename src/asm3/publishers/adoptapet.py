
import asm3.configuration
import asm3.i18n
import asm3.medical

from .base import FTPPublisher
from asm3.sitedefs import ADOPTAPET_FTP_HOST
from asm3.typehints import Database, PublishCriteria, ResultRow

import os
import sys

class AdoptAPetPublisher(FTPPublisher):
    """
    Handles publishing to AdoptAPet.com
    """
    def __init__(self, dbo: Database, publishCriteria: PublishCriteria) -> None:
        publishCriteria.uploadDirectly = True
        publishCriteria.forceReupload = False
        publishCriteria.checkSocket = True
        publishCriteria.scaleImages = 1
        publishCriteria.thumbnails = False
        FTPPublisher.__init__(self, dbo, publishCriteria, 
            ADOPTAPET_FTP_HOST, asm3.configuration.adoptapet_user(dbo), 
            asm3.configuration.adoptapet_password(dbo))
        self.initLog("adoptapet", "AdoptAPet Publisher")

    def apYesNo(self, condition: bool) -> str:
        """
        Returns a CSV entry for yes or no based on the condition
        """
        if condition:
            return "\"1\""
        else:
            return "\"0\""

    def apYesNoUnknown(self, ourval: int) -> str:
        """
        Returns a CSV entry for yes or no based on our yes/no/unknown.
        In our scheme 0 = yes, 1 = no, 2 = unknown
        Their scheme 0 = no, 1 = yes, blank = unknown
        """
        if ourval == 0:
            return "\"1\""
        elif ourval == 1:
            return "\"0\""
        else:
            return "\"\""

    def apHairLength(self, a: ResultRow) -> str:
        """
        Returns a valid hair length entry for adoptapet.
        For species "Cat", values are "Short", "Medium" or "Long"
        For species "Rabbit", values are "Short" or "Long"
        For species "Small Animal", values are "Hairless", "Short", "Medium" or "Long"
        """
        s = a["PETFINDERSPECIES"]
        c = a["COATTYPENAME"]
        if s == "Cat":
            if c in ("Short", "Medium", "Long"):
                return c
            return "Short"
        elif s == "Rabbit":
            if c in ("Short", "Long"):
                return c
            return "Short"
        elif s == "Small Animal":
            if c in ("Hairless", "Short", "Medium", "Long"):
                return c
            return "Short"
        return ""

    def apMapFile(self, includecolours: bool) -> str:
        breedmap = "Appenzell Mountain Dog=Shepherd (Unknown Type)\n" \
            "American Bully=Bull Terrier\n" \
            "Australian Cattle Dog/Blue Heeler=Australian Cattle Dog\n" \
            "Belgian Shepherd Dog Sheepdog=Belgian Shepherd\n" \
            "Belgian Shepherd Tervuren=Belgian Tervuren\n" \
            "Belgian Shepherd Malinois=Belgian Malinois\n" \
            "Black Labrador Retriever=Labrador Retriever\n" \
            "Blue Lacy=Blue Lacy/Texas Lacy\n" \
            "Brittany Spaniel=Brittany\n" \
            "Cane Corso Mastiff=Cane Corso\n" \
            "Chinese Crested Dog=Chinese Crested\n" \
            "Chinese Foo Dog=Shepherd (Unknown Type)\n" \
            "Chocolate Labrador Retriever=Labrador Retriever\n" \
            "Dandi Dinmont Terrier=Dandie Dinmont Terrier\n" \
            "English Cocker Spaniel=Cocker Spaniel\n" \
            "English Coonhound=English (Redtick) Coonhound\n" \
            "Flat-coated Retriever=Flat-Coated Retriever\n" \
            "Fox Terrier=Fox Terrier (Smooth)\n" \
            "Hound=Hound (Unknown Type)\n" \
            "Illyrian Sheepdog=Shepherd (Unknown Type)\n" \
            "McNab=Shepherd (Unknown Type)\n" \
            "Mixed Breed=Mixed Breed (Medium)\n" \
            "Mountain Dog=Bernese Mountain Dog\n" \
            "New Guinea Singing Dog=Shepherd (Unknown Type)\n" \
            "Newfoundland Dog=Newfoundland\n" \
            "Norweigan Lundehund=Shepherd (Unknown Type)\n" \
            "Peruvian Inca Orchid=Shepherd (Unknown Type)\n" \
            "Pit Bull Terrier=American Pit Bull Terrier\n" \
            "Poodle=Poodle (Standard)\n" \
            "Retriever=Retriever (Unknown Type)\n" \
            "Saint Bernard St. Bernard=St. Bernard\n" \
            "Schipperkev=Schipperke\n" \
            "Schnauzer=Schnauzer (Standard)\n" \
            "Scottish Terrier Scottie=Scottie, Scottish Terrier\n" \
            "Setter=Setter (Unknown Type)\n" \
            "Sheep Dog=Old English Sheepdog\n" \
            "Shepherd=Shepherd (Unknown Type)\n" \
            "Shetland Sheepdog Sheltie=Sheltie, Shetland Sheepdog\n" \
            "Spaniel=Spaniel (Unknown Type)\n" \
            "Spitz=Spitz (Unknown Type, Medium)\n" \
            "South Russian Ovcharka=Shepherd (Unknown Type)\n" \
            "Terrier=Terrier (Unknown Type, Small)\n" \
            "West Highland White Terrier Westie=Westie, West Highland White Terrier\n" \
            "White German Shepherd=German Shepherd Dog\n" \
            "Wire-haired Pointing Griffon=Wirehaired Pointing Griffon\n" \
            "Wirehaired Terrier=Terrier (Unknown Type, Medium)\n" \
            "Yellow Labrador Retriever=Labrador Retriever\n" \
            "Yorkshire Terrier Yorkie=Yorkie, Yorkshire Terrier\n" \
            "American Siamese=Siamese\n" \
            "Bobtail=American Bobtail\n" \
            "Burmilla=Burmese\n" \
            "Canadian Hairless=Sphynx\n" \
            "Dilute Calico=Calico\n" \
            "Dilute Tortoiseshell=Domestic Shorthair\n" \
            "Domestic Long Hair=Domestic Longhair\n" \
            "Domestic Long Hair-black=Domestic Longhair\n" \
            "Domestic Long Hair - buff=Domestic Longhair\n" \
            "Domestic Long Hair-gray=Domestic Longhair\n" \
            "Domestic Long Hair - orange=Domestic Longhair\n" \
            "Domestic Long Hair - orange and white=Domestic Longhair\n" \
            "Domestic Long Hair - gray and white=Domestic Longhair\n" \
            "Domestic Long Hair-white=Domestic Longhair\n" \
            "Domestic Long Hair-black and white=Domestic Longhair\n" \
            "Domestic Long Hair (Black)=Domestic Longhair\n" \
            "Domestic Long Hair (Buff)=Domestic Longhair\n" \
            "Domestic Long Hair (Gray)=Domestic Longhair\n" \
            "Domestic Long Hair (Orange)=Domestic Longhair\n" \
            "Domestic Long Hair (Orange & White)=Domestic Longhair\n" \
            "Domestic Long Hair (Gray & White)=Domestic Longhair\n" \
            "Domestic Long Hair (White)=Domestic Longhair\n" \
            "Domestic Long Hair (Black & White)=Domestic Longhair\n" \
            "Domestic Medium Hair=Domestic Mediumhair\n" \
            "Domestic Medium Hair - buff=Domestic Mediumhair\n" \
            "Domestic Medium Hair - gray and white=Domestic Mediumhair\n" \
            "Domestic Medium Hair-white=Domestic Mediumhair\n" \
            "Domestic Medium Hair-orange=Domestic Mediumhair\n" \
            "Domestic Medium Hair - orange and white=Domestic Mediumhair\n" \
            "Domestic Medium Hair-black and white=Domestic Mediumhair\n" \
            "Domestic Medium Hair (Buff)=Domestic Mediumhair\n" \
            "Domestic Medium Hair (Gray & White)=Domestic Mediumhair\n" \
            "Domestic Medium Hair (White)=Domestic Mediumhair\n" \
            "Domestic Medium Hair (Orange)=Domestic Mediumhair\n" \
            "Domestic Medium Hair (Orange & White)=Domestic Mediumhair\n" \
            "Domestic Medium Hair (Black & White)=Domestic Mediumhair\n" \
            "Domestic Short Hair=Domestic Shorthair\n" \
            "Domestic Short Hair - buff=Domestic Shorthair\n" \
            "Domestic Short Hair - gray and white=Domestic Shorthair\n" \
            "Domestic Short Hair-white=Domestic Shorthair\n" \
            "Domestic Short Hair-orange=Domestic Shorthair\n" \
            "Domestic Short Hair - orange and white=Domestic Shorthair\n" \
            "Domestic Short Hair-black and white=Domestic Shorthair\n" \
            "Domestic Short Hair (Buff)=Domestic Shorthair\n" \
            "Domestic Short Hair (Gray & White)=Domestic Shorthair\n" \
            "Domestic Short Hair (White)=Domestic Shorthair\n" \
            "Domestic Short Hair (Orange)=Domestic Shorthair\n" \
            "Domestic Short Hair (Orange & White)=Domestic Shorthair\n" \
            "Domestic Short Hair (Black & White)=Domestic Shorthair\n" \
            "Exotic Shorthair=Exotic\n" \
            "Extra-Toes Cat (Hemingway Polydactyl)=Hemingway/Polydactyl\n" \
            "Oriental Long Hair=Oriental\n" \
            "Oriental Short Hair=Oriental\n" \
            "Oriental Tabby=Oriental\n" \
            "Pixie-Bob=Domestic Shorthair\n" \
            "Sphynx (hairless cat)=Sphynx\n" \
            "Tabby=Domestic Shorthair\n" \
            "Tabby - Orange=Domestic Shorthair\n" \
            "Tabby - Grey=Domestic Shorthair\n" \
            "Tabby - Brown=Domestic Shorthair\n" \
            "Tabby - white=Domestic Shorthair\n" \
            "Tabby - buff=Domestic Shorthair\n" \
            "Tabby - black=Domestic Shorthair\n" \
            "Tabby (Orange)=Domestic Shorthair\n" \
            "Tabby (Grey)=Domestic Shorthair\n" \
            "Tabby (Brown)=Domestic Shorthair\n" \
            "Tabby (White)=Domestic Shorthair\n" \
            "Tabby (Buff)=Domestic Shorthair\n" \
            "Tabby (Black)=Domestic Shorthair\n" \
            "Tiger=Domestic Shorthair\n" \
            "Torbie=Domestic Shorthair\n" \
            "Tortoiseshell=Domestic Shorthair\n" \
            "Tuxedo=Domestic Shorthair\n" \
            "Angora Rabbit=Angora, English\n" \
            "English Lop=Lop, English\n" \
            "French-Lop=Lop, French\n" \
            "Hotot=Blanc de Hotot\n" \
            "Holland Lop=Lop, Holland\n" \
            "Lop Eared=Lop-Eared\n" \
            "Mini-Lop=Mini Lop\n" \
            "Bunny Rabbit=Other/Unknown\n" \
            "Pot Bellied=Pig (Potbellied)\n" \
            "Budgie/Budgerigar=Budgie\n" \
            "Parakeet (Other)=Parakeet - Other\n"
        defmap = "; AdoptAPet.com import map. This file was autogenerated by\n" \
            "; Animal Shelter Manager. http://sheltermanager.com\n" \
            "; The FREE, open source solution for animal sanctuaries and rescue shelters.\n\n" \
            "#1:Id=Id\n" \
            "#2:Animal=Animal\n" \
            "Sugar Glider=Small Animal\n" \
            "Mouse=Small Animal\n" \
            "Rat=Small Animal\n" \
            "Hedgehog=Small Animal\n" \
            "Dove=Bird\n" \
            "Ferret=Small Animal\n" \
            "Chinchilla=Small Animal\n" \
            "Snake=Reptile\n" \
            "Tortoise=Reptile\n" \
            "Terrapin=Reptile\n" \
            "Chicken=Farm Animal\n" \
            "Owl=Bird\n" \
            "Goat=Farm Animal\n" \
            "Goose=Bird\n" \
            "Gerbil=Small Animal\n" \
            "Cockatiel=Bird\n" \
            "Guinea Pig=Small Animal\n" \
            "Hamster=Small Animal\n" \
            "Camel=Horse\n" \
            "Pony=Horse\n" \
            "Donkey=Horse\n" \
            "Llama=Horse\n" \
            "Pig=Farm Animal\n" \
            "Barnyard=Farm Animal\n" \
            "Small&Furry=Small Animal\n" \
            "#3:Breed=Breed\n"
        defmap += breedmap
        defmap += "#4:Breed2=Breed2\n"
        defmap += breedmap
        defmap += "#5:Purebred=Purebred\n" \
            "#6:Age=Age\n" \
            "#7:Name=Name\n" \
            "#8:Size=Size\n" \
            "#9:Sex=Sex\n"
        if not includecolours:
            defmap += "#10:Description=Description\n" \
            "#11:Status=Status\n" \
            "#12:GoodWKids=GoodWKids\n" \
            "#13:GoodWCats=GoodWCats\n" \
            "#14:GoodWDogs=GoodWDogs\n" \
            "#15:SpayedNeutered=SpayedNeutered\n" \
            "#16:ShotsCurrent=ShotsCurrent\n" \
            "#17:Housetrained=Housetrained\n" \
            "#18:Declawed=Declawed\n" \
            "#19:SpecialNeeds=SpecialNeeds\n" \
            "#20:HairLength=HairLength\n" \
            "#21:YouTubeVideoURL=YouTubeVideoURL\n" \
            "#22:Birthdate=Birthdate\n" \
            "#23:Sizecurrent=Sizecurrent\n" \
            "#24:SizeUOM=SizeUOM\n" \
            "#25:AdoptionFee=AdoptionFee"
        else:
            defmap += "#10:Color=Color\n" \
            "#11:Description=Description\n" \
            "#12:Status=Status\n" \
            "#13:GoodWKids=GoodWKids\n" \
            "#14:GoodWCats=GoodWCats\n" \
            "#15:GoodWDogs=GoodWDogs\n" \
            "#16:SpayedNeutered=SpayedNeutered\n" \
            "#17:ShotsCurrent=ShotsCurrent\n" \
            "#18:Housetrained=Housetrained\n" \
            "#19:Declawed=Declawed\n" \
            "#20:SpecialNeeds=SpecialNeeds\n" \
            "#21:HairLength=HairLength\n" \
            "#22:YouTubeVideoURL=YouTubeVideoURL\n" \
            "#23:Birthdate=Birthdate\n" \
            "#24:Sizecurrent=Sizecurrent\n" \
            "#25:SizeUOM=SizeUOM\n" \
            "#26:AdoptionFee=AdoptionFee"

        return defmap

    def apYouTubeURL(self, u: str) -> str:
        """
        Returns a YouTube URL in the format adoptapet want - https://www.youtube.com/watch?v=X
        returns a blank if u is not a youtube URL
        """
        if u is None: return ""
        if u.find("youtube") == -1 and u.find("youtu.be") == -1: return ""
        watch = ""
        if u.find("watch?v=") != -1:
            watch = u[u.rfind("v=")+2:]
        if u.find("youtu.be/") != -1:
            watch = u[u.rfind("/")+1:]
        if watch == "":
            return ""
        return "https://www.youtube.com/watch?v=%s" % watch

    def run(self) -> None:
        
        self.log("AdoptAPetPublisher starting...")

        if self.isPublisherExecuting(): return
        self.updatePublisherProgress(0)
        self.setLastError("")
        self.setStartPublishing()

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
        if not self.isChangedSinceLastPublish():
            self.logSuccess("No animal/movement changes have been made since last publish")
            self.setLastError("No animal/movement changes have been made since last publish", log_error = False)
            self.cleanup()
            return

        shelterid = asm3.configuration.adoptapet_user(self.dbo)
        if shelterid == "":
            self.setLastError("No AdoptAPet.com shelter id has been set.")
            self.cleanup()
            return

        # NOTE: We still publish even if there are no animals. This prevents situations
        # where the last animal can't be removed from AdoptAPet because the shelter
        # has no animals to send.
        animals = self.getMatchingAnimals()
        if len(animals) == 0:
            self.log("No animals found to publish, sending empty file.")

        if not self.openFTPSocket(): 
            self.setLastError("Failed opening FTP socket.")
            if self.logSearch("530 Login") != -1:
                self.log("Found 530 Login incorrect: disabling AdoptAPet publisher.")
                asm3.configuration.publishers_enabled_disable(self.dbo, "ap")
            self.cleanup()
            return

        # Do the images first
        self.mkdir("photos")
        self.chdir("photos", "photos")

        # Remove old unreferenced images before we start
        self.clearUnusedFTPImages(animals)

        csv = []

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

                # Upload images for this animal
                self.uploadImages(an)

                # Add the CSV line
                csv.append( self.processAnimal(an) )

                # Mark success in the log
                self.logSuccess("Processed: %s: %s (%d of %d)" % ( an["SHELTERCODE"], an["ANIMALNAME"], anCount, len(animals)))

            except Exception as err:
                self.logError("Failed processing animal: %s, %s" % (str(an["SHELTERCODE"]), err), sys.exc_info())

        # Mark published
        self.markAnimalsPublished(animals, first=True)

        # Upload the datafiles
        mapfile = self.apMapFile(self.pc.includeColours)
        self.saveFile(os.path.join(self.publishDir, "import.cfg"), mapfile)
        self.saveFile(os.path.join(self.publishDir, "pets.csv"), "\n".join(csv))
        self.log("Saving datafile and map, %s %s" % ("pets.csv", "import.cfg"))
        self.chdir("..", "")
        self.log("Uploading pets.csv")
        self.upload("pets.csv")
        if not self.pc.noImportFile:
            self.log("Uploading import.cfg")
            self.upload("import.cfg")
        else:
            self.log("import.cfg upload is DISABLED")
        self.log("-- FILE DATA --(csv)")
        self.log("\n".join(csv))
        self.log("-- FILE DATA --(map)")
        self.log(mapfile)
        self.cleanup()

    def processAnimal(self, an: ResultRow) -> str:
        """
        Builds a line for the CSV file from an animal and returns it.
        """
        line = []
        # Id
        line.append(an.SHELTERCODE)
        # Species
        line.append(an.PETFINDERSPECIES)
        # Breed 1
        line.append(an.PETFINDERBREED)
        # Breed 2
        line.append(self.getPublisherBreed(an, 2))
        # Purebred 
        line.append(self.apYesNo(not self.isCrossBreed(an)))
        # Age, one of Adult, Baby, Senior and Young
        ageinyears = asm3.i18n.date_diff_days(an.DATEOFBIRTH, asm3.i18n.now(self.dbo.timezone))
        ageinyears /= 365.0
        agename = "Adult"
        if ageinyears < 0.5: agename = "Baby"
        elif ageinyears < 2: agename = "Young"
        elif ageinyears < 9: agename = "Adult"
        else: agename = "Senior"
        line.append(agename)
        # Name
        line.append(an.ANIMALNAME)
        # Size, one of S, M, L, XL
        ansize = "M"
        if an["SIZE"] == 0: ansize = "XL"
        elif an["SIZE"] == 1: ansize = "L"
        elif an["SIZE"] == 2: ansize = "M"
        elif an["SIZE"] == 3: ansize = "S"
        # If the animal is not a dog or cat, leave size blank as
        # adoptapet will throw errors otherwise
        if an["PETFINDERSPECIES"] != "Dog" and an["PETFINDERSPECIES"] != "Cat":
            ansize = ""
        line.append(ansize)
        # Sex, one of M or F
        sexname = "M"
        if an["SEX"] == 0: sexname = "F"
        line.append(sexname)
        # Colour
        if self.pc.includeColours: line.append(an.ADOPTAPETCOLOUR)
        # Description
        line.append(self.getDescription(an, crToBr=True))
        # Status, one of Available, Adopted or Delete
        line.append("Available")
        # Good with Kids
        line.append(self.apYesNoUnknown(an.ISGOODWITHCHILDREN))
        # Good with Cats
        line.append(self.apYesNoUnknown(an.ISGOODWITHCATS))
        # Good with Dogs
        line.append(self.apYesNoUnknown(an.ISGOODWITHDOGS))
        # Spayed/Neutered
        line.append(self.apYesNo(an.NEUTERED == 1))
        # Shots current
        line.append(self.apYesNo(asm3.medical.get_vaccinated(self.dbo, int(an["ID"]))))
        # Housetrained
        line.append(self.apYesNoUnknown(an.ISHOUSETRAINED))
        # Declawed
        line.append(self.apYesNo(an.DECLAWED == 1))
        # Special needs
        line.append(self.apYesNo(an.CRUELTYCASE == 1 or an.HASSPECIALNEEDS == 1))
        # Hair Length
        line.append(self.apHairLength(an))
        # YouTube Video URL
        line.append(self.apYouTubeURL(an.WEBSITEVIDEOURL))
        # Birthdate 
        line.append(asm3.i18n.format_date(an.DATEOFBIRTH, "%m/%d/%Y"))
        # Sizecurrent
        line.append(str(asm3.utils.cint(an.WEIGHT)))
        # SizeUOM
        line.append("lbs")
        # AdoptionFee
        if an.FEE == 0:
            line.append("")
        else:
            line.append(str(int(asm3.utils.cint(an.FEE) / 100)))
        return self.csvLine(line)

