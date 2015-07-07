#!/usr/bin/python

import asm

"""
Import script for ShelterBuddy MDB/SQL Server export with QueryExpress
2nd June, 2012 - 7th July, 2015
"""

PATH = "data/shelterbuddy_uvhs/"

# Use gmdb2 to export these tables from Access
# OR use queryexpress to do it from SQL Server Ex2005

# animaltype
# tbladdress.csv
# tbladoption.csv
# tblanimal.csv
# tblanimalbreeds.csv
# tblanimalvacc.csv
# tblanimalvettreatments.csv
# tblnotes.csv
# tblpaymenttypes.csv
# tblperson.csv
# tblreceiptentry.csv
# tblspecies.csv
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
    if s.find("/1900") != -1 or s.find("/00") != -1: return None
    return asm.getdate_mmddyy(s)

def getsbnotes(animalid):
    global cnotes
    for r in cnotes:
        if r["animalID"] == animalid and r["fieldText"] != "":
            return r["fieldText"]
    return ""

def getsbpaymentmethod(pmid):
    global cpaymentmethods
    for r in cpaymentmethods:
        if r["id"] == pmid:
            return r["PaymentType"]
    return ""

def getsbspecies(id):
    global cspecies
    for r in cspecies:
        if r["id"] == id:
            return r
    return None

def getsbtypenamefromspeciesid(speciesid):
    sbs = getsbspecies(speciesid)
    if sbs is None: return ""
    id = sbs["typeID"]
    global ctypes
    for r in ctypes:
        if r["ID"] == id:
            #print "getsbtypenamefromspeciesid: %s = %s" % (speciesid, r["Description"])
            return r["Description"]
    return ""

def getsbbreednamefromspeciesid(speciesid):
    sbs = getsbspecies(speciesid)
    if sbs is None: return ""
    id = sbs["breedID"]
    global cbreeds
    for r in cbreeds:
        if r["BreedID"] == id:
            #print "getsbbreednamefromspeciesid: %s = %s" % (speciesid, r["Breed"])
            return r["Breed"]
    return ""

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
asm.setid("ownerdonation", 100)
asm.setid("adoption", 100)
asm.setid("animalvaccination", 100)

print "DELETE FROM animal WHERE ID >= 100;"
print "DELETE FROM animalvaccination WHERE ID >= 100;"
print "DELETE FROM owner WHERE ID >= 100;"
print "DELETE FROM ownerdonation WHERE ID >= 100;"
print "DELETE FROM adoption WHERE ID >= 100;"

# load lookups into memory
cnotes = asm.csv_to_list(PATH + "tblnotes.csv")
cspecies = asm.csv_to_list(PATH + "tblspecies.csv")
cbreeds = asm.csv_to_list(PATH + "tblanimalbreeds.csv")
ctypes = asm.csv_to_list(PATH + "animaltype.csv")
cpaymentmethods = asm.csv_to_list(PATH + "tblpaymenttypes.csv")

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
    vc = row["vaccCode"].strip()
    vt = row["description"]
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
    # Depending on the version of shelterbuddy, sometimes there's 
    ## type, breed and secondBreed cols that dereference the tables
    typecol = ""
    breedcol = ""
    breed2col = ""
    if row.has_key("type"):
        typecol = row["type"]
        breedcol = row["breed"]
        breed2col = row["secondBreed"]
    else:
        # We're going to have to look them up from the speciesID and
        # secondarySpeciesID fields
        typecol = getsbtypenamefromspeciesid(row["speciesID"])
        breedcol = getsbbreednamefromspeciesid(row["speciesID"])
        breed2col = getsbbreednamefromspeciesid(row["secondarySpeciesID"])
    a.AnimalTypeID = asm.type_id_for_name(typecol)
    a.SpeciesID = asm.species_id_for_name(typecol)
    a.BreedID = asm.breed_id_for_name(breedcol)
    a.Breed2ID = asm.breed_id_for_name(breed2col)
    if row["DateIN"].strip() != "": 
        a.DateBroughtIn = getdate(row["DateIN"])
        if a.DateBroughtIn is None:
            a.DateBroughtIn = getdate(row["AddDateTime"])
            if a.DateBroughtIn is None:
                print "BOLLOCKS: " + str(row)
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
    comments = "Original Type: " + typecol
    comments += "\nOriginal Breed: " + breedcol + "/" + breed2col
    comments += "\nOriginal Colour: " + row["Colour"] + "/" + row["SecondaryColour"]
    comments += "\nCircumstance: " + row["circumstance"]
    a.HiddenAnimalDetails = comments
    a.AnimalComments = getsbnotes(row["AnimalID"])
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

# tblreceiptentry.csv
for row in asm.csv_to_list(PATH + "tblreceiptentry.csv"):
    od = asm.OwnerDonation()
    od.DonationTypeID = 1
    pm = getsbpaymentmethod(row["paymentmethod"])
    od.DonationPaymentID = 1
    if pm.find("Check") != -1: od.DonationPaymentID = 2
    if pm.find("Credit Card") != -1: od.DonationPaymentID = 3
    if pm.find("Debit Card") != -1: od.DonationPaymentID = 4
    od.Date = getdate(row["receiptdate"])
    od.OwnerID = findowner(row["recnum"]).ID
    od.Donation = asm.get_currency(row["Amount"])
    comments = "Check No: " + row["chequeno"]
    comments += "\nMethod: " + pm
    comments += "\n" + row["NotesToPrint"]
    od.Comments = comments
    print od

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

