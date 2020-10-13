
import asm3.additional
import asm3.al
import asm3.animal
import asm3.asynctask
import asm3.cachedisk
import asm3.configuration
import asm3.dbfs
import asm3.diary
import asm3.log
import asm3.media
import asm3.reports
import asm3.utils
import asm3.waitinglist
from asm3.i18n import _, date_diff_days, now, subtract_years, python2display

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
    lmicrochip = ""
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
    fmicrochip = ""
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
                self.lsexid, self.lspeciesid, self.lbreedid, self.ldistinguishingfeatures, self.lbasecolourid, self.ldatelost, self.lmicrochip, self.fmicrochip,
                self.fcontactname, self.fcontactnumber, self.fareafound, self.fareapostcode, self.fagegroup, self.fsexid, self.fspeciesid, self.fbreedid,
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
        "LEFT OUTER JOIN owner o ON a.OwnerID = o.ID" % asm3.media.FOUNDANIMAL

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
        "LEFT OUTER JOIN owner o ON a.OwnerID = o.ID" % asm3.media.LOSTANIMAL

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

def get_lostanimal_find_simple(dbo, query = "", limit = 0, siteid = 0):
    """
    Returns rows for simple lost animal searches.
    query: The search criteria
    """
    ss = asm3.utils.SimpleSearchBuilder(dbo, query)

    sitefilter = ""
    if siteid != 0: sitefilter = " AND (o.SiteID = 0 OR o.SiteID = %d)" % siteid

    # If no query has been given, show unfound lost animal records
    # for the last 30 days
    if query == "":
        ss.ors.append("a.DateLost > ? AND a.DateFound Is Null %s" % sitefilter)
        ss.values.append(dbo.today(offset=-30))
    else:
        if asm3.utils.is_numeric(query): ss.add_field_value("a.ID", asm3.utils.cint(query))
        ss.add_fields([ "o.OwnerName", "a.AreaLost", "a.AreaPostcode", "a.MicrochipNumber" ])
        ss.add_clause("EXISTS(SELECT ad.Value FROM additional ad " \
            "INNER JOIN additionalfield af ON af.ID = ad.AdditionalFieldID AND af.Searchable = 1 " \
            "WHERE ad.LinkID=a.ID AND ad.LinkType IN (%s) AND LOWER(ad.Value) LIKE ?)" % asm3.additional.LOSTANIMAL_IN)
        ss.add_large_text_fields([ "b.BreedName", "a.DistFeat", "a.Comments" ])

    sql = "%s WHERE a.ID > 0 %s AND (%s)" % (get_lostanimal_query(dbo), sitefilter, " OR ".join(ss.ors))
    return dbo.query(sql, ss.values, limit=limit, distincton="ID")

def get_foundanimal_find_simple(dbo, query = "", limit = 0, siteid = 0):
    """
    Returns rows for simple found animal searches.
    query: The search criteria
    """
    ss = asm3.utils.SimpleSearchBuilder(dbo, query)

    sitefilter = ""
    if siteid != 0: sitefilter = " AND (o.SiteID = 0 OR o.SiteID = %d)" % siteid

    # If no query has been given, show unfound lost animal records
    # for the last 30 days
    if query == "":
        ss.ors.append("a.DateFound > ? AND a.ReturnToOwnerDate Is Null %s" % sitefilter)
        ss.values.append(dbo.today(offset=-30))
    else:
        if asm3.utils.is_numeric(query): ss.add_field_value("a.ID", asm3.utils.cint(query))
        ss.add_fields([ "o.OwnerName", "a.AreaFound", "a.AreaPostcode", "a.MicrochipNumber" ])
        ss.add_clause("EXISTS(SELECT ad.Value FROM additional ad " \
            "INNER JOIN additionalfield af ON af.ID = ad.AdditionalFieldID AND af.Searchable = 1 " \
            "WHERE ad.LinkID=a.ID AND ad.LinkType IN (%s) AND LOWER(ad.Value) LIKE ?)" % asm3.additional.FOUNDANIMAL_IN)
        ss.add_large_text_fields([ "b.BreedName", "a.DistFeat", "a.Comments" ])

    sql = "%s WHERE a.ID > 0 %s AND (%s)" % (get_foundanimal_query(dbo), sitefilter, " OR ".join(ss.ors))
    return dbo.query(sql, ss.values, limit=limit, distincton="ID")

