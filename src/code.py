#!/usr/bin/python

import os, sys

# The path to the folder containing the ASM3 modules
PATH = os.path.dirname(os.path.abspath(__file__)) + os.sep

# Put the rest of our modules on the path
sys.path.append(PATH)
sys.path.append(PATH + "locale")

import al
import additional as extadditional
import animal as extanimal
import animalcontrol as extanimalcontrol
import async
import audit
import cachemem
import configuration
import csvimport as extcsvimport
import db, dbfs, dbupdate
import diary as extdiary
import financial
import html
from i18n import _, BUILD, translate, get_version, get_display_date_format, get_currency_prefix, get_currency_symbol, get_currency_dp, python2display, add_days, subtract_days, subtract_months, first_of_month, last_of_month, monday_of_week, sunday_of_week, first_of_year, last_of_year, now, format_currency, i18nstringsjs
import log as extlog
import lookups as extlookups
import lostfound as extlostfound
import media as extmedia
import medical as extmedical
import mimetypes
import mobile as extmobile
import movement as extmovement
import onlineform as extonlineform
import person as extperson
import publish as extpublish
import reports as extreports
import search as extsearch
import service as extservice
import smcom
import stock as extstock
import users
import utils
import waitinglist as extwaitinglist
import web
import wordprocessor
from sitedefs import BASE_URL, DEPLOYMENT_TYPE, ELECTRONIC_SIGNATURES, EMERGENCY_NOTICE, FORGOTTEN_PASSWORD, FORGOTTEN_PASSWORD_LABEL, LARGE_FILES_CHUNKED, LOCALE, GEO_PROVIDER, GEO_PROVIDER_KEY, JQUERY_UI_CSS, LEAFLET_CSS, LEAFLET_JS, MULTIPLE_DATABASES, MULTIPLE_DATABASES_TYPE, MULTIPLE_DATABASES_PUBLISH_URL, MULTIPLE_DATABASES_PUBLISH_FTP, ADMIN_EMAIL, EMAIL_ERRORS, MANUAL_HTML_URL, MANUAL_PDF_URL, MANUAL_FAQ_URL, MANUAL_VIDEO_URL, MAP_LINK, MAP_PROVIDER, OSM_MAP_TILES, FOUNDANIMALS_FTP_USER, PETRESCUE_FTP_HOST, PETSLOCATED_FTP_USER, QR_IMG_SRC, SERVICE_URL, SESSION_STORE, SESSION_SECURE_COOKIE, SHARE_BUTTON, SMARTTAG_FTP_USER, SMCOM_PAYMENT_LINK, VETENVOY_US_VENDOR_PASSWORD, VETENVOY_US_VENDOR_USERID

# URL to class mappings
urls = (
    "/", "index",
    "/accounts", "accounts", 
    "/accounts_trx", "accounts_trx", 
    "/additional", "additional",
    "/animal", "animal",
    "/animal_bulk", "animal_bulk",
    "/animal_costs", "animal_costs", 
    "/animal_diary", "animal_diary", 
    "/animal_diet", "animal_diet", 
    "/animal_donations", "animal_donations",
    "/animal_embed", "animal_embed",
    "/animal_find", "animal_find",
    "/animal_find_results", "animal_find_results",
    "/animal_licence", "animal_licence",
    "/animal_log", "animal_log",
    "/animal_media", "animal_media",
    "/animal_medical", "animal_medical",
    "/animal_movements", "animal_movements",
    "/animal_new", "animal_new",
    "/animal_test", "animal_test",
    "/animal_transport", "animal_transport",
    "/animal_vaccination", "animal_vaccination", 
    "/batch", "batch", 
    "/calendarview", "calendarview",
    "/change_password", "change_password",
    "/change_user_settings", "change_user_settings",
    "/citations", "citations", 
    "/config.js", "configjs",
    "/rollup.js", "rollupjs",
    "/css", "css",
    "/csvimport", "csvimport",
    "/database", "database",
    "/diary_edit", "diary_edit",
    "/diary_edit_my", "diary_edit_my",
    "/diarytask", "diarytask",
    "/diarytasks", "diarytasks",
    "/document_gen", "document_gen",
    "/document_edit", "document_edit",
    "/document_media_edit", "document_media_edit",
    "/document_repository", "document_repository",
    "/document_templates", "document_templates",
    "/donation", "donation",
    "/donation_receive", "donation_receive",
    "/foundanimal", "foundanimal",
    "/foundanimal_diary", "foundanimal_diary",
    "/foundanimal_find", "foundanimal_find",
    "/foundanimal_find_results", "foundanimal_find_results",
    "/foundanimal_log", "foundanimal_log",
    "/foundanimal_media", "foundanimal_media",
    "/foundanimal_new", "foundanimal_new",
    "/giftaid_hmrc_spreadsheet", "giftaid_hmrc_spreadsheet",
    "/htmltemplates", "htmltemplates",
    "/i18n.js", "i18njs",
    "/js", "js",
    "/jserror", "jserror",
    "/image", "image",
    "/incident", "incident",
    "/incident_citations", "incident_citations",
    "/incident_diary", "incident_diary",
    "/incident_log", "incident_log",
    "/incident_map", "incident_map",
    "/incident_media", "incident_media",
    "/incident_new", "incident_new",
    "/incident_find", "incident_find",
    "/incident_find_results", "incident_find_results",
    "/latency", "latency",
    "/licence", "licence",
    "/licence_renewal", "licence_renewal",
    "/litters", "litters", 
    "/log_new", "log_new",
    "/lookups", "lookups",
    "/lostanimal", "lostanimal",
    "/lostanimal_find", "lostanimal_find",
    "/lostanimal_find_results", "lostanimal_find_results",
    "/lostanimal_diary", "lostanimal_diary",
    "/lostanimal_log", "lostanimal_log",
    "/lostfound_match", "lostfound_match", 
    "/lostanimal_media", "lostanimal_media",
    "/lostanimal_new", "lostanimal_new",
    "/mailmerge", "mailmerge",
    "/media", "media",
    "/medicalprofile", "medicalprofile",
    "/mobile", "mobile",
    "/mobile_login", "mobile_login",
    "/mobile_logout", "mobile_logout",
    "/mobile_post", "mobile_post",
    "/mobile_report", "mobile_report",
    "/mobile_sign", "mobile_sign",
    "/move_adopt", "move_adopt",
    "/move_book_foster", "move_book_foster",
    "/move_book_reservation", "move_book_reservation",
    "/move_book_retailer", "move_book_retailer",
    "/move_book_recent_adoption", "move_book_recent_adoption",
    "/move_book_recent_other", "move_book_recent_other",
    "/move_book_recent_transfer", "move_book_recent_transfer",
    "/move_book_trial_adoption", "move_book_trial_adoption",
    "/move_book_unneutered", "move_book_unneutered",
    "/move_deceased", "move_deceased",
    "/move_foster", "move_foster",
    "/move_gendoc", "move_gendoc",
    "/move_reclaim", "move_reclaim",
    "/move_reserve", "move_reserve",
    "/move_retailer", "move_retailer",
    "/move_transfer", "move_transfer",
    "/main", "main",
    "/login", "login",
    "/login_jsonp", "login_jsonp",
    "/login_splash", "login_splash",
    "/logout", "logout",
    "/medical", "medical",
    "/onlineform", "onlineform",
    "/onlineform_incoming", "onlineform_incoming",
    "/onlineforms", "onlineforms",
    "/options", "options",
    "/person", "person",
    "/person_citations", "person_citations",
    "/person_diary", "person_diary",
    "/person_donations", "person_donations",
    "/person_embed", "person_embed",
    "/person_find", "person_find",
    "/person_find_results", "person_find_results",
    "/person_investigation", "person_investigation",
    "/person_licence", "person_licence",
    "/person_links", "person_links",
    "/person_log", "person_log",
    "/person_lookingfor", "person_lookingfor",
    "/person_media", "person_media",
    "/person_movements", "person_movements",
    "/person_new", "person_new",
    "/person_rota", "person_rota",
    "/person_traploan", "person_traploan",
    "/person_vouchers", "person_vouchers",
    "/publish", "publish",
    "/publish_logs", "publish_logs",
    "/publish_options", "publish_options",
    "/report", "report",
    "/report_export", "report_export",
    "/report_images", "report_images",
    "/reports", "reports",
    "/roles", "roles",
    "/schema.js", "schemajs",
    "/search", "search",
    "/service", "service",
    "/shelterview", "shelterview",
    "/smcom_my", "smcom_my",
    "/staff_rota", "staff_rota", 
    "/stocklevel", "stocklevel",
    "/sql", "sql",
    "/sql_dump", "sql_dump", 
    "/systemusers", "systemusers",
    "/test", "test",
    "/timeline", "timeline",
    "/traploan", "traploan",
    "/transport", "transport",
    "/vaccination", "vaccination",
    "/waitinglist", "waitinglist",
    "/waitinglist_diary", "waitinglist_diary",
    "/waitinglist_log", "waitinglist_log",
    "/waitinglist_media", "waitinglist_media",
    "/waitinglist_new", "waitinglist_new",
    "/waitinglist_results", "waitinglist_results",
    "/welcome", "welcome"
)

class MemCacheStore(web.session.Store):
    """ 
    A session manager that uses the local memcache install
    If anything goes wrong reading or writing a value, the client
    reconnects so as not to leave the store in a broken state.
    """
    def __contains__(self, key):
        return cachemem.get(key) is not None
    def __getitem__(self, key):
        return cachemem.get(key)
    def __setitem__(self, key, value):
        return cachemem.put(key, value, web.config.session_parameters["timeout"])
    def __delitem__(self, key):
        cachemem.delete(key)
    def cleanup(self, timeout):
        pass # Not needed, we assign values to memcache with timeout

def remote_ip():
    """
    Gets the IP address of the requester, taking account of
    reverse proxies
    """
    remoteip = web.ctx['ip']
    if web.ctx.env.has_key("HTTP_X_FORWARDED_FOR"):
        xf = web.ctx.env["HTTP_X_FORWARDED_FOR"]
        if xf is not None and str(xf).strip() != "":
            remoteip = xf
    return remoteip

def session_manager():
    """
    Sort out our session manager. We use a global in the utils module
    to hold the session to make sure if the app is reloaded it
    always gets the same session manager.
    """
    # Set session parameters, 24 hour timeout
    web.config.session_parameters["cookie_name"] = "asm_session_id"
    web.config.session_parameters["cookie_path"] = "/"
    web.config.session_parameters["timeout"] = 3600 * 24
    web.config.session_parameters["ignore_change_ip"] = True
    web.config.session_parameters["secure"] = SESSION_SECURE_COOKIE
    sess = None
    if utils.websession is None:
        # Disable noisy logging from session db
        web.config.debug_sql = False
        if SESSION_STORE == "memcached":
            store = MemCacheStore()
        else:
            # Otherwise we're using the main database for session storage
            dbs = db.DatabaseInfo()
            dbn = dbs.dbtype.lower()
            if dbn == "postgresql": dbn = "postgres"
            if dbn == "mysql" or dbn == "postgres":
                if dbs.password != "":
                    wdb = web.database(dbn=dbn, host=dbs.host, port=dbs.port, db=dbs.database, user=dbs.username, pw=dbs.password)
                else:
                    wdb = web.database(dbn=dbn, host=dbs.host, port=dbs.port, db=dbs.database, user=dbs.username)
            elif dbn == "sqlite":
                wdb = web.database(dbn=dbn, db=dbs.database)
            try:
                wdb.printing = False
                wdb.query("create table sessions (" \
                    "session_id char(128) UNIQUE NOT NULL," \
                    "atime timestamp NOT NULL default current_timestamp," \
                    "data text)")
            except:
                pass
            store = web.session.DBStore(wdb, 'sessions')
        sess = web.session.Session(app, store, initializer={"user" : None, "dbo" : None, "locale" : None, "searches" : [] })
        utils.websession = sess
    else:
        sess = utils.websession
    return sess

def asm_404():
    """
    Custom 404 page
    """
    s = """
        <html>
        <head>
        <title>404</title>
        </head>
        <body style="background-color: #999">
        <div style="position: absolute; left: 20%; width: 60%; padding: 20px; background-color: white">

        <img src="static/images/logo/icon-64.png" align="right" />
        <h2>Error 404</h2>

        <p>Sorry, but the record you tried to access was not found.</p>

        <p><a href="javascript:history.back()">Go Back</a></p>

        </div>
        </body>
        </html>
    """
    return web.notfound(s)

def asm_500_email():
    """
    Custom 500 error page that sends emails to the site admin
    """
    web.emailerrors(ADMIN_EMAIL, web.webapi._InternalError)()
    s = """
        <html>
        <head>
        <title>500</title>
        <meta http-equiv="refresh" content="5;url=main">
        </head>
        <body style="background-color: #999">
        <div style="position: absolute; left: 20%; width: 60%; padding: 20px; background-color: white">

        <img src="static/images/logo/icon-64.png" align="right" />
        <h2>Error 500</h2>

        <p>An error occurred trying to process your request.</p>

        <p>The system administrator has been notified to fix the problem.</p>

        <p>Sometimes, a database update needs to have been run, or you 
        need to update your browser's local version of the application. 
        Please return to the <a href="main">home page</a> to run and
        receive any updates.</p>

        </div>
        </body>
        </html>
    """
    return web.internalerror(s)

def emergency_notice():
    """
    Returns emergency notice text if any is set.
    """
    if EMERGENCY_NOTICE != "":
        if os.path.exists(EMERGENCY_NOTICE):
            f = open(EMERGENCY_NOTICE, "r")
            s = f.read()
            f.close()
            return s
    return ""

def full_or_json(modulename, s, c, json = False):
    """
    If a json is true, return the controller as json,
    otherwise return the full page in s and add an inline
    script to load the correct module.
    """
    web.header("X-Frame-Options", "SAMEORIGIN")
    web.header("Cache-Control", "no-cache, no-store, must-revalidate")
    if not json:
        web.header("Content-Type", "text/html")
        extra = "<script>\n$(document).ready(function() { common.route_listen(); common.module_start(\"%s\"); });\n</script>\n</body></html>" % modulename
        bodypos = s.rfind("</body>")
        if bodypos == -1:
            return s
        s = s[0:bodypos] + extra
        return s
    else:
        web.header("Content-Type", "application/json")
        if c.endswith(","): c = c[0:len(c)-1]
        return "{ %s }" % c

# SSL for the server can be passed as an extra startup argument, eg:
# python code.py 5000 ssl=true,cert=/etc/cert.crt,key=/etc/cert.key,chain=/etc/chain.crt
if len(sys.argv) > 2:
    from web.wsgiserver import CherryPyWSGIServer
    for arg in sys.argv[2].split(","):
        if arg.find("=") == -1: continue
        k, v = arg.split("=")
        if k == "cert": CherryPyWSGIServer.ssl_certificate = v
        if k == "key": CherryPyWSGIServer.ssl_private_key = v
        if k == "chain": CherryPyWSGIServer.ssl_certificate_chain = v

# Setup the WSGI application object and session with mappings
app = web.application(urls, globals())
app.notfound = asm_404
if EMAIL_ERRORS:
    app.internalerror = asm_500_email
session = session_manager()

# Choose startup mode
if DEPLOYMENT_TYPE == "wsgi":
    application = app.wsgifunc()
elif DEPLOYMENT_TYPE == "fcgi":
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    web.runwsgi = web.runfcgi

class index:
    def GET(self):
        # If there's no database structure, create it before 
        # redirecting to the login page.
        if not MULTIPLE_DATABASES:
            dbo = db.DatabaseInfo()
            if not db.has_structure(dbo):
                raise web.seeother("/database")
        raise web.seeother("/main")

class database:
    def GET(self):
        dbo = db.DatabaseInfo()
        if MULTIPLE_DATABASES:
            if smcom.active():
                raise utils.ASMPermissionError("N/A for sm.com")
            else:
                # We can't create the database as we have multiple, so
                # output the SQL creation script with default data
                # for whatever our dbtype is instead
                s = "-- Creation script for %s\n\n" % dbo.dbtype
                s += dbupdate.sql_structure(dbo)
                s += dbupdate.sql_default_data(dbo).replace("|=", ";")
                web.header("Content-Type", "text/plain")
                web.header("Content-Disposition", "attachment; filename=\"setup.sql\"")
                return s
        if db.has_structure(dbo):
            raise utils.ASMPermissionError("Database already created")
        s = html.bare_header("Create your database")
        s += """
            <h2>Create your new ASM database</h2>
            <form id="cdbf" method="post" action="database">
            <p>Please select your locale: 
            <select name="locale" class="asm-selectbox">
            %s
            </select>
            </p>
            <button id="createdb">Create Database</button>
            <div id="info" class="ui-state-highlight ui-corner-all" style="margin-top: 20px; padding: 0 .7em; display: none">
            <p><span class="ui-icon ui-icon-info" style="float: left; margin-right: .3em;"></span>
            Please be patient, this can take upto a few minutes.
            </p>
            </div>
            </form>
            <script type="text/javascript">
            $("#createdb").button().click(function() {
                $("#createdb").button("disable");
                $("#info").fadeIn();
                $("#cdbf").submit();
            });
            </script>
            """ % html.options_locales()
        s += html.footer()
        web.header("Content-Type", "text/html")
        return s

    def POST(self):
        post = utils.PostedData(web.input(locale = LOCALE), LOCALE)
        dbo = db.DatabaseInfo()
        dbo.locale = post["locale"]
        dbo.installpath = PATH
        dbupdate.install(dbo)
        raise web.seeother("/login")

class image:
    def GET(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode = "animal", id = "0", seq = -1), session.locale)
        try:
            lastmod, imagedata = extmedia.get_image_file_data(session.dbo, post["mode"], post["id"], post.integer("seq"), False)
        except Exception,err:
            al.error("%s" % str(err), "code.image", session.dbo)
            return ""
        if imagedata != "NOPIC":
            web.header("Content-Type", "image/jpeg")
            web.header("Cache-Control", "max-age=86400")
            return imagedata
        else:
            web.header("Content-Type", "image/jpeg")
            web.header("Cache-Control", "no-cache")
            raise web.seeother("image?db=%s&mode=dbfs&id=/reports/nopic.jpg" % session.dbo.database)

class rollupjs:
    def GET(self):
        web.header("Content-Type", "text/javascript")
        web.header("Cache-Control", "max-age=86400")
        rollup = cachemem.get("rollup")
        if rollup is None:
            rollup = html.asm_rollup_scripts(PATH)
            cachemem.put("rollup", rollup, 60)
        return rollup

class configjs:
    def GET(self):
        # db is the database name and ts is the date/time the config was
        # last read upto. The ts value (config_ts) is set during login and
        # updated whenever the user posts to publish_options or options.
        # Both values are used purely to cache the config in the browser, but
        # aren't actually used by the controller here.
        # post = utils.PostedData(web.input(db = "", ts = ""), session.locale)
        if utils.is_loggedin(session) and session.dbo is not None:
            dbo = session.dbo
            web.header("Content-Type", "text/javascript")
            web.header("Cache-Control", "max-age=86400")
            realname = ""
            emailaddress = ""
            expirydate = ""
            expirydatedisplay = ""
            if smcom.active():
                expirydate = smcom.get_expiry_date(dbo)
                if expirydate is not None: 
                    expirydatedisplay = python2display(session.locale, expirydate)
                    expirydate = expirydate.isoformat()
            us = users.get_users(dbo, session.user)
            if len(us) > 0:
                emailaddress = utils.nulltostr(us[0]["EMAILADDRESS"])
                realname = utils.nulltostr(us[0]["REALNAME"])
            geoprovider = GEO_PROVIDER
            geoprovidero = configuration.geo_provider_override(dbo)
            if geoprovidero != "": geoprovider = geoprovidero
            geoproviderkey = GEO_PROVIDER_KEY
            geoproviderkeyo = configuration.geo_provider_key_override(dbo)
            if geoproviderkeyo != "": geoproviderkey = geoproviderkeyo
            mapprovider = MAP_PROVIDER
            mapprovidero = configuration.map_provider_override(dbo)
            if mapprovidero != "": mapprovider = mapprovidero
            maplink = MAP_LINK
            maplinko = configuration.map_link_override(dbo)
            if maplinko != "": maplinko = maplink
            s = "asm={baseurl:'%s'," % BASE_URL
            s += "serviceurl:'%s'," % SERVICE_URL
            s += "build:'%s'," % BUILD
            s += "locale:'%s'," % session.locale
            s += "theme:'%s'," % session.theme
            s += "user:'%s'," % session.user.replace("'", "\\'")
            s += "useremail:'%s'," % emailaddress.replace("'", "\\'")
            s += "userreal:'%s'," % realname.replace("'", "\\'")
            s += "useraccount:'%s'," % dbo.database
            s += "useraccountalias: '%s'," % dbo.alias
            s += "dateformat:'%s'," % get_display_date_format(session.locale)
            s += "currencysymbol:'%s'," % get_currency_symbol(session.locale)
            s += "currencydp:%d," % get_currency_dp(session.locale)
            s += "currencyprefix:'%s'," % get_currency_prefix(session.locale)
            s += "securitymap:'%s'," % session.securitymap
            s += "superuser:%s," % (session.superuser and "true" or "false")
            s += "locationfilter:'%s'," % session.locationfilter
            s += "siteid:%s," % session.siteid
            s += "roles:'%s'," % (session.roles.replace("'", "\\'"))
            s += "roleids:'%s'," % (session.roleids)
            s += "manualhtml:'%s'," % (MANUAL_HTML_URL)
            s += "manualpdf:'%s'," % (MANUAL_PDF_URL)
            s += "manualfaq:'%s'," % (MANUAL_FAQ_URL)
            s += "manualvideo:'%s'," % (MANUAL_VIDEO_URL)
            s += "smcom:%s," % (smcom.active() and "true" or "false")
            s += "smcomexpiry:'%s'," % expirydate
            s += "smcomexpirydisplay:'%s'," % expirydatedisplay
            s += "smcompaymentlink:'%s'," % (SMCOM_PAYMENT_LINK.replace("{alias}", dbo.alias).replace("{database}", dbo.database))
            s += "geoprovider:'%s'," % (geoprovider)
            s += "geoproviderkey:'%s'," % (geoproviderkey)
            s += "jqueryuicss:'%s'," % (JQUERY_UI_CSS)
            s += "leafletcss:'%s'," % (LEAFLET_CSS)
            s += "leafletjs:'%s'," % (LEAFLET_JS)
            s += "maplink:'%s'," % (maplink)
            s += "mapprovider:'%s'," % (mapprovider)
            s += "osmmaptiles:'%s'," % (OSM_MAP_TILES)
            s += "hascustomlogo:%s," % (dbfs.file_exists(dbo, "logo.jpg") and "true" or "false")
            s += "mobileapp:%s," % (session.mobileapp and "true" or "false")
            s += "config:" + html.json([configuration.get_map(dbo),]) + ", "
            s += "menustructure:" + html.json_menu(session.locale, 
                extreports.get_reports_menu(dbo, session.roleids, session.superuser), 
                extreports.get_mailmerges_menu(dbo, session.roleids, session.superuser))
            s += "};"
            return s
        else:
            # Not logged in
            web.header("Content-Type", "text/javascript")
            web.header("Cache-Control", "no-cache")
            return ""

class css:
    def GET(self):
        post = utils.PostedData(web.input(v = "", k = ""), LOCALE) # k is ignored here, but versions css within browser cache
        v = post["v"]
        csspath = PATH + "static/css/" + v
        if v.find("..") != -1: raise web.notfound() # prevent escaping our PATH
        if not os.path.exists(csspath): raise web.notfound()
        if v == "": raise web.notfound()
        f = open(csspath, "r")
        content = f.read()
        f.close()
        web.header("Content-Type", "text/css")
        web.header("Cache-Control", "max-age=8640000") # Don't refresh this version for 100 days
        return content

class i18njs:
    def GET(self):
        post = utils.PostedData(web.input(l = LOCALE, k = ""), LOCALE) # k is ignored here, but versions locale within cache
        l = post["l"]
        web.header("Content-Type", "text/javascript")
        web.header("Cache-Control", "max-age=8640000")
        return i18nstringsjs(l)

class js:
    def GET(self):
        post = utils.PostedData(web.input(v = "", k = ""), LOCALE) # k is ignored here, but versions js within browser cache
        v = post["v"]
        jspath = PATH + "static/js/" + v
        if v.find("..") != -1: raise web.notfound() # prevent escaping our PATH
        if not os.path.exists(jspath): raise web.notfound()
        if v == "": raise web.notfound()
        f = open(jspath, "r")
        content = f.read()
        f.close()
        web.header("Content-Type", "text/javascript")
        web.header("Cache-Control", "max-age=8640000") # Don't refresh this version for 100 days
        return content

class jserror:
    """
    Target for logging javascript errors from the frontend.
    Nothing is returned as the UI does not expect a response.
    Errors are logged and emailed to the admin if EMAIL_ERRORS is set.
    """
    def POST(self):
        post = utils.PostedData(web.input(), LOCALE)
        if utils.is_loggedin(session) and session.dbo is not None:
            dbo = session.dbo
            emailsubject = "%s @ %s" % (post["user"], post["account"])
            emailbody = "%s:\n\n%s" % (post["msg"], post["stack"])
            logmess = "%s@%s: %s %s" % (post["user"], post["account"], post["msg"], post["stack"])
            al.error(logmess, "code.jserror", dbo)
            if EMAIL_ERRORS:
                utils.send_email(dbo, ADMIN_EMAIL, ADMIN_EMAIL, "", emailsubject, emailbody, "plain")

class media:
    def GET(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(id = "0"), LOCALE)
        lastmod, medianame, mimetype, filedata = extmedia.get_media_file_data(session.dbo, post.integer("id"))
        web.header("Content-Type", mimetype)
        web.header("Cache-Control", "max-age=86400")
        web.header("Content-Disposition", "inline; filename=\"%s\"" % medianame)
        return filedata

class mobile:
    def GET(self):
        utils.check_loggedin(session, web, "/mobile_login")
        web.header("Content-Type", "text/html")
        return extmobile.page(session.dbo, session, session.user)

class mobile_login:
    def GET(self):
        l = LOCALE
        post = utils.PostedData(web.input( smaccount = "", username = "", password = "" ), LOCALE)
        if not MULTIPLE_DATABASES:
            dbo = db.DatabaseInfo()
            l = configuration.locale(dbo)
        web.header("Content-Type", "text/html")
        return extmobile.page_login(l, post)

    def POST(self):
        post = utils.PostedData(web.input( database="", username="", password="" ), LOCALE)
        raise web.seeother( extmobile.login(post, session, remote_ip(), PATH) )

class mobile_logout:
    def GET(self):
        url = "mobile_login"
        post = utils.PostedData(web.input(smaccount=""), session.locale)
        if post["smaccount"] != "":
            url = "login?smaccount=" + post["smaccount"]
        elif MULTIPLE_DATABASES and session.dbo is not None and session.dbo.alias != None:
            url = "mobile_login?smaccount=" + session.dbo.alias
        users.update_user_activity(session.dbo, session.user, False)
        users.logout(session, remote_ip())
        raise web.seeother(url)

class mobile_post:
    def handle(self):
        utils.check_loggedin(session, web, "/mobile_login")
        post = utils.PostedData(web.input(posttype = "", id = "0", animalid = "0", medicalid = "0", logtypeid = "0", logtext = "", filechooser = {}, success = ""), session.locale)
        s = extmobile.handler(session, post)
        if s is None:
            raise utils.ASMValidationError("mobile handler failed.")
        elif s.startswith("GO "):
            raise web.seeother(s[3:])
        else:
            web.header("Content-Type", "text/html")
            return s
    def GET(self):
        return self.handle()
    def POST(self):
        return self.handle()

class mobile_report:
    def GET(self):
        utils.check_loggedin(session, web, "/mobile_login")
        users.check_permission(session, users.VIEW_REPORT)
        post = utils.PostedData(web.input(id = "0", mode = "criteria"), session.locale)
        mode = post["mode"]
        dbo = session.dbo
        user = session.user
        crid = post.integer("id")
        # Make sure this user has a role that can view the report
        extreports.check_view_permission(session, crid)
        crit = extreports.get_criteria_controls(session.dbo, crid, mode = "MOBILE", locationfilter = session.locationfilter, siteid = session.siteid) 
        web.header("Content-Type", "text/html")
        web.header("Cache-Control", "no-cache")
        # If the report doesn't take criteria, just show it
        if crit == "":
            al.debug("report %d has no criteria, displaying" % crid, "code.mobile_report", dbo)
            return extreports.execute(dbo, crid, user)
        # If we're in criteria mode (and there are some to get here), ask for them
        elif mode == "criteria":
            title = extreports.get_title(dbo, crid)
            al.debug("building criteria form for report %d %s" % (crid, title), "code.mobile_report", dbo)
            return extmobile.report_criteria(dbo, crid, title, crit)
        # The user has entered the criteria and we're in exec mode, unpack
        # the criteria and run the report
        elif mode == "exec":
            al.debug("got criteria (%s), executing report %d" % (str(post.data), crid), "code.report", dbo)
            p = extreports.get_criteria_params(dbo, crid, post)
            return extreports.execute(dbo, crid, user, p)

class mobile_sign:
    def GET(self):
        utils.check_loggedin(session, web, "/mobile_login")
        web.header("Content-Type", "text/html")
        return extmobile.page_sign(session.dbo, session, session.user)

