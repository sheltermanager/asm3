#!/usr/bin/python

import additional
import al
import animal
import async
import configuration
import dbfs
import diary
import log
import media
import reports
import utils
import waitinglist
from i18n import _, date_diff_days, now, subtract_years, python2display

class LostFoundMatch:
    dbo = None
    lid = 0
    lcontactname = ""
    lcontactnumber = ""
    larealost = ""
    lareapostcode = ""
    lagegroup = ""
    lsexid = 0
    lsexname = ""
    lspeciesid = 0
    lspeciesname = ""
    lbreedid = 0
    lbreedname = ""
    ldistinguishingfeatures = ""
    lbasecolourid = 0
    lbasecolourname = ""
    ldatelost = None
    fid = 0
    fanimalid = 0
    fcontactname = ""
    fcontactnumber = ""
    fareafound = ""
    fareapostcode = ""
    fagegroup = ""
    fsexid = 0
    fsexname = ""
    fspeciesid = 0
    fspeciesname = ""
    fbreedid = 0
    fbreedname = ""
    fdistinguishingfeatures = ""
    fbasecolourid = 0
    fbasecolourname = ""
    fdatefound = None
    matchpoints = 0
    def __init__(self, dbo):
        self.dbo = dbo
    def toParams(self):
        """ Returns batch parameters for database insert """
        return (self.lid, self.fid, self.fanimalid, self.lcontactname, self.lcontactnumber, self.larealost, self.lareapostcode, self.lagegroup,
                self.lsexid, self.lspeciesid, self.lbreedid, self.ldistinguishingfeatures, self.lbasecolourid, self.ldatelost, self.fcontactname,
                self.fcontactnumber, self.fareafound, self.fareapostcode, self.fagegroup, self.fsexid, self.fspeciesid, self.fbreedid,
                self.fdistinguishingfeatures, self.fbasecolourid, self.fdatefound, self.matchpoints)

def get_foundanimal_query(dbo):
    return "SELECT a.*, a.ID AS LFID, s.SpeciesName, b.BreedName, " \
        "c.BaseColour AS BaseColourName, c.AdoptAPetColour, x.Sex AS SexName, " \
        "o.OwnerSurname, o.OwnerForeNames, o.OwnerTitle, o.OwnerInitials, " \
        "o.OwnerName, o.OwnerPostcode, o.HomeTelephone, o.WorkTelephone, o.MobileTelephone, " \
        "web.ID AS WebsiteMediaID, " \
        "web.MediaName AS DocMediaName, " \
        "web.Date AS DocMediaDate, " \
        "web.MediaName AS WebsiteMediaName, " \
        "web.Date AS WebsiteMediaDate, " \
        "web.MediaNotes AS WebsiteMediaNotes " \
        "FROM animalfound a " \
        "LEFT OUTER JOIN breed b ON a.BreedID = b.ID " \
        "LEFT OUTER JOIN species s ON a.AnimalTypeID = s.ID " \
        "LEFT OUTER JOIN basecolour c ON a.BaseColourID = c.ID " \
        "LEFT OUTER JOIN lksex x ON a.Sex = x.ID " \
        "LEFT OUTER JOIN media web ON web.LinkID = a.ID AND web.LinkTypeID = %d AND web.WebsitePhoto = 1 " \
        "LEFT OUTER JOIN owner o ON a.OwnerID = o.ID" % media.FOUNDANIMAL

def get_lostanimal_query(dbo):
    return "SELECT a.*, a.ID AS LFID, s.SpeciesName, b.BreedName, " \
        "c.BaseColour AS BaseColourName, c.AdoptAPetColour, x.Sex AS SexName, " \
        "o.OwnerSurname, o.OwnerForeNames, o.OwnerTitle, o.OwnerInitials, " \
        "o.OwnerName, o.OwnerPostcode, o.HomeTelephone, o.WorkTelephone, o.MobileTelephone, " \
        "web.ID AS WebsiteMediaID, " \
        "web.MediaName AS DocMediaName, " \
        "web.Date AS DocMediaDate, " \
        "web.MediaName AS WebsiteMediaName, " \
        "web.Date AS WebsiteMediaDate, " \
        "web.MediaNotes AS WebsiteMediaNotes " \
        "FROM animallost a " \
        "LEFT OUTER JOIN breed b ON a.BreedID = b.ID " \
        "LEFT OUTER JOIN species s ON a.AnimalTypeID = s.ID " \
        "LEFT OUTER JOIN basecolour c ON a.BaseColourID = c.ID " \
        "LEFT OUTER JOIN lksex x ON a.Sex = x.ID " \
        "LEFT OUTER JOIN media web ON web.LinkID = a.ID AND web.LinkTypeID = %d AND web.WebsitePhoto = 1 " \
        "LEFT OUTER JOIN owner o ON a.OwnerID = o.ID" % media.LOSTANIMAL

def get_lostanimal(dbo, aid):
    """
    Returns a lost animal record
    """
    return dbo.first_row( dbo.query(get_lostanimal_query(dbo) + " WHERE a.ID = %d" % int(aid)) )

def get_foundanimal(dbo, aid):
    """
    Returns a found animal record
    """
    return dbo.first_row( dbo.query(get_foundanimal_query(dbo) + " WHERE a.ID = %d" % int(aid)) )

