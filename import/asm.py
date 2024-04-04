#!/usr/bin/python

"""
ASM modules. Supplies objects representing ASM entities that can write
SQL to generate themselves. Objects are basically the SQL tables, but with
sane defaults already completed and ID generation handled.

Eg:

    a = asm.Animal() # Empty constructor generates ID
    a.AnimalName = "Socks"
    print(a)

Also has some extra functions for grabbing functions from PetFinder:

Eg:
    page = petfinder_get_adoptable("NC500")
    petfinder_image(page, "Rover")

    (prints media/dbfs INSERTS after getting Rover's petid and
     downloading primary image and base64 encoding it)
     
Also has some useful helper functions for reading CSVs and parsing values, eg:

    asm.atoi(string)
    asm.cint(string)
    asm.cfloat(string)
    asm.csv_to_list(filename)
    asm.get_currency
    asm.getdate_yyyymmdd (and variants)
    asm.getsex_mf
    asm.now()
    asm.nulltostr()
    asm.regex(findin, pattern)
    asm.subtract_days, asm.add_days
    asm.fw (first word)
    asm.iif (inline if, eg: iif(condition, true, false))
    asm.md5(s)
    asm.spaceleft(s, length)
    asm.spaceright(s, length)
    asm.padleft(s, length)
    asm.padright(s, length)
    asm.truncate(s, length)
    asm.find_row (list_of_dicts, fieldname, value)
    asm.find_value (list_of_dicts, fieldname, value, fieldtoreturn)
    asm.animal_image(animalid, imagedata)
    asm.adopt_to(a, ownerid)
    asm.load_image_from_file(filename)
    asm.stderr()
    
"""

import csv, datetime, re, time
import os, sys, base64, requests

try:
    import dbfread
    """ when faced with a field type it doesn't understand, dbfread can produce an error
        'Unknown field type xx'. This parser returns anything unrecognised as binary data """
    class ExtraFieldParser(dbfread.FieldParser):
        def parse(self, field, data):
            try:
                return dbfread.FieldParser.parse(self, field, data)
            except ValueError:
                return data
except:
    pass

if sys.version_info[0] > 2: # PYTHON3
    import urllib.request as urllib2
    from io import StringIO
else:
    import urllib2
    from cStringIO import StringIO

# Next year code to use for animals when generating shelter codes
nextyearcode = 1

# Dictionary of tables and next ID
ids = {}

# Dictionary of jurisdictions
jurisdictions = {}

# Dictionary of locations
locations = {}

# Dictionary of pickup locations
pickuplocations = {}

# Dictionary of custom colours if we're going to supply a new set
customcolours = {}

# media files written
mediafilescount = 0
mediafilesbytes = 0

# See end of file for dictionaries of lookups that require classes

def atoi(s):
    """ Returns an integer based on only the numeric
        portion of a string like the C lib atoi function """
    try:
        return int("".join(re.findall(r'[\d-]',s)))
    except:
        return 0

def atof(s):
    """ Returns a float based on only the numeric
        portion of a string like the C lib atoi function """
    try:
        return float("".join(re.findall(r'[\d-]',s)))
    except:
        return 0

def csv_to_list(fname, strip = False, remove_bom = True, remove_control = False, remove_non_ascii = False, uppercasekeys = False, unicodehtml = False, encoding="utf-8-sig"):
    """
    Reads the csv file fname and returns it as a list of maps 
    with the first row used as the keys. Uses utf-8-sig to ignore any BOM
    strip: If True, removes whitespace from all fields
    remove_control: If True, removes all ascii chars < 32
    remove_non_ascii: If True, removes all ascii chars < 32 or > 127
    uppercasekeys: If True, runs upper() on headings/map keys
    unicodehtml: If True, interprets the file as utf8 and replaces unicode chars with HTML entities
    returns a list of maps
    returns None if the file does not exist
    """
    if not os.path.exists(fname): return None
    o = []
    # Read the file into memory buffer b first
    # any raw transformations can be done on it there
    b = StringIO()
    with open(fname, "r", encoding=encoding) as f:
        for s in f.readlines():
            if remove_bom:
                s = s.replace("\ufeff", "")
            if remove_control:
                s = ''.join(c for c in s if ord(c) >= 32) + "\n"
            if remove_non_ascii:
                s = ''.join(c for c in s if ord(c) >= 32 and ord(c) <= 127) + "\n"
            if unicodehtml:
                s = s.encode("ascii", "xmlcharrefreplace").decode("ascii")
            b.write(s)
        f.close()
    reader = csv.DictReader(StringIO(b.getvalue()))
    for row in reader:
        if strip:
            for k, v in row.items():
                row[k] = v.strip()
        if uppercasekeys:
            row = {k.upper(): v for k, v in row.items()}
        o.append(row)
    return o

def csv_to_list_cols(fname, cols, strip = False, remove_control = False, uppercasekeys = False, unicodehtml = False):
    """
    Reads the csv file fname and returns it as a list of maps 
    with cols used as the keys.
    strip: If True, removes whitespace from all fields
    remove_control: If True, removes all ascii chars < 32
    uppercasekeys: If True, runs upper() on headings/map keys
    unicodehtml: If True, interprets the file as utf8 and replaces unicode chars with HTML entities
    returns a list of maps
    returns None if the file does not exist
    """
    if not os.path.exists(fname): return None
    o = []
    # Read the file into memory buffer b first
    # any raw transformations can be done on it there
    b = StringIO()
    with open(fname, "rb") as f:
        for s in f.readlines():
            if remove_control:
                b.write(''.join(c for c in s if ord(c) >= 32))
                b.write("\n")
            elif unicodehtml:
                b.write(s.decode("utf8").encode("ascii", "xmlcharrefreplace"))
            else:
                b.write(s)
        f.close()
    reader = csv.DictReader(StringIO(b.getvalue()), cols)
    for row in reader:
        if strip:
            for k, v in row.iteritems():
                row[k] = v.strip()
        if uppercasekeys:
            row = {k.upper(): v for k, v in row.iteritems()}
        o.append(row)
    return o

def read_dbf(name, encoding="cp1252"):
    return dbfread.DBF(name, encoding=encoding, parserclass=ExtraFieldParser)

def cint(s):
    try:
        return int(s)
    except:
        return 0

def cfloat(s):
    try:
        return float(s)
    except:
        return 0.0

def good_with(s):
    """ Returns 0 = unknown, 1 = no, 2 = yes for good with fields """
    if s.lower().find("no") != -1: return 1
    if s.lower().find("yes") != -1: return 2
    return 0

def get_currency(s):
    if s is None: return 0
    if type(s) == int or type(s) == float: return int(s * 100)
    if s.strip() == "": return 0
    s = s.replace("$", "")
    s = s.replace("&nbsp;", "")
    try:
        return int(float(s) * 100)
    except:
        return 0

def nulltostr(s):
    if s is None: 
        return ""
    else:
        return s

def file_exists(f):
    return os.path.exists(f)

def fw(s):
    """ returns the first word """
    if s is None: return s
    if s.find(" ") == -1: return s
    return s.split(" ", 2)[0]

def remove_time(s):
    if s is None: return s
    if s.find(" ") == -1:
        return s
    return s.split(" ")[0]

def remove_seconds(s):
    if s is None: return s
    if s.find(" ") == -1:
        return s
    b = s.split(" ", 1)
    d = b[0]
    t = b[1]
    if t.find(":") != -1:
        t = t[0:5]
    return d + " " + t

def format_date(d, f):
    try:
        return d.strftime(f)
    except:
        return ""

def parse_date(s, f):
    try:
        return datetime.datetime.strptime(s, f)
    except:
        return None

def getdate_guess(s):
    """ Attempts to guess the date from multiple formats, eg:
        25/08/2015, 5-3-17
        It will assume US format and the year in third position unless obvious (4 digit year in first pos)
        If the year is under 2000, makes it 4 digit.
    """
    if s is None or s == "" or s.find("N/A") != -1 or s.find("NA") != -1 or s.find("TBA") != -1 or s.find("TBD") != -1: return None
    if s.find(" ") > -1: s = s[0:s.find(" ")]
    b = s.split("/")
    if s.find("-") != -1:
        b = s.split("-")
    if len(b) < 3: return None
    m = cint(b[0])
    d = cint(b[1])
    y = cint(b[2])
    if m > 1000:
        # it's ymd
        y = cint(b[0])
        m = cint(b[1])
        d = cint(b[2])
    elif m > 12:
        # it's dmy
        d = cint(b[0])
        m = cint(b[1])
        y = cint(b[2])
    if y < 2000: y += 2000
    if y == 0 or m == 0: return None
    try:
        return datetime.datetime(y, m, d)
    except Exception as err:
        stderr("bad data: %s" % s)
        raise err

def getdate_yyyymmdd(s):
    s = remove_time(s)
    return parse_date(s, "%Y/%m/%d")

def getdate_mmddyyyy(s):
    s = remove_time(s)
    return parse_date(s, "%m/%d/%Y")

def getdate_mmddyy(s):
    s = remove_time(s)
    return parse_date(s, "%m/%d/%y")

def getdate_ddmmyy(s):
    s = remove_time(s)
    return parse_date(s, "%d/%m/%y")

def getdate_ddmmyyyy(s):
    s = remove_time(s)
    return parse_date(s, "%d/%m/%Y")

def getdate_ddmmmyy(s):
    s = remove_time(s)
    return parse_date(s, "%d-%b-%y")

def getdate_jackcess(s):
    """ Parses dates in the Jackcess format: Thu Apr 23 00:00:00 BST 2015 """
    return parse_date(s, "%a %b %d %H:%M:%S %Z %Y")

def getdate_iso(s):
    s = remove_time(s)
    return parse_date(s, "%Y-%m-%d")

def getdatetime_iso(s, defyear = "15"):
    s = remove_seconds(s)
    return parse_date(s, "%Y-%m-%d %H:%M")

def getsex_mf(s):
    if s is None: return 0
    if s.lower().startswith("m"):
        return 1
    elif s.lower().startswith("f"):
        return 0
    else:
        return 2

def now():
    return datetime.datetime.today()

def today():
    """ Returns today as a Python date """
    return datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

def stderr(s):
    sys.stderr.write("%s\n" % s)

def stderr_onshelter(animals=[]):
    for a in animals:
        if a.Archived == 0:
            stderr(a.infoLine())

def stderr_summary(animals=[], animalmedicals=[], animalvaccinations=[], animaltests=[], owners=[], ownerlicences=[], ownerdonations=[], animalcontrol=[], movements=[], logs=[], stocklevels=[], waitinglists=[]):
    def o(l, d):
        if len(l) > 0:
            stderr("%d %s" % (len(l), d))
    if len(animals) != 0:
        onshelter = 0
        offshelter = 0
        nonshelter = 0
        dead = 0
        euth = 0
        dupcodes = 0
        codes = set()
        dups = []
        errors = []
        for a in animals:
            if a.ShelterCode in codes: 
                dupcodes += 1
                dups.append(a.ShelterCode)
            codes.add(a.ShelterCode)
            if a.Archived == 0:
                onshelter += 1
            elif a.Archived == 1 and a.NonShelterAnimal == 1:
                nonshelter += 1
            elif a.Archived == 1 and a.DeceasedDate is None:
                offshelter += 1
            elif a.DeceasedDate is not None and a.PutToSleep == 0:
                dead += 1
            elif a.DeceasedDate is not None and a.PutToSleep == 1:
                euth += 1
            if a.DateBroughtIn is None:
                errors.append("ERROR: %s %s - DateBroughtIn is None" % (a.AnimalName, a.ShelterCode))
            if a.DateOfBirth is None:
                errors.append("ERROR: %s %s - DateOfBirth is None" % (a.AnimalName, a.ShelterCode))
        stderr("%d animals (%d on-shelter, %d off-shelter, %d non-shelter, %d dead, %d euthanised)" % (len(animals), onshelter, offshelter, nonshelter, dead, euth))
        if dupcodes > 0:
            stderr("WARNING: %d duplicate shelter codes (%s .. %s)" % (dupcodes, dups[0], dups[-1]))
        if len(errors) > 0:
            stderr("\n".join(errors))
            stderr("\n%s errors found." % len(errors))
    o(animalmedicals, "medicals")
    o(animalvaccinations, "vaccinations")
    o(animaltests, "tests")
    o(owners, "people")
    o(logs, "logs")
    o(movements, "movements")
    o(ownerlicences, "licences")
    o(ownerdonations, "payments")
    o(animalcontrol, "incidents")
    o(stocklevels, "stock levels")
    o(waitinglists, "waiting list entries")
    if mediafilescount > 0:
        stderr("%d media files (%d bytes)" % (mediafilescount, mediafilesbytes))

# List of default colours
colours = (
("1","Black"),
("2","White"),
("3","Black and White"),
("4","Ginger"),
("4","Orange"),
("5","White and Black"),
("6","Tortie"),
("7","Tabby"),
("8","Tan"),
("9","Black and Tan"),
("10","Tan and Black"),
("11","Brown"),
("12","Brown and Black"),
("13","Black and Brown"),
("14","Brindle"),
("15","Brindle and Black"),
("16","Brindle and White"),
("17","Black and Brindle"),
("18","White and Brindle"),
("19","Tricolour"),
("20","Liver"),
("21","Liver and White"),
("22","White and Liver"),
("23","Cream"),
("24","Tan and White"),
("26","White and Tan"),
("27","Tortie and White"),
("28","Tabby and White"),
("29","Ginger and White"),
("30","Grey"),
("31","Grey and White"),
("32","White and Grey"),
("33","White and Torti"),
("35","Brown and White"),
("36","Blue"),
("37","White and Tabby"),
("38","Yellow and Grey"),
("39","Various"),
("40","White and Brown"),
("41","Green"),
("42","Amber"),
("43","Black Tortie"),
("44","Blue Tortie"),
("45","Chocolate"),
("46","Chocolate Tortie"),
("47","Cinnamon"),
("48","Cinnamon Tortoiseshell"),
("49","Fawn"),
("50","Fawn Tortoiseshell"),
("51","Golden"),
("52","Light Amber"),
("53","Lilac"),
("54","Lilac Tortie"),
("55","Ruddy"),
("56","Seal"),
("57","Silver"),
("58","Sorrel"),
("59","Sorrel Tortoiseshell")
)

