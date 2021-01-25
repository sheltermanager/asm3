#!/usr/bin/python

import asm, csv, datetime, sys

"""
Import script for Noah's Ark custom access db

12th November, 2014
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
        amt = amt.replace("$", "").replace(",", "")
        if amt.find("(") != -1:
            amt = "-" + amt.replace("(", "").replace(")", "")
        amt = float(amt)
        amt = amt * 100
        return int(amt)
    except Exception,err:
        sys.stderr.write(str(err) + "\n")
        return 0

def getentryreason(oldcat):
    if oldcat == "1": return 12 # Domestic
    if oldcat == "2": return 14 # Wildlife
    return 13 # Exotic

def gettype(oldclass):
    if oldclass == "1": return 51 # Bird
    if oldclass == "2": return 53 # Reptile
    if oldclass == "3": return 52 # Mammal
    if oldclass == "5": return 54 # Fish
    return 51

def gettypeletter(aid):
    tmap = {
        48: "W",
        49: "D",
        50: "E",
        51: "B",
        52: "M",
        53: "R",
        54: "F"
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

def findowner(personkey = ""):
    """ Looks for an owner with the given name in the collection
        of owners. If one wasn't found, None is returned """
    if ownermap.has_key(personkey):
        return ownermap[personkey]
    return None

def getdate(s, defyear = "14"):
    """ Parses a date in MM/DD/YYYY format. If the field is blank or not a date, None is returned """
    if s.strip() == "": return None
    if s.find("/") == -1: return None
    if s.find(" ") != -1: s = s.split(" ")[0]
    b = s.split("/")
    # if we couldn't parse the date, use the first of the default year
    if len(b) < 3: return datetime.date(int(defyear) + 2000, 1, 1)
    try:
        return datetime.date(int(b[2]), int(b[0]), int(b[1]))
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
    """ Returns a date adjusted for age. """
    d = getdate(arrivaldate)
    if d == None: d = datetime.datetime.today()
    if age == "Adult":
        d = d - datetime.timedelta(days = 365 * 2)
    if age == "Youth":
        d = d - datetime.timedelta(days = 365 * 1)
    if age == "Baby":
        d = d - datetime.timedelta(days = 60)
    return d

def bs(s):
    return s.replace("\\", "/").replace("'", "`")

# --- START OF CONVERSION ---

print "\\set ON_ERROR_STOP\nBEGIN;"

owners = []
ownerdonations = []
movements = []
animals = []
animalvaccinations = []
logs = []

ownermap = {}
animalmap = {}

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

# Create new owner records for "Noah's Ark" and "Other Shelter"
o = asm.Owner(nextownerid)
owners.append(o)
nextownerid += 1
o.OwnerSurname = "Noah's Ark"
o.OwnerName = o.OwnerSurname
o = asm.Owner(nextownerid)
owners.append(o)
nextownerid += 1
o.OwnerSurname = "Other Shelter"
o.OwnerName = o.OwnerSurname

LNGSPECIESID = 0
TXTSPECIESDESC = 1
LNGCATEGORYID = 2
LNGCLASSID = 3

spcat = {}
spcls = {}

