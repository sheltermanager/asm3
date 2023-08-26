
"""
    Geocoding module. Functions to look up geocodes from addresses, and addresses from a postcode.
    Supports google and nominatim
"""

import asm3.al
import asm3.cachedisk
import asm3.configuration
import asm3.i18n
import asm3.utils
from asm3.sitedefs import BASE_URL, GEO_PROVIDER, GEO_PROVIDER_KEY, GEO_LOOKUP_TIMEOUT, GEO_SLEEP_AFTER, GEO_SMCOM_URL, GEO_SMCOM_ADDRESS_URL
from asm3.typehints import Database
from asm3.__version__ import VERSION

import json
import threading
import time

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

    def __init__(self, dbo: Database, address: str, town: str, county: str, postcode: str, country: str):
        self.dbo = dbo
        self.address = address
        self.town = town
        self.county = county
        self.postcode = postcode
        self.country = country
        self.build_url()

    def first_line(self, s: str) -> str:
        """ Returns just the first line of a string """
        if s.find("\n") == -1: return s
        return s[0:s.find("\n")]

    def address_hash(self) -> str:
        """ Produces a hash of the address to include with latlon values """
        addrhash = "%s%s%s%s" % (self.address, self.town, self.county, self.postcode)
        addrhash = addrhash.replace(" ", "").replace(",", "").replace("\n", "")
        if len(addrhash) > 220: addrhash = addrhash[0:220]
        return addrhash
    
    def build_url(self) -> None:
        """ Builds the URL """
        street = asm3.utils.encode_uri(self.first_line(self.address))
        address = asm3.utils.encode_uri(self.address)
        town = asm3.utils.encode_uri(self.town)
        county = asm3.utils.encode_uri(self.county)
        postcode = asm3.utils.encode_uri(self.postcode)
        country = asm3.utils.encode_uri(self.country)
        self.q = "%s,%s,%s,%s,%s" % (address, town, county, postcode, country)
        self.url = self.url.replace("{q}", self.q)
        self.url = self.url.replace("{street}", street).replace("{address}", address)
        self.url = self.url.replace("{town}", town).replace("{city}", town)
        self.url = self.url.replace("{county}", county).replace("{state}", county)
        self.url = self.url.replace("{postcode}", postcode).replace("{zipcode}", postcode)
        self.url = self.url.replace("{country}", country)
        self.url = self.url.replace("{locale}", self.dbo.locale)
        self.url = self.url.replace("{account}", self.dbo.database)
        self.url = self.url.replace("{key}", GEO_PROVIDER_KEY)

    def search(self) -> None:
        """ Calls the service, retrieves the data and sets self.response / self.json_response """
        headers = { "Referer": BASE_URL, "User-Agent": "Animal Shelter Manager %s" % VERSION }
        self.response = asm3.utils.get_url(self.url, headers=headers, timeout=GEO_LOOKUP_TIMEOUT)["response"]
        self.json_response = json.loads(self.response)

    def parse(self) -> str:
        """ Virtual method, returns latlon value by parsing response/json_response """
        raise NotImplementedError()

class Nominatim(GeoProvider):
    """ Geocoding support from Nominatim """
    def __init__(self, dbo: Database, address: str, town: str, county: str, postcode: str, country: str):
        self.url = GEO_NOMINATIM_URL
        GeoProvider.__init__(self, dbo, address, town, county, postcode, country)

    def parse(self) -> str:
        h = self.address_hash()
        j = self.json_response
        if len(j) == 0:
            asm3.al.debug("no response from nominatim for %s (response %s)" % (self.url, str(self.response)), "geo.parse_nominatim", self.dbo)
            return "0,0,%s" % h
        try:
            latlon = "%s,%s,%s" % (str(asm3.utils.strip_non_ascii(j[0]["lat"])), str(asm3.utils.strip_non_ascii(j[0]["lon"])), h)
            asm3.al.debug("contacted nominatim to get geocode for %s = %s" % (self.url, latlon), "geo.parse_nominatim", self.dbo)
            return latlon
        except Exception as err:
            asm3.al.error("couldn't find geocode in nominatim response: %s, %s" % (str(err), self.response), "geo.parse_nominatim", self.dbo)
            return "0,0,%s" % h

class Google(GeoProvider):
    """ Geocoding support from Google """
    def __init__(self, dbo: Database, address: str, town: str, county: str, postcode: str, country: str):
        self.url = GEO_GOOGLE_URL
        GeoProvider.__init__(self, dbo, address, town, county, postcode, country)

    def parse(self) -> str:
        h = self.address_hash()
        j = self.json_response
        if len(j) == 0:
            asm3.al.debug("no response from google for %s (response %s)" % (self.url, str(self.response)), "geo.parse_google", self.dbo)
            return "0,0,%s" % h
        try:
            loc = j["results"][0]["geometry"]["location"]
            latlon = "%s,%s,%s" % (str(loc["lat"]), str(loc["lng"]), h)
            asm3.al.debug("contacted google to get geocode for %s = %s" % (self.url, latlon), "geo.parse_google", self.dbo)
            return latlon
        except Exception as err:
            asm3.al.error("couldn't find geocode in google response. Status was %s: %s, %s" % (j["status"], str(err), self.response), "geo.parse_google", self.dbo)
            return "0,0,%s" % h

