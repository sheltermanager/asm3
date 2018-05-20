#!/usr/bin/python

import os, sys

# The path to the folder containing the ASM3 modules
PATH = os.path.dirname(os.path.abspath(__file__)) + os.sep

# Put the rest of our modules on the path
sys.path.append(PATH)

import al
import additional as extadditional
import animal as extanimal
import animalcontrol as extanimalcontrol
import async
import audit
import base64
import cachemem
import clinic
import configuration
import csvimport as extcsvimport
import db, dbfs, dbupdate
import diary as extdiary
import financial
import html
from i18n import _, BUILD, translate, get_version, get_display_date_format, get_currency_prefix, get_currency_symbol, get_currency_dp, get_currency_radix, get_currency_digit_grouping, get_locales, parse_date, python2display, add_minutes, add_days, subtract_days, subtract_months, first_of_month, last_of_month, monday_of_week, sunday_of_week, first_of_year, last_of_year, now, format_currency, i18nstringsjs
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
import publishers.base
import publishers.vetenvoy
import reports as extreports
import search as extsearch
import service as extservice
import smcom
import stock as extstock
import template
import users
import utils
import waitinglist as extwaitinglist
import web
import wordprocessor
from sitedefs import BASE_URL, DEPLOYMENT_TYPE, ELECTRONIC_SIGNATURES, EMERGENCY_NOTICE, FORGOTTEN_PASSWORD, FORGOTTEN_PASSWORD_LABEL, LARGE_FILES_CHUNKED, LOCALE, GEO_PROVIDER, GEO_PROVIDER_KEY, JQUERY_UI_CSS, LEAFLET_CSS, LEAFLET_JS, MULTIPLE_DATABASES, MULTIPLE_DATABASES_TYPE, MULTIPLE_DATABASES_PUBLISH_URL, MULTIPLE_DATABASES_PUBLISH_FTP, ADMIN_EMAIL, EMAIL_ERRORS, MADDIES_FUND_TOKEN_URL, MANUAL_HTML_URL, MANUAL_PDF_URL, MANUAL_FAQ_URL, MANUAL_VIDEO_URL, MAP_LINK, MAP_PROVIDER, OSM_MAP_TILES, FOUNDANIMALS_FTP_USER, PETLINK_BASE_URL, PETRESCUE_FTP_HOST, PETSLOCATED_FTP_USER, QR_IMG_SRC, SERVICE_URL, SESSION_SECURE_COOKIE, SESSION_DEBUG, SHARE_BUTTON, SMARTTAG_FTP_USER, SMCOM_LOGIN_URL, SMCOM_PAYMENT_LINK, VETENVOY_US_VENDOR_PASSWORD, VETENVOY_US_VENDOR_USERID

CACHE_ONE_HOUR = 3600
CACHE_ONE_DAY = 86400
CACHE_ONE_WEEK = 604800
CACHE_ONE_MONTH = 2592000
CACHE_ONE_YEAR = 31536000 

def session_manager():
    """
    Sort out our session manager. We use a global in the utils module
    to hold the session to make sure if the app/code.py is reloaded it
    always gets the same session manager.
    """
    class MemCacheStore(web.session.Store):
        """ 
        A session manager that uses either an in-memory dictionary or memcache
        (if available).
        """
        def __contains__(self, key):
            rv = cachemem.get(key) is not None
            if SESSION_DEBUG: al.debug("contains(%s)=%s" % (key, rv), "MemCacheStore.__contains__")
            return rv
        def __getitem__(self, key):
            rv = cachemem.get(key)
            if SESSION_DEBUG: al.debug("getitem(%s)=%s" % (key, rv), "MemCacheStore.__getitem__")
            return rv
        def __setitem__(self, key, value):
            rv = cachemem.put(key, value, web.config.session_parameters["timeout"])
            if SESSION_DEBUG: al.debug("setitem(%s, %s)=%s" % (key, value, rv), "MemCacheStore.__setitem__")
            return rv
        def __delitem__(self, key):
            rv = cachemem.delete(key)
            if SESSION_DEBUG: al.debug("delitem(%s)=%s" % (key, rv), "MemCacheStore.__delitem__")
            return rv
        def cleanup(self, timeout):
            pass # Not needed, we assign values to memcache with timeout
    # Set session parameters, 24 hour timeout
    web.config.session_parameters["cookie_name"] = "asm_session_id"
    web.config.session_parameters["cookie_path"] = "/"
    web.config.session_parameters["timeout"] = 3600 * 24
    web.config.session_parameters["ignore_change_ip"] = True
    web.config.session_parameters["secure"] = SESSION_SECURE_COOKIE
    sess = None
    if utils.websession is None:
        sess = web.session.Session(app, MemCacheStore(), initializer={"user" : None, "dbo" : None, "locale" : None, 
            "searches" : [], "siteid": None, "locationfilter": None })
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
            s = utils.read_text_file(EMERGENCY_NOTICE)
            return s
    return ""

def generate_routes():
    """ Extract the url property from all classes and construct the route list """
    g = globals().copy()
    for name, obj in g.iteritems():
        try:
            url = getattr(obj, "url")
            if url != "" and name != "web":
                if not url.startswith("/"): url = "/%s" % url
                routes.append(url)
                routes.append(name)
        except:
            pass # Ignore objects that don't have url attributes
    return routes

class ASMEndpoint(object):
    """ Base class for ASM endpoints """
    url = ""               # The route/url to this target
    get_permissions = ( )  # List of permissions needed to GET
    post_permissions = ( ) # List of permissions needed to POST
    check_logged_in = True # Check whether we have a valid login
    login_url = "/login"   # The url to go to if not logged in

    def _params(self):
        l = session.locale
        if l is None:
            l = LOCALE
        post = utils.PostedData(web.input(filechooser = {}), l)
        return web.utils.storage( post=post, dbo=session.dbo, locale=l, user=session.user, session=session, \
            siteid = session.siteid, locationfilter = session.locationfilter )

    def check(self, permissions):
        """ Check logged in and permissions (which can be a single permission string or a list/tuple) """
        if self.check_logged_in:
            utils.check_loggedin(session, web, self.login_url)
        if isinstance(permissions, str):
            users.check_permission(session, permissions)
        else:
            for p in permissions:
                users.check_permission(session, p)

    def checkb(self, permissions):
        """ Check logged in and a single permission, returning a boolean """
        if self.check_logged_in:
            utils.check_loggedin(session, web, self.login_url)
        return users.check_permission_bool(session, permissions)

    def check_locked_db(self):
        utils.check_locked_db(session)

    def content(self, o):
        """ Virtual function: override to get the content """
        return ""

    def cache_control(self, client_ttl = 0, cache_ttl = 0):
        """ Sends a cache control header.
        client_ttl: The max-age to send for the client
        cache_ttl:  The s-maxage to send for an edge cache
        """
        if client_ttl == 0 and cache_ttl == 0:
            self.header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0")
        elif client_ttl > 0 and cache_ttl == 0:
            self.header("Cache-Control", "public, max-age=%s" % client_ttl)
        else:
            self.header("Cache-Control", "public, max-age=%s, s-maxage=%s" % (client_ttl, cache_ttl))

    def content_type(self, ct):
        """ Sends a content-type header """
        self.header("Content-Type", ct)

    def header(self, key, value):
        """ Set the response header key to value """
        web.header(key, value)

    def notfound(self):
        """ Returns a 404 """
        raise web.notfound()

    def post_all(self, o):
        """ Virtual function: override to handle postback """
        return ""

    def query(self):
        """ Returns the request query string """
        return web.ctx.query

    def redirect(self, route):
        """ Redirect to another route 
            Uses BASE_URL if a relative route is given to help CDNs. """
        if not route.startswith("http"): route = "%s/%s" % (BASE_URL, route)
        raise web.seeother(route)

    def referer(self):
        """ Returns the referer request header """
        return web.ctx.env.get("HTTP_REFERER", "")

    def reload_config(self):
        """ Reloads items in the session based on database values, invalids config.js so client reloads it """
        users.update_session(session)

    def remote_ip(self):
        """ Gets the IP address of the requester, taking account of reverse proxies """
        remoteip = web.ctx['ip']
        if "HTTP_X_FORWARDED_FOR" in web.ctx.env:
            xf = web.ctx.env["HTTP_X_FORWARDED_FOR"]
            if xf is not None and str(xf).strip() != "":
                remoteip = xf
        return remoteip

    def user_agent(self):
        """ Returns the user agent request header """
        return web.ctx.env.get("HTTP_USER_AGENT", "")

    def GET(self):
        self.check(self.get_permissions)
        return self.content(self._params())

    def POST(self):
        """ Handle a POST, deal with permissions and locked databases """
        if self.check_logged_in:
            self.check_locked_db()
        self.check(self.post_permissions)
        o = self._params()
        mode = o.post["mode"]
        if mode == "": 
            return self.post_all(o)
        else:
            # Mode has been supplied, call post_mode
            return getattr(self.__class__, "post_%s" % mode)(self, o)

class GeneratorEndpoint(ASMEndpoint):
    """Base class for endpoints that use generators for their content """
    def GET(self):
        self.check(self.get_permissions)
        for x in self.content(self._params()):
            yield x

class JSONEndpoint(ASMEndpoint):
    """ Base class for ASM endpoints that return JSON """
    js_module = ""         # The javascript module to start (can be omitted if same as url)
    url = ""               # The route/url to this target

    def controller(self, o):
        """ Virtual function to be overridden - return controller as a dict """
        pass

    def GET(self):
        """ Handle a GET, deal with permissions, session and JSON responses """
        self.check(self.get_permissions)
        o = self._params()
        c = self.controller(o)
        self.header("X-Frame-Options", "SAMEORIGIN")
        self.cache_control(0)
        if self.js_module == "":
            self.js_module = self.url
        if not o.post["json"] == "true":
            self.content_type("text/html")
            footer = "<script>\n$(document).ready(function() { " \
                "common.route_listen(); " \
                "common.module_start(\"%(js_module)s\"); " \
                "});\n</script>\n</body>\n</html>" % { "js_module": self.js_module }
            return "%s\n<script type=\"text/javascript\">\ncontroller = %s;\n</script>\n%s" % (html.header("", session), utils.json(c), footer)
        else:
            self.content_type("application/json")
            return utils.json(c)

class index(ASMEndpoint):
    url = "/"
    check_logged_in = False

    def content(self, o):
        # If there's no database structure, create it before 
        # redirecting to the login page.
        if not MULTIPLE_DATABASES:
            dbo = db.get_database()
            if not dbo.has_structure():
                self.redirect("database")
        self.redirect("main")

class database(ASMEndpoint):
    url = "database"
    check_logged_in = False

    def content(self, o):
        dbo = db.get_database()
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
                self.content_type("text/plain")
                self.header("Content-Disposition", "attachment; filename=\"setup.sql\"")
                return s
        if dbo.has_structure():
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
        self.content_type("text/html")
        return s

    def post_all(self, o):
        dbo = db.get_database()
        dbo.locale = o.post["locale"]
        dbo.installpath = PATH
        dbupdate.install(dbo)
        self.redirect("login")

class image(ASMEndpoint):
    url = "image"

    def content(self, o):
        try:
            lastmod, imagedata = extmedia.get_image_file_data(session.dbo, o.post["mode"], o.post["id"], o.post.integer("seq"), False)
        except Exception as err:
            al.error("%s" % str(err), "code.image", o.dbo)
            return ""
        if imagedata != "NOPIC":
            self.content_type("image/jpeg")
            if o.post["date"] != "":
                # if we have a date parameter, it can be used to invalidate any cache
                self.cache_control(CACHE_ONE_YEAR)
            else:
                # otherwise cache for an hour in CDNs and just for the day locally
                self.cache_control(CACHE_ONE_DAY, CACHE_ONE_HOUR)
            al.debug("mode=%s id=%s seq=%s (%s bytes)" % (o.post["mode"], o.post["id"], o.post["seq"], len(imagedata)), "image.content", o.dbo)
            return imagedata
        else:
            self.redirect("image?db=%s&mode=nopic" % o.dbo.database)

class rollupjs(ASMEndpoint):
    url = "rollup.js"
    check_logged_in = False

    def content(self, o):
        # b=build is passed as a parameter and to invalidate caching
        self.content_type("text/javascript")
        self.cache_control(CACHE_ONE_YEAR)
        rollup = cachemem.get("rollup")
        if rollup is None:
            rollup = html.asm_rollup_scripts(PATH)
            cachemem.put("rollup", rollup, 60)
        return rollup

class configjs(ASMEndpoint):
    url = "config.js"
    check_logged_in = False

    def content(self, o):
        # db is the database name and ts is the date/time the config was
        # last read upto. The ts value (config_ts) is set during login and
        # updated whenever the user posts to publish_options or options.
        # Both values are used purely to cache the config in the browser, but
        # aren't actually used by the controller here.
        # post = utils.PostedData(web.input(db = "", ts = ""), session.locale)
        if o.user is None:
            # We aren't logged in and can't do anything, don't cache an empty page
            self.content_type("text/javascript")
            self.cache_control(0)
            return ""
        dbo = o.dbo
        self.content_type("text/javascript")
        self.cache_control(CACHE_ONE_YEAR)
        realname = ""
        emailaddress = ""
        expirydate = ""
        expirydatedisplay = ""
        if smcom.active():
            expirydate = smcom.get_expiry_date(dbo)
            if expirydate is not None: 
                expirydatedisplay = python2display(o.locale, expirydate)
                expirydate = expirydate.isoformat()
        us = users.get_users(dbo, o.user)
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
        c = { "baseurl": BASE_URL,
            "serviceurl": SERVICE_URL,
            "build": BUILD,
            "locale": o.locale,
            "theme": o.session.theme,
            "user": o.session.user,
            "useremail": emailaddress,
            "userreal": realname,
            "useraccount": dbo.database,
            "useraccountalias": dbo.alias,
            "dateformat": get_display_date_format(o.locale),
            "currencysymbol": get_currency_symbol(o.locale),
            "currencydp": get_currency_dp(o.locale),
            "currencyprefix": get_currency_prefix(o.locale),
            "currencyradix": get_currency_radix(o.locale),
            "currencydigitgrouping": get_currency_digit_grouping(o.locale),
            "securitymap": o.session.securitymap,
            "superuser": o.session.superuser,
            "locationfilter": o.locationfilter,
            "siteid": o.siteid,
            "roles": o.session.roles,
            "roleids": o.session.roleids,
            "manualhtml": MANUAL_HTML_URL,
            "manualpdf": MANUAL_PDF_URL,
            "manualfaq": MANUAL_FAQ_URL,
            "manualvideo": MANUAL_VIDEO_URL,
            "smcom": smcom.active(),
            "smcomexpiry": expirydate,
            "smcomexpirydisplay": expirydatedisplay,
            "smcompaymentlink": SMCOM_PAYMENT_LINK.replace("{alias}", dbo.alias).replace("{database}", dbo.database),
            "geoprovider": geoprovider,
            "geoproviderkey": geoproviderkey,
            "jqueryuicss": JQUERY_UI_CSS,
            "leafletcss": LEAFLET_CSS,
            "leafletjs": LEAFLET_JS,
            "maplink": maplink,
            "mapprovider": mapprovider,
            "osmmaptiles": OSM_MAP_TILES,
            "hascustomlogo": dbfs.file_exists(dbo, "logo.jpg"),
            "mobileapp": o.session.mobileapp,
            "config": configuration.get_map(dbo),
            "menustructure": html.menu_structure(o.locale, 
            extreports.get_reports_menu(dbo, o.session.roleids, o.session.superuser), 
            extreports.get_mailmerges_menu(dbo, o.session.roleids, o.session.superuser))
        }
        return "asm = %s;" % utils.json(c)

class css(ASMEndpoint):
    url = "x.css"
    check_logged_in = False

    def content(self, o):
        # k=build is passed to invalidate cache
        v = o.post["v"]
        csspath = PATH + "static/css/" + v
        if v.find("..") != -1: self.notfound() # prevent escaping our PATH
        if not os.path.exists(csspath): self.notfound()
        if v == "": self.notfound()
        content = utils.read_binary_file(csspath)
        self.content_type("text/css")
        self.cache_control(CACHE_ONE_YEAR)
        return content

class i18njs(ASMEndpoint):
    url = "i18n.js"
    check_logged_in = False

    def content(self, o):
        # k=build is passed to invalidate cache
        l = o.post["l"]
        if l == "": l = LOCALE
        self.content_type("text/javascript")
        self.cache_control(CACHE_ONE_YEAR)
        return i18nstringsjs(l)

class js(ASMEndpoint):
    url = "x.js"
    check_logged_in = False

    def content(self, o):
        # k=build is passed to invalidate cache
        v = o.post["v"]
        jspath = PATH + "static/js/" + v
        if v.find("..") != -1: self.notfound() # prevent escaping our PATH
        if not os.path.exists(jspath): self.notfound()
        if v == "": self.notfound()
        content = utils.read_binary_file(jspath)
        self.content_type("text/javascript")
        self.cache_control(CACHE_ONE_YEAR)
        return content

class jserror(ASMEndpoint):
    """
    Target for logging javascript errors from the frontend.
    Nothing is returned as the UI does not expect a response.
    Errors are logged and emailed to the admin if EMAIL_ERRORS is set.
    """
    url = "jserror"

    def post_all(self, o):
        dbo = o.dbo
        post = o.post
        emailsubject = "%s @ %s" % (post["user"], post["account"])
        emailbody = "%s:\n\n%s\n\nUA: %s\nIP: %s" % (post["msg"], post["stack"], self.user_agent(), self.remote_ip())
        logmess = "%s@%s: %s %s" % (post["user"], post["account"], post["msg"], post["stack"])
        al.error(logmess, "code.jserror", dbo)
        if EMAIL_ERRORS:
            utils.send_email(dbo, ADMIN_EMAIL, ADMIN_EMAIL, "", emailsubject, emailbody, "plain")

class media(ASMEndpoint):
    url = "media"

    def content(self, o):
        lastmod, medianame, mimetype, filedata = extmedia.get_media_file_data(o.dbo, o.post.integer("id"))
        self.content_type(mimetype)
        self.header("Content-Disposition", "inline; filename=\"%s\"" % medianame)
        self.cache_control(CACHE_ONE_DAY)
        al.debug("%s %s (%s bytes)" % (medianame, mimetype, len(filedata)), "media.content", o.dbo)
        return filedata

    def log_from_media_type(self, x):
        m = {
            extmedia.ANIMAL: extlog.ANIMAL,
            extmedia.PERSON: extlog.PERSON,
            extmedia.LOSTANIMAL: extlog.LOSTANIMAL,
            extmedia.FOUNDANIMAL: extlog.FOUNDANIMAL,
            extmedia.WAITINGLIST: extlog.WAITINGLIST,
            extmedia.ANIMALCONTROL: extlog.ANIMALCONTROL
        }
        return m[x]

    def post_create(self, o):
        self.check(users.ADD_MEDIA)
        linkid = o.post.integer("linkid")
        linktypeid = o.post.integer("linktypeid")
        extmedia.attach_file_from_form(o.dbo, o.user, linktypeid, linkid, o.post)
        self.redirect("%s?id=%d" % (o.post["controller"], linkid))

    def post_createdoc(self, o):
        self.check(users.ADD_MEDIA)
        linkid = o.post.integer("linkid")
        linktypeid = o.post.integer("linktypeid")
        mediaid = extmedia.create_blank_document_media(o.dbo, o.user, linktypeid, linkid)
        self.redirect("document_media_edit?id=%d&redirecturl=%s?id=%d" % (mediaid, o.post["controller"], linkid))

    def post_createlink(self, o):
        self.check(users.ADD_MEDIA)
        linkid = o.post.integer("linkid")
        linktypeid = o.post.integer("linktypeid")
        extmedia.attach_link_from_form(o.dbo, o.user, linktypeid, linkid, o.post)
        self.redirect("%s?id=%d" % (o.post["controller"], linkid))

    def post_update(self, o):
        self.check(users.CHANGE_MEDIA)
        extmedia.update_media_notes(o.dbo, o.user, o.post.integer("mediaid"), o.post["comments"])

    def post_delete(self, o):
        self.check(users.DELETE_MEDIA)
        for mid in o.post.integer_list("ids"):
            extmedia.delete_media(o.dbo, o.user, mid)

    def post_email(self, o):
        self.check(users.EMAIL_PERSON)
        dbo = o.dbo
        post = o.post
        l = o.locale
        emailadd = post["to"]
        if emailadd == "" or emailadd.find("@") == -1:
            raise utils.ASMValidationError(_("Invalid email address", l))
        for mid in post.integer_list("ids"):
            m = extmedia.get_media_by_id(dbo, mid)
            if len(m) == 0: self.notfound()
            m = m[0]
            content = dbfs.get_string(dbo, m["MEDIANAME"])
            if m["MEDIANAME"].endswith("html"):
                content = utils.fix_relative_document_uris(content, BASE_URL, MULTIPLE_DATABASES and dbo.database or "")
            utils.send_email(dbo, post["from"], emailadd, post["cc"], m["MEDIANOTES"], post["body"], "html", content, m["MEDIANAME"])
            if post.boolean("addtolog"):
                extlog.add_log(dbo, o.user, self.log_from_media_type(m["LINKTYPEID"]), m["LINKID"], post.integer("logtype"), "[%s] %s :: %s" % (emailadd, m["MEDIANOTES"], utils.html_email_to_plain(post["body"])))
        return emailadd

    def post_emailpdf(self, o):
        self.check(users.EMAIL_PERSON)
        dbo = o.dbo
        post = o.post
        l = o.locale
        emailadd = post["to"]
        if emailadd == "" or emailadd.find("@") == -1:
            raise utils.ASMValidationError(_("Invalid email address", l))
        for mid in post.integer_list("ids"):
            m = extmedia.get_media_by_id(dbo, mid)
            if len(m) == 0: self.notfound()
            m = m[0]
            if not m["MEDIANAME"].endswith("html"): continue
            content = dbfs.get_string(dbo, m["MEDIANAME"])
            contentpdf = utils.html_to_pdf(content, BASE_URL, MULTIPLE_DATABASES and dbo.database or "")
            utils.send_email(dbo, post["from"], emailadd, post["cc"], m["MEDIANOTES"], post["body"], "html", contentpdf, "document.pdf")
            if post.boolean("addtolog"):
                extlog.add_log(dbo, o.user, self.log_from_media_type(m["LINKTYPEID"]), m["LINKID"], post.integer("logtype"), "[%s] %s :: %s" % (emailadd, m["MEDIANOTES"], utils.html_email_to_plain(post["body"])))
        return emailadd

    def post_emailsign(self, o):
        self.check(users.EMAIL_PERSON)
        dbo = o.dbo
        post = o.post
        l = o.locale
        emailadd = post["to"]
        if emailadd == "" or emailadd.find("@") == -1:
            raise utils.ASMValidationError(_("Invalid email address", l))
        body = []
        body.append(post["body"])
        for mid in post.integer_list("ids"):
            m = extmedia.get_media_by_id(dbo, mid)
            if len(m) == 0: raise web.notfound()
            m = m[0]
            if not m["MEDIANAME"].endswith("html"): continue
            body.append("<p><a href=\"%s?account=%s&method=sign_document&formid=%d\">%s</a></p>" % (SERVICE_URL, dbo.database, mid, m["MEDIANOTES"]))
            if post.boolean("addtolog"):
                extlog.add_log(dbo, o.user, self.log_from_media_type(m["LINKTYPEID"]), m["LINKID"], post.integer("logtype"), "[%s] %s :: %s" % (emailadd, _("Document signing request", l), utils.html_email_to_plain("\n".join(body))))
        utils.send_email(dbo, post["from"], emailadd, post["cc"], _("Document signing request", l), "\n".join(body), "html")
        return emailadd

    def post_sign(self, o):
        self.check(users.CHANGE_MEDIA)
        for mid in o.post.integer_list("ids"):
            extmedia.sign_document(o.dbo, o.user, mid, o.post["sig"], o.post["signdate"])

    def post_signpad(self, o):
        configuration.signpad_ids(o.dbo, o.user, o.post["ids"])

    def post_rotateclock(self, o):
        self.check(users.CHANGE_MEDIA)
        for mid in o.post.integer_list("ids"):
            extmedia.rotate_media(o.dbo, o.user, mid, True)

    def post_rotateanti(self, o):
        self.check(users.CHANGE_MEDIA)
        for mid in o.post.integer_list("ids"):
            extmedia.rotate_media(o.dbo, o.user, mid, False)

    def post_web(self, o):
        self.check(users.CHANGE_MEDIA)
        mid = o.post.integer_list("ids")[0]
        extmedia.set_web_preferred(o.dbo, o.user, mid)

    def post_video(self, o):
        self.check(users.CHANGE_MEDIA)
        mid = o.post.integer_list("ids")[0]
        extmedia.set_video_preferred(o.dbo, o.user, mid)

    def post_doc(self, o):
        self.check(users.CHANGE_MEDIA)
        mid = o.post.integer_list("ids")[0]
        extmedia.set_doc_preferred(o.dbo, o.user, mid)

    def post_exclude(self, o):
        self.check(users.CHANGE_MEDIA)
        extmedia.set_excluded(o.dbo, o.user, o.post.integer("mediaid"), o.post.integer("exclude"))

class mobile(ASMEndpoint):
    url = "mobile"
    login_url = "/mobile_login"

    def content(self, o):
        self.content_type("text/html")
        return extmobile.page(o.dbo, o.session, o.user)

class mobile_login(ASMEndpoint):
    url = "mobile_login"
    check_logged_in = False

    def content(self, o):
        if not MULTIPLE_DATABASES:
            dbo = db.get_database()
            o.locale = configuration.locale(dbo)
        self.content_type("text/html")
        return extmobile.page_login(o.locale, o.post)

    def post_all(self, o):
        self.redirect( extmobile.login(o.post, o.session, self.remote_ip(), PATH) )

class mobile_logout(ASMEndpoint):
    url = "mobile_logout"
    login_url = "/mobile_login"

    def content(self, o):
        url = "mobile_login"
        if o.post["smaccount"] != "":
            url = "login?smaccount=" + o.post["smaccount"]
        elif MULTIPLE_DATABASES and o.dbo is not None and o.dbo.alias is not None:
            url = "mobile_login?smaccount=" + o.dbo.alias
        users.update_user_activity(o.dbo, o.user, False)
        users.logout(o.session, self.remote_ip())
        self.redirect(url)

class mobile_post(ASMEndpoint):
    url = "mobile_post"
    login_url = "/mobile_login"

    def handle(self, o):
        s = extmobile.handler(session, o.post)
        if s is None:
            raise utils.ASMValidationError("mobile handler failed.")
        elif s.startswith("GO "):
            self.redirect(s[3:])
        else:
            self.content_type("text/html")
            return s

    def content(self, o):
        return self.handle(o)

    def post_all(self, o):
        return self.handle(o)

