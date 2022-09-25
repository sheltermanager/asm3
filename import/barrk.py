#!/usr/bin/env python3

import asm, os

"""
Import module to read from BARRK CSV export.

Last updated 6th Apr, 2022

The following files are needed:

    adopters.csv
    people.csv
    vets.csv
    volunteers.csv (these first 4 are all person records with different extra columns)

    animals.csv (uses adopted/fosterer/deceased info for outcomes and links on person name)
    vet_visits.csv (become medical records)

This file has a load of S3 http links to retrieve application forms and things:

    documents.csv

We can't use data from these files as they are not linked to anything and we have nowhere to put the data:

    costs.csv
    donations.csv
    animal_relations.csv (has person and animal ids, but little else)

These are for stock control (unsupported at the moment, former could be equipment loan and latter is stock - 
    reconsider converting when we have a link between them):

    inventory_assigned.csv
    inventory.csv

There were some file encoding errors, that I corrected with vim by using :set fileencoding=utf-8 and saving

"""

PATH = "/home/robin/tmp/asm3_import_data/barrk_rh2756"

DEFAULT_BREED = 442 # default to mixed breed
START_ID = 100
FETCH_MEDIA = False

animals = []
animalmedicals = []
owners = []
movements = []

ppa = {}
ppo = {}
ppon = {} # lookup for owner via name instead of id

asm.setid("adoption", START_ID)
asm.setid("animal", START_ID)
asm.setid("animalmedical", START_ID)
asm.setid("animalmedicaltreatment", START_ID)
asm.setid("owner", START_ID)
asm.setid("media", START_ID)
asm.setid("dbfs", START_ID)

def getdate(s):
    return asm.getdate_iso(s)

print("\\set ON_ERROR_STOP\nBEGIN;")
print("DELETE FROM adoption WHERE ID >= %s;" % START_ID)
print("DELETE FROM animal WHERE ID >= %s;" % START_ID)
print("DELETE FROM animalmedical WHERE ID >= %s;" % START_ID)
print("DELETE FROM animalmedicaltreatment WHERE ID >= %s;" % START_ID)
print("DELETE FROM owner WHERE ID >= %s;" % START_ID)
print("DELETE FROM media WHERE ID >= %s;" % START_ID)
print("DELETE FROM dbfs WHERE ID >= %s;" % START_ID)

for d in asm.csv_to_list("%s/people.csv" % PATH):
    if d["name"] == "name": continue # skip repeated header rows
    if d["id"] in ppo: continue # skip repeated rows
    # Each row contains a person
    o = asm.Owner()
    owners.append(o)
    ppo[d["id"]] = o
    ppon[d["name"]] = o
    o.SplitName(d["name"], False)
    o.OwnerAddress = d["address"]
    o.OwnerTown = d["city"]
    o.OwnerCounty = d["province"]
    o.OwnerPostcode = d["postal"]
    o.EmailAddress = d["email"]
    o.HomeTelephone = d["phone"]
    o.MobileTelephone = d["phone_cell"]
    if d["donator"] == "true": o.IsDonor = 1
    o.Comments = "group: %s\n%s" % ( d["group"], d["notes"] )
    o.LastChangedDate = getdate(d["updated_at"])

for d in asm.csv_to_list("%s/adopters.csv" % PATH):
    if d["name"] == "name": continue # skip repeated header rows
    if d["id"] in ppo: continue # skip repeated rows
    # Each row contains a person
    o = asm.Owner()
    owners.append(o)
    ppo[d["id"]] = o
    ppon[d["name"]] = o
    o.SplitName(d["name"], False)
    o.OwnerAddress = d["address"]
    o.OwnerTown = d["city"]
    o.OwnerCounty = d["province"]
    o.OwnerPostcode = d["postal"]
    o.EmailAddress = d["email"]
    o.HomeTelephone = d["phone"]
    o.MobileTelephone = d["phone_cell"]
    if d["adopter_unfit"] == "true":
        o.IsBanned = 1
    else:
        o.IsAdopter = 1
    o.Comments = "group: %s\n%s" % ( d["group"], d["notes"] )
    o.CreatedDate = getdate(d["adopter_created_at"])
    o.LastChangedDate = getdate(d["updated_at"])

