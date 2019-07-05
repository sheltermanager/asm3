#!/usr/bin/python

import asm

"""
Import script for iShelters CSV export.
It can be accessed by going to adminShelter and then System->Misc->Downloads

7th July, 2015 - 18th May, 2016
"""

PATH = "/home/robin/tmp/asm3_import_data/ishelters_cm2044/"

# Files needed
# adoptions.csv, animals.csv, checkins.csv, donations.csv, allmedical.csv, people.csv, releases.csv

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
    for k, v in er.iteritems():
        if s.find(k) != -1:
            return v
    return 11

# --- START OF CONVERSION ---
print "\\set ON_ERROR_STOP\nBEGIN;"

animals = []
animalmedicals = []
animalvaccinations = []
owners = []
ownerdonations = []
ppo = {}
ppa = {}
movements = []

asm.setid("adoption", 100)
asm.setid("animal", 100)
asm.setid("animalmedical", 100)
asm.setid("animalmedicaltreatment", 100)
asm.setid("animalvaccination", 100)
asm.setid("owner", 100)
asm.setid("ownerdonation", 100)

print "DELETE FROM adoption WHERE ID >= 100;"
print "DELETE FROM animal WHERE ID >= 100;"
print "DELETE FROM animalmedical WHERE ID >= 100;"
print "DELETE FROM animalmedicaltreatment WHERE ID >= 100;"
print "DELETE FROM animalvaccination WHERE ID >= 100;"
print "DELETE FROM owner WHERE ID >= 100;"
print "DELETE FROM ownerdonation WHERE ID >= 100;"
print "DELETE FROM vaccinationtype;"

to = asm.Owner()
to.OwnerSurname = "Unknown Transfer Owner"
owners.append(to)

ro = asm.Owner()
ro.OwnerSurname = "Unknown Reclaim Owner"
owners.append(ro)

# people.csv
for row in asm.csv_to_list(PATH + "people.csv"):
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
for row in asm.csv_to_list(PATH + "animals.csv"):
    if row["name"] is None: continue
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
    a.NeuteredDate = asm.getdate_iso(row["neutered/spayed date"])
    if a.NeuteredDate is not None: a.Neutered = 1
    a.Archived = 0
    a.IdentichipNumber = row["microchip #"]
    if a.IdentichipNumber != "": a.Identichipped = 1
    a.HiddenAnimalDetails = "Original Breed: %s/%s, Color: %s\n%s" % (row["primary breed"], row["secondary breed"], row["primary color"], row["hidden comments"])
    a.AnimalComments = row["general comments"]
    a.Markings = row["distinctive features"]
    a.DeceasedDate = asm.getdate_iso(row["date of death"])
    a.PTSReason = row["reason of death"]
    a.RabiesTag = row["tag #"]

    a.InTheShelter = row["in the shelter"]

# checkins.csv
for row in asm.csv_to_list(PATH + "checkins.csv"):
    a = None
    if ppa.has_key(row["Animal Id"]): a = ppa[row["Animal Id"]]
    if a is None: continue
    a.DateBroughtIn = asm.getdate_iso(row["Check-In Date"])
    if ppo.has_key(row["Brought In By Id"]): 
        a.BroughtInByOwnerID = ppo[row["Brought In By Id"]].ID
    if ppo.has_key(row["Previous Owner Id"]):
        a.OriginalOwnerID = ppo[row["Previous Owner Id"]].ID
    a.ReasonForEntry = "%s: %s %s %s" % (row["Type of Check-In"], row["Reason for Surrender"], row["General Comments"], row["Hidden Comments"])
    a.EntryReasonID = getentryreason(row["Type of Check-In"])

# adoptions.csv
for row in asm.csv_to_list(PATH + "adoptions.csv"):
    o = None
    if ppo.has_key(row["Adopter Id"]): o = ppo[row["Adopter Id"]]
    a = None
    if ppa.has_key(row["Animal Id"]): a = ppa[row["Animal Id"]]
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
for row in asm.csv_to_list(PATH + "releases.csv"):
    a = None
    if ppa.has_key(row["Animal Id"]): a = ppa[row["Animal Id"]]
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

# donations.csv
for row in asm.csv_to_list(PATH + "donations.csv"):
    o = None
    if ppo.has_key(row["Person Id"]): o = ppo[row["Person Id"]]
    if o is None: continue
    aid = 0
    if ppa.has_key(row["Animal Id"]): aid = ppa[row["Animal Id"]].ID
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
for row in asm.csv_to_list(PATH + "allmedical.csv"):
    a = None
    if not ppa.has_key(row["Animal Id"]): continue
    a = ppa[row["Animal Id"]]
    dg = asm.getdate_iso(row["Date Given"])
    if dg is None: dg = a.DateBroughtIn
    if row["Type of Medical Entry"] == "Vaccination":
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.AnimalID = a.ID
        av.DateRequired = asm.getdate_iso(row["Date Needed"])
        av.DateOfVaccination = dg
        if av.DateRequired is None: av.DateRequired = av.DateOfVaccination
        av.VaccinationID = asm.vaccinationtype_id_for_name(row["Vaccination"], True)
        av.Comments = "%s %s" % (row["Comments"], row["Hidden comments"])
    else:
        animalmedicals.append(asm.animal_regimen_single(a.ID, dg, "%s %s" % (row["Medical Procedure Type"], row["Medication Name"]), row["Medication Dose"], "%s %s" % (row["Comments"], row["Hidden comments"])))

# Now that everything else is done, output stored records
print "DELETE FROM primarykey;"
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
for k, v in asm.vaccinationtypes.iteritems():
    print v

asm.stderr_summary(animals=animals, animalmedicals=animalmedicals, animalvaccinations=animalvaccinations, owners=owners, movements=movements, ownerdonations=ownerdonations)

print "DELETE FROM configuration WHERE ItemName Like 'VariableAnimalDataUpdated';"
print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

