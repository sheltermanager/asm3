
"""
Service functions for external applications.

An account, username and password is mandatory for
sheltermanager accounts, username and password
for others.
"""

import asm3.al
import asm3.animal
import asm3.cachedisk
import asm3.configuration
import asm3.db
import asm3.dbfs
import asm3.dbupdate
import asm3.html
import asm3.media
import asm3.lostfound
import asm3.movement
import asm3.onlineform
import asm3.publishers.base
import asm3.publishers.html
import asm3.reports
import asm3.users
import asm3.utils
from asm3.i18n import _
from asm3.sitedefs import JQUERY_JS, JQUERY_UI_JS, MOMENT_JS, SIGNATURE_JS, TOUCHPUNCH_JS
from asm3.sitedefs import BASE_URL, MULTIPLE_DATABASES, CACHE_SERVICE_RESPONSES, IMAGE_HOTLINKING_ONLY_FROM_DOMAIN

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

def flood_protect(method, account, remoteip, ttl, message = ""):
    """ Checks to see if we've had a request for method from remoteip since ttl seconds ago.
    If we haven't, we record this as the last time we saw a request
    from this ip address for that method. Otherwise, an error is thrown.
    method: The service method we're protecting
    remoteip: The ip address of the caller
    ttl: The protection period (one request per ttl seconds)
    """
    cache_key = "m%sr%s" % (method, str(remoteip).replace(", ", "")) # X-FORWARDED-FOR can be a list, remove commas
    v = asm3.cachedisk.get(cache_key, account)
    asm3.al.debug("method: %s, remoteip: %s, ttl: %d, cacheval: %s" % (method, remoteip, ttl, v), "service.flood_protect")
    if v is None:
        asm3.cachedisk.put(cache_key, account, "x", ttl)
    else:
        if message == "":
            message = "You have already called '%s' in the last %d seconds, please wait before trying again." % (method, ttl)
        raise asm3.utils.ASMError(message)

def hotlink_protect(method, referer):
    """ Protect a method from having any referer other than the one we set """
    domains = IMAGE_HOTLINKING_ONLY_FROM_DOMAIN.split(",")
    fromhldomain = False
    for d in domains:
        if d != "" and referer.find(d) != -1: fromhldomain = True
    if referer != "" and IMAGE_HOTLINKING_ONLY_FROM_DOMAIN != "" and not fromhldomain:
        raise asm3.utils.ASMPermissionError("Hotlinking to %s from %s is forbidden" % (method, referer))

def get_cached_response(cache_key, path):
    """ Gets a service call response from the cache based on its key.
    If no entry is found, None is returned.
    """
    if not CACHE_SERVICE_RESPONSES: return None
    response = asm3.cachedisk.get(cache_key, path)
    if response is None or len(response) != 4: return None
    asm3.al.debug("GET: %s (%d bytes)" % (cache_key, len(response[3])), "service.get_cached_response")
    return response

def set_cached_response(cache_key, path, mime, clientage, serverage, content):
    """ Sets a service call response in the cache and returns it
    methods can use this as a passthrough to return the response.
    cache_key: The constructed cache key from the parameters
    mime: The mime type to return in the response
    clientage: The max-age to set for the client to cache the response (seconds)
    serverage: The ttl for storing in our server cache (seconds)
    content: The response
    """
    response = (mime, clientage, serverage, content)
    if not CACHE_SERVICE_RESPONSES: return response
    asm3.al.debug("PUT: %s (%d bytes)" % (cache_key, len(content)), "service.set_cached_response")
    asm3.cachedisk.put(cache_key, path, response, serverage)
    return response

def sign_document_page(dbo, mid):
    """ Outputs a page that allows signing of document with media id mid"""
    l = dbo.locale
    if asm3.media.has_signature(dbo, mid):
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
        "css":      asm3.html.asm_css_tag("asm-icon.css"),
        "thankyou": _("Thank you, the document is now signed.", l),
        "scripts":  asm3.html.script_tag(JQUERY_JS) + asm3.html.script_tag(JQUERY_UI_JS) +
                    asm3.html.script_tag(TOUCHPUNCH_JS) + asm3.html.script_tag(SIGNATURE_JS) + asm3.html.script_tag(MOMENT_JS)
    })
    d = []
    docnotes = []
    docnotes.append(asm3.media.get_notes_for_id(dbo, int(mid)))
    dummy, dummy, dummy, contents = asm3.media.get_media_file_data(dbo, int(mid))
    d.append(asm3.utils.bytes2str(contents))
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