def colour_id_for_name(name, firstWordOnly = False, default = 1):
    if name is None: return default
    if firstWordOnly:
        if name.find(" ") != -1: name = name[0:name.find(" ")]
        if name.find("/") != -1: name = name[0:name.find("/")]
    for cid, cname in colours:
        if cname.upper().find(name.upper()) != -1:
            return int(cid)
    return default

def colour_id_for_names(name1, name2, default = 1):
    if name1 == name2 or name2.strip() == "" or name2.lower() == "unknown" or name2.lower() == "n/a":
        return colour_id_for_name(name1, True)
    for cid, cname in colours:
        if cname.upper().find(name1.upper()) != -1 and cname.upper().find(name2.upper()) != -1:
            return int(cid)
    return default

def colour_from_db(name, default = 1):
    """ Looks up the colour in the db when the conversion is run, assign to BaseColourID """
    return "COALESCE((SELECT ID FROM basecolour WHERE lower(BaseColour) LIKE lower('%s') LIMIT 1), %d)" % (name.strip(), default)

def colour_name_for_id(id, default = "Black"):
    for cid, cname in colours:
        if int(cid) == id:
            return cname
    return default

# List of default species
species = (
("1","Dog"),
("1","Canine"),
("2","Cat"),
("2","Feline"),
("3","Bird"),
("4","Mouse"),
("5","Rat"),
("6","Hedgehog"),
("7","Rabbit"),
("8","Dove"),
("9","Ferret"),
("10","Chinchilla"),
("11","Snake"),
("12","Tortoise"),
("13","Terrapin"),
("14","Chicken"),
("15","Owl"),
("16","Goat"),
("17","Goose"),
("18","Gerbil"),
("19","Cockatiel"),
("20","Guinea Pig"),
("21","Goldfish"),
("22","Hamster"),
("23","Camel"),
("24","Horse"),
("24","Equine"),
("25","Pony"),
("26","Donkey"),
("27","Llama"),
("28","Pig")
)

def species_id_for_name(name):
    if name is None: return 1
    for sid, sname in species:
        if sname.upper().find(name.upper()) != -1:
            return int(sid)
    return 1

def species_name_for_id(id):
    for sid, sname in species:
        if int(sid) == id:
            return sname
    return "Dog"

def species_from_db(name, default = 1):
    """ Looks up the species in the db when the conversion is run, assign to SpeciesID """
    return "COALESCE((SELECT ID FROM species WHERE lower(SpeciesName) LIKE lower('%s') LIMIT 1), %d)" % (name.strip(), default)

# These are breed keywords to match commonly used breeds
breedkeywords = (
("13", "Cattle"),
("30", "Lab"),
("30", "Labrador"),
("34", "Collie"),
("73", "Bulldog"),
("92", "Shep"),
("92", "Shepherd"),
("92", "Shepard"),
("103", "Hound"),
("157", "Pit"),
("199", "Terrier"),
("178", "Schnauzer"),
("219", "Yorkie"),
("243", "Long"),
("243", "DLH"),
("252", "Medium"),
("252", "DMH"),
("261", "Short"),
("261", "DSH")
)

# List of default breeds
breeds = (
("1","Affenpinscher"),
("2","Afghan Hound"),
("3","Airedale Terrier"),
("4","Akbash"),
("5","Akita"),
("6","Alaskan Malamute"),
("7","American Bulldog"),
("8","American Eskimo Dog"),
("9","American Staffordshire Terrier"),
("10","American Water Spaniel"),
("11","Anatolian Shepherd"),
("12","Appenzell Mountain Dog"),
("13","Australian Cattle Dog/Blue Heeler"),
("14","Australian Kelpie"),
("15","Australian Shepherd"),
("16","Australian Terrier"),
("17","Basenji"),
("18","Basset Hound"),
("19","Beagle"),
("20","Bearded Collie"),
("21","Beauceron"),
("22","Bedlington Terrier"),
("23","Belgian Shepherd Dog Sheepdog"),
("24","Belgian Shepherd Laekenois"),
("25","Belgian Shepherd Malinois"),
("26","Belgian Shepherd Tervuren"),
("27","Bernese Mountain Dog"),
("28","Bichon Frise"),
("29","Black and Tan Coonhound"),
("30","Black Labrador Retriever"),
("31","Black Mouth Cur"),
("32","Bloodhound"),
("33","Bluetick Coonhound"),
("34","Border Collie"),
("35","Border Terrier"),
("36","Borzoi"),
("37","Boston Terrier"),
("38","Bouvier des Flanders"),
("39","Boykin Spaniel"),
("40","Boxer"),
("41","Briard"),
("42","Brittany Spaniel"),
("43","Brussels Griffon"),
("44","Bull Terrier"),
("45","Bullmastiff"),
("46","Cairn Terrier"),
("47","Canaan Dog"),
("48","Cane Corso Mastiff"),
("49","Carolina Dog"),
("50","Catahoula Leopard Dog"),
("51","Cattle Dog"),
("52","Cavalier King Charles Spaniel"),
("53","Chesapeake Bay Retriever"),
("54","Chihuahua"),
("55","Chinese Crested Dog"),
("56","Chinese Foo Dog"),
("57","Chocolate Labrador Retriever"),
("58","Chow Chow"),
("59","Clumber Spaniel"),
("60","Cockapoo"),
("61","Cocker Spaniel"),
("62","Collie"),
("63","Coonhound"),
("64","Corgi"),
("65","Coton de Tulear"),
("66","Dachshund"),
("67","Dalmatian"),
("68","Dandi Dinmont Terrier"),
("69","Doberman Pinscher"),
("70","Dogo Argentino"),
("71","Dogue de Bordeaux"),
("72","Dutch Shepherd"),
("73","English Bulldog"),
("74","English Cocker Spaniel"),
("75","English Coonhound"),
("76","English Pointer"),
("77","English Setter"),
("78","English Shepherd"),
("79","English Springer Spaniel"),
("80","English Toy Spaniel"),
("81","Entlebucher"),
("82","Eskimo Dog"),
("83","Field Spaniel"),
("84","Fila Brasileiro"),
("85","Finnish Lapphund"),
("86","Finnish Spitz"),
("87","Flat-coated Retriever"),
("88","Fox Terrier"),
("89","Foxhound"),
("90","French Bulldog"),
("91","German Pinscher"),
("92","German Shepherd Dog"),
("92","GSD"),
("93","German Shorthaired Pointer"),
("94","German Wirehaired Pointer"),
("95","Glen of Imaal Terrier"),
("96","Golden Retriever"),
("97","Gordon Setter"),
("98","Great Dane"),
("99","Great Pyrenees"),
("100","Greater Swiss Mountain Dog"),
("101","Greyhound"),
("102","Havanese"),
("103","Hound"),
("104","Hovawart"),
("105","Husky"),
("106","Ibizan Hound"),
("107","Illyrian Sheepdog"),
("108","Irish Setter"),
("109","Irish Terrier"),
("110","Irish Water Spaniel"),
("111","Irish Wolfhound"),
("112","Italian Greyhound"),
("113","Italian Spinone"),
("114","Jack Russell Terrier"),
("115","Japanese Chin"),
("116","Jindo"),
("117","Kai Dog"),
("118","Karelian Bear Dog"),
("119","Keeshond"),
("120","Kerry Blue Terrier"),
("121","Kishu"),
("122","Komondor"),
("123","Kuvasz"),
("124","Kyi Leo"),
("125","Labrador Retriever"),
("126","Lakeland Terrier"),
("127","Lancashire Heeler"),
("128","Lhasa Apso"),
("129","Leonberger"),
("130","Lowchen"),
("131","Maltese"),
("132","Manchester Terrier"),
("133","Maremma Sheepdog"),
("134","Mastiff"),
("135","McNab"),
("136","Miniature Pinscher"),
("137","Mountain Cur"),
("138","Mountain Dog"),
("139","Munsterlander"),
("140","Neapolitan Mastiff"),
("141","New Guinea Singing Dog"),
("142","Newfoundland Dog"),
("143","Norfolk Terrier"),
("144","Norwich Terrier"),
("145","Norwegian Buhund"),
("146","Norwegian Elkhound"),
("147","Norwegian Lundehund"),
("148","Nova Scotia Duck-Tolling Retriever"),
("149","Old English Sheepdog"),
("150","Otterhound"),
("151","Papillon"),
("152","Patterdale Terrier (Fell Terrier)"),
("153","Pekingese"),
("154","Peruvian Inca Orchid"),
("155","Petit Basset Griffon Vendeen"),
("156","Pharaoh Hound"),
("157","Pit Bull Terrier"),
("157","Pitbull Terrier"),
("157","Pitbull"),
("158","Plott Hound"),
("159","Portugese Podengo"),
("160","Pointer"),
("161","Polish Lowland Sheepdog"),
("162","Pomeranian"),
("163","Poodle"),
("164","Portuguese Water Dog"),
("165","Presa Canario"),
("166","Pug"),
("167","Puli"),
("168","Pumi"),
("169","Rat Terrier"),
("170","Redbone Coonhound"),
("171","Retriever"),
("172","Rhodesian Ridgeback"),
("173","Rottweiler"),
("174","Saluki"),
("175","Saint Bernard St. Bernard"),
("176","Samoyed"),
("177","Schipperke"),
("178","Schnauzer"),
("179","Scottish Deerhound"),
("180","Scottish Terrier Scottie"),
("181","Sealyham Terrier"),
("182","Setter"),
("183","Shar Pei"),
("184","Sheep Dog"),
("185","Shepherd"),
("186","Shetland Sheepdog Sheltie"),
("187","Shiba Inu"),
("188","Shih Tzu"),
("189","Siberian Husky"),
("190","Silky Terrier"),
("191","Skye Terrier"),
("192","Sloughi"),
("193","Smooth Fox Terrier"),
("194","Spaniel"),
("195","Spitz"),
("196","Staffordshire Bull Terrier"),
("197","South Russian Ovcharka"),
("198","Swedish Vallhund"),
("199","Terrier"),
("200","Thai Ridgeback"),
("201","Tibetan Mastiff"),
("202","Tibetan Spaniel"),
("203","Tibetan Terrier"),
("204","Tosa Inu"),
("205","Toy Fox Terrier"),
("206","Treeing Walker Coonhound"),
("207","Vizsla"),
("208","Weimaraner"),
("209","Welsh Corgi"),
("210","Welsh Terrier"),
("211","Welsh Springer Spaniel"),
("212","West Highland White Terrier Westie"),
("213","Wheaten Terrier"),
("214","Whippet"),
("215","White German Shepherd"),
("216","Wire-haired Pointing Griffon"),
("217","Wirehaired Terrier"),
("218","Yellow Labrador Retriever"),
("219","Yorkshire Terrier Yorkie"),
("220","Xoloitzcuintle/Mexican Hairless"),
("221","Abyssinian"),
("222","American Curl"),
("223","American Shorthair"),
("224","American Wirehair"),
("225","Applehead Siamese"),
("226","Balinese"),
("227","Bengal"),
("228","Birman"),
("229","Bobtail"),
("230","Bombay"),
("231","British Shorthair"),
("232","Burmese"),
("233","Burmilla"),
("234","Calico"),
("235","Canadian Hairless"),
("236","Chartreux"),
("237","Chinchilla"),
("238","Cornish Rex"),
("239","Cymric"),
("240","Devon Rex"),
("243","Domestic Long Hair"),
("243","Domestic Semi L/H"),
("243","DLH"),
("252","Domestic Medium Hair"),
("252","DMH"),
("261","Domestic Short Hair"),
("261","DSH"),
("261","Tabby"),
("271","Egyptian Mau"),
("272","Exotic Shorthair"),
("273","Extra-Toes Cat (Hemingway Polydactyl)"),
("274","Havana"),
("275","Himalayan"),
("276","Japanese Bobtail"),
("277","Javanese"),
("278","Korat"),
("279","Maine Coon"),
("280","Manx"),
("281","Munchkin"),
("282","Norwegian Forest Cat"),
("283","Ocicat"),
("284","Oriental Long Hair"),
("285","Oriental Short Hair"),
("286","Oriental Tabby"),
("287","Persian"),
("288","Pixie-Bob"),
("289","Ragamuffin"),
("290","Ragdoll"),
("291","Russian Blue"),
("292","Scottish Fold"),
("293","Selkirk Rex"),
("294","Siamese"),
("295","Siberian"),
("296","Singapura"),
("297","Snowshoe"),
("298","Somali"),
("299","Sphynx (hairless cat)"),
("307","Tiger"),
("308","Tonkinese"),
("311","Turkish Angora"),
("312","Turkish Van"),
("314","American"),
("315","American Fuzzy Lop"),
("316","American Sable"),
("317","Angora Rabbit"),
("318","Belgian Hare"),
("319","Beveren"),
("320","Britannia Petite"),
("321","Bunny Rabbit"),
("322","Californian"),
("323","Champagne DArgent"),
("324","Checkered Giant"),
("325","Chinchilla"),
("326","Cinnamon"),
("327","Creme DArgent"),
("328","Dutch"),
("329","Dwarf"),
("330","Dwarf Eared"),
("331","English Lop"),
("332","English Spot"),
("333","Flemish Giant"),
("334","Florida White"),
("335","French-Lop"),
("336","Harlequin"),
("337","Havana"),
("338","Himalayan"),
("339","Holland Lop"),
("340","Hotot"),
("341","Jersey Wooly"),
("342","Lilac"),
("343","Lop Eared"),
("344","Mini-Lop"),
("345","Mini Rex"),
("346","Netherland Dwarf"),
("347","New Zealand"),
("348","Palomino"),
("349","Polish"),
("350","Rex"),
("351","Rhinelander"),
("352","Satin"),
("353","Silver"),
("354","Silver Fox"),
("355","Silver Marten"),
("356","Tan"),
("357","Appaloosa"),
("358","Arabian"),
("359","Clydesdale"),
("360","Donkey/Mule"),
("361","Draft"),
("362","Gaited"),
("363","Grade"),
("364","Missouri Foxtrotter"),
("365","Morgan"),
("366","Mustang"),
("367","Paint/Pinto"),
("368","Palomino"),
("369","Paso Fino"),
("370","Percheron"),
("371","Peruvian Paso"),
("372","Pony"),
("373","Quarterhorse"),
("374","Saddlebred"),
("375","Standardbred"),
("376","Thoroughbred"),
("377","Tennessee Walker"),
("378","Warmblood"),
("379","Chinchilla"),
("380","Ferret"),
("381","Gerbil"),
("382","Guinea Pig"),
("383","Hamster"),
("384","Hedgehog"),
("385","Mouse"),
("386","Prairie Dog"),
("387","Rat"),
("388","Skunk"),
("389","Sugar Glider"),
("390","Pot Bellied"),
("391","Vietnamese Pot Bellied"),
("392","Gecko"),
("393","Iguana"),
("394","Lizard"),
("395","Snake"),
("396","Turtle"),
("397","Fish"),
("398","African Grey"),
("399","Amazon"),
("400","Brotogeris"),
("401","Budgie/Budgerigar"),
("402","Caique"),
("403","Canary"),
("404","Chicken"),
("405","Cockatiel"),
("406","Cockatoo"),
("407","Conure"),
("408","Dove"),
("409","Duck"),
("410","Eclectus"),
("411","Emu"),
("412","Finch"),
("413","Goose"),
("414","Guinea fowl"),
("415","Kakariki"),
("416","Lory/Lorikeet"),
("417","Lovebird"),
("418","Macaw"),
("419","Mynah"),
("420","Ostrich"),
("421","Parakeet (Other)"),
("422","Parrot (Other)"),
("423","Parrotlet"),
("424","Peacock/Pea fowl"),
("425","Pheasant"),
("426","Pigeon"),
("427","Pionus"),
("428","Poicephalus/Senegal"),
("429","Quaker Parakeet"),
("430","Rhea"),
("431","Ringneck/Psittacula"),
("432","Rosella"),
("433","Softbill (Other)"),
("434","Swan"),
("435","Toucan"),
("436","Turkey"),
("437","Cow"),
("438","Goat"),
("439","Sheep"),
("440","Llama"),
("441","Pig (Farm)"),
("442","Mixed Breed")
)

