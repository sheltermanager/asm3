#!/usr/bin/python3

import asm

"""
Import script for ARK DBF databases, covers people, animals, payments, events, licences and complaints

21st March, 2015
Last changed: 2nd Feb, 2023
"""

PATH = "/home/robin/tmp/asm3_import_data/ark_kw2942"
START_ID = 100
PICTURE_IMPORT = False

BLANK_DATE = asm.parse_date("2015-01-01", "%Y-%m-%d") # Date used for licenses and incidents when the date was blank in ARK

owners = []
ownerdonations = []
ownerlicences = []
movements = []
logs = []
animals = []
animalcontrol = []
ppa = {}
ppo = {}

arkspecies = {
    "C": 1, # Dog
    "F": 2, # Cat
    "E": 24,# Horse
    "R": 7  # Rabbit
}

asm.setid("animal", START_ID)
asm.setid("owner", START_ID)
asm.setid("ownerdonation", START_ID)
asm.setid("ownerlicence", START_ID)
asm.setid("adoption", START_ID)
asm.setid("animalcontrol", START_ID)
asm.setid("log", START_ID)
asm.setid("media", START_ID)
asm.setid("dbfs", START_ID)

print("\\set ON_ERROR_STOP\nBEGIN;")
print("DELETE FROM animal WHERE ID >= %s;" % START_ID)
print("DELETE FROM animalcontrol WHERE ID >= %s;" % START_ID)
print("DELETE FROM owner WHERE ID >= %s;" % START_ID)
print("DELETE FROM ownerdonation WHERE ID >= %s;" % START_ID)
print("DELETE FROM ownerlicence WHERE ID >= %s;" % START_ID)
print("DELETE FROM adoption WHERE ID >= %s;" % START_ID)
print("DELETE FROM log WHERE ID >= %s;" % START_ID)
print("DELETE FROM media WHERE ID >= %s;" % START_ID)
print("DELETE FROM dbfs WHERE ID >= %s;" % START_ID)

# Create an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname

for p in asm.read_dbf("%s/NAMES.DBF" % PATH):
    o = asm.Owner()
    owners.append(o)
    ppo[p["ID"]] = o
    o.OwnerForeNames = p["F_NAME"].title()
    o.OwnerSurname = p["L_NAME"].title()
    o.OwnerAddress = "%s %s\n%s" % (p["ADR_ST_NUM"].title(), p["ADR_ST_NAM"].title(), p["ADR_LINE2"].title())
    o.OwnerTown = p["CITY"].title()
    o.OwnerCounty = p["STATE"]
    o.OwnerPostcode = p["ZIP"]
    o.HomeTelephone = p["H_PHONE"]
    o.WorkTelephone = p["W_PHONE"]
    comments = "ID: %s" % p["ID"]
    comments += "\n%s" % asm.nulltostr(p["NAMES_TXT"])
    o.Comments = comments

