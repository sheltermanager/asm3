
import asm3.additional
import asm3.animal
import asm3.configuration
import asm3.financial
import asm3.lookups
import asm3.medical
import asm3.person
import asm3.users
import asm3.utils

from asm3.i18n import BUILD, _, translate, format_currency, format_date, get_locales, now, python2display, python2unix, real_locale
from asm3.sitedefs import QR_IMG_SRC
from asm3.sitedefs import BASE_URL, LOCALE, ROLLUP_JS, SERVICE_URL
from asm3.sitedefs import ASMSELECT_CSS, ASMSELECT_JS, BASE64_JS, CODEMIRROR_CSS, CODEMIRROR_JS, CODEMIRROR_BASE, FLOT_JS, FLOT_PIE_JS, FULLCALENDAR_JS, FULLCALENDAR_CSS, HTMLFTP_PUBLISHER_ENABLED, JQUERY_JS, JQUERY_UI_JS, JQUERY_UI_CSS, MOMENT_JS, MOUSETRAP_JS, PATH_JS, SIGNATURE_JS, TABLESORTER_CSS, TABLESORTER_JS, TABLESORTER_WIDGETS_JS, TIMEPICKER_CSS, TIMEPICKER_JS, TINYMCE_5_JS, TOUCHPUNCH_JS

import os

BACKGROUND_COLOURS = {
    "asm":              "#ffffff",
    "asm-dark":         "#000000",
    "base":             "#ffffff",
    "black-tie":        "#333333",
    "blitzer":          "#cc0000",
    "cupertino":        "#deedf7",
    "dark-hive":        "#444444",
    "dot-luv":          "#0b3e6f",
    "eggplant":         "#30273a",
    "excite-bike":      "#f9f9f9",
    "flick":            "#dddddd",
    "hot-sneaks":       "#35414f",
    "humanity":         "#cb842e",
    "le-frog":          "#3a8104",
    "mint-choc":        "#453326",
    "overcast":         "#dddddd",
    "pepper-grinder":   "#ffffff",
    "redmond":          "#5c9ccc",
    "smoothness":       "#cccccc",
    "south-street":     "#ece8da",
    "start":            "#2191c0",
    "sunny":            "#817865",
    "swanky-purse":     "#261803",
    "trontastic":       "#9fda58",
    "ui-darkness":      "#333333",
    "ui-lightness":     "#ffffff",
    "vader":            "#888888"
}

def css_tag(uri, idattr=""):
    """
    Returns a css link tag to a resource.
    """
    if idattr != "": idattr = "id=\"%s\"" % idattr
    return "<link rel=\"stylesheet\" type=\"text/css\" href=\"%s\" %s />\n" % (uri, idattr)

def asm_css_tag(filename):
    """
    Returns a path to one of our stylesheets
    """
    return "<link rel=\"stylesheet\" type=\"text/css\" href=\"static/css/%s?b=%s\" />\n" % (filename, BUILD)

def script_i18n(l):
    return "<script type=\"text/javascript\" src=\"static/js/locales/locale_%s.js?b=%s\"></script>\n" % (real_locale(l), BUILD)

def script_tag(uri, idattr=""):
    """
    Returns a script tag to a resource.
    """
    if idattr != "": idattr = "id=\"%s\"" % idattr
    return "<script type=\"text/javascript\" src=\"%s\" %s></script>\n" % (uri, idattr)

def asm_script_tag(filename):
    """
    Returns a path to one of our javascript files.
    If we're in rollup mode and one of our standalone files is requested,
    get it from the compat folder instead so it's still cross-browser compliant and minified.
    """
    standalone = [ "animal_view_adoptable.js", "document_edit.js", "mobile.js", "mobile_sign.js", 
        "onlineform_extra.js", "report_toolbar.js", "service_sign_document.js", "service_checkout_adoption.js" ]
    if ROLLUP_JS and filename in standalone and filename.find("/") == -1: filename = "compat/%s" % filename
    return "<script type=\"text/javascript\" src=\"static/js/%s?b=%s\"></script>\n" % (filename, BUILD)

