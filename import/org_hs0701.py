#!/usr/bin/python

import asm, datetime

def findin(d, k, v, k2):
    """
    Finds the value for k2 in list d where k = v
    """
    for a in d:
        if a[k] == v:
            return a[k2]
    return ""

canimal = asm.csv_to_list("data/hs0701_ac/Animal.xlsx.csv")
cacat = asm.csv_to_list("data/hs0701_ac/aCat.xlsx.csv")
cadog = asm.csv_to_list("data/hs0701_ac/aDog.xlsx.csv")
caother = asm.csv_to_list("data/hs0701_ac/aOther.xlsx.csv")
canimalnote = asm.csv_to_list("data/hs0701_ac/Animal_Note.xlsx.csv")
ccustomeranimallink = asm.csv_to_list("data/hs0701_ac/CustomerAnimalLink.xlsx.csv")
ccustomer = asm.csv_to_list("data/hs0701_ac/Customer.xlsx.csv")
ccustomernote = asm.csv_to_list("data/hs0701_ac/Customer_Note.xlsx.csv")
cdisposition = asm.csv_to_list("data/hs0701_ac/Disposition.xlsx.csv")
cintake = asm.csv_to_list("data/hs0701_ac/Intake.xlsx.csv")
cmicrochip = asm.csv_to_list("data/hs0701_ac/Microchip.xlsx.csv")
cnote = asm.csv_to_list("data/hs0701_ac/Note.xlsx.csv")

cadoptions = asm.csv_to_list("data/hs0701_ac/dAdoption.xlsx.csv")
cdied = asm.csv_to_list("data/hs0701_ac/dDiedInCare.xlsx.csv")
ceuth = asm.csv_to_list("data/hs0701_ac/dEuthanization.xlsx.csv")
credemption = asm.csv_to_list("data/hs0701_ac/dRedemption.xlsx.csv")
ctransfer = asm.csv_to_list("data/hs0701_ac/dTransfer.xlsx.csv")

clucat = asm.csv_to_list("data/hs0701_ac/LU_FelineBreed.xlsx.csv")
cludog = asm.csv_to_list("data/hs0701_ac/LU_CanineBreed.xlsx.csv")
cluother = asm.csv_to_list("data/hs0701_ac/LU_OtherType.xlsx.csv")

ccall = asm.csv_to_list("data/hs0701_ac/Call.xlsx.csv")
ccallnote = asm.csv_to_list("data/hs0701_ac/Call_Note.xlsx.csv")
coriginalcall = asm.csv_to_list("data/hs0701_ac/cOriginalCall.xlsx.csv")
clic = asm.csv_to_list("data/hs0701_ac/RabVacCitLic.xlsx.csv")

cusers = asm.csv_to_list("data/hs0701_ac/ShelterUser.xlsx.csv")

asm.setid("adoption", 1000)
asm.setid("animal", 10000)
asm.setid("animalcontrol", 1000)
asm.setid("owner", 1000)
asm.setid("ownerdonation", 1000)
asm.setid("ownerlicence", 1000)

animals = {}
animalcontrol = []
movements = []
owners = {}
ownerdonations = []
ownerlicences = []

unknowntransfer = asm.Owner()
unknowntransfer.OwnerSurname = "Transfer Location"
unknowntransfer.Comments = "Unknown transfer location, see movement comments"
owners["0"] = unknowntransfer

