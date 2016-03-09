#!/usr/bin/python

import asm
from dbfread import DBF

"""
Import script for Petwhere DBF databases, 

covers animal, people, addresses, complaints

note that this is currently animal control focused and will create
non-shelter animals.

9th March, 2016
"""

PATH = "data/petwhere_wa1003"

owners = []
ownerlicence = []
ownerdonation = []
animals = []
animalcontrol = []
animalcontrolanimal = []
ppa = {}
ppo = {}

asm.setid("animal", 100)
asm.setid("owner", 100)
asm.setid("ownerlicence", 100)
asm.setid("ownerdonation", 100)
asm.setid("animalcontrol", 100)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= 100;"
print "DELETE FROM animalcontrol WHERE ID >= 100;"
print "DELETE FROM owner WHERE ID >= 100;"
print "DELETE FROM ownerlicence WHERE ID >= 100;"
print "DELETE FROM ownerdonation WHERE ID >= 100;"

# pre-load address and residences mappings
addresses = {}
for a in DBF("%s/ADDRESS.DBF" % PATH):
    addresses[a["ADDRESSNO"]] = a

residences = {}
for r in DBF("%s/RESIDENC.DBF" % PATH):
    residences[r["PERSONNO"]] = r

for p in DBF("%s/PERSON.DBF" % PATH):
    if p["PERSONNO"] == "New": continue
    o = asm.Owner()
    owners.append(o)
    ppo[p["PERSONNO"]] = o
    o.OwnerForeNames = p["FIRSTNAME"]
    o.OwnerSurname = p["LASTNAME"]
    if p["AGENCY"] != "" and o.OwnerSurname == "":
        o.OwnerSurname = p["AGENCY"]
    o.ExcludeFromBulkEmail = asm.iif(p["SENDMAIL"] == "FALSE", 1, 0)
    if residences.has_key(p["PERSONNO"]):
        res = residences[p["PERSONNO"]]
        if addresses.has_key(res["ADDRESSNO"]):
            ad = addresses[res["ADDRESSNO"]]
            o.OwnerAddress = "%s %s %s %s" % (ad["STREETNO"], ad["STREETDIR"], ad["STREETNAME"], ad["STREETTYPE"])
            o.OwnerTown = ad["CITY"]
            o.OwnerCounty = ad["STATE"]
            o.OwnerPostcode = ad["ZIP"].replace("-", "")
    o.HomeTelephone = p["WORKPHONE"]
    comments = "No: %s" % p["PERSONNO"]
    if p["IDTYPE"] != "Unspecified":
        comments += "\n%s %s" % (p["IDTYPE"], p["IDNUM"])
    if p["DOB"] is not None:
        comments += "\nDOB: %s" % p["DOB"]
    o.Comments = comments

