.. _wordkeys:

Appendix: Wordkeys
==================
 
The following wordkeys are available in different areas of the system when
generating documents from templates. Wordkeys should be placed in your
templates, wrapped in double angle-brackets. Eg: <<AnimalName>> 
 
Organisation Keys
-----------------
 
These keys are available in all types of documents.
 
Organisation
    The shelter's name
OrganisationAddress
    The shelter's address
OrganisationTelephone
    The shelter's telephone number
Date
    Today's date
Username
    The current user generating the document
UserRealname
    The real name of the user generating the document
UserEmailAddress
    The email address of the user generating the document

Animal Keys
-----------

Animal keys are available for documents generated from the animal details and
movement tab of the animal screens. 

DocumentImgLink
    An <img> tag containing a link to the animal's preferred document image.
DocumentImgThumbLink
    An <img> tag containing a link to a thumbnail of the animal's preferred document image.
DocumentQRLink
    An <img> tag containing a link to QR code that references a URL to the animal's record within ASM.
ShelterCode
    The animal's shelter code 
ShortShelterCode
    The shortened version of the shelter code 
Age
    The animal's age in readable form (eg: “5 years and 6 months”) 
AnimalComments
    The animal comment box 
HealthProblems
    The health problems field 
AcceptanceNumber
    The acceptance number 
AddressOfPersonBroughtAnimalIn
    The full address of the person who brought the animal in 
AnimalName
    The animal's name 
AnimalTypeName
    The animal's type 
BaseColourName (BaseColorName for US users)
    The animal's colour 
BreedName
    The animal's breed. If the “Use single breed field” option is not set and
    the animal is a crossbreed, ASM will output the this field as "Breed 1 /
    Breed 2" to indicate that the animal is a cross of two breeds. 
InternalLocation
    The animal's location within the shelter 
LocationUnit
    The location unit (eg, pen or cage number)
DisplayLocation
    Either the internal location if the animal is on shelter, a movement type/person for animals leaving the shelter or a deceased reason if the animal is no longer alive
CoatType
    The animal's coat type 
AnimalComments
    The animal comments box 
AnimalCreatedBy
    The user who created the animal record (AnimalCreatedByName for full user
    name) 
AnimalCreatedDate
    The date the animal record was created 
DateBroughtIn
    The date the animal was first brought to the shelter 
MonthBroughtIn
    The month the animal was first brought to the shelter 
DateOfBirth
    The animal's date of birth 
EstimatedDOB
    The word (estimated) if the estimated date of birth flag is ticked on the animal, or a blank string if not. 
AgeGroup
    The animal's age group (the defaults are Baby, Adult, Young Adult and Senior). These can be configured under the Settings->Options screen. 
DisplayAge
    If the EstimatedDOB flag is set, outputs the age group, if not, outputs a string representation of the animal's age. 
DisplayDOB
    If the EstimatedDOB flag is set, outputs the age group, if not, outputs the animal's date of birth. 
DeceasedDate
    The date the animal died (if applicable) 
DeceasedNotes
    The comments on the animal's death
DeceasedCategory
    The deceased category for the animal
Declawed
    "Yes" if the animal has been declawed 
AnimalID
    The animal's internal ID number 
BondedWith
    A list of the names and codes of animals this one is bonded with 
Fee
    The animal's adoption fee if you are using per-animal adoption fees
MicrochipNumber
    The animal's microchip number 
Microchipped
    "Yes" if the animal has been microchipped 
MicrochipDate
    The date the animal was microchipped 
MicrochipManufacturer
    The manufacturer of the microchip
Tattoo
    "Yes" if the animal has an identifying tattoo 
TattooNumber
    The tattoo number 
TattooDate
    The date the tattoo was applied 
CombiTested (FIVLTested for US users)
    “Yes” if the animal has been combi-tested (or FIV/L testing for the US) 
CombiTestDate (FIVLTestDate for US users)
    The date of the test 
CombiTestResult (FIVResult for US users)
    The test result - Positive or Negative. 
FLVResult
    The result of the FLV test - Positive or Negative 
HeartwormTested
    “Yes” if the animal has been heartworm tested. 
HeartwormTestDate
    The date of the test 
HeartwormTestResult
    The result - positive or negative 
HiddenAnimalDetails
    The hidden details box 
AnimalLastChangedBy
    The user who last changed the animal record (AnimalLastChangedByName for full user name) 
AnimalLastChangedDate
    The date record was last changed 
Markings
    The markings box 
NameOfOwnersVet
    The owner's vet box 
HasSpecialNeeds
    "Yes" if the animal has the box ticked for special needs on the vet tab 
Neutered
    "Yes" if the animal has been neutered/spayed (usually called "altered" or "fixed" in the US) 
