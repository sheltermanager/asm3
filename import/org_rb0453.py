#!/usr/bin/python

import asm, csv, datetime

# Import script for Bristol RSPCA/AccessDB
# 9th January 2014
# consists of 4 files exported access tables:
# adoption.csv, basics.csv, black.csv, claims.csv

def getsexmf(s):
    s = s.lower()
    if s.startswith("male") or s.find("tom") != -1 or s.find("dog") != -1:
        return 1
    return 0

def strip(row, index):
    s = ""
    try:
        s = row[index]
    except:
        pass
    return s.replace("NULL", "").replace("\\N", "").replace("\\", "").strip()

def getspecies(cat, typ):
    if cat == "Dog":
        return 1
    if cat == "Cat":
        return 2
    if typ != "":
        return asm.species_id_for_name(typ)
    else:
        return 1

def getbreedsp(cat, typ, breed):
    breed = breed.lower()
    typ = typ.lower()
    cat = cat.lower()
    if cat == "cat":
        speciesid = 2
        breedmap = {
            "dsh": 261,
            "d s h": 261,
            "s h d": 261,
            "d l h": 243,
            "dlh" : 243,
            "dmh" : 252,
            "slh" : 252,
            "s l h": 252,
            "burmese": 232,
            "persian": 287,
            "oriental": 286,
            "siamese": 294,
            "burman": 228,
            "birman": 228
        }
        for k, v in breedmap.iteritems():
            if breed.find(k) != -1:
                breedid = v
                return (speciesid, breedid)
        return (speciesid, 261)
    if cat == "dog":
        speciesid = 1
        breedmap = {
            "staf": 196,
            "sbt": 196,
            "s b t": 196,
            "lurcher": 443,
            "collie": 34,
            "saluki": 174,
            "gsd": 92,
            "rotti": 173,
            "russ": 114,
            "jrt": 114,
            "dane": 98,
            "lab": 125,
            "patter": 152,
            "mastif": 134,
            "shih": 188,
            "sharpei": 183, 
            "spaniel": 194
        }
        for k, v in breedmap.iteritems():
            if breed.find(k) != -1:
                breedid = v
                return (speciesid, breedid)
        return (speciesid, asm.breed_id_for_name(breed, NO_BREED_ID))
    if cat == "other":
        breespmap = {
            "rabbit": (7, 321),
            "budgie": (3, 401),
            "cockatiel": (3, 405),
            "cockateil": (3, 405),
            "chipmunk": (24, 382),
            "guinea pig": (24, 382),
            "g. pig": (24, 382),
            "g/pig": (24, 382),
            "hamster": (24, 383),
            "dove": (3, 408),
            "polecat": (24, 380),
            "ferret": (24, 380),
            "rat": (24, 387),
            "lop": (7, 343),
            "hare": (7, 321),
            "mouse": (24, 385),
            "pigeon": (3, 426),
            "canary": (3, 403),
            "finch": (3, 412),
            "hedgehog": (24, 384),
            "tortoise": (25, 1)
        }
        for k, v in breespmap.iteritems():
            if breed.find(k) != -1 or typ.find(k) != -1:
                speciesid = v[0]
                breedid = v[1]
                return (speciesid, breedid)
        # small and furry, unable to match
        return (24, 445)
    return (2, 261)

def gettypefromcardno(cardno):
    cardno = cardno.upper().strip()
    typedict = {
        "GS": 10, # typo of GD
        "CG": 11, # typo of GC
        "SC": 44, # typo of CT
        "GD": 10,
        "DW": 2,
        "MP": 41,
        "EX": 42,
        "GC": 11,
        "RS": 43,
        "CT": 44,
        "MS": 13,
        "DB": 41, #MP
        "KW": 42, #EX
        "MA": 13, #MS
        "PS": 41  #MP
    }
    return typedict[cardno[0:2]]
       
def gettypenamefromcardno(cardno):
    cardno = cardno.upper().strip()
    if cardno.startswith("DB"): return "MP"
    if cardno.startswith("KW"): return "EX"
    if cardno.startswith("MA"): return "MS"
    if cardno.startswith("PS"): return "MP"
    return cardno[0:2]

