#!/usr/bin/python

import asm

"""
Import script for dh1449

21st June 2018
"""

START_ID = 200

ADOPTED_FILENAME = "data/dh1449_excel/dh1449_adopted.csv"
CATS_FILENAME = "data/dh1449_excel/dh1449_cats.csv"
DOGS_FILENAME = "data/dh1449_excel/dh1449_dogs.csv"

def findowner(ownername = ""):
    """ Looks for an owner with the given name in the collection
        of owners. If one wasn't found, None is returned """
    for o in owners:
        if o.OwnerName == ownername.strip():
            return o
    return None

def get_sgn(s):
    sgn = s.split("/")
    if len(sgn) == 3:
        return s.split("/")
    if len(sgn) == 2:
        return s.split("/") + [""]
    elif len(sgn) == 1:
        return [s, "", ""]
    else:
        return ["", "", ""]

def get_bc(s):
    bc = s.split("/")
    if len(bc) >= 2:
        return [bc[0], bc[1]]
    elif len(bc) == 1:
        return [bc[0], ""]
    else:
        return ["", ""]

def getdate(d):
    return asm.getdate_guess(d)

# --- START OF CONVERSION ---

owners = []
movements = []
animals = []
animaltests = []
animalvaccinations = []
logs = []

asm.setid("animal", START_ID)
asm.setid("animalvaccination", START_ID)
asm.setid("log", START_ID)
asm.setid("owner", START_ID)
asm.setid("adoption", START_ID)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM animalvaccination WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM log WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM owner WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM adoption WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID

