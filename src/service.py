#!/usr/bin/python

"""
Service functions for external applications. 

An account, username and password is mandatory for
sheltermanager accounts, username and password
for others.
"""

import al
import animal
import cachemem
import cachedisk
import configuration
import db
import dbfs
import dbupdate
import html
import media
import movement
import onlineform
import publish
import reports
import smcom
import users
import utils
from sitedefs import BASE_URL, MULTIPLE_DATABASES, MULTIPLE_DATABASES_TYPE, CACHE_SERVICE_RESPONSES, IMAGE_HOTLINKING_ONLY_FROM_DOMAIN

# Service methods that require authentication
AUTH_METHODS = [ 
    "csv_mail", "csv_report", "html_report", "rss_timeline", "upload_animal_image", 
    "xml_adoptable_animals", "json_adoptable_animals",
    "xml_recent_adoptions", "json_recent_adoptions", 
    "xml_shelter_animals", "json_shelter_animals", "jsonp_shelter_animals"
]

def flood_protect(method, remoteip, ttl, message = ""):
    """
    Checks to see if we've had a request for method from 
    remoteip since ttl seconds ago.
    If we haven't, we record this as the last time we saw a request
    from this ip address for that method. Otherwise, an error is thrown.
    method: The service method we're protecting
    remoteip: The ip address of the caller
    ttl: The protection period (one request per ttl seconds)
    """
    cache_key = "m%sr%s" % (method, remoteip.replace(", ", "")) # X-FORWARDED-FOR can be a list, remove commas
    v = cachemem.get(cache_key)
    #al.debug("method: %s, remoteip: %s, ttl: %d, cacheval: %s" % (method, remoteip, ttl, v), "service.flood_protect")
    if v is None:
        cachemem.put(cache_key, "x", ttl)
    else:
        if message == "":
            message = "You have already called '%s' in the last %d seconds, please wait before trying again." % (method, ttl)
        raise utils.ASMError(message)

def hotlink_protect(method, referer):
    domains = IMAGE_HOTLINKING_ONLY_FROM_DOMAIN.split(",")
    fromhldomain = False
    for d in domains:
        if d != "" and referer.find(d) != -1: fromhldomain = True
    if referer != "" and IMAGE_HOTLINKING_ONLY_FROM_DOMAIN != "" and not fromhldomain:
        raise utils.ASMPermissionError("Hotlinking to %s from %s is forbidden" % (method, referer))

def get_cached_response(cache_key):
    """
    Gets a service call response from the disk cache based on its key.
    If no entry is found, None is returned.
    """
    if not CACHE_SERVICE_RESPONSES: return None
    response = cachedisk.get(cache_key)
    if response is None: return None
    #al.debug("GET: %s (%d bytes)" % (cache_key, len(response[2])), "service.get_cached_response")
    return response

