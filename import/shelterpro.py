#!/usr/bin/python

import asm, csv, datetime, sys, os, base64

"""
Import script for Shelterpro databases exported as CSV
(requires shelter.csv, animal.csv, person.csv, address.csv, addrlink.csv, vacc.csv)

Will also look in PATH/images/ANIMALKEY.[jpg|JPG] for animal photos if available.

6th Oct, 2014 - 8th Jan, 2015
"""

PATH = "data/shelterpro_porter"

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

def firstw(s):
    if s is None: 
        return ""
    elif s.find(" ") != -1:
        return s[0:s.find(" ")]
    else:
        return s

def gettype(animaldes):
    spmap = {
        "DOG": 2,
        "CAT": 11
    }
    species = animaldes.split(" ")[0]
    if spmap.has_key(species):
        return spmap[species]
    else:
        return 2

def gettypeletter(aid):
    tmap = {
        2: "D",
        11: "U"
    }
    return tmap[aid]

def getsize(size):
    if size == "VERY":
        return 0
    elif size == "LARGE":
        return 1
    elif size == "MEDIUM":
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

def findowner(personkey = ""):
    """ Looks for an owner with the given name in the collection
        of owners. If one wasn't found, None is returned """
    for o in owners:
        if o.ExtraID == personkey.strip():
            return o
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
animalvaccinations = []

addresses = {}
addrlink = {}

nextanimalid = 100
nextanimalvaccinationid = 100
nextownerid = 100
nextmovementid = 100
nextmediaid = 100
nextdbfsid = 300
startanimalid = 100
startanimalvaccinationid = 100
startownerid = 100
startmovementid = 100
startmediaid = 100
startdbfsid = 300

# Remove existing
print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= %d;" % startanimalid
print "DELETE FROM animalvaccination WHERE ID >= %d;" % startanimalvaccinationid
print "DELETE FROM owner WHERE ID >= %d;" % startownerid
print "DELETE FROM adoption WHERE ID >= %d;" % startmovementid
print "DELETE FROM media WHERE ID >= %d;" % startmediaid
print "DELETE FROM dbfs WHERE ID >=%d;" % startdbfsid

# Create a transfer owner
o = asm.Owner(nextownerid)
owners.append(o)
nextownerid += 1
o.OwnerSurname = "Other Shelter"
o.OwnerName = o.OwnerSurname

ANIMALKEY = 0
PERSOWNR = 1
ANIMLDES = 2
BREED1 = 3
PUREBRED = 4
GENDER = 5
FIX = 6
AGE = 7
WEIGHT = 8
FURCOLR1 = 9
FURCOLR2 = 10
COLLRTYP = 11
COLLRCOL = 12
LICENSE = 13
VACC = 14
DECLAWED = 15
PETNAME = 16
RET_FIX = 17
VACDATE = 18
MEMO = 19
MICROCHIP = 20
STATUS = 21
CROSSBREED = 22
DOB = 23
COAT = 24
FURPATTERN = 25
TAIL = 26
REGISTRATI = 27
TATOO = 28
DANGEROUS = 29
BITES = 30
PERSVET = 31
LICENSEKEY = 32
MICROCHPKE = 33
VACCKEY = 34
REGISTKEY = 35
RET_LIC = 36
RET_VACC = 37
ADDEDBYUSE = 38
ADDEDDATET = 39
LASTUSERTO = 40
LASTSAVEDA = 41
BEH_HOUSEB = 42
BEH_SPECNE = 43
BEH_GOODWK = 44
BEH_GOODWC = 45
BEH_GOODWD = 46
BEH_ADOPTA = 47
BEH_AGGRES = 48
BEH_SUBMIS = 49
BEH_DOMINA = 50
BEH_SHY = 51
BEH_NOISY = 52
BEH_QUIET = 53
BEH_AFRAID = 54
BEH_MUSTUS = 55
BEH_LIKESL = 56
BEH_PLAYFU = 57
BEH_REQEXE = 58
BEH_LIKESG = 59
BEH_GETSLO = 60
BEH_DIGS = 61
BEH_ENERGE = 62
BEH_NERVOU = 63
BEH_FRIEND = 64
BEH_EASYGO = 65
BEH_PROTEC = 66
BEH_CLAWS = 67
BEH_CHEWS = 68
BEH_JUMPS = 69
BEH_CHASES = 70
BEH_LIKESC = 71
BEH_KEPTIN = 72
BEH_KEPTOU = 73
BEH_TAG1 = 74
BEH_VALUE1 = 75
BEH_TAG2 = 76
BEH_VALUE2 = 77
BEH_TAG3 = 78
BEH_VALUE3 = 79
BEH_TAG4 = 80
BEH_VALUE4 = 81
BEH_TAG5 = 82
BEH_VALUE5 = 83
BEH_TAG6 = 84
BEH_VALUE6 = 85
BEH_TAG7 = 86
BEH_VALUE7 = 87
BEH_TAG8 = 88
BEH_VALUE8 = 89
BEH_TAG9 = 90
BEH_VALUE9 = 91
BEH_TAG10 = 92
BEH_VALU10 = 93
BEH_TAG11 = 94
BEH_VALU11 = 95
BEH_TAG12 = 96
BEH_VALU12 = 97
BEH_TAG13 = 98
BEH_VALU13 = 99
BEH_TAG14 = 100
BEH_VALU14 = 101
BEH_TAG15 = 102
BEH_VALU15 = 103
BEH_TAG16 = 104
BEH_VALU16 = 105
BEH_TAG17 = 106
BEH_VALU17 = 107
BEH_TAG18 = 108
BEH_VALU18 = 109
BEH_TAG19 = 110
BEH_VALU19 = 111
BEH_TAG20 = 112
BEH_VALU20 = 113
BEH_TAG21 = 114
BEH_VALU21 = 115
BEH_TAG22 = 116
BEH_VALU22 = 117

