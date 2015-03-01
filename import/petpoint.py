#!/usr/bin/python

import asm, csv, datetime

"""
Import script for PetPoint databases exported as CSV
(requires AnimalIntakeWithResultsExtended.csv)

27th October, 2014
"""

# The shelter's petfinder ID for grabbing animal images
PETFINDER_ID = "NC500"

# For use with fields that just contain the sex
def getsexmf(s):
    if s.startswith("M"):
        return 1
    elif s.startswith("F"):
        return 0
    else:
        return 2

def cint(s):
    try:
        return int(s)
    except:
        return 0

def strip(row, index):
    s = ""
    try:
        s = row[index]
    except:
        pass
    return s.replace("NULL", "").strip()

def gettype(s):
    spmap = {
        "Dog": 2,
        "Cat": 11
    }
    if spmap.has_key(s):
        return spmap[s]
    else:
        return 13 # Misc

def gettypeletter(aid):
    tmap = {
        2: "D",
        11: "U",
        12: "S",
        13: "M"
    }
    return tmap[aid]

def getsize(size):
    if size == "Very":
        return 0
    elif size == "Large":
        return 1
    elif size == "Medium":
        return 2
    else:
        return 3

def findanimal(animalkey):
    """ Looks for an animal with the given code in the collection
        of animals. If one wasn't found, It tries the name. If still
        nothing is found, None is returned """
    for a in animals:
        if a.ExtraID == animalkey.strip():
            return a
    return None

def findowner(ownername = ""):
    """ Looks for an owner with the given name in the collection
        of owners. If one wasn't found, None is returned """
    for o in owners:
        if o.OwnerName == ownername.strip():
            return o
    return None

def getdate(s, defyear = "14"):
    """ Parses a date in MM/DD/YYYY HH:MM:SS format. If the field is blank or not a date, None is returned """
    if s.strip() == "": return None
    if s.find("/") == -1: return None
    if s.find(" ") != -1: s = s.split(" ")[0]
    b = s.split("/")
    # if we couldn't parse the date, use the first of the default year
    if len(b) < 3: return datetime.date(int(defyear) + 2000, 1, 1)
    try:
        return datetime.date(int(b[2]), int(b[0]), int(b[1]))
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
    """ Returns a date adjusted for age. Age can be one of
        ADULT, PUPPY, KITTEN, SENIOR """
    d = getdate(arrivaldate)
    if d == None: d = datetime.datetime.today()
    if age == "ADULT":
        d = d - datetime.timedelta(days = 365 * 2)
    if age == "SENIOR":
        d = d - datetime.timedelta(days = 365 * 7)
    if age == "KITTEN":
        d = d - datetime.timedelta(days = 60)
    if age == "PUPPY":
        d = d - datetime.timedelta(days = 60)
    return d

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
ppa = {}

asm.setid("animal", 100)
asm.setid("owner", 100)
asm.setid("adoption", 100)
asm.setid("media", 100)
asm.setid("dbfs", 200)
print "DELETE FROM internallocation;"
print "DELETE FROM animal WHERE ID >= 100;"
print "DELETE FROM media WHERE ID >= 100;"
print "DELETE FROM dbfs WHERE ID >= 200;"
print "DELETE FROM owner WHERE ID >= 100;"
print "DELETE FROM adoption WHERE ID >= 100;"