class mobile_report(ASMEndpoint):
    url = "mobile_report"
    login_url = "/mobile_login"
    get_permissions = users.VIEW_REPORT

    def content(self, o):
        dbo = o.dbo
        user = o.user
        post = o.post
        mode = post["mode"]
        crid = post.integer("id")
        # Make sure this user has a role that can view the report
        extreports.check_view_permission(o.session, crid)
        crit = extreports.get_criteria_controls(dbo, crid, mode = "MOBILE", locationfilter = o.locationfilter, siteid = o.siteid) 
        self.content_type("text/html")
        self.cache_control(0)
        # If the report doesn't take criteria, just show it
        if crit == "":
            al.debug("report %d has no criteria, displaying" % crid, "code.mobile_report", dbo)
            return extreports.execute(dbo, crid, user)
        # If we're in criteria mode (and there are some to get here), ask for them
        elif mode == "":
            title = extreports.get_title(dbo, crid)
            al.debug("building criteria form for report %d %s" % (crid, title), "code.mobile_report", dbo)
            return extmobile.report_criteria(dbo, crid, title, crit)
        # The user has entered the criteria and we're in exec mode, unpack
        # the criteria and run the report
        elif mode == "exec":
            al.debug("got criteria (%s), executing report %d" % (str(post.data), crid), "code.report", dbo)
            p = extreports.get_criteria_params(dbo, crid, post)
            return extreports.execute(dbo, crid, user, p)

class mobile_sign(ASMEndpoint):
    url = "mobile_sign"
    login_url = "/mobile_login"

    def content(self, o):
        self.content_type("text/html")
        return extmobile.page_sign(o.dbo, o.session, o.user)

class main(JSONEndpoint):
    url = "main"

    def controller(self, o):
        l = o.locale
        dbo = o.dbo
        # Do we need to request a password change?
        if session.passchange:
            self.redirect("change_password?suggest=1")
        # If there's something wrong with the database, logout
        if not dbo.has_structure():
            self.redirect("logout")
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
            animallinks = extanimal.get_links_recently_changed(dbo, linkmax, o.locationfilter, o.siteid)
        elif linkmode == "recentlyentered":
            linkname = _("Recently Entered Shelter", l)
            animallinks = extanimal.get_links_recently_entered(dbo, linkmax, o.locationfilter, o.siteid)
        elif linkmode == "recentlyadopted":
            linkname = _("Recently Adopted", l)
            animallinks = extanimal.get_links_recently_adopted(dbo, linkmax, o.locationfilter, o.siteid)
        elif linkmode == "recentlyfostered":
            linkname = _("Recently Fostered", l)
            animallinks = extanimal.get_links_recently_fostered(dbo, linkmax, o.locationfilter, o.siteid)
        elif linkmode == "longestonshelter":
            linkname = _("Longest On Shelter", l)
            animallinks = extanimal.get_links_longest_on_shelter(dbo, linkmax, o.locationfilter, o.siteid)
        elif linkmode == "adoptable":
            linkname = _("Up for adoption", l)
            animallinks = publishers.base.get_animal_data(dbo, limit=linkmax)
        # Users and roles, active users
        usersandroles = users.get_users_and_roles(dbo)
        activeusers = users.get_active_users(dbo)
        # Alerts
        alerts = extanimal.get_alerts(dbo, o.locationfilter, o.siteid)
        if len(alerts) > 0: 
            alerts[0]["LOOKFOR"] = configuration.lookingfor_last_match_count(dbo)
            alerts[0]["LOSTFOUND"] = configuration.lostfound_last_match_count(dbo)
        # Diary Notes
        dm = None
        if configuration.all_diary_home_page(dbo): 
            dm = extdiary.get_uncompleted_upto_today(dbo, "", False)
        else:
            dm = extdiary.get_uncompleted_upto_today(dbo, session.user, False)
        al.debug("main for '%s', %d diary notes, %d messages" % (session.user, len(dm), len(mess)), "code.main", dbo)
        return {
            "showwelcome": showwelcome,
            "build": BUILD,
            "news": news,
            "dbmessage": dbmessage,
            "version": get_version(),
            "emergencynotice": emergency_notice(),
            "linkname": linkname,
            "activeusers": activeusers,
            "usersandroles": usersandroles,
            "alerts": alerts,
            "recent": extanimal.get_timeline(dbo, 10),
            "stats": extanimal.get_stats(dbo),
            "animallinks": extanimal.get_animals_brief(animallinks),
            "noreload": o.post.integer("noreload"),
            "diary": dm,
            "mess": mess 
        }

    def post_addmessage(self, o):
        extlookups.add_message(o.dbo, o.user, o.post.boolean("email"), o.post["message"], o.post["forname"], o.post.integer("priority"), o.post.date("expires"))

    def post_delmessage(self, o):
        extlookups.delete_message(o.dbo, o.post.integer("id"))

    def post_showfirsttimescreen(self, o):
        configuration.show_first_time_screen(o.dbo, True, False)

class login(ASMEndpoint):
    url = "login"
    check_logged_in = False

    def content(self, o):
        l = LOCALE
        post = o.post
        has_animals = True
        custom_splash = False
        # Filter out IE8 and below right now - they just aren't good enough
        ua = self.user_agent()
        if ua.find("MSIE 6") != -1 or ua.find("MSIE 7") != -1 or ua.find("MSIE 8") != -1:
            self.redirect("static/pages/unsupported_ie.html")
        # Figure out how to get the default locale and any overridden splash screen
        # Single database
        if not MULTIPLE_DATABASES:
            dbo = db.get_database()
            l = configuration.locale(dbo)
            has_animals = extanimal.get_has_animals(dbo)
            custom_splash = dbfs.file_exists(dbo, "splash.jpg")
        # Multiple databases, no account given
        elif MULTIPLE_DATABASES and MULTIPLE_DATABASES_TYPE == "map" and post["smaccount"] == "":
            try:
                dbo = db.get_database()
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
                self.redirect(SMCOM_LOGIN_URL)
            elif dbo.database != "FAIL" and dbo.database != "DISABLED":
                custom_splash = dbfs.file_exists(dbo, "splash.jpg")
                l = configuration.locale(dbo)
        title = _("Animal Shelter Manager Login", l)
        s = html.bare_header(title, locale = l)
        c = { "smcom": smcom.active(),
             "multipledatabases": MULTIPLE_DATABASES,
             "locale": l,
             "hasanimals": has_animals,
             "customsplash": custom_splash,
             "forgottenpassword": FORGOTTEN_PASSWORD,
             "forgottenpasswordlabel": FORGOTTEN_PASSWORD_LABEL,
             "emergencynotice": emergency_notice(),
             "smaccount": post["smaccount"],
             "husername": post["username"],
             "hpassword": post["password"],
             "smcomloginurl": SMCOM_LOGIN_URL,
             "nologconnection": post["nologconnection"],
             "qrimg": QR_IMG_SRC,
             "target": post["target"]
        }
        s += "<script type=\"text/javascript\">\ncontroller = %s;\n</script>\n" % utils.json(c)
        s += '<script>\n$(document).ready(function() { $("body").append(login.render()); login.bind(); });\n</script>'
        s += html.footer()
        self.content_type("text/html")
        self.header("X-Frame-Options", "SAMEORIGIN")
        return s

    def post_all(self, o):
        return users.web_login(o.post, session, self.remote_ip(), PATH)

class login_jsonp(ASMEndpoint):
    url = "login_jsonp"
    check_logged_in = False

    def content(self, o):
        self.content_type("text/javascript")
        return "%s({ response: '%s' })" % (o.post["callback"], users.web_login(o.post, o.session, self.remote_ip(), PATH))

class login_splash(ASMEndpoint):
    url = "login_splash"
    check_logged_in = False

    def content(self, o):
        try:
            dbo = db.get_database()
            smaccount = o.post["smaccount"]
            if MULTIPLE_DATABASES:
                if smaccount != "":
                    if MULTIPLE_DATABASES_TYPE == "smcom":
                        dbo = smcom.get_database_info(smaccount)
                    else:
                        dbo = db.get_multiple_database_info(smaccount)
            self.content_type("image/jpeg")
            self.cache_control(CACHE_ONE_DAY, 120)
            return dbfs.get_string_filepath(dbo, "/reports/splash.jpg")
        except Exception as err:
            al.error("%s" % str(err), "code.login_splash", dbo)
            return ""

class logout(ASMEndpoint):
    url = "logout"
    check_logged_in = False

    def content(self, o):
        url = "login"
        if o.post["smaccount"] != "":
            url = "login?smaccount=" + o.post["smaccount"]
        elif MULTIPLE_DATABASES and o.dbo is not None and o.dbo.alias is not None:
            url = "login?smaccount=" + o.dbo.alias
        users.update_user_activity(o.dbo, o.user, False)
        users.logout(o.session, self.remote_ip())
        self.redirect(url)

class accounts(JSONEndpoint):
    url = "accounts"
    get_permissions = users.VIEW_ACCOUNT

    def controller(self, o):
        dbo = o.dbo
        if o.post["offset"] == "all":
            accounts = financial.get_accounts(dbo)
        else:
            accounts = financial.get_accounts(dbo, True)
        al.debug("got %d accounts" % len(accounts), "code.accounts", dbo)
        return {
            "accounttypes": extlookups.get_account_types(dbo),
            "costtypes": extlookups.get_costtypes(dbo),
            "donationtypes": extlookups.get_donation_types(dbo),
            "roles": users.get_roles(dbo),
            "rows": accounts
        }

    def post_create(self, o):
        self.check(users.ADD_ACCOUNT)
        return financial.insert_account_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.CHANGE_ACCOUNT)
        financial.update_account_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_ACCOUNT)
        for aid in o.post.integer_list("ids"):
            financial.delete_account(o.dbo, o.user, aid)

class accounts_trx(JSONEndpoint):
    url = "accounts_trx"
    get_permissions = users.VIEW_ACCOUNT

    def controller(self, o):
        dbo = o.dbo
        post = o.post
        defview = configuration.default_account_view_period(dbo)
        fromdate = post["fromdate"]
        todate = post["todate"]
        today = dbo.today()
        if fromdate != "" and todate != "":
            fromdate = post.date("fromdate")
            todate = post.date("todate")
        elif defview == financial.THIS_MONTH:
            fromdate = first_of_month(today)
            todate = last_of_month(today)
        elif defview == financial.THIS_WEEK:
            fromdate = monday_of_week(today)
            todate = sunday_of_week(today)
        elif defview == financial.THIS_YEAR:
            fromdate = first_of_year(today)
            todate = last_of_year(today)
        elif defview == financial.LAST_MONTH:
            fromdate = first_of_month(subtract_months(today, 1))
            todate = last_of_month(subtract_months(today, 1))
        elif defview == financial.LAST_WEEK:
            fromdate = monday_of_week(subtract_days(today, 7))
            todate = sunday_of_week(subtract_days(today, 7))
        transactions = financial.get_transactions(dbo, post.integer("accountid"), fromdate, todate, post.integer("recfilter"))
        accountcode = financial.get_account_code(dbo, post.integer("accountid"))
        accounteditroles = financial.get_account_edit_roles(dbo, post.integer("accountid"))
        al.debug("got %d trx for %s <-> %s" % (len(transactions), str(fromdate), str(todate)), "code.accounts_trx", dbo)
        return {
            "rows": transactions,
            "codes": "|".join(financial.get_account_codes(dbo, accountcode)),
            "accountid": post.integer("accountid"),
            "accountcode": accountcode,
            "accounteditroles": "|".join(accounteditroles),
            "fromdate": python2display(o.locale, fromdate),
            "todate": python2display(o.locale, todate)
        }

    def post_create(self, o):
        self.check(users.CHANGE_TRANSACTIONS)
        financial.insert_trx_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.CHANGE_TRANSACTIONS)
        financial.update_trx_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.CHANGE_TRANSACTIONS)
        for tid in o.post.integer_list("ids"):
            financial.delete_trx(o.dbo, o.user, tid)

    def post_reconcile(self, o):
        self.check(users.CHANGE_TRANSACTIONS)
        for tid in o.post.integer_list("ids"):
            financial.mark_reconciled(o.dbo, tid)

class additional(JSONEndpoint):
    url = "additional"
    get_permissions = users.MODIFY_LOOKUPS

    def controller(self, o):
        dbo = o.dbo
        fields = extadditional.get_fields(dbo)
        al.debug("got %d additional field definitions" % len(fields), "code.additional", dbo)
        return {
            "rows": fields,
            "fieldtypes": extlookups.get_additionalfield_types(dbo),
            "linktypes": extlookups.get_additionalfield_links(dbo)
        }

    def post_create(self, o):
        self.check(users.MODIFY_LOOKUPS)
        return extadditional.insert_field_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.MODIFY_LOOKUPS)
        extadditional.update_field_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.MODIFY_LOOKUPS)
        for fid in o.post.integer_list("ids"):
            extadditional.delete_field(o.dbo, o.user, fid)

class animal(JSONEndpoint):
    url = "animal"
    get_permissions = users.VIEW_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        # If the animal is not on the shelter currently, update the variable data 
        # prior to opening so age/etc. is shown correctly (shelter animals are updated by the batch)
        if not extanimal.get_is_on_shelter(dbo, o.post.integer("id")):
            extanimal.update_variable_animal_data(dbo, o.post.integer("id"))
        a = extanimal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        # If a location filter is set, prevent the user opening this animal if it's
        # not in their location.
        if not extanimal.is_animal_in_location_filter(a, o.locationfilter, o.siteid):
            raise utils.ASMPermissionError("animal not in location filter/site")
        al.debug("opened animal %s %s" % (a["CODE"], a["ANIMALNAME"]), "code.animal", dbo)
        return {
            "animal": a,
            "activelitters": extanimal.get_active_litters_brief(dbo),
            "additional": extadditional.get_additional_fields(dbo, a["ID"], "animal"),
            "animaltypes": extlookups.get_animal_types(dbo),
            "audit": self.checkb(users.VIEW_AUDIT_TRAIL) and audit.get_audit_for_link(dbo, "animal", a["ID"]) or [],
            "species": extlookups.get_species(dbo),
            "breeds": extlookups.get_breeds_by_species(dbo),
            "coattypes": extlookups.get_coattypes(dbo),
            "colours": extlookups.get_basecolours(dbo),
            "deathreasons": extlookups.get_deathreasons(dbo),
            "diarytasks": extdiary.get_animal_tasks(dbo),
            "entryreasons": extlookups.get_entryreasons(dbo),
            "flags": extlookups.get_animal_flags(dbo),
            "incidents": extanimalcontrol.get_animalcontrol_for_animal(dbo, o.post.integer("id")),
            "internallocations": extlookups.get_internal_locations(dbo, o.locationfilter, o.siteid),
            "microchipmanufacturers": extlookups.MICROCHIP_MANUFACTURERS,
            "pickuplocations": extlookups.get_pickup_locations(dbo),
            "publishhistory": extanimal.get_publish_history(dbo, a["ID"]),
            "posneg": extlookups.get_posneg(dbo),
            "sexes": extlookups.get_sexes(dbo),
            "sizes": extlookups.get_sizes(dbo),
            "sharebutton": SHARE_BUTTON,
            "tabcounts": extanimal.get_satellite_counts(dbo, a["ID"])[0],
            "templates": template.get_document_templates(dbo),
            "ynun": extlookups.get_ynun(dbo)
        }

    def post_save(self, o):
        self.check(users.CHANGE_ANIMAL)
        extanimal.update_animal_from_form(o.dbo, o.post, o.user)

    def post_delete(self, o):
        self.check(users.DELETE_ANIMAL)
        extanimal.delete_animal(o.dbo, o.user, o.post.integer("animalid"))

    def post_gencode(self, o):
        post = o.post
        animaltypeid = post.integer("animaltypeid")
        entryreasonid = post.integer("entryreasonid")
        speciesid = post.integer("speciesid")
        datebroughtin = post.date("datebroughtin")
        sheltercode, shortcode, unique, year = extanimal.calc_shelter_code(o.dbo, animaltypeid, entryreasonid, speciesid, datebroughtin)
        return sheltercode + "||" + shortcode + "||" + str(unique) + "||" + str(year)

    def post_randomname(self, o):
        return extanimal.get_random_name(o.dbo, o.post.integer("sex"))

    def post_shared(self, o):
        extanimal.insert_publish_history(o.dbo, o.post.integer("id"), o.post["service"])

    def post_clone(self, o):
        self.check(users.CLONE_ANIMAL)
        nid = extanimal.clone_animal(o.dbo, o.user, o.post.integer("animalid"))
        return str(nid)

    def post_forgetpublish(self, o):
        extanimal.delete_publish_history(o.dbo, o.post.integer("id"), o.post["service"])

    def post_webnotes(self, o):
        self.check(users.CHANGE_MEDIA)
        extanimal.update_preferred_web_media_notes(o.dbo, o.user, o.post.integer("id"), o.post["comments"])

class animal_bulk(JSONEndpoint):
    url = "animal_bulk"
    get_permissions = users.CHANGE_ANIMAL
    post_permissions = users.CHANGE_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        return {
            "ynun": extlookups.get_ynun(dbo),
            "animaltypes": extlookups.get_animal_types(dbo),
            "autolitters": extanimal.get_active_litters_brief(dbo),
            "flags": extlookups.get_animal_flags(dbo),
            "internallocations": extlookups.get_internal_locations(dbo, o.locationfilter, o.siteid),
            "movementtypes": extlookups.get_movement_types(dbo)
        }

    def post_all(self, o):
        return extanimal.update_animals_from_form(o.dbo, o.post, o.user)

class animal_clinic(JSONEndpoint):
    url = "animal_clinic"
    js_module = "clinic_appointment"
    get_permissions = users.VIEW_CLINIC

    def controller(self, o):
        dbo = o.dbo
        animalid = o.post.integer("id")
        a = extanimal.get_animal(dbo, animalid)
        if a is None: self.notfound()
        rows = clinic.get_animal_appointments(dbo, animalid)
        al.debug("got %d appointments for animal %s %s" % (len(rows), a.CODE, a.ANIMALNAME), "code.animal_clinic", dbo)
        return {
            "name": self.url,
            "animal": a,
            "clinicstatuses": extlookups.get_clinic_statuses(dbo),
            "donationtypes": extlookups.get_donation_types(dbo),
            "paymenttypes": extlookups.get_payment_types(dbo),
            "forlist": users.get_users(dbo),
            "rows": rows,
            "templates": template.get_document_templates(dbo),
            "tabcounts": extanimal.get_satellite_counts(dbo, animalid)[0]
        }

class animal_costs(JSONEndpoint):
    url = "animal_costs"
    get_permissions = users.VIEW_COST

    def controller(self, o):
        dbo = o.dbo
        animalid = o.post.integer("id")
        a = extanimal.get_animal(dbo, animalid)
        if a is None: self.notfound()
        cost = extanimal.get_costs(dbo, animalid)
        al.debug("got %d costs for animal %s %s" % (len(cost), a["CODE"], a["ANIMALNAME"]), "code.animal_costs", dbo)
        return {
            "rows": cost,
            "animal": a,
            "costtypes": extlookups.get_costtypes(dbo),
            "costtotals": extanimal.get_cost_totals(dbo, animalid),
            "tabcounts": extanimal.get_satellite_counts(dbo, animalid)[0]
        }

    def post_create(self, o):
        self.check(users.ADD_COST)
        return extanimal.insert_cost_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.CHANGE_COST)
        extanimal.update_cost_from_form(o.dbo, o.user, o.post)

    def post_dailyboardingcost(self, o):
        self.check(users.CHANGE_ANIMAL)
        animalid = o.post.integer("animalid")
        cost = o.post.integer("dailyboardingcost")
        extanimal.update_daily_boarding_cost(o.dbo, o.user, animalid, cost)

    def post_delete(self, o):
        self.check(users.DELETE_COST)
        for cid in o.post.integer_list("ids"):
            extanimal.delete_cost(o.dbo, o.user, cid)

class animal_diary(JSONEndpoint):
    url = "animal_diary"
    js_module = "diary"
    get_permissions = users.VIEW_DIARY

    def controller(self, o):
        dbo = o.dbo
        animalid = o.post.integer("id")
        a = extanimal.get_animal(dbo, animalid)
        if a is None: self.notfound()
        diaries = extdiary.get_diaries(dbo, extdiary.ANIMAL, animalid)
        al.debug("got %d notes for animal %s %s" % (len(diaries), a["CODE"], a["ANIMALNAME"]), "code.animal_diary", dbo)
        return {
            "rows": diaries,
            "animal": a,
            "tabcounts": extanimal.get_satellite_counts(dbo, animalid)[0],
            "name": "animal_diary",
            "linkid": animalid,
            "linktypeid": extdiary.ANIMAL,
            "forlist": users.get_users_and_roles(dbo)
        }

class animal_diet(JSONEndpoint):
    url = "animal_diet"
    get_permissions = users.VIEW_DIET

    def controller(self, o):
        dbo = o.dbo
        animalid = o.post.integer("id")
        a = extanimal.get_animal(dbo, animalid)
        if a is None: self.notfound()
        diet = extanimal.get_diets(dbo, animalid)
        al.debug("got %d diets for animal %s %s" % (len(diet), a["CODE"], a["ANIMALNAME"]), "code.animal_diet", dbo)
        return {
            "rows": diet,
            "animal": a,
            "tabcounts": extanimal.get_satellite_counts(dbo, animalid)[0],
            "diettypes": extlookups.get_diets(dbo)
        }

    def post_create(self, o):
        self.check(users.ADD_DIET)
        return str(extanimal.insert_diet_from_form(o.dbo, o.user, o.post))

    def post_update(self, o):
        self.check(users.CHANGE_DIET)
        extanimal.update_diet_from_form(o.dbo, o.user, o.post)
        
    def post_delete(self, o):
        self.check( users.DELETE_DIET)
        for did in o.post.integer_list("ids"):
            extanimal.delete_diet(o.dbo, o.user, did)

class animal_donations(JSONEndpoint):
    url = "animal_donations"
    js_module = "donations"
    get_permissions = users.VIEW_DONATION

    def controller(self, o):
        dbo = o.dbo
        animalid = o.post.integer("id")
        a = extanimal.get_animal(dbo, animalid)
        if a is None: raise web.notfound()
        donations = financial.get_animal_donations(dbo, animalid)
        al.debug("got %d donations for animal %s %s" % (len(donations), a["CODE"], a["ANIMALNAME"]), "code.animal_donations", dbo)
        return {
            "rows": donations,
            "animal": a,
            "tabcounts": extanimal.get_satellite_counts(dbo, animalid)[0],
            "name": "animal_donations",
            "donationtypes": extlookups.get_donation_types(dbo),
            "accounts": financial.get_accounts(dbo),
            "paymenttypes": extlookups.get_payment_types(dbo),
            "frequencies": extlookups.get_donation_frequencies(dbo),
            "templates": template.get_document_templates(dbo)
        }

class animal_embed(ASMEndpoint):
    url = "animal_embed"
    check_logged_in = False
    post_permissions = users.VIEW_ANIMAL

    def post_find(self, o):
        self.content_type("application/json")
        q = o.post["q"]
        rows = extanimal.get_animal_find_simple(o.dbo, q, o.post["filter"], 100, o.locationfilter, o.siteid)
        al.debug("got %d results for '%s'" % (len(rows), self.query()), "code.animal_embed", o.dbo)
        return utils.json(rows)

    def post_multiselect(self, o):
        self.content_type("application/json")
        dbo = o.dbo
        rows = extanimal.get_animal_find_simple(dbo, "", "all", configuration.record_search_limit(dbo), o.locationfilter, o.siteid)
        locations = extlookups.get_internal_locations(dbo)
        species = extlookups.get_species(dbo)
        litters = extanimal.get_litters(dbo)
        rv = { "rows": rows, "locations": locations, "species": species, "litters": litters }
        return utils.json(rv)

    def post_id(self, o):
        self.content_type("application/json")
        dbo = o.dbo
        animalid = o.post.integer("id")
        a = extanimal.get_animal(dbo, animalid)
        if a is None:
            al.error("get animal by id %d found no records." % animalid, "code.animal_embed", dbo)
            self.notfound()
        else:
            al.debug("got animal %s %s by id" % (a["CODE"], a["ANIMALNAME"]), "code.animal_embed", dbo)
            return utils.json((a,))

class animal_find(JSONEndpoint):
    url = "animal_find"
    get_permissions = users.VIEW_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        c = {
            "agegroups": configuration.age_groups(dbo),
            "animaltypes": extlookups.get_animal_types(dbo),
            "species": extlookups.get_species(dbo),
            "breeds": extlookups.get_breeds_by_species(dbo),
            "flags": extlookups.get_animal_flags(dbo),
            "sexes": extlookups.get_sexes(dbo),
            "internallocations": extlookups.get_internal_locations(dbo, o.locationfilter, o.siteid),
            "sizes": extlookups.get_sizes(dbo),
            "colours": extlookups.get_basecolours(dbo),
            "users": users.get_users(dbo)
        }
        al.debug("loaded lookups for find animal", "code.animal_find", dbo)
        return c

class animal_find_results(JSONEndpoint):
    url = "animal_find_results"
    get_permissions = users.VIEW_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        q = o.post["q"]
        mode = o.post["mode"]
        if mode == "SIMPLE":
            results = extanimal.get_animal_find_simple(dbo, q, "all", configuration.record_search_limit(dbo), o.locationfilter, o.siteid)
        else:
            results = extanimal.get_animal_find_advanced(dbo, o.post.data, configuration.record_search_limit(dbo), o.locationfilter, o.siteid)
        add = None
        if len(results) > 0: 
            add = extadditional.get_additional_fields_ids(dbo, results, "animal")
        al.debug("found %d results for %s" % (len(results), self.query()), "code.animal_find_results", dbo)
        return {
            "rows": results,
            "additional": add,
            "wasonshelter": q == "" and mode == "SIMPLE"
        }

class animal_licence(JSONEndpoint):
    url = "animal_licence"
    js_module = "licence"
    get_permissions = users.VIEW_LICENCE

    def controller(self, o):
        dbo = o.dbo
        a = extanimal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        licences = financial.get_animal_licences(dbo, o.post.integer("id"))
        al.debug("got %d licences" % len(licences), "code.animal_licence", dbo)
        return {
            "name": "animal_licence",
            "rows": licences,
            "animal": a,
            "templates": template.get_document_templates(dbo),
            "tabcounts": extanimal.get_satellite_counts(dbo, a["ID"])[0],
            "licencetypes": extlookups.get_licence_types(dbo)
        }

