#!/usr/bin/python

import asm, os

"""
Import script for ShelterBuddy MDB/SQL Server export with QueryExpress

Use ~/usr/access2csv-master/access2csv (which uses Jackcess)

cd ~/usr/access2csv-master
./access2csv --with-header --input ~/Downloads/*.accdb --output ~/Downloads/

Make an /images folder in PATH below if you have photos or documents to import.

2nd June, 2012 - 23rd Feb, 2017

The following query can be run after import to fix any records that didn't have an entry in tbladoption but had a valid DateOUT

insert into adoption (id, adoptionnumber, animalid, ownerid, retailerid, originalretailermovementid, movementdate, movementtype,
	returndate, returnedreasonid, insurancenumber, reasonforreturn, returnedbyownerid, reservationstatusid, donation,
    istrial, ispermanentfoster, trialenddate, comments,
    createdby, createddate, lastchangedby, lastchangeddate, recordversion)
    select nextval('seq_adoption'), sheltercode, id, 100, 0, 0, activemovementdate, 1, null, 0, '', '', 0, 0, 0, 0, 0, null, 'Fix for missing SB adopter info', 'missingfix', now(), 'missingfix', now(), 0
    from animal where activemovementdate is not null and activemovementtype = 1 and not exists(select id from adoption where animalid=animal.id)

"""

PATH = "/home/robin/tmp/asm3_import_data/shelterbuddy_gb2258/"

START_ID = 100

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
    global ppa
    if ppa.has_key(animalid):
        return ppa[animalid]
    return None

def findowner(recnum = ""):
    """ Looks for an owner with the given name in the collection
        of owners. If one wasn't found, None is returned """
    global ppo
    if ppo.has_key(recnum):
        return ppo[recnum]
    return None

def getdate(s):
    if s.find(" 1900") != -1: return None
    return asm.getdate_jackcess(s)

def getsblocation(locationid):
    global clocations
    for r in clocations:
        if r["LocationID"] == locationid:
            return r["Description"]
    return ""

def getsbnotes(animalid):
    global animalnotes
    if animalnotes.has_key(animalid):
        return animalnotes[animalid]
    else:
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
    streetDir = ""
    streetType = ""
    extraAddress = ""
    postcode = ""
    city = ""
    state = ""
    def address(self):
        s = "%s %s %s %s" % (self.streetNum.strip(), self.streetDir.strip(), self.streetName.strip(), self.streetType.strip())
        if s.strip() == "" and self.extraAddress.strip() != "": 
            s = self.extraAddress
        return s.strip()

# --- START OF CONVERSION ---
print "\\set ON_ERROR_STOP\nBEGIN;"

addresses = {}
streets = {}
suburbs = {}
vacctype = {}
medtype = {}
animalnotes = {}
users = {}
phonenumbers = {}

owners = []
ownerdonations = []
documents = {}
ppo = {}
ppa = {}
movements = []
animals = []
animalmedicals = []
animalvaccinations = []
logs = []

asm.setid("animal", START_ID)
asm.setid("dbfs", START_ID)
asm.setid("media", START_ID)
asm.setid("owner", START_ID)
asm.setid("ownerdonation", START_ID)
asm.setid("adoption", START_ID)
asm.setid("animalvaccination", START_ID)
asm.setid("animalmedical", START_ID)
asm.setid("animalmedicaltreatment", START_ID)
asm.setid("log", START_ID)

print "DELETE FROM animal WHERE ID >= %s;" % START_ID
print "DELETE FROM animalvaccination WHERE ID >= %s;" % START_ID
print "DELETE FROM animalmedical WHERE ID >= %s;" % START_ID
print "DELETE FROM animalmedicaltreatment WHERE ID >= %s;" % START_ID
print "DELETE FROM dbfs WHERE ID >= %s;" % START_ID
print "DELETE FROM media WHERE ID >= %s;" % START_ID
print "DELETE FROM owner WHERE ID >= %s;" % START_ID
print "DELETE FROM ownerdonation WHERE ID >= %s;" % START_ID
print "DELETE FROM adoption WHERE ID >= %s;" % START_ID
print "DELETE FROM log WHERE ID >= %s;" % START_ID

uo = asm.Owner()
uo.OwnerSurname = "Unknown"
uo.OwnerName = "Unknown"
owners.append(uo)

# load lookups into memory
cnotes = asm.csv_to_list(PATH + "dbo_tblNotes.csv")
cspecies = asm.csv_to_list(PATH + "dbo_tblSpecies.csv")
cbreeds = asm.csv_to_list(PATH + "dbo_tblAnimalBreeds.csv")
ctypes = asm.csv_to_list(PATH + "dbo_AnimalType.csv")
cpaymentmethods = asm.csv_to_list(PATH + "dbo_tblPaymentTypes.csv")
clocations = asm.csv_to_list(PATH + "dbo_tblPhysicalLocation.csv")

