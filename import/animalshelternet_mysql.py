#!/usr/bin/python

import asm, datetime, sys, os, web

"""
Import script for AnimalShelterNet databases in MYSQL form.

Does people, animals, intakes and dispositions.

Currently does not do medical or payments because the last conversion
we did with a MySQL ASN database did not have data in any of those tables.

13th September 2017
"""

db = web.database( dbn = "mysql", db = "sherwood", user = "root", pw = "root" )

START_ID = 100
FIX_FIELD_LENGTHS = False
REPAIR_TABLES = False

if FIX_FIELD_LENGTHS:
    db.query("ALTER TABLE animals " \
        "MODIFY Name VARCHAR(255), " \
        "MODIFY MicrochipID VARCHAR(255), " \
        "MODIFY RabiesNum VARCHAR(255)")

if REPAIR_TABLES:
    for t in ( "ac_animal", "ac_subject", "ac_rpt_bite", "ac_rpt_complaint", "ac_rpt_misc", "animals", "people", "intake", "disposit", "license", "medetail" ):
        db.query("REPAIR TABLE %s" % t)

def gettypeletter(aid):
    tmap = {
        2: "D",
        10: "A",
        11: "U",
        12: "S",
        40: "N"
    }
    return tmap[aid]

def ynu(s):
    if s == "Y": return 0
    if s == "N": return 1
    if s == "U": return 2

owners = []
ownerlicences = []
movements = []
animals = []
animalvaccinations = []
animalcontrol = []
animalcontrolanimals = []

ppa = {}
ppo = {}

asm.setid("adoption", START_ID)
asm.setid("animal", START_ID)
asm.setid("owner", START_ID)
asm.setid("ownerlicence", START_ID)
asm.setid("animalcontrol", START_ID)
asm.setid("animalvaccination", START_ID)

# Remove existing
print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM adoption WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM animal WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM animalcontrol WHERE ID >= %d AND LastChangedBy = 'conversion';" % START_ID
print "DELETE FROM animalcontrolanimal WHERE AnimalID IN " \
    "(SELECT ID FROM animalcontrol WHERE ID >= %d AND LastChangedBy = 'conversion');" % START_ID
print "DELETE FROM owner WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM ownerlicence WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM animalvaccination WHERE ID >= %d AND CreatedBy = 'conversion';" % START_ID

# Create a transfer owner
to = asm.Owner()
owners.append(to)
to.OwnerSurname = "Other Shelter"
to.OwnerName = to.OwnerSurname

# Create an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname

# People
for row in db.select("people"):
    o = asm.Owner()
    owners.append(o)
    ppo[str(row.CustUid)] = o
    o.OwnerTitle = row.Title
    o.OwnerSurname = row.LastName
    if o.OwnerSurname is None or o.OwnerSurname == "": 
        o.OwnerSurname = row.OrgName
        o.OwnerType = 2
    if o.OwnerSurname is None: o.OwnerSurname = "Unknown"
    o.OwnerForeNames = row.FirstName
    o.OwnerAddress = "%s %s" % (row.Addr1, row.Addr2)
    o.OwnerTown = row.City
    o.OwnerCounty = row.State
    o.OwnerPostcode = row.Zip
    o.HomeTelephone = row.Phone1
    o.WorkTelephone = row.Phone2
    o.MobileTelephone = row.Phone3
    o.Comments = asm.strip(row.Comments)
    o.IsACO = asm.iif(row.ACOFlag == "Y", 1, 0)
    o.IsShelter = asm.iif(row.RescueFlag == "Y", 1, 0)
    o.IsFosterer = asm.iif(row.FosterFlag == "Y", 1, 0)
    o.IsMember = asm.iif(row.MailingList == "Y", 1, 0)
    o.EmailAddress = row.Email

