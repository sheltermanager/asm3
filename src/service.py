#!/usr/bin/python

"""
Service functions for external applications.

An account, username and password is mandatory for
sheltermanager accounts, username and password
for others.
"""

import al
import animal
import cachedisk
import cachemem
import configuration
import db
import dbfs
import dbupdate
import html
import media
import lostfound
import movement
import onlineform
import publishers.base
import publishers.html
import reports
import smcom
import users
import utils
from i18n import _
from sitedefs import JQUERY_JS, JQUERY_UI_JS, MOMENT_JS, SIGNATURE_JS, TOUCHPUNCH_JS
from sitedefs import BASE_URL, MULTIPLE_DATABASES, MULTIPLE_DATABASES_TYPE, CACHE_SERVICE_RESPONSES, IMAGE_HOTLINKING_ONLY_FROM_DOMAIN

# Service methods that require authentication
AUTH_METHODS = [
    "csv_mail", "csv_report", "html_report", "rss_timeline", "upload_animal_image",
    "xml_adoptable_animal", "json_adoptable_animal",
    "xml_adoptable_animals", "json_adoptable_animals", "jsonp_adoptable_animals",
    "xml_found_animals", "json_found_animals", "jsonp_found_animals",
    "xml_lost_animals", "json_lost_animals", "jsonp_lost_animals",
    "xml_recent_adoptions", "json_recent_adoptions", "jsonp_recent_adoptions",
    "xml_shelter_animals", "json_shelter_animals", "jsonp_shelter_animals",
    "xml_recent_changes", "json_recent_changes", "jsonp_recent_changes"
]

def flood_protect(method, remoteip, ttl, message = ""):
    """ Checks to see if we've had a request for method from remoteip since ttl seconds ago.
    If we haven't, we record this as the last time we saw a request
    from this ip address for that method. Otherwise, an error is thrown.
    method: The service method we're protecting
    remoteip: The ip address of the caller
    ttl: The protection period (one request per ttl seconds)
    """
    cache_key = "m%sr%s" % (method, str(remoteip).replace(", ", "")) # X-FORWARDED-FOR can be a list, remove commas
    v = cachemem.get(cache_key)
    #al.debug("method: %s, remoteip: %s, ttl: %d, cacheval: %s" % (method, remoteip, ttl, v), "service.flood_protect")
    if v is None:
        cachemem.put(cache_key, "x", ttl)
    else:
        if message == "":
            message = "You have already called '%s' in the last %d seconds, please wait before trying again." % (method, ttl)
        raise utils.ASMError(message)

def hotlink_protect(method, referer):
    """ Protect a method from having any referer other than the one we set """
    domains = IMAGE_HOTLINKING_ONLY_FROM_DOMAIN.split(",")
    fromhldomain = False
    for d in domains:
        if d != "" and referer.find(d) != -1: fromhldomain = True
    if referer != "" and IMAGE_HOTLINKING_ONLY_FROM_DOMAIN != "" and not fromhldomain:
        raise utils.ASMPermissionError("Hotlinking to %s from %s is forbidden" % (method, referer))

def get_cached_response(cache_key):
    """ Gets a service call response from the cache based on its key.
    If no entry is found, None is returned.
    """
    if not CACHE_SERVICE_RESPONSES: return None
    response = cachedisk.get(cache_key)
    if response is None: return None
    #al.debug("GET: %s (%d bytes)" % (cache_key, len(response[2])), "service.get_cached_response")
    return response

def set_cached_response(cache_key, mime, clientage, serverage, content):
    """ Sets a service call response in the cache and returns it
    methods can use this as a passthrough to return the response.
    cache_key: The constructed cache key from the parameters
    mime: The mime type to return in the response
    clientage: The max-age to set for the client to cache the response (seconds)
    serverage: The ttl for storing in our server cache (seconds)
    content: The response
    """
    response = (mime, clientage, content)
    if not CACHE_SERVICE_RESPONSES: return response
    #al.debug("PUT: %s (%d bytes)" % (cache_key, len(content)), "service.set_cached_response")
    cachedisk.put(cache_key, response, serverage)
    return response

