
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
import asm3.event
import asm3.financial
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
from asm3.i18n import _, now, add_seconds, format_currency, format_time, python2display, subtract_seconds
from asm3.sitedefs import BOOTSTRAP_JS, BOOTSTRAP_CSS, BOOTSTRAP_ICONS_CSS
from asm3.sitedefs import JQUERY_JS, JQUERY_UI_JS, SIGNATURE_JS
from asm3.sitedefs import BASE_URL, SERVICE_URL, MULTIPLE_DATABASES, CACHE_SERVICE_RESPONSES, IMAGE_HOTLINKING_ONLY_FROM_DOMAIN
from asm3.typehints import Database, PostedData, Results, ServiceResponse

# Service methods that require authentication
AUTH_METHODS = [
    "csv_import", "csv_mail", "csv_report", 
    "json_report", "jsonp_report", "json_mail", "jsonp_mail",
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
    "animal_view": [ "animalid", "template" ],
    "animal_view_adoptable_js": [], 
    "animal_view_adoptable_html": [],
    "checkout": [ "processor", "payref" ],
    # "checkout_adoption" - write method
    # "checkout_licence" - write method
    # "csv_import" - write method
    # "csv_mail", "csv_report" - custom params
    "dbfs_image": [ "title" ],
    "document_repository": [ "mediaid" ],
    "extra_image": [ "title" ],
    # "html_report" - custom params
    "media_image": [ "mediaid" ],
    "media_file": [ "mediaid" ],
    "json_adoptable_animal": [ "animalid" ],
    "html_adoptable_animals": [ "speciesid", "animaltypeid", "locationid", "template", "underweeks", "overweeks" ],
    "html_adopted_animals": [ "days", "template", "speciesid", "animaltypeid", "order" ],
    "html_deceased_animals": [ "days", "template", "speciesid", "animaltypeid", "order" ],
    "html_events": [ "count", "template" ],
    "html_flagged_animals": [ "template", "speciesid", "animaltypeid", "flag", "all", "order" ],
    "html_held_animals": [ "template", "speciesid", "animaltypeid", "order" ],
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
    "json_recent_changes": [], 
    "xml_recent_changes": [],
    "json_shelter_animals": [ "sensitive" ],
    "xml_shelter_animals": [ "sensitive" ],
    "rss_timeline": [],
    "online_form_html": [ "formid" ],
    "online_form_json": [ "formid" ]
    # "online_form_post" - write method
    # "sign_document" - write method
    # "upload_animal_image" - write method
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
    "online_form_post": [ 1, 15, 15 ]
}

def flood_protect(method: str, remoteip: str) -> None:
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
        v = { "b": None, "h": [ now() ] } # b = banned until, h = list of hits as timestamps
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

def hotlink_protect(method: str, referer: str) -> None:
    """ Protect a method from having any referer other than the one we set """
    domains = IMAGE_HOTLINKING_ONLY_FROM_DOMAIN.split(",")
    fromhldomain = False
    for d in domains:
        if d != "" and referer.find(d) != -1: fromhldomain = True
    if referer != "" and IMAGE_HOTLINKING_ONLY_FROM_DOMAIN != "" and not fromhldomain:
        raise asm3.utils.ASMPermissionError("Hotlinking to %s from %s is forbidden" % (method, referer))

def safe_cache_key(method: str, qs: str) -> str:
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

def get_cached_response(cache_key: str, path: str) -> ServiceResponse:
    """ Gets a service call response from the cache based on its key.
    If no entry is found, None is returned.
    """
    if not CACHE_SERVICE_RESPONSES: return None
    response = asm3.cachedisk.get(cache_key, path)
    if response is None or len(response) != 4: return None
    # asm3.al.debug("GET: %s (%d bytes)" % (cache_key, len(response[3])), "service.get_cached_response")
    return response

def set_cached_response(cache_key: str, path: str, mime: str, clientage: int, serverage: int, content: bytes) -> ServiceResponse:
    """ Sets a service call response in the cache and returns it
    methods can use this as a passthrough to return the response.
    cache_key: The constructed cache key from the parameters
    mime: The mime type to return in the response
    clientage: The max-age to set for the client to cache the response (seconds)
    serverage: The ttl for storing in our server cache (seconds)
    content: The response (str or bytes)
    """
    response = (mime, clientage, serverage, content)
    if not CACHE_SERVICE_RESPONSES: return response
    # asm3.al.debug("PUT: %s (%d bytes)" % (cache_key, len(content)), "service.set_cached_response")
    asm3.cachedisk.put(cache_key, path, response, serverage)
    return response

