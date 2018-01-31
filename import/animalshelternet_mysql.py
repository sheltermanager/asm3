#!/usr/bin/python

import asm, datetime, sys, os, web

"""
Import script for AnimalShelterNet databases in MYSQL form.

Does people, animals, intakes and dispositions.

Currently does not do medical, payments or licenses because the last conversion
we did with a MySQL ASN database did not have data in any of those tables.

13th September 2017
"""

db = web.database( dbn = "mysql", db = "zc1502", user = "robin", pw = "robin" )

START_ID = 100
HOLDS_AS_ADOPTIONS = True
FIX_FIELD_LENGTHS = True

if FIX_FIELD_LENGTHS:
    db.query("ALTER TABLE animals MODIFY Name VARCHAR(255)")
    db.query("ALTER TABLE animals MODIFY MicrochipID VARCHAR(255)")

def gettypeletter(aid):
    tmap = {
        2: "D",
        10: "A",
        11: "U",
        12: "S"
    }
    return tmap[aid]

def ynu(s):
    if s == "Y": return 0
    if s == "N": return 1
    if s == "U": return 2

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

# Remove existing
print "\\set ON_ERROR_STOP\nBEGIN;"
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

# People
for row in db.select("people"):
    o = asm.Owner()
    owners.append(o)
    ppo[str(row.CustUid)] = o
    o.OwnerTitle = row.Title
    o.OwnerSurname = row.LastName
    if o.OwnerSurname == "": 
        o.OwnerSurname = row.OrgName
        o.OwnerType = 2
    o.OwnerForeNames = row.FirstName
    o.OwnerAddress = row.Addr1 + " " + row.Addr2
    o.OwnerTown = row.City
    o.OwnerCounty = row.State
    o.OwnerPostcode = row.Zip
    o.HomeTelephone = row.Phone1
    o.WorkTelephone = row.Phone2
    o.MobileTelephone = row.Phone3
    o.Comments = row.Comments
    o.IsACO = asm.iif(row.ACOFlag == "Y", 1, 0)
    o.IsShelter = asm.iif(row.RescueFlag == "Y", 1, 0)
    o.IsFosterer = asm.iif(row.FosterFlag == "Y", 1, 0)
    o.IsMember = asm.iif(row.MailingList == "Y", 1, 0)
    o.EmailAddress = row.Email