def breed_id_for_name(name, default = 1):
    if name is None: return default
    if name.find(" x") != -1 or name.find(" X") != -1:
        name = name.replace(" x", "").replace(" X", "")
    # try a complete match first
    for bid, bname in breeds:
        if bname.upper() == name.upper():
            return int(bid)
    # now do keyword matching to see if any are present in the breed given
    for bid, bname in breedkeywords:
        if name.upper().find(bname.upper()) != -1:
            return int(bid)
    # fall back to looking for the name given in each item in the full breed list
    for bid, bname in breeds:
        if bname.upper().find(name.upper()) != -1 or name.upper().find(bname.upper()) != -1:
            return int(bid)
    return default

def breed_name_for_id(id):
    for bid, bname in breeds:
        if int(bid) == id:
            return bname
    return "Invalid ID"

def breed_name(id1, id2 = None):
    if id2 is None or id2 == 0:
        return breed_name_for_id(id1)
    return breed_name_for_id(id1) + " / " + breed_name_for_id(id2)
   
def breed_ids(a, breed1, breed2 = "", default = 1):
    a.BreedID = breed_id_for_name(breed1, default)
    a.Breed2ID = a.BreedID
    a.BreedName = breed_name_for_id(a.BreedID)
    a.CrossBreed = 0
    if breed2 is not None and breed2.strip() != "":
        a.CrossBreed = 1
        if breed2 == "Mix" or breed2 == "Unknown":
            a.Breed2ID = 442
        else:
            a.Breed2ID = breed_id_for_name(breed2, default)
        if a.Breed2ID == default: a.Breed2ID = 442
        if a.Breed2ID != a.BreedID: 
            a.BreedName = "%s / %s" % ( breed_name_for_id(a.BreedID), breed_name_for_id(a.Breed2ID) )

def breed_from_db(name, default = 2):
    """ Looks up the breed in the db when the conversion is run, assign to BreedID """
    return "COALESCE((SELECT ID FROM breed WHERE lower(BreedName) LIKE lower('%s') LIMIT 1), %d)" % (name.strip(), default)

def coattype_from_db(name, default = 1):
    """ Looks up the size in the db when the conversion is run, assign to animal.CoatType """
    return "COALESCE((SELECT ID FROM lkcoattype WHERE lower(CoatType) LIKE lower('%s') LIMIT 1), %d)" % (name.strip(), default)

def incidenttype_from_db(name, default = 1):
    """ Looks up the type in the db when the conversion is run, assign to IncidentTypeID """
    return "COALESCE((SELECT ID FROM incidenttype WHERE lower(IncidentName) LIKE lower(%s) LIMIT 1), %d)" % (ds(name.strip()), default)

def jurisdiction_id_for_name(name, createIfNotExist = True):
    global jurisdictions
    if name.strip() == "": return 1
    if name in jurisdictions:
        return jurisdictions[name].ID
    else:
        jurisdictions[name] = Jurisdiction(Name=name)
        return jurisdictions[name].ID

def jurisdiction_from_db(name, default = 1):
    """ Looks up the jurisdiction in the db when the conversion is run, assign to JurisdictionID """
    return "COALESCE((SELECT ID FROM jurisdiction WHERE lower(JurisdictionName) LIKE lower('%s') LIMIT 1), %d)" % (name.strip(), default)

def location_id_for_name(name, createIfNotExist = True):
    global locations
    if name.strip() == "": return 1
    if name in locations:
        return locations[name].ID
    else:
        locations[name] = Location(Name=name)
        return locations[name].ID

def location_from_db(name, default = 2):
    """ Looks up the internallocation in the db when the conversion is run, assign to ShelterLocation """
    return "COALESCE((SELECT ID FROM internallocation WHERE lower(LocationName) LIKE lower('%s') LIMIT 1), %d)" % (name.strip().replace("'", "`"), default)

def pickuplocation_id_for_name(name, createIfNotExist = True):
    global pickuplocations
    if name.strip() == "": return 1
    if name in pickuplocations:
        return pickuplocations[name].ID
    else:
        pickuplocations[name] = PickupLocation(Name=name)
        return pickuplocations[name].ID

def pickuplocation_from_db(name, default = 2):
    """ Looks up the pickuplocation in the db when the conversion is run, assign to PickupLocationID """
    return "COALESCE((SELECT ID FROM pickuplocation WHERE lower(LocationName) LIKE lower('%s') LIMIT 1), %d)" % (name.strip(), default)

def customcolour_id_for_name(name, createIfNotExist = True):
    global customcolours
    if name.strip() == "": return 1
    if name in customcolours:
        return customcolours[name].ID
    else:
        customcolours[name] = BaseColour(Name=name)
        return customcolours[name].ID

def entryreason_id_for_name(name, createIfNotExist = True):
    global entryreasons
    if name.strip() == "": return 1
    if name in entryreasons:
        return entryreasons[name].ID
    else:
        entryreasons[name] = EntryReason(Name=name)
        return entryreasons[name].ID

def animaltype_from_db(name, default = 2):
    """ Looks up the animaltype in the db when the conversion is run, assign to AnimalTypeID """
    return "COALESCE((SELECT ID FROM animaltype WHERE lower(AnimalType) LIKE lower('%s') LIMIT 1), %d)" % (name.strip().replace("'", "`"), default)

def entryreason_from_db(name, default = 2):
    """ Looks up the entryreason in the db when the conversion is run, assign to EntryReasonID """
    return "COALESCE((SELECT ID FROM entryreason WHERE lower(ReasonName) LIKE lower('%s') LIMIT 1), %d)" % (name.strip().replace("'", "`"), default)

def size_from_db(name, default = 1):
    """ Looks up the size in the db when the conversion is run, assign to animal.Size """
    return "COALESCE((SELECT ID FROM lksize WHERE lower(Size) LIKE lower('%s') LIMIT 1), %d)" % (name.strip(), default)

def size_id_for_name(name):
    name = name.lower()
    if name.startswith("v") or name.startswith("x"): return 0
    if name.startswith("l"): return 1
    if name.startswith("s"): return 2
    return 3

def donationtype_id_for_name(name, createIfNotExist = True):
    global donationtypes
    if name.strip() == "": return 1
    if name in donationtypes:
        return donationtypes[name].ID
    else:
        donationtypes[name] = DonationType(Name=name)
        return donationtypes[name].ID

def donationtype_from_db(name, default = 2):
    """ Looks up the donationtype in the db when the conversion is run, assign to DonationID """
    return "COALESCE((SELECT ID FROM donationtype WHERE lower(DonationName) LIKE lower('%s') LIMIT 1), %d)" % (name.strip(), default)

def licencetype_from_db(name, default = 1):
    """ Looks up the licencetype in the db when the conversion is run, assign to ownerlicence.LicenceTypeID """
    return "COALESCE((SELECT ID FROM licencetype WHERE lower(LicenceTypeName) LIKE lower('%s') LIMIT 1), %d)" % (name.strip(), default)

def testtype_id_for_name(name, createIfNotExist = True):
    global testtypes
    if name.strip() == "": return 1
    if name in testtypes:
        return testtypes[name].ID
    else:
        testtypes[name] = TestType(Name=name)
        return testtypes[name].ID

def vaccinationtype_from_db(name, default = 1):
    """ Looks up the vaccinationtype in the db when the conversion is run, assign to VaccinationID """
    return "COALESCE((SELECT ID FROM vaccinationtype WHERE lower(VaccinationType) LIKE lower('%s') LIMIT 1), %d)" % (name.strip(), default)

def vaccinationtype_id_for_name(name, createIfNotExist = True):
    global vaccinationtypes
    if name.strip() == "": return 1
    if name in vaccinationtypes:
        return vaccinationtypes[name].ID
    else:
        vaccinationtypes[name] = VaccinationType(Name=name)
        return vaccinationtypes[name].ID

types = (
("2","D (Dog)"),
("10","A (Stray Dog)"),
("11","U (Unwanted Cat)"),
("12","S (Stray Cat)"),
("20","F (Feral Cat)"),
("13","M (Miscellaneous)"),
("40","N (Non Shelter Animal)"),
("41","B (Boarding Animal)")
)

def type_id_for_name(name):
    if name is None: return 2
    for tid, tname in types:
        if tname.upper().find(name.upper()) != -1:
            return int(tid)
    return 2

def type_id_for_species_id(sid):
    if sid is None: return 2
    if sid == 1: return 2
    elif sid == 2: return 11
    else: return 13

def type_name_for_id(id):
    for tid, tname in types:
        if int(tid) == id:
            return tname
    return "D (Dog)"

def type_from_db(name, default = 2):
    """ Looks up the type in the db when the conversion is run, assign to AnimalTypeID """
    return "COALESCE((SELECT ID FROM animaltype WHERE lower(AnimalType) LIKE lower('%s') LIMIT 1), %d)" % (name.strip(), default)

def md5(s):
    """
    Generates an md5 hash of str(s), returning the hash as a hex string
    """
    import hashlib
    m = hashlib.md5()
    m.update(str(s).encode("utf-8"))
    return m.hexdigest()

def uuid_b64():
    """ Returns a type 4 UUID as a base64 encoded str (shorter) """
    import base64, uuid
    return base64.b64encode(uuid.uuid4().bytes).decode("utf-8").replace("=", "")

def strip(s):
    """
    Remove any unicode or control characters and whitespace
    """
    if sys.version_info[0] > 2: 
        if type(s) != str: return s # PYTHON3
    else:
        if type(s) != str and type(s) != unicode: return s # PYTHON2
    return ("".join(i for i in s if ord(i) >= 32 and ord(i)<128)).strip()

def strip_unicode(s):
    """
    Remove any unicode characters
    """
    return "".join(i for i in s if ord(i)<128)

def dd(d):
    if d == None: return "NULL"
    return "'%d-%02d-%02d 00:00:00'" % ( d.year, d.month, d.day )

def ddt(d):
    if d == None: return "NULL"
    if type(d) == datetime.date: return dd(d)
    return "'%d-%02d-%02d %02d:%02d:%02d'" % ( d.year, d.month, d.day, d.hour, d.minute, d.second )

def ds(s):
    if s == None: return "NULL"
    return "'%s'" % str(s).replace("'", "''")

def df(f):
    if f == None: return "NULL"
    return str(f)

def di(i):
    if i == None: return "NULL"
    return str(i)

