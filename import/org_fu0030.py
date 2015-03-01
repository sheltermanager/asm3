#!/usr/bin/python

import asm, csv, sys, datetime

# Import script for FuRR, October 15, 2009

# Collection of converted owner, animal and movement objects so far
owners = []
animals = []
movements = []

# Map of words used in files to standard ASM breed IDs
breedmap = ( 
        ("Scottish Fold", 292, "Scottish Fold"),
        ("Himalayan", 338, "Himalayan"),
        ("Snowshoe", 297, "Snowshoe"),
        ("Ragdoll", 290, "Ragdoll"),
        ("Persian", 287, "Persian"),
        ("Maine Coon" , 279, "Maine Coon"),
        ("Siamese" , 294, "Siamese"),
        ("Russian Blue" , 291, "Russian Blue"),
        ("Dilute Calico" , 241, "Dilute Calico"),
        ("Calico" , 234, "Calico"),
        ("Tabby" , 300, "Tabby"),
        ("DLH" , 243, "Domestic Long Hair"),
        ("DMH" , 252, "Domestic Medium Hair"),
        ("DSH" , 261, "Domestic Short Hair")
        )
def getbreed(s):
    """ Looks up the breed, returns DSH if nothing matches """
    for b in breedmap:
        if s.find(b[0]) != -1:
            return b[1]
    return 261

def getbreedname(i):
    """ Looks up the breed's name """
    for b in breedmap:
        if b[1] == i:
            return b[2]
    return "Domestic Short Hair"

colourmap = (
            ( "Black and White", 3 ),
            ( "Black & White", 3 ),
            ( "White and Black", 5),
            ( "White & Black", 5),
            ( "Brown and Black", 12 ),
            ( "Brown & Black", 12 ),
            ( "Black and Brown", 13 ),
            ( "Black & Brown", 13 ),
            ( "Torti and White", 27 ),
            ( "Torti & White", 27 ),
            ( "Tabby and White", 28 ),
            ( "Tabby & White", 28 ),
            ( "Ginger and White", 29 ),
            ( "Ginger & White", 29 ),
            ( "Red and White", 29 ),
            ( "Red & White", 29 ),
            ( "Orange and White", 29 ),
            ( "Orange & White", 29 ),
            ( "Grey and White", 31 ),
            ( "Grey & White", 31 ),
            ( "Brown and White", 35 ),
            ( "Brown & White", 35 ),
            ( "White and Grey", 32 ),
            ( "White & Grey", 32 ),
            ( "White and Gray", 32 ),
            ( "White & Gray", 32 ),
            ( "White and Tabby", 37 ),
            ( "White & Tabby", 37 ),
            ( "White and Brown", 40 ),
            ( "White & Brown", 40 ),
            ( "Blue", 36 ),
            ( "Black", 1 ),
            ( "White", 2 ),
            ( "Ginger", 4 ),
            ( "Red", 4 ),
            ( "Orange", 4 ),
            ( "Torti", 6),
            ( "Tabby", 7),
            ( "Brown", 11 ),
            ( "Cream", 23 ),
            ( "Grey", 30 ),
            ( "Gray", 30 )
            )

def getcolour(s):
    """ Lookup the colour, returns black if nothing matches """
    for c in colourmap:
        if s.find(c[0]) != -1:
            return c[1]
    return 1

# Sex appears as -- Male or -- Female in description field
# if it's not present, return unknown as sex
def getsex(s):
    if s.find("Male") != -1 or s.find("-- M") != -1:
        return 1
    elif s.find("Female") != -1 or s.find("-- F") != -1:
        return 0
    else:
        return 2

# For use with fields that just contain the sex
def getsexmf(s):
    if s.find("M"):
        return 1
    elif s.find("F"):
        return 0
    else:
        return 2


def getcity(s):
    """Get city from city/state/zip field - City, ST  ZIP """
    if s.strip() == "": return ""
    return s[0:s.find(",")]

def getstate(s):
    if s.strip() == "": return ""
    x = s.find(",")
    if x == -1: return ""
    return s[x + 2:x + 4]

def getzip(s):
    if s.strip() == "": return ""
    x = s.find("  ")
    if x == -1: return ""
    return s[x + 2:]

def getdate(s, defyear = "03"):
    """ Parses a date in MM/DD/YYYY format. If the field is blank, None is returned """
    if s.strip() == "": return None
    b = s.split("/")
    # if we couldn't parse the date, use the first of the default year
    if len(b) < 3: return datetime.date(int(defyear) + 2000, 1, 1)
    try:
        year = int(b[2])
        if year < 1900: year += 2000
        return datetime.date(year, int(b[0]), int(b[1]))
    except:
        return datetime.date(int(defyear) + 2000, 1, 1)

def salestype(s):
    if s.find("Vet") != -1: return 3
    if s.find("Clinic") != -1: return 3
    if s.find("Kro") != -1: return 4
    if s.find("Misc") != -1: return 5
    if s.find("Food") != -1: return 6
    if s.find("Ebay") != -1: return 7
    if s.find("Med") != -1: return 8
    if s.find("Yard") != -1: return 9
    return 2

def tocurrency(s):
    if s.strip() == "": return 0.0
    s = s.replace("$", "")
    try:
        return float(s)
    except:
        return 0.0