for d in asm.csv_to_list("%s/vets.csv" % PATH):
    if d["vet_name"] == "vet_name": continue # skip repeated header rows
    if d["id"] in ppo: continue # skip repeated rows
    # Each row contains a person
    o = asm.Owner()
    owners.append(o)
    ppo[d["id"]] = o
    ppon[d["vet_name"]] = o
    o.OwnerType = 2
    o.OwnerName = d["vet_name"]
    o.OwnerSurname = d["vet_name"]
    o.OwnerAddress = d["address"]
    o.OwnerTown = d["city"]
    o.OwnerCounty = d["province"]
    o.OwnerPostcode = d["postal"]
    o.HomeTelephone = d["phone"]
    o.IsVet = 1

for d in asm.csv_to_list("%s/volunteers.csv" % PATH):
    if d["name"] == "name": continue # skip repeated header rows
    if d["id"] in ppo: continue # skip repeated rows
    # Each row contains a person
    o = asm.Owner()
    owners.append(o)
    ppo[d["id"]] = o
    ppon[d["name"]] = o
    o.SplitName(d["name"], False)
    o.OwnerAddress = d["address"]
    o.OwnerTown = d["city"]
    o.OwnerCounty = d["province"]
    o.OwnerPostcode = d["postal"]
    o.EmailAddress = d["email"]
    o.HomeTelephone = d["phone"]
    o.MobileTelephone = d["phone_cell"]
    o.IsVolunteer = d["volunteer_inactive"] == "true" and 0 or 1
    o.IsFosterer = d["volunteer_foster"] == "true" and 1 or 0
    o.IsDriver = d["volunteer_transport_local"] == "true" and 1 or 0
    o.IsStaff = d["volunteer_shelterworker"] == "true" and 1 or 0
    comments = "group: %s\n" % d["group"]
    for x in d.keys():
        if x.startswith("volunteer_"):
            comments += "%s: %s," % (x, d[x])
    comments += "\n%s" % d["notes"]
    o.Comments = comments