def sign_document_page(dbo, mid):
    """ Outputs a page that allows signing of document with media id mid"""
    l = dbo.locale
    if media.has_signature(dbo, mid):
        return "<!DOCTYPE html><head><title>%s</title></head>" \
            "<body><p>%s</p></body></html>" % \
            ( _("Already Signed", l), _("Sorry, this document has already been signed", l))
    h = []
    h.append("""<!DOCTYPE html>
    <html>
    <head>
    <title>
    %(title)s
    </title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    %(css)s
    %(scripts)s
    <script type="text/javascript">
        $(document).ready(function() {
            $("#signature").signature({ guideline: true });
            $("#sig-clear").click(function() {
                $("#signature").signature("clear");
            });
            $("#sig-sign").click(function() {
                var img = $("#signature canvas").get(0).toDataURL("image/png");
                var formdata = "account=%(account)s&method=sign_document&formid=%(id)s&sig=" + encodeURIComponent(img);
                formdata += "&signdate=" + encodeURIComponent(moment().format("YYYY-MM-DD HH:mm:ss"));
                if ($("#signature").signature("isEmpty")) {
                    alert("Signature is required");
                    return;
                }
                $.ajax({
                    type: "POST",
                    url: "service",
                    data: formdata,
                    dataType: "text",
                    mimeType: "textPlain",
                    success: function(response) {
                        $("body").empty().append("<p>%(thankyou)s</p>");
                    },
                    error: function(jqxhr, textstatus, response) {
                        $("body").append("<p>" + response + "</p>");
                    }
                });
            });
            $("#reviewlink").click(function() {
                $("#reviewlink").fadeOut();
                $("#review").slideDown();
            });
        });
    </script>
    <style>
    button {
        padding: 10px;
        font-size: 100%%;
    }
    #signature {
        border: 1px solid #aaa;
        height: 200px;
        width: 100%%;
        max-width: 500px;
    }
    </style>
    </head>
    <body>
    """ % {
        "title":    _("Signing Pad", l),
        "id":       mid,
        "account":  dbo.database,
        "css":      html.asm_css_tag("asm-icon.css"),
        "thankyou": _("Thank you, the document is now signed.", l),
        "scripts":  html.script_tag(JQUERY_JS) + html.script_tag(JQUERY_UI_JS) +
                    html.script_tag(TOUCHPUNCH_JS) + html.script_tag(SIGNATURE_JS) + html.script_tag(MOMENT_JS)
    })
    d = []
    docnotes = []
    docnotes.append(media.get_notes_for_id(dbo, int(mid)))
    mdate, medianame, mimetype, contents = media.get_media_file_data(dbo, int(mid))
    d.append(contents)
    d.append("<hr />")
    h.append("<p><b>%s: %s</b></p>" % (_("Signing", l), ", ".join(docnotes)))
    h.append('<p><a id="reviewlink" href="#">%s</a></p>' % _("View Document", l))
    h.append('<div id="review" style="display: none">')
    h.append("\n".join(d))
    h.append('</div>')
    h.append('<div id="signature"></div>')
    h.append('<p>')
    h.append('<button id="sig-clear" type="button">' + _("Clear", l) + '</button>')
    h.append('<button id="sig-sign" type="button">' + _("Sign", l) + '</button>')
    h.append('</p>')
    h.append('<p>')
    h.append(_("Please click the Sign button when you are finished.", l))
    h.append('</p>')
    h.append('<p>')
    h.append(_("Once signed, this document cannot be edited or tampered with.", l))
    h.append('</p>')
    h.append("</body></html>")
    return "\n".join(h)