def checkout_adoption_page(dbo: Database, token: str) -> str:
    """ Outputs a page that generates paperwork, allows an adopter to sign it
        and then pay their adoption fee and an optional donation """
    l = dbo.locale
    scripts = [ 
        asm3.html.script_tag(JQUERY_JS),
        asm3.html.script_tag(JQUERY_UI_JS),
        asm3.html.script_tag(BOOTSTRAP_JS),
        asm3.html.script_tag(SIGNATURE_JS),
        asm3.html.css_tag(BOOTSTRAP_CSS),
        asm3.html.css_tag(BOOTSTRAP_ICONS_CSS),
        asm3.html.script_i18n(dbo.locale),
        asm3.html.asm_script_tag("service_checkout_adoption.js") 
    ]
    co = asm3.cachedisk.get(token, dbo.database)
    if co is None:
        raise asm3.utils.ASMError("invalid token")
    # Generate the adoption paperwork if it has not been generated already
    if co["mediaid"] == 0:
        dtid = co["templateid"]
        content = asm3.wordprocessor.generate_movement_doc(dbo, dtid, co["movementid"], "checkout")
        # Save the doc with the person and animal, record the person copy for signing
        tempname = asm3.template.get_document_template_name(dbo, dtid)
        tempname = "%s - %s::%s" % (tempname, asm3.animal.get_animal_namecode(dbo, co["animalid"]), 
            asm3.person.get_person_name(dbo, co["personid"]))
        amid, pmid = asm3.media.create_document_animalperson(dbo, "checkout", co["animalid"], co["personid"], tempname, content)
        co["mediaid"] = pmid
        content = asm3.utils.fix_relative_document_uris(dbo, asm3.utils.bytes2str(content))
        co["mediacontent"] = content
        asm3.cachedisk.put(token, dbo.database, co, 86400 * 2)
    # Include extra values
    co["donationmsg"] = asm3.configuration.adoption_checkout_donation_msg(dbo)
    co["donationtiers"] = asm3.configuration.adoption_checkout_donation_tiers(dbo)
    co["token"] = token
    # Record that the checkout was accessed in the log
    logtypeid = asm3.configuration.system_log_type(dbo)
    logmsg = "AC02:%s:%s(%s)-->%s(%s)" % (co["movementid"], co["animalname"], co["animalid"], co["personname"], co["personid"])
    asm3.log.add_log(dbo, "system", asm3.log.PERSON, co["personid"], logtypeid, logmsg)
    return asm3.html.js_page(scripts, _("Adoption Checkout", l), co)