class animal_log(JSONEndpoint):
    url = "animal_log"
    js_module = "log"
    get_permissions = users.VIEW_LOG

    def controller(self, o):
        dbo = o.dbo
        logfilter = o.post.integer("filter")
        if logfilter == 0: logfilter = configuration.default_log_filter(dbo)
        a = extanimal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        logs = extlog.get_logs(dbo, extlog.ANIMAL, o.post.integer("id"), logfilter)
        al.debug("got %d logs for animal %s %s" % (len(logs), a["CODE"], a["ANIMALNAME"]), "code.animal_log", dbo)
        return {
            "name": "animal_log",
            "linkid": o.post.integer("id"),
            "linktypeid": extlog.ANIMAL,
            "filter": logfilter,
            "rows": logs,
            "animal": a,
            "tabcounts": extanimal.get_satellite_counts(dbo, a["ID"])[0],
            "logtypes": extlookups.get_log_types(dbo)
        }

class animal_media(JSONEndpoint):
    url = "animal_media"
    js_module = "media"
    get_permissions = users.VIEW_MEDIA

    def controller(self, o):
        dbo = o.dbo
        a = extanimal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        m = extmedia.get_media(dbo, extmedia.ANIMAL, o.post.integer("id"))
        al.debug("got %d media entries for animal %s %s" % (len(m), a["CODE"], a["ANIMALNAME"]), "code.animal_media", dbo)
        return {
            "media": m,
            "animal": a,
            "tabcounts": extanimal.get_satellite_counts(dbo, a["ID"])[0],
            "showpreferred": True,
            "linkid": o.post.integer("id"),
            "linktypeid": extmedia.ANIMAL,
            "logtypes": extlookups.get_log_types(dbo),
            "newmedia": o.post.integer("newmedia") == 1,
            "name": self.url,
            "sigtype": ELECTRONIC_SIGNATURES
        }

class animal_medical(JSONEndpoint):
    url = "animal_medical"
    js_module = "medical"
    get_permissions = users.VIEW_MEDICAL

    def controller(self, o):
        dbo = o.dbo
        a = extanimal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        med = extmedical.get_regimens_treatments(dbo, o.post.integer("id"))
        profiles = extmedical.get_profiles(dbo)
        al.debug("got %d medical entries for animal %s %s" % (len(med), a["CODE"], a["ANIMALNAME"]), "code.animal_medical", dbo)
        return {
            "profiles": profiles,
            "rows": med,
            "name": "animal_medical",
            "tabcounts": extanimal.get_satellite_counts(dbo, a["ID"])[0],
            "stockitems": extstock.get_stock_items(dbo),
            "stockusagetypes": extlookups.get_stock_usage_types(dbo),
            "users": users.get_users(dbo),
            "animal": a
        }

class animal_movements(JSONEndpoint):
    url = "animal_movements"
    js_module = "movements"
    get_permissions = users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        a = extanimal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        movements = extmovement.get_animal_movements(dbo, o.post.integer("id"))
        al.debug("got %d movements for animal %s %s" % (len(movements), a["CODE"], a["ANIMALNAME"]), "code.animal_movements", dbo)
        return {
            "rows": movements,
            "animal": a,
            "tabcounts": extanimal.get_satellite_counts(dbo, a["ID"])[0],
            "movementtypes": extlookups.get_movement_types(dbo),
            "reservationstatuses": extlookups.get_reservation_statuses(dbo),
            "returncategories": extlookups.get_entryreasons(dbo),
            "templates": template.get_document_templates(dbo),
            "name": self.url
        }

class animal_new(JSONEndpoint):
    url = "animal_new"
    get_permissions = users.ADD_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        c = {
            "autolitters": extanimal.get_active_litters_brief(dbo),
            "additional": extadditional.get_additional_fields(dbo, 0, "animal"),
            "animaltypes": extlookups.get_animal_types(dbo),
            "species": extlookups.get_species(dbo),
            "breeds": extlookups.get_breeds_by_species(dbo),
            "colours": extlookups.get_basecolours(dbo),
            "flags": extlookups.get_animal_flags(dbo),
            "sexes": extlookups.get_sexes(dbo),
            "entryreasons": extlookups.get_entryreasons(dbo),
            "internallocations": extlookups.get_internal_locations(dbo, o.locationfilter, o.siteid),
            "sizes": extlookups.get_sizes(dbo)
        }
        al.debug("loaded lookups for new animal", "code.animal_new", dbo)
        return c

    def post_save(self, o):
        self.check(users.ADD_ANIMAL)
        animalid, code = extanimal.insert_animal_from_form(o.dbo, o.post, o.user)
        return "%s %s" % (animalid, code)

    def post_recentnamecheck(self, o):
        rows = extanimal.get_recent_with_name(o.dbo, o.post["animalname"])
        al.debug("recent names found %d rows for '%s'" % (len(rows), o.post["animalname"]), "code.animal_new.recentnamecheck", o.dbo)
        if len(rows) > 0:
            return "|".join((str(rows[0]["ANIMALID"]), rows[0]["SHELTERCODE"], rows[0]["ANIMALNAME"]))

    def post_units(self, o):
        return "&&".join(extanimal.get_units_with_availability(o.dbo, o.post.integer("locationid")))

class animal_test(JSONEndpoint):
    url = "animal_test"
    js_module = "test"
    get_permissions = users.VIEW_TEST

    def controller(self, o):
        dbo = o.dbo
        a = extanimal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        test = extmedical.get_tests(dbo, o.post.integer("id"))
        al.debug("got %d tests" % len(test), "code.animal_test", dbo)
        return {
            "name": "animal_test",
            "animal": a,
            "tabcounts": extanimal.get_satellite_counts(dbo, a["ID"])[0],
            "rows": test,
            "stockitems": extstock.get_stock_items(dbo),
            "stockusagetypes": extlookups.get_stock_usage_types(dbo),
            "testtypes": extlookups.get_test_types(dbo),
            "testresults": extlookups.get_test_results(dbo)
        }

class animal_transport(JSONEndpoint):
    url = "animal_transport"
    js_module = "transport"
    get_permissions = users.VIEW_TRANSPORT

    def controller(self, o):
        dbo = o.dbo
        a = extanimal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        transports = extmovement.get_animal_transports(dbo, o.post.integer("id"))
        al.debug("got %d transports" % len(transports), "code.animal_transport", dbo)
        return {
            "name": "animal_transport",
            "animal": a,
            "tabcounts": extanimal.get_satellite_counts(dbo, a["ID"])[0],
            "transporttypes": extlookups.get_transport_types(dbo),
            "rows": transports
        }

class animal_vaccination(JSONEndpoint):
    url = "animal_vaccination"
    js_module = "vaccination"
    get_permissions = users.VIEW_VACCINATION

    def controller(self, o):
        dbo = o.dbo
        a = extanimal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        vacc = extmedical.get_vaccinations(dbo, o.post.integer("id"))
        al.debug("got %d vaccinations" % len(vacc), "code.vaccination", dbo)
        return {
            "name": "animal_vaccination",
            "animal": a,
            "tabcounts": extanimal.get_satellite_counts(dbo, a["ID"])[0],
            "rows": vacc,
            "batches": extmedical.get_batch_for_vaccination_types(dbo),
            "manufacturers": "|".join(extmedical.get_vacc_manufacturers(dbo)),
            "stockitems": extstock.get_stock_items(dbo),
            "stockusagetypes": extlookups.get_stock_usage_types(dbo),
            "vaccinationtypes": extlookups.get_vaccination_types(dbo)
        }

class batch(JSONEndpoint):
    url = "batch"
    get_permissions = users.TRIGGER_BATCH
    post_permissions = users.TRIGGER_BATCH

    def controller(self, o):
        return {}

    def post_genfigyear(self, o):
        l = o.locale
        if o.post.date("taskdate") is None: raise utils.ASMValidationError("no date parameter")
        async.function_task(o.dbo, _("Regenerate annual animal figures for", l), extanimal.update_animal_figures_annual, o.dbo, o.post.date("taskdate").year)

    def post_genfigmonth(self, o):
        l = o.locale
        if o.post.date("taskdate") is None: raise utils.ASMValidationError("no date parameter")
        async.function_task(o.dbo, _("Regenerate monthly animal figures for", l), extanimal.update_animal_figures, o.dbo, o.post.date("taskdate").month, o.post.date("taskdate").year)

    def post_genshelterpos(self, o):
        l = o.locale
        async.function_task(o.dbo, _("Recalculate on-shelter animal locations", l), extanimal.update_on_shelter_animal_statuses, o.dbo)

    def post_genallpos(self, o):
        l = o.locale
        async.function_task(o.dbo, _("Recalculate ALL animal locations", l), extanimal.update_all_animal_statuses, o.dbo)

    def post_genallvariable(self, o):
        l = o.locale
        async.function_task(o.dbo, _("Recalculate ALL animal ages/times", l), extanimal.update_all_variable_animal_data, o.dbo)

    def post_genlookingfor(self, o):
        l = o.locale
        async.function_task(o.dbo, _("Regenerate 'Person looking for' report", l), extperson.update_lookingfor_report, o.dbo)

    def post_genownername(self, o):
        l = o.locale
        async.function_task(o.dbo, _("Regenerate person names in selected format", l), extperson.update_owner_names, o.dbo)

    def post_genlostfound(self, o):
        l = o.locale
        async.function_task(o.dbo, _("Regenerate 'Match lost and found animals' report", l), extlostfound.update_match_report, o.dbo)

class calendarview(JSONEndpoint):
    url = "calendarview"
    get_permissions = users.VIEW_ANIMAL

    def controller(self, o):
        return {}

class calendar_events(ASMEndpoint):
    url = "calendar_events"

    def content(self, o):
        start = parse_date("%Y-%m-%d", o.post["start"])
        end = parse_date("%Y-%m-%d", o.post["end"])
        if not start or not end:
            return "[]"
        events = []
        ev = o.post["ev"]
        user = o.user
        dbo = o.dbo
        l = o.locale
        if "d" in ev and self.checkb(users.VIEW_DIARY):
            # Show all diary notes on the calendar if the user chose to see all
            # on the home page, or they have permission to view all notes
            if configuration.all_diary_home_page(dbo) or self.checkb(users.EDIT_ALL_DIARY_NOTES):
                user = ""
            for d in extdiary.get_between_two_dates(dbo, user, start, end):
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
        if "v" in ev and self.checkb(users.VIEW_VACCINATION):
            for v in extmedical.get_vaccinations_two_dates(dbo, start, end, o.locationfilter, o.siteid):
                sub = "%s - %s" % (v["VACCINATIONTYPE"], v["ANIMALNAME"])
                tit = "%s - %s %s %s" % (v["VACCINATIONTYPE"], v["SHELTERCODE"], v["ANIMALNAME"], v["COMMENTS"])
                events.append({ 
                    "title": sub, 
                    "allDay": True, 
                    "start": v["DATEREQUIRED"], 
                    "tooltip": tit, 
                    "icon": "vaccination",
                    "link": "animal_vaccination?id=%d" % v["ANIMALID"] })
            for v in extmedical.get_vaccinations_expiring_two_dates(dbo, start, end, o.locationfilter, o.siteid):
                sub = "%s - %s" % (v["VACCINATIONTYPE"], v["ANIMALNAME"])
                tit = "%s - %s %s %s" % (v["VACCINATIONTYPE"], v["SHELTERCODE"], v["ANIMALNAME"], v["COMMENTS"])
                events.append({ 
                    "title": sub, 
                    "allDay": True, 
                    "start": v["DATEEXPIRES"], 
                    "tooltip": tit, 
                    "icon": "vaccination",
                    "link": "animal_vaccination?id=%d" % v["ANIMALID"] })
        if "m" in ev and self.checkb(users.VIEW_MEDICAL):
            for m in extmedical.get_treatments_two_dates(dbo, start, end, o.locationfilter, o.siteid):
                sub = "%s - %s" % (m["TREATMENTNAME"], m["ANIMALNAME"])
                tit = "%s - %s %s %s %s" % (m["TREATMENTNAME"], m["SHELTERCODE"], m["ANIMALNAME"], m["DOSAGE"], m["COMMENTS"])
                events.append({ 
                    "title": sub, 
                    "allDay": True, 
                    "start": m["DATEREQUIRED"], 
                    "tooltip": tit, 
                    "icon": "medical",
                    "link": "animal_medical?id=%d" % m["ANIMALID"] })
        if "t" in ev and self.checkb(users.VIEW_TEST):
            for t in extmedical.get_tests_two_dates(dbo, start, end, o.locationfilter, o.siteid):
                sub = "%s - %s" % (t["TESTNAME"], t["ANIMALNAME"])
                tit = "%s - %s %s %s" % (t["TESTNAME"], t["SHELTERCODE"], t["ANIMALNAME"], t["COMMENTS"])
                events.append({ 
                    "title": sub, 
                    "allDay": True, 
                    "start": t["DATEREQUIRED"], 
                    "tooltip": tit, 
                    "icon": "test",
                    "link": "animal_test?id=%d" % t["ANIMALID"] })
        if "c" in ev and self.checkb(users.VIEW_CLINIC):
            for c in clinic.get_appointments_two_dates(dbo, start, end, o.post["apptfor"], o.siteid):
                sub = "%s - %s" % (c.OWNERNAME, c.ANIMALNAME)
                tit = "%s - %s (%s) %s" % (c.OWNERNAME, c.ANIMALNAME, c.APPTFOR, c.REASONFORAPPOINTMENT)
                events.append({ 
                    "title": sub, 
                    "allDay": False, 
                    "start": c.DATETIME,
                    "end": add_minutes(c.DATETIME, 20),
                    "tooltip": tit, 
                    "icon": "health",
                    "link": "person_clinic?id=%d" % c.OWNERID })
        if "p" in ev and self.checkb(users.VIEW_DONATION):
            for p in financial.get_donations_due_two_dates(dbo, start, end):
                sub = "%s - %s" % (p["DONATIONNAME"], p["OWNERNAME"])
                tit = "%s - %s %s %s" % (p["DONATIONNAME"], p["OWNERNAME"], html.format_currency(l, p["DONATION"]), p["COMMENTS"])
                events.append({ 
                    "title": sub, 
                    "allDay": True, 
                    "start": p["DATEDUE"], 
                    "tooltip": tit, 
                    "icon": "donation",
                    "link": "person_donations?id=%d" % p["OWNERID"] })
        if "o" in ev and self.checkb(users.VIEW_INCIDENT):
            for o in extanimalcontrol.get_followup_two_dates(dbo, start, end):
                sub = "%s - %s" % (o["INCIDENTNAME"], o["OWNERNAME"])
                tit = "%s - %s %s, %s" % (o["INCIDENTNAME"], o["OWNERNAME"], o["DISPATCHADDRESS"], o["CALLNOTES"])
                events.append({ 
                    "title": sub, 
                    "allDay": False, 
                    "start": o["FOLLOWUPDATETIME"], 
                    "tooltip": tit, 
                    "icon": "call",
                    "link": "incident?id=%d" % o["ACID"] })
        if "r" in ev and self.checkb(users.VIEW_TRANSPORT):
            for r in extmovement.get_transport_two_dates(dbo, start, end):
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
        if "l" in ev and self.checkb(users.VIEW_TRAPLOAN):
            for l in extanimalcontrol.get_traploan_two_dates(dbo, start, end):
                sub = "%s - %s" % (l["TRAPTYPENAME"], l["OWNERNAME"])
                tit = "%s - %s %s, %s" % (l["TRAPTYPENAME"], l["OWNERNAME"], l["TRAPNUMBER"], l["COMMENTS"])
                events.append({ 
                    "title": sub, 
                    "allDay": True, 
                    "start": l["RETURNDUEDATE"], 
                    "tooltip": tit, 
                    "icon": "traploan",
                    "link": "person_traploan?id=%d" % l["OWNERID"]})
        al.debug("calendarview found %d events (%s->%s)" % (len(events), start, end), "code.calendarview", dbo)
        self.content_type("application/json")
        return utils.json(events)

class change_password(JSONEndpoint):
    url = "change_password"

    def controller(self, o):
        al.debug("%s change password screen" % o.user, "code.change_password", o.dbo)
        return {
            "ismaster": smcom.active() and o.dbo.database == o.user,
            "issuggest": o.post.integer("suggest") == 1,
            "username": o.user
        }

    def post_all(self, o):
        oldpass = o.post["oldpassword"]
        newpass = o.post["newpassword"]
        al.debug("%s changed password" % (o.user), "code.change_password", o.dbo)
        users.change_password(o.dbo, o.user, oldpass, newpass)

class change_user_settings(JSONEndpoint):
    url = "change_user_settings"

    def controller(self, o):
        al.debug("%s change user settings screen" % o.user, "code.change_user_settings", o.dbo)
        return {
            "user": users.get_users(o.dbo, o.user),
            "locales": get_locales(),
            "sigtype": ELECTRONIC_SIGNATURES,
            "themes": extlookups.VISUAL_THEMES
        }

    def post_all(self, o):
        post = o.post
        theme = post["theme"]
        locale = post["locale"]
        realname = post["realname"]
        email = post["email"]
        signature = post["signature"]
        al.debug("%s changed settings: theme=%s, locale=%s, realname=%s, email=%s" % (o.user, theme, locale, realname, email), "code.change_password", o.dbo)
        users.update_user_settings(o.dbo, o.user, email, realname, locale, theme, signature)
        self.reload_config()

class citations(JSONEndpoint):
    url = "citations"
    get_permissions = users.VIEW_CITATION

    def controller(self, o):
        # this screen only supports one mode at present - unpaid fines
        # if o.post["filter"] == "unpaid" or o.post["filter"] == "":
        citations = financial.get_unpaid_fines(o.dbo)
        al.debug("got %d citations" % len(citations), "code.citations", o.dbo)
        return {
            "name": "citations",
            "rows": citations,
            "citationtypes": extlookups.get_citation_types(o.dbo)
        }

    def post_create(self, o):
        self.check(users.ADD_CITATION)
        return financial.insert_citation_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.CHANGE_CITATION)
        financial.update_citation_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_CITATION)
        for lid in o.post.integer_list("ids"):
            financial.delete_citation(o.dbo, o.user, lid)

class clinic_appointment(ASMEndpoint):
    url = "clinic_appointment"

    def post_create(self, o):
        self.check(users.ADD_CLINIC)
        return clinic.insert_appointment_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.CHANGE_CLINIC)
        clinic.update_appointment_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_CLINIC)
        for cid in o.post.integer_list("ids"):
            clinic.delete_appointment(o.dbo, o.user, cid)

    def post_payment(self, o):
        self.check(users.ADD_DONATION)
        for cid in o.post.integer_list("ids"):
            clinic.insert_payment_from_appointment(o.dbo, o.user, cid, o.post)

    def post_personanimals(self, o):
        self.check(users.VIEW_ANIMAL)
        return utils.json(extanimal.get_animals_owned_by(o.dbo, o.post.integer("personid")))

    def post_towaiting(self, o):
        self.check(users.CHANGE_CLINIC)
        for cid in o.post.integer_list("ids"):
            clinic.update_appointment_to_waiting(o.dbo, o.user, cid, o.post.datetime("date", "time"))

    def post_towithvet(self, o):
        self.check(users.CHANGE_CLINIC)
        for cid in o.post.integer_list("ids"):
            clinic.update_appointment_to_with_vet(o.dbo, o.user, cid, o.post.datetime("date", "time"))

    def post_tocomplete(self, o):
        self.check(users.CHANGE_CLINIC)
        for cid in o.post.integer_list("ids"):
            clinic.update_appointment_to_complete(o.dbo, o.user, cid, o.post.datetime("date", "time"))

class clinic_calendar(JSONEndpoint):
    url = "clinic_calendar"
    get_permissions = users.VIEW_CLINIC

    def controller(self, o):
        return {
            "forlist": users.get_users(o.dbo)
        }

class clinic_invoice(JSONEndpoint):
    url = "clinic_invoice"
    get_permissions = users.VIEW_CLINIC

    def controller(self, o):
        dbo = o.dbo
        appointmentid = o.post.integer("appointmentid")
        appointment = clinic.get_appointment(dbo, appointmentid)
        if appointment is None: self.notfound()
        rows = clinic.get_invoice_items(dbo, appointmentid)
        al.debug("got %d invoice items for appointment %d" % (len(rows), appointmentid), "code.clinic_invoice", dbo)
        return {
            "appointment": appointment,
            "appointmentid": appointmentid,
            "rows": rows
        }

    def post_create(self, o):
        self.check(users.ADD_CLINIC)
        return clinic.insert_invoice_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.CHANGE_CLINIC)
        clinic.update_invoice_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_CLINIC)
        for iid in o.post.integer_list("ids"):
            clinic.delete_invoice(o.dbo, o.user, iid)

class clinic_consultingroom(JSONEndpoint):
    url = "clinic_consultingroom"
    js_module = "clinic_appointment"
    get_permissions = users.VIEW_CLINIC

    def controller(self, o):
        dbo = o.dbo
        sf = o.post.integer("filter")
        if o.post["filter"] == "": sf = -1
        rows = clinic.get_appointments_today(dbo, statusfilter = sf, userfilter = o.user, siteid = o.siteid)
        al.debug("got %d appointments" % (len(rows)), "code.clinic_consultingroom", dbo)
        return {
            "name": self.url,
            "filter": sf,
            "clinicstatuses": extlookups.get_clinic_statuses(dbo),
            "donationtypes": extlookups.get_donation_types(dbo),
            "paymenttypes": extlookups.get_payment_types(dbo),
            "forlist": users.get_users(dbo),
            "templates": template.get_document_templates(dbo),
            "rows": rows
        }

class clinic_waitingroom(JSONEndpoint):
    url = "clinic_waitingroom"
    js_module = "clinic_appointment"
    get_permissions = users.VIEW_CLINIC

    def controller(self, o):
        dbo = o.dbo
        sf = o.post.integer("filter")
        if o.post["filter"] == "": sf = -1
        rows = clinic.get_appointments_today(dbo, statusfilter = sf, siteid = o.siteid)
        al.debug("got %d appointments" % (len(rows)), "code.clinic_waitingroom", dbo)
        return {
            "name": self.url,
            "filter": sf,
            "clinicstatuses": extlookups.get_clinic_statuses(dbo),
            "donationtypes": extlookups.get_donation_types(dbo),
            "paymenttypes": extlookups.get_payment_types(dbo),
            "forlist": users.get_users(dbo),
            "templates": template.get_document_templates(dbo),
            "rows": rows
        }

class csvexport(JSONEndpoint):
    url = "csvexport"
    get_permissions = users.USE_SQL_INTERFACE

    def post_all(self, o):
        self.content_type("text/csv")
        self.header("Content-Disposition", u"attachment; filename=export.csv")
        return extcsvimport.csvexport_animals(o.dbo, o.post["animals"], o.post.boolean("includeimage") == 1)

class csvimport(JSONEndpoint):
    url = "csvimport"
    get_permissions = users.USE_SQL_INTERFACE
    post_permissions = users.USE_SQL_INTERFACE

    def controller(self, o):
        return {}

    def post_all(self, o):
        l = o.locale
        async.function_task(o.dbo, _("Import a CSV file", l), extcsvimport.csvimport, o.dbo, o.post.filedata(), o.post["encoding"], 
            o.post.boolean("createmissinglookups") == 1, o.post.boolean("cleartables") == 1, o.post.boolean("checkduplicates") == 1)
        self.redirect("task")

class csvimport_paypal(JSONEndpoint):
    url = "csvimport_paypal"
    get_permissions = users.USE_SQL_INTERFACE
    post_permissions = users.USE_SQL_INTERFACE

    def controller(self, o):
        return { 
            "donationtypes": extlookups.get_donation_types(o.dbo),
            "paymenttypes": extlookups.get_payment_types(o.dbo),
            "flags": extlookups.get_person_flags(o.dbo)
        }

    def post_all(self, o):
        l = o.locale
        async.function_task(o.dbo, _("Import a PayPal CSV file", l), extcsvimport.csvimport_paypal, o.dbo, \
            o.post.filedata(), o.post.integer("type"), o.post.integer("payment"), o.post["flags"])
        self.redirect("task")

class diary(ASMEndpoint):
    url = "diary"

    def post_create(self, o):
        self.check(users.ADD_DIARY)
        extdiary.insert_diary_from_form(o.dbo, o.user, o.post.integer("linktypeid"), o.post.integer("linkid"), o.post)

    def post_update(self, o):
        self.check(users.EDIT_MY_DIARY_NOTES)
        extdiary.update_diary_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_DIARY)
        for did in o.post.integer_list("ids"):
            extdiary.delete_diary(o.dbo, o.user, did)

    def post_complete(self, o):
        self.check(users.BULK_COMPLETE_NOTES)
        for did in o.post.integer_list("ids"):
            extdiary.complete_diary_note(o.dbo, o.user, did)

class diary_edit(JSONEndpoint):
    url = "diary_edit"
    js_module = "diary"
    get_permissions = users.EDIT_ALL_DIARY_NOTES

    def controller(self, o):
        dbo = o.dbo
        dfilter = o.post["filter"]
        if dfilter == "uncompleted" or dfilter == "":
            diaries = extdiary.get_uncompleted_upto_today(dbo)
        elif dfilter == "completed":
            diaries = extdiary.get_completed_upto_today(dbo)
        elif dfilter == "future":
            diaries = extdiary.get_future(dbo)
        elif dfilter == "all":
            diaries = extdiary.get_all_upto_today(dbo)
        al.debug("got %d diaries, filter was %s" % (len(diaries), dfilter), "code.diary_edit", dbo)
        return {
            "rows": diaries,
            "newnote": o.post.integer("newnote") == 1,
            "name": "diary_edit",
            "linkid": 0,
            "linktypeid": extdiary.NO_LINK,
            "forlist": users.get_users_and_roles(dbo)
        }

class diary_edit_my(JSONEndpoint):
    url = "diary_edit_my"
    js_module = "diary"
    get_permissions = users.EDIT_MY_DIARY_NOTES

    def controller(self, o):
        dbo = o.dbo
        userfilter = o.user
        dfilter = o.post["filter"]
        if dfilter == "uncompleted" or dfilter == "":
            diaries = extdiary.get_uncompleted_upto_today(dbo, userfilter)
        elif dfilter == "completed":
            diaries = extdiary.get_completed_upto_today(dbo, userfilter)
        elif dfilter == "future":
            diaries = extdiary.get_future(dbo, userfilter)
        elif dfilter == "all":
            diaries = extdiary.get_all_upto_today(dbo, userfilter)
        al.debug("got %d diaries (%s), filter was %s" % (len(diaries), userfilter, dfilter), "code.diary_edit_my", dbo)
        return {
            "rows": diaries,
            "newnote": o.post.integer("newnote") == 1,
            "name": "diary_edit_my",
            "linkid": 0,
            "linktypeid": extdiary.NO_LINK,
            "forlist": users.get_users_and_roles(dbo)
        }

