#!/usr/bin/python

import asm

"""
Import script for "To Your Rescue" databases exported as CSV
(requires animals_Table.xlsx.csv animalMilestones_Table.xlsx.csv animalHealth_Table.xlsx.csv and people_Table.xlsx.csv)

2nd July, 2018
"""

START_ID = 200

ANIMAL_FILENAME = "/home/robin/tmp/asm3_import_data/zw1754_tyr/animals_Table.xlsx.csv"
PERSON_FILENAME = "/home/robin/tmp/asm3_import_data/zw1754_tyr/people_Table.xlsx.csv"
HEALTH_FILENAME = "/home/robin/tmp/asm3_import_data/zw1754_tyr/animalHealth_Table.xlsx.csv"
MILESTONE_FILENAME = "/home/robin/tmp/asm3_import_data/zw1754_tyr/animalMilestones_Table.xlsx.csv"

def getdate(d):
    return asm.getdate_guess(d)

# --- START OF CONVERSION ---

owners = []
movements = []
animals = []
animalmedicals = []
animalvaccinations = []
ppa = {}
ppo = {}

asm.setid("animal", START_ID)
asm.setid("animalmedical", START_ID)
asm.setid("animalmedicaltreatment", START_ID)
asm.setid("animalvaccination", START_ID)
asm.setid("owner", START_ID)
asm.setid("adoption", START_ID)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= %s;" % START_ID
print "DELETE FROM animalmedical WHERE ID >= %s;" % START_ID
print "DELETE FROM animalmedicaltreatment WHERE ID >= %s;" % START_ID
print "DELETE FROM animalvaccination WHERE ID >= %s;" % START_ID
print "DELETE FROM owner WHERE ID >= %s;" % START_ID
print "DELETE FROM adoption WHERE ID >= %s;" % START_ID

# Deal with people first (if set)
if PERSON_FILENAME != "":
    PERSON_COLS = [ "ID", "OrgID", "OrgName", "DateAdded", "AddedBy", "UBool1", "FirstName", "UStr1", 
        "LastName", "Address", "City", "State", "Zip", "HomePhone", "WorkPhone", "Email", "UBool2", "Ufo1", "Ufo2", "Ufo3", "Ufo4", "Comments" ]
    for d in asm.csv_to_list_cols(PERSON_FILENAME, PERSON_COLS):
        if d["LastName"] == "": continue
        # Each row contains a person
        o = asm.Owner()
        owners.append(o)
        ppo[d["ID"]] = o
        o.OwnerForeNames = d["FirstName"]
        o.OwnerSurname = d["LastName"]
        o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
        o.OwnerAddress = d["Address"]
        o.OwnerTown = d["City"]
        o.OwnerCounty = d["State"]
        o.OwnerPostcode = d["Zip"]
        o.EmailAddress = d["Email"]
        o.HomeTelephone = d["HomePhone"]
        o.WorkTelephone = d["WorkPhone"]

# Animal records next
ANIMAL_COLS = [ "ID", "OrgID", "OrgName", "Uint1", "AddedDate", "AddedBy", "Species", "Name", "UBool1", "Ustr1", "UBool2", 
    "Status", "Breed", "Color", "DOB", "Sex", "Altered", "OutcomeType", "OutcomeDate", "Comments" ]
