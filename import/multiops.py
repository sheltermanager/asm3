#!/usr/bin/python

import asm

"""
Import script for Multiple Options SQL Server databases exported to MDB and then CSV

7th September, 2015 - 8th Feb, 2018
"""

PATH = "/home/robin/tmp/asm3_import_data/multiops_dm1807"
START_ID = 500
IMPORT_IMAGES = False
ADOPT_LONGER_THAN_DAYS = 0 # All animals on shelter longer than this, auto adopt to unknown owner (default 365)
DEFAULT_INTAKE_DATE = asm.getdate_yyyymmdd("2017/12/31")

owners = []
ownerlicences = []
logs = []
movements = []
animals = []
animalmedicals = []
animalcontrol = []
animalcontrolanimals = []
animalvaccinations = []

ppa = {}
ppo = {}
ppac = {}

intakes = {} # map of tblAnimalsID -> tblAnimalIntakesDisposition row for speed processing large tblAnimals

asm.setid("animal", START_ID)
asm.setid("animalcontrol", START_ID)
asm.setid("animalmedical", START_ID)
asm.setid("animalmedicaltreatment", START_ID)
asm.setid("animalvaccination", START_ID)
asm.setid("log", START_ID)
asm.setid("owner", START_ID)
asm.setid("ownerlicence", START_ID)
asm.setid("adoption", START_ID)
asm.setid("media", START_ID)
asm.setid("dbfs", START_ID)

# Remove existing
print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM additional WHERE LinkID >= %d;" % START_ID
print "DELETE FROM animal WHERE ID >= %d;" % START_ID
print "DELETE FROM animalcontrol WHERE ID >= %d;" % START_ID
print "DELETE FROM animalmedical WHERE ID >= %d;" % START_ID
print "DELETE FROM animalmedicaltreatment WHERE ID >= %d;" % START_ID
print "DELETE FROM animalvaccination WHERE ID >= %d;" % START_ID
print "DELETE FROM log WHERE ID >= %d;" % START_ID
print "DELETE FROM owner WHERE ID >= %d;" % START_ID
print "DELETE FROM ownerlicence WHERE ID >= %d;" % START_ID
print "DELETE FROM adoption WHERE ID >= %d;" % START_ID
print "DELETE FROM media WHERE ID >= %d;" % START_ID
print "DELETE FROM dbfs WHERE ID >= %d;" % START_ID

# Create a transfer owner
to = asm.Owner()
owners.append(to)
to.OwnerSurname = "Other Shelter"
to.OwnerName = to.OwnerSurname

# And an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname

