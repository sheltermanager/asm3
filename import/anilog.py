#!/usr/bin/env python3

import asm

"""
Import script for AniLog databases exported as CSV

24th October, 2022
"""

START_ID = 50000
PATH = "/home/robin/tmp/asm3_import_data/anilog_rr0147/"

# If True, uses an empty string instead of the DBFS contents for testing so that it
# is quick to load into a database and see the media entries. 
# Should be FALSE for a production import.
EMPTY_DBFS_FILES = False

# THIS IS USED IN ONE SPECIAL CASE - ANILOG IMPORTED RAIN RESCUE'S DATA FROM US, THEN
# RAIN WANTED TO COME BACK, SO THIS CUTOFF IGNORES RECORDS BEFORE THIS DATE SINCE THEY
# WILL ALREADY EXIST IN THE TARGET DATABASE.
# Set to None to not use a cutoff.
CUTOFF_DATE = asm.getdatetime_iso("2022-04-01 00:00:00") # Ignore records that are older than this date

# --- START OF CONVERSION ---

owners = []
ownerdonations = []
movements = []
animals = []
animalmedicals = []
logs = []
stocklevels = []
waitinglists = []
ppa = {}
ppaid = {}
ppo = {}
ppoid = {}

asm.setid("adoption", START_ID)
asm.setid("animal", START_ID)
asm.setid("animalmedical", START_ID)
asm.setid("animalmedicaltreatment", START_ID)
asm.setid("animalwaitinglist", START_ID)
asm.setid("dbfs", START_ID)
asm.setid("media", START_ID)
asm.setid("log", START_ID)
asm.setid("owner", START_ID)
asm.setid("ownerdonation", START_ID)
asm.setid("stocklevel", START_ID)

