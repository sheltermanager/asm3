#!/usr/bin/env python3

import asm

"""
Import script for Petstablished databases exported as CSV
(requires animals.csv and optionally medical.csv)

Steps to export data from Petstablished:

    My Organization->Reports->Create New Report
    Custom Report
    Tick all the boxes
    Export CSV
    
    Then return to Reports page and once finished will show under Reports Available for Download

    Medical data can be extracted by doing the same thing, but
    choosing "Medical Report" instead of Custom Report and ticking all the boxes.

20th November, 2025
"""

# The shelter's petfinder ID for grabbing animal images for adoptable animals
START_ID = 100
PATH = "/home/robin/tmp/asm3_import_data/ps_ss3537"

def getdate(d, noblanks=False):
    rv = asm.getdate_guess(d)
    if noblanks and rv is None: rv = asm.now()
    return rv

def extract_address(o, location):
    """ Extract the address from a "Current Location" in the form NAME, ADDRESS, CITY, STATE, ZIP """
    chunks = location.split(",")
    if len(chunks) < 5: return # we can't do anything if there aren't 5 sections
    o.OwnerAddress = chunks[1].strip()
    o.OwnerTown = chunks[2].strip()
    o.OwnerCounty = chunks[3].strip()
    o.OwnerPostcode = chunks[4].strip()

def psYesNoUnknown(v):
    """ Translates a ps value of Yes, No or Not Sure into our yes no unknown integers """
    if v.lower() == "yes": return 0
    elif v.lower() == "no": return 1
    else: return 2

# --- START OF CONVERSION ---

owners = []
movements = []
animals = []
animalmedicals = []
animaltests = []
animalvaccinations = []
ppa = {}
ppo = {}

asm.setid("animal", START_ID)
asm.setid("animalmedical", START_ID)
asm.setid("animalmedicaltreatment", START_ID)
asm.setid("animaltest", START_ID)
asm.setid("animalvaccination", START_ID)
asm.setid("owner", START_ID)
asm.setid("adoption", START_ID)

