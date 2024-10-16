#!/usr/bin/python

import asm, os

"""
Import script for Ark CSV, covers people, animals, payments, licences and complaints.

2nd Sep, 2015
"""

PATH = "/home/robin/tmp/asm3_import_data/multiops_zg0861"

owners = []
ownerdonations = []
ownerlicences = []
movements = []
animals = []
animalcontrol = []
ppa = {}
ppo = {}

arkspecies = {
    "C": 1, # Dog
    "F": 2, # Cat
    "E": 24 # Horse
}

asm.setid("animal", 100)
asm.setid("owner", 100)
asm.setid("ownerdonation", 100)
asm.setid("ownerlicence", 100)
asm.setid("adoption", 100)
asm.setid("animalcontrol", 100)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= 100 AND ID < 49999;"
print "DELETE FROM animalcontrol WHERE ID >= 100 AND ID < 49999;"
print "DELETE FROM owner WHERE ID >= 100 AND ID < 49999;"
print "DELETE FROM ownerdonation WHERE ID >= 100 AND ID < 49999;"
print "DELETE FROM ownerlicence WHERE ID >= 100 AND ID < 49999;"
print "DELETE FROM adoption WHERE ID >= 100 AND ID < 49999;"

for p in asm.csv_to_list("%s/NAMES.csv" % PATH):
    o = asm.Owner()
    owners.append(o)
    ppo[p["ID"]] = o
    o.OwnerForeNames = p["F_NAME"]
    o.OwnerSurname = p["L_NAME"]
    o.OwnerAddress = "%s %s\n%s" % (p["ADR_ST_NUM"], p["ADR_ST_NAM"], p["ADR_LINE2"])
    o.OwnerTown = p["CITY"]
    o.OwnerCounty = p["STATE"]
    o.OwnerPostcode = p["ZIP"]
    o.HomeTelephone = p["H_PHONE"]
    o.WorkTelephone = p["W_PHONE"]
    comments = "ID: %s" % p["ID"]
    comments += "\n%s" % asm.nulltostr(p["NAMES_TXT"])
    o.Comments = comments