def asm_script_tags(path):
    """
    Returns separate script tags for all ASM javascript files.
    """
    jsfiles = [ "common.js", "common_map.js", "common_widgets.js", "common_animalchooser.js",
        "common_animalchoosermulti.js", "common_personchooser.js", "common_tableform.js", "header.js",
        "header_additional.js", "header_edit_header.js" ]
    exclude = [ "animal_view_adoptable.js", "document_edit.js", "mobile.js", "mobile_sign.js", 
        "onlineform_extra.js", "report_toolbar.js", "service_sign_document.js", "service_checkout_adoption.js" ]
    # Read our available js files and append them to this list, not including ones
    # we've explicitly added above (since they are in correct load order)
    # or those we should exclude because they are standalone files
    for i in os.listdir(path + "static/js"):
        if i not in jsfiles and i not in exclude and not i.startswith(".") and i.endswith(".js"):
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
        return "<script type=\"text/javascript\" src=\"config.js?db=%s&ts=%s\"></script>\n" % (config_db, config_ts)
    def script_schema():
        return asm_script_tag("bundle/schema.js") # statically generated
    # Use the default if we have no locale
    if locale is None: locale = LOCALE
    # Load the asm scripts
    if ROLLUP_JS:
        asm_scripts = asm_script_tag("bundle/rollup_compat.min.js")
    else:
        asm_scripts = asm_script_tags(asm3.utils.PATH) 
    # Set the body colour from the theme
    bgcol = BACKGROUND_COLOURS["asm"]
    if theme in BACKGROUND_COLOURS:
        bgcol = BACKGROUND_COLOURS[theme]
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
                css_tag(JQUERY_UI_CSS % { "theme": theme}, "jqt") +
                asm_css_tag("asm-icon.css") +
                asm_css_tag("asm.css") + 
                script_tag("static/lib/modernizr/modernizr.min.js") + 
                script_tag(JQUERY_JS) +
                script_tag(JQUERY_UI_JS) +
                script_tag(TOUCHPUNCH_JS) +
                script_tag(MOMENT_JS) + 
                script_tag(MOUSETRAP_JS) + 
                script_tag(ASMSELECT_JS) + 
                script_tag(BASE64_JS) + 
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
            "bgcol": bgcol }

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
        </head>
        <body>
        <script>
        controller = %s;
        %s
        </script>
        </body>
        <html>""" % ( title, "\n".join(include), asm3.utils.json(controller), execline )

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
        <script type="text/javascript" src="config.js?ts=%(time)s"></script>
        %(common)s
        %(commonmap)s
    """ % { "mousetrap": script_tag(MOUSETRAP_JS),
            "jquery": script_tag(JQUERY_JS), 
            "time": escape(now()),
            "common": asm_script_tag("common.js"),
            "commonmap": asm_script_tag("common_map.js") }

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

def rss(inner, title, link, description):
    """ Renders an RSS document """
    return '<?xml version="1.0" encoding="UTF-8"?>' \
        '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/" >' \
        '<channel rdf:about="%s">' \
        '<title>%s</title>' \
        '<description>%s</description>' \
        '<link>%s</link>' \
        '</channel>' \
        '%s' \
        '</rdf:RDF>' % (BASE_URL, title, description, link, inner)

