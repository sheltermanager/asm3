#!/usr/bin/python

import asm, csv, sys, datetime

# Import script for Cornwall RSPCA/VetRescue
# 10th January 2013

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

def gettype(species):
    spmap = {
        "Canine": 9,
        "Feline": 4,
        "SmallDomestic": 11,
        "WaterBird": 6,
        "CaptiveBird": 19,
        "Rabbit": 19,
        "WildMammal": 6,
        "WildBird": 6,
        "CaptiveExotic": 19,
        "FarmBird": 6
    }
    if spmap.has_key(species):
        return spmap[species]
    else:
        return 1

def getspecies(species, breed):
    spmap = [
        ("Canine", "", 1),
        ("Feline", "", 2),
        ("SmallDomestic", "Rat", 5),
        ("SmallDomestic", "Ferret", 9),
        ("SmallDomestic", "Gerbil", 18),
        ("SmallDomestic", "Guinea", 20),
        ("WaterBird", "", 3),
        ("WildBird", "", 3),
        ("FarmBird", "", 3),
        ("WildMammal", "", 6),
        ("Rabbit", "", 7),
        ("CaptiveExotic", "", 29)
    ]
    for spn, brn, sid in spmap:
        if brn == "" and spn.find(species) != -1:
            return sid
        elif brn.find(breed) != -1 and spn.find(species) != -1:
            return sid
    return 1

def findanimal(petref = ""):
    """ Looks for an animal with the given extra id in the collection
        of animals. If one wasn't found, None is returned """
    for a in animals:
        if a.ExtraID == petref.strip():
            return a
    return None

def findowner(xid = ""):
    """ Looks for an owner with the given extra id in the collection
        of owners. If one wasn't found, None is returned """
    for o in owners:
        if o.ExtraID == xid.strip():
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

ANIMALID = 0
CUSTCODE = 1
PETNUMCODE = 2
PETNAME = 3
SPECIES = 4
BREED = 5
COLOUR = 6
DOB = 7
INSURANCE = 8
INSDATEREGISTERED = 9
WEIGHT = 10
SEX = 11
ANIMALPORT = 12
REFERRAL = 13
DATEREGISTERED = 14
WEIGHTHIGH = 15
WEIGHTLOW = 16
VACCDATE = 17
ANIMALSTATUS = 18
VACCDATE2 = 19
POSTIT = 20
ALLERGY = 21
OTHER = 22
INSURANCENAME = 23
POLICYNUMBER = 24
EMERGENCY = 25
IDNUM = 26
RESCUE = 27
PETREF = 28
ENTRYREASON = 29
TATTOO = 30
UTILREF = 31
RESERVED = 32
RESCUSTCODE = 33
DATEFOUND = 34
WELFARE = 35
STRAY = 36
VACCINATED = 37
HANDOVERNOTE = 38
GENNOTE = 39
TS = 40
COSTCENTRE = 41
WILD = 42
ONSITE = 43
AGEEST = 44
MICRODATE = 45
LOGG = 46
STRAYLOC = 47
BEHTYPE = 48
REDCARD = 49
ANIMALST = 50

reader = csv.reader(open("rc0266_animal.csv", "rb"), dialect="excel")
for row in reader:

    # Ignore the header and blanks
    if row[ANIMALID] == "AnimalID": continue
    if len(row) <= MICRODATE: continue
    if row[ANIMALID].strip() == "": break

    # Each row contains a new animal
    a = asm.Animal(nextanimalid)
    animals.append(a)
    nextanimalid += 1
    comments = "%s, Species: %s, Breed: %s, Insurance: %s %s %s %s, Weight: %s, WeightHigh: %s, WeightLow: %s, VaccDate: %s %s, StrayLoc: %s" % (
        strip(row, POSTIT), strip(row, SPECIES), strip(row, BREED), strip(row, INSURANCE), strip(row, INSURANCENAME), strip(row, POLICYNUMBER), 
        strip(row, INSDATEREGISTERED), strip(row, WEIGHT), strip(row, WEIGHTHIGH), strip(row, WEIGHTLOW), 
        strip(row, VACCDATE), strip(row, VACCDATE2), strip(row, STRAYLOC))
    a.AnimalName = strip(row, PETNAME)
    a.AnimalTypeID = gettype(row[SPECIES])
    a.SpeciesID = getspecies(row[SPECIES], row[BREED])
    a.BreedID = asm.breed_id_for_name(row[BREED])
    a.Breed2ID = a.BreedID
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    a.BaseColourID = asm.colour_id_for_name(row[COLOUR], True)
    dob = row[DOB]
    if dob.find("/") == -1: dob = row[DATEREGISTERED]
    a.DateOfBirth = getdate(dob)
    a.DateBroughtIn = getdate(row[DATEREGISTERED])
    if a.DateBroughtIn == None:
        a.DateBroughtIn = getdate("2012/12/31")
    a.Sex = getsexmf(row[SEX])
    if row[PETREF].strip() != "":
        a.ShelterCode = str(a.DateBroughtIn.year) + row[PETREF]
        a.ShortCode = row[PETREF]
        a.ExtraID = row[PETREF]
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 1
    a.IdentichipNumber = strip(row, IDNUM)
    if a.IdentichipNumber.strip() != "":
        a.Identichipped = 1
    if row[MICRODATE].strip() != "":
        a.IdentichipDate = getdate(row[MICRODATE])
    a.ReasonForEntry = strip(row, ENTRYREASON)
    a.AnimalComments = strip(row, GENNOTE)
    a.HiddenAnimalDetails = comments
    if row[SEX].find("euter") != -1:
        a.Neutered = 1
    a.Archived = 0
    a.ActiveMovementType = 0
    a.ActiveMovementID = 0