# Load up data files
asm.stderr("Load data files")
canimaldispo = asm.csv_to_list("%s/sysAnimalDispositionChoices.csv" % PATH)
canimalrectypes = asm.csv_to_list("%s/sysAnimalReceivedTypes.csv" % PATH)
canimalstatuses = asm.csv_to_list("%s/sysAnimalStatusChoices.csv" % PATH)
cbreeds = asm.csv_to_list("%s/sysBreeds.csv" % PATH)
ccolors = asm.csv_to_list("%s/sysCoatColors.csv" % PATH)
cgenders = asm.csv_to_list("%s/sysGenderChoices.csv" % PATH)
cpens = asm.csv_to_list("%s/sysPens.csv" % PATH)
cshelterareas = asm.csv_to_list("%s/sysShelterAreas.csv" % PATH)
cspecies = asm.csv_to_list("%s/sysSpecies.csv" % PATH)
cvacctype = asm.csv_to_list("%s/sysVaccinations.csv" % PATH)
cadoptions = asm.csv_to_list("%s/tblAdoptions.csv" % PATH)
canimalguardians = asm.csv_to_list("%s/tblAnimalGuardians.csv" % PATH)
canimals = asm.csv_to_list("%s/tblAnimals.csv" % PATH)
canimalids = asm.csv_to_list("%s/tblAnimalIDs.csv" % PATH)
canimalimages = []
if IMPORT_IMAGES: canimalimages = asm.csv_to_list("%s/tblAnimalImages.csv" % PATH)
canimalintakes = asm.csv_to_list("%s/tblAnimalIntakesDispositions.csv" % PATH)
canimalsnotes = asm.csv_to_list("%s/tblAnimalsNotes.csv" % PATH)
ccomplaints = asm.csv_to_list("%s/tblComplaints.csv" % PATH)
ccomplaintsanimals = asm.csv_to_list("%s/tblComplaintsAnimals.csv" % PATH)
ccomplaintsnotes = asm.csv_to_list("%s/tblComplaintsNotes.csv" % PATH)
ccomplaintspeople = asm.csv_to_list("%s/tblComplaintsKnownPersons.csv" % PATH)
ccomplainttypes = asm.csv_to_list("%s/sysComplaintTypes.csv" % PATH)
cmedicalhistory = asm.csv_to_list("%s/tblMedicalHistory.csv" % PATH)
cpersons = asm.csv_to_list("%s/tblKnownPersons.csv" % PATH)
cpersonsaddresses = asm.csv_to_list("%s/tblKnownPersonsAddresses.csv" % PATH)
cpersonsids = asm.csv_to_list("%s/tblKnownPersonsIDs.csv" % PATH)
cpersonsnotes = asm.csv_to_list("%s/tblKnownPersonsNotes.csv" % PATH)
cpersonsphone = asm.csv_to_list("%s/tblKPPhoneNumbers.csv" % PATH)
crabies = asm.csv_to_list("%s/tblRabiesCertificates.csv" % PATH)
cvaccinations = asm.csv_to_list("%s/tblVaccinations.csv" % PATH)

# people
asm.stderr("Process people")
for row in cpersons:
    o = asm.Owner()
    owners.append(o)
    ppo[row["tblKnownPersonsID"]] = o
    o.OwnerForeNames = row["FirstName"]
    o.OwnerSurname = row["LastName"]
    #o.OwnerTitle = asm.fw(row["LetterName"]) # Disabled as this cust did not want
    o.OwnerName = o.OwnerTitle + " " + o.OwnerForeNames + " " + o.OwnerSurname
    o.OwnerName = o.OwnerName.strip()
    o.EmailAddress = row["EmailAddress"]
    o.IsBanned = row["NoAdoptPermanently"] == "-1" and 1 or 0
    o.ExcludeFromBulkEmail = row["DoNotSolicitContact"] == "-1" and 1 or 0

# addresses
asm.stderr("Process addresses")
for row in cpersonsaddresses:
    if ppo.has_key(row["tblKnownPersonsID"]):
        o = ppo[row["tblKnownPersonsID"]]
        o.OwnerAddress = row["StreetNumber"] + " " + row["Street"] + " " + row["Address2"]
        o.OwnerTown = row["City"]
        o.OwnerCounty = row["State"]
        o.OwnerPostcode = row["ZipCode"]
        if row["Latitude"].strip() != "0":
            o.LatLong = row["Latitude"] + "," + row["Longitude"], ","

# phone numbers
asm.stderr("Process phone numbers")
for row in cpersonsphone:
    if ppo.has_key(row["tblKnownPersonsID"]):
        o = ppo[row["tblKnownPersonsID"]]
        if row["Type"] == "Home" or row["Type"] == "Main Number" or row["Type"].strip() == "":
            o.HomeTelephone = row["Telephone"]
        elif row["Type"] == "Work":
            o.WorkTelephone = row["Telephone"]
        elif row["Type"] == "Mobile":
            o.MobileTelephone = row["Telephone"]

# ids
asm.stderr("Process person ID numbers")
for row in cpersonsids:
    # TODO: 1 == Driver's licence - user specific
    if row["sysKnownPersonsIDTypesID"] == "1":
        if ppo.has_key(row["tblKnownPersonsID"]):
            o = ppo[row["tblKnownPersonsID"]]
            asm.additional_field("DriversLicense", 1, o.ID, row["Code"])