def regex(findin, pattern):
    matches = re.findall(pattern, findin)
    if len(matches) == 0: return ""
    return str(matches[0])

def iif(cond, iftrue, iffalse):
    if cond:
        return iftrue
    else:
        return iffalse

def spaceleft(s, spaces):
    """
    leftpads a string to a number of spaces
    """
    sp = "                                                 "
    if len(s) > spaces: return s
    nr = spaces - len(s)
    return sp[0:nr] + s

def spaceright(s, spaces):
    """
    rightpads a string to a number of spaces
    """
    sp = "                                                 "
    if len(s) > spaces: return s
    nr = spaces - len(s)
    return s + sp[0:nr]

def padleft(num, digits):
    """
    leftpads a number to digits
    """
    zeroes = "000000000000000"
    s = str(num)
    if len(s) > digits: return s
    nr = digits - len(s)
    return zeroes[0:nr] + s

def padright(num, digits):
    """
    rightpads a number to digits
    """
    zeroes = "000000000000000"
    s = str(num)
    if len(s) > digits: return s
    nr = digits - len(s)
    return s + zeroes[0:nr]

def truncate(s, length = 100):
    """
    Truncates a string to length. If the string is longer than
    length, appends ...
    Removes any unicode sequences
    HTML entities count as one character
    """
    if s is None: s = ""
    if len(s) < length: return s
    return s[0:length] + "..."

def find_row(d, fieldname, value):
    """
    given a list of dictionaries d, returns the
    row where fieldname = value
    """
    for x in d:
        if fieldname not in x:
            break
        if x[fieldname] == value:
            return x
    return None

def find_value(d, fieldname, value, findfield):
    """
    given a list of dictionaries d, returns findfield
    where fieldname = value
    """
    for x in d:
        if fieldname not in x or findfield not in x:
            break
        if x[fieldname] == value:
            return x[findfield]
    return ""

def makesql(table, s):
    fl = ""
    fv = ""
    for r in s:
        if fl != "": 
            fl += ", "
            fv += ", "
        fl += r[0]
        fv += r[1]
    return "INSERT INTO %s (%s) VALUES (%s);" % ( table, fl, fv )

def getid(table = "animal"):
    global ids
    if table in ids:
        nextid = ids[table]
        ids[table] = nextid + 1
        return nextid
    else:
        nextid = 1
        ids[table] = nextid + 1
        return nextid

def setid(table, nextid):
    global ids
    ids[table] = nextid

def date_diff_days(date1, date2):
    """
    Returns the difference in days between two dates. It's
    assumed that date2 > date1. We aren't using subtraction
    for timedeltas because it doesn't seem to work correctly
    when subtracting date from datetime (and some items
    in the database come through as date). Instead, we convert
    to unix time to calculate.
    (datetime) date1
    (datetime) date2
    """
    if date1 is None or date2 == None: return 0
    try:
        ux1 = time.mktime(date1.timetuple())
        ux2 = time.mktime(date2.timetuple())
        delta = int((ux2 - ux1) / 60 / 60 / 24)
        return delta
    except:
        sys.stderr.write("Invalid date: %s or %s\n" % ( date1, date2 ))
        return 0

def date_diff(date1, date2):
    """
    Outputs the difference between two dates as a readable string.
    date2 should be > date1
    """
    days = int(date_diff_days(date1, date2))
    if days < 0: days = 0
    weeks = int(days / 7)
    months = int(days / 30)
    years = int(days / 365)
    if days < 7:
        return "%d days." % days
    elif weeks <= 16:
        return "%d weeks." % weeks
    elif weeks <= 52:
        return "%d months." % months
    else:
        months = float(weeks % 52)
        months = int((months / 52.0) * 12)
        return "%d years %d months." % (years, months)

def todatetime(d):
    """ If d is a datetime.date returns it as a datetime.datetime """
    if d is None: return None
    if type(d) == datetime.date: d = datetime.datetime.combine(d, datetime.time())
    return d

def add_days(d, dy):
    if d is None: return d
    return d + datetime.timedelta(days=dy)

def subtract_days(d, dy):
    if d is None: return d
    return d - datetime.timedelta(days=dy)

def additional_field(fieldname, linktypeid, linkid, value):
    """ Writes an additional field entry """
    print("DELETE FROM additional WHERE LinkType=%d AND LinkID=%d AND AdditionalFieldID = " \
        "(SELECT ID FROM additionalfield WHERE FieldName LIKE '%s');" % (linktypeid, linkid, fieldname))
    print("INSERT INTO additional (LinkType, LinkID, AdditionalFieldID, Value) VALUES (" \
        "%d, %d, (SELECT ID FROM additionalfield WHERE FieldName LIKE '%s'), %s);" % \
        ( linktypeid, linkid, fieldname, ds(value)))

def additional_field_id(fieldid, linkid, value):
    """ Writes an additional field entry with a known additionalfieldid """
    print(f"DELETE FROM additional WHERE AdditionalFieldID={fieldid} AND LinkID={linkid};")
    print(f"INSERT INTO additional (LinkType, LinkID, AdditionalFieldID, Value) VALUES (" \
        f"(SELECT LinkType FROM additionalfield WHERE ID={fieldid}), {linkid}, {fieldid}, {ds(value)});")

def age_group(dob):
    """ Returns the age group for a date of birth """
    d = date_diff_days(dob, today())
    if d < 182: return "Baby"
    if d < 365*2: return "Young Adult"
    if d < 365*7: return "Adult"
    return "Senior"

def adopt_to(a, ownerid, movementtype = 1, movementdate = None):
    """ Writes an adoption movement insert 
        a: The animal object to adopt
        ownerid: The ownerid to adopt to
        movementtype: movement type to create (1 = adoption)
        movementdate: movement date, if None, DateBroughtIn is used
    """
    m = Movement()
    m.AnimalID = a.ID
    m.OwnerID = ownerid
    m.MovementType = movementtype
    m.MovementDate = movementdate
    if movementdate is None:
        m.MovementDate = a.DateBroughtIn
    a.Archived = 1
    a.ActiveMovementID = m.ID
    a.ActiveMovementDate = m.MovementDate
    a.ActiveMovementType = m.MovementType
    return m

def adopt_older_than(animals, movements, ownerid=100, days=365):
	""" Runs through animals and if any are still on shelter after 'days',
        creates an adoption to ownerid. Returns movements
	"""
	for a in animals:
		if a.Archived == 0 and a.DateBroughtIn < subtract_days(now(), days):
			m = Movement()
			m.AnimalID = a.ID
			m.OwnerID = ownerid
			m.MovementType = 1
			m.MovementDate = a.DateBroughtIn
			a.Archived = 1
			a.ActiveMovementID = m.ID
			a.ActiveMovementDate = a.DateBroughtIn
			a.ActiveMovementType = 1
			movements.append(m)
	return movements

def escaped_older_than(animals, movements, days=365):
	""" Runs through animals and if any are still on shelter after 'days',
        creates an escaped movement. Returns movements
	"""
	for a in animals:
		if a.Archived == 0 and a.DateBroughtIn < subtract_days(now(), days):
			m = Movement()
			m.AnimalID = a.ID
			m.OwnerID = 0
			m.MovementType = 4
			m.MovementDate = a.DateBroughtIn
			a.Archived = 1
			a.ActiveMovementID = m.ID
			a.ActiveMovementDate = a.DateBroughtIn
			a.ActiveMovementType = 4
			movements.append(m)
	return movements

def mime_type(filename):
    """
    Returns the mime type for a file with the given name
    """
    types = {
        "jpg"   : "image/jpeg",
        "jpeg"  : "image/jpeg",
        "bmp"   : "image/bmp",
        "gif"   : "image/gif",
        "png"   : "image/png",
        "doc"   : "application/msword",
        "xls"   : "application/vnd.ms-excel",
        "ppt"   : "application/vnd.ms-powerpoint",
        "docx"  : "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pptx"  : "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "xslx"  : "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "odt"   : "application/vnd.oasis.opendocument.text",
        "sxw"   : "application/vnd.oasis.opendocument.text",
        "ods"   : "application/vnd.oasis.opendocument.spreadsheet",
        "odp"   : "application/vnd.oasis.opendocument.presentation",
        "pdf"   : "application/pdf",
        "mpg"   : "video/mpg",
        "mp3"   : "audio/mpeg3",
        "avi"   : "video/avi",
        "htm"   : "text/html",
        "html"  : "text/html"
    }
    ext = filename[filename.rfind(".")+1:].lower()
    if ext in types:
        return types[ext]
    return "application/octet-stream"

def animal_image(animalid, imagedata):
    """ Writes the media and dbfs entries to add an image to an animal """
    media_file(0, animalid, "x.jpg", imagedata)

def media_file(linktypeid, linkid, filename, filedata, medianotes = ""):
    """ Writes the media and dbfs entries to add a piece of media to an animal or person """
    if filedata is None: return
    mediaid = getid("media")
    if filename.rfind(".") == -1: return
    extension = filename[filename.rfind("."):].lower()
    medianame = str(mediaid) + extension
    mimetype = mime_type(filename)
    encoded = base64.b64encode(filedata)
    if medianotes == "": medianotes = filename
    medianotes = medianotes.replace("'", "''")
    filename = filename.replace("'", "''")
    if sys.version_info[0] > 2: encoded = encoded.decode("ascii") # PYTHON3 - turn base64 into str for stdout
    websitephoto = extension == ".jpg" and 1 or 0
    dbfsidpath = "/animal"
    if linktypeid > 0: dbfsidpath = "/owner"
    print(f"UPDATE media SET websitephoto = 0, docphoto = 0 WHERE linkid = {linkid} AND linktypeid = {linktypeid};")
    print(f"INSERT INTO media (id, medianame, medianotes, mediasize, mediamimetype, websitephoto, docphoto, newsincelastpublish, updatedsincelastpublish, " \
        f"excludefrompublish, linkid, linktypeid, recordversion, date) VALUES ({mediaid}, '{medianame}', '{medianotes}', {len(filedata)}, '{mimetype}', {websitephoto}, {websitephoto}, 0, 0, 0, " \
        f"{linkid}, {linktypeid}, 0, {dd(datetime.datetime.today())});")
    dbfsid = getid("dbfs")
    print(f"INSERT INTO dbfs (id, name, path, url, content) VALUES ({dbfsid}, '{medianame}', '{dbfsidpath + '/' + str(linkid)}', 'base64:', '{encoded}');")
    print(f"UPDATE media SET DBFSID = {dbfsid} WHERE ID = {mediaid};")
    global mediafilescount
    global mediafilesbytes
    mediafilescount += 1
    mediafilesbytes += len(filedata)

def animal_test(animalid, required, given, typename, resultname, comments = ""):
    """ Returns an animaltest object """
    result = 1 # Unknown
    if resultname.lower().find("egative"): result = 2
    elif resultname.lower().find("ositive"): result = 3
    av = AnimalTest()
    av.AnimalID = animalid
    av.DateRequired = required
    av.DateOfTest = given
    av.TestTypeID = testtype_id_for_name(typename, True)
    av.TestResultID = result
    av.Comments = comments
    return av

def animal_vaccination(animalid, required, given, typename, comments = "", batchnumber = "", manufacturer = "", rabiestag = ""):
    """ Returns an animalvaccination object """
    av = AnimalVaccination()
    av.AnimalID = animalid
    av.DateRequired = required
    av.DateOfVaccination = given
    av.VaccinationID = vaccinationtype_id_for_name(typename, True)
    av.BatchNumber = batchnumber
    av.Manufacturer = manufacturer
    av.RabiesTag = rabiestag
    av.Comments = comments
    return av

def animal_regimen_single(animalid, dategiven, treatmentname, dosage = "", comments = "", cost = 0):
    """ Writes a regimen and treatment record for a single given treatment """
    regimenid = getid("animalmedical")
    treatmentid = getid("animalmedicaltreatment")
    s = (
        ( "ID", di(regimenid)),
        ( "AnimalID", di(animalid)),
        ( "MedicalProfileID", di(0)),
        ( "TreatmentName", ds(treatmentname)),
        ( "Dosage", ds(dosage)),
        ( "StartDate", dd(dategiven)),
        ( "Status", di(2)), # Completed
        ( "Cost", di(cost)),
        ( "CostPaidDate", dd(None)),
        ( "TimingRule", di(0)),
        ( "TimingRuleFrequency", di(0)),
        ( "TimingRuleNoFrequencies", di(0)),
        ( "TreatmentRule", di(0)),
        ( "TotalNumberOfTreatments", di(1)),
        ( "TreatmentsGiven", di(1)),
        ( "TreatmentsRemaining", di(0)),
        ( "Comments", ds(comments)),
        ( "RecordVersion", di(0) ),
        ( "CreatedBy", ds("conversion") ),
        ( "CreatedDate", dd(today()) ),
        ( "LastChangedBy", ds("conversion") ),
        ( "LastChangedDate", dd(today()) )
        )
    am = makesql("animalmedical", s)
    s = (
        ( "ID", di(treatmentid)),
        ( "AnimalID", di(animalid)),
        ( "AnimalMedicalID", di(regimenid)),
        ( "DateRequired", dd(dategiven)),
        ( "DateGiven", dd(dategiven)),
        ( "GivenBy", ds("conversion")),
        ( "TreatmentNumber", di(1)),
        ( "TotalTreatments", di(1)),
        ( "Comments", ds("")),
        ( "RecordVersion", di(0) ),
        ( "CreatedBy", ds("conversion") ),
        ( "CreatedDate", dd(today()) ),
        ( "LastChangedBy", ds("conversion") ),
        ( "LastChangedDate", dd(today()) )
        )
    amt = makesql("animalmedicaltreatment", s)
    return "%s\n%s\n" % (am, amt)

