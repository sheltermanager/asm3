#!/usr/bin/env python3

import asm

"""
Import script for VetRescue databases exported to MDB, then extracted to CSV with mdb-tools

extraction script:

#!/usr/bin/env python3
import os, sys
dbfile = sys.argv[1]
lines = os.popen(f"mdb-tables -1 {dbfile}").readlines()
for l in lines:
    l = l.strip()
    cmd = f"mdb-export {dbfile} \"{l}\" > \"{l}.csv\""
    print(cmd)
    os.system(cmd)

28th Feb, 2023
"""

START_ID = 100
PATH = "/home/robin/tmp/asm3_import_data/vr_tc2979"

def findowner(last = "", address = ""):
    """ Looks for an owner with the given name and address in the collection
        of owners. If one wasn't found, None is returned """
    for o in owners:
        if o.OwnerSurname == last.strip() and o.OwnerAddress.startswith(address.strip()):
            return o
    return None

def getdatetime(d, noblanks=False):
    rv = asm.parse_date(d, "%m/%d/%Y %H:%M:%S")
    if noblanks and rv is None: rv = asm.now()
    return rv

def getdate(d, noblanks=False):
    rv = asm.getdate_guess(d)
    if noblanks and rv is None: rv = asm.now()
    return rv

# --- START OF CONVERSION ---

owners = []
ownerdonations = []
logs = []
movements = []
animals = []
ppa = {}
ppo = {}

asm.setid("animal", START_ID)
asm.setid("log", START_ID)
asm.setid("owner", START_ID)
asm.setid("ownerdonation", START_ID)
asm.setid("adoption", START_ID)

