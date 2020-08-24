#!/usr/bin/python

import asm

"""
Import script for kf2322 csv files (virtually the same as sb1875 with a few minor changes)

24 Aug, 2020
"""

START_ID = 1000

ANIMAL_FILENAME = "/home/robin/tmp/asm3_import_data/sb1875_csv/ASM_Animal_Master.csv"
LOG_FILENAME = "/home/robin/tmp/asm3_import_data/sb1875_csv/ASM_Animal_Log.csv"
PERSON_FILENAME = "/home/robin/tmp/asm3_import_data/sb1875_csv/ASM_People.csv"

def getdate(d):
    if d == "02/01/1900": return None # Weird quirk of their files
    return asm.getdate_ddmmyyyy(d)

# --- START OF CONVERSION ---

owners = []
movements = []
animals = []
animaltests = []
animalmedicals = []
animalvaccinations = []
logs = []
ppa = {}
ppo = {}

asm.setid("animal", START_ID)
asm.setid("animaltest", START_ID)
asm.setid("animalmedical", START_ID)
asm.setid("animalmedicaltreatment", START_ID)
asm.setid("animalvaccination", START_ID)
asm.setid("log", START_ID)
asm.setid("owner", START_ID)
asm.setid("adoption", START_ID)

print("\\set ON_ERROR_STOP\nBEGIN;")
print("DELETE FROM animal WHERE ID >= %s;" % START_ID)
print("DELETE FROM animalmedical WHERE ID >= %s;" % START_ID)
print("DELETE FROM animalmedicaltreatment WHERE ID >= %s;" % START_ID)
print("DELETE FROM animaltest WHERE ID >= %s;" % START_ID)
print("DELETE FROM animalvaccination WHERE ID >= %s;" % START_ID)
print("DELETE FROM log WHERE ID >= %s;" % START_ID)
print("DELETE FROM owner WHERE ID >= %s;" % START_ID)
print("DELETE FROM adoption WHERE ID >= %s;" % START_ID)

# print("DELETE FROM media;") 

# Create an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname

# Deal with people first
for d in asm.csv_to_list(PERSON_FILENAME, remove_non_ascii=True):
    # Each row contains a person
    o = asm.Owner()
    owners.append(o)
    ppo[d["People_Ctr"]] = o
    o.OwnerForeNames = d["PERSONFIRSTNAME"]
    o.OwnerSurname = d["PERSONLASTNAME"]
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = d["PERSONADDRESS"]
    o.OwnerTown = d["PERSONCITY"]
    o.OwnerCounty = d["PERSONSTATE"]
    o.OwnerPostcode = d["PERSONZIPCODE"]
    o.EmailAddress = d["PERSONEMAIL"]
    o.WorkTelephone = d["PERSONWORKPHONE"]
    o.MobileTelephone = d["PERSONCELLPHONE"]
    o.IsBanned = asm.iif(d["PERSONFLAGS"].find("Banned") != -1, 1, 0)
    o.IsDonor = asm.iif(d["PERSONDONOR"] == "1", 1, 0)
    o.IsFosterer = asm.iif(d["PERSONFOSTERER"] == "1", 1, 0)
    o.Comments = d["PERSONCOMMENTS"]
    o.JurisdictionID = asm.jurisdiction_from_db(d["PERSONADDITIONALCOUNCILNAME"])

