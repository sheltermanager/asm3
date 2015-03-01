#!/usr/bin/python

# Import script for Columbia Humane Society, donor list
# 21st April, 2013

import asm
import csv, re, datetime

# Readable references to CSV columns in the file
LAST_NAME = 0
FIRST_NAME = 1
DATE = 2
AMOUNT = 3
ITEMS = 4
ADDRESS = 5
CITYSTATEZIP = 6
PHONE = 7
EMAIL_ADDRESS = 8
SPECIAL_FEATURE = 9

nextdid = 790

def getdate(s, defyear = "12"):
    """ Parses a date in YYYY/MM/DD format. If the field is blank, None is returned """
    if s.strip() == "": return None
    # Throw away time info
    if s.find(" ") != -1: s = s[0:s.find(" ")]
    b = s.split("/")
    if s.find("-") != -1:
        b = s.split("-")
    # if we couldn't parse the date, use the first of the default year
    if len(b) < 3: return datetime.date(int(defyear) + 2000, 1, 1)
    try:
        year = int(b[0])
        if year < 1900: year += 2000
        return datetime.date(year, int(b[1]), int(b[2]))
    except:
        return datetime.date(int(defyear) + 2000, 1, 1)

def findowner(firstname, lastname):
    """ Finds an owner ID, returns None if no first/last name match """
    for o in owners:
        if o.lastname == lastname.strip() and o.firstname == firstname.strip():
            return o.oid
    return None

def finddonation(firstname, lastname, donationdate, donationamount):
    """ Finds an existing donation. Returns true if it exists """
    dd = getdate(donationdate)
    da = 0
    if donationamount.strip() != "":
        da = float(donationamount)
    for o in owners:
        if o.lastname == lastname.strip() and o.firstname == firstname.strip() and o.donationdate == dd and o.donationamount == da:
            return True
    return False

class MiniOwner:
    oid = 0
    firstname = ""
    lastname = ""
    donationdate = None
    donationamount = 0

print "\\set ON_ERROR_STOP\nBEGIN;"

owners = []
reader = csv.reader(open("ch0059_existing.csv"))
for row in reader:
    try:
        o = MiniOwner()
        o.oid = row[0]
        o.firstname = row[1]
        o.lastname = row[2]
        o.donationdate = getdate(row[3])
        if row[4].strip() != "":
            o.donationamount = float(row[4])
        owners.append(o)
    except Exception,err:
        print str(err)
        print row

for fname in [ "201301.csv", "201302.csv", "201303.csv" ]:

    reader = csv.reader(open(fname), dialect="excel")
    for row in reader:
        # Skip first row of header
        if row[AMOUNT] == "Amount": continue

        # Enough data for row?
        if len(row) < 2: break
        if row[0].strip() == "" and row[1].strip() == "" and row[2].strip() == "": continue

        # Have we already got a record for this owner and their donation?
        if not finddonation(row[FIRST_NAME], row[LAST_NAME], row[DATE], row[AMOUNT]):
            # Nope, let's grab the owner record so we can make one
            oid = findowner(row[FIRST_NAME], row[LAST_NAME])
            if oid == None: continue
            
            # Create the donation
            if row[AMOUNT] != "" and row[AMOUNT] != "0":
                d = asm.OwnerDonation(nextdid)
                nextdid += 1
                d.OwnerID = oid
                d.MovementID = 0
                d.AnimalID = 0
                d.DonationTypeID = 1
                d.Date = getdate(row[DATE])
                d.Donation = int(float(row[AMOUNT]) * 100)
                d.Comments = row[SPECIAL_FEATURE].strip()
                print d

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"
