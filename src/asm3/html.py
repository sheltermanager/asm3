
import asm3.additional
import asm3.animal
import asm3.configuration
import asm3.financial
import asm3.lookups
import asm3.medical
import asm3.person
import asm3.users
import asm3.utils

from asm3.i18n import BUILD, _, translate, format_currency, get_locales, now, python2unix, real_locale
from asm3.sitedefs import QR_IMG_SRC
from asm3.sitedefs import BASE_URL, LOCALE, ROLLUP_JS, SERVICE_URL
from asm3.sitedefs import ASMSELECT_CSS, ASMSELECT_JS, BASE64_JS, BOOTSTRAP_JS, BOOTSTRAP_CSS, BOOTSTRAP_GRID_CSS, BOOTSTRAP_ICONS_CSS, CODEMIRROR_CSS, CODEMIRROR_JS, CODEMIRROR_BASE, FLOT_JS, FLOT_PIE_JS, FULLCALENDAR_JS, FULLCALENDAR_CSS, HTMLFTP_PUBLISHER_ENABLED, JQUERY_JS, JQUERY_UI_JS, JQUERY_UI_CSS, MOMENT_JS, MOUSETRAP_JS, PATH_JS, QRCODE_JS, SIGNATURE_JS, TABLESORTER_CSS, TABLESORTER_JS, TABLESORTER_WIDGETS_JS, TIMEPICKER_CSS, TIMEPICKER_JS, TINYMCE_5_JS

import os

def css_tag(uri, idattr="", addbuild=False):
    """
    Returns a css link tag to a resource.
    """
    if idattr != "": idattr = "id=\"%s\"" % idattr
    buildqs = asm3.utils.iif(addbuild, "?b=%s" % BUILD, "")
    return f"<link rel=\"stylesheet\" type=\"text/css\" href=\"{uri}{buildqs}\" {idattr} />\n"

def asm_css_tag(filename):
    """
    Returns a path to one of our stylesheets
    """
    return css_tag(f"static/css/{filename}", addbuild=True)

def script_i18n(l):
    return f"<script type=\"text/javascript\" src=\"static/js/locales/locale_{real_locale(l)}.js?b={BUILD}\"></script>\n"

def script_tag(uri, idattr="", addbuild=False):
    """
    Returns a script tag to a resource.
    """
    if idattr != "": idattr = "id=\"%s\"" % idattr
    buildqs = asm3.utils.iif(addbuild, "?b=%s" % BUILD, "")
    return f"<script type=\"text/javascript\" src=\"{uri}{buildqs}\" {idattr}></script>\n"

def asm_script_tag(filename):
    """
    Returns a path to one of our javascript files.
    If we're in rollup mode and one of our standalone files is requested,
    get it from the compat folder instead so it's still cross-browser compliant and minified.
    """
    standalone = [ "animal_view_adoptable.js", "document_edit.js", 
        "mobile.js", "mobile2.js", "mobile_login.js", "mobile_report.js", "mobile_sign.js", 
        "onlineform_extra.js", "report_toolbar.js", "service_sign_document.js", "service_checkout_adoption.js" ]
    if ROLLUP_JS and filename in standalone and filename.find("/") == -1: filename = f"compat/{filename}"
    return script_tag(f"static/js/{filename}", addbuild=True)

def asm_script_tags(path):
    """
    Returns separate script tags for all ASM javascript files.
    """
    jsfiles = [ "common.js", "common_validate.js", "common_html.js", "common_map.js", "common_widgets.js", "common_animalchooser.js",
        "common_animalchoosermulti.js", "common_personchooser.js", "common_tableform.js", "common_microchip.js", "header.js",
        "header_additional.js", "header_edit_header.js" ]
    standalone = [ "animal_view_adoptable.js", "document_edit.js", 
        "mobile.js", "mobile2.js", "mobile_login.js", "mobile_report.js", "mobile_sign.js", 
        "onlineform_extra.js", "report_toolbar.js", "service_sign_document.js", "service_checkout_adoption.js" ]
    # Read our available js files and append them to this list, not including ones
    # we've explicitly added above (since they are in correct load order)
    # or those we should exclude because they are standalone files
    for i in os.listdir(path + "static/js"):
        if i not in jsfiles and i not in standalone and not i.startswith(".") and i.endswith(".js"):
            jsfiles.append(i)
    buf = []
    for i in jsfiles:
        buf.append(asm_script_tag(i))
    return "".join(buf)

def xml(results):
    """
    Takes a list of dictionaries and converts them into
    an XML string. All values are treated as a strings
    and None values are turned into the string "null"
    """
    s = ""
    for row in results:
        cr = "    <row>\n"
        for k, v in row.items():
            if v is None:
                v = "null"
            v = str(v)
            v = v.replace("&", "&amp;")
            v = v.replace(">", "&gt;")
            v = v.replace("<", "&lt;")
            cr += "        <" + k.lower() + ">"
            cr += str(v)
            cr += "</" + k.lower() + ">\n"
        cr += "    </row>\n"
        s += cr
    return '<?xml version="1.0" standalone="yes" ?>\n<xml>\n' + s + '\n</xml>'

def table(results):
    """
    Takes a list of dictionaries and converts them into
    an HTML thead and tbody string.
    """
    if len(results) == 0: return ""
    s = "<thead>\n<tr>\n"
    cols = sorted(results[0].keys())
    for c in cols:
        s += "<th>%s</th>\n" % c
    s += "</thead>\n<tbody>\n"
    for row in results:
        s += "<tr>"
        for c in cols:
            s += "<td>%s</td>\n" % str(row[c])
        s += "</tr>"
    s += "</tbody>\n"
    return s

def bare_header(title, theme = "asm", locale = LOCALE, config_db = "asm", config_ts = "0"):
    """
    A bare header with just the script files needed for the program.
    title: The page title
    js: The name of an accompanying js file to load
    theme: A pre-rolled jquery-ui theme
    locale: The current system locale (used for requesting i18n.js)
    config_db: The name of the system database (used for requesting config.js)
    config_ts: A unique timestamp for when we last wanted the config (used for requesting config.js)
               This value changes when we update the config so the cache can be invalidated.
    """
    if config_db == "asm" and config_ts == "0":
        config_ts = python2unix(now())
    def script_config():
        return script_tag("config.js?db=%s&ts=%s" % (config_db, config_ts))
    def script_schema():
        return asm_script_tag("bundle/schema.js") # statically generated
    # Use the default if we have no locale
    if locale is None: locale = LOCALE
    # Load the asm scripts
    if ROLLUP_JS:
        asm_scripts = asm_script_tag("bundle/rollup_compat.min.js")
    else:
        asm_scripts = asm_script_tags(asm3.utils.PATH) 
    # Set the body colour from the theme and make sure the theme is a valid choice.
    themecode, themejq, themebg, themename = asm3.lookups.get_theme(theme)
    return '<!DOCTYPE html>\n' \
        '<html>\n' \
        '<head>\n' \
        '<title>%(title)s</title>\n' \
        '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n' \
        '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=2.0">\n' \
        '<link rel="shortcut icon" href="static/images/logo/icon-16.png" />\n' \
        '<link rel="icon" href="static/images/logo/icon-32.png" sizes="32x32"/>\n' \
        '<link rel="icon" href="static/images/logo/icon-48.png" sizes="48x48"/>\n' \
        '<link rel="icon" href="static/images/logo/icon-128.png" sizes="128x128"/>\n' \
        '%(scripts)s\n' \
        '</head>\n' \
        '<body style="background-color: %(bgcol)s">\n' \
        '<noscript>\n' \
        'Sorry. ASM will not work without Javascript.\n' \
        '</noscript>\n' % {
            "title": title, 
            "scripts": 
                css_tag(ASMSELECT_CSS) + 
                css_tag(CODEMIRROR_CSS) + 
                css_tag(CODEMIRROR_BASE + "addon/display/fullscreen.css") + 
                css_tag(CODEMIRROR_BASE + "addon/hint/show-hint.css") + 
                css_tag(FULLCALENDAR_CSS) +
                css_tag(TABLESORTER_CSS) + 
                css_tag(TIMEPICKER_CSS) + 
                css_tag(JQUERY_UI_CSS % { "theme": themejq}, idattr="jqt", addbuild=True) +
                css_tag(BOOTSTRAP_GRID_CSS) +
                asm_css_tag("asm-icon.css") +
                asm_css_tag("asm.css") + 
                script_tag("static/lib/modernizr/modernizr.min.js") + 
                script_tag(JQUERY_JS) +
                script_tag(JQUERY_UI_JS) +
                script_tag(MOMENT_JS) + 
                script_tag(MOUSETRAP_JS) + 
                script_tag(ASMSELECT_JS) + 
                script_tag(BASE64_JS) + 
                script_tag(QRCODE_JS) +
                script_tag(CODEMIRROR_JS) + 
                script_tag(CODEMIRROR_BASE + "addon/display/fullscreen.js") + 
                script_tag(CODEMIRROR_BASE + "addon/hint/show-hint.js") + 
                script_tag(CODEMIRROR_BASE + "addon/hint/sql-hint.js") + 
                script_tag(CODEMIRROR_BASE + "mode/javascript/javascript.js") + 
                script_tag(CODEMIRROR_BASE + "mode/xml/xml.js") + 
                script_tag(CODEMIRROR_BASE + "mode/htmlmixed/htmlmixed.js") + 
                script_tag(CODEMIRROR_BASE + "mode/sql/sql.js") + 
                script_tag(FULLCALENDAR_JS) + 
                script_tag(SIGNATURE_JS) +
                script_tag(TABLESORTER_JS) + 
                script_tag(TABLESORTER_WIDGETS_JS) + 
                script_tag(TIMEPICKER_JS) +
                script_tag(TINYMCE_5_JS) +
                script_tag(PATH_JS) + 
                script_config() + 
                script_i18n(locale) + 
                script_schema() + 
                asm_scripts,
            "bgcol": themebg }

