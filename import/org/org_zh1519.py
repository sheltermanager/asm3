#!/usr/bin/python

import asm

"""
Import script for custom Access database for zh1519

20th Nov, 2017
"""

ANIMAL_FILENAME = "data/zh1519_access/Animal.csv"
ATTACHMENTS_FILENAME = "data/zh1519_access/Attachments.csv"
COMPLAINTS_FILENAME = "data/zh1519_access/Complaints.csv"
PERSONANIMAL_FILENAME = "data/zh1519_access/PersonAnimal.csv"
PERSON_FILENAME = "data/zh1519_access/Person.csv"
TREATMENT_FILENAME = "data/zh1519_access/TreatmentsProvided.csv"
IMAGE_PATH = "data/zh1519_access/photos"

def getdate(d):
    return asm.getdate_guess(d)

# --- START OF CONVERSION ---

animalcontrols = []
animalcontrolanimals = []
owners = []
ownerdonations = []
ownerlicences = []
movements = []
animals = []
animalmedicals = []
animalvaccinations = []
ppa = {}
ppo = {}
atop = {}
atoi = {}

asm.setid("animal", 100)
asm.setid("animalcontrol", 100)
asm.setid("animalmedical", 100)
asm.setid("animalmedicaltreatment", 100)
asm.setid("animalvaccination", 100)
asm.setid("log", 100)
asm.setid("owner", 100)
asm.setid("ownerdonation", 100)
asm.setid("ownerlicence", 100)
asm.setid("adoption", 100)
asm.setid("media", 100)
asm.setid("dbfs", 200)
print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM animalcontrol WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM animalcontrolanimal WHERE AnimalControlID >= 100;"
print "DELETE FROM animalmedical WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM animalmedicaltreatment WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM animalvaccination WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM owner WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM ownerdonation WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM ownerlicence WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM adoption WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM media WHERE ID >= 100;"
print "DELETE FROM dbfs WHERE ID >= 200;"


def get_asm_ownerid(oldanimalid):
    if not oldanimalid in atop:
        asm.stderr("can't find old animal id %s in PersonAnimal.csv" % oldanimalid)
        return 0
    oldpersonid = atop[oldanimalid]
    if not oldpersonid in ppo:
        asm.stderr("can't find old person id %s in ppo" % oldpersonid)
        return 0
    return ppo[oldpersonid].ID

# Create an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname

# Create a map of Animal IDs to Person IDs from PersonAnimal
for d in asm.csv_to_list(PERSONANIMAL_FILENAME):
    if d["PersonType"] == "CURRENT OWNER":
        atop[d["AnimalID"]] = d["PersonID"]

# Create a map of Animal IDs to Filenames from Attachments
for d in asm.csv_to_list(ATTACHMENTS_FILENAME):
    f = d["FileName"]
    if not f.startswith("A:"): continue # apparently causes problems
    atoi[d["AnimalID"]] = f[f.rfind("\\")+1:]

# Deal with people first
for d in asm.csv_to_list(PERSON_FILENAME):
    # Each row contains a person
    o = asm.Owner()
    owners.append(o)
    ppo[d["ID"]] = o
    o.OwnerForeNames = d["FirstName"]
    o.OwnerSurname = d["LastName"]
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = "%s %s" % (d["Address1"], d["Address2"])
    o.OwnerTown = d["City"]
    o.OwnerCounty = d["State"]
    o.OwnerPostcode = d["ZipCode"]
    o.EmailAddress = d["Email"]
    o.HomeTelephone = d["Phone1"]
    o.MobileTelephone = d["Phone2"]
    o.IsShelter = asm.iif(d["AnimalControlOffice"] == "TRUE", 1, 0)