def load_image_from_file(fpath, case_sensitive = True):
    """ Reads image data from a disk file or returns None if the file does not exist """
    if case_sensitive and not os.path.exists(fpath): return None
    if not case_sensitive:
        # Search the directory for the filename and compare case insensitive, then
        # update fpath if we find the file
        filename = fpath[fpath.rfind("/") + 1:]
        foldername = fpath[0:fpath.rfind("/")]
        result = False
        for x in os.listdir(foldername):
            if x.lower() == filename.lower():
                fpath = foldername + "/" + x
                result = True
                break
        if not result: return None
    try:
        f = open(fpath, "rb")
        s = f.read()
        f.close()
        return s
    except:
        return None

def load_image_from_url(imageurl, cache=True):
    return load_file_from_url(imageurl, cache=cache)

def load_file_from_url(url, cache=True):
    """
    Returns a file from a URL. If cache == True, will remember the URL in /tmp/import_cache/
    so that repeated calls do not go back to the origin.
    """
    try:
        if url.startswith("//"): 
            url = "https:%s" % url
        sys.stderr.write("GET %s\n" % url)
        if not os.path.exists("/tmp/import_cache"):
            os.mkdir("/tmp/import_cache")
        cachename = "/tmp/import_cache/%s" % md5(url)
        if cache and os.path.exists(cachename):
            sys.stderr.write("(retrieved from %s)\n" % cachename)
            with open(cachename, "rb") as f:
                return f.read()
        filedata = urllib2.urlopen(url).read()
        sys.stderr.write("200 OK %s\n" % url)
        if cache:
            with open(cachename, "wb") as f:
                f.write(filedata)
    except Exception as err:
        sys.stderr.write(str(err) + "\n")
        return None
    return filedata

def petfinder_get_adoptable(shelterid):
    """
    Returns the page of adoptable animals for the PetFinder shelterid
    """
    url = "http://fpm.petfinder.com/petlist/petlist.cgi?shelter=%s&status=A&limit=500&offset=0" % shelterid
    sys.stderr.write("GET " + url + "\n")
    page = ""
    try:
        page = urllib2.urlopen(url).read()
        return page
    except Exception as err:
        sys.stderr.write(str(err) + "\n")
        return ""

def petfinder_image(page, animalid, animalname):
    """
    Prints INSERTs to media/dbfs for the main image for animalname,
    found in the petfinder "page"
    """
    sp = page.find(animalname)
    if sp == -1: return
    # Each animal appears on its on row in a table, by taking
    # everything upto the closing table row, we can do regex for just this
    # animal to find its PetID and img URL
    ep = page.find("</tr>", sp)
    chunk = page[sp:ep]
    petid = regex(chunk, r"\/petdetail\/(.+?)\"")
    sys.stderr.write("Got PetID: %s\n" % petid)
    imageurl = "http://photos.petfinder.com/photos/pets/%s/1/?bust=1425358987&width=632&no_scale_up=1" % petid
    jpgdata = load_image_from_url(imageurl)
    animal_image(animalid, jpgdata)

def get_url(url, headers = {}, cookies = {}, timeout = None):
    """
    Retrieves a URL
    """
    # requests timeout is seconds/float, but some may call this with integer ms instead so convert
    if timeout is not None and timeout > 1000: timeout = timeout / 1000.0
    r = requests.get(url, headers = headers, cookies=cookies, timeout=timeout)
    return { "cookies": r.cookies, "headers": r.headers, "response": r.text, "status": r.status_code, "requestheaders": r.request.headers, "requestbody": r.request.body }

def get_image_url(url, headers = {}, cookies = {}, timeout = None):
    """
    Retrives an image from a URL
    """
    # requests timeout is seconds/float, but some may call this with integer ms instead so convert
    if timeout is not None and timeout > 1000: timeout = timeout / 1000.0
    r = requests.get(url, headers = headers, cookies=cookies, timeout=timeout, stream=True)
    s = StringIO()
    for chunk in r:
        s.write(chunk) # default from requests is 128 byte chunks
    return { "cookies": r.cookies, "headers": r.headers, "response": s.getvalue(), "status": r.status_code, "requestheaders": r.request.headers, "requestbody": r.request.body }
        
def post_data(url, data, contenttype = "", httpmethod = "", headers = {}):
    """ 
    Posts data to a URL as the body
    httpmethod: POST by default
    """
    try:
        if contenttype != "": headers["Content-Type"] = contenttype
        req = urllib2.Request(url, data, headers)
        if httpmethod != "": req.get_method = lambda: httpmethod
        resp = urllib2.urlopen(req)
        return { "requestheaders": headers, "requestbody": data, "headers": resp.info().headers, "response": resp.read(), "status": resp.getcode() }
    except urllib2.HTTPError as e:
        return { "requestheaders": headers, "requestbody": data, "headers": e.info().headers, "response": e.read(), "status": e.getcode() }
    
def post_form(url, fields, headers = {}, cookies = {}):
    """
    Does a form post
    url: The http url to post to
    fields: A map of { name: value } elements
    headers: A map of { name: value } headers
    return value is the http headers (a map) and server's response as a string
    """
    r = requests.post(url, data=fields, headers=headers, cookies=cookies)
    return { "cookies": r.cookies, "headers": r.headers, "response": r.text, "status": r.status_code, "requestheaders": r.request.headers, "requestbody": r.request.body }

class AnimalType:
    ID = 0
    Name = ""
    Description = None
    def __init__(self, ID = 0, Name = "", Description = ""):
        self.ID = ID
        if ID == 0: self.ID = getid("animaltype")
        self.Name = Name
        self.Description = Description
    def __str__(self):
        s = (
            ( "ID", di(self.ID) ),
            ( "AnimalType", ds(self.Name) ),
            ( "AnimalDescription", ds(self.Description) )
            )
        return makesql("animaltype", s)

class BaseColour:
    ID = 0
    Name = ""
    Description = None
    def __init__(self, ID = 0, Name = "", Description = ""):
        self.ID = ID
        if ID == 0: self.ID = getid("basecolour")
        self.Name = Name
        self.Description = Description
    def __str__(self):
        s = (
            ( "ID", di(self.ID) ),
            ( "BaseColour", ds(self.Name) ),
            ( "BaseColourDescription", ds(self.Description) )
            )
        return makesql("basecolour", s)

class Breed:
    ID = 0
    Name = ""
    Description = None
    SpeciesID = 0
    def __init__(self, ID = 0, Name = "", Description = "", SpeciesID = 0):
        self.ID = ID
        if ID == 0: self.ID = getid("breed")
        self.Name = Name
        self.Description = Description
        self.SpeciesID = SpeciesID
    def __str__(self):
        s = (
            ( "ID", di(self.ID) ),
            ( "BreedName", ds(self.Name) ),
            ( "BreedDescription", ds(self.Description) ),
	    ( "SpeciesID", di(self.SpeciesID) )
            )
        return makesql("breed", s)

class Species:
    ID = 0
    Name = ""
    Description = None
    PetFinder = None
    def __init__(self, ID = 0, Name = "", Description = "", PetFinder = ""):
        self.ID = ID
        if ID == 0: self.ID = getid("species")
        self.Name = Name
        self.Description = Description
        self.PetFinder = PetFinder
    def __str__(self):
        s = (
            ( "ID", di(self.ID) ),
            ( "SpeciesName", ds(self.Name) ),
            ( "SpeciesDescription", ds(self.Description) ),
            ( "PetFinderSpecies", ds(self.PetFinder) ),
            )
        return makesql("species", s)

class EntryReason:
    ID = 0
    Name = ""
    Description = None
    def __init__(self, ID = 0, Name = "", Description = ""):
        self.ID = ID
        if ID == 0: self.ID = getid("entryreason")
        self.Name = Name
        self.Description = Description
    def __str__(self):
        s = (
            ( "ID", di(self.ID) ),
            ( "ReasonName", ds(self.Name) ),
            ( "ReasonDescription", ds(self.Description) )
            )
        return makesql("entryreason", s)

class Jurisdiction:
    ID = 0
    Name = ""
    Description = None
    def __init__(self, ID = 0, Name = "", Description = ""):
        self.ID = ID
        if ID == 0: self.ID = getid("jurisdiction")
        self.Name = Name
        self.Description = Description
    def __str__(self):
        s = (
            ( "ID", di(self.ID) ),
            ( "JurisdictionName", ds(self.Name) ),
            ( "JurisdictionDescription", ds(self.Description) )
            )
        return makesql("jurisdiction", s)

class Location:
    ID = 0
    Name = ""
    Description = None
    def __init__(self, ID = 0, Name = "", Description = ""):
        self.ID = ID
        if ID == 0: self.ID = getid("internallocation")
        self.Name = Name
        self.Description = Description
    def __str__(self):
        s = (
            ( "ID", di(self.ID) ),
            ( "LocationName", ds(self.Name) ),
            ( "LocationDescription", ds(self.Description) )
            )
        return makesql("internallocation", s)

class PickupLocation:
    ID = 0
    Name = ""
    Description = None
    def __init__(self, ID = 0, Name = "", Description = ""):
        self.ID = ID
        if ID == 0: self.ID = getid("pickuplocation")
        self.Name = Name
        self.Description = Description
    def __str__(self):
        s = (
            ( "ID", di(self.ID) ),
            ( "LocationName", ds(self.Name) ),
            ( "LocationDescription", ds(self.Description) )
            )
        return makesql("pickuplocation", s)

class TestType:
    ID = 0
    Name = ""
    Description = None
    DefaultCost = 0
    def __init__(self, ID = 0, Name = "", Description = "", DefaultCost = 0):
        self.ID = ID
        if ID == 0: self.ID = getid("testtype")
        self.Name = Name
        self.Description = Description
        self.DefaultCost = 0
    def __str__(self):
        s = (
            ( "ID", di(self.ID) ),
            ( "TestName", ds(self.Name) ),
            ( "TestDescription", ds(self.Description) ),
            ( "DefaultCost", df(self.DefaultCost) ),
            )
        return makesql("testtype", s)

class VaccinationType:
    ID = 0
    Name = ""
    Description = None
    DefaultCost = 0
    def __init__(self, ID = 0, Name = "", Description = "", DefaultCost = 0):
        self.ID = ID
        if ID == 0: self.ID = getid("vaccinationtype")
        self.Name = Name
        self.Description = Description
        self.DefaultCost = 0
    def __str__(self):
        s = (
            ( "ID", di(self.ID) ),
            ( "VaccinationType", ds(self.Name) ),
            ( "VaccinationDescription", ds(self.Description) ),
            ( "DefaultCost", df(self.DefaultCost) ),
            )
        return makesql("vaccinationtype", s)

class DonationType:
    ID = 0
    Name = ""
    Description = None
    DefaultCost = 0
    def __init__(self, ID = 0, Name = "", Description = "", DefaultCost = 0):
        self.ID = ID
        if ID == 0: self.ID = getid("donationtype")
        self.Name = Name
        self.Description = Description
        self.DefaultCost = DefaultCost
    def __str__(self):
        s = (
            ( "ID", di(self.ID) ),
            ( "DonationName", ds(self.Name) ),
            ( "DonationDescription", ds(self.Description) ),
            ( "DefaultCost", df(self.DefaultCost) )
            )
        return makesql("donationtype", s)

class AnimalControl:
    ID = 0
    IncidentCode = ""
    IncidentDateTime = None
    IncidentTypeID = 1
    CallDateTime = None
    CallNotes = ""
    CallTaker = ""
    CallerID = 0
    VictimID = 0
    DispatchAddress = ""
    DispatchTown = ""
    DispatchCounty = ""
    DispatchPostcode = ""
    DispatchLatLong = ""
    DispatchedACO = ""
    DispatchDateTime = None
    JurisdictionID = 0
    PickupLocationID = 0
    RespondedDateTime = None
    FollowupDateTime = None
    FollowupComplete = 0
    FollowupDateTime2 = None
    FollowupComplete2 = 0
    FollowupDateTime3 = None
    FollowupComplete3 = 0
    CompletedDate = None
    IncidentCompletedID = 0
    OwnerID = 0
    Owner2ID = 0
    Owner3ID = 0
    AnimalID = 0
    AnimalDescription = ""
    SpeciesID = 0
    Sex = 0
    AgeGroup = ""
    RecordVersion = 0
    CreatedBy = "conversion"
    CreatedDate = today()
    LastChangedBy = "conversion"
    LastChangedDate = today()
    def __init__(self, ID = 0):
        self.ID = ID
        if ID == 0: self.ID = getid("animalcontrol")
    def __str__(self):
        if self.IncidentCode.strip() == "": 
            self.IncidentCode = padleft(self.ID, 6)
        s = (
            ( "ID", di(self.ID) ),
            ( "IncidentCode", ds(self.IncidentCode) ),
            ( "IncidentDateTime", ddt(self.IncidentDateTime) ),
            ( "IncidentTypeID", di(self.IncidentTypeID) ),
            ( "CallDateTime", ddt(self.CallDateTime) ),
            ( "CallNotes", ds(self.CallNotes) ),
            ( "CallTaker", ds(self.CallTaker) ),
            ( "CallerID", di(self.CallerID) ),
            ( "VictimID", di(self.VictimID) ),
            ( "DispatchAddress", ds(self.DispatchAddress) ),
            ( "DispatchTown", ds(self.DispatchTown) ),
            ( "DispatchCounty", ds(self.DispatchCounty) ),
            ( "DispatchPostcode", ds(self.DispatchPostcode) ),
            ( "DispatchLatLong", ds(self.DispatchLatLong) ),
            ( "DispatchedACO", ds(self.DispatchedACO) ),
            ( "JurisdictionID", di(self.JurisdictionID) ),
            ( "PickupLocationID", di(self.PickupLocationID) ),
            ( "DispatchDateTime", ddt(self.DispatchDateTime) ),
            ( "RespondedDateTime", ddt(self.RespondedDateTime) ),
            ( "FollowupDateTime", ddt(self.FollowupDateTime) ),
            ( "FollowupComplete", di(self.FollowupComplete) ),
            ( "FollowupDateTime2", ddt(self.FollowupDateTime2) ),
            ( "FollowupComplete2", di(self.FollowupComplete2) ),
            ( "FollowupDateTime3", ddt(self.FollowupDateTime3) ),
            ( "FollowupComplete3", di(self.FollowupComplete3) ),
            ( "CompletedDate", dd(self.CompletedDate) ),
            ( "IncidentCompletedID", di(self.IncidentCompletedID) ),
            ( "OwnerID", di(self.OwnerID) ),
            ( "Owner2ID", di(self.Owner2ID) ),
            ( "Owner3ID", di(self.Owner3ID) ),
            ( "AnimalID", di(self.AnimalID) ),
            ( "AnimalDescription", ds(self.AnimalDescription) ),
            ( "SpeciesID", di(self.SpeciesID) ),
            ( "Sex", di(self.Sex) ),
            ( "AgeGroup", ds(self.AgeGroup) ),
            ( "RecordVersion", di(self.RecordVersion) ),
            ( "CreatedBy", ds(self.CreatedBy) ),
            ( "CreatedDate", dd(self.CreatedDate) ),
            ( "LastChangedBy", ds(self.LastChangedBy) ),
            ( "LastChangedDate", dd(self.LastChangedDate) )
            )
        return makesql("animalcontrol", s)

