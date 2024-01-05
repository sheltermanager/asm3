#!/usr/bin/env python3

import asm

"""
Import script for PetPal databases exported as CSV

4th Jan, 2022
"""

PATH = "/home/robin/tmp/asm3_import_data/petpal_dg2748.csv"

# The shelter's petfinder ID for grabbing animal images for adoptable animals
PETFINDER_ID = ""

# --- START OF CONVERSION ---

owners = []
movements = []
animals = []

asm.setid("animal", 100)
asm.setid("owner", 100)
asm.setid("adoption", 100)

print("\\set ON_ERROR_STOP\nBEGIN;")
print("DELETE FROM animal WHERE ID >= 100 AND CreatedBy LIKE '%conversion';")
print("DELETE FROM owner WHERE ID >= 100 AND CreatedBy = 'conversion';")
print("DELETE FROM adoption WHERE ID >= 100 AND CreatedBy = 'conversion';")

pf = ""
if PETFINDER_ID != "":
    asm.setid("media", 100)
    asm.setid("dbfs", 200)
    print("DELETE FROM media WHERE ID >= 100;")
    print("DELETE FROM dbfs WHERE ID >= 200;")
    pf = asm.petfinder_get_adoptable(PETFINDER_ID)

data = asm.csv_to_list(PATH)

uo = asm.Owner()
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname
owners.append(uo)

# petpal files are newest first order
for d in reversed(data):
    a = asm.Animal()
    animals.append(a)
    a.AnimalTypeID = asm.iif(d["Pet Type"] == "Cat", 11, 2)
    if a.AnimalTypeID == 11 and d["Intake Type"] == "Stray":
        a.AnimalTypeID = 12
    a.SpeciesID = asm.species_id_for_name(d["Pet Type"])
    a.AnimalName = d["Pet Name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    if d["DOB"].strip() == "":
        a.DateOfBirth = asm.getdate_mmddyyyy(d["Intake Date"])
        a.EstimatedDOB = 1
    else:
        a.DateOfBirth = asm.getdate_mmddyyyy(d["DOB"])
    if a.DateOfBirth is None:
        a.DateOfBirth = asm.today()
        a.EstimatedDOB = 1
    a.DateBroughtIn = asm.getdate_mmddyyyy(d["Intake Date"])
    if a.DateBroughtIn is None:
        a.DateBroughtIn = asm.today()
    a.CreatedDate = asm.getdate_mmddyyyy(d["Added On"])
    a.CreatedBy = "%s/%s" %(d["Added By"], "conversion")
    a.LastChangedDate = asm.getdate_mmddyyyy(d["Updated On"])
    a.LastChangedBy = d["Last Updated By"]
    if a.CreatedDate is None: a.CreatedDate = asm.today()
    if a.LastChangedDate is None: a.LastChangedDate = asm.today()
    if d["Intake Type"] == "Shelter Transfer" or d["Intake Type"] == "Rescue Transfer" or d["Intake Type"] == "Pet Pulled":
        a.IsTransfer = 1
    a.ShelterCode = d["Pet ID"]
    a.ShortCode = d["Pet ID"]
    a.Markings = d["Colors or Markings"]
    a.BaseColourID = asm.colour_id_for_name(d["Colors or Markings"], True)
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 1
    a.ShelterLocationUnit = d["Cage Number"]
    a.Sex = asm.getsex_mf(d["Gender"])
    a.Size = asm.size_from_db(d["Size"])
    a.Weight = asm.cfloat(d["Weight"])
    if d["Is Declawed"] == "Yes": 
        a.Declawed = 1
    if d["HIV Positive"] == "Yes":
        a.CombiTested = 1
        a.CombiTestResult = 0
    if d["Has Tattoo"] == "Yes":
        a.Tattoo = 1
    a.Neutered = d["Is Pet Altered"] == "Yes" and 1 or 0
    a.IsGoodWithCats = 2
    a.IsGoodWithDogs = 2
    a.IsGoodWithChildren = 2
    a.HouseTrained = asm.iif(d["Housebroken"] == "Yes", 0, 2)
    a.Archived = 0
    a.EntryReasonID = 1
    if d["Intake Type"] == "Born In-House": 
        a.EntryReasonID = 13
        a.EntryTypeID = 5
    if d["Intake Type"] == "Pet Pulled" or d["Intake Type"] == "Rescue Transfer" or d["Intake Type"] == "Shelter Transfer": 
        a.EntryReasonID = 15
        a.EntryTypeID = 3
    if d["Intake Type"] == "Abandoned" or d["Intake Type"] == "Voluntary Surrender": 
        a.EntryReasonID = 11
        a.EntryTypeID = 1
    a.BreedID = asm.breed_id_for_name(d["Primary Breed"])
    a.Breed2ID = a.BreedID
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    a.CrossBreed = 0
    if d["Mix Breed"].strip() != "":
        a.CrossBreed = 1
        if d["Mix Breed"] == "Unknown Mixed Breed":
            a.Breed2ID = 442
        else:
            a.Breed2ID = asm.breed_id_for_name(d["Mix Breed"])
        if a.Breed2ID == 1: a.Breed2ID = 442
        a.BreedName = "%s / %s" % ( asm.breed_name_for_id(a.BreedID), asm.breed_name_for_id(a.Breed2ID) )
    comments = "Intake type: %s\nStatus: %s\nBreed: %s / %s\nAge: %s\nTemperament: %s" % \
        (d["Intake Type"], d["Status"], d["Primary Breed"], d["Mix Breed"], d["Age"], d["Temperament"])
    a.HiddenAnimalDetails = comments
    description = d["Description/Story"].replace("<p>", "").replace("\n", "").replace("</p>", "\n")
    a.AnimalComments = description

    if d["Status"] == "Deceased":
        a.DeceasedDate = min(a.LastChangedDate, a.DateBroughtIn)
        a.PTSReasonID = 2
        a.Archived = 1
    elif d["Status"] == "Adopted":
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = uo.ID
        m.MovementType = 1
        m.MovementDate = a.DateBroughtIn
        m.Comments = description
        a.Archived = 1
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 1
        a.LastChangedDate = m.MovementDate
        movements.append(m)
    elif d["Status"] == "Transferred Out":
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = uo.ID
        m.MovementType = 3
        m.MovementDate = a.DateBroughtIn
        m.Comments = description
        a.Archived = 1
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 3
        a.LastChangedDate = m.MovementDate
        movements.append(m)

# Get the current image for this animal from PetFinder if it is on shelter
if a.Archived == 0 and PETFINDER_ID != "" and pf != "":
    asm.petfinder_image(pf, a.ID, a.AnimalName)

# Now that everything else is done, output stored records
for a in animals:
    print(a)
for o in owners:
    print(o)
for m in movements:
    print(m)

asm.stderr_summary(animals=animals, owners=owners, movements=movements)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")

