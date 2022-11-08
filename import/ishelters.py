#!/usr/bin/env python3

import asm, os

"""
Import script for iShelters CSV export.
It can be accessed by going to adminShelter and then System->Misc->Downloads

7th July, 2015 - 8th Nov, 2022
"""

PATH = "/home/robin/tmp/asm3_import_data/ishelters_ec2883/"

# Files needed
# adoptions.csv, animals.csv, checkins.csv, donations.csv, allmedical.csv, movements.csv, people.csv, releases.csv

# animalpictures.csv for images (seems to be using s3 signed URLs that are active for 5 minutes)

START_ID = 5000

# This is only ever going to be any good if ishelters make their bucket public
IMAGE_PREFIX = "https://ishelters.s3.us-west-2.amazonaws.com/shelters/384/animals/images/200x200s/"

def getentryreason(s):
    er = {
        "Surrendered": 11,
        "Dumped": 11,
        "Return": 11,
        "Abandoned": 11,
        "Stray": 7,
        "Impound": 7,
        "Animal Control": 7,
        "Born": 13
    }
    for k, v in er.items():
        if s.find(k) != -1:
            return v
    return 11

# --- START OF CONVERSION ---
print("\\set ON_ERROR_STOP\nBEGIN;")

animals = []
animalmedicals = []
animaltests = []
animalvaccinations = []
owners = []
ownerdonations = []
ppo = {}
ppa = {}
movements = []

asm.setid("adoption", START_ID)
asm.setid("animal", START_ID)
asm.setid("animalmedical", START_ID)
asm.setid("animalmedicaltreatment", START_ID)
asm.setid("animaltest", START_ID)
asm.setid("animalvaccination", START_ID)
asm.setid("owner", START_ID)
asm.setid("ownerdonation", START_ID)
asm.setid("vaccinationtype", 100)
asm.setid("testtype", 100)
asm.setid("media", 100)
asm.setid("dbfs", 100)

print("DELETE FROM adoption WHERE ID >= %s;" % START_ID)
print("DELETE FROM animal WHERE ID >= %s;" % START_ID)
print("DELETE FROM animalmedical WHERE ID >= %s;" % START_ID)
print("DELETE FROM animalmedicaltreatment WHERE ID >= %s;" % START_ID)
print("DELETE FROM animaltest WHERE ID >= %s;" % START_ID)
print("DELETE FROM animalvaccination WHERE ID >= %s;" % START_ID)
print("DELETE FROM owner WHERE ID >= %s;" % START_ID)
print("DELETE FROM ownerdonation WHERE ID >= %s;" % START_ID)
print("DELETE FROM testtype WHERE ID >= %s;" % START_ID)
print("DELETE FROM vaccinationtype WHERE ID >= %s;" % START_ID)
print("DELETE FROM dbfs WHERE ID >= %s;" % START_ID)
print("DELETE FROM media WHERE ID >= %s;" % START_ID)

to = asm.Owner()
to.OwnerSurname = "Unknown Transfer Owner"
owners.append(to)

ro = asm.Owner()
ro.OwnerSurname = "Unknown Reclaim Owner"
owners.append(ro)

fo = asm.Owner()
fo.OwnerSurname = "Unknown Foster Owner"
owners.append(fo)

uo = asm.Owner()
uo.OwnerSurname = "Unknown Adopter"
owners.append(uo)

# people.csv
for row in asm.csv_to_list(PATH + "people.csv", encoding="cp1252"):
    if row["last name"] is None: continue
    o = asm.Owner()
    ppo[row["id"]] = o
    owners.append(o)
    o.OwnerForeNames = row["first name"]
    o.OwnerSurname = row["last name"]
    o.HomeTelephone = row["home phone"]
    o.WorkTelephone = row["work phone"]
    o.MobileTelephone = row["cell phone"]
    o.EmailAddress = row["primary email"]
    o.OwnerAddress = "%s %s" % (row["address"], row["second address line"])
    o.OwnerTown = row["city"]
    o.OwnerCounty = row["region/state"]
    o.OwnerPostcode = row["postalCode"]
    o.Comments = "%s %s %s" % (row["general comments"], row["hidden comments"], row["banned comments"])
    if row["banned date"] != "": o.IsBanned = 1
    # type(s) field missing in last extract I saw but was row["Type(s)"]
    types = "" 
    if types.find("Volunteer") != -1: o.IsVolunteer = 1
    if types.find("Employee") != -1: o.IsStaff = 1
    if types.find("Member") != -1: o.IsMember = 1
    if types.find("Foster") != -1: o.IsFosterer = 1

