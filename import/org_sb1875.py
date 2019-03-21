#!/usr/bin/python

import asm

"""
Import script for sb1875 csv files

1st March, 2019
"""

START_ID = 1000

ANIMAL_FILENAME = "data/sb1875_csv/ASM_Animal_Master.csv"
LOG_FILENAME = "data/sb1875_csv/ASM_Animal_Log.csv"
PERSON_FILENAME = "data/sb1875_csv/ASM_People.csv"

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

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM animalmedical WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM animaltest WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM animalvaccination WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM log WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM owner WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM adoption WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID

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
    if d["Species"] == "Cat":
        a.AnimalTypeID = 11 # Unwanted Cat
        if d["Pound_Reason"] == "Stray":
            a.AnimalTypeID = 12 # Stray Cat
    elif d["Species"] == "Dog":
        a.AnimalTypeID = 2 # Unwanted Dog
        if d["Pound_Reason"] == "Stray":
            a.AnimalTypeID = 10 # Stray Dog
    else:
        a.AnimalTypeID = 40 # Misc
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
    asm.additional_field("Legacy_Tag_No", 0, a.ID, d["Tag_no"])
    asm.additional_field("Legacy_Tag_No_Q", 0, a.ID, d["Tag_no_qualifier"])
    a.ShortCode = "%s:%s" % (d["Tag_no"], d["Tag_no_qualifier"])
    a.ShelterCode = a.ShortCode
    asm.breed_ids(a, d["Breed"], d["Cross_Breed"])
    a.BaseColourID = asm.colour_id_for_names(d["Base_Colour"], d["Secondary_Colour"])
    a.AnimalComments = d["Notes"]
    a.Sex = asm.getsex_mf(d["Sex"])
    a.Size = asm.size_id_for_name(d["Size"])
    a.NeuteredDate = getdate(d["Date_Desexed"])
    if a.NeuteredDate is not None: a.Neutered = 1
    a.IdentichipNumber = d["Microchip_no"]
    a.Identichip2Number = d["Alternate_Chip_No"]
    if a.IdentichipNumber != "": a.Identichipped = 1
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
    if d["Pound_Reason"] == "Stray": a.EntryReasonID = 7
    # If this animal is not a resident, such as just to see the vet mark it non-shelter
    if d["Pound_Reason"] not in ( "Stray", "Pound", "Owner Surrender" ): 
        a.NonShelterAnimal = 1
        a.Archived = 1

# Animal log, recording medical history and linking adoptions/surrenderers/etc
for d in asm.csv_to_list(LOG_FILENAME, remove_non_ascii=True):

    a = ppa[d["Animal_Identifier"]]
    o = None
    ed = getdate(d["Entry_date"])

    if not ed: continue
    if d["People_ctr"] != "": o = ppo[d["People_ctr"]]

    if d["Action"] == "Admission" and d["Log_Description"] == "Owner Surrender" and o:
        a.OriginalOwnerID = o.ID
        a.BroughtInByOwnerID = o.ID
        a.DateBroughtIn = ed
        a.CreatedBy = d["User_Id"]

    elif d["Weight"] != "0":
        a.Weight = float(d["Weight"])
        l = asm.Log()
        logs.append(l)
        l.LogTypeID = 1 # Weight
        l.LinkID = a.ID
        l.LinkType = 0
        l.Date = ed
        l.Comments = d["Weight"]

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

    elif d["Action"] == "Foster Care" and d["Log_Description"] == "Foster Care" and o:
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

    elif d["Action"] == "Foster Care" and d["Log_Description"] == "Carer Return" and o:
        # Return this person's most recent foster
        for m in movements:
            if m.AnimalID == a.ID and m.ReturnDate is None and m.MovementType == 2 and m.OwnerID == o.ID:
                m.ReturnDate = ed
                a.Archived = 0 # Return to shelter so another movement takes it away again
                break

    elif d["Action"] == "Adoption" and o:
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

    elif d["Action"] == "Claim" and o:
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

    elif d["Action"] == "Euthanasia":
        a.PutToSleep = 1
        a.DeceasedDate = ed
        a.Archived = 1
        a.PTSReasonID = 2
        a.PTSReason = d["Log_Description"] + ": " + d["Log_Notes"]
        a.LastChangedDate = ed

    elif d["Action"] == "Return" and o:
        # Return the most recent adoption for this animal/person
        for m in movements:
            if m.AnimalID == a.ID and m.ReturnDate is None and m.MovementType == 1 and m.OwnerID == o.ID:
                m.ReturnDate = ed
                m.ReturnedReasonID = 17 # Surrender
                a.Archived = 0 # Return to shelter so another movement takes it away again
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
for m in movements:
    print m
for l in logs:
    print l

asm.stderr_summary(animals=animals, animaltests=animaltests, animalmedicals=animalmedicals, animalvaccinations=animalvaccinations, logs=logs, owners=owners, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

