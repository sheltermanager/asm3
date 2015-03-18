#!/usr/bin/python

import asm

"""
Import script for kc0748 access database (almost home rescue)
9th March March, 2015
"""

# --- START OF CONVERSION ---

# The shelter's petfinder ID for grabbing animal images for adoptable animals
PETFINDER_ID = "CO145"
pf = ""
if PETFINDER_ID != "":
    pf = asm.petfinder_get_adoptable(PETFINDER_ID)

owners = {}
movements = []
animals = {}
ownerdonations = []
animalvaccinations = []

asm.setid("animal", 100)
asm.setid("animalvaccination", 100)
asm.setid("owner", 100)
asm.setid("ownerdonation", 100)
asm.setid("adoption", 100)
asm.setid("media", 100)
asm.setid("dbfs", 300)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= 100;"
print "DELETE FROM media WHERE ID >= 100;"
print "DELETE FROM dbfs WHERE ID >= 200;"
print "DELETE FROM owner WHERE ID >= 100;"
print "DELETE FROM ownerdonation WHERE ID >= 100;"
print "DELETE FROM animalvaccination WHERE ID >= 100;"
print "DELETE FROM adoption WHERE ID >= 100;"

cadoptions = asm.csv_to_list("data/kc0748_almosthome/adoptions.csv")
ccats = asm.csv_to_list("data/kc0748_almosthome/cats.csv")
cdonors = asm.csv_to_list("data/kc0748_almosthome/donordatabase.csv")
cpeople = asm.csv_to_list("data/kc0748_almosthome/people.csv")
creceipts = asm.csv_to_list("data/kc0748_almosthome/receipts.csv")
cvolunteers = asm.csv_to_list("data/kc0748_almosthome/volunteers.csv")

vaccmap = {
    "Leuk": 12,
    "ombo": 9,
    "all": 9,
    "All": 9,
    "fvrcp": 9,
    "FVCC": 9,
    "FVRC": 9,
    "FVRCP": 9,
    "FVCP": 9,
    "abies": 4,
    "elovax": 9
}

