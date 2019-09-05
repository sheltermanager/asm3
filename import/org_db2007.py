#!/usr/bin/python

import asm

"""
Import script for licence/incidents for db2007

25th May, 2019
"""

def getdate(d):
    if d.find("?") != -1: return None
    return asm.getdate_guess(d)

PATH = "/home/robin/tmp/asm3_import_data/db2007_csv/"

# --- START OF CONVERSION ---

animals = []
movements = []
owners = []
ownerlicences = []
ppo = {}

asm.setid("adoption", 100)
asm.setid("animal", 100)
asm.setid("owner", 100)
asm.setid("ownerlicence", 100)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM adoption WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM owner WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM ownerlicence WHERE ID >= 100 AND CreatedBy = 'conversion';"

# Create an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname

def process_licence(d, dt):
    if d["Owner"] in ppo:
        o = ppo[d["Owner"]]
    else:
        o = asm.Owner()
        owners.append(o)
        name = d["Owner"]
        firstname = ""
        lastname = name
        if name.find(",") != -1:
            firstname, lastname = name.split(",", 1)
        ppo[name] = o
        o.OwnerForeNames = firstname
        o.OwnerSurname = lastname
        o.OwnerName = name
        o.OwnerAddress = d["Address"]
        o.OwnerTown = "Burnsville"
        o.OwnerCounty = "MN"
        o.HomeTelephone = d["Phone"]
    ol = asm.OwnerLicence()
    ol.LicenceType = 1
    ol.OwnerID = o.ID
    ol.LicenceNumber = "%s/%s" % (ol.ID, d["Lic. #"])
    ol.IssueDate = dt
    ol.ExpiryDate = asm.add_days(dt, 365)
    ol.Comments = "Name: %s\nSex: %s\nBreed: %s\nColor: %s" % (d["Pet Name"], d["Sex"], d["Breed"], d["Color"])
    ownerlicences.append(ol)

def process_impound(d, dt):
    a = asm.Animal()
    animals.append(a)
    a.EntryReasonID = 7 # Stray
    if d["Species"].lower() == "cat":
        a.AnimalTypeID = 12 # Stray Cat
    elif d["Species"].lower() == "dog":
        a.AnimalTypeID = 10 # Stray Dog
    else:
        a.AnimalTypeID = 40 # Misc
    a.SpeciesID = asm.species_id_for_name(d["Species"])
    a.AnimalName = d["Animal's Name"].replace("\n", " ")
    if a.AnimalName == "?" or a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    releasedate = getdate(d["Date of Release"])
    intakedate = getdate(d["Date of P/U"])
    if intakedate is None and releasedate is not None: intakedate = releasedate
    if intakedate is None: intakedate = dt
    a.DateBroughtIn = intakedate
    a.DateOfBirth = asm.subtract_days(a.DateBroughtIn, 365)
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    a.generateCode()
    a.Sex = asm.getsex_mf(d["Sex-Altered?"])
    a.Size = 2
    a.Neutered = asm.iif(d["Sex-Altered?"].lower() == "mn" or d["Sex-Altered?"].lower() == "fs", 1, 0)
    a.IdentichipNumber = d["Microchip"]
    if a.IdentichipNumber != "no chip found" and a.IdentichipNumber != "Unable to scan" and a.IdentichipNumber != "no" and a.IdentichipNumber != "":
        a.Identichipped = 1
    asm.breed_ids(a, d["Breed"], default=442) 
    if d["Breed"].lower().find("mix") != -1 or d["Breed"].find("X") != -1:
        a.CrossBreed = 1
        a.Breed2ID = 442
    a.HiddenDetails = "Breed: %s\nColor: %s\nCollar: %s\nTags: %s\nMicrochip: %s\n" % ( d["Breed"], d["Color"], d["Collar"], d["Tags"], d["Microchip"])
    a.Comments = d["Comments"]
    # Now create the owner
    if d["Owner's Name"] != "n/a" and d["Owner's Name"] != "" and d["Owner's Name"] != "?" and d["Owner's Name"] != "Went to Rescue" and d["Owner's Name"] != "unknown" and d["Address"] != "" and d["Address"] != "n/a":
        o = asm.Owner()
        owners.append(o)
        name = d["Owner's Name"]
        lastname = name
        firstname = ""
        if name.find(" ") != -1:
            firstname, lastname = name.split(" ", 1)
        ppo[name] = o
        o.OwnerForeNames = firstname
        o.OwnerSurname = lastname
        o.OwnerName = "%s, %s" % (lastname, firstname)
        o.OwnerAddress = d["Address"]
        o.OwnerTown = "Burnsville"
        o.OwnerCounty = "MN"
        o.HomeTelephone = d["Phone #"]
        # Reclaim if there's a date
        if releasedate is not None:
            m = asm.Movement()
            m.AnimalID = a.ID
            m.OwnerID = o.ID
            m.MovementType = 5
            m.MovementDate = releasedate
            a.Archived = 1
            a.ActiveMovementID = m.ID
            a.ActiveMovementType = 5
            a.LastChangedDate = m.MovementDate
            movements.append(m)
    # Was the animal euthanised?
    if "Euthanized" in d and d["Euthanized"] == "1":
        a.DeceasedDate = releasedate or intakedate
        a.PutToSleep = 1
        a.PTSReasonID = 4
        a.PTSReason = d["If Euthanized, Why?"]
        a.Archived = 1
    # Is this animal still on shelter? If so, we need to get it off with a fake reclaim
    if a.Archived == 0:
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = uo.ID
        m.MovementType = 5
        m.MovementDate = releasedate or intakedate
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 5
        a.LastChangedDate = m.MovementDate
        movements.append(m)

# Process licence files
LICENCE_FILES = [ "20082009", "20102011", "20122013", "20142015", "2016", "2018", "2019" ]
for s in LICENCE_FILES:
    fname = PATH + s + ".csv"
    fdate = asm.getdate_yyyymmdd("%s/01/01" % s[:4])
    asm.stderr("%s / %s" % (fname, fdate))
    for d in asm.csv_to_list(fname):
        process_licence(d, fdate)

# Process impound files
IMPOUND_FILES = [ "impound2017", "impound2018", "impound2019" ]
for s in IMPOUND_FILES:
    fname = PATH + s + ".csv"
    fdate = asm.getdate_yyyymmdd("%s/01/01" % s[7:])
    asm.stderr("%s / %s" % (fname, fdate))
    for d in asm.csv_to_list(fname):
        process_impound(d, fdate)

# Now that everything else is done, output stored records
for a in animals:
    print a
for m in movements:
    print m
for o in owners:
    print o
for ol in ownerlicences:
    print ol

asm.stderr_summary(animals=animals, owners=owners, ownerlicences=ownerlicences, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