def strip_personal_data(rows):
    """ Removes any personal data from animal rows 
        include_current: If False, strips CURRENTOWNER tokens (typically foster for shelter animals)
    """
    for r in rows:
        for k in r.keys():
            if k.startswith("CURRENTOWNER") or k.startswith("ORIGINALOWNER") or k.startswith("BROUGHTINBY") or k.startswith("RESERVEDOWNER"):
                r[k] = ""
    return rows

def handler(post, path, remoteip, referer, querystring):
    """ Handles the various service method types.
    post:        The GET/POST parameters
    path:        The current system path/code.PATH
    remoteip:    The IP of the caller
    referer:     The referer HTTP header
    querystring: The complete querystring
    return value is a tuple containing MIME type, max-age, content
    """
    # Get service parameters
    account = post["account"]
    username = post["username"]
    password = post["password"]
    method = post["method"]
    animalid = post.integer("animalid")
    formid = post.integer("formid")
    seq = post.integer("seq")
    title = post["title"]
    strip_personal = post.integer("sensitive") == 0

    cache_key = querystring.replace(" ", "")

    # Do we have a cached response for these parameters?
    cached_response = get_cached_response(cache_key, account)
    if cached_response is not None:
        asm3.al.debug("cache hit for %s" % (cache_key), "service.handler")
        return cached_response

    # Are we dealing with multiple databases, but no account was specified?
    if account == "" and MULTIPLE_DATABASES:
        return ("text/plain", 0, 0, "ERROR: No database/alias specified")

    dbo = asm3.db.get_database(account)

    if dbo.database in asm3.db.ERROR_VALUES:
        asm3.al.error("auth failed - invalid smaccount %s from %s (%s)" % (account, remoteip, dbo.database), "service.handler", dbo)
        return ("text/plain", 0, 0, "ERROR: Invalid database (%s)" % dbo.database)

    # If the database has disabled the service API, stop now
    if not asm3.configuration.service_enabled(dbo):
        asm3.al.error("Service API is disabled (%s)" % method, "service.handler", dbo)
        return ("text/plain", 0, 0, "ERROR: Service API is disabled")

    # Do any database updates need doing in this db?
    dbo.installpath = path
    if asm3.dbupdate.check_for_updates(dbo):
        asm3.dbupdate.perform_updates(dbo)

    # Does the method require us to authenticate? If so, do it.
    user = None
    securitymap = ""
    if method in AUTH_METHODS:
        # If the database has authenticated service methods disabled, stop now
        if not asm3.configuration.service_auth_enabled(dbo):
            asm3.al.error("Service API for auth methods is disabled (%s)" % method, "service.handler", dbo)
            return ("text/plain", 0, 0, "ERROR: Service API for authenticated methods is disabled")
        user = asm3.users.authenticate(dbo, username, password)
        if user is None:
            asm3.al.error("auth failed - %s/%s is not a valid username/password from %s" % (username, password, remoteip), "service.handler", dbo)
            return ("text/plain", 0, 0, "ERROR: Invalid username and password")
        securitymap = asm3.users.get_security_map(dbo, user["USERNAME"])

    # Get the preferred locale and timezone for the site
    l = asm3.configuration.locale(dbo)
    dbo.locale = l
    dbo.timezone = asm3.configuration.timezone(dbo)
    asm3.al.info("call %s->%s [%s %s]" % (username, method, str(animalid), title), "service.handler", dbo)

    if method =="animal_image":
        hotlink_protect("animal_image", referer)
        if asm3.utils.cint(animalid) == 0:
            asm3.al.error("animal_image failed, %s is not an animalid" % str(animalid), "service.handler", dbo)
            return ("text/plain", 0, 0, "ERROR: Invalid animalid")
        else:
            dummy, data = asm3.media.get_image_file_data(dbo, "animal", asm3.utils.cint(animalid), seq)
            if data == "NOPIC": dummy, data = asm3.media.get_image_file_data(dbo, "nopic", 0)
            return set_cached_response(cache_key, account, "image/jpeg", 86400, 3600, data)

    elif method =="animal_thumbnail":
        if asm3.utils.cint(animalid) == 0:
            asm3.al.error("animal_thumbnail failed, %s is not an animalid" % str(animalid), "service.handler", dbo)
            return ("text/plain", 0, 0, "ERROR: Invalid animalid")
        else:
            dummy, data = asm3.media.get_image_file_data(dbo, "animalthumb", asm3.utils.cint(animalid), seq)
            if data == "NOPIC": dummy, data = asm3.media.get_image_file_data(dbo, "nopic", 0)
            return set_cached_response(cache_key, account, "image/jpeg", 86400, 86400, data)

    elif method == "animal_view":
        if asm3.utils.cint(animalid) == 0:
            asm3.al.error("animal_view failed, %s is not an animalid" % str(animalid), "service.handler", dbo)
            return ("text/plain", 0, 0, "ERROR: Invalid animalid")
        else:
            return set_cached_response(cache_key, account, "text/html", 86400, 120, asm3.publishers.html.get_animal_view(dbo, asm3.utils.cint(animalid)))

    elif method == "animal_view_adoptable_js":
        return set_cached_response(cache_key, account, "application/javascript", 10800, 600, asm3.publishers.html.get_animal_view_adoptable_js(dbo))

    elif method == "animal_view_adoptable_html":
        return set_cached_response(cache_key, account, "text/html", 86400, 120, asm3.publishers.html.get_animal_view_adoptable_html(dbo))

    elif method == "checkout":
        processor = asm3.financial.get_payment_processor(dbo, post["processor"])
        return_url = post["return"] or asm3.configuration.payment_return_url(dbo)
        return set_cached_response(cache_key, account, "text/html", 120, 120, processor.checkoutPage(post["payref"], return_url, title))

    elif method =="dbfs_image":
        hotlink_protect("dbfs_image", referer)
        return set_cached_response(cache_key, account, "image/jpeg", 86400, 86400, asm3.utils.iif(title.startswith("/"),
            asm3.dbfs.get_string_filepath(dbo, title), asm3.dbfs.get_string(dbo, title)))

    elif method =="extra_image":
        hotlink_protect("extra_image", referer)
        return set_cached_response(cache_key, account, "image/jpeg", 86400, 86400, asm3.dbfs.get_string(dbo, title, "/reports"))

    elif method == "json_adoptable_animal":
        if asm3.utils.cint(animalid) == 0:
            asm3.al.error("json_adoptable_animal failed, %s is not an animalid" % str(animalid), "service.handler", dbo)
            return ("text/plain", 0, 0, "ERROR: Invalid animalid")
        else:
            asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
            rs = asm3.publishers.base.get_animal_data(dbo, None, asm3.utils.cint(animalid), include_additional_fields = True)
            return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.utils.json(rs))

    elif method == "html_adoptable_animals":
        return set_cached_response(cache_key, account, "text/html", 10800, 1800, \
            asm3.publishers.html.get_adoptable_animals(dbo, style=post["template"], \
                speciesid=post.integer("speciesid"), animaltypeid=post.integer("animaltypeid"), locationid=post.integer("locationid")))

    elif method == "html_adopted_animals":
        return set_cached_response(cache_key, account, "text/html", 10800, 1800, \
            asm3.publishers.html.get_adopted_animals(dbo, daysadopted=post.integer("days"), style=post["template"], \
                speciesid=post.integer("speciesid"), animaltypeid=post.integer("animaltypeid")))

    elif method == "html_deceased_animals":
        return set_cached_response(cache_key, account, "text/html", 10800, 1800, \
            asm3.publishers.html.get_deceased_animals(dbo, daysdeceased=post.integer("days"), style=post["template"], \
                speciesid=post.integer("speciesid"), animaltypeid=post.integer("animaltypeid")))

    elif method == "html_flagged_animals":
        if post["flag"] == "":
            asm3.al.error("html_flagged_animals requested with no flag.", "service.handler", dbo)
            return ("text/plain", 0, 0, "ERROR: Invalid flag")
        return set_cached_response(cache_key, account, "text/html", 10800, 1800, \
            asm3.publishers.html.get_flagged_animals(dbo, style=post["template"], \
                speciesid=post.integer("speciesid"), animaltypeid=post.integer("animaltypeid"), flag=post["flag"], allanimals=post.integer("all")))

    elif method == "html_held_animals":
        return set_cached_response(cache_key, account, "text/html", 10800, 1800, \
            asm3.publishers.html.get_held_animals(dbo, style=post["template"], \
                speciesid=post.integer("speciesid"), animaltypeid=post.integer("animaltypeid")))

    elif method == "json_adoptable_animals":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.publishers.base.get_animal_data(dbo, None, include_additional_fields = True)
        if strip_personal: rs = strip_personal_data(rs)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.utils.json(rs))

    elif method == "jsonp_adoptable_animals":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.publishers.base.get_animal_data(dbo, None, include_additional_fields = True)
        if strip_personal: rs = strip_personal_data(rs)
        return ("application/javascript", 0, 0, "%s(%s);" % (post["callback"], asm3.utils.json(rs)))

    elif method == "xml_adoptable_animal":
        if asm3.utils.cint(animalid) == 0:
            asm3.al.error("xml_adoptable_animal failed, %s is not an animalid" % str(animalid), "service.handler", dbo)
            return ("text/plain", 0, 0, "ERROR: Invalid animalid")
        else:
            asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
            rs = asm3.publishers.base.get_animal_data(dbo, None, asm3.utils.cint(animalid), include_additional_fields = True)
            return set_cached_response(cache_key, account, "application/xml", 3600, 3600, asm3.html.xml(rs))

    elif method == "xml_adoptable_animals":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.publishers.base.get_animal_data(dbo, None, include_additional_fields = True)
        if strip_personal: rs = strip_personal_data(rs)
        return set_cached_response(cache_key, account, "application/xml", 3600, 3600, asm3.html.xml(rs))

    elif method == "json_found_animals":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_FOUND_ANIMAL)
        rs = asm3.lostfound.get_foundanimal_last_days(dbo)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.utils.json(rs))

    elif method == "jsonp_found_animals":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_FOUND_ANIMAL)
        rs = asm3.lostfound.get_foundanimal_last_days(dbo)
        return ("application/javascript", 0, 0, "%s(%s);" % (post["callback"], asm3.utils.json(rs)))

    elif method == "xml_found_animals":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_FOUND_ANIMAL)
        rs = asm3.lostfound.get_foundanimal_last_days(dbo)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.html.xml(rs))

    elif method == "json_lost_animals":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_LOST_ANIMAL)
        rs = asm3.lostfound.get_lostanimal_last_days(dbo)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.utils.json(rs))

    elif method == "jsonp_lost_animals":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_LOST_ANIMAL)
        rs = asm3.lostfound.get_lostanimal_last_days(dbo)
        return ("application/javascript", 0, 0, "%s(%s);" % (post["callback"], asm3.utils.json(rs)))

    elif method == "xml_lost_animals":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_LOST_ANIMAL)
        rs = asm3.lostfound.get_lostanimal_last_days(dbo)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.html.xml(rs))

    elif method == "json_recent_adoptions":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.movement.get_recent_adoptions(dbo)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.utils.json(rs))

    elif method == "jsonp_recent_adoptions":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.movement.get_recent_adoptions(dbo)
        return ("application/javascript", 0, 0, "%s(%s);" % (post["callback"], asm3.utils.json(rs)))

    elif method == "xml_recent_adoptions":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.movement.get_recent_adoptions(dbo)
        return set_cached_response(cache_key, account, "application/xml", 3600, 3600, asm3.html.xml(rs))

    elif method == "html_report":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_REPORT)
        crid = asm3.reports.get_id(dbo, title)
        p = asm3.reports.get_criteria_params(dbo, crid, post)
        rhtml = asm3.reports.execute(dbo, crid, username, p)
        return set_cached_response(cache_key, account, "text/html", 600, 600, rhtml)

    elif method == "csv_mail" or method == "csv_report":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_REPORT)
        crid = asm3.reports.get_id(dbo, title)
        p = asm3.reports.get_criteria_params(dbo, crid, post)
        rows, cols = asm3.reports.execute_query(dbo, crid, username, p)
        mcsv = asm3.utils.csv(l, rows, cols, True)
        return set_cached_response(cache_key, account, "text/csv", 600, 600, mcsv)

    elif method == "jsonp_recent_changes":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        sa = asm3.animal.get_recent_changes(dbo)
        return ("application/javascript", 0, 0, "%s(%s);" % (post["callback"], asm3.utils.json(sa)))

    elif method == "json_recent_changes":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        sa = asm3.animal.get_recent_changes(dbo)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.utils.json(sa))

    elif method == "xml_recent_changes":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        sa = asm3.animal.get_recent_changes(dbo)
        return set_cached_response(cache_key, account, "application/xml", 3600, 3600, asm3.html.xml(sa))

    elif method == "jsonp_shelter_animals":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        sa = asm3.animal.get_shelter_animals(dbo)
        if strip_personal: sa = strip_personal_data(sa)
        return ("application/javascript", 0, 0, "%s(%s);" % (post["callback"], asm3.utils.json(sa)))

    elif method == "json_shelter_animals":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        sa = asm3.animal.get_shelter_animals(dbo)
        if strip_personal: sa = strip_personal_data(sa)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.utils.json(sa))

    elif method == "xml_shelter_animals":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        sa = asm3.animal.get_shelter_animals(dbo)
        if strip_personal: sa = strip_personal_data(sa)
        return set_cached_response(cache_key, account, "application/xml", 3600, 3600, asm3.html.xml(sa))

    elif method == "rss_timeline":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        return set_cached_response(cache_key, account, "application/rss+xml", 3600, 3600, asm3.html.timeline_rss(dbo))

    elif method == "upload_animal_image":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.ADD_MEDIA)
        asm3.media.attach_file_from_form(dbo, username, asm3.media.ANIMAL, int(animalid), post)
        return ("text/plain", 0, 0, "OK")

    elif method == "online_form_html":
        if formid == 0:
            raise asm3.utils.ASMError("method online_form_html requires a valid formid")
        return set_cached_response(cache_key, account, "text/html; charset=utf-8", 120, 120, asm3.onlineform.get_onlineform_html(dbo, formid))

    elif method == "online_form_json":
        if formid == 0:
            raise asm3.utils.ASMError("method online_form_json requires a valid formid")
        return set_cached_response(cache_key, account, "application/json; charset=utf-8", 30, 30, asm3.onlineform.get_onlineform_json(dbo, formid))

    elif method == "online_form_post":
        flood_protect("online_form_post", account, remoteip, 15)
        asm3.onlineform.insert_onlineformincoming_from_form(dbo, post, remoteip)
        redirect = post["redirect"]
        if redirect == "":
            redirect = BASE_URL + "/static/pages/form_submitted.html"
        return ("redirect", 0, 0, redirect)

    elif method == "sign_document":
        if formid == 0:
            raise asm3.utils.ASMError("method sign_document requires a valid formid")
        if post["sig"] == "":
            return set_cached_response(cache_key, account, "text/html", 2, 2, sign_document_page(dbo, formid))
        else:
            asm3.media.sign_document(dbo, "service", formid, post["sig"], post["signdate"])
            asm3.media.create_log(dbo, "service", formid, "ES02", _("Document signed", l))
            return ("text/plain", 0, 0, "OK")

    else:
        asm3.al.error("invalid method '%s'" % method, "service.handler", dbo)
        raise asm3.utils.ASMError("Invalid method '%s'" % method)

