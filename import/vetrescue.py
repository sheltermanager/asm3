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
PATH = "/home/robin/tmp/asm3_import_data/vr_sm2963"
SHELTER_CUSTCODE = "Southampton" # do not create adoption movements to this person

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
movements = []
animals = []
ppa = {}
ppo = {}

asm.setid("animal", START_ID)
asm.setid("owner", START_ID)
asm.setid("adoption", START_ID)

print("\\set ON_ERROR_STOP\nBEGIN;")
print("DELETE FROM animal WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM owner WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM adoption WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)

# Create an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname

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
    o.IsStaff = asm.iif(d["Staff"] == "Y", 1, 0)
    gdpr = []
    if d["FundPhone"] == "Y": gdpr.append("phone")
    if d["FundSMS"] == "Y": gdpr.append("sms")
    if d["FundEmail"] == "Y": gdpr.append("email")
    if d["FundPost"] == "Y": gdpr.append("post")
    o.GDPRContactOptIn = ",".join(gdpr)

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

# Use rehoming list to create the adoption movements
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

for d in asm.csv_to_list(f"{PATH}/Death.csv"):
    if d["PetRef"] not in ppa: continue
    a = ppa[d["PetRef"]]
    a.PutToSleep = asm.iif(d["PTS"] == "-1", 1, 0)
    a.DeceasedDate = getdate(d["DateOfDeath"])
    a.Archived = 1
    a.PTSReason = d["Notes"]
    a.PTSReasonID = asm.iif(a.PutToSleep == 1, 4, 2) # 4 = Sick/Injured, 2 = Died
    a.LastChangedDate = a.DeceasedDate

# Now that everything else is done, output stored records
for a in animals:
    print(a)
for o in owners:
    print(o)
for m in movements:
    print(m)

asm.stderr_summary(animals=animals, owners=owners, movements=movements)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")

