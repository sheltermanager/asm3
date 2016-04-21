#!/usr/bin/python

import asm, csv, sys, datetime

"""
Import script for Trackabeast export as csv
13th January, 2012
"""

# Map of words used in file to standard ASM breed IDs
breedmap = ( 
        ("German Shorthaired Pointer", 93, "German Shorthaired Pointer"),
        ("German Wirehaired Pointer", 94, "German Wirehaired Pointer")
        )
def getbreed(s):
    """ Looks up the breed, returns DSH if nothing matches """
    for b in breedmap:
        if s.find(b[0]) != -1:
            return b[1]
    return 261

def getspecies(s):
    """ Looks up the species, returns Cat if nothing matches """
    if s.find("dog") != -1: return 1
    if s.find("puppy") != -1: return 1
    if s.find("cat") != -1: return 2
    if s.find("kitten") != -1: return 2
    return 2

def gettype(s):
    """ Looks up the animal type from a species. Returns Unwanted Cat for no match """
    sp = getspecies(s)
    if s == 1: return 2 # Dog
    if s == 2: return 11 # Unwanted Cat
    return 11

def getbreedname(i):
    """ Looks up the breed's name """
    for b in breedmap:
        if b[1] == i:
            return b[2]
    return "German Shorthaired Pointer"

colourmap = (
            ( "Black and White", 3 ),
            ( "Black & White", 3 ),
            ( "White and Black", 5),
            ( "White & Black", 5),
            ( "Brown and Black", 12 ),
            ( "Brown & Black", 12 ),
            ( "Black and Brown", 13 ),
            ( "Black & Brown", 13 ),
            ( "Torti and White", 27 ),
            ( "Torti & White", 27 ),
            ( "Tabby and White", 28 ),
            ( "Tabby & White", 28 ),
            ( "Ginger and White", 29 ),
            ( "Ginger & White", 29 ),
            ( "Red and White", 29 ),
            ( "Red & White", 29 ),
            ( "Orange and White", 29 ),
            ( "Orange & White", 29 ),
            ( "Grey and White", 31 ),
            ( "Grey & White", 31 ),
            ( "Brown and White", 35 ),
            ( "Brown & White", 35 ),
            ( "White and Grey", 32 ),
            ( "White & Grey", 32 ),
            ( "White and Gray", 32 ),
            ( "White & Gray", 32 ),
            ( "White and Tabby", 37 ),
            ( "White & Tabby", 37 ),
            ( "White and Brown", 40 ),
            ( "White & Brown", 40 ),
            ( "Blue", 36 ),
            ( "Black", 1 ),
            ( "White", 2 ),
            ( "Ginger", 4 ),
            ( "Red", 4 ),
            ( "Orange", 4 ),
            ( "Torti", 6),
            ( "Tabby", 7),
            ( "Brown", 11 ),
            ( "Cream", 23 ),
            ( "Grey", 30 ),
            ( "Gray", 30 )
            )

def getcolour(s):
    """ Lookup the colour, returns black if nothing matches """
    for c in colourmap:
        if s.find(c[0]) != -1:
            return c[1]
    return 1

# For use with fields that just contain the sex
def getsexmf(s):
    if s.find("M") != -1:
        return 1
    elif s.find("F") != -1:
        return 0
    else:
        return 2

def getsize(s):
    if s.find("Very") != -1:
        return 0
    if s.find("Large") != -1:
        return 1
    if s.find("Medium") != -1:
        return 2
    if s.find("Small") != -1:
        return 3
    return 2

def getcity(s):
    """Get city from city/state/zip field - City, ST  ZIP """
    if s.strip() == "": return ""
    return s[0:s.find(",")]

def getstate(s):
    if s.strip() == "": return ""
    x = s.find(",")
    if x == -1: return ""
    return s[x + 2:x + 4]

def getzip(s):
    if s.strip() == "": return ""
    x = s.find("  ")
    if x == -1: return ""
    return s[x + 2:]

def findanimal(name = ""):
    """ Looks for an animal with the given name in the collection
        of animals. If one wasn't found, None is returned """
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

def getdate(s, defyear = "11"):
    """ Parses a date in YYYY/MM/DD format. If the field is blank, None is returned """
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

# List of trackids we've seen for animals so far
animaltrackids = {}

# List of trackids we've seen for people so far
ownertrackids = {}