# Animals
for d in asm.csv_to_list(ANIMAL_FILENAME):
    # Each row contains an animal, intake and outcome
    if ppa.has_key(d["ID"]):
        a = ppa[d["ID"]]
    else:
        a = asm.Animal()
        animals.append(a)
        ppa[d["ID"]] = a
        activeowner = 0
        a.EntryReasonID = 17 # Surrender
        if d["Ownership"] == "Stray": a.EntryReasonID = 7 # Stray
        if d["Species"] == "Cat":
            a.AnimalTypeID = 11 # Unwanted Cat
            if a.EntryReasonID == 7:
                a.AnimalTypeID = 12 # Stray Cat
        elif d["Species"] == "Dog":
            a.AnimalTypeID = 2 # Unwanted Dog
            if a.EntryReasonID == 7:
                a.AnimalTypeID = 10 # Stray Dog
        else:
            a.AnimalTypeID = 40 # Misc
        a.SpeciesID = asm.species_id_for_name(d["Species"])
        a.AnimalName = d["AnimalName"]
        if a.AnimalName.strip() == "":
            a.AnimalName = "(unknown)"
        a.DateBroughtIn = getdate(d["IntakeDate"])
        if a.DateBroughtIn is None:
            a.DateBroughtIn = asm.today()
        ageinmonths = asm.cint(d["AgeMonths"])
        age = asm.cint(d["Age"])
        if age > 0: ageinmonths += (age * 12)
        if ageinmonths == 0: ageinmonths = 12
        a.DateOfBirth = asm.subtract_days(a.DateBroughtIn, int(ageinmonths * 30.5))
        a.CreatedDate = getdate(d["CreateDate"])
        a.LastChangedDate = getdate(d["UpdateDate"])
        a.generateCode()
        if asm.cint(d["AnimalNumber"]) > 0:
            a.ShortCode = d["AnimalNumber"]
        else:
            # Animals with a 0 or non-integer number are non-shelter
            a.NonShelterAnimal = 1
            a.Archived = 1
            a.OriginalOwnerID = get_asm_ownerid(d["ID"])
            activeowner = a.OriginalOwnerID
        a.IsNotAvailableForAdoption = 0
        a.Sex = asm.getsex_mf(d["Gender"])
        a.Size = 2
        a.Neutered = asm.iif(d["SpayNeuter"] == "TRUE", 1, 0)
        a.IdentichipNumber = d["MicrochipNumber"]
        if a.IdentichipNumber != "N/A" and a.IdentichipNumber != "":
            a.Identichipped = 1
        asm.breed_ids(a, d["Breed"], default=443) # 443 = Unknown in their data
        if d["Breed"].find("Mix") != -1:
            a.CrossBreed = 1
            a.Breed2ID = 442
            a.BreedName = asm.breed_name(a.BreedID, a.Breed2ID)
        a.BaseColourID = asm.colour_id_for_name(d["Color"], default=60) # 60 = Unknown in their data
        markings = "Breed: %s" % d["Breed"]
        markings += "\nColor: %s" % d["Color"]
        markings += "\nCoat: %s %s" % (d["CoatLength"], d["CoatTexture"])
        markings += "\nCollar: %s" % d["Collar"]
        markings += "\nTail: %s" % d["Tail"]
        if d["Weight"] != "": markings += "\nWeight: %s" % d["Weight"]
        a.Markings = markings
        a.HiddenAnimalDetails = d["Comments"]
        a.AnimalComments = d["CageCardNotes"]
        a.IsGoodWithCats = 2
        a.IsGoodWithDogs = 2
        a.IsGoodWithChildren = 2
        a.HouseTrained = 0

        if d["ID"] in atoi:
            imagedata = asm.load_image_from_file("%s/%s" % (IMAGE_PATH, atoi[d["ID"]]))
            asm.animal_image(a.ID, imagedata) 

        if d["PrevOwnerID"] != "0" and d["PrevOwnerID"] != "":
            if d["PrevOwnerID"] in ppo:
                a.OriginalOwnerID = ppo[d["PrevOwnerID"]].ID
                activeowner = a.OriginalOwnerID
        if d["DateEuthanized"] != "":
            a.DeceasedDate = getdate(d["DateEuthanized"])
            a.Archived = 1
            a.PutToSleep = 1
            a.PTSReasonID = 2
        if d["DateAdopted"] != "":
            m = asm.Movement()
            m.AnimalID = a.ID
            m.OwnerID = get_asm_ownerid(d["ID"])
            activeowner = m.OwnerID
            m.MovementType = 1
            m.MovementDate = getdate(d["DateAdopted"])
            a.Archived = 1
            a.ActiveMovementID = m.ID
            a.ActiveMovementType = 1
            a.LastChangedDate = m.MovementDate
            movements.append(m)
            if d["AdoptionFee"] != "":
                od = asm.OwnerDonation()
                od.DonationTypeID = 2 # adoption fee
                od.DonationPaymentID = 1
                od.Date = m.MovementDate
                od.OwnerID = m.OwnerID
                od.Donation = asm.get_currency(d["AdoptionFee"])
                ownerdonations.append(od)
            if d["SpayNeuterAmt"] != "":
                od = asm.OwnerDonation()
                od.DonationTypeID = 1 # donation
                od.DonationPaymentID = 1
                od.Date = a.DateBroughtIn
                od.OwnerID = m.OwnerID
                od.Donation = asm.get_currency(d["SpayNeuterAmt"])
                od.Comments = "Spay/Neuter fee"
                ownerdonations.append(od)
            if d["MicrochipFee"] != "":
                od = asm.OwnerDonation()
                od.DonationTypeID = 1 # donation
                od.DonationPaymentID = 1
                od.Date = a.DateBroughtIn
                od.OwnerID = m.OwnerID
                od.Donation = asm.get_currency(d["MicrochipFee"])
                od.Comments = "Microchip fee"
                a.IdentichipDate = getdate(d["MicrochipDate"])
                ownerdonations.append(od)

        if d["DateReclaimed"] != "":
            m = asm.Movement()
            m.AnimalID = a.ID
            m.OwnerID = get_asm_ownerid(d["ID"])
            activeowner = m.OwnerID
            m.MovementType = 5
            m.MovementDate = getdate(d["DateReclaimed"])
            a.Archived = 1
            a.ActiveMovementID = m.ID
            a.ActiveMovementType = 5
            a.LastChangedDate = m.MovementDate
            movements.append(m)
            if d["ReclaimFee"] != "":
		od = asm.OwnerDonation()
		od.DonationTypeID = 1 # donation
		od.DonationPaymentID = 1
		od.Date = m.MovementDate
		od.OwnerID = m.OwnerID
                od.Donation = asm.get_currency(d["ReclaimFee"])
                od.Comments = "Reclaim fee"
                ownerdonations.append(od)

        # If there's any licence info set, do it
        if d["LicenseNbr"] != "" and d["LicenseDate"] != "" and activeowner > 0:
            ol = asm.OwnerLicence()
            ol.LicenceType = 1
            ol.AnimalID = a.ID
            ol.OwnerID = activeowner
            ol.LicenceNumber = d["LicenseNbr"]
            ol.IssueDate = getdate(d["LicenseDate"])
            ol.ExpiryDate = asm.add_days(ol.IssueDate, 365)
            ownerlicences.append(ol)

        # Vacces
        """
        if d["Vaccine"] != "" and d["Vaccine"] != "None":
            av = asm.AnimalVaccination()
            animalvaccinations.append(av)
            av.AnimalID = a.ID
            av.VaccinationID = 9 # FVRCP
            if a.SpeciesID == 1: av.VaccinationID = 8 # DHLPP
            av.DateRequired = a.DateBroughtIn
            av.DateOfVaccination = a.DateBroughtIn
            av.Comments = "%s %s" % (d["Vaccine"], d["Vaccinator"])
        if d["RabiesDate"] != "":
            av = asm.AnimalVaccination()
            animalvaccinations.append(av)
            av.AnimalID = a.ID
            av.VaccinationID = 4 # Rabies
            av.DateRequired = a.DateBroughtIn
            av.DateOfVaccination = a.DateBroughtIn
            av.Comments = "%s %s" % (d["Vaccine"], d["Vaccinator"])
        """

