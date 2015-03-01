#!/usr/bin/python

import asm, csv, datetime, sys

"""
Import script for Betsie Nachtigal (Coulee Region)

7th January, 2015
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

def firstword(s):
    if s.find(" ") != -1:
        return s.split(" ")[0]
    return s

def getcurrency(amt):
    try:
        amt = float(amt.replace("$", ""))
        amt = amt * 100
        return int(amt)
    except Exception,err:
        #sys.stderr.write(str(err) + "\n")
        return 0

def getincidenttype(ctype):
    imap = {
        "at large": 3,
        "bite": 5,
        "trap": 3, 
        "injured": 10,
        "holding stray": 8,
        "cruelty": 7,
        "nuisance": 3,
        "abandonment": 7,
        "in car": 4,
        "hit by car": 10
    }
    for k, v in imap.iteritems():
        if ctype.find(k) != -1:
            return v
    return 3

def getcompletedtype(ctype):
    cmap = {
        "issued": 3,
        "picked": 2,
    }
    for k, v in cmap.iteritems():
        if ctype.find(k) != -1:
            return v
    return 2

def gettype(sp):
    if sp == "Dog" or sp == "Puppy": return 2 # Unwanted Dog
    if sp == "Cat" or sp == "Kitten": return 11 # Unwanted Cat
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
    elif meth == "Mastercard":
        return 3
    elif meth == "Check":
        return 2
    elif meth == "Cash":
        return 1
    else:
        return 1

def getsize(size):
    if size == "L": return 1
    if size == "M": return 2
    if size == "S": return 3
    return 2

def findanimal(animalkey):
    """ Looks for an animal with the given code in the collection
        of animals. If one wasn't found, It tries the name. If still
        nothing is found, None is returned """
    if animalmap.has_key(animalkey):
        return animalmap[animalkey]
    return None

def findowner(firstname = "", lastname = "", address = "", fullname = "", masterid = "0"):
    """ Looks for an owner with the given name in the collection
        of owners. If one wasn't found, None is returned """
    if fullname != "":
        if ownermapbyname.has_key(fullname):
            return ownermapbyname[fullname]
        return None
    if masterid != "0":
        if ownermapbymasterid.has_key(masterid):
            return ownermapbymasterid[masterid]
        return None
    key = firstname + " " + lastname + " " + address
    if ownermapbykey.has_key(key):
        return ownermapbykey[key]
    return None

def getdate(s, defyear = "14"):
    """ Parses a date in MM/DD/YY format. If the field is blank or not a date, None is returned """
    if s.strip() == "": return None
    if s.find("/") == -1: return None
    if s.find(" ") != -1: s = s.split(" ")[0]
    b = s.split("/")
    # if we couldn't parse the date, use the first of the default year
    if len(b) < 3: return datetime.date(int(defyear) + 2000, 1, 1)
    try:
        year = int(b[2])
        if year > 75: 
            year += 1900
        else:
            year += 2000
        return datetime.date(year, int(b[0]), int(b[1]))
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

ownermapbyname = {}
ownermapbykey = {}
ownermapbymasterid = {}
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

asm.setid("donationtype", 100)

unknown = asm.Owner(nextownerid)
owners.append(unknown)
nextownerid += 1
unknown.OwnerSurname = "Unknown"
unknown.OwnerName = unknown.OwnerSurname