def gettypefromcattyp(cat, typ):
    if cat.lower().startswith("dog"):
        return 45
    elif cat.lower().startswith("cat"):
        return 46
    elif typ.lower().startswith("ferret"):
        return 47
    elif typ.lower().startswith("rabbit"):
        return 49
    else:
        return 48 # misc

def gettypenamefromtypeid(typeid):
    typedict = {
        45: "Dog",
        46: "Cat",
        47: "Ferret",
        48: "Misc",
        49: "Rabbit"
    }
    return typedict[typeid]

def findanimal_adopt(adopt = ""):
    if a_adopt.has_key(adopt):
        return a_adopt[adopt]
    return None

def findanimal_claim(claim = ""):
    if a_claim.has_key(claim):
        return a_claim[claim]
    return None

def findanimal_card(card = ""):
    if a_cards.has_key(card):
        return a_cards[card]
    return None

def findowner_addr(addr = ""):
    if o_addr.has_key(addr):
        return o_addr[addr]
    return None

def getdate(s, defyear = "13"):
    """ Parses a date in MM/DD/YY HH:MM:SS format. If the field is blank, None is returned """
    if s.strip() == "": return None
    if s.find(" ") != -1: s = s[0:s.find(" ")]
    b = s.split("/")
    # if we couldn't parse the date, use the first of the default year
    if len(b) < 3: return datetime.date(int(defyear) + 2000, 1, 1)
    try:
        year = int(b[2])
        if year > 70: 
            year += 1900
        else:
            year += 2000
        return datetime.date(year, int(b[0]), int(b[1]))
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
    if s.strip() == "": return 0
    try:
        return int(float(s) * 100)
    except:
        return 0

# --- START OF CONVERSION ---

owners = []
movements = []
animals = []
a_cards = {}
a_claim = {}
a_adopt = {}
o_addr = {}
donations = []

CROSSBREED_ID = 442
NO_BREED_ID = 444
NO_BREED_ID_SF = 445
startanimalid = 100
startownerid = 100
startmovementid = 100
startdonationid = 100
nextanimalid = 100
nextownerid = 100
nextmovementid = 100
nextdonationid = 100

CARD_NO = 0
SEARCH = 1
BLOCK = 2
TODAY = 3
RETURN = 4
CATEGORY = 5
TYPE_ = 6
NAME_ = 7
FINDER = 8
FIND_ADDR = 9
DATE_FOUND = 10
WHERE_FND = 11
TITLE = 12
OWNER = 13
O_ADDR_1 = 14
O_ADDR_2 = 15
O_CITY = 16
O_PCODE = 17
TELEPHONE = 18
OWNER_NTF = 19
S_OR_G = 20
BREED = 21
COLOUR = 22
SEX = 23
N_DATE = 24
ID_CHIP_NO = 25
ID_DATE = 26
RESERVE_1 = 27
RESERVE_2 = 28
ADOPT_NO = 29
CLAIM_NO = 30
DATE_DEST = 31
NOTES = 32

