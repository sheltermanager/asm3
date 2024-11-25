#!/usr/bin/python

import asm, os

"""
Import script for RescueConnection file exports. RC give people a zip file containing .xls files of the data.

Run this script to convert:

#!/bin/sh
for i in *.xls; do ssconvert $i $i.csv; done

27th January, 2020
"""

START_ID = 200

PATH = "/home/robin/tmp/asm3_import_data/rc_li2142"

PICTURE_IMPORT = False
PICTURES = f"{PATH}/photos/final"

def getdate(d, noblanks=False):
    rv = asm.getdate_guess(d)
    if noblanks and rv is None: rv = asm.now()
    return rv

# --- START OF CONVERSION ---

owners = []
movements = []
animals = []

asm.setid("animal", START_ID)
asm.setid("owner", START_ID)
asm.setid("adoption", START_ID)
if PICTURE_IMPORT: asm.setid("media", START_ID)
if PICTURE_IMPORT: asm.setid("dbfs", START_ID)

print("\\set ON_ERROR_STOP\nBEGIN;")
print(f"DELETE FROM animal WHERE ID >= {START_ID} AND CreatedBy = 'conversion';")
print(f"DELETE FROM owner WHERE ID >= {START_ID} AND CreatedBy = 'conversion';")
print(f"DELETE FROM adoption WHERE ID >= {START_ID} AND CreatedBy = 'conversion';")
if PICTURE_IMPORT: print(f"DELETE FROM media WHERE ID >= {START_ID};")
if PICTURE_IMPORT: print(f"DELETE FROM dbfs WHERE ID >= {START_ID};")

# Create an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname

# People
for d in asm.csv_to_list(f"{PATH}/People.xls.csv", strip=True, remove_non_ascii=True):
    pass

# Animals
for d in asm.csv_to_list(f"{PATH}/Animals.xls.csv", strip=True, remove_non_ascii=True):
    a = asm.Animal()
    animals.append(a)
    if d["Species"] == "Cat":
        a.AnimalTypeID = 11 # Unwanted Cat
        if d["Entry Category"] == "Stray":
            a.AnimalTypeID = 12 # Stray Cat
    elif d["Species"] == "Dog":
        a.AnimalTypeID = 2 # Unwanted Dog
        if d["Entry Category"] == "Stray":
            a.AnimalTypeID = 10 # Stray Dog
    else:
        a.AnimalTypeID = 40 # Misc
    a.SpeciesID = asm.species_id_for_name(d["Species"])
    a.AnimalName = d["Animal name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.ShelterCode = d["ID number"].strip()
    a.ShortCode = a.ShelterCode
    a.IdentichipNumber = d["Microchip"].strip()
    if a.IdentichipNumber != "": a.Identichipped = 1
    a.Sex = asm.getsex_mf(d["Gender"])
    asm.breed_ids(a, d["Breeds"], d["CrossBreed"])
    a.Neutered = d["Altered"] == "Yes" and 1 or 0
    a.BaseColourID = asm.colour_id_for_name(d["Color"])
    a.Size = 2 
    if d["Size"] == "L": a.Size = 1
    if d["Size"] == "XL": a.Size = 0
    if d["Size"] == "S": a.Size = 3
    a.Weight = asm.cfloat(d["Weight"])
    a.Declawed = d["Declawed"] == "Yes" and 1 or 0
    a.HouseTrained = d["Housetrained"] == "Yes" and 2 or 1
    a.HasSpecialNeeds = d["Special needs"] == "Yes" and 1 or 0
    a.GoodWithChildren = d["Needs home without small children"] == "Yes" and 1 or 0
    a.GoodWithCats = d["Needs home without cats"] == "Yes" and 1 or 0
    a.GoodWithDogs = d["Needs home without dogs"] == "Yes" and 1 or 0

    a.HealthProblems = d["Known issues"]
    ec = d["Entry Category"].strip().lower()
    if ec.startswith("stray"):
        a.EntryReasonID = 7
        a.EntryTypeID = 2
    elif ec.startswith("surrender"):
        a.EntryReasonID = 17
        a.EntryTypeID = 1
    elif ec.startswith("born"):
        a.EntryReasonID = 13
        a.EntryTypeID = 5
    elif ec.startswith("transfer"):
        a.EntryReasonID = 15
        a.EntryTypeID = 3
        a.TransferIn = 1
    a.ReasonForEntry = d["Source/origin"]
    a.AnimalComments = d["Full description"]

    a.DateBroughtIn = getdate(d["Arrival"]) or asm.today()
    a.DateOfBirth = getdate(d["Date of birth"])
    if a.DateOfBirth is None:
        a.DateOfBirth = asm.subtract_days(a.DateBroughtIn, 365)
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn

    hcomments = d["Internal notes"]
    hcomments = "\nEntry category: " + d["Entry Category"]
    hcomments += "\nBreed: " + d["Breeds"] + "/" + d["CrossBreed"]
    hcomments += "\nColor: " + d["Color"]
    hcomments += "\nDisposition: " + d["Disposition"]
    a.HiddenAnimalDetails = hcomments

    dd = getdate(d["Disposition date"])
    di = d["Disposition"].strip()
    if di.startswith("Adopted"):
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = uo.ID
        m.MovementType = 1
        m.MovementDate = dd
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = m.MovementType
        a.LastChangedDate = dd
        movements.append(m)
    elif di.startswith("Released") or di.startswith("Returned to owner"):
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = uo.ID
        m.MovementType = 5
        m.MovementDate = dd
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = m.MovementType
        a.LastChangedDate = dd
        movements.append(m)
    elif di.startswith("Moved/transferred"):
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = uo.ID
        m.MovementType = 3
        m.MovementDate = dd
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = m.MovementType
        a.LastChangedDate = dd
        movements.append(m)
    elif di.startswith("Died"):
        a.PutToSleep = 0
        a.PTSReasonID = 2
        a.DeceasedDate = dd
        a.Archived = 1
    elif di.startswith("Euthanized"):
        a.PutToSleep = 1
        a.PTSReasonID = 2
        a.DeceasedDate = dd
        a.Archived = 1

    # Does this animal have an image? If so, add media/dbfs entries for it
    if PICTURE_IMPORT:
        imdata = None
        for i in range(0, 3):
            fname = "%s/%s-%s.jpg" % (PICTURES, a.ShelterCode, i)
            if os.path.exists(fname):
                with open(fname, "rb") as f:
                    asm.animal_image(a.ID, f.read())


# Run back through the animals, if we have any that are still
# on shelter after 1 year, add an adoption to an unknown owner
# asm.adopt_older_than(animals, movements, uo.ID, 365)

# Now that everything else is done, output stored records
for a in animals:
    print(a)
for o in owners:
    print(o)
for m in movements:
    print(m)

#asm.stderr_allanimals(animals)
#asm.stderr_onshelter(animals)
asm.stderr_summary(animals=animals, owners=owners, movements=movements)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")