class diarytask(JSONEndpoint):
    url = "diarytask"
    get_permissions = users.EDIT_DIARY_TASKS
    post_permissions = users.EDIT_DIARY_TASKS

    def controller(self, o):
        dbo = o.dbo
        taskid = o.post.integer("taskid")
        taskname = extdiary.get_diarytask_name(dbo, taskid)
        diarytaskdetail = extdiary.get_diarytask_details(dbo, taskid)
        al.debug("got %d diary task details" % len(diarytaskdetail), "code.diarytask", dbo)
        return {
            "rows": diarytaskdetail,
            "taskid": taskid,
            "taskname": taskname,
            "forlist": users.get_users_and_roles(dbo)
        }

    def post_create(self, o):
        return extdiary.insert_diarytaskdetail_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        extdiary.update_diarytaskdetail_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        for did in o.post.integer_list("ids"):
            extdiary.delete_diarytaskdetail(o.dbo, o.user, did)
    
    def post_exec(self, o):
        self.check(users.ADD_DIARY)
        extdiary.execute_diary_task(o.dbo, o.user, o.post["tasktype"], o.post.integer("taskid"), o.post.integer("id"), o.post.date("seldate"))

class diarytasks(JSONEndpoint):
    url = "diarytasks"
    get_permissions = users.EDIT_DIARY_TASKS
    post_permissions = users.EDIT_DIARY_TASKS

    def controller(self, o):
        dbo = o.dbo
        diarytaskhead = extdiary.get_diarytasks(dbo)
        al.debug("got %d diary tasks" % len(diarytaskhead), "code.diarytasks", dbo)
        return {
            "rows": diarytaskhead
        }

    def post_create(self, o):
        return extdiary.insert_diarytaskhead_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        extdiary.update_diarytaskhead_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        for did in o.post.integer_list("ids"):
            extdiary.delete_diarytask(o.dbo, o.user, did)

class document_gen(ASMEndpoint):
    url = "document_gen"
    get_permissions = users.GENERATE_DOCUMENTS

    def content(self, o):
        dbo = o.dbo
        post = o.post
        linktype = post["linktype"]
        if post["id"] == "" or post["id"] == "0": raise utils.ASMValidationError("no id parameter")
        dtid = post.integer("dtid")
        templatename = template.get_document_template_name(dbo, dtid)
        title = templatename
        loglinktype = extlog.ANIMAL
        al.debug("generating %s document for %d, template '%s'" % (linktype, post.integer("id"), templatename), "code.document_gen", dbo)
        logid = post.integer("id")
        if linktype == "ANIMAL" or linktype == "":
            loglinktype = extlog.ANIMAL
            content = wordprocessor.generate_animal_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "ANIMALCONTROL":
            loglinktype = extlog.ANIMALCONTROL
            content = wordprocessor.generate_animalcontrol_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "CLINIC":
            loglinktype = extlog.PERSON
            content = wordprocessor.generate_clinic_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "PERSON":
            loglinktype = extlog.PERSON
            content = wordprocessor.generate_person_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "DONATION":
            loglinktype = extlog.PERSON
            logid = financial.get_donation(dbo, post.integer_list("id")[0])["OWNERID"]
            content = wordprocessor.generate_donation_doc(dbo, dtid, post.integer_list("id"), o.user)
        elif linktype == "FOUNDANIMAL":
            loglinktype = extlog.FOUNDANIMAL
            logid = extlostfound.get_foundanimal(dbo, post.integer("id"))["OWNERID"]
            content = wordprocessor.generate_foundanimal_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "LOSTANIMAL":
            loglinktype = extlog.LOSTANIMAL
            logid = extlostfound.get_lostanimal(dbo, post.integer("id"))["OWNERID"]
            content = wordprocessor.generate_lostanimal_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "LICENCE":
            loglinktype = extlog.PERSON
            logid = financial.get_licence(dbo, post.integer("id"))["OWNERID"]
            content = wordprocessor.generate_licence_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "MOVEMENT":
            loglinktype = extlog.PERSON
            logid = extmovement.get_movement(dbo, post.integer("id"))["OWNERID"]
            content = wordprocessor.generate_movement_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "WAITINGLIST":
            loglinktype = extlog.WAITINGLIST
            logid = extwaitinglist.get_waitinglist_by_id(dbo, post.integer("id"))["OWNERID"]
            content = wordprocessor.generate_waitinglist_doc(dbo, dtid, post.integer("id"), o.user)
        if configuration.generate_document_log(dbo) and configuration.generate_document_log_type(dbo) > 0:
            extlog.add_log(dbo, o.user, loglinktype, logid, configuration.generate_document_log_type(dbo), _("Generated document '{0}'").format(templatename))
        if templatename.endswith(".html"):
            self.content_type("text/html")
            self.cache_control(0)
            return html.tinymce_header(title, "document_edit.js", visualaids=False, jswindowprint=configuration.js_window_print(dbo)) + \
                html.tinymce_main(dbo.locale, "document_gen", recid=post["id"], linktype=post["linktype"], \
                    dtid=dtid, content=utils.escape_tinymce(content))
        elif templatename.endswith(".odt"):
            self.content_type("application/vnd.oasis.opendocument.text")
            self.header("Content-Disposition", "attach; filename=\"%s\"" % templatename)
            self.cache_control(0)
            return content

    def post_save(self, o):
        self.check(users.ADD_MEDIA)
        dbo = o.dbo
        post = o.post
        linktype = post["linktype"]
        dtid = post.integer("dtid")
        tempname = template.get_document_template_name(dbo, dtid)
        recid = post.integer("recid")
        if linktype == "ANIMAL":
            tempname += " - " + extanimal.get_animal_namecode(dbo, recid)
            extmedia.create_document_media(dbo, session.user, extmedia.ANIMAL, recid, tempname, post["document"])
            self.redirect("animal_media?id=%d" % recid)
        elif linktype == "ANIMALCONTROL":
            tempname += " - " + utils.padleft(recid, 6)
            extmedia.create_document_media(dbo, session.user, extmedia.ANIMALCONTROL, recid, tempname, post["document"])
            self.redirect("incident_media?id=%d" % recid)
        elif linktype == "CLINIC":
            c = clinic.get_appointment(dbo, recid)
            if c is None:
                raise utils.ASMValidationError("%d is not a valid clinic id" % recid)
            ownerid = c.OWNERID
            tempname += " - " + c.OWNERNAME
            extmedia.create_document_media(dbo, session.user, extmedia.PERSON, ownerid, tempname, post["document"])
            self.redirect("person_media?id=%d" % ownerid)
        elif linktype == "FOUNDANIMAL":
            tempname += " - " + utils.padleft(recid, 6)
            extmedia.create_document_media(dbo, session.user, extmedia.FOUNDANIMAL, recid, tempname, post["document"])
            self.redirect("foundanimal_media?id=%d" % recid)
        elif linktype == "LOSTANIMAL":
            tempname += " - " + utils.padleft(recid, 6)
            extmedia.create_document_media(dbo, session.user, extmedia.LOSTANIMAL, recid, tempname, post["document"])
            self.redirect("lostanimal_media?id=%d" % recid)
        elif linktype == "PERSON":
            tempname += " - " + extperson.get_person_name(dbo, recid)
            extmedia.create_document_media(dbo, session.user, extmedia.PERSON, recid, tempname, post["document"])
            self.redirect("person_media?id=%d" % recid)
        elif linktype == "WAITINGLIST":
            tempname += " - " + utils.padleft(recid, 6)
            extmedia.create_document_media(dbo, session.user, extmedia.WAITINGLIST, recid, tempname, post["document"])
            self.redirect("waitinglist_media?id=%d" % recid)
        elif linktype == "DONATION":
            d = financial.get_donations_by_ids(dbo, post.integer_list("recid"))
            if len(d) == 0:
                raise utils.ASMValidationError("list '%s' does not contain valid ids" % recid)
            ownerid = d[0]["OWNERID"]
            tempname += " - " + extperson.get_person_name(dbo, ownerid)
            extmedia.create_document_media(dbo, session.user, extmedia.PERSON, ownerid, tempname, post["document"])
            self.redirect("person_media?id=%d" % ownerid)
        elif linktype == "LICENCE":
            l = financial.get_licence(dbo, recid)
            if l is None:
                raise utils.ASMValidationError("%d is not a valid licence id" % recid)
            ownerid = l["OWNERID"]
            tempname += " - " + extperson.get_person_name(dbo, ownerid)
            extmedia.create_document_media(dbo, session.user, extmedia.PERSON, ownerid, tempname, post["document"])
            self.redirect("person_media?id=%d" % ownerid)
        elif linktype == "MOVEMENT":
            m = extmovement.get_movement(dbo, recid)
            if m is None:
                raise utils.ASMValidationError("%d is not a valid movement id" % recid)
            animalid = m["ANIMALID"]
            ownerid = m["OWNERID"]
            tempname = "%s - %s::%s" % (tempname, extanimal.get_animal_namecode(dbo, animalid), extperson.get_person_name(dbo, ownerid))
            extmedia.create_document_media(dbo, session.user, extmedia.PERSON, ownerid, tempname, post["document"])
            extmedia.create_document_media(dbo, session.user, extmedia.ANIMAL, animalid, tempname, post["document"])
            self.redirect("person_media?id=%d" % ownerid)
        else:
            raise utils.ASMValidationError("Linktype '%s' is invalid, cannot save" % linktype)

    def post_pdf(self, o):
        self.check(users.VIEW_MEDIA)
        dbo = o.dbo
        post = o.post
        disposition = configuration.pdf_inline(dbo) and "inline; filename=\"doc.pdf\"" or "attachment; filename=\"doc.pdf\""
        self.content_type("application/pdf")
        self.header("Content-Disposition", disposition)
        return utils.html_to_pdf(post["document"], BASE_URL, MULTIPLE_DATABASES and dbo.database or "")

    def post_print(self, o):
        self.check(users.VIEW_MEDIA)
        l = o.locale
        post = o.post
        self.content_type("text/html")
        return "%s%s%s" % (html.tinymce_print_header(_("Print Preview", l)), post["document"], "</body></html>")

class document_template_edit(ASMEndpoint):
    url = "document_template_edit"
    get_permissions = users.MODIFY_DOCUMENT_TEMPLATES
    post_permissions = users.MODIFY_DOCUMENT_TEMPLATES

    def content(self, o):
        dbo = o.dbo
        post = o.post
        dtid = post.integer("dtid")
        templatename = template.get_document_template_name(dbo, dtid)
        if templatename == "": self.notfound()
        title = templatename
        al.debug("editing %s" % templatename, "code.document_template_edit", dbo)
        if templatename.endswith(".html"):
            content = utils.escape_tinymce(template.get_document_template_content(dbo, dtid))
            self.content_type("text/html")
            self.cache_control(0)
            return html.tinymce_header(title, "document_edit.js", jswindowprint=configuration.js_window_print(dbo)) + \
                html.tinymce_main(dbo.locale, "document_template_edit", dtid=dtid, content=content)
        elif templatename.endswith(".odt"):
            content = template.get_document_template_content(dbo, dtid)
            self.content_type("application/vnd.oasis.opendocument.text")
            self.cache_control(0)
            return content

    def post_save(self, o):
        dbo = o.dbo
        post = o.post
        dtid = post.integer("dtid")
        template.update_document_template_content(dbo, dtid, post["document"])
        self.redirect("document_templates")

    def post_pdf(self, o):
        dbo = o.dbo
        post = o.post
        disposition = configuration.pdf_inline(dbo) and "inline; filename=\"doc.pdf\"" or "attachment; filename=\"doc.pdf\""
        self.content_type("application/pdf")
        self.header("Content-Disposition", disposition)
        return utils.html_to_pdf(post["document"], BASE_URL, MULTIPLE_DATABASES and dbo.database or "")

    def post_print(self, o):
        post = o.post
        l = o.locale
        self.content_type("text/html")
        return "%s%s%s" % (html.tinymce_print_header(_("Print Preview", l)), post["document"], "</body></html>")

class document_media_edit(ASMEndpoint):
    url = "document_media_edit"
    get_permissions = users.VIEW_MEDIA

    def content(self, o):
        dbo = o.dbo
        post = o.post
        lastmod, medianame, mimetype, filedata = extmedia.get_media_file_data(dbo, post.integer("id"))
        al.debug("editing media %d" % post.integer("id"), "code.document_media_edit", dbo)
        title = medianame
        self.content_type("text/html")
        return html.tinymce_header(title, "document_edit.js", jswindowprint=configuration.js_window_print(dbo), \
            onlysavewhendirty=False, readonly=extmedia.has_signature(dbo, post.integer("id"))) + \
            html.tinymce_main(dbo.locale, "document_media_edit", mediaid=post.integer("id"), redirecturl=post["redirecturl"], \
                content=utils.escape_tinymce(filedata))

    def post_save(self, o):
        self.check(users.CHANGE_MEDIA)
        post = o.post
        extmedia.update_file_content(o.dbo, o.user, post.integer("mediaid"), post["document"])
        raise self.redirect(post["redirecturl"])

    def post_pdf(self, o):
        self.check(users.VIEW_MEDIA)
        dbo = o.dbo
        disposition = configuration.pdf_inline(dbo) and "inline; filename=\"doc.pdf\"" or "attachment; filename=\"doc.pdf\""
        self.content_type("application/pdf")
        self.header("Content-Disposition", disposition)
        return utils.html_to_pdf(o.post["document"], BASE_URL, MULTIPLE_DATABASES and dbo.database or "")

    def post_print(self, o):
        self.check(users.VIEW_MEDIA)
        l = o.locale
        self.content_type("text/html")
        return "%s%s%s" % (html.tinymce_print_header(_("Print Preview", l)), o.post["document"], "</body></html>")

class document_repository(JSONEndpoint):
    url = "document_repository"
    get_permissions = users.VIEW_REPO_DOCUMENT

    def controller(self, o):
        documents = dbfs.get_document_repository(o.dbo)
        al.debug("got %d documents in repository" % len(documents), "code.document_repository", o.dbo)
        return { "rows": documents }

    def post_create(self, o):
        self.check(users.ADD_REPO_DOCUMENT)
        if o.post["filename"] != "":
            # If filename is supplied it's an HTML5 upload
            filename = o.post["filename"]
            filedata = o.post["filedata"]
            # Strip the data URL and decode
            if filedata.startswith("data:"):
                filedata = filedata[filedata.find(",")+1:]
                filedata = filedata.replace(" ", "+") # Unescape turns pluses back into spaces, which breaks base64
            filedata = base64.b64decode(filedata)
        else:
            # Otherwise it's an old style file input
            filename = utils.filename_only(o.post.data.filechooser.filename)
            filedata = o.post.data.filechooser.value
        dbfs.upload_document_repository(o.dbo, o.post["path"], filename, filedata)
        self.redirect("document_repository")

    def post_delete(self, o):
        self.check(users.DELETE_REPO_DOCUMENT)
        for i in o.post.integer_list("ids"):
            dbfs.delete_id(o.dbo, i)

class document_repository_file(ASMEndpoint):
    url = "document_repository_file"
    get_permissions = users.VIEW_REPO_DOCUMENT

    def content(self, o):
        if o.post.integer("dbfsid") != 0:
            name = dbfs.get_name_for_id(o.dbo, o.post.integer("dbfsid"))
            mimetype, encoding = mimetypes.guess_type("file://" + name, strict=False)
            disp = "attachment"
            if mimetype == "application/pdf": 
                disp = "inline" # Try to show PDFs in place
            self.content_type(mimetype)
            self.header("Content-Disposition", "%s; filename=\"%s\"" % (disp, name))
            return dbfs.get_string_id(o.dbo, o.post.integer("dbfsid"))

class document_templates(JSONEndpoint):
    url = "document_templates"
    get_permissions = users.MODIFY_DOCUMENT_TEMPLATES
    post_permissions = users.MODIFY_DOCUMENT_TEMPLATES

    def controller(self, o):
        templates = template.get_document_templates(o.dbo)
        al.debug("got %d document templates" % len(templates), "code.document_templates", o.dbo)
        return {
            "rows": templates
        }

    def post_create(self, o):
        return template.create_document_template(o.dbo, o.user, o.post["template"])

    def post_createodt(self, o):
        post = o.post
        fn = post.filename()
        if post["path"] != "": fn = post["path"] + "/" + fn
        template.create_document_template(o.dbo, o.user, fn, ".odt", post.filedata())
        self.redirect("document_templates")

    def post_clone(self, o):
        for t in o.post.integer_list("ids"):
            return template.clone_document_template(o.dbo, o.user, t, o.post["template"])

    def post_delete(self, o):
        for t in o.post.integer_list("ids"):
            template.delete_document_template(o.dbo, o.user, t)

    def post_rename(self, o):
        template.rename_document_template(o.dbo, o.user, o.post.integer("dtid"), o.post["newname"])

class donation(JSONEndpoint):
    url = "donation"
    js_module = "donations"
    get_permissions = users.VIEW_DONATION

    def controller(self, o):
        dbo = o.dbo
        offset = o.post["offset"]
        if offset == "": offset = "m0"
        donations = financial.get_donations(dbo, offset)
        al.debug("got %d donations" % (len(donations)), "code.donation", dbo)
        return {
            "name": "donation",
            "donationtypes": extlookups.get_donation_types(dbo),
            "accounts": financial.get_accounts(dbo),
            "paymenttypes": extlookups.get_payment_types(dbo),
            "frequencies": extlookups.get_donation_frequencies(dbo),
            "templates": template.get_document_templates(dbo),
            "rows": donations
        }

    def post_create(self, o):
        self.check(users.ADD_DONATION)
        return "%s|%s" % (financial.insert_donation_from_form(o.dbo, o.user, o.post), o.post["receiptnumber"])

    def post_update(self, o):
        self.check(users.CHANGE_DONATION)
        financial.update_donation_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_DONATION)
        for did in o.post.integer_list("ids"):
            financial.delete_donation(o.dbo, o.user, did)

    def post_nextreceipt(self, o):
        return financial.get_next_receipt_number(o.dbo)

    def post_receive(self, o):
        self.check( users.CHANGE_DONATION)
        for did in o.post.integer_list("ids"):
            financial.receive_donation(o.dbo, o.user, did)

    def post_personmovements(self, o):
        self.check(users.VIEW_MOVEMENT)
        self.content_type("application/json")
        return utils.json(extmovement.get_person_movements(o.dbo, o.post.integer("personid")))

class donation_receive(JSONEndpoint):
    url = "donation_receive"
    get_permissions = users.ADD_DONATION

    def controller(self, o):
        dbo = o.dbo
        al.debug("receiving donation", "code.donation_receive", dbo)
        return {
            "donationtypes": extlookups.get_donation_types(dbo),
            "paymenttypes": extlookups.get_payment_types(dbo),
            "accounts": financial.get_accounts(dbo)
        }

    def post_create(self, o):
        self.check(users.ADD_DONATION)
        return financial.insert_donations_from_form(o.dbo, o.user, o.post, o.post["received"], True, o.post["person"], o.post["animal"], o.post["movement"], False)

class foundanimal(JSONEndpoint):
    url = "foundanimal"
    js_module = "lostfound"
    get_permissions = users.VIEW_FOUND_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        a = extlostfound.get_foundanimal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        al.debug("open found animal %s %s %s" % (a["AGEGROUP"], a["SPECIESNAME"], a["OWNERNAME"]), "code.foundanimal", dbo)
        return {
            "animal": a,
            "name": "foundanimal",
            "additional": extadditional.get_additional_fields(dbo, a["ID"], "foundanimal"),
            "agegroups": configuration.age_groups(dbo),
            "audit": self.checkb(users.VIEW_AUDIT_TRAIL) and audit.get_audit_for_link(dbo, "animalfound", a["ID"]) or [],
            "breeds": extlookups.get_breeds_by_species(dbo),
            "colours": extlookups.get_basecolours(dbo),
            "logtypes": extlookups.get_log_types(dbo),
            "sexes": extlookups.get_sexes(dbo),
            "species": extlookups.get_species(dbo),
            "templates": template.get_document_templates(dbo),
            "tabcounts": extlostfound.get_foundanimal_satellite_counts(dbo, a["LFID"])[0]
        }

    def post_save(self, o):
        self.check(users.CHANGE_FOUND_ANIMAL)
        extlostfound.update_foundanimal_from_form(o.dbo, o.post, o.user)

    def post_email(self, o):
        l = o.locale
        self.check(users.EMAIL_PERSON)
        if not extlostfound.send_email_from_form(o.dbo, o.user, o.post):
            raise utils.ASMError(_("Failed sending email", l))

    def post_delete(self, o):
        self.check(users.DELETE_FOUND_ANIMAL)
        extlostfound.delete_foundanimal(o.dbo, o.user, o.post.integer("id"))

    def post_toanimal(self, o):
        self.check(users.ADD_ANIMAL)
        return str(extlostfound.create_animal_from_found(o.dbo, o.user, o.post.integer("id")))

    def post_towaitinglist(self, o):
        self.check(users.ADD_WAITING_LIST)
        return str(extlostfound.create_waitinglist_from_found(o.dbo, o.user, o.post.integer("id")))

class foundanimal_diary(JSONEndpoint):
    url = "foundanimal_diary"
    js_module = "diary"
    get_permissions = users.VIEW_DIARY

    def controller(self, o):
        dbo = o.dbo
        a = extlostfound.get_foundanimal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        diaries = extdiary.get_diaries(dbo, extdiary.FOUNDANIMAL, o.post.integer("id"))
        al.debug("got %d diaries for found animal %s %s %s" % (len(diaries), a["AGEGROUP"], a["SPECIESNAME"], a["OWNERNAME"]), "code.foundanimal_diary", dbo)
        return {
            "rows": diaries,
            "animal": a,
            "tabcounts": extlostfound.get_foundanimal_satellite_counts(dbo, a["LFID"])[0],
            "name": "foundanimal_diary",
            "linkid": a["LFID"],
            "linktypeid": extdiary.FOUNDANIMAL,
            "forlist": users.get_users_and_roles(dbo)
        }

class foundanimal_find(JSONEndpoint):
    url = "foundanimal_find"
    js_module = "lostfound_find"
    get_permissions = users.VIEW_FOUND_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        return {
            "agegroups": configuration.age_groups(dbo),
            "colours": extlookups.get_basecolours(dbo),
            "name": "foundanimal_find",
            "species": extlookups.get_species(dbo),
            "breeds": extlookups.get_breeds_by_species(dbo),
            "sexes": extlookups.get_sexes(dbo),
            "mode": "found"
        }

class foundanimal_find_results(JSONEndpoint):
    url = "foundanimal_find_results"
    js_module = "lostfound_find_results"
    get_permissions = users.VIEW_FOUND_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        results = extlostfound.get_foundanimal_find_advanced(dbo, o.post.data, configuration.record_search_limit(dbo))
        al.debug("found %d results for %s" % (len(results), self.query()), "code.foundanimal_find_results", dbo)
        return {
            "rows": results,
            "name": "foundanimal_find_results"
        }

class foundanimal_log(JSONEndpoint):
    url = "foundanimal_log"
    js_module = "log"
    get_permissions = users.VIEW_LOG

    def controller(self, o):
        dbo = o.dbo
        logfilter = o.post.integer("filter")
        if logfilter == 0: logfilter = configuration.default_log_filter(dbo)
        a = extlostfound.get_foundanimal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        logs = extlog.get_logs(dbo, extlog.FOUNDANIMAL, o.post.integer("id"), logfilter)
        return {
            "name": "foundanimal_log",
            "linkid": o.post.integer("id"),
            "linktypeid": extlog.FOUNDANIMAL,
            "filter": logfilter,
            "rows": logs,
            "animal": a,
            "tabcounts": extlostfound.get_foundanimal_satellite_counts(dbo, a["LFID"])[0],
            "logtypes": extlookups.get_log_types(dbo)
        }

class foundanimal_media(JSONEndpoint):
    url = "foundanimal_media"
    js_module = "media"
    get_permissions = users.VIEW_MEDIA

    def controller(self, o):
        dbo = o.dbo
        a = extlostfound.get_foundanimal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        m = extmedia.get_media(dbo, extmedia.FOUNDANIMAL, o.post.integer("id"))
        al.debug("got %d media for found animal %s %s %s" % (len(m), a["AGEGROUP"], a["SPECIESNAME"], a["OWNERNAME"]), "code.foundanimal_media", dbo)
        return {
            "media": m,
            "animal": a,
            "tabcounts": extlostfound.get_foundanimal_satellite_counts(dbo, a["LFID"])[0],
            "showpreferred": True,
            "linkid": o.post.integer("id"),
            "linktypeid": extmedia.FOUNDANIMAL,
            "logtypes": extlookups.get_log_types(dbo),
            "name": self.url,
            "sigtype": ELECTRONIC_SIGNATURES
        }

class foundanimal_new(JSONEndpoint):
    url = "foundanimal_new"
    js_module = "lostfound_new"
    get_permissions = users.ADD_FOUND_ANIMAL
    post_permissions = users.ADD_FOUND_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        return {
            "agegroups": configuration.age_groups(dbo),
            "additional": extadditional.get_additional_fields(dbo, 0, "foundanimal"),
            "colours": extlookups.get_basecolours(dbo),
            "species": extlookups.get_species(dbo),
            "breeds": extlookups.get_breeds_by_species(dbo),
            "sexes": extlookups.get_sexes(dbo),
            "name": "foundanimal_new"
        }

    def post_all(self, o):
        return str(extlostfound.insert_foundanimal_from_form(o.dbo, o.post, o.user))

class giftaid_hmrc_spreadsheet(JSONEndpoint):
    url = "giftaid_hmrc_spreadsheet"
    get_permissions = users.VIEW_DONATION

    def controller(self, o):
        return {}

    def post_all(self, o):
        fromdate = o.post["fromdate"]
        todate = o.post["todate"]
        al.debug("generating HMRC giftaid spreadsheet for %s -> %s" % (fromdate, todate), "code.giftaid_hmrc_spreadsheet", o.dbo)
        self.content_type("application/vnd.oasis.opendocument.spreadsheet")
        self.cache_control(0)
        self.header("Content-Disposition", "attachment; filename=\"giftaid.ods\"")
        return financial.giftaid_spreadsheet(o.dbo, PATH, o.post.date("fromdate"), o.post.date("todate"))