def set_cached_response(cache_key, mime, clientage, serverage, content):
    """
    Sets a service call response in the cache and returns
    the response so methods can use this as a passthrough
    to return the response.
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

def handler(post, remoteip, referer):
    """
    Handles the various service method types.
    data: The GET/POST parameters 
    return value is a tuple containing MIME type, max-age, content
    """
    # Database info
    dbo = db.DatabaseInfo()

    # Get service parameters
    account = post["account"]
    username = post["username"]
    password = post["password"]
    method = post["method"]
    animalid = post.integer("animalid")
    formid = post.integer("formid")
    title = post["title"]
    cache_key = "a" + account + "u" + username + "p" + password + "m" + method + "a" + str(animalid) + "f" + str(formid) + "t" + title
    
    # cache keys aren't allowed spaces
    cache_key = cache_key.replace(" ", "")

    # Do we have a cached response for these parameters?
    cached_response = get_cached_response(cache_key)
    if cached_response is not None:
        al.debug("cache hit for %s/%s/%s/%s" % (account, method, animalid, title), "service.handler")
        return cached_response

    # Are we dealing with multiple databases, but no account was specified?
    if account == "" and MULTIPLE_DATABASES:
        return ("text/plan", 0, "ERROR: No database/alias specified")

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
            if dbo.database == "FAIL" or dbo.database == "DISABLED": 
                al.error("auth failed - invalid smaccount %s from %s" % (account, remoteip), "service.handler", dbo)
                return ("text/plain", 0, "ERROR: Invalid database")

    # Do any database updates need doing in this db?
    if dbupdate.check_for_updates(dbo):
        dbupdate.perform_updates(dbo)

    # Does the method require us to authenticate? If so, do it.
    user = None
    securitymap = ""
    if method in AUTH_METHODS:
        user = users.authenticate(dbo, username, password)
        if user is None:
            al.error("auth failed - %s/%s is not a valid username/password from %s" % (username, password, remoteip), "service.handler", dbo)
            return ("text/plain", 0, "ERROR: Invalid username and password")
        securitymap = users.get_security_map(dbo, user["USERNAME"])

    # Get the preferred locale for the site
    l = configuration.locale(dbo)
    dbo.locale = l
    al.info("call %s->%s [%s %s]" % (username, method, str(animalid), title), "service.handler", dbo)

    if method =="animal_image":
        hotlink_protect("animal_image", referer)
        if animalid == "" or utils.cint(animalid) == 0:
            al.error("animal_image failed, %s is not an animalid" % str(animalid), "service.handler", dbo)
            return ("text/plain", 0, "ERROR: Invalid animalid")
        else:
            seq = post.integer("seq")
            if seq == 0: seq = 1
            mm = media.get_media_by_seq(dbo, media.ANIMAL, utils.cint(animalid), seq)
            if len(mm) == 0:
                return set_cached_response(cache_key, "image/jpeg", 86400, 120, dbfs.get_string(dbo, "nopic.jpg", "/reports"))
            else:
                return set_cached_response(cache_key, "image/jpeg", 86400, 120, dbfs.get_string(dbo, mm[0]["MEDIANAME"]))

    elif method == "animal_view":
        if animalid == "" or utils.cint(animalid) == 0:
            al.error("animal_view failed, %s is not an animalid" % str(animalid), "service.handler", dbo)
            return ("text/plain", 0, "ERROR: Invalid animalid")
        else:
            return set_cached_response(cache_key, "text/html", 120, 120, publish.get_animal_view(dbo, int(animalid)))

    elif method =="dbfs_image":
        hotlink_protect("dbfs_image", referer)
        return set_cached_response(cache_key, "image/jpeg", 86400, 120, dbfs.get_string_filepath(dbo, title))

    elif method =="extra_image":
        hotlink_protect("extra_image", referer)
        return set_cached_response(cache_key, "image/jpeg", 86400, 120, dbfs.get_string(dbo, title, "/reports"))

    elif method == "json_adoptable_animals":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        pc = publish.PublishCriteria(configuration.publisher_presets(dbo))
        rs = publish.get_animal_data(dbo, pc, True)
        return set_cached_response(cache_key, "application/json", 3600, 3600, html.json(rs))

    elif method == "xml_adoptable_animals":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        pc = publish.PublishCriteria(configuration.publisher_presets(dbo))
        rs = publish.get_animal_data(dbo, pc, True)
        return set_cached_response(cache_key, "application/xml", 3600, 3600, html.xml(rs))

    elif method == "json_recent_adoptions":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        rs = movement.get_recent_adoptions(dbo)
        return set_cached_response(cache_key, "application/json", 3600, 3600, html.json(rs))

    elif method == "xml_recent_adoptions":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        rs = movement.get_recent_adoptions(dbo)
        return set_cached_response(cache_key, "application/xml", 3600, 3600, html.xml(rs))

    elif method == "html_report":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_REPORT)
        crid = reports.get_id(dbo, title)
        p = reports.get_criteria_params(dbo, crid, post.data)
        rhtml = reports.execute(dbo, crid, username, p)
        return set_cached_response(cache_key, "text/html", 3600, 3600, rhtml)

    elif method == "csv_mail" or method == "csv_report":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_REPORT)
        crid = reports.get_id(dbo, title)
        p = reports.get_criteria_params(dbo, crid, post.data)
        rows, cols = reports.execute_query(dbo, crid, username, p)
        mcsv = utils.csv(rows, cols, True)
        return set_cached_response(cache_key, "text/csv", 3600, 3600, mcsv)

    elif method == "jsonp_shelter_animals":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        sa = animal.get_animal_find_simple(dbo, "", "shelter")
        return set_cached_response(cache_key, "application/javascript", 3600, 3600, str(post["callback"]) + "(" + html.json(sa) + ")")

    elif method == "json_shelter_animals":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        sa = animal.get_animal_find_simple(dbo, "", "shelter")
        return set_cached_response(cache_key, "application/json", 3600, 3600, html.json(sa))

    elif method == "xml_shelter_animals":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        sa = animal.get_animal_find_simple(dbo, "", "shelter")
        return set_cached_response(cache_key, "application/xml", 3600, 3600, html.xml(sa))

    elif method == "rss_timeline":
        users.check_permission_map(l, user["SUPERUSER"], securitymap, users.VIEW_ANIMAL)
        return set_cached_response(cache_key, "application/rss+xml", 3600, 3600, html.timeline_rss(dbo))

    elif method == "upload_animal_image":
        flood_protect("upload_animal_image", remoteip, 60)
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
        flood_protect("online_form_post", remoteip, 60)
        onlineform.insert_onlineformincoming_from_form(dbo, post, remoteip)
        redirect = post["redirect"]
        if redirect == "":
            redirect = BASE_URL + "/static/pages/form_submitted.html"
        return ("redirect", 0, redirect)

    else:
        al.error("invalid method '%s'" % method, "service.handler", dbo)
        raise utils.ASMError("Invalid method '%s'" % method)

