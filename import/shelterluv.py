#!/usr/bin/env python3

import asm, os

"""
Import module to read from ShelterLuv CSV export.

Last updated 17th Feb, 2021

The following files are needed:

    Entities - Animals -> animals.csv
    Entities - Persons -> people.csv
    Events - Intake    -> intake.csv
    Events - Intake Non Shelter -> nonshelter.csv
    Events - Outcome   -> outcome.csv
    Events - Foster out to -> fosters.csv

    Events - Diagnostic Tests -> tests.csv
    Events - Procedures and Surgeries -> procedures.csv
    Events - Treatments Completed -> medical.csv
    Events - Vaccines Administered -> vaccinations.csv
"""

PATH = "/home/robin/tmp/asm3_import_data/sluv_kg2678"

DEFAULT_BREED = 261 # default to dsh
DATE_FORMAT = "MDY" # Normally MDY
USE_SMDB_ENTRY_TYPE = False # If False, maps to new db defaults, if True looks up animal type and entry reason in target db
START_ID = 100

animals = []
animaltests = []
animalmedicals = []
animalvaccinations = []
owners = []
movements = []

ppa = {}
ppo = {}

asm.setid("adoption", START_ID)
asm.setid("animal", START_ID)
asm.setid("animaltest", START_ID)
asm.setid("animalmedical", START_ID)
asm.setid("animalmedicaltreatment", START_ID)
asm.setid("animalvaccination", START_ID)
asm.setid("owner", START_ID)
asm.setid("ownerdonation", START_ID)
asm.setid("testtype", START_ID)
asm.setid("vaccinationtype", START_ID)

def getdate(s):
    if DATE_FORMAT == "DMY":
        return asm.getdate_ddmmyyyy(s)
    else:
        return asm.getdate_mmddyyyy(s)

def size_id_for_name(name):
    return {
        "": 3, 
        "LARGE": 1,
        "SMALL": 2,
        "MEDIUM": 3, 
        "X-LARGE": 0
    }[name.upper().strip()]

#uo = asm.Owner()
#owners.append(uo)
#uo.OwnerSurname = "Unknown Owner"
#uo.OwnerName = "Unknown Owner"
#uo.Comments = "Catchall for adopted animal data from ShelterLuv"

print("\\set ON_ERROR_STOP\nBEGIN;")
print("DELETE FROM adoption WHERE ID >= %s;" % START_ID)
print("DELETE FROM animal WHERE ID >= %s;" % START_ID)
print("DELETE FROM animalmedical WHERE ID >= %s;" % START_ID)
print("DELETE FROM animalmedicaltreatment WHERE ID >= %s;" % START_ID)
print("DELETE FROM animaltest WHERE ID >= %s;" % START_ID)
print("DELETE FROM animalvaccination WHERE ID >= %s;" % START_ID)
print("DELETE FROM internallocation WHERE ID >= %s;" % START_ID)
print("DELETE FROM owner WHERE ID >= %s;" % START_ID)
print("DELETE FROM ownerdonation WHERE ID >= %s;" % START_ID)
print("DELETE FROM testtype WHERE ID >= %s;" % START_ID)
print("DELETE FROM vaccinationtype WHERE ID >= %s;" % START_ID)

for d in asm.csv_to_list("%s/people.csv" % PATH):
    if d["Name"] == "Name": continue # skip repeated header rows
    if d["Name"] in ppo: continue # skip repeated rows
    # Each row contains a person
    o = asm.Owner()
    owners.append(o)
    ppo[d["Name"]] = o
    # ppo[d["Person ID"]] = o # Never seen one in a person file so have to use name
    o.SplitName(d["Name"])
    o.OwnerAddress = d["Street"]
    o.OwnerTown = d["City"]
    o.OwnerCounty = d["State"]
    if "Zip Code" in d: o.OwnerPostcode = d["Zip Code"]
    o.EmailAddress = d["Primary Email"]
    o.HomeTelephone = d["Phone"]
    # Last file I saw had repeated "Comments" columns, so need to be renumbered manually
    if "Comments" in d and d["Comments"] != "": 
        o.Comments += d["Comments"]
    if "Comments1" in d and d["Comments1"] and d["Comments1"] != "": 
        o.Comments += " " + d["Comments1"]
    if "Comments2" in d and d["Comments2"] and d["Comments2"] != "": 
        o.Comments += " " + d["Comments2"]
    if "Comments3" in d and d["Comments3"] and d["Comments3"] != "": 
        o.Comments += " " + d["Comments3"]
    if "Attributes" in d and d["Attributes"] != "": 
        o.Comments = "Attributes: %s" % d["Attributes"]
        if d["Attributes"].find("Banned") != -1: o.IsBanned = 1
        if d["Attributes"].find("Foster") != -1: o.IsFosterer = 1

