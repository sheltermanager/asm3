
import asm3.cachedisk
import asm3.configuration
import asm3.financial
import asm3.utils
from asm3.i18n import _
from asm3.sitedefs import URL_MICROCHIP_PREFIXES
from asm3.typehints import datetime, Database, Dict, List, LocationFilter, Results, Tuple

import re

# Look up tables map
# tablename : ( tablelabel, namefield, namelabel, descfield, hasspecies, haspfspecies, haspfbreed, hasapcolour, hasdefaultcost, hasunits, hassite, canadd, candelete, canretire,(foreignkeys) )
# tablename : ( tablelabel, namefield, namelabel, descfield, modifiers,(foreignkeys) )
# modifiers: 
#   add - add new records
#   del - can delete
#   ret - can retire a value
#   species - has a SpeciesID column (breed)
#   pubspec - has a PetFinderSpecies column (species)
#   pubbreed - has a PetFinderBreed column (breed)
#   pubcol - has an AdoptAPetColour column (basecolour)
#   sched - has a RescheduleDays column (testtype, vaccinationtype)
#   acc - has an AccountID column (costtype, donationtype)
#   cost - has a DefaultCost column (citationtype, costtype, donationtype, licencetype)
#   units - has Units column (internallocation)
#   site - has SiteID column (internallocation)
#   vat - has an IsVAT column (donationtype)
LOOKUP_TABLES = {
    "lksaccounttype":   (_("Account Types"), "AccountType", _("Type"), "", "", ("accounts.AccountType",)),
    "lkanimalflags":    (_("Animal Flags"), "Flag", _("Flag"), "", "add del ret", ""),
    "animaltype":       (_("Animal Types"), "AnimalType", _("Type"), "AnimalDescription", "add del ret", ("animal.AnimalTypeID",)),
    "basecolour":       (_("Colors"), "BaseColour", _("Color"), "BaseColourDescription", "add del ret pubcol", ("animal.BaseColourID", "animallost.BaseColourID", "animalfound.BaseColourID")),
    "lkboardingtype":   (_("Boarding Types"), "BoardingName", _("Boarding Type"), "BoardingDescription", "add del ret cost", ("animalboarding.BoardingTypeID",)),
    "lkclinictype":     (_("Clinic Appointment Types"), "ClinicTypeName", _("Appointment Type"), "ClinicTypeDescription", "add del ret", ("clinicappointment.ClinicTypeID",)),
    "breed":            (_("Breeds"), "BreedName", _("Breed"), "BreedDescription", "add del ret species pubbreed", ("animal.BreedID", "animal.Breed2ID", "animallost.BreedID", "animalfound.BreedID")),
    "lkcoattype":       (_("Coat Types"), "CoatType", _("Coat Type"), "", "add del", ("animal.CoatType",)),
    "citationtype":     (_("Citation Types"), "CitationName", _("Citation Type"), "CitationDescription", "add del ret cost", ("ownercitation.CitationTypeID",)),
    "lksclinicstatus":  (_("Clinic Statuses"), "Status", _("Status"), "", "", ("clinicappointment.Status",)),
    "costtype":         (_("Cost Types"), "CostTypeName", _("Cost Type"), "CostTypeDescription", "add del ret cost acc", ("animalcost.CostTypeID",)),
    "deathreason":      (_("Death Reasons"), "ReasonName", _("Reason"), "ReasonDescription", "add del ret", ("animal.PTSReasonID",)),
    "diet":             (_("Diets"), "DietName", _("Diet"), "DietDescription", "add del ret", ("animaldiet.DietID",)),
    "donationpayment":  (_("Payment Methods"), "PaymentName", _("Type"), "PaymentDescription", "add del ret", ("ownerdonation.DonationPaymentID",)),
    "donationtype":     (_("Payment Types"), "DonationName", _("Type"), "DonationDescription", "add del ret cost vat acc", ("ownerdonation.DonationTypeID", "accounts.DonationTypeID")),
    "entryreason":      (_("Entry Reasons"), "ReasonName", _("Reason"), "ReasonDescription", "add del ret", ("animal.EntryReasonID", "adoption.ReturnedReasonID") ),
    "lksentrytype":     (_("Entry Types"), "EntryTypeName", _("Type"), "", "", ("animal.EntryTypeID", "animalentry.EntryTypeID") ),
    "incidentcompleted":(_("Incident Completed Types"), "CompletedName", _("Completed Type"), "CompletedDescription", "add del ret", ("animalcontrol.IncidentCompletedID",)),
    "incidenttype":     (_("Incident Types"), "IncidentName", _("Type"), "IncidentDescription", "add del ret", ("animalcontrol.IncidentTypeID",)),
    "internallocation": (_("Internal Locations"), "LocationName", _("Location"), "LocationDescription", "add del ret units site", ("animal.ShelterLocation",)),
    "jurisdiction":     (_("Jurisdictions"), "JurisdictionName", _("Jurisdiction"), "JurisdictionDescription", "add del ret", ("animal.JurisdictionID", "animalcontrol.JurisdictionID","owner.JurisdictionID")),
    "licencetype":      (_("License Types"), "LicenceTypeName", _("Type"), "LicenceTypeDescription", "add del ret cost sched", ("ownerlicence.LicenceTypeID",)),
    "logtype":          (_("Log Types"), "LogTypeName", _("Type"), "LogTypeDescription", "add del ret", ("log.LogTypeID",)),
    "lkmediaflags":     (_("Media Flags"), "Flag", _("Flag"), "", "add del ret", ""),
    "lksmovementtype":  (_("Movement Types"), "MovementType", _("Type"), "", "", ("adoption.MovementType", "animal.ActiveMovementType",)),
    "lksoutcome":       (_("Outcomes"), "Outcome", _("Outcome"), "", "", ""),
    "lkownerflags":     (_("Person Flags"), "Flag", _("Flag"), "", "add del ret", ""),
    "lkproducttype":    (_("Product Types"), "ProductTypeName", _("Name"), _("Description"), "add del ret", ""),
    "lksrotatype":      (_("Rota Types"), "RotaType", _("Type"), "", "", ("ownerrota.RotaTypeID",)),
    "lksex":            (_("Sexes"), "Sex", _("Sex"), "", "", ("animal.Sex", "animallost.Sex", "animalfound.Sex")),
    "lksize":           (_("Sizes"), "Size", _("Size"), "", "", ("animal.Size",)),
    "lksyesno":         (_("Yes/No"), "Name", _("Yes/No"), "", "", ("animal.Neutered",)),
    "lksynun":          (_("Yes/No/Unknown"), "Name", _("Yes/No/Unknown"), "", "", ("animal.IsHouseTrained",)),
    "lksynunk":         (_("Good with kids"), "Name", _("Good with kids"), "", "", ("animal.IsGoodWithChildren",)),
    "lksposneg":        (_("Positive/Negative"), "Name", _("Positive/Negative"), "", "", ("animal.CombiTestResult",)),
    "pickuplocation":   (_("Pickup Locations"), "LocationName", _("Location"), "LocationDescription", "add del ret", ("animal.PickupLocationID", "animalcontrol.PickupLocationID")),
    "reservationstatus": (_("Reservation Statuses"), "StatusName", _("Status"), "StatusDescription", "add del ret", ("adoption.ReservationStatusID",)),
    "site":             (_("Sites"), "SiteName", _("Site"), "", "add del", ("users.SiteID","internallocation.SiteID")),
    "species":          (_("Species"), "SpeciesName", _("Species"), "SpeciesDescription", "add del ret pubspec", ("animal.SpeciesID", "onlineformfield.SpeciesID", "animallost.AnimalTypeID", "animalfound.AnimalTypeID")),
    "stocklocation":    (_("Stock Locations"), "LocationName", _("Location"), "LocationDescription", "add del ret", ("stocklevel.StockLocationID",)),
    "stockusagetype":   (_("Stock Usage Type"), "UsageTypeName", _("Usage Type"), "UsageTypeDescription", "add del ret", ("stockusage.StockUsageTypeID",)),
    "lkurgency":        (_("Urgencies"), "Urgency", _("Urgency"), "", "", ("animalwaitinglist.Urgency",)),
    "lktaxrate":        (_("Tax Rate"), "TaxRateName", _("Name"), _("Description"), "add del ret", ("lktaxrate.TaxRate",)),
    "testtype":         (_("Test Types"), "TestName", _("Type"), "TestDescription", "add del ret cost sched", ("animaltest.TestTypeID",)),
    "testresult":       (_("Test Results"), "ResultName", _("Result"), "ResultDescription", "add del ret", ("animaltest.TestResultID",)),
    "lkstransportstatus": (_("Transport Statuses"), "Name", _("Status"), "", "", ("animaltransport.Status",)),
    "transporttype":    (_("Transport Types"), "TransportTypeName", _("Type"), "TransportTypeDescription", "add del ret", ("animaltransport.TransportTypeID",)),
    "traptype":         (_("Equipment Loan Types"), "TrapTypeName", _("Type"), "TrapTypeDescription", "add del ret cost", ("ownertraploan.TrapTypeID",)),
    "vaccinationtype":  (_("Vaccination Types"), "VaccinationType", _("Type"), "VaccinationDescription", "add del ret cost sched", ("animalvaccination.VaccinationID",)),
    "voucher":          (_("Voucher Types"), "VoucherName", _("Type"), "VoucherDescription", "add del ret cost", ("ownervoucher.VoucherID",)),
    "lkwaitinglistremoval": (_("Waiting List Removal"), "RemovalName", _("Type"), "", "add del", ("animalwaitinglist.WaitingListRemovalID",)),
    "lkworktype":       (_("Work Types"), "WorkType", _("Type"), "", "add del ret", ("ownerrota.WorkTypeID",))
}
LOOKUP_TABLELABEL = 0
LOOKUP_NAMEFIELD = 1
LOOKUP_NAMELABEL = 2
LOOKUP_DESCFIELD = 3
LOOKUP_MODIFIERS = 4
LOOKUP_FOREIGNKEYS = 5