DUMMY = 0
CUSTCODE = 1
TITLE = 2
FIRST = 3
LAST = 4
AD = 5
AD1 = 6
AD2 = 7
COUNTY = 8
POSTC = 9
HOMEP = 10
WORKP = 11
KEEPERDATE = 12
POSTIT = 13
MOBILE = 14
ASSESSREF = 15
PETREF = 16
KEEPERSTAT = 17
MEMBERNO = 18
MENBERTYPE = 19
VOTE = 20
MEMBERFEE = 21
DATEOFMEM = 22
RENEWALDATE = 23
PRESENTKEEPER = 24
REASONFORENTRY = 25
MAILSHOTS = 26
BANDING = 27
BANDDATE = 28
BANDCHANGE = 29
SECOND = 30
TS = 31
EXPDATEY = 32
EXPDATE = 33
STOPPED = 34
LOGON = 35
CLASS = 36
EMAIL = 37
EMERNO = 38
EXPORTED = 39
ORGOWNER = 40
KEEPERTYPE = 41
CLISTAT = 42
STOPNOTE = 43
NOVAT = 44

reader = csv.reader(open("rc0266_keeper.csv", "rb"), dialect="excel")
for row in reader:

    # Ignore the header and blanks
    if row[DUMMY] == "Dummy": continue
    if row[CUSTCODE].strip() == "": break

    # Find the matching animal
    a = findanimal(row[PETREF])

    # Do we already have this owner?
    o = findowner(row[CUSTCODE])
    if o == None:
        o = asm.Owner(nextownerid)
        nextownerid += 1
        owners.append(o)
        o.ExtraID = row[CUSTCODE]
        o.OwnerTitle = strip(row, TITLE)
        o.OwnerForeNames = strip(row, FIRST)
        o.OwnerSurname = strip(row, LAST)
        o.OwnerAddress = strip(row, AD) + "\n" + strip(row, AD1)
        o.OwnerTown = strip(row, AD2)
        o.OwnerCounty = strip(row, COUNTY)
        o.OwnerPostcode = strip(row, POSTC)
        o.HomeTelephone = strip(row, HOMEP)
        o.WorkTelephone = strip(row, WORKP)
        comments = "%s, Keeper date: %s, CustCode: %s" % ( strip(row, POSTIT), row[KEEPERDATE], row[CUSTCODE] )
        o.Comments = comments

    # If we didn't find a matching animal, we can't do very much
    if a == None: continue

    # What kind of movement is this row?
    if row[ORGOWNER].find("\\N") == -1:
        # It's an original owner - update the animal record
        a.OriginalOwnerID = o.ID
        a.ReasonForEntry += " " + strip(row, REASONFORENTRY)
    elif row[KEEPERTYPE] == "New Keeper":
        # It's an adoption
        m = asm.Movement(nextmovementid)
        movements.append(m)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = getdate(row[KEEPERDATE])
        m.Comments = strip(row, REASONFORENTRY)
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = m.MovementType
        a.Archived = 1
    elif row[KEEPERTYPE] == "Transfer":
        # It's a transfer
        m = asm.Movement(nextmovementid)
        movements.append(m)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 3
        m.MovementDate = getdate(row[KEEPERDATE])
        m.Comments = strip(row, REASONFORENTRY)
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = m.MovementType
        a.Archived = 1
    elif row[KEEPERTYPE] == "Return to Original Owner":
        # It's a reclaim
        m = asm.Movement(nextmovementid)
        movements.append(m)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 5
        m.MovementDate = getdate(row[KEEPERDATE])
        m.Comments = strip(row, REASONFORENTRY)
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = m.MovementType
        a.Archived = 1

# Now go through the remaining animals - do we have any wildlife
# with no active movement? If so, auto return it after a month to
# stop them screwing up our figures
for a in animals:
    if a.ActiveMovementID == 0 and a.SpeciesID == 3:
        m = asm.Movement(nextmovementid)
        movements.append(m)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = 0
        m.MovementType = 7
        m.MovementDate = a.DateBroughtIn + datetime.timedelta(days=31)
        m.Comments = "Auto return"
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = m.MovementType
        a.Archived = 1

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

