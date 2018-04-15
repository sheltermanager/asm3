#!/usr/bin/python

import additional
import audit
import configuration
import dbfs
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
        "ti.IncidentName, ci.CompletedName, pl.LocationName, j.JurisdictionName, " \
        "web.ID AS WebsiteMediaID, " \
        "web.MediaName AS WebsiteMediaName, " \
        "web.Date AS WebsiteMediaDate, " \
        "web.MediaNotes AS WebsiteMediaNotes " \
        "FROM animalcontrol ac " \
        "LEFT OUTER JOIN species s ON s.ID = ac.SpeciesID " \
        "LEFT OUTER JOIN lksex x ON x.ID = ac.Sex " \
        "LEFT OUTER JOIN jurisdiction j ON j.ID = ac.JurisdictionID " \
        "LEFT OUTER JOIN owner co ON co.ID = ac.CallerID " \
        "LEFT OUTER JOIN owner o1 ON o1.ID = ac.OwnerID " \
        "LEFT OUTER JOIN owner o2 ON o2.ID = ac.Owner2ID " \
        "LEFT OUTER JOIN owner o3 ON o3.ID = ac.Owner3ID " \
        "LEFT OUTER JOIN owner vo ON vo.ID = ac.VictimID " \
        "LEFT OUTER JOIN media web ON web.LinkID = ac.ID AND web.LinkTypeID = 6 AND web.WebsitePhoto = 1 " \
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

def get_animalcontrol_animals(dbo, acid):
    """ Return the list of linked animals for an incident """
    return dbo.query(get_animalcontrol_animals_query(dbo) + " WHERE aca.AnimalControlID = ?", [acid])

def get_animalcontrol_for_animal(dbo, aid):
    """ Return the list of linked incidents for an animal """
    return dbo.query(get_animalcontrol_query(dbo) + " INNER JOIN animalcontrolanimal aca ON aca.AnimalControlID = ac.ID WHERE aca.AnimalID = ? ORDER BY IncidentDateTime DESC", [aid])

def get_followup_two_dates(dbo, start, end):
    """
    Returns incidents for followup between the two dates specified
    """
    return dbo.query(get_animalcontrol_query(dbo) + " WHERE " \
        "(ac.FollowupDateTime >= ? AND ac.FollowupDateTime <= ? AND NOT ac.FollowupComplete = 1) OR " \
        "(ac.FollowupDateTime2 >= ? AND ac.FollowupDateTime2 <= ? AND NOT ac.FollowupComplete2 = 1) OR " \
        "(ac.FollowupDateTime3 >= ? AND ac.FollowupDateTime3 <= ? AND NOT ac.FollowupComplete3 = 1)", (start, end, start, end, start, end))