def get_lostanimal_find_simple(dbo, query = "", limit = 0):
    """
    Returns rows for simple lost animal searches.
    query: The search criteria
    """
    ors = []
    values = []
    query = query.replace("'", "`")
    querylike = "%%%s%%" % query.lower()
    def add(field):
        ors.append("(LOWER(%s) LIKE ? OR LOWER(%s) LIKE ?)" % (field, field))
        values.append(querylike)
        values.append(utils.decode_html(querylike))
    def addclause(clause):
        ors.append(clause)
        values.append(querylike)
    # If no query has been given, show unfound lost animal records
    # for the last 30 days
    if query == "":
        ors.append("a.DateLost > ? AND a.DateFound Is Null")
        values.append(dbo.today(offset=-30))
    else:
        if utils.is_numeric(query):
            ors.append("a.ID = ?")
            values.append(utils.cint(query))
        add("o.OwnerName")
        add("a.AreaLost")
        add("a.AreaPostcode")
        addclause("EXISTS(SELECT ad.Value FROM additional ad " \
            "INNER JOIN additionalfield af ON af.ID = ad.AdditionalFieldID AND af.Searchable = 1 " \
            "WHERE ad.LinkID=a.ID AND ad.LinkType IN (%s) AND LOWER(ad.Value) LIKE ?)" % additional.LOSTANIMAL_IN)
        if not dbo.is_large_db:
            add("b.BreedName")
            add("a.DistFeat")
            add("a.Comments")
    sql = "%s WHERE %s" % (get_lostanimal_query(dbo), " OR ".join(ors))
    return dbo.query(sql, values, limit=limit, distincton="ID")

def get_foundanimal_find_simple(dbo, query = "", limit = 0):
    """
    Returns rows for simple found animal searches.
    query: The search criteria
    """
    ors = []
    values = []
    query = query.replace("'", "`")
    querylike = "%%%s%%" % query.lower()
    def add(field):
        ors.append("(LOWER(%s) LIKE ? OR LOWER(%s) LIKE ?)" % (field, field))
        values.append(querylike)
        values.append(utils.decode_html(querylike))
    def addclause(clause):
        ors.append(clause)
        values.append(querylike)
    # If no query has been given, show unfound lost animal records
    # for the last 30 days
    if query == "":
        ors.append("a.DateFound > ? AND a.ReturnToOwnerDate Is Null")
        values.append(dbo.today(offset=-30))
    else:
        if utils.is_numeric(query):
            ors.append("a.ID = ?")
            values.append(utils.cint(query))
        add("o.OwnerName")
        add("a.AreaFound")
        add("a.AreaPostcode")
        addclause("EXISTS(SELECT ad.Value FROM additional ad " \
            "INNER JOIN additionalfield af ON af.ID = ad.AdditionalFieldID AND af.Searchable = 1 " \
            "WHERE ad.LinkID=a.ID AND ad.LinkType IN (%s) AND LOWER(ad.Value) LIKE ?)" % additional.FOUNDANIMAL_IN)
        if not dbo.is_large_db:
            add("b.BreedName")
            add("a.DistFeat")
            add("a.Comments")
    sql = "%s WHERE %s" % (get_foundanimal_query(dbo), " OR ".join(ors))
    return dbo.query(sql, values, limit=limit, distincton="ID")

def get_lostanimal_find_advanced(dbo, criteria, limit = 0):
    """
    Returns rows for advanced lost animal searches.
    criteria: A dictionary of criteria
       number - string partial pattern
       contact - string partial pattern
       area - string partial pattern
       postcode - string partial pattern
       features - string partial pattern
       agegroup - agegroup text to match
       sex - -1 for all or ID
       species - -1 for all or ID
       breed - -1 for all or ID
       colour - -1 for all or ID
       excludecomplete - 1 for yes
       datefrom - lost date from in current display locale format
       dateto - lost date to in current display locale format
       completefrom - found date from in current display locale format
       completeto - found date to in current display locale format
    """
    ands = []
    values = []
    l = dbo.locale
    post = utils.PostedData(criteria, l)

    def addid(cfield, field): 
        if post[cfield] != "" and post.integer(cfield) > -1:
            ands.append("%s = ?" % field)
            values.append(post.integer(cfield))

    def addstr(cfield, field): 
        if post[cfield] != "":
            x = post[cfield].lower().replace("'", "`")
            x = "%%%s%%" % x
            ands.append("(LOWER(%s) LIKE ? OR LOWER(%s) LIKE ?)" % (field, field))
            values.append(x)
            values.append(utils.decode_html(x))

    def adddate(cfieldfrom, cfieldto, field): 
        if post[cfieldfrom] != "" and post[cfieldto] != "":
            post.data["dayend"] = "23:59:59"
            ands.append("%s >= ? AND %s <= ?" % (field, field))
            values.append(post.date(cfieldfrom))
            values.append(post.datetime(cfieldto, "dayend"))

    def addfilter(f, condition):
        if post["filter"].find(f) != -1: ands.append(condition)

    def addcomp(cfield, value, condition):
        if post[cfield] == value: ands.append(condition)

    def addwords(cfield, field):
        if post[cfield] != "":
            words = post[cfield].split(" ")
            for w in words:
                x = w.lower().replace("'", "`")
                x = "%%%s%%" % x
                ands.append("(LOWER(%s) LIKE ? OR LOWER(%s) LIKE ?)" % (field, field))
                values.append(x)
                values.append(utils.decode_html(x))

    ands.append("a.ID > 0")
    addid("number", "a.ID")
    addstr("contact", "o.OwnerName")
    addstr("area", "a.AreaLost")
    addstr("postcode", "a.AreaPostcode")
    addstr("features", "a.DistFeat")
    if post["agegroup"] != "-1": addstr("agegroup", "a.AgeGroup")
    addid("sex", "a.Sex")
    addid("species", "a.AnimalTypeID")
    addid("breed", "a.BreedID")
    addid("colour", "a.BaseColourID")
    adddate("datefrom", "dateto", "a.DateLost")
    adddate("completefrom", "completeto", "a.DateFound")
    if post["excludecomplete"] == "1":
        ands.append("a.DateFound Is Null")
    where = " WHERE " + " AND ".join(ands)
    sql = "%s %s ORDER BY a.ID" % (get_lostanimal_query(dbo), where)
    return dbo.query(sql, values, limit=limit, distincton="ID")

