#!/usr/bin/python

import asm, csv, sys, datetime

"""
Import script for ShelterBuddy MDB export
2nd June, 2012
"""

# Use gmdb2 to export these tables 
# tbladdress.csv
# tbladoption.csv
# tblanimal.csv
# tblanimalvacc.csv
# tblanimalvettreatments.csv
# tblperson.csv
# tblsuburblist.csv

def getsex12(s):
    """ 1 = Male, 2 = Female """
    if s.find("1") != -1:
        return 1
    elif s.find("2") != -1:
        return 0
    else:
        return 2

def findanimal(animalid = ""):
    """ Looks for an animal with the given shelterbuddy id in the collection
        of animals. If one wasn't found, None is returned """
    for a in animals:
        if a.ExtraID == animalid.strip():
            return a
    return None

def findowner(recnum = ""):
    """ Looks for an owner with the given name in the collection
        of owners. If one wasn't found, None is returned """
    for o in owners:
        if o.ExtraID == recnum.strip():
            return o
    return None

def getdate(s, defyear = "12"):
    """ Parses a date in DD/MM/YY format. If the field is blank, None is returned """
    if s.strip() == "": return None
    # If there's time info, throw it
    if s.find(" ") != -1: s = s[0:s.find(" ")]
    b = s.split("/")
    # if we couldn't parse the date, use the first of the default year
    if len(b) < 3: return datetime.date(int(defyear) + 2000, 1, 1)
    try:
        year = int(b[2])
        if year < 1900: year += 2000
        return datetime.date(year, int(b[1]), int(b[0]))
    except:
        return datetime.date(int(defyear) + 2000, 1, 1)

def tocurrency(s):
    if s.strip() == "": return 0.0
    s = s.replace("$", "")
    try:
        return float(s)
    except:
        return 0.0

class SBSuburb:
    id = 0
    suburb = ""
    postcode = ""
    state = ""

class SBAddress:
    id = 0
    streetNum = ""
    streetName = ""
    extraAddress = ""
    postcode = ""
    city = ""
    state = ""
    def address(self):
        s = self.streetNum + " " + self.streetName
        if self.extraAddress.strip() != "": s = self.extraAddress
        return s

# --- START OF CONVERSION ---
print "\\set ON_ERROR_STOP\nBEGIN;"

addresses = {}
suburbs = {}
vacctype = {}

owners = []
movements = []
animals = []

asm.setid("animal", 100)
asm.setid("person", 100)
asm.setid("adoption", 100)
asm.setid("animalvaccination", 100)

# tblsuburblist.csv
SUBURBID = 0
SUBURBNAME = 1
POSTCODE = 2
STATE = 3
reader = csv.reader(open("tblsuburblist.csv", "r"), dialect="excel")
reader.next() # skip header
for row in reader:
    if row[0].strip() == "": break
    s = SBSuburb()
    s.id = row[SUBURBID].strip()
    s.suburb = row[SUBURBNAME]
    s.postcode = row[POSTCODE]
    s.state = row[STATE]
    suburbs[s.id] = s
    
# tblanimalvacc.csv
VDESCRIPTION = 1
VCODE = 4
print "DELETE FROM vaccinationtype WHERE ID > 200;"
reader = csv.reader(open("tblanimalvacc.csv", "r"), dialect="excel")
reader.next() # skip header
for row in reader:
    if row[1].strip() == "": break
    vt = row[VDESCRIPTION].strip()
    vc = row[VCODE].strip()
    vacctype[vc] = vt
    print "INSERT INTO vaccinationtype VALUES (%s, '%s');" % (vc, vt.replace("'", "`"))

# tbladdress.csv
ADDRESSID = 0
STREETNUM = 1
STREETNAME = 2
EXTRAADD = 7
POSTCODE = 9
SUBURBID = 13
reader = csv.reader(open("tbladdress.csv", "r"), dialect="excel")
reader.next() # skip header
for row in reader:
    if row[0].strip() == "": break
    s = SBAddress()
    s.id = row[ADDRESSID].strip()
    s.streetNum = row[STREETNUM]
    s.streetName = row[STREETNAME]
    s.extraAddress = row[EXTRAADD]
    s.postcode = row[POSTCODE]
    if suburbs.has_key(row[SUBURBID]):
        sb = suburbs[row[SUBURBID]]
        s.city = sb.suburb
        s.state = sb.state
    addresses[s.id] = s

# tblanimal.csv
ANIMALID = 0 
RECNUM = 1              # Could be original owner?
MICROCHIP = 4
TYPE = 5                # Cat or Dog
BREED = 6               # Primary breed
SEX = 7                 # 1 for Male, 2 for Female
COLOUR = 8
DATEIN = 21             # Date brought in
DATEOUT = 22
DESEXDATE = 41          # Neutered date
ENTRYREASON = 46        # Plain text
NAME = 50
CROSSBREED = 77         # -1 for yes, 0 for no
SECONDBREED = 78
DOB = 95