def get_lostanimal_find_advanced(dbo, criteria, limit = 0, siteid = 0):
    """
    Returns rows for advanced lost animal searches.
    criteria: A dictionary of criteria
       number - string partial pattern
       contact - string partial pattern
       microchip - string partial pattern
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
    post = asm3.utils.PostedData(criteria, dbo.locale)
    ss = asm3.utils.AdvancedSearchBuilder(dbo, post)

    ss.ands.append("a.ID > 0")
    if siteid != 0: ss.ands.append("(o.SiteID = 0 OR o.SiteID = %d)" % siteid)
    ss.add_id("number", "a.ID")
    ss.add_str("contact", "o.OwnerName")
    ss.add_str("microchip", "a.MicrochipNumber")
    ss.add_str("area", "a.AreaLost")
    ss.add_str("postcode", "a.AreaPostcode")
    ss.add_str("features", "a.DistFeat")
    if post["agegroup"] != "-1": ss.add_str("agegroup", "a.AgeGroup")
    ss.add_id("sex", "a.Sex")
    ss.add_id("species", "a.AnimalTypeID")
    ss.add_id("breed", "a.BreedID")
    ss.add_id("colour", "a.BaseColourID")
    ss.add_date("datefrom", "dateto", "a.DateLost")
    ss.add_date("completefrom", "completeto", "a.DateFound")
    if post["excludecomplete"] == "1":
        ss.ands.append("a.DateFound Is Null")

    sql = "%s WHERE %s ORDER BY a.ID" % (get_lostanimal_query(dbo), " AND ".join(ss.ands))
    return dbo.query(sql, ss.values, limit=limit, distincton="ID")

def get_foundanimal_find_advanced(dbo, criteria, limit = 0, siteid = 0):
    """
    Returns rows for advanced lost animal searches.
    criteria: A dictionary of criteria
       number - string partial pattern
       contact - string partial pattern
       microchip - string partial pattern
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
    post = asm3.utils.PostedData(criteria, dbo.locale)
    ss = asm3.utils.AdvancedSearchBuilder(dbo, post)

    ss.ands.append("a.ID > 0")
    if siteid != 0: ss.ands.append("(o.SiteID = 0 OR o.SiteID = %d)" % siteid)
    ss.add_id("number", "a.ID")
    ss.add_str("contact", "o.OwnerName")
    ss.add_str("microchip", "a.MicrochipNumber")
    ss.add_str("area", "a.AreaFound")
    ss.add_str("postcode", "a.AreaPostcode")
    ss.add_str("features", "a.DistFeat")
    if post["agegroup"] != "-1": ss.add_str("agegroup", "a.AgeGroup")
    ss.add_id("sex", "a.Sex")
    ss.add_id("species", "a.AnimalTypeID")
    ss.add_id("breed", "a.BreedID")
    ss.add_id("colour", "a.BaseColourID")
    ss.add_date("datefrom", "dateto", "a.DateFound")
    ss.add_date("completefrom", "completeto", "a.ReturnToOwnerDate")
    if post["excludecomplete"] == "1":
        ss.ands.append("a.ReturnToOwnerDate Is Null")

    sql = "%s WHERE %s ORDER BY a.ID" % (get_foundanimal_query(dbo), " AND ".join(ss.ands))
    return dbo.query(sql, ss.values, limit=limit, distincton="ID")

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
        % (asm3.media.LOSTANIMAL, asm3.diary.LOSTANIMAL, asm3.log.LOSTANIMAL)
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
        % (asm3.media.FOUNDANIMAL, asm3.diary.FOUNDANIMAL, asm3.log.FOUNDANIMAL)
    return dbo.query(sql, [lfid])