def tinymce_header(title, js, jswindowprint = True, pdfenabled = True, visualaids = True, onlysavewhendirty = False, readonly = False):
    """
    Outputs a header for tinymce pages.
    js: The name of the script file to load.
    jswindowprint: If true, a hidden iframe with window.print is used for printing (tinymce's default behaviour)
                   If false, a postback is done to redirect to a page containing just the content
    visualaids:    If true, visual aids are on (show dotted lines round tables with no border)
    pdfenabled:    Whether the PDF button is available
    onlysavewhendirty: The save button only becomes active when a change is made
    readonly:      If true, does not allow editing, all toolbar buttons but print and pdf are available
    """
    return """<!DOCTYPE html>
        <html>
        <head>
        <title>%(title)s</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="shortcut icon" href="static/images/logo/icon-16.png">
        <link rel="icon" href="static/images/logo/icon-32.png" sizes="32x32">
        <link rel="icon" href="static/images/logo/icon-48.png" sizes="48x48">
        <link rel="icon" href="static/images/logo/icon-128.png" sizes="128x128">
        %(jquery)s
        %(css)s
        <script type="text/javascript">
        var baseurl = '%(baseurl)s';
        var buildno = '%(buildno)s';
        var jswindowprint = %(jswindowprint)s;
        var onlysavewhendirty = %(onlysavewhendirty)s;
        var pdfenabled = %(pdfenabled)s;
        var visualaids = %(visualaids)s;
        var readonly = %(readonly)s;
        </script>
        %(tinymce)s
        %(script)s
        </head>
        <body>
    """ % { "title": title,
           "jquery": script_tag(JQUERY_JS), 
           "tinymce": script_tag(TINYMCE_5_JS),
           "css": asm_css_tag("asm-tinymce.css"),
           "script": asm_script_tag(js),
           "baseurl": BASE_URL,
           "buildno": BUILD,
           "jswindowprint": jswindowprint and "true" or "false",
           "onlysavewhendirty": onlysavewhendirty and "true" or "false", 
           "pdfenabled": pdfenabled and "true" or "false",
           "visualaids": visualaids and "true" or "false",
           "readonly": readonly and "true" or "false"}

def tinymce_print_header(title):
    """
    Outputs a header for printable tinymce pages on mobile devices.
    """
    return """<!DOCTYPE html>
        <html>
        <head>
        <title>%(title)s</title>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <link rel="shortcut icon" href="static/images/logo/icon-16.png" />
        <link rel="icon" href="static/images/logo/icon-32.png" sizes="32x32">
        <link rel="icon" href="static/images/logo/icon-48.png" sizes="48x48">
        <link rel="icon" href="static/images/logo/icon-128.png" sizes="128x128">
        %(css)s
        </head>
        <body>
    """ % { "title": title,
           "css": asm_css_tag("asm-tinymce.css") }

def tinymce_main(locale, action, recid="", mediaid = "", linktype = "", redirecturl = "", dtid = "", content = ""):
    """ 
    Outputs the main body of a tinymce page.
    action: The post target for the controller
    template: The ID of the template to post back
    content: The content for the box
    """
    return """
        <form method="post" action="%(action)s">
        <input type="hidden" id="locale" value="%(locale)s" />
        <input type="hidden" name="dtid" value="%(dtid)s" />
        <input type="hidden" name="recid" value="%(recid)s" />
        <input type="hidden" name="mediaid" value="%(mediaid)s" />
        <input type="hidden" name="linktype" value="%(linktype)s" />
        <input type="hidden" name="redirecturl" value="%(redirecturl)s" />
        <input type="hidden" name="mode" value="save" />
        <div style="padding: 0; margin-left: auto; margin-right: auto">
        <textarea id="wp" name="document" style="margin: 0; padding: 0">
        %(content)s
        </textarea>
        </div>
        </form>
        </body>
        </html>
    """ % { "action": action, 
            "locale": locale, 
            "dtid": dtid, 
            "recid": recid, 
            "mediaid": mediaid, 
            "linktype": linktype, 
            "redirecturl": redirecturl, 
            "content": content }

def js_page(include, title = "", controller = [], execline = ""):
    """
    Returns a page that just runs javascript to get the job done
    include: a list of scripts or link tags (asm_script_tag or asm_css_tag calls)
    controller: a global object to be output. will be turned into json
    execline: a single line of javascript to run to start the page if needed
    """
    return """<!DOCTYPE html>
        <html>
        <head>
        <meta charset="utf-8">
        <title>%s</title>
        %s
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="shortcut icon" href="static/images/logo/icon-16.png">
        <link rel="icon" href="static/images/logo/icon-32.png" sizes="32x32">
        <link rel="icon" href="static/images/logo/icon-48.png" sizes="48x48">
        <link rel="icon" href="static/images/logo/icon-128.png" sizes="128x128">
        </head>
        <body>
        <noscript>Sorry. ASM will not work without Javascript.</noscript>
        <script>
        controller = %s;
        %s
        </script>
        </body>
        </html>""" % ( title, "\n".join(include), asm3.utils.json(controller), execline )

def mobile_page(l, title, scripts = [], controller = {}, execline = ""):
    """
    Outputs the boilerplate stuff for mobile pages using bootstrap.
    l: The current locale
    title: The page title
    scripts: A list of script names (will be passed to asm_script_tag for resolution)
    controller: A dictionary of values to pass to the page
    execline: A line of javascript to run to start the page if needed
    """
    tags = [ 
        script_tag(JQUERY_JS),
        script_tag(JQUERY_UI_JS),
        script_tag(BOOTSTRAP_JS),
        script_tag(MOMENT_JS),
        script_tag(MOUSETRAP_JS),
        script_tag(SIGNATURE_JS),
        css_tag(BOOTSTRAP_CSS),
        css_tag(BOOTSTRAP_ICONS_CSS),
        script_tag("config.js?ts=%s" % python2unix(now())),
        script_i18n(l)
    ]
    for s in scripts:
        tags.append(asm_script_tag(s))
    return js_page(tags, title, controller, execline)

def graph_js(l):
    return """
        %(jquery)s
        %(flot)s
        %(flotpie)s
        %(jqueryui)s
        %(jqueryuicss)s
        %(i18n)s
        %(asmcss)s
    """ % { "asmcss": asm_css_tag("asm.css"),
            "jquery": script_tag(JQUERY_JS), 
            "flot": script_tag(FLOT_JS), 
            "flotpie": script_tag(FLOT_PIE_JS),
            "i18n": script_i18n(l),
            "jqueryui": script_tag(JQUERY_UI_JS),
            "jqueryuicss": css_tag(JQUERY_UI_CSS % { "theme": "asm" })
          }

def map_js():
    return """
        %(jquery)s
        %(mousetrap)s
        %(config)s
        %(common)s
        %(commonmap)s
    """ % { "jquery": script_tag(JQUERY_JS), 
            "mousetrap": script_tag(MOUSETRAP_JS),
            "config": script_tag("config.js?ts=%s" % python2unix(now())),
            "common": asm_script_tag("common.js"),
            "commonmap": asm_script_tag("common_map.js")  }

