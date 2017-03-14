#!/usr/bin/python

import additional
import audit
import configuration
import db
import diary
import log
import media
import users
import utils
from i18n import _, now, subtract_days, python2display, format_time_now

ASCENDING = 0
DESCENDING = 1

def get_animalcontrol_query(dbo):
    return "SELECT ac.*, ac.ID AS ACID, s.SpeciesName, x.Sex AS SexName, " \
        "co.OwnerName AS CallerName, co.OwnerAddress AS CallerAddress, co.OwnerTown AS CallerTown, co.OwnerCounty AS CallerCounty, co.OwnerPostcode AS CallerPostcode," \
        "co.HomeTelephone AS CallerHomeTelephone, co.WorkTelephone AS CallerWorkTelephone, co.MobileTelephone AS CallerMobileTelephone, " \
        "o1.OwnerName AS OwnerName, o1.OwnerName AS OwnerName1, o2.OwnerName AS OwnerName2, o3.OwnerName AS OwnerName3, " \
        "o1.OwnerName AS SuspectName, o1.OwnerAddress AS SuspectAddress, o1.OwnerTown AS SuspectTown, o1.OwnerCounty AS SuspectCounty, o1.OwnerPostcode AS SuspectPostcode, " \
        "o1.HomeTelephone AS SuspectHomeTelephone, o1.WorkTelephone AS SuspectWorkTelephone, o1.MobileTelephone AS SuspectMobileTelephone, " \
        "vo.OwnerName AS VictimName, vo.OwnerAddress AS VictimAddress, vo.OwnerTown AS VictimTown, vo.OwnerCounty AS VictimCounty, vo.OwnerPostcode AS VictimPostcode," \
        "vo.HomeTelephone AS VictimHomeTelephone, vo.WorkTelephone AS VictimWorkTelephone, vo.MobileTelephone AS VictimMobileTelephone, " \
        "ti.IncidentName, ci.CompletedName, pl.LocationName " \
        "FROM animalcontrol ac " \
        "LEFT OUTER JOIN species s ON s.ID = ac.SpeciesID " \
        "LEFT OUTER JOIN lksex x ON x.ID = ac.Sex " \
        "LEFT OUTER JOIN owner co ON co.ID = ac.CallerID " \
        "LEFT OUTER JOIN owner o1 ON o1.ID = ac.OwnerID " \
        "LEFT OUTER JOIN owner o2 ON o2.ID = ac.Owner2ID " \
        "LEFT OUTER JOIN owner o3 ON o3.ID = ac.Owner3ID " \
        "LEFT OUTER JOIN owner vo ON vo.ID = ac.VictimID " \
        "LEFT OUTER JOIN pickuplocation pl ON pl.ID = ac.PickupLocationID " \
        "LEFT OUTER JOIN incidenttype ti ON ti.ID = ac.IncidentTypeID " \
        "LEFT OUTER JOIN incidentcompleted ci ON ci.ID = ac.IncidentCompletedID"

def get_animalcontrol_animals_query(dbo):
    return "SELECT a.ID, aca.AnimalID, a.ShelterCode, a.ShortCode, a.AgeGroup, a.AnimalName, " \
        "a.Neutered, a.DateBroughtIn, a.DeceasedDate, a.HasActiveReserve, " \
        "a.HasTrialAdoption, a.IsHold, a.IsQuarantine, a.HoldUntilDate, a.CrueltyCase, a.NonShelterAnimal, " \
        "a.ActiveMovementType, a.Archived, a.IsNotAvailableForAdoption, " \
        "a.CombiTestResult, a.FLVResult, a.HeartwormTestResult, " \
        "s.SpeciesName, t.AnimalType AS AnimalTypeName " \
        "FROM animalcontrolanimal aca " \
        "INNER JOIN animal a ON aca.AnimalID = a.ID " \
        "INNER JOIN species s ON s.ID = a.SpeciesID " \
        "INNER JOIN animaltype t ON t.ID = a.AnimalTypeID "