print("\\set ON_ERROR_STOP\nBEGIN;")
print("DELETE FROM adoption WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM animal WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM animalmedical WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM animalmedicaltreatment WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM dbfs WHERE ID >= %s;" % START_ID)
print("DELETE FROM media WHERE ID >= %s;" % START_ID)
print("DELETE FROM log WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM owner WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM ownerdonation WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM stocklevel WHERE ID >= %s;" % START_ID)
print("DELETE FROM animalwaitinglist WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)

def getdate(d, todayIfNull=False):
    o = asm.getdatetime_iso(d)
    if todayIfNull and o is None: return asm.today()
    return o

def nonull(s):
    if s == "NULL": return ""
    return s

for d in asm.csv_to_list(PATH + "Contacts.csv"):
    # Ignore repeated headers
    if d["ContactID"] == "ContactID": continue
    # Ignore malformed rows - they only escape fields if they contain a comma, but not carriage returns
    if asm.cint(d["ContactID"]) == 0: continue
    if "Address2" not in d or d["Address2"] is None: continue
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
    o.OwnerSurname = d["Lastname"]
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = d["Address1"]
    if d["Address2"] != "" and d["Address2"] != "NULL": o.OwnerAddress += "\n" + d["Address2"]
    o.OwnerTown = d["TownCity"]
    o.OwnerCounty = nonull(d["CountyName"])
    o.OwnerPostcode = nonull(d["Postcode"])
    o.EmailAddress = nonull(d["EmailAddress"])
    o.HomeTelephone = nonull(d["HomePhone"])
    o.WorkTelephone = nonull(d["WorkPhone"])
    o.MobileTelephone = nonull(d["MobilePhone"])
    o.ExcludeFromBulkEmail = asm.cint(d["DoNotContact"])
    o.IsGiftAid = asm.cint(d["GiftAid"])
    if d["ContactByPost"] == 1: o.GDPRContactOptIn += ",post"
    if d["ContactByEmail"] == 1: o.GDPRContactOptIn += ",email"
    if d["ContactByPhone"] == 1: o.GDPRContactOptIn += ",phone"
    if d["ContactBySMS"] == 1: o.GDPRContactOptIn += ",sms"

for d in asm.csv_to_list(PATH + "Contact_Notes.csv"):
    if d["Notes"] == "Record imported from Animal Shelter Manager": continue # Skip junk imported notes
    # Ignore malformed rows - they only escape fields if they contain a comma, but not carriage returns
    if "ContactID" not in d or asm.cint(d["ContactID"]) == 0: continue
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
    if d["contactid"] in ppo: # can only assign for records we created
        o = ppo[d["contactid"]]
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
    # Ignore waiting list animals, not sure what to do with those
    if d["AnimalRef"].startswith("WL"): continue
    # If this record was previously imported from ASM, record the id mapping and skip creating it
    if d["AnimalRef"].startswith("ASM"):
        ppaid[d["AnimalId"]] = asm.cint(d["AnimalRef"].replace("ASM", ""))
        continue
    a = asm.Animal()
    animals.append(a)
    ppa[d["AnimalId"]] = a
    ppaid[d["AnimalId"]] = a.ID
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
    a.DateOfBirth = getdate(d["DateOfBirth"]) or asm.today()
    a.ShelterCode = d["AnimalRef"]
    a.ShortCode = d["AnimalRef"]
    a.Sex = asm.getsex_mf(d["gender"])
    a.Neutered = d["Neutered"] == "Yes" and 1 or 0
    asm.breed_ids(a, d["breed"], d["breed2"], default=442)
    a.CrossBreed = d["CrossBreed"] == "1" and 1 or 0
    a.BaseColourID = asm.colour_id_for_name(d["Colour"])
    a.Size = asm.size_id_for_name(d["sizeName"])
    if d["Chip1Number"] != "" and d["Chip1Number"] != "NULL":
        a.Identichipped = 1
        a.IdentichipNumber = d["Chip1Number"]
        a.IdentichipDate = getdate(d["Chip1ImplantDate"])
    if d["Chip2number"] != "" and d["Chip2number"] != "NULL":
        a.Identichipped = 1
        a.Identichip2Number = d["Chip2number"]
        a.Identichip2Date = getdate(d["Chip2ImplantDate"])
    a.Archived = 0
    comments = "breed: " + d["breed"] + "/" + d["breed2"] + " " + d["OtherBreed"]
    comments += "\ncolour: " + d["Colour"]
    if d["TattooNumber"] and d["TattooNumber"] != "NULL": comments += "\ntatoo: " + d["TattooNumber"]
    if d["PassportNumber"] and d["PassportNumber"] != "NULL": comments += "\npassport: " + d["PassportNumber"]
    a.HiddenAnimalDetails = comments
    # Admission record will set non-shelter=0/archived=0
    a.NonShelterAnimal = 1
    # Undo default behaviour of not registering chips created from this source
    a.IsNotForRegistration = 0
    a.Archived = 1
    # Some readable fields we can use later when creating waiting lists
    a.SpeciesName = d["AnimalTypeName"]
    a.SexName = d["gender"]

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

for d in sorted(asm.csv_to_list(PATH + "Animal_Admissions.csv"), key=lambda k: getdate(k["AdmissionDate"], True)):
    # Can only work for records we just created as we won't have an object for previous records
    if d["AnimalId"] not in ppa: continue
    # Ignore any records before the cutoff
    if CUTOFF_DATE and getdate(d["AdmissionDate"]) < CUTOFF_DATE: continue
    a = ppa[d["AnimalId"]]
    if a.DateBroughtIn == asm.today(): 
        a.DateBroughtIn = getdate(d["AdmissionDate"])
        a.NonShelterAnimal = 0
        a.Archived = 0
    if a.DateOfBirth is None or a.DateOfBirth == asm.today():
        a.DateOfBirth = a.DateBroughtIn
        a.EstimatedDOB = 1
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    if d["AdmissionReason"] == "Transfer":
        a.IsTransfer = 1
    if d["AdmissionReason"] == "Stray or Abandoned":
        a.EntryReasonID = 7 # Stray
        a.EntryTypeID = 2
    else:
        a.EntryReasonID = 17 # Surrender
        a.EntryTypeID = 1
    if d["BroughtInByContactId"] in ppoid:
        a.BroughtInByOwnerID = ppoid[d["BroughtInByContactId"]]
    a.HiddenAnimalDetails += "\nadmission reason: " + d["AdmissionReason"] + "\nhand in reason: " + d["HandInReason"]
    a.ReasonForEntry = "%s %s" % (d["AdmissionReasonNotes"], d["AdmissionNotes"])

# The ownership history duplicates movements/rehoming, but can be used to identify non-shelter
# animals who never came to the shelter (no admission record)
# We deliberately do this before movements because we need to find the owner of these
# non-shelter animals in order to put their owner on the waiting list when processing movements
for d in asm.csv_to_list(PATH + "Animal_OwnershipHistory.csv"):
    # Can only work for records we just created as we won't have an object for previous records
    if d["AnimalId"] not in ppa: continue
    odate = getdate(d["StartDate"]) or getdate(d["EndDate"])
    if odate is None: odate = asm.today()
    # Ignore any records before the cutoff
    if CUTOFF_DATE and odate < CUTOFF_DATE: continue
    a = ppa[d["AnimalId"]]
    # This animal did not have an admission record if DateBroughtIn == today, make it nonshelter to its owner
    if a.DateBroughtIn == asm.today() and d["OwnerContactId"] in ppoid: 
        a.NonShelterAnimal = 1
        a.Archived = 1
        a.DateBroughtIn = odate
        a.OriginalOwnerID = ppoid[d["OwnerContactId"]]
        a.OwnerID = ppoid[d["OwnerContactId"]]
        if a.DateOfBirth is None or a.DateOfBirth == asm.today():
            a.DateOfBirth = a.DateBroughtIn
            a.EstimatedDOB = 1

for d in sorted(asm.csv_to_list(PATH + "Animal_Movements.csv"), key=lambda k: getdate(k["FromDate"], True)):
    # Ignore malformed rows - they only escape fields if they contain a comma, but not carriage returns
    if asm.cint(d["AnimalId"]) == 0: continue
    # Ignore any records before the cutoff
    if CUTOFF_DATE and getdate(d["FromDate"]) < CUTOFF_DATE: continue
    # If a MovementFee has been set, update the adoption fee on the animal record
    if asm.cint(d["MovementFee"]) > 0 and d["AnimalId"] in ppa:
        ppa[d["AnimalId"]].Fee = asm.cint(d["MovementFee"]) * 100
    if d["LocationStatusName"] == "Rehomed":
        if d["LocationId"] not in ppoid: continue # skip missing people
        if d["AnimalId"] not in ppaid: continue # skip missing animals
        m = asm.Movement()
        m.AnimalID = ppaid[d["AnimalId"]]
        m.OwnerID = ppoid[d["LocationId"]]
        m.MovementType = 1
        m.MovementDate = getdate(d["FromDate"])
        m.ReturnDate = getdate(d["ToDate"])
        if d["AnimalId"] in ppa:
            a = ppa[d["AnimalId"]]
            a.Archived = 1
            a.ActiveMovementID = m.ID
            a.ActiveMovementDate = m.MovementDate
            a.ActiveMovementType = 1
            a.LastChangedDate = m.MovementDate
        movements.append(m)
        # If a DonationReceived amount has been set, create a payment for the adoption fee
        if asm.cint(d["DonationReceived"]) > 0:
            od = asm.OwnerDonation()
            ownerdonations.append(od)
            od.DonationTypeID = 2
            od.DonationPaymentID = 1
            od.Date = m.MovementDate
            od.OwnerID = m.OwnerID
            od.AnimalID = m.AnimalID
            od.MovementID = m.ID
            od.Donation = asm.get_currency(d["DonationReceived"])
    elif d["LocationStatusName"] == "Fostered":
        if d["LocationId"] not in ppoid: continue # skip missing people
        if d["AnimalId"] not in ppaid: continue # skip missing animals
        m = asm.Movement()
        m.AnimalID = ppaid[d["AnimalId"]]
        m.OwnerID = ppoid[d["LocationId"]]
        m.MovementType = 2
        m.MovementDate = getdate(d["FromDate"])
        m.ReturnDate = getdate(d["ToDate"])
        if d["AnimalId"] in ppa:
            a = ppa[d["AnimalId"]]
            a.ActiveMovementID = m.ID
            a.ActiveMovementDate = m.MovementDate
            a.ActiveMovementType = 2
            a.LastChangedDate = m.MovementDate
        movements.append(m)
    elif d["LocationStatusName"] == "External Transfer":
        if d["LocationId"] not in ppoid: continue # skip missing people
        if d["AnimalId"] not in ppaid: continue # skip missing animals
        m = asm.Movement()
        m.AnimalID = ppaid[d["AnimalId"]]
        m.OwnerID = ppoid[d["LocationId"]]
        m.MovementType = 3
        m.MovementDate = getdate(d["FromDate"])
        m.ReturnDate = getdate(d["ToDate"])
        if d["AnimalId"] in ppa:
            a = ppa[d["AnimalId"]]
            a.Archived = 1
            a.ActiveMovementID = m.ID
            a.ActiveMovementDate = m.MovementDate
            a.ActiveMovementType = 3
            a.LastChangedDate = m.MovementDate
        movements.append(m)
    elif d["LocationStatusName"] == "On Site":
        # Just record the location in the comments as it's all we can do
        if d["AnimalId"] not in ppa: continue
        a = ppa[d["AnimalId"]]
        a.HiddenAnimalDetails += "\nlocation: " + d["LocationName"]
    elif d["LocationStatusName"] == "Put to Sleep":
        if d["AnimalId"] in ppa:
            a = ppa[d["AnimalId"]]
            a.DeceasedDate = getdate(d["FromDate"])
            a.PutToSleep = 1
            a.PTSReasonID = 4
            a.Archived = 1
    elif d["LocationStatusName"] == "Deceased":
        if d["AnimalId"] in ppa:
            a = ppa[d["AnimalId"]]
            a.DeceasedDate = getdate(d["FromDate"])
            a.PutToSleep = 0
            a.Archived = 1
    elif d["LocationStatusName"] == "Waiting List":
        if d["AnimalId"] in ppa:
            a = ppa[d["AnimalId"]]
            if a.OwnerID is None or a.OwnerID == 0: continue # can't do anything without an owner
            wl = asm.AnimalWaitingList()
            waitinglists.append(wl)
            wl.Size = a.Size
            wl.SpeciesID = a.SpeciesID
            wl.OwnerID = a.OwnerID
            wl.DatePutOnList = getdate(d["FromDate"])
            wl.DateRemovedFromList = getdate(d["ToDate"])
            wl.AnimalDescription = "%s - %s (%s %s %s)" % (a.AnimalName, a.ShelterCode, a.SexName, a.BreedName, a.SpeciesName)
            wl.ReasonForWantingToPart = a.ReasonForEntry
            wl.Comments = "AniLog waiting list entry: see owner record for non-shelter animal info"
            wl.CreatedDate = wl.DatePutOnList
            wl.LastChangedDate = wl.DateRemovedFromList or wl.DatePutOnList
           
for d in asm.csv_to_list(PATH + "Animal_Vet_Treatments.csv"):
    # Ignore malformed rows - they only escape fields if they contain a comma, but not carriage returns
    if asm.cint(d["animalid"]) == 0: continue
    tdate = getdate(d["TreatmentDate"])
    if tdate is None: continue
    if CUTOFF_DATE and tdate < CUTOFF_DATE: continue
    tcat = d["TreatmentCategory"]
    tnotes = d["TreatmentNotes"]
    if d["animalid"] in ppaid:
        animalmedicals.append(asm.animal_regimen_single( ppaid[d["animalid"]], tdate, tcat, comments = tnotes ))

for d in asm.csv_to_list(PATH + "Animal_Attachments.csv"):
    # Ignore malformed rows - they only escape fields if they contain a comma, but not carriage returns
    if asm.cint(d["AnimalId"]) == 0: continue
    # Ignore any records before the cutoff
    if CUTOFF_DATE and getdate(d["DateAdded"]) < CUTOFF_DATE: continue
    # Ignore broken links
    if d["AnimalId"] not in ppaid: continue
    filedata = asm.load_image_from_file(PATH + "attachments/" + d["AttachmentFileName"])
    if EMPTY_DBFS_FILES: filedata = b"" 
    notes = d["Notes"]
    if notes == "NULL": notes = ""
    asm.media_file(0, ppaid[d["AnimalId"]], d["AttachmentFileName"], filedata, notes)

for d in asm.csv_to_list(PATH + "Animal_TreatmentAttachments.csv"):
    # Ignore malformed rows - they only escape fields if they contain a comma, but not carriage returns
    if asm.cint(d["AnimalId"]) == 0: continue
    # Ignore any records before the cutoff
    if CUTOFF_DATE and getdate(d["DateAdded"]) < CUTOFF_DATE: continue
    # Ignore broken links
    if d["AnimalId"] not in ppaid: continue
    filedata = asm.load_image_from_file(PATH + "attachments/" + d["AttachmentFileName"])
    if EMPTY_DBFS_FILES: filedata = b"" 
    notes = d["Notes"]
    if notes == "NULL": notes = ""
    asm.media_file(0, ppaid[d["AnimalId"]], d["AttachmentFileName"], filedata, notes)

for d in asm.csv_to_list(PATH + "Contact_Attachments.csv"):
    # Ignore malformed rows - they only escape fields if they contain a comma, but not carriage returns
    if asm.cint(d["ContactId"]) == 0: continue
    # Ignore any records before the cutoff
    if CUTOFF_DATE and getdate(d["DateAdded"]) < CUTOFF_DATE: continue
    # Ignore broken links
    if d["ContactId"] not in ppoid: continue
    filedata = asm.load_image_from_file(PATH + "attachments/" + d["AttachmentFileName"])
    if EMPTY_DBFS_FILES: filedata = b"" 
    notes = d["Notes"]
    if notes == "NULL": notes = ""
    asm.media_file(3, ppoid[d["ContactId"]], d["AttachmentFileName"], filedata, notes)

for d in asm.csv_to_list(PATH + "DrugStockReceipts.csv"):
     # Ignore any records before the cutoff
    if CUTOFF_DATE and getdate(d["DateReceived"]) < CUTOFF_DATE: continue
    l = asm.StockLevel()
    stocklevels.append(l)
    l.Name = d["DrugName"]
    l.Description = d["PackDesc"]
    l.UnitName = d["PackDesc"]
    l.Total = asm.cint(d["PackQuantity"]) * asm.cint(d["QuantityReceived"])
    l.Balance = l.Total - asm.cint(d["UnitsUsed"])
    l.Expiry= getdate(d["ExpiryDate"])
    l.BatchNumber = ""
    l.Cost = asm.get_currency(d["PackPrice"])
    l.UnitPrice = 0
    l.CreatedDate = getdate(d["DateReceived"], True)

# Run back through the animals, if we have any that are still
# on shelter after 1 year, add an adoption to an unknown owner
# asm.adopt_older_than(animals, movements, uo.ID, 365)

# Now that everything else is done, output stored records
for a in animals:
    print(a)
for am in animalmedicals:
    print(am)
for o in owners:
    print(o)
for od in ownerdonations:
    print(od)
for m in movements:
    print(m)
for l in logs:
    print(l)
for l in stocklevels:
    print(l)
for wl in waitinglists:
    print(wl)

#asm.stderr_allanimals(animals)
#asm.stderr_onshelter(animals)
asm.stderr_summary(animals=animals, animalmedicals=animalmedicals, logs=logs, owners=owners, ownerdonations=ownerdonations, movements=movements, stocklevels=stocklevels, waitinglists=waitinglists)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")

