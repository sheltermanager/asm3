.. _wordkeys:

Appendix: Wordkeys
==================
 
The following wordkeys are available in different areas of the system when
generating documents from templates. Wordkeys should be placed in your
templates, wrapped in double angle-brackets. Eg: <<AnimalName>> 
 
Organisation Keys
-----------------
 
These keys are available in all types of documents.
 
Organisation / Organization
    The shelter's name
OrganisationAddress / OrganizationAddress
    The shelter's address
OrganisationTown / OrganizationCity
    The shelter's town / city
OrganisationCounty / OrganizationState
    The shelter's county / province / state
OrganisationPostcode / OrganizationZipcode
    The shelter's zip or postal code
OrganisationTelephone / OrganizationTelephone
    The shelter's telephone number
OrganisationEmail / OrganizationEmail
   The shelter's email address
Date
    Today's date
Database
    The name of the database (or account number if using sheltermanager.com)
Signature
    A signature:placeholder image for inserting a signature later (default
    150px wide)
Signature100 /Signature150 / Signature200 / Signature300
    Controls the max width of the signature while retaining aspect ratio
Username
    The current user generating the document
UserRealname
    The real name of the user generating the document
UserEmailAddress
    The email address of the user generating the document
UserSignature
    An image tag containing the electronic signature of the user generating the
    document (default 150px wide)
UserSignature100 / UserSignature150 / UserSignature200 / UserSignature300
    Controls the max width of the signature while retaining aspect ratio
UserSignatureSrc
    Just the src attribute value so the signature can be applied to your own
    image tag (eg: to override size)

Animal Keys
-----------

Animal keys are available for documents generated from the animal details and
movement screens.

DocumentImgLink
    An <img> tag containing a link to the animal's preferred document image.
    The image will be 200px high. You can also suffix a pixel height in
    increments of 100 upto 500px if you would like the image to be larger, eg:
    <<DocumentImgLink300>>, <<DocumentImgLink400>>, <<DocumentImgLink500>>
DocumentImgSrc
    Just the src attribute value for an image link to the preferred document image.
DocumentImgThumbLink
    An <img> tag containing a link to a thumbnail of the animal's preferred document image.
DocumentImgThumbSrc
    Just the src attribute value for a thumbnail link to the preferred document image.
DocumentQRLink
    An <img> tag containing a link to QR code that references a URL to the
    animal's record within ASM. Supports an optional pixel height suffix with
    the following values: 50, 100, 150, 200, eg: <<DocumentQRLink100>>
DocumentQRShare
    An <img> tag containing a link to a QR code that references a URL to the
    "share a link to this animal" public page for the animal. Supports an
    optional pixel height suffix with the following values: 50, 100, 150, 200,
    eg: <<DocumentQRShare>>, <<DocumentQRShare200>>
ShelterCode
    The animal's shelter code 
ShortShelterCode
    The shortened version of the shelter code 
Age
    The animal's age in readable form (eg: "6 weeks", “5 years”) 
AgeYM
    The animal's age in years and months (eg: “5 years and 6 months”) 
Description / AnimalComments
    The animal description box. 
DescriptionAttr
    The descriptionfield, but truncated to 100 characters with linebreaks
    suppressed and double quotes escaped to use in an HTML attribute
HealthProblems
    The health problems field 
LitterID / AcceptanceNumber
    The litter reference / acceptance number
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
InternalLocation / LocationName
    The animal's location within the shelter 
LocationDescription
    The description field from the animal's internal location
LocationUnit
    The location unit (eg, pen or cage number)
DisplayLocation
    Either the internal location if the animal is on shelter, a movement
    type/person for animals leaving the shelter or a deceased reason if the
    animal is no longer alive
UnitSponsor (only available in HTML website templates)
    Returns the name of the sponsor of the unit the animal is currently in
CoatType
    The animal's coat type 
AnimalFlags
    A list of the flags assigned to an animal, separated by commas.
AnimalFlagsEmblems
    Like AnimalFlags, but if you have assigned a custom emblem to a flag,
    outputs that emblem before the flag name
AnimalFlagsEmblemsX
    Like AnimalFlagsEmblems but excludes flags with no emblem
AnimalFlagsEmblemsOnly
    Like AnimalFlagsEmblems, but only outputs the emblem and not the flag name
AnimalFlagsEmblemsOnlyX
    Like AnimalFlagsEmblemsOnly but only excludes flags with no emblem
AnimalCreatedBy
    The user who created the animal record (AnimalCreatedByName for full user
    name) 
AnimalCreatedDate
    The date the animal record was created 
DateBroughtIn
    The date the animal was first brought to the shelter 
TimeBroughtIn
    The time of day the animal was first brought to the shelter
MonthBroughtIn
    The month the animal was first brought to the shelter 
DateOfBirth
    The animal's date of birth 
EstimatedDOB
    The word (estimated) if the estimated date of birth flag is ticked on the
    animal, or a blank string if not. 
AgeGroup
    The animal's age group (the defaults are Baby, Adult, Young Adult and
    Senior). These can be configured under the Settings->Options screen. 
