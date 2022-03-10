#!/usr/bin/env python3

import asm, datetime, os, dbfread

"""
Import script for Shelterpro databases in DBF format

Requires my hack to dbfread to support VFP9 - 
copy parseC in FieldParser.py and rename it parseV, then remove
encoding so it's just a binary string that can be ignored.


Requires address.dbf, addrlink.dbf, animal.dbf, incident.dbf, license.dbf, note.dbf, person.dbf, shelter.dbf, vacc.dbf

Will also look in PATH/images/IMAGEKEY.[jpg|JPG] for animal photos if available.

29th December, 2016 - 2nd April 2020
"""

PATH = "/home/robin/tmp/asm3_import_data/shelterpro_mm2710"

START_ID = 100

INCIDENT_IMPORT = True
LICENCE_IMPORT = False
PICTURE_IMPORT = False
VACCINATION_IMPORT = True
NOTE_IMPORT = False
SHELTER_IMPORT = True 

SEPARATE_ADDRESS_TABLE = True
IMPORT_ANIMALS_WITH_NO_NAME = True

""" when faced with a field type it doesn't understand, dbfread can produce an error
    'Unknown field type xx'. This parser returns anything unrecognised as binary data """
class ExtraFieldParser(dbfread.FieldParser):
    def parse(self, field, data):
        try:
            return dbfread.FieldParser.parse(self, field, data)
        except ValueError:
            return data

def open_dbf(name):
    return asm.read_dbf("%s/%s.dbf" % (PATH, name))

def gettype(animaldes):
    spmap = {
        "DOG": 2,
        "CAT": 11
    }
    species = animaldes.split(" ")[0]
    if species in spmap:
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
logs = []
movements = []
animals = []
animalvaccinations = []
animalcontrol = []
animalcontrolanimals = []

ppa = {}
ppo = {}
ppi = {}
addresses = {}
addrlink = {}
notes = {}

asm.setid("adoption", START_ID)
asm.setid("animal", START_ID)
asm.setid("animalcontrol", START_ID)
asm.setid("log", START_ID)
asm.setid("owner", START_ID)

if VACCINATION_IMPORT: asm.setid("animalvaccination", START_ID)
if LICENCE_IMPORT: asm.setid("ownerlicence", START_ID)
if PICTURE_IMPORT: asm.setid("media", START_ID)
if PICTURE_IMPORT: asm.setid("dbfs", START_ID)

