.. _csvimportfields:

Appendix: CSV file import fields
================================

ASM will recognise columns with the following names when importing CSV files:

ANIMALCODE
    A code for the animal. If supplied, it will set the sheltercode and short sheltercode fields. If not supplied, the system will generate a code for the animal to the appropriate scheme. If you have manual codes turned on and no animal code is supplied, an error message will be displayed and the import abandoned.
ANIMALNAME
    The animal's name
ANIMALNOTFORADOPTION
    Y/N to indicate whether this animal is not available for adoption (Y is not available).
ANIMALSEX
    The animal's gender. ASM looks for the initial letter “M” in the string to indicate male.
ANIMALTYPE
    The animal's type. This should correspond to one of ASM's animal types from your database.
ANIMALCOLOR
    The animal's color. This should correspond to a color in your database.
ANIMALBREED1
    The animal's primary breed. It should match a breed in your database.
ANIMALBREED2
    The animal's secondary breed. If different from ANIMALBREED1, ASM will mark the animal as a crossbreed.
ANIMALDOB
    The animal's date of birth. This field, or ANIMALAGE must be supplied or the record will not be imported.
ANIMALAGE
    The animal's current age in years. ASM will calculate a date of birth from this during import if ANIMALDOB is not supplied or blank.
ANIMALLOCATION
    The animal's location within your shelter. This should correspond to a location in your database.
ANIMALSPECIES
    The animal's species. This should match a species in your database.
ANIMALHOUSETRAINED
    Y/N/U to indicate yes/no/unknown
ANIMALGOODWITHCATS
    Y/N/U to indicate yes/no/unknown
ANIMALGOODWITHDOGS
    Y/N/U to indicate yes/no/unknown
ANIMALGOODWITHKIDS
    Y/N/U to indicate yes/no/unknown
ANIMALCOMMENTS
    Some comments to put in the animal's comment field.
ANIMALHIDDENDETAILS
    Some comments for the animal's hidden details field.
ANIMALHEALTHPROBLEMS
    Some comments for the animal's health problems field.
ANIMALNEUTERED
    Y/N to indicate yes/no
ANIMALNEUTEREDDATE
    The date the animal was neuteured. If supplied and not blank, ANIMALNEUTERED = Y is also assumed.
ANIMALMICROCHIP
    If not blank, ASM will mark the animal microchipped with this as the microchip number.
ANIMALENTRYDATE
    The date the animal entered the shelter (date brought in). Today's date will be used if this column is not present or the value is blank.
ANIMALREASONFORENTRY
    Free text, notes on the reason the animal entered the shelter.
ANIMALDECEASEDDATE
    If the animal is deceased, the date it died.
ANIMALADDITIONAL<fieldname>
    If you have animal additional fields defined, you can put the uppercased version of their name as a suffix to this. Eg, for an additional field called Weight, ANIMALADDITIONALWEIGHT
DONATIONDATE
    The date the donation amount on this line was received. If movement columns are present, it will be attached to the movement as well as the person. If no person columns are present, having this column in the CSV file will cause an error.
DONATIONAMOUNT
    The amount of the donation on this line (as a floating point number)
DONATIONCOMMENTS
    Any comments to go with the donation
DONATIONPAYMENT
    The payment method to use (should correspond to a payment method in your database, eg: Cash)
DONATIONTYPE
    The payment type to use (should correspond to a payment type in your database).
MOVEMENTTYPE
    The type of movement for this line (1 = Adoption, 2 = Foster, 3 = Transfer, 4 = Escaped, 5 = Reclaimed, 6 = Stolen, 7 = Released to Wild, 8 = Moved to Retailer. If MOVEMENTTYPE is not specified, but a MOVEMENTDATE has been given, ASM will default the type to adoption.
MOVEMENTDATE
    The date of the movement
MOVEMENTCOMMENTS
    Any comments for the movement
ORIGINALOWNERTITLE
    If we have original owner info for the animal, the person's title.
ORIGINALOWNERINITIALS
    Original owner's initials.
ORIGINALOWNERFIRSTNAME
    The original owner's first name(s).
ORIGINALOWNERLASTNAME
    The original owner's last name. This column being present and having data in it determines whether or not the importer will consider the animal as having original owner info.
ORIGINALOWNERADDRESS
    Original owner's address.
ORIGINALOWNERCITY
    The original owner's city/town.
ORIGINALOWNERSTATE
    The original owner's state/county.
ORIGINALOWNERZIPCODE
    The original owner's zip or postcode.
ORIGINALOWNERHOMEPHONE
    The original owner's home phone.
ORIGINALOWNERWORKPHONE
    The original owner's work phone.
ORIGINALOWNERCELLPHONE
    The original owner's mobile phone.
ORIGINALOWNEREMAIL
    The original owner's email.
ORIGINALOWNERADDITIONAL<fieldname> 
    If you have person additional fields defined, you can put the uppercased version of their name as a suffix to this. Eg, for an additional field called DateOfBirth ORIGINALOWNERADDITIONALDATEOFBIRTH
PERSONCLASS
    1 = Individual/Couple, 2 = Organisation
PERSONTITLE
    The person's title
PERSONINITIALS
    The person's initials
PERSONFIRSTNAME
    The person's first name (forenames)
PERSONLASTNAME
    The person's last name (surname)
PERSONNAME
    If this field is supplied, ASM will assume it contains first names and a last name, overriding any fields that set those. Everything up to the last space is considered first names and everything up to the last space the last name.
PERSONADDRESS
    The person's address
PERSONCITY
    The person's town/city
PERSONSTATE
    The person's state/county
PERSONZIPCODE
    The person's zip or postcode
PERSONHOMEPHONE
    The person's home phone number
PERSONWORKPHONE
    The person's work phone number
PERSONCELLPHONE
    The person's cell/mobile number
PERSONEMAIL
    The person's email address
PERSONMEMBER
    Y or 1 in this column to indicate the person should have the membership flag set.
PERSONFOSTERER
    Y or 1 in this column to indicate the person should have the fosterer flag set.
PERSONDONOR
    Y or 1 in this column to indicate the person is a regular donor.
PERSONFLAGS
    This column can be used to set any other person flags on the imported person. Flags should be comma separated with no extra spaces. Built in flags are their lower case English names, eg: banned,aco,homechecked,homechecker
    Additional flags that you have added to the system should exactly match their flag names as they appear on the person screens, eg: banned,Fundraising Flag 1,Custom Flag
PERSONCOMMENTS
    Any comments to go with the person record.
PERSONADDITIONAL<fieldname>
    If you have person additional fields defined, you can put the uppercased version of their name as a suffix to this. Eg, for an additional field called DateOfBirth PERSONADDITIONALDATEOFBIRTH