class main:
    def GET(self):
        utils.check_loggedin(session, web)
        l = session.locale
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        # Do we need to request a password change?
        if session.passchange:
            raise web.seeother("change_password?suggest=1")
        s = html.header("", session)
        # If there's something wrong with the database, logout
        if not db.has_structure(dbo):
            raise web.seeother("logout")
        # Database update checks
        dbmessage = ""
        if dbupdate.check_for_updates(dbo):
            newversion = dbupdate.perform_updates(dbo)
            if newversion != "":
                dbmessage = _("Updated database to version {0}", l).format(str(newversion))
                session.configuration = configuration.get_map(dbo)
        if dbupdate.check_for_view_seq_changes(dbo):
            dbupdate.install_db_views(dbo)
            dbupdate.install_db_sequences(dbo)
            dbupdate.install_db_stored_procedures(dbo)
        # News
        news = configuration.asm_news(dbo)
        # Welcome dialog
        showwelcome = False
        if configuration.show_first_time_screen(dbo) and session.superuser == 1:
            showwelcome = True
        # Messages
        mess = extlookups.get_messages(dbo, session.user, session.roles, session.superuser)
        # Animal links
        linkmode = configuration.main_screen_animal_link_mode(dbo)
        linkmax = configuration.main_screen_animal_link_max(dbo)
        animallinks = []
        linkname = ""
        if linkmode == "recentlychanged":
            linkname = _("Recently Changed", l)
            animallinks = extanimal.get_links_recently_changed(dbo, linkmax, session.locationfilter, session.siteid)
        elif linkmode == "recentlyentered":
            linkname = _("Recently Entered Shelter", l)
            animallinks = extanimal.get_links_recently_entered(dbo, linkmax, session.locationfilter, session.siteid)
        elif linkmode == "recentlyadopted":
            linkname = _("Recently Adopted", l)
            animallinks = extanimal.get_links_recently_adopted(dbo, linkmax, session.locationfilter, session.siteid)
        elif linkmode == "recentlyfostered":
            linkname = _("Recently Fostered", l)
            animallinks = extanimal.get_links_recently_fostered(dbo, linkmax, session.locationfilter, session.siteid)
        elif linkmode == "longestonshelter":
            linkname = _("Longest On Shelter", l)
            animallinks = extanimal.get_links_longest_on_shelter(dbo, linkmax, session.locationfilter, session.siteid)
        elif linkmode == "adoptable":
            linkname = _("Up for adoption", l)
            pc = extpublish.PublishCriteria(configuration.publisher_presets(dbo))
            pc.limit = linkmax
            animallinks = extpublish.get_animal_data(dbo, pc)
        # Users and roles, active users
        usersandroles = users.get_users_and_roles(dbo)
        activeusers = users.get_active_users(dbo)
        # Alerts
        alerts = extanimal.get_alerts(dbo, session.locationfilter, session.siteid)
        if len(alerts) > 0: 
            alerts[0]["LOOKFOR"] = configuration.lookingfor_last_match_count(dbo)
            alerts[0]["LOSTFOUND"] = configuration.lostfound_last_match_count(dbo)
        # Diary Notes
        dm = None
        if configuration.all_diary_home_page(dbo): 
            dm = extdiary.get_uncompleted_upto_today(dbo, "", False)
        else:
            dm = extdiary.get_uncompleted_upto_today(dbo, session.user, False)
        # Create controller
        c = html.controller_bool("showwelcome", showwelcome)
        c += html.controller_str("build", BUILD)
        c += html.controller_str("news", news)
        c += html.controller_str("dbmessage", dbmessage)
        c += html.controller_str("version", get_version())
        c += html.controller_str("emergencynotice", emergency_notice())
        c += html.controller_str("linkname", linkname)
        c += html.controller_str("activeusers", activeusers)
        c += html.controller_json("usersandroles", usersandroles)
        c += html.controller_json("alerts", alerts)
        c += html.controller_json("recent", extanimal.get_timeline(dbo, 10))
        c += html.controller_json("stats", extanimal.get_stats(dbo))
        c += html.controller_json("animallinks", extanimal.get_animals_brief(animallinks))
        c += html.controller_json("diary", dm)
        c += html.controller_json("mess", mess)
        s += html.controller(c)
        s += html.footer()
        al.debug("main for '%s', %d diary notes, %d messages" % (session.user, len(dm), len(mess)), "code.main", dbo)
        return full_or_json("main", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input( mode = "", id = 0 ), session.locale)
        dbo = session.dbo
        mode = post["mode"]
        if mode == "addmessage":
            extlookups.add_message(dbo, session.user, post.boolean("email"), post["message"], post["forname"], post.integer("priority"), post.date("expires"))
        elif mode == "delmessage":
            extlookups.delete_message(dbo, post.integer("id"))
        elif mode == "showfirsttimescreen":
            configuration.show_first_time_screen(dbo, True, False)

class login:
    def GET(self):
        l = LOCALE
        has_animals = True
        custom_splash = False
        post = utils.PostedData(web.input(smaccount = "", username = "", password = "", target = "", nologconnection = ""), l)
        # Filter out IE8 and below right now - they just aren't good enough
        ua = web.ctx.env.get("HTTP_USER_AGENT", "")
        if ua.find("MSIE 6") != -1 or ua.find("MSIE 7") != -1 or ua.find("MSIE 8") != -1:
            raise web.seeother("static/pages/unsupported_ie.html")
        # Figure out how to get the default locale and any overridden splash screen
        # Single database
        if not MULTIPLE_DATABASES:
            dbo = db.DatabaseInfo()
            l = configuration.locale(dbo)
            has_animals = extanimal.get_has_animals(dbo)
            custom_splash = dbfs.file_exists(dbo, "splash.jpg")
        # Multiple databases, no account given
        elif MULTIPLE_DATABASES and MULTIPLE_DATABASES_TYPE == "map" and post["smaccount"] == "":
            try:
                dbo = db.DatabaseInfo()
                l = configuration.locale(dbo)
            except:
                l = LOCALE
                pass
        # Multiple databases, account given
        elif MULTIPLE_DATABASES and MULTIPLE_DATABASES_TYPE == "map" and post["smaccount"] != "":
            dbo = db.get_multiple_database_info(post["smaccount"])
            if dbo.database != "FAIL" and dbo.database != "DISABLED":
                custom_splash = dbfs.file_exists(dbo, "splash.jpg")
                l = configuration.locale(dbo)
        # Sheltermanager.com
        elif MULTIPLE_DATABASES and MULTIPLE_DATABASES_TYPE == "smcom" and post["smaccount"] != "":
            dbo = smcom.get_database_info(post["smaccount"])
            if dbo.database == "WRONGSERVER":
                raise web.seeother("https://sheltermanager.com/service/asmlogin")
            elif dbo.database != "FAIL" and dbo.database != "DISABLED":
                custom_splash = dbfs.file_exists(dbo, "splash.jpg")
                l = configuration.locale(dbo)
        title = _("Animal Shelter Manager Login", l)
        s = html.bare_header(title, locale = l)
        c = html.controller_bool("smcom", smcom.active())
        c += html.controller_bool("multipledatabases", MULTIPLE_DATABASES)
        c += html.controller_str("locale", l)
        c += html.controller_bool("hasanimals", has_animals)
        c += html.controller_bool("customsplash", custom_splash)
        c += html.controller_str("forgottenpassword", FORGOTTEN_PASSWORD)
        c += html.controller_str("forgottenpasswordlabel", FORGOTTEN_PASSWORD_LABEL)
        c += html.controller_str("emergencynotice", emergency_notice())
        c += html.controller_str("smaccount", post["smaccount"])
        c += html.controller_str("husername", post["username"])
        c += html.controller_str("hpassword", post["password"]) 
        c += html.controller_str("nologconnection", post["nologconnection"])
        c += html.controller_str("qrimg", QR_IMG_SRC)
        c += html.controller_str("target", post["target"])
        s += html.controller(c)
        s += "<noscript>" + _("Sorry. ASM will not work without Javascript.", l) + "</noscript>\n"
        s += '<script>\n$(document).ready(function() { $("body").append(login.render()); login.bind(); });\n</script>'
        s += html.footer()
        web.header("Content-Type", "text/html")
        web.header("X-Frame-Options", "SAMEORIGIN")
        return s

    def POST(self):
        post = utils.PostedData(web.input( database = "", username = "", password = "", nologconnection = "", mobile = "" ), LOCALE)
        return users.web_login(post, session, remote_ip(), PATH)

class login_jsonp:
    def GET(self):
        post = utils.PostedData(web.input( database = "", username = "", password = "", nologconnection = "", mobile = "", callback = "" ), LOCALE)
        web.header("Content-Type", "text/javascript")
        return "%s({ response: '%s' })" % (post["callback"], users.web_login(post, session, remote_ip(), PATH))

class login_splash:
    def GET(self):
        post = utils.PostedData(web.input(smaccount = ""), LOCALE)
        try:
            dbo = db.DatabaseInfo()
            if MULTIPLE_DATABASES:
                if post["smaccount"] != "":
                    if MULTIPLE_DATABASES_TYPE == "smcom":
                        dbo = smcom.get_database_info(post["smaccount"])
                    else:
                        dbo = db.get_multiple_database_info(post["smaccount"])
            web.header("Content-Type", "image/jpeg")
            web.header("Cache-Control", "max-age=86400")
            return dbfs.get_string_filepath(dbo, "/reports/splash.jpg")
        except Exception,err:
            al.error("%s" % str(err), "code.login_splash", session.dbo)
            return ""

class logout:
    def GET(self):
        url = "login"
        post = utils.PostedData(web.input(smaccount=""), session.locale)
        if post["smaccount"] != "":
            url = "login?smaccount=" + post["smaccount"]
        elif MULTIPLE_DATABASES and session.dbo is not None and session.dbo.alias != None:
            url = "login?smaccount=" + session.dbo.alias
        users.update_user_activity(session.dbo, session.user, False)
        users.logout(session, remote_ip())
        raise web.seeother(url)

class accounts:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_ACCOUNT)
        dbo = session.dbo
        post = utils.PostedData(web.input(offset="active"), session.locale)
        if post["offset"] == "all":
            accounts = financial.get_accounts(dbo)
        else:
            accounts = financial.get_accounts(dbo, True)
        al.debug("got %d accounts" % len(accounts), "code.accounts", dbo)
        s = html.header("", session)
        c = html.controller_json("accounttypes", extlookups.get_account_types(dbo))
        c += html.controller_json("costtypes", extlookups.get_costtypes(dbo))
        c += html.controller_json("donationtypes", extlookups.get_donation_types(dbo))
        c += html.controller_json("roles", users.get_roles(dbo))
        c += html.controller_json("rows", accounts)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("accounts", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post.string("mode")
        if mode == "create":
            users.check_permission(session, users.ADD_ACCOUNT)
            return financial.insert_account_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_ACCOUNT)
            financial.update_account_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_ACCOUNT)
            for aid in post.integer_list("ids"):
                financial.delete_account(session.dbo, session.user, aid)

class accounts_trx:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_ACCOUNT)
        l = session.locale
        dbo = session.dbo
        post = utils.PostedData(web.input(accountid = 0, fromdate = "", todate = "", recfilter = 0), l)
        defview = configuration.default_account_view_period(dbo)
        fromdate = post["fromdate"]
        todate = post["todate"]
        if fromdate != "" and todate != "":
            fromdate = post.date("fromdate")
            todate = post.date("todate")
        elif defview == financial.THIS_MONTH:
            fromdate = first_of_month(now())
            todate = last_of_month(now())
        elif defview == financial.THIS_WEEK:
            fromdate = monday_of_week(now())
            todate = sunday_of_week(now())
        elif defview == financial.THIS_YEAR:
            fromdate = first_of_year(now())
            todate = last_of_year(now())
        elif defview == financial.LAST_MONTH:
            fromdate = first_of_month(subtract_months(now(), 1))
            todate = last_of_month(subtract_months(now(), 1))
        elif defview == financial.LAST_WEEK:
            fromdate = monday_of_week(subtract_days(now(), 7))
            todate = sunday_of_week(subtract_days(now(), 7))
        transactions = financial.get_transactions(dbo, post.integer("accountid"), fromdate, todate, post.integer("recfilter"))
        accountcode = financial.get_account_code(dbo, post.integer("accountid"))
        accounteditroles = financial.get_account_edit_roles(dbo, post.integer("accountid"))
        al.debug("got %d trx for %s <-> %s" % (len(transactions), str(fromdate), str(todate)), "code.accounts_trx", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", transactions)
        c += html.controller_json("codes", "|".join(financial.get_account_codes(dbo, accountcode)))
        c += html.controller_int("accountid", post.integer("accountid"))
        c += html.controller_str("accountcode", accountcode);
        c += html.controller_str("accounteditroles", "|".join(accounteditroles));
        c += html.controller_str("fromdate", python2display(l, fromdate))
        c += html.controller_str("todate", python2display(l, todate))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("accounts_trx", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.CHANGE_TRANSACTIONS)
            financial.insert_trx_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_TRANSACTIONS)
            financial.update_trx_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.CHANGE_TRANSACTIONS)
            for tid in post.integer_list("ids"):
                financial.delete_trx(session.dbo, session.user, tid)
        elif mode == "reconcile":
            users.check_permission(session, users.CHANGE_TRANSACTIONS)
            for tid in post.integer_list("ids"):
                financial.mark_reconciled(session.dbo, tid)

class additional:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.MODIFY_LOOKUPS)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        fields = extadditional.get_fields(dbo)
        al.debug("got %d additional field definitions" % len(fields), "code.additional", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", fields)
        c += html.controller_json("fieldtypes", extlookups.get_additionalfield_types(dbo))
        c += html.controller_json("linktypes", extlookups.get_additionalfield_links(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("additional", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.MODIFY_LOOKUPS)
            return extadditional.insert_field_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.MODIFY_LOOKUPS)
            extadditional.update_field_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.MODIFY_LOOKUPS)
            for fid in post.integer_list("ids"):
                extadditional.delete_field(session.dbo, session.user, fid)

class animal:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_ANIMAL)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extanimal.get_animal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        # If a location filter is set, prevent the user opening this animal if it's
        # not in their location.
        if not extanimal.is_animal_in_location_filter(a, session.locationfilter, session.siteid):
            raise utils.ASMPermissionError("animal not in location filter/site")
        al.debug("opened animal %s %s" % (a["CODE"], a["ANIMALNAME"]), "code.animal", dbo)
        s = html.header("", session)
        c = html.controller_json("animal", a)
        c += html.controller_plain("activelitters", html.json_autocomplete_litters(dbo))
        c += html.controller_json("additional", extadditional.get_additional_fields(dbo, a["ID"], "animal"))
        c += html.controller_json("animaltypes", extlookups.get_animal_types(dbo))
        if users.check_permission_bool(session, users.VIEW_AUDIT_TRAIL):
            c += html.controller_json("audit", audit.get_audit_for_link(dbo, "animal", a["ID"]))
        c += html.controller_json("species", extlookups.get_species(dbo))
        c += html.controller_json("breeds", extlookups.get_breeds_by_species(dbo))
        c += html.controller_json("coattypes", extlookups.get_coattypes(dbo))
        c += html.controller_json("colours", extlookups.get_basecolours(dbo))
        c += html.controller_json("deathreasons", extlookups.get_deathreasons(dbo))
        c += html.controller_json("diarytasks", extdiary.get_animal_tasks(dbo))
        c += html.controller_json("entryreasons", extlookups.get_entryreasons(dbo))
        c += html.controller_json("flags", extlookups.get_animal_flags(dbo))
        c += html.controller_json("internallocations", extlookups.get_internal_locations(dbo, session.locationfilter, session.siteid))
        c += html.controller_json("microchipmanufacturers", extlookups.MICROCHIP_MANUFACTURERS)
        c += html.controller_json("pickuplocations", extlookups.get_pickup_locations(dbo))
        c += html.controller_json("publishhistory", extanimal.get_publish_history(dbo, a["ID"]))
        c += html.controller_json("posneg", extlookups.get_posneg(dbo))
        c += html.controller_json("sexes", extlookups.get_sexes(dbo))
        c += html.controller_json("sizes", extlookups.get_sizes(dbo))
        c += html.controller_str("sharebutton", SHARE_BUTTON)
        c += html.controller_json("tabcounts", extanimal.get_satellite_counts(dbo, a["ID"])[0])
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_json("ynun", extlookups.get_ynun(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("animal", s, c, post["json"] == "true")
        
    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(mode="save"), session.locale)
        mode = post["mode"]
        if mode == "save":
            users.check_permission(session, users.CHANGE_ANIMAL)
            extanimal.update_animal_from_form(dbo, post, session.user)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_ANIMAL)
            extanimal.delete_animal(dbo, session.user, post.integer("animalid"))
        elif mode == "gencode":
            animaltypeid = post.integer("animaltypeid")
            entryreasonid = post.integer("entryreasonid")
            speciesid = post.integer("speciesid")
            datebroughtin = post.date("datebroughtin")
            sheltercode, shortcode, unique, year = extanimal.calc_shelter_code(dbo, animaltypeid, entryreasonid, speciesid, datebroughtin)
            return sheltercode + "||" + shortcode + "||" + str(unique) + "||" + str(year)
        elif mode == "randomname":
            return extanimal.get_random_name(dbo, post.integer("sex"))
        elif mode == "shared":
            extanimal.insert_publish_history(dbo, post.integer("id"), post["service"])
        elif mode == "clone":
            users.check_permission(session, users.CLONE_ANIMAL)
            utils.check_locked_db(session)
            nid = extanimal.clone_animal(dbo, session.user, post.integer("animalid"))
            return str(nid)
        elif mode == "forgetpublish":
            extanimal.delete_publish_history(dbo, post.integer("id"), post["service"])
        elif mode == "webnotes":
            users.check_permission(session, users.CHANGE_MEDIA)
            extanimal.update_preferred_web_media_notes(dbo, session.user, post.integer("id"), post["comments"])

class animal_bulk:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.CHANGE_ANIMAL)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        c = html.controller_json("ynun", extlookups.get_ynun(dbo))
        c += html.controller_json("animaltypes", extlookups.get_animal_types(dbo))
        c += html.controller_plain("autolitters", html.json_autocomplete_litters(dbo))
        c += html.controller_json("flags", extlookups.get_animal_flags(dbo))
        c += html.controller_json("internallocations", extlookups.get_internal_locations(dbo, session.locationfilter, session.siteid))
        c += html.controller_json("movementtypes", extlookups.get_movement_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("animal_bulk", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        return extanimal.update_animals_from_form(dbo, post, session.user)

class animal_costs:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_COST)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extanimal.get_animal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        cost = extanimal.get_costs(dbo, post.integer("id"))
        costtypes = extlookups.get_costtypes(dbo)
        costtotals = extanimal.get_cost_totals(dbo, post.integer("id"))
        al.debug("got %d costs for animal %s %s" % (len(cost), a["CODE"], a["ANIMALNAME"]), "code.animal_costs", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", cost)
        c += html.controller_json("animal", a)
        c += html.controller_json("costtypes", costtypes)
        c += html.controller_json("costtotals", costtotals)
        c += html.controller_json("tabcounts", extanimal.get_satellite_counts(dbo, a["ID"])[0])
        s += html.controller(c)
        s += html.footer()
        return full_or_json("animal_costs", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        username = session.user
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_COST)
            return extanimal.insert_cost_from_form(dbo, username, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_COST)
            extanimal.update_cost_from_form(dbo, username, post)
        elif mode == "dailyboardingcost":
            users.check_permission(session, users.CHANGE_ANIMAL)
            animalid = post.integer("animalid")
            cost = post.integer("dailyboardingcost")
            extanimal.update_daily_boarding_cost(dbo, username, animalid, cost)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_COST)
            for cid in post.integer_list("ids"):
                extanimal.delete_cost(session.dbo, session.user, cid)

class animal_diary:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_DIARY)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extanimal.get_animal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        diaries = extdiary.get_diaries(dbo, extdiary.ANIMAL, post.integer("id"))
        al.debug("got %d notes for animal %s %s" % (len(diaries), a["CODE"], a["ANIMALNAME"]), "code.animal_diary", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", diaries)
        c += html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extanimal.get_satellite_counts(dbo, a["ID"])[0])
        c += html.controller_str("name", "animal_diary")
        c += html.controller_int("linkid", a["ID"])
        c += html.controller_json("forlist", users.get_users_and_roles(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("diary", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_DIARY)
            return extdiary.insert_diary_from_form(session.dbo, session.user, extdiary.ANIMAL, post.integer("linkid"), post)
        elif mode == "update":
            users.check_permission(session, users.EDIT_ALL_DIARY_NOTES)
            extdiary.update_diary_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_DIARY)
            for did in post.integer_list("ids"):
                extdiary.delete_diary(session.dbo, session.user, did)
        elif mode == "complete":
            users.check_permission(session, users.BULK_COMPLETE_NOTES)
            for did in post.integer_list("ids"):
                extdiary.complete_diary_note(session.dbo, session.user, did)

class animal_diet:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_DIET)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extanimal.get_animal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        diet = extanimal.get_diets(dbo, post.integer("id"))
        diettypes = extlookups.get_diets(dbo)
        al.debug("got %d diets for animal %s %s" % (len(diet), a["CODE"], a["ANIMALNAME"]), "code.animal_diet", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", diet)
        c += html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extanimal.get_satellite_counts(dbo, a["ID"])[0])
        c += html.controller_json("diettypes", diettypes)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("animal_diet", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_DIET)
            return str(extanimal.insert_diet_from_form(session.dbo, session.user, post))
        elif mode == "update":
            users.check_permission(session, users.CHANGE_DIET)
            extanimal.update_diet_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_DIET)
            for did in post.integer_list("ids"):
                extanimal.delete_diet(session.dbo, session.user, did)

class animal_donations:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_DONATION)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extanimal.get_animal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        donations = financial.get_animal_donations(dbo, post.integer("id"))
        al.debug("got %d donations for animal %s %s" % (len(donations), a["CODE"], a["ANIMALNAME"]), "code.animal_donations", dbo)
        s = html.header("", session)
        c = html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extanimal.get_satellite_counts(dbo, a["ID"])[0])
        c += html.controller_str("name", "animal_donations")
        c += html.controller_json("donationtypes", extlookups.get_donation_types(dbo))
        c += html.controller_json("accounts", financial.get_accounts(dbo))
        c += html.controller_json("paymenttypes", extlookups.get_payment_types(dbo))
        c += html.controller_json("frequencies", extlookups.get_donation_frequencies(dbo))
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_json("rows", donations)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("donations", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        dbo = session.dbo
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_DONATION)
            return financial.insert_donation_from_form(dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_DONATION)
            financial.update_donation_from_form(dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_DONATION)
            for did in post.integer_list("ids"):
                financial.delete_donation(dbo, session.user, did)
        elif mode == "receive":
            users.check_permission(session, users.CHANGE_DONATION)
            for did in post.integer_list("ids"):
                financial.receive_donation(dbo, session.user, did)
        elif mode == "personmovements":
            users.check_permission(session, users.VIEW_MOVEMENT)
            web.header("Content-Type", "application/json")
            return html.json(extmovement.get_person_movements(dbo, post.integer("personid")))

class animal_embed:
    def POST(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_ANIMAL)
        dbo = session.dbo
        post = utils.PostedData(web.input(mode = "find"), session.locale)
        web.header("Content-Type", "application/json")
        mode = post["mode"]
        if mode == "find":
            q = post["q"]
            rows = extanimal.get_animal_find_simple(dbo, q, post["filter"], 100, session.locationfilter, session.siteid)
            al.debug("got %d results for '%s'" % (len(rows), str(web.ctx.query)), "code.animal_embed", dbo)
            return html.json(rows)
        elif mode == "multiselect":
            rows = extanimal.get_animal_find_simple(dbo, "", "all", configuration.record_search_limit(dbo), session.locationfilter, session.siteid)
            locations = extlookups.get_internal_locations(dbo)
            species = extlookups.get_species(dbo)
            litters = extanimal.get_litters(dbo)
            rv = { "rows": rows, "locations": locations, "species": species, "litters": litters }
            return html.json(rv)
        elif mode == "id":
            a = extanimal.get_animal(dbo, post.integer("id"))
            if a is None:
                al.error("get animal by id %d found no records." % (post.integer("id")), "code.animal_embed", dbo)
                raise web.notfound()
            else:
                al.debug("got animal %s %s by id" % (a["CODE"], a["ANIMALNAME"]), "code.animal_embed", dbo)
                return html.json((a,))

class animal_find:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_ANIMAL)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        c = html.controller_json("agegroups", configuration.age_groups(dbo))
        c += html.controller_json("animaltypes", extlookups.get_animal_types(dbo))
        c += html.controller_json("species", extlookups.get_species(dbo))
        c += html.controller_json("breeds", extlookups.get_breeds_by_species(dbo))
        c += html.controller_json("flags", extlookups.get_animal_flags(dbo))
        c += html.controller_json("sexes", extlookups.get_sexes(dbo))
        c += html.controller_json("internallocations", extlookups.get_internal_locations(dbo, session.locationfilter, session.siteid))
        c += html.controller_json("sizes", extlookups.get_sizes(dbo))
        c += html.controller_json("colours", extlookups.get_basecolours(dbo))
        c += html.controller_json("users", users.get_users(dbo))
        s += html.controller(c)
        s += html.footer()
        al.debug("loaded lookups for find animal", "code.animal_find", dbo)
        return full_or_json("animal_find", s, c, post["json"] == "true")

class animal_find_results:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_ANIMAL)
        dbo = session.dbo
        l = session.locale
        post = utils.PostedData(web.input(q = "", mode = ""), session.locale)
        q = post["q"]
        mode = post["mode"]
        if mode == "SIMPLE":
            results = extanimal.get_animal_find_simple(dbo, q, "all", configuration.record_search_limit(dbo), session.locationfilter, session.siteid)
        else:
            results = extanimal.get_animal_find_advanced(dbo, post.data, configuration.record_search_limit(dbo), session.locationfilter, session.siteid)
        add = None
        if len(results) > 0: 
            add = extadditional.get_additional_fields_ids(dbo, results, "animal")
        al.debug("found %d results for %s" % (len(results), str(web.ctx.query)), "code.animal_find_results", dbo)
        wasonshelter = False
        if q == "" and mode == "SIMPLE":
            wasonshelter = True
        s = html.header("", session)
        c = html.controller_json("rows", results)
        c += html.controller_str("resultsmessage", _("Search returned {0} results.", l).format(len(results)))
        c += html.controller_json("additional", add)
        c += html.controller_bool("wasonshelter", wasonshelter)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("animal_find_results", s, c, post["json"] == "true")

class animal_licence:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_LICENCE)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extanimal.get_animal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        licences = financial.get_animal_licences(dbo, post.integer("id"))
        al.debug("got %d licences" % len(licences), "code.animal_licence", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "animal_licence")
        c += html.controller_json("rows", licences)
        c += html.controller_json("animal", a)
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_json("tabcounts", extanimal.get_satellite_counts(dbo, a["ID"])[0])
        c += html.controller_json("licencetypes", extlookups.get_licence_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("licence", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_LICENCE)
            return financial.insert_licence_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_LICENCE)
            financial.update_licence_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_LICENCE)
            for lid in post.integer_list("ids"):
                financial.delete_licence(session.dbo, session.user, lid)

class animal_log:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_LOG)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0, filter = -2), session.locale)
        logfilter = post.integer("filter")
        if logfilter == -2: logfilter = configuration.default_log_filter(dbo)
        a = extanimal.get_animal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        logs = extlog.get_logs(dbo, extlog.ANIMAL, post.integer("id"), logfilter)
        al.debug("got %d logs for animal %s %s" % (len(logs), a["CODE"], a["ANIMALNAME"]), "code.animal_log", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "animal_log")
        c += html.controller_int("linkid", post.integer("id"))
        c += html.controller_int("filter", logfilter)
        c += html.controller_json("rows", logs)
        c += html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extanimal.get_satellite_counts(dbo, a["ID"])[0])
        c += html.controller_json("logtypes", extlookups.get_log_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("log", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_LOG)
            return extlog.insert_log_from_form(session.dbo, session.user, extlog.ANIMAL, post.integer("linkid"), post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_LOG)
            extlog.update_log_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_LOG)
            for lid in post.integer_list("ids"):
                extlog.delete_log(session.dbo, session.user, lid)

