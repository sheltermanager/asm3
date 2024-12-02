#!/usr/bin/env python3

import asm, os

"""
Import script for RescueConnection file exports. RC give people a zip file containing .xls files of the data.

Run this script to convert:

#!/bin/sh
for i in *.xls; do ssconvert $i $i.csv; done

29th November, 2024
"""

START_ID = 200

PATH = "/home/robin/tmp/asm3_import_data/rc_kd3359"

PICTURE_IMPORT = False
PICTURES = f"{PATH}/photos/final"

def getdate(d, noblanks=False):
    rv = asm.getdate_guess(d)
    if noblanks and rv is None: rv = asm.now()
    return rv

def getelements(s):
    """ 
    Parses the encoded strings from rescueconnection
    These use asterisk as a separator and have a label first followed by a colon:
    * Home: Address1, Address2, Address3 * Work: Address1, Address2, Address3
    becomes [ [ "Address1", "Address2", "Address3" ], [ "Address1", "Address2", "Address3" ] ]
    * Primary: (123) 1234-209 * Work: (321) 0912-093
    becomes [ [ "(123) 1234-209" ], [ "(321) 0912-093" ]]
    """
    if s is None: return []
    outer = []
    for i in s.split("*"):
        s = s[s.find(":")+1:] # only interested in elements after the colon
        inner = []
        for x in s.split(","):
            inner.append(x.strip())
        outer.append(inner)
    return outer

def getaddress(s):
    """
    Gets the first address from s and returns address, city, state, zipcode as a tuple
    """
    addresses = getelements(s)
    if len(addresses) == 0: return ("", "", "", "")
    a = addresses[0]
    if len(a) < 3: return ("", "", "", "")
    lastone = a[-1]
    lv = lastone.split(" ", 1)
    state = ""
    zipcode = ""
    if len(lv) == 2:
        state = lv[0]
        zipcode = lv[1]
    elif len(lv) == 1:
        state = lv[0]
    city = a[-2]
    add = a[-3]
    return (add, city, state, zipcode)

# --- START OF CONVERSION ---

logs = []
owners = []
movements = []
animals = []
animalcontrol = []
animalmedicals = []

ppa = {}
ppac = {}
ppo = {}

asm.setid("animal", START_ID)
asm.setid("animalcontrol", START_ID)
asm.setid("animalmedical", START_ID)
asm.setid("animalmedicaltreatment", START_ID)
asm.setid("owner", START_ID)
asm.setid("adoption", START_ID)
asm.setid("incidenttype", START_ID)
asm.setid("log", START_ID)
if PICTURE_IMPORT: asm.setid("media", START_ID)
if PICTURE_IMPORT: asm.setid("dbfs", START_ID)

print("\\set ON_ERROR_STOP\nBEGIN;")
print(f"DELETE FROM animal WHERE ID >= {START_ID} AND CreatedBy = 'conversion';")
print(f"DELETE FROM animalcontrol WHERE ID >= {START_ID} AND CreatedBy = 'conversion';")
print(f"DELETE FROM animalmedical WHERE ID >= {START_ID} AND CreatedBy = 'conversion';")
print(f"DELETE FROM animalmedicaltreatment WHERE ID >= {START_ID} AND CreatedBy = 'conversion';")
print(f"DELETE FROM incidenttype WHERE ID >= {START_ID};")
print(f"DELETE FROM log WHERE ID >= {START_ID} AND CreatedBy = 'conversion';")
print(f"DELETE FROM owner WHERE ID >= {START_ID} AND CreatedBy = 'conversion';")
print(f"DELETE FROM adoption WHERE ID >= {START_ID} AND CreatedBy = 'conversion';")
if PICTURE_IMPORT: print(f"DELETE FROM media WHERE ID >= {START_ID};")
if PICTURE_IMPORT: print(f"DELETE FROM dbfs WHERE ID >= {START_ID};")

# Create an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname

# People
for d in asm.csv_to_list(f"{PATH}/People.xls.csv", strip=True, remove_non_ascii=True):
    # Each row contains a person
    o = asm.Owner()
    owners.append(o)
    name = d["FullName"].split(",")
    o.OwnerSurname = name[0].strip()
    if len(name) > 1:
        o.OwnerForeNames = name[1].strip()
        o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    if d["Type"] == "Company":
        o.OwnerType = 1
        o.OwnerName = o.OwnerSurname
    ppo[o.OwnerName] = o
    o.IdentificationNumber = d["IDNumber"]
    address, city, state, zipcode = getaddress(d["CurrentAddresses"])
    phones = getelements(d["CurrentPhones"])
    emails = getelements(d["CurrentEMails"])
    o.OwnerAddress = address
    o.OwnerTown = city
    o.OwnerCounty = state
    o.OwnerPostcode = zipcode
    if len(emails) > 0: o.EmailAddress = emails[0][0]
    if len(phones) > 0: o.MobileTelephone = phones[0][0]

