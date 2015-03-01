#!/usr/bin/python

import asm, csv, sys, datetime

# Import script for Madison Animal Rescue Foundation
# 7th December, 2012

# For use with fields that just contain the sex
def getsexmf(s):
    if s.find("Male") != -1:
        return 1
    elif s.find("Female") != -1:
        return 0
    else:
        return 2

def strip(row, index):
    s = ""
    try:
        s = row[index]
    except:
        pass
    return s.replace("NULL", "").strip()

def gettype(species):
    if species.find("Cat") != -1:
        return 43
    else: 
        return 44

def getsize(size):
    if size == "Very":
        return 0
    elif size == "Large":
        return 1
    elif size == "Medium":
        return 2
    else:
        return 3

def findanimal(code = "", name = ""):
    """ Looks for an animal with the given code in the collection
        of animals. If one wasn't found, It tries the name. If still
        nothing is found, None is returned """
    for a in animals:
        if a.ShelterCode == code.strip():
            return a
    for a in animals:
        if a.AnimalName == name.strip():
            return a
    return None

def findowner(name = ""):
    """ Looks for an owner with the given name in the collection
        of owners. If one wasn't found, None is returned """
    for o in owners:
        if o.OwnerName == name.strip():
            return o
    return None

def getdate(s, defyear = "12"):
    """ Parses a date in YYYY/MM/DD format. If the field is blank, None is returned """
    if s.startswith("Abt"):
        # It's an about date, use the last 2 characters as 2 digit year
        return datetime.date(int(s[len(s)-2:]) + 2000, 1, 1)
    if s.strip() == "": return None
    b = s.split("/")
    # if we couldn't parse the date, use the first of the default year
    if len(b) < 3: return datetime.date(int(defyear) + 2000, 1, 1)
    try:
        year = int(b[0])
        if year < 1900: year += 2000
        return datetime.date(year, int(b[1]), int(b[2]))
    except:
        return datetime.date(int(defyear) + 2000, 1, 1)

def getdateiso(s, defyear = "12"):
    """ Parses a date in YYYY-MM-DD format. If the field is blank, None is returned """
    if s.strip() == "": return None
    b = s.split("/")
    # if we couldn't parse the date, use the first of the default year
    if len(b) < 3: return datetime.date(int(defyear) + 2000, 1, 1)
    try:
        year = int(b[0])
        if year < 1900: year += 2000
        return datetime.date(year, int(b[1]), int(b[2]))
    except:
        return datetime.date(int(defyear) + 2000, 1, 1)

def getdateage(age, arrivaldate):
    """ Returns a date for one of Baby, Young, Adult, Senior """
    if age == "Baby":
        return arrivaldate - datetime.timedelta(days=30 * 3)
    elif age == "Young":
        return arrivaldate - datetime.timedelta(days=30 * 9)
    elif age == "Adult":
        return arrivaldate - datetime.timedelta(days=365 * 2)
    else:
        return arrivaldate - datetime.timedelta(days=365 * 9)

def tocurrency(s):
    if s.strip() == "": return 0.0
    s = s.replace("$", "")
    try:
        return float(s)
    except:
        return 0.0

# --- START OF CONVERSION ---

owners = []
movements = []
animals = []

nextanimalid = 100
nextownerid = 100
nextmovementid = 100

# Create a catchall unknown owner
o = asm.Owner(nextownerid)
owners.append(o)
nextownerid += 1
o.OwnerForeNames = "Unknown"
o.OwnerSurname = "Unknown"
o.Comments = "Catchall owner for adopted animals that did not have an owner in the data source."
UNKNOWN_OWNER_ID = o.ID

PETFINDER_SYSTEMID = 0
ANIMAL_ID = 1
NAME = 2
STATUS = 3
ARRIVAL_DATE = 4
ANIMAL_TYPE = 5
SPECIES = 6
BREED = 7
SECONDARY_BREED = 8
MIXED_BREED = 9
COLOR = 10
COAT_LENGTH = 11
GENDER = 12
SIZE = 13
AGE = 14
CONTACT = 15
LOCATION = 16

reader = csv.reader(open("animals.csv", "r"), dialect="excel")
for row in reader:

    # If the animal is adoptable, they've already keyed it in
    if row[STATUS].strip() != "Adopted": continue

    # Each row contains a new animal
    a = asm.Animal(nextanimalid)
    animals.append(a)
    nextanimalid += 1
    comments = "PetFinder SystemID: %s, PetFinder AnimalID: %s" % (row[PETFINDER_SYSTEMID], row[ANIMAL_ID])
    a.AnimalTypeID = gettype(row[SPECIES])
    a.SpeciesID = asm.species_id_for_name(row[SPECIES])
    a.AnimalName = row[NAME]
    a.DateOfBirth = getdateage(row[AGE], getdateiso(row[ARRIVAL_DATE]))
    a.DateBroughtIn = getdateiso(row[ARRIVAL_DATE])
    if a.AnimalTypeID == 43:
        a.generateCode("C")
    else:
        a.generateCode("D")
    if row[ANIMAL_ID].strip() != "":
        a.ShelterCode = row[ANIMAL_ID]
        a.ShortCode = row[ANIMAL_ID]
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 6
    a.Sex = getsexmf(row[GENDER])
    a.Size = getsize(row[SIZE])
    a.BaseColourID = asm.colour_id_for_name(row[COLOR], True)
    comments += ", Original breed: " + row[BREED] + " / " + row[SECONDARY_BREED]
    comments += row[MIXED_BREED] == "TRUE" and " (mixed)" or ""
    a.BreedID = asm.breed_id_for_name(row[BREED])
    if row[SECONDARY_BREED].strip() != "":
        a.Breed2ID = asm.breed_id_for_name(row[SECONDARY_BREED])
        a.BreedName = asm.breed_name_for_id(a.BreedID) + " / " + asm.breed_name_for_id(a.Breed2ID)
        a.CrossBreed = 1
    else:
        a.Breed2ID = a.BreedID
        a.BreedName = asm.breed_name_for_id(a.BreedID)
        a.CrossBreed = 0
    a.HiddenAnimalDetails = comments
    a.Archived = 0

