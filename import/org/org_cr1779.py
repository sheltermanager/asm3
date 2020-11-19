#!/usr/bin/python

import asm, datetime
import web

"""
Import script for Greyhound rescue database cr1779

23rd August, 2018
"""

db = web.database( dbn = "mysql", db = "greyho13_greyhound", user = "robin", pw = "robin" )

START_ID = 100

def note_fix(s):
    return asm.nulltostr(s).encode("ascii", "xmlcharrefreplace")

def create_or_find_transfer_target(s):
    for o in owners:
        if o.OwnerName == s:
            return o
    o = Owner()
    owners.append(o)
    o.OwnerSurname = s
    o.OwnerName = s
    return o

# --- START OF CONVERSION ---

owners = []
ownerdonations = []
movements = []
animals = []
animalvaccinations = []
logs = []
ppa = {}
ppo = {}

asm.setid("animal", START_ID)
asm.setid("animalvaccination", START_ID)
asm.setid("log", START_ID)
asm.setid("owner", START_ID)
asm.setid("ownerdonation", START_ID)
asm.setid("adoption", START_ID)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= %s;" % START_ID
print "DELETE FROM animalvaccination WHERE ID >= %s;" % START_ID
print "DELETE FROM owner WHERE ID >= %s;" % START_ID
print "DELETE FROM ownerdonation WHERE ID >= %s;" % START_ID
print "DELETE FROM adoption WHERE ID >= %s;" % START_ID

# Create an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname

# Deal with people first
for d in db.select("Contacts").list() + db.select("ContactsOld").list():
    # Each row contains a person
    o = asm.Owner()
    owners.append(o)
    ppo[d.contactID] = o
    o.OwnerForeNames = note_fix(d.contactFname)
    o.OwnerSurname = note_fix(d.contactLname)
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = note_fix(d.contactStreet)
    o.OwnerTown = note_fix(d.contactCity)
    o.OwnerCounty = note_fix(d.contactState)
    o.OwnerPostcode = note_fix(d.contactZip)
    o.EmailAddress = note_fix(d.contactEmail)
    o.HomeTelephone = note_fix(d.contactPhone)
    if "contactWorkPhone" in d: o.WorkTelephone = note_fix(d.contactWorkPhone)
    comments = ""
    if "contactOccupation" in d: comments += "Occupation: %s\n" % d.contactOccupation
    comments += note_fix(d.contactComments)
    o.Comments = comments
    o.IsVolunteer = d.isVolunteer
    o.IsMember = d.isMember
    o.MembershipExpiryDate = d.contactMemberExpires
    if "contactReceiveNoMail" in d: o.ExcludeFromBulkEmail = d.contactReceiveNoMail
    o.CreatedDate = d.dateAdded or asm.today()
    o.CreatedBy = d.addedBy or "conversion"
    o.LastChangedBy = d.modifiedBy or "conversion"
    o.LastChangedDate = d.dateModifed or o.CreatedDate