# Remove existing
print("\\set ON_ERROR_STOP\nBEGIN;")
print("DELETE FROM adoption WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM animal WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM owner WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID)
if INCIDENT_IMPORT: print("DELETE FROM animalcontrol WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID)
if VACCINATION_IMPORT: print("DELETE FROM animalvaccination WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID)
if LICENCE_IMPORT: print("DELETE FROM ownerlicence WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID)
if PICTURE_IMPORT: print("DELETE FROM media WHERE ID >= %d;" % START_ID)
if PICTURE_IMPORT: print("DELETE FROM dbfs WHERE ID >= %d;" % START_ID)

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
if SEPARATE_ADDRESS_TABLE:
    caddress = open_dbf("address")
    caddrlink = open_dbf("addrlink")
canimal = open_dbf("animal")
if LICENCE_IMPORT: clicense = open_dbf("license")
cperson = open_dbf("person")
if SHELTER_IMPORT: cshelter = open_dbf("shelter")
if VACCINATION_IMPORT: cvacc = open_dbf("vacc")
if INCIDENT_IMPORT: cincident = open_dbf("incident")
if NOTE_IMPORT: cnote = open_dbf("note")
if PICTURE_IMPORT: cimage = open_dbf("image")

# Addresses if we have a separate file
if SEPARATE_ADDRESS_TABLE:
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

# People
for row in cperson:
    o = asm.Owner()
    owners.append(o)
    personkey = 0
    # Sometimes called UNIQUE 
    if "PERSONKEY" in row: personkey = row["PERSONKEY"]
    elif "UNIQUE" in row: personkey = row["UNIQUE"]
    ppo[personkey] = o
    o.OwnerForeNames = asm.strip(row["FNAME"])
    o.OwnerSurname = asm.strip(row["LNAME"])
    o.OwnerName = o.OwnerTitle + " " + o.OwnerForeNames + " " + o.OwnerSurname
    # Find the address if it's in a separate table
    if SEPARATE_ADDRESS_TABLE:
        if personkey in addrlink:
            addrkey = addrlink[personkey]
            if addrkey in addresses:
                add = addresses[addrkey]
                o.OwnerAddress = add["address"]
                o.OwnerTown = add["city"]
                o.OwnerCounty = add["state"]
                o.OwnerPostcode = add["zip"]
    else:
        # Otherwise, address fields are in the person table
        o.OwnerAddress = row["ADDR1"].encode("ascii", "xmlcharrefreplace") + "\n" + row["ADDR2"].encode("ascii", "xmlcharrefreplace")
        o.OwnerTown = row["CITY"]
        o.OwnerCounty = row["STATE"]
        o.OwnerPostcode = row["POSTAL_ID"]
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
    if "FOSTERS" in row: o.IsFosterer = asm.cint(row["FOSTERS"])
    # o.ExcludeFromBulkEmail = asm.cint(row["MAILINGSAM"]) # Not sure this is correct

# Animals
for row in canimal:
    if not IMPORT_ANIMALS_WITH_NO_NAME and row["PETNAME"].strip() == "": continue
    a = asm.Animal()
    animals.append(a)
    ppa[row["ANIMALKEY"]] = a
    a.AnimalTypeID = gettype(row["ANIMLDES"])
    a.SpeciesID = asm.species_id_for_name(row["ANIMLDES"].split(" ")[0])
    a.AnimalName = asm.strip(row["PETNAME"]).title()
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    age = row["AGE"].split(" ")[0]
    added = asm.now()
    if "ADDEDDATET" in row and row["ADDEDDATET"] is not None: added = row["ADDEDDATET"]
    if "DOB" in row: a.DateOfBirth = row["DOB"]
    if a.DateOfBirth is None: a.DateOfBirth = getdateage(age, added)
    a.DateBroughtIn = added
    a.LastChangedDate = a.DateBroughtIn
    a.CreatedDate = a.DateBroughtIn
    a.EntryReasonID = 4
    a.generateCode(gettypeletter(a.AnimalTypeID))
    a.ShortCode = row["ANIMALKEY"]
    a.Neutered = asm.cint(row["FIX"])
    a.Declawed = asm.cint(row["DECLAWED"])
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 1
    a.Sex = asm.getsex_mf(asm.strip(row["GENDER"]))
    a.Size = getsize(asm.strip(row["WEIGHT"]))
    a.BaseColourID = asm.colour_id_for_names(asm.strip(row["FURCOLR1"]), asm.strip(row["FURCOLR2"]))
    a.IdentichipNumber = asm.strip(row["MICROCHIP"])
    if a.IdentichipNumber != "": a.Identichipped = 1
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
    # If the row has an original owner
    if row["PERSOWNR"] in ppo:
        o = ppo[row["PERSOWNR"]]
        a.OriginalOwnerID = o.ID
    # Shelterpro records Deceased as Status == 2 as far as we can tell
    if row["STATUS"] == 2:
        a.DeceasedDate = a.DateBroughtIn
        a.PTSReasonID = 2 # Died

# Vaccinations
if VACCINATION_IMPORT:
    for row in cvacc:
        if not row["ANIMALKEY"] in ppa: continue
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
        av.DateExpires = row["VACCEXPIRA"]
        av.Manufacturer = row["VACCMANUFA"]
        av.BatchNumber = row["VACCSERIAL"]
        av.Comments = "Name: %s, Issue: %s" % (row["VACCDRUGNA"], row["VACCISSUED"])


# Run through the shelter file and create any movements/euthanisation info
if SHELTER_IMPORT:
    for row in cshelter:
        a = None
        if row["ANIMALKEY"] in ppa:
            a = ppa[row["ANIMALKEY"]]
            arivdate = row["ARIVDATE"]
            a.ShortCode = asm.strip(row["ANIMALKEY"])
            a.ShelterLocationUnit = asm.strip(row["KENNEL"])
            a.NonShelterAnimal = 0
            if arivdate is not None:
                a.DateBroughtIn = arivdate
                a.LastChangedDate = a.DateBroughtIn
                a.CreatedDate = a.DateBroughtIn
                a.generateCode(gettypeletter(a.AnimalTypeID))
                a.ShortCode = asm.strip(row["ANIMALKEY"])
        else:
            # Couldn't find an animal record, bail
            continue

        o = None
        if row["OWNERATDIS"] in ppo:
            o = ppo[row["OWNERATDIS"]]

        dispmeth = asm.strip(row["DISPMETH"])
        dispdate = row["DISPDATE"]

        # Apply other fields
        if row["ARIVREAS"] == "QUARANTINE":
            a.IsQuarantine = 1

        elif row["ARIVREAS"] == "STRAY":
            if a.AnimalTypeID == 2: a.AnimalTypeID = 10
            if a.AnimalTypeID == 11: a.AnimalTypeID = 12
            a.EntryReasonID = 7

        # Adoptions
        if dispmeth == "ADOPTED":
            if a is None or o is None: continue
            m = asm.Movement()
            m.AnimalID = a.ID
            m.OwnerID = o.ID
            m.MovementType = 1
            m.MovementDate = dispdate
            a.Archived = 1
            a.ActiveMovementID = m.ID
            a.ActiveMovementDate = m.MovementDate
            a.ActiveMovementType = 1
            movements.append(m)

        # Reclaims
        elif dispmeth == "RETURN TO OWNER":
            if a is None or o is None: continue
            m = asm.Movement()
            m.AnimalID = a.ID
            m.OwnerID = o.ID
            m.MovementType = 5
            m.MovementDate = dispdate
            a.Archived = 1
            a.ActiveMovementID = m.ID
            a.ActiveMovementDate = m.MovementDate
            a.ActiveMovementType = 5
            movements.append(m)

        # Released or Other
        elif dispmeth == "RELEASED" or dispmeth == "OTHER":
            if a is None or o is None: continue
            m = asm.Movement()
            m.AnimalID = a.ID
            m.OwnerID = 0
            m.MovementType = 7
            m.MovementDate = dispdate
            m.Comments = dispmeth
            a.Archived = 1
            a.ActiveMovementDate = m.MovementDate
            a.ActiveMovementID = m.ID
            a.ActiveMovementType = 7
            movements.append(m)

        # Holding
        elif dispmeth == "" and row["ANIMSTAT"] == "HOLDING":
            a.IsHold = 1
            a.Archived = 0

        # Deceased
        elif dispmeth == "DECEASED":
            a.DeceasedDate = dispdate
            a.PTSReasonID = 2 # Died
            a.Archived = 1

        # Euthanized
        elif dispmeth == "EUTHANIZED":
            a.DeceasedDate = dispdate
            a.PutToSleep = 1
            a.PTSReasonID = 4 # Sick/Injured
            a.Archived = 1

        # If the outcome is blank, it's on the shelter
        elif dispmeth == "":
            a.Archived = 0

        # It's the name of an organisation that received the animal
        else:
            if a is None: continue
            m = asm.Movement()
            m.AnimalID = a.ID
            m.OwnerID = to.ID
            m.MovementType = 3
            m.MovementDate = dispdate
            m.Comments = dispmeth
            a.Archived = 1
            a.ActiveMovementID = m.ID
            a.ActiveMovementType = 3
            movements.append(m)

if LICENCE_IMPORT:
    for row in clicense:
        a = None
        if row["ANIMALKEY"] in ppa:
            a = ppa[row["ANIMALKEY"]]
        o = None
        if row["LICENSEOWN"] in ppo:
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

if PICTURE_IMPORT:
    for row in cimage:
        a = None
        if not row["ANIMALKEY"] in ppa:
            continue
        a = ppa[row["ANIMALKEY"]]
        imdata = None
        if os.path.exists(PATH + "/images/%s.jpg" % row["IMAGEKEY"]):
            f = open(PATH + "/images/%s.jpg" % row["IMAGEKEY"], "rb")
            imdata = f.read()
            f.close()
        if imdata is not None:
            asm.animal_image(a.ID, imdata)

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
        if row["CITIZENMAK"] in ppo:
            ac.CallerID = ppo[row["CITIZENMAK"]].ID
        if row["OWNERATORI"] in ppo:
            ac.OwnerID = ppo[row["OWNERATORI"]].ID
        ac.IncidentCompletedID = 2
        if row["FINALOUTCO"] == "ANIMAL PICKED UP":
            ac.IncidentCompletedID = 2
        elif row["FINALOUTCO"] == "OTHER":
            ac.IncidentCompletedID = 6 # Does not exist in default data
        ac.IncidentTypeID = 1
        incidentkey = 0
        if "INCIDENTKE" in row: incidentkey = row["INCIDENTKE"]
        elif "KEY" in row: incidentkey = row["KEY"]
        comments = "case: %s\n" % incidentkey
        comments += "outcome: %s\n" % asm.strip(row["FINALOUTCO"])
        comments += "precinct: %s\n" % asm.strip(row["PRECINCT"])
        ac.CallNotes = comments
        ac.Sex = 2
        if "ANIMALKEY" in row:
            if row["ANIMALKEY"] in ppa:
                a = ppa[row["ANIMALKEY"]]
                animalcontrolanimals.append("INSERT INTO animalcontrolanimal (AnimalControlID, AnimalID) VALUES (%s, %s);" % (ac.ID, a.ID))

# Notes as log entries
if NOTE_IMPORT:
    for row in cnote:
        eventtype = row["EVENTTYPE"]
        eventkey = row["EVENTKEY"]
        notedate = row["NOTEDATE"]
        memo = row["NOTEMEMO"]
        if eventtype in [ 1, 3 ]: # animal/intake or case notes
            if not eventkey in ppa: continue
            linkid = ppa[eventkey].ID
            ppa[eventkey].HiddenAnimalDetails += "\n" + memo
            l = asm.Log()
            logs.append(l)
            l.LogTypeID = 3
            l.LinkID = linkid
            l.LinkType = 0
            l.Date = notedate
            if l.Date is None:
                l.Date = asm.now()
            l.Comments = memo
        elif eventtype in [ 2, 5, 10 ]: # person, case and incident notes
            if not eventkey in ppi: continue
            linkid = ppi[eventkey].ID
            ppi[eventkey].CallNotes += "\n" + memo
            l = asm.Log()
            logs.append(l)
            l.LogTypeID = 3
            l.LinkID = linkid
            l.LinkType = 6
            l.Date = notedate
            if l.Date is None:
                l.Date = asm.now()
            l.Comments = memo

# Run back through the animals, if we have any that are still
# on shelter after 2 years, add an adoption to an unknown owner
#asm.adopt_older_than(animals, movements, uo.ID, 365*2)

# Now that everything else is done, output stored records
for a in animals:
    print(a)
for av in animalvaccinations:
    print(av)
for o in owners:
    print(o)
for l in logs:
    print(l)
for m in movements:
    print(m)
for ol in ownerlicences:
    print(ol)
for ac in animalcontrol:
    print(ac)
for aca in animalcontrolanimals:
    print(aca)

asm.stderr_summary(animals=animals, animalvaccinations=animalvaccinations, logs=logs, owners=owners, movements=movements, ownerlicences=ownerlicences, animalcontrol=animalcontrol)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")

