#!/usr/bin/python

import asm, datetime, dbfread, os

"""
Import script for Shelterpro databases in DBF format

Requires my hack to dbfread to support VFP9 - 
copy parseC in FieldParser.py and rename it parseV, then remove
encoding so it's just a binary string that can be ignored.


Requires address.dbf, addrlink.dbf, animal.dbf, incident.dbf, license.dbf, note.dbf, person.dbf, shelter.dbf, vacc.dbf

Will also look in PATH/images/ANIMALKEY.[jpg|JPG] for animal photos if available.

29th December, 2016
"""

PATH = "data/shelterpro_ac0916"

START_ID = 2500

INCIDENT_IMPORT = False
LICENCE_IMPORT = True
PICTURE_IMPORT = False
VACCINATION_IMPORT = True

IMPORT_ANIMALS_WITH_NO_NAME = True

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
        10: "A",
        11: "U",
        12: "S"
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
    d = arrivaldate
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
animalcontrol = []

ppa = {}
ppo = {}
addresses = {}
addrlink = {}
notes = {}

asm.setid("adoption", START_ID)
asm.setid("animal", START_ID)
asm.setid("animalcontrol", START_ID)
asm.setid("owner", START_ID)

if VACCINATION_IMPORT: asm.setid("animalvaccination", START_ID)
if LICENCE_IMPORT: asm.setid("ownerlicence", START_ID)
if PICTURE_IMPORT: asm.setid("media", START_ID)
if PICTURE_IMPORT: asm.setid("dbfs", START_ID)

# Remove existing
print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM adoption WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM animal WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM owner WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID
if INCIDENT_IMPORT: print "DELETE FROM animalcontrol WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID
if VACCINATION_IMPORT: print "DELETE FROM animalvaccination WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID
if LICENCE_IMPORT: print "DELETE FROM ownerlicence WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID
if PICTURE_IMPORT: print "DELETE FROM media WHERE ID >= %d;" % START_ID
if PICTURE_IMPORT: print "DELETE FROM dbfs WHERE ID >= %d;" % START_ID

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
caddress = dbfread.DBF("%s/address.dbf" % PATH)
caddrlink = dbfread.DBF("%s/addrlink.dbf" % PATH)
canimal = dbfread.DBF("%s/animal.dbf" % PATH)
clicense = dbfread.DBF("%s/license.dbf" % PATH)
cperson = dbfread.DBF("%s/person.dbf" % PATH)
cshelter = dbfread.DBF("%s/shelter.dbf" % PATH)
cvacc = dbfread.DBF("%s/vacc.dbf" % PATH)
cincident = dbfread.DBF("%s/incident.dbf" % PATH)
#cnote = dbfread.DBF("%s/note.dbf" % PATH)

# Start with animals
for row in canimal:
    if not IMPORT_ANIMALS_WITH_NO_NAME and row["PETNAME"].strip() == "": continue
    a = asm.Animal()
    animals.append(a)
    ppa[row["ANIMALKEY"]] = a
    a.AnimalTypeID = gettype(row["ANIMLDES"])
    a.SpeciesID = asm.species_id_for_name(row["ANIMLDES"].split(" ")[0])
    a.AnimalName = asm.strip(row["PETNAME"])
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    age = row["AGE"].split(" ")[0]
    # TODO: DOB is not always present in these things
    a.DateOfBirth = row["DOB"]
    if a.DateOfBirth is None: a.DateOfBirth = getdateage(age, row["ADDEDDATET"])
    a.DateBroughtIn = row["ADDEDDATET"]
    if a.DateBroughtIn is None:
        asm.stderr("Bad datebroughtin: '%s'" % row["ADDEDDATET"])
        a.DateBroughtIn = datetime.datetime.today()    
    a.LastChangedDate = a.DateBroughtIn
    a.CreatedDate = a.DateBroughtIn
    a.EntryReasonID = 4
    a.generateCode(gettypeletter(a.AnimalTypeID))
    a.Neutered = asm.cint(row["FIX"])
    a.Declawed = asm.cint(row["DECLAWED"])
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 1
    a.Sex = asm.getsex_mf(asm.strip(row["GENDER"]))
    a.Size = getsize(asm.strip(row["WEIGHT"]))
    a.BaseColourID = asm.colour_id_for_names(asm.strip(row["FURCOLR1"]), asm.strip(row["FURCOLR2"]))
    a.IdentichipNumber = asm.strip(row["MICROCHIP"])
    comments = "Original breed: " + asm.strip(row["BREED1"]) + "/" + asm.strip(row["CROSSBREED"]) + ", age: " + age
    comments += ",Color: " + asm.strip(row["FURCOLR1"]) + "/" + asm.strip(row["FURCOLR2"])
    comments += ", Coat: " + asm.strip(row["COAT"])
    comments += ", Collar: " + asm.strip(row["COLLRTYP"])
    a.BreedID = asm.breed_id_for_name(asm.strip(row["BREED1"]))
    a.Breed2ID = a.BreedID
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    if row["PUREBRED"] == "0":
        a.Breed2ID = asm.breed_id_for_name(asm.strip(row["CROSSBREED"]))
        if a.Breed2ID == 1: a.Breed2ID = 442
        a.BreedName = "%s / %s" % ( asm.breed_name_for_id(a.BreedID), asm.breed_name_for_id(a.Breed2ID) )
    a.HiddenAnimalDetails = comments
    # Make everything non-shelter until it's in the shelter file
    a.NonShelterAnimal = 1
    a.Archived = 1
    # Shelterpro records Deceased as Status == 2 as far as we can tell
    if row["STATUS"] == 2:
        a.DeceasedDate = a.DateBroughtIn
        a.PTSReasonID = 2 # Died
    # Does this animal have an image? If so, add media/dbfs entries for it
    if PICTURE_IMPORT:
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
if VACCINATION_IMPORT:
    for row in cvacc:
        if not ppa.has_key(row["ANIMALKEY"]): continue
        a = ppa[row["ANIMALKEY"]]
        # Each row contains a vaccination
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        vaccdate = row["VACCEFFECT"]
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
        "address": asm.strip(row["ADDRESSSTR"]) + " " + asm.strip(row["ADDRESSST2"]) + " " + asm.strip(row["ADDRESSST3"]),
        "city": asm.strip(row["ADDRESSCIT"]),
        "state": asm.strip(row["ADDRESSSTA"]),
        "zip": asm.strip(row["ADDRESSPOS"])
    }

