
import asm3.additional
import asm3.audit
import asm3.configuration
import asm3.dbfs
import asm3.diary
import asm3.geo
import asm3.log
import asm3.media
import asm3.users
import asm3.utils

from asm3.i18n import _, python2display, format_time_now
from asm3.typehints import Database, List, PostedData, ResultRow, Results, Session

from datetime import datetime

ASCENDING = 0
DESCENDING = 1

def get_animalcontrol_query(dbo: Database) -> str:
    return "SELECT ac.*, ac.ID AS ACID, s.SpeciesName, x.Sex AS SexName, " \
        "co.OwnerName AS CallerName, co.OwnerAddress AS CallerAddress, co.OwnerTown AS CallerTown, co.OwnerCounty AS CallerCounty, co.OwnerPostcode AS CallerPostcode," \
        "co.HomeTelephone AS CallerHomeTelephone, co.WorkTelephone AS CallerWorkTelephone, co.MobileTelephone AS CallerMobileTelephone, " \
        "o1.OwnerName AS OwnerName, o1.OwnerName AS OwnerName1, o2.OwnerName AS OwnerName2, o3.OwnerName AS OwnerName3, " \
        "o1.OwnerName AS SuspectName, o1.OwnerAddress AS SuspectAddress, o1.OwnerTown AS SuspectTown, o1.OwnerCounty AS SuspectCounty, o1.OwnerPostcode AS SuspectPostcode, " \
        "o1.HomeTelephone AS SuspectHomeTelephone, o1.WorkTelephone AS SuspectWorkTelephone, o1.MobileTelephone AS SuspectMobileTelephone, " \
        "vo.OwnerName AS VictimName, vo.OwnerAddress AS VictimAddress, vo.OwnerTown AS VictimTown, vo.OwnerCounty AS VictimCounty, vo.OwnerPostcode AS VictimPostcode," \
        "vo.HomeTelephone AS VictimHomeTelephone, vo.WorkTelephone AS VictimWorkTelephone, vo.MobileTelephone AS VictimMobileTelephone, " \
        "ti.IncidentName, ci.CompletedName, pl.LocationName, j.JurisdictionName, " \
        "web.ID AS WebsiteMediaID, " \
        "web.MediaName AS WebsiteMediaName, " \
        "web.Date AS WebsiteMediaDate, " \
        "web.MediaNotes AS WebsiteMediaNotes, " \
        "doc.ID AS DocMediaID, " \
        "doc.MediaName AS DocMediaName, " \
        "doc.Date AS DocMediaDate " \
        "FROM animalcontrol ac " \
        "LEFT OUTER JOIN species s ON s.ID = ac.SpeciesID " \
        "LEFT OUTER JOIN lksex x ON x.ID = ac.Sex " \
        "LEFT OUTER JOIN jurisdiction j ON j.ID = ac.JurisdictionID " \
        "LEFT OUTER JOIN owner co ON co.ID = ac.CallerID " \
        "LEFT OUTER JOIN owner o1 ON o1.ID = ac.OwnerID " \
        "LEFT OUTER JOIN owner o2 ON o2.ID = ac.Owner2ID " \
        "LEFT OUTER JOIN owner o3 ON o3.ID = ac.Owner3ID " \
        "LEFT OUTER JOIN owner vo ON vo.ID = ac.VictimID " \
        "LEFT OUTER JOIN media web ON web.LinkID = ac.ID AND web.LinkTypeID = %d AND web.WebsitePhoto = 1 " \
        "LEFT OUTER JOIN media doc ON doc.LinkID = ac.ID AND doc.LinkTypeID = %d AND doc.DocPhoto = 1 " \
        "LEFT OUTER JOIN pickuplocation pl ON pl.ID = ac.PickupLocationID " \
        "LEFT OUTER JOIN incidenttype ti ON ti.ID = ac.IncidentTypeID " \
        "LEFT OUTER JOIN incidentcompleted ci ON ci.ID = ac.IncidentCompletedID" % (asm3.media.ANIMALCONTROL, asm3.media.ANIMALCONTROL)

def get_animalcontrol_animals_query(dbo: Database) -> str:
    return "SELECT a.ID, aca.AnimalID, a.ShelterCode, a.ShortCode, a.IdentichipNumber, a.AgeGroup, a.AnimalName, " \
        "a.BreedName, a.Neutered, a.DateBroughtIn, a.DeceasedDate, a.HasActiveReserve, " \
        "a.HasTrialAdoption, a.IsHold, a.IsQuarantine, a.HoldUntilDate, a.CrueltyCase, a.NonShelterAnimal, " \
        "a.ActiveMovementType, a.Archived, a.IsNotAvailableForAdoption, " \
        "a.CombiTestResult, a.FLVResult, a.HeartwormTestResult, " \
        "s.SpeciesName, t.AnimalType AS AnimalTypeName, " \
        "c.BaseColour AS BaseColourName, sx.Sex AS SexName, sz.Size AS SizeName, ct.CoatType As CoatTypeName " \
        "FROM animalcontrolanimal aca " \
        "INNER JOIN animal a ON aca.AnimalID = a.ID " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "INNER JOIN animaltype t ON t.ID = a.AnimalTypeID " \
        "LEFT OUTER JOIN basecolour c ON c.ID = a.BaseColourID " \
        "LEFT OUTER JOIN lksex sx ON sx.ID = a.Sex " \
        "LEFT OUTER JOIN lksize sz ON sz.ID = a.Size " \
        "LEFT OUTER JOIN lkcoattype ct ON ct.ID = a.CoatType " \

