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
from sitedefs import BASE_URL, GEO_PROVIDER, GEO_PROVIDER_KEY, GEO_LOOKUP_TIMEOUT, GEO_SLEEP_AFTER, GEO_SMCOM_URL

GEO_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search?format=json&street={street}&city={city}&state={state}&postalcode={zipcode}&country={country}"
GEO_GOOGLE_URL = "https://maps.googleapis.com/maps/api/geocode/json?address={q}&sensor=false&key={key}"

lat_long_lock = threading.Lock()

class GeoProvider(object):
    """ Geocoding provider base class """
    dbo = None
    address = ""
    town = ""
    county = ""
    postcode = ""
    country = ""
    url = ""
    response = ""
    json_response = ""

    def __init__(self, dbo, address, town, county, postcode, country):
        self.dbo = dbo
        self.address = address
        self.town = town
        self.county = county
        self.postcode = postcode
        self.country = country
        self.build_url()

    def uri_encode(self, s):
        """ Converts a parameter to URI encoding """
        s = utils.html_to_uri(s) # Convert HTML entities to URI encoded entities &#255; becomes %ff
        return s.replace("&", "").replace("=", "").replace("^", "").replace(".", "").replace("\r", "").replace("\n", ",").replace(", ", ",").replace(" ", "+")

    def first_line(self, s):
        """ Returns just the first line of a string """
        if s.find("\n") == -1: return s
        return s[0:s.find("\n")]

    def address_hash(self):
        """ Produces a hash of the address to include with latlon values """
        addrhash = "%s%s%s%s" % (self.address, self.town, self.county, self.postcode)
        addrhash = addrhash.replace(" ", "").replace(",", "").replace("\n", "")
        if len(addrhash) > 220: addrhash = addrhash[0:220]
        return addrhash
    
    def build_url(self):
        """ Builds the URL """
        street = self.uri_encode(self.first_line(self.address))
        address = self.uri_encode(self.address)
        town = self.uri_encode(self.town)
        county = self.uri_encode(self.county)
        postcode = self.uri_encode(self.postcode)
        country = self.uri_encode(self.country)
        self.q = "%s,%s,%s,%s,%s" % (address, town, county, postcode, country)
        self.url = self.url.replace("{q}", self.q)
        self.url = self.url.replace("{street}", street).replace("{address}", address)
        self.url = self.url.replace("{town}", town).replace("{city}", town)
        self.url = self.url.replace("{county}", county).replace("{state}", county)
        self.url = self.url.replace("{postcode}", postcode).replace("{zipcode}", postcode)
        self.url = self.url.replace("{country}", country)
        self.url = self.url.replace("{locale}", self.dbo.locale)
        self.url = self.url.replace("{key}", GEO_PROVIDER_KEY)

    def search(self):
        """ Calls the service, retrieves the data and sets self.response / self.json_response """
        headers = { "Referer": BASE_URL, "User-Agent": "Animal Shelter Manager %s" % i18n.VERSION }
        self.response = utils.get_url(self.url, headers=headers, timeout=GEO_LOOKUP_TIMEOUT)["response"]
        self.json_response = json.loads(self.response)

    def parse(self):
        """ Virtual method, returns latlon value by parsing response/json_response """
        pass

class Nominatim(GeoProvider):
    """ Geocoding support from Nominatim """
    def __init__(self, dbo, address, town, county, postcode, country):
        self.url = GEO_NOMINATIM_URL
        GeoProvider.__init__(self, dbo, address, town, county, postcode, country)

    def parse(self):
        h = self.address_hash()
        j = self.json_response
        if len(j) == 0:
            al.debug("no response from nominatim for %s (response %s)" % (self.url, str(self.response)), "geo.parse_nominatim", self.dbo)
            return "0,0,%s" % h
        try:
            latlon = "%s,%s,%s" % (str(utils.strip_non_ascii(j[0]["lat"])), str(utils.strip_non_ascii(j[0]["lon"])), h)
            al.debug("contacted nominatim to get geocode for %s = %s" % (self.url, latlon), "geo.parse_nominatim", self.dbo)
            return latlon
        except Exception as err:
            al.error("couldn't find geocode in nominatim response: %s, %s" % (str(err), self.response), "geo.parse_nominatim", self.dbo)
            return "0,0,%s" % h