for d in asm.csv_to_list("%s/animals.csv" % PATH):
    if d["Animal ID"] == "Animal ID": continue # skip repeated header rows
    if d["Animal ID"] in ppa: continue # skip repeated rows
    a = asm.Animal()
    animals.append(a)
    if d["Species"] == "Cat":
        animaltype = 11
        animalletter = "U"
    else:
        animaltype = 2
        animalletter = "D"
    a.AnimalTypeID = animaltype
    a.SpeciesID = asm.species_id_for_name(d["Species"])
    a.generateCode()
    a.ShortCode = d["Animal ID"]
    a.ShelterCode = d["Animal ID"]
    ppa[d["Animal ID"]] = a
    a.AnimalName = d["Name"]
    if "Created Date" in d: a.DateBroughtIn = getdate(d["Created Date"])
    dob = a.DateBroughtIn
    a.EstimatedDOB = 1
    # Ages are stored as 2Y/ 4M/ 26D
    age = d["Age (Y/M/D)"]
    for b in age.split("/"):
        b = b.strip();
        if b.endswith("Y"): dob = asm.subtract_days(dob, 365 * asm.atoi(b))
        if b.endswith("M"): dob = asm.subtract_days(dob, 30 * asm.atoi(b))
        if b.endswith("D"): dob = asm.subtract_days(dob, asm.atoi(b))
    a.DateOfBirth = dob
    a.Sex = 1
    if d["Sex"].startswith("F"):
        a.Sex = 0
    primary = d["Primary Breed"]
    secondary = ""
    if "Secondary Breed" in d: secondary = d["Secondary Breed"]
    asm.breed_ids(a, primary, secondary, DEFAULT_BREED)
    a.BaseColourID = asm.colour_id_for_name(d["Primary Color"])
    if "Current Weight" in d and d["Current Weight"] != "":
        a.Weight = asm.atof(d["Current Weight"])
    a.HiddenAnimalDetails = "Age: %s, Breed: %s / %s, Color: %s" % (age, primary, secondary, d["Primary Color"])
    if "Attributes" in d and d["Attributes"] != "":
        a.HiddenAnimalDetails += "\nAttributes: " + d["Attributes"]
        if d["Attributes"].find("Special Needs") != -1: a.HasSpecialNeeds = 1
        if d["Attributes"].find("Cat Friendly") != -1: a.IsGoodWithCats = 0
        if d["Attributes"].find("No cats") != -1: a.IsGoodWithCats = 1
        if d["Attributes"].find("Dog Social") != -1: a.IsGoodWithDogs = 0
        if d["Attributes"].find("No dogs") != -1 or d["Attributes"].find("no other dogs") != -1: a.IsGoodWithDogs = 1
        if d["Attributes"].find("No small children") != -1: a.IsGoodWithChildren = 5
    if "Kennel Card / Web Site Memo" in d: a.AnimalComments = d["Kennel Card / Web Site Memo"]
    if "Behavioral" in d and d["Behavioral"] != "": a.HiddenAnimalDetails += "\nBehavioral: " + d["Behavioral"]
    if "History" in d and d["History"] != "": a.HiddenAnimalDetails += "\nHistory: " + d["History"]
    if "Private**" in d and d["Private**"] != "": a.HiddenAnimalDetails += "\n" + d["History"]
    if "Medical" in d and d["Medical"] != "": a.HealthProblems = d["Medical"]
    if "Intake Memo" in d and d["Intake Memo"] != "": a.ReasonForEntry = d["Intake Memo"]
    if d["Altered in Care"].startswith("Altered"):
        a.Neutered = 1
        a.NeuteredDate = a.DateBroughtIn
    if "Altered before Arrival" in d and d["Altered before Arrival"] == "Yes":
        a.Neutered = 1
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    #if "In Custody" in d and d["In Custody"]: a.Archived = asm.iif(d["In Custody"] == "No", 1, 0)

