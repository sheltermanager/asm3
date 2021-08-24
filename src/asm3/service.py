
"""
Service functions for external applications.

An account, username and password is mandatory for
sheltermanager accounts, username and password
for others.
"""

import asm3.al
import asm3.animal
import asm3.cachemem
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
from asm3.i18n import _, now, add_seconds, subtract_seconds
from asm3.sitedefs import BOOTSTRAP_JS, BOOTSTRAP_CSS, BOOTSTRAP_ICONS_CSS
from asm3.sitedefs import JQUERY_JS, JQUERY_UI_JS, MOMENT_JS, SIGNATURE_JS, TOUCHPUNCH_JS
from asm3.sitedefs import BASE_URL, MULTIPLE_DATABASES, CACHE_SERVICE_RESPONSES, IMAGE_HOTLINKING_ONLY_FROM_DOMAIN

# Service methods that require authentication
AUTH_METHODS = [
    "csv_mail", "csv_report", "json_report", "jsonp_report", "json_mail", "jsonp_mail",
    "html_report", "rss_timeline", "upload_animal_image", "xml_adoptable_animal", 
    "json_adoptable_animal", "xml_adoptable_animals", "json_adoptable_animals", 
    "jsonp_adoptable_animals", "xml_found_animals", "json_found_animals", 
    "jsonp_found_animals", "xml_held_animals", "json_held_animals", 
    "jsonp_held_animals", "xml_lost_animals", "json_lost_animals", 
    "jsonp_lost_animals", "xml_recent_adoptions", "json_recent_adoptions", 
    "jsonp_recent_adoptions", "xml_shelter_animals", "json_shelter_animals", 
    "jsonp_shelter_animals", "xml_recent_changes", "json_recent_changes", 
    "jsonp_recent_changes"
]

# These are service methods that are defended against cache busting
CACHE_PROTECT_METHODS = {
    "animal_image": [ "animalid", "seq" ],
    "animal_thumbnail": [ "animalid", "seq", "d" ],
    "animal_view": [ "animalid" ],
    "animal_view_adoptable_js": [], 
    "animal_view_adoptable_html": [],
    "checkout": [ "processor", "payref" ],
    "dbfs_image": [ "title" ],
    "document_repository": [ "mediaid" ],
    "extra_image": [ "title" ],
    "media_image": [ "mediaid" ],
    "json_adoptable_animal": [ "animalid" ],
    "html_adoptable_animals": [ "speciesid", "animaltypeid", "locationid", "template" ],
    "html_adopted_animals": [ "days", "template", "speciesid", "animaltypeid" ],
    "html_deceased_animals": [ "days", "template", "speciesid", "animaltypeid" ],
    "html_flagged_animals": [ "template", "speciesid", "animaltypeid", "flag", "all" ],
    "html_held_animals": [ "template", "speciesid", "animaltypeid" ],
    "json_adoptable_animals": [ "sensitive" ],
    "json_adoptable_animals_xp": [],
    "xml_adoptable_animal": [ "animalid" ],
    "xml_adoptable_animals": [ "sensitive" ],
    "json_found_animals": [],
    "xml_found_animals": [],
    "json_held_animals": [],
    "xml_held_animals": [],
    "json_lost_animals": [],
    "xml_lost_animals": [],
    "json_recent_adoptions": [], 
    "xml_recent_adoptions": [],
    # "html_report", "csv_mail", "csv_report" not included due to custom params
    "json_recent_changes": [], 
    "xml_recent_changes": [],
    "json_shelter_animals": [ "sensitive" ],
    "xml_shelter_animals": [ "sensitive" ],
    "rss_timeline": [],
    # "upload_animal_image" is a write method
    "online_form_html": [ "formid" ],
    "online_form_json": [ "formid" ]
    # "online_form_post" is a write method
    # "sign_document" is a write method
}

# Service methods that require flood protection
# method, request limit, requests in last seconds, ban period in seconds
# Eg: 1 / 15 / 30 bans for 30 seconds after 1 request in 15 seconds.
FLOOD_PROTECT_METHODS = {
    "csv_mail": [ 5, 60, 60 ],
    "csv_report": [ 5, 60, 60 ],
    "html_report": [ 5, 60, 60 ],
    "json_report": [ 5, 60, 60 ],
    "jsonp_report": [ 5, 60, 60 ],
    "json_mail": [ 5, 60, 60 ],
    "jsonp_mail": [ 5, 60, 60 ],
    "online_form_post": [ 1, 15, 15 ],
    "upload_animal_image": [ 10, 30, 30 ]
}