class animal_media:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MEDIA)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0, newmedia=0), session.locale)
        a = extanimal.get_animal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        m = extmedia.get_media(dbo, extmedia.ANIMAL, post.integer("id"))
        al.debug("got %d media entries for animal %s %s" % (len(m), a["CODE"], a["ANIMALNAME"]), "code.animal_media", dbo)
        s = html.header("", session)
        c = html.controller_json("media", m)
        c += html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extanimal.get_satellite_counts(dbo, a["ID"])[0])
        c += html.controller_bool("showpreferred", True)
        c += html.controller_int("linkid", post.integer("id"))
        c += html.controller_int("linktypeid", extmedia.ANIMAL)
        c += html.controller_bool("newmedia", post.integer("newmedia") == 1)
        c += html.controller_str("name", self.__class__.__name__)
        c += html.controller_str("sigtype", ELECTRONIC_SIGNATURES)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("media", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create", filechooser={}, linkid="0", base64image = "", _unicode=False), session.locale)
        mode = post["mode"]
        dbo = session.dbo
        l = session.locale
        linkid = post.integer("linkid")
        if mode == "create":
            users.check_permission(session, users.ADD_MEDIA)
            extmedia.attach_file_from_form(session.dbo, session.user, extmedia.ANIMAL, linkid, post)
            raise web.seeother("animal_media?id=%d" % linkid)
        elif mode == "createdoc":
            users.check_permission(session, users.ADD_MEDIA)
            mediaid = extmedia.create_blank_document_media(session.dbo, session.user, extmedia.ANIMAL, linkid)
            raise web.seeother("document_media_edit?id=%d&redirecturl=animal_media?id=%d" % (mediaid, linkid))
        elif mode == "createlink":
            users.check_permission(session, users.ADD_MEDIA)
            mediaid = extmedia.attach_link_from_form(session.dbo, session.user, extmedia.ANIMAL, linkid, post)
            raise web.seeother("animal_media?id=%d" % linkid)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MEDIA)
            extmedia.update_media_notes(session.dbo, session.user, post.integer("mediaid"), post["comments"])
        elif mode == "delete":
            users.check_permission(session, users.DELETE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.delete_media(session.dbo, session.user, mid)
        elif mode == "email":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                content = dbfs.get_string(dbo, m["MEDIANAME"])
                if m["MEDIANAME"].endswith("html"):
                    content = utils.fix_relative_document_uris(content, BASE_URL, MULTIPLE_DATABASES and dbo.database or "")
                utils.send_email(dbo, configuration.email(dbo), emailadd, "", m["MEDIANOTES"], post["emailnote"], "html", content, m["MEDIANAME"])
            return emailadd
        elif mode == "emailpdf":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                if not m["MEDIANAME"].endswith("html"): continue
                content = dbfs.get_string(dbo, m["MEDIANAME"])
                contentpdf = utils.html_to_pdf(content, BASE_URL, MULTIPLE_DATABASES and dbo.database or "")
                utils.send_email(dbo, configuration.email(dbo), emailadd, "", m["MEDIANOTES"], post["emailnote"], "plain", contentpdf, "document.pdf")
            return emailadd
        elif mode == "emailsign":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            body = []
            body.append(post["emailnote"] + "\n\n")
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                if not m["MEDIANAME"].endswith("html"): continue
                body.append(m["MEDIANOTES"])
                body.append("%s?account=%s&method=sign_document&formid=%d" % (SERVICE_URL, dbo.database, mid))
                body.append("")
            utils.send_email(dbo, configuration.email(dbo), emailadd, "", _("Document signing request", l), "\n".join(body), "plain")
            return emailadd
        elif mode == "sign":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.sign_document(session.dbo, session.user, mid, post["sig"], post["signdate"])
        elif mode == "signpad":
            configuration.signpad_ids(session.dbo, session.user, post["ids"])
        elif mode == "rotateclock":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.rotate_media(session.dbo, session.user, mid, True)
        elif mode == "rotateanti":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.rotate_media(session.dbo, session.user, mid, False)
        elif mode == "web":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_web_preferred(session.dbo, session.user, mid)
        elif mode == "video":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_video_preferred(session.dbo, session.user, mid)
        elif mode == "doc":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_doc_preferred(session.dbo, session.user, mid)
        elif mode == "exclude":
            users.check_permission(session, users.CHANGE_MEDIA)
            extmedia.set_excluded(session.dbo, session.user, post.integer("mediaid"), post.integer("exclude"))

class animal_medical:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MEDICAL)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extanimal.get_animal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        med = extmedical.get_regimens_treatments(dbo, post.integer("id"))
        profiles = extmedical.get_profiles(dbo)
        al.debug("got %d medical entries for animal %s %s" % (len(med), a["CODE"], a["ANIMALNAME"]), "code.animal_medical", dbo)
        s = html.header("", session)
        c = html.controller_json("profiles", profiles)
        c += html.controller_json("rows", med)
        c += html.controller_str("name", "animal_medical")
        c += html.controller_json("tabcounts", extanimal.get_satellite_counts(dbo, a["ID"])[0])
        c += html.controller_json("stockitems", extstock.get_stock_items(dbo))
        c += html.controller_json("stockusagetypes", extlookups.get_stock_usage_types(dbo))
        c += html.controller_json("users", users.get_users(dbo))
        c += html.controller_json("animal", a)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("medical", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MEDICAL)
            extmedical.insert_regimen_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MEDICAL)
            extmedical.update_regimen_from_form(session.dbo, session.user, post)
        elif mode == "delete_regimen":
            users.check_permission(session, users.DELETE_MEDICAL)
            for mid in post.integer_list("ids"):
                extmedical.delete_regimen(session.dbo, session.user, mid)
        elif mode == "delete_treatment":
            users.check_permission(session, users.DELETE_MEDICAL)
            for mid in post.integer_list("ids"):
                extmedical.delete_treatment(session.dbo, session.user, mid)
        elif mode == "get_profile":
            return html.json([extmedical.get_profile(session.dbo, post.integer("profileid"))])
        elif mode == "given":
            users.check_permission(session, users.BULK_COMPLETE_MEDICAL)
            newdate = post.date("newdate")
            vet = post.integer("givenvet")
            by = post["givenby"]
            comments = post["treatmentcomments"]
            for mid in post.integer_list("ids"):
                extmedical.update_treatment_given(session.dbo, session.user, mid, newdate, by, vet, comments)
            if post.integer("item") != -1:
                extstock.deduct_stocklevel_from_form(session.dbo, session.user, post)
        elif mode == "required":
            users.check_permission(session, users.BULK_COMPLETE_MEDICAL)
            newdate = post.date("newdate")
            for mid in post.integer_list("ids"):
                extmedical.update_treatment_required(session.dbo, session.user, mid, newdate)

class animal_movements:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MOVEMENT)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extanimal.get_animal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        movements = extmovement.get_animal_movements(dbo, post.integer("id"))
        al.debug("got %d movements for animal %s %s" % (len(movements), a["CODE"], a["ANIMALNAME"]), "code.animal_movements", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", movements)
        c += html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extanimal.get_satellite_counts(dbo, a["ID"])[0])
        c += html.controller_json("movementtypes", extlookups.get_movement_types(dbo))
        c += html.controller_json("reservationstatuses", extlookups.get_reservation_statuses(dbo))
        c += html.controller_json("returncategories", extlookups.get_entryreasons(dbo))
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_str("name", self.__class__.__name__)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("movements", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MOVEMENT)
            return extmovement.insert_movement_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MOVEMENT)
            extmovement.update_movement_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_MOVEMENT)
            for mid in post.integer_list("ids"):
                extmovement.delete_movement(session.dbo, session.user, mid)
        elif mode == "insurance":
            return extmovement.generate_insurance_number(session.dbo)

class animal_new:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_ANIMAL)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        c = html.controller_plain("autolitters", html.json_autocomplete_litters(dbo))
        c += html.controller_json("additional", extadditional.get_additional_fields(dbo, 0, "animal"))
        c += html.controller_json("animaltypes", extlookups.get_animal_types(dbo))
        c += html.controller_json("species", extlookups.get_species(dbo))
        c += html.controller_json("breeds", extlookups.get_breeds_by_species(dbo))
        c += html.controller_json("colours", extlookups.get_basecolours(dbo))
        c += html.controller_json("flags", extlookups.get_animal_flags(dbo))
        c += html.controller_json("sexes", extlookups.get_sexes(dbo))
        c += html.controller_json("entryreasons", extlookups.get_entryreasons(dbo))
        c += html.controller_json("internallocations", extlookups.get_internal_locations(dbo, session.locationfilter, session.siteid))
        c += html.controller_json("sizes", extlookups.get_sizes(dbo))
        s += html.controller(c)
        s += html.footer()
        al.debug("loaded lookups for new animal", "code.animal_new", dbo)
        return full_or_json("animal_new", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        utils.check_locked_db(session)
        post = utils.PostedData(web.input(mode = "save"), session.locale)
        mode = post["mode"]
        if mode == "save":
            users.check_permission(session, users.ADD_ANIMAL)
            animalid, code = extanimal.insert_animal_from_form(session.dbo, post, session.user)
            return str(animalid) + " " + str(code)
        elif mode == "recentnamecheck":
            rows = extanimal.get_recent_with_name(session.dbo, post["animalname"])
            al.debug("recent names found %d rows for '%s'" % (len(rows), post["animalname"]), "code.animal_new.recentnamecheck", session.dbo)
            if len(rows) > 0:
                return "|".join((str(rows[0]["ANIMALID"]), rows[0]["SHELTERCODE"], rows[0]["ANIMALNAME"]))
        elif mode == "units":
            return "&&".join(extanimal.get_units_with_availability(session.dbo, post.integer("locationid")))

class animal_test:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_TEST)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extanimal.get_animal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        test = extmedical.get_tests(dbo, post.integer("id"))
        al.debug("got %d tests" % len(test), "code.animal_test", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "animal_test")
        c += html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extanimal.get_satellite_counts(dbo, a["ID"])[0])
        c += html.controller_json("rows", test)
        c += html.controller_json("stockitems", extstock.get_stock_items(dbo))
        c += html.controller_json("stockusagetypes", extlookups.get_stock_usage_types(dbo))
        c += html.controller_json("testtypes", extlookups.get_test_types(dbo))
        c += html.controller_json("testresults", extlookups.get_test_results(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("test", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode = "create", ids = ""), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_TEST)
            return extmedical.insert_test_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_TEST)
            extmedical.update_test_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_TEST)
            for vid in post.integer_list("ids"):
                extmedical.delete_test(session.dbo, session.user, vid)
        elif mode == "perform":
            users.check_permission(session, users.CHANGE_TEST)
            newdate = post.date("newdate")
            vet = post.integer("givenvet")
            testresult = post.integer("testresult")
            for vid in post.integer_list("ids"):
                extmedical.complete_test(session.dbo, session.user, vid, newdate, testresult, vet)
            if post.integer("item") != -1:
                extstock.deduct_stocklevel_from_form(session.dbo, session.user, post)

class animal_transport:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_TRANSPORT)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extanimal.get_animal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        transports = extmovement.get_animal_transports(dbo, post.integer("id"))
        al.debug("got %d transports" % len(transports), "code.animal_transport", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "animal_transport")
        c += html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extanimal.get_satellite_counts(dbo, a["ID"])[0])
        c += html.controller_json("transporttypes", extlookups.get_transport_types(dbo))
        c += html.controller_json("rows", transports)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("transport", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_TRANSPORT)
            return extmovement.insert_transport_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_TRANSPORT)
            extmovement.update_transport_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_TRANSPORT)
            for mid in post.integer_list("ids"):
                extmovement.delete_transport(session.dbo, session.user, mid)
        elif mode == "setstatus":
            users.check_permission(session, users.CHANGE_TRANSPORT)
            extmovement.update_transport_statuses(session.dbo, session.user, post.integer_list("ids"), post.integer("newstatus"))

class animal_vaccination:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_VACCINATION)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extanimal.get_animal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        vacc = extmedical.get_vaccinations(dbo, post.integer("id"))
        al.debug("got %d vaccinations" % len(vacc), "code.vaccination", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "animal_vaccination")
        c += html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extanimal.get_satellite_counts(dbo, a["ID"])[0])
        c += html.controller_json("rows", vacc)
        c += html.controller_json("manufacturers", "|".join(extmedical.get_vacc_manufacturers(dbo)))
        c += html.controller_json("stockitems", extstock.get_stock_items(dbo))
        c += html.controller_json("stockusagetypes", extlookups.get_stock_usage_types(dbo))
        c += html.controller_json("vaccinationtypes", extlookups.get_vaccination_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("vaccination", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode = "create", ids = "", duration = 0), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_VACCINATION)
            return extmedical.insert_vaccination_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_VACCINATION)
            extmedical.update_vaccination_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_VACCINATION)
            for vid in post.integer_list("ids"):
                extmedical.delete_vaccination(session.dbo, session.user, vid)
        elif mode == "given":
            users.check_permission(session, users.BULK_COMPLETE_VACCINATION)
            newdate = post.date("newdate")
            rescheduledate = post.date("rescheduledate")
            reschedulecomments = post["reschedulecomments"]
            vet = post.integer("givenvet")
            for vid in post.integer_list("ids"):
                extmedical.complete_vaccination(session.dbo, session.user, vid, newdate, vet)
                if rescheduledate is not None:
                    extmedical.reschedule_vaccination(session.dbo, session.user, vid, rescheduledate, reschedulecomments)
                if post.integer("item") != -1:
                    extmedical.update_vaccination_batch_stock(session.dbo, session.user, vid, post.integer("item"))
            if post.integer("item") != -1:
                extstock.deduct_stocklevel_from_form(session.dbo, session.user, post)
        elif mode == "required":
            users.check_permission(session, users.BULK_COMPLETE_VACCINATION)
            newdate = post.date("newdate")
            for vid in post.integer_list("ids"):
                extmedical.update_vaccination_required(session.dbo, session.user, vid, newdate)

class batch:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.TRIGGER_BATCH)
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        s += html.controller("")
        s += html.footer()
        return full_or_json("batch", s, "", post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        utils.check_locked_db(session)
        dbo = session.dbo
        post = utils.PostedData(web.input(mode = ""), session.locale)
        users.check_permission(session, users.TRIGGER_BATCH)
        web.header("Content-Type", "text/html")
        if post["mode"] == "genfigyear":
            try:
                extanimal.update_animal_figures_annual(dbo, post.date("figyear").year)
                extanimal.update_animal_figures_asilomar(dbo, post.date("figyear").year)
                return "0"
            except Exception,err:
                return str(err)
        elif post["mode"] == "genfigmonth":
            try:
                extanimal.update_animal_figures(dbo, post.date("figmonth").month, post.date("figmonth").year)
                extanimal.update_animal_figures_monthly_asilomar(dbo, post.date("figmonth").month, post.date("figmonth").year)
                return "0"
            except Exception,err:
                return str(err)
        elif post["mode"] == "genshelterpos":
            try:
                extanimal.update_on_shelter_animal_statuses(dbo)
                return "0"
            except Exception,err:
                return str(err)
        elif post["mode"] == "genallpos":
            try:
                extanimal.update_all_animal_statuses(dbo)
                return "0"
            except Exception,err:
                return str(err)
        elif post["mode"] == "genlookingfor":
            try:
                extperson.update_lookingfor_report(dbo)
                return "0"
            except Exception,err:
                return str(err)
        elif post["mode"] == "genownername":
            try:
                extperson.update_owner_names(dbo)
                return "0"
            except Exception,err:
                return str(err)
        elif post["mode"] == "genlostfound":
            try:
                extlostfound.update_match_report(dbo)
                return "0"
            except Exception,err:
                return str(err)

class calendarview:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_ANIMAL)
        l = session.locale
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        if post["start"] == "":
            s = html.header("", session)
            s += html.footer()
            al.debug("calendarview load page", "code.calendarview", dbo)
            return full_or_json("calendarview", s, "", post["json"] == "true")
        elif post["start"] != "" and post["end"] != "":
            ev = post["ev"]
            if ev == "": ev = "dvmtrolp"
            events = []
            # Find data for the month
            if "d" in ev and users.check_permission_bool(session, users.VIEW_DIARY):
                user = session.user
                # Show all diary notes on the calendar if the user chose to see all
                # on the home page, or they have permission to view all notes
                if configuration.all_diary_home_page(dbo) or users.check_permission_bool(session, users.EDIT_ALL_DIARY_NOTES):
                    user = ""
                for d in extdiary.get_between_two_dates(dbo, user, post["start"], post["end"]):
                    allday = False
                    # If the diary time is midnight, assume all day instead
                    if d["DIARYDATETIME"].hour == 0 and d["DIARYDATETIME"].minute == 0:
                        allday = True
                    events.append({ 
                        "title": d["SUBJECT"], 
                        "allDay": allday, 
                        "start": d["DIARYDATETIME"], 
                        "tooltip": "%s %s" % (d["LINKINFO"], d["NOTE"]), 
                        "icon": "diary",
                        "link": "diary_edit_my" })
            if "v" in ev and users.check_permission_bool(session, users.VIEW_VACCINATION):
                for v in extmedical.get_vaccinations_two_dates(dbo, post["start"], post["end"], session.locationfilter, session.siteid):
                    sub = "%s - %s" % (v["VACCINATIONTYPE"], v["ANIMALNAME"])
                    tit = "%s - %s %s %s" % (v["VACCINATIONTYPE"], v["SHELTERCODE"], v["ANIMALNAME"], v["COMMENTS"])
                    events.append({ 
                        "title": sub, 
                        "allDay": True, 
                        "start": v["DATEREQUIRED"], 
                        "tooltip": tit, 
                        "icon": "vaccination",
                        "link": "animal_vaccination?id=%d" % v["ANIMALID"] })
                for v in extmedical.get_vaccinations_expiring_two_dates(dbo, post["start"], post["end"], session.locationfilter, session.siteid):
                    sub = "%s - %s" % (v["VACCINATIONTYPE"], v["ANIMALNAME"])
                    tit = "%s - %s %s %s" % (v["VACCINATIONTYPE"], v["SHELTERCODE"], v["ANIMALNAME"], v["COMMENTS"])
                    events.append({ 
                        "title": sub, 
                        "allDay": True, 
                        "start": v["DATEEXPIRES"], 
                        "tooltip": tit, 
                        "icon": "vaccination",
                        "link": "animal_vaccination?id=%d" % v["ANIMALID"] })
            if "m" in ev and users.check_permission_bool(session, users.VIEW_MEDICAL):
                for m in extmedical.get_treatments_two_dates(dbo, post["start"], post["end"], session.locationfilter, session.siteid):
                    sub = "%s - %s" % (m["TREATMENTNAME"], m["ANIMALNAME"])
                    tit = "%s - %s %s %s %s" % (m["TREATMENTNAME"], m["SHELTERCODE"], m["ANIMALNAME"], m["DOSAGE"], m["COMMENTS"])
                    events.append({ 
                        "title": sub, 
                        "allDay": True, 
                        "start": m["DATEREQUIRED"], 
                        "tooltip": tit, 
                        "icon": "medical",
                        "link": "animal_medical?id=%d" % m["ANIMALID"] })
            if "t" in ev and users.check_permission_bool(session, users.VIEW_TEST):
                for t in extmedical.get_tests_two_dates(dbo, post["start"], post["end"], session.locationfilter, session.siteid):
                    sub = "%s - %s" % (t["TESTNAME"], t["ANIMALNAME"])
                    tit = "%s - %s %s %s" % (t["TESTNAME"], t["SHELTERCODE"], t["ANIMALNAME"], t["COMMENTS"])
                    events.append({ 
                        "title": sub, 
                        "allDay": True, 
                        "start": t["DATEREQUIRED"], 
                        "tooltip": tit, 
                        "icon": "test",
                        "link": "animal_test?id=%d" % t["ANIMALID"] })
            if "p" in ev and users.check_permission_bool(session, users.VIEW_DONATION):
                for p in financial.get_donations_due_two_dates(dbo, post["start"], post["end"]):
                    sub = "%s - %s" % (p["DONATIONNAME"], p["OWNERNAME"])
                    tit = "%s - %s %s %s" % (p["DONATIONNAME"], p["OWNERNAME"], html.format_currency(l, p["DONATION"]), p["COMMENTS"])
                    events.append({ 
                        "title": sub, 
                        "allDay": True, 
                        "start": p["DATEDUE"], 
                        "tooltip": tit, 
                        "icon": "donation",
                        "link": "person_donations?id=%d" % p["OWNERID"] })
            if "o" in ev and users.check_permission_bool(session, users.VIEW_INCIDENT):
                for o in extanimalcontrol.get_followup_two_dates(dbo, post["start"], post["end"]):
                    sub = "%s - %s" % (o["INCIDENTNAME"], o["OWNERNAME"])
                    tit = "%s - %s %s, %s" % (o["INCIDENTNAME"], o["OWNERNAME"], o["DISPATCHADDRESS"], o["CALLNOTES"])
                    events.append({ 
                        "title": sub, 
                        "allDay": False, 
                        "start": o["FOLLOWUPDATETIME"], 
                        "tooltip": tit, 
                        "icon": "call",
                        "link": "incident?id=%d" % o["ACID"] })
            if "r" in ev and users.check_permission_bool(session, users.VIEW_TRANSPORT):
                for r in extmovement.get_transport_two_dates(dbo, post["start"], post["end"]):
                    sub = "%s - %s" % (r["ANIMALNAME"], r["SHELTERCODE"])
                    tit = "%s - %s :: %s, %s" % (r["DRIVEROWNERNAME"], r["PICKUPOWNERADDRESS"], r["DROPOFFOWNERADDRESS"], r["COMMENTS"])
                    allday = False
                    if r["PICKUPDATETIME"].hour == 0 and r["PICKUPDATETIME"].minute == 0:
                        allday = True
                    events.append({ 
                        "title": sub, 
                        "allDay": allday, 
                        "start": r["PICKUPDATETIME"], 
                        "end": r["DROPOFFDATETIME"],
                        "tooltip": tit, 
                        "icon": "transport",
                        "link": "animal_transport?id=%d" % r["ANIMALID"]})
            if "l" in ev and users.check_permission_bool(session, users.VIEW_TRAPLOAN):
                for l in extanimalcontrol.get_traploan_two_dates(dbo, post["start"], post["end"]):
                    sub = "%s - %s" % (l["TRAPTYPENAME"], l["OWNERNAME"])
                    tit = "%s - %s %s, %s" % (l["TRAPTYPENAME"], l["OWNERNAME"], l["TRAPNUMBER"], l["COMMENTS"])
                    events.append({ 
                        "title": sub, 
                        "allDay": True, 
                        "start": l["RETURNDUEDATE"], 
                        "tooltip": tit, 
                        "icon": "traploan",
                        "link": "person_traploan?id=%d" % l["OWNERID"]})
            al.debug("calendarview found %d events (%s->%s)" % (len(events), post["start"], post["end"]), "code.calendarview", dbo)
            return html.json(events)

class change_password:
    def GET(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        al.debug("%s change password screen" % session.user, "code.change_password", dbo)
        s = html.header("", session)
        c = html.controller_bool("ismaster", smcom.active() and dbo.database == session.user)
        c += html.controller_bool("issuggest", post.integer("suggest") == 1)
        c += html.controller_str("username", session.user)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("change_password", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(oldpassword = "", newpassword = ""), session.locale)
        oldpass = post["oldpassword"]
        newpass = post["newpassword"]
        al.debug("%s changed password" % (session.user), "code.change_password", dbo)
        users.change_password(dbo, session.user, oldpass, newpass)

class change_user_settings:
    def GET(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        al.debug("%s change user settings screen" % session.user, "code.change_user_settings", dbo)
        s = html.header("", session)
        c = html.controller_json("user", users.get_users(dbo, session.user))
        c += html.controller_json("locales", extlookups.LOCALES)
        c += html.controller_str("sigtype", ELECTRONIC_SIGNATURES)
        c += html.controller_json("themes", extlookups.VISUAL_THEMES)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("change_user_settings", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(theme = "", locale = "", realname = "", email = ""), session.locale)
        theme = post["theme"]
        locale = post["locale"]
        realname = post["realname"]
        email = post["email"]
        signature = post["signature"]
        al.debug("%s changed settings: theme=%s, locale=%s, realname=%s, email=%s" % (session.user, theme, locale, realname, email), "code.change_password", dbo)
        users.update_user_settings(dbo, session.user, email, realname, locale, theme, signature)
        users.update_session(session)

class citations:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_CITATION)
        l = session.locale
        dbo = session.dbo
        post = utils.PostedData(web.input(filter = "unpaid"), session.locale)
        title = ""
        citations = []
        if post["filter"] == "unpaid":
            title = _("Unpaid Fines", l)
            citations = financial.get_unpaid_fines(dbo)
        al.debug("got %d citations" % len(citations), "code.citations", dbo)
        s = html.header(title, session)
        c = html.controller_str("name", "citations")
        c += html.controller_str("title", title)
        c += html.controller_json("rows", citations)
        c += html.controller_json("citationtypes", extlookups.get_citation_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("citations", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_CITATION)
            return financial.insert_citation_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_CITATION)
            financial.update_citation_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_CITATION)
            for lid in post.integer_list("ids"):
                financial.delete_citation(session.dbo, session.user, lid)

class csvimport:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.USE_SQL_INTERFACE)
        s = html.header("", session)
        s += html.controller("")
        s += html.footer()
        return full_or_json("csvimport", s, "", False)

    def POST(self):
        utils.check_loggedin(session, web)
        utils.check_locked_db(session)
        dbo = session.dbo
        l = session.locale
        post = utils.PostedData(web.input(createmissinglookups = "", cleartables = "", checkduplicates = "", filechooser={}), session.locale)
        users.check_permission(session, users.USE_SQL_INTERFACE)
        web.header("Content-Type", "text/html")
        try:
            errors = extcsvimport.csvimport(dbo, post.filedata(), 
                post.boolean("createmissinglookups") == 1, post.boolean("cleartables") == 1, post.boolean("checkduplicates") == 1)
            title = _("Import a CSV file", l)
            s = html.header(title, session)
            c = html.controller_json("errors", errors)
            s += html.controller(c)
            s += html.footer()
            return full_or_json("csvimport", s, c, False)
        except Exception,err:
            al.error("error in CSV data: %s" % str(err), "csvimport.csvimport", dbo, sys.exc_info())
            if str(err).find("no attribute 'value'") != -1:
                err = "No CSV file was uploaded"
            title = _("Import a CSV file", l)
            s = html.header(title, session)
            c = html.controller_str("error", str(err))
            s += html.controller(c)
            s += html.footer()
            return full_or_json("csvimport", s, c, False)

class diary_edit:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.EDIT_ALL_DIARY_NOTES)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0, filter="uncompleted", newnote="0"), session.locale)
        dfilter = post["filter"]
        if dfilter == "uncompleted":
            diaries = extdiary.get_uncompleted_upto_today(dbo)
        elif dfilter == "completed":
            diaries = extdiary.get_completed_upto_today(dbo)
        elif dfilter == "future":
            diaries = extdiary.get_future(dbo)
        elif dfilter == "all":
            diaries = extdiary.get_all_upto_today(dbo)
        al.debug("got %d diaries, filter was %s" % (len(diaries), dfilter), "code.diary_edit", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", diaries)
        c += html.controller_bool("newnote", post.integer("newnote") == 1)
        c += html.controller_str("name", "diary_edit")
        c += html.controller_json("forlist", users.get_users_and_roles(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("diary", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_DIARY)
            return extdiary.insert_diary_from_form(session.dbo, session.user, extdiary.NO_LINK, 0, post)
        elif mode == "update":
            users.check_permission(session, users.EDIT_ALL_DIARY_NOTES)
            extdiary.update_diary_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_DIARY)
            for did in post.integer_list("ids"):
                extdiary.delete_diary(session.dbo, session.user, did)
        elif mode == "complete":
            users.check_permission(session, users.BULK_COMPLETE_NOTES)
            for did in post.integer_list("ids"):
                extdiary.complete_diary_note(session.dbo, session.user, did)

class diary_edit_my:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.EDIT_MY_DIARY_NOTES)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0, filter="uncompleted", newnote="0"), session.locale)
        userfilter = session.user.strip()
        dfilter = post["filter"]
        if dfilter == "uncompleted":
            diaries = extdiary.get_uncompleted_upto_today(dbo, userfilter)
        elif dfilter == "completed":
            diaries = extdiary.get_completed_upto_today(dbo, userfilter)
        elif dfilter == "future":
            diaries = extdiary.get_future(dbo, userfilter)
        elif dfilter == "all":
            diaries = extdiary.get_all_upto_today(dbo, userfilter)
        al.debug("got %d diaries (%s), filter was %s" % (len(diaries), userfilter, dfilter), "code.diary_edit_my", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", diaries)
        c += html.controller_bool("newnote", post.integer("newnote") == 1)
        c += html.controller_str("name", "diary_edit_my")
        c += html.controller_json("forlist", users.get_users_and_roles(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("diary", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_DIARY)
            extdiary.insert_diary_from_form(session.dbo, session.user, extdiary.NO_LINK, 0, post)
        elif mode == "update":
            users.check_permission(session, users.EDIT_MY_DIARY_NOTES)
            extdiary.update_diary_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_DIARY)
            for did in post.integer_list("ids"):
                extdiary.delete_diary(session.dbo, session.user, did)
        elif mode == "complete":
            users.check_permission(session, users.BULK_COMPLETE_NOTES)
            for did in post.integer_list("ids"):
                extdiary.complete_diary_note(session.dbo, session.user, did)

class diarytask:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.EDIT_DIARY_TASKS)
        l = session.locale
        dbo = session.dbo
        post = utils.PostedData(web.input(taskid = 0), session.locale)
        taskid = post.integer("taskid")
        taskname = extdiary.get_diarytask_name(dbo, taskid)
        diarytaskdetail = extdiary.get_diarytask_details(dbo, taskid)
        title = _("Diary task: {0}", l).format(taskname)
        al.debug("got %d diary task details" % len(diarytaskdetail), "code.diarytask", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", diarytaskdetail)
        c += html.controller_int("taskid", taskid)
        c += html.controller_str("taskname", taskname)
        c += html.controller_str("title", title)
        c += html.controller_json("forlist", users.get_users_and_roles(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("diarytask", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(mode="create", tasktype="ANIMAL", taskid="0", id="0", seldate=""), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.EDIT_DIARY_TASKS)
            return extdiary.insert_diarytaskdetail_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.EDIT_DIARY_TASKS)
            extdiary.update_diarytaskdetail_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.EDIT_DIARY_TASKS)
            for did in post.integer_list("ids"):
                extdiary.delete_diarytaskdetail(session.dbo, session.user, did)
        elif mode == "exec":
            users.check_permission(session, users.ADD_DIARY)
            extdiary.execute_diary_task(dbo, session.user, post["tasktype"], post.integer("taskid"), post.integer("id"), post.date("seldate"))

class diarytasks:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.EDIT_DIARY_TASKS)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        diarytaskhead = extdiary.get_diarytasks(dbo)
        al.debug("got %d diary tasks" % len(diarytaskhead), "code.diarytasks", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", diarytaskhead)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("diarytasks", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.EDIT_DIARY_TASKS)
            return extdiary.insert_diarytaskhead_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.EDIT_DIARY_TASKS)
            extdiary.update_diarytaskhead_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.EDIT_DIARY_TASKS)
            for did in post.integer_list("ids"):
                extdiary.delete_diarytask(session.dbo, session.user, did)