# Do their species list
print "DELETE FROM species WHERE ID > 100;"
reader = csv.reader(open("data/noah/tblAnimalSpeciesType-csv.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[LNGSPECIESID] == "lngSpeciesID": continue
    desc = row[TXTSPECIESDESC].title()
    if desc == "": desc = "(blank)"
    spid = int(row[LNGSPECIESID]) + 100
    print "INSERT INTO species (ID, SpeciesName, SpeciesDescription) VALUES (%d, '%s', ''); " % (spid, desc)
    spcat[row[LNGSPECIESID]] = row[LNGCATEGORYID]
    spcls[row[LNGSPECIESID]] = row[LNGCLASSID]

LNGANIMALID = 0
ANIMALID = 1
ANIMALSPECIES = 2
ANIMALDIED = 3
ANIMALRELEASED = 4
ANIMALPERM = 5
ANIMALTRANSF = 6
PRIORMEDICAL = 7
MEDICALTREATMENT = 8
DISPOSITIONDATE = 9
DISPOSITION = 10
COUNTYFOUND = 11
STATEFOUND = 12
LNGANIMALCASENUMBER = 13
DTMANIMALDATE = 14
TXTHEARABOUTUS = 15
LNGANIMALSPECIES = 16
TXTANIMALAGE = 17
TXTANIMALSEX = 18
BLNANIMALINJURED = 19
LNGANIMALCOUNT = 20
TXTANIMALNAME = 21
TXTANIMALWHEREFOUND = 22
TXTANIMALLENGTHOFCARE = 23
TXTANIMALTREATMENT = 24
MEMNOTES = 25

AF_INJURED = 7
AF_HOWHEAR = 9
AF_NOANIMALS = 5
AF_AGE = 22
AF_WHEREFOUND = 13

# Clear additional fields before animals
print "DELETE FROM additional;" 

# Start with the animal file
reader = csv.reader(open("data/noah/tblAnimal-csv.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[LNGANIMALID] == "lngAnimalID": continue
    if strip(row, LNGANIMALSPECIES) == "": continue

    # Each row contains a new animal, owner and adoption
    a = asm.Animal(nextanimalid)
    animals.append(a)
    animalmap[row[LNGANIMALID]] = a
    nextanimalid += 1
    a.ExtraID = row[LNGANIMALID]
    if not spcls.has_key(row[LNGANIMALSPECIES]): 
        a.AnimalTypeID = 51
    else:
        a.AnimalTypeID = gettype(spcls[row[LNGANIMALSPECIES]])
    a.SpeciesID = int(row[LNGANIMALSPECIES]) + 100
    a.AnimalName = row[TXTANIMALNAME]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    age = row[TXTANIMALAGE]
    a.DateOfBirth = getdateage(age, row[DTMANIMALDATE])
    a.DateBroughtIn = getdate(row[DTMANIMALDATE])
    if a.DateBroughtIn is None:
        a.DateBroughtIn = datetime.datetime.today()    
    a.generateCode(gettypeletter(a.AnimalTypeID))
    a.EntryReasonID = 12
    if spcat.has_key(row[LNGANIMALSPECIES]):
        a.EntryReasonID = getentryreason(spcat[row[LNGANIMALSPECIES]])
    a.ShelterCode = row[LNGANIMALCASENUMBER]
    a.ShortCode = row[LNGANIMALCASENUMBER]
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 1
    a.Sex = getsexmf(row[TXTANIMALSEX])
    comments = "Age: " + row[TXTANIMALAGE]
    comments += ", Injured: "
    comments += row[BLNANIMALINJURED] == "FALSE" and "No" or "Yes"
    comments += ", Heard about us: " + row[TXTHEARABOUTUS]
    comments += ", Count: " + row[LNGANIMALCOUNT]
    comments += ", Found: " + row[TXTANIMALWHEREFOUND]
    comments += ", Length of care: " + row[TXTANIMALLENGTHOFCARE]
    comments += ", Treatment: " + row[TXTANIMALTREATMENT]
    a.HiddenAnimalDetails = bs(comments)
    a.AnimalComments = bs(row[MEMNOTES])
    a.Archived = 1

    # Additional fields
    if row[BLNANIMALINJURED] != "FALSE":
        print "INSERT INTO additional (AdditionalFieldID, LinkID, LinkType, Value) VALUES ( %d, %d, %d, '1' );" % (AF_INJURED, a.ID, 0)
    print "INSERT INTO additional (AdditionalFieldID, LinkID, LinkType, Value) VALUES ( %d, %d, %d, '%s' );" % (AF_HOWHEAR, a.ID, 0, bs(row[TXTHEARABOUTUS]))
    print "INSERT INTO additional (AdditionalFieldID, LinkID, LinkType, Value) VALUES ( %d, %d, %d, '%s' );" % (AF_NOANIMALS, a.ID, 0, bs(row[LNGANIMALCOUNT]))
    print "INSERT INTO additional (AdditionalFieldID, LinkID, LinkType, Value) VALUES ( %d, %d, %d, '%s' );" % (AF_AGE, a.ID, 2, age)
    print "INSERT INTO additional (AdditionalFieldID, LinkID, LinkType, Value) VALUES ( %d, %d, %d, '%s' );" % (AF_WHEREFOUND, a.ID, 0, bs(row[TXTANIMALWHEREFOUND]))

LNGEVENTID = 0
LNGANIMALID = 1
DTMEVENTDATE = 2
LNGEVENTTYPEID = 3
INTANIMALCOUNT = 4
TXTEVENTCOMMENT = 5

CHECKED_IN = "1"
RELEASED = "2"
PERMANENT = "3"
DIED = "4"
TRANSFERRED = "7"
EUTHANIZED = "8"
DOA = "10"

# Look at animal events next
reader = csv.reader(open("data/noah/tblAnimalEvent-csv.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[LNGANIMALID] == "lngAnimalID": continue
    a = findanimal(row[LNGANIMALID])
    if a is None: continue
    evtdate = getdatefi(row[DTMEVENTDATE])
    if evtdate is None: continue

    if row[LNGEVENTTYPEID] == CHECKED_IN:
        a.DateBroughtIn = evtdate
    if row[LNGEVENTTYPEID] == RELEASED:
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.MovementType = 7
        m.MovementDate = evtdate
        m.Comments = row[TXTEVENTCOMMENT]
        a.Archived = 1
        a.ActiveMovementDate = evtdate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 7
        movements.append(m)
    if row[LNGEVENTTYPEID] == PERMANENT:
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = 100
        m.MovementType = 2
        m.IsPermanentFoster = 1
        m.MovementDate = evtdate
        m.Comments = row[TXTEVENTCOMMENT]
        a.Archived = 1
        a.ActiveMovementDate = evtdate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 2
        movements.append(m)
    if row[LNGEVENTTYPEID] == DIED:
        a.DeceasedDate = evtdate
        a.Archived = 1
        a.PTSReason = row[TXTEVENTCOMMENT]
    if row[LNGEVENTTYPEID] == TRANSFERRED:
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = 101
        m.MovementType = 3
        m.IsPermanentFoster = 1
        m.MovementDate = evtdate
        m.Comments = row[TXTEVENTCOMMENT]
        a.Archived = 1
        a.ActiveMovementDate = evtdate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 3
        movements.append(m)
    if row[LNGEVENTTYPEID] == EUTHANIZED:
        a.DeceasedDate = evtdate
        a.PutToSleep = 1
        a.PTSReason = row[TXTEVENTCOMMENT]
        a.Archived = 1
    if row[LNGEVENTTYPEID] == DOA:
        a.DeceasedDate = evtdate
        a.IsDOA = 1
        a.PTSReason = row[TXTEVENTCOMMENT]
        a.Archived = 1

LNGPERSONID = 0
IMPORT_DONOR_ID = 1
IMPORT_PERSONID = 2
IMPORT_COMPANYID = 3
LNGPERSONTYPEID = 4
DTMDATECREATED = 5
DTMDATEMODIFIED = 6
DTMRENEWALDATE = 7
TXTMAILDEST = 8
TXTBUSCONTACT = 9
TXTLAST = 10
TXTFIRST = 11
TXTMIDDLE = 12
TXTNICKNAME = 13
TXTPREFIX = 14
TXTSUFFIX = 15
TXTSALUTATION = 16
BLNHOUSEHEAD = 17
TXTSEX = 18
DTMBIRTHDATE = 19
TXTEMPLOYER = 20
TXTOCCUPATION = 21
MEMINFO = 22
TXTADR1 = 23
TXTADR2 = 24
TXTADR3 = 25
TXTCITY = 26
TXTSTATE = 27
TXTZIP = 28
TXTCOUNTY = 29
INTDISTRICT = 30
TXTPRECINCT = 31
TXTPHONE = 32
TXTPAGER = 33
TXTCELL = 34
TXTFAX = 35
TXTEMAIL = 36
TXTMAILCODE = 37
TXTWEBSITE = 38
TXTMADR1 = 39
TXTMADR2 = 40
TXTMADR3 = 41
TXTMCITY = 42
TXTMSTATE = 43
TXTMZIP = 44
TXTMCOUNTY = 45
INTMDISTRICT = 46
TXTMPRECINCT = 47
TXTMPHONE = 48
TXTMPAGER = 49
TXTMCELL = 50
TXTMFAX = 51
TXTMEMAIL = 52
TXTMMAILCODE = 53
TXTMWEBSITE = 54
TXTALTADR1 = 55
TXTALTADR2 = 56
TXTALTADR3 = 57
TXTALTCITY = 58
TXTALTSTATE = 59
TXTALTZIP = 60
TXTALTCOUNTY = 61
INTALTDISTRICT = 62
TXTALTPRECINCT = 63
TXTALTPHONE = 64
TXTALTPAGER = 65
TXTALTCELL = 66
TXTALTFAX = 67
TXTALTEMAIL = 68
TXTALTMAILCODE = 69
TXTALTWEBSITE = 70
LABEL = 71
VIDEO = 72
BLNINTERNATIONAL = 73

# People 1
reader = csv.reader(open("data/noah/tblPerson-1-csv.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[LNGPERSONID] == "lngPersonID": continue

    o = asm.Owner(nextownerid)
    owners.append(o)
    ownermap[row[LNGPERSONID]] = o
    nextownerid += 1
    o.ExtraID = row[LNGPERSONID]
    o.OwnerForeNames = row[TXTFIRST]
    o.OwnerSurname = row[TXTLAST]
    o.OwnerName = o.OwnerTitle + " " + o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = row[TXTADR1] + " " + row[TXTADR2] + " " + row[TXTADR3]
    o.OwnerTown = row[TXTCITY]
    o.OwnerCounty = row[TXTSTATE]
    o.OwnerPostcode = row[TXTZIP]
    o.EmailAddress = row[TXTEMAIL]
    o.HomeTelephone = row[TXTPHONE]
    o.MobileTelephone = row[TXTCELL]
    o.Comments = strip(row, MEMINFO)

# People 2
reader = csv.reader(open("data/noah/tblPerson-2-csv.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[LNGPERSONID] == "lngPersonID": continue

    o = asm.Owner(nextownerid)
    owners.append(o)
    ownermap[row[LNGPERSONID]] = o
    nextownerid += 1
    o.ExtraID = row[LNGPERSONID]
    o.OwnerForeNames = row[TXTFIRST]
    o.OwnerSurname = row[TXTLAST]
    o.OwnerName = o.OwnerTitle + " " + o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = row[TXTADR1] + " " + row[TXTADR2] + " " + row[TXTADR3]
    o.OwnerTown = row[TXTCITY]
    o.OwnerCounty = row[TXTSTATE]
    o.OwnerPostcode = row[TXTZIP]
    o.EmailAddress = row[TXTEMAIL]
    o.HomeTelephone = row[TXTPHONE]
    o.MobileTelephone = row[TXTCELL]
    o.Comments = strip(row, MEMINFO)

LNGANIMALASSIGNID = 0
LNGANIMALID = 1
LNGTRANSACTIONID = 2
IMPORTANIMALID = 3

# AnimalAssign - builds a map of transaction IDs to ASM animal IDs before
# transactions are built
transanimal = {}
reader = csv.reader(open("data/noah/tblAnimalAssign-csv.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[LNGTRANSACTIONID] == "lngTransactionID": continue
    a = findanimal(row[LNGANIMALID])
    if a is not None:
        transanimal[row[LNGTRANSACTIONID]] = a

LNGTRANSACTIONID = 0
LNGPERSONID = 1
LNGCONTACTID = 2
LNGAIDEID = 3
DTMDATEENTERED = 4
DTMDATECOMMITTED = 5
CURAMOUNT = 6
LNGCHECKNUM = 7
MEMNOTES = 8
LNGDEPOSITID = 9
LNGTRANSACTIONINTYPEID = 10
LNGPAYMENTTYPEID = 11
IMPORTPERSONID = 12
IMPORTANIMALID = 13
IMPORTCONTTYPE = 14
IMPORTCONTNUM = 15
IMPORTACCTNUM = 16
LNGNAACCOUNTID = 17
RECIEPT_PRINTED = 18
DTMDATERECIEPT = 19
NO_RECIEPT = 20
SENT_LETTER = 21
LNGTRANSACTIONCATAGORY = 22
LNGCLASS = 23

print "DELETE FROM donationpayment;"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 1, 'Cash', '' );"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 2, 'Check', '' );"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 3, 'Credit Card', '' );"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 4, 'Debit Card', '' );"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 5, 'In-Kind-NA', '' );"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 6, 'In-Kind-CCH', '' );"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 10, 'Animal', '' );"
#print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 11, 'In-Kind', '' );"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 12, 'Cash-CCH', '' );"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 13, 'Check-CCH', '' );"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 14, 'Outgoing', '' );"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 15, 'Credit-CCH', '' );"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 16, 'Credit-NA', '' );"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 17, 'Fundraiser-NA', '' );"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 18, 'Fundraiser-CCH', '' );"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 19, 'Giftcard-CCH', '' );"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 20, 'Giftcard-NA', '' );"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 21, 'Adopt/Surrender-Fee-NA', '' );"
print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 22, 'Statement-NA', '' );"
#print "INSERT INTO donationpayment (ID, PAYMENTNAME, PAYMENTDESCRIPTION) VALUES ( 23, 'None', '' );"

paymenttypes = {
    "": 1,
    "0": 1, # None
    "1": 1, # cash
    "2": 2, # check
    "3": 10, # animal
    "4": 5, # in kind
    "5": 12, # cash - cch
    "6": 13, # check -cch
    "9": 5, # in kind - na
    "10": 14, # outgoing
    "11": 15, # credit cch
    "12": 16, # credit na
    "13": 17, # fundraiser na
    "14": 18, # fundraiser cch
    "15": 19, # giftcard cch
    "16": 20, # giftcard na
    "17": 21, # adopt/surrender fee na
    "18": 22 # statement na
}

print "DELETE FROM donationtype WHERE ID >= 100;"

transactioncats = {
    "": 9,
    "0": 9, # individuals
    "1": 7, # grants
    "2": 8, # corporate projects
    "3": 9, # individuals 601
    "4": 6, # fundraiser 609
    "6": 9, # foundation
    "7": 10 # memberships
}

# Transactions 1
reader = csv.reader(open("data/noah/tblTransactionIN-1-csv.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[LNGPERSONID] == "lngPersonID": continue
    # Skip junk data
    if strip(row, CURAMOUNT) == "": continue
    if not transactioncats.has_key(row[LNGTRANSACTIONCATAGORY]): continue
    if not paymenttypes.has_key(row[LNGPAYMENTTYPEID]): continue
    o = findowner(row[LNGPERSONID])
    if o is None: continue
    od = asm.OwnerDonation(nextownerdonationid)
    ownerdonations.append(od)
    nextownerdonationid += 1
    od.OwnerID = o.ID
    od.AnimalID = 0
    od.MovementID = 0
    if transanimal.has_key(row[LNGTRANSACTIONID]):
        od.AnimalID = transanimal[row[LNGTRANSACTIONID]].ID
        transanimal[row[LNGTRANSACTIONID]].OriginalOwnerID = o.ID
    od.DateDue = getdate(row[DTMDATECOMMITTED])
    od.Date = getdate(row[DTMDATEENTERED])
    od.Donation = getcurrency(row[CURAMOUNT])
    od.Comments = bs("%s, %s" % (strip(row, LNGCHECKNUM), strip(row, MEMNOTES)))
    od.DonationTypeID = transactioncats[row[LNGTRANSACTIONCATAGORY]]
    od.DonationPaymentID = paymenttypes[row[LNGPAYMENTTYPEID]]

# Transactions 2
reader = csv.reader(open("data/noah/tblTransactionIN-2-csv.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[LNGPERSONID] == "lngPersonID": continue
    # Skip junk data
    if strip(row, CURAMOUNT) == "": continue
    if not transactioncats.has_key(row[LNGTRANSACTIONCATAGORY]): continue
    if not paymenttypes.has_key(row[LNGPAYMENTTYPEID]): continue
    o = findowner(row[LNGPERSONID])
    if o is None: continue
    od = asm.OwnerDonation(nextownerdonationid)
    ownerdonations.append(od)
    nextownerdonationid += 1
    od.OwnerID = o.ID
    od.AnimalID = 0
    od.MovementID = 0
    if transanimal.has_key(row[LNGTRANSACTIONID]):
        od.AnimalID = transanimal[row[LNGTRANSACTIONID]].ID
        transanimal[row[LNGTRANSACTIONID]].OriginalOwnerID = o.ID
    od.DateDue = getdate(row[DTMDATECOMMITTED])
    od.Date = getdate(row[DTMDATEENTERED])
    od.Donation = getcurrency(row[CURAMOUNT])
    od.Comments = bs("%s, %s" % (strip(row, LNGCHECKNUM), strip(row, MEMNOTES)))
    od.DonationTypeID = transactioncats[row[LNGTRANSACTIONCATAGORY]]
    od.DonationPaymentID = paymenttypes[row[LNGPAYMENTTYPEID]]

# Treatment types - create log records for them
LNGTREATMENTID = 0
LNGANIMALID = 1
LNGTREATMENTTYPEID = 2

treatments = {
    "1": "26 - Medication",
    "2": "27 - Stabilized",
    "3": "28 - Isolate",
    "4": "29 - Proper food & water",
    "5": "30 - Nestling formula",
    "6": "31 - Mammal formula",
    "7": "32 - Released same day",
    "8": "33 - Hacking out",
    "9": "34 - Outside enclosure",
    "10": "35 - Inside enclosure",
    "11": "36 - Splint",
    "12": "37 - Cast",
    "13": "38 - Sutures",
    "14": "39 - Incubator or extra heat",
    "15": "40 - Amputated",
    "16": "41 - Euthanized",
    "17": "42 - Vet care",
    "18": "43 - IV fluids",
    "19": "44 - None",
    "20": "45 - Permanent"
}
print "DELETE FROM logtype WHERE ID >= 100;"
for k, v in treatments.iteritems():
    print "INSERT INTO logtype (ID, LOGTYPENAME, LOGTYPEDESCRIPTION) VALUES ( %s, '%s', '');" % (int(k) + 100, v)

reader = csv.reader(open("data/noah/tblAnimalTreatment-csv.csv", "r"), dialect="excel")
for row in reader:
    # Skip the header
    if row[LNGANIMALID] == "lngAnimalID": continue
    a = findanimal(row[LNGANIMALID])
    if a is None: continue
    l = asm.Log(nextlogid)
    logs.append(l)
    nextlogid += 1
    l.LogTypeID = int(row[LNGTREATMENTTYPEID]) + 100
    l.LinkID = a.ID
    l.LinkType = 0
    l.Date = a.DateBroughtIn

LNGINJURYID = 0
LNGANIMALID = 1
LNGINJURYTYPEID = 2

injuries = {
    "1": "1 - Hit by a vehicle",
    "2": "2 - Internal injuries",
    "3": "3 - Head injuries",
    "4": "4 - Orphaned baby",
    "5": "5 - Juvenile",
    "6": "6 - Geriatric",
    "7": "7 - Cold/weak",
    "8": "8 - Wing injury",
    "9": "9 - Limb injury",
    "10": "10 - Foot injury",
    "11": "11 - Eye injury",
    "12": "12 - Lice or ticks",
    "13": "13 - Unknown, appears healthy",
    "14": "14 - DOA",
    "15": "15 - In shock",
    "16": "16 - Imprinted",
    "17": "17 - Abrasions/Lacerations",
    "18": "18 - Give up",
    "19": "19 - No licence",
    "20": "20 - Confiscated by DNR",
    "21": "21 - Abandoned",
    "22": "22 - Cruelty",
    "23": "23 - Poor health/thin",
    "24": "24 - Found",
    "25": "25 - Died Same Day"
}
print "DELETE FROM logtype WHERE ID >= 200;"
for k, v in injuries.iteritems():
    print "INSERT INTO logtype (ID, LOGTYPENAME, LOGTYPEDESCRIPTION) VALUES ( %s, '%s', '');" % (int(k) + 200, v)

reader = csv.reader(open("data/noah/tblAnimalInjury-csv.csv", "r"), dialect="excel")
for row in reader:
    # Skip the header
    if row[LNGANIMALID] == "lngAnimalID": continue
    a = findanimal(row[LNGANIMALID])
    if a is None: continue
    l = asm.Log(nextlogid)
    logs.append(l)
    nextlogid += 1
    l.LogTypeID = int(row[LNGINJURYTYPEID]) + 200
    l.LinkID = a.ID
    l.LinkType = 0
    l.Date = a.DateBroughtIn

print "DELETE FROM animal WHERE ID >= %d;" % startanimalid
print "DELETE FROM owner WHERE ID >= %d;" % startownerid
print "DELETE FROM ownerdonation WHERE ID >= %d;" % startownerdonationid
print "DELETE FROM adoption WHERE ID >= %d;" % startmovementid
print "DELETE FROM log WHERE ID >= %d;" % startlogid

# Now that everything else is done, output stored records
for a in animals:
    print a
for o in owners:
    print o
for od in ownerdonations:
    print od
for l in logs:
    print l
for m in movements:
    print m

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