class htmltemplates(JSONEndpoint):
    url = "htmltemplates"
    get_permissions = users.PUBLISH_OPTIONS
    post_permissions = users.PUBLISH_OPTIONS

    def controller(self, o):
        templates = template.get_html_templates(o.dbo)
        al.debug("editing %d html templates" % len(templates), "code.htmltemplates", o.dbo)
        return {
            "rows": templates
        }

    def post_create(self, o):
        if o.post["templatename"] in ( "onlineform", "report" ):
            raise utils.ASMValidationError("Illegal name '%s'" % o.post["templatename"])
        template.update_html_template(o.dbo, o.user, o.post["templatename"], o.post["header"], o.post["body"], o.post["footer"])

    def post_update(self, o):
        if o.post["templatename"] in ( "onlineform", "report" ):
            raise utils.ASMValidationError("Illegal name '%s'" % o.post["templatename"])
        template.update_html_template(o.dbo, o.user, o.post["templatename"], o.post["header"], o.post["body"], o.post["footer"])

    def post_delete(self, o):
        for name in o.post["names"].split(","):
            if name != "": template.delete_html_template(o.dbo, o.user, name)

class incident(JSONEndpoint):
    url = "incident"
    get_permissions = users.VIEW_INCIDENT

    def controller(self, o):
        dbo = o.dbo
        a = extanimalcontrol.get_animalcontrol(dbo, o.post.integer("id"))
        extanimalcontrol.check_view_permission(dbo, o.user, o.session, o.post.integer("id"))
        if o.siteid != 0 and a["SITEID"] != 0 and o.siteid != a["SITEID"]:
            raise utils.ASMPermissionError("incident not in user site")
        if a is None: self.notfound()
        al.debug("open incident %s %s %s" % (a["ACID"], a["INCIDENTNAME"], python2display(o.locale, a["INCIDENTDATETIME"])), "code.incident", dbo)
        return {
            "agegroups": configuration.age_groups(dbo),
            "additional": extadditional.get_additional_fields(dbo, a["ACID"], "incident"),
            "audit": self.checkb(users.VIEW_AUDIT_TRAIL) and audit.get_audit_for_link(dbo, "animalcontrol", a["ACID"]) or [],
            "incident": a,
            "jurisdictions": extlookups.get_jurisdictions(dbo),
            "animallinks": extanimalcontrol.get_animalcontrol_animals(dbo, o.post.integer("id")),
            "incidenttypes": extlookups.get_incident_types(dbo),
            "completedtypes": extlookups.get_incident_completed_types(dbo),
            "pickuplocations": extlookups.get_pickup_locations(dbo),
            "roles": users.get_roles(dbo),
            "species": extlookups.get_species(dbo),
            "sexes": extlookups.get_sexes(dbo),
            "sites": extlookups.get_sites(dbo),
            "tabcounts": extanimalcontrol.get_animalcontrol_satellite_counts(dbo, a["ACID"])[0],
            "templates": template.get_document_templates(dbo),
            "users": users.get_users(dbo)
        }

    def post_save(self, o):
        self.check(users.CHANGE_INCIDENT)
        extanimalcontrol.update_animalcontrol_from_form(o.dbo, o.post, o.user)

    def post_delete(self, o):
        self.check(users.DELETE_INCIDENT)
        extanimalcontrol.delete_animalcontrol(o.dbo, o.user, o.post.integer("id"))

    def post_latlong(self, o):
        self.check(users.CHANGE_INCIDENT)
        extanimalcontrol.update_dispatch_latlong(o.dbo, o.post.integer("incidentid"), o.post["latlong"])

    def post_email(self, o):
        self.check(users.EMAIL_PERSON)
        if not extperson.send_email_from_form(o.dbo, o.user, o.post):
            l = o.locale
            raise utils.ASMError(_("Failed sending email", l))

    def post_linkanimaladd(self, o):
        self.check(users.CHANGE_INCIDENT)
        extanimalcontrol.update_animalcontrol_addlink(o.dbo, o.user, o.post.integer("id"), o.post.integer("animalid"))

    def post_linkanimaldelete(self, o):
        self.check(users.CHANGE_INCIDENT)
        extanimalcontrol.update_animalcontrol_removelink(o.dbo, o.user, o.post.integer("id"), o.post.integer("animalid"))

class incident_citations(JSONEndpoint):
    url = "incident_citations"
    js_module = "citations"
    get_permissions = users.VIEW_CITATION

    def controller(self, o):
        dbo = o.dbo
        a = extanimalcontrol.get_animalcontrol(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        citations = financial.get_incident_citations(dbo, o.post.integer("id"))
        al.debug("got %d citations" % len(citations), "code.incident_citations", dbo)
        return {
            "name": "incident_citations",
            "rows": citations,
            "incident": a,
            "tabcounts": extanimalcontrol.get_animalcontrol_satellite_counts(dbo, a["ACID"])[0],
            "citationtypes": extlookups.get_citation_types(dbo)
        }

class incident_find(JSONEndpoint):
    url = "incident_find"
    get_permissions = users.VIEW_INCIDENT

    def controller(self, o):
        dbo = o.dbo
        return {
            "agegroups": configuration.age_groups(dbo),
            "incidenttypes": extlookups.get_incident_types(dbo),
            "completedtypes": extlookups.get_incident_completed_types(dbo),
            "citationtypes": extlookups.get_citation_types(dbo),
            "jurisdictions": extlookups.get_jurisdictions(dbo),
            "pickuplocations": extlookups.get_pickup_locations(dbo),
            "species": extlookups.get_species(dbo),
            "sexes": extlookups.get_sexes(dbo),
            "users": users.get_users(dbo)
        }

class incident_find_results(JSONEndpoint):
    url = "incident_find_results"
    get_permissions = users.VIEW_INCIDENT

    def controller(self, o):
        results = extanimalcontrol.get_animalcontrol_find_advanced(o.dbo, o.post.data, o.user, configuration.record_search_limit(o.dbo))
        al.debug("found %d results for %s" % (len(results), self.query()), "code.incident_find_results", o.dbo)
        return {
            "rows": results
        }

class incident_diary(JSONEndpoint):
    url = "incident_diary"
    js_module = "diary"
    get_permissions = users.VIEW_DIARY

    def controller(self, o):
        dbo = o.dbo
        a = extanimalcontrol.get_animalcontrol(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        diaries = extdiary.get_diaries(dbo, extdiary.ANIMALCONTROL, o.post.integer("id"))
        al.debug("got %d diaries" % len(diaries), "code.incident_diary", dbo)
        return {
            "rows": diaries,
            "incident": a,
            "tabcounts": extanimalcontrol.get_animalcontrol_satellite_counts(dbo, a["ACID"])[0],
            "name": "incident_diary",
            "linkid": a["ACID"],
            "linktypeid": extdiary.ANIMALCONTROL,
            "forlist": users.get_users_and_roles(dbo)
        }

class incident_log(JSONEndpoint):
    url = "incident_log"
    js_module = "log"
    get_permissions = users.VIEW_LOG

    def controller(self, o):
        dbo = o.dbo
        a = extanimalcontrol.get_animalcontrol(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        logfilter = o.post.integer("filter")
        if logfilter == 0: logfilter = configuration.default_log_filter(dbo)
        logs = extlog.get_logs(dbo, extlog.ANIMALCONTROL, o.post.integer("id"), logfilter)
        al.debug("got %d logs" % len(logs), "code.incident_log", dbo)
        return {
            "name": "incident_log",
            "linkid": o.post.integer("id"),
            "linktypeid": extlog.ANIMALCONTROL,
            "filter": logfilter,
            "rows": logs,
            "incident": a,
            "tabcounts": extanimalcontrol.get_animalcontrol_satellite_counts(dbo, a["ACID"])[0],
            "logtypes": extlookups.get_log_types(dbo)
        }

class incident_map(JSONEndpoint):
    url = "incident_map"
    get_permissions = users.VIEW_INCIDENT

    def controller(self, o):
        dbo = o.dbo
        rows = extanimalcontrol.get_animalcontrol_find_advanced(dbo, { "filter": "incomplete" }, o.user)
        al.debug("incident map, %d active" % (len(rows)), "code.incident_map", dbo)
        return {
            "rows": rows
        }

class incident_media(JSONEndpoint):
    url = "incident_media"
    js_module = "media"
    get_permissions = users.VIEW_MEDIA

    def controller(self, o):
        dbo = o.dbo
        a = extanimalcontrol.get_animalcontrol(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        m = extmedia.get_media(dbo, extmedia.ANIMALCONTROL, o.post.integer("id"))
        al.debug("got %d media" % len(m), "code.incident_media", dbo)
        return {
            "media": m,
            "incident": a,
            "tabcounts": extanimalcontrol.get_animalcontrol_satellite_counts(dbo, a["ACID"])[0],
            "showpreferred": True,
            "linkid": o.post.integer("id"),
            "linktypeid": extmedia.ANIMALCONTROL,
            "logtypes": extlookups.get_log_types(dbo),
            "name": self.url,
            "sigtype": ELECTRONIC_SIGNATURES
        }

class incident_new(JSONEndpoint):
    url = "incident_new"
    get_permissions = users.ADD_INCIDENT
    post_permissions = users.ADD_INCIDENT

    def controller(self, o):
        dbo = o.dbo
        al.debug("add incident", "code.incident_new", dbo)
        return {
            "incidenttypes": extlookups.get_incident_types(dbo),
            "jurisdictions": extlookups.get_jurisdictions(dbo),
            "additional": extadditional.get_additional_fields(dbo, 0, "incident"),
            "pickuplocations": extlookups.get_pickup_locations(dbo),
            "roles": users.get_roles(dbo),
            "sites": extlookups.get_sites(dbo),
            "users": users.get_users(dbo)
        }

    def post_all(self, o):
        incidentid = extanimalcontrol.insert_animalcontrol_from_form(o.dbo, o.post, o.user)
        return str(incidentid)

class latency(JSONEndpoint):
    url = "latency"

    def controller(self, o):
        return {}

    def post_all(self, o):
        self.content_type("text/plain")
        self.cache_control(0)
        return "pong"

class licence(JSONEndpoint):
    url = "licence"
    get_permissions = users.VIEW_LICENCE

    def controller(self, o):
        dbo = o.dbo
        offset = o.post["offset"]
        if offset == "": offset = "i31"
        licences = financial.get_licences(dbo, offset)
        al.debug("got %d licences" % len(licences), "code.licence", dbo)
        return {
            "name": "licence",
            "rows": licences,
            "templates": template.get_document_templates(dbo),
            "licencetypes": extlookups.get_licence_types(dbo)
        }

    def post_create(self, o):
        self.check(users.ADD_LICENCE)
        return financial.insert_licence_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.CHANGE_LICENCE)
        financial.update_licence_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_LICENCE)
        for lid in o.post.integer_list("ids"):
            financial.delete_licence(o.dbo, o.user, lid)

class licence_renewal(JSONEndpoint):
    url = "licence_renewal"
    get_permissions = users.ADD_LICENCE
    post_permissions = users.ADD_LICENCE

    def controller(self, o):
        dbo = o.dbo
        al.debug("renewing licence", "code.licence_renewal", dbo)
        return {
            "donationtypes": extlookups.get_donation_types(dbo),
            "licencetypes": extlookups.get_licence_types(dbo),
            "paymenttypes": extlookups.get_payment_types(dbo),
            "accounts": financial.get_accounts(dbo)
        }

    def post_all(self, o):
        financial.insert_donations_from_form(o.dbo, o.user, o.post, o.post["issuedate"], False, o.post["person"], o.post["animal"]) 
        return financial.insert_licence_from_form(o.dbo, o.user, o.post)

class litters(JSONEndpoint):
    url = "litters"
    get_permissions = users.VIEW_LITTER

    def controller(self, o):
        dbo = o.dbo
        litters = extanimal.get_litters(dbo)
        al.debug("got %d litters" % len(litters), "code.litters", dbo)
        return {
            "rows": litters,
            "species": extlookups.get_species(dbo)
        }

    def post_create(self, o):
        self.check(users.ADD_LITTER)
        return extanimal.insert_litter_from_form(o.dbo, o.user, o.post)

    def post_nextlitterid(self, o):
        nextid = db.query_int(o.dbo, "SELECT MAX(ID) FROM animallitter") + 1
        return utils.padleft(nextid, 6)

    def post_update(self, o):
        self.check(users.CHANGE_LITTER)
        extanimal.update_litter_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_LITTER) 
        for lid in o.post.integer_list("ids"):
            extanimal.delete_litter(o.dbo, o.user, lid)

class log(ASMEndpoint):
    url = "log"

    def post_create(self, o):
        self.check(users.ADD_LOG)
        return extlog.insert_log_from_form(o.dbo, o.user, o.post.integer("linktypeid"), o.post.integer("linkid"), o.post)

    def post_update(self, o):
        self.check(users.CHANGE_LOG)
        extlog.update_log_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_LOG)
        for lid in o.post.integer_list("ids"):
            extlog.delete_log(o.dbo, o.user, lid)

class log_new(JSONEndpoint):
    url = "log_new"
    get_permissions = users.ADD_LOG
    post_permissions = users.ADD_LOG

    def controller(self, o):
        dbo = o.dbo
        mode = o.post["mode"]
        if mode == "": mode = "animal"
        return {
            "logtypes": extlookups.get_log_types(dbo),
            "mode": mode
        }

    def post_animal(self, o):
        extlog.insert_log_from_form(o.dbo, o.user, extlog.ANIMAL, o.post.integer("animal"), o.post)

    def post_person(self, o):
        extlog.insert_log_from_form(o.dbo, o.user, extlog.PERSON, o.post.integer("person"), o.post)

class lookups(JSONEndpoint):
    url = "lookups"
    get_permissions = users.MODIFY_LOOKUPS
    post_permissions = users.MODIFY_LOOKUPS

    def controller(self, o):
        dbo = o.dbo
        l = o.locale
        tablename = o.post["tablename"]
        if tablename == "": tablename = "animaltype"
        table = list(extlookups.LOOKUP_TABLES[tablename])
        table[0] = translate(table[0], l)
        table[2] = translate(table[2], l)
        rows = extlookups.get_lookup(dbo, tablename, table[1])
        al.debug("edit lookups for %s, got %d rows" % (tablename, len(rows)), "code.lookups", dbo)
        return {
            "rows": rows,
            "adoptapetcolours": extlookups.ADOPTAPET_COLOURS,
            "petfinderspecies": extlookups.PETFINDER_SPECIES,
            "petfinderbreeds": extlookups.PETFINDER_BREEDS,
            "sites": extlookups.get_sites(dbo),
            "tablename": tablename,
            "tablelabel": table[0],
            "namefield": table[1].upper(),
            "namelabel": table[2],
            "descfield": table[3].upper(),
            "hasspecies": table[4] == 1,
            "haspfspecies": table[5] == 1,
            "haspfbreed": table[6] == 1,
            "hasapcolour": table[7] == 1,
            "hasdefaultcost": table[8] == 1,
            "hasunits": table[9] == 1,
            "hassite": table[10] == 1,
            "canadd": table[11] == 1,
            "candelete": table[12] == 1,
            "canretire": table[13] == 1,
            "species": extlookups.get_species(dbo),
            "tables": html.json_lookup_tables(l)
        }

    def post_create(self, o):
        post = o.post
        return extlookups.insert_lookup(o.dbo, post["lookup"], post["lookupname"], post["lookupdesc"], \
            post.integer("species"), post["pfbreed"], post["pfspecies"], post["apcolour"], post["units"], post.integer("site"), post.integer("defaultcost"), post.integer("retired"))

    def post_update(self, o):
        post = o.post
        extlookups.update_lookup(o.dbo, post.integer("id"), post["lookup"], post["lookupname"], post["lookupdesc"], \
            post.integer("species"), post["pfbreed"], post["pfspecies"], post["apcolour"], post["units"], post.integer("site"), post.integer("defaultcost"), post.integer("retired"))

    def post_delete(self, o):
        for lid in o.post.integer_list("ids"):
            extlookups.delete_lookup(o.dbo, o.post["lookup"], lid)

    def post_active(self, o):
        for lid in o.post.integer_list("ids"):
            extlookups.update_lookup_retired(o.dbo, o.post["lookup"], lid, 0)

    def post_inactive(self, o):
        for lid in o.post.integer_list("ids"):
            extlookups.update_lookup_retired(o.dbo, o.post["lookup"], lid, 1)

class lostanimal(JSONEndpoint):
    url = "lostanimal"
    js_module = "lostfound"
    get_permissions = users.VIEW_LOST_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        a = extlostfound.get_lostanimal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        al.debug("open lost animal %s %s %s" % (a["AGEGROUP"], a["SPECIESNAME"], a["OWNERNAME"]), "code.foundanimal", dbo)
        return {
            "animal": a,
            "name": "lostanimal",
            "additional": extadditional.get_additional_fields(dbo, a["ID"], "lostanimal"),
            "agegroups": configuration.age_groups(dbo),
            "audit": self.checkb(users.VIEW_AUDIT_TRAIL) and audit.get_audit_for_link(dbo, "animallost", a["ID"]) or [],
            "breeds": extlookups.get_breeds_by_species(dbo),
            "colours": extlookups.get_basecolours(dbo),
            "logtypes": extlookups.get_log_types(dbo),
            "sexes": extlookups.get_sexes(dbo),
            "species": extlookups.get_species(dbo),
            "templates": template.get_document_templates(dbo),
            "tabcounts": extlostfound.get_lostanimal_satellite_counts(dbo, a["LFID"])[0]
        }

    def post_save(self, o):
        self.check(users.CHANGE_LOST_ANIMAL)
        extlostfound.update_lostanimal_from_form(o.dbo, o.post, o.user)

    def post_email(self, o):
        self.check(users.EMAIL_PERSON)
        l = o.locale
        if not extlostfound.send_email_from_form(o.dbo, o.user, o.post):
            raise utils.ASMError(_("Failed sending email", l))

    def post_delete(self, o):
        self.check(users.DELETE_LOST_ANIMAL)
        extlostfound.delete_lostanimal(o.dbo, o.user, o.post.integer("id"))

class lostanimal_diary(JSONEndpoint):
    url = "lostanimal_diary"
    js_module = "diary"
    get_permissions = users.VIEW_DIARY

    def controller(self, o):
        dbo = o.dbo
        a = extlostfound.get_lostanimal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        diaries = extdiary.get_diaries(dbo, extdiary.LOSTANIMAL, o.post.integer("id"))
        al.debug("got %d diaries for lost animal %s %s %s" % (len(diaries), a["AGEGROUP"], a["SPECIESNAME"], a["OWNERNAME"]), "code.foundanimal_diary", dbo)
        return {
            "rows": diaries,
            "animal": a,
            "tabcounts": extlostfound.get_lostanimal_satellite_counts(dbo, a["LFID"])[0],
            "name": "lostanimal_diary",
            "linkid": a["LFID"],
            "linktypeid": extdiary.LOSTANIMAL,
            "forlist": users.get_users_and_roles(dbo)
        }

class lostanimal_find(JSONEndpoint):
    url = "lostanimal_find"
    js_module = "lostfound_find"
    get_permissions = users.VIEW_LOST_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        return {
            "agegroups": configuration.age_groups(dbo),
            "name": "lostanimal_find",
            "colours": extlookups.get_basecolours(dbo),
            "species": extlookups.get_species(dbo),
            "breeds": extlookups.get_breeds_by_species(dbo),
            "sexes": extlookups.get_sexes(dbo),
            "mode": "lost"
        }

class lostanimal_find_results(JSONEndpoint):
    url = "lostanimal_find_results"
    js_module = "lostfound_find_results"
    get_permissions = users.VIEW_LOST_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        results = extlostfound.get_lostanimal_find_advanced(dbo, o.post.data, configuration.record_search_limit(dbo))
        al.debug("found %d results for %s" % (len(results), self.query()), "code.lostanimal_find_results", dbo)
        return {
            "rows": results,
            "name": "lostanimal_find_results"
        }

class lostanimal_log(JSONEndpoint):
    url = "lostanimal_log"
    js_module = "log"
    get_permissions = users.VIEW_LOG

    def controller(self, o):
        dbo = o.dbo
        logfilter = o.post.integer("filter")
        if logfilter == 0: logfilter = configuration.default_log_filter(dbo)
        a = extlostfound.get_lostanimal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        logs = extlog.get_logs(dbo, extlog.LOSTANIMAL, o.post.integer("id"), logfilter)
        return {
            "name": "lostanimal_log",
            "linkid": o.post.integer("id"),
            "linktypeid": extlog.LOSTANIMAL,
            "filter": logfilter,
            "rows": logs,
            "animal": a,
            "tabcounts": extlostfound.get_lostanimal_satellite_counts(dbo, a["LFID"])[0],
            "logtypes": extlookups.get_log_types(dbo)
        }

class lostanimal_media(JSONEndpoint):
    url = "lostanimal_media"
    js_module = "media"
    get_permissions = users.VIEW_MEDIA

    def controller(self, o):
        dbo = o.dbo
        a = extlostfound.get_lostanimal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        m = extmedia.get_media(dbo, extmedia.LOSTANIMAL, o.post.integer("id"))
        al.debug("got %d media for lost animal %s %s %s" % (len(m), a["AGEGROUP"], a["SPECIESNAME"], a["OWNERNAME"]), "code.foundanimal_media", dbo)
        return {
            "media": m,
            "animal": a,
            "tabcounts": extlostfound.get_lostanimal_satellite_counts(dbo, a["LFID"])[0],
            "showpreferred": True,
            "linkid": o.post.integer("id"),
            "linktypeid": extmedia.LOSTANIMAL,
            "logtypes": extlookups.get_log_types(dbo),
            "name": self.url, 
            "sigtype": ELECTRONIC_SIGNATURES
        }

class lostanimal_new(JSONEndpoint):
    url = "lostanimal_new"
    js_module = "lostfound_new"
    get_permissions = users.ADD_LOST_ANIMAL
    post_permissions = users.ADD_LOST_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        return {
            "agegroups": configuration.age_groups(dbo),
            "additional": extadditional.get_additional_fields(dbo, 0, "lostanimal"),
            "colours": extlookups.get_basecolours(dbo),
            "species": extlookups.get_species(dbo),
            "breeds": extlookups.get_breeds_by_species(dbo),
            "sexes": extlookups.get_sexes(dbo),
            "name": "lostanimal_new"
        }

    def post_all(self, o):
        return str(extlostfound.insert_lostanimal_from_form(o.dbo, o.post, o.user))

class lostfound_match(ASMEndpoint):
    url = "lostfound_match"
    get_permissions = ( users.VIEW_LOST_ANIMAL, users.VIEW_FOUND_ANIMAL, users.VIEW_PERSON )

    def content(self, o):
        dbo = o.dbo
        post = o.post
        lostanimalid = post.integer("lostanimalid")
        foundanimalid = post.integer("foundanimalid")
        animalid = post.integer("animalid")
        self.content_type("text/html")
        self.cache_control(0)
        # If no parameters have been given, use the cached daily copy of the match report
        if lostanimalid == 0 and foundanimalid == 0 and animalid == 0:
            al.debug("no parameters given, using cached report at /reports/daily/lost_found_match.html", "code.lostfound_match", dbo)
            return configuration.lostfound_report(dbo)
        else:
            al.debug("match lost=%d, found=%d, animal=%d" % (lostanimalid, foundanimalid, animalid), "code.lostfound_match", dbo)
            return extlostfound.match_report(dbo, session.user, lostanimalid, foundanimalid, animalid)

class mailmerge_criteria(JSONEndpoint):
    url = "mailmerge_criteria"
    get_permissions = users.MAIL_MERGE

    def controller(self, o):
        dbo = o.dbo
        post = o.post
        title = extreports.get_title(o.dbo, o.post.integer("id"))
        al.debug("building report criteria form for mailmerge %d %s" % (post.integer("id"), title), "code.mailmerge", dbo)
        return {
            "id": post.integer("id"),
            "title": title,
            "criteriahtml": extreports.get_criteria_controls(o.dbo, o.post.integer("id"))
        }

class mailmerge(JSONEndpoint):
    url = "mailmerge"
    get_permissions = users.MAIL_MERGE
    post_permissions = users.MAIL_MERGE

    def controller(self, o):
        l = o.locale
        dbo = o.dbo
        post = o.post
        crid = post.integer("id")
        crit = extreports.get_criteria_controls(dbo, crid, locationfilter = o.locationfilter, siteid = o.siteid) 
        title = extreports.get_title(dbo, crid)
        # If this mail merge takes criteria and none were supplied, go to the criteria screen to get them
        if crit != "" and post["hascriteria"] == "": self.redirect("mailmerge_criteria?id=%d" % crid)
        al.debug("entering mail merge selection mode for %d" % post.integer("id"), "code.mailmerge", dbo)
        p = extreports.get_criteria_params(dbo, crid, post)
        # values we store in the session for the post handler to save sending them back every time
        o.session.mergeparams = p
        o.session.mergereport = crid
        o.session.mergetitle = title.replace(" ", "_").replace("\"", "").replace("'", "").lower()
        rows, cols = extreports.execute_query(dbo, crid, o.user, p)
        if rows is None: rows = []
        al.debug("got merge rows (%d items)" % len(rows), "code.mailmerge", dbo)
        # construct a list of field tokens for the email helper
        fields = []
        if len(rows) > 0:
            for fname in sorted(rows[0].iterkeys()):
                fields.append(fname)
        # send the selection form
        title = _("Mail Merge - {0}", l).format(title)
        return {
            "title": title,
            "fields": fields,
            "numrows": len(rows),
            "hasperson": "OWNERNAME" in fields and "OWNERADDRESS" in fields and "OWNERTOWN" in fields and "OWNERPOSTCODE" in fields,
            "templates": template.get_document_templates(dbo)
        }
   
    def post_email(self, o):
        dbo = o.dbo
        post = o.post
        rows, cols = extreports.execute_query(dbo, o.session.mergereport, o.user, o.session.mergeparams)
        fromadd = post["from"]
        subject = post["subject"]
        body = post["body"]
        utils.send_bulk_email(dbo, fromadd, subject, body, rows, "html")

    def post_document(self, o):
        dbo = o.dbo
        post = o.post
        rows, cols = extreports.execute_query(dbo, o.session.mergereport, o.user, o.session.mergeparams)
        templateid = post.integer("templateid")
        templatecontent = template.get_document_template_content(dbo, templateid)
        templatename = template.get_document_template_name(dbo, templateid)
        if not templatename.endswith(".html"):
            raise utils.ASMValidationError("Only html templates are allowed")
        # Generate a document from the template for each row
        org_tags = wordprocessor.org_tags(dbo, session.user)
        c = []
        for d in rows:
            c.append( wordprocessor.substitute_tags(templatecontent, wordprocessor.append_tags(d, org_tags)) )
        content = '<div class="mce-pagebreak" style="page-break-before: always; clear: both; border: 0">&nbsp;</div>'.join(c)
        self.content_type("text/html")
        self.cache_control(0)
        return html.tinymce_header(templatename, "document_edit.js", jswindowprint=True, pdfenabled=False, readonly=True) + \
            html.tinymce_main(o.locale, "", recid=0, linktype="", \
                dtid="", content=utils.escape_tinymce(content))

    def post_labels(self, o):
        dbo = o.dbo
        post = o.post
        rows, cols = extreports.execute_query(dbo, o.session.mergereport, o.user, o.session.mergeparams)
        self.content_type("application/pdf")
        disposition = configuration.pdf_inline(dbo) and "inline; filename=%s" or "attachment; filename=%s"
        self.header("Content-Disposition", disposition % o.session.mergetitle + ".pdf")
        return utils.generate_label_pdf(dbo, o.locale, rows, post["papersize"], post["units"],
            post.floating("hpitch"), post.floating("vpitch"), 
            post.floating("width"), post.floating("height"), 
            post.floating("lmargin"), post.floating("tmargin"),
            post.integer("cols"), post.integer("rows"))

    def post_csv(self, o):
        dbo = o.dbo
        post = o.post
        rows, cols = extreports.execute_query(dbo, o.session.mergereport, o.user, o.session.mergeparams)
        self.content_type("text/csv")
        self.header("Content-Disposition", u"attachment; filename=" + utils.decode_html(o.session.mergetitle) + u".csv")
        includeheader = 1 == post.boolean("includeheader")
        return utils.csv(o.locale, rows, cols, includeheader)

    def post_preview(self, o):
        dbo = o.dbo
        rows, cols = extreports.execute_query(dbo, o.session.mergereport, o.user, o.session.mergeparams)
        al.debug("returning preview rows for %d" % o.session.mergereport, "code.mailmerge", dbo)
        return utils.json(rows)