reader = csv.reader(open("tblanimal.csv", "r"), dialect="excel")
reader.next() # skip header
for row in reader:
    if row[0].strip() == "": break
    a = asm.Animal()
    animals.append(a)
    a.ExtraID = row[ANIMALID].strip()
    a.AnimalName = row[NAME]
    a.AnimalTypeID = asm.type_id_for_name(row[TYPE])
    a.SpeciesID = asm.species_id_for_name(row[TYPE])
    if row[DATEIN].strip() != "": a.DateBroughtIn = getdate(row[DATEIN])
    a.Neutered = row[DESEXDATE].strip() != "" and 1 or 0
    a.NeuteredDate = getdate(row[DESEXDATE])
    a.BreedID = asm.breed_id_for_name(row[BREED])
    a.Breed2ID = asm.breed_id_for_name(row[SECONDBREED])
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    a.CrossBreed = row[CROSSBREED] == -1 and 1 or 0
    if row[DOB].strip() != "": a.DateOfBirth = getdate(row[DOB])
    a.IdentichipNumber = row[MICROCHIP]
    if row[MICROCHIP].strip() != "": a.Identichipped = 1
    a.Sex = getsex12(row[SEX])
    a.BaseColourID = asm.colour_id_for_name(row[COLOUR])
    a.ShelterLocation = 1
    a.generateCode(asm.type_name_for_id(a.AnimalTypeID))
    comments = "Original Breed: " + row[BREED] + " " + row[SECONDBREED] + ", "
    comments += "Original Colour: " + row[COLOUR]
    a.HiddenAnimalDetails = comments
    #if row[PLACEMENT_STATUS].strip() == "Deceased": 
    #    a.DeceasedDate = getdate(row[PLACEMENT_DATE])

# tblperson.csv
RECNUM = 0
TITLE = 1
TITLE2 = 2
FIRSTNAME = 3
LASTNAME = 4
PNAME = 5
DEAR = 6
HOMEPHONE = 10
WORKPHONE = 11
MOBILEPHONE = 12
ADDRESSID = 85
reader = csv.reader(open("tblperson.csv", "r"), dialect="excel")
reader.next() # skip header
for row in reader:
    if row[0].strip() == "": break
    o = asm.Owner()
    owners.append(o)
    o.ExtraID = row[RECNUM].strip()
    o.OwnerTitle = row[TITLE]
    o.OwnerForeNames = row[FIRSTNAME]
    o.OwnerSurname = row[LASTNAME]
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.HomeTelephone = row[HOMEPHONE]
    o.WorkTelephone = row[WORKPHONE]
    o.MobileTelephone = row[MOBILEPHONE]
    if addresses.has_key(row[ADDRESSID].strip()):
        a = addresses[row[ADDRESSID].strip()]
        o.OwnerAddress = a.address()
        o.OwnerTown = a.city
        o.OwnerCounty = a.state
        o.OwnerPostcode = a.postcode

# tbladoption.csv
ADOPTIONID = 0
RECNUM = 1
ANIMALID = 2
DATE = 4
reader = csv.reader(open("tbladoption.csv", "r"), dialect="excel")
reader.next() # skip header
for row in reader:
    if row[0].strip() == "": break
    # Find the animal and owner for this movement
    a = findanimal(row[ANIMALID].strip())
    o = findowner(row[RECNUM].strip())
    if a != None and o != None:
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = o.ID
        m.AnimalID = a.ID
        m.MovementDate = getdate(row[DATE])
        m.MovementType = 1

# tblanimalvettreatments.csv
ANIMALID = 1
DUEDATE = 2
DATEGIVEN = 3
VACCID = 4
print "DELETE FROM animalvaccination WHERE ID > 100;"
reader = csv.reader(open("tblanimalvettreatments.csv", "r"), dialect="excel")
reader.next() # skip header
for row in reader:
    if row[0].strip() == "": break
    av = asm.AnimalVaccination()
    av.DateRequired = getdate(row[DUEDATE])
    av.DateOfVaccination = getdate(row[DATEGIVEN])
    a = findanimal(row[ANIMALID].strip())
    if a == None: continue
    av.AnimalID = a.ID
    av.VaccinationID = int(row[VACCID].strip())
    print av

# Now that everything else is done, output stored records
print "DELETE FROM animal WHERE ID > 100;"
print "DELETE FROM owner WHERE ID > 100;"
print "DELETE FROM adoption WHERE ID > 100;"
print "DELETE FROM primarykey;"
print "DELETE FROM configuration WHERE ItemName Like 'VariableAnimalDataUpdated';"
for a in animals:
    print a
for o in owners:
    print o
for m in movements:
    print m

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