# GSP-animals.csv
TRACKID = 0             # 5 digit ID
NAME = 1                # animal name
TYPE = 2                # dog/cat, puppy/kitten
ENTRY_DATE = 3          # brought in date
ACTIVE = 4              # Y / N for archived
AD_READY = 5            # Unknown
SPAY = 6                # Y / N
FULLY_VACC = 7          # Y / N
FEL_LEUK = 8            # Y / N
RABIES = 9              # Y / N
CURRENT_LOCATION = 10   # Owner name or blank for on shelter
PLACEMENT_STATUS = 11   # Blank / Intake / Returned for on shelter or Fostered | Adopted | Deceased
ORIGIN = 12             # Entry category
MED_CHARGES = 13        # Cost 
SUPPLIES = 14           # Cost
BOARDING = 15           # Cost
TRAINING = 16           # Cost
AD_FEES = 17            # Cost
RESCUE_TYPE = 18        # No idea what this is
BREED = 19              # Animal breed name
BIRTHDATE = 20          # Animal DOB
IMPOUND = 21            # Presumably impound animal came from
RESCUE_GROUP_ANIMAL_ID = 22 # No idea
MICROCHIP = 23          # Microchip no
TATTOO = 24             # Tattoo no
REGISTRATION = 25       # No idea
INITIAL_RESCUE = 26     # No idea
SEX = 27                # Male/Female
SIZE = 28               # Large/Medium/Small/unknown
WEIGHT = 29             # Weight lb
SPECIAL_NEEDS = 30      # Comment field -> health problems
BIOGRAPHY = 31          # Comments
DESCRIPTION = 32        # Comments
FILE_NAME = 33          # Useless to us without exported files
COLOR = 34              # Looks like free form text
PLACEMENT_DATE = 35     # Active movement date effectively

reader = csv.reader(open("GSP-animals.csv", "r"), dialect="excel")
for row in reader:

    # Not enough data for row
    if row[1].strip() == "": break

    # New animal record if we haven't seen this trackid before
    trackid = row[TRACKID].strip()
    if not animaltrackids.has_key(trackid):
        extradata = ""
        a = asm.Animal()
        animaltrackids[trackid] = a.ID
        a.AnimalName = row[NAME]
        a.AnimalTypeID = gettype(row[TYPE])
        a.SpeciesID = getspecies(row[TYPE])
        if row[ENTRY_DATE].strip() != "": a.DateBroughtIn = getdate(row[ENTRY_DATE])
        a.Neutuered = row[SPAY].strip() == "Y" and 1 or 0
        a.CombiTested = 1
        a.FLVResult = row[FEL_LEUK].strip() == "Y" and 0 or 1
        extradata += "Rabies: " + row[RABIES] + ", "
        extradata += "Origin: " + row[ORIGIN] + ", "
        extradata += "Rescue Type: " + row[RESCUE_TYPE] + ", "
        a.BreedID = getbreed(row[BREED])
        a.Breed2ID = getbreed(row[BREED])
        a.BreedName = getbreedname(a.BreedID)
        if row[BIRTHDATE].strip() != "": a.DateOfBirth = getdate(row[BIRTHDATE])
        extradata += "Impound: " + row[IMPOUND] + ", "
        a.IdentichipNumber = row[MICROCHIP]
        if row[MICROCHIP].strip() != "": a.Identichipped = 1
        a.TattooNumber = row[TATTOO]
        if row[TATTOO].strip() != "": a.Tattoo = 1
        extradata += "Registration: " + row[REGISTRATION] + ", "
        extradata += "Initial Rescue: " + row[INITIAL_RESCUE] + ", "
        a.Sex = getsexmf(row[SEX])
        a.Size = getsize(row[SIZE])
        extradata += "Weight: " + row[WEIGHT]
        a.HiddenAnimalDetails = extradata
        if row[SPECIAL_NEEDS].strip() != "":
            a.HasSpecialNeeds = 1
            a.HealthProblems = row[SPECIAL_NEEDS]
        a.AnimalComments = row[BIOGRAPHY]
        a.Markings = row[DESCRIPTION]
        #a.BaseColourID = getcolour(row[COLOR])
        a.BaseColourID = 21 # Liver and White
        a.ShelterLocation = 1
        a.generateCode("Dog")
        if row[PLACEMENT_STATUS].strip() == "Deceased": 
            a.DeceasedDate = getdate(row[PLACEMENT_DATE])
        animals.append(a)