def get_traploan_query(dbo: Database) -> str:
    return "SELECT ot.ID, ot.TrapTypeID, ot.LoanDate, tt.TrapTypeName, ot.TrapNumber, " \
        "ot.DepositAmount, ot.DepositReturnDate, ot.ReturnDueDate, ot.ReturnDate, " \
        "ot.OwnerID, ot.Comments, " \
        "ot.CreatedBy, ot.CreatedDate, ot.LastChangedBy, ot.LastChangedDate, " \
        "o.OwnerTitle, o.OwnerInitials, o.OwnerSurname, o.OwnerForenames, o.OwnerName " \
        "FROM ownertraploan ot " \
        "INNER JOIN traptype tt ON tt.ID = ot.TrapTypeID " \
        "INNER JOIN owner o ON o.ID = ot.OwnerID "

def get_animalcontrol(dbo: Database, acid: int) -> ResultRow:
    """
    Returns an animal control incident record
    """
    rows = dbo.query(get_animalcontrol_query(dbo) + " WHERE ac.ID = ?", [acid])
    if rows is None or len(rows) == 0:
        return None
    else:
        ac = rows[0]
        roles = dbo.query("SELECT acr.*, r.RoleName FROM animalcontrolrole acr INNER JOIN role r ON acr.RoleID = r.ID WHERE acr.AnimalControlID = ?", [acid])
        viewroleids = []
        viewrolenames = []
        editroleids = []
        editrolenames = []
        for r in roles:
            if r.canview == 1:
                viewroleids.append(str(r.roleid))
                viewrolenames.append(str(r.rolename))
            if r.canedit == 1:
                editroleids.append(str(r.roleid))
                editrolenames.append(str(r.rolename))
        ac["VIEWROLEIDS"] = "|".join(viewroleids)
        ac["VIEWROLES"] = "|".join(viewrolenames)
        ac["EDITROLEIDS"] = "|".join(editroleids)
        ac["EDITROLES"] = "|".join(editrolenames)
        return ac

def get_animalcontrol_numbertype(dbo: Database, acid: int) -> str:
    """ Return the number and type of an incident (used by diary notes) """
    ac = dbo.first_row(dbo.query("SELECT ac.ID, tt.IncidentName FROM animalcontrol ac INNER JOIN incidenttype tt ON " \
        "tt.ID = ac.IncidentTypeID WHERE ac.ID = ?", [acid]))
    if ac is None: return ""
    return f"{ac.ID:06} - {ac.INCIDENTNAME}"

def get_animalcontrol_animals(dbo: Database, acid: int) -> Results:
    """ Return the list of linked animals for an incident """
    return dbo.query(get_animalcontrol_animals_query(dbo) + " WHERE aca.AnimalControlID = ?", [acid])

def get_animalcontrol_for_animal(dbo: Database, aid: int) -> Results:
    """ Return the list of linked incidents for an animal """
    return dbo.query(get_animalcontrol_query(dbo) + " INNER JOIN animalcontrolanimal aca ON aca.AnimalControlID = ac.ID WHERE aca.AnimalID = ? ORDER BY IncidentDateTime DESC", [aid])

def get_followup_two_dates(dbo: Database, start: datetime, end: datetime) -> Results:
    """
    Returns incidents for followup between the two dates specified
    """
    return dbo.query(get_animalcontrol_query(dbo) + " WHERE " \
        "(ac.FollowupDateTime >= ? AND ac.FollowupDateTime <= ? AND NOT ac.FollowupComplete = 1) OR " \
        "(ac.FollowupDateTime2 >= ? AND ac.FollowupDateTime2 <= ? AND NOT ac.FollowupComplete2 = 1) OR " \
        "(ac.FollowupDateTime3 >= ? AND ac.FollowupDateTime3 <= ? AND NOT ac.FollowupComplete3 = 1)", (start, end, start, end, start, end))

def get_animalcontrol_find_simple(dbo: Database, query: str = "", username: str = "", limit: int = 0, siteid: int = 0) -> Results:
    """
    Returns rows for simple animal control searches.
    query: The search criteria
    """
    ss = asm3.utils.SimpleSearchBuilder(dbo, query)

    sitefilter = ""
    if siteid != 0: sitefilter = " AND (ac.SiteID = 0 OR ac.SiteID = %d)" % siteid

    # If no query has been given, show open animal control records
    # from the last 30 days
    if query == "":
        ss.ors.append("ac.IncidentDateTime > %s AND ac.CompletedDate Is Null %s" % (dbo.sql_date(dbo.today(offset=-30)), sitefilter))
    else:
        if asm3.utils.is_numeric(query): ss.add_field_value("ac.ID", asm3.utils.cint(query))
        ss.add_fields([ "ac.IncidentCode", "co.OwnerName", "ti.IncidentName", "ac.DispatchAddress", "ac.DispatchPostcode", 
            "o1.OwnerName", "o2.OwnerName", "o3.OwnerName", "vo.OwnerName" ])
        ss.add_clause(u"EXISTS(SELECT ad.Value FROM additional ad " \
            "INNER JOIN additionalfield af ON af.ID = ad.AdditionalFieldID AND af.Searchable = 1 " \
            "WHERE ad.LinkID=ac.ID AND ad.LinkType IN (%s) AND LOWER(ad.Value) LIKE ?)" % (asm3.additional.INCIDENT_IN))
        ss.add_large_text_fields([ "ac.CallNotes", "ac.AnimalDescription" ])

    sql = "%s WHERE ac.ID > 0 %s AND (%s) ORDER BY ac.ID" % ( get_animalcontrol_query(dbo), sitefilter, " OR ".join(ss.ors))
    return reduce_find_results(dbo, username, dbo.query(sql, ss.values, limit=limit, distincton="ID"))