class document_gen:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.GENERATE_DOCUMENTS)
        dbo = session.dbo
        post = utils.PostedData(web.input(mode = "ANIMAL", id = "0", template = "0"), session.locale)
        mode = post["mode"]
        if post["id"] == "" or post["id"] == "0": raise utils.ASMValidationError("no id parameter")
        template = post.integer("template")
        templatename = dbfs.get_name_for_id(dbo, template)
        title = templatename
        loglinktype = extlog.ANIMAL
        al.debug("generating %s document for %d" % (mode, post.integer("id")), "code.document_gen", dbo)
        logid = post.integer("id")
        if mode == "ANIMAL":
            loglinktype = extlog.ANIMAL
            content = wordprocessor.generate_animal_doc(dbo, template, post.integer("id"), session.user)
        elif mode == "ANIMALCONTROL":
            loglinktype = extlog.ANIMALCONTROL
            content = wordprocessor.generate_animalcontrol_doc(dbo, template, post.integer("id"), session.user)
        elif mode == "PERSON":
            loglinktype = extlog.PERSON
            content = wordprocessor.generate_person_doc(dbo, template, post.integer("id"), session.user)
        elif mode == "DONATION":
            loglinktype = extlog.PERSON
            logid = financial.get_donation(dbo, post.integer_list("id")[0])["OWNERID"]
            content = wordprocessor.generate_donation_doc(dbo, template, post.integer_list("id"), session.user)
        elif mode == "LICENCE":
            loglinktype = extlog.PERSON
            logid = financial.get_licence(dbo, post.integer("id"))["OWNERID"]
            content = wordprocessor.generate_licence_doc(dbo, template, post.integer("id"), session.user)
        elif mode == "MOVEMENT":
            loglinktype = extlog.PERSON
            logid = extmovement.get_movement(dbo, post.integer("id"))["OWNERID"]
            content = wordprocessor.generate_movement_doc(dbo, template, post.integer("id"), session.user)
        if configuration.generate_document_log(dbo) and configuration.generate_document_log_type(dbo) > 0:
            extlog.add_log(dbo, session.user, loglinktype, logid, configuration.generate_document_log_type(dbo), _("Generated document '{0}'").format(templatename))
        if templatename.endswith(".html"):
            web.header("Content-Type", "text/html")
            web.header("Cache-Control", "no-cache")
            return html.tinymce_header(title, "document_edit.js", configuration.js_window_print(dbo)) + \
                html.tinymce_main(dbo.locale, "document_gen", recid=post["id"], mode=post["mode"], \
                    template=post["template"], content=utils.escape_tinymce(content))
        elif templatename.endswith(".odt"):
            web.header("Content-Type", "application/vnd.oasis.opendocument.text")
            web.header("Content-Disposition", "attach; filename=\"%s\"" % templatename)
            web.header("Cache-Control", "no-cache")
            return content

    def POST(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.GENERATE_DOCUMENTS)
        dbo = session.dbo
        l = session.locale
        post = utils.PostedData(web.input(recid = 0, mode = "ANIMAL", template = 0, document = "", savemode="save"), session.locale)
        mode = post["mode"]
        template = post.integer("template")
        tempname = dbfs.get_name_for_id(dbo, template)
        if post["savemode"] == "save":
            recid = post.integer("recid")
            if mode == "ANIMAL":
                tempname += " - " + extanimal.get_animal_namecode(dbo, recid)
                extmedia.create_document_media(dbo, session.user, extmedia.ANIMAL, recid, tempname, post["document"])
                raise web.seeother("animal_media?id=%d" % recid)
            elif mode == "ANIMALCONTROL":
                tempname += " - " + utils.padleft(recid, 6)
                extmedia.create_document_media(dbo, session.user, extmedia.ANIMALCONTROL, recid, tempname, post["document"])
                raise web.seeother("incident_media?id=%d" % recid)
            elif mode == "PERSON":
                tempname += " - " + extperson.get_person_name(dbo, recid)
                extmedia.create_document_media(dbo, session.user, extmedia.PERSON, recid, tempname, post["document"])
                raise web.seeother("person_media?id=%d" % recid)
            elif mode == "DONATION":
                d = financial.get_donations_by_ids(dbo, post.integer_list("recid"))
                if len(d) == 0:
                    raise utils.ASMValidationError("list '%s' does not contain valid ids" % recid)
                ownerid = d[0]["OWNERID"]
                tempname += " - " + extperson.get_person_name(dbo, ownerid)
                extmedia.create_document_media(dbo, session.user, extmedia.PERSON, ownerid, tempname, post["document"])
                raise web.seeother("person_media?id=%d" % ownerid)
            elif mode == "LICENCE":
                l = financial.get_licence(dbo, recid)
                if l is None:
                    raise utils.ASMValidationError("%d is not a valid licence id" % recid)
                ownerid = l["OWNERID"]
                tempname += " - " + extperson.get_person_name(dbo, ownerid)
                extmedia.create_document_media(dbo, session.user, extmedia.PERSON, recid, tempname, post["document"])
                raise web.seeother("person_media?id=%d" % ownerid)
            elif mode == "MOVEMENT":
                m = extmovement.get_movement(dbo, recid)
                if m is None:
                    raise utils.ASMValidationError("%d is not a valid movement id" % recid)
                animalid = m["ANIMALID"]
                ownerid = m["OWNERID"]
                tempname = "%s - %s::%s" % (tempname, extanimal.get_animal_namecode(dbo, animalid), extperson.get_person_name(dbo, ownerid))
                extmedia.create_document_media(dbo, session.user, extmedia.PERSON, ownerid, tempname, post["document"])
                extmedia.create_document_media(dbo, session.user, extmedia.ANIMAL, animalid, tempname, post["document"])
                raise web.seeother("person_media?id=%d" % ownerid)
            else:
                raise utils.ASMValidationError("Mode '%s' is invalid, cannot save" % mode)
        elif post["savemode"] == "pdf":
            web.header("Content-Type", "application/pdf")
            disposition = configuration.pdf_inline(dbo) and "inline; filename=\"doc.pdf\"" or "attachment; filename=\"doc.pdf\""
            web.header("Content-Disposition", disposition)
            return utils.html_to_pdf(post["document"], BASE_URL, MULTIPLE_DATABASES and dbo.database or "")
        elif post["savemode"] == "print":
            web.header("Content-Type", "text/html")
            return "%s%s%s" % (html.tinymce_print_header(_("Print Preview", l)), post["document"], "</body></html>")

class document_edit:
    def GET(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(template = 0), session.locale)
        template = post.integer("template")
        templatename = dbfs.get_name_for_id(dbo, template)
        if templatename == "": raise web.notfound()
        title = templatename
        al.debug("editing %s" % templatename, "code.document_edit", dbo)
        if templatename.endswith(".html"):
            content = utils.escape_tinymce(dbfs.get_string_id(dbo, template))
            web.header("Content-Type", "text/html")
            web.header("Cache-Control", "no-cache")
            return html.tinymce_header(title, "document_edit.js", configuration.js_window_print(dbo)) + \
                html.tinymce_main(dbo.locale, "document_edit", template=template, content=content)
        elif templatename.endswith(".odt"):
            content = dbfs.get_string_id(dbo, template)
            web.header("Content-Type", "application/vnd.oasis.opendocument.text")
            web.header("Cache-Control", "no-cache")
            return content

    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        l = session.locale
        post = utils.PostedData(web.input(template = "", document = "", savemode = "save"), session.locale)
        if post["savemode"] == "save":
            template = post.integer("template")
            templatename = dbfs.get_name_for_id(dbo, template)
            dbfs.put_string_id(dbo, template, templatename, post["document"])
            raise web.seeother("document_templates")
        elif post["savemode"] == "pdf":
            web.header("Content-Type", "application/pdf")
            disposition = configuration.pdf_inline(dbo) and "inline; filename=\"doc.pdf\"" or "attachment; filename=\"doc.pdf\""
            web.header("Content-Disposition", disposition)
            return utils.html_to_pdf(post["document"], BASE_URL, MULTIPLE_DATABASES and dbo.database or "")
        elif post["savemode"] == "print":
            web.header("Content-Type", "text/html")
            return "%s%s%s" % (html.tinymce_print_header(_("Print Preview", l)), post["document"], "</body></html>")

class document_media_edit:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MEDIA)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0, redirecturl = "/main"), session.locale)
        lastmod, medianame, mimetype, filedata = extmedia.get_media_file_data(session.dbo, post.integer("id"))
        al.debug("editing media %d" % post.integer("id"), "code.document_media_edit", dbo)
        title = medianame
        web.header("Content-Type", "text/html")
        return html.tinymce_header(title, "document_edit.js", configuration.js_window_print(dbo), False, extmedia.has_signature(dbo, post.integer("id"))) + \
            html.tinymce_main(dbo.locale, "document_media_edit", mediaid=post.integer("id"), redirecturl=post["redirecturl"], \
                content=utils.escape_tinymce(filedata))

    def POST(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.CHANGE_MEDIA)
        dbo = session.dbo
        l = session.locale
        post = utils.PostedData(web.input(mediaid = 0, redirecturl = "main", document = "", savemode = "save"), session.locale)
        if post["savemode"] == "save":
            extmedia.update_file_content(dbo, session.user, post.integer("mediaid"), post["document"])
            raise web.seeother(post["redirecturl"])
        elif post["savemode"] == "pdf":
            web.header("Content-Type", "application/pdf")
            disposition = configuration.pdf_inline(dbo) and "inline; filename=\"doc.pdf\"" or "attachment; filename=\"doc.pdf\""
            web.header("Content-Disposition", disposition)
            return utils.html_to_pdf(post["document"], BASE_URL, MULTIPLE_DATABASES and dbo.database or "")
        elif post["savemode"] == "print":
            web.header("Content-Type", "text/html")
            return "%s%s%s" % (html.tinymce_print_header(_("Print Preview", l)), post["document"], "</body></html>")

class document_repository:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_REPO_DOCUMENT)
        dbo = session.dbo
        post = utils.PostedData(web.input(dbfsid = 0), session.locale)
        if post.integer("dbfsid") != 0:
            name = dbfs.get_name_for_id(dbo, post.integer("dbfsid"))
            mimetype, encoding = mimetypes.guess_type("file://" + name, strict=False)
            web.header("Content-Type", mimetype)
            web.header("Content-Disposition", "attachment; filename=\"%s\"" % name)
            return dbfs.get_string_id(dbo, post.integer("dbfsid"))
        else:
            documents = dbfs.get_document_repository(dbo)
            al.debug("got %d documents in repository" % len(documents), "code.document_repository", dbo)
            s = html.header("", session)
            c = html.controller_json("rows", documents)
            s += html.controller(c)
            s += html.footer()
            return full_or_json("document_repository", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(mode="create", filechooser={}), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_REPO_DOCUMENT)
            dbfs.upload_document_repository(dbo, post["path"], post.data.filechooser)
            raise web.seeother("document_repository")
        if mode == "delete":
            users.check_permission(session, users.DELETE_REPO_DOCUMENT)
            for i in post.integer_list("ids"):
                dbfs.delete_id(dbo, i)

class document_templates:
    def GET(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        templates = dbfs.get_document_templates(dbo)
        al.debug("got %d document templates" % len(templates), "code.document_templates", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", templates)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("document_templates", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        username = session.user
        post = utils.PostedData(web.input(mode="create", template="", filechooser={}), session.locale)
        mode = post["mode"]
        if mode == "create":
            return dbfs.create_document_template(dbo, username, post["template"])
        elif mode == "createodt":
            fn = post.filename()
            if post["path"] != "": fn = post["path"] + "/" + fn
            dbfs.create_document_template(dbo, username, fn, ".odt", post.filedata())
            raise web.seeother("document_templates")
        elif mode == "clone":
            for t in post.integer_list("ids"):
                return dbfs.clone_document_template(dbo, username, t, post["template"])
        elif mode == "delete":
            for t in post.integer_list("ids"):
                dbfs.delete_document_template(dbo, username, t)
        elif mode == "rename":
            dbfs.rename_document_template(dbo, username, post.integer("dbfsid"), post["newname"])

class donation:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_DONATION)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0, offset = "m0"), session.locale)
        donations = financial.get_donations(dbo, post["offset"])
        al.debug("got %d donations" % (len(donations)), "code.donation", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "donation")
        c += html.controller_json("donationtypes", extlookups.get_donation_types(dbo))
        c += html.controller_json("accounts", financial.get_accounts(dbo))
        c += html.controller_json("paymenttypes", extlookups.get_payment_types(dbo))
        c += html.controller_json("frequencies", extlookups.get_donation_frequencies(dbo))
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_json("rows", donations)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("donations", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        dbo = session.dbo
        if mode == "create":
            users.check_permission(session, users.ADD_DONATION)
            return financial.insert_donation_from_form(dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_DONATION)
            financial.update_donation_from_form(dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_DONATION)
            for did in post.integer_list("ids"):
                financial.delete_donation(dbo, session.user, did)
        elif mode == "receive":
            users.check_permission(session, users.CHANGE_DONATION)
            for did in post.integer_list("ids"):
                financial.receive_donation(dbo, session.user, did)
        elif mode == "nextreceipt":
            return financial.get_next_receipt_number(dbo)
        elif mode == "personmovements":
            users.check_permission(session, users.VIEW_MOVEMENT)
            web.header("Content-Type", "application/json")
            return html.json(extmovement.get_person_movements(dbo, post.integer("personid")))

class donation_receive:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_DONATION)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        al.debug("receiving donation", "code.donation_receive", dbo)
        c = html.controller_json("donationtypes", extlookups.get_donation_types(dbo))
        c += html.controller_json("paymenttypes", extlookups.get_payment_types(dbo))
        c += html.controller_json("accounts", financial.get_accounts(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("donation_receive", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_DONATION)
            return financial.insert_donations_from_form(session.dbo, session.user, post, post["received"], True, post["person"], post["animal"], False)

class foundanimal:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_FOUND_ANIMAL)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extlostfound.get_foundanimal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        al.debug("open found animal %s %s %s" % (a["AGEGROUP"], a["SPECIESNAME"], a["OWNERNAME"]), "code.foundanimal", dbo)
        s = html.header("", session)
        c = html.controller_json("animal", a)
        c += html.controller_str("name", "foundanimal")
        c += html.controller_json("additional", extadditional.get_additional_fields(dbo, a["ID"], "foundanimal"))
        c += html.controller_json("agegroups", configuration.age_groups(dbo))
        if users.check_permission_bool(session, users.VIEW_AUDIT_TRAIL):
            c += html.controller_json("audit", audit.get_audit_for_link(dbo, "animalfound", a["ID"]))
        c += html.controller_json("breeds", extlookups.get_breeds_by_species(dbo))
        c += html.controller_json("colours", extlookups.get_basecolours(dbo))
        c += html.controller_json("logtypes", extlookups.get_log_types(dbo))
        c += html.controller_json("sexes", extlookups.get_sexes(dbo))
        c += html.controller_json("species", extlookups.get_species(dbo))
        c += html.controller_json("tabcounts", extlostfound.get_foundanimal_satellite_counts(dbo, a["LFID"])[0])
        s += html.controller(c)
        s += html.footer()
        return full_or_json("lostfound", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        l = session.locale
        dbo = session.dbo
        post = utils.PostedData(web.input(mode="save"), session.locale)
        mode = post["mode"]
        if mode == "save":
            users.check_permission(session, users.CHANGE_FOUND_ANIMAL)
            extlostfound.update_foundanimal_from_form(dbo, post, session.user)
        elif mode == "email":
            users.check_permission(session, users.EMAIL_PERSON)
            if not extlostfound.send_email_from_form(dbo, session.user, post):
                raise utils.ASMError(_("Failed sending email", l))
        elif mode == "delete":
            users.check_permission(session, users.DELETE_FOUND_ANIMAL)
            extlostfound.delete_foundanimal(dbo, session.user, post.integer("id"))
        elif mode == "toanimal":
            users.check_permission(session, users.ADD_ANIMAL)
            return str(extlostfound.create_animal_from_found(dbo, session.user, post.integer("id")))
        elif mode == "towaitinglist":
            users.check_permission(session, users.ADD_WAITING_LIST)
            return str(extlostfound.create_waitinglist_from_found(dbo, session.user, post.integer("id")))

class foundanimal_diary:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_DIARY)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extlostfound.get_foundanimal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        diaries = extdiary.get_diaries(dbo, extdiary.FOUNDANIMAL, post.integer("id"))
        al.debug("got %d diaries for found animal %s %s %s" % (len(diaries), a["AGEGROUP"], a["SPECIESNAME"], a["OWNERNAME"]), "code.foundanimal_diary", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", diaries)
        c += html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extlostfound.get_foundanimal_satellite_counts(dbo, a["LFID"])[0])
        c += html.controller_str("name", "foundanimal_diary")
        c += html.controller_int("linkid", a["LFID"])
        c += html.controller_json("forlist", users.get_users_and_roles(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("diary", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_DIARY)
            return extdiary.insert_diary_from_form(session.dbo, session.user, extdiary.FOUNDANIMAL, post.integer("linkid"), post)
        elif mode == "update":
            users.check_permission(session, users.EDIT_ALL_DIARY_NOTES)
            extdiary.update_diary_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_DIARY)
            for did in post.integer_list("ids"):
                extdiary.delete_diary(session.dbo, session.user, did)
        elif mode == "complete":
            users.check_permission(session, users.BULK_COMPLETE_NOTES)
            for did in post.integer_list("ids"):
                extdiary.complete_diary_note(session.dbo, session.user, did)

class foundanimal_find:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_FOUND_ANIMAL)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        c = html.controller_json("agegroups", configuration.age_groups(dbo))
        c += html.controller_json("colours", extlookups.get_basecolours(dbo))
        c += html.controller_str("name", "foundanimal_find")
        c += html.controller_json("species", extlookups.get_species(dbo))
        c += html.controller_json("breeds", extlookups.get_breeds_by_species(dbo))
        c += html.controller_json("sexes", extlookups.get_sexes(dbo))
        c += html.controller_str("mode", "found")
        s += html.controller(c)
        s += html.footer()
        return full_or_json("lostfound_find", s, c, post["json"] == "true")

class foundanimal_find_results:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_FOUND_ANIMAL)
        dbo = session.dbo
        l = session.locale
        post = utils.PostedData(web.input(mode = ""), session.locale)
        results = extlostfound.get_foundanimal_find_advanced(dbo, post.data, configuration.record_search_limit(dbo))
        resultsmessage = _("Find found animal returned {0} results.", l).format(len(results))
        al.debug("found %d results for %s" % (len(results), str(web.ctx.query)), "code.foundanimal_find_results", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", results)
        c += html.controller_str("name", "foundanimal_find_results")
        c += html.controller_str("resultsmessage", resultsmessage)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("lostfound_find_results", s, c, post["json"] == "true")

class foundanimal_log:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_LOG)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0, filter = -2), session.locale)
        logfilter = post.integer("filter")
        if logfilter == -2: logfilter = configuration.default_log_filter(dbo)
        a = extlostfound.get_foundanimal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        logs = extlog.get_logs(dbo, extlog.FOUNDANIMAL, post.integer("id"), logfilter)
        s = html.header("", session)
        c = html.controller_str("name", "foundanimal_log")
        c += html.controller_int("linkid", post.integer("id"))
        c += html.controller_int("filter", logfilter)
        c += html.controller_json("rows", logs)
        c += html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extlostfound.get_foundanimal_satellite_counts(dbo, a["LFID"])[0])
        c += html.controller_json("logtypes", extlookups.get_log_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("log", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_LOG)
            return extlog.insert_log_from_form(session.dbo, session.user, extlog.FOUNDANIMAL, post.integer("linkid"), post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_LOG)
            extlog.update_log_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_LOG)
            for lid in post.integer_list("ids"):
                extlog.delete_log(session.dbo, session.user, lid)

class foundanimal_media:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MEDIA)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extlostfound.get_foundanimal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        m = extmedia.get_media(dbo, extmedia.FOUNDANIMAL, post.integer("id"))
        al.debug("got %d media for found animal %s %s %s" % (len(m), a["AGEGROUP"], a["SPECIESNAME"], a["OWNERNAME"]), "code.foundanimal_media", dbo)
        s = html.header("", session)
        c = html.controller_json("media", m)
        c += html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extlostfound.get_foundanimal_satellite_counts(dbo, a["LFID"])[0])
        c += html.controller_bool("showpreferred", False)
        c += html.controller_int("linkid", post.integer("id"))
        c += html.controller_int("linktypeid", extmedia.FOUNDANIMAL)
        c += html.controller_str("name", self.__class__.__name__)
        c += html.controller_str("sigtype", ELECTRONIC_SIGNATURES)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("media", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create", filechooser={}, linkid="0", base64image = "", _unicode=False), session.locale)
        mode = post["mode"]
        dbo = session.dbo
        l = session.locale
        linkid = post.integer("linkid")
        if mode == "create":
            users.check_permission(session, users.ADD_MEDIA)
            extmedia.attach_file_from_form(session.dbo, session.user, extmedia.FOUNDANIMAL, linkid, post)
            raise web.seeother("foundanimal_media?id=%d" % linkid)
        elif mode == "createdoc":
            users.check_permission(session, users.ADD_MEDIA)
            mediaid = extmedia.create_blank_document_media(session.dbo, session.user, extmedia.FOUNDANIMAL, linkid)
            raise web.seeother("document_media_edit?id=%d&redirecturl=foundanimal_media?id=%d" % (mediaid, linkid))
        elif mode == "createlink":
            users.check_permission(session, users.ADD_MEDIA)
            mediaid = extmedia.attach_link_from_form(session.dbo, session.user, extmedia.FOUNDANIMAL, linkid, post)
            raise web.seeother("foundanimal_media?id=%d" % linkid)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MEDIA)
            extmedia.update_media_notes(session.dbo, session.user, post.integer("mediaid"), post["comments"])
        elif mode == "delete":
            users.check_permission(session, users.DELETE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.delete_media(session.dbo, session.user, mid)
        elif mode == "email":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                content = dbfs.get_string(dbo, m["MEDIANAME"])
                if m["MEDIANAME"].endswith("html"):
                    content = utils.fix_relative_document_uris(content, BASE_URL, MULTIPLE_DATABASES and dbo.database or "")
                utils.send_email(dbo, configuration.email(dbo), emailadd, "", m["MEDIANOTES"], post["emailnote"], "html", content, m["MEDIANAME"])
            return emailadd
        elif mode == "emailpdf":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                if not m["MEDIANAME"].endswith("html"): continue
                content = dbfs.get_string(dbo, m["MEDIANAME"])
                contentpdf = utils.html_to_pdf(content, BASE_URL, MULTIPLE_DATABASES and dbo.database or "")
                utils.send_email(dbo, configuration.email(dbo), emailadd, "", m["MEDIANOTES"], "", "plain", contentpdf, "document.pdf")
            return emailadd
        elif mode == "emailsign":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            body = []
            body.append(post["emailnote"] + "\n\n")
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                if not m["MEDIANAME"].endswith("html"): continue
                body.append(m["MEDIANOTES"])
                body.append("%s?account=%s&method=sign_document&formid=%d" % (SERVICE_URL, dbo.database, mid))
                body.append("")
            utils.send_email(dbo, configuration.email(dbo), emailadd, "", _("Document signing request", l), "\n".join(body), "plain")
            return emailadd
        elif mode == "sign":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.sign_document(session.dbo, session.user, mid, post["sig"], post["signdate"])
        elif mode == "signpad":
            configuration.signpad_ids(session.dbo, session.user, post["ids"])
        elif mode == "rotateclock":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.rotate_media(session.dbo, session.user, mid, True)
        elif mode == "rotateanti":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.rotate_media(session.dbo, session.user, mid, False)
        elif mode == "web":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_web_preferred(session.dbo, session.user, mid)
        elif mode == "video":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_video_preferred(session.dbo, session.user, mid)
        elif mode == "doc":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_doc_preferred(session.dbo, session.user, mid)

class foundanimal_new:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_FOUND_ANIMAL)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        c = html.controller_json("agegroups", configuration.age_groups(dbo))
        c += html.controller_json("additional", extadditional.get_additional_fields(dbo, 0, "foundanimal"))
        c += html.controller_json("colours", extlookups.get_basecolours(dbo))
        c += html.controller_json("species", extlookups.get_species(dbo))
        c += html.controller_json("breeds", extlookups.get_breeds_by_species(dbo))
        c += html.controller_json("sexes", extlookups.get_sexes(dbo))
        c += html.controller_str("name", "foundanimal_new")
        s += html.controller(c)
        s += html.footer()
        return full_or_json("lostfound_new", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_FOUND_ANIMAL)
        utils.check_locked_db(session)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        return str(extlostfound.insert_foundanimal_from_form(dbo, post, session.user))

class giftaid_hmrc_spreadsheet:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_DONATION)
        dbo = session.dbo
        post = utils.PostedData(web.input(fromdate = "", todate = ""), session.locale)
        fromdate = post["fromdate"]
        todate = post["todate"]
        if fromdate == "":
            s = html.header("", session)
            s += html.footer()
            return full_or_json("giftaid_hmrc_spreadsheet", s, "", False)
        else:
            al.debug("generating HMRC giftaid spreadsheet for %s -> %s" % (fromdate, todate), "code.giftaid_hmrc_spreadsheet", dbo)
            web.header("Content-Type", "application/vnd.oasis.opendocument.spreadsheet")
            web.header("Cache-Control", "no-cache")
            web.header("Content-Disposition", "attachment; filename=\"giftaid.ods\"")
            return financial.giftaid_spreadsheet(dbo, PATH, post.date("fromdate"), post.date("todate"))

class htmltemplates:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.PUBLISH_OPTIONS)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        templates = dbfs.get_html_publisher_templates_files(dbo)
        al.debug("editing %d html templates" % len(templates), "code.htmltemplates", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", templates)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("htmltemplates", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create", templatename = "", header = "", body = "", footer = ""), session.locale)
        mode = post["mode"]
        dbo = session.dbo
        if mode == "create":
            users.check_permission(session, users.PUBLISH_OPTIONS)
            dbfs.update_html_publisher_template(dbo, session.user, post["templatename"], post["header"], post["body"], post["footer"])
        elif mode == "update":
            users.check_permission(session, users.PUBLISH_OPTIONS)
            dbfs.update_html_publisher_template(dbo, session.user, post["templatename"], post["header"], post["body"], post["footer"])
        elif mode == "delete":
            users.check_permission(session, users.PUBLISH_OPTIONS)
            for name in post["names"].split(","):
                if name != "": dbfs.delete_html_publisher_template(dbo, session.user, name)