def get_animalcontrol_find_simple(dbo, query = "", username = "", limit = 0):
    """
    Returns rows for simple animal control searches.
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
    # If no query has been given, show open animal control records
    # from the last 30 days
    if query == "":
        ors.append("ac.IncidentDateTime > %s AND ac.CompletedDate Is Null" % dbo.sql_date(subtract_days(dbo.today(), 30)))
    else:
        if utils.is_numeric(query):
            ors.append("ac.ID = %s" % utils.cint(query))
        add("co.OwnerName")
        add("ti.IncidentName")
        add("ac.DispatchAddress")
        add("ac.DispatchPostcode")
        add("o1.OwnerName")
        add("o2.OwnerName")
        add("o3.OwnerName")
        add("vo.OwnerName")
        addclause(u"EXISTS(SELECT ad.Value FROM additional ad " \
            "INNER JOIN additionalfield af ON af.ID = ad.AdditionalFieldID AND af.Searchable = 1 " \
            "WHERE ad.LinkID=ac.ID AND ad.LinkType IN (%s) AND LOWER(ad.Value) LIKE ?)" % (additional.INCIDENT_IN))
        if not dbo.is_large_db:
            add("ac.CallNotes")
            add("ac.AnimalDescription")
    sql = "%s WHERE %s ORDER BY ac.ID" % ( \
        get_animalcontrol_query(dbo),
        " OR ".join(ors))
    return reduce_find_results(dbo, username, dbo.query(sql, values, limit=limit))

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
       jurisdiction - -1 for all or ID
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
    ands = []
    values = []
    l = dbo.locale
    post = utils.PostedData(criteria, l)

    def addid(cfield, field): 
        if post[cfield] != "" and post.integer(cfield) > -1:
            ands.append("%s = ?" % field)
            values.append(post.integer(cfield))

    def addidpair(cfield, field, field2): 
        if post[cfield] != "" and post.integer(cfield) > 0: 
            ands.append("(%s = ? OR %s = ?)" % (field, field2))
            values.append(post.integer(cfield))
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

    ands.append("ac.ID > 0")
    addid("number", "ac.ID")
    addstr("callername", "co.OwnerName")
    addstr("victimname", "vo.OwnerName")
    addstr("callerphone", "co.HomeTelephone")
    addid("incidenttype", "ac.IncidentTypeID")
    addid("pickuplocation", "ac.PickupLocationID")
    addid("jurisdiction", "ac.JurisdictionID")
    if post["dispatchedaco"] != "-1": addstr("dispatchedaco", "ac.DispatchedACO")
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
    if post["agegroup"] != "-1": addstr("agegroup", "ac.AgeGroup")
    addid("sex", "ac.Sex")
    addid("species", "ac.SpeciesID")
    addfilter("incomplete", "ac.CompletedDate Is Null")
    addfilter("undispatched", "ac.CompletedDate Is Null AND ac.CallDateTime Is Not Null AND ac.DispatchDateTime Is Null")
    addfilter("requirefollowup", "(" \
        "(ac.FollowupDateTime Is Not Null AND ac.FollowupDateTime <= %(now)s AND NOT ac.FollowupComplete = 1) OR " \
        "(ac.FollowupDateTime2 Is Not Null AND ac.FollowupDateTime2 <= %(now)s AND NOT ac.FollowupComplete2 = 1) OR " \
        "(ac.FollowupDateTime3 Is Not Null AND ac.FollowupDateTime3 <= %(now)s AND NOT ac.FollowupComplete3 = 1) " \
        ")" % { "now": dbo.sql_date(dbo.now(settime="23:59:59")) } )
    sql = "%s WHERE %s ORDER BY ac.ID" % (get_animalcontrol_query(dbo), " AND ".join(ands))
    return reduce_find_results(dbo, username, dbo.query(sql, values, limit=limit))

def reduce_find_results(dbo, username, rows):
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
    roles = users.get_roles_ids_for_user(dbo, username)
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

def check_view_permission(dbo, username, session, acid):
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
    raise utils.ASMPermissionError("User does not have required role to view this incident")

def get_animalcontrol_satellite_counts(dbo, acid):
    """
    Returns a resultset containing the number of each type of satellite
    record that an animal control entry has.
    """
    return dbo.query("SELECT a.ID, " \
        "(SELECT COUNT(*) FROM ownercitation oc WHERE oc.AnimalControlID = a.ID) AS citation, " \
        "(SELECT COUNT(*) FROM media me WHERE me.LinkID = a.ID AND me.LinkTypeID = ?) AS media, " \
        "(SELECT COUNT(*) FROM diary di WHERE di.LinkID = a.ID AND di.LinkType = ?) AS diary, " \
        "(SELECT COUNT(*) FROM log WHERE log.LinkID = a.ID AND log.LinkType = ?) AS logs " \
        "FROM animalcontrol a WHERE a.ID = ?", (media.ANIMALCONTROL, diary.ANIMALCONTROL, log.ANIMALCONTROL, acid))

def get_active_traploans(dbo):
    """
    Returns all active traploan records
    ID, TRAPTYPEID, TRAPTYPENAME, LOANDATE, DEPOSITRETURNDATE,
    TRAPNUMBER, RETURNDUEDATE, RETURNDATE,
    OWNERNAME
    """
    return dbo.query(get_traploan_query(dbo) + \
        "WHERE ot.ReturnDate Is Null OR ot.ReturnDate > ? " \
        "ORDER BY ot.LoanDate DESC", [dbo.today()])

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
    return dbo.query(get_traploan_query(dbo) + \
        "WHERE ot.OwnerID = ? " \
        "ORDER BY %s" % order, [oid])

def get_traploan_two_dates(dbo, start, end):
    """
    Returns unreturned trap loans with a due date between the two dates
    """
    return dbo.query(get_traploan_query(dbo) + \
        "WHERE ReturnDate Is Null AND ReturnDueDate >= ? AND ReturnDueDate <= ?", (start, end))

def update_animalcontrol_completenow(dbo, acid, username, completetype):
    """
    Updates an animal control incident record, marking it completed now with the type specified
    """
    dbo.update("animalcontrol", acid, {
        "IncidentCompletedID":  completetype,
        "CompletedDate":         dbo.today(),
    }, username)

def update_animalcontrol_dispatchnow(dbo, acid, username):
    """
    Updates an animal control incident record, marking it dispatched
    now with the current user as ACO.
    """
    dbo.update("animalcontrol", acid, {
        "DispatchedACO":        username,
        "DispatchDateTime":     dbo.now()
    }, username)

def update_animalcontrol_respondnow(dbo, acid, username):
    """
    Updates an animal control incident record, marking it responded to now
    """
    dbo.update("animalcontrol", acid, {
        "RespondedDateTime":    dbo.now()
    }, username)

def update_animalcontrol_from_form(dbo, post, username):
    """
    Updates an animal control incident record from the screen
    data: The webpy data object containing form parameters
    """
    l = dbo.locale
    acid = post.integer("id")

    if not dbo.optimistic_check("animalcontrol", post.integer("id"), post.integer("recordversion")):
        raise utils.ASMValidationError(_("This record has been changed by another user, please reload.", l))

    if post.date("incidentdate") is None:
        raise utils.ASMValidationError(_("Incident date cannot be blank", l))

    dbo.update("animalcontrol", acid, {
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
        "CompletedDate":        post.date("completeddate"),
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

    additional.save_values_for_link(dbo, post, acid, "incident")
    update_animalcontrol_roles(dbo, acid, post.integer_list("viewroles"), post.integer_list("editroles"))

def update_animalcontrol_roles(dbo, acid, viewroles, editroles):
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

def update_animalcontrol_addlink(dbo, username, acid, animalid):
    """
    Adds a link between an animal and an incident.
    """
    l = dbo.locale
    if 0 != dbo.query_int("SELECT COUNT(*) FROM animalcontrolanimal WHERE AnimalControlID = ? AND AnimalID = ?", (acid, animalid)):
        raise utils.ASMValidationError(_("That animal is already linked to the incident", l))
    dbo.execute("INSERT INTO animalcontrolanimal (AnimalControlID, AnimalID) VALUES (?, ?)", (acid, animalid))
    audit.create(dbo, username, "animalcontrolanimal", acid, "incident %d linked to animal %d" % (acid, animalid))

def update_animalcontrol_removelink(dbo, username, acid, animalid):
    """
    Removes a link between an animal and an incident.
    """
    dbo.execute("DELETE FROM animalcontrolanimal WHERE AnimalControlID = ? AND AnimalID = ?", (acid, animalid))
    audit.delete(dbo, username, "animalcontrolanimal", acid, "incident %d no longer linked to animal %d" % (acid, animalid))

def insert_animalcontrol_from_form(dbo, post, username):
    """
    Inserts a new animal control incident record from the screen
    data: The webpy data object containing form parameters
    """
    l = dbo.locale
    if post.date("incidentdate") is None:
        raise utils.ASMValidationError(_("Incident date cannot be blank", l))

    nid = dbo.insert("animalcontrol", {
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
        "CompletedDate":        post.date("completeddate"),
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

    additional.save_values_for_link(dbo, post, nid, "incident")
    update_animalcontrol_roles(dbo, nid, post.integer_list("viewroles"), post.integer_list("editroles"))
    return nid

def delete_animalcontrol(dbo, username, acid):
    """
    Deletes an animal control record
    """
    dbo.delete("media", "LinkID=%d AND LinkTypeID=%d" % (acid, media.ANIMALCONTROL), username)
    dbo.delete("diary", "LinkID=%d AND LinkType=%d" % (acid, diary.ANIMALCONTROL), username)
    dbo.delete("log", "LinkID=%d AND LinkType=%d" % (acid, log.ANIMALCONTROL), username)
    dbo.execute("DELETE FROM additional WHERE LinkID = %d AND LinkType IN (%s)" % (acid, additional.INCIDENT_IN))
    dbo.delete("animalcontrol", acid, username)
    dbfs.delete_path(dbo, "/animalcontrol/%d" % acid)

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

def update_traploan_from_form(dbo, username, post):
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

def delete_traploan(dbo, username, tid):
    """
    Deletes a traploan record
    """
    dbo.delete("ownertraploan", tid, username)

def update_dispatch_latlong(dbo, incidentid, latlong):
    """
    Updates the dispatch latlong field.
    """
    dbo.update("animalcontrol", incidentid, {
        "DispatchLatLong":  latlong
    })