# GSP-people.csv
TRACKID = 0             # 5 digit ID
FIRST_NAME = 1
LAST_NAME = 2
MAIN_PHONE = 3
EMAIL_1 = 4
EMAIL_2 = 5
ADDRESS_1 = 6
ADDRESS_2 = 7
ADDRESS_3 = 8
CITY = 9
STATE = 10
ZIP = 11
HOME_PHONE = 12
CELL_PHONE = 13
WORK_PHONE = 14
FAX = 15
ACTIVE = 16             # Y/N
VOLUNTEER = 17          # Y/N
DON = 17                # Y/N
FOSTER = 18             # Y/N
ADOPTER = 19            # Y/N
STAFF = 20              # Y/N
BOARD_MEMBER = 21       # Y/N
PET_WISH = 22           # Y/N
ANIMAL_DESIRED = 23     # Free form text
DATE_ACTIVE = 24        # Not sure
SEND_EMAIL = 25         # Y/N
COMMENTS = 26
WORKS_WITH_CATS = 27    # Y/N
WORKS_WITH_DOGS = 28    # Y/N
WORKS_WITH_HTHDOGS = 29 # Y/N
TYPE_OF_ANIMAL_DESIRED = 30
HOURS_FOR_MOBILES = 31
VOL_DESC_COMMENTS = 32
VOLUNTEER_INTERESTS = 33 # Y/N
FOS_CATS = 34           # Y/N
FOS_KITTENS = 35
FOS_DOGS = 36
FOS_PUPPIES = 37
FOS_SPEC_NDS = 38
FOS_FIV = 39
FOS_REQ_SUP = 40
FOS_CAN_TRANS = 41
FOS_STAY_ADO = 42
FOS_COMMENTS = 43 # Y/N
DO_NOT_ADOPT = 44 # Free form text
ADOPTION_STAGE = 45 # Y/N
TRANSPORT_LOCAL = 46
TRANSPORT_LONGDISTANCE = 47

reader = csv.reader(open("GSP-people.csv", "r"), dialect="excel")
for row in reader:
    # Not enough data for row
    if row[1].strip() == "": break

    # New owner record if we haven't seen this trackid before
    trackid = row[TRACKID].strip()
    if not ownertrackids.has_key(trackid):
        extradata = ""
        o = asm.Owner()
        ownertrackids[trackid] = o.ID
        o.OwnerForeNames = row[FIRST_NAME]
        o.OwnerSurname = row[LAST_NAME]
        o.OwnerName = o.ForeNames + " " + o.Surname
        o.EmailAddress = row[EMAIL_1]
        o.OwnerAddress = row[ADDRESS_1] + " " + row[ADDRESS_2] + " " + row[ADDRESS_3]
        o.OwnerTown = row[CITY]
        o.OwnerCounty = row[STATE]
        o.OwnerPostcode = row[ZIP]
        o.HomeTelephone = row[HOME_PHONE]
        o.MobileTelephone = row[CELL_PHONE]
        o.WorkTelephone = row[WORK_PHONE]
        o.IsVolunteer = row[VOLUNTEER].strip() == "Y" and 1 or 0
        o.IsFosterer = row[FOSTER].strip() == "Y" and 1 or 0
        o.Comments = row[COMMENTS]
        o.IsBanned = row[DO_NOT_ADOPT].strip() != "" and 1 or 0
        owners.append(o)

# GSP-placements.csv
RESCUE_ID = 0           # No idea
ANIMAL_NAME = 1         
ANIMAL_TYPE = 2 
PLACEMENT_DATE = 3
PLACEMENT_STATUS = 4    # Adopted | Fostered | Deceased | Returned 
LOCATION = 5            # Owner name
ADDRESS = 6
CITY = 7
STATE = 8
ZIP = 9
PHONE = 10
EMAIL = 11
BIRTHDATE = 12
COMMENTS = 13
IMPOUND = 14
ORIGIN = 15
ADOPT_FEE = 16
SUPPLIES = 17
BOARDING = 18
TRAINING = 19
REMINDER = 20
REMINDER_TEXT = 21

reader = csv.reader(open("GSP-placements.csv", "r"), dialect="excel")
for row in reader:

    # Not enough data for row
    if row[1].strip() == "": break

    # Find the animal and owner for this placement
    a = findanimal(row[ANIMAL_NAME])
    o = findowner(row[LOCATION])

    # Is it a death movement? If so, just mark the animal deceased
    if row[PLACEMENT_STATUS].strip() == "Deceased" and a != None:
        a.DeceasedDate = getdate(row[PLACEMENT_DATE])
        a.PTSReason = row[COMMENTS]
        continue

    # Adoption or Foster
    if row[PLACEMENT_STATUS].strip() == "Adopted" or row[PLACEMENT_STATUS].strip() == "Fostered":
        if o != None and a != None:
            m = asm.Movement()
            m.OwnerID = o.ID
            m.AnimalID = a.ID
            m.MovementDate = getdate(row[PLACEMENT_DATE])
            if row[PLACEMENT_STATUS].strip() == "Adopted":
                m.MovementType = 1
            if row[PLACEMENT_STATUS].strip() == "Fostered":
                m.MovementType = 2
            movements.append(m)

# Now that everything else is done, output stored records
print "\\set ON_ERROR_STOP\nBEGIN;"

for a in animals:
    print a
for o in owners:
    print o
for m in movements:
    print m

asm.stderr_summary(animals=animals, owners=owners, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

