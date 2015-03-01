#!/usr/bin/python

import asm, csv, datetime, re

"""
Import script for Peter Mah 

4th February, 2015
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

def getdateh(s):
    """ Parses dates like August, 2001 or just 2005 """
    if s.strip() == "": return None
    d = 1
    m = 1
    y = 2015
    if s.find("Jan") != -1: m = 1
    elif s.find("Feb") != -1: m = 1
    elif s.find("Mar") != -1: m = 1
    elif s.find("Apr") != -1: m = 1
    elif s.find("May") != -1: m = 1
    elif s.find("Jun") != -1: m = 1
    elif s.find("Jul") != -1: m = 1
    elif s.find("Aug") != -1: m = 1
    elif s.find("Sep") != -1: m = 1
    elif s.find("Oct") != -1: m = 1
    elif s.find("Nov") != -1: m = 1
    elif s.find("Dec") != -1: m = 1
    yy = re.findall("\d\d\d\d", s)
    if len(yy) != 0:
        y = int(yy[0])
    return datetime.date(y,m,d)

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

animals = []

nextanimalid = 5800
startanimalid = 5800

locations = {
    "Cat Sanctuary - Moore House": 20,
    "Cat Sanctuary - New Aids": 21,
    "Cat Sanctuary - Old Aids": 23,
    "Cat Sanctuary - Val Jones": 24,
    "Cat Sanctuary - Single Wide": 25,
    "Cat Sanctuary - SW Leukemia Room": 26,
    "Cat Sanctuary - Leukemia Room": 26,
    "Cat Sanctuary - Double Wide": 27,
    "Cat Sanctuary - Back Pen #3": 29,
    "Cat Sanctuary - Back Pen #4": 30,
    "Cat Sanctuary - Back Pen #5": 31,
    "Cat Sanctuary - Back Pen #7": 32,
    "Cat Sanctuary - Back Pen #8": 33,
    "Cat Sanctuary - Prince of Wales Pen": 34,
    "Cat Sanctuary - Doug's Shed": 35,
    "Cat Sanctuary - Back Courtyard": 28,
    "Cat Sanctuary - Connor": 36,
    "Cat Sanctuary - Front Courtyard": 22,
    "Cat Sanctuary - No 5 Transfer": 3,
    "Cat Sanctuary": 37,
    "Foster": 37,
    "foster": 37
}

NAME = 0
TATTOO = 1
SPECIES = 2
SEX = 3
DATE_OF_BIRTH = 4
ARRIVAL_DATE = 5
ALIAS = 6
BREED = 7
COLOUR = 8
COMMENTS = 9
INTERNAL_LOCATION = 10
LOCATION_ = 11
DATE_OF_DEATH = 12

reader = csv.reader(open("data/petermah/rapscats.csv", "r"), dialect="excel")
for row in reader:

    # Skip the header
    if row[NAME] == "Name": continue

    # Each row contains a new animal
    a = asm.Animal(nextanimalid)
    animals.append(a)
    nextanimalid += 1
    
    a.DeceasedDate = getdate(row[DATE_OF_DEATH])
    if a.DeceasedDate is not None:
        a.DateBroughtIn = a.DeceasedDate - datetime.timedelta(days=365*5)
        a.DateOfBirth = a.DeceasedDate - datetime.timedelta(days=365*10)
        a.PutToSleep = 1
        a.PTSReasonID = 2
    else:
        a.DateBroughtIn = getdateh(row[ARRIVAL_DATE])
        if a.DateBroughtIn is None:
            a.DateBroughtIn = datetime.date(2010, 1, 1)
        a.DateOfBirth = getdateh(row[DATE_OF_BIRTH])
        if a.DateOfBirth is None:
            a.DateOfBirth = datetime.date(2005, 1, 1)

    a.AnimalName = row[NAME]
    a.TattooNumber = strip(row, TATTOO)
    if a.TattooNumber != "": a.Tattoo = 1
    a.SpeciesID = 2
    a.EntryReasonID = 12
    a.AnimalTypeID = 11
    a.ShelterLocation = locations[row[INTERNAL_LOCATION]]
    a.ShelterCode = "U%d%d" % (a.DateBroughtIn.year, a.ID)
    a.ShortCode = "%dU" % a.ID
    a.BreedID = asm.breed_id_for_name(row[BREED])
    a.BreedName = asm.breed_name(a.BreedID, a.Breed2ID)
    a.Sex = getsexmf(row[SEX])
    a.BaseColourID = asm.colour_from_db(row[COLOUR], 9)
    a.AnimalComments = bs(row[COMMENTS])
    if strip(row, ALIAS) != "":
        a.AnimalComments += "\nAlias: %s" % strip(row, ALIAS)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= %d;" % startanimalid

# Now that everything else is done, output stored records
for a in animals:
    print a

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

