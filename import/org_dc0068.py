#!/usr/bin/python

import asm, csv, sys, datetime

# Import script for Debbie Cook, 6th June, 2010

# Map of words used in file to standard ASM breed IDs
breedmap = ( 
        ("Lab", 30, "Black Labrador Retriever"),
        ("Collie", 34, "Border Collie"),
        ("Shar Pei", 183, "Shar Pei"),
        ("Akita", 5, "Akita"),
        ("Boxer", 40, "Boxer"),
        ("Coon", 63, "Coonhound"),
        ("Terrier", 199, "Terrier"),
        ("Dane" , 98, "Great Dane"),
        ("Shep" , 185, "Shepherd"),
        ("Point" , 160, "Pointer"),
        ("Beagle" , 19, "Beagle"),
        ("Dachshund" , 66, "Dachshund"),
        ("York" , 219, "Yorkshire Terrier Yorkie"),
        ("Pug" , 166, "Pug"),
        ("Jack" , 114, "Jack Russell Terrier"),
        ("Poodle" , 163, "Poodle"),
        ("Chih" , 54, "Chihuahua"),
        ("Shih" , 188, "Shih Tzu"),
        ("Appal" , 357, "Appaloosa"),
        ("Husky", 105, "Husky"),
        ("Tiger", 307, "Tiger"),
        ("Eski", 8, "American Eskimo Dog"),
        ("Pomera", 162, "Pomeranian"),
        ("altese", 131, "Maltese"),
        ("Hima", 275, "Himalayan"),
        ("Tort", 310, "Tortoiseshell"),
        ("Bass", 18, "Basset Hound"),
        ("Corgi", 64, "Corgi"),
        ("Russian", 291, "Russian Blue"),
        ("Ridge", 172, "Rhodesian Ridgeback"),
        ("Bull", 73, "English Bulldog"),
        ("Malin", 25, "Belgian Shepherd Malinois"),
        ("Setter", 77, "English Setter"),
        ("Schnauzer", 178, "Schnauzer"),
        ("Papil", 151, "Papillon"),
        ("Affen", 1, "Affenpinscher"),
        ("Shep", 92, "German Shepherd Dog"),
        ("stiff", 134, "Mastiff"),
        ("Siame", 294, "Siamese"),
        ("ilute Calico" , 241, "Dilute Calico"),
        ("Calico" , 234, "Calico"),
        ("Tabby" , 300, "Tabby"),
        ("DLH" , 243, "Domestic Long Hair"),
        ("D.L.H" , 243, "Domestic Long Hair"),
        ("Long Hair", 243, "Domestic Long Hair"),
        ("DMH" , 252, "Domestic Medium Hair"),
        ("D.M.H" , 252, "Domestic Medium Hair"),
        ("DSH" , 261, "Domestic Short Hair"),
        ("D.S.H" , 261, "Domestic Short Hair")
        )
def getbreed(s):
    """ Looks up the breed, returns DSH if nothing matches """
    for b in breedmap:
        if s.find(b[0]) != -1:
            return b[1]
    return 261

def getspecies(s):
    """ Looks up the species, returns Cat if nothing matches """
    if s.find("Dog") != -1: return 1
    if s.find("Cat") != -1: return 2
    if s.find("Horse") != -1: return 24
    return 2

def gettype(s):
    """ Looks up the animal type from a species. Returns Unwanted Cat for no match """
    if s.find("Dog") != -1: return 2
    if s.find("Cat") != -1: return 11
    if s.find("Horse") != -1: return 13
    return 11

def getbreedname(i):
    """ Looks up the breed's name """
    for b in breedmap:
        if b[1] == i:
            return b[2]
    return "Domestic Short Hair"

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

def getdate(s, defyear = "03"):
    """ Parses a date in YYY/MM/DD format. If the field is blank, None is returned """
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

print "\\set ON_ERROR_STOP\nBEGIN;"

# Starting IDs
asm.setid("animal", 128)
asm.setid("adoption", 36)
asm.setid("owner", 11)

# Create a single owner for all movements
o = asm.Owner()
o.OwnerName = "Owner"
print o


# List of codes we've seen to animals so far - if we already
# have an animal we can add movements to it
codes = {}

# Readable references to CSV columns in the file
CODE = 0
SPECIES = 1
SEX = 2
NAME = 3
DATEOFBIRTH = 4
DESCRIPTION = 5
DATEIN = 6
ADOPTED = 7
TRANSFERRED = 8
RECLAIMED = 9
DIED = 10
ESCAPED = 11
RETURNEDTO = 12

reader = csv.reader(open("dc.csv", "r"), dialect="excel")
for row in reader:

    # Not enough data for row
    if row[1].strip() == "": break

    # New animal record if we haven't seen this code before
    code = row[CODE].strip()
    aid = 0
    if not codes.has_key(code):
        a = asm.Animal()
        aid = a.ID
        codes[code] = aid
        a.ShelterCode = row[CODE]
        a.ShortCode = row[CODE][2:]
        a.AnimalName = row[NAME]
        a.Sex = getsexmf(row[SEX])
        a.Size = 2
        a.Markings = row[DESCRIPTION]
        a.Neutered = 1
        a.SpeciesID = getspecies(row[SPECIES])
        a.AnimalTypeID = gettype(row[SPECIES])
        a.BaseColourID = getcolour(row[DESCRIPTION])
        a.ShelterLocation = 1
        a.BreedID = getbreed(row[DESCRIPTION])
        a.Breed2ID = getbreed(row[DESCRIPTION])
        a.BreedName = getbreedname(a.BreedID)
        if row[DATEOFBIRTH].strip() != "": a.DateOfBirth = getdate(row[DATEOFBIRTH])
        if row[DATEIN].strip() != "": a.DateBroughtIn = getdate(row[DATEIN])
        if row[DIED].strip() != "": a.DeceasedDate = getdate(row[DIED])
        print a
    else:
        aid = codes[code]

    # Movements

    if row[ADOPTED].strip() != "":
        am = asm.Movement()
        am.OwnerID = o.ID
        am.AnimalID = aid
        am.MovementDate = getdate(row[ADOPTED])
        am.MovementType = 1
        if row[RETURNEDTO].strip() != "":
            am.ReturnDate = getdate(row[RETURNEDTO])
        print am

    elif row[TRANSFERRED].strip() != "":
        am = asm.Movement()
        am.OwnerID = o.ID
        am.AnimalID = aid
        am.MovementDate = getdate(row[TRANSFERRED])
        am.MovementType = 3
        if row[RETURNEDTO].strip() != "":
            am.ReturnDate = getdate(row[RETURNEDTO])
        print am

    elif row[RECLAIMED].strip() != "":
        am = asm.Movement()
        am.OwnerID = o.ID
        am.AnimalID = aid
        am.MovementDate = getdate(row[RECLAIMED])
        am.MovementType = 5
        if row[RETURNEDTO].strip() != "":
            am.ReturnDate = getdate(row[RETURNEDTO])
        print am

    elif row[ESCAPED].strip() != "":
        am = asm.Movement()
        am.OwnerID = o.ID
        am.AnimalID = aid
        am.MovementDate = getdate(row[ESCAPED])
        am.MovementType = 4
        if row[RETURNEDTO].strip() != "":
            am.ReturnDate = getdate(row[RETURNEDTO])
        print am

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"
