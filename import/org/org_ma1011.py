#!/usr/bin/python

import asm

"""
Import script for customer ma1011
13th February, 2016
"""

PATH = "data/ma1011_csv/"

# Files needed
# customers.csv, items.csv, invoices.csv

def getcreateowner(first, last, address, city, state, postal):
    global owners
    global ppo
    k = first + last + address
    if ppo.has_key(k):
        return ppo[k]
    else:
        o = asm.Owner()
        owners.append(o)
        ppo[k] = o
        o.OwnerForeNames = first
        o.OwnerSurname = last
        o.OwnerName = first + " " + last
        o.OwnerAddress = address
        o.OwnerTown = city
        o.OwnerCounty = state
        o.OwnerPostcode = postal
        return o

# --- START OF CONVERSION ---
print "\\set ON_ERROR_STOP\nBEGIN;"

owners = []
ownerdonations = []
donationtypes = []
ppo = {}
ppt = {}

asm.setid("owner", 100)
asm.setid("ownerdonation", 100)
asm.setid("donationtype", 100)

print "DELETE FROM owner WHERE ID >= 100;"
print "DELETE FROM ownerdonation WHERE ID >= 100;"
print "DELETE FROM donationtype WHERE ID >= 100;"

# customers.csv
for row in asm.csv_to_list(PATH + "customers.csv"):
    if ppo.has_key(row["id"]): continue
    o = asm.Owner()
    owners.append(o)
    ppo[row["id"]] = o
    o.OwnerForeNames = row["First"]
    o.OwnerSurname = row["Last"]
    o.OwnerName = o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerAddress = row["Address"]
    o.OwnerTown = row["City"]
    o.OwnerCounty = row["State"]
    o.OwnerPostcode = row["Zip"]
    o.HomeTelephone = row["Phone"]
    o.CreatedDate = asm.getdate_ddmmyyyy(row["DateAdd"])
    o.Comments = row["Notes"]

# items.csv
for row in asm.csv_to_list(PATH + "items.csv"):
    if ppt.has_key(row["Item"]): continue
    dt = asm.DonationType()
    donationtypes.append(dt)
    ppt[row["Item"]] = dt
    dt.Name = "%s - %s" % (row["Item"], row["Desc"])
    dt.Description = row["Desc"]
    dt.DefaultCost = asm.get_currency(row["Amount"])

# invoices.csv
for row in asm.csv_to_list(PATH + "invoices.csv"):
    if not ppt.has_key(row["Item"]): continue
    if not ppo.has_key(row["custid"]): continue
    od = asm.OwnerDonation()
    ownerdonations.append(od)
    dt = ppt[row["Item"]]
    o = ppo[row["custid"]]
    od.OwnerID = o.ID
    od.DonationTypeID = dt.ID
    od.Date = asm.getdate_ddmmyyyy(row["Date"])
    od.Donation = asm.get_currency(row["Amount"])
    od.Quantity = asm.cint(row["Qty"])
    try:
        od.UnitPrice = od.Donation / od.Quantity
    except:
        od.UnitPrice = od.Donation
    od.Comments = row["Desc"]

# Now that everything else is done, output stored records
for o in owners:
    print o
for od in ownerdonations:
    print od
for dt in donationtypes:
    print dt

print "DELETE FROM configuration WHERE ItemName Like 'VariableAnimalDataUpdated';"
print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