def getmydate(s, mandatory = False, defyear = "03"):
    """ Parses a date in 
    		Month/Year (03/2005) format
    		Month-Year (Apr-03) format 
		Month/Day/Year (05/02/08) format
		Month/Day/Year (Sep/02/08) format
		and returns a python date. 
		If the date is blank, it returns None.
		If mandatory is set, the beginning of the passed year is returned
		if the date is blank or could not be parsed.
                """
    mos = ( ("Jan", 1),
            ("Feb", 2),
            ("Mar", 3),
            ("Apr", 4),
            ("May", 5),
            ("Jun", 6),
            ("Jul", 7),
            ("Aug", 8),
            ("Sep", 9),
            ("Oct", 10),
            ("Nov", 11),
            ("Dec", 12) )
    # If the date's blank and we're mandatory just use the current year
    if s.strip() == "" and mandatory:
        return datetime.date(int(defyear) + 2000, 1, 1)
    elif s.strip() == "" and not mandatory:
    	return None
    # Is there a string month in our date?
    hasstr = False
    month = 1
    for m in mos:
        if s.find(m[0]) != -1:
	    hasstr = True
            month = m[1]
            break
    # If the date doesn't have a monthstr, contains a slash and is less than 7 chars, 
    # it must be MM/YYYY format
    if not hasstr and s.find("/") != -1 and len(s) <= 7: 
    	dbit = s.split("/")
	return getdate("%s/%s/%s" % ( dbit[0], "01", dbit[1] ))
    # If the date doesn't have a monthstr, contains a slash and is less than 10 chars, 
    # it must be MM/DD/YYYY format
    if not hasstr and s.find("/") != -1 and len(s) <= 10:
    	return getdate(s, defyear)
    # Split the date according to its separator char
    if s.find("-") != -1:
    	dbit = s.split("-")
    else:
    	dbit = s.split("/")
    nd = ""
    # How many bits? 2 and we need to supply the day
    if len(dbit) == 2:
    	nd = "%s/%s/%s" % ( month, "01", dbit[1] )
    # 3 bits and we have the day
    elif len(dbit) == 3:
    	nd = "%s/%s/%s" % ( month, dbit[1], dbit[2] )
    dd = getdate(nd, defyear)
    if dd == None and mandatory:
        dd = datetime.date(int(defyear) + 2000, 1, 1)
    return dd

def yearfromfilename(s):
    return s[len(s) - 6: len(s) - 4]

def findanimal(furrid = ""):
    """ Looks for an animal with the given FuRR ID in the collection
        of animals. If one wasn't found, or the ID given was blank,
        a new animal is added to the collection and returned """

    if furrid.strip() == "":
        a = asm.Animal()
        animals.append(a)
        return a

    for a in animals:
        if a.ExtraID == furrid.strip():
            return a

    a = asm.Animal()
    a.ExtraID = furrid.strip()
    animals.append(a)
    return a

def animaldetails(a, name, description, arrivaldate, rescuedfrom, dateofbirth, defyear = "03"):
	a.AnimalName = name
        a.BaseColourID = getcolour(description)
        a.Sex = getsex(description)
        a.Size = 2
        a.BreedID = getbreed(description)
        a.Breed2ID = a.BreedID
        a.BreedName = getbreedname(a.BreedID)
        a.SpeciesID = 1
        a.DateBroughtIn = getmydate(arrivaldate, True, defyear)
        # animal type and code
        atype = "Unwanted"
        if rescuedfrom.find("Feral") != -1:
            a.AnimalTypeID = 3
            a.EntryReasonID = 7
            atype = "Feral"
        elif rescuedfrom.find("Stray") != -1:
            a.AnimalTypeID = 2
            a.EntryReasonID = 7
            atype = "Stray"
        else:
            a.AnimalTypeID = 1
            a.EntryReasonID = 11
            atype = "Unwanted"
        a.generateCode(atype)
        dob = getmydate(dateofbirth, True, defyear)
        a.DateOfBirth = dob

def animalflags(a, neutered, specialneeds, tested, shots, defyear = "03"):
	""" Bits related to special animal flags """
	# neutered
        if neutered.startswith("Y"):
            a.Neutered = 1
        else:
            a.Neutered = 0
	# see if we can parse a neutered date
	neutered = neutered.replace("Y/", "")
	if neutered.find("/") != -1:
	    a.NeuteredDate = getmydate(neutered, False, defyear)
        # special needs
        if specialneeds.strip() != "":
            a.HasSpecialNeeds = 1
            a.HealthProblems = row[SPECIALNEEDS]
        # fivl/fevl tested
        if tested.find("Y") != "":
            a.CombiTested = 1
	    tested = tested.lower()
	    # Can we get a date in there?
	    dbit = tested.split(" ")
	    dd = None
	    for b in dbit:
	    	if b.find("/") != -1:
			dd = getmydate(b, True, defyear)
            a.CombiTestDate = dd
	    # Default to unknown
	    a.CombiTestResult = 0
	    a.FLVResult = 0
	    # Lets look for a negative first
            if row[TESTED].find("Neg") != -1:
                a.CombiTestResult = 1
                a.FLVResult = 1
	    # Individual positives
            if tested.find("fiv+") != -1 or tested.find("fiv +") != -1:
	    	a.CombiTestResult = 2
	    if tested.find("felv+") != -1 or tested.find("felv +") != -1:
	    	a.FLVResult = 2
	    if tested.find("fiv-") != -1 or tested.find ("fiv -") != -1:
	    	a.CombiTestResult = 1
	    if tested.find("felv-") != -1 or tested.find ("felv -") != -1:
	    	a.FLVResult = 1
        # shots
        shots = shots.replace("\n", " ")
        sb = shots.split(" ")
        firstvacc = False
        secondvacc = False
        thirdvacc = False
        rabiesvacc = False
        boostervacc = False
        for b in sb:
            if b.startswith("1-"):
                dd = getmydate(b.replace("1-", ""), False, defyear)
                if dd != None and not firstvacc:
                    firstvacc = True
                    av = asm.AnimalVaccination()
                    av.DateRequired = dd
                    av.DateOfVaccination = dd
                    av.AnimalID = a.ID
                    av.VaccinationID = 1
                    print av
            elif b.startswith("2-"):
                dd = getmydate(b.replace("2-", ""), False, defyear)
                if dd != None and not secondvacc:
                    secondvacc = True
                    av = asm.AnimalVaccination()
                    av.DateRequired = dd
                    av.DateOfVaccination = dd
                    av.AnimalID = a.ID
                    av.VaccinationID = 2
                    print av
            elif b.startswith("3-"):
                dd = getmydate(b.replace("3-", ""), False, defyear)
                if dd != None and not thirdvacc:
                    thirdvacc = True
                    av = asm.AnimalVaccination()
                    av.DateRequired = dd
                    av.DateOfVaccination = dd
                    av.AnimalID = a.ID
                    av.VaccinationID = 3
                    print av
            elif b.find("/") != -1 and b != 'w/R':
                dd = getmydate(b, False, defyear)
                if dd != None:
                    av = asm.AnimalVaccination()
                    av.DateRequired = dd
                    av.DateOfVaccination = dd
                    av.AnimalID = a.ID
                    if shots.find("w/R") != -1 and not rabiesvacc:
                        av.VaccinationID = 4
                        rabiesvacc = True
                        print av
                    elif not boostervacc:
                        av.VaccinationID = 5
                        boostervacc = True
                        print av

	# good with flags
	a.IsGoodWithCats = 2
	a.IsGoodWithDogs = 2
	a.IsGoodWithChildren = 2
	a.IsHouseTrained = 2

