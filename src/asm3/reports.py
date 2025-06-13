
import asm3.al
import asm3.animal
import asm3.cachedisk
import asm3.configuration
import asm3.dbms.base
import asm3.dbupdate
import asm3.i18n
import asm3.lookups
import asm3.html
import asm3.person
import asm3.template
import asm3.users
import asm3.utils
from asm3.sitedefs import BASE_URL, SERVICE_URL, URL_REPORTS
from asm3.typehints import Any, CriteriaParams, datetime, Database, List, MenuItems, PostedData, ReportParams, ResultRow, Results, Session, Tuple

HEADER = 0
FOOTER = 1

RECOMMENDED_REPORTS = [
    "Active Donors", "Active Fosters", "Active Members", "Adoptions by Date with Addresses",
    "Animal Entry Reasons", "Animal Return Reasons", "Animals Inducted by Date and Species",
    "Animals Without Photo Media", "Annual Figures (by species)", "Annual Figures (by type)",
    "Asilomar Figures (Live)", "Audit Trail: All Changes by Date", "Audit Trail: All Changes by Specific user",
    "Audit Trail: Deletions by Date", "Average Time On Shelter By Species", "Banned Owners",
    "Brought In Figures", "Cage Card", "Deceased Reasons by Species and Date",
    "Detailed Shelter Inventory", "In/Out", "In/Out by Species", "In/Out with Donations",
    "Intakes by Date with Outcomes", "Long Term Animals", "Medical Diary", 
    "Monthly Adoptions By Species", 
    "Monthly Figures (by species)", "Monthly Figures (by type)", "Most Common Name",
    "Non-Microchipped Animals", "Non-Neutered/Spayed Animals Aged Over 6 Months", "Non-Returned Adoptions",
    "Payment Breakdown By Date", "Print Animal Record", "Print Animal Record (for adopters)", "Print Person Record", 
    "Reserves without Homechecks", "Returned Animals", "shelteranimalscount.org matrix", 
    "Shelter Inventory", "Shelter Inventory with Pictures by Location", "Shelter Inventory at Date", 
    "Vaccination Diary (Off Shelter)", "Vaccination Diary (On Shelter)"
]

def get_all_report_titles(dbo: Database):
    """
    Returns a list of titles for every report on the system, does not
    include builtin reports since they don't count for ASM3 (and should be
    replaced when viewing available reports)
    """
    return dbo.query("SELECT ID, Title, Category, Revision FROM customreport WHERE SQLCommand NOT LIKE '0%' AND SQLCommand NOT LIKE '%$PARENT%' ORDER BY Title")

def get_available_reports(dbo: Database, include_with_criteria: bool = True) -> Results:
    """
    Returns a list of reports available for running. The return
    value is a tuple of category, ID and title.
    If include_with_criteria is false, only reports that don't
    have ASK or VAR tags are included.
    """
    reps = []
    rs = get_reports(dbo)
    for r in rs:
        htmlbody = r.HTMLBODY
        sql = r.SQLCOMMAND
        # Ignore ASM 2.x builtin reports
        if sql.startswith("0"):
            continue
        # Ignore mail merges
        if htmlbody.upper().startswith("MAIL"):
            continue
        # Ignore subreports
        if sql.find("$PARENTKEY$") != -1 or sql.find("$PARENTARG") != -1:
            continue
        # If we're excluding reports with criteria, check now
        if not include_with_criteria:
            if sql.find("$ASK") != -1 or sql.find("$VAR") != -1:
                continue
        reps.append(r)
    return reps

def get_available_mailmerges(dbo: Database) -> Results:
    """
    Returns a list of mail merges available for running. Return
    value is a tuple of category, ID and title.
    """
    reps = []
    rs = get_reports(dbo)
    for r in rs:
        if not r.HTMLBODY.startswith("MAIL"): continue
        reps.append(r)
    return reps

def get_reports(dbo: Database) -> Results:
    """
    Returns a list of all reports on the system, filtering out any of
    the old ASM2 built in reports
    """
    reps = dbo.query("SELECT * FROM customreport WHERE SQLCommand NOT LIKE '0%' ORDER BY Category, Title")
    roles = dbo.query("SELECT cr.*, r.RoleName FROM customreportrole cr INNER JOIN role r ON cr.RoleID = r.ID")
    for r in reps:
        viewroleids = []
        viewrolenames = []
        for o in roles:
            if o.REPORTID == r.ID and o.CANVIEW == 1:
                viewroleids.append(str(o.ROLEID))
                viewrolenames.append(str(o.ROLENAME))
        r.VIEWROLEIDS = "|".join(viewroleids)
        r.VIEWROLES = "|".join(viewrolenames)
    return reps

def get_raw_report_header(dbo: Database) -> str:
    header, body, footer = asm3.template.get_html_template(dbo, "report")
    if header.strip() == "": header = asm3.utils.read_text_file(dbo.installpath + "media/reports/head.html")
    return header

def get_raw_report_footer(dbo: Database) -> str:
    header, body, footer = asm3.template.get_html_template(dbo, "report")
    if footer.strip() == "": footer = asm3.utils.read_text_file(dbo.installpath + "media/reports/foot.html")
    return footer

def set_raw_report_headerfooter(dbo: Database, head: str, foot: str) -> None:
    asm3.template.update_html_template(dbo, "", "report", head, "", foot, True)

def get_report_header(dbo: Database, title: str, username: str) -> str:
    """
    Returns the stock report header
    """
    r = Report(dbo)
    r.title = title
    r.user = username
    return r._ReadHeader()

def get_report_footer(dbo: Database, title: str, username: str) -> str:
    """
    Returns the stock report footer
    """
    r = Report(dbo)
    r.title = title
    r.user = username
    return r._ReadFooter()

def get_categories(dbo: Database) -> List[str]:
    cat = dbo.query("SELECT DISTINCT Category FROM customreport ORDER BY Category")
    rv = []
    for c in cat:
        rv.append(c.CATEGORY)
    return rv

def get_title(dbo: Database, customreportid: int) -> str:
    """
    Returns the title of a custom report from its ID
    """
    return dbo.query_string("SELECT Title FROM customreport WHERE ID = ?", [customreportid])

def get_id(dbo: Database, title: str) -> int:
    """
    Returns the id of a custom report from its title. 0 if not found.
    """
    return dbo.query_int("SELECT ID FROM customreport WHERE Title LIKE ?", [title.strip()])

def is_mailmerge(dbo: Database, crid: int) -> bool:
    """
    Returns true if the report with crid is a mailmerge
    """
    return dbo.query_string("SELECT HTMLBody FROM customreport WHERE ID = ?", [crid]).startswith("MAIL")

def get_criteria(dbo: Database, customreportid: int) -> ReportParams:
    """
    Returns the criteria list for a report as a list of tuples containing name, type and question
    """
    return Report(dbo).GetParams(customreportid)

def get_criteria_params(dbo: Database, customreportid: int, post: PostedData) -> CriteriaParams:
    """
    Creates a list of criteria parameters to pass to a report. The post
    parameter contains the posted form data from a report criteria screen.
    These correspond to supporting values used in these locations:
        report_criteria.js, mobile_report.js, main.py/report_criteria, main.py/mobile_report_criteria
    """
    crit = Report(dbo).GetParams(customreportid)
    p = []
    l = dbo.locale
    for name, rtype, question in crit:
        if name not in post:
            raise asm3.utils.ASMValidationError("Missing parameter: %s" % name)
        if rtype == "DATE":
            p.append( ( name , question, dbo.sql_date(asm3.i18n.display2python(l, post[name]), includeTime=False, wrapParens=False), post[name]) )  
        elif rtype == "STRING":
            p.append( ( name, question, post[name], post[name] ) )
        elif rtype == "LOOKUP":
            question = question[0:question.find("|")]
            p.append( ( name, question, post[name], post[name] ) )
        elif rtype == "NUMBER":
            p.append( ( name, question, post[name], post[name] ) )
        elif rtype == "ANIMAL" or rtype == "FSANIMAL" or rtype == "ALLANIMAL":
            p.append( ( name, asm3.i18n._("Animal", l), post[name], asm3.animal.get_animal_namecode(dbo, post[name])) )
        elif rtype == "ANIMALS":
            animals = []
            for a in post[name].split(","):
                animals.append(asm3.animal.get_animal_namecode(dbo, a))
            p.append( ( name, asm3.i18n._("Animals", l), post[name], ", ".join(animals) ))
        elif rtype == "ANIMALFLAG":
            p.append( ( name, asm3.i18n._("Flag", l), post[name], post[name] ) )
        elif rtype == "DONATIONTYPE" or rtype == "PAYMENTTYPE":
            p.append( ( name, asm3.i18n._("Payment Type", l), post[name], asm3.lookups.get_donationtype_name(dbo, post.integer(name) )) )
        elif rtype == "ENTRYCATEGORY":
            p.append( ( name, asm3.i18n._("Entry Category", l), post[name], asm3.lookups.get_entryreason_name(dbo, post.integer(name) )) )
        elif rtype == "LITTER":
            p.append( ( name, asm3.i18n._("Litter", l), post[name], post[name]) )
        elif rtype == "LOCATION":
            p.append( ( name, asm3.i18n._("Location", l), post[name], asm3.lookups.get_internallocation_name(dbo, post.integer(name) )) )
        elif rtype == "LOGTYPE":
            p.append( ( name, asm3.i18n._("Log Type", l), post[name], asm3.lookups.get_logtype_name(dbo, post.integer(name) )) )
        elif rtype == "MEDIAFLAG":
            p.append( ( name, asm3.i18n._("Flag", l), post[name], post[name] ) )
        elif rtype == "PAYMENTMETHOD":
            p.append( ( name, asm3.i18n._("Payment Method", l), post[name], asm3.lookups.get_paymentmethod_name(dbo, post.integer(name) )) )
        elif rtype == "PERSON":
            p.append( ( name, asm3.i18n._("Person", l), post[name], asm3.person.get_person_name(dbo, post[name])) )
        elif rtype == "PERSONFLAG":
            p.append( ( name, asm3.i18n._("Flag", l), post[name], post[name] ) )
        elif rtype == "SITE":
            p.append( ( name, asm3.i18n._("Site", l), post[name], asm3.lookups.get_site_name(dbo, post.integer(name) )) )
        elif rtype == "SPECIES":
            p.append( ( name, asm3.i18n._("Species", l), post[name], asm3.lookups.get_species_name(dbo, post.integer(name) )) )
        elif rtype == "TYPE":
            p.append( ( name, asm3.i18n._("Type", l), post[name], asm3.lookups.get_animaltype_name(dbo, post.integer(name) )) )
    return p

