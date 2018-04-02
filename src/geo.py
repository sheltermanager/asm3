#!/usr/bin/python

"""
    Geocoding module. Supports google and nominatim
"""

import al
import cachemem
import json
import i18n
import threading
import time
import utils
from sitedefs import BASE_URL, BULK_GEO_PROVIDER, BULK_GEO_PROVIDER_KEY, BULK_GEO_NOMINATIM_URL, BULK_GEO_GOOGLE_URL, BULK_GEO_LOOKUP_TIMEOUT, BULK_GEO_SLEEP_AFTER

lat_long_lock = threading.Lock()

def get_lat_long(dbo, address, town, county, postcode, country = None):
    """
    Looks up a latitude and longitude from an address using GEOCODE_URL
    and returns them as lat,long,hash
    If no results were found, a zero lat and long are returned so that
    we know not to try and look this up again until the address hash changes.
    NB: dbo is only used for contextual reference in logging and obtaining locale, 
        no database calls are made by any of this code.
    """

    if address.strip() == "":
        return None

    try:
        # Synchronise this process to a single thread to prevent
        # abusing our geo provider
        lat_long_lock.acquire()

        url = ""
        h = address_hash(address, town, county, postcode)

        if country is None: 
            country = i18n.get_country(dbo.locale)

        if BULK_GEO_PROVIDER == "nominatim":
            q = normalise_nominatim(address, town, county, postcode, country)
            url = BULK_GEO_NOMINATIM_URL.replace("{q}", q)
        elif BULK_GEO_PROVIDER == "google":
            q = normalise_google(address, town, county, postcode, country)
            url = BULK_GEO_GOOGLE_URL.replace("{q}", q)
            if BULK_GEO_PROVIDER_KEY != "": 
                url += "&key=%s" % BULK_GEO_PROVIDER_KEY
        else:
            al.error("unrecognised geo provider: %s" % BULK_GEO_PROVIDER, "geo.get_lat_long", dbo)

        al.debug("looking up geocode for address: %s" % q, "geo.get_lat_long", dbo)
        
        key = "nom:" + q
        v = cachemem.get(key)
        if v is not None:
            al.debug("cache hit for address: %s = %s" % (q, v), "geo.get_lat_long", dbo)
            return v

        jr = utils.get_url(url, headers = { "Referer": BASE_URL }, timeout = BULK_GEO_LOOKUP_TIMEOUT)["response"]
        j = json.loads(jr)

        latlon = None
        if BULK_GEO_PROVIDER == "nominatim":
            latlon = parse_nominatim(dbo, jr, j, q, h)
        elif BULK_GEO_PROVIDER == "google":
            latlon = parse_google(dbo, jr, j, q, h)

        if BULK_GEO_SLEEP_AFTER > 0:
            time.sleep(BULK_GEO_SLEEP_AFTER)

        cachemem.put(key, latlon, 86400)
        return latlon

    except Exception as err:
        al.error(str(err), "geo.get_lat_long", dbo)
        return None

    finally:
        lat_long_lock.release()

def address_hash(address, town, city, postcode):
    addrhash = "%s%s%s%s" % (address, town, city, postcode)
    addrhash = addrhash.replace(" ", "").replace(",", "").replace("\n", "")
    if len(addrhash) > 220: addrhash = addrhash[0:220]
    return addrhash

def parse_nominatim(dbo, jr, j, q, h):
    if len(j) == 0:
        al.debug("no response from nominatim for %s (response %s)" % (q, str(jr)), "geo.parse_nominatim", dbo)
        return "0,0,%s" % h
    try:
        latlon = "%s,%s,%s" % (str(utils.strip_non_ascii(j[0]["lat"])), str(utils.strip_non_ascii(j[0]["lon"])), h)
        al.debug("contacted nominatim to get geocode for %s = %s" % (q, latlon), "geo.parse_nominatim", dbo)
        return latlon
    except Exception as err:
        al.error("couldn't find geocode in nominatim response: %s, %s" % (str(err), jr), "geo.parse_nominatim", dbo)
        return "0,0,%s" % h
    
def parse_google(dbo, jr, j, q, h):
    if len(j) == 0:
        al.debug("no response from google for %s (response %s)" % (q, str(jr)), "geo.parse_google", dbo)
        return "0,0,%s" % h
    try:
        loc = j["results"][0]["geometry"]["location"]
        latlon = "%s,%s,%s" % (str(loc["lat"]), str(loc["lng"]), h)
        al.debug("contacted google to get geocode for %s = %s" % (q, latlon), "geo.parse_google", dbo)
        return latlon
    except Exception as err:
        al.error("couldn't find geocode in google response. Status was %s: %s, %s" % (j["status"], str(err), jr), "geo.parse_google", dbo)
        return "0,0,%s" % h

def normalise_nominatim(address, town, county, postcode, country):
    q = address + "," + town + "," + country
    q = utils.html_to_uri(q)
    q = q.replace("&", "").replace("=", "").replace("^", "").replace(".", "")
    q = q.replace("\r", "").replace("\n", ",").replace(", ", ",").replace(" ", "+")
    q = q.lower()
    return q

def normalise_google(address, town, county, postcode, country):
    q = address + "," + town + "," + county +"," + postcode + "," + country
    q = utils.html_to_uri(q)
    q = q.replace("&", "").replace("=", "").replace("^", "").replace(".", "")
    q = q.replace("\r", "").replace("\n", ",").replace(", ", ",").replace(" ", "+")
    q = q.lower()
    return q