def findowner(name):
    """ Looks for an owner with name given in the collection of owners.
        If one isn't found, adds a new owner to the collection with
        the name given (which is assumed to be "surname forenames")
        and returns that. This means we try our best to reuse and
        update owner records with the same name.
    """

    # Remove the word "Foster " or "Foster/" from the name - it appeared
    # in earlier files
    name = name.replace("Foster ", "")
    name = name.replace("Foster/", "")

    # If there's a slash in the name, only take the first portion, 
    # otherwise it will look stupid
    if name.find("/") != -1:
        name = name[0:name.find("/")]

    # Remove any whitespace
    name = name.strip()

    for o in owners:
        if o.OwnerName.find(name) != -1:
            return o

    o = asm.Owner()
    o.OwnerName = name
    o.OwnerSurname = name[0:name.find(" ")]
    o.OwnerForeNames = name[name.find(" ") + 1:]
    owners.append(o)
    return o





# --- START OF CONVERSION ---

print "\\set ON_ERROR_STOP\nBEGIN;"

# Clear anything from previous runs
print "DELETE FROM animal;"
print "DELETE FROM owner;"
print "DELETE FROM adoption;"
print "DELETE FROM ownerdonation;"
print "DELETE FROM animalvaccination;"

# We can blow away the species list before we start - they only
# deal with cats.
print "DELETE FROM species;"
print asm.Species(Name = "Cat", PetFinder = "Cat")

print "DELETE FROM internallocation;"
print asm.Location(Name = "FuRR")

print "DELETE FROM animaltype;"
print asm.AnimalType(Name = "U - Unwanted Cat")
print asm.AnimalType(Name = "S - Stray Cat")
print asm.AnimalType(Name = "F - Feral Cat")
print asm.AnimalType(Name = "N - Non-FuRR Animal")

print "DELETE FROM vaccinationtype;"
print asm.VaccinationType(Name = "First Vaccination")
print asm.VaccinationType(Name = "Second Vaccination")
print asm.VaccinationType(Name = "Third Vaccination")
print asm.VaccinationType(Name = "Rabies")
print asm.VaccinationType(Name = "Booster")


print "DELETE FROM donationtype;"
print asm.DonationType(Name = "Adoption Fee")
print asm.DonationType(Name = "Donation")
print asm.DonationType(Name = "Vet Services")
print asm.DonationType(Name = "Kroger")
print asm.DonationType(Name = "Misc")
print asm.DonationType(Name = "Food")
print asm.DonationType(Name = "Ebay")
print asm.DonationType(Name = "Meds")
print asm.DonationType(Name = "Yard Sale")


# Extra return type for animals coming back from foster home to be adopted
print "DELETE FROM entryreason WHERE ID = 12;"
print "INSERT INTO entryreason VALUES ( 12, 'For Adoption', '' );"


# ================ ADOPTIONS =========================

files = ( "Cat_Kitten Adoptions_03.csv",
          "Cat_Kitten Adoptions_04.csv",
          "Cat_Kitten Adoptions_05.csv",
          "Cat_Kitten Adoptions_06.csv",
          "Cat_Kitten Adoptions_07.csv",
          "Cat_Kitten Adoptions_08.csv",
          "Cat_Kitten Adoptions_09.csv" )

# Readable references to CSV columns in the file
ID = 0
NAME = 1
DESCRIPTION = 2
DATEOFBIRTH = 4
RESCUEDFROM = 5
FOSTERHOME = 6
ARRIVALDATE = 7
TESTED = 8
SHOTS = 9
NEUTERED = 10
LASTFLEA = 11
LASTWORM = 12
INDOOR = 13
SPECIALNEEDS = 14
ADOPTIONDATE = 15
SURNAME = 16
FORENAMES = 17
ADDRESS1 = 18
ADDRESS2 = 19
CITYSTATEZIP= 20
EMAIL = 21
TELEPHONE = 22
FEE = 23
DONATION = 24
FOLLOWUP = 25
COMMENTS = 26
for file in files:
    reader = csv.reader(open(file), dialect="excel")
    irow = 0
    for row in reader:
        
        # Skip first 3 rows of header
        irow += 1
        if irow < 4: continue

        # Not enough data for row
        if len(row) < 2: break
        if row[0].strip() == "" and row[1].strip() == "" and row[2].strip() == "": break
    
        # New animal record 
        a = findanimal(row[ID])
	animaldetails(a, row[NAME], row[DESCRIPTION], row[ARRIVALDATE], row[RESCUEDFROM], row[DATEOFBIRTH], yearfromfilename(file))
        # Stick bits we can't convert 100% in the animal's hidden comments
        a.HiddenAnimalDetails = "Previous ID:%s\nDescription: %s\nRescued From: %s\nLast Flea: %s\nLast Worm: %s\nIndoor/Outdoor: %s\nShots: %s\nTested: %s" % ( 
            row[ID], row[DESCRIPTION], row[RESCUEDFROM], row[LASTFLEA], row[LASTWORM], row[INDOOR], row[SHOTS], row[TESTED] )
        a.AnimalComments = row[COMMENTS]
        adoptiondate = getmydate(row[ADOPTIONDATE], True, yearfromfilename(file))

        # Do we have a foster name? If so, Find/Create the fosterer
        if row[FOSTERHOME].strip() != "":
            fosterer = findowner(row[FOSTERHOME])
            fosterer.IsFosterer = 1
            # Create a foster movement, with the animal returned on
            # the adoption date
            fm = asm.Movement()
            fm.OwnerID = fosterer.ID
            fm.AnimalID = a.ID
            fm.MovementDate = a.DateBroughtIn
            fm.MovementType = 2
            fm.ReturnDate = adoptiondate
            fm.ReturnedReasonID = 12
            movements.append(fm)

        # Create the adopter
        adopter = findowner(row[FORENAMES] + " " + row[SURNAME])
        adopter.OwnerSurname = row[SURNAME]
        adopter.OwnerForeNames = row[FORENAMES]
        adopter.OwnerAddress = row[ADDRESS1] 
        if row[ADDRESS2].strip() != "": adopter.OwnerAddress += "\n" + row[ADDRESS2]
        adopter.OwnerTown = getcity(row[CITYSTATEZIP])
        adopter.OwnerCounty = getstate(row[CITYSTATEZIP])
        adopter.OwnerPostcode = getzip(row[CITYSTATEZIP])
        adopter.HomeTelephone = row[TELEPHONE]
        adopter.EmailAddress = row[EMAIL]

        # And the adoption movement
        am = asm.Movement()
        am.OwnerID = adopter.ID
        am.AnimalID = a.ID
        am.MovementDate = adoptiondate
        am.MovementType = 1
        if row[COMMENTS].find("Transfer") != -1:
            am.MovementType = 3
        am.Comments = row[FOLLOWUP]
        am.Donation = tocurrency(row[FEE])
        movements.append(am)

        # And the donation/fee record
        if am.Donation > 0:
            d = asm.OwnerDonation()
            d.OwnerID = adopter.ID
            d.MovementID = am.ID
            d.DonationTypeID = 1
            d.Date = am.MovementDate
            d.Donation = am.Donation
            print d

        # Mark the adoption as the active movement for the animal
        # and make sure it's off shelter
        a.ActiveMovementID = am.ID
        a.ActiveMovementDate = am.MovementDate
        a.ActiveMovementType = 1
        a.Archived = 1