class AnimalTest:
    ID = 0
    AnimalID = 0
    TestTypeID = 0
    TestResultID = 0
    DateOfTest = None
    DateRequired = today()
    Comments = ""
    Cost = 0
    RecordVersion = 0
    CreatedBy = "conversion"
    CreatedDate = today()
    LastChangedBy = "conversion"
    LastChangedDate = today()
    def __init__(self, ID = 0):
        self.ID = ID
        if ID == 0: self.ID = getid("animaltest")
    def __str__(self):
        s = (
            ( "ID", di(self.ID) ),
            ( "AnimalID", di(self.AnimalID) ),
            ( "TestTypeID", di(self.TestTypeID) ),
            ( "TestResultID", di(self.TestResultID) ),
            ( "DateOfTest", dd(self.DateOfTest) ),
            ( "DateRequired", dd(self.DateRequired) ),
            ( "Comments", ds(self.Comments) ),
            ( "Cost", di(self.Cost) ),
            ( "RecordVersion", di(self.RecordVersion) ),
            ( "CreatedBy", ds(self.CreatedBy) ),
            ( "CreatedDate", dd(self.CreatedDate) ),
            ( "LastChangedBy", ds(self.LastChangedBy) ),
            ( "LastChangedDate", dd(self.LastChangedDate) )
            )
        return makesql("animaltest", s)

class AnimalVaccination:
    ID = 0
    AnimalID = 0
    VaccinationID = 0
    DateOfVaccination = None
    DateRequired = today()
    DateExpires = None
    Manufacturer = ""
    BatchNumber = ""
    RabiesTag = ""
    Comments = ""
    Cost = 0
    RecordVersion = 0
    CreatedBy = "conversion"
    CreatedDate = today()
    LastChangedBy = "conversion"
    LastChangedDate = today()
    def __init__(self, ID = 0):
        self.ID = ID
        if ID == 0: self.ID = getid("animalvaccination")
    def __str__(self):
        s = (
            ( "ID", di(self.ID) ),
            ( "AnimalID", di(self.AnimalID) ),
            ( "VaccinationID", di(self.VaccinationID) ),
            ( "DateOfVaccination", dd(self.DateOfVaccination) ),
            ( "DateRequired", dd(self.DateRequired) ),
            ( "DateExpires", dd(self.DateExpires) ),
            ( "Comments", ds(self.Comments) ),
            ( "Manufacturer", ds(self.Manufacturer) ),
            ( "BatchNumber", ds(self.BatchNumber) ),
            ( "RabiesTag", ds(self.BatchNumber) ),
            ( "Cost", di(self.Cost) ),
            ( "RecordVersion", di(self.RecordVersion) ),
            ( "CreatedBy", ds(self.CreatedBy) ),
            ( "CreatedDate", dd(self.CreatedDate) ),
            ( "LastChangedBy", ds(self.LastChangedBy) ),
            ( "LastChangedDate", dd(self.LastChangedDate) )
            )
        return makesql("animalvaccination", s)

class AnimalWaitingList:
    ID = 0
    SpeciesID = 1
    Size = 1
    DatePutOnList = None
    OwnerID = 0
    AnimalDescription = ""
    ReasonForWantingToPart = ""
    CanAffordDonation = 0
    Urgency = 5
    DateRemovedFromList = None
    AutoRemovePolicy = 1
    DateOfLastOwnerContact = None
    ReasonForRemoval = ""
    Comments = ""
    UrgencyUpdateDate = None
    UrgencyLastUpdatedDate = None
    RecordVersion = 0
    CreatedBy = "conversion"
    CreatedDate = today()
    LastChangedBy = "conversion"
    LastChangedDate = today()
    def __init__(self, ID = 0):
        self.ID = ID
        if ID == 0: self.ID = getid("animalwaitinglist")
    def __str__(self):
        s = (
            ( "ID", di(self.ID) ),
            ( "SpeciesID", di(self.SpeciesID) ),
            ( "Size", di(self.Size) ),
            ( "DatePutOnList", dd(self.DatePutOnList) ),
            ( "OwnerID", di(self.OwnerID) ),
            ( "AnimalDescription", ds(self.AnimalDescription) ),
            ( "ReasonForWantingToPart", ds(self.ReasonForWantingToPart) ),
            ( "CanAffordDonation", di(self.CanAffordDonation) ),
            ( "Urgency", di(self.Urgency) ),
            ( "DateRemovedFromList", dd(self.DateRemovedFromList) ),
            ( "AutoRemovePolicy", di(self.AutoRemovePolicy) ),
            ( "DateOfLastOwnerContact", dd(self.DateOfLastOwnerContact) ),
            ( "ReasonForRemoval", ds(self.ReasonForRemoval) ),
            ( "Comments", ds(self.Comments) ),
            ( "UrgencyUpdateDate", dd(self.UrgencyUpdateDate) ),
            ( "UrgencyLastUpdatedDate", dd(self.UrgencyLastUpdatedDate) ),
            ( "RecordVersion", di(self.RecordVersion) ),
            ( "CreatedBy", ds(self.CreatedBy) ),
            ( "CreatedDate", dd(self.CreatedDate) ),
            ( "LastChangedBy", ds(self.LastChangedBy) ),
            ( "LastChangedDate", dd(self.LastChangedDate) )
            )
        return makesql("animalwaitinglist", s)

class Animal:
    ID = 0
    AnimalTypeID = 1
    AnimalName = ""
    NonShelterAnimal = 0
    CrueltyCase = 0
    BondedAnimalID = 0
    BondedAnimal2ID = 0
    BaseColourID = 1
    SpeciesID = 1
    BreedID = 1
    Breed2ID = 0
    BreedName = ""
    CrossBreed = 0
    CoatType = 0
    Markings = ""
    ShelterCode = ""
    ShortCode = ""
    UniqueCodeID = 0
    YearCodeID = 0
    AcceptanceNumber = ""
    DateOfBirth = today()
    EstimatedDOB = 0
    DeceasedDate = None
    Sex = 0
    Identichipped = 0
    IdentichipNumber = ""
    IdentichipDate = None
    Identichip2Number = ""
    Identichip2Date = None
    Tattoo = 0
    TattooNumber = ""
    TattooDate = None
    SmartTag = 0
    SmartTagNumber = ""
    SmartTagDate = None
    SmartTagSentDate = None
    SmartTagType = 0
    Neutered = 0
    NeuteredDate = None
    NeuteredByVetID = 0
    CombiTested = 0
    CombiTestDate = None
    CombiTestResult = 0
    HeartwormTested = 0
    HeartwormTestDate = None
    HeartwormTestResult = 0
    FLVResult = 0
    Declawed = 0
    HiddenAnimalDetails = ""
    AnimalComments = ""
    OwnersVetID = 0
    CurrentVetID = 0
    OwnerID = 0
    OriginalOwnerID = 0
    BroughtInByOwnerID = 0
    AdoptionCoordinatorID = 0
    ReasonForEntry = ""
    ReasonNO = ""
    DateBroughtIn = today()
    EntryReasonID = 1
    EntryTypeID = 1
    HealthProblems = ""
    PutToSleep = 0
    PTSReason = ""
    PTSReasonID = 1
    IsDOA = 0
    IsTransfer = 0
    IsPickup = 0
    JurisdictionID = 0
    PickupLocationID = 0
    PickupAddress = ""
    IsGoodWithCats = 2
    IsGoodWithDogs = 2
    IsGoodWithChildren = 2
    IsHouseTrained = 2
    IsNotAvailableForAdoption = 0
    IsNotForRegistration = 1
    IsHold = 0
    HoldUntilDate = None
    IsQuarantine = 0
    IsCourtesy = 0
    AdditionalFlags = ""
    HasSpecialNeeds = 0
    ShelterLocation = 1
    ShelterLocationUnit = ""
    DiedOffShelter = 0
    Size = 2
    Weight = 0.0
    RabiesTag = ""
    Archived = 0
    ActiveMovementID = 0
    ActiveMovementType = 0
    ActiveMovementDate = None
    ActiveMovementReturn = None
    HasActiveReserve = 0
    HasTrialAdoption = 0
    HasPermanentFoster = 0
    MostRecentEntryDate = None
    TimeOnShelter = ""
    DaysOnShelter = 0
    DailyBoardingCost = 0.0
    AnimalAge = ""
    RecordVersion = 0
    CreatedBy = "conversion"
    CreatedDate = today()
    LastChangedBy = "conversion"
    LastChangedDate = today()
    ExtraID = ""
    def __init__(self, ID = 0):
        self.ID = ID
        if ID == 0: self.ID = getid("animal")
    def generateCode(self, typename = ""):
        """ Generates a sheltercode and shortcode for the animal
            to the default schemes.
            typename is the animaltype name (eg: Unwanted Cat). The
            year is got from DateBroughtIn, the index maintained
            internally. """
        global nextyearcode
        if typename == "": typename = type_name_for_id(self.AnimalTypeID)
        self.YearCodeID = nextyearcode
        self.ShelterCode = "%s%d%03d" % ( typename[0:1], self.DateBroughtIn.year, nextyearcode)
        if self.ShortCode == "": self.ShortCode = "%03d%s" % (nextyearcode, typename[0:1]) # check so it can be assigned before generating code
        nextyearcode += 1
    def infoLine(self):
        return "animal: %d %s %s %s, %s %s, arc: %s, ns: %s, intake %s, dob %s" % (self.ID, self.AnimalName, self.ShelterCode, self.ShortCode, self.BreedName, species_name_for_id(self.SpeciesID), self.Archived, self.NonShelterAnimal, self.DateBroughtIn, self.DateOfBirth)
    def __str__(self):
        if self.AnimalAge == "" and self.DateOfBirth is not None:
            self.AnimalAge = date_diff(self.DateOfBirth, today())
        if self.ShelterCode == "":
            self.generateCode(type_name_for_id(self.AnimalTypeID))
        if self.DaysOnShelter == 0 and self.TimeOnShelter == "":
            self.DaysOnShelter = date_diff_days(self.DateBroughtIn, today())
            self.TimeOnShelter = date_diff(self.DateBroughtIn, today())
            if self.ActiveMovementDate is not None:
                self.TimeOnShelter = date_diff(self.DateBroughtIn, self.ActiveMovementDate)
                self.DaysOnShelter = date_diff_days(self.DateBroughtIn, self.ActiveMovementDate)
        if self.MostRecentEntryDate is None:
            self.MostRecentEntryDate = self.DateBroughtIn
        if self.IdentichipNumber is None:
            self.IdentichipNumber = ""
        s = (
            ( "ID", di(self.ID) ),
            ( "AnimalTypeID", di(self.AnimalTypeID) ),
            ( "AnimalName", ds(self.AnimalName) ),
            ( "NonShelterAnimal", di(self.NonShelterAnimal) ),
            ( "CrueltyCase", di(self.CrueltyCase) ),
            ( "BondedAnimalID", di(self.BondedAnimalID) ),
            ( "BondedAnimal2ID", di(self.BondedAnimal2ID) ),
            ( "BaseColourID", di(self.BaseColourID) ),
            ( "SpeciesID", di(self.SpeciesID) ),
            ( "BreedID", di(self.BreedID) ),
            ( "Breed2ID", di(self.Breed2ID) ),
            ( "BreedName", ds(self.BreedName) ),
            ( "CrossBreed", di(self.CrossBreed) ),
	        ( "CoatType", di(self.CoatType) ),
            ( "Markings", ds(self.Markings) ),
            ( "ShelterCode", ds(self.ShelterCode) ),
            ( "ShortCode", ds(self.ShortCode) ),
            ( "UniqueCodeID", di(self.UniqueCodeID) ),
            ( "YearCodeID", di(self.YearCodeID) ),
            ( "AcceptanceNumber", ds(self.AcceptanceNumber) ),
            ( "DateOfBirth", dd(self.DateOfBirth) ),
            ( "AgeGroup", ds( age_group(self.DateOfBirth)) ),
            ( "EstimatedDOB", di(self.EstimatedDOB) ),
            ( "DeceasedDate", dd(self.DeceasedDate) ),
            ( "Sex", di(self.Sex) ),
            ( "Identichipped", di(self.Identichipped) ),
            ( "IdentichipNumber", ds(self.IdentichipNumber) ),
            ( "IdentichipDate", dd(self.IdentichipDate) ),
            ( "Identichip2Number", ds(self.Identichip2Number) ),
            ( "Identichip2Date", dd(self.Identichip2Date) ),
            ( "Tattoo", di(self.Tattoo) ),
            ( "TattooNumber", ds(self.TattooNumber) ),
            ( "TattooDate", dd(self.TattooDate) ),
            ( "SmartTag", di(self.SmartTag) ),
            ( "SmartTagNumber", ds(self.SmartTagNumber) ),
            ( "SmartTagDate", dd(self.SmartTagDate) ),
            ( "SmartTagSentDate", dd(self.SmartTagSentDate) ),
            ( "SmartTagType", di(self.SmartTagType) ),
            ( "Neutered", di(self.Neutered) ),
            ( "NeuteredDate", dd(self.NeuteredDate) ),
            ( "NeuteredByVetID", di(self.NeuteredByVetID) ),
            ( "CombiTested", di(self.CombiTested) ),
            ( "CombiTestDate", dd(self.CombiTestDate) ),
            ( "CombiTestResult", di(self.CombiTestResult) ),
            ( "HeartwormTested", di(self.HeartwormTested) ),
            ( "HeartwormTestDate", dd(self.HeartwormTestDate) ),
            ( "HeartwormTestResult", di(self.HeartwormTestResult) ),
            ( "FLVResult", di(self.FLVResult) ),
            ( "Declawed", di(self.Declawed) ),
            ( "HiddenAnimalDetails", ds(self.HiddenAnimalDetails) ),
            ( "AnimalComments", ds(self.AnimalComments) ),
            ( "OwnersVetID", di(self.OwnersVetID) ),
            ( "CurrentVetID", di(self.CurrentVetID) ),
            ( "OwnerID", di(self.OwnerID) ),
            ( "OriginalOwnerID", di(self.OriginalOwnerID) ),
            ( "BroughtInByOwnerID", di(self.BroughtInByOwnerID) ),
            ( "AdoptionCoordinatorID", di(self.AdoptionCoordinatorID) ),
            ( "ReasonForEntry", ds(self.ReasonForEntry) ),
            ( "ReasonNO", ds(self.ReasonNO) ),
            ( "DateBroughtIn", dd(self.DateBroughtIn) ),
            ( "EntryReasonID", di(self.EntryReasonID) ),
            ( "EntryTypeID", di(self.EntryTypeID) ),
            ( "AsilomarIsTransferExternal", di(0) ),
            ( "AsilomarIntakeCategory", di(0) ),
            ( "AsilomarOwnerRequestedEuthanasia", di(0) ),
            ( "HealthProblems", ds(self.HealthProblems) ),
            ( "PutToSleep", di(self.PutToSleep) ),
            ( "PTSReason", ds(self.PTSReason) ),
            ( "PTSReasonID", di(self.PTSReasonID) ),
            ( "IsDOA", di(self.IsDOA) ),
            ( "IsTransfer", di(self.IsTransfer) ),
            ( "IsPickup", di(self.IsPickup) ),
            ( "JurisdictionID", di(self.JurisdictionID) ),
            ( "PickupLocationID", di(self.PickupLocationID) ),
            ( "PickupAddress", ds(self.PickupAddress) ),
            ( "IsGoodWithCats", di(self.IsGoodWithCats) ),
            ( "IsGoodWithDogs", di(self.IsGoodWithDogs) ),
            ( "IsGoodWithChildren", di(self.IsGoodWithChildren) ),
            ( "IsHouseTrained", di(self.IsHouseTrained) ),
            ( "IsNotAvailableForAdoption", di(self.IsNotAvailableForAdoption) ),
            ( "IsNotForRegistration", di(self.IsNotForRegistration) ),
            ( "IsHold", di(self.IsHold) ),
            ( "HoldUntilDate", dd(self.HoldUntilDate) ),
            ( "IsQuarantine", di(self.IsQuarantine) ),
            ( "IsCourtesy", di(self.IsCourtesy) ),
            ( "HasSpecialNeeds", di(self.HasSpecialNeeds) ),
            ( "AdditionalFlags", ds(self.AdditionalFlags) ),
            ( "ShelterLocation", di(self.ShelterLocation) ),
            ( "ShelterLocationUnit", ds(self.ShelterLocationUnit) ),
            ( "DiedOffShelter", di(self.DiedOffShelter) ),
            ( "Size", di(self.Size) ),
            ( "Weight", df(self.Weight) ),
            ( "RabiesTag", ds(self.RabiesTag) ),
            ( "Archived", di(self.Archived) ),
            ( "ActiveMovementID", di(self.ActiveMovementID) ),
            ( "ActiveMovementType", di(self.ActiveMovementType) ),
            ( "ActiveMovementDate", dd(self.ActiveMovementDate) ),
            ( "ActiveMovementReturn", dd(self.ActiveMovementReturn) ),
            ( "HasActiveReserve", di(self.HasActiveReserve) ),
            ( "HasTrialAdoption", di(self.HasTrialAdoption) ),
            ( "HasPermanentFoster", di(self.HasPermanentFoster) ),
            ( "MostRecentEntryDate", dd(self.MostRecentEntryDate) ),
            ( "TimeOnShelter", ds(self.TimeOnShelter) ),
            ( "DaysOnShelter", di(self.DaysOnShelter) ),
            ( "DailyBoardingCost", di(self.DailyBoardingCost) ),
            ( "AnimalAge", ds(self.AnimalAge) ),
            ( "RecordVersion", di(self.RecordVersion) ),
            ( "CreatedBy", ds(self.CreatedBy) ),
            ( "CreatedDate", dd(self.CreatedDate) ),
            ( "LastChangedBy", ds(self.LastChangedBy) ),
            ( "LastChangedDate", dd(self.LastChangedDate) )
            )
        stderr(self.infoLine())
        return makesql("animal", s)

