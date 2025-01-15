.. _csvimportfields:

Appendix: CSV file import fields
================================

ASM will recognise columns with the following names when importing CSV files.
Where you wish to supply multiple rows for the same animal (such as for
vaccinations or regimens), make sure you have a populated ANIMALCODE column,
similarly for multiple rows to people (such as movements, licenses, etc) make
sure you have populated person data.

When processing animal records that already exist, there are certain key fields
that will be overwritten on the existing animal from the CSV data if those columns
exist in the CSV data and have a value for that row. 

These fields are:

* ANIMALCOMMENTS / ANIMALDESCRIPTION / ANIMALWARNING
* ANIMALDECEASEDDATE
* ANIMALDECEASEDNOTES
* ANIMALDECEASEDREASON
* ANIMALDOB
* ANIMALEUTHANIZED
* ANIMALFLAGS
* ANIMALHEALTHPROBLEMS. 
* ANIMALLOCATION / ANIMALUNIT
* ANIMALMICROCHIP / ANIMALMICROCHIPDATE
* ANIMALNEUTERED / ANIMALNEUTEREDDATE
* ANIMALPICKUPADDRESS
* ANIMALPICKUPLOCATION

This allows you to use a spreadsheet of data to update many animals on chipping/neutering
days (for example), or update many animal bios in one go.

When importing incident data from CSV files, the person fields supplied will be used as
the caller.

ANIMALCODE
    A code for the animal. If supplied, it will set the sheltercode and short sheltercode fields. If not supplied, the system will generate a code for the animal to the appropriate scheme. If you have manual codes turned on and no animal code is supplied, an error message will be displayed and the import abandoned.
ANIMALLITTER
    A litter reference for the animal. Animals with the same reference can be viewed together with the "littermates" button on animal records.
ANIMALNAME
    The animal's name.
ANIMALIMAGE
    A photo for the animal, it can either be an absolute HTTP URL to a JPG image OR a base64 encoded JPG expressed as a data URI.
ANIMALPDFDATA
    A PDF file to attach to the animal. Like image, it can be an absolute URL or a base64 encoded PDF as a data URI.
ANIMALPDFNAME
    The filename associated with the PDF data.
ANIMALNONSHELTER
    Y/N to indicate whether this animal is a owned by a member of the public and not a shelter animal.
ANIMALNOTFORADOPTION
    Y/N to indicate whether this animal is not available for adoption (Y is not available).
ANIMALTRANSFER
    Y/N to indicate whether this animal as transferred in. If set to Y, the ORIGINALOWNER fields will be used in the "Transferred From" field.
ANIMALFLAGS
    A comma separated list of animal flags, including builtins courtesy,
    crueltycase, notforadoption, notforregistration, nonshelter, quarantine.
ANIMALSEX
    The animal's gender. ASM looks for the initial letter “M” in the string to indicate male, "F" for Female or "U" for Unknown.
ANIMALTYPE
    The animal's type. This should correspond to one of ASM's animal types from your database.
ANIMALCOLOR
    The animal's color. This should correspond to a color in your database.
ANIMALCOATTYPE
    The animal's coat type. This should correspond to a coat type in your database.
ANIMALBREED1
    The animal's primary breed. It should match a breed in your database.
ANIMALBREED2
    The animal's secondary breed. If different from ANIMALBREED1, ASM will mark the animal as a crossbreed.
ANIMALDOB
    The animal's date of birth. This field, or ANIMALAGE must be supplied or the record will not be imported.
ANIMALSIZE
    The animal's size. This should correspond to a size in your database.
ANIMALWEIGHT
    The animal's weight as a floating point number of pounds or kilos (eg: 2.5 = 2 lb and 8 oz).
ANIMALAGE
    The animal's current age in years. ASM will calculate a date of birth from this during import if ANIMALDOB is not supplied or blank.
ANIMALLOCATION
    The animal's location within your shelter. This should correspond to a location in your database.
ANIMALUNIT
    The unit within the animal's location within the shelter, eg: pen/cage number.
ANIMALJURISDICTION
    The jurisidiction to allocate the animal to based on entry circumstances (usually pickup).
ANIMALPICKUPLOCATION
    The location where the animal was picked up. This should match a value in the pickup location lookup.
ANIMALPICKUPADDRESS
    The address where the animal was picked up.
ANIMALSPECIES
    The animal's species. This should match a species in your database.
ANIMALCRATETRAINED
    Y/N/U to indicate yes/no/unknown.
ANIMALHOUSETRAINED
    Y/N/U to indicate yes/no/unknown.
ANIMALENERGYLEVEL
    Y/N/U to indicate yes/no/unknown.
ANIMALGOODWITHCATS
    Y/N/U to indicate yes/no/unknown.
ANIMALGOODWITHDOGS
    Y/N/U to indicate yes/no/unknown.