class incident:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_INCIDENT)
        l = session.locale
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extanimalcontrol.get_animalcontrol(dbo, post.integer("id"))
        if session.siteid != 0 and a["SITEID"] != 0 and session.siteid != a["SITEID"]:
            raise utils.ASMPermissionError("incident not in user site")
        if a is None: raise web.notfound()
        al.debug("open incident %s %s %s" % (a["ACID"], a["INCIDENTNAME"], python2display(l, a["INCIDENTDATETIME"])), "code.incident", dbo)
        s = html.header("", session)
        c = html.controller_json("agegroups", configuration.age_groups(dbo))
        c += html.controller_json("additional", extadditional.get_additional_fields(dbo, a["ACID"], "incident"))
        if users.check_permission_bool(session, users.VIEW_AUDIT_TRAIL):
            c += html.controller_json("audit", audit.get_audit_for_link(dbo, "animalcontrol", a["ACID"]))
        c += html.controller_json("incident", a)
        c += html.controller_json("animallinks", extanimalcontrol.get_animalcontrol_animals(dbo, post.integer("id")))
        c += html.controller_json("incidenttypes", extlookups.get_incident_types(dbo))
        c += html.controller_json("completedtypes", extlookups.get_incident_completed_types(dbo))
        c += html.controller_json("pickuplocations", extlookups.get_pickup_locations(dbo))
        c += html.controller_json("roles", users.get_roles(dbo))
        c += html.controller_json("species", extlookups.get_species(dbo))
        c += html.controller_json("sexes", extlookups.get_sexes(dbo))
        c += html.controller_json("sites", extlookups.get_sites(dbo))
        c += html.controller_json("tabcounts", extanimalcontrol.get_animalcontrol_satellite_counts(dbo, a["ACID"])[0])
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_json("users", users.get_users(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("incident", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        l = session.locale
        post = utils.PostedData(web.input(mode="save"), session.locale)
        mode = post["mode"]
        if mode == "save":
            users.check_permission(session, users.CHANGE_INCIDENT)
            extanimalcontrol.update_animalcontrol_from_form(dbo, post, session.user)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_INCIDENT)
            extanimalcontrol.delete_animalcontrol(dbo, session.user, post.integer("id"))
        elif mode == "latlong":
            users.check_permission(session, users.CHANGE_INCIDENT)
            extanimalcontrol.update_dispatch_latlong(dbo, post.integer("incidentid"), post["latlong"])
        elif mode == "email":
            users.check_permission(session, users.EMAIL_PERSON)
            if not extperson.send_email_from_form(dbo, session.user, post):
                raise utils.ASMError(_("Failed sending email", l))
        elif mode == "linkanimaladd":
            users.check_permission(session, users.CHANGE_INCIDENT)
            extanimalcontrol.update_animalcontrol_addlink(dbo, session.user, post.integer("id"), post.integer("animalid"))
        elif mode == "linkanimaldelete":
            users.check_permission(session, users.CHANGE_INCIDENT)
            extanimalcontrol.update_animalcontrol_removelink(dbo, session.user, post.integer("id"), post.integer("animalid"))

class incident_citations:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_CITATION)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extanimalcontrol.get_animalcontrol(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        citations = financial.get_incident_citations(dbo, post.integer("id"))
        al.debug("got %d citations" % len(citations), "code.incident_citations", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "incident_citations")
        c += html.controller_json("rows", citations)
        c += html.controller_json("incident", a)
        c += html.controller_json("tabcounts", extanimalcontrol.get_animalcontrol_satellite_counts(dbo, a["ACID"])[0])
        c += html.controller_json("citationtypes", extlookups.get_citation_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("citations", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_CITATION)
            return financial.insert_citation_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_CITATION)
            financial.update_citation_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_CITATION)
            for lid in post.integer_list("ids"):
                financial.delete_citation(session.dbo, session.user, lid)

class incident_find:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_INCIDENT)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        c = html.controller_json("agegroups", configuration.age_groups(dbo))
        c += html.controller_json("incidenttypes", extlookups.get_incident_types(dbo))
        c += html.controller_json("completedtypes", extlookups.get_incident_completed_types(dbo))
        c += html.controller_json("citationtypes", extlookups.get_citation_types(dbo))
        c += html.controller_json("pickuplocations", extlookups.get_pickup_locations(dbo))
        c += html.controller_json("species", extlookups.get_species(dbo))
        c += html.controller_json("sexes", extlookups.get_sexes(dbo))
        c += html.controller_json("users", users.get_users(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("incident_find", s, c, post["json"] == "true")

class incident_find_results:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_INCIDENT)
        dbo = session.dbo
        l = session.locale
        post = utils.PostedData(web.input(mode = ""), session.locale)
        results = extanimalcontrol.get_animalcontrol_find_advanced(dbo, post.data, session.user, configuration.record_search_limit(dbo))
        resultsmessage = _("Find animal control incidents returned {0} results.", l).format(len(results))
        al.debug("found %d results for %s" % (len(results), str(web.ctx.query)), "code.incident_find_results", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", results)
        c += html.controller_str("name", "incident_find_results")
        c += html.controller_str("resultsmessage", resultsmessage)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("incident_find_results", s, c, post["json"] == "true")

class incident_diary:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_DIARY)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extanimalcontrol.get_animalcontrol(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        diaries = extdiary.get_diaries(dbo, extdiary.ANIMALCONTROL, post.integer("id"))
        al.debug("got %d diaries" % len(diaries), "code.incident_diary", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", diaries)
        c += html.controller_json("incident", a)
        c += html.controller_json("tabcounts", extanimalcontrol.get_animalcontrol_satellite_counts(dbo, a["ACID"])[0])
        c += html.controller_str("name", "incident_diary")
        c += html.controller_int("linkid", a["ACID"])
        c += html.controller_json("forlist", users.get_users_and_roles(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("diary", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_DIARY)
            return extdiary.insert_diary_from_form(session.dbo, session.user, extdiary.ANIMALCONTROL, post.integer("linkid"), post)
        elif mode == "update":
            users.check_permission(session, users.EDIT_ALL_DIARY_NOTES)
            extdiary.update_diary_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_DIARY)
            for did in post.integer_list("ids"):
                extdiary.delete_diary(session.dbo, session.user, did)
        elif mode == "complete":
            users.check_permission(session, users.BULK_COMPLETE_NOTES)
            for did in post.integer_list("ids"):
                extdiary.complete_diary_note(session.dbo, session.user, did)

class incident_log:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_LOG)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0, filter = -2), session.locale)
        a = extanimalcontrol.get_animalcontrol(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        logfilter = post.integer("filter")
        if logfilter == -2: logfilter = configuration.default_log_filter(dbo)
        logs = extlog.get_logs(dbo, extlog.ANIMALCONTROL, post.integer("id"), logfilter)
        al.debug("got %d logs" % len(logs), "code.incident_log", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "incident_log")
        c += html.controller_int("linkid", post.integer("id"))
        c += html.controller_int("filter", logfilter)
        c += html.controller_json("rows", logs)
        c += html.controller_json("incident", a)
        c += html.controller_json("tabcounts", extanimalcontrol.get_animalcontrol_satellite_counts(dbo, a["ACID"])[0])
        c += html.controller_json("logtypes", extlookups.get_log_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("log", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_LOG)
            return extlog.insert_log_from_form(session.dbo, session.user, extlog.ANIMALCONTROL, post.integer("linkid"), post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_LOG)
            extlog.update_log_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_LOG)
            for lid in post.integer_list("ids"):
                extlog.delete_log(session.dbo, session.user, lid)

class incident_map:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_INCIDENT)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        rows = extanimalcontrol.get_animalcontrol_find_advanced(dbo, { "filter": "incomplete" }, session.user)
        al.debug("incident map, %d active" % (len(rows)), "code.incident_map", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", rows);
        s += html.controller(c)
        s += html.footer()
        return full_or_json("incident_map", s, c, post["json"] == "true")

class incident_media:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MEDIA)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extanimalcontrol.get_animalcontrol(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        m = extmedia.get_media(dbo, extmedia.ANIMALCONTROL, post.integer("id"))
        al.debug("got %d media" % len(m), "code.incident_media", dbo)
        s = html.header("", session)
        c = html.controller_json("media", m)
        c += html.controller_json("incident", a)
        c += html.controller_json("tabcounts", extanimalcontrol.get_animalcontrol_satellite_counts(dbo, a["ACID"])[0])
        c += html.controller_bool("showpreferred", False)
        c += html.controller_int("linkid", post.integer("id"))
        c += html.controller_int("linktypeid", extmedia.ANIMALCONTROL)
        c += html.controller_str("name", self.__class__.__name__)
        c += html.controller_str("sigtype", ELECTRONIC_SIGNATURES)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("media", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create", filechooser={}, linkid="0", base64image = "", _unicode=False), session.locale)
        mode = post["mode"]
        dbo = session.dbo
        l = session.locale
        linkid = post.integer("linkid")
        if mode == "create":
            users.check_permission(session, users.ADD_MEDIA)
            extmedia.attach_file_from_form(session.dbo, session.user, extmedia.ANIMALCONTROL, linkid, post)
            raise web.seeother("incident_media?id=%d" % post.integer("linkid"))
        elif mode == "createdoc":
            users.check_permission(session, users.ADD_MEDIA)
            mediaid = extmedia.create_blank_document_media(session.dbo, session.user, extmedia.ANIMALCONTROL, linkid)
            raise web.seeother("document_media_edit?id=%d&redirecturl=incident_media?id=%d" % (mediaid, linkid))
        elif mode == "createlink":
            users.check_permission(session, users.ADD_MEDIA)
            mediaid = extmedia.attach_link_from_form(session.dbo, session.user, extmedia.ANIMALCONTROL, linkid, post)
            raise web.seeother("incident_media?id=%d" % linkid)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MEDIA)
            extmedia.update_media_notes(session.dbo, session.user, post.integer("mediaid"), post["comments"])
        elif mode == "delete":
            users.check_permission(session, users.DELETE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.delete_media(session.dbo, session.user, mid)
        elif mode == "email":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                content = dbfs.get_string(dbo, m["MEDIANAME"])
                if m["MEDIANAME"].endswith("html"):
                    content = utils.fix_relative_document_uris(content, BASE_URL, MULTIPLE_DATABASES and dbo.database or "")
                utils.send_email(dbo, configuration.email(dbo), emailadd, "", m["MEDIANOTES"], post["emailnote"], "html", content, m["MEDIANAME"])
            return emailadd
        elif mode == "emailpdf":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                if not m["MEDIANAME"].endswith("html"): continue
                content = dbfs.get_string(dbo, m["MEDIANAME"])
                contentpdf = utils.html_to_pdf(content, BASE_URL, MULTIPLE_DATABASES and dbo.database or "")
                utils.send_email(dbo, configuration.email(dbo), emailadd, "", m["MEDIANOTES"], "", "plain", contentpdf, "document.pdf")
            return emailadd
        elif mode == "emailsign":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            body = []
            body.append(post["emailnote"] + "\n\n")
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                if not m["MEDIANAME"].endswith("html"): continue
                body.append(m["MEDIANOTES"])
                body.append("%s?account=%s&method=sign_document&formid=%d" % (SERVICE_URL, dbo.database, mid))
                body.append("")
            utils.send_email(dbo, configuration.email(dbo), emailadd, "", _("Document signing request", l), "\n".join(body), "plain")
            return emailadd
        elif mode == "sign":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.sign_document(session.dbo, session.user, mid, post["sig"], post["signdate"])
        elif mode == "signpad":
            configuration.signpad_ids(session.dbo, session.user, post["ids"])
        elif mode == "rotateclock":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.rotate_media(session.dbo, session.user, mid, True)
        elif mode == "rotateanti":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.rotate_media(session.dbo, session.user, mid, False)
        elif mode == "web":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_web_preferred(session.dbo, session.user, mid)
        elif mode == "video":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_video_preferred(session.dbo, session.user, mid)
        elif mode == "doc":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_doc_preferred(session.dbo, session.user, mid)

class incident_new:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_INCIDENT)
        l = session.locale
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        title = _("Report a new incident", l)
        s = html.header(title, session)
        c = html.controller_json("incidenttypes", extlookups.get_incident_types(dbo))
        c += html.controller_json("additional", extadditional.get_additional_fields(dbo, 0, "incident"))
        c += html.controller_json("pickuplocations", extlookups.get_pickup_locations(dbo))
        c += html.controller_json("roles", users.get_roles(dbo))
        c += html.controller_json("sites", extlookups.get_sites(dbo))
        c += html.controller_json("users", users.get_users(dbo))
        s += html.controller(c)
        s += html.footer()
        al.debug("add incident", "code.incident_new", dbo)
        return full_or_json("incident_new", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_INCIDENT)
        utils.check_locked_db(session)
        post = utils.PostedData(web.input(), session.locale)
        incidentid = extanimalcontrol.insert_animalcontrol_from_form(session.dbo, post, session.user)
        return str(incidentid)

class latency:
    def GET(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        title = _("Latency", session.locale)
        al.debug("latency check", "code.latency", dbo)
        s = html.header(title, session)
        s += html.footer()
        return full_or_json("latency", s, "", False)

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(), session.locale)
        post.has_key("junk")
        web.header("Content-Type", "text/plain")
        web.header("Cache-Control", "no-cache")
        return "pong"

class licence:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_LICENCE)
        dbo = session.dbo
        post = utils.PostedData(web.input(offset = "i31"), session.locale)
        licences = financial.get_licences(dbo, post["offset"])
        al.debug("got %d licences" % len(licences), "code.licence", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "licence")
        c += html.controller_json("rows", licences)
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_json("licencetypes", extlookups.get_licence_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("licence", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_LICENCE)
            return financial.insert_licence_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_LICENCE)
            financial.update_licence_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_LICENCE)
            for lid in post.integer_list("ids"):
                financial.delete_licence(session.dbo, session.user, lid)

class licence_renewal:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_LICENCE)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        al.debug("renewing licence", "code.licence_renewal", dbo)
        c = html.controller_json("donationtypes", extlookups.get_donation_types(dbo))
        c += html.controller_json("licencetypes", extlookups.get_licence_types(dbo))
        c += html.controller_json("paymenttypes", extlookups.get_payment_types(dbo))
        c += html.controller_json("accounts", financial.get_accounts(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("licence_renewal", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        dbo = session.dbo
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_LICENCE)
            financial.insert_donations_from_form(dbo, session.user, post, post["issuedate"], False, post["person"], post["animal"]) 
            return financial.insert_licence_from_form(session.dbo, session.user, post)

class litters:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_LITTER)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        litters = extanimal.get_litters(dbo)
        al.debug("got %d litters" % len(litters), "code.litters", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", litters)
        c += html.controller_json("species", extlookups.get_species(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("litters", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        dbo = session.dbo
        if mode == "create":
            users.check_permission(session, users.ADD_LITTER)
            return extanimal.insert_litter_from_form(session.dbo, session.user, post)
        elif mode == "nextlitterid":
            nextid = db.query_int(dbo, "SELECT MAX(ID) FROM animallitter") + 1
            return utils.padleft(nextid, 6)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_LITTER)
            extanimal.update_litter_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_LITTER)
            for lid in post.integer_list("ids"):
                extanimal.delete_litter(session.dbo, session.user, lid)

class log_new:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.CHANGE_ANIMAL)
        dbo = session.dbo
        post = utils.PostedData(web.input(mode = "animal"), session.locale)
        s = html.header("", session)
        c = html.controller_json("logtypes", extlookups.get_log_types(dbo))
        c += html.controller_str("mode", post["mode"])
        al.debug("loaded lookups for new log", "code.log_new", dbo)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("log_new", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        users.check_permission(session, users.ADD_LOG)
        if mode == "animal":
            extlog.insert_log_from_form(dbo, session.user, extlog.ANIMAL, post.integer("animal"), post)
        elif mode == "person":
            extlog.insert_log_from_form(dbo, session.user, extlog.PERSON, post.integer("person"), post)

class lookups:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.MODIFY_LOOKUPS)
        l = session.locale
        dbo = session.dbo
        post = utils.PostedData(web.input(tablename="animaltype"), session.locale)
        tablename = post["tablename"]
        table = list(extlookups.LOOKUP_TABLES[tablename])
        table[0] = translate(table[0], l)
        table[2] = translate(table[2], l)
        rows = extlookups.get_lookup(dbo, tablename, table[1])
        al.debug("edit lookups for %s, got %d rows" % (tablename, len(rows)), "code.lookups", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", rows)
        c += html.controller_json("adoptapetcolours", extlookups.ADOPTAPET_COLOURS)
        c += html.controller_json("petfinderspecies", extlookups.PETFINDER_SPECIES)
        c += html.controller_json("petfinderbreeds", extlookups.PETFINDER_BREEDS)
        c += html.controller_json("sites", extlookups.get_sites(dbo))
        c += html.controller_str("tablename", tablename)
        c += html.controller_str("tablelabel", table[0])
        c += html.controller_str("namefield", table[1].upper())
        c += html.controller_str("namelabel", table[2])
        c += html.controller_str("descfield", table[3].upper())
        c += html.controller_bool("hasspecies", table[4] == 1)
        c += html.controller_bool("haspfspecies", table[5] == 1)
        c += html.controller_bool("haspfbreed", table[6] == 1)
        c += html.controller_bool("hasapcolour", table[7] == 1)
        c += html.controller_bool("hasdefaultcost", table[8] == 1)
        c += html.controller_bool("hasunits", table[9] == 1)
        c += html.controller_bool("hassite", table[10] == 1)
        c += html.controller_bool("canadd", table[11] == 1)
        c += html.controller_bool("candelete", table[12] == 1)
        c += html.controller_bool("canretire", table[13] == 1)
        c += html.controller_json("species", extlookups.get_species(dbo))
        c += html.controller_json("tables", html.json_lookup_tables(l))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("lookups", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(mode="create", id=0, lookup="", lookupname="", lookupdesc="", species=0, pfbreed="", pfspecies="", defaultcost="", adoptionfee=""), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.MODIFY_LOOKUPS)
            return extlookups.insert_lookup(dbo, post["lookup"], post["lookupname"], post["lookupdesc"], \
                post.integer("species"), post["pfbreed"], post["pfspecies"], post["apcolour"], post["units"], post.integer("site"), post.integer("defaultcost"), post.integer("retired"))
        elif mode == "update":
            users.check_permission(session, users.MODIFY_LOOKUPS)
            extlookups.update_lookup(dbo, post.integer("id"), post["lookup"], post["lookupname"], post["lookupdesc"], \
                post.integer("species"), post["pfbreed"], post["pfspecies"], post["apcolour"], post["units"], post.integer("site"), post.integer("defaultcost"), post.integer("retired"))
        elif mode == "delete":
            users.check_permission(session, users.MODIFY_LOOKUPS)
            for lid in post.integer_list("ids"):
                extlookups.delete_lookup(dbo, post["lookup"], lid)
        elif mode == "active":
            users.check_permission(session, users.MODIFY_LOOKUPS)
            for lid in post.integer_list("ids"):
                extlookups.update_lookup_retired(dbo, post["lookup"], lid, 0)
        elif mode == "inactive":
            users.check_permission(session, users.MODIFY_LOOKUPS)
            for lid in post.integer_list("ids"):
                extlookups.update_lookup_retired(dbo, post["lookup"], lid, 1)

class lostanimal:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_LOST_ANIMAL)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extlostfound.get_lostanimal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        al.debug("open lost animal %s %s %s" % (a["AGEGROUP"], a["SPECIESNAME"], a["OWNERNAME"]), "code.foundanimal", dbo)
        s = html.header("", session)
        c = html.controller_json("animal", a)
        c += html.controller_str("name", "lostanimal")
        c += html.controller_json("additional", extadditional.get_additional_fields(dbo, a["ID"], "lostanimal"))
        c += html.controller_json("agegroups", configuration.age_groups(dbo))
        if users.check_permission_bool(session, users.VIEW_AUDIT_TRAIL):
            c += html.controller_json("audit", audit.get_audit_for_link(dbo, "animallost", a["ID"]))
        c += html.controller_json("breeds", extlookups.get_breeds_by_species(dbo))
        c += html.controller_json("colours", extlookups.get_basecolours(dbo))
        c += html.controller_json("logtypes", extlookups.get_log_types(dbo))
        c += html.controller_json("sexes", extlookups.get_sexes(dbo))
        c += html.controller_json("species", extlookups.get_species(dbo))
        c += html.controller_json("tabcounts", extlostfound.get_lostanimal_satellite_counts(dbo, a["LFID"])[0])
        s += html.controller(c)
        s += html.footer()
        return full_or_json("lostfound", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        l = session.locale
        dbo = session.dbo
        post = utils.PostedData(web.input(mode="save"), session.locale)
        mode = post["mode"]
        if mode == "save":
            users.check_permission(session, users.CHANGE_LOST_ANIMAL)
            extlostfound.update_lostanimal_from_form(dbo, post, session.user)
        elif mode == "email":
            users.check_permission(session, users.EMAIL_PERSON)
            if not extlostfound.send_email_from_form(dbo, session.user, post):
                raise utils.ASMError(_("Failed sending email", l))
        elif mode == "delete":
            users.check_permission(session, users.DELETE_LOST_ANIMAL)
            extlostfound.delete_lostanimal(dbo, session.user, post.integer("id"))

class lostanimal_diary:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_DIARY)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extlostfound.get_lostanimal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        diaries = extdiary.get_diaries(dbo, extdiary.LOSTANIMAL, post.integer("id"))
        al.debug("got %d diaries for lost animal %s %s %s" % (len(diaries), a["AGEGROUP"], a["SPECIESNAME"], a["OWNERNAME"]), "code.foundanimal_diary", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", diaries)
        c += html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extlostfound.get_lostanimal_satellite_counts(dbo, a["LFID"])[0])
        c += html.controller_str("name", "lostanimal_diary")
        c += html.controller_int("linkid", a["LFID"])
        c += html.controller_json("forlist", users.get_users_and_roles(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("diary", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_DIARY)
            return extdiary.insert_diary_from_form(session.dbo, session.user, extdiary.LOSTANIMAL, post.integer("linkid"), post)
        elif mode == "update":
            users.check_permission(session, users.EDIT_ALL_DIARY_NOTES)
            extdiary.update_diary_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_DIARY)
            for did in post.integer_list("ids"):
                extdiary.delete_diary(session.dbo, session.user, did)
        elif mode == "complete":
            users.check_permission(session, users.BULK_COMPLETE_NOTES)
            for did in post.integer_list("ids"):
                extdiary.complete_diary_note(session.dbo, session.user, did)

class lostanimal_find:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_LOST_ANIMAL)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        c = html.controller_json("agegroups", configuration.age_groups(dbo))
        c += html.controller_str("name", "lostanimal_find")
        c += html.controller_json("colours", extlookups.get_basecolours(dbo))
        c += html.controller_json("species", extlookups.get_species(dbo))
        c += html.controller_json("breeds", extlookups.get_breeds_by_species(dbo))
        c += html.controller_json("sexes", extlookups.get_sexes(dbo))
        c += html.controller_str("mode", "lost")
        s += html.controller(c)
        s += html.footer()
        return full_or_json("lostfound_find", s, c, post["json"] == "true")

class lostanimal_find_results:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_LOST_ANIMAL)
        dbo = session.dbo
        l = session.locale
        post = utils.PostedData(web.input(mode = ""), session.locale)
        results = extlostfound.get_lostanimal_find_advanced(dbo, post.data, configuration.record_search_limit(dbo))
        resultsmessage = _("Find lost animal returned {0} results.", l).format(len(results))
        al.debug("found %d results for %s" % (len(results), str(web.ctx.query)), "code.lostanimal_find_results", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", results)
        c += html.controller_str("name", "lostanimal_find_results")
        c += html.controller_str("resultsmessage", resultsmessage)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("lostfound_find_results", s, c, post["json"] == "true")

class lostanimal_log:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_LOG)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0, filter = -2), session.locale)
        logfilter = post.integer("filter")
        if logfilter == -2: logfilter = configuration.default_log_filter(dbo)
        a = extlostfound.get_lostanimal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        logs = extlog.get_logs(dbo, extlog.LOSTANIMAL, post.integer("id"), logfilter)
        s = html.header("", session)
        c = html.controller_str("name", "lostanimal_log")
        c += html.controller_int("linkid", post.integer("id"))
        c += html.controller_int("filter", logfilter)
        c += html.controller_json("rows", logs)
        c += html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extlostfound.get_lostanimal_satellite_counts(dbo, a["LFID"])[0])
        c += html.controller_json("logtypes", extlookups.get_log_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("log", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_LOG)
            return extlog.insert_log_from_form(session.dbo, session.user, extlog.LOSTANIMAL, post.integer("linkid"), post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_LOG)
            extlog.update_log_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_LOG)
            for lid in post.integer_list("ids"):
                extlog.delete_log(session.dbo, session.user, lid)

class lostanimal_media:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MEDIA)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extlostfound.get_lostanimal(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        m = extmedia.get_media(dbo, extmedia.LOSTANIMAL, post.integer("id"))
        al.debug("got %d media for lost animal %s %s %s" % (len(m), a["AGEGROUP"], a["SPECIESNAME"], a["OWNERNAME"]), "code.foundanimal_media", dbo)
        s = html.header("", session)
        c = html.controller_json("media", m)
        c += html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extlostfound.get_lostanimal_satellite_counts(dbo, a["LFID"])[0])
        c += html.controller_bool("showpreferred", False)
        c += html.controller_int("linkid", post.integer("id"))
        c += html.controller_int("linktypeid", extmedia.LOSTANIMAL)
        c += html.controller_str("name", self.__class__.__name__)
        c += html.controller_str("sigtype", ELECTRONIC_SIGNATURES)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("media", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create", filechooser={}, linkid="0", base64image = "", _unicode=False), session.locale)
        mode = post["mode"]
        dbo = session.dbo
        l = session.locale
        linkid = post.integer("linkid")
        if mode == "create":
            users.check_permission(session, users.ADD_MEDIA)
            extmedia.attach_file_from_form(session.dbo, session.user, extmedia.LOSTANIMAL, linkid, post)
            raise web.seeother("lostanimal_media?id=%d" % linkid)
        elif mode == "createdoc":
            users.check_permission(session, users.ADD_MEDIA)
            mediaid = extmedia.create_blank_document_media(session.dbo, session.user, extmedia.LOSTANIMAL, linkid)
            raise web.seeother("document_media_edit?id=%d&redirecturl=lostanimal_media?id=%d" % (mediaid, linkid))
        elif mode == "createlink":
            users.check_permission(session, users.ADD_MEDIA)
            mediaid = extmedia.attach_link_from_form(session.dbo, session.user, extmedia.LOSTANIMAL, linkid, post)
            raise web.seeother("lostanimal_media?id=%d" % linkid)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MEDIA)
            extmedia.update_media_notes(session.dbo, session.user, post.integer("mediaid"), post["comments"])
        elif mode == "delete":
            users.check_permission(session, users.DELETE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.delete_media(session.dbo, session.user, mid)
        elif mode == "email":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                content = dbfs.get_string(dbo, m["MEDIANAME"])
                if m["MEDIANAME"].endswith("html"):
                    content = utils.fix_relative_document_uris(content, BASE_URL, MULTIPLE_DATABASES and dbo.database or "")
                utils.send_email(dbo, configuration.email(dbo), emailadd, "", m["MEDIANOTES"], post["emailnote"], "html", content, m["MEDIANAME"])
            return emailadd
        elif mode == "emailpdf":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                if not m["MEDIANAME"].endswith("html"): continue
                content = dbfs.get_string(dbo, m["MEDIANAME"])
                contentpdf = utils.html_to_pdf(content, BASE_URL, MULTIPLE_DATABASES and dbo.database or "")
                utils.send_email(dbo, configuration.email(dbo), emailadd, "", m["MEDIANOTES"], "", "plain", contentpdf, "document.pdf")
            return emailadd
        elif mode == "emailsign":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            body = []
            body.append(post["emailnote"] + "\n\n")
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                if not m["MEDIANAME"].endswith("html"): continue
                body.append(m["MEDIANOTES"])
                body.append("%s?account=%s&method=sign_document&formid=%d" % (SERVICE_URL, dbo.database, mid))
                body.append("")
            utils.send_email(dbo, configuration.email(dbo), emailadd, "", _("Document signing request", l), "\n".join(body), "plain")
            return emailadd
        elif mode == "sign":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.sign_document(session.dbo, session.user, mid, post["sig"], post["signdate"])
        elif mode == "signpad":
            configuration.signpad_ids(session.dbo, session.user, post["ids"])
        elif mode == "rotateclock":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.rotate_media(session.dbo, session.user, mid, True)
        elif mode == "rotateanti":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.rotate_media(session.dbo, session.user, mid, False)
        elif mode == "web":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_web_preferred(session.dbo, session.user, mid)
        elif mode == "video":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_video_preferred(session.dbo, session.user, mid)
        elif mode == "doc":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_doc_preferred(session.dbo, session.user, mid)

class lostanimal_new:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_LOST_ANIMAL)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        c = html.controller_json("agegroups", configuration.age_groups(dbo))
        c += html.controller_json("additional", extadditional.get_additional_fields(dbo, 0, "lostanimal"))
        c += html.controller_json("colours", extlookups.get_basecolours(dbo))
        c += html.controller_json("species", extlookups.get_species(dbo))
        c += html.controller_json("breeds", extlookups.get_breeds_by_species(dbo))
        c += html.controller_json("sexes", extlookups.get_sexes(dbo))
        c += html.controller_str("name", "lostanimal_new")
        s += html.controller(c)
        s += html.footer()
        return full_or_json("lostfound_new", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_LOST_ANIMAL)
        utils.check_locked_db(session)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        return str(extlostfound.insert_lostanimal_from_form(dbo, post, session.user))

class lostfound_match:
    def GET(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(lostanimalid = 0, foundanimalid = 0, animalid = 0), session.locale)
        lostanimalid = post.integer("lostanimalid")
        foundanimalid = post.integer("foundanimalid")
        animalid = post.integer("animalid")
        web.header("Content-Type", "text/html")
        web.header("Cache-Control", "no-cache")
        # If no parameters have been given, use the cached daily copy of the match report
        if lostanimalid == 0 and foundanimalid == 0 and animalid == 0:
            al.debug("no parameters given, using cached report at /reports/daily/lost_found_match.html", "code.lostfound_match", dbo)
            return configuration.lostfound_report(dbo)
        else:
            al.debug("match lost=%d, found=%d, animal=%d" % (lostanimalid, foundanimalid, animalid), "code.lostfound_match", dbo)
            return extlostfound.match_report(dbo, session.user, lostanimalid, foundanimalid, animalid)

class mailmerge:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.MAIL_MERGE)
        post = utils.PostedData(web.input(id = "0", mode = "criteria"), session.locale)
        mode = post["mode"]
        dbo = session.dbo
        l = session.locale
        user = session.user
        crit = extreports.get_criteria_controls(session.dbo, post.integer("id"))
        title = extreports.get_title(dbo, post.integer("id"))
        web.header("Content-Type", "text/html")
        web.header("Cache-Control", "no-cache")
        # If the mail merge doesn't take criteria, go to the merge selection screen instead
        if crit == "":
            al.debug("mailmerge %d has no criteria, moving to merge selection" % post.integer("id"), "code.mailmerge", dbo)
            mode = "selection"
        # If we're in criteria mode (and there are some to get here), ask for them
        if mode == "criteria":
            al.debug("building report criteria form for mailmerge %d %s" % (post.integer("id"), title), "code.mailmerge", dbo)
            s = html.header(title, session)
            c = html.controller_bool("criteria", True)
            c += html.controller_str("title", title)
            s += html.controller(c)
            s += html.heading(title)
            s += "<div id=\"criteriaform\">"
            s += "<input data-post=\"id\" type=\"hidden\" value=\"%d\" />" % post.integer("id")
            s += "<input data-post=\"mode\" type=\"hidden\" value=\"selection\" />"
            s += crit
            s += "</div>"
            s += html.footing()
            s += html.footer()
            return full_or_json("mailmerge", s, c, post["json"] == "true")
        elif mode == "selection":
            al.debug("entering mail merge selection mode for %d" % post.integer("id"), "code.mailmerge", dbo)
            p = extreports.get_criteria_params(dbo, post.integer("id"), post)
            session.mergeparams = p
            session.mergereport = post.integer("id")
            rows, cols = extreports.execute_query(dbo, post.integer("id"), user, p)
            if rows is None: rows = []
            al.debug("got merge rows (%d items)" % len(rows), "code.mailmerge", dbo)
            session.mergetitle = title.replace(" ", "_").replace("\"", "").replace("'", "").lower()
            # construct a list of field tokens for the email helper
            fields = []
            if len(rows) >  0:
                for fname in sorted(rows[0].iterkeys()):
                    fields.append(fname)
            # send the selection form
            title = _("Mail Merge - {0}", l).format(title)
            s = html.header(title, session)
            c = html.controller_json("fields", fields)
            c += html.controller_int("numrows", len(rows))
            c += html.controller_bool("hasperson", "OWNERNAME" in fields and "OWNERADDRESS" in fields and "OWNERTOWN" in fields and "OWNERPOSTCODE" in fields)
            c += html.controller_json("templates", dbfs.get_document_templates(dbo))
            s += html.controller(c)
            s += html.footer()
            return full_or_json("mailmerge", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        l = session.locale
        dbo = session.dbo
        post = utils.PostedData(web.input(mode="csv"), session.locale)
        mode = post["mode"]
        rows, cols = extreports.execute_query(dbo, session.mergereport, session.user, session.mergeparams)
        al.debug("got merge rows (%d items)" % len(rows), "code.mailmerge", dbo)
        if mode == "email":
            fromadd = post["from"]
            subject = post["subject"]
            body = post["body"]
            utils.send_bulk_email(dbo, fromadd, subject, body, rows, "html")
        elif mode == "document":
            templateid = post.integer("templateid")
            template = dbfs.get_string_id(dbo, templateid)
            templatename = dbfs.get_name_for_id(dbo, templateid)
            if not templatename.endswith(".html"):
                raise utils.ASMValidationError("Only html templates are allowed")
            # Generate a document from the template for each row
            org_tags = wordprocessor.org_tags(dbo, session.user)
            c = []
            for d in rows:
                c.append( wordprocessor.substitute_tags(template, wordprocessor.append_tags(d, org_tags)) )
            content = '<div class="mce-pagebreak" style="page-break-before: always; clear: both; border: 0">&nbsp;</div>'.join(c)
            web.header("Content-Type", "text/html")
            web.header("Cache-Control", "no-cache")
            return html.tinymce_header(templatename, "document_edit.js", configuration.js_window_print(dbo)) + \
                html.tinymce_main(dbo.locale, "", recid=0, mode="", \
                    template="", content=utils.escape_tinymce(content))
        elif mode == "labels":
            web.header("Content-Type", "application/pdf")
            disposition = configuration.pdf_inline(dbo) and "inline; filename=%s" or "attachment; filename=%s"
            web.header("Content-Disposition", disposition % session.mergetitle + ".pdf")
            return utils.generate_label_pdf(dbo, session.locale, rows, post["papersize"], post["units"],
                post.floating("hpitch"), post.floating("vpitch"), 
                post.floating("width"), post.floating("height"), 
                post.floating("lmargin"), post.floating("tmargin"),
                post.integer("cols"), post.integer("rows"))
        elif mode == "csv":
            web.header("Content-Type", "text/csv")
            web.header("Content-Disposition", u"attachment; filename=" + utils.decode_html(session.mergetitle) + u".csv")
            includeheader = 1 == post.boolean("includeheader")
            return utils.csv(l, rows, cols, includeheader)
        elif mode == "preview":
            al.debug("returning preview rows for %d" % session.mergereport, "code.mailmerge", dbo)
            return html.json(rows)

class medical:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MEDICAL)
        dbo = session.dbo
        post = utils.PostedData(web.input(newmed = "0", offset = "m365"), session.locale)
        med = extmedical.get_treatments_outstanding(dbo, post["offset"], session.locationfilter, session.siteid)
        profiles = extmedical.get_profiles(dbo)
        al.debug("got %d medical treatments" % len(med), "code.medical", dbo)
        s = html.header("", session)
        c = html.controller_json("profiles", profiles)
        c += html.controller_json("rows", med)
        c += html.controller_bool("newmed", post.integer("newmed") == 1)
        c += html.controller_str("name", "medical")
        c += html.controller_json("stockitems", extstock.get_stock_items(dbo))
        c += html.controller_json("stockusagetypes", extlookups.get_stock_usage_types(dbo))
        c += html.controller_json("users", users.get_users(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("medical", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"] 
        if mode == "create":
            users.check_permission(session, users.ADD_MEDICAL)
            extmedical.insert_regimen_from_form(session.dbo, session.user, post)
        if mode == "createbulk":
            users.check_permission(session, users.ADD_MEDICAL)
            for animalid in post.integer_list("animals"):
                post.data["animal"] = str(animalid)
                extmedical.insert_regimen_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MEDICAL)
            extmedical.update_regimen_from_form(session.dbo, session.user, post)
        elif mode == "delete_regimen":
            users.check_permission(session, users.DELETE_MEDICAL)
            for mid in post.integer_list("ids"):
                extmedical.delete_regimen(session.dbo, session.user, mid)
        elif mode == "delete_treatment":
            users.check_permission(session, users.DELETE_MEDICAL)
            for mid in post.integer_list("ids"):
                extmedical.delete_treatment(session.dbo, session.user, mid)
        elif mode == "get_profile":
            return html.json([extmedical.get_profile(session.dbo, post.integer("profileid"))])
        elif mode == "given":
            users.check_permission(session, users.BULK_COMPLETE_MEDICAL)
            newdate = post.date("newdate")
            vet = post.integer("givenvet")
            by = post["givenby"]
            comments = post["treatmentcomments"]
            for mid in post.integer_list("ids"):
                extmedical.update_treatment_given(session.dbo, session.user, mid, newdate, by, vet, comments)
            if post.integer("item") != -1:
                extstock.deduct_stocklevel_from_form(session.dbo, session.user, post)
        elif mode == "required":
            users.check_permission(session, users.BULK_COMPLETE_MEDICAL)
            newdate = post.date("newdate")
            for mid in post.integer_list("ids"):
                extmedical.update_treatment_required(session.dbo, session.user, mid, newdate)

class medicalprofile:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MEDICAL)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        med = extmedical.get_profiles(dbo)
        al.debug("got %d medical profiles" % len(med), "code.medical_profile", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", med)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("medicalprofile", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MEDICAL)
            extmedical.insert_profile_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MEDICAL)
            extmedical.update_profile_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_MEDICAL)
            for mid in post.integer_list("ids"):
                extmedical.delete_profile(session.dbo, session.user, mid)

