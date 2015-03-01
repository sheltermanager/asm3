#!/usr/bin/python

# Import script for Rawley Penick, cw0243 - volunteer list
# October 11, 2012

import asm
import csv

# Readable references to CSV columns in the file
LAST_NAME = 0
FIRST_NAME = 1
HOME_NUMBER = 2
CELL_NUMBER = 3
EMAIL = 4
ADDRESS = 6
CITYSTZIP = 7
SHIFTS_DUTIES = 8
POSITION_HELD = 9

def city_state_zip(s):
    city = ""
    state = ""
    zipcode = ""
    s = s.strip()
    if s.find(",") != -1:
        city = s[0:s.find(",")]
        chunk = s[s.find(",")+1:].strip()
        bits = chunk.split(" ")
        if len(bits) > 1:
            state = bits[0]
            zipcode = bits[1]
    return (city, state, zipcode)

print "\\set ON_ERROR_STOP\nBEGIN;"

reader = csv.reader(open("caaws_volunteers.csv"), dialect="excel")
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

    o.OwnerSurname = row[LAST_NAME]
    o.OwnerForeNames = row[FIRST_NAME]
    o.OwnerInitials = row[FIRST_NAME][0:1].upper()
    o.OwnerName = row[FIRST_NAME] + " " + row[LAST_NAME]
    o.OwnerAddress = row[ADDRESS]
    city, state, zipcode = city_state_zip(row[CITYSTZIP])
    o.OwnerTown = city
    o.OwnerCounty = state
    o.OwnerPostcode = zipcode
    o.HomeTelephone = row[HOME_NUMBER]
    o.MobileTelephone = row[CELL_NUMBER]
    o.EmailAddress = row[EMAIL]
    o.IsVolunteer = 1
    o.Comments = "Shifts/Duties: " + row[SHIFTS_DUTIES] + ", Position Held: " + row[POSITION_HELD]

    print o

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"