def get_animalcontrol_find_advanced(dbo: Database, criteria: dict, username: str, limit: int = 0, siteid: int = 0) -> Results:
    """
    Returns rows for advanced animal control searches.
    criteria: A dictionary of criteria
       code - string partial pattern
       number - string partial pattern
       callername - string partial pattern
       victimname - string partial pattern
       callerphone - string partial pattern
       incidenttype - -1 for all or ID
       dispatchedaco - string partial pattern
       completedtype - -1 for all or ID
       citationtype - -1 for all or ID
       address - string partial pattern
       city - string partial pattern
       postcode - string partial pattern
       jurisdiction - -1 for all or ID
       pickuplocation - -1 for all or ID
       description - string partial pattern
       agegroup - agegroup text to match
       sex - -1 for all or ID
       species - -1 for all or ID
       filter - incomplete, undispatched, requirefollowup, completed
       incidentfrom - incident date from in current display locale format
       incidentto - incident date to in current display locale format
       dispatchfrom - dispatch date from in current display locale format
       dispatchto - dispatch date from in current display locale format
       respondedfrom - responded date from in current display locale format
       respondedto - responded date to in current display locale format
       followupfrom - follow up date from in current display locale format
       followupto - follow up date to in current display locale format
       completedfrom - completed date from in current display locale format
       completedto - completed date to in current display locale format

    """
    post = asm3.utils.PostedData(criteria, dbo.locale)
    ss = asm3.utils.AdvancedSearchBuilder(dbo, post)

    ss.ands.append("ac.ID > 0")
    if siteid != 0: ss.ands.append("(ac.SiteID = 0 OR ac.SiteID = %d)" % siteid)
    ss.add_id("number", "ac.ID")
    ss.add_str("code", "ac.IncidentCode")
    ss.add_str("callername", "co.OwnerName")
    ss.add_str("victimname", "vo.OwnerName")
    ss.add_str("callerphone", "co.HomeTelephone")
    ss.add_id("incidenttype", "ac.IncidentTypeID")
    ss.add_id("pickuplocation", "ac.PickupLocationID")
    ss.add_id("jurisdiction", "ac.JurisdictionID")
    if post["dispatchedaco"] != "-1": ss.add_str("dispatchedaco", "ac.DispatchedACO")
    ss.add_date("incidentfrom", "incidentto", "ac.IncidentDateTime")
    ss.add_date("dispatchfrom", "dispatchto", "ac.DispatchDateTime")
    ss.add_date("respondedfrom", "respondedto", "ac.RespondedDateTime")
    ss.add_date("followupfrom", "followupto", "ac.FollowupDateTime")
    ss.add_date("completedfrom", "completedto", "ac.CompletedDate")
    ss.add_id("completedtype", "ac.IncidentCompletedID")
    ss.add_id("citationtype", "ac.CitationTypeID")
    ss.add_str("address", "ac.DispatchAddress")
    ss.add_str("city", "ac.DispatchTown")
    ss.add_str("postcode", "ac.DispatchPostcode")
    ss.add_str("callnotes", "ac.CallNotes")
    ss.add_str("description", "ac.AnimalDescription")
    if post["agegroup"] != "-1": ss.add_str("agegroup", "ac.AgeGroup")
    ss.add_id("sex", "ac.Sex")
    ss.add_id("species", "ac.SpeciesID")
    ss.add_filter("incomplete", "ac.CompletedDate Is Null")
    ss.add_filter("completed", "ac.CompletedDate Is Not Null")
    ss.add_filter("undispatched", "ac.CompletedDate Is Null AND ac.CallDateTime Is Not Null AND ac.DispatchDateTime Is Null")
    ss.add_filter("requirefollowup", "(" \
        "(ac.FollowupDateTime Is Not Null AND ac.FollowupDateTime <= %(now)s AND NOT ac.FollowupComplete = 1) OR " \
        "(ac.FollowupDateTime2 Is Not Null AND ac.FollowupDateTime2 <= %(now)s AND NOT ac.FollowupComplete2 = 1) OR " \
        "(ac.FollowupDateTime3 Is Not Null AND ac.FollowupDateTime3 <= %(now)s AND NOT ac.FollowupComplete3 = 1) " \
        ")" % { "now": dbo.sql_date(dbo.now(settime="23:59:59")) } )
    for k, v in post.data.items():
        if k.startswith("af_") and v != "":
            afid = asm3.utils.atoi(k)
            ilike = dbo.sql_ilike("Value", "?")
            ss.ands.append(f"EXISTS (SELECT Value FROM additional WHERE LinkID=ac.ID AND AdditionalFieldID={afid} AND {ilike})")
            ss.values.append( "%%%s%%" % v.strip().lower() )

    sql = "%s WHERE %s ORDER BY ac.ID DESC" % (get_animalcontrol_query(dbo), " AND ".join(ss.ands))
    return reduce_find_results(dbo, username, dbo.query(sql, ss.values, limit=limit, distincton="ID"))