# Currency codes used by payment processors when accepting payments
CURRENCIES = [
    { "CODE": "USD", "DISPLAY": "USD - United States Dollar"},
    { "CODE": "AUD", "DISPLAY": "AUD - Australian Dollar"},
    { "CODE": "BRL", "DISPLAY": "BRL - Brazilian Real"},
    { "CODE": "CAD", "DISPLAY": "CAD - Canadian Dollar"},
    { "CODE": "CHF", "DISPLAY": "CHF - Swiss Franc"},
    { "CODE": "CZK", "DISPLAY": "CZK - Czech Koruna"},
    { "CODE": "DKK", "DISPLAY": "DKK - Danish Krone"},
    { "CODE": "EUR", "DISPLAY": "EUR - Euro"},
    { "CODE": "GBP", "DISPLAY": "GBP - Pound Sterling"},
    { "CODE": "HKD", "DISPLAY": "HKD - Hong Kong Dollar"},
    { "CODE": "HUF", "DISPLAY": "HUF - Hungarian Forint"},
    { "CODE": "INR", "DISPLAY": "INR - Indian Rupee"},
    { "CODE": "ILS", "DISPLAY": "ILS - Israeli New Sheqel"},
    { "CODE": "JPY", "DISPLAY": "JPY - Japanese Yen"},
    { "CODE": "MYR", "DISPLAY": "MYR - Malaysian Ringgit"},
    { "CODE": "MXN", "DISPLAY": "MXN - Mexican Peso"},
    { "CODE": "NOK", "DISPLAY": "NOK - Norwegian Krone"},
    { "CODE": "NZD", "DISPLAY": "NZD - New Zealand Dollar"},
    { "CODE": "PLN", "DISPLAY": "PLN - Polish Zloty"},
    { "CODE": "RUB", "DISPLAY": "RUB - Russian Ruble"},
    { "CODE": "SEK", "DISPLAY": "SEK - Swedish Krona"},
    { "CODE": "TWD", "DISPLAY": "TWD - Taiwan New Dollar"},
    { "CODE": "THB", "DISPLAY": "THB - Thai Baht"},
]

VISUAL_THEMES = [
    ( "asm", "asm", "#ffffff", _("Light") ),
    ( "asm-mid", "asm-mid", "#bbbbbb", _("Medium") ),
    ( "asm-mid-blue", "asm-mid", "#4e7dbf", _("Medium - Blue") ),
    ( "asm-mid-green", "asm-mid", "#47a56b", _("Medium - Green") ),
    ( "asm-mid-lilac", "asm-mid", "#914b89", _("Medium - Lilac") ),
    ( "asm-mid-orange", "asm-mid", "#eaae5b", _("Medium - Orange") ),
    ( "asm-mid-pink", "asm-mid", "#9b7388", _("Medium - Pink") ),
    ( "asm-mid-red", "asm-mid", "#ed5557", _("Medium - Red") ),
    ( "asm-mid-teal", "asm-mid", "#47a59a", _("Medium - Teal") ),
    ( "asm-dark", "asm-dark", "#000000", _("Dark") )
]

