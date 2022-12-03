
import asm3.al
import asm3.animal
import asm3.asynctask
import asm3.configuration
import asm3.i18n
import asm3.lostfound
import asm3.person
import asm3.users
import asm3.utils
import asm3.waitinglist
import asm3.wordprocessor

# Diary Links
NO_LINK = 0
ANIMAL = 1
PERSON = 2
LOSTANIMAL = 3
FOUNDANIMAL = 4
WAITINGLIST = 5
MOVEMENT = 6
ANIMALCONTROL = 7

ANIMAL_TASK = 0
PERSON_TASK = 1

def email_uncompleted_upto_today(dbo):
    """
    Goes through all system users and emails them their diary for the
    day - unless the option is turned off.
    """
    if not asm3.configuration.email_diary_notes(dbo): return
    l = dbo.locale
    try:
        allusers = asm3.users.get_users(dbo)
    except Exception as err:
        asm3.al.error("failed getting list of users: %s" % str(err), "diary.email_uncompleted_upto_today", dbo)
    # Grab list of diary notes for today
    notes = get_uncompleted_upto_today(dbo)
    # If we don't have any, bail out
    if len(notes) == 0: return
    # Go through all user to see if we have relevant notes for them
    for u in allusers:
        if u.emailaddress and u.emailaddress.strip() != "":
            s = ""
            totalforuser = 0
            for n in notes:
                # Is this note relevant for this user?
                if (n.diaryforname == "*") \
                or (n.diaryforname == u.username) \
                or (n.diaryforname in u.roles.split("|")):
                    s += "%s %s - %s - " % (asm3.i18n.python2display(l, n.diarydatetime), asm3.i18n.format_time(n.diarydatetime), n.diaryforname)
                    s += n.subject
                    if n.linkinfo is not None and n.linkinfo != "": s += " / %s" % n.linkinfo
                    s += " (%s)" % n.createdby
                    s += "\n%s\n\n%s" % (n.note, n.comments)
                    totalforuser += 1
            if totalforuser > 0:
                asm3.al.debug("got %d notes for user %s" % (totalforuser, u.username), "diary.email_uncompleted_upto_today", dbo)
                subject = asm3.i18n._("Diary notes for: {0}", l).format(asm3.i18n.python2display(l, dbo.now()))
                asm3.utils.send_email(dbo, asm3.configuration.email(dbo), u.emailaddress, "", "", subject, s, exceptions=False, bulk=True)
                if asm3.configuration.audit_on_send_email(dbo): 
                    asm3.audit.email(dbo, "system", asm3.configuration.email(dbo), u.emailaddress, "", "", subject, s)

def email_note_on_change(dbo, n, username):
    """
    Emails the recipients of a diary note n with the note content
    username the user triggering the send by adding/updating a diary
    """
    if not asm3.configuration.email_diary_on_change(dbo): return
    if n is None: return
    l = dbo.locale
    allusers = asm3.users.get_users(dbo)
    s = asm3.i18n._("Diary change triggered by {0} on {1}", l).format(username, asm3.i18n.python2display(l, dbo.now()))
    s += "\n\n%s %s - %s - " % (asm3.i18n.python2display(l, n.diarydatetime), asm3.i18n.format_time(n.diarydatetime), n.diaryforname)
    s += n.subject
    if n.linkinfo is not None and n.linkinfo != "": s += " / %s" % n.linkinfo
    s += "\n%s\n\n%s" % (n.note, n.comments)
    for u in allusers:
        if u.emailaddress and u.emailaddress.strip() != "":
            # Is this note relevant for this user?
            if (n.diaryforname == "*") \
            or (n.diaryforname == u.username) \
            or (n.diaryforname in u.roles.split("|")):
                # Yes, send it to them
                subject = asm3.i18n._("Diary update: {0}", l).format(n.subject)
                asm3.utils.send_email(dbo, asm3.configuration.email(dbo), u.emailaddress, "", "", subject, s, exceptions=False, bulk=True)
                if asm3.configuration.audit_on_send_email(dbo): 
                    asm3.audit.email(dbo, username, asm3.configuration.email(dbo), u.emailaddress, "", "", subject, s)

