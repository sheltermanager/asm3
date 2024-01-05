#!/usr/bin/python

import asm, datetime

"""
Import script for AdoptAFriend - www.adoptafriend.us

Source is two Access MDB files: ShelAnml.mdb and ShelData.mdb

Use mdb-export to generate CSV files from these tables (and holy
hell is this one amateurish pile of mess!)

ShelData.mdb:
    adopts.csv         appeals.csv     euthanasia.csv  list1.csv     
    animalhistory.csv  complaints.csv  license.csv     payments.csv  
    
ShelAnml.mdb:
    record.csv

26th January, 2015, rewritten with new kit 27th October, 2015
Last change 14th January, 2020
"""

PATH = "/home/robin/tmp/asm3_import_data/aaf_ch2183/"

# For use with fields that just contain the sex
def getincidenttype(ctype):
    imap = {
        "at large": 3,
        "bite": 5,
        "trap": 3, 
        "injured": 10,
        "holding stray": 8,
        "cruelty": 7,
        "nuisance": 3,
        "abandonment": 7,
        "in car": 4,
        "hit by car": 10
    }
    for k, v in imap.iteritems():
        if ctype.find(k) != -1:
            return v
    return 3

def getcompletedtype(ctype):
    cmap = {
        "issued": 3,
        "picked": 2,
    }
    for k, v in cmap.iteritems():
        if ctype.find(k) != -1:
            return v
    return 2

def gettype(sp):
    if sp == "Dog" or sp == "Puppy": return 2 # Unwanted Dog
    if sp == "Cat" or sp == "Kitten": return 11 # Unwanted Cat
    return 13 # Misc

def gettypeletter(aid):
    tmap = {
        2: "D",
        11: "U",
        13: "M"
    }
    return tmap[aid]

def getpaymentmethod(meth):
    meth = meth.strip()
    if meth == "Visa":
        return 3
    elif meth == "Mastercard":
        return 3
    elif meth == "Check":
        return 2
    elif meth == "Cash":
        return 1
    else:
        return 1

def getsize(size):
    if size == "L": return 1
    if size == "M": return 2
    if size == "S": return 3
    return 2

def findanimal(animalkey):
    """ Looks for an animal with the given code in the collection
        of animals. If one wasn't found, It tries the name. If still
        nothing is found, None is returned """
    if animalmap.has_key(animalkey):
        return animalmap[animalkey]
    return None

def findowner(firstname = "", lastname = "", address = "", fullname = "", masterid = "0"):
    """ Looks for an owner with the given name in the collection
        of owners. If one wasn't found, None is returned """
    if fullname != "":
        if ownermapbyname.has_key(fullname):
            return ownermapbyname[fullname]
        return None
    if masterid != "0":
        if ownermapbymasterid.has_key(masterid):
            return ownermapbymasterid[masterid]
        return None
    key = firstname + " " + lastname + " " + address
    if ownermapbykey.has_key(key):
        return ownermapbykey[key]
    return None

def bs(s):
    return s.replace("\\", "/").replace("'", "`")

# --- START OF CONVERSION ---

owners = []
ownerdonations = []
movements = []
animals = []
animalcontrols = []

ownermapbyname = {}
ownermapbykey = {}
ownermapbymasterid = {}
animalmap = {}

nextanimalid = 100
nextanimalcontrolid = 100
nextownerid = 100
nextownerdonationid = 100
nextmovementid = 100
startanimalid = 100
startanimalcontrolid = 100
startownerdonationid = 100
startownerid = 100
startmovementid = 100

asm.setid("donationtype", 100)

unknown = asm.Owner(nextownerid)
owners.append(unknown)
nextownerid += 1
unknown.OwnerSurname = "Unknown"
unknown.OwnerName = unknown.OwnerSurname