lastbroughtin = None
for d in ccats:
    # Each row contains an animal with intake info and sometimes outcome
    a = asm.Animal()
    animals[d["CatId"]] = a
    a.AnimalName = d["Name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateBroughtIn = asm.getdate_mmddyy(d["IntakeDate"])
    if a.DateBroughtIn is None:
        a.DateBroughtIn = lastbroughtin
    else:
        lastbroughtin = a.DateBroughtIn
    a.BreedID = asm.breed_id_for_name(d["CatBreed"], 261)
    a.BaseColourID = asm.colour_id_for_name(d["CatColor"])
    a.AnimalTypeID = asm.iif(d["OwnerSurrender"] == "1", 11, 12)
    a.SpeciesID = 2
    a.Sex = asm.getsex_mf(d["Sex"])
    a.DateOfBirth = asm.getdate_mmddyy(d["DOB"])
    if a.DateOfBirth is None:
        dy = 365 * asm.cint(d["AgeYrs"])
        dy += 30 * asm.cint(d["AgeMos"])
        dy += 7 * asm.cint(d["AgeWks"])
        dy += asm.cint(d["AgeDays"])
        a.DateOfBirth = asm.subtract_days(a.DateBroughtIn, dy)
    a.Neutered = asm.iif(d["SpayOrNeuteredPreviously"] == "1", 1, 0)
    if a.Neutered == 0:
        a.Neutered = asm.iif(d["Spay/NeuterDate"] != "", 1, 0)
    a.NeuteredDate = asm.getdate_mmddyy(d["Spay/NeuterDate"])
    a.AnimalComments = d["Comments"]
    a.IdentichipDate = asm.getdate_mmddyy(d["MicrochipDate"])
    if a.IdentichipDate is not None:
        a.Identichipped = 1
        a.IdentichipNumber = d["Microchip#"]
    a.CombiTestDate = asm.getdate_mmddyy(d["FIV/FELVDate"])
    if a.CombiTestDate is not None:
        a.CombiTested = 1
        a.CombiTestResult = asm.iif(d["FIVPosorNeg"] == "p", 2, 1)
        a.FLVResult = asm.iif(d["FELVPosorNeg"] == "p", 2, 1)
    a.HealthProblems = d["MedHistory"]
    a.ReasonForEntry = d["ReasonForSurrender"]
    a.TransferIn = asm.iif(d["TransferredFrom"] != "", 1, 0)
    a.IsGoodWithCats = 2
    a.IsGoodWithDogs = 2
    a.IsGoodWithChildren = 2
    a.HouseTrained = 0
    a.Size = 2
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn

    for k, v in vaccmap.iteritems():
        vd = asm.getdate_mmddyy(d["DateVaccinatedByOwner"])
        if d["TypeOfVaccinations"].find(k) != -1 and vd is not None:
            av = asm.AnimalVaccination()
            animalvaccinations.append(av)
            av.DateRequired = vd
            av.DateOfVaccination = vd
            av.VaccinationID = v
            av.Comments = d["TypeOfVaccinations"]
    
    comments = "color: %s" % d["CatColor"]
    if d["LocationWhereFound"] != "": comments += "\nfound: %s" % d["LocationWhereFound"]
    if d["TransferredTo"] != "": 
        comments += "\ntransferred to: %s %s" % (d["TransferredTo"], d["Transferred"])
        a.Archived = 1
    if d["ReturnedToOwner"] == "1":
        comments += "\nreturned to owner"
        a.Archived = 1
    if d["SurrenderedBy"] != "":
        comments += "\nsurrendered: %s %s %s %s" % (d["SurrenderedBy"], d["SurrAddress"], d["SurrDL#"], d["SurrPhone"])
    if d["Eyes"] != "": comments += "\neyes: %s" % d["Eyes"]
    if d["Ears"] != "": comments += "\neyes: %s" % d["Ears"]
    if asm.cfloat(d["Weight_oz"]) != 0: comments += "\nweight: %d %d" % (asm.cint(d["Weight_lbs"]), asm.cfloat(d["Weight_oz"]))
    if d["Mouth"] != "": comments += "\nmouth: %s" % d["Mouth"]
    if d["Nose"] != "": comments += "\nnose: %s" % d["Nose"]
    if d["Coat"] != "": comments += "\ncoat: %s" % d["Coat"]
    a.HiddenAnimalDetails = comments

    a.DeceasedDate = asm.getdate_mmddyy(d["Deceased"])
    if d["Euthanized"] == "1": a.PutToSleep = 1
    if a.DeceasedDate is not None:
        a.Archived = 1

    if d["Treatable Healthy"] == "1":
        a.AsilomarIntakeCategory = 1
    elif d["Treatable Manageable"] == "1":
        a.AsilomarIntakeCategory = 2
    elif d["Unhealthy Untreatable"] == "1":
        a.AsilomarIntakeCategory = 3

for d in cpeople:
    o = asm.Owner()
    owners[d["PerID"]] = o
    od = asm.getdate_mmddyy(d["Date"])
    if od is not None:
        o.LastChangedDate = od
        o.CreatedDate = od
    o.OwnerForeNames = d["FirstName"]
    o.OwnerSurname = d["LastName"]
    if d["SpouseName"] != "":
        o.OwnerForeNames += " and " + d["SpouseName"]
    o.OwnerAddress = d["Address"]
    o.OwnerTown = d["City"]
    o.OwnerCounty = d["State"]
    o.OwnerPostcode = d["Zip"]
    o.WorkTelephone = d["WorkPhone"]
    o.HomeTelephone = d["HomePhone"]
    o.MobileTelephone = d["CellPhone"]
    o.EmailAddress = d["EMail"]
    o.IsFosterer = asm.iif(d["Foster"] == "1", 1, 0)
    o.IsVolunteer = asm.iif(d["Volunteer"] == "1", 1, 0)
    o.ExcludeFromBulkEmail = asm.iif(d["emailOptOut"] == "1", 1, 0)
    o.IsBanned = asm.iif(d["noAdopt"] == "1", 1, 0)
    comments = ""
    if d["Occupation"] != "": comments += "\noccupation: %s" % d["Occupation"]
    if d["DOB"] != "": comments += "\ndob: %s" % d["DOB"]
    if d["EmplName"] != "": comments += "\nemplname: %s" % d["EmplName"]
    if d["EmplAddress"] != "": comments += "\nempladdr: %s" % d["EmplAddress"]
    if d["EmplPhone"] != "": comments += "\nemplphone: %s" % d["EmplPhone"]
    if d["NumberDogsCurrently"] != "0": comments += "\ndogscurrently: %s" % d["NumberDogsCurrently"]
    if d["NumberCatsCurrently"] != "0": comments += "\ncatscurrently: %s" % d["NumberCatsCurrently"]
    if d["NumberOtherPetsCurrently"] != "0": comments += "\nothercurrently: %s" % d["NumberOtherPetsCurrently"]
    if d["NumberDogsPrior"] != "0": comments += "\nnumberdogsprior: %s" % d["NumberDogsPrior"]
    if d["NumberCatsPrior"] != "0": comments += "\nnumbercatsprior: %s" % d["NumberCatsPrior"]
    if d["NumberOtherPetsPrior"] != "0": comments += "\nnumberotherprior: %s" % d["NumberOtherPetsPrior"]
    if d["PriorReasonGone"] != "": comments += "\npriorreason: %s" % d["PriorReasonGone"]
    if d["Comment"] != "": comments += "\n%s" % d["Comment"]
    o.Comments = comments

for d in cadoptions:
    if not animals.has_key(d["CatId"]): continue
    if not owners.has_key(d["PerID"]): continue
    a = animals[d["CatId"]]
    o = owners[d["PerID"]]
    if a is None or o is None: continue
    m = asm.Movement()
    m.AnimalID = a.ID
    m.OwnerID = o.ID
    m.MovementType = 1
    m.MovementDate = asm.getdate_mmddyy(d["AdoptDate"])
    m.Comments = d["Comments"]
    m.ReturnDate = asm.getdate_mmddyy(d["ReturnDate"])
    if d["ReasonForReturn"] != "":
        m.Comments += " " + d["ReasonForReturn"]
    a.Archived = 1
    a.ActiveMovementID = m.ID
    a.ActiveMovementType = 1
    a.LastChangedDate = m.MovementDate
    movements.append(m)
    if d["AdoptionFeePd"] == "1":
        od = asm.OwnerDonation()
        ownerdonations.append(od)
        od.OwnerID = o.ID
        od.AnimalID = a.ID
        od.MovementID = m.ID
        od.Date = m.MovementDate
        od.Donation = asm.get_currency(d["AdoptionFeeAmount"])
        od.DonationTypeID = 2 # Adoption Fee

    # Get the current image for this animal from PetFinder if it is on shelter
    if a.Archived == 0 and PETFINDER_ID != "" and pf != "":
        asm.petfinder_image(pf, a.ID, a.AnimalName)

for d in creceipts:
    if not owners.has_key(d["PerID"]): continue
    o = owners[d["PerID"]]
    od = asm.OwnerDonation()
    ownerdonations.append(od)
    od.OwnerID = o.ID
    od.AnimalID = 0
    od.MovementID = 0
    od.Date = asm.getdate_mmddyy(d["Date"])
    od.Donation = asm.get_currency(d["Donation$"])
    comments = ""
    if d["InMemoryOf"] != "": comments += "memory: %s" % d["InMemoryOf"]
    if d["DonationFrom"] != "": comments += "\nfrom: %s" % d["DonationFrom"]
    if d["DonatedGoods"] != "": comments += "\ngoods: %s" % d["DonatedGoods"]
    od.DonationTypeID = asm.iif(d["ReceiptType"] == "Membership", 6, 1) # Membership or donation

# Now that everything else is done, output stored records
for a in animals.itervalues():
    print a
for o in owners.itervalues():
    print o
for m in movements:
    print m
for od in ownerdonations:
    print od
for av in animalvaccinations:
    print av

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

