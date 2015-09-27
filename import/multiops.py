#!/usr/bin/python

import asm

"""
Import script for Multiple Options SQL Server databases exported to MDB and then CSV

7th September, 2015
"""

PATH = "data/multiops_zg0861"

owners = []
ownerlicences = []
logs = []
movements = []
animals = []
animalcontrol = []
animalcontrolanimals = []
animalvaccinations = []

ppa = {}
ppo = {}
ppac = {}
addresses = {}
addrlink = {}

asm.setid("animal", 50000)
asm.setid("animalcontrol", 50000)
asm.setid("animalmedical", 50000)
asm.setid("animalmedicaltreatment", 50000)
asm.setid("animalvaccination", 50000)
asm.setid("log", 50000)
asm.setid("owner", 50000)
asm.setid("ownerlicence", 50000)
asm.setid("adoption", 50000)
asm.setid("media", 50000)
asm.setid("dbfs", 50000)

# Remove existing
print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM additional WHERE LinkID >= 50000;"
print "DELETE FROM animal WHERE ID >= 50000;"
print "DELETE FROM animalcontrol WHERE ID >= 50000;"
print "DELETE FROM animalmedical WHERE ID >= 50000;"
print "DELETE FROM animalmedicaltreatment WHERE ID >= 50000;"
print "DELETE FROM animalvaccination WHERE ID >= 50000;"
print "DELETE FROM log WHERE ID >= 50000;"
print "DELETE FROM owner WHERE ID >= 50000;"
print "DELETE FROM ownerlicence WHERE ID >= 50000;"
print "DELETE FROM adoption WHERE ID >= 50000;"
print "DELETE FROM media WHERE ID >= 50000;"
print "DELETE FROM dbfs WHERE ID >= 50000;"

# Create a transfer owner
to = asm.Owner()
owners.append(to)
to.OwnerSurname = "Other Shelter"
to.OwnerName = to.OwnerSurname

# Load up data files
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
canimalimages = asm.csv_to_list("%s/tblAnimalImages.csv" % PATH)
canimalintakes = asm.csv_to_list("%s/tblAnimalIntakesDispositions.csv" % PATH)
canimalsnotes = asm.csv_to_list("%s/tblAnimalsNotes.csv" % PATH)
ccomplaints = asm.csv_to_list("%s/tblComplaints.csv" % PATH)
ccomplaintsanimals = asm.csv_to_list("%s/tblComplaintsAnimals.csv" % PATH)
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
for row in cpersonsids:
    # TODO: 1 == Driver's licence - user specific
    if row["sysKnownPersonsIDTypesID"] == "1":
        if ppo.has_key(row["tblKnownPersonsID"]):
            o = ppo[row["tblKnownPersonsID"]]
            asm.additional_field("DriversLicense", 1, o.ID, row["Code"])

# animals
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
    a.DateOfBirth = asm.getdate_mmddyy(row["DateOfBirth"])
    if a.DateOfBirth is None: a.DateOfBirth = asm.now()
    a.DateBroughtIn = asm.now()
    irow = asm.find_row(canimalintakes, "tblAnimalsID", row["tblAnimalsID"])
    if irow is not None:
        a.DateBroughtIn = asm.getdate_mmddyy(irow["DateReceived"])
    if a.DateBroughtIn is None:
        a.DateBroughtIn = asm.now()
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
    # needs checking on future conversions
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

# Read and store images
for row in canimalimages:
    if not ppa.has_key(row["tblAnimalsID"]): continue
    a = ppa[row["tblAnimalsID"]]
    asm.animal_image(a.ID, asm.load_image_from_file("%s/images/%s" % (PATH, row["ImageFilename"])))

# microchips, animal codes and document ids
for row in canimalids:
    if not ppa.has_key(row["tblAnimalsID"]): continue
    a = ppa[row["tblAnimalsID"]]
    # TODO: These are customer specific. 2 == microchip
    if row["sysAnimalIDTypesID"] == "2":
        a.IdentichipNumber = row["Code"]
        a.Identichipped = 1
        a.IdentichipDate = asm.getdate_mmddyy(row["LastUpdate"])
    # 10 = police document id
    if row["sysAnimalIDTypesID"] == "10":
        asm.additional_field("DocumentID", 0, a.ID, row["Code"])
    # 21 = jcas animal code
    if row["sysAnimalIDTypesID"] == "21" and row["Code"].strip() != "":
        a.ShelterCode = "JCAS%s (%s)" % (row["Code"], a.ID)
        a.ShortCode = row["Code"]

# animal intake/disposition list
for row in canimalintakes:
    disposition = asm.find_value(canimaldispo, "sysAnimalDispositionChoicesID", row["sysAnimalDispositionChoicesID"], "Disposition")
    ddate = asm.getdate_mmddyy(row["DispositionDate"])
    if not ppa.has_key(row["tblAnimalsID"]):
        continue
    a = ppa[row["tblAnimalsID"]]
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
        asm.animal_regimen_single(a.ID, sdate, tname, "", row["Note"])

# animal notes
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
    ac.DispatchAddress = row["StreetNumber"] + " " + row["Street"]
    ac.DispatchTown = row["City"]
    ac.DispatchCounty = row["State"]
    ac.DispatchPostcode = row["ZipCode"]
    comments = ""
    if row["Location"].strip() != "": comments += "Location: %s" % row["Location"]
    comments += "\nMO ID: %s" % row["tblComplaintsID"]
    ac.CallNotes = comments

for row in ccomplaintsanimals:
    if not ppac.has_key(row["tblComplaintsID"]): continue
    ac = ppac[row["tblComplaintsID"]]
    if not ppa.has_key(row["tblAnimalsID"]): continue
    a = ppa[row["tblAnimalsID"]]
    animalcontrolanimals.append("DELETE FROM animalcontrolanimal WHERE AnimalControlID = %s AND AnimalID = %s;" % (ac.ID, a.ID))
    animalcontrolanimals.append("INSERT INTO animalcontrolanimal (AnimalControlID, AnimalID) VALUES (%s, %s);" % (ac.ID, a.ID))

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

# Now that everything else is done, output stored records
for a in animals:
    print a
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

# Move all animals without a matching location off shelter
print "UPDATE animal SET Archived = 1 WHERE Archived = 0 AND ActiveMovementID = 0 AND ShelterLocation = 1;"
print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