# tblDocument.csv
for row in asm.csv_to_list(PATH + "dbo_tblDocument.csv"):
    if row["objectypeid"] == "0" and row["extension"] == "jpg" and row["isDefault"] == "-1":
        documents[row["objectid"]] = PATH + "images/doc_%s.jpg" % row["docID"]

# tblNotes
for r in cnotes:
    if r["fieldText"] != "":
        animalnotes[r["animalID"]] = r["fieldText"]

# tblPhoneNumber
for r in asm.csv_to_list(PATH + "dbo_tblPhoneNumber.csv"):
    if r["enteredValue"] != "": 
        phonenumbers[r["Id"]] = r["phoneTypeId"] + " " + r["enteredValue"]

# tblSuburblist.csv
for row in asm.csv_to_list(PATH + "dbo_tblSuburbList.csv"):
    s = SBSuburb()
    s.id = row["ID"].strip()
    s.suburb = row["Suburb"]
    s.postcode = row["postcode"]
    s.state = row["state"]
    suburbs[s.id] = s

# tblStreets.csv
for row in asm.csv_to_list(PATH + "dbo_tblStreets.csv"):
    streets[row["type_id"]] = row["name"]
    
# tblAnimalVacc.csv
print "DELETE FROM vaccinationtype WHERE ID > 200;"
for row in asm.csv_to_list(PATH + "dbo_tblAnimalVacc.csv"):
    vc = row["vaccCode"].strip()
    vt = row["description"] + " " + row["dep_type"]
    vacctype[vc] = vt
    print "INSERT INTO vaccinationtype VALUES (%s, '%s');" % (vc, vt.replace("'", "`"))

# lookupconsultmedications.csv
for row in asm.csv_to_list(PATH + "dbo_lookupConsultMedications.csv"):
    medtype[row["ID"]] = row["description"]

# users.csv
for row in asm.csv_to_list(PATH + "dbo_Users.csv"):
    users[row["UserID"]] = row["Username"]

# tblAddress.csv
for row in asm.csv_to_list(PATH + "dbo_tblAddress.csv"):
    s = SBAddress()
    s.id = row["id"].strip()
    s.streetNum = row["streetNum"]
    s.streetName = row["streetName"]
    s.streetDir = row["dirOne"]
    if row["streetType"] in streets:
        s.streetType = streets[row["streetType"]]
    s.extraAddress = row["extraAddress"]
    s.postcode = row["postcode"]
    if suburbs.has_key(row["suburbId"]):
        sb = suburbs[row["suburbId"]]
        s.city = sb.suburb
        s.state = sb.state
    addresses[s.id] = s

