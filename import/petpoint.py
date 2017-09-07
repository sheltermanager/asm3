#!/usr/bin/python

import asm

"""
Import script for PetPoint databases exported as CSV
(requires AnimalIntakeWithResultsExtended.csv, AnimalMemoHistory.csv and PersonByAssociationExtended.csv)

Can optionally import vacc and tests too, the PP reports
are MedicalVaccineExpress and MedicalTestsExpress

3rd March - 30th August, 2017
"""

# The shelter's petfinder ID for grabbing animal images for adoptable animals
PETFINDER_ID = ""

INTAKE_FILENAME = "data/petpoint_rw1412/animals.csv"
MEMO_FILENAME = "data/petpoint_rw1412/memo.csv"
PERSON_FILENAME = "data/petpoint_rw1412/person.csv"
VACC_FILENAME = "data/petpoint_rw1412/vaccinations.csv"
TEST_FILENAME = "data/petpoint_rw1412/tests.csv"

# Whether or not the vaccine and test files are in two row stacked format
MEDICAL_TWO_ROW_FORMAT = False

def findowner(ownername = ""):
    """ Looks for an owner with the given name in the collection
        of owners. If one wasn't found, None is returned """
    for o in owners:
        if o.OwnerName == ownername.strip():
            return o
    return None

def getdate(d):
    return asm.getdate_guess(d)

# --- START OF CONVERSION ---

owners = []
movements = []
animals = []
animaltests = []
animalvaccinations = []
logs = []
ppa = {}
ppo = {}

asm.setid("animal", 100)
asm.setid("animaltest", 100)
asm.setid("animalvaccination", 100)
asm.setid("log", 100)
asm.setid("owner", 100)
asm.setid("adoption", 100)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM internallocation;"
print "DELETE FROM animal WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM animaltest WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM animalvaccination WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM log WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM owner WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM adoption WHERE ID >= 100 AND CreatedBy = 'conversion';"

# Create an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname

pf = ""
if PETFINDER_ID != "":
    asm.setid("media", 100)
    asm.setid("dbfs", 200)
    print "DELETE FROM media WHERE ID >= 100;"
    print "DELETE FROM dbfs WHERE ID >= 200;"
    pf = asm.petfinder_get_adoptable(PETFINDER_ID)

# Deal with people first (if set)
if PERSON_FILENAME != "":
    for d in asm.csv_to_list(PERSON_FILENAME):
        # Each row contains a person
        o = asm.Owner()
        owners.append(o)
        ppo[d["Person ID"]] = o
        o.OwnerForeNames = d["Name First"]
        o.OwnerSurname = d["Name Last"]
        o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
        o.OwnerAddress = "%s %s %s %s" % (d["Street Number"], d["Street Name"], d["Street Type"], d["Street Direction"])
        o.OwnerTown = d["City"]
        o.OwnerCounty = d["Province"]
        o.OwnerPostcode = d["Postal Code"]
        o.EmailAddress = d["Email"]
        o.HomeTelephone = d["Phone Number"]
        o.IsBanned = asm.iif(d["Association"] == "Do Not Adopt", 1, 0)
        o.IsDonor = asm.iif(d["Association"] == "Donor", 1, 0)
        o.IsMember = asm.iif(d["Association"] == "Mailing List", 1, 0)
        o.IsFosterer = asm.iif(d["Association"] == "Foster", 1, 0)
        o.IsStaff = asm.iif(d["Association"] == "Employee", 1, 0)
        o.IsVet = asm.iif(d["Association"] == "Operation by" or d["Association"] == "Medical Personnel", 1, 0)
        o.IsVolunteer = asm.iif(d["Association"] == "Volunteer", 1, 0)
        o.ExcludeFromBulkEmail = asm.iif(d["Contact By Email"] == "Yes", 1, 0)