def email_note_on_complete(dbo, n, username):
    """
    Emails the creator of a diary note n with the note's content 
    username the user triggering the send by completing a diary
    """
    if not asm3.configuration.email_diary_on_complete(dbo): return
    if n is None: return
    l = dbo.locale
    allusers = asm3.users.get_users(dbo)
    s = asm3.i18n._("Diary completion triggered by {0} on {1}", l).format(username, asm3.i18n.python2display(l, dbo.now()))
    s += "\n\n%s %s - %s - " % (asm3.i18n.python2display(l, n.diarydatetime), asm3.i18n.format_time(n.diarydatetime), n.diaryforname)
    s += n.subject
    if n.linkinfo is not None and n.linkinfo != "": s += " / %s" % n.linkinfo
    s += "\n%s\n\n%s" % (n.note, n.comments)
    for u in allusers:
        if u.emailaddress and u.emailaddress.strip() != "":
            # Is this note relevant for this user?
            if (n.createdby == u.username):
                # Yes, send it to them
                subject = asm3.i18n._("Diary complete: {0}", l).format(n.subject)
                asm3.utils.send_email(dbo, asm3.configuration.email(dbo), u.emailaddress, "", "", subject, s, exceptions=False, bulk=True)
                if asm3.configuration.audit_on_send_email(dbo): 
                    asm3.audit.email(dbo, username, asm3.configuration.email(dbo), u.emailaddress, "", "", subject, s)

def user_role_where_clause(dbo, user = "", includecreatedby = True):
    """
    Returns a suitable where clause for filtering diary notes
    to the given user or any roles the user is in. If user is
    blank, the where clause return is empty.
    includecreatedby: If true includes diary notes this user created as well as those for them.
    """
    if user == "": return "1=1"
    roles = asm3.users.get_roles_for_user(dbo, user)
    createdby = ""
    if includecreatedby: createdby = "OR CreatedBy = %s" % dbo.sql_value(user)
    if len(roles) == 0: return "(DiaryForName = %s %s)" % (dbo.sql_value(user), createdby)
    sroles = []
    for r in roles:
        sroles.append(dbo.sql_value(r))
    return "(DiaryForName = %s %s OR DiaryForName IN (%s))" % (dbo.sql_value(user), createdby, ",".join(sroles))

def get_between_two_dates(dbo, user, start, end):
    """
    Gets a list of incomplete diary notes between two dates for the user supplied
    LINKID, LINKTYPE, DIARYDATETIME, DIARYFORNAME, SUBJECT, NOTE, LINKINFO
    start: Start date
    end: End date
    """
    return dbo.query("SELECT d.*, cast(DiaryDateTime AS time) AS DiaryTime " \
        "FROM diary d WHERE %s " \
        "AND DateCompleted Is Null AND DiaryDateTime >= ? AND DiaryDateTime <= ? " \
        "ORDER BY DiaryDateTime DESC" % user_role_where_clause(dbo, user), (start, end))

def get_uncompleted_upto_today(dbo, user = "", includecreatedby = True, offset=-99999):
    """
    Gets a list of uncompleted diary notes upto and including
    today for the user supplied (or all users if no user passed)
    LINKID, LINKTYPE, DIARYDATETIME, DIARYFORNAME, SUBJECT, NOTE, LINKINFO
    offset: A negative day value to go back (eg: -182 = stop at 6 months)
    """
    cutoff = dbo.today(offset = offset)
    alltoday = dbo.today(settime = "23:59:59")
    return dbo.query("SELECT d.*, cast(DiaryDateTime AS time) AS DiaryTime " \
        "FROM diary d WHERE %s " \
        "AND d.DateCompleted Is Null AND d.DiaryDateTime <= ? AND d.DiaryDateTime >= ? " \
        "ORDER BY d.DiaryDateTime DESC" % user_role_where_clause(dbo, user, includecreatedby), ( alltoday, cutoff ))