# tblAnimal.csv
for row in asm.csv_to_list(PATH + "dbo_tblAnimal.csv"):
    a = asm.Animal()
    animals.append(a)
    ppa[row["AnimalID"]] = a
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
    if typecol == "Puppy": a.SpeciesID = 1
    if typecol == "Kitten": a.SpeciesID = 2
    a.BreedID = asm.breed_id_for_name(breedcol)
    a.Breed2ID = asm.breed_id_for_name(breed2col)
    if row["DateIN"].strip() != "": 
        a.DateBroughtIn = getdate(row["DateIN"])
        if a.DateBroughtIn is None:
            a.DateBroughtIn = getdate(row["AddDateTime"])
            if a.DateBroughtIn is None:
                a.DateBroughtIn = asm.now()
    if row["DateOUT"].strip() != "":
        a.ActiveMovementDate = getdate(row["DateOUT"])
        if a.ActiveMovementDate is not None:
            a.ActiveMovementType = 1
            a.Archived = 1
        elif a.DateBroughtIn.year < asm.now().year - 1:
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
    if "size" in row: a.Size = asm.size_id_for_name(row["size"])
    a.BaseColourID = asm.colour_id_for_name(row["Colour"], firstWordOnly=True)
    a.ShelterLocation = 1
    a.generateCode(asm.type_name_for_id(a.AnimalTypeID))
    if "dep_sReason" in row: a.ReasonForEntry = row["dep_sReason"]
    if row["sOther"] != "":
        a.ReasonForEntry = row["sOther"]
    a.EntryReasonID = 11
    if row["circumstance"].find("Stray"):
        a.EntryReasonID = 7
        a.EntryTypeID = 2
    comments = "Original Type: " + typecol
    comments += "\nOriginal Breed: " + breedcol + "/" + breed2col
    comments += "\nOriginal Colour: " + row["Colour"] + "/" + row["SecondaryColour"]
    comments += "\nLocation: " + getsblocation(row["refugelocation"])
    comments += "\nCircumstance: " + row["circumstance"]
    a.HiddenAnimalDetails = comments
    a.AnimalComments = getsbnotes(row["AnimalID"])
    # StatusID == 2 is euth in SB, 23 is unassisted death, 133 is death in foster - tblAnimalStatus contains explanations
    if row["StatusID"] in ("2", "23", "133"):
        a.DeceasedDate = getdate(row["dep_DeceasedDate"]) or getdate(row["statusdate"]) or a.DateBroughtIn
        a.Archived = 1
        a.PTSReasonID = 2
        if row["StatusID"] == "2": 
            a.PutToSleep = 1
            a.PTSReasonID = 4
    if row["crueltyCase"] == "1":
        a.CrueltyCase = 1
    a.CreatedBy = "conversion/%s" % users[row["AddAdminID"]]
    a.LastChangedDate = getdate(row["AddDateTime"])
    # Do we have a default image for this animal in the images folder and document table?
    if documents.has_key(row["AnimalID"]):
        imagedata = asm.load_image_from_file(documents[row["AnimalID"]])
        if imagedata is not None:
            asm.animal_image(a.ID, imagedata)
    # Status 16 is reclaim, could not find any indicator of target
    if row["StatusID"] == "16":
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = uo.ID
        m.AnimalID = a.ID
        m.MovementDate = getdate(row["statusdate"])
        m.MovementType = 5
        a.Archived = 1
        a.ActiveMovementType = 5
        a.ActiveMovementID = m.ID
    # Status 22 is transferred out, could not find any indicator of target
    if row["StatusID"] == "22":
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = uo.ID
        m.AnimalID = a.ID
        m.MovementDate = getdate(row["statusdate"])
        m.MovementType = 3
        a.Archived = 1
        a.ActiveMovementType = 3
        a.ActiveMovementID = m.ID

# tblAnimalDetails.csv
for row in asm.csv_to_list(PATH + "dbo_tblAnimalDetails.csv"):
    if not row["animalID"] in ppa: continue
    a = ppa[row["animalID"]]
    if row["oldDatabaseNumber"] != "": a.ShortCode = row["oldDatabaseNumber"]

# tblPerson.csv
for row in asm.csv_to_list(PATH + "dbo_tblPerson.csv"):
    o = asm.Owner()
    owners.append(o)
    ppo[row["recnum"]] = o
    o.OwnerTitle = row["Title"]
    o.OwnerForeNames = row["FirstName"]
    o.OwnerSurname = row["LastName"]
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    if "dep_HomePhone" in row: o.HomeTelephone = row["dep_HomePhone"]
    if "dep_WorkPhone" in row: o.WorkTelephone = row["dep_WorkPhone"]
    if "dep_MobilePhone" in row: o.MobileTelephone = row["dep_MobilePhone"]
    if "origin" in row and row["origin"].find("Foster") != -1: o.IsFosterer = 1
    if "origin" in row and row["origin"].find("Volunteer") != -1: o.IsVolunteer = 1
    if addresses.has_key(row["physicalAddress"].strip()):
        a = addresses[row["physicalAddress"].strip()]
        o.OwnerAddress = a.address()
        o.OwnerTown = a.city
        o.OwnerCounty = a.state
        o.OwnerPostcode = a.postcode

# tblPersonPhoneNumber.csv
for row in asm.csv_to_list(PATH + "dbo_tblPersonPhoneNumber.csv"):
    if row["PersonId"] in ppo and row["PhoneNumberId"] in phonenumbers:
        o = ppo[row["PersonId"]]
        ptype, num = phonenumbers[row["PhoneNumberId"]].split(" ", 1)
        if ptype == "1":
            o.HomeTelephone = num
        elif ptype == "2":
            o.WorkTelephone = num
        elif ptype == "3":
            o.MobileTelephone = num

# tblFosterInstructions.csv
for row in asm.csv_to_list(PATH + "dbo_tblFosterInstructions.csv"):
    # Find the animal and owner for this movement
    a = findanimal(row["animalID"])
    o = findowner(row["recnum"])
    if a != None and o != None:
        o.IsFosterer = 1
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = o.ID
        m.AnimalID = a.ID
        m.MovementDate = getdate(row["dateIn"])
        m.ReturnDate = getdate(row["dateDue"])
        m.Comments = row["careInstructions"]
        m.MovementType = 2
        a.Archived = 0
        a.ActiveMovementType = 2
        a.ActiveMovementID = m.ID