ANIMAL_ID = 0
ARN = 1
ANIMAL_NAME = 2
ANIMAL_TYPE = 3
SPECIES = 4
PRIMARY_BREED = 5
SECONDARY_BREED = 6
DISTINGUISHING_MARKINGS = 7
GENDER = 8
ALTERED = 9
DANGER = 10
DANGER_REASON = 11
DATE_OF_BIRTH = 12
AGE_IN_MONTHS_INTAKE = 13
AGE_GROUP = 14
INTAKE_ASILOMAR_STATUS = 15
INTAKE_CONDITION = 16
INTAKE_RECORD_OWNER = 17
INTAKE_DATE = 18
INTAKE_TYPE = 19
INTAKE_SUBTYPE = 20
FOUND_ADDRESS = 21
FOUND_ZIP_CODE = 22
REASON = 23
INTAKE_SITENAME = 24
JURISDICTION_IN = 25
AGENCY_NAME = 26
AGENCY_MEMBER = 27
AGENCY_MEMBER_PHONE = 28
AGENCY_ADDRESS = 29
INTAKE_PERSON_ID = 30
INTAKE_PERSON_ID_TYPE = 31
ADMITTER = 32
STREET_NUMBER = 33
STREET_NAME = 34
STREET_TYPE = 35
STREET_DIRECTION = 36
STREET_DIRECTION2 = 37
UNIT_NUMBER = 38
CITY = 39
PROVINCE = 40
POSTAL_CODE = 41
ADMITTERS_EMAIL = 42
ADMITTERS_HOME_PHONE = 43
ADMITTERS_CELL_PHONE = 44
INITIAL_STAGE = 45
INITIAL_REVIEW_DATE = 46
AGE_IN_MONTHS_CURRENT = 47
MICROCHIP_ISSUE_DATE = 48
MICROCHIP_PROVIDER = 49
MICROCHIP_NUMBER = 50
PET_ID = 51
PET_ID_TYPE = 52
STATUS = 53
STAGE = 54
LOCATION = 55
SUBLOCATION = 56
OUTCOME_ASILOMAR_STATUS = 57
OUTCOME_NUMBER = 58
RELEASED_BY = 59
DATE_CREATED = 60
OUTCOME_DATE = 61
RELEASE_DATE = 62
OUTCOME_TYPE = 63
OUTCOME_SUBTYPE = 64
OUTCOME_SITENAME = 65
JURISDICTION_OUT = 66
OUTCOME_REASON = 67
OUTCOME_PERSON_ID = 68
OUTCOME_PERSON_ID_TYPE = 69
OUTCOME_PERSON_NAME = 70
OUT_STREET_NUMBER = 71
OUT_STREET_NAME = 72
OUT_STREET_TYPE = 73
OUT_STREET_DIRECTION = 74
OUT_STREET_DIRECTION2 = 75
OUT_UNIT_NUMBER = 76
OUT_CITY = 77
OUT_PROVINCE = 78
OUT_POSTAL_CODE = 79
OUT_EMAIL = 80
OUT_HOME_PHONE = 81
OUT_CELL_PHONE = 82

pf = ""
if PETFINDER_ID != "":
    pf = asm.petfinder_get_adoptable(PETFINDER_ID)

