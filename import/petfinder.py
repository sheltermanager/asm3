#!/usr/bin/python

import asm, csv, urllib2, re, sys, base64, datetime, json

"""
Import module to scrape the PetFinder website. Requires CSV
export of all data from the shelter as PFID.csv
"""

SHELTER = "WI424" # Will read SHELTER.csv for IDs to scrape
#DEFAULT_BREED = 261 # default to dsh
DEFAULT_BREED = 30 # default to black lab

nextid = 500
mediaid = 200
nextownerid = 500
nextmoveid = 500
dbfsid = 500

cols = None
animaldata = {}

def getdate(s):
    """ Parses a date in YYYY-MM-DD format. If the field is blank, today is returned """
    if s.strip() == "": return datetime.datetime.today()
    # Throw away time info
    if s.find(" ") != -1: s = s[0:s.find(" ")]
    b = s.split("-")
    # if we couldn't parse the date, use the first of the default year
    if len(b) < 3: return datetime.date(int(14) + 2000, 1, 1)
    try:
        year = int(b[0])
        if year < 1900: year += 2000
        return datetime.date(year, int(b[1]), int(b[2]))
    except:
        return datetime.datetime.today()

def col(s):
    """ Returns column index for name s """
    global cols
    for i, x in enumerate(cols):
        if x.upper() == s.upper():
            return i
    return -1

def rc(r, c):
    """ Returns a value for a csv row """
    cx = col(c)
    if cx == -1: return ""
    return r[cx].replace("\"", "")

# Read the PetFinder export file
ADOPTABLE_IDS = []
ADOPTED_IDS = []
reader = csv.reader(open("data/" + SHELTER + ".csv", "r"), dialect="excel")
for row in reader:
    # Is this the first row? set column headings if so
    if cols is None: 
        cols = row
        continue
    # skip blank rows
    if len(row) == 0: continue
    petid = rc(row, "Petfinder SystemID").strip()
    if petid == "": continue
    # Send to the right collection based on status
    if rc(row, "Status") == "Adoptable" or rc(row, "Status").strip() == "" or rc(row, "Status").strip == "N":
        ADOPTABLE_IDS.append(petid)
    else:
        ADOPTED_IDS.append(petid)
    # build a map of useful data from this row if we have it
    animaldata[petid] = {
        "petid": rc(row, "Petfinder SystemID"),
        "animalid": rc(row, "Animal ID"),
        "name": rc(row, "Name"),
        "status": rc(row, "Status"),
        "broughtin": rc(row, "Arrival Date"),
        "breed": rc(row, "Breed"),
        "crossbreed": rc(row, "2nd Breed"),
        "mixed": rc(row, "Mixed Breed"),
        "type": rc(row, "Animal Type"),
        "species": rc(row, "Species"),
        "size": rc(row, "Size"),
        "color": rc(row, "Color"),
        "coat": rc(row, "Coat Length"),
        "age": rc(row, "Age"),
        "sex": rc(row, "Gender"),
        "features": rc(row, "Features"),
        "internal": rc(row, "Internal"),
        "contact": rc(row, "Contact"),
        "location": rc(row, "Location"),
        "description": rc(row, "Description"),
        "youtube": rc(row, "YouTube")
    }

o = None
if len(ADOPTED_IDS) > 0:
    o = asm.Owner(nextownerid)
    o.OwnerSurname = "Unknown Owner"
    o.OwnerName = "Unknown Owner"
    o.Comments = "Catchall for adopted animal data from PetFinder"
    print o

TAG_REMOVE = re.compile("<.*?>")
def remove_html_tags(s):
    return re.sub(TAG_REMOVE, "", s)

def strip_unicode(s):
    return "".join(i for i in s if ord(i)<128)

def runre(regex, page):
    rv = re.findall(regex, page)
    if len(rv) == 0: return ""
    return rv[0].strip()

def size_id_for_name(name):
    if name.startswith("Very"):
        return 0
    if name.startswith("Large"):
        return 1
    if name.startswith("Medium"):
        return 2
    if name.startswith("Small"):
        return 3
    return 2


"""
# Get all available petdetail urls by hitting the petfinder page
links = []
url = "http://www.petfinder.com/pet-search?shelterid=" + SHELTER
while True:
    try:
        page = urllib2.urlopen(url).read()
    except Exception,err:
        page = ""
        sys.stderr.write(str(err) + "\n")
        continue
    # Grab petdetail links
    pd = re.findall(".*class=['\"]petlink['\"].*href=['\"](.+?)['\"]", page)
    links += pd
    # If there's a next page, get it, otherwise carry on
    np = re.findall("href=['\"](.+?)['\"]> <img src=[\"']/images/design/next", page)
    if len(np) == 0:
        break
    else:
        url = "http://www.petfinder.com/pet-search?" + np[0]
"""

