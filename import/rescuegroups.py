#!/usr/bin/python3

import asm, os

"""
Import module to read from rescuegroups CSV export.

Need to create the Animals.csv, Contacts.csv and Adoptions.csv files.

This is done with Reports, then "Create a Custom Report", choose all of the fields
(139) from the Animal section. This is the only way to get all rows as their built
in Animals (All Fields) report now requires you to choose a status.
Choose "Run Report", then while it's running click "Export Data", then "Export Report" 
which will give you Animals.csv

Do the same again, but this time for all Contact fields (33).

Then again for Adoption fields (12), but also include from the Adopters section the
First Name and Last Name fields, as well as Animal ID from the animals section.

I think if people haven't paid for their "Data Management Service" they aren't allowed to
run any reports. This export will also work with CSVs extracted from Animals->Animal List,
change the View to Export and then hit Export as CSV.

"""

PATH = "/home/robin/tmp/asm3_import_data/rg_cf3099"

DEFAULT_BREED = 261 # default to dsh

IMPORT_PICTURES = False 
RG_IMG_LINK = "https://cdn.rescuegroups.org{name}" # To resolve URLs from the "Picture X" field of imports.

animals = []
owners = []
ownerdonations = []
movements = []

ppa = {}
ppo = {}
ppocid = {}

asm.setid("adoption", 100)
asm.setid("animal", 100)
asm.setid("owner", 100)
asm.setid("ownerdonation", 100)
if IMPORT_PICTURES:
    asm.setid("media", 100)
    asm.setid("dbfs", 300)

def getdate(s):
    return asm.getdate_mmddyyyy(s)

def getimage(name, a):
    """
    Retrieves the image with name and outputs the SQL for it. 
    """
    if not IMPORT_PICTURES: return
    if name is None or name.strip() == "": return
    picurl = RG_IMG_LINK
    picurl = picurl.replace("{name}", name)
    imdata = asm.load_image_from_url(picurl)
    if imdata is not None:
        asm.animal_image(a.ID, imdata)

def size_id_for_name(name):
    return {
        "": 3, 
        "LARGE": 1,
        "SMALL": 2,
        "MEDIUM": 3, 
        "X-LARGE": 0
    }[name.upper().strip()]

uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = "Unknown Owner"
uo.Comments = "Catchall for adopted animal data from RescueGroups"

print("\\set ON_ERROR_STOP\nBEGIN;")
print("DELETE FROM adoption WHERE ID >= 100;")
print("DELETE FROM animal WHERE ID >= 100;")
print("DELETE FROM owner WHERE ID >= 100;")
print("DELETE FROM ownerdonation WHERE ID >= 100;")
if IMPORT_PICTURES:
    print("DELETE FROM media WHERE ID >= 100;")
    print("DELETE FROM dbfs WHERE ID >= 300;")

if os.path.exists("%s/Contacts.csv" % PATH):
    for d in asm.csv_to_list("%s/Contacts.csv" % PATH):
        # Each row contains a person
        o = asm.Owner()
        owners.append(o)
        o.OwnerForeNames = d["First Name"].strip()
        o.OwnerSurname = d["Last Name"].strip()
        o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
        o.OwnerAddress = d["Address"]
        o.OwnerTown = d["City"]
        o.OwnerCounty = d["State"]
        if "Zipcode" in d: o.OwnerPostcode = d["Zipcode"]
        if "Zip/Postal Code" in d: o.OwnerPostcode = d["Zip/Postal Code"]
        o.EmailAddress = d["Email"]
        o.HomeTelephone = d["Phone (Home)"]
        o.WorkTelephone = d["Phone (Home)"]
        o.MobileTelephone = d["Phone (Cell)"]
        o.Comments = d["Comment"]
        if "Groups" in d:
            if d["Groups"].find("Do Not Adopt") != -1: o.IsBanned = 1
            if d["Groups"].find("Other Rescue") != -1: o.IsShelter = 1
            if d["Groups"].find("Caretaker/Foster") != -1: o.IsFosterer = 1
            if d["Groups"].find("Volunteer") != -1: o.IsVolunteer = 1
            if d["Groups"].find("Microchip Clinic") != -1: o.IsVet = 1
        ppo[o.OwnerName] = o
        ppocid[d["Contact ID"]] = o