def check_view_permission(session: Session, customreportid: int) -> bool:
    """
    Checks that the currently logged in user has permission to view the report with customreportid.
    If they can't, an ASMPermissionError is thrown.
    """
    l = session.locale
    dbo = session.dbo
    # Superusers can do anything
    if session.superuser == 1: return True
    reportroles = []
    for rr in dbo.query("SELECT RoleID FROM customreportrole WHERE ReportID = ? AND CanView = 1", [customreportid]):
        reportroles.append(rr.ROLEID)
    # No view roles means anyone can view
    if len(reportroles) == 0:
        return True
    # Does the user have any of the view roles?
    userroles = []
    for ur in dbo.query("SELECT RoleID FROM userrole INNER JOIN users ON userrole.UserID = users.ID WHERE users.UserName LIKE ?", [session.user]):
        userroles.append(ur.ROLEID)
    hasperm = False
    for ur in userroles:
        if ur in reportroles:
            hasperm = True
    if hasperm:
        return True
    raise asm3.utils.ASMPermissionError(asm3.i18n._("No view permission for this report", l))

def insert_report_from_form(dbo: Database, username: str, post: PostedData) -> int:
    """
    Creates a report record from posted form data
    """
    rtype = post["type"]
    if rtype != "REPORT" and rtype != "":
        htmlbody = rtype
    else:
        htmlbody = post["html"]

    reportid = dbo.insert("customreport", {
        "Title":                post["title"],
        "Category":             post["category"],
        "*SQLCommand":          post["sql"],
        "*HTMLBody":            htmlbody,
        "DailyEmail":           post["dailyemail"],
        "DailyEmailHour":       post.integer("dailyemailhour"),
        "DailyEmailFrequency":  post.integer("dailyemailfrequency"),
        "Description":          post["description"],
        "OmitHeaderFooter":     post.boolean("omitheaderfooter"),
        "OmitCriteria":         post.boolean("omitcriteria"),
        "Revision":             post.integer("revision")
    }, username, setRecordVersion=False)

    dbo.delete("customreportrole", "ReportID=%d" % reportid)
    for rid in post.integer_list("viewroles"):
        dbo.insert("customreportrole", { "ReportID": reportid, "RoleID": rid, "CanView": 1 }, generateID=False, setCreated=False)
    return reportid

def update_report_from_form(dbo: Database, username: str, post: PostedData) -> None:
    """
    Updates a report record from posted form data
    """
    reportid = post.integer("reportid")
    prev = dbo.first_row(dbo.query("SELECT Title, Category FROM customreport WHERE ID=?", [reportid]))
    values = {
        "Title":                post["title"],
        "Category":             post["category"],
        "*SQLCommand":          post["sql"],
        "*HTMLBody":            post["html"],
        "DailyEmail":           post["dailyemail"],
        "DailyEmailHour":       post.integer("dailyemailhour"),
        "DailyEmailFrequency":  post.integer("dailyemailfrequency"),
        "Description":          post["description"],
        "OmitHeaderFooter":     post.boolean("omitheaderfooter"),
        "OmitCriteria":         post.boolean("omitcriteria")
    }
    # If the name or category was changed, clear any revision number
    if prev is not None and (prev.TITLE != post["title"] or prev.CATEGORY != post["category"]): values["Revision"] = 0
    dbo.update("customreport", reportid, values, username, setRecordVersion=False)

    update_report_viewroles_from_form(dbo, [reportid], post.integer_list("viewroles"))

def update_report_viewroles_from_form(dbo: Database, reportids: List[int], roleids: List[int]) -> None:
    """ 
    Updates the view roles to roleids for the reports given 
    """
    for reportid in reportids:
        dbo.delete("customreportrole", f"ReportID={reportid}")
        for roleid in roleids:
            dbo.insert("customreportrole", { "ReportID": reportid, "RoleID": roleid, "CanView": 1 }, generateID=False, setCreated=False)

def delete_report(dbo: Database, username: str, rid: int) -> None:
    """
    Deletes a report record
    """
    dbo.delete("customreportrole", "ReportID=%d" % rid)
    dbo.delete("customreport", rid, username)

def check_sql(dbo: Database, username: str, sql: str) -> str:
    """
    Verifies that report sql works correctly. Returns the SELECT query,
    sanitised and in a ready-to-run state.
    If there is a problem with the query, an ASMValidationError is raised
    """
    COMMON_DATE_TOKENS = ( "CURRENT_DATE", "@from", "@to", "@osfrom", "@osto", "@osatdate", "@thedate", "@dt" )
    # Clean up and substitute some tags
    sql = sql.replace("$USER$", username)
    # Subtitute CONST tokens
    for name, value in asm3.utils.regex_multi(r"\$CONST (.+?)\=(.+?)\$", sql):
        sql = sql.replace("$%s$" % name, value) # replace all tokens with the constant value
        sql = sql.replace("$CONST %s=%s$" % (name, value), "") # remove the constant declaration
    i = sql.find("$")
    while (i != -1):
        end = sql.find("$", i+1)
        if end == -1:
            raise asm3.utils.ASMValidationError("Unclosed $ token found")
        token = sql[i+1:end]
        sub = ""
        if token.startswith("VAR"):
            # VAR tags don't need a substitution
            sub = ""
        elif token == "@year":
            sub = "2001"
        elif token.startswith("ASK DATE") or token.startswith("CURRENT_DATE") or token in COMMON_DATE_TOKENS:
            sub = "2001-01-01"
        elif token.startswith("SQL AGE"):
            sub = "''"
        elif token.startswith("SQL CONCAT"):
            sub = "''"
        elif token.startswith("SQL ILIKE"):
            sub = "0=0"
        elif token.startswith("SQL INTERVAL"):
            sub = "'2001-01-01'"
        elif token.startswith("SQL DATEDIFF"):
            sub = "0"
        elif token.startswith("SQL DATETOCHAR"):
            sub = "'2001-01-01'"
        elif token.startswith("SQL HOUR"):
            sub = "1"
        elif token.startswith("SQL MINUTE"):
            sub = "1"
        elif token.startswith("SQL DAY"):
            sub = "1"
        elif token.startswith("SQL MONTH"):
            sub = "1"
        elif token.startswith("SQL YEAR"):
            sub = "2001"
        elif token.startswith("SQL WEEKDAY"):
            sub = "Monday"
        elif token == "":
            # an empty token means $$ was used, it can be used to quote strings in Postgres - leave it alone
            i = sql.find("$", end+1)
            continue
        else:
            sub = "0"
        sql = sql[0:i] + sub + sql[end+1:]
        i = sql.find("$", i+1)
    # Make sure the query is a valid one
    if not is_valid_query(sql):
        raise asm3.utils.ASMValidationError("Reports must be based on a SELECT query.")
    # Test the query
    try:
        dbo.query_tuple(sql)
    except Exception as e:
        raise asm3.utils.ASMValidationError(str(e))
    return sql

def is_valid_query(sql: str) -> bool:
    """
    Returns true if this is a valid report query.
    """
    sql = strip_sql_comments(sql)
    return sql.lower().strip().startswith("select") or sql.lower().strip().startswith("with")

def strip_sql_comments(sql: str) -> str:
    """
    Removes any single line SQL comments that start with --
    """
    lines = []
    for x in sql.split("\n"):
        if not x.strip().startswith("--"):
            lines.append(x)
    return "\n".join(lines)

def generate_html(dbo: Database, username: str, sql: str) -> str:
    """
    Runs the query given and returns some auto-generated HTML to
    output the data in a table.
    """
    sql = check_sql(dbo, username, sql)
    rs, cols = dbo.query_tuple_columns(sql)
    h = "$$HEADER\n" 
    th = "<table border=\"1\">\n<thead>\n<tr>\n"
    b = "$$BODY\n<tr>\n"
    f = "$$FOOTER\n"
    for c in cols:
        th += "<th>%s</th>\n" % c
        b += "<td>$%s</td>\n" % c.upper()
    th += "</thead>\n<tbody>\n"
    g = ""
    if sql.find("-- GRP:") != -1:
        gstart = sql.find("-- GRP:") + 7
        gl = sql[gstart:sql.find("\n", gstart)].split(",")
        for i, gn in enumerate(gl):
            g += f"$$GROUP_{gn}\n$$HEAD\n<h3>${gn}</h3>\n"
            if i == len(gl)-1:
                g += th
            g += "$$FOOT\n"
            if i == len(gl)-1:
                g += "</table>\n"
            g += "<h3>Total $%s: {COUNT.%s}</h3>\nGROUP$$\n\n" % (gn, gn)
    else:
        h += th
        f += "</table>\n"
    if len(cols) > 0:
        f += "<h2>Total: {COUNT.%s}</h2>\n" % cols[0].upper()
    h += "HEADER$$\n\n"
    b += "</tr>\nBODY$$\n\n"
    f += "FOOTER$$\n"
    return h + g + b + f

def get_smcom_reports_installable(dbo: Database) -> Results:
    """
    Returns the collection of sheltermanager.com reports available to install
    as a list of dictionaries. Reports not suitable for this database
    type/version are automatically filtered out.
    [ { TITLE, CATEGORY, DATABASE, DESCRIPTION, LOCALE, SQL, HTML, SUBREPORTS } ]
    """
    reports = get_smcom_reports(dbo)
    return [ x for x in reports if x.INSTALLABLE ]

def get_smcom_reports_update(dbo: Database) -> Results:
    """
    Returns the collection of sheltermanager.com reports that require an update
    as a list of dictionaries. 
    [ { TITLE, CATEGORY, DATABASE, DESCRIPTION, LOCALE, SQL, HTML, SUBREPORTS } ]
    """
    reports = get_smcom_reports(dbo)
    return [ x for x in reports if x.UPDATE ]

def get_smcom_reports_txt(dbo: Database) -> str:
    """
    Retrieves the reports.txt file with standard report definitions from sheltermanager.com
    """
    try:
        REPORTS_CACHE_TTL = 86400
        s = asm3.cachedisk.get("reports", "reports")
        if s is None:
            s = asm3.utils.get_url(URL_REPORTS)["response"]
            if not URL_REPORTS.startswith("file:"):
                asm3.cachedisk.put("reports", "reports", s, REPORTS_CACHE_TTL)
        asm3.al.debug("read reports.txt (%s bytes)" % len(s), "reports.get_smcom_reports_txt", dbo)
        return s
    except Exception as err:
        asm3.al.error("Failed reading reports_txt: %s" % err, "reports.get_smcom_reports_txt", dbo)

