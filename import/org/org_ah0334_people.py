#!/usr/bin/python

# Import script for Almost Home pet owner list
# 12th Dec, 2013

import asm
import csv

# Readable references to CSV columns in the file
TAGID = 0
OWNERFIRSTNAME = 1
OWNERLASTNAME = 2
OWNERSTREETADDRESS = 3
OWNERCITY = 4
STATE = 5
OWNERZIP = 6
PETNAME = 7

print "\\set ON_ERROR_STOP\nBEGIN;"

reader = csv.reader(open("ah0334.csv"), dialect="excel")
nextid = 1000
done = {}
for row in reader:
    # Skip first row of header
    if row[TAGID] == "TagID": continue
    # Skip unknown
    if row[OWNERFIRSTNAME].find("nknown") != -1: continue
    # Enough data for row?
    if len(row) < 2: break
    if row[0].strip() == "" and row[1].strip() == "" and row[2].strip() == "": continue
    # Have we already seen this combo
    key = row[OWNERLASTNAME] + "|" + row[OWNERFIRSTNAME] + "|" + row[OWNERSTREETADDRESS]
    if done.has_key(key): continue

    o = asm.Owner(nextid)
    nextid += 1
    o.OwnerSurname = row[OWNERLASTNAME]
    o.OwnerForeNames = row[OWNERFIRSTNAME]
    o.OwnerInitials = row[OWNERFIRSTNAME][0:1].upper()
    o.OwnerAddress = row[OWNERSTREETADDRESS]
    o.OwnerTown = row[OWNERCITY].strip()
    o.OwnerCounty = row[STATE].strip()
    o.OwnerPostcode = row[OWNERZIP]
    o.Comments = "TagID: %s, Pet name: %s" % (row[TAGID], row[PETNAME])
    o.AdditionalFlags = "General Pet Owner|"
    done[key] = "D"

    print o

print "COMMIT;"