def report_js(l):
    return """
        %(jqueryuicss)s
        %(jquery)s
        %(jqueryui)s
        %(i18n)s
        %(asmcss)s
        %(report_toolbar)s
    """ % { "asmcss": asm_css_tag("asm.css"),
            "jquery": script_tag(JQUERY_JS),
            "jqueryui": script_tag(JQUERY_UI_JS),
            "jqueryuicss": css_tag(JQUERY_UI_CSS % { "theme": "asm" }),
            "i18n": script_i18n(l),
            "report_toolbar": asm_script_tag("report_toolbar.js") }

def escape(s):
    if s is None: return ""
    s = str(s)
    return s.replace("'", "&apos;").replace("\"", "&quot;").replace(">", "&gt;").replace("<", "&lt;")

def escape_angle(s):
    if s is None: return ""
    s = str(s)
    return s.replace(">", "&gt;").replace("<", "&lt;")

def header(title, session):
    """
    The header for html pages.
    title: The page title
    session: The user session
    compatjs: True if this browser requires compatibility js for older browsers
    """
    s = bare_header(title, session.theme, session.locale, session.dbo.database, session.config_ts)
    return s

def footer():
    return "\n</body>\n</html>"

def currency(l, v):
    """
    Outputs a currency value. If it's negative, it shows in red.
    """
    s = format_currency(l, v)
    if s.startswith("("):
        s = "<span style=\"color: red\">" + s + "</span>"
    return s

def hidden(eid, value):
    """
    Outputs a hidden input field
    eid: The id of the input
    value: The value of the input
    """
    return "<input id=\"%s\" value=\"%s\" type=\"hidden\" />\n" % ( eid, str(value) )

def box(margintop=0, padding=5):
    """
    Outputs a div box container with jquery ui style
    """
    return """<div class="ui-helper-reset centered ui-widget-content ui-corner-all" style="margin-top: %dpx; padding: %dpx;">""" % (margintop, padding)

def heading(title, iscontent = True):
    """
    Outputs the heading for a page along with the asm content div
    """
    mid = ""
    if iscontent: mid = "id=\"asm-content\""
    return """
        <div %s class="ui-accordion ui-widget ui-helper-reset ui-accordion-icons">
        <h3 class="ui-accordion-header ui-helper-reset ui-corner-top ui-state-active centered"><a href="#">%s</a></h3>
        <div class="ui-helper-reset ui-widget-content ui-corner-bottom" style="padding: 5px;">
        """ % (mid, title)

def footing():
    """
    Outputs the footing for a page to close heading.
    """
    return """
    </div>
    </div>
    """
    
def script(code):
    """
    Outputs a script tag with javascript code
    """
    v = code
    # Escape anything in there that might cause our javascript
    # code to be malformed.
    v = v.replace("<script>", "&lt;script&gt;")
    v = v.replace("</script>", "&lt;\\/script&gt;")
    v = v.replace("\\\\\"", "\\\"")
    return "<script type=\"text/javascript\">\n%s\n</script>\n" % v

def script_json(varname, obj, prefix = "controller."):
    """
    Outputs a script tag with a variable varname containing 
    the object obj.
    """
    jv = asm3.utils.json(obj)
    return script("var %s%s = %s;" % (prefix, varname, jv))

def script_var(varname, v, prefix = "controller."):
    """
    Outputs a script tag with a javascript variable varname
    containing the value v
    """
    return script("var %s%s = %s;" % (prefix, varname, v))

def script_var_str(varname, v, prefix = "controller."):
    """
    Outputs a script tag with a javascript variable varname
    that contains a string value v. Handles escaping
    """
    v = "'" + v.replace("'", "\\'").replace("\n", " ") + "'"
    return script_var(varname, v, prefix)

def icon(name, title = ""):
    """
    Outputs a span tag containing an icon
    """
    if title == "":
        return "<span class=\"asm-icon asm-icon-%s\"></span>" % name
    else:
        return "<span class=\"asm-icon asm-icon-%s\" title=\"%s\"></span>" % (name, escape(title))

def doc_img_src(dbo, row):
    """
    Gets the img src attribute/link for a document picture. If the row
    doesn't have doc preferred media, the nopic src is returned instead.
    row: A query containing DOCMEDIAID
    """
    if row["DOCMEDIAID"] is None or row["DOCMEDIAID"] == "":
        return "image?db=%s&mode=nopic" % dbo.database
    else:
        return "image?db=%s&mode=media&id=%s&date=%s" % (dbo.database, row["DOCMEDIAID"], row["DOCMEDIADATE"].isoformat())