def get_foundanimal_find_advanced(dbo, criteria, limit = 0):
    """
    Returns rows for advanced lost animal searches.
    criteria: A dictionary of criteria
       number - string partial pattern
       contact - string partial pattern
       area - string partial pattern
       postcode - string partial pattern
       features - string partial pattern
       agegroup - agegroup text to match
       sex - -1 for all or ID
       species - -1 for all or ID
       breed - -1 for all or ID
       colour - -1 for all or ID
       excludecomplete - 1 for yes
       datefrom - lost date from in current display locale format
       dateto - lost date to in current display locale format
       completefrom - returned date from in current display locale format
       completeto - returned date to in current display locale format
    """
    ands = []
    values = []
    l = dbo.locale
    post = utils.PostedData(criteria, l)

    def addid(cfield, field): 
        if post[cfield] != "" and post.integer(cfield) > -1:
            ands.append("%s = ?" % field)
            values.append(post.integer(cfield))

    def addstr(cfield, field): 
        if post[cfield] != "":
            x = post[cfield].lower().replace("'", "`")
            x = "%%%s%%" % x
            ands.append("(LOWER(%s) LIKE ? OR LOWER(%s) LIKE ?)" % (field, field))
            values.append(x)
            values.append(utils.decode_html(x))

    def adddate(cfieldfrom, cfieldto, field): 
        if post[cfieldfrom] != "" and post[cfieldto] != "":
            post.data["dayend"] = "23:59:59"
            ands.append("%s >= ? AND %s <= ?" % (field, field))
            values.append(post.date(cfieldfrom))
            values.append(post.datetime(cfieldto, "dayend"))

    def addfilter(f, condition):
        if post["filter"].find(f) != -1: ands.append(condition)

    def addcomp(cfield, value, condition):
        if post[cfield] == value: ands.append(condition)

    def addwords(cfield, field):
        if post[cfield] != "":
            words = post[cfield].split(" ")
            for w in words:
                x = w.lower().replace("'", "`")
                x = "%%%s%%" % x
                ands.append("(LOWER(%s) LIKE ? OR LOWER(%s) LIKE ?)" % (field, field))
                values.append(x)
                values.append(utils.decode_html(x))

    ands.append("a.ID > 0")
    addid("number", "a.ID")
    addstr("contact", "o.OwnerName")
    addstr("area", "a.AreaFound")
    addstr("postcode", "a.AreaPostcode")
    addstr("features", "a.DistFeat")
    if post["agegroup"] != "-1": addstr("agegroup", "a.AgeGroup")
    addid("sex", "a.Sex")
    addid("species", "a.AnimalTypeID")
    addid("breed", "a.BreedID")
    addid("colour", "a.BaseColourID")
    adddate("datefrom", "dateto", "a.DateFound")
    adddate("completefrom", "completeto", "a.ReturnToOwnerDate")
    if post["excludecomplete"] == "1":
        ands.append("a.ReturnToOwnerDate Is Null")
    where = " WHERE " + " AND ".join(ands)
    sql = "%s %s ORDER BY a.ID" % (get_foundanimal_query(dbo), where)
    return dbo.query(sql, values, limit=limit, distincton="ID")

def get_lostanimal_last_days(dbo, days = 90):
    """
    Returns lost animals active for the last X days
    """
    return dbo.query(get_lostanimal_query(dbo) + " WHERE a.DateLost > ? AND a.DateFound Is Null", [dbo.today(offset=days*-1)])

def get_foundanimal_last_days(dbo, days = 90):
    """
    Returns found animals active for the last X days
    """
    return dbo.query(get_foundanimal_query(dbo) + " WHERE a.DateFound > ? AND a.ReturnToOwnerDate Is Null", [dbo.today(offset=days*-1)])

def get_lostanimal_satellite_counts(dbo, lfid):
    """
    Returns a resultset containing the number of each type of satellite
    record that a lost animal entry has.
    """
    sql = "SELECT a.ID, " \
        "(SELECT COUNT(*) FROM media me WHERE me.LinkID = a.ID AND me.LinkTypeID = %d) AS media, " \
        "(SELECT COUNT(*) FROM diary di WHERE di.LinkID = a.ID AND di.LinkType = %d) AS diary, " \
        "(SELECT COUNT(*) FROM log WHERE log.LinkID = a.ID AND log.LinkType = %d) AS logs " \
        "FROM animallost a WHERE a.ID = ?" \
        % (media.LOSTANIMAL, diary.LOSTANIMAL, log.LOSTANIMAL)
    return dbo.query(sql, [lfid])