def reduce_find_results(dbo: Database, username: str, rows: Results) -> Results:
    """
    Given the results of a find operation, goes through the results and removes 
    any results which the user does not have permission to view.
    1. Because there are one or more view roles on the incident and the user doesn't have any
    2. Multi-site is on, there's a site on the incident that is not the users
    """
    # Do nothing if there are no results
    if len(rows) == 0: return rows
    u = dbo.query("SELECT * FROM users WHERE UserName = ?", [username])
    # Do nothing if we can't find the user
    if len(u) == 0: return rows
    # Do nothing if the user is a super user and has no site
    u = u[0]
    if u.superuser == 1 and u.siteid == 0: return rows
    roles = asm3.users.get_roles_ids_for_user(dbo, username)
    # Build an IN clause of result IDs
    rids = []
    for r in rows:
        rids.append(str(r.acid))
    viewroles = dbo.query("SELECT * FROM animalcontrolrole WHERE AnimalControlID IN (%s)" % dbo.sql_placeholders(rids), rids)
    # Remove rows where the user doesn't have that role
    results = []
    for r in rows:
        rok = False
        # Compare the site ID on the incident to our user - to exclude the record,
        # both user and incident must have a site ID and they must be different
        if r.siteid != 0 and u.siteid != 0 and r.siteid != u.siteid: continue
        # Get the list of required view roles for this incident
        incroles = [ x for x in viewroles if r.acid == x.animalcontrolid and x.canview == 1 ]
        # If there aren't any, it's fine to view the incident
        if len(incroles) == 0: 
            rok = True
        else:
            # If the user has any of the set view roles, we're good
            for v in incroles:
                if v.roleid in roles:
                    rok = True
        if rok:
            results.append(r)
    return results

def calc_incident_code(dbo: Database, acid: int, incidentdate: datetime) -> str:
    """
    Generates a new incident code to the format/scheme. 
    Form tokens include:
    YYYY - 4 digit incident year
    YY   - 2 digit incident year
    MM   - 2 digit incident month
    DD   - 2 digit incident day
    UUUUUUUUUU - 10 digit padded unique number
    UUUUUU - 6 digit padded unique number
    UUUU - 4 digit padded unique number
    XXX  - 3 digit padded next incident for the year
    XX   - unpadded next incident for the year
    OOO  - 3 digit padded next incident for the month
    OO   - unpadded next incident for the month
    """
    def substitute_tokens(fmt: str, year: int, month: int) -> str:
        """
        Produces a code by switching tokens in the code format fmt.
        The format is parsed to left to right, testing for tokens. Anything
        not recognised as a token is added. Anything preceded by a backslash is added.
        """
        code = []
        x = 0
        while x < len(fmt):
            # Add the next character if we encounter a backslash to effectively escape it
            if fmt[x:x+1] == "\\":
                x += 1
                code.append(fmt[x:x+1])
                x += 1
            elif fmt[x:x+4] == "YYYY": 
                code.append("%04d" % incidentdate.year)
                x += 4
            elif fmt[x:x+2] == "YY":   
                code.append("%02d" % (int(incidentdate.year) - 2000))
                x += 2
            elif fmt[x:x+2] == "MM":   
                code.append("%02d" % incidentdate.month)
                x += 2
            elif fmt[x:x+2] == "DD":   
                code.append("%02d" % incidentdate.day)
                x += 2
            elif fmt[x:x+10] == "UUUUUUUUUU": 
                code.append("%010d" % acid)
                x += 10
            elif fmt[x:x+6] == "UUUUUUUUUU": 
                code.append("%06d" % acid)
                x += 6
            elif fmt[x:x+4] == "UUUU": 
                code.append("%04d" % acid)
                x += 4
            elif fmt[x:x+3] == "XXX":  
                code.append("%03d" % year)
                x += 3
            elif fmt[x:x+2] == "XX":   
                code.append(str(year))
                x += 2
            elif fmt[x:x+3] == "OOO":  
                code.append("%03d" % month)
                x += 3
            elif fmt[x:x+2] == "OO":   
                code.append(str(month))
                x += 2
            else:
                code.append(fmt[x:x+1])
                x += 1
        return "".join(code)

    if incidentdate is None:
        incidentdate = dbo.today()

    codeformat = asm3.configuration.incident_coding_format(dbo)
    beginningofyear = datetime(incidentdate.year, 1, 1, 0, 0, 0)
    endofyear = datetime(incidentdate.year, 12, 31, 23, 59, 59)
    beginningofmonth = asm3.i18n.first_of_month(incidentdate)
    endofmonth = asm3.i18n.last_of_month(incidentdate)
    highestyear = 0
    highestmonth = 0

    # If our code uses X, calculate the highest code seen this year
    if codeformat.find("X") != -1:
        highestyear = dbo.query_int("SELECT COUNT(ID) FROM animalcontrol WHERE " \
            "IncidentDateTime >= ? AND " \
            "IncidentDateTime <= ?", (beginningofyear, endofyear))
        highestyear += 1

    # If our code uses O, calculate the highest code seen this month
    if codeformat.find("O") != -1:
        highestmonth = dbo.query_int("SELECT COUNT(ID) FROM animalcontrol WHERE " \
            "IncidentDateTime >= ? AND " \
            "IncidentDateTime <= ?", (beginningofmonth, endofmonth))
        highestmonth += 1

    unique = False
    code = ""
    while not unique:

        # Generate the codes
        code = substitute_tokens(codeformat, highestyear, highestmonth)

        # Verify the code is unique
        unique = 0 == dbo.query_int("SELECT COUNT(*) FROM animalcontrol WHERE IncidentCode LIKE ?", [code])

        # If it's not, increment and try again
        if not unique:
            if codeformat.find("X") != -1: highestyear += 1
            if codeformat.find("O") != -1: highestmonth += 1

    asm3.al.debug("incidentcode: code=%s, incidentdate %s" % (code, incidentdate), "animalcontrol.calc_incident_code", dbo)
    return code

