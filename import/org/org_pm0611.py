#!/usr/bin/python

import asm, csv, datetime

"""
Import script for Peter Mah 

16th December, 2014
"""

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

def getcurrency(amt):
    try:
        amt = float(amt.replace("$", ""))
        amt = amt * 100
        return int(amt)
    except Exception,err:
        #sys.stderr.write(str(err) + "\n")
        return 0

def getentryreason(rel):
    if rel == "Found": return 14
    if rel == "Owner Surrender": return 15
    if rel == "City ACO": return 16
    if rel == "Police": return 17
    if rel.startswith("Shelter Employee"): return 18
    if rel == "Neighbour": return 19
    if rel == "Seized": return 20
    return 21

def gettype(sp):
    if sp == "Canine": return 2 # Unwanted Dog
    if sp == "Feline": return 11 # Unwanted Cat
    return 13 # Misc

def gettypeletter(aid):
    tmap = {
        2: "D",
        11: "U",
        13: "M"
    }
    return tmap[aid]

def getpaymentmethod(meth):
    meth = meth.strip()
    if meth == "Visa":
        return 3
    elif meth == "M/Card":
        return 3
    elif meth == "Cheque":
        return 2
    elif meth == "Cash":
        return 1
    else:
        return 1

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

def findowner(recordnum = ""):
    """ Looks for an owner with the given name in the collection
        of owners. If one wasn't found, None is returned """
    if ownermap.has_key(recordnum):
        return ownermap[recordnum]
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
    """ Returns a date adjusted for age where age is
        a string containing a floating point number of years. """
    d = getdate(arrivaldate)
    if d == None: d = datetime.datetime.today()
    try:
        yrs = float(age)
    except:
        yrs = 0.0
    if yrs == 0: yrs = 1
    return d - datetime.timedelta(days = 365 * yrs)

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

owners = []
ownerdonations = []
movements = []
animals = []
animalcontrols = []

ownermap = {}
animalmap = {}

nextanimalid = 100
nextanimalcontrolid = 100
nextownerid = 100
nextownerdonationid = 100
nextmovementid = 100
startanimalid = 100
startanimalcontrolid = 100
startownerdonationid = 100
startownerid = 100
startmovementid = 100

unknown = asm.Owner(nextownerid)
owners.append(unknown)
nextownerid += 1
unknown.OwnerSurname = "Unknown"
unknown.OwnerName = unknown.OwnerSurname

DATE = 0
FNAME = 1
LNAME = 2
ADDRESS = 3
CITY = 4
PROV = 5
POST_CODE = 6
PHONE_1 = 7
PHONE_2 = 8
RECORD_NO = 9
COMPANY = 10
TITLE = 11
EMAIL = 12
WEB_PAGE = 13