reader = csv.reader(open("basics.csv", "rb"), dialect="excel")
for row in reader:

    # Ignore the header
    if row[CARD_NO] == "CARD_NO": continue

    # Ignore blank card numbers
    if strip(row, CARD_NO) == "": continue

    # Each row contains a new animal
    a = asm.Animal(nextanimalid)
    animals.append(a)
    nextanimalid += 1
    comments = []
    finder = []
    def addtocomments(name, field):
        if strip(row, field) == "": return
        comments.append("%s: %s" % (name, strip(row, field)))
    def addtofinder(name, field):
        if strip(row, field) == "": return
        finder.append("%s: %s" % (name, strip(row, field)))
    addtocomments("Original breed", BREED)
    addtocomments("Search", SEARCH)
    addtocomments("Reserve1", RESERVE_1)
    addtocomments("Reserve2", RESERVE_2)
    addtocomments("Claim No", CLAIM_NO)
    addtofinder("Finder", FINDER)
    addtofinder("Find addr", FIND_ADDR)
    addtofinder("Found at", WHERE_FND)
    a.AnimalName = strip(row, NAME_)
    if a.AnimalName == "": a.AnimalName = strip(row, CARD_NO).upper()
    if a.AnimalName == "": a.AnimalName = "(blank)"
    cardno = strip(row, CARD_NO).upper()
    a.DateBroughtIn = getdate(strip(row, TODAY))
    if a.DateBroughtIn is None:
        a.DateBroughtIn = datetime.datetime.today()
    if strip(row, OWNER) != "":
        o = asm.Owner(nextownerid)
        owners.append(o)
        nextownerid += 1
        o.OwnerTitle = strip(row, TITLE)
        o.OwnerSurname = strip(row, OWNER)
        o.OwnerName = "%s %s" % (o.OwnerTitle, o.OwnerSurname)
        o.OwnerAddress = "%s\n%s" % (strip(row, O_ADDR_1), strip(row, O_ADDR_2))
        o.OwnerTown = strip(row, O_CITY)
        o.OwnerPostcode = strip(row, O_PCODE)
        o.HomeTelephone = strip(row, OWNER_NTF)
    breed = strip(row, BREED)
    category = strip(row, CATEGORY)
    atype = strip(row, TYPE_)
    #a.AnimalTypeID = gettype(cardno)
    a.AnimalTypeID = gettypefromcattyp(category, atype)
    speciesid, breedid = getbreedsp(category, atype, breed)
    a.SpeciesID = speciesid
    if breed.lower().startswith("x ") and len(breed) > 2:
        a.CrossBreed = 1
        a.Breed2ID = CROSSBREED_ID
        a.BreedID = breedid
        a.BreedName = "%s / CrossBreed" % asm.breed_name_for_id(a.BreedID)
    else:
        a.BreedID = breedid
        a.Breed2ID = a.BreedID
        a.BreedName = asm.breed_name_for_id(a.BreedID)
    a.BaseColourID = asm.colour_id_for_name(row[COLOUR], True)
    a.Sex = getsexmf(row[SEX])
    # No age/dob field, assume one year old at induction
    dob = getdate(row[TODAY])
    if dob is None: dob = datetime.datetime.today()
    dob -= datetime.timedelta(days=365)
    a.DateOfBirth = dob
    a.EstimatedDOB = 1
    a.Archived = 0
    a.PTSReasonID = 11
    a.EntryReasonID = 12
    if strip(row, DATE_DEST) != "":
        a.DeceasedDate = getdate(row[DATE_DEST])
        a.PutToSleep = 1
        a.Archived = 1
    #a.generateCode(gettypenamefromcardno(cardno))
    a.generateCode(gettypenamefromtypeid(a.AnimalTypeID))
    a.ShortCode = cardno
    a_cards[cardno] = a
    if strip(row, CLAIM_NO) != "":
        a_claim[strip(row, CLAIM_NO).lower()] = a
    if strip(row, ADOPT_NO) != "":
        a_adopt[strip(row, ADOPT_NO).lower()] = a
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 1
    a.IdentichipNumber = strip(row, ID_CHIP_NO)
    if a.IdentichipNumber.strip() != "":
        a.Identichipped = 1
    if row[ID_DATE].strip() != "":
        a.IdentichipDate = getdate(row[ID_DATE])
    a.ReasonForEntry = ", ".join(finder)
    a.AnimalComments = ", ".join(comments)
    a.IsGoodWithCats = 2
    a.IsGoodWithDogs = 2
    a.IsGoodWithChildren = 2
    a.IsHouseTrained = 2
    a.HiddenAnimalDetails = strip(row, NOTES)
    if row[SEX].find("sp") != -1 or row[SEX].find("&"):
        a.Neutered = 1
    if strip(row, N_DATE) != "":
        a.NeuteredDate = getdate(row[N_DATE])
    a.ActiveMovementType = 0
    a.ActiveMovementID = 0

REFNO = 0
DATE_ = 1
SEARCH = 2
TITLE = 3
NAME_ = 4
BL_ADDR_1 = 5
BL_ADDR_2 = 6
BL_CITY = 7
BL_PCODE = 8
NOTES = 9