def check_view_permission(dbo: Database, username: str, session: Session, acid: int) -> bool:
    """
    Checks that the currently logged in user has permission to
    view the incident with acid.
    If they can't, an ASMPermissionError is thrown.
    """
    # Superusers can do anything
    if session.superuser == 1: return True
    viewroles = []
    for rr in dbo.query("SELECT RoleID FROM animalcontrolrole WHERE AnimalControlID = ? AND CanView = 1", [acid]):
        viewroles.append(rr.ROLEID)
    # No view roles means anyone can view
    if len(viewroles) == 0:
        return True
    # Does the user have any of the view roles?
    userroles = []
    for ur in dbo.query("SELECT RoleID FROM userrole INNER JOIN users ON userrole.UserID = users.ID WHERE users.UserName LIKE ?", [username]):
        userroles.append(ur.ROLEID)
    hasperm = False
    for ur in userroles:
        if ur in viewroles:
            hasperm = True
    if hasperm:
        return True
    raise asm3.utils.ASMPermissionError("User does not have required role to view this incident")

def get_animalcontrol_satellite_counts(dbo: Database, acid: int) -> Results:
    """
    Returns a resultset containing the number of each type of satellite
    record that an animal control entry has.
    """
    return dbo.query("SELECT a.ID, " \
        "(SELECT COUNT(*) FROM ownercitation oc WHERE oc.AnimalControlID = a.ID) AS citation, " \
        "(SELECT COUNT(*) FROM media me WHERE me.LinkID = a.ID AND me.LinkTypeID = ?) AS media, " \
        "(SELECT COUNT(*) FROM diary di WHERE di.LinkID = a.ID AND di.LinkType = ?) AS diary, " \
        "(SELECT COUNT(*) FROM log WHERE log.LinkID = a.ID AND log.LinkType = ?) AS logs " \
        "FROM animalcontrol a WHERE a.ID = ?", (asm3.media.ANIMALCONTROL, asm3.diary.ANIMALCONTROL, asm3.log.ANIMALCONTROL, acid))

def get_active_traploans(dbo: Database) -> Results:
    """
    Returns all active traploan records
    ID, TRAPTYPEID, TRAPTYPENAME, LOANDATE, DEPOSITRETURNDATE,
    TRAPNUMBER, RETURNDUEDATE, RETURNDATE,
    OWNERNAME
    """
    return dbo.query(get_traploan_query(dbo) + \
        "WHERE ot.ReturnDate Is Null OR ot.ReturnDate > ? " \
        "ORDER BY ot.LoanDate DESC", [dbo.today()])

def get_returned_traploans(dbo: Database, offset: str = "m31") -> Results:
    """
    Returns returned traploan records
    ID, TRAPTYPEID, TRAPTYPENAME, LOANDATE, DEPOSITRETURNDATE,
    TRAPNUMBER, RETURNDUEDATE, RETURNDATE,
    OWNERNAME
    """
    offsetdays = asm3.utils.atoi(offset)
    return dbo.query(get_traploan_query(dbo) + \
        "WHERE ot.ReturnDate >= ? " \
        "AND ot.ReturnDate <= ? " \
        "ORDER BY ot.LoanDate DESC", [ dbo.today(offset=offsetdays*-1), dbo.today() ])

def get_person_traploans(dbo: Database, oid: int, sort: int = ASCENDING) -> Results:
    """
    Returns all of the traploan records for a person, along with
    some owner info.
    ID, TRAPTYPEID, TRAPTYPENAME, LOANDATE, DEPOSITRETURNDATE,
    TRAPNUMBER, RETURNDUEDATE, RETURNDATE,
    OWNERNAME
    """
    order = "ot.LoanDate DESC"
    if sort == ASCENDING:
        order = "ot.LoanDate"
    return dbo.query(get_traploan_query(dbo) + \
        "WHERE ot.OwnerID = ? " \
        "ORDER BY %s" % order, [oid])

def get_traploan_two_dates(dbo: Database, start: datetime, end: datetime) -> Results:
    """
    Returns unreturned trap loans with a due date between the two dates
    """
    return dbo.query(get_traploan_query(dbo) + \
        "WHERE ReturnDate Is Null AND ReturnDueDate >= ? AND ReturnDueDate <= ?", (start, end))

def send_email_from_form(dbo: Database, username: str, post: PostedData) -> bool:
    """
    Sends an email to a person from a posted form. Attaches it as
    a log entry if specified.
    Passes the return value from send_email (a bool for success)
    """
    emailfrom = post["from"]
    emailto = post["to"]
    emailcc = post["cc"]
    emailbcc = post["bcc"]
    subject = post["subject"]
    addtolog = post.boolean("addtolog")
    logtype = post.integer("logtype")
    body = post["body"]
    rv = asm3.utils.send_email(dbo, emailfrom, emailto, emailcc, emailbcc, subject, body, "html")
    if asm3.configuration.audit_on_send_email(dbo): 
        asm3.audit.email(dbo, username, emailfrom, emailto, emailcc, emailbcc, subject, body)
    if addtolog == 1:
        asm3.log.add_log_email(dbo, username, asm3.log.ANIMALCONTROL, post.integer("incidentid"), logtype, emailto, subject, body)
    return rv