def checkout_adoption_post(dbo: Database, post: PostedData) -> str:
    """
    Called by the adoption checkout frontend with the document signature and donation amount.
    Handles the document signing, triggers creation of the payment records, etc.
    Returns the URL needed to redirect to the payment processor to complete payment.
    """
    l = dbo.locale
    co = asm3.cachedisk.get(post["token"], dbo.database)
    if co is None:
        raise asm3.utils.ASMError("invalid token")
    mediaid = co["mediaid"]
    donationamt = post.integer("donationamt") * 100
    # Sign the docs if they haven't been done already
    if not asm3.media.has_signature(dbo, mediaid):
        signdate = "%s %s" % (python2display(l, dbo.now()), format_time(dbo.now()))
        asm3.media.sign_document(dbo, "service", mediaid, post["sig"], signdate, "signemail")
        if post.boolean("sendsigned"):
            m = asm3.media.get_media_by_id(dbo, mediaid)
            if m is None: raise asm3.utils.ASMError("cannot find %s" % mediaid)
            content = asm3.utils.bytes2str(asm3.dbfs.get_string_id(dbo, m.DBFSID))
            contentpdf = asm3.utils.html_to_pdf(dbo, content)
            attachments = [( "%s.pdf" % m.ID, "application/pdf", contentpdf )]
            asm3.utils.send_email(dbo, "", co["email"], "", "", 
                _("Signed Document", l), m.MEDIANOTES, "plain", attachments)
    # Create the due payment records if they haven't been done already, along with a receipt/payref
    if co["paymentfeeid"] == 0:
        co["paymentprocessor"] = asm3.configuration.adoption_checkout_processor(dbo)
        co["receiptnumber"] = asm3.financial.get_next_receipt_number(dbo) # Both go on the same receipt
        co["payref"] = "%s-%s" % (co["personcode"], co["receiptnumber"])
        # Adoption Fee
        co["paymentfeeid"] = asm3.financial.insert_donation_from_form(dbo, "checkout", asm3.utils.PostedData({
            "person":       str(co["personid"]),
            "animal":       str(co["animalid"]),
            "movement":     str(co["movementid"]),
            "type":         co["feetypeid"], 
            "payment":      asm3.configuration.adoption_checkout_payment_method(dbo),
            "amount":       co["fee"],
            "due":          python2display(l, dbo.now()),
            "receiptnumber": co["receiptnumber"],
            "giftaid":      str(co["giftaid"])
        }, l))
        # Donation (not linked to movement on purpose to avoid showing on adoption fee reports)
        if donationamt > 0:
            co["paymentdonid"] = asm3.financial.insert_donation_from_form(dbo, "checkout", asm3.utils.PostedData({
                "person":       str(co["personid"]),
                "animal":       str(co["animalid"]),
                "type":         str(asm3.configuration.adoption_checkout_donationid(dbo)),
                "payment":      str(asm3.configuration.adoption_checkout_payment_method(dbo)),
                "amount":       str(donationamt),
                "due":          python2display(l, dbo.now()),
                "receiptnumber": co["receiptnumber"],
                "giftaid":      str(co["giftaid"])
            }, l))
        # Update the cache entry
        asm3.cachedisk.put(post["token"], dbo.database, co, 86400 * 2)
    elif co["paymentdonid"] > 0 and donationamt > 0:
        # payments have already been created, must be a user revisiting the checkout.
        # update their donation amount in case they made a different choice this time.
        dbo.update("ownerdonation", co["paymentdonid"], {
            "Donation": donationamt
        }, "checkout")
    elif co["paymentdonid"] > 0 and donationamt == 0:
        # The user has changed their voluntary donation amount to 0 - delete it
        dbo.delete("ownerdonation", co["paymentdonid"], "checkout")
    # Record that the checkout was completed in the log
    logtypeid = asm3.configuration.system_log_type(dbo)
    logmsg = "AC03:%s:%s(%s)-->%s(%s):volamt=%s" % (co["movementid"], co["animalname"], co["animalid"], co["personname"], co["personid"], donationamt)
    asm3.log.add_log(dbo, "system", asm3.log.PERSON, co["personid"], logtypeid, logmsg)
    # Construct the payment checkout URL
    title = _("{0}: Adoption fee", l)
    if co["paymentdonid"] != "0": title = _("{0}: Adoption fee and donation", l)
    params = { 
        "account": dbo.database, 
        "method": "checkout",
        "processor": co["paymentprocessor"],
        "payref": co["payref"],
        "title": title.format(co["animalname"])
    }
    url = "%s?%s" % (SERVICE_URL, asm3.utils.urlencode(params))
    return url

