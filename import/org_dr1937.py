#!/usr/bin/python

import asm

"""
Import script for dr1937 csv files

3rd July, 2019
"""

START_ID = 500

FILENAME = "/home/robin/tmp/asm3_import_data/dr1937_csv/master.csv"

def getdate(d):
    return asm.getdate_mmddyy(d)

# --- START OF CONVERSION ---

owners = []
ownerdonations = []
movements = []
animals = []
animaltests = []
animalmedicals = []
animalvaccinations = []
logs = []

asm.setid("animal", START_ID)
asm.setid("animalmedical", START_ID)
asm.setid("animalmedicaltreatment", START_ID)
asm.setid("animalvaccination", START_ID)
asm.setid("log", START_ID)
asm.setid("owner", START_ID)
asm.setid("ownerdonation", START_ID)
asm.setid("adoption", START_ID)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= %s;" % START_ID
print "DELETE FROM animalmedical WHERE ID >= %s;" % START_ID
print "DELETE FROM animalmedicaltreatment WHERE ID >= %s;" % START_ID
print "DELETE FROM animalvaccination WHERE ID >= %s;" % START_ID
print "DELETE FROM log WHERE ID >= %s;" % START_ID
print "DELETE FROM owner WHERE ID >= %s;" % START_ID
print "DELETE FROM ownerdonation WHERE ID >= %s;" % START_ID
print "DELETE FROM adoption WHERE ID >= %s;" % START_ID

# Create an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname

def create_vacc(vaccname, vaccdate, vaccrenew):
    vacctypes = {
        "Rabies": 4,
        "Distemper": 1,
        "Lepto": 3,
        "Bordetella": 6,
        "Influenza": 10
    }
    given = getdate(vaccdate)
    if given is not None:
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.AnimalID = a.ID
        av.VaccinationID = vacctypes[vaccname]
        av.DateRequired = given
        av.DateOfVaccination = given
    nx = getdate(vaccrenew)
    if nx is not None and nx > asm.now():
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.AnimalID = a.ID
        av.VaccinationID = vacctypes[vaccname]
        av.DateRequired = nx
        av.DateOfVaccination = None

