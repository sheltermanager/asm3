#!/usr/bin/python

import csv

LNGSPECIESID = 0
TXTSPECIESDESC = 1
LNGCATEGORYID = 2
LNGCLASSID = 3

print "\\set ON_ERROR_STOP\nBEGIN;"

# Do their species list
reader = csv.reader(open("data/tblAnimalSpeciesType-cvs.csv", "r"), dialect="excel")
for row in reader:
    if row[LNGSPECIESID] == "lngSpeciesID": continue
    spid = int(row[LNGSPECIESID]) + 100
    # Domestic
    if row[LNGCATEGORYID] == "1":
        print "UPDATE animal SET EntryReasonID = 12 WHERE SpeciesID = %d;" % spid
    # Wildlife
    if row[LNGCATEGORYID] == "2":
        print "UPDATE animal SET EntryReasonID = 14 WHERE SpeciesID = %d;" % spid
    # Exotic
    if row[LNGCATEGORYID] == "3":
        print "UPDATE animal SET EntryReasonID = 13 WHERE SpeciesID = %d;" % spid

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