def update_dispatch_geocode(dbo: Database, incidentid: int, latlon: str = "", address: str = "", town: str = "", county: str = "", postcode: str = "", country: str = "") -> str:
    """
    Looks up the geocode for this incident with the address info given.
    If latlon is already set to a value, checks the address hash to see if it
    matches and does not do the geocode if it does.
    """
    # If an address hasn't been specified, look it up from the incidentid given
    if address == "":
        row = dbo.first_row(dbo.query("SELECT DispatchAddress, DispatchTown, DispatchCounty, DispatchPostcode FROM animalcontrol WHERE ID=?", [incidentid]))
        address = row.DISPATCHADDRESS
        town = row.DISPATCHTOWN
        county = row.DISPATCHCOUNTY
        postcode = row.DISPATCHPOSTCODE
    # If we're allowing manual entry of latlon values and we have a non-empty
    # value, do nothing so that changes to address don't overwrite it
    # If someone has deleted the values, a latlon of ,,HASH is returned so
    # we allow the geocode to be regenerated in that case.
    if asm3.configuration.show_lat_long(dbo) and latlon is not None and latlon != "" and not latlon.startswith(",,"):
        return latlon
    # If a latlon has been passed and it contains a hash of the address elements,
    # then the address hasn't changed since the last geocode was done - do nothing
    if latlon is not None and latlon != "":
        if latlon.find(asm3.geo.address_hash(address, town, county, postcode, country)) != -1:
            return latlon
    # Do the geocode
    latlon = asm3.geo.get_lat_long(dbo, address, town, county, postcode)
    update_dispatch_latlong(dbo, incidentid, latlon)
    return latlon

def update_dispatch_latlong(dbo: Database, incidentid: int, latlong: str) -> None:
    """
    Updates the latlong field on an incident.
    """
    dbo.update("animalcontrol", incidentid, { "DispatchLatLong": latlong })

def update_animalcontrol_completenow(dbo: Database, acid: int, username: str, completetype: int) -> None:
    """
    Updates an animal control incident record, marking it completed now with the type specified
    """
    dbo.update("animalcontrol", acid, {
        "IncidentCompletedID":  completetype,
        "CompletedDate":         dbo.now(),
    }, username)

def update_animalcontrol_dispatchnow(dbo: Database, acid: int, username: str) -> None:
    """
    Updates an animal control incident record, marking it dispatched
    now with the current user as ACO.
    """
    dbo.update("animalcontrol", acid, {
        "DispatchedACO":        username,
        "DispatchDateTime":     dbo.now()
    }, username)

def update_animalcontrol_respondnow(dbo: Database, acid: int, username: str) -> None:
    """
    Updates an animal control incident record, marking it responded to now
    """
    dbo.update("animalcontrol", acid, {
        "RespondedDateTime":    dbo.now()
    }, username)

def update_animalcontrol_from_form(dbo: Database, post: PostedData, username: str, geocode: bool = True) -> None:
    """
    Updates an animal control incident record from the screen
    data: The webpy data object containing form parameters
    """
    l = dbo.locale
    acid = post.integer("id")

    if not dbo.optimistic_check("animalcontrol", post.integer("id"), post.integer("recordversion")):
        raise asm3.utils.ASMValidationError(_("This record has been changed by another user, please reload.", l))

    if post.date("incidentdate") is None:
        raise asm3.utils.ASMValidationError(_("Incident date cannot be blank", l))

    dbo.update("animalcontrol", acid, {
        "IncidentCode":         post["incidentcode"],
        "IncidentDateTime":     post.datetime("incidentdate", "incidenttime"),
        "IncidentTypeID":       post.integer("incidenttype"),
        "CallDateTime":         post.datetime("calldate", "calltime"),
        "CallNotes":            post["callnotes"],
        "CallTaker":            post["calltaker"],
        "CallerID":             post.integer("caller"),
        "VictimID":             post.integer("victim"),
        "DispatchAddress":      post["dispatchaddress"],
        "DispatchTown":         post["dispatchtown"],
        "DispatchCounty":       post["dispatchcounty"],
        "DispatchPostcode":     post["dispatchpostcode"],
        "JurisdictionID":       post.integer("jurisdiction"),
        "PickupLocationID":     post.integer("pickuplocation"),
        "DispatchLatLong":      post["dispatchlatlong"],
        "DispatchedACO":        post["dispatchedaco"],
        "DispatchDateTime":     post.datetime("dispatchdate", "dispatchtime"),
        "RespondedDateTime":    post.datetime("respondeddate", "respondedtime"),
        "FollowupDateTime":     post.datetime("followupdate", "followuptime"),
        "FollowupComplete":     post.boolean("followupcomplete"),
        "FollowupDateTime2":    post.datetime("followupdate2", "followuptime2"),
        "FollowupComplete2":    post.boolean("followupcomplete2"),
        "FollowupDateTime3":    post.datetime("followupdate3", "followuptime3"),
        "FollowupComplete3":    post.boolean("followupcomplete3"),
        "CompletedDate":        post.datetime("completeddate", "completedtime"),
        "IncidentCompletedID":  post.integer("completedtype"),
        "SiteID":               post.integer("site"),
        "OwnerID":              post.integer("owner"),
        "Owner2ID":             post.integer("owner2"),
        "Owner3ID":             post.integer("owner3"),
        "AnimalDescription":    post["animaldescription"],
        "SpeciesID":            post.integer("species"),
        "Sex":                  post.integer("sex"),
        "AgeGroup":             post["agegroup"]
    }, username)

    asm3.additional.save_values_for_link(dbo, post, username, acid, "incident")
    asm3.diary.update_link_info(dbo, username, asm3.diary.ANIMALCONTROL, acid)
    update_animalcontrol_roles(dbo, acid, post.integer_list("viewroles"), post.integer_list("editroles"))

    # Check/update the geocode for the dispatch address
    if geocode: update_dispatch_geocode(dbo, acid, post["dispatchlatlong"], post["dispatchaddress"], post["dispatchtown"], post["dispatchcounty"], post["dispatchpostcode"])