DisplayAge
    If the EstimatedDOB flag is set, outputs the age group, if not, outputs a
    string representation of the animal's age. 
DisplayDOB
    If the EstimatedDOB flag is set, outputs the age group, if not, outputs the
    animal's date of birth. 
HoldUntilDate
    If the animal is held, the date it will be held until
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
BondedAnimal1Name
    The name of the first animal this animal is bonded to
BondedAnimal1Code
    The code of the first animal this animal is bonded to
BondedAnimal2Name
    The name of the second animal this animal is bonded to
BondedAnimal2Code
    The code of the second animal this animal is bonded to
BondedAnimal1Microchip
    The microchip number of the first animal this animal is bonded to
BondedAnimal2Microchip
    The microchip number of the second animal this animal is bonded to
BondedNames
    returns the name with bonds eg: AnimalName / BondedAnimal1Name /
    BondedAnimal2Name
BondedCodes
    returns the codes with bonds eg: ShelterCode / BondedAnimal1Code /
    BondedAnimal2Code
BondedMicrochips
    returns all microchip numbers eg: MicrochipNumber / BondedAnimal1Microchip
    / BondedAnimal2Microchip
Fee
    The animal's adoption fee if you are using per-animal adoption fees
LicenceNumber / LicenseNumber
    The latest licence number on file for this animal from the licence tab
Microchipped
    "Yes" if the animal has been microchipped 
MicrochipNumber
    The animal's microchip number 
MicrochipNumber2
    The animal's second microchip number if it has one
MicrochipDate
    The date the animal was microchipped 
MicrochipDate2
    The date the animal received a second microchip
MicrochipManufacturer
    The manufacturer of the microchip
MicrochipManufacturer2
    The manufacturer of the second microchip
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
HiddenComments / HiddenAnimalDetails
    The hidden comments box 
AnimalLastChangedBy
    The user who last changed the animal record (AnimalLastChangedByName for full user name) 
AnimalLastChangedDate
    The date record was last changed 
Markings
    The markings box 
Warning
    The warning box
NameOfOwnersVet
    The owner's vet box 
HasSpecialNeeds
    "Yes" if the animal has the box ticked for special needs on the vet tab 
Neutered
    "Yes" if the animal has been neutered/spayed (usually called "altered" or "fixed" in the US) 
NeuteredDate
    The date the animal was neutered 
PickupAddress
    The pickup address
PickupLocationName
    The pickup location set on the animal
AnimalJurisdiction
    The animal's jurisdiction
CoordinatorName
    The name of the adoption coordinator
CoordinatorHomePhone
    The home phone number of the adoption coordinator
CoordinatorWorkPhone
    The work phone number of the adoption coordinator
CoordinatorMobilePhone / CoordinatorCellPhone
    The mobile phone number of the adoption coordinator
CoordinatorEmail
    The email address of the adoption coordinator
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
BroughtInByJurisdiction
    The jurisdiction of the person who brought the animal in
BroughtInBy Additional Fields
    Additional fields on the brought in by person can be accessed via BroughtInByFIELDNAME
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
OriginalOwnerIDNumber
    The original owner's identification number (driving licence, passport, etc)
OriginalOwnerJurisdiction
    The jurisdiction of the original owner
OriginalOwner Additional Fields
    Additional fields on the original owner can be accessed via OriginalOwnerFIELDNAME
CurrentOwnerName
    The name of the animal's current owner (fosterer or adopter)
CurrentOwnerTitle
    The title of the current owner
CurrentOwnerFirstname / CurrentOwnerForenames 
    The first name(s) of the current owner
CurrentOwnerLastname / CurrentOwnerSurname
    The last name of the current owner
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
CurrentOwnerIDNumber
    The current owner's identification number (driving licence, passport, etc)
CurrentOwnerJurisdiction
    The jurisdiction of the current owner
CurrentOwner Additional Fields
    Additional fields on the current owner can be accessed via CurrentOwnerFIELDNAME
ReservedOwnerName
    The name of the person with an active reserve on the animal
ReservedOwnerTitle
    The title of the reserving person
ReservedOwnerFirstname / ReservedOwnerForenames
    The first name of the reserving person
ReservedOwnerLastname / ReservedOwnerSurname
    The last name of the reserving person
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
ReservedOwnerIDNumber
    The reserving owner's identification number (driving licence, passport, etc)
ReservedOwnerJurisdiction
    The jurisdiction of the reserving owner
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
CurrentVetEmail
    The email address of the animal's current vet
CurrentVetLicence / CurrentVetLicense
    The veterinary licence number
CurrentVet Additional Fields
    Additional fields on the current vet person can be accessed via CurrentVetFIELDNAME
NeuteringVetName
    The name of the vet that neutered/spayed the animal
NeuteringVetAddress
    The address of the vet that neutered/spayed the animal
NeuteringVetTown 
    (NeuteringVetCity for US users)
NeuteringVetCounty 
    (NeuteringVetState for US users)
NeuteringVetPostcode
    The postal code of the the vet that neutered/spayed the animal