for d in asm.csv_to_list_cols(ANIMAL_FILENAME, ANIMAL_COLS):
    # Each row contains an animal
    a = asm.Animal()
    animals.append(a)
    ppa[d["ID"]] = a
    if d["Species"] == "Cat":
        a.AnimalTypeID = 11 # Unwanted Cat
    elif d["Species"] == "Dog":
        a.AnimalTypeID = 2 # Unwanted Dog
    else:
        a.AnimalTypeID = 40 # Misc
    a.SpeciesID = asm.species_id_for_name(d["Species"])
    a.AnimalName = d["Name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateBroughtIn = getdate(d["AddedDate"]) or asm.today()
    a.DateOfBirth = getdate(d["DOB"]) or asm.subtract_days(a.DateBroughtIn, 365)
    a.CreatedDate = getdate(d["AddedDate"])
    a.CreatedBy = d["AddedBy"]
    a.LastChangedDate = getdate(d["AddedDate"])
    a.LastChangedBy = d["AddedBy"]
    #if d["Intake Type"] == "Transfer In":
    #    a.IsTransfer = 1
    a.generateCode()
    a.IsNotAvailableForAdoption = 0
    a.Sex = asm.getsex_mf(d["Sex"])
    a.Size = 2
    a.Neutered = d["Altered"] == "TRUE" and 1 or 0
    a.EntryReasonID = 17 # Surrender
    a.IsGoodWithCats = 2
    a.IsGoodWithDogs = 2
    a.IsGoodWithChildren = 2
    a.HouseTrained = 0
    a.Archived = 0
    hcomments = "Species: " + d["Species"] + ", Breed: " + d["Breed"] + ", Color: " + d["Color"]
    asm.breed_ids(a, d["Breed"])
    a.BaseColourID = asm.colour_id_for_name(d["Color"])
    a.HiddenAnimalDetails = hcomments
    a.AnimalComments = d["Comments"]

# Then milestones (intakes and movements)
MILESTONE_COLS = [ "ID", "OrgID", "OrgName", "AddedDate", "AddedBy", "Date", "Type", "PersonID", 
    "AnimalID", "Species", "Name", "EntryType", "Ustr1", "Ustr2", "Uint1", "Uint2", "Comments" ]
for d in asm.csv_to_list_cols(MILESTONE_FILENAME, MILESTONE_COLS):
    a = None
    o = None
    if d["AnimalID"] in ppa: a = ppa[d["AnimalID"]]
    if d["PersonID"] in ppo: o = ppo[d["PersonID"]]
    if d["Type"] == "Birth":
        a.DateOfBirth = getdate(d["Date"])
    elif o is not None and (d["Type"] == "Intake" or d["Type"] == "ReIntake"):
        a.DateBroughtIn = getdate(d["Date"])
        a.OriginalOwnerID = o.ID
        a.ReasonForEntry = d["Comments"]
    elif o is not None and (d["Type"] in ( "Foster", "Adoption", "Transfer", "Released", "Returned to Owner" )):
        mt = {
            "Foster": 2,
            "Adoption": 1,
            "Transfer": 3,
            "Released": 5,
            "Returned to Owner": 5
        }
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = mt[d["Type"]]
        m.MovementDate = getdate(d["Date"])
        m.Comments = d["Comments"]
        a.Archived = (m.MovementType == 2 and 0 or 1)
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = m.MovementType
        a.CreatedBy = d["AddedBy"]
        a.CreatedDate = getdate(d["AddedDate"])
        a.LastChangedDate = getdate(d["AddedDate"])
        a.LastChangedBy = d["AddedBy"]
        movements.append(m)
    elif d["Type"] == "Foster Return":
        for m in movements:
            if m.AnimalID == a.ID and m.OwnerID == o.ID and m.MovementType == 2 and m.ReturnDate is None:
                m.ReturnDate = getdate(d["Date"])
    elif d["Type"] == "Adoption Return":
        for m in movements:
            if m.AnimalID == a.ID and m.OwnerID == o.ID and m.MovementType == 1 and m.ReturnDate is None:
                m.ReturnDate = getdate(d["Date"])
    elif d["Type"] == "Death":
        a.DeceasedDate = getdate(d["Date"])
        if d["Comments"].find("uthan") != -1:
            a.PutToSleep = 1
        a.PTSReasonID = 2
        a.PTSReason = d["Comments"]
        a.Archived = 1

def process_vacc(animalid, vaccdate = None, vaccexpires = None, vaccname = "", batchnumber = "", manufacturer = "", comments = ""):
    """ Processes a vaccination record. PP have multiple formats of this data file """
    av = asm.AnimalVaccination()
    animalvaccinations.append(av)
    if vaccdate is None:
        vaccdate = a.DateBroughtIn
    av.AnimalID = animalid
    av.VaccinationID = 8
    vaccmap = {
        "Bordatella": 6,
        "Bordetella": 6,
        "6-in-1 Canine": 8,
        "5-in-1 Canine": 8,
        "4-in-1 Canine": 8,
        "D-A2-P": 8,
        "Rabies": 4,
        "FeLV": 12,
        "FVRCP": 14,
        "Distemper": 1
    }
    for k, i in vaccmap.iteritems():
        if vaccname.find(k) != -1: av.VaccinationID = i
    av.DateRequired = vaccdate
    av.DateOfVaccination = vaccdate
    av.DateExpires = vaccexpires
    av.Manufacturer = manufacturer
    av.BatchNumber = batchnumber
    av.Comments = "Type: %s, %s" % (vaccname, comments)

# Finally health
HEALTH_COLS = [ "ID", "OrgID", "OrgName", "AddedDate", "AddedBy", "Uint1", "Ustr1", "AnimalID", "Name", "Type", "Ustr2", "Ustr3", 
    "Type2", "Thing", "Ubool1", "Ustr4", "Status", "Given", "Due", "U1", "U2", "U3", "U4", "Manufacturer", "BatchNumber", "U7", "U8", "U9", "U10", "User", "Vet", "Ustr5", "TestResult", "Microchip", "Comments" ]
for d in asm.csv_to_list_cols(HEALTH_FILENAME, HEALTH_COLS):
    a = None
    healthdate = getdate(d["Given"]) or getdate(d["Due"])
    if d["AnimalID"] in ppa: a = ppa[d["AnimalID"]]
    if d["Type"] == "Vaccination":
        process_vacc( a.ID, healthdate, None, d["Thing"], d["BatchNumber"], d["Manufacturer"], d["Comments"] )
    elif d["Type"] == "Procedure":
        animalmedicals.append( asm.animal_regimen_single(d["AnimalID"], healthdate, d["Thing"], "Procedure", d["Comments"] + " " + d["TestResult"]) )
        if d["Thing"] == "Microchip Implant":
            a.Identichipped = 1
            a.IdentichipNumber = d["Microchip"]

# Now that everything else is done, output stored records
for k,v in asm.locations.iteritems():
    print v
for a in animals:
    #if a.Archived == 1: print a
    print a
for am in animalmedicals:
    print am
for av in animalvaccinations:
    print av
for o in owners:
    print o
for m in movements:
    print m

#asm.stderr_allanimals(animals)
#asm.stderr_onshelter(animals)
asm.stderr_summary(animals=animals, animalmedicals=animalmedicals, animalvaccinations=animalvaccinations, owners=owners, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