def menu_structure(l, publisherlist, reports, mailmerges):
    """
    Returns a list of lists representing the main menu structure
    l: The locale
    publisherlist: A reference to publish.PUBLISHER_LIST
    reports: A list of tuples containing the report url and name
    mailmerges: A list of tuples containing the report/mailmerge url and name
    """
    publishers = []
    for k, v in publisherlist.items():
        if k == "html" and not HTMLFTP_PUBLISHER_ENABLED: continue # Hide HTML publisher if it's disabled by sitedef
        if k == "html": # HTML requires translated text, where other publishers are localised/English
            publishers.append(("", "", "", "publish?mode=html", "asm-icon-blank", _("Publish HTML via FTP", l) ))
        else:
            publishers.append(("", "", "", "publish?mode=%s" % k, "asm-icon-blank", v["label"]))
    return (
        ("", "asm", _("ASM", l), (
            ( "", "", "", "--cat", "asm-icon-animal", _("Animals", l) ),
            ( asm3.users.VIEW_ANIMAL, "alt+shift+v", "", "shelterview", "asm-icon-location", _("Shelter view", l) ),
            ( asm3.users.VIEW_ANIMAL, "alt+shift+f", "", "animal_find", "asm-icon-animal-find", _("Find animal", l) ),
            ( asm3.users.ADD_ANIMAL, "alt+shift+n", "", "animal_new", "asm-icon-animal-add", _("Add a new animal", l) ),
            ( asm3.users.ADD_LOG, "alt+shift+l", "", "log_new?mode=animal", "asm-icon-log", _("Add a log entry", l) ),
            ( asm3.users.CHANGE_ANIMAL, "", "", "animal_bulk", "asm-icon-litter", _("Bulk change animals", l) ),
            ( asm3.users.ADD_LITTER, "", "", "litters", "asm-icon-litter", _("Edit litters", l) ),
            ( asm3.users.VIEW_ANIMAL, "alt+shift+t", "", "timeline", "asm-icon-calendar", _("Timeline", l) ),
            ( "", "", "taglostfound", "--cat", "asm-icon-animal-lost", _("Lost/Found", l) ),
            ( asm3.users.VIEW_LOST_ANIMAL, "", "taglostfound", "lostanimal_find", "asm-icon-animal-lost-find", _("Find a lost animal", l) ),
            ( asm3.users.VIEW_FOUND_ANIMAL, "", "taglostfound", "foundanimal_find", "asm-icon-animal-found-find", _("Find a found animal", l) ),
            ( asm3.users.ADD_LOST_ANIMAL, "", "taglostfound", "lostanimal_new", "asm-icon-animal-lost-add", _("Add a lost animal", l) ),
            ( asm3.users.ADD_FOUND_ANIMAL, "", "taglostfound", "foundanimal_new", "asm-icon-animal-found-add", _("Add a found animal", l) ),
            ( asm3.users.MATCH_LOST_FOUND, "", "taglostfound", "lostfound_match", "asm-icon-match", _("Match lost and found animals", l) ),
            ( "", "", "", "--cat", "asm-icon-person", _("People", l) ),
            ( asm3.users.VIEW_PERSON, "alt+shift+p", "", "person_find", "asm-icon-person-find", _("Find person", l) ),
            ( asm3.users.ADD_PERSON, "", "", "person_new", "asm-icon-person-add", _("Add a new person", l) ),
            ( asm3.users.ADD_LOG, "", "", "log_new?mode=person", "asm-icon-log", _("Add a log entry", l) ),
            ( asm3.users.VIEW_PERSON, "", "", "person_lookingfor", "asm-icon-animal-find", _("Person looking for report", l) ),
            ( asm3.users.VIEW_STAFF_ROTA, "", "tagrota", "staff_rota", "asm-icon-rota", _("Staff rota", l) ),
            ( "", "", "", "--break", "", "" ),
            ( "", "", "taganimalcontrolheader", "--cat", "asm-icon-call", _("Animal Control", l) ),
            ( asm3.users.ADD_INCIDENT, "alt+shift+i", "taganimalcontrol", "incident_new", "asm-icon-blank", _("Report a new incident", l) ),
            ( asm3.users.VIEW_INCIDENT, "", "taganimalcontrol", "incident_find", "asm-icon-blank", _("Find incident", l) ),
            ( asm3.users.VIEW_INCIDENT, "", "taganimalcontrol", "incident_map", "asm-icon-map", _("Map of active incidents", l) ),
            ( asm3.users.VIEW_TRAPLOAN, "", "tagtraploan", "traploan?filter=active", "asm-icon-traploan", _("Equipment loans", l) ),
            ( asm3.users.VIEW_LICENCE, "", "taganimalcontrol", "licence?offset=i31", "asm-icon-licence", _("Licensing", l) ),
            ( asm3.users.ADD_LICENCE, "", "taganimalcontrol", "licence_renewal", "asm-icon-blank", _("Renew license", l) ),
            ( asm3.users.VIEW_INCIDENT, "", "taganimalcontrol", "calendarview?ev=ol", "asm-icon-calendar", _("Animal control calendar", l) ),
            ( "", "", "", "--cat", "asm-icon-diary", _("Diary", l) ),
            ( asm3.users.ADD_DIARY, "", "", "diary_edit_my?newnote=1", "asm-icon-blank", _("Add a diary note", l) ),
            ( asm3.users.EDIT_MY_DIARY_NOTES, "", "", "diary_edit_my", "asm-icon-blank", _("My diary notes", l) ),
            ( asm3.users.EDIT_ALL_DIARY_NOTES, "", "", "diary_edit", "asm-icon-blank", _("All diary notes", l) ),
            ( asm3.users.EDIT_DIARY_TASKS, "", "", "diarytasks", "asm-icon-diary-task", _("Edit diary tasks", l) ),
            ( asm3.users.EDIT_MY_DIARY_NOTES, "alt+shift+c", "", "calendarview?ev=d", "asm-icon-calendar", _("Diary calendar", l) ),
            ( "", "", "tagdocumentrepo", "--cat", "asm-icon-document", _("Document Repository", l) ),
            ( asm3.users.VIEW_REPO_DOCUMENT, "", "tagdocumentrepo", "document_repository", "asm-icon-blank", _("Document Repository", l) ),
            ( "", "", "tagonlineform", "--cat", "asm-icon-forms", _("Online Forms", l) ),
            ( asm3.users.VIEW_ONLINE_FORMS, "", "tagonlineform", "onlineforms", "asm-icon-blank", _("Edit Online Forms", l) ),
            ( asm3.users.VIEW_INCOMING_FORMS, "alt+shift+m", "tagonlineform", "onlineform_incoming", "asm-icon-blank", _("View Incoming Forms", l) ),
            ( "", "", "tagwaitinglist", "--cat", "asm-icon-waitinglist", _("Waiting List", l) ),
            ( asm3.users.ADD_WAITING_LIST, "", "tagwaitinglist", "waitinglist_new", "asm-icon-blank", _("Add an animal to the waiting list", l) ),
            ( asm3.users.VIEW_WAITING_LIST, "alt+shift+w", "tagwaitinglist", "waitinglist_results", "asm-icon-blank", _("Edit the current waiting list", l) )
        )),
        (asm3.users.VIEW_MOVEMENT, "move", _("Move", l), (
            ( asm3.users.ADD_MOVEMENT, "", "", "--cat", "asm-icon-movement", _("Out", l) ),
            ( asm3.users.ADD_MOVEMENT, "", "", "move_reserve", "asm-icon-reservation", _("Reserve an animal", l) ),
            ( asm3.users.ADD_MOVEMENT, "alt+shift+o", "", "move_foster", "asm-icon-blank", _("Foster an animal", l) ),
            ( asm3.users.ADD_MOVEMENT, "", "", "move_transfer", "asm-icon-blank", _("Transfer an animal", l) ),
            ( asm3.users.ADD_MOVEMENT, "alt+shift+a", "", "move_adopt", "asm-icon-person", _("Adopt an animal", l) ),
            ( asm3.users.ADD_MOVEMENT, "", "", "move_reclaim", "asm-icon-blank", _("Reclaim an animal", l) ),
            ( asm3.users.ADD_MOVEMENT, "", "tagretailer", "move_retailer", "asm-icon-blank", _("Move an animal to a retailer", l) ),
            ( asm3.users.CHANGE_ANIMAL, "", "", "move_deceased", "asm-icon-death", _("Mark an animal deceased", l) ),
            ( asm3.users.VIEW_MOVEMENT, "", "", "--cat", "asm-icon-book", _("Books", l) ),
            ( asm3.users.VIEW_MOVEMENT, "", "", "move_book_reservation", "asm-icon-reservation", _("Reservation book", l) ),
            ( asm3.users.VIEW_MOVEMENT, "", "", "move_book_foster", "asm-icon-blank", _("Foster book", l) ),
            ( asm3.users.VIEW_MOVEMENT, "", "tagretailer", "move_book_retailer", "asm-icon-blank", _("Retailer book", l) ),
            ( asm3.users.VIEW_TRANSPORT, "", "tagtransport", "transport", "asm-icon-transport", _("Transport book", l) ),
            ( asm3.users.VIEW_MOVEMENT, "", "tagtrial", "move_book_trial_adoption", "asm-icon-trial", _("Trial adoption book", l) ),
            ( asm3.users.VIEW_MOVEMENT, "", "tagsoftrelease", "move_book_soft_release", "asm-icon-blank", _("Soft release book", l) ),
            ( "", "", "", "--break", "", "" ),
            ( asm3.users.ADD_MOVEMENT, "", "", "--cat", "asm-icon-animal", _("In", l) ),
            ( asm3.users.ADD_ANIMAL, "", "alt+shift+n", "animal_new", "asm-icon-animal-add", _("Induct a new animal", l) ),
            ( asm3.users.ADD_MOVEMENT, "", "", "move_book_recent_adoption", "asm-icon-blank", _("Return an animal from adoption", l) ),
            ( asm3.users.ADD_MOVEMENT, "", "", "move_book_recent_transfer", "asm-icon-blank", _("Return a transferred animal", l) ),
            ( asm3.users.ADD_MOVEMENT, "", "", "move_book_recent_other", "asm-icon-blank", _("Return an animal from another movement", l) )
        )),
        ("", "medical", _("Medical", l), (
            ( asm3.users.VIEW_MEDICAL, "", "", "calendarview?ev=vmt", "asm-icon-calendar", _("Medical calendar", l) ),
            ("", "", "", "--cat", "asm-icon-vaccination", _("Vaccinations", l) ),
            (asm3.users.ADD_VACCINATION, "", "", "vaccination?newvacc=1", "asm-icon-blank", _("Add a vaccination", l) ),
            (asm3.users.VIEW_VACCINATION, "", "", "vaccination", "asm-icon-book", _("Vaccination book", l) ),
            ("", "", "", "--cat", "asm-icon-test", _("Tests", l) ),
            (asm3.users.ADD_TEST, "", "", "test?newtest=1", "asm-icon-blank", _("Add a test", l) ),
            (asm3.users.VIEW_TEST, "", "", "test", "asm-icon-book", _("Test book", l) ),
            ("", "", "", "--cat", "asm-icon-medical", _("Treatments", l) ),
            (asm3.users.ADD_MEDICAL, "", "", "medical?newmed=1", "asm-icon-blank", _("Add a medical regimen", l) ),
            (asm3.users.VIEW_MEDICAL, "", "", "medical", "asm-icon-book", _("Medical book", l) ),
            (asm3.users.VIEW_MEDICAL, "", "", "medicalprofile", "asm-icon-blank", _("Medical profiles", l) ),
            ( "", "", "tagclinic", "--break", "", "" ),
            (asm3.users.VIEW_CLINIC, "", "tagclinic", "--cat", "asm-icon-health", _("Clinic", l) ),
            (asm3.users.VIEW_CLINIC, "", "tagclinic", "clinic_waitingroom", "asm-icon-person", _("Waiting Room", l) ),
            (asm3.users.VIEW_CLINIC, "", "tagclinic", "clinic_consultingroom", "asm-icon-users", _("Consulting Room", l) ),
            (asm3.users.VIEW_CLINIC, "", "tagclinic", "clinic_calendar", "asm-icon-diary", _("Clinic Calendar", l) ),
        )),
        ("", "financial", _("Financial", l), (
            ( asm3.users.VIEW_ACCOUNT, "alt+shift+x", "tagaccounts", "accounts", "asm-icon-accounts", _("Accounts", l) ),
            ( asm3.users.VIEW_STOCKLEVEL, "", "tagstock", "stocklevel", "asm-icon-stock", _("Stock", l) ),
            ( asm3.users.VIEW_VOUCHER, "", "", "voucher", "asm-icon-blank", _("Voucher book", l) ),
            ( asm3.users.VIEW_DONATION, "", "", "--cat", "", "Payments" ),
            ( asm3.users.VIEW_DONATION, "alt+shift+d", "", "donation", "asm-icon-donation", _("Payment book", l) ),
            ( asm3.users.VIEW_DONATION, "", "", "calendarview?ev=p", "asm-icon-calendar", _("Payment calendar", l) ),
            ( asm3.users.ADD_DONATION, "", "", "donation_receive", "asm-icon-blank", _("Receive a payment", l) ),
            ( asm3.users.VIEW_DONATION, "", "taggb", "--cat", "", "HMRC" ),
            ( asm3.users.VIEW_DONATION, "", "taggb", "giftaid_hmrc_spreadsheet", "asm-icon-report", "Generate HMRC Gift Aid spreadsheet" )
        )),
        (asm3.users.USE_INTERNET_PUBLISHER, "publishing", _("Publishing", l), [
            ("", "", "", "--cat", "asm-icon-settings", _("Configuration", l) ),
            (asm3.users.VIEW_ANIMAL, "", "", "search?q=forpublish", "asm-icon-animal", _("View animals matching publishing options", l) ),
            (asm3.users.PUBLISH_OPTIONS, "", "", "publish_options", "asm-icon-settings", _("Set publishing options", l) ),
            (asm3.users.PUBLISH_OPTIONS, "", "", "htmltemplates", "asm-icon-document", _("Edit HTML publishing templates", l)),
            ("", "", "", "--cat", "web", _("Publish now", l) ) 
        ] + publishers + [
            (asm3.users.USE_INTERNET_PUBLISHER, "", "", "publish_logs", "asm-icon-log", _("View publishing logs", l) )
        ]),
        (asm3.users.MAIL_MERGE, "mailmerge", _("Mail", l),
            mailmerges
        ),
        (asm3.users.VIEW_REPORT, "reports", _("Reports", l), 
            reports 
        ),
        (asm3.users.SYSTEM_MENU, "settings", _("Settings", l), (
            ("", "", "", "--cat", "asm-icon-settings", _("System", l)),
            (asm3.users.MODIFY_ADDITIONAL_FIELDS, "", "", "additional", "asm-icon-additional-field", _("Additional fields", l) ),
            (asm3.users.MODIFY_DOCUMENT_TEMPLATES, "", "", "document_templates", "asm-icon-document", _("Document templates", l) ),
            (asm3.users.MODIFY_LOOKUPS, "", "", "lookups", "asm-icon-lookups", _("Lookup data", l) ),
            (asm3.users.CHANGE_REPORT, "", "", "reports", "asm-icon-report", _("Reports", l) ),
            (asm3.users.USE_SQL_INTERFACE, "", "", "sql", "asm-icon-sql", _("SQL interface", l) ),
            (asm3.users.EDIT_USER, "", "", "systemusers", "asm-icon-users", _("System user accounts", l) ),
            (asm3.users.EDIT_USER, "", "", "roles", "asm-icon-auth", _("User roles", l) ),
            (asm3.users.SYSTEM_OPTIONS, "", "", "options", "asm-icon-settings", _("Options", l) ),
            ("", "", "", "--cat", "asm-icon-database", _("Data", l)),
            (asm3.users.EXPORT_REPORT, "", "", "report_export", "asm-icon-report", _("Export Reports as CSV", l) ),
            (asm3.users.EXPORT_ANIMAL_CSV, "", "", "csvexport", "asm-icon-animal", _("Export Animals as CSV", l) ),
            (asm3.users.IMPORT_CSV_FILE, "", "", "csvimport", "asm-icon-database", _("Import a CSV file", l) ),
            (asm3.users.IMPORT_CSV_FILE, "", "", "csvimport_paypal", "asm-icon-paypal", _("Import a PayPal CSV file", l) ),
            (asm3.users.IMPORT_CSV_FILE, "", "", "csvimport_stripe", "asm-icon-stripe", _("Import a Stripe CSV file", l) ),
            (asm3.users.TRIGGER_BATCH, "", "", "batch", "asm-icon-batch", _("Trigger Batch Processes", l) )
        ))
    )