NeuteringVetPhone
    A phone number for the vet that neutered/spayed the animal
NeuteringVetEmail
    The email address of the vet that neutered/spayed the animal
NeuteringVetLicence / NeuteringVetLicense
    The veterinary licence number
OwnersVetName
    The owner's vet
OwnersVetAddress
    The address of the owner's vet
OwnersVetTown 
    (OwnersVetCity for US users)
OwnersVetCounty 
    (OwnersVetState for US users)
OwnersVetPostcode
    The postal code of the owner's vet
OwnersVetPhone
    A phone number for the owner's vet
OwnersVetEmail
    The email address of the owner's vet
OwnersVetLicence / OwnersVetLicense
    The veterinary licence number
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
DisplayCatsIfGoodWith
    Outputs "Cats" if this animal is good with cats
DisplayDogsIfGoodWith
    Outputs "Dogs" if this animal is good with dogs
DisplayChildrenIfGoodWith
    Outputs "Children" if this animal is good with children
DisplayCatsIfBadWith
    Outputs "Cats" if this animal is bad with cats
DisplayDogsIfBadWith
    Outputs "Dogs" if this animal is bad with dogs
DisplayChildrenIfBadWith
    Outputs "Children" if this animal is bad with children
DisplayXIfCat / DisplayXIfDog / DisplayXIfRabbit / DisplayXIfMale / DisplayXIfFemale
    Outputs an X if this animal is a cat, dog, rabbit, male or female (used for form boxes)
DisplayXIfPedigree / DisplayXIfCrossbreed
    Outputs an X if this animal is a pure or crossbreed
DisplayXIfNeutered / DisplayXIfFixedMale / DisplayXIfFixedFemale
    Outputs an X if this animal is neutered/spayed
DisplayXIfNotNeutered / DisplayXIfEntireMale / DisplayXIfEntireFemale
    Outputs an X if this animal is not neutered/spayed
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
DisplayWeight
    The animal's weight, shown as either kg or lb/oz according to system display options
SpeciesName
    The animal's species 
MostRecentEntry / MostRecentEntryDate
    The date the animal most recently entered the shelter (if it was returned
    from an adoption or fostering for example) 
MostRecentMonthEntry
    The month the animal most recently entered the shelter 
MostRecentEntryCategory
    The entry category or return category depending on which happened most recently
TimeOnShelter
    A readable string showing the time the animal has spent on the shelter
    (from the last time it entered), eg: 4 weeks. 
DaysOnShelter
    The number of days the animal has spent on the shelter
NoTimesReturned
    The number of times the animal has been returned to the shelter 
AdoptionStatus
    A readable string of the animal's status, eg: Hold, Reserved, Quarantine, Adoptable
HasValidMedia
    "Yes" if the animal has a photo flagged for website generation 
WebMediaFilename
WebMediaNotes
    The notes to accompany the picture 
WebMediaNew
    "Yes" if the animal has not been published via the web publishing tool 
WebMediaUpdated
    "Yes" if the notes on the media for the animal have been edited since the
    animal was last published via the web publishing tool 
WebsiteVideoURL
    The web address of the default video link for this animal
WebsiteVideoNotes
    The notes accompanying the video link
AnimalAtRetailer
    "Yes" if the animal is currently located at a retailer
AnimalIsAdoptable
    "Yes" if the animal is available for adoption
DateAvailableForAdoption
    The date animal was first made available for adoption in its current stay in care.
AnimalOnFoster
    "Yes" if the animal is in a foster home
AnimalOnShelter
    "Yes" if the animal is on the shelter 
AnimalPermanentFoster
    "Yes" if the animal is a permanent foster
AnimalIsReserved
    "Yes" if the animal has been reserved
AnimalIsVaccinated
    "Yes" if the animal has at least one vaccination given and no vaccinations
    due before today that have not been given
OutcomeDate
    If the animal has left the care of the shelter, the date it left
OutcomeType
    How the animal left the shelter (can be a movement type or deceased reason
    if the animal died)

Qualifiers
----------

For situations where a record can be linked to many records, such as an animal with
many vaccination or medical records, or a person with many payments, then you
must qualify the tokens with a suffix to indicate which of those records you want
to access.

n (index)
^^^^^^^^^

Suffix a token with a number to get the nth record when counting from oldest to
newest. Eg::

    <<VaccinationName1>> - name of oldest vaccination
    <<TestGiven3>> - given date of 3rd test

Last(n)
^^^^^^^

Suffix a token with Last[number] to get the nth record counting from newest to
oldest. Eg::

    <<VaccinationGivenLast1>> - date given of newest vaccination
    <<MedicalDateStartedLast2>> - start date of second newest medical regimen

(name)
^^^^^^

Suffix a token with the name of a type to get the oldest given record with that
type. Eg::

    <<VaccinationGivenRabies>> - first date given of type "Rabies"
    <<DietDateStartedStandard>> - date first diet on file was started of type "Standard"

Recent(name)
^^^^^^^^^^^^