# Medical treatments/vaccinations
for d in asm.csv_to_list(TREATMENT_FILENAME):
    if d["AnimalID"] not in ppa: continue
    aid = ppa[d["AnimalID"]].ID
    a = ppa[d["AnimalID"]]
    meddate = getdate(d["CreateDate"])
    if meddate is None: meddate = a.DateBroughtIn
    if d["SerialNumber"] != "":
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.AnimalID = aid
        av.VaccinationID = 4 # Rabies
        av.DateRequired = meddate
        av.DateOfVaccination = meddate
        av.BatchNumber = d["SerialNumber"]
        av.Manufacturer = d["Manufacturer"]
        av.Comments = "%s Vaccinator: %s, Vet: %s, License: %s. %s, Batch Expires: %s" % (d["TreatmentName"], d["Vaccinator"], d["Vet"], d["VetLicenseNumber"], d["Comments"], d["ExpireDate"])
        a.RabiesTag = d["VaccineTagNbr"]
    elif d["TreatmentName"] in ( "BORDETELLA", "DHLP/P", "FVRCP" ):
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.AnimalID = aid
        av.VaccinationID = 6 # Bordetella
        if d["TreatmentName"].startswith("DHLP"): av.VaccinationID = 8 # DHLPP
        if d["TreatmentName"].startswith("FVRCP"): av.VaccinationID = 9 # FVRCP
        av.DateRequired = meddate
        av.DateOfVaccination = meddate
        av.BatchNumber = d["SerialNumber"]
        av.Manufacturer = d["Manufacturer"]
        av.DateExpires = getdate(d["ExpireDate"])
        av.Comments = "%s Vaccinator: %s, Vet: %s, License: %s. %s %s" % (d["TreatmentName"], d["Vaccinator"], d["Vet"], d["VetLicenseNumber"], d["VaccineTagNbr"], d["Comments"])
    else:
        animalmedicals.append(asm.animal_regimen_single(aid, meddate, d["TreatmentName"], "", "%s %s" % (d["VaccineTagNbr"], d["Comments"])))