def flood_protect(method, remoteip):
    """ 
    Implements flood protection for methods.
    Keeps a list of timestamps in an in memory cache for the method and IP address.
    If this IP makes more than the request limit for the period, the request is rejected 
        and the IP banned for a period.
    method: The service method we're protecting
    remoteip: The ip address of the caller
    """
    CACHE_TTL = 120 # Flood protection only operates for a minute or so keep entry alive for a couple
    remoteip = str(remoteip).replace(", ", "") # X-FORWARDED-FOR can be a list, remove commas
    cache_key = "m%sr%s" % (method, remoteip)    
    # Get the entry for this IP
    v = asm3.cachemem.get(cache_key)
    if v is None:
        v = { "b": None, "h": [ asm3.i18n.now() ] } # b = banned until, h = list of hits as timestamps
        asm3.cachemem.put(cache_key, v, CACHE_TTL) 
    else:
        # asm3.al.debug("protecting '%s' from '%s': cache: %s" % (method, remoteip, v), "service.flood_protect")
        # Is this IP banned?
        if v["b"] is not None and now() < v["b"]:
            asm3.al.error("%s is banned from calling '%s' until '%s'" % (remoteip, method, v["b"]), "service.flood_protect")
            message = "You cannot call '%s' until '%s'" % (method, v["b"])
            raise asm3.utils.ASMError(message)
        # Add a hit for now
        v["h"].append(now())
        request_limit, periods, banneds = FLOOD_PROTECT_METHODS[method]
        # Calculate how long ago period in s was and how many requests this IP has made in the period
        cutoff = subtract_seconds(now(), periods)
        requests_in_period = 0
        for d in v["h"]:
            if d > cutoff: requests_in_period += 1
        # Are we over the limit?
        if requests_in_period > request_limit:
            v["b"] = add_seconds(now(), banneds) # Mark this IP banned for this method for the ban period
            asm3.cachemem.put(cache_key, v, CACHE_TTL)
            asm3.al.error("%s has called '%s', %s times in the last %d seconds. Banning until '%s' (%s seconds)" % (remoteip, method, request_limit, periods, v["b"], banneds), "service.flood_protect")
            message = "You have already called '%s', %s times in the last %d seconds, please wait %d seconds before trying again." % (method, request_limit, periods, banneds)
            raise asm3.utils.ASMError(message)
        else:
            # Update the cache with the new hit and continue
            asm3.cachemem.put(cache_key, v, CACHE_TTL)

def hotlink_protect(method, referer):
    """ Protect a method from having any referer other than the one we set """
    domains = IMAGE_HOTLINKING_ONLY_FROM_DOMAIN.split(",")
    fromhldomain = False
    for d in domains:
        if d != "" and referer.find(d) != -1: fromhldomain = True
    if referer != "" and IMAGE_HOTLINKING_ONLY_FROM_DOMAIN != "" and not fromhldomain:
        raise asm3.utils.ASMPermissionError("Hotlinking to %s from %s is forbidden" % (method, referer))

def safe_cache_key(method, qs):
    """ 
    Reads the parameters from querystring and throws away 
    any parameters that are not in CACHE_PROTECT_METHODS for the method.
    If the method appears in AUTH_METHODS, whitelists the username/password params.
    """
    if qs.startswith("?"): qs = qs[1:]
    whitelist = [ "method", "account" ]
    if method in AUTH_METHODS:
        whitelist += [ "username", "password" ]
    whitelist += CACHE_PROTECT_METHODS[method]
    out = []
    for p in qs.split("&"):
        b = p.split("=", 1)
        if len(b) != 2: continue
        if b[0].lower() in whitelist: out.append(p)
    return "&".join(out)

def get_cached_response(cache_key, path):
    """ Gets a service call response from the cache based on its key.
    If no entry is found, None is returned.
    """
    if not CACHE_SERVICE_RESPONSES: return None
    response = asm3.cachedisk.get(cache_key, path)
    if response is None or len(response) != 4: return None
    # asm3.al.debug("GET: %s (%d bytes)" % (cache_key, len(response[3])), "service.get_cached_response")
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
    # asm3.al.debug("PUT: %s (%d bytes)" % (cache_key, len(content)), "service.set_cached_response")
    asm3.cachedisk.put(cache_key, path, response, serverage)
    return response