for row in asm.csv_to_list(PATH + "list1.csv", strip=True):
    o = asm.Owner(nextownerid)
    owners.append(o)
    nextownerid += 1
    o.ExtraID = row["MasterID"]
    o.OwnerTitle = row["TITLE"]
    o.OwnerForeNames = row["FIRSTNAME"]
    o.OwnerSurname = row["LASTNAME"]
    if o.OwnerSurname == "": o.OwnerSurname = "(blank)"
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = row["ADD1"]
    o.OwnerTown = row["CITY"]
    o.OwnerCounty = row["STATE"]
    o.OwnerPostcode = row["ZIP"]
    o.HomeTelephone = row["PHONENUMB"]
    o.WorkTelephone = row["BPHONE"]
    o.EmailAddress = row["Email"]
    o.Comments = row["MEMOPAD"]
    tf = row["TYPE"]
    if tf.lower().find("x") != -1:
        o.ExcludeFromBulkEmail = 1
    if tf.lower().find("b") != -1:
        o.IsBanned = 1
    if tf.lower().find("d") != -1:
        o.IsDeceased = 1
    #flags = ""
    #o.AdditionalFlags = flags
    ownermapbymasterid[o.ExtraID] = o
    ownermapbyname[o.OwnerName] = o
    ownermapbykey[o.OwnerForeNames + " " + o.OwnerSurname + " " + asm.fw(o.OwnerAddress)] = o

# On shelter animals are kept in a separate database table called RECORD
# with a slightly different layout to animalhistory
for row in asm.csv_to_list(PATH + "record.csv", strip=True):

    # Each row contains a new animal
    a = asm.Animal(nextanimalid)
    animals.append(a)
    animalmap[row["RECORDNUMBER"]] = a
    nextanimalid += 1
    a.ExtraID = row["RECORDNUMBER"]

    a.DateBroughtIn = asm.getdate_mmddyy(row["DATE"])
    if a.DateBroughtIn is None:
        a.DateBroughtIn = asm.now()
    a.AnimalTypeID = gettype(row["SPECIES"])
    if row["SPECIES"] == "Kitten":
        a.SpeciesID = 1
    elif row["SPECIES"] == "Puppy":
        a.SpeciesID = 2
    else:
        a.SpeciesID = asm.species_id_for_name(row["SPECIES"])
    a.generateCode(gettypeletter(a.AnimalTypeID))
    a.ShortCode = row["FORMNUM"]
    ob = row["BREEDID"]
    a.CrossBreed = 0
    if ob.find("Mix") != -1:
        a.CrossBreed = 1
        a.Breed2ID = 442
        ob = ob.replace("Mix", "")
    a.BreedID = asm.breed_id_for_name(ob)
    a.BreedName = asm.breed_name(a.BreedID, a.Breed2ID)
    a.Sex = asm.getsex_mf(row["SEX"])
    a.Size = getsize(row["RSize"])
    a.Neutered = asm.cint(row["SPAYED"])
    a.NeuteredDate = asm.getdate_mmddyy(row["SPAYDATE"])
    a.DateOfBirth = asm.getdate_mmddyy(row["DOB"])
    if a.DateOfBirth is None: 
        a.DateOfBirth = a.DateBroughtIn
    a.BaseColourID = asm.colour_id_for_name(row["RColor"])
    a.RabiesTag = row["TAG"]
    a.IdentichipNumber = row["MICROCHIP"]
    if a.IdentichipNumber.strip() != "": 
        a.Identichipped = 1
        a.IdentichipDate = a.DateBroughtIn
    a.AnimalName = row["PETNAME"]
    if a.AnimalName == "":
        a.AnimalName = "(unknown)"
    a.Markings = row["RDescr"]
    comments = ""
    comments += "Breed: %s" % row["BREEDID"]
    a.HiddenAnimalDetails = bs(comments)
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 1
    a.AnimalComments = bs(row["MEMOPAD"])
    a.ReasonForEntry = row["RSurrenderReason"]
    a.IsHouseTrained = row["RHousebroken"] == 1 and 0 or 1
    a.IsGoodWithChildren = row["RChildren"] == 1 and 0 or 1
    a.IsGoodWithDogs = row["RAnimals"] == 1 and 0 or 1
    a.IsGoodWithCats = row["RAnimals"] == 1 and 0 or 1
    if row["DeclawType"] != "": a.Declawed = 1
    origin = row["ROriginOfAnimal"]
    disp = row["RDisposition"]
    a.EntryReasonID = 17 # Surrender
    if origin.startswith("Stray"):
        a.EntryReasonID = 7
        a.EntryTypeID = 2
    elif origin.startswith("Transfer"):
        a.EntryReasonID = 15
        a.IsTransfer = 1
        a.EntryTypeID = 3
    elif origin.startswith("Euthan"):
        a.DeceasedDate = a.DateBroughtIn
        a.PTSReason = origin
        a.PutToSleep = 1
        a.Archived = 1
    if disp.startswith("Euthan"):
        a.DeceasedDate = a.DateBroughtIn
        a.PTSReason = disp
        a.PutToSleep = 1
        a.Archived = 1
    if disp.startswith("DOA"):
        a.EntryReasonID = 6
        a.DeceasedDate = a.DateBroughtIn
        a.IsDOA = 1
        a.Archived = 1
    im = row["RIntakeMunicipality"]
    im = im.replace("'", "").replace(";", "").replace("`", "").replace(".", "").replace("\"", "")
    if im != "" and im != "y" and im != "l" and im != "v":
        a.IsPickup = 1
        a.PickupLocationID = asm.pickuplocation_id_for_name(im, True)
    # Surrendering owner info if available
    if row["MasterID"] != "":
        o = findowner(masterid = row["MasterID"])
        if o is not None:
            a.OriginalOwnerID = ownermapbymasterid[row["MasterID"]].ID
    # If we have a disposition of reclaimed, create a reclaim movement
    # to the original owner
    if row["RDisposition"] == "RECLAIMED" and a.OriginalOwnerID != 0:
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = a.OriginalOwnerID
        m.MovementType = 5
        m.MovementDate = a.DateBroughtIn
        a.Archived = 1
        a.ActiveMovementDate = a.DateBroughtIn
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 5
        movements.append(m)

