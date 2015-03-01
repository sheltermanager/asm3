#!/usr/bin/python

"""
Allows for quick generation of online forms. This allows you to
specify the online form info in this python file, run it and
get INSERT statements for your database. Just update the fields
below.
"""

YESNO = 0
TEXT = 1
NOTES = 2
LOOKUP = 3
SHELTERANIMAL = 4
ADOPTABLEANIMAL = 5
COLOUR = 6
BREED = 7
SPECIES = 8
RAWMARKUP = 9
DATE = 10

NEXT_ONLINEFORM_ID = 100
NEXT_ONLINEFORMFIELD_ID = 100
FORM_NAME = "Your form name"

# Field layout
# ( "fieldname", "label", TYPE, mandatory T/F, displayindex, "lookups", "tooltip/rawmarkup" )
FIELDS = (
    ( "fieldname", "label", TEXT, False, 10, "lookups", "tooltip" ),
)

for x in FIELDS:
    if len(x) < 7:
        print x

print "INSERT INTO onlineform (ID, Name) VALUES (%d, '%s');" % (NEXT_ONLINEFORM_ID, FORM_NAME)
nextfieldid = NEXT_ONLINEFORMFIELD_ID
for fieldname, label, fieldtype, mandatory, displayindex, lookups, tooltip in FIELDS:
    print "INSERT INTO onlineformfield (ID, OnlineFormID, FieldName, FieldType, DisplayIndex, Mandatory, Label, Lookups, Tooltip) " \
        "VALUES (%d, %d, '%s', %d, %d, %d, '%s', '%s', '%s');" % \
        ( nextfieldid, NEXT_ONLINEFORM_ID, fieldname, fieldtype, displayindex, mandatory and 1 or 0, label, lookups, tooltip)
    nextfieldid += 1

