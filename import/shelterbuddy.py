#!/usr/bin/python

import asm

"""
Import script for ShelterBuddy MDB/SQL Server export with QueryExpress
2nd June, 2012 - 22nd May, 2015
"""

PATH = "data/uvhs/"

# Use gmdb2 to export these tables from Access
# OR use queryexpress to do it from SQL Server Ex2005
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

def getdate(s):
    if s.find("/1900") != -1: return None
    return asm.getdate_mmddyyyy(s)

def gettype(col1, col2):
    catwords = [ "tabby", "calico", "tortoise", "tiger", "buff", "seal", "tri" ]
    dogwords = [ "tan", "brindle", "yellow", "liver" ]
    for c in catwords:
        if col1.find(c) != -1 or col2.find(c) != -1: return 11 # cat
    for d in dogwords:
        if col1.find(d) != -1 or col2.find(d) != -1: return 2 # dog
    return 11 # cat

def getspecies(col1, col2):
    if gettype(col1, col2) == 11: return 2
    return 1

def getbreed(col1, col2):
    if getspecies(col1, col2) == 2:
        return 261 # domestic shorthair
    return 30 # black lab

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
asm.setid("owner", 100)
asm.setid("adoption", 100)
asm.setid("animalvaccination", 100)

print "DELETE FROM animal WHERE ID >= 100;"
print "DELETE FROM animalvaccination WHERE ID >= 100;"
print "DELETE FROM owner WHERE ID >= 100;"
print "DELETE FROM adoption WHERE ID >= 100;"

# tblsuburblist.csv
for row in asm.csv_to_list(PATH + "tblsuburblist.csv"):
    s = SBSuburb()
    s.id = row["ID"].strip()
    s.suburb = row["Suburb"]
    s.postcode = row["postcode"]
    s.state = row["state"]
    suburbs[s.id] = s
    
# tblanimalvacc.csv
print "DELETE FROM vaccinationtype WHERE ID > 200;"
for row in asm.csv_to_list(PATH + "tblanimalvacc.csv"):
    vc = row["show"].strip()
    vt = row["vaccCode2"].strip() + " " + row["description"]
    vacctype[vc] = vt
    print "INSERT INTO vaccinationtype VALUES (%s, '%s');" % (vc, vt.replace("'", "`"))

# tbladdress.csv
for row in asm.csv_to_list(PATH + "tbladdress.csv"):
    s = SBAddress()
    s.id = row["id"].strip()
    s.streetNum = row["streetNum"]
    s.streetName = row["streetName"]
    s.extraAddress = row["extraAddress"]
    s.postcode = row["postcode"]
    if suburbs.has_key(row["suburbId"]):
        sb = suburbs[row["suburbId"]]
        s.city = sb.suburb
        s.state = sb.state
    addresses[s.id] = s

