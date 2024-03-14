"""
Module to support looking up microchips with check-a-chip type services.
Has to be done from the backend due to most of them being web interfaces with CORS restrictions,
or them requiring to go through their search page due to state, etc.
Since we're using parsing/scraping some of these functions may be brittle.
"""

import asm3.al
import asm3.cachemem
import asm3.utils
from asm3.typehints import ChipCheckResults, Database

from lxml import etree

class ChipCheckService(object):
    
    dbo: Database = None
    name: str = ""
    results: ChipCheckResults
    error: str = ""

    def __init__(self, dbo: Database, name: str):
        self.dbo = dbo
        self.name = name

    def search(self, chipnumber: str) -> ChipCheckResults:
        """ Override in subclass. Perform the search and return the results. """
        pass

class AAHAOrg(ChipCheckService):
    """ aaha.org (USA) """

    def __init__(self, dbo: Database):
        ChipCheckService.__init__(self, dbo, "aaha.org")

    def search(self, chipnumber: str) -> ChipCheckResults:
        headers = { "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0" }
        page = asm3.utils.get_url(f"https://www.aaha.org/your-pet/pet-microchip-lookup/microchip-search/?microchip_id={chipnumber}", headers=headers, timeout = 20)
        asm3.al.debug("got response from aaha.org (%s bytes)" % len(page["response"]), "AAHAOrg.search", self.dbo)
        self.results = []
        tree = etree.HTML(page["response"])
        for r in tree.xpath("//b-link"):
            if str(r.text).strip() == "": continue
            self.results.append( (r.get("href"), r.text) )
        
        asm3.al.info("results: %s" % self.results, "AAHAOrg.search", self.dbo)
        return self.results

class CheckAChipCom(ChipCheckService):
    """ checkachip.com (UK) """

    def __init__(self, dbo: Database):
        ChipCheckService.__init__(self, dbo, "checkachip.com")

    def search(self, chipnumber: str) -> ChipCheckResults:
        postdata = { "microchip_number": chipnumber, "are_you": "no", "phone_number": "" }
        asm3.al.debug("POST %s" % postdata, "CheckAChip.search", self.dbo)
        posted = asm3.utils.post_form("https://www.checkachip.com/microchipsearch/", postdata)
        asm3.al.debug("got response from checkachip.com (%s bytes)" % len(posted["response"]), "CheckAChip.search", self.dbo)

        self.results = []
        tree = etree.HTML(posted["response"])
        for r in tree.xpath("//p[@class='bull']/a"):
            self.results.append( (r.get("href"), r.text) )

        asm3.al.info("results: %s" % self.results, "CheckAChip.search", self.dbo)
        return self.results

class PetAddressComAu(ChipCheckService):
    """ petaddress.com.au (Australia) """
    def __init__(self, dbo: Database):
        ChipCheckService.__init__(self, dbo, "petaddress.com.au")

    def search(self, chipnumber: str) -> ChipCheckResults:
        postdata = { "txtNumber": chipnumber }
        searchpage = asm3.utils.get_url("http://www.petaddress.com.au", timeout = 5)
        asm3.al.debug("retrieved page at www.petaddress.com.au (%s bytes)" % len(searchpage["response"]), "PetAddressComAu.search", self.dbo)

        parse = asm3.utils.FormHTMLParser()
        parse.feed(searchpage["response"])
        for c in parse.controls:
            if "name" in c and c["name"] in ("__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION"):
                postdata[c["name"]] = c["value"]

        asm3.al.debug("POST %s" % postdata, "checkmicrochip.petaddress_com_au", self.dbo)
        posted = asm3.utils.post_form("http://www.petaddress.com.au/", postdata)
        asm3.al.debug("got response from www.petaddress.com.au (%s bytes)" % len(posted["response"]), "PetAddressComAu.search", self.dbo)

        self.error = ""
        self.results = []

        tree = etree.HTML(posted["response"])
        errx = tree.xpath("//span[@id='lblError']/font")
        if len(errx) > 0:
            self.error = errx[0].text
        for r in tree.xpath("//div[@class='ResultItem']/a"):
            self.results.append( (r.get("href"), r.text) )

        asm3.al.info("results: %s" % self.results, "PetAddressComAu.search", self.dbo)
        return self.results

LOCALE_MAP = {
    "en":    [ "aaha.org", AAHAOrg ],
    "en_AU": [ "petaddress.com.au", PetAddressComAu ],
    "en_GB": [ "checkachip.com", CheckAChipCom ]
}

def check(dbo: Database, locale: str, chipnumber: str) -> ChipCheckResults:
    """
    Check a microchip, choosing the appropriate service based on the locale.
    dbo is actually optional and can be passed as None when testing, the purpose of it being here is for logging.
    Uses a read-through memory cache.
    """
    cachekey = f"cac_{chipnumber}"
    TTL = 86400
    if (len(chipnumber) != 15 and len(chipnumber) != 9 and len(chipnumber) != 10):
        raise asm3.utils.ASMValidationError("Microchip numbers must be 9, 10 or 15 characters")
    results = asm3.cachemem.get(cachekey)
    if results is not None:
        return results
    if locale in LOCALE_MAP:
        results = { "name": LOCALE_MAP[locale][0], "results": LOCALE_MAP[locale][1](dbo).search(chipnumber) }
        asm3.cachemem.put(cachekey, results, TTL)
        return results
