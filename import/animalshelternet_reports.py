#!/usr/bin/python

import asm, datetime, sys, os

"""
Import script for AnimalShelterNet databases exported to spreadsheet

Requires the following reports:

    Adoption List
    Disposition
    Medication Usage

28th April 2017
"""

PATH = "/home/robin/tmp/asm3_import_data/asn_ba1385"

START_ID = 2500

def gettypeletter(aid):
    tmap = {
        2: "D",
        10: "A",
        11: "U",
        12: "S"
    }
    return tmap[aid]

def getdate(s):
    return asm.getdate_ddmmyyyy(s)

def ce(s, x):
    bits = s.split(",")
    try:
        return bits[x]
    except:
        return ""

owners = []
movements = []
animals = []
animalvaccinations = []

ppa = {}
ppo = {}

asm.setid("adoption", START_ID)
asm.setid("animal", START_ID)
asm.setid("owner", START_ID)
asm.setid("animalvaccination", START_ID)
asm.setid("internallocation", 2)

# Remove existing
print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM internallocation WHERE ID >= 2;"
print "DELETE FROM adoption WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM animal WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM owner WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM animalvaccination WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID

# Create a transfer owner
to = asm.Owner()
owners.append(to)
to.OwnerSurname = "Other Shelter"
to.OwnerName = to.OwnerSurname

# Create an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname

# Load up data files
cadopt = asm.csv_to_list("%s/adoption_list.csv" % PATH, uppercasekeys=True)
cdisp = asm.csv_to_list("%s/disposition.csv" % PATH, uppercasekeys=True)
cmed = asm.csv_to_list("%s/medication_usage.csv" % PATH, uppercasekeys=True, unicodehtml=True)

