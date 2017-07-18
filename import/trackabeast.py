#!/usr/bin/python

import asm, csv, sys, datetime

"""
Import script for Trackabeast export as csv
13th January, 2012

Complete rewrite for new library and customer, 18th July 2017
"""

PATH = "data/trackabeast_bm1439"

def getspecies(s):
    """ Looks up the species, returns Cat if nothing matches """
    if s.find("dog") != -1: return 1
    if s.find("puppy") != -1: return 1
    if s.find("cat") != -1: return 2
    if s.find("kitten") != -1: return 2
    return 2

def gettype(s):
    """ Looks up the animal type from a species. Returns Unwanted Cat for no match """
    sp = getspecies(s)
    if s == 1: return 2 # Dog
    if s == 2: return 11 # Unwanted Cat
    return 11

def getsize(s):
    if s.find("Very") != -1:
        return 0
    if s.find("Large") != -1:
        return 1
    if s.find("Medium") != -1:
        return 2
    if s.find("Small") != -1:
        return 3
    return 2

def getdate(s):
    return asm.getdate_mmddyy(s)

# --- START OF CONVERSION ---

asm.setid("animal", 100)
asm.setid("owner", 100)
asm.setid("adoption", 100)

owners = []
movements = []
animals = []

# List of trackids we've seen for animals so far
ppa = {}

# List of trackids we've seen for people so far
ppo = {}

for d in asm.csv_to_list("%s/animals.csv" % PATH):

    # New animal record if we haven't seen this trackid before
    trackid = d["TrackID"].strip()
    if not trackid in ppa:
        extradata = ""
        a = asm.Animal()
        ppa[trackid] = a
        a.AnimalName = d["Name"]
        a.AnimalTypeID = gettype(d["Type"])
        a.SpeciesID = getspecies(d["Type"])
        if d["Entry Date"].strip() != "": 
            a.DateBroughtIn = getdate(d["Entry Date"])
        a.Neutuered = d["Spay"].strip() == "Y" and 1 or 0
        a.CombiTested = 1
        a.FLVResult = d["Fel Leuk"].strip() == "Y" and 0 or 1
        extradata += "Rabies: " + d["Rabies"] + "\n"
        extradata += "Origin: " + d["Origin"] + "\n"
        extradata += "Rescue Type: " + d["Rescue Type"] + "\n"
        extradata += "Breed: " + d["Breed"] + " " + d["Breed #2"] + "\n"
        a.BreedID = asm.breed_id_for_name(d["Breed"])
        if d["Breed #2"] != "":
            a.Breed2ID = asm.breed_id_for_name(d["Breed #2"])
            a.CrossBreed = 1
        a.BreedName = asm.breed_name(a.BreedID, a.Breed2ID)
        if d["Birthdate"].strip() != "": a.DateOfBirth = getdate(d["Birthdate"])
        extradata += "Impound: " + d["Impound"] + "\n"
        a.IdentichipNumber = d["Microchip"]
        if d["Microchip"].strip() != "": a.Identichipped = 1
        a.TattooNumber = d["Tattoo"]
        if d["Tattoo"].strip() != "": a.Tattoo = 1
        extradata += "Registration: " + d["Registration"] + "\n"
        extradata += "Initial Rescue: " + d["Initial Rescue"] + "\n"
        a.Sex = asm.getsex_mf(d["Sex"])
        a.Size = getsize(d["Size"])
        extradata += "Weight: " + d["Weight"]
        a.HiddenAnimalDetails = extradata
        a.Weight = asm.cfloat(d["Weight"])
        if d["Special Needs"].strip() != "":
            a.HasSpecialNeeds = 1
            a.HealthProblems = d["Special Needs"]
        a.AnimalComments = d["Biography"]
        a.Markings = d["Description"]
        a.BaseColourID = asm.colour_id_for_name(d["Color"])
        a.ShelterLocation = 1
        a.generateCode("Dog")
        if d["Placement Status"].strip() == "Deceased": 
            a.DeceasedDate = getdate(d["Placement Date"])
            a.Archived = 1
        a.CreatedDate = a.DateBroughtIn
        a.LastChangedDate = a.DateBroughtIn
        animals.append(a)

for d in asm.csv_to_list("%s/people.csv" % PATH):

    # New owner record if we haven't seen this trackid before
    trackid = d["TrackID"].strip()
    if not trackid in ppo:
        extradata = ""
        o = asm.Owner()
        ppo[trackid] = o
        o.OwnerForeNames = d["First Name"]
        o.OwnerSurname = d["Last Name"]
        o.EmailAddress = d["Email 1"]
        o.OwnerAddress = "%s %s %s" % (d["Address 1"], d["Address 2"], d["Address 3"])
        o.OwnerTown = d["City"]
        o.OwnerCounty = d["State"]
        o.OwnerPostcode = d["Zip"]
        o.HomeTelephone = d["Home Phone"]
        o.MobileTelephone = d["Cell Phone"]
        o.WorkTelephone = d["Work Phone"]
        o.IsVolunteer = d["Vol"].strip() == "Y" and 1 or 0
        o.IsFosterer = d["Foster"].strip() == "Y" and 1 or 0
        o.Comments = d["Comments"]
        o.IsBanned = d["Do Not Adopt"].strip() != "" and 1 or 0
        owners.append(o)

for d in asm.csv_to_list("%s/placements.csv" % PATH):

    # Find the animal and owner for this placement
    a = None
    o = None
    if d["AnimalID"] in ppa:
        a = ppa[d["AnimalID"]]
    if d["PersonID"] in ppo:
        o = ppo[d["PersonID"]]

    # Is it a death movement? If so, just mark the animal deceased
    if d["Placement Status"].strip() == "Deceased" and a is not None:
        a.DeceasedDate = getdate(d["Placement Date"])
        a.PTSReason = d["Comments"]
        a.Archived = 1
        continue

    # Adoption or Foster
    if d["Placement Status"].strip() == "Adopted" or d["Placement Status"].strip() == "Fostered":
        if o is not None and a is not None:
            m = asm.Movement()
            m.OwnerID = o.ID
            m.AnimalID = a.ID
            m.MovementDate = getdate(d["Placement Date"])
            if d["Placement Status"].strip() == "Adopted":
                m.MovementType = 1
                a.Archived = 1
            if d["Placement Status"].strip() == "Fostered":
                m.MovementType = 2
            movements.append(m)
            a.ActiveMovementID = m.ID
            a.ActiveMovementDate = m.MovementDate
            a.ActiveMovementType = m.MovementType

# Now that everything else is done, output stored records
print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM owner WHERE ID >= 100 AND CreatedBy = 'conversion';"
print "DELETE FROM adoption WHERE ID >= 100 AND CreatedBy = 'conversion';"

for a in animals:
    print a
for o in owners:
    print o
for m in movements:
    print m

asm.stderr_summary(animals=animals, owners=owners, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