def get_completed_upto_today(dbo, user = ""):
    """
    Gets a list of completed diary notes upto and including
    today for the user supplied (or all users if no user passed)
    LINKID, LINKTYPE, DIARYDATETIME, DIARYFORNAME, SUBJECT, NOTE, LINKINFO
    """
    cutoff = dbo.today(offset = -99999)
    return dbo.query("SELECT d.*, cast(DiaryDateTime AS time) AS DiaryTime " \
        "FROM diary d WHERE %s " \
        "AND d.DateCompleted Is Not Null AND d.DiaryDateTime <= ? AND d.DiaryDateTime >= ? " \
        "ORDER BY d.DiaryDateTime DESC" % user_role_where_clause(dbo, user), ( dbo.now(), cutoff ))

def get_all_upto_today(dbo, user = ""):
    """f
    Gets a list of all diary notes upto and including
    today for the user supplied (or all users if no user passed)
    LINKID, LINKTYPE, DIARYDATETIME, DIARYFORNAME, SUBJECT, NOTE, LINKINFO
    """
    cutoff = dbo.today(offset = -99999)
    return dbo.query("SELECT d.*, cast(DiaryDateTime AS time) AS DiaryTime " \
        "FROM diary d WHERE %s " \
        "AND d.DiaryDateTime <= ? AND d.DiaryDateTime >= ? " \
        "ORDER BY d.DiaryDateTime DESC" % user_role_where_clause(dbo, user), ( dbo.now(), cutoff ))

def get_future(dbo, user = ""):
    """
    Gets a list of future diary notes
    for the user supplied (or all users if no user passed)
    LINKID, LINKTYPE, DIARYDATETIME, DIARYFORNAME, SUBJECT, NOTE, LINKINFO
    """
    return dbo.query("SELECT d.*, cast(DiaryDateTime AS time) AS DiaryTime " \
        "FROM diary d WHERE %s " \
        "AND d.DiaryDateTime > ? " \
        "ORDER BY d.DiaryDateTime" % user_role_where_clause(dbo, user), [ dbo.now() ])

def complete_diary_note(dbo, username, diaryid):
    """
    Marks a diary note completed as of right now
    """
    dbo.update("diary", diaryid, {
        "DateCompleted": dbo.today()
    }, username)
    email_note_on_complete(dbo, get_diary(dbo, diaryid), username)

def complete_diary_notes_for_animal(dbo, username, animalid):
    """
    Marks all diary notes for an animal complete.
    """
    dbo.update("diary", "LinkType=%d AND LinkID=%d" % (ANIMAL, animalid), {
        "DateCompleted": dbo.today()
    }, username)
    for n in dbo.query("SELECT ID FROM diary WHERE LinkType=%d AND LinkID=%d" % (ANIMAL, animalid)):
        email_note_on_complete(dbo, get_diary(dbo, n.id), username)

def rediarise_diary_note(dbo, username, diaryid, newdate):
    """
    Moves a diary note on to the date supplied (newdate is a python date)
    """
    dbo.update("diary", diaryid, {
        "DiaryDateTime": newdate
    }, username)
    email_note_on_change(dbo, get_diary(dbo, diaryid), username)

def get_animal_tasks(dbo):
    """
    Lists all diary tasks for animals
    """
    return dbo.query("SELECT dth.*, CASE " \
        "WHEN EXISTS(SELECT dtd.* FROM diarytaskdetail dtd WHERE " \
        "DiaryTaskHeadID = dth.ID AND dtd.DayPivot = 9999) THEN 1 " \
        "ELSE 0 END AS NEEDSDATE " \
        "FROM diarytaskhead dth WHERE dth.RecordType = %d" % ANIMAL_TASK)

