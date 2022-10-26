#!/usr/bin/env python3

import asm

"""
Import script for AniLog databases exported as CSV

24th October, 2022
"""

START_ID = 20000
PATH = "/home/robin/tmp/asm3_import_data/anilog_rr0147/"

# THIS IS USED IN ONE SPECIAL CASE - ANILOG IMPORTED RAIN RESCUE'S DATA FROM US, THEN
# RAIN WANTED TO COME BACK, SO THIS CUTOFF IGNORES RECORDS BEFORE THIS DATE SINCE THEY
# WILL ALREADY EXIST IN THE TARGET DATABASE.
# Set to None to not use a cutoff.
CUTOFF_DATE = asm.getdatetime_iso("2022-01-10") # Ignore records that are older than this date

# --- START OF CONVERSION ---

owners = []
movements = []
animals = []
animaltests = []
animalvaccinations = []
logs = []
ppa = {}
ppaid = {}
ppo = {}
ppoid = {}

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

def getdate(d):
    return asm.getdatetime_iso(d)

for d in asm.csv_to_list(PATH + "Contacts.csv"):
    # Ignore repeated headers
    if d["ContactID"] == "ContactID": continue
    # Ignore malformed rows - they only escape fields if they contain a comma, but not carriage returns
    if asm.cint(d["ContactID"]) == 0: continue
    # Ignore deleted rows
    if asm.cint(d["Deleted"]) == 1: continue
    # If this record was previously imported from ASM, record the id mapping and skip creating it
    if d["ContactRef"].find("ASM_") != -1:
        ppoid[d["ContactID"]] = asm.cint(d["ContactRef"].replace("ASM_", ""))
        continue
    o = asm.Owner()
    owners.append(o)
    ppo[d["ContactID"]] = o
    ppoid[d["ContactID"]] = o.ID
    o.OwnerTitle = d["TitleDescription"]
    o.OwnerForeNames = d["FirstName"]
    o.OwnerSurname = d["LastName"]
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = d["Address1"] + "\n" + d["Address2"]
    o.OwnerTown = d["TownCity"]
    o.OwnerCounty = d["CountyName"]
    o.OwnerPostcode = d["Postcode"]
    o.EmailAddress = d["EmailAddress"]
    o.HomeTelephone = d["HomePhone"]
    o.WorkTelephone = d["WorkPhone"]
    o.MobileTelephone = d["MobilePhone"]
    o.ExcludeFromBulkEmail = asm.cint(d["DoNotContact"])
    o.IsGiftAid = asm.cint(d["GiftAid"])
    if d["ContactByPost"] == 1: o.GDPRContactOptIn += ",post"
    if d["ContactByEmail"] == 1: o.GDPRContactOptIn += ",email"
    if d["ContactByPhone"] == 1: o.GDPRContactOptIn += ",phone"
    if d["ContactBySMS"] == 1: o.GDPRContactOptIn += ",sms"

for d in asm.csv_to_list(PATH + "Contact_Notes.csv"):
    if d["Notes"] == "Record imported from Animal Shelter Manager": continue # Skip junk imported notes
    # Ignore malformed rows - they only escape fields if they contain a comma, but not carriage returns
    if asm.cint(d["ContactID"]) == 0: continue
    # Ignore any records before the cutoff
    if CUTOFF_DATE and getdate(d["EnteredOn"]) < CUTOFF_DATE: continue
    if d["ContactId"] in ppoid: # can assign notes even for existing ASM records we aren't creating in this import
        l = asm.Log()
        logs.append(l)
        l.LogTypeID = 3 # History
        l.LinkID = ppoid[d["ContactId"]]
        l.LinkType = 1
        l.Date = getdate(d["EnteredOn"])
        if l.Date is None:
            l.Date = asm.now()
        l.Comments = d["Notes"]

for d in asm.csv_to_list(PATH + "Contact_Types.csv"):
    if d["contactId"] in ppo: # can only assign for records we created
        o = ppo[d["contactId"]]
        if d["Description"] == "Staff Member": o.IsStaff = 1
        if d["Description"] == "Adopter": o.IsAdopter = 1
        if d["Description"] == "Home Visitor": o.IsHomeChecker = 1
        if d["Description"] == "Vet": o.IsVet = 1
        if d["Description"] == "Fosterer": o.IsFosterer = 1
        if d["Description"] == "Warden": o.IsACO = 1
    