def update_animalcontrol_roles(dbo: Database, acid: int, viewroles: List[int], editroles: List[int]) -> None:
    """
    Updates the view and edit roles for an incident
    acid:       The incident ID
    viewroles:  a list of integer role ids
    editroles:  a list of integer role ids
    """
    dbo.execute("DELETE FROM animalcontrolrole WHERE AnimalControlID = ?", [acid])
    for rid in viewroles:
        dbo.insert("animalcontrolrole", {
            "AnimalControlID":  acid,
            "RoleID":           rid,
            "CanView":          1,
            "CanEdit":          0
        }, generateID=False)
    for rid in editroles:
        if rid in viewroles:
            dbo.execute("UPDATE animalcontrolrole SET CanEdit = 1 WHERE AnimalControlID = ? AND RoleID = ?", (acid, rid))
        else:
            dbo.insert("animalcontrolrole", {
                "AnimalControlID":  acid,
                "RoleID":           rid,
                "CanView":          0,
                "CanEdit":          1
            }, generateID=False)

def update_animalcontrol_addlink(dbo: Database, username: str, acid: int, animalid: int) -> None:
    """
    Adds a link between an animal and an incident.
    """
    l = dbo.locale
    if 0 != dbo.query_int("SELECT COUNT(*) FROM animalcontrolanimal WHERE AnimalControlID = ? AND AnimalID = ?", (acid, animalid)):
        raise asm3.utils.ASMValidationError(_("That animal is already linked to the incident", l))
    dbo.execute("INSERT INTO animalcontrolanimal (AnimalControlID, AnimalID) VALUES (?, ?)", (acid, animalid))
    asm3.audit.create(dbo, username, "animalcontrolanimal", acid, "", "incident %d linked to animal %d" % (acid, animalid))

def update_animalcontrol_removelink(dbo: Database, username: str, acid: int, animalid: int) -> None:
    """
    Removes a link between an animal and an incident.
    """
    dbo.execute("DELETE FROM animalcontrolanimal WHERE AnimalControlID = ? AND AnimalID = ?", (acid, animalid))
    asm3.audit.delete(dbo, username, "animalcontrolanimal", acid, "", "incident %d no longer linked to animal %d" % (acid, animalid))

def insert_animalcontrol_from_form(dbo: Database, post: PostedData, username: str, geocode: bool = True) -> int:
    """
    Inserts a new animal control incident record from the screen
    data: The webpy data object containing form parameters
    """
    l = dbo.locale
    if post.date("incidentdate") is None:
        raise asm3.utils.ASMValidationError(_("Incident date cannot be blank", l))

    nid = dbo.get_id("animalcontrol")
    dbo.insert("animalcontrol", {
        "ID":                   nid,
        "IncidentCode":         calc_incident_code(dbo, nid, post.datetime("incidentdate", "incidenttime")),
        "IncidentDateTime":     post.datetime("incidentdate", "incidenttime"),
        "IncidentTypeID":       post.integer("incidenttype"),
        "CallDateTime":         post.datetime("calldate", "calltime"),
        "CallNotes":            post["callnotes"],
        "CallTaker":            post["calltaker"],
        "CallerID":             post.integer("caller"),
        "VictimID":             post.integer("victim"),
        "DispatchAddress":      post["dispatchaddress"],
        "DispatchedACO":        post["dispatchedaco"],
        "DispatchDateTime":     post["dispatchdate"],
        "DispatchTown":         post["dispatchtown"],
        "DispatchCounty":       post["dispatchcounty"],
        "DispatchPostcode":     post["dispatchpostcode"],
        "JurisdictionID":       post.integer("jurisdiction"),
        "PickupLocationID":     post.integer("pickuplocation"),
        "DispatchLatLong":      post["dispatchlatlong"],
        "DispatchedACO":        post["dispatchedaco"],
        "DispatchDateTime":     post.datetime("dispatchdate", "dispatchtime"),
        "RespondedDateTime":    post.datetime("respondeddate", "respondedtime"),
        "FollowupDateTime":     post.datetime("followupdate", "followuptime"),
        "FollowupComplete":     post.boolean("followupcomplete"),
        "FollowupDateTime2":    post.datetime("followupdate2", "followuptime2"),
        "FollowupComplete2":    post.boolean("followupcomplete2"),
        "FollowupDateTime3":    post.datetime("followupdate3", "followuptime3"),
        "FollowupComplete3":    post.boolean("followupcomplete3"),
        "CompletedDate":        post.datetime("completeddate", "completedtime"),
        "IncidentCompletedID":  post.integer("completedtype"),
        "SiteID":               post.integer("site"),
        "OwnerID":              post.integer("owner"),
        "Owner2ID":             post.integer("owner2"),
        "Owner3ID":             post.integer("owner3"),
        "AnimalDescription":    post["animaldescription"],
        "SpeciesID":            post.integer("species"),
        "Sex":                  post.integer("sex"),
        "AgeGroup":             post["agegroup"]
    }, username, generateID=False)

    asm3.additional.save_values_for_link(dbo, post, username, nid, "incident", True)
    update_animalcontrol_roles(dbo, nid, post.integer_list("viewroles"), post.integer_list("editroles"))

    # Look up a geocode for the dispatch address
    if geocode: update_dispatch_geocode(dbo, nid, "", post["dispatchaddress"], post["dispatchtown"], post["dispatchcounty"], post["dispatchpostcode"])

    return nid