for d in DBF("%s/ANIMAL.DBF" % PATH):
    if d["ANIMALNO"] == "New": continue
    a = asm.Animal()
    animals.append(a)
    ppa[d["ANIMALNO"]] = a
    a.AnimalName = d["ANIMALNAME"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    if d["SPECIES"] == "Dog":
        # Canine
        a.SpeciesID = 1
        a.AnimalTypeID = 10
        a.EntryReasonID = 11
    elif d["SPECIES"] == "Cat":
        # Feline
        a.SpeciesID = 2
        a.EntryReasonID = 11
        a.AnimalTypeID = 12
    else:
        # Other species
        a.SpeciesID = asm.species_id_for_name(d["SPECIES"])
        a.AnimalTypeID = asm.type_id_for_name(d["SPECIES"])
    a.generateCode()
    a.ShortCode = d["ANIMALNO"]
    a.Sex = asm.getsex_mf(d["SEX"])
    a.BreedID = asm.breed_id_for_name(d["BREED1"])
    if d["BREED2"] == "Unspecified":
        a.Breed2ID = a.BreedID
        a.CrossBreed = 0
    else:
        a.CrossBreed = 1
        a.Breed2ID = asm.breed_id_for_name(d["BREED2"])
    a.BreedName = asm.breed_name(a.BreedID, a.Breed2ID)
    if d["BREED2"].find("Mix") != -1:
        a.CrossBreed = 1
        a.Breed2ID = 442
        a.BreedName = asm.breed_name_for_id(a.BreedID) + " / " + asm.breed_name_for_id(a.Breed2ID)
    a.BaseColourID = asm.colour_id_for_name(d["COLOR1"])
    a.DateBroughtIn = d["FOUNDDATE"]
    if a.DateBroughtIn is None: a.DateBroughtIn = asm.now()
    a.Neutered = asm.iif(d["ALTERED"] == "Yes", 1, 0)
    a.DateOfBirth = d["BIRTHDATE"]
    if a.DateOfBirth is None:
        a.EstimatedDOB = 1
        a.DateOfBirth = asm.subtract_days(a.DateBroughtIn, 365)
    a.PickupAddress = d["CITY"]
    a.AnimalComments = d["NOTES"]
    a.Markings = d["MARKINGS"]
    comments = "Status: %s" % d["STATUS"]
    comments += "\nOriginal breed: %s / %s" % (d["BREED1"], d["BREED2"])
    comments += "\nColor: %s / %s" % (d["COLOR1"], d["COLOR2"])
    comments += "\nPattern: %s" % d["PATTERN"]
    comments += "\nAge Group: %s" % d["AGEGROUP"]
    comments += "\nWeight Group: %s" % d["WEIGHTGRP"]
    comments += "\nCoat: %s" % d["COAT"]
    comments += "\nTail: %s" % d["TAIL"]
    a.HiddenAnimalDetails = comments
    a.LastChangedDate = a.DateBroughtIn
    a.NonShelterAnimal = 1

"""
for p in DBF("%s/PAYMENTS.DBF" % PATH):
    od = asm.OwnerDonation()
    ownerdonations.append(od)
    if ppo.has_key(p["PMNT_ID"]):
        o = ppo[p["PMNT_ID"]]
        od.OwnerID = o.ID
        od.Donation = int(p["AMOUNT"] * 100)
        od.Date = p["PMNT_DATE"]
        od.DonationTypeID = 4 # Surrender
        if p["PMNT_CODE"] == "ADP":
            od.DonationTypeID = 2

for l in DBF("%s/LICENSE.DBF" % PATH):
    ol = asm.OwnerLicence()
    ownerlicences.append(ol)
    if ppo.has_key(l["OWNER_ID"]):
        o = ppo[l["OWNER_ID"]]
        ol.OwnerID = o.ID
        ol.LicenceTypeID = 1
        ol.LicenceNumber = l["LIC_NUM"]
        ol.LicenceFee = int(l["FEE"] * 100)
        ol.IssueDate = l["LIC_DATE"]
        if ol.IssueDate is None: ol.IssueDate = asm.parse_date("2015-01-01", "%Y-%m-%d")
        ol.ExpiryDate = l["LIC_EXDATE"]
        if ol.ExpiryDate is None: ol.ExpiryDate = asm.parse_date("2015-01-01", "%Y-%m-%d")
"""

typemap = {
    "ABANDONMENT": 7,
    "AGGRESSIVE": 1,
    "AT LARGE": 3,
    "BARKING": 8,
    "BITE LIVESTOCK": 5,
    "CHASE LIVESTOCK": 3,
    "CRUELTY / NEGLECT": 7,
    "FOUND ANIMAL": 7,
    "HIT BY CAR": 10,
    "INJURED ANIMAL": 10, 
    "LIVESTOCK IN CITY": 3,
    "LIVESTOCK LOOSE": 3,
    "LOST ANIMAL": 7,
    "STRAY": 7
}

for c in DBF("%s/COMPLNTS.DBF" % PATH):
    ac = asm.AnimalControl()
    animalcontrol.append(ac)
    if c["COMPLANANT"] != "Unspecified" and ppo.has_key(c["COMPLANANT"]):
        ac.CallerID = ppo[c["COMPLANANT"]].ID
    if c["OWNER"] != "Unspecified" and ppo.has_key(c["OWNER"]):
        ac.OwnerID = ppo[c["OWNER"]].ID
    ac.CallDateTime = c["OPENDT"]
    ac.IncidentDateTime = ac.CallDateTime
    ac.DispatchDateTime = ac.CallDateTime
    ac.CompletedDate = c["CLOSEDT"]
    ac.IncidentTypeID = 3
    if typemap.has_key(c["CASETYPE"]):
        ac.IncidentTypeID = typemap[c["CASETYPE"]]
    ac.DispatchAddress = c["COMPADDR"]
    comments = asm.nulltostr(c["CASEDESC"])
    comments += "\nBeat: %s" % c["BEAT"]
    comments += "\nOfficer: %s" % c["OFFICER"]
    comments += "\nType: %s" % c["CASETYPE"]
    comments += "\nValid: %s" % c["COMPVALID"]
    comments += "\nCondition: %s" % c["ANMLCOND"]
    if type(comments) == unicode: comments = comments.encode("ascii", "xmlcharrefreplace")
    ac.CallNotes = comments
    if c["ANIMALNO"] != "Unspecified" and ppa.has_key(c["ANIMALNO"]):
        animalcontrolanimal.append("INSERT INTO animalcontrolanimal (AnimalID, AnimalControlID) VALUES (%d, %d);" % (ppa[c["ANIMALNO"]].ID, ac.ID))

for a in animals:
    print a
for o in owners:
    print o
#for m in movements:
#    print m
#for od in ownerdonations:
#    print od
#for ol in ownerlicences:
#    print ol
for ac in animalcontrol:
    print ac
for aca in animalcontrolanimal:
    print aca

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