class medical(JSONEndpoint):
    url = "medical"
    get_permissions = users.VIEW_MEDICAL

    def controller(self, o):
        dbo = o.dbo
        offset = o.post["offset"]
        if offset == "": offset = "m365"
        med = extmedical.get_treatments_outstanding(dbo, offset, o.locationfilter, o.siteid)
        profiles = extmedical.get_profiles(dbo)
        al.debug("got %d medical treatments" % len(med), "code.medical", dbo)
        return {
            "profiles": profiles,
            "rows": med,
            "newmed": o.post.integer("newmed") == 1,
            "name": "medical",
            "stockitems": extstock.get_stock_items(dbo),
            "stockusagetypes": extlookups.get_stock_usage_types(dbo),
            "users": users.get_users(dbo)
        }

    def post_create(self, o):
        self.check(users.ADD_MEDICAL)
        extmedical.insert_regimen_from_form(o.dbo, o.user, o.post)

    def post_createbulk(self, o):
        self.check(users.ADD_MEDICAL)
        for animalid in o.post.integer_list("animals"):
            o.post.data["animal"] = str(animalid)
            extmedical.insert_regimen_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.CHANGE_MEDICAL)
        extmedical.update_regimen_from_form(o.dbo, o.user, o.post)

    def post_delete_regimen(self, o):
        self.check(users.DELETE_MEDICAL)
        for mid in o.post.integer_list("ids"):
            extmedical.delete_regimen(o.dbo, o.user, mid)

    def post_delete_treatment(self, o):
        self.check(users.DELETE_MEDICAL)
        for mid in o.post.integer_list("ids"):
            extmedical.delete_treatment(o.dbo, o.user, mid)

    def post_get_profile(self, o):
        return utils.json([extmedical.get_profile(o.dbo, o.post.integer("profileid"))])

    def post_given(self, o):
        self.check(users.BULK_COMPLETE_MEDICAL)
        post = o.post
        newdate = post.date("newdate")
        vet = post.integer("givenvet")
        by = post["givenby"]
        comments = post["treatmentcomments"]
        for mid in post.integer_list("ids"):
            extmedical.update_treatment_given(o.dbo, o.user, mid, newdate, by, vet, comments)
        if post.integer("item") != -1:
            extstock.deduct_stocklevel_from_form(session.dbo, session.user, post)

    def post_required(self, o):
        self.check(users.BULK_COMPLETE_MEDICAL)
        newdate = o.post.date("newdate")
        for mid in o.post.integer_list("ids"):
            extmedical.update_treatment_required(o.dbo, o.user, mid, newdate)

class medicalprofile(JSONEndpoint):
    url = "medicalprofile"
    get_permissions = users.VIEW_MEDICAL

    def controller(self, o):
        med = extmedical.get_profiles(o.dbo)
        al.debug("got %d medical profiles" % len(med), "code.medical_profile", o.dbo)
        return {
            "rows": med
        }

    def post_create(self, o):
        self.check(users.ADD_MEDICAL)
        extmedical.insert_profile_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.CHANGE_MEDICAL)
        extmedical.update_profile_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_MEDICAL)
        for mid in o.post.integer_list("ids"):
            extmedical.delete_profile(o.dbo, o.user, mid)

class move_adopt(JSONEndpoint):
    url = "move_adopt"
    get_permissions = users.ADD_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        return {
            "donationtypes": extlookups.get_donation_types(dbo),
            "accounts": financial.get_accounts(dbo),
            "paymenttypes": extlookups.get_payment_types(dbo)
        }

    def post_create(self, o):
        self.check(users.ADD_MOVEMENT)
        return str(extmovement.insert_adoption_from_form(o.dbo, o.user, o.post))

    def post_cost(self, o):
        dbo = o.dbo
        post = o.post
        l = o.locale
        self.check(users.VIEW_COST)
        dailyboardcost = extanimal.get_daily_boarding_cost(dbo, post.integer("id"))
        dailyboardcostdisplay = format_currency(l, dailyboardcost)
        daysonshelter = extanimal.get_days_on_shelter(dbo, post.integer("id"))
        totaldisplay = format_currency(l, dailyboardcost * daysonshelter)
        return totaldisplay + "||" + \
            _("On shelter for {0} days, daily cost {1}, cost record total <b>{2}</b>", l).format(daysonshelter, dailyboardcostdisplay, totaldisplay)
    
    def post_donationdefault(self, o):
        return extlookups.get_donation_default(o.dbo, o.post.integer("donationtype"))

    def post_insurance(self, o):
        return extmovement.generate_insurance_number(o.dbo)

class move_book_foster(JSONEndpoint):
    url = "move_book_foster"
    js_module = "movements"
    get_permissions = users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        movements = extmovement.get_movements(dbo, extmovement.FOSTER)
        al.debug("got %d movements" % len(movements), "code.move_book_foster", dbo)
        return {
            "name": "move_book_foster",
            "rows": movements,
            "movementtypes": extlookups.get_movement_types(dbo),
            "reservationstatuses": extlookups.get_reservation_statuses(dbo),
            "returncategories": extlookups.get_entryreasons(dbo),
            "templates": template.get_document_templates(dbo)
        }

class move_book_recent_adoption(JSONEndpoint):
    url = "move_book_recent_adoption"
    js_module = "movements"
    get_permissions = users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        movements = extmovement.get_recent_adoptions(dbo)
        al.debug("got %d movements" % len(movements), "code.move_book_recent_adoption", dbo)
        return {
            "name": "move_book_recent_adoption",
            "rows": movements,
            "movementtypes": extlookups.get_movement_types(dbo),
            "reservationstatuses": extlookups.get_reservation_statuses(dbo),
            "returncategories": extlookups.get_entryreasons(dbo),
            "templates": template.get_document_templates(dbo)
        }

class move_book_recent_other(JSONEndpoint):
    url = "move_book_recent_other"
    js_module = "movements"
    get_permissions = users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        movements = extmovement.get_recent_nonfosteradoption(dbo)
        al.debug("got %d movements" % len(movements), "code.move_book_recent_other", dbo)
        return {
            "name": "move_book_recent_other",
            "rows": movements,
            "movementtypes": extlookups.get_movement_types(dbo),
            "reservationstatuses": extlookups.get_reservation_statuses(dbo),
            "returncategories": extlookups.get_entryreasons(dbo),
            "templates": template.get_document_templates(dbo)
        }

class move_book_recent_transfer(JSONEndpoint):
    url = "move_book_recent_transfer"
    js_module = "movements"
    get_permissions = users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        movements = extmovement.get_recent_transfers(dbo)
        al.debug("got %d movements" % len(movements), "code.move_book_recent_transfer", dbo)
        return {
            "name": "move_book_recent_transfer",
            "rows": movements,
            "movementtypes": extlookups.get_movement_types(dbo),
            "reservationstatuses": extlookups.get_reservation_statuses(dbo),
            "returncategories": extlookups.get_entryreasons(dbo),
            "templates": template.get_document_templates(dbo)
        }

class move_book_reservation(JSONEndpoint):
    url = "move_book_reservation"
    js_module = "movements"
    get_permissions = users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        movements = extmovement.get_active_reservations(dbo)
        al.debug("got %d movements" % len(movements), "code.move_book_reservation", dbo)
        return {
            "name": "move_book_reservation",
            "rows": movements,
            "movementtypes": extlookups.get_movement_types(dbo),
            "reservationstatuses": extlookups.get_reservation_statuses(dbo),
            "returncategories": extlookups.get_entryreasons(dbo),
            "templates": template.get_document_templates(dbo)
        }

class move_book_retailer(JSONEndpoint):
    url = "move_book_retailer"
    js_module = "movements"
    get_permissions = users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        movements = extmovement.get_movements(dbo, extmovement.RETAILER)
        al.debug("got %d movements" % len(movements), "code.move_book_retailer", dbo)
        return {
            "name": "move_book_retailer",
            "rows": movements,
            "movementtypes": extlookups.get_movement_types(dbo),
            "reservationstatuses": extlookups.get_reservation_statuses(dbo),
            "returncategories": extlookups.get_entryreasons(dbo),
            "templates": template.get_document_templates(dbo)
        }

class move_book_trial_adoption(JSONEndpoint):
    url = "move_book_trial_adoption"
    js_module = "movements"
    get_permissions = users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        movements = extmovement.get_trial_adoptions(dbo)
        al.debug("got %d movements" % len(movements), "code.move_book_trial_adoption", dbo)
        return {
            "name": "move_book_trial_adoption",
            "rows": movements,
            "movementtypes": extlookups.get_movement_types(dbo),
            "reservationstatuses": extlookups.get_reservation_statuses(dbo),
            "returncategories": extlookups.get_entryreasons(dbo),
            "templates": template.get_document_templates(dbo)
        }

class move_book_unneutered(JSONEndpoint):
    url = "move_book_unneutered"
    js_module = "movements"
    get_permissions = users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        movements = extmovement.get_recent_unneutered_adoptions(dbo)
        al.debug("got %d movements" % len(movements), "code.move_book_unneutered", dbo)
        return {
            "name": "move_book_unneutered",
            "rows": movements,
            "movementtypes": extlookups.get_movement_types(dbo),
            "reservationstatuses": extlookups.get_reservation_statuses(dbo),
            "returncategories": extlookups.get_entryreasons(dbo),
            "templates": template.get_document_templates(dbo)
        }

class move_deceased(JSONEndpoint):
    url = "move_deceased"
    get_permissions = users.CHANGE_ANIMAL
    post_permissions = users.CHANGE_ANIMAL

    def controller(self, o):
        return {
            "deathreasons": extlookups.get_deathreasons(o.dbo)
        }

    def post_create(self, o):
        extanimal.update_deceased_from_form(o.dbo, o.user, o.post)

class move_foster(JSONEndpoint):
    url = "move_foster"
    get_permissions = users.ADD_MOVEMENT
    post_permissions = users.ADD_MOVEMENT

    def controller(self, o):
        return {}

    def post_create(self, o):
        return str(extmovement.insert_foster_from_form(o.dbo, o.user, o.post))

class move_gendoc(JSONEndpoint):
    url = "move_gendoc"
    get_permissions = users.GENERATE_DOCUMENTS

    def controller(self, o):
        return {
            "message": o.post["message"],
            "templates": html.template_selection(template.get_document_templates(o.dbo), "document_gen?linktype=%s&id=%s" % (o.post["linktype"], o.post["id"]))
        }

class move_reclaim(JSONEndpoint):
    url = "move_reclaim"
    get_permissions = users.ADD_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        return {
            "donationtypes": extlookups.get_donation_types(dbo),
            "accounts": financial.get_accounts(dbo),
            "paymenttypes": extlookups.get_payment_types(dbo)
        }

    def post_create(self, o):
        self.check(users.ADD_MOVEMENT)
        return str(extmovement.insert_reclaim_from_form(o.dbo, o.user, o.post))

    def post_cost(self, o):
        l = o.locale
        dbo = o.dbo
        post = o.post
        self.check(users.VIEW_COST)
        dailyboardcost = extanimal.get_daily_boarding_cost(dbo, post.integer("id"))
        dailyboardcostdisplay = format_currency(l, dailyboardcost)
        daysonshelter = extanimal.get_days_on_shelter(dbo, post.integer("id"))
        totaldisplay = format_currency(l, dailyboardcost * daysonshelter)
        return totaldisplay + "||" + _("On shelter for {0} days, daily cost {1}, cost record total <b>{2}</b>", l).format(daysonshelter, dailyboardcostdisplay, totaldisplay)

    def post_donationdefault(self, o):
        return extlookups.get_donation_default(o.dbo, o.post.integer("donationtype"))

class move_reserve(JSONEndpoint):
    url = "move_reserve"
    get_permissions = users.ADD_MOVEMENT
    post_permissions = users.ADD_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        return {
            "donationtypes": extlookups.get_donation_types(dbo),
            "accounts": financial.get_accounts(dbo),
            "paymenttypes": extlookups.get_payment_types(dbo),
            "reservationstatuses": extlookups.get_reservation_statuses(dbo)
        }

    def post_create(self, o):
        return str(extmovement.insert_reserve_from_form(o.dbo, o.user, o.post))

class move_retailer(JSONEndpoint):
    url = "move_retailer"
    get_permissions = users.ADD_MOVEMENT
    post_permissions = users.ADD_MOVEMENT

    def controller(self, o):
        return {}

    def post_create(self, o):
        return str(extmovement.insert_retailer_from_form(o.dbo, o.user, o.post))

class move_transfer(JSONEndpoint):
    url = "move_transfer"
    get_permissions = users.ADD_MOVEMENT
    post_permissions = users.ADD_MOVEMENT

    def controller(self, o):
        return {}

    def post_create(self, o):
        return str(extmovement.insert_transfer_from_form(o.dbo, o.user, o.post))

class movement(JSONEndpoint):
    url = "movement"

    def post_create(self, o):
        self.check(users.ADD_MOVEMENT)
        return extmovement.insert_movement_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.CHANGE_MOVEMENT)
        extmovement.update_movement_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_MOVEMENT)
        for mid in o.post.integer_list("ids"):
            extmovement.delete_movement(o.dbo, o.user, mid)

    def post_insurance(self, o):
        return extmovement.generate_insurance_number(o.dbo)

class onlineform_incoming(JSONEndpoint):
    url = "onlineform_incoming"
    get_permissions = users.VIEW_INCOMING_FORMS

    def controller(self, o):
        headers = extonlineform.get_onlineformincoming_headers(o.dbo)
        al.debug("got %d submitted headers" % len(headers), "code.onlineform_incoming", o.dbo)
        return {
            "rows": headers
        }

    def post_view(self, o):
        self.check(users.VIEW_INCOMING_FORMS)
        return extonlineform.get_onlineformincoming_html(o.dbo, o.post.integer("collationid"))

    def post_delete(self, o):
        self.check(users.DELETE_INCOMING_FORMS)
        for did in o.post.integer_list("ids"):
            extonlineform.delete_onlineformincoming(o.dbo, o.user, did)

    def post_attachanimal(self, o):
        dbo = o.dbo
        collationid = o.post.integer("collationid")
        animalid = o.post.integer("animalid")
        formname = extonlineform.get_onlineformincoming_name(dbo, collationid)
        formhtml = extonlineform.get_onlineformincoming_html_print(dbo, [collationid,] )
        extmedia.create_document_media(dbo, o.user, extmedia.ANIMAL, animalid, formname, formhtml )
        return animalid

    def post_attachperson(self, o):
        dbo = o.dbo
        collationid = o.post.integer("collationid")
        personid = o.post.integer("personid")
        formname = extonlineform.get_onlineformincoming_name(dbo, collationid)
        formhtml = extonlineform.get_onlineformincoming_html_print(dbo, [collationid,] )
        extmedia.create_document_media(dbo, session.user, extmedia.PERSON, personid, formname, formhtml )
        return personid 

    def post_animal(self, o):
        self.check(users.ADD_MEDIA)
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, animalid, animalname = extonlineform.attach_animal(o.dbo, o.user, pid)
            rv.append("%d|%d|%s" % (collationid, animalid, animalname))
        return "^$".join(rv)

    def post_person(self, o):
        self.check(users.ADD_PERSON)
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, personid, personname = extonlineform.create_person(o.dbo, o.user, pid)
            rv.append("%d|%d|%s" % (collationid, personid, personname))
        return "^$".join(rv)

    def post_lostanimal(self, o):
        self.check(users.ADD_LOST_ANIMAL)
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, lostanimalid, personname = extonlineform.create_lostanimal(o.dbo, o.user, pid)
            rv.append("%d|%d|%s" % (collationid, lostanimalid, personname))
        return "^$".join(rv)

    def post_foundanimal(self, o):
        self.check(users.ADD_FOUND_ANIMAL)
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, foundanimalid, personname = extonlineform.create_foundanimal(o.dbo, o.user, pid)
            rv.append("%d|%d|%s" % (collationid, foundanimalid, personname))
        return "^$".join(rv)

    def post_incident(self, o):
        self.check(users.ADD_INCIDENT)
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, incidentid, personname = extonlineform.create_animalcontrol(o.dbo, o.user, pid)
            rv.append("%d|%d|%s" % (collationid, incidentid, personname))
        return "^$".join(rv)

    def post_transport(self, o):
        self.check(users.ADD_TRANSPORT)
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, animalid, animalname = extonlineform.create_transport(o.dbo, o.user, pid)
            rv.append("%d|%d|%s" % (collationid, animalid, animalname))
        return "^$".join(rv)

    def post_waitinglist(self, o):
        self.check(users.ADD_WAITING_LIST)
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, wlid, personname = extonlineform.create_waitinglist(o.dbo, o.user, pid)
            rv.append("%d|%d|%s" % (collationid, wlid, personname))
        return "^$".join(rv)

class onlineform_incoming_print(ASMEndpoint):
    url = "onlineform_incoming_print"
    get_permissions = users.VIEW_INCOMING_FORMS

    def content(self, o):
        self.content_type("text/html")
        self.cache_control(0)
        return extonlineform.get_onlineformincoming_html_print(o.dbo, o.post.integer_list("ids"))

class onlineform(JSONEndpoint):
    url = "onlineform"
    get_permissions = users.EDIT_ONLINE_FORMS
    post_permissions = users.EDIT_ONLINE_FORMS

    def controller(self, o):
        l = o.locale
        dbo = o.dbo
        formid = o.post.integer("formid")
        formname = extonlineform.get_onlineform_name(dbo, formid)
        fields = extonlineform.get_onlineformfields(dbo, formid)
        # Escape any angle brackets in raw markup output. This is needed
        # to target tooltip as a textarea
        for r in fields:
            if r["FIELDTYPE"] == extonlineform.FIELDTYPE_RAWMARKUP:
                r["TOOLTIP"] = html.escape_angle(r["TOOLTIP"]) 
        title = _("Online Form: {0}", l).format(formname)
        al.debug("got %d online form fields" % len(fields), "code.onlineform", dbo)
        return {
            "rows": fields,
            "formid": formid,
            "formname": formname,
            "formfields": extonlineform.FORM_FIELDS,
            "title": title
        }

    def post_create(self, o):
        return extonlineform.insert_onlineformfield_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        extonlineform.update_onlineformfield_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        for did in o.post.integer_list("ids"):
            extonlineform.delete_onlineformfield(o.dbo, o.user, did)

class onlineforms(JSONEndpoint):
    url = "onlineforms"
    get_permissions = users.EDIT_ONLINE_FORMS
    post_permissions = users.EDIT_ONLINE_FORMS

    def controller(self, o):
        dbo = o.dbo
        onlineforms = extonlineform.get_onlineforms(dbo)
        al.debug("got %d online forms" % len(onlineforms), "code.onlineforms", dbo)
        return {
            "rows": onlineforms,
            "flags": extlookups.get_person_flags(dbo),
            "header": extonlineform.get_onlineform_header(dbo),
            "footer": extonlineform.get_onlineform_footer(dbo)
        }

    def post_create(self, o):
        return extonlineform.insert_onlineform_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        extonlineform.update_onlineform_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        for did in o.post.integer_list("ids"):
            extonlineform.delete_onlineform(o.dbo, o.user, did)

    def post_clone(self, o):
        for did in o.post.integer_list("ids"):
            extonlineform.clone_onlineform(o.dbo, o.user, did)

    def post_headfoot(self, o):
        extonlineform.set_onlineform_headerfooter(o.dbo, o.post["header"], o.post["footer"])

    def post_import(self, o):
        fd = o.post.filedata()
        if fd.startswith("{"):
            extonlineform.import_onlineform_json(o.dbo, o.post.filedata())
        else:
            extonlineform.import_onlineform_html(o.dbo, o.post.filedata())
        self.redirect("onlineforms")

class onlineform_json(ASMEndpoint):
    url = "onlineform_json"
    get_permissions = users.EDIT_ONLINE_FORMS

    def content(self, o):
        self.content_type("application/json")
        return extonlineform.get_onlineform_json(o.dbo, o.post.integer("formid"))

class options(JSONEndpoint):
    url = "options"
    get_permissions = users.SYSTEM_OPTIONS
    post_permissions = users.SYSTEM_OPTIONS

    def controller(self, o):
        dbo = o.dbo
        c = {
            "accounts": financial.get_accounts(dbo),
            "animalfindcolumns": html.json_animalfindcolumns(dbo),
            "breeds": extlookups.get_breeds(dbo),
            "coattypes": extlookups.get_coattypes(dbo),
            "colours": extlookups.get_basecolours(dbo),
            "costtypes": extlookups.get_costtypes(dbo),
            "deathreasons": extlookups.get_deathreasons(dbo),
            "donationtypes": extlookups.get_donation_types(dbo),
            "entryreasons": extlookups.get_entryreasons(dbo),
            "incidenttypes": extlookups.get_incident_types(dbo),
            "locales": get_locales(),
            "locations": extlookups.get_internal_locations(dbo),
            "logtypes": extlookups.get_log_types(dbo),
            "paymenttypes": extlookups.get_payment_types(dbo),
            "personfindcolumns": html.json_personfindcolumns(dbo),
            "quicklinks": html.json_quicklinks(dbo),
            "reservationstatuses": extlookups.get_reservation_statuses(dbo),
            "sizes": extlookups.get_sizes(dbo),
            "species": extlookups.get_species(dbo),
            "themes": extlookups.VISUAL_THEMES,
            "testtypes": extlookups.get_test_types(dbo),
            "types": extlookups.get_animal_types(dbo),
            "urgencies": extlookups.get_urgencies(dbo),
            "usersandroles": users.get_users_and_roles(dbo),
            "vaccinationtypes": extlookups.get_vaccination_types(dbo),
            "waitinglistcolumns": html.json_waitinglistcolumns(dbo)
        }
        al.debug("lookups loaded", "code.options", dbo)
        return c

    def post_save(self, o):
        configuration.csave(o.dbo, o.user, o.post)
        self.reload_config()

class person(JSONEndpoint):
    url = "person"
    get_permissions = users.VIEW_PERSON

    def controller(self, o):
        dbo = o.dbo
        p = extperson.get_person(dbo, o.post.integer("id"))
        if p is None: 
            self.notfound()
        if p["ISSTAFF"] == 1:
            self.check(users.VIEW_STAFF)
        if p["ISVOLUNTEER"] == 1:
            self.check(users.VIEW_VOLUNTEER)
        if o.siteid != 0 and p["SITEID"] != 0 and o.siteid != p["SITEID"]:
            raise utils.ASMPermissionError("person not in user site")
        upid = users.get_personid(dbo, o.user)
        if upid != 0 and upid == p.id:
            raise utils.ASMPermissionError("cannot view user staff record")
        al.debug("opened person '%s'" % p["OWNERNAME"], "code.person", dbo)
        return {
            "additional": extadditional.get_additional_fields(dbo, p.id, "person"),
            "animaltypes": extlookups.get_animal_types(dbo),
            "audit": self.checkb(users.VIEW_AUDIT_TRAIL) and audit.get_audit_for_link(dbo, "owner", p.id) or [],
            "species": extlookups.get_species(dbo),
            "breeds": extlookups.get_breeds_by_species(dbo),
            "colours": extlookups.get_basecolours(dbo),
            "diarytasks": extdiary.get_person_tasks(dbo),
            "flags": extlookups.get_person_flags(dbo),
            "ynun": extlookups.get_ynun(dbo),
            "homecheckhistory": extperson.get_homechecked(dbo, p.id),
            "jurisdictions": extlookups.get_jurisdictions(dbo),
            "logtypes": extlookups.get_log_types(dbo),
            "sexes": extlookups.get_sexes(dbo),
            "sites": extlookups.get_sites(dbo),
            "sizes": extlookups.get_sizes(dbo),
            "towns": "|".join(extperson.get_towns(dbo)),
            "counties": "|".join(extperson.get_counties(dbo)),
            "towncounties": "|".join(extperson.get_town_to_county(dbo)),
            "tabcounts": extperson.get_satellite_counts(dbo, p.id)[0],
            "templates": template.get_document_templates(dbo),
            "person": p
        }

    def post_save(self, o):
        self.check(users.CHANGE_PERSON)
        extperson.update_person_from_form(o.dbo, o.post, o.user)

    def post_delete(self, o):
        self.check(users.DELETE_PERSON)
        extperson.delete_person(o.dbo, o.user, o.post.integer("personid"))

    def post_email(self, o):
        self.check(users.EMAIL_PERSON)
        l = o.locale
        if not extperson.send_email_from_form(o.dbo, o.user, o.post):
            raise utils.ASMError(_("Failed sending email", l))

    def post_latlong(self, o):
        self.check(users.CHANGE_PERSON)
        extperson.update_latlong(o.dbo, o.post.integer("personid"), o.post["latlong"])

    def post_merge(self, o):
        self.check(users.MERGE_PERSON)
        extperson.merge_person(o.dbo, o.user, o.post.integer("personid"), o.post.integer("mergepersonid"))

class person_citations(JSONEndpoint):
    url = "person_citations"
    js_module = "citations"
    get_permissions = users.VIEW_CITATION

    def controller(self, o):
        dbo = o.dbo
        p = extperson.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        citations = financial.get_person_citations(dbo, o.post.integer("id"))
        al.debug("got %d citations" % len(citations), "code.incident_citations", dbo)
        return {
            "name": "person_citations",
            "rows": citations,
            "person": p,
            "tabcounts": extperson.get_satellite_counts(dbo, p["ID"])[0],
            "citationtypes": extlookups.get_citation_types(dbo)
        }