# Records
for d in asm.csv_to_list(FILENAME, remove_non_ascii=True):
    # Each row contains an animal with intake and outcome info:
    a = asm.Animal()
    flags = ""
    animals.append(a)
    a.SpeciesID = asm.species_id_for_name(d["Type"])
    a.AnimalTypeID = 11
    if a.SpeciesID == 1: a.AnimalTypeID = 2 # dog
    if a.SpeciesID == 2: a.AnimalTypeID = 11 # unwanted cat
    a.AnimalName = d["Name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateBroughtIn = getdate(d["Date In"]) or asm.today()
    if d["DOB"].strip() != "":
        a.DateOfBirth = getdate(d["DOB"])
    if a.DateOfBirth is None:
        a.DateOfBirth = asm.subtract_days(a.DateBroughtIn, 365)
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    a.ShortCode = d["File"]
    a.ShelterCode = str(a.ID) + " " + d["File"]
    a.BreedID = asm.breed_id_for_name(d["Breed"].replace(" mix", ""))
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    if d["Breed"].find("mix") != -1:
        a.CrossBreed = 1
        a.Breed2ID = 442
        a.BreedName = asm.breed_name(a.BreedID, a.Breed2ID)
    a.BaseColourID = asm.colour_id_for_name(d["Color"])

    a.Sex = asm.getsex_mf(d["Male Female"])
    a.Weight = asm.cint(d["Weight"].replace("lbs", "").strip())

    if a.Weight > 0:
        l = asm.Log()
        logs.append(l)
        l.LogTypeID = 4 # Weight
        l.LinkID = a.ID
        l.LinkType = 0
        l.Date = a.DateBroughtIn
        l.Comments = d["Weight"]

    a.NeuteredDate = getdate(d["Spay Neuter Date"])
    if a.NeuteredDate is not None: a.Neutered = 1
    a.HealthProblems = d["Medical Notes"]

    create_vacc("Rabies", d["Rabies Date"], d["Rabies Renewal"])
    create_vacc("Distemper", d["Distemper Parvo Date"], d["Distemper Parvo Renewal"])
    create_vacc("Lepto", d["Lepto Date"], d["Lepto Renewal"])
    create_vacc("Influenza", d["Influenza Date"], d["Influenza Renewal"])
    create_vacc("Bordetella", d["Bordetella Date"], d["Bordetella Renewal"])
    
    a.HeartwormTestDate = getdate(d["HW Test"])
    if a.HeartwormTestDate is not None: 
        a.HeartwormTested = 1
        a.HeartwormTestResult = 1
        if d["HW Test Results"].find("ositive") != -1: a.HeartwormTestResult=2

    deworm = getdate(d["Dewormed"])
    if deworm is not None:
        animalmedicals.append( asm.animal_regimen_single(a.ID, deworm, "Dewormer", "Dose") )

    flea = getdate(d["Flea Treatment"])
    if flea is not None:
        animalmedicals.append( asm.animal_regimen_single(a.ID, flea, "Flea treatment", "Dose") )

    a.IdentichipNumber = d["Microchip Info"]
    if a.IdentichipNumber != "": a.Identichipped = 1
    a.IsGoodWithCats = asm.good_with(d["Good w/ cats"])
    a.IsGoodWithDogs = asm.good_with(d["Good w/ dogs"])
    a.IsGoodWithChildren = asm.good_with(d["Good w/ children"])
    a.HouseTrained = 0

    comments = "Breed: " + d["Breed"]
    comments += "\nType: " + d["Type"]
    comments += "\nColor: " + d["Color"]
    comments += "\nLocation: " + d["Location"] + " " + d["Haven location"]
    comments += "\nTr.Color: " + d["Tcolor"]
    comments += "\nGood with cats: " + d["Good w/ cats"]
    comments += "\nGood with dogs: " + d["Good w/ dogs"] + " " + d["Good w/ dogs notes"]
    comments += "\nGood with kids: " + d["Good w/ children"]
    comments += "\nEnergy: " + d["Energy level"]
    comments += "\nBehavior: " + d["Behavior Notes"]
    comments += "\nKennel Card Notes: " + d["Kennel Card Notes"]
    a.HiddenAnimalDetails = comments
    a.AnimalComments = d["About"]

    if d["Where from?"].startswith("DV"):
        flags += "Domestic Violence|"

    if d["Pit?"] == "Yes":
        flags += "Pitbull"

    asm.additional_field("CollarColor", 6, a.ID, d["Tcolor"])

    if d["Kennel Card Notes"].strip() != "":
        l = asm.Log()
        logs.append(l)
        l.LogTypeID = 3 # History
        l.LinkID = a.ID
        l.LinkType = 0
        l.Date = a.DateBroughtIn
        l.Comments = "Kennel Card: " + d["Kennel Card Notes"]

    if d["Behavior Notes"].strip() != "":
        l = asm.Log()
        logs.append(l)
        l.LogTypeID = 3 # History
        l.LinkID = a.ID
        l.LinkType = 0
        l.Date = a.DateBroughtIn
        l.Comments = "Behavior: " + d["Behavior Notes"]

    l = asm.Log()
    logs.append(l)
    l.LogTypeID = 3 # History
    l.LinkID = a.ID
    l.LinkType = 0
    l.Date = a.DateBroughtIn
    l.Comments = "Diet: Food-Dry (cups 2x/day) = %s %s" % ( d["Food-Dry (cups 2x/day)"], d["Food-Special"] )

    dateout = getdate(d["Date Out"])

    if dateout is not None and d["Adoption Status"] == "Adopted":
        o = asm.Owner()
        owners.append(o)
        o.OwnerForeNames = d["First"]
        o.OwnerSurname = d["Last"]
        o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
        o.OwnerAddress = d["Address"]
        o.OwnerTown = d["City"]
        o.OwnerCounty = d["State"]
        o.OwnerPostcode = d["Zip"]
        o.EmailAddress = d["Email"]
        o.HomeTelephone = d["Phone"]
        o.MobileTelephone = d["Phone #2"]

        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = dateout
        m.Comments = d["Notes from New Owners"]
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 1
        a.LastChangedDate = dateout
        movements.append(m)

        # If there's $100 in the Spay/Neu Dep column, that means a deposit was
        # taken for spaying/neutering. 
        # If the word "returned" is present, make it $0 (eg: $100 returned to adopter)
        # If the word "NOT" is present, do nothing (eg: $100 dep NOT taken)
        # If $100 is not present, do nothing
        if d["Spay/Neu Dep"].startswith("$100") and d["Spay/Neu Dep"].find("NOT") == -1:
            amt = 10000
            if d["Spay/Neu Dep"].find("returned") != -1: amt = 0
            od = asm.OwnerDonation()
            od.DonationTypeID = 7
            od.DonationPaymentID = 1
            od.Date = m.MovementDate
            od.OwnerID = o.ID
            od.AnimalID = a.ID
            od.Donation = amt
            od.Comments = d["Spay/Neu Dep"]
            ownerdonations.append(od)

    if dateout is not None and d["Adoption Status"] == "Returned to owner":
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = uo.ID
        m.MovementType = 5
        m.MovementDate = dateout
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 5
        a.LastChangedDate = dateout
        movements.append(m)

    elif dateout is not None and d["Adoption Status"] == "Deceased":
        a.PutToSleep = 0
        a.DeceasedDate = dateout
        a.Archived = 1
        a.PTSReasonID = 2
        a.LastChangedDate = dateout

    elif dateout is not None and d["Adoption Status"].startswith("Euth"):
        a.PutToSleep = 1
        a.DeceasedDate = dateout
        a.Archived = 1
        a.PTSReasonID = 2
        a.LastChangedDate = dateout


# Run back through the animals, if we have any that are still
# on shelter after 1 year, add an adoption to an unknown owner
# asm.adopt_older_than(animals, movements, uo.ID, 365)

# Go back through the animals and mark anything on shelter as non-shelter
#for a in animals:
#    if a.Archived == 0:
#        a.NonShelterAnimal = 1
#        a.Archived = 1

# Now that everything else is done, output stored records
for k,v in asm.locations.iteritems():
    print v
for a in animals:
    print a
for am in animalmedicals:
    print am
for at in animaltests:
    print at
for av in animalvaccinations:
    print av
for o in owners:
    print o
for o in ownerdonations:
    print o
for m in movements:
    print m
for l in logs:
    print l

asm.stderr_summary(animals=animals, animaltests=animaltests, animalmedicals=animalmedicals, animalvaccinations=animalvaccinations, logs=logs, owners=owners, ownerdonations=ownerdonations, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