class move_adopt:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_MOVEMENT)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        c = html.controller_json("donationtypes", extlookups.get_donation_types(dbo))
        c += html.controller_json("accounts", financial.get_accounts(dbo))
        c += html.controller_json("paymenttypes", extlookups.get_payment_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("move_adopt", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        l = dbo.locale
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MOVEMENT)
            return str(extmovement.insert_adoption_from_form(session.dbo, session.user, post))
        elif mode == "cost":
            users.check_permission(session, users.VIEW_COST)
            dailyboardcost = extanimal.get_daily_boarding_cost(dbo, post.integer("id"))
            dailyboardcostdisplay = format_currency(l, dailyboardcost)
            daysonshelter = extanimal.get_days_on_shelter(dbo, post.integer("id"))
            totaldisplay = format_currency(l, dailyboardcost * daysonshelter)
            return totaldisplay + "||" + _("On shelter for {0} days, daily cost {1}, cost record total <b>{2}</b>", l).format(daysonshelter, dailyboardcostdisplay, totaldisplay)
        elif mode == "donationdefault":
            return extlookups.get_donation_default(dbo, post.integer("donationtype"))
        elif mode == "insurance":
            return extmovement.generate_insurance_number(dbo)

class move_book_foster:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MOVEMENT)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        movements = extmovement.get_movements(dbo, extmovement.FOSTER)
        al.debug("got %d movements" % len(movements), "code.move_book_foster", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", movements)
        c += html.controller_json("movementtypes", extlookups.get_movement_types(dbo))
        c += html.controller_json("reservationstatuses", extlookups.get_reservation_statuses(dbo))
        c += html.controller_json("returncategories", extlookups.get_entryreasons(dbo))
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_str("name", self.__class__.__name__)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("movements", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MOVEMENT)
            return extmovement.insert_movement_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MOVEMENT)
            extmovement.update_movement_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_MOVEMENT)
            for mid in post.integer_list("ids"):
                extmovement.delete_movement(session.dbo, session.user, mid)

class move_book_recent_adoption:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MOVEMENT)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        movements = extmovement.get_recent_adoptions(dbo)
        al.debug("got %d movements" % len(movements), "code.move_book_recent_adoption", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", movements)
        c += html.controller_json("movementtypes", extlookups.get_movement_types(dbo))
        c += html.controller_json("reservationstatuses", extlookups.get_reservation_statuses(dbo))
        c += html.controller_json("returncategories", extlookups.get_entryreasons(dbo))
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_str("name", self.__class__.__name__)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("movements", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MOVEMENT)
            return extmovement.insert_movement_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MOVEMENT)
            extmovement.update_movement_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_MOVEMENT)
            for mid in post.integer_list("ids"):
                extmovement.delete_movement(session.dbo, session.user, mid)

class move_book_recent_other:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MOVEMENT)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        movements = extmovement.get_recent_nonfosteradoption(dbo)
        al.debug("got %d movements" % len(movements), "code.move_book_recent_other", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", movements)
        c += html.controller_json("movementtypes", extlookups.get_movement_types(dbo))
        c += html.controller_json("reservationstatuses", extlookups.get_reservation_statuses(dbo))
        c += html.controller_json("returncategories", extlookups.get_entryreasons(dbo))
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_str("name", self.__class__.__name__)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("movements", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MOVEMENT)
            return extmovement.insert_movement_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MOVEMENT)
            extmovement.update_movement_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_MOVEMENT)
            for mid in post.integer_list("ids"):
                extmovement.delete_movement(session.dbo, session.user, mid)

class move_book_recent_transfer:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MOVEMENT)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        movements = extmovement.get_recent_transfers(dbo)
        al.debug("got %d movements" % len(movements), "code.move_book_recent_transfer", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", movements)
        c += html.controller_json("movementtypes", extlookups.get_movement_types(dbo))
        c += html.controller_json("reservationstatuses", extlookups.get_reservation_statuses(dbo))
        c += html.controller_json("returncategories", extlookups.get_entryreasons(dbo))
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_str("name", self.__class__.__name__)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("movements", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MOVEMENT)
            return extmovement.insert_movement_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MOVEMENT)
            extmovement.update_movement_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_MOVEMENT)
            for mid in post.integer_list("ids"):
                extmovement.delete_movement(session.dbo, session.user, mid)

class move_book_reservation:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MOVEMENT)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        movements = extmovement.get_active_reservations(dbo)
        al.debug("got %d movements" % len(movements), "code.move_book_reservation", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", movements)
        c += html.controller_json("movementtypes", extlookups.get_movement_types(dbo))
        c += html.controller_json("reservationstatuses", extlookups.get_reservation_statuses(dbo))
        c += html.controller_json("returncategories", extlookups.get_entryreasons(dbo))
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_str("name", self.__class__.__name__)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("movements", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MOVEMENT)
            return extmovement.insert_movement_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MOVEMENT)
            extmovement.update_movement_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_MOVEMENT)
            for mid in post.integer_list("ids"):
                extmovement.delete_movement(session.dbo, session.user, mid)

class move_book_retailer:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MOVEMENT)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        movements = extmovement.get_movements(dbo, extmovement.RETAILER)
        al.debug("got %d movements" % len(movements), "code.move_book_retailer", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", movements)
        c += html.controller_json("movementtypes", extlookups.get_movement_types(dbo))
        c += html.controller_json("reservationstatuses", extlookups.get_reservation_statuses(dbo))
        c += html.controller_json("returncategories", extlookups.get_entryreasons(dbo))
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_str("name", self.__class__.__name__)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("movements", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MOVEMENT)
            return extmovement.insert_movement_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MOVEMENT)
            extmovement.update_movement_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_MOVEMENT)
            for mid in post.integer_list("ids"):
                extmovement.delete_movement(session.dbo, session.user, mid)

class move_book_trial_adoption:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MOVEMENT)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        movements = extmovement.get_trial_adoptions(dbo)
        al.debug("got %d movements" % len(movements), "code.move_book_trial_adoption", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", movements)
        c += html.controller_json("movementtypes", extlookups.get_movement_types(dbo))
        c += html.controller_json("reservationstatuses", extlookups.get_reservation_statuses(dbo))
        c += html.controller_json("returncategories", extlookups.get_entryreasons(dbo))
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_str("name", self.__class__.__name__)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("movements", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MOVEMENT)
            return extmovement.insert_movement_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MOVEMENT)
            extmovement.update_movement_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_MOVEMENT)
            for mid in post.integer_list("ids"):
                extmovement.delete_movement(session.dbo, session.user, mid)

class move_book_unneutered:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MOVEMENT)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        movements = extmovement.get_recent_unneutered_adoptions(dbo)
        al.debug("got %d movements" % len(movements), "code.move_book_unneutered", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", movements)
        c += html.controller_json("movementtypes", extlookups.get_movement_types(dbo))
        c += html.controller_json("reservationstatuses", extlookups.get_reservation_statuses(dbo))
        c += html.controller_json("returncategories", extlookups.get_entryreasons(dbo))
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_str("name", self.__class__.__name__)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("movements", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MOVEMENT)
            return extmovement.insert_movement_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MOVEMENT)
            extmovement.update_movement_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_MOVEMENT)
            for mid in post.integer_list("ids"):
                extmovement.delete_movement(session.dbo, session.user, mid)

class move_deceased:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.CHANGE_ANIMAL)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        c = html.controller_json("deathreasons", extlookups.get_deathreasons(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("move_deceased", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.CHANGE_ANIMAL)
            extanimal.update_deceased_from_form(dbo, session.user, post)

class move_foster:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_MOVEMENT)
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        s += html.footer()
        return full_or_json("move_foster", s, "", post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MOVEMENT)
            return str(extmovement.insert_foster_from_form(session.dbo, session.user, post))

class move_gendoc:
    def GET(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(), session.locale)
        dbo = session.dbo
        s = html.header("", session)
        c = html.controller_str("templates", html.template_selection(
            dbfs.get_document_templates(dbo), "document_gen?mode=%s&id=%s" % (post["mode"], post["id"])))
        c += html.controller_str("message", post["message"])
        s += html.controller(c)
        s += html.footer()
        return full_or_json("move_gendoc", s, c, post["json"] == "true")

class move_reclaim:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_MOVEMENT)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        c = html.controller_json("donationtypes", extlookups.get_donation_types(dbo))
        c += html.controller_json("accounts", financial.get_accounts(dbo))
        c += html.controller_json("paymenttypes", extlookups.get_payment_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("move_reclaim", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        l = dbo.locale
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MOVEMENT)
            return str(extmovement.insert_reclaim_from_form(session.dbo, session.user, post))
        elif mode == "cost":
            users.check_permission(session, users.VIEW_COST)
            dailyboardcost = extanimal.get_daily_boarding_cost(dbo, post.integer("id"))
            dailyboardcostdisplay = format_currency(l, dailyboardcost)
            daysonshelter = extanimal.get_days_on_shelter(dbo, post.integer("id"))
            totaldisplay = format_currency(l, dailyboardcost * daysonshelter)
            return totaldisplay + "||" + _("On shelter for {0} days, daily cost {1}, cost record total <b>{2}</b>", l).format(daysonshelter, dailyboardcostdisplay, totaldisplay)
        elif mode == "donationdefault":
            return extlookups.get_donation_default(dbo, post.integer("donationtype"))

class move_reserve:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_MOVEMENT)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        c = html.controller_json("donationtypes", extlookups.get_donation_types(dbo))
        c += html.controller_json("accounts", financial.get_accounts(dbo))
        c += html.controller_json("paymenttypes", extlookups.get_payment_types(dbo))
        c += html.controller_json("reservationstatuses", extlookups.get_reservation_statuses(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("move_reserve", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MOVEMENT)
            return str(extmovement.insert_reserve_from_form(session.dbo, session.user, post))

class move_retailer:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_MOVEMENT)
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        s += html.controller("")
        s += html.footer()
        return full_or_json("move_retailer", s, "", post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MOVEMENT)
            return str(extmovement.insert_retailer_from_form(session.dbo, session.user, post))

class move_transfer:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_MOVEMENT)
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        s += html.controller("")
        s += html.footer()
        return full_or_json("move_transfer", s, "", post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MOVEMENT)
            return str(extmovement.insert_transfer_from_form(session.dbo, session.user, post))

class onlineform_incoming:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_INCOMING_FORMS)
        dbo = session.dbo
        post = utils.PostedData(web.input(mode="view"), session.locale)
        mode = post["mode"]
        web.header("Content-Type", "text/html")
        web.header("Cache-Control", "no-cache")
        if mode == "print":
            users.check_permission(session, users.VIEW_INCOMING_FORMS)
            return extonlineform.get_onlineformincoming_html_print(dbo, post.integer_list("ids"))
        headers = extonlineform.get_onlineformincoming_headers(dbo)
        al.debug("got %d submitted headers" % len(headers), "code.onlineform_incoming", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", headers)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("onlineform_incoming", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(mode="view"), session.locale)
        mode = post["mode"]
        personid = post.integer("personid")
        animalid = post.integer("animalid")
        collationid = post.integer("collationid")
        web.header("Content-Type", "text/plain")
        if mode == "view":
            users.check_permission(session, users.VIEW_INCOMING_FORMS)
            return extonlineform.get_onlineformincoming_html(dbo, collationid)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_INCOMING_FORMS)
            for did in post.integer_list("ids"):
                extonlineform.delete_onlineformincoming(session.dbo, session.user, did)
        elif mode == "attachanimal":
            formname = extonlineform.get_onlineformincoming_name(dbo, collationid)
            formhtml = extonlineform.get_onlineformincoming_html_print(dbo, [collationid,] )
            extmedia.create_document_media(dbo, session.user, extmedia.ANIMAL, animalid, formname, formhtml )
            return animalid 
        elif mode == "attachperson":
            formname = extonlineform.get_onlineformincoming_name(dbo, collationid)
            formhtml = extonlineform.get_onlineformincoming_html_print(dbo, [collationid,] )
            extmedia.create_document_media(dbo, session.user, extmedia.PERSON, personid, formname, formhtml )
            return personid 
        elif mode == "animal":
            users.check_permission(session, users.ADD_MEDIA)
            rv = []
            for pid in post.integer_list("ids"):
                collationid, animalid, animalname = extonlineform.attach_animal(session.dbo, session.user, pid)
                rv.append("%d|%d|%s" % (collationid, animalid, animalname))
            return "^$".join(rv)
        elif mode == "person":
            users.check_permission(session, users.ADD_PERSON)
            rv = []
            for pid in post.integer_list("ids"):
                collationid, personid, personname = extonlineform.create_person(session.dbo, session.user, pid)
                rv.append("%d|%d|%s" % (collationid, personid, personname))
            return "^$".join(rv)
        elif mode == "lostanimal":
            users.check_permission(session, users.ADD_LOST_ANIMAL)
            rv = []
            for pid in post.integer_list("ids"):
                collationid, lostanimalid, personname = extonlineform.create_lostanimal(session.dbo, session.user, pid)
                rv.append("%d|%d|%s" % (collationid, lostanimalid, personname))
            return "^$".join(rv)
        elif mode == "foundanimal":
            users.check_permission(session, users.ADD_FOUND_ANIMAL)
            rv = []
            for pid in post.integer_list("ids"):
                collationid, foundanimalid, personname = extonlineform.create_foundanimal(session.dbo, session.user, pid)
                rv.append("%d|%d|%s" % (collationid, foundanimalid, personname))
            return "^$".join(rv)
        elif mode == "incident":
            users.check_permission(session, users.ADD_INCIDENT)
            rv = []
            for pid in post.integer_list("ids"):
                collationid, incidentid, personname = extonlineform.create_animalcontrol(session.dbo, session.user, pid)
                rv.append("%d|%d|%s" % (collationid, incidentid, personname))
            return "^$".join(rv)
        elif mode == "transport":
            users.check_permission(session, users.ADD_TRANSPORT)
            rv = []
            for pid in post.integer_list("ids"):
                collationid, animalid, animalname = extonlineform.create_transport(session.dbo, session.user, pid)
                rv.append("%d|%d|%s" % (collationid, animalid, animalname))
            return "^$".join(rv)
        elif mode == "waitinglist":
            users.check_permission(session, users.ADD_WAITING_LIST)
            rv = []
            for pid in post.integer_list("ids"):
                collationid, wlid, personname = extonlineform.create_waitinglist(session.dbo, session.user, pid)
                rv.append("%d|%d|%s" % (collationid, wlid, personname))
            return "^$".join(rv)

class onlineform:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.EDIT_ONLINE_FORMS)
        l = session.locale
        dbo = session.dbo
        post = utils.PostedData(web.input(formid = 0), session.locale)
        formid = post.integer("formid")
        formname = extonlineform.get_onlineform_name(dbo, formid)
        fields = extonlineform.get_onlineformfields(dbo, formid)
        # Escape any angle brackets in raw markup output. This is needed
        # to target tooltip as a textarea
        for r in fields:
            if r["FIELDTYPE"] == extonlineform.FIELDTYPE_RAWMARKUP:
               r["TOOLTIP"] = html.escape_angle(r["TOOLTIP"]) 
        title = _("Online Form: {0}", l).format(formname)
        al.debug("got %d online form fields" % len(fields), "code.onlineform", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", fields)
        c += html.controller_int("formid", formid)
        c += html.controller_str("formname", formname)
        c += html.controller_json("formfields", extonlineform.FORM_FIELDS)
        c += html.controller_str("title", title)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("onlineform", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.EDIT_ONLINE_FORMS)
            return extonlineform.insert_onlineformfield_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.EDIT_ONLINE_FORMS)
            extonlineform.update_onlineformfield_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.EDIT_ONLINE_FORMS)
            for did in post.integer_list("ids"):
                extonlineform.delete_onlineformfield(session.dbo, session.user, did)

class onlineforms:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.EDIT_ONLINE_FORMS)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        onlineforms = extonlineform.get_onlineforms(dbo)
        al.debug("got %d online forms" % len(onlineforms), "code.onlineforms", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", onlineforms)
        c += html.controller_json("flags", extlookups.get_person_flags(dbo))
        c += html.controller_json("header", extonlineform.get_onlineform_header(dbo))
        c += html.controller_json("footer", extonlineform.get_onlineform_footer(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("onlineforms", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create", filechooser={}), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.EDIT_ONLINE_FORMS)
            return extonlineform.insert_onlineform_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.EDIT_ONLINE_FORMS)
            extonlineform.update_onlineform_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.EDIT_ONLINE_FORMS)
            for did in post.integer_list("ids"):
                extonlineform.delete_onlineform(session.dbo, session.user, did)
        elif mode == "clone":
            users.check_permission(session, users.EDIT_ONLINE_FORMS)
            for did in post.integer_list("ids"):
                extonlineform.clone_onlineform(session.dbo, session.user, did)
        elif mode == "headfoot":
            users.check_permission(session, users.EDIT_ONLINE_FORMS)
            dbfs.put_string_filepath(session.dbo, "/onlineform/head.html", post["header"])
            dbfs.put_string_filepath(session.dbo, "/onlineform/foot.html", post["footer"])
        elif mode == "import":
            users.check_permission(session, users.EDIT_ONLINE_FORMS)
            extonlineform.import_onlineform_json(session.dbo, post.filedata())
            raise web.seeother("onlineforms")

class options:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.SYSTEM_OPTIONS)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        session.configuration = configuration.get_map(dbo)
        s = html.header("", session)
        c = html.controller_json("accounts", financial.get_accounts(dbo))
        c += html.controller_plain("animalfindcolumns", html.json_animalfindcolumns(dbo))
        c += html.controller_json("breeds", extlookups.get_breeds(dbo))
        c += html.controller_json("coattypes", extlookups.get_coattypes(dbo))
        c += html.controller_json("colours", extlookups.get_basecolours(dbo))
        c += html.controller_json("costtypes", extlookups.get_costtypes(dbo))
        c += html.controller_json("deathreasons", extlookups.get_deathreasons(dbo))
        c += html.controller_json("donationtypes", extlookups.get_donation_types(dbo))
        c += html.controller_json("entryreasons", extlookups.get_entryreasons(dbo))
        c += html.controller_json("incidenttypes", extlookups.get_incident_types(dbo))
        c += html.controller_json("locales", extlookups.LOCALES)
        c += html.controller_json("locations", extlookups.get_internal_locations(dbo))
        c += html.controller_json("logtypes", extlookups.get_log_types(dbo))
        c += html.controller_plain("personfindcolumns", html.json_personfindcolumns(dbo))
        c += html.controller_plain("quicklinks", html.json_quicklinks(dbo))
        c += html.controller_json("reservationstatuses", extlookups.get_reservation_statuses(dbo))
        c += html.controller_json("sizes", extlookups.get_sizes(dbo))
        c += html.controller_json("species", extlookups.get_species(dbo))
        c += html.controller_json("themes", extlookups.VISUAL_THEMES)
        c += html.controller_json("testtypes", extlookups.get_test_types(dbo))
        c += html.controller_json("types", extlookups.get_animal_types(dbo))
        c += html.controller_json("urgencies", extlookups.get_urgencies(dbo))
        c += html.controller_json("usersandroles", users.get_users_and_roles(dbo))
        c += html.controller_json("vaccinationtypes", extlookups.get_vaccination_types(dbo))
        c += html.controller_plain("waitinglistcolumns", html.json_waitinglistcolumns(dbo))
        al.debug("lookups loaded", "code.options", dbo)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("options", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="save"), session.locale)
        mode = post["mode"]
        if mode == "save":
            users.check_permission(session, users.SYSTEM_OPTIONS)
            configuration.csave(session.dbo, session.user, post)
            users.update_session(session)

class person:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_PERSON)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        p = extperson.get_person(dbo, post.integer("id"))
        if p is None: raise web.notfound()
        if p["ISSTAFF"] == 1:
            users.check_permission(session, users.VIEW_STAFF)
        if p["ISVOLUNTEER"] == 1:
            users.check_permission(session, users.VIEW_VOLUNTEER)
        if session.siteid != 0 and p["SITEID"] != 0 and session.siteid != p["SITEID"]:
            raise utils.ASMPermissionError("person not in user site")
        al.debug("opened person '%s'" % p["OWNERNAME"], "code.person", dbo)
        s = html.header("", session)
        c = html.controller_json("additional", extadditional.get_additional_fields(dbo, p["ID"], "person"))
        c += html.controller_json("animaltypes", extlookups.get_animal_types(dbo))
        if users.check_permission_bool(session, users.VIEW_AUDIT_TRAIL):
            c += html.controller_json("audit", audit.get_audit_for_link(dbo, "owner", p["ID"]))
        c += html.controller_json("species", extlookups.get_species(dbo))
        c += html.controller_json("breeds", extlookups.get_breeds_by_species(dbo))
        c += html.controller_json("colours", extlookups.get_basecolours(dbo))
        c += html.controller_json("diarytasks", extdiary.get_person_tasks(dbo))
        c += html.controller_json("flags", extlookups.get_person_flags(dbo))
        c += html.controller_json("ynun", extlookups.get_ynun(dbo))
        c += html.controller_json("homecheckhistory", extperson.get_homechecked(dbo, post.integer("id")))
        c += html.controller_json("logtypes", extlookups.get_log_types(dbo))
        c += html.controller_json("sexes", extlookups.get_sexes(dbo))
        c += html.controller_json("sites", extlookups.get_sites(dbo))
        c += html.controller_json("sizes", extlookups.get_sizes(dbo))
        c += html.controller_json("towns", "|".join(extperson.get_towns(dbo)))
        c += html.controller_json("counties", "|".join(extperson.get_counties(dbo)))
        c += html.controller_json("towncounties", "|".join(extperson.get_town_to_county(dbo)))
        c += html.controller_json("tabcounts", extperson.get_satellite_counts(dbo, p["ID"])[0])
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_json("person", p)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("person", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        l = session.locale
        post = utils.PostedData(web.input(mode="save"), session.locale)
        mode = post["mode"]
        if mode == "save":
            users.check_permission(session, users.CHANGE_PERSON)
            extperson.update_person_from_form(dbo, post, session.user)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_PERSON)
            extperson.delete_person(dbo, session.user, post.integer("personid"))
        elif mode == "email":
            users.check_permission(session, users.EMAIL_PERSON)
            if not extperson.send_email_from_form(dbo, session.user, post):
                raise utils.ASMError(_("Failed sending email", l))
        elif mode == "latlong":
            users.check_permission(session, users.CHANGE_PERSON)
            extperson.update_latlong(dbo, post.integer("personid"), post["latlong"])
        elif mode == "merge":
            users.check_permission(session, users.MERGE_PERSON)
            extperson.merge_person(dbo, session.user, post.integer("personid"), post.integer("mergepersonid"))

class person_citations:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_CITATION)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        p = extperson.get_person(dbo, post.integer("id"))
        if p is None: raise web.notfound()
        title = p["OWNERNAME"]
        citations = financial.get_person_citations(dbo, post.integer("id"))
        al.debug("got %d citations" % len(citations), "code.incident_citations", dbo)
        s = html.header(title, session)
        c = html.controller_str("name", "person_citations")
        c += html.controller_json("rows", citations)
        c += html.controller_json("person", p)
        c += html.controller_json("tabcounts", extperson.get_satellite_counts(dbo, p["ID"])[0])
        c += html.controller_json("citationtypes", extlookups.get_citation_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("citations", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_CITATION)
            return financial.insert_citation_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_CITATION)
            financial.update_citation_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_CITATION)
            for lid in post.integer_list("ids"):
                financial.delete_citation(session.dbo, session.user, lid)