def get_foundanimal_satellite_counts(dbo, lfid):
    """
    Returns a resultset containing the number of each type of satellite
    record that a found animal entry has.
    """
    sql = "SELECT a.ID, " \
        "(SELECT COUNT(*) FROM media me WHERE me.LinkID = a.ID AND me.LinkTypeID = %d) AS media, " \
        "(SELECT COUNT(*) FROM diary di WHERE di.LinkID = a.ID AND di.LinkType = %d) AS diary, " \
        "(SELECT COUNT(*) FROM log WHERE log.LinkID = a.ID AND log.LinkType = %d) AS logs " \
        "FROM animalfound a WHERE a.ID = ?" \
        % (media.FOUNDANIMAL, diary.FOUNDANIMAL, log.FOUNDANIMAL)
    return dbo.query(sql, [lfid])

def send_email_from_form(dbo, username, post):
    """
    Sends an email to a lost/found person from a posted form. Attaches it as
    a log entry if specified.
    """
    emailfrom = post["from"]
    emailto = post["to"]
    emailcc = post["cc"]
    subject = post["subject"]
    ishtml = post.boolean("html")
    addtolog = post.boolean("addtolog")
    logtype = post.integer("logtype")
    body = post["body"]
    rv = utils.send_email(dbo, emailfrom, emailto, emailcc, subject, body, ishtml == 1 and "html" or "plain")
    if addtolog == 1:
        log.add_log(dbo, username, post["lfmode"] == "lost" and log.LOSTANIMAL or log.FOUNDANIMAL, post.integer("lfid"), logtype, body)
    return rv

def words(str1, str2, maxpoints):
    """
    Evalutes words in string 1 for appearances in string 2
    Returns the number of points for 1 to 2 as a percentage of maxpoints
    """
    if str1 is None: str1 = ""
    if str2 is None: str2 = ""
    str1 = str1.replace(",", " ").replace("\n", " ").lower().strip()
    str2 = str2.replace(",", " ").replace("\n", " ").lower().strip()
    matches = 0
    s1words = str1.split(" ")
    s2words = str2.split(" ")
    for w in s1words:
        if w in s2words: 
            matches += 1
    return int((float(matches) / float(len(s1words))) * float(maxpoints))