Suffix a token with Recent and the name of the type to get the most recently
given record of that type. Eg::

    <<VaccinationGivenRecentRabies>> - date of most recently given vaccination of type "Rabies"
    <<LogCommentsRecentWeight>> - log message of the most recently recorded log of type "Weight"

.. note:: When constructing names, the tokens will suppress any spaces, so "Rabies 3 Yr" would become "Rabies3Yr"

Due(name)
^^^^^^^^^

Suffix a token with Due and the name of the type to get the newest ungiven record
of that type. Eg::

    <<VaccinationRequiredDueRabies>> - required date for the newest ungiven vaccination of type "Rabies"
    <<PaymentAmountDueRegular>> - amount for the newest unreceived payment of type "Regular"

Note that the "Due" keyword will not work for medical, vaccination or tests if
you have turned off the option to include incomplete medical items from
documents under :menuselection:`Settings --> Options --> Documents --> Include
incomplete medical records when generating document templates`

Vaccination Keys
----------------

You must use a qualifier suffix to access these records.

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
VaccinationRabiesTag
    The rabies tag number accompanying this vaccine
VaccinationCost
    The cost of this vaccine
VaccinationComments
    The vaccination comments
VaccinationDescription
    The vaccination description from the lookup data.
VaccinationAdministeringVetName
    The name of the vet who administered the vaccination
VaccinationAdministeringVetLicence / VaccinationAdministeringVetLicense
    The licence number of the vet who administered the vaccination
VaccinationAdministeringVetAddress
    The address of the vet who administered the vaccination
VaccinationAdministeringVetTown / VaccinationAdministeringVetCity
    The town/city of the vet who administered the vaccination
VaccinationAdministeringVetCounty / VaccinationAdministeringVetState
    The county/state of the vet who administered the vaccination
VaccinationAdministeringVetPostcode / VaccinationAdministeringVetZipcode
    The postal/zip code of the vet who administered the vaccination
VaccinationAdministeringVetEmail
    The email address of the vet who administered the vaccination

Test Keys
----------

You must use a qualifier suffix to access these records.

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
TestAdministeringVetName
    The name of the vet who administered the test
TestAdministeringVetLicence / TestAdministeringVetLicense
    The licence number of the vet who administered the test
TestAdministeringVetAddress
    The address of the vet who administered the test
TestAdministeringVetTown / TestAdministeringVetCity
    The town/city of the vet who administered the test
TestAdministeringVetCounty / TestAdministeringVetState
    The county/state of the vet who administered the test
TestAdministeringVetPostcode / TestAdministeringVetZipcode
    The postal/zip code of the vet who administered the test
TestAdministeringVetEmail
    The email address of the vet who administered the test


Medical Keys
------------

You must use a qualifier suffix to access these records.

.. note:: For medical regimens, the Recent keyword only looks for those with a status of Completed, while the Due keyword only looks for those with a status of Active.

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
MedicalLastTreatmentComments
    The comments attached to the last treatment given
MedicalCost
    The cost of this medical regimen
MedicalComments
    The medical comments 


Payment Keys
------------

If you are creating a document from the animal or person records, then you must
use a qualifier suffix to access these records. The Recent keyword looks for
payments that have been received and Due for non-received payments.

However, if you create an invoice/receipt document from the payment tab of a
person or animal record (or the payment book), you can select multiple payments
before creating the document and access the information by suffixing a number
to the end of the keys listed below (eg: PaymentType1, PaymentComments2)

The fields are:

ReceiptNum
    If you issue receipts for donations, the receipt number 
CheckNum / ChequeNum
    The cheque number for the payment
PaymentType
    The payment type
PaymentMethod
    The payment method
PaymentDate
    The date the payment was received 
PaymentDateDue
    If this is a recurring payment, the date it is due 
PaymentGross
    The total gross amount of the payment, including any fees and taxes
PaymentFee
    Any transaction fees incurred on the payment
PaymentAmount / PaymentNet
    The net amount of the payment, excludes any fees and taxes
PaymentQuantity
    (if quantities are enabled) The number of items the payment covers
PaymentUnitPrice
    (if quantities are enabled) The price per item
PaymentGiftAid
    Yes or No if this payment is eligible for UK giftaid
PaymentTax / PaymentVAT
    Yes or No if this payment was taxable for sales tax/VAT/GST
PaymentTaxRate / PaymentVATRate
    The taxable rate applied
PaymentTaxAmount / PaymentVATAmount
    The taxable amount charged
PaymentComments 
    Any comments on the payment

The following fields are only available to payments generated via
invoice/receipt document: 

PaymentAnimalName
    The name of the animal the payment is linked to
PaymentAnimalShelterCode
    The full shelter code of the animal the payment is linked to
PaymentAnimalShortCode
    The short shelter code of the animal the payment is linked to
PaymentPersonName
    The name of the person the payment is linked to
PaymentPersonAddress
   The address of the person the payment is linked to
PaymentPersonCity / PaymentPersonTown
   The city of the person the payment is linked to
PaymentPersonState / PaymentPersonCounty
   The state of the person the payment is linked to
PaymentPersonZipcode / PaymentPersonPostcode
   The zipcode of the person the payment is linked to