def get_person_tasks(dbo):
    """
    Lists all diary tasks for people
    """
    return dbo.query("SELECT dth.*, CASE " \
        "WHEN EXISTS(SELECT dtd.* FROM diarytaskdetail dtd WHERE " \
        "DiaryTaskHeadID = dth.ID AND dtd.DayPivot = 9999) THEN 1 " \
        "ELSE 0 END AS NEEDSDATE " \
        "FROM diarytaskhead dth WHERE dth.RecordType = %d" % PERSON_TASK)

def get_diarytasks(dbo):
    """
    Returns all diary tasks headers with a NUMBEROFTASKS value.
    """
    return dbo.query("SELECT dth.*, " \
        "(SELECT COUNT(*) FROM diarytaskdetail WHERE DiaryTaskHeadID = dth.ID) AS NUMBEROFTASKS " \
        "FROM diarytaskhead dth " \
        "ORDER BY dth.Name")

def get_diarytask_name(dbo, taskid):
    """
    Returns the name for a diarytask
    """
    return dbo.query_string("SELECT Name FROM diarytaskhead WHERE ID = ?", [taskid])

def get_diarytask_details(dbo, headid):
    """
    Returns the detail rows for a diary task
    """
    rows = dbo.query("SELECT * FROM diarytaskdetail WHERE DiaryTaskHeadID = ?", [headid])
    for r in rows:
        r["SUBJECT"] = r["SUBJECT"]
        r["NOTE"] = r["NOTE"]
    return rows

def get_diary(dbo, diaryid):
    """
    Returns a diary record
    """
    return dbo.first_row(dbo.query("SELECT * FROM diary WHERE ID = ?", [diaryid]))

def delete_diary(dbo, username, diaryid):
    """
    Deletes a diary record
    """
    dbo.delete("diary", diaryid, username)

def get_diaries(dbo, linktypeid, linkid):
    """
    Returns all diary notes for a particular link
    """
    return dbo.query("SELECT d.*, cast(DiaryDateTime AS time) AS DiaryTime " \
        "FROM diary d WHERE d.LinkType= ? AND d.LinkID= ? " \
        "ORDER BY d.DiaryDateTime", (linktypeid, linkid) )

def get_link_info(dbo, linktypeid, linkid):
    """
    Returns the linkinfo string for the id/type
    """
    l = dbo.locale
    if linktypeid == ANIMAL:
        return "%s [%s]" % (asm3.animal.get_animal_namecode(dbo, linkid), asm3.animal.get_display_location_noq(dbo, linkid))

    elif linktypeid == ANIMALCONTROL:
        return asm3.i18n._("Incident: {0}").format(asm3.animalcontrol.get_animalcontrol_numbertype(dbo, linkid))

    elif linktypeid == PERSON:
        return asm3.person.get_person_name(dbo, linkid)

    elif linktypeid == LOSTANIMAL:
        return asm3.i18n._("Lost Animal: {0}", l).format(asm3.lostfound.get_lost_person_name(dbo, linkid))

    elif linktypeid == FOUNDANIMAL:
        return asm3.i18n._("Found Animal: {0}", l).format(asm3.lostfound.get_found_person_name(dbo, linkid))

    elif linktypeid == WAITINGLIST:
        return asm3.i18n._("Waiting List: {0}", l).format(asm3.waitinglist.get_person_name(dbo, linkid))

def update_link_info(dbo, username, linktypeid, linkid):
    """
    Updates all diary notes of linktypeid/linkid
    """
    dbo.update("diary", f"LinkType={linktypeid} AND LinkID={linkid}", {
        "LinkInfo":     get_link_info(dbo, linktypeid, linkid)
    }, username)

def update_link_info_incomplete(dbo):
    """
    Updates the link info of all incomplete diary notes
    """
    rows = dbo.query("SELECT DISTINCT LinkType, LinkID FROM diary WHERE DateCompleted Is Null")
    asm3.asynctask.set_progress_max(dbo, len(rows))
    for d in rows:
        update_link_info(dbo, "system", d.LINKTYPE, d.LINKID)
        asm3.asynctask.increment_progress_value(dbo)
    asm3.al.info(f"updated {len(rows)} diary link info elements", "diary.update_link_info_incomplete", dbo)