def match(dbo, lostanimalid = 0, foundanimalid = 0, animalid = 0, limit = 0):
    """
    Performs a lost and found match by going through all lost animals
    lostanimalid:   Compare this lost animal against all found animals
    foundanimalid:  Compare all lost animals against this found animal
    animalid:       Compare all lost animals against this shelter animal
    limit:          Stop when we hit this many matches (or 0 for all)
    returns a list of LostFoundMatch objects
    """
    l = dbo.locale
    batch = []
    matches = []
    matchspecies = configuration.match_species(dbo)
    matchbreed = configuration.match_breed(dbo)
    matchage = configuration.match_age(dbo)
    matchsex = configuration.match_sex(dbo)
    matcharealost = configuration.match_area_lost(dbo)
    matchfeatures = configuration.match_features(dbo)
    matchpostcode = configuration.match_postcode(dbo)
    matchcolour = configuration.match_colour(dbo)
    matchdatewithin2weeks = configuration.match_within2weeks(dbo)
    matchmax = matchspecies + matchbreed + matchage + matchsex + \
        matcharealost + matchfeatures + matchpostcode + matchcolour + \
        matchdatewithin2weeks
    matchpointfloor = configuration.match_point_floor(dbo)
    includeshelter = configuration.match_include_shelter(dbo)
    fullmatch = animalid == 0 and lostanimalid == 0 and foundanimalid == 0
    # Ignore records older than 6 months to keep things useful
    giveup = dbo.today(offset=-182)

    # Get our set of lost animals
    lostanimals = None
    if lostanimalid == 0:
        lostanimals = dbo.query(get_lostanimal_query(dbo) + \
            " WHERE a.DateFound Is Null AND a.DateLost > ? ORDER BY a.DateLost", [giveup])
    else:
        lostanimals = dbo.query(get_lostanimal_query(dbo) + \
            " WHERE a.ID = ?", [lostanimalid])

    oldestdate = giveup
    if len(lostanimals) > 0:
        oldestdate = lostanimals[0].DATELOST

    # Get the set of found animals for comparison
    foundanimals = None
    if foundanimalid == 0:
        foundanimals = dbo.query(get_foundanimal_query(dbo) + \
            " WHERE a.ReturnToOwnerDate Is Null" \
            " AND a.DateFound >= ? ", [oldestdate])
    else:
        foundanimals = dbo.query(get_foundanimal_query(dbo) + " WHERE a.ID = ?", [foundanimalid])

    # Get the set of shelter animals for comparison - anything brought in recently
    # that's 1. still on shelter or 2. was released to wild, transferred or escaped
    shelteranimals = None
    if includeshelter:
        if animalid == 0:
            shelteranimals = dbo.query(animal.get_animal_query(dbo) + " WHERE " + \
                "(a.Archived = 0 OR a.ActiveMovementType IN (3,4,7)) " \
                "AND a.DateBroughtIn > ?", [oldestdate])
        else:
            shelteranimals = dbo.query(animal.get_animal_query(dbo) + " WHERE a.ID = ?", [animalid])

    async.set_progress_max(dbo, len(lostanimals))
    for la in lostanimals:
        async.increment_progress_value(dbo)
        # Stop if we've hit our limit
        if limit > 0 and len(matches) >= limit:
            break
        # Found animals (if an animal id has been given don't
        # check found animals)
        if animalid == 0:
            for fa in foundanimals:
                matchpoints = 0
                if la["ANIMALTYPEID"] == fa["ANIMALTYPEID"]: matchpoints += matchspecies
                if la["BREEDID"] == fa["BREEDID"]: matchpoints += matchbreed
                if la["AGEGROUP"] == fa["AGEGROUP"]: matchpoints += matchage
                if la["SEX"] == fa["SEX"]: matchpoints += matchsex
                matchpoints += words(la["AREALOST"], fa["AREAFOUND"], matcharealost)
                matchpoints += words(la["DISTFEAT"], fa["DISTFEAT"], matchfeatures)
                if la["AREAPOSTCODE"] == fa["AREAPOSTCODE"]: matchpoints += matchpostcode
                if la["BASECOLOURID"] == fa["BASECOLOURID"]: matchpoints += matchcolour
                if date_diff_days(la["DATELOST"], fa["DATEFOUND"]) <= 14: matchpoints += matchdatewithin2weeks
                if matchpoints > matchmax: matchpoints = matchmax
                if matchpoints >= matchpointfloor:
                    m = LostFoundMatch(dbo)
                    m.lid = la["ID"]
                    m.lcontactname = la["OWNERNAME"]
                    m.lcontactnumber = la["HOMETELEPHONE"]
                    m.larealost = la["AREALOST"]
                    m.lareapostcode = la["AREAPOSTCODE"]
                    m.lagegroup = la["AGEGROUP"]
                    m.lsexid = la["SEX"]
                    m.lsexname = la["SEXNAME"]
                    m.lspeciesid = la["ANIMALTYPEID"]
                    m.lspeciesname = la["SPECIESNAME"]
                    m.lbreedid = la["BREEDID"]
                    m.lbreedname = la["BREEDNAME"]
                    m.ldistinguishingfeatures = la["DISTFEAT"]
                    m.lbasecolourid = la["BASECOLOURID"]
                    m.lbasecolourname = la["BASECOLOURNAME"]
                    m.ldatelost = la["DATELOST"]
                    m.fid = fa["ID"]
                    m.fanimalid = 0
                    m.fcontactname = fa["OWNERNAME"]
                    m.fcontactnumber = fa["HOMETELEPHONE"]
                    m.fareafound = fa["AREAFOUND"]
                    m.fareapostcode = fa["AREAPOSTCODE"]
                    m.fagegroup = fa["AGEGROUP"]
                    m.fsexid = fa["SEX"]
                    m.fsexname = fa["SEXNAME"]
                    m.fspeciesid = fa["ANIMALTYPEID"]
                    m.fspeciesname = fa["SPECIESNAME"]
                    m.fbreedid = fa["BREEDID"]
                    m.fbreedname = fa["BREEDNAME"]
                    m.fdistinguishingfeatures = fa["DISTFEAT"]
                    m.fbasecolourid = fa["BASECOLOURID"]
                    m.fbasecolourname = fa["BASECOLOURNAME"]
                    m.fdatefound = fa["DATEFOUND"]
                    m.matchpoints = int((float(matchpoints) / float(matchmax)) * 100.0)
                    matches.append(m)
                    if fullmatch: 
                        batch.append(m.toParams())
                    if limit > 0 and len(matches) >= limit:
                        break

        # Shelter animals
        if includeshelter:
            for a in shelteranimals:
                matchpoints = 0
                if la["ANIMALTYPEID"] == a["SPECIESID"]: matchpoints += matchspecies
                if la["BREEDID"] == a["BREEDID"] or la["BREEDID"] == a["BREED2ID"]: matchpoints += matchbreed
                if la["BASECOLOURID"] == a["BASECOLOURID"]: matchpoints += matchcolour
                if la["AGEGROUP"] == a["AGEGROUP"]: matchpoints += matchage
                if la["SEX"] == a["SEX"]: matchpoints += matchsex
                matchpoints += words(la["AREALOST"], a["ORIGINALOWNERADDRESS"], matcharealost)
                matchpoints += words(la["DISTFEAT"], a["MARKINGS"], matchfeatures)
                if utils.nulltostr(a["ORIGINALOWNERPOSTCODE"]).find(la["AREAPOSTCODE"]) != -1: matchpoints += matchpostcode
                if date_diff_days(la["DATELOST"], a["DATEBROUGHTIN"]) <= 14: matchpoints += matchdatewithin2weeks
                if matchpoints > matchmax: matchpoints = matchmax
                if matchpoints >= matchpointfloor:
                    m = LostFoundMatch(dbo)
                    m.lid = la["ID"]
                    m.lcontactname = la["OWNERNAME"]
                    m.lcontactnumber = la["HOMETELEPHONE"]
                    m.larealost = la["AREALOST"]
                    m.lareapostcode = la["AREAPOSTCODE"]
                    m.lagegroup = la["AGEGROUP"]
                    m.lsexid = la["SEX"]
                    m.lsexname = la["SEXNAME"]
                    m.lspeciesid = la["ANIMALTYPEID"]
                    m.lspeciesname = la["SPECIESNAME"]
                    m.lbreedid = la["BREEDID"]
                    m.lbreedname = la["BREEDNAME"]
                    m.ldistinguishingfeatures = la["DISTFEAT"]
                    m.lbasecolourid = la["BASECOLOURID"]
                    m.lbasecolourname = la["BASECOLOURNAME"]
                    m.ldatelost = la["DATELOST"]
                    m.fid = 0
                    m.fanimalid = a["ID"]
                    m.fcontactname = _("Shelter animal {0} '{1}'", l).format(a["CODE"], a["ANIMALNAME"])
                    m.fcontactnumber = a["SPECIESNAME"]
                    m.fareafound = _("On Shelter", l)
                    m.fareapostcode = a["ORIGINALOWNERPOSTCODE"]
                    m.fagegroup = a["AGEGROUP"]
                    m.fsexid = a["SEX"]
                    m.fsexname = a["SEXNAME"]
                    m.fspeciesid = a["SPECIESID"]
                    m.fspeciesname = a["SPECIESNAME"]
                    m.fbreedid = a["BREEDID"]
                    m.fbreedname = a["BREEDNAME"]
                    m.fdistinguishingfeatures = a["MARKINGS"]
                    m.fbasecolourid = a["BASECOLOURID"]
                    m.fbasecolourname = a["BASECOLOURNAME"]
                    m.fdatefound = a["DATEBROUGHTIN"]
                    m.matchpoints = int((float(matchpoints) / float(matchmax)) * 100.0)
                    matches.append(m)
                    if fullmatch:
                        batch.append(m.toParams())
                    if limit > 0 and len(matches) >= limit:
                        break

    if fullmatch:
        dbo.execute("DELETE FROM animallostfoundmatch")
        sql = "INSERT INTO animallostfoundmatch (AnimalLostID, AnimalFoundID, AnimalID, LostContactName, LostContactNumber, " \
            "LostArea, LostPostcode, LostAgeGroup, LostSex, LostSpeciesID, LostBreedID, LostFeatures, LostBaseColourID, LostDate, " \
            "FoundContactName, FoundContactNumber, FoundArea, FoundPostcode, FoundAgeGroup, FoundSex, FoundSpeciesID, FoundBreedID, " \
            "FoundFeatures, FoundBaseColourID, FoundDate, MatchPoints) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        if len(batch) > 0:
            dbo.execute_many(sql, batch)

    return matches