# Animals/intake
for row in db.query("select animals.*, intake.Comments as IntakeComments, intake.CustUid as IntakeCustUid, " \
    "IntakeDTL1, IntakeDTL2, intake.ReasonCode " \
    #"coalesce((select descr from lookup where value = intake.ReasonCode limit 1), '') AS IntakeReason, " \
    #"coalesce((select descr from lookup where value = animals.Color limit 1), '') AS ColorName " \
    "from animals " \
    "left outer join intake on intake.RefUID = animals.IntakeRefUID " \
    "order by IntakeDTL1").list():

    if str(row.AnimalUid) in ppa:
        a = ppa[str(row.AnimalUid)]
    else:
        a = asm.Animal()
        animals.append(a)
        ppa[str(row.AnimalUid)] = a
    ecode = row.ReasonCode
    if ecode is None: ecode = "" 
    a.SpeciesID = asm.species_id_for_name(row.Species)
    if a.SpeciesID == 1 and ecode == "STR":
        a.AnimalTypeID = 10
    elif a.SpeciesID == 1:
        a.AnimalTypeID = 2
    elif a.SpeciesID == 2 and ecode == "STR":
        a.AnimalTypeID = 12
    else:
        a.AnimalTypeID = 11
    a.ReasonForEntry = "%s. %s" % (ecode, row.IntakeComments)
    a.EntryReasonID = 7 # Stray
    a.EntryTypeID = 2
    if ecode.startswith("O"): 
        a.EntryReasonID = 17 # Owner
        a.EntryTypeID = 1
    asm.breed_ids(a, row.Breed1, row.Breed2)
    a.BaseColourID = asm.colour_id_for_name(row.Color, firstWordOnly=True)
    a.Sex = asm.getsex_mf(row.Sex)
    a.generateCode(gettypeletter(a.AnimalTypeID))
    a.ShortCode = row.AnimalUid
    a.AnimalName = row.Name
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.RabiesTag = row.RabiesNum
    a.ShelterLocationUnit = row.CageLocation
    a.Markings = row.Marking
    a.GoodWithCats = ynu(row.GoodWithCats)
    a.GoodWithDogs = ynu(row.GoodWithDogs)
    a.GoodWithChildren = ynu(row.GoodWithChildren)
    a.HouseTrained = ynu(row.HouseBroken)
    a.AnimalComments = row.Comments
    a.HiddenAnimalDetails = "Original breed: %s / %s, color: %s" % (row.Breed1, row.Breed2, row.Color)
    a.IdentichipNumber = asm.nulltostr(row.MicrochipID)
    if a.IdentichipNumber != "": a.Identichipped = 1
    a.TattooNumber = asm.nulltostr(row.tattoo)
    if a.TattooNumber != "": a.Tattoo = 1
    if row.Size == "X": a.Size = 0
    if row.Size == "L": a.Size = 1
    if row.Size == "M": a.Size = 2
    if row.Size == "S": a.Size = 3
    if row.AlteredAtIntake == "Y": 
        a.Neutered = 1
    a.NeuteredDate = row.AlteredDate
    if a.NeuteredDate is not None:
        a.Neutered = 1
    if row.Declawed == "Y": a.Declawed = 1
    if str(row.IntakeCustUid) in ppo:
        a.OriginalOwnerID = ppo[str(row.IntakeCustUid)].ID
        a.BroughtInByOwnerID = a.OriginalOwnerID
    a.DateOfBirth = row.Birthdate
    a.DateBroughtIn = row.IntakeDTL1
    if a.DateBroughtIn is None:
        # Treat no intake record as a non-shelter animal
        a.DateBroughtIn = row.tsAdded
        a.NonShelterAnimal = 1
        a.Archived = 1
        a.AnimalTypeID = 40
        if str(row.CurrentOwner) in ppo: 
            a.OriginalOwnerID = ppo[str(row.CurrentOwner)].ID
            a.OwnerID = a.OriginalOwnerID
    if a.DateOfBirth is None:
        a.DateOfBirth = a.DateBroughtIn or row.tsAdded
    a.LastChangedDate = a.DateBroughtIn
    a.CreatedDate = a.DateBroughtIn

# Dispositions/animals
for row in db.query("select * from disposit").list():
    a = None
    if str(row.AnimalUid) in ppa:
        a = ppa[str(row.AnimalUid)]
    if a is None: continue

    if row.TransType == "EU": # Euthanasia
        a.DeceasedDate = row.DispositDTL1
        a.PutToSleep = 1
        a.PTSReason = row.Comments
        a.Archived = 1
        a.NonShelterAnimal = 0

    if row.TransType == "DO": # DOA
        a.DeceasedDate = row.DispositDTL1
        a.PutToSleep = 0
        a.IsDOA = 1
        a.PTSReason = row.Comments
        a.Archived = 1
        a.NonShelterAnimal = 0

    if row.TransType == "AD" and str(row.CustUid) in ppo: # Adoption
        o = ppo[row.CustUid]
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = row.DispositDTL1
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 1
        a.NonShelterAnimal = 0
        movements.append(m)

    if row.TransType in ("BR", "CR") and str(row.CustUid) in ppo: # Reclaim
        o = ppo[row.CustUid]
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 5
        m.MovementDate = row.DispositDTL1
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 5
        a.NonShelterAnimal = 0
        movements.append(m)

    if row.TransType == "FO" and str(row.CustUid) in ppo: # Released to wild
        m = asm.Movement()
        m.AnimalID = a.ID
        m.MovementType = 7
        m.MovementDate = row.DispositDTL1
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 7
        a.NonShelterAnimal = 0
        movements.append(m)

