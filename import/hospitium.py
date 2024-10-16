#!/usr/bin/python

import asm

"""
Import script for Hospitium databases exported as CSV
produces animals.csv, adoption_contacts.csv, relinquishment_contacts.csv

9th March, 2018
"""

PATH = "/home/robin/tmp/asm3_import_data/hospitium_hs1402"
START_ID = 500

def getdate(d):
    return asm.getdate_guess(d)

# --- START OF CONVERSION ---

owners = []
movements = []
animals = []
ppa = {}
ppo = {}

asm.setid("animal", START_ID)
asm.setid("owner", START_ID)
asm.setid("adoption", START_ID)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM owner WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM adoption WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID

# Create an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname

for d in asm.csv_to_list("%s/animals.csv" % PATH):
    a = asm.Animal()
    animals.append(a)
    ppa[d["ID"]] = a
    if d["Species"] == "Cat":
        a.AnimalTypeID = 11 # Unwanted Cat
    elif d["Species"] == "Dog":
        a.AnimalTypeID = 2 # Unwanted Dog
    else:
        a.AnimalTypeID = 40 # Misc
    a.SpeciesID = asm.species_id_for_name(d["Species"])
    a.AnimalName = d["Name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateBroughtIn = getdate(d["Date of Well Check"]) or getdate(d["Adopted Date"]) or getdate(d["Birthday"]) or asm.today()
    a.DateOfBirth = getdate(d["Birthday"]) or a.DateBroughtIn
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    a.ShelterCode = d["ID"][d["ID"].rfind("-")+1:]
    a.ShortCode = a.ShelterCode
    a.BaseColourID = asm.colour_id_for_name(d["Animal Color"])
    a.IsNotAvailableForAdoption = 0
    a.Sex = asm.getsex_mf(d["Sex"])
    a.Size = 2
    a.Neutered = asm.iif(d["Spay / Neuter"] == "Yes", 1, 0)
    a.EntryReasonID = 17 # Surrender
    a.Archived = 0
    a.HiddenAnimalDetails = "Color: %s\nPrevious Name: %s\nBiter: %s\nDiet: %s\n%s" % (d["Animal Color"], d["Previous Name"], d["Biter"], d["Diet"], d["Special Needs"])
    a.SourceAdoptedDate = getdate(d["Adopted Date"])

    if d["Deceased Date"] != "":
        a.PutToSleep = 0
        a.DeceasedDate = getdate(d["Deceased Date"])
        a.Archived = 1
        a.PTSReason = d["Deceased Reason"]

for d in asm.csv_to_list("%s/relinquishment_contacts.csv" % PATH):
    o = asm.Owner()
    owners.append(o)
    ppo[d["ID"]] = o
    o.OwnerForeNames = d["First Name"]
    o.OwnerSurname = d["Last Name"]
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = d["Address"]
    o.HomeTelephone = d["Phone"]
    o.EmailAddress = d["Email"]
    for aid in d["Relinquished Animal IDs"].split(","):
        if aid != "":
            a = ppa[aid]
            a.ReasonForEntry = d["Reason"]
            a.OriginalOwnerID = o.ID
            a.BroughtInByOwnerID = o.ID

for d in asm.csv_to_list("%s/adoption_contacts.csv" % PATH):
    o = asm.Owner()
    owners.append(o)
    ppo[d["ID"]] = o
    o.OwnerForeNames = d["First Name"]
    o.OwnerSurname = d["Last Name"]
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = d["Address"]
    o.HomeTelephone = d["Phone"]
    o.EmailAddress = d["Email"]
    for aid in d["Adopted Animal IDs"].split(","):
        if aid != "":
            a = ppa[aid]
            m = asm.Movement()
            m.AnimalID = a.ID
            m.OwnerID = o.ID
            m.MovementType = 1
            m.MovementDate = a.SourceAdoptedDate
            a.Archived = 1
            a.ActiveMovementDate = m.MovementDate
            a.ActiveMovementID = m.ID
            a.ActiveMovementType = 1
            a.LastChangedDate = m.MovementDate
            movements.append(m)

# Run back through the animals, if we have any with an adopted date
# but they weren't in the adopted_contacts, adopt them to the unknown owner
for a in animals:
    if a.SourceAdoptedDate is not None and a.ActiveMovementDate is None:
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = uo.ID
        m.MovementType = 1
        m.MovementDate = a.SourceAdoptedDate
        a.Archived = 1
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 1
        a.LastChangedDate = m.MovementDate
        movements.append(m)

# Catch all for remaining animals, adopt everyone still on shelter
asm.adopt_older_than(animals, movements, uo.ID, 0)

# Now that everything else is done, output stored records
for a in animals:
    print a
for o in owners:
    print o
for m in movements:
    print m

#asm.stderr_allanimals(animals)
#asm.stderr_onshelter(animals)
asm.stderr_summary(animals=animals, owners=owners, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

