#!/usr/bin/python

import asm, csv, datetime, sys

"""
Import script for Pets In Need custom access db

15th December, 2014
"""

# For use with fields that just contain the sex
def getsexmf(s):
    if s.startswith("MALE"):
        return 1
    elif s.startswith("FEMALE"):
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

def getcurrency(amt):
    try:
        amt = float(amt.replace("$", ""))
        amt = amt * 100
        return int(amt)
    except Exception,err:
        #sys.stderr.write(str(err) + "\n")
        return 0

def getpaymentmethod(meth):
    meth = meth.strip()
    if meth == "VISA":
        return 3
    elif meth == "MC":
        return 3
    elif meth == "CHECK":
        return 2
    elif meth == "CASH":
        return 1
    else:
        return 1

def getspecies(gtype):
    if gtype == "DOG" or gtype == "PUPPY": return 1
    if gtype == "CAT" or gtype == "KITTEN": return 2
    return 1
   
def gettype(gtype):
    if gtype == "DOG" or gtype == "PUPPY": return 2
    if gtype == "CAT" or gtype == "KITTEN": return 11
    return 2

def gettypeletter(aid):
    tmap = {
        2: "D",
        11: "U"
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
    if animalmap.has_key(animalkey):
        return animalmap[animalkey]
    return None

def findperson(personkey):
    """ Looks for an owner with the given name in the collection
        of owners. If one wasn't found, None is returned """
    if ownermap.has_key(personkey):
        return ownermap[personkey]
    return None

def getdate(s, defyear = "14"):
    """ Parses a date in YYYY/MM/DD format. If the field is blank or not a date, None is returned """
    if s.strip() == "": return None
    if s.find("/") == -1: return None
    if s.find(" ") != -1: s = s.split(" ")[0]
    b = s.split("/")
    # if we couldn't parse the date, use the first of the default year
    if len(b) < 3: return datetime.date(int(defyear) + 2000, 1, 1)
    try:
        return datetime.date(int(b[0]), int(b[1]), int(b[2]))
    except:
        return datetime.date(int(defyear) + 2000, 1, 1)

def getdatefi(s, defyear = "14"):
    try:
        return datetime.datetime.strptime(s, "%d-%b-%y")
    except:
        return None

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
    """ Returns a date adjusted for age, eg: 5 MONTHS, 2 YEARS. """
    d = getdate(arrivaldate)
    if d == None: d = datetime.datetime.today()
    w = age.split(" ")
    if len(w) != 2:
        # Didn't get two words
        return d - datetime.timedelta(days = 365)
    da = cint(w[0])
    if da == 0: 
        # Couldn't cast first word to an int - default 1 year
        return d - datetime.timedelta(days = 365)
    if w[1].startswith("MONTH"):
        d = d - datetime.timedelta(days = 30 * da)
    elif w[1].startswith("YEAR"):
        d = d - datetime.timedelta(days = 365 * da)
    # Didn't understand, default 1 year
    return d - datetime.timedelta(days = 365)

def tocurrency(s):
    if s.strip() == "": return 0.0
    s = s.replace("$", "")
    try:
        return float(s)
    except:
        return 0.0

def bs(s):
    return s.replace("\\", "/").replace("'", "`")

# --- START OF CONVERSION ---

ownermap = {}

owners = []
ownerdonations = []
movements = []
animals = []
animalvaccinations = []
logs = []

nextanimalid = 100
nextanimalvaccinationid = 100
nextlogid = 100
nextownerid = 100
nextownerdonationid = 100
nextmovementid = 100
startanimalid = 100
startanimalvaccinationid = 100
startownerdonationid = 100
startownerid = 100
startlogid = 100
startmovementid = 100

o = asm.Owner(nextownerid)
owners.append(o)
nextownerid += 1
o.OwnerSurname = "Unknown"
o.OwnerName = o.OwnerSurname

GUEST_PIN_ID = 0
GUEST_PIN_INTAKE_DATE = 1
GUEST_SHELTER_GUEST_NAME = 2
GUEST_DOG = 3
GUEST_MALE = 4
GUEST_BREED = 5
GUEST_AGE = 6
GUEST_COLOR = 7
GUEST_MICROCHIP__ = 8
GUEST_SOURCE = 9
GUEST_GUEST_STATUS = 10
GUEST_LOCATION = 11
ADOPT_DATE_OF_ADOPTION = 12
ADOPT_LAST_NAME = 13
ADOPT_FIRST_NAME = 14
ADOPT_2ND_FIRST_NAME = 15
ADOPT_2ND_LAST_NAME = 16
ADOPT_ADDRESS = 17
ADOPT_CITY = 18
ADOPT_STATE = 19
ADOPT_ZIP_CODE = 20
ADOPT_EMAIL = 21
ADOPT_WORK_PHONE = 22
ADOPT_WORK_PHONE_EXT = 23
ADOPT_HOME_PHONE = 24
ADOPT_CS_REP = 25
ADOPT_CS_REP_RETURN = 26
ADOPT_CA_DRIVERS_LICENSE = 27
ADOPT_ADOPTION_FEE = 28
ADOPT_DONATION = 29
ADOPT_OTHER_FEE = 30
ADOPT_TOTAL = 31
ADOPT_PAYMENT_TYPE = 32
ADOPT_PAYMENT__ = 33
ADOPT_EXP_DATE = 34
ADOPT_RABIES_TAG__ = 35
ADOPT_PIN_TAG = 36
ADOPT_DATE_RETURNED = 37
ADOPT_COMMENT = 38
CAT_FELV = 39
CAT_FELV_RESULT = 40
CAT_FIV = 41
CAT_FIV_RESULT = 42
CAT_BORDETELLA = 43
CAT_FVRCP_VACCINE_1 = 44
CAT_FVRCP_VACCINE_2 = 45
CAT_FVRCP_3 = 46
CAT_RABIES = 47
CAT_RABIES_SERIAL_NUMBER = 48
CAT_PERS_A1 = 49
CAT_PERS_A4 = 50
CAT_PERS_B1 = 51
CAT_PERS_B4 = 52
CAT_PERS_C1 = 53
CAT_PERS_C4 = 54
CAT_PERS_D1 = 55
CAT_PERS_D4 = 56
CAT_PERS_E1 = 57
CAT_PERS_E4 = 58
CAT_PERS_CHILD_LEVELS = 59
CAT_PERS_COMPATIBLE = 60
DOG_DHLPP_VACCINE_1 = 61
DOG_DHLPP_VACCINE_2 = 62
DOG_DHLPP_VACCINE_3 = 63
DOG_BORDETELLA = 64
DOG_RABIES = 65
DOG_RABIES_SERIAL_NUMBER = 66
DOG_PERS_A1 = 67
DOG_PERS_A4 = 68
DOG_PERS_B1 = 69
DOG_PERS_B4 = 70
DOG_PERS_C1 = 71
DOG_PERS_C4 = 72
DOG_PERS_D1 = 73
DOGPERS__D4 = 74
DOG_PERS_E1 = 75
DOG_PERS_E4 = 76
DOG_PERS_EXPERIENCE_LEVEL = 77
DOG_PERS_CHILD_LEVELS = 78
VET_EXAMINATION_DATE = 79
VET_OVERALL_APPEARANCE = 80
VET_WEIGHT = 81
VET_TEMP = 82
VET_EYES = 83
VET_EARS = 84
VET_NOSE = 85
VET_NAILS = 86
VET_MOUTH = 87
VET_SKIN = 88
VET_WOODS_LIGHT = 89
VET_CULTURE_STARTED = 90
VET_FECAL_DATE = 91
VET_DEWORMING = 92
VET_FLEA_TREATMENT = 93
VET_HOME_AGAIN = 94
VET_ALTERED = 95
VET_TREATMENT_SUMMARY = 96
VET_OTHER = 97
VET_DATE_OF_DEATH = 98
VET_DATE_OF_TREATMENT_SUMMARY = 99
PERS_NOTES = 100
PERS_SOURCE = 101
BEH_BEHAVIOR_INTAKE__DATE = 102
BEH_MADE_ADOPTABLE_DATE = 103

reader = csv.reader(open("data/shelter_guest_info.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[GUEST_PIN_ID].startswith("GUEST"): continue

    # Skip some blank rows with no intake date
    if strip(row, GUEST_PIN_INTAKE_DATE) == "": continue

    # Each row contains a new animal, owner, adoption and adoption donation
    a = asm.Animal(nextanimalid)
    animals.append(a)
    nextanimalid += 1
    a.DateBroughtIn = getdate(row[GUEST_PIN_INTAKE_DATE])
    if a.DateBroughtIn is None:
        a.DateBroughtIn = datetime.datetime.today()    
    a.SpeciesID = getspecies(row[GUEST_DOG])
    a.AnimalTypeID = gettype(row[GUEST_DOG])
    a.AnimalName = row[GUEST_SHELTER_GUEST_NAME]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.generateCode(gettypeletter(a.AnimalTypeID))
    a.ShortCode = row[GUEST_PIN_ID]
    a.Sex = getsexmf(row[GUEST_MALE])
    breed = row[GUEST_BREED]
    if breed.find("MIX") != -1:
        a.CrossBreed = 1
        breed = breed.replace("MIX", "")
        a.BreedID = asm.breed_id_for_name(breed)
        a.Breed2ID = 442
        a.BreedName = asm.breed_name_for_id(a.BreedID) + " / Crossbreed"
    else:
        a.BreedID = asm.breed_id_for_name(breed)
        a.BreedName = asm.breed_name_for_id(a.BreedID)
    a.DateOfBirth = getdateage(row[GUEST_AGE], row[GUEST_PIN_INTAKE_DATE])
    a.EstimatedDOB = 1
    a.BaseColourID = asm.colour_id_for_name(row[GUEST_COLOR])
    a.IdentichipNumber = row[GUEST_MICROCHIP__]
    if a.IdentichipNumber.strip() != "": a.Identichipped = 1
    a.IdentichipDate = a.DateBroughtIn
    a.RabiesTag = row[ADOPT_RABIES_TAG__]
    a.EntryReasonID = 1
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 1
    a.Sex = getsexmf(row[GUEST_MALE])
    if strip(row, VET_ALTERED) != "":
        a.Neutered = 1
        a.NeuteredDate = getdate(row[VET_ALTERED])
    if row[CAT_FIV] == "TRUE":
        a.CombiTested = 1
        a.CombiTestDate = a.DateBroughtIn
        a.CombiTestResult = row[CAT_FIV_RESULT] == "POSITIVE" and 2 or 1
    if row[CAT_FELV] == "TRUE":
        a.CombiTested = 1
        a.CombiTestDate = a.DateBroughtIn
        a.FLVResult = row[CAT_FELV_RESULT] == "POSITIVE" and 2 or 1
    a.ReasonForEntry = row[GUEST_SOURCE]
    comments = "Age: " + row[GUEST_AGE]
    comments += ", Breed: " + row[GUEST_BREED]
    comments += ", Color: " + row[GUEST_COLOR]
    comments += ", Type: " + row[GUEST_DOG]
    comments += ", PIN Tag: " + row[ADOPT_PIN_TAG]
    comments += ", Vet Exam: " + row[VET_EXAMINATION_DATE]
    comments += ", Weight: " + row[VET_WEIGHT]
    a.HiddenAnimalDetails = bs(comments)
    a.HealthProblems = bs(row[VET_TREATMENT_SUMMARY])
    a.AnimalComments = bs(row[PERS_NOTES])

    # If there are person details on the row, create a person from them
    # (checking we haven't already seen them before)
    o = None
    if strip(row, ADOPT_LAST_NAME) != "":
        personkey = strip(row, ADOPT_FIRST_NAME), strip(row, ADOPT_LAST_NAME), strip(row, ADOPT_ADDRESS)
        o = findperson(personkey)
        if o is None:
            o = asm.Owner(nextownerid)
            owners.append(o)
            nextownerid += 1
            o.OwnerForeNames = row[ADOPT_FIRST_NAME]
            o.OwnerSurname = row[ADOPT_LAST_NAME]
            o.OwnerName = o.OwnerTitle + " " + o.OwnerForeNames + " " + o.OwnerSurname
            o.OwnerAddress = row[ADOPT_ADDRESS]
            o.OwnerTown = row[ADOPT_CITY]
            o.OwnerCounty = row[ADOPT_STATE]
            o.OwnerPostcode = row[ADOPT_ZIP_CODE]
            o.EmailAddress = row[ADOPT_EMAIL]
            o.HomeTelephone = row[ADOPT_HOME_PHONE]
            o.Comments = "Drivers Lic: " + row[ADOPT_CA_DRIVERS_LICENSE]
            ownermap[personkey] = o

    # If there is an donation fee amount on the row, create one
    if getcurrency(row[ADOPT_DONATION]) > 0 and o is not None:
        od = asm.OwnerDonation(nextownerdonationid)
        ownerdonations.append(od)
        nextownerdonationid += 1
        od.OwnerID = o.ID
        od.AnimalID = a.ID
        od.MovementID = 0
        od.Comments = row[ADOPT_PAYMENT_TYPE] + " " + row[ADOPT_PAYMENT__] + " " + row[ADOPT_EXP_DATE]
        od.Date = getdate(row[ADOPT_DATE_OF_ADOPTION])
        od.Donation = getcurrency(row[ADOPT_DONATION])
        od.DonationTypeID = 1 # Donation
        od.DonationPaymentID = getpaymentmethod(row[ADOPT_PAYMENT_TYPE])

    # If there is an adoption fee amount on the row, create one.
    # NB: od deliberately holds adoption fee going into the next
    #     section so that adoptions can embellish movement id on it
    od = None
    if getcurrency(row[ADOPT_ADOPTION_FEE]) > 0 and o is not None:
        od = asm.OwnerDonation(nextownerdonationid)
        ownerdonations.append(od)
        nextownerdonationid += 1
        od.OwnerID = o.ID
        od.AnimalID = a.ID
        od.MovementID = 0
        od.Comments = row[ADOPT_PAYMENT_TYPE] + " " + row[ADOPT_PAYMENT__] + " " + row[ADOPT_EXP_DATE]
        od.Date = getdate(row[ADOPT_DATE_OF_ADOPTION])
        od.Donation = getcurrency(row[ADOPT_ADOPTION_FEE])
        od.DonationTypeID = 2 # Adoption Fee
        od.DonationPaymentID = getpaymentmethod(row[ADOPT_PAYMENT_TYPE])

    evtdate = getdate(row[ADOPT_DATE_OF_ADOPTION])

    if row[GUEST_GUEST_STATUS] == "ADOPTED":
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = o is None and 100 or o.ID
        m.MovementType = 1
        m.MovementDate = evtdate
        m.Comments = row[ADOPT_COMMENT]
        m.ReturnDate = getdate(row[ADOPT_DATE_RETURNED])
        a.Archived = 1
        a.ActiveMovementDate = evtdate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 1
        movements.append(m)
        if od is not None:
            od.MovementID = m.ID

    elif row[GUEST_GUEST_STATUS] == "AVAILABLE" or row[GUEST_GUEST_STATUS] == "FOSTER" or row[GUEST_GUEST_STATUS] == "BEHAVIOUR" or row[GUEST_GUEST_STATUS] == "EMPLOYEE PET":
        a.Archived = 0

    elif row[GUEST_GUEST_STATUS] == "INTAKE QUARANTINE":
        a.IsQuarantine = 1

    elif row[GUEST_GUEST_STATUS] == "UNAVAILABLE":
        a.IsNotAvailableForAdoption = 1

    elif row[GUEST_GUEST_STATUS] == "EUTHANIZED":
        a.Archived = 1
        a.PutToSleep = 1
        a.DeceasedDate = a.DateBroughtIn
        a.PTSReason = row[PERS_NOTES]

    elif row[GUEST_GUEST_STATUS] == "DIED IN KENNEL":
        a.Archived = 1
        a.DeceasedDate = a.DateBroughtIn
        a.PTSReason = row[PERS_NOTES]

    elif row[GUEST_GUEST_STATUS] == "DIED IN FOSTER":
        a.Archived = 1
        a.DeceasedDate = a.DateBroughtIn
        a.PTSReason = row[PERS_NOTES]

    elif row[GUEST_GUEST_STATUS] == "TRANSFERRED":
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = o is None and 100 or o.ID
        m.MovementType = 3
        m.MovementDate = evtdate
        m.Comments = row[ADOPT_COMMENT]
        m.ReturnDate = getdate(row[ADOPT_DATE_RETURNED])
        a.Archived = 1
        a.ActiveMovementDate = evtdate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 3
        movements.append(m)

    elif row[GUEST_GUEST_STATUS] == "RELEASED TO COLONY":
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.MovementType = 7
        m.MovementDate = evtdate
        m.Comments = row[GUEST_GUEST_STATUS]
        a.Archived = 1
        a.ActiveMovementDate = evtdate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 7
        movements.append(m)

    elif row[GUEST_GUEST_STATUS] == "RETURN TO OWNER" or row[GUEST_GUEST_STATUS] == "WENT BACK TO OWNER" or row[GUEST_GUEST_STATUS] == "RETURNED TO GUARDIAN":
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = o is None and 100 or o.ID
        m.MovementType = 5
        m.MovementDate = evtdate
        m.Comments = row[GUEST_GUEST_STATUS]
        a.Archived = 1
        a.ActiveMovementDate = evtdate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 5
        movements.append(m)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= %d;" % startanimalid
print "DELETE FROM owner WHERE ID >= %d;" % startownerid
print "DELETE FROM ownerdonation WHERE ID >= %d;" % startownerdonationid
print "DELETE FROM adoption WHERE ID >= %d;" % startmovementid

# Now that everything else is done, output stored records
for a in animals:
    print a
for o in owners:
    print o
for od in ownerdonations:
    print od
for m in movements:
    print m

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