def send_email_from_form(dbo, username, post):
    """
    Sends an email to a lost/found person from a posted form. Attaches it as
    a log entry if specified.
    """
    emailfrom = post["from"]
    emailto = post["to"]
    emailcc = post["cc"]
    emailbcc = post["bcc"]
    subject = post["subject"]
    ishtml = post.boolean("html")
    addtolog = post.boolean("addtolog")
    logtype = post.integer("logtype")
    body = post["body"]
    rv = asm3.utils.send_email(dbo, emailfrom, emailto, emailcc, emailbcc, subject, body, ishtml == 1 and "html" or "plain")
    if asm3.configuration.audit_on_send_email(dbo): 
        asm3.audit.email(dbo, username, emailfrom, emailto, emailcc, emailbcc, subject, body)
    if addtolog == 1:
        asm3.log.add_log_email(dbo, username, post["lfmode"] == "lost" and asm3.log.LOSTANIMAL or asm3.log.FOUNDANIMAL, post.integer("lfid"), logtype, emailto, subject, body)
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
    matchspecies = asm3.configuration.match_species(dbo)
    matchbreed = asm3.configuration.match_breed(dbo)
    matchage = asm3.configuration.match_age(dbo)
    matchsex = asm3.configuration.match_sex(dbo)
    matcharealost = asm3.configuration.match_area_lost(dbo)
    matchfeatures = asm3.configuration.match_features(dbo)
    matchpostcode = asm3.configuration.match_postcode(dbo)
    matchcolour = asm3.configuration.match_colour(dbo)
    matchmicrochip = asm3.configuration.match_microchip(dbo)
    matchdatewithin2weeks = asm3.configuration.match_within2weeks(dbo)
    matchmax = matchspecies + matchbreed + matchage + matchsex + \
        matcharealost + matchfeatures + matchpostcode + matchcolour + \
        matchmicrochip + matchdatewithin2weeks
    matchpointfloor = asm3.configuration.match_point_floor(dbo)
    includeshelter = asm3.configuration.match_include_shelter(dbo)
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
            shelteranimals = dbo.query(asm3.animal.get_animal_query(dbo) + " WHERE " + \
                "(a.Archived = 0 OR a.ActiveMovementType IN (3,4,7)) " \
                "AND a.DateBroughtIn > ?", [oldestdate])
        else:
            shelteranimals = dbo.query(asm3.animal.get_animal_query(dbo) + " WHERE a.ID = ?", [animalid])

    asm3.asynctask.set_progress_max(dbo, len(lostanimals))
    for la in lostanimals:
        asm3.asynctask.increment_progress_value(dbo)
        # Stop if we've hit our limit
        if limit > 0 and len(matches) >= limit:
            break
        # Found animals (if an animal id has been given don't
        # check found animals)
        if animalid == 0:
            for fa in foundanimals:
                matchpoints = 0
                if la["MICROCHIPNUMBER"] != "" and la["MICROCHIPNUMBER"] == fa["MICROCHIPNUMBER"]: matchpoints += matchmicrochip
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
                    m.lmicrochip = la["MICROCHIPNUMBER"]
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
                    m.fmicrochip = fa["MICROCHIPNUMBER"]
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
                foundarea = ""
                foundpostcode = ""
                if la["MICROCHIPNUMBER"] != "" and la["MICROCHIPNUMBER"] == a["IDENTICHIPNUMBER"]: matchpoints += matchmicrochip
                if la["ANIMALTYPEID"] == a["SPECIESID"]: matchpoints += matchspecies
                if la["BREEDID"] == a["BREEDID"] or la["BREEDID"] == a["BREED2ID"]: matchpoints += matchbreed
                if la["BASECOLOURID"] == a["BASECOLOURID"]: matchpoints += matchcolour
                if la["AGEGROUP"] == a["AGEGROUP"]: matchpoints += matchage
                if la["SEX"] == a["SEX"]: matchpoints += matchsex
                matchpoints += words(la["DISTFEAT"], a["MARKINGS"], matchfeatures)
                if a["ISPICKUP"] == 1:
                    matchpoints += words(la["AREALOST"], a["PICKUPADDRESS"], matcharealost)
                    foundarea = a["PICKUPADDRESS"]
                elif a["BROUGHTINBYOWNERADDRESS"] is not None:
                    matchpoints += words(la["AREALOST"], a["BROUGHTINBYOWNERADDRESS"], matcharealost)
                    if asm3.utils.nulltostr(a["BROUGHTINBYOWNERPOSTCODE"]).find(la["AREAPOSTCODE"]) != -1: matchpoints += matchpostcode
                    foundarea = a["BROUGHTINBYOWNERADDRESS"]
                    foundpostcode = a["BROUGHTINBYOWNERPOSTCODE"]
                elif a["ORIGINALOWNERADDRESS"] is not None:
                    matchpoints += words(la["AREALOST"], a["ORIGINALOWNERADDRESS"], matcharealost)
                    if asm3.utils.nulltostr(a["ORIGINALOWNERPOSTCODE"]).find(la["AREAPOSTCODE"]) != -1: matchpoints += matchpostcode
                    foundarea = a["ORIGINALOWNERADDRESS"]
                    foundpostcode = a["ORIGINALOWNERPOSTCODE"]
                if date_diff_days(la["DATELOST"], a["DATEBROUGHTIN"]) <= 14: matchpoints += matchdatewithin2weeks
                if matchpoints > matchmax: matchpoints = matchmax
                if matchpoints >= matchpointfloor:
                    m = LostFoundMatch(dbo)
                    m.lid = la["ID"]
                    m.lcontactname = la["OWNERNAME"]
                    m.lmicrochip = la["MICROCHIPNUMBER"]
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
                    m.fmicrochip = a["IDENTICHIPNUMBER"]
                    m.fcontactnumber = a["SPECIESNAME"]
                    m.fareafound = foundarea
                    m.fareapostcode = foundpostcode
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
            "LostMicrochipNumber, FoundMicrochipNumber, " \
            "FoundContactName, FoundContactNumber, FoundArea, FoundPostcode, FoundAgeGroup, FoundSex, FoundSpeciesID, FoundBreedID, " \
            "FoundFeatures, FoundBaseColourID, FoundDate, MatchPoints) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
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
    h.append(asm3.reports.get_report_header(dbo, title, username))
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
                    "%s/%s %s" % (m.lspeciesname, m.lbreedname, m.lmicrochip), \
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
                h.append("<th>%s</th>" % _("Microchip", l))
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
            h.append(td(m.fmicrochip))
            h.append(td(str(m.matchpoints) + "%"))
            h.append("</tr>")
        h.append("</tr></table>")
    else:
        h.append(p(_("No matches found.", l)))
    h.append(asm3.reports.get_report_footer(dbo, title, username))
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
    asm3.al.debug("updating lost/found match report", "lostfound.update_match_report", dbo)
    s = match_report(dbo, limit=1000)
    count = lostfound_last_match_count(dbo)
    asm3.cachedisk.put("lostfound_report", dbo.database, s, 86400)
    asm3.cachedisk.put("lostfound_lastmatchcount", dbo.database, count, 86400)
    return "OK %d" % count

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
        raise asm3.utils.ASMValidationError(_("This record has been changed by another user, please reload.", l))

    if post.date("datelost") is None:
        raise asm3.utils.ASMValidationError(_("Date lost cannot be blank", l))
    if post.date("datereported") is None:
        raise asm3.utils.ASMValidationError(_("Date reported cannot be blank", l))
    if post.integer("owner") == "0":
        raise asm3.utils.ASMValidationError(_("Lost animals must have a contact", l))

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
        "MicrochipNumber":  post["microchip"],
        "OwnerID":          post.integer("owner"),
        "Comments":         post["comments"]
    }, username)
    asm3.additional.save_values_for_link(dbo, post, lfid, "lostanimal")