ID = 0
ANIMALID = 1
ANIMALNAME = 2
MICROCHIPID = 3
DATEARF = 4
SPECIES = 5
SEX = 6
SPAYNEUT = 7
AGE = 8
SIZE = 9
DESCRIPTION = 10
TEMPERAMENT = 11
PHYSICALCONDITION = 12
MEDICALNEEDS = 13
SPECIALNEEDS = 14
SIBLINGIDS = 15
PHOTOFILENAMES = 16
FLAG = 17
WRITEUP = 18
DATEPICKEDUP = 19
DATETORELEASE = 20
WHEREPICKEDUP = 21
ORIGIN = 22
FLAGAC = 23
HAPPYTALES = 24
FLAGMED = 25
JUVENILE = 26
AGGRESSION = 27
SNIP = 28
BIRTHDATE = 29
DISPOSITION = 30
DATEADOPTED = 31

reader = csv.reader(open("animals2.csv", "r"), dialect="excel")
for row in reader:

    # Find the matching animal
    a = findanimal(row[ANIMAL_ID], row[ANIMALNAME])

    # Skip if there wasn't one
    if a == None: continue

    # Update extra info from these fields
    a.AnimalComments = strip(row, WRITEUP)
    a.HiddenAnimalDetails += ", Picked up: " + strip(row, WHEREPICKEDUP)
    a.HealthProblems = strip(row, MEDICALNEEDS) + " " + strip(row, SPECIALNEEDS)
    if a.HealthProblems.strip() != "": a.HasSpecialNeeds = 1
    if strip(row, SPAYNEUT).find("Y") != -1:
        a.Neutered = 1

ID = 0
ANIMALID = 1
ANIMALNAME = 2
DATEADOPTED = 3
FNAME = 4
LNAME = 5
ADDRESS = 6
CITY = 7
STATE = 8
ZIP = 9
PHONEHOME = 10
PHONECELL = 11
EMAIL = 12
COMMENTS = 13
RECORDCREATED = 14
DATAENTEREDBY = 15
VENUE = 16
MODE = 17
ADOPTIONFEE = 18

reader = csv.reader(open("adopters.csv", "r"), dialect="excel")
for row in reader:

    # Find the matching animal for this adoption
    a = findanimal(row[ANIMALID], row[ANIMALNAME])

    # Skip if there wasn't one
    if a == None: continue

    # Create the owner
    o = asm.Owner(nextownerid)
    owners.append(o)
    nextownerid += 1
    o.OwnerForeNames = strip(row, FNAME)
    o.OwnerSurname = strip(row, LNAME)
    o.OwnerAddress = strip(row, ADDRESS)
    o.OwnerTown = strip(row, CITY)
    o.OwnerCounty = strip(row, STATE)
    o.OwnerPostcode = strip(row, ZIP)
    o.EmailAddress = strip(row, EMAIL)
    o.HomeTelephone = strip(row, PHONEHOME)
    o.MobileTelephone = strip(row, PHONECELL)
    o.Comments = strip(row, COMMENTS)

    m = asm.Movement(nextmovementid)
    nextmovementid += 1
    m.AnimalID = a.ID
    m.OwnerID = o.ID
    m.MovementType = 1
    m.MovementDate =  getdateiso(strip(row, DATEADOPTED))
    m.Comments = "Adoption Fee: " + strip(row, ADOPTIONFEE)
    a.Archived = 1
    a.ActiveMovementID = m.ID
    a.ActiveMovementType = 1
    movements.append(m)

ID = 0
FNAME = 1
LNAME = 2
FENCE = 3
WHAT2FOSTER = 4
OWNEDANIMALS = 5
KIDS = 6
REMARKS = 7
LICENSE = 8
ACTIVE = 9
UNALTERED = 10

reader = csv.reader(open("fosterers.csv", "r"), dialect="excel")
for row in reader:

    # Create the owner
    o = asm.Owner(nextownerid)
    owners.append(o)
    nextownerid += 1
    o.IsFosterer = 1
    o.OwnerForeNames = row[FNAME]
    o.OwnerSurname = row[LNAME]
    comments = "What2foster: " + strip(row, WHAT2FOSTER)
    comments += ", Fence: " + strip(row, FENCE)
    comments += ", Owned Animals: " + strip(row, OWNEDANIMALS)
    comments += ", Kids: " + strip(row, KIDS)
    comments += ", Remarks: " + strip(row, REMARKS)
    comments += ", License: " + strip(row, LICENSE)
    comments += ", Active: " + strip(row, ACTIVE)
    o.Comments = comments

# Find all the animals that don't have an owner and assign them the
# catchall
for a in animals:
    if a.Archived == 0:
        a.Archived = 1
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = UNKNOWN_OWNER_ID
        m.MovementType = 1
        m.MovementDate =  a.DateBroughtIn
        m.Comments = "No adoption record found."
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 1
        movements.append(m)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= 100;"
print "DELETE FROM owner WHERE ID >= 100;"
print "DELETE FROM adoption WHERE ID >= 100;"

# Now that everything else is done, output stored records
for a in animals:
    print a
for o in owners:
    print o
for m in movements:
    print m

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

