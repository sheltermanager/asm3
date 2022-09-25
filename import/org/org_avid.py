#!/usr/bin/python

import asm, csv, sys, datetime

# Import script for AVID, 19th October, 2010
# Updated: 15th November, 2010

# Collection of converted owner, animal and movement objects so far
owners = []
animals = []
movements = []

def getdate(s):
    """ Parses a date in YYYY/MM/DD format. If the field is blank or contains no / separators, None is returned """
    if s.strip() == "": return None
    if s.find("/") == -1: return None
    b = s.split("/")
    if len(b) < 3: return None
    return datetime.date(int(b[0]), int(b[1]), int(b[2]))

def findanimal(adoption = ""):
    """ Looks for an animal with the given adoption no in the collection
        of animals. If one wasn't found, None is returned """
    for a in animals:
        if a.ExtraID == adoption.strip():
            return a
    return None

def findowner(adoption = ""):
    """ Looks for an owner with the given adoption no in the collection
        of owners. If one wasn't found, None is returned """
    for o in owners:
        if o.ExtraID == adoption.strip():
            return o
    return None

def findownerbyname(name = ""):
    """ Looks for an owner with the given name, returns a new
    one, added to the set if it wasn't found """
    for o in owners:
        if o.OwnerName == name:
            return o
    o = asm.Owner()
    o.OwnerName = name
    sp = name.rfind(" ")
    o.Surname = name[sp + 1:]
    o.ForeNames = name[0:sp]
    owners.append(o)
    return o

def adoption_used(adoption = ""):
    """ Looks to see if we already have an adoption number used
    returns True if it is """
    for m in movements:
        if m.AdoptionNumber == adoption.strip():
            return True
    return False

def ft(s):
    return s.strip().title().replace("\\", "")

def ftadd(s):
    return ft(s.replace("\n", ", "))

# --- START OF CONVERSION ---

# Clear anything from previous runs
print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal;"
print "DELETE FROM owner;"
print "DELETE FROM adoption;"
print "DELETE FROM primarykey;"

print "DELETE FROM internallocation;"
print asm.Location(Name = "AVID")

print "DELETE FROM breed WHERE ID = 500 OR ID = 501;"
print asm.Breed(ID = 500, Name = "Unknown Dog", SpeciesID = 1)
print asm.Breed(ID = 501, Name = "Unknown Cat", SpeciesID = 2)

# Readable references to CSV columns in the file
AVIDNO = 0
MOVEMENTDATE = 1
TELEPHONE = 2
LASTNAME = 3
FIRSTNAME = 4
ADDRESS = 5
CITY = 6
STATE = 7
ZIP = 8
ADOPTIONNO = 9
ANIMALNAME = 10
CATDOG = 11

# ================ Main avid database first
reader = csv.reader(open("avid.csv"), dialect="excel")
irow = 0
for row in reader:
    # Skip first row of header
    irow += 1
    if irow < 2: continue

    # Enough data for row?
    if len(row) < 2: break
    if row[0].strip() == "" and row[1].strip() == "" and row[2].strip() == "": continue

    # New animal record 
    a = asm.Animal()
    a.Identichipped = 1
    a.IdentichipNumber = row[AVIDNO].strip()
    a.AnimalName = ft(row[ANIMALNAME])
    if row[CATDOG].strip() == "cat":
        a.SpeciesID = 2
        a.AnimalTypeID = 11
        a.BreedID = 501
        a.Breed2ID = 501
        a.BreedName = "Unknown Cat"
        atype = "U"
        a.ShelterLocation = 1
    else:
        a.SpeciesID = 1
        a.AnimalTypeID = 2
        a.BreedID = 500
        a.Breed2ID = 500
        a.BreedName = "Unknown Dog"
        atype = "D"
        a.ShelterLocation = 1
    a.Sex = 2
    thedate = getdate(row[MOVEMENTDATE])
    if thedate == None: thedate = datetime.datetime.today()
    a.DateBroughtIn = thedate
    a.DateOfBirth = thedate
    a.ExtraID = row[ADOPTIONNO].strip()
    a.generateCode(atype)
    animals.append(a)

    # Create the owner record
    o = asm.Owner()
    o.OwnerForeNames = ft(row[FIRSTNAME])
    o.OwnerSurname = ft(row[LASTNAME])
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.HomeTelephone = ft(row[TELEPHONE])
    o.OwnerAddress = ftadd(row[ADDRESS])
    o.OwnerTown = ft(row[CITY])
    o.OwnerCounty = ft(row[STATE])
    o.OwnerPostcode = ft(row[ZIP])
    o.ExtraID = row[ADOPTIONNO].strip()
    # Mark the owner as homechecked
    o.IDCheck = 1
    o.DateLastHomeChecked = thedate
    o.Comments = "Pre-ASM conversion"
    owners.append(o)

    # And the movement
    m = asm.Movement()
    no = row[ADOPTIONNO].strip()
    if no == "" or no == "N/A" or no == "NA" or no.find("ours") != -1 or no.find("blank") != -1 or adoption_used(no): no = str(900000 + m.ID)
    m.AdoptionNumber = no
    m.OwnerID = o.ID
    m.AnimalID = a.ID
    m.MovementDate = thedate
    m.MovementType = 1
    movements.append(m)
    a.Archived = 1
    a.ActiveMovementID = m.ID
    a.ActiveMovementDate = thedate
    a.ActiveMovementType = m.MovementType

