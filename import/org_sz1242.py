#!/usr/bin/python

import asm

"""
Import script for sz1242 custom access database 
layout (adoptions, catinfo, returns)

22nd November, 2016
"""

# --- START OF CONVERSION ---

owners = []
movements = []
animals = []
ppa = {}
ppo = {}

asm.setid("animal", 100)
asm.setid("owner", 100)
asm.setid("adoption", 100)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM owner WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM adoption WHERE ID >= 100 AND CreatedBy = 'conversion';"

cadoptions = asm.csv_to_list("data/sz1242_access/adoptions.csv", unicodehtml=True)
ccatinfo = asm.csv_to_list("data/sz1242_access/catinfo.csv", unicodehtml=True)
creturns = asm.csv_to_list("data/sz1242_access/returns.csv", unicodehtml=True)

for d in ccatinfo:
    a = asm.Animal()
    animals.append(a)
    ppa[d["CatName"]] = a
    a.AnimalTypeID = 12 # stray cat
    if d["AcquiredType"].startswith("County"):
        a.AnimalTypeID = 44 # county shelter cat
        a.TransferIn = 1
    a.SpeciesID = 2
    a.AnimalName = d["CatName"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateBroughtIn = asm.getdate_mmddyy(d["DateAcquired"])
    if a.DateBroughtIn is None:
        a.DateBroughtIn = asm.today()
    ea = asm.cint(d["EstimatedAge"])
    eu = d["EstimatedAgeUnits"]
    if eu.startswith("Week"):
        ea = ea * 7
    elif eu.startswith("Month"):
        ea = ea * 30.5
    elif eu.startswith("Year"):
        ea = ea * 365
    a.DateOfBirth = asm.subtract_days(a.DateBroughtIn, ea)
    if a.DateOfBirth is None:
        a.DateOfBirth = asm.today()
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    a.generateCode()
    a.ShortCode = d["IDNumber"]
    a.Markings = d["Description"]
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 1
    a.Sex = asm.getsex_mf(d["CatGender"])
    a.Size = 2
    a.Neutered = d["Sterilized"] == "1" and 1 or 0
    a.NeuteredDate = asm.getdate_mmddyy(d["SterilizedDate"])
    a.ReasonForEntry = d["AcquiredType"] + "::" + d["AcquiredFrom"]
    a.IdentichipNumber = d["MicrochipNo"]
    if a.IdentichipNumber != "":
        a.Identichipped = 1
    a.IsGoodWithCats = 2
    a.IsGoodWithDogs = 2
    a.IsGoodWithChildren = 2
    a.HouseTrained = 0
    a.Archived = 0
    a.BreedID = 261
    a.Breed2ID = 261
    a.BreedName = "Domestic Short Hair"
    a.CrossBreed = 0
    if d["Deceased"] == "1":
        a.DeceasedDate = a.DateBroughtIn
        a.PTSReasonID = 2
        a.Archived = 1

for d in cadoptions:
    if d["AdoptedBy"].strip() != "" and asm.cint(d["AdoptedBy"]) == 0:
        if ppo.has_key(d["AdoptedBy"]):
            o = ppo[d["AdoptedBy"]]
        else:
            o = asm.Owner()
            owners.append(o)
            ppo[d["AdoptedBy"]] = o
            o.OwnerName = d["AdoptedBy"]
            bits = o.OwnerName.split(" ")
            if len(bits) > 1:
                o.OwnerForeNames = bits[0]
                o.OwnerSurname = bits[len(bits)-1]
            else:
                o.OwnerSurname = o.OwnerName

    if ppa.has_key(d["CatName"]):
        a = ppa[d["CatName"]]
        if a is None or o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = asm.getdate_mmddyy(d["DateAdopted"])
        mc = ""
        if d["AdoptionCounsellor"] != "":
            mc = "Adoption counsellor: %s" % d["AdoptionCounsellor"]
        m.Comments = mc
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 1
        a.LastChangedDate = m.MovementDate
        movements.append(m)

for d in creturns:
    if ppa.has_key(d["CatName"]):
        a = ppa[d["CatName"]]
        for m in movements:
            if m.AnimalID == a.ID and m.ReturnDate is None:
                m.ReturnDate = asm.getdate_mmddyy(d["ReturnDate"])
                m.ReasonForReturn = d["Reason"]
                break

# Now that everything else is done, output stored records
for a in animals:
    print a
for o in owners:
    print o
for m in movements:
    print m

asm.stderr_summary(animals=animals, owners=owners, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