NeuteredDate
    The date the animal was neutered 
BroughtInByAddress
    The address of the person who brought the animal in
BroughtInByName
    The name of the person who brought the animal in
BroughtInByTown 
    (BroughtInByCity for US users) 
BroughtInByCounty 
    (BroughtInByState for US users) 
BroughtInByPostcode 
    (BroughtInByZipcode for US users) 
BroughtInByHomePhone
    The home phone number of the person who brought the animal in
BroughtInByWorkPhone 
    The work phone number of the person who brought the animal in
BroughtInByMobilePhone 
    (BroughtInByCellPhone for US users)
BroughtInByEmail
    The email address of the person who brought the animal in
OriginalOwnerAddress
    The address of the animal's original owner 
OriginalOwnerName
    The name of the animal's original owner 
OriginalOwnerTown (OriginalOwnerCity for US users)
    The town of the animal's original owner 
OriginalOwnerCounty (OriginalOwnerState for US users)
    The county of the animal's original owner 
OriginalOwnerPostcode (OriginalOwnerZipcode for US users)
    The original owner's post/zipcode 
OriginalOwnerHomePhone
    The original owner's home phone number 
OriginalOwnerWorkPhone
    The original owner's work phone number 
OriginalOwnerMobilePhone
    The original owner's mobile phone number 
OriginalOwnerEmail
    The original owner's email address 
CurrentOwnerName
    The name of the animal's current owner (fosterer or adopter)
CurrentOwnerAddress 
    Current owner's address
CurrentOwnerTown 
    (CurrentOwnerCity for US users) 
CurrentOwnerCounty 
    (CurrentOwnerState for US users) 
CurrentOwnerPostcode 
    (CurrentOwnerZipcode for US users) 
CurrentOwnerHomePhone 
    Current owner's home phone number
CurrentOwnerWorkPhone 
    Current owner's work phone number
CurrentOwnerMobilePhone 
    Current owner's cell/mobile phone number
CurrentOwnerEmail 
    Current owner's email address
ReservedOwnerName
    The name of the person with an active reserve on the animal
ReservedOwnerAddress 
    Reserved owner's address
ReservedOwnerTown 
    (ReservedOwnerCity for US users) 
ReservedOwnerCounty 
    (ReservedOwnerState for US users) 
ReservedOwnerPostcode 
    (ReservedOwnerZipcode for US users) 
ReservedOwnerHomePhone 
    Reserved owner's home phone number
ReservedOwnerWorkPhone 
    Reserved owner's work phone number
ReservedOwnerMobilePhone 
    Reserved owner's cell/mobile phone number
ReservedOwnerEmail 
    Reserved owner's email address
ReservationStatus
    The active reservation/application status
CurrentVetName
    The name of the animal's current vet
CurrentVetAddress
    The address of the animal's current vet
CurrentVetTown 
    (CurrentVetCity for US users)
CurrentVetCounty 
    (CurrentVetState for US users)
CurrentVetPostcode
    The postal code of the animal's current vet
CurrentVetPhone
    A phone number for the animal's current vet
OwnersVetName
    The owner's vet
OwnersVetAddress
    The address of the owner's vet
OwnersVetTown 
    (CurrentVetCity for US users)
OwnersVetCounty 
    (CurrentVetState for US users)
OwnersVetPostcode
    The postal code of the owner's vet
OwnersVetPhone
    A phone number for the owner's vet
RabiesTag
    The animal's rabies tag 
GoodWithCats
    "Yes/No/Unknown" 
GoodWithDogs
    "Yes/No/Unknown" 
GoodWithChildren
    "Yes/No/Unknown" 
HouseTrained
    "Yes/No/Unknown" 
EntryCategory
    The entry category of the animal 
ReasonForEntry
    The reason the animal was brought to the shelter 
ReasonNotBroughtByOwner
    The reason (if any) that the animal was not brought in by the owner 
Sex
    The animal's sex 
Size
    The animal's size 
Weight
    The animal's weight
SpeciesName
    The animal's species 
ReclaimedDate
    The date (if applicable) that the animal was reclaimed by its owner 
MostRecentEntry
    The date the animal most recently entered the shelter (if it was returned from an adoption or fostering for example) 
MostRecentMonthEntry
    The month the animal most recently entered the shelter 
TimeOnShelter
    A readable string showing the time the animal has spent on the shelter (from the last time it entered), eg: 4 weeks. 
NoTimesReturned
    The number of times the animal has been returned to the shelter 
HasValidMedia
    "Yes" if the animal has a photo flagged for website generation 
WebMediaFilename
    The filename of the animal's default picture 
WebMediaNotes
    The notes to accompany the picture 
WebMediaNew
    "Yes" if the animal has not been published via the web publishing tool 
