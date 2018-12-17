#!/usr/bin/python

import asm, os

"""
Import module to read from rescuegroups CSV export.
This is done with Reports, then Animals (All Fields) for adoptable and adopted, etc.
It produces an Animals.csv file.
If you use Animals->Exports, you can do a manual export for PetFinder that puts all
your images on their FTP server to pick up.

If RG are running slow, a custom report can be made with the following fields:

Animal ID, Internal ID, Status, Species, Name, Created, Last Updated, 
General Age, Mixed, Sex, Primary Breed, Secondary Breed, Color (General), 
Declawed, Special Needs, Altered, Housetrained, OK with Cats, OK with Kids, OK with Cats, 
Microchip Number, Description, Location, Summary, Picture 1

Will also import data from RG All Contacts report, called Contacts.csv:

Address, Comment, Email, First Name, Last Name, Phone (Cell), Phone (Home)

"""

PATH = "data/rg_ck1833"

DEFAULT_BREED = 261 # default to dsh
PETFINDER_ID = ""

animals = []
owners = []
movements = []

asm.setid("adoption", 100)
asm.setid("animal", 100)
asm.setid("owner", 100)
asm.setid("media", 100)
asm.setid("dbfs", 300)

def getdate(s):
    return asm.getdate_mmddyyyy(s)

def size_id_for_name(name):
    return {
        "": 3, 
        "LARGE": 1,
        "SMALL": 2,
        "MEDIUM": 3, 
        "X-LARGE": 0
    }[name.upper().strip()]

uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = "Unknown Owner"
uo.Comments = "Catchall for adopted animal data from RescueGroups"

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM adoption WHERE ID >= 100;"
print "DELETE FROM animal WHERE ID >= 100;"
print "DELETE FROM owner WHERE ID >= 100;"
print "DELETE FROM media WHERE ID >= 100;"
print "DELETE FROM dbfs WHERE ID >= 300;"
pfpage = ""
if PETFINDER_ID != "":
    pfpage = asm.petfinder_get_adoptable(PETFINDER_ID)

for d in asm.csv_to_list("%s/Animals.csv" % PATH):
    if d["Status"] == "Deleted": continue
    a = asm.Animal()
    animals.append(a)
    if d["Species"] == "Cat":
        animaltype = 11
        animalletter = "U"
    else:
        animaltype = 2
        animalletter = "D"
    a.AnimalTypeID = animaltype
    a.SpeciesID = asm.species_id_for_name(d["Species"])
    a.ShelterCode = "RG%s" % d["Animal ID"]
    a.ShortCode = a.ShelterCode
    a.AnimalName = d["Name"]
    broughtin = getdate(d["Created"])
    a.DateBroughtIn = broughtin
    dob = broughtin
    if d["General Age"].find("Baby") != -1:
        dob = asm.subtract_days(asm.today(), 91)
    elif d["General Age"].find("Young") != -1:
        dob = asm.subtract_days(asm.today(), 182)
    elif d["General Age"].find("Adult") != -1:
        dob = asm.subtract_days(asm.today(), 730)
    elif d["General Age"].find("Senior") != -1:
        dob = asm.subtract_days(asm.today(), 2555)
    a.DateOfBirth = dob
    a.EstimatedDOB = 1
    a.Sex = 1
    if d["Sex"].startswith("F"):
        a.Sex = 0
    a.BreedID = asm.breed_id_for_name(d["Primary Breed"], DEFAULT_BREED)
    osecondbreed = ""
    if not d["Mixed"] == "Yes":
        a.Breed2ID = a.BreedID
        a.BreedName = asm.breed_name_for_id(a.BreedID)
        a.CrossBreed = 0
    else:
        a.Breed2ID = a.BreedID
        if "Secondary Breed" in d: 
            a.Breed2ID = asm.breed_id_for_name(d["Secondary Breed"], DEFAULT_BREED)
            osecondbreed = d["Secondary Breed"]
        a.BreedName = asm.breed_name_for_id(a.BreedID) + " / " + asm.breed_name_for_id(a.Breed2ID)
        a.CrossBreed = 1
    a.BaseColourID = asm.colour_id_for_name(d["Color (General)"])
    a.ShelterLocation = 1
    if "Size Potential (General)" in d: a.Size = size_id_for_name(d["Size Potential (General)"])
    a.Declawed = d["Declawed"] == "Yes" and 1 or 0
    a.HasSpecialNeeds = d["Special Needs"] == "Yes" and 1 or 0
    a.EntryReasonID = 1
    a.Neutered = d["Altered"] == "Yes" and 1 or 0
    if d["Housetrained"] == "Yes": a.IsHouseTrained = 0
    if d["OK with Cats"] == "Yes": a.IsGoodWithDogs = 0
    if d["OK with Kids"] == "Yes": a.IsGoodWithChildren = 0
    if d["OK with Cats"] == "Yes": a.IsGoodWithCats = 0
    a.IdentichipNumber = d["Microchip Number"]
    if a.IdentichipNumber != "": a.Identichipped = 1
    a.AnimalComments = d["Description"]
    a.HiddenAnimalDetails = d["Summary"] + ", original breed: " + d["Primary Breed"] + " " + osecondbreed + ", color: " + \
        d["Color (General)"] + ", status: " + d["Status"] + ", internal: " + d["Internal ID"] + ", location: " + d["Location"]
    a.CreatedDate = getdate(d["Created"])
    a.LastChangedDate = getdate(d["Last Updated"])
    # If the animal is adopted, send it to our unknown owner
    if d["Status"] in ("Adopted", "Transferred", "Escaped", "Stolen"):
        mt = { "Adopted": 1, "Transferred": 3, "Escaped": 4, "Stolen": 6 }[d["Status"]]
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = uo.ID
        m.AnimalID = a.ID
        m.MovementDate = broughtin
        m.MovementType = mt
        a.ActiveMovementType = m.MovementType
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementID = m.ID
        a.Archived = 1
    elif d["Status"] == "Passed Away":
        a.DeceasedDate = broughtin
        a.PutToSleep = 0
        a.PTSReasonID = 2 # Died
        a.Archived = 1
    elif d["Status"] == "Euthanized":
        a.DeceasedDate = broughtin
        a.PutToSleep = 1
        a.PTSReasonID = 4 # Sick
        a.Archived = 1

    # Now do the dbfs and media inserts for a photo if one is available
    pic1 = d["Picture 1"]
    if pic1.rfind("/") != -1: pic1 = pic1[pic1.rfind("/")+1:]
    imdata = asm.load_image_from_file("%s/%s" % (PATH, pic1))
    asm.animal_image(a.ID, imdata)
    if a.Archived == 0 and imdata is None and pfpage != "":
        asm.petfinder_image(pfpage, a.ID, a.AnimalName)

if os.path.exists("%s/Contacts.csv" % PATH):
    for d in asm.csv_to_list("%s/Contacts.csv" % PATH):
        # Each row contains a person
        o = asm.Owner()
        owners.append(o)
        o.OwnerForeNames = d["First Name"]
        o.OwnerSurname = d["Last Name"]
        o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
        o.OwnerAddress = d["Address"]
        #o.OwnerTown = d["City"]
        #o.OwnerCounty = d["State"]
        #o.OwnerPostcode = d["Zipcode"]
        o.EmailAddress = d["Email"]
        o.HomeTelephone = d["Phone (Home)"]
        o.MobileTelephone = d["Phone (Cell)"]
        o.Comments = d["Comment"]

# Now that everything else is done, output stored records
for a in animals:
    print a
for o in owners:
    print o
for m in movements:
    print m

asm.stderr_summary(animals=animals, owners=owners, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