def json_animalfindcolumns(dbo):
    l = dbo.locale
    cols = [ 
        ( "AnimalTypeID", _("Animal Type", l) ),
        ( "AnimalName", _("Name", l) ),
        ( "BaseColourID", _("Color", l) ),
        ( "CreatedBy", _("Created By", l) ),
        ( "SpeciesID", _("Species", l) ),
        ( "BreedName", _("Breed", l) ),
        ( "CoatType", _("Coat", l) ),
        ( "Markings", _("Features", l) ),
        ( "ShelterCode", _("Code", l) ),
        ( "AcceptanceNumber", _("Litter Ref", l) ),
        ( "DateOfBirth", _("Date Of Birth", l) ),
        ( "AgeGroup", _("Age Group", l) ),
        ( "AnimalAge", _("Age", l) ),
        ( "DeceasedDate", _("Died", l) ),
        ( "Sex", _("Sex", l) ),
        ( "IdentichipNumber", _("Microchip Number", l) ),
        ( "IdentichipDate", _("Microchip Date", l) ),
        ( "TattooNumber", _("Tattoo Number", l) ),
        ( "TattooDate", _("Tattoo Date", l) ),
        ( "Neutered", _("Altered", l) ),
        ( "NeuteredDate", _("Altered Date", l) ),
        ( "CombiTested", _("FIV/L Tested", l) ),
        ( "CombiTestDate", _("FIV/L Test Date", l) ),
        ( "CombiTestResult", _("FIV Result", l) ),
        ( "FLVResult", _("FLV Result", l) ),
        ( "HeartwormTested", _("Heartworm Tested", l) ),
        ( "HeartwormTestDate", _("Heartworm Test Date", l) ),
        ( "HeartwormTestResult", _("Heartworm Test Result", l) ),
        ( "Declawed", _("Declawed", l) ),
        ( "HiddenAnimalDetails", _("Hidden Comments", l) ),
        ( "AnimalComments", _("Description", l) ),
        ( "ReasonForEntry", _("Entry Reason", l) ),
        ( "ReasonNO", _("Reason Not From Owner", l) ),
        ( "DateBroughtIn", _("Date Brought In", l) ),
        ( "EntryReasonID", _("Entry Reason Category", l) ),
        ( "HealthProblems", _("Health Problems", l) ),
        ( "PTSReason", _("Death Comments", l) ),
        ( "PTSReasonID", _("Death Reason", l) ),
        ( "IsGoodWithCats", _("Good With Cats", l) ),
        ( "IsGoodWithDogs", _("Good With Dogs", l) ),
        ( "IsGoodWithChildren", _("Good With Children", l) ),
        ( "IsHouseTrained", _("Housetrained", l) ),
        ( "IsNotAvailableForAdoption", _("Not Available For Adoption", l) ),
        ( "IsHold", _("Hold", l) ),
        ( "HoldUntilDate", _("Hold until", l) ),
        ( "IsPickup", _("Picked Up", l) ),
        ( "PickupAddress", _("Pickup Address", l) ),
        ( "PickupLocationID", _("Pickup Location", l) ),
        ( "JurisdictionID", _("Jurisdiction", l) ),
        ( "IsQuarantine", _("Quarantine", l) ),
        ( "HasSpecialNeeds", _("Special Needs", l) ),
        ( "AdditionalFlags", _("Flags", l) ),
        ( "ShelterLocation", _("Location", l) ),
        ( "ShelterLocationUnit", _("Unit", l) ),
        ( "Fosterer", _("Fosterer", l) ),
        ( "OwnerID", _("Owner", l) ),
        ( "Size", _("Size", l) ),
        ( "Weight", _("Weight", l) ), 
        ( "RabiesTag", _("RabiesTag", l) ),
        ( "TimeOnShelter", _("Time On Shelter", l) ),
        ( "DaysOnShelter", _("Days On Shelter", l) ),
        ( "HasActiveReserve", _("Reserved", l) ), 
        ( "Adoptable", _("Adoptable", l) ),
        ( "Image", _("Image", l) )
        ]
    fd = asm3.additional.get_field_definitions(dbo, "animal")
    for f in fd:
        cols.append( (f["FIELDNAME"], f["FIELDLABEL"]) )
    cols = findcolumns_sort(cols)
    findcolumns_selectedtofront(cols, asm3.configuration.animal_search_columns(dbo))
    return cols