print("\\set ON_ERROR_STOP\nBEGIN;")
print("DELETE FROM animal WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM log WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM owner WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM ownerdonation WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM adoption WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)

# Create an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname

# Do both Keeper.csv and FClient.csv as FClient seems to have more records, but somehow less data? 
# This database makes no sense at all.
for d in asm.csv_to_list(f"{PATH}/Keeper.csv"):
    # Ignore repeated headers
    if d["CustCode"] == "CustCode": continue
    # Each row contains a person, but is also duplicated for every animal, so skip duplicates
    if d["CustCode"] in ppo: continue
    o = asm.Owner()
    owners.append(o)
    ppo[d["CustCode"]] = o
    o.ExtraID = d["CustCode"]
    o.OwnerTitle = d["Title"]
    o.OwnerForeNames = d["First"]
    o.OwnerSurname = d["Last"]
    o.OwnerType = 1
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    # Organisations don't have a title and first name - just like our schema
    if o.OwnerTitle == "" and o.OwnerForeNames == "":
        o.OwnerType = 2
        o.OwnerName = o.OwnerSurname
    o.OwnerAddress = d["Ad"]
    # Ad1 contains town if there isn't an ad2
    if d["Ad1"] != "" and d["Ad2"] != "": 
        o.OwnerAddress += "\n" + d["Ad1"]
        o.OwnerTown = d["Ad2"]
    else:
        o.OwnerTown = d["Ad1"]
    o.OwnerCounty = d["County"]
    o.OwnerPostcode = d["PostC"]
    o.EmailAddress = d["Email"]
    o.HomeTelephone = d["HomeP"]
    o.WorkTelephone = d["WorkP"]
    o.MobileTelephone = d["Mobile"]
    o.CreatedDate = getdatetime(d["KeeperDate"])
    if o.CreatedDate is None: o.CreatedDate = asm.now()
    o.Comments = d["PostIt"]
    o.MembershipNumber = d["MemberNo"]
    o.MembershipExpiryDate = getdate(d["RenewalDate"])
    o.ExcludeFromBulkEmail = asm.iif(d["Mailshots"] == -1, 1, 0)
    o.IsMember = asm.iif(o.MembershipNumber != "", 1, 0)
    if "Staff" in d: o.IsStaff = asm.iif(d["Staff"] == "Y", 1, 0)
    gdpr = []
    if d["FundPhone"] == "Y": gdpr.append("phone")
    if d["FundSMS"] == "Y": gdpr.append("sms")
    if "FundEmail" in d and d["FundEmail"] == "Y": gdpr.append("email")
    if d["FundPost"] == "Y": gdpr.append("post")
    o.GDPRContactOptIn = ",".join(gdpr)

for d in asm.csv_to_list(f"{PATH}/FClient.csv"):
    # Ignore repeated headers
    if d["CustCode"] == "CustCode": continue
    # Each row contains a person, but skip duplicates just in case
    if d["CustCode"] in ppo: continue
    o = asm.Owner()
    owners.append(o)
    ppo[d["CustCode"]] = o
    o.ExtraID = d["CustCode"]
    o.OwnerTitle = d["Title"]
    o.OwnerInitials = d["Inits"]
    o.OwnerForeNames = d["First"]
    o.OwnerSurname = d["Surname"]
    o.OwnerType = 1
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    # Organisations don't have a first name - just like our schema
    if o.OwnerTitle == "" and o.OwnerForeNames == "":
        o.OwnerType = 2
        o.OwnerName = o.OwnerSurname
    o.OwnerAddress = d["Ad1"] + " " + d["Ad2"]
    o.OwnerTown = d["Ad3"]
    o.OwnerCounty = d["Ad4"]
    if o.OwnerCounty.strip() == "": o.OwnerCounty = d["Ad5"]
    o.OwnerPostcode = d["PC"]
    o.EmailAddress = d["Email"]
    o.HomeTelephone = d["Tel"]
    o.WorkTelephone = d["Work"]
    o.MobileTelephone = d["Mobile"]
    o.CreatedDate = getdatetime(d["LastCheckDate"])
    if o.CreatedDate is None: o.CreatedDate = asm.now()
    o.ExcludeFromBulkEmail = asm.iif(d["EMailOk"] == 0, 1, 0)

for d in asm.csv_to_list(f"{PATH}/Animal.csv"):
    # If it's a repeat of the header row, skip
    if d["PetRef"] == "PetRef": continue
    # If it's a blank row, skip
    if d["PetRef"] == "": continue
    # Each row contains an animal
    a = asm.Animal()
    animals.append(a)
    ppa[d["PetRef"]] = a
    if d["Species"] == "Feline":
        a.AnimalTypeID = 11 # Unwanted Cat
        if d["EntryReason"] == "Stray":
            a.AnimalTypeID = 12 # Stray Cat
    elif d["Species"] == "Canine":
        a.AnimalTypeID = 2 # Unwanted Dog
        if d["EntryReason"] == "Stray":
            a.AnimalTypeID = 10 # Stray Dog
    else:
        a.AnimalTypeID = 13 # Misc
    a.SpeciesID = asm.species_id_for_name(d["Species"])
    a.AnimalName = d["PetName"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateBroughtIn = getdate(d["DateRegistered"]) or asm.today()
    a.DateOfBirth = getdate(d["DOB"])
    if a.DateOfBirth is None: a.DateOfBirth = asm.subtract_days(a.DateBroughtIn, 365)
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    if d["EntryReason"].find("Transfer") != -1:
        a.IsTransfer = 1
    a.EntryReasonID = 17 # Surrender
    if d["EntryReason"] == "Stray": a.EntryReasonID = 7 # Stray
    if a.IsTransfer == 1: a.EntryReasonID = 15 # Transfer from other shelter
    a.generateCode()
    a.ShortCode = d["PetRef"]
    a.IdentichipNumber = d["IdNum"].strip()
    if a.IdentichipNumber != "": a.Identichipped = 1
    a.IdentichipDate = getdate(d["MicroDate"])
    asm.breed_ids(a, d["Breed"])
    a.Sex = asm.getsex_mf(d["Sex"])
    a.Neutered = d["Sex"].find("neutered") != -1 and 1 or 0
    a.Size = 2
    a.IsGoodWithCats = 2
    a.IsGoodWithDogs = 2
    a.IsGoodWithChildren = 2
    a.HouseTrained = 0
    a.Archived = 0
    comments = "Species: " + d["Species"] + ", Breed: " + d["Breed"] + ", Colour: " + d["Colour"]
    comments += ", Vaccinated: " + asm.iif(d["Vaccinated"] == "0", "N", "Y")
    a.AnimalComments = d["GenNote"]
    a.ReasonForEntry = d["EntryReason"]
    a.HiddenAnimalDetails = comments

for d in asm.csv_to_list(f"{PATH}/AnimalNotes.csv"):
    if d["PetRef"] not in ppa: continue
    a = ppa[d["PetRef"]]
    l = asm.Log()
    l.LogTypeID = 3 # History
    l.Date = getdate(d["Date"])
    l.LinkID = a.ID
    l.LinkType = 0
    l.Comments = d["Notes"]
    logs.append(l)

# Clinic history, can't really map it to any of our medical areas as
# there isn't enough of it. Put the notes in the log instead.
for d in asm.csv_to_list(f"{PATH}/ClinHist.csv"):
    if d["PetRef"] not in ppa: continue
    if d["MedicalNotes"].strip() == "": continue
    a = ppa[d["PetRef"]]
    l = asm.Log()
    l.LogTypeID = 3 # History
    try:
        l.Date = getdate(d["ConsultDateID"])
    except:
        l.Date = asm.today()
    l.LinkID = a.ID
    l.LinkType = 0
    l.Comments = d["MedicalNotes"]
    logs.append(l)

"""
# Use rehoming list report to create the adoption movements.
# deprecated, it was only in the first database got. There's an AniMovement
# table that indicates rehomed and is consistently there.
for d in asm.csv_to_list(f"{PATH}/Rehomed list.csv"):
    # Find the person and animal
    if d["PetRef"] not in ppa: continue
    a = ppa[d["PetRef"]]
    o = findowner(d["Last"], d["Ad"])
    if a is None or o is None: continue
    if o.ExtraID == SHELTER_CUSTCODE: continue # skip rehoming entries to the shelter
    m = asm.Movement()
    m.AnimalID = a.ID
    m.OwnerID = o.ID
    m.MovementType = 1
    m.MovementDate = getdate(d["KeeperDate"])
    a.Archived = 1
    a.ActiveMovementID = m.ID
    a.ActiveMovementDate = m.MovementDate
    a.ActiveMovementType = 1
    a.LastChangedDate = m.MovementDate
    movements.append(m)
"""

for d in asm.csv_to_list(f"{PATH}/AniMovement.csv"):
    # Find the person and animal
    if d["PetRef"] not in ppa: continue
    a = ppa[d["PetRef"]]
    if d["CustCode"] not in ppo: continue
    o = ppo[d["CustCode"]]
    if a is None or o is None: continue
    if d["ReHomeDate"] == "": continue
    m = asm.Movement()
    m.AnimalID = a.ID
    m.OwnerID = o.ID
    m.MovementType = 1
    m.MovementDate = getdate(d["ReHomeDate"])
    a.Archived = 1
    a.ActiveMovementID = m.ID
    a.ActiveMovementDate = m.MovementDate
    a.ActiveMovementType = 1
    a.LastChangedDate = m.MovementDate
    movements.append(m)

# Run another pass through the Keeper file to update who has which animal
# and pick up anything that wasn't in AniMovement
for d in asm.csv_to_list(f"{PATH}/Keeper.csv"):
    # Find the person and animal
    if d["PetRef"] not in ppa: continue
    a = ppa[d["PetRef"]]
    if d["CustCode"] not in ppo: continue
    o = ppo[d["CustCode"]]
    if a is None or o is None: continue
    if d["KeeperDate"] == "": continue
    if d["KeeperType"] != "New Keeper": continue
    m = asm.Movement()
    m.AnimalID = a.ID
    m.OwnerID = o.ID
    m.MovementType = 1
    m.MovementDate = getdate(d["KeeperDate"])
    a.Archived = 1
    a.ActiveMovementID = m.ID
    a.ActiveMovementDate = m.MovementDate
    a.ActiveMovementType = 1
    a.LastChangedDate = m.MovementDate
    movements.append(m)

# Run another pass through the Animal file. If an animal is still on shelter
# but has AnimalST = Rehome then use CustCode to find the person
# Man this database is really inconsistent and poor.
for d in asm.csv_to_list(f"{PATH}/Animal.csv"):
    # Find the person and animal
    if d["PetRef"] not in ppa: continue
    a = ppa[d["PetRef"]]
    if d["CustCode"] not in ppo: continue
    o = ppo[d["CustCode"]]
    if a is None or o is None: continue
    if a.Archived == 1: continue
    if d["AnimalST"] != "Rehome": continue
    m = asm.Movement()
    m.AnimalID = a.ID
    m.OwnerID = o.ID
    m.MovementType = 1
    m.MovementDate = getdate(d["DateRegistered"])
    a.Archived = 1
    a.ActiveMovementID = m.ID
    a.ActiveMovementDate = m.MovementDate
    a.ActiveMovementType = 1
    a.LastChangedDate = m.MovementDate
    movements.append(m)

for d in asm.csv_to_list(f"{PATH}/Death.csv"):
    if d["PetRef"] not in ppa: continue
    a = ppa[d["PetRef"]]
    a.PutToSleep = asm.iif(d["PTS"] == "-1", 1, 0)
    a.DeceasedDate = getdate(d["DateOfDeath"])
    a.Archived = 1
    a.PTSReason = d["Notes"]
    a.PTSReasonID = asm.iif(a.PutToSleep == 1, 4, 2) # 4 = Sick/Injured, 2 = Died
    a.LastChangedDate = a.DeceasedDate

for d in asm.csv_to_list(f"{PATH}/InvoiceHistory.csv"):
    if d["CustCode"] not in ppo: continue
    o = ppo[d["CustCode"]]
    a = None
    if d["PetRef"] in ppa: a = ppa[d["PetRef"]]
    od = asm.OwnerDonation()
    od.DonationTypeID = 1
    od.DonationPaymentID = 1
    od.Date = getdate(d["Date"])
    od.OwnerID = o.ID
    if a is not None: od.AnimalID = a.ID
    od.Donation = asm.get_currency(d["Amount"])
    ownerdonations.append(od)

# Now that everything else is done, output stored records
for a in animals:
    print(a)
for l in logs:
    print(l)
for o in owners:
    print(o)
for od in ownerdonations:
    print(od)
for m in movements:
    print(m)

asm.stderr_summary(animals=animals, logs=logs, owners=owners, ownerdonations=ownerdonations, movements=movements)
asm.stderr_onshelter(animals)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")