ANIMALGOODWITHELDERLY
    Y/N/U to indicate yes/no/unknown.
ANIMALGOODWITHKIDS
    Y/N/U to indicate yes/no/unknown.
ANIMALGOODONLEAD
    Y/N/U to indicate yes/no/unknown.
ANIMALDESCRIPTION
    Some comments to put in the animal's description field.
ANIMALHIDDENDETAILS
    Some comments for the animal's hidden details field.
ANIMALMARKINGS
    Some comments for the animal's markings field.
ANIMALHEALTHPROBLEMS
    Some comments for the animal's health problems field.
ANIMALWARNING
    A popup warning to display when viewing the animal record.
ANIMALNEUTERED
    Y/N to indicate yes/no.
ANIMALNEUTEREDDATE
    The date the animal was neuteured. If supplied and not blank, ANIMALNEUTERED = Y is also assumed.
ANIMALMICROCHIP
    If not blank, ASM will mark the animal microchipped with this as the microchip number.
ANIMALMICROCHIPDATE
    The date the microchip was implanted.
ANIMALTATTOO
    If not blank, ASM will mark the animal tattooed with this as the tattoo number.
ANIMALTATTOODATE
    The date the tattoo was implanted.
ANIMALDECLAWED
    Y/N to indicate yes/no.
ANIMALHASSPECIALNEEDS
    Y/N to indicate yes/no.
ANIMALENTRYDATE
    The date the animal entered the shelter (date brought in). Today's date will be used if this column is not present or the value is blank.
ANIMALENTRYTIME
    The time the animal entered the shelter. These should be in 24 hour clock format with either 4 or 6 digits if seconds are included, seperated by colons.    
ANIMALENTRYCATEGORY
    The animal's entry category, which should correspond to an entry category in your database.
ANIMALENTRYTYPE
    The animal's entry type, which should be one of the fixed entry types, Surrender, Stray, Transfer In, etc.
ANIMALREASONFORENTRY
    Free text, notes on the reason the animal entered the shelter.
ANIMALDECEASEDDATE
    If the animal is deceased, the date it died.
ANIMALDECEASEDREASON
    The death category for the animal, which should correspond to one in your database.
ANIMALDECEASEDNOTES
    The notes about the animal's death.
ANIMALEUTHANIZED
    Y/N to indicate whether the animal was euthanized.
ANIMALADDITIONAL<fieldname>
    If you have animal additional fields defined, you can put the uppercased version of their name as a suffix to this. Eg, for an additional field called Weight, ANIMALADDITIONALWEIGHT.
COSTTYPE
    The cost type to use (should correspond to a cost type in your database).
COSTDATE
    The date of the cost on this line.
COSTAMOUNT
    The amount of the cost on this line.
COSTDESCRIPTION
    A description of the cost on this line.
CURRENTVETTITLE
    If we have current vet info for the animal, the vet's title.
CURRENTVETINITIALS
    Vet's initials.
CURRENTVETFIRSTNAME
    The vet's first name(s).
CURRENTVETLASTNAME
    The vet's last name. This column being present and having data in it determines whether or not the importer will consider the animal as having current vet info. If ANIMALNEUTEREDDATE is included in the file along with CURRENTVET info, then the neutering vet will be copied from the current vet info.
CURRENTVETADDRESS
    Vet's address.
CURRENTVETCITY
    The vet's city/town.
CURRENTVETSTATE
    The vet's state/county.
CURRENTVETZIPCODE
    The vet's zip or postcode.
CURRENTVETJURISDICTION
    The vet's jurisdiction.
CURRENTVETHOMEPHONE
    The vet's home phone.
CURRENTVETWORKPHONE
    The vet's work phone.
CURRENTVETCELLPHONE
    The vet's mobile phone.
CURRENTVETEMAIL
    The vet's email.
CURRENTVETADDITIONAL<fieldname> 
    If you have person additional fields defined, you can put the uppercased version of their name as a suffix to this. Eg, for an additional field called DateOfBirth CURRENTVETADDITIONALDATEOFBIRTH.
DIARYDATE
    The date of the diary entry.
DIARYFOR
    The person the diary note is for.
DIARYSUBJECT
    The subject of the diary note.
DIARYNOTE
    The diary note section.
DONATIONDATE
    The date the donation amount on this line was received. If movement columns are present, it will be attached to the movement as well as the person. If no person columns are present, having this column in the CSV file will cause an error.
DONATIONAMOUNT
    The amount of the donation on this line (as a floating point number).
DONATIONFEE
   The amount of any transaction fee in handling the donation.
DONATIONCHECKNUMBER
    The cheque/check number for the donation.
DONATIONCOMMENTS
    Any comments to go with the donation.