# tblanimal.csv
for row in asm.csv_to_list(PATH + "tblanimal.csv"):
    a = asm.Animal()
    animals.append(a)
    a.ExtraID = row["AnimalID"].strip()
    a.AnimalName = row["name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    if row.has_key("type"):
        a.AnimalTypeID = asm.type_id_for_name(row["type"])
        a.SpeciesID = asm.species_id_for_name(row["type"])
        a.BreedID = asm.breed_id_for_name(row["breed"])
        a.Breed2ID = asm.breed_id_for_name(row["secondBreed"])
    else:
        # I've seen a version of this database where there's no type field in tblanimal,
        # so we have to infer fields from the colours - ridiculous
        a.AnimalTypeID = gettype(row["Colour"], row["SecondaryColour"])
        a.SpeciesID = getspecies(row["Colour"], row["SecondaryColour"])
        a.BreedID = getbreed(row["Colour"], row["SecondaryColour"])
        # If there's Chicken or Duck or Rabbit in the name, set accordingly
        if a.AnimalName.lower().find("chicken") != -1:
            a.SpeciesID = 14
            a.BreedID = 404
        elif a.AnimalName.lower().find("duck") != -1:
            a.SpeciesID = 3
            a.BreedID = 409
        elif a.AnimalName.lower().find("rabbit") != -1:
            a.SpeciesID = 7
            a.BreedID = 321
    if row["DateIN"].strip() != "": 
        a.DateBroughtIn = getdate(row["DateIN"])
        if a.DateBroughtIn is None:
            a.DateBroughtIn = getdate(row["AddDateTime"])
    if row["DateOUT"].strip() != "":
        a.ActiveMovementDate = getdate(row["DateOUT"])
        if a.ActiveMovementDate is not None:
            a.ActiveMovementType = 1
            a.Archived = 1
        elif a.DateBroughtIn.year < 2015:
            a.Archived = 1
    a.Neutered = row["desexdate"].strip() != "" and 1 or 0
    a.NeuteredDate = getdate(row["desexdate"])
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    a.CrossBreed = row["crossbreed"] == "TRUE" and 1 or 0
    if a.CrossBreed == 1:
        a.Breed2ID = 442
    if row["dob"].strip() != "":
        a.DateOfBirth = getdate(row["dob"])
    if a.DateOfBirth is None:
        a.DateOfBirth = a.DateBroughtIn
    a.IdentichipNumber = row["MicroChip"]
    if a.IdentichipNumber != "": a.Identichipped = 1
    a.Sex = getsex12(row["Sex"])
    a.Weight = asm.cfloat(row["weight"])
    a.BaseColourID = asm.colour_id_for_name(row["Colour"])
    a.ShelterLocation = 1
    a.generateCode(asm.type_name_for_id(a.AnimalTypeID))
    a.ReasonForEntry = row["dep_sReason"]
    if row["sOther"] != "":
        a.ReasonForEntry = row["sOther"]
    a.EntryReasonID = 11
    if row["circumstance"].find("Stray"):
        a.EntryReasonID = 7
    comments = "Original Colour: " + row["Colour"] + "/" + row["SecondaryColour"]
    comments += "\nCircumstance: " + row["circumstance"]
    a.HiddenAnimalDetails = comments
    if row["euthanasiaType"] != "0":
        a.Archived = 1
        a.DeceasedDate = a.DateBroughtIn
        a.PutToSleep = 1
        a.PTSReasonID = 4
    if row["crueltyCase"] == "TRUE":
        a.CrueltyCase = 1
    a.LastChangedDate = getdate(row["AddDateTime"])

# tblperson.csv
for row in asm.csv_to_list(PATH + "tblperson.csv"):
    o = asm.Owner()
    owners.append(o)
    o.ExtraID = row["recnum"].strip()
    o.OwnerTitle = row["Title"]
    o.OwnerForeNames = row["FirstName"]
    o.OwnerSurname = row["LastName"]
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.HomeTelephone = row["dep_HomePhone"]
    o.WorkTelephone = row["dep_WorkPhone"]
    o.MobileTelephone = row["dep_MobilePhone"]
    if addresses.has_key(row["physicalAddress"].strip()):
        a = addresses[row["physicalAddress"].strip()]
        o.OwnerAddress = a.address()
        o.OwnerTown = a.city
        o.OwnerCounty = a.state
        o.OwnerPostcode = a.postcode

# tbladoption.csv
for row in asm.csv_to_list(PATH + "tbladoption.csv"):
    # Find the animal and owner for this movement
    a = findanimal(row["animalid"].strip())
    o = findowner(row["recnum"].strip())
    if a != None and o != None:
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = o.ID
        m.AnimalID = a.ID
        if a.ActiveMovementDate is not None:
            m.MovementDate = a.ActiveMovementDate
        else:
            m.MovementDate = getdate(row["adddatetime"])
        m.MovementType = 1
        a.Archived = 1
        a.ActiveMovementType = 1
        a.ActiveMovementID = m.ID

# tblanimalvettreatments.csv
for row in asm.csv_to_list(PATH + "tblanimalvettreatments.csv"):
    av = asm.AnimalVaccination()
    av.DateRequired = getdate(row["dueDate"])
    if av.DateRequired is None:
        av.DateRequired = getdate(row["addDateTime"])
    av.DateOfVaccination = getdate(row["dateGiven"])
    a = findanimal(row["animalid"].strip())
    if a == None: continue
    av.AnimalID = a.ID
    av.VaccinationID = int(row["vacc"].strip())
    print av

# Now that everything else is done, output stored records
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