# Animals/intake
for row in db.query("select animals.*, intake.Comments as IntakeComments, intake.CustUid as IntakeCustUid, " \
    "IntakeDTL1, IntakeDTL2, " \
    "coalesce((select descr from lookup where value = intake.ReasonCode limit 1), '') AS IntakeReason, " \
    "coalesce((select descr from lookup where value = animals.Color limit 1), '') AS ColorName " \
    "from animals " \
    "left outer join intake on intake.RefUID = animals.IntakeRefUID " \
    "order by IntakeDTL1").list():

    if str(row.AnimalUid) in ppa:
        a = ppa[str(row.AnimalUid)]
    else:
        a = asm.Animal()
        animals.append(a)
        ppa[str(row.AnimalUid)] = a
    a.SpeciesID = asm.species_id_for_name(row.Species)
    if a.SpeciesID == 1 and row.IntakeReason.startswith("Stray"):
        a.AnimalTypeID = 10
    elif a.SpeciesID == 1:
        a.AnimalTypeID = 2
    elif a.SpeciesID == 2 and row.IntakeReason.startswith("Stray"):
        a.AnimalTypeID = 12
    else:
        a.AnimalTypeID = 11
    a.ReasonForEntry = "%s. %s" % (row.IntakeReason, row.IntakeComments)
    a.EntryReasonID = 7 # Stray
    if row.IntakeReason.startswith("Owner"): a.EntryReasonID = 17 # Owner
    asm.breed_ids(a, row.Breed1, row.Breed2)
    a.BaseColourID = asm.colour_id_for_name(row.ColorName, firstWordOnly=True)
    a.Sex = asm.getsex_mf(row.Sex)
    a.generateCode(gettypeletter(a.AnimalTypeID))
    a.ShortCode = row.AnimalUid
    a.AnimalName = row.Name
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.RabiesTag = row.RabiesNum
    a.ShelterLocationUnit = row.CageLocation
    a.Markings = row.Marking
    a.GoodWithCats = ynu(row.GoodWithCats)
    a.GoodWithDogs = ynu(row.GoodWithDogs)
    a.GoodWithChildren = ynu(row.GoodWithChildren)
    a.HouseTrained = ynu(row.HouseBroken)
    a.AnimalComments = row.Comments
    a.HiddenAnimalDetails = "Original breed: %s / %s, color: %s" % (row.Breed1, row.Breed2, row.ColorName)
    a.IdentichipNumber = asm.nulltostr(row.MicrochipID)
    if a.IdentichipNumber != "": a.Identichipped = 1
    a.TattooNumber = asm.nulltostr(row.tattoo)
    if a.TattooNumber != "": a.Tattoo = 1
    if row.Size == "X": a.Size = 0
    if row.Size == "L": a.Size = 1
    if row.Size == "M": a.Size = 2
    if row.Size == "S": a.Size = 3
    if row.AlteredAtIntake == "Y": 
        a.Neutered = 1
    a.NeuteredDate = row.AlteredDate
    if a.NeuteredDate is not None:
        a.Neutered = 1
    if row.Declawed == "Y": a.Declawed = 1
    if str(row.IntakeCustUid) in ppo:
        a.OriginalOwnerID = ppo[str(row.IntakeCustUid)].ID
        a.BroughtInByOwnerID = a.OriginalOwnerID
    a.DateOfBirth = row.Birthdate
    a.DateBroughtIn = row.IntakeDTL1
    if a.DateBroughtIn is None:
        # If there's no intake date/link, assume a non-shelter animal instead
        a.DateBroughtIn = row.tsAdded
        a.NonShelterAnimal = 1
        a.Archived = 1
    if a.DateOfBirth is None:
        a.DateOfBirth = a.DateBroughtIn or row.tsAdded
    a.LastChangedDate = a.DateBroughtIn
    a.CreatedDate = a.DateBroughtIn

# Dispositions/animals
for row in db.query("select disposit.*, (select descr from lookup where value = disposit.transtype limit 1) as disptype from disposit").list():
    a = None
    if str(row.AnimalUid) in ppa:
        a = ppa[str(row.AnimalUid)]
    if a is None: continue

    if row.disptype == "Euthanize":
        a.DeceasedDate = row.DispositDTL1
        a.PutToSleep = 1
        a.PTSReason = row.Comments
        a.Archived = 1
        a.NonShelterAnimal = 0

    if row.disptype == "DOA":
        a.DeceasedDate = row.DispositDTL1
        a.PutToSleep = 0
        a.IsDOA = 1
        a.PTSReason = row.Comments
        a.Archived = 1
        a.NonShelterAnimal = 0

    if row.disptype == "Adoption" and str(row.CustUid) in ppo:
        o = ppo[row.CustUid]
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = row.DispositDTL1
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 1
        a.NonShelterAnimal = 0
        movements.append(m)

# At least one customer has used holds to store adoptions instead of dispositions
if HOLDS_AS_ADOPTIONS:
    for row in db.query("select * from hold").list():
        a = None
        if str(row.AnimalUid) in ppa:
            a = ppa[str(row.AnimalUid)]
        o = None
        if str(row.CustUid) in ppo:
            o = ppo[str(row.CustUid)]
        if a is None or o is None:
            asm.stderr("No animal/person combo: %s, %s" % (row.AnimalUid, row.CustUid))
            continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = row.Startts
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 1
        a.NonShelterAnimal = 0
        movements.append(m)

"""
# Medical - this info MAY be supplied by the medetail table, but it was blank
# in the MySQL database we converted this time.

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
"""

# Run back through the animals, if we have any that are still
# on shelter after 1 year, add an adoption to an unknown owner
asm.adopt_older_than(animals, movements, uo.ID, 365)

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

asm.stderr_summary(animals=animals, animalvaccinations=animalvaccinations, owners=owners, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

