#!/usr/bin/python

import asm

"""
Import script for PetPoint databases exported as CSV
(requires AnimalIntakeWithResultsExtended.csv)

Can optionally import vacc and tests too, the PP reports
are MedicalVaccineExpress and MedicalTestsExpress

3rd March - 14th February, 2016
"""

# The shelter's petfinder ID for grabbing animal images for adoptable animals
PETFINDER_ID = ""

INTAKE_FILENAME = "data/pp_bk1217.csv"
VACC_FILENAME = ""
TEST_FILENAME = ""

def findowner(ownername = ""):
    """ Looks for an owner with the given name in the collection
        of owners. If one wasn't found, None is returned """
    for o in owners:
        if o.OwnerName == ownername.strip():
            return o
    return None

# --- START OF CONVERSION ---

owners = []
movements = []
animals = []
animaltests = []
animalvaccinations = []
ppa = {}

asm.setid("animal", 100)
asm.setid("animaltest", 100)
asm.setid("animalvaccination", 100)
asm.setid("owner", 100)
asm.setid("adoption", 100)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM internallocation;"
print "DELETE FROM animal WHERE ID >= 100;"
print "DELETE FROM animaltest WHERE ID >= 100;"
print "DELETE FROM animalvaccination WHERE ID >= 100;"
print "DELETE FROM owner WHERE ID >= 100;"
print "DELETE FROM adoption WHERE ID >= 100;"

pf = ""
if PETFINDER_ID != "":
    asm.setid("media", 100)
    asm.setid("dbfs", 200)
    print "DELETE FROM media WHERE ID >= 100;"
    print "DELETE FROM dbfs WHERE ID >= 200;"
    pf = asm.petfinder_get_adoptable(PETFINDER_ID)

data = asm.csv_to_list(INTAKE_FILENAME)

for d in data:
    # Each row contains an animal, intake and outcome
    if ppa.has_key(d["Animal ID"]):
        a = ppa[d["Animal ID"]]
    else:
        a = asm.Animal()
        animals.append(a)
        ppa[d["Animal ID"]] = a
        a.AnimalTypeID = asm.iif(d["Animal Type"] == "Cat", 11, 2)
        if a.AnimalTypeID == 11 and d["Intake Type"] == "Stray":
            a.AnimalTypeID = 12
        a.SpeciesID = asm.species_id_for_name(d["Animal Type"])
        a.AnimalName = d["Animal Name"]
        if a.AnimalName.strip() == "":
            a.AnimalName = "(unknown)"
        if d["Date Of Birth"].strip() == "":
            a.DateOfBirth = asm.getdate_mmddyyyy(d["Date Of Birth"])
        else:
            a.DateOfBirth = asm.getdate_mmddyyyy(d["Date Of Birth"])
        if a.DateOfBirth is None:
            a.DateOfBirth = asm.today()
        a.DateBroughtIn = asm.getdate_mmddyyyy(d["Intake Date"])
        a.CreatedDate = a.DateBroughtIn
        a.LastChangedDate = a.DateBroughtIn
        if a.DateBroughtIn is None:
            a.DateBroughtIn = asm.today()
        if d["Intake Type"] == "Transfer In":
            a.IsTransfer = 1
        a.generateCode()
        a.ShortCode = d["Animal ID"]
        a.Markings = d["Distinguishing Markings"]
        a.IsNotAvailableForAdoption = 0
        a.ShelterLocation = asm.location_id_for_name(d["Location"])
        a.Sex = asm.getsex_mf(d["Gender"])
        a.Size = 2
        a.Neutered = d["Altered"] == "Yes" and 1 or 0
        a.ReasonForEntry = d["Reason"]
        a.IdentichipDate = asm.getdate_mmddyyyy(d["Microchip Issue Date"])
        a.IdentichipNumber = d["Microchip Number"]
        a.IsGoodWithCats = 2
        a.IsGoodWithDogs = 2
        a.IsGoodWithChildren = 2
        a.AsilomarIntakeCategory = d["Intake Condition"] == "Healthy" and 0 or 1
        a.HouseTrained = 0
        if a.IdentichipNumber != "": 
            a.Identichipped = 1
        a.Archived = 0
        comments = "Intake type: " + d["Intake Type"] + " " + d["Intake Subtype"] + ", breed: " + d["Primary Breed"] + "/" + d["Secondary Breed"]
        comments += ", age: " + d["Age Group"]
        comments += ", intake condition: " + d["Intake Condition"]
        a.BreedID = asm.breed_id_for_name(d["Primary Breed"])
        a.Breed2ID = a.BreedID
        a.BreedName = asm.breed_name_for_id(a.BreedID)
        a.CrossBreed = 0
        if d["Secondary Breed"].strip() != "":
            a.CrossBreed = 1
            if d["Secondary Breed"] == "Mix":
                a.Breed2ID = 442
            else:
                a.Breed2ID = asm.breed_id_for_name(d["Secondary Breed"])
            if a.Breed2ID == 1: a.Breed2ID = 442
            a.BreedName = "%s / %s" % ( asm.breed_name_for_id(a.BreedID), asm.breed_name_for_id(a.Breed2ID) )
        a.HiddenAnimalDetails = comments

    o = None
    if d["Outcome Person Name"].strip() != "":
        o = findowner(d["Outcome Person Name"])
        if o == None:
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

    ot = d["Outcome Type"]
    ost = d["Outcome Subtype"]
    od = asm.getdate_mmddyyyy(d["Outcome Date"])
    if (ot == "Transfer Out" and ost == "Potential Adopter") or ot == "Adoption":
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