def json_lookup_tables(l):
    aslist = []
    for k, v in asm3.lookups.LOOKUP_TABLES.items():
        if k.startswith("lks") and not k == "lksize":
            # static tables only appear in non-English locales
            # for translation purposes and to stop people messing 
            # with things and breaking them
            if not l.startswith("en"):
                aslist.append(( k, translate(v[0], l)))
        else:
            aslist.append(( k, translate(v[0], l)))
    return sorted(aslist, key=lambda x: x[1])

def json_personfindcolumns(dbo):
    l = dbo.locale
    cols = [ 
        ( "CreatedBy", _("Created By", l) ),
        ( "CreatedDate", _("Created Date", l) ),
        ( "OwnerTitle", _("Title", l) ),
        ( "OwnerInitials", _("Initials", l) ),
        ( "OwnerForenames", _("First Names", l) ),
        ( "OwnerSurname", _("Last Name", l) ),
        ( "OwnerName", _("Name", l) ),
        ( "OwnerAddress", _("Address", l) ),
        ( "OwnerTown", _("City", l) ),
        ( "OwnerCounty", _("State", l) ),
        ( "OwnerPostcode", _("Zipcode", l) ),
        ( "HomeTelephone", _("Home", l) ),
        ( "WorkTelephone", _("Work", l) ),
        ( "MobileTelephone", _("Cell", l) ),
        ( "EmailAddress", _("Email", l) ),
        ( "IDCheck", _("Homechecked", l) ),
        ( "Jurisdiction", _("Jurisdiction", l) ),
        ( "Comments", _("Comments", l) ),
        ( "IsBanned", _("Banned", l) ),
        ( "IsDangerous", _("Dangerous", l) ),
        ( "IsVolunteer", _("Volunteer", l) ),
        ( "IsHomeChecker", _("Homechecker", l) ),
        ( "IsMember", _("Member", l) ),
        ( "MembershipExpiryDate", _("Membership Expiry", l) ),
        ( "MembershipNumber", _("Membership Number", l) ),
        ( "IsDonor", _("Donor", l) ),
        ( "IsShelter", _("Shelter", l) ),
        ( "IsACO", _("ACO", l) ),
        ( "IsStaff", _("Staff", l) ),
        ( "IsFosterer", _("Fosterer", l) ),
        ( "IsRetailer", _("Retailer", l) ),
        ( "IsVet", _("Vet", l) ),
        ( "IsGiftAid", _("GiftAid", l) ),
        ( "AdditionalFlags", _("Flags", l) ),
        ( "LookingForSummary", _("Looking For", l) ),
        ( "HomeCheckAreas", _("Homecheck Areas", l) ),
        ( "DateLastHomeChecked", _("Homecheck Date", l) ),
        ( "HomeCheckedBy", _("Homechecked By", l) ),
        ("IsSponsor", _("Sponsor", l) )
        ]
    fd = asm3.additional.get_field_definitions(dbo, "person")
    for f in fd:
        cols.append((f["FIELDNAME"], f["FIELDLABEL"]))
    cols = findcolumns_sort(cols)
    findcolumns_selectedtofront(cols, asm3.configuration.person_search_columns(dbo))
    return cols

def json_eventfindcolumns(dbo):
    l = dbo.locale
    cols = [ 
        ( "CreatedBy", _("Created By", l) ),
        ( "CreatedDate", _("Created Date", l) ),
        ( "LastChangedBy", _("Last Changed By", l) ),
        ( "LastChangedDate", _("Last Change Date", l) ),

        ( "EventName", _("Event Name", l) ),
        ( "StartDateTime", _("Start Date", l) ),
        ( "EndDateTime", _("End Date", l) ),
        ( "EventOwnerName", _("Location", l) ),
        ( "EventAddress", _("Address", l) ),
        ( "EventTown", _("City", l) ),
        ( "EventCounty", _("State", l) ),
        ( "EventPostcode", _("Zipcode", l) ),
        ( "EventCountry", _("Country", l) ),
        ]
    fd = asm3.additional.get_field_definitions(dbo, "event")
    for f in fd:
        cols.append((f["FIELDNAME"], f["FIELDLABEL"]))
    cols = findcolumns_sort(cols)
    findcolumns_selectedtofront(cols, asm3.configuration.event_search_columns(dbo))
    return cols
    
def json_incidentfindcolumns(dbo):
    l = dbo.locale
    cols = [ 
        ( "IncidentType", _("Incident Type", l) ),
        ( "IncidentNumber", _("Incident Number", l) ),
        ( "IncidentDateTime", _("Incident Date/Time", l) ),
        ( "DispatchAddress", _("Address", l) ),
        ( "DispatchTown", _("City", l) ),
        ( "DispatchPostcode", _("Zipcode", l) ),
        ( "JurisdictionName", _("Jurisdiction", l) ),
        ( "LocationName", _("Pickup Location", l) ),
        ( "Suspect", _("Suspect", l) ),
        ( "Victim", _("Victim", l) ),
        ( "DispatchDateTime", _("Dispatch Date/Time", l) ),
        ( "RespondedDateTime", _("Responded Date/Time", l) ),
        ( "DispatchedACO", _("ACO", l) ),
        ( "FollowupDateTime", _("Followup Date", l) ),
        ( "CompletedDate", _("Completed Date", l) ),
        ( "CompletedName", _("Completed Type", l) ),
        ( "Caller", _("Caller", l) ),
        ( "CallNotes", _("Notes", l) )
        ]
    fd = asm3.additional.get_field_definitions(dbo, "incident")
    for f in fd:
        cols.append( (f["FIELDNAME"], f["FIELDLABEL"]) )
    cols = findcolumns_sort(cols)
    findcolumns_selectedtofront(cols, asm3.configuration.incident_search_columns(dbo))
    return cols

def json_foundanimalfindcolumns(dbo):
    l = dbo.locale
    cols = [ 
        ("LostFoundID", _("Number", l)),
        ("Owner", _("Contact", l)),
        ("MicrochipNumber", _("Microchip", l)),
        ("AreaFound", _("Area", l)),
        ("AreaPostCode", _("Zipcode", l)),
        ("DateFound", _("Date", l)),
        ("AgeGroup", _("Age Group", l)),
        ("SexName", _("Sex", l)),
        ("SpeciesName", _("Species", l)),
        ("BreedName", _("Breed", l)),
        ("BaseColourName", _("Color", l)),
        ("DistFeat", _("Features", l))
        ]
    fd = asm3.additional.get_field_definitions(dbo, "foundanimal")
    for f in fd:
        cols.append( (f["FIELDNAME"], f["FIELDLABEL"]) )
    cols = findcolumns_sort(cols)
    findcolumns_selectedtofront(cols, asm3.configuration.foundanimal_search_columns(dbo))
    return cols

def json_lostanimalfindcolumns(dbo):
    l = dbo.locale
    cols = [ 
        ("LostFoundID", _("Number", l)),
        ("Owner", _("Contact", l)),
        ("MicrochipNumber", _("Microchip", l)),
        ("AreaLost", _("Area", l)),
        ("AreaPostCode", _("Zipcode", l)),
        ("DateLost", _("Date", l)),
        ("AgeGroup", _("Age Group", l)),
        ("SexName", _("Sex", l)),
        ("SpeciesName", _("Species", l)),
        ("BreedName", _("Breed", l)),
        ("BaseColourName", _("Color", l)),
        ("DistFeat", _("Features", l))
        ]
    fd = asm3.additional.get_field_definitions(dbo, "lostanimal")
    for f in fd:
        cols.append( (f["FIELDNAME"], f["FIELDLABEL"]) )
    cols = findcolumns_sort(cols)
    findcolumns_selectedtofront(cols, asm3.configuration.lostanimal_search_columns(dbo))
    return cols

def json_quicklinks(dbo):
    l = dbo.locale
    ql = []
    for k, v in asm3.configuration.QUICKLINKS_SET.items():
        ql.append( ( str(k), translate(v[2], l) ) )
    ql = findcolumns_sort(ql)
    findcolumns_selectedtofront(ql, asm3.configuration.quicklinks_id(dbo))
    return ql