acsv = asm.csv_to_list("%s/Animals.csv" % PATH)
for i, d in enumerate(acsv):
    if d["Status"] == "Deleted": continue
    if d["Animal ID"] == "Animal ID": continue # skip repeated headers
    a = asm.Animal()
    animals.append(a)
    if d["Species"] == "Cat":
        animaltype = 11
        animalletter = "U"
    else:
        animaltype = 2
        animalletter = "D"
    a.AnimalTypeID = animaltype
    a.SpeciesID = asm.species_id_for_name(d["Species"])
    if "Animal ID" in d:
        a.ShortCode = "RG%s" % d["Animal ID"]
        a.ShelterCode = "RG%s %s" % (d["Animal ID"], a.ID)
        if "Rescue ID" in d: a.ShortCode = d["Rescue ID"]
        ppa[d["Animal ID"]] = a
    else:
        a.generateCode()
    a.AnimalName = d["Name"]

    broughtin = None
    if "Received Date" in d and d["Received Date"] != "":
        broughtin = getdate(d["Received Date"])
    if broughtin is None and "Created" in d and d["Created"] != "":
        broughtin = getdate(d["Created"])
    if broughtin is None and "Last Updated" in d and d["Last Updated"] != "":
        broughtin = getdate(d["Last Updated"])
    a.DateBroughtIn = broughtin or asm.today()

    dob = None
    a.EstimatedDOB = 1
    if "Birthdate" in d and d["Birthdate"] != "":
        dob = getdate(d["Birthdate"])
        a.EstimatedDOB = 0
    if dob is None and "General Age" in d:
        if d["General Age"].find("Baby") != -1:
            dob = asm.subtract_days(a.DateBroughtIn, 91)
        elif d["General Age"].find("Young") != -1:
            dob = asm.subtract_days(a.DateBroughtIn, 182)
        elif d["General Age"].find("Adult") != -1:
            dob = asm.subtract_days(a.DateBroughtIn, 730)
        elif d["General Age"].find("Senior") != -1:
            dob = asm.subtract_days(a.DateBroughtIn, 2555)
    a.DateOfBirth = dob or a.DateBroughtIn
    a.Sex = 1
    if d["Sex"].startswith("F"):
        a.Sex = 0
    
    breed1 = ""
    breed2 = ""
    mixed = "No"
    if "Primary Breed" in d:
        breed1 = d["Primary Breed"]
        breed2 = d["Secondary Breed"]
        mixed = d["Mixed"]
    elif "Breed" in d:
        # Breed is in form breed1 / breed2 / mixed, sections only present if set
        breed2 = ""
        bb = d["Breed"].split("/")
        breed1 = bb[0]
        if len(bb) > 1: breed2 = bb[1]
        if len(bb) > 2: mixed = "Yes"
        
    a.BreedID = asm.breed_id_for_name(breed1, DEFAULT_BREED)
    if not mixed == "Yes":
        a.Breed2ID = a.BreedID
        a.BreedName = asm.breed_name_for_id(a.BreedID)
        a.CrossBreed = 0
    else:
        a.Breed2ID = a.BreedID
        if breed2 != "":
            a.Breed2ID = asm.breed_id_for_name(breed2, DEFAULT_BREED)
        a.BreedName = asm.breed_name_for_id(a.BreedID) + " / " + asm.breed_name_for_id(a.Breed2ID)
        a.CrossBreed = 1
    color = ""
    if "Color (General)" in d: color = d["Color (General)"]
    a.BaseColourID = asm.colour_id_for_name(color)
    a.ShelterLocation = 1
    if "Size Potential (General)" in d: a.Size = size_id_for_name(d["Size Potential (General)"])
    if "Declawed" in d: a.Declawed = d["Declawed"] == "Yes" and 1 or 0
    if "Special Needs" in d: a.HasSpecialNeeds = d["Special Needs"] == "Yes" and 1 or 0
    a.EntryReasonID = 1
    if "Altered" in d: a.Neutered = d["Altered"] == "Yes" and 1 or 0
    if "Housetrained" in d and d["Housetrained"] == "Yes": a.IsHouseTrained = 0
    if "OK with Dogs" in d and d["OK with Dogs"] == "Yes": a.IsGoodWithDogs = 0
    if "OK with Kids" in d and d["OK with Kids"] == "Yes": a.IsGoodWithChildren = 0
    if "OK with Cats" in d and d["OK with Cats"] == "Yes": a.IsGoodWithCats = 0
    if "Microchip Number" in d: a.IdentichipNumber = d["Microchip Number"].replace(" ", "")
    if a.IdentichipNumber != "": a.Identichipped = 1
    if "Description" in d: a.AnimalComments = d["Description"]
    if "Description (no html)" in d: a.AnimalComments = d["Description (no html)"]
    status = ""
    summary = ""
    origin = ""
    if "Status" in d: status = d["Status"]
    if "Summary" in d: summary = d["Summary"]
    if "Origin" in d: origin = d["Origin"]
    if "Notes" in d: notes = d["Notes"]
    a.HiddenAnimalDetails = f"{summary}, breed: {breed1} {breed2}, color: {color}, status: {status}, origin: {origin}, notes: {notes}"
    if "Internal ID" in d and "Location" in d: a.HiddenAnimalDetails += ", internal: " + d["Internal ID"] + ", location: " + d["Location"]
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    # If there's a fosterer, add the fosterer movement
    if "Foster ID" in d and d["Foster ID"] in ppocid: 
        o = ppocid[d["Foster ID"]]
        o.IsFosterer = 1
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 2
        m.MovementDate = a.DateBroughtIn
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 2
        a.LastChangedDate = m.MovementDate
        movements.append(m)
    # If the animal is adopted and we don't have an adoptions file, mark it to an unknown owner
    if status == "Adopted" and not asm.file_exists("%s/Adoptions.csv" % PATH):
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = uo.ID
        m.AnimalID = a.ID
        m.MovementDate = broughtin
        m.MovementType = 1
        a.ActiveMovementType = m.MovementType
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementID = m.ID
        a.Archived = 1
    # Mark the animal removed for other statuses 
    elif status in ("Transferred", "Escaped", "Stolen"):
        mt = { "Adopted": 1, "Transferred": 3, "Escaped": 4, "Stolen": 6 }[d["Status"]]
        m = asm.Movement()
        movements.append(m)
        m.OwnerID = uo.ID
        m.AnimalID = a.ID
        m.MovementDate = broughtin
        m.MovementType = mt
        a.ActiveMovementType = m.MovementType
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementID = m.ID
        a.Archived = 1
    elif status == "Passed Away":
        a.DeceasedDate = broughtin
        a.PutToSleep = 0
        a.PTSReasonID = 2 # Died
        a.Archived = 1
    elif status == "Euthanized":
        a.DeceasedDate = broughtin
        a.PutToSleep = 1
        a.PTSReasonID = 4 # Sick
        a.Archived = 1

    # Now do the dbfs and media inserts for photos if available
    if IMPORT_PICTURES: asm.stderr(f"retrieving pictures ({i+1} of {len(acsv)})")
    if "Picture 1" in d: getimage(d["Picture 1"], a)
    if "Picture 2" in d: getimage(d["Picture 2"], a)
    if "Picture 3" in d: getimage(d["Picture 3"], a)
    if "Picture 4" in d: getimage(d["Picture 4"], a)