for d in asm.csv_to_list(PATH + "Animals.csv"):
    # Ignore repeated headers
    if d["AnimalId"] == "AnimalId": continue
    # Ignore malformed rows - they only escape fields if they contain a comma, but not carriage returns
    if asm.cint(d["AnimalId"]) == 0: continue
    # If this record was previously imported from ASM, record the id mapping and skip creating it
    if d["AnimalRef"].find("ASM") != -1:
        ppaid[d["AnimalId"]] = asm.cint(d["AnimalRef"].replace("ASM", ""))
        continue
    a = asm.Animal()
    animals.append(o)
    ppa[d["AnimalId"]] = o
    ppaid[d["AnimalId"]] = o.ID
    if d["AnimalTypeName"] == "Cat":
        a.AnimalTypeID = 11 # Unwanted Cat
    elif d["AnimalTypeName"] == "Dog":
        a.AnimalTypeID = 2 # Unwanted Dog
    else:
        a.AnimalTypeID = 40 # Misc
    a.SpeciesID = asm.species_id_for_name(d["AnimalTypeName"])
    a.AnimalName = d["CurrentName"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateOfBirth = getdate(d["DateOfBirth"])
    a.ShortCode = d["AnimalRef"]
    a.Sex = asm.getsex_mf(d["gender"])
    a.Neutered = d["Neutered"] == "Yes" and 1 or 0
    asm.breed_ids(a, d["breed"], d["breed2"])
    a.CrossBreed = d["CrossBreed"] == "1" and 1 or 0
    a.BaseColourID = asm.colour_id_for_name(d["Colour"])
    a.Size = asm.size_id_for_name(d["sizeName"])
    if d["Chip1Number"] != "":
        a.Identichipped = 1
        a.IdentichipNumber = d["Chip1Number"]
        if d["Chip1ImplantDate"] != "NULL": a.IdentichipDate = getdate(d["Chip1ImplantDate"])
    if d["Chip2number"] != "":
        a.Identichipped = 1
        a.Identichip2Number = d["Chip2number"]
        if d["Chip2ImplantDate"] != "NULL": a.Identichip2Date = getdate(d["Chip2ImplantDate"])
    a.Archived = 0
    comments = "breed: " + d["breed"] + "/" + d["breed2"]
    comments += "\ncolour: " + d["Colour"]
    comments += "\ntatoo: " + d["TattooNumber"]
    comments += "\npassport: " + d["PassportNumber"]
    a.HiddenAnimalDetails = comments

for d in asm.csv_to_list(PATH + "Animal_BehaviourNotes.csv"):
    # Turn behaviour notes into logs
    # Ignore malformed rows - they only escape fields if they contain a comma, but not carriage returns
    if asm.cint(d["AnimalId"]) == 0: continue
    # Ignore any records before the cutoff
    if CUTOFF_DATE and getdate(d["EnteredOn"]) < CUTOFF_DATE: continue
    if d["AnimalId"] in ppaid: 
        l = asm.Log()
        logs.append(l)
        l.LogTypeID = 3 # History
        l.LinkID = ppaid[d["AnimalId"]]
        l.LinkType = 0
        l.Date = getdate(d["EnteredOn"])
        if l.Date is None:
            l.Date = asm.now()
        l.Comments = d["ObservationNotes"]

for d in asm.csv_to_list(PATH + "Animal_Admissions.csv"):
    # Can only work for records we just created as we won't have an object for previous records
    if d["AnimalId"] not in ppa: continue
    # Ignore any records before the cutoff
    if CUTOFF_DATE and getdate(d["AdmissionDate"]) < CUTOFF_DATE: continue
    a = ppa[d["AnimalId"]]
    if a.DateBroughtIn is None: a.DateBroughtIn = getdate(d["AdmissionDate"])
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    if d["AdmissionReason"] == "Transfer":
        a.IsTransfer = 1
    if d["AdmissionReason"] == "Stray or Abandoned":
        a.EntryReasonID = 7 # Stray
    else:
        a.EntryReasonID = 17 # Surrender
    a.generateCode()
    if ppoid[d["BroughtInByContactId"]] != "NULL":
        a.BroughtInByOwnerID = ppoid[d["BroughtInByContactId"]]
    a.HiddenAnimalDetails += "\nadmission reason: " + d["AdmissionReason"] + "\nhand in reason: " + d["HandInReason"]
    a.ReasonForEntry = d["AdmissionReasonNotes"] + " " + d["AdmissionNotes"]

for d in asm.csv_to_list(PATH + "Animal_Movements.csv"):
    # Ignore any records before the cutoff
    if CUTOFF_DATE and getdate(d["FromDate"]) < CUTOFF_DATE: continue
    # TODO: MovementFee and DonationReceived are float amounts, update the adoption fee
    # and create a payment record 
    if d["LocationStatusName"] == "Rehomed":
        pass # handle adoption
    elif d["LocationStatusName"] == "Fostered":
        pass # handle foster
    elif d["LocationStatusName"] == "External Transfer":
        pass # handle transfer
    elif d["LocationStatusName"] == "On Site":
        pass # shelter animal
    elif d["LocationStatusName"] == "Put to Sleep":
        pass # shelter animal
    elif d["LocationStatusName"] == "Deceased":
        pass # shelter animal
    elif d["LocationStatusName"] == "Waiting List":
        pass # TODO: What do we do with these? Make non-shelter? Cr

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

