#!/usr/bin/python

import asm, csv, sys, datetime

# Import script for animals, cw0243
# 18th October, 2012

# For use with fields that just contain the sex
def getsexmf(s):
    if s.find("M") != -1:
        return 1
    elif s.find("F") != -1:
        return 0
    else:
        return 2

def getdate(s, defyear = "11"):
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

def datetous(d):
    """
    Formats a python date to US format
    """
    import time
    if d == None: return ""
    try:
        return time.strftime("%m/%d/%Y", d.timetuple())
    except:
        return ""

def tocurrency(s):
    if s.strip() == "": return 0.0
    s = s.replace("$", "")
    try:
        return float(s)
    except:
        return 0.0

types = (
("46", "Cat (Pull from AC)"),
("42", "Cat (Return)"),
("44", "Dog (Return)"),
("45", "Dog (Stray)"),
("47", "Dog (Pull from AC)"),
("48", "Dog (Rescue)"),
("49", "Cat (Rescue)"),
("12", "Cat (Stray)"),
("50", "Dog (Owner Surrender)"),
("51", "Cat (Owner Surrender)"),
("52", "Cat (Dump)"),
("53", "Dog (Dump)"),
("40","N (Non Shelter Animal\)")
)

def type_id_for_name(name):
    for tid, tname in types:
        if tname.upper().find(name.upper()) != -1:
            return int(tid)
    return 2

locations = (
("1", "No Locations"),
("2", "Shelter Cat Room"),
("3", "Shelter Cat Isolation Room"),
("4", "Shelter Office"),
("5", "Shelter Dog Room"),
("6", "Foster Care")
)

def location_id_for_name(name):
    for lid, lname in locations:
        if lname.upper().find(name.upper()) != -1:
            return int(lid)
    return 1

reasons = (
("1", "Marriage/Relationship split"),
("2", "Allergies"),
("3", "Biting"),
("4", "Unable to Cope"),
("5", "Unsuitable Accomodation"),
("6", "Died"),
("7", "Stray"),
("8", "Sick/Injured"),
("9", "Unable to Afford"),
("10", "Abuse"),
("11", "Abandoned"),
("12", "Pulled"),
("13", "Unable to Keep")
)

def reason_id_for_name(name):
    for rid, rname in reasons:
        if rname.upper().find(name.upper()) != -1:
            return int(rid)
    return 1

def size_id_for_name(name):
    if name.startswith("Very"):
        return 0
    if name.startswith("Large"):
        return 1
    if name.startswith("Medium"):
        return 2
    if name.startswith("Small"):
        return 3
    return 2

def getresult(name):
    if name == "Positive":
        return 2
    if name == "Negative":
        return 1
    return 0

# --- START OF CONVERSION ---

CODE = 0
NAME = 1
DOB = 2
SEX = 3
TYPE = 4
SPECIES = 5
BREED = 6
CROSSBREED = 7
BASE_COLOR = 8
INTERNAL_LOCATION = 9
SIZE = 10
DATE_IN = 11
ORIGINAL_OWNER = 12
ENTRY_CATEGORY = 13
MICROCHIP = 14
NEUTERSPAY = 15
NEUTERSPAY_LOCATION = 16
HW_TEST = 17
HW_RESULTS = 18
HW_LOCATION = 19
FIVL_TEST = 20
FIVL_RESULTS = 21
FIVL_LOCATION = 22
RABIES_TAG = 23
RABIES_DATE = 24
RABIES_LOCATION = 25
HEALTH_PROBLEMS = 26

print "\\set ON_ERROR_STOP\nBEGIN;"

print "DELETE FROM animal WHERE ID >= 2;"
print "DELETE FROM additional WHERE LinkType = 0;"

nextid = 2
reader = csv.reader(open("cw0243.csv", "r"), dialect="excel")
for row in reader:

    # Not enough data for row
    if row[1].strip() == "": break

    a = asm.Animal(nextid)
    nextid += 1
    comments = ""
    a.ShelterCode = row[CODE]
    a.ShortCode = row[CODE]
    a.AnimalName = row[NAME]
    a.DateOfBirth = getdate(row[DOB])
    a.Sex = getsexmf(row[SEX])
    a.AnimalTypeID = type_id_for_name(row[TYPE])
    a.SpeciesID = asm.species_id_for_name(row[SPECIES])
    a.BreedID = asm.breed_id_for_name(row[BREED])
    if row[CROSSBREED].strip() == "":
        a.Breed2ID = a.BreedID
        a.BreedName = asm.breed_name_for_id(a.BreedID)
        a.CrossBreed = 0
    else:
        a.Breed2ID = asm.breed_id_for_name(row[CROSSBREED])
        a.BreedName = asm.breed_name_for_id(a.BreedID) + " / " + asm.breed_name_for_id(a.Breed2ID)
        a.CrossBreed = 1
    a.BaseColourID = asm.colour_id_for_name(row[BASE_COLOR], True)
    a.ShelterLocation = location_id_for_name(row[INTERNAL_LOCATION])
    a.Size = size_id_for_name(row[SIZE])
    a.DateBroughtIn = getdate(row[DATE_IN])
    comments += "Original owner: " + row[ORIGINAL_OWNER]
    a.EntryReasonID = reason_id_for_name(row[ENTRY_CATEGORY])
    a.IdentichipNumber = row[MICROCHIP]
    if row[MICROCHIP].strip() != "":
        a.Identichipped = 1
    a.NeuteredDate = getdate(row[NEUTERSPAY])
    a.HeartwormTestDate = getdate(row[HW_TEST])
    if row[HW_TEST].strip() != "": a.HeartwormTested = 1
    a.HeartwormTestResult = getresult(row[HW_RESULTS])
    if row[FIVL_TEST].strip() != "":
        a.CombiTested = 1
    a.CombiTestDate = getdate(row[FIVL_TEST])
    a.CombiTestResult = getresult(row[FIVL_RESULTS])
    a.RabiesTag = row[RABIES_TAG]
    a.HealthProblems = row[HEALTH_PROBLEMS]
    a.HiddenAnimalDetails = comments

    print a

    # Additional fields
    print "INSERT INTO additional (LinkType, LinkID, AdditionalFieldID, Value) VALUES (" \
        "%d, %d, %d, '%s');" % (0, a.ID, 4, row[HW_LOCATION] )
    print "INSERT INTO additional (LinkType, LinkID, AdditionalFieldID, Value) VALUES (" \
        "%d, %d, %d, '%s');" % (0, a.ID, 5, row[FIVL_LOCATION] )
    print "INSERT INTO additional (LinkType, LinkID, AdditionalFieldID, Value) VALUES (" \
        "%d, %d, %d, '%s');" % (0, a.ID, 7, row[RABIES_LOCATION] )
    print "INSERT INTO additional (LinkType, LinkID, AdditionalFieldID, Value) VALUES (" \
        "%d, %d, %d, '%s');" % (0, a.ID, 6, datetous(getdate(row[RABIES_DATE]) ))
    print "INSERT INTO additional (LinkType, LinkID, AdditionalFieldID, Value) VALUES (" \
        "%d, %d, %d, '%s');" % (0, a.ID, 3, row[NEUTERSPAY_LOCATION] )


print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"