def handler(post, path, remoteip, referer, querystring):
    """ Handles the various service method types.
    post:        The GET/POST parameters
    path:        The current system path/code.PATH
    remoteip:    The IP of the caller
    referer:     The referer HTTP header
    querystring: The complete querystring
    return value is a tuple containing MIME type, max-age, content
    """
    # Database info
    dbo = db.get_database()

    # Get service parameters
    account = post["account"]
    username = post["username"]
    password = post["password"]
    method = post["method"]
    animalid = post.integer("animalid")
    formid = post.integer("formid")
    seq = post.integer("seq")
    title = post["title"]

    cache_key = querystring.replace(" ", "")

    # Do we have a cached response for these parameters?
    cached_response = get_cached_response(cache_key)
    if cached_response is not None:
        al.debug("cache hit for %s" % (cache_key), "service.handler")
        return cached_response

    # Are we dealing with multiple databases, but no account was specified?
    if account == "" and MULTIPLE_DATABASES:
        return ("text/plain", 0, "ERROR: No database/alias specified")

    # Are we dealing with multiple databases and an account was specified?
    if account != "":
        if MULTIPLE_DATABASES:
            if MULTIPLE_DATABASES_TYPE == "smcom":
                # Is this sheltermanager.com? If so, we need to get the
                # database connection info (dbo) before we can login.
                dbo = smcom.get_database_info(account)
            else:
                # Look up the database info from our map
                dbo  = db.get_multiple_database_info(account)
            if dbo.database in ( "FAIL", "DISABLED", "WRONGSERVER" ):
                al.error("auth failed - invalid smaccount %s from %s (%s)" % (account, remoteip, dbo.database), "service.handler", dbo)
                return ("text/plain", 0, "ERROR: Invalid database (%s)" % dbo.database)

    # If the database has disabled the service API, stop now
    if not configuration.service_enabled(dbo):
        al.error("Service API is disabled (%s)" % method, "service.handler", dbo)
        return ("text/plain", 0, "ERROR: Service API is disabled")

    # Do any database updates need doing in this db?
    dbo.installpath = path
    if dbupdate.check_for_updates(dbo):
        dbupdate.perform_updates(dbo)

    # Does the method require us to authenticate? If so, do it.
    user = None
    securitymap = ""
    if method in AUTH_METHODS:
        # If the database has authenticated service methods disabled, stop now
        if not configuration.service_auth_enabled(dbo):
            al.error("Service API for auth methods is disabled (%s)" % method, "service.handler", dbo)
            return ("text/plain", 0, "ERROR: Service API for authenticated methods is disabled")
        user = users.authenticate(dbo, username, password)
        if user is None:
            al.error("auth failed - %s/%s is not a valid username/password from %s" % (username, password, remoteip), "service.handler", dbo)
            return ("text/plain", 0, "ERROR: Invalid username and password")
        securitymap = users.get_security_map(dbo, user["USERNAME"])

    # Get the preferred locale and timezone for the site
    l = configuration.locale(dbo)
    dbo.locale = l
    dbo.timezone = configuration.timezone(dbo)
    al.info("call %s->%s [%s %s]" % (username, method, str(animalid), title), "service.handler", dbo)

    if method =="animal_image":
        hotlink_protect("animal_image", referer)
        if utils.cint(animalid) == 0:
            al.error("animal_image failed, %s is not an animalid" % str(animalid), "service.handler", dbo)
            return ("text/plain", 0, "ERROR: Invalid animalid")
        else:
            mediadate, data = media.get_image_file_data(dbo, "animal", utils.cint(animalid), seq)
            if data == "NOPIC": mediadate, data = media.get_image_file_data(dbo, "nopic", 0)
            return set_cached_response(cache_key, "image/jpeg", 86400, 3600, data)

    elif method =="animal_thumbnail":
        if utils.cint(animalid) == 0:
            al.error("animal_thumbnail failed, %s is not an animalid" % str(animalid), "service.handler", dbo)
            return ("text/plain", 0, "ERROR: Invalid animalid")
        else:
            mediadate, data = media.get_image_file_data(dbo, "animalthumb", utils.cint(animalid), seq)
            if data == "NOPIC": mediadate, data = media.get_image_file_data(dbo, "nopic", 0)
            return set_cached_response(cache_key, "image/jpeg", 86400, 86400, data)

    elif method == "animal_view":
        if utils.cint(animalid) == 0:
            al.error("animal_view failed, %s is not an animalid" % str(animalid), "service.handler", dbo)
            return ("text/plain", 0, "ERROR: Invalid animalid")
        else:
            return set_cached_response(cache_key, "text/html", 120, 120, publishers.html.get_animal_view(dbo, utils.cint(animalid)))

    elif method == "animal_view_adoptable_js":
        return set_cached_response(cache_key, "application/javascript", 600, 600, publishers.html.get_animal_view_adoptable_js(dbo))

    elif method == "animal_view_adoptable_html":
        return set_cached_response(cache_key, "text/html", 120, 120, publishers.html.get_animal_view_adoptable_html(dbo))

    elif method =="dbfs_image":
        hotlink_protect("dbfs_image", referer)
        return set_cached_response(cache_key, "image/jpeg", 86400, 86400, utils.iif(title.startswith("/"),
            dbfs.get_string_filepath(dbo, title), dbfs.get_string(dbo, title)))

    elif method =="extra_image":
        hotlink_protect("extra_image", referer)
        return set_cached_response(cache_key, "image/jpeg", 86400, 86400, dbfs.get_string(dbo, title, "/reports"))

    elif method == "json_adoptable_animal":
        if utils.cint(animalid) == 0:
            al.error("json_adoptable_animal failed, %s is not an animalid" % str(animalid), "service.handler", dbo)
            return ("text/plain", 0, "ERROR: Invalid animalid")
        else:
            users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
            rs = publishers.base.get_animal_data(dbo, None, utils.cint(animalid), include_additional_fields = True)
            return set_cached_response(cache_key, "application/json", 3600, 3600, utils.json(rs))

    elif method == "html_adoptable_animals":
        return set_cached_response(cache_key, "text/html", 1800, 1800, \
            publishers.html.get_adoptable_animals(dbo, style=post["template"], \
                speciesid=post.integer("speciesid"), animaltypeid=post.integer("animaltypeid")))

    elif method == "json_adoptable_animals":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        rs = publishers.base.get_animal_data(dbo, None, include_additional_fields = True)
        return set_cached_response(cache_key, "application/json", 3600, 3600, utils.json(rs))

    elif method == "jsonp_adoptable_animals":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        rs = publishers.base.get_animal_data(dbo, None, include_additional_fields = True)
        return ("application/javascript", 0, "%s(%s);" % (post["callback"], utils.json(rs)))

    elif method == "xml_adoptable_animal":
        if utils.cint(animalid) == 0:
            al.error("xml_adoptable_animal failed, %s is not an animalid" % str(animalid), "service.handler", dbo)
            return ("text/plain", 0, "ERROR: Invalid animalid")
        else:
            users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
            rs = publishers.base.get_animal_data(dbo, None, utils.cint(animalid), include_additional_fields = True)
            return set_cached_response(cache_key, "application/xml", 3600, 3600, html.xml(rs))

    elif method == "xml_adoptable_animals":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        rs = publishers.base.get_animal_data(dbo, None, include_additional_fields = True)
        return set_cached_response(cache_key, "application/xml", 3600, 3600, html.xml(rs))

    elif method == "json_found_animals":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_FOUND_ANIMAL)
        rs = lostfound.get_foundanimal_last_days(dbo)
        return set_cached_response(cache_key, "application/json", 3600, 3600, utils.json(rs))

    elif method == "jsonp_found_animals":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_FOUND_ANIMAL)
        rs = lostfound.get_foundanimal_last_days(dbo)
        return ("application/javascript", 0, "%s(%s);" % (post["callback"], utils.json(rs)))

    elif method == "xml_found_animals":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_FOUND_ANIMAL)
        rs = lostfound.get_foundanimal_last_days(dbo)
        return set_cached_response(cache_key, "application/json", 3600, 3600, html.xml(rs))

    elif method == "json_lost_animals":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_LOST_ANIMAL)
        rs = lostfound.get_lostanimal_last_days(dbo)
        return set_cached_response(cache_key, "application/json", 3600, 3600, utils.json(rs))

    elif method == "jsonp_lost_animals":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_LOST_ANIMAL)
        rs = lostfound.get_lostanimal_last_days(dbo)
        return ("application/javascript", 0, "%s(%s);" % (post["callback"], utils.json(rs)))

    elif method == "xml_lost_animals":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_LOST_ANIMAL)
        rs = lostfound.get_lostanimal_last_days(dbo)
        return set_cached_response(cache_key, "application/json", 3600, 3600, html.xml(rs))

    elif method == "json_recent_adoptions":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        rs = movement.get_recent_adoptions(dbo)
        return set_cached_response(cache_key, "application/json", 3600, 3600, utils.json(rs))

    elif method == "jsonp_recent_adoptions":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        rs = movement.get_recent_adoptions(dbo)
        return ("application/javascript", 0, "%s(%s);" % (post["callback"], utils.json(rs)))

    elif method == "xml_recent_adoptions":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        rs = movement.get_recent_adoptions(dbo)
        return set_cached_response(cache_key, "application/xml", 3600, 3600, html.xml(rs))

    elif method == "html_report":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_REPORT)
        crid = reports.get_id(dbo, title)
        p = reports.get_criteria_params(dbo, crid, post)
        rhtml = reports.execute(dbo, crid, username, p)
        return set_cached_response(cache_key, "text/html", 600, 600, rhtml)

    elif method == "csv_mail" or method == "csv_report":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_REPORT)
        crid = reports.get_id(dbo, title)
        p = reports.get_criteria_params(dbo, crid, post)
        rows, cols = reports.execute_query(dbo, crid, username, p)
        mcsv = utils.csv(l, rows, cols, True)
        return set_cached_response(cache_key, "text/csv", 600, 600, mcsv)

    elif method == "jsonp_recent_changes":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        sa = animal.get_recent_changes(dbo)
        return ("application/javascript", 0, "%s(%s);" % (post["callback"], utils.json(sa)))

    elif method == "json_recent_changes":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        sa = animal.get_recent_changes(dbo)
        return set_cached_response(cache_key, "application/json", 3600, 3600, utils.json(sa))

    elif method == "xml_recent_changes":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        sa = animal.get_recent_changes(dbo)
        return set_cached_response(cache_key, "application/xml", 3600, 3600, html.xml(sa))

    elif method == "jsonp_shelter_animals":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        sa = animal.get_shelter_animals(dbo)
        return ("application/javascript", 0, "%s(%s);" % (post["callback"], utils.json(sa)))

    elif method == "json_shelter_animals":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        sa = animal.get_shelter_animals(dbo)
        return set_cached_response(cache_key, "application/json", 3600, 3600, utils.json(sa))

    elif method == "xml_shelter_animals":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        sa = animal.get_shelter_animals(dbo)
        return set_cached_response(cache_key, "application/xml", 3600, 3600, html.xml(sa))

    elif method == "rss_timeline":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        return set_cached_response(cache_key, "application/rss+xml", 3600, 3600, html.timeline_rss(dbo))

    elif method == "upload_animal_image":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.ADD_MEDIA)
        media.attach_file_from_form(dbo, username, media.ANIMAL, int(animalid), post)
        return ("text/plain", 0, "OK")

    elif method == "online_form_html":
        if formid == 0:
            raise utils.ASMError("method online_form_html requires a valid formid")
        return set_cached_response(cache_key, "text/html; charset=utf-8", 120, 120, onlineform.get_onlineform_html(dbo, formid))

    elif method == "online_form_json":
        if formid == 0:
            raise utils.ASMError("method online_form_json requires a valid formid")
        return set_cached_response(cache_key, "text/json; charset=utf-8", 30, 30, onlineform.get_onlineform_json(dbo, formid))

    elif method == "online_form_post":
        flood_protect("online_form_post", remoteip, 15)
        onlineform.insert_onlineformincoming_from_form(dbo, post, remoteip)
        redirect = post["redirect"]
        if redirect == "":
            redirect = BASE_URL + "/static/pages/form_submitted.html"
        return ("redirect", 0, redirect)

    elif method == "sign_document":
        if formid == 0:
            raise utils.ASMError("method sign_document requires a valid formid")
        if post["sig"] == "":
            return set_cached_response(cache_key, "text/html", 2, 2, sign_document_page(dbo, formid))
        else:
            media.sign_document(dbo, "service", formid, post["sig"], post["signdate"])
            return ("text/plain", 0, "OK")

    else:
        al.error("invalid method '%s'" % method, "service.handler", dbo)
        raise utils.ASMError("Invalid method '%s'" % method)