def rss_item(title, link, description):
    return '<item rdf:about="%s">' \
        '<title>%s</title>' \
        '<link>%s</link>' \
        '<description>' \
        '%s' \
        '</description>' \
        '</item>' % (BASE_URL, title, link, description)

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
    row: A query containing DOCMEDIANAME
    """
    if row["DOCMEDIANAME"] is None or row["DOCMEDIANAME"] == "":
        return "image?db=%s&mode=nopic" % dbo.database
    else:
        return "image?db=%s&mode=dbfs&id=%s&date=%s" % (dbo.database, row["DOCMEDIANAME"], row["DOCMEDIADATE"].isoformat())

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
        ( "HomeCheckedBy", _("Homechecked By", l) )
        ]
    fd = asm3.additional.get_field_definitions(dbo, "person")
    for f in fd:
        cols.append( (f["FIELDNAME"], f["FIELDLABEL"]) )
    cols = findcolumns_sort(cols)
    findcolumns_selectedtofront(cols, asm3.configuration.person_search_columns(dbo))
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

def options_accounts(dbo, includeAll = False, selected = -1, alltext = "*"):
    s = ""
    l = dbo.locale
    if includeAll: 
        if alltext == "*": s += option(_("(all)", l), "-1", False)
        else: s += option(alltext, "-1", False)
    ac = asm3.financial.get_accounts(dbo)
    for a in ac:
        s += option("%s" % a["CODE"],
            str(a["ID"]), 
            int(a["ID"]) == selected)
    return s

def options_account_types(dbo, includeAll = False, selected = -1, alltext = "*"):
    l = dbo.locale
    s = ""
    if includeAll: 
        if alltext == "*": s += option(_("(all)", l), "-1", False)
        else: s += option(alltext, "-1", False)
    at = asm3.lookups.get_account_types(dbo)
    for a in at:
        s += option(a["ACCOUNTTYPE"],
            str(a["ID"]),
            int(a["ID"]) == selected)
    return s

def options_additionalfield_links(dbo, includeAll = False, selected = -1):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    al = asm3.lookups.get_additionalfield_links(dbo)
    for a in al:
        s += option(a["LINKTYPE"], 
            str(a["ID"]), 
            int(a["ID"]) == selected)
    return s

def options_additionalfield_types(dbo, includeAll = False, selected = -1):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    at = asm3.lookups.get_additionalfield_types(dbo)
    for a in at:
        s += option(a["FIELDTYPE"], 
            str(a["ID"]), 
            int(a["ID"]) == selected)
    return s

def options_agegroups(dbo, includeAll = False, includeUnknown = False, selected = "-1"):
    s = ""
    l = dbo.locale
    if includeAll: s += option(_("(all)", l), "-1", False)
    if includeUnknown: s += option(_("(unknown)", l), "Unknown", False)
    ag = asm3.configuration.age_groups(dbo)
    for a in ag:
        s += option(a, a, a == selected)
    return s

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
    s = ""
    l = dbo.locale
    if includeAll: s += option(_("(all)", l), "-1", False)
    an = asm3.animal.get_animals_namecode(dbo)
    for a in an:
        s += option("%s - %s" % ( a["ANIMALNAME"], a["SHELTERCODE"] ), 
            str(a["ID"]), 
            int(a["ID"]) == selected)
    return s

def options_animals_on_shelter(dbo, includeAll = False, selected = -1):
    s = ""
    l = dbo.locale
    if includeAll: s += option(_("(all)", l), "-1", False)
    an = asm3.animal.get_animals_on_shelter_namecode(dbo)
    for a in an:
        s += option("%s - %s" % ( a["ANIMALNAME"], a["CODE"] ), 
            str(a["ID"]), 
            int(a["ID"]) == selected)
    return s

def options_animals_on_shelter_foster(dbo, includeAll = False, selected = -1):
    s = ""
    l = dbo.locale
    if includeAll: s += option(_("(all)", l), "-1", False)
    an = asm3.animal.get_animals_on_shelter_foster_namecode(dbo)
    for a in an:
        s += option("%s - %s" % ( a["ANIMALNAME"], a["CODE"] ), 
            str(a["ID"]), 
            int(a["ID"]) == selected)
    return s

def options_animal_types(dbo, includeAll = False, selected = -1, includeRetired = False):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    at = asm3.lookups.get_animal_types(dbo)
    for a in at:
        if not includeRetired and a.ISRETIRED: continue
        s += option(a["ANIMALTYPE"], 
            str(a["ID"]), 
            int(a["ID"]) == selected)
    return s

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
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    ct = asm3.lookups.get_coattypes(dbo)
    for c in ct:
        s += option(c["COATTYPE"],
            str(c["ID"]),
            int(c["ID"]) == selected)
    return s

def options_colours(dbo, includeAll = False, selected = -1, includeRetired = False):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    bc = asm3.lookups.get_basecolours(dbo)
    for c in bc:
        if not includeRetired and c.ISRETIRED: continue
        s += option(c["BASECOLOUR"],
            str(c["ID"]),
            int(c["ID"]) == selected)
    return s

def options_cost_types(dbo, includeAll = False, selected = -1, includeRetired = False):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    bc = asm3.lookups.get_costtypes(dbo)
    for c in bc:
        if not includeRetired and c.ISRETIRED: continue
        s += option(c["COSTTYPENAME"],
            str(c["ID"]),
            int(c["ID"]) == selected)
    return s

def options_deathreasons(dbo, includeAll = False, selected = -1, includeRetired = False):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    dr = asm3.lookups.get_deathreasons(dbo)
    for d in dr:
        if not includeRetired and d.ISRETIRED: continue
        s += option(d["REASONNAME"],
            str(d["ID"]),
            int(d["ID"]) == selected)
    return s

def options_diets(dbo, includeAll = False, selected = -1, includeRetired = False):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    di = asm3.lookups.get_diets(dbo)
    for d in di:
        if not includeRetired and d.ISRETIRED: continue
        s += option(d["DIETNAME"],
            str(d["ID"]),
            int(d["ID"]) == selected)
    return s

def options_donation_types(dbo, includeAll = False, includeNone = False, selected = -1, alltext = "*", includeRetired = False):
    l = dbo.locale
    s = ""
    if includeAll: 
        if alltext == "*": s += option(_("(all)", l), "-1", False)
        else: s += option(alltext, "-1", False)
    if includeNone:
        s += option(_("(none)", l), "0", False)
    dt = asm3.lookups.get_donation_types(dbo)
    for d in dt:
        if not includeRetired and d.ISRETIRED: continue
        s += option(d["DONATIONNAME"],
            str(d["ID"]),
            int(d["ID"]) == selected)
    return s

def options_donation_frequencies(dbo, includeAll = False, selected = -1):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    df = asm3.lookups.get_donation_frequencies(dbo)
    for d in df:
        s += option(d["FREQUENCY"],
            str(d["ID"]),
            int(d["ID"]) == selected)
    return s

def options_entryreasons(dbo, includeAll = False, selected = -1, includeRetired = False):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    er = asm3.lookups.get_entryreasons(dbo)
    for e in er:
        if not includeRetired and e.ISRETIRED: continue
        s += option(e["REASONNAME"],
            str(e["ID"]),
            int(e["ID"]) == selected)
    return s

def options_incident_types(dbo, includeAll = False, selected = -1, includeRetired = False):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    er = asm3.lookups.get_incident_types(dbo)
    for e in er:
        if not includeRetired and e.ISRETIRED: continue
        s += option(e["INCIDENTNAME"],
            str(e["ID"]),
            int(e["ID"]) == selected)
    return s

def options_internal_locations(dbo, includeAll = False, selected = -1, locationfilter = "", siteid = 0, includeRetired = False):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    lo = asm3.lookups.get_internal_locations(dbo, locationfilter, siteid)
    for l in lo:
        if not includeRetired and l.ISRETIRED: continue
        s += option(l["LOCATIONNAME"], 
            str(l["ID"]), 
            int(l["ID"]) == selected)
    return s

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
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    lt = asm3.lookups.get_log_types(dbo)
    for l in lt:
        if not includeRetired and l.ISRETIRED: continue
        s += option(l["LOGTYPENAME"], 
            str(l["ID"]), 
            int(l["ID"]) == selected)
    return s

def options_medicalprofiles(dbo, includeNone = False, selected = 0):
    s = ""
    if includeNone: s += option("", "0", False)
    mp = asm3.medical.get_profiles(dbo)
    for m in mp:
        s += option(m["PROFILENAME"], 
            str(m["ID"]), 
            int(m["ID"]) == selected)
    return s

def options_movement_types(dbo, includeAll = False, selected = -1):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    mt = asm3.lookups.get_movement_types(dbo)
    for m in mt:
        if m["ID"] != 9 and m["ID"] != 10 and m["ID"] != 11:
            s += option(m["MOVEMENTTYPE"], 
                str(m["ID"]), 
                int(m["ID"]) == selected)
    return s

def options_person_flags(dbo):
    s = ""
    l = dbo.locale
    pf = asm3.lookups.get_person_flags(dbo)
    s += option(_("ACO", l), "aco")
    s += option(_("Adopter", l), "adopter")
    s += option(_("Adoption Coordinator", l), "coordinator")
    s += option(_("Banned", l), "banned")
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
    for p in pf:
        s += option(p["FLAG"])
    return s

def options_people(dbo, includeAll = False, selected = -1):
    s = ""
    l = dbo.locale
    if includeAll: s += option(_("(all)", l), "-1", False)
    pp = asm3.person.get_person_name_addresses(dbo)
    for p in pp:
        s += option("%s - %s" % ( p["OWNERNAME"], p["OWNERADDRESS"] ), 
            str(p["ID"]), 
            int(p["ID"]) == selected)
    return s

def options_people_not_homechecked(dbo, includeAll = False, selected = -1):
    s = ""
    l = dbo.locale
    if includeAll: s += option(_("(all)", l), "-1", False)
    pp = asm3.person.get_reserves_without_homechecks(dbo)
    for p in pp:
        s += option("%s - %s" % ( p["OWNERNAME"], p["OWNERADDRESS"] ), 
            str(p["ID"]), 
            int(p["ID"]) == selected)
    return s

def options_posneg(dbo, includeAll = False, selected = -1):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    pn = asm3.lookups.get_posneg(dbo)
    for p in pn:
        s += option(p["NAME"],
            str(p["ID"]),
            int(p["ID"]) == selected)
    return s

def options_species(dbo, includeAll = False, selected = -1, includeRetired = False):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    sp = asm3.lookups.get_species(dbo)
    for sx in sp:
        if not includeRetired and sx.ISRETIRED: continue
        s += option(sx["SPECIESNAME"], 
            str(sx["ID"]), 
            int(sx["ID"]) == selected)
    return s

def options_sexes(dbo,  includeAll = False, selected = -1):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    se = asm3.lookups.get_sexes(dbo)
    for sx in se:
        s += option(sx["SEX"],
            str(sx["ID"]),
            int(sx["ID"]) == selected)
    return s

def options_sizes(dbo, includeAll = False, selected = -1):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    se = asm3.lookups.get_sizes(dbo)
    for sz in se:
        s += option(sz["SIZE"],
            str(sz["ID"]),
            int(sz["ID"]) == selected)
    return s

def options_sites(dbo, includeAll = False, selected = -1):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    se = asm3.lookups.get_sites(dbo)
    for i in se:
        s += option(i["SITENAME"], 
            str(i["ID"]), 
            int(i["ID"]) == selected)
    return s

def options_smarttagtypes(dbo, includeAll = False, selected = -1):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    st = [{ "ID" : 0, "TYPE" : _("Annual", l)},
          { "ID" : 1, "TYPE" : _("5 Year", l)},
          { "ID" : 2, "TYPE" : _("Lifetime", l)}]
    for t in st:
        s += option(t["TYPE"],
            str(t["ID"]),
            int(t["ID"]) == selected)
    return s

def options_urgencies(dbo, includeAll = False, selected = -1):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "all", False)
    wu = asm3.lookups.get_urgencies(dbo)
    for u in wu:
        s += option(u["URGENCY"],
            str(u["ID"]),
            int(u["ID"]) == selected)
    return s

def options_users(dbo, includeAll = False, selected = ""):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "all", selected == "all")
    su = asm3.users.get_users(dbo)
    for u in su:
        s += option(u["USERNAME"], u["USERNAME"], u["USERNAME"] == selected)
    return s

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
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    vt = asm3.lookups.get_vaccination_types(dbo)
    for v in vt:
        if not includeRetired and v.ISRETIRED: continue
        s += option(v["VACCINATIONTYPE"],
            str(v["ID"]),
            int(v["ID"]) == selected)
    return s

def options_voucher_types(dbo, includeAll = False, selected = -1, includeRetired = False):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    vt = asm3.lookups.get_voucher_types(dbo)
    for v in vt:
        if not includeRetired and v.ISRETIRED: continue
        s += option(v["VOUCHERNAME"],
            str(v["ID"]),
            int(v["ID"]) == selected)
    return s

def options_yesno(dbo, includeAll = False, selected = -1):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    yn = asm3.lookups.get_yesno(dbo)
    for y in yn:
        s += option(y["NAME"],
            str(y["ID"]),
            int(y["ID"]) == selected)
    return s
  
def options_ynun(dbo, includeAll = False, selected = -1):
    l = dbo.locale
    s = ""
    if includeAll: s += option(_("(all)", l), "-1", False)
    yn = asm3.lookups.get_ynun(dbo)
    for y in yn:
        s += option(y["NAME"],
            str(y["ID"]),
            int(y["ID"]) == selected)
    return s

def template_selection(templates, url):
    """
    templates: A list of templates pathnames
    url: The initial portion of the url
    """
    s = ""
    lastpath = ""
    for t in templates:
        if t["PATH"] != lastpath:
            s += "<li class=\"asm-menu-category\">%s</li>" % ( t["PATH"] )
            lastpath = t["PATH"]
        s += "<li class=\"asm-menu-item\"><a target=\"_blank\" class=\"templatelink\" data=\"%d\" href=\"%s&dtid=%s\">%s</a></li>" % (t["ID"], url, t["ID"], t["NAME"])
    return s

def timeline_rss(dbo, limit = 500):
    l = dbo.locale
    rows = asm3.animal.get_timeline(dbo, limit)
    h = []
    for r in rows:
        h.append( rss_item( r["DESCRIPTION"], "%s/%s?id=%d" % (BASE_URL, r["LINKTARGET"], r["ID"]), "") )
    return rss("\n".join(h), _("Showing {0} timeline events.", l).format(limit), BASE_URL, "")

def report_criteria(dbo, crit, locationfilter = "", siteid = 0):
    """
    Renders report criteria as an HTML form
    crit: The criteria - a list of tuples containing name, type and a question
    locationfilter: A comma separated list of location ids for filtering the internal location list
    """
    l = dbo.locale
    s = "<table>"
    for name, rtype, question in crit:
        if rtype == "DATE":
            s += """
            <tr>
            <td>%s</td>
            <td>
            <input class="asm-textbox asm-datebox" id="report-%s" data-post="%s" value="%s" />
            </td>
            </tr>""" % ( question, name, name, python2display(l, now(dbo.timezone)) )
        elif rtype == "STRING":
            s += """
            <tr>
            <td>%s</td>
            <td>
            <input class="asm-textbox" id="report-%s" data-post="%s" />
            </td>
            </tr>""" % ( question, name, name )
        elif rtype == "NUMBER":
            s += """
            <tr>
            <td>%s</td>
            <td>
            <input class="asm-textbox asm-numberbox" id="report-%s" data-post="%s" />
            </td>
            </tr>""" % ( question, name, name )
        elif rtype == "ANIMAL" or rtype == "FSANIMAL" or rtype == "ALLANIMAL":
            s += """
            <tr>
            <td>%s</td>
            <td>
            <input class="asm-animalchooser" id="report-%s" data-post="%s" type="hidden" />
            </td>
            </tr>""" % ( _("Animal", l), name, name )
        elif rtype == "ANIMALS":
            s += """
            <tr>
            <td>%s</td>
            <td>
            <input class="asm-animalchoosermulti" id="report-%s" data-post="%s" type="hidden" />
            </td>
            </tr>""" % ( _("Animals", l), name, name )
        elif rtype == "ANIMALFLAG":
            s += """
            <tr>
            <td>%s</td>
            <td>
            <select class="asm-selectbox" id="report-%s" data-post="%s">
            %s
            </select>
            </td>
            </tr>""" % ( _("Flag", l), name, name, options_animal_flags(dbo))
        elif rtype == "PERSON":
            s += """
            <tr>
            <td>%s</td>
            <td>
            <input class="asm-personchooser" id="report-%s" data-post="%s" type="hidden" />
            </td>
            </tr>""" % ( _("Person", l), name, name )
        elif rtype == "PERSONFLAG":
            s += """
            <tr>
            <td>%s</td>
            <td>
            <select class="asm-selectbox" id="report-%s" data-post="%s">
            %s
            </select>
            </td>
            </tr>""" % ( _("Flag", l), name, name, options_person_flags(dbo))
        elif rtype == "DONATIONTYPE":
            s += """
            <tr>
            <td>%s</td>
            <td>
            <select class="asm-selectbox" id="report-%s" data-post="%s">
            %s
            </select>
            </td>
            </tr>""" % ( _("Payment Type", l), name, name, options_donation_types(dbo) )
        elif rtype == "LITTER":
            s += """
            <tr>
            <td>%s</td>
            <td>
            <select class="asm-selectbox" id="report-%s" data-post="%s">
            %s
            </select>
            </td>
            </tr>""" % ( _("Litter", l), name, name, options_litters(dbo) )
        elif rtype == "SPECIES":
            s += """
            <tr>
            <td>%s</td>
            <td>
            <select class="asm-selectbox" id="report-%s" data-post="%s">
            %s
            </select>
            </td>
            </tr>""" % ( _("Species", l), name, name, options_species(dbo) )
        elif rtype == "LOCATION":
            s += """
            <tr>
            <td>%s</td>
            <td>
            <select class="asm-selectbox" id="report-%s" data-post="%s">
            %s
            </select>
            </td>
            </tr>""" % ( _("Location", l), name, name, options_internal_locations(dbo, False, -1, locationfilter, siteid) )
        elif rtype == "LOGTYPE":
            s += """
            <tr>
            <td>%s</td>
            <td>
            <select class="asm-selectbox" id="report-%s" data-post="%s">
            %s
            </select>
            </td>
            </tr>""" % ( _("Log Type", l), name, name, options_log_types(dbo, False, -1) )
        elif rtype == "SITE":
            s += """
            <tr>
            <td>%s</td>
            <td>
            <select class="asm-selectbox" id="report-%s" data-post="%s">
            %s
            </select>
            </td>
            </tr>""" % ( _("Site", l), name, name, options_sites(dbo, False, -1) )
        elif rtype == "TYPE":
            s += """
            <tr>
            <td>%s</td>
            <td>
            <select class="asm-selectbox" id="report-%s" data-post="%s">
            %s
            </select>
            </td>
            </tr>""" % ( _("Type", l), name, name, options_animal_types(dbo) )
    s += "<tr><td></td><td><button id=\"submitcriteria\">%s</button></td></tr></table>" % _("Generate", l)
    return s

def report_criteria_mobile(dbo, crit, locationfilter = "", siteid = 0):
    """
    l: The locale
    crit: The criteria - a list of tuples containing name, type and a question
    """
    l = dbo.locale
    s = ""
    for name, rtype, question in crit:
        if rtype == "DATE":
            s += """
            <div data-role=\"fieldcontain\"><label for=\"%s\">%s</label>
            <input type="date" id="report-%s" data-post="%s" value="%s" />
            </div>
            """ % (name, question, name, name, format_date(now(dbo.timezone), "%Y-%m-%d"))
        elif rtype == "STRING":
            s += """
            <div data-role=\"fieldcontain\"><label for=\"%s\">%s</label>
            <input type="text" id="report-%s" data-post="%s" value="" />
            </div>
            """ % (name, question, name, name)
        elif rtype == "NUMBER":
            s += """
            <div data-role=\"fieldcontain\"><label for=\"%s\">%s</label>
            <input type="number" id="report-%s" data-post="%s" value="" />
            </div>
            """ % (name, question, name, name)
        elif rtype == "ANIMAL":
            s += """
            <div data-role=\"fieldcontain\"><label for=\"%s\">%s</label>
            <select id="report-%s" data-post="%s">%s</select>
            </div>
            """ % (name, _("Animal", l), name, name, options_animals_on_shelter(dbo))
        elif rtype == "FSANIMAL":
            s += """
            <div data-role=\"fieldcontain\"><label for=\"%s\">%s</label>
            <select id="report-%s" data-post="%s">%s</select>
            </div>
            """ % (name, _("Animal", l), name, name, options_animals_on_shelter_foster(dbo))
        elif rtype == "ALLANIMAL":
            s += """
            <div data-role=\"fieldcontain\"><label for=\"%s\">%s</label>
            <select id="report-%s" data-post="%s">%s</select>
            </div>
            """ % (name, _("Animal", l), name, name, options_animals(dbo))
        elif rtype == "ANIMALS":
            s += """
            <div data-role=\"fieldcontain\"><label for=\"%s\">%s</label>
            <select multiple=\"multiple\" id="report-%s" data-post="%s">%s</select>
            </div>
            """ % (name, _("Animals", l), name, name, options_animals_on_shelter(dbo))
        elif rtype == "ANIMALFLAG":
            s += """
            <div data-role=\"fieldcontain\"><label for=\"%s\">%s</label>
            <select id="report-%s" data-post="%s">%s</select>
            </div>
            """ % (name, _("Flag", l), name, name, options_animal_flags(dbo))
        elif rtype == "PERSON":
            s += """
            <div data-role=\"fieldcontain\"><label for=\"%s\">%s</label>
            <select id="report-%s" data-post="%s">%s</select>
            </div>
            """ % (name, _("Person", l), name, name, options_people(dbo))
        elif rtype == "PERSONFLAG":
            s += """
            <div data-role=\"fieldcontain\"><label for=\"%s\">%s</label>
            <select id="report-%s" data-post="%s">%s</select>
            </div>
            """ % (name, _("Flag", l), name, name, options_person_flags(dbo))
        elif rtype == "DONATIONTYPE":
            s += """
            <div data-role=\"fieldcontain\"><label for=\"%s\">%s</label>
            <select id="report-%s" data-post="%s">%s</select>
            </div>
            """ % (name, _("Payment Type", l), name, name, options_donation_types(dbo))
        elif rtype == "LITTER":
            s += """
            <div data-role=\"fieldcontain\"><label for=\"%s\">%s</label>
            <select id="report-%s" data-post="%s">%s</select>
            </div>
            """ % (name, _("Litter", l), name, name, options_litters(dbo))
        elif rtype == "SPECIES":
            s += """
            <div data-role=\"fieldcontain\"><label for=\"%s\">%s</label>
            <select id="report-%s" data-post="%s">%s</select>
            </div>
            """ % (name, _("Species", l), name, name, options_species(dbo))
        elif rtype == "LOCATION":
            s += """
            <div data-role=\"fieldcontain\"><label for=\"%s\">%s</label>
            <select id="report-%s" data-post="%s">%s</select>
            </div>
            """ % (name, _("Location", l), name, name, options_internal_locations(dbo, False, -1, locationfilter, siteid))
        elif rtype == "LOGTYPE":
            s += """
            <div data-role=\"fieldcontain\"><label for=\"%s\">%s</label>
            <select id="report-%s" data-post="%s">%s</select>
            </div>
            """ % (name, _("Log Type", l), name, name, options_log_types(dbo, False, -1))
        elif rtype == "SITE":
            s += """
            <div data-role=\"fieldcontain\"><label for=\"%s\">%s</label>
            <select id="report-%s" data-post="%s">%s</select>
            </div>
            """ % (name, _("Site", l), name, name, options_sites(dbo, False, -1))
        elif rtype == "TYPE":
            s += """
            <div data-role=\"fieldcontain\"><label for=\"%s\">%s</label>
            <select id="report-%s" data-post="%s">%s</select>
            </div>
            """ % (name, _("Type", l), name, name, options_animal_types(dbo))
    s += "<input id=\"submitcriteria\" type=\"submit\" value=\"%s\" />" % _("Generate", l)
    return s