MASTERID = 0
LASTNAME = 1
FIRSTNAME = 2
PHONENUMB = 3
BPHONE = 4
FAXNO = 5
EMAIL = 6
TITLE = 7
ADD1 = 8
ADD2 = 9
ZIP = 10
CITY = 11
STATE = 12
MUNICIPALITY = 13
TYPE = 14
LISTNUM = 15
MEMOPAD = 16
SPONSORTYPE = 17
LASTADOPTDATE = 18
LASTPETADOPTED = 19
FIRSTENTERED = 20
SECUREMEMO = 21
LUSERFIELD1 = 22
LUSERFIELD2 = 23
LUSERFIELD3 = 24
LUSERFIELD4 = 25
LUSERFIELD5 = 26
LUSERFIELD6 = 27
LUSERFIELD7 = 28
LUSERFIELD8 = 29
LUSERFIELD9 = 30
LUSERFIELD10 = 31
CONAME = 32
DRIVERSLICENSE = 33
LDOB = 34
LHEIGHT = 35
LWEIGHT = 36
EYECOLOR = 37
LADD1 = 38
LADD2 = 39
LZIP = 40
LCITY = 41
LSTATE = 42
LMUNICIPALITY = 43
PHONEEXT = 44
CELLPHONE = 45
MADD1 = 46
MADD2 = 47
MZIP = 48
MCITY = 49
MSTATE = 50
MAILSWITCHJAN = 51
MAILSWITCHFEB = 52
MAILSWITCHMAR = 53
MAILSWITCHAPR = 54
MAILSWITCHMAY = 55
MAILSWITCHJUN = 56
MAILSWITCHJUL = 57
MAILSWITCHAUG = 58
MAILSWITCHSEP = 59
MAILSWITCHOCT = 60
MAILSWITCHNOV = 61
MAILSWITCHDEC = 62
AMAILSWITCHJAN = 63
AMAILSWITCHFEB = 64
AMAILSWITCHMAR = 65
AMAILSWITCHAPR = 66
AMAILSWITCHMAY = 67
AMAILSWITCHJUN = 68
AMAILSWITCHJUL = 69
AMAILSWITCHAUG = 70
AMAILSWITCHSEP = 71
AMAILSWITCHOCT = 72
AMAILSWITCHNOV = 73
AMAILSWITCHDEC = 74
ALASTNAME = 75
AFIRSTNAME = 76
ACELLPHONE = 77
SALUTATION = 78
APHONENUMB = 79
ABPHONE = 80
AFAXNO = 81
APHONEEXT = 82
PHONETYPE1 = 83
PHONETYPE2 = 84
PHONETYPE3 = 85
PHONETYPE4 = 86
PHONETYPE5 = 87
PHONETYPE6 = 88
PHONETYPE7 = 89
PHONETYPE8 = 90
ATITLE = 91
OPTOUT1 = 92
OPTOUT2 = 93