class Smcom(GeoProvider):
    """ Geocoding support from sheltermanager.com """
    def __init__(self, dbo: Database, address: str, town: str, county: str, postcode: str, country: str):
        self.url = GEO_SMCOM_URL
        GeoProvider.__init__(self, dbo, address, town, county, postcode, country)

    def parse(self) -> str:
        h = self.address_hash()
        j = self.json_response
        if len(j) == 0:
            asm3.al.debug("no response from smcom for %s (response %s)" % (self.url, str(self.response)), "geo.parse_smcom", self.dbo)
            return "0,0,%s" % h
        try:
            latlon = "%s,%s,%s" % (str(j["lat"]), str(j["lng"]), h)
            asm3.al.debug("contacted smcom to get geocode for %s = %s" % (self.url, latlon), "geo.parse_smcom", self.dbo)
            return latlon
        except:
            asm3.al.error("couldn't find geocode in smcom response. Response was %s" % self.response, "geo.parse_google", self.dbo)
            return "0,0,%s" % h


def address_hash(address: str, town: str, county: str, postcode: str, country: str) -> str:
    """ Produces a hash of the address to include with latlon values """
    addrhash = "%s%s%s%s%s" % (address, town, county, postcode, country)
    addrhash = addrhash.replace(" ", "").replace(",", "").replace("\n", "")
    if len(addrhash) > 220: addrhash = addrhash[0:220]
    return addrhash

def get_lat_long(dbo: Database, address: str, town: str, county: str, postcode: str, country: str = "") -> str:
    """
    Looks up a latitude and longitude from an address using the set geocoding provider 
    and returns them as a str "lat,long,hash"
    If no results were found, a zero lat and long are returned so that
    we know not to try and look this up again until the address hash changes.
    """

    if address.strip() == "":
        return None

    try:
        # Synchronise this process to a single thread to prevent
        # abusing our geo provider
        lat_long_lock.acquire()

        # Use the country passed. If no country was passed, check
        # if one has been set with the shelter details in settings,
        # otherwise use the country from the user's locale.
        if country is None or country == "": 
            country = asm3.configuration.organisation_country(dbo)
            if country == "": country = asm3.i18n.get_country(dbo.locale)

        g = None
        if GEO_PROVIDER == "nominatim":
            g = Nominatim(dbo, address, town, county, postcode, country)
        elif GEO_PROVIDER == "google":
            g = Google(dbo, address, town, county, postcode, country)
        elif GEO_PROVIDER == "smcom":
            g = Smcom(dbo, address, town, county, postcode, country)
        else:
            asm3.al.error("unrecognised geo provider: %s" % GEO_PROVIDER, "geo.get_lat_long", dbo)
            return None

        # Check the cache in case we already requested this address
        cachekey = "nom:%s" % g.q
        v = asm3.cachedisk.get(cachekey, dbo.database)
        if v is not None:
            asm3.al.debug("cache hit for address: %s = %s" % (cachekey, v), "geo.get_lat_long", dbo)
            return v

        # Call the service to get the data
        g.search()

        # Parse the response to a lat/long value
        latlon = g.parse()
        asm3.cachedisk.put(cachekey, dbo.database, latlon, 86400)

        if GEO_SLEEP_AFTER > 0:
            time.sleep(GEO_SLEEP_AFTER)

        return latlon

    except Exception as err:
        asm3.al.error(str(err), "geo.get_lat_long", dbo)
        return None

    finally:
        lat_long_lock.release()

def get_address(dbo: Database, postcode: str, country: str = "") -> str:
    """
    Looks up an address from a postcode and country.
    Currently smcom only as it requires on our postcode lookup service smcom_geo.
    Returns None if an error occurs during the lookup, otherwise returns a list of dictionaries of addresses for the postcode.
    """
    try:
        if GEO_SMCOM_ADDRESS_URL == "": return None

        # Check the cache in case we already requested this postcode
        cachekey = "addr:p=%sc=%s" % (postcode, country)
        v = asm3.cachedisk.get(cachekey, dbo.database)
        if v is not None:
            asm3.al.debug("cache hit for postcode/country: %s/%s = %s" % (postcode, country, v), "geo.get_address", dbo)
            return v

        # Build our postcode lookup url
        url = GEO_SMCOM_ADDRESS_URL
        url = url.replace("{postcode}", postcode).replace("{zipcode}", postcode)
        url = url.replace("{country}", country)
        url = url.replace("{key}", GEO_PROVIDER_KEY)

        headers = { "Referer": BASE_URL, "User-Agent": "Animal Shelter Manager %s" % VERSION }
        response = asm3.utils.get_url(url, headers=headers, timeout=GEO_LOOKUP_TIMEOUT)["response"]
        
        asm3.cachedisk.put(cachekey, dbo.database, v, 86400)

        asm3.al.debug("postcode lookup: %s/%s = %s" % (postcode, country, response), "geo.get_postcode", dbo)

        return response

    except Exception as err:
        asm3.al.error(str(err), "geo.get_postcode", dbo)
        return None

def get_postcode_lookup_available(l: str) -> bool:
    """ Returns True if postcode lookup is available for locale l. 
        Only includes countries with postcodes that are specific enough to get a street.
    """
    return GEO_SMCOM_ADDRESS_URL != "" and l in ( 
        "en_CA", "fr_CA",
        "en_GB", 
        "en_IE",
        "nl"
    )