for d in asm.read_dbf("%s/ANIMALS.DBF" % PATH):
    a = asm.Animal()
    animals.append(a)
    ppa[d["ID_NUM"]] = a
    a.AnimalName = d["NAME"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.AnimalName = a.AnimalName.title()
    if d["SPECIES"] == "C":
        # Canine
        a.SpeciesID = 1
        if d["SURR_CODE"] == "STR":
            a.AnimalTypeID = 10
            a.EntryReasonID = 11
        else:
            a.AnimalTypeID = 2
    elif d["SPECIES"] == "F":
        # Feline
        a.SpeciesID = 2
        if d["SURR_CODE"] == "STR":
            a.EntryReasonID = 11
            a.AnimalTypeID = 12
        else:
            a.AnimalTypeID = 11
    elif d["SPECIES"] == "R":
        # Rabbit
        a.SpeciesID = 7
        a.AnimalTypeID = 13
        if d["SURR_CODE"] == "STR":
            a.EntryReasonID = 11
    else:
        # SPECIES == "O" for other, BREED contains species instead
        a.SpeciesID = asm.species_id_for_name(d["BREED"])
        a.AnimalTypeID = 13 # Miscellaneous
        a.EntryReasonID = 11
    if d["SURR_ID"] != "":
        if d["SURR_ID"] in ppo:
            a.OriginalOwnerID = ppo[d["SURR_ID"]].ID
    a.Sex = asm.getsex_mf(d["SEX"])
    a.ShelterLocationUnit = d["LOCATION"]
    a.BreedID = asm.breed_id_for_name(d["BREED"])
    if a.BreedID == 1 and a.SpeciesID == 1: a.BreedID = 442 # switch to mixed breed for dogs
    if a.BreedID == 1 and a.SpeciesID == 2: a.BreedID = 261 # or DSH for cats
    a.BaseColourID = asm.colour_id_for_name(d["COLOR"])
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    if d["BREED"].find("MIX") != -1:
        a.CrossBreed = 1
        a.Breed2ID = 442
        a.BreedName = asm.breed_name_for_id(a.BreedID) + " / " + asm.breed_name_for_id(a.Breed2ID)
    a.DateBroughtIn = asm.todatetime(d["DATE_SURR"])
    if a.DateBroughtIn is None: a.DateBroughtIn = asm.now()
    a.ShelterCode = d["ID_NUM"]
    a.ShortCode = d["ID_NUM"]
    a.NeuteredDate = d["NEUTER_DAT"]
    if a.NeuteredDate is not None:
        a.Neutered = 1
    a.EstimatedDOB = 1
    dob = a.DateBroughtIn
    if "DOB" in d and d["DOB"] is not None:
        dob = d["DOB"]
    elif type(d["AGE"]) == int:
        dob = asm.subtract_days(dob, d["AGE"] * 365)
    elif type(d["AGE"]) == str and d["AGE"] != "":
        if d["AGE"].find("YR") != -1:
            dob = asm.subtract_days(dob, asm.atoi(d["AGE"]) * 365)
        elif d["AGE"].find("M") != -1:
            dob = asm.subtract_days(dob, asm.atoi(d["AGE"]) * 30)
    a.DateOfBirth = dob
    if d["EUTH_USD"] is not None and d["EUTH_USD"] > 0:
        a.PutToSleep = 1
        a.Archived = 1
        a.DeceasedDate = d["DATE_DISPO"]
    if d["CHIP_NUM"] != "":
        a.Identichipped = 1
        a.IdentichipNumber = d["CHIP_NUM"]
    comments = "Original breed: %s\nColor: %s" % (d["BREED"].strip(), d["COLOR"].strip())
    if asm.nulltostr(d["PU_LOC"]).strip() != "":
        comments += "\nPicked up from: %s" % d["PU_LOC"]
    a.HiddenAnimalDetails = comments
    a.AnimalComments = asm.nulltostr(d["ANIMAL_TXT"]).strip()
    a.HealthProblems = d["HEALTH"]
    a.LastChangedDate = a.DateBroughtIn
    if d["ADPT_ID"] != "":
        if d["ADPT_ID"] in ppo:
            o = ppo[d["ADPT_ID"]]
            m = asm.Movement()
            movements.append(m)
            m.AnimalID = a.ID
            m.OwnerID = o.ID
            m.MovementType = 1
            m.MovementDate = asm.todatetime(d["DATE_DISPO"])
            # I've seen it happen where disposition date is years ago, but there was no intake date
            if m.MovementDate < a.DateBroughtIn:
                a.DateBroughtIn = m.MovementDate
            if d["RECLAIMED"] == "X": 
                m.MovementType = 5
            m.LastChangedDate = m.MovementDate
            a.Archived = 1
            a.ActiveMovementType = m.MovementType
            a.ActiveMovementDate = m.MovementDate
    if PICTURE_IMPORT and d["IMAGE"] != "" and d["IMAGE"] != "no_image.jpg" and d["IMAGE"] != "NO_IMAGE.JPG":
        fpath = "%s/pictures/Animals/%s" % (PATH, d["IMAGE"])
        imdata = asm.load_image_from_file(fpath, case_sensitive = False) # ARK is a Windows program
        if imdata is not None:
            asm.animal_image(a.ID, imdata)

for p in asm.read_dbf("%s/PAYMENTS.DBF" % PATH):
    if p["PMNT_ID"] not in ppo: continue
    od = asm.OwnerDonation()
    ownerdonations.append(od)
    o = ppo[p["PMNT_ID"]]
    od.OwnerID = o.ID
    od.Donation = asm.get_currency(p["AMOUNT"])
    od.Date = p["PMNT_DATE"]
    od.DonationTypeID = 4 # Surrender
    if p["PMNT_CODE"] == "ADP":
        od.DonationTypeID = 2

for l in asm.read_dbf("%s/LICENSE.DBF" % PATH):
    if l["OWNER_ID"] not in ppo: continue
    ol = asm.OwnerLicence()
    ownerlicences.append(ol)
    o = ppo[l["OWNER_ID"]]
    ol.OwnerID = o.ID
    ol.LicenceTypeID = 1
    ol.LicenceNumber = l["LIC_NUM"]
    if "FEE" in l: ol.LicenceFee = asm.get_currency(l["FEE"])
    ol.IssueDate = l["LIC_DATE"]
    if ol.IssueDate is None: ol.IssueDate = BLANK_DATE
    ol.ExpiryDate = l["LIC_EXDATE"]
    if ol.ExpiryDate is None: ol.ExpiryDate = BLANK_DATE

for c in asm.read_dbf("%s/CMPLAINT.DBF" % PATH):
    ac = asm.AnimalControl()
    animalcontrol.append(ac)
    if c["FROM_ID"] != "" and c["FROM_ID"] in ppo:
        ac.CallerID = ppo[c["FROM_ID"]].ID
    if c["ABOUT_ID"] != "" and c["ABOUT_ID"] in ppo:
        ac.OwnerID = ppo[c["ABOUT_ID"]].ID
    ac.CallDateTime = c["DATE"]
    if ac.CallDateTime is None:
        ac.CallDateTime = BLANK_DATE
    ac.IncidentDateTime = ac.CallDateTime
    ac.DispatchDateTime = ac.CallDateTime
    ac.CompletedDate = ac.CallDateTime
    ac.DispatchAddress = c["LOCATION"]
    if c["SPECIES"] in arkspecies:
        ac.SpeciesID = arkspecies[c["SPECIES"]]
    ac.Sex = asm.getsex_mf(c["SEX"])
    comments = ""
    comments = "Problem: %s" % c["PROBLEM"]
    if c["FOLLOW_UP"] != "": comments += "\nFollowup: %s" % c["FOLLOW_UP"]
    if c["OFFICER_ID"] != "": comments += "\nOfficer: %s" % c["OFFICER_ID"]
    if c["CITATION"] != "": comments += "\nCitation: %s" % c["CITATION"]
    if c["CMPL_TEXT"] != "": comments += "\nCompleted: %s" % c["CMPL_TEXT"]
    ac.CallNotes = comments

for c in asm.read_dbf("%s/AN_EVNTS.DBF" % PATH):
    if c["ID_NUM"] not in ppa: continue
    a = ppa[c["ID_NUM"]]
    l = asm.Log()
    logs.append(l)
    l.LogTypeID = 3
    l.LinkID = a.ID
    l.LinkType = 0
    l.Date = c["DATE_DONE"]
    if l.Date is None: l.Date = asm.now()
    l.Comments = "%s %s" % (c["TYPE"], c["DESCRIP"])
    l.CreatedBy = c["LAST_USER"]
    l.CreatedDate = c["LAST_TIME"]
    l.LastChangedBy = c["LAST_USER"]
    l.LastChangedDate = c["LAST_TIME"]

# Adopt out any animals still on shelter to an unknown owner
asm.adopt_older_than(animals, movements, uo.ID, 0)

for a in animals:
    print(a)
for o in owners:
    print(o)
for m in movements:
    print(m)
for od in ownerdonations:
    print(od)
for ol in ownerlicences:
    print(ol)
for ac in animalcontrol:
    print(ac)
for l in logs:
    print(l)

asm.stderr_summary(animals=animals, logs=logs, owners=owners, movements=movements, ownerlicences=ownerlicences, ownerdonations=ownerdonations, animalcontrol=animalcontrol)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")