WebMediaUpdated
    "Yes" if the notes on the media for the animal have been edited since the animal was last published via the web publishing tool 
WebsiteVideoURL
    The web address of the default video link for this animal
WebsiteVideoNotes
    The notes accompanying the video link
AnimalOnShelter
    "Yes" if the animal is on the shelter 
AnimalIsReserved
    "Yes" if the animal has been reserved

Vaccination Keys
----------------

Vaccination keys let you access the vaccination records for an animal. There
are multiple ways of accessing the records. You construct a key that contains
the field name and then an index for it. The field names are:

VaccinationName
    The name of the vaccination (eg: Booster) 
VaccinationRequired
    The date the vaccination is required 
VaccinationGiven
    The date the vaccination was given 
VaccinationExpires
    The date the vaccination expires if known
VaccinationBatch
    The batch number from the vaccination adminstered
VaccinationManufacturer
    The manufacturer of the vaccine
VaccinationCost
    The cost of this vaccine
VaccinationComments
    The vaccination comments
VaccinationDescription
    The vaccination description from the lookup data.

Just putting a number on the end of the fieldname returns that field for the
records, counting from oldest to newest. For example, VaccinationName1 returns
the name of the first vaccination on file for the animal.

You can use the suffix Lastn, where n is a number to count from the newest to
the oldest instead. For example, VaccinationGivenLast1 returns the given date
of the most recent vaccination record.

You can also use the vaccination type itself as an index, for example
VaccinationRequiredDHCPP will return the latest vaccination record of type
DHCPP. If your vaccination type has spaces in its name, then remove them when
constructing the key. Eg: A type of “DHCPP Vacc” would bcome
<<VaccinationRequiredDHCPPVacc>> when accessing it via a wordkey.

The “Recent” keyword operates with the vaccination type and allows you to
select the most recent vaccination of that type that has a non-blank given
date. Eg: VaccinationCommentsRecentDHCPP will return the comments of the last
given DHCPP vaccination.

Test Keys
----------

The same rules for vaccinations apply to reading test records.

TestName
    The name of the test (eg: FIV) 
TestResult
    The test result (eg: Positive)
TestRequired
    The date the test is required 
TestGiven
    The date the test was performed 
TestCost
    The cost of the test
TestComments
    The test comments
TestDescription
    The test description from the lookup data.

Medical Keys
------------

The same rules for vaccinations apply to reading medical records, except the
MedicalName field can be used for looking up the most recent record of that
treatment. In addition, the Recent keyword looks for medical regimens that have
a status of complete.

MedicalName
    The name of the medical treatment 
MedicalFrequency
    How often the treatment is given (eg: Monthly) 
MedicalNumberOfTreatments
    The total number of treatments 
MedicalStatus
    The treatment status (eg: Active) 
MedicalDosage
    The treatment dosage 
MedicalStartDate
    The date treatment started 
MedicalTreatmentsGiven
    How many treatments the animal has had 
MedicalTreatmentsRemaining
    How many treatments are remaining 
MedicalNextTreatmentDue
    The date of the next due treatment in the regimen
MedicalLastTreatmentGiven
    The date the last treatment was given in the regimen
MedicalCost
    The cost of this medical regimen
MedicalComments
    The medical comments 

Payment Keys
------------

If you are creating a document from the animal or person records, then the same
rules apply as for vaccinations and medical records when accessing payments.
payments. The Recent keyword looks for payments that have been received. 

However, if you create an invoice/receipt document from the payment tab of a
person or animal record, you can select multiple payments before creating the
document and access the information by suffixing a number to the end of the
keys listed below (eg: PaymentType1, PaymentComments2)

The fields are:

ReceiptNum
    If you issue receipts for donations, the receipt number 
PaymentType
    The payment type
PaymentMethod
    The payment method
PaymentDate
    The date the payment was received 
PaymentDateDue
    If this is a recurring payment, the date it is due 
PaymentAmount 
    The amount of the payment
PaymentGiftAid
    Yes or No if this donation is eligible for UK giftaid
PaymentComments 
    Any comments on the payment
PaymentTotalDue
    The total of all selected payments that have a due date and no received date
PaymentTotalReceived
    The total of all selected payments that have a received date

Cost Keys
---------

The same rules apply as for vaccinations and medical records but for accessing
costs. The fields are:

CostType
    The cost type
CostDate
    The date the cost was incurred
CostDatePaid
    If the “show cost paid field” option is on, the date the cost was actually paid for
CostAmount
    The value of the cost
CostDescription
    Any other information about the cost

Diet Keys
---------

The same rules apply as for vaccinations, but for accessing diet records. The fields are:

DietName
    The name of the diet 
DietDescription
    The diet description 
DietDateStarted
    The date the diet started 
DietComments
    Any comments on the diet

