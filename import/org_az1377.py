#!/usr/bin/python

import asm, datetime

"""
Import script for custom Excel for az1377

10th July, 2017
"""

FILENAME = "data/az1377_excel.csv"

def getdate(d):
    return asm.getdate_guess(d)

def getpartdate(ye, mo):
    """ creates a date at 01/m/y """
    months = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12
    }
    d = 1
    m = 1
    if mo.strip() != "" and mo in months:
        m = months[mo]
    y = asm.cint(ye)
    if y == 0: return None
    return datetime.datetime(y, m, d)

# --- START OF CONVERSION ---

owners = []
movements = []
animals = []

asm.setid("animal", 100)
asm.setid("owner", 100)
asm.setid("adoption", 100)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM owner WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM adoption WHERE ID >= 100 AND CreatedBy = 'conversion';"

# Create an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname

# Each row contains an animal with possible adoption and owner info
for d in asm.csv_to_list(FILENAME):

    a = asm.Animal()
    animals.append(a)
    # ACC Number
    if d["ACC Number"].strip() != "":
        asm.additional_field("accno", 2, a.ID, d["ACC Number"])
    # animaltype is upstairs or downstairs, upstairs = 42, downstairs = 43
    if d["Cat Cafe Down (Y/N)"] == "Y":
        a.AnimalTypeID = 43
        a.generateCode("D")
    else:
        a.AnimalTypeID = 42
        a.generateCode("U")
    # all cats
    a.SpeciesID = 2
    a.ShortCode = d["BBAWC Animal ID #"]
    a.AnimalName = d["Name (s) of Animal (list all names)"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateBroughtIn = getpartdate(d["Intake Year"], d["Intake Month"])
    if a.DateBroughtIn is None:
        a.DateBroughtIn = datetime.datetime(2007, 1, 1)
    a.DateOfBirth = getdate(d["Date of Birth (or age)"])
    if a.DateOfBirth is None:
        a.DateOfBirth = asm.subtract_days(a.DateBroughtIn, 365)
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    comments = ""
    status = d["Status (Adopted Died Foster etc.)"]
    if status != "":
        comments = "Status: %s" % d["Status (Adopted Died Foster etc.)"]
    exitdate = getpartdate(d["Year Closed"], d["Month Closed"])
    if status.find("Deceased") != -1:
        a.Archived = 1
        a.DeceasedDate = exitdate
        a.PutToSleep = 0
        a.PTSReasonID = 2
    if status.find("TNR") != -1 and exitdate is not None:
        m = asm.Movement()
        m.AnimalID = a.ID
        m.MovementType = 7
        m.MovementDate = exitdate
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 7
        movements.append(m)
    sx = d["Sex (M, F, N, S)"].upper()
    if sx.find("M") != -1:
        a.Sex = 1
    if sx.find("F") != -1:
        a.Sex = 0
    if sx.find("N") != -1:
        a.Neutered = 1
        a.Sex = 1
    if sx.find("S") != -1:
        a.Neutered = 1
        a.Sex = 0
    a.Markings = d["Description"]
    if d["Rescuer"] != "":
        comments += "\nRescuer: %s" % d["Rescuer"]
    if d["Current Location of Animal (if not adopted)"] != "":
        comments += "\nCurrent Location: %s" % d["Current Location of Animal (if not adopted)"]
    comments += "\nSex: %s" % sx
    if d["Exam Date(s)"] != "":
        comments += "\nExam Date: %s" % d["Exam Date(s)"]
    if d["Snap Test date"] != "":
        comments += "\nSnap Test date: %s" % d["Snap Test date"]
    if d["Snap Test result"] != "":
        comments += "\nSnap Test result: %s" % d["Snap Test result"]
    if d["FVRCP vaccine(s)"] != "":
        comments += "\nFVRCP vaccine(s): %s" % d["FVRCP vaccine(s)"]
    if d["Rabies Vaccine"] != "":
        comments += "\nRabies Vaccine: %s" % d["Rabies Vaccine"]
    if d["Spay/ Neuter Date"] != "":
        comments += "\nSpay/Neuter Date: %s" % d["Spay/ Neuter Date"]
        a.NeuteredDate = getdate(d["Spay/ Neuter Date"])
    if d["Parasite Tx"] != "":
        comments += "\nParasite Tx: %s" % d["Parasite Tx"]
    if d["Microchip"] != "":
        a.IdentichipNumber = d["Microchip"]
        a.Identichipped = 1
    a.AnimalComments = d["Other Info/ Notes about Animal"]
    a.HiddenAnimalDetails = comments

    a.IsNotAvailableForAdoption = 0
    a.Size = 2
    a.EntryReasonID = 17 # Surrender
    a.IsGoodWithCats = 2
    a.IsGoodWithDogs = 2
    a.IsGoodWithChildren = 2
    a.HouseTrained = 0
    a.BreedID = 261
    a.Breed2ID = a.BreedID
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    a.CrossBreed = 0

    o = None
    if d["Title"] != "":
        o = asm.Owner()
        owners.append(o)
        o.OwnerTitle = d["Title"]
        o.OwnerForeNames = d["First Name"]
        o.OwnerSurname = d["Last Name"]
        o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
        o.OwnerAddress = d["Street Address"]
        o.OwnerTown = d["City"]
        o.OwnerCounty = d["State"]
        o.OwnerPostcode = d["Zip"]
        o.EmailAddress = d["Email Address"]
        o.HomeTelephone = d["Home Phone"]
        o.WorkTelephone = d["Work phone"]
        o.MobileTelephone = d["Cell Phone"]

    if exitdate is not None and o is not None:
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = exitdate
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 1
        movements.append(m)
        comments = "Total fee: %s" % d["Total Fee, Payment type, check #"]
        comments += "\nMicrochip fee: %s" % d["Microchip Fee"]
        comments += "\nS/N Fee: %s" % d["S/N Fee (Put N/A if already Fixed)"]
        comments += "\nAdoption Fee: %s" % d["Adoption Fee"]
        comments += "\nDonation Amount: %s" % d["Donation Amount"]
        comments += "\nBBAWC Rep: %s" % d["BBAWC Representative"]
        comments += "\nAdoption Notes: %s" % d["Adoption Notes"]
        m.Comments = comments

# Run back through the animals, if we have any that are still
# on shelter after 1 year, add an adoption to an unknown owner
for a in animals:
    if a.Archived == 0 and a.DateBroughtIn < asm.subtract_days(asm.now(), 365):
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
for o in owners:
    print o
for m in movements:
    print m

asm.stderr_summary(animals=animals, owners=owners, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