def insert_lostanimal_from_form(dbo, post, username):
    """
    Inserts a new lost animal record from the screen
    data: The webpy data object containing form parameters
    """
    l = dbo.locale
    if post.date("datelost") is None:
        raise asm3.utils.ASMValidationError(_("Date lost cannot be blank", l))
    if post.date("datereported") is None:
        raise asm3.utils.ASMValidationError(_("Date reported cannot be blank", l))
    if post.integer("owner") == "0":
        raise asm3.utils.ASMValidationError(_("Lost animals must have a contact", l))

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
        "MicrochipNumber":  post["microchip"],
        "OwnerID":          post.integer("owner"),
        "Comments":         post["comments"]
    }, username)

    # Save any additional field values given
    asm3.additional.save_values_for_link(dbo, post, nid, "lostanimal", True)

    return nid

def update_foundanimal_from_form(dbo, post, username):
    """
    Updates a found animal record from the screen
    post: The webpy data object containing form parameters
    """
    l = dbo.locale
    lfid = post.integer("id")

    if not dbo.optimistic_check("animalfound", post.integer("id"), post.integer("recordversion")):
        raise asm3.utils.ASMValidationError(_("This record has been changed by another user, please reload.", l))

    if post.date("datefound") is None:
        raise asm3.utils.ASMValidationError(_("Date found cannot be blank", l))
    if post.date("datereported") is None:
        raise asm3.utils.ASMValidationError(_("Date reported cannot be blank", l))
    if post.integer("owner") == 0:
        raise asm3.utils.ASMValidationError(_("Found animals must have a contact", l))

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
        "MicrochipNumber":  post["microchip"],
        "OwnerID":          post.integer("owner"),
        "Comments":         post["comments"]
    }, username)
    asm3.additional.save_values_for_link(dbo, post, lfid, "foundanimal")