for d in reversed(asm.csv_to_list("%s/animals.csv" % PATH)):
    if d["id"] == "id": continue # skip repeated header rows
    if d["id"] in ppa: continue # skip repeated rows
    a = asm.Animal()
    animals.append(a)
    ppa[d["id"]] = a
    # NB: only really seen dogs
    if d["as_animal_type"] == "Dog":
        animaltype = 2
        animalletter = "D"
    else:
        animaltype = 11
        animalletter = "U"
    a.AnimalTypeID = animaltype
    # There is a species column, but the last file I saw it seemed to be pretty optional and not filled in
    a.SpeciesID = asm.species_id_for_name(d["as_animal_type"])
    a.generateCode()
    a.ShortCode = d["id"]
    a.ShelterCode = d["id"]
    a.AnimalName = d["name"]
    a.AcceptanceNumber = d["litter_id"]
    a.DateBroughtIn = getdate(d["intake_date"])
    if a.DateBroughtIn is None: a.DateBroughtIn = getdate(d["created_at"])
    a.DateOfBirth = getdate(d["birthday"])
    if a.DateOfBirth is None: a.DateOfBirth = a.DateBroughtIn
    a.Sex = 1
    if d["gender"] == "1": # They use 1 for female, 0 for male
        a.Sex = 0
    a.Size = asm.cint(d["size_when_grown"])
    primary = d["breed"]
    secondary = d["breed_secondary"]
    asm.breed_ids(a, primary, secondary, DEFAULT_BREED)
    color = d["color_primary"]
    a.BaseColourID = asm.colour_id_for_name(color)
    a.IdentichipNumber = d["tattoo"]
    if a.IdentichipNumber != "": a.Identichipped = 1
    a.Weight = asm.atof(d["weight"])
    a.Neutered = d["altered"] == "true" and 1 or 0
    intaketype = d["intake_reason"]
    if intaketype.find("Transfer In") != -1:
        a.IsTransfer = 1
        a.EntryReasonID = 15
    elif intaketype.find("Stray") != -1:
        a.EntryReasonID = 7
    elif intaketype.find("Surrender") != -1 or intaketype.find("Return") != -1:
        a.EntryReasonID = 17 
    else:
        a.EntryReasonID = 15 # Stray
    a.Fee = asm.cint(d["adoption_fees_amount"]) * 100
    a.HiddenAnimalDetails = "Breed: %s / %s, Color: %s / %s\nIntake Location: %s" % (primary, secondary, color, d["color_secondary"], d["intake_location"])
    if d["foster_tag"] != "": a.HiddenAnimalDetails += "\nFoster Tag: %s" % d["foster_tag"]
    a.HiddenAnimalDetails += d["notes"]
    a.CreatedDate = getdate(d["created_at"])
    a.LastChangedDate = getdate(d["updated_at"])
    o = None
    if d["person_name"] in ppon: o = ppon[d["person_name"]]
    if d["deceased"] == "true":
        a.DeceasedDate = getdate(d["date_of_death"])
        if a.DeceasedDate is None: a.DeceasedDate = a.DateBroughtIn
        a.Archived = 1
        a.PTSReasonID = 2 # Died
        if d["euthanized"] == "true":
            a.PutToSleep = 1
            a.PTSReasonID = 4 # Sick/Injured
    elif d["adopted"] == "true" and o is not None:
        adopteddate = getdate(d["adoption_date"])
        m = asm.Movement()
        movements.append(m)
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = adopteddate
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 1
        a.CreatedDate = m.MovementDate
    elif o is not None:
        # assume the person is the fosterer
        m = asm.Movement()
        movements.append(m)
        o.IsFosterer = 1
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 2
        m.MovementDate = a.DateBroughtIn
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 2
        a.CreatedDate = m.MovementDate

if asm.file_exists("%s/vet_visits.csv" % PATH):
    for d in asm.csv_to_list("%s/vet_visits.csv" % PATH):
        if d["animal_id"] == "animal_id": continue
        if d["animal_id"] not in ppa: continue
        a = ppa[d["animal_id"]]
        meddate = getdate(d["visit_date"])
        m = asm.animal_regimen_single(a.ID, meddate, d["treatment"], "Vet Visit", d["reason"], cost = asm.cfloat(d["cost"])*100)
        animalmedicals.append(m)

if FETCH_MEDIA and asm.file_exists("%s/documents.csv" % PATH):
    for d in asm.csv_to_list("%s/documents.csv" % PATH):
        if d["attachment_type"] == "Animal":
            a = ppa[d["attachment_id"]]
            if a is None: continue
            url = d["url"]
            filename = url[url.rfind("/")+1:]
            data = asm.load_file_from_url(url)
            asm.media_file(0, a.ID, filename, data)
        elif d["attachment_type"] == "Person":
            o = ppo[d["attachment_id"]]
            if o is None: continue
            url = d["url"]
            filename = url[url.rfind("/")+1:]
            data = asm.load_file_from_url(url)
            asm.media_file(3, o.ID, filename, data)

# Allow shelter animals to have their chips registered
for a in animals:
    if a.Archived == 0:
        a.IsNotForRegistration = 0

# Now that everything else is done, output stored records
for a in animals:
    print (a)
for o in owners:
    print (o)
for m in movements:
    print (m)
for am in animalmedicals:
    print (am)

asm.stderr_summary(animals=animals, owners=owners, movements=movements, animalmedicals=animalmedicals)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")