def get_smcom_reports(dbo: Database) -> Results:
    """
    Returns the full collection of sheltermanager.com reports
    as a list of dictionaries. 
    DATABASE string format is "VERSION/DBNAME [omitheader] [omitcriteria] [rev00]"
    INSTALLABLE will be True if the report can be installed in this database.
    INSTALLED will be True if the report is already installed in this database.
    UPDATE will be True if the report is already installed in this database and is older than the last revision.
        (NB: the category as well as title has to match, so people can protect their copies by changing category)
    [ { TITLE, CATEGORY, DATABASE, DESCRIPTION, LOCALE, SQL, HTML, SUBREPORTS, INSTALLABLE, INSTALLED, REVISION, UPDATE} ]
    """
    l = dbo.locale
    s = get_smcom_reports_txt(dbo)
    reps = s.split("&&&")
    reports = []
    loaded = get_all_report_titles(dbo)
    latest_db_version = asm3.dbupdate._dbupdates_latest_ver(dbo)
    def version_ok(rdb):
        if rdb.find("/") == -1: return True
        ver = asm3.utils.cint(rdb[0:rdb.find("/")])
        return latest_db_version >= ver
    def database_ok(rdb):
        if rdb.find("ASM2") != -1: return False
        if rdb.find("Any") != -1: return True
        if rdb.find("MySQL") != -1 and dbo.dbtype == "MYSQL": return True
        if rdb.find("PostgreSQL") != -1 and dbo.dbtype == "POSTGRESQL": return True
        if rdb.find("DB2") != -1 and dbo.dbtype == "DB2": return True
        if rdb.find("SQLite") != -1 and dbo.dbtype == "SQLITE": return True
        return False
    def builtin(s):
        return s.startswith("0")
    def installed(title):
        for lrec in loaded:
            if lrec.TITLE == title: return True
        return False
    def customreportid(title):
        for lrec in loaded:
            if lrec.TITLE == title: return lrec.ID
        return 0
    def update(title, category, rev):
        if rev == "": return False
        for lrec in loaded:
            if lrec.TITLE == title and lrec.CATEGORY == category and lrec.REVISION != rev: return True
        return False
    for i, rp in enumerate(reps):
        b = rp.split("###")
        if len(b) < 7: continue # Malformed if we have less than 7 elements
        d = asm3.dbms.base.ResultRow()
        d.TITLE = b[0].strip()
        d.CATEGORY = b[1].strip()
        d.DATABASE = b[2].strip()
        d.DESCRIPTION = b[3].strip()
        d.LOCALE = b[4].strip()
        d.SQL = b[5].strip()
        d.HTML = b[6].strip()
        d.ID = i+1
        d.TYPE = asm3.i18n._("Report", l)
        if d.HTML.startswith("GRAPH"): d.TYPE = asm3.i18n._("Chart", l)
        if d.HTML.startswith("MAIL"): d.TYPE = asm3.i18n._("Mail Merge", l)
        if d.HTML.startswith("MAP"): d.TYPE = asm3.i18n._("Map", l)
        d.SUBREPORTS = ""
        if len(b) == 8: 
            d.SUBREPORTS = b[7].strip()
        d.INSTALLABLE = not builtin(d.SQL) and database_ok(d.DATABASE) and version_ok(d.DATABASE)
        d.INSTALLED = installed(d.TITLE)
        d.CUSTOMREPORTID = customreportid(d.TITLE)
        d.REVISION = 0
        revp = d.DATABASE.find("rev")
        if revp != -1:
            d.REVISION = asm3.utils.cint(d.DATABASE[revp+3:revp+5])
        d.UPDATE = update(d.TITLE, d.CATEGORY, d.REVISION) and database_ok(d.DATABASE) \
            and version_ok(d.DATABASE) and not builtin(d.SQL)
        reports.append(d)
    return reports

def install_smcom_report(dbo: Database, user: str, r: ResultRow) -> None:
    """
    Installs the sheltermanager.com report r (an item from get_smcom_reports).
    If a report with the same title exists in the database already, deletes it first.
    """
    xid = get_id(dbo, r.TITLE)
    if xid > 0: dbo.delete("customreport", xid, user)
    data = {"title" : r.TITLE, 
        "category" : r.CATEGORY, 
        "sql" : r.SQL,
        "html": r.HTML, 
        "description" : r.DESCRIPTION,
        "revision": r.REVISION, 
        "omitheaderfooter" : r.DATABASE.find("omitheader") != -1 and "on" or "",
        "omitcriteria" : r.DATABASE.find("omitcriteria") != -1 and "on" or ""}
    insert_report_from_form(dbo, user, asm3.utils.PostedData(data, dbo.locale))
    install_smcom_subreports(dbo, user, r)

def install_smcom_reports(dbo: Database, user: str, ids: Results) -> None :
    """
    Installs the sheltermanager.com reports with the ids given
    ids: List of report id numbers
    """
    reports = get_smcom_reports(dbo)
    for r in reports:
        if r.ID in ids: 
            install_smcom_report(dbo, user, r)

def install_smcom_subreports(dbo: Database, user: str, r: ResultRow):
    """
    Installs the subreports from smcom report r
    """
    if r.SUBREPORTS != "":
        b = r.SUBREPORTS.split("+++")
        while len(b) >= 3:
            dbo.delete("customreport", "Title LIKE '%s'" % b[0].strip().replace("'", "`"))
            data = { "title": b[0].strip(),
                "category": r.CATEGORY,
                "description": r.DESCRIPTION,
                "revision": r.REVISION,
                "sql": b[1],
                "html": b[2] }
            insert_report_from_form(dbo, user, asm3.utils.PostedData(data, dbo.locale))
            # Reduce the list by the 3 elements we just saw
            if len(b) > 3:
                b = b[3:]
            else:
                break

def install_recommended_smcom_reports(dbo: Database, user: str) -> None:
    """
    Installs the recommended set of reports from sheltermanger.com
    This is usually called on login if there aren't any reports in the system currently.
    """
    reports = get_smcom_reports(dbo)
    for r in reports:
        if r.TITLE in RECOMMENDED_REPORTS: 
            install_smcom_report(dbo, user, r)

def install_smcom_report_file(dbo: Database, user: str, filename: str) -> None:
    """
    Installs all the reports in an smcom report .txt file.
    If that report is already installed, it will be deleted and reinstalled instead.
    Deliberately does no database or version checks.
    This is a development tool and it can be called via cron.py
    """
    l = dbo.locale
    s = asm3.utils.read_text_file(filename)
    reps = s.split("&&&")
    for rp in reps:
        b = rp.split("###")
        d = asm3.dbms.base.ResultRow()
        d.TITLE = b[0].strip()
        d.CATEGORY = b[1].strip()
        d.DATABASE = b[2].strip()
        d.DESCRIPTION = b[3].strip()
        d.LOCALE = b[4].strip()
        d.SQL = b[5].strip()
        d.HTML = b[6].strip()
        d.TYPE = asm3.i18n._("Report", l)
        if d.HTML.startswith("GRAPH"): d.TYPE = asm3.i18n._("Chart", l)
        if d.HTML.startswith("MAIL"): d.TYPE = asm3.i18n._("Mail Merge", l)
        if d.HTML.startswith("MAP"): d.TYPE = asm3.i18n._("Map", l)
        d.SUBREPORTS = ""
        if len(b) == 8: 
            d.SUBREPORTS = b[7].strip()
        d.REVISION = 0
        revp = d.DATABASE.find("rev")
        if revp != -1:
            d.REVISION = asm3.utils.cint(d.DATABASE[revp+3:revp+5])
        install_smcom_report(dbo, user, d)

def update_smcom_reports(dbo: Database, user: str = "system") -> int:
    """
    Finds all reports with available updates and updates them.
    Note that only the SQL, HTML and Revision are updated.
    Any subreports are reinstalled.
    """
    reports = get_smcom_reports(dbo)
    updated = 0
    for r in reports:
        if r.UPDATE:
            dbo.update("customreport", r.CUSTOMREPORTID, {
                "*SQLCommand":  r.SQL,
                "*HTMLBody":    r.HTML,
                "Revision":     r.REVISION
            }, user, setRecordVersion=False)
            install_smcom_subreports(dbo, user, r)
            updated += 1
    asm3.al.info(f"updated {updated} reports.", "reports.update_smcom_reports", dbo)
    return updated

def get_reports_menu(dbo: Database, roleids: str = "", superuser: bool = False) -> MenuItems:
    """
    Reads the list of reports and returns them as a list for inserting into
    our menu structure. 
    The return value is a list of reports with a tuple containing URL and
    name. Categories are also output.
    roleids: comma separated list of roleids for the current user
    superuser: true if the user is a superuser
    """
    rv = []
    rep = get_available_reports(dbo)
    lastcat = ""
    for r in rep:
        if superuser or r.VIEWROLEIDS == "" or asm3.utils.list_overlap(r.VIEWROLEIDS.split("|"), roleids.split("|")):
            if r.CATEGORY != lastcat:
                lastcat = r.CATEGORY
                rv.append( ("", "", "", "--cat", "", lastcat) )
            rv.append( ( asm3.users.VIEW_REPORT, "", "", "report?id=%d" % r.ID, "", r.TITLE ) )
    return rv

def get_mailmerges_menu(dbo: Database, roleids: str = "", superuser: bool = False) -> MenuItems:
    """
    Reads the list of mail merges and returns them s a list for inserting into
    our menu structure.
    The return value is a list of merge reports with a tuple containing URL and
    name. Categories are also output.
    roleids: comma separated list of roleids for the current user
    superuser: true if the user is a superuser
    """
    mv = []
    mm = get_available_mailmerges(dbo)
    lastcat = ""
    for m in mm:
        if m.CATEGORY != lastcat:
            lastcat = m.CATEGORY
            mv.append( ("", "", "", "--cat", "", lastcat) )
        if superuser or m.VIEWROLEIDS == "" or asm3.utils.list_overlap(m.VIEWROLEIDS.split("|"), roleids.split("|")):
            mv.append( ( asm3.users.MAIL_MERGE, "", "", "mailmerge?id=%d" % m.ID, "", m.TITLE ) )
    return mv