# animals
for row in asm.csv_to_list(PATH + "animalhistory.csv", strip=True):

    # Did we already see this animal in record.csv ?
    if animalmap.has_key(row["RECORDNUMBER"]):
        continue

    a = asm.Animal(nextanimalid)
    animals.append(a)
    animalmap[row["RECORDNUMBER"]] = a
    nextanimalid += 1
    a.ExtraID = row["RECORDNUMBER"]

    a.DateBroughtIn = asm.getdate_mmddyy(row["DATE"])
    if a.DateBroughtIn is None:
        a.DateBroughtIn = asm.now()
    a.AnimalTypeID = gettype(row["SPECIES"])
    if row["SPECIES"] == "Kitten":
        a.SpeciesID = 1
    elif row["SPECIES"] == "Puppy":
        a.SpeciesID = 2
    else:
        a.SpeciesID = asm.species_id_for_name(row["SPECIES"])
    a.generateCode(gettypeletter(a.AnimalTypeID))
    a.ShortCode = row["FORMNUM"]
    ob = row["BREEDID"]
    a.CrossBreed = 0
    if ob.find("Mix") != -1:
        a.CrossBreed = 1
        a.Breed2ID = 442
        ob = ob.replace("Mix", "")
    a.BreedID = asm.breed_id_for_name(ob)
    a.BreedName = asm.breed_name(a.BreedID, a.Breed2ID)
    a.Sex = asm.getsex_mf(row["SEX"])
    a.Size = getsize(row["RSize"])
    a.Neutered = asm.cint(row["SPAYED"])
    a.NeuteredDate = asm.getdate_mmddyy(row["SPAYDATE"])
    a.DateOfBirth = asm.getdate_mmddyy(row["DOB"])
    if a.DateOfBirth is None: 
        a.DateOfBirth = a.DateBroughtIn
    a.BaseColourID = asm.colour_id_for_name(row["RColor"])
    a.RabiesTag = row["TAG"]
    a.IdentichipNumber = row["MICROCHIP"]
    if a.IdentichipNumber.strip() != "": 
        a.Identichipped = 1
        a.IdentichipDate = a.DateBroughtIn
    a.AnimalName = row["PETNAME"]
    if a.AnimalName == "":
        a.AnimalName = "(unknown)"
    a.Markings = row["RDescr"]
    comments = ""
    comments += "Breed: %s" % row["BREEDID"]
    a.HiddenAnimalDetails = bs(comments)
    a.IsNotAvailableForAdoption = 0
    a.ShelterLocation = 1
    a.AnimalComments = bs(row["MEMOPAD"])
    a.ReasonForEntry = row["RSurrenderReason"]
    a.IsHouseTrained = row["RHousebroken"] == 1 and 0 or 1
    a.IsGoodWithChildren = row["RChildren"] == 1 and 0 or 1
    a.IsGoodWithDogs = row["RAnimals"] == 1 and 0 or 1
    a.IsGoodWithCats = row["RAnimals"] == 1 and 0 or 1
    if row["DeclawType"] != "": a.Declawed = 1
    origin = row["ROriginOfAnimal"]
    if len(origin) < 3:
        origin = "Surrender"
    disp = row["RDisposition"]
    a.EntryReasonID = asm.entryreason_id_for_name(origin, True)
    if origin.startswith("Transfer"):
        a.IsTransfer = 1
    elif origin.startswith("Euthan"):
        a.DeceasedDate = a.DateBroughtIn
        a.PTSReason = origin
        a.PutToSleep = 1
        a.Archived = 1
    if disp.startswith("Euthan"):
        a.DeceasedDate = a.DateBroughtIn
        a.PTSReason = disp
        a.PutToSleep = 1
        a.Archived = 1
    if disp.startswith("DOA"):
        a.DeceasedDate = a.DateBroughtIn
        a.IsDOA = 1
        a.Archived = 1
    im = row["RIntakeMunicipality"]
    im = im.replace("'", "").replace(";", "").replace("`", "").replace(".", "").replace("\"", "")
    if im != "" and im != "y" and im != "l" and im != "v":
        a.IsPickup = 1
        a.PickupLocationID = asm.pickuplocation_id_for_name(im, True)
    # Surrendering owner info if available
    if row["MasterID"] != "":
        o = findowner(masterid = row["MasterID"])
        if o is not None:
            a.OriginalOwnerID = ownermapbymasterid[row["MasterID"]].ID
    # If we have a disposition of reclaimed, create a reclaim movement
    # to the original owner
    if row["RDisposition"] == "RECLAIMED" and a.OriginalOwnerID != 0:
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = a.OriginalOwnerID
        m.MovementType = 5
        m.MovementDate = a.DateBroughtIn
        a.Archived = 1
        a.ActiveMovementDate = a.DateBroughtIn
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 5
        movements.append(m)