def checkout_licence_page(dbo: Database, token: str) -> str:
    """ Outputs a page that allows a licence holder to confirm and pay
        for their licence renewal """ 
    l = dbo.locale
    scripts = [ 
        asm3.html.script_tag(JQUERY_JS),
        asm3.html.script_tag(JQUERY_UI_JS),
        asm3.html.script_tag(BOOTSTRAP_JS),
        asm3.html.script_tag(SIGNATURE_JS),
        asm3.html.css_tag(BOOTSTRAP_CSS),
        asm3.html.css_tag(BOOTSTRAP_ICONS_CSS),
        asm3.html.script_i18n(dbo.locale),
        asm3.html.asm_script_tag("service_checkout_licence.js") 
    ]
    co = asm3.cachedisk.get(token, dbo.database)
    if co is None:
        li = asm3.financial.get_licence_token(dbo, token)
        if li is None:
            raise asm3.utils.ASMError("invalid token")
        if li.RENEWED == 1:
            raise asm3.utils.ASMError("license already renewed")
        co["row"] = li
        co["licencenumber"] = li.LICENCENUMBER
        co["animalname"] = li.ANIMALNAME
        co["animalid"] = li.ANIMALID
        co["ownercode"] = li.OWNERCODE
        co["ownerid"] = li.OWNERID
        co["database"] = dbo.database
        co["paymentfeeid"] = 0
        co["newfee"] = asm3.financial.get_licence_fee(li.LICENCETYPEID)
        co["formatfee"] = format_currency(co["newfee"])
        asm3.cachedisk.put(token, dbo.database, co, 86400 * 2)
    # Record that the checkout was accessed in the log
    logtypeid = asm3.configuration.system_log_type(dbo)
    logmsg = "LC01:%s" % co["licencenumber"]
    asm3.log.add_log(dbo, "system", asm3.log.PERSON, co["ownerid"], logtypeid, logmsg)
    return asm3.html.js_page(scripts, _("License Checkout", l), co)

def checkout_licence_post(dbo: Database, post: PostedData) -> str:
    """
    Called by the licence checkout frontend with the renewal amount.
    Triggers creation of the payment records, etc.
    Returns the URL needed to redirect to the payment processor to complete payment.
    """
    l = dbo.locale
    co = asm3.cachedisk.get(post["token"], dbo.database)
    if co is None:
        raise asm3.utils.ASMError("invalid token")
    # Create the due payment record if it hasn't been done already, along with a receipt/payref
    if co["paymentfeeid"] == 0:
        co["feetypeid"] = asm3.configuration.licence_checkout_feeid(dbo)
        co["processor"] = asm3.configuration.adoption_checkout_processor(dbo)
        co["receiptnumber"] = asm3.financial.get_next_receipt_number(dbo) # Both go on the same receipt
        co["payref"] = "%s-%s" % (co["ownercode"], co["receiptnumber"])
        # Renewal Fee
        co["paymentfeeid"] = asm3.financial.insert_donation_from_form(dbo, "checkout", asm3.utils.PostedData({
            "person":       str(co["ownerid"]),
            "animal":       str(co["animalid"]),
            "movement":     "0",
            "type":         co["feetypeid"], 
            "payment":      asm3.configuration.adoption_checkout_payment_method(dbo),
            "amount":       co["newfee"],
            "due":          python2display(l, dbo.now()),
            "receiptnumber": co["receiptnumber"],
            "giftaid":      str("0")
        }, l))
        # Update the cache entry
        asm3.cachedisk.put(post["token"], dbo.database, co, 86400 * 2)
    # Record that the checkout was completed in the log
    logtypeid = asm3.configuration.system_log_type(dbo)
    logmsg = "LC02:%s:%s" % ( co["licencenumber"], co["newfee"] )
    asm3.log.add_log(dbo, "system", asm3.log.PERSON, co["ownerid"], logtypeid, logmsg)
    # TODO: We need to set the renewed flag on the existing licence and create the new one
    # problem is, we should only do it when the payment has actually been received, which
    # means some kind of callback mechanism from paymentprocessor.receive. How to implement?
    # Construct the payment checkout URL
    title = _("{0}: License renewal fee", l)
    params = { 
        "account": dbo.database, 
        "method": "checkout",
        "processor": co["paymentprocessor"],
        "payref": co["payref"],
        "title": title.format(co["animalname"])
    }
    url = "%s?%s" % (SERVICE_URL, asm3.utils.urlencode(params))
    return url

