#!/usr/bin/python

import asm

"""
Import script for kw1533

21st December, 2017
"""

def getdate(d):
    return asm.parse_date(d, "%d.%m.%y")

def movement_type(d):
    if d == "Adoption": return 1
    elif d == "Foster": return 2
    elif d == "Reclaimed": return 5
    raise Exception("Surprise movement type %s" % d)

# --- START OF CONVERSION ---

owners = []
movements = []
animals = []
animaltests = []
animalvaccinations = []

asm.setid("animal", 100)
asm.setid("animaltest", 100)
asm.setid("animalvaccination", 100)
asm.setid("owner", 100)
asm.setid("adoption", 100)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM animaltest WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM animalvaccination WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM owner WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM adoption WHERE ID >= 100 AND CreatedBy = 'conversion';"

for d in asm.csv_to_list("data/kw1533_excel.csv"):
    a = asm.Animal()
    animals.append(a)
    a.AnimalTypeID = "COALESCE((SELECT ID FROM animaltype WHERE AnimalType LIKE '%s%%' LIMIT 1), 11)" % d["Type"]
    a.EntryReasonID = 17 # Surrender
    if d["Entry Category"] == "Stray": a.EntryReasonID = 7 # Stray
    a.SpeciesID = asm.species_id_for_name(d["Species"])
    a.AcceptanceNumber = d["Litter"]
    a.AnimalName = d["Name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateBroughtIn = getdate(d["Date brought in"])
    if a.DateBroughtIn is None:
        a.DateBroughtIn = asm.today()
    if "Date Of Birth" in d and d["Date of Birth"].strip() != "":
        a.DateOfBirth = getdate(d["Date of Birth"])
    else:
        a.DateOfBirth = asm.subtract_days(a.DateBroughtIn, 365)
    a.EstimatedDOB = d["Estimate"] == "Yes" and 1 or 0
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    a.generateCode()
    if d["Old number (notes field)"] != "":
        a.ShortCode = d["Old number (notes field)"]
    a.ReasonForEntry = d["Reason for Entry"]
    a.ShelterLocation = asm.location_from_db(d["Internal Location"])
    a.Sex = asm.getsex_mf(d["Sex"])
    a.BreedID = "COALESCE((SELECT ID FROM breed WHERE BreedName LIKE '%s' LIMIT 1), 1)" % d["Breed 1"]
    if d["Breed 2"].strip() == "" or d["Breed 2"] == "NULL":
        a.Breed2ID = a.BreedID
        a.BreedName = asm.breed_name_for_id(a.BreedID)
        a.CrossBreed = 0
    else:
        a.Breed2ID = "COALESCE((SELECT ID FROM breed WHERE BreedName LIKE '%s' LIMIT 1), 1)" % d["Breed 2"]
        a.BreedName = asm.breed_name_for_id(a.BreedID) + " / " + asm.breed_name_for_id(a.Breed2ID)
        a.CrossBreed = 1
    a.BaseColourID = asm.colour_id_for_name(d["Colour"])
    a.Markings = d["Markings"]
    a.AnimalComments = d["Comments"]
    a.HiddenAnimalDetails = "breed: %s / %s, colour: %s" % (d["Breed 1"], d["Breed 2"], d["Colour"])
    a.Weight = asm.cfloat(d["Wt"])
    a.Size = 2
    if d["Size"] == "Large": a.Size = 1
    if d["Size"] == "Small": a.Size = 3
    a.Identichipped = d["Microchip"] == "Yes" and 1 or 0
    a.IdentichipNumber = d["Microchip number"]
    a.IdentichipDate = getdate(d["Microchip date"])
    a.Neutered = d["Neutered/Spayed"] == "Yes" and 1 or 0
    a.NeuteredDate = getdate(d["Neutered Date"])
    if d["Flag"].strip() != "":
        a.AdditionalFlags = d["Flag"] + "|"
    a.DeceasedDate = getdate(d["Deceased Date"])
    a.PTSReasonID = 4
    a.PTSReason = d["Reason"]
    if a.DeceasedDate:
        a.Archived = 1

    if d["Movement 1 Person"] != "" and d["Movement 1 Type"] != "":
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = "(SELECT ID FROM owner WHERE OwnerCode = '%s')" % d["Movement 1 Person"].replace("'", "`")
        m.MovementType = movement_type(d["Movement 1 Type"])
        m.MovementDate = getdate(d["Movement 1 date"])
        m.ReturnDate = getdate(d["Movement 1 Return Date"])
        a.Archived = m.MovementType == 2 and 0 or 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = m.MovementType
        a.LastChangedDate = m.MovementDate
        movements.append(m)

    if d["Movement 2 Person"] != "" and d["Movement 2 Type"] != "":
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = "(SELECT ID FROM owner WHERE OwnerCode = '%s')" % d["Movement 2 Person"].replace("'", "`")
        m.MovementType = movement_type(d["Movement 2 Type"])
        m.MovementDate = getdate(d["Movement 2 date"])
        m.ReturnDate = getdate(d["Movement 2 Return Date"])
        a.Archived = m.MovementType == 2 and 0 or 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = m.MovementType
        a.LastChangedDate = m.MovementDate
        movements.append(m)

    for x in range(1, 9):
        vgiven = getdate(d["Vaccination %d Given" % x])
        vtype = d["Vaccination %d Type" % x]
        if vgiven:
            av = asm.AnimalVaccination()
            animalvaccinations.append(av)
            av.AnimalID = a.ID
            av.VaccinationID = "COALESCE((SELECT ID FROM vaccinationtype WHERE VaccinationType LIKE '%s' LIMIT 1), 1)" % vtype
            av.DateRequired = vgiven
            av.DateOfVaccination = vgiven

    for x in range(1, 9):
        tperformed = getdate(d["Test %d Performed" % x])
        ttype = d["Test %d Type" % x].strip()[0:5]
        tresult = d["Test %d Result" % x]
        tcomments = d["Test %d Comments" % x]
        if tperformed:
            at = asm.AnimalTest()
            animaltests.append(at)
            at.AnimalID = a.ID
            at.DateRequired = tperformed
            at.DateOfTest = tperformed
            at.TestTypeID = "COALESCE((SELECT ID FROM testtype WHERE TestName LIKE '%%%s%%' LIMIT 1), 1)" % ttype
            asmresult = 0
            if tresult == "Negative": asmresult = 1
            if tresult == "Positive": asmresult = 2
            at.TestResultID = asmresult + 1
            at.Comments = tcomments

# Now that everything else is done, output stored records
for a in animals:
    print a
for at in animaltests:
    print at
for av in animalvaccinations:
    print av
for m in movements:
    print m

asm.stderr_summary(animals=animals, animaltests=animaltests, animalvaccinations=animalvaccinations, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