# Sort the data on intake date ascending
for d in sorted(asm.csv_to_list(INTAKE_FILENAME), key=lambda k: getdate(k["Intake Date"])):
    # Each row contains an animal, intake and outcome
    if ppa.has_key(d["Animal ID"]):
        a = ppa[d["Animal ID"]]
    else:
        a = asm.Animal()
        animals.append(a)
        ppa[d["Animal ID"]] = a
        if d["Species"] == "Cat":
            a.AnimalTypeID = 11 # Unwanted Cat
            if d["Intake Type"] == "Stray":
                a.AnimalTypeID = 12 # Stray Cat
        elif d["Species"] == "Dog":
            a.AnimalTypeID = 2 # Unwanted Dog
            if d["Intake Type"] == "Stray":
                a.AnimalTypeID = 10 # Stray Dog
        else:
            a.AnimalTypeID = 40 # Misc
        a.SpeciesID = asm.species_id_for_name(d["Species"])
        a.AnimalName = d["Animal Name"]
        if a.AnimalName.strip() == "":
            a.AnimalName = "(unknown)"
        a.DateBroughtIn = getdate(d["Intake Date"])
        if a.DateBroughtIn is None:
            a.DateBroughtIn = asm.today()
        if "Date Of Birth" in d and d["Date Of Birth"].strip() != "":
            a.DateOfBirth = getdate(d["Date Of Birth"])
        else:
            a.DateOfBirth = asm.subtract_days(a.DateBroughtIn, 365)
        a.CreatedDate = a.DateBroughtIn
        a.LastChangedDate = a.DateBroughtIn
        if d["Intake Type"] == "Transfer In":
            a.IsTransfer = 1
        a.generateCode()
        a.ShortCode = d["Animal ID"]
        if "Distinguishing Markings" in d: a.Markings = d["Distinguishing Markings"]
        a.IsNotAvailableForAdoption = 0
        a.ShelterLocation = asm.location_id_for_name(d["Location"])
        a.Sex = asm.getsex_mf(d["Gender"])
        a.Size = 2
        a.Neutered = d["Altered"] == "Yes" and 1 or 0
        a.EntryReasonID = 17 # Surrender
        if d["Intake Type"] == "Stray": a.EntryReasonID = 7 # Stray
        if d["Intake Type"] == "Transfer In": a.EntryReasonID = 15 # Transfer from other shelter
        a.ReasonForEntry = d["Reason"]
        if "Microchip Issue Date" in d: a.IdentichipDate = getdate(d["Microchip Issue Date"])
        if "Microchip Number" in d: a.IdentichipNumber = d["Microchip Number"]
        a.IsGoodWithCats = 2
        a.IsGoodWithDogs = 2
        a.IsGoodWithChildren = 2
        if "Intake Condition" in d: a.AsilomarIntakeCategory = d["Intake Condition"] == "Healthy" and 0 or 1
        a.HouseTrained = 0
        if a.IdentichipNumber != "": 
            a.Identichipped = 1
        a.Archived = 0
        comments = "Intake type: " + d["Intake Type"] + " " + d["Intake Subtype"] + ", breed: " + d["Primary Breed"] + "/"
        if "Secondary Breed" in d: comments += d["Secondary Breed"]
        comments += ", age: " + d["Age Group"]
        if "Intake Condition" in d: comments += ", intake condition: " + d["Intake Condition"]
        a.BreedID = asm.breed_id_for_name(d["Primary Breed"])
        a.Breed2ID = a.BreedID
        a.BreedName = asm.breed_name_for_id(a.BreedID)
        a.CrossBreed = 0
        if "Secondary Breed" in d and d["Secondary Breed"].strip() != "":
            a.CrossBreed = 1
            if d["Secondary Breed"] == "Mix":
                a.Breed2ID = 442
            else:
                a.Breed2ID = asm.breed_id_for_name(d["Secondary Breed"])
            if a.Breed2ID == 1: a.Breed2ID = 442
            a.BreedName = "%s / %s" % ( asm.breed_name_for_id(a.BreedID), asm.breed_name_for_id(a.Breed2ID) )
        a.HiddenAnimalDetails = comments

        if d["Admitter"] != "" and d["Intake Type"] == "Owner/Guardian Surrender":
            o = findowner(d["Admitter"])
            if o == None:
                o = asm.Owner()
                owners.append(o)
                o.OwnerName = d["Admitter"]
                bits = o.OwnerName.split(" ")
                if len(bits) > 1:
                    o.OwnerForeNames = bits[0]
                    o.OwnerSurname = bits[len(bits)-1]
                else:
                    o.OwnerSurname = o.OwnerName
                o.OwnerAddress = d["Street Number"] + " " + d["Street Name"] + " " + d["Street Type"] + " " + d["Street Direction"]
                o.OwnerTown = d["City"]
                o.OwnerCounty = d["Province"]
                o.OwnerPostcode = d["Postal Code"]
                o.EmailAddress = d["Admitter's Email"]
                o.HomeTelephone = d["Admitter's Home Phone"]
                o.MobileTelephone = d["Admitter's Cell Phone"]
            a.OriginalOwnerID = o.ID
            a.BroughtInByOwnerID = o.ID

    if d["Intake Type"] == "Return":
        # Return the most recent adoption for this animal
        for m in movements:
            if m.AnimalID == a.ID and m.ReturnDate is None and m.MovementType == 1:
                m.ReturnDate = getdate(d["Intake Date"])
                m.ReturnedReasonID = 17 # Surrender
                a.Archived = 0 # Return to shelter so another movement takes it away again
                break

    o = None
    if d["Outcome Person Name"].strip() != "":
        o = findowner(d["Outcome Person Name"])
        if o is None:
            o = asm.Owner()
            owners.append(o)
            o.OwnerName = d["Outcome Person Name"]
            bits = o.OwnerName.split(" ")
            if len(bits) > 1:
                o.OwnerForeNames = bits[0]
                o.OwnerSurname = bits[len(bits)-1]
            else:
                o.OwnerSurname = o.OwnerName
            o.OwnerAddress = d["Out Street Number"] + " " + d["Out Street Name"] + " " + d["Out Street Type"] + " " + d["Out Street Direction"]
            o.OwnerTown = d["Out City"]
            o.OwnerCounty = d["Out Province"]
            o.OwnerPostcode = d["Out Postal Code"]
            o.EmailAddress = d["Out Email"]
            o.HomeTelephone = d["Out Home Phone"]
            o.MobileTelephone = d["Out Cell Phone"]
    elif d["Outcome Agency Name"].strip() != "":
        o = findowner(d["Outcome Agency Name"])
        if o is None:
            o = asm.Owner()
            owners.append(o)
            o.OwnerName = d["Outcome Agency Name"]
            bits = o.OwnerName.split(" ")
            if len(bits) > 1:
                o.OwnerForeNames = bits[0]
                o.OwnerSurname = bits[len(bits)-1]
            else:
                o.OwnerSurname = o.OwnerName
            o.OwnerAddress = d["Agency Street Number"] + " " + d["Agency Street Name"] + " " + d["Agency Street Type"] + " " + d["Agency Street Direction"]
            o.OwnerTown = d["Agency City"]
            o.OwnerCounty = d["Agency Province"]
            o.OwnerPostcode = d["Agency Postal Code"]
            o.EmailAddress = d["Agency Email"]
            o.HomeTelephone = d["Agency Home Phone"]
            o.MobileTelephone = d["Agency Cell Number"]
            o.IsShelter = 1

    ot = d["Outcome Type"]
    ost = d["Outcome Subtype"]
    od = getdate(d["Outcome Date"])
    if (ot == "Transfer Out" and ost == "Potential Adopter" and d["Outcome Person Name"] != "") or ot == "Adoption":
        if a is None or o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = od
        m.Comments = ot + "/" + ost
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 1
        a.LastChangedDate = od
        movements.append(m)
    elif ot == "Transfer Out":
        if a is None or o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 3
        m.MovementDate = od
        m.Comments = ot + "/" + ost
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 3
        a.LastChangedDate = od
        movements.append(m)
    elif ot == "Return to Owner/Guardian":
        if a is None or o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 4
        m.MovementDate = od
        m.Comments = ot + "/" + ost
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 3
        a.LastChangedDate = od
        movements.append(m)
    elif ot == "Died":
        a.PutToSleep = 0
        a.DeceasedDate = od
        a.Archived = 1
        a.PTSReason = ot + "/" + ost 
        a.LastChangedDate = od
    elif ot == "Euthanasia":
        a.PutToSleep = 1
        a.DeceasedDate = od
        a.Archived = 1
        a.PTSReason = ot + "/" + ost 
        a.LastChangedDate = od
    elif ot == "Service Out" or ot == "Clinic Out":
        if a is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = 0
        if o is not None:
            m.OwnerID = o.ID
        m.MovementType = 8
        m.MovementDate = od
        m.Comments = ot + "/" + ost
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 8
        a.LastChangedDate = od
        movements.append(m)

    # Get the current image for this animal from PetFinder if it is on shelter
    if a.Archived == 0 and PETFINDER_ID != "" and pf != "":
        asm.petfinder_image(pf, a.ID, a.AnimalName)