def insert_diary_from_form(dbo, username, linktypeid, linkid, post):
    """
    Creates a diary note from the form data
    username: User creating the diary
    linktypeid, linkid: The link
    post: A PostedData object
    """
    l = dbo.locale
    if post["diarydate"] == "":
        raise asm3.utils.ASMValidationError(asm3.i18n._("Diary date cannot be blank", l))
    if post.date("diarydate") is None:
        raise asm3.utils.ASMValidationError(asm3.i18n._("Diary date is not valid", l))
    if post["subject"] == "":
        raise asm3.utils.ASMValidationError(asm3.i18n._("Diary subject cannot be blank", l))
    diarytime = post["diarytime"].strip()
    if diarytime != "":
        if diarytime.find(":") == -1:
            raise asm3.utils.ASMValidationError(asm3.i18n._("Invalid time, times should be in HH:MM format", l))
        if not asm3.utils.is_numeric(diarytime.replace(":", "")):
            raise asm3.utils.ASMValidationError(asm3.i18n._("Invalid time, times should be in HH:MM format", l))

    linkinfo = get_link_info(dbo, linktypeid, linkid)

    diaryid = dbo.insert("diary", {
        "LinkID":           linkid,
        "LinkType":         linktypeid,
        "LinkInfo":         linkinfo,
        "DiaryDateTime":    post.datetime("diarydate", "diarytime"),
        "DiaryForName":     post["diaryfor"],
        "Subject":          post["subject"],
        "Note":             post["note"],
        "Comments":         post["comments"],
        "DateCompleted":    post.date("completed")
    }, username)

    email_note_on_change(dbo, get_diary(dbo, diaryid), username)
    return diaryid

def insert_diary(dbo, username, linktypeid, linkid, diarydate, diaryfor, subject, note):
    """
    Creates a diary note from the form data
    username: User creating the diary
    linktypeid, linkid: The link
    diarydate: The date to stamp on the note (python format)
    diaryfor: Who the diary note is for
    subject, note
    """
    linkinfo = ""
    if linkid != 0:
        linkinfo = get_link_info(dbo, linktypeid, linkid)

    diaryid = dbo.insert("diary", {
        "LinkID":           linkid,
        "LinkType":         linktypeid,
        "LinkInfo":         linkinfo,
        "DiaryDateTime":    diarydate,
        "DiaryForName":     diaryfor,
        "Subject":          subject,
        "Note":             note
    }, username)

    email_note_on_change(dbo, get_diary(dbo, diaryid), username)
    return diaryid

def update_diary_from_form(dbo, username, post):
    """
    Updates a diary note from form data
    """
    l = dbo.locale
    if post["diarydate"] == "":
        raise asm3.utils.ASMValidationError(asm3.i18n._("Diary date cannot be blank", l))
    if post.date("diarydate") is None:
        raise asm3.utils.ASMValidationError(asm3.i18n._("Diary date is not valid", l))
    if post["subject"] == "":
        raise asm3.utils.ASMValidationError(asm3.i18n._("Diary subject cannot be blank", l))
    diarytime = post["diarytime"].strip()
    if diarytime != "":
        if diarytime.find(":") == -1:
            raise asm3.utils.ASMValidationError(asm3.i18n._("Invalid time, times should be in HH:MM format", l))
        if not asm3.utils.is_numeric(diarytime.replace(":", "")):
            raise asm3.utils.ASMValidationError(asm3.i18n._("Invalid time, times should be in HH:MM format", l))

    diaryid = post.integer("diaryid")
    dbo.update("diary", diaryid, {
        "DiaryDateTime":    post.datetime("diarydate", "diarytime"),
        "DiaryForName":     post["diaryfor"],
        "Subject":          post["subject"],
        "Note":             post["note"],
        "Comments":         post["comments"],
        "DateCompleted":    post.date("completed")
    }, username)

    if post.date("completed") is None:
        email_note_on_change(dbo, get_diary(dbo, diaryid), username)
    else:
        email_note_on_complete(dbo, get_diary(dbo, diaryid), username)