class person_diary:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_DIARY)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        p = extperson.get_person(dbo, post.integer("id"))
        if p is None: raise web.notfound()
        diaries = extdiary.get_diaries(dbo, extdiary.PERSON, post.integer("id"))
        al.debug("got %d diaries" % len(diaries), "code.person_diary", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", diaries)
        c += html.controller_json("person", p)
        c += html.controller_json("tabcounts", extperson.get_satellite_counts(dbo, p["ID"])[0])
        c += html.controller_str("name", "person_diary")
        c += html.controller_int("linkid", p["ID"])
        c += html.controller_json("forlist", users.get_users_and_roles(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("diary", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_DIARY)
            return extdiary.insert_diary_from_form(session.dbo, session.user, extdiary.PERSON, post.integer("linkid"), post)
        elif mode == "update":
            users.check_permission(session, users.EDIT_ALL_DIARY_NOTES)
            extdiary.update_diary_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_DIARY)
            for did in post.integer_list("ids"):
                extdiary.delete_diary(session.dbo, session.user, did)
        elif mode == "complete":
            users.check_permission(session, users.BULK_COMPLETE_NOTES)
            for did in post.integer_list("ids"):
                extdiary.complete_diary_note(session.dbo, session.user, did)

class person_donations:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_DONATION)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        p = extperson.get_person(dbo, post.integer("id"))
        if p is None: raise web.notfound()
        donations = financial.get_person_donations(dbo, post.integer("id"))
        s = html.header("", session)
        c = html.controller_json("person", p)
        c += html.controller_json("tabcounts", extperson.get_satellite_counts(dbo, p["ID"])[0])
        c += html.controller_str("name", "person_donations")
        c += html.controller_json("donationtypes", extlookups.get_donation_types(dbo))
        c += html.controller_json("accounts", financial.get_accounts(dbo))
        c += html.controller_json("paymenttypes", extlookups.get_payment_types(dbo))
        c += html.controller_json("frequencies", extlookups.get_donation_frequencies(dbo))
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_json("rows", donations)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("donations", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        dbo = session.dbo
        if mode == "create":
            users.check_permission(session, users.ADD_DONATION)
            return financial.insert_donation_from_form(dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_DONATION)
            financial.update_donation_from_form(dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_DONATION)
            for did in post.integer_list("ids"):
                financial.delete_donation(dbo, session.user, did)
        elif mode == "receive":
            users.check_permission(session, users.CHANGE_DONATION)
            for did in post.integer_list("ids"):
                financial.receive_donation(dbo, session.user, did)
        elif mode == "personmovements":
            users.check_permission(session, users.VIEW_MOVEMENT)
            return html.json(extmovement.get_person_movements(dbo, post.integer("personid")))

class person_embed:
    def GET(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(mode = "lookup"), session.locale)
        mode = post["mode"]
        if mode == "lookup":
            rv = {}
            rv["towns"] = "|".join(extperson.get_towns(dbo))
            rv["counties"] = "|".join(extperson.get_counties(dbo))
            rv["towncounties"] = "|".join(extperson.get_town_to_county(dbo))
            rv["flags"] = extlookups.get_person_flags(dbo)
            rv["sites"] = extlookups.get_sites(dbo)
            web.header("Content-Type", "application/json")
            web.header("Cache-Control", "max-age=60")
            return html.json(rv)

    def POST(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_PERSON)
        dbo = session.dbo
        post = utils.PostedData(web.input(mode = "find", filter = "all", id = 0), session.locale)
        mode = post["mode"]
        q = post["q"]
        web.header("Content-Type", "application/json")
        if mode == "find":
            rows = extperson.get_person_find_simple(dbo, q, session.user, post["filter"], users.check_permission_bool(session, users.VIEW_STAFF), users.check_permission_bool(session, users.VIEW_VOLUNTEER), 100)
            al.debug("find '%s' got %d rows" % (str(web.ctx.query), len(rows)), "code.person_embed", dbo)
            return html.json(rows)
        elif mode == "id":
            p = extperson.get_person(dbo, post.integer("id"))
            if p is None:
                al.error("get person by id %d found no records." % (post.integer("id")), "code.person_embed", dbo)
                raise web.notfound()
            else:
                al.debug("get person by id %d got '%s'" % (post.integer("id"), p["OWNERNAME"]), "code.person_embed", dbo)
                return html.json((p,))
        elif mode == "similar":
            surname = post["surname"]
            forenames = post["forenames"]
            address = post["address"]
            email = post["emailaddress"]
            p = extperson.get_person_similar(dbo, email, surname, forenames, address)
            if len(p) == 0:
                al.debug("No similar people found for %s, %s, %s" % (surname, forenames, address), "code.person_embed", dbo)
            else:
                al.debug("found similar people for %s, %s, %s: got %d records" % (surname, forenames, address, len(p)), "code.person_embed", dbo)
            return html.json(p)
        elif mode == "add":
            users.check_permission(session, users.ADD_PERSON)
            al.debug("add new person", "code.person_embed", dbo)
            pid = extperson.insert_person_from_form(dbo, post, session.user)
            p = extperson.get_person(dbo, pid)
            return html.json((p,))

class person_find:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_PERSON)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        flags = extlookups.get_person_flags(dbo)
        al.debug("lookups loaded", "code.person_find", dbo)
        s = html.header("", session)
        c = html.controller_json("flags", flags)
        c += html.controller_json("users", users.get_users(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("person_find", s, c, post["json"] == "true")

class person_find_results:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_PERSON)
        dbo = session.dbo
        l = session.locale
        post = utils.PostedData(web.input(mode = "", q = ""), session.locale)
        mode = post["mode"]
        q = post["q"]
        if mode == "SIMPLE":
            results = extperson.get_person_find_simple(dbo, q, session.user, "all", users.check_permission_bool(session, users.VIEW_STAFF), users.check_permission_bool(session, users.VIEW_VOLUNTEER), configuration.record_search_limit(dbo))
        else:
            results = extperson.get_person_find_advanced(dbo, post.data, session.user, users.check_permission_bool(session, users.VIEW_STAFF), configuration.record_search_limit(dbo))
        add = None
        if len(results) > 0: 
            add = extadditional.get_additional_fields_ids(dbo, results, "person")
        al.debug("found %d results for %s" % (len(results), str(web.ctx.query)), "code.person_find_results", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", results)
        c += html.controller_json("additional", add)
        c += html.controller_str("resultsmessage", _("Search returned {0} results.", l).format(len(results)))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("person_find_results", s, c, post["json"] == "true")

class person_investigation:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_INVESTIGATION)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        p = extperson.get_person(dbo, post.integer("id"))
        if p is None: raise web.notfound()
        investigation = extperson.get_investigation(dbo, post.integer("id"))
        al.debug("got %d investigation records for person %s" % (len(investigation), p["OWNERNAME"]), "code.person_investigation", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", investigation)
        c += html.controller_json("person", p)
        c += html.controller_json("tabcounts", extperson.get_satellite_counts(dbo, p["ID"])[0])
        s += html.controller(c)
        s += html.footer()
        return full_or_json("person_investigation", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_INVESTIGATION)
            return str(extperson.insert_investigation_from_form(session.dbo, session.user, post))
        elif mode == "update":
            users.check_permission(session, users.CHANGE_INVESTIGATION)
            extperson.update_investigation_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_INVESTIGATION)
            for did in post.integer_list("ids"):
                extperson.delete_investigation(session.dbo, session.user, did)

class person_licence:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_LICENCE)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        p = extperson.get_person(dbo, post.integer("id"))
        if p is None: raise web.notfound()
        licences = financial.get_person_licences(dbo, post.integer("id"))
        al.debug("got %d licences" % len(licences), "code.person_licence", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "person_licence")
        c += html.controller_json("rows", licences)
        c += html.controller_json("person", p)
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_json("tabcounts", extperson.get_satellite_counts(dbo, p["ID"])[0])
        c += html.controller_json("licencetypes", extlookups.get_licence_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("licence", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_LICENCE)
            return financial.insert_licence_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_LICENCE)
            financial.update_licence_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_LICENCE)
            for lid in post.integer_list("ids"):
                financial.delete_licence(session.dbo, session.user, lid)

class person_log:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_LOG)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0, filter = -2), session.locale)
        logfilter = post.integer("filter")
        if logfilter == -2: logfilter = configuration.default_log_filter(dbo)
        p = extperson.get_person(dbo, post.integer("id"))
        if p is None: raise web.notfound()
        logs = extlog.get_logs(dbo, extlog.PERSON, post.integer("id"), logfilter)
        s = html.header("", session)
        c = html.controller_str("name", "person_log")
        c += html.controller_int("linkid", post.integer("id"))
        c += html.controller_int("filter", logfilter)
        c += html.controller_json("rows", logs)
        c += html.controller_json("person", p)
        c += html.controller_json("tabcounts", extperson.get_satellite_counts(dbo, p["ID"])[0])
        c += html.controller_json("logtypes", extlookups.get_log_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("log", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_LOG)
            return extlog.insert_log_from_form(session.dbo, session.user, extlog.PERSON, post.integer("linkid"), post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_LOG)
            extlog.update_log_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_LOG)
            for lid in post.integer_list("ids"):
                extlog.delete_log(session.dbo, session.user, lid)

class person_lookingfor:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_PERSON)
        post = utils.PostedData(web.input(), session.locale)
        dbo = session.dbo
        web.header("Content-Type", "text/html")
        if post.integer("personid") == 0:
            return configuration.lookingfor_report(dbo)
        else:
            return extperson.lookingfor_report(dbo, session.user, post.integer("personid"))

class person_links:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_PERSON_LINKS)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        links = extperson.get_links(dbo, post.integer("id"))
        p = extperson.get_person(dbo, post.integer("id"))
        if p is None: raise web.notfound()
        title = p["OWNERNAME"]
        s = html.header(title, session)
        al.debug("got %d person links" % len(links), "code.person_links", dbo)
        c = html.controller_json("links", links)
        c += html.controller_json("person", p)
        c += html.controller_json("tabcounts", extperson.get_satellite_counts(dbo, p["ID"])[0])
        s += html.controller(c)
        s += html.footer()
        return full_or_json("person_links", s, c, post["json"] == "true")

class person_media:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MEDIA)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        p = extperson.get_person(dbo, post.integer("id"))
        if p is None: raise web.notfound()
        m = extmedia.get_media(dbo, extmedia.PERSON, post.integer("id"))
        al.debug("got %d media" % len(m), "code.person_media", dbo)
        s = html.header("", session)
        c = html.controller_json("media", m)
        c += html.controller_json("person", p)
        c += html.controller_json("tabcounts", extperson.get_satellite_counts(dbo, p["ID"])[0])
        c += html.controller_bool("showpreferred", True)
        c += html.controller_int("linkid", post.integer("id"))
        c += html.controller_int("linktypeid", extmedia.PERSON)
        c += html.controller_str("name", self.__class__.__name__)
        c += html.controller_str("sigtype", ELECTRONIC_SIGNATURES)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("media", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create", filechooser={}, linkid="0", base64image = "", _unicode=False), session.locale)
        mode = post["mode"]
        dbo = session.dbo
        l = session.locale
        linkid = post.integer("linkid")
        if mode == "create":
            users.check_permission(session, users.ADD_MEDIA)
            extmedia.attach_file_from_form(dbo, session.user, extmedia.PERSON, linkid, post)
            raise web.seeother("person_media?id=%d" % linkid)
        elif mode == "createdoc":
            users.check_permission(session, users.ADD_MEDIA)
            mediaid = extmedia.create_blank_document_media(dbo, session.user, extmedia.PERSON, linkid)
            raise web.seeother("document_media_edit?id=%d&redirecturl=person_media?id=%d" % (mediaid, linkid))
        elif mode == "createlink":
            users.check_permission(session, users.ADD_MEDIA)
            mediaid = extmedia.attach_link_from_form(session.dbo, session.user, extmedia.PERSON, linkid, post)
            raise web.seeother("person_media?id=%d" % linkid)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MEDIA)
            extmedia.update_media_notes(dbo, session.user, post.integer("mediaid"), post["comments"])
        elif mode == "delete":
            users.check_permission(session, users.DELETE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.delete_media(dbo, session.user, mid)
        elif mode == "email":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                content = dbfs.get_string(dbo, m["MEDIANAME"])
                if m["MEDIANAME"].endswith("html"):
                    content = utils.fix_relative_document_uris(content, BASE_URL, MULTIPLE_DATABASES and dbo.database or "")
                utils.send_email(dbo, configuration.email(dbo), emailadd, "", m["MEDIANOTES"], post["emailnote"], "html", content, m["MEDIANAME"])
            return emailadd
        elif mode == "emailpdf":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                if not m["MEDIANAME"].endswith("html"): continue
                content = dbfs.get_string(dbo, m["MEDIANAME"])
                contentpdf = utils.html_to_pdf(content, BASE_URL, MULTIPLE_DATABASES and dbo.database or "")
                utils.send_email(dbo, configuration.email(dbo), emailadd, "", m["MEDIANOTES"], post["emailnote"], "plain", contentpdf, "document.pdf")
            return emailadd
        elif mode == "emailsign":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            body = []
            body.append(post["emailnote"] + "\n\n")
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                if not m["MEDIANAME"].endswith("html"): continue
                body.append(m["MEDIANOTES"])
                body.append("%s?account=%s&method=sign_document&formid=%d" % (SERVICE_URL, dbo.database, mid))
                body.append("")
            utils.send_email(dbo, configuration.email(dbo), emailadd, "", _("Document signing request", l), "\n".join(body), "plain")
            return emailadd
        elif mode == "sign":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.sign_document(session.dbo, session.user, mid, post["sig"], post["signdate"])
        elif mode == "signpad":
            configuration.signpad_ids(session.dbo, session.user, post["ids"])
        elif mode == "rotateclock":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.rotate_media(dbo, session.user, mid, True)
        elif mode == "rotateanti":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.rotate_media(dbo, session.user, mid, False)
        elif mode == "web":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_web_preferred(dbo, session.user, mid)
        elif mode == "video":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_video_preferred(session.dbo, session.user, mid)
        elif mode == "doc":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_doc_preferred(dbo, session.user, mid)

class person_movements:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MOVEMENT)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        p = extperson.get_person(dbo, post.integer("id"))
        if p is None: raise web.notfound()
        movements = extmovement.get_person_movements(dbo, post.integer("id"))
        al.debug("got %d movements" % len(movements), "code.person_movements", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", movements)
        c += html.controller_json("person", p)
        c += html.controller_json("tabcounts", extperson.get_satellite_counts(dbo, p["ID"])[0])
        c += html.controller_json("movementtypes", extlookups.get_movement_types(dbo))
        c += html.controller_json("reservationstatuses", extlookups.get_reservation_statuses(dbo))
        c += html.controller_json("returncategories", extlookups.get_entryreasons(dbo))
        c += html.controller_json("templates", dbfs.get_document_templates(dbo))
        c += html.controller_str("name", self.__class__.__name__)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("movements", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_MOVEMENT)
            return extmovement.insert_movement_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MOVEMENT)
            extmovement.update_movement_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_MOVEMENT)
            for mid in post.integer_list("ids"):
                extmovement.delete_movement(session.dbo, session.user, mid)
        elif mode == "insurance":
            return extmovement.generate_insurance_number(session.dbo)

class person_new:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_PERSON)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        c = html.controller_json("towns", "|".join(extperson.get_towns(dbo)))
        c += html.controller_json("counties", "|".join(extperson.get_counties(dbo)))
        c += html.controller_json("towncounties", "|".join(extperson.get_town_to_county(dbo)))
        c += html.controller_json("additional", extadditional.get_additional_fields(dbo, 0, "person"))
        c += html.controller_json("flags", extlookups.get_person_flags(dbo))
        c += html.controller_json("sites", extlookups.get_sites(dbo))
        s += html.controller(c)
        s += html.footer()
        al.debug("add person", "code.person_new", dbo)
        return full_or_json("person_new", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_PERSON)
        utils.check_locked_db(session)
        post = utils.PostedData(web.input(), session.locale)
        personid = extperson.insert_person_from_form(session.dbo, post, session.user)
        return str(personid)

class person_rota:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_ROTA)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        p = extperson.get_person(dbo, post.integer("id"))
        if p is None: raise web.notfound()
        rota = extperson.get_person_rota(dbo, post.integer("id"))
        al.debug("got %d rota items" % len(rota), "code.person_rota", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "person_rota")
        c += html.controller_json("rows", rota)
        c += html.controller_json("person", p)
        c += html.controller_json("rotatypes", extlookups.get_rota_types(dbo))
        c += html.controller_json("worktypes", extlookups.get_work_types(dbo))
        c += html.controller_json("tabcounts", extperson.get_satellite_counts(dbo, p["ID"])[0])
        s += html.controller(c)
        s += html.footer()
        return full_or_json("rota", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_ROTA)
            return extperson.insert_rota_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_ROTA)
            extperson.update_rota_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_ROTA)
            for rid in post.integer_list("ids"):
                extperson.delete_rota(session.dbo, session.user, rid)

class staff_rota:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_ROTA)
        dbo = session.dbo
        post = utils.PostedData(web.input(start = ""), session.locale)
        startdate = post.date("start")
        if startdate is None: startdate = monday_of_week(now())
        rota = extperson.get_rota(dbo, startdate, add_days(startdate, 7))
        al.debug("got %d rota items" % len(rota), "code.staff_rota", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "staff_rota")
        c += html.controller_json("rows", rota)
        c += html.controller_json("flags", extlookups.get_person_flags(dbo))
        c += html.controller_json("flagsel", post["flags"])
        c += html.controller_date("startdate", startdate)
        c += html.controller_date("prevdate", subtract_days(startdate, 7))
        c += html.controller_date("nextdate", add_days(startdate, 7))
        c += html.controller_json("rotatypes", extlookups.get_rota_types(dbo))
        c += html.controller_json("worktypes", extlookups.get_work_types(dbo))
        c += html.controller_json("staff", extperson.get_staff_volunteers(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("staff_rota", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_ROTA)
            return extperson.insert_rota_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_ROTA)
            extperson.update_rota_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_ROTA)
            for rid in post.integer_list("ids"):
                extperson.delete_rota(session.dbo, session.user, rid)
        elif mode == "deleteweek":
            users.check_permission(session, users.DELETE_ROTA)
            extperson.delete_rota_week(session.dbo, session.user, post.date("startdate"))
        elif mode == "clone":
            users.check_permission(session, users.ADD_ROTA)
            startdate = post.date("startdate")
            newdate = post.date("newdate")
            flags = post["flags"]
            extperson.clone_rota_week(session.dbo, session.user, startdate, newdate, flags)

class person_traploan:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_TRAPLOAN)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        p = extperson.get_person(dbo, post.integer("id"))
        if p is None: raise web.notfound()
        traploans = extanimalcontrol.get_person_traploans(dbo, post.integer("id"))
        al.debug("got %d trap loans" % len(traploans), "code.person_traploan", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "person_traploan")
        c += html.controller_json("rows", traploans)
        c += html.controller_json("person", p)
        c += html.controller_json("tabcounts", extperson.get_satellite_counts(dbo, p["ID"])[0])
        c += html.controller_json("traptypes", extlookups.get_trap_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("traploan", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_TRAPLOAN)
            return extanimalcontrol.insert_traploan_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_TRAPLOAN)
            extanimalcontrol.update_traploan_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_TRAPLOAN)
            for lid in post.integer_list("ids"):
                extanimalcontrol.delete_traploan(session.dbo, session.user, lid)

class person_vouchers:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_VOUCHER)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        p = extperson.get_person(dbo, post.integer("id"))
        if p is None: raise web.notfound()
        vouchers = financial.get_vouchers(dbo, post.integer("id"))
        al.debug("got %d vouchers" % len(vouchers), "code.person_vouchers", dbo)
        s = html.header("", session)
        c = html.controller_json("vouchertypes", extlookups.get_voucher_types(dbo))
        c += html.controller_json("rows", vouchers)
        c += html.controller_json("person", p)
        c += html.controller_json("tabcounts", extperson.get_satellite_counts(dbo, p["ID"])[0])
        s += html.controller(c)
        s += html.footer()
        return full_or_json("person_vouchers", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_VOUCHER)
            return financial.insert_voucher_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_VOUCHER)
            financial.update_voucher_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_VOUCHER)
            for vid in post.integer_list("ids"):
                financial.delete_voucher(session.dbo, session.user, vid)

class publish:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.USE_INTERNET_PUBLISHER)
        dbo = session.dbo
        post = utils.PostedData(web.input(mode="page"), session.locale)
        mode = post["mode"]
        failed = False
        al.debug("publish started for mode %s" % mode, "code.publish", dbo)
        # If a publisher is already running and we have a mode, mark
        # a failure starting
        if async.is_task_running(dbo):
            al.debug("publish already running, not starting new publish", "code.publish", dbo)
        else:
            # If a publishing mode is requested, start that publisher
            # running on a background thread
            pc = extpublish.PublishCriteria(configuration.publisher_presets(dbo))
            if mode == "ftp":
                h = extpublish.HTMLPublisher(dbo, pc, session.user)
                h.start()
            elif mode == "pf": 
                pf = extpublish.PetFinderPublisher(dbo, pc)
                pf.start()
            elif mode == "ap": 
                ap = extpublish.AdoptAPetPublisher(dbo, pc)
                ap.start()
            elif mode == "rg": 
                rg = extpublish.RescueGroupsPublisher(dbo, pc)
                rg.start()
            elif mode == "mp": 
                mp = extpublish.MeetAPetPublisher(dbo, pc)
                mp.start()
            elif mode == "hlp": 
                mp = extpublish.HelpingLostPetsPublisher(dbo, pc)
                mp.start()
            elif mode == "pl": 
                mp = extpublish.PetLinkPublisher(dbo, pc)
                mp.start()
            elif mode == "pr": 
                mp = extpublish.PetRescuePublisher(dbo, pc)
                mp.start()
            elif mode == "p9": 
                pn = extpublish.Pets911Publisher(dbo, pc)
                pn.start()
            elif mode == "st": 
                st = extpublish.SmartTagPublisher(dbo, pc)
                st.start()
            elif mode == "abuk": 
                mp = extpublish.AnibaseUKPublisher(dbo, pc)
                mp.start()
            elif mode == "fa":
                mp = extpublish.FoundAnimalsPublisher(dbo, pc)
                mp.start()
            elif mode == "pcuk": 
                mp = extpublish.PetsLocatedUKPublisher(dbo, pc)
                mp.start()
            elif mode == "ptuk": 
                mp = extpublish.PETtracUKPublisher(dbo, pc)
                mp.start()
            elif mode == "veha":
                mp = extpublish.HomeAgainPublisher(dbo, pc)
                mp.start()
            elif mode == "vear":
                mp = extpublish.AKCReunitePublisher(dbo, pc)
                mp.start()
        s = html.header("", session)
        c = html.controller_bool("failed", failed)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("publish", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="poll"), session.locale)
        mode = post["mode"]
        dbo = session.dbo
        if mode == "poll":
            users.check_permission(session, users.USE_INTERNET_PUBLISHER)
            return "%s|%d|%s" % (async.get_task_name(dbo), async.get_progress_percent(dbo), async.get_last_error(dbo))
        elif mode == "stop":
            async.set_cancel(dbo, True)

class publish_logs:
    def GET(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(view = ""), session.locale)
        if post["view"] == "":
            s = html.header("", session)
            logs = extpublish.get_publish_logs(dbo)
            al.debug("viewing %d publishing logs" % len(logs), "code.publish_logs", dbo)
            c = html.controller_json("rows", logs)
            s += html.controller(c)
            s += html.footer()
            return full_or_json("publish_logs", s, c, post["json"] == "true")
        else:
            al.debug("viewing log file %s" % post["view"], "code.publish_logs", dbo)
            web.header("Content-Type", "text/plain")
            web.header("Cache-Control", "max-age=10000000")
            web.header("Content-Disposition", "inline; filename=\"%s\"" % post["view"])
            return extpublish.get_publish_log(dbo, post.integer("view"))

class publish_options:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.PUBLISH_OPTIONS)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        c = html.controller_json("locations", extlookups.get_internal_locations(dbo))
        c += html.controller_str("publishurl", MULTIPLE_DATABASES_PUBLISH_URL)
        c += html.controller_json("flags", extlookups.get_animal_flags(dbo))
        c += html.controller_bool("hasftpoverride", MULTIPLE_DATABASES_PUBLISH_FTP is not None and not configuration.publisher_ignore_ftp_override(dbo))
        c += html.controller_bool("hasfoundanimals", FOUNDANIMALS_FTP_USER != "")
        c += html.controller_bool("haspetslocated", PETSLOCATED_FTP_USER != "")
        c += html.controller_bool("hassmarttag", SMARTTAG_FTP_USER != "")
        c += html.controller_bool("hasvevendor", VETENVOY_US_VENDOR_PASSWORD != "")
        c += html.controller_bool("hasvesys", VETENVOY_US_VENDOR_USERID != "")
        c += html.controller_bool("haspetrescue", PETRESCUE_FTP_HOST != "")
        c += html.controller_json("logtypes", extlookups.get_log_types(dbo))
        c += html.controller_json("styles", dbfs.get_html_publisher_templates(dbo))
        c += html.controller_json("users", users.get_users(dbo))
        s += html.controller(c)
        s += html.footer()
        al.debug("loaded lookups", "code.publish_options", dbo)
        return full_or_json("publish_options", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="save"), session.locale)
        mode = post["mode"]
        if mode == "save":
            users.check_permission(session, users.PUBLISH_OPTIONS)
            configuration.csave(session.dbo, session.user, post)
            users.update_session(session)
        elif mode == "vesignup":
            users.check_permission(session, users.PUBLISH_OPTIONS)
            userid, userpwd = extpublish.VetEnvoyUSMicrochipPublisher.signup(session.dbo, post)
            return "%s,%s" % (userid, userpwd)

class report:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_REPORT)
        post = utils.PostedData(web.input(id = "0", mode = "criteria"), session.locale)
        mode = post["mode"]
        dbo = session.dbo
        user = session.user
        crid = post.integer("id")
        # Make sure this user has a role that can view the report
        extreports.check_view_permission(session, crid)
        crit = extreports.get_criteria_controls(session.dbo, crid, locationfilter = session.locationfilter, siteid = session.siteid) 
        web.header("Content-Type", "text/html")
        web.header("Cache-Control", "no-cache")
        # If the report doesn't take criteria, just show it
        if crit == "":
            al.debug("report %d has no criteria, displaying" % crid, "code.report", dbo)
            return extreports.execute(dbo, crid, user)
        # If we're in criteria mode (and there are some to get here), ask for them
        elif mode == "criteria":
            title = extreports.get_title(dbo, crid)
            al.debug("building criteria form for report %d %s" % (crid, title), "code.report", dbo)
            s = html.header(title, session)
            s += html.heading(title)
            s += "<div id=\"criteriaform\">"
            s += "<input data-post=\"id\" type=\"hidden\" value=\"%d\" />" % crid
            s += "<input data-post=\"mode\" type=\"hidden\" value=\"exec\" />"
            s += crit
            s += "</div>"
            s += html.footing()
            c = html.controller_str("title", title)
            s += html.controller(c)
            s += html.footer()
            return full_or_json("report", s, "", post["json"] == "true")
        # The user has entered the criteria and we're in exec mode, unpack
        # the criteria and run the report
        elif mode == "exec":
            al.debug("got criteria (%s), executing report %d" % (str(post.data), crid), "code.report", dbo)
            p = extreports.get_criteria_params(dbo, crid, post)
            return extreports.execute(dbo, crid, user, p)

class report_export:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_REPORT)
        dbo = session.dbo
        l = session.locale
        post = utils.PostedData(web.input(id = "0", mode = "criteria"), l)
        mode = post["mode"]
        crid = post.integer("id")
        # No report param passed, show the list of reports for export
        if crid == 0:
            reports = extreports.get_available_reports(dbo)
            al.debug("exporting %d reports" % len(reports), "code.report_export", dbo)
            s = html.header("", session)
            c = html.controller_json("rows", reports)
            s += html.controller(c)
            s += html.footer()
            return full_or_json("report_export", s, c, post["json"] == "true")
        elif mode == "criteria":
            # Make sure this user has a role that can view the report
            extreports.check_view_permission(session, crid)
            crit = extreports.get_criteria_controls(dbo, crid)
            title = extreports.get_title(dbo, post.integer("id"))
            filename = title.replace(" ", "_").replace("\"", "").replace("'", "").lower()
            # If this report has no criteria, go straight to CSV export instead
            if crit == "":
                al.debug("report %d has no criteria, exporting to CSV" % post.integer("id"), "code.report_export", dbo)
                rows, cols = extreports.execute_query(dbo, crid, session.user, [])
                web.header("Content-Type", "text/csv")
                web.header("Content-Disposition", u"attachment; filename=\"" + utils.decode_html(filename) + u".csv\"")
                return utils.csv(l, rows, cols, True)
            # If we're in criteria mode (and there are some to get here), ask for them
            title = extreports.get_title(dbo, crid)
            al.debug("building criteria form for report %d %s" % (crid, title), "code.report", dbo)
            s = html.header(title, session)
            c = html.controller_bool("norows", True)
            s += html.controller(c)
            s += html.heading(title)
            s += "<div id=\"criteriaform\">"
            s += "<input data-post=\"id\" type=\"hidden\" value=\"%d\" />" % crid
            s += "<input data-post=\"mode\" type=\"hidden\" value=\"exec\" />"
            s += crit
            s += "</div>"
            s += html.footing()
            s += html.footer()
            return full_or_json("report_export", s, c, post["json"] == "true")
        elif mode == "exec":
            title = extreports.get_title(dbo, post.integer("id"))
            filename = title.replace(" ", "_").replace("\"", "").replace("'", "").lower()
            p = extreports.get_criteria_params(dbo, crid, post)
            rows, cols = extreports.execute_query(dbo, crid, session.user, p)
            web.header("Content-Type", "text/csv")
            web.header("Content-Disposition", u"attachment; filename=\"" + utils.decode_html(filename) + u".csv\"")
            return utils.csv(l, rows, cols, True)

class report_images:
    def GET(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        images = dbfs.get_report_images(dbo)
        al.debug("got %d extra images" % len(images), "code.report_images", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", images)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("report_images", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        post = utils.PostedData(web.input(mode="create", filechooser={}), session.locale)
        mode = post["mode"]
        if mode == "create":
            dbfs.upload_report_image(dbo, post.data.filechooser)
            users.update_session(session)
            raise web.seeother("report_images")
        elif mode == "delete":
            for i in post["ids"].split(","):
                if i != "" and not i.endswith("nopic.jpg"): dbfs.delete_filepath(dbo, "/reports/" + i)
            users.update_session(session)
        elif mode == "rename":
            dbfs.rename_file(dbo, "/reports", post["oldname"], post["newname"])

class reports:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_REPORT)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        reports = extreports.get_reports(dbo)
        header = dbfs.get_string(dbo, "head.html", "/reports")
        if header == "": header = dbfs.get_string(dbo, "head.dat", "/reports")
        footer = dbfs.get_string(dbo, "foot.html", "/reports")
        if footer == "": footer = dbfs.get_string(dbo, "foot.dat", "/reports")
        al.debug("editing %d reports" % len(reports), "code.reports", dbo)
        s = html.header("", session)
        c = html.controller_json("categories", "|".join(extreports.get_categories(dbo)))
        c += html.controller_json("header", header)
        c += html.controller_json("footer", footer)
        c += html.controller_json("roles", users.get_roles(dbo))
        c += html.controller_json("rows", reports)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("reports", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        dbo = session.dbo
        if mode == "create":
            users.check_permission(session, users.ADD_REPORT)
            rid = extreports.insert_report_from_form(dbo, session.user, post)
            users.update_session(session)
            return rid
        elif mode == "update":
            users.check_permission(session, users.CHANGE_REPORT)
            extreports.update_report_from_form(dbo, session.user, post)
            users.update_session(session)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_REPORT)
            for rid in post.integer_list("ids"):
                extreports.delete_report(dbo, session.user, rid)
            users.update_session(session)
        elif mode == "sql":
            users.check_permission(session, users.USE_SQL_INTERFACE)
            extreports.check_sql(dbo, session.user, post["sql"])
        elif mode == "genhtml":
            users.check_permission(session, users.USE_SQL_INTERFACE)
            return extreports.generate_html(dbo, session.user, post["sql"])
        elif mode == "headfoot":
            users.check_permission(session, users.CHANGE_REPORT)
            dbfs.put_string_filepath(dbo, "/reports/head.html", post["header"])
            dbfs.put_string_filepath(dbo, "/reports/foot.html", post["footer"])
        elif mode == "smcomlist":
            return html.json(extreports.get_smcom_reports(dbo))
        elif mode == "smcominstall":
            users.check_permission(session, users.ADD_REPORT)
            extreports.install_smcom_reports(dbo, session.user, post.integer_list("ids"))
            users.update_session(session)

class roles:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.EDIT_USER)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        roles = users.get_roles(dbo)
        al.debug("editing %d roles" % len(roles), "code.roles", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", roles)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("roles", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.EDIT_USER)
            users.insert_role_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.EDIT_USER)
            users.update_role_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.EDIT_USER)
            for rid in post.integer_list("ids"):
                users.delete_role(session.dbo, session.user, rid)