reader = csv.reader(open("data/AnimalIntakeWithResultsExtended.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[ANIMAL_ID] == "Animal ID": continue

    # Each row contains an animal, intake and outcome
    if not ppa.has_key(row[ANIMAL_ID]):
        a = asm.Animal()
        animals.append(a)
        ppa[row[ANIMAL_ID]] = a
        a.AnimalTypeID = gettype(row[ANIMAL_TYPE])
        if a.AnimalTypeID == 11 and row[INTAKE_TYPE] == "Stray":
            a.AnimalTypeID = 12
        a.SpeciesID = asm.species_id_for_name(row[ANIMAL_TYPE])
        a.AnimalName = row[ANIMAL_NAME]
        if a.AnimalName.strip() == "":
            a.AnimalName = "(unknown)"
        if row[DATE_OF_BIRTH].strip() == "":
            a.DateOfBirth = getdate(row[INTAKE_DATE])
        else:
            a.DateOfBirth = getdate(row[DATE_OF_BIRTH])
        if a.DateOfBirth is None:
            a.DateOfBirth = datetime.datetime.today()    
        a.DateBroughtIn = getdate(row[INTAKE_DATE])
        a.CreatedDate = a.DateBroughtIn
        a.LastChangedDate = a.DateBroughtIn
        if a.DateBroughtIn is None:
            a.DateBroughtIn = datetime.datetime.today()
        if row[INTAKE_TYPE] == "Transfer In":
            a.IsTransfer = 1
        a.generateCode(gettypeletter(a.AnimalTypeID))
        a.ShortCode = row[ANIMAL_ID]
        a.Markings = row[DISTINGUISHING_MARKINGS]
        a.IsNotAvailableForAdoption = 0
        a.ShelterLocation = asm.location_id_for_name(row[LOCATION])
        a.Sex = getsexmf(row[GENDER])
        a.Size = getsize(2)
        a.Neutered = row[ALTERED] == "Yes" and 1 or 0
        a.ReasonForEntry = row[REASON]
        a.IdentichipDate = getdate(row[MICROCHIP_ISSUE_DATE])
        a.IdentichipNumber = row[MICROCHIP_NUMBER]
        a.IsGoodWithCats = 2
        a.IsGoodWithDogs = 2
        a.IsGoodWithChildren = 2
        a.AsilomarIntakeCategory = row[INTAKE_CONDITION] == "Healthy" and 0 or 1
        a.HouseTrained = 0
        if a.IdentichipNumber != "": 
            a.Identichipped = 1
        a.Archived = 0
        comments = "Intake type: " + row[INTAKE_TYPE] + " " + row[INTAKE_SUBTYPE] + ", breed: " + row[PRIMARY_BREED] + "/" + row[SECONDARY_BREED]
        comments += ", age: " + row[AGE_GROUP]
        comments += ", intake condition: " + row[INTAKE_CONDITION]
        a.BreedID = asm.breed_id_for_name(row[PRIMARY_BREED])
        a.Breed2ID = a.BreedID
        a.BreedName = asm.breed_name_for_id(a.BreedID)
        a.CrossBreed = 0
        if row[SECONDARY_BREED].strip() != "":
            a.CrossBreed = 1
            if row[SECONDARY_BREED] == "Mix":
                a.Breed2ID = 442
            else:
                a.Breed2ID = asm.breed_id_for_name(row[SECONDARY_BREED])
            if a.Breed2ID == 1: a.Breed2ID = 442
            a.BreedName = "%s / %s" % ( asm.breed_name_for_id(a.BreedID), asm.breed_name_for_id(a.Breed2ID) )
        a.HiddenAnimalDetails = comments

    o = None
    if row[OUTCOME_PERSON_NAME].strip() != "":
        o = findowner(row[OUTCOME_PERSON_NAME])
        if o == None:
            o = asm.Owner()
            owners.append(o)
            o.OwnerName = row[OUTCOME_PERSON_NAME]
            bits = o.OwnerName.split(" ")
            if len(bits) > 1:
                o.OwnerForeNames = bits[0]
                o.OwnerSurname = bits[len(bits)-1]
            else:
                o.OwnerSurname = o.OwnerName
            o.OwnerAddress = row[OUT_STREET_NUMBER] + " " + row[OUT_STREET_NAME] + " " + row[OUT_STREET_TYPE] + " " + row[OUT_STREET_DIRECTION]
            o.OwnerTown = row[OUT_CITY]
            o.OwnerCounty = row[OUT_PROVINCE]
            o.OwnerPostcode = row[OUT_POSTAL_CODE]
            o.EmailAddress = row[OUT_EMAIL]
            o.HomeTelephone = row[OUT_HOME_PHONE]
            o.MobileTelephone = row[OUT_CELL_PHONE]

    ot = row[OUTCOME_TYPE]
    ost = row[OUTCOME_SUBTYPE]
    od = getdate(row[OUTCOME_DATE])
    if (ot == "Transfer Out" and ost == "Potential Adopter") or ot == "Adoption":
        if a is None or o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = od
        m.Comments = ot + "/" + ost
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 1
        a.LastChangedDate = od
        movements.append(m)
    elif ot == "Transfer Out":
        if a is None or o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 3
        m.MovementDate = od
        m.Comments = ot + "/" + ost
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 3
        a.LastChangedDate = od
        movements.append(m)
    elif ot == "Return to Owner/Guardian":
        if a is None or o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 4
        m.MovementDate = od
        m.Comments = ot + "/" + ost
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 3
        a.LastChangedDate = od
        movements.append(m)
    elif ot == "Died":
        a.PutToSleep = 0
        a.DeceasedDate = od
        a.Archived = 1
        a.PTSReason = ot + "/" + ost 
        a.LastChangedDate = od
    elif ot == "Euthanasia":
        a.PutToSleep = 1
        a.DeceasedDate = od
        a.Archived = 1
        a.PTSReason = ot + "/" + ost 
        a.LastChangedDate = od
    elif ot == "Service Out" or ot == "Clinic Out":
        if a is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = 0
        if o is not None:
            m.OwnerID = o.ID
        m.MovementType = 8
        m.MovementDate = od
        m.Comments = ot + "/" + ost
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 8
        a.LastChangedDate = od
        movements.append(m)

    # Get the current image for this animal from PetFinder if it is on shelter
    if a.Archived == 0 and PETFINDER_ID != "" and pf != "":
        asm.petfinder_image(pf, a.ID, a.AnimalName)

# Now that everything else is done, output stored records
print "\\set ON_ERROR_STOP\nBEGIN;"
for k,v in asm.locations.iteritems():
    print v
for a in animals:
    print a
for o in owners:
    print o
for m in movements:
    print m
print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