def execute_diary_task(dbo, username, tasktype, taskid, linkid, selecteddate):
    """
    Runs a diary task
    tasktype: ANIMAL or PERSON
    taskid: The ID of the diarytaskhead record to run
    linkid: The ID of the animal or person to run against
    selecteddate: If the task has any detail records with a pivot of 0, the date to supply (as python date)
    """
    def fix(s):
        return s.replace("<", "&lt;").replace(">", "&gt;")
    rollingdate = dbo.today()
    dtd = dbo.query("SELECT * FROM diarytaskdetail WHERE DiaryTaskHeadID = ? ORDER BY OrderIndex", [taskid])
    tags = {}
    linktype = ANIMAL
    if tasktype == "ANIMAL": 
        linktype = ANIMAL
        tags = asm3.wordprocessor.animal_tags(dbo, asm3.animal.get_animal(dbo, int(linkid)))
    elif tasktype == "PERSON": 
        linktype = PERSON
        tags = asm3.wordprocessor.person_tags(dbo, asm3.person.get_person(dbo, int(linkid)))
    for d in dtd:
        if d["DAYPIVOT"] == 9999: 
            rollingdate = selecteddate
        else:
            rollingdate = asm3.i18n.add_days(rollingdate, int(d["DAYPIVOT"]))
        insert_diary(dbo, username, linktype, int(linkid), rollingdate, \
            d["WHOFOR"], \
            asm3.wordprocessor.substitute_tags(fix(d["SUBJECT"]), tags, True), \
            asm3.wordprocessor.substitute_tags(fix(d["NOTE"]), tags, True))

def insert_diarytaskhead_from_form(dbo, username, post):
    """
    Creates a diary task header from form data
    """
    return dbo.insert("diarytaskhead", {
        "Name":             post["name"],
        "RecordType":       post.integer("type"),
        "RecordVersion":    0
    }, username, setCreated=False)

def update_diarytaskhead_from_form(dbo, username, post):
    """
    Updates a diary task header from form data
    """
    dbo.update("diarytaskhead", post.integer("diarytaskid"), {
        "Name":             post["name"],
        "RecordType":       post.integer("type")
    }, username, setLastChanged=False)

def delete_diarytask(dbo, username, taskid):
    """
    Deletes a diary task
    """
    dbo.delete("diarytaskdetail", "DiaryTaskHeadID=%d" % taskid, username)
    dbo.delete("diarytaskhead", taskid, username)

def insert_diarytaskdetail_from_form(dbo, username, post):
    """
    Creates a diary task detail from form data
    """
    return dbo.insert("diarytaskdetail", {
        "DiaryTaskHeadID":      post.integer("taskid"),
        "OrderIndex":           post.integer("orderindex"),
        "DayPivot":             post.integer("pivot"),
        "WhoFor":               post["for"],
        "Subject":              post["subject"],
        "Note":                 post["note"],
        "RecordVersion":        0
    }, username, setCreated=False)

def update_diarytaskdetail_from_form(dbo, username, post):
    """
    Updates a diary task detail from form data
    """
    dbo.update("diarytaskdetail", post.integer("diarytaskdetailid"), {
        "OrderIndex":           post.integer("orderindex"),
        "DayPivot":             post.integer("pivot"),
        "WhoFor":               post["for"],
        "Subject":              post["subject"],
        "Note":                 post["note"]
    }, username, setLastChanged=False)

def delete_diarytaskdetail(dbo, username, did):
    """
    Deletes a diary task detail record
    """
    dbo.delete("diarytaskdetail", did, username)