class schemajs:
    def GET(self):
        # Return schema of all database tables
        if utils.is_loggedin(session) and session.dbo is not None:
            dbo = session.dbo
            web.header("Content-Type", "text/javascript")
            web.header("Cache-Control", "max-age=86400")
            tobj = {}
            for t in dbupdate.TABLES:
                try:
                    rows = db.query(dbo, "SELECT * FROM %s LIMIT 1" % t)
                    if len(rows) != 0:
                        tobj[t] = rows[0]
                except Exception,err:
                    al.error("%s" % str(err), "code.schemajs", dbo)
            return "schema = %s;" % html.json(tobj)
        else:
            # Not logged in
            web.header("Content-Type", "text/javascript")
            web.header("Cache-Control", "no-cache")
            return ""

class search:
    def GET(self):
        utils.check_loggedin(session, web)
        dbo = session.dbo
        l = session.locale
        post = utils.PostedData(web.input(), session.locale)
        q = post["q"]
        title = _("Search Results for '{0}'", l).format(q)
        results, timetaken, explain, sortname = extsearch.search(dbo, session, q)
        is_large_db = ""
        if dbo.is_large_db: is_large_db = " (indexed only)"
        al.debug("searched for '%s', got %d results in %s, sorted %s %s" % (q, len(results), timetaken, sortname, is_large_db), "code.search", dbo)
        s = html.header("", session)
        c = html.controller_json("results", results)
        c += html.controller_str("timetaken", str(round(timetaken, 2)))
        c += html.controller_str("title", title)
        c += html.controller_str("explain", explain)
        c += html.controller_str("sortname", sortname)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("search", s, c, post["json"] == "true")

class service:
    def handle(self):
        post = utils.PostedData(web.input(filechooser = {}), LOCALE)
        contenttype, maxage, response = extservice.handler(post, remote_ip(),  web.ctx.env.get("HTTP_REFERER", ""), web.ctx.query)
        if contenttype == "redirect":
            raise web.seeother(response)
        else:
            web.header("Content-Type", contenttype)
            web.header("Cache-Control", "max-age=%d" % maxage)
            return response
    def POST(self):
        return self.handle()
    def GET(self):
        return self.handle()

class shelterview:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_ANIMAL)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        animals = extanimal.get_shelterview_animals(dbo, session.locationfilter, session.siteid)
        perrow = configuration.main_screen_animal_link_max(dbo)
        al.debug("got %d animals for shelterview" % (len(animals)), "code.shelterview", dbo)
        s = html.header("", session)
        c = html.controller_json("animals", extanimal.get_animals_brief(animals))
        c += html.controller_json("flags", extlookups.get_animal_flags(dbo))
        c += html.controller_json("fosterers", extperson.get_shelterview_fosterers(dbo))
        c += html.controller_json("locations", extlookups.get_internal_locations(dbo, session.locationfilter, session.siteid))
        c += html.controller_int("perrow", perrow)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("shelterview", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="move"), session.locale)
        mode = post["mode"]
        if mode == "movelocation":
            users.check_permission(session, users.CHANGE_ANIMAL)
            extanimal.update_location_unit(session.dbo, session.user, post.integer("animalid"), post.integer("locationid"))
        if mode == "moveunit":
            users.check_permission(session, users.CHANGE_ANIMAL)
            extanimal.update_location_unit(session.dbo, session.user, post.integer("animalid"), post.integer("locationid"), post["unit"])
        if mode == "movefoster":
            users.check_permission(session, users.ADD_MOVEMENT)
            post.data["person"] = post["personid"]
            post.data["animal"] = post["animalid"]
            post.data["fosterdate"] = python2display(session.locale, now(session.dbo.timezone))
            return extmovement.insert_foster_from_form(session.dbo, session.user, post)

class smcom_my:
    def GET(self):
        utils.check_loggedin(session, web)
        if session.superuser == 1: smcom.go_smcom_my(session.dbo)

class sql:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.USE_SQL_INTERFACE)
        l = session.locale
        dbo = session.dbo
        post = utils.PostedData(web.input(), l)
        al.debug("%s opened SQL interface" % str(session.user), "code.sql", dbo)
        s = html.header("", session)
        c = html.controller_json("tables", dbupdate.TABLES + dbupdate.VIEWS)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("sql", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="exec", sql = "", sqlfile = "", table = ""), session.locale)
        mode = post["mode"]
        dbo = session.dbo
        if mode == "cols":
            try:
                if post["table"].strip() == "": return ""
                rows = db.query(dbo, "SELECT * FROM %s LIMIT 1" % post["table"])
                if len(rows) == 0: return ""
                return "|".join(sorted(rows[0].iterkeys()))
            except Exception,err:
                al.error("%s" % str(err), "code.sql", dbo)
                raise utils.ASMValidationError(str(err))
        elif mode == "exec":
            users.check_permission(session, users.USE_SQL_INTERFACE)
            utils.check_locked_db(session)
            sql = post["sql"].strip()
            return self.exec_sql(dbo, sql)
        elif mode == "execfile":
            users.check_permission(session, users.USE_SQL_INTERFACE)
            utils.check_locked_db(session)
            sql = post["sqlfile"].strip()
            web.header("Content-Type", "text/plain")
            return self.exec_sql_from_file(dbo, sql)

    def exec_sql(self, dbo, sql):
        l = dbo.locale
        rowsaffected = 0
        try:
            for q in db.split_queries(sql):
                if q == "": continue
                al.info("%s query: %s" % (session.user, q), "code.sql", dbo)
                if q.lower().startswith("select") or q.lower().startswith("show"):
                    return html.table(db.query(dbo, q))
                else:
                    rowsaffected += db.execute(dbo, q)
                    configuration.db_view_seq_version(dbo, "0")
            return _("{0} rows affected.", l).format(rowsaffected)
        except Exception,err:
            al.error("%s" % str(err), "code.sql", dbo)
            raise utils.ASMValidationError(str(err))

    def exec_sql_from_file(self, dbo, sql):
        l = dbo.locale
        output = []
        for q in db.split_queries(sql):
            try:
                if q == "": continue
                al.info("%s query: %s" % (session.user, q), "code.sql", dbo)
                if q.lower().startswith("select") or q.lower().startswith("show"):
                    output.append(str(db.query(dbo, q)))
                else:
                    rowsaffected = db.execute(dbo, q)
                    configuration.db_view_seq_version(dbo, "0")
                    output.append(_("{0} rows affected.", l).format(rowsaffected))
            except Exception,err:
                al.error("%s" % str(err), "code.sql", dbo)
                output.append("ERROR: %s" % str(err))
        return "\n\n".join(output)

class sql_dump:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.USE_SQL_INTERFACE)
        l = session.locale
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        mode = post["mode"]
        web.header("Content-Type", "text/plain")
        if LARGE_FILES_CHUNKED: web.header("Transfer-Encoding", "chunked")
        if mode == "dumpsql":
            al.info("%s executed SQL database dump" % str(session.user), "code.sql", dbo)
            web.header("Content-Disposition", "attachment; filename=\"dump.sql\"")
            for x in dbupdate.dump(dbo): yield x
        elif mode == "dumpsqlnomedia":
            al.info("%s executed SQL database dump (without media)" % str(session.user), "code.sql", dbo)
            web.header("Content-Disposition", "attachment; filename=\"dump.sql\"")
            for x in dbupdate.dump(dbo, includeDBFS = False): yield x
        elif mode == "dumpsqlasm2":
            # ASM2_COMPATIBILITY
            al.info("%s executed SQL database dump (ASM2 HSQLDB)" % str(session.user), "code.sql", dbo)
            web.header("Content-Disposition", "attachment; filename=\"asm2.sql\"")
            for x in dbupdate.dump_hsqldb(dbo): yield x
        elif mode == "dumpsqlasm2nomedia":
            # ASM2_COMPATIBILITY
            al.info("%s executed SQL database dump (ASM2 HSQLDB, without media)" % str(session.user), "code.sql", dbo)
            web.header("Content-Disposition", "attachment; filename=\"asm2.sql\"")
            for x in dbupdate.dump_hsqldb(dbo, includeDBFS = False): yield x
        elif mode == "animalcsv":
            al.debug("%s executed CSV animal dump" % str(session.user), "code.sql", dbo)
            web.header("Content-Disposition", "attachment; filename=\"animal.csv\"")
            yield utils.csv(l, extanimal.get_animal_find_advanced(dbo, { "logicallocation" : "all", "includedeceased": "true", "includenonshelter": "true" }))
        elif mode == "personcsv":
            al.debug("%s executed CSV person dump" % str(session.user), "code.sql", dbo)
            web.header("Content-Disposition", "attachment; filename=\"person.csv\"")
            yield utils.csv(l, extperson.get_person_find_simple(dbo, "", session.user, "all", True, True, 0))
        elif mode == "incidentcsv":
            al.debug("%s executed CSV incident dump" % str(session.user), "code.sql", dbo)
            web.header("Content-Disposition", "attachment; filename=\"incident.csv\"")
            yield utils.csv(l, extanimalcontrol.get_animalcontrol_find_advanced(dbo, { "filter" : "" }, 0))

class stocklevel:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_STOCKLEVEL)
        dbo = session.dbo
        post = utils.PostedData(web.input(newlevel = "0", sortexp = "0", viewlocation = "0"), session.locale)
        levels = extstock.get_stocklevels(dbo, post.integer("viewlocation"))
        al.debug("got %d stock levels" % len(levels), "code.stocklevel", dbo)
        s = html.header("", session)
        c = html.controller_json("stocklocations", extlookups.get_stock_locations(dbo))
        c += html.controller_str("stocknames", "|".join(extstock.get_stock_names(dbo)))
        c += html.controller_json("stockusagetypes", extlookups.get_stock_usage_types(dbo))
        c += html.controller_str("stockunits", "|".join(extstock.get_stock_units(dbo)))
        c += html.controller_bool("newlevel", post.integer("newlevel") == 1)
        c += html.controller_bool("sortexp", post.integer("sortexp") == 1)
        c += html.controller_json("rows", levels)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("stocklevel", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode = "create", ids = "", duration = 0), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_STOCKLEVEL)
            for dummy in xrange(0, post.integer("quantity")):
                extstock.insert_stocklevel_from_form(session.dbo, post, session.user)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_STOCKLEVEL)
            extstock.update_stocklevel_from_form(session.dbo, post, session.user)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_STOCKLEVEL)
            for sid in post.integer_list("ids"):
                extstock.delete_stocklevel(session.dbo, session.user, sid)
        elif mode == "lastname":
            users.check_permission(session, users.VIEW_STOCKLEVEL)
            return extstock.get_last_stock_with_name(session.dbo, post["name"])

class systemusers:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.EDIT_USER)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        user = users.get_users(dbo)
        roles = users.get_roles(dbo)
        al.debug("editing %d system users" % len(user), "code.systemusers", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", user)
        c += html.controller_json("roles", roles)
        c += html.controller_json("internallocations", extlookups.get_internal_locations(dbo))
        c += html.controller_json("sites", extlookups.get_sites(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("users", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_USER)
            return users.insert_user_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.EDIT_USER)
            users.update_user_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.EDIT_USER)
            for uid in post.integer_list("ids"):
                users.delete_user(session.dbo, session.user, uid)
        elif mode == "reset":
            users.check_permission(session, users.EDIT_USER)
            for uid in post.integer_list("ids"):
                users.reset_password(session.dbo, uid, post["password"])

class test:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_TEST)
        dbo = session.dbo
        post = utils.PostedData(web.input(newtest = "0", offset = "m365"), session.locale)
        test = extmedical.get_tests_outstanding(dbo, post["offset"], session.locationfilter, session.siteid)
        al.debug("got %d tests" % len(test), "code.test", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "test")
        c += html.controller_bool("newtest", post.integer("newtest") == 1)
        c += html.controller_json("rows", test)
        c += html.controller_json("stockitems", extstock.get_stock_items(dbo))
        c += html.controller_json("stockusagetypes", extlookups.get_stock_usage_types(dbo))
        c += html.controller_json("testtypes", extlookups.get_test_types(dbo))
        c += html.controller_json("testresults", extlookups.get_test_results(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("test", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode = "create", ids = ""), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_TEST)
            return extmedical.insert_test_from_form(session.dbo, session.user, post)
        if mode == "createbulk":
            users.check_permission(session, users.ADD_TEST)
            for animalid in post.integer_list("animals"):
                post.data["animal"] = str(animalid)
                extmedical.insert_test_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_TEST)
            extmedical.update_test_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_TEST)
            for vid in post.integer_list("ids"):
                extmedical.delete_test(session.dbo, session.user, vid)
        elif mode == "perform":
            users.check_permission(session, users.CHANGE_TEST)
            newdate = post.date("newdate")
            vet = post.integer("givenvet")
            testresult = post.integer("testresult")
            for vid in post.integer_list("ids"):
                extmedical.complete_test(session.dbo, session.user, vid, newdate, testresult, vet)
            if post.integer("item") != -1:
                extstock.deduct_stocklevel_from_form(session.dbo, session.user, post)

class timeline:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_ANIMAL)
        l = session.locale
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        evts = extanimal.get_timeline(dbo, 500)
        s = html.header("", session)
        c = html.controller_json("recent", evts)
        c += html.controller_str("explain", _("Showing {0} timeline events.", l).format(len(evts)));
        s += html.controller(c)
        s += html.footer()
        al.debug("timeline events, run by %s, got %d events" % (session.user, len(evts)), "code.timeline", dbo)
        return full_or_json("timeline", s, c, post["json"] == "true")

class transport:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_TRANSPORT)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        transports = extmovement.get_active_transports(dbo)
        al.debug("got %d transports" % len(transports), "code.transport", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "transport")
        c += html.controller_json("transporttypes", extlookups.get_transport_types(dbo))
        c += html.controller_json("rows", transports)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("transport", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_TRANSPORT)
            return extmovement.insert_transport_from_form(session.dbo, session.user, post)
        elif mode == "createbulk":
            users.check_permission(session, users.ADD_TRANSPORT)
            for animalid in post.integer_list("animals"):
                post.data["animal"] = str(animalid)
                extmovement.insert_transport_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_TRANSPORT)
            extmovement.update_transport_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_TRANSPORT)
            for mid in post.integer_list("ids"):
                extmovement.delete_transport(session.dbo, session.user, mid)
        elif mode == "setstatus":
            users.check_permission(session, users.CHANGE_TRANSPORT)
            extmovement.update_transport_statuses(session.dbo, session.user, post.integer_list("ids"), post.integer("newstatus"))

class traploan:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_TRAPLOAN)
        dbo = session.dbo
        post = utils.PostedData(web.input(filter = "active"), session.locale)
        title = ""
        traploans = []
        if post["filter"] == "active":
            traploans = extanimalcontrol.get_active_traploans(dbo)
        al.debug("got %d trap loans" % len(traploans), "code.traploan", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "traploan")
        c += html.controller_str("title", title)
        c += html.controller_json("rows", traploans)
        c += html.controller_json("traptypes", extlookups.get_trap_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("traploan", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_TRAPLOAN)
            return extanimalcontrol.insert_traploan_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_TRAPLOAN)
            extanimalcontrol.update_traploan_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_TRAPLOAN)
            for lid in post.integer_list("ids"):
                extanimalcontrol.delete_traploan(session.dbo, session.user, lid)

class vaccination:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_VACCINATION)
        dbo = session.dbo
        post = utils.PostedData(web.input(newvacc = "0", offset = "m365"), session.locale)
        vacc = extmedical.get_vaccinations_outstanding(dbo, post["offset"], session.locationfilter, session.siteid)
        al.debug("got %d vaccinations" % len(vacc), "code.vaccination", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "vaccination")
        c += html.controller_bool("newvacc", post.integer("newvacc") == 1)
        c += html.controller_json("rows", vacc)
        c += html.controller_json("manufacturers", "|".join(extmedical.get_vacc_manufacturers(dbo)))
        c += html.controller_json("stockitems", extstock.get_stock_items(dbo))
        c += html.controller_json("stockusagetypes", extlookups.get_stock_usage_types(dbo))
        c += html.controller_json("vaccinationtypes", extlookups.get_vaccination_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("vaccination", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode = "create", ids = "", duration = 0), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_VACCINATION)
            return extmedical.insert_vaccination_from_form(session.dbo, session.user, post)
        if mode == "createbulk":
            users.check_permission(session, users.ADD_VACCINATION)
            for animalid in post.integer_list("animals"):
                post.data["animal"] = str(animalid)
                extmedical.insert_vaccination_from_form(session.dbo, session.user, post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_VACCINATION)
            extmedical.update_vaccination_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_VACCINATION)
            for vid in post.integer_list("ids"):
                extmedical.delete_vaccination(session.dbo, session.user, vid)
        elif mode == "given":
            users.check_permission(session, users.BULK_COMPLETE_VACCINATION)
            newdate = post.date("newdate")
            vet = post.integer("givenvet")
            rescheduledate = post.date("rescheduledate")
            reschedulecomments = post["reschedulecomments"]
            for vid in post.integer_list("ids"):
                extmedical.complete_vaccination(session.dbo, session.user, vid, newdate, vet)
                if rescheduledate is not None:
                    extmedical.reschedule_vaccination(session.dbo, session.user, vid, rescheduledate, reschedulecomments)
                if post.integer("item") != -1:
                    extmedical.update_vaccination_batch_stock(session.dbo, session.user, vid, post.integer("item"))
            if post.integer("item") != -1:
                extstock.deduct_stocklevel_from_form(session.dbo, session.user, post)
        elif mode == "required":
            users.check_permission(session, users.BULK_COMPLETE_VACCINATION)
            newdate = post.date("newdate")
            for vid in post.integer_list("ids"):
                extmedical.update_vaccination_required(session.dbo, session.user, vid, newdate)

class waitinglist:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_WAITING_LIST)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extwaitinglist.get_waitinglist_by_id(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        al.debug("opened waiting list %s %s" % (a["OWNERNAME"], a["SPECIESNAME"]), "code.waitinglist", dbo)
        s = html.header("", session)
        c = html.controller_json("animal", a)
        c += html.controller_json("additional", extadditional.get_additional_fields(dbo, a["ID"], "waitinglist"))
        if users.check_permission_bool(session, users.VIEW_AUDIT_TRAIL):
            c += html.controller_json("audit", audit.get_audit_for_link(dbo, "animalwaitinglist", a["ID"]))
        c += html.controller_json("logtypes", extlookups.get_log_types(dbo))
        c += html.controller_json("sizes", extlookups.get_sizes(dbo))
        c += html.controller_json("species", extlookups.get_species(dbo))
        c += html.controller_json("urgencies", extlookups.get_urgencies(dbo))
        c += html.controller_json("tabcounts", extwaitinglist.get_satellite_counts(dbo, a["ID"])[0])
        s += html.controller(c)
        s += html.footer()
        return full_or_json("waitinglist", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        l = session.locale
        dbo = session.dbo
        post = utils.PostedData(web.input(mode="save"), session.locale)
        mode = post["mode"]
        if mode == "save":
            users.check_permission(session, users.CHANGE_WAITING_LIST)
            extwaitinglist.update_waitinglist_from_form(dbo, post, session.user)
        elif mode == "email":
            users.check_permission(session, users.EMAIL_PERSON)
            if not extwaitinglist.send_email_from_form(dbo, session.user, post):
                raise utils.ASMError(_("Failed sending email", l))
        elif mode == "delete":
            users.check_permission(session, users.DELETE_WAITING_LIST)
            extwaitinglist.delete_waitinglist(dbo, session.user, post.integer("id"))
        elif mode == "toanimal":
            users.check_permission(session, users.ADD_ANIMAL)
            return str(extwaitinglist.create_animal(dbo, session.user, post.integer("id")))

class waitinglist_diary:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_DIARY)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extwaitinglist.get_waitinglist_by_id(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        diaries = extdiary.get_diaries(dbo, extdiary.WAITINGLIST, post.integer("id"))
        al.debug("got %d diaries" % len(diaries), "code.waitinglist_diary", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", diaries)
        c += html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extwaitinglist.get_satellite_counts(dbo, a["WLID"])[0])
        c += html.controller_str("name", "waitinglist_diary")
        c += html.controller_int("linkid", a["WLID"])
        c += html.controller_json("forlist", users.get_users_and_roles(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("diary", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_DIARY)
            return extdiary.insert_diary_from_form(session.dbo, session.user, extdiary.WAITINGLIST, post.integer("linkid"), post)
        elif mode == "update":
            users.check_permission(session, users.EDIT_ALL_DIARY_NOTES)
            extdiary.update_diary_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_DIARY)
            for did in post.integer_list("ids"):
                extdiary.delete_diary(session.dbo, session.user, did)
        elif mode == "complete":
            users.check_permission(session, users.BULK_COMPLETE_NOTES)
            for did in post.integer_list("ids"):
                extdiary.complete_diary_note(session.dbo, session.user, did)

class waitinglist_log:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_LOG)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0, filter = -2), session.locale)
        logfilter = post.integer("filter")
        if logfilter == -2: logfilter = configuration.default_log_filter(dbo)
        a = extwaitinglist.get_waitinglist_by_id(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        logs = extlog.get_logs(dbo, extlog.WAITINGLIST, post.integer("id"), logfilter)
        al.debug("got %d logs" % len(logs), "code.waitinglist_diary", dbo)
        s = html.header("", session)
        c = html.controller_str("name", "waitinglist_log")
        c += html.controller_int("linkid", post.integer("id"))
        c += html.controller_int("filter", logfilter)
        c += html.controller_json("rows", logs)
        c += html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extwaitinglist.get_satellite_counts(dbo, a["WLID"])[0])
        c += html.controller_json("logtypes", extlookups.get_log_types(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("log", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "create":
            users.check_permission(session, users.ADD_LOG)
            return extlog.insert_log_from_form(session.dbo, session.user, extlog.WAITINGLIST, post.integer("linkid"), post)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_LOG)
            extlog.update_log_from_form(session.dbo, session.user, post)
        elif mode == "delete":
            users.check_permission(session, users.DELETE_LOG)
            for lid in post.integer_list("ids"):
                extlog.delete_log(session.dbo, session.user, lid)

class waitinglist_media:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_MEDIA)
        dbo = session.dbo
        post = utils.PostedData(web.input(id = 0), session.locale)
        a = extwaitinglist.get_waitinglist_by_id(dbo, post.integer("id"))
        if a is None: raise web.notfound()
        m = extmedia.get_media(dbo, extmedia.WAITINGLIST, post.integer("id"))
        al.debug("got %d media" % len(m), "code.waitinglist_media", dbo)
        s = html.header("", session)
        c = html.controller_json("media", m)
        c += html.controller_json("animal", a)
        c += html.controller_json("tabcounts", extwaitinglist.get_satellite_counts(dbo, a["WLID"])[0])
        c += html.controller_bool("showpreferred", False)
        c += html.controller_int("linkid", post.integer("id"))
        c += html.controller_int("linktypeid", extmedia.WAITINGLIST)
        c += html.controller_str("name", self.__class__.__name__)
        c += html.controller_str("sigtype", ELECTRONIC_SIGNATURES)
        s += html.controller(c)
        s += html.footer()
        return full_or_json("media", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create", filechooser={}, linkid="0", base64image = "", _unicode=False), session.locale)
        mode = post["mode"]
        dbo = session.dbo
        l = session.locale
        linkid = post.integer("linkid")
        if mode == "create":
            users.check_permission(session, users.ADD_MEDIA)
            extmedia.attach_file_from_form(session.dbo, session.user, extmedia.WAITINGLIST, linkid, post)
            raise web.seeother("waitinglist_media?id=%d" % post.integer("linkid"))
        elif mode == "createdoc":
            users.check_permission(session, users.ADD_MEDIA)
            mediaid = extmedia.create_blank_document_media(session.dbo, session.user, extmedia.WAITINGLIST, linkid)
            raise web.seeother("document_media_edit?id=%d&redirecturl=waitinglist_media?id=%d" % (mediaid, linkid))
        elif mode == "createlink":
            users.check_permission(session, users.ADD_MEDIA)
            mediaid = extmedia.attach_link_from_form(session.dbo, session.user, extmedia.WAITINGLIST, linkid, post)
            raise web.seeother("waitinglist_media?id=%d" % linkid)
        elif mode == "update":
            users.check_permission(session, users.CHANGE_MEDIA)
            extmedia.update_media_notes(session.dbo, session.user, post.integer("mediaid"), post["comments"])
        elif mode == "delete":
            users.check_permission(session, users.DELETE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.delete_media(session.dbo, session.user, mid)
        elif mode == "email":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                content = dbfs.get_string(dbo, m["MEDIANAME"])
                if m["MEDIANAME"].endswith("html"):
                    content = utils.fix_relative_document_uris(content, BASE_URL, MULTIPLE_DATABASES and dbo.database or "")
                utils.send_email(dbo, configuration.email(dbo), emailadd, "", m["MEDIANOTES"], post["emailnote"], "html", content, m["MEDIANAME"])
            return emailadd
        elif mode == "emailpdf":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                if not m["MEDIANAME"].endswith("html"): continue
                content = dbfs.get_string(dbo, m["MEDIANAME"])
                contentpdf = utils.html_to_pdf(content, BASE_URL, MULTIPLE_DATABASES and dbo.database or "")
                utils.send_email(dbo, configuration.email(dbo), emailadd, "", m["MEDIANOTES"], "", "plain", contentpdf, "document.pdf")
            return emailadd
        elif mode == "emailsign":
            users.check_permission(session, users.EMAIL_PERSON)
            emailadd = post["email"]
            if emailadd == "" or emailadd.find("@") == -1:
                raise utils.ASMValidationError(_("Invalid email address", l))
            body = []
            body.append(post["emailnote"] + "\n\n")
            for mid in post.integer_list("ids"):
                m = extmedia.get_media_by_id(dbo, mid)
                if len(m) == 0: raise web.notfound()
                m = m[0]
                if not m["MEDIANAME"].endswith("html"): continue
                body.append(m["MEDIANOTES"])
                body.append("%s?account=%s&method=sign_document&formid=%d" % (SERVICE_URL, dbo.database, mid))
                body.append("")
            utils.send_email(dbo, configuration.email(dbo), emailadd, "", _("Document signing request", l), "\n".join(body), "plain")
            return emailadd
        elif mode == "sign":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.sign_document(session.dbo, session.user, mid, post["sig"], post["signdate"])
        elif mode == "signpad":
            configuration.signpad_ids(session.dbo, session.user, post["ids"])
        elif mode == "rotateclock":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.rotate_media(session.dbo, session.user, mid, True)
        elif mode == "rotateanti":
            users.check_permission(session, users.CHANGE_MEDIA)
            for mid in post.integer_list("ids"):
                extmedia.rotate_media(session.dbo, session.user, mid, False)
        elif mode == "web":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_web_preferred(session.dbo, session.user, mid)
        elif mode == "video":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_video_preferred(session.dbo, session.user, mid)
        elif mode == "doc":
            users.check_permission(session, users.CHANGE_MEDIA)
            mid = post.integer_list("ids")[0]
            extmedia.set_doc_preferred(session.dbo, session.user, mid)

class waitinglist_new:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_WAITING_LIST)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        s = html.header("", session)
        c = html.controller_json("species", extlookups.get_species(dbo))
        c += html.controller_json("additional", extadditional.get_additional_fields(dbo, 0, "waitinglist"))
        c += html.controller_json("sizes", extlookups.get_sizes(dbo))
        c += html.controller_json("urgencies", extlookups.get_urgencies(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("waitinglist_new", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.ADD_WAITING_LIST)
        dbo = session.dbo
        post = utils.PostedData(web.input(), session.locale)
        return str(extwaitinglist.insert_waitinglist_from_form(dbo, post, session.user))

class waitinglist_results:
    def GET(self):
        utils.check_loggedin(session, web)
        users.check_permission(session, users.VIEW_WAITING_LIST)
        dbo = session.dbo
        urgencies = extlookups.get_urgencies(dbo)
        lowest_priority = len(urgencies)
        post = utils.PostedData(web.input(priorityfloor = lowest_priority, includeremoved = 0, species = -1, size = -1, 
            namecontains = "", addresscontains = "", descriptioncontains = ""), session.locale)
        rows = extwaitinglist.get_waitinglist(dbo, post.integer("priorityfloor"), post.integer("species"), post.integer("size"),
            post["addresscontains"], post.integer("includeremoved"), post["namecontains"], post["descriptioncontains"])
        al.debug("found %d results" % (len(rows)), "code.waitinglist_results", dbo)
        s = html.header("", session)
        c = html.controller_json("rows", rows)
        c += html.controller_str("seladdresscontains", post["addresscontains"])
        c += html.controller_str("seldescriptioncontains", post["descriptioncontains"])
        c += html.controller_int("selincluderemoved", post.integer("includeremoved"))
        c += html.controller_str("selnamecontains", post["namecontains"])
        c += html.controller_int("selpriorityfloor", post.integer("priorityfloor"))
        c += html.controller_int("selspecies", post.integer("species"))
        c += html.controller_json("species", extlookups.get_species(dbo))
        c += html.controller_json("sizes", extlookups.get_sizes(dbo))
        c += html.controller_json("urgencies", urgencies)
        c += html.controller_json("yesno", extlookups.get_yesno(dbo))
        s += html.controller(c)
        s += html.footer()
        return full_or_json("waitinglist_results", s, c, post["json"] == "true")

    def POST(self):
        utils.check_loggedin(session, web)
        post = utils.PostedData(web.input(mode="create"), session.locale)
        mode = post["mode"]
        if mode == "delete":
            users.check_permission(session, users.DELETE_WAITING_LIST)
            for wid in post.integer_list("ids"):
                extwaitinglist.delete_waitinglist(session.dbo, session.user, wid)
        elif mode == "complete":
            users.check_permission(session, users.CHANGE_WAITING_LIST)
            for wid in post.integer_list("ids"):
                extwaitinglist.update_waitinglist_remove(session.dbo, session.user, wid)
        elif mode == "highlight":
            users.check_permission(session, users.CHANGE_WAITING_LIST)
            for wid in post.integer_list("ids"):
                extwaitinglist.update_waitinglist_highlight(session.dbo, wid, post["himode"])

if __name__ == "__main__":
    app.run()