# The link between addresses and people
for row in caddrlink:
    addrlink[row["EVENTKEY"]] = row["ADDRLINKAD"]

# Now do people
for row in cperson:
    o = asm.Owner()
    owners.append(o)
    ppo[row["PERSONKEY"]] = o
    o.OwnerForeNames = asm.strip(row["FNAME"])
    o.OwnerSurname = asm.strip(row["LNAME"])
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
    if asm.strip(row["EMAIL"]) != "(": o.EmailAddress = asm.strip(row["EMAIL"])
    if row["HOME_PH"] != 0: o.HomeTelephone = asm.strip(row["HOME_PH"])
    if row["WORK_PH"] != 0: o.WorkTelephone = asm.strip(row["WORK_PH"])
    if row["THIRD_PH"] != 0: o.MobileTelephone = asm.strip(row["THIRD_PH"])
    o.IsACO = asm.cint(row["ACO_IND"])
    o.IsStaff = asm.cint(row["STAFF_IND"])
    o.IsVolunteer = asm.cint(row["VOL_IND"])
    o.IsDonor = asm.cint(row["DONOR_IND"])
    o.IsMember = asm.cint(row["MEMBER_IND"])
    o.IsBanned = asm.cint(row["NOADOPT"] == "T" and "1" or "0")
    o.IsFosterer = asm.cint(row["FOSTERS"])
    # o.ExcludeFromBulkEmail = asm.cint(row["MAILINGSAM"]) # Not sure this is correct