# ================ DEATHS =========================

files = ( "Cat_Kitten Deceased_03.csv",
          "Cat_Kitten Deceased_04.csv",
          "Cat_Kitten Deceased_05.csv",
          "Cat_Kitten Deceased_06.csv",
          "Cat_Kitten Deceased_07.csv",
          "Cat_Kitten Deceased_08.csv",
          "Cat_Kitten Deceased_09.csv" )

# Readable references to CSV columns in the file
ID = 0
NAME = 1
DESCRIPTION = 2
DATEOFBIRTH = 4
RESCUEDFROM = 5
FOSTERHOME = 6
ARRIVALDATE = 7
TESTED = 8
SHOTS = 9
NEUTERED = 10
LASTFLEA = 11
LASTWORM = 12
INDOOR = 13
SPECIALNEEDS = 14
ADOPTIONDATE = 15
SURNAME = 16
FORENAMES = 17
ADDRESS1 = 18
ADDRESS2 = 19
CITYSTATEZIP= 20
EMAIL = 21
TELEPHONE = 22
FEE = 23
DONATION = 24
FOLLOWUP = 25
COMMENTS = 26
for file in files:
    reader = csv.reader(open(file), dialect="excel")
    irow = 0
    for row in reader:
        
        # Skip first 3 rows of header
        irow += 1
        if irow < 4: continue

        # Not enough data for row
        if len(row) < 2: break
        if row[0].strip() == "" and row[1].strip() == "" and row[2].strip() == "": break
    
        # New animal record 
        a = findanimal(row[ID])
	animaldetails(a, row[NAME], row[DESCRIPTION], row[ARRIVALDATE], row[RESCUEDFROM], row[DATEOFBIRTH], yearfromfilename(file))
       	animalflags(a, row[NEUTERED], row[SPECIALNEEDS], row[TESTED], row[SHOTS], yearfromfilename(file))
        # Deceased date - chop up the comments and find something
        # that looks like a date
        cb = row[COMMENTS].split(" ")
        dd = datetime.date(int(yearfromfilename(file)) + 2000, 1, 1)
        for b in cb:
            if b.find("/") != -1:
                dd = getmydate(b.replace(".", ""), True, yearfromfilename(file))
                break
        a.DeceasedDate = dd

        # Stick bits we can't convert 100% in the animal's hidden comments
        a.HiddenAnimalDetails = "Previous ID:%s\nDescription: %s\nRescued From: %s\nLast Flea: %s\nLast Worm: %s\nIndoor/Outdoor: %s\nShots: %s\nTested: %s" % ( 
            row[ID], row[DESCRIPTION], row[RESCUEDFROM], row[LASTFLEA], row[LASTWORM], row[INDOOR], row[SHOTS], row[TESTED] )
        a.AnimalComments = row[COMMENTS]
        adoptiondate = getmydate(row[ADOPTIONDATE], True, yearfromfilename(file))

        # Do we have a foster name? If so, Find/Create the fosterer
        if row[FOSTERHOME].strip() != "":
            fosterer = findowner(row[FOSTERHOME])
            fosterer.IsFosterer = 1
            # Create a foster movement 
            fm = asm.Movement()
            fm.OwnerID = fosterer.ID
            fm.AnimalID = a.ID
            fm.MovementDate = a.DateBroughtIn
            fm.MovementType = 2
            fm.ReturnedReasonID = 12
            movements.append(fm)

        # Create the adopter - if there's an adoption date
        if row[ADOPTIONDATE].strip() != "":
            adopter = findowner(row[FORENAMES] + " " + row[SURNAME])
            adopter.OwnerSurname = row[SURNAME]
            adopter.OwnerForeNames = row[FORENAMES]
            adopter.OwnerAddress = row[ADDRESS1] 
            if row[ADDRESS2].strip() != "": adopter.OwnerAddress += "\n" + row[ADDRESS2]
            adopter.OwnerTown = getcity(row[CITYSTATEZIP])
            adopter.OwnerCounty = getstate(row[CITYSTATEZIP])
            adopter.OwnerPostcode = getzip(row[CITYSTATEZIP])
            adopter.HomeTelephone = row[TELEPHONE]
            adopter.EmailAddress = row[EMAIL]

            # And the adoption movement
            am = asm.Movement()
            am.OwnerID = adopter.ID
            am.AnimalID = a.ID
            am.MovementDate = adoptiondate
            am.MovementType = 1
            if row[COMMENTS].find("Transfer") != -1:
                am.MovementType = 3
            am.Comments = row[FOLLOWUP]
            am.Donation = tocurrency(row[FEE])
            movements.append(am)

            # And the donation/fee record
            if am.Donation > 0:
                d = asm.OwnerDonation()
                d.OwnerID = adopter.ID
                d.MovementID = am.ID
                d.DonationTypeID = 1
                d.Date = am.MovementDate
                d.Donation = am.Donation
                print d

            # If the animal was adopted, it died off shelter
            a.DiedOffShelter = 1

            # Mark the adoption as the active movement for the animal
            a.ActiveMovementID = am.ID
            a.ActiveMovementDate = am.MovementDate
            a.ActiveMovementType = 1

        # Add the animal to our list
        a.Archived = 1


# ================ CURRENT =========================


