#!/usr/bin/env python3

import sys
sys.path.insert(0, "..")

import asm, os

"""
Import module for Access DB for stayawhile shelter jm3202

Last updated 3rd Apr, 2024
"""

PATH = "/home/robin/tmp/asm3_import_data/jm3202_access"

DEFAULT_BREED = 261 # default to dsh
DATE_FORMAT = "MDY" # Normally MDY
START_ID = 100

NO_DATE = asm.parse_date("2020-01-01", "%Y-%m-%d")

animals = []
owners = []
ownerdonations = []
movements = []

ppa = {}
ppai = {}
ppo = {}

asm.setid("adoption", START_ID)
asm.setid("animal", START_ID)
asm.setid("owner", START_ID)
asm.setid("ownerdonation", START_ID)

def getdate(s):
    return asm.getdate_mmddyyyy(s)

print("\\set ON_ERROR_STOP\nBEGIN;")
print("DELETE FROM adoption WHERE ID >= %s;" % START_ID)
print("DELETE FROM animal WHERE ID >= %s;" % START_ID)
print("DELETE FROM owner WHERE ID >= %s;" % START_ID)
print("DELETE FROM ownerdonation WHERE ID >= %s;" % START_ID)

for d in asm.csv_to_list("%s/Copy of Supporters.csv" % PATH):
    if d["Last Name"] == "Last Name": continue # skip repeated header rows
    if d["Last Name"].strip() == "": continue # skip blank rows
    # Each row contains a person
    o = asm.Owner()
    owners.append(o)
    ppo[d["Supporters ID"]] = o
    o.OwnerForeNames = d["First Name"].title()
    o.OwnerSurname = d["Last Name"].title()
    o.OwnerAddress = d["Address 1"].title()
    if d["Address 2"] != "":
        o.OwnerAddress += "\n" + d["Address 2"].title()
    o.OwnerTown = d["City"].title()
    o.OwnerCounty = d["State"].upper()
    o.OwnerPostcode = d["Zip"].upper()
    o.EmailAddress = ""
    o.HomeTelephone = d["Home Phone"]
    o.MobileTelephone = d["Cell Phone"]
    o.ExcludeFromBulkEmail = d["Mailing list?"] == 0 and 1 or 0
    if d["Role"] == "Donator": o.IsDonor = 1
    if d["Role"] == "Volunteer": o.IsVolunteer = 1
    if d["Role"] == "Employee": o.IsStaff = 1
    o.Comments = d["Special Abilities"]

for d in asm.csv_to_list("%s/cat names import.csv" % PATH):
    if d["Cat ID"] == "Cat ID": continue # skip repeated header rows
    if d["Cat Name"] == "": continue # skip blank rows
    a = asm.Animal()
    animals.append(a)
    a.AnimalTypeID = 11
    a.SpeciesID = 2
    a.ShortCode = "SA" + d["Cat ID"]
    a.ShelterCode = "SA" + d["Cat ID"]
    ppa[d["Cat Name"]] = a
    ppai[d["Cat ID"]] = a
    a.AnimalName = d["Cat Name"].title()
    broughtin = getdate(d["Arrival or Return Date"])
    dob = getdate(d["Birth Date"])
    if broughtin is None: 
        broughtin = NO_DATE
    if dob is None: 
        a.EstimatedDOB = 1
        dob = broughtin
    a.DateOfBirth = dob
    a.DateBroughtIn = broughtin
    a.CreatedDate = broughtin
    a.LastChangedDate = broughtin
    a.Sex = 1
    if d["Sex"].startswith("F"):
        a.Sex = 0
    a.BreedID = DEFAULT_BREED
    a.Breed2ID = DEFAULT_BREED
    a.BreedName = "Domestic Short Hair"
    a.EntryReasonID = 17
    color = d["Color"].replace("DSH ", "").replace("DMH ", "").replace("DLH ", "")
    a.BaseColourID = asm.colour_id_for_name(color)
    a.HiddenAnimalDetails = "Color: %s" % (color)
    a.ReasonForEntry = "How Obtained: %s" % d["How Obtained"]
    if d["Deceased"] == "1":
        a.DeceasedDate = a.DateBroughtIn
        a.Archived = 1
    if d["Adopted"] == "1":
        a.ActiveMovementDate = a.DateBroughtIn
        a.ActiveMovementType = 1
        a.Archived = 1
    if d["Neuter Date"] != "":
        a.NeuteredDate = getdate(d["Neuter Date"])
        a.Neutered = 1
        a.HiddenAnimalDetails += "\n" + d["Issues"]

for d in asm.csv_to_list("%s/Adoptions.csv" % PATH):
    if d["Cat ID"] == "Cat ID": continue # skip repeated headers
    o = None
    if d["Supporter ID"] in ppo: o = ppo[d["Supporter ID"]]
    a = None
    if d["Cat Name"] in ppa: a = ppa[d["Cat Name"]]
    if o is None or a is None: continue
    # Person has to be an adopter
    o.IsAdopter = 1
    m = asm.Movement()
    m.AnimalID = a.ID
    m.OwnerID = o.ID
    m.MovementType = 1
    m.MovementDate = getdate(d["Date of Adoption"])
    if m.MovementDate is None: 
        m.MovementDate = getdate(d["Date of Birth"])
    if m.MovementDate is None:
        m.MovementDate = NO_DATE
    a.ActiveMovementID = m.ID
    a.ActiveMovementDate = m.MovementDate
    a.ActiveMovementType = 1
    a.Archived = 1
    a.CreatedDate = m.MovementDate
    a.LastChangedDate = m.MovementDate
    movements.append(m)

for d in asm.csv_to_list("%s/Donations.csv" % PATH):
    if d["Supporter ID"] not in ppo: continue
    o = ppo[d["Supporter ID"]]
    od = asm.OwnerDonation()
    od.OwnerID = o.ID
    od.DonationTypeID = 1 # General donation
    if d["Category of Donation"] == "Memory of" or d["Category of Donation"] == "Honor of":
        od.DonationTypeID = 1
    if d["Category of Donation"] == "Adoption":
        od.DonationTypeID = 2
    if d["Category of Donation"] == "Sponsor":
        od.DonationTypeID = 5
    od.DonationPaymentID = 1 # Cash - Default
    if d["Form of Donation"] == "Check":
        od.DonationPaymentID = 2
    od.Donation = asm.get_currency(d["Amount of Donation"])
    od.ChequeNumber = d["Check Number"]
    od.Date = getdate(d["Date of Donation"])
    if od.Date is None: 
        od.Date = NO_DATE
    od.Comments = "Category: %s\n\n%s" % ( d["Category of Donation"], d["Comment for Other"])
    ownerdonations.append(od)

for d in asm.csv_to_list("%s/Sponsors.csv" % PATH):
    if d["Supporter ID"] not in ppo: continue
    o = ppo[d["Supporter ID"]]
    if d["Cat ID"] not in ppai: continue
    a = ppai[d["Cat ID"]]
    od = asm.OwnerDonation()
    od.OwnerID = o.ID
    od.DonationTypeID = 5 # Sponsorship
    od.Donation = 0 # Zero amount on purpose
    od.Date = a.DateBroughtIn
    od.Comments = "Sponsor link"
    ownerdonations.append(od)
    o.IsSponsor = 1

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
for od in ownerdonations:
    print (od)

asm.stderr_summary(animals=animals, owners=owners, movements=movements, ownerdonations=ownerdonations)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")
