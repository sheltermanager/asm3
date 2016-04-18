#!/usr/bin/python

import asm

"""
Import script for BlueCross "Zoo Prod" access database:
    tblOwnerDetails, tblPetDetails, tblSurrenderDetails

15th April, 2016
"""

PATH = "data/bluecross"

def getcoattype(hair):
    if hair == "SHORT":
        return 0
    elif hair == "MEDIUM" or hair == "LONG":
        return 1
    elif hair == "WIRE":
        return 2
    elif hair == "CURLY":
        return 3
    return 0

def gettype(animaldes):
    spmap = {
        "DOG": 2,
        "CAT": 11,
        "BIRD": 13,
        "RABBIT": 13
    }
    species = animaldes.upper()
    if spmap.has_key(species):
        return spmap[species]
    else:
        return 2

def gettypeletter(aid):
    tmap = {
        2: "D",
        11: "U",
        13: "M"
    }
    return tmap[aid]

def getdate(d):
    return asm.getdate_mmddyy(d)

def getdateage(arrivaldate, age, period):
    """ Returns a date adjusted for age. 
        age is a number, period is YEARS, MONTHS or WEEKS """
    d = getdate(arrivaldate)
    if d is None: d = asm.now()
    if period == "YEARS":
        d = asm.subtract_days(d, 365 * asm.cfloat(age))
    if period == "MONTHS":
        d = asm.subtract_days(d, 31 * asm.cfloat(age))
    if period == "WEEKS":
        d = asm.subtract_days(d, 7 * asm.cfloat(age))
    return d

owners = []
movements = []
animals = []
animalvaccinations = []

ppa = {}
ppo = {}

asm.setid("animal", 100)
asm.setid("animalvaccination", 100)
asm.setid("owner", 100)
asm.setid("adoption", 100)

# Remove existing
print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= 100;"
print "DELETE FROM animalvaccination WHERE ID >= 100;"
print "DELETE FROM owner WHERE ID >= 100;"
print "DELETE FROM adoption WHERE ID >= 100;"

# Load up data files
cowner = asm.csv_to_list("%s/tblOwnerDetails.csv" % PATH)
canimal = asm.csv_to_list("%s/tblPetDetails.csv" % PATH)
csurr = asm.csv_to_list("%s/tblSurrenderDetails.csv" % PATH)

# People first
for row in cowner:
    o = asm.Owner()
    owners.append(o)
    ppo[row["OwnerId"]] = o
    o.OwnerTitle = row["Title"]
    o.OwnerForeNames = row["FirstName"]
    o.OwnerSurname = row["Surname"]
    o.OwnerName = o.OwnerTitle + " " + o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = row["Street"]
    o.OwnerTown = row["Suburb"]
    o.OwnerCounty = row["State"]
    o.OwnerPostcode = row["PostCode"]
    o.HomeTelephone = row["PhoneHome"]
    o.WorkTelephone = row["PhoneWork"]
    o.MobilePhone = row["MobilePhone"]
    o.EmailAddress = row["Email"]
    if row["AlternatePhone"] != "":
        o.Comments = "Alternate: %s %s" % (row["AlternateName"], row["AlternatePhone"])

# Now animals
for row in canimal:
    a = asm.Animal()
    animals.append(a)
    ppa[row["PetId"]] = a
    a.AnimalTypeID = gettype(row["Species"])
    a.SpeciesID = asm.species_id_for_name(row["Species"])
    a.AnimalName = row["Name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateOfBirth = getdateage(row["ArrivalDate"], row["Age"], row["Period"])
    if a.DateOfBirth is None: a.DateOfBirth = asm.now()
    a.DateBroughtIn = getdate(row["ArrivalDate"])
    if a.DateBroughtIn is None:
        a.DateBroughtIn = asm.now()
    a.generateCode(gettypeletter(a.AnimalTypeID))
    a.ShortCode = row["EntryNo"]
    a.RabiesTag = row["DiscNo"]
    a.BreedID = asm.breed_id_for_name(row["Breed"])
    # If we've got the default dog breed with a cat, switch to DSH
    if a.SpeciesID == 2 and a.BreedID == 1: a.BreedID = 261
    if row["Breed"].find("X") != -1:
        a.CrossBreed = 1
        a.Breed2ID = 442
    a.BreedName = asm.breed_name(a.BreedID, a.Breed2ID)
    a.BaseColourID = asm.colour_id_for_name(row["Color"])
    a.AnimalComments = row["Notes"]
    a.IdentichipNumber = row["ChipId"]
    if a.IdentichipNumber != "": a.Identichipped = 1
    a.Neutered = asm.iif(row["Desex"] == "YES", 1, 0)
    a.NeuteredDate = getdate(row["DesexDate"])
    a.HealthProblems = row["VetNotes"]
    a.EntryReasonID = 4
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 1
    a.Sex = asm.getsex_mf(row["Sex"])
    a.CoatType = getcoattype(row["Hair"])
    a.HiddenAnimalDetails = "Breed: %s\nColor: %s\nCollarNo: %s\nHair: %s\nStatus: %s" % (row["Breed"], row["Color"], row["CollarNo"], row["Hair"], row["Status"])
    a.Archived = 0
    # Deal with shelter status
    exitdate = getdate(row["StatusDate"])
    if exitdate is None: exitdate = getdate(row["DepartureDate"])
    if exitdate is None: exitdate = getdate(row["ArrivalDate"])
    if row["Status"] == "PTS":
        a.PutToSleep = 1
        a.DeceasedDate = exitdate
        a.Archived = 1
    elif row["Status"] == "DIED":
        a.PutToSleep = 0
        a.DeceasedDate = exitdate
        a.Archived = 1
    elif row["Status"] == "SOLD":
        if not ppo.has_key(row["OwnerId"]): 
            #print "MISSING OWNERID: %s" % row["OwnerId"]
            continue
        o = ppo[row["OwnerId"]]
        if o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = exitdate
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = exitdate
        a.ActiveMovementType = 1
        movements.append(m)
    elif row["Status"] == "QTD":
        a.IsQuarantine = 1

# Now that everything else is done, output stored records
for a in animals:
    print a
#for av in animalvaccinations:
#    print av
for o in owners:
    print o
for m in movements:
    print m

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

