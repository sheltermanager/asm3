#!/usr/bin/python

import asm, datetime, sys, os

"""
Import script for Shelterpro databases exported as CSV
(requires shelter.csv, animal.csv, person.csv, address.csv, addrlink.csv, license.csv, vacc.csv)

Will also look in PATH/images/ANIMALKEY.[jpg|JPG] for animal photos if available.

6th Oct, 2014 - 8th April, 2015
"""

PATH = "data/shelterpro_porter"

def gettype(animaldes):
    spmap = {
        "DOG": 2,
        "CAT": 11
    }
    species = animaldes.split(" ")[0]
    if spmap.has_key(species):
        return spmap[species]
    else:
        return 2

def gettypeletter(aid):
    tmap = {
        2: "D",
        11: "U"
    }
    return tmap[aid]

def getsize(size):
    if size == "VERY":
        return 0
    elif size == "LARGE":
        return 1
    elif size == "MEDIUM":
        return 2
    else:
        return 3

def getdateage(age, arrivaldate):
    """ Returns a date adjusted for age. Age can be one of
        ADULT, PUPPY, KITTEN, SENIOR """
    d = asm.getdate_yyyymmdd(arrivaldate)
    if d == None: d = datetime.datetime.today()
    if age == "ADULT":
        d = d - datetime.timedelta(days = 365 * 2)
    if age == "SENIOR":
        d = d - datetime.timedelta(days = 365 * 7)
    if age == "KITTEN":
        d = d - datetime.timedelta(days = 60)
    if age == "PUPPY":
        d = d - datetime.timedelta(days = 60)
    return d

owners = []
ownerlicences = []
movements = []
animals = []
animalvaccinations = []

ppa = {}
ppo = {}
addresses = {}
addrlink = {}

asm.setid("animal", 100)
asm.setid("animalvaccination", 100)
asm.setid("owner", 100)
asm.setid("ownerlicence", 100)
asm.setid("adoption", 100)
asm.setid("media", 100)
asm.setid("dbfs", 300)

# Remove existing
print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= 100;"
print "DELETE FROM animalvaccination WHERE ID >= 100;"
print "DELETE FROM owner WHERE ID >= 100;"
print "DELETE FROM ownerlicence WHERE ID >= 100;"
print "DELETE FROM adoption WHERE ID >= 100;"
print "DELETE FROM media WHERE ID >= 100;"
print "DELETE FROM dbfs WHERE ID >= 300;"

# Create a transfer owner
o = asm.Owner()
owners.append(o)
o.OwnerSurname = "Other Shelter"
o.OwnerName = o.OwnerSurname

# Load up data files
caddress = asm.csv_to_list("%s/address.csv" % PATH)
caddrlink = asm.csv_to_list("%s/addrlink.csv" % PATH)
canimal = asm.csv_to_list("%s/animal.csv" % PATH)
clicense = asm.csv_to_list("%s/license.csv" % PATH)
cperson = asm.csv_to_list("%s/person.csv" % PATH)
cshelter = asm.csv_to_list("%s/shelter.csv" % PATH)
cvacc = asm.csv_to_list("%s/vacc.csv" % PATH)

