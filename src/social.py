#!/usr/bin/python

import al
import animal
import configuration
import dbfs
import html
import log
import sys
import utils
import wordprocessor
from i18n import _
from sitedefs import BASE_URL, FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET

def post_animal_facebook(dbo, user, oauth_code, oauth_state):
    """
    Post an animal to Facebook
    oauth_code: Provided by FB redirect, code to obtain user's access token
    oauth_state: Provided by FB redirect, from our original link the animal ID to post
    """

    # Request an access token for the logged in Facebook user from the
    # oauth code we were given.
    try:
        client_id = FACEBOOK_CLIENT_ID
        client_secret = FACEBOOK_CLIENT_SECRET
        redirect_uri = BASE_URL + "/animal_facebook"
        fb_url = "https://graph.facebook.com/oauth/access_token?client_id=%s&redirect_uri=%s&client_secret=%s&code=%s" %  \
            (client_id, redirect_uri, client_secret, oauth_code)

        al.debug("FB access token request: " + fb_url, "social.post_animal_facebook", dbo)
        access_token = utils.get_url(fb_url)["response"]
        al.debug("FB access token response: " + access_token, "social.post_animal_facebook", dbo)

    except Exception,err:
        em = str(err)
        al.error("Failed getting facebook access token: %s" % em, "social.post_animal_facebook", dbo)
        raise utils.ASMValidationError("Failed getting Facebook access token.")

    # Read the access token from the response
    eq = access_token.find("=")
    fa = access_token.find("&")
    if fa == -1: 
        fa = len(access_token)
    access_token = access_token[eq+1:fa]

    # Who are we posting as? Choices are me or page
    post_as = configuration.facebook_post_as(dbo)

    # Where are we posting to? This will be "me" or a page id
    post_to = post_as

    # Partial page name if one has been set
    page_name = configuration.facebook_pagename(dbo)

    # If we're set to post as the page, but no page name has been
    # given, that's a showstopper.
    if post_as == "page" and page_name == "":
        raise utils.ASMValidationError("Set to post as page, but no page name has been set.")

    # If the user has set a page name to post to, then try and 
    # find the page id and access token for it in their list of 
    # available accounts
    page_access_token = ""
    page_id = ""
    accounts_list = ""
    if page_name != "":
        try:
            fb_url = "https://graph.facebook.com/me/accounts?access_token=%s" % access_token
            al.debug("FB accounts list request: " + fb_url, "social.post_animal_facebook", dbo)
            accounts_list = utils.get_url(fb_url)["response"]
            json_response = html.json_parse(accounts_list)
            al.debug("FB accounts list response: %s" + accounts_list, "social.post_animal_facebook", dbo)
            al.debug("FB page name to look for '%s'" % page_name, "social.post_animal_facebook", dbo)
            for item in json_response["data"]:
                if item["name"].find(page_name) != -1:
                    page_id = item["id"]
                    page_access_token = item["access_token"]
                    al.debug("FB page access token and id found: %s, %s" % (page_access_token, page_id), "social.post_animal_facebook", dbo)
                    break
        except Exception,err:
            em = str(err)
            al.error("Failed getting facebook access token for page: %s" % em, "social.post_animal_facebook", dbo)
            raise utils.ASMValidationError("Failed getting Facebook access token for page admin.")

    # Did we find the page? If not, stop now
    if page_name != "" and page_id == "":
        raise utils.ASMValidationError("Could not find page '%s' in Facebook user accounts list (%s)" % (page_name, accounts_list))

    # If we're posting as the page, we can only post to the page.
    # switch us to post using the page's access token
    if post_as == "page":
        post_to = page_id
        access_token = page_access_token

    # If we're posting as us, but to a page, post to the page
    # but stick with the user's access_token
    if page_name != "":
        post_to = page_id

    # Grab the animal details
    a = animal.get_animal(dbo, utils.cint(oauth_state[1:]))

    # Bail out if we have a problem
    if a is None: 
        raise utils.ASMValidationError("Facebook response did not contain a valid animal ID (got %s)" % oauth_state[1:])

    # Generate the body of the post from our facebook template
    tags = wordprocessor.animal_tags(dbo, a)
    template = configuration.facebook_template(dbo)
    posttext = wordprocessor.substitute_tags(template, tags, False, "$$", "$$")

    # Post on the wall
    try:

        l = dbo.locale
        fb_url = "https://graph.facebook.com/%s/photos?access_token=%s" % (post_to, access_token)
        al.debug("FB posting photo and text '%s' to '%s' at %s" % (posttext, page_name, fb_url), "social.post_animal_facebook", dbo)
        imagedata = dbfs.get_string(dbo, a["WEBSITEMEDIANAME"])
        message = utils.decode_html(posttext).encode("utf-8")
        r = utils.post_multipart(fb_url, { "message": message }, {"source": ("pic.jpg", imagedata, "image/jpeg")})
        al.debug("FB response: %s" % r["response"], "social.post_animal_facebook", dbo)

        # If the option is on and all was ok, make a note in the log
        if configuration.facebook_log(dbo):
            al.debug("FB writing entry to animal log: %s %s" % (a["SHELTERCODE"], a["ANIMALNAME"]), "social.post_animal_facebook", dbo)
            log.add_log(dbo, user, log.ANIMAL, utils.cint(oauth_state[1:]), configuration.facebook_log_type(dbo),
                _("{0} {1}: posted to Facebook page {2} by {3}", l).format(a["SHELTERCODE"], a["ANIMALNAME"], page_name, 
                user))

    except Exception,err:
        em = str(err)
        al.error("Failed posting photo to facebook: %s" % em, "social.post_animal_facebook", dbo, sys.exc_info())
        raise utils.ASMValidationError("Failed posting photo and details to Facebook.")


