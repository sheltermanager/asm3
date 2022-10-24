#!/usr/bin/env python3

import asm

"""
Import script for AniLog databases exported as CSV

24th October, 2022
"""

# The shelter's petfinder ID for grabbing animal images for adoptable animals
START_ID = 20000
PATH = "/home/robin/tmp/asm3_import_data/anilog_rr0147/"

# --- START OF CONVERSION ---

owners = []
movements = []
animals = []
animaltests = []
animalvaccinations = []
logs = []
ppa = {}
ppo = {}

asm.setid("animal", START_ID)
asm.setid("animaltest", START_ID)
asm.setid("animalvaccination", START_ID)
asm.setid("log", START_ID)
asm.setid("owner", START_ID)
asm.setid("adoption", START_ID)

print("\\set ON_ERROR_STOP\nBEGIN;")
print("DELETE FROM animal WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM animaltest WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM animalvaccination WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM log WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM owner WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM adoption WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)

# Create an unknown owner
#uo = asm.Owner()
#owners.append(uo)
#uo.OwnerSurname = "Unknown Owner"
#uo.OwnerName = uo.OwnerSurname

for d in asm.csv_to_list(PATH + "Contacts.csv"):
    # TODO: ContactRef = ASM ID and Origin=ASMimport for ASM records
    pass
    """
    # Ignore repeated headers
    if d["Person ID"] == "Person ID": continue
    # Each row contains a person
    o = asm.Owner()
    owners.append(o)
    ppo[d["Person ID"]] = o
    o.OwnerForeNames = d["Name First"]
    o.OwnerSurname = d["Name Last"]
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = d["Street Address"]
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
    """

for d in asm.csv_to_list(PATH + "Animals.csv"):
    #TODO: AnimalRef = ASM[Our ID] for records imported from ASM
    pass
    """
    # If it's a repeat of the header row, skip
    if d["Animal #"] == "Animal #": continue
    # If it's a blank row, skip
    if d["Animal #"] == "": continue
    # Each row contains an animal, intake and outcome
    if d["Animal #"] in ppa:
        a = ppa[d["Animal #"]]
    else:
        a = asm.Animal()
        animals.append(a)
        ppa[d["Animal #"]] = a
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
        a.DateBroughtIn = getdate(d["Intake Date"]) or asm.today()
        if "Date Of Birth" in d and d["Date Of Birth"].strip() != "":
            a.DateOfBirth = getdate(d["Date Of Birth"])
        else:
            a.DateOfBirth = asm.subtract_days(a.DateBroughtIn, 365)
        a.CreatedDate = a.DateBroughtIn
        a.LastChangedDate = a.DateBroughtIn
        if d["Intake Type"] == "Transfer In":
            a.IsTransfer = 1
        a.generateCode()
        a.ShortCode = d["ARN"]
        if a.ShortCode.strip() == "": a.ShortCode = d["Animal #"]
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
        comments += ", ID: " + d["Animal #"] + ", ARN: " + d["ARN"]
        asm.breed_ids(a, d["Primary Breed"], d["Secondary Breed"])
        a.HiddenAnimalDetails = comments
        """

for d in asm.csv_to_list(PATH + "Animal_Admissions.csv"):
    pass
    """
        if d["Admitter"] != "" and d["Intake Type"] in ("Owner/Guardian Surrender", "Transfer In"):
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
                o.OwnerAddress = d["Street Address"]
                if o.OwnerAddress == "": o.OwnerAddress = d["Agency Address"]
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
    """


for d in asm.csv_to_list(PATH + "Animal_Movements.csv"):
    pass
    """
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
            o.OwnerAddress = d["Out Street Address"]
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
            o.OwnerAddress = d["Agency Street Address"]
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
        a.ActiveMovementDate = m.MovementDate
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
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 3
        a.LastChangedDate = od
        movements.append(m)
    elif ot == "Return to Owner/Guardian":
        if a is None or o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 5
        m.MovementDate = od
        m.Comments = ot + "/" + ost
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
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
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 8
        a.LastChangedDate = od
        movements.append(m)
    """


# Turn behaviour notes into logs
for d in asm.csv_to_list(PATH + "Animal_BehaviourNotes.csv"):
    pass
    """
    if datefield not in d: continue # Can't do anything without our field
    if d[datefield] == datefield: continue # Ignore repeated headers
    if d[idfield] in ppa:
        a = ppa[d[idfield]]
        l = asm.Log()
        logs.append(l)
        l.LogTypeID = 3 # History
        l.LinkID = a.ID
        l.LinkType = 0
        l.Date = asm.getdate_mmddyyyy(d["textbox20"])
        if l.Date is None:
            l.Date = asm.now()
        l.Comments = d["Textbox131"]
    """

for d in asm.csv_to_list(PATH + "Animal_Treatments.csv"):
    pass

"""
def process_vacc(animalno, vaccdate = None, vaccexpires = None, vaccname = ""):
    if animalno in ppa:
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
    for k, i in vaccmap.items():
        if vaccname.find(k) != -1: av.VaccinationID = i
    av.DateRequired = vaccdate
    av.DateOfVaccination = vaccdate
    av.DateExpires = vaccexpires
    av.Comments = "Type: %s" % vaccname

if VACC_FILENAME != "" and asm.file_exists(VACC_FILENAME):
    vacc = asm.csv_to_list(VACC_FILENAME)
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
            if v["AnimalID"] == "AnimalID": continue
            #process_vacc(v["AnimalID"], getdate(v["Date"]), None, v["RecordType3"])
            process_vacc(v["StatusDateTime3"], getdate(v["BodyWeight"]), None, v["RecordType3"]) # Once saw a broken version of this file like this

def process_test(animalno, testdate = None, testname = "", result = ""):
    if animalno in ppa:
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

if TEST_FILENAME != "" and asm.file_exists(TEST_FILENAME):
    test = asm.csv_to_list(TEST_FILENAME)
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
            if t["AnimalID"] == "AnimalID": continue
            process_test(t["AnimalID"], getdate(t["ItemStatusDateTime"]), t["TestForCondition"], t["Result"])
"""

# Run back through the animals, if we have any that are still
# on shelter after 1 year, add an adoption to an unknown owner
# asm.adopt_older_than(animals, movements, uo.ID, 365)

# Now that everything else is done, output stored records
for a in animals:
    print(a)
for at in animaltests:
    print(at)
for av in animalvaccinations:
    print(av)
for o in owners:
    print(o)
for m in movements:
    print(m)
for l in logs:
    print(l)

asm.stderr_summary(animals=animals, animaltests=animaltests, animalvaccinations=animalvaccinations, logs=logs, owners=owners, movements=movements)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")