# Start with animals
for row in canimal:
    a = asm.Animal()
    animals.append(a)
    ppa[row["ANIMALKEY"]] = a
    a.AnimalTypeID = gettype(row["ANIMLDES"])
    a.SpeciesID = asm.species_id_for_name(row["ANIMLDES"].split(" ")[0])
    a.AnimalName = row["PETNAME"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    age = row["AGE"].split(" ")[0]
    a.DateOfBirth = getdateage(age, row["ADDEDDATET"])
    a.DateBroughtIn = asm.getdate_yyyymmdd(row["ADDEDDATET"])
    if a.DateBroughtIn is None:
        sys.stderr.write("Bad datebroughtin: '%s'\n" % row["ADDEDDATET"])
        a.DateBroughtIn = datetime.datetime.today()    
    a.EntryReasonID = 4
    a.generateCode(gettypeletter(a.AnimalTypeID))
    a.Neutered = asm.cint(row["FIX"])
    a.Declawed = asm.cint(row["DECLAWED"])
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 1
    a.Sex = asm.getsex_mf(asm.fw(row["GENDER"]))
    a.Size = getsize(asm.fw(row["WEIGHT"]))
    a.BaseColourID = asm.colour_id_for_names(asm.fw(row["FURCOLR1"]), asm.fw(row["FURCOLR2"]))
    a.IdentichipNumber = row["MICROCHIP"]
    comments = "Original breed: " + row["BREED1"] + "/" + row["CROSSBREED"] + ", age: " + age
    comments += ",Color: " + asm.fw(row["FURCOLR1"]) + "/" + asm.fw(row["FURCOLR2"])
    comments += ", Coat: " + row["COAT"]
    comments += ", Collar: " + row["COLLRTYP"]
    a.BreedID = asm.breed_id_for_name(row["BREED1"])
    a.Breed2ID = a.BreedID
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    if row["PUREBRED"] == "0":
        a.Breed2ID = asm.breed_id_for_name(row["CROSSBREED"])
        if a.Breed2ID == 1: a.Breed2ID = 442
        a.BreedName = "%s / %s" % ( asm.breed_name_for_id(a.BreedID), asm.breed_name_for_id(a.Breed2ID) )
    a.HiddenAnimalDetails = comments
    a.Archived = 1
    # Does this animal have an image? If so, add media/dbfs entries for it
    imdata = None
    if os.path.exists(PATH + "/images/%s.jpg" % row["ANIMALKEY"]):
        f = open(PATH + "/images/%s.jpg" % row["ANIMALKEY"], "rb")
        imdata = f.read()
        f.close()
    elif os.path.exists(PATH + "/images/%s.JPG" % row["ANIMALKEY"]):
        f = open(PATH + "/images/%s.JPG" % row["ANIMALKEY"], "rb")
        imdata = f.read()
        f.close()
    if imdata is not None:
        asm.animal_image(a.ID, imdata)

# Vaccinations
for row in cvacc:
    if not ppa.has_key(row["ANIMALKEY"]): continue
    a = ppa[row["ANIMALKEY"]]
    # Each row contains a vaccination
    av = asm.AnimalVaccination()
    animalvaccinations.append(av)
    vaccdate = asm.getdate_yyyymmdd(row["VACCEFFECT"])
    if vaccdate is None:
        vaccdate = a.DateBroughtIn
    av.AnimalID = a.ID
    av.VaccinationID = 8
    if row["VACCTYPE"].find("DHLPP") != -1: av.VaccinationID = 8
    if row["VACCTYPE"].find("BORDETELLA") != -1: av.VaccinationID = 6
    if row["VACCTYPE"].find("RABIES") != -1: av.VaccinationID = 4
    av.DateRequired = vaccdate
    av.DateOfVaccination = vaccdate
    av.Manufacturer = row["VACCMANUFA"]
    av.BatchNumber = row["VACCSERIAL"]
    av.Comments = "Name: %s, Issue: %s" % (row["VACCDRUGNA"], row["VACCISSUED"])

# Next, addresses
for row in caddress:
    addresses[row["ADDRESSKEY"]] = {
        "address": row["ADDRESSSTR"] + " " + row["ADDRESSST2"] + " " + row["ADDRESSST3"],
        "city": row["ADDRESSCIT"],
        "state": row["ADDRESSSTA"],
        "zip": row["ADDRESSPOS"]
    }

# The link between addresses and people
for row in caddrlink:
    addrlink[row["EVENTKEY"]] = row["ADDRLINKAD"]

# Now do people
for row in cperson:
    o = asm.Owner()
    owners.append(o)
    ppo[row["PERSONKEY"]] = o
    o.OwnerForeNames = asm.fw(row["FNAME"])
    o.OwnerSurname = row["LNAME"]
    o.OwnerName = o.OwnerTitle + " " + o.OwnerForeNames + " " + o.OwnerSurname
    # Find the address
    if addrlink.has_key(row["PERSONKEY"]):
        addrkey = addrlink[row["PERSONKEY"]]
        if addresses.has_key(addrkey):
            add = addresses[addrkey]
            o.OwnerAddress = add["address"]
            o.OwnerTown = add["city"]
            o.OwnerCounty = add["state"]
            o.OwnerPostcode = add["zip"]
    o.EmailAddress = row["EMAIL"]
    o.HomeTelephone = row["HOME_PH"]
    o.WorkTelephone = row["WORK_PH"]
    o.MobileTelephone = row["THIRD_PH"]
    o.IsACO = asm.cint(row["ACO_IND"])
    o.IsStaff = asm.cint(row["STAFF_IND"])
    o.IsVolunteer = asm.cint(row["VOL_IND"])
    o.IsDonor = asm.cint(row["DONOR_IND"])
    o.IsMember = asm.cint(row["MEMBER_IND"])
    o.IsBanned = asm.cint(row["NOADOPT"] == "T" and "1" or "0")
    o.IsFosterer = asm.cint(row["FOSTERS"])
    o.ExcludeFromBulkEmail = asm.cint(row["MAILINGSAM"])


# Run through the shelter file and create any movements/euthanisation info
for row in cshelter:
    a = None
    if ppa.has_key(row["ANIMALKEY"]):
        a = ppa[row["ANIMALKEY"]]
        arivdate = asm.getdate_yyyymmdd(row["ARIVDATE"])
        a.ShortCode = asm.fw(row["FIELDCARD"])
        a.ShelterLocationUnit = asm.fw(row["KENNEL"])
        if arivdate is not None:
            a.DateBroughtIn = arivdate
            a.generateCode(gettypeletter(a.AnimalTypeID))
            a.ShortCode = asm.fw(row["FIELDCARD"])
    o = None
    if ppo.has_key(row["OWNERATDIS"]):
        o = ppo[row["OWNERATDIS"]]

    # Apply other fields
    if row["ARIVREAS"] == "QUARANTINE":
        a.IsQuarantine = 1

    elif row["ARIVREAS"] == "STRAY":
        if a.AnimalTypeID == 2: a.AnimalTypeID == 10
        if a.AnimalTypeID == 11: a.AnimalTypeID == 12
        a.EntryReasonID = 7

    # Adoptions
    if row["DISPMETH"] == "ADOPTED":
        if a is None or o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = asm.getdate_yyyymmdd(row["DISPDATE"])
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 1
        movements.append(m)

    # Reclaims
    elif row["DISPMETH"] == "RETURN TO OWNER":
        if a is None or o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 5
        m.MovementDate = asm.getdate_yyyymmdd(row["DISPDATE"])
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 5
        movements.append(m)

    # Released or Other
    elif row["DISPMETH"].startswith("RELEASED") or row["DISPMETH"] == "OTHER":
        if a is None or o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = 0
        m.MovementType = 7
        m.MovementDate = asm.getdate_yyyymmdd(row["DISPDATE"])
        m.Comments = row["DISPMETH"]
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 7
        movements.append(m)

    # Holding
    elif row["DISPMETH"] == "" and row["ANIMSTAT"] == "HOLDING":
        a.IsHold = 1
        a.Archived = 0

    # Deceased
    elif row["DISPMETH"] == "DECEASED":
        a.DeceasedDate = asm.getdate_yyyymmdd(row["DISPDATE"])
        a.Archived = 1

    # Euthanized
    elif row["DISPMETH"] == "EUTHANIZED":
        a.DeceasedDate = asm.getdate_yyyymmdd(row["DISPDATE"])
        a.PutToSleep = 1
        a.Archived = 1

    # If the outcome is blank, it's on the shelter
    elif row["DISPMETH"].strip() == "":
        a.Archived = 0

    # It's the name of an organisation that received the animal
    else:
        if a is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = 100
        m.MovementType = 3
        m.MovementDate = asm.getdate_yyyymmdd(row["DISPDATE"])
        m.Comments = row["DISPMETH"]
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 3
        movements.append(m)

for row in clicense:
    a = None
    if ppa.has_key(row["ANIMALKEY"]):
        a = ppa[row["ANIMALKEY"]]
    o = None
    if ppo.has_key(row["LICENSEOWN"]):
        o = ppo[row["LICENSEOWN"]]
    if a is not None and o is not None:
        if asm.getdate_yyyymmdd(row["LICENSEEFF"]) is None:
            continue
        ol = asm.OwnerLicence()
        ownerlicences.append(ol)
        ol.AnimalID = a.ID
        ol.OwnerID = o.ID
        ol.IssueDate = asm.getdate_yyyymmdd(row["LICENSEEFF"])
        ol.ExpiryDate = asm.getdate_yyyymmdd(row["LICENSEEXP"])
        ol.LicenceNumber = asm.fw(row["LICENSE"])
        ol.LicenceTypeID = 2 # Unaltered dog
        if row["LICENSEFIX"] == "1":
            ol.LicenceTypeID = 1 # Altered dog

# Now that everything else is done, output stored records
for a in animals:
    print a
for av in animalvaccinations:
    print av
for o in owners:
    print o
for m in movements:
    print m
for ol in ownerlicences:
    print ol

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