# Set up animal records first
for ca in canimal:
    a = asm.Animal()
    a.Archived = 1
    a.DateBroughtIn = datetime.datetime.today() - datetime.timedelta( days=365 )
    animals[ca["animalID"]] = a
    if ca["animalType"] == "C":
        a.SpeciesID = 2
    elif ca["animalType"] == "D":
        a.SpeciesID = 1
    else:
        a.SpeciesID = 7 # X - assume rabbit/misc
    a.AnimalName = ca["nameIfKnown"]
    if a.AnimalName.strip() == "":
        a.AnimalName = "(unknown)"
    a.DateOfBirth = asm.getdate_yyyymmdd(ca["DOB"])
    if a.DateOfBirth is None: a.DateOfBirth = asm.getdate_iso(ca["dateEntered"])
    a.EstimatedDOB = ca["DOBisActual"] == "0" and 1 or 0
    a.Sex = 1
    if ca["sex"] == "F": a.Sex = 0
    a.Neutered = 1
    if ca["altered"] == "U": a.Neuteured = 0
    # Find the breed
    if ca["animalType"] == "C":
        b = findin(cacat, "animalID", ca["animalID"], "felineBreedLUID")
        b = findin(clucat, "luid", b, "hoverText")
        if b != "":
            a.BreedID = asm.breed_id_for_name(b)
            a.BreedName = asm.breed_name_for_id(a.BreedID)
    elif ca["animalType"] == "D":
        b1 = findin(cadog, "animalID", ca["animalID"], "canineBreed1LUID")
        b2 = findin(cadog, "animalID", ca["animalID"], "canineBreed2LUID")
        b1n = findin(cludog, "luid", b1, "hoverText")
        if b2 != "":
            b2n = findin(cludog, "luid", b2, "hoverText")
            a.BreedID = asm.breed_id_for_name(b1n)
            a.Breed2ID = asm.breed_id_for_name(b2n)
            a.CrossBreed = 1
            a.BreedName = asm.breed_name_for_id(a.BreedID) + " / " + asm.breed_name_for_id(a.Breed2ID)
            a.HiddenAnimalDetails = "breed: %s / %s" % (b1n, b2n)
        else:
            a.BreedID = asm.breed_id_for_name(b1n)
            a.BreedName = asm.breed_name_for_id(a.BreedID)
            a.HiddenAnimalDetails = "breed: %s" % b1n
    if ca["animalType"] == "X":
        b = findin(caother, "animalID", ca["animalID"], "otherTypeLUID")
        b = findin(cluother, "luid", b, "hoverText")
        a.HiddenAnimalDetails = "other type: %s" % b

# Now go through the intake records and augment our animal records with how they entered the shelter
for ci in cintake:
    a = animals[ci["animalID"]]
    a.DateBroughtIn = asm.getdatetime_iso(ci["dateTimeIn"])
    # Choose type based on agencyId - 5 = NB, 6 = CC, 7 = CM, 8 = HSNBA
    if ci["agencyID"] == "5":
        a.AnimalTypeID = 42 # NB New Braunfels
        a.generateCode("N")
    elif ci["agencyID"] == "6":
        a.AnimalTypeID = 45 # CC Comal County
        a.generateCode("C")
    elif ci["agencyID"] == "7":
        a.AnimalTypeID = 48 # MA Marion
        a.generateCode("M")
    elif ci["agencyID"] == "8":
        a.AnimalTypeID = 50 # HSNBA
        a.generateCode("H")
    a.ShortCode = ci["controlNo"]
    if ci["intakeType"] == "ST": a.EntryReasonID = 7
    if ci["intakeType"] == "SZ": a.EntryReasonID = 19
    if ci["intakeType"] == "PA": a.EntryReasonID = 14
    if ci["intakeType"] == "OR": a.EntryReasonID = 11
    if ci["intakeType"] == "BC": a.EntryReasonID = 18
    if ci["intakeType"] == "Q": a.EntryReasonID = 15
    hw = asm.getdate_iso(ci["dogHeartwormTest_dateTime"])
    if hw is not None:
        a.HeartwormTested = 1
        a.HeartwormTestDate = hw
        a.HeartwormTestResult = ci["dogHeartwormTest_results"].find("osit") and 2 or 1

# Microchip info
for cm in cmicrochip:
    a = animals[cm["animalID"]]
    a.IdentichipNumber = cm["chipNo"]
    a.IdentichipDate = asm.getdate_yyyymmdd(cm["chipDate"])
    a.Identichipped = 1

# Customers
for cp in ccustomer:
    o = asm.Owner()
    owners[cp["customerID"]] = o
    o.OwnerForeNames = cp["fName"]
    o.OwnerSurname = cp["lName"]
    o.OwnerAddress = cp["addressLine1"]
    o.OwnerTown = cp["city"]
    o.OwnerCounty = cp["state"]
    o.OwnerPostcode = cp["zip"]
    if cp["phone1Type"] == "Cell": 
        o.MobileTelephone = cp["phone1"]
    else:
        o.HomeTelephone = cp["phone1"]
    o.Comments = "Drivers Lic: %s, State: %s, DOB: %s" % (cp["driverLicenseNo"], cp["driverLicenseState"], cp["DOB"])
    if cp["allowAdoption"] == "0":
        o.IsBanned = 1