if os.path.exists("%s/Adoptions.csv" % PATH):
    for d in asm.csv_to_list("%s/Adoptions.csv" % PATH):
        if "First Name" in d: 
            oname = d["First Name"].strip() + " " + d["Last Name"].strip()
        elif "Adopter" in d:
            b = d["Adopter"].split("  ", 1) # They separate the names with 2 spaces and put last before first
            oname = b[1] + " " + b[0]
        o = None
        if oname in ppo: o = ppo[oname]
        a = None
        if d["Animal ID"] in ppa: a = ppa[d["Animal ID"]]
        if o and a:
            m = asm.Movement()
            m.AnimalID = a.ID
            m.OwnerID = o.ID
            m.MovementType = 1
            m.MovementDate = getdate(d["Date"])
            a.Archived = 1
            a.ActiveMovementID = m.ID
            a.ActiveMovementDate = m.MovementDate
            a.ActiveMovementType = 1
            a.LastChangedDate = m.MovementDate
            movements.append(m)
            fee = asm.get_currency(d["Fee Paid"])
            if fee > 0:
                od = asm.OwnerDonation()
                od.DonationTypeID = 1
                od.DonationPaymentID = 1
                od.Date = m.MovementDate
                od.OwnerID = o.ID
                od.Donation = fee
                ownerdonations.append(od)

# Allow shelter animals to have their chips registered
for a in animals:
    if a.Archived == 0:
        a.IsNotForRegistration = 0

# Now that everything else is done, output stored records
for a in animals:
    print (a)
for o in owners:
    print (o)
for m in movements:
    print (m)
for od in ownerdonations:
    print (od)

asm.stderr_summary(animals=animals, owners=owners, movements=movements, ownerdonations=ownerdonations)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")