# Animals
for d in asm.csv_to_list(f"{PATH}/Animals.xls.csv", strip=True, remove_non_ascii=True):
    a = asm.Animal()
    animals.append(a)
    stray = False
    if "Entry Category" in d and d["Entry Category"] == "Stray": stray = True
    if "LatestIntake" in d and (d["LatestIntake"].find("Stray") != -1 or d["LatestIntake"].find("Impound") != -1): stray = True
    if d["Species"] == "Cat":
        a.AnimalTypeID = 11 # Unwanted Cat
        if stray:
            a.AnimalTypeID = 12 # Stray Cat
    elif d["Species"] == "Dog":
        a.AnimalTypeID = 2 # Unwanted Dog
        if stray:
            a.AnimalTypeID = 10 # Stray Dog
    else:
        a.AnimalTypeID = 40 # Misc
    a.SpeciesID = asm.species_id_for_name(d["Species"])
    a.AnimalName = d["Name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.ShelterCode = d["ID"].strip()
    a.ShortCode = a.ShelterCode
    a.IdentichipNumber = d["Chip"].strip()
    if a.IdentichipNumber != "": a.Identichipped = 1
    a.Sex = asm.getsex_mf(d["Gender"])
    asm.breed_ids(a, d["PrimaryBreed"], d["SecondaryBreed"])
    a.Neutered = d["Altered"] == "Yes" and 1 or 0
    a.IdentichipNumber = d["Chip"]
    if a.IdentichipNumber != "": a.Identichipped = 1
    a.BaseColourID = asm.colour_id_for_name(d["PrimaryColor"])
    a.Size = 2 
    if d["AnimalSize"] == "Large": a.Size = 1
    if d["AnimalSize"] == "Extra-large": a.Size = 0
    if d["AnimalSize"] == "Small": a.Size = 3
    a.Weight = asm.atof(d["Weight"])
    if "Declawed" in d: a.Declawed = d["Declawed"] == "Yes" and 1 or 0
    if "Housetrained" in d: a.HouseTrained = d["Housetrained"] == "Yes" and 2 or 1
    if "SpecialNeeds" in d: a.HasSpecialNeeds = d["SpecialNeeds"] == "Yes" and 1 or 0
    if "Needs home without small children" in d: a.GoodWithChildren = d["Needs home without small children"] == "Yes" and 1 or 0
    if "Needs home without cats" in d: a.GoodWithCats = d["Needs home without cats"] == "Yes" and 1 or 0
    if "Needs home without dogs" in d: a.GoodWithDogs = d["Needs home without dogs"] == "Yes" and 1 or 0
    if "Known issues" in d: a.HealthProblems = d["Known issues"]
    ec = ""
    if "Entry Category" in d: ec = d["Entry Category"].strip().lower()
    if "LatestIntake" in d: ec = d["LatestIntake"].strip().lower()
    if ec.find("stray") != -1:
        a.EntryReasonID = 7
        a.EntryTypeID = 2
    elif ec.find("surrender") != -1:
        a.EntryReasonID = 17
        a.EntryTypeID = 1
    elif ec.find("born") != -1:
        a.EntryReasonID = 13
        a.EntryTypeID = 5
    elif ec.find("transfer") != -1:
        a.EntryReasonID = 15
        a.EntryTypeID = 3
        a.TransferIn = 1
    if "Source/origin" in d: a.ReasonForEntry = d["Source/origin"]
    if "Full description" in d: a.AnimalComments = d["Full description"]
    if "Description" in d: a.AnimalComments = d["Description"]

    a.DateBroughtIn = getdate(d["LatestIntake"]) or asm.today()
    age = d["Age"]
    if age.find("/") != -1 and age.find("DOB: ") != -1:
        age = age[age.find("DOB: ")+5:]
        age = age.replace(")", "")
        a.DateOfBirth = getdate(age)
    if a.DateOfBirth is None:
        a.DateOfBirth = asm.subtract_days(a.DateBroughtIn, 365)
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn

    hcomments = "\nLatestIntake: " + d["LatestIntake"]
    hcomments += "\nBreed: " + d["PrimaryBreed"] + "/" + d["SecondaryBreed"]
    hcomments += "\nColor: " + d["PrimaryColor"]
    hcomments += "\nLatestOutcome: " + d["LatestOutcome"]
    a.HiddenAnimalDetails = hcomments

    dd = a.DateBroughtIn
    if "Disposition date" in d: getdate(d["Disposition date"])
    latestin = d["LatestIntake"].strip()
    latestout = d["LatestOutcome"].strip()
    o = uo
    if d["CurrentGuardian"] in ppo: o = ppo[d["CurrentGuardian"]]
    if latestout.startswith("Adopt"):
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = dd
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = m.MovementType
        a.LastChangedDate = dd
        movements.append(m)
    elif latestout.startswith("Release") or latestout.startswith("Returned to owner") or latestout.startswith("Redemption"):
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 5
        m.MovementDate = dd
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = m.MovementType
        a.LastChangedDate = dd
        movements.append(m)
    elif latestout.startswith("Transfer") or latestout.startswith("Move"):
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 3
        m.MovementDate = dd
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = m.MovementType
        a.LastChangedDate = dd
        movements.append(m)
    elif latestout.startswith("Died"):
        a.PutToSleep = 0
        a.PTSReasonID = 2
        a.DeceasedDate = dd
        a.Archived = 1
    elif latestout.startswith("Euthanasia"):
        a.PutToSleep = 1
        a.PTSReasonID = 2
        a.DeceasedDate = dd
        a.Archived = 1
    elif latestin.startswith("N/A"):
        a.NonShelterAnimal = 1
        a.Archived = 1
        if o: 
            a.OriginalOwnerID = o.ID
            a.OwnerID = a.OriginalOwnerID
    elif latestout.startswith("N/A"):
        a.Archived = 0
    else:
        asm.stderr(f"unrecognised outcome: {di}")
    # Does this animal have an image? If so, add media/dbfs entries for it
    if PICTURE_IMPORT:
        imdata = None
        for i in range(0, 3):
            fname = "%s/%s-%s.jpg" % (PICTURES, a.ShelterCode, i)
            if os.path.exists(fname):
                with open(fname, "rb") as f:
                    asm.animal_image(a.ID, f.read())

# Medications
for d in asm.csv_to_list(f"{PATH}/Medications.xls.csv", strip=True, remove_non_ascii=True):
    animalmedicals.append( asm.animal_regimen_single(a.ID, getdate(d["BeginDate"]), d["Drug"], d["Dose"], d["Instructions"]) )

# Incidents
for d in asm.csv_to_list(f"{PATH}/Legal_AllItems.xls.csv", strip=True, remove_non_ascii=True):
    ac = asm.AnimalControl()
    animalcontrol.append(ac)
    ppac[d["IDNumber"]] = ac
    ac.IncidentTypeID = asm.incidenttype_id_for_name(d["ItemType"], True)
    calldate = getdate(d["Opened"])
    if calldate is None: calldate = asm.now()
    ac.CallDateTime = calldate
    ac.IncidentDateTime = calldate
    ac.DispatchDateTime = calldate
    ac.CompletedDate = getdate(d["Closed"])
    if ac.CompletedDate is None: ac.CompletedDate = calldate
    ac.IncidentCompletedID = 5
    comments = "case: %s\n" % d["AssociatedCase"]
    comments += "\n%s" % d["DescriptionOrNotes"]
    ac.CallNotes = comments
    ac.Sex = 2
    """
    if "ANIMALKEY" in row:
        if row["ANIMALKEY"] in ppa:
            a = ppa[row["ANIMALKEY"]]
            animalcontrolanimals.append("INSERT INTO animalcontrolanimal (AnimalControlID, AnimalID) VALUES (%s, %s);" % (ac.ID, a.ID))
    """

# Incident logs
for d in asm.csv_to_list(f"{PATH}/Legal_Cases_History.xls.csv", strip=True, remove_non_ascii=True):
    if d["CaseNumber"] not in ppac: continue
    ac = ppac[d["CaseNumber"]]
    l = asm.Log()
    logs.append(l)
    l.LogTypeID = 3
    l.LinkID = ac.ID
    l.LinkType = 6
    l.Date = getdate(d["LogDate"])
    if l.Date is None:
        l.Date = asm.now()
    l.Comments = d["Description"]
for d in asm.csv_to_list(f"{PATH}/Legal_Cases_Statements.xls.csv", strip=True, remove_non_ascii=True):
    if d["CaseNumber"] not in ppac: continue
    ac = ppac[d["CaseNumber"]]
    l = asm.Log()
    logs.append(l)
    l.LogTypeID = 3
    l.LinkID = ac.ID
    l.LinkType = 6
    l.Date = getdate(d["StatementDate"])
    if l.Date is None:
        l.Date = asm.now()
    statement = "Statement taken by %s [%s]: %s" % (d["StatementTakenBy"], d["Notes"], d["StatementText"] )
    l.Comments = statement

# Run back through the animals, if we have any that are still
# on shelter after 1 year, add an adoption to an unknown owner
# asm.adopt_older_than(animals, movements, uo.ID, 365)

# Now that everything else is done, output stored records
for k, v in asm.incidenttypes.items():
    if v.ID >= START_ID: print(v)
for a in animals:
    print(a)
for ac in animalcontrol:
    print(ac)
for am in animalmedicals:
    print(am)
for l in logs:
    print(l)
for o in owners:
    print(o)
for m in movements:
    print(m)

#asm.stderr_allanimals(animals)
#asm.stderr_onshelter(animals)
asm.stderr_summary(animals=animals, animalcontrol=animalcontrol, animalmedicals=animalmedicals, logs=logs, owners=owners, movements=movements)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")