def sign_document_page(dbo: Database, mid: int, email: str) -> str:
    """ Outputs a page that allows signing of document with media id mid. 
        email is the address to send a copy of the signed document to. """
    l = dbo.locale
    scripts = [ 
        asm3.html.script_tag(JQUERY_JS),
        asm3.html.script_tag(JQUERY_UI_JS),
        asm3.html.script_tag(BOOTSTRAP_JS),
        asm3.html.script_tag(SIGNATURE_JS),
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

def strip_personal_data(rows: Results) -> Results:
    """ Removes any personal data from animal rows 
        include_current: If False, strips CURRENTOWNER tokens (typically foster for shelter animals)
    """
    for r in rows:
        for k in r.keys():
            if k.startswith("CURRENTOWNER") or k.startswith("ORIGINALOWNER") or k.startswith("BROUGHTINBY") or k.startswith("RESERVEDOWNER"):
                r[k] = ""
    return rows

def handler(post: PostedData, path: str, remoteip: str, referer: str, useragent: str, querystring: str) -> ServiceResponse:
    """ Handles the various service method types.
    post:        The GET/POST parameters
    path:        The current system path/code.PATH
    remoteip:    The IP of the caller
    referer:     The referer HTTP header
    useragent:   The user-agent HTTP header
    querystring: The complete querystring
    return value is a tuple containing MIME type, clientcachettl, edgecachettl, content
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
        securitymap = asm3.users.get_security_map(dbo, user.ID)

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
            return set_cached_response(cache_key, account, "text/html", 3600, 600, asm3.publishers.html.get_animal_view(dbo, asm3.utils.cint(animalid), style=post["template"]))

    elif method == "animal_view_adoptable_js":
        return set_cached_response(cache_key, account, "application/javascript", 3600, 600, asm3.publishers.html.get_animal_view_adoptable_js(dbo))

    elif method == "animal_view_adoptable_html":
        return set_cached_response(cache_key, account, "text/html", 86400, 600, asm3.publishers.html.get_animal_view_adoptable_html(dbo))

    elif method == "checkout":
        processor = asm3.financial.get_payment_processor(dbo, post["processor"])
        if not processor.validatePaymentReference(post["payref"]):
            return ("text/plain", 0, 0, "ERROR: Invalid payref")
        if processor.isPaymentReceived(post["payref"]):
            return ("text/plain", 0, 0, "ERROR: Expired payref")
        return_url = post["return"] or asm3.configuration.payment_return_url(dbo)
        return set_cached_response(cache_key, account, "text/html", 15, 15, processor.checkoutPage(post["payref"], return_url, title))

    elif method == "checkout_adoption":
        if post["token"] == "":
            raise asm3.utils.ASMError("method checkout_adoption requires a valid token")
        elif post["sig"] == "":
            return set_cached_response(cache_key, account, "text/html", 120, 120, checkout_adoption_page(dbo, post["token"]))
        else:
            return ("text/plain", 0, 0, checkout_adoption_post(dbo, post))
        
    elif method == "checkout_licence":
        if post["token"] == "":
            raise asm3.utils.ASMError("method checkout_licence requires a valid token")
        elif post["action"] == "":
            return set_cached_response(cache_key, account, "text/html", 120, 120, checkout_licence_page(dbo, post["token"]))
        else:
            return ("text/plain", 0, 0, checkout_licence_post(dbo, post))

    elif method == "csv_import":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.IMPORT_CSV_FILE)
        csvdata = asm3.utils.base64decode(post["data"])
        encoding = post["encoding"] or "utf-8-sig"
        jsonresults = asm3.csvimport.csvimport(dbo, csvdata, encoding, user.USERNAME, checkduplicates=True, htmlresults=False)
        return ("application/json", 0, 0, jsonresults)

    elif method =="dbfs_image":
        hotlink_protect("dbfs_image", referer)
        if title.startswith("/"):
            imagedata = asm3.dbfs.get_string_filepath(dbo, title)
        else:
            imagedata = asm3.dbfs.get_string(dbo, title)
        return set_cached_response(cache_key, account, "image/jpeg", 86400, 86400, imagedata)

    elif method == "document_repository":
        return set_cached_response(cache_key, account, asm3.media.mime_type(asm3.dbfs.get_name_for_id(dbo, mediaid)), 86400, 86400, 
            asm3.dbfs.get_string_id(dbo, mediaid))
    
    elif method == "extra_image":
        hotlink_protect("extra_image", referer)
        return set_cached_response(cache_key, account, "image/jpeg", 86400, 86400, asm3.dbfs.get_string(dbo, title, "/reports"))

    elif method == "media_image":
        hotlink_protect("media_image", referer)
        lastmodified, medianame, mimetype, filedata = asm3.media.get_media_file_data(dbo, mediaid)
        if medianame == "": return ("text/plain", 0, 0, "ERROR: Invalid mediaid")
        return set_cached_response(cache_key, account, mimetype, 86400, 86400, filedata)

    elif method == "media_file":
        lastmodified, medianame, mimetype, filedata = asm3.media.get_media_file_data(dbo, mediaid)
        if medianame == "": return ("text/plain", 0, 0, "ERROR: Invalid mediaid")
        return set_cached_response(cache_key, account, mimetype, 86400, 86400, filedata)

    elif method == "json_adoptable_animal":
        if asm3.utils.cint(animalid) == 0:
            asm3.al.error("json_adoptable_animal failed, %s is not an animalid" % str(animalid), "service.handler", dbo)
            return ("text/plain", 0, 0, "ERROR: Invalid animalid")
        else:
            asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
            rs = asm3.publishers.base.get_animal_data(dbo, None, asm3.utils.cint(animalid), include_additional_fields = True)
            return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.utils.json(rs))

    elif method == "html_adoptable_animals":
        return set_cached_response(cache_key, account, "text/html", 600, 600, \
            asm3.publishers.html.get_adoptable_animals(dbo, style=post["template"], \
                speciesid=post.integer("speciesid"), animaltypeid=post.integer("animaltypeid"), \
                locationid=post.integer("locationid"), underweeks=post.integer("underweeks"), \
                overweeks=post.integer("overweeks")))

    elif method == "html_adopted_animals":
        return set_cached_response(cache_key, account, "text/html", 10800, 1800, \
            asm3.publishers.html.get_adopted_animals(dbo, daysadopted=post.integer("days"), style=post["template"], \
                speciesid=post.integer("speciesid"), animaltypeid=post.integer("animaltypeid"), orderby=post["order"]))

    elif method == "html_deceased_animals":
        return set_cached_response(cache_key, account, "text/html", 10800, 1800, \
            asm3.publishers.html.get_deceased_animals(dbo, daysdeceased=post.integer("days"), style=post["template"], \
                speciesid=post.integer("speciesid"), animaltypeid=post.integer("animaltypeid"), orderby=post["order"]))
    
    elif method == "html_events":
        return set_cached_response(cache_key, account, "text/html", 3600, 3600, 
            asm3.event.get_events_html(dbo, post.integer("count"), template=post["template"]))

    elif method == "html_flagged_animals":
        if post["flag"] == "":
            asm3.al.error("html_flagged_animals requested with no flag.", "service.handler", dbo)
            return ("text/plain", 0, 0, "ERROR: Invalid flag")
        return set_cached_response(cache_key, account, "text/html", 1800, 1800, \
            asm3.publishers.html.get_flagged_animals(dbo, style=post["template"], \
                speciesid=post.integer("speciesid"), animaltypeid=post.integer("animaltypeid"), flag=post["flag"], 
                allanimals=post.integer("all"), orderby=post["orderby"]))

    elif method == "html_held_animals":
        return set_cached_response(cache_key, account, "text/html", 1800, 1800, \
            asm3.publishers.html.get_held_animals(dbo, style=post["template"], \
                speciesid=post.integer("speciesid"), animaltypeid=post.integer("animaltypeid"), orderby=post["order"]))

    elif method == "json_adoptable_animals_xp":
        rs = strip_personal_data(asm3.publishers.base.get_animal_data(dbo, None, include_additional_fields = True))
        return set_cached_response(cache_key, account, "application/json", 600, 600, asm3.utils.json(rs))

    elif method == "json_adoptable_animals":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.publishers.base.get_animal_data(dbo, None, include_additional_fields = True)
        if strip_personal: rs = strip_personal_data(rs)
        return set_cached_response(cache_key, account, "application/json", 600, 600, asm3.utils.json(rs))

    elif method == "jsonp_adoptable_animals":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.publishers.base.get_animal_data(dbo, None, include_additional_fields = True)
        if strip_personal: rs = strip_personal_data(rs)
        return ("application/javascript", 0, 0, "%s(%s);" % (post["callback"], asm3.utils.json(rs)))

    elif method == "xml_adoptable_animal":
        if asm3.utils.cint(animalid) == 0:
            asm3.al.error("xml_adoptable_animal failed, %s is not an animalid" % str(animalid), "service.handler", dbo)
            return ("text/plain", 0, 0, "ERROR: Invalid animalid")
        else:
            asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
            rs = asm3.publishers.base.get_animal_data(dbo, None, asm3.utils.cint(animalid), include_additional_fields = True)
            return set_cached_response(cache_key, account, "application/xml", 600, 600, asm3.html.xml(rs))

    elif method == "xml_adoptable_animals":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.publishers.base.get_animal_data(dbo, None, include_additional_fields = True)
        if strip_personal: rs = strip_personal_data(rs)
        return set_cached_response(cache_key, account, "application/xml", 600, 600, asm3.html.xml(rs))

    elif method == "json_found_animals":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_FOUND_ANIMAL)
        rs = asm3.lostfound.get_foundanimal_last_days(dbo)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.utils.json(rs))

    elif method == "jsonp_found_animals":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_FOUND_ANIMAL)
        rs = asm3.lostfound.get_foundanimal_last_days(dbo)
        return ("application/javascript", 0, 0, "%s(%s);" % (post["callback"], asm3.utils.json(rs)))

    elif method == "xml_found_animals":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_FOUND_ANIMAL)
        rs = asm3.lostfound.get_foundanimal_last_days(dbo)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.html.xml(rs))

    elif method == "json_held_animals":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.animal.get_animals_hold(dbo)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.utils.json(rs))

    elif method == "xml_held_animals":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.animal.get_animals_hold(dbo)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.html.xml(rs))

    elif method == "jsonp_held_animals":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.animal.get_animals_hold(dbo)
        return ("application/javascript", 0, 0, "%s(%s);" % (post["callback"], asm3.utils.json(rs)))

    elif method == "json_lost_animals":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_LOST_ANIMAL)
        rs = asm3.lostfound.get_lostanimal_last_days(dbo)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.utils.json(rs))

    elif method == "jsonp_lost_animals":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_LOST_ANIMAL)
        rs = asm3.lostfound.get_lostanimal_last_days(dbo)
        return ("application/javascript", 0, 0, "%s(%s);" % (post["callback"], asm3.utils.json(rs)))

    elif method == "xml_lost_animals":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_LOST_ANIMAL)
        rs = asm3.lostfound.get_lostanimal_last_days(dbo)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.html.xml(rs))

    elif method == "json_recent_adoptions":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.movement.get_recent_adoptions(dbo)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.utils.json(rs))

    elif method == "jsonp_recent_adoptions":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.movement.get_recent_adoptions(dbo)
        return ("application/javascript", 0, 0, "%s(%s);" % (post["callback"], asm3.utils.json(rs)))

    elif method == "xml_recent_adoptions":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
        rs = asm3.movement.get_recent_adoptions(dbo)
        return set_cached_response(cache_key, account, "application/xml", 3600, 3600, asm3.html.xml(rs))

    elif method == "html_report":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_REPORT)
        crid = asm3.reports.get_id(dbo, title)
        p = asm3.reports.get_criteria_params(dbo, crid, post)
        rhtml = asm3.reports.execute(dbo, crid, username, p, toolbar=False)
        rhtml = asm3.utils.fix_relative_document_uris(dbo, rhtml)
        return set_cached_response(cache_key, account, "text/html", 600, 600, rhtml)

    elif method == "csv_mail" or method == "csv_report":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_REPORT)
        crid = asm3.reports.get_id(dbo, title)
        p = asm3.reports.get_criteria_params(dbo, crid, post)
        rows, cols = asm3.reports.execute_query(dbo, crid, username, p)
        mcsv = asm3.utils.csv(l, rows, cols, True)
        return set_cached_response(cache_key, account, "text/csv", 600, 600, mcsv)

    elif method == "json_report" or method == "json_mail":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_REPORT)
        crid = asm3.reports.get_id(dbo, title)
        p = asm3.reports.get_criteria_params(dbo, crid, post)
        rows, cols = asm3.reports.execute_query(dbo, crid, username, p)
        return set_cached_response(cache_key, account, "application/json", 600, 600, asm3.utils.json(rows))

    elif method == "jsonp_report" or method == "jsonp_mail":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_REPORT)
        crid = asm3.reports.get_id(dbo, title)
        p = asm3.reports.get_criteria_params(dbo, crid, post)
        rows, cols = asm3.reports.execute_query(dbo, crid, username, p)
        return ("application/javascript", 0, 0, "%s(%s);" % (post["callback"], asm3.utils.json(rows)))

    elif method == "jsonp_recent_changes":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
        sa = asm3.animal.get_recent_changes(dbo)
        return ("application/javascript", 0, 0, "%s(%s);" % (post["callback"], asm3.utils.json(sa)))

    elif method == "json_recent_changes":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
        sa = asm3.animal.get_recent_changes(dbo)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.utils.json(sa))

    elif method == "xml_recent_changes":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
        sa = asm3.animal.get_recent_changes(dbo)
        return set_cached_response(cache_key, account, "application/xml", 3600, 3600, asm3.html.xml(sa))

    elif method == "jsonp_shelter_animals":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
        sa = asm3.animal.get_shelter_animals(dbo)
        if strip_personal: sa = strip_personal_data(sa)
        return ("application/javascript", 0, 0, "%s(%s);" % (post["callback"], asm3.utils.json(sa)))

    elif method == "json_shelter_animals":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
        sa = asm3.animal.get_shelter_animals(dbo)
        if strip_personal: sa = strip_personal_data(sa)
        return set_cached_response(cache_key, account, "application/json", 3600, 3600, asm3.utils.json(sa))

    elif method == "xml_shelter_animals":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
        sa = asm3.animal.get_shelter_animals(dbo)
        if strip_personal: sa = strip_personal_data(sa)
        return set_cached_response(cache_key, account, "application/xml", 3600, 3600, asm3.html.xml(sa))

    elif method == "rss_timeline":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.VIEW_ANIMAL)
        RSS_LIMIT = 500
        rows = asm3.animal.get_timeline(dbo, RSS_LIMIT)
        h = []
        for r in rows:
            h.append( asm3.utils.rss_item( r["DESCRIPTION"], "%s/%s?id=%d" % (BASE_URL, r["LINKTARGET"], r["ID"]), "") )
        rssdocument = asm3.utils.rss("\n".join(h), _("Showing {0} timeline events.", l).format(RSS_LIMIT), BASE_URL, "")
        return set_cached_response(cache_key, account, "application/rss+xml", 3600, 3600, rssdocument)

    elif method == "upload_animal_image":
        asm3.users.check_permission_map(l, user.SUPERUSER, securitymap, asm3.users.ADD_MEDIA)
        asm3.media.attach_file_from_form(dbo, username, asm3.media.ANIMAL, int(animalid), post)
        return ("text/plain", 0, 0, "OK")

    elif method == "online_form_html":
        if formid == 0:
            raise asm3.utils.ASMError("method online_form_html requires a valid formid")
        return set_cached_response(cache_key, account, "text/html; charset=utf-8", 1800, 1800, asm3.onlineform.get_onlineform_html(dbo, formid))

    elif method == "online_form_json":
        if formid == 0:
            raise asm3.utils.ASMError("method online_form_json requires a valid formid")
        return set_cached_response(cache_key, account, "application/json; charset=utf-8", 1800, 1800, asm3.onlineform.get_onlineform_json(dbo, formid))

    elif method == "online_form_post":
        asm3.onlineform.insert_onlineformincoming_from_form(dbo, post, remoteip, useragent)
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
            signdate = "%s %s" % (python2display(l, dbo.now()), format_time(dbo.now()))
            asm3.media.sign_document(dbo, "service", formid, post["sig"], signdate, "signemail")
            asm3.media.create_log(dbo, "service", formid, "ES02", _("Document signed", l))
            if post.boolean("sendsigned"):
                m = asm3.media.get_media_by_id(dbo, formid)
                if m is None: raise asm3.utils.ASMError("cannot find %s" % formid)
                content = asm3.utils.bytes2str(asm3.dbfs.get_string_id(dbo, m.DBFSID))
                contentpdf = asm3.utils.html_to_pdf(dbo, content)
                attachments = [( "%s.pdf" % m.ID, "application/pdf", contentpdf )]
                fromaddr = asm3.configuration.email(dbo)
                asm3.utils.send_email(dbo, fromaddr, post["email"], "", "", _("Signed Document", l), m.MEDIANOTES, "plain", attachments)
            return ("text/plain", 0, 0, "OK")

    else:
        asm3.al.error("invalid method '%s'" % method, "service.handler", dbo)
        raise asm3.utils.ASMError("Invalid method '%s'" % method)

