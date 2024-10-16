#!/usr/bin/python

import asm, csv, urllib2, re, sys, base64, datetime, json

"""
Import module for PetFinder data. 
Uses their api v2 with oauth to import adoptable animals.

Not sure how long this api/secret will last and whether it's compatible with 
other shelters - it was generated for the shelter_id below.
"""

DEFAULT_BREED = 261 # default to dsh
#DEFAULT_BREED = 30 # default to black lab

SHELTER_ID = "NC675" 
API_KEY = "wbYkzzcnp9bqh7U6J51sXrfCXTvDAkQjd73N7SsrZBnwFbpuPj"
SECRET_KEY = "kpYuCm9siJI0GbaY3OueUOzXtOyzzKhn827UQrjB"

URL = "http://api.petfinder.com/v2/animals?organization=" + SHELTER_ID + "&page=1&limit=100&status=adoptable"

START_ID = 500

animals = []
movements = []
owners = []

def getdate(s):
    return asm.getdate_yyyymmdd(s)

def nte(s):
    if s is None: return ""
    return s

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

asm.setid("animal", START_ID)
asm.setid("media", START_ID)
asm.setid("dbfs", START_ID)
asm.setid("owner", START_ID)
asm.setid("adoption", START_ID)

print "\\set ON_ERROR_STOP\nBEGIN;"
print "DELETE FROM animal WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM owner WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM adoption WHERE ID >= %s AND CreatedBy = 'conversion';" % START_ID
print "DELETE FROM media WHERE ID >= %s;" % START_ID
print "DELETE FROM dbfs WHERE ID >= %s;" % START_ID

# Create an unknown owner
uo = asm.Owner()
owners.append(uo)
uo.OwnerSurname = "Unknown Owner"
uo.OwnerName = uo.OwnerSurname


# Call the API to get the pet list
r = asm.post_data("https://api.petfinder.com/v2/oauth2/token", "grant_type=client_credentials&client_id=" + API_KEY + "&client_secret=" + SECRET_KEY)
access_token = json.loads(r["response"])["access_token"]

data = asm.get_url(URL, headers={"Authorization": "Bearer " + access_token})
rows = json.loads(data["response"])["animals"]

asm.stderr("processing %d animals" % len(rows))

for r in rows:

    asm.stderr(r)

    broughtin = getdate(r["published_at"])
    if broughtin is None: broughtin = asm.today()
    petid = nte(r["id"])
    name = nte(r["name"])
    breed1 = nte(r["breeds"]["primary"])
    breed2 = nte(r["breeds"]["secondary"])
    crossbreed = r["breeds"]["mixed"]
    species = nte(r["species"])
    color = nte(r["colors"]["primary"])
    size = nte(r["size"])
    coat = nte(r["coat"])
    age = nte(r["age"])
    sex = nte(r["gender"])
    description = nte(r["description"])
    description = asm.strip_unicode(description)
    description = description.replace("&#39;", "'").replace("&quot;", "\"").replace("&apos;", "'").replace("&nbsp;", " ")
    neutered = r["attributes"]["spayed_neutered"]
    hasshots = r["attributes"]["shots_current"]
    declawed = r["attributes"]["declawed"]
    specialneeds = r["attributes"]["special_needs"]
    housetrained = r["attributes"]["house_trained"]
    nocats = not r["environment"]["cats"]
    nodogs = not r["environment"]["dogs"]
    nokids = not r["environment"]["children"]

    # Dump animal info to console
    #deb = u"petid: %s, name: %s, species: %s, breed1: %s, breed2: %s, crossbreed: %s, size: %s, age: %s, sex: %s, neutered: %s, hasshots: %s, specialneeds: %s, declawed: %s, housetrained: %s, nocats: %s, nodogs: %s, nokids: %s\ndescription: %s\n" % (
    #    petid, name, species, breed1, breed2, crossbreed, size, age, sex, neutered, hasshots, specialneeds, declawed, housetrained, nocats, nodogs, nokids, description)
    #sys.stderr.write(deb)

    # Build our animal record
    a = asm.Animal()
    animals.append(a)
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

    # Grab all the animal's images
    for p in r["photos"]:
        url = p["large"]
        asm.stderr("retrieving photo from '%s'" % url)
        imdata = asm.load_image_from_url(url)
        asm.animal_image(a.ID, imdata)

    # If the animal is adopted, send it to our unknown owner
    if r["status"] == "adopted":
        movements.append( asm.adopt_to(a, uo.ID) )

# Now that everything else is done, output stored records
for a in animals:
    print a
for o in owners:
    print o
for m in movements:
    print m

#asm.stderr_allanimals(animals)
#asm.stderr_onshelter(animals)
asm.stderr_summary(animals=animals, owners=owners, movements=movements)

print "DELETE FROM configuration WHERE ItemName LIKE 'DBView%';"
print "COMMIT;"

