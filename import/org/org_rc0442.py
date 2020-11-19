#!/usr/bin/python

import asm, csv, datetime

# Import script for Red Collar Rescue
# 26th Nov, 2013

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
    return s.replace("NULL", "").replace("\\N", "").replace("\\", "").strip()

def findowner(oname = ""):
    """ Looks for an owner with the given name in the collection
        of owners. If one wasn't found, None is returned """
    for o in owners:
        if o.OwnerSurname == oname.strip():
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
    if s.find(" ") != -1: s = s[0:s.find(" ")]
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

startanimalid = 100
startownerid = 100
startmovementid = 100
nextanimalid = 100
nextownerid = 100
nextmovementid = 100

oa = asm.Owner(nextownerid)
nextownerid += 1
oa.OwnerSurname = "Catchall for animals leaving the shelter"
oa.OwnerName = "Catchall for animals leaving the shelter"
owners.append(oa)

DATE_IN = 0
ADOPTED_MOVED = 1
IMPOUND_NO = 2
DATE_OUT = 3
BLANK = 4
DOG_NAME = 5
DESEXED = 6
ADOPTION_FEE_PAID = 7
AGE = 8
BREED = 9
COLOUR = 10
GENDER = 11
WEIGHT = 12
SURRENDER_TO = 13
MEDICATION = 14
VET_WORK = 15
VACC = 16
MICROCHIP_NUMBER = 17
NOTES = 18
FOSTER = 19
ADOPTERS_NAME = 20
ADOPTION_FEE = 21

lastdatein = "2009/12/01"
reader = csv.reader(open("rcr.csv", "rb"), dialect="excel")
for row in reader:

    # Ignore the header and blanks
    if row[DATE_IN] == "Date In": continue
    if row[DATE_IN] != "":
        lastdatein = row[DATE_IN]

    # Each row contains a new animal
    a = asm.Animal(nextanimalid)
    animals.append(a)
    nextanimalid += 1
    comments = "%s, Impound: %s, Adoption Fee: %s, Age: %s, Breed: %s, Colour: %s, Weight: %s, Medication: %s, Vet Work: %s, Vacc: %s, Foster: %s, Adopter Name: %s, Adoption Fee: %s" % (
        strip(row, NOTES), strip(row, IMPOUND_NO), strip(row, ADOPTION_FEE), strip(row, AGE), strip(row, BREED), strip(row, COLOUR), strip(row, WEIGHT), strip(row, MEDICATION), strip(row, VET_WORK), strip(row, VACC), strip(row, FOSTER), strip(row, ADOPTERS_NAME), strip(row, ADOPTION_FEE)
    )
    a.AnimalName = strip(row, DOG_NAME)
    a.AnimalTypeID = 2
    a.SpeciesID = 1
    a.BreedID = asm.breed_id_for_name(row[BREED])
    a.Breed2ID = a.BreedID
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    a.BaseColourID = asm.colour_id_for_name(row[COLOUR], True)
    a.DateOfBirth = getdate(lastdatein)
    a.DateBroughtIn = getdate(lastdatein)
    a.Sex = getsexmf(row[GENDER])
    a.generateCode("D")
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 1
    a.IdentichipNumber = strip(row, MICROCHIP_NUMBER)
    if a.IdentichipNumber.strip() != "":
        a.Identichipped = 1
        a.IdentichipDate = getdate(lastdatein)
    a.HiddenAnimalDetails = comments
    if row[DESEXED].find("Y") != -1:
        a.Neutered = 1
        a.NeuteredDate = getdate(lastdatein)
    if row[ADOPTED_MOVED].find("PTS") != -1 or row[DESEXED].find("PTS") != -1:
        a.DeceasedDate = getdate(lastdatein)
        a.PutToSleep = 1
    if row[ADOPTED_MOVED].find("Gone") != -1:
        m = asm.Movement(nextmovementid)
        movements.append(m)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = oa.ID
        m.MovementType = 1
        m.MovementDate = getdate(lastdatein)
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = m.MovementType
        a.Archived = 1
    if row[SURRENDER_TO] != "":
        so = findowner(row[SURRENDER_TO])
        if so is None:
            so = asm.Owner(nextownerid)
            nextownerid += 1
            so.OwnerSurname = row[SURRENDER_TO]
            so.OwnerName = so.OwnerSurname
            owners.append(so)
        a.BroughtInByOwnerID = so.ID

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= %d;" % startanimalid
print "DELETE FROM owner WHERE ID >= %d;" % startownerid
print "DELETE FROM adoption WHERE ID >= %d;" % startmovementid

# Now that everything else is done, output stored records
for a in animals:
    print a
for o in owners:
    print o
for m in movements:
    print m

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