# Readable references to CSV columns in the file
ID = 0
NAME = 1
DESCRIPTION = 2
DATEOFBIRTH = 4
RESCUEDFROM = 5
FOSTERHOME = 6
FOSTERCERT = 7
ARRIVALDATE = 8
TESTED = 9
SHOTS = 10
NEUTERED = 11
LASTFLEA = 12
LASTWORM = 13
INDOOR = 14
SPECIALNEEDS = 15
COMMENTS = 16

file = "Cat_Kitten DB.csv"
reader = csv.reader(open(file), dialect="excel")
irow = 0
for row in reader:
    
    # Skip first 2 rows of header
    irow += 1
    if irow < 3: continue

    # Not enough data for row
    if len(row) < 2: break
    if row[0].strip() == "" and row[1].strip() == "" and row[2].strip() == "": break

    # New animal record 
    a = findanimal(row[ID])
    animaldetails(a, row[NAME], row[DESCRIPTION], row[ARRIVALDATE], row[RESCUEDFROM], row[DATEOFBIRTH], "09")
    animalflags(a, row[NEUTERED], row[SPECIALNEEDS], row[TESTED], row[SHOTS], "09")
    # Stick bits we can't convert 100% in the animal's hidden comments
    a.HiddenAnimalDetails = "Previous ID:%s\nDescription: %s\nRescued From: %s\nLast Flea: %s\nLast Worm: %s\nIndoor/Outdoor: %s\nShots: %s\nTested: %s" % ( 
        row[ID], row[DESCRIPTION], row[RESCUEDFROM], row[LASTFLEA], row[LASTWORM], row[INDOOR], row[SHOTS], row[TESTED] )
    a.AnimalComments = row[COMMENTS]
    adoptiondate = getmydate(row[ADOPTIONDATE], True, "09")

    # Do we have a foster name? If so, Find/Create the fosterer
    if row[FOSTERHOME].strip() != "":
        fosterer = findowner(row[FOSTERHOME])
        fosterer.IsFosterer = 1
        # Create a foster movement, with the animal returned on
        # the adoption date
        fm = asm.Movement()
        fm.OwnerID = fosterer.ID
        fm.AnimalID = a.ID
        fm.MovementDate = a.DateBroughtIn
        fm.MovementType = 2
        fm.ReturnedReasonID = 12
        movements.append(fm)

        # Mark the foster as the active movement for the animal
        a.ActiveMovementID = fm.ID
        a.ActiveMovementDate = fm.MovementDate
        a.ActiveMovementType = 2
        a.Archived = 0


# ================ BANNED OWNERS =========================


# Readable references to CSV columns in the file
SURNAME = 0
FORENAMES = 1
ADDRESS1 = 2
ADDRESS2 = 3
CITYSTATEZIP = 4
EMAIL = 5
TELEPHONE = 6
COMMENTS = 7

file = "Cat_Kitten_Do_Not_Adopt_Foster.csv"
reader = csv.reader(open(file), dialect="excel")
irow = 0
for row in reader:
    
    # Skip first 4 rows of header
    irow += 1
    if irow < 5: continue

    # Not enough data for row
    if len(row) < 2: break

    # Create/update banned owner
    o = findowner(row[FORENAMES] + " " + row[SURNAME])
    o.IsBanned = 1
    o.OwnerSurname = row[SURNAME]
    o.OwnerForeNames = row[FORENAMES]
    o.OwnerAddress = row[ADDRESS1] 
    if row[ADDRESS2].strip() != "": o.OwnerAddress += "\n" + row[ADDRESS2]
    o.OwnerTown = getcity(row[CITYSTATEZIP])
    o.OwnerCounty = getstate(row[CITYSTATEZIP])
    o.OwnerPostcode = getzip(row[CITYSTATEZIP])
    o.HomeTelephone = row[TELEPHONE]
    o.EmailAddress = row[EMAIL]
    o.Comments = row[COMMENTS]



# ================ VOLUNTEERS =========================


# Readable references to CSV columns in the file
SURNAME = 0
FORENAMES = 1
ADDRESS = 2
CITY = 3
STATE = 4
ZIP = 5
MOBILE = 6
HOME = 7
WORK = 8
OCCUPATION = 9
EMAIL = 10
DOB = 11
APPDATE = 12
STATUS = 13
SHELTER = 14
CLINIC = 15
COLONYMGMT = 16
PR = 17
CONSTRUCT = 18
VM = 19
FUNDRAISE = 20
CALLS = 21
COMPUTE = 22
PHOTO = 23
FOSTER = 24
YARDWORK = 25
ADOPTION = 26
TRANSP = 27
OTHER = 28

file = "Vol Record.csv"
reader = csv.reader(open(file), dialect="excel")
irow = 0
for row in reader:
    
    # Skip first 3 rows of header
    irow += 1
    if irow < 4: continue

    # Not enough data for row
    if len(row) < 2: break
    if row[SURNAME].strip() == "" and row[FORENAMES].strip() == "": break

    # Create/update volunteer
    o = findowner(row[FORENAMES] + " " + row[SURNAME])
    o.IsVolunteer = 1
    o.OwnerSurname = row[SURNAME]
    o.OwnerForeNames = row[FORENAMES]
    o.OwnerAddress = row[ADDRESS] 
    o.OwnerTown = row[CITY]
    o.OwnerCounty = row[STATE]
    o.OwnerPostcode = row[ZIP]
    o.HomeTelephone = row[HOME]
    o.WorkTelephone = row[WORK]
    o.MobileTelephone = row[MOBILE]
    o.EmailAddress = row[EMAIL]
    if row[FOSTER].strip() != "": o.IsFosterer = 1
    c = """DOB: %s
APPDATE: %s
OCCUPATION: %s
STATUS: %s
SHELTER: %s
CLINIC: %s
COLONYMGMT: %s
PR: %s
CONSTRUCT: %s
VM: %s
FUNDRAISE: %s
CALLS: %s
COMPUTE: %s
PHOTO: %s
FOSTER: %s
YARDWORK: %s
ADOPTION: %s
TRANSP: %s
OTHER: %s""" % ( row[DOB], row[APPDATE], row[OCCUPATION], row[STATUS], row[SHELTER], row[CLINIC], row[COLONYMGMT], row[PR], row[CONSTRUCT], row[VM], row[FUNDRAISE], row[CALLS], row[COMPUTE], row[PHOTO], row[FOSTER], row[YARDWORK], row[ADOPTION], row[TRANSP], row[OTHER] )
    o.Comments = c