# Blacklisted owners
reader = csv.reader(open("black.csv", "rb"), dialect="excel")
for row in reader:

    # Ignore the header
    if row[REFNO] == "RefNo": continue
    if strip(row, BL_ADDR_1) == "": continue

    o = findowner_addr(strip(row, BL_ADDR_1))
    if o is None:
        o = asm.Owner(nextownerid)
        nextownerid += 1
        owners.append(o)
        o.OwnerTitle = strip(row, TITLE)
        o.OwnerSurname = strip(row, NAME_)
        o.OwnerName = "%s %s" % (o.OwnerTitle, o.OwnerSurname)
        o.OwnerAddress = strip(row, BL_ADDR_1) + "\n" + strip(row, BL_ADDR_2)
        o.OwnerTown = strip(row, BL_CITY)
        o.OwnerPostcode = strip(row, BL_PCODE)
    o.IsBanned = 1
    o.AdditionalFlags += "|banned"
    o.Comments += strip(row, NOTES)

CLAIM_ID = 0
CARD_NO = 1
SEARCH = 2
TODAY = 3
CLAIM_NO = 4
CLAIM_FEE = 5
CL_DATE = 6
TITLE = 7
CL_NAME = 8
CL_ADDR1 = 9
CL_ADDR2 = 10
CL_CITY = 11
CL_PCODE = 12
TELEPHONE = 13
WK_PHONE = 14
NOTES = 15

# Reclaims
reader = csv.reader(open("claims.csv", "rb"), dialect="excel")
for row in reader:

    # Ignore the header and blanks
    if row[CLAIM_ID] == "Claim_ID": continue
    if strip(row, CARD_NO) == "": continue

    o = findowner_addr(strip(row, CL_ADDR1))
    if o is None:
        o = asm.Owner(nextownerid)
        nextownerid += 1
        owners.append(o)
        o.OwnerTitle = strip(row, TITLE)
        o.OwnerSurname = strip(row, CL_NAME)
        o.OwnerName = "%s %s" % (o.OwnerTitle, o.OwnerSurname)
        o.OwnerAddress = strip(row, CL_ADDR1) + "\n" + strip(row, CL_ADDR2)
        o.OwnerTown = strip(row, CL_CITY)
        o.OwnerPostcode = strip(row, CL_PCODE)
        o.HomeTelephone = strip(row, TELEPHONE)
        o.WorkTelephone = strip(row, WK_PHONE)
    o.Comments += strip(row, NOTES)

    # If we didn't find a matching animal, we can't do very much
    #a = findanimal_claim(strip(row, CLAIM_NO).lower())
    a = findanimal_card(strip(row, CARD_NO).upper())
    if a == None: continue

    # It's a reclaim
    if strip(row, CL_DATE) != "":
        m = asm.Movement(nextmovementid)
        movements.append(m)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 5
        m.MovementDate = getdate(row[CL_DATE])
        m.Comments = strip(row, CLAIM_NO) + " " + strip(row, NOTES)
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = m.MovementType
        a.Archived = 1

        if strip(row, CLAIM_FEE) != "" and strip(row, CLAIM_FEE) != "0":
            d = asm.OwnerDonation(nextdonationid)
            nextdonationid += 1
            d.OwnerID = o.ID
            d.MovementID = m.ID
            d.AnimalID = a.ID
            d.DonationTypeID = 6
            d.Date = getdate(row[CL_DATE])
            d.Donation = tocurrency(strip(row, CLAIM_FEE))
            d.Comments = ""
            donations.append(d)


CARD_NO = 0
SEARCH = 1
TODAY = 2
TITLE = 3
AD_NAME = 4
AD_ADDR1 = 5
AD_ADDR2 = 6
AD_CITY = 7
AD_PCODE = 8
TELEPHONE = 9
WK_PHONE = 10
RESERVE_1 = 11
RESERVE_2 = 12
REF_NO = 13
VISIT_DATE = 14
ACCEPTED = 15
VISITOR = 16
ACC_DATE = 17
ADOPT_NO = 18
ADOPT_FEE = 19
ADOPT_DATE = 20
REVISIT = 21
REVISITDATE = 22
NOTES = 23
RECORD_NUMBER = 24