# Adopted animals first
for d in asm.csv_to_list(ADOPTED_FILENAME):
    # Each row contains an animal, person and adoption
    if d["PET NAME"].strip() == "": continue
    a = asm.Animal()
    animals.append(a)
    species, gender, neutered = get_sgn(d["SPECIES / GENDER"])
    if species == "F":
        a.AnimalTypeID = 11 # Unwanted Cat
        a.SpeciesID = 2
    else:
        a.AnimalTypeID = 2 # Unwanted Dog
        a.SpeciesID = 1
    a.AnimalName = d["PET NAME"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateBroughtIn = getdate(d["INTAKE"]) or asm.today().replace(year=2017,month=1,day=1)
    a.DateOfBirth = getdate(d["DOB"]) or a.DateBroughtIn
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    a.generateCode()
    a.Sex = asm.getsex_mf(gender)
    breed, color = get_bc(d["BREED/COLOR"])
    breed = breed.strip()
    color = color.strip()
    asm.breed_ids(a, breed)
    a.BaseColourID = asm.colour_id_for_name(color)
    a.Size = 2
    a.Neutered = neutered in ( "N", "S") and 1 or 0
    a.EntryReasonID = 17 # Surrender
    a.IdentichipNumber = d["AVID #"]
    if a.IdentichipNumber != "": 
        a.Identichipped = 1
    a.IsGoodWithCats = 2
    a.IsGoodWithDogs = 2
    a.IsGoodWithChildren = 2
    a.HouseTrained = 0
    a.AnimalComments = d["NOTES"]
    a.HiddenAnimalDetails = "Foster: " + d["FOSTER"] + ", Breed/Color: " + d["BREED/COLOR"] + ", Species/Gender: " + d["SPECIES / GENDER"]

    # rabies
    rabiesdate = getdate(d["RABIES DATE"])
    rabiesexp = getdate(d["RABIES EXP."])
    if rabiesdate:
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.AnimalID = a.ID
        av.VaccinationID = 4
        av.DateRequired = rabiesdate
        av.DateOfVaccination = rabiesdate
        av.DateExpires = rabiesexp

    # adopter
    adoptdate = getdate(d["ADOPT DATE"])
    if adoptdate:
        o = findowner(d["NAME"])
        if o == None:
            o = asm.Owner()
            owners.append(o)
            o.OwnerName = d["NAME"]
            bits = o.OwnerName.split(" ")
            if len(bits) > 1:
                o.OwnerForeNames = bits[0]
                o.OwnerSurname = bits[len(bits)-1]
            else:
                o.OwnerSurname = o.OwnerName
            o.OwnerAddress = d["ADDR"]
            o.OwnerTown = "Layton"
            o.OwnerCounty = "UT"
            o.OwnerPostcode = o.OwnerAddress[-5:]
            o.EmailAddress = d["email"]
            o.HomeTelephone = d["HOME"]
            o.MobileTelephone = d["WORK"]
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = adoptdate
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 1
        a.LastChangedDate = adoptdate
        movements.append(m)

# CATS
for d in asm.csv_to_list(CATS_FILENAME):
    if d["PET NAME/ID"].strip() == "": continue
    # Each row contains an animal
    a = asm.Animal()
    animals.append(a)
    species, gender, neutered = get_sgn(d["SPECIES / GENDER"])
    if species == "F":
        a.AnimalTypeID = 11 # Unwanted Cat
        a.SpeciesID = 2
    else:
        a.AnimalTypeID = 2 # Unwanted Dog
        a.SpeciesID = 1
    a.AnimalName = d["PET NAME/ID"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateBroughtIn = getdate(d["INTAKE"]) or asm.today().replace(year=2017,month=1,day=1)
    a.DateOfBirth = getdate(d["DOB"]) or a.DateBroughtIn
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    a.generateCode()
    a.Sex = asm.getsex_mf(gender)
    breed, color = get_bc(d["BREED/COLOR"])
    breed = breed.strip()
    color = color.strip()
    asm.breed_ids(a, breed)
    a.BaseColourID = asm.colour_id_for_name(color)
    a.Size = 2
    a.Neutered = neutered in ( "N", "S") and 1 or 0
    a.EntryReasonID = 17 # Surrender
    a.IdentichipNumber = d["AVID #"]
    if a.IdentichipNumber != "": 
        a.Identichipped = 1
    a.IsGoodWithCats = 2
    a.IsGoodWithDogs = 2
    a.IsGoodWithChildren = 2
    a.HouseTrained = 0
    a.AnimalComments = d["NOTES"]
    a.HiddenAnimalDetails = "Foster: " + d["FOSTER"] + ", Breed/Color: " + d["BREED/COLOR"] + ", Species/Gender: " + d["SPECIES / GENDER"] + ", Tag: " + d["TAG #"]

    # fvrcpc
    fvrcpc = getdate(d["FVRCPC"])
    if fvrcpc:
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.AnimalID = a.ID
        av.VaccinationID = 14
        av.DateRequired = fvrcpc
        av.DateOfVaccination = fvrcpc

    # rabies
    rabiesdate = getdate(d["Rabies Date"])
    rabiesexp = getdate(d["Rabies Exp."])
    if rabiesdate:
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.AnimalID = a.ID
        av.VaccinationID = 4
        av.DateRequired = rabiesdate
        av.DateOfVaccination = rabiesdate
        av.DateExpires = rabiesexp

# DOGS
for d in asm.csv_to_list(DOGS_FILENAME):
    if d["PET NAME"].strip() == "": continue
    # Each row contains an animal
    a = asm.Animal()
    animals.append(a)
    species, gender, neutered = get_sgn(d["SPECIES / GENDER"])
    if species == "F":
        a.AnimalTypeID = 11 # Unwanted Cat
        a.SpeciesID = 2
    else:
        a.AnimalTypeID = 2 # Unwanted Dog
        a.SpeciesID = 1
    a.AnimalName = d["PET NAME"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateBroughtIn = getdate(d["INTAKE"]) or asm.today().replace(year=2017,month=1,day=1)
    a.DateOfBirth = getdate(d["DOB"]) or a.DateBroughtIn
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    a.generateCode()
    a.Sex = asm.getsex_mf(gender)
    breed, color = get_bc(d["BREED/COLOR"])
    breed = breed.strip()
    color = color.strip()
    asm.breed_ids(a, breed)
    a.BaseColourID = asm.colour_id_for_name(color)
    a.Size = 2
    a.Neutered = neutered in ( "N", "S") and 1 or 0
    a.EntryReasonID = 17 # Surrender
    a.IdentichipNumber = d["chip "]
    if a.IdentichipNumber != "": 
        a.Identichipped = 1
    a.IsGoodWithCats = 2
    a.IsGoodWithDogs = 2
    a.IsGoodWithChildren = 2
    a.HouseTrained = 0
    a.AnimalComments = d["NOTES"]
    a.HiddenAnimalDetails = "Foster: " + d["FOSTER"] + ", Breed/Color: " + d["BREED/COLOR"] + ", Species/Gender: " + d["SPECIES / GENDER"]

    # fvrcpc
    fvrcpc = getdate(d["FVRCPC"])
    if fvrcpc:
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.AnimalID = a.ID
        av.VaccinationID = 8
        av.DateRequired = fvrcpc
        av.DateOfVaccination = fvrcpc

    # rabies
    rabiesdate = getdate(d["RABIES DATE"])
    rabiesexp = getdate(d["RABIES EXP."])
    if rabiesdate:
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.AnimalID = a.ID
        av.VaccinationID = 4
        av.DateRequired = rabiesdate
        av.DateOfVaccination = rabiesdate
        av.DateExpires = rabiesexp



# Run back through the animals, if we have any that are still
# on shelter after 1 year, add an adoption to an unknown owner
# asm.adopt_older_than(animals, movements, uo.ID, 365)

# Now that everything else is done, output stored records
for a in animals:
    print a
for av in animalvaccinations:
    print av
for o in owners:
    print o
for m in movements:
    print m
for l in logs:
    print l

asm.stderr_summary(animals=animals, animalvaccinations=animalvaccinations, logs=logs, owners=owners, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