# ================ MAILING LIST =========================

# Readable references to CSV columns in the file
NAME = 0
SURNAME = 1
SUFFIX = 2
FORENAMES = 3
MID = 4
ADDRESS1 = 5
ADDRESS2 = 6
CITY = 7
STATE = 8
ZIP = 9
ZIP4 = 10
EMAIL = 11
DATE = 12
TELEPHONE = 13
WHY = 14

file = "Mailing List.csv"
reader = csv.reader(open(file), dialect="excel")
irow = 0
for row in reader:
    
    # Skip first row of header
    irow += 1
    if irow < 2: continue

    # Not enough data for row
    if len(row) < 2: break
    if row[SURNAME].strip() == "" and row[FORENAMES].strip() == "": break

    # Create/update member
    o = findowner(row[FORENAMES] + " " + row[SURNAME])
    o.IsMember = 1
    o.OwnerSurname = row[SURNAME]
    o.OwnerForeNames = row[FORENAMES]
    o.OwnerAddress = row[ADDRESS2] 
    if row[ADDRESS1].strip() != "":
        o.OwnerAddress = row[ADDRESS1] + "\n" + row[ADDRESS2]
    o.OwnerTown = row[CITY]
    o.OwnerCounty = row[STATE]
    o.OwnerPostcode = row[ZIP]
    o.HomeTelephone = row[TELEPHONE]
    o.EmailAddress = row[EMAIL]
    if row[WHY].find("Don") != -1: 
        o.IsDonor = 1
    c = """Why: %s
Zip4: %s""" % ( row[WHY], row[ZIP4] )
    o.Comments = c





# ================ CLINIC =========================

files = ( "Clinic_02_03.csv",
          "Clinic_04.csv",
          "Clinic_05.csv",
          "Clinic_06.csv",
          "Clinic_07.csv",
          "Clinic_08.csv",
          "Clinic_09.csv" )

# Readable references to CSV columns in the file

for file in files:

    format = 0
    if file.find("02") != -1 or file.find("04") != -1 or file.find("05") != -1:
        format = 1
        DATE = 0
        ISFURR = 1
        ISFOSTER = 2
        TESTINGVACSONLY = 3
        SURNAME = 4
        FORENAMES = 5
        ADDRESS = 6
        CITYSTATEZIP = 7
        TELEPHONE = 8
        EMAIL = 9
        SEX = 10
        DESCRIPTION = 11
        ANIMALNAME = 12
        TFS = 13
        EARTIP = 14
        RABIES = 15
        VETCOMMENTS = 16
    elif file.find("06") != -1:
        format = 2
        DATE = 1
        ISFURR = 2
        ISFOSTER = 3
	FURRCOLONY = 4
	FURRFOOD = 5
        TESTINGVACSONLY = 6
        SURNAME = 7
        FORENAMES = 8
        ADDRESS = 9
        CITYSTATEZIP = 10
        TELEPHONE = 11
        EMAIL = 12
        SEX = 13
        DESCRIPTION = 14
        ANIMALNAME = 15
        TFS = 16
        BOOSTER = 17
        BOOSTERAMT = 18
        RABIES = 19
        RABIESAMT = 20
        FIVFELV = 21
        FIVFELVAMT = 22
        REVOLUTION = 23
        REVOLUTIONAMT = 24
        EARTIP = 25
        SNAMT = 26
        MONEYCOMMENTS = 27
        VETCOMMENTS = 28
    elif file.find("07") != -1:
        format = 3
        DATE = 1
        ISFURR = 2
        ISFOSTER = 3
	FURRCOLONY = 4
	FURRFOOD = 5
	OJ = 6
        TESTINGVACSONLY = 7
        SURNAME = 8
        FORENAMES = 9
        ADDRESS = 10
        CITYSTATEZIP = 11
        TELEPHONE = 12
        EMAIL = 13
        SEX = 14
        DESCRIPTION = 15
        ANIMALNAME = 16
        TFS = 17
        BOOSTER = 18
        BOOSTERAMT = 19
        RABIES = 20
        RABIESAMT = 21
        FIVFELV = 22
        FIVFELVAMT = 23
        REVOLUTION = 24
        REVOLUTIONAMT = 25
        EARTIP = 26
        SNAMT = 27
        MONEYCOMMENTS = 28
        VETCOMMENTS = 29
    elif file.find("08") != -1:
        format = 4
        DATE = 1
        ISFURR = 2
        ISFOSTER = 3
	FURRCOLONY = 4
	FURRFOOD = 5
	OJ = 6
        TESTINGVACSONLY = 7
        SURNAME = 8
        FORENAMES = 9
        ADDRESS = 10
        CITYSTATEZIP = 11
        TELEPHONE = 12
        EMAIL = 13
        SEX = 14
        DESCRIPTION = 15
        ANIMALNAME = 16
        TFS = 17
        TRAPPED = 18
        BOOSTER = 19
        BOOSTERAMT = 20
        RABIES = 21
        RABIESNO = 22
        RABIESAMT = 23
        FIVFELV = 24
        FIVFELVAMT = 25
        REVOLUTION = 26
        REVOLUTIONAMT = 27
        EARTIP = 28
        SNAMT = 29
        DONATION = 30
        MONEYCOMMENTS = 31
        VETCOMMENTS = 32

    elif file.find("09") != -1:
        format = 5
        DATE = 1
        ISFURR = 2
        ISFOSTER = 3
	FURRCOLONY = 4
	FURRFOOD = 5
	OJ = 6
	MEDICAT = 7
        TESTINGVACSONLY = 8
        SURNAME = 9
        FORENAMES = 10
        ADDRESS = 11
        CITYSTATEZIP = 12
        TELEPHONE = 13
        EMAIL = 14
        SEX = 15
        DESCRIPTION = 16
        ANIMALNAME = 17
        TFS = 18
        TRAPPED = 19
        BOOSTER = 20
        BOOSTERAMT = 21
        RABIES = 22
        RABIESNO = 23
        RABIESAMT = 24
        FIVFELV = 25
        FIVFELVAMT = 26
        REVOLUTION = 27
        REVOLUTIONAMT = 28
        EARTIP = 29
        SNAMT = 30
        DONATION = 31
        MONEYCOMMENTS = 32
        VETCOMMENTS = 33

    reader = csv.reader(open(file), dialect="excel")
    irow = 0
    for row in reader:
        
        # Skip first 2 rows of header
        irow += 1
        if irow < 3: continue

        # Not enough data for row
        if len(row) < 2: break
        if row[0].strip() == "": break
    
        # New animal record 
        a = asm.Animal()
	animaldetails(a, row[ANIMALNAME], row[DESCRIPTION], row[DATE], "", "", yearfromfilename(file))
	if row[SEX].find("M") != -1:
	    a.Sex = 1
	else:
	    a.Sex = 0
        a.AnimalTypeID = 4
        a.NonShelterAnimal = 1
        a.Archived = 1
        a.generateCode("N")
        vetcomments = ""
        moneycomments = ""
        try: 
            vetcomments = row[VETCOMMENTS]
            moneycomments = row[MONEYCOMMENTS]
        except:
            pass
        # Put vet stuff in the health bit
        if format == 1:
            c = """Tame/Feral/Semi-Feral: %s
Ear Tip? %s
Rabies Vacc: %s
%s""" % ( row[TFS], row[EARTIP], row[RABIES], row[VETCOMMENTS] )
        if format == 2 or format == 3:
            #sys.stderr.write("Format: %d, file %s, data %s\n" % (format, file, ", ".join(row)))
            c = """Tame/Feral/Semi-Feral: %s
Booster: %s
Booster Amount: %s
Rabies: %s
Rabies Amount: %s
FiV/FeLV: %s
FiV/FeLV Amount: %s
Revolution: %s
Revolution Amount: %s
Ear Tip: %s
S/N Amount: %s

%s
%s""" % ( row[TFS], row[BOOSTER], row[BOOSTERAMT], row[RABIES], row[RABIESAMT], row[FIVFELV], row[FIVFELVAMT], row[REVOLUTION], row[REVOLUTIONAMT], row[EARTIP], row[SNAMT], moneycomments, vetcomments )
        if format == 4 or format == 5:

            #sys.stderr.write("Format: %d, file %s, data %s\n" % (format, file, ", ".join(row)))
            rt = row[RABIESNO]
            rt = rt.replace("\n", " ").strip()
            a.RabiesTag = rt
            c = """Tame/Feral/Semi-Feral: %s
Trapped: %s
Booster: %s
Booster Amount: %s
Rabies: %s
Rabies Serial: %s
Rabies Amount: %s
FiV/FeLV: %s
FiV/FeLV Amount: %s
Revolution: %s
Revolution Amount: %s
Ear Tip: %s
S/N Amount: %s
Donation: %s

%s
%s""" % ( row[TFS], row[TRAPPED], row[BOOSTER], row[BOOSTERAMT], row[RABIES], row[RABIESNO], row[RABIESAMT], row[FIVFELV], row[FIVFELVAMT], row[REVOLUTION], row[REVOLUTIONAMT], row[EARTIP], row[SNAMT], row[DONATION], moneycomments, vetcomments )

        a.HealthProblems = c

        # Create the original owner
        o = findowner(row[FORENAMES] + " " + row[SURNAME])
        o.OwnerSurname = row[SURNAME]
        o.OwnerForeNames = row[FORENAMES]
        o.OwnerAddress = row[ADDRESS] 
        o.OwnerTown = getcity(row[CITYSTATEZIP])
        o.OwnerCounty = getstate(row[CITYSTATEZIP])
        o.OwnerPostcode = getzip(row[CITYSTATEZIP])
        o.HomeTelephone = row[TELEPHONE]
        o.EmailAddress = row[EMAIL]
        a.OriginalOwnerID = o.ID
        animals.append(a)


