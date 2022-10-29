#!/usr/bin/env python3

import sys
sys.path.append("..")
import asm, os

"""
Custom access import for al2858

30th Sep, 2022
"""

PATH = "/home/robin/tmp/asm3_import_data/al2858.csv"

DEFAULT_BREED = 261 # default to dsh
DATE_FORMAT = "MDY" # Normally MDY
START_ID = 100

animals = []
owners = []
movements = []

ppo = {}

asm.setid("adoption", START_ID)
asm.setid("animal", START_ID)
asm.setid("owner", START_ID)

uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = "Unknown Owner"
uo.Comments = "Catchall for adopted animal data"

ur = asm.Owner()
owners.append(ur)
ur.OwnerSurname = "Unknown Rescue"
ur.OwnerName = "Unknown Rescue"
ur.OwnerType = 2
ur.Comments = "Catchall for transferred animal data"

print("\\set ON_ERROR_STOP\nBEGIN;")
print("DELETE FROM adoption WHERE ID >= %s;" % START_ID)
print("DELETE FROM animal WHERE ID >= %s;" % START_ID)
print("DELETE FROM owner WHERE ID >= %s;" % START_ID)

for d in asm.csv_to_list(PATH):
    if d["Database"] == "Database": continue # skip repeated header rows
    if d["Date In"] == "": continue # skip blank rows
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
    a.generateCode()
    a.AnimalName = d["Database"]
    a.DateBroughtIn = asm.getdate_mmddyy(d["Date In"])
    a.DateOfBirth = a.DateBroughtIn
    a.EstimatedDOB = 1
    a.Sex = 1
    if d["Sex"].startswith("F"):
        a.Sex = 0
    if d["Neutered / Spayed"] != "":
        a.Neutered = 1
    if d["Stray / Surrendered"] == "Stray":
        a.EntryReasonID = 7
    else:
        a.EntryReasonID = 17 

    hc = "Breed: " + d["Breed/Type"]
    hc += "\nColor: " + d["Color"]
    hc += "\nCage: " + d["Cage #"]
    hc += "\nStaff ID: " + d["Staff ID"]
    hc += "\nIntake: " + d["Stray / Surrendered"] + " " + d["Quarantined /Seized"]
    hc += "\nCollar: " + d["Collar"]
    hc += "\nID Type: " + d["ID# / Type"]
    hc += "\nOwner: " + d["Owner"]
    hc += "\nContacted By: " + d["Contacted By"] + " " + d["Contact Date"]
    outcome = d["Euthanized/Adopted/Reclaimed/Rescued"]
    hc += "\nOutcome: " + outcome
    asm.breed_ids(a, d["Breed/Type"], "", DEFAULT_BREED)
    a.BaseColourID = asm.colour_id_for_name(d["Color"])
    a.ReasonForEntry = d["Area Found"]
    a.AnimalComments = d["Information"]
    a.HiddenAnimalDetails = hc
    a.HealthProblems = d["Medical"]
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn

    # handle the person full name/phone
    o = None
    if d["Full Name"] != "":
        if d["Full Name"] in ppo:
            o = ppo[d["Full Name"]]
        else:
            o = asm.Owner()
            owners.append(o)
            ppo[d["Full Name"]] = o
            o.SplitName(d["Full Name"])
            o.HomeTelephone = d["Phone Number"]

    if outcome == "Adoption":
        if o is None: o = uo
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = a.DateBroughtIn
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 1
        a.CreatedDate = m.MovementDate
        a.LastChangedDate = m.MovementDate
        movements.append(m)
    elif outcome == "Rescued":
        if o is None: o = ur
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 3
        m.MovementDate = a.DateBroughtIn
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 3
        a.CreatedDate = m.MovementDate
        a.LastChangedDate = m.MovementDate
        movements.append(m)
    elif outcome == "Reclaimed":
        if o is None: o = uo
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 5
        m.MovementDate = a.DateBroughtIn
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 5
        a.CreatedDate = m.MovementDate
        a.LastChangedDate = m.MovementDate
        movements.append(m)
    elif outcome == "Euthanized":
        a.DeceasedDate = a.DateBroughtIn
        a.PutToSleep = 1
        a.PTSReasonID = 4 # Sick
        a.Archived = 1

asm.adopt_older_than(animals, movements, uo.ID, 0)

# Now that everything else is done, output stored records
for a in animals:
    print (a)
for o in owners:
    print (o)
for m in movements:
    print (m)

asm.stderr_summary(animals=animals, owners=owners, movements=movements)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")
