#!/usr/bin/python

import asm, os

"""
Import module to read from rescuegroups CSV export
"""

PATH = "data/zb1564_rescuegroups"

#DEFAULT_BREED = 261 # default to dsh
DEFAULT_BREED = 30 # default to black lab

animals = []
owners = []
movements = []

asm.setid("animal", 100)
asm.setid("owner", 100)
asm.setid("media", 100)
asm.setid("dbfs", 300)

def getdate(s):
    return asm.getdate_mmddyyyy(s)

def size_id_for_name(name):
    return {
        "L": 1,
        "S": 2,
        "M": 3, 
        "XL": 0
    }[name.upper().strip()]

uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = "Unknown Owner"
uo.Comments = "Catchall for adopted animal data from PetFinder"

for d in asm.csv_to_list("%s/pets.csv" % PATH):
    a = asm.Animal()
    animals.append(a)
    if d["Type"] == "Cat":
        animaltype = 11
        animalletter = "U"
    else:
        animaltype = 2
        animalletter = "D"
    a.AnimalTypeID = animaltype
    a.SpeciesID = asm.species_id_for_name(d["Type"])
    a.ShelterCode = "RG%s" % d["ID"]
    a.ShortCode = a.ShelterCode
    a.AnimalName = d["AnimalName"]
    broughtin = asm.subtract_days(asm.today(), 365)
    a.DateBroughtIn = broughtin
    dob = asm.today()
    if d["Age"].find("Baby") != -1:
        dob = asm.subtract_days(asm.today(), 91)
    elif d["Age"].find("Young") != -1:
        dob = asm.subtract_days(asm.today(), 182)
    elif d["Age"].find("Adult") != -1:
        dob = asm.subtract_days(asm.today(), 730)
    elif d["Age"].find("Senior") != -1:
        dob = asm.subtract_days(asm.today(), 2555)
    a.DateOfBirth = dob
    a.EstimatedDOB = 1
    a.Sex = 1
    if d["Sex"] == "F":
        a.Sex = 0
    a.BreedID = asm.breed_id_for_name(d["PrimaryBreed"], DEFAULT_BREED)
    if not d["Mix"] == "M":
        a.Breed2ID = a.BreedID
        a.BreedName = asm.breed_name_for_id(a.BreedID)
        a.CrossBreed = 0
    else:
        a.Breed2ID = asm.breed_id_for_name(d["SecondaryBreed"], DEFAULT_BREED)
        a.BreedName = asm.breed_name_for_id(a.BreedID) + " / " + asm.breed_name_for_id(a.Breed2ID)
        a.CrossBreed = 1
    a.BaseColourID = 1
    a.ShelterLocation = 1
    a.Size = size_id_for_name(d["Size"])
    a.Declawed = d["Declawed"] == "1" and 1 or 0
    a.HasSpecialNeeds = d["specialNeeds"] == "1" and 1 or 0
    a.EntryReasonID = 1
    a.Neutered = d["Altered"] == "1" and 1 or 0
    if d["Housetrained"] == "1": a.IsHouseTrained = 0
    if d["NoDogs"] == "1": a.IsGoodWithDogs = 1
    if d["NoKids"] == "1": a.IsGoodWithChildren = 1
    if d["NoCats"] == "1": a.IsGoodWithCats = 1
    a.AnimalComments = d["Desc"]
    a.HiddenAnimalDetails = "original breed: " + d["PrimaryBreed"] + " " + d["SecondaryBreed"] + ", shots: " + d["Shots"] + ", status: " + d["Status"] + ", internal: " + d["Internal"]
    # Now do the dbfs and media inserts for a photo if one is available
    photos = os.listdir(PATH)
    imdata = None
    for x in photos:
        if x.startswith(d["ID"]):
            f = open("%s/%s" % (PATH, x), "rb")
            imdata = f.read()
            f.close()
    if imdata is not None:
        asm.animal_image(a.ID, imdata)
    # If the animal is adopted, send it to our unknown owner
    if d["Status"] == "X":
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = uo.ID
        m.AnimalID = a.ID
        m.MovementDate = broughtin
        m.MovementType = 1
        a.ActiveMovementType = m.MovementType
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementID = m.ID
        a.Archived = 1
    print a

# Now follow each link to get the animal details page and extract info
print "\\set ON_ERROR_STOP\nBEGIN;"

# Now that everything else is done, output stored records
for k,v in asm.locations.iteritems():
    print v
for a in animals:
    print a
for o in owners:
    print o
for m in movements:
    print m

asm.stderr_summary(animals=animals, owners=owners, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