def get_traploan_query(dbo):
    return "SELECT ot.ID, ot.TrapTypeID, ot.LoanDate, tt.TrapTypeName, ot.TrapNumber, " \
        "ot.DepositAmount, ot.DepositReturnDate, ot.ReturnDueDate, ot.ReturnDate, " \
        "ot.OwnerID, ot.Comments, " \
        "ot.CreatedBy, ot.CreatedDate, ot.LastChangedBy, ot.LastChangedDate, " \
        "o.OwnerTitle, o.OwnerInitials, o.OwnerSurname, o.OwnerForenames, o.OwnerName " \
        "FROM ownertraploan ot " \
        "INNER JOIN traptype tt ON tt.ID = ot.TrapTypeID " \
        "INNER JOIN owner o ON o.ID = ot.OwnerID "

def get_animalcontrol(dbo, acid):
    """
    Returns an animal control incident record
    """
    rows = db.query(dbo, get_animalcontrol_query(dbo) + " WHERE ac.ID = %d" % acid)
    if rows is None or len(rows) == 0:
        return None
    else:
        ac = rows[0]
        roles = db.query(dbo, "SELECT acr.*, r.RoleName FROM animalcontrolrole acr INNER JOIN role r ON acr.RoleID = r.ID WHERE acr.AnimalControlID = %d" % acid)
        viewroleids = []
        viewrolenames = []
        editroleids = []
        editrolenames = []
        for r in roles:
            if r["CANVIEW"] == 1:
                viewroleids.append(str(r["ROLEID"]))
                viewrolenames.append(str(r["ROLENAME"]))
            if r["CANEDIT"] == 1:
                editroleids.append(str(r["ROLEID"]))
                editrolenames.append(str(r["ROLENAME"]))
        ac["VIEWROLEIDS"] = "|".join(viewroleids)
        ac["VIEWROLES"] = "|".join(viewrolenames)
        ac["EDITROLEIDS"] = "|".join(editroleids)
        ac["EDITROLES"] = "|".join(editrolenames)
        return ac

def get_animalcontrol_animals(dbo, acid):
    return db.query(dbo, get_animalcontrol_animals_query(dbo) + " WHERE aca.AnimalControlID = %d" % acid)

def get_followup_two_dates(dbo, dbstart, dbend):
    """
    Returns incidents for followup between the two ISO dates specified
    """
    return db.query(dbo, get_animalcontrol_query(dbo) + " WHERE " \
        "(ac.FollowupDateTime >= '%(start)s' AND ac.FollowupDateTime <= '%(end)s' AND NOT ac.FollowupComplete = 1) OR " \
        "(ac.FollowupDateTime2 >= '%(start)s' AND ac.FollowupDateTime2 <= '%(end)s' AND NOT ac.FollowupComplete2 = 1) OR " \
        "(ac.FollowupDateTime3 >= '%(start)s' AND ac.FollowupDateTime3 <= '%(end)s' AND NOT ac.FollowupComplete3 = 1)" % { "start": dbstart, "end": dbend })

def get_animalcontrol_find_simple(dbo, query = "", username = "", limit = 0):
    """
    Returns rows for simple animal control searches.
    query: The search criteria
    """
    ors = []
    query = query.replace("'", "`")
    def add(field):
        return utils.where_text_filter(dbo, field, query)
    # If no query has been given, show open animal control records
    # from the last 30 days
    if query == "":
        ors.append("ac.IncidentDateTime > %s AND ac.CompletedDate Is Null" % db.dd(subtract_days(now(dbo.timezone), 30)))
    else:
        if utils.is_numeric(query):
            ors.append("ac.ID = " + str(utils.cint(query)))
        ors.append(add("co.OwnerName"))
        ors.append(add("ti.IncidentName"))
        ors.append(add("ac.DispatchAddress"))
        ors.append(add("ac.DispatchPostcode"))
        ors.append(add("o1.OwnerName"))
        ors.append(add("o2.OwnerName"))
        ors.append(add("o3.OwnerName"))
        ors.append(add("vo.OwnerName"))
        ors.append(u"EXISTS(SELECT ad.Value FROM additional ad " \
            "INNER JOIN additionalfield af ON af.ID = ad.AdditionalFieldID AND af.Searchable = 1 " \
            "WHERE ad.LinkID=ac.ID AND ad.LinkType IN (%s) AND LOWER(ad.Value) LIKE '%%%s%%')" % (additional.INCIDENT_IN, query.lower()))
        if not dbo.is_large_db:
            ors.append(add("ac.CallNotes"))
            ors.append(add("ac.AnimalDescription"))
    sql = get_animalcontrol_query(dbo) + " WHERE " + " OR ".join(ors)
    if limit > 0: sql += " LIMIT " + str(limit)
    return reduce_find_results(dbo, username, db.query(dbo, sql))