Log Keys
--------

The same rules apply as for vaccinations, but for accessing log records. The
fields are:

LogName
    The type of log 
LogDate
    The date of the log  
LogComments
    The log entry

Movement Keys
-------------

Movement keys are available for documents generated either from the Move->Adopt
screen, or from the animal details screen (in which case the animal's active
movement is assumed if it has one). Since movements tie together animals and
owners, all of the animal and owner keys are also available for movements. 

AdoptionID
    The adoption number 
AdoptionDate
    The date of the adoption 
ReservationDate
    The date the animal was reserved (if it's a reserve record) 
ReturnDate
    The date the animal was returned from this movement 
FosteredDate
    The date the animal was fostered (if applicable) 
TransferDate
    The date the animal was transferred (if applicable) 
TrialEndDate
    The date the trial adoption ends (if applicable)
MovementDate
    The date the animal was moved (whatever the type) 
MovementType
    The movement type (eg: Adoption, Foster, Transfer, etc) 
AdoptionNumber
    The adoption number 
AdoptionDonation
    The amount donated for the adoption 
AdoptionCreatedBy
    The user who created the movement record (AdoptionCreatedByName) 
AdoptionCreatedDate
    The date the movement was created 
AdoptionLastChangedBy
    The user who last changed the movement (AdoptionLastChangedByName) 
AdoptionLastChangedDate
    The date the movement was last changed 
InsuranceNumber
    If your shelter insures animals as they are adopted, the insurance number 

Person Keys
-----------

Person keys are available for documents generated from the owner and movement
screens, they are also available for documents generated from the payment tab. 

OwnerTitle 
    The person's title
OwnerInitials 
    The person's initials
OwnerForenames 
    (OwnerFirstNames for US users) 
OwnerSurname 
    (OwnerLastName for US users) 
OwnerComments 
    Any comments on the person
OwnerCreatedBy 
    (OwnerCreatedByName) 
OwnerCreatedDate 
    The date the person record was created
HomeTelephone 
    The person's home phone number
OwnerID 
    The ID of the person record
IDCheck
    “Yes” if the owner has been homechecked 
HomeCheckedByName
    The name of the person who homechecked this person
HomeCheckedByEmail
    The email address of the person who homechecked this person
HomeCheckedByHomeTelephone
    A phone number for the person who homechecked this person
HomeCheckedByMobileTelephone 
    (HomeCheckedByCellTelephone for US users)
OwnerLastChangedDate 
    The date this person record was last changed
OwnerLastChangedBy 
    (OwnerLastChangedByName) - The person who last changed this person record
OwnerAddress
    The person's address
OwnerName 
    The person's display name in the selected system display format
OwnerTown 
    (OwnerCity for US users) 
OwnerCounty 
    (OwnerState for US users) 
OwnerPostcode 
    (OwnerZipcode for US users) 
WorkTelephone 
    The person's work telephone number
MobileTelephone 
    (CellTelephone for US users)
EmailAddress 
    The person's email address
MembershipNumber 
    The person's membership number
MembershipExpiryDate 
    The date this person's membership with the shelter expires

Traploan Keys
-------------

The same rules apply as for vaccinations, but for accessing trap loans. Each
loan is indexed with a number for ascending (eg: TrapTypeName1), LastX for
descending (eg: TrapTypeNameLast1) and with the type name for the most recent
loan of that type for the person (eg: TrapLoanDateCat). The fields are:

TrapTypeName
    The type of trap being loaned
TrapLoanDate
    The date the trap was loaned
TrapDepositAmount
    The amount of deposit on the loan
TrapDepositReturnDate
    The date the deposit was returned
TrapNumber
    The trap number of the trap being loaned
TrapReturnDueDate
    The date the trap is due for return
TrapReturnDate
    The date the trap was returned
TrapComments
    Any comments on the traploana

Payment/Receipt/Invoice Keys
----------------------------

Payment keys are available for documents generated for a single payment from
the payment tab. Keys for the person making the payment are also present and if
the payment is linked to an animal, animal keys are also present. 

PaymentID 
    The payment record ID (used to generate receipt number)
PaymentType
    The payment type
PaymentMethod
    The payment method
PaymentDate
    The date the payment was received 
PaymentDateDue
    If this is a recurring payment, the date it is due 
PaymentAmount 
    The payment amount
ReceiptNum
    If you issue receipts for donations, the receipt number 
PaymentGiftAid
    Yes or No if this donation is eligible for UK giftaid
PaymentComments 
    Any comments for the payment
PaymentCreatedBy 
    (PaymentCreatedByName) 
PaymentCreatedDate 
    The date this payment record was created
PaymentLastChangedBy 
    (PaymentLastChangedByName) 
PaymentLastChangedDate  
    The date this payment record was last changed