class Google(GeoProvider):
    """ Geocoding support from Google """
    def __init__(self, dbo, address, town, county, postcode, country):
        self.url = GEO_GOOGLE_URL
        GeoProvider.__init__(self, dbo, address, town, county, postcode, country)

    def parse(self):
        h = self.address_hash()
        j = self.json_response
        if len(j) == 0:
            al.debug("no response from google for %s (response %s)" % (self.url, str(self.response)), "geo.parse_google", self.dbo)
            return "0,0,%s" % h
        try:
            loc = j["results"][0]["geometry"]["location"]
            latlon = "%s,%s,%s" % (str(loc["lat"]), str(loc["lng"]), h)
            al.debug("contacted google to get geocode for %s = %s" % (self.url, latlon), "geo.parse_google", self.dbo)
            return latlon
        except Exception as err:
            al.error("couldn't find geocode in google response. Status was %s: %s, %s" % (j["status"], str(err), self.response), "geo.parse_google", self.dbo)
            return "0,0,%s" % h

class Smcom(GeoProvider):
    """ Geocoding support from sheltermanager.com """
    def __init__(self, dbo, address, town, county, postcode, country):
        self.url = GEO_SMCOM_URL
        GeoProvider.__init__(self, dbo, address, town, county, postcode, country)

    def parse(self):
        h = self.address_hash()
        j = self.json_response
        if len(j) == 0:
            al.debug("no response from smcom for %s (response %s)" % (self.url, str(self.response)), "geo.parse_smcom", self.dbo)
            return "0,0,%s" % h
        try:
            latlon = "%s,%s,%s" % (str(j["lat"]), str(j["lng"]), h)
            al.debug("contacted smcom to get geocode for %s = %s" % (self.url, latlon), "geo.parse_smcom", self.dbo)
            return latlon
        except Exception as err:
            al.error("couldn't find geocode in smcom response. Response was %s" % self.response, "geo.parse_google", self.dbo)
            return "0,0,%s" % h


def address_hash(address, town, county, postcode):
    """ Produces a hash of the address to include with latlon values """
    addrhash = "%s%s%s%s" % (address, town, county, postcode)
    addrhash = addrhash.replace(" ", "").replace(",", "").replace("\n", "")
    if len(addrhash) > 220: addrhash = addrhash[0:220]
    return addrhash

def get_lat_long(dbo, address, town, county, postcode, country = None):
    """
    Looks up a latitude and longitude from an address using the set geocoding provider 
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

        if country is None: 
            country = i18n.get_country(dbo.locale)

        g = None
        if GEO_PROVIDER == "nominatim":
            g = Nominatim(dbo, address, town, county, postcode, country)
        elif GEO_PROVIDER == "google":
            g = Google(dbo, address, town, county, postcode, country)
        elif GEO_PROVIDER == "smcom":
            g = Smcom(dbo, address, town, county, postcode, country)
        else:
            al.error("unrecognised geo provider: %s" % GEO_PROVIDER, "geo.get_lat_long", dbo)
            return None

        # Check the cache in case we already requested this address
        cachekey = "nom:" + g.q
        v = cachemem.get(cachekey)
        if v is not None:
            al.debug("cache hit for address: %s = %s" % (cachekey, v), "geo.get_lat_long", dbo)
            return v

        # Call the service to get the data
        g.search()

        # Parse the response to a lat/long value
        latlon = g.parse()
        cachemem.put(cachekey, latlon, 86400)

        if GEO_SLEEP_AFTER > 0:
            time.sleep(GEO_SLEEP_AFTER)

        return latlon

    except Exception as err:
        al.error(str(err), "geo.get_lat_long", dbo)
        return None

    finally:
        lat_long_lock.release()