PETFINDER_BREEDS = (
    "**--Dogs",
    "Affenpinscher",
    "Afghan Hound",
    "Airedale Terrier",
    "Akbash",
    "Akita",
    "Alaskan Malamute",
    "American Bulldog",
    "American Bully",
    "American Eskimo Dog",
    "American Staffordshire Terrier",
    "American Water Spaniel",
    "Anatolian Shepherd",
    "Appenzell Mountain Dog",
    "Australian Cattle Dog/Blue Heeler",
    "Australian Kelpie",
    "Australian Shepherd",
    "Australian Terrier",
    "Basenji",
    "Basset Hound",
    "Beagle",
    "Bearded Collie",
    "Beauceron",
    "Bedlington Terrier",
    "Belgian Shepherd Dog Sheepdog",
    "Belgian Shepherd Laekenois",
    "Belgian Shepherd Malinois",
    "Belgian Shepherd Tervuren ",
    "Bernese Mountain Dog",
    "Bichon Frise",
    "Black and Tan Coonhound",
    "Black Labrador Retriever",
    "Black Mouth Cur",
    "Bloodhound",
    "Bluetick Coonhound",
    "Blue Lacy",
    "Border Collie",
    "Border Terrier",
    "Borzoi",
    "Boston Terrier",
    "Bouvier des Flanders",
    "Boykin Spaniel",
    "Boxer",
    "Briard",
    "Brittany Spaniel",
    "Brussels Griffon",
    "Bull Terrier",
    "Bullmastiff",
    "Cairn Terrier",
    "Canaan Dog",
    "Cane Corso Mastiff",
    "Carolina Dog",
    "Catahoula Leopard Dog",
    "Cattle Dog",
    "Cavalier King Charles Spaniel",
    "Chesapeake Bay Retriever",
    "Chihuahua",
    "Chinese Crested Dog",
    "Chinese Foo Dog",
    "Chocolate Labrador Retriever",
    "Chow Chow",
    "Clumber Spaniel",
    "Cockapoo",
    "Cocker Spaniel",
    "Collie",
    "Coonhound",
    "Corgi",
    "Coton de Tulear",
    "Dachshund",
    "Dalmatian",
    "Dandie Dinmont Terrier",
    "Doberman Pinscher",
    "Dogo Argentino",
    "Dogue de Bordeaux",
    "Dutch Shepherd",
    "English Bulldog",
    "English Cocker Spaniel",
    "English Coonhound",
    "English Pointer",
    "English Setter",
    "English Shepherd",
    "English Springer Spaniel",
    "English Toy Spaniel",
    "Entlebucher",
    "Eskimo Dog",
    "Feist",
    "Field Spaniel",
    "Fila Brasileiro",
    "Finnish Lapphund",
    "Finnish Spitz",
    "Flat-coated Retriever",
    "Fox Terrier",
    "Foxhound",
    "French Bulldog",
    "German Pinscher",
    "German Shepherd Dog",
    "German Shorthaired Pointer",
    "German Wirehaired Pointer",
    "Glen of Imaal Terrier",
    "Golden Retriever",
    "Gordon Setter",
    "Great Dane",
    "Great Pyrenees",
    "Greater Swiss Mountain Dog",
    "Greyhound",
    "Harrier",
    "Havanese",
    "Hound",
    "Hovawart",
    "Husky",
    "Ibizan Hound",
    "Illyrian Sheepdog",
    "Irish Setter",
    "Irish Terrier",
    "Irish Water Spaniel",
    "Irish Wolfhound",
    "Italian Greyhound",
    "Italian Spinone",
    "Jack Russell Terrier",
    "Japanese Chin",
    "Jindo",
    "Kai Dog",
    "Karelian Bear Dog",
    "Keeshond",
    "Kerry Blue Terrier",
    "Kishu",
    "Komondor",
    "Kuvasz",
    "Kyi Leo",
    "Labrador Retriever",
    "Lakeland Terrier",
    "Lancashire Heeler",
    "Lhasa Apso",
    "Leonberger",
    "Lowchen",
    "Maltese",
    "Manchester Terrier",
    "Maremma Sheepdog",
    "Mastiff",
    "McNab",
    "Miniature Pinscher",
    "Mixed Breed",
    "Mountain Cur",
    "Mountain Dog",
    "Munsterlander",
    "Neapolitan Mastiff",
    "New Guinea Singing Dog",
    "Newfoundland Dog",
    "Norfolk Terrier",
    "Norwich Terrier",
    "Norwegian Buhund",
    "Norwegian Elkhound",
    "Norwegian Lundehund",
    "Nova Scotia Duck-Tolling Retriever",
    "Old English Sheepdog",
    "Otterhound",
    "Papillon",
    "Patterdale Terrier (Fell Terrier)",
    "Pekingese",
    "Peruvian Inca Orchid",
    "Petit Basset Griffon Vendeen",
    "Pharaoh Hound",
    "Pit Bull Terrier",
    "Plott Hound",
    "Podengo Portugueso",
    "Pointer",
    "Polish Lowland Sheepdog",
    "Pomeranian",
    "Poodle",
    "Portuguese Water Dog",
    "Presa Canario",
    "Pug",
    "Puli",
    "Pumi",
    "Rat Terrier",
    "Redbone Coonhound",
    "Retriever",
    "Rhodesian Ridgeback",
    "Rottweiler",
    "Saluki",
    "Saint Bernard St. Bernard",
    "Samoyed",
    "Schipperke",
    "Schnauzer",
    "Scottish Deerhound",
    "Scottish Terrier Scottie",
    "Sealyham Terrier",
    "Setter",
    "Shar Pei",
    "Sheep Dog",
    "Shepherd",
    "Shetland Sheepdog Sheltie",
    "Shiba Inu",
    "Shih Tzu",
    "Siberian Husky",
    "Silky Terrier",
    "Skye Terrier",
    "Sloughi",
    "Smooth Fox Terrier",
    "Spaniel",
    "Spitz",
    "Staffordshire Bull Terrier",
    "South Russian Ovcharka",
    "Swedish Vallhund",
    "Terrier",
    "Thai Ridgeback",
    "Tibetan Mastiff",
    "Tibetan Spaniel",
    "Tibetan Terrier",
    "Tosa Inu",
    "Toy Fox Terrier",
    "Treeing Walker Coonhound",
    "Vizsla",
    "Weimaraner",
    "Welsh Corgi",
    "Welsh Terrier",
    "Welsh Springer Spaniel",
    "West Highland White Terrier Westie",
    "Wheaten Terrier",
    "Whippet",
    "White German Shepherd",
    "Wire-haired Pointing Griffon",
    "Wirehaired Terrier",
    "Yellow Labrador Retriever",
    "Yorkshire Terrier Yorkie",
    "Xoloitzcuintle/Mexican Hairless",
    "**--Cats",
    "Abyssinian",
    "American Curl",
    "American Shorthair",
    "American Wirehair",
    "Applehead Siamese",
    "Balinese",
    "Bengal",
    "Birman",
    "Bobtail",
    "Bombay",
    "British Shorthair",
    "Burmese",
    "Burmilla",
    "Calico",
    "Canadian Hairless",
    "Chartreux",
    "Chinchilla",
    "Cornish Rex",
    "Cymric",
    "Devon Rex",
    "Dilute Calico",
    "Dilute Tortoiseshell",
    "Domestic Long Hair",
    "Domestic Long Hair (Black)",
    "Domestic Long Hair (Black & White)",
    "Domestic Long Hair (Buff)",
    "Domestic Long Hair (Gray)",
    "Domestic Long Hair (Orange)",
    "Domestic Long Hair (Orange & White)",
    "Domestic Long Hair (Gray & White)",
    "Domestic Long Hair (White)",
    "Domestic Medium Hair",
    "Domestic Medium Hair (Black)",
    "Domestic Medium Hair (Black & White)",
    "Domestic Medium Hair (Buff)",
    "Domestic Medium Hair (Gray)",
    "Domestic Medium Hair (Gray & White)",
    "Domestic Medium Hair (Orange)",
    "Domestic Medium Hair (Orange & White)",
    "Domestic Medium Hair (White)",
    "Domestic Short Hair",
    "Domestic Short Hair (Black)",
    "Domestic Short Hair (Black & White)",
    "Domestic Short Hair (Buff)",
    "Domestic Short Hair (Gray)",
    "Domestic Short Hair (Gray & White)",
    "Domestic Short Hair (Mitted)",
    "Domestic Short Hair (Orange)",
    "Domestic Short Hair (Orange & White)",
    "Domestic Short Hair (White)",
    "Egyptian Mau",
    "Exotic Shorthair",
    "Extra-Toes Cat (Hemingway Polydactyl)",
    "Havana Brown",
    "Himalayan",
    "Japanese Bobtail",
    "Javanese",
    "Korat",
    "Maine Coon",
    "Manx",
    "Munchkin",
    "Nebelung", 
    "Norwegian Forest Cat",
    "Ocicat",
    "Oriental Long Hair",
    "Oriental Short Hair",
    "Oriental Tabby",
    "Persian",
    "Pixie-Bob",
    "Ragamuffin",
    "Ragdoll",
    "Russian Blue",
    "Scottish Fold",
    "Selkirk Rex",
    "Siamese",
    "Siberian",
    "Singapura",
    "Snowshoe",
    "Somali",
    "Sphynx (hairless cat)",
    "Tabby",
    "Tabby (Black)",
    "Tabby (Brown)",
    "Tabby (Buff)",
    "Tabby (Grey)",
    "Tabby (Orange)",
    "Tabby (White)",
    "Tiger",
    "Tonkinese",
    "Torbie",
    "Tortoiseshell",
    "Turkish Angora",
    "Turkish Van",
    "Tuxedo",
    "**--Rabbits",
    "American",
    "American Fuzzy Lop",
    "American Sable",
    "Angora Rabbit",
    "Belgian Hare",
    "Beveren",
    "Britannia Petite",
    "Bunny Rabbit",
    "Californian",
    "Champagne D'Argent",
    "Checkered Giant",
    "Chinchilla",
    "Cinnamon",
    "Creme D'Argent",
    "Dutch",
    "Dwarf",
    "Dwarf Eared",
    "English Lop",
    "English Spot",
    "Flemish Giant",
    "Florida White",
    "French-Lop",
    "Harlequin",
    "Havana",
    "Himalayan",
    "Holland Lop",
    "Hotot",
    "Jersey Wooly",
    "Lilac",
    "Lionhead",
    "Lop Eared",
    "Mini-Lop",
    "Mini Rex",
    "Netherland Dwarf",
    "New Zealand",
    "Palomino",
    "Polish",
    "Rex",
    "Rhinelander",
    "Satin",
    "Silver",
    "Silver Fox",
    "Silver Marten",
    "Tan",
    "**--Equine",
    "Appaloosa",
    "Arabian",
    "Clydesdale",
    "Donkey/Mule",
    "Draft",
    "Gaited ",
    "Grade",
    "Missouri Foxtrotter",
    "Morgan",
    "Mustang",
    "Paint/Pinto",
    "Palomino",
    "Paso Fino",
    "Percheron",
    "Peruvian Paso",
    "Pony",
    "Quarterhorse",
    "Saddlebred",
    "Standardbre",
    "Thoroughbred",
    "Tennessee Walker",
    "Warmblood",
    "**--Small Mammals",
    "Chinchilla",
    "Degu",
    "Ferret",
    "Gerbil",
    "Guinea Pig",
    "Hamster",
    "Hedgehog",
    "Mouse",
    "Prairie Dog",
    "Rat",
    "Skunk",
    "Sugar Glider",
    "Pot Bellied",
    "Vietnamese Pot Bellied",
    "**--Snakes and Reptiles",
    "Asian Box",
    "Ball Python",
    "Bearded Dragon",
    "Boa",
    "Boa Constrictor",
    "Box",
    "Bull Frog",
    "Burmese Python",
    "Chameleon",
    "Corn Snake",
    "Corn/Rat",
    "Eastern Box",
    "Fire-bellied",
    "Fire-bellied Newt",
    "Fire Salamander",
    "Florida Box",
    "Frog",
    "Garter/Ribbon",
    "Gecko",
    "Goldfish",
    "Hermit Crab",
    "Horned Frog",
    "Iguana",
    "King/Milk",
    "Leopard Frog",
    "Lizard",
    "Monitor",
    "Oregon Newt",
    "Ornamental Box",
    "Paddle Tailed Newt",
    "Python",
    "Red-eared Slider",
    "Red Foot",
    "Russian",
    "Snake",
    "Sulcata",
    "Tarantula",
    "Three Toed Box",
    "Tiger Salamander",
    "Tortoise",
    "Tree Frog",
    "Toad",
    "Turtle",
    "Uromastyx",
    "Yellow-Bellied Slider", 
    "**--Fish",
    "Fish",
    "Freshwater Fish",
    "Saltwater Fish",
    "**--Birds",
    "African Grey",
    "Amazon",
    "Brotogeris",
    "Budgie/Budgerigar",
    "Caique",
    "Canary",
    "Chicken",
    "Cockatiel",
    "Cockatoo",
    "Conure",
    "Dove",
    "Duck",
    "Eclectus",
    "Emu",
    "Finch",
    "Goose",
    "Guinea fowl",
    "Kakariki",
    "Lory/Lorikeet",
    "Lovebird",
    "Macaw",
    "Mynah",
    "Ostrich",
    "Parakeet (Other)",
    "Parrot (Other)",
    "Parrotlet",
    "Peacock/Pea fowl",
    "Pheasant",
    "Pigeon",
    "Pionus",
    "Poicephalus/Senegal",
    "Quaker Parakeet",
    "Rhea",
    "Ringneck/Psittacula",
    "Rosella",
    "Softbill (Other)",
    "Swan",
    "Toucan",
    "Turkey",
    "**--Farm Animals",
    "Alpaca",
    "Cow",
    "Goat",
    "Sheep",
    "Llama",
    "Pig (Farm)"
)