for d in asm.csv_to_list("%s/intake.csv" % PATH):
    if d["Animal ID"] == "Animal ID": continue
    if d["Animal ID"] not in ppa: continue
    a = ppa[d["Animal ID"]]
    intaketype = d["Intake Type"] # Seems to change names a lot, has been AnimalIntakeType, Entry Category
    subtype = d["Intake Sub-Type"] # Also seems to change, has been AnimalIntakeSub-Type, Animal Type
    if "Intake Date" in d: a.DateBroughtIn = getdate(d["Intake Date"])
    # Intake person
    linkperson = 0
    if "Intake From Name" in d and d["Intake From Name"] != "" and d["Intake From Name"] in ppo:
        linkperson = ppo[d["Intake From Name"]].ID
    # Location
    if "Location" in d and d["Location"] != "":
        locs = d["Location"] # Locations are a comma separated list, with latest on the right
        if locs.find(",") != -1: locs = locs[locs.rfind(",")+1:]
        a.ShelterLocation = asm.location_id_for_name(locs, True)
        # a.ShelterLocation = asm.location_from_db(locs)
    if intaketype == "Transfer In":
        a.IsTransfer = 1
        a.EntryReasonID = 15
        a.BroughtInByOwnerID = linkperson
    elif intaketype == "Stray":
        a.EntryReasonID = 7
        a.BroughtInByOwnerID = linkperson
    elif intaketype == "Surrender":
        a.EntryReasonID = 17 
        a.OriginalOwnerID = linkperson
        a.BroughtInByOwnerID = linkperson
    elif intaketype == "Return":
        a.EntryReasonID = 17 # Surrender
        a.OriginalOwnerID = linkperson
        a.BroughtInByOwnerID = linkperson
    elif intaketype == "Service In":
        a.NonShelterAnimal = 1
        a.Archived = 1
        a.OriginalOwnerID = linkperson
        a.BroughtInByOwnerID = linkperson
    else:
        a.EntryReasonID = 17 # Surrender
        a.OriginalOwnerID = linkperson
        a.BroughtInByOwnerID = linkperson
    a.ReasonForEntry = "%s / %s" % ( intaketype, subtype )
    # Last customer broke both categories and manually entered everything in
    # ASM's lookup data before conversion. 
    # The lines below will look up the entry reason and animal type in the target
    # db from intake/subtype if the option is on.
    if USE_SMDB_ENTRY_TYPE:
        a.EntryReasonID = asm.entryreason_from_db(intaketype)
        a.AnimalTypeID = asm.animaltype_from_db(subtype)

# This file was sent by one customer, it looks like the events - intake file, but contains
# animals that only came in for some kind of service (typically feral spay/neuter), we
# use it to flag animals as non-shelter
if asm.file_exists("%s/nonshelter.csv" % PATH):
    for d in asm.csv_to_list("%s/nonshelter.csv" % PATH):
        if d["Animal ID"] == "Animal ID": continue
        if d["Animal ID"] not in ppa: continue
        a = ppa[d["Animal ID"]]
        a.NonShelterAnimal = 1
        a.Archived = 1
    linkperson = 0
    if "Intake From Name" in d and d["Intake From Name"] != "" and d["Intake From Name"] in ppo:
        linkperson = ppo[d["Intake From Name"]].ID
        a.OriginalOwnerID = linkperson

for d in asm.csv_to_list("%s/outcomes.csv" % PATH):
    if d["Animal ID"] == "Animal ID": continue # skip repeated headers
    o = None
    if d["Assoc. Person Name"] in ppo: o = ppo[d["Assoc. Person Name"]]
    a = None
    if d["Animal ID"] in ppa: a = ppa[d["Animal ID"]]
    if o is None or a is None: continue
    if d["Outcome Type"] == "Adoption":
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = getdate(d["Outcome Date"])
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 1
        a.CreatedDate = m.MovementDate
        if "Outcome By" in d: a.CreatedBy = "conversion/%s" % d["Outcome By"]
        a.LastChangedDate = m.MovementDate
        movements.append(m)
    elif d["Outcome Type"] == "Transfer Out" or d["Outcome Type"] == "Transfer":
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 3
        m.MovementDate = getdate(d["Outcome Date"])
        a.Archived = 3
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 1
        a.CreatedDate = m.MovementDate
        if "Outcome By" in d: a.CreatedBy = "conversion/%s" % d["Outcome By"]
        a.LastChangedDate = m.MovementDate
        movements.append(m)
    elif d["Outcome Type"] == "Return To Owner/Guardian" or d["Outcome Type"] == "Reclaimed":
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 5
        m.MovementDate = getdate(d["Outcome Date"])
        a.Archived = 5
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 5
        a.CreatedDate = m.MovementDate
        if "Outcome By" in d: a.CreatedBy = "conversion/%s" % d["Outcome By"]
        a.LastChangedDate = m.MovementDate
        movements.append(m)
    elif d["Outcome Type"] == "Euthanasia":
        a.DeceasedDate = getdate(d["Outcome Date"])
        a.PutToSleep = 1
        a.PTSReasonID = 4 # Sick
        a.Archived = 1
    elif d["Outcome Type"] == "Died":
        a.DeceasedDate = getdate(d["Outcome Date"])
        a.PutToSleep = 0
        a.PTSReasonID = 2 # Died
        a.Archived = 1