def match_report(dbo, username = "system", lostanimalid = 0, foundanimalid = 0, animalid = 0, limit = 0):
    """
    Generates the match report and returns it as a string
    """
    l = dbo.locale
    title = _("Match lost and found animals", l)
    h = []
    h.append(reports.get_report_header(dbo, title, username))
    if limit > 0:
        h.append("<p>(" + _("Limited to {0} matches", l).format(limit) + ")</p>")
    def p(s): 
        return "<p>%s</p>" % s
    def td(s): 
        return "<td>%s</td>" % s
    def hr(): 
        return "<hr />"
    lastid = 0
    matches = match(dbo, lostanimalid, foundanimalid, animalid, limit)
    if len(matches) > 0:
        for m in matches:
            if lastid != m.lid:
                if lastid != 0:
                    h.append("</tr></table>")
                    h.append(hr())
                h.append(p(_("{0} - {1} {2} ({3}), contact {4} ({5}) - lost in {6}, postcode {7}, on {8}", l).format( \
                    m.lid, "%s %s %s" % (m.lagegroup, m.lbasecolourname, m.lsexname), \
                    "%s/%s" % (m.lspeciesname,m.lbreedname), \
                    m.ldistinguishingfeatures, m.lcontactname, m.lcontactnumber, m.larealost, m.lareapostcode,
                    python2display(l, m.ldatelost))))
                h.append("<table border=\"1\" width=\"100%\"><tr>")
                h.append("<th>%s</th>" % _("Reference", l))
                h.append("<th>%s</th>" % _("Description", l))
                h.append("<th>%s</th>" % _("Area Found", l))
                h.append("<th>%s</th>" % _("Area Postcode", l))
                h.append("<th>%s</th>" % _("Date Found", l))
                h.append("<th>%s</th>" % _("Contact", l))
                h.append("<th>%s</th>" % _("Number", l))
                h.append("<th>%s</th>" % _("Match", l))
                h.append("</tr>")
                lastid = m.lid
            h.append("<tr>")
            h.append(td(str(m.fid)))
            h.append(td("%s %s %s %s %s" % (m.fagegroup, m.fbasecolourname, m.fsexname, m.fspeciesname, m.fbreedname)))
            h.append(td(m.fareafound))
            h.append(td(m.fareapostcode))
            h.append(td(python2display(l, m.fdatefound)))
            h.append(td(m.fcontactname))
            h.append(td(m.fcontactnumber))
            h.append(td(str(m.matchpoints) + "%"))
            h.append("</tr>")
        h.append("</tr></table>")
    else:
        h.append(p(_("No matches found.", l)))
    h.append(reports.get_report_footer(dbo, title, username))
    return "\n".join(h)