PaymentTotalDue
    The gross total of all selected payments that have a due date and no received date
PaymentTotalNet / PaymentTotalReceived
    The net total of all selected payments that have a received date
PaymentTotalTaxRate / PaymentTotalVATRate
    The highest rate of tax applied by any of the selected payments
PaymentTotalTax / PaymentTotalVAT
    The total of all sales tax/VAT/GST on the selected payments
PaymentTotal / PaymentTotalGross
    The gross total of all received payments

Transport Keys
--------------

If you are creating a document from the animal or person records, then the same
rules apply as for vaccinations and medical records when accessing transports.
The Recent keyword looks for transports with the most recent drop off date/time
and the Due keyword uses the pickup date/time.

However, if you create a document from the transport tab of an
animal record (or the transport book), you can select multiple transports
before creating the document and access the information by suffixing a number
to the end of the keys listed below (eg: TransportType1, TransportComments2)

The fields are:

TransportID
   A unique ID number representing the transport
TransportType
   The type of transport
TransportDriveName
   The transport driver if known
TransportPickupDateTime / TransportPickupDate / TransportPickupTime
   The date and time of the pickup
TransportPickupName
   The person the transport is picking up from if known
TransportPickupAddress
   The pickup address
TransportPickupCity / TransportPickupTown
   The pickup city / town
TransportState / TransportCounty
   The pickup state / county
TransportPickupZipcode / TransportPickupPostcode
   The pickup zipcode/postcode
TransportPickupCountry
   The pickup country
TransportPickupEmail
   The email address of the pickup contact
TransportPickupHomePhone
   The home phone number of the pickup contact
TransportPickupWorkPhone
   The work phone number of the pickup contact
TransportPickupCellPhone / TransportPickupMobilePhone
   The mobile phone number of the pickup contact
TransportDropoffName
   The person the transport is taking the animal to if known
TransportDropoffDateTime / TransportDropoffDate / TransportDropoffTime
   The date and time of the dropoff
TransportDropoffAddress
   The dropoff address
TransportDropoffCity / TransportDropoffTown
   The dropoff city / town
TransportDropoffState / TransportDropoffCounty
   The dropoff state / county
TransportDropoffZipcode / TransportDropoffPostcode
   The dropoff zipcode / postcode
TransportDropoffCountry
   The dropoff country
TransportDropoffEmail
   The email address of the dropoff contact
TransportDropoffHomePhone
   The home phone number of the dropoff contact
TransportDropoffWorkPhone
   The work phone number of the dropoff contact
TransportDropoffCellPhone / TransportDropoffMobilePhone
   The mobile phone number of the dropoff contact
TransportMiles
   The distance of the transport in miles (if known)
TransportCost
   The cost of the transport
TransportComments
   Any comments present for the transport

The following fields are only available to transports generated via
the transport tab or book: 

TransportAnimalName
   The name of the animal being transported
TransportShelterCode / TransportShortCode
   The code of the animal being transported
TransportSpecies
   The species of animal being transported
TransportBreed
   The breed of animal being transported
TransportSex
   The sex of the animal being transported

Cost Keys
---------

You must use a qualifier suffix to access these records.

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

In addition there are a number of total fields for costs:

TotalVaccinationCosts
    The total of all vaccination costs for the animal
TotalTransportCosts
    The total of all transport costs for the animal
TotalTestCosts
    The total of all test costs for the animal
TotalMedicalCosts
    The total of all medical costs for the animal
TotalLineCosts
    The total of all cost lines from the cost tab for the animal
DailyBoardingCost
    The animal's daily boarding cost
CurrentBoardingCost
    The daily boarding cost multiplied by days on shelter for the animal
TotalCosts
    The total of CurrentBoardingCost and all the Total Cost fields.

Diet Keys
---------

You must use a qualifier suffix to access these records.

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

You must use a qualifier suffix to access these records.

LogName
    The type of log 
LogDate
    The date of the log  
LogTime
    The time of the log  
LogComments
    The log entry
LogCreatedBy
    The person who created the log entry

Movement Keys
-------------

Movement keys are available for documents generated either from the Move->Adopt
screen, or from the animal details screen (in which case the animal's active
movement is assumed if it has one) or movement tabs. Since movements tie together 
animals and owners, all of the animal and owner keys are also available for 
movements. 

MovementDate
    The date the animal was moved (whatever the type) 
MovementType
    The movement type (eg: Adoption, Foster, Transfer, etc) 
MovementNumber
    The movement number 
MovementComments
    The comments from the movement
InsuranceNumber
    If your shelter insures animals as they are adopted, the insurance number 