def json_waitinglistcolumns(dbo):
    l = dbo.locale
    cols = [ 
        ( "Number", _("Number", l) ),
        ( "CreatedBy", _("Created By", l) ),
        ( "Rank", _("Rank", l) ),
        ( "SpeciesID", _("Species", l) ),
        ( "Size", _("Size", l) ),
        ( "DatePutOnList", _("Date Put On", l) ),
        ( "TimeOnList", _("Time On List", l) ),
        ( "OwnerName", _("Name", l) ),
        ( "OwnerAddress", _("Address", l) ),
        ( "OwnerTown", _("City", l) ),
        ( "OwnerCounty", _("State", l) ),
        ( "OwnerPostcode", _("Zipcode", l) ),
        ( "HomeTelephone", _("Home", l) ),
        ( "WorkTelephone", _("Work", l) ),
        ( "MobileTelephone", _("Cell", l) ),
        ( "EmailAddress", _("Email", l) ),
        ( "AnimalDescription", _("Description", l) ),
        ( "ReasonForWantingToPart", _("Reason", l) ),
        ( "CanAffordDonation", _("Donation?", l) ),
        ( "Urgency", _("Urgency", l) ),
        ( "DateRemovedFromList", _("Date Removed", l) ),
        ( "ReasonForRemoval", _("Removal Reason", l) ),
        ( "Comments", _("Comments") )
        ]
    fd = asm3.additional.get_field_definitions(dbo, "waitinglist")
    for f in fd:
        cols.append( (f["FIELDNAME"], f["FIELDLABEL"]) )
    cols = findcolumns_sort(cols)
    findcolumns_selectedtofront(cols, asm3.configuration.waiting_list_view_columns(dbo))
    return cols

def findcolumns_sort(cols):
    """
    For options_*findcolumns routines, sorts the list alphabetically
    by display string
    """
    return sorted(cols, key=lambda x: x[1])

def findcolumns_selectedtofront(cols, vals):
    """
    For options_*findcolumns routines, moves selected items
    to the beginning of the list in order they appear in
    vals. vals is a comma separated string.
    """
    for v in reversed(vals.split(",")):
        v = v.strip()
        for i,val in enumerate(cols):
            if val[0] == v:
                cols.insert(0, cols.pop(i))
                break
    return vals

def qr_animal_img_record_src(animalid, size = "150x150"):
    """
    Returns an img src attribute for a QR code to an animal's record.
    size is a sizespec eg: 150x150
    """
    return QR_IMG_SRC % { "url": f"{BASE_URL}/animal?id={animalid}", "size": size }

def qr_animal_img_share_src(dbo, animalid, size = "150x150"):
    """
    Returns an img src attribute for a QR code to the public animalview page for the animal.
    size is a sizespec eg: 150x150
    """
    return QR_IMG_SRC % { "url": f"{SERVICE_URL}?account={dbo.database}&method=animal_view&animalid={animalid}", "size": size }

def thumbnail_img_src(dbo, row, mode):
    """
    Gets the img src attribute for a thumbnail picture. If the row
    doesn't have preferred media, the nopic src is returned instead.
    We do it this way to make things more easily cacheable.
    If we're in animal mode, we'll take ANIMALID or ID, if we're
    in person mode we'll use PERSONID or ID
    row: An animal_query or person_query row containing ID, ANIMALID or PERSONID and WEBSITEMEDIANAME/DATE
    mode: The mode - animalthumb or personthumb
    """
    if row["WEBSITEMEDIANAME"] is None or row["WEBSITEMEDIANAME"] == "":
        return "image?db=%s&mode=dbfs&id=/reports/nopic.jpg" % dbo.database
    else:
        idval = 0
        if mode == "animalthumb":
            if "ANIMALID" in row:
                idval = int(row["ANIMALID"])
            elif "ID" in row:
                idval = int(row["ID"])
        elif mode == "personthumb":
            if "PERSONID" in row:
                idval = int(row["PERSONID"])
            elif "ID" in row:
                idval = int(row["ID"])
        else:
            idval = int(row["ID"])
        uri = "image?db=" + dbo.database + "&mode=" + mode + "&id=" + str(idval)
        if "WEBSITEMEDIADATE" in row and row["WEBSITEMEDIADATE"] is not None:
            uri += "&date=" + str(row["WEBSITEMEDIADATE"].isoformat())
        return uri

def option(name, value = None, selected = False):
    sel = ""
    val = ""
    if selected: sel = " selected=\"selected\""
    if value is not None: val = " value=\"%s\"" % value
    return "<option %s%s>%s</option>\n" % ( val, sel, name )

def options(l, rows, displayfield, idfield = "ID", includeAll = False, includeRetired = False, selected = -1, alltext = "*"):
    s = []
    if includeAll:
        if alltext == "*": alltext = _("(all)", l)
        s.append(option(alltext, "-1", False))
    for r in rows:
        if not includeRetired and "ISRETIRED" in r and r.ISRETIRED: continue
        if displayfield == "ANIMALNAMECODE":
            s.append(option("%s - %s" % (r.ANIMALNAME, r.SHELTERCODE), str(r[idfield]), r[idfield] == selected))
        elif displayfield == "PERSONNAMEADDRESS":
            s.append(option("%s - %s" % (r.OWNERNAME, r.OWNERADDRESS), str(r[idfield]), r[idfield] == selected))
        else: 
            s.append(option("%s" % r[displayfield], str(r[idfield]), r[idfield] == selected))
    return "".join(s)

def options_accounts(dbo, includeAll = False, selected = -1, alltext = "*"):
    return options(dbo.locale, asm3.financial.get_accounts(dbo), "CODE", includeAll=includeAll, alltext=alltext, selected=selected)

def options_account_types(dbo, includeAll = False, selected = -1, alltext = "*"):
    return options(dbo.locale, asm3.lookups.get_account_types(dbo), "ACCOUNTTYPE", includeAll=includeAll, alltext=alltext, selected=selected)

def options_additionalfield_links(dbo, includeAll = False, selected = -1):
    return options(dbo.locale, asm3.lookups.get_additionalfield_links(dbo), "LINKTYPE", includeAll=includeAll, selected=selected)

def options_additionalfield_types(dbo, includeAll = False, selected = -1):
    return options(dbo.locale, asm3.lookups.get_additionalfield_types(dbo), "FIELDTYPE", includeAll=includeAll, selected=selected)

def options_animal_flags(dbo):
    s = ""
    l = dbo.locale
    pf = asm3.lookups.get_animal_flags(dbo)
    s += option(_("Courtesy Listing", l), "courtesy")
    s += option(_("Cruelty Case", l), "crueltycase")
    s += option(_("Do Not Register Microchip", l), "notforregistration")
    s += option(_("Non-Shelter", l), "nonshelter")
    s += option(_("Not For Adoption", l), "notforadoption")
    s += option(_("Quarantine", l), "quarantine")
    for p in pf:
        s += option(p["FLAG"])
    return s

def options_animals(dbo, includeAll = False, selected = -1):
    return options(dbo.locale, asm3.animal.get_animals_namecode(dbo), "ANIMALNAMECODE", includeAll=includeAll, selected=selected)

def options_animals_on_shelter(dbo, includeAll = False, selected = -1):
    return options(dbo.locale, asm3.animal.get_animals_on_shelter_namecode(dbo), "ANIMALNAMECODE", includeAll=includeAll, selected=selected)

def options_animals_on_shelter_foster(dbo, includeAll = False, selected = -1):
    return options(dbo.locale, asm3.animal.get_animals_on_shelter_foster_namecode(dbo), "ANIMALNAMECODE", includeAll=includeAll, selected=selected)

def options_animal_types(dbo, includeAll = False, selected = -1, includeRetired = False):
    return options(dbo.locale, asm3.lookups.get_animal_types(dbo), "ANIMALTYPE", includeAll=includeAll, selected=selected, includeRetired=includeRetired)

def options_breeds(dbo, includeAll = False, selected = -1, includeRetired = False):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    bd = asm3.lookups.get_breeds_by_species(dbo)
    gp = ""
    ngp = ""
    for b in bd:
        
        ngp = b["SPECIESNAME"]
        if ngp is None: ngp = ""

        if gp != ngp:
            if gp != "":
                s += "</optgroup>\n"
            s += "<optgroup id='ngp-" + str(b["SPECIESID"]) + "' label=\"%s\">\n" % ngp
            gp = ngp

        if not includeRetired and b.ISRETIRED: continue
        s += option(b["BREEDNAME"], str(b["ID"]), int(b["ID"]) == selected)
    return s

