#!/usr/bin/python

import asm, os

"""
Import script for ShelterBuddy exports of 
Report15 (animals.csv)
Report18 (vacc.csv)
17th Jan 2018
"""

PATH = "/home/robin/tmp/asm3_import_data/shelterbuddy_zw1610/"

def getdate(s):
    return asm.getdate_yyyymmdd(s)

# --- START OF CONVERSION ---
print "\\set ON_ERROR_STOP\nBEGIN;"

owners = []
ppo = {}
ppa = {}
movements = []
animals = []
animalmedicals = []
animalvaccinations = []

asm.setid("animal", 100)
asm.setid("owner", 100)
asm.setid("adoption", 100)
asm.setid("animalmedical", 100)
asm.setid("animalmedicaltreatment", 100)
asm.setid("animalvaccination", 100)

print "DELETE FROM animal WHERE ID >= 100;"
print "DELETE FROM animalmedical WHERE ID >= 100;"
print "DELETE FROM animalmedicaltreatment WHERE ID >= 100;"
print "DELETE FROM animalvaccination WHERE ID >= 100;"
print "DELETE FROM owner WHERE ID >= 100;"
print "DELETE FROM adoption WHERE ID >= 100;"

canimals = asm.csv_to_list(PATH + "animals.csv")
cvacc = asm.csv_to_list(PATH + "vacc.csv")

for row in canimals:
    a = asm.Animal()
    animals.append(a)
    ppa[row["Animal ID"]] = a
    a.AnimalName = row["Name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    typecol = row["Type"]
    breedcol = row["Breed"]
    breed2col = row["Secondary Breed"]
    a.AnimalTypeID = asm.type_id_for_name(typecol)
    a.generateCode(asm.type_name_for_id(a.AnimalTypeID))
    a.SpeciesID = asm.species_id_for_name(typecol)
    asm.breed_ids(a, breedcol, breed2col)
    a.DateBroughtIn = getdate(row["Incoming Date"])
    a.DateOfBirth = getdate(row["DOB"])
    if a.DateOfBirth is None: a.DateOfBirth = a.DateBroughtIn
    a.Neutered = row["Spay/Neutered"].strip().lower() == "yes" and 1 or 0
    a.NeuteredDate = getdate(row["Spay/Neutered Date"])
    a.IdentichipNumber = row["Microchip"]
    if a.IdentichipNumber != "": a.Identichipped = 1
    a.Sex = asm.getsex_mf(row["Gender"])
    a.BaseColourID = asm.colour_id_for_names(row["Color"], row["Second Color"])
    a.ReasonForEntry = row["Surrender Reason"]
    a.EntryReasonID = 11
    if row["Source (Current)"] == "Stray":
        a.EntryReasonID = 7
        a.EntryTypeID = 2
    comments = "Original Type: " + typecol
    comments += "\nOriginal Breed: " + breedcol + "/" + breed2col
    comments += "\nOriginal Colour: " + row["Color"] + "/" + row["Second Color"]
    comments += "\nSource: " + row["Source (Current)"]
    comments += "\nStatus: " + row["Status (Current)"]
    a.HiddenAnimalDetails = comments
    a.Markings = row["Distinguishing Features"]
    a.PTSReason = row["Euthanasia Reason"]
    a.AnimalComments = row["General Notes from animal details screen"]
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn

    o = None
    if row["Person ID"] != "":
        if row["Person ID"] in ppo:
            o = ppo[row["Person ID"]]
        else:
            o = asm.Owner()
            owners.append(o)
            ppo[row["Person ID"]] = o
            o.OwnerForeNames = row["Person First Name"]
            o.OwnerSurname = row["Person Last Name"]
            o.OwnerAddress = row["Mailing Address"]
            o.OwnerTown = row["Mailing Suburb"]
            o.OwnerPostcode = row["Mailing Post Code"]
            o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname

    if row["Status (Current)"].startswith("Adopted") and o:
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = o.ID
        m.AnimalID = a.ID
        m.MovementDate = a.DateBroughtIn
        m.MovementType = 1
        a.Archived = 1
        a.ActiveMovementType = 1
        a.ActiveMovementID = m.ID
    elif row["Status (Current)"] == "Deceased" or row["Status (Current)"].startswith("Unassisted Death"):
        a.DeceasedDate = a.DateBroughtIn
        a.Archived = 1
    elif row["Status (Current)"].startswith("Euthanized"):
        a.DeceasedDate = a.DateBroughtIn
        a.PutToSleep = 1
        a.Archived = 1
    elif row["Status (Current)"].startswith("Released by Agency"):
        pass
    elif row["Status (Current)"] == "Reclaimed" and o:
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = o.ID
        m.AnimalID = a.ID
        m.MovementDate = a.DateBroughtIn
        m.MovementType = 5
        a.Archived = 1
        a.ActiveMovementType = 5
        a.ActiveMovementID = m.ID
    elif row["Status (Current)"] == "Transfer Out" and o:
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = o.ID
        m.AnimalID = a.ID
        m.MovementDate = a.DateBroughtIn
        m.MovementType = 3
        a.Archived = 1
        a.ActiveMovementType = 3
        a.ActiveMovementID = m.ID

for row in cvacc:
    if row["Animal ID"] not in ppa or row["Date Given"] == "":
        continue
    a = ppa[row["Animal ID"]]
    comments = "Entered By: %s, Administered By: %s" % (row["System User Entered"], row["Adminstered By"])
    if row["Type"] == "Vaccination":
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.DateRequired = getdate(row["Date Given"])
        av.DateOfVaccination = av.DateRequired
        av.Manufacturer = row["Manufacturer"]
        av.BatchNumber = row["lot"]
        av.AnimalID = a.ID
        av.Comments = comments
        vaccmap = {
            "bordetella": 6,
            "dapp": 8,
            "dhlpp": 8,
            "rabies": 4,
            "feLV": 12,
            "fvrcp": 14,
            "distemper": 1
        }
        for k, i in vaccmap.iteritems():
            if row["Treatment"].lower().find(k) != -1: 
                av.VaccinationID = i
                break
    if row["Type"] == "Test":
        if row["Treatment"].startswith("Heartworm"):
            a.HeartwormTested = 1
            a.HeartwormTestDate = getdate(row["Date Given"])
    if row["Type"] == "Vet Treatment":
        startdate = getdate(row["Date Given"])
        treatmentname = row["Treatment"]
        dosage = "n/a"
        animalmedicals.append(asm.animal_regimen_single(a.ID, startdate, treatmentname, dosage, comments))

# Now that everything else is done, output stored records
print "DELETE FROM primarykey;"
print "DELETE FROM configuration WHERE ItemName Like 'VariableAnimalDataUpdated';"
for a in animals:
    print a
for am in animalmedicals:
    print am
for av in animalvaccinations:
    print av
for o in owners:
    print o
for m in movements:
    print m

asm.stderr_summary(animals=animals, animalmedicals=animalmedicals, animalvaccinations=animalvaccinations, owners=owners, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