ReservationDate
    The date the animal was reserved (if it's a reserve record)
ReservationCancelledDate
    The date the reservation was cancelled
ReservationStatus
    The status of the selected reservation
ReturnDate
    The date the animal was returned from this movement 
ReturnNotes
    The reason for return notes
ReturnReason
    The return category
ReturnedByName
    The name of the person who returned the animal
ReturnedByFirstname / ReturnedByForenames 
    The first name(s) of the person who returned the animal
ReturnedByLastname / ReturnedBySurname
    The last name of the person who returned the animal
ReturnedByAddress 
    The returner's address
ReturnedByTown 
    (ReturnedByCity for US users) 
ReturnedByCounty 
    (ReturnedByState for US users) 
ReturnedByPostcode 
    (ReturnedByZipcode for US users) 
ReturnedByHomePhone 
    Returner's home phone number
ReturnedByWorkPhone 
    Returner's work phone number
ReturnedByMobilePhone 
    Returner's cell/mobile phone number
ReturnedByEmail 
    Returner's email address
AdoptionDate
    The date of the adoption (if this is an adoption, alias for MovementDate)
FosteredDate
    The date the animal was fostered (if this is a foster, alias for MovementDate)) 
TransferDate
    The date the animal was transferred (if this is a transfer, alias for MovementDate) 
TrialEndDate
    The date the trial adoption ends
MovementIsTrial
    Yes if this movement is a trial adoption
MovementIsPermanentFoster
    Yes if this movement is a permanent foster
MovementPaymentTotal
    The total of any payments for this movement
MovementCreatedBy
    The user who created the movement record (AdoptionCreatedByName) 
MovementCreatedDate
    The date the movement was created 
MovementLastChangedBy
    The user who last changed the movement (AdoptionLastChangedByName) 
MovementLastChangedDate
    The date the movement was last changed 

Person Keys
-----------

Person keys are available for documents generated from the person and movement
screens, they are also available for documents generated from the payment 
and licence tabs as well as lost animal, found animal and waiting list.
For documents generated from the animal screen, the person will be chosen in
the following order: Latest movement on file, latest reservation on file, 
current owner (if the animal is non-shelter)
Log keys are available for people, but prefixed with PersonLog instead of just Log.

Title / OwnerTitle / Title2 /
    The person's title
Initials / OwnerInitials / Initials2
    The person's initials
Forenames / OwnerForenames / Forenames2
    (Firstnames / OwnerFirstNames / Firstnames2 for US users) 
Surname / OwnerSurname / Surname2
    (Lastname / OwnerLastName / Lastname2 for US users) 
OwnerFlags
    A list of the flags assigned to a person, separated by commas.
OwnerComments 
    Any comments on the person
OwnerWarning
    The warning box on the person
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
HomeCheckedDate
    The date this person was homechecked
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
Address / OwnerAddress
    The person's address
Name / OwnerName 
    The person's display name in the selected system display format
Town / OwnerTown 
    (City / OwnerCity for US users) 
County / OwnerCounty 
    (State / OwnerState for US users) 
Postcode / OwnerPostcode 
    (Zipcode / OwnerZipcode for US users) 
Country / OwnerCountry
    The country this person lives in
OwnerLookingFor
    A summary of the "Looking for" slider on the person's record
OwnerJurisdiction
    The person's jurisdiction
OwnerSite
    The site this person is linked to
WorkTelephone / WorkTelephone2
    The person's work telephone number
MobileTelephone / MobileTelephone2
    (CellTelephone / CellTelephone2 for US users)
EmailAddress / EmailAddress2
    The person's email address
OwnerDateOfBirth / OwnerDateOfBirth2
    The person's date of birth
IDNumber / IDNumber2
    The person's identification number (driving licence, passport, national ID card, etc)
MembershipNumber 
    The person's membership number
MembershipExpiryDate 
    The date this person's membership with the shelter expires
DocumentImgLink
    An <img> tag containing a link to the person's preferred document image.
    The image will be 200px high. You can also suffix a pixel height in
    increments of 100 upto 500px if you would like the image to be larger, eg:
    <<DocumentImgLink300>>, <<DocumentImgLink400>>, <<DocumentImgLink500>>
DocumentImgSrc
    Just the src attribute value for an image link to the preferred document image.

Citation Keys
-------------

You must use a qualifier suffix to access these records.

.. note:: The Recent keyword returns citations where the fine is paid where Due returns unpaid.

CitationName
    The type of citation being issued
CitationDate
    The date of the citation
CitationComments
    Any comments on the citation
FineAmount
    The fine amount
FineDueDate
    The date the fine is due to be paid
FinePaidDate
    The date the fine was paid

Equipment Loan Keys
-------------------

You must use a qualifier suffix to access these records.

.. note:: The Recent keyword returns returned trap loan records where Due is unreturned.

EquipmentTypeName
    The type of equipment being loaned
EquipmentLoanDate
    The date the equipment was loaned
EquipmentDepositAmount
    The amount of deposit on the loan
EquipmentDepositReturnDate
    The date the deposit was returned
EquipmentNumber
    The equipment number of the trap being loaned
EquipmentReturnDueDate
    The date the equipment is due for return
EquipmentReturnDate
    The date the equipment was returned
EquipmentComments
    Any comments on the equipment loan

Licence Keys
------------

Licence keys are only available for documents generated for a single licence
under the licence tab or licencing book. Keys for the person purchasing the
licence are also present and if the licence is linked to an animal, animal
keys are also present.

