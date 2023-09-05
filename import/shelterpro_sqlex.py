#!/usr/bin/python3

import asm, datetime, sys, os

"""
Import script for Shelterpro databases exported from SQL Server to MDB and then CSV
this version differs from other shelterpro as some of the fieldnames are full length instead
of truncated at 8 chars as with the DBF variants

(requires shelter.csv, animal.csv, person.csv, address.csv, addrlink.csv, license.csv, vacc.csv)
(optional: license.csv, payments.csv, bite.csv, incident.csv, image.csv)

Will also look in PATH/images/ANIMALKEY.[jpg|JPG] for animal photos if IMAGE_FILE_IMPORT is set.

6th Oct, 2014 - 30th August, 2023
"""

"""
unpack.sh - put this in the folder with the MDB file:

#!/bin/sh
MDB=Database1.mdb
for t in `mdb-tables $MDB`; do
    mdb-export -b hex $MDB $t > $t.csv
done
"""

"""
These are just notes for where the last customer deleted some lookup values prior to the import.
Update some values to something sensible.
-- not found
UPDATE animalcontrol SET IncidentCompletedID = 29 WHERE IncidentCompletedID = 4;
-- bite
UPDATE animalcontrol SET IncidentTypeID = 35 WHERE IncidentTypeID = 5;
"""

PATH = "/home/robin/tmp/asm3_import_data/shelterpro_mg3031"

START_ID = 1000

BITE_IMPORT = True
INCIDENT_IMPORT = True
LICENCE_IMPORT = False
IMAGE_FILE_IMPORT = False
IMAGE_TABLE_IMPORT = False
PAYMENT_IMPORT = True
VACCINATION_IMPORT = True

IMPORT_ANIMALS_WITH_NO_NAME = True      # Some people like these filtered out. They'll come through with name (unknown)
FAKE_ADOPTION_ONSHELTER_DAYS = 0        # Animals on shelter longer than this many days will have a fake adoption, 0 to do nothing

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

def getdate(s):
    return asm.getdate_mmddyy(s)

cusers = None
def getuser(personkey):
    global cusers
    if cusers is None: cusers = asm.csv_to_list("%s/parmuser.csv" % PATH, uppercasekeys=True, strip=True)
    for row in cusers:
        if row["PERSONKEY"] == personkey:
            return "conversion/%s" % row["USERID"]
    return "conversion"

def setuserfields(row, o):
    """ If row contains shelterpro user fields, sets them on object o """
    if "ADDEDBYUSER" in row and row["ADDEDBYUSER"] != "": o.CreatedBy = getuser(row["ADDEDBYUSER"])
    if "ADDEDDATETIME" in row and row["ADDEDDATETIME"] != "": o.CreatedDate = getdate(row["ADDEDDATETIME"])
    if "LASTUSERTOSAVE" in row and row["LASTUSERTOSAVE"] != "": o.LastChangedBy = getuser(row["LASTUSERTOSAVE"])
    if "LASTSAVEDATETIME" in row and row["LASTSAVEDATETIME"] != "": o.LastChangedDate = getdate(row["LASTSAVEDATETIME"])

owners = []
ownerdonations = []
ownerlicences = []
logs = []
movements = []
animals = []
animalvaccinations = []
animalcontrol = []

ppa = {}
ppo = {}
ppoid = {}
ppi = {}
addresses = {}
addrlink = {}

asm.setid("adoption", START_ID)
asm.setid("animal", START_ID)
asm.setid("animalcontrol", START_ID)
asm.setid("owner", START_ID)
asm.setid("log", START_ID)

if VACCINATION_IMPORT: asm.setid("animalvaccination", START_ID)
if LICENCE_IMPORT: asm.setid("ownerlicence", START_ID)
if IMAGE_FILE_IMPORT or IMAGE_TABLE_IMPORT: asm.setid("media", START_ID)
if IMAGE_FILE_IMPORT or IMAGE_TABLE_IMPORT: asm.setid("dbfs", START_ID)
if PAYMENT_IMPORT: asm.setid("ownerdonation", START_ID)