print("\\set ON_ERROR_STOP\nBEGIN;")
print("DELETE FROM animal WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM animalmedical WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM animalmedicaltreatment WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM animaltest WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM animalvaccination WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM owner WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)
print("DELETE FROM adoption WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID)

# Create an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname

# Sort the data on intake date ascending
for d in sorted(asm.csv_to_list(PATH + "/animals.csv"), key=lambda k: getdate(k["Date Pet Entered Your Care"], True)):
    # If it's a repeat of the header row, skip
    if d["Pet Name"] == "Pet Name": continue
    # Each row contains an animal, intake and outcome
    if d["Petstablished ID"] in ppa:
        a = ppa[d["Petstablished ID"]]
    else:
        a = asm.Animal()
        animals.append(a)
        ppa[d["Petstablished ID"]] = a
        breed1 = ""
        breed2 = ""
        breeds = [ "" ]
        if "Pet Breed" in d: 
            breeds = d["Pet Breed"].split(",")
            breed1 = breeds[0]
            breed2 = ""
            if len(breeds) > 1: breed2 = breeds[1]
        elif "Pet Primary Breed" in d and "Pet Secondary Breed" in d:
            breed1 = d["Pet Primary Breed"]
            breed2 = d["Pet Secondary Breed"]
            breeds = [ breed1, breed2 ]
        asm.breed_ids(a, breed1, breed2)
        pettype = "Dog"
        if "Pet Type" in d: 
            pettype = d["Pet Type"]
        else:
            if breed1.find("Domestic") != -1:
                pettype = "Cat"
        if pettype == "Cat":
            a.AnimalTypeID = 11 # Unwanted Cat
            if d["Type of Intake"] == "Stray At Large":
                a.AnimalTypeID = 12 # Stray Cat
        elif pettype == "Dog":
            a.AnimalTypeID = 2 # Unwanted Dog
            if d["Type of Intake"] == "Stray At Large":
                a.AnimalTypeID = 10 # Stray Dog
        else:
            a.AnimalTypeID = 40 # Misc
        a.SpeciesID = asm.species_id_for_name(pettype)
        a.AnimalName = d["Pet Name"]
        if a.AnimalName.strip() == "":
            a.AnimalName = "(unknown)"
        a.DateBroughtIn = getdate(d["Date Pet Entered Your Care"]) or asm.today()
        if "Date of Birth" in d and d["Date of Birth"].strip() != "":
            a.DateOfBirth = getdate(d["Date of Birth"])
        else:
            a.DateOfBirth = asm.subtract_days(a.DateBroughtIn, 365)
        a.CreatedDate = a.DateBroughtIn
        a.LastChangedDate = a.DateBroughtIn
        if d["Type of Intake"] == "Transferred In":
            a.IsTransfer = 1
        a.generateCode()
        a.ShortCode = d["Petstablished ID"]
        a.IsNotAvailableForAdoption = 0
        a.Sex = asm.getsex_mf(d["Gender"])
        a.Size = asm.size_from_db(d["Size"])
        a.Weight = asm.atof(d["Weight"])
        colors = d["Color"].split(",")
        color1 = colors[0]
        color2 = ""
        if len(colors) > 1: color2 = colors[1]
        a.BaseColourID = asm.colour_id_for_names(color1, color2)

        a.Neutered = d["Spayed/Neutered?"].lower() == "yes" and 1 or 0
        a.HasSpecialNeeds = d["Special Need?"].lower() == "yes" and 1 or 0
        a.IsGoodWithDogs = psYesNoUnknown(d["Gets along with Dogs?"])
        a.IsGoodWithCats = psYesNoUnknown(d["Gets along with Cats?"])
        a.IsGoodWithChildren = psYesNoUnknown(d["Gets along with Kids?"])
        a.HouseTrained = 0

        a.EntryReasonID = 17 # Surrender
        if d["Type of Intake"] == "Stray At Large": 
            a.EntryReasonID = 7 # Stray
            a.EntryTypeID = 2
        if d["Type of Intake"] == "Transferred In": 
            a.EntryReasonID = 15 # Transfer from other shelter
            a.EntryTypeID = 3
        if d["Type of Intake"] == "Relinquished By Owner": 
            a.EntryReasonID = 17 # Surrender
    
        a.AnimalComments = d["Internal Notes"].replace("<p>", "").replace("</p>", "")
        a.HiddenAnimalDetails = d["Additional Comments"]
        a.ReasonForEntry = d["Where was pet originally found"] + " previous owner: " + d["Previous Owner Information"]
        a.IdentichipNumber = d["Microchip ID"]
        if a.IdentichipNumber != "": a.Identichipped = 1

        comments = "Intake type: " + d["Type of Intake"] + ", breed: " + breed1 + "/" + breed2
        comments += ", color: " + d["Color"] + ", coat: " + d["Coat Pattern"] + " " + d["Coat Length"] + ", age: " + d["Age in Years"]
        a.Markings = comments

        status = d["Current Status"]

        if status == "Available":
            a.Archived = 0

        elif status == "Adopted":
            o = None
            if d["Current Foster/Adopter"] in ppo:
                o = ppo[d["Current Foster/Adopter"]]
            else:
                o = asm.Owner()
                owners.append(o)
                ppo[d["Current Foster/Adopter"]] = o
                o.OwnerName = d["Current Foster/Adopter"]
                bits = o.OwnerName.split(" ")
                if len(bits) > 1:
                    o.OwnerForeNames = bits[0]
                    o.OwnerSurname = bits[len(bits)-1]
                else:
                    o.OwnerSurname = o.OwnerName
                extract_address(o, d["Current Location"])
                o.EmailAddress = d["Current Foster/Adopter Email"]
                if "Pet Owner's Home Number" in d: o.HomeTelephone = d["Pet Owner's Home Number"]
                if "Pet Owner's Cell Number" in d: o.MobileTelephone = d["Pet Owner's Cell Number"]
                if "Pet Owner's Work Phone" in d: o.WorkTelephone = d["Pet Owner's Work Phone"]
            m = asm.Movement()
            m.AnimalID = a.ID
            m.OwnerID = o.ID
            m.MovementType = 1
            m.MovementDate = getdate(d["Adoption/Foster Date"], True)
            a.Archived = 1
            a.ActiveMovementID = m.ID
            a.ActiveMovementDate = m.MovementDate
            a.ActiveMovementType = 1
            a.LastChangedDate = m.MovementDate
            movements.append(m)

        elif status == "Deceased":
            a.DeceasedDate = a.DateBroughtIn
            a.PutToSleep = 0
            a.PTSReasonID = 2 # Died
            a.Archived = 1

        elif status == "Free-Roaming":
            m = asm.Movement()
            m.AnimalID = a.ID
            m.OwnerID = o.ID
            m.MovementType = 7
            m.MovementDate = a.DateBroughtIn
            a.Archived = 1
            a.ActiveMovementID = m.ID
            a.ActiveMovementDate = m.MovementDate
            a.ActiveMovementType = 7
            a.LastChangedDate = m.MovementDate
            movements.append(m)

        elif status == "Hold":
            a.IsHold = 1

        elif status == "Not Available":
            pass # What is this?

        elif status == "Quarantined":
            a.IsQuarantine = 1

        elif status == "Returned to Owner":
            m = asm.Movement()
            m.AnimalID = a.ID
            m.OwnerID = o.ID
            m.MovementType = 5
            m.MovementDate = a.DateBroughtIn
            a.Archived = 1
            a.ActiveMovementID = m.ID
            a.ActiveMovementDate = m.MovementDate
            a.ActiveMovementType = 5
            a.LastChangedDate = m.MovementDate
            movements.append(m)

        elif status == "Transferred":
            m = asm.Movement()
            m.AnimalID = a.ID
            m.OwnerID = o.ID
            m.MovementType = 3
            m.MovementDate = a.DateBroughtIn
            a.Archived = 1
            a.ActiveMovementID = m.ID
            a.ActiveMovementDate = m.MovementDate
            a.ActiveMovementType = 3
            a.LastChangedDate = m.MovementDate
            movements.append(m)

# If the medical.csv file exists, import medical data from it
if asm.file_exists(PATH + "/medical.csv"):
    for d in asm.csv_to_list(PATH + "/medical.csv"):
        # If it's a repeat of the header row, skip
        if d["Pet Name"] == "Pet Name": continue
        a = ppa[d["Petstablished ID"]]

        if d["Subtype"] == "Vaccines Given":
            av = asm.AnimalVaccination()
            animalvaccinations.append(av)
            vaccname = d["Vaccine Name"]
            vaccdate = getdate(d["Date of Visit"])
            if vaccdate is None:
                vaccdate = a.DateBroughtIn
            vaccexpires = getdate(d["Vaccine Expiration Date"])
            av.AnimalID = a.ID
            av.VaccinationID = 8
            vaccmap = {
                "Bordatella": 6,
                "Bordetella": 6,
                "6-in-1 Canine": 8,
                "5-in-1 Canine": 8,
                "4-in-1 Canine": 8,
                "D-A2-P": 8,
                "DHPP": 8,
                "Rabies": 4,
                "FeLV": 12,
                "FVRCP": 14,
                "Distemper": 1
            }
            for k, i in vaccmap.items():
                if vaccname.find(k) != -1: av.VaccinationID = i
            av.DateRequired = vaccdate
            av.DateOfVaccination = vaccdate
            av.DateExpires = vaccexpires
            av.RabiesTag = d["Tag ID"]
            if av.RabiesTag != "" and a.RabiesTag == "": a.RabiesTag = av.RabiesTag
            av.Manufacturer = d["Vaccine Manufacturer Name"]
            av.BatchNumber = d["Vaccine Serial Number"]
            av.Comments = "Type: %s\n%s" % (vaccname, d["Description"])

        elif d["Subtype"] == "Viral Testing":
            at = asm.AnimalTest()
            animaltests.append(at)
            testdate = getdate(d["Date of Visit"])
            if testdate is None:
                testdate = a.DateBroughtIn
            at.DateRequired = testdate
            at.DateOfTest = testdate
            result = d["Test Result"]
            asmresult = 0
            if result == "Negative": asmresult = 1
            if result == "Positive": asmresult = 2
            at.TestResultID = asmresult + 1
            at.TestTypeID = 1 # Everything is FIV, customer didn't use anything else, but Name field contains test type
            at.Comments = "%s %s" % (d["Name"], d["Description"])

        else:
            # Surgery/Procedure... basically anything that wants a medical rather than vacc and test
            meddate = getdate(d["Date of Visit"])
            comments = d["Description"]
            if meddate is None:
                meddate = a.DateBroughtIn
            animalmedicals.append( asm.animal_regimen_single(a.ID, meddate, d["Name"], "N/A", comments) )



# Run back through the animals, if we have any that are still
# on shelter after 1 year, add an adoption to an unknown owner
# asm.adopt_older_than(animals, movements, uo.ID, 365)

# Now that everything else is done, output stored records
for a in animals:
    print(a)
for o in owners:
    print(o)
for m in movements:
    print(m)
for am in animalmedicals:
    print(am)
for at in animaltests:
    print(at)
for av in animalvaccinations:
    print(av)


#asm.stderr_allanimals(animals)
#asm.stderr_onshelter(animals)
asm.stderr_summary(animals=animals, animalmedicals=animalmedicals, animaltests=animaltests, animalvaccinations=animalvaccinations, owners=owners, movements=movements)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")