# ================ RETURNS TO OWNERS =========================

files = ( "Cat_Kitten_Cats_Returned_to_Owners_06.csv",
          "Cat_Kitten_Cats_Returned_to_Owners_07.csv",
          "Cat_Kitten_Cats_Returned_to_Owners_09.csv" )

# Readable references to CSV columns in the file
ID = 0
NAME = 1
DESCRIPTION = 2
DATEOFBIRTH = 4
RESCUEDFROM = 5
FOSTERHOME = 6
ARRIVALDATE = 8
TESTED = 9
SHOTS = 10
NEUTERED = 11
LASTFLEA = 12
LASTWORM = 13
INDOOR = 14
SPECIALNEEDS = 15
COMMENTS = 16

oo = findowner("Original Owner")

for file in files:
    reader = csv.reader(open(file), dialect="excel")
    irow = 0
    for row in reader:
        
        # Skip first 2 rows of header
        irow += 1
        if irow < 3: continue

        # Not enough data for row
        if len(row) < 2: break
        if row[0].strip() == "" and row[1].strip() == "" and row[2].strip() == "": break
    
        # New animal record 
    	animaldetails(a, row[NAME], row[DESCRIPTION], row[ARRIVALDATE], row[RESCUEDFROM], row[DATEOFBIRTH], yearfromfilename(file))
        animalflags(a, row[NEUTERED], row[SPECIALNEEDS], row[TESTED], row[SHOTS], yearfromfilename(file))
        # Stick bits we can't convert 100% in the animal's hidden comments
        a.HiddenAnimalDetails = "Previous ID:%s\nDescription: %s\nRescued From: %s\nLast Flea: %s\nLast Worm: %s\nIndoor/Outdoor: %s\nShots: %s\nTested: %s" % ( 
            row[ID], row[DESCRIPTION], row[RESCUEDFROM], row[LASTFLEA], row[LASTWORM], row[INDOOR], row[SHOTS], row[TESTED] )
        a.AnimalComments = row[COMMENTS]

        # Reclaim date - chop up the comments and find something
        # that looks like a date
        cb = row[COMMENTS].split(" ")
        rd = datetime.date(int(yearfromfilename(file)) + 2000, 1, 1)
        for b in cb:
            if b.find("/") != -1:
                rd = getmydate(b.replace(".", ""), True, yearfromfilename(file))
                break

        # Do we have a foster name? If so, Find/Create the fosterer
        if row[FOSTERHOME].strip() != "":
            fosterer = findowner(row[FOSTERHOME])
            fosterer.IsFosterer = 1
            # Create a foster movement, with the animal returned on
            # the reclaim date
            fm = asm.Movement()
            fm.OwnerID = fosterer.ID
            fm.AnimalID = a.ID
            fm.MovementDate = a.DateBroughtIn
            fm.MovementType = 2
            fm.ReturnDate = rd
            fm.ReturnedReasonID = 12
            movements.append(fm)

        # Create the reclaim
        rm = asm.Movement()
        rm.OwnerID = oo.ID
        rm.AnimalID = a.ID
        rm.MovementDate = rd
        rm.MovementType = 5
        rm.Comments = row[COMMENTS]
        movements.append(rm)

        # Mark the reclaim as the active movement for the animal
        # and make sure it's off shelter
        a.ActiveMovementID = rm.ID
        a.ActiveMovementDate = rm.MovementDate
        a.ActiveMovementType = 5
        a.Archived = 1