class Log:
    ID = 0
    LogTypeID = 0
    LinkID = 0 
    LinkType = 0
    Date = None
    Comments = ""
    RecordVersion = 0
    CreatedBy = "conversion"
    CreatedDate = today()
    LastChangedBy = "conversion"
    LastChangedDate = today()
    def __init__(self, ID = 0):
        self.ID = ID
        if ID == 0: self.ID = getid("log")
    def __str__(self):
        s = (
            ( "ID", di(self.ID) ),
            ( "LogTypeID", di(self.LogTypeID) ),
            ( "LinkID", di(self.LinkID) ),
            ( "LinkType", di(self.LinkType) ),
            ( "Date", dd(self.Date) ),
            ( "Comments", ds(self.Comments) ),
            ( "RecordVersion", di(self.RecordVersion) ),
            ( "CreatedBy", ds(self.CreatedBy) ),
            ( "CreatedDate", dd(self.CreatedDate) ),
            ( "LastChangedBy", ds(self.LastChangedBy) ),
            ( "LastChangedDate", dd(self.LastChangedDate) )
            )
        return makesql("log", s)

class Movement:
    ID = 0
    AdoptionNumber = ""
    AnimalID = 0
    OwnerID = 0
    RetailerID = 0
    OriginalRetailerMovementID = 0
    MovementDate = None
    MovementType = 0
    ReturnDate = None
    ReturnedReasonID = 4 # Unable to cope
    ReturnedByOwnerID = 0
    InsuranceNumber = ""
    ReasonForReturn = ""
    ReservationDate = None
    Donation = 0.0
    ReservationCancelledDate = None
    IsTrial = 0
    TrialEndDate = None
    IsPermanentFoster = 0
    Comments = ""
    RecordVersion = 0
    CreatedBy = "conversion"
    CreatedDate = today()
    LastChangedBy = "conversion"
    LastChangedDate = today()
    def __init__(self, ID = 0):
        self.ID = ID
        if ID == 0: self.ID = getid("adoption")
        self.AdoptionNumber = self.ID
    def __str__(self):
        s = (
            ( "ID", di(self.ID) ),
            ( "AdoptionNumber", ds(self.AdoptionNumber) ),
            ( "AnimalID", di(self.AnimalID) ),
            ( "OwnerID", di(self.OwnerID) ),
            ( "RetailerID", di(self.RetailerID) ),
            ( "OriginalRetailerMovementID", di(self.OriginalRetailerMovementID) ),
            ( "MovementDate", dd(self.MovementDate) ),
            ( "MovementType", di(self.MovementType) ),
            ( "ReturnDate", dd(self.ReturnDate) ),
            ( "ReturnedReasonID", di(self.ReturnedReasonID) ),
            ( "ReturnedByOwnerID", di(self.ReturnedByOwnerID) ),
            ( "InsuranceNumber", ds(self.InsuranceNumber) ),
            ( "ReasonForReturn", ds(self.ReasonForReturn) ),
            ( "ReservationDate", dd(self.ReservationDate) ),
            ( "Donation", df(self.Donation) ),
            ( "ReservationCancelledDate", dd(self.ReservationCancelledDate) ),
            ( "IsTrial", di(self.IsTrial) ),
            ( "TrialEndDate", dd(self.TrialEndDate) ),
            ( "IsPermanentFoster", di(self.IsPermanentFoster) ),
            ( "Comments", ds(self.Comments) ),
            ( "RecordVersion", di(self.RecordVersion) ),
            ( "CreatedBy", ds(self.CreatedBy) ),
            ( "CreatedDate", dd(self.CreatedDate) ),
            ( "LastChangedBy", ds(self.LastChangedBy) ),
            ( "LastChangedDate", dd(self.LastChangedDate) )
            )
        sql = makesql("adoption", s)
        # Close any existing movements for this animal
        sql += "\nUPDATE adoption SET ReturnDate = %s WHERE ID <> %s AND AnimalID = %s AND ReturnDate Is Null;" % ( dd(self.MovementDate), di(self.ID), di(self.AnimalID))
        return sql

