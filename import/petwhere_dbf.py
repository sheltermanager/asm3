#!/usr/bin/python

import asm

"""
Import script for Petwhere DBF databases, 

covers animal, people, addresses, bites, complaints, licences, payments

note that this is currently animal control focused and will create
non-shelter animals for incident records and with originalowner links.

Pay attention to the encoding - we had one where ascii was fine, but the last import was latin1

9th March, 2016 - 27th April, 2016
"""

PATH = "/home/robin/tmp/asm3_import_data/petwhere_tg1077"

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
for a in asm.read_dbf("%s/ADDRESS.DBF" % PATH):
    addresses[a["ADDRESSNO"]] = a

residences = {}
for r in asm.read_dbf("%s/RESIDENC.DBF" % PATH):
    residences[r["PERSONNO"]] = r

for p in asm.read_dbf("%s/PERSON.DBF" % PATH):
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

for d in asm.read_dbf("%s/ANIMAL.DBF" % PATH):
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
    a.Archived = 1

# Mark the orignal owner of the animal based on the ownershp table
for s in asm.read_dbf("%s/OWNERSHP.DBF" % PATH):
    a = None
    o = None
    if ppo.has_key(s["PERSONNO"]):
        o = ppo[s["PERSONNO"]]
    if ppa.has_key(s["ANIMALNO"]):
        a = ppa[s["ANIMALNO"]]
    if a is not None and o is not None and s["RELATIONSH"].find("Owner") != -1:
        a.OriginalOwnerID = o.ID

for p in asm.read_dbf("%s/PAYMENTS.DBF" % PATH):
    od = asm.OwnerDonation()
    ownerdonation.append(od)
    if ppo.has_key(p["PERSONNO"]):
        o = ppo[p["PERSONNO"]]
        od.ReceiptNumber = p["PAYMENTNO"]
        od.OwnerID = o.ID
        od.Donation = int(p["PAIDAMT"] * 100)
        od.Date = p["DATE"]
        od.DonationTypeID = 1
        od.DonationPaymentID = 1 # Cash
        if p["CHECKAMT"] > 0: od.DonationPaymentID = 2 # Cheque
        if p["CHARGEAMT"] > 0: od.DonationPaymentID = 3 # CC
        if p["CHECKREF"].strip() != "": od.ChequeNumber = p["CHECKREF"]

for l in asm.read_dbf("%s/LICENSES.DBF" % PATH):
    if l["LUPTDT"] is None or l["LICENSENO"].strip() == "": continue
    if ppa.has_key(l["ANIMALNO"]):
        a = ppa[l["ANIMALNO"]]
        if a.OriginalOwnerID > 0:
            ol = asm.OwnerLicence()
            ownerlicence.append(ol)
            ol.OwnerID = a.OriginalOwnerID
            ol.LicenceTypeID = 1
            ol.LicenceNumber = "%s (%d)" % (l["LICENSENO"], ol.ID)
            ol.LicenceFee = 0
            ol.IssueDate = l["LUPTDT"]
            ol.ExpiryDate = l["EXPIRATION"]
            if ol.ExpiryDate is None: ol.ExpiryDate = asm.add_days(ol.IssueDate, 365)

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

try:
    for c in asm.read_dbf("%s/COMPLNTS.DBF" % PATH, encoding="latin1"):
        ac = asm.AnimalControl()
        animalcontrol.append(ac)
        if c["COMPLANANT"] != "Unspecified" and ppo.has_key(c["COMPLANANT"]):
            ac.CallerID = ppo[c["COMPLANANT"]].ID
        if c["OWNER"] != "Unspecified" and ppo.has_key(c["OWNER"]):
            ac.OwnerID = ppo[c["OWNER"]].ID
        ac.CallDateTime = c["OPENDT"]
        if ac.CallDateTime is None: ac.CallDateTime = c["LUPTDT"]
        if ac.CallDateTime is None: ac.CallDateTime = asm.now()
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
except:
    pass # we had a corrupted file from a customer, that's why this is here

for c in asm.read_dbf("%s/BITES.DBF" % PATH, encoding="latin1"):
    ac = asm.AnimalControl()
    animalcontrol.append(ac)
    if c["VICTIMNO"] != "Unspecified" and ppo.has_key(c["VICTIMNO"]):
        ac.CallerID = ppo[c["VICTIMNO"]].ID
        ac.VictimID = ppo[c["VICTIMNO"]].ID
    if c["OWNER"] != "Unspecified" and ppo.has_key(c["OWNER"]):
        ac.OwnerID = ppo[c["OWNER"]].ID
    ac.CallDateTime = c["OPENDT"]
    if ac.CallDateTime is None: ac.CallDateTime = c["LUPTDT"]
    if ac.CallDateTime is None: ac.CallDateTime = asm.now()
    ac.IncidentDateTime = ac.CallDateTime
    ac.DispatchDateTime = ac.CallDateTime
    ac.CompletedDate = c["CLOSEDT"]
    ac.IncidentTypeID = 5
    ac.DispatchAddress = c["BITEADDR"]
    comments = asm.nulltostr(c["BITEMEMO"])
    comments += "\nReport By: %s" % c["REPORTBY"]
    comments += "\nOfficer: %s" % c["OFFICER"]
    comments += "\nSeverity: %s" % c["SEVERITY"]
    comments += "\nOwner Statement: %s" % c["OWNERSTMT"]
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
for od in ownerdonation:
    print od
for ol in ownerlicence:
    print ol
for ac in animalcontrol:
    print ac
for aca in animalcontrolanimal:
    print aca

#asm.stderr_allanimals(animals)
#asm.stderr_onshelter(animals)
asm.stderr_summary(animals=animals, owners=owners, animalcontrol=animalcontrol, ownerlicences=ownerlicence, ownerdonations=ownerdonation)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