for d in asm.csv_to_list("%s/ANIMALS.csv" % PATH):
    a = asm.Animal()
    animals.append(a)
    ppa[d["ID_NUM"]] = a
    a.AnimalName = d["NAME"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    if d["SPECIES"] == "C":
        # Canine
        a.SpeciesID = 1
        if d["SURR_CODE"] == "STR":
            a.AnimalTypeID = 10
            a.EntryReasonID = 11
            a.EntryTypeID = 2
        else:
            a.AnimalTypeID = 2
    elif d["SPECIES"] == "F":
        # Feline
        a.SpeciesID = 2
        if d["SURR_CODE"] == "STR":
            a.EntryReasonID = 11
            a.AnimalTypeID = 12
            a.EntryTypeID = 2
        else:
            a.AnimalTypeID = 11
    if d["SURR_ID"] != "":
        if ppo.has_key(d["SURR_ID"]):
            a.OriginalOwnerID = ppo[d["SURR_ID"]].ID
    a.generateCode()
    a.ShortCode = d["ID_NUM"]
    a.Sex = asm.getsex_mf(d["SEX"])
    a.ShelterLocationUnit = d["LOCATION"]
    a.BreedID = asm.breed_id_for_name(d["BREED"])
    a.BaseColourID = asm.colour_id_for_name(d["COLOR"])
    a.BreedName = asm.breed_name_for_id(a.BreedID)
    if d["BREED"].find("MIX") != -1:
        a.CrossBreed = 1
        a.Breed2ID = 442
        a.BreedName = asm.breed_name_for_id(a.BreedID) + " / " + asm.breed_name_for_id(a.Breed2ID)
    a.DateBroughtIn = asm.getdate_mmddyy(d["DATE_SURR"])
    if a.DateBroughtIn is None: a.DateBroughtIn = asm.now()
    a.NeuteredDate = asm.getdate_mmddyy(d["NEUTER_DAT"])
    if a.NeuteredDate is not None:
        a.Neutered = 1
    a.EstimatedDOB = 1
    dob = a.DateBroughtIn
    if d["AGE"] != "":
        if d["AGE"].find("YR") != -1:
            dob = asm.subtract_days(dob, asm.atoi(d["AGE"]) * 365)
        elif d["AGE"].find("M") != -1:
            dob = asm.subtract_days(dob, asm.atoi(d["AGE"]) * 30)
    a.DateOfBirth = dob
    if asm.atoi(d["EUTH_USD"]) > 0:
        a.PutToSleep = 1
        a.Archived = 1
        a.DeceasedDate = asm.getdate_mmddyy(d["DATE_DISPO"])
    comments = "Original breed: %s\nColor: %s" % (d["BREED"].strip(), d["COLOR"].strip())
    if asm.nulltostr(d["PU_LOC"]).strip() != "":
        comments += "\nPicked up from: %s" % d["PU_LOC"]
    a.HiddenAnimalDetails = comments
    a.AnimalComments = asm.nulltostr(d["ANIMAL_TXT"]).strip()
    a.HealthProblems = d["HEALTH"]
    a.LastChangedDate = a.DateBroughtIn
    if d["ADPT_ID"] != "":
        if ppo.has_key(d["ADPT_ID"]):
            o = ppo[d["ADPT_ID"]]
            m = asm.Movement()
            movements.append(m)
            m.AnimalID = a.ID
            m.OwnerID = o.ID
            m.MovementType = 1
            m.MovementDate = asm.getdate_mmddyy(d["DATE_DISPO"])
            if d["RECLAIMED"] == "X": 
                m.MovementType = 5
            m.LastChangedDate = m.MovementDate
            a.Archived = 1
            a.ActiveMovementType = m.MovementType
            a.ActiveMovementDate = m.MovementDate

for p in asm.csv_to_list("%s/PAYMENTS.csv" % PATH):
    od = asm.OwnerDonation()
    ownerdonations.append(od)
    if ppo.has_key(p["PMNT_ID"]):
        o = ppo[p["PMNT_ID"]]
        od.OwnerID = o.ID
        od.Donation = asm.atoi(p["AMOUNT"]) * 100
        od.Date = asm.getdate_mmddyy(p["PMNT_DATE"])
        od.DonationTypeID = 4 # Surrender
        if p["PMNT_CODE"] == "ADP":
            od.DonationTypeID = 2

if os.path.exists("%s/LICENSE.csv" % PATH):
    for l in asm.csv_to_list("%s/LICENSE.csv" % PATH):
        ol = asm.OwnerLicence()
        ownerlicences.append(ol)
        if ppo.has_key(l["OWNER_ID"]):
            o = ppo[l["OWNER_ID"]]
            ol.OwnerID = o.ID
            ol.LicenceTypeID = 1
            ol.LicenceNumber = l["LIC_NUM"]
            ol.LicenceFee = int(l["FEE"] * 100)
            ol.IssueDate = asm.getdate_mmddyy(l["LIC_DATE"])
            if ol.IssueDate is None: ol.IssueDate = asm.parse_date("2015-01-01", "%Y-%m-%d")
            ol.ExpiryDate = asm.getdate_mmddyy(l["LIC_EXDATE"])
            if ol.ExpiryDate is None: ol.ExpiryDate = asm.parse_date("2015-01-01", "%Y-%m-%d")

if os.path.exists("%s/CMPLAINT.csv" % PATH):
    for c in asm.csv_to_list("%s/CMPLAINT.csv" % PATH):
        ac = asm.AnimalControl()
        animalcontrol.append(ac)
        if c["FROM_ID"] != "" and ppo.has_key(c["FROM_ID"]):
            ac.CallerID = ppo[c["FROM_ID"]].ID
        if c["ABOUT_ID"] != "" and ppo.has_key(c["ABOUT_ID"]):
            ac.OwnerID = ppo[c["ABOUT_ID"]].ID
        ac.CallDateTime = asm.getdate_mmddyy(c["C_DATE"])
        if ac.CallDateTime is None:
            ac.CallDateTime = asm.parse_date("2015-01-01", "%Y-%m-%d")
        ac.IncidentDateTime = ac.CallDateTime
        ac.DispatchDateTime = ac.CallDateTime
        ac.CompletedDate = ac.CallDateTime
        ac.DispatchAddress = c["C_LOCATION"]
        if arkspecies.has_key(c["C_SPECIES"]):
            ac.SpeciesID = arkspecies[c["C_SPECIES"]]
        ac.Sex = asm.getsex_mf(c["C_SEX"])
        comments = ""
        comments = "Problem: %s" % c["PROBLEM"]
        if c["FOLLOW_UP"] != "": comments += "\nFollowup: %s" % c["FOLLOW_UP"]
        if c["OFFICER_ID"] != "": comments += "\nOfficer: %s" % c["OFFICER_ID"]
        if c["CITATION"] != "": comments += "\nCitation: %s" % c["CITATION"]
        if c["CMPL_TEXT"] != "": comments += "\nCompleted: %s" % c["CMPL_TEXT"]
        if type(comments) == unicode: comments = comments.encode("ascii", "xmlcharrefreplace")
        ac.CallNotes = comments

for a in animals:
    print a
for o in owners:
    print o
for m in movements:
    print m
for od in ownerdonations:
    print od
for ol in ownerlicences:
    print ol
for ac in animalcontrol:
    print ac

#asm.stderr_allanimals(animals)
#asm.stderr_onshelter(animals)
asm.stderr_summary(animals=animals, owners=owners, movements=movements, ownerlicences=ownerlicences, ownerdonations=ownerdonations, animalcontrol=animalcontrol)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
# TODO: Most recent customer wanted all ark data as historic - this should be 
# removed for future conversions
print "UPDATE animal SET Archived = 1 WHERE ID >= 100;"
print "COMMIT;"