# Turn memos into history logs
if MEMO_FILENAME != "":
    for d in asm.csv_to_list(MEMO_FILENAME):
        if ppa.has_key(d["AnimalID"]):
            a = ppa[d["AnimalID"]]
            l = asm.Log()
            logs.append(l)
            l.LogTypeID = 3 # History
            l.LinkID = a.ID
            l.LinkType = 0
            l.Date = asm.getdate_mmddyyyy(d["textbox20"])
            if l.Date is None:
                l.Date = asm.now()
            l.Comments = d["Textbox131"]

vacc = asm.csv_to_list(VACC_FILENAME)

def process_vacc(animalno, vaccdate = None, vaccexpires = None, vaccname = ""):
    """ Processes a vaccination record. PP have multiple formats of this data file """
    if ppa.has_key(animalno):
        a = ppa[animalno]
    else:
        asm.stderr("cannot process vacc %s, %s, %s, - no matching animal" % (animalno, vaccdate, vaccname))
        return
    av = asm.AnimalVaccination()
    animalvaccinations.append(av)
    if vaccdate is None:
        vaccdate = a.DateBroughtIn
    av.AnimalID = a.ID
    av.VaccinationID = 8
    vaccmap = {
        "Bordatella": 6,
        "Bordetella": 6,
        "6-in-1 Canine": 8,
        "5-in-1 Canine": 8,
        "4-in-1 Canine": 8,
        "D-A2-P": 8,
        "Rabies": 4,
        "FeLV": 12,
        "FVRCP": 14,
        "Distemper": 1
    }
    for k, i in vaccmap.iteritems():
        if vaccname.find(k) != -1: av.VaccinationID = i
    av.DateRequired = vaccdate
    av.DateOfVaccination = vaccdate
    av.DateExpires = vaccexpires
    av.Comments = "Type: %s" % vaccname

