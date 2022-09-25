#!/usr/bin/python

# Import script for Columbia Humane Society, donor list
# 27th March, 2013

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

owners = []
nextoid = 2500
nextdid = 10

def getdate(s, defyear = "12"):
    """ Parses a date in YYYY/MM/DD format. If the field is blank, None is returned """
    if s.strip() == "": return None
    # Throw away time info
    if s.find(" ") != -1: s = s[0:s.find(" ")]
    b = s.split("/")
    # if we couldn't parse the date, use the first of the default year
    if len(b) < 3: return datetime.date(int(defyear) + 2000, 1, 1)
    try:
        year = int(b[0])
        if year < 1900: year += 2000
        return datetime.date(year, int(b[1]), int(b[2]))
    except:
        return datetime.date(int(defyear) + 2000, 1, 1)

def findowner(lastname, address):
    for o in owners:
        if o.OwnerSurname == lastname and o.OwnerAddress == address:
            return o
    return None

print "\\set ON_ERROR_STOP\nBEGIN;"

for fname in [ "012012.csv", "022012.csv", "032012.csv", "042012.csv", "052012.csv", "062012.csv", "072012.csv", "082012.csv", "092012.csv", "102012.csv", "112012.csv", "122012.csv", "2013.csv" ]:

    reader = csv.reader(open(fname), dialect="excel")

    for row in reader:
        # Skip first row of header
        if row[AMOUNT] == "Amount": continue

        # Enough data for row?
        if len(row) < 2: break
        if row[0].strip() == "" and row[1].strip() == "" and row[2].strip() == "": continue

        # Have we already got a record for this owner?
        o = findowner(row[LAST_NAME], row[ADDRESS])
        if o == None:
            o = asm.Owner(nextoid)
            nextoid += 1
            owners.append(o)
            o.OwnerSurname = row[LAST_NAME].strip()
            o.OwnerForeNames = row[FIRST_NAME].strip()
            o.OwnerInitials = row[FIRST_NAME].strip()[0:1].upper()
            o.OwnerAddress = row[ADDRESS].strip()

            csz = re.findall("(.+?), (.+?) (.+?)$", row[CITYSTATEZIP].strip())
            if len(csz) > 0:
                csz = csz[0]
                if len(csz) > 0: o.OwnerTown = csz[0].strip()
                if len(csz) > 1: o.OwnerCounty = csz[1].strip()
                if len(csz) > 2: o.OwnerPostcode = csz[2].strip()

            o.HomeTelephone = row[PHONE].strip()
            o.EmailAddress = row[EMAIL_ADDRESS].strip()
            print o

        # Create the donation
        if row[AMOUNT] != "" and row[AMOUNT] != "0":
            o.IsDonor = 1
            d = asm.OwnerDonation(nextdid)
            nextdid += 1
            d.OwnerID = o.ID
            d.MovementID = 0
            d.AnimalID = 0
            d.DonationTypeID = 1
            d.Date = getdate(row[DATE])
            d.Donation = int(float(row[AMOUNT]) * 100)
            d.Comments = row[SPECIAL_FEATURE].strip()
            print d

        # If there's an item value, put it in the comments
        if row[ITEMS] != "" and row[ITEMS] != "0":
            if o.Comments != "": o.Comments += ", "
            o.Comments += row[ITEMS] + " items donated on " + row[DATE]

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"