PETFINDER_SPECIES = (
    "Barnyard", "Bird", "Cat", "Dog", "Horse", "Pig", "Rabbit",
    "Reptile", "Scales, Fins & Other", "Small&Furry"
)

ADOPTAPET_COLOURS = (
    "**--Dogs",
    "Black",
    "Black - with Tan, Yellow or Fawn",
    "Black - with White",
    "Brindle",
    "Brindle - with White",
    "Brown/Chocolate",
    "Brown/Chocolate - with Black",
    "Brown/Chocolate - with White",
    "Red/Golden/Orange/Chestnut",
    "Red/Golden/Orange/Chestnut - with Black",
    "Red/Golden/Orange/Chestnut - with White",
    "Silver & Tan (Yorkie colors)",
    "Tan/Yellow/Fawn",
    "Tan/Yellow/Fawn - with White",
    "Tricolor (Tan/Brown & Black & White)",
    "White",
    "White - with Black",
    "White - with Brown or Chocolate",
    "Black - with Brown, Red, Golden, Orange or Chestnut",
    "Black - with Gray or Silver",
    "Brown/Chocolate - with Tan",
    "Gray/Blue/Silver/Salt & Pepper",
    "Gray/Silver/Salt & Pepper - with White",
    "Gray/Silver/Salt & Pepper - with Black",
    "Merle",
    "Tan/Yellow/Fawn - with Black",
    "White - with Tan, Yellow or Fawn",
    "White - with Red, Golden, Orange or Chestnut",
    "White - with Gray or Silver",
    "**--Cats",
    "Black (All)",
    "Cream or Ivory",
    "Cream or Ivory (Mostly)",
    "Spotted Tabby/Leopard Spotted",
    "Black (Mostly)",
    "Black & White or Tuxedo",
    "Brown or Chocolate",
    "Brown or Chocolate (Mostly)",
    "Brown Tabby",
    "Calico or Dilute Calico",
    "Gray or Blue ",
    "Gray or Blue (Mostly)",
    "Gray, Blue or Silver Tabby",
    "Orange or Red",
    "Orange or Red (Mostly)",
    "Orange or Red Tabby",
    "Tan or Fawn ",
    "Tan or Fawn (Mostly)",
    "Tan or Fawn Tabby",
    "Tiger Striped",
    "Tortoiseshell",
    "White",
    "White (Mostly)",
    "**--Horses",
    "Palomino",
    "Gray",
    "Dun",
    "Cremello",
    "Chestnut/Sorrel",
    "Champagne",
    "Buckskin",
    "Black",
    "Bay",
    "Appy",
    "Grullo",
    "White",
    "Roan",
    "Perlino",
    "Paint",
    "**--Birds",
    "Gray",
    "Green",
    "Olive",
    "Orange",
    "Pink",
    "Purple/Violet",
    "Red",
    "Rust",
    "Tan",
    "Buff",
    "Yellow",
    "White",
    "Black",
    "Blue",
    "Brown",
    "**--Rabbits",
    "Sable",
    "Albino or Red-Eyed White",
    "Blue",
    "Black",
    "Blond/Golden",
    "Chinchilla",
    "Chocolate",
    "Cinnamon",
    "Copper",
    "Cream",
    "Dutch",
    "Fawn",
    "Grey/Silver",
    "Harlequin",
    "Lilac",
    "Multi",
    "Orange",
    "Red",
    "Agouti",
    "Siamese",
    "Tan",
    "Tortoise",
    "Tri-color",
    "White",
    "**--Small Animals",
    "Yellow",
    "White",
    "Tortoiseshell",
    "Tan or Beige",
    "Silver or Gray",
    "Sable",
    "Red",
    "Orange",
    "Multi",
    "Lilac",
    "Golden",
    "Cream",
    "Calico",
    "Buff",
    "Brown or Chocolate",
    "Blonde",
    "Black",
    "Albino or Red-Eyed White"
)

