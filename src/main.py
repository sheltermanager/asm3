#!/usr/bin/env python3

import os, sys, traceback

# The path to the folder containing the ASM3 modules
PATH = os.path.dirname(os.path.abspath(__file__)) + os.sep

# Prepend our modules to the path to make sure they're added first
sys.path.insert(0, PATH)

import web062 as web

import asm3.al
import asm3.additional
import asm3.animal
import asm3.animalcontrol
import asm3.asynctask
import asm3.audit
import asm3.cachedisk
import asm3.cachemem
import asm3.checkmicrochip
import asm3.clinic
import asm3.configuration
import asm3.csvimport
import asm3.db
import asm3.dbfs
import asm3.dbupdate
import asm3.diary
import asm3.event
import asm3.financial
import asm3.html
import asm3.log
import asm3.lookups
import asm3.lostfound
import asm3.media
import asm3.medical
import asm3.movement
import asm3.onlineform
import asm3.paymentprocessor.base
import asm3.paymentprocessor.paypal
import asm3.paymentprocessor.stripeh
import asm3.paymentprocessor.cardcom
import asm3.person
import asm3.publish
import asm3.publishers.base
import asm3.publishers.html
import asm3.publishers.vetenvoy
import asm3.reports
import asm3.search
import asm3.service
import asm3.smcom
import asm3.stock
import asm3.template
import asm3.users
import asm3.utils
import asm3.waitinglist
import asm3.wordprocessor

from asm3.i18n import _, translate, get_version, get_display_date_format, \
    get_currency_prefix, get_currency_symbol, get_currency_dp, get_currency_radix, \
    get_currency_digit_grouping, get_dst, get_locales, parse_date, python2display, \
    add_minutes, add_days, subtract_days, subtract_months, first_of_month, last_of_month, \
    monday_of_week, sunday_of_week, first_of_year, last_of_year, now, format_currency

from asm3.sitedefs import AUTORELOAD, BASE_URL, CONTENT_SECURITY_POLICY, DEPLOYMENT_TYPE, \
    ELECTRONIC_SIGNATURES, EMERGENCY_NOTICE, \
    AKC_REUNITE_BASE_URL, BUDDYID_BASE_URL, FINDPET_BASE_URL, HOMEAGAIN_BASE_URL, \
    LARGE_FILES_CHUNKED, LOCALE, JQUERY_UI_CSS, \
    LEAFLET_CSS, LEAFLET_JS, MULTIPLE_DATABASES, \
    ADMIN_EMAIL, EMAIL_ERRORS, MADDIES_FUND_TOKEN_URL, HTMLFTP_PUBLISHER_ENABLED, \
    MANUAL_HTML_URL, MANUAL_PDF_URL, MANUAL_FAQ_URL, MANUAL_VIDEO_URL, MAP_LINK, MAP_PROVIDER, \
    MAP_PROVIDER_KEY, MAX_DOCUMENT_TEMPLATE_SIZE, OSM_MAP_TILES, FOUNDANIMALS_FTP_USER, PETCADEMY_FTP_HOST, \
    PETLINK_BASE_URL, PETRESCUE_URL, PETSLOCATED_FTP_USER, \
    RESIZE_IMAGES_DURING_ATTACH, RESIZE_IMAGES_SPEC, SAC_METRICS_URL, \
    SAVOURLIFE_URL, SERVICE_URL, SESSION_SECURE_COOKIE, SESSION_DEBUG, SHARE_BUTTON, SMARTTAG_FTP_USER, \
    SMCOM_LOGIN_URL, SMCOM_PAYMENT_LINK, PAYPAL_VALIDATE_IPN_URL, SQUARE_PAYMENT_ENVIRONMENT

from asm3.typehints import Any, Dict, Generator, List, ResultRow, Session

from asm3.__version__ import BUILD

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
        def __contains__(self, key: str) -> bool:
            rv = asm3.cachemem.get(key) is not None
            if SESSION_DEBUG: asm3.al.debug("contains(%s)=%s" % (key, rv), "MemCacheStore.__contains__")
            return rv
        def __getitem__(self, key: str) -> Any:
            rv = asm3.cachemem.get(key)
            if SESSION_DEBUG: asm3.al.debug("getitem(%s)=%s" % (key, rv), "MemCacheStore.__getitem__")
            return rv
        def __setitem__(self, key: str, value: Any) -> Any:
            rv = asm3.cachemem.put(key, value, web.config.session_parameters["timeout"])
            if SESSION_DEBUG: asm3.al.debug("setitem(%s, %s)=%s" % (key, value, rv), "MemCacheStore.__setitem__")
            return rv
        def __delitem__(self, key: str) -> Any:
            rv = asm3.cachemem.delete(key)
            if SESSION_DEBUG: asm3.al.debug("delitem(%s)=%s" % (key, rv), "MemCacheStore.__delitem__")
            return rv
        def cleanup(self, timeout):
            pass # Not needed, we assign values to memcache with timeout
    # Set session parameters, 24 hour timeout
    web.config.session_parameters["cookie_name"] = "asm_session_id"
    web.config.session_parameters["cookie_path"] = "/"
    web.config.session_parameters["timeout"] = 86400
    web.config.session_parameters["ignore_change_ip"] = True
    web.config.session_parameters["ignore_expiry"] = True # session disappears on timeout set above 
    web.config.session_parameters["secure"] = SESSION_SECURE_COOKIE
    sess = None
    if asm3.utils.websession is None:
        sess = web.session.Session(app, MemCacheStore(), initializer={"user" : None, "dbo" : None, "locale" : None, 
            "roles": None, "securitymap": None, "superuser": None, "searches" : [], "staffid": None, 
            "siteid": None, "locationfilter": None,  "visibleanimalids": "" })
        asm3.utils.websession = sess
    else:
        sess = asm3.utils.websession
    return sess

def asm_404() -> str:
    """
    Custom 404 page
    """
    s = """<!DOCTYPE html>
        <html>
        <head>
        <title>404</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <link rel="shortcut icon" href="static/images/logo/icon-16.png">
        <link rel="icon" href="static/images/logo/icon-32.png" sizes="32x32">
        <link rel="icon" href="static/images/logo/icon-48.png" sizes="48x48">
        <link rel="icon" href="static/images/logo/icon-128.png" sizes="128x128">
        </head>
        <body style="background-color: #999">
        <div style="position: absolute; left: 20%; width: 60%; padding: 20px; background-color: white">
        <img src="static/images/logo/icon-64.png" align="right" />
        <h2>Error 404</h2>
        <p>Sorry, but the record or resource you tried to access was not found.</p>
        <p><a href="javascript:history.back()">Go Back</a></p>
        </div>
        </body>
        </html>"""
    web.header("Content-Type", "text/html")
    web.header("Cache-Control", "public, max-age=3600, s-maxage=3600") # Cache 404s for an hour at any proxy/CDN as they can be a DoS vector
    session.no_cookie = True
    return web.notfound(s)

def asm_500_email() -> Any:
    """
    Custom 500 error page that sends emails to the site admin
    (web.InternalError)
    """
    ei = sys.exc_info()
    path = web.ctx.path 
    env = ""
    for k, v in web.ctx.env.items(): env += f"{k}: {v}\n"
    msg = f"{traceback.format_exc()}\n\nDatabase:\n\n{session.dbo}\n\nData:\n\n{web.ctx.query} {web.data()}\n\nEnvironment:\n\n{env}"
    asm3.utils.send_error_email(ei[0], ei[1], path, msg)
    s = """<!DOCTYPE html
        <html>
        <head>
        <title>500</title>
        <meta http-equiv="refresh" content="5;url=main">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <link rel="shortcut icon" href="static/images/logo/icon-16.png">
        <link rel="icon" href="static/images/logo/icon-32.png" sizes="32x32">
        <link rel="icon" href="static/images/logo/icon-48.png" sizes="48x48">
        <link rel="icon" href="static/images/logo/icon-128.png" sizes="128x128">
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
        </html>"""
    web.header("Content-Type", "text/html")
    web.header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0") # Never cache 500 errors
    return web.internalerror(s)

def asm_500() -> Any:
    """
    Custom 500 error page that outputs the stack trace
    (web.InternalError)
    """
    env = ""
    for k, v in web.ctx.env.items(): env += f"{k}: {v}\n"
    s = f"""<!DOCTYPE html
        <html>
        <head>
        <title>500</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <link rel="shortcut icon" href="static/images/logo/icon-16.png">
        <link rel="icon" href="static/images/logo/icon-32.png" sizes="32x32">
        <link rel="icon" href="static/images/logo/icon-48.png" sizes="48x48">
        <link rel="icon" href="static/images/logo/icon-128.png" sizes="128x128">
        </head>
        <body style="background-color: #999">
        <div style="position: absolute; left: 20%; width: 60%; padding: 20px; background-color: white">
        <img src="static/images/logo/icon-64.png" align="right" />
        <h2>Error 500 --&gt; {web.ctx.path}</h2>
        <pre>{traceback.format_exc()}</pre>
        <h3>Database</h3>
        <pre>{session.dbo}</pre>
        <h3>Data</h3>
        <pre>{web.ctx.query} {web.data()}</pre>
        <h3>Enivronment</h3>
        <pre>{env}</pre>
        </div>
        </body>
        </html>"""
    web.header("Content-Type", "text/html")
    web.header("Cache-Control", "no-cache, no-store, must-revalidate, max-age=0") # Never cache 500 errors
    session.no_cookie = True
    return web.internalerror(s)

def emergency_notice() -> str:
    """
    Returns emergency notice text if any is set.
    """
    if EMERGENCY_NOTICE != "":
        if os.path.exists(EMERGENCY_NOTICE):
            s = asm3.utils.read_text_file(EMERGENCY_NOTICE)
            return s
    return ""

def generate_routes() -> List[str]:
    """ Extract the url property from all classes and construct the route list """
    g = globals().copy()
    for name, obj in g.items():
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
    session_cookie = True  # Whether to send a session cookie
    user_activity = True   # Hitting this endpoint qualifies as user activity
    use_web_input = True   # Unpack values with webpy's web.input()
    login_url = "login"    # The url to go to if not logged in
    data = None            # Request data posted to this endpoint as bytes or str if data_encoding is set
    data_encoding = None   # codec to use for decoding of posted data to str (None to not decode)

    def _params(self) -> None:
        l = session.locale
        if l is None:
            l = LOCALE
        post = asm3.utils.PostedData({}, l)
        try:
            if self.use_web_input: post = asm3.utils.PostedData(web.input(filechooser = {}), l)
            self.data = web.data()
            if self.data_encoding: self.data = asm3.utils.bytes2str(self.data, encoding=self.data_encoding)
        except Exception as err:
            asm3.al.error("Failed unpacking params: %s" % str(err), "ASMEndpoint._params", session.dbo, sys.exc_info())
        return web.utils.storage( data=self.data, post=post, dbo=session.dbo, locale=l, user=session.user, session=session,
            staffid = session.staffid, siteid = session.siteid,
            lf = asm3.animal.LocationFilter(session.locationfilter, session.siteid, session.visibleanimalids))

    def check(self, permissions: Any) -> None:
        """ Check logged in and permissions (which can be a single permission string or a list/tuple) """
        if not self.session_cookie:
            session.send_cookie = False # Stop the session object calling setcookie
        if self.check_logged_in:
            self.check_loggedin(session, web, self.login_url)
            self.check_2fa(session, web)
        if isinstance(permissions, str):
            asm3.users.check_permission(session, permissions)
        else:
            for p in permissions:
                asm3.users.check_permission(session, p)

    def checkb(self, permissions: Any) -> bool:
        """ Check logged in and a single permission, returning a boolean """
        if self.check_logged_in:
            self.check_loggedin(session, web, self.login_url)
        return asm3.users.check_permission_bool(session, permissions)

    def check_animal(self, a: ResultRow) -> None:
        """ Checks whether the animal we're about to look at is viewable by the user """
        lf = asm3.animal.LocationFilter(session.locationfilter, session.siteid, session.visibleanimalids)
        if not lf.match(a):
            raise asm3.utils.ASMPermissionError("animal not in location filter/site")

    def check_locked_db(self) -> None:
        if session.dbo and session.dbo.locked: 
            l = session.locale
            raise asm3.utils.ASMPermissionError(_("This database is locked.", l))

    def check_loggedin(self, session: Session, web: Any, loginpage = "login") -> None:
        """
        Checks if we have a logged in user and if not, redirects to
        the login page
        """
        if not self.is_loggedin(session):
            path = web.ctx.path
            if path.startswith("/"): path = path[1:]
            query = str(web.ctx.query)
            raise web.seeother("%s/%s?target=%s%s" % (BASE_URL, loginpage, path, query))
        elif self.user_activity:
            # update the last user activity if logged in
            asm3.users.update_user_activity(session.dbo, session.user)

    def check_2fa(self, session: Session, web: Any) -> None:
        """
        Checks if the force2fa flag has been set in the session, and if so
        redirects to the change_user_settings page for the user to enable 2FA.
        force2fa is only set if the cfg option Force2FA is on, and the user logged
        in without using 2FA.
        Does not apply if the URL being requested is the change_user_settings
        page to stop a redirect loop.
        """
        if "force2fa" in session and session.force2fa and web.ctx.path.find("/change_user_settings") == -1:
            raise web.seeother("%s/change_user_settings?force2fa=1" % BASE_URL)

    def check_mode(self, mode: str) -> bool:
        """
        Verify that the value given for mode is valid. Valid mode
        values are between 2 and 30 chars in length and contain only
        lowercase ASCII letters [a-z] (no punctuation or spaces).
        """
        if len(mode) < 2 or len(mode) > 30: return False
        for c in mode:
            if ord(c) < 97 or ord(c) > 122:
                return False
        return True

    def content(self, o) -> str:
        """ Virtual function: override to get the content """
        return ""

    def cache_control(self, client_ttl = 0, cache_ttl = 0) -> None:
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

    def content_disposition(self, disp: str = "inline", filename: str = "", extension: str = "", default: str = "filename") -> None:
        """ 
        Sends a Content-Disposition header
        disp: inline or attachment
        filename: the filename portion without extension
        extension: The extension to add to the filename. If extension is "", assume it has already been added to filename
        default: If there are no latin1 chars in the filename, use this name instead
        """
        filename = asm3.utils.strip_non_ascii(filename).strip()
        filename = filename.replace(" ", "_").replace(",", "_").replace("\"", "").replace("'", "").replace("\\", "").replace("/", "").lower()
        if filename == "": filename = default
        if extension != "": filename = "%s.%s" % (filename, extension)
        disposition = f"{disp}; filename={filename}"
        self.header("Content-Disposition", disposition)

    def content_type(self, ct: str) -> None:
        """ Sends a content-type header """
        self.header("Content-Type", ct)

    def data_param(self, p: str) -> str:
        """ Returns a URL encoded parameter from the data stream.
            This is useful for some services where they send data in
            odd encodings (eg: PayPal use cp1252) and we can't use 
            web.input, which assumes utf-8 """
        for b in self.data.split("&"):
            if b.startswith(p):
                return b.split("=")[1]
        return ""

    def get_cookie(self, s: str) -> str:
        """ Returns the value of cookie s. Returns None if it does not exist. """
        try:
            return web.cookies().get(s)
        except:
            return None

    def set_cookie(self, name: str, value: str, ttl: int) -> None:
        """ Sets a cookie value """
        web.setcookie(name, value, expires=ttl, secure=SESSION_SECURE_COOKIE, httponly=True, samesite="none")

    def header(self, key: str, value: str) -> None:
        """ Set the response header key to value """
        web.header(key, value)

    def is_loggedin(self, session: Session) -> bool:
        """
        Returns true if the user is logged in and the user is valid 
        (ie. has not been deleted or had login disabled)
        """
        if "user" not in session: return False
        if session.user is None: return False
        if "dbo" not in session: return False
        if session.dbo is None: return False
        return asm3.users.is_user_valid(session.dbo, session.user)

    def notfound(self) -> Any:
        """ Returns a 404 (web.NotFound) """
        raise web.notfound()

    def post_all(self, o) -> str:
        """ Virtual function: override to handle postback """
        return ""

    def query(self) -> str:
        """ Returns the request query string """
        return web.ctx.query

    def redirect(self, route: str) -> None:
        """ Redirect to another route 
            Uses BASE_URL if a relative route is given to help CDNs. """
        if not route.startswith("http"): route = "%s/%s" % (BASE_URL, route)
        raise web.seeother(route)

    def referer(self) -> str:
        """ Returns the referer request header """
        return web.ctx.env.get("HTTP_REFERER", "")

    def reload_config(self) -> None:
        """ Reloads items in the session based on database values, invalidates config.js so client reloads it """
        asm3.users.update_session(session.dbo, session, session.user)

    def remote_ip(self) -> str:
        """ Gets the IP address of the requester, taking account of reverse proxies """
        remoteip = web.ctx['ip']
        if "HTTP_X_FORWARDED_FOR" in web.ctx.env:
            xf = web.ctx.env["HTTP_X_FORWARDED_FOR"]
            if xf is not None and str(xf).strip() != "":
                remoteip = xf
        return remoteip

    def user_agent(self) -> str:
        """ Returns the user agent request header """
        return web.ctx.env.get("HTTP_USER_AGENT", "")

    def GET(self) -> str:
        self.check(self.get_permissions)
        return self.content(self._params())

    def POST(self) -> str:
        """ Handle a POST, deal with permissions and locked databases """
        if self.check_logged_in:
            self.check_locked_db()
        self.check(self.post_permissions)
        o = self._params()
        mode = o.post["mode"]
        if mode == "": 
            return self.post_all(o)
        elif not self.check_mode(mode):
            raise asm3.utils.ASMError("invalid mode")
        else:
            # valid mode value has been supplied, call post_mode
            return getattr(self.__class__, "post_%s" % mode)(self, o)

class GeneratorEndpoint(ASMEndpoint):
    """Base class for endpoints that use generators for their content """
    def GET(self) -> Generator[str, None, None]:
        self.check(self.get_permissions)
        if LARGE_FILES_CHUNKED: 
            self.header("Transfer-Encoding", "chunked")
        for x in self.content(self._params()):
            yield x

class JSONEndpoint(ASMEndpoint):
    """ Base class for ASM endpoints that return JSON """
    js_module = ""         # The javascript module to start (can be omitted if same as url)
    url = ""               # The route/url to this target

    def controller(self, o) -> Dict:
        """ Virtual function to be overridden - return controller as a dict """
        return {}

    def GET(self) -> str:
        """ Handle a GET, deal with permissions, session and JSON responses """
        self.check(self.get_permissions)
        o = self._params()
        c = self.controller(o)
        self.cache_control(0)
        if self.js_module == "":
            self.js_module = self.url
        if not o.post["json"] == "true":
            self.content_type("text/html")
            self.header("X-Frame-Options", "SAMEORIGIN") 
            self.header("X-Content-Type-Options", "nosniff") 
            self.header("X-XSS-Protection", "1; mode=block") 
            self.header("Referrer-Policy", "same-origin") 
            self.header("Strict-Transport-Security", "max-age=%s" % CACHE_ONE_MONTH) 
            nonce = asm3.utils.uuid_str()
            # CSP is not applied to users of the mobile app as we still have users with
            # older iPads on iOS/Safari 9 that only supports CSP1
            if CONTENT_SECURITY_POLICY != "":
                self.header("Content-Security-Policy", CONTENT_SECURITY_POLICY % { "nonce": nonce })
            return "%(header)s\n" \
                "<script nonce='%(nonce)s'>\n" \
                "controller=%(controller)s;\n" \
                "$(document).ready(function() { " \
                "common.route_listen(); " \
                "common.module_start(\"%(js_module)s\"); " \
                "%(js_injection)s " \
                "});\n</script>\n</body>\n</html>" % { 
                    "controller": asm3.utils.json(c),
                    "header": asm3.html.header("", session),
                    "js_injection": asm3.configuration.js_injection(o.dbo),
                    "js_module": self.js_module, 
                    "nonce": nonce }
        else:
            self.content_type("application/json")
            return asm3.utils.json(c)

class index(ASMEndpoint):
    url = "/"
    check_logged_in = False

    def content(self, o):
        # If there's no database structure, create it before 
        # redirecting to the login page.
        if not MULTIPLE_DATABASES:
            dbo = asm3.db.get_database()
            if not dbo.has_structure():
                self.redirect("database")
        self.redirect("main")

class database(ASMEndpoint):
    url = "database"
    check_logged_in = False

    def content(self, o):
        if MULTIPLE_DATABASES:
            if asm3.smcom.active():
                raise asm3.utils.ASMPermissionError("N/A for sm.com")
            else:
                # We can't create the database as we have multiple, so
                # output the SQL creation script with default data
                # for whatever our dbtype is instead
                dbo = asm3.db.get_dbo()
                s = "-- Creation script for %s\n\n" % dbo.dbtype
                s += asm3.dbupdate.sql_structure(dbo)
                s += asm3.dbupdate.sql_default_data(dbo).replace("|=", ";")
                self.content_type("text/plain")
                self.content_disposition("attachment", "setup.sql")
                return s
            
        optionslocales = ""
        for code, label in get_locales():
            optionslocales += "<option value=\"" + code + "\">" + label + "</option>"

        dbo = asm3.db.get_database()
        if dbo.has_structure():
            raise asm3.utils.ASMPermissionError("Database already created")
        
        s = asm3.html.bare_header("Create your database")
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
            $("select").val("%s");
            $("#createdb").button().click(function() {
                $("#createdb").button("disable");
                $("#info").fadeIn();
                $("#cdbf").submit();
            });
            </script>
            """ % (optionslocales, LOCALE)
        s += asm3.html.footer()
        self.content_type("text/html")
        return s

    def post_all(self, o):
        dbo = asm3.db.get_database()
        dbo.locale = o.post["locale"]
        dbo.installpath = PATH
        asm3.dbupdate.install(dbo)
        self.redirect("login")

class faviconico(ASMEndpoint):
    url = "favicon.ico"
    session_cookie = False
    check_logged_in = False

    def content(self, o):
        self.cache_control(CACHE_ONE_HOUR, CACHE_ONE_HOUR)
        self.redirect("static/images/logo/icon-16.png")

class image(ASMEndpoint):
    url = "image"
    user_activity = False
    session_cookie = False # Disable sending the cookie with the response to assist with CDN caching

    def content(self, o):
        try:
            # Use a read through disk cache for thumbnails.
            # This saves on database calls and thumbnail scaling for busier sites.
            # We only cache if a date parameter is specified so that changing the date can invalidate the cache.
            cache_indicator = ""
            if o.post["date"] != "" and o.post["mode"].endswith("thumb"):
                cache_key = "%s:id=%s:seq=%s:date=%s" % ( o.post["mode"], o.post["id"], o.post.integer("seq"), o.post["date"])
                cache_path = o.dbo.name()
                imagedata = asm3.cachedisk.get(cache_key, cache_path)
                cache_indicator = asm3.utils.iif(imagedata is None, "", " from cache")
                if imagedata is None:
                    lastmod, imagedata = asm3.media.get_image_file_data(o.dbo, o.post["mode"], o.post["id"], o.post.integer("seq"), False)
                    if len(imagedata) > 50: # Never cache empty/broken thumbnails
                        asm3.cachedisk.put(cache_key, cache_path, imagedata, CACHE_ONE_WEEK)
            else:
                lastmod, imagedata = asm3.media.get_image_file_data(o.dbo, o.post["mode"], o.post["id"], o.post.integer("seq"), False)
        except Exception as err:
            # The call to get_image_file_data can produce a lot of errors when people try to access 
            # images via unsubstituted tokens in documents, etc. 
            # Log them and rethrow an error that won't end up in our unhandled error box
            msg = str(err)
            if hasattr(err, "msg"): msg = err.msg # Our custom exceptions like DBFSError, ASMError, etc all have a msg attribute
            asm3.al.error(msg, "main.image", o.dbo, sys.exc_info())
            raise asm3.utils.ASMError("failure retrieving image")

        if imagedata != b"NOPIC":
            self.content_type("image/jpeg")
            if o.post["date"] != "":
                # if we have a date parameter, it can be used to invalidate any cache, so cache on the client for a long time
                self.cache_control(CACHE_ONE_YEAR)
            else:
                # otherwise cache for an hour in CDNs and just for the day locally
                self.cache_control(CACHE_ONE_DAY, CACHE_ONE_HOUR)
            asm3.al.debug("mode=%s id=%s seq=%s (%s bytes%s)" % (o.post["mode"], o.post["id"], o.post["seq"], len(imagedata), cache_indicator), "image.content", o.dbo)
            return imagedata
        else:
            # If a parameter of nopic=404 is passed, we return a 404 instead of redirecting to nopic
            if o.post["nopic"] == "404": self.notfound()
            self.redirect("image?db=%s&mode=nopic" % o.dbo.name())

class configjs(ASMEndpoint):
    url = "config.js"
    check_logged_in = False
    user_activity = False

    def content(self, o):
        # db is the database name and ts is the date/time the config was
        # last read upto. The ts value (config_ts) is set during login and
        # updated whenever the user posts to publish_options or options.
        # Both values are used purely to cache the config in the browser, but
        # aren't actually used by the controller here.
        # post = asm3.utils.PostedData(web.input(db = "", ts = ""), o.locale)
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
        if asm3.smcom.active():
            expirydate = asm3.smcom.get_expiry_date(dbo)
            if expirydate is not None: 
                expirydatedisplay = python2display(o.locale, expirydate)
                expirydate = expirydate.isoformat()
        us = asm3.users.get_users(dbo, o.user)
        if len(us) > 0:
            emailaddress = asm3.utils.nulltostr(us[0]["EMAILADDRESS"])
            realname = asm3.utils.nulltostr(us[0]["REALNAME"])
        mapprovider = MAP_PROVIDER
        mapprovidero = asm3.configuration.map_provider_override(dbo)
        mapproviderkey = MAP_PROVIDER_KEY
        mapproviderkeyo = asm3.configuration.map_provider_key_override(dbo)
        if mapprovidero != "": mapprovider = mapprovidero
        if mapproviderkeyo != "": mapproviderkey = mapproviderkeyo
        maplink = MAP_LINK
        maplinko = asm3.configuration.map_link_override(dbo)
        if maplinko != "": maplinko = maplink
        osmmaptiles = OSM_MAP_TILES
        osmmaptileso = asm3.configuration.osm_map_tiles_override(dbo)
        if osmmaptileso != "": osmmaptiles = osmmaptileso
        c = { "baseurl": BASE_URL,
            "serviceurl": SERVICE_URL,
            "build": BUILD,
            "locale": o.locale,
            "theme": o.session.theme,
            "user": o.session.user,
            "useremail": emailaddress,
            "userreal": realname,
            "useraccount": dbo.name(),
            "useraccountalias": dbo.alias,
            "dateformat": get_display_date_format(o.locale),
            "currencysymbol": get_currency_symbol(o.locale),
            "currencydp": get_currency_dp(o.locale),
            "currencyprefix": get_currency_prefix(o.locale),
            "currencyradix": get_currency_radix(o.locale),
            "currencydigitgrouping": get_currency_digit_grouping(o.locale),
            "securitymap": o.session.securitymap,
            "superuser": o.session.superuser,
            "locationfilter": o.session.locationfilter,
            "siteid": o.session.siteid,
            "roles": o.session.roles,
            "roleids": o.session.roleids,
            "manualhtml": MANUAL_HTML_URL,
            "manualpdf": MANUAL_PDF_URL,
            "manualfaq": MANUAL_FAQ_URL,
            "manualvideo": MANUAL_VIDEO_URL,
            "microchipmanufacturers": asm3.lookups.get_microchip_prefixes(),
            "smcom": asm3.smcom.active(),
            "smcomexpiry": expirydate,
            "smcomexpirydisplay": expirydatedisplay,
            "smcompaymentlink": SMCOM_PAYMENT_LINK.replace("{alias}", dbo.alias).replace("{database}", dbo.name()),
            "jqueryuicss": JQUERY_UI_CSS,
            "leafletcss": LEAFLET_CSS,
            "leafletjs": LEAFLET_JS,
            "maplink": maplink,
            "mapprovider": mapprovider,
            "mapproviderkey": mapproviderkey,
            "osmmaptiles": osmmaptiles,
            "hascustomlogo": asm3.dbfs.file_exists(dbo, "logo.jpg"),
            "fontfiles": asm3.configuration.watermark_get_valid_font_files(),
            "config": asm3.configuration.get_map(dbo),
            "menustructure": asm3.html.menu_structure(o.locale, 
                asm3.publish.PUBLISHER_LIST,
                asm3.reports.get_reports_menu(dbo, o.session.roleids, o.session.superuser), 
                asm3.reports.get_mailmerges_menu(dbo, o.session.roleids, o.session.superuser)),
            "publishers": asm3.publish.PUBLISHER_LIST
        }
        return "const asm = %s;" % asm3.utils.json(c)

class csperror(ASMEndpoint):
    """
    Target for logging content security policy errors from the frontend
    via the CSP directive: report-uri /csperror
    Nothing is returned as the UI does not expect a response.
    Errors are logged and emailed to the admin if EMAIL_ERRORS is set.
    """
    url = "csperror"
    user_activity = False

    def post_all(self, o):
        asm3.al.error(str(self.data), "main.csperror", o.dbo)
        if EMAIL_ERRORS:
            asm3.utils.send_email(o.dbo, ADMIN_EMAIL, ADMIN_EMAIL, "", "", "CSP violation", str(self.data), "plain", exceptions=False, bulk=True, fromoverride=False)

class jserror(ASMEndpoint):
    """
    Target for logging javascript errors from the frontend.
    Nothing is returned as the UI does not expect a response.
    Errors are logged and emailed to the admin if EMAIL_ERRORS is set.
    """
    url = "jserror"
    user_activity = False

    def post_all(self, o):
        dbo = o.dbo
        post = o.post
        emailsubject = "%s @ %s" % (post["user"], post["account"])
        emailbody = "%s:\n\n%s\n\nUA: %s\nIP: %s" % (post["msg"], post["stack"], self.user_agent(), self.remote_ip())
        logmess = "%s@%s: %s %s" % (post["user"], post["account"], post["msg"], post["stack"])
        asm3.al.error(logmess, "main.jserror", dbo)
        if EMAIL_ERRORS:
            asm3.utils.send_email(dbo, ADMIN_EMAIL, ADMIN_EMAIL, "", "", emailsubject, emailbody, "plain", exceptions=False, bulk=True, fromoverride=False)

class custom_logo(ASMEndpoint):
    url = "custom_logo"
    check_logged_in = False

    def content(self, o):
        try:
            dbo = o.dbo
            self.content_type("image/jpeg")
            self.cache_control(CACHE_ONE_DAY, 120)
            return asm3.dbfs.get_string_filepath(dbo, "/reports/logo.jpg")
        except Exception as err:
            asm3.al.error("%s" % str(err), "main.custom_logo", dbo)
            return ""

class custom_splash(ASMEndpoint):
    url = "custom_splash"
    check_logged_in = False

    def content(self, o):
        try:
            dbo = asm3.db.get_database(o.post["smaccount"])
            self.content_type("image/jpeg")
            self.cache_control(CACHE_ONE_DAY, 120)
            return asm3.dbfs.get_string_filepath(dbo, "/reports/splash.jpg")
        except Exception as err:
            asm3.al.error("%s" % str(err), "main.custom_splash", dbo)
            return ""

class media(ASMEndpoint):
    url = "media"

    def content(self, o):
        lastmod, medianame, mimetype, filedata = asm3.media.get_media_file_data(o.dbo, o.post.integer("id"))
        self.content_type(mimetype)
        self.content_disposition("inline", medianame)
        self.cache_control(CACHE_ONE_DAY)
        asm3.al.debug("%s %s (%s bytes)" % (medianame, mimetype, len(filedata)), "media.content", o.dbo)
        return filedata

    def post_create(self, o):
        self.check(asm3.users.ADD_MEDIA)
        linkid = o.post.integer("linkid")
        linktypeid = o.post.integer("linktypeid")
        sourceid = o.post.integer("sourceid")
        asm3.media.attach_file_from_form(o.dbo, o.user, linktypeid, linkid, sourceid, o.post)
        self.redirect("%s?id=%d" % (o.post["controller"], linkid))

    def post_createdoc(self, o):
        self.check(asm3.users.ADD_MEDIA)
        linkid = o.post.integer("linkid")
        linktypeid = o.post.integer("linktypeid")
        mediaid = asm3.media.create_blank_document_media(o.dbo, o.user, linktypeid, linkid)
        self.redirect("document_media_edit?id=%d&redirecturl=%s?id=%d" % (mediaid, o.post["controller"], linkid))

    def post_createlink(self, o):
        self.check(asm3.users.ADD_MEDIA)
        linkid = o.post.integer("linkid")
        linktypeid = o.post.integer("linktypeid")
        asm3.media.attach_link_from_form(o.dbo, o.user, linktypeid, linkid, o.post)
        self.redirect("%s?id=%d" % (o.post["controller"], linkid))

    def post_update(self, o):
        self.check(asm3.users.CHANGE_MEDIA)
        asm3.media.update_media_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_MEDIA)
        for mid in o.post.integer_list("ids"):
            asm3.media.delete_media(o.dbo, o.user, mid)

    def post_email(self, o):
        self.check(asm3.users.EMAIL_PERSON)
        dbo = o.dbo
        post = o.post
        emailadd = post["to"]
        attachments = []
        subject = [ post["subject"] ]
        linktypeid = 0
        linkid = 0
        # handle attaching selected media files
        for mid in post.integer_list("ids"):
            m = asm3.media.get_media_by_id(dbo, mid)
            filename = asm3.media._get_media_filename(m)
            if m is None: self.notfound()
            linktypeid = m.LINKTYPEID
            linkid = m.LINKID
            content = asm3.dbfs.get_string_id(dbo, m.DBFSID)
            if m.MEDIAMIMETYPE == "text/html":
                content = asm3.utils.bytes2str(content)
                content = asm3.utils.fix_relative_document_uris(dbo, content)
                content = asm3.utils.str2bytes(content)
            attachments.append(( filename, m.MEDIAMIMETYPE, content ))
            subject.append(filename)
        # handle attaching selected repository documents
        for drid in post.integer_list("docrepo"):
            content = asm3.dbfs.get_string_id(dbo, drid)
            filename = asm3.dbfs.get_name_for_id(dbo, drid)
            mimetype = asm3.media.mime_type(filename)
            attachments.append(( filename, mimetype, content))
        asm3.utils.send_email(dbo, post["from"], emailadd, post["cc"], post["bcc"], post["subject"], post["body"], "html", attachments)
        if asm3.configuration.audit_on_send_email(dbo): 
            asm3.audit.email(dbo, o.user, post["from"], emailadd, post["cc"], post["bcc"], post["subject"], post["body"])
        if post.boolean("addtolog"):
            asm3.log.add_log_email(dbo, o.user, asm3.media.get_log_from_media_type(linktypeid), linkid, post.integer("logtype"), 
                emailadd, ", ".join(subject), post["body"])
        return emailadd

    def post_emailpdf(self, o):
        self.check(asm3.users.EMAIL_PERSON)
        dbo = o.dbo
        post = o.post
        emailadd = post["to"]
        attachments = []
        subject = [ post["subject"] ]
        linktypeid = 0
        linkid = 0
        # handle converting/attaching selected media files
        for mid in post.integer_list("ids"):
            m = asm3.media.get_media_by_id(dbo, mid)
            if m is None: self.notfound()
            if m.MEDIAMIMETYPE != "text/html": continue
            linktypeid = m.LINKTYPEID
            linkid = m.LINKID
            content = asm3.utils.bytes2str(asm3.dbfs.get_string_id(dbo, m.DBFSID))
            contentpdf = asm3.utils.html_to_pdf(dbo, content)
            filename = asm3.media._get_media_filename(m).replace(".html", ".pdf")
            attachments.append(( filename, "application/pdf", contentpdf ))
            subject.append(filename)
        # handle attaching selected repository documents
        for drid in post.integer_list("docrepo"):
            content = asm3.dbfs.get_string_id(dbo, drid)
            filename = asm3.dbfs.get_name_for_id(dbo, drid)
            mimetype = asm3.media.mime_type(filename)
            attachments.append(( filename, mimetype, content))
        asm3.utils.send_email(dbo, post["from"], emailadd, post["cc"], post["bcc"], post["subject"], post["body"], "html", attachments)
        if asm3.configuration.audit_on_send_email(dbo): 
            asm3.audit.email(dbo, o.user, post["from"], emailadd, post["cc"], post["bcc"], post["subject"], post["body"])
        if post.boolean("addtolog"):
            asm3.log.add_log_email(dbo, o.user, asm3.media.get_log_from_media_type(linktypeid), linkid, post.integer("logtype"), 
                emailadd, ", ".join(subject), post["body"])
        return emailadd

    def post_emailsign(self, o):
        self.check(asm3.users.EMAIL_PERSON)
        for mid in o.post.integer_list("ids"):
            asm3.media.send_signature_request(o.dbo, o.user, mid, o.post)
        return o.post["to"]

    def post_jpgpdf(self, o):
        self.check(asm3.users.CHANGE_MEDIA)
        for mid in o.post.integer_list("ids"):
            asm3.media.convert_media_jpg2pdf(o.dbo, o.user, mid)

    def post_copyanimal(self, o):
        self.check(asm3.users.ADD_MEDIA)
        for mid in o.post.integer_list("ids"):
            asm3.media.clone_media(o.dbo, o.user, mid, asm3.media.ANIMAL, o.post.integer("animalid"))

    def post_copyperson(self, o):
        self.check(asm3.users.ADD_MEDIA)
        for mid in o.post.integer_list("ids"):
            asm3.media.clone_media(o.dbo, o.user, mid, asm3.media.PERSON, o.post.integer("personid"))

    def post_moveanimal(self, o):
        self.check(asm3.users.CHANGE_MEDIA)
        for mid in o.post.integer_list("ids"):
            asm3.media.update_media_link(o.dbo, o.user, mid, asm3.media.ANIMAL, o.post.integer("animalid"))

    def post_moveperson(self, o):
        self.check(asm3.users.CHANGE_MEDIA)
        for mid in o.post.integer_list("ids"):
            asm3.media.update_media_link(o.dbo, o.user, mid, asm3.media.PERSON, o.post.integer("personid"))

    def post_sign(self, o):
        self.check(asm3.users.CHANGE_MEDIA)
        for mid in o.post.integer_list("ids"):
            asm3.media.sign_document(o.dbo, o.user, mid, o.post["sig"], o.post["signdate"], "signscreen")

    def post_signpad(self, o):
        asm3.configuration.signpad_ids(o.dbo, o.user, o.post["ids"])

    def post_rotateclock(self, o):
        self.check(asm3.users.CHANGE_MEDIA)
        for mid in o.post.integer_list("ids"):
            asm3.media.rotate_media(o.dbo, o.user, mid, True)

    def post_rotateanti(self, o):
        self.check(asm3.users.CHANGE_MEDIA)
        for mid in o.post.integer_list("ids"):
            asm3.media.rotate_media(o.dbo, o.user, mid, False)

    def post_watermark(self, o):
        self.check(asm3.users.CHANGE_MEDIA)
        for mid in o.post.integer_list("ids"):
            asm3.media.watermark_media(o.dbo, o.user, mid)

    def post_web(self, o):
        self.check(asm3.users.CHANGE_MEDIA)
        mid = o.post.integer_list("ids")[0]
        asm3.media.set_web_preferred(o.dbo, o.user, mid)

    def post_video(self, o):
        self.check(asm3.users.CHANGE_MEDIA)
        mid = o.post.integer_list("ids")[0]
        asm3.media.set_video_preferred(o.dbo, o.user, mid)

    def post_doc(self, o):
        self.check(asm3.users.CHANGE_MEDIA)
        mid = o.post.integer_list("ids")[0]
        asm3.media.set_doc_preferred(o.dbo, o.user, mid)

    def post_include(self, o):
        self.check(asm3.users.CHANGE_MEDIA)
        for mid in o.post.integer_list("ids"):
            asm3.media.set_excluded(o.dbo, o.user, mid, 0)

    def post_exclude(self, o):
        self.check(asm3.users.CHANGE_MEDIA)
        for mid in o.post.integer_list("ids"):
            asm3.media.set_excluded(o.dbo, o.user, mid, 1)

class mobile(ASMEndpoint):
    url = "mobile"
    login_url = "mobile_login"

    def content(self, o):
        dbo = o.dbo
        animals = asm3.animal.get_shelterview_animals(dbo, o.lf)
        asm3.al.debug("mobile for '%s' (%s animals)" % (o.user, len(animals)), "main.mobile", dbo)

        c = {
            "animals":      animals,
            "reports":      asm3.reports.get_available_reports(dbo),
            "vaccinations": asm3.medical.get_vaccinations_outstanding(dbo, "m31", o.lf),
            "tests":        asm3.medical.get_tests_outstanding(dbo, "m31", o.lf),
            "medicals":     asm3.medical.get_treatments_outstanding(dbo, "m31", o.lf),
            "diaries":      asm3.diary.get_uncompleted_upto_today(dbo, o.user),
            "rsvhomecheck": asm3.person.get_reserves_without_homechecks(dbo),
            "messages":     asm3.lookups.get_messages(dbo, o.user, o.session.roles, o.session.superuser),
            "testresults":  asm3.lookups.get_test_results(dbo),
            "stocklocations": asm3.stock.get_stock_locations_totals(dbo),
            "incidentsmy":  asm3.animalcontrol.get_animalcontrol_find_advanced(dbo, { "dispatchedaco": o.user, "filter": "incomplete" }, o.user),
            "incidentsundispatched": asm3.animalcontrol.get_animalcontrol_find_advanced(dbo, { "dispatchedaco": o.user, "filter": "undispatched" }, o.user),
            "incidentsincomplete": asm3.animalcontrol.get_animalcontrol_find_advanced(dbo, { "filter": "incomplete" }, o.user),
            "incidentsfollowup": asm3.animalcontrol.get_animalcontrol_find_advanced(dbo, { "filter": "requirefollowup" }, o.user),
            "maplink":      MAP_LINK,
            "animaltypes":  asm3.lookups.get_animal_types(dbo),
            "breeds":       asm3.lookups.get_breeds_by_species(dbo),
            "colours":      asm3.lookups.get_basecolours(dbo),
            "completedtypes": asm3.lookups.get_incident_completed_types(dbo),
            "incidenttypes": asm3.lookups.get_incident_types(dbo),
            "internallocations": asm3.lookups.get_internal_locations(dbo, o.lf),
            "logtypes":     asm3.lookups.get_log_types(dbo),
            "sexes":        asm3.lookups.get_sexes(dbo),
            "sizes":        asm3.lookups.get_sizes(dbo),
            "smdblocked":   asm3.configuration.smdb_locked(dbo),
            "species":      asm3.lookups.get_species(dbo),
            "timeline":     asm3.animal.get_timeline(dbo, 30, age=300),
            "usersandroles": asm3.users.get_users_and_roles(dbo),
            "user":         o.user,
            "locale":       o.locale
        }
        self.content_type("text/html")
        return asm3.html.mobile_page(o.locale, "", [ "common.js", "common_html.js", "mobile.js", 
            "mobile_ui_addanimal.js", "mobile_ui_animal.js", "mobile_ui_image.js", "mobile_ui_incident.js", 
            "mobile_ui_person.js", "mobile_ui_stock.js" ], c)

    def post_addanimal(self, o):
        self.check(asm3.users.ADD_ANIMAL)
        nid, dummy = asm3.animal.insert_animal_from_form(o.dbo, o.post, o.user)
        return asm3.utils.json( asm3.animal.get_animal(o.dbo, nid) )

    def post_addlog(self, o):
        self.check(asm3.users.ADD_LOG)
        asm3.log.add_log(o.dbo, o.user, o.post.integer("linktypeid"), o.post.integer("linkid"), o.post.integer("type"), o.post["comments"])

    def post_addmessage(self, o):
        asm3.lookups.add_message(o.dbo, o.user, asm3.configuration.email_messages(o.dbo) and 1 or 0, o.post["body"], o.post["for"])
        messages = asm3.lookups.get_messages(o.dbo, o.user, o.session.roles, o.session.superuser)
        return asm3.utils.json(messages)

    def post_checklicence(self, o):
        self.check(asm3.users.VIEW_LICENCE)
        rows = asm3.financial.get_licence_find_simple(o.dbo, o.post["licencenumber"])
        return asm3.utils.json(rows)

    def post_diarycomplete(self, o):
        self.check(asm3.users.EDIT_MY_DIARY_NOTES)
        asm3.diary.complete_diary_note(o.dbo, o.user, o.post.integer("id"))

    def post_findperson(self, o):
        self.check(asm3.users.VIEW_PERSON)
        rows = asm3.person.get_person_find_simple(o.dbo, o.post["q"], o.user, limit=100, siteid=o.siteid)
        return asm3.utils.json(rows)

    def post_getstocklevel(self, o):
        self.check(asm3.users.VIEW_STOCKLEVEL)
        return asm3.utils.json( 
            { "levels": asm3.stock.get_stocklevels(o.dbo, o.post.integer("id")), 
              "usagetypes": asm3.lookups.get_stock_usage_types(o.dbo) })

    def post_homecheck(self, o):
        self.check(asm3.users.CHANGE_PERSON)
        asm3.person.update_pass_homecheck(o.dbo, o.user, o.post["id"], "")

    def post_inccomplete(self, o):
        self.check(asm3.users.CHANGE_INCIDENT)
        asm3.animalcontrol.update_animalcontrol_completenow(o.dbo, o.post.integer("id"), o.user, o.post.integer("ctype"))

    def post_incdispatch(self, o):
        self.check(asm3.users.CHANGE_INCIDENT)
        asm3.animalcontrol.update_animalcontrol_dispatchnow(o.dbo, o.post.integer("id"), o.user)

    def post_increspond(self, o):
        self.check(asm3.users.CHANGE_INCIDENT)
        asm3.animalcontrol.update_animalcontrol_respondnow(o.dbo, o.post.integer("id"), o.user)
    
    def post_incfollowup(self, o):
        self.check(asm3.users.CHANGE_INCIDENT)
        asm3.animalcontrol.update_animalcontrol_followupnow(o.dbo, o.post.integer("id"), o.user)

    def post_medical(self, o):
        self.check(asm3.users.CHANGE_MEDICAL)
        asm3.medical.update_treatment_today(o.dbo, o.user, o.post.integer("id"))

    def post_stocktake(self, o):
        self.check(asm3.users.CHANGE_STOCKLEVEL)
        asm3.stock.stock_take_from_mobile_form(o.dbo, o.user, o.post)

    def post_test(self, o):
        self.check(asm3.users.CHANGE_TEST)
        asm3.medical.update_test_today(o.dbo, o.user, o.post.integer("id"), o.post.integer("resultid"))

    def post_vaccinate(self, o):
        self.check(asm3.users.CHANGE_VACCINATION)
        asm3.medical.update_vaccination_today(o.dbo, o.user, o.post.integer("id"))

    def post_loadanimal(self, o):
        self.check(asm3.users.VIEW_ANIMAL)
        l = o.locale
        dbo = o.dbo
        pid = o.post.integer("id")
        self.content_type("application/json")
        af = asm3.additional.get_additional_fields(dbo, pid, "animal")
        afout = []
        if len(af) > 0:
            for d in af:
                if d["FIELDTYPE"] == asm3.additional.ANIMAL_LOOKUP:
                    afout.append({ "NAME": d["FIELDLABEL"], "VALUE": asm3.animal.get_animal_namecode(dbo, asm3.utils.cint(d["VALUE"]))})
                elif d["FIELDTYPE"] == asm3.additional.PERSON_LOOKUP:
                    afout.append({ "NAME": d["FIELDLABEL"], "VALUE": asm3.person.get_person_name_code(dbo, asm3.utils.cint(d["VALUE"]))})
                elif d["FIELDTYPE"] == asm3.additional.MONEY:
                    afout.append({ "NAME": d["FIELDLABEL"], "VALUE": format_currency(l, d["VALUE"]) })
                elif d["FIELDTYPE"] == asm3.additional.YESNO:
                    afout.append({ "NAME": d["FIELDLABEL"], "VALUE": d["VALUE"] == "1" and _("Yes", l) or _("No", l) })
                else:
                    afout.append({ "NAME": d["FIELDLABEL"], "VALUE": d["VALUE"] })
        return asm3.utils.json({
            "animal": asm3.animal.get_animal(dbo, pid),
            "additional": afout,
            "diary": asm3.diary.get_diaries(dbo, asm3.diary.ANIMAL, pid),
            "diets": asm3.animal.get_diets(dbo, pid),
            "vaccinations": asm3.medical.get_vaccinations(dbo, pid),
            "tests": asm3.medical.get_tests(dbo, pid),
            "medicals": asm3.medical.get_regimens(dbo, pid),
            "logs": asm3.log.get_logs(dbo, asm3.log.ANIMAL, pid),
            "media": asm3.media.get_media(dbo, asm3.media.ANIMAL, pid)
        })

    def post_loadincident(self, o):
        self.check(asm3.users.VIEW_INCIDENT)
        dbo = o.dbo
        pid = o.post.integer("id")
        self.content_type("application/json")
        return asm3.utils.json({
            "animalcontrol": asm3.animalcontrol.get_animalcontrol(dbo, pid),
            "animals": asm3.animalcontrol.get_animalcontrol_animals(dbo, pid),
            "citations": asm3.financial.get_incident_citations(dbo, pid),
            "diary": asm3.diary.get_diaries(dbo, asm3.diary.ANIMALCONTROL, pid),
            "logs": asm3.log.get_logs(dbo, asm3.log.ANIMALCONTROL, pid),
            "media": asm3.media.get_media(dbo, asm3.media.ANIMALCONTROL, pid)
        })

    def post_loadperson(self, o):
        self.check(asm3.users.VIEW_PERSON)
        l = o.locale
        dbo = o.dbo
        pid = o.post.integer("id")
        self.content_type("application/json")
        af = asm3.additional.get_additional_fields(dbo, pid, "person")
        afout = []
        if len(af) > 0:
            for d in af:
                if d["FIELDTYPE"] == asm3.additional.ANIMAL_LOOKUP:
                    afout.append({ "NAME": d["FIELDLABEL"], "VALUE": asm3.animal.get_animal_namecode(dbo, asm3.utils.cint(d["VALUE"]))})
                elif d["FIELDTYPE"] == asm3.additional.PERSON_LOOKUP:
                    afout.append({ "NAME": d["FIELDLABEL"], "VALUE": asm3.person.get_person_name_code(dbo, asm3.utils.cint(d["VALUE"]))})
                elif d["FIELDTYPE"] == asm3.additional.MONEY:
                    afout.append({ "NAME": d["FIELDLABEL"], "VALUE": format_currency(l, d["VALUE"]) })
                elif d["FIELDTYPE"] == asm3.additional.YESNO:
                    afout.append({ "NAME": d["FIELDLABEL"], "VALUE": d["VALUE"] == "1" and _("Yes", l) or _("No", l) })
                else:
                    afout.append({ "NAME": d["FIELDLABEL"], "VALUE": d["VALUE"] })
        return asm3.utils.json({
            "additional": afout,
            "citations": asm3.financial.get_person_citations(dbo, pid),
            "diary": asm3.diary.get_diaries(dbo, asm3.diary.PERSON, pid),
            "licences": asm3.financial.get_person_licences(dbo, pid),
            "links": asm3.person.get_links(dbo, pid),
            "logs": asm3.log.get_logs(dbo, asm3.log.PERSON, pid),
            "person": asm3.person.get_person(dbo, pid)
            #"movements": asm3.movement.get_person_movements(dbo, pid)
        })

class mobile_login(ASMEndpoint):
    url = "mobile_login"
    check_logged_in = False

    def content(self, o):
        l = o.locale
        if not MULTIPLE_DATABASES:
            dbo = asm3.db.get_database()
            o.locale = asm3.configuration.locale(dbo)
        database = o.post["smaccount"]
        username = o.post["username"]
        password = o.post["password"]
        # Do we have a remember me token?
        rmtoken = self.get_cookie("asm_remember_me")
        if rmtoken:
            cred = asm3.cachemem.get(rmtoken)
            if cred and cred.find("|") != -1 and cred.count("|") == 2:
                database, username, password = cred.split("|")
                rpost = asm3.utils.PostedData({ "database": database, "username": username, "password": password }, LOCALE)
                asm3.al.info("attempting auth with remember me token for %s/%s" % (database, username), "main.mobile_login")
                user = asm3.users.web_login(rpost, session, self.remote_ip(), self.user_agent(), PATH, use2fa = False)
                if user not in ( "FAIL", "DISABLED", "WRONGSERVER" ):
                    self.redirect("mobile")
                    return
        # Do we have base64 encoded credentials?
        if o.post["b"] != "":
            cred = ""
            try:
                cred = asm3.utils.base64decode_str(o.post["b"])
            except Exception as err:
                asm3.al.error("failed decoding base64 credentials: %s (%s)" % (o.post["b"], err), "main.mobile_login")
            if cred and cred.find("|") != -1 and cred.count("|") == 3:
                database, username, password, rememberme = cred.split("|")
                rpost = asm3.utils.PostedData({ "database": database, "username": username, "password": password, "rememberme": rememberme }, LOCALE)
                asm3.al.info("attempting auth with base64 token for %s/%s" % (database, username), "main.mobile_login")
                user = asm3.users.web_login(rpost, session, self.remote_ip(), self.user_agent(), PATH)
                if user not in ( "FAIL", "DISABLED", "WRONGSERVER", "ASK2FA" ):
                    self.redirect("mobile")
                    return
        self.content_type("text/html")
        c = {
            "smcom": asm3.smcom.active(),
            "smcomloginurl": SMCOM_LOGIN_URL,
            "multipledatabases": MULTIPLE_DATABASES,
            "target": o.post["target"],
            "smaccount": database,
            "username": username,
            "password": password
        }
        return asm3.html.mobile_page(l, _("Login"), [ "mobile_login.js" ], c)

class mobile_logout(ASMEndpoint):
    url = "mobile_logout"
    check_logged_in = False

    def content(self, o):
        url = "mobile_login"
        if o.post["smaccount"] != "":
            url = "mobile_login?smaccount=" + o.post["smaccount"]
        elif MULTIPLE_DATABASES and o.dbo is not None and o.dbo.alias is not None:
            url = "mobile_login?smaccount=" + o.dbo.alias
        asm3.users.update_user_activity(o.dbo, o.user, False)
        asm3.users.logout(o.session, self.remote_ip(), self.user_agent())
        self.set_cookie("asm_remember_me", "", 0) # user explicitly logged out, remove remember me
        self.redirect(url)

class mobile_photo_upload(ASMEndpoint):
    url = "mobile_photo_upload"
    login_url = "/mobile_login"

    def content(self, o):
        dbo = o.dbo
        l = o.locale
        self.content_type("text/html")
        animalsos = asm3.animal.get_animals_on_shelter_namecode(dbo, remove_units=True, lf=o.lf)
        # Only include recently adopted animals if the user either has no location filter, or
        # has a location filter that includes adopted animals
        animalsra = []
        if o.lf is not None and o.lf.locationfilter != "" and o.lf.locationfilter.find("-1") == -1:
            animalsra = asm3.animal.get_animals_adopted_namecode(dbo, remove_adopter=True)
        litters = asm3.animal.get_active_litters_brief(dbo)
        c = {
            "animals":  animalsos + animalsra,
            "litters":  litters
        }
        return asm3.html.mobile_page(l, _("Photo Uploader", l), [ "mobile_photo_uploader.js" ], c)

    def attach_animal_file(self, o, animalid):
        mid = asm3.media.attach_file_from_form(o.dbo, o.user, asm3.media.ANIMAL, animalid, asm3.media.MEDIASOURCE_MOBILEUI, o.post)
        if o.post["type"] == "paperwork":
            asm3.media.convert_media_jpg2pdf(o.dbo, o.user, mid)
            asm3.media.delete_media(o.dbo, o.user, mid)
        return mid
    
    def attach_incident_file(self, o, incidentid):
        mid = asm3.media.attach_file_from_form(o.dbo, o.user, asm3.media.ANIMALCONTROL, incidentid, asm3.media.MEDIASOURCE_MOBILEUI, o.post)
        if o.post["type"] == "paperwork":
            asm3.media.convert_media_jpg2pdf(o.dbo, o.user, mid)
            asm3.media.delete_media(o.dbo, o.user, mid)
        return mid

    def post_all(self, o):
        dbo = o.dbo
        if "incidentid" in o.post:
            mid = self.attach_incident_file(o, o.post.integer("incidentid"))
            return str(mid)
        if "litterid" in o.post:
            littermates = asm3.animal.get_litter_animals_by_id(dbo, o.post["litterid"])
            for lm in littermates:
                mid = self.attach_animal_file(o, lm.ID)
        else: 
            mid = self.attach_animal_file(o, o.post.integer("animalid"))
        return str(mid)

class mobile_report(ASMEndpoint):
    url = "mobile_report"
    login_url = "mobile_login"
    get_permissions = asm3.users.VIEW_REPORT

    def content(self, o):
        dbo = o.dbo
        post = o.post
        crid = post.integer("id")
        # Make sure this user has a role that can view the report
        asm3.reports.check_view_permission(o.session, crid)
        crit = asm3.reports.get_criteria(dbo, crid) 
        self.content_type("text/html")
        self.cache_control(0)
        # If this report takes criteria and none were supplied, go to the criteria screen instead to get them
        if len(crit) != 0 and post["hascriteria"] == "": self.redirect("mobile_report_criteria?id=%s" % post.integer("id"))
        title = asm3.reports.get_title(dbo, crid)
        asm3.al.debug("got criteria (%s), executing report %d" % (str(post.data), crid), "main.report", dbo)
        p = asm3.reports.get_criteria_params(dbo, crid, post)
        if asm3.configuration.audit_on_view_report(dbo):
            asm3.audit.view_report(dbo, o.user, crid, title, str(post.data))
        s = asm3.reports.execute(dbo, crid, o.user, p)
        return s

class mobile_report_criteria(ASMEndpoint):
    url = "mobile_report_criteria"
    get_permissions = asm3.users.VIEW_REPORT

    def content(self, o):
        dbo = o.dbo
        crid = o.post.integer("id")
        crit = asm3.reports.get_criteria(dbo, crid) 
        title = asm3.reports.get_title(dbo, crid)
        self.content_type("text/html")
        self.cache_control(0)
        def has_criteria(c):
            for name, rtype, question in crit:
                if rtype == c: return True
            return False
        asm3.al.debug("building criteria form for report %d %s" % (crid, title), "main.mobile_report", dbo)
        c = {
            "crid":         crid,
            "criteria":     crit,
            "title":        title,
            "user":         o.user
        }
        # Only load lookup items for criteria that need them to save bandwidth
        if has_criteria("ANIMAL") or has_criteria("FSANIMAL") or has_criteria("ALLANIMAL") or has_criteria("ANIMALS"):
            c["animals"] = asm3.animal.get_animals_on_shelter_namecode(dbo)
        if has_criteria("ANIMALFLAG"): c["animalflags"] = asm3.lookups.get_animal_flags(dbo)
        if has_criteria("DONATIONTYPE") or has_criteria("PAYMENTTYPE"): c["donationtypes"] = asm3.lookups.get_donation_types(dbo)
        if has_criteria("ENTRYCATEGORY"): c["entryreasons"] = asm3.lookups.get_entryreasons(dbo)
        if has_criteria("LITTER"): c["litters"] = asm3.animal.get_active_litters_brief(dbo)
        if has_criteria("LOCATION"): c["locations"] = asm3.lookups.get_internal_locations(dbo, o.lf)
        if has_criteria("LOGTYPE"): c["logtypes"] = asm3.lookups.get_log_types(dbo)
        if has_criteria("MEDIAFLAG"): c["mediaflags"] = asm3.lookups.get_media_flags(dbo)
        if has_criteria("PAYMENTMETHOD") or has_criteria("PAYMENTTYPE"): c["paymentmethods"] = asm3.lookups.get_payment_methods(dbo)
        if has_criteria("PERSON"): c["people"] = asm3.person.get_person_name_addresses(dbo)
        if has_criteria("PERSONFLAG"): c["personflags"] = asm3.lookups.get_person_flags(dbo)
        if has_criteria("SITE"): c["sites"] = asm3.lookups.get_sites(dbo)
        if has_criteria("SPECIES"): c["species"] = asm3.lookups.get_species(dbo)
        if has_criteria("TYPE"): c["types"] = asm3.lookups.get_animal_types(dbo)
        self.content_type("text/html")
        return asm3.html.mobile_page(o.locale, "", [ "common.js", "common_html.js", "mobile_report.js" ], c)

class mobile_sign(ASMEndpoint):
    url = "mobile_sign"
    login_url = "/mobile_login"

    def content(self, o):
        self.content_type("text/html")
        ids = asm3.configuration.signpad_ids(o.dbo, o.user)
        names = []
        preview = []
        for mid in ids.strip().split(","):
            if mid.strip() != "": 
                names.append(asm3.media.get_notes_for_id(o.dbo, int(mid)))
                dummy, dummy, dummy, contents = asm3.media.get_media_file_data(o.dbo, int(mid))
                preview.append(asm3.utils.bytes2str(contents))
        l = o.dbo.locale
        c = {
            "ids": ids,
            "count": len(names),
            "names": ", ".join(names),
            "preview": "\n<hr/>\n".join(preview)
        }
        return asm3.html.mobile_page(l, _("Signing Pad", l), [ "mobile_sign.js" ], c)

    def post_all(self, o):
        for mid in o.post.integer_list("ids"):
            asm3.media.sign_document(o.dbo, o.user, mid, o.post["sig"], o.post["signdate"], "signmobile")
        asm3.configuration.signpad_ids(o.dbo, o.user, "")

class main(JSONEndpoint):
    url = "main"

    def controller(self, o):
        dbo = o.dbo
        # If a b (build) parameter was passed to indicate the client wants to
        # get the latest js files, invalidate the config so that the
        # frontend doesn't keep receiving the same build number via configjs 
        # and get into an endless loop of reloads
        if o.post["b"] != "": self.reload_config()
        # Database update checks
        dbupdated = ""
        if asm3.dbupdate.check_for_updates(dbo):
            dbupdated = asm3.dbupdate.perform_updates(dbo)
        if asm3.dbupdate.check_for_view_seq_changes(dbo):
            asm3.dbupdate.install_db_views(dbo)
            asm3.dbupdate.install_db_sequences(dbo)
            asm3.dbupdate.install_db_stored_procedures(dbo)
        # Welcome dialog
        showwelcome = False
        if asm3.configuration.show_first_time_screen(dbo) and o.session.superuser == 1:
            showwelcome = True
        # News (text file on disk that is retrieved as part of the batch)
        news = asm3.utils.get_asm_news(dbo)
        # Use a 5 minute cache, with a longer cache time of 15 minutes for big databases
        # on the following calls for links, stats, alerts and the timeline
        age = 300
        if dbo.is_large_db: age = 900
        # Animal links 
        linkmode = asm3.configuration.main_screen_animal_link_mode(dbo)
        linkmax = asm3.configuration.main_screen_animal_link_max(dbo)
        animallinks = []
        if linkmode == "adoptable":
            animallinks = asm3.animal.get_links_adoptable(dbo, o.lf, linkmax, age)
        elif linkmode == "longestonshelter":
            animallinks = asm3.animal.get_links_longest_on_shelter(dbo, o.lf, linkmax, age)
        elif linkmode == "recentlyadopted":
            animallinks = asm3.animal.get_links_recently_adopted(dbo, o.lf, linkmax, age)
        elif linkmode == "recentlychanged":
            animallinks = asm3.animal.get_links_recently_changed(dbo, o.lf, linkmax, age)
        elif linkmode == "recentlyentered":
            animallinks = asm3.animal.get_links_recently_entered(dbo, o.lf, linkmax, age)
        elif linkmode == "recentlyfostered":
            animallinks = asm3.animal.get_links_recently_fostered(dbo, o.lf, linkmax, age)
        # Alerts
        alerts = []
        if asm3.configuration.show_alerts_home_page(dbo):
            alerts = asm3.animal.get_alerts(dbo, o.lf, age=age)
            if len(alerts) > 0: 
                alerts[0]["LOOKFOR"] = asm3.cachedisk.get("lookingfor_lastmatchcount", dbo.name())
                alerts[0]["LOSTFOUND"] = asm3.cachedisk.get("lostfound_lastmatchcount", dbo.name())
        # Overview
        overview = {}
        if asm3.configuration.show_overview_home_page(dbo):
            overview = asm3.animal.get_overview(dbo, age=age)
        # Stats
        stats = []
        if asm3.configuration.show_stats_home_page(dbo) != "none":
            stats = asm3.animal.get_stats(dbo, age=age)
        # Timeline
        timeline = []
        if asm3.configuration.show_timeline_home_page(dbo):
            timeline = asm3.animal.get_timeline(dbo, 10, age=age)
        # Users and roles - for adding messages
        usersandroles = asm3.users.get_users_and_roles(dbo)
        # Active users for display (all done through memory cache)
        activeusers = asm3.users.get_active_users(dbo)
        # Messages
        mess = asm3.lookups.get_messages(dbo, o.session.user, o.session.roles, o.session.superuser)
        # Diary Notes
        dm = None
        if asm3.configuration.all_diary_home_page(dbo): 
            dm = asm3.diary.get_uncompleted_upto_today(dbo, "", includecreatedby=False, offset=-365)
        else:
            dm = asm3.diary.get_uncompleted_upto_today(dbo, o.user, includecreatedby=False, offset=-365)
        asm3.al.debug("main for '%s', %d diary notes, %d messages" % (o.user, len(dm), len(mess)), "main.main", dbo)
        return {
            "age": age,
            "showwelcome": showwelcome,
            "build": BUILD,
            "noreload": o.post["b"] != "", 
            "news": news,
            "dbupdated": dbupdated,
            "version": get_version(),
            "emergencynotice": emergency_notice(),
            "linkmode": linkmode,
            "activeusers": activeusers,
            "usersandroles": usersandroles,
            "alerts": alerts,
            "overview": overview,
            "recent": timeline,
            "stats": stats,
            "animallinks": animallinks,
            "diary": dm,
            "mess": mess 
        }

    def post_addmessage(self, o):
        asm3.lookups.add_message(o.dbo, o.user, o.post.boolean("email"), o.post["message"], o.post["forname"], o.post.integer("priority"), o.post.date("expires"))

    def post_delmessage(self, o):
        asm3.lookups.delete_message(o.dbo, o.post.integer("id"))

    def post_showfirsttimescreen(self, o):
        asm3.configuration.show_first_time_screen(o.dbo, True, False)

class login(ASMEndpoint):
    url = "login"
    check_logged_in = False

    def content(self, o):
        l = LOCALE
        post = o.post
        has_animals = True
        custom_splash = False
        database = post["smaccount"]
        username = post["username"]
        password = post["password"]

        # Filter out Internet Explorer altogether.
        ua = self.user_agent()
        if ua.find("MSIE") != -1 or ua.find("Trident") != -1:
            self.redirect("static/pages/unsupported_ie.html")

        # Figure out how to get the default locale and any overridden splash screen
        # Single database
        if not MULTIPLE_DATABASES:
            dbo = asm3.db.get_database()
            l = asm3.configuration.locale(dbo)
            has_animals = asm3.animal.get_has_animals(dbo)
            custom_splash = asm3.dbfs.file_exists(dbo, "splash.jpg")

        # Multiple databases, account given
        elif MULTIPLE_DATABASES and post["smaccount"] != "":
            dbo = asm3.db.get_database(post["smaccount"])
            if dbo.database == "WRONGSERVER":
                self.redirect(SMCOM_LOGIN_URL)
            elif dbo.database not in asm3.db.ERROR_VALUES:
                custom_splash = asm3.dbfs.file_exists(dbo, "splash.jpg")
                l = asm3.configuration.locale(dbo)

        # Fall back to system locale
        else:
            l = LOCALE

        # Do we have a remember me token?
        rmtoken = self.get_cookie("asm_remember_me")
        if rmtoken:
            cred = asm3.cachemem.get(rmtoken)
            if cred and cred.find("|") != -1 and cred.count("|") == 2:
                database, username, password = cred.split("|")
                rpost = asm3.utils.PostedData({ "database": database, "username": username, "password": password }, LOCALE)
                asm3.al.info("attempting auth with remember me token for %s/%s" % (database, username), "main.login")
                user = asm3.users.web_login(rpost, session, self.remote_ip(), self.user_agent(), PATH, use2fa = False)
                if user not in ( "FAIL", "DISABLED", "WRONGSERVER" ):
                    self.redirect("main")
                    return

        # Do we have base64 encoded credentials?
        if post["b"] != "":
            cred = ""
            try:
                cred = asm3.utils.base64decode_str(post["b"])
            except Exception as err:
                asm3.al.error("failed decoding base64 credentials: %s (%s)" % (post["b"], err), "main.login")
            if cred and cred.find("|") != -1 and cred.count("|") == 3:
                database, username, password, rememberme = cred.split("|")
                rpost = asm3.utils.PostedData({ "database": database, "username": username, "password": password, "rememberme": rememberme }, LOCALE)
                asm3.al.info("attempting auth with base64 token for %s/%s" % (database, username), "main.login")
                user = asm3.users.web_login(rpost, session, self.remote_ip(), self.user_agent(), PATH)
                if user not in ( "FAIL", "DISABLED", "WRONGSERVER", "ASK2FA" ):
                    self.redirect("main")
                    return

        title = _("Animal Shelter Manager Login", l)
        s = asm3.html.bare_header(title, locale = l)
        c = { "smcom": asm3.smcom.active(),
             "multipledatabases": MULTIPLE_DATABASES,
             "locale": l,
             "hasanimals": has_animals,
             "customsplash": custom_splash,
             "emergencynotice": emergency_notice(),
             "smaccount": database, 
             "husername": username,
             "hpassword": password,
             "baseurl": BASE_URL,
             "smcomloginurl": SMCOM_LOGIN_URL,
             "nologconnection": post["nologconnection"],
             "target": post["target"]
        }
        nonce = asm3.utils.uuid_str()
        s += '<script nonce="%s">\ncontroller = %s;\n' % (nonce, asm3.utils.json(c))
        s += '$(document).ready(function() { $("body").append(login.render()); login.bind(); });\n'
        s += 'window.onunload = function() {}; \n' # invalidate Firefox bfcache as login page hides elements after transition to main
        s += '</script>'
        s += asm3.html.footer()
        self.content_type("text/html")
        self.header("X-Frame-Options", "SAMEORIGIN")
        self.header("X-Content-Type-Options", "nosniff") 
        self.header("X-XSS-Protection", "1; mode=block") 
        self.header("Strict-Transport-Security", "max-age=%s" % CACHE_ONE_MONTH) 
        if CONTENT_SECURITY_POLICY != "":
            self.header("Content-Security-Policy", CONTENT_SECURITY_POLICY % { "nonce": nonce })
        return s

    def post_all(self, o):
        user = asm3.users.web_login(o.post, session, self.remote_ip(), self.user_agent(), PATH)
        # If there's a pipe in the result, we have a remember me cookie/token to set
        if user.find("|") != -1:
            user, token = user.split("|")
            self.set_cookie("asm_remember_me", token, CACHE_ONE_MONTH)
        return user

    def post_reset(self, o):
        dbo = asm3.db.get_database(o.post["database"])
        if dbo.database in asm3.db.ERROR_VALUES: return "FAIL"
        asm3.al.info("password reset request from %s for %s:%s" % (self.remote_ip(), o.post["database"], o.post["username"]), "main.login", dbo)
        l = dbo.locale
        # This cannot be used to reset the SM master password
        if asm3.smcom.active() and o.post["username"].lower() == dbo.name():
            asm3.al.error("failed password reset: master user %s cannot be reset here" % o.post["username"], "main.login", dbo)
            return "MASTER"
        # Find the user id and email address for the username given
        user = dbo.first_row(dbo.query("SELECT ID, EmailAddress, DisableLogin FROM users WHERE LOWER(UserName) LIKE ?", [o.post["username"].lower()]))
        if not user or not user.EMAILADDRESS or user.DISABLELOGIN == 1: 
            asm3.al.error("failed password reset: user %s is disabled, does not exist or have an email address" % o.post["username"], "main.login", dbo)
            return "NOEMAIL"
        # Generate a random cache key for this reset
        cache_key = asm3.utils.uuid_str()
        # Store info about this reset in the cache for 10 minutes
        asm3.cachedisk.put(cache_key, "", { "username": o.post["username"], "userid": user.ID,
            "database": o.post["database"], "email": user.EMAILADDRESS }, 600)
        # Construct the reset link
        resetlink = "%s/reset_password?token=%s" % (BASE_URL, cache_key)
        # Send the email
        asm3.utils.send_email(dbo, asm3.configuration.email(dbo), user.EMAILADDRESS, "", "",
            _("Reset password request", l),
            _("To reset your ASM password, please follow this link:", l) + "\n\n" + resetlink + "\n\n" +
            _("This link will remain active for 10 minutes.", l))
        return "OK"

class logout(ASMEndpoint):
    url = "logout"
    check_logged_in = False

    def content(self, o):
        url = "login"
        if o.post["smaccount"] != "":
            url = "login?smaccount=" + o.post["smaccount"]
        elif MULTIPLE_DATABASES and o.dbo is not None and o.dbo.alias is not None:
            url = "login?smaccount=" + o.dbo.alias
        asm3.users.update_user_activity(o.dbo, o.user, False)
        asm3.users.logout(o.session, self.remote_ip(), self.user_agent())
        self.set_cookie("asm_remember_me", "", 0) # user explicitly logged out, remove remember me
        self.redirect(url)

class reset_password(ASMEndpoint):
    url = "reset_password"
    check_logged_in = False

    def content(self, o):
        token = o.post["token"]
        rinfo = asm3.cachedisk.get(token, "")
        if rinfo is None: raise asm3.utils.ASMValidationError("invalid token")
        dbo = asm3.db.get_database(rinfo["database"])
        if dbo.database in asm3.db.ERROR_VALUES: raise asm3.utils.ASMValidationError("bad database")
        # Reset their password to something random and send an email with the new password
        l = dbo.locale
        newpass = asm3.utils.random_password(10)
        asm3.users.reset_password(dbo, rinfo["userid"], newpass)
        asm3.al.info("reset password for %s to %s" % (rinfo["username"], newpass), "main.reset_password", dbo)
        asm3.utils.send_email(dbo, asm3.configuration.email(dbo), rinfo["email"], "", "", 
            _("Reset password request", l),
            _("The ASM password for {0} has been reset to:", l).format(rinfo["username"]) + 
            "\n\n    " + newpass)
        self.redirect("static/pages/password_reset.html")

class accounts(JSONEndpoint):
    url = "accounts"
    get_permissions = asm3.users.VIEW_ACCOUNT

    def controller(self, o):
        dbo = o.dbo
        if o.post["offset"] == "all":
            accounts = asm3.financial.get_accounts(dbo)
        else:
            accounts = asm3.financial.get_accounts(dbo, onlyactive=True)
        asm3.al.debug("got %d accounts" % len(accounts), "main.accounts", dbo)
        return {
            "accounttypes": asm3.lookups.get_account_types(dbo),
            "costtypes": asm3.lookups.get_costtypes(dbo),
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "roles": asm3.users.get_roles(dbo),
            "rows": accounts
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_ACCOUNT)
        return asm3.financial.insert_account_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_ACCOUNT)
        asm3.financial.update_account_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_ACCOUNT)
        for aid in o.post.integer_list("ids"):
            asm3.financial.delete_account(o.dbo, o.user, aid)

    def post_reconcile(self, o):
        self.check(asm3.users.CHANGE_TRANSACTIONS)
        for aid in o.post.integer_list("ids"):
            asm3.financial.mark_account_reconciled(o.dbo, o.user, aid)

class accounts_trx(JSONEndpoint):
    url = "accounts_trx"
    get_permissions = asm3.users.VIEW_ACCOUNT

    def controller(self, o):
        dbo = o.dbo
        post = o.post
        defview = asm3.configuration.default_account_view_period(dbo)
        fromdate = post["fromdate"]
        todate = post["todate"]
        today = dbo.today()
        if fromdate != "" and todate != "":
            fromdate = post.date("fromdate")
            todate = post.date("todate")
        elif defview == asm3.financial.THIS_MONTH:
            fromdate = first_of_month(today)
            todate = last_of_month(today)
        elif defview == asm3.financial.THIS_WEEK:
            fromdate = monday_of_week(today)
            todate = sunday_of_week(today)
        elif defview == asm3.financial.THIS_YEAR:
            fromdate = first_of_year(today)
            todate = last_of_year(today)
        elif defview == asm3.financial.LAST_MONTH:
            fromdate = first_of_month(subtract_months(today, 1))
            todate = last_of_month(subtract_months(today, 1))
        elif defview == asm3.financial.LAST_WEEK:
            fromdate = monday_of_week(subtract_days(today, 7))
            todate = sunday_of_week(subtract_days(today, 7))
        transactions = asm3.financial.get_transactions(dbo, post.integer("accountid"), fromdate, todate, post.integer("recfilter"))
        accountcode = asm3.financial.get_account_code(dbo, post.integer("accountid"))
        accounteditroles = asm3.financial.get_account_edit_roles(dbo, post.integer("accountid"))
        asm3.al.debug("got %d trx for %s <-> %s" % (len(transactions), str(fromdate), str(todate)), "main.accounts_trx", dbo)
        return {
            "rows": transactions,
            "codes": "|".join(asm3.financial.get_account_codes(dbo, accountcode)),
            "accountid": post.integer("accountid"),
            "accountcode": accountcode,
            "accounteditroles": "|".join(accounteditroles),
            "fromdate": python2display(o.locale, fromdate),
            "todate": python2display(o.locale, todate)
        }

    def post_create(self, o):
        self.check(asm3.users.CHANGE_TRANSACTIONS)
        asm3.financial.insert_trx_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_TRANSACTIONS)
        asm3.financial.update_trx_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.CHANGE_TRANSACTIONS)
        for tid in o.post.integer_list("ids"):
            asm3.financial.delete_trx(o.dbo, o.user, tid)

    def post_reconcile(self, o):
        self.check(asm3.users.CHANGE_TRANSACTIONS)
        for tid in o.post.integer_list("ids"):
            asm3.financial.mark_trx_reconciled(o.dbo, o.user, tid)

class additional(JSONEndpoint):
    url = "additional"
    get_permissions = asm3.users.MODIFY_ADDITIONAL_FIELDS

    def controller(self, o):
        dbo = o.dbo
        fields = asm3.additional.get_fields(dbo)
        asm3.al.debug("got %d additional field definitions" % len(fields), "main.additional", dbo)
        return {
            "rows": fields,
            "fieldtypes": asm3.lookups.get_additionalfield_types(dbo),
            "linktypes": asm3.lookups.get_additionalfield_links(dbo)
        }

    def post_create(self, o):
        self.check(asm3.users.MODIFY_ADDITIONAL_FIELDS)
        return asm3.additional.insert_field_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.MODIFY_ADDITIONAL_FIELDS)
        asm3.additional.update_field_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.MODIFY_ADDITIONAL_FIELDS)
        for fid in o.post.integer_list("ids"):
            asm3.additional.delete_field(o.dbo, o.user, fid)

class animal(JSONEndpoint):
    url = "animal"
    get_permissions = asm3.users.VIEW_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        a = asm3.animal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        # If a location filter is set, prevent the user opening this animal if it's
        # not in their location.
        self.check_animal(a)
        recname = "%s %s" % (a.CODE, a.ANIMALNAME)
        if asm3.configuration.audit_on_view_record(dbo): asm3.audit.view_record(dbo, o.user, "animal", a["ID"], recname)
        asm3.al.debug("opened animal %s" % recname, "main.animal", dbo)
        return {
            "animal": a,
            "activelitters": asm3.animal.get_active_litters_brief(dbo),
            "additional": asm3.additional.get_additional_fields(dbo, a.ID, "animal"),
            "animaltypes": asm3.lookups.get_animal_types(dbo),
            "audit": self.checkb(asm3.users.VIEW_AUDIT_TRAIL) and asm3.audit.get_audit_for_link(dbo, "animal", a.ID) or [],
            "species": asm3.lookups.get_species(dbo),
            "breeds": asm3.lookups.get_breeds_by_species(dbo),
            "coattypes": asm3.lookups.get_coattypes(dbo),
            "colours": asm3.lookups.get_basecolours(dbo),
            "deathreasons": asm3.lookups.get_deathreasons(dbo),
            "entryhistory": asm3.animal.get_animal_entries(dbo, a.ID),
            "entryreasons": asm3.lookups.get_entryreasons(dbo),
            "entrytypes": asm3.lookups.get_entry_types(dbo),
            "events": asm3.event.get_events_by_animal(dbo, a.ID),
            "flags": asm3.lookups.get_animal_flags(dbo, a.ADDITIONALFLAGS),
            "incidents": asm3.animalcontrol.get_animalcontrol_for_animal(dbo, o.user, a.ID),
            "internallocations": asm3.lookups.get_internal_locations(dbo),
            "jurisdictions": asm3.lookups.get_jurisdictions(dbo),
            "logtypes": asm3.lookups.get_log_types(dbo),
            "pickuplocations": asm3.lookups.get_pickup_locations(dbo),
            "publishhistory": asm3.animal.get_publish_history(dbo, a.ID),
            "posneg": asm3.lookups.get_posneg(dbo),
            "returnedexitmovements": asm3.animal.get_returned_exit_movements(dbo, a.ID),
            "sexes": asm3.lookups.get_sexes(dbo),
            "sizes": asm3.lookups.get_sizes(dbo),
            "sharebutton": SHARE_BUTTON,
            "tabcounts": asm3.animal.get_satellite_counts(dbo, a.ID)[0],
            "templates": asm3.template.get_document_templates(dbo, "animal"),
            "templatesemail": asm3.template.get_document_templates(dbo, "email"),
            "view": o.post["view"],
            "ynun": asm3.lookups.get_ynun(dbo),
            "ynunk": asm3.lookups.get_ynunk(dbo)
        }

    def post_save(self, o):
        self.check(asm3.users.CHANGE_ANIMAL)
        asm3.animal.update_animal_from_form(o.dbo, o.post, o.user)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_ANIMAL)
        asm3.animal.delete_animal(o.dbo, o.user, o.post.integer("animalid"))

    def post_email(self, o):
        self.check(asm3.users.EMAIL_PERSON)
        asm3.animal.send_email_from_form(o.dbo, o.user, o.post)

    def post_checkchip(self, o):
        return asm3.utils.json(asm3.checkmicrochip.check(o.dbo, o.locale, o.post["n"]))

    def post_gencode(self, o):
        post = o.post
        animaltypeid = post.integer("animaltypeid")
        entryreasonid = post.integer("entryreasonid")
        speciesid = post.integer("speciesid")
        datebroughtin = post.date("datebroughtin")
        sheltercode, shortcode, unique, year = asm3.animal.calc_shelter_code(o.dbo, animaltypeid, entryreasonid, speciesid, datebroughtin)
        return sheltercode + "||" + shortcode + "||" + str(unique) + "||" + str(year)

    def post_merge(self, o):
        self.check(asm3.users.MERGE_ANIMAL)
        asm3.animal.merge_animal(o.dbo, o.user, o.post.integer("animalid"), o.post.integer("mergeanimalid"))

    def post_deleteentryhistory(self, o):
        self.check(asm3.users.CHANGE_ANIMAL)
        return asm3.animal.delete_animal_entry(o.dbo, o.user, o.post.integer("id"))

    def post_newentry(self, o):
        self.check(asm3.users.CHANGE_ANIMAL)
        return asm3.animal.insert_animal_entry(o.dbo, o.user, o.post.integer("animalid"))

    def post_randomname(self, o):
        return asm3.animal.get_random_name(o.dbo, o.post.integer("sex"))

    def post_shared(self, o):
        asm3.animal.insert_publish_history(o.dbo, o.post.integer("id"), o.post["service"])

    def post_clone(self, o):
        self.check(asm3.users.CLONE_ANIMAL)
        nid = asm3.animal.clone_animal(o.dbo, o.user, o.post.integer("animalid"))
        return str(nid)

    def post_forgetpublish(self, o):
        asm3.animal.delete_publish_history(o.dbo, o.post.integer("id"), o.post["service"])

    def post_webnotes(self, o):
        self.check(asm3.users.CHANGE_MEDIA)
        asm3.animal.update_preferred_web_media_notes(o.dbo, o.user, o.post.integer("id"), o.post["comments"])

class animal_boarding(JSONEndpoint):
    url = "animal_boarding"
    js_module = "boarding"
    get_permissions = asm3.users.VIEW_BOARDING

    def controller(self, o):
        dbo = o.dbo
        animalid = o.post.integer("id")
        a = asm3.animal.get_animal(dbo, animalid)
        if a is None: self.notfound()
        self.check_animal(a)
        rows = asm3.financial.get_animal_boarding(dbo, animalid)
        asm3.al.debug("got %d animal boarding records" % (len(rows)), "main.animal_boarding", dbo)
        return {
            "name": "animal_boarding",
            "animal": a,
            "boardingtypes": asm3.lookups.get_boarding_types(dbo),
            "internallocations": asm3.lookups.get_internal_locations(dbo, o.lf),
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "paymentmethods": asm3.lookups.get_payment_methods(dbo),
            "rows": rows,
            "templates": asm3.template.get_document_templates(dbo, "boarding"),
            "tabcounts": asm3.animal.get_satellite_counts(dbo, animalid)[0]
        }

class animal_bulk(JSONEndpoint):
    url = "animal_bulk"
    get_permissions = asm3.users.CHANGE_ANIMAL
    post_permissions = asm3.users.CHANGE_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        return {
            "ynun": asm3.lookups.get_ynun(dbo),
            "ynunk": asm3.lookups.get_ynunk(dbo),
            "animaltypes": asm3.lookups.get_animal_types(dbo),
            "autolitters": asm3.animal.get_active_litters_brief(dbo),
            "flags": asm3.lookups.get_animal_flags(dbo),
            "entryreasons": asm3.lookups.get_entryreasons(dbo),
            "forlist": asm3.users.get_diary_forlist(dbo),
            "internallocations": asm3.lookups.get_internal_locations(dbo, o.lf),
            "logtypes": asm3.lookups.get_log_types(dbo),
            "movementtypes": asm3.lookups.get_movement_types(dbo)
        }

    def post_update(self, o):
        return asm3.animal.update_animals_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        return asm3.animal.delete_animals_from_form(o.dbo, o.user, o.post)

class animal_clinic(JSONEndpoint):
    url = "animal_clinic"
    js_module = "clinic_appointment"
    get_permissions = asm3.users.VIEW_CLINIC

    def controller(self, o):
        dbo = o.dbo
        animalid = o.post.integer("id")
        a = asm3.animal.get_animal(dbo, animalid)
        if a is None: self.notfound()
        self.check_animal(a)
        rows = asm3.clinic.get_animal_appointments(dbo, animalid)
        asm3.al.debug("got %d appointments for animal %s %s" % (len(rows), a.CODE, a.ANIMALNAME), "main.animal_clinic", dbo)
        return {
            "name": self.url,
            "animal": a,
            "clinicstatuses": asm3.lookups.get_clinic_statuses(dbo),
            "clinictypes": asm3.lookups.get_clinic_types(dbo),
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "paymentmethods": asm3.lookups.get_payment_methods(dbo),
            "forlist": asm3.users.get_users_with_permission(dbo, asm3.users.VIEW_CONSULTING_ROOM),
            "rows": rows,
            "templates": asm3.template.get_document_templates(dbo, "clinic"),
            "tabcounts": asm3.animal.get_satellite_counts(dbo, animalid)[0]
        }

class animal_costs(JSONEndpoint):
    url = "animal_costs"
    get_permissions = asm3.users.VIEW_COST

    def controller(self, o):
        dbo = o.dbo
        animalid = o.post.integer("id")
        a = asm3.animal.get_animal(dbo, animalid)
        if a is None: self.notfound()
        self.check_animal(a)
        cost = asm3.animal.get_costs(dbo, animalid)
        asm3.al.debug("got %d costs for animal %s %s" % (len(cost), a["CODE"], a["ANIMALNAME"]), "main.animal_costs", dbo)
        return {
            "rows": cost,
            "animal": a,
            "costtypes": asm3.lookups.get_costtypes(dbo),
            "costtotals": asm3.animal.get_cost_totals(dbo, animalid),
            "tabcounts": asm3.animal.get_satellite_counts(dbo, animalid)[0]
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_COST)
        return asm3.animal.insert_cost_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_COST)
        asm3.animal.update_cost_from_form(o.dbo, o.user, o.post)

    def post_dailyboardingcost(self, o):
        self.check(asm3.users.CHANGE_ANIMAL)
        animalid = o.post.integer("animalid")
        cost = o.post.integer("dailyboardingcost")
        asm3.animal.update_daily_boarding_cost(o.dbo, o.user, animalid, cost)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_COST)
        for cid in o.post.integer_list("ids"):
            asm3.animal.delete_cost(o.dbo, o.user, cid)

class animal_diary(JSONEndpoint):
    url = "animal_diary"
    js_module = "diary"
    get_permissions = asm3.users.VIEW_DIARY

    def controller(self, o):
        dbo = o.dbo
        animalid = o.post.integer("id")
        a = asm3.animal.get_animal(dbo, animalid)
        if a is None: self.notfound()
        self.check_animal(a)
        diaries = asm3.diary.get_diaries(dbo, asm3.diary.ANIMAL, animalid)
        asm3.al.debug("got %d notes for animal %s %s" % (len(diaries), a["CODE"], a["ANIMALNAME"]), "main.animal_diary", dbo)
        return {
            "rows": diaries,
            "animal": a,
            "tabcounts": asm3.animal.get_satellite_counts(dbo, animalid)[0],
            "name": "animal_diary",
            "linkid": animalid,
            "linktypeid": asm3.diary.ANIMAL,
            "diarytasks": asm3.diary.get_animal_tasks(dbo),
            "forlist": asm3.users.get_diary_forlist(dbo)
        }

class animal_diet(JSONEndpoint):
    url = "animal_diet"
    get_permissions = asm3.users.VIEW_DIET

    def controller(self, o):
        dbo = o.dbo
        animalid = o.post.integer("id")
        a = asm3.animal.get_animal(dbo, animalid)
        if a is None: self.notfound()
        self.check_animal(a)
        diet = asm3.animal.get_diets(dbo, animalid)
        asm3.al.debug("got %d diets for animal %s %s" % (len(diet), a["CODE"], a["ANIMALNAME"]), "main.animal_diet", dbo)
        return {
            "rows": diet,
            "animal": a,
            "tabcounts": asm3.animal.get_satellite_counts(dbo, animalid)[0],
            "diettypes": asm3.lookups.get_diets(dbo)
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_DIET)
        return str(asm3.animal.insert_diet_from_form(o.dbo, o.user, o.post))

    def post_update(self, o):
        self.check(asm3.users.CHANGE_DIET)
        asm3.animal.update_diet_from_form(o.dbo, o.user, o.post)
        
    def post_delete(self, o):
        self.check( asm3.users.DELETE_DIET)
        for did in o.post.integer_list("ids"):
            asm3.animal.delete_diet(o.dbo, o.user, did)

class animal_donations(JSONEndpoint):
    url = "animal_donations"
    js_module = "donations"
    get_permissions = asm3.users.VIEW_DONATION

    def controller(self, o):
        dbo = o.dbo
        animalid = o.post.integer("id")
        a = asm3.animal.get_animal(dbo, animalid)
        if a is None: raise web.notfound()
        self.check_animal(a)
        donations = asm3.financial.get_animal_donations(dbo, animalid)
        asm3.al.debug("got %d donations for animal %s %s" % (len(donations), a["CODE"], a["ANIMALNAME"]), "main.animal_donations", dbo)
        return {
            "rows": donations,
            "animal": a,
            "tabcounts": asm3.animal.get_satellite_counts(dbo, animalid)[0],
            "name": "animal_donations",
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "accounts": asm3.financial.get_accounts(dbo, onlybank=True),
            "logtypes": asm3.lookups.get_log_types(dbo), 
            "paymentmethods": asm3.lookups.get_payment_methods(dbo),
            "frequencies": asm3.lookups.get_donation_frequencies(dbo),
            "templates": asm3.template.get_document_templates(dbo, "payment")
        }

class animal_embed(ASMEndpoint):
    url = "animal_embed"
    check_logged_in = False
    post_permissions = asm3.users.VIEW_ANIMAL

    def post_find(self, o):
        self.content_type("application/json")
        q = o.post["q"]
        rows = asm3.animal.get_animal_find_simple(o.dbo, q, classfilter=o.post["filter"], limit=100, lf=o.lf, brief=True)
        asm3.al.debug("got %d results for '%s'" % (len(rows), self.query()), "main.animal_embed", o.dbo)
        return asm3.utils.json(rows)

    def post_multiselect(self, o):
        self.content_type("application/json")
        dbo = o.dbo
        rows = asm3.animal.get_animal_find_simple(dbo, "", classfilter="all", limit=asm3.configuration.record_search_limit(dbo), lf=o.lf, brief=True)
        locations = asm3.lookups.get_internal_locations(dbo, o.lf)
        species = asm3.lookups.get_species(dbo)
        litters = asm3.animal.get_litters(dbo)
        flags = asm3.lookups.get_animal_flags(dbo)
        agegroups = asm3.configuration.age_groups(dbo)
        rv = { "rows": rows, "locations": locations, "species": species, "litters": litters, "flags": flags, "agegroups": agegroups }
        return asm3.utils.json(rv)

    def post_id(self, o):
        self.content_type("application/json")
        dbo = o.dbo
        animalid = o.post.integer("id")
        a = asm3.animal.get_animal(dbo, animalid)
        if a is None:
            asm3.al.error("get animal by id %d found no records." % animalid, "main.animal_embed", dbo)
            self.notfound()
        else:
            asm3.al.debug("got animal %s %s by id" % (a["CODE"], a["ANIMALNAME"]), "main.animal_embed", dbo)
            return asm3.utils.json((a,))

class animal_find(JSONEndpoint):
    url = "animal_find"
    get_permissions = asm3.users.VIEW_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        c = {
            "additionalfields": asm3.additional.get_additional_fields(dbo, 0, "animal"),
            "agegroups": asm3.configuration.age_groups(dbo),
            "animaltypes": asm3.lookups.get_animal_types(dbo),
            "species": asm3.lookups.get_species(dbo),
            "breeds": asm3.lookups.get_breeds_by_species(dbo),
            "flags": asm3.lookups.get_animal_flags(dbo),
            "diettypes": asm3.lookups.get_diets(dbo),
            "sexes": asm3.lookups.get_sexes(dbo),
            "entryreasons": asm3.lookups.get_entryreasons(dbo),
            "entrytypes": asm3.lookups.get_entry_types(dbo),
            "internallocations": asm3.lookups.get_internal_locations(dbo, o.lf),
            "jurisdictions": asm3.lookups.get_jurisdictions(dbo),
            "pickuplocations": asm3.lookups.get_pickup_locations(dbo),
            "sizes": asm3.lookups.get_sizes(dbo),
            "colours": asm3.lookups.get_basecolours(dbo),
            "users": asm3.users.get_users(dbo)
        }
        asm3.al.debug("loaded lookups for find animal", "main.animal_find", dbo)
        return c

class animal_find_results(JSONEndpoint):
    url = "animal_find_results"
    get_permissions = asm3.users.VIEW_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        q = o.post["q"]
        mode = o.post["mode"]
        if mode == "SIMPLE":
            results = asm3.animal.get_animal_find_simple(dbo, q, classfilter="all", limit=asm3.configuration.record_search_limit(dbo), lf=o.lf)
        else:
            results = asm3.animal.get_animal_find_advanced(dbo, o.post.data, limit=asm3.configuration.record_search_limit(dbo), lf=o.lf)
        add = None
        if len(results) > 0: 
            add = asm3.additional.get_additional_fields_ids(dbo, results, "animal")
        asm3.al.debug("found %d results for %s" % (len(results), self.query()), "main.animal_find_results", dbo)
        return {
            "rows": results,
            "additional": add,
            "wasonshelter": q == "" and mode == "SIMPLE"
        }

class animal_licence(JSONEndpoint):
    url = "animal_licence"
    js_module = "licence"
    get_permissions = asm3.users.VIEW_LICENCE

    def controller(self, o):
        dbo = o.dbo
        a = asm3.animal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        self.check_animal(a)
        licences = asm3.financial.get_animal_licences(dbo, o.post.integer("id"))
        asm3.al.debug("got %d licences" % len(licences), "main.animal_licence", dbo)
        return {
            "name": "animal_licence",
            "rows": licences,
            "animal": a,
            "baselink": f"{SERVICE_URL}?account={dbo.name()}&method=checkout_licence&token=",
            "templates": asm3.template.get_document_templates(dbo, "licence"),
            "tabcounts": asm3.animal.get_satellite_counts(dbo, a["ID"])[0],
            "licencetypes": asm3.lookups.get_licence_types(dbo)
        }

class animal_log(JSONEndpoint):
    url = "animal_log"
    js_module = "log"
    get_permissions = asm3.users.VIEW_LOG

    def controller(self, o):
        dbo = o.dbo
        logfilter = o.post.integer("filter")
        if logfilter == 0: logfilter = asm3.configuration.default_log_filter(dbo)
        a = asm3.animal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        self.check_animal(a)
        logs = asm3.log.get_logs(dbo, asm3.log.ANIMAL, o.post.integer("id"), logfilter)
        asm3.al.debug("got %d logs for animal %s %s" % (len(logs), a["CODE"], a["ANIMALNAME"]), "main.animal_log", dbo)
        return {
            "name": "animal_log",
            "linkid": o.post.integer("id"),
            "linktypeid": asm3.log.ANIMAL,
            "filter": logfilter,
            "rows": logs,
            "animal": a,
            "tabcounts": asm3.animal.get_satellite_counts(dbo, a["ID"])[0],
            "logtypes": asm3.lookups.get_log_types(dbo)
        }

class animal_media(JSONEndpoint):
    url = "animal_media"
    js_module = "media"
    get_permissions = asm3.users.VIEW_MEDIA

    def controller(self, o):
        dbo = o.dbo
        a = asm3.animal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        self.check_animal(a)
        m = asm3.media.get_media(dbo, asm3.media.ANIMAL, o.post.integer("id"))
        asm3.al.debug("got %d media entries for animal %s %s" % (len(m), a["CODE"], a["ANIMALNAME"]), "main.animal_media", dbo)
        return {
            "media": m,
            "animal": a,
            "tabcounts": asm3.animal.get_satellite_counts(dbo, a["ID"])[0],
            "canwatermark": True and asm3.media.watermark_available(dbo),
            "documentrepository": asm3.dbfs.get_document_repository(o.dbo),
            "showpreferred": True,
            "linkid": o.post.integer("id"),
            "linktypeid": asm3.media.ANIMAL,
            "logtypes": asm3.lookups.get_log_types(dbo),
            "newmedia": o.post.integer("newmedia") == 1,
            "name": self.url,
            "flags": asm3.lookups.get_media_flags(dbo),
            "resizeimagespec": asm3.utils.iif(RESIZE_IMAGES_DURING_ATTACH, RESIZE_IMAGES_SPEC, ""),
            "templates": asm3.template.get_document_templates(dbo, "email"),
            "sigtype": ELECTRONIC_SIGNATURES
        }

class animal_medical(JSONEndpoint):
    url = "animal_medical"
    js_module = "medical"
    get_permissions = asm3.users.VIEW_MEDICAL

    def controller(self, o):
        dbo = o.dbo
        a = asm3.animal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        self.check_animal(a)
        limit = asm3.configuration.medical_item_display_limit(dbo)
        med = asm3.medical.get_regimens_treatments(dbo, o.post.integer("id"), limit=limit)
        profiles = asm3.medical.get_profiles(dbo)
        asm3.al.debug("got %d medical entries for animal %s %s" % (len(med), a["CODE"], a["ANIMALNAME"]), "main.animal_medical", dbo)
        return {
            "profiles": profiles,
            "rows": med,
            "overlimit": len(med) == limit and limit or 0,
            "name": "animal_medical",
            "tabcounts": asm3.animal.get_satellite_counts(dbo, a["ID"])[0],
            "stockitems": asm3.stock.get_stock_items(dbo),
            "stockusagetypes": asm3.lookups.get_stock_usage_types(dbo),
            "templates": asm3.template.get_document_templates(dbo, "medical"),
            "users": asm3.users.get_users(dbo),
            "animal": a
        }

class animal_movements(JSONEndpoint):
    url = "animal_movements"
    js_module = "movements"
    get_permissions = asm3.users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        a = asm3.animal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        self.check_animal(a)
        movements = asm3.movement.get_animal_movements(dbo, o.post.integer("id"))
        movements = asm3.person.reduce_find_results(dbo, o.user, movements, idcol="OWNERID", sitecol="OWNERSITEID")
        asm3.al.debug("got %d movements for animal %s %s" % (len(movements), a["CODE"], a["ANIMALNAME"]), "main.animal_movements", dbo)
        return {
            "rows": movements,
            "animal": a,
            "tabcounts": asm3.animal.get_satellite_counts(dbo, a["ID"])[0],
            "logtypes": asm3.lookups.get_log_types(dbo), 
            "movementtypes": asm3.lookups.get_movement_types(dbo),
            "additional": asm3.additional.get_field_definitions(dbo, "movement"),
            "movementtypes_additionalfieldtypes": asm3.additional.MOVEMENT_MAPPING,
            "reservationstatuses": asm3.lookups.get_reservation_statuses(dbo),
            "returncategories": asm3.lookups.get_entryreasons(dbo),
            "templates": asm3.template.get_document_templates(dbo, "movement"),
            "templatesemail": asm3.template.get_document_templates(dbo, "email"),
            "name": self.url
        }

class animal_new(JSONEndpoint):
    url = "animal_new"
    get_permissions = asm3.users.ADD_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        c = {
            "autolitters": asm3.animal.get_active_litters_brief(dbo),
            "additional": asm3.additional.get_additional_fields(dbo, 0, "animal"),
            "animaltypes": asm3.lookups.get_animal_types(dbo),
            "species": asm3.lookups.get_species(dbo),
            "breeds": asm3.lookups.get_breeds_by_species(dbo),
            "coattypes": asm3.lookups.get_coattypes(dbo),
            "colours": asm3.lookups.get_basecolours(dbo),
            "flags": asm3.lookups.get_animal_flags(dbo),
            "sexes": asm3.lookups.get_sexes(dbo),
            "entryreasons": asm3.lookups.get_entryreasons(dbo),
            "entrytypes": asm3.lookups.get_entry_types(dbo),
            "jurisdictions": asm3.lookups.get_jurisdictions(dbo),
            "internallocations": asm3.lookups.get_internal_locations(dbo, o.lf),
            "pickuplocations": asm3.lookups.get_pickup_locations(dbo),
            "sizes": asm3.lookups.get_sizes(dbo)
        }
        asm3.al.debug("loaded lookups for new animal", "main.animal_new", dbo)
        return c

    def post_save(self, o):
        self.check(asm3.users.ADD_ANIMAL)
        animalid, code = asm3.animal.insert_animal_from_form(o.dbo, o.post, o.user)
        return "%s %s" % (animalid, code)

    def post_recentnamecheck(self, o):
        rows = asm3.animal.get_recent_with_name(o.dbo, o.post["animalname"])
        asm3.al.debug("recent names found %d rows for '%s'" % (len(rows), o.post["animalname"]), "main.animal_new.recentnamecheck", o.dbo)
        if len(rows) > 0:
            return "|".join((str(rows[0]["ANIMALID"]), rows[0]["SHELTERCODE"], rows[0]["ANIMALNAME"]))

    def post_units(self, o):
        return "&&".join(asm3.animal.get_units_with_availability(o.dbo, o.post.integer("locationid")))

class animal_observations(JSONEndpoint):
    url = "animal_observations"
    get_permissions = asm3.users.ADD_LOG

    def controller(self, o):
        dbo = o.dbo
        animals = asm3.animal.get_shelterview_animals(dbo, o.lf)
        asm3.al.debug("got %d shelter animals" % len(animals), "main.animal_observations", dbo)
        return { 
            "animals": animals,
            "logtypes": asm3.lookups.get_log_types(dbo), 
            "internallocations": asm3.lookups.get_internal_locations_counts(dbo, o.lf)
        }

    def post_save(self, o):
        self.check(asm3.users.ADD_LOG)
        nocreated = 0
        for row in o.post["logs"].split("^^"):
            animalid, msg = row.split("==")
            asm3.log.add_log(o.dbo, o.user, asm3.log.ANIMAL, asm3.utils.atoi(animalid), o.post.integer("logtype"), msg)
            nocreated += 1
        return str(nocreated)

class animal_test(JSONEndpoint):
    url = "animal_test"
    js_module = "test"
    get_permissions = asm3.users.VIEW_TEST

    def controller(self, o):
        dbo = o.dbo
        a = asm3.animal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        self.check_animal(a)
        test = asm3.medical.get_tests(dbo, o.post.integer("id"))
        asm3.al.debug("got %d tests" % len(test), "main.animal_test", dbo)
        return {
            "name": "animal_test",
            "animal": a,
            "tabcounts": asm3.animal.get_satellite_counts(dbo, a["ID"])[0],
            "rows": test,
            "stockitems": asm3.stock.get_stock_items(dbo),
            "stockusagetypes": asm3.lookups.get_stock_usage_types(dbo),
            "testtypes": asm3.lookups.get_test_types(dbo),
            "testresults": asm3.lookups.get_test_results(dbo)
        }

class animal_transport(JSONEndpoint):
    url = "animal_transport"
    js_module = "transport"
    get_permissions = asm3.users.VIEW_TRANSPORT

    def controller(self, o):
        dbo = o.dbo
        a = asm3.animal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        self.check_animal(a)
        transports = asm3.movement.get_animal_transports(dbo, o.post.integer("id"))
        asm3.al.debug("got %d transports" % len(transports), "main.animal_transport", dbo)
        return {
            "name": "animal_transport",
            "animal": a,
            "tabcounts": asm3.animal.get_satellite_counts(dbo, a["ID"])[0],
            "statuses": asm3.lookups.get_transport_statuses(dbo),
            "templates": asm3.template.get_document_templates(dbo, "transport"),
            "transporttypes": asm3.lookups.get_transport_types(dbo),
            "rows": transports
        }

class animal_vaccination(JSONEndpoint):
    url = "animal_vaccination"
    js_module = "vaccination"
    get_permissions = asm3.users.VIEW_VACCINATION

    def controller(self, o):
        dbo = o.dbo
        a = asm3.animal.get_animal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        self.check_animal(a)
        vacc = asm3.medical.get_vaccinations(dbo, o.post.integer("id"))
        asm3.al.debug("got %d vaccinations" % len(vacc), "main.vaccination", dbo)
        return {
            "name": "animal_vaccination",
            "animal": a,
            "tabcounts": asm3.animal.get_satellite_counts(dbo, a["ID"])[0],
            "rows": vacc,
            "batches": asm3.medical.get_batch_for_vaccination_types(dbo),
            "manufacturers": "|".join(asm3.medical.get_vacc_manufacturers(dbo)),
            "stockitems": asm3.stock.get_stock_items(dbo),
            "stockusagetypes": asm3.lookups.get_stock_usage_types(dbo),
            "users": asm3.users.get_users(dbo),
            "vaccinationtypes": asm3.lookups.get_vaccination_types(dbo)
        }

class batch(JSONEndpoint):
    url = "batch"
    get_permissions = asm3.users.TRIGGER_BATCH
    post_permissions = asm3.users.TRIGGER_BATCH

    def controller(self, o):
        return {}

    def post_genfigyear(self, o):
        l = o.locale
        if o.post.date("taskdate") is None: raise asm3.utils.ASMValidationError("no date parameter")
        asm3.asynctask.function_task(o.dbo, _("Regenerate annual animal figures for", l), asm3.animal.update_animal_figures_annual, o.dbo, o.post.date("taskdate").year)

    def post_genfigmonth(self, o):
        l = o.locale
        if o.post.date("taskdate") is None: raise asm3.utils.ASMValidationError("no date parameter")
        asm3.asynctask.function_task(o.dbo, _("Regenerate monthly animal figures for", l), asm3.animal.update_animal_figures, o.dbo, o.post.date("taskdate").month, o.post.date("taskdate").year)

    def post_genshelterpos(self, o):
        l = o.locale
        asm3.asynctask.function_task(o.dbo, _("Recalculate on-shelter animal locations", l), asm3.animal.update_on_shelter_animal_statuses, o.dbo)

    def post_genallpos(self, o):
        l = o.locale
        asm3.asynctask.function_task(o.dbo, _("Recalculate ALL animal locations", l), asm3.animal.update_all_animal_statuses, o.dbo)

    def post_genallvariable(self, o):
        l = o.locale
        asm3.asynctask.function_task(o.dbo, _("Recalculate ALL animal ages/times", l), asm3.animal.update_all_variable_animal_data, o.dbo)

    def post_genallbreeds(self, o):
        l = o.locale
        asm3.asynctask.function_task(o.dbo, _("Recalculate ALL animal breed names", l), asm3.animal.update_animal_breeds, o.dbo)

    def post_genlitters(self, o):
        l = o.locale
        asm3.asynctask.function_task(o.dbo, _("Recalculate active litter counts", l), asm3.animal.update_active_litters, o.dbo)

    def post_gendiarylinkinfo(self, o):
        l = o.locale
        asm3.asynctask.function_task(o.dbo, _("Regenerate diary link info for incomplete notes", l), asm3.diary.update_link_info_incomplete, o.dbo)

    def post_genlookingfor(self, o):
        l = o.locale
        asm3.asynctask.function_task(o.dbo, _("Regenerate 'Person looking for' report", l), asm3.person.update_lookingfor_report, o.dbo)

    def post_genownername(self, o):
        l = o.locale
        asm3.asynctask.function_task(o.dbo, _("Regenerate person names in selected format", l), asm3.person.update_owner_names, o.dbo)

    def post_genownerflags(self, o):
        l = o.locale
        asm3.asynctask.function_task(o.dbo, _("Regenerate person flags column", l), asm3.person.update_check_flags, o.dbo)

    def post_genlostfound(self, o):
        l = o.locale
        asm3.asynctask.function_task(o.dbo, _("Regenerate 'Match lost and found animals' report", l), asm3.lostfound.update_match_report, o.dbo)

    def post_resetnnncodes(self, o):
        l = o.locale
        asm3.asynctask.function_task(o.dbo, _("Reset NNN animal code counts for this year", l), asm3.animal.maintenance_reset_nnn_codes, o.dbo)

class boarding(JSONEndpoint):
    url = "boarding"
    js_module = "boarding"
    get_permissions = asm3.users.VIEW_BOARDING

    def controller(self, o):
        dbo = o.dbo
        rows = asm3.financial.get_boarding(dbo, o.post["filter"])
        asm3.al.debug("got %d boarding records" % (len(rows)), "main.boarding", dbo)
        return {
            "name": "boarding",
            "boardingtypes": asm3.lookups.get_boarding_types(dbo),
            "internallocations": asm3.lookups.get_internal_locations(dbo, o.lf),
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "paymentmethods": asm3.lookups.get_payment_methods(dbo),
            "rows": rows,
            "templates": asm3.template.get_document_templates(dbo, "boarding")
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_BOARDING)
        return asm3.financial.insert_boarding_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_BOARDING)
        asm3.financial.update_boarding_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_BOARDING)
        for did in o.post.integer_list("ids"):
            asm3.financial.delete_boarding(o.dbo, o.user, did)

class calendarview(JSONEndpoint):
    url = "calendarview"
    get_permissions = asm3.users.VIEW_ANIMAL

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
        if "d" in ev and self.checkb(asm3.users.VIEW_DIARY):
            # Show all diary notes on the calendar if the user chose to see all
            # on the home page, or they have permission to view all notes
            diarylink = "diary_edit_my"
            diaryfilter = "uncompleted"
            if asm3.configuration.all_diary_home_page(dbo) or self.checkb(asm3.users.EDIT_ALL_DIARY_NOTES):
                user = ""
                diarylink = "diary_edit"
            for d in asm3.diary.get_between_two_dates(dbo, user, start, end):
                allday = False
                # If the diary time is midnight, assume all day instead
                if d.DIARYDATETIME.hour == 0 and d.DIARYDATETIME.minute == 0:
                    allday = True
                # If the diary has been completed, change the filter to completed
                if d.DIARYDATETIME > dbo.now():
                    diaryfilter = "future"
                if d.DATECOMPLETED is not None:
                    diaryfilter = "completed"
                events.append({ 
                    "title": d.SUBJECT, 
                    "allDay": allday, 
                    "start": d.DIARYDATETIME,
                    "end": add_minutes(d.DIARYDATETIME, 60),
                    "tooltip": "%s %s %s" % (d["SUBJECT"], d["LINKINFO"], d["NOTE"]), 
                    "icon": "diary",
                    "link": f"{diarylink}?id={d.ID}&filter={diaryfilter}" })
        if "v" in ev and self.checkb(asm3.users.VIEW_VACCINATION):
            for v in asm3.medical.get_vaccinations_two_dates(dbo, start, end, o.lf):
                sub = "%s - %s" % (v.VACCINATIONTYPE, v.ANIMALNAME)
                tit = "%s - %s %s (%s) %s" % (v.VACCINATIONTYPE, v.SHELTERCODE, v.ANIMALNAME, v.DISPLAYLOCATIONNAME, v.COMMENTS)
                events.append({ 
                    "title": sub, 
                    "allDay": True, 
                    "start": v.DATEREQUIRED, 
                    "tooltip": tit, 
                    "icon": "vaccination",
                    "link": "animal_vaccination?id=%s" % v.ANIMALID })
            for v in asm3.medical.get_vaccinations_expiring_two_dates(dbo, start, end, o.lf):
                sub = "%s - %s" % (v.VACCINATIONTYPE, v.ANIMALNAME)
                tit = "%s - %s %s (%s) %s" % (v.VACCINATIONTYPE, v.SHELTERCODE, v.ANIMALNAME, v.DISPLAYLOCATIONNAME, v.COMMENTS)
                events.append({ 
                    "title": sub, 
                    "allDay": True, 
                    "start": v.DATEEXPIRES, 
                    "tooltip": tit, 
                    "icon": "vaccination",
                    "link": "animal_vaccination?id=%s" % v.ANIMALID })
        if "m" in ev and self.checkb(asm3.users.VIEW_MEDICAL):
            for m in asm3.medical.get_treatments_two_dates(dbo, start, end, o.lf):
                sub = "%s - %s" % (m.TREATMENTNAME, m.ANIMALNAME)
                tit = "%s - %s %s (%s) %s %s" % (m.TREATMENTNAME, m.SHELTERCODE, m.ANIMALNAME, m.DISPLAYLOCATIONNAME, m.DOSAGE, m.COMMENTS)
                events.append({ 
                    "title": sub, 
                    "allDay": True, 
                    "start": m.DATEREQUIRED, 
                    "tooltip": tit, 
                    "icon": "medical",
                    "link": "animal_medical?id=%s" % m.ANIMALID })
        if "t" in ev and self.checkb(asm3.users.VIEW_TEST):
            for t in asm3.medical.get_tests_two_dates(dbo, start, end, o.lf):
                sub = "%s - %s" % (t.TESTNAME, t.ANIMALNAME)
                tit = "%s - %s %s (%s) %s" % (t.TESTNAME, t.SHELTERCODE, t.ANIMALNAME, t.DISPLAYLOCATIONNAME, t.COMMENTS)
                events.append({ 
                    "title": sub, 
                    "allDay": True, 
                    "start": t.DATEREQUIRED, 
                    "tooltip": tit, 
                    "icon": "test",
                    "link": "animal_test?id=%s" % t.ANIMALID })
        if "b" in ev and self.checkb(asm3.users.VIEW_BOARDING):
            for b in asm3.financial.get_boarding_due_two_dates(dbo, start, end):
                sub = "%s:%s - %s" % (b.SHELTERLOCATIONNAME, b.SHELTERLOCATIONUNIT, b.ANIMALNAME)
                tit = "%s:%s - %s, %s" % (b.SHELTERLOCATIONNAME, b.SHELTERLOCATIONUNIT, b.ANIMALNAME, b.OWNERNAME)
                events.append({ 
                    "title": sub, 
                    "allDay": False, 
                    "start": b.INDATETIME, 
                    "end": b.OUTDATETIME,
                    "tooltip": tit, 
                    "icon": "boarding",
                    "link": "animal_boarding?id=%s" % b.ANIMALID })
        if "c" in ev and self.checkb(asm3.users.VIEW_CLINIC):
            for c in asm3.clinic.get_appointments_two_dates(dbo, start, end, o.post["apptfor"], o.siteid):
                if c.OWNERNAME is not None:
                    sub = "%s - %s" % (c.OWNERNAME, c.ANIMALNAME)
                    tit = "%s - %s (%s) %s: %s" % (c.OWNERNAME, c.ANIMALNAME, c.APPTFOR, c.CLINICTYPENAME, c.REASONFORAPPOINTMENT)
                    link = "person_clinic?id=%s" % c.OWNERID
                else:
                    sub = "%s" % c.ANIMALNAME
                    tit = "%s (%s) %s: %s" % (c.ANIMALNAME, c.APPTFOR, c.CLINICTYPENAME, c.REASONFORAPPOINTMENT)
                    link = "animal_clinic?id=%s" % c.ANIMALID
                events.append({ 
                    "title": sub, 
                    "allDay": False, 
                    "start": c.DATETIME,
                    "end": add_minutes(c.DATETIME, 20),
                    "tooltip": tit, 
                    "icon": "health",
                    "link": link })
        if "p" in ev and self.checkb(asm3.users.VIEW_DONATION):
            for p in asm3.financial.get_donations_due_two_dates(dbo, start, end):
                sub = "%s - %s" % (p.DONATIONNAME, p.OWNERNAME)
                tit = "%s - %s %s %s" % (p.DONATIONNAME, p.OWNERNAME, format_currency(l, p.DONATION), p.COMMENTS)
                events.append({ 
                    "title": sub, 
                    "allDay": True, 
                    "start": p.DATEDUE, 
                    "tooltip": tit, 
                    "icon": "donation",
                    "link": "person_donations?id=%s" % p.OWNERID })
        if "o" in ev and self.checkb(asm3.users.VIEW_INCIDENT):
            for o in asm3.animalcontrol.get_followup_two_dates(dbo, start, end):
                sub = "%s - %s" % (o.INCIDENTNAME, o.OWNERNAME)
                tit = "%s - %s %s, %s" % (o.INCIDENTNAME, o.OWNERNAME, o.DISPATCHADDRESS, o.CALLNOTES)
                events.append({ 
                    "title": sub, 
                    "allDay": False, 
                    "start": o.FOLLOWUPDATETIME, 
                    "tooltip": tit, 
                    "icon": "call",
                    "link": "incident?id=%s" % o.ACID })
        if "r" in ev and self.checkb(asm3.users.VIEW_TRANSPORT):
            for r in asm3.movement.get_transport_two_dates(dbo, start, end):
                sub = "%s - %s" % (r.ANIMALNAME, r.SHELTERCODE)
                tit = "%s %s, %s - %s :: %s, %s" % (r.ANIMALNAME, r.SHELTERCODE, r.DRIVEROWNERNAME, r.PICKUPOWNERADDRESS, r.DROPOFFOWNERADDRESS, r.COMMENTS)
                allday = False
                if r.PICKUPDATETIME.hour == 0 and r.PICKUPDATETIME.minute == 0:
                    allday = True
                events.append({ 
                    "title": sub, 
                    "allDay": allday, 
                    "start": r.PICKUPDATETIME, 
                    "end": r.DROPOFFDATETIME,
                    "tooltip": tit, 
                    "icon": "transport",
                    "link": "animal_transport?id=%s" % r.ANIMALID})
        if "l" in ev and self.checkb(asm3.users.VIEW_TRAPLOAN):
            for l in asm3.animalcontrol.get_traploan_two_dates(dbo, start, end):
                sub = "%s - %s" % (l.TRAPTYPENAME, l.OWNERNAME)
                tit = "%s - %s %s, %s" % (l.TRAPTYPENAME, l.OWNERNAME, l.TRAPNUMBER, l.COMMENTS)
                events.append({ 
                    "title": sub, 
                    "allDay": True, 
                    "start": l.RETURNDUEDATE, 
                    "tooltip": tit, 
                    "icon": "traploan",
                    "link": "person_traploan?id=%s" % l.OWNERID})
        asm3.al.debug("calendarview found %d events (%s->%s)" % (len(events), start, end), "main.calendarview", dbo)
        self.content_type("application/json")
        return asm3.utils.json(events)

class change_password(JSONEndpoint):
    url = "change_password"

    def controller(self, o):
        asm3.al.debug("%s change password screen" % o.user, "main.change_password", o.dbo)
        return {
            "ismaster": asm3.smcom.is_master_user(o.user, o.dbo.name()),
            "username": o.user
        }

    def post_all(self, o):
        oldpass = o.post["oldpassword"]
        newpass = o.post["newpassword"]
        asm3.al.debug("%s changed password" % (o.user), "main.change_password", o.dbo)
        asm3.users.change_password(o.dbo, o.user, oldpass, newpass)

class change_user_settings(JSONEndpoint):
    url = "change_user_settings"

    def controller(self, o):
        asm3.al.debug("%s change user settings screen" % o.user, "main.change_user_settings", o.dbo)
        u = asm3.users.get_user(o.dbo, o.user)
        if not u.OTPSECRET:
            asm3.al.debug("missing otp secret for user %s, generating" % o.user, "main.change_user_settings", o.dbo)
            secret = asm3.utils.otp_secret()
            u.OTPSECRET = secret
            asm3.users.update_user_otp_secret(o.dbo, u.ID, secret)
        return {
            "user": u,
            "smcom": asm3.smcom.active(),
            "locales": get_locales(),
            "sigtype": ELECTRONIC_SIGNATURES,
            "themes": asm3.lookups.VISUAL_THEMES,
            "reports": asm3.reports.get_all_report_titles(o.dbo),
            "stocklocations": asm3.lookups.get_stock_locations(o.dbo),
            "stockusagetypes": asm3.lookups.get_stock_usage_types(o.dbo)
        }

    def post_all(self, o):
        post = o.post
        theme = post["theme"]
        locale = post["locale"]
        realname = post["realname"]
        email = post["email"]
        signature = post["signature"]
        quicklinks = post["quicklinksid"]
        quickreports = post["quickreportsid"]
        quickreportscfg = []
        reports = asm3.reports.get_reports(o.dbo)
        if quickreports != "":
            for reportid in quickreports.split(","):
                for report in reports:
                    if report.ID == int(reportid.split("=")[0]):
                        reporttitle = report.TITLE
                        quickreportscfg.append( f"{reportid}={reporttitle}" ) 
                        break
        quickreportscfg = ",".join(quickreportscfg)
        twofavalidcode = post["twofavalidcode"]
        twofavalidpassword = post["twofavalidpassword"]
        defaultlocationid = post["defaultlocationid"]
        defaultstockusagetypeid = post["defaultstockusagetypeid"]
        asm3.al.debug("%s changed settings: theme=%s, locale=%s, realname=%s, email=%s, quicklinks=%s, twofacode=%s, twofapass=%s" % (o.user, theme, locale, realname, email, quicklinks, twofavalidcode, twofavalidpassword), "main.change_password", o.dbo)
        asm3.users.update_user_settings(o.dbo, o.user, email, realname, locale, theme, signature, twofavalidcode, twofavalidpassword, defaultlocationid, defaultstockusagetypeid)
        # If the user now has 2FA enabled, and force2fa session flag is on, we can turn it off
        if "force2fa" in o.session and o.session.force2fa and asm3.users.get_user(o.dbo, o.user).ENABLETOTP == 1:
            o.session.force2fa = False
        # If the user's quicklinks are the same as the global ones, set to a blank instead
        if quicklinks == asm3.configuration.quicklinks_id(o.dbo):
            asm3.configuration.cset(o.dbo, "%s_QuicklinksID" % o.user, "")
        else:
            asm3.configuration.cset(o.dbo, "%s_QuicklinksID" % o.user, quicklinks)
        asm3.configuration.cset(o.dbo, "%s_QuickReportsID" % o.user, quickreportscfg)
        asm3.configuration.cset(o.dbo, "%s_ShelterView" % o.user, post["shelterview"])
        asm3.configuration.cset(o.dbo, "%s_EmailDefault" % o.user, asm3.utils.iif(post.boolean("emaildefault"), "Yes", "No"))

        asm3.configuration.cset(o.dbo, "%s_DefaultStockLocationID" % o.user, defaultlocationid)
        asm3.configuration.cset(o.dbo, "%s_DefaultStockUsageTypeID" % o.user, defaultstockusagetypeid)

        self.reload_config()

class citations(JSONEndpoint):
    url = "citations"
    get_permissions = asm3.users.VIEW_CITATION

    def controller(self, o):
        # this screen only supports one mode at present - unpaid fines
        # if o.post["filter"] == "unpaid" or o.post["filter"] == "":
        citations = asm3.financial.get_unpaid_fines(o.dbo)
        asm3.al.debug("got %d citations" % len(citations), "main.citations", o.dbo)
        return {
            "name": "citations",
            "rows": citations,
            "citationtypes": asm3.lookups.get_citation_types(o.dbo),
            "nextid": o.dbo.get_id_max("ownercitation")
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_CITATION)
        return asm3.financial.insert_citation_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_CITATION)
        asm3.financial.update_citation_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_CITATION)
        for lid in o.post.integer_list("ids"):
            asm3.financial.delete_citation(o.dbo, o.user, lid)

class clinic_appointment(ASMEndpoint):
    url = "clinic_appointment"

    def post_create(self, o):
        self.check(asm3.users.ADD_CLINIC)
        return asm3.clinic.insert_appointment_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_CLINIC)
        asm3.clinic.update_appointment_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_CLINIC)
        for cid in o.post.integer_list("ids"):
            asm3.clinic.delete_appointment(o.dbo, o.user, cid)

    def post_personanimals(self, o):
        self.check(asm3.users.VIEW_ANIMAL)
        return asm3.utils.json(asm3.animal.get_animals_owned_by(o.dbo, o.post.integer("personid")))

    def post_towaiting(self, o):
        self.check(asm3.users.CHANGE_CLINIC)
        for cid in o.post.integer_list("ids"):
            asm3.clinic.update_appointment_to_waiting(o.dbo, o.user, cid, o.post.datetime("date", "time"))

    def post_towithvet(self, o):
        self.check(asm3.users.CHANGE_CLINIC)
        for cid in o.post.integer_list("ids"):
            asm3.clinic.update_appointment_to_with_vet(o.dbo, o.user, cid, o.post.datetime("date", "time"))

    def post_tocomplete(self, o):
        self.check(asm3.users.CHANGE_CLINIC)
        for cid in o.post.integer_list("ids"):
            asm3.clinic.update_appointment_to_complete(o.dbo, o.user, cid, o.post.datetime("date", "time"))

class clinic_calendar(JSONEndpoint):
    url = "clinic_calendar"
    get_permissions = asm3.users.VIEW_CLINIC

    def controller(self, o):
        return {
            "forlist": asm3.users.get_users_with_permission(o.dbo, asm3.users.VIEW_CONSULTING_ROOM)
        }

class clinic_invoice(JSONEndpoint):
    url = "clinic_invoice"
    get_permissions = asm3.users.VIEW_CLINIC

    def controller(self, o):
        dbo = o.dbo
        appointmentid = o.post.integer("appointmentid")
        appointment = asm3.clinic.get_appointment(dbo, appointmentid)
        if appointment is None: self.notfound()
        rows = asm3.clinic.get_invoice_items(dbo, appointmentid)
        asm3.al.debug("got %d invoice items for appointment %d" % (len(rows), appointmentid), "main.clinic_invoice", dbo)
        return {
            "appointment": appointment,
            "appointmentid": appointmentid,
            "rows": rows
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_CLINIC)
        return asm3.clinic.insert_invoice_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_CLINIC)
        asm3.clinic.update_invoice_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_CLINIC)
        for iid in o.post.integer_list("ids"):
            asm3.clinic.delete_invoice(o.dbo, o.user, iid)

class clinic_consultingroom(JSONEndpoint):
    url = "clinic_consultingroom"
    js_module = "clinic_appointment"
    get_permissions = asm3.users.VIEW_CLINIC

    def controller(self, o):
        dbo = o.dbo
        sf = o.post.integer("filter")
        if o.post["filter"] == "": sf = -1
        rows = asm3.clinic.get_appointments_today(dbo, statusfilter = sf, userfilter = o.user, siteid = o.siteid)
        asm3.al.debug("got %d appointments" % (len(rows)), "main.clinic_consultingroom", dbo)
        return {
            "name": self.url,
            "filter": sf,
            "clinicstatuses": asm3.lookups.get_clinic_statuses(dbo),
            "clinictypes": asm3.lookups.get_clinic_types(dbo),
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "paymentmethods": asm3.lookups.get_payment_methods(dbo),
            "forlist": asm3.users.get_users_with_permission(dbo, asm3.users.VIEW_CONSULTING_ROOM),
            "templates": asm3.template.get_document_templates(dbo, "clinic"),
            "rows": rows
        }

class clinic_waitingroom(JSONEndpoint):
    url = "clinic_waitingroom"
    js_module = "clinic_appointment"
    get_permissions = asm3.users.VIEW_CLINIC

    def controller(self, o):
        dbo = o.dbo
        sf = o.post.integer("filter")
        if o.post["filter"] == "": sf = -1
        rows = asm3.clinic.get_appointments_today(dbo, statusfilter = sf, siteid = o.siteid)
        asm3.al.debug("got %d appointments" % (len(rows)), "main.clinic_waitingroom", dbo)
        return {
            "name": self.url,
            "filter": sf,
            "clinicstatuses": asm3.lookups.get_clinic_statuses(dbo),
            "clinictypes": asm3.lookups.get_clinic_types(dbo),
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "paymentmethods": asm3.lookups.get_payment_methods(dbo),
            "forlist": asm3.users.get_users_with_permission(dbo, asm3.users.VIEW_CONSULTING_ROOM),
            "templates": asm3.template.get_document_templates(dbo, "clinic"),
            "rows": rows
        }

class csvexport_animals(JSONEndpoint):
    url = "csvexport_animals"
    get_permissions = asm3.users.EXPORT_REPORT

class csvexport_people(JSONEndpoint):
    url = "csvexport_people"
    get_permissions = asm3.users.EXPORT_REPORT

    def controller(self, o):
        return {
            "flags": asm3.lookups.get_person_flags(o.dbo)
        }

class csvexport_animals_ex(ASMEndpoint):
    url = "csvexport_animals_ex"
    get_permissions = asm3.users.EXPORT_REPORT

    def content(self, o):
        # If we're retrieving an already saved export, serve it.
        if o.post["get"] != "":
            self.content_type("text/csv")
            self.content_disposition("attachment", "export.csv")
            v = asm3.cachedisk.get(o.post["get"], o.dbo.name())
            if v is None: self.notfound()
            return v
        else:
            l = o.locale
            asm3.asynctask.function_task(o.dbo, _("Export Animals as CSV", l), asm3.csvimport.csvexport_animals, 
                o.dbo, o.post["filter"], o.post["animals"], o.post["where"], o.post["media"] )
            self.redirect("task")

class csvexport_people_ex(ASMEndpoint):
    url = "csvexport_people_ex"
    get_permissions = asm3.users.EXPORT_REPORT

    def content(self, o):
        # If we're retrieving an already saved export, serve it.
        if o.post["get"] != "":
            self.content_type("text/csv")
            self.content_disposition("attachment", "export.csv")
            v = asm3.cachedisk.get(o.post["get"], o.dbo.name())
            if v is None: self.notfound()
            return v
        else:
            l = o.locale
            #csvexport_people(dbo: Database, dataset: str, where: str = "", includemedia: str = "photo")
            asm3.asynctask.function_task(o.dbo, _("Export People as CSV", l), asm3.csvimport.csvexport_people, 
                o.dbo, o.post["filter"], o.post["flags"], o.post["where"], o.post["media"] )
            self.redirect("task")

class csvimport(JSONEndpoint):
    url = "csvimport"
    get_permissions = asm3.users.IMPORT_CSV_FILE
    post_permissions = asm3.users.IMPORT_CSV_FILE

    def controller(self, o):
        return { "islargedb": o.dbo.is_large_db }

    def post_all(self, o):
        l = o.locale
        # NOTE: Can't use named arguments when passing function parameters
        asm3.asynctask.function_task(o.dbo, _("Import a CSV file", l), asm3.csvimport.csvimport, 
            o.dbo, o.post.filedata(), o.post["encoding"], o.user, 
            o.post.boolean("createmissinglookups") == 1, 
            o.post.boolean("cleartables") == 1, 
            True,
            o.post.boolean("prefixanimalcodes") == 1,
            o.post.boolean("entrytoday") == 1)
        self.redirect("task")

class csvimport_paypal(JSONEndpoint):
    url = "csvimport_paypal"
    get_permissions = asm3.users.IMPORT_CSV_FILE
    post_permissions = asm3.users.IMPORT_CSV_FILE

    def controller(self, o):
        return { 
            "donationtypes": asm3.lookups.get_donation_types(o.dbo),
            "paymentmethods": asm3.lookups.get_payment_methods(o.dbo),
            "flags": asm3.lookups.get_person_flags(o.dbo)
        }

    def post_all(self, o):
        l = o.locale
        asm3.asynctask.function_task(o.dbo, _("Import a PayPal CSV file", l), asm3.csvimport.csvimport_paypal, o.dbo, \
            o.post.filedata(), o.post.integer("type"), o.post.integer("payment"), o.post["flags"], o.user, o.post["encoding"])
        self.redirect("task")

class csvimport_stripe(JSONEndpoint):
    url = "csvimport_stripe"
    get_permissions = asm3.users.IMPORT_CSV_FILE
    post_permissions = asm3.users.IMPORT_CSV_FILE

    def controller(self, o):
        return { 
            "donationtypes": asm3.lookups.get_donation_types(o.dbo),
            "paymentmethods": asm3.lookups.get_payment_methods(o.dbo),
            "flags": asm3.lookups.get_person_flags(o.dbo)
        }

    def post_all(self, o):
        l = o.locale
        asm3.asynctask.function_task(o.dbo, _("Import a Stripe CSV file", l), asm3.csvimport.csvimport_stripe, o.dbo, \
            o.post.filedata(), o.post.integer("type"), o.post.integer("payment"), o.post["flags"], o.user, o.post["encoding"])
        self.redirect("task")

class diary(ASMEndpoint):
    url = "diary"

    def post_create(self, o):
        self.check(asm3.users.ADD_DIARY)
        return asm3.diary.insert_diary_from_form(o.dbo, o.user, o.post.integer("linktypeid"), o.post.integer("linkid"), o.post)

    def post_update(self, o):
        self.check(asm3.users.EDIT_MY_DIARY_NOTES)
        asm3.diary.update_diary_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_DIARY)
        for did in o.post.integer_list("ids"):
            asm3.diary.delete_diary(o.dbo, o.user, did)

    def post_complete(self, o):
        self.check(asm3.users.BULK_COMPLETE_NOTES)
        for did in o.post.integer_list("ids"):
            asm3.diary.complete_diary_note(o.dbo, o.user, did)

class diary_edit(JSONEndpoint):
    url = "diary_edit"
    js_module = "diary"
    get_permissions = asm3.users.EDIT_ALL_DIARY_NOTES

    def controller(self, o):
        dbo = o.dbo
        dfilter = o.post["filter"]
        if dfilter == "uncompleted" or dfilter == "":
            diaries = asm3.diary.get_uncompleted_upto_today(dbo)
        elif dfilter == "completed":
            diaries = asm3.diary.get_completed_upto_today(dbo)
        elif dfilter == "future":
            diaries = asm3.diary.get_future(dbo)
        elif dfilter == "all":
            diaries = asm3.diary.get_all_upto_today(dbo)
        asm3.al.debug("got %d diaries, filter was %s" % (len(diaries), dfilter), "main.diary_edit", dbo)
        return {
            "rows": diaries,
            "newnote": o.post.integer("newnote") == 1,
            "name": "diary_edit",
            "linkid": 0,
            "linktypeid": asm3.diary.NO_LINK,
            "forlist": asm3.users.get_diary_forlist(dbo)
        }

class diary_edit_my(JSONEndpoint):
    url = "diary_edit_my"
    js_module = "diary"
    get_permissions = asm3.users.EDIT_MY_DIARY_NOTES

    def controller(self, o):
        dbo = o.dbo
        userfilter = o.user
        dfilter = o.post["filter"]
        if dfilter == "uncompleted" or dfilter == "":
            diaries = asm3.diary.get_uncompleted_upto_today(dbo, userfilter)
        elif dfilter == "completed":
            diaries = asm3.diary.get_completed_upto_today(dbo, userfilter)
        elif dfilter == "future":
            diaries = asm3.diary.get_future(dbo, userfilter)
        elif dfilter == "all":
            diaries = asm3.diary.get_all_upto_today(dbo, userfilter)
        asm3.al.debug("got %d diaries (%s), filter was %s" % (len(diaries), userfilter, dfilter), "main.diary_edit_my", dbo)
        return {
            "rows": diaries,
            "newnote": o.post.integer("newnote") == 1,
            "name": "diary_edit_my",
            "linkid": 0,
            "linktypeid": asm3.diary.NO_LINK,
            "forlist": asm3.users.get_diary_forlist(dbo)
        }

class diarytask(JSONEndpoint):
    url = "diarytask"
    get_permissions = asm3.users.EDIT_DIARY_TASKS
    post_permissions = asm3.users.EDIT_DIARY_TASKS

    def controller(self, o):
        dbo = o.dbo
        taskid = o.post.integer("taskid")
        taskname = asm3.diary.get_diarytask_name(dbo, taskid)
        diarytaskdetail = asm3.diary.get_diarytask_details(dbo, taskid)
        asm3.al.debug("got %d diary task details" % len(diarytaskdetail), "main.diarytask", dbo)
        return {
            "rows": diarytaskdetail,
            "taskid": taskid,
            "taskname": taskname,
            "forlist": asm3.users.get_diary_forlist(dbo)
        }

    def post_create(self, o):
        return asm3.diary.insert_diarytaskdetail_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        asm3.diary.update_diarytaskdetail_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        for did in o.post.integer_list("ids"):
            asm3.diary.delete_diarytaskdetail(o.dbo, o.user, did)
    
    def post_exec(self, o):
        self.check(asm3.users.ADD_DIARY)
        asm3.diary.execute_diary_task(o.dbo, o.user, o.post["tasktype"], o.post.integer("taskid"), o.post.integer("id"), o.post.date("seldate"))

class diarytasks(JSONEndpoint):
    url = "diarytasks"
    get_permissions = asm3.users.EDIT_DIARY_TASKS
    post_permissions = asm3.users.EDIT_DIARY_TASKS

    def controller(self, o):
        dbo = o.dbo
        diarytaskhead = asm3.diary.get_diarytasks(dbo)
        asm3.al.debug("got %d diary tasks" % len(diarytaskhead), "main.diarytasks", dbo)
        return {
            "rows": diarytaskhead
        }

    def post_create(self, o):
        return asm3.diary.insert_diarytaskhead_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        asm3.diary.update_diarytaskhead_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        for did in o.post.integer_list("ids"):
            asm3.diary.delete_diarytask(o.dbo, o.user, did)

class document_gen(ASMEndpoint):
    url = "document_gen"
    get_permissions = asm3.users.GENERATE_DOCUMENTS

    def content(self, o):
        dbo = o.dbo
        post = o.post
        linktype = post["linktype"]
        if post["id"] == "" or post["id"] == "0": raise asm3.utils.ASMValidationError("no id parameter")
        dtid = post.integer("dtid")
        templatename = asm3.template.get_document_template_name(dbo, dtid)
        title = templatename
        loglinktype = asm3.log.ANIMAL
        asm3.al.debug("generating %s document for %d, template '%s'" % (linktype, post.integer("id"), templatename), "main.document_gen", dbo)
        logid = post.integer("id")
        if linktype == "ANIMAL" or linktype == "":
            loglinktype = asm3.log.ANIMAL
            content = asm3.wordprocessor.generate_animal_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "ANIMALCONTROL":
            loglinktype = asm3.log.ANIMALCONTROL
            content = asm3.wordprocessor.generate_animalcontrol_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "BOARDING":
            loglinktype = asm3.log.PERSON
            content = asm3.wordprocessor.generate_boarding_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "CLINIC":
            loglinktype = asm3.log.PERSON
            content = asm3.wordprocessor.generate_clinic_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "PERSON":
            loglinktype = asm3.log.PERSON
            content = asm3.wordprocessor.generate_person_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "DONATION":
            loglinktype = asm3.log.PERSON
            logid = asm3.financial.get_donation(dbo, post.integer_list("id")[0])["OWNERID"]
            content = asm3.wordprocessor.generate_donation_doc(dbo, dtid, post.integer_list("id"), o.user)
        elif linktype == "FOUNDANIMAL":
            loglinktype = asm3.log.FOUNDANIMAL
            logid = asm3.lostfound.get_foundanimal(dbo, post.integer("id"))["OWNERID"]
            content = asm3.wordprocessor.generate_foundanimal_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "LOSTANIMAL":
            loglinktype = asm3.log.LOSTANIMAL
            logid = asm3.lostfound.get_lostanimal(dbo, post.integer("id"))["OWNERID"]
            content = asm3.wordprocessor.generate_lostanimal_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "LICENCE":
            loglinktype = asm3.log.PERSON
            logid = asm3.financial.get_licence(dbo, post.integer("id"))["OWNERID"]
            content = asm3.wordprocessor.generate_licence_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "MEDICAL":
            loglinktype = asm3.log.ANIMAL
            logid = asm3.medical.get_regimen_id(dbo, post.integer_list("id")[0])["ANIMALID"]
            content = asm3.wordprocessor.generate_medical_doc(dbo, dtid, post.integer_list("id"), o.user)
        elif linktype == "MOVEMENT":
            loglinktype = asm3.log.PERSON
            logid = asm3.movement.get_movement(dbo, post.integer("id"))["OWNERID"]
            content = asm3.wordprocessor.generate_movement_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "TRANSPORT":
            loglinktype = asm3.log.ANIMAL
            logid = asm3.movement.get_transport(dbo, post.integer_list("id")[0])["ANIMALID"]
            content = asm3.wordprocessor.generate_transport_doc(dbo, dtid, post.integer_list("id"), o.user)
        elif linktype == "VOUCHER":
            loglinktype = asm3.log.PERSON
            logid = asm3.financial.get_voucher(dbo, post.integer("id"))["OWNERID"]
            content = asm3.wordprocessor.generate_voucher_doc(dbo, dtid, post.integer("id"), o.user)
        elif linktype == "WAITINGLIST":
            loglinktype = asm3.log.WAITINGLIST
            logid = asm3.waitinglist.get_waitinglist_by_id(dbo, post.integer("id"))["OWNERID"]
            content = asm3.wordprocessor.generate_waitinglist_doc(dbo, dtid, post.integer("id"), o.user)
        if asm3.configuration.generate_document_log(dbo) and asm3.configuration.generate_document_log_type(dbo) > 0:
            asm3.log.add_log(dbo, o.user, loglinktype, logid, asm3.configuration.generate_document_log_type(dbo), _("Generated document '{0}'").format(templatename))
        if templatename.endswith(".html"):
            self.content_type("text/html")
            self.cache_control(0)
            return asm3.html.tinymce_header(title, "document_edit.js", visualaids=False, jswindowprint=asm3.configuration.js_window_print(dbo)) + \
                asm3.html.tinymce_main(dbo.locale, "document_gen", recid=post["id"], linktype=post["linktype"], \
                    dtid=dtid, content=asm3.utils.escape_tinymce(content))
        elif templatename.endswith(".odt"):
            self.content_type("application/vnd.oasis.opendocument.text")
            self.content_disposition("attachment", templatename)
            self.cache_control(0)
            return content

    def post_save(self, o):
        self.check(asm3.users.ADD_MEDIA)
        dbo = o.dbo
        post = o.post
        linktype = post["linktype"]
        dtid = post.integer("dtid")
        tempname = asm3.template.get_document_template_name(dbo, dtid)
        recid = post.integer("recid")
        if linktype == "ANIMAL":
            tempname += " - " + asm3.animal.get_animal_namecode(dbo, recid)
            asm3.media.create_document_media(dbo, o.user, asm3.media.ANIMAL, recid, tempname, post["document"])
            self.redirect("animal_media?id=%d" % recid)
        elif linktype == "ANIMALCONTROL":
            tempname += " - " + asm3.utils.padleft(recid, 6)
            asm3.media.create_document_media(dbo, o.user, asm3.media.ANIMALCONTROL, recid, tempname, post["document"])
            self.redirect("incident_media?id=%d" % recid)
        elif linktype == "BOARDING":
            m = asm3.movement.get_movement(dbo, recid)
            if m is None:
                raise asm3.utils.ASMValidationError("%d is not a valid movement id" % recid)
            animalid = m["ANIMALID"]
            ownerid = m["OWNERID"]
            tempname = "%s - %s::%s" % (tempname, asm3.animal.get_animal_namecode(dbo, animalid), asm3.person.get_person_name(dbo, ownerid))
            if animalid and ownerid: 
                asm3.media.create_document_animalperson(dbo, o.user, animalid, ownerid, tempname, post["document"])
            elif ownerid: 
                asm3.media.create_document_media(dbo, o.user, asm3.media.PERSON, ownerid, tempname, post["document"])
            elif animalid: 
                asm3.media.create_document_media(dbo, o.user, asm3.media.ANIMAL, animalid, tempname, post["document"])
            self.redirect("animal_media?id=%d" % animalid)
        elif linktype == "CLINIC":
            c = asm3.clinic.get_appointment(dbo, recid)
            if c is None:
                raise asm3.utils.ASMValidationError("%d is not a valid clinic id" % recid)
            animalid = c["ANIMALID"]
            ownerid = c["OWNERID"]
            if ownerid: 
                tempname = "%s - %s" % (tempname, asm3.person.get_person_name(dbo, ownerid))
                asm3.media.create_document_media(dbo, o.user, asm3.media.PERSON, ownerid, tempname, post["document"])
                self.redirect("person_media?id=%d" % ownerid)
            else:
                tempname = "%s - %s" % (tempname, asm3.animal.get_animal_namecode(dbo, animalid))
                asm3.media.create_document_media(dbo, o.user, asm3.media.ANIMAL, animalid, tempname, post["document"])
                self.redirect("animal_media?id=%d" % animalid)
        elif linktype == "DONATION":
            d = asm3.financial.get_donations_by_ids(dbo, post.integer_list("recid"))
            if len(d) == 0:
                raise asm3.utils.ASMValidationError("list '%s' does not contain valid ids" % recid)
            ownerid = d[0]["OWNERID"]
            tempname += " - " + asm3.person.get_person_name(dbo, ownerid)
            asm3.media.create_document_media(dbo, o.user, asm3.media.PERSON, ownerid, tempname, post["document"])
            self.redirect("person_media?id=%d" % ownerid)
        elif linktype == "FOUNDANIMAL":
            tempname += " - " + asm3.utils.padleft(recid, 6)
            asm3.media.create_document_media(dbo, o.user, asm3.media.FOUNDANIMAL, recid, tempname, post["document"])
            self.redirect("foundanimal_media?id=%d" % recid)
        elif linktype == "LOSTANIMAL":
            tempname += " - " + asm3.utils.padleft(recid, 6)
            asm3.media.create_document_media(dbo, o.user, asm3.media.LOSTANIMAL, recid, tempname, post["document"])
            self.redirect("lostanimal_media?id=%d" % recid)
        elif linktype == "MEDICAL":
            d = asm3.medical.get_regimens_ids(dbo, post.integer_list("recid"))
            if len(d) == 0:
                raise asm3.utils.ASMValidationError("list '%s' does not contain valid ids" % recid)
            animalid = d[0]["ANIMALID"]
            tempname += " - " + asm3.animal.get_animal_name(dbo, animalid)
            asm3.media.create_document_media(dbo, o.user, asm3.media.ANIMAL, animalid, tempname, post["document"])
            self.redirect("animal_media?id=%d" % animalid)
        elif linktype == "PERSON":
            tempname += " - " + asm3.person.get_person_name(dbo, recid)
            asm3.media.create_document_media(dbo, o.user, asm3.media.PERSON, recid, tempname, post["document"])
            self.redirect("person_media?id=%d" % recid)
        elif linktype == "WAITINGLIST":
            tempname += " - " + asm3.utils.padleft(recid, 6)
            asm3.media.create_document_media(dbo, o.user, asm3.media.WAITINGLIST, recid, tempname, post["document"])
            self.redirect("waitinglist_media?id=%d" % recid)
        elif linktype == "TRANSPORT":
            t = asm3.movement.get_transports_by_ids(dbo, post.integer_list("recid"))
            if len(t) == 0:
                raise asm3.utils.ASMValidationError("list '%s' does not contain valid ids" % recid)
            animalid = t[0]["ANIMALID"]
            tempname += " - " + asm3.animal.get_animal_namecode(dbo, animalid)
            asm3.media.create_document_media(dbo, o.user, asm3.media.ANIMAL, animalid, tempname, post["document"])
            self.redirect("animal_media?id=%d" % animalid)
        elif linktype == "VOUCHER":
            v = asm3.financial.get_voucher(dbo, recid)
            if v is None:
                raise asm3.utils.ASMValidationError("%d is not a valid voucher id" % recid)
            ownerid = v["OWNERID"]
            tempname += " - " + asm3.person.get_person_name(dbo, ownerid)
            asm3.media.create_document_media(dbo, o.user, asm3.media.PERSON, ownerid, tempname, post["document"])
            self.redirect("person_media?id=%d" % ownerid)
        elif linktype == "LICENCE":
            l = asm3.financial.get_licence(dbo, recid)
            if l is None:
                raise asm3.utils.ASMValidationError("%d is not a valid licence id" % recid)
            animalid = l["ANIMALID"]
            ownerid = l["OWNERID"]
            tempname += " - " + asm3.person.get_person_name(dbo, ownerid)
            if animalid and ownerid: 
                asm3.media.create_document_animalperson(dbo, o.user, animalid, ownerid, tempname, post["document"])
            elif ownerid: 
                asm3.media.create_document_media(dbo, o.user, asm3.media.PERSON, ownerid, tempname, post["document"])
            elif animalid: 
                asm3.media.create_document_media(dbo, o.user, asm3.media.ANIMAL, animalid, tempname, post["document"])
            self.redirect("person_media?id=%d" % ownerid)
        elif linktype == "MOVEMENT":
            m = asm3.movement.get_movement(dbo, recid)
            if m is None:
                raise asm3.utils.ASMValidationError("%d is not a valid movement id" % recid)
            animalid = m["ANIMALID"]
            ownerid = m["OWNERID"]
            tempname = "%s - %s::%s" % (tempname, asm3.animal.get_animal_namecode(dbo, animalid), asm3.person.get_person_name(dbo, ownerid))
            if animalid and ownerid: 
                asm3.media.create_document_animalperson(dbo, o.user, animalid, ownerid, tempname, post["document"])
            elif ownerid: 
                asm3.media.create_document_media(dbo, o.user, asm3.media.PERSON, ownerid, tempname, post["document"])
            elif animalid: 
                asm3.media.create_document_media(dbo, o.user, asm3.media.ANIMAL, animalid, tempname, post["document"])
            self.redirect("animal_media?id=%d" % animalid)
        else:
            raise asm3.utils.ASMValidationError("Linktype '%s' is invalid, cannot save" % linktype)

    def post_emailtemplate(self, o):
        self.content_type("text/html")
        content = ""
        if o.post["donationids"] != "":
            content = asm3.wordprocessor.generate_donation_doc(o.dbo, o.post.integer("dtid"), o.post.integer_list("donationids"), o.user)
        elif o.post.integer("personid") != 0:
            content = asm3.wordprocessor.generate_person_doc(o.dbo, o.post.integer("dtid"), o.post.integer("personid"), o.user)
        elif o.post.integer("animalid") != 0:
            content = asm3.wordprocessor.generate_animal_doc(o.dbo, o.post.integer("dtid"), o.post.integer("animalid"), o.user)
        elif o.post.integer("animalcontrolid") != 0:
            content = asm3.wordprocessor.generate_animalcontrol_doc(o.dbo, o.post.integer("dtid"), o.post.integer("animalcontrolid"), o.user)
        elif o.post.integer("licenceid") != 0:
            content = asm3.wordprocessor.generate_licence_doc(o.dbo, o.post.integer("dtid"), o.post.integer("licenceid"), o.user)
        else:
            content = asm3.template.get_document_template_content(o.dbo, o.post.integer("dtid"))
        tokens = asm3.wordprocessor.extract_mail_tokens(content)
        return asm3.utils.json(tokens)

    def post_pdf(self, o):
        self.check(asm3.users.VIEW_MEDIA)
        dbo = o.dbo
        post = o.post
        disp = asm3.configuration.pdf_inline(dbo) and "inline" or "attachment"
        self.content_type("application/pdf")
        self.content_disposition(disp, "doc.pdf")
        return asm3.utils.html_to_pdf(dbo, post["document"])

    def post_print(self, o):
        self.check(asm3.users.VIEW_MEDIA)
        l = o.locale
        post = o.post
        self.content_type("text/html")
        return "%s%s%s" % (asm3.html.tinymce_print_header(_("Print Preview", l)), post["document"], "</body></html>")

class document_template_edit(ASMEndpoint):
    url = "document_template_edit"
    get_permissions = asm3.users.MODIFY_DOCUMENT_TEMPLATES
    post_permissions = asm3.users.MODIFY_DOCUMENT_TEMPLATES

    def content(self, o):
        dbo = o.dbo
        post = o.post
        dtid = post.integer("dtid")
        templatename = asm3.template.get_document_template_name(dbo, dtid)
        if templatename == "": self.notfound()
        title = templatename
        asm3.al.debug("editing %s" % templatename, "main.document_template_edit", dbo)
        if templatename.endswith(".html"):
            content = asm3.utils.escape_tinymce(asm3.template.get_document_template_content(dbo, dtid))
            self.content_type("text/html")
            self.cache_control(0)
            return asm3.html.tinymce_header(title, "document_edit.js", jswindowprint=asm3.configuration.js_window_print(dbo)) + \
                asm3.html.tinymce_main(dbo.locale, "document_template_edit", dtid=dtid, content=content)
        elif templatename.endswith(".odt"):
            content = asm3.template.get_document_template_content(dbo, dtid)
            self.content_type("application/vnd.oasis.opendocument.text")
            self.cache_control(0)
            return content

    def post_save(self, o):
        dbo = o.dbo
        post = o.post
        sz = len(post["document"])
        if sz > MAX_DOCUMENT_TEMPLATE_SIZE:
            raise asm3.utils.ASMValidationError(f"Error: {sz} > {MAX_DOCUMENT_TEMPLATE_SIZE}. Use extra images instead of pasting images.")
        dtid = post.integer("dtid")
        asm3.template.update_document_template_content(dbo, o.user, dtid, post["document"])
        self.redirect("document_templates")

    def post_pdf(self, o):
        dbo = o.dbo
        post = o.post
        disp = asm3.configuration.pdf_inline(dbo) and "inline" or "attachment"
        self.content_type("application/pdf")
        self.content_disposition(disp, "doc.pdf")
        return asm3.utils.html_to_pdf(dbo, post["document"])

    def post_print(self, o):
        post = o.post
        l = o.locale
        self.content_type("text/html")
        return "%s%s%s" % (asm3.html.tinymce_print_header(_("Print Preview", l)), post["document"], "</body></html>")

class document_media_edit(ASMEndpoint):
    url = "document_media_edit"
    get_permissions = asm3.users.VIEW_MEDIA

    def content(self, o):
        dbo = o.dbo
        post = o.post
        lastmod, medianame, mimetype, filedata = asm3.media.get_media_file_data(dbo, post.integer("id"))
        readonly = asm3.media.has_signature(dbo, post.integer("id"))
        asm3.al.debug("editing media %d" % post.integer("id"), "main.document_media_edit", dbo)
        title = medianame
        self.content_type("text/html")
        return asm3.html.tinymce_header(title, "document_edit.js", jswindowprint=asm3.configuration.js_window_print(dbo), \
            visualaids=not readonly, onlysavewhendirty=False, readonly=readonly) + \
            asm3.html.tinymce_main(dbo.locale, "document_media_edit", mediaid=post.integer("id"), redirecturl=post["redirecturl"], \
                content=asm3.utils.escape_tinymce(filedata))

    def post_save(self, o):
        self.check(asm3.users.CHANGE_MEDIA)
        try:
            asm3.media.update_file_content(o.dbo, o.user, o.post.integer("mediaid"), o.post["document"])
        except Exception as err:
            raise asm3.utils.ASMError(str(err)) # see a lot of errors where mediaid is 0 for some reason
        raise self.redirect(o.post["redirecturl"])

    def post_pdf(self, o):
        self.check(asm3.users.VIEW_MEDIA)
        dbo = o.dbo
        disp = asm3.configuration.pdf_inline(dbo) and "inline" or "attachment"
        self.content_type("application/pdf")
        self.content_disposition(disp, "doc.pdf")
        return asm3.utils.html_to_pdf(dbo, o.post["document"])

    def post_print(self, o):
        self.check(asm3.users.VIEW_MEDIA)
        l = o.locale
        self.content_type("text/html")
        return "%s%s%s" % (asm3.html.tinymce_print_header(_("Print Preview", l)), o.post["document"], "</body></html>")

class document_repository(JSONEndpoint):
    url = "document_repository"
    get_permissions = asm3.users.VIEW_REPO_DOCUMENT

    def controller(self, o):
        documents = asm3.dbfs.get_document_repository(o.dbo)
        asm3.al.debug("got %d documents in repository" % len(documents), "main.document_repository", o.dbo)
        return { 
            "rows": documents,
            "templates": asm3.template.get_document_templates(o.dbo, "email")
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_REPO_DOCUMENT)
        if o.post["filename"] != "":
            # If filename is supplied it's an HTML5 upload
            filename = o.post["filename"]
            filedata = o.post["filedata"]
            # Strip the data URL and decode
            if filedata.startswith("data:"):
                filedata = filedata[filedata.find(",")+1:]
                filedata = filedata.replace(" ", "+") # Unescape turns pluses back into spaces, which breaks base64
            filedata = asm3.utils.base64decode(filedata)
        else:
            # Otherwise it's an old style file input
            filename = asm3.utils.filename_only(o.post.data.filechooser.filename)
            filedata = o.post.data.filechooser.value
        asm3.dbfs.upload_document_repository(o.dbo, o.post["path"], filename, filedata)
        self.redirect("document_repository")

    def post_delete(self, o):
        self.check(asm3.users.DELETE_REPO_DOCUMENT)
        for i in o.post.integer_list("ids"):
            asm3.dbfs.delete_id(o.dbo, i)

    def post_email(self, o):
        self.check(asm3.users.EMAIL_PERSON)
        dbo = o.dbo
        post = o.post
        attachments = []
        for dbfsid in post.integer_list("ids"):
            name = asm3.dbfs.get_name_for_id(dbo, dbfsid)
            content = asm3.dbfs.get_string_id(dbo, dbfsid)
            attachments.append(( name, asm3.media.mime_type(name), content ))
        asm3.utils.send_email(dbo, post["from"], post["to"], post["cc"], post["bcc"], post["subject"], post["body"], "html", attachments)
        if asm3.configuration.audit_on_send_email(dbo): 
            asm3.audit.email(dbo, o.user, post["from"], post["to"], post["cc"], post["bcc"], post["subject"], post["body"])
        return post["to"]

    def post_rename(self, o):
        asm3.dbfs.rename_file(o.dbo, o.post["path"], o.post["oldname"], o.post["newname"])

class document_repository_file(ASMEndpoint):
    url = "document_repository_file"
    get_permissions = asm3.users.VIEW_REPO_DOCUMENT

    def content(self, o):
        if o.post.integer("dbfsid") != 0:
            name = asm3.dbfs.get_name_for_id(o.dbo, o.post.integer("dbfsid"))
            mimetype = asm3.media.mime_type(name)
            disp = "attachment"
            if mimetype == "application/pdf": disp = "inline" # Try to show PDFs in place
            self.content_type(mimetype)
            self.content_disposition(disp, name)
            return asm3.dbfs.get_string_id(o.dbo, o.post.integer("dbfsid"))

class document_templates(JSONEndpoint):
    url = "document_templates"
    get_permissions = asm3.users.MODIFY_DOCUMENT_TEMPLATES
    post_permissions = asm3.users.MODIFY_DOCUMENT_TEMPLATES

    def controller(self, o):
        templates = asm3.template.get_document_templates(o.dbo)
        asm3.al.debug("got %d document templates" % len(templates), "main.document_templates", o.dbo)
        return {
            "rows": templates,
            "defaults": asm3.template.get_document_templates_defaults(o.dbo)
        }

    def post_create(self, o):
        return asm3.template.create_document_template(o.dbo, o.user, o.post["template"], show = o.post["show"])

    def post_clone(self, o):
        for t in o.post.integer_list("ids"):
            return asm3.template.clone_document_template(o.dbo, o.user, t, o.post["template"])

    def post_delete(self, o):
        for t in o.post.integer_list("ids"):
            asm3.template.delete_document_template(o.dbo, o.user, t)

    def post_reload(self, o):
        for name in o.post["names"].split(","):
            content = asm3.utils.read_binary_file(f"{PATH}media/templates/{name}")
            asm3.template.create_document_template(o.dbo, o.user, name, show="nowhere", content=content)

    def post_rename(self, o):
        asm3.template.rename_document_template(o.dbo, o.user, o.post.integer("dtid"), o.post["newname"])

    def post_upload(self, o):
        post = o.post
        fname = post.filename()
        ext = fname[fname.rfind("."):]
        if ext not in (".html", ".odt"): raise asm3.utils.ASMValidationError("Document template files must be .html or .odt")
        if post["uploadpath"] != "": fname = post["uploadpath"] + "/" + fname
        asm3.template.create_document_template(o.dbo, o.user, fname, ext, post.filedata(), show = o.post["uploadshow"])
        self.redirect("document_templates")

    def post_show(self, o):
        for t in o.post.integer_list("ids"):
            asm3.template.update_document_template_show(o.dbo, o.user, t, o.post["newshow"])

class donation(JSONEndpoint):
    url = "donation"
    js_module = "donations"
    get_permissions = asm3.users.VIEW_DONATION

    def controller(self, o):
        dbo = o.dbo
        offset = o.post["offset"]
        if offset == "": offset = "m0"
        donations = asm3.financial.get_donations(dbo, offset)
        asm3.al.debug("got %d donations" % (len(donations)), "main.donation", dbo)
        return {
            "name": "donation",
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "accounts": asm3.financial.get_accounts(dbo, onlybank=True),
            "logtypes": asm3.lookups.get_log_types(dbo), 
            "paymentmethods": asm3.lookups.get_payment_methods(dbo),
            "frequencies": asm3.lookups.get_donation_frequencies(dbo),
            "templates": asm3.template.get_document_templates(dbo, "payment"),
            "rows": donations
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_DONATION)
        return "%s|%s" % (asm3.financial.insert_donation_from_form(o.dbo, o.user, o.post), o.post["receiptnumber"])

    def post_update(self, o):
        self.check(asm3.users.CHANGE_DONATION)
        asm3.financial.update_donation_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_DONATION)
        for did in o.post.integer_list("ids"):
            asm3.financial.delete_donation(o.dbo, o.user, did)

    def post_tokencharge(self, o):
        self.check(asm3.users.CHANGE_DONATION)
        dbo = o.dbo
        post = o.post
        title = post["title"]
        installments = post["installments"] # number of payments to pass to cardcom
        processor = asm3.financial.get_payment_processor(dbo, post["processor"])
        if not processor.validatePaymentReference(post["payref"]):
            return (asm3.utils.json({"error": "Invalid payref"}))
        if processor.isPaymentReceived(post["payref"]):
            return (asm3.utils.json({"error": "Expired payref"}))
        try:
            processor.tokenCharge(post["payref"], title, installments)
            return (asm3.utils.json({"message": _("Successful token charge.")}))
        except Exception as e:
            return (asm3.utils.json({"error": str(e)}))

    def post_popuprequest(self, o):
        self.check(asm3.users.CHANGE_DONATION)
        dbo = o.dbo
        post = o.post
        title = post["title"]
        processor = asm3.financial.get_payment_processor(dbo, post["processor"])
        if not processor.validatePaymentReference(post["payref"]):
            return (asm3.utils.json({"error": "Invalid payref"}))
        if processor.isPaymentReceived(post["payref"]):
            return (asm3.utils.json({"error": "Expired payref"}))
        return_url = post["return"] or asm3.configuration.payment_return_url(dbo)
        try:
            url = processor.checkoutUrl(post["payref"], return_url, title)
            return (asm3.utils.json({"url": url}))
        except Exception as e:
            return (asm3.utils.json({"error": str(e)}))

    def post_emailrequest(self, o):
        self.check(asm3.users.EMAIL_PERSON)
        dbo = o.dbo
        l = o.locale
        post = o.post
        emailadd = post["to"]
        body = post["body"]
        params = { 
            "account": dbo.name(), 
            "method": "checkout",
            "processor": post["processor"],
            "payref": post["payref"],
            "title": post["subject"] 
        }
        url = "%s?%s" % (SERVICE_URL, asm3.utils.urlencode(params))
        body = asm3.utils.replace_url_token(body, url, _("Click here to pay", l))
        if post.boolean("addtolog"):
            asm3.log.add_log_email(dbo, o.user, asm3.log.PERSON, post.integer("person"), post.integer("logtype"), 
                emailadd, post["subject"], body)
        asm3.utils.send_email(dbo, post["from"], emailadd, post["cc"], post["bcc"], post["subject"], body, "html")
        if asm3.configuration.audit_on_send_email(dbo): 
            asm3.audit.email(dbo, o.user, post["from"], emailadd, post["cc"], post["bcc"], post["subject"], body)
        return emailadd

    def post_nextreceipt(self, o):
        return asm3.financial.get_next_receipt_number(o.dbo)

    def post_receive(self, o):
        self.check( asm3.users.CHANGE_DONATION)
        for did in o.post.integer_list("ids"):
            asm3.financial.receive_donation(o.dbo, o.user, did)

    def post_personmovements(self, o):
        self.check(asm3.users.VIEW_MOVEMENT)
        self.content_type("application/json")
        return asm3.utils.json(asm3.movement.get_person_movements(o.dbo, o.post.integer("personid")))

class donation_receive(JSONEndpoint):
    url = "donation_receive"
    get_permissions = asm3.users.ADD_DONATION

    def controller(self, o):
        dbo = o.dbo
        asm3.al.debug("receiving donation", "main.donation_receive", dbo)
        return {
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "paymentmethods": asm3.lookups.get_payment_methods(dbo),
            "accounts": asm3.financial.get_accounts(dbo, onlybank=True)
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_DONATION)
        return asm3.financial.insert_donations_from_form(o.dbo, o.user, o.post, o.post["received"], True, o.post["person"], o.post["animal"], o.post["movement"], False)

class event(JSONEndpoint):
    url = "event"
    get_permissions = asm3.users.VIEW_EVENT

    def controller(self, o):
        dbo = o.dbo
        e = asm3.event.get_event(dbo, o.post.integer("id"))
        if e is None: self.notfound()
        asm3.al.debug("opened event %s" % "recname", "main.event", dbo)
        return {
            "event": e,
            "additional": asm3.additional.get_additional_fields(dbo, e["ID"], "event")
        }

    def post_save(self, o):
        self.check(asm3.users.CHANGE_EVENT)
        asm3.event.update_event_from_form(o.dbo, o.post, o.user)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_EVENT)
        asm3.event.delete_event(o.dbo, o.user, o.post.integer("eventid"))

class event_animals(JSONEndpoint):
    url = "event_animals"
    get_permissions = asm3.users.VIEW_EVENT_ANIMALS

    def controller(self, o):
        dbo = o.dbo
        event_id = o.post.integer("id")
        e = asm3.event.get_event(dbo, o.post.integer("id"))
        if e is None: self.notfound()
        queryfilter = o.post["filter"]
        ea = asm3.event.get_animals_by_event(dbo, event_id, queryfilter)
        asm3.al.debug("opened event animals %s" % event_id, "main.event_animals", dbo)
        return {
            "rows": ea,
            "name": "event_animals",
            "event": e,
            "additional": asm3.additional.get_additional_fields(dbo, e["ID"], "event")
        }

    def post_create(self, o):
        self.check(asm3.users.CHANGE_EVENT_ANIMALS)
        asm3.event.insert_event_animal(o.dbo, o.user, o.post)

    def post_createbulk(self, o):
        self.check(asm3.users.CHANGE_EVENT_ANIMALS)
        for animalid in o.post.integer_list("animals"):
            o.post.data["animalid"] = str(animalid)
            asm3.event.insert_event_animal(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_EVENT_ANIMALS)
        asm3.event.update_event_animal(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.CHANGE_EVENT_ANIMALS)
        for eaid in o.post.integer_list("ids"):
            asm3.event.delete_event_animal(o.dbo, o.user, eaid)

    def post_arrived(self, o):
        self.check(asm3.users.CHANGE_EVENT_ANIMALS)
        for eaid in o.post.integer_list("ids"):
            asm3.event.update_event_animal_arrived(o.dbo, o.user, eaid)

    def post_endactivefoster(self, o):
        self.check(asm3.users.CHANGE_EVENT_ANIMALS) # TODO: change permission check
        for eaid in o.post.integer_list("ids"):
            asm3.event.end_active_foster(o.dbo, o.user, eaid)


class event_find(JSONEndpoint):
    url = "event_find"
    get_permissions = asm3.users.VIEW_EVENT

    def controller(self, o):
        return {}

class event_find_results(JSONEndpoint):
    url = "event_find_results"
    get_permissions = asm3.users.VIEW_EVENT

    def controller(self, o):
        results = asm3.event.get_event_find_advanced(o.dbo, o.post.data, asm3.configuration.record_search_limit(o.dbo))
        add = None
        if len(results) > 0: 
            add = asm3.additional.get_additional_fields_ids(o.dbo, results, "event")
        asm3.al.debug("found %d results for %s" % (len(results), self.query()), "main.event_find_results", o.dbo)
        return {
            "additional": add,
            "rows": results
        }

class event_new(JSONEndpoint):
    url = "event_new"
    get_permissions = asm3.users.ADD_EVENT
    post_permissions = asm3.users.ADD_EVENT

    def controller(self, o):
        dbo = o.dbo
        asm3.al.debug("add event", "main.event_new", dbo)
        return {
            "additional": asm3.additional.get_additional_fields(dbo, 0, "event")
        }

    def post_all(self, o):
        return str(asm3.event.insert_event_from_form(o.dbo, o.post, o.user))

class foundanimal(JSONEndpoint):
    url = "foundanimal"
    js_module = "lostfound"
    get_permissions = asm3.users.VIEW_FOUND_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        a = asm3.lostfound.get_foundanimal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        recname = "%s %s %s" % (a.AGEGROUP, a.SPECIESNAME, a.OWNERNAME)
        if asm3.configuration.audit_on_view_record(dbo): asm3.audit.view_record(dbo, o.user, "animalfound", a["ID"], recname)
        asm3.al.debug("open found animal %s" % recname, "main.foundanimal", dbo)
        return {
            "animal": a,
            "name": "foundanimal",
            "additional": asm3.additional.get_additional_fields(dbo, a["ID"], "foundanimal"),
            "agegroups": asm3.configuration.age_groups(dbo),
            "audit": self.checkb(asm3.users.VIEW_AUDIT_TRAIL) and asm3.audit.get_audit_for_link(dbo, "animalfound", a["ID"]) or [],
            "breeds": asm3.lookups.get_breeds_by_species(dbo),
            "colours": asm3.lookups.get_basecolours(dbo),
            "logtypes": asm3.lookups.get_log_types(dbo),
            "sexes": asm3.lookups.get_sexes(dbo),
            "species": asm3.lookups.get_species(dbo),
            "templates": asm3.template.get_document_templates(dbo, "foundanimal"),
            "templatesemail": asm3.template.get_document_templates(dbo, "email"),
            "tabcounts": asm3.lostfound.get_foundanimal_satellite_counts(dbo, a["LFID"])[0]
        }

    def post_save(self, o):
        self.check(asm3.users.CHANGE_FOUND_ANIMAL)
        asm3.lostfound.update_foundanimal_from_form(o.dbo, o.post, o.user)

    def post_email(self, o):
        self.check(asm3.users.EMAIL_PERSON)
        asm3.lostfound.send_email_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_FOUND_ANIMAL)
        asm3.lostfound.delete_foundanimal(o.dbo, o.user, o.post.integer("id"))

    def post_toanimal(self, o):
        self.check(asm3.users.ADD_ANIMAL)
        return str(asm3.lostfound.create_animal_from_found(o.dbo, o.user, o.post.integer("id")))

    def post_towaitinglist(self, o):
        self.check(asm3.users.ADD_WAITING_LIST)
        return str(asm3.lostfound.create_waitinglist_from_found(o.dbo, o.user, o.post.integer("id")))

class foundanimal_diary(JSONEndpoint):
    url = "foundanimal_diary"
    js_module = "diary"
    get_permissions = asm3.users.VIEW_DIARY

    def controller(self, o):
        dbo = o.dbo
        a = asm3.lostfound.get_foundanimal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        diaries = asm3.diary.get_diaries(dbo, asm3.diary.FOUNDANIMAL, o.post.integer("id"))
        asm3.al.debug("got %d diaries for found animal %s %s %s" % (len(diaries), a["AGEGROUP"], a["SPECIESNAME"], a["OWNERNAME"]), "main.foundanimal_diary", dbo)
        return {
            "rows": diaries,
            "animal": a,
            "tabcounts": asm3.lostfound.get_foundanimal_satellite_counts(dbo, a["LFID"])[0],
            "name": "foundanimal_diary",
            "linkid": a["LFID"],
            "linktypeid": asm3.diary.FOUNDANIMAL,
            "forlist": asm3.users.get_diary_forlist(dbo)
        }

class foundanimal_find(JSONEndpoint):
    url = "foundanimal_find"
    js_module = "lostfound_find"
    get_permissions = asm3.users.VIEW_FOUND_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        return {
            "additionalfields": asm3.additional.get_additional_fields(dbo, 0, "foundanimal"),
            "agegroups": asm3.configuration.age_groups(dbo),
            "colours": asm3.lookups.get_basecolours(dbo),
            "name": "foundanimal_find",
            "species": asm3.lookups.get_species(dbo),
            "breeds": asm3.lookups.get_breeds_by_species(dbo),
            "sexes": asm3.lookups.get_sexes(dbo),
            "mode": "found"
        }

class foundanimal_find_results(JSONEndpoint):
    url = "foundanimal_find_results"
    js_module = "lostfound_find_results"
    get_permissions = asm3.users.VIEW_FOUND_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        results = asm3.lostfound.get_foundanimal_find_advanced(dbo, o.post.data, asm3.configuration.record_search_limit(dbo))
        add = None
        if len(results) > 0: 
            add = asm3.additional.get_additional_fields_ids(dbo, results, "foundanimal")
        asm3.al.debug("found %d results for %s" % (len(results), self.query()), "main.foundanimal_find_results", dbo)
        return {
            "additional": add,
            "rows": results,
            "name": "foundanimal_find_results"
        }

class foundanimal_log(JSONEndpoint):
    url = "foundanimal_log"
    js_module = "log"
    get_permissions = asm3.users.VIEW_LOG

    def controller(self, o):
        dbo = o.dbo
        logfilter = o.post.integer("filter")
        if logfilter == 0: logfilter = asm3.configuration.default_log_filter(dbo)
        a = asm3.lostfound.get_foundanimal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        logs = asm3.log.get_logs(dbo, asm3.log.FOUNDANIMAL, o.post.integer("id"), logfilter)
        return {
            "name": "foundanimal_log",
            "linkid": o.post.integer("id"),
            "linktypeid": asm3.log.FOUNDANIMAL,
            "filter": logfilter,
            "rows": logs,
            "animal": a,
            "tabcounts": asm3.lostfound.get_foundanimal_satellite_counts(dbo, a["LFID"])[0],
            "logtypes": asm3.lookups.get_log_types(dbo)
        }

class foundanimal_media(JSONEndpoint):
    url = "foundanimal_media"
    js_module = "media"
    get_permissions = asm3.users.VIEW_MEDIA

    def controller(self, o):
        dbo = o.dbo
        a = asm3.lostfound.get_foundanimal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        m = asm3.media.get_media(dbo, asm3.media.FOUNDANIMAL, o.post.integer("id"))
        asm3.al.debug("got %d media for found animal %s %s %s" % (len(m), a["AGEGROUP"], a["SPECIESNAME"], a["OWNERNAME"]), "main.foundanimal_media", dbo)
        return {
            "media": m,
            "animal": a,
            "tabcounts": asm3.lostfound.get_foundanimal_satellite_counts(dbo, a["LFID"])[0],
            "showpreferred": True,
            "canwatermark": False,
            "documentrepository": asm3.dbfs.get_document_repository(o.dbo),
            "linkid": o.post.integer("id"),
            "linktypeid": asm3.media.FOUNDANIMAL,
            "logtypes": asm3.lookups.get_log_types(dbo),
            "name": self.url,
            "flags": asm3.lookups.get_media_flags(dbo),
            "resizeimagespec": asm3.utils.iif(RESIZE_IMAGES_DURING_ATTACH, RESIZE_IMAGES_SPEC, ""),
            "templates": asm3.template.get_document_templates(dbo, "email"),
            "sigtype": ELECTRONIC_SIGNATURES
        }

class foundanimal_new(JSONEndpoint):
    url = "foundanimal_new"
    js_module = "lostfound_new"
    get_permissions = asm3.users.ADD_FOUND_ANIMAL
    post_permissions = asm3.users.ADD_FOUND_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        return {
            "agegroups": asm3.configuration.age_groups(dbo),
            "additional": asm3.additional.get_additional_fields(dbo, 0, "foundanimal"),
            "colours": asm3.lookups.get_basecolours(dbo),
            "species": asm3.lookups.get_species(dbo),
            "breeds": asm3.lookups.get_breeds_by_species(dbo),
            "sexes": asm3.lookups.get_sexes(dbo),
            "name": "foundanimal_new"
        }

    def post_all(self, o):
        return str(asm3.lostfound.insert_foundanimal_from_form(o.dbo, o.post, o.user))

class giftaid_hmrc_spreadsheet(JSONEndpoint):
    url = "giftaid_hmrc_spreadsheet"
    get_permissions = asm3.users.VIEW_DONATION

    def controller(self, o):
        return {}

    def post_all(self, o):
        fromdate = o.post["fromdate"]
        todate = o.post["todate"]
        asm3.al.debug("generating HMRC giftaid spreadsheet for %s -> %s" % (fromdate, todate), "main.giftaid_hmrc_spreadsheet", o.dbo)
        self.content_type("application/vnd.oasis.opendocument.spreadsheet")
        self.content_disposition("attachment", "giftaid.ods")
        self.cache_control(0)
        return asm3.financial.giftaid_spreadsheet(o.dbo, PATH, o.post.date("fromdate"), o.post.date("todate"))

class htmltemplates(JSONEndpoint):
    url = "htmltemplates"
    get_permissions = asm3.users.PUBLISH_OPTIONS
    post_permissions = asm3.users.PUBLISH_OPTIONS

    def controller(self, o):
        templates = asm3.template.get_html_templates(o.dbo)
        asm3.al.debug("editing %d html templates" % len(templates), "main.htmltemplates", o.dbo)
        #animalviewhead, animalviewbody, animalviewfoot = asm3.template.get_html_template_from_file(o.dbo, "animalview")
        templatedata = {}
        for a in ("animalview", "animalviewadoptable", "animalviewcarousel", "littlebox", "plain", "responsive", "rss", "slideshow", "sm.com"):
            templatedata[a] = asm3.template.get_html_template_from_file(o.dbo, a)
        return {
            "templates": {
                "animalview": {"head": templatedata["animalview"][0], "body": templatedata["animalview"][1], "foot": templatedata["animalview"][2]},
                "animalviewadoptable": {"head": templatedata["animalviewadoptable"][0], "body": templatedata["animalviewadoptable"][1], "foot": templatedata["animalviewadoptable"][2]},
                "animalviewcarousel": {"head": templatedata["animalviewcarousel"][0], "body": templatedata["animalviewcarousel"][1], "foot": templatedata["animalviewcarousel"][2]},
                "littlebox": {"head": templatedata["littlebox"][0], "body": templatedata["littlebox"][1], "foot": templatedata["littlebox"][2]},
                "plain": {"head": templatedata["plain"][0], "body": templatedata["plain"][1], "foot": templatedata["plain"][2]},
                "responsive": {"head": templatedata["responsive"][0], "body": templatedata["responsive"][1], "foot": templatedata["responsive"][2]},
                "rss": {"head": templatedata["rss"][0], "body": templatedata["rss"][1], "foot": templatedata["rss"][2]},
                "slideshow": {"head": templatedata["slideshow"][0], "body": templatedata["slideshow"][1], "foot": templatedata["slideshow"][2]},
                "sm.com": {"head": templatedata["sm.com"][0], "body": templatedata["sm.com"][1], "foot": templatedata["sm.com"][2]}
            },
            "rows": templates
        }

    def post_create(self, o):
        if o.post["templatename"] in ( "onlineform", "report" ):
            raise asm3.utils.ASMValidationError("Illegal name '%s'" % o.post["templatename"])
        asm3.template.update_html_template(o.dbo, o.user, o.post["templatename"], o.post["header"], o.post["body"], o.post["footer"])

    def post_update(self, o):
        if o.post["templatename"] in ( "onlineform", "report" ):
            raise asm3.utils.ASMValidationError("Illegal name '%s'" % o.post["templatename"])
        asm3.template.update_html_template(o.dbo, o.user, o.post["templatename"], o.post["header"], o.post["body"], o.post["footer"])

    def post_delete(self, o):
        for name in o.post["names"].split(","):
            if name != "": asm3.template.delete_html_template(o.dbo, o.user, name)

class htmltemplates_preview(ASMEndpoint):
    url = "htmltemplates_preview"

    def content(self, o):
        template = o.post["template"].replace(",", "")
        inclause = o.post["animals"]
        if inclause == "": inclause = "0"
        rows = asm3.animal.get_animals_ids(o.dbo, "DateBroughtIn", f"SELECT ID FROM animal WHERE ID IN ({inclause})", limit=10)
        asm3.additional.append_to_results(o.dbo, rows, "animal")
        self.content_type("text/html")
        self.cache_control(0)
        return asm3.publishers.html.animals_to_page(o.dbo, rows, template)

class incident(JSONEndpoint):
    url = "incident"
    get_permissions = asm3.users.VIEW_INCIDENT

    def controller(self, o):
        dbo = o.dbo
        a = asm3.animalcontrol.get_animalcontrol(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        asm3.animalcontrol.check_view_permission(dbo, o.user, o.session, a.ID)
        if o.siteid != 0 and a.SITEID != 0 and o.siteid != a.SITEID:
            raise asm3.utils.ASMPermissionError("incident not in user site")
        if (a.DISPATCHLATLONG is None or a.DISPATCHLATLONG == "") and a.DISPATCHADDRESS != "":
            a.DISPATCHLATLONG = asm3.animalcontrol.update_dispatch_geocode(dbo, a.ID, \
                a.DISPATCHLATLONG, a.DISPATCHADDRESS, a.DISPATCHTOWN, a.DISPATCHCOUNTY, a.DISPATCHPOSTCODE)
        recname = "%s %s %s" % (a.ACID, a.INCIDENTNAME, python2display(o.locale, a.INCIDENTDATETIME))
        if asm3.configuration.audit_on_view_record(dbo): asm3.audit.view_record(dbo, o.user, "animalcontrol", a["ID"], recname)
        asm3.al.debug("open incident %s" % recname, "main.incident", dbo)
        return {
            "acos": asm3.users.get_users_with_permission(dbo, asm3.users.DISPATCH_INCIDENT),
            "agegroups": asm3.configuration.age_groups(dbo),
            "additional": asm3.additional.get_additional_fields(dbo, a["ACID"], "incident"),
            "audit": self.checkb(asm3.users.VIEW_AUDIT_TRAIL) and asm3.audit.get_audit_for_link(dbo, "animalcontrol", a["ACID"]) or [],
            "incident": a,
            "jurisdictions": asm3.lookups.get_jurisdictions(dbo),
            "animallinks": asm3.animalcontrol.get_animalcontrol_animals(dbo, o.post.integer("id")),
            "incidenttypes": asm3.lookups.get_incident_types(dbo),
            "completedtypes": asm3.lookups.get_incident_completed_types(dbo),
            "logtypes": asm3.lookups.get_log_types(dbo),
            "pickuplocations": asm3.lookups.get_pickup_locations(dbo),
            "roles": asm3.users.get_roles(dbo),
            "species": asm3.lookups.get_species(dbo),
            "sexes": asm3.lookups.get_sexes(dbo),
            "sites": asm3.lookups.get_sites(dbo),
            "tabcounts": asm3.animalcontrol.get_animalcontrol_satellite_counts(dbo, a["ACID"])[0],
            "templates": asm3.template.get_document_templates(dbo, "incident"),
            "templatesemail": asm3.template.get_document_templates(dbo, "email"),
            "users": asm3.users.get_users(dbo)
        }

    def post_save(self, o):
        self.check(asm3.users.CHANGE_INCIDENT)
        asm3.animalcontrol.update_animalcontrol_from_form(o.dbo, o.post, o.user)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_INCIDENT)
        asm3.animalcontrol.delete_animalcontrol(o.dbo, o.user, o.post.integer("id"))

    def post_clone(self, o):
        self.check(asm3.users.ADD_INCIDENT)
        nid = asm3.animalcontrol.clone_animalcontrol(o.dbo, o.user, o.post.integer("id"))
        return str(nid)

    def post_latlong(self, o):
        self.check(asm3.users.CHANGE_INCIDENT)
        asm3.animalcontrol.update_dispatch_latlong(o.dbo, o.post.integer("incidentid"), o.post["latlong"])

    def post_email(self, o):
        self.check(asm3.users.EMAIL_PERSON)
        asm3.animalcontrol.send_email_from_form(o.dbo, o.user, o.post)

    def post_linkanimaladd(self, o):
        self.check(asm3.users.CHANGE_INCIDENT)
        asm3.animalcontrol.update_animalcontrol_addlink(o.dbo, o.user, o.post.integer("id"), o.post.integer("animalid"))

    def post_linkanimaldelete(self, o):
        self.check(asm3.users.CHANGE_INCIDENT)
        asm3.animalcontrol.update_animalcontrol_removelink(o.dbo, o.user, o.post.integer("id"), o.post.integer("animalid"))

class incident_citations(JSONEndpoint):
    url = "incident_citations"
    js_module = "citations"
    get_permissions = asm3.users.VIEW_CITATION

    def controller(self, o):
        dbo = o.dbo
        a = asm3.animalcontrol.get_animalcontrol(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        citations = asm3.financial.get_incident_citations(dbo, o.post.integer("id"))
        asm3.al.debug("got %d citations" % len(citations), "main.incident_citations", dbo)
        return {
            "name": "incident_citations",
            "rows": citations,
            "incident": a,
            "tabcounts": asm3.animalcontrol.get_animalcontrol_satellite_counts(dbo, a["ACID"])[0],
            "citationtypes": asm3.lookups.get_citation_types(dbo),
            "nextid": dbo.get_id_max("ownercitation")
        }

class incident_find(JSONEndpoint):
    url = "incident_find"
    get_permissions = asm3.users.VIEW_INCIDENT

    def controller(self, o):
        dbo = o.dbo
        return {
            "additionalfields": asm3.additional.get_additional_fields(dbo, 0, "incident"),
            "agegroups": asm3.configuration.age_groups(dbo),
            "incidenttypes": asm3.lookups.get_incident_types(dbo),
            "completedtypes": asm3.lookups.get_incident_completed_types(dbo),
            "citationtypes": asm3.lookups.get_citation_types(dbo),
            "jurisdictions": asm3.lookups.get_jurisdictions(dbo),
            "pickuplocations": asm3.lookups.get_pickup_locations(dbo),
            "species": asm3.lookups.get_species(dbo),
            "sexes": asm3.lookups.get_sexes(dbo),
            "users": asm3.users.get_users(dbo)
        }

class incident_find_results(JSONEndpoint):
    url = "incident_find_results"
    get_permissions = asm3.users.VIEW_INCIDENT

    def controller(self, o):
        results = asm3.animalcontrol.get_animalcontrol_find_advanced(o.dbo, o.post.data, o.user, asm3.configuration.record_search_limit(o.dbo))
        add = None
        if len(results) > 0: 
            add = asm3.additional.get_additional_fields_ids(o.dbo, results, "incident")
        asm3.al.debug("found %d results for %s" % (len(results), self.query()), "main.incident_find_results", o.dbo)
        return {
            "additional": add,
            "rows": results
        }

class incident_diary(JSONEndpoint):
    url = "incident_diary"
    js_module = "diary"
    get_permissions = asm3.users.VIEW_DIARY

    def controller(self, o):
        dbo = o.dbo
        a = asm3.animalcontrol.get_animalcontrol(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        diaries = asm3.diary.get_diaries(dbo, asm3.diary.ANIMALCONTROL, o.post.integer("id"))
        asm3.al.debug("got %d diaries" % len(diaries), "main.incident_diary", dbo)
        return {
            "rows": diaries,
            "incident": a,
            "tabcounts": asm3.animalcontrol.get_animalcontrol_satellite_counts(dbo, a["ACID"])[0],
            "name": "incident_diary",
            "linkid": a["ACID"],
            "linktypeid": asm3.diary.ANIMALCONTROL,
            "forlist": asm3.users.get_diary_forlist(dbo)
        }

class incident_log(JSONEndpoint):
    url = "incident_log"
    js_module = "log"
    get_permissions = asm3.users.VIEW_LOG

    def controller(self, o):
        dbo = o.dbo
        a = asm3.animalcontrol.get_animalcontrol(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        logfilter = o.post.integer("filter")
        if logfilter == 0: logfilter = asm3.configuration.default_log_filter(dbo)
        logs = asm3.log.get_logs(dbo, asm3.log.ANIMALCONTROL, o.post.integer("id"), logfilter)
        asm3.al.debug("got %d logs" % len(logs), "main.incident_log", dbo)
        return {
            "name": "incident_log",
            "linkid": o.post.integer("id"),
            "linktypeid": asm3.log.ANIMALCONTROL,
            "filter": logfilter,
            "rows": logs,
            "incident": a,
            "tabcounts": asm3.animalcontrol.get_animalcontrol_satellite_counts(dbo, a["ACID"])[0],
            "logtypes": asm3.lookups.get_log_types(dbo)
        }

class incident_map(JSONEndpoint):
    url = "incident_map"
    get_permissions = asm3.users.VIEW_INCIDENT

    def controller(self, o):
        dbo = o.dbo
        rows = asm3.animalcontrol.get_animalcontrol_find_advanced(dbo, { "filter": "incomplete" }, o.user)
        asm3.al.debug("incident map, %d active" % (len(rows)), "main.incident_map", dbo)
        return {
            "rows": rows
        }

class incident_media(JSONEndpoint):
    url = "incident_media"
    js_module = "media"
    get_permissions = asm3.users.VIEW_MEDIA

    def controller(self, o):
        dbo = o.dbo
        a = asm3.animalcontrol.get_animalcontrol(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        m = asm3.media.get_media(dbo, asm3.media.ANIMALCONTROL, o.post.integer("id"))
        asm3.al.debug("got %d media" % len(m), "main.incident_media", dbo)
        return {
            "media": m,
            "incident": a,
            "tabcounts": asm3.animalcontrol.get_animalcontrol_satellite_counts(dbo, a["ACID"])[0],
            "showpreferred": True,
            "canwatermark": False,
            "documentrepository": asm3.dbfs.get_document_repository(o.dbo),
            "linkid": o.post.integer("id"),
            "linktypeid": asm3.media.ANIMALCONTROL,
            "logtypes": asm3.lookups.get_log_types(dbo),
            "name": self.url,
            "flags": asm3.lookups.get_media_flags(dbo),
            "resizeimagespec": asm3.utils.iif(RESIZE_IMAGES_DURING_ATTACH, RESIZE_IMAGES_SPEC, ""),
            "templates": asm3.template.get_document_templates(dbo, "email"),
            "sigtype": ELECTRONIC_SIGNATURES
        }

class incident_new(JSONEndpoint):
    url = "incident_new"
    get_permissions = asm3.users.ADD_INCIDENT
    post_permissions = asm3.users.ADD_INCIDENT

    def controller(self, o):
        dbo = o.dbo
        asm3.al.debug("add incident", "main.incident_new", dbo)
        return {
            "acos": asm3.users.get_users_with_permission(dbo, asm3.users.DISPATCH_INCIDENT),
            "incidenttypes": asm3.lookups.get_incident_types(dbo),
            "jurisdictions": asm3.lookups.get_jurisdictions(dbo),
            "additional": asm3.additional.get_additional_fields(dbo, 0, "incident"),
            "pickuplocations": asm3.lookups.get_pickup_locations(dbo),
            "towns": asm3.person.get_towns(dbo),
            "counties": asm3.person.get_counties(dbo),
            "towncounties": asm3.person.get_town_to_county(dbo),
            "roles": asm3.users.get_roles(dbo),
            "sites": asm3.lookups.get_sites(dbo),
            "users": asm3.users.get_users(dbo)
        }

    def post_all(self, o):
        incidentid = asm3.animalcontrol.insert_animalcontrol_from_form(o.dbo, o.post, o.user)
        return str(incidentid)

class licence(JSONEndpoint):
    url = "licence"
    get_permissions = asm3.users.VIEW_LICENCE

    def controller(self, o):
        dbo = o.dbo
        offset = o.post["offset"]
        if offset == "": offset = "i31"
        licences = asm3.financial.get_licences(dbo, offset)
        asm3.al.debug("got %d licences" % len(licences), "main.licence", dbo)
        return {
            "name": "licence",
            "rows": licences,
            "baselink": f"{SERVICE_URL}?account={dbo.name()}&method=checkout_licence&token=",
            "templates": asm3.template.get_document_templates(dbo, "licence"),
            "licencetypes": asm3.lookups.get_licence_types(dbo)
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_LICENCE)
        return asm3.financial.insert_licence_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_LICENCE)
        asm3.financial.update_licence_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_LICENCE)
        for lid in o.post.integer_list("ids"):
            asm3.financial.delete_licence(o.dbo, o.user, lid)

    def post_email(self, o):
        self.check(asm3.users.EMAIL_PERSON)
        asm3.person.send_email_from_form(o.dbo, o.user, o.post)

class licence_renewal(JSONEndpoint):
    url = "licence_renewal"
    get_permissions = asm3.users.ADD_LICENCE
    post_permissions = asm3.users.ADD_LICENCE

    def controller(self, o):
        dbo = o.dbo
        asm3.al.debug("renewing licence", "main.licence_renewal", dbo)
        return {
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "licencetypes": asm3.lookups.get_licence_types(dbo),
            "paymentmethods": asm3.lookups.get_payment_methods(dbo),
            "accounts": asm3.financial.get_accounts(dbo, onlybank=True)
        }

    def post_all(self, o):
        asm3.financial.insert_donations_from_form(o.dbo, o.user, o.post, o.post["issuedate"], False, o.post["person"], o.post["animal"]) 
        return asm3.financial.insert_licence_from_form(o.dbo, o.user, o.post)

class litters(JSONEndpoint):
    url = "litters"
    get_permissions = asm3.users.VIEW_LITTER

    def controller(self, o):
        dbo = o.dbo
        offset = o.post["offset"]
        if offset == "": offset = "active"
        if offset == "active":
            litters = asm3.animal.get_active_litters(dbo)
        else:
            litters = asm3.animal.get_litters(dbo, offset)
        littermates = asm3.animal.get_litter_animals(dbo, litters)
        mothers = asm3.animal.get_litter_mothers(dbo, litters)
        asm3.al.debug("got %d litters" % len(litters), "main.litters", dbo)
        return {
            "rows": litters,
            "littermates": littermates,
            "mothers": mothers,
            "species": asm3.lookups.get_species(dbo)
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_LITTER)
        return asm3.animal.insert_litter_from_form(o.dbo, o.user, o.post)

    def post_nextlitterid(self, o):
        nextid = o.dbo.query_int("SELECT MAX(ID) FROM animallitter") + 1
        return asm3.utils.padleft(nextid, 6)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_LITTER)
        asm3.animal.update_litter_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_LITTER) 
        for lid in o.post.integer_list("ids"):
            asm3.animal.delete_litter(o.dbo, o.user, lid)

class log(ASMEndpoint):
    url = "log"

    def post_create(self, o):
        self.check(asm3.users.ADD_LOG)
        return asm3.log.insert_log_from_form(o.dbo, o.user, o.post.integer("linktypeid"), o.post.integer("linkid"), o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_LOG)
        asm3.log.update_log_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_LOG)
        for lid in o.post.integer_list("ids"):
            asm3.log.delete_log(o.dbo, o.user, lid)

class log_new(JSONEndpoint):
    url = "log_new"
    get_permissions = asm3.users.ADD_LOG
    post_permissions = asm3.users.ADD_LOG

    def controller(self, o):
        dbo = o.dbo
        mode = o.post["mode"]
        if mode == "": mode = "animal"
        return {
            "logtypes": asm3.lookups.get_log_types(dbo),
            "mode": mode
        }

    def post_animal(self, o):
        asm3.log.insert_log_from_form(o.dbo, o.user, asm3.log.ANIMAL, o.post.integer("animal"), o.post)

    def post_person(self, o):
        asm3.log.insert_log_from_form(o.dbo, o.user, asm3.log.PERSON, o.post.integer("person"), o.post)

class lookups(JSONEndpoint):
    url = "lookups"
    get_permissions = asm3.users.MODIFY_LOOKUPS
    post_permissions = asm3.users.MODIFY_LOOKUPS

    def controller(self, o):
        dbo = o.dbo
        l = o.locale
        tablename = o.post["tablename"]
        if tablename == "": tablename = "animaltype"
        table = list(asm3.lookups.LOOKUP_TABLES[tablename])
        table[0] = translate(table[0], l)
        table[2] = translate(table[2], l)
        modifiers = table[4].split(" ")
        rows = asm3.lookups.get_lookup(dbo, tablename, table[1])
        asm3.al.debug("edit lookups for %s, got %d rows" % (tablename, len(rows)), "main.lookups", dbo)
        return {
            "rows": rows,
            "adoptapetcolours": asm3.lookups.ADOPTAPET_COLOURS,
            "petfinderspecies": asm3.lookups.PETFINDER_SPECIES,
            "petfinderbreeds": asm3.lookups.PETFINDER_BREEDS,
            "sites": asm3.lookups.get_sites(dbo),
            "tablename": tablename,
            "tablelabel": table[0],
            "namefield": table[1].upper(),
            "namelabel": table[2],
            "descfield": table[3].upper(),
            "hasspecies": "species" in modifiers,
            "haspfspecies": "pubspec" in modifiers,
            "haspfbreed": "pubbreed" in modifiers,
            "hasapcolour": "pubcol" in modifiers,
            "hasrescheduledays": "sched" in modifiers,
            "hasaccountid": "acc" in modifiers,
            "hasdefaultcost": "cost" in modifiers,
            "hasunits": "units" in modifiers,
            "hassite": "site" in modifiers,
            "hasvat": "vat" in modifiers,
            "hastaxrate": tablename == "lktaxrate",
            "canadd": "add" in modifiers,
            "candelete": "del" in modifiers,
            "canretire": "ret" in modifiers,
            "accounts": asm3.financial.get_accounts(dbo, onlyactive=True),
            "species": asm3.lookups.get_species(dbo),
            "tables": asm3.html.json_lookup_tables(l)
        }

    def post_create(self, o):
        post = o.post
        return asm3.lookups.insert_lookup(o.dbo, o.user, post["lookup"], post["lookupname"], post["lookupdesc"], \
            post.integer("species"), post["pfbreed"], post["pfspecies"], post["apcolour"], post["units"], post.integer("site"), post.integer("rescheduledays"), post.integer("account"), post.integer("defaultcost"), post.integer("vat"), post.integer("retired"), post.floating("taxrate"))

    def post_update(self, o):
        post = o.post
        asm3.lookups.update_lookup(o.dbo, o.user, post.integer("id"), post["lookup"], post["lookupname"], post["lookupdesc"], \
            post.integer("species"), post["pfbreed"], post["pfspecies"], post["apcolour"], post["units"], post.integer("site"), post.integer("rescheduledays"), post.integer("account"), post.integer("defaultcost"), post.integer("vat"), post.integer("retired"), post.floating("taxrate"))

    def post_delete(self, o):
        for lid in o.post.integer_list("ids"):
            asm3.lookups.delete_lookup(o.dbo, o.user, o.post["lookup"], lid)

    def post_active(self, o):
        for lid in o.post.integer_list("ids"):
            asm3.lookups.update_lookup_retired(o.dbo, o.user, o.post["lookup"], lid, 0)

    def post_inactive(self, o):
        for lid in o.post.integer_list("ids"):
            asm3.lookups.update_lookup_retired(o.dbo, o.user, o.post["lookup"], lid, 1)

class lostanimal(JSONEndpoint):
    url = "lostanimal"
    js_module = "lostfound"
    get_permissions = asm3.users.VIEW_LOST_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        a = asm3.lostfound.get_lostanimal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        recname = "%s %s %s" % (a.AGEGROUP, a.SPECIESNAME, a.OWNERNAME)
        if asm3.configuration.audit_on_view_record(dbo): asm3.audit.view_record(dbo, o.user, "animallost", a["ID"], recname)
        asm3.al.debug("open lost animal %s" % recname, "main.foundanimal", dbo)
        return {
            "animal": a,
            "name": "lostanimal",
            "additional": asm3.additional.get_additional_fields(dbo, a["ID"], "lostanimal"),
            "agegroups": asm3.configuration.age_groups(dbo),
            "audit": self.checkb(asm3.users.VIEW_AUDIT_TRAIL) and asm3.audit.get_audit_for_link(dbo, "animallost", a["ID"]) or [],
            "breeds": asm3.lookups.get_breeds_by_species(dbo),
            "colours": asm3.lookups.get_basecolours(dbo),
            "logtypes": asm3.lookups.get_log_types(dbo),
            "sexes": asm3.lookups.get_sexes(dbo),
            "species": asm3.lookups.get_species(dbo),
            "templates": asm3.template.get_document_templates(dbo, "lostanimal"),
            "templatesemail": asm3.template.get_document_templates(dbo, "email"),
            "tabcounts": asm3.lostfound.get_lostanimal_satellite_counts(dbo, a["LFID"])[0]
        }

    def post_save(self, o):
        self.check(asm3.users.CHANGE_LOST_ANIMAL)
        asm3.lostfound.update_lostanimal_from_form(o.dbo, o.post, o.user)

    def post_email(self, o):
        self.check(asm3.users.EMAIL_PERSON)
        asm3.lostfound.send_email_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_LOST_ANIMAL)
        asm3.lostfound.delete_lostanimal(o.dbo, o.user, o.post.integer("id"))

class lostanimal_diary(JSONEndpoint):
    url = "lostanimal_diary"
    js_module = "diary"
    get_permissions = asm3.users.VIEW_DIARY

    def controller(self, o):
        dbo = o.dbo
        a = asm3.lostfound.get_lostanimal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        diaries = asm3.diary.get_diaries(dbo, asm3.diary.LOSTANIMAL, o.post.integer("id"))
        asm3.al.debug("got %d diaries for lost animal %s %s %s" % (len(diaries), a["AGEGROUP"], a["SPECIESNAME"], a["OWNERNAME"]), "main.foundanimal_diary", dbo)
        return {
            "rows": diaries,
            "animal": a,
            "tabcounts": asm3.lostfound.get_lostanimal_satellite_counts(dbo, a["LFID"])[0],
            "name": "lostanimal_diary",
            "linkid": a["LFID"],
            "linktypeid": asm3.diary.LOSTANIMAL,
            "forlist": asm3.users.get_diary_forlist(dbo)
        }

class lostanimal_find(JSONEndpoint):
    url = "lostanimal_find"
    js_module = "lostfound_find"
    get_permissions = asm3.users.VIEW_LOST_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        return {
            "additionalfields": asm3.additional.get_additional_fields(dbo, 0, "lostanimal"),
            "agegroups": asm3.configuration.age_groups(dbo),
            "name": "lostanimal_find",
            "colours": asm3.lookups.get_basecolours(dbo),
            "species": asm3.lookups.get_species(dbo),
            "breeds": asm3.lookups.get_breeds_by_species(dbo),
            "sexes": asm3.lookups.get_sexes(dbo),
            "mode": "lost"
        }

class lostanimal_find_results(JSONEndpoint):
    url = "lostanimal_find_results"
    js_module = "lostfound_find_results"
    get_permissions = asm3.users.VIEW_LOST_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        results = asm3.lostfound.get_lostanimal_find_advanced(dbo, o.post.data, asm3.configuration.record_search_limit(dbo))
        add = None
        if len(results) > 0: 
            add = asm3.additional.get_additional_fields_ids(dbo, results, "lostanimal")
        asm3.al.debug("found %d results for %s" % (len(results), self.query()), "main.lostanimal_find_results", dbo)
        return {
            "additional": add,
            "rows": results,
            "name": "lostanimal_find_results"
        }

class lostanimal_log(JSONEndpoint):
    url = "lostanimal_log"
    js_module = "log"
    get_permissions = asm3.users.VIEW_LOG

    def controller(self, o):
        dbo = o.dbo
        logfilter = o.post.integer("filter")
        if logfilter == 0: logfilter = asm3.configuration.default_log_filter(dbo)
        a = asm3.lostfound.get_lostanimal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        logs = asm3.log.get_logs(dbo, asm3.log.LOSTANIMAL, o.post.integer("id"), logfilter)
        return {
            "name": "lostanimal_log",
            "linkid": o.post.integer("id"),
            "linktypeid": asm3.log.LOSTANIMAL,
            "filter": logfilter,
            "rows": logs,
            "animal": a,
            "tabcounts": asm3.lostfound.get_lostanimal_satellite_counts(dbo, a["LFID"])[0],
            "logtypes": asm3.lookups.get_log_types(dbo)
        }

class lostanimal_media(JSONEndpoint):
    url = "lostanimal_media"
    js_module = "media"
    get_permissions = asm3.users.VIEW_MEDIA

    def controller(self, o):
        dbo = o.dbo
        a = asm3.lostfound.get_lostanimal(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        m = asm3.media.get_media(dbo, asm3.media.LOSTANIMAL, o.post.integer("id"))
        asm3.al.debug("got %d media for lost animal %s %s %s" % (len(m), a["AGEGROUP"], a["SPECIESNAME"], a["OWNERNAME"]), "main.foundanimal_media", dbo)
        return {
            "media": m,
            "animal": a,
            "tabcounts": asm3.lostfound.get_lostanimal_satellite_counts(dbo, a["LFID"])[0],
            "showpreferred": True,
            "canwatermark": False,
            "documentrepository": asm3.dbfs.get_document_repository(o.dbo),
            "linkid": o.post.integer("id"),
            "linktypeid": asm3.media.LOSTANIMAL,
            "logtypes": asm3.lookups.get_log_types(dbo),
            "name": self.url, 
            "flags": asm3.lookups.get_media_flags(dbo),
            "resizeimagespec": asm3.utils.iif(RESIZE_IMAGES_DURING_ATTACH, RESIZE_IMAGES_SPEC, ""),
            "templates": asm3.template.get_document_templates(dbo, "email"),
            "sigtype": ELECTRONIC_SIGNATURES
        }

class lostanimal_new(JSONEndpoint):
    url = "lostanimal_new"
    js_module = "lostfound_new"
    get_permissions = asm3.users.ADD_LOST_ANIMAL
    post_permissions = asm3.users.ADD_LOST_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        return {
            "agegroups": asm3.configuration.age_groups(dbo),
            "additional": asm3.additional.get_additional_fields(dbo, 0, "lostanimal"),
            "colours": asm3.lookups.get_basecolours(dbo),
            "species": asm3.lookups.get_species(dbo),
            "breeds": asm3.lookups.get_breeds_by_species(dbo),
            "sexes": asm3.lookups.get_sexes(dbo),
            "name": "lostanimal_new"
        }

    def post_all(self, o):
        return str(asm3.lostfound.insert_lostanimal_from_form(o.dbo, o.post, o.user))

class lostfound_match(ASMEndpoint):
    url = "lostfound_match"
    get_permissions = ( asm3.users.VIEW_LOST_ANIMAL, asm3.users.VIEW_FOUND_ANIMAL, asm3.users.VIEW_PERSON )

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
            asm3.al.debug("no parameters given, using cached report", "main.lostfound_match", dbo)
            return asm3.cachedisk.get("lostfound_report", dbo.name())
        else:
            asm3.al.debug("match lost=%d, found=%d, animal=%d" % (lostanimalid, foundanimalid, animalid), "main.lostfound_match", dbo)
            return asm3.lostfound.match_report(dbo, o.user, lostanimalid, foundanimalid, animalid)

class mailmerge(JSONEndpoint):
    url = "mailmerge"
    get_permissions = asm3.users.MAIL_MERGE
    post_permissions = asm3.users.MAIL_MERGE

    def recipients(self, rows):
        """ Returns a list of all recipients for rows """
        emails = []
        if len(rows) > 0 and "EMAILADDRESS" in rows[0]:
            emails += [r.EMAILADDRESS for r in rows if r.EMAILADDRESS]
        if len(rows) > 0 and "EMAILADDRESS2" in rows[0]:
            emails += [r.EMAILADDRESS2 for r in rows if r.EMAILADDRESS2]
        return emails

    def controller(self, o):
        l = o.locale
        dbo = o.dbo
        post = o.post
        crid = post.integer("id")
        crit = asm3.reports.get_criteria(dbo, crid)
        title = asm3.reports.get_title(dbo, crid)
        # If this mail merge takes criteria and none were supplied, go to the criteria screen to get them
        if len(crit) != 0 and post["hascriteria"] == "": self.redirect("report_criteria?id=%s&target=mailmerge" % crid)
        asm3.al.debug("entering mail merge selection mode for %d" % post.integer("id"), "main.mailmerge", dbo)
        p = asm3.reports.get_criteria_params(dbo, crid, post)
        rows, cols = asm3.reports.execute_query(dbo, crid, o.user, p)
        if rows is None: rows = []
        numemails = len(self.recipients(rows))
        asm3.al.debug("got merge rows (%d items, %d email addresses)" % (len(rows), numemails), "main.mailmerge", dbo)
        # construct a list of field tokens for the email helper
        fields = []
        if len(rows) > 0:
            for fname in sorted(rows[0].keys()):
                fields.append(fname)
        # send the selection form
        title = _("Mail Merge - {0}", l).format(title)
        return {
            "title": title,
            "fields": fields,
            "issmcomsmtp": asm3.utils.is_smcom_smtp(dbo),
            "smcommaxemails": asm3.smcom.MAX_EMAILS,
            "mergeparams": asm3.utils.json(p),
            "mergereport": crid,
            "mergetitle": title.replace(" ", "_").replace("\"", "").replace("'", "").lower(),
            "numemails": numemails,
            "numrows": len(rows),
            "hasemail": "EMAILADDRESS" in fields,
            "hasaddress": "OWNERNAME" in fields and "OWNERADDRESS" in fields and "OWNERTOWN" in fields and "OWNERCOUNTY" in fields and "OWNERPOSTCODE" in fields,
            "templates": asm3.template.get_document_templates(dbo, "mailmerge")
        }
   
    def post_email(self, o):
        dbo = o.dbo
        post = o.post
        mergeparams = ""
        if post["mergeparams"] != "": mergeparams = asm3.utils.json_parse(post["mergeparams"])
        rows, cols = asm3.reports.execute_query(dbo, post.integer("mergereport"), o.user, mergeparams)
        if asm3.utils.is_smcom_smtp(dbo) and len(rows) > asm3.smcom.MAX_EMAILS:
            raise asm3.utils.ASMError("{0} exceeds limit of {1} emails allowed through sheltermanager.com email server".format(len(rows), asm3.smcom.MAX_EMAILS))
        if len(rows) > asm3.configuration.mail_merge_max_emails(dbo):
            raise asm3.utils.ASMError("{0} exceeds configured limit of {1} emails via mail merge".format(len(rows), asm3.configuration.mail_merge_max_emails(dbo)))
        fromadd = post["from"]
        subject = post["subject"]
        body = post["body"]
        if asm3.configuration.audit_on_send_email(dbo):
            emails = self.recipients(rows)
            asm3.audit.email(dbo, o.user, fromadd, ",".join(emails), "", "", subject, body)
        asm3.utils.send_bulk_email(dbo, fromadd, subject, body, rows, "html", post.boolean("unsubscribe"))

    def post_document(self, o):
        dbo = o.dbo
        post = o.post
        mergeparams = ""
        if post["mergeparams"] != "": mergeparams = asm3.utils.json_parse(post["mergeparams"])
        rows, cols = asm3.reports.execute_query(dbo, post.integer("mergereport"), o.user, mergeparams)
        templateid = post.integer("templateid")
        templatecontent = asm3.template.get_document_template_content(dbo, templateid)
        templatename = asm3.template.get_document_template_name(dbo, templateid)
        if not templatename.endswith(".html"):
            raise asm3.utils.ASMValidationError("Only html templates are allowed")
        # Generate a document from the template for each row
        org_tags = asm3.wordprocessor.org_tags(dbo, o.user)
        c = []
        for d in rows:
            c.append( asm3.wordprocessor.substitute_tags(asm3.utils.bytes2str(templatecontent), asm3.wordprocessor.append_tags(d, org_tags)) )
        content = '<div class="mce-pagebreak" style="page-break-before: always; clear: both; border: 0">&nbsp;</div>'.join(c)
        self.content_type("text/html")
        self.cache_control(0)
        return asm3.html.tinymce_header(templatename, "document_edit.js", jswindowprint=True, pdfenabled=False, readonly=True) + \
            asm3.html.tinymce_main(o.locale, "", recid=0, linktype="", \
                dtid="", content=asm3.utils.escape_tinymce(content))

    def post_labels(self, o):
        dbo = o.dbo
        post = o.post
        mergeparams = ""
        if post["mergeparams"] != "": mergeparams = asm3.utils.json_parse(post["mergeparams"])
        rows, cols = asm3.reports.execute_query(dbo, post.integer("mergereport"), o.user, mergeparams)
        disp = asm3.configuration.pdf_inline(dbo) and "inline" or "attachment"
        self.content_disposition(disp, post["mergetitle"], "pdf", "labels.pdf" )
        self.content_type("application/pdf")
        return asm3.utils.generate_label_pdf(dbo, o.locale, rows, post["papersize"], post["units"], post["fontpt"], 
            post.floating("hpitch"), post.floating("vpitch"), 
            post.floating("width"), post.floating("height"), 
            post.floating("lmargin"), post.floating("tmargin"),
            post.integer("cols"), post.integer("rows"))

    def post_csv(self, o):
        dbo = o.dbo
        post = o.post
        mergeparams = ""
        if post["mergeparams"] != "": mergeparams = asm3.utils.json_parse(post["mergeparams"])
        rows, cols = asm3.reports.execute_query(dbo, post.integer("mergereport"), o.user, mergeparams)
        self.content_disposition("attachment", post["mergetitle"], "csv", "download.csv")
        self.content_type("text/csv")
        includeheader = 1 == post.boolean("includeheader")
        return asm3.utils.csv_generator(o.locale, rows, cols, includeheader)

    def post_preview(self, o):
        dbo = o.dbo
        post = o.post
        mergeparams = ""
        if post["mergeparams"] != "": mergeparams = asm3.utils.json_parse(post["mergeparams"])
        rows, cols = asm3.reports.execute_query(dbo, post.integer("mergereport"), o.user, mergeparams)
        asm3.al.debug("returning preview rows for %d [%s]" % (post.integer("mergereport"), post["mergetitle"]), "main.mailmerge", dbo)
        return asm3.utils.json(rows)

    def post_recipients(self, o):
        dbo = o.dbo
        post = o.post
        mergeparams = ""
        if post["mergeparams"] != "": mergeparams = asm3.utils.json_parse(post["mergeparams"])
        rows, cols = asm3.reports.execute_query(dbo, post.integer("mergereport"), o.user, mergeparams)
        return ", ".join(self.recipients(rows))

class maint_be_user(ASMEndpoint):
    url = "maint_be_user"

    def content(self, o):
        if not session.nologconnection: raise asm3.utils.ASMError("Forbidden")
        asm3.users.update_session(o.dbo, o.session, o.post["user"])
        self.redirect("main")

class maint_db_stats(ASMEndpoint):
    url = "maint_db_stats"

    def content(self, o):
        self.content_type("text/plain")
        self.cache_control(0)
        s = o.dbo.stats()
        def rnd(x):
            if x is None: return "0"
            return round(x, 1)
        return f"first record added on {s.firstrecord}\n\n" \
            f"{s.shelteranimals:,} shelter animals\n" \
            f"{s.totalanimals:,} total animals (max id {s.maxidanimal})\n" \
            f"{s.totalvacc:,} vaccinations (max id {s.maxidanimalvaccination})\n" \
            f"{s.totaltreatments:,} treatments (max id {s.maxidanimalmedicaltreatment})\n" \
            f"{s.totalpeople:,} people (max id {s.maxidowner})\n" \
            f"{s.totalmovements:,} movements (max id {s.maxidadoption})\n" \
            f"{s.totalincidents:,} incidents (max id {s.maxidanimalcontrol})\n\n" \
            f"{s.totalmedia:,} media ({rnd(s.mediasize)} MB)\n" \
            f"    {s.totaljpg} image/jpeg ({rnd(s.jpgsize)} MB)\n" \
            f"    {s.totalpdf} application/pdf ({rnd(s.pdfsize)} MB)\n" \
            f"    {s.totalhtml} text/html ({rnd(s.htmlsize)} MB)\n" \
            f"    {s.totalother} other ({rnd(s.othersize)} MB)\n"

class maint_deps(ASMEndpoint):
    url = "maint_deps"

    def content(self, o):
        self.content_type("text/plain")
        self.cache_control(0)
        return "web.py %s" % web.__version__

class maint_error(ASMEndpoint):
    url = "maint_error"

    def content(self, o):
        return 1 / 0 # Test error handling

class maint_latency(JSONEndpoint):
    url = "maint_latency"

    def controller(self, o):
        return {}

    def post_all(self, o):
        self.content_type("text/plain")
        self.cache_control(0)
        return "pong"

class maint_petfinder(ASMEndpoint):
    url = "maint_petfinder"

    def content(self, o):
        """ Clears all PetFinder listings """
        self.content_type("text/plain")
        self.cache_control(0)
        try:
            pc = asm3.publishers.base.PublishCriteria(asm3.configuration.publisher_presets(o.dbo))
            p = asm3.publishers.petfinder.PetFinderPublisher(o.dbo, pc)
            return p.clearListings()
        except Exception as err:
            return str(err)

class maint_ping(ASMEndpoint):
    url = "maint_ping"
    check_logged_in = False

    def content(self, o):
        self.content_type("text/plain")
        self.cache_control(0)
        self.header("Access-Control-Allow-Origin", "*") # CORS
        keywords = ["pong"]
        frules = asm3.smcom.iptables_rules()
        if frules.find("REJECT") != -1 or frules.find("DROP") != -1: keywords.append("firewall")
        return " ".join(keywords)

class maint_sac_metrics(ASMEndpoint):
    url = "maint_sac_metrics"

    def content(self, o):
        """ Forces an upload of a particular month and year to SAC """
        self.content_type("text/plain")
        self.cache_control(0)
        year = o.post.integer("year")
        month = o.post.integer("month")
        externalid = o.post["externalid"]
        species = asm3.publishers.sacmetrics.SAC_SPECIES.keys()
        if year == 0 or month < 0 or month > 12:
            raise asm3.utils.ASMValidationError("Endpoint requires parameters for year (int) and optionally month (int). If no month is set, all months are sent.")
        try:
            pc = asm3.publishers.base.PublishCriteria(asm3.configuration.publisher_presets(o.dbo))
            p = asm3.publishers.sacmetrics.SACMetricsPublisher(o.dbo, pc)
            if month == 0:
                # Do all months of year if no month was given
                for m in range(1,13):
                    for s in species:
                        data = p.processStats(m, year, s, externalid)
                        p.putData(data)
            else:
                for s in species:
                    data = p.processStats(month, year, s, externalid)
                p.putData(data)
            return "\n".join(p.logBuffer)
        except Exception as err:
            return str(err)
        
class maint_sql_lookups(ASMEndpoint):
    url = "maint_sql_lookups"

    def content(self, o):
        """ Outputs the SQL for the lookup data in this database so it can be copied/saved and run in another database """
        self.content_disposition("attachment", "lookups.sql")
        return asm3.dbupdate.dump_lookups(o.dbo)

class maint_switch_species(ASMEndpoint):
    url = "maint_switch_species"

    def content(self, o):
        """ Swaps species id source to target """
        find = o.post.integer("find")
        replace = o.post.integer("replace")
        if find == 0 or replace == 0:
            raise asm3.utils.ASMValidationError("find and replace parameters must be supplied and valid")
        affected = asm3.lookups.update_species_id(o.dbo, find, replace)
        self.content_type("text/plain")
        self.cache_control(0)
        return f"{affected} rows affected."

class maint_time(ASMEndpoint):
    url = "maint_time"

    def content(self, o):
        self.content_type("text/plain")
        self.cache_control(0)
        return "Time now is %s. TZ=%s DST=%s (%s)" % \
            ( o.dbo.now(), o.dbo.timezone, o.dbo.timezone_dst == 1 and "ON" or "OFF", get_dst(o.locale) )

class maint_undelete(JSONEndpoint):
    url = "maint_undelete"
    get_permissions = asm3.users.USE_SQL_INTERFACE

    def controller(self, o):
        offset = o.post.integer("offset")
        d = asm3.audit.get_deletions(o.dbo, offset)
        asm3.al.debug("got %d deleted top level records" % len(d), "main.undelete", o.dbo)
        return { "rows": d }

    def post_view(self, o):
        self.check(asm3.users.USE_SQL_INTERFACE)
        tablename, iid = o.post["key"].split(":")
        return asm3.audit.get_restoresql(o.dbo, tablename, iid) 

    def post_undelete(self, o):
        self.check(asm3.users.USE_SQL_INTERFACE)
        for i in o.post["ids"].split(","):
            if i == "": continue
            tablename, iid = i.split(":")
            asm3.audit.undelete(o.dbo, asm3.utils.cint(iid), tablename)

class maint_update_reports(ASMEndpoint):
    url = "maint_update_reports"

    def content(self, o):
        self.content_type("text/plain")
        self.cache_control(0)
        return "%s reports updated" % asm3.reports.update_smcom_reports(o.dbo, o.user)

class medical(JSONEndpoint):
    url = "medical"
    get_permissions = asm3.users.VIEW_MEDICAL

    def controller(self, o):
        dbo = o.dbo
        offset = o.post["offset"]
        if offset == "": offset = "m365"
        med = asm3.medical.get_treatments_outstanding(dbo, offset, o.lf)
        profiles = asm3.medical.get_profiles(dbo)
        asm3.al.debug("got %d medical treatments" % len(med), "main.medical", dbo)
        return {
            "profiles": profiles,
            "rows": med,
            "overlimit": 0,
            "newmed": o.post.integer("newmed") == 1,
            "name": "medical",
            "stockitems": asm3.stock.get_stock_items(dbo),
            "stockusagetypes": asm3.lookups.get_stock_usage_types(dbo),
            "templates": asm3.template.get_document_templates(dbo, "medical"),
            "users": asm3.users.get_users(dbo)
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_MEDICAL)
        asm3.medical.insert_regimen_from_form(o.dbo, o.user, o.post)

    def post_createbulk(self, o):
        self.check(asm3.users.ADD_MEDICAL)
        for animalid in o.post.integer_list("animals"):
            o.post.data["animal"] = str(animalid)
            asm3.medical.insert_regimen_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_MEDICAL)
        asm3.medical.update_regimen_from_form(o.dbo, o.user, o.post)

    def post_deleteregimen(self, o):
        self.check(asm3.users.DELETE_MEDICAL)
        for mid in o.post.integer_list("ids"):
            asm3.medical.delete_regimen(o.dbo, o.user, mid)

    def post_deletetreatment(self, o):
        self.check(asm3.users.DELETE_MEDICAL)
        for mid in o.post.integer_list("ids"):
            asm3.medical.delete_treatment(o.dbo, o.user, mid)

    def post_getprofile(self, o):
        return asm3.utils.json([asm3.medical.get_profile(o.dbo, o.post.integer("profileid"))])

    def post_given(self, o):
        self.check(asm3.users.BULK_COMPLETE_MEDICAL)
        post = o.post
        newdate = post.date("newdate")
        vet = post.integer("givenvet")
        by = post["givenby"]
        comments = post["treatmentcomments"]
        for mid in post.integer_list("ids"):
            asm3.medical.update_treatment_given(o.dbo, o.user, mid, newdate, by, vet, comments)
        if post.integer("item") != -1:
            asm3.stock.deduct_stocklevel_from_form(o.dbo, o.user, post)

    def post_undo(self, o):
        self.check(asm3.users.BULK_COMPLETE_MEDICAL)
        for mid in o.post.integer_list("ids"):
            asm3.medical.update_treatment_given(o.dbo, o.user, mid, None)

    def post_required(self, o):
        self.check(asm3.users.BULK_COMPLETE_MEDICAL)
        newdate = o.post.date("newdate")
        for mid in o.post.integer_list("ids"):
            asm3.medical.update_treatment_required(o.dbo, o.user, mid, newdate)

class medicalprofile(JSONEndpoint):
    url = "medicalprofile"
    get_permissions = asm3.users.VIEW_MEDICAL

    def controller(self, o):
        med = asm3.medical.get_profiles(o.dbo)
        asm3.al.debug("got %d medical profiles" % len(med), "main.medical_profile", o.dbo)
        return {
            "rows": med
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_MEDICAL)
        asm3.medical.insert_profile_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_MEDICAL)
        asm3.medical.update_profile_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_MEDICAL)
        for mid in o.post.integer_list("ids"):
            asm3.medical.delete_profile(o.dbo, o.user, mid)

class move_adopt(JSONEndpoint):
    url = "move_adopt"
    get_permissions = asm3.users.ADD_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        return {
            "additional": asm3.additional.get_additional_fields(dbo, 0, "movement", asm3.additional.MOVEMENT_ADOPTION),
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "accounts": asm3.financial.get_accounts(dbo, onlybank=True),
            "paymentmethods": asm3.lookups.get_payment_methods(dbo),
            "templates": asm3.template.get_document_templates(dbo, "movement"),
            "templatesemail": asm3.template.get_document_templates(dbo, "email")
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_MOVEMENT)
        dbo = o.dbo
        post = o.post
        l = dbo.locale
        checkout = o.post.boolean("checkoutcreate")
        paperwork = o.post.boolean("sigpaperwork")
        if checkout and post.integer("templateid") == 0:
            raise asm3.utils.ASMValidationError("No template given for checkout")
        if checkout and post.integer("emailtemplateid") == 0:
            raise asm3.utils.ASMValidationError("No email template given for checkout email")
        if paperwork and post.integer("sigtemplateid")== 0:
            raise asm3.utils.ASMValidationError("No template given for paperwork")
        if paperwork and post.integer("sigemailtemplateid") == 0:
            raise asm3.utils.ASMValidationError("No email template given for request signature email")
        movementid = asm3.movement.insert_adoption_from_form(dbo, o.user, post, create_payments = not checkout)
        if checkout:
            l = o.dbo.locale
            body = asm3.wordprocessor.generate_movement_doc(dbo, post.integer("emailtemplateid"), movementid, o.user)
            tokens = asm3.wordprocessor.extract_mail_tokens(body)
            d = {
                "id":           str(movementid),
                "animalid":     post["animal"],
                "personid":     post["person"],
                "templateid":   post["templateid"],
                "feetypeid":    post["feetypeid"],
                "from":         tokens["FROM"] or asm3.configuration.email(dbo),
                "to":           post["emailaddress"],
                "cc":           tokens["CC"] or "",
                "bcc":          tokens["BCC"] or "",
                "subject":      tokens["SUBJECT"] or _("Adoption Checkout", l),
                "body":         tokens["BODY"]
            }
            asm3.movement.send_adoption_checkout(dbo, o.user, asm3.utils.PostedData(d, dbo.locale))
        elif paperwork:
            # Generate the adoption paperwork and save it to the animal/person
            dtid = post.integer("sigtemplateid")
            content = asm3.wordprocessor.generate_movement_doc(dbo, dtid, movementid, o.user)
            tempname = asm3.template.get_document_template_name(dbo, dtid)
            tempname = "%s - %s::%s" % (tempname, asm3.animal.get_animal_namecode(dbo, o.post.integer("animal")), 
                asm3.person.get_person_name(dbo, o.post.integer("person")))
            amid, pmid = asm3.media.create_document_animalperson(dbo, o.user, post.integer("animal"), post.integer("person"), tempname, content)
            # Generate the email body from the email template
            sigbody = asm3.wordprocessor.generate_movement_doc(dbo, post.integer("sigemailtemplateid"), movementid, o.user)
            tokens = asm3.wordprocessor.extract_mail_tokens(sigbody)
            d = {
                "addtolog": "on",
                "logtype":  str(asm3.configuration.system_log_type(dbo)),
                "from":     tokens["FROM"] or asm3.configuration.email(dbo),
                "to":       post["sigemailaddress"],
                "subject":  tokens["SUBJECT"] or _("Document signing request", l),
                "body":     tokens["BODY"]
            }
            asm3.media.send_signature_request(dbo, o.user, pmid, asm3.utils.PostedData(d, dbo.locale))
        return movementid

    def post_cost(self, o):
        dbo = o.dbo
        post = o.post
        l = o.locale
        self.check(asm3.users.VIEW_COST)
        dailyboardcost = asm3.animal.get_daily_boarding_cost(dbo, post.integer("id"))
        dailyboardcostdisplay = format_currency(l, dailyboardcost)
        daysonshelter = asm3.animal.get_days_on_shelter(dbo, post.integer("id"))
        totaldisplay = format_currency(l, dailyboardcost * daysonshelter)
        return totaldisplay + "||" + \
            _("On shelter for {0} days, daily cost {1}, cost record total <b>{2}</b>", l).format(daysonshelter, dailyboardcostdisplay, totaldisplay)
    
    def post_donationdefault(self, o):
        return asm3.lookups.get_donation_default(o.dbo, o.post.integer("donationtype"))

    def post_insurance(self, o):
        return asm3.movement.generate_insurance_number(o.dbo)

class move_book_foster(JSONEndpoint):
    url = "move_book_foster"
    js_module = "movements"
    get_permissions = asm3.users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        movements = asm3.movement.get_active_movements(dbo, asm3.movement.FOSTER)
        movements = asm3.person.reduce_find_results(dbo, o.user, movements, idcol="OWNERID", sitecol="OWNERSITEID")
        movements = o.lf.reduce(movements)
        asm3.al.debug("got %d movements" % len(movements), "main.move_book_foster", dbo)
        return {
            "name": "move_book_foster",
            "rows": movements,
            "movementtypes": asm3.lookups.get_movement_types(dbo),
            "additional": asm3.additional.get_field_definitions(dbo, "movement"),
            "movementtypes_additionalfieldtypes": asm3.additional.MOVEMENT_MAPPING,
            "reservationstatuses": asm3.lookups.get_reservation_statuses(dbo),
            "returncategories": asm3.lookups.get_entryreasons(dbo),
            "templates": asm3.template.get_document_templates(dbo, "movement")
        }

class move_book_recent_adoption(JSONEndpoint):
    url = "move_book_recent_adoption"
    js_module = "movements"
    get_permissions = asm3.users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        movements = asm3.movement.get_recent_adoptions(dbo)
        movements = asm3.person.reduce_find_results(dbo, o.user, movements, idcol="OWNERID", sitecol="OWNERSITEID")
        asm3.al.debug("got %d movements" % len(movements), "main.move_book_recent_adoption", dbo)
        return {
            "name": "move_book_recent_adoption",
            "rows": movements,
            "logtypes": asm3.lookups.get_log_types(dbo), 
            "movementtypes": asm3.lookups.get_movement_types(dbo),
            "additional": asm3.additional.get_field_definitions(dbo, "movement"),
            "movementtypes_additionalfieldtypes": asm3.additional.MOVEMENT_MAPPING,
            "reservationstatuses": asm3.lookups.get_reservation_statuses(dbo),
            "returncategories": asm3.lookups.get_entryreasons(dbo),
            "templates": asm3.template.get_document_templates(dbo, "movement")
        }

class move_book_recent_other(JSONEndpoint):
    url = "move_book_recent_other"
    js_module = "movements"
    get_permissions = asm3.users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        movements = asm3.movement.get_recent_nonfosteradoption(dbo)
        movements = asm3.person.reduce_find_results(dbo, o.user, movements, idcol="OWNERID", sitecol="OWNERSITEID")
        asm3.al.debug("got %d movements" % len(movements), "main.move_book_recent_other", dbo)
        return {
            "name": "move_book_recent_other",
            "rows": movements,
            "movementtypes": asm3.lookups.get_movement_types(dbo),
            "additional": asm3.additional.get_field_definitions(dbo, "movement"),
            "movementtypes_additionalfieldtypes": asm3.additional.MOVEMENT_MAPPING,
            "reservationstatuses": asm3.lookups.get_reservation_statuses(dbo),
            "returncategories": asm3.lookups.get_entryreasons(dbo),
            "templates": asm3.template.get_document_templates(dbo, "movement")
        }

class move_book_recent_transfer(JSONEndpoint):
    url = "move_book_recent_transfer"
    js_module = "movements"
    get_permissions = asm3.users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        movements = asm3.movement.get_recent_transfers(dbo)
        movements = asm3.person.reduce_find_results(dbo, o.user, movements, idcol="OWNERID", sitecol="OWNERSITEID")
        asm3.al.debug("got %d movements" % len(movements), "main.move_book_recent_transfer", dbo)
        return {
            "name": "move_book_recent_transfer",
            "rows": movements,
            "movementtypes": asm3.lookups.get_movement_types(dbo),
            "additional": asm3.additional.get_field_definitions(dbo, "movement"),
            "movementtypes_additionalfieldtypes": asm3.additional.MOVEMENT_MAPPING,
            "reservationstatuses": asm3.lookups.get_reservation_statuses(dbo),
            "returncategories": asm3.lookups.get_entryreasons(dbo),
            "templates": asm3.template.get_document_templates(dbo, "movement")
        }

class move_book_reservation(JSONEndpoint):
    url = "move_book_reservation"
    js_module = "movements"
    get_permissions = asm3.users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        movements = asm3.movement.get_active_reservations(dbo)
        movements = asm3.person.reduce_find_results(dbo, o.user, movements, idcol="OWNERID", sitecol="OWNERSITEID")
        asm3.al.debug("got %d movements" % len(movements), "main.move_book_reservation", dbo)
        return {
            "name": "move_book_reservation",
            "rows": movements,
            "logtypes": asm3.lookups.get_log_types(dbo),
            "movementtypes": asm3.lookups.get_movement_types(dbo),
            "additional": asm3.additional.get_field_definitions(dbo, "movement"),
            "movementtypes_additionalfieldtypes": asm3.additional.MOVEMENT_MAPPING,
            "reservationstatuses": asm3.lookups.get_reservation_statuses(dbo),
            "returncategories": asm3.lookups.get_entryreasons(dbo),
            "templates": asm3.template.get_document_templates(dbo, "movement"),
            "templatesemail": asm3.template.get_document_templates(dbo, "email")
        }

class move_book_retailer(JSONEndpoint):
    url = "move_book_retailer"
    js_module = "movements"
    get_permissions = asm3.users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        movements = asm3.movement.get_active_movements(dbo, asm3.movement.RETAILER)
        movements = asm3.person.reduce_find_results(dbo, o.user, movements, idcol="OWNERID", sitecol="OWNERSITEID")
        asm3.al.debug("got %d movements" % len(movements), "main.move_book_retailer", dbo)
        return {
            "name": "move_book_retailer",
            "rows": movements,
            "logtypes": asm3.lookups.get_log_types(dbo), 
            "movementtypes": asm3.lookups.get_movement_types(dbo),
            "additional": asm3.additional.get_field_definitions(dbo, "movement"),
            "movementtypes_additionalfieldtypes": asm3.additional.MOVEMENT_MAPPING,
            "reservationstatuses": asm3.lookups.get_reservation_statuses(dbo),
            "returncategories": asm3.lookups.get_entryreasons(dbo),
            "templates": asm3.template.get_document_templates(dbo, "movement")
        }

class move_book_soft_release(JSONEndpoint):
    url = "move_book_soft_release"
    js_module = "movements"
    get_permissions = asm3.users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        movements = asm3.movement.get_soft_releases(dbo)
        asm3.al.debug("got %d movements" % len(movements), "main.move_book_soft_release", dbo)
        return {
            "name": "move_book_soft_release",
            "rows": movements,
            "additional": asm3.additional.get_field_definitions(dbo, "movement"),
            "movementtypes": asm3.lookups.get_movement_types(dbo),
            "reservationstatuses": asm3.lookups.get_reservation_statuses(dbo),
            "returncategories": asm3.lookups.get_entryreasons(dbo),
            "templates": asm3.template.get_document_templates(dbo, "movement")
        }

class move_book_trial_adoption(JSONEndpoint):
    url = "move_book_trial_adoption"
    js_module = "movements"
    get_permissions = asm3.users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        movements = asm3.movement.get_trial_adoptions(dbo)
        movements = asm3.person.reduce_find_results(dbo, o.user, movements, idcol="OWNERID", sitecol="OWNERSITEID")
        asm3.al.debug("got %d movements" % len(movements), "main.move_book_trial_adoption", dbo)
        return {
            "name": "move_book_trial_adoption",
            "rows": movements,
            "logtypes": asm3.lookups.get_log_types(dbo), 
            "additional": asm3.additional.get_field_definitions(dbo, "movement"),
            "movementtypes": asm3.lookups.get_movement_types(dbo),
            "reservationstatuses": asm3.lookups.get_reservation_statuses(dbo),
            "returncategories": asm3.lookups.get_entryreasons(dbo),
            "templates": asm3.template.get_document_templates(dbo, "movement")
        }

class move_book_unneutered(JSONEndpoint):
    url = "move_book_unneutered"
    js_module = "movements"
    get_permissions = asm3.users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        movements = asm3.movement.get_recent_unneutered_adoptions(dbo)
        movements = asm3.person.reduce_find_results(dbo, o.user, movements, idcol="OWNERID", sitecol="OWNERSITEID")
        asm3.al.debug("got %d movements" % len(movements), "main.move_book_unneutered", dbo)
        return {
            "name": "move_book_unneutered",
            "rows": movements,
            "logtypes": asm3.lookups.get_log_types(dbo), 
            "additional": asm3.additional.get_field_definitions(dbo, "movement"),
            "movementtypes": asm3.lookups.get_movement_types(dbo),
            "reservationstatuses": asm3.lookups.get_reservation_statuses(dbo),
            "returncategories": asm3.lookups.get_entryreasons(dbo),
            "templates": asm3.template.get_document_templates(dbo, "movement")
        }

class move_deceased(JSONEndpoint):
    url = "move_deceased"
    get_permissions = asm3.users.CHANGE_ANIMAL
    post_permissions = asm3.users.CHANGE_ANIMAL

    def controller(self, o):
        return {
            "deathreasons": asm3.lookups.get_deathreasons(o.dbo),
            "stockitems": asm3.stock.get_stock_items(o.dbo),
            "stockusagetypes": asm3.lookups.get_stock_usage_types(o.dbo)
        }

    def post_create(self, o):
        asm3.animal.update_deceased_from_form(o.dbo, o.user, o.post)
        if o.post.integer("item") != -1:
            asm3.stock.deduct_stocklevel_from_form(o.dbo, o.user, o.post)

class move_donations(JSONEndpoint):
    url = "move_donations"
    get_permissions = asm3.users.VIEW_DONATION

    def controller(self, o):
        dbo = o.dbo
        donations = asm3.financial.get_movement_donations(dbo, o.post["id"])
        asm3.al.debug("got %d donations for movement %s" % (len(donations), o.post["id"]), "main.move_donations", dbo)
        return {
            "message": o.post["message"],
            "id": o.post["id"],
            "animalid": o.post["animalid"],
            "ownerid": o.post["ownerid"],
            "linktype": o.post["linktype"],
            "rows": donations,
            "name": "move_donations",
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "accounts": asm3.financial.get_accounts(dbo, onlybank=True),
            "logtypes": asm3.lookups.get_log_types(dbo), 
            "paymentmethods": asm3.lookups.get_payment_methods(dbo),
            "frequencies": asm3.lookups.get_donation_frequencies(dbo),
            "templates": asm3.template.get_document_templates(dbo, "payment")
        }


class move_foster(JSONEndpoint):
    url = "move_foster"
    get_permissions = asm3.users.ADD_MOVEMENT
    post_permissions = asm3.users.ADD_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        return {
            "additional": asm3.additional.get_additional_fields(dbo, 0, "movement", asm3.additional.MOVEMENT_FOSTER)
        }

    def post_create(self, o):
        return str(asm3.movement.insert_foster_from_form(o.dbo, o.user, o.post))

class move_gendoc(JSONEndpoint):
    url = "move_gendoc"
    get_permissions = asm3.users.GENERATE_DOCUMENTS

    def controller(self, o):
        return {
            "message": o.post["message"],
            "id": o.post["id"],
            "linktype": o.post["linktype"],
            "templates": asm3.template.get_document_templates(o.dbo, "movement")
        }

class move_reclaim(JSONEndpoint):
    url = "move_reclaim"
    get_permissions = asm3.users.ADD_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        return {
            "additional": asm3.additional.get_additional_fields(dbo, 0, "movement", asm3.additional.MOVEMENT_RECLAIMED),
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "accounts": asm3.financial.get_accounts(dbo, onlybank=True),
            "paymentmethods": asm3.lookups.get_payment_methods(dbo)
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_MOVEMENT)
        return str(asm3.movement.insert_reclaim_from_form(o.dbo, o.user, o.post))

    def post_cost(self, o):
        l = o.locale
        dbo = o.dbo
        post = o.post
        self.check(asm3.users.VIEW_COST)
        dailyboardcost = asm3.animal.get_daily_boarding_cost(dbo, post.integer("id"))
        dailyboardcostdisplay = format_currency(l, dailyboardcost)
        daysonshelter = asm3.animal.get_days_on_shelter(dbo, post.integer("id"))
        totaldisplay = format_currency(l, dailyboardcost * daysonshelter)
        return totaldisplay + "||" + _("On shelter for {0} days, daily cost {1}, cost record total <b>{2}</b>", l).format(daysonshelter, dailyboardcostdisplay, totaldisplay)

    def post_donationdefault(self, o):
        return asm3.lookups.get_donation_default(o.dbo, o.post.integer("donationtype"))

class move_reserve(JSONEndpoint):
    url = "move_reserve"
    get_permissions = asm3.users.ADD_MOVEMENT
    post_permissions = asm3.users.ADD_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        return {
            "additional": asm3.additional.get_additional_fields(dbo, 0, "movement", asm3.additional.MOVEMENT_RESERVATION),
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "accounts": asm3.financial.get_accounts(dbo, onlybank=True),
            "paymentmethods": asm3.lookups.get_payment_methods(dbo),
            "reservationstatuses": asm3.lookups.get_reservation_statuses(dbo)
        }

    def post_create(self, o):
        return str(asm3.movement.insert_reserve_from_form(o.dbo, o.user, o.post))

class move_retailer(JSONEndpoint):
    url = "move_retailer"
    get_permissions = asm3.users.ADD_MOVEMENT
    post_permissions = asm3.users.ADD_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        return {
            "additional": asm3.additional.get_additional_fields(dbo, 0, "movement", asm3.additional.MOVEMENT_RETAILER)
        }

    def post_create(self, o):
        return str(asm3.movement.insert_retailer_from_form(o.dbo, o.user, o.post))

class move_transfer(JSONEndpoint):
    url = "move_transfer"
    get_permissions = asm3.users.ADD_MOVEMENT
    post_permissions = asm3.users.ADD_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        return {
            "additional": asm3.additional.get_additional_fields(dbo, 0, "movement", asm3.additional.MOVEMENT_TRANSFER),
        }

    def post_create(self, o):
        return str(asm3.movement.insert_transfer_from_form(o.dbo, o.user, o.post))

class movement(JSONEndpoint):
    url = "movement"

    def post_create(self, o):
        self.check(asm3.users.ADD_MOVEMENT)
        return asm3.movement.insert_movement_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_MOVEMENT)
        asm3.movement.update_movement_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_MOVEMENT)
        for mid in o.post.integer_list("ids"):
            asm3.movement.delete_movement(o.dbo, o.user, mid)

    def post_email(self, o):
        self.check(asm3.users.EMAIL_PERSON)
        asm3.movement.send_movement_emails(o.dbo, o.user, o.post)

    def post_insurance(self, o):
        return asm3.movement.generate_insurance_number(o.dbo)

    def post_cancelreserve(self, o):
        self.check(asm3.users.CHANGE_MOVEMENT)
        for mid in o.post.integer_list("ids"):
            asm3.movement.cancel_reservation(o.dbo, o.user, mid)

    def post_trialfull(self, o):
        self.check(asm3.users.CHANGE_MOVEMENT)
        for mid in o.post.integer_list("ids"):
            asm3.movement.trial_to_full_adoption(o.dbo, o.user, mid)

    def post_checkout(self, o):
        asm3.movement.send_adoption_checkout(o.dbo, o.user, o.post)
        
    def post_eventlink(self, o):
        self.check(asm3.users.LINK_EVENT_MOVEMENT)
        e = asm3.event.get_events_by_date(o.dbo, o.post.date("movementdate"))
        return asm3.utils.json(e)
    
    def post_bulkstatus(self, o):
        self.check(asm3.users.CHANGE_MOVEMENT)
        asm3.movement.bulk_update_movement_statuses(o.dbo, o.user, o.post.integer_list("ids"), o.post.integer("flagid"))

class onlineform_incoming(JSONEndpoint):
    url = "onlineform_incoming"
    get_permissions = asm3.users.VIEW_INCOMING_FORMS

    def controller(self, o):
        headers = asm3.onlineform.get_onlineformincoming_headers(o.dbo)
        asm3.al.debug("got %d submitted headers" % len(headers), "main.onlineform_incoming", o.dbo)
        return {
            "rows": headers
        }

    def post_view(self, o):
        self.check(asm3.users.VIEW_INCOMING_FORMS)
        return asm3.onlineform.get_onlineformincoming_html(o.dbo, o.post.integer("collationid"), include_raw=False)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_INCOMING_FORMS)
        for did in o.post.integer_list("ids"):
            asm3.onlineform.delete_onlineformincoming(o.dbo, o.user, did)

    def post_attachanimal(self, o):
        self.check(asm3.users.ADD_MEDIA)
        dbo = o.dbo
        collationid = o.post.integer("collationid")
        animalid = o.post.integer("animalid")
        asm3.onlineform.attach_animal(dbo, o.user, animalid, collationid)
        if asm3.configuration.onlineform_delete_on_process(dbo): asm3.onlineform.delete_onlineformincoming(o.dbo, o.user, collationid)
        return animalid

    def post_attachanimalbyname(self, o):
        self.check(asm3.users.ADD_MEDIA)
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, animalid, animalname = asm3.onlineform.attach_animalbyname(o.dbo, o.user, pid)
            rv.append("%d|%d|%s" % (collationid, animalid, animalname))
        if asm3.configuration.onlineform_delete_on_process(o.dbo): asm3.onlineform.delete_onlineformincoming(o.dbo, o.user, collationid)
        return "^$".join(rv)

    def post_attachanimalnomedia(self, o):
        self.check(asm3.users.ADD_MEDIA)
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, animalid, animalname = asm3.onlineform.attach_animalbyname(o.dbo, o.user, pid, attachmedia=False)
            rv.append("%d|%d|%s" % (collationid, animalid, animalname))
        if asm3.configuration.onlineform_delete_on_process(o.dbo): asm3.onlineform.delete_onlineformincoming(o.dbo, o.user, collationid)
        return "^$".join(rv)

    def post_attachperson(self, o):
        self.check(asm3.users.ADD_MEDIA)
        dbo = o.dbo
        collationid = o.post.integer("collationid")
        personid = o.post.integer("personid")
        asm3.onlineform.attach_person(dbo, o.user, personid, collationid)
        if asm3.configuration.onlineform_delete_on_process(dbo): asm3.onlineform.delete_onlineformincoming(o.dbo, o.user, collationid)
        return personid 

    def post_animal(self, o):
        self.check(asm3.users.ADD_ANIMAL)
        user = "form/%s" % o.user
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, animalid, animalname, status = asm3.onlineform.create_animal(o.dbo, user, pid)
            rv.append("%d|%d|%s|%s" % (collationid, animalid, animalname, status))
            if asm3.configuration.onlineform_delete_on_process(o.dbo): asm3.onlineform.delete_onlineformincoming(o.dbo, user, collationid)
        return "^$".join(rv)

    def post_animalbroughtin(self, o):
        self.check(asm3.users.ADD_ANIMAL)
        self.check(asm3.users.ADD_PERSON)
        user = "form/%s" % o.user
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, personid, personname, status = asm3.onlineform.create_person(o.dbo, user, pid)
            collationid, animalid, animalname, status = asm3.onlineform.create_animal(o.dbo, user, pid, broughtinby=personid)
            rv.append("%d|%d|%s|%s" % (collationid, animalid, animalname, status))
            if asm3.configuration.onlineform_delete_on_process(o.dbo): asm3.onlineform.delete_onlineformincoming(o.dbo, user, collationid)
        return "^$".join(rv)
    
    def post_animalnonshelter(self, o):
        self.check(asm3.users.ADD_ANIMAL)
        self.check(asm3.users.ADD_PERSON)
        user = "form/%s" % o.user
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, personid, personname, status = asm3.onlineform.create_person(o.dbo, user, pid)
            collationid, animalid, animalname, status = asm3.onlineform.create_animal(o.dbo, user, pid, nsowner=personid)
            rv.append("%d|%d|%s|%s" % (collationid, animalid, animalname, status))
            if asm3.configuration.onlineform_delete_on_process(o.dbo): asm3.onlineform.delete_onlineformincoming(o.dbo, user, collationid)
        return "^$".join(rv)

    def post_person(self, o):
        self.check(asm3.users.ADD_PERSON)
        user = "form/%s" % o.user
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, personid, personname, status = asm3.onlineform.create_person(o.dbo, user, pid)
            rv.append("%d|%d|%s|%s" % (collationid, personid, personname, status))
            if asm3.configuration.onlineform_delete_on_process(o.dbo): asm3.onlineform.delete_onlineformincoming(o.dbo, user, collationid)
        return "^$".join(rv)

    def post_personnomerge(self, o):
        self.check(asm3.users.ADD_PERSON)
        user = "form/%s" % o.user
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, personid, personname, status = asm3.onlineform.create_person(o.dbo, user, pid, merge=False)
            rv.append("%d|%d|%s|%s" % (collationid, personid, personname, status))
            if asm3.configuration.onlineform_delete_on_process(o.dbo): asm3.onlineform.delete_onlineformincoming(o.dbo, user, collationid)
        return "^$".join(rv)

    def post_lostanimal(self, o):
        self.check(asm3.users.ADD_LOST_ANIMAL)
        user = "form/%s" % o.user
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, lostanimalid, personname, status = asm3.onlineform.create_lostanimal(o.dbo, user, pid)
            rv.append("%d|%d|%s|%s" % (collationid, lostanimalid, personname, status))
            if asm3.configuration.onlineform_delete_on_process(o.dbo): asm3.onlineform.delete_onlineformincoming(o.dbo, user, collationid)
        return "^$".join(rv)

    def post_foundanimal(self, o):
        self.check(asm3.users.ADD_FOUND_ANIMAL)
        user = "form/%s" % o.user
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, foundanimalid, personname, status = asm3.onlineform.create_foundanimal(o.dbo, user, pid)
            rv.append("%d|%d|%s|%s" % (collationid, foundanimalid, personname, status))
            if asm3.configuration.onlineform_delete_on_process(o.dbo): asm3.onlineform.delete_onlineformincoming(o.dbo, user, collationid)
        return "^$".join(rv)

    def post_incident(self, o):
        self.check(asm3.users.ADD_INCIDENT)
        user = "form/%s" % o.user
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, incidentid, personname, status = asm3.onlineform.create_animalcontrol(o.dbo, user, pid)
            rv.append("%d|%d|%s|%s" % (collationid, incidentid, personname, status))
            if asm3.configuration.onlineform_delete_on_process(o.dbo): asm3.onlineform.delete_onlineformincoming(o.dbo, user, collationid)
        return "^$".join(rv)

    def post_transport(self, o):
        self.check(asm3.users.ADD_TRANSPORT)
        user = "form/%s" % o.user
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, animalid, animalname = asm3.onlineform.create_transport(o.dbo, user, pid)
            rv.append("%d|%d|%s|0" % (collationid, animalid, animalname))
            if asm3.configuration.onlineform_delete_on_process(o.dbo): asm3.onlineform.delete_onlineformincoming(o.dbo, user, collationid)
        return "^$".join(rv)

    def post_waitinglist(self, o):
        self.check(asm3.users.ADD_WAITING_LIST)
        user = "form/%s" % o.user
        rv = []
        for pid in o.post.integer_list("ids"):
            collationid, wlid, personname, status = asm3.onlineform.create_waitinglist(o.dbo, user, pid)
            rv.append("%d|%d|%s|%s" % (collationid, wlid, personname, status))
            if asm3.configuration.onlineform_delete_on_process(o.dbo): asm3.onlineform.delete_onlineformincoming(o.dbo, user, collationid)
        return "^$".join(rv)

class onlineform_incoming_csv(ASMEndpoint):
    url = "onlineform_incoming_csv"
    get_permissions = asm3.users.VIEW_INCOMING_FORMS

    def content(self, o):
        self.content_type("text/plain")
        self.cache_control(0)
        self.content_disposition("attachment", "incoming%s" % o.post["ids"].replace(",", ""), "csv")
        return asm3.onlineform.get_onlineformincoming_csv(o.dbo, o.post.integer_list("ids"))

class onlineform_incoming_print(ASMEndpoint):
    url = "onlineform_incoming_print"
    get_permissions = asm3.users.VIEW_INCOMING_FORMS

    def content(self, o):
        self.content_type("text/html")
        self.cache_control(0)
        return asm3.onlineform.get_onlineformincoming_html_print(o.dbo, o.post.integer_list("ids"))

class onlineform(JSONEndpoint):
    url = "onlineform"
    get_permissions = asm3.users.VIEW_ONLINE_FORMS
    post_permissions = asm3.users.CHANGE_ONLINE_FORMS

    def controller(self, o):
        l = o.locale
        dbo = o.dbo
        formid = o.post.integer("formid")
        formname = asm3.onlineform.get_onlineform_name(dbo, formid)
        fields = asm3.onlineform.get_onlineformfields(dbo, formid)
        # Make a list of all additional fields, prefixed with the "additional" to
        # add to the autocomplete field names.
        addf = []
        for r in asm3.additional.get_fields(dbo):
            addf.append(f"additional{r.FIELDNAME}")
        title = _("Online Form: {0}", l).format(formname)
        asm3.al.debug("got %d online form fields" % len(fields), "main.onlineform", dbo)
        return {
            "rows": fields,
            "formid": formid,
            "formname": formname,
            "formfields": asm3.utils.deduplicate_list(asm3.onlineform.FORM_FIELDS + addf),
            "species": asm3.lookups.get_species(dbo),
            "title": title
        }

    def post_create(self, o):
        return asm3.onlineform.insert_onlineformfield_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        asm3.onlineform.update_onlineformfield_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        for did in o.post.integer_list("ids"):
            asm3.onlineform.delete_onlineformfield(o.dbo, o.user, did)

    def post_reindex(self, o):
        asm3.onlineform.reindex_onlineform(o.dbo, o.user, o.post.integer("formid"))
        
class onlineforms(JSONEndpoint):
    url = "onlineforms"
    get_permissions = asm3.users.VIEW_ONLINE_FORMS

    def controller(self, o):
        dbo = o.dbo
        onlineforms = asm3.onlineform.get_onlineforms(dbo)
        asm3.al.debug("got %d online forms" % len(onlineforms), "main.onlineforms", dbo)
        return {
            "rows": onlineforms,
            "flags": asm3.lookups.get_person_flags(dbo),
            "header": asm3.onlineform.get_onlineform_header(dbo),
            "footer": asm3.onlineform.get_onlineform_footer(dbo)
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_ONLINE_FORMS)
        return asm3.onlineform.insert_onlineform_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_ONLINE_FORMS)
        asm3.onlineform.update_onlineform_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_ONLINE_FORMS)
        for did in o.post.integer_list("ids"):
            asm3.onlineform.delete_onlineform(o.dbo, o.user, did)

    def post_clone(self, o):
        self.check(asm3.users.ADD_ONLINE_FORMS)
        for did in o.post.integer_list("ids"):
            asm3.onlineform.clone_onlineform(o.dbo, o.user, did)

    def post_headfoot(self, o):
        self.check(asm3.users.CHANGE_ONLINE_FORMS)
        asm3.onlineform.set_onlineform_headerfooter(o.dbo, o.post["rhead"], o.post["rfoot"])

    def post_import(self, o):
        self.check(asm3.users.ADD_ONLINE_FORMS)
        fd = asm3.utils.bytes2str(o.post.filedata())
        if fd.startswith("{"):
            asm3.onlineform.import_onlineform_json(o.dbo, fd)
        else:
            asm3.onlineform.import_onlineform_html(o.dbo, fd)
        self.redirect("onlineforms")

class onlineform_json(ASMEndpoint):
    url = "onlineform_json"
    get_permissions = asm3.users.VIEW_ONLINE_FORMS

    def content(self, o):
        self.content_type("application/json")
        self.cache_control(0)
        return asm3.onlineform.get_onlineform_json(o.dbo, o.post.integer("formid"))

class onlineform_view(ASMEndpoint):
    url = "onlineform_view"
    get_permissions = asm3.users.VIEW_ONLINE_FORMS

    def content(self, o):
        self.content_type("text/html")
        self.cache_control(0)
        return asm3.onlineform.get_onlineform_html(o.dbo, o.post.integer("formid"))

class options(JSONEndpoint):
    url = "options"
    get_permissions = asm3.users.SYSTEM_OPTIONS
    post_permissions = asm3.users.SYSTEM_OPTIONS

    def controller(self, o):
        dbo = o.dbo
        pp_paypal = "%s/pp_paypal" % BASE_URL
        pp_stripe = "%s/pp_stripe" % BASE_URL
        pp_square = "%s/pp_square" % BASE_URL
        if asm3.smcom.active():
            pp_paypal = asm3.smcom.get_payments_url()
            pp_stripe = asm3.smcom.get_payments_url()
            pp_square = asm3.smcom.get_payments_url()
        c = {
            "accounts": asm3.financial.get_accounts(dbo, onlybank=True),
            "accountsexp": asm3.financial.get_accounts(dbo, onlyexpense=True),
            "accountsinc": asm3.financial.get_accounts(dbo, onlyincome=True),
            "animalfindcolumns": asm3.html.json_animalfindcolumns(dbo),
            "animalflags": asm3.lookups.get_animal_flags(dbo),
            "breeds": asm3.lookups.get_breeds(dbo),
            "clinictypes": asm3.lookups.get_clinic_types(dbo),
            "coattypes": asm3.lookups.get_coattypes(dbo),
            "colours": asm3.lookups.get_basecolours(dbo),
            "costtypes": asm3.lookups.get_costtypes(dbo),
            "currencies": asm3.lookups.CURRENCIES,
            "deathreasons": asm3.lookups.get_deathreasons(dbo),
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "eventfindcolumns": asm3.html.json_eventfindcolumns(dbo),
            "entryreasons": asm3.lookups.get_entryreasons(dbo),
            "entrytypes": asm3.lookups.get_entry_types(dbo),
            "foundanimalfindcolumns": asm3.html.json_foundanimalfindcolumns(dbo),
            "incidenttypes": asm3.lookups.get_incident_types(dbo),
            "haspaypal": PAYPAL_VALIDATE_IPN_URL != "",
            "hassquare": SQUARE_PAYMENT_ENVIRONMENT != "",
            "incidentfindcolumns": asm3.html.json_incidentfindcolumns(dbo),
            "jurisdictions": asm3.lookups.get_jurisdictions(dbo),
            "locales": get_locales(),
            "locations": asm3.lookups.get_internal_locations(dbo),
            "logtypes": asm3.lookups.get_log_types(dbo),
            "lostanimalfindcolumns": asm3.html.json_lostanimalfindcolumns(dbo),
            "paymentmethods": asm3.lookups.get_payment_methods(dbo),
            "personfindcolumns": asm3.html.json_personfindcolumns(dbo),
            "pp_paypal": pp_paypal,
            "pp_stripe": pp_stripe,
            "pp_square": pp_square,
            "producttypes": asm3.lookups.get_product_types(dbo),
            "reservationstatuses": asm3.lookups.get_reservation_statuses(dbo),
            "sizes": asm3.lookups.get_sizes(dbo),
            "species": asm3.lookups.get_species(dbo),
            "stockusagetypes": asm3.lookups.get_stock_usage_types(dbo),
            "taxrates": asm3.lookups.get_tax_rates(dbo),
            "themes": asm3.lookups.VISUAL_THEMES,
            "templates": asm3.template.get_document_templates(dbo, "movement"),
            "templatesclinic": asm3.template.get_document_templates(dbo, "clinic"),
            "templateslicence": asm3.template.get_document_templates(dbo, "licence"),
            "testtypes": asm3.lookups.get_test_types(dbo),
            "transporttypes": asm3.lookups.get_transport_types(dbo),
            "types": asm3.lookups.get_animal_types(dbo),
            "urgencies": asm3.lookups.get_urgencies(dbo),
            "usersandroles": asm3.users.get_users_and_roles(dbo),
            "vaccinationtypes": asm3.lookups.get_vaccination_types(dbo),
            "waitinglistcolumns": asm3.html.json_waitinglistcolumns(dbo)
        }
        asm3.al.debug("lookups loaded", "main.options", dbo)
        return c

    def post_save(self, o):
        asm3.configuration.csave(o.dbo, o.user, o.post)
        self.reload_config()

class options_font_preview(ASMEndpoint):
    url = "options_font_preview"
    user_activity = False
    session_cookie = False # Disable sending the cookie with the response to assist with CDN caching

    def content(self, o):
        self.cache_control(CACHE_ONE_YEAR)
        return asm3.media.watermark_font_preview(o.post["fontfile"])

class pp_cardcom(ASMEndpoint):
    """ 
    Cardcom Indicator endpoint. 
    """
    url = "pp_cardcom"
    check_logged_in = False
    use_web_input = False

    def content(self, o):
        asm3.al.debug("in pp_cardcom_content")
        asm3.al.debug(o.post, "main.pp_cardcom")
        asm3.al.debug(self.query(), "main.pp_cardcom")

        querystring = self.query()
        if querystring.startswith("?"):
            querystring = querystring[1:]
        params = asm3.utils.parse_qs(querystring)
        #ReturnValue contains db-payref. Extract db
        client_reference_id = dict(params).get("ReturnValue","")
        dbname = client_reference_id[0:client_reference_id.find("-")]
        dbo = asm3.db.get_database(dbname)
        if dbo.database in asm3.db.ERROR_VALUES:
            asm3.al.error("invalid database '%s'" % dbname, "main.pp_cardcom")
            return
        try:
            dbo.locale = asm3.configuration.locale(dbo)
            dbo.timezone = asm3.configuration.timezone(dbo)
            dbo.timezone_dst = asm3.configuration.timezone_dst(dbo)
            p = asm3.paymentprocessor.cardcom.Cardcom(dbo)
            p.receive(querystring)
        except asm3.paymentprocessor.base.ProcessorError:
            # ProcessorError subclasses are thrown when there is a problem with the 
            # data PayPal have sent, but we do not want them to send it again.
            # By catching these and returning a 200 empty body, they will not
            # send it again.
            return

class pp_paypal(ASMEndpoint):
    """ 
    PayPal IPN endpoint. If we return anything but 200 OK with an
    empty body, PayPal will retry the IPN at a later time. 
    Note that PayPal send POSTed data encoded as cp1252, so we
    parse it ourselves using data_param() instead of web.input (hard-coded to utf-8)
    """
    url = "pp_paypal"
    check_logged_in = False
    use_web_input = False
    data_encoding = "cp1252"

    def post_all(self, o):
        asm3.al.debug(o.data, "main.pp_paypal")
        dbname = self.data_param("custom")
        dbo = asm3.db.get_database(dbname)
        if dbo.database in asm3.db.ERROR_VALUES:
            asm3.al.error("invalid database '%s'" % dbname, "main.pp_paypal")
            return
        try:
            dbo.locale = asm3.configuration.locale(dbo)
            dbo.timezone = asm3.configuration.timezone(dbo)
            dbo.timezone_dst = asm3.configuration.timezone_dst(dbo)
            p = asm3.paymentprocessor.paypal.PayPal(dbo)
            p.receive(o.data)
        except asm3.paymentprocessor.base.ProcessorError:
            # ProcessorError subclasses are thrown when there is a problem with the 
            # data PayPal have sent, but we do not want them to send it again.
            # By catching these and returning a 200 empty body, they will not
            # send it again.
            return

class pp_stripe(ASMEndpoint):
    """
    Stripe webhook endpoint. Like PayPal, a non-200 return code
    will force a retry.
    The payload is utf-8 encoded JSON.
    """
    url = "pp_stripe"
    check_logged_in = False
    use_web_input = False
    data_encoding = "utf-8"

    def post_all(self, o):
        asm3.al.debug(o.data, "main.pp_stripe")
        try:
            j = asm3.utils.json_parse(o.data)
            if "client_reference_id" not in j["data"]["object"]:
                asm3.al.error("client_reference_id missing, this is not an ASM requested payment", "main.pp_stripe")
                return # OK 200, this payment notification is not for us
            client_reference_id = j["data"]["object"]["client_reference_id"]
            dbname = client_reference_id[0:client_reference_id.find("-")]
            dbo = asm3.db.get_database(dbname)
            if dbo.database in asm3.db.ERROR_VALUES:
                asm3.al.error("invalid database '%s'" % dbname, "main.pp_stripe")
                return # OK 200, we can't do anything with this
        except Exception as e:
            asm3.al.error("failed extracting dbname from client_reference_id: %s" % e, "main.pp_stripe")
            return

        try:
            dbo.locale = asm3.configuration.locale(dbo)
            dbo.timezone = asm3.configuration.timezone(dbo)
            dbo.timezone_dst = asm3.configuration.timezone_dst(dbo)
            p = asm3.paymentprocessor.stripeh.Stripe(dbo)
            p.receive(o.data)
        except asm3.paymentprocessor.base.ProcessorError:
            # ProcessorError subclasses are thrown when there is a problem with the 
            # data Stripe have sent, but we do not want them to send it again.
            # By catching these and returning a 200 empty body, they will not
            # send it again.
            return

class pp_square(ASMEndpoint):
    """
    Square webhook endpoint. Like PayPal, a non-200 return code
    will force a retry.
    The payload is utf-8 encoded JSON?
    """
    url = "pp_square"
    check_logged_in = False
    use_web_input = False
    data_encoding = "utf-8"

    def post_all(self, o):
        asm3.al.debug(o.data, "main.pp_square")
        try:
            j = asm3.utils.json_parse(o.data)
            if "note" not in j["data"]["object"]["payment"]:
                asm3.al.error("'note' parameter missing, this is not an ASM requested payment", "main.pp_square")
                return # OK 200, this payment notification is not for us
            note = j["data"]["object"]["payment"]["note"]
            if note == "" or len(note.split("-")) < 2:
                asm3.al.error("'note' parameter invlaid, this is not an ASM requested payment", "main.pp_square")
                return # OK 200, this payment notification is not for us
            
            dbname = note[-2:note.find("-")]
            dbo = asm3.db.get_database(dbname)
            if dbo.database in asm3.db.ERROR_VALUES:
                asm3.al.error("invalid database '%s'" % dbname, "main.pp_square")
                return # OK 200, we can't do anything with this

            if j["data"]["object"]["payment"]["status"] != "COMPLETED":
                asm3.al.error("payment incomplete", "main.pp_square")
                return
        except Exception as e:
            asm3.al.error("failed extracting status from square payment: %s" % e, "main.pp_square")
            return

        try:
            dbo.locale = asm3.configuration.locale(dbo)
            dbo.timezone = asm3.configuration.timezone(dbo)
            dbo.timezone_dst = asm3.configuration.timezone_dst(dbo)
            p = asm3.paymentprocessor.square.Square(dbo)
            p.receive(o.data)
        except asm3.paymentprocessor.base.ProcessorError:
            # ProcessorError subclasses are thrown when there is a problem with the 
            # data Stripe have sent, but we do not want them to send it again.
            # By catching these and returning a 200 empty body, they will not
            # send it again.
            return

class person(JSONEndpoint):
    url = "person"
    get_permissions = asm3.users.VIEW_PERSON

    def controller(self, o):
        dbo = o.dbo
        p = asm3.person.get_person(dbo, o.post.integer("id"))
        if p is None: 
            self.notfound()
        if p.ISSTAFF == 1:
            self.check(asm3.users.VIEW_STAFF)
        if p.ISVOLUNTEER == 1:
            self.check(asm3.users.VIEW_VOLUNTEER)
        if o.siteid != 0 and p.SITEID != 0 and o.siteid != p.SITEID:
            raise asm3.utils.ASMPermissionError("person not in user site")
        asm3.person.check_view_permission(dbo, o.user, o.session, p.ID)
        if (p.LATLONG is None or p.LATLONG == "") and p.OWNERADDRESS != "":
            p.LATLONG = asm3.person.update_geocode(dbo, p.ID, p.LATLONG, p.OWNERADDRESS, p.OWNERTOWN, p.OWNERCOUNTY, p.OWNERPOSTCODE)
        upid = asm3.users.get_personid(dbo, o.user)
        if upid != 0 and upid == p.id:
            raise asm3.utils.ASMPermissionError("cannot view user staff record")
        if asm3.configuration.audit_on_view_record(dbo): asm3.audit.view_record(dbo, o.user, "owner", p.ID, p.OWNERNAME)
        asm3.al.debug("opened person '%s'" % p.OWNERNAME, "main.person", dbo)
        return {
            "additional": asm3.additional.get_additional_fields(dbo, p.id, "person"),
            "animalflags": asm3.lookups.get_animal_flags(dbo),
            "animaltypes": asm3.lookups.get_animal_types(dbo),
            "audit": self.checkb(asm3.users.VIEW_AUDIT_TRAIL) and asm3.audit.get_audit_for_link(dbo, "owner", p.id) or [],
            "species": asm3.lookups.get_species(dbo),
            "breeds": asm3.lookups.get_breeds_by_species(dbo),
            "colours": asm3.lookups.get_basecolours(dbo),
            "flags": asm3.lookups.get_person_flags(dbo, p.ADDITIONALFLAGS),
            "ynun": asm3.lookups.get_ynun(dbo),
            "ynunk": asm3.lookups.get_ynunk(dbo),
            "homecheckhistory": asm3.person.get_homechecked(dbo, p.id),
            "jurisdictions": asm3.lookups.get_jurisdictions(dbo),
            "logtypes": asm3.lookups.get_log_types(dbo),
            "sexes": asm3.lookups.get_sexes(dbo),
            "sites": asm3.lookups.get_sites(dbo),
            "sizes": asm3.lookups.get_sizes(dbo),
            "towns": asm3.person.get_towns(dbo),
            "counties": asm3.person.get_counties(dbo),
            "towncounties": asm3.person.get_town_to_county(dbo),
            "tabcounts": asm3.person.get_satellite_counts(dbo, p.id)[0],
            "templates": asm3.template.get_document_templates(dbo, "person"),
            "templatesemail": asm3.template.get_document_templates(dbo, "email"),
            "roles": asm3.users.get_roles(dbo),
            "person": p
        }

    def post_save(self, o):
        self.check(asm3.users.CHANGE_PERSON)
        asm3.person.update_person_from_form(o.dbo, o.post, o.user)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_PERSON)
        asm3.person.delete_person(o.dbo, o.user, o.post.integer("personid"))

    def post_email(self, o):
        self.check(asm3.users.EMAIL_PERSON)
        asm3.person.send_email_from_form(o.dbo, o.user, o.post)

    def post_latlong(self, o):
        self.check(asm3.users.CHANGE_PERSON)
        asm3.person.update_latlong(o.dbo, o.post.integer("personid"), o.post["latlong"])

    def post_merge(self, o):
        self.check(asm3.users.MERGE_PERSON)
        asm3.person.merge_person(o.dbo, o.user, o.post.integer("personid"), o.post.integer("mergepersonid"))

class person_boarding(JSONEndpoint):
    url = "person_boarding"
    js_module = "boarding"
    get_permissions = asm3.users.VIEW_BOARDING

    def controller(self, o):
        dbo = o.dbo
        p = asm3.person.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        rows = asm3.financial.get_person_boarding(dbo, p.ID)
        asm3.al.debug("got %d person boarding records" % (len(rows)), "main.person_boarding", dbo)
        return {
            "name": "person_boarding",
            "person": p,
            "boardingtypes": asm3.lookups.get_boarding_types(dbo),
            "internallocations": asm3.lookups.get_internal_locations(dbo, o.lf),
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "paymentmethods": asm3.lookups.get_payment_methods(dbo),
            "rows": rows,
            "templates": asm3.template.get_document_templates(dbo, "boarding"),
            "tabcounts": asm3.person.get_satellite_counts(dbo, p.ID)[0]
        }

class person_citations(JSONEndpoint):
    url = "person_citations"
    js_module = "citations"
    get_permissions = asm3.users.VIEW_CITATION

    def controller(self, o):
        dbo = o.dbo
        p = asm3.person.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        citations = asm3.financial.get_person_citations(dbo, o.post.integer("id"))
        asm3.al.debug("got %d citations" % len(citations), "main.person_citations", dbo)
        return {
            "name": "person_citations",
            "rows": citations,
            "person": p,
            "tabcounts": asm3.person.get_satellite_counts(dbo, p.ID)[0],
            "citationtypes": asm3.lookups.get_citation_types(dbo),
            "nextid": dbo.get_id_max("ownercitation")
        }

class person_clinic(JSONEndpoint):
    url = "person_clinic"
    js_module = "clinic_appointment"
    get_permissions = asm3.users.VIEW_CLINIC

    def controller(self, o):
        dbo = o.dbo
        personid = o.post.integer("id")
        p = asm3.person.get_person(dbo, personid)
        if p is None: self.notfound()
        rows = asm3.clinic.get_person_appointments(dbo, personid)
        asm3.al.debug("got %d appointments for person %s" % (len(rows), p.OWNERNAME), "main.person_clinic", dbo)
        return {
            "name": self.url,
            "person": p,
            "tabcounts": asm3.person.get_satellite_counts(dbo, personid)[0],
            "clinicstatuses": asm3.lookups.get_clinic_statuses(dbo),
            "clinictypes": asm3.lookups.get_clinic_types(dbo),
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "paymentmethods": asm3.lookups.get_payment_methods(dbo),
            "forlist": asm3.users.get_users_with_permission(dbo, asm3.users.VIEW_CONSULTING_ROOM),
            "templates": asm3.template.get_document_templates(dbo, "clinic"),
            "rows": rows
        }

class person_diary(JSONEndpoint):
    url = "person_diary"
    js_module = "diary"
    get_permissions = asm3.users.VIEW_DIARY

    def controller(self, o):
        dbo = o.dbo
        p = asm3.person.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        diaries = asm3.diary.get_diaries(dbo, asm3.diary.PERSON, o.post.integer("id"))
        asm3.al.debug("got %d diaries" % len(diaries), "main.person_diary", dbo)
        return {
            "rows": diaries,
            "person": p,
            "tabcounts": asm3.person.get_satellite_counts(dbo, p["ID"])[0],
            "name": "person_diary",
            "linkid": p["ID"],
            "linktypeid": asm3.diary.PERSON,
            "diarytasks": asm3.diary.get_person_tasks(dbo),
            "forlist": asm3.users.get_diary_forlist(dbo)
        }

class person_donations(JSONEndpoint):
    url = "person_donations"
    js_module = "donations"
    get_permissions = asm3.users.VIEW_DONATION

    def controller(self, o):
        dbo = o.dbo
        p = asm3.person.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        donations = asm3.financial.get_person_donations(dbo, o.post.integer("id"))
        return {
            "person": p,
            "tabcounts": asm3.person.get_satellite_counts(dbo, p["ID"])[0],
            "name": "person_donations",
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "accounts": asm3.financial.get_accounts(dbo, onlybank=True),
            "logtypes": asm3.lookups.get_log_types(dbo), 
            "paymentmethods": asm3.lookups.get_payment_methods(dbo),
            "frequencies": asm3.lookups.get_donation_frequencies(dbo),
            "templates": asm3.template.get_document_templates(dbo, "payment"),
            "rows": donations
        }

class person_embed(ASMEndpoint):
    url = "person_embed"
    check_logged_in = False

    def content(self, o):
        if not o.dbo: raise asm3.utils.ASMPermissionError("No session")
        dbo = o.dbo
        self.content_type("application/json")
        self.cache_control(180) # Person data can be cached for a few minutes, useful for multiple widgets on one page
        return asm3.utils.json({
            "additional": asm3.additional.get_additional_fields(dbo, 0, "person"),
            "jurisdictions": asm3.lookups.get_jurisdictions(dbo),
            "towns": asm3.person.get_towns(dbo),
            "counties": asm3.person.get_counties(dbo),
            "towncounties": asm3.person.get_town_to_county(dbo),
            "postcodelookup": asm3.geo.get_postcode_lookup_available(o.locale),
            "flags": asm3.lookups.get_person_flags(dbo),
            "sites": asm3.lookups.get_sites(dbo)
        })

    def post_find(self, o):
        self.check(asm3.users.VIEW_PERSON)
        self.content_type("application/json")
        q = o.post["q"]
        rows = asm3.person.get_person_find_simple(o.dbo, q, o.user, classfilter=o.post["filter"], typefilter=o.post["type"], \
            includeStaff=self.checkb(asm3.users.VIEW_STAFF), \
            includeVolunteers=self.checkb(asm3.users.VIEW_VOLUNTEER), limit=100, siteid=o.siteid)
        asm3.al.debug("find '%s' got %d rows" % (self.query(), len(rows)), "main.person_embed", o.dbo)
        return asm3.utils.json(rows)

    def post_id(self, o):
        self.check(asm3.users.VIEW_PERSON)
        self.content_type("application/json")
        self.cache_control(120)
        dbo = o.dbo
        pid = o.post.integer("id")
        p = asm3.person.get_person_embedded(dbo, pid)
        if not asm3.person.check_view_permission_bool(o.dbo, o.user, o.session, pid):
            p = asm3.person.get_person_embedded_forbidden(dbo, pid)
        if not p:
            asm3.al.error("get person by id %d found no records." % pid, "main.person_embed", dbo)
            raise web.notfound()
        else:
            return asm3.utils.json((p,))

    def post_personwarn(self, o):
        self.check(asm3.users.VIEW_PERSON)
        self.content_type("application/json")
        self.cache_control(120)
        dbo = o.dbo
        pid = o.post.integer("id")
        p = asm3.person.get_person_embedded(dbo, pid)
        if not p:
            asm3.al.error("get person by id %d found no records." % pid, "main.person_embed", dbo)
            raise web.notfound()
        else:
            asm3.person.embellish_adoption_warnings(dbo, p)
            return asm3.utils.json((p,))

    def post_postcodelookup(self, o):
        self.content_type("application/json")
        self.cache_control(120)
        return asm3.geo.get_address(o.dbo, o.post["postcode"], o.post["country"])

    def post_similar(self, o):
        self.check(asm3.users.VIEW_PERSON)
        self.content_type("application/json")
        dbo = o.dbo
        post = o.post
        surname = post["surname"]
        forenames = post["forenames"]
        address = post["address"]
        email = post["emailaddress"]
        mobile = post["mobiletelephone"]
        p = asm3.person.get_person_similar(dbo, email, mobile, surname, forenames, address, siteid=o.siteid, checkcouple=True, checkforenames=False, checkmobilehome=True)
        p = asm3.person.reduce_find_results(dbo, o.user, p)
        if len(p) == 0:
            asm3.al.debug("No similar people found for %s, %s, %s, %s, %s" % (email, mobile, surname, forenames, address), "main.person_embed", dbo)
        else:
            asm3.al.debug("found similar people for %s, %s, %s, %s, %s: got %d records" % (email, mobile, surname, forenames, address, len(p)), "main.person_embed", dbo)
        return asm3.utils.json(p)

    def post_add(self, o):
        self.check(asm3.users.ADD_PERSON)
        self.content_type("application/json")
        dbo = o.dbo
        asm3.al.debug("add new person", "main.person_embed", dbo)
        pid = asm3.person.insert_person_from_form(dbo, o.post, o.user)
        p = asm3.person.get_person(dbo, pid)
        return asm3.utils.json((p,))

class person_find(JSONEndpoint):
    url = "person_find"
    get_permissions = asm3.users.VIEW_PERSON

    def controller(self, o):
        dbo = o.dbo
        flags = asm3.lookups.get_person_flags(dbo)
        asm3.al.debug("lookups loaded", "main.person_find", dbo)
        return {
            "additionalfields": asm3.additional.get_additional_fields(dbo, 0, "person"),
            "flags": flags,
            "jurisdictions": asm3.lookups.get_jurisdictions(dbo),
            "sites": asm3.lookups.get_sites(dbo),
            "users": asm3.users.get_users(dbo)
        }

class person_find_results(JSONEndpoint):
    url = "person_find_results"
    get_permissions = asm3.users.VIEW_PERSON

    def controller(self, o):
        dbo = o.dbo
        mode = o.post["mode"]
        q = o.post["q"]
        if mode == "SIMPLE":
            results = asm3.person.get_person_find_simple(dbo, q, o.user, classfilter="all", \
                includeStaff=self.checkb(asm3.users.VIEW_STAFF), \
                includeVolunteers=self.checkb(asm3.users.VIEW_VOLUNTEER), \
                limit=asm3.configuration.record_search_limit(dbo), siteid=o.siteid)
        else:
            results = asm3.person.get_person_find_advanced(dbo, o.post.data, o.user, \
                includeStaff=self.checkb(asm3.users.VIEW_STAFF), includeVolunteers=self.checkb(asm3.users.VIEW_VOLUNTEER), \
                limit=asm3.configuration.record_search_limit(dbo), siteid=o.siteid)
        add = None
        if len(results) > 0: 
            add = asm3.additional.get_additional_fields_ids(dbo, results, "person")
        asm3.al.debug("found %d results for %s" % (len(results), self.query()), "main.person_find_results", dbo)
        return {
            "rows": results,
            "additional": add
        }

class person_investigation(JSONEndpoint):
    url = "person_investigation"
    get_permissions = asm3.users.VIEW_INVESTIGATION

    def controller(self, o):
        dbo = o.dbo
        p = asm3.person.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        investigation = asm3.person.get_investigation(dbo, o.post.integer("id"))
        asm3.al.debug("got %d investigation records for person %s" % (len(investigation), p["OWNERNAME"]), "main.person_investigation", dbo)
        return {
            "rows": investigation,
            "person": p,
            "tabcounts": asm3.person.get_satellite_counts(dbo, p["ID"])[0]
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_INVESTIGATION)
        return str(asm3.person.insert_investigation_from_form(o.dbo, o.user, o.post))

    def post_update(self, o):
        self.check(asm3.users.CHANGE_INVESTIGATION)
        asm3.person.update_investigation_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_INVESTIGATION)
        for did in o.post.integer_list("ids"):
            asm3.person.delete_investigation(o.dbo, o.user, did)

class person_licence(JSONEndpoint):
    url = "person_licence"
    js_module = "licence"
    get_permissions = asm3.users.VIEW_LICENCE

    def controller(self, o):
        dbo = o.dbo
        p = asm3.person.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        licences = asm3.financial.get_person_licences(dbo, o.post.integer("id"))
        asm3.al.debug("got %d licences" % len(licences), "main.person_licence", dbo)
        return {
            "name": "person_licence",
            "rows": licences,
            "person": p,
            "baselink": f"{SERVICE_URL}?account={dbo.name()}&method=checkout_licence&token=",
            "templates": asm3.template.get_document_templates(dbo, "licence"),
            "tabcounts": asm3.person.get_satellite_counts(dbo, p["ID"])[0],
            "licencetypes": asm3.lookups.get_licence_types(dbo)
        }

class person_log(JSONEndpoint):
    url = "person_log"
    js_module = "log"
    get_permissions = asm3.users.VIEW_LOG

    def controller(self, o):
        dbo = o.dbo
        logfilter = o.post.integer("filter")
        if logfilter == 0: logfilter = asm3.configuration.default_log_filter(dbo)
        p = asm3.person.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        logs = asm3.log.get_logs(dbo, asm3.log.PERSON, o.post.integer("id"), logfilter)
        return {
            "name": "person_log",
            "linkid": o.post.integer("id"),
            "linktypeid": asm3.log.PERSON,
            "filter": logfilter,
            "rows": logs,
            "person": p,
            "tabcounts": asm3.person.get_satellite_counts(dbo, p["ID"])[0],
            "logtypes": asm3.lookups.get_log_types(dbo)
        }

class person_lookingfor(ASMEndpoint):
    url = "person_lookingfor"
    get_permissions = asm3.users.VIEW_PERSON

    def content(self, o):
        self.content_type("text/html")
        if o.post.integer("personid") == 0:
            return asm3.cachedisk.get("lookingfor_report", o.dbo.name())
        else:
            return asm3.person.lookingfor_report(o.dbo, o.user, o.post.integer("personid"))

class person_links(JSONEndpoint):
    url = "person_links"
    get_permissions = asm3.users.VIEW_PERSON_LINKS

    def controller(self, o):
        dbo = o.dbo
        links = asm3.person.get_links(dbo, o.post.integer("id"))
        p = asm3.person.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        asm3.al.debug("got %d person links" % len(links), "main.person_links", dbo)
        return {
            "links": links,
            "person": p,
            "tabcounts": asm3.person.get_satellite_counts(dbo, p["ID"])[0]
        }

class person_media(JSONEndpoint):
    url = "person_media"
    js_module = "media"
    get_permissions = asm3.users.VIEW_MEDIA

    def controller(self, o):
        dbo = o.dbo
        p = asm3.person.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        m = asm3.media.get_media(dbo, asm3.media.PERSON, o.post.integer("id"))
        asm3.al.debug("got %d media" % len(m), "main.person_media", dbo)
        return {
            "media": m,
            "person": p,
            "tabcounts": asm3.person.get_satellite_counts(dbo, p["ID"])[0],
            "showpreferred": True,
            "canwatermark": False,
            "documentrepository": asm3.dbfs.get_document_repository(o.dbo),
            "linkid": o.post.integer("id"),
            "linktypeid": asm3.media.PERSON,
            "logtypes": asm3.lookups.get_log_types(dbo),
            "name": self.url,
            "flags": asm3.lookups.get_media_flags(dbo),
            "resizeimagespec": asm3.utils.iif(RESIZE_IMAGES_DURING_ATTACH, RESIZE_IMAGES_SPEC, ""),
            "templates": asm3.template.get_document_templates(dbo, "email"),
            "sigtype": ELECTRONIC_SIGNATURES
        }

class person_movements(JSONEndpoint):
    url = "person_movements"
    js_module = "movements"
    get_permissions = asm3.users.VIEW_MOVEMENT

    def controller(self, o):
        dbo = o.dbo
        p = asm3.person.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        movements = asm3.movement.get_person_movements(dbo, o.post.integer("id"))
        movements = asm3.person.reduce_find_results(dbo, o.user, movements, idcol="OWNERID", sitecol="OWNERSITEID")
        asm3.al.debug("got %d movements" % len(movements), "main.person_movements", dbo)
        return {
            "name": "person_movements",
            "rows": movements,
            "person": p,
            "tabcounts": asm3.person.get_satellite_counts(dbo, p["ID"])[0],
            "logtypes": asm3.lookups.get_log_types(dbo), 
            "movementtypes": asm3.lookups.get_movement_types(dbo),
            "additional": asm3.additional.get_field_definitions(dbo, "movement"),
            "movementtypes_additionalfieldtypes": asm3.additional.MOVEMENT_MAPPING,
            "reservationstatuses": asm3.lookups.get_reservation_statuses(dbo),
            "returncategories": asm3.lookups.get_entryreasons(dbo),
            "templates": asm3.template.get_document_templates(dbo, "movement"),
            "templatesemail": asm3.template.get_document_templates(dbo, "email")
        }

class person_new(JSONEndpoint):
    url = "person_new"
    get_permissions = asm3.users.ADD_PERSON
    post_permissions = asm3.users.ADD_PERSON

    def controller(self, o):
        dbo = o.dbo
        asm3.al.debug("add person", "main.person_new", dbo)
        return {
            "towns": asm3.person.get_towns(dbo),
            "counties": asm3.person.get_counties(dbo),
            "towncounties": asm3.person.get_town_to_county(dbo),
            "additional": asm3.additional.get_additional_fields(dbo, 0, "person"),
            "jurisdictions": asm3.lookups.get_jurisdictions(dbo),
            "postcodelookup": asm3.geo.get_postcode_lookup_available(o.locale),
            "flags": asm3.lookups.get_person_flags(dbo),
            "sites": asm3.lookups.get_sites(dbo)
        }

    def post_all(self, o):
        return str(asm3.person.insert_person_from_form(o.dbo, o.post, o.user))

class person_rota(JSONEndpoint):
    url = "person_rota"
    js_module = "rota"
    get_permissions = asm3.users.VIEW_ROTA

    def controller(self, o):
        dbo = o.dbo
        p = asm3.person.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        rota = asm3.person.get_person_rota(dbo, o.post.integer("id"))
        asm3.al.debug("got %d rota items" % len(rota), "main.person_rota", dbo)
        return {
            "name": "person_rota",
            "rows": rota,
            "person": p,
            "rotatypes": asm3.lookups.get_rota_types(dbo),
            "worktypes": asm3.lookups.get_work_types(dbo),
            "tabcounts": asm3.person.get_satellite_counts(dbo, p["ID"])[0]
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_ROTA)
        return asm3.person.insert_rota_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_ROTA)
        asm3.person.update_rota_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_ROTA)
        for rid in o.post.integer_list("ids"):
            asm3.person.delete_rota(o.dbo, o.user, rid)

class person_traploan(JSONEndpoint):
    url = "person_traploan"
    js_module = "traploan"
    get_permissions = asm3.users.VIEW_TRAPLOAN

    def controller(self, o):
        dbo = o.dbo
        p = asm3.person.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        traploans = asm3.animalcontrol.get_person_traploans(dbo, o.post.integer("id"))
        asm3.al.debug("got %d trap loans" % len(traploans), "main.person_traploan", dbo)
        return {
            "name": "person_traploan",
            "rows": traploans,
            "person": p,
            "tabcounts": asm3.person.get_satellite_counts(dbo, p["ID"])[0],
            "traptypes": asm3.lookups.get_trap_types(dbo)
        }

class person_vouchers(JSONEndpoint):
    url = "person_vouchers"
    js_module = "vouchers"
    get_permissions = asm3.users.VIEW_VOUCHER

    def controller(self, o):
        dbo = o.dbo
        p = asm3.person.get_person(dbo, o.post.integer("id"))
        if p is None: self.notfound()
        vouchers = asm3.financial.get_person_vouchers(dbo, o.post.integer("id"))
        asm3.al.debug("got %d person vouchers" % len(vouchers), "main.person_vouchers", dbo)
        return {
            "name": "person_vouchers",
            "rows": vouchers,
            "person": p,
            "tabcounts": asm3.person.get_satellite_counts(dbo, p["ID"])[0],
            "templates": asm3.template.get_document_templates(dbo, "voucher"),
            "vouchertypes": asm3.lookups.get_voucher_types(dbo)
        }

class product(JSONEndpoint):
    url = "product"
    js_module = "product"
    get_permissions = asm3.users.VIEW_STOCKLEVEL

    def controller(self, o):
        dbo = o.dbo
        productid = 0
        if o.post["id"]:
            productid = o.post.integer("id")
        if o.post.integer("productfilter") == -1:
            products = asm3.stock.get_depleted_products(dbo)
        elif o.post.integer("productfilter") == -2:
            products = asm3.stock.get_low_balance_products(dbo)
        elif o.post.integer("productfilter") == -3:
            products = asm3.stock.get_negative_balance_products(dbo)
        elif o.post.integer("productfilter") == -4:
            products = asm3.stock.get_retired_products(dbo)
        else:
            products = asm3.stock.get_active_products(dbo)
        asm3.al.debug("got %d products" % len(products), "main.product", dbo)
        return {
            "productid": productid,
            "producttypes": asm3.stock.get_product_types(dbo),
            "taxrates": asm3.stock.get_tax_rates(dbo),
            "stocklocations": asm3.lookups.get_stock_locations(dbo),
            "stockusagetypes": asm3.lookups.get_stock_usage_types(dbo),
            "units": asm3.lookups.get_unit_types(dbo),
            "yesno": asm3.lookups.get_yesno(dbo),
            "rows": products
        }
    
    def post_create(self, o):
        self.check(asm3.users.ADD_STOCKLEVEL)
        productid = asm3.stock.insert_product_from_form(o.dbo, o.post, o.user)
        return productid
        
    
    def post_move(self, o):
        self.check(asm3.users.CHANGE_STOCKLEVEL)
        asm3.stock.insert_productmovement_from_form(o.dbo, o.post, o.user)
    
    def post_update(self, o):
        self.check(asm3.users.CHANGE_STOCKLEVEL)
        asm3.stock.update_product_from_form(o.dbo, o.post, o.user)
    
    def post_delete(self, o):
        self.check(asm3.users.DELETE_STOCKLEVEL)
        for pid in o.post.integer_list("ids"):
            asm3.stock.delete_product(o.dbo, o.user, pid)

class publish(JSONEndpoint):
    url = "publish"
    get_permissions = asm3.users.USE_INTERNET_PUBLISHER

    def controller(self, o):
        dbo = o.dbo
        mode = o.post["mode"]
        failed = False
        asm3.al.debug("publish started for mode %s" % mode, "main.publish", dbo)
        # If a publisher is already running and we have a mode, mark
        # a failure starting
        if asm3.asynctask.is_task_running(dbo):
            asm3.al.debug("publish already running, not starting new publish", "main.publish", dbo)
        else:
            # If a publishing mode is requested, start that publisher
            # running on a background thread
            asm3.publish.start_publisher(dbo, mode, user=o.user, newthread=True)
        return { "failed": failed }

    def post_poll(self, o):
        return "%s|%d|%s" % (asm3.asynctask.get_task_name(o.dbo), asm3.asynctask.get_progress_percent(o.dbo), asm3.asynctask.get_last_error(o.dbo))

    def post_stop(self, o):
        asm3.asynctask.set_cancel(o.dbo, True)

class publish_logs(JSONEndpoint):
    url = "publish_logs"
    get_permissions = asm3.users.USE_INTERNET_PUBLISHER

    def controller(self, o):
        logs = asm3.publish.get_publish_logs(o.dbo)
        asm3.al.debug("viewing %d publishing logs" % len(logs), "main.publish_logs", o.dbo)
        return {
            "rows": logs
        }

class publish_log_view(ASMEndpoint):
    url = "publish_log_view"
    get_permissions = asm3.users.USE_INTERNET_PUBLISHER

    def content(self, o):
        asm3.al.debug("viewing log file %s" % o.post["view"], "main.publish_logs", o.dbo)
        self.cache_control(CACHE_ONE_WEEK) # log files never change
        self.content_type("text/plain")
        self.content_disposition("inline", o.post["view"], "txt", "log.txt")
        return asm3.publish.get_publish_log(o.dbo, o.post.integer("view"))

class publish_options(JSONEndpoint):
    url = "publish_options"
    get_permissions = asm3.users.PUBLISH_OPTIONS
    post_permissions = asm3.users.PUBLISH_OPTIONS

    def controller(self, o):
        dbo = o.dbo
        c = {
            "breeds": asm3.lookups.get_breeds(dbo),
            "locations": asm3.lookups.get_internal_locations(dbo),
            "flags": asm3.lookups.get_animal_flags(dbo),
            "hasakcreunite": AKC_REUNITE_BASE_URL != "",
            "hasbuddyid": BUDDYID_BASE_URL != "",
            "hasfindpet": FINDPET_BASE_URL != "",
            "hasfoundanimals": FOUNDANIMALS_FTP_USER != "",
            "hashomeagain": HOMEAGAIN_BASE_URL != "",
            "hashtmlftp": HTMLFTP_PUBLISHER_ENABLED,
            "hasmaddiesfund": MADDIES_FUND_TOKEN_URL != "",
            "haspetcademy": PETCADEMY_FTP_HOST != "",
            "haspetlink": PETLINK_BASE_URL != "",
            "haspetslocated": PETSLOCATED_FTP_USER != "",
            "hassac": SAC_METRICS_URL != "",
            "hassmarttag": SMARTTAG_FTP_USER != "",
            "hasvetenvoy": False, # Disabled. VETENVOY_US_BASE_URL != "",
            "haspetrescue": PETRESCUE_URL != "",
            "hassavourlife": SAVOURLIFE_URL != "",
            "entryreasons": asm3.lookups.get_entryreasons(dbo),
            "logtypes": asm3.lookups.get_log_types(dbo),
            "styles": asm3.template.get_html_template_names(dbo),
            "users": asm3.users.get_users(dbo)
        }
        asm3.al.debug("loaded lookups", "main.publish_options", dbo)
        return c

    def post_save(self, o):
        asm3.configuration.csave(o.dbo, o.user, o.post)
        self.reload_config()

    def post_vesignup(self, o):
        userid, userpwd = asm3.publishers.vetenvoy.VetEnvoyUSMicrochipPublisher.signup(o.dbo, o.post)
        return "%s,%s" % (userid, userpwd)

class report(ASMEndpoint):
    url = "report"
    get_permissions = asm3.users.VIEW_REPORT

    def content(self, o):
        dbo = o.dbo
        post = o.post
        crid = post.integer("id")
        # Make sure this user has a role that can view the report
        asm3.reports.check_view_permission(o.session, crid)
        crit = asm3.reports.get_criteria(dbo, crid)
        self.content_type("text/html")
        self.cache_control(0)
        # If this report takes criteria and none were supplied, go to the criteria screen instead to get them
        if len(crit) != 0 and post["hascriteria"] == "": self.redirect("report_criteria?id=%d&target=report" % post.integer("id"))
        title = asm3.reports.get_title(dbo, crid)
        asm3.al.debug("got criteria (%s), executing report %d %s" % (str(post.data), crid, title), "main.report", dbo)
        p = asm3.reports.get_criteria_params(dbo, crid, post)
        if asm3.configuration.audit_on_view_report(dbo):
            asm3.audit.view_report(dbo, o.user, crid, title, str(post.data))
        s = asm3.reports.execute(dbo, crid, o.user, p)
        return s

class report_criteria(JSONEndpoint):
    url = "report_criteria"
    get_permissions = asm3.users.VIEW_REPORT

    def controller(self, o):
        dbo = o.dbo
        post = o.post
        title = asm3.reports.get_title(o.dbo, post.integer("id"))
        crit = asm3.reports.get_criteria(dbo, post.integer("id"))
        asm3.al.debug("building report criteria form for report %d %s" % (post.integer("id"), title), "main.report_criteria", dbo)
        def has_criteria(c):
            for name, rtype, question in crit:
                if rtype == c: return True
            return False
        c = {
            "id":           post.integer("id"),
            "title":        title,
            "target":       post["target"],
            "criteria":     crit
        }
        if has_criteria("ANIMALFLAG"): c["animalflags"] = asm3.lookups.get_animal_flags(dbo)
        if has_criteria("DONATIONTYPE") or has_criteria("PAYMENTTYPE"): c["donationtypes"] = asm3.lookups.get_donation_types(dbo)
        if has_criteria("ENTRYCATEGORY"): c["entryreasons"] = asm3.lookups.get_entryreasons(dbo)
        if has_criteria("LITTER"): c["litters"] = asm3.animal.get_active_litters_brief(dbo)
        if has_criteria("LOCATION"): c["locations"] = asm3.lookups.get_internal_locations(dbo, o.lf)
        if has_criteria("LOGTYPE"): c["logtypes"] = asm3.lookups.get_log_types(dbo)
        if has_criteria("MEDIAFLAG"): c["mediaflags"] = asm3.lookups.get_media_flags(dbo)
        if has_criteria("PAYMENTMETHOD") or has_criteria("PAYMENTTYPE"): c["paymentmethods"] = asm3.lookups.get_payment_methods(dbo)
        if has_criteria("PERSON"): c["people"] = asm3.person.get_person_name_addresses(dbo)
        if has_criteria("PERSONFLAG"): c["personflags"] = asm3.lookups.get_person_flags(dbo)
        if has_criteria("SITE"): c["sites"] = asm3.lookups.get_sites(dbo)
        if has_criteria("SPECIES"): c["species"] = asm3.lookups.get_species(dbo)
        if has_criteria("TYPE"): c["types"] = asm3.lookups.get_animal_types(dbo)
        return c

class report_export(JSONEndpoint):
    url = "report_export"
    get_permissions = asm3.users.EXPORT_REPORT

    def controller(self, o):
        dbo = o.dbo
        reports = asm3.reports.get_available_reports(dbo)
        asm3.al.debug("exporting %d reports" % len(reports), "main.report_export", dbo)
        return {
            "rows": reports
        }

class report_export_csv(ASMEndpoint):
    url = "report_export_csv"
    get_permissions = asm3.users.EXPORT_REPORT

    def content(self, o):
        dbo = o.dbo
        post = o.post
        crid = post.integer("id")
        crit = asm3.reports.get_criteria(dbo, crid)
        # If this report takes criteria and none were supplied, go to the criteria screen instead to get them
        if len(crit) != 0 and post["hascriteria"] == "": self.redirect("report_criteria?id=%d&target=report_export_csv" % crid)
        # Make sure this user has a role that can view the report
        asm3.reports.check_view_permission(o.session, crid)
        title = asm3.reports.get_title(dbo, crid)
        p = asm3.reports.get_criteria_params(dbo, crid, post)
        rows, cols = asm3.reports.execute_query(dbo, crid, o.user, p)
        titlecaseheader = cols is not None and "TITLECASEHEADER" in cols
        lowercaseheader = cols is not None and "LOWERCASEHEADER" in cols
        renameheader = ""
        if cols is not None and "RENAMEHEADER" in cols and len(rows) > 0:
            renameheader = rows[0].RENAMEHEADER
        self.content_type("text/csv")
        self.content_disposition("attachment", title, "csv", "report.csv")
        cols = [ c for c in cols if c not in ( "TITLECASEHEADER", "LOWERCASEHEADER", "RENAMEHEADER" ) ]
        return asm3.utils.csv_generator(o.locale, rows, cols, includeheader=True, titlecaseheader=titlecaseheader, lowercaseheader=lowercaseheader, renameheader=renameheader)

class report_export_email(ASMEndpoint):
    url = "report_export_email"
    get_permissions = asm3.users.EXPORT_REPORT

    def content(self, o):
        dbo = o.dbo
        post = o.post
        crid = post.integer("id")
        email = post["email"]
        crit = asm3.reports.get_criteria(dbo, crid)
        # If this report takes criteria and none were supplied, go to the criteria screen instead to get them
        if len(crit) != 0 and post["hascriteria"] == "": self.redirect("report_criteria?id=%d&target=report_export_email" % crid)
        # Make sure this user has a role that can view the report
        asm3.reports.check_view_permission(o.session, crid)
        title = asm3.reports.get_title(dbo, crid)
        p = asm3.reports.get_criteria_params(dbo, crid, post)
        content = asm3.reports.execute(dbo, crid, o.user, p)
        asm3.utils.send_email(dbo, asm3.configuration.email(dbo), email, "", "", title, content, "html")
        self.redirect("report%s" % self.query() + "&sent=1")

class report_export_excel(ASMEndpoint):
    url = "report_export_excel"
    get_permissions = asm3.users.EXPORT_REPORT

    def content(self, o):
        dbo = o.dbo
        post = o.post
        crid = post.integer("id")
        crit = asm3.reports.get_criteria(dbo, crid)
        # If this report takes criteria and none were supplied, go to the criteria screen instead to get them
        if len(crit) != 0 and post["hascriteria"] == "": self.redirect("report_criteria?id=%d&target=report_export_excel" % crid)
        # Make sure this user has a role that can view the report
        asm3.reports.check_view_permission(o.session, crid)
        title = asm3.reports.get_title(dbo, crid)
        p = asm3.reports.get_criteria_params(dbo, crid, post)
        rows, cols = asm3.reports.execute_query(dbo, crid, o.user, p)
        titlecaseheader = cols is not None and "TITLECASEHEADER" in cols
        lowercaseheader = cols is not None and "LOWERCASEHEADER" in cols
        renameheader = ""
        if cols is not None and "RENAMEHEADER" in cols and len(rows) > 0:
            renameheader = rows[0].RENAMEHEADER
        self.content_type("application/vnd.ms-excel")
        self.content_disposition("attachment", title, "xlsx", "report.xlsx")
        cols = [ c for c in cols if c not in ( "TITLECASEHEADER", "LOWERCASEHEADER", "RENAMEHEADER" ) ]
        return asm3.utils.excel(o.locale, rows, cols, includeheader=True, titlecaseheader=titlecaseheader, lowercaseheader=lowercaseheader, renameheader=renameheader)

class report_export_pdf(ASMEndpoint):
    url = "report_export_pdf"
    get_permissions = asm3.users.EXPORT_REPORT

    def content(self, o):
        dbo = o.dbo
        post = o.post
        crid = post.integer("id")
        crit = asm3.reports.get_criteria(dbo, crid)
        # If this report takes criteria and none were supplied, go to the criteria screen instead to get them
        if len(crit) != 0 and post["hascriteria"] == "": self.redirect("report_criteria?id=%d&target=report_export_pdf" % crid)
        # Make sure this user has a role that can view the report
        asm3.reports.check_view_permission(o.session, crid)
        p = asm3.reports.get_criteria_params(dbo, crid, post)
        disp = asm3.configuration.pdf_inline(dbo) and "inline" or "attachment"
        self.content_type("application/pdf")
        self.content_disposition(disp, "report.pdf")
        return asm3.utils.html_to_pdf(dbo, asm3.reports.execute(dbo, crid, o.user, p))

class report_images(JSONEndpoint):
    url = "report_images"
    
    def controller(self, o):
        images = asm3.dbfs.get_report_images(o.dbo)
        asm3.al.debug("got %d extra images" % len(images), "main.report_images", o.dbo)
        return { "rows": images }

    def post_create(self, o):
        asm3.dbfs.upload_report_image(o.dbo, o.post.data.filechooser)
        self.reload_config()
        self.redirect("report_images")

    def post_delete(self, o):
        for i in o.post["ids"].split(","):
            if i != "": asm3.dbfs.delete_filepath(o.dbo, "/reports/" + i)
        self.reload_config()

    def post_rename(self, o):
        asm3.dbfs.rename_file(o.dbo, "/reports", o.post["oldname"], o.post["newname"])

class reports(JSONEndpoint):
    url = "reports"
    get_permissions = asm3.users.VIEW_REPORT

    def controller(self, o):
        dbo = o.dbo
        reports = asm3.reports.get_reports(dbo)
        header = asm3.reports.get_raw_report_header(dbo)
        footer = asm3.reports.get_raw_report_footer(dbo)
        asm3.al.debug("editing %d reports" % len(reports), "main.reports", dbo)
        return {
            "categories": "|".join(asm3.reports.get_categories(dbo)),
            "recommended": asm3.reports.RECOMMENDED_REPORTS,
            "header": header,
            "footer": footer,
            "roles": asm3.users.get_roles(dbo),
            "additionalfields": asm3.additional.get_fields(dbo),
            "animalflags": asm3.lookups.get_animal_flags(dbo),
            "animaltypes": asm3.lookups.get_animal_types(dbo),
            "donationtypes": asm3.lookups.get_donation_types(dbo),
            "entryreasons": asm3.lookups.get_entryreasons(dbo),
            "incidenttypes": asm3.lookups.get_incident_types(dbo),
            "completedtypes": asm3.lookups.get_incident_completed_types(dbo),
            "jurisdictions": asm3.lookups.get_jurisdictions(dbo),
            "locations": asm3.lookups.get_internal_locations(dbo),
            "medicalprofiles": asm3.medical.get_profiles(o.dbo),
            "paymentmethods": asm3.lookups.get_payment_methods(dbo),
            "personflags": asm3.lookups.get_person_flags(dbo),
            "sizes": asm3.lookups.get_sizes(dbo),
            "species": asm3.lookups.get_species(dbo),
            "testtypes": asm3.lookups.get_test_types(dbo),
            "urgencies": asm3.lookups.get_urgencies(dbo),
            "vaccinationtypes": asm3.lookups.get_vaccination_types(dbo),
            "rows": reports
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_REPORT)
        rid = asm3.reports.insert_report_from_form(o.dbo, o.user, o.post)
        self.reload_config()
        return rid

    def post_update(self, o):
        self.check(asm3.users.CHANGE_REPORT)
        asm3.reports.update_report_from_form(o.dbo, o.user, o.post)
        self.reload_config()

    def post_delete(self, o):
        self.check(asm3.users.DELETE_REPORT)
        for rid in o.post.integer_list("ids"):
            asm3.reports.delete_report(o.dbo, o.user, rid)
        self.reload_config()
    
    def post_bulkupdateviewroles(self, o):
        self.check(asm3.users.CHANGE_REPORT)
        asm3.reports.update_report_viewroles_from_form(o.dbo, o.post.integer_list("reportids"), o.post.integer_list("viewbulkroles"))
        self.reload_config()

    def post_sql(self, o):
        self.check(asm3.users.USE_SQL_INTERFACE)
        asm3.reports.check_sql(o.dbo, o.user, o.post["sql"])

    def post_genhtml(self, o):
        self.check(asm3.users.USE_SQL_INTERFACE)
        return asm3.reports.generate_html(o.dbo, o.user, o.post["sql"])

    def post_headfoot(self, o):
        self.check(asm3.users.CHANGE_REPORT)
        asm3.reports.set_raw_report_headerfooter(o.dbo, o.post["rhead"], o.post["rfoot"])

    def post_smcomlist(self, o):
        return asm3.utils.json(asm3.reports.get_smcom_reports_installable(o.dbo))

    def post_smcominstall(self, o):
        self.check(asm3.users.ADD_REPORT)
        asm3.reports.install_smcom_reports(o.dbo, o.user, o.post.integer_list("ids"))
        self.reload_config()

class roles(JSONEndpoint):
    url = "roles"
    get_permissions = asm3.users.EDIT_USER
    post_permissions = asm3.users.EDIT_USER

    def controller(self, o):
        roles = asm3.users.get_roles(o.dbo)
        asm3.al.debug("editing %d roles" % len(roles), "main.roles", o.dbo)
        return { "rows": roles }

    def post_create(self, o):
        asm3.users.insert_role_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        asm3.users.update_role_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        for rid in o.post.integer_list("ids"):
            asm3.users.delete_role(o.dbo, o.user, rid)

class search(JSONEndpoint):
    url = "search"
    
    def controller(self, o):
        q = o.post["q"]
        results, timetaken, explain, sortname = asm3.search.search(o.dbo, o, q)
        is_large_db = ""
        if o.dbo.is_large_db: is_large_db = " (indexed only)"
        asm3.al.debug("searched for '%s', got %d results in %s, sorted %s %s" % (q, len(results), timetaken, sortname, is_large_db), "main.search", o.dbo)
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
    session_cookie = False

    def handle(self, o):
        contenttype, client_ttl, cache_ttl, response = asm3.service.handler(o.post, PATH, self.remote_ip(), self.referer(), self.user_agent(), self.query())
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
    get_permissions = asm3.users.VIEW_ANIMAL

    def controller(self, o):
        dbo = o.dbo
        animals = asm3.animal.get_shelterview_animals(dbo, o.lf)
        asm3.al.debug("got %d animals for shelterview" % (len(animals)), "main.shelterview", dbo)
        return {
            "animals": animals,
            "flags": asm3.lookups.get_animal_flags(dbo),
            "fosterers": asm3.person.get_shelterview_fosterers(dbo, o.siteid),
            "locations": asm3.lookups.get_internal_locations(dbo, o.lf),
            "perrow": asm3.configuration.main_screen_animal_link_max(dbo),
            "unitextra": asm3.configuration.unit_extra(dbo)
        }

    def post_editunit(self, o):
        self.check(asm3.users.RESERVESPONSOR_UNIT)
        locationid = o.post.integer("location")
        unit = o.post["unit"]
        sponsor = o.post["sponsor"]
        reserved = o.post["reserved"]
        asm3.audit.edit(o.dbo, o.user, "configuration", 0, "", f"update unit: locationid={locationid}, unit={unit}, sponsor={sponsor}, reserved={reserved}")
        return asm3.configuration.unit_extra_edit(o.dbo, locationid, unit, sponsor, reserved)

    def post_movelocation(self, o):
        self.check(asm3.users.CHANGE_ANIMAL)
        asm3.animal.update_location_unit(o.dbo, o.user, o.post.integer("animalid"), o.post.integer("locationid"))

    def post_moveunit(self, o):
        self.check(asm3.users.CHANGE_ANIMAL)
        asm3.animal.update_location_unit(o.dbo, o.user, o.post.integer("animalid"), o.post.integer("locationid"), o.post["unit"])

    def post_movefoster(self, o):
        self.check(asm3.users.ADD_MOVEMENT)
        post = o.post
        post.data["person"] = post["personid"]
        post.data["animal"] = post["animalid"]
        post.data["fosterdate"] = python2display(o.locale, now(o.dbo.timezone))
        return asm3.movement.insert_foster_from_form(o.dbo, o.user, post)
    
class smcom_my(ASMEndpoint):
    url = "smcom_my"

    def content(self, o):
        if o.session.superuser == 1: asm3.smcom.go_smcom_my(o.dbo)

class sql(JSONEndpoint):
    url = "sql"
    get_permissions = asm3.users.USE_SQL_INTERFACE
    post_permissions = asm3.users.USE_SQL_INTERFACE

    def controller(self, o):
        asm3.al.debug("%s opened SQL interface" % o.user, "main.sql", o.dbo)
        return {}

    def post_exec(self, o):
        sql = o.post["sql"].strip()
        return self.exec_sql(o.dbo, o.user, sql)

    def post_execfile(self, o):
        sql = asm3.utils.bytes2str(o.post.filedata())
        self.content_type("text/plain")
        return self.exec_sql_from_file(o.dbo, o.user, sql)

    def check_update_query(self, q):
        """ Prevent updates or deletes to certain tables or columns to prevent
            more savvy malicious users tampering via SQL Interface.
            q is already stripped and converted to lower case by the exec_sql caller.
            If one of our tamper proofed tables is touched, an Exception is raised
            and the query not run.
            This will also throw an error if we have an update or delete query
            without a where clause to prevent people doing something daft
            (easy to get around with WHERE 1=1 or something)
        """
        for t in ( "audittrail", "deletion", "signaturehash" ):
            if q.find(t) != -1:
                raise Exception("Forbidden: %s" % q)
        if q.find("where") == -1 and (q.startswith("delete") or q.startswith("update")):
            raise Exception("Forbidden: DELETE or UPDATE")

    def exec_sql(self, dbo, user, sql):
        l = dbo.locale
        rowsaffected = 0
        try:
            for q in dbo.split_queries(sql):
                if q == "": continue
                q = self.substitute_report_tokens(dbo, user, q)
                ql = q.lower()
                asm3.al.info("%s query: %s" % (user, q), "main.sql", dbo)
                if ql.startswith("select") or ql.startswith("show") or ql.startswith("with"):
                    return asm3.html.table(dbo.query(q))
                elif ql.startswith("insert"):
                    rowsaffected += dbo.execute(q)
                else:
                    self.check_update_query(ql)
                    rowsaffected += dbo.execute(q)
            asm3.configuration.db_view_seq_version(dbo, "0")
            return _("{0} rows affected.", l).format(rowsaffected)
        except Exception as err:
            asm3.al.error("%s" % str(err), "main.sql", dbo)
            raise asm3.utils.ASMValidationError(str(err))

    def exec_sql_from_file(self, dbo, user, sql):
        l = dbo.locale
        output = []
        for q in dbo.split_queries(sql):
            try:
                if q == "": continue
                q = self.substitute_report_tokens(dbo, user, q)
                ql = q.lower()
                asm3.al.info("%s query: %s" % (user, q), "main.sql", dbo)
                if ql.startswith("select") or ql.startswith("show") or ql.startswith("with"):
                    output.append(str(dbo.query(q)))
                else:
                    # self.check_update_query(ql)
                    rowsaffected = dbo.execute(q)
                    output.append(_("{0} rows affected.", l).format(rowsaffected))
            except Exception as err:
                asm3.al.error("%s" % str(err), "main.sql", dbo)
                output.append("ERROR: %s" % str(err))
        asm3.configuration.db_view_seq_version(dbo, "0")
        return "\n\n".join(output)

    def substitute_report_tokens(self, dbo, user, q):
        """ Substitutes any of our report tokens that might be in query q """
        # Substitute CURRENT_DATE-X tokens
        for day in asm3.utils.regex_multi(r"\$CURRENT_DATE\-(.+?)\$", q):
            d = dbo.today(offset=asm3.utils.cint(day)*-1)
            q = q.replace("$CURRENT_DATE-%s$" % day, dbo.sql_date(d, includeTime=False, wrapParens=False))
        # Substitute CURRENT_DATE+X tokens
        for day in asm3.utils.regex_multi(r"\$CURRENT_DATE\+(.+?)\$", q):
            d = dbo.today(offset=asm3.utils.cint(day))
            q = q.replace("$CURRENT_DATE+%s$" % day, dbo.sql_date(d, includeTime=False, wrapParens=False))
        # straight tokens
        q = q.replace("$CURRENT_DATE$", dbo.sql_date(dbo.now(), includeTime=False, wrapParens=False))
        q = q.replace("$CURRENT_DATE_TIME$", dbo.sql_date(dbo.now(), includeTime=True, wrapParens=False))
        q = q.replace("$CURRENT_DATE_FDM$", dbo.sql_date(asm3.i18n.first_of_month(dbo.now()), includeTime=False, wrapParens=False))
        q = q.replace("$CURRENT_DATE_LDM$", dbo.sql_date(asm3.i18n.last_of_month(dbo.now()), includeTime=False, wrapParens=False))
        q = q.replace("$CURRENT_DATE_FDY$", dbo.sql_date(asm3.i18n.first_of_year(dbo.now()), includeTime=False, wrapParens=False))
        q = q.replace("$CURRENT_DATE_LDY$", dbo.sql_date(asm3.i18n.last_of_year(dbo.now()), includeTime=False, wrapParens=False))
        q = q.replace("$USER$", user)
        q = q.replace("$DATABASENAME$", dbo.name())
        return q

class sql_dump(ASMEndpoint):
    url = "sql_dump"
    get_permissions = asm3.users.USE_SQL_INTERFACE

    def content(self, o):
        l = o.locale
        dbo = o.dbo
        mode = o.post["mode"]
        self.content_type("text/plain")
        if mode == "dumpsql":
            asm3.al.info("%s executed SQL database dump" % o.user, "main.sql", dbo)
            self.content_disposition("attachment", "dump.sql")
            return asm3.dbupdate.dump(dbo) # generator
        if mode == "dumpsqlmedia":
            asm3.al.info("%s executed SQL database dump (base64/media)" % o.user, "main.sql", dbo)
            self.content_disposition("attachment", "media.sql")
            return asm3.dbupdate.dump_dbfs_base64(dbo) # generator
        if mode == "dumpddlmysql":
            asm3.al.info("%s executed DDL dump MySQL" % o.user, "main.sql", dbo)
            self.content_disposition("attachment", "ddl_mysql.sql")
            dbo2 = asm3.db.get_dbo("MYSQL")
            dbo2.locale = dbo.locale
            return asm3.dbupdate.sql_structure(dbo2)
            return asm3.dbupdate.sql_default_data(dbo2).replace("|=", ";")
        if mode == "dumpddlpostgres":
            asm3.al.info("%s executed DDL dump PostgreSQL" % o.user, "main.sql", dbo)
            self.content_disposition("attachment", "ddl_postgresql.sql")
            dbo2 = asm3.db.get_dbo("POSTGRESQL")
            dbo2.locale = dbo.locale
            return asm3.dbupdate.sql_structure(dbo2)
            return asm3.dbupdate.sql_default_data(dbo2).replace("|=", ";")
        if mode == "dumpddldb2":
            asm3.al.info("%s executed DDL dump DB2" % o.user, "main.sql", dbo)
            self.content_disposition("attachment", "ddl_db2.sql")
            dbo2 = asm3.db.get_dbo("DB2")
            dbo2.locale = dbo.locale
            return asm3.dbupdate.sql_structure(dbo2)
            return asm3.dbupdate.sql_default_data(dbo2).replace("|=", ";")
        elif mode == "dumpsqlasm2":
            # ASM2_COMPATIBILITY
            asm3.al.info("%s executed SQL database dump (ASM2 HSQLDB)" % o.user, "main.sql", dbo)
            self.content_disposition("attachment", "asm2.sql")
            return asm3.dbupdate.dump_hsqldb(dbo) # generator
        elif mode == "dumpsqlasm2nomedia":
            # ASM2_COMPATIBILITY
            asm3.al.info("%s executed SQL database dump (ASM2 HSQLDB, without media)" % o.user, "main.sql", dbo)
            self.content_disposition("attachment", "asm2.sql")
            return asm3.dbupdate.dump_hsqldb(dbo, includeDBFS = False) # generator
        elif mode == "animalcsv":
            asm3.al.debug("%s executed CSV animal dump" % o.user, "main.sql", dbo)
            self.content_disposition("attachment", "animal.csv")
            rows = asm3.animal.get_animal_find_advanced(dbo, { "logicallocation" : "all", "filter" : "includedeceased,includenonshelter" })
            asm3.additional.append_to_results(dbo, rows, "animal")
            return asm3.utils.csv_generator(l, rows)
        elif mode == "mediacsv":
            asm3.al.debug("%s executed CSV media dump" % o.user, "main.sql", dbo)
            self.content_disposition("attachment", "media.csv")
            return asm3.utils.csv_generator(l, asm3.media.get_media_export(dbo))
        elif mode == "medicalcsv":
            asm3.al.debug("%s executed CSV medical dump" % o.user, "main.sql", dbo)
            self.content_disposition("attachment", "medical.csv")
            return asm3.utils.csv_generator(l, asm3.medical.get_medical_export(dbo))
        elif mode == "personcsv":
            asm3.al.debug("%s executed CSV person dump" % o.user, "main.sql", dbo)
            self.content_disposition("attachment", "person.csv")
            rows = asm3.person.get_person_find_simple(dbo, "", o.user, includeStaff=True, includeVolunteers=True)
            asm3.additional.append_to_results(dbo, rows, "person")
            return asm3.utils.csv_generator(l, rows)
        elif mode == "incidentcsv":
            asm3.al.debug("%s executed CSV incident dump" % o.user, "main.sql", dbo)
            self.content_disposition("attachment", "incident.csv")
            rows = asm3.animalcontrol.get_animalcontrol_find_advanced(dbo, { "filter" : "" }, o.user)
            asm3.additional.append_to_results(dbo, rows, "incident")
            return asm3.utils.csv_generator(l, rows)
        elif mode == "licencecsv":
            asm3.al.debug("%s executed CSV licence dump" % o.user, "main.sql", dbo)
            self.content_disposition("attachment", "licence.csv")
            return asm3.utils.csv_generator(l, asm3.financial.get_licence_find_simple(dbo, ""))
        elif mode == "paymentcsv":
            asm3.al.debug("%s executed CSV payment dump" % o.user, "main.sql", dbo)
            self.content_disposition("attachment", "payment.csv")
            return asm3.utils.csv_generator(l, asm3.financial.get_donations(dbo, "m10000"))

class staff_rota(JSONEndpoint):
    url = "staff_rota"
    get_permissions = asm3.users.VIEW_STAFF_ROTA

    def controller(self, o):
        dbo = o.dbo
        startdate = o.post.date("start")
        if startdate is None: startdate = monday_of_week(dbo.today())
        rota = asm3.person.get_rota(dbo, startdate, add_days(startdate, 7))
        asm3.al.debug("got %d rota items" % len(rota), "main.staff_rota", dbo)
        return {
            "name": "staff_rota",
            "rows": rota,
            "flags": asm3.lookups.get_person_flags(dbo),
            "flagsel": o.post["flags"],
            "startdate": startdate,
            "prevdate": subtract_days(startdate, 7),
            "nextdate": add_days(startdate, 7),
            "rotatypes": asm3.lookups.get_rota_types(dbo),
            "worktypes": asm3.lookups.get_work_types(dbo),
            "staff": asm3.person.get_staff_volunteers(dbo, o.siteid)
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_ROTA)
        return asm3.person.insert_rota_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_ROTA)
        asm3.person.update_rota_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_ROTA)
        for rid in o.post.integer_list("ids"):
            asm3.person.delete_rota(o.dbo, o.user, rid)

    def post_deleteweek(self, o):
        self.check(asm3.users.DELETE_ROTA)
        asm3.person.delete_rota_week(o.dbo, o.user, o.post.date("startdate"))

    def post_clone(self, o):
        self.check(asm3.users.ADD_ROTA)
        startdate = o.post.date("startdate")
        newdate = o.post.date("newdate")
        flags = o.post["flags"]
        asm3.person.clone_rota_week(o.dbo, o.user, startdate, newdate, flags)

class stock_level(JSONEndpoint):
    url = "stock_level"
    get_permissions = asm3.users.VIEW_STOCKLEVEL

    def controller(self, o):
        dbo = o.dbo
        if o.post.integer("viewlocation") == -1:
            levels = asm3.stock.get_stocklevels_depleted(dbo)
        elif o.post.integer("viewlocation") == -2:
            levels = asm3.stock.get_stocklevels_lowbalance(dbo)
        else:
            levels = asm3.stock.get_stocklevels(dbo, o.post.integer("viewlocation"))
        asm3.al.debug("got %d stock levels" % len(levels), "main.stock_level", dbo)
        return {
            "stocklocations": asm3.lookups.get_stock_locations(dbo),
            "stocknames": "|".join(asm3.stock.get_stock_names(dbo)),
            "stockusagetypes": asm3.lookups.get_stock_usage_types(dbo),
            "stockunits": "|".join(asm3.stock.get_stock_units(dbo)),
            "newlevel": o.post.integer("newlevel") == 1,
            "sortexp": o.post.integer("sortexp") == 1,
            "products": asm3.stock.get_products(dbo),
            "rows": levels
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_STOCKLEVEL)
        for dummy in range(0, o.post.integer("quantity")):
            asm3.stock.insert_stocklevel_from_form(o.dbo, o.post, o.user)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_STOCKLEVEL)
        asm3.stock.update_stocklevel_from_form(o.dbo, o.post, o.user)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_STOCKLEVEL)
        for sid in o.post.integer_list("ids"):
            asm3.stock.delete_stocklevel(o.dbo, o.user, sid)

    def post_lastname(self, o):
        self.check(asm3.users.VIEW_STOCKLEVEL)
        return asm3.stock.get_last_stock_with_name(o.dbo, o.post["name"])

class stock_usage(JSONEndpoint):
    url = "stock_usage"
    js_module = "stock_usage"
    get_permissions = asm3.users.VIEW_STOCKLEVEL

    def controller(self, o):
        dbo = o.dbo
        productid = 0
        stocklevelid = 0
        productname = ""
        stocklevelname = ""
        if o.post["offset"]:
            offset = o.post.integer("offset") * -1
            fromdate = dbo.today(offset=offset)
        else:
            offset = 0
            fromdate = dbo.today()
        if o.post["stocklevelid"]:
            stocklevelid = o.post.integer("stocklevelid")
            stocklevelname = asm3.stock.get_stocklevel(dbo, stocklevelid)["NAME"]
        if o.post["productid"]:
            productid = o.post.integer("productid")
            productname = asm3.stock.get_product_name(dbo, productid)
        return {
            "productid": productid,
            "stocklevelid": stocklevelid,
            "productname": productname,
            "stocklevelname": stocklevelname,
            "rows": asm3.stock.get_stock_usage(dbo, productid, stocklevelid, fromdate)
        }

class systemusers(JSONEndpoint):
    url = "systemusers"
    js_module = "users"
    get_permissions = asm3.users.EDIT_USER

    def controller(self, o):
        dbo = o.dbo
        user = asm3.users.get_users(dbo)
        roles = asm3.users.get_roles(dbo)
        asm3.al.debug("editing %d system users" % len(user), "main.systemusers", dbo)
        return {
            "rows": user,
            "roles": roles,
            "internallocations": asm3.lookups.get_internal_locations(dbo),
            "sites": asm3.lookups.get_sites(dbo)
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_USER)
        return asm3.users.insert_user_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.EDIT_USER)
        asm3.users.update_user_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.EDIT_USER)
        for uid in o.post.integer_list("ids"):
            asm3.users.delete_user(o.dbo, o.user, uid)

    def post_reset(self, o):
        self.check(asm3.users.EDIT_USER)
        for uid in o.post.integer_list("ids"):
            asm3.users.reset_password(o.dbo, uid, o.post["password"])

class task(JSONEndpoint):
    url = "task"

    def controller(self, o):
        return { }
   
    def post_poll(self, o):
        return "%s|%d|%s|%s" % (asm3.asynctask.get_task_name(o.dbo), asm3.asynctask.get_progress_percent(o.dbo), asm3.asynctask.get_last_error(o.dbo), asm3.asynctask.get_return_value(o.dbo))

    def post_stop(self, o):
        asm3.asynctask.set_cancel(o.dbo, True)

class test(JSONEndpoint):
    url = "test"
    get_permissions = asm3.users.VIEW_TEST

    def controller(self, o):
        dbo = o.dbo
        offset = o.post["offset"]
        if offset == "": offset = "m365"
        test = asm3.medical.get_tests_outstanding(dbo, offset, o.lf)
        asm3.al.debug("got %d tests" % len(test), "main.test", dbo)
        return {
            "name": "test",
            "newtest": o.post.integer("newtest") == 1,
            "rows": test,
            "stockitems": asm3.stock.get_stock_items(dbo),
            "stockusagetypes": asm3.lookups.get_stock_usage_types(dbo),
            "testtypes": asm3.lookups.get_test_types(dbo),
            "testresults": asm3.lookups.get_test_results(dbo)
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_TEST)
        return asm3.medical.insert_test_from_form(o.dbo, o.user, o.post)

    def post_createbulk(self, o):
        self.check(asm3.users.ADD_TEST)
        for animalid in o.post.integer_list("animals"):
            o.post.data["animal"] = str(animalid)
            asm3.medical.insert_test_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_TEST)
        asm3.medical.update_test_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_TEST)
        for vid in o.post.integer_list("ids"):
            asm3.medical.delete_test(o.dbo, o.user, vid)

    def post_perform(self, o):
        self.check(asm3.users.CHANGE_TEST)
        newdate = o.post.date("newdate")
        retestdate = o.post.date("retestdate")
        reschedulecomments = o.post["usagecomments"]
        cost = o.post.integer("givencost")
        vet = o.post.integer("givenvet")
        testresult = o.post.integer("testresult")
        for vid in o.post.integer_list("ids"):
            asm3.medical.complete_test(o.dbo, o.user, vid, newdate, testresult, vet, cost)
            if retestdate is not None:
                asm3.medical.reschedule_test(o.dbo, o.user, vid, retestdate, reschedulecomments)
        if o.post.integer("item") != -1:
            asm3.stock.deduct_stocklevel_from_form(o.dbo, o.user, o.post)

class timeline(JSONEndpoint):
    url = "timeline"
    get_permissions = asm3.users.VIEW_TIMELINE

    def controller(self, o):
        dbo = o.dbo
        evts = asm3.animal.get_timeline(dbo, 500)
        asm3.al.debug("timeline events, run by %s, got %d events" % (o.user, len(evts)), "main.timeline", dbo)
        return {
            "recent": evts,
            "resultcount": len(evts)
        }

class transport(JSONEndpoint):
    url = "transport"
    get_permissions = asm3.users.VIEW_TRANSPORT

    def controller(self, o):
        dbo = o.dbo
        transports = asm3.movement.get_active_transports(dbo)
        asm3.al.debug("got %d transports" % len(transports), "main.transport", dbo)
        return {
            "name": "transport",
            "statuses": asm3.lookups.get_transport_statuses(dbo),
            "templates": asm3.template.get_document_templates(dbo, "transport"),
            "transporttypes": asm3.lookups.get_transport_types(dbo),
            "rows": transports
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_TRANSPORT)
        return asm3.movement.insert_transport_from_form(o.dbo, o.user, o.post)

    def post_createbulk(self, o):
        self.check(asm3.users.ADD_TRANSPORT)
        for animalid in o.post.integer_list("animals"):
            o.post.data["animal"] = str(animalid)
            asm3.movement.insert_transport_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_TRANSPORT)
        asm3.movement.update_transport_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_TRANSPORT)
        for mid in o.post.integer_list("ids"):
            asm3.movement.delete_transport(o.dbo, o.user, mid)

    def post_setstatus(self, o):
        self.check(asm3.users.CHANGE_TRANSPORT)
        asm3.movement.update_transport_statuses(o.dbo, o.user, o.post.integer_list("ids"), o.post.integer("newstatus"))

class traploan(JSONEndpoint):
    url = "traploan"
    get_permissions = asm3.users.VIEW_TRAPLOAN

    def controller(self, o):
        dbo = o.dbo
        traploans = []
        offset = o.post["offset"]
        if offset == "" or offset == "a":
            traploans = asm3.animalcontrol.get_active_traploans(dbo)
        else:
            traploans = asm3.animalcontrol.get_returned_traploans(dbo, offset)
        asm3.al.debug("got %d trap loans" % len(traploans), "main.traploan", dbo)
        return {
            "name": "traploan",
            "rows": traploans,
            "traptypes": asm3.lookups.get_trap_types(dbo)
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_TRAPLOAN)
        return asm3.animalcontrol.insert_traploan_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_TRAPLOAN)
        asm3.animalcontrol.update_traploan_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_TRAPLOAN)
        for lid in o.post.integer_list("ids"):
            asm3.animalcontrol.delete_traploan(o.dbo, o.user, lid)

class vaccination(JSONEndpoint):
    url = "vaccination"
    get_permissions = asm3.users.VIEW_VACCINATION

    def controller(self, o):
        dbo = o.dbo
        offset = o.post["offset"]
        if offset == "": offset = "m365"
        vacc = asm3.medical.get_vaccinations_outstanding(dbo, offset, o.lf)
        asm3.al.debug("got %d vaccinations" % len(vacc), "main.vaccination", dbo)
        return {
            "name": "vaccination",
            "newvacc": o.post.integer("newvacc") == 1,
            "rows": vacc,
            "batches": asm3.medical.get_batch_for_vaccination_types(dbo),
            "manufacturers": "|".join(asm3.medical.get_vacc_manufacturers(dbo)),
            "stockitems": asm3.stock.get_stock_items(dbo),
            "stockusagetypes": asm3.lookups.get_stock_usage_types(dbo),
            "users": asm3.users.get_users(dbo),
            "vaccinationtypes": asm3.lookups.get_vaccination_types(dbo)
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_VACCINATION)
        return asm3.medical.insert_vaccination_from_form(o.dbo, o.user, o.post)

    def post_createbulk(self, o):
        self.check(asm3.users.ADD_VACCINATION)
        for animalid in o.post.integer_list("animals"):
            o.post.data["animal"] = str(animalid)
            asm3.medical.insert_vaccination_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_VACCINATION)
        asm3.medical.update_vaccination_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_VACCINATION)
        for vid in o.post.integer_list("ids"):
            asm3.medical.delete_vaccination(o.dbo, o.user, vid)

    def post_given(self, o):
        self.check(asm3.users.BULK_COMPLETE_VACCINATION)
        post = o.post
        newdate = post.date("givennewdate")
        rescheduledate = post.date("rescheduledate")
        reschedulecomments = post["reschedulecomments"]
        givenexpires = post.date("givenexpires")
        givenbatch = post["givenbatch"]
        givencost = post.integer("givencost")
        givenmanufacturer = post["givenmanufacturer"]
        givenby = post["givenby"]
        givenrabiestag = post["givenrabiestag"]
        vet = post.integer("givenvet")
        for vid in post.integer_list("ids"):
            asm3.medical.complete_vaccination(o.dbo, o.user, vid, newdate, givenby, vet, givenexpires, givenbatch, givenmanufacturer, givencost, givenrabiestag)
            if rescheduledate is not None:
                asm3.medical.reschedule_vaccination(o.dbo, o.user, vid, rescheduledate, reschedulecomments)
        if post.integer("item") != -1:
            asm3.stock.deduct_stocklevel_from_form(o.dbo, o.user, post)

    def post_required(self, o):
        self.check(asm3.users.BULK_COMPLETE_VACCINATION)
        newdate = o.post.date("newdate")
        for vid in o.post.integer_list("ids"):
            asm3.medical.update_vaccination_required(o.dbo, o.user, vid, newdate)

class voucher(JSONEndpoint):
    url = "voucher"
    js_module = "vouchers"
    get_permissions = asm3.users.VIEW_VOUCHER

    def controller(self, o):
        dbo = o.dbo
        offset = o.post["offset"]
        if offset == "": offset = "i31"
        vouchers = asm3.financial.get_vouchers(dbo, offset)
        asm3.al.debug("got %d vouchers for %s" % (len(vouchers), offset), "main.person_vouchers", dbo)
        return {
            "name": "voucher",
            "rows": vouchers,
            "templates": asm3.template.get_document_templates(dbo, "voucher"),
            "vouchertypes": asm3.lookups.get_voucher_types(dbo)
        }

    def post_create(self, o):
        self.check(asm3.users.ADD_VOUCHER)
        return asm3.financial.insert_voucher_from_form(o.dbo, o.user, o.post)

    def post_update(self, o):
        self.check(asm3.users.CHANGE_VOUCHER)
        asm3.financial.update_voucher_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_VOUCHER)
        for vid in o.post.integer_list("ids"):
            asm3.financial.delete_voucher(o.dbo, o.user, vid)

class waitinglist(JSONEndpoint):
    url = "waitinglist"
    get_permissions = asm3.users.VIEW_WAITING_LIST

    def controller(self, o):
        dbo = o.dbo
        a = asm3.waitinglist.get_waitinglist_by_id(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        recname = "%s %s" % (a.OWNERNAME, a.SPECIESNAME)
        if asm3.configuration.audit_on_view_record(dbo): asm3.audit.view_record(dbo, o.user, "animalwaitinglist", a["ID"], recname)
        asm3.al.debug("opened waiting list %s" % recname, "main.waitinglist", dbo)
        return {
            "animal": a,
            "additional": asm3.additional.get_additional_fields(dbo, a["ID"], "waitinglist"),
            "audit": self.checkb(asm3.users.VIEW_AUDIT_TRAIL) and asm3.audit.get_audit_for_link(dbo, "animalwaitinglist", a["ID"]) or [],
            "breeds": asm3.lookups.get_breeds_by_species(dbo),
            "logtypes": asm3.lookups.get_log_types(dbo),
            "sexes": asm3.lookups.get_sexes(dbo),
            "sizes": asm3.lookups.get_sizes(dbo),
            "species": asm3.lookups.get_species(dbo),
            "urgencies": asm3.lookups.get_urgencies(dbo),
            "templates": asm3.template.get_document_templates(dbo, "waitinglist"),
            "templatesemail": asm3.template.get_document_templates(dbo, "email"),
            "tabcounts": asm3.waitinglist.get_satellite_counts(dbo, a["ID"])[0],
            "waitinglistremovals": asm3.lookups.get_waitinglist_removals(dbo)
        }

    def post_save(self, o):
        self.check(asm3.users.CHANGE_WAITING_LIST)
        asm3.waitinglist.update_waitinglist_from_form(o.dbo, o.post, o.user)
    
    def post_clone(self, o):
        self.check(asm3.users.ADD_WAITING_LIST)
        nid = asm3.waitinglist.clone_waitinglist(o.dbo, o.user, o.post.integer("waitinglistid"))
        return str(nid)

    def post_email(self, o):
        self.check(asm3.users.EMAIL_PERSON)
        asm3.waitinglist.send_email_from_form(o.dbo, o.user, o.post)

    def post_delete(self, o):
        self.check(asm3.users.DELETE_WAITING_LIST)
        asm3.waitinglist.delete_waitinglist(o.dbo, o.user, o.post.integer("id"))

    def post_toanimal(self, o):
        self.check(asm3.users.ADD_ANIMAL)
        return str(asm3.waitinglist.create_animal(o.dbo, o.user, o.post.integer("id")))

class waitinglist_diary(JSONEndpoint):
    url = "waitinglist_diary"
    js_module = "diary"
    get_permissions = asm3.users.VIEW_DIARY

    def controller(self, o):
        dbo = o.dbo
        a = asm3.waitinglist.get_waitinglist_by_id(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        diaries = asm3.diary.get_diaries(dbo, asm3.diary.WAITINGLIST, o.post.integer("id"))
        asm3.al.debug("got %d diaries" % len(diaries), "main.waitinglist_diary", dbo)
        return {
            "rows": diaries,
            "animal": a,
            "tabcounts": asm3.waitinglist.get_satellite_counts(dbo, a["WLID"])[0],
            "name": "waitinglist_diary",
            "linkid": a["WLID"],
            "linktypeid": asm3.diary.WAITINGLIST,
            "forlist": asm3.users.get_diary_forlist(dbo)
        }

class waitinglist_log(JSONEndpoint):
    url = "waitinglist_log"
    js_module = "log"
    get_permissions = asm3.users.VIEW_LOG

    def controller(self, o):
        dbo = o.dbo
        logfilter = o.post.integer("filter")
        if logfilter == 0: logfilter = asm3.configuration.default_log_filter(dbo)
        a = asm3.waitinglist.get_waitinglist_by_id(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        logs = asm3.log.get_logs(dbo, asm3.log.WAITINGLIST, o.post.integer("id"), logfilter)
        asm3.al.debug("got %d logs" % len(logs), "main.waitinglist_diary", dbo)
        return {
            "name": "waitinglist_log",
            "linkid": o.post.integer("id"),
            "linktypeid": asm3.log.WAITINGLIST,
            "filter": logfilter,
            "rows": logs,
            "animal": a,
            "tabcounts": asm3.waitinglist.get_satellite_counts(dbo, a["WLID"])[0],
            "logtypes": asm3.lookups.get_log_types(dbo)
        }

class waitinglist_media(JSONEndpoint):
    url = "waitinglist_media"
    js_module = "media"
    get_permissions = asm3.users.VIEW_MEDIA

    def controller(self, o):
        dbo = o.dbo
        a = asm3.waitinglist.get_waitinglist_by_id(dbo, o.post.integer("id"))
        if a is None: self.notfound()
        m = asm3.media.get_media(dbo, asm3.media.WAITINGLIST, o.post.integer("id"))
        asm3.al.debug("got %d media" % len(m), "main.waitinglist_media", dbo)
        return {
            "media": m,
            "animal": a,
            "tabcounts": asm3.waitinglist.get_satellite_counts(dbo, a["WLID"])[0],
            "showpreferred": True,
            "canwatermark": False,
            "documentrepository": asm3.dbfs.get_document_repository(o.dbo),
            "linkid": o.post.integer("id"),
            "linktypeid": asm3.media.WAITINGLIST,
            "logtypes": asm3.lookups.get_log_types(dbo),
            "name": self.url,
            "flags": asm3.lookups.get_media_flags(dbo),
            "resizeimagespec": asm3.utils.iif(RESIZE_IMAGES_DURING_ATTACH, RESIZE_IMAGES_SPEC, ""),
            "templates": asm3.template.get_document_templates(dbo, "email"),
            "sigtype": ELECTRONIC_SIGNATURES
        }

class waitinglist_new(JSONEndpoint):
    url = "waitinglist_new"
    get_permissions = asm3.users.ADD_WAITING_LIST
    post_permissions = asm3.users.ADD_WAITING_LIST

    def controller(self, o):
        dbo = o.dbo
        return {
            "additional": asm3.additional.get_additional_fields(dbo, 0, "waitinglist"),
            "breeds": asm3.lookups.get_breeds_by_species(dbo),
            "sexes": asm3.lookups.get_sexes(dbo),
            "species": asm3.lookups.get_species(dbo),
            "sizes": asm3.lookups.get_sizes(dbo),
            "urgencies": asm3.lookups.get_urgencies(dbo),
            "waitinglistremovals": asm3.lookups.get_waitinglist_removals(dbo),
        }

    def post_all(self, o):
        return str(asm3.waitinglist.insert_waitinglist_from_form(o.dbo, o.post, o.user))

class waitinglist_results(JSONEndpoint):
    url = "waitinglist_results"
    get_permissions = asm3.users.VIEW_WAITING_LIST

    def controller(self, o):
        dbo = o.dbo
        post = o.post
        priorityfloor = asm3.utils.iif(post["priorityfloor"] == "", dbo.query_int("SELECT MAX(ID) FROM lkurgency"), post.integer("priorityfloor"))
        speciesfilter = asm3.utils.iif(post["species"] == "", -1, post.integer("species"))
        sizefilter = asm3.utils.iif(post["size"] == "", -1, post.integer("size"))
        rows = asm3.waitinglist.get_waitinglist(dbo, priorityfloor, speciesfilter, sizefilter,
            post["addresscontains"], post.integer("includeremoved"), post["namecontains"], post["descriptioncontains"])
        add = None
        if len(rows) > 0: 
            add = asm3.additional.get_additional_fields_ids(dbo, rows, "waitinglist")
        asm3.al.debug("found %d results" % (len(rows)), "main.waitinglist_results", dbo)
        return {
            "rows": rows,
            "additional": add, 
            "seladdresscontains": post["addresscontains"],
            "seldescriptioncontains": post["descriptioncontains"],
            "selincluderemoved": post.integer("includeremoved"),
            "selnamecontains": post["namecontains"],
            "selpriorityfloor": priorityfloor,
            "selspecies": speciesfilter,
            "selsize": sizefilter,
            "species": asm3.lookups.get_species(dbo),
            "sizes": asm3.lookups.get_sizes(dbo),
            "urgencies": asm3.lookups.get_urgencies(dbo),
            "yesno": asm3.lookups.get_yesno(dbo)
        }

    def post_delete(self, o):
        self.check(asm3.users.DELETE_WAITING_LIST)
        for wid in o.post.integer_list("ids"):
            asm3.waitinglist.delete_waitinglist(o.dbo, o.user, wid)

    def post_complete(self, o):
        self.check(asm3.users.CHANGE_WAITING_LIST)
        for wid in o.post.integer_list("ids"):
            asm3.waitinglist.update_waitinglist_remove(o.dbo, o.user, wid)

    def post_highlight(self, o):
        self.check(asm3.users.CHANGE_WAITING_LIST)
        for wid in o.post.integer_list("ids"):
            asm3.waitinglist.update_waitinglist_highlight(o.dbo, wid, o.post["himode"])

# List of routes constructed from class definitions
routes = []

# Setup the WSGI application object and session with mappings
app = web.application(generate_routes(), globals(), autoreload=AUTORELOAD)
app.notfound = asm_404
app.internalerror = asm_500
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