class Owner:
    ID = 0
    OwnerType = 1
    OwnerCode = ""
    OwnerTitle = ""
    OwnerInitials = ""
    OwnerForeNames = ""
    OwnerSurname = ""
    OwnerTitle2 = ""
    OwnerInitials2 = ""
    OwnerForeNames2 = ""
    OwnerSurname2 = ""
    OwnerName = ""
    OwnerAddress = ""
    OwnerTown = ""
    OwnerCounty = ""
    OwnerPostcode = ""
    HomeTelephone = ""
    WorkTelephone = ""
    MobileTelephone = ""
    EmailAddress = ""
    WorkTelephone2 = ""
    MobileTelephone2 = ""
    EmailAddress2 = ""
    DateOfBirth = None
    DateOfBirth2 = None
    IdentificationNumber = ""
    IdentificationNumber2 = ""
    LatLong = ""
    IDCheck = 0
    Comments = ""
    IsBanned = 0
    IsVolunteer = 0
    IsHomeChecker = 0
    IsMember = 0
    MembershipExpiryDate = None
    MembershipNumber = ""
    IsDonor = 0
    IsShelter = 0
    IsACO = 0
    IsStaff = 0
    IsFosterer = 0
    IsRetailer = 0
    IsVet = 0
    IsGiftAid = 0
    IsDeceased = 0
    IsSponsor = 0
    ExcludeFromBulkEmail = 0
    GDPRContactOptIn = ""
    HomeCheckAreas = ""
    DateLastHomeChecked = None
    HomeCheckedBy = 0
    MatchAdded = None
    MatchExpires = None
    MatchActive = 0
    MatchSex = 0
    MatchSize = 0
    MatchAgeFrom = 0
    MatchAgeTo = 0
    MatchAnimalType = 0
    MatchSpecies = 0
    MatchBreed = 0
    MatchBreed2 = 0
    MatchGoodWithCats = 0
    MatchGoodWithDogs = 0
    MatchGoodWithChildren = 0
    MatchHouseTrained = 0
    MatchCommentsContain = ""
    AdditionalFlags = ""
    RecordVersion = 0
    CreatedBy = "conversion"
    CreatedDate = today()
    LastChangedBy = "conversion"
    LastChangedDate = today()
    ExtraID = ""
    def __init__(self, ID = 0):
        self.ID = ID
        if ID == 0: self.ID = getid("owner")
    def SplitName(self, name, lastwordassurname = True):
        """
        Uses the last word as surname and first ones as
        forenames, sets ownername.
        if lastwordassurname is False, uses first word as forenames and
        everything else as surname.
        """
        self.OwnerName = name
        lastspace = name.rfind(" ")
        if lastwordassurname == False: lastspace = name.find(" ")
        if lastspace == -1:
            self.OwnerSurname = name
        else:
            self.OwnerForeNames = name[0:lastspace]
            self.OwnerSurname = name[lastspace+1:]
    def __str__(self):
        if self.OwnerName.strip() == "":
            if self.OwnerForeNames.strip() != "" and self.OwnerSurname2.strip() == "":
                self.OwnerType = 1  # Individual
                self.OwnerName = "%s %s" % (self.OwnerForeNames, self.OwnerSurname)
            elif self.OwnerSurname2.strip() != "":
                self.OwnerName = "%s %s & %s %s" % (self.OwnerForeNames, self.OwnerSurname, self.OwnerForeNames2, self.OwnerSurname2)
                self.OwnerType = 3 # Couple
            else:
                self.OwnerName = self.OwnerSurname
                self.OwnerType = 2 # Organisation
        if self.OwnerCode.strip() == "":
            prefix = "XX"
            if self.OwnerSurname and len(self.OwnerSurname) >= 2 and not self.OwnerSurname.startswith("&"):
                prefix = self.OwnerSurname[0:2].upper()
            self.OwnerCode = "%s%s" % (prefix, padleft(self.ID, 6))
        s = (
            ( "ID", di(self.ID) ),
            ( "OwnerType", di(self.OwnerType) ),
            ( "OwnerCode", ds(self.OwnerCode) ),
            ( "OwnerTitle", ds(self.OwnerTitle) ),
            ( "OwnerInitials", ds(self.OwnerInitials) ),
            ( "OwnerForeNames", ds(self.OwnerForeNames) ),
            ( "OwnerSurname", ds(self.OwnerSurname) ),
            ( "OwnerTitle2", ds(self.OwnerTitle2) ),
            ( "OwnerInitials2", ds(self.OwnerInitials2) ),
            ( "OwnerForeNames2", ds(self.OwnerForeNames2) ),
            ( "OwnerSurname2", ds(self.OwnerSurname2) ),
            ( "OwnerName", ds(self.OwnerName) ),
            ( "OwnerAddress", ds(self.OwnerAddress) ),
            ( "OwnerTown", ds(self.OwnerTown) ),
            ( "OwnerCounty", ds(self.OwnerCounty) ),
            ( "OwnerPostcode", ds(self.OwnerPostcode) ),
            ( "HomeTelephone", ds(self.HomeTelephone) ),
            ( "WorkTelephone", ds(self.WorkTelephone) ),
            ( "MobileTelephone", ds(self.MobileTelephone) ),
            ( "EmailAddress", ds(self.EmailAddress) ),
            ( "WorkTelephone2", ds(self.WorkTelephone2) ),
            ( "MobileTelephone2", ds(self.MobileTelephone2) ),
            ( "EmailAddress2", ds(self.EmailAddress2) ),
            ( "DateOfBirth", dd(self.DateOfBirth) ),
            ( "DateOfBirth2", dd(self.DateOfBirth2) ),
            ( "IdentificationNumber", ds(self.IdentificationNumber) ),
            ( "IdentificationNumber2", ds(self.IdentificationNumber2) ),
            ( "LatLong", ds(self.LatLong) ),
            ( "IDCheck", di(self.IDCheck) ),
            ( "Comments", ds(self.Comments) ),
            ( "IsBanned", di(self.IsBanned) ),
            ( "IsVolunteer", di(self.IsVolunteer) ),
            ( "IsHomeChecker", di(self.IsHomeChecker) ),
            ( "IsMember", di(self.IsMember) ),
            ( "MembershipExpiryDate", dd(self.MembershipExpiryDate) ),
            ( "MembershipNumber", ds(self.MembershipNumber) ),
            ( "IsDonor", di(self.IsDonor) ),
            ( "IsShelter", di(self.IsShelter) ),
            ( "IsACO", di(self.IsACO) ),
            ( "IsStaff", di(self.IsStaff) ),
            ( "IsFosterer", di(self.IsFosterer) ),
            ( "IsRetailer", di(self.IsRetailer) ),
            ( "IsVet", di(self.IsVet) ),
            ( "IsGiftAid", di(self.IsGiftAid) ),
            ( "IsDeceased", di(self.IsDeceased) ),
            ( "IsSponsor", di(self.IsSponsor) ),
            ( "ExcludeFromBulkEmail", di(self.ExcludeFromBulkEmail) ),
            ( "GDPRContactOptIn", ds(self.GDPRContactOptIn) ),
            ( "HomeCheckAreas", ds(self.HomeCheckAreas) ),
            ( "DateLastHomeChecked", dd(self.DateLastHomeChecked) ),
            ( "HomeCheckedBy", di(self.HomeCheckedBy) ),
            ( "MatchAdded", dd(self.MatchAdded) ),
            ( "MatchExpires", dd(self.MatchExpires) ),
            ( "MatchActive", di(self.MatchActive) ),
            ( "MatchSex", di(self.MatchSex) ),
            ( "MatchSize", di(self.MatchSize) ),
            ( "MatchAgeFrom", df(self.MatchAgeFrom) ),
            ( "MatchAgeTo", df(self.MatchAgeTo) ),
            ( "MatchAnimalType", di(self.MatchAnimalType) ),
            ( "MatchSpecies", di(self.MatchSpecies) ),
            ( "MatchBreed", di(self.MatchBreed) ),
            ( "MatchBreed2", di(self.MatchBreed2) ),
            ( "MatchGoodWithCats", di(self.MatchGoodWithCats) ),
            ( "MatchGoodWithDogs", di(self.MatchGoodWithDogs) ),
            ( "MatchGoodWithChildren", di(self.MatchGoodWithChildren) ),
            ( "MatchHouseTrained", di(self.MatchHouseTrained) ),
            ( "MatchCommentsContain", ds(self.MatchCommentsContain) ),
            ( "AdditionalFlags", ds(self.AdditionalFlags) ),
            ( "RecordVersion", di(self.RecordVersion) ),
            ( "CreatedBy", ds(self.CreatedBy) ),
            ( "CreatedDate", dd(self.CreatedDate) ),
            ( "LastChangedBy", ds(self.LastChangedBy) ),
            ( "LastChangedDate", dd(self.LastChangedDate) )
            )
        #sys.stderr.write("owner: %d %s, %s, %s, %s %s, %s, %s\n" % (self.ID, self.OwnerName, self.OwnerAddress, self.OwnerTown, self.OwnerCounty, self.OwnerPostcode, self.EmailAddress, self.HomeTelephone))
        return makesql("owner", s)

class OwnerDonation:
    ID = 0
    ReceiptNumber = ""
    ChequeNumber = ""
    AnimalID = 0
    OwnerID = 0
    MovementID = 0
    DonationTypeID = 1
    DonationPaymentID = 1
    Date = None
    DateDue = None
    Quantity = 0
    UnitPrice = 0
    Donation = 0
    IsGiftAid = 0
    Frequency = 0
    NextCreated = 0
    Comments = ""
    RecordVersion = 0
    CreatedBy = "conversion"
    CreatedDate = today()
    LastChangedBy = "conversion"
    LastChangedDate = today()
    def __init__(self, ID = 0):
        self.ID = ID
        if ID == 0: self.ID = getid("ownerdonation")
    def __str__(self):
        if self.ReceiptNumber == "":
            self.ReceiptNumber = padleft(self.ID, 8)
        s = (
            ( "ID", di(self.ID) ),
            ( "ReceiptNumber", ds(self.ReceiptNumber) ),
            ( "ChequeNumber", ds(self.ChequeNumber) ),
            ( "AnimalID", di(self.AnimalID) ),
            ( "OwnerID", di(self.OwnerID) ),
            ( "MovementID", di(self.MovementID) ),
            ( "DonationTypeID", di(self.DonationTypeID) ),
            ( "DonationPaymentID", di(self.DonationPaymentID) ),
            ( "Date", dd(self.Date) ),
            ( "DateDue", dd(self.DateDue) ),
            ( "Quantity", di(self.Quantity) ),
            ( "UnitPrice", di(self.UnitPrice) ),
            ( "Donation", df(self.Donation) ),
            ( "IsGiftAid", di(self.IsGiftAid) ),
            ( "Frequency", di(self.Frequency) ),
            ( "NextCreated", di(self.NextCreated) ),
            ( "Comments", ds(self.Comments) ),
            ( "RecordVersion", di(self.RecordVersion) ),
            ( "CreatedBy", ds(self.CreatedBy) ),
            ( "CreatedDate", dd(self.CreatedDate) ),
            ( "LastChangedBy", ds(self.LastChangedBy) ),
            ( "LastChangedDate", dd(self.LastChangedDate) )
            )
        return makesql("ownerdonation", s)

class OwnerLicence:
    ID = 0
    OwnerID = 0
    AnimalID = 0
    LicenceTypeID = 1
    LicenceNumber = ""
    LicenceFee = 0
    IssueDate = None
    ExpiryDate = None
    Token = ""
    Renewed = 1
    Comments = ""
    RecordVersion = 0
    CreatedBy = "conversion"
    CreatedDate = today()
    LastChangedBy = "conversion"
    LastChangedDate = today()
    def __init__(self, ID = 0):
        self.ID = ID
        if ID == 0: self.ID = getid("ownerlicence")
    def __str__(self):
        if self.Token == "": self.Token = uuid_b64()
        s = (
            ( "ID", di(self.ID) ),
            ( "OwnerID", di(self.OwnerID) ),
            ( "AnimalID", di(self.AnimalID) ),
            ( "LicenceTypeID", di(self.LicenceTypeID) ),
            ( "LicenceNumber", ds(self.LicenceNumber) ),
            ( "LicenceFee", di(self.LicenceFee) ),
            ( "IssueDate", dd(self.IssueDate) ),
            ( "ExpiryDate", dd(self.ExpiryDate) ),
            ( "Token", ds(self.Token) ),
            ( "Renewed", di(self.Renewed) ),
            ( "Comments", ds(self.Comments) ),
            ( "RecordVersion", di(self.RecordVersion) ),
            ( "CreatedBy", ds(self.CreatedBy) ),
            ( "CreatedDate", dd(self.CreatedDate) ),
            ( "LastChangedBy", ds(self.LastChangedBy) ),
            ( "LastChangedDate", dd(self.LastChangedDate) )
            )
        return makesql("ownerlicence", s)

class StockLevel:
    ID = 0
    Name = ""
    Description = ""
    StockLocationID = 1
    UnitName = ""
    Total = 0
    Balance = 0
    Expiry= None
    BatchNumber = ""
    Cost = 0
    UnitPrice = 0
    CreatedDate = None
    def __init__(self, ID = 0):
        self.ID = ID
        if ID == 0: self.ID = getid("stocklevel")
    def __str__(self):
        s = (
            ( "ID", di(self.ID) ),
            ( "Name", ds(self.Name) ),
            ( "Description", ds(self.Description) ),
            ( "StockLocationID", di(self.StockLocationID) ),
            ( "UnitName", ds(self.UnitName) ),
            ( "Total", di(self.Total) ),
            ( "Balance", di(self.Balance) ),
            ( "Expiry", dd(self.Expiry) ),
            ( "BatchNumber", ds(self.BatchNumber) ),
            ( "Cost", di(self.Cost) ),
            ( "UnitPrice", di(self.UnitPrice) ),
            ( "CreatedDate", dd(self.CreatedDate) )
            )
        return makesql("stocklevel", s)



# Dictionary of entry reasons
entryreasons = {
    "Marriage/Relationship split": EntryReason(1, "Marriage/Relationship split"),
    "Allergies": EntryReason(2, "Allergies"),
    "Biting": EntryReason(3, "Biting"),
    "Unable to Cope": EntryReason(4, "Unable to Cope"),
    "Unsuitable Accommodation": EntryReason(5, "Unsuitable Accommodation"),
    "Died": EntryReason(6, "Died"),
    "Stray": EntryReason(7, "Stray"),
    "Sick/Injured": EntryReason(8, "Sick/Injured"),
    "Unable to Afford": EntryReason(9, "Unable to Afford"),
    "Abuse": EntryReason(10, "Abuse"),
    "Abandoned": EntryReason(11, "Abandoned"),
    "Boarding": EntryReason(12, "Boarding"),
    "Born in Shelter": EntryReason(13, "Born in Shelter"),
    "TNR - Trap/Neuter/Release": EntryReason(14, "TNR - Trap/Neuter/Release"),
    "Transfer from Other Shelter": EntryReason(15, "Transfer from Other Shelter"),
    "Transfer from Municipal Shelter": EntryReason(16, "Transfer from Municipal Shelter"),
    "Surrender": EntryReason(17, "Surrender"),
    "Too Many Animals": EntryReason(18, "Too Many Animals")
}

# Dictionary of donation types
donationtypes = {
    "Donation": DonationType(1, "Donation"),
    "Adoption Fee": DonationType(2, "Adoption Fee"),
    "Waiting List Donation": DonationType(3, "Waiting List Donation"),
    "Entry Donation": DonationType(4, "Entry Donation"),
    "Animal Sponsorship": DonationType(5, "Animal Sponsorship"),
    "In-Kind Donation": DonationType(6, "In-Kind Donation")
}

# Dictionary of test types
testtypes = {
    "FIV": TestType(1, "FIV"),
    "FLV": TestType(2, "FLV"),
    "Heartworm": TestType(3, "Heartworm")
}

# Dictionary of vaccination types
vaccinationtypes = {
    "Distemper": VaccinationType(1, "Distemper"),
    "Hepatitis": VaccinationType(2, "Hepatitis"),
    "Leptospirosis": VaccinationType(3, "Leptospirosis"),
    "Rabies": VaccinationType(4, "Rabies"),
    "Parainfluenza": VaccinationType(5, "Parainfluenza"),
    "Bordetella": VaccinationType(6, "Bordetella"), 
    "Parvovirus": VaccinationType(7, "Parvovirus"),
    "DHLPP": VaccinationType(8, "DHLPP"),
    "FVRCP": VaccinationType(9, "FVRCP"),
    "Chlamydophila": VaccinationType(10, "Chlamydophila"),
    "FIV": VaccinationType(11, "FIV"),
    "FeLV": VaccinationType(12, "FeLV"),
    "FIPV": VaccinationType(13, "FIPV"),
    "FECV/FeCoV": VaccinationType(14, "FECV/FeCoV")
}