if vacc is not None:
    if MEDICAL_TWO_ROW_FORMAT:
        odd = True
        vaccname = ""
        vaccdate = None
        vaccexpires = None
        animalno = ""
        for v in vacc:
            if odd:
                animalno = v["Animal #"]
                vaccname = v["Vaccination"]
                vaccexpires = getdate(v["Re-Vac Date/Time"])
            else:
                vaccdate = getdate(v["Status"])
                process_vacc(animalno, vaccdate, vaccexpires, vaccname)
            odd = not odd
    else:
        for v in vacc:
            process_vacc(v["AnimalID"], getdate(v["Date"]), None, v["RecordType3"])
            #process_vacc(v["StatusDateTime3"], getdate(v["BodyWeight"]), None, v["RecordType3"]) # Once saw a broken version of this file like this

test = asm.csv_to_list(TEST_FILENAME)

def process_test(animalno, testdate = None, testname = "", result = ""):
    """ Process a test record """
    if ppa.has_key(animalno):
        a = ppa[animalno]
    else:
        asm.stderr("cannot process test %s, %s, %s, %s - no matching animal" % (animalno, testdate, testname, result))
        return
    at = asm.AnimalTest()
    animaltests.append(at)
    at.AnimalID = a.ID
    if testdate is None:
        testdate = a.DateBroughtIn
    at.DateRequired = testdate
    at.DateOfTest = testdate
    asmresult = 0
    if result == "Negative": asmresult = 1
    if result == "Positive": asmresult = 2
    at.TestResultID = asmresult + 1
    if testname == "Heartworm":
        a.HeartwormTested = 1
        a.HeartwormTestDate = testdate
        a.HeartwormTestResult = asmresult
        at.TestTypeID = 3
    elif testname == "FIV":
        a.CombiTested = 1
        a.CombiTestDate = testdate
        a.CombiTestResult = asmresult
        at.TestTypeID = 1
    elif testname == "FELV":
        a.CombiTested = 1
        a.CombiTestDate = testdate
        a.FLVResult = asmresult
        at.TestTypeID = 2
    else:
        at.TestTypeID = 1
        at.Comments = "Test for %s" % testname

if test is not None:
    if MEDICAL_TWO_ROW_FORMAT:
        odd = True
        testname = ""
        testdate = None
        animalno = ""
        result = ""
        for t in test:
            if odd:
                animalno = t["Animal #"]
                testname = t["Test"]
            else:
                testdate = getdate(t["Status"])
                result = t["Test For"]
                process_test(animalno, testdate, testname, result)
            odd = not odd
    else:
        for t in test:
            process_test(t["AnimalID"], getdate(t["ItemStatusDateTime"]), t["TestForCondition"], t["Result"])

# Run back through the animals, if we have any that are still
# on shelter after 1 year, add an adoption to an unknown owner
for a in animals:
    if a.Archived == 0 and a.DateBroughtIn < asm.subtract_days(asm.now(), 365):
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = uo.ID
        m.MovementType = 1
        m.MovementDate = a.DateBroughtIn
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = a.DateBroughtIn
        a.ActiveMovementType = 1
        movements.append(m)

# Now that everything else is done, output stored records
for k,v in asm.locations.iteritems():
    print v
for a in animals:
    print a
for at in animaltests:
    print at
for av in animalvaccinations:
    print av
for o in owners:
    print o
for m in movements:
    print m
for l in logs:
    print l

asm.stderr_summary(animals=animals, animaltests=animaltests, animalvaccinations=animalvaccinations, logs=logs, owners=owners, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