def get_animalcontrol_find_advanced(dbo, criteria, username, limit = 0):
    """
    Returns rows for advanced animal control searches.
    criteria: A dictionary of criteria
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
       pickuplocation - -1 for all or ID
       description - string partial pattern
       agegroup - agegroup text to match
       sex - -1 for all or ID
       species - -1 for all or ID
       filter - unpaid, incomplete, undispatched, requirefollowup
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
    c = []
    l = dbo.locale
    post = utils.PostedData(criteria, l)

    def hk(cfield):
        return post[cfield] != ""

    def crit(cfield):
        return post[cfield]

    def addid(cfield, field): 
        if hk(cfield) and int(crit(cfield)) != -1: 
            c.append("%s = %s" % (field, crit(cfield)))

    def addstr(cfield, field): 
        if hk(cfield) and crit(cfield) != "": 
            c.append("LOWER(%s) LIKE '%%%s%%'" % ( field, crit(cfield).lower().replace("'", "`")))

    def adddate(cfieldfrom, cfieldto, field): 
        if hk(cfieldfrom) and hk(cfieldto): 
            post.data["dayend"] = "23:59:59"
            c.append("%s >= %s AND %s <= %s" % ( 
                field, post.db_date(cfieldfrom),
                field, post.db_datetime(cfieldto, "dayend")))

    def addcomp(cfield, value, condition):
        if hk(cfield) and crit(cfield) == value: 
            c.append(condition)

    c.append("ac.ID > 0")
    if crit("number") != "": c.append("ac.ID = " + str(utils.cint(crit("number"))))
    addstr("callername", "co.OwnerName")
    addstr("victimname", "vo.OwnerName")
    addstr("callerphone", "co.HomeTelephone")
    addid("incidenttype", "ac.IncidentTypeID")
    addid("pickuplocation", "ac.PickupLocationID")
    if (crit("dispatchedaco") != "-1"): addstr("dispatchedaco", "ac.DispatchedACO")
    adddate("incidentfrom", "incidentto", "ac.IncidentDateTime")
    adddate("dispatchfrom", "dispatchto", "ac.DispatchDateTime")
    adddate("respondedfrom", "respondedto", "ac.RespondedDateTime")
    adddate("followupfrom", "followupto", "ac.FollowupDateTime")
    adddate("completedfrom", "completedto", "ac.CompletedDate")
    addid("completedtype", "ac.IncidentCompletedID")
    addid("citationtype", "ac.CitationTypeID")
    addstr("address", "ac.DispatchAddress")
    addstr("city", "ac.DispatchTown")
    addstr("postcode", "ac.DispatchPostcode")
    addstr("callnotes", "ac.CallNotes")
    addstr("description", "ac.AnimalDescription")
    if (crit("agegroup") != "-1"): addstr("agegroup", "ac.AgeGroup")
    addid("sex", "ac.Sex")
    addid("species", "ac.SpeciesID")
    addcomp("filter", "incomplete", "ac.CompletedDate Is Null")
    addcomp("filter", "undispatched", "ac.CompletedDate Is Null AND ac.CallDateTime Is Not Null AND ac.DispatchDateTime Is Null")
    addcomp("filter", "requirefollowup", "(" \
        "(ac.FollowupDateTime Is Not Null AND ac.FollowupDateTime <= %(now)s AND NOT ac.FollowupComplete = 1) OR " \
        "(ac.FollowupDateTime2 Is Not Null AND ac.FollowupDateTime2 <= %(now)s AND NOT ac.FollowupComplete2 = 1) OR " \
        "(ac.FollowupDateTime3 Is Not Null AND ac.FollowupDateTime3 <= %(now)s AND NOT ac.FollowupComplete3 = 1) " \
        ")" % { "now": db.ddt(now(dbo.timezone).replace(hour = 23, minute = 59, second = 59)) } )
    where = ""
    if len(c) > 0:
        where = " WHERE " + " AND ".join(c)
    sql = get_animalcontrol_query(dbo) + where + " ORDER BY ac.ID"
    if limit > 0: sql += " LIMIT " + str(limit)
    return reduce_find_results(dbo, username, db.query(dbo, sql))

def reduce_find_results(dbo, username, rows):
    """
    Given the results of a find operation, goes through the results and removes 
    any results which the user does not have permission to view.
    1. Because there are one or more view roles on the incident and the user doesn't have any
    2. Multi-site is on, there's a site on the incident that is not the users
    """
    # Do nothing if there are no results
    if len(rows) == 0: return rows
    u = db.query(dbo, "SELECT * FROM users WHERE UserName = %s" % db.ds(username))
    # Do nothing if we can't find the user
    if len(u) == 0: return rows
    # Do nothing if the user is a super user and has no site
    u = u[0]
    if u["SUPERUSER"] == 1 and u["SITEID"] == 0: return rows
    roles = users.get_roles_ids_for_user(dbo, username)
    # Build an IN clause of result IDs
    rids = []
    for r in rows:
        rids.append(str(r["ACID"]))
    viewroles = db.query(dbo, "SELECT * FROM animalcontrolrole WHERE AnimalControlID IN (%s)" % ",".join(rids))
    # Remove rows where the user doesn't have that role
    results = []
    for r in rows:
        rok = False
        # Compare the site ID on the incident to our user - to exclude the record,
        # both user and incident must have a site ID and they must be different
        if r["SITEID"] != 0 and u["SITEID"] != 0 and r["SITEID"] != u["SITEID"]: continue
        # Get the list of required view roles for this incident
        incroles = [ x for x in viewroles if r["ACID"] == x["ANIMALCONTROLID"] and x["CANVIEW"] == 1 ]
        # If there aren't any, it's fine to view the incident
        if len(incroles) == 0: 
            rok = True
        else:
            # If the user has any of the set view roles, we're good
            for v in incroles:
                if v["ROLEID"] in roles:
                    rok = True
        if rok:
            results.append(r)
    return results

def get_animalcontrol_satellite_counts(dbo, acid):
    """
    Returns a resultset containing the number of each type of satellite
    record that an animal control entry has.
    """
    sql = "SELECT a.ID, " \
        "(SELECT COUNT(*) FROM ownercitation oc WHERE oc.AnimalControlID = a.ID) AS citation, " \
        "(SELECT COUNT(*) FROM media me WHERE me.LinkID = a.ID AND me.LinkTypeID = %d) AS media, " \
        "(SELECT COUNT(*) FROM diary di WHERE di.LinkID = a.ID AND di.LinkType = %d) AS diary, " \
        "(SELECT COUNT(*) FROM log WHERE log.LinkID = a.ID AND log.LinkType = %d) AS logs " \
        "FROM animalcontrol a WHERE a.ID = %d" \
        % (media.ANIMALCONTROL, diary.ANIMALCONTROL, log.ANIMALCONTROL, int(acid))
    return db.query(dbo, sql)

def get_active_traploans(dbo):
    """
    Returns all active traploan records
    ID, TRAPTYPEID, TRAPTYPENAME, LOANDATE, DEPOSITRETURNDATE,
    TRAPNUMBER, RETURNDUEDATE, RETURNDATE,
    OWNERNAME
    """
    return db.query(dbo, get_traploan_query(dbo) + \
        "WHERE ot.ReturnDate Is Null OR ot.ReturnDate > %s " \
        "ORDER BY ot.LoanDate DESC" % db.dd(now(dbo.timezone)))

def get_person_traploans(dbo, oid, sort = ASCENDING):
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
    return db.query(dbo, get_traploan_query(dbo) + \
        "WHERE ot.OwnerID = %d " \
        "ORDER BY %s" % (int(oid), order))

def get_traploan_two_dates(dbo, dbstart, dbend):
    """
    Returns unreturned trap loans with a due date between the two ISO dates
    """
    return db.query(dbo, get_traploan_query(dbo) + \
        "WHERE ReturnDate Is Null AND ReturnDueDate >= '%s' AND ReturnDueDate <= '%s'" % (dbstart, dbend))

def update_animalcontrol_completenow(dbo, acid, username, completetype):
    """
    Updates an animal control incident record, marking it completed now with the type specified
    """
    db.execute(dbo, "UPDATE animalcontrol SET IncidentCompletedID=%s, CompletedDate=%s WHERE ID=%d" % (db.di(completetype), db.dd(now(dbo.timezone)), acid))
    audit.edit(dbo, username, "animalcontrol", acid, "completetype=%s, completedate=%s" % (completetype, now(dbo.timezone)))

def update_animalcontrol_dispatchnow(dbo, acid, username):
    """
    Updates an animal control incident record, marking it dispatched
    now with the current user as ACO.
    """
    db.execute(dbo, "UPDATE animalcontrol SET DispatchedACO=%s, DispatchDateTime=%s WHERE ID=%d" % (db.ds(username), db.ddt(now(dbo.timezone)), acid))
    audit.edit(dbo, username, "animalcontrol", acid, "aco=%s, dispatch=%s" % (username, now(dbo.timezone)))

def update_animalcontrol_respondnow(dbo, acid, username):
    """
    Updates an animal control incident record, marking it responded to now
    """
    db.execute(dbo, "UPDATE animalcontrol SET RespondedDateTime=%s WHERE ID=%d" % (db.ddt(now(dbo.timezone)), acid))
    audit.edit(dbo, username, "animalcontrol", acid, "responded=%s" % now(dbo.timezone))

def update_animalcontrol_from_form(dbo, post, username):
    """
    Updates an animal control incident record from the screen
    data: The webpy data object containing form parameters
    """
    l = dbo.locale
    acid = post.integer("id")

    if not db.check_recordversion(dbo, "animalcontrol", post.integer("id"), post.integer("recordversion")):
        raise utils.ASMValidationError(_("This record has been changed by another user, please reload.", l))

    if post.date("incidentdate") is None:
        raise utils.ASMValidationError(_("Incident date cannot be blank", l))

    preaudit = db.query(dbo, "SELECT * FROM animalcontrol WHERE ID = %d" % acid)
    db.execute(dbo, db.make_update_user_sql(dbo, "animalcontrol", username, "ID=%d" % acid, (
        ( "IncidentDateTime", post.db_datetime("incidentdate", "incidenttime")),
        ( "IncidentTypeID", post.db_integer("incidenttype")),
        ( "CallDateTime", post.db_datetime("calldate", "calltime")),
        ( "CallNotes", post.db_string("callnotes")),
        ( "CallTaker", post.db_string("calltaker")),
        ( "CallerID", post.db_integer("caller")),
        ( "VictimID", post.db_integer("victim")),
        ( "DispatchAddress", post.db_string("dispatchaddress")),
        ( "DispatchTown", post.db_string("dispatchtown")),
        ( "DispatchCounty", post.db_string("dispatchcounty")),
        ( "DispatchPostcode", post.db_string("dispatchpostcode")),
        ( "PickupLocationID", post.db_integer("pickuplocation")),
        ( "DispatchLatLong", post.db_string("dispatchlatlong")),
        ( "DispatchedACO", post.db_string("dispatchedaco")),
        ( "DispatchDateTime", post.db_datetime("dispatchdate", "dispatchtime")),
        ( "RespondedDateTime", post.db_datetime("respondeddate", "respondedtime")),
        ( "FollowupDateTime", post.db_datetime("followupdate", "followuptime")),
        ( "FollowupComplete", post.db_boolean("followupcomplete")),
        ( "FollowupDateTime2", post.db_datetime("followupdate2", "followuptime2")),
        ( "FollowupComplete2", post.db_boolean("followupcomplete2")),
        ( "FollowupDateTime3", post.db_datetime("followupdate3", "followuptime3")),
        ( "FollowupComplete3", post.db_boolean("followupcomplete3")),
        ( "CompletedDate", post.db_date("completeddate")),
        ( "IncidentCompletedID", post.db_integer("completedtype")),
        ( "SiteID", post.db_integer("site")),
        ( "OwnerID", post.db_integer("owner")),
        ( "Owner2ID", post.db_integer("owner2")),
        ( "Owner3ID", post.db_integer("owner3")),
        ( "AnimalDescription", post.db_string("animaldescription")),
        ( "SpeciesID", post.db_integer("species")),
        ( "Sex", post.db_integer("sex")),
        ( "AgeGroup", post.db_string("agegroup"))
    )))
    additional.save_values_for_link(dbo, post, acid, "incident")
    postaudit = db.query(dbo, "SELECT * FROM animalcontrol WHERE ID = %d" % acid)
    audit.edit(dbo, username, "animalcontrol", acid, audit.map_diff(preaudit, postaudit))

    # Update view/edit roles
    db.execute(dbo, "DELETE FROM animalcontrolrole WHERE AnimalControlID = %d" % acid)
    for rid in post.integer_list("viewroles"):
        db.execute(dbo, "INSERT INTO animalcontrolrole (AnimalControlID, RoleID, CanView, CanEdit) VALUES (%d, %d, 1, 0)" % (acid, rid))
    for rid in post.integer_list("editroles"):
        if rid in post.integer_list("viewroles"):
            db.execute(dbo, "UPDATE animalcontrolrole SET CanEdit = 1 WHERE AnimalControlID = %d AND RoleID = %d" % (acid, rid))
        else:
            db.execute(dbo, "INSERT INTO animalcontrolrole (AnimalControlID, RoleID, CanView, CanEdit) VALUES (%d, %d, 0, 1)" % (acid, rid))

def update_animalcontrol_addlink(dbo, username, acid, animalid):
    """
    Adds a link between an animal and an incident.
    """
    l = dbo.locale
    if 0 != db.query_int(dbo, "SELECT COUNT(*) FROM animalcontrolanimal WHERE AnimalControlID = %d AND AnimalID = %d" % (acid, animalid)):
        raise utils.ASMValidationError(_("That animal is already linked to the incident", l))
    db.execute(dbo, "INSERT INTO animalcontrolanimal (AnimalControlID, AnimalID) VALUES (%d, %d)" % (acid, animalid))
    audit.create(dbo, username, "animalcontrolanimal", acid, "incident %d linked to animal %d" % (acid, animalid))

def update_animalcontrol_removelink(dbo, username, acid, animalid):
    """
    Removes a link between an animal and an incident.
    """
    db.execute(dbo, "DELETE FROM animalcontrolanimal WHERE AnimalControlID = %d AND AnimalID = %d" % (acid, animalid))
    audit.delete(dbo, username, "animalcontrolanimal", acid, "incident %d no longer linked to animal %d" % (acid, animalid))

def insert_animalcontrol_from_form(dbo, post, username):
    """
    Inserts a new animal control incident record from the screen
    data: The webpy data object containing form parameters
    """
    l = dbo.locale
    if post.date("incidentdate") is None:
        raise utils.ASMValidationError(_("Incident date cannot be blank", l))

    nid = db.get_id(dbo, "animalcontrol")
    db.execute(dbo, db.make_insert_user_sql(dbo, "animalcontrol", username, (
        ( "ID", db.di(nid)),
        ( "IncidentDateTime", post.db_datetime("incidentdate", "incidenttime")),
        ( "IncidentTypeID", post.db_integer("incidenttype")),
        ( "CallDateTime", post.db_datetime("calldate", "calltime")),
        ( "CallNotes", post.db_string("callnotes")),
        ( "CallTaker", post.db_string("calltaker")),
        ( "CallerID", post.db_integer("caller")),
        ( "VictimID", post.db_integer("victim")),
        ( "DispatchAddress", post.db_string("dispatchaddress")),
        ( "DispatchTown", post.db_string("dispatchtown")),
        ( "DispatchCounty", post.db_string("dispatchcounty")),
        ( "DispatchPostcode", post.db_string("dispatchpostcode")),
        ( "PickupLocationID", post.db_integer("pickuplocation")),
        ( "DispatchLatLong", post.db_string("dispatchlatlong")),
        ( "DispatchedACO", post.db_string("dispatchedaco")),
        ( "DispatchDateTime", post.db_datetime("dispatchdate", "dispatchtime")),
        ( "RespondedDateTime", post.db_datetime("respondeddate", "respondedtime")),
        ( "FollowupDateTime", post.db_datetime("followupdate", "followuptime")),
        ( "FollowupComplete", post.db_boolean("followupcomplete")),
        ( "FollowupDateTime2", post.db_datetime("followupdate2", "followuptime2")),
        ( "FollowupComplete2", post.db_boolean("followupcomplete2")),
        ( "FollowupDateTime3", post.db_datetime("followupdate3", "followuptime3")),
        ( "FollowupComplete3", post.db_boolean("followupcomplete3")),
        ( "CompletedDate", post.db_date("completeddate")),
        ( "IncidentCompletedID", post.db_integer("completedtype")),
        ( "SiteID", post.db_integer("site")),
        ( "OwnerID", post.db_integer("owner")),
        ( "Owner2ID", post.db_integer("owner2")),
        ( "Owner3ID", post.db_integer("owner3")),
        ( "AnimalDescription", post.db_string("animaldescription")),
        ( "SpeciesID", post.db_integer("species")),
        ( "Sex", post.db_integer("sex")),
        ( "AgeGroup", post.db_string("agegroup"))
        )))
    audit.create(dbo, username, "animalcontrol", nid, audit.dump_row(dbo, "animalcontrol", nid))

    # Save any additional field values given
    additional.save_values_for_link(dbo, post, nid, "incident")

    # Update view/edit roles
    db.execute(dbo, "DELETE FROM animalcontrolrole WHERE AnimalControlID = %d" % nid)
    for rid in post.integer_list("viewroles"):
        db.execute(dbo, "INSERT INTO animalcontrolrole (AnimalControlID, RoleID, CanView, CanEdit) VALUES (%d, %d, 1, 0)" % (nid, rid))
    for rid in post.integer_list("editroles"):
        if rid in post.integer_list("viewroles"):
            db.execute(dbo, "UPDATE animalcontrolrole SET CanEdit = 1 WHERE AnimalControlID = %d AND RoleID = %d" % (nid, rid))
        else:
            db.execute(dbo, "INSERT INTO animalcontrolrole (AnimalControlID, RoleID, CanView, CanEdit) VALUES (%d, %d, 0, 1)" % (nid, rid))

    return nid

def delete_animalcontrol(dbo, username, acid):
    """
    Deletes an animal control record
    """
    audit.delete(dbo, username, "animalcontrol", acid, audit.dump_row(dbo, "animalcontrol", acid))
    db.execute(dbo, "DELETE FROM animalcontrol WHERE ID = %d" % acid)
    db.execute(dbo, "DELETE FROM media WHERE LinkID = %d AND LinkTypeID = %d" % (acid, media.ANIMALCONTROL))
    db.execute(dbo, "DELETE FROM diary WHERE LinkID = %d AND LinkType = %d" % (acid, diary.ANIMALCONTROL))
    db.execute(dbo, "DELETE FROM log WHERE LinkID = %d AND LinkType = %d" % (acid, log.ANIMALCONTROL))
    db.execute(dbo, "DELETE FROM additional WHERE LinkID = %d AND LinkType IN (%s)" % (acid, additional.INCIDENT_IN))

def insert_animalcontrol(dbo, username):
    """
    Creates a new animal control incident record and returns the id
    """
    l = dbo.locale
    d = {
        "incidentdate":     python2display(l, now(dbo.timezone)),
        "incidenttime":     format_time_now(dbo.timezone),
        "incidenttype":     configuration.default_incident(dbo),
        "calldate":         python2display(l, now(dbo.timezone)),
        "calltime":         format_time_now(dbo.timezone),
        "calltaker":        username
    }
    return insert_animalcontrol_from_form(dbo, utils.PostedData(d, dbo.locale), username)

def insert_traploan_from_form(dbo, username, post):
    """
    Creates a traploan record from posted form data 
    """
    traploanid = db.get_id(dbo, "ownertraploan")
    sql = db.make_insert_user_sql(dbo, "ownertraploan", username, ( 
        ( "ID", db.di(traploanid)),
        ( "OwnerID", post.db_integer("person")),
        ( "TrapTypeID", post.db_integer("type")),
        ( "LoanDate", post.db_date("loandate")),
        ( "DepositAmount", post.db_integer("depositamount")),
        ( "DepositReturnDate", post.db_date("depositreturndate")),
        ( "TrapNumber", post.db_string("trapnumber")),
        ( "ReturnDueDate", post.db_date("returnduedate")),
        ( "ReturnDate", post.db_date("returndate")),
        ( "Comments", post.db_string("comments"))
        ))
    db.execute(dbo, sql)
    audit.create(dbo, username, "ownertraploan", traploanid, audit.dump_row(dbo, "ownertraploan", traploanid))
    return traploanid

def update_traploan_from_form(dbo, username, post):
    """
    Updates a traploan record from posted form data
    """
    traploanid = post.integer("traploanid")
    sql = db.make_update_user_sql(dbo, "ownertraploan", username, "ID=%d" % traploanid, ( 
        ( "OwnerID", post.db_integer("person")),
        ( "TrapTypeID", post.db_integer("type")),
        ( "LoanDate", post.db_date("loandate")),
        ( "DepositAmount", post.db_integer("depositamount")),
        ( "DepositReturnDate", post.db_date("depositreturndate")),
        ( "TrapNumber", post.db_string("trapnumber")),
        ( "ReturnDueDate", post.db_date("returnduedate")),
        ( "ReturnDate", post.db_date("returndate")),
        ( "Comments", post.db_string("comments"))
    ))
    preaudit = db.query(dbo, "SELECT * FROM ownertraploan WHERE ID = %d" % traploanid)
    db.execute(dbo, sql)
    postaudit = db.query(dbo, "SELECT * FROM ownertraploan WHERE ID = %d" % traploanid)
    audit.edit(dbo, username, "ownertraploan", traploanid, audit.map_diff(preaudit, postaudit))

def delete_traploan(dbo, username, tid):
    """
    Deletes a traploan record
    """
    audit.delete(dbo, username, "ownertraploan", tid, audit.dump_row(dbo, "ownertraploan", tid))
    db.execute(dbo, "DELETE FROM ownertraploan WHERE ID = %d" % int(tid))

def update_dispatch_latlong(dbo, incidentid, latlong):
    """
    Updates the dispatch latlong field.
    """
    db.execute(dbo, "UPDATE animalcontrol SET DispatchLatLong = %s WHERE ID = %d" % (db.ds(latlong), int(incidentid)))