reader = csv.reader(open("data/petermah/People.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[DATE] == "Date": continue

    o = asm.Owner(nextownerid)
    owners.append(o)
    ownermap[row[RECORD_NO]] = o
    nextownerid += 1
    o.ExtraID = getdate(row[DATE])
    o.OwnerForeNames = strip(row, FNAME)
    o.OwnerSurname = strip(row, LNAME)
    if o.OwnerSurname == "": o.OwnerSurname = "(blank)"
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = strip(row, ADDRESS)
    o.OwnerTown = strip(row, CITY)
    o.OwnerCounty = strip(row, PROV)
    o.OwnerPostcode = strip(row, POST_CODE)
    o.EmailAddress = strip(row, EMAIL)
    o.HomeTelephone = strip(row, PHONE_1)
    o.MobileTelephone = strip(row, PHONE_2)
    o.WorkTelephone = "P" + strip(row, RECORD_NO)

ARRIVAL_DATE = 0
RAPS_FILE_NO = 1
SPECIES = 2
TYPE = 3
SEX = 4
COLOUR = 5
TAG_NO = 6
TATOO = 7
CHIP = 8
AGE = 9
NAME = 10
GENERAL_CONDITION = 11
VICIOUS = 12
DANGEROUS = 13
NEUTERED = 14
REQUIRES_MEDIC = 15
MEMO = 16
PHOTO = 17
RECORD_NO = 18
FNAME = 19
LNAME = 20
ADDRESS = 21
CITY = 22
PROV = 23
POST_CODE = 24
PHONE_1 = 25
PHONE_2 = 26
RELATIONSHIP_TO_ANIMAL = 27
REASON_FOR_PICKUP = 28
LOCATION_OF_PICKUP = 29
NOTE = 30
DATE = 31
VET_CLINIC = 32
CLINIC_INVOICE = 33
PROCEDURE = 34
UNIT_PRICE = 35
MEDICATION = 36
PRICE = 37
LINE_TOT = 38
TOTAL = 39
COMMENT = 40
ANIMAL_DEPART_DATE = 41
DEPARTURE_DETAILS = 42
ANIMAL_LOCATION = 43
INVOICE_NO = 44
INVOICE_LICENSE_NO = 45
DRIVERS_LIC = 46
KENNEL_NO = 47
DATE_OF_OWNERSHIP = 48
LENGTH_OF_OWNERSHIP_YRS = 49
ORIGIN_OF_ANIMAL = 50
REASON_FOR_AQUISITION = 51
REASON_FOR_SURRENDERING = 52

lastarrival = None
reader = csv.reader(open("data/petermah/Animals.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[ARRIVAL_DATE] == "Arrival Date": continue
    if row[SPECIES].strip() == "": continue

    # Each row contains a new animal
    a = asm.Animal(nextanimalid)
    animals.append(a)
    animalmap[row[RAPS_FILE_NO]] = a
    nextanimalid += 1
    a.ExtraID = row[RAPS_FILE_NO]

    a.DateBroughtIn = getdate(row[ARRIVAL_DATE])
    if a.DateBroughtIn is not None:
        lastarrival = a.DateBroughtIn
    if a.DateBroughtIn is None:
        a.DateBroughtIn = lastarrival

    a.AnimalTypeID = gettype(row[SPECIES])
    a.generateCode(gettypeletter(a.AnimalTypeID))
    if strip(row, SPECIES) == "Canine":
        a.SpeciesID = 1
    elif strip(row, SPECIES) == "Feline":
        a.SpeciesID = 2
    else:
        a.SpeciesID = asm.species_id_for_name(row[SPECIES])
    ob = strip(row, TYPE)
    if ob.endswith("X"):
        a.Breed2ID = 442
    elif ob.find(" X") != -1:
        obs = ob.split("X")
        if len(obs) == 2:
            a.BreedID = asm.breed_id_for_name(obs[0])
            a.Breed2ID = asm.breed_id_for_name(obs[1])
        else:
            a.BreedID = asm.breed_id_for_name(ob)
    else:
        a.BreedID = asm.breed_id_for_name(ob)
    a.BreedName = asm.breed_name(a.BreedID, a.Breed2ID)
    a.Sex = getsexmf(row[SEX])
    a.BaseColourID = asm.customcolour_id_for_name(strip(row, COLOUR).replace("&", "and"), True)
    a.RabiesTag = row[TAG_NO]
    a.TattooNumber = row[TATOO]
    a.IdentichipNumber = row[CHIP]
    if a.TattooNumber.strip() != "": 
        a.Tattoo = 1
        a.TattooDate = a.DateBroughtIn
    if a.IdentichipNumber.strip() != "": 
        a.Identichipped = 1
        a.IdentichipDate = a.DateBroughtIn
    a.DateOfBirth = getdateage(row[AGE], row[ARRIVAL_DATE])
    a.AnimalName = strip(row, NAME)
    if a.AnimalName == "":
        a.AnimalName = "(unknown)"
    a.ShortCode = row[RAPS_FILE_NO]
    a.Neutered = row[NEUTERED] == "Y" and 1 or 0
    comments = ""
    if strip(row, GENERAL_CONDITION) != "": comments += "Condition: " + row[GENERAL_CONDITION]
    if strip(row, VICIOUS) != "": comments += ", Vicious: " + row[VICIOUS]
    if strip(row, DANGEROUS) != "": comments += ", Dangerous: " + row[DANGEROUS]
    a.HasSpecialNeeds = row[REQUIRES_MEDIC] == "Y" and 1 or 0
    a.HiddenAnimalDetails = bs(comments)
    a.IsNotAvailableForAdoption = 0
    # Default to animal shelter unless location has No.6 in it,
    # in which case it's the cat sanctuary
    a.ShelterLocation = 2
    if row[ANIMAL_LOCATION].find("6") != -1: a.ShelterLocation = 3
    a.AnimalComments = bs(row[MEMO])
    a.ReasonForEntry = row[REASON_FOR_SURRENDERING]
    a.EntryReasonID = getentryreason(strip(row, RELATIONSHIP_TO_ANIMAL))

    if strip(row, ANIMAL_DEPART_DATE) != "":
        a.Archived = 1

    if row[RELATIONSHIP_TO_ANIMAL] == "Owner Surrendered":
        oo = findowner(row[RECORD_NO])
        if oo is not None:
            a.OriginalOwnerID = oo.ID

    if row[DEPARTURE_DETAILS] == "Deceased":
        a.DeceasedDate = getdate(row[ANIMAL_DEPART_DATE])
    elif row[DEPARTURE_DETAILS] == "Euthanized":
        a.DeceasedDate = getdate(row[ANIMAL_DEPART_DATE])
        a.PutToSleep = 1
    elif row[ANIMAL_LOCATION] == "DOA":
        a.DeceasedDate = a.DateBroughtIn
        a.IsDOA = 1
        a.Archived = 1
    elif row[ANIMAL_LOCATION] == "Reclaimed" and strip(row, DEPARTURE_DETAILS) == "":
        # Animal is reclaimed, but we don't know who to
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = unknown.ID
        m.MovementType = 5
        m.MovementDate = a.DateBroughtIn
        a.Archived = 1
        a.ActiveMovementDate = a.DateBroughtIn
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 5
        movements.append(m)

AFR_DATE = 0
ADOPTED = 1
FOSTERED = 2
RECLAIMED = 3
RAPS_FILE_NO = 4
ANIMAL_NAME = 5
SPECIES = 6
TYPE = 7
RECORD_NO = 8
FNAME = 9
LNAME = 10
ADDRESS = 11
CITY = 12
PROV = 13
PHONE1 = 14
DATE_RETURNED = 15

reader = csv.reader(open("data/petermah/Fostered.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[ADOPTED] == "Adopted": continue

    a = findanimal("A" + row[RAPS_FILE_NO])
    if a is None: continue
    evtdate = getdate(row[AFR_DATE])
    if evtdate is None: continue
    o = findowner(row[RECORD_NO])
    if o is None: continue

    if row[ADOPTED] == "X":
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = evtdate
        m.ReturnDate = getdate(row[DATE_RETURNED])
        a.Archived = 1
        a.ActiveMovementDate = evtdate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 1
        movements.append(m)
    elif row[FOSTERED] == "X":
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 2
        m.MovementDate = evtdate
        m.ReturnDate = getdate(row[DATE_RETURNED])
        a.Archived = 1
        a.ActiveMovementDate = evtdate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 2
        movements.append(m)
    elif row[RECLAIMED] == "X":
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 5
        m.MovementDate = evtdate
        m.ReturnDate = getdate(row[DATE_RETURNED])
        a.Archived = 1
        a.ActiveMovementDate = evtdate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 5
        movements.append(m)

RECORD_NO = 0
FNAME = 1
LNAME = 2
ADDRESS = 3
CITY = 4
PROV = 5
POST_CODE = 6
PHONE_1 = 7
INVOICE_NO = 8
RAPS_FILE_NO = 9
SPECIES = 10
TYPE = 11
NAME = 12
QUANTITY = 13
PRICE = 14
PAID_BY = 15
AMT_TENDERED = 16

reader = csv.reader(open("data/petermah/Invoice.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[FNAME] == "FName": continue
    # Skip junk data
    if strip(row, AMT_TENDERED) == "": continue

    o = findowner(row[RECORD_NO])
    if o is None: continue
    a = findanimal("A" + row[RAPS_FILE_NO])

    od = asm.OwnerDonation(nextownerdonationid)
    ownerdonations.append(od)
    nextownerdonationid += 1
    od.OwnerID = o.ID
    aid = 0
    if a is not None: aid = a.ID
    od.AnimalID = aid
    od.MovementID = 0
    adate = o.ExtraID
    if a is not None: adate = a.DateBroughtIn
    od.Date = adate
    od.Donation = getcurrency(row[AMT_TENDERED])
    od.DonationTypeID = 1
    od.DonationPaymentID = getpaymentmethod(row[PAID_BY])

LOG_NO = 0
OPEN_TIME = 1
STATUS = 2
OPEN_DATE = 3
AREA = 4
CLOSE_DATE = 5
CLOSE_TIME = 6
OFFICER = 7
COMPLAINANT_FNAME = 8
LNAME = 9
P_RECORD_NO = 10
PHONE_1 = 11
PHONE = 12
DETAILS = 13

reader = csv.reader(open("data/petermah/PatrolReport.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[STATUS] == "Status": continue
    # Skip junk data
    if strip(row, OPEN_DATE) == "": continue

    ac = asm.AnimalControl(nextanimalcontrolid)
    animalcontrols.append(ac)
    nextanimalcontrolid += 1
    o = findowner(row[P_RECORD_NO])
    ac.IncidentTypeID = 11 # Imported in their DB
    ac.IncidentDateTime = getdate(row[OPEN_DATE])
    ac.CallDateTime = getdate(row[OPEN_DATE])
    ac.DispatchDateTime = getdate(row[OPEN_DATE])
    ac.CompletedDate = getdate(row[CLOSE_DATE])
    if ac.CompletedDate is not None:
        ac.IncidentCompletedID = 1
    comments = "Officer: " + row[OFFICER]
    if o is not None: ac.CallerID = o.ID
    ac.CallNotes = comments + "\n" + row[DETAILS]
    ac.DispatchAddress = row[AREA]
    ac.Sex = 2

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= %d;" % startanimalid
print "DELETE FROM animalcontrol WHERE ID >= %d;" % startanimalcontrolid
print "DELETE FROM owner WHERE ID >= %d;" % startownerid
print "DELETE FROM ownerdonation WHERE ID >= %d;" % startownerdonationid
print "DELETE FROM adoption WHERE ID >= %d;" % startmovementid
print "DELETE FROM basecolour;"

# Now that everything else is done, output stored records
for k, v in asm.customcolours.iteritems():
    print v
for a in animals:
    print a
for o in owners:
    print o
for od in ownerdonations:
    print od
for m in movements:
    print m
for ac in animalcontrols:
    print ac

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