def lostfound_last_match_count(dbo):
    """
    Returns the number of lost/found matches from the last run
    """
    return dbo.query_int("SELECT COUNT(*) FROM animallostfoundmatch")

def update_match_report(dbo):
    """
    Updates the latest version of the lost/found match report 
    """
    al.debug("updating lost/found match report", "lostfound.update_match_report", dbo)
    configuration.lostfound_report(dbo, match_report(dbo, limit = 1000))
    configuration.lostfound_last_match_count(dbo, lostfound_last_match_count(dbo))
    return "OK %d" % lostfound_last_match_count(dbo)

def get_lost_person_name(dbo, aid):
    """
    Returns the contact name for a lost animal
    """
    return dbo.query_string("SELECT o.OwnerName FROM animallost a INNER JOIN owner o ON a.OwnerID = o.ID WHERE a.ID = ?", [aid])

def get_found_person_name(dbo, aid):
    """
    Returns the contact name for a found animal
    """
    return dbo.query_string("SELECT o.OwnerName FROM animalfound a INNER JOIN owner o ON a.OwnerID = o.ID WHERE a.ID = ?", [aid])

def update_lostanimal_from_form(dbo, post, username):
    """
    Updates a lost animal record from the screen
    data: The webpy data object containing form parameters
    """
    l = dbo.locale
    lfid = post.integer("id")

    if not dbo.optimistic_check("animallost", post.integer("id"), post.integer("recordversion")):
        raise utils.ASMValidationError(_("This record has been changed by another user, please reload.", l))

    if post.date("datelost") is None:
        raise utils.ASMValidationError(_("Date lost cannot be blank", l))
    if post.date("datereported") is None:
        raise utils.ASMValidationError(_("Date reported cannot be blank", l))
    if post.integer("owner") == "0":
        raise utils.ASMValidationError(_("Lost animals must have a contact", l))

    dbo.update("animallost", lfid, {
        "AnimalTypeID":     post.integer("species"),
        "DateReported":     post.date("datereported"),
        "DateLost":         post.date("datelost"),
        "DateFound":        post.date("datefound"),
        "Sex":              post.integer("sex"),
        "BreedID":          post.integer("breed"),
        "AgeGroup":         post["agegroup"],
        "BaseColourID":     post.integer("colour"),
        "DistFeat":         post["markings"],
        "AreaLost":         post["arealost"],
        "AreaPostcode":     post["areapostcode"],
        "OwnerID":          post.integer("owner"),
        "Comments":         post["comments"]
    }, username)
    additional.save_values_for_link(dbo, post, lfid, "lostanimal")

def insert_lostanimal_from_form(dbo, post, username):
    """
    Inserts a new lost animal record from the screen
    data: The webpy data object containing form parameters
    """
    l = dbo.locale
    if post.date("datelost") is None:
        raise utils.ASMValidationError(_("Date lost cannot be blank", l))
    if post.date("datereported") is None:
        raise utils.ASMValidationError(_("Date reported cannot be blank", l))
    if post.integer("owner") == "0":
        raise utils.ASMValidationError(_("Lost animals must have a contact", l))

    nid = dbo.insert("animallost", {
        "AnimalTypeID":     post.integer("species"),
        "DateReported":     post.date("datereported"),
        "DateLost":         post.date("datelost"),
        "DateFound":        post.date("datefound"),
        "Sex":              post.integer("sex"),
        "BreedID":          post.integer("breed"),
        "AgeGroup":         post["agegroup"],
        "BaseColourID":     post.integer("colour"),
        "DistFeat":         post["markings"],
        "AreaLost":         post["arealost"],
        "AreaPostcode":     post["areapostcode"],
        "OwnerID":          post.integer("owner"),
        "Comments":         post["comments"]
    }, username)

    # Save any additional field values given
    additional.save_values_for_link(dbo, post, nid, "lostanimal")

    return nid

def update_foundanimal_from_form(dbo, post, username):
    """
    Updates a found animal record from the screen
    post: The webpy data object containing form parameters
    """
    l = dbo.locale
    lfid = post.integer("id")

    if not dbo.optimistic_check("animalfound", post.integer("id"), post.integer("recordversion")):
        raise utils.ASMValidationError(_("This record has been changed by another user, please reload.", l))

    if post.date("datefound") is None:
        raise utils.ASMValidationError(_("Date found cannot be blank", l))
    if post.date("datereported") is None:
        raise utils.ASMValidationError(_("Date reported cannot be blank", l))
    if post.integer("owner") == 0:
        raise utils.ASMValidationError(_("Found animals must have a contact", l))

    dbo.update("animalfound", lfid, {
        "AnimalTypeID":     post.integer("species"),
        "DateReported":     post.date("datereported"),
        "ReturnToOwnerDate": post.date("returntoownerdate"),
        "DateFound":        post.date("datefound"),
        "Sex":              post.integer("sex"),
        "BreedID":          post.integer("breed"),
        "AgeGroup":         post["agegroup"],
        "BaseColourID":     post.integer("colour"),
        "DistFeat":         post["markings"],
        "AreaFound":        post["areafound"],
        "AreaPostcode":     post["areapostcode"],
        "OwnerID":          post.integer("owner"),
        "Comments":         post["comments"]
    }, username)
    additional.save_values_for_link(dbo, post, lfid, "foundanimal")