# Dispositions
for cd in cdisposition:
    exitdate = asm.getdate_iso(cd["dateTimeOut"])
    a = animals[cd["animalID"]]
    if cd["dispositionType"] == "E":
        a.PutToSleep = 1
        a.PTSReasonID = 4
        a.DeceasedDate = exitdate
    if cd["dispositionType"] == "DC":
        a.PutToSleep = 0
        a.PTSReasonID = 2
        a.DeceasedDate = exitdate
    elif cd["dispositionType"] == "A":
        customerid = findin(cadoptions, "dispRecID", cd["recID"], "customerID")
        amount = findin(cadoptions, "dispRecID", cd["recID"], "amountCollected")
        o = owners[customerid]
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 1
        m.MovementDate = exitdate
        a.Archived = 1
        a.ActiveMovementDate = exitdate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 1
        movements.append(m)
        if amount != "0":
            od = asm.OwnerDonation()
            ownerdonations.append(od)
            od.OwnerID = o.ID
            od.AnimalID = a.ID
            od.MovementID = m.ID
            od.Date = exitdate
            od.Donation = asm.get_currency(amount)
            od.DonationTypeID = 2
            od.DonationPaymentID = 1
    elif cd["dispositionType"] == "R":
        customerid = findin(credemption, "dispRecID", cd["recID"], "customerID")
        amount = findin(cadoptions, "dispRecID", cd["recID"], "amountCollected")
        o = owners[customerid]
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 5
        m.MovementDate = exitdate
        a.Archived = 1
        a.ActiveMovementDate = exitdate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 5
        movements.append(m)
        if amount != "0":
            od = asm.OwnerDonation()
            ownerdonations.append(od)
            od.OwnerID = o.ID
            od.AnimalID = a.ID
            od.MovementID = m.ID
            od.Date = exitdate
            od.Donation = asm.get_currency(amount)
            od.DonationTypeID = 8
            od.DonationPaymentID = 1
    elif cd["dispositionType"] == "T":
        transferloc = findin(ctransfer, "dispRecID", cd["recID"], "transferLocation")
        o = unknowntransfer
        m = asm.Movement()
        m.AnimalID = a.ID
        m.OwnerID = o.ID
        m.MovementType = 3
        m.MovementDate = exitdate
        m.Comments = transferloc
        a.Archived = 1
        a.ActiveMovementDate = exitdate
        a.ActiveMovementID = m.ID
        a.ActiveMovementType = 3
        movements.append(m)

# animal notes
for no in canimalnote:
    a = animals[no["animalID"]]
    a.AnimalComments = findin(cnote, "noteID", no["noteID"], "noteText")

# person notes
for no in ccustomernote:
    o = owners[no["customerID"]]
    o.Comments = findin(cnote, "noteID", no["noteID"], "noteText")

incidenttypes = {
    "1": 16, # 10-45
    "2": 43, # Stray
    "3": 47, # Welfare
    "4": 22, # Bite
    "5": 45, # Trap
    "6": 23, # Barking
    "7": 30, # Injured
    "8": 39, # PD
    "9": 32, # Livestock
    "10": 41, # Reptile
    "11": 38, # Patrol
    "12": 20, # Vets
    "13": 33, # Lunch
    "14": 31, # Inspection
    "15": 17, # 10-6
    "16": 48, # Wildlife
    "17": 36, # Owner Release
    "18": 18, # Abandoned
    "19": 27, # Locked in car
    "20": 24, # Chickens
    "21": 26, # Confined
    "22": 34, # Made contact
    "23": 35, # Officer initiated
    "24": 29, # Recheck
    "25": 40, # Public service
    "26": 29, # Follow up
    "27": 28, # Excessive animals
    "28": 37, # Prisoner animal
    "29": 46, # Unauthorised
    "30": 25, # Class
    "31": 44, # Tether
    "32": 21, # Assist ACO
    "33": 42, # Speak to owner
    "34": 19 # Animal vs Animal
}

completedtypes = {
    "1": 2, # Picked up 1 or more
    "2": 3, # citation
    "3": 11, # verbal warning
    "4": 12, # unable to locate
    "5": 13, # unable to capture
    "7": 32, # bite report taken
    "8": 35, # returned to owner
    "9": 6, # left a door hanger
    "10": 8, # left copy of city ordnance
    "11": 7, # left business card
    "12": 30, # transferred to vet
    "13": 2, # other
    "14": 14, # picked up deceased
    "15": 33, # clear call
    "16": 21, # spoke to owner
    "17": 18, # relocated
    "18": 4, # out of jurisdiction
    "19": 24, # cancelled
    "20": 19, # resecured
    "21": 21, # spoke to complainant
    "22": 15, # set trap
    "23": 5, # transferred to txdot
    "24": 8, # left door hanger and city ordnance
    "25": 36, # discharged firearm
    "26": 31, # game warden
    "27": 9, # left tether law notice
    "28": 27, # picked up trap
    "29": 34, # public service
    "30": 31, # wildlife rescue
    "32": 26, # transferred to county
    "33": 26, # pd assisted
    "34": 26, # trans to pd/sheriff
    "35": 26, # trans to ACO
    "36": 9, # left door hanger, city ordnance, tether law
    "37": 20, # requested contact from owner/complainant
    "38": 17 # location unfounded
}