# ================ ODAS 1995
# The odas tags files contains more upto date owner telephone information,
# as well as the odas tag field
# however, it's split into two rows per record
TAG = 0
ANIMALNAME = 1
DATE = 2
ADOPTIONNO = 3
ADOPTERSNAME = 4
PHONE = 5

files = ( "odas1995", "" )
for file in files:
    if file == "": break
    reader = csv.reader(open(file + ".csv"), dialect="excel")

    irow = 0
    for row in reader:
        
        # Skip first row of header
        irow += 1
        if irow < 2: continue

        # Find the matching owner record if there is one
        o = None

        # Does the row have a tag and the name isn't VOID?
        if row[TAG].strip() != "" and row[ANIMALNAME].strip() != "VOID":
            o = findowner(row[ADOPTIONNO])
            if o != None: 
                # If we have a number for the owner, update it
                p = row[PHONE].strip()
                if p != "" and p != "N/A" and p != "**":
                    o.HomeTelephone = p

            # Add the ODAS tag to the animal
            a = findanimal(row[ADOPTIONNO])
            if a != None:
                a.TattooNumber = row[TAG].strip()

# ================ ODAS 1996
# The odas tags files contains more upto date owner telephone information,
# as well as the odas tag field
# however, it's split into two rows per record
TAG = 0
ANIMALNAME = 1
ADDRESS = 2
DATE = 2
ADOPTIONNO = 3
ADOPTERSNAME = 4
HOMEWORK = 5
PHONE = 5
CELL = 6

files = ( "odas1996", "" )
for file in files:
    if file == "": break
    reader = csv.reader(open(file + ".csv"), dialect="excel")

    irow = 0
    for row in reader:
        
        # Skip first row of header
        irow += 1
        if irow < 2: continue

        # Find the matching owner record if there is one
        o = None

        # Does the row have a tag and the name isn't VOID?
        if row[TAG].strip() != "" and row[ANIMALNAME].strip() != "VOID":
            o = findowner(row[ADOPTIONNO])
            if o != None: 
                # If we have a home or cell number for the owner, update it
                p = row[PHONE].strip()
                c = row[CELL].strip()
                if p != "" and p != "N/A" and p != "**":
                    o.HomeTelephone = p
                if c != "" and p.find("N/A") == -1 and c != "**":
                    o.MobileTelephone = c

            # Add the ODAS tag to the animal
            a = findanimal(row[ADOPTIONNO])
            if a != None:
                a.TattooNumber = row[TAG].strip()

        else:
            # It's a continuation of the previous row
            if row[ANIMALNAME].strip() != "VOID":

                # Do we have a work phone?
                p = row[PHONE].strip()
                if o != None and p != "" and p != "N/A" and p != "**":
                    o.WorkTelephone = p


# ================ RABIES

files = ( "rabies2006", "rabies2007", "rabies2008", "rabies2009", "rabies2010" )
TAG = 0
ANIMALNAME = 1
OWNERNAME = 2
ADOPTIONNO = 3
PHONE = 4
DATE = 5

for file in files:
    reader = csv.reader(open(file + ".csv"), dialect="excel")
    irow = 0
    for row in reader:
        
        # Skip first row of header
        irow += 1
        if irow < 2: continue

        # Update the home phone number if we have one
        o = findowner(row[ADOPTIONNO].strip())
        if o != None:
            p = row[PHONE].strip()
            if p != "" and p != "N/A" and p != "**":
                o.HomeTelephone = p

        # Add the rabies tag to the animal
        a = findanimal(row[ADOPTIONNO].strip())
        if a != None:
            a.RabiesTag = row[TAG].strip()
        else:

            # This rabies entry doesn't have an adoption number,
            # create it as a non-shelter animal with original owner
            # link instead
            o = findownerbyname(ft(row[OWNERNAME]))
            o.HomeTelephone = row[PHONE].strip()

            a = asm.Animal()
            a.NonShelterAnimal = 1
            a.RabiesTag = ft(row[TAG])
            a.AnimalName = ft(row[ANIMALNAME])
            a.AnimalTypeID = 40
            thedate = getdate(row[MOVEMENTDATE])
            if thedate == None: thedate = datetime.datetime.today()
            a.DateBroughtIn = thedate
            a.DateOfBirth = thedate
            a.generateCode("N")
            a.BreedID = 500
            a.Breed2ID = 501
            a.BreedName = "Unknown Dog"
            a.OriginalOwnerID = o.ID
            animals.append(a)


# Now that everything else is done, output stored records
for a in animals:
    print a
for m in movements:
    print m
for o in owners:
    print o

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"
