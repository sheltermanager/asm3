.. _onlineformfields:

Appendix: Online Form import fields
===================================

ASM will recognise fields with the following names when receiving incoming
online form submissions. These can be used to create person, lost animal, found
animal, incident and waiting list records as well as attach to existing 
animal records.

title / title2
    The person's title, eg: Mr
    Person fields suffixed with 2 update the second person for couple records
initials / initials2
    The person's initials
forenames / firstname / forenames2 / firstname2
    The person's first name
surname / lastname / surname2 / lastname2
    The person's last name
address
    The person's address
town / city
    The person's town or city
county / state
    The person's county or state
postcode / zipcode
    The person's postcode or zipcode
hometelephone
    The person's home phone number
worktelephone / worktelephone2
    The person's work phone number
mobiletelephone / celltelephone / mobiletelephone2 / celltelephone2
    The person's mobile number
emailaddress / emailaddress2
    The person's email address
dateofbirth / dateofbirth2
    The person's date of birth
idnumber / idnumber2
    The person's ID number (passport, driving license, national ID card, etc)
excludefrombulkemail
    If this field is supplied and not a blank or "No" in your language, the exclude from bulk email flag will be set for the created person
comments
    The comments field for the animal (for historical reasons, comments populates the animal's description field), person, lost, found or waiting list animal
description
    The description for the lost, found or waiting list animal
reason
    The reason the person is putting their animal on the waiting list (or reason for entry if creating an animal)
type
   The animal type for the animal. ASM will try and guess based on the text which one is meant. Use a lookup field to limit the choices to known items.
species
    The species of the animal. ASM will try and guess based on the text which one is meant. Use a lookup field to limit the choices to known items (or use the Species field type)
breed1 / breed2
    The breed of the animal. ASM will try and guess one of it's lookup values (or use the Breed field type to limit to them)
agegroup
    The age group of the animal. Again, ASM will try and guess one if it's internal values.
color / colour
    The colour of the animal. ASM will try and guess a match (or use the Color field type to limit to them)
sex
    The sex of the animal. ASM will look at the first letter of the value for an M or F
neutered
    Whether the animal is neutered/spayed. Should be a checkbox or Yes/No field and should contain a value that translates to Yes or on.
weight
    The weight of the animal in system units (lb or kg). Should not contain anything but numbers and optionally a decimal mark.
datelost
   The date the animal was lost (lost animals only)
datefound
   The date the animal was found (found animals only)
arealost
    The area the animal was lost in (lost animals only)
areafound
    The area the animal was found in (found animals only)
areapostcode / areazipcode
    The postcode/zipcode area the animal was lost or found in
microchip
   The animal's microchip number
animalname
    The name of an existing shelter animal to attach this form to if specified (use the adoptable/shelter animal field types to get a valid animal name from your form)
reserveanimalname[x]
    The name of a shelter/adoptable animal to reserve to the imported person record. This is useful when creating adoption application forms to automatically tie the person to the animal they are interested in adopting. Unlike the other keys, you can add a numeric suffix to have multiple animals reserved by the imported person (eg: reserveanimalname1, reserveanimalname2...)
callnotes
   When creating an incident, the incident notes
dispatchaddress / dispatchcity / dispatchstate / dispatchzipcode
   The dispatch address for an incident