for row in asm.csv_to_list(PATH + "euthanasia.csv", strip=True):
    a = findanimal(row["EuthPetID"])
    if a is None: continue
    a.DeceasedDate = asm.getdate_mmddyy(row["EuthDateTime"])
    a.PutToSleep = 1
    a.Archived = 1

for row in asm.csv_to_list(PATH + "adopts.csv", strip=True):
    a = findanimal(row["ANIMDALID"])
    if a is None: continue
    evtdate = asm.getdate_mmddyy(row["dateadopted"])
    if evtdate is None: continue
    o = findowner(masterid = row["MasterID"])
    if o is None: continue

    m = asm.Movement(nextmovementid)
    nextmovementid += 1
    m.AnimalID = a.ID
    m.OwnerID = o.ID
    m.MovementType = 1
    m.MovementDate = evtdate
    a.Archived = 1
    a.ActiveMovementDate = evtdate
    a.ActiveMovementID = m.ID
    a.ActiveMovementType = 1
    movements.append(m)

for row in asm.csv_to_list(PATH + "appeals.csv", strip=True):

    # Skip junk data
    if asm.get_currency(row["Amount"]) == 0: continue

    o = findowner(masterid = row["SponsorID"])
    if o is None: continue

    od = asm.OwnerDonation(nextownerdonationid)
    ownerdonations.append(od)
    nextownerdonationid += 1
    od.OwnerID = o.ID
    od.AnimalID = 0
    od.MovementID = 0
    od.Date = asm.getdate_mmddyy(row["AppealDate"])
    od.Donation = asm.get_currency(row["Amount"])
    od.DonationTypeID = asm.donationtype_id_for_name(row["AppealType"], True)
    od.DonationPaymentID = getpaymentmethod(row["Paymethod"])
    od.Comments = row["Anotes"]

# For one customer, this duplicated appeals, but not in the last one I saw
for row in asm.csv_to_list(PATH + "payments.csv", strip=True):
    # Skip junk data
    if row["Customer"]: continue
    if asm.get_currency(row["Paid"]) == 0: continue

    o = findowner(fullname = row["Customer"])
    if o is None: continue

    od = asm.OwnerDonation(nextownerdonationid)
    ownerdonations.append(od)
    nextownerdonationid += 1
    od.OwnerID = o.ID
    od.AnimalID = o.ExtraID
    if od.AnimalID == "": od.AnimalID = 0
    od.MovementID = 0
    od.Date = asm.getdate_mmddyy(row["Date"])
    od.Donation = asm.get_currency(row["Paid"])
    od.DonationTypeID = 2
    od.DonationPaymentID = getpaymentmethod(row["PaidBy"])