# Dispositions/animals
for row in cdisp:
    if row["ANIMALUID"] in ppa:
        a = ppa[row["ANIMALUID"]]
    else:
        a = asm.Animal()
        animals.append(a)
        ppa[row["ANIMALUID"]] = a
    a.SpeciesID = asm.species_id_for_name(row["SPECIES"])
    if a.SpeciesID == 1 and row["INTAKE"].startswith("Stray"):
        a.AnimalTypeID = 10
    elif a.SpeciesID == 1:
        a.AnimalTypeID = 2
    elif a.SpeciesID == 2 and row["INTAKE"].startswith("Stray"):
        a.AnimalTypeID = 12
    else:
        a.AnimalTypeID = 11
    a.BreedID = asm.breed_id_for_name(row["PRIMARY BREED"])
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    a.Sex = asm.getsex_mf(row["SEX"])
    a.CrossBreed = 0
    a.generateCode(gettypeletter(a.AnimalTypeID))
    a.ShortCode = row["ANIMALUID"]
    a.AnimalName = row["NAME"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateOfBirth = getdate(row["BIRTHDATE"])
    a.DateBroughtIn = getdate(row["INTAKETS"])
    if a.DateBroughtIn is None:
        a.DateBroughtIn = datetime.datetime.today()
    a.LastChangedDate = a.DateBroughtIn
    a.CreatedDate = a.DateBroughtIn
    a.Neutered = row["ALTERED"] == "Y" and 1 or 0
    a.NeuteredDate = (row["ALTEREDATINTAKE"] == "N" and a.Neutered == 1) and a.DateBroughtIn or None
    a.EntryReasonID = 7 # Stray
    a.EntryTypeID = 2
    if row["INTAKE"].startswith("Owner"): 
        a.EntryReasonID = 17 # Owner
        a.EntryTypeID = 1
    a.ReasonForEntry = "%s %s %s" % (row["INTAKE"], row["INTAKE REASON"], row["INTAKE LOCATION"])
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = asm.location_id_for_name(row["INTAKE LOCATION"])
    if row["DISPOSIT"] == "Euthanize":
        a.DeceasedDate = getdate(row["DISPOSITTS"])
        a.PutToSleep = 1
        a.PTSReason = row["DISPOSIT REASON"]
        a.Archived = 1

# Adoptions
for row in cadopt:
    # Rows contain a person, animal and adoption - person first
    if row["CUSTUID"] in ppo:
        o = ppo[row["CUSTUID"]]
    else:
        o = asm.Owner()
        owners.append(o)
        ppo[row["CUSTUID"]] = o
        o.OwnerSurname = ce(row["NAME"], 0)
        o.OwnerForeNames = ce(row["NAME"], 1)
        o.OwnerAddress = ce(row["ADDRESS"], 0)
        o.OwnerTown = ce(row["ADDRESS"], 1)
        o.OwnerCounty = ce(row["ADDRESS"], 2)
        o.OwnerPostcode = ce(row["ADDRESS"], 3)
        if row["PHONE1"].startswith("Home"):
            o.HomeTelephone = row["PHONE1"].replace("Home-", "")
        if row["PHONE2"].startswith("Home"):
            o.HomeTelephone = row["PHONE2"].replace("Home-", "")
        if row["PHONE1"].startswith("Cell"):
            o.MobileTelephone = row["PHONE1"].replace("Cell-", "")
        if row["PHONE2"].startswith("Cell"):
            o.MobileTelephone = row["PHONE2"].replace("Cell-", "")
        o.EmailAddress = row["EMAIL"]
    # Find the animal record - bail if we don't have one
    if not row["ANIMALUID"] in ppa:
        continue
    a = ppa[row["ANIMALUID"]]
    # Add some extra animal info
    a.BreedID = asm.breed_id_for_name(row["BREED1"])
    if row["BREED2"] == "Unknown" or row["BREED2"] == "Mix": 
        a.Breed2ID = 442
    else:
        a.Breed2ID = asm.breed_id_for_name(row["BREED2"])
    a.BreedName = asm.breed_name_for_id(a.BreedID) + " / " + asm.breed_name_for_id(a.Breed2ID)
    a.CrossBreed = 1
    a.Neutered = row["ALTERED"] == "Y" and 1 or 0
    a.IdentichipNumber = row["CHIPNUMBER"]
    if a.IdentichipNumber != "": a.Identichipped = 1
    # Do the adoption
    m = asm.Movement()
    m.AnimalID = a.ID
    m.OwnerID = o.ID
    m.MovementType = 1
    m.MovementDate = getdate(row["ADOPTION"])
    a.Archived = 1
    a.ActiveMovementID = m.ID
    a.ActiveMovementDate = m.MovementDate
    a.ActiveMovementType = 1
    movements.append(m)

# Medical
for row in cmed:
    auid = row["ANIMAL NUMBER"]
    if auid.find("&") != -1: auid = auid[0:auid.find("&")]
    if not auid in ppa: continue
    a = ppa[auid]
    date = asm.getdate_mmddyy(row["DATE USED"])
    # Each row contains a vaccination or test
    if row["MED"].startswith("HW Test"):
        a.HeartwormTested = 1
        a.HeartwormTestDate = date
        a.HeartwormTestResult = row["NOTES"].find("gative") != -1 and 1 or 2
    elif row["MED"].startswith("Combo"):
        a.CombiTested = 1
        a.CombiTestDate = date
        a.CombiTestResult = row["NOTES"].find("gative") != -1 and 1 or 2
    else:
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.DateRequired = date
        av.DateOfVaccination = date
        av.VaccinationID = 6
        if row["MED"].startswith("FelV"): av.VaccinationID = 12
        if row["MED"].startswith("FVRCP"): av.VaccinationID = 9
        if row["MED"].startswith("DA2PP"): av.VaccinationID = 8
        if row["MED"].startswith("Bord"): av.VaccinationID = 6
        if row["MED"].startswith("Rabies"): av.VaccinationID = 4
        if row["MED"].startswith("Lepto"): av.VaccinationID = 3
        av.Comments = "%s %s" % (row["MED"], row["NOTES"])

# Run back through the animals, if we have any that are still
# on shelter after 1 year, add an adoption to an unknown owner
for a in animals:
    if a.Archived == 0 and a.DateBroughtIn < asm.subtract_days(asm.now(), 365):
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = uo.ID
        m.MovementType = 1
        m.MovementDate = a.DateBroughtIn
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = a.DateBroughtIn
        a.ActiveMovementType = 1
        movements.append(m)

# Now that everything else is done, output stored records
for k,v in asm.locations.iteritems():
    print v
for a in animals:
    print a
for av in animalvaccinations:
    print av
for o in owners:
    print o
for m in movements:
    print m

#asm.stderr_allanimals(animals)
#asm.stderr_onshelter(animals)
asm.stderr_summary(animals=animals, animalvaccinations=animalvaccinations, owners=owners, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