def sign_document_page(dbo, mid, email):
    """ Outputs a page that allows signing of document with media id mid. 
        email is the address to send a copy of the signed document to. """
    l = dbo.locale
    scripts = [ 
        asm3.html.script_tag(JQUERY_JS),
        asm3.html.script_tag(JQUERY_UI_JS),
        asm3.html.script_tag(BOOTSTRAP_JS),
        asm3.html.script_tag(TOUCHPUNCH_JS),
        asm3.html.script_tag(SIGNATURE_JS),
        asm3.html.script_tag(MOMENT_JS),
        asm3.html.css_tag(BOOTSTRAP_CSS),
        asm3.html.css_tag(BOOTSTRAP_ICONS_CSS),
        asm3.html.script_i18n(dbo.locale),
        asm3.html.asm_script_tag("service_sign_document.js") 
    ]
    dummy, dummy, dummy, contents = asm3.media.get_media_file_data(dbo, int(mid))
    content = asm3.utils.fix_relative_document_uris(dbo, asm3.utils.bytes2str(contents))
    controller = {
        "id":       mid,
        "account":  dbo.database,
        "email":    email,
        "notes":    asm3.media.get_notes_for_id(dbo, int(mid)),
        "signed":   asm3.media.has_signature(dbo, mid),
        "content":  content
    }
    return asm3.html.js_page(scripts, _("Signing Pad", l), controller)

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
    mediaid = post.integer("mediaid")
    seq = post.integer("seq")
    title = post["title"]
    strip_personal = post.integer("sensitive") == 0

    # If this method is in the cache protected list, only use
    # whitelisted parameters for the key to prevent callers 
    # cache-busting by adding junk parameters
    cache_key = querystring.replace(" ", "")
    if method in CACHE_PROTECT_METHODS:
        cache_key = safe_cache_key(method, cache_key)

    # Do we have a cached response for these parameters?
    cached_response = get_cached_response(cache_key, account)
    if cached_response is not None:
        asm3.al.debug("cache hit: %s (%d bytes)" % (cache_key, len(cached_response[3])), "service.handler", account)
        return cached_response

    # Are we dealing with multiple databases, but no account was specified?
    if account == "" and MULTIPLE_DATABASES:
        return ("text/plain", 0, 0, "ERROR: No database/alias specified")

    # Is flood protection activated for this method?
    if method in FLOOD_PROTECT_METHODS:
        flood_protect(method, remoteip)

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
    dbo.timezone_dst = asm3.configuration.timezone_dst(dbo)
    asm3.al.info("call @%s --> %s [%s]" % (username, method, querystring), "service.handler", dbo)

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
            return set_cached_response(cache_key, account, "image/jpeg", 86400, 3600, data)

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
        if not processor.validatePaymentReference(post["payref"]):
            return ("text/plain", 0, 0, "ERROR: Invalid payref")
        if processor.isPaymentReceived(post["payref"]):
            return ("text/plain", 0, 0, "ERROR: Expired payref")
        return_url = post["return"] or asm3.configuration.payment_return_url(dbo)
        return set_cached_response(cache_key, account, "text/html", 120, 120, processor.checkoutPage(post["payref"], return_url, title))

    elif method =="dbfs_image":
        hotlink_protect("dbfs_image", referer)
        return set_cached_response(cache_key, account, "image/jpeg", 86400, 86400, asm3.utils.iif(title.startswith("/"),
            asm3.dbfs.get_string_filepath(dbo, title), asm3.dbfs.get_string(dbo, title)))

    elif method =="document_repository":
        return set_cached_response(cache_key, account, asm3.media.mime_type(asm3.dbfs.get_name_for_id(dbo, mediaid)), 86400, 86400, asm3.dbfs.get_string_id(dbo, mediaid))

    elif method =="extra_image":
        hotlink_protect("extra_image", referer)
        return set_cached_response(cache_key, account, "image/jpeg", 86400, 86400, asm3.dbfs.get_string(dbo, title, "/reports"))

    elif method =="media_image":
        hotlink_protect("media_image", referer)
        return set_cached_response(cache_key, account, "image/jpeg", 86400, 86400, 
            asm3.dbfs.get_string_id( dbo, dbo.query_int("select dbfsid from media where id = ?", [mediaid]) ))

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

    elif method == "json_adoptable_animals_xp":
        rs = strip_personal_data(asm3.publishers.base.get_animal_data(dbo, None, include_additional_fields = True))
        return set_cached_response(cache_key, account, "application/json", 600, 600, asm3.utils.json(rs))

    elif method == "json_adoptable_animals":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.publishers.base.get_animal_data(dbo, None, include_additional_fields = True)
        if strip_personal: rs = strip_personal_data(rs)
        return set_cached_response(cache_key, account, "application/json", 600, 600, asm3.utils.json(rs))

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
            return set_cached_response(cache_key, account, "application/xml", 600, 600, asm3.html.xml(rs))

    elif method == "xml_adoptable_animals":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.publishers.base.get_animal_data(dbo, None, include_additional_fields = True)
        if strip_personal: rs = strip_personal_data(rs)
        return set_cached_response(cache_key, account, "application/xml", 600, 600, asm3.html.xml(rs))

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

    elif method == "json_held_animals":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.animal.get_animals_hold(dbo)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.utils.json(rs))

    elif method == "xml_held_animals":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.animal.get_animals_hold(dbo)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.html.xml(rs))

    elif method == "jsonp_held_animals":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.animal.get_animals_hold(dbo)
        return ("application/javascript", 0, 0, "%s(%s);" % (post["callback"], asm3.utils.json(rs)))

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
        rhtml = asm3.utils.fix_relative_document_uris(dbo, rhtml)
        return set_cached_response(cache_key, account, "text/html", 600, 600, rhtml)

    elif method == "csv_mail" or method == "csv_report":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_REPORT)
        crid = asm3.reports.get_id(dbo, title)
        p = asm3.reports.get_criteria_params(dbo, crid, post)
        rows, cols = asm3.reports.execute_query(dbo, crid, username, p)
        mcsv = asm3.utils.csv(l, rows, cols, True)
        return set_cached_response(cache_key, account, "text/csv", 600, 600, mcsv)

    elif method == "json_report" or method == "json_mail":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_REPORT)
        crid = asm3.reports.get_id(dbo, title)
        p = asm3.reports.get_criteria_params(dbo, crid, post)
        rows, cols = asm3.reports.execute_query(dbo, crid, username, p)
        return set_cached_response(cache_key, account, "application/json", 600, 600, asm3.utils.json(rows))

    elif method == "jsonp_report" or method == "jsonp_mail":
        asm3.users.check_permission_map(l, user["SUPERUSER"], securitymap, asm3.users.VIEW_REPORT)
        crid = asm3.reports.get_id(dbo, title)
        p = asm3.reports.get_criteria_params(dbo, crid, post)
        rows, cols = asm3.reports.execute_query(dbo, crid, username, p)
        return ("application/javascript", 0, 0, "%s(%s);" % (post["callback"], asm3.utils.json(rows)))

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
        asm3.onlineform.insert_onlineformincoming_from_form(dbo, post, remoteip)
        redirect = post["redirect"]
        if redirect == "":
            redirect = BASE_URL + "/static/pages/form_submitted.html"
        return ("redirect", 0, 0, redirect)

    elif method == "sign_document":
        if formid == 0:
            raise asm3.utils.ASMError("method sign_document requires a valid formid")
        if post["sig"] == "":
            m = asm3.media.get_media_by_id(dbo, formid)
            if m is None: raise asm3.utils.ASMError("invalid link")
            token = asm3.utils.md5_hash_hex("%s%s" % (m.ID, m.LINKID))
            if token != post["token"]: raise asm3.utils.ASMError("invalid token")
            return set_cached_response(cache_key, account, "text/html", 2, 2, sign_document_page(dbo, formid, post["email"]))
        else:
            asm3.media.sign_document(dbo, "service", formid, post["sig"], post["signdate"], "signemail")
            asm3.media.create_log(dbo, "service", formid, "ES02", _("Document signed", l))
            if post.boolean("sendsigned"):
                m = asm3.media.get_media_by_id(dbo, formid)
                if m is None: raise asm3.utils.ASMError("cannot find %s" % formid)
                content = asm3.utils.bytes2str(asm3.dbfs.get_string(dbo, m.MEDIANAME))
                contentpdf = asm3.utils.html_to_pdf(dbo, content)
                attachments = [( "%s.pdf" % m.ID, "application/pdf", contentpdf )]
                fromaddr = asm3.configuration.email(dbo)
                asm3.utils.send_email(dbo, fromaddr, post["email"], "", "", _("Signed Document", l), m.MEDIANOTES, "plain", attachments)
            return ("text/plain", 0, 0, "OK")

    else:
        asm3.al.error("invalid method '%s'" % method, "service.handler", dbo)
        raise asm3.utils.ASMError("Invalid method '%s'" % method)