# This table records changes in status. In some cases, it's the only way to find
# things like adoptions or historic licenses
for row in db.query("select * from hold").list():
    a = None
    if str(row.AnimalUid) in ppa:
        a = ppa[str(row.AnimalUid)]
    o = None
    if str(row.CustUid) in ppo:
        o = ppo[str(row.CustUid)]
    if a is None or o is None:
        asm.stderr("No animal/person combo: %s, %s" % (row.AnimalUid, row.CustUid))
        continue

    if row.EndStatus == "35": # License purchase, 149 is license expiry
        l = asm.OwnerLicence()
        ownerlicences.append(l)
        l.AnimalID = a.ID
        l.OwnerID = o.ID
        l.LicenceType = 1
        l.LicenceNumber = "H%s" % row.HoldUid
        l.IssueDate = row.Startts
        l.ExpiryDate = row.Endts

    elif row.EndStatus == "00" and True == False: # Routing status for adoption? Disabled for now
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = row.Startts
        a.Archived = 1
        a.ActiveMovementID = m.ID
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementType = 1
        a.NonShelterAnimal = 0
        movements.append(m)


"""
# Medical - this info MAY be supplied by the medetail table, but it was blank
# in the MySQL database we converted this time.

for row in cmed:
    auid = row["ANIMAL NUMBER"]
    if auid.find("&") != -1: auid = auid[0:auid.find("&")]
    if not auid in ppa: continue
    a = ppa[auid]
    date = asm.getdate_mmddyy(row["DATE USED"])
    # Each row contains a vaccination or test
    if row["MED"].startswith("HW Test"):
        a.HeartwormTested = 1
        a.HeartwormTestDate = date
        a.HeartwormTestResult = row["NOTES"].find("gative") != -1 and 1 or 2
    elif row["MED"].startswith("Combo"):
        a.CombiTested = 1
        a.CombiTestDate = date
        a.CombiTestResult = row["NOTES"].find("gative") != -1 and 1 or 2
    else:
        av = asm.AnimalVaccination()
        animalvaccinations.append(av)
        av.DateRequired = date
        av.DateOfVaccination = date
        av.VaccinationID = 6
        if row["MED"].startswith("FelV"): av.VaccinationID = 12
        if row["MED"].startswith("FVRCP"): av.VaccinationID = 9
        if row["MED"].startswith("DA2PP"): av.VaccinationID = 8
        if row["MED"].startswith("Bord"): av.VaccinationID = 6
        if row["MED"].startswith("Rabies"): av.VaccinationID = 4
        if row["MED"].startswith("Lepto"): av.VaccinationID = 3
        av.Comments = "%s %s" % (row["MED"], row["NOTES"])
"""

# Licences
for row in db.select("license"):
    if str(row.OwnerUid) in ppo:
        o = ppo[str(row.OwnerUid)]
    else:
        o = asm.Owner()
        owners.append(o)
        ppo[str(row.OwnerUid)] = o
        o.OwnerForeNames = row.FirstName
        o.OwnerSurname = row.LastName
        if o.OwnerSurname is None or o.OwnerSurname == "": o.OwnerSurname = "Unknown"
        o.OwnerAddress = row.OwnerAddr1 + " " + row.OwnerAddr2
        o.OwnerTown = row.OwnerCity
        o.OwnerCounty = row.OwnerState
        o.OwnerPostcode = row.OwnerZip
        o.HomeTelephone = row.OwnerPhone1
        o.WorkTelephone = row.OwnerPhone2
        o.EmailAddress = row.OwnerEmail
    if str(row.AnimalUid) in ppa:
        a = ppa[str(row.AnimalUid)]
    else:
        a = None
        if row.AnimalName != "" and row.breed1 != "":
            a = asm.Animal()
            animals.append(a)
            ppa[str(row.AnimalUid)] = a
            a.SpeciesID = asm.species_id_for_name(row.species)
            a.AnimalTypeID = 40
            asm.breed_ids(a, row.breed1, row.breed2)
            a.BaseColourID = asm.colour_id_for_name(row.color, firstWordOnly=True)
            a.Sex = asm.getsex_mf(row.sex)
            a.generateCode(gettypeletter(a.AnimalTypeID))
            a.ShortCode = row.AnimalUid
            a.AnimalName = row.AnimalName
            if a.AnimalName.strip() == "":
                a.AnimalName = "(unknown)"
            a.HiddenAnimalDetails = "Original breed: %s / %s, color: %s" % (row.breed1, row.breed2, row.color)
            #a.IdentichipNumber = asm.nulltostr(row.MicrochipID)
            #if a.IdentichipNumber != "": a.Identichipped = 1
            a.DateOfBirth = row.DOB
            a.DateBroughtIn = row.LicIssuedts
            a.NonShelterAnimal = 1
            a.Archived = 1
            a.LastChangedDate = a.DateBroughtIn
            a.CreatedDate = a.DateBroughtIn
    if o is not None:
        l = asm.OwnerLicence()
        ownerlicences.append(l)
        if a is not None: l.AnimalID = a.ID
        l.OwnerID = o.ID
        l.LicenceType = 1
        l.LicenceNumber = row.LicenseNum
        if row.LicCost is not None: l.LicenceFee = int(row.LicCost * 100)
        l.IssueDate = row.LicIssuedts
        l.ExpiryDate = row.LicExpirets
        comments = "Type: %s, group: %s, cert: %s, jurisdiction: %s" % \
            (row.LicenseType, row.ItemGroup, row.CertNum, row.Jurisdiction)
        l.Comments = comments