# Remove existing
print("\\set ON_ERROR_STOP\nBEGIN TRANSACTION;")
print("DELETE FROM adoption WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM animal WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM log WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM owner WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID)
if INCIDENT_IMPORT: print("DELETE FROM animalcontrol WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID)
if VACCINATION_IMPORT: print("DELETE FROM animalvaccination WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID)
if LICENCE_IMPORT: print("DELETE FROM ownerlicence WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID)
if PAYMENT_IMPORT: print("DELETE FROM ownerdonation WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID)
if IMAGE_FILE_IMPORT or IMAGE_TABLE_IMPORT: print("DELETE FROM media WHERE ID >= %d;" % START_ID)
if IMAGE_FILE_IMPORT or IMAGE_TABLE_IMPORT: print("DELETE FROM dbfs WHERE ID >= %d;" % START_ID)

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

# Addresses
caddress = asm.csv_to_list("%s/address.csv" % PATH, uppercasekeys=True, strip=True)
caddrlink = asm.csv_to_list("%s/addrlink.csv" % PATH, uppercasekeys=True, strip=True)
for row in caddress:
    addresses[row["ADDRESSKEY"]] = {
        "address": "%s %s %s %s" % (row["ADDRESSSTREETNUMBER"], row["ADDRESSSTREETDIR"], row["ADDRESSSTREETNAME"], row["ADDRESSSTREETTYPE"]),
        "city": row["ADDRESSCITY"],
        "state": row["ADDRESSSTATE"],
        "zip": row["ADDRESSPOSTAL"]
    }

# The link between addresses and people
for row in caddrlink:
    addrlink[row["EVENTKEY"]] = row["ADDRLINKADDRESSKEY"]

# Now do people
cperson = asm.csv_to_list("%s/person.csv" % PATH, uppercasekeys=True, strip=True)
for row in cperson:
    o = asm.Owner()
    owners.append(o)
    ppo[row["PERSONKEY"]] = o
    ppoid[o.ID] = o
    o.OwnerForeNames = asm.strip(row["FNAME"]).title()
    o.OwnerSurname = asm.strip(row["LNAME"]).title()
    o.OwnerName = o.OwnerTitle + " " + o.OwnerForeNames + " " + o.OwnerSurname
    # Find the address
    if row["PERSONKEY"] in addrlink:
        addrkey = addrlink[row["PERSONKEY"]]
        if addrkey in addresses:
            add = addresses[addrkey]
            o.OwnerAddress = add["address"].replace("  ", " ").title()
            o.OwnerTown = add["city"].title()
            o.OwnerCounty = add["state"].upper()
            o.OwnerPostcode = add["zip"].upper()
    if asm.strip(row["EMAIL"]) != "(": o.EmailAddress = asm.strip(row["EMAIL"])
    if row["HOME_PH"] != "0": o.HomeTelephone = asm.strip(row["HOME_PH"])
    if row["WORK_PH"] != "0": o.WorkTelephone = asm.strip(row["WORK_PH"])
    if row["THIRD_PH"] != "0": o.MobileTelephone = asm.strip(row["THIRD_PH"])
    o.IsACO = asm.cint(row["ACO_IND"])
    o.IsStaff = asm.cint(row["STAFF_IND"])
    o.IsVolunteer = asm.cint(row["VOL_IND"])
    o.IsDonor = asm.cint(row["DONOR_IND"])
    o.IsMember = asm.cint(row["MEMBER_IND"])
    o.IsBanned = asm.cint(row["NOADOPT"] == "T" and "1" or "0")
    o.IsFosterer = asm.cint(row["FOSTERS"])
    o.IdentificationNumber = row["DRIV_LIC"]
    o.DateOfBirth = getdate(row["BIRTH"])
    # o.ExcludeFromBulkEmail = asm.cint(row["MAILINGSAM"]) # Not sure this is correct
    setuserfields(row, o)

if PAYMENT_IMPORT:
    cpayment = asm.csv_to_list("%s/payments.csv" % PATH, uppercasekeys=True, strip=True)
    for row in cpayment:
        if row["PAYMENTPRSN"] not in ppo: continue
        o = ppo[row["PAYMENTPRSN"]]
        od = asm.OwnerDonation()
        od.DonationTypeID = 1
        od.DonationPaymentID = 1 # Cash - Default
        if row["PAYMENTMETH"] == "CHECK":
            od.DonationPaymentID = 2 # Check
            od.ChequeNumber = row["PAYMENTREF"]
        elif row["PAYMENTCARDTYPE"] != "": 
            od.DonationPaymentID = 3 # Credit Card
        od.Date = getdate(row["PAYMENTDATE"])
        if od.Date is None: od.Date = asm.today()
        od.OwnerID = o.ID
        if row["PAYMENTREVERSALAMOUNT"] != "0":
            od.Donation = asm.get_currency(row["PAYMENTREVERSALAMOUNT"]) * -1
        else:
            od.Donation = asm.get_currency(row["PAYMENTAMOUNT"])
        comments = "Method/Card Type: %s/%s" % (row["PAYMENTMETH"], row["PAYMENTCARDTYPE"])
        comments += "\nVerification: " + row["PAYMENTIDVERIFICATION"]
        od.Comments = comments
        setuserfields(row, od)
        ownerdonations.append(od)

# Animals
canimal = asm.csv_to_list("%s/animal.csv" % PATH, uppercasekeys=True, strip=True)
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
    # TODO: DOB is not always present in these things
    a.DateOfBirth = getdate(row["DOB"])
    if a.DateOfBirth is None: 
        a.DateOfBirth = getdateage(age, getdate(row["ADDEDDATETIME"]))
        a.EstimatedDOB = 1
    a.DateBroughtIn = getdate(row["ADDEDDATETIME"])
    if a.DateBroughtIn is None:
        a.DateBroughtIn = datetime.datetime.today()    
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
    # If there's an owner, record it
    if row["PERSOWNR"] in ppo:
        o = ppo[row["PERSOWNR"]]
        a.OriginalOwnerID = o.ID
    # Shelterpro records Deceased as Status == 2 as far as we can tell
    if row["STATUS"] == 2:
        a.DeceasedDate = a.DateBroughtIn
        a.PTSReasonID = 2 # Died
    setuserfields(row, a)
    # Does this animal have an image? If so, add media/dbfs entries for it
    if IMAGE_FILE_IMPORT:
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


# Run through the shelter file and create any movements/euthanisation info
cshelter = asm.csv_to_list("%s/shelter.csv" % PATH, uppercasekeys=True, strip=True)
for row in cshelter:
    if row["ANIMALKEY"] not in ppa: continue
    a = ppa[row["ANIMALKEY"]]
    arivdate = getdate(row["ARIVDATE"])
    a.ShortCode = asm.strip(row["ANIMALKEY"])
    a.ShelterLocationUnit = asm.strip(row["KENNEL"])
    a.NonShelterAnimal = 0
    if arivdate is not None:
        a.DateBroughtIn = arivdate
        a.LastChangedDate = a.DateBroughtIn
        a.CreatedDate = a.DateBroughtIn
        a.generateCode(gettypeletter(a.AnimalTypeID))
        a.ShortCode = asm.strip(row["ANIMALKEY"])
        setuserfields(row, a)

    o = None
    if row["OWNERATDISPOSITION"] in ppo:
        o = ppo[row["OWNERATDISPOSITION"]]

    # Apply other fields
    if row["ARIVREAS"] == "QUARANTINE":
        a.IsQuarantine = 1
        setuserfields(row, a)

    elif row["ARIVREAS"] == "STRAY":
        if a.AnimalTypeID == 2: a.AnimalTypeID = 10
        if a.AnimalTypeID == 11: a.AnimalTypeID = 12
        a.EntryReasonID = 7
        setuserfields(row, a)

    # Adoptions
    if row["DISPMETH"] == "ADOPTED":
        if a is None or o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = getdate(row["DISPDATE"])
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 1
        setuserfields(row, a)
        setuserfields(row, m)
        movements.append(m)

    # Reclaims
    elif row["DISPMETH"] == "RETURN TO OWNER":
        if a is None or o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 5
        m.MovementDate = getdate(row["DISPDATE"])
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 5
        setuserfields(row, a)
        setuserfields(row, m)
        movements.append(m)

    # Released or Other
    elif row["DISPMETH"].startswith("RELEASED") or row["DISPMETH"] == "OTHER":
        if a is None or o is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = 0
        m.MovementType = 7
        m.MovementDate = getdate(row["DISPDATE"])
        m.Comments = row["DISPMETH"]
        a.Archived = 1
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 7
        setuserfields(row, a)
        setuserfields(row, m)
        movements.append(m)

    # Holding
    elif row["DISPMETH"] == "" and row["ANIMSTAT"] == "HOLDING":
        a.IsHold = 1
        a.Archived = 0
        setuserfields(row, a)

    # Deceased
    elif row["DISPMETH"] == "DECEASED":
        a.DeceasedDate = getdate(row["DISPDATE"])
        a.PTSReasonID = 2 # Died
        a.Archived = 1
        setuserfields(row, a)

    # Euthanized
    elif row["DISPMETH"].startswith("EUTH"):
        a.DeceasedDate = getdate(row["DISPDATE"])
        a.PutToSleep = 1
        a.PTSReasonID = 4 # Sick/Injured
        if row["DISPMETH"].find("BEHAVIOUR") != -1: a.PTSReasonID = 8 # Biting
        a.Archived = 1
        setuserfields(row, a)

    # If the outcome is blank, it's on the shelter
    elif row["DISPMETH"].strip() == "":
        a.Archived = 0
        setuserfields(row, a)

    # It's the name of an organisation that received the animal
    else:
        if a is None: continue
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = to.ID
        m.MovementType = 3
        m.MovementDate = getdate(row["DISPDATE"])
        m.Comments = row["DISPMETH"]
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 3
        setuserfields(row, a)
        setuserfields(row, m)
        movements.append(m)

if LICENCE_IMPORT:
    clicense = asm.csv_to_list("%s/license.csv" % PATH, uppercasekeys=True, strip=True)
    for row in clicense:
        a = None
        if row["ANIMALKEY"] in ppa:
            a = ppa[row["ANIMALKEY"]]
        o = None
        if row["LICENSEOWNER"] in ppo:
            o = ppo[row["LICENSEOWNER"]]
        if a is not None and o is not None:
            if getdate(row["LICENSEEFFECTIVEDATE"]) is None:
                continue
            ol = asm.OwnerLicence()
            ownerlicences.append(ol)
            ol.AnimalID = a.ID
            ol.OwnerID = o.ID
            ol.IssueDate = getdate(row["LICENSEEFFECTIVEDATE"])
            ol.ExpiryDate = getdate(row["LICENSEEXPIRATIONDATE"])
            if ol.ExpiryDate is None: ol.ExpiryDate = ol.IssueDate
            ol.LicenceNumber = asm.strip(row["LICENSE"])
            ol.LicenceTypeID = 2 # Unaltered dog
            if a.Neutered == 1:
                ol.LicenceTypeID = 1 # Altered dog
            setuserfields(row, ol)

# Incidents
if INCIDENT_IMPORT:
    cincident = asm.csv_to_list("%s/incident.csv" % PATH, uppercasekeys=True, strip=True)
    for row in cincident:
        ac = asm.AnimalControl()
        animalcontrol.append(ac)
        ppi[row["INCIDENTKEY"]] = ac
        calldate = getdate(row["DATETIMEASSIGNED"])
        if calldate is None: calldate = getdate(row["DATETIMEORIGINATION"])
        if calldate is None: calldate = asm.now()
        ac.CallDateTime = calldate
        ac.IncidentDateTime = calldate
        ac.DispatchDateTime = calldate
        ac.CompletedDate = getdate(row["DATETIMEOUTCOME"])
        if ac.CompletedDate is None: ac.CompletedDate = calldate
        if row["CITIZENMAKINGREPORT"] in ppo:
            ac.CallerID = ppo[row["CITIZENMAKINGREPORT"]].ID
        if row["OWNERATORIGINATION"] in ppo:
            ac.OwnerID = ppo[row["OWNERATORIGINATION"]].ID
        ac.IncidentCompletedID = 2
        if row["FINALOUTCOME"] == "ANIMAL PICKED UP":
            ac.IncidentCompletedID = 2 # Animal picked up
        elif row["FINALOUTCOME"] == "ANIMAL NOT FOUND":
            ac.IncidentCompletedID = 4 # Animal not found
        elif row["FINALOUTCOME"] == "OTHER":
            ac.IncidentCompletedID = 5 # Other
        ac.IncidentTypeID = 3 # Animals at large
        comments = "Case: %s\n" % row["INCIDENTKEY"]
        comments += "Outcome: %s\n" % row["FINALOUTCOME"]
        comments += "Precinct: %s\n" % row["PRECINCT"]
        ac.CallNotes = comments
        ac.Sex = 2
        setuserfields(row, ac)

# Incidents
if BITE_IMPORT:
    cbite = asm.csv_to_list("%s/bite.csv" % PATH, uppercasekeys=True, strip=True)
    for row in cbite:
        if row["BITEINCIDENTKEY"] not in ppi: continue
        ac = ppi[row["BITEINCIDENTKEY"]]
        # We don't create new incident records for bites, we just add the
        # extra info, such as the victim and suspect to the existing incident 
        # as all bites seem to be an incident in ShelterPro
        ac.IncidentTypeID = 5 # Switch incident type to Bite
        if row["BITEVICTIMKEY"] in ppo:
            ac.VictimID = ppo[row["BITEVICTIMKEY"]].ID
        """
        # NOTE: Could not find any instance in the data where biteownerkey didn't already match
        #       the owner from the incident, so the below is not necessary
        if row["BITEOWNERKEY"] in ppo:
            biteo = ppo[row["BITEOWNERKEY"]].ID
            if ac.OwnerID > 0: 
                ac.Owner2ID = biteo
            else:
                ac.OwnerID = biteo
        """
        comments = "Bite test type: %s\n" % row["BITETESTTYPE"]
        comments += "Bite test method: %s\n" % row["BITETESTMETHOD"]
        comments += "Bite test result: %s\n" % row["BITETESTRESULT"]
        comments += "Bite precinct: %s\n" % row["BITEPRECINCT"]
        comments += "Bite status: %s\n" % row["BITESTATUS"]
        if ac.CallNotes == "": 
            ac.CallNotes = comments
            setuserfields(row, ac)
        l = asm.Log()
        logs.append(l)
        l.LogTypeID = 3
        l.LinkID = ac.ID
        l.LinkType = 6
        l.Date = getdate(row["BITEDATE"])
        if l.Date is None:
            l.Date = asm.now()
        l.Comments = comments
        setuserfields(row, l)

# Notes as log entries
cnote = asm.csv_to_list("%s/note.csv" % PATH, uppercasekeys=True, strip=True)
for row in cnote:
    eventtype = row["EVENTTYPE"]
    eventkey = row["EVENTKEY"]
    notedate = asm.getdate_mmddyy(row["NOTEDATE"])
    memo = row["NOTEMEMO"]
    if eventtype in [ "1", "3" ]: # animal/intake or case notes
        if not eventkey in ppa: continue
        linkid = ppa[eventkey].ID
        ppa[eventkey].HiddenAnimalDetails += "\n" + memo
        l = asm.Log()
        logs.append(l)
        l.LogTypeID = 3
        l.LinkID = linkid
        l.LinkType = 0 # animal
        l.Date = notedate
        if l.Date is None:
            l.Date = asm.now()
        l.Comments = memo
        setuserfields(row, l)
    elif eventtype in [ "2" ]: # person notes
        if not eventkey in ppo: continue
        linkid = ppo[eventkey].ID
        l = asm.Log()
        logs.append(l)
        l.LogTypeID = 3
        l.LinkID = linkid
        l.LinkType = 1 # person
        l.Date = notedate
        if l.Date is None:
            l.Date = asm.now()
        l.Comments = memo
        setuserfields(row, l)
    elif eventtype in [ "5", "10" ]: # case and incident notes
        if not eventkey in ppi: continue
        linkid = ppi[eventkey].ID
        ppi[eventkey].CallNotes += "\n" + memo
        l = asm.Log()
        logs.append(l)
        l.LogTypeID = 3
        l.LinkID = linkid
        l.LinkType = 6 # animalcontrol
        l.Date = notedate
        if l.Date is None:
            l.Date = asm.now()
        l.Comments = memo
        setuserfields(row, l)

# Image table
if IMAGE_TABLE_IMPORT:
    # The image.csv file exported from MDB needs to have the -b hex flag parameter
    # passed to mdb-export so that the file data is hex. 
    # This allows bytes.fromhex(s) to be used to unpack the data.
    # Due to the potential size that this file can be, we use the csvreader to
    # stream it in rather than loading the whole lot into RAM at once
    import csv
    csv.field_size_limit(sys.maxsize) # Python has a default field size limit of 128Kb
    with open("%s/image.csv" % PATH) as f:
        reader = csv.reader(f)
        for r in reader:
            eventkey = r[2]
            if eventkey not in ppa: continue # bail if we have no animal to link it to
            a = ppa[eventkey]
            imagedata = r[9]
            imagedata = bytes.fromhex(imagedata)
            asm.animal_image(a.ID, imagedata) # This handles outputting both media and dbfs

# Vaccinations
if VACCINATION_IMPORT:
    cvacc = asm.csv_to_list("%s/vacc.csv" % PATH, uppercasekeys=True, strip=True)
    for row in cvacc:
        if row["ANIMALKEY"] not in ppa: continue
        a = ppa[row["ANIMALKEY"]]
        # Each row contains a vaccination
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        vaccdate = getdate(row["VACCEFFECTIVEDATE"])
        if vaccdate is None:
            vaccdate = a.DateBroughtIn
        av.AnimalID = a.ID
        av.VaccinationID = 8
        if row["VACCTYPE"].find("DHLPP") != -1: av.VaccinationID = 8
        if row["VACCTYPE"].find("BORDETELLA") != -1: av.VaccinationID = 6
        if row["VACCTYPE"].find("RABIES") != -1: av.VaccinationID = 4
        av.DateRequired = vaccdate
        av.DateOfVaccination = vaccdate
        av.DateExpires = getdate(row["VACCEXPIRATIONDATE"])
        av.Manufacturer = row["VACCMANUFACTURER"]
        av.BatchNumber = row["VACCSERIALNUMBER"]
        av.Comments = "Name: %s, Issue: %s" % (row["VACCDRUGNAME"], row["VACCISSUEDPRTDATE"])
        setuserfields(row, av)
    del cvacc

# Run back through the animals, if we have any that are still
# on shelter after 2 years, add an adoption to an unknown owner
if FAKE_ADOPTION_ONSHELTER_DAYS > 0:
    asm.adopt_older_than(animals, movements, uo.ID, FAKE_ADOPTION_ONSHELTER_DAYS)

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
for od in ownerdonations:
    print(od)
for ol in ownerlicences:
    print(ol)
for ac in animalcontrol:
    print(ac)

asm.stderr_summary(animals=animals, animalvaccinations=animalvaccinations, logs=logs, owners=owners, movements=movements, ownerdonations=ownerdonations, ownerlicences=ownerlicences, animalcontrol=animalcontrol)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")

