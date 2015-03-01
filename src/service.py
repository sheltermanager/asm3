#!/usr/bin/python

"""
Service functions for external applications. 

An account, username and password is mandatory for
sheltermanager accounts, username and password
for others.
"""

import al
import animal
import cache
import configuration
import db
import dbfs
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
    "upload_animal_image", 
    "json_shelter_animals", "jsonp_shelter_animals", "xml_shelter_animals", 
    "html_report", "csv_mail", 
    "xml_recent_adoptions", "json_recent_adoptions", 
    "xml_adoptable_animals", "json_adoptable_animals"  
]

def get_cached_response(cache_key):
    """
    Gets a service call response from the cache based on its key.
    If no entry is found, None is returned.
    """
    if not CACHE_SERVICE_RESPONSES:
        return None
    return cache.get(cache_key)

def set_cached_response(cache_key, mime, maxage, content):
    """
    Sets a service call response in the cache and returns
    the response so methods can use this as a passthrough
    to return the response.
    """
    response = (mime, maxage, content)
    if not CACHE_SERVICE_RESPONSES:
        return response
    cache.put(cache_key, response, maxage)
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

    # Does the method require us to authenticate? If so, do it.
    user = None
    if method in AUTH_METHODS:
        user = users.authenticate(dbo, username, password)
        if user is None:
            al.error("auth failed - %s/%s is not a valid username/password from %s" % (username, password, remoteip), "service.handler", dbo)
            return ("text/plain", 0, "ERROR: Invalid username and password")

    # Get the preferred locale for the site
    dbo.locale = configuration.locale(dbo)
    al.info("call %s->%s [%s %s]" % (username, method, str(animalid), title), "service.handler", dbo)

    if method =="animal_image":
        # If we have a hotlinking restriction, enforce it
        if referer != "" and IMAGE_HOTLINKING_ONLY_FROM_DOMAIN != "" and referer.find(IMAGE_HOTLINKING_ONLY_FROM_DOMAIN) == -1:
            raise utils.ASMPermissionError("Image hotlinking is forbidden.")
        if animalid == "" or utils.cint(animalid) == 0:
            al.error("animal_image failed, %s is not an animalid" % str(animalid), "service.handler", dbo)
            return ("text/plain", 0, "ERROR: Invalid animalid")
        else:
            seq = post.integer("seq")
            if seq == 0: seq = 1
            mm = media.get_media_by_seq(dbo, media.ANIMAL, utils.cint(animalid), seq)
            if len(mm) == 0:
                return ("image/jpeg", 86400, dbfs.get_string(dbo, "nopic.jpg", "/reports"))
            else:
                return ("image/jpeg", 86400, dbfs.get_string(dbo, mm[0]["MEDIANAME"]))

    elif method =="extra_image":
        return ("image/jpeg", 86400, dbfs.get_string(dbo, title, "/reports"))

    elif method == "json_adoptable_animals":
        pc = publish.PublishCriteria(configuration.publisher_presets(dbo))
        rs = publish.get_animal_data(dbo, pc, True)
        return set_cached_response(cache_key, "application/json", 3600, html.json(rs))

    elif method == "xml_adoptable_animals":
        pc = publish.PublishCriteria(configuration.publisher_presets(dbo))
        rs = publish.get_animal_data(dbo, pc, True)
        return set_cached_response(cache_key, "application/xml", 3600, html.xml(rs))

    elif method == "json_recent_adoptions":
        rs = movement.get_recent_adoptions(dbo)
        return set_cached_response(cache_key, "application/json", 3600, html.json(rs))

    elif method == "xml_recent_adoptions":
        rs = movement.get_recent_adoptions(dbo)
        return set_cached_response(cache_key, "application/xml", 3600, html.xml(rs))

    elif method == "html_report":
        crid = reports.get_id(dbo, title)
        p = reports.get_criteria_params(dbo, crid, post.data)
        rhtml = reports.execute(dbo, crid, username, p)
        return set_cached_response(cache_key, "text/html", 3600, rhtml)

    elif method == "csv_mail":
        crid = reports.get_id(dbo, title)
        p = reports.get_criteria_params(dbo, crid, post.data)
        rows, cols = reports.execute_query(dbo, crid, username, p)
        mcsv = utils.csv(rows, cols, True)
        return set_cached_response(cache_key, "text/csv", 3600, mcsv)

    elif method == "jsonp_shelter_animals":
        sa = animal.get_animal_find_simple(dbo, "", "shelter")
        return set_cached_response(cache_key, "application/javascript", 3600, str(post["callback"]) + "(" + html.json(sa) + ")")

    elif method == "json_shelter_animals":
        sa = animal.get_animal_find_simple(dbo, "", "shelter")
        return set_cached_response(cache_key, "application/json", 3600, html.json(sa))

    elif method == "xml_shelter_animals":
        sa = animal.get_animal_find_simple(dbo, "", "shelter")
        return set_cached_response(cache_key, "application/xml", 3600, html.xml(sa))

    elif method == "upload_animal_image":
        media.attach_file_from_form(dbo, username, media.ANIMAL, int(animalid), post)
        return ("text/plain", 0, "OK")

    elif method == "online_form_html":
        if formid == 0:
            raise utils.ASMError("method online_form_html requires a valid formid")
        return set_cached_response(cache_key, "text/html; charset=utf-8", 120, onlineform.get_onlineform_html(dbo, formid))

    elif method == "online_form_post":
        onlineform.insert_onlineformincoming_from_form(dbo, post, remoteip)
        redirect = post["redirect"]
        if redirect == "":
            redirect = BASE_URL + "/static/pages/form_submitted.html"
        return ("redirect", 0, redirect)

    else:
        al.error("invalid method '%s'" % method, "service.handler", dbo)
        raise utils.ASMError("Invalid method '%s'" % method)