for d in asm.csv_to_list("%s/fosters.csv" % PATH):
    if d["Animal ID"] == "Animal ID": continue # skip repeated headers
    o = None
    if d["Foster Parent Name"] in ppo: o = ppo[d["Foster Parent Name"]]
    a = None
    if d["Animal ID"] in ppa: a = ppa[d["Animal ID"]]
    if o is None or a is None: continue
    # Add some other values that weren't present in the animal file
    if "Microchip Number" in d: a.IdentichipNumber = d["Microchip Number"]
    # Person has to be a fosterer
    o.IsFosterer = 1
    if a.IdentichipNumber != "": a.Identichipped = 1
    m = asm.Movement()
    m.AnimalID = a.ID
    m.OwnerID = o.ID
    m.MovementType = 2
    m.MovementDate = getdate(d["Outcome Date"])
    a.Archived = 2
    a.ActiveMovementID = m.ID
    a.ActiveMovementDate = m.MovementDate
    a.ActiveMovementType = 2
    a.CreatedDate = m.MovementDate
    a.LastChangedDate = m.MovementDate
    movements.append(m)

if asm.file_exists("%s/tests.csv" % PATH):
    for d in asm.csv_to_list("%s/tests.csv" % PATH):
        if d["Animal ID"] == "Animal ID": continue
        if d["Animal ID"] not in ppa: continue
        a = ppa[d["Animal ID"]]
        testdate = getdate(d["Date"])
        t = asm.animal_test(a.ID, testdate, testdate, d["Product"], d["Result"])
        animaltests.append(t)

if asm.file_exists("%s/procedures.csv" % PATH):
    for d in asm.csv_to_list("%s/procedures.csv" % PATH):
        if d["Animal ID"] == "Animal ID": continue
        if d["Animal ID"] not in ppa: continue
        a = ppa[d["Animal ID"]]
        meddate = getdate(d["Date"])
        treatmentname = ""
        comments = ""
        if "Treatment" in d: treatmentname = d["Treatment"]
        if "Type" in d and treatmentname == "": treatmentname = d["Type"]
        if "Comments" in d: comments = d["Comments"]
        m = asm.animal_regimen_single(a.ID, meddate, treatmentname, "Procedure", comments)
        animalmedicals.append(m)

if asm.file_exists("%s/medical.csv" % PATH):
    for d in asm.csv_to_list("%s/medical.csv" % PATH):
        if d["Animal ID"] == "Animal ID": continue
        if d["Animal ID"] not in ppa: continue
        a = ppa[d["Animal ID"]]
        meddate = getdate(d["Date given"])
        m = asm.animal_regimen_single(a.ID, meddate, d["Product"], d["Amount"], d["Dose notes"])
        animalmedicals.append(m)

if asm.file_exists("%s/vaccinations.csv" % PATH):
    for d in asm.csv_to_list("%s/vaccinations.csv" % PATH):
        if d["Animal ID"] == "Animal ID": continue
        if d["Animal ID"] not in ppa: continue
        a = ppa[d["Animal ID"]]
        vaccdate = getdate(d["Date given"])
        lotno = ""
        if "Lot #" in d: lotno = d["Lot #"]
        t = asm.animal_vaccination(a.ID, vaccdate, vaccdate, d["Vaccine product"], rabiestag=d["Rabies tag number"], batchnumber = lotno)
        animalvaccinations.append(t)

# Allow shelter animals to have their chips registered
for a in animals:
    if a.Archived == 0:
        a.IsNotForRegistration = 0

# Now that everything else is done, output stored records
for k, v in asm.testtypes.items():
    if v.ID >= START_ID: print(v)
for k, v in asm.vaccinationtypes.items():
    if v.ID >= START_ID: print(v)
for k, v in asm.locations.items():
    if v.ID >= START_ID: print(v)
for a in animals:
    print (a)
for o in owners:
    print (o)
for m in movements:
    print (m)
for av in animalvaccinations:
    print (av)
for at in animaltests:
    print (at)
for am in animalmedicals:
    print (am)

asm.stderr_summary(animals=animals, owners=owners, movements=movements, animalvaccinations=animalvaccinations, animaltests=animaltests, animalmedicals=animalmedicals)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")
