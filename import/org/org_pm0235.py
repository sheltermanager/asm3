#!/usr/bin/python

# Import script for Homeward Bound, owners list
# July 30, 2012

import asm
import csv

def cint(i):
    try:
        return abs(int(i))
    except:
        return 0

print "\\set ON_ERROR_STOP\nBEGIN;"

# Readable references to CSV columns in the file
ID = 0
OWNERTITLE = 1
OWNERINITIALS = 2
OWNERFORENAMES = 3
OWNERSURNAME = 4
OWNERNAME = 5
OWNERADDRESS = 6
OWNERTOWN = 7
OWNERCOUNTY = 8
OWNERPOSTCODE = 9
HOMETELEPHONE = 10
WORKTELEPHONE = 11
MOBILETELEPHONE = 12
EMAILADDRESS = 13
IDCHECK = 14
COMMENTS = 15
ISBANNED = 16
ISVOLUNTEER = 17
ISHOMECHECKER = 18
ISMEMBER = 19
MEMBERSHIPEXPIRYDATE = 20
MEMBERSHIPNUMBER = 21
ISDONOR = 22
ISSHELTER = 23
ISACO = 24
ISSTAFF = 25
ISFOSTERER = 26
ISRETAILER = 27
ISVET = 28
ISGIFTAID = 29
HOMECHECKAREAS = 30
DATELASTHOMECHECKED = 31
HOMECHECKEDBY = 32
MATCHADDED = 33
MATCHEXPIRES = 34
MATCHACTIVE = 35
MATCHSEX = 36
MATCHSIZE = 37
MATCHAGEFROM = 38
MATCHAGETO = 39
MATCHANIMALTYPE = 40
MATCHSPECIES = 41
MATCHBREED = 42
MATCHBREED2 = 43
MATCHGOODWITHCATS = 44
MATCHGOODWITHDOGS = 45
MATCHGOODWITHCHILDREN = 46
MATCHHOUSETRAINED = 47
MATCHCOMMENTSCONTAIN = 48
RECORDVERSION = 49
CREATEDBY = 50
CREATEDDATE = 51
LASTCHANGEDBY = 52
LASTCHANGEDDATE = 53
ADDITIONALFLAGS = 54
reader = csv.reader(open("pm0235.csv"), dialect="excel")
irow = 0
nextid = 20
for row in reader:

    # Skip first row of header
    irow += 1
    if irow < 2: continue

    # Enough data for row?
    if len(row) < 2: break
    if row[0].strip() == "" and row[1].strip() == "" and row[2].strip() == "": continue

    o = asm.Owner(nextid)
    nextid += 1

    o.OwnerTitle = row[OWNERTITLE]
    o.OwnerInitials = row[OWNERINITIALS]
    o.OwnerForeNames = row[OWNERFORENAMES]
    o.OwnerSurname = row[OWNERSURNAME]
    o.OwnerName = row[OWNERNAME]
    o.OwnerAddress = row[OWNERADDRESS]
    o.OwnerTown = row[OWNERTOWN]
    o.OwnerCounty = row[OWNERCOUNTY]
    o.OwnerPostcode = row[OWNERPOSTCODE]
    o.HomeTelephone = row[HOMETELEPHONE]
    o.WorkTelephone = row[WORKTELEPHONE]
    o.MobileTelephone = row[MOBILETELEPHONE]
    o.EmailAddress = row[EMAILADDRESS]
    o.Comments = row[COMMENTS]
    o.IsBanned = cint(row[ISBANNED])
    o.IsVolunteer = cint(row[ISVOLUNTEER])
    o.IsHomeChecker = cint(row[ISHOMECHECKER])
    o.IsMember = cint(row[ISMEMBER])
    o.MembershipNumber = row[MEMBERSHIPNUMBER]
    o.IsDonor = cint(row[ISDONOR])
    o.IsShelter = cint(row[ISSHELTER])
    o.IsACO = cint(row[ISACO])
    o.IsStaff = cint(row[ISSTAFF])
    o.IsFosterer = cint(row[ISFOSTERER])
    o.IsRetailer = cint(row[ISRETAILER])
    o.IsVet = cint(row[ISVET])
    o.IsGiftAid = cint(row[ISGIFTAID])

    print o

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