# Animal intake records
for d in asm.csv_to_list(ANIMAL_FILENAME, remove_non_ascii=True):
    # Each row contains an animal with intake info:
    a = asm.Animal()
    animals.append(a)
    ppa[d["Animal_Identifier"]] = a
    a.AnimalTypeID = asm.type_from_db(d["Pound_Reason"])
    a.SpeciesID = asm.species_id_for_name(d["Species"])
    a.AnimalName = d["Name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateBroughtIn = getdate(d["Date_Admitted"]) or asm.today()
    if d["Date_Of_Birth"].strip() != "":
        a.DateOfBirth = getdate(d["Date_Of_Birth"])
    if a.DateOfBirth is None:
        a.DateOfBirth = asm.subtract_days(a.DateBroughtIn, 365)
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    #asm.additional_field("Legacy_Tag_No", 0, a.ID, d["Tag_no"])
    #asm.additional_field("Legacy_Tag_No_Q", 0, a.ID, d["Tag_no_qualifier"])
    a.ShortCode = d["Tag_no"]
    a.ShelterCode = a.ShortCode
    a.BreedID = asm.breed_from_db(d["Breed"], 1)
    a.BreedName = d["Breed"]
    if d["Cross_Breed"] != "":
        a.Breed2ID = asm.breed_from_db(d["Cross_Breed"], 1)
        a.CrossBreed = 1
        a.BreedName = "%s / %s" % (d["Breed"], d["Cross_Breed"])
    #a.BaseColourID = asm.colour_id_for_names(d["Base_Colour"], d["Secondary_Colour"])
    a.BaseColourID = asm.colour_from_db(d["Base_"])
    a.AnimalComments = d["Notes"]
    a.Sex = asm.getsex_mf(d["Sex"])
    a.Size = asm.size_id_for_name(d["Size"])
    a.NeuteredDate = getdate(d["Date_Desexed"])
    if a.NeuteredDate is not None: a.Neutered = 1
    a.IsNotForRegistration = 0
    a.IsNotAvailableForAdoption = 1
    a.IdentichipNumber = d["Microchip_no"]
    a.Identichip2Number = d["Alternate_Chip_No"]
    asm.additional_field("MChipType", 5, a.ID, d["Microchip_Type"]) # MChipType additional field
    if a.IdentichipNumber != "": a.Identichipped = 1
    if a.IdentichipNumber == "0": 
        a.Identichipped = 0
        a.IdentichipNumber = ""
    a.IdentichipDate = asm.getdate_ddmmyyyy(d["Date_Microchipped"])
    a.IsGoodWithCats = 2
    a.IsGoodWithDogs = 2
    a.IsGoodWithChildren = 2
    a.HouseTrained = 0
    a.AcceptanceNumber = d["Litter No"]

    comments = "Breed: " + d["Breed"] + "/" + d["Cross_Breed"]
    comments += "\nSpecies: " + d["Species"]
    comments += "\nMicrochip Type: " + d["Microchip_Type"]
    comments += "\nSize: " + d["Size"]
    comments += "\nCondition: " + d["Animal_Condition"]
    a.HiddenAnimalDetails = comments

    entrycomments = "Pound Reason: " + d["Pound_Reason"]
    entrycomments += "\nWhere Found: " + d["Where_found"]
    entrycomments += "\nStreet Found: " + d["Street_Found_In"]
    a.ReasonForEntry = entrycomments
    a.EntryReasonID = 17 # Surrender
    #if d["InShelterSearchFlag"] == "N":
    #    a.Archived = 1
    if d["Location"] != "": a.ShelterLocation = asm.location_from_db(d["Location"])
    if d["Unit"] != "": a.ShelterLocationUnit = d["Unit"]


# Animal log, recording medical history and linking adoptions/surrenderers/etc
for d in asm.csv_to_list(LOG_FILENAME, remove_non_ascii=True):

    if d["Animal_Identifier"] not in ppa: continue
    a = ppa[d["Animal_Identifier"]]
    o = uo
    if d["People_ctr"] != "": o = ppo[d["People_ctr"]]
    ed = getdate(d["Entry_date"])
    if not ed: continue

    if d["Weight"] != "0" and d["Weight"] != "":
        try:
            a.Weight = float(d["Weight"])
        except ValueError:
            pass
        l = asm.Log()
        logs.append(l)
        l.LogTypeID = 4 # Weight
        l.LinkID = a.ID
        l.LinkType = 0
        l.Date = ed
        l.Comments = d["Weight"]

    if d["Action"] == "Admission" and d["Log_Description"] == "Owner Surrender" and o:
        a.OriginalOwnerID = o.ID
        a.BroughtInByOwnerID = o.ID
        a.DateBroughtIn = ed
        a.CreatedBy = d["User_Id"]

    elif d["Action"] == "Veterinary" and d["Log_Description"] == "Desexed":
        a.Neutered = 1
        a.NeuteredDate = ed
        animalmedicals.append( asm.animal_regimen_single(a.ID, ed, d["Log_Description"], "N/A", d["Log_Notes"]) )

    elif d["Action"] == "Veterinary":
        animalmedicals.append( asm.animal_regimen_single(a.ID, ed, d["Log_Description"], "N/A", d["Log_Notes"]) )

    elif d["Action"] == "Vaccination":
        vacctypes = {
            "C3": 16,
            "C5": 18,
            "F3": 22,
            "F4": 23
        }
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.AnimalID = a.ID
        av.VaccinationID = 8
        for k, i in vacctypes.iteritems():
            if d["Log_Description"].find(k) != -1: av.VaccinationID = i
        av.DateRequired = ed
        av.DateOfVaccination = ed
        av.Comments = "Type: %s\n%s" % (d["Log_Description"], d["Log_Notes"])
        av.CreatedBy = d["User_Id"]

    elif d["Action"] == "Foster Care" and d["Log_Description"] == "Foster Care":
        o.IsFosterer = 1
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 2
        m.MovementDate = ed
        m.Comments = d["Log_Notes"]
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 2
        a.LastChangedDate = ed
        movements.append(m)

    elif d["Action"] == "Foster Care" and d["Log_Description"] == "Carer Return":
        # Return this person's most recent foster
        for m in movements:
            if m.AnimalID == a.ID and m.ReturnDate is None and m.MovementType == 2 and m.OwnerID == o.ID:
                m.ReturnDate = ed
                break

    elif d["Action"] == "Adoption" or d["Action"] == "Exit Log":
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = ed
        m.Comments = d["Log_Notes"]
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 1
        a.LastChangedDate = ed
        movements.append(m)

    elif d["Action"] == "Claim":
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 5
        m.MovementDate = ed
        m.Comments = d["Log_Notes"]
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 5
        a.LastChangedDate = ed
        movements.append(m)

    elif d["Action"] == "Outlet Transfer":
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 3
        m.MovementDate = ed
        m.Comments = d["Log_Notes"]
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 3
        a.LastChangedDate = ed
        movements.append(m)

    elif d["Action"] == "Euthanasia":
        a.PutToSleep = 1
        a.DeceasedDate = ed
        a.Archived = 1
        a.PTSReasonID = 2
        a.PTSReason = d["Log_Description"] + ": " + d["Log_Notes"]
        a.LastChangedDate = ed

    elif d["Action"] == "Return" or d["Action"] == "ReAdmission":
        # Return the most recent exit movement for this animal/person
        for m in movements:
            if m.AnimalID == a.ID and m.ReturnDate is None and m.MovementType not in (2, 8) and m.OwnerID == o.ID:
                m.ReturnDate = ed
                m.ReturnedReasonID = 17 # Surrender
                break

    elif d["Action"] == "VetCatDischarge":
        a.NonShelterAnimal = 1
        a.Archived = 1

    else:
        # Create a log entry for action, log_description, log_notes
        l = asm.Log()
        logs.append(l)
        l.LogTypeID = 3 # History
        l.LinkID = a.ID
        l.LinkType = 0
        l.Date = ed
        l.Comments = d["Log_Notes"]

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
    print(v)
for a in animals:
    print(a)
for am in animalmedicals:
    print(am)
for at in animaltests:
    print(at)
for av in animalvaccinations:
    print(av)
for o in owners:
    print(o)
for m in movements:
    print(m)
for l in logs:
    print(l)

asm.stderr_summary(animals=animals, animaltests=animaltests, animalmedicals=animalmedicals, animalvaccinations=animalvaccinations, logs=logs, owners=owners, movements=movements)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")

