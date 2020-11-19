#!/usr/bin/python

import asm, csv, sys, datetime, math

# Import script for City of Ridgecrest Dog licensing
# 2nd June, 2012

# For use with fields that just contain the sex
def getsexmf(s):
    if s.find("F") != -1:
        return 0
    else:
        return 1

def findanimal(code = ""):
    """ Looks for an animal with the given code in the collection
        of animals. If one wasn't found, None is returned """
    for a in animals:
        if a.ShelterCode == code.strip():
            return a
    return None

def findowner(number = ""):
    """ Looks for an owner with the given membershipnumber in the collection
        of owners. If one wasn't found, None is returned """
    for o in owners:
        if o.MembershipNumber == number.strip():
            return o
    return None

def findownername(name = ""):
    """ Looks for an owner with the given name in the collection
        of owners. If one wasn't found, None is returned """
    for o in owners:
        if o.OwnerName == name.strip():
            return o
    return None

def getdate_fromage(age = 0):
    if age == None or age == 0 or age == "":
        return datetime.datetime.today()
    try:
        nodays = float(age) * 365.0
        nodays = math.floor(nodays)
        return datetime.datetime.today() - datetime.timedelta(days = nodays)
    except Exception,err:
        sys.stderr.write(str(err))
        return datetime.datetime.today()

def getdate(s, defyear = "11"):
    """ Parses a date in YYYY/MM/DD format. If the field is blank, None is returned """
    if s.startswith("Abt"):
        # It's an about date, use the last 2 characters as 2 digit year
        return datetime.date(int(s[len(s)-2:]) + 2000, 1, 1)
    if s.strip() == "": return None
    # Throw away time info
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
animals = []

ID = 0
TAG = 1                 # The licence tag number
DLAMT = 2               # Not used
DLPAMT = 3              # Not used
FIRSTNAME = 4
LASTNAME = 5
ADDRESS = 6
MAILING = 7
CITY = 8
STATE = 9
ZIP = 10
HOMEPHONE = 11
WORKPHONE = 12
VACCINATIONDATE = 13
VACCINATIONTYPE = 14
VACCINATIONMANUFACTURER = 15
VACCINATIONLOT = 16
DOGNAME = 17
DOGBREED = 18
DOGAGE = 19
DOGSEX = 20
ALTEREDDATE = 21
ALTERED = 22            # Y/N
COLOR = 23
VETNAME = 24
VETCITY = 25
VETSTATE = 26
VETPHONE = 27
VACCEXPIRES = 28
VICIOUS = 29
LICENSEEXPIRES = 30
DLACTV = 31             # Not used
NOTES1 = 32             # Only one that seems populated
NOTES2 = 33
NOTES3 = 34
NOTES4 = 35
NOTES5 = 36
LUDATE = 37             # Also not used
COMMENTSDATE = 38
COMMENTS = 39
AMOUNTUSED = 40
BOTTLE = 41
DESCRIPTION = 42
INITIALS = 43
SOMEDATE = 44
IMPOUNDDATE = 45
IMPOUND = 46
MICROCHIPNO = 47
ANIMALTYPE = 48         # Always DOG
ROWGUID = 49
USER = 50
RECORDDATE = 51

reader = csv.reader(open("ACO.csv", "r"), dialect="excel")
reader.next() # skip header
for row in reader:

    # Not enough data for row
    if row[0].strip() == "": break

    # Each row contains an original owner and animal - overwrite
    # if we've seen it before
    a = findanimal(row[TAG])
    if a == None:
        a = asm.Animal()
        animals.append(a)
    comments = ""
    a.AnimalTypeID = 2 # DOG
    a.SpeciesID = 1    # DOG
    a.AnimalName = row[DOGNAME]
    a.DateOfBirth = getdate_fromage(row[DOGAGE])
    a.EstimatedDOB = 1
    comments += "Age: " + row[DOGAGE] + ", "
    datebroughtin = getdate(row[RECORDDATE])
    if datebroughtin == None:
        datebroughtin = datetime.datetime.today()
    a.DateBroughtIn = datebroughtin
    a.ShelterCode = row[TAG]
    a.IsNotAvailableForAdoption = 1
    a.Sex = getsexmf(row[DOGSEX])
    a.BaseColourID = asm.colour_id_for_name(row[COLOR], True)
    comments += "Original color: " + row[COLOR] + ", "
    a.BreedID = asm.breed_id_for_name(row[DOGBREED])
    a.Breed2ID = asm.breed_id_for_name(row[DOGBREED])
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    a.CrossBreed = 0
    comments += "Original breed: " + row[DOGBREED] + ", "
    a.Neutered = row[ALTERED].find("Y") != -1 and 1 or 0
    a.NeuteredDate = getdate(row[ALTEREDDATE])
    a.Identichipped = row[MICROCHIPNO].strip() != "" and 1 or 0
    a.IdentichipNumber = row[MICROCHIPNO]
    comments += "Vaccination Type: " + row[VACCINATIONTYPE] + ", "
    comments += "Vaccination Date: " + row[VACCINATIONDATE] + ", "
    comments += "Vaccination Man: " + row[VACCINATIONMANUFACTURER] + ", "
    comments += "Vaccination Lot: " + row[VACCINATIONLOT]
    a.AnimalComments = row[NOTES1] + " " + row[COMMENTS]
    a.HiddenAnimalDetails = comments

    # Original Owner with license info
    o = findowner(row[TAG])
    if o == None:
        o = asm.Owner()
        owners.append(o)
    o.OwnerForeNames = row[FIRSTNAME]
    o.OwnerSurname = row[LASTNAME]
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = row[ADDRESS]
    o.OwnerTown = row[CITY]
    o.OwnerCounty = row[STATE]
    o.OwnerPostcode = row[ZIP]
    o.MembershipNumber = row[TAG]
    o.MembershipExpiryDate = getdate(row[LICENSEEXPIRES])
    o.IsMember = 1
    a.OriginalOwnerID = o.ID

    # Vet if we don't already have them
    o = findownername(row[VETNAME])
    if o == None:
        o = asm.Owner()
        owners.append(o)
        o.OwnerSurname = row[VETNAME]
        o.OwnerName = row[VETNAME]
        o.OwnerTown = row[VETCITY]
        o.OwnerCounty = row[VETSTATE]
        o.WorkTelephone = row[VETPHONE]
    a.CurrentVetID = o.ID
    a.OwnersVetID = o.ID

# Now that everything else is done, output stored records
print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal;\n"
print "DELETE FROM owner;\n"
for a in animals:
    print a
for o in owners:
    print o
print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