# Now dogs
for d in db.select("Dogs").list() + db.select("Dogs_old").list():
    # Each row contains an animal
    a = asm.Animal()
    animals.append(a)
    ppa[d.dogID] = a
    has_intake = True
    a.SpeciesID = 1
    a.AnimalTypeID = 2
    a.BaseColourID = asm.colour_id_for_name(asm.nulltostr(d.dogColor), firstWordOnly=True)
    a.BreedID = 101 # Greyhound
    a.Breed2ID = a.BreedID
    a.BreedName = "Greyhound"
    a.AnimalName = note_fix(d.dogCallName)
    if a.AnimalName.strip() == "": a.AnimalName = note_fix(d.dogRegisteredName)
    if a.AnimalName.strip() == "": a.AnimalName = "(unknown)"
    a.DateBroughtIn = d.dogIntakeDate or d.dateAdded
    a.DateOfBirth = d.dogDateBorn or a.DateBroughtIn
    a.CreatedDate = d.dateAdded or a.DateBroughtIn
    a.CreatedBy = d.addedBy or "conversion"
    a.LastChangedBy = d.modifiedBy or "conversion"
    a.LastChangedDate = d.dateModified or a.CreatedDate
    a.generateCode()
    if d.dogSerialNum and asm.nulltostr(d.dogSerialNum) != "": a.ShortCode = d.dogSerialNum
    a.Sex = asm.iif(d.dogSex.lower().startswith("m"), 1, 0)
    a.Neutered = asm.iif(d.dogSex.lower().find("s") != -1 or d.dogSex.lower().find("n") != -1, 1, 0)
    a.Size = 2
    a.Weight = asm.cint(d.dogWeight)
    a.NeuteredDate = d.dogDateNeutered
    a.IsGoodWithCats = asm.iif(d.dogWithCats == 1, 0, 1)
    a.IsGoodWithDogs = asm.iif(d.dogWithDogs == 1, 0, 1)
    a.IsGoodWithChildren = asm.iif(d.dogWithKids == 1, 0, 1)
    a.IsHouseTrained = asm.iif(d.dogHousebroken == 1, 0, 1)
    if d.dogLeftEarNum != "" or d.dogRightEarNum != "":
        a.Tattoo = 1
        a.TattooNumber = "L:%s R:%s" % (d.dogLeftEarNum, d.dogRightEarNum)
    a.RabiesTag = d.dogRabiesTag
    a.HeartwormTestDate = d.dogHWTDate
    if a.HeartwormTestDate is not None: a.HeartwormTested = 1
    a.Archived = 0
    a.AnimalComments = note_fix(d.dogDescription)

    comments = "Color: %s" % d.dogColor
    if d.dogRegisteredName != "": comments += "\nRegistered Name: %s" % d.dogRegisteredName
    if d.dogTrack != "":          comments += "\nDog Track: %s" % d.dogTrack
    if d.dogStatus != "":         comments += "\nDog Status: %s" % d.dogStatus
    health = "Neuter Location: %s" % d.dogNeuterLocation
    if d.dogOtherMedical != "":   health += "\nOther Medical: %s" % d.dogOtherMedical
    if d.dogInjuries != "":       health += "\nInjuries: %s" % d.dogInjuries
    a.HiddenAnimalDetails = note_fix(comments)

    # Create vacc records from dogBordetella, dogRabiesDate and dogDistemperDate
    if d.dogBordetella is not None:
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.AnimalID = a.ID
        av.VaccinationID = 6 # Bordetella
        av.DateRequired = d.dogBordetella
        av.DateOfVaccination = d.dogBordetella
    if d.dogRabiesDate is not None:
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.AnimalID = a.ID
        av.VaccinationID = 4 # Rabies
        av.DateRequired = d.dogRabiesDate
        av.DateOfVaccination = d.dogRabiesDate
    if d.dogDistemperDate is not None:
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.AnimalID = a.ID
        av.VaccinationID = 1 # Distemper
        av.DateRequired = d.dogDistemperDate
        av.DateOfVaccination = d.dogDistemperDate

    # Create transfer records from dogMoved fields
    if d.dogMoved == 1:
        m = asm.Movement()
        movements.append(m)
        m.AnimalID = a.ID
        m.OwnerID = create_or_find_transfer_target(d.dogMovedComments)
        m.MovementType = 3
        m.MovementDate = d.dogMovedDate
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = m.MovementType
        a.LastChangedDate = m.MovementDate

# Adoptions
for d in db.select("Adoptions"):
    if not ppo.has_key(d.contactID): continue
    if not ppa.has_key(d.dogID): continue
    a = ppa[d.dogID]
    o = ppo[d.contactID]
    m = asm.Movement()
    movements.append(m)
    m.AnimalID = a.ID
    m.OwnerID = o.ID
    m.MovementType = 1
    m.MovementDate = d.adoptionDate
    a.Fee = int(d.adoptionFee * 100)
    m.Comments = d.adoptionComment
    a.Archived = 1
    a.ActiveMovementID = m.ID
    a.ActiveMovementDate = m.MovementDate
    a.ActiveMovementType = m.MovementType
    a.LastChangedDate = m.MovementDate
    if d.adoptionFee > 0:
        od = asm.OwnerDonation()
        ownerdonations.append(od)
        od.AnimalID = a.ID
        od.OwnerID = o.ID
        od.Donation = int(d.adoptionFee * 100)
        od.Date = d.adoptionDate
        od.DonationTypeID = 2 # Adoption Fee
        od.DonationPaymentID = 1 # Cash

# Donations
for d in db.select("Donations"):
    if not ppo.has_key(d.contactID): continue
    o = ppo[d.contactID]
    od = asm.OwnerDonation()
    ownerdonations.append(od)
    od.OwnerID = o.ID
    od.Donation = int(d.donationAmount * 100)
    od.Date = d.donationDate
    od.DonationTypeID = 1 # Donation
    od.DonationPaymentID = 1 # Cash

# Run back through the animals, if we have any that are still
# on shelter, add an adoption to an unknown owner
asm.adopt_older_than(animals, movements, uo.ID, 0)

# Now that everything else is done, output stored records
for k,v in asm.locations.iteritems():
    print v
for a in animals:
    print a
for av in animalvaccinations:
    print av
for o in owners:
    print o
for od in ownerdonations:
    print od
for m in movements:
    print m
for l in logs:
    print l

asm.stderr_summary(animals=animals, animalvaccinations=animalvaccinations, logs=logs, ownerdonations=ownerdonations, owners=owners, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