vacc = asm.csv_to_list(VACC_FILENAME)
if vacc is not None:
    for v in vacc:
        if ppa.has_key(v["AnimalID"]):
            a = ppa[v["AnimalID"]]
            av = asm.AnimalVaccination()
            animalvaccinations.append(av)
            vaccdate = asm.getdate_mmddyyyy(v["Date"])
            if vaccdate is None:
                vaccdate = a.DateBroughtIn
            av.AnimalID = a.ID
            av.VaccinationID = 8
            vacctype = v["RecordType3"]
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
                if vacctype.find(k) != -1: av.VaccinationID = i
            av.DateRequired = vaccdate
            av.DateOfVaccination = vaccdate
            av.Comments = "Type: %s" % vacctype

test = asm.csv_to_list(TEST_FILENAME)
if test is not None:
    for t in test:
        if ppa.has_key(t["AnimalID"]):
            a = ppa[t["AnimalID"]]
            at = asm.AnimalTest()
            animaltests.append(at)
            at.AnimalID = a.ID
            testdate = asm.getdate_mmddyyyy(t["ItemStatusDateTime"])
            if testdate is None:
                testdate = a.DateBroughtIn
            at.DateRequired = testdate
            at.DateOfTest = testdate
            testtype = t["TestForCondition"]
            result = t["Result"]
            asmresult = 0
            if result == "Negative": asmresult = 1
            if result == "Positive": asmresult = 2
            at.TestResultID = asmresult + 1
            if testtype == "Heartworm":
                a.HeartwormTested = 1
                a.HeartwormTestDate = testdate
                a.HeartwormTestResult = asmresult
                at.TestTypeID = 3
            elif testtype == "FIV":
                a.CombiTested = 1
                a.CombiTestDate = testdate
                a.CombiTestResult = asmresult
                at.TestTypeID = 1
            elif testtype == "FELV":
                a.CombiTested = 1
                a.CombiTestDate = testdate
                a.FLVResult = asmresult
                at.TestTypeID = 2
            else:
                at.TestTypeID = 1
                at.Comments = "Test for %s" % testtype

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

asm.stderr_summary(animals=animals, animaltests=animaltests, animalvaccinations=animalvaccinations, owners=owners, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