# animals.csv
for row in asm.csv_to_list(PATH + "animals.csv", encoding="cp1252"):
    if row["name"] is None: continue
    if row["code"] is None or row["code"] == "": continue
    if row["primary breed"] is None or row["primary breed"] == "": continue
    if row["species"] is None or row["species"] == "": continue
    if row["primary color"] is None or row["primary color"] == "": continue
    a = asm.Animal()
    animals.append(a)
    ppa[row["id"]] = a
    a.AnimalName = row["name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.ShortCode = row["code"]
    a.AnimalTypeID = asm.type_id_for_name(row["species"])
    a.SpeciesID = asm.species_id_for_name(row["species"])
    a.BreedID = asm.breed_id_for_name(row["primary breed"])
    a.Breed2ID = asm.breed_id_for_name(row["secondary breed"])
    a.CrossBreed = asm.iif(row["secondary breed"] != "", 1, 0)
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    a.BaseColourID = asm.colour_id_for_name(row["primary color"])
    a.Sex = asm.getsex_mf(row["sex"])
    a.DateBroughtIn = asm.getdate_iso(row["time entered"])
    if a.DateBroughtIn is None: a.DateBroughtIn = asm.now()
    a.DateOfBirth = asm.getdate_iso(row["birth date"])
    if a.DateOfBirth is None: a.DateOfBirth = asm.getdate_iso(row["time entered"])
    if a.DateOfBirth is None: a.DateOfBirth = a.DateBroughtIn
    a.NeuteredDate = asm.getdate_iso(row["neutered/spayed date"])
    if a.NeuteredDate is not None: a.Neutered = 1
    a.Archived = 0
    a.IdentichipNumber = row["microchip #"]
    if a.IdentichipNumber != "": a.Identichipped = 1
    a.HiddenAnimalDetails = "Original Breed: %s/%s, Color: %s\n%s" % (row["primary breed"], row["secondary breed"], row["primary color"], row["hidden comments"])
    a.HiddenAnimalDetails = a.HiddenAnimalDetails.replace("\\", "/")
    a.AnimalComments = ("%s" % row["general comments"]).replace("\\", "/")
    a.Markings = ("%s" % row["distinctive features"]).replace("\\", "/")
    a.DeceasedDate = asm.getdate_iso(row["date of death"])
    a.PTSReason = row["reason of death"]
    a.RabiesTag = row["tag #"]
    a.IsNotForRegistration = 0

    a.InTheShelter = row["in the shelter"]

# checkins.csv
for row in asm.csv_to_list(PATH + "checkins.csv", encoding="cp1252"):
    a = None
    if row["Animal Id"] in ppa: a = ppa[row["Animal Id"]]
    if a is None: continue
    if row["Type of Check-In"] is None: continue
    if asm.getdate_iso(row["Check-In Date"]) is not None: 
        a.DateBroughtIn = asm.getdate_iso(row["Check-In Date"])
    if row["Brought In By Id"] in ppo: 
        a.BroughtInByOwnerID = ppo[row["Brought In By Id"]].ID
    if row["Previous Owner Id"] in ppo:
        a.OriginalOwnerID = ppo[row["Previous Owner Id"]].ID
    a.ReasonForEntry = "%s: %s %s %s" % (row["Type of Check-In"], row["Reason for Surrender"], row["General Comments"], row["Hidden Comments"])
    a.EntryReasonID = getentryreason(row["Type of Check-In"])

# adoptions.csv
for row in asm.csv_to_list(PATH + "adoptions.csv", encoding="cp1252"):
    o = None
    if row["Adopter Id"] in ppo: o = ppo[row["Adopter Id"]]
    a = None
    if row["Animal Id"] in ppa: a = ppa[row["Animal Id"]]
    if a is None or o is None: continue
    m = asm.Movement()
    movements.append(m)
    m.OwnerID = o.ID
    m.AnimalID = a.ID
    m.MovementDate = asm.getdate_iso(row["Adopted On"])
    m.MovementType = 1
    m.Comments = row["Comments"]
    a.Archived = 1
    a.ActiveMovementDate = m.MovementDate
    a.ActiveMovementType = 1
    a.ActiveMovementID = m.ID
    if row["Fee"] != "":
        od = asm.OwnerDonation()
        ownerdonations.append(od)
        od.DonationTypeID = 2
        od.DonationPaymentID = 1
        od.Date = m.MovementDate
        od.OwnerID = o.ID
        od.AnimalID = a.ID
        od.MovementID = m.ID
        od.Donation = asm.get_currency(row["Fee"])

# releases.csv
for row in asm.csv_to_list(PATH + "releases.csv", encoding="cp1252"):
    a = None
    if row["Animal Id"] in ppa: a = ppa[row["Animal Id"]]
    if a is None: continue
    m = asm.Movement()
    movements.append(m)
    m.OwnerID = 0
    m.AnimalID = a.ID
    m.MovementDate = asm.getdate_iso(row["Date Released"])
    m.MovementType = 7 # Released to wild
    a.ActiveMovementType = 7
    if row["Type"] == "Transfer":
        m.OwnerID = to.ID
        m.MovementType = 3
        a.ActiveMovementType = 3
    elif row["Type"] == "Returned to Owner":
        m.OwnerID = ro.ID
        m.MovementType = 5
        a.ActiveMovementType = 5
    m.Comments = "%s\n%s %s %s\n%s %s" % (row["Address"], row["City"], row["Region"], row["Postal Code"], row["Type"], row["Comments"])
    a.Archived = 1
    a.ActiveMovementDate = m.MovementDate
    a.ActiveMovementID = m.ID

# movements.csv
for row in asm.csv_to_list(PATH + "movements.csv", encoding="cp1252"):
    a = None
    lastadopted = "0"
    if row["Animal Id"] in ppa: a = ppa[row["Animal Id"]]
    if a is None: continue
    if a.ActiveMovementDate is None and row["Location"] == "Adopted" and row["Animal Id"] != lastadopted: # quite a few duplicate rows together
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = uo.ID
        m.AnimalID = a.ID
        m.MovementDate = asm.getdate_iso(row["Moved On"])
        m.MovementType = 1
        m.Comments = row["Comments"]
        a.Archived = 1
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 1
        a.ActiveMovementID = m.ID
        lastadopted = row["Animal Id"]
    elif row["Location"] == "Foster Care":
        if a.ActiveMovementDate and a.ActiveMovementDate > asm.getdate_iso(row["Moved On"]): continue # Don't bother if the current active adoption is newer than this one
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = fo.ID
        m.AnimalID = a.ID
        m.MovementDate = asm.getdate_iso(row["Moved On"])
        m.MovementType = 2
        m.Comments = row["Comments"]
        a.Archived = 0
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 2
        a.ActiveMovementID = m.ID
    elif row["Location"] == "Transferred to another agency":
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = to.ID
        m.AnimalID = a.ID
        m.MovementDate = asm.getdate_iso(row["Moved On"])
        m.MovementType = 3
        m.Comments = row["Comments"]
        a.Archived = 1
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 3
        a.ActiveMovementID = m.ID

# donations.csv
if asm.file_exists(PATH + "donations.csv"):
    for row in asm.csv_to_list(PATH + "donations.csv", encoding="cp1252"):
        o = None
        if row["Person Id"] in ppo: o = ppo[row["Person Id"]]
        if o is None: continue
        aid = 0
        if row["Animal Id"] in ppa: aid = ppa[row["Animal Id"]].ID
        od = asm.OwnerDonation()
        ownerdonations.append(od)
        od.DonationTypeID = 1
        pm = ""
        if "Method" in row: pm = row["Method"]
        od.DonationPaymentID = 1
        if pm.find("Check") != -1: od.DonationPaymentID = 2
        if pm.find("Credit Card") != -1: od.DonationPaymentID = 3
        if pm.find("Debit Card") != -1: od.DonationPaymentID = 4
        if "Method Details" in row: od.ChequeNumber = row["Method Details"]
        od.Date = asm.getdate_iso(row["Date Donated"])
        if od.Date is None: od.Date = asm.getdate_iso(row["Date Pledged"])
        od.OwnerID = o.ID
        od.AnimalID = aid
        od.MovementID = 0
        od.Donation = asm.get_currency(row["Amount"])
        od.Comments = "%s %s" % (row["Type"], row["Comments"])

# allmedical.csv
vx = {} # lookup of animal ID to vaccinations for speed
for row in asm.csv_to_list(PATH + "allmedical.csv", encoding="cp1252"):
    a = None
    if row["Animal Id"] not in ppa: continue
    a = ppa[row["Animal Id"]]
    dg = asm.getdate_iso(row["Date Given"])
    dn = asm.getdate_iso(row["Date Needed"])

    if row["Type of Medical Entry"] == "Vaccination":
        if a.ID not in vx: vx[a.ID] = []
        # Create a vacc with just the needed date
        if dn is not None:
            av = asm.animal_vaccination(a.ID, dn, None, row["Vaccination"], "%s %s" % (row["Comments"], row["Hidden comments"]))
            animalvaccinations.append(av)
            vx[a.ID].append(av)
        # now, go back through our vaccinations to find any for this animal with a needed date that matches the given date
        # so we can mark them given. This is because ishelters store pairs of given and next needed, where we store needed and given.
        gotone = False
        for v in vx[a.ID]:
            if v.AnimalID == a.ID and v.DateOfVaccination is None and v.DateRequired == dg: 
                v.DateOfVaccination = dg
                v.Comments += " %s %s" % (row["Comments"], row["Hidden comments"])
                gotone = True
        if not gotone and dg is not None:
            # We didn't find one, record it as a standalone vacc
            av = asm.animal_vaccination(a.ID, dg, dg, row["Vaccination"], "%s %s" % (row["Comments"], row["Hidden comments"]))
            animalvaccinations.append(av)

    elif row["Type of Medical Entry"] == "Diagnostic Test":
        if dg is None: dg = a.DateBroughtIn
        animaltests.append( asm.animal_test(a.ID, dg, dg, row["Diagnostic Test Name"], row["Diagnostic Test Result"], "%s %s" % (row["Comments"], row["Hidden comments"])) )

    elif row["Type of Medical Entry"] == "Medical Condition":
        if dg is None: dg = asm.getdate_iso(row["Medical Condition Noticed On"])
        if dg is None: dg = a.DateBroughtIn
        animalmedicals.append(asm.animal_regimen_single(a.ID, dg, row["Medical Condition Name"], "N/A", "%s %s" % (row["Comments"], row["Hidden comments"])))

    elif row["Type of Medical Entry"] == "Medical Procedure":
        if dg is None: dg = dn
        if dg is None: dg = a.DateBroughtIn
        animalmedicals.append(asm.animal_regimen_single(a.ID, dg, row["Medical Procedure Type"], "N/A", "%s %s" % (row["Comments"], row["Hidden comments"])))

    elif dg is not None:
        animalmedicals.append(asm.animal_regimen_single(a.ID, dg, "%s %s" % (row["Medical Procedure Type"], row["Medication Name"]), row["Medication Dose"], "%s %s" % (row["Comments"], row["Hidden comments"])))

# images
if IMAGE_PREFIX != "" and asm.file_exists(PATH + "animalpictures.csv"):
    for row in asm.csv_to_list(PATH + "animalpictures.csv", remove_non_ascii=True):
        pass # not sure of extraction method yet

# Now that everything else is done, output stored records
for a in animals:
    print(a)
for am in animalmedicals:
    print(am)
for at in animaltests:
    print(at)
for av in animalvaccinations:
    print(av)
for o in owners:
    print(o)
for od in ownerdonations:
    print(od)
for m in movements:
    print(m)
for k, v in asm.vaccinationtypes.items():
    if v.ID >= START_ID: print(v)
for k, v in asm.testtypes.items():
    if v.ID >= START_ID: print(v)

asm.stderr_summary(animals=animals, animalmedicals=animalmedicals, animaltests=animaltests, animalvaccinations=animalvaccinations, owners=owners, movements=movements, ownerdonations=ownerdonations)

print("DELETE FROM configuration WHERE ItemName Like 'VariableAnimalDataUpdated';")
print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")