# tblAdoption.csv
for row in asm.csv_to_list(PATH + "dbo_tblAdoption.csv"):
    # Find the animal and owner for this movement
    a = findanimal(row["animalid"])
    o = findowner(row["recnum"])
    if a != None and o != None:
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = o.ID
        m.AnimalID = a.ID
        m.MovementDate = getdate(row["adddatetime"])
        m.MovementType = 1
        a.Archived = 1
        a.ActiveMovementType = 1
        a.ActiveMovementID = m.ID

# tblAnimalVetTreatments.csv
for row in asm.csv_to_list(PATH + "dbo_tblAnimalVetTreatments.csv"):
    av = asm.AnimalVaccination()
    av.DateRequired = getdate(row["dueDate"])
    if av.DateRequired is None:
        av.DateRequired = getdate(row["addDateTime"])
    av.DateOfVaccination = getdate(row["dateGiven"])
    if av.DateOfVaccination is None: 
        av.DateOfVaccination = av.DateRequired
    a = findanimal(row["animalid"])
    if a is None: continue
    av.AnimalID = a.ID
    av.VaccinationID = int(row["vacc"].strip())
    animalvaccinations.append(av)

# tblMedications.csv
"""
for row in asm.csv_to_list(PATH + "dbo_tblMedications.csv"):
    a = findanimal(row["animalID"])
    if a is None: continue
    startdate = getdate(row["datefrom"])
    treatmentname = medtype[row["medicationID"]]
    dosage = row["notes"]
    comments = row["notes"]
    if startdate is not None:
        animalmedicals.append(asm.animal_regimen_single(a.ID, startdate, treatmentname, dosage, comments))
"""

# tblAnimalVetMedicalNote.csv
for row in asm.csv_to_list(PATH + "dbo_tblAnimalVetMedicalNote.csv"):
    a = findanimal(row["animalID"])
    if a is None: continue
    l = asm.Log()
    l.LogTypeID=3
    l.Date = getdate(row["createDate"])
    l.LinkID = a.ID
    l.LinkType = 0
    l.Comments = row["noteText"]
    logs.append(l)

# tblReceiptEntry.csv
for row in asm.csv_to_list(PATH + "dbo_tblReceiptEntry.csv"):
    od = asm.OwnerDonation()
    od.DonationTypeID = 1
    pm = getsbpaymentmethod(row["method"])
    od.DonationPaymentID = 1
    if pm.find("Check") != -1: od.DonationPaymentID = 2
    if pm.find("Credit Card") != -1: od.DonationPaymentID = 3
    if pm.find("Debit Card") != -1: od.DonationPaymentID = 4
    od.Date = getdate(row["receiptdate"])
    od.OwnerID = findowner(row["recnum"]).ID
    od.Donation = asm.get_currency(row["dep_amount"])
    comments = "Check No: " + row["chequeNumber"]
    comments += "\nMethod: " + pm
    comments += "\n" + row["NotesToPrint"]
    od.Comments = comments
    ownerdonations.append(od)

# tblQuestionAnswersHistory (behaviour -> Logs)
for row in asm.csv_to_list(PATH + "dbo_tblQuestionAnswersHistory.csv"):
    if row["questionType"] != "behaviour": continue
    a = findanimal(row["animalID"])
    if a is None: continue
    a.ExtraID += row["questionText"] + " = " + row["answerText"] + "\n" 
for a in animals:
    if a.ExtraID != "":
        l = asm.Log()
        l.LogTypeID = 3
        l.Date = a.DateBroughtIn
        l.LinkID = a.ID
        l.LinkType = 0
        l.Comments = a.ExtraID
        logs.append(l)

"""
# Used to populate an additional field called Tag with any SB tag number set
for row in asm.csv_to_list(PATH + "dbo_tbltaghistory.csv"):
    a = findanimal(row["animalId"])
    if a is not None: 
        asm.additional_field("Tag", 2, a.ID, row["tagNumber"])
"""

# Now that everything else is done, output stored records
print "DELETE FROM primarykey;"
print "DELETE FROM configuration WHERE ItemName Like 'VariableAnimalDataUpdated';"
for a in animals:
    print a
for am in animalmedicals:
    print am
for av in animalvaccinations:
    print av
for o in owners:
    print o
for od in ownerdonations:
    print od
for m in movements:
    print m
for l in logs:
    print l

asm.stderr_summary(animals=animals, animalmedicals=animalmedicals, animalvaccinations=animalvaccinations, logs=logs, owners=owners, ownerdonations=ownerdonations, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

