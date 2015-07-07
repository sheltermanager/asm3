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
owners = []
ppo = {}
ppa = {}
movements = []

asm.setid("animal", 100)
asm.setid("owner", 100)
asm.setid("ownerdonation", 100)
asm.setid("adoption", 100)
asm.setid("animalvaccination", 100)

print "DELETE FROM animal WHERE ID >= 100;"
print "DELETE FROM animalvaccination WHERE ID >= 100;"
print "DELETE FROM owner WHERE ID >= 100;"
print "DELETE FROM ownerdonation WHERE ID >= 100;"
print "DELETE FROM adoption WHERE ID >= 100;"

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
    a.CrossBreed = row["Secondary Breed"] != "" and 1 or 0
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    a.BaseColourID = asm.color_id_for_name(row["Primary Color"])
    a.Sex = asm.get_sexmf(row["Gender"])
    a.DateOfBirth = asm.getdate_yyyymmdd(row["Birthdate"])
    a.DateBroughtIn = asm.getdate_yyyymmdd(row["Check-In Date"])
    a.EntryReasonID = getentryreason(row["Check-In Type"])
    a.ReasonForEntry = row["Check-In Type"] + ": " + row["Reason for Surrender"]
    a.NeuteredDate = asm.getdate_yyyymmdd(row["Fixed On"])
    if a.NeuteredDate is not None: a.Neutered = 1
    a.Archived = 0
    a.IdentichipNumber = row["Microchip Number"]
    if a.IdentichipNumber != "": a.Identichipped = 1
    a.OriginalOwnerID = getcreateowner(row["Prev. Own F. Name"], row["Prev. Own L. Name"], row["Prev. Own Address"], row["Prev. Own City"], row["Prev. Own Region"], row["Prev. Own Postal Code"])

# adoptions.csv
for row in asm.csv_to_list(PATH + "adoptions.csv"):
    
    ### UPTO HERE ###

    # Find the animal and owner for this movement
    a = findanimal(row["animalid"])
    o = findowner(row["recnum"])
    if a != None and o != None:
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = o.ID
        m.AnimalID = a.ID
        if a.ActiveMovementDate is not None:
            m.MovementDate = a.ActiveMovementDate
        else:
            m.MovementDate = getdate(row["adddatetime"])
        m.MovementType = 1
        a.Archived = 1
        a.ActiveMovementType = 1
        a.ActiveMovementID = m.ID

# tblanimalvettreatments.csv
for row in asm.csv_to_list(PATH + "tblanimalvettreatments.csv"):
    av = asm.AnimalVaccination()
    av.DateRequired = getdate(row["dueDate"])
    if av.DateRequired is None:
        av.DateRequired = getdate(row["addDateTime"])
    av.DateOfVaccination = getdate(row["dateGiven"])
    a = findanimal(row["animalid"])
    if a == None: continue
    av.AnimalID = a.ID
    av.VaccinationID = int(row["vacc"].strip())
    print av

# tblreceiptentry.csv
for row in asm.csv_to_list(PATH + "tblreceiptentry.csv"):
    od = asm.OwnerDonation()
    od.DonationTypeID = 1
    pm = getsbpaymentmethod(row["paymentmethod"])
    od.DonationPaymentID = 1
    if pm.find("Check") != -1: od.DonationPaymentID = 2
    if pm.find("Credit Card") != -1: od.DonationPaymentID = 3
    if pm.find("Debit Card") != -1: od.DonationPaymentID = 4
    od.Date = getdate(row["receiptdate"])
    od.OwnerID = findowner(row["recnum"]).ID
    od.Donation = asm.get_currency(row["Amount"])
    comments = "Check No: " + row["chequeno"]
    comments += "\nMethod: " + pm
    comments += "\n" + row["NotesToPrint"]
    od.Comments = comments
    print od

# Now that everything else is done, output stored records
print "DELETE FROM primarykey;"
print "DELETE FROM configuration WHERE ItemName Like 'VariableAnimalDataUpdated';"
for a in animals:
    print a
for o in owners:
    print o
for m in movements:
    print m

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

