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


I think if people haven't paid for their "Data Management Service" they aren't allowed to
run any reports. This export will also work with CSVs extracted from Animals->Animal List,
change the View to Export and then hit Export as CSV.

"""

PATH = "/home/robin/tmp/asm3_import_data/rg_tn2023"

DEFAULT_BREED = 261 # default to dsh
PETFINDER_ID = "" # Shouldn't be needed if Picture 1 is present

RG_AWS_PREFIX = "https://s3.amazonaws.com/filestore.rescuegroups.org" # To resolve URLs from the "Picture 1" field of imports

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
    if "Animal ID" in d:
        a.ShelterCode = "RG%s" % d["Animal ID"]
        a.ShortCode = a.ShelterCode
    else:
        a.generateCode()
    a.AnimalName = d["Name"]

    broughtin = asm.today()
    if "Created" in d:
        broughtin = getdate(d["Created"])
    a.DateBroughtIn = broughtin

    dob = broughtin
    a.EstimatedDOB = 1
    if "General Age" in d:
        if d["General Age"].find("Baby") != -1:
            dob = asm.subtract_days(asm.today(), 91)
        elif d["General Age"].find("Young") != -1:
            dob = asm.subtract_days(asm.today(), 182)
        elif d["General Age"].find("Adult") != -1:
            dob = asm.subtract_days(asm.today(), 730)
        elif d["General Age"].find("Senior") != -1:
            dob = asm.subtract_days(asm.today(), 2555)
    if "Birthdate" in d and d["Birthdate"] != "":
        dob = asm.getdate_mmddyyyy(d["Birthdate"])
        a.EstimatedDOB = 0
    a.DateOfBirth = dob
    a.Sex = 1
    if d["Sex"].startswith("F"):
        a.Sex = 0
    
    breed1 = ""
    breed2 = ""
    mixed = "No"
    if "Primary Breed" in d:
        breed1 = d["Primary Breed"]
        breed2 = d["Secondary Breed"]
        mixed = d["Mixed"]
    elif "Breed" in d:
        # Breed is in form breed1 / breed2 / mixed, sections only present if set
        breed2 = ""
        bb = d["Breed"].split("/")
        breed1 = bb[0]
        if len(bb) > 1: breed2 = bb[1]
        if len(bb) > 2: mixed = "Yes"
        
    a.BreedID = asm.breed_id_for_name(breed1, DEFAULT_BREED)
    if not mixed == "Yes":
        a.Breed2ID = a.BreedID
        a.BreedName = asm.breed_name_for_id(a.BreedID)
        a.CrossBreed = 0
    else:
        a.Breed2ID = a.BreedID
        if breed2 != "":
            a.Breed2ID = asm.breed_id_for_name(breed2, DEFAULT_BREED)
        a.BreedName = asm.breed_name_for_id(a.BreedID) + " / " + asm.breed_name_for_id(a.Breed2ID)
        a.CrossBreed = 1
    a.BaseColourID = asm.colour_id_for_name(d["Color (General)"])
    a.ShelterLocation = 1
    if "Size Potential (General)" in d: a.Size = size_id_for_name(d["Size Potential (General)"])
    if "Declawed" in d: a.Declawed = d["Declawed"] == "Yes" and 1 or 0
    if "Special Needs" in d: a.HasSpecialNeeds = d["Special Needs"] == "Yes" and 1 or 0
    a.EntryReasonID = 1
    if "Altered" in d: a.Neutered = d["Altered"] == "Yes" and 1 or 0
    if "Housetrained" in d and d["Housetrained"] == "Yes": a.IsHouseTrained = 0
    if "OK with Dogs" in d and d["OK with Dogs"] == "Yes": a.IsGoodWithDogs = 0
    if "OK with Kids" in d and d["OK with Kids"] == "Yes": a.IsGoodWithChildren = 0
    if "OK with Cats" in d and d["OK with Cats"] == "Yes": a.IsGoodWithCats = 0
    if "Microchip Number" in d: a.IdentichipNumber = d["Microchip Number"]
    if a.IdentichipNumber != "": a.Identichipped = 1
    if "Description" in d: a.AnimalComments = d["Description"]
    if "Description (no html)" in d: a.AnimalComments = d["Description (no html)"]
    summary = ""
    if "Summary" in d: summary = d["Summary"]
    a.HiddenAnimalDetails = summary + ", original breed: " + breed1 + " " + breed2 + ", color: " + \
        d["Color (General)"] + ", status: " + d["Status"]
    if "Internal ID" in d and "Location" in d: a.HiddenAnimalDetails += ", internal: " + d["Internal ID"] + ", location: " + d["Location"]
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
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
    if "Picture 1" in d and d["Picture 1"] != "":
        pic1 = d["Picture 1"]
        picurl = "%s/%s" % (RG_AWS_PREFIX, pic1)
        # Check for locally saved photo first
        if pic1.rfind("/") != -1: pic1 = pic1[pic1.rfind("/")+1:]
        imdata = asm.load_image_from_file("%s/%s" % (PATH, pic1))
        if imdata is not None:
            asm.animal_image(a.ID, imdata)
        # Try online
        imdata = asm.load_image_from_url(picurl)
        if imdata is not None:
            asm.animal_image(a.ID, imdata)
        # Try PetFinder
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