# build intakes map
for row in canimalintakes:
    if row["tblAnimalsID"] not in intakes: intakes[row["tblAnimalsID"]] = row

# animals
asm.stderr("Process animals")
for row in canimals:
    if row["PrimaryIDString"] == "": continue
    a = asm.Animal()
    animals.append(a)
    ppa[row["tblAnimalsID"]] = a
    species = asm.find_value(cspecies, "sysSpeciesID", row["sysSpeciesID"], "CommonName")
    a.AnimalTypeID = 2
    a.SpeciesID = asm.species_id_for_name(asm.fw(species))
    a.AnimalName = row["Name"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateBroughtIn = DEFAULT_INTAKE_DATE
    irow = None
    if row["tblAnimalsID"] in intakes: irow = intakes[row["tblAnimalsID"]]
    if irow is not None and asm.getdate_mmddyy(irow["DateReceived"]) is not None:
        a.DateBroughtIn = asm.getdate_mmddyy(irow["DateReceived"])
    a.DateOfBirth = asm.getdate_mmddyy(row["DateOfBirth"])
    if a.DateOfBirth is None: 
        a.DateOfBirth = a.DateBroughtIn
    a.CreatedDate = a.DateBroughtIn
    a.LastChangedDate = a.DateBroughtIn
    a.EntryReasonID = 1
    #a.generateCode(gettypeletter(a.AnimalTypeID))
    code = "MO" + asm.padleft(row["tblAnimalsID"], 6)
    a.ShelterCode = code
    a.ShortCode = code
    a.NeuteredDate = asm.getdate_mmddyy(row["SpayNeuterPerformedDate"])
    if a.NeuteredDate is not None:
        a.Neutered = 1
    # 1 = neutered, 2 = spayed, 3 = entire, 5 = unknown
    if row["sysAlteredChoicesID"] == "1" or row["sysAlteredChoicesID"] == "2":
        a.Neutered = 1
    a.Markings = row["DistinguishingMarks"]
    a.HealthProblems = row["Condition"]
    a.AnimalComments = row["Description"]
    a.Weight = asm.atoi(row["Weight"])
    a.IsNotAvailableForAdoption = 0
    location = asm.find_value(cshelterareas, "sysShelterAreasID", row["sysShelterAreasID"], "ShelterArea")
    pen = asm.find_value(cpens, "sysPensID", row["sysPensID"], "Pen")
    a.ShelterLocation = asm.location_from_db(location, 1)
    a.ShelterLocationUnit = pen
    a.Sex = asm.getsex_mf(asm.find_value(cgenders, "sysGenderChoicesID", row["sysGenderChoicesID"], "GenderChoice"))
    a.Size = 2
    color1 = asm.find_value(ccolors, "sysCoatColorsID", row["ColorPrimaryID"], "Description")
    color2 = asm.find_value(ccolors, "sysCoatColorsID", row["ColorSecondaryID"], "Description")
    a.BaseColourID = asm.colour_id_for_names(asm.fw(color1), asm.fw(color2))
    #a.IdentichipNumber = row["MICROCHIP"]
    breed1 = asm.find_value(cbreeds, "sysBreedsID", row["sysBreedPrimaryID"], "Breed")
    breed2 = asm.find_value(cbreeds, "sysBreedsID", row["sysBreedSecondaryID"], "Breed")
    a.BreedID = asm.breed_id_for_name(breed1)
    a.Breed2ID = asm.breed_id_for_name(breed2)
    # Not sure if this was customer specific with the (Mix) (Purebred) -
    # needs checking on future conversions.
    # It wasn't customer specific - present in last multiops we saw.
    if breed2 == "(Mix)": 
        a.Breed2ID = 442
        a.CrossBreed = 1
        a.BreedName = asm.breed_name(a.BreedID, a.Breed2ID)
    if breed2 == "(Purebred)":
        a.Breed2ID = a.BreedID
        a.CrossBreed = 0
        a.BreedName = asm.breed_name_for_id(a.BreedID)
    status = asm.find_value(canimalstatuses, "sysAnimalStatusChoicesID", row["sysAnimalStatusChoicesID"], "STATUS")
    statusdate = asm.getdate_mmddyy(row["StatusDate"])
    a.ExtraID = statusdate
    a.OnFoster = False
    # Set a new flag of OnFoster = True if the animal is fostered in MO
    # TODO: customer specific
    # sysLocationChoicesID == 5 "Foster Care"
    # sysAnimalStatusChoicesID = 26 "Adoptable"
    # sysAnimalStatusChoicesID = 32 "Shelter"
    # sysShelterAreasID = 11 "Foster"
    if (row["sysLocationChoicesID"] == "5" and (row["sysAnimalStatusChoicesID"] == "26" or row["sysAnimalStatusChoicesID"] == "32")) or row["sysShelterAreasID"] == "11": a.OnFoster = True
    # Oddly, customer reported some death statuses not in disposition
    # TODO: customer specific, 10 == euthanized, 15 = died
    if row["sysAnimalStatusChoicesID"] == "10":
        a.DeceasedDate = a.DateBroughtIn
        a.PutToSleep = 1
        a.PTSReasonID = 2
        a.Archived = 1
    if row["sysAnimalStatusChoicesID"] == "15":
        a.DeceasedDate = a.DateBroughtIn
        a.PutToSleep = 0
        a.PTSReasonID = 2
        a.Archived = 1
    comments = "Original breed: " + breed1 + "/" + breed2
    comments += ", Color: " + color1 + "/" + color2
    comments += ", Status: " + status
    comments += ", Area: " + location + ", Pen: " + pen
    a.HiddenAnimalDetails = comments
    # All animals are non-shelter until we find them in the intake list
    a.NonShelterAnimal = 1
    a.Archived = 1

# Read and store images
asm.stderr("Process images")
for row in canimalimages:
    if not ppa.has_key(row["tblAnimalsID"]): continue
    a = ppa[row["tblAnimalsID"]]
    asm.animal_image(a.ID, asm.load_image_from_file("%s/images/%s" % (PATH, row["ImageFilename"])))

# microchips, animal codes and document ids
asm.stderr("Process animal ID numbers")
for row in canimalids:
    if not ppa.has_key(row["tblAnimalsID"]): continue
    a = ppa[row["tblAnimalsID"]]
    # TODO: These can be customer specific, but appear to be default/fixed 2 == microchip
    if row["sysAnimalIDTypesID"] == "2":
        a.IdentichipNumber = row["Code"]
        a.Identichipped = 1
        a.IdentichipDate = asm.getdate_mmddyy(row["LastUpdate"])
    # 10 = police document id
    if row["sysAnimalIDTypesID"] == "10":
        asm.additional_field("DocumentID", 0, a.ID, row["Code"])
    # 21 = shelter's animal code
    if row["sysAnimalIDTypesID"] == "21" and row["Code"].strip() != "":
        a.ShelterCode = "%s (%s)" % (row["Code"], a.ID)
        a.ShortCode = row["Code"]

# animal intake/disposition list
asm.stderr("Process intakes and dispositions")
for row in canimalintakes:
    disposition = asm.find_value(canimaldispo, "sysAnimalDispositionChoicesID", row["sysAnimalDispositionChoicesID"], "Disposition")
    ddate = asm.getdate_mmddyy(row["DispositionDate"])
    if not ppa.has_key(row["tblAnimalsID"]):
        continue
    a = ppa[row["tblAnimalsID"]]
    # If it's been an intake, it's not non-shelter
    a.NonShelterAnimal = 0
    a.Archived = 0
    a.AnimalTypeID = asm.type_from_db(asm.find_value(canimalrectypes, "sysAnimalReceivedTypesID", row["sysAnimalReceivedTypesID"], "ReceivedType"))
    a.EntryReason = row["SurrenderReasons"] + ". " + row["Location"] + ": " + row["StreetNumber"] + " " + row["Street"] + " " + row["City"] + " " + row["State"] + " " + row["ZipCode"]
    if row["BroughtInByID"] != "":
        if ppo.has_key(row["BroughtInByID"]):
            a.BroughtInByOwnerID = ppo[row["BroughtInByID"]].ID
    if row["SurrenderedByID"] != "":
        if ppo.has_key(row["SurrenderedByID"]):
            a.OriginalOwnerID = ppo[row["SurrenderedByID"]].ID
    if row["ReturnedToOwnerID"] != "":
        if ppo.has_key(row["ReturnedToOwnerID"]):
            o = ppo[row["ReturnedToOwnerID"]]
            m = asm.Movement()
            m.AnimalID = a.ID
            m.OwnerID = o.ID
            m.MovementType = 5
            m.MovementDate = ddate
            a.Archived = 1
            a.ActiveMovementID = m.ID
            a.ActiveMovementDate = m.MovementDate
            a.ActiveMovementType = 5
            movements.append(m)
    if disposition.startswith("Euthanized"):
        a.DeceasedDate = ddate
        a.PutToSleep = 1
        a.PTSReasonID = 2
        a.Archived = 1
    if disposition.startswith("Died"):
        a.DeceasedDate = ddate
        a.PutToSleep = 0
        a.PTSReasonID = 2
        a.Archived = 1
    if disposition == "Stolen":
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = 0
        m.MovementType = 6
        m.MovementDate = ddate
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 6
        movements.append(m)
    if disposition == "Escaped":
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = 0
        m.MovementType = 4
        m.MovementDate = ddate
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 4
        movements.append(m)
    if disposition == "Returned To Nature" or disposition == "TNR":
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = 0
        m.MovementType = 7
        m.MovementDate = ddate
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 7
        movements.append(m)
    if disposition.startswith("Transfer"):
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = to.ID
        m.MovementType = 3
        m.MovementDate = ddate
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 3
        movements.append(m)

# adoption list
asm.stderr("Process adoptions")
for row in cadoptions:
    if not ppa.has_key(row["tblAnimalsID"]) or not ppo.has_key(row["tblKnownPersonsID"]): continue
    a = ppa[row["tblAnimalsID"]]
    o = ppo[row["tblKnownPersonsID"]]
    m = asm.Movement()
    m.AnimalID = a.ID
    m.OwnerID = o.ID
    m.MovementType = 1
    m.MovementDate = a.DateBroughtIn
    if a.ExtraID != "": m.MovementDate = a.ExtraID
    a.Archived = 1
    a.ActiveMovementID = m.ID
    a.ActiveMovementDate = m.MovementDate
    a.ActiveMovementType = 1
    movements.append(m)

# foster list
asm.stderr("Process fosters")
for row in canimalguardians:
    if not ppa.has_key(row["tblAnimalsID"]) or not ppo.has_key(row["tblKnownPersonsID"]): continue
    a = ppa[row["tblAnimalsID"]]
    o = ppo[row["tblKnownPersonsID"]]
    # if we didn't previously flag this animal as fostered, don't bother
    if not a.OnFoster: continue
    # if the animal is dead, also don't bother
    if a.DeceasedDate is not None: continue
    # Make this person a fosterer
    o.IsFosterer = 1
    o.AdditionalFlags = "fosterer|"
    m = asm.Movement()
    m.AnimalID = a.ID
    m.OwnerID = o.ID
    m.MovementType = 2
    fromdate = asm.getdate_mmddyy(row["DateFrom"])
    m.MovementDate = fromdate
    if m.MovementDate is None:
        m.MovementDate = a.DateBroughtIn
    m.ReturnDate = asm.getdate_mmddyy(row["DateTo"])
    a.Archived = 0
    a.ActiveMovementID = m.ID
    a.ActiveMovementDate = m.MovementDate
    a.ActiveMovementType = 2
    movements.append(m)

# vaccinations
asm.stderr("Process vaccinations")
for row in cvaccinations:
    if not ppa.has_key(row["tblAnimalsID"]): continue
    a = ppa[row["tblAnimalsID"]]
    # Each row contains a vaccination
    av = asm.AnimalVaccination()
    animalvaccinations.append(av)
    av.AnimalID = a.ID
    vtype = asm.find_value(cvacctype, "sysVaccinationsID", row["sysVaccinationsID"], "Vaccination")
    av.VaccinationID = 6
    if vtype.startswith("Rhino"): av.VaccinationID = 14
    if vtype.startswith("Rabies"): av.VaccinationID = 4
    if vtype.startswith("Bord"): av.VaccinationID = 6
    if vtype.startswith("Parv"): av.VaccinationID = 7
    av.DateOfVaccination = asm.getdate_mmddyy(row["DateReceived"])
    av.DateRequired = asm.getdate_mmddyy(row["DueDate"])
    if av.DateRequired is None: 
        av.DateRequired = av.DateOfVaccination
        if av.DateRequired is None:
            av.DateRequired = a.DateBroughtIn

# rabies certs
asm.stderr("Process rabies certs")
for row in crabies:
    if not ppa.has_key(row["tblAnimalsID"]): continue
    if asm.getdate_mmddyy(row["RabiesVaccinationDate"]) is None: continue
    a = ppa[row["tblAnimalsID"]]
    # Each row contains a rabies vaccination/cert
    a.RabiesTag = row["RabiesVaccinationCertificateNumber"]
    av = asm.AnimalVaccination()
    animalvaccinations.append(av)
    av.AnimalID = a.ID
    av.VaccinationID = 4
    av.DateOfVaccination = asm.getdate_mmddyy(row["RabiesVaccinationDate"])
    av.DateRequired = av.DateOfVaccination
    av.DateExpires = asm.getdate_mmddyy(row["RabiesVaccinationExpiration"])
    av.Manufacturer = "%s %s" % (row["RabiesVaccinationManufacturer"], row["RabiesVaccinationBrand"])
    av.BatchNumber = "%s %s" % (row["RabiesVaccinationLotNumber"], asm.fw(row["RabiesVaccinationLotExpiration"]))

# medical history
asm.stderr("Process medical history")
for row in cmedicalhistory:
    if not ppa.has_key(row["tblAnimalsID"]): continue
    a = ppa[row["tblAnimalsID"]]
    if row["Issue"] == "Spay" or row["Issue"] == "Neuter":
        a.Neutered = 1
        a.NeuteredDate = asm.getdate_mmddyy(row["DateOfService"])
    else:
        tname = row["Issue"]
        if tname == "": tname = row["Note"]
        sdate = asm.getdate_mmddyy(row["DateOfService"])
        if sdate is None: sdate = a.DateBroughtIn
        animalmedicals.append(asm.animal_regimen_single(a.ID, sdate, tname, "", row["Note"]))

# animal notes
asm.stderr("Process animal notes")
for row in canimalsnotes:
    if not ppa.has_key(row["tblAnimalsID"]): continue
    a = ppa[row["tblAnimalsID"]]
    l = asm.Log()
    logs.append(l)
    l.LogTypeID = 3
    l.LinkID = a.ID
    l.LinkType = 0
    l.Date = asm.getdate_mmddyy(row["NoteDate"])
    if l.Date is None:
        l.Date = asm.now()
    l.Comments = row["Note"]

# person notes
asm.stderr("Process person notes")
for row in cpersonsnotes:
    if not ppo.has_key(row["tblKnownPersonsID"]): continue
    a = ppo[row["tblKnownPersonsID"]]
    l = asm.Log()
    logs.append(l)
    l.LogTypeID = 3
    l.LinkID = a.ID
    l.LinkType = 1
    l.Date = asm.now()
    l.Comments = row["Note"]

asm.stderr("Process complaints")
for row in ccomplaints:
    ac = asm.AnimalControl()
    ppac[row["tblComplaintsID"]] = ac 
    animalcontrol.append(ac)
    ac.CallDateTime = asm.getdate_mmddyy(row["ReceivedDate"])
    if ac.CallDateTime is None:
        ac.CallDateTime = asm.parse_date("2015-01-01", "%Y-%m-%d")
    ac.IncidentDateTime = ac.CallDateTime
    incidentname = asm.find_value(ccomplainttypes, "sysComplaintTypesID", row["sysComplaintTypesID"], "ComplaintType")
    ac.IncidentTypeID = asm.incidenttype_from_db(incidentname)
    ac.DispatchDateTime = ac.CallDateTime
    ac.CompletedDate = asm.getdate_mmddyy(row["StatusDate"])
    if ac.CompletedDate is None:
        ac.CompletedDate = ac.CallDateTime
    ac.DispatchAddress = row["StreetNumber"] + " " + row["Street"]
    ac.DispatchTown = row["City"]
    ac.DispatchCounty = row["State"]
    ac.DispatchPostcode = row["ZipCode"]
    comments = ""
    if row["Location"].strip() != "": comments += "Location: %s" % row["Location"]
    comments += "\nMO ID: %s" % row["tblComplaintsID"]
    ac.CallNotes = comments

asm.stderr("Process animals linked to complaints")
for row in ccomplaintsanimals:
    if not ppac.has_key(row["tblComplaintsID"]): continue
    ac = ppac[row["tblComplaintsID"]]
    if not ppa.has_key(row["tblAnimalsID"]): continue
    a = ppa[row["tblAnimalsID"]]
    animalcontrolanimals.append("DELETE FROM animalcontrolanimal WHERE AnimalControlID = %s AND AnimalID = %s;" % (ac.ID, a.ID))
    animalcontrolanimals.append("INSERT INTO animalcontrolanimal (AnimalControlID, AnimalID) VALUES (%s, %s);" % (ac.ID, a.ID))

asm.stderr("Process people linked to complaints")
for row in ccomplaintspeople:
    if not ppo.has_key(row["tblKnownPersonsID"]): continue
    o = ppo[row["tblKnownPersonsID"]]
    if not ppac.has_key(row["tblComplaintsID"]): continue
    ac = ppac[row["tblComplaintsID"]]
    if row["CalledInFromTelephoneNumber"].strip() != "": ac.CallNotes += "\nNumber: %s" % row["CalledInFromTelephoneNumber"]
    if row["Note"].strip() != "": ac.CallNotes += "\n" + row["Note"]
    itype = row["sysComplaintsInvolvementTypesID"]
    if itype == "1": ac.CallerID = o.ID # Complainant
    elif itype == "2" or itype == "5": ac.OwnerID = o.ID # Animal Owner or Suspect
    elif itype == "4": ac.VictimID = o.ID # Victim

asm.stderr("Process complaint notes")
for row in ccomplaintsnotes:
    if not ppac.has_key(row["tblComplaintsID"]): continue
    a = ppac[row["tblComplaintsID"]]
    l = asm.Log()
    logs.append(l)
    l.LogTypeID = 3
    l.LinkID = a.ID
    l.LinkType = 6
    l.Date = asm.getdate_mmddyy(row["LastUpdate"])
    if l.Date is None: l.Date = asm.now()
    l.Comments = row["Note"]

# Take remaining animals off shelter if they've been on longer than ADOPT_LONGER_THAN_DAYS
asm.adopt_older_than(animals, movements, ownerid=uo.ID, days=ADOPT_LONGER_THAN_DAYS)

# Now that everything else is done, output stored records
for a in animals:
    print a
for am in animalmedicals:
    print am
for av in animalvaccinations:
    print av
for l in logs:
    print l
for o in owners:
    print o
for m in movements:
    print m
for ol in ownerlicences:
    print ol
for ac in animalcontrol:
    print ac
for ac in animalcontrolanimals:
    print ac

#asm.stderr_allanimals(animals)
#asm.stderr_onshelter(animals)
asm.stderr_summary(animals=animals, animalmedicals=animalmedicals, animalvaccinations=animalvaccinations, logs=logs, owners=owners, movements=movements, ownerlicences=ownerlicences, animalcontrol=animalcontrol)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