def delete_animalcontrol(dbo: Database, username: str, acid: int) -> None:
    """
    Deletes an animal control record
    """
    dbo.delete("media", "LinkID=%d AND LinkTypeID=%d" % (acid, asm3.media.ANIMALCONTROL), username)
    dbo.delete("diary", "LinkID=%d AND LinkType=%d" % (acid, asm3.diary.ANIMALCONTROL), username)
    dbo.delete("log", "LinkID=%d AND LinkType=%d" % (acid, asm3.log.ANIMALCONTROL), username)
    dbo.execute("DELETE FROM additional WHERE LinkID = %d AND LinkType IN (%s)" % (acid, asm3.additional.INCIDENT_IN))
    dbo.delete("animalcontrol", acid, username)
    # asm3.dbfs.delete_path(dbo, "/animalcontrol/%d" % acid) # Use maint_db_delete_orphaned_media to remove dbfs later if needed

def insert_animalcontrol(dbo: Database, username: str) -> int:
    """
    Creates a new animal control incident record and returns the id
    """
    l = dbo.locale
    d = {
        "incidentdate":     python2display(l, dbo.now()),
        "incidenttime":     format_time_now(dbo.timezone),
        "incidenttype":     asm3.configuration.default_incident(dbo),
        "calldate":         python2display(l, dbo.now()),
        "calltime":         format_time_now(dbo.timezone),
        "calltaker":        username
    }
    return insert_animalcontrol_from_form(dbo, asm3.utils.PostedData(d, dbo.locale), username)

def clone_animalcontrol(dbo: Database, username: str, acid: int) -> int:
    """
    Clones animal control record acid. Returns the ID of the new record.
    """
    ac = get_animalcontrol(dbo, acid)
    nid = dbo.get_id("animalcontrol")
    dbo.insert("animalcontrol", {
        "ID":                   nid,
        "IncidentCode":         calc_incident_code(dbo, nid, ac.INCIDENTDATETIME),
        "IncidentDateTime":     ac.INCIDENTDATETIME,
        "IncidentTypeID":       ac.INCIDENTTYPEID,
        "CallDateTime":         ac.CALLDATETIME,
        "CallNotes":            ac.CALLNOTES,
        "CallTaker":            ac.CALLTAKER,
        "CallerID":             ac.CALLERID,
        "VictimID":             ac.VICTIMID,
        "DispatchAddress":      ac.DISPATCHADDRESS,
        "DispatchTown":         ac.DISPATCHTOWN,
        "DispatchCounty":       ac.DISPATCHCOUNTY,
        "DispatchPostcode":     ac.DISPATCHPOSTCODE,
        "JurisdictionID":       ac.JURISDICTIONID,
        "PickupLocationID":     ac.PICKUPLOCATIONID,
        "DispatchLatLong":      ac.DISPATCHLATLONG,
        "DispatchedACO":        ac.DISPATCHEDACO,
        "DispatchDateTime":     ac.DISPATCHDATETIME,
        "RespondedDateTime":    ac.RESPONDEDDATETIME,
        "FollowupDateTime":     ac.FOLLOWUPDATETIME,
        "FollowupComplete":     ac.FOLLOWUPCOMPLETE,
        "FollowupDateTime2":    ac.FOLLOWUPDATETIME2,
        "FollowupComplete2":    ac.FOLLOWUPCOMPLETE2,
        "FollowupDateTime3":    ac.FOLLOWUPDATETIME3,
        "FollowupComplete3":    ac.FOLLOWUPCOMPLETE3,
        "CompletedDate":        ac.COMPLETEDDATE,
        "IncidentCompletedID":  ac.INCIDENTCOMPLETEDID,
        "SiteID":               ac.SITEID,
        "OwnerID":              ac.OWNERID,
        "Owner2ID":             ac.OWNER2ID,
        "Owner3ID":             ac.OWNER3ID,
        "AnimalDescription":    ac.ANIMALDESCRIPTION,
        "SpeciesID":            ac.SPECIESID,
        "Sex":                  ac.SEX,
        "AgeGroup":             ac.AGEGROUP
    }, username, generateID=False)

    # Additional Fields
    for af in dbo.query("SELECT * FROM additional WHERE LinkID = %d AND LinkType IN (%s)" % (acid, asm3.additional.INCIDENT_IN)):
        asm3.additional.insert_additional(dbo, af.linktype, nid, af.additionalfieldid, af.value)

    # TODO: roles?
    return nid

def insert_traploan_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Creates a traploan record from posted form data 
    """
    return dbo.insert("ownertraploan", {
        "OwnerID":          post.integer("person"),
        "TrapTypeID":       post.integer("type"),
        "LoanDate":         post.date("loandate"),
        "DepositAmount":    post.integer("depositamount"),
        "DepositReturnDate": post.date("depositreturndate"),
        "TrapNumber":       post["trapnumber"],
        "ReturnDueDate":    post.date("returnduedate"),
        "ReturnDate":       post.date("returndate"),
        "Comments":         post["comments"]
    }, username)

def update_traploan_from_form(dbo: Database, username: str, post: PostedData) -> None:
    """
    Updates a traploan record from posted form data
    """
    dbo.update("ownertraploan", post.integer("traploanid"), {
        "OwnerID":          post.integer("person"),
        "TrapTypeID":       post.integer("type"),
        "LoanDate":         post.date("loandate"),
        "DepositAmount":    post.integer("depositamount"),
        "DepositReturnDate": post.date("depositreturndate"),
        "TrapNumber":       post["trapnumber"],
        "ReturnDueDate":    post.date("returnduedate"),
        "ReturnDate":       post.date("returndate"),
        "Comments":         post["comments"]
    }, username)

def delete_traploan(dbo: Database, username: str, tid: int) -> None:
    """
    Deletes a traploan record
    """
    dbo.delete("ownertraploan", tid, username)