# Start with the animal file
reader = csv.reader(open(PATH + "/animal.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[ANIMALKEY] == "ANIMALKEY": continue

    # Each row contains a new animal, owner and adoption
    a = asm.Animal(nextanimalid)
    animals.append(a)
    nextanimalid += 1
    a.ExtraID = row[ANIMALKEY]
    a.AnimalTypeID = gettype(row[ANIMLDES])
    a.SpeciesID = asm.species_id_for_name(row[ANIMLDES].split(" ")[0])
    a.AnimalName = row[PETNAME]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    age = row[AGE].split(" ")[0]
    a.DateOfBirth = getdateage(age, row[ADDEDDATET])
    a.DateBroughtIn = getdate(row[ADDEDDATET])
    if a.DateBroughtIn is None:
        sys.stderr.write("Bad datebroughtin: '%s'\n" % row[ADDEDDATET])
        a.DateBroughtIn = datetime.datetime.today()    
    a.EntryReasonID = 4
    a.generateCode(gettypeletter(a.AnimalTypeID))
    a.Neutered = cint(row[FIX])
    a.Declawed = cint(row[DECLAWED])
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 1
    a.Sex = getsexmf(firstw(row[GENDER]))
    a.Size = getsize(firstw(row[WEIGHT]))
    a.BaseColourID = asm.colour_id_for_names(firstw(row[FURCOLR1]), firstw(row[FURCOLR2]))
    a.IdentichipNumber = row[MICROCHIP]
    comments = "Original breed: " + row[BREED1] + "/" + row[CROSSBREED] + ", age: " + age
    comments += ",Color: " + firstw(row[FURCOLR1]) + "/" + firstw(row[FURCOLR2])
    comments += ", Coat: " + row[COAT]
    comments += ", Collar: " + row[COLLRTYP]
    a.BreedID = asm.breed_id_for_name(row[BREED1])
    a.Breed2ID = a.BreedID
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    if row[PUREBRED] == "0":
        a.Breed2ID = asm.breed_id_for_name(row[CROSSBREED])
        if a.Breed2ID == 1: a.Breed2ID = 442
        a.BreedName = "%s / %s" % ( asm.breed_name_for_id(a.BreedID), asm.breed_name_for_id(a.Breed2ID) )
    a.HiddenAnimalDetails = comments
    a.Archived = 1

    # Does this animal have an image? If so, add media/dbfs entries for it
    imdata = None
    if os.path.exists(PATH + "/images/%s.jpg" % row[ANIMALKEY]):
        f = open(PATH + "/images/%s.jpg" % row[ANIMALKEY], "rb")
        imdata = f.read()
        f.close()
    elif os.path.exists(PATH + "/images/%s.JPG" % row[ANIMALKEY]):
        f = open(PATH + "/images/%s.JPG" % row[ANIMALKEY], "rb")
        imdata = f.read()
        f.close()
    if imdata is not None:
        encoded = base64.b64encode(imdata)
        medianame = str(nextmediaid) + '.jpg'
        print "INSERT INTO media (id, medianame, medianotes, websitephoto, docphoto, newsincelastpublish, updatedsincelastpublish, " \
            "excludefrompublish, linkid, linktypeid, recordversion, date) VALUES (%d, '%s', %s, 1, 1, 0, 0, 0, %d, 0, 0, %s);" % \
            ( nextmediaid, medianame, asm.ds(""), a.ID, asm.dd(a.DateBroughtIn) )
        print "INSERT INTO dbfs (id, name, path, content) VALUES (%d, '%s', '%s', '');" % ( nextdbfsid, str(a.ID), '/animal' )
        nextdbfsid += 1
        print "INSERT INTO dbfs (id, name, path, content) VALUES (%d, '%s', '%s', '%s');" % (nextdbfsid, medianame, "/animal/" + str(a.ID), encoded)
        nextmediaid += 1
        nextdbfsid += 1

VACCKEY = 0
VACCOWNER = 1
ANIMALKEY = 2
VACC = 3
VACCTYPE = 4
VACCEFFECT = 5
VACCEXPIRA = 6
VACCRENEWA = 7
VACCRENEW2 = 8
VACCPRECIN = 9
VACCISSUER = 10
VACCSTAFF = 11
MEDICATEKE = 12
VACCISSUED = 13
VACCMANUFA = 14
VACCDRUGNA = 15
VACCLOTNUM = 16
VACCSERIAL = 17
ADDEDBYUSE = 18
ADDEDDATET = 19
LASTUSERTO = 20
LASTSAVEDA = 21
EDITSPASSE = 22
BATCHPOSTD = 23
VERIFICATI = 24

# Vaccinations
reader = csv.reader(open(PATH + "/vacc.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[ANIMALKEY] == "ANIMALKEY": continue

    a = findanimal(row[ANIMALKEY])
    if a is None: continue

    # Each row contains a vaccination
    av = asm.AnimalVaccination(nextanimalvaccinationid)
    animalvaccinations.append(av)
    nextanimalvaccinationid += 1
    vaccdate = getdate(row[VACCEFFECT])
    if vaccdate is None:
        vaccdate = a.DateBroughtIn
    av.AnimalID = a.ID
    av.VaccinationID = 8
    if row[VACCTYPE].find("DHLPP") != -1: av.VaccinationID = 8
    if row[VACCTYPE].find("BORDETELLA") != -1: av.VaccinationID = 6
    if row[VACCTYPE].find("RABIES") != -1: av.VaccinationID = 4
    av.DateRequired = vaccdate
    av.DateOfVaccination = vaccdate
    av.Manufacturer = row[VACCMANUFA]
    av.BatchNumber = row[VACCSERIAL]
    av.Comments = "Name: %s, Issue: %s" % (row[VACCDRUGNA], row[VACCISSUED])

ADDRESSKEY = 0
ADDRESSSTR = 1
ADDRESSST2 = 2
ADDRESSST3 = 3
ADDRESSST4 = 4
ADDRESSSEC = 5
ADDRESSCIT = 6
ADDRESSSTA = 7
ADDRESSPOS = 8
ADDRESSISC = 9
ADDRESSCOU = 10
ADDRESSCTR = 11
ADDRESSLOC = 12
ADDRESSPRE = 13
ADDRESSVER = 14
ADDRESSBAD = 15
ADDEDBYUSE = 16
ADDEDDATET = 17
LASTUSERTO = 18
LASTSAVEDA = 19

# Next, addresses
reader = csv.reader(open(PATH + "/address.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[ADDRESSKEY] == "ADDRESSKEY": continue
    
    addresses[row[ADDRESSKEY]] = {
        "address": row[ADDRESSSTR] + " " + row[ADDRESSST2] + " " + row[ADDRESSST3],
        "city": row[ADDRESSCIT],
        "state": row[ADDRESSSTA],
        "zip": row[ADDRESSPOS]
    }

PERSONKEY = 1
ADDRESSKEY = 3

# The link between addresses and people
reader = csv.reader(open(PATH + "/addrlink.csv", "r"), dialect="excel")
for row in reader:
    # Skip the header
    if row[PERSONKEY] == "EVENTKEY": continue
    addrlink[row[PERSONKEY]] = row[ADDRESSKEY]


PERSONKEY = 0
HOME_PH = 1
DRIV_LIC = 2
NAME = 3
FNAME = 4
MNAME = 5
LNAME = 6
WORK_PH = 7
ACO_IND = 8
STAFF_IND = 9
EUTH_IND = 10
VOL_IND = 11
DONOR_IND = 12
MEMBER_IND = 13
MEMO = 14
NOADOPT = 15
EMAIL = 16
BIRTH = 17
THIRD_PH = 18
RECORDTYPE = 19
VETCLINIC = 20
VETERINARI = 21
VACCISSUER = 22
LICENSEISS = 23
REGISTERIS = 24
CHARGEBACK = 25
DISABLED = 26
SENIOR = 27
FOSTERS = 28
MAILINGSAM = 29
ADDEDBYUSE = 30
ADDEDDATET = 31
LASTUSERTO = 32
LASTSAVEDA = 33
LOCATION_I = 34
PRECINCT = 35
EMAIL2 = 36
EMAIL3 = 37
CUSTOM1_IN = 38
CUSTOM2_IN = 39
CUSTOM3_IN = 40
CUSTOM4_IN = 41
CUSTOM5_IN = 42
CUSTOM6_IN = 43
CUSTOM7_IN = 44
CUSTOM8_IN = 45
CUSTOM9_IN = 46
CUSTOM10_I = 47
CUSTOM11_I = 48
CUSTOM12_I = 49
CUSTOM13_I = 50
CUSTOM14_I = 51
CUSTOM15_I = 52
SPN_PASSWO = 53
SPN_FIRSTL = 54
SPN_LASTLO = 55
SPN_STATUS = 56
SPN_SESSIO = 57
COMMUNICAT = 58

# Now do people
reader = csv.reader(open(PATH + "/person.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[PERSONKEY] == "PERSONKEY": continue

    o = asm.Owner(nextownerid)
    owners.append(o)
    nextownerid += 1
    o.ExtraID = row[PERSONKEY]
    o.OwnerForeNames = row[FNAME].split(" ")[0]
    o.OwnerSurname = row[LNAME]
    o.OwnerName = o.OwnerTitle + " " + o.OwnerForeNames + " " + o.OwnerSurname
    # Find the address
    if addrlink.has_key(row[PERSONKEY]):
        addrkey = addrlink[row[PERSONKEY]]
        if addresses.has_key(addrkey):
            add = addresses[addrkey]
            o.OwnerAddress = add["address"]
            o.OwnerTown = add["city"]
            o.OwnerCounty = add["state"]
            o.OwnerPostcode = add["zip"]
    o.EmailAddress = row[EMAIL]
    o.HomeTelephone = row[HOME_PH]
    o.WorkTelephone = row[WORK_PH]
    o.MobileTelephone = row[THIRD_PH]
    o.IsACO = cint(row[ACO_IND])
    o.IsStaff = cint(row[STAFF_IND])
    o.IsVolunteer = cint(row[VOL_IND])
    o.IsDonor = cint(row[DONOR_IND])
    o.IsMember = cint(row[MEMBER_IND])
    o.IsBanned = cint(row[NOADOPT] == "T" and "1" or "0")
    o.IsFosterer = cint(row[FOSTERS])
    o.ExcludeFromBulkEmail = cint(row[MAILINGSAM])

CASEDATE = 0
CASENUM = 1
FIELDCARD = 2
KENNEL = 3
ANIMALKEY = 4
ANIMSTAT = 5
ARIVDATE = 6
ARIVREAS = 7
ARIVMETH = 8
PRECINCT = 9
CONDITION = 10
BITECASE = 11
ADPTDATE = 12
EUTHDATE = 13
QUAR_BEG = 14
EVALDATE = 15
DISPMETH = 16
DISPDATE = 17
PERSDELV = 18
PERSACO = 19
PERSINTAKE = 20
PERSDISP = 21
PERSEUTH = 22
PERSPREVOW = 23
MEMO = 24
CASEKEY = 25
OWNERATDIS = 26
INCIDENTKE = 27
PRECINCTDI = 28
PERSFOSTER = 29
ADDEDBYUSE = 30
ADDEDDATET = 31
LASTUSERTO = 32
LASTSAVEDA = 33
KENNELSECT = 34
BEHAVIORAS = 35
BEHAVIORA2 = 36
BEHAVIORA3 = 37
VETCHECK = 38
VETCHECKRE = 39
EUTHAPPROV = 40
EUTHAPPRO2 = 41
EUTHAPPRO3 = 42
EUTHAPPRO4 = 43
WEBUPLOADP = 44
WEBUPLOAD2 = 45
WEBUPLOADA = 46
WEBUPLOAD3 = 47
WEBUPLOADO = 48
WEBUPLOADF = 49
WEBUPLOAD4 = 50
WEBUPLOAD5 = 51

# Run through the shelter file and create any movements/euthanisation info
reader = csv.reader(open(PATH + "/shelter.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[CASEDATE] == "CASEDATE": continue

    a = findanimal(row[ANIMALKEY])
    if a is not None:
        arivdate = getdate(row[ARIVDATE])
        a.ShortCode = firstw(row[FIELDCARD])
        a.ShelterLocationUnit = firstw(row[KENNEL])
        if arivdate is not None:
            a.DateBroughtIn = arivdate
            a.generateCode(gettypeletter(a.AnimalTypeID))
            a.ShortCode = firstw(row[FIELDCARD])
    o = findowner(row[OWNERATDIS])

    # Apply other fields
    if row[ARIVREAS] == "QUARANTINE":
        a.IsQuarantine = 1

    elif row[ARIVREAS] == "STRAY":
        if a.AnimalTypeID == 2: a.AnimalTypeID == 10
        if a.AnimalTypeID == 11: a.AnimalTypeID == 12
        a.EntryReasonID = 7

    # Adoptions
    if row[DISPMETH] == "ADOPTED":
        if a is None or o is None: continue
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = getdate(row[DISPDATE])
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 1
        movements.append(m)

    # Reclaims
    elif row[DISPMETH] == "RETURN TO OWNER":
        if a is None or o is None: continue
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 5
        m.MovementDate = getdate(row[DISPDATE])
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 5
        movements.append(m)

    # Released or Other
    elif row[DISPMETH].startswith("RELEASED") or row[DISPMETH] == "OTHER":
        if a is None or o is None: continue
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = 0
        m.MovementType = 7
        m.MovementDate = getdate(row[DISPDATE])
        m.Comments = row[DISPMETH]
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 7
        movements.append(m)

    # Holding
    elif strip(row, DISPMETH) == "" and row[ANIMSTAT] == "HOLDING":
        a.IsHold = 1
        a.Archived = 0

    # Deceased
    elif row[DISPMETH] == "DECEASED":
        a.DeceasedDate = getdate(row[DISPDATE])
        a.Archived = 1

    # Euthanized
    elif row[DISPMETH] == "EUTHANIZED":
        a.DeceasedDate = getdate(row[DISPDATE])
        a.PutToSleep = 1
        a.Archived = 1

    # If the outcome is blank, it's on the shelter
    elif row[DISPMETH].strip() == "":
        a.Archived = 0

    # It's the name of an organisation that received the animal
    else:
        if a is None: continue
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = 100
        m.MovementType = 3
        m.MovementDate = getdate(row[DISPDATE])
        m.Comments = row[DISPMETH]
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 3
        movements.append(m)

# Now that everything else is done, output stored records
for a in animals:
    print a
for av in animalvaccinations:
    print av
for o in owners:
    print o
for m in movements:
    print m

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

