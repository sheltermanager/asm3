#!/usr/bin/python

import asm

"""
Import script for custom Excel for zb1415

5th July, 2017
"""

PATH = "data/zb1417_excel"

def getdate(d):
    return asm.getdate_ddmmyyyy(d)

# --- START OF CONVERSION ---

ppo = {}
owners = []
movements = []
animals = []

asm.setid("animal", 100)
asm.setid("owner", 100)
asm.setid("adoption", 100)
asm.nextyearcode = 16

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM owner WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM adoption WHERE ID >= 100 AND CreatedBy = 'conversion';"

# Customers first
for d in asm.csv_to_list("%s/customers.csv" % PATH):
    o = asm.Owner()
    owners.append(o)
    ppo[d["CustID"]] = o
    o.OwnerForeNames = ("%s %s" % (d["FName"], d["MName"])).strip()
    o.OwnerSurname = d["LName"]
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = "%s %s" % (d["Address1"], d["Address2"])
    o.OwnerTown = d["City"]
    o.OwnerCounty = d["State"]
    o.OwnerPostcode = d["ZipCode"]
    o.HomeTelephone = d["HPhone"]
    o.MobileTelephone = d["BPhone"]
    o.Comments = d["Notes"]

typemap = {
    "Dog": 2,
    "dog": 2,
    "DOG": 2,
    "Puppy": 2,
    "PUPPY": 2,
    "Cat": 11,
    "CAT": 11,
    "Kitten": 11,
    "KITTEN": 11,
    "KITEN": 11,
    "Other": 13
}

speciesmap = {
    "Dog": 1,
    "dog": 1,
    "DOG": 1,
    "Puppy": 1,
    "PUPPY": 1,
    "Cat": 2,
    "CAT": 2,
    "Kitten": 2,
    "KITTEN": 2,
    "KITEN": 2,
    "Other": 3
}

sizesmap = {
    "Small": 3,
    "Medium": 2,
    "Large": 1
}

coatmap = {
    "Medium": 0,
    "Short": 0,
    "Long": 1,
    "Wiry": 2,
    "Curly": 3
}

# Now animals
for d in asm.csv_to_list("%s/animals.csv" % PATH):
    a = asm.Animal()
    animals.append(a)

    a.AnimalTypeID = d["Type"] in typemap and typemap[d["Type"]] or 2
    a.SpeciesID = d["Type"] in speciesmap and speciesmap[d["Type"]] or 1
    a.AnimalName = d["Name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateBroughtIn = getdate(d["entries_Date"])
    if a.DateBroughtIn is None:
        a.DateBroughtIn = asm.today()
    a.DateOfBirth = asm.subtract_days(a.DateBroughtIn, 365)
    a.EstimatedDOB = 1
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    a.generateCode()
    a.ShortCode = d["AnimalID"]
    if d["Type of Entry"].find("Surrender") != -1 or d["Type of Entry"].find("Relinquish") != -1:
        a.EntryReasonID = 17 # Surrender
    elif d["Type of Entry"].find("Stray") != -1:
        a.EntryReasonID = 7 # Stray
        if a.AnimalTypeID == 2: a.AnimalTypeID = 10 # Make it a stray dog
        if a.AnimalTypeID == 11: a.AnimalTypeID = 12 # Make it a stray cat
    elif d["Type of Entry"].find("Return") != -1:
        a.EntryReasonID = 17
    elif d["Type of Entry"].find("Other Animal Shelter") != -1:
        a.EntryReasonID = 15 # Transfer from other shelter
        a.TransferIn = 1
    if d["entries_CustID"] in ppo:
        a.OriginalOwnerID = ppo[d["entries_CustID"]].ID
        a.BroughtInByOwnerID = a.OriginalOwnerID
    a.ReasonForEntry = d["Reason Surrendered"]
    if d["Location Found"].strip() != "":
        a.PickupAddress = d["Location Found"]
        a.IsPickup = 1
    a.BreedID = asm.breed_id_for_name(d["Breed"])
    if a.BreedID == 261:
        a.Breed2ID = 261
    else:
        a.Breed2ID = 442
        a.CrossBreed = 1
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    a.BaseColourID = asm.colour_id_for_name(d["Color"])
    a.HiddenAnimalDetails = "Type: %s, Breed: %s, Color: %s, Age: %s, Ears: %s, Tail: %s, Spay/Neuter: %s" % (d["Type"], d["Breed"], d["Color"], d["Age"], d["Ears"], d["Tail"], d["SpayNeuterDate"])
    if d["SpayNeuterDate"].strip() != "": a.Neutered = 1
    if d["Euthanized"] != "0":
        a.DeceasedDate = a.DateBroughtIn
        a.PTSReasonID = 2
        a.PutToSleep = 1
        a.Archived = 1
    a.AnimalComments = d["Remarks"]
    a.RabiesTag = d["RabiesTagInfo"]
    a.IsNotAvailableForAdoption = 0
    a.Size = d["Size"] in sizesmap and sizesmap[d["Size"]] or 2
    a.CoatType = d["Coat"] in coatmap and coatmap[d["Coat"]] or 1
    a.IsGoodWithCats = 2
    a.IsGoodWithDogs = 2
    a.IsGoodWithChildren = 2
    a.HouseTrained = 0

    if d["Placed"] != "0" and d["Placements_CustID"] != "":
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = ppo[d["Placements_CustID"]].ID
        m.MovementType = 1
        if d["Type of Placement"] == "Adoption":
            m.MovementType = 1
        elif d["Type of Placement"] == "Foster Care":
            m.MovementType = 2
        elif d["Type of Placement"] == "Other Animal Shelter":
            m.MovementType = 3
        elif d["Type of Placement"] == "Return to Owner":
            m.MovementType = 5
        m.MovementDate = getdate(d["Placements_Date"])
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = m.MovementType
        a.ActiveMovementDate = m.MovementDate
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