for row in asm.csv_to_list(PATH + "complaints.csv", strip=True):

    if asm.getdate_mmddyy(row["Date"]) is None: continue

    ac = asm.AnimalControl(nextanimalcontrolid)
    animalcontrols.append(ac)
    nextanimalcontrolid += 1
    calldate = asm.getdate_mmddyy(row["Date"])
    invdate = asm.getdate_mmddyy(row["InvestigationDate"])
    if invdate is None: invdate = calldate
    # Caller details
    if row["CDLastname"] != "":
        o = findowner(row["CDFirstname"], row["CDLastname"], row["CDAdd1"])
        if o is None:
            o = asm.Owner(nextownerid)
            owners.append(o)
            nextownerid += 1
            o.OwnerForeNames = row["CDFirstname"]
            o.OwnerSurname = row["CDLastname"]
            if o.OwnerSurname == "": o.OwnerSurname = "(blank)"
            o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
            o.OwnerAddress = row["CDAdd1"]
            o.OwnerTown = row["CDCity"]
            o.OwnerCounty = row["CDState"]
            o.OwnerPostcode = row["CDZip"]
            o.HomeTelephone = row["CDHomePhone"]
            o.WorkTelephone = row["CDBusinessPhone"]
            ownermapbyname[o.OwnerName] = o
            ownermapbykey[o.OwnerForeNames + " " + o.OwnerSurname + " " + asm.fw(o.OwnerAddress)] = o
        ac.CallerID = o.ID

    # Dispatch
    ac.DispatchAddress = row["CWAdd1"]
    ac.DispatchTown = row["CWCity"]
    ac.DispatchCounty = row["CWState"]
    ac.DispatchPostcode = row["CWZip"]
    ac.IncidentCompletedID = getcompletedtype(row["ComplaintResolutionType"])
    ac.IncidentTypeID = getincidenttype(row["ComplaintType"])
    ac.IncidentDateTime = calldate
    ac.CallDateTime = calldate
    ac.DispatchDateTime = invdate
    ac.CompletedDate = invdate
    comments = ""
    if row["OfficerAssigned"] != "": comments += "Officer: " + row["OfficerAssigned"] + "\n"
    if row["ComplaintType"] != "": comments += "Complaint: " + row["ComplaintType"] + ", Resolution: " + row["ComplaintResolutionType"] + "\n"
    if row["CWMunicipality"] != "": comments += "Municipality: " + row["CWMunicipality"] + "\n"
    if row["CWDirections"] != "": comments += "Directions: " + row["CWDirections"] + "\n"
    if row["Offense"] != "": comments += "Offense: " + row["Offense"] + "\n"
    if row["AdditinalInfo"] != "": comments += "Additional: " + row["AdditinalInfo"] + "\n"
    if row["Narrative"] != "": comments += "Narrative: " + row["Narrative"] + "\n"
    ac.CallNotes = comments
    ac.Sex = 2

for a in animals:
    # If an animal has been on shelter longer than 3 months, adopt them
    # to the unknown owner to prevent a massive amount of on shelter animals
    if a.Archived == 0 and a.DateBroughtIn.date() < (datetime.date.today() - datetime.timedelta(days = 28 * 3)):
        adoptdate = a.DateBroughtIn + datetime.timedelta(days=31)
        m = asm.Movement(nextmovementid)
        nextmovementid += 1
        m.AnimalID = a.ID
        m.OwnerID = 100
        m.MovementType = 1
        m.MovementDate = adoptdate
        a.Archived = 1
        a.ActiveMovementDate = adoptdate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 1
        movements.append(m)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= %d;" % startanimalid
print "DELETE FROM animalcontrol WHERE ID >= %d;" % startanimalcontrolid
print "DELETE FROM owner WHERE ID >= %d;" % startownerid
print "DELETE FROM ownerdonation WHERE ID >= %d;" % startownerdonationid
print "DELETE FROM adoption WHERE ID >= %d;" % startmovementid
print "DELETE FROM pickuplocation;"
print "DELETE FROM entryreason;"
print "DELETE FROM donationtype WHERE ID >= 100;"

# Now that everything else is done, output stored records
for k, v in asm.pickuplocations.iteritems():
    print v
for k, v in asm.entryreasons.iteritems():
    print v
for k, v in asm.donationtypes.iteritems():
    print v
for a in animals:
    print a
for o in owners:
    print o
for od in ownerdonations:
    print od
for m in movements:
    print m
for ac in animalcontrols:
    print ac

asm.stderr_summary(animals=animals, owners=owners, movements=movements, ownerdonations=ownerdonations, animalcontrol=animalcontrols)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"
