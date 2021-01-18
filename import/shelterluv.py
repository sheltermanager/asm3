#!/usr/bin/python

import asm, os

"""
Import module to read from ShelterLuv CSV export.

The following files are needed:

    Entities - Animals -> animals.csv
    Entities - Persons -> people.csv
    Events - Intake    -> intake.csv
    Events - Outcome   -> outcome.csv

"""

PATH = "/home/robin/tmp/asm3_import_data/sluv_gd2427"

DEFAULT_BREED = 261 # default to dsh
DATE_FORMAT = "MDY" # Normally MDY
START_ID = 100

animals = []
owners = []
movements = []

ppa = {}
ppo = {}

asm.setid("adoption", START_ID)
asm.setid("animal", START_ID)
asm.setid("owner", START_ID)

def getdate(s):
    if DATE_FORMAT == "DMY":
        return asm.getdate_ddmmyyyy(s)
    else:
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

print("\\set ON_ERROR_STOP\nBEGIN;")
print("DELETE FROM adoption WHERE ID >= %s;" % START_ID)
print("DELETE FROM animal WHERE ID >= %s;" % START_ID)
print("DELETE FROM owner WHERE ID >= %s;" % START_ID)
print("DELETE FROM ownerdonation WHERE ID >= %s;" % START_ID)

for d in asm.csv_to_list("%s/animals.csv" % PATH):
    if d["Animal ID"] == "Animal ID": continue # skip repeated header rows
    if d["Animal ID"] in ppa: continue # skip repeated rows
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
    a.ShortCode = d["Animal ID"]
    a.ShelterCode = d["Animal ID"]
    ppa[d["Animal ID"]] = a
    a.AnimalName = d["Name"]
    a.DateBroughtIn = getdate(d["Created Date"])
    dob = a.DateBroughtIn
    a.EstimatedDOB = 1
    # Ages are stored as 2Y/ 4M/ 26D
    age = d["Age (Y/M/D)"]
    for b in age.split("/"):
        b = b.strip();
        if b.endswith("Y"): dob = asm.subtract_days(dob, 365 * asm.atoi(b))
        if b.endswith("M"): dob = asm.subtract_days(dob, 30 * asm.atoi(b))
        if b.endswith("D"): dob = asm.subtract_days(dob, asm.atoi(b))
    a.DateOfBirth = dob
    a.Sex = 1
    if d["Sex"].startswith("F"):
        a.Sex = 0
    asm.breed_ids(a, d["Primary Breed"], d["Secondary Breed"], DEFAULT_BREED)
    a.BaseColourID = asm.colour_id_for_name(d["Primary Color"])
    a.HiddenAnimalDetails = "Age: %s, Breed: %s / %s, Color: %s" % (age, d["Primary Breed"], d["Secondary Breed"], d["Primary Color"])
    a.ShelterLocation = 1
    if d["Altered in Care"].startswith("Altered"):
        a.Neutered = 1
        a.NeuteredDate = a.DateBroughtIn
    if d["Altered before arrival"] == "Yes":
        a.Neutered = 1
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn

for d in asm.csv_to_list("%s/people.csv" % PATH):
    if d["Name"] == "Name": continue # skip repeated header rows
    if d["Name"] in ppo: continue # skip repeated rows
    # Each row contains a person
    o = asm.Owner()
    owners.append(o)
    ppo[d["Name"]] = o
    # ppo[d["Person ID"]] = o
    o.SplitName(d["Name"])
    o.OwnerAddress = d["Street"]
    o.OwnerTown = d["City"]
    o.OwnerCounty = d["State"]
    #o.OwnerPostcode = d["Zipcode"]
    o.EmailAddress = d["Primary Email"]
    o.HomeTelephone = d["Phone"]

for d in asm.csv_to_list("%s/outcomes.csv" % PATH):
    if d["Animal ID"] == "Animal ID": continue # skip repeated headers
    o = None
    if d["Assoc. Person Name"] in ppo: o = ppo[d["Assoc. Person Name"]]
    a = None
    if d["Animal ID"] in ppa: a = ppa[d["Animal ID"]]
    if o is None or a is None: continue
    # Add some other values that weren't present in the animal file
    a.IdentichipNumber = d["Microchip Number"]
    if a.IdentichipNumber != "": a.Identichipped = 1
    if d["Outcome Type"] == "Adoption":
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = getdate(d["Outcome Date"])
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 1
        a.CreatedDate = m.MovementDate
        a.CreatedBy = "conversion/%s" % d["Outcome By"]
        a.LastChangedDate = m.MovementDate
        movements.append(m)
    elif d["Outcome Type"] == "Euthanized": # Not seen in data we've actually had
        a.DeceasedDate = getdate(d["Outcome Date"])
        a.PutToSleep = 1
        a.PTSReasonID = 4 # Sick
        a.Archived = 1

for d in asm.csv_to_list("%s/intake.csv" % PATH):
    if d["AnimalCode"] == "AnimalCode": continue
    a = ppa[d["AnimalCode"]]
    if a is not None:
        if d["AnimalIntakeType"] == "Transfer In":
            a.IsTransfer = 1
            a.EntryReasonID = 15
        elif d["AnimalIntakeType"] == "Stray":
            a.EntryReasonID = 7
        elif d["AnimalIntakeType"] == "Return":
            a.EntryReasonID = 17 # Surrender
        else:
            a.EntryReasonID = 17 # Surrender
        a.ReasonForEntry = "%s / %s" % ( d["AnimalIntakeType"], d["AnimalIntakeSub-Type"] )

# Allow shelter animals to have their chips registered
for a in animals:
    if a.Archived == 0:
        a.IsNotForRegistration = 0

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