for oc in coriginalcall:
    ac = asm.AnimalControl()
    animalcontrol.append(ac)
    comments = ""
    calldate = asm.getdatetime_iso(oc["dateTimeRcvd"])
    ac.CallTaker = findin(cusers, "userID", oc["rcvdBy"], "fName")
    if oc["callerName"].strip() != "":
        comments = "caller: %s %s %s" % (oc["callerName"], oc["callerAddress"], oc["callerPhone"])
        comments += "\ncall taken by: %s" % ac.CallTaker
    # Dispatch
    ac.DispatchAddress = oc["locationOfComplaint"]
    ac.IncidentTypeID = incidenttypes[oc["natureOfComplaintLUID"]]
    ac.IncidentDateTime = calldate
    ac.CallDateTime = calldate
    ac.DispatchDateTime = asm.getdatetime_iso(oc["dateTimeDispatched"])
    ac.DispatchedACO = findin(cusers, "userID", oc["dispatchedTo"], "fName")
    comments += "\ndispatched to: %s" % ac.DispatchedACO
    ac.Sex = 2
    # Find the call record to get completion info
    for cc in ccall:
        if cc["callID"] == oc["callID"]:
            ac.RespondedDateTime = asm.getdatetime_iso(cc["dateTimeArrived"])
            ac.CompletedDate = asm.getdate_iso(cc["dateTimeComplete"])
            ac.IncidentCompletedID = completedtypes[cc["outcomeCodeLUID"]]
            comments += "\ncase no: %s" % cc["caseNo"]
            if cc["outcomeAnimalCount"] != "":
                comments += "\nanimal count: %s" % cc["outcomeAnimalCount"]
    # Any notes?
    noteid = findin(ccallnote, "callID", oc["callID"], "noteID")
    notetext = findin(cnote, "noteID", noteid, "noteText")
    if notetext != "":
        comments += "\n%s" % notetext
    # Does an animal record have this callID? If so, link to it
    for ci in cintake:
        if ci["callID"] == oc["callID"]:
            ac.AnimalID = animals[ci["animalID"]].ID
    ac.CallNotes = comments.strip().replace("'", "`")

for rl in clic:
    if rl["customerID"].strip() == "": continue
    if rl["animalID"].strip() == "": continue
    ol = asm.OwnerLicence()
    ownerlicences.append(ol)
    ol.OwnerID = owners[rl["customerID"]].ID
    ol.AnimalID = animals[rl["animalID"]].ID
    ol.IssueDate = asm.getdate_yyyymmdd(rl["CL_IssueDate"])
    ol.ExpiryDate = asm.getdate_yyyymmdd(rl["RV_ExpDate"])
    if rl["CL_Type"] == "A":
        ol.LicenceTypeID = 1
    else: 
        ol.LicenceTypeID = 2
    ol.LicenceNumber = "cv%d: %s" % (ol.ID, rl["RV_TagNo"])

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= 10000 AND ID < %d;" % asm.getid("animal")
print "DELETE FROM animalcontrol WHERE ID >= 1000 AND ID < %d;" % asm.getid("animalcontrol")
print "DELETE FROM owner WHERE ID >= 1000 AND ID < %d;" % asm.getid("owner")
print "DELETE FROM ownerdonation WHERE ID >= 1000 AND ID < %d;" % asm.getid("ownerdonation")
print "DELETE FROM ownerlicence WHERE ID >= 1000 AND ID < %d;" % asm.getid("ownerlicence")
print "DELETE FROM adoption WHERE ID >= 1000 AND ID < %d;" % asm.getid("adoption")

# Now that everything else is done, output stored records
for a in animals.itervalues():
    print a
for o in owners.itervalues():
    print o
for od in ownerdonations:
    print od
for m in movements:
    print m
for ac in animalcontrol:
    print ac
for ol in ownerlicences:
    print ol

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

