#!/usr/bin/python

import asm

"""
Import script for kb1851 custom spreadsheets

1st September, 2020
"""

PATH = "/home/robin/tmp/asm3_import_data/kb1851_csv"
START_ID = 2000

owners = []
ownerlicence = []
ownerdonation = []
animals = []
animalcontrol = []
animalcontrolanimal = []
ppa = {}
ppo = {}

asm.setid("animal", START_ID)
asm.setid("owner", START_ID)
asm.setid("ownerlicence", START_ID)
asm.setid("animalcontrol", START_ID)

print("\\set ON_ERROR_STOP\nBEGIN;")
print("DELETE FROM animal WHERE ID >= %s AND CreatedBy LIKE 'conversion%%';" % START_ID)
print("DELETE FROM animalcontrol WHERE ID >= %s AND CreatedBy LIKE 'conversion%%';" % START_ID)
print("DELETE FROM owner WHERE ID >= %s AND CreatedBy LIKE 'conversion%%';" % START_ID)
print("DELETE FROM ownerlicence WHERE ID >= %s AND CreatedBy LIKE 'conversion%%';" % START_ID)

def extract_address(s):
    """ Extracts an address from a comma separated list of address items,
        returning address, city, state and zipcode """
    b = s.split(",")
    address = b[0].strip()
    city = b[1].strip()
    state = b[2][:b[2].find(" ")].strip()
    zipcode = b[2][b[2].find(" "):].strip()
    return (address, city, state, zipcode)

def get_owner(s):
    """ Returns an owner object for the fields in supplied in s. 
        s is asterisk separated with the first one or two items usually
        being the address and anything remaining being phone numbers
    """
    gotemail = False
    gotaddress = False
    gotphone = False
    gotcell = False
    o = None
    for i, c in enumerate(s.split("*")):
        x = c.strip()
        if i == 0: # first portion is always name
            # Do we already have an owner with this name? If so, just return it and save time
            if x in ppo: return ppo[x]
            # Otherwise, create the owner and set the name
            o = asm.Owner() 
            owners.append(o)
            o.SplitName(x)
            ppo[x] = o
        # Is this an address?
        elif not gotaddress and (x.find("  94") != -1 or x.find("  96") != -1):
            gotaddress = True
            o.OwnerAddress, o.OwnerTown, o.OwnerCounty, o.OwnerPostcode = extract_address(x)
        # An email?
        elif not gotemail and x.find("@") != -1:
            gotemail = True
            o.EmailAddress = x
        # Must be a phone
        elif not gotphone:
            gotphone = True
            o.HomeTelephone = x
        elif not gotcell:
            gotcell = True
            o.MobileTelephone = x
    return o

def getdate(s):
    """ Returns a python date for s """
    if s == "NA": return None
    return asm.getdate_ddmmyyyy(s)

def get_dispatch_date(s):
    """ Parses one of their dispatch dates """
    if s.strip() == "": return None
    return asm.getdate_mmddyyyy(s[:s.find(" ")])

# People and licenses first
for d in asm.csv_to_list("%s/licenses.csv" % PATH, strip=True):
    if d["Animal People"].strip() == "": continue # Can't do anything without person
    o = get_owner(d["Animal People"].strip())
    ol = asm.OwnerLicence()
    ownerlicence.append(ol)
    ol.OwnerID = o.ID
    ol.LicenceTypeID = 1
    ol.LicenceNumber = d["ID Number"]
    ol.LicenceFee = asm.get_currency(d["License Fee"])
    ol.IssueDate = getdate(d["Issue Date"])
    ol.ExpiryDate = getdate(d["End Date"])
    ol.CreatedBy = "conversion/%s" % d["Issued By"]
    if ol.ExpiryDate is None: ol.ExpiryDate = asm.add_days(ol.IssueDate, 3650)
    ol.Comments = "Item: %s\nAnimal: %s\nReceipt: %s" % (d["Fee Item"], d["Animal Name"], d["Receipt #"])

# People and microchips next
for d in asm.csv_to_list("%s/microchips.csv" % PATH, strip=True):
    if d["Associated people"].strip() == "": continue # Can't do anything without person
    if d["Microchip"].strip() == "": continue # Pointless without an actual microchip
    o = get_owner(d["Associated people"].strip())
    # Bare minimum non-shelter animal record for the microchip
    a = asm.Animal()
    animals.append(a)
    a.AnimalTypeID = 40 # Non-shelter
    a.DateBroughtIn = asm.today()
    a.ShelterCode = "%s (%s)" % (d["Microchip"], a.ID)
    a.ShortCode = d["Microchip"]
    a.NonShelterAnimal = 1
    a.Archived = 1
    a.AnimalName = d["Animal"]
    a.OwnerID = o.ID
    a.OriginalOwnerID = o.ID
    a.IdentichipNumber = d["Microchip"]
    a.Identichipped = 1
    a.SpeciesID = d["Species"] == "Cat" and 2 or 1
    a.Sex = asm.getsex_mf(d["Gender"])
    a.Neutered = d["Altered"] == "Yes" and 1 or 0

# Dispatch/incidents
typemap = {
    "#1 Injured animal": 10,
    "#2 Dangerous": 1,
    "#3 Loose/public safety": 3,
    "#4 Immed cruelty/neg": 7,
    "#5 Police request": 10,
    "#6 Contained stray": 3,
    "#7 Cru/neg not immediate": 7,
    "#8 Unlicensed loose": 3,
    "#9 Defecation": 2,
    "Dead Animal P/U": 6,
    "Barking": 8,
    "Owner Surrender p/u": 3,
    "Misc Animal Control": 10,
    "Cat in Trap Pick Up": 3,
    "Random Stray": 3
}
for d in asm.csv_to_list("%s/dispatch.csv" % PATH, strip=True):
    ac = asm.AnimalControl()
    animalcontrol.append(ac)
    dd = get_dispatch_date(d["DispatchDate"])
    if dd is None:
        dd = asm.today()
        asm.stderr("Bad dispatch date: %s" % d["DispatchDate"])
    ac.CallDateTime = dd
    ac.IncidentDateTime = dd
    ac.DispatchDateTime = dd
    ac.CompletedDate = dd
    ac.IncidentTypeID = 3
    ac.IncidentCompletedID = 3
    if d["Priority"] in typemap:
        ac.IncidentTypeID = typemap[d["Priority"]]
    ac.DispatchAddress = d["Address"]
    ac.DispatchTown = d["City"]
    ac.DispatchCounty = d["State"]
    ac.DispatchPostcode = d["Zip Code"]
    ac.DispatchedACO = d["ACO Assigned"]
    comments = "Case Number: %s" % d["Case Number"]
    comments += "\nSubject: %s" % d["Subject of Call"]
    comments += "\nACO: %s" % d["ACO Assigned"]
    comments += "\nPriority: %s" % d["Priority"]
    comments += "\nEnding Status: %s" % d["Ending Status"]
    comments += "\nDispatcher: %s" % d["Dispatcher"]
    comments += "\nLocation Notes: %s" % d["Location Notes"]
    comments += "\nDispatch Notes: %s" % d["Dispatch Notes"]
    ac.CallNotes = comments

for a in animals:
    print(a)
for o in owners:
    print(o)
for ol in ownerlicence:
    print(ol)
for ac in animalcontrol:
    print(ac)

asm.stderr_summary(animals=animals, owners=owners, animalcontrol=animalcontrol, ownerlicences=ownerlicence)

print("DELETE FROM configuration WHERE ItemName LIKE 'DBView%';")
print("COMMIT;")