def process_animals(reportuid, ac):
    """ Handle animals linked to an ac record """
    for row in db.query("select * from ac_animal where reportuid = %s" % reportuid):
        if row.AnimalUid in ppa:
            a = ppa[row.AnimalUid]
            animalcontrolanimals.append("INSERT INTO animalcontrolanimal (AnimalControlID, AnimalID) VALUES (%s, %s);" % (ac.ID, a.ID))
            a.NonShelterAnimal = 1 # has to be NS for incident
            a.Archived = 1
            if a.IdentichipNumber == "" and (row.MicrochipID is not None and row.MicrochipID != ""):
                a.IdentichipNumber = row.MicrochipID
                a.Identichipped = 1

def process_subjects(reportuid, ac):
    """ Handle people linked to an ac record
        VIC = victim, WIT = witness, OWN / SUS = suspect, ACO """
    for row in db.query("select * from ac_subject where reportuid = %s" % reportuid):
        ck = "sub%s" % row.subjectuid
        if ck in ppo:
            o = ppo[ck]
        else:
            o = asm.Owner()
            owners.append(o)
            ppo[ck] = o
            o.OwnerForeNames = row.subjFirstName
            o.OwnerSurname = row.subjLastName
            if o.OwnerSurname is None or o.OwnerSurname == "": o.OwnerSurname = "Unknown"
            o.OwnerAddress = row.subjaddr1 + " " + row.subjaddr2
            o.OwnerTown = row.subjcity
            o.OwnerCounty = row.subjstate
            o.OwnerPostcode = row.subjzipcode
            o.HomeTelephone = row.subjphone1
            o.WorkTelephone = row.subjphone2
            o.MobileTelephone = row.subjphone3
            o.Comments = asm.strip("%s %s %s" % (row.physdescr, row.notes, row.statement))
        st = str(row.subject_type)
        if st.find("VIC") != -1:
            ac.VictimID = o.ID
        if st.find("WIT") != -1 or st.find("ACO") != -1:
            ac.CallerID = o.ID
        if st.find("OWN") != -1 or st.find("SUS") != -1:
            if ac.OwnerID == 0:
                ac.OwnerID = o.ID
            elif ac.Owner2ID == 0:
                ac.Owner2ID = o.ID
            elif ac.Owner3ID == 0:
                ac.Owner3ID = o.ID

# Animal control records
for row in db.select("ac_rpt_bite"):
    ac = asm.AnimalControl()
    animalcontrol.append(ac)
    ac.CallDateTime = row.ts_create
    ac.CreatedDate = row.ts_create
    ac.CreatedBy = row.user_create
    ac.IncidentDateTime = ac.CallDateTime
    ac.IncidentTypeID = 5 # Bite
    ac.DispatchDateTime = ac.CallDateTime
    ac.CompletedDate = row.ts_closed
    ac.IncidentCompletedID = 0
    ac.FollowupDateTime = row.ts_followup
    if ac.CompletedDate is None:
        ac.CompletedDate = ac.CallDateTime
    ac.DispatchedACO = row.user_followup
    ac.DispatchAddress = "%s %s" % (row.Addr1, row.Addr2)
    ac.DispatchTown = row.City
    ac.DispatchCounty = row.State
    ac.DispatchPostcode = row.Zip
    c = "\n%s %s, " % (asm.strip(row.reportnum), asm.strip(row.reporttype))
    c += "\nStatus: %s, " % asm.strip(row.status)
    c += "\nInjury: %s %s, " % (asm.strip(row.injury_desc), asm.strip(row.injury_loc))
    c += "\n%s %s" % (asm.strip(row.report_desc), asm.strip(row.remarks))
    ac.CallNotes = c
    process_animals(row.reportuid, ac)
    process_subjects(row.reportuid, ac)