def email_daily_reports(dbo: Database, now: datetime = None) -> None:
    """
    Finds all reports that have addresses set in DailyEmail 
    and no criteria. It will execute each of those reports in 
    turn and email them to the addresses set.
    It also takes into account the hour of the day set if any and 
    a frequency, so instead of emailing every day, it can be set to
    a particular weekday or the first/last of the month/year.
    now: The time right now in local time. If now is None, then we run anything
         with a dailyemailhour of -1, which is "batch".
    """
    rs = get_available_reports(dbo, False)
    hour = -1
    weekday = -1
    day = -1
    month = -1
    lastdayofmonth = -1
    if now is not None:
        hour = now.hour
        weekday = now.weekday()
        day = now.day
        month = now.month
        lastdayofmonth = asm3.i18n.last_of_month(now).day
    for r in rs:
        emails = asm3.utils.nulltostr(r.DAILYEMAIL)
        runhour = r.DAILYEMAILHOUR
        freq = r.DAILYEMAILFREQUENCY
        if emails == "": continue # No emails to send to, don't do anything
        if now is None and runhour != -1: continue # We're running for the batch, but an hour is set on the report
        if now is not None and hour != runhour: continue # It's not the right hour to send
        if freq == 1 and weekday != 0: continue # Freq is Mon and that's not today
        if freq == 2 and weekday != 1: continue # Freq is Tue and that's not today
        if freq == 3 and weekday != 2: continue # Freq is Wed and that's not today
        if freq == 4 and weekday != 3: continue # Freq is Thu and that's not today
        if freq == 5 and weekday != 4: continue # Freq is Fri and that's not today
        if freq == 6 and weekday != 5: continue # Freq is Sat and that's not today
        if freq == 7 and weekday != 6: continue # Freq is Sun and that's not today
        if freq == 8 and day != 1: continue # Freq is beginning of month and it's not the 1st
        if freq == 9 and day != lastdayofmonth: continue # Freq is end of month and it's not the last day of the month
        if freq == 10 and day != 1 and month != 1: continue # Freq is beginning of year and its not 1st Jan
        if freq == 11 and day != 31 and month != 12: continue # Freq is end of year and its not 31st Dec
        # If we get here, we're good to send
        asm3.al.debug("executing scheduled report '%s' (hour=%s, freq=%s)" % (r.TITLE, r.DAILYEMAILHOUR, r.DAILYEMAILFREQUENCY), "reports.email_daily_reports", dbo)
        body = execute(dbo, r.ID, "dailyemail")
        # If we aren't sending empty reports and there's no data, bail
        if body.find("NODATA") != -1 and not asm3.configuration.email_empty_reports(dbo): 
            asm3.al.debug("report '%s' contained no data and option is on to skip sending empty reports" % (r.TITLE), "reports.email_daily_reports", dbo)
            continue
        asm3.utils.send_email(dbo, "", emails, "", "", r.TITLE, body, "html", exceptions=False, retries=3)

def execute_title(dbo: Database, title: str, username: str = "system", params: ReportParams = None, toolbar: bool = True) -> str:
    """
    Executes a custom report by a match on its title. 'params' is a list of tuples.
    username is the name of the user running the report.
    if toolbar is True and it's a report we're running, the toolbar will be injected
    into the report document.
    See the Report._SubstituteSQLParameters function for more info.
    Return value is a string containing the report as an HTML document.
    """
    crid = get_id(dbo, title)
    if crid == 0:
        return "<html><body><h1>404 Not Found</h1><p>The report '%s' does not exist.</p></body></html>" % title
    else:
        return execute(dbo, crid, username, params, toolbar)

def execute(dbo: Database, customreportid: int, username: str = "system", params: CriteriaParams = None, toolbar: bool = True) -> str:
    """
    Executes a custom report by its ID. 'params' is a list of tuples of parameters. 
    username is the name of the user running the report. 
    See the Report._SubstituteSQLParameters function for more info. 
    if toolbar is True and it's a report we're running, the toolbar will be injected
    into the report document.
    Return value is a string containing the report as an
    HTML document.
    """
    r = Report(dbo)
    r.toolbar = toolbar
    return r.Execute(customreportid, username, params)

def execute_query(dbo: Database, customreportid: int, username: str = "system", params: CriteriaParams = None) -> Tuple[Results, List[str]]:
    """
    Executes a custom report query by its ID. 'params' is a tuple of 
    parameters. username is the name of the user running the 
    report. See the Report._SubstituteSQLParameters function for
    more info. Return value is the list of rows from the query and
    a list of columns.
    """
    r = Report(dbo)
    return r.ExecuteQuery(customreportid, username, params)

def execute_sql(dbo: Database, title: str, sql: str, html: str, headerfooter: bool = True, username: str = "system") -> str:
    """
    Executes a sql/html combo as if it were a custom report.
    title: The report title
    sql: The report sql
    html: The report html
    headerfooter: Whether or not to include report HTML header/footer
    return value is the report HTML as a string
    """
    r = Report(dbo)
    r.title = title
    r.sql = sql
    r.html = html
    r.user = username
    r.omitCriteria = True
    r.omitHeaderFooter = headerfooter
    return r.Execute(0, username)

class GroupDescriptor:
    """
    Contains info on report groups
    """
    fieldName = ""
    lastFieldValue = ""
    header = ""
    footer = ""
    forceFinish = False
    lastGroupStartPosition = 0
    lastGroupEndPosition = 0

