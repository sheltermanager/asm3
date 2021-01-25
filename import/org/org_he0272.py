#!/usr/bin/python

import asm, csv, sys, datetime

# Import script for Happy Endings Rescue
# 11th Jan, 2013

# For use with fields that just contain the sex
def getsexmf(s):
    if s.find("Male") != -1:
        return 1
    elif s.find("Female") != -1:
        return 0
    elif s.find("Bitch") != -1:
        return 0
    elif s.find("Geld") != -1:
        return 0
    elif s.find("Mare") != -1:
        return 0
    elif s.find("Colt") != -1:
        return 1
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
    spmap = {
        "Canine": 2,
        "Feline": 11,
        "Equine": 41,
        "Rabbit": 42,
        "Donkey": 41
    }
    if spmap.has_key(species):
        return spmap[species]
    else:
        return 2

def gettypeletter(aid):
    tmap = {
        2: "D",
        11: "C",
        41: "H",
        42: "R"
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
    """ Parses a date in YYYY/MM/DD format. If the field is blank or not a date, None is returned """
    if s.strip() == "": return None
    if s.find("/") == -1: return None
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
    """ Returns a date adjusted for age. age can be a date,
        a number and mnth or yr (default is yr if none supplied) """
    # is age a date? Use it if so
    d = getdate(age)
    if d != None: 
        return d
    # Nope, is arrivaldate a date? Use today if not
    d = getdate(arrivaldate)
    if d == None: d = datetime.datetime.today()
    # Let's have a look at the age token now to get our
    # units and amount
    units = "Y"
    amt = 1
    if age.find("mnth") != -1: units = "M"
    if age.find("wk") != -1: units = "W"
    amt = "".join(c for c in age if c.isdigit())
    amt = amt.strip()
    if amt == "": amt = "0"
    dys = 0
    if units == "W": dys = (int(amt) * 7)
    if units == "M": dys = (int(amt) * 31)
    if units == "Y": dys = (int(amt) * 365)
    d = d - datetime.timedelta(days = dys)
    return d

def tocurrency(s):
    if s.strip() == "": return 0.0
    s = s.replace("$", "")
    try:
        return float(s)
    except:
        return 0.0

# --- START OF CONVERSION ---

print "\\set ON_ERROR_STOP\nBEGIN;"

owners = []
movements = []
animals = []
donations = []

nextanimalid = 100
nextownerid = 100
nextmovementid = 100
nextdonationid = 100
startanimalid = 100
startownerid = 100
startmovementid = 100
startdonationid = 100

NAME = 0
TYPE = 1
SEX = 2
BREED = 3
SIZE = 4
COLOUR = 5
AGE = 6
CHIP_NUMBER = 7
PASSPORT_NO = 8
PASSPORT_NAME = 9
RESCUE_DATE = 10
TITLE = 11
FIRST_NAME = 12
SURNAME = 13
ADDRESS1 = 14
ADDRESS2 = 15
TOWN = 16
COUNTY = 17
POSTCODE = 18
TELEPHONE_1 = 19
TELEPHONE_2 = 20
EMAIL = 21
ADOPTION_DATE = 22
ADOPTION_FEE = 23
CARD = 24

reader = csv.reader(open("he0272_adopted.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[NAME] == "Name": continue

    # Each row contains a new animal, owner and adoption
    a = asm.Animal(nextanimalid)
    animals.append(a)
    nextanimalid += 1
    a.AnimalTypeID = gettype(row[TYPE])
    a.SpeciesID = asm.species_id_for_name(row[TYPE])
    a.AnimalName = row[NAME]
    a.DateOfBirth = getdateage(row[AGE], row[ADOPTION_DATE])
    a.DateBroughtIn = getdate(row[RESCUE_DATE])
    if a.DateBroughtIn == None: a.DateBroughtIn = getdate(row[ADOPTION_DATE])
    if a.DateBroughtIn == None: a.DateBroughtIn = getdate("2012/12/01")
    a.generateCode(gettypeletter(a.AnimalTypeID))
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 1
    a.Sex = getsexmf(row[SEX])
    a.Size = getsize(row[SIZE])
    a.BaseColourID = asm.colour_id_for_name(row[COLOUR], True)
    comments = "Original breed: " + row[BREED] + ", original sex: " + row[SEX] + ", original age: " + row[AGE]
    a.BreedID = asm.breed_id_for_name(row[BREED])
    a.Breed2ID = a.BreedID
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    a.IdentichipNumber = row[CHIP_NUMBER]
    a.TattooNumber = row[PASSPORT_NO]
    comments += ", Passport: " + row[PASSPORT_NAME] + " " + row[PASSPORT_NO]
    a.HiddenAnimalDetails = comments
    a.Archived = 1

    o = asm.Owner(nextownerid)
    owners.append(o)
    nextownerid += 1
    o.OwnerTitle = row[TITLE]
    o.OwnerForeNames = row[FIRST_NAME]
    o.OwnerSurname = row[SURNAME]
    o.OwnerName = o.OwnerTitle + " " + o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = row[ADDRESS1] + "\n" + row[ADDRESS2]
    o.OwnerTown = row[TOWN]
    o.OwnerCounty = row[COUNTY]
    o.OwnerPostcode = row[POSTCODE]
    o.EmailAddress = row[EMAIL]
    o.HomeTelephone = row[TELEPHONE_1]
    o.MobileTelephone = row[TELEPHONE_2]

    m = asm.Movement(nextmovementid)
    nextmovementid += 1
    m.AnimalID = a.ID
    m.OwnerID = o.ID
    m.MovementType = 1
    m.MovementDate =  getdate(row[ADOPTION_DATE])
    if row[ADOPTION_FEE].strip() != "":
        m.Comments = "Adoption Fee: " + row[ADOPTION_FEE]
    a.Archived = 1
    a.ActiveMovementID = m.ID
    a.ActiveMovementType = 1
    movements.append(m)

    if row[ADOPTION_FEE].strip() != "":
        d = asm.OwnerDonation(nextdonationid)
        nextdonationid += 1
        d.OwnerID = o.ID
        d.MovementID = m.ID
        d.AnimalID = a.ID
        d.DonationTypeID = 2
        d.Date = getdate(row[ADOPTION_DATE])
        d.Donation = int(tocurrency(row[ADOPTION_FEE]) * 100)
        donations.append(d)

TITLE = 0
FIRST_NAME = 1
SURNAME = 2
ADDRESS_LINE_1 = 3
ADDRESS_LINE_2 = 4
TOWN = 5
COUNTY = 6
POSTCODE = 7
TELEPHONE = 8
EMAIL_ADDRESS = 9
GIFT_AID = 10
ADOPTEE = 11
DONATION1 = 12
DATE1 = 13
COMMENT1 = 14
DONATION2 = 15
DATE2 = 16
COMMENT2 = 17
DONATION3 = 18
DATE3 = 19
COMMENT3 = 20
DONATION4 = 21
DATE4 = 22
COMMENT4 = 23
DONATION5 = 24
DATE5 = 25
COMMENT5 = 26
DONATION6 = 27
DATE6 = 28
COMMENT6 = 29
DONATION7 = 30
DATE7 = 31
COMMENT7 = 32

def add_donation(donationdate, ownerid, amount, comment):
    """
    Adds a donation
    """
    global nextdonationid
    ddate = getdate(donationdate)
    if ddate == None: return
    if amount.strip() == "": return
    d = asm.OwnerDonation(nextdonationid)
    nextdonationid += 1
    d.OwnerID = ownerid
    d.MovementID = 0
    d.AnimalID = 0
    d.DonationTypeID = 1
    d.Date = ddate
    d.Donation = int(tocurrency(amount) * 100)
    d.Comments = comment
    donations.append(d)

reader = csv.reader(open("he0272_supporters.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[TITLE] == "Title": continue
    if row[FIRST_NAME].strip() == "" and row[ADDRESS_LINE_1].strip() == "" and row[SURNAME].strip() == "": break

    o = asm.Owner(nextownerid)
    owners.append(o)
    nextownerid += 1
    o.OwnerTitle = row[TITLE]
    o.OwnerForeNames = row[FIRST_NAME]
    o.OwnerSurname = row[SURNAME]
    o.OwnerName = o.OwnerTitle + " " + o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = row[ADDRESS_LINE_1] + "\n" + row[ADDRESS_LINE_2]
    o.OwnerTown = row[TOWN]
    o.OwnerCounty = row[COUNTY]
    o.OwnerPostcode = row[POSTCODE]
    o.EmailAddress = row[EMAIL_ADDRESS]
    o.HomeTelephone = row[TELEPHONE]
    o.IsGiftAid = row[GIFT_AID].find("X") != -1 and 1 or 0

    # Create each donation if necessary
    add_donation(row[DATE1], o.ID, row[DONATION1], row[COMMENT1])
    add_donation(row[DATE2], o.ID, row[DONATION2], row[COMMENT2])
    add_donation(row[DATE3], o.ID, row[DONATION3], row[COMMENT3])
    add_donation(row[DATE4], o.ID, row[DONATION4], row[COMMENT4])
    add_donation(row[DATE5], o.ID, row[DONATION5], row[COMMENT5])
    add_donation(row[DATE6], o.ID, row[DONATION6], row[COMMENT6])
    add_donation(row[DATE7], o.ID, row[DONATION7], row[COMMENT7])


print "DELETE FROM animal WHERE ID >= %d;" % startanimalid
print "DELETE FROM owner WHERE ID >= %d;" % startownerid
print "DELETE FROM adoption WHERE ID >= %d;" % startmovementid
print "DELETE FROM ownerdonation WHERE ID >= %d;" % startdonationid

# Now that everything else is done, output stored records
for a in animals:
    print a
for o in owners:
    print o
for m in movements:
    print m
for d in donations:
    print d

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"