# ================ DONATIONS AND MISC DONATIONS =========================

files = ( "Donations_03.csv",
          "Donations_04.csv",
          "Donations_05.csv",
          "Donations_06.csv",
          "Donations_07.csv",
          "Donations_08.csv",
          "Donations_09.csv",
          "Donations_Miscellaneous_Sales_03.csv",
          "Donations_Miscellaneous_04.csv",
          "Donations_Miscellaneous_Sales_05.csv",
          "Donations_Miscellaneous_Sales_06.csv",
          "Donations_Miscellaneous_Sales_07.csv",
          "Donations_Miscellaneous_Sales_08.csv",
          "Donations_Miscellaneous_Sales_09.csv" )

# Readable references to CSV columns in the file
SURNAME = 0
FORENAMES = 1
ADDRESS1 = 2
ADDRESS2 = 3
CITYSTATEZIP = 4
HOME = 5
WORK = 6
MOBILE = 7
EMAIL = 8
DATE = 9
AMOUNT = 10
ACCEPTEDBY = 11
COMMENTS = 12
SALESTYPE = 13

for file in files:
    reader = csv.reader(open(file), dialect="excel")
    irow = 0
    for row in reader:
        
        # Skip first 4 rows of header
        irow += 1
        if irow < 5: continue

        # Not enough data for row
        if len(row) < 2: break
        if row[0].strip() == "" and row[1].strip() == "" and row[2].strip() == "": break
    
        o = findowner(row[FORENAMES] + " " + row[SURNAME])
        o.IsDonor = 1
        o.OwnerSurname = row[SURNAME]
        o.OwnerForeNames = row[FORENAMES]
        o.OwnerAddress = row[ADDRESS1] 
        if row[ADDRESS2].strip() != "": o.OwnerAddress += "\n" + row[ADDRESS2]
        o.OwnerTown = getcity(row[CITYSTATEZIP])
        o.OwnerCounty = getstate(row[CITYSTATEZIP])
        o.OwnerPostcode = getzip(row[CITYSTATEZIP])
        o.HomeTelephone = row[HOME]
        o.WorkTelephone = row[WORK]
        o.MobileTelephone = row[MOBILE]
        o.EmailAddress = row[EMAIL]

        # Donation record
        d = asm.OwnerDonation()
        d.OwnerID = o.ID
        d.MovementID = 0
        if row[SALESTYPE].strip() != "":
            d.DonationTypeID = salestype(row[SALESTYPE])
        else:
            d.DonationTypeID = salestype(row[ACCEPTEDBY] + row[COMMENTS])
        d.Date = getmydate(row[DATE], True, yearfromfilename(file))
        d.Donation = tocurrency(row[AMOUNT])
        d.Comments = "%s %s" % ( row[ACCEPTEDBY], row[COMMENTS] )
        print d


# ================ YARD SALE DONATIONS =========================

files = ( "Yard_Sale_Donations_03.csv",
          "Yard_Sale_Donations_04.csv",
          "Yard_Sale_05.csv",
          "Yard_Sale_Misc._Donations_06.csv",
          "Yard_Sale_Misc._Donations_07.csv",
          "Yard_Sale_Misc._Donations_08.csv",
          "Yard_Sale_Misc._Donations_09.csv" )

# Readable references to CSV columns in the file
SURNAME = 0
FORENAMES = 1
ADDRESS1 = 2
ADDRESS2 = 3
CITYSTATEZIP = 4
HOME = 5
WORK = 6
MOBILE = 7
EMAIL = 8
DATE = 9
DESCRIPTION = 10
ACCEPTEDBY = 11
CASHCHECK = 12

for file in files:

    # the 03/04 files don't have an email address, accepted by
    # and comments are over a field as well
    if file.find("03") != -1 or file.find("04") != -1:
        DATE = 8
        DESCRIPTION = 9
        ACCEPTEDBY = 11
        CASHCHECK = 12
    else:
        DATE = 9
        DESCRIPTION = 10
        ACCEPTEDBY = 11
        CASHCHECK = 12

    reader = csv.reader(open(file), dialect="excel")
    irow = 0
    for row in reader:
        
        # Skip first 4 rows of header
        irow += 1
        if irow < 5: continue

        # Not enough data for row
        if len(row) < 2: break
        if row[0].strip() == "" and row[1].strip() == "" and row[2].strip() == "": break
    
        o = findowner(row[FORENAMES] + " " + row[SURNAME])
        o.IsDonor = 1
        o.OwnerSurname = row[SURNAME]
        o.OwnerForeNames = row[FORENAMES]
        o.OwnerAddress = row[ADDRESS1] 
        if row[ADDRESS2].strip() != "": o.OwnerAddress += "\n" + row[ADDRESS2]
        o.OwnerTown = getcity(row[CITYSTATEZIP])
        o.OwnerCounty = getstate(row[CITYSTATEZIP])
        o.OwnerPostcode = getzip(row[CITYSTATEZIP])
        o.HomeTelephone = row[HOME]
        o.WorkTelephone = row[WORK]
        o.MobileTelephone = row[MOBILE]
        # Only set email if we have one
        if EMAIL != DATE:
            o.EmailAddress = row[EMAIL]

        # Donation record
        d = asm.OwnerDonation()
        d.OwnerID = o.ID
        d.MovementID = 0
        d.DonationTypeID = salestype("Yard Sale")
        d.Date = getmydate(row[DATE], True, yearfromfilename(file))
        d.Comments = "%s %s" % ( row[ACCEPTEDBY], row[CASHCHECK] )
        print d






# Now that everything else is done, output stored records
for a in animals:
    # Filter out purely numeric names
    try:
        int(a.AnimalName)
    except:
        print a

for m in movements:
    print m
for o in owners:
    print o

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"