class person_clinic(JSONEndpoint):
    url = "person_clinic"
    js_module = "clinic_appointment"
    get_permissions = users.VIEW_CLINIC

    def controller(self, o):
        dbo = o.dbo
        personid = o.post.integer("id")
        p = extperson.get_person(dbo, personid)
        if p is None: self.notfound()
        rows = clinic.get_person_appointments(dbo, personid)
        al.debug("got %d appointments for person %s" % (len(rows), p.OWNERNAME), "code.person_clinic", dbo)
        return {
            "name": self.url,
            "person": p,
            "tabcounts": extperson.get_satellite_counts(dbo, personid)[0],
            "clinicstatuses": extlookups.get_clinic_statuses(dbo),
            "donationtypes": extlookups.get_donation_types(dbo),
            "paymenttypes": extlookups.get_payment_types(dbo),
            "forlist": users.get_users(dbo),
            "templates": template.get_document_templates(dbo),
            "rows": rows
        }

class person_diary(JSONEndpoint):
    url = "person_diary"
    js_module = "diary"
    get_permissions = users.VIEW_DIARY

    def controller(self, o):
        dbo = o.dbo
        p = extperson.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        diaries = extdiary.get_diaries(dbo, extdiary.PERSON, o.post.integer("id"))
        al.debug("got %d diaries" % len(diaries), "code.person_diary", dbo)
        return {
            "rows": diaries,
            "person": p,
            "tabcounts": extperson.get_satellite_counts(dbo, p["ID"])[0],
            "name": "person_diary",
            "linkid": p["ID"],
            "linktypeid": extdiary.PERSON,
            "forlist": users.get_users_and_roles(dbo)
        }

class person_donations(JSONEndpoint):
    url = "person_donations"
    js_module = "donations"
    get_permissions = users.VIEW_DONATION

    def controller(self, o):
        dbo = o.dbo
        p = extperson.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        donations = financial.get_person_donations(dbo, o.post.integer("id"))
        return {
            "person": p,
            "tabcounts": extperson.get_satellite_counts(dbo, p["ID"])[0],
            "name": "person_donations",
            "donationtypes": extlookups.get_donation_types(dbo),
            "accounts": financial.get_accounts(dbo),
            "paymenttypes": extlookups.get_payment_types(dbo),
            "frequencies": extlookups.get_donation_frequencies(dbo),
            "templates": template.get_document_templates(dbo),
            "rows": donations
        }

class person_embed(ASMEndpoint):
    url = "person_embed"
    check_logged_in = False

    def content(self, o):
        if not session.dbo: raise utils.ASMPermissionError("No session")
        dbo = session.dbo
        self.content_type("application/json")
        self.cache_control(180) # Person data can be cached for a few minutes, useful for multiple widgets on one page
        return utils.json({
            "additional": extadditional.get_additional_fields(dbo, 0, "person"),
            "jurisdictions": extlookups.get_jurisdictions(dbo),
            "towns": "|".join(extperson.get_towns(dbo)),
            "counties": "|".join(extperson.get_counties(dbo)),
            "towncounties": "|".join(extperson.get_town_to_county(dbo)),
            "flags": extlookups.get_person_flags(dbo),
            "sites": extlookups.get_sites(dbo)
        })

    def post_find(self, o):
        self.check(users.VIEW_PERSON)
        self.content_type("application/json")
        q = o.post["q"]
        rows = extperson.get_person_find_simple(o.dbo, q, o.user, o.post["filter"], \
            self.checkb(users.VIEW_STAFF), \
            self.checkb(users.VIEW_VOLUNTEER), 100)
        al.debug("find '%s' got %d rows" % (self.query(), len(rows)), "code.person_embed", o.dbo)
        return utils.json(rows)

    def post_id(self, o):
        self.check(users.VIEW_PERSON)
        self.content_type("application/json")
        self.cache_control(120)
        dbo = o.dbo
        pid = o.post.integer("id")
        p = extperson.get_person_embedded(dbo, pid)
        if not p:
            al.error("get person by id %d found no records." % pid, "code.person_embed", dbo)
            raise web.notfound()
        else:
            return utils.json((p,))

    def post_similar(self, o):
        self.check(users.VIEW_PERSON)
        self.content_type("application/json")
        dbo = o.dbo
        post = o.post
        surname = post["surname"]
        forenames = post["forenames"]
        address = post["address"]
        email = post["emailaddress"]
        p = extperson.get_person_similar(dbo, email, surname, forenames, address)
        if len(p) == 0:
            al.debug("No similar people found for %s, %s, %s" % (surname, forenames, address), "code.person_embed", dbo)
        else:
            al.debug("found similar people for %s, %s, %s: got %d records" % (surname, forenames, address, len(p)), "code.person_embed", dbo)
        return utils.json(p)

    def post_add(self, o):
        self.check(users.ADD_PERSON)
        self.content_type("application/json")
        dbo = o.dbo
        al.debug("add new person", "code.person_embed", dbo)
        pid = extperson.insert_person_from_form(dbo, o.post, session.user)
        p = extperson.get_person(dbo, pid)
        return utils.json((p,))

class person_find(JSONEndpoint):
    url = "person_find"
    get_permissions = users.VIEW_PERSON

    def controller(self, o):
        dbo = o.dbo
        flags = extlookups.get_person_flags(dbo)
        al.debug("lookups loaded", "code.person_find", dbo)
        return {
            "flags": flags,
            "jurisdictions": extlookups.get_jurisdictions(dbo),
            "users": users.get_users(dbo)
        }

class person_find_results(JSONEndpoint):
    url = "person_find_results"
    get_permissions = users.VIEW_PERSON

    def controller(self, o):
        dbo = o.dbo
        mode = o.post["mode"]
        q = o.post["q"]
        if mode == "SIMPLE":
            results = extperson.get_person_find_simple(dbo, q, o.user, "all", \
                self.checkb(users.VIEW_STAFF), \
                self.checkb(users.VIEW_VOLUNTEER), \
                configuration.record_search_limit(dbo))
        else:
            results = extperson.get_person_find_advanced(dbo, o.post.data, o.user, self.checkb(users.VIEW_STAFF), configuration.record_search_limit(dbo))
        add = None
        if len(results) > 0: 
            add = extadditional.get_additional_fields_ids(dbo, results, "person")
        al.debug("found %d results for %s" % (len(results), self.query()), "code.person_find_results", dbo)
        return {
            "rows": results,
            "additional": add
        }

class person_investigation(JSONEndpoint):
    url = "person_investigation"
    get_permissions = users.VIEW_INVESTIGATION

    def controller(self, o):
        dbo = o.dbo
        p = extperson.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        investigation = extperson.get_investigation(dbo, o.post.integer("id"))
        al.debug("got %d investigation records for person %s" % (len(investigation), p["OWNERNAME"]), "code.person_investigation", dbo)
        return {
            "rows": investigation,
            "person": p,
            "tabcounts": extperson.get_satellite_counts(dbo, p["ID"])[0]
        }

    def post_create(self, o):
        self.check(users.ADD_INVESTIGATION)
        return str(extperson.insert_investigation_from_form(o.dbo, o.user, o.post))

    def post_update(self, o):
        self.check(users.CHANGE_INVESTIGATION)
        extperson.update_investigation_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_INVESTIGATION)
        for did in o.post.integer_list("ids"):
            extperson.delete_investigation(o.dbo, o.user, did)

class person_licence(JSONEndpoint):
    url = "person_licence"
    js_module = "licence"
    get_permissions = users.VIEW_LICENCE

    def controller(self, o):
        dbo = o.dbo
        p = extperson.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        licences = financial.get_person_licences(dbo, o.post.integer("id"))
        al.debug("got %d licences" % len(licences), "code.person_licence", dbo)
        return {
            "name": "person_licence",
            "rows": licences,
            "person": p,
            "templates": template.get_document_templates(dbo),
            "tabcounts": extperson.get_satellite_counts(dbo, p["ID"])[0],
            "licencetypes": extlookups.get_licence_types(dbo)
        }

class person_log(JSONEndpoint):
    url = "person_log"
    js_module = "log"
    get_permissions = users.VIEW_LOG

    def controller(self, o):
        dbo = o.dbo
        logfilter = o.post.integer("filter")
        if logfilter == 0: logfilter = configuration.default_log_filter(dbo)
        p = extperson.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        logs = extlog.get_logs(dbo, extlog.PERSON, o.post.integer("id"), logfilter)
        return {
            "name": "person_log",
            "linkid": o.post.integer("id"),
            "linktypeid": extlog.PERSON,
            "filter": logfilter,
            "rows": logs,
            "person": p,
            "tabcounts": extperson.get_satellite_counts(dbo, p["ID"])[0],
            "logtypes": extlookups.get_log_types(dbo)
        }

class person_lookingfor(ASMEndpoint):
    url = "person_lookingfor"
    get_permissions = users.VIEW_PERSON

    def content(self, o):
        self.content_type("text/html")
        if o.post.integer("personid") == 0:
            return configuration.lookingfor_report(o.dbo)
        else:
            return extperson.lookingfor_report(o.dbo, o.user, o.post.integer("personid"))

class person_links(JSONEndpoint):
    url = "person_links"
    get_permissions = users.VIEW_PERSON_LINKS

    def controller(self, o):
        dbo = o.dbo
        links = extperson.get_links(dbo, o.post.integer("id"))
        p = extperson.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        al.debug("got %d person links" % len(links), "code.person_links", dbo)
        return {
            "links": links,
            "person": p,
            "tabcounts": extperson.get_satellite_counts(dbo, p["ID"])[0]
        }

class person_media(JSONEndpoint):
    url = "person_media"
    js_module = "media"
    get_permissions = users.VIEW_MEDIA

    def controller(self, o):
        dbo = o.dbo
        p = extperson.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        m = extmedia.get_media(dbo, extmedia.PERSON, o.post.integer("id"))
        al.debug("got %d media" % len(m), "code.person_media", dbo)
        return {
            "media": m,
            "person": p,
            "tabcounts": extperson.get_satellite_counts(dbo, p["ID"])[0],
            "showpreferred": True,
            "linkid": o.post.integer("id"),
            "linktypeid": extmedia.PERSON,
            "logtypes": extlookups.get_log_types(dbo),
            "name": self.url,
            "sigtype": ELECTRONIC_SIGNATURES
        }

class person_movements(JSONEndpoint):
    url = "person_movements"
    js_module = "movements"
    get_permissions = users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        p = extperson.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        movements = extmovement.get_person_movements(dbo, o.post.integer("id"))
        al.debug("got %d movements" % len(movements), "code.person_movements", dbo)
        return {
            "name": "person_movements",
            "rows": movements,
            "person": p,
            "tabcounts": extperson.get_satellite_counts(dbo, p["ID"])[0],
            "movementtypes": extlookups.get_movement_types(dbo),
            "reservationstatuses": extlookups.get_reservation_statuses(dbo),
            "returncategories": extlookups.get_entryreasons(dbo),
            "templates": template.get_document_templates(dbo)
        }

class person_new(JSONEndpoint):
    url = "person_new"
    get_permissions = users.ADD_PERSON
    post_permissions = users.ADD_PERSON

    def controller(self, o):
        dbo = o.dbo
        al.debug("add person", "code.person_new", dbo)
        return {
            "towns": "|".join(extperson.get_towns(dbo)),
            "counties": "|".join(extperson.get_counties(dbo)),
            "towncounties": "|".join(extperson.get_town_to_county(dbo)),
            "additional": extadditional.get_additional_fields(dbo, 0, "person"),
            "jurisdictions": extlookups.get_jurisdictions(dbo),
            "flags": extlookups.get_person_flags(dbo),
            "sites": extlookups.get_sites(dbo)
        }

    def post_all(self, o):
        return str(extperson.insert_person_from_form(o.dbo, o.post, o.user))

class person_rota(JSONEndpoint):
    url = "person_rota"
    js_module = "rota"
    get_permissions = users.VIEW_ROTA

    def controller(self, o):
        dbo = o.dbo
        p = extperson.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        rota = extperson.get_person_rota(dbo, o.post.integer("id"))
        al.debug("got %d rota items" % len(rota), "code.person_rota", dbo)
        return {
            "name": "person_rota",
            "rows": rota,
            "person": p,
            "rotatypes": extlookups.get_rota_types(dbo),
            "worktypes": extlookups.get_work_types(dbo),
            "tabcounts": extperson.get_satellite_counts(dbo, p["ID"])[0]
        }

    def post_create(self, o):
        self.check(users.ADD_ROTA)
        return extperson.insert_rota_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.CHANGE_ROTA)
        extperson.update_rota_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_ROTA)
        for rid in o.post.integer_list("ids"):
            extperson.delete_rota(o.dbo, o.user, rid)

class person_traploan(JSONEndpoint):
    url = "person_traploan"
    js_module = "traploan"
    get_permissions = users.VIEW_TRAPLOAN

    def controller(self, o):
        dbo = o.dbo
        p = extperson.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        traploans = extanimalcontrol.get_person_traploans(dbo, o.post.integer("id"))
        al.debug("got %d trap loans" % len(traploans), "code.person_traploan", dbo)
        return {
            "name": "person_traploan",
            "rows": traploans,
            "person": p,
            "tabcounts": extperson.get_satellite_counts(dbo, p["ID"])[0],
            "traptypes": extlookups.get_trap_types(dbo)
        }

class person_vouchers(JSONEndpoint):
    url = "person_vouchers"
    get_permissions = users.VIEW_VOUCHER

    def controller(self, o):
        dbo = o.dbo
        p = extperson.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        vouchers = financial.get_vouchers(dbo, o.post.integer("id"))
        al.debug("got %d vouchers" % len(vouchers), "code.person_vouchers", dbo)
        return {
            "vouchertypes": extlookups.get_voucher_types(dbo),
            "rows": vouchers,
            "person": p,
            "tabcounts": extperson.get_satellite_counts(dbo, p["ID"])[0]
        }

    def post_create(self, o):
        self.check(users.ADD_VOUCHER)
        return financial.insert_voucher_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.CHANGE_VOUCHER)
        financial.update_voucher_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_VOUCHER)
        for vid in o.post.integer_list("ids"):
            financial.delete_voucher(o.dbo, o.user, vid)

class publish(JSONEndpoint):
    url = "publish"
    get_permissions = users.USE_INTERNET_PUBLISHER

    def controller(self, o):
        dbo = o.dbo
        mode = o.post["mode"]
        failed = False
        al.debug("publish started for mode %s" % mode, "code.publish", dbo)
        # If a publisher is already running and we have a mode, mark
        # a failure starting
        if async.is_task_running(dbo):
            al.debug("publish already running, not starting new publish", "code.publish", dbo)
        else:
            # If a publishing mode is requested, start that publisher
            # running on a background thread
            extpublish.start_publisher(dbo, mode, user=o.user, async=True)
        return { "failed": failed }

    def post_poll(self, o):
        return "%s|%d|%s" % (async.get_task_name(o.dbo), async.get_progress_percent(o.dbo), async.get_last_error(o.dbo))

    def post_stop(self, o):
        async.set_cancel(o.dbo, True)

class publish_logs(JSONEndpoint):
    url = "publish_logs"
    get_permissions = users.USE_INTERNET_PUBLISHER

    def controller(self, o):
        logs = extpublish.get_publish_logs(o.dbo)
        al.debug("viewing %d publishing logs" % len(logs), "code.publish_logs", o.dbo)
        return {
            "rows": logs
        }

class publish_log_view(ASMEndpoint):
    url = "publish_log_view"
    get_permissions = users.USE_INTERNET_PUBLISHER

    def content(self, o):
        al.debug("viewing log file %s" % o.post["view"], "code.publish_logs", o.dbo)
        self.cache_control(CACHE_ONE_WEEK) # log files never change
        self.content_type("text/plain")
        self.header("Content-Disposition", "inline; filename=\"%s\"" % o.post["view"])
        return extpublish.get_publish_log(o.dbo, o.post.integer("view"))

class publish_options(JSONEndpoint):
    url = "publish_options"
    get_permissions = users.PUBLISH_OPTIONS
    post_permissions = users.PUBLISH_OPTIONS

    def controller(self, o):
        dbo = o.dbo
        c = {
            "locations": extlookups.get_internal_locations(dbo),
            "publishurl": MULTIPLE_DATABASES_PUBLISH_URL,
            "flags": extlookups.get_animal_flags(dbo),
            "hasftpoverride": MULTIPLE_DATABASES_PUBLISH_FTP is not None and not configuration.publisher_ignore_ftp_override(dbo),
            "hasfoundanimals": FOUNDANIMALS_FTP_USER != "",
            "hasmaddiesfund": MADDIES_FUND_TOKEN_URL != "",
            "haspetlink": PETLINK_BASE_URL != "",
            "haspetslocated": PETSLOCATED_FTP_USER != "",
            "hassmarttag": SMARTTAG_FTP_USER != "",
            "hasvevendor": VETENVOY_US_VENDOR_PASSWORD != "",
            "hasvesys": VETENVOY_US_VENDOR_USERID != "",
            "haspetrescue": PETRESCUE_FTP_HOST != "",
            "logtypes": extlookups.get_log_types(dbo),
            "styles": template.get_html_template_names(dbo),
            "users": users.get_users(dbo)
        }
        al.debug("loaded lookups", "code.publish_options", dbo)
        return c

    def post_save(self, o):
        configuration.csave(o.dbo, o.user, o.post)
        self.reload_config()

    def post_vesignup(self, o):
        userid, userpwd = publishers.vetenvoy.VetEnvoyUSMicrochipPublisher.signup(o.dbo, o.post)
        return "%s,%s" % (userid, userpwd)

class report(ASMEndpoint):
    url = "report"
    get_permissions = users.VIEW_REPORT

    def content(self, o):
        dbo = o.dbo
        post = o.post
        crid = post.integer("id")
        # Make sure this user has a role that can view the report
        extreports.check_view_permission(o.session, crid)
        crit = extreports.get_criteria_controls(dbo, crid, locationfilter = o.locationfilter, siteid = o.siteid) 
        self.content_type("text/html")
        self.cache_control(0)
        # If this report takes criteria and none were supplied, go to the criteria screen instead to get them
        if crit != "" and post["hascriteria"] == "": self.redirect("report_criteria?id=%d&target=report" % post.integer("id"))
        al.debug("got criteria (%s), executing report %d" % (str(post.data), crid), "code.report", dbo)
        p = extreports.get_criteria_params(dbo, crid, post)
        return extreports.execute(dbo, crid, o.user, p)

class report_criteria(JSONEndpoint):
    url = "report_criteria"
    get_permissions = users.VIEW_REPORT

    def controller(self, o):
        dbo = o.dbo
        post = o.post
        title = extreports.get_title(o.dbo, o.post.integer("id"))
        al.debug("building report criteria form for report %d %s" % (post.integer("id"), title), "code.report_criteria", dbo)
        return {
            "id": post.integer("id"),
            "title": title,
            "target": post["target"],
            "criteriahtml": extreports.get_criteria_controls(o.dbo, o.post.integer("id"), locationfilter = o.locationfilter, siteid = o.siteid)
        }

class report_export(JSONEndpoint):
    url = "report_export"
    get_permissions = users.EXPORT_REPORT

    def controller(self, o):
        dbo = o.dbo
        reports = extreports.get_available_reports(dbo)
        al.debug("exporting %d reports" % len(reports), "code.report_export", dbo)
        return {
            "rows": reports
        }

class report_export_csv(ASMEndpoint):
    url = "report_export_csv"
    get_permissions = users.EXPORT_REPORT

    def content(self, o):
        dbo = o.dbo
        post = o.post
        crid = post.integer("id")
        crit = extreports.get_criteria_controls(dbo, crid, locationfilter = o.locationfilter, siteid = o.siteid) 
        # If this report takes criteria and none were supplied, go to the criteria screen instead to get them
        if crit != "" and post["hascriteria"] == "": self.redirect("report_criteria?id=%d&target=report_export_csv" % crid)
        # Make sure this user has a role that can view the report
        extreports.check_view_permission(session, crid)
        title = extreports.get_title(dbo, crid)
        filename = title.replace(" ", "_").replace("\"", "").replace("'", "").lower()
        p = extreports.get_criteria_params(dbo, crid, post)
        rows, cols = extreports.execute_query(dbo, crid, session.user, p)
        self.content_type("text/csv")
        self.header("Content-Disposition", u"attachment; filename=\"" + utils.decode_html(filename) + u".csv\"")
        return utils.csv(o.locale, rows, cols, True)

class report_images(JSONEndpoint):
    url = "report_images"
    
    def controller(self, o):
        images = dbfs.get_report_images(o.dbo)
        al.debug("got %d extra images" % len(images), "code.report_images", o.dbo)
        return { "rows": images }

    def post_all(self, o):
        dbfs.upload_report_image(o.dbo, o.post.data.filechooser)
        self.reload_config()
        self.redirect("report_images")

    def post_delete(self, o):
        for i in o.post["ids"].split(","):
            if i != "": dbfs.delete_filepath(o.dbo, "/reports/" + i)
        self.reload_config()

    def post_rename(self, o):
        dbfs.rename_file(o.dbo, "/reports", o.post["oldname"], o.post["newname"])

class reports(JSONEndpoint):
    url = "reports"
    get_permissions = users.VIEW_REPORT

    def controller(self, o):
        dbo = o.dbo
        reports = extreports.get_reports(dbo)
        header = extreports.get_raw_report_header(dbo)
        footer = extreports.get_raw_report_footer(dbo)
        al.debug("editing %d reports" % len(reports), "code.reports", dbo)
        return {
            "categories": "|".join(extreports.get_categories(dbo)),
            "header": header,
            "footer": footer,
            "roles": users.get_roles(dbo),
            "rows": reports
        }

    def post_create(self, o):
        self.check(users.ADD_REPORT)
        rid = extreports.insert_report_from_form(o.dbo, o.user, o.post)
        self.reload_config()
        return rid

    def post_update(self, o):
        self.check(users.CHANGE_REPORT)
        extreports.update_report_from_form(o.dbo, o.user, o.post)
        self.reload_config()

    def post_delete(self, o):
        self.check(users.DELETE_REPORT)
        for rid in o.post.integer_list("ids"):
            extreports.delete_report(o.dbo, o.user, rid)
        self.reload_config()

    def post_sql(self, o):
        self.check(users.USE_SQL_INTERFACE)
        extreports.check_sql(o.dbo, o.user, o.post["sql"])

    def post_genhtml(self, o):
        self.check(users.USE_SQL_INTERFACE)
        return extreports.generate_html(o.dbo, o.user, o.post["sql"])

    def post_headfoot(self, o):
        self.check(users.CHANGE_REPORT)
        extreports.set_raw_report_headerfooter(o.dbo, o.post["header"], o.post["footer"])

    def post_smcomlist(self, o):
        return utils.json(extreports.get_smcom_reports(o.dbo))

    def post_smcominstall(self, o):
        self.check(users.ADD_REPORT)
        extreports.install_smcom_reports(o.dbo, o.user, o.post.integer_list("ids"))
        self.reload_config()

class roles(JSONEndpoint):
    url = "roles"
    get_permissions = users.EDIT_USER
    post_permissions = users.EDIT_USER

    def controller(self, o):
        roles = users.get_roles(o.dbo)
        al.debug("editing %d roles" % len(roles), "code.roles", o.dbo)
        return { "rows": roles }

    def post_create(self, o):
        users.insert_role_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        users.update_role_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        for rid in o.post.integer_list("ids"):
            users.delete_role(o.dbo, o.user, rid)

class schemajs(ASMEndpoint):
    url = "schema.js"
    check_logged_in = False

    def content(self, o):
        # Return schema of all database tables, includes k=build param to invalidate cache
        if utils.is_loggedin(o.session) and o.dbo is not None:
            dbo = o.dbo
            self.content_type("text/javascript")
            self.cache_control(CACHE_ONE_YEAR)
            CACHE_KEY = "schema"
            tobj = cachemem.get(CACHE_KEY)
            if tobj is None:
                tobj = {}
                for t in dbupdate.TABLES:
                    try:
                        rows = db.query(dbo, "SELECT * FROM %s" % t, limit=1)
                        if len(rows) != 0:
                            row = rows[0]
                            for k in row.copy():
                                row[k] = ""
                            tobj[t] = row
                    except Exception as err:
                        al.error("%s" % str(err), "code.schemajs", dbo)
                # Derive the extra *NAME fields from *ID in view tables.
                # We do this instead of reading a row from the view. 
                # This is because MySQL view performance can be absolutely 
                # horrible on large tables as it implements views
                # by creating a temporary table (which has none of the indexes).
                for t in dbupdate.VIEWS:
                    realtable = t.replace("v_", "")
                    try:
                        if realtable in tobj:
                            row = tobj[realtable]
                            for k in row.copy().iterkeys():
                                if k.endswith("ID") and k != "ID":
                                    row[k.replace("ID", "NAME")] = ""
                            tobj[t] = row
                    except Exception as err:
                        al.error("%s" % str(err), "code.schemajs", dbo)
                cachemem.put(CACHE_KEY, tobj, 86400)
            return "schema = %s;" % utils.json(tobj)
        else:
            # Not logged in
            self.content_type("text/javascript")
            self.cache_control(0)
            return ""

class search(JSONEndpoint):
    url = "search"
    
    def controller(self, o):
        q = o.post["q"]
        results, timetaken, explain, sortname = extsearch.search(o.dbo, o.session, q)
        is_large_db = ""
        if o.dbo.is_large_db: is_large_db = " (indexed only)"
        al.debug("searched for '%s', got %d results in %s, sorted %s %s" % (q, len(results), timetaken, sortname, is_large_db), "code.search", o.dbo)
        return {
            "q": q,
            "results": results,
            "timetaken": str(round(timetaken, 2)),
            "explain": explain,
            "sortname": sortname
        }

class service(ASMEndpoint):
    url = "service"
    check_logged_in = False

    def handle(self, o):
        contenttype, client_ttl, cache_ttl, response = extservice.handler(o.post, PATH, self.remote_ip(), self.referer(), self.query())
        if contenttype == "redirect":
            self.redirect(response)
        else:
            self.content_type(contenttype)
            self.cache_control(client_ttl, cache_ttl) 
            self.header("Access-Control-Allow-Origin", "*") # CORS
            return response

    def content(self, o):
        return self.handle(o)

    def post_all(self, o):
        return self.handle(o)