class Report:
    dbo = None
    user = ""
    reportId = 0
    criteria = ""
    queries = []
    params = []
    title = ""
    category = ""
    sql = ""
    html = ""
    omitCriteria = False
    omitHeaderFooter = False
    isSubReport = False
    toolbar = False
    output = ""
    
    def __init__(self, dbo: Database):
        self.dbo = dbo

    def _ReadReport(self, reportId: int) -> bool:
        """
        Reads the report info from the database and populates
        our local class variables.
        Returns True on success.
        """
        rs = self.dbo.query("SELECT Title, Category, HTMLBody, SQLCommand, OmitCriteria, " \
            "OmitHeaderFooter FROM customreport WHERE ID = ?", [reportId])
        
        # Can't do anything if the ID was invalid
        if len(rs) == 0: return False

        r = rs[0]
        self.title = r.TITLE
        self.category = r.CATEGORY
        self.html = r.HTMLBODY
        self.sql = r.SQLCOMMAND
        self.omitCriteria = r.OMITCRITERIA > 0
        self.omitHeaderFooter = r.OMITHEADERFOOTER > 0
        self.isSubReport = self.sql.find("PARENTKEY") != -1 or self.sql.find("PARENTARG") != -1
        return True

    def _ReadHeader(self) -> str:
        """
        Reads the report header from the DB. If the omitHeaderFooter
        flag is set, returns a basic header, if it's a subreport,
        returns nothing.
        """
        if self.omitHeaderFooter:
            return "<!DOCTYPE html>\n" \
                "<html>\n" \
                "<head>\n" \
                "<meta charset=\"utf-8\">\n" \
                "<title></title>\n" \
                "</head>\n" \
                "<body>\n"
        elif self.isSubReport:
            return ""
        else:
            # Look it up from the DB
            s = get_raw_report_header(self.dbo)
            s = self._SubstituteTemplateHeaderFooter(s)
            return s

    def _ReadFooter(self) -> str:
        """
        Reads the report footer from the DB. If the omitHeaderFooter
        flag is set, returns a basic footer, if it's a subreport,
        returns nothing.
        """
        if self.omitHeaderFooter:
            return "</body></html>"
        elif self.isSubReport:
            return ""
        else:
            # Look it up from the DB
            s = get_raw_report_footer(self.dbo)
            s = self._SubstituteTemplateHeaderFooter(s)
            return s

    def _Append(self, s: str) -> str:
        self.output += str(s)
        return self.output

    def _p(self, s: str) -> str:
        self._Append("<p>%s</p>" % s)

    def _hr(self) -> str:
        self._Append("<hr />")

    def _ReplaceFields(self, s: str, k: str, v: str) -> str:
        """
        Replaces field tokens in HTML for real fields. 
        Escapes curly braces and dollars for HTML entities as they can blow 
        up the parser after substitution.
        s is the html string, k is the fieldname, v is the value
        """
        # Characters that denote a field token has ended
        validend = (" ", "\n", "\r", ",", "<", ">", "&" , "[", "]", "{", "}", ".", "$", "*", ":", ";", "!", "%", "^", "(", ")", "@", "~", "/", "\\", "'", "\"", "|")
        lc = s.lower()
        tok = lc.find("$")
        while tok != -1:
            aftertok = lc[tok+1+len(k):tok+1+len(k)+1]
            if lc[tok+1:tok+1+len(k)] == k.lower() and aftertok in validend:
                foundtok = s[tok+1:tok+1+len(k)]
                v = v.replace("{", "&#123;").replace("}", "&#125;")
                v = v.replace("$", "&#36;")
                s = s.replace("$" + foundtok + aftertok, v + aftertok)
                lc = s.lower()
            tok = lc.find("$", tok+1) 
        return s
        
    def _DisplayValue(self, k: str, v: Any) -> str:
        """
        Returns the display version of any value
        k: fieldname
        v: value
        """
        l = self.dbo.locale
        if v is None: return ""

        if asm3.utils.is_date(v):
            return asm3.i18n.python2displaytime(l, v)

        if asm3.utils.is_currency(k):
            return asm3.i18n.format_currency(l, v)

        if k.upper().endswith("N2BR"):
            return str(v).replace("\n", "<br>")

        return str(v)
    
    def _OutputGroupBlock(self, gd: GroupDescriptor, headfoot: int, rs: Results) -> str:
        """
        Outputs a group block, 'gd' is the group descriptor,
        'headfoot' is 0 for header, 1 for footer, 'rs' is
        the resultset and 'rowindex' is the row of results being
        looked at
        """
        out = gd.footer
        if headfoot == 0:
            out = gd.header

        # If there aren't any records in the set, then we might as
        # well stop now
        if len(rs) == 0:
            self._Append(out)
            return

        # Replace any fields in the block based on the last row
        # in the group
        for k, v in rs[gd.lastGroupEndPosition].items():
            out = self._ReplaceFields(out, k, self._DisplayValue(k, v))

        # Replace any of our special header/footer tokens
        out = self._SubstituteTemplateHeaderFooter(out)

        # Find calculation keys in our block
        startkey = out.find("{")
        while startkey != -1:

            endkey = out.find("}", startkey)
            if endkey == -1: endkey = len(out)-1
            key = out[startkey + 1:endkey]
            value = ""
            valid = False

            # {SUM.field[.round]}
            if key.lower().startswith("sum."):
                valid = True
                fields = key.lower().split(".")
                calcfield = fields[1].upper()
                
                # rounding
                roundto = 2
                if len(fields) > 2:
                    roundto = abs(asm3.utils.cint(fields[2]))

                total = 0.0
                for i in range(gd.lastGroupStartPosition, gd.lastGroupEndPosition + 1):
                    if calcfield in rs[i]:
                        total += asm3.utils.cfloat(rs[i][calcfield])

                if asm3.utils.is_currency(fields[1]):
                    value = asm3.i18n.format_currency(self.dbo.locale, asm3.utils.cint(total))
                else:
                    fmt = "%%0.%sf" % roundto
                    value = fmt % total

            # {COUNT.field[.distinct]}
            if key.lower().startswith("count."):
                valid = True
                fields = key.lower().split(".")
                countfield = fields[1].upper()
                if len(fields) > 2 and fields[2].lower() == "distinct":
                    # distinct set, return the number of unique values of field in the group
                    countitems = []
                    for i in range(gd.lastGroupStartPosition, gd.lastGroupEndPosition + 1):
                        countitems.append(rs[i][countfield])
                    value = str(len(set(countitems)))
                else:
                    # no distinct flag, just return how many records there are in the group
                    value = str(gd.lastGroupEndPosition - gd.lastGroupStartPosition + 1)

            # {AVG.field[.round]}
            if key.lower().startswith("avg."):
                valid = True
                fields = key.lower().split(".")
                calcfield = fields[1].upper()
               
                # rounding
                roundto = 2
                if len(fields) > 2:
                    roundto = abs(asm3.utils.cint(fields[2]))

                total = 0.0
                num = 0
                for i in range(gd.lastGroupStartPosition, gd.lastGroupEndPosition + 1):
                    fv = 0
                    if calcfield in rs[i]:
                        fv = asm3.utils.cfloat(rs[i][calcfield])
                        if asm3.utils.is_currency(fields[1]):
                            fv /= 100
                        total += fv
                        num += 1
                fstr = "%0." + str(roundto) + "f"
                value = fstr % (0)
                if num > 0:
                    value = fstr % (total / num)

            # {PCT.field.match[.round]}
            if key.lower().startswith("pct."):
                valid = True
                fields = key.lower().split(".")
                calcfield = fields[1].upper()
                calcfield2 = fields[2].upper()
                
                # rounding
                roundto = 2
                if len(fields) > 3:
                    roundto = abs(asm3.utils.cint(fields[3]))

                matched = 0
                for i in range(gd.lastGroupStartPosition, gd.lastGroupEndPosition + 1):
                    try:
                        if str(rs[i][calcfield]).strip().lower() == str(calcfield2).strip().lower():
                            matched += 1
                    except:
                        # Ignore errors
                        pass

                outof = gd.lastGroupEndPosition - gd.lastGroupStartPosition + 1
                fstr = "%0." + str(roundto) + "f"
                value = fstr % ((matched / outof) * 100)

            # {PCTG.field[.round]}
            if key.lower().startswith("pctg."):
                valid = True
                fields = key.lower().split(".")
                calcfield = fields[1].upper()
                
                # rounding
                roundto = 2
                if len(fields) > 2:
                    roundto = abs(asm3.utils.cint(fields[2]))

                matched = gd.lastGroupEndPosition - gd.lastGroupStartPosition + 1
                outof = len(rs)
                fstr = "%0." + str(roundto) + "f"
                value = fstr % ((matched / outof) * 100)

            # {MIN.field}
            if key.lower().startswith("min."):
                valid = True
                fields = key.lower().split(".")
                calcfield = fields[1].upper()
               
                HIGH_MINVAL = 9999999
                minval = HIGH_MINVAL
                for i in range(gd.lastGroupStartPosition, gd.lastGroupEndPosition + 1):
                    try:
                        minval = min(minval, rs[i][calcfield])
                    except:
                        # Ignore errors
                        pass
                if minval == HIGH_MINVAL: minval = 0
                if asm3.utils.is_currency(fields[1]):
                    value = str(minval / 100.0)
                else:
                    value = str(minval)

            # {MAX.field}
            if key.lower().startswith("max."):
                valid = True
                fields = key.lower().split(".")
                calcfield = fields[1].upper()
               
                maxval = 0
                for i in range(gd.lastGroupStartPosition, gd.lastGroupEndPosition + 1):
                    try:
                        maxval = max(maxval, rs[i][calcfield])
                    except:
                        # Ignore errors
                        pass
                if asm3.utils.is_currency(fields[1]):
                    value = str(maxval / 100.0)
                else:
                    value = str(maxval)

            # {FIRST.field}
            if key.lower().startswith("first."):
                valid = True
                fields = key.lower().split(".")
                calcfield = fields[1].upper()
                value = str(rs[gd.lastGroupStartPosition][calcfield])
                if asm3.utils.is_currency(calcfield):
                    value = str(asm3.utils.cfloat(value) / 100)

            # {LAST.field}
            if key.lower().startswith("last."):
                valid = True
                fields = key.lower().split(".")
                calcfield = fields[1].upper()
                value = str(rs[gd.lastGroupStartPosition][calcfield])
                if asm3.utils.is_currency(calcfield):
                    value = str(asm3.utils.cfloat(value) / 100)

            # {SQL.sql} - arbitrary sql command, output first
            # column of first row
            if key.lower().startswith("sql."):
                valid = True
                asql = key[4:]
                if asql.lower().startswith("select"):
                    # Select - return first row/column
                    try:
                        value = self.dbo.query_string(asql)
                    except Exception as e:
                        value = str(e)
                else:
                    # Action query, run it
                    try:
                        value = ""
                        self.dbo.execute(asql)
                    except Exception as e:
                        value = str(e)

            # {IMAGE.animalid[.seq]} - substitutes a link to the image
            # page to direct the browser to retrieve an image. seq is
            # optional and includes image number X for the asm3.animal. If
            # seq is not given, the preferred image is used.
            if key.lower().startswith("image."):
                valid = True
                fields = key.lower().split(".")
                animalid = fields[1]
                seq = ""
                if len(fields) > 2: seq = "&seq=" + fields[2]
                value = "image?db=%s&mode=animal&id=%s%s" % (self.dbo.name(), animalid, seq)

            # {CHIPMANUFACTURER.chipno} - substitutes the microchip
            # manufacturer for the chip number specified
            if key.lower().startswith("chipmanufacturer."):
                valid = True
                fields = key.split(".")
                chipno = fields[1]
                value = asm3.lookups.get_microchip_manufacturer(self.dbo.locale, chipno)

            # {QR.animalid[.size]} - inserts a QR code that
            # links back to an animal's record.
            if key.lower().startswith("qr."):
                valid = True
                fields = key.lower().split(".")
                animalid = fields[1]
                size = "150x150"
                if len(fields) > 2: size = fields[2]
                url = BASE_URL + "/animal?id=%s" % animalid
                value = asm3.utils.qr_datauri(url, size) 

            # {QRS.animalid[.size]} - inserts a QR code that
            # links to the animal's adoptable page
            if key.lower().startswith("qrs."):
                valid = True
                fields = key.lower().split(".")
                animalid = fields[1]
                size = "150x150"
                if len(fields) > 2: size = fields[2]
                url = f"{SERVICE_URL}?account={self.dbo.name()}&method=animal_view&animalid={animalid}"
                value = asm3.utils.qr_datauri(url, size) 

            # {SUBREPORT.[title].[parentField]} - embed a subreport
            if key.lower().startswith("subreport."):
                valid = True
                fields = key.lower().split(".")
                row = gd.lastGroupStartPosition
                if len(fields) < 2:
                    self._p("Invalid SUBREPORT tag, requires minimum 2 components: %s" % key)
                    valid = False
                    startkey = out.find("{", startkey+1)
                    continue

                # Get custom report ID from title
                crid = self.dbo.query_int("SELECT ID FROM customreport WHERE LOWER(Title) LIKE ?", [fields[1]])
                if crid == 0:
                    self._p("Custom report '" + fields[1] + "' doesn't exist.")
                    valid = False
                    startkey = out.find("{", startkey+1)
                    continue

                # Create our list of parameters from the fields passed
                # to the subreport key. They are accessed as PARENTARGX
                # The first one is also passed as PARENTKEY for compatibility
                # with older reports.
                subparams = []
                for x in range(2, len(fields)):
                    fieldname = fields[x].upper()
                    fieldvalue = ""
                    if fieldname not in rs[row]:
                        self._p("Subreport field '" + fields[x] + "' doesn't exist.")
                        valid = False
                    else:
                        fieldvalue = str(rs[row][fieldname])
                    if x == 2:
                        subparams.append(("PARENTKEY", "No question parentkey", fieldvalue, fieldvalue))
                    subparams.append(("PARENTARG%d" % (x-1), "No question parentarg", fieldvalue, fieldvalue ))
                    
                # Get the content from it
                r = Report(self.dbo)
                value = r.Execute(crid, self.user, subparams)

            # Modify our block with the token value
            if valid:
                out = out[0:startkey] + value + out[endkey+1:]

            # Find the next key
            startkey = out.find("{", startkey+1)

        # Output the HTML to the report
        self._Append(out)

    def _SubstituteTemplateHeaderFooter(self, s: str) -> str:
        """
        Substitutes special tokens in the report template
        header and footer. 's' is the header/footer to
        find tokens in, return value is the substituted 
        header/footer.
        """
        l = self.dbo.locale
        s = s.replace("$$TITLE$$", self.title)
        s = s.replace("$$CATEGORY$$", self.category)
        s = s.replace("$$DATE$$", asm3.i18n.python2display(l, self.dbo.now()))
        s = s.replace("$$TIME$$", asm3.i18n.format_time(self.dbo.now()))
        s = s.replace("$$DATETIME$$", asm3.i18n.python2display(l, self.dbo.now()) + " " + asm3.i18n.format_time(self.dbo.now()))
        s = s.replace("$$VERSION$$", asm3.i18n.get_version())
        s = s.replace("$$USER$$", self.user)
        s = s.replace("$$DATABASE$$", self.dbo.name())
        s = s.replace("$$REGISTEREDTO$$", asm3.configuration.organisation(self.dbo))
        s = s.replace("$$ORGANISATION$$", asm3.configuration.organisation(self.dbo))
        s = s.replace("$$ORGANISATIONADDRESS$$", asm3.configuration.organisation_address(self.dbo))
        s = s.replace("$$ORGANISATIONTOWN$$", asm3.configuration.organisation_town(self.dbo))
        s = s.replace("$$ORGANISATIONCITY$$", asm3.configuration.organisation_town(self.dbo))
        s = s.replace("$$ORGANISATIONCOUNTY$$", asm3.configuration.organisation_county(self.dbo))
        s = s.replace("$$ORGANISATIONSTATE$$", asm3.configuration.organisation_county(self.dbo))
        s = s.replace("$$ORGANISATIONPOSTCODE$$", asm3.configuration.organisation_postcode(self.dbo))
        s = s.replace("$$ORGANISATIONZIPCODE$$", asm3.configuration.organisation_postcode(self.dbo))
        s = s.replace("$$ORGANISATIONTELEPHONE$$", asm3.configuration.organisation_telephone(self.dbo))
        return s

    def _SubstituteHeaderFooter(self, headfoot: int, text: str, rs: Results) -> None:
        """
        Outputs the header and footer blocks, 
        'headfoot' - 0 = main header, 1 = footer
        text is the text of the block,
        'rs' is the resultset and
        'rowindex' is the current row from the recordset being looked at
        """
        gd = GroupDescriptor()
        gd.lastGroupEndPosition = len(rs) - 1
        gd.lastGroupStartPosition = 0
        gd.footer = text
        gd.header = text
        self._OutputGroupBlock(gd, headfoot, rs)

    def _SubstituteSQLParameters(self, params: CriteriaParams) -> None:
        """
        Substitutes tokens in the report SQL.
        'params' is expected to be a list of parameters, each
        parameter is a tuple, containing:
        (variable name, question text, substitution value, display value)
        If the parameter wasn't from a var tag, the variable name will contain 
        ASK<x> where <x> is the nth ASK tag in the SQL. In addition, the
        PARENTKEY and PARENTARG types are used for passing values to a subreport.
        The return value is the substituted SQL.
        """
        s = self.sql
        # Throw away any SQL comments
        s = strip_sql_comments(s)
        # Subtitute CONST tokens (do this first so CONST can expand to other tokens)
        for name, value in asm3.utils.regex_multi(r"\$CONST (.+?)\=(.+?)\$", s):
            s = s.replace("$%s$" % name, value) # replace all tokens with the constant value
            s = s.replace("$CONST %s=%s$" % (name, value), "") # remove the constant declaration
        # Substitute CURRENT_DATE-X tokens
        for day in asm3.utils.regex_multi(r"\$CURRENT_DATE\-(.+?)\$", s):
            d = self.dbo.today(offset=asm3.utils.cint(day)*-1)
            s = s.replace("$CURRENT_DATE-%s$" % day, self.dbo.sql_date(d, includeTime=False, wrapParens=False))
        # Substitute CURRENT_DATE+X tokens
        for day in asm3.utils.regex_multi(r"\$CURRENT_DATE\+(.+?)\$", s):
            d = self.dbo.today(offset=asm3.utils.cint(day))
            s = s.replace("$CURRENT_DATE+%s$" % day, self.dbo.sql_date(d, includeTime=False, wrapParens=False))
        # straight tokens
        s = s.replace("$CURRENT_DATE$", self.dbo.sql_date(self.dbo.now(), includeTime=False, wrapParens=False))
        s = s.replace("$CURRENT_DATE_TIME$", self.dbo.sql_date(self.dbo.now(), includeTime=True, wrapParens=False))
        s = s.replace("$CURRENT_DATE_FDM$", self.dbo.sql_date(asm3.i18n.first_of_month(self.dbo.now()), includeTime=False, wrapParens=False))
        s = s.replace("$CURRENT_DATE_LDM$", self.dbo.sql_date(asm3.i18n.last_of_month(self.dbo.now()), includeTime=False, wrapParens=False))
        s = s.replace("$CURRENT_DATE_FDY$", self.dbo.sql_date(asm3.i18n.first_of_year(self.dbo.now()), includeTime=False, wrapParens=False))
        s = s.replace("$CURRENT_DATE_LDY$", self.dbo.sql_date(asm3.i18n.last_of_year(self.dbo.now()), includeTime=False, wrapParens=False))
        s = s.replace("$USER$", self.user)
        s = s.replace("$DATABASENAME$", self.dbo.name())
        # Substitute the location filter, but only if the report actually
        # references it to save unnecessary database lookups
        if s.find("$LOCATIONFILTER$") != -1:
            lf = self.dbo.query_string("SELECT LocationFilter FROM users WHERE UserName = ?", [self.user])
            # If the locationfilter is blank, make it a list of all possible internal location IDs
            if lf == "":
                ils = [ ]
                for il in asm3.lookups.get_internal_locations(self.dbo):
                    ils.append(str(il["ID"]))
                lf = ",".join(ils)
            s = s.replace("$LOCATIONFILTER$", lf)
        # Same goes for site
        if s.find("$SITE$") != -1:
            sf = self.dbo.query_int("SELECT SiteID FROM users WHERE UserName = ?", [self.user])
            s = s.replace("$SITE$", str(sf))
        self.sql = s
        # If we don't have any parameters, no point trying to deal with these
        if params is None: return
        sp = s.find("$")
        asktagsseen = 0
        while sp != -1:
            ep = s.find("$", sp+1)
            if ep == -1: return # Stop if we have an unclosed tag
            token = s[sp+1:ep]
            value = ""
            # ASK tag
            if token.startswith("ASK"):
                asktagsseen += 1
                # Loop through the list of parameters, skipping
                # ASK tags until we get to the correct value
                pop = asktagsseen
                for p in params:
                    if p[0].startswith("ASK"):
                        pop -= 1
                        if pop == 0: 
                            value = p[2]
                            break
            # VAR tag
            if token.startswith("VAR"):
                # Just remove it from the SQL altogether
                value = ""
            # SQL tag
            if token.startswith("SQL"):
                elems = token.split(" ", 2)
                if len(elems) == 3:
                    stype = elems[1]
                    # Substitute any PARENTARGX values in our parameters
                    # since they are frequently used to pass dates
                    for p in params:
                        if p[0].startswith("PARENTARG") and elems[2].find("PARENTARG") != -1: 
                            elems[2] = elems[2].replace(p[0], p[2])
                    # Substitute any @ variable values in our parameters
                    for p in params:
                        elems[2] = elems[2].replace(f"@{p[0]}", p[2])
                    sparams = elems[2].split(",")
                    if stype == "AGE":
                        value = self.dbo.sql_age(sparams[0], sparams[1])
                    elif stype == "CONCAT":
                        value = self.dbo.sql_concat(sparams)
                    elif stype == "ILIKE":
                        value = self.dbo.sql_ilike(sparams[0], sparams[1])
                    elif stype == "INTERVAL":
                        value = self.dbo.sql_interval(sparams[0], sparams[2], sparams[1], sparams[3])
                    elif stype == "DATEDIFF":
                        value = self.dbo.sql_datediff(sparams[0], sparams[1])
                    elif stype == "DATETOCHAR":
                        value = self.dbo.sql_datetochar(sparams[0], sparams[1])
                    elif stype == "HOUR":
                        value = self.dbo.sql_datexhour(sparams[0])
                    elif stype == "MINUTE":
                        value = self.dbo.sql_datexminute(sparams[0])
                    elif stype == "DAY":
                        value = self.dbo.sql_datexday(sparams[0])
                    elif stype == "MONTH":
                        value = self.dbo.sql_datexmonth(sparams[0])
                    elif stype == "YEAR":
                        value = self.dbo.sql_datexyear(sparams[0])
                    elif stype == "WEEKDAY":
                        value = self.dbo.sql_datexweekday(sparams[0])
                    else:
                        value = ""
            # Variable replacement
            if token.startswith("@"):
                vname = token[1:]
                for p in params:
                    if p[0] == vname:
                        value = p[2]
                        break
            # PARENTKEY
            if token.startswith("PARENTKEY"):
                for p in params:
                    if p[0] == "PARENTKEY":
                        value = p[2]
                        break
            # PARENTARGX
            if token.startswith("PARENTARG"):
                for p in params:
                    if p[0] == token:
                        value = p[2]
            # empty token - so $$ entered, used for quoting strings in postgres
            # - skip replacing the token and leave it alone
            if token == "":
                sp = s.find("$", ep+1)
                continue
            # Do the replace
            s = s[0:sp] + value + s[ep+1:]
            # Next token
            sp = s.find("$", sp)
        self.sql = s
        # self._p("substituted sql: %s" % self.sql)

    def GetParams(self, reportId: int) -> ReportParams:
        """
        Returns a list of parameters required for a report, 
        with their types
        'reportId' is the ID of the report to get parameters for.
        Returns a list of parameters, each item is a list containing a
            variable name (or ASK with a number for a one-shot ask), 
            a type and a question string.
        """
        self._ReadReport(reportId)
        params = []

        s = self.sql
        sp = s.find("$")
        asks = 0
        while sp != -1:
            
            # Has to be ASK or VAR - if it isn't, keep looking
            if s[sp:sp+4] != "$ASK" and s[sp:sp+4] != "$VAR":
                sp = s.find("$", sp+1)
                continue

            ep = s.find("$", sp+1)
            if ep == -1: break # stop if we have an unclosed tag

            token = s[sp+1:ep]
            paramtype = ""
            varname = ""
            question = ""

            # ASK
            if token.startswith("ASK"):                
                asks += 1
                varname = "ASK%s" % asks
                fields = token.split(" ", 2)
                if len(fields) > 1: paramtype = fields[1]
                if len(fields) > 2: question = fields[2]

            # VAR
            if token.startswith("VAR"):
                fields = token.split(" ", 3)
                if len(fields) > 1: varname = fields[1]
                if len(fields) > 2: paramtype = fields[2]
                if len(fields) > 3: question = fields[3]

            # Bundle them up
            params.append((varname, paramtype, question))

            # Next token
            sp = s.find("$", ep+1)

        return params

    def OutputCriteria(self) -> None:
        """
        Outputs a human readable string of any criteria set into the 
        report document.
        """
        l = self.dbo.locale
        # Calculate criteria from parameters
        self.criteria = ""
        if self.params is not None:
            for p in self.params:
                self.criteria += p[1] + ": " + p[3] + "<br />"

        # Display criteria if there is some and the option is on
        if self.criteria != "" and not self.omitCriteria and not self.isSubReport:
            self._p(asm3.i18n._("Criteria:", l))
            self._p(self.criteria)
            self._hr()

    def UpdateTables(self) -> None:
        """
        Checks the query, and if it finds tables of generated data that the report is 
        dependent on, runs the necessary processes to update that table.
        Currently works for monthly and annual figures, but it does slow things down a bit.
        Decided not to do this for ownerlookingfor or lostfoundmatch as they would be even slower.
        """
        # Find year, month or date parameters and extract the year and month for updating
        year = 0
        month = 0
        if self.params is not None:
            for p in self.params:
                iv = asm3.utils.cint(p[3])
                dv = asm3.i18n.display2python(self.dbo.locale, p[3])
                if dv is not None:
                    year = dv.year
                    month = dv.month
                elif iv > 1980 and iv < 2100:
                    year = iv
                elif iv > 0 and iv <= 12:
                    month = iv
        if self.sql.find("animalfigures") != -1 and year > 0 and month > 0:
            asm3.animal.update_animal_figures(self.dbo, month, year)
        if self.sql.find("animalfiguresannual") != -1 and year > 0:
            asm3.animal.update_animal_figures_annual(self.dbo, year)

    def Execute(self, reportId: int = 0, username: str = "system", params: CriteriaParams = None) -> str:
        """
        Executes a report
        'reportId' is the ID of the report to run, 'username' is the
        name of the user running the reoprt, 'params' is a list
        of values in order to substitute tokens in the report SQL for.
        They should all be strings and will be literally replaced.
        Return value is the HTML output of the report.
        """
        self.user = username
        self.params = params
        self.output = ""

        # Attempt to read our report if an ID was specified
        if reportId != 0: 
            if not self._ReadReport(reportId):
                raise asm3.utils.ASMValidationError("Report %s does not exist." % reportId)

        # Substitute our parameters in the SQL
        self._SubstituteSQLParameters(params)

        # Make sure the report query is valid
        if not is_valid_query(self.sql):
            raise asm3.utils.ASMValidationError("Reports must be based on a SELECT query.")

        if self.html.upper().startswith("GRAPH"):
            return self._GenerateGraph()
        elif self.html.upper().startswith("MAP"):
            return self._GenerateMap()
        else:
            self._GenerateReport()

        return self.output

    def ExecuteQuery(self, reportId: int = 0, username: str = "system", params: CriteriaParams = None) -> Tuple[Results, List[str]]:
        """
        Executes the query portion of a report only and then returns
        the query results and column order.
        If the query fails to execute
        """
        self.user = username
        self.params = params
        self.output = ""

        # Attempt to read our report if an ID was specified
        if reportId != 0: 
            if not self._ReadReport(reportId):
                raise asm3.utils.ASMValidationError("Report %s does not exist." % reportId)

        # Substitute our parameters in the SQL
        self._SubstituteSQLParameters(params)

        # Make sure the report query is valid
        if not is_valid_query(self.sql):
            raise asm3.utils.ASMValidationError("Reports must be based on a SELECT query.")

        # Run the query
        rs = None
        cols = None
        try:
            rs = self.dbo.query(self.sql)
            cols = self.dbo.query_columns(self.sql)
        except Exception as e:
            self._p(e)
            raise asm3.utils.ASMError(str(e))
        return (rs, cols)
    
    def _GenerateGraph(self) -> str:
        """
        Does the work of generating a graph. Graph queries have to return rows that
        have two or three columns and obey either of the following patterns:
        ( X_AXIS_LABEL, VALUE ) - assumed for two columns
        ( SERIES_LABEL, X_AXIS_VALUE, Y_AXIS_VALUE ) - assumed for three columns, all items with the
                                                same series label will be plotted on a separate line
                                                and both VALUE columns must be numbers
        The html can be just the word GRAPH for a bar chart
        alternatively, a type can be specified as well:
        GRAPH [ LINES | BARS | POINTS | STEPS ]
        """
        l = self.dbo.locale

        htmlheader = self._ReadHeader()
        htmlfooter = self._ReadFooter()

        # Inject the script tags needed into the header
        htmlheader = htmlheader.replace("</head>", asm3.html.graph_js(l) + "\n</head>")

        # Check for plot type
        mode = "bar"
        step = ""
        chartcss = "max-width: 1024px;max-height: 600px;"
        if self.html.find("LINES") != -1:
            mode = "line"
        elif self.html.find("BARS") != -1:
            mode = "bar"
        elif self.html.find("POINTS") != -1:
            mode = "line"
        elif self.html.find("STEPS") != -1:
            mode = "line"
            step = "Chart.defaults.elements.line.stepped = true;\n"
        elif self.html.find("PIE") != -1:
            mode = "pie"
            chartcss = "max-width: 800px;max-height: 800px;"
        # Start the graph off with the HTML header
        self._Append(htmlheader)
        canvashtml = '<canvas class="chartplaceholder" style="display: none;%s"></canvas>' % chartcss
        self._Append(canvashtml)

        # Run the graph query, bail out if we have an error
        try:
            rs, cols = self.dbo.query_tuple_columns(self.sql)
        except Exception as e:
            self._p(e)
            self._Append(htmlfooter)
            return self.output

        # Output any criteria given at the top of the chart
        self.OutputCriteria()

        # Check for no data
        if len(rs) == 0:
            self._Append("<!-- NODATA -->")
            self._p(asm3.i18n._("No data.", l))
            self._Append(htmlfooter)
            return self.output

        self._Append("""
        <script type="text/javascript">
        $(function() {
            $(".chartplaceholder").show();
        """)

        

        labels = []
        datasets = []

        if len(rs[0]) == 2:
            data = []
            for row in rs:
                if row[1] not in labels:
                    labels.append(row[0])
                data.append(row[1])
            dataset = {
                'label': self.title,
                'data': data
            }
            if mode == 'line':
                dataset["showLine"] = False
            datasets.append(dataset)
        else:
            data = {}
            for row in rs:
                if row[0] not in data.keys():
                    data[row[0]] = []
                data[row[0]].append((row[1], row[2]))
                if row[1] not in labels:
                    labels.append(row[1])
            for ds in data.items():
                if mode == 'line':
                    dataset["showLine"] = False
                dsdata = []
                for label in labels:
                    dpvalue = 0
                    for dp in ds[1]:
                        if dp[0] == label:
                            dpvalue += dp[1]
                    dsdata.append(dpvalue)
                dataset = {
                    'label': ds[0],
                    'data': dsdata
                }
                datasets.append(dataset)
        chartdata = {}
        chartdata['type'] = mode
        chartdata['data'] = {
            'labels': labels,
            'datasets': datasets
        }

        self._Append(
        "\n".join([
            step,
            "$.each($('.chartplaceholder'), function(i, ctx) {new Chart(ctx, %s);});\n" % asm3.utils.json(chartdata ,True)
            ])
        )
        self._Append("""
        });
        </script>""")
        self._Append(htmlfooter)

        return self.output

    def _GenerateMap(self) -> str:
        """
        Does the work of generating a map. Map queries have to return rows that
        have two columns:
        ( LATLONG, POPUP )
        The html can just be the word MAP.
        Optionally, you can include where you would like the map centering,
        FIRST for the first value in the dataset, USER for the user's current location
        or an actual latlong separated by a comma
        Eg: MAP FIRST, MAP USER, MAP 51.2,54.5
        """
        l = self.dbo.locale

        htmlheader = self._ReadHeader()
        htmlfooter = self._ReadFooter()

        # Inject the script tags needed into the header and set the title
        htmlheader = htmlheader.replace("</head>", asm3.html.map_js() + "\n</head>")

        # Start the map off with the HTML header
        self._Append(htmlheader)

        # Run the map query, bail out if we have an error
        try:
            rs, cols = self.dbo.query_tuple_columns(self.sql)
        except Exception as e:
            self._p(e)
            self._Append(htmlfooter)
            return self.output

        # Output any criteria given at the top of the chart
        self.OutputCriteria()

        # Check for no data
        if len(rs) == 0:
            self._Append("<!-- NODATA -->")
            self._p(asm3.i18n._("No data.", l))
            self._Append(htmlfooter)
            return self.output

        # Check we have at least two columns
        if len(rs[0]) < 2:
            self._p("Map query should have at least two columns.")
            self._Append(htmlfooter)
            return self.output

        # Choose the center location for the map 
        mapcenter = ""
        if self.html.find("FIRST") != -1 or self.html == "MAP":
            # First valid geocode in the dataset
            for r in rs:
                if r[0] is not None and r[0] != "" and not r[0].startswith("0,0"):
                    mapcenter = r[0]
                    break
        elif self.html.find("USER") != -1: 
            # User's location
            mapcenter = "" 
        elif len(self.html) > 3 and self.html[3] == " " and self.html.find(",") != -1:
            # Actual latlong specified
            mapcenter = self.html[self.html.find(" ")+1:] 

        self._Append('<div id="embeddedmap" style="z-index: 1; width: 100%; height: 600px; color: #000"></div>\n')
        self._Append("<script type='text/javascript'>\n" \
            "setTimeout(function() {\n" \
            "var points = \n")

        p = []
        for values in rs:
            concat = []
            for i, s in enumerate(values):
                if i == 0: continue # skip lat/long
                if asm3.utils.is_date(s): 
                    concat.append(asm3.i18n.python2display(l, s))
                else:
                    concat.append(str(s))
            p.append({ "latlong": values[0], "popuptext": "".join(concat) })

        self._Append( asm3.utils.json(p) + ";\n" )
        self._Append( "mapping.draw_map(\"embeddedmap\", 10, \"%s\", points);\n" % mapcenter )
        self._Append( "}, 50);\n" )
        self._Append("</script>")
        self._Append(htmlfooter)
        return self.output

    def _GenerateReport(self) -> None:
        """
        Does the work of generating the report content, building self.output
        """

        # String indexes within report html string to where 
        # tokens begin and end
        headerstart = 0
        headerend = 0
        bodystart = 0
        bodyend = 0
        footerstart = 0
        footerend = 0
        groupstart = 0
        groupend = 0

        tempbody = ""
        cheader = ""
        cbody = ""
        cfooter = ""

        l = self.dbo.locale

        htmlheader = self._ReadHeader()
        htmlheaderstart = self.html.find("$$HTMLHEADER")
        htmlheaderend = self.html.find("HTMLHEADER$$")
        if htmlheaderstart != -1 and htmlheaderend != -1:
            htmlheader = self.html[htmlheaderstart+12:htmlheaderend]

        # Inject the script tags needed into the header for showing the print toolbar
        if self.toolbar and asm3.configuration.report_toolbar(self.dbo) and not self.isSubReport:
            htmlheader = htmlheader.replace("</head>", asm3.html.report_js(l) + "\n</head>")

        htmlfooter = self._ReadFooter()
        htmlfooterstart = self.html.find("$$HTMLFOOTER")
        htmlfooterend = self.html.find("HTMLFOOTER$$")
        if htmlfooterstart != -1 and htmlfooterend != -1:
            htmlfooter = self.html[htmlfooterstart+12:htmlfooterend]

        # Start the report off with the HTML header
        self._Append(htmlheader)

        headerstart = self.html.find("$$HEADER")
        headerend = self.html.find("HEADER$$", headerstart)
        if headerstart == -1 or headerend == -1:
            self._p("The header block of your report is invalid.")
            return
        cheader = self.html[headerstart+8:headerend]

        bodystart = self.html.find("$$BODY")
        bodyend = self.html.find("BODY$$")

        if bodystart == -1 or bodyend == -1:
            self._p("The body block of your report is invalid.")
            return
        cbody = self.html[bodystart+6:bodyend]

        footerstart = self.html.find("$$FOOTER")
        footerend = self.html.find("FOOTER$$", footerstart)

        if footerstart == -1 or footerend == -1:
            self._p("The footer block of your report is invalid.")
            return
        cfooter = self.html[footerstart+8:footerend]

        # Optional NODATA block
        nodata = ""
        nodatastart = self.html.find("$$NODATA")
        nodataend = self.html.find("NODATA$$")
        if nodatastart != -1 and nodataend != -1:
            nodata = self.html[nodatastart+8:nodataend]

        # Parse all groups from the HTML
        groups = []
        groupstart = self.html.find("$$GROUP_")

        while groupstart != -1:
            groupend = self.html.find("GROUP$$", groupstart)

            if groupend == -1:
                self._p("A group block of your report is invalid (missing GROUP$$ closing tag)")
                return

            ghtml = self.html[groupstart:groupend]
            ghstart = ghtml.find("$$HEAD")
            if ghstart == -1:
                self._p("A group block of your report is invalid (no group $$HEAD)")
                return

            ghstart += 6
            ghend = ghtml.find("$$FOOT", ghstart)

            if ghend == -1:
                self._p("A group block of your report is invalid (no group $$FOOT)")
                return

            gd = GroupDescriptor()
            gd.header = ghtml[ghstart:ghend]
            gd.footer = ghtml[ghend+6:]
            gd.fieldName = ghtml[8:ghstart-6].strip().upper()
            groups.append(gd)
            groupstart = self.html.find("$$GROUP_", groupend)

        # Scan the ORDER BY clause to make sure the order
        # matches the grouping levels.  
        if len(groups) > 0:

            lsql = self.sql.lower()
            startorder = lsql.find("order by")

            if startorder == -1:
                self._p("You have grouping levels on this report without an ORDER BY clause.")
                return

            orderBy = lsql[startorder:]
            ok = False

            for gd in groups:
                ok = -1 != orderBy.find(gd.fieldName.lower())
                if not ok: break

            # This breaks expressions as ORDER BY - let's give the user the power to
            # shoot themselves in the foot here.
            #if not ok:
            #    self._p("Your ORDER BY clause does not match the order of your groups.")
            #    return

        # Output any criteria given at the top of the report
        self.OutputCriteria()

        # If this report relies on tables that are generated by a process (eg: figures reports and animalfigures)
        # run that process to make sure the data is upto date.
        self.UpdateTables()

        # Run the query
        rs = None
        try:
            rs = self.dbo.query(self.sql)
        except Exception as e:
            self._p(e)

        first_record = True

        # If there are no records, show a message to say so
        # but only if it's not a subreport
        if rs is None or len(rs) == 0:
            self._Append("<!-- NODATA -->")
            if not self.isSubReport:
                if nodata == "":
                    self._p(asm3.i18n._("No data to show on the report.", l))
                else:
                    self._Append(nodata)
            else:
                self._Append(nodata)
            return

        # Add the header to the report
        self._SubstituteHeaderFooter(HEADER, cheader, rs)

        # Construct our report
        for row in range(0, len(rs)):

            # If an outer group has changed, we need to end
            # the inner groups first
            if not first_record:
                # This same flag is used to determine whether or
                # not to update the header
                cascade = False

                # Loop through the groups in ascending order.
                # If the switch value for an outer group changes,
                # we need to force finishing of its inner groups.
                for gd in groups:
                    # Check the group field exists
                    if gd.fieldName not in rs[row]:
                        self._p("Cannot construct group, field '%s' does not exist" % gd.fieldName)
                        return
                    if cascade or gd.lastFieldValue != rs[row][gd.fieldName]:
                        # Mark this one for update
                        gd.forceFinish = True
                        gd.lastGroupEndPosition = row - 1
                        cascade = True
                    else:
                        gd.forceFinish = False

                # Now do each group footer in reverse order
                for gd in reversed(groups):
                    if gd.forceFinish:
                        # Output the footer, switching the
                        # field values and calculating any totals
                        self._OutputGroupBlock(gd, FOOTER, rs)

            # Do each header in ascending order
            prevgroup = ""
            for gd in groups:
                if gd.forceFinish or first_record:
                    # Mark the start position
                    gd.lastGroupStartPosition = row
                    gd.lastGroupEndPosition = len(rs)-1
                    # Check the group field exists
                    if gd.fieldName not in rs[row]:
                        self._p("Cannot construct group, field '%s' does not exist" % gd.fieldName)
                        return
                    # Find the end position of the group so that calculations work in headers. 
                    # Also tracks the previous group changing to mark the end if this is a 2nd level group.
                    groupval = rs[row][gd.fieldName]
                    prevgroupval = ""
                    if prevgroup != "": prevgroupval = rs[row][prevgroup]
                    for trow in range(row, len(rs)):
                        if prevgroupval != "" and prevgroupval != rs[trow][prevgroup]:
                            gd.lastGroupEndPosition = trow-1
                            break
                        if groupval != rs[trow][gd.fieldName]:
                            gd.lastGroupEndPosition = trow-1
                            break
                    # Output the header, switching field values
                    # and calculating any totals
                    self._OutputGroupBlock(gd, HEADER, rs)
                prevgroup = gd.fieldName

            first_record = False

            # Make a temp string to hold the body block 
            # while we substitute fields for tags
            tempbody = cbody
            for k, v in rs[row].items():
                tempbody = self._ReplaceFields(tempbody, k, self._DisplayValue(k, v))

            # Update the last value for each group
            for gd in groups:
                try:
                    gd.lastFieldValue = rs[row][gd.fieldName]
                except Exception as e:
                    self._p(e)

            # Deal with any non-field/calculation keys
            startkey = tempbody.find("{")
            while startkey != -1:
                endkey = tempbody.find("}", startkey)
                if endkey == -1: endkey = len(tempbody)-1
                key = tempbody[startkey+1:endkey]
                value = ""
                valid = False

                # {SQL.sql}
                if key.lower().startswith("sql."):
                    valid = True
                    asql = key[4:]
                    if asql.lower().startswith("select"):
                        # Select - return first row/column
                        try:
                            value = self.dbo.query_string(asql)
                        except Exception as e:
                            value = str(e)
                    else:
                        # Action query, run it
                        try:
                            value = ""
                            self.dbo.execute(asql)
                        except Exception as e:
                            value = str(e)

                # {IMAGE.animalid[.seq]} - substitutes a link to the image
                # page to direct the browser to retrieve an image. seq is
                # optional and includes image number X for the asm3.animal. If
                # seq is not given, the preferred image is used.
                if key.lower().startswith("image."):
                    valid = True
                    fields = key.lower().split(".")
                    if len(fields) < 2:
                        self._p("Invalid IMAGE tag, requires 2 components: %s" % key)
                        valid = False
                        startkey = tempbody.find("{", startkey+1)
                        continue
                    animalid = fields[1]
                    seq = ""
                    if len(fields) > 2: seq = "&seq=" + fields[2]
                    value = "image?db=%s&mode=animal&id=%s%s" % (self.dbo.name(), animalid, seq)

                # {CHIPMANUFACTURER.chipno} - substitutes the microchip
                # manufacturer for the chip number specified
                if key.lower().startswith("chipmanufacturer."):
                    valid = True
                    fields = key.split(".")
                    chipno = fields[1]
                    value = asm3.lookups.get_microchip_manufacturer(self.dbo.locale, chipno)

                # {QR.animalid[.size]} - inserts a QR code that
                # links back to an animal's record.
                if key.lower().startswith("qr."):
                    valid = True
                    fields = key.lower().split(".")
                    if len(fields) < 2:
                        self._p("Invalid QR tag, requires 2 components: %s" % key)
                        valid = False
                        startkey = tempbody.find("{", startkey+1)
                        continue
                    animalid = fields[1]
                    size = "150x150"
                    if len(fields) > 2: size = fields[2]
                    url = BASE_URL + "/animal?id=%s" % animalid
                    value = asm3.utils.qr_datauri(url, size)

                # {QRS.animalid[.size]} - inserts a QR code that
                # links to the animal's adoptable page
                if key.lower().startswith("qrs."):
                    valid = True
                    fields = key.lower().split(".")
                    if len(fields) < 2:
                        self._p("Invalid QRS tag, requires 2 components: %s" % key)
                        valid = False
                        startkey = tempbody.find("{", startkey+1)
                        continue
                    animalid = fields[1]
                    size = "150x150"
                    if len(fields) > 2: size = fields[2]
                    url = f"{SERVICE_URL}?account={self.dbo.name()}&method=animal_view&animalid={animalid}"
                    value = asm3.utils.qr_datauri(url, size) 

                # {SUBREPORT.[title].[parentField]} - embed a subreport
                if key.lower().startswith("subreport."):
                    valid = True
                    fields = key.lower().split(".")
                    if len(fields) < 2:
                        self._p("Invalid SUBREPORT tag, requires minimum 2 components: %s" % key)
                        valid = False
                        startkey = tempbody.find("{", startkey+1)
                        continue
                    
                    # Get custom report ID from title
                    crid = self.dbo.query_int("SELECT ID FROM customreport WHERE LOWER(Title) LIKE ?", [fields[1]])
                    if crid == 0:
                        self._p("Custom report '" + fields[1] + "' doesn't exist.")
                        valid = False
                        startkey = tempbody.find("{", startkey+1)
                        continue

                    # Create our list of parameters from the fields passed
                    # to the subreport key. They are accessed as PARENTARGX
                    # The first one is also passed as PARENTKEY for compatibility
                    # with older reports.
                    subparams = []
                    for x in range(2, len(fields)):
                        fieldname = fields[x].upper()
                        fieldvalue = ""
                        if fieldname not in rs[row]:
                            self._p("Subreport field '" + fields[x] + "' doesn't exist.")
                            valid = False
                        else:
                            fieldvalue = str(rs[row][fieldname])
                        if x == 2:
                            subparams.append(("PARENTKEY", "No question parentkey", fieldvalue, fieldvalue))
                        subparams.append(("PARENTARG%d" % (x-1), "No question parentarg", fieldvalue, fieldvalue ))

                    # Get the content from it
                    r = Report(self.dbo)
                    value = r.Execute(crid, self.user, subparams)

                if valid:
                    tempbody = tempbody[0:startkey] + value + tempbody[endkey+1:]

                # next key
                startkey = tempbody.find("{", startkey+1)

            # Add the substituted body block to our report
            self._Append(tempbody)

        # Add the final group footers if there are any
        row = len(rs) - 1
        for gd in reversed(groups):
            gd.lastGroupEndPosition = row
            self._OutputGroupBlock(gd, FOOTER, rs)

        # And the report footer
        self._SubstituteHeaderFooter(FOOTER, cfooter, rs)

        # HTML footer to finish 
        self._Append(htmlfooter)