def options_coattypes(dbo, includeAll = False, selected = -1):
    return options(dbo.locale, asm3.lookups.get_coattypes(dbo), "COATTYPE", includeAll=includeAll, selected=selected)

def options_colours(dbo, includeAll = False, selected = -1, includeRetired = False):
    return options(dbo.locale, asm3.lookups.get_basecolours(dbo), "BASECOLOUR", includeAll=includeAll, selected=selected, includeRetired=includeRetired)

def options_cost_types(dbo, includeAll = False, selected = -1, includeRetired = False):
    return options(dbo.locale, asm3.lookups.get_costtypes(dbo), "COSTTYPENAME", includeAll=includeAll, selected=selected, includeRetired=includeRetired)

def options_deathreasons(dbo, includeAll = False, selected = -1, includeRetired = False):
    return options(dbo.locale, asm3.lookups.get_deathreasons(dbo), "REASONNAME", includeAll=includeAll, selected=selected, includeRetired=includeRetired)

def options_diets(dbo, includeAll = False, selected = -1, includeRetired = False):
    return options(dbo.locale, asm3.lookups.get_diets(dbo), "DIETNAME", includeAll=includeAll, selected=selected, includeRetired=includeRetired)

def options_donation_types(dbo, includeAll = False, selected = -1, alltext = "*", includeRetired = False):
    return options(dbo.locale, asm3.lookups.get_donation_types(dbo), "DONATIONNAME", includeAll=includeAll, alltext=alltext, selected=selected, includeRetired=includeRetired)

def options_donation_methods(dbo, includeAll = False, selected = -1, includeRetired = False):
    return options(dbo.locale, asm3.lookups.get_payment_methods(dbo), "PAYMENTNAME", includeAll=includeAll, selected=selected, includeRetired=includeRetired)

def options_donation_frequencies(dbo, includeAll = False, selected = -1):
    return options(dbo.locale, asm3.lookups.get_donation_frequencies(dbo), "FREQUENCY", includeAll=includeAll, selected=selected)

def options_entryreasons(dbo, includeAll = False, selected = -1, includeRetired = False):
    return options(dbo.locale, asm3.lookups.get_entryreasons(dbo), "REASONNAME", includeAll=includeAll, selected=selected, includeRetired=includeRetired)

def options_incident_types(dbo, includeAll = False, selected = -1, includeRetired = False):
    return options(dbo.locale, asm3.lookups.get_incident_types(dbo), "INCIDENTNAME", includeAll=includeAll, selected=selected, includeRetired=includeRetired)

def options_internal_locations(dbo, includeAll = False, selected = -1, locationfilter = "", siteid = 0, includeRetired = False):
    return options(dbo.locale, asm3.lookups.get_internal_locations(dbo, locationfilter, siteid), "LOCATIONNAME", includeAll=includeAll, selected=selected, includeRetired=includeRetired)

def options_litters(dbo, includeAll = False, selected = "-1"):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    al = asm3.animal.get_litters(dbo)
    for i in al:
        disp = ""
        if i["PARENTANIMALID"] is not None and i["PARENTANIMALID"] > 0:
            disp = _("{0}: {1} {2} - {3} {4}", l).format(
                i["MOTHERCODE"], i["MOTHERNAME"],
                i["ACCEPTANCENUMBER"], i["SPECIESNAME"],
                i["COMMENTS"][:40])
        else:
            disp = _("{0} - {1} {2}", l).format(
                i["ACCEPTANCENUMBER"], i["SPECIESNAME"],
                i["COMMENTS"][:40])
        s += option(disp, i["ACCEPTANCENUMBER"], i["ACCEPTANCENUMBER"] == selected)
    return s

def options_locales():
    s = ""
    for code, label in get_locales():
        s += "<option value=\"" + code + "\">" + label + "</option>"
    return s

def options_log_types(dbo, includeAll = False, selected = -1, includeRetired = False):
    return options(dbo.locale, asm3.lookups.get_log_types(dbo), "LOGTYPENAME", includeAll=includeAll, selected=selected, includeRetired=includeRetired)

def options_medicalprofiles(dbo, selected = -1):
    return options(dbo.locale, asm3.medical.get_profiles(dbo), "PROFILENAME", selected=selected)

def options_movement_types(dbo, includeAll = False, selected = -1):
    return options(dbo.locale, asm3.lookups.get_movement_types(dbo), "MOVEMENTTYPE", includeAll=includeAll, selected=selected)

def options_person_flags(dbo):
    s = ""
    l = dbo.locale
    pf = asm3.lookups.get_person_flags(dbo)
    s += option(_("ACO", l), "aco")
    s += option(_("Adopter", l), "adopter")
    s += option(_("Adoption Coordinator", l), "coordinator")
    s += option(_("Banned", l), "banned")
    s += option(_("Dangerous", l), "dangerous")
    s += option(_("Deceased", l), "deceased")
    s += option(_("Donor", l), "donor")
    s += option(_("Driver", l), "driver")
    s += option(_("Exclude from bulk email", l), "excludefrombulkemail")
    s += option(_("Fosterer", l), "fosterer")
    s += option(_("Homechecked", l), "homechecked")
    s += option(_("Homechecker", l), "homechecker")
    s += option(_("Member", l), "member")
    s += option(_("Other Shelter", l), "shelter")
    s += option(_("Retailer", l), "retailer")
    s += option(_("Staff", l), "staff")
    if l == "en_GB": s += option(_("UK Giftaid", l), "giftaid")
    s += option(_("Vet", l), "vet")
    s += option(_("Volunteer", l), "volunteer")
    s += option(_("Sponsor", l), "sponsor")
    for p in pf:
        s += option(p["FLAG"])
    return s

def options_people(dbo, includeAll = False, selected = -1):
    return options(dbo.locale, asm3.person.get_person_name_addresses(dbo), "PERSONNAMEADDRESS", includeAll=includeAll, selected=selected)

def options_people_not_homechecked(dbo, includeAll = False, selected = -1):
    return options(dbo.locale, asm3.person.get_reserves_without_homechecks(dbo), "PERSONNAMEADDRESS", includeAll=includeAll, selected=selected)

def options_posneg(dbo, includeAll = False, selected = -1):
    return options(dbo.locale, asm3.lookups.get_posneg(dbo), "NAME", includeAll=includeAll, selected=selected)

def options_species(dbo, includeAll = False, selected = -1, includeRetired = False):
    return options(dbo.locale, asm3.lookups.get_species(dbo), "SPECIESNAME", includeAll=includeAll, selected=selected, includeRetired=includeRetired)

def options_sexes(dbo,  includeAll = False, selected = -1):
    return options(dbo.locale, asm3.lookups.get_sexes(dbo), "SEX", includeAll=includeAll, selected=selected)

def options_sizes(dbo, includeAll = False, selected = -1):
    return options(dbo.locale, asm3.lookups.get_sizes(dbo), "SIZE", includeAll=includeAll, selected=selected)

def options_sites(dbo, includeAll = False, selected = -1):
    return options(dbo.locale, asm3.lookups.get_sites(dbo), "SITENAME", includeAll=includeAll, selected=selected)

def options_users(dbo, includeAll = False, selected = ""):
    return options(dbo.locale, asm3.users.get_users(dbo), "USERNAME", idfield="USERNAME", includeAll=includeAll, selected=selected)

def options_users_and_roles(dbo, includeAll = False, includeEveryone = False, selected = ""):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "all", selected == "all")
    if includeEveryone: s += option(_("(everyone)", l), "*", selected == "*")
    su = asm3.users.get_users_and_roles(dbo)
    for u in su:
        s += option(u["USERNAME"], u["USERNAME"], u["USERNAME"] == selected)
    return s

def options_vaccination_types(dbo, includeAll = False, selected = -1, includeRetired = False):
    return options(dbo.locale, asm3.lookups.get_vaccination_types(dbo), "VACCINATIONTYPE", includeAll=includeAll, selected=selected, includeRetired=includeRetired)

def options_voucher_types(dbo, includeAll = False, selected = -1, includeRetired = False):
    return options(dbo.locale, asm3.lookups.get_voucher_types(dbo), "VOUCHERNAME", includeAll=includeAll, selected=selected, includeRetired=includeRetired)

def options_yesno(dbo, includeAll = False, selected = -1):
    return options(dbo.locale, asm3.lookups.get_yesno(dbo), "NAME", includeAll=includeAll, selected=selected)
  
def options_ynun(dbo, includeAll = False, selected = -1):
    return options(dbo.locale, asm3.lookups.get_ynun(dbo), "NAME", includeAll=includeAll, selected=selected)