# Incidents
for d in asm.csv_to_list(COMPLAINTS_FILENAME):
    if d["Complaint"].strip() == "" or d["ComplaintType"].strip() == "": continue
    ac = asm.AnimalControl()
    animalcontrols.append(ac)
    calldate = getdate(d["ComplaintDate"])
    if calldate is None: calldate = asm.now()
    ac.CallDateTime = calldate
    ac.IncidentDateTime = calldate
    ac.DispatchDateTime = calldate
    ac.CompletedDate = calldate
    ac.CallerID = d["CallerPersonID"] in ppo and ppo[d["CallerPersonID"]].ID or 0
    ac.OwnerID = d["OwnerPersonID"] in ppo and ppo[d["OwnerPersonID"]].ID or 0
    if d["AnimalID"] in ppa:
        animalcontrolanimals.append("INSERT INTO animalcontrolanimal (AnimalID, AnimalControlID) VALUES (%s, %s);\n" % ( ppa[d["AnimalID"]].ID, ac.ID ))
    ac.IncidentCompletedID = 2 # Picked up
    ac.IncidentTypeID = 7 # Neglect
    if d["ComplaintType"] == "Loose" or d["ComplaintType"] == "Running At Large": ac.IncidentType = 3 # At large
    if d["ComplaintType"] == "Bite": ac.IncidentType = 5 # Bite
    if d["ComplaintType"] == "Aggressive": ac.IncidentType = 1 # Aggressive
    if d["ComplaintType"] == "Barking": ac.IncidentType = 8
    comments = "type: %s, PU: %s" % (d["ComplaintType"], d["PU"])
    ac.CallNotes = "%s. %s" % (d["Complaint"], comments)
    ac.Sex = 2

# Run back through the animals, if we have any that are still
# on shelter after 1 year, add an adoption to an unknown owner
asm.adopt_older_than(animals, movements, uo.ID, 365)

# Now that everything else is done, output stored records
for k,v in asm.locations.iteritems():
    print v
for a in animals:
    print a
for am in animalmedicals:
    print am
for av in animalvaccinations:
    print av
for o in owners:
    print o
for od in ownerdonations:
    print od
for ol in ownerlicences:
    print ol
for m in movements:
    print m
for ac in animalcontrols:
    print ac
for aca in animalcontrolanimals:
    print aca

asm.stderr_summary(animals=animals, animalcontrol=animalcontrols, animalmedicals=animalmedicals, animalvaccinations=animalvaccinations, owners=owners, ownerdonations=ownerdonations, ownerlicences=ownerlicences, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