.. note:: You can use "Licence" or "License" when accessing these keys - either will work.

LicenceTypeName
    The type of licence purchased
LicenceNumber
    The unique number of the licence
LicenceFee
    The fee for the licence
LicenceIssued
    The date the licence was issued
LicenceExpires
    The date the licence expires
LicenceComments
    Any comments from the licence record

Voucher Keys
------------

Voucher keys are only available for documents generated for a single voucher
under the voucher tab or the voucher book. Keys for the person the voucher
has been issued to are also present and if the licence is linked to an animal,
animal keys are also present.

VoucherTypeName
   The type of voucher
VoucherCode
   The voucher's unique code
VoucherValue
   The amount the voucher can be redeemed for if appropriate
VoucherIssued
   The date the voucher was issued
VoucherExpires
   The date the voucher expires
VoucherRedeemed
   The date the voucher was redeemed/used
VoucherComments
   Any comments about the voucher

Incident Keys
-------------

Incident keys are only available for documents generated with the document button
on a single incident. Log keys are available for incidents, but prefixed with
IncidentLog instead of just Log.

IncidentNumber
    The unique incident number
IncidentDate
    The date of the incident
IncidentTime
    The time of the incident
IncidentTypeName
    The type of incident
CallDate
    The date of the call
CallTime
    The time of the call
CallerName
    The name of the caller
CallerAddress
    The address of the caller
CallerTown / CallerCity
    The city of the caller
CallerCounty / CallerState
    The state of the caller
CallerPostcode / CallerZipcode
    The zipcode of the caller
CallerHomeTelephone
    The caller's home number
CallerWorkTelephone
    The caller's work number
CallerMobileTelephone / CallerCellTelephone
    The caller's mobile number
CallNotes
    Any notes about the call. 
CallTaker
    The username of the staff member that took the call
DispatchDate
    The date an ACO was dispatched
DispatchTime    
    The dispatch time
DispatchAddress
    The address an ACO was dispatched to
DispatchTown / DispatchCity
    The city an ACO was dispatched to
DispatchCounty / DispatchState
    The state an ACO was dispatched to
DispatchPostcode / DispatchZipcode
    The zipcode an ACO was dispatched to
PickupLocationName
    The pickup location set on the incident
IncidentJurisdiction
    The incident jurisdiction
RespondedDate
    The date the incident was attended by an ACO
RespondedTime
    The time the incident was attended by an ACO
FollowupDate
    The date the incident is due for followup
FollowupTime
    The time the incident is due for followup
FollowupDate2
    The date the incident is due for followup
FollowupTime2
    The time the incident is due for followup
FollowupDate3
    The date the incident is due for followup
FollowupTime3
    The time the incident is due for followup
CompletedDate
    The date the incident was completed
CompletedTypeName
    The completion code/name
AnimalDescription
    A description of any animals involved in the incident
SpeciesName
    The species of animal(s) involved in the incident
Sex
    The sex of the animal(s) involved in the incident
AgeGroup
    The age group of the animal(s) involved in the incident
SuspectName
    The name of the main suspect
SuspectAddress
    The suspect's address
SuspectTown / SuspectCity
    The suspect's city
SuspectCounty / SuspectState
    The suspect's state
SuspectPostcode / SuspectZipcode
    The suspect's postal/zip code
SuspectHomeTelephone
    The suspect's home number
SuspectWorkTelephone
    The suspect's work number
SuspectMobileTelephone / SuspectCellTelephone
    The suspect's mobile number
Suspect1Name
    The name of the first suspect
Suspect2Name
    The name of the second suspect
Suspect3Name
    The name of the third suspect
VictimName
    The name of the victim
VictimAddress
    The address of the victim
VictimTown / VictimCity
    The victim's city
VictimCounty / VictimState
    The victim's state
VictimPostcode / VictimZipcode
    The victim's postal/zip code
VictimHomeTelephone
    The victim's home number
VictimWorkTelephone
    The victim's work number
VictimMobileTelephone / VictimCellTelephone
    The victim's mobile number
DocumentImgLink
    An <img> tag containing a link to the incident's preferred document image.
    The image will be 200px high. You can also suffix a pixel height in
    increments of 100 upto 500px if you would like the image to be larger, eg:
    <<DocumentImgLink300>>, <<DocumentImgLink400>>, <<DocumentImgLink500>>
DocumentImgSrc
    Just the src attribute value for an image link to the preferred document image.

Incident Animal Keys
--------------------

Incident animal keys allow accessing of the animals linked to an incident. Each
animal is indexed with a number for ascending (eg: AnimalName1) or LastX for
descending (AnimalNameLast1).

AnimalName
    The animal's name
ShelterCode
    The animal's shelter code
ShortCode
    The animal's short shelter code
MicrochipNumber
    The animal's microchip number
AgeGroup
    The animal's age group
AnimalTypeName
    The type of animal
SpeciesName
    The species of animal
Sex
    The sex of the animal
Size
    The size of the animal
BaseColorName / BaseColourName
    The color of the animal
CoatType
    The coat type of the animal