class shelterview(JSONEndpoint):
    url = "shelterview"
    get_permissions = users.VIEW_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        animals = extanimal.get_shelterview_animals(dbo, o.locationfilter, o.siteid)
        al.debug("got %d animals for shelterview" % (len(animals)), "code.shelterview", dbo)
        return {
            "animals": extanimal.get_animals_brief(animals),
            "flags": extlookups.get_animal_flags(dbo),
            "fosterers": extperson.get_shelterview_fosterers(dbo, o.siteid),
            "locations": extlookups.get_internal_locations(dbo, o.locationfilter, o.siteid),
            "perrow": configuration.main_screen_animal_link_max(dbo)
        }

    def post_movelocation(self, o):
        self.check(users.CHANGE_ANIMAL)
        extanimal.update_location_unit(o.dbo, o.user, o.post.integer("animalid"), o.post.integer("locationid"))

    def post_moveunit(self, o):
        self.check(users.CHANGE_ANIMAL)
        extanimal.update_location_unit(o.dbo, o.user, o.post.integer("animalid"), o.post.integer("locationid"), o.post["unit"])

    def post_movefoster(self, o):
        self.check(users.ADD_MOVEMENT)
        post = o.post
        post.data["person"] = post["personid"]
        post.data["animal"] = post["animalid"]
        post.data["fosterdate"] = python2display(o.locale, now(o.dbo.timezone))
        return extmovement.insert_foster_from_form(o.dbo, o.user, post)

class smcom_my(ASMEndpoint):
    url = "smcom_my"

    def content(self, o):
        if session.superuser == 1: smcom.go_smcom_my(o.dbo)

class sql(JSONEndpoint):
    url = "sql"
    get_permissions = users.USE_SQL_INTERFACE
    post_permissions = users.USE_SQL_INTERFACE

    def controller(self, o):
        al.debug("%s opened SQL interface" % o.user, "code.sql", o.dbo)
        return {
            "tables": dbupdate.TABLES + dbupdate.VIEWS
        }

    def post_cols(self, o):
        try:
            if o.post["table"].strip() == "": return ""
            rows = db.query(o.dbo, "SELECT * FROM %s" % o.post["table"], limit=1)
            if len(rows) == 0: return ""
            return "|".join(sorted(rows[0].iterkeys()))
        except Exception as err:
            al.error("%s" % str(err), "code.sql", o.dbo)
            raise utils.ASMValidationError(str(err))

    def post_exec(self, o):
        sql = o.post["sql"].strip()
        return self.exec_sql(o.dbo, sql)

    def post_execfile(self, o):
        sql = o.post["sqlfile"].strip()
        self.content_type("text/plain")
        return self.exec_sql_from_file(o.dbo, sql)

    def exec_sql(self, dbo, sql):
        l = dbo.locale
        rowsaffected = 0
        try:
            for q in dbo.split_queries(sql):
                if q == "": continue
                al.info("%s query: %s" % (session.user, q), "code.sql", dbo)
                if q.lower().startswith("select") or q.lower().startswith("show"):
                    return html.table(db.query(dbo, q))
                else:
                    rowsaffected += db.execute(dbo, q)
                    configuration.db_view_seq_version(dbo, "0")
            return _("{0} rows affected.", l).format(rowsaffected)
        except Exception as err:
            al.error("%s" % str(err), "code.sql", dbo)
            raise utils.ASMValidationError(str(err))

    def exec_sql_from_file(self, dbo, sql):
        l = dbo.locale
        output = []
        for q in dbo.split_queries(sql):
            try:
                if q == "": continue
                al.info("%s query: %s" % (session.user, q), "code.sql", dbo)
                if q.lower().startswith("select") or q.lower().startswith("show"):
                    output.append(str(db.query(dbo, q)))
                else:
                    rowsaffected = db.execute(dbo, q)
                    configuration.db_view_seq_version(dbo, "0")
                    output.append(_("{0} rows affected.", l).format(rowsaffected))
            except Exception as err:
                al.error("%s" % str(err), "code.sql", dbo)
                output.append("ERROR: %s" % str(err))
        return "\n\n".join(output)

class sql_dump(GeneratorEndpoint):
    url = "sql_dump"
    get_permissions = users.USE_SQL_INTERFACE

    def content(self, o):
        l = o.locale
        dbo = o.dbo
        mode = o.post["mode"]
        self.content_type("text/plain")
        if LARGE_FILES_CHUNKED: self.header("Transfer-Encoding", "chunked")
        if mode == "dumpsql":
            al.info("%s executed SQL database dump" % str(session.user), "code.sql", dbo)
            self.header("Content-Disposition", "attachment; filename=\"dump.sql\"")
            for x in dbupdate.dump(dbo): yield x
        if mode == "dumpsqlmedia":
            al.info("%s executed SQL database dump (base64/media)" % str(session.user), "code.sql", dbo)
            self.header("Content-Disposition", "attachment; filename=\"media.sql\"")
            for x in dbupdate.dump_dbfs_base64(dbo): yield x
        if mode == "dumpddlmysql":
            al.info("%s executed DDL dump MySQL" % str(session.user), "code.sql", dbo)
            self.header("Content-Disposition", "attachment; filename=\"ddl_mysql.sql\"")
            dbo2 = db.get_database("MYSQL")
            dbo2.locale = dbo.locale
            yield dbupdate.sql_structure(dbo2)
            yield dbupdate.sql_default_data(dbo2).replace("|=", ";")
        if mode == "dumpddlpostgres":
            al.info("%s executed DDL dump PostgreSQL" % str(session.user), "code.sql", dbo)
            self.header("Content-Disposition", "attachment; filename=\"ddl_postgresql.sql\"")
            dbo2 = db.get_database("POSTGRESQL")
            dbo2.locale = dbo.locale
            yield dbupdate.sql_structure(dbo2)
            yield dbupdate.sql_default_data(dbo2).replace("|=", ";")
        if mode == "dumpddldb2":
            al.info("%s executed DDL dump DB2" % str(session.user), "code.sql", dbo)
            self.header("Content-Disposition", "attachment; filename=\"ddl_db2.sql\"")
            dbo2 = db.get_database("DB2")
            dbo2.locale = dbo.locale
            yield dbupdate.sql_structure(dbo2)
            yield dbupdate.sql_default_data(dbo2).replace("|=", ";")
        elif mode == "dumpsqlasm2":
            # ASM2_COMPATIBILITY
            al.info("%s executed SQL database dump (ASM2 HSQLDB)" % str(session.user), "code.sql", dbo)
            self.header("Content-Disposition", "attachment; filename=\"asm2.sql\"")
            for x in dbupdate.dump_hsqldb(dbo): yield x
        elif mode == "dumpsqlasm2nomedia":
            # ASM2_COMPATIBILITY
            al.info("%s executed SQL database dump (ASM2 HSQLDB, without media)" % str(session.user), "code.sql", dbo)
            self.header("Content-Disposition", "attachment; filename=\"asm2.sql\"")
            for x in dbupdate.dump_hsqldb(dbo, includeDBFS = False): yield x
        elif mode == "animalcsv":
            al.debug("%s executed CSV animal dump" % str(session.user), "code.sql", dbo)
            self.header("Content-Disposition", "attachment; filename=\"animal.csv\"")
            yield utils.csv(l, extanimal.get_animal_find_advanced(dbo, { "logicallocation" : "all", "filter" : "includedeceased,includenonshelter" }))
        elif mode == "personcsv":
            al.debug("%s executed CSV person dump" % str(session.user), "code.sql", dbo)
            self.header("Content-Disposition", "attachment; filename=\"person.csv\"")
            yield utils.csv(l, extperson.get_person_find_simple(dbo, "", session.user, "all", True, True, 0))
        elif mode == "incidentcsv":
            al.debug("%s executed CSV incident dump" % str(session.user), "code.sql", dbo)
            self.header("Content-Disposition", "attachment; filename=\"incident.csv\"")
            yield utils.csv(l, extanimalcontrol.get_animalcontrol_find_advanced(dbo, { "filter" : "" }, 0))
        elif mode == "licencecsv":
            al.debug("%s executed CSV licence dump" % str(session.user), "code.sql", dbo)
            self.header("Content-Disposition", "attachment; filename=\"licence.csv\"")
            yield utils.csv(l, financial.get_licence_find_simple(dbo, ""))
        elif mode == "paymentcsv":
            al.debug("%s executed CSV payment dump" % str(session.user), "code.sql", dbo)
            self.header("Content-Disposition", "attachment; filename=\"payment.csv\"")
            yield utils.csv(l, financial.get_donations(dbo, "m10000"))

class staff_rota(JSONEndpoint):
    url = "staff_rota"
    get_permissions = users.VIEW_ROTA

    def controller(self, o):
        dbo = o.dbo
        startdate = o.post.date("start")
        if startdate is None: startdate = monday_of_week(now())
        rota = extperson.get_rota(dbo, startdate, add_days(startdate, 7))
        al.debug("got %d rota items" % len(rota), "code.staff_rota", dbo)
        return {
            "name": "staff_rota",
            "rows": rota,
            "flags": extlookups.get_person_flags(dbo),
            "flagsel": o.post["flags"],
            "startdate": startdate,
            "prevdate": subtract_days(startdate, 7),
            "nextdate": add_days(startdate, 7),
            "rotatypes": extlookups.get_rota_types(dbo),
            "worktypes": extlookups.get_work_types(dbo),
            "staff": extperson.get_staff_volunteers(dbo)
        }

    def post_create(self, o):
        self.check(users.ADD_ROTA)
        return extperson.insert_rota_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.CHANGE_ROTA)
        extperson.update_rota_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_ROTA)
        for rid in o.post.integer_list("ids"):
            extperson.delete_rota(o.dbo, o.user, rid)

    def post_deleteweek(self, o):
        self.check(users.DELETE_ROTA)
        extperson.delete_rota_week(o.dbo, o.user, o.post.date("startdate"))

    def post_clone(self, o):
        self.check(users.ADD_ROTA)
        startdate = o.post.date("startdate")
        newdate = o.post.date("newdate")
        flags = o.post["flags"]
        extperson.clone_rota_week(o.dbo, o.user, startdate, newdate, flags)

class stocklevel(JSONEndpoint):
    url = "stocklevel"
    get_permissions = users.VIEW_STOCKLEVEL

    def controller(self, o):
        dbo = o.dbo
        levels = extstock.get_stocklevels(dbo, o.post.integer("viewlocation"))
        al.debug("got %d stock levels" % len(levels), "code.stocklevel", dbo)
        return {
            "stocklocations": extlookups.get_stock_locations(dbo),
            "stocknames": "|".join(extstock.get_stock_names(dbo)),
            "stockusagetypes": extlookups.get_stock_usage_types(dbo),
            "stockunits": "|".join(extstock.get_stock_units(dbo)),
            "newlevel": o.post.integer("newlevel") == 1,
            "sortexp": o.post.integer("sortexp") == 1,
            "rows": levels
        }

    def post_create(self, o):
        self.check(users.ADD_STOCKLEVEL)
        for dummy in range(0, o.post.integer("quantity")):
            extstock.insert_stocklevel_from_form(o.dbo, o.post, o.user)

    def post_update(self, o):
        self.check(users.CHANGE_STOCKLEVEL)
        extstock.update_stocklevel_from_form(o.dbo, o.post, o.user)

    def post_delete(self, o):
        self.check(users.DELETE_STOCKLEVEL)
        for sid in o.post.integer_list("ids"):
            extstock.delete_stocklevel(o.dbo, o.user, sid)

    def post_lastname(self, o):
        self.check(users.VIEW_STOCKLEVEL)
        return extstock.get_last_stock_with_name(o.dbo, o.post["name"])

class systemusers(JSONEndpoint):
    url = "systemusers"
    js_module = "users"
    get_permissions = users.EDIT_USER

    def controller(self, o):
        dbo = o.dbo
        user = users.get_users(dbo)
        roles = users.get_roles(dbo)
        al.debug("editing %d system users" % len(user), "code.systemusers", dbo)
        return {
            "rows": user,
            "roles": roles,
            "internallocations": extlookups.get_internal_locations(dbo),
            "sites": extlookups.get_sites(dbo)
        }

    def post_create(self, o):
        self.check(users.ADD_USER)
        return users.insert_user_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.EDIT_USER)
        users.update_user_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.EDIT_USER)
        for uid in o.post.integer_list("ids"):
            users.delete_user(o.dbo, o.user, uid)

    def post_reset(self, o):
        self.check(users.EDIT_USER)
        for uid in o.post.integer_list("ids"):
            users.reset_password(o.dbo, uid, o.post["password"])

class task(JSONEndpoint):
    url = "task"

    def controller(self, o):
        return { }
   
    def post_poll(self, o):
        return "%s|%d|%s|%s" % (async.get_task_name(o.dbo), async.get_progress_percent(o.dbo), async.get_last_error(o.dbo), async.get_return_value(o.dbo))

    def post_stop(self, o):
        async.set_cancel(o.dbo, True)

class test(JSONEndpoint):
    url = "test"
    get_permissions = users.VIEW_TEST

    def controller(self, o):
        dbo = o.dbo
        offset = o.post["offset"]
        if offset == "": offset = "m365"
        test = extmedical.get_tests_outstanding(dbo, offset, o.locationfilter, o.siteid)
        al.debug("got %d tests" % len(test), "code.test", dbo)
        return {
            "name": "test",
            "newtest": o.post.integer("newtest") == 1,
            "rows": test,
            "stockitems": extstock.get_stock_items(dbo),
            "stockusagetypes": extlookups.get_stock_usage_types(dbo),
            "testtypes": extlookups.get_test_types(dbo),
            "testresults": extlookups.get_test_results(dbo)
        }

    def post_create(self, o):
        self.check(users.ADD_TEST)
        return extmedical.insert_test_from_form(o.dbo, o.user, o.post)

    def post_createbulk(self, o):
        self.check(users.ADD_TEST)
        for animalid in o.post.integer_list("animals"):
            o.post.data["animal"] = str(animalid)
            extmedical.insert_test_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.CHANGE_TEST)
        extmedical.update_test_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_TEST)
        for vid in o.post.integer_list("ids"):
            extmedical.delete_test(o.dbo, o.user, vid)

    def post_perform(self, o):
        self.check(users.CHANGE_TEST)
        newdate = o.post.date("newdate")
        vet = o.post.integer("givenvet")
        testresult = o.post.integer("testresult")
        for vid in o.post.integer_list("ids"):
            extmedical.complete_test(o.dbo, o.user, vid, newdate, testresult, vet)
        if o.post.integer("item") != -1:
            extstock.deduct_stocklevel_from_form(o.dbo, o.user, o.post)

class timeline(JSONEndpoint):
    url = "timeline"
    get_permissions = users.VIEW_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        evts = extanimal.get_timeline(dbo, 500)
        al.debug("timeline events, run by %s, got %d events" % (o.user, len(evts)), "code.timeline", dbo)
        return {
            "recent": evts,
            "resultcount": len(evts)
        }

class transport(JSONEndpoint):
    url = "transport"
    get_permissions = users.VIEW_TRANSPORT

    def controller(self, o):
        dbo = o.dbo
        transports = extmovement.get_active_transports(dbo)
        al.debug("got %d transports" % len(transports), "code.transport", dbo)
        return {
            "name": "transport",
            "transporttypes": extlookups.get_transport_types(dbo),
            "rows": transports
        }

    def post_create(self, o):
        self.check(users.ADD_TRANSPORT)
        return extmovement.insert_transport_from_form(o.dbo, o.user, o.post)

    def post_createbulk(self, o):
        self.check(users.ADD_TRANSPORT)
        for animalid in o.post.integer_list("animals"):
            o.post.data["animal"] = str(animalid)
            extmovement.insert_transport_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.CHANGE_TRANSPORT)
        extmovement.update_transport_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_TRANSPORT)
        for mid in o.post.integer_list("ids"):
            extmovement.delete_transport(o.dbo, o.user, mid)

    def post_setstatus(self, o):
        self.check(users.CHANGE_TRANSPORT)
        extmovement.update_transport_statuses(o.dbo, o.user, o.post.integer_list("ids"), o.post.integer("newstatus"))

class traploan(JSONEndpoint):
    url = "traploan"
    get_permissions = users.VIEW_TRAPLOAN

    def controller(self, o):
        dbo = o.dbo
        traploans = []
        if o.post["filter"] == "" or o.post["filter"] == "active":
            traploans = extanimalcontrol.get_active_traploans(dbo)
        al.debug("got %d trap loans" % len(traploans), "code.traploan", dbo)
        return {
            "name": "traploan",
            "rows": traploans,
            "traptypes": extlookups.get_trap_types(dbo)
        }

    def post_create(self, o):
        self.check(users.ADD_TRAPLOAN)
        return extanimalcontrol.insert_traploan_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.CHANGE_TRAPLOAN)
        extanimalcontrol.update_traploan_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_TRAPLOAN)
        for lid in o.post.integer_list("ids"):
            extanimalcontrol.delete_traploan(o.dbo, o.user, lid)

class vaccination(JSONEndpoint):
    url = "vaccination"
    get_permissions = users.VIEW_VACCINATION

    def controller(self, o):
        dbo = o.dbo
        offset = o.post["offset"]
        if offset == "": offset = "m365"
        vacc = extmedical.get_vaccinations_outstanding(dbo, offset, o.locationfilter, o.siteid)
        al.debug("got %d vaccinations" % len(vacc), "code.vaccination", dbo)
        return {
            "name": "vaccination",
            "newvacc": o.post.integer("newvacc") == 1,
            "rows": vacc,
            "batches": extmedical.get_batch_for_vaccination_types(dbo),
            "manufacturers": "|".join(extmedical.get_vacc_manufacturers(dbo)),
            "stockitems": extstock.get_stock_items(dbo),
            "stockusagetypes": extlookups.get_stock_usage_types(dbo),
            "vaccinationtypes": extlookups.get_vaccination_types(dbo)
        }

    def post_create(self, o):
        self.check(users.ADD_VACCINATION)
        return extmedical.insert_vaccination_from_form(o.dbo, o.user, o.post)

    def post_createbulk(self, o):
        self.check(users.ADD_VACCINATION)
        for animalid in o.post.integer_list("animals"):
            o.post.data["animal"] = str(animalid)
            extmedical.insert_vaccination_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(users.CHANGE_VACCINATION)
        extmedical.update_vaccination_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(users.DELETE_VACCINATION)
        for vid in o.post.integer_list("ids"):
            extmedical.delete_vaccination(o.dbo, o.user, vid)

    def post_given(self, o):
        self.check(users.BULK_COMPLETE_VACCINATION)
        post = o.post
        newdate = post.date("newdate")
        rescheduledate = post.date("rescheduledate")
        reschedulecomments = post["reschedulecomments"]
        givenexpires = post.date("givenexpires")
        givenbatch = post["givenbatch"]
        givenmanufacturer = post["givenmanufacturer"]
        vet = post.integer("givenvet")
        for vid in post.integer_list("ids"):
            extmedical.complete_vaccination(o.dbo, o.user, vid, newdate, vet, givenexpires, givenbatch, givenmanufacturer)
            if rescheduledate is not None:
                extmedical.reschedule_vaccination(o.dbo, o.user, vid, rescheduledate, reschedulecomments)
            if post.integer("item") != -1:
                extmedical.update_vaccination_batch_stock(o.dbo, o.user, vid, post.integer("item"))
        if post.integer("item") != -1:
            extstock.deduct_stocklevel_from_form(o.dbo, o.user, post)

    def post_required(self, o):
        self.check(users.BULK_COMPLETE_VACCINATION)
        newdate = o.post.date("newdate")
        for vid in o.post.integer_list("ids"):
            extmedical.update_vaccination_required(o.dbo, o.user, vid, newdate)

class waitinglist(JSONEndpoint):
    url = "waitinglist"
    get_permissions = users.VIEW_WAITING_LIST

    def controller(self, o):
        dbo = o.dbo
        a = extwaitinglist.get_waitinglist_by_id(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        al.debug("opened waiting list %s %s" % (a["OWNERNAME"], a["SPECIESNAME"]), "code.waitinglist", dbo)
        return {
            "animal": a,
            "additional": extadditional.get_additional_fields(dbo, a["ID"], "waitinglist"),
            "audit": self.checkb(users.VIEW_AUDIT_TRAIL) and audit.get_audit_for_link(dbo, "animalwaitinglist", a["ID"]) or [],
            "logtypes": extlookups.get_log_types(dbo),
            "sizes": extlookups.get_sizes(dbo),
            "species": extlookups.get_species(dbo),
            "urgencies": extlookups.get_urgencies(dbo),
            "templates": template.get_document_templates(dbo),
            "tabcounts": extwaitinglist.get_satellite_counts(dbo, a["ID"])[0]
        }

    def post_save(self, o):
        self.check(users.CHANGE_WAITING_LIST)
        extwaitinglist.update_waitinglist_from_form(o.dbo, o.post, o.user)

    def post_email(self, o):
        self.check(users.EMAIL_PERSON)
        l = o.locale
        if not extwaitinglist.send_email_from_form(o.dbo, o.user, o.post):
            raise utils.ASMError(_("Failed sending email", l))

    def post_delete(self, o):
        self.check(users.DELETE_WAITING_LIST)
        extwaitinglist.delete_waitinglist(o.dbo, o.user, o.post.integer("id"))

    def post_toanimal(self, o):
        self.check(users.ADD_ANIMAL)
        return str(extwaitinglist.create_animal(o.dbo, o.user, o.post.integer("id")))

class waitinglist_diary(JSONEndpoint):
    url = "waitinglist_diary"
    js_module = "diary"
    get_permissions = users.VIEW_DIARY

    def controller(self, o):
        dbo = o.dbo
        a = extwaitinglist.get_waitinglist_by_id(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        diaries = extdiary.get_diaries(dbo, extdiary.WAITINGLIST, o.post.integer("id"))
        al.debug("got %d diaries" % len(diaries), "code.waitinglist_diary", dbo)
        return {
            "rows": diaries,
            "animal": a,
            "tabcounts": extwaitinglist.get_satellite_counts(dbo, a["WLID"])[0],
            "name": "waitinglist_diary",
            "linkid": a["WLID"],
            "linktypeid": extdiary.WAITINGLIST,
            "forlist": users.get_users_and_roles(dbo)
        }

class waitinglist_log(JSONEndpoint):
    url = "waitinglist_log"
    js_module = "log"
    get_permissions = users.VIEW_LOG

    def controller(self, o):
        dbo = o.dbo
        logfilter = o.post.integer("filter")
        if logfilter == 0: logfilter = configuration.default_log_filter(dbo)
        a = extwaitinglist.get_waitinglist_by_id(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        logs = extlog.get_logs(dbo, extlog.WAITINGLIST, o.post.integer("id"), logfilter)
        al.debug("got %d logs" % len(logs), "code.waitinglist_diary", dbo)
        return {
            "name": "waitinglist_log",
            "linkid": o.post.integer("id"),
            "linktypeid": extlog.WAITINGLIST,
            "filter": logfilter,
            "rows": logs,
            "animal": a,
            "tabcounts": extwaitinglist.get_satellite_counts(dbo, a["WLID"])[0],
            "logtypes": extlookups.get_log_types(dbo)
        }

class waitinglist_media(JSONEndpoint):
    url = "waitinglist_media"
    js_module = "media"
    get_permissions = users.VIEW_MEDIA

    def controller(self, o):
        dbo = o.dbo
        a = extwaitinglist.get_waitinglist_by_id(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        m = extmedia.get_media(dbo, extmedia.WAITINGLIST, o.post.integer("id"))
        al.debug("got %d media" % len(m), "code.waitinglist_media", dbo)
        return {
            "media": m,
            "animal": a,
            "tabcounts": extwaitinglist.get_satellite_counts(dbo, a["WLID"])[0],
            "showpreferred": True,
            "linkid": o.post.integer("id"),
            "linktypeid": extmedia.WAITINGLIST,
            "logtypes": extlookups.get_log_types(dbo),
            "name": self.url,
            "sigtype": ELECTRONIC_SIGNATURES
        }

class waitinglist_new(JSONEndpoint):
    url = "waitinglist_new"
    get_permissions = users.ADD_WAITING_LIST
    post_permissions = users.ADD_WAITING_LIST

    def controller(self, o):
        dbo = o.dbo
        return {
            "species": extlookups.get_species(dbo),
            "additional": extadditional.get_additional_fields(dbo, 0, "waitinglist"),
            "sizes": extlookups.get_sizes(dbo),
            "urgencies": extlookups.get_urgencies(dbo)
        }

    def post_all(self, o):
        return str(extwaitinglist.insert_waitinglist_from_form(o.dbo, o.post, o.user))

class waitinglist_results(JSONEndpoint):
    url = "waitinglist_results"
    get_permissions = users.VIEW_WAITING_LIST

    def controller(self, o):
        dbo = o.dbo
        post = o.post
        priorityfloor = utils.iif(post["priorityfloor"] == "", db.query_int(dbo, "SELECT MAX(ID) FROM lkurgency"), post.integer("priorityfloor"))
        speciesfilter = utils.iif(post["species"] == "", -1, post.integer("species"))
        sizefilter = utils.iif(post["size"] == "", -1, post.integer("size"))
        rows = extwaitinglist.get_waitinglist(dbo, priorityfloor, speciesfilter, sizefilter,
            post["addresscontains"], post.integer("includeremoved"), post["namecontains"], post["descriptioncontains"])
        al.debug("found %d results" % (len(rows)), "code.waitinglist_results", dbo)
        return {
            "rows": rows,
            "seladdresscontains": post["addresscontains"],
            "seldescriptioncontains": post["descriptioncontains"],
            "selincluderemoved": post.integer("includeremoved"),
            "selnamecontains": post["namecontains"],
            "selpriorityfloor": priorityfloor,
            "selspecies": speciesfilter,
            "selsize": sizefilter,
            "species": extlookups.get_species(dbo),
            "sizes": extlookups.get_sizes(dbo),
            "urgencies": extlookups.get_urgencies(dbo),
            "yesno": extlookups.get_yesno(dbo)
        }

    def post_delete(self, o):
        self.check(users.DELETE_WAITING_LIST)
        for wid in o.post.integer_list("ids"):
            extwaitinglist.delete_waitinglist(o.dbo, o.user, wid)

    def post_complete(self, o):
        self.check(users.CHANGE_WAITING_LIST)
        for wid in o.post.integer_list("ids"):
            extwaitinglist.update_waitinglist_remove(o.dbo, o.user, wid)

    def post_highlight(self, o):
        self.check(users.CHANGE_WAITING_LIST)
        for wid in o.post.integer_list("ids"):
            extwaitinglist.update_waitinglist_highlight(o.dbo, wid, o.post["himode"])



# List of routes constructed from class definitions
routes = []

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
app = web.application(generate_routes(), globals())
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

if __name__ == "__main__":
    app.run()