DONATIONPAYMENT
    The payment method to use (should correspond to a payment method in your database, eg: Cash).
DONATIONTYPE
    The payment type to use (should correspond to a payment type in your database).
DONATIONGIFTAID
    Y / N if the payment should have the giftaid flag set.
INCIDENTDATE
    The date of the incident and call.
INCIDENTTIME
    The time of the incident. These should be in 24 hour clock format with either 4 or 6 digits if seconds are included, seperated by colons.    
INCIDENTCOMPLETEDDATE
    The date the incident was completed.
INCIDENTCOMPLETEDTIME
    The time the incident was completed should be in 24 hour clock format with either 4 or 6 digits if seconds are included, seperated by colons.  
INCIDENTCOMPLETEDTYPE
    The incident completion disposition.
INCIDENTRESPONDEDDATE
    The date the officer responded to the incident.
INCIDENTFOLLOWUPDATE
    The date of follow for the incident.
INCIDENTTYPE
    The type for the incident (should correspond to an incident type in your database).
INCIDENTNOTES
    The call notes for the incident.
DISPATCHACO
    The animal control officer dispatched to the incident .
DISPATCHDATE
    The date the officer was dispatched to the incident.   
DISPATCHTIME
    The time the officer was dispatched to the incident. Should be in 24 hour clock format with either 4 or 6 digits if seconds are included, seperated by colons. 
DISPATCHADDRESS
    The dispatch address for the incident.
DISPATCHCITY
    The dispatch city.
DISPATCHSTATE
    The dispatch state.
DISPATCHZIPCODE
    The dispatch zipcode.
INCIDENTANIMALSPECIES
    The species of animal involved in the incident.
INCIDENTANIMALSEX
    The sex of the animal involved in the incident.
INCIDENTANIMALDESCRIPTION
    Description of the animal involved in the incident.
LICENSETYPE
    The license type to use (licenses need at least person info).
LICENSENUMBER
    The license number (mandatory).
LICENSEFEE
    The fee paid for the license.
LICENSEISSUEDATE
    The date the license was issued.
LICENSEEXPIRESDATE
    The date the license expires.
LICENSECOMMENTS
    Any comments on the license
LOGDATE
   The date of any log entry (only animal logs can be imported).
LOGTIME
   The time of any log entry. Should be in 24 hour clock format with either 4 or 6 digits if seconds are included, seperated by colons.  
LOGTYPE
   The type of log entry.
LOGCOMMENTS
   The log entry itself.
MEDICALNAME
    The name of the medical regimen for this line.
MEDICALDOSAGE
    The dosage of the medical regimen.
MEDICALGIVENDATE
    The date the medical regimen started (only one-off treatment regimens can be created via import).
MEDICALCOMMENTS
    Any comments on the medical regimen.