def insert_foundanimal_from_form(dbo, post, username):
    """
    Inserts a new found animal record from the screen
    data: The webpy data object containing form parameters
    """
    l = dbo.locale
    if post.date("datefound") is None:
        raise utils.ASMValidationError(_("Date found cannot be blank", l))
    if post.date("datereported") is None:
        raise utils.ASMValidationError(_("Date reported cannot be blank", l))
    if post.integer("owner") == 0:
        raise utils.ASMValidationError(_("Found animals must have a contact", l))

    nid = dbo.insert("animalfound", {
        "AnimalTypeID":     post.integer("species"),
        "DateReported":     post.date("datereported"),
        "ReturnToOwnerDate": post.date("returntoownerdate"),
        "DateFound":        post.date("datefound"),
        "Sex":              post.integer("sex"),
        "BreedID":          post.integer("breed"),
        "AgeGroup":         post["agegroup"],
        "BaseColourID":     post.integer("colour"),
        "DistFeat":         post["markings"],
        "AreaFound":        post["areafound"],
        "AreaPostcode":     post["areapostcode"],
        "OwnerID":          post.integer("owner"),
        "Comments":         post["comments"]
    }, username)

    # Save any additional field values given
    additional.save_values_for_link(dbo, post, nid, "foundanimal")

    return nid

def create_animal_from_found(dbo, username, aid):
    """
    Creates an animal record from a found animal with the id given
    """
    a = dbo.first_row( dbo.query("SELECT * FROM animalfound WHERE ID = %d" % int(aid)) )
    l = dbo.locale
    data = {
        "animalname":           _("Found Animal {0}", l).format(aid),
        "markings":             str(a["DISTFEAT"]),
        "species":              str(a["ANIMALTYPEID"]),
        "comments":             str(a["COMMENTS"]),
        "broughtinby":          str(a["OWNERID"]),
        "originalowner":        str(a["OWNERID"]),
        "animaltype":           configuration.default_type(dbo),
        "breed1":               a["BREEDID"],
        "breed2":               a["BREEDID"],
        "basecolour":           str(a["BASECOLOURID"]),
        "size":                 configuration.default_size(dbo),
        "internallocation":     configuration.default_location(dbo),
        "dateofbirth":          python2display(l, subtract_years(now(dbo.timezone))),
        "estimateddob":         "1",
    }
    # If we're creating shelter codes manually, we need to put something unique
    # in there for now. Use the id
    if configuration.manual_codes(dbo):
        data["sheltercode"] = "FA" + str(aid)
        data["shortcode"] = "FA" + str(aid)
    nextid, code = animal.insert_animal_from_form(dbo, utils.PostedData(data, l), username)
    return nextid

def create_waitinglist_from_found(dbo, username, aid):
    """
    Creates a waiting list entry from a found animal with the id given
    """
    a = dbo.first_row( dbo.query("SELECT * FROM animalfound WHERE ID = %d" % int(aid)) )
    l = dbo.locale
    data = {
        "dateputon":            python2display(l, now(dbo.timezone)),
        "description":          str(a["DISTFEAT"]),
        "species":              str(a["ANIMALTYPEID"]),
        "comments":             str(a["COMMENTS"]),
        "owner":                str(a["OWNERID"]),
        "breed1":               a["BREEDID"],
        "breed2":               a["BREEDID"],
        "basecolour":           str(a["BASECOLOURID"]),
        "urgency":              str(configuration.waiting_list_default_urgency(dbo))
    }
    nextid = waitinglist.insert_waitinglist_from_form(dbo, utils.PostedData(data, dbo.locale), username)
    return nextid

def delete_lostanimal(dbo, username, aid):
    """
    Deletes a lost animal
    """
    dbo.delete("media", "LinkID=%d AND LinkTypeID=%d" % (aid, media.LOSTANIMAL), username)
    dbo.delete("diary", "LinkID=%d AND LinkType=%d" % (aid, diary.LOSTANIMAL), username)
    dbo.delete("log", "LinkID=%d AND LinkType=%d" % (aid, log.LOSTANIMAL), username)
    dbo.execute("DELETE FROM additional WHERE LinkID = %d AND LinkType IN (%s)" % (aid, additional.LOSTANIMAL_IN))
    dbo.delete("animallost", aid, username)
    dbfs.delete_path(dbo, "/lostanimal/%d" % aid)

def delete_foundanimal(dbo, username, aid):
    """
    Deletes a found animal
    """
    dbo.delete("media", "LinkID=%d AND LinkTypeID=%d" % (aid, media.FOUNDANIMAL), username)
    dbo.delete("diary", "LinkID=%d AND LinkType=%d" % (aid, diary.FOUNDANIMAL), username)
    dbo.delete("log", "LinkID=%d AND LinkType=%d" % (aid, log.FOUNDANIMAL), username)
    dbo.execute("DELETE FROM additional WHERE LinkID = %d AND LinkType IN (%s)" % (aid, additional.FOUNDANIMAL_IN))
    dbo.delete("animalfound", aid, username)
    dbfs.delete_path(dbo, "/foundanimal/%d" % aid)