reader = csv.reader(open("data/coulee/list1.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[MASTERID] == "MasterID": continue

    o = asm.Owner(nextownerid)
    owners.append(o)
    nextownerid += 1

    o.ExtraID = row[MASTERID]
    o.OwnerTitle = strip(row, TITLE)
    o.OwnerForeNames = strip(row, FIRSTNAME)
    o.OwnerSurname = strip(row, LASTNAME)
    if o.OwnerSurname == "": o.OwnerSurname = "(blank)"
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = strip(row, ADD1)
    o.OwnerTown = strip(row, CITY)
    o.OwnerCounty = strip(row, STATE)
    o.OwnerPostcode = strip(row, ZIP)
    o.HomeTelephone = strip(row, PHONENUMB)
    o.WorkTelephone = strip(row, BPHONE)
    o.EmailAddress = strip(row, EMAIL)
    o.Comments = strip(row, MEMOPAD)
    tf = strip(row, TYPE)
    if tf.lower().find("x") != -1:
        o.ExcludeFromBulkEmail = 1
    if tf.lower().find("b") != -1:
        o.IsBanned = 1
    if tf.lower().find("d") != -1:
        o.IsDeceased = 1
    #flags = ""
    #o.AdditionalFlags = flags
    ownermapbymasterid[o.ExtraID] = o
    ownermapbyname[o.OwnerName] = o
    ownermapbykey[o.OwnerForeNames + " " + o.OwnerSurname + " " + firstword(o.OwnerAddress)] = o

# Not sure animalhistory is needed
"""
ANIMALHISTORYID = 0
ANIMALHISTORYPOSTDATE = 1
RECORDNUMBER = 2
FORMNUM = 3
PETNAME = 4
SPECIES = 5
BREEDID = 6
SEX = 7
SPAYED = 8
SPAYDATE = 9
DOB = 10
MASTERID = 11
NAME = 12
FNAME = 13
ZIP = 14
ADD1 = 15
ADD2 = 16
CITY = 17
STATE = 18
RCOUNTY = 19
HPHONE = 20
BPHONE = 21
DONATIONS = 22
VETER = 23
ACCEPTED = 24
WHYRETURN = 25
DAP2 = 26
DHPL = 27
HWT = 28
WORMED = 29
RABIES = 30
FVRCP = 31
LEUK = 32
AIDS = 33
DATE = 34
ADOPTDATE = 35
MEMOPAD = 36
TAG = 37
MICROCHIP = 38
INTERNETDESCRIPTION = 39
RLENGTHOFOWNERSHIP = 40
RLOOUNITS = 41
RCOLOR = 42
RDESCR = 43
RSHELTER = 44
RORIGINOFANIMAL = 45
RSURRENDERREASON = 46
RHOUSEBROKEN = 47
RBITTEN = 48
RCHILDREN = 49
RANIMALS = 50
RDISPOSITION = 51
ROFFSPRINGMALE = 52
ROFFSPRINGFEMALE = 53
RSURRENDERMEMO = 54
RCAGECARDMEMO = 55
RCAGELOC = 56
RSURRENDERTYPE = 57
RDECLAWED = 58
RUSERFIELD1 = 59
RUSERFIELD2 = 60
RUSERFIELD3 = 61
RUSERFIELD4 = 62
RUSERFIELD5 = 63
RUSERFIELD6 = 64
RUSERFIELD7 = 65
RUSERFIELD8 = 66
RUSERFIELD9 = 67
RUSERFIELD10 = 68
RSIZE = 69
RINTAKEMUNICIPALITY = 70
RDISPOSITIONMUNICIPALITY = 71
PROFITCENTER = 72
SERIALNUMBER = 73
WILDLIFE = 74
ACO = 75
DECLAWTYPE = 76
AVAILFORADOPT = 77
BREEDID2 = 78
MICROCHIPTYPE = 79
AACODE = 80
CUSTODYDATE = 81
LISTASFOUND = 82
PETEVALUATION = 83
PETSIGNATURE = 84
ALTERNATEAGE = 85
STSIGNUPIDASSIGNED = 86
STSIGNUPTYPE = 87
STSIGNUPDATE = 88
STINVOICENUMBER = 89
FEECHARGED = 90
MICROCHIPDATE = 91
MICROCHIPINVOICENUMBER = 92
MICROCHIPFEECHARGED = 93


reader = csv.reader(open("data/coulee/animalhistory.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[RECORDNUMBER] == "RECORDNUMBER": continue
    if strip(row, DATE) == "": continue

    # Each row contains a new animal
    a = asm.Animal(nextanimalid)
    animals.append(a)
    animalmap[row[RECORDNUMBER]] = a
    nextanimalid += 1
    a.ExtraID = row[RECORDNUMBER]

    a.DateBroughtIn = getdate(row[DATE])
    a.AnimalTypeID = gettype(row[SPECIES])
    if row[SPECIES] == "Kitten":
        a.SpeciesID = 1
    elif row[SPECIES] == "Puppy":
        a.SpeciesID = 2
    else:
        a.SpeciesID = asm.species_id_for_name(row[SPECIES])
    a.generateCode(gettypeletter(a.AnimalTypeID))
    a.ShortCode = strip(row, FORMNUM)
    ob = strip(row, BREEDID)
    a.CrossBreed = 0
    if ob.find("Mix") != -1:
        a.CrossBreed = 1
        a.Breed2ID = 442
        ob = ob.replace("Mix", "")
    a.BreedID = asm.breed_id_for_name(ob)
    a.BreedName = asm.breed_name(a.BreedID, a.Breed2ID)
    a.Sex = getsexmf(row[SEX])
    a.Size = getsize(row[RSIZE])
    a.Neutered = cint(row[SPAYED])
    a.NeuteredDate = getdate(row[SPAYDATE])
    a.DateOfBirth = getdate(row[DOB])
    if a.DateOfBirth is None: 
        a.DateOfBirth = a.DateBroughtIn
    a.BaseColourID = asm.colour_id_for_name(row[RCOLOR])
    a.RabiesTag = row[TAG]
    a.IdentichipNumber = row[MICROCHIP]
    if a.IdentichipNumber.strip() != "": 
        a.Identichipped = 1
        a.IdentichipDate = a.DateBroughtIn
    a.AnimalName = strip(row, PETNAME)
    if a.AnimalName == "":
        a.AnimalName = "(unknown)"
    a.Markings = row[RDESCR]
    #comments = ""
    #if strip(row, GENERAL_CONDITION) != "": comments += "Condition: " + row[GENERAL_CONDITION]
    #if strip(row, VICIOUS) != "": comments += ", Vicious: " + row[VICIOUS]
    #if strip(row, DANGEROUS) != "": comments += ", Dangerous: " + row[DANGEROUS]
    #a.HiddenAnimalDetails = bs(comments)
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 1
    a.AnimalComments = bs(row[MEMOPAD])
    a.ReasonForEntry = row[RSURRENDERREASON]
    a.IsHouseTrained = row[RHOUSEBROKEN] == 1 and 0 or 1
    a.IsGoodWithChildren = row[RCHILDREN] == 1 and 0 or 1
    a.IsGoodWithDogs = row[RANIMALS] == 1 and 0 or 1
    a.IsGoodWithCats = row[RANIMALS] == 1 and 0 or 1
    if strip(row, DECLAWTYPE) != "": a.Declawed = 1
    origin = strip(row, RORIGINOFANIMAL)
    if len(origin) < 3:
        origin = "Surrender"
    disp = strip(row, RDISPOSITION)
    a.EntryReasonID = asm.entryreason_id_for_name(origin, True)
    if origin.startswith("Transfer"):
        a.IsTransfer = 1
    elif origin.startswith("Euthan"):
        a.DeceasedDate = a.DateBroughtIn
        a.PTSReason = origin
        a.PutToSleep = 1
        a.Archived = 1
    if disp.startswith("Euthan"):
        a.DeceasedDate = a.DateBroughtIn
        a.PTSReason = disp
        a.PutToSleep = 1
        a.Archived = 1
    if disp.startswith("DOA"):
        a.DeceasedDate = a.DateBroughtIn
        a.IsDOA = 1
        a.Archived = 1
    im = strip(row, RINTAKEMUNICIPALITY)
    im = im.replace("'", "").replace(";", "").replace("`", "").replace(".", "").replace("\"", "")
    if im != "" and im != "y" and im != "l" and im != "v":
        a.IsPickup = 1
        a.PickupLocationID = asm.pickuplocation_id_for_name(im, True)
    # Surrendering owner info if available
    o = None
    if strip(row, NAME) != "":
        o = findowner(strip(row, FNAME), strip(row, NAME), strip(row, ADD1))
        if o is None:
            o = asm.Owner(nextownerid)
            owners.append(o)
            nextownerid += 1
            o.OwnerForeNames = strip(row, FNAME)
            o.OwnerSurname = strip(row, NAME)
            if o.OwnerSurname == "": o.OwnerSurname = "(blank)"
            o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
            o.OwnerAddress = strip(row, ADD1)
            o.OwnerTown = strip(row, CITY)
            o.OwnerCounty = strip(row, STATE)
            o.OwnerPostcode = strip(row, ZIP)
            o.HomeTelephone = strip(row, HPHONE)
            o.WorkTelephone = strip(row, BPHONE)
            ownermapbyname[o.OwnerName] = o
            ownermapbykey[o.OwnerForeNames + " " + o.OwnerSurname + " " + firstword(o.OwnerAddress)] = o
        a.OriginalOwnerID = o.ID
    # If we have a disposition of reclaimed, create a reclaim movement
    # to the original owner
    if strip(row, RDISPOSITION) == "RECLAIMED" and o is not None:
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 5
        m.MovementDate = a.DateBroughtIn
        a.Archived = 1
        a.ActiveMovementDate = a.DateBroughtIn
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 5
        movements.append(m)
"""

RECORDNUMBER = 0
FORMNUM = 1
PETNAME = 2
SPECIES = 3
BREEDID = 4
SEX = 5
SPAYED = 6
SPAYDATE = 7
DOB = 8
MASTERID = 9
NAME = 10
FNAME = 11
ZIP = 12
ADD1 = 13
ADD2 = 14
CITY = 15
STATE = 16
RCOUNTY = 17
HPHONE = 18
BPHONE = 19
DONATIONS = 20
VETER = 21
ACCEPTED = 22
WHYRETURN = 23
DAP2 = 24
DHPL = 25
HWT = 26
WORMED = 27
RABIES = 28
FVRCP = 29
LEUK = 30
AIDS = 31
DATE = 32
ADOPTDATE = 33
MEMOPAD = 34
TAG = 35
MICROCHIP = 36
INTERNETDESCRIPTION = 37
RLENGTHOFOWNERSHIP = 38
RLOOUNITS = 39
RCOLOR = 40
RDESCR = 41
RSHELTER = 42
RORIGINOFANIMAL = 43
RSURRENDERREASON = 44
RHOUSEBROKEN = 45
RBITTEN = 46
RCHILDREN = 47
RANIMALS = 48
RDISPOSITION = 49
ROFFSPRINGMALE = 50
ROFFSPRINGFEMALE = 51
RSURRENDERMEMO = 52
RCAGECARDMEMO = 53
RCAGELOC = 54
RSURRENDERTYPE = 55
RDECLAWED = 56
RUSERFIELD1 = 57
RUSERFIELD2 = 58
RUSERFIELD3 = 59
RUSERFIELD4 = 60
RUSERFIELD5 = 61
RUSERFIELD6 = 62
RUSERFIELD7 = 63
RUSERFIELD8 = 64
RUSERFIELD9 = 65
RUSERFIELD10 = 66
RSIZE = 67
RINTAKEMUNICIPALITY = 68
RDISPOSITIONMUNICIPALITY = 69
PROFITCENTER = 70
SERIALNUMBER = 71
WILDLIFE = 72
ACO = 73
DECLAWTYPE = 74
AVAILFORADOPT = 75
BREEDID2 = 76
MICROCHIPTYPE = 77
AACODE = 78
CUSTODYDATE = 79
LISTASFOUND = 80
PETEVALUATION = 81
PETSIGNATURE = 82
ALTERNATEAGE = 83
STSIGNUPIDASSIGNED = 84
STSIGNUPTYPE = 85
STSIGNUPDATE = 86
STINVOICENUMBER = 87
FEECHARGED = 88
MICROCHIPDATE = 89
MICROCHIPINVOICENUMBER = 90
MICROCHIPFEECHARGED = 91

# On shelter animals are kept in a separate database table called RECORD
# with a slightly different layout to animalhistory
reader = csv.reader(open("data/coulee/record.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[RECORDNUMBER] == "RECORDNUMBER": continue
    if strip(row, DATE) == "": continue

    # Each row contains a new animal
    a = asm.Animal(nextanimalid)
    animals.append(a)
    animalmap[row[RECORDNUMBER]] = a
    nextanimalid += 1
    a.ExtraID = row[RECORDNUMBER]

    a.DateBroughtIn = getdate(row[DATE])
    a.AnimalTypeID = gettype(row[SPECIES])
    if row[SPECIES] == "Kitten":
        a.SpeciesID = 1
    elif row[SPECIES] == "Puppy":
        a.SpeciesID = 2
    else:
        a.SpeciesID = asm.species_id_for_name(row[SPECIES])
    a.generateCode(gettypeletter(a.AnimalTypeID))
    a.ShortCode = strip(row, FORMNUM)
    ob = strip(row, BREEDID)
    a.CrossBreed = 0
    if ob.find("Mix") != -1:
        a.CrossBreed = 1
        a.Breed2ID = 442
        ob = ob.replace("Mix", "")
    a.BreedID = asm.breed_id_for_name(ob)
    a.BreedName = asm.breed_name(a.BreedID, a.Breed2ID)
    a.Sex = getsexmf(row[SEX])
    a.Size = getsize(row[RSIZE])
    a.Neutered = cint(row[SPAYED])
    a.NeuteredDate = getdate(row[SPAYDATE])
    a.DateOfBirth = getdate(row[DOB])
    if a.DateOfBirth is None: 
        a.DateOfBirth = a.DateBroughtIn
    a.BaseColourID = asm.colour_id_for_name(row[RCOLOR])
    a.RabiesTag = row[TAG]
    a.IdentichipNumber = row[MICROCHIP]
    if a.IdentichipNumber.strip() != "": 
        a.Identichipped = 1
        a.IdentichipDate = a.DateBroughtIn
    a.AnimalName = strip(row, PETNAME)
    if a.AnimalName == "":
        a.AnimalName = "(unknown)"
    a.Markings = row[RDESCR]
    #comments = ""
    #if strip(row, GENERAL_CONDITION) != "": comments += "Condition: " + row[GENERAL_CONDITION]
    #if strip(row, VICIOUS) != "": comments += ", Vicious: " + row[VICIOUS]
    #if strip(row, DANGEROUS) != "": comments += ", Dangerous: " + row[DANGEROUS]
    #a.HiddenAnimalDetails = bs(comments)
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 1
    a.AnimalComments = bs(row[MEMOPAD])
    a.ReasonForEntry = row[RSURRENDERREASON]
    a.IsHouseTrained = row[RHOUSEBROKEN] == 1 and 0 or 1
    a.IsGoodWithChildren = row[RCHILDREN] == 1 and 0 or 1
    a.IsGoodWithDogs = row[RANIMALS] == 1 and 0 or 1
    a.IsGoodWithCats = row[RANIMALS] == 1 and 0 or 1
    if strip(row, DECLAWTYPE) != "": a.Declawed = 1
    origin = strip(row, RORIGINOFANIMAL)
    if len(origin) < 3:
        origin = "Surrender"
    disp = strip(row, RDISPOSITION)
    a.EntryReasonID = asm.entryreason_id_for_name(origin, True)
    if origin.startswith("Transfer"):
        a.IsTransfer = 1
    elif origin.startswith("Euthan"):
        a.DeceasedDate = a.DateBroughtIn
        a.PTSReason = origin
        a.PutToSleep = 1
        a.Archived = 1
    if disp.startswith("Euthan"):
        a.DeceasedDate = a.DateBroughtIn
        a.PTSReason = disp
        a.PutToSleep = 1
        a.Archived = 1
    if disp.startswith("DOA"):
        a.DeceasedDate = a.DateBroughtIn
        a.IsDOA = 1
        a.Archived = 1
    im = strip(row, RINTAKEMUNICIPALITY)
    im = im.replace("'", "").replace(";", "").replace("`", "").replace(".", "").replace("\"", "")
    if im != "" and im != "y" and im != "l" and im != "v":
        a.IsPickup = 1
        a.PickupLocationID = asm.pickuplocation_id_for_name(im, True)
    # Surrendering owner info if available
    o = None
    if strip(row, NAME) != "":
        o = findowner(strip(row, FNAME), strip(row, NAME), strip(row, ADD1))
        if o is None:
            o = asm.Owner(nextownerid)
            owners.append(o)
            nextownerid += 1
            o.OwnerForeNames = strip(row, FNAME)
            o.OwnerSurname = strip(row, NAME)
            if o.OwnerSurname == "": o.OwnerSurname = "(blank)"
            o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
            o.OwnerAddress = strip(row, ADD1)
            o.OwnerTown = strip(row, CITY)
            o.OwnerCounty = strip(row, STATE)
            o.OwnerPostcode = strip(row, ZIP)
            o.HomeTelephone = strip(row, HPHONE)
            o.WorkTelephone = strip(row, BPHONE)
            ownermapbyname[o.OwnerName] = o
            ownermapbykey[o.OwnerForeNames + " " + o.OwnerSurname + " " + firstword(o.OwnerAddress)] = o
        a.OriginalOwnerID = o.ID
    # If we have a disposition of reclaimed, create a reclaim movement
    # to the original owner
    if strip(row, RDISPOSITION) == "RECLAIMED" and o is not None:
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 5
        m.MovementDate = a.DateBroughtIn
        a.Archived = 1
        a.ActiveMovementDate = a.DateBroughtIn
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 5
        movements.append(m)

EUTHID = 0
EUTHDATETIME = 1
EUTHAGENT = 2
EUTHDISPOSITION = 3
EUTHSTAFF = 4
EUTHPETNAME = 5
EUTHSPECIES = 6
EUTHBREEDID = 7
EUTHSEX = 8
EUTHNAME = 9
EUTHFNAME = 10
EUTHZIP = 11
EUTHADD1 = 12
EUTHADD2 = 13
EUTHCITY = 14
EUTHSTATE = 15
EUTHDOSAGE = 16
EUTHMEMO = 17
EUTHINVOICENUM = 18
EUTHPETID = 19
EUTHAGENT2 = 20
EUTHDOSAGE2 = 21

reader = csv.reader(open("data/coulee/euthanasia.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[EUTHPETID] == "EuthPetID": continue
    a = findanimal(row[EUTHPETID])
    if a is None: continue
    a.DeceasedDate = getdate(row[EUTHDATETIME])
    a.PutToSleep = 1
    a.Archived = 1

ADOPTID = 0
CONTRACT = 1
ANIMDALID = 2
MASTERID = 3
NAME = 4
FIRSTNAME = 5
ADD1 = 6
ADD2 = 7
CITY = 8
STATE = 9
ZIP = 10
HOME = 11
BUSINESS = 12
PETNAME = 13
SPECIES = 14
BREED = 15
BIRTH = 16
SEX = 17
COLOR = 18
DHPL = 19
HWT = 20
RABIES = 21
FVRCP = 22
LEUK = 23
STOOL = 24
SRESULT = 25
HEARTGRD = 26
SPAY = 27
FEE = 28
SPAYDEP = 29
MISC = 30
STAFF = 31
MEMOPAD = 32
AIDS = 33
AUSERFIELD1 = 34
AUSERFIELD2 = 35
AUSERFIELD3 = 36
AUSERFIELD4 = 37
AUSERFIELD5 = 38
DATEADOPTED = 39
SPAYED = 40
CONTRACTMEMO = 41
BREEDID2 = 42
ADOPTIONSIGNATURE = 43

reader = csv.reader(open("data/coulee/adopts.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[ANIMDALID] == "ANIMDALID": continue

    a = findanimal(row[ANIMDALID])
    if a is None: continue
    evtdate = getdate(row[DATEADOPTED])
    if evtdate is None: continue

    o = findowner(strip(row, FIRSTNAME), strip(row, NAME), strip(row, ADD1))
    if o is None:
        o = asm.Owner(nextownerid)
        owners.append(o)
        nextownerid += 1
        o.OwnerForeNames = strip(row, FIRSTNAME)
        o.OwnerSurname = strip(row, NAME)
        if o.OwnerSurname == "": o.OwnerSurname = "(blank)"
        o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
        o.OwnerAddress = strip(row, ADD1)
        o.OwnerTown = strip(row, CITY)
        o.OwnerCounty = strip(row, STATE)
        o.OwnerPostcode = strip(row, ZIP)
        o.HomeTelephone = strip(row, HOME)
        o.WorkTelephone = strip(row, BUSINESS)
        ownermapbyname[o.OwnerName] = o
        ownermapbykey[o.OwnerForeNames + " " + o.OwnerSurname + " " + firstword(o.OwnerAddress)] = o

    o.ExtraID = a.ID
    m = asm.Movement(nextmovementid)
    nextmovementid += 1
    m.AnimalID = a.ID
    m.OwnerID = o.ID
    m.MovementType = 1
    m.MovementDate = evtdate
    a.Archived = 1
    a.ActiveMovementDate = evtdate
    a.ActiveMovementID = m.ID
    a.ActiveMovementType = 1
    movements.append(m)

SPONSORID = 0
APPEALDATE = 1
AMOUNT = 2
APPEALTYPE = 3
APPEALDESCR = 4
PLEDGEID = 5
TAXDEDUCTIBLE = 6
REASONCODE = 7
PAYMETHOD = 8
ANOTES = 9
SOURCEFIELD = 10
MEMORIALORHONOR = 11
MEMORIAL = 12
FUNDCODE = 13
BATCHCODE = 14
ANOTES2 = 15
BATCHDATE = 16

reader = csv.reader(open("data/coulee/appeals.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[SPONSORID] == "SponsorID": continue
    # Skip junk data
    if getcurrency(row[AMOUNT]) == 0: continue

    o = findowner(masterid = strip(row, SPONSORID))
    if o is None: continue

    od = asm.OwnerDonation(nextownerdonationid)
    ownerdonations.append(od)
    nextownerdonationid += 1
    od.OwnerID = o.ID
    od.AnimalID = 0
    od.MovementID = 0
    od.Date = getdate(row[APPEALDATE])
    od.Donation = getcurrency(row[AMOUNT])
    od.DonationTypeID = asm.donationtype_id_for_name(strip(row, APPEALTYPE), True)
    od.DonationPaymentID = getpaymentmethod(row[PAYMETHOD])
    od.Comments = strip(row, ANOTES)

RECEIPTNUM = 0
INVOICENUM = 1
CUSTOMER = 2
DATE = 3
PAID = 4
PAIDBY = 5
PRINTED = 6
CCLAST4 = 7
CCAUTHCODE = 8
CCEXPIRE = 9
CHECKNUMBER = 10
PAYMENTDATE = 11
XCTRANSACTIONID = 12
XCBALANCEAVAILABLE = 13

reader = csv.reader(open("data/coulee/payments.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[CUSTOMER] == "Customer": continue
    # Skip junk data
    if strip(row, CUSTOMER) == "": continue
    if getcurrency(row[PAID]) == 0: continue

    o = findowner(fullname = strip(row, CUSTOMER))
    if o is None: continue

    od = asm.OwnerDonation(nextownerdonationid)
    ownerdonations.append(od)
    nextownerdonationid += 1
    od.OwnerID = o.ID
    od.AnimalID = o.ExtraID
    if od.AnimalID == "": od.AnimalID = 0
    od.MovementID = 0
    od.Date = getdate(row[DATE])
    od.Donation = getcurrency(row[PAID])
    od.DonationTypeID = 2
    od.DonationPaymentID = getpaymentmethod(row[PAIDBY])

COMPLAINTID = 0
CDMASTERID = 1
CDLASTNAME = 2
CDFIRSTNAME = 3
CDADD1 = 4
CDADD2 = 5
CDCITY = 6
CDSTATE = 7
CDZIP = 8
CDMUNICIPALITY = 9
CDNEARESTINTERSECTION = 10
CDDIRECTIONS = 11
CDHOMEPHONE = 12
CDBUSINESSPHONE = 13
CWMASTERID = 14
CWLASTNAME = 15
CWFIRSTNAME = 16
CWADD1 = 17
CWADD2 = 18
CWCITY = 19
CWSTATE = 20
CWZIP = 21
CWMUNICIPALITY = 22
CWDIRECTIONS = 23
CWHOMEPHONE = 24
CWBUSINESSPHONE = 25
DATE = 26
TAKENBY = 27
CONTACTEDBY = 28
COMPLAINTTYPE = 29
OFFENSE = 30
ADDITINALINFO = 31
COMMENTS = 32
INVESTIGATIONAUTHORIZED = 33
INVESTIGATIONDATE = 34
OFFICERASSIGNED = 35
OFFICERSASSISTING = 36
INVESTIGATINGOFFICER = 37
CASENUM = 38
NARRATIVE = 39
COMPLAINTRESOLUTIONTYPE = 40
CORRECTIONRECOMMENDED = 41
WARNINGISSUED = 42
WARNINGDATE = 43
SUMMONSISSUED = 44
SUMMONSDATE = 45
COMPLIANCE = 46
HEARINGDATE = 47
VIOLATIONID = 48
FOLLOWUPCALLREQUIRED = 49
CDPHYSICALADDRESS = 50
CWPHYSICALLADDRESS = 51
DRVLICENSE = 52
CDOB = 53
CHEIGHT = 54
CWEIGHT = 55
CEYECOLOR = 56
COMPLETEDDATE = 57
COMPLAINTRESOLUTIONTYPE2 = 58
COMPLAINTRESOLUTIONTYPE3 = 59
TEXTDATE = 60
INVOICENUMBER = 61

reader = csv.reader(open("data/coulee/complaints.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[COMPLAINTID] == "ComplaintID": continue
    if getdate(row[DATE]) is None: continue

    ac = asm.AnimalControl(nextanimalcontrolid)
    animalcontrols.append(ac)
    nextanimalcontrolid += 1
    calldate = getdate(row[DATE])
    invdate = getdate(row[INVESTIGATIONDATE])
    if invdate is None: invdate = calldate
    # Caller details
    if strip(row, CDLASTNAME) != "":
        o = findowner(strip(row, CDFIRSTNAME), strip(row, CDLASTNAME), strip(row, ADD1))
        if o is None:
            o = asm.Owner(nextownerid)
            owners.append(o)
            nextownerid += 1
            o.OwnerForeNames = strip(row, CDFIRSTNAME)
            o.OwnerSurname = strip(row, CDLASTNAME)
            if o.OwnerSurname == "": o.OwnerSurname = "(blank)"
            o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
            o.OwnerAddress = strip(row, CDADD1)
            o.OwnerTown = strip(row, CDCITY)
            o.OwnerCounty = strip(row, CDSTATE)
            o.OwnerPostcode = strip(row, CDZIP)
            o.HomeTelephone = strip(row, CDHOMEPHONE)
            o.WorkTelephone = strip(row, CDBUSINESSPHONE)
            ownermapbyname[o.OwnerName] = o
            ownermapbykey[o.OwnerForeNames + " " + o.OwnerSurname + " " + firstword(o.OwnerAddress)] = o
        ac.CallerID = o.ID

    # Dispatch
    ac.DispatchAddress = row[CWADD1]
    ac.DispatchTown = row[CWCITY]
    ac.DispatchCounty = row[CWSTATE]
    ac.DispatchPostcode = row[CWZIP]
    ac.IncidentCompletedID = getcompletedtype(strip(row, COMPLAINTRESOLUTIONTYPE))
    ac.IncidentTypeID = getincidenttype(strip(row, COMPLAINTTYPE))
    ac.IncidentDateTime = calldate
    ac.CallDateTime = calldate
    ac.DispatchDateTime = invdate
    ac.CompletedDate = invdate
    comments = ""
    if strip(row, OFFICERASSIGNED) != "": comments += "Officer: " + row[OFFICERASSIGNED] + "\n"
    if strip(row, COMPLAINTTYPE) != "": comments += "Complaint: " + row[COMPLAINTTYPE] + ", Resolution: " + row[COMPLAINTRESOLUTIONTYPE] + "\n"
    if strip(row, CWMUNICIPALITY) != "": comments += "Municipality: " + row[CWMUNICIPALITY] + "\n"
    if strip(row, CWDIRECTIONS) != "": comments += "Directions: " + row[CWDIRECTIONS] + "\n"
    if strip(row, OFFENSE) != "": comments += "Offense: " + row[OFFENSE] + "\n"
    if strip(row, ADDITINALINFO) != "": comments += "Additional: " + row[ADDITINALINFO] + "\n"
    if strip(row, NARRATIVE) != "": comments += "Narrative: " + row[NARRATIVE] + "\n"
    ac.CallNotes = comments
    ac.Sex = 2

for a in animals:
    # If an animal has been on shelter longer than 6 weeks, adopt them
    # to the unknown owner to prevent a massive amount of on shelter animals
    if a.DateBroughtIn < datetime.date(2014, 11, 14):
        adoptdate = a.DateBroughtIn + datetime.timedelta(days=31)
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = 100
        m.MovementType = 1
        m.MovementDate = adoptdate
        a.Archived = 1
        a.ActiveMovementDate = adoptdate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 1
        movements.append(m)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= %d;" % startanimalid
print "DELETE FROM animalcontrol WHERE ID >= %d;" % startanimalcontrolid
print "DELETE FROM owner WHERE ID >= %d;" % startownerid
print "DELETE FROM ownerdonation WHERE ID >= %d;" % startownerdonationid
print "DELETE FROM adoption WHERE ID >= %d;" % startmovementid
print "DELETE FROM pickuplocation;"
print "DELETE FROM entryreason;"
print "DELETE FROM donationtype WHERE ID >= 100;"

# Now that everything else is done, output stored records
for k, v in asm.pickuplocations.iteritems():
    print v
for k, v in asm.entryreasons.iteritems():
    print v
for k, v in asm.donationtypes.iteritems():
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