# Adoptions
reader = csv.reader(open("adoption.csv", "rb"), dialect="excel")
for row in reader:

    # Ignore the header and blanks
    if strip(row, CARD_NO) == "Card_No": continue
    if strip(row, CARD_NO) == "": continue

    o = findowner_addr(strip(row, AD_ADDR1))
    if o is None:
        o = asm.Owner(nextownerid)
        nextownerid += 1
        owners.append(o)
        o.OwnerTitle = strip(row, TITLE)
        o.OwnerSurname = strip(row, AD_NAME)
        o.OwnerName = "%s %s" % (o.OwnerTitle, o.OwnerSurname)
        o.OwnerAddress = strip(row, AD_ADDR1) + "\n" + strip(row, AD_ADDR2)
        o.OwnerTown = strip(row, AD_CITY)
        o.OwnerPostcode = strip(row, AD_PCODE)
        o.HomeTelephone = strip(row, TELEPHONE)
        o.WorkTelephone = strip(row, WK_PHONE)
    if strip(row, VISIT_DATE) != "":
        o.IDCheck = 1
        o.AdditionalFlags += "|homechecked"
        o.DateLastHomeChecked = getdate(row[VISIT_DATE])
    o.Comments = strip(row, NOTES)

    # If we didn't find a matching animal, we can't do very much
    #a = findanimal_adopt(strip(row, ADOPT_NO).lower())
    a = findanimal_card(strip(row, CARD_NO).upper())
    if a == None: continue

    # It's an adoption
    if strip(row, ADOPT_DATE) != "":
        m = asm.Movement(nextmovementid)
        movements.append(m)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = getdate(row[ADOPT_DATE])
        m.Comments = strip(row, NOTES)
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = m.MovementType
        a.Archived = 1

        if strip(row, ADOPT_FEE) != "" and strip(row, ADOPT_FEE) != "0":
            d = asm.OwnerDonation(nextdonationid)
            nextdonationid += 1
            d.OwnerID = o.ID
            d.MovementID = m.ID
            d.AnimalID = a.ID
            d.DonationTypeID = 2
            d.Date = getdate(row[ADOPT_DATE])
            d.Donation = tocurrency(strip(row, ADOPT_FEE))
            d.Comments = ""
            donations.append(d)

# Fix for animals still on shelter who shouldn't be, mark them adopted to an unknown owner
unknown = asm.Owner(nextownerid)
nextownerid += 1
owners.append(unknown)
unknown.OwnerTitle = ""
unknown.OwnerSurname = "Unknown"
unknown.OwnerName = "Unknown"
for a in animals:
    if a.ActiveMovementID == 0 and a.DeceasedDate is None:
        m = asm.Movement(nextmovementid)
        movements.append(m)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = unknown.ID
        m.MovementType = 1
        m.MovementDate = a.DateBroughtIn + datetime.timedelta(days=31)
        m.Comments = "Auto return"
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = m.MovementType
        a.ActiveMovementDate = m.MovementDate
        a.Archived = 1

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= %d;" % startanimalid
print "DELETE FROM owner WHERE ID >= %d;" % startownerid
print "DELETE FROM adoption WHERE ID >= %d;" % startmovementid
print "DELETE FROM ownerdonation WHERE ID >= %d;" % startdonationid
print "DELETE FROM configuration WHERE ItemName LIKE 'DBViewSeq%';"
print "DELETE FROM media;"
print "DELETE FROM dbfs WHERE Path LIKE '/animal/%';"
print "DELETE FROM animaldiet;"
print "DELETE FROM animalcost;"
print "DELETE FROM animalmedical;"
print "DELETE FROM animalmedicaltreatment;"
print "DELETE FROM animaltest;"
print "DELETE FROM animalvaccination;"
print "DELETE FROM diary;"
print "DELETE FROM log;"
print "VACUUM FULL dbfs;"

# Now that everything else is done, output stored records
for a in animals:
    print a
for o in owners:
    print o
for m in movements:
    print m
for d in donations:
    print d

print "UPDATE animal SET BreedID = 444 WHERE BreedID NOT IN (SELECT ID FROM breed);"
print "UPDATE animal SET Breed2ID = 444 WHERE Breed2ID NOT IN (SELECT ID FROM breed);"
print "UPDATE animal SET BreedName = 'Unable to match Access data' WHERE BreedID = 444 OR Breed2ID = 444 OR BreedID = 445 OR Breed2ID = 445;"
print "UPDATE animal SET BreedName = 'Lurcher' WHERE BreedID = 443;"
print "UPDATE animal SET yearcodeid = 0;"

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