def add_message(dbo: Database, createdby: str, email: int, message: str, forname: str = "*", 
                priority: int = 0, expires: datetime = None, added: datetime = None) -> int:
    if added is None: added = dbo.today()
    if expires is None: expires = dbo.today(offset=7)
    l = dbo.locale
    mid = dbo.insert("messages", {
        "Added":        added,
        "Expires":      expires,
        "CreatedBy":    createdby,
        "Priority":     priority,
        "ForName":      forname,
        "Message":      message
    })
    # If email is set, we email the message to everyone that it would match
    if email == 1:
        asm3.utils.send_user_email(dbo, createdby, forname, _("Message from {0}", l).format(createdby), message)
    return mid

def delete_message(dbo: Database, mid: int) -> None:
    dbo.delete("messages", mid)

def get_account_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lksaccounttype ORDER BY AccountType")

def get_additionalfield_links(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lksfieldlink ORDER BY LinkType")

def get_additionalfield_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lksfieldtype ORDER BY FieldType")

def _merge_db_flags(dbflags: Results, flags: str = "") -> Results:
    """
    Given a list of flag results from the database, adds any that are not present from
    the pipe separated list of flags from an ADDITIONALFLAGS column.
    The built in lower-case flags are ignored.
    """
    BUILTINS = [ "aco", "adopter", "banned", "coordinator", "dangerous", "deceased", "donor", "driver", 
        "excludefrombulkemail", "fosterer", "giftaid", "homechecked", "homechecker", "member", "padopter", 
        "retailer", "shelter", "staff", "sponsor", "vet", "volunteer", "supplier",
        "courtesy", "crueltycase", "nonshelter", "notforadoption", "notforregistration", "quarantine" ]
    if flags is None or flags == "" or flags == "|": return dbflags
    out = dbflags.copy()
    for f in flags.split("|"):
        f = f.strip()
        if f == "": continue
        if f in BUILTINS: continue
        match = False
        for r in dbflags:
            if r.FLAG == f: match = True
        if not match:
            out.append({ "FLAG": f, "ISRETIRED": 0 })
    return out

def get_animal_flags(dbo: Database, flags: str = "") -> Results:
    dbflags = dbo.query("SELECT * FROM lkanimalflags WHERE IsRetired=0 ORDER BY Flag")
    return _merge_db_flags(dbflags, flags)

def get_animal_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM animaltype ORDER BY AnimalType")

def get_animaltype_name(dbo: Database, aid: int) -> str:
    if id is None: return ""
    return dbo.query_string("SELECT AnimalType FROM animaltype WHERE ID = ?", [aid])

def get_basecolours(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM basecolour ORDER BY BaseColour")

def get_basecolour_name(dbo: Database, cid: int) -> str:
    if id is None: return ""
    return dbo.query_string("SELECT BaseColour FROM basecolour WHERE ID = ?", [cid])

def get_boarding_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lkboardingtype ORDER BY BoardingName")

def get_breeds(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM breed ORDER BY BreedName")

def get_breeds_by_species(dbo: Database) -> Results:
    return dbo.query("SELECT breed.*, species.SpeciesName FROM breed " \
        "LEFT OUTER JOIN species ON breed.SpeciesID = species.ID " \
        "ORDER BY species.SpeciesName, breed.BreedName")

def get_clinic_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lkclinictype ORDER BY ClinicTypeName")

def get_species_for_breed(dbo: Database, bid: int) -> int:
    return dbo.query_int("SELECT SpeciesID FROM breed WHERE ID=?", [bid])

def get_breed_name(dbo: Database, bid: int) -> str:
    if id is None: return ""
    return dbo.query_string("SELECT BreedName FROM breed WHERE ID = ?", [bid])

def get_citation_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM citationtype ORDER BY CitationName")

def get_clinic_statuses(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lksclinicstatus ORDER BY ID")

def get_coattypes(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lkcoattype ORDER BY CoatType")

def get_costtypes(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM costtype ORDER BY CostTypeName")

def get_coattype_name(dbo: Database, cid: int) -> str:
    if id is None: return ""
    return dbo.query_string("SELECT CoatTypeName FROM lkcoattype WHERE ID = ?", [cid])

def get_deathreasons(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM deathreason ORDER BY ReasonName")

def get_deathreason_name(dbo: Database, rid: int) -> str:
    if id is None: return ""
    return dbo.query_string("SELECT ReasonName FROM deathreason WHERE ID = ?", [rid])

def get_diets(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM diet ORDER BY DietName")

def get_donation_default(dbo: Database, donationtypeid: int) -> int:
    return dbo.query_int("SELECT DefaultCost FROM donationtype WHERE ID = ?", [donationtypeid])

def get_donation_frequencies(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lksdonationfreq ORDER BY ID")

def get_donation_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM donationtype ORDER BY DonationName")

def get_donationtype_name(dbo: Database, did: int) -> str:
    if did is None: return ""
    return dbo.query_string("SELECT DonationName FROM donationtype WHERE ID = ?", [did])

def get_entryreasons(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM entryreason ORDER BY ReasonName")

def get_entryreason_name(dbo: Database, rid: int) -> str:
    if rid is None: return ""
    return dbo.query_string("SELECT ReasonName FROM entryreason WHERE ID = ?", [rid])

def get_entry_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lksentrytype ORDER BY EntryTypeName")

def get_incident_completed_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM incidentcompleted ORDER BY CompletedName")

def get_incident_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM incidenttype ORDER BY IncidentName")

def get_internal_locations(dbo: Database, lf: LocationFilter = None) -> Results:
    clauses = []
    if lf is not None and lf.locationfilter != "": clauses.append("ID IN (%s)" % lf.locationfilter)
    if lf is not None and lf.siteid != 0: clauses.append("SiteID = %s" % lf.siteid)
    c = " AND ".join(clauses)
    if c != "": c = "WHERE %s" % c
    return dbo.query("SELECT * FROM internallocation %s ORDER BY LocationName" % c)

def get_internal_locations_counts(dbo: Database, lf: LocationFilter = None) -> Results:
    clauses = []
    if lf is not None and lf.locationfilter != "": clauses.append("ID IN (%s)" % lf.locationfilter)
    if lf is not None and lf.siteid != 0: clauses.append("SiteID = %s" % lf.siteid)
    c = " AND ".join(clauses)
    if c != "": c = "WHERE %s" % c
    return dbo.query("SELECT *, " \
        "(SELECT COUNT(*) FROM animal WHERE Archived=0 AND (ActiveMovementType Is Null OR ActiveMovementType=0) AND " \
            "ShelterLocation=internallocation.ID) AS Total " \
        "FROM internallocation %s ORDER BY LocationName" % c)

def get_internallocation_name(dbo: Database, lid: int) -> str:
    if lid is None: return ""
    return dbo.query_string("SELECT LocationName FROM internallocation WHERE ID = ?", [lid])

def get_jurisdictions(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM jurisdiction ORDER BY JurisdictionName")

def get_licence_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM licencetype ORDER BY LicenceTypeName")

def get_messages(dbo: Database, user: str, roles: str, superuser: int) -> Results:
    """
    Returns a list of messages for the user given.
    user: The user to get messages for
    roles: A pipe separated list of roles the user is in (session.roles)
    superuser: 1 if the user is a superuser
    """
    messages = dbo.query("SELECT * FROM messages WHERE Expires >= ? ORDER BY ID DESC", [dbo.today()])
    rv = []
    # Add messages our user can see
    for m in messages:
        if m.FORNAME == "*":
            rv.append(m)
        elif m.FORNAME == user:
            rv.append(m)
        elif m.CREATEDBY == user:
            rv.append(m)
        #elif superuser == 1:
        #    rv.append(m)
        elif roles is not None and roles.find(m.FORNAME) != -1:
            rv.append(m)
    return rv

def get_log_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM logtype ORDER BY LogTypeName")

def get_logtype_name(dbo: Database, tid: int) -> str:
    if tid is None: return ""
    return dbo.query_string("SELECT LogTypeName FROM logtype WHERE ID = ?", [tid])

def get_media_flags(dbo: Database, flags: str = "") -> Results:
    dbflags = dbo.query("SELECT * FROM lkmediaflags WHERE IsRetired=0 ORDER BY Flag")
    return _merge_db_flags(dbflags, flags)

def get_theme(theme: str) -> Tuple[str, str, str, str]:
    """ Returns a tuple of values code, jq, bg, name for a theme """
    for code, jq, bg, name in VISUAL_THEMES:
        if code == theme:
            return (code, jq, bg, name)
    return ("asm", "asm", "#ffffff", "Light")

def get_lookup(dbo: Database, tablename: str, namefield: str) -> Results:
    if tablename == "breed":
        return dbo.query("SELECT b.*, s.SpeciesName FROM breed b LEFT OUTER JOIN species s ON s.ID = b.SpeciesID ORDER BY b.BreedName")
    return dbo.query("SELECT * FROM %s ORDER BY %s" % ( tablename, namefield ))

def insert_lookup(dbo: Database, username: str, lookup: str, name: str, desc: str = "", 
                  speciesid: int = 0, pfbreed: str = "", pfspecies: str = "", apcolour: str = "", 
                  units: str = "", site: int = 1, rescheduledays: int = 0, accountid: int = 0, 
                  defaultcost: int = 0, vat: int = 0, retired: int = 0, taxrate: float = 0) -> int:
    t = LOOKUP_TABLES[lookup]
    nid = 0
    if lookup == "basecolour":
        return dbo.insert("basecolour", {
            "BaseColour":               name,
            "BaseColourDescription":    desc,
            "AdoptAPetColour":          apcolour,
            "IsRetired":                retired
        }, username, setCreated=False)
    elif lookup == "breed":
        return dbo.insert("breed", {
            "BreedName":        name,
            "BreedDescription": desc,
            "PetFinderBreed":   pfbreed,
            "SpeciesID":        speciesid,
            "IsRetired":        retired
        }, username, setCreated=False)
    elif lookup == "internallocation":
        return dbo.insert("internallocation", {
            "LocationName":         name,
            "LocationDescription":  desc,
            "Units":                units,
            "SiteID":               site,
            "IsRetired":            retired
        }, username, setCreated=False)
    elif lookup == "species":
        return dbo.insert("species", {
            "SpeciesName":          name,
            "SpeciesDescription":   desc,
            "PetFinderSpecies":     pfspecies,
            "IsRetired":            retired
        }, username, setCreated=False)
    elif lookup == "costtype":
        # Create a matching account if the option is on and link it
        if asm3.configuration.create_cost_trx(dbo):
            accountid = asm3.financial.insert_account_from_costtype(dbo, name, desc)
        nid = dbo.insert(lookup, {
            t[LOOKUP_NAMEFIELD]:    name,
            t[LOOKUP_DESCFIELD]:    desc,
            "DefaultCost":          defaultcost,
            "AccountID":            accountid,
            "IsRetired":            retired
        }, username, setCreated=False)
        return nid
    elif lookup == "donationtype":
        if accountid == 0 and asm3.configuration.create_donation_trx(dbo):
            accountid = asm3.financial.insert_account_from_donationtype(dbo, name, desc)
        nid = dbo.insert(lookup, {
            t[LOOKUP_NAMEFIELD]:    name,
            t[LOOKUP_DESCFIELD]:    desc,
            "DefaultCost":          defaultcost,
            "AccountID":            accountid,
            "IsVAT":                vat,
            "IsRetired":            retired
        }, username, setCreated=False)
        return nid
    elif lookup == "voucher" or lookup == "traptype" or lookup == "citationtype" or lookup == "lkboardingtype":
        nid = dbo.insert(lookup, {
            t[LOOKUP_NAMEFIELD]:    name,
            t[LOOKUP_DESCFIELD]:    desc,
            "DefaultCost":          defaultcost,
            "IsRetired":            retired
        }, username, setCreated=False)
        return nid
    elif lookup == "licencetype" or lookup == "testtype" or lookup == "vaccinationtype":
        nid = dbo.insert(lookup, {
            t[LOOKUP_NAMEFIELD]:    name,
            t[LOOKUP_DESCFIELD]:    desc,
            "DefaultCost":          defaultcost,
            "RescheduleDays":       rescheduledays,
            "IsRetired":            retired
        }, username, setCreated=False)
        return nid
    elif lookup == "lkownerflags" or lookup == "lkanimalflags":
        name = name.replace(",", " ").replace("|", " ").replace("'", " ") # Remove bad chars
        name = asm3.utils.strip_duplicate_spaces(name) # Strip dup spaces Bad   Flag->Bad Flag
        return dbo.insert(lookup, {
            t[LOOKUP_NAMEFIELD]:    name,
            "IsRetired":            retired
        }, username, setCreated=False)
    elif lookup == "lktaxrate":
        return dbo.insert(lookup, {
            t[LOOKUP_NAMEFIELD]:    name,
            t[LOOKUP_DESCFIELD]:    desc,
            "TaxRate":              taxrate,
            "IsRetired":            retired
        }, username, setCreated=False)
    elif t[LOOKUP_DESCFIELD] == "":
        # No description
        if t[LOOKUP_MODIFIERS].find("ret") != -1:
            return dbo.insert(lookup, { t[LOOKUP_NAMEFIELD]: name, "IsRetired": retired }, username, setCreated=False)    
        else:
            return dbo.insert(lookup, { t[LOOKUP_NAMEFIELD]: name }, username, setCreated=False)    
    else:
        # Name/Description
        if t[LOOKUP_MODIFIERS].find("ret") != -1:
            return dbo.insert(lookup, { t[LOOKUP_NAMEFIELD]: name, t[LOOKUP_DESCFIELD]: desc, "IsRetired": retired }, username, setCreated=False)
        else:
            return dbo.insert(lookup, { t[LOOKUP_NAMEFIELD]: name, t[LOOKUP_DESCFIELD]: desc }, username, setCreated=False)

def update_lookup(dbo: Database, username: str, iid: int, lookup: str, name: str, desc: str = "", 
                  speciesid: int = 0, pfbreed: str = "", pfspecies: str = "", apcolour: str = "", units: str = "", 
                  site: int = 1, rescheduledays: int = 0, accountid: int = 0, 
                  defaultcost: int = 0, vat: int = 0, retired: int = 0, taxrate: float = 0) -> None:
    t = LOOKUP_TABLES[lookup]
    if lookup == "basecolour":
        dbo.update("basecolour", iid, { 
            "BaseColour":               name,
            "BaseColourDescription":    desc,
            "AdoptAPetColour":          apcolour,
            "IsRetired":                retired
        }, username, setLastChanged=False)
    elif lookup == "breed":
        dbo.update("breed", iid, {
            "BreedName":            name,
            "BreedDescription":     desc,
            "PetFinderBreed":       pfbreed,
            "SpeciesID":            speciesid,
            "IsRetired":            retired
        }, username, setLastChanged=False)
    elif lookup == "internallocation":
        dbo.update("internallocation", iid, {
            "LocationName":         name,
            "LocationDescription":  desc,
            "Units":                units,
            "SiteID":               site,
            "IsRetired":            retired
        }, username, setLastChanged=False)
    elif lookup == "species":
        dbo.update("species", iid, {
            "SpeciesName":          name,
            "SpeciesDescription":   desc,
            "PetFinderSpecies":     pfspecies,
            "IsRetired":            retired
        }, username, setLastChanged=False)
    elif lookup == "costtype":
        dbo.update(lookup, iid, {
            t[LOOKUP_NAMEFIELD]:    name,
            t[LOOKUP_DESCFIELD]:    desc,
            "DefaultCost":          defaultcost,
            "AccountID":            accountid,
            "IsRetired":            retired
        }, username, setLastChanged=False)
    elif lookup == "donationtype":
        dbo.update(lookup, iid, {
            t[LOOKUP_NAMEFIELD]:    name,
            t[LOOKUP_DESCFIELD]:    desc,
            "DefaultCost":          defaultcost,
            "AccountID":            accountid,
            "IsVAT":                vat,
            "IsRetired":            retired
        }, username, setLastChanged=False)
    elif lookup == "voucher" or lookup == "traptype" or lookup == "citationtype" or lookup == "lkboardingtype":
        dbo.update(lookup, iid, {
            t[LOOKUP_NAMEFIELD]:    name,
            t[LOOKUP_DESCFIELD]:    desc,
            "DefaultCost":          defaultcost,
            "IsRetired":            retired
        }, username, setLastChanged=False)
    elif lookup == "licencetype" or lookup == "testtype" or lookup == "vaccinationtype":
        dbo.update(lookup, iid, {
            t[LOOKUP_NAMEFIELD]:    name,
            t[LOOKUP_DESCFIELD]:    desc,
            "RescheduleDays":       rescheduledays,
            "DefaultCost":          defaultcost,
            "IsRetired":            retired
        }, username, setLastChanged=False)
    elif lookup == "lkownerflags" or lookup == "lkanimalflags":
        oldflag = dbo.query_string("SELECT Flag FROM %s WHERE ID = ?" % lookup, [iid])
        newflag = name.replace(",", " ").replace("|", " ").replace("'", " ") # Remove bad chars
        newflag = asm3.utils.strip_duplicate_spaces(newflag) # Strip dup spaces Bad   Flag->Bad Flag
        dbo.update(lookup, iid, { t[LOOKUP_NAMEFIELD]: newflag, "IsRetired": retired }, username, setLastChanged=False)
        # Update the text in flags fields where appropriate
        if lookup == "lkownerflags":
            dbo.execute("UPDATE owner SET AdditionalFlags = %s WHERE AdditionalFlags LIKE ?" % dbo.sql_replace("AdditionalFlags"), (f"{oldflag}|", f"{newflag}|", f"%{oldflag}|%"))
        elif lookup == "lkanimalflags":
            dbo.execute("UPDATE animal SET AdditionalFlags = %s WHERE AdditionalFlags LIKE ?" % dbo.sql_replace("AdditionalFlags"), (f"{oldflag}|", f"{newflag}|", f"%{oldflag}|%"))
    elif lookup == "lktaxrate":
        dbo.update(lookup, iid, {
            t[LOOKUP_NAMEFIELD]:    name,
            t[LOOKUP_DESCFIELD]:    desc,
            "TaxRate":              taxrate,
            "IsRetired":            retired
        }, username, setLastChanged=False)
    elif t[LOOKUP_DESCFIELD] == "":
        # No description
        if t[LOOKUP_MODIFIERS].find("ret") != -1:
            dbo.update(lookup, iid, { t[LOOKUP_NAMEFIELD]: name, "IsRetired": retired }, username, setLastChanged=False)
        else:
            dbo.update(lookup, iid, { t[LOOKUP_NAMEFIELD]: name }, username, setLastChanged=False)
    else:
        # Name/Description
        if t[LOOKUP_MODIFIERS].find("ret") != -1:
            dbo.update(lookup, iid, { t[LOOKUP_NAMEFIELD]: name, t[LOOKUP_DESCFIELD]: desc, "IsRetired": retired }, username, setLastChanged=False)
        else:
            dbo.update(lookup, iid, { t[LOOKUP_NAMEFIELD]: name, t[LOOKUP_DESCFIELD]: desc }, username, setLastChanged=False)

def update_lookup_retired(dbo: Database, username: str, lookup: str, iid: int, retired: int) -> None:
    """ Updates lookup item with ID=iid, setting IsRetired=retired """
    dbo.update(lookup, iid, { "IsRetired": retired }, username, setLastChanged=False)

def delete_lookup(dbo: Database, username: str, lookup: str, iid: int) -> None:
    l = dbo.locale
    t = LOOKUP_TABLES[lookup]
    for fv in t[LOOKUP_FOREIGNKEYS]:
        table, field = fv.split(".")
        if 0 < dbo.query_int("SELECT COUNT(*) FROM %s WHERE %s = %s" % (table, field, iid)):
            raise asm3.utils.ASMValidationError(_("This item is referred to in the database ({0}) and cannot be deleted until it is no longer in use.", l).format(fv))
    dbo.delete(lookup, iid, username)

def get_microchip_manufacturer(l: str, chipno: str) -> str:
    """
    Figures out the microchip manufacturer of chipno. 
    Returns a blank for a blank chip number and does validation for a chip number
        with no matching manufacturer.
    """
    mf = None
    if chipno is None or chipno == "": return ""
    for prefix in get_microchip_prefixes():
        if len(chipno) == prefix["length"] and re.compile(prefix["regex"]).match(chipno):
            if prefix["locales"] == "" or l in prefix["locales"].split(" "):
                mf = prefix["name"]
                break
    if mf is None and (len(chipno) != 9 and len(chipno) != 10 and len(chipno) != 15):
        return _("Invalid microchip number length", l)
    if mf is None:
        return _("Unknown microchip brand", l)
    return mf

def get_microchip_prefixes() -> List[Dict[str, str]]:
    """ Returns the chipprefixes.txt file from the server as a dictionary with elements length, regex, name, locale.
        This file is in the format:
        LENGTH | REGEX | NAME | LOCALES 
        Whitespace between the pipes will be suppressed. The locales element is optional,
        with an empty string making the prefix applied to all locales.
        Eg: 
        15 | ^956     | AVID | en en_US
        15 | ^98102   | DataMARS
    """
    try:
        CACHE_TTL = 86400
        s = asm3.cachedisk.get("chipprefixes", "chipprefixes")
        if s is None:
            s = asm3.utils.get_url(URL_MICROCHIP_PREFIXES)["response"]
            if not URL_MICROCHIP_PREFIXES.startswith("file:"):
                asm3.cachedisk.put("chipprefixes", "chipprefixes", s, CACHE_TTL)
        asm3.al.debug("read chipprefixes.txt (%s bytes)" % len(s), "lookups.get_microchip_prefixes")
        prefixes = []
        for p in s.split("\n"):
            if p.startswith("#"): continue
            m = p.split("|")
            if len(m) < 3: continue
            clen = m[0].strip()
            cregex = m[1].strip()
            cname = m[2].strip()
            clocale = ""
            if len(m) == 4: clocale = m[3].strip()
            prefixes.append( { "length": asm3.utils.cint(clen), "regex": cregex, "name": cname, "locales": clocale  })
        return prefixes
    except Exception as err:
        asm3.al.error("Failed reading chipprefixes.txt: %s" % err, "lookups.get_microchip_prefixes")

def get_movementtype_name(dbo: Database, mid: int) -> str:
    if mid is None: return ""
    return dbo.query_string("SELECT MovementType FROM lksmovementtype WHERE ID = ?", [mid])

def get_movement_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lksmovementtype ORDER BY ID")

def get_paymentmethod_name(dbo: Database, pid: int) -> str:
    if pid is None: return ""
    return dbo.query_string("SELECT PaymentName FROM donationpayment WHERE ID = ?", [pid])

def get_payment_methods(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM donationpayment ORDER BY PaymentName")

def get_person_flags(dbo: Database, flags: str = "") -> Results:
    dbflags = dbo.query("SELECT * FROM lkownerflags WHERE IsRetired=0 ORDER BY Flag")
    return _merge_db_flags(dbflags, flags)

def get_pickup_locations(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM pickuplocation ORDER BY LocationName")

def get_posneg(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lksposneg ORDER BY Name")

def get_product_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lkproducttype ORDER BY ProductTypeName")

def get_reservation_statuses(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM reservationstatus ORDER BY StatusName")

def get_rota_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lksrotatype ORDER BY ID")

def get_sex_name(dbo: Database, sid: int) -> str:
    if id is None: return ""
    return dbo.query_string("SELECT Sex FROM lksex WHERE ID = ?", [sid])

def get_sexes(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lksex ORDER BY Sex")

def get_sites(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM site ORDER BY SiteName")

def get_site_name(dbo: Database, sid: int) -> str:
    if sid is None: return ""
    return dbo.query_string("SELECT SiteName FROM site WHERE ID = ?", [sid])

def get_size_name(dbo: Database, sid: int) -> str:
    if sid is None: return ""
    return dbo.query_string("SELECT Size FROM lksize WHERE ID = ?", [sid])

def get_species(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM species ORDER BY SpeciesName")

def get_species_name(dbo: Database, sid: int) -> str:
    if id is None: return ""
    return dbo.query_string("SELECT SpeciesName FROM species WHERE ID = ?", [sid])

def update_species_id(dbo: Database, find: str, replace: str) -> int:
    """ Changes all instances of speciesid from find to replace """
    cols = [ "animal.SpeciesID", "animalcontrol.SpeciesID", "animalfiguresannual.SpeciesID",
        "animallitter.SpeciesID", "animallostfoundmatch.LostSpeciesID", "animallostfoundmatch.FoundSpeciesID",
        "animalwaitinglist.SpeciesID", "breed.SpeciesID", "onlineformfield.SpeciesID",
        "animallost.AnimalTypeID", "animalfound.AnimalTypeID", "species.ID" ]
    affected = 0
    for c in cols:
        table, col = c.split(".")
        q = f"UPDATE {table} SET {col}={replace} WHERE {col}={find}"
        affected += dbo.execute(q)
    return affected

def get_sizes(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lksize ORDER BY Size")

def get_stock_locations(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM stocklocation ORDER BY LocationName")

def get_stock_location_name(dbo: Database, slid: int) -> str:
    if slid is None: return ""
    return dbo.query_string("SELECT LocationName FROM stocklocation WHERE ID = ?", [slid])

def get_stock_usage_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM stockusagetype ORDER BY UsageTypeName")

def get_trap_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM traptype ORDER BY TrapTypeName")

def get_urgencies(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lkurgency ORDER BY ID")

def get_urgency_name(dbo: Database, uid: int) -> str:
    if id is None: return ""
    return dbo.query_string("SELECT Urgency FROM lkurgency WHERE ID = ?", [uid])

def get_tax_rates(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lktaxrate ORDER BY TaxRateName")

def get_test_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM testtype ORDER BY TestName")

def get_test_results(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM testresult ORDER BY ResultName")

def get_transport_statuses(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lkstransportstatus ORDER BY ID")

def get_transport_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM transporttype ORDER BY TransportTypeName")

def get_vaccination_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM vaccinationtype ORDER BY VaccinationType")

def get_voucher_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM voucher ORDER BY VoucherName")

def get_waitinglist_removals(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lkwaitinglistremoval ORDER BY RemovalName")

def get_work_types(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lkworktype ORDER BY WorkType")

def get_yesno(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lksyesno ORDER BY Name")

def get_ynun(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lksynun ORDER BY ID")

def get_ynunk(dbo: Database) -> Results:
    return dbo.query("SELECT * FROM lksynunk ORDER BY ID")

