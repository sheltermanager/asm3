#!/usr/bin/python

# Import script for Homeward Bound, owners list
# July 30, 2012

import asm
import csv

print "\\set ON_ERROR_STOP\nBEGIN;"

# Readable references to CSV columns in the file
LAST = 0
FIRST = 1
ADDRESS = 2
CITY = 3
STATE = 4
ZIP = 5
HOME = 6
WORK = 7
CELL = 8
EMAIL = 9

reader = csv.reader(open("hb.csv"), dialect="excel")
irow = 0
nextid = 15
for row in reader:
    # Skip first row of header
    irow += 1
    if irow < 2: continue

    # Enough data for row?
    if len(row) < 2: break
    if row[0].strip() == "" and row[1].strip() == "" and row[2].strip() == "": continue

    o = asm.Owner(nextid)
    nextid += 1

    o.OwnerSurname = row[LAST]
    o.OwnerForeNames = row[FIRST]
    o.OwnerInitials = row[FIRST][0:1].upper()
    o.OwnerAddress = row[ADDRESS]
    o.OwnerTown = row[CITY]
    o.OwnerCounty = row[STATE]
    o.OwnerPostcode = row[ZIP]
    o.HomeTelephone = row[HOME]
    o.WorkTelephone = row[WORK]
    o.MobileTelephone = row[CELL]
    o.EmailAddress = row[EMAIL]
    o.IsVolunteer = 1

    print o

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"