for row in db.select("ac_rpt_complaint"):
    ac = asm.AnimalControl()
    animalcontrol.append(ac)
    ac.CallDateTime = row.ts_call_received
    ac.CreatedDate = row.ts_create
    ac.CreatedBy = row.user_create
    ac.IncidentDateTime = ac.CallDateTime
    ac.IncidentTypeID = 3 
    ac.DispatchDateTime = ac.CallDateTime
    ac.CompletedDate = row.ts_closed
    ac.IncidentCompletedID = 0
    ac.FollowupDateTime = row.ts_followup
    if ac.CompletedDate is None:
        ac.CompletedDate = ac.CallDateTime
    ac.DispatchedACO = row.user_followup
    ac.DispatchAddress = "%s %s" % (row.Addr1, row.Addr2)
    ac.DispatchTown = row.City
    ac.DispatchCounty = row.State
    ac.DispatchPostcode = row.Zip
    c = "\n%s %s, " % (asm.strip(row.reportnum), asm.strip(row.complainttype))
    c += "\nStatus: %s, " % asm.strip(row.status)
    c += "\nLocation: %s, " % asm.strip(row.location)
    c += "\nOccurred: %s, " % asm.strip(row.occured)
    c += "\nOutcome: %s %s, " % (asm.strip(row.outcome), asm.strip(row.outcome_notes))
    c += "\n%s %s" % (asm.strip(row.report_desc), asm.strip(row.Notes))
    ac.CallNotes = c
    process_animals(row.reportuid, ac)
    process_subjects(row.reportuid, ac)

for row in db.select("ac_rpt_misc"):
    ac = asm.AnimalControl()
    animalcontrol.append(ac)
    ac.CallDateTime = row.ts_create
    ac.CreatedDate = row.ts_create
    ac.CreatedBy = row.user_create
    ac.IncidentDateTime = row.ts_incident
    if ac.IncidentDateTime is None: ac.IncidentDateTime = ac.CallDateTime
    ac.IncidentTypeID = 3 
    ac.DispatchDateTime = ac.CallDateTime
    ac.CompletedDate = row.ts_closed
    ac.IncidentCompletedID = 0
    ac.FollowupDateTime = row.ts_followup
    if ac.CompletedDate is None:
        ac.CompletedDate = ac.CallDateTime
    ac.DispatchedACO = row.user_followup
    ac.DispatchAddress = "%s %s" % (row.Addr1, row.Addr2)
    ac.DispatchTown = row.City
    ac.DispatchCounty = row.State
    ac.DispatchPostcode = row.Zip
    c = "\n%s %s, " % (asm.strip(row.reportnum), asm.strip(row.reporttype))
    c += "\nStatus: %s, " % asm.strip(row.status)
    c += "\nLocation: %s, " % asm.strip(row.location)
    c += "\nViolation code: %s, " % asm.strip(row.violation_code)
    c += "\nOutcome: %s %s, " % (asm.strip(row.outcome), asm.strip(row.outcome_notes))
    c += "\n%s %s" % (asm.strip(row.report_desc), asm.strip(row.comments))
    ac.CallNotes = c
    process_animals(row.reportuid, ac)
    process_subjects(row.reportuid, ac)

# Run back through the animals, if we have any that are still
# on shelter after 1 year, add an adoption to an unknown owner
#asm.adopt_older_than(animals, movements, uo.ID, 365)

# This last customer did not want any leftover animals on file -
# get rid of every remaining animal
asm.adopt_older_than(animals, movements, uo.ID, 0)

# Now that everything else is done, output stored records
for k,v in asm.locations.iteritems():
    print v
for a in animals:
    print a
for av in animalvaccinations:
    print av
for o in owners:
    print o
for l in ownerlicences:
    print l
for m in movements:
    print m
for ac in animalcontrol:
    print ac
for aca in animalcontrolanimals:
    print aca

#asm.stderr_allanimals(animals)
#asm.stderr_onshelter(animals)
asm.stderr_summary(animals=animals, animalvaccinations=animalvaccinations, owners=owners, ownerlicences=ownerlicences, movements=movements, animalcontrol=animalcontrol)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

