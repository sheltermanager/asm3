#!/usr/bin/python

# Import script for Haven of the Ozarks, owners list
# August 13, 2012

import asm
import csv

# Readable references to CSV columns in the file
EARLIEST_DATE = 1
LAST = 2
FIRST = 3
ADDRESS = 4
CITY = 5
STATE = 6
ZIP = 7
HOME = 8
WORK = 9
EMAIL = 10
ADOPTED = 11

print "\\set ON_ERROR_STOP\nBEGIN;"

reader = csv.reader(open("hb0221.csv"), dialect="excel")
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
    o.EmailAddress = row[EMAIL]
    if row[ADOPTED].strip() != "":
        o.Comments = "Adopted: " + row[ADOPTED]

    print o

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"