# Run through the shelter file and create any movements/euthanisation info
for row in cshelter:
    a = None
    if ppa.has_key(row["ANIMALKEY"]):
        a = ppa[row["ANIMALKEY"]]
        arivdate = row["ARIVDATE"]
        a.ShortCode = asm.strip(row["FIELDCARD"])
        a.ShelterLocationUnit = asm.strip(row["KENNEL"])
        a.NonShelterAnimal = 0
        if arivdate is not None:
            a.DateBroughtIn = arivdate
            a.LastChangedDate = a.DateBroughtIn
            a.CreatedDate = a.DateBroughtIn
            a.generateCode(gettypeletter(a.AnimalTypeID))
            a.ShortCode = asm.strip(row["FIELDCARD"])
    else:
        # Couldn't find an animal record, bail
        continue

    o = None
    if ppo.has_key(row["OWNERATDIS"]):
        o = ppo[row["OWNERATDIS"]]

    # Apply other fields
    if row["ARIVREAS"] == "QUARANTINE":
        a.IsQuarantine = 1

    elif row["ARIVREAS"] == "STRAY":
        if a.AnimalTypeID == 2: a.AnimalTypeID = 10
        if a.AnimalTypeID == 11: a.AnimalTypeID = 12
        a.EntryReasonID = 7

    # Adoptions
    if row["DISPMETH"] == "ADOPTED":
        if a is None or o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = row["DISPDATE"]
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 1
        movements.append(m)

    # Reclaims
    elif row["DISPMETH"] == "RETURN TO OWNER":
        if a is None or o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 5
        m.MovementDate = row["DISPDATE"]
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 5
        movements.append(m)

    # Released or Other
    elif row["DISPMETH"].startswith("RELEASED") or row["DISPMETH"] == "OTHER":
        if a is None or o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = 0
        m.MovementType = 7
        m.MovementDate = row["DISPDATE"]
        m.Comments = row["DISPMETH"]
        a.Archived = 1
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 7
        movements.append(m)

    # Holding
    elif row["DISPMETH"] == "" and row["ANIMSTAT"] == "HOLDING":
        a.IsHold = 1
        a.Archived = 0

    # Deceased
    elif row["DISPMETH"] == "DECEASED":
        a.DeceasedDate = row["DISPDATE"]
        a.PTSReasonID = 2 # Died
        a.Archived = 1

    # Euthanized
    elif row["DISPMETH"] == "EUTHANIZED":
        a.DeceasedDate = row["DISPDATE"]
        a.PutToSleep = 1
        a.PTSReasonID = 4 # Sick/Injured
        a.Archived = 1

    # If the outcome is blank, it's on the shelter
    elif row["DISPMETH"].strip() == "":
        a.Archived = 0

    # It's the name of an organisation that received the animal
    else:
        if a is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = to.ID
        m.MovementType = 3
        m.MovementDate = row["DISPDATE"]
        m.Comments = row["DISPMETH"]
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 3
        movements.append(m)

if LICENCE_IMPORT:
    for row in clicense:
        a = None
        if ppa.has_key(row["ANIMALKEY"]):
            a = ppa[row["ANIMALKEY"]]
        o = None
        if ppo.has_key(row["LICENSEOWN"]):
            o = ppo[row["LICENSEOWN"]]
        if a is not None and o is not None:
            if row["LICENSEEFF"] is None:
                continue
            ol = asm.OwnerLicence()
            ownerlicences.append(ol)
            ol.AnimalID = a.ID
            ol.OwnerID = o.ID
            ol.IssueDate = row["LICENSEEFF"]
            ol.ExpiryDate = row["LICENSEEXP"]
            if ol.ExpiryDate is None: ol.ExpiryDate = ol.IssueDate
            ol.LicenceNumber = asm.strip(row["LICENSE"])
            ol.LicenceTypeID = 2 # Unaltered dog
            if a.Neutered == 1:
                ol.LicenceTypeID = 1 # Altered dog

# Incident notes
#for row in cnote:
#    if row["EVENTTYPE"] == 2:
#        notes[row["EVENTKEY"]] = row["NOTEMEMO"]

# Incidents
if INCIDENT_IMPORT:
    for row in cincident:
        ac = asm.AnimalControl()
        animalcontrol.append(ac)
        calldate = row["DATETIMEAS"]
        if calldate is None: calldate = row["DATETIMEOR"]
        if calldate is None: calldate = asm.now()
        ac.CallDateTime = calldate
        ac.IncidentDateTime = calldate
        ac.DispatchDateTime = calldate
        ac.CompletedDate = row["DATETIMEOU"]
        if ac.CompletedDate is None: ac.CompletedDate = calldate
        if ppo.has_key(row["CITIZENMAK"]):
            ac.CallerID = ppo[row["CITIZENMAK"]].ID
        if ppo.has_key(row["OWNERATORI"]):
            ac.OwnerID = ppo[row["OWNERATORI"]].ID
        ac.IncidentCompletedID = 2
        if row["FINALOUTCO"] == "ANIMAL PICKED UP":
            ac.IncidentCompletedID = 2
        elif row["FINALOUTCO"] == "OTHER":
            ac.IncidentCompletedID = 6 # Does not exist in default data
        ac.IncidentTypeID = 1
        comments = "outcome: %s\n" % row["FINALOUTCO"]
        comments += "precinct: %s\n" % row["PRECINCT"]
        if notes.has_key(row["INCIDENTKE"]):
            comments += notes[row["INCIDENTKE"]]
        ac.CallNotes = comments
        ac.Sex = 2

# Run back through the animals, if we have any that are still
# on shelter after 2 years, add an adoption to an unknown owner
for a in animals:
    if a.Archived == 0 and a.DateBroughtIn < asm.subtract_days(asm.now(), 365*2):
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
for ac in animalcontrol:
    print ac

asm.stderr_summary(animals=animals, animalvaccinations=animalvaccinations, owners=owners, movements=movements, ownerlicences=ownerlicences, animalcontrol=animalcontrol)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