DateBroughtIn
    The date the animal entered the shelter
DeceasedDate
    The date the animal died

Lost Animal Keys
----------------

Lost animal keys are only available for documents generated with the document
button on a single lost animal record. In addition to the tokens listed below,
the person keys listed above are also valid for the primary contact along with
log keys.

DateReported
    The date the report was received
DateLost
    The date the animal was first missing
DateFound
    The date the animal was found
AgeGroup
    An age group for the animal
Features
    Any information about the animal's appearance
AreaLost
    The area in which the animal was lost (street, etc)
AreaPostcode
    The postcode in which the animal was lost
Comments
    Any comments about the lost record
SpeciesName
    The species of animal
BreedName
    The breed of animal
BaseColorName / BaseColourName
    The color of the animal
Sex
    The sex of the animal
DocumentImgLink
    A photo of the animal if one exists. 200/300/400/500 can also be suffixed
    as with animal images above to control the size of the output.

Found Animal Keys
-----------------

Found animal keys are only available for documents generated with the document
button on a single found animal record. In addition to the tokens listed below,
the person keys listed above are also valid for the primary contact along with
log keys.

DateReported
    The date the report was received
DateFound
    The date the animal was found
DateReturned
    The date the animal was returned to its owner
AgeGroup
    An age group for the animal
Features
    Any information about the animal's appearance
AreaFound
    The area in which the animal was found (street, etc)
AreaPostcode
    The postcode in which the animal was found
Comments
    Any comments about the found record
SpeciesName
    The species of animal
BreedName
    The breed of animal
BaseColorName / BaseColourName
    The color of the animal
Sex
    The sex of the animal
DocumentImgLink
    A photo of the animal if one exists. 200/300/400/500 can also be suffixed
    as with animal images above to control the size of the output.

Waiting List Keys
-----------------

Waiting list keys are only available for documents generated with the document
button on a single waiting list record. In addition to the tokens listed below,
the person keys listed above are also valid for the primary contact along with
log keys.

DatePutOnList
    The date the animal was put on the waiting list
DateRemovedFromList
    The date the animal was removed from the waiting list
DateOfLastOwnerContact
    The last time we heard from the owner
Size   
    The size of the animal
SpeciesName
    The species of animal
Description
    A description of the animal
ReasonForWantingToPart
    The reason the owner is relinquishing the animal
ReasonForRemoval
    The reason this waiting list entry was removed
CanAffordDonation
    Yes/No - whether the person can afford to make a donation
Urgency
    An urgency rating for this waiting list item
Comments
    Any comments on this waiting list entry
DocumentImgLink
    A photo of the animal if one exists. 200/300/400/500 can also be suffixed
    as with animal images above to control the size of the output.

Clinic Keys
-----------

Clinic keys are only available for documents generated with the document button
on a single clinic appointment record (either via the Clinic tab of an animal
or person, or the "Consulting Room" or "Waiting Room" screens). In addition to
these keys, the person and animal keys listed above are valid for clinic
appointments.

AppointmentFor
    The name of the vet the appointment is with
AppointmentDate
    The date of the appointment
AppointmentTime
    The time of the appointment
Status
    The appointment's current status
ArrivedDate
    The date the person arrived for the appointment
ArrivedTime
    The time the person arrived for the appointment
WithVetDate
    The date the person was with the vet for the appointment
WithVetTime
    The time the person was with the vet for the appointment
CompletedDate
    The date the appointment was complete
CompletedTime
    The time the appointment was complete
ReasonForAppointment
    The reason the appointment was made
AppointmentComments
    Any comments on the appointment
InvoiceAmount
    The total of all invoice items for the appointment
InvoiceVatAmount / InvoiceTaxAmount
    The total VAT/Tax on the invoice
InvoiceVatRate / InvoiceTaxRate
    The tax rate applied to the invoice
InvoiceTotal
    The total of invoice amount and VAT/Tax

Table Keys
----------

These are special keys that insert a table into your document that contains the
complete data from a tab. 

These keys do not allow the flexibility of formatting that the other keys
offer, but they do offer a simple way of putting bulk data into a document without 
having to create a table containing many "just in case" placeholder keys. 

They will also dynamically expand the document according to how many records
there are.  Records are output in ascending order of date.

AnimalVaccinations
   Inserts a table containing all the animal's vaccinations into the document
AnimalTests
   Inserts a table containing all of the animal's tests into the document
AnimalMedicals
   Inserts a table containing all of the animal's medical regimens
ActiveAnimalMedicals
   Inserts a table containing all of the animal's medical regimens where the status is active
AnimalLogs
   Inserts a table containing all of the animal's log entries
AnimalLogsTYPE
   Inserts a table containing all of the animal's log entries of TYPE
IncidentLogs
   Inserts a table containing all of the incident's log entries
LitterMates
   Inserts a table containing a list of the animal's littermates
ActiveLitterMates
   Inserts a table containing a list of the animal's littermates (only those still in care)
MovementPayments
   Inserts a table containing all of the payments for the active movement for
   the person, animal or movement the document is being generated for.

