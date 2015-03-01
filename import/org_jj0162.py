#!/usr/bin/python

import asm, csv, sys, datetime

# Import script for Joe Jackson's Dog World, Inc.
# 3rd February, 2012

# For use with fields that just contain the sex
def getsexmf(s):
    if s.find("M") != -1:
        return 1
    elif s.find("F") != -1:
        return 0
    else:
        return 2

def findanimal(name = ""):
    """ Looks for an animal with the given name in the collection
        of animals. If one wasn't found, None is returned """
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

def getdate(s, defyear = "11"):
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

INTAKE = 0              # Eg: 2004 - 1, generate shelter code from it
NAME = 1                # Animal name
DOB = 2                 # DOB (y/m/d or sometimes Abt.*YEAR)
RESCUE_DATE = 3         # (y/m/d)
NOT_FOR_ADOPTION = 4    # x if not or empty string
SEX = 5                 # M or F
COLOR = 6               # String description of colour
BREED = 7               # Breed string 
                        # "MIX of (then comma list)"
                        # Remove the word "Mix" if it appears at end
                        # .*/.* is a mix
                        # What's left is breed to map
LITTER = 8              # L x-y (number of total)
FOSTERED = 9            # Y if fostered
FOSTER_PARENT = 10      # Foster owner name
DNA_TEST = 11           # Y / N
NEUTERED = 12           # Y / N
NEUTERED_DATE = 13      # (y/m/d)
MICROCHIPPED = 14       # Y / N
MICROCHIP_VENDOR = 15   # Vendor name
MICROCHIP_NUMBER = 16
RABIES_DATE = 17        # Date of rabies shot (y/m/d)
RABIES_TAG = 18
RABIES_DUE = 19         # Date next rabies due (y/m/d)
DHLPP2 = 20             # Date (y/m/d)
WORMS = 21              # String
BORDATELLA = 22         # Date (y/m/d)
HW_TEST_DATE = 23       # Date (y/m/d)
HW_RESULT = 24          # Neg
WEIGHT = 25             # Weight
HW_MEDICINE = 26        # String
HW_MEDICINE_DATE = 27   # Date (y/m/d)
ADOPTED = 28            # x = yes, empty string for no
ADOPTED_DATE = 29       # Date (y/m/d)
ADOPTER_NAME = 30
ADDRESS = 31
CITY = 32
STATE = 33
ZIP = 34
EMAIL = 35
RETURNED = 36           # Blank in data?
DECEASED = 37           # x = yes
DECEASED_DATE = 38      # (y/m/d)
COMMENTS = 39

reader = csv.reader(open("jjdwi.csv", "r"), dialect="excel")
for row in reader:

    # Not enough data for row
    if row[1].strip() == "": break

    # Each row contains a new animal
    a = asm.Animal()
    animals.append(a)
    comments = ""
    a.AnimalTypeID = 2
    a.SpeciesID = 1
    a.AnimalName = row[NAME]
    a.DateOfBirth = getdate(row[DOB])
    a.DateBroughtIn = getdate(row[RESCUE_DATE])
    a.generateCode("D")
    a.IsNotAvailableForAdoption = row[NOT_FOR_ADOPTION].find("x") != -1 and 1 or 0
    a.Sex = getsexmf(row[SEX])
    a.BaseColourID = asm.colour_id_for_name(row[COLOR], True)
    comments = "Original breed: " + row[BREED] + ", "
    breed = row[BREED]
    breed = breed.replace(" Mix", "").replace("MIX of", "").replace("?", "").replace("/", ",")
    breeds = breed.split(",")
    if len(breeds) == 1:
        a.BreedID = asm.breed_id_for_name(breeds[0].strip())
        a.Breed2ID = asm.breed_id_for_name(breeds[0].strip())
        a.BreedName = asm.breed_name_for_id(a.BreedID)
        a.CrossBreed = 0
    elif len(breeds) > 1:
        a.BreedID = asm.breed_id_for_name(breeds[0].strip())
        a.Breed2ID = asm.breed_id_for_name(breeds[1].strip())
        a.BreedName = asm.breed_name_for_id(a.BreedID) + " / " + asm.breed_name_for_id(a.Breed2ID)
        a.CrossBreed = 1
    else:
        a.BreedID = 1
        a.Breed2ID = 1
        a.BreedName = asm.breed_name_for_id(1)
        a.CrossBreed = 0
    a.AcceptanceNumber = row[LITTER]
    if row[FOSTERED].strip() == "Y":
        o = asm.Owner()
        o.SplitName(row[FOSTER_PARENT])
        o.IsFosterer = 1
        owners.append(o)
        m = asm.Movement()
        m.OwnerID = o.ID
        m.AnimalID = a.ID
        m.MovementType = 2
        m.MovementDate = a.DateBroughtIn
        movements.append(m)
    comments += "DNA Test: " + row[DNA_TEST] + ", "
    a.Neutered = row[NEUTERED].find("Y") != -1 and 1 or 0
    a.NeuteredDate = getdate(row[NEUTERED_DATE])
    a.Identichipped = row[MICROCHIPPED].find("Y") != -1 and 1 or 0
    comments += "Microchip Vendor: " + row[MICROCHIP_VENDOR] + ", "
    a.IdentichipNumber = row[MICROCHIP_NUMBER]
    comments += "Last Date Rabies Given: " + row[RABIES_DATE] + ", "
    a.RabiesTag = row[RABIES_TAG]
    comments += "Rabies Due: " + row[RABIES_DUE] + ", "
    comments += "DHLPP2: " + row[DHLPP2] + ", "
    comments += "Worms: " + row[WORMS] + ", "
    comments += "Bordatella: " + row[BORDATELLA] + ", "
    a.HeartwormTestDate = getdate(row[HW_TEST_DATE])
    a.HeartwormTested = a.HeartwormTestDate == None and 0 or 1
    a.HeartwormTestResult = row[HW_RESULT].strip() == "Neg" and 1 or 0
    comments += "Weight: " + row[WEIGHT] + ", "
    comments += "HW Medicine Given: " + row[HW_MEDICINE] + ", "
    comments += "HW Medicine Date: " + row[HW_MEDICINE_DATE] + ", "
    if row[ADOPTED].strip() == "x":
        o = asm.Owner()
        o.SplitName(row[ADOPTER_NAME])
        owners.append(o)
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate =  getdate(row[ADOPTED_DATE])
        movements.append(m)
        o.OwnerAddress = row[ADDRESS]
        o.OwnerTown = row[CITY]
        o.OwnerCounty = row[STATE]
        o.OwnerPostcode = row[ZIP]
        o.EmailAddress = row[EMAIL]
    if row[DECEASED].strip() == "x":
        a.DeceasedDate = getdate(row[DECEASED_DATE])
    a.AnimalComments = row[COMMENTS]
    a.HiddenAnimalDetails = comments

# Now that everything else is done, output stored records
print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal;\n"
print "DELETE FROM owner;\n"
print "DELETE FROM adoption;\n"
for a in animals:
    print a
for o in owners:
    print o
for m in movements:
    print m

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"
