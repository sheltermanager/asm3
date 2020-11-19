#!/usr/bin/python

import asm

"""
Import script for custom Excel for zb1415

28th June, 2017
"""

FILENAME = "data/zb1415.csv"

def getdate(d):
    return asm.getdate_ddmmyyyy(d)

# --- START OF CONVERSION ---

owners = []
movements = []
animals = []

asm.setid("animal", 100)
asm.setid("owner", 100)
asm.setid("adoption", 100)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM owner WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM adoption WHERE ID >= 100 AND CreatedBy = 'conversion';"

# Each row contains an adoption with animal and owner info
for d in asm.csv_to_list(FILENAME):
    o = asm.Owner()
    owners.append(o)
    o.OwnerTitle = d["Title"]
    o.OwnerInitials = d["Initials"]
    o.OwnerForeNames = d["First Name(s)"]
    o.OwnerSurname = d["Last Name"]
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = d["Address"]
    o.OwnerTown = d["City"]
    o.OwnerCounty = d["State"]
    o.OwnerPostcode = d["Zip Code"]
    o.EmailAddress = d["Email Address"]
    o.HomeTelephone = d["Home Phone"]

    a = asm.Animal()
    animals.append(a)
    a.AnimalTypeID = 11
    a.SpeciesID = 2
    a.AnimalName = d["Cat Name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateBroughtIn = getdate(d["Movement/Adoption Date"])
    if a.DateBroughtIn is None:
        a.DateBroughtIn = asm.today()
    a.DateOfBirth = getdate(d["Cat Date of Birth"])
    if a.DateOfBirth is None:
        a.DateOfBirth = asm.subtract_days(a.DateBroughtIn, 365)
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    a.generateCode()
    a.IsNotAvailableForAdoption = 0
    a.Size = 2
    a.EntryReasonID = 17 # Surrender
    a.IsGoodWithCats = 2
    a.IsGoodWithDogs = 2
    a.IsGoodWithChildren = 2
    a.HouseTrained = 0
    a.Archived = 1
    a.BreedID = 261
    a.Breed2ID = a.BreedID
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    a.CrossBreed = 0

    m = asm.Movement()
    m.AnimalID = a.ID
    m.OwnerID = o.ID
    m.MovementType = 1
    m.MovementDate = a.DateBroughtIn
    m.Comments = "Location of Movement: %s" % d["Location of Movement (adoption)"]
    a.Archived = 1
    a.ActiveMovementID = m.ID
    a.ActiveMovementType = 1
    movements.append(m)


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

