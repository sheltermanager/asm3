#!/usr/bin/python

import asm

"""
Import script for iShelters Excel sheets
7th July, 2015
"""

PATH = "data/ishelters_beltrami/"

# Files needed
# adoptions.csv, checkins.csv, medical.csv, volunteers.csv

def getcreateowner(first, last, address, city, state, postal):
    global owners
    global ppo
    k = first + last + address
    if ppo.has_key(k):
        return ppo[k]
    else:
        o = asm.Owner()
        owners.append(o)
        ppo[k] = o
        o.OwnerForeNames = first
        o.OwnerSurname = last
        o.OwnerName = first + " " + last
        o.OwnerAddress = address
        o.OwnerTown = city
        o.OwnerCounty = state
        o.OwnerPostcode = postal
        return o

def getentryreason(s):
    er = {
        "Surrendered": 11,
        "Return": 11,
        "Stray": 7,
        "Born in the Shelter": 13,
        "Abandoned at the Shelter": 11,
        "Impound": 7
    }
    for k, v in er.iteritems():
        if s.find(k) != -1:
            return v
    return 11

# --- START OF CONVERSION ---
print "\\set ON_ERROR_STOP\nBEGIN;"

animals = []
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

# checkins.csv
for row in asm.csv_to_list(PATH + "checkins.csv"):
    a = asm.Animal()
    animals.append(a)
    ppa[row["Code"]] = a
    a.AnimalName = row["Name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.ShortCode = row["Code"]
    a.AnimalTypeID = asm.type_id_for_name(row["Species"])
    a.SpeciesID = asm.species_id_for_name(row["Species"])
    a.BreedID = asm.breed_id_for_name(row["Primary Breed"])
    a.Breed2ID = asm.breed_id_for_name(row["Secondary Breed"])
    a.CrossBreed = asm.iif(row["Secondary Breed"] != "", 1, 0)
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    a.BaseColourID = asm.colour_id_for_name(row["Primary Color"])
    a.Sex = asm.getsex_mf(row["Gender"])
    a.DateBroughtIn = asm.getdate_iso(row["Check-In Date"])
    if a.DateBroughtIn is None: a.DateBroughtIn = asm.today()
    a.DateOfBirth = asm.getdate_iso(row["Birthdate"])
    if a.DateOfBirth is None: a.DateOfBirth = a.DateBroughtIn
    a.EntryReasonID = getentryreason(row["Check-In Type"])
    a.ReasonForEntry = row["Check-In Type"] + ": " + row["Reason for Surrender"]
    a.NeuteredDate = asm.getdate_iso(row["Fixed On"])
    if a.NeuteredDate is not None: a.Neutered = 1
    a.Archived = 0
    a.IdentichipNumber = row["Microchip Number"]
    if a.IdentichipNumber != "": a.Identichipped = 1
    a.OriginalOwnerID = getcreateowner(row["Prev. Own F. Name"], row["Prev. Own L. Name"], row["Prev. Own Address"], row["Prev. Own City"], row["Prev. Own Region"], row["Prev. Own Postal Code"]).ID
    a.HiddenAnimalDetails = "Original Breed: %s/%s, Color: %s" % (row["Primary Breed"], row["Secondary Breed"], row["Primary Color"])

# adoptions.csv
for row in asm.csv_to_list(PATH + "adoptions.csv"):
    o = getcreateowner(row["First"], row["Last"], row["Address"] + " " + row["2nd Address Line"], row["City"], row["State"], row["Zip"])
    o.HomeTelephone = row["Home"]
    o.WorkTelephone = row["Work"]
    o.MobileTelephone = row["Cell"]
    o.EmailAddress = row["Email"]
    a = None
    if ppa.has_key(row["Code"]): a = ppa[row["Code"]]
    if o is not None and a is not None:
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = o.ID
        m.AnimalID = a.ID
        m.MovementDate = asm.getdate_iso(row["Adoption Date"])
        m.MovementType = 1
        a.Archived = 1
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 1
        a.ActiveMovementID = m.ID
        if row["Fee"] != "":
            od = asm.OwnerDonation()
            ownerdonations.append(od)
            od.DonationTypeID = 2
            pm = row["Payment Type"]
            od.DonationPaymentID = 1
            if pm.find("Check") != -1: od.DonationPaymentID = 2
            if pm.find("Credit Card") != -1: od.DonationPaymentID = 3
            if pm.find("Debit Card") != -1: od.DonationPaymentID = 4
            od.Date = m.MovementDate
            od.OwnerID = o.ID
            od.AnimalID = a.ID
            od.MovementID = m.ID
            od.Donation = asm.get_currency(row["Fee"])
            od.Comments = row["Payment Details"]

# medicals.csv
for row in asm.csv_to_list(PATH + "medicals.csv"):
    a = None
    if not ppa.has_key(row["Code"]): continue
    a = ppa[row["Code"]]
    if row["Type"] == "Vaccination":
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.AnimalID = a.ID
        av.DateRequired = asm.getdate_iso(row["Date needed"])
        av.DateOfVaccination = asm.getdate_iso(row["Date given"])
        if av.DateRequired is None: av.DateRequired = av.DateOfVaccination
        av.VaccinationID = asm.vaccinationtype_id_for_name(row["Information"], True)
    else:
        asm.animal_regimen_single(a.ID, asm.getdate_iso(row["Date given"]), row["Information"], row["Type"], row["Given at"])

# volunteers.csv
for row in asm.csv_to_list(PATH + "volunteers.csv"):
    o = asm.Owner()
    owners.append(o)
    o.OwnerForeNames = row["First Name"]
    o.OwnerSurname = row["Last Name"]
    o.HomeTelephone = row["Home Phone"]
    o.WorkTelephone = row["Work Phone"]
    o.MobileTelephone = row["Cell Phone"]
    o.EmailAddress = row["Primary Email"]
    o.OwnerAddress = row["Address 1st Line"] + " " + row["Address 2nd Line"]
    o.OwnerTown = row["City"]
    o.OwnerCounty = row["State"]
    o.OwnerPostcode = row["Zip Code"]
    types = row["Type(s)"]
    if row["Banned Date"] != "": o.IsBanned = 1
    if types.find("Volunteer") != -1: o.IsVolunteer = 1
    if types.find("Employee") != -1: o.IsStaff = 1
    if types.find("Member") != -1: o.IsMember = 1
    if types.find("Foster") != -1: o.IsFosterer = 1

# Now that everything else is done, output stored records
print "DELETE FROM primarykey;"
for a in animals:
    print a
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

print "DELETE FROM configuration WHERE ItemName Like 'VariableAnimalDataUpdated';"
print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