MOVEMENTTYPE
    The type of movement for this line (0 = Reservation, 1 = Adoption, 2 = Foster, 3 = Transfer, 4 = Escaped, 5 = Reclaimed, 6 = Stolen, 7 = Released to Wild, 8 = Moved to Retailer. If MOVEMENTTYPE is not specified, but a MOVEMENTDATE has been given, ASM will default the type to adoption. If MOVEMENTTYPE is 0, then MOVEMENTDATE and MOVEMENTRETURNDATE will be used to set the reservation date and reservation cancelled date fields.
MOVEMENTDATE
    The date of the movement.
MOVEMENTRETURNDATE
    The return date of the movement.
MOVEMENTCOMMENTS
    Any comments for the movement.
ORIGINALOWNERTITLE
    If we have original owner info for the animal, the person's title. If the animal has been marked as non-shelter, the ORIGINALOWNER will become the animal's owner.
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
ORIGINALOWNERJURISDICTION
    The original owner's jurisdiction.
ORIGINALOWNERHOMEPHONE
    The original owner's home phone.
ORIGINALOWNERWORKPHONE
    The original owner's work phone.
ORIGINALOWNERCELLPHONE
    The original owner's mobile phone.
ORIGINALOWNEREMAIL
    The original owner's email.
ORIGINALOWNERWARNING
    A popup warning to display when viewing the original owner record.
ORIGINALOWNERFLAGS
    This column can be used to set any other person flags on the original owner. Flags should be comma separated with no extra spaces. Built in flags are their lower case English names, eg: banned,aco,homechecked,homechecker,excludefrombulkemail
    Additional flags that you have added to the system should exactly match their flag names as they appear on the person screens, eg: banned,Fundraising Flag 1,Custom Flag.
ORIGINALOWNERADDITIONAL<fieldname> 
    If you have person additional fields defined, you can put the uppercased version of their name as a suffix to this. Eg, for an additional field called DateOfBirth ORIGINALOWNERADDITIONALDATEOFBIRTH.
PERSONCLASS
    1 = Individual, 2 = Organisation.
PERSONTITLE
    The person's title.
PERSONINITIALS
    The person's initials.
PERSONFIRSTNAME
    The person's first name (forenames).
PERSONLASTNAME
    The person's last name (surname).
PERSONNAME
    If this field is supplied, ASM will assume it contains first names and a last name, overriding any fields that set those. Everything up to the last space is considered first names and everything up to the last space the last name.
PERSONADDRESS
    The person's address.
PERSONCITY
    The person's town/city.
PERSONSTATE
    The person's state/county.
PERSONZIPCODE
    The person's zip or postcode.
PERSONJURISDICTION
    The person's jurisdiction.
PERSONHOMEPHONE
    The person's home phone number.
PERSONWORKPHONE
    The person's work phone number.
PERSONCELLPHONE
    The person's cell/mobile number.
PERSONEMAIL
    The person's email address.
PERSONGDPRCONTACTOPTIN
    The GDPR contact optin values, separated by a comma. These values are: didnotask, declined, email, post, sms, phone.
PERSONMEMBER
    Y or 1 in this column to indicate the person should have the membership flag set.
PERSONMEMBERSHIPNUMBER
    The person's membership number.
PERSONMEMBERSHIPEXPIRY
    A date for when this person's membership expires.
PERSONFOSTERER
    Y or 1 in this column to indicate the person should have the fosterer flag set.
PERSONFOSTERCAPACITY
    The number of animals this person is willing to foster.
PERSONDONOR
    Y or 1 in this column to indicate the person is a regular donor.
PERSONFLAGS
    This column can be used to set any other person flags on the imported person. Flags should be comma separated with no extra spaces. Built in flags are their lower case English names, eg: banned,aco,homechecked,homechecker,excludefrombulkemail
    Additional flags that you have added to the system should exactly match their flag names as they appear on the person screens, eg: banned,Fundraising Flag 1,Custom Flag.
PERSONCOMMENTS
    Any comments to go with the person record.
PERSONWARNING
    A popup warning to display when viewing the person record.
PERSONMATCHACTIVE
    Y or 1 in this column indicates the person is looking for an animal. If this field is not set to Y or 1, the other PERSONMATCH columns are ignored for this row.
PERSONMATCHADDED
    The date the system should start looking for matches.
PERSONMATCHEXPIRES
    The date the system should stop looking for matches.
PERSONMATCHSEX
    The gender. ASM looks for the initial letter “M” in the string to indicate male, "F" for Female, "U" for Unknown or "A" for any.
PERSONMATCHSIZE
    The size of the animal the person is looking for.
PERSONMATCHCOLOR
    The color of the animal the person is looking for.
PERSONMATCHAGEFROM, PERSONMATCHAGETO
    The age range of the animal the person is looking for in years.
PERSONMATCHTYPE
    The animal type of the animal the person is looking for.
PERSONMATCHSPECIES
    The species of animal the person is looking for.
PERSONMATCHBREED1, PERSONMATCHBREED2
    The breed of the animal the person is looking for
PERSONMATCHGOODWITHCATS, PERSONMATCHGOODWITHDOGS, PERSONMATCHGOODWITHCHILDREN, PERSONMATCHHOUSETRAINED
    The good with/housetrained flags of the animal the person is looking for.
PERSONMATCHCOMMENTSCONTAIN
    The animal this person is looking for will have this value in its comments.
PERSONADDITIONAL<fieldname>
    If you have person additional fields defined, you can put the uppercased version of their name as a suffix to this. Eg, for an additional field called DateOfBirth PERSONADDITIONALDATEOFBIRTH.
PERSONIMAGE
    A photo for the person, it can either be an absolute HTTP URL to a JPG image OR a base64 encoded JPG expressed as a data URI.
PERSONPDFDATA
    A PDF file to attach to the person. Like image, it can be an absolute URL or a base64 encoded PDF as a data URI.
PERSONPDFNAME
    The filename associated with the PDF data.
TESTTYPE
   The type of test on this line.
TESTRESULT
   The test result.
TESTDUEDATE
   The due date for the test.
TESTPERFORMEDDATE
   The date the test was performed.
TESTCOMMENTS
   Any comments for the test.
VACCINATIONTYPE
    The type of vaccination on this line. 
VACCINATIONDUEDATE
    The due date for the vaccination.
VACCINATIONGIVENDATE
    The date the vaccination was given.
VACCINATIONEXPIRESDATE
    The date the vaccine wears off and needs to be re-administered.
VACCINATIONMANUFACTURER
    The manufacturer of the vaccine.
VACCINATIONBATCHNUMBER
    The serial/batch number of the vaccine.
VACCINATIONRABIESTAG
    The rabies tag accompanying the vaccine.
VACCINATIONCOMMENTS
    Comments on the vaccine.