# Because links to the same animals appear multiple times, squash duplicates
ADOPTABLE_IDS = list(set(ADOPTABLE_IDS))
sys.stderr.write("Found %d pets for %s\n" % (len(ADOPTABLE_IDS), SHELTER))

def pfimport(petid, adopted=False):
    """ Imports a petfinder csv record """
    global nextid
    global dbfsid
    global mediaid
    global nextownerid
    global nextmoveid
    global DEFAULT_BREED
    if not animaldata.has_key(petid):
        sys.stderr.write("Did not find matching entry for %s, giving up")
        return
    # Get the JSON data for the animal from petfinder so we can
    # augment CSV data
    url = "http://www.petfinder.com/v1/pets/%s.json?api_key=98719f8ded45b41f3153f5736d55d162" % petid
    sys.stderr.write("GET " + url + "\n")
    page = ""
    try:
        page = urllib2.urlopen(url).read()
    except Exception,err:
        sys.stderr.write(str(err) + "\n")
        return
    # Find the pfjs JSON and parse it to get details
    js = json.loads(page)
    def rjs(attr):
        if not js.has_key("results"): return ""
        if len(js["results"]) == 0: return ""
        if not js["results"][0].has_key(attr): return ""
        return js["results"][0][attr]
    rec = animaldata[petid]
    broughtin = getdate(rec["broughtin"])
    name = rec["name"]
    breed1 = rec["breed"].strip()
    breed2 = rec["crossbreed"].strip()
    crossbreed = breed2 != ""
    species = rec["species"]
    color = rec["color"]
    size = rec["size"]
    age = rec["age"]
    sex = rec["sex"]
    description = rjs("description")
    description = strip_unicode(description)
    description = description.replace("&#39;", "'").replace("&quot;", "\"").replace("&apos;", "'").replace("&nbsp;", " ")
    description = remove_html_tags(description)
    neutered = "Spay/Neuter" in rjs("features")
    hasshots = "Shots Current" in rjs("features")
    declawed = "Declawed" in rjs("features")
    specialneeds = "Special Needs" in rjs("features")
    housetrained = "House trained" in rjs("features")
    nocats = "Home without cats" in rjs("features")
    nodogs = "Home without dogs" in rjs("features")
    nokids = "Home without small children (< 5yrs old)" in rjs("features")
    # Dump animal info to console
    #deb = u"petid: %s, name: %s, species: %s, breed1: %s, breed2: %s, crossbreed: %s, size: %s, age: %s, sex: %s, neutered: %s, hasshots: %s, specialneeds: %s, declawed: %s, housetrained: %s, nocats: %s, nodogs: %s, nokids: %s\ndescription: %s\n" % (
    #    petid, name, species, breed1, breed2, crossbreed, size, age, sex, neutered, hasshots, specialneeds, declawed, housetrained, nocats, nodogs, nokids, description)
    #sys.stderr.write(deb)
    # If there are enough blanks, bail out
    if name.strip() == "" and species.strip() == "" and breed1.strip() == "":
        sys.stderr.write("ERROR: name, species and breed are all blank, abandoning...\n")
        return
    # Grab all the animal's images and base64 encode them
    encodedjpgdata = []
    if petid != "" and type(rjs("pet_photo") is list):
        for im in rjs("pet_photo"):
            imageurl = "http://photos.petfinder.com" + im
            try:
                sys.stderr.write("GET %s\n" % imageurl)
                jpgdata = urllib2.urlopen(imageurl).read()
                encoded = base64.b64encode(jpgdata)
                encodedjpgdata.append(encoded)
                sys.stderr.write("Got image from %s\n" % imageurl)
            except Exception,err:
                sys.stderr.write(str(err) + "\n")
    # Write our SQL
    a = asm.Animal(nextid)
    nextid += 1
    if species.lower().find("cat") != -1:
        animaltype = 11
        animalletter = "U"
    else:
        animaltype = 2
        animalletter = "D"
    a.AnimalTypeID = animaltype
    a.SpeciesID = asm.species_id_for_name(species)
    a.ShelterCode = "PF%s" % petid
    a.ShortCode = a.ShelterCode
    a.AnimalName = name
    dob = broughtin
    if age.find("Baby") != -1:
        dob -= datetime.timedelta(days = 91)
    elif age.find("Young") != -1:
        dob -= datetime.timedelta(days = 182)
    elif age.find("Adult") != -1:
        dob -= datetime.timedelta(days = 730)
    elif age.find("Senior") != -1:
        dob -= datetime.timedelta(days = 2555)
    a.DateOfBirth = dob
    a.EstimatedDOB = 1
    a.Sex = 1
    if sex.strip().lower().find("female") != -1:
        a.Sex = 0
    a.BreedID = asm.breed_id_for_name(breed1, DEFAULT_BREED)
    if not crossbreed:
        a.Breed2ID = a.BreedID
        a.BreedName = asm.breed_name_for_id(a.BreedID)
        a.CrossBreed = 0
    else:
        a.Breed2ID = asm.breed_id_for_name(breed2, DEFAULT_BREED)
        a.BreedName = asm.breed_name_for_id(a.BreedID) + " / " + asm.breed_name_for_id(a.Breed2ID)
        a.CrossBreed = 1
    a.BaseColourID = asm.colour_id_for_name(color)
    a.ShelterLocation = 1
    a.Size = size_id_for_name(size)
    a.Declawed = declawed and 1 or 0
    a.HasSpecialNeeds = specialneeds and 1 or 0
    a.DateBroughtIn = broughtin
    a.EntryReasonID = 1
    if neutered:
        a.Neutered = 1
    if housetrained: a.IsHouseTrained = 0
    if nodogs: a.IsGoodWithDogs = 1
    if nokids: a.IsGoodWithChildren = 1
    if nocats: a.IsGoodWithCats = 1
    a.AnimalComments = description
    a.HiddenAnimalDetails = "original breed: " + breed1 + " " + breed2 + ", hasshots: " + str(hasshots)
    # Now do the dbfs and media inserts for any photos
    preferred = 1
    for encoded in encodedjpgdata:
        medianame = str(mediaid) + '.jpg'
        print "INSERT INTO media (id, medianame, medianotes, websitephoto, docphoto, newsincelastpublish, updatedsincelastpublish, " \
            "excludefrompublish, linkid, linktypeid, recordversion, date) VALUES (%d, '%s', %s, %d, %d, 0, 0, 0, %d, 0, 0, %s);" % \
            ( mediaid, medianame, asm.ds(description), preferred, preferred, a.ID, asm.dd(datetime.datetime.today()) )
        print "INSERT INTO dbfs (id, name, path, content) VALUES (%d, '%s', '%s', '');" % ( dbfsid, str(a.ID), '/animal' )
        dbfsid += 1
        print "INSERT INTO dbfs (id, name, path, content) VALUES (%d, '%s', '%s', '%s');" % (dbfsid, medianame, "/animal/" + str(a.ID), encoded)
        preferred = 0
        mediaid += 1
        dbfsid += 1
    # If there's a video link, create a media link record for it
    petvideo = rjs("pet_video_link")
    yts = petvideo.find("//www.youtube.com")
    if petvideo != "" and yts != -1:
        youtube = petvideo[yts:petvideo.find("\"", yts)]
        sys.stderr.write("youtube: " + youtube + "\n")
        print "INSERT INTO media (id, medianame, medianotes, websitevideo, websitephoto, docphoto, newsincelastpublish, updatedsincelastpublish, " \
            "excludefrompublish, mediatype, linkid, linktypeid, recordversion, date) VALUES (%d, '%s', %s, %d, %d, %d, 0, 0, 0, %d, %d, 0, 0, %s);" % \
            ( mediaid, youtube, asm.ds("Video"), 1, 0, 0, 2, a.ID, asm.dd(datetime.datetime.today()) )
        mediaid += 1
    # If the animal is adopted, send it to our unknown owner
    if adopted:
        m = asm.Movement(nextmoveid)
        nextmoveid += 1
        m.OwnerID = o.ID
        m.AnimalID = a.ID
        m.MovementDate = broughtin + datetime.timedelta(days = 1)
        m.MovementType = 1
        print m
        a.ActiveMovementType = m.MovementType
        a.ActiveMovementDate = m.MovementDate
        a.ActiveMovementID = m.ID
        a.Archived = 1
    print a

# Now follow each link to get the animal details page and extract info
print "\\set ON_ERROR_STOP\nBEGIN;"

for idx, pfid in enumerate(ADOPTABLE_IDS):
    sys.stderr.write("on shelter %d of %d\n" % (idx, len(ADOPTABLE_IDS)))
    pfimport(pfid, False)

for idx, pfid in enumerate(ADOPTED_IDS):
    sys.stderr.write("adopted %d of %d\n" % (idx, len(ADOPTED_IDS)))
    pfimport(pfid, True)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