def insert_foundanimal_from_form(dbo, post, username):
    """
    Inserts a new found animal record from the screen
    data: The webpy data object containing form parameters
    """
    l = dbo.locale
    if post.date("datefound") is None:
        raise asm3.utils.ASMValidationError(_("Date found cannot be blank", l))
    if post.date("datereported") is None:
        raise asm3.utils.ASMValidationError(_("Date reported cannot be blank", l))
    if post.integer("owner") == 0:
        raise asm3.utils.ASMValidationError(_("Found animals must have a contact", l))

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
        "MicrochipNumber":  post["microchip"],
        "OwnerID":          post.integer("owner"),
        "Comments":         post["comments"]
    }, username)

    # Save any additional field values given
    asm3.additional.save_values_for_link(dbo, post, nid, "foundanimal", True)

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
        "animaltype":           asm3.configuration.default_type(dbo),
        "breed1":               a["BREEDID"],
        "breed2":               a["BREEDID"],
        "basecolour":           str(a["BASECOLOURID"]),
        "microchipped":         asm3.utils.iif(a["MICROCHIPNUMBER"] is not None and a["MICROCHIPNUMBER"] != "", "1", "0"),
        "microchipnumber":      a["MICROCHIPNUMBER"],
        "size":                 asm3.configuration.default_size(dbo),
        "internallocation":     asm3.configuration.default_location(dbo),
        "dateofbirth":          python2display(l, subtract_years(now(dbo.timezone))),
        "estimateddob":         "1",
    }
    # If we're creating shelter codes manually, we need to put something unique
    # in there for now. Use the id
    if asm3.configuration.manual_codes(dbo):
        data["sheltercode"] = "FA" + str(aid)
        data["shortcode"] = "FA" + str(aid)
    nextid, dummy = asm3.animal.insert_animal_from_form(dbo, asm3.utils.PostedData(data, l), username)
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
        "urgency":              str(asm3.configuration.waiting_list_default_urgency(dbo))
    }
    nextid = asm3.waitinglist.insert_waitinglist_from_form(dbo, asm3.utils.PostedData(data, dbo.locale), username)
    return nextid

def delete_lostanimal(dbo, username, aid):
    """
    Deletes a lost animal
    """
    dbo.delete("media", "LinkID=%d AND LinkTypeID=%d" % (aid, asm3.media.LOSTANIMAL), username)
    dbo.delete("diary", "LinkID=%d AND LinkType=%d" % (aid, asm3.diary.LOSTANIMAL), username)
    dbo.delete("log", "LinkID=%d AND LinkType=%d" % (aid, asm3.log.LOSTANIMAL), username)
    dbo.execute("DELETE FROM additional WHERE LinkID = %d AND LinkType IN (%s)" % (aid, asm3.additional.LOSTANIMAL_IN))
    dbo.delete("animallost", aid, username)
    # asm3.dbfs.delete_path(dbo, "/lostanimal/%d" % aid)  # Use maint_db_delete_orphaned_media to remove dbfs later if needed

def delete_foundanimal(dbo, username, aid):
    """
    Deletes a found animal
    """
    dbo.delete("media", "LinkID=%d AND LinkTypeID=%d" % (aid, asm3.media.FOUNDANIMAL), username)
    dbo.delete("diary", "LinkID=%d AND LinkType=%d" % (aid, asm3.diary.FOUNDANIMAL), username)
    dbo.delete("log", "LinkID=%d AND LinkType=%d" % (aid, asm3.log.FOUNDANIMAL), username)
    dbo.execute("DELETE FROM additional WHERE LinkID = %d AND LinkType IN (%s)" % (aid, asm3.additional.FOUNDANIMAL_IN))
    dbo.delete("animalfound", aid, username)
    # asm3.dbfs.delete_path(dbo, "/foundanimal/%d" % aid)  # Use maint_db_delete_orphaned_media to remove dbfs later if needed

