
import asm3.al
import asm3.configuration
import asm3.i18n
import asm3.users

from asm3.sitedefs import ADMIN_EMAIL, BASE_URL, MULTIPLE_DATABASES, SMTP_SERVER, FROM_ADDRESS, HTML_TO_PDF, URL_NEWS

import web062 as web

import base64
import datetime
import decimal
import hashlib
import json as extjson
import os
import re
import requests
import smtplib
import subprocess
import sys
import tempfile
import time
import uuid
import zipfile

import _thread as thread
import urllib.request as urllib2
import urllib.parse
from io import BytesIO, StringIO
from html.parser import HTMLParser
from html import unescape
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import make_msgid, formatdate
import email.encoders as Encoders

# Global reference to the Python websession. This is used to allow
# debug mode with webpy by keeping a global single copy of the
# session (in debug mode, module reloading means you'd create two
# session objects)
websession = None

# Global reference to the current code path
PATH = os.path.dirname(os.path.abspath(__file__)) + os.sep + ".." + os.sep

class PostedData(object):
    """
    Helper class for reading fields from the web.py web.input object
    and doing type coercion.
    """
    data = None
    locale = None

    def __init__(self, data, locale):
        self.data = data
        self.locale = locale

    def boolean(self, field):
        if field not in self.data:
            return 0
        if self.data[field] == "checked" or self.data[field] == "on":
            return 1
        else:
            return 0

    def date(self, field):
        """ Returns a date key from a datafield """
        if field in self.data:
            return asm3.i18n.display2python(self.locale, self.data[field])
        else:
            return None

    def datetime(self, datefield, timefield):
        """ Returns a datetime field """
        if datefield in self.data:
            d = asm3.i18n.display2python(self.locale, self.data[datefield])
            if d is None: return None
            if timefield in self.data:
                tbits = self.data[timefield].split(":")
                hour = 0
                minute = 0
                second = 0
                if len(tbits) > 0:
                    hour = cint(tbits[0])
                if len(tbits) > 1:
                    minute = cint(tbits[1])
                if len(tbits) > 2:
                    second = cint(tbits[2])
                t = datetime.time(hour, minute, second)
                d = d.combine(d, t)
            return d
        else:
            return None

    def integer(self, field, default=0):
        """ Returns an integer key from a datafield """
        if field in self.data:
            return cint(self.data[field])
        else:
            return default

    def integer_list(self, field):
        """
        Returns a list of integers from a datafield that contains
        comma separated numbers.
        """
        if field in self.data:
            s = self.string(field)
            items = s.split(",")
            ids = []
            for i in items:
                if is_numeric(i):
                    ids.append(cint(i))
            return ids
        else:
            return []

    def floating(self, field, default=0.0):
        """ Returns a float key from a datafield """
        if field in self.data:
            return cfloat(self.data[field])
        else:
            return default

    def string(self, field, strip=True, default=""):
        """ Returns a string key from a datafield """
        if field in self.data:
            s = self.data[field]
            if s is None: return ""
            if strip: s = s.strip()
            return s
        else:
            return default

    def filename(self, default=""):
        if "filechooser" in self.data:
            return self.data.filechooser.filename
        return default

    def filedata(self, default=""):
        if "filechooser" in self.data:
            return self.data.filechooser.value
        return default

    def __contains__(self, key):
        return key in self.data

    def has_key(self, key):
        return key in self.data

    def __getitem__(self, key):
        return self.string(key)

    def __setitem__(self, key, value):
        self.data[key] = value

    def __repr__(self):
        return json(self.data)

class AdvancedSearchBuilder(object):
    """
    Builds an advanced search (requires a post with multiple supplied parameters)
    as = AdvancedSearchBuilder(dbo, post)
    as.add_id("litterid", "a.AcceptanceNumber")
    as.add_str("rabiestag", "a.RabiesTag")
    as.ands, as.values
    """

    ands = []
    values = []
    dbo = None
    post = None

    def __init__(self, dbo, post):
        self.dbo = dbo
        self.post = post
        self.ands = []
        self.values = []

    def add_id(self, cfield, field): 
        """ Adds a clause for comparing an ID field """
        if self.post[cfield] != "" and self.post.integer(cfield) > -1:
            self.ands.append(f"{field} = ?")
            self.values.append(self.post.integer(cfield))

    def add_id_pair(self, cfield, field, field2): 
        """ Adds a clause for a posted value to one of two ID fields (eg: breeds) """
        if self.post[cfield] != "" and self.post.integer(cfield) > 0: 
            self.ands.append(f"({field} = ? OR {field2} = ?)")
            self.values.append(self.post.integer(cfield))
            self.values.append(self.post.integer(cfield))

    def add_str(self, cfield, field): 
        """ Adds a clause for a posted value to a string field """
        if self.post[cfield] != "":
            x = self.post[cfield].lower().replace("'", "`")
            x = f"%{x}%"
            self.ands.append(self.dbo.sql_ilike(field))
            self.values.append(x)

    def add_str_pair(self, cfield, field, field2): 
        """ Adds a clause for a posted value to one of two string fields """
        if self.post[cfield] != "":
            x = self.post[cfield].lower().replace("'", "`")
            x = f"%{x}%"
            self.ands.append("(%s OR %s)" % (self.dbo.sql_ilike(field), self.dbo.sql_ilike(field2)))
            self.values.append(x)
            self.values.append(x)

    def add_str_triplet(self, cfield, field, field2, field3): 
        """ Adds a clause for a posted value to one of three string fields """
        if self.post[cfield] != "":
            x = self.post[cfield].lower().replace("'", "`")
            x = f"%{x}%"
            self.ands.append("(%s OR %s OR %s)" % (self.dbo.sql_ilike(field), 
                self.dbo.sql_ilike(field2), self.dbo.sql_ilike(field3)))
            self.values.append(x)
            self.values.append(x)
            self.values.append(x)

    def add_date(self, cfieldfrom, cfieldto, field): 
        """ Adds a clause for a posted date range to a date field """
        if self.post[cfieldfrom] != "" and self.post[cfieldto] != "":
            self.post.data["dayend"] = "23:59:59"
            self.ands.append(f"{field} >= ? AND {field} <= ?")
            self.values.append(self.post.date(cfieldfrom))
            self.values.append(self.post.datetime(cfieldto, "dayend"))

    def add_date_pair(self, cfieldfrom, cfieldto, field, field2): 
        """ Adds a clause for a posted date range to one of two date fields """
        if self.post[cfieldfrom] != "" and self.post[cfieldto] != "":
            self.post.data["dayend"] = "23:59:59"
            self.ands.append(f"(({field} >= ? AND {field} <= ?) OR ({field2} >= ? AND {field2} <= ?))")
            self.values.append(self.post.date(cfieldfrom))
            self.values.append(self.post.datetime(cfieldto, "dayend"))
            self.values.append(self.post.date(cfieldfrom))
            self.values.append(self.post.datetime(cfieldto, "dayend"))

    def add_date_since(self, cfield, field):
        """ Adds a claused for a date range between a cfield and now """
        if self.post[cfield] != "":
            self.ands.append(f"{field} >= ? AND {field} <= ?")
            self.values.append(self.post.date(cfield))
            self.values.append(self.dbo.now())

    def add_phone_triplet(self, cfield, field, field2, field3): 
        """ Adds a clause for a posted value to one of three telephone fields """
        if self.post[cfield] != "":
            x = atoi(self.post[cfield])
            if x < 999: return # 4 digits required or likely to be far too many results
            x = f"%{x}%"
            self.ands.append("(%s LIKE ? OR %s LIKE ? OR %s LIKE ?)" % (self.dbo.sql_atoi(field), 
                self.dbo.sql_atoi(field2), self.dbo.sql_atoi(field3)))
            self.values.append(x)
            self.values.append(x)
            self.values.append(x)

    def add_filter(self, f, condition):
        """ Adds a complete clause if posted filter value is present """
        if self.post["filter"].find(f) != -1: self.ands.append(condition)

    def add_comp(self, cfield, value, condition):
        """ Adds a clause if a field holds a value """
        if self.post[cfield] == value: self.ands.append(condition)

    def add_words(self, cfield, field):
        """ Adds a separate clause for each word in cfield """
        if self.post[cfield] != "":
            words = self.post[cfield].split(" ")
            for w in words:
                x = w.lower().replace("'", "`")
                x = f"%{x}%"
                self.ands.append(self.dbo.sql_ilike(field))
                self.values.append(x)

class SimpleSearchBuilder(object):
    """
    Builds a simple search (based on a single search term)
    ss = SimpleSearchBuilder(dbo, "test")
    ss.add_field("a.AnimalName")
    ss.add_field("a.ShelterCode")
    ss.add_fields([ "a.BreedName", "a.AnimalComments" ])
    ss.ors, ss.values
    """
    
    q = ""
    qlike = ""
    ors = []
    values = []
    dbo = None

    def __init__(self, dbo, q):
        self.dbo = dbo
        self.q = q.replace("'", "`")
        self.qlike = f"%{self.q.lower()}%"
        self.ors = []
        self.values = []

    def add_field(self, field):
        """ Add a field to search """
        self.ors.append(self.dbo.sql_ilike(field))
        self.values.append(self.qlike)

    def add_field_value(self, field, value):
        """ Add a field with a specific value """
        self.ors.append(f"{field} = ?")
        self.values.append(value)

    def add_field_phone(self, field):
        """ Adds a phone number field to search 
            Simple search needs at least 6 digits for searching phone numbers to
            avoid phone numbers being returned when the intention was an owner code or 
            address (US postal addresses frequently have 4-5 digit house numbers).
            We do nothing if the search term does not start with a number.
        """
        if len(self.q) == 0 or not is_numeric(self.q[0]): return
        x = atoi(self.q)
        if x < 99999: return # minimum 6 digits for searching phone numbers
        self.ors.append(f"{self.dbo.sql_atoi(field)} LIKE ?")
        self.values.append(f"%{x}%")

    def add_fields(self, fieldlist):
        """ Add clauses for many fields in one list """
        for f in fieldlist:
            if f.find("Telephone") != -1:
                self.add_field_phone(f)
            else:
                self.add_field(f)

    def add_large_text_fields(self, fieldlist):
        """ Add clauses for many large text fields (only search in smaller databases) in one list """
        if not self.dbo.is_large_db:
            for f in fieldlist:
                self.add_field(f)

    def add_words(self, field):
        """ Adds each word in the term as and clauses so that each word is separately matched and has to be present """
        ands = []
        for w in self.q.split(" "):
            x = w.lower().replace("'", "`")
            x = f"%{x}%"
            ands.append(self.dbo.sql_ilike(field))
            self.values.append(x)
        self.ors.append("(" + " AND ".join(ands) + ")")

    def add_clause(self, clause):
        self.ors.append(clause)
        self.values.append(self.qlike)

class FormHTMLParser(HTMLParser):
    """ Class for parsing HTML forms and extracting the input/select/textarea tags """
    tag = ""
    title = ""
    controls = None

    def handle_starttag(self, tag, attrs):
        self.tag = tag
        if self.controls is None: self.controls = []
        if tag == "select" or tag == "input" or tag == "textarea":
            ad = { "tag": tag }
            for k, v in attrs:
                ad[k] = v
            self.controls.append(ad)

    def handle_data(self, data):
        if self.tag == "title":
            self.title = data

class ImgSrcHTMLParser(HTMLParser):
    """
    Class for parsing HTML files and extracting the img src attributes.
    Used by the remove_dead_img_src function to verify image links in a
    document and blank dead ones before feeding to wkhtmltopdf.
    """
    links = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            for k, v in attrs:
                if k == "src":
                    self.links.append(v)

class PlainTextWriterHTMLParser(HTMLParser):
    """ Class for parsing HTML and generating a plain text document """
    tag = ""
    olmode = False
    olcount = 1
    ulmode = False
    tdmode = False
    s = []

    def __init__(self):
        HTMLParser.__init__(self)
        self.s = []

    def handle_starttag(self, tag, attrs):
        self.tag = tag
        if tag == "ol": self.olmode = True
        if tag == "ul": self.ulmode = True
        if tag == "td": self.tdmode = True

    def handle_endtag(self, tag):
        if tag == "ol": 
            self.olmode = False
            self.olcount = 1
        elif tag == "ul": 
            self.ulmode = False
        elif tag == "td": 
            self.tdmode = False
            self.s.append(" | ")
        if tag in ( "li", "tr", "p", "div", "br" ) and not self.tdmode: 
            self.s.append("\n")
        else:
            if len(self.s) == 0 or self.s[-1] != " ": self.s.append(" ")

    def handle_data(self, data):
        if self.tag == "li" and self.ulmode:
            self.s.append(" * %s" % data)
        elif self.tag == "li" and self.olmode:
            self.s.append(" %s. %s" % (self.olcount, data))
            self.olcount += 1
        else:
            self.s.append(data.strip())

def is_bytes(f):
    """ Returns true if the f is a bytes string """
    return isinstance(f, bytes)

def is_currency(f):
    """ Returns true if the field with name f is a currency field """
    CURRENCY_FIELDS = "AMT AMOUNT DONATION DAILYBOARDINGCOST COSTAMOUNT COST FEE LICENCEFEE DEPOSITAMOUNT FINEAMOUNT UNITPRICE VATAMOUNT"
    return f.upper().startswith("MONEY") or CURRENCY_FIELDS.find(f.upper()) != -1

def is_date(d):
    """ Returns true if d is a date field """
    return isinstance(d, datetime.datetime) or isinstance(d, datetime.date)

def is_numeric(s):
    """
    Returns true if the string s is a number
    """
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True

def is_str(s):
    """
    Returns true if the string s is a str
    """
    return isinstance(s, str)

def is_unicode(s):
    """
    Returns true if the string s is unicode
    """
    return isinstance(s, str)

def str2bytes(s, encoding = "utf-8"):
    """
    Converts a unicode str to a utf-8 bytes string
    Does nothing if the value is not str
    """
    if isinstance(s, str): return s.encode(encoding)
    return s 

def bytes2str(s, encoding = "utf-8"):
    """
    Converts a utf-8 bytes string to a unicode str.
    Does nothing if the value is not bytes
    """
    if isinstance(s, bytes): return s.decode(encoding)
    return s 

def atoi(s):
    """
    Converts only the numeric portion of a string to an integer
    """
    return cint(re.sub(r'[^0-9]', "", s))

def cint(s):
    """
    Converts a value to an int, coping with None and non-int values
    """
    try:
        return int(s)
    except:
        return 0

def cfloat(s):
    """
    Converts a value to a float, coping with None and non-numeric values
    """
    try:
        return float(s)
    except:
        return float(0)

def cmd(c, shell=False):
    """
    Runs the command c and returns a tuple of return code and output
    """
    output = None
    try:
        output = subprocess.check_output(c.split(" "), stderr=subprocess.STDOUT, shell=shell)
        return (0, output)
    except subprocess.CalledProcessError as e:
        return (e.returncode, e.output)

def deduplicate_list(l):
    """
    Removes duplicates from the list l and returns a new list
    """
    uq = []
    for i in l:
        if i not in uq:
            uq.append(i)
    return uq

def digits_only(s):
    """
    Returns only the digits from a string
    """
    return re.sub(r'[^0-9]', "", s)

def file_contains(f, v):
    """
    Returns true if file f contains value v
    """
    return 0 == os.system("grep %s %s" % (v, f))

def iif(c, t, f):
    """
    Evaluates c and returns t for True or f for False
    """
    return c and t or f

def nulltostr(s):
    try:
        if s is None: return ""
        return str(s)
    except:
        return ""

def filename_only(filename):
    """ If a filename has a path, return just the name """
    if filename.find("/") != -1: filename = filename[filename.rfind("/")+1:]
    if filename.find("\\") != -1: filename = filename[filename.rfind("\\")+1:]
    return filename

def json_parse(s):
    """
    Parses json and returns an object tree.
    s can be either a bytes string or str
    """
    return extjson.loads(s)

def json_handler(obj):
    """
    Used to help when serializing python objects to json
    """
    if obj is None:
        return "null"
    elif hasattr(obj, "isoformat"):
        return obj.isoformat()
    elif type(obj) == datetime.timedelta:
        hours, remain = divmod(obj.seconds, 3600)
        minutes, seconds = divmod(remain, 60)
        return "%02d:%02d:%02d" % (hours, minutes, seconds)
    elif isinstance(obj, decimal.Decimal):
        return str(obj)
    elif isinstance(obj, bytes): 
        return str(obj)
    elif isinstance(obj, type):
        return str(obj)
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj)))

def json(obj, readable = False):
    """
    Takes a python object and serializes it to JSON.
    None objects are turned into "null"
    datetime objects are turned into string isoformat for use with js Date.
    This function switches </ for <\/ in output to prevent HTML tags in any content
        from breaking out of a script tag.
    readable: If True, line breaks and padding are added to make it human-readable
    """
    if not readable:
        return extjson.dumps(obj, default=json_handler).replace("</", "<\\/")
    else:
        return extjson.dumps(obj, default=json_handler, indent=4, separators=(',', ': ')).replace("</", "<\\/")

def parse_qs(s):
    """ Given a querystring, parses it and returns a dict of elements """
    return dict(urllib.parse.parse_qsl(s))

def address_first_line(address):
    """
    Returns the first line of an address
    """
    if address is None: return ""
    bits = address.split("\n")
    if len(bits) > 0:
        return bits[0]
    return ""

def address_house_number(address):
    """
    Returns the house number from an address
    """
    fl = address_first_line(address)
    if fl == "": return ""
    bits = fl.split(" ")
    if is_numeric(bits[0]):
        return bits[0]
    return ""

def address_street_name(address):
    """
    Returns the street name from an address line
    """
    fl = address_first_line(address)
    if fl == "": return ""
    bits = fl.split(" ", 1)
    if len(bits) == 2:
        return bits[1]
    return ""

def spaceleft(s, spaces):
    """
    leftpads a string to a number of spaces
    """
    sp = "                                                 "
    if len(s) > spaces: return s
    nr = spaces - len(s)
    return sp[0:nr] + s

def spaceright(s, spaces):
    """
    rightpads a string to a number of spaces
    """
    sp = "                                                 "
    if len(s) > spaces: return s
    nr = spaces - len(s)
    return s + sp[0:nr]

def unixtime():
    """ Returns Unix time (seconds since epoch 01/01/1970) """
    return time.time()

def padleft(num, digits):
    """
    leftpads a number to digits
    """
    zeroes = "000000000000000"
    s = str(num)
    if len(s) > digits: return s
    nr = digits - len(s)
    return zeroes[0:nr] + s

def padright(num, digits):
    """
    rightpads a number to digits
    """
    zeroes = "000000000000000"
    s = str(num)
    if len(s) > digits: return s
    nr = digits - len(s)
    return s + zeroes[0:nr]

def truncate(s, length = 100):
    """
    Truncates a string to length.
    """
    if s is None: return ""
    if len(s) > length: return s[0:length]
    return s

def stringio(contents = ""):
    if contents != "": return StringIO(contents)
    return StringIO()

def bytesio(contents = ""):
    if contents != "": return BytesIO(contents)
    return BytesIO()

def strip_background_images(s):
    """
    Removes background-image CSS directives from a string.
    """
    return re.sub(r'background-image:.*?;', '', s)

def strip_duplicate_spaces(s):
    """
    Removes duplicate spaces from a string and strips, eg: ' Bad   Flag' becomes 'Bad Flag'
    """
    if s is None: return ""
    return " ".join(re.split("\s+", s)).strip()

def strip_html_tags(s):
    """
    Removes all html tags from a string, leaving just the
    content behind.
    """
    return re.sub('<.*?>', '', s)

def strip_script_tags(s):
    """
    Removes all script tags from a string
    """
    return re.sub(r'<(script).*?</\1>(?s)', '', s)

def strip_non_ascii(s):
    """
    Remove any non-ascii characters from a string str
    """
    return "".join(i for i in s if ord(i)<128)

def decode_html(s):
    """
    Decodes HTML entities in s and turns them into unicode
    """
    if s is None: return ""
    return unescape(s)

def encode_html(s):
    """
    Accepts str or utf-8 bytes
    returns str with HTML entities instead of unicode code points
    """
    if s is None: return ""
    if is_bytes(s): s = bytes2str(s)
    return s.encode("ascii", "xmlcharrefreplace").decode("ascii") 

def encode_uri(s):
    """
    Encodes unicode codepoints in a str as URI encoding
    """
    if s is None: return ""
    if is_bytes(s): s = bytes2str(s) 
    return urllib.parse.quote_plus(s)

def list_overlap(l1, l2):
    """
    Returns True if any of the items in l1 are present in l2.
    """
    for l in l1:
        if l in l2:
            return True
    return False

def base64encode(s):
    """ Base64 encodes s, returning the result as a string """
    if not is_bytes(s): s = s.encode("utf-8") # Only byte strings can be encoded so convert first
    return base64.b64encode(s).decode("utf-8") # Return the encoded value as a string rather than bytes

def base64decode(s):
    """ Base64 decodes s, returning the result as bytes """
    if not is_bytes(s): s = s.encode("utf-8") # Only byte strings can be decoded so convert first
    return base64.b64decode(s)

def base64decode_str(s):
    """ Base64 decodes, returning the result as a str. """
    rv = base64decode(s)
    return rv.decode("utf-8")

def uuid_str():
    """ Returns a type 4 UUID as a string """
    return str(uuid.uuid4())

def pbkdf2_hash_hex(plaintext, salt="", algorithm="sha1", iterations=1000):
    """ Returns a hex pbkdf2 hash of the plaintext given. 
        If salt is not given, a random salt is generated.
        We have implementations for both python2 and python3
        The return type is str whatever version of python.
    """
    if salt == "": salt = base64.b64encode(os.urandom(16))
    hashfunc = getattr(hashlib, algorithm)
    import asm3.pbkdf2.pbkdf23
    return str(asm3.pbkdf2.pbkdf23.pbkdf2(hashfunc, str2bytes(plaintext), str2bytes(salt), iterations, 24).hex())

def regex_multi(pattern, findin):
    """
    Returns all matches for pattern in findin
    """
    return re.findall(pattern, findin)

def regex_one(pattern, findin):
    """
    Returns the first match for pattern in findin or an empty
    string for no match.
    """
    r = regex_multi(pattern, findin)
    if len(r) == 0: return ""
    return r[0]

class ASMValidationError(web.HTTPError):
    """
    Custom error thrown by data modules when validation fails
    """
    msg = ""
    def __init__(self, msg):
        self.msg = msg
        status = '500 Internal Server Error'
        headers = { 'Content-Type': "text/html" }
        data = "<h1>Validation Error</h1><p>%s</p>" % msg
        if "headers" not in web.ctx: web.ctx.headers = []
        web.HTTPError.__init__(self, status, headers, data)

    def getMsg(self):
        return self.msg

class ASMPermissionError(web.HTTPError):
    """
    Custom error thrown by data modules when permission checks fail
    """
    def __init__(self, msg):
        status = '500 Internal Server Error'
        headers = { 'Content-Type': "text/html" }
        data = "<h1>Permission Error</h1><p>%s</p>" % msg
        if "headers" not in web.ctx: web.ctx.headers = []
        web.HTTPError.__init__(self, status, headers, data)

class ASMError(web.HTTPError):
    """
    Custom error thrown by data modules 
    """
    def __init__(self, msg):
        status = '500 Internal Server Error'
        headers = { 'Content-Type': "text/html" }
        data = "<h1>Error</h1><p>%s</p>" % msg
        if "headers" not in web.ctx: web.ctx.headers = []
        web.HTTPError.__init__(self, status, headers, data)

def escape_tinymce(content):
    """
    Escapes HTML content for placing inside a tinymce
    textarea. Basically, just the < and > markers - other
    escaped tokens should be left for the browser to
    expand - except &gt; and &lt; for our << >> markers
    (god this is confusing), which need to be double
    escaped or tinymce breaks. 
    """
    c = bytes2str(content)
    c = c.replace("&gt;", "&amp;gt;")
    c = c.replace("&lt;", "&amp;lt;")
    c = c.replace("<", "&lt;")
    c = c.replace(">", "&gt;")
    return c

def csv_parse(s):
    """
    Reads CSV data from a unicode string "s" 
    Assumes data has been decoded appropriately to unicode/str by the caller.
    Assumes the first row is the column/header names
    return value is a list of dictionaries.
    We've basically implemented DictCSVReader ourselves because subclassing 
    csvreader in a way that works for Python 2 and 3 is a nightmare and more code than
    just doing it yourself.
    """
    if s[0:3] == "\xef\xbb\xbf": s = s[3:] # strip any utf-8 BOM if included (should not be necessary with utf-8-sig)
    s = s.replace("\r\n", "\n")
    s = s.replace("\r", "\n")
    rows = [] # parsed rows
    pos = [0, 0, False] # line start position, item start position and EOF 
    def readline():
        # Finds the next line ending and returns the line as a list of items
        items = []
        inquoted = False
        rpos = pos[0] # read position marker, start at the line
        while True:
            if s[rpos:rpos+1] == "\"": inquoted = not inquoted
            if not inquoted and (s[rpos:rpos+1] == "," or s[rpos:rpos+1] == "\n" or rpos == len(s)): 
                # Hit delimiter, line break or end of file - parse the item
                item = s[pos[1]:rpos]
                pos[1] = rpos+1 # advance next item start position
                if item.startswith("\""): item = item[1:]
                if item.endswith("\""): item = item[0:len(item)-1]
                items.append(item.strip()) # strip whitespace before storing the item
            if not inquoted and (s[rpos:rpos+1] == "\n" or rpos == len(s)):
                # Hit line break or end of file, move to the next line and return our set
                pos[0] = rpos+1
                if rpos == len(s): pos[2] = True # EOF
                return items
            rpos += 1
    # Read the columns from the first row
    cols = readline()
    if len(cols) == 0: return rows # Empty file
    # Iterate the rest of the data and construct dictionaries of the column/rows
    while True:
        items = readline()
        d = {}
        for i, c in enumerate(cols):
            if i < len(items): d[c] = items[i]
        if len(d) > 1: # Don't append empty rows (can also be empty string in first col)
            rows.append(d)
        if pos[2]: break # EOF
    return rows

def csv(l, rows, cols = None, includeheader = True, titlecaseheader = False, renameheader = ""):
    """
    Creates a CSV file from a set of resultset rows. If cols has been 
    supplied as a list of strings, fields will be output in that
    order.
    The file is constructed as a list of unicode strings and returned as a utf-8 encoded byte string.
    l:  locale (used for formatting currencies and dates)
    rows: list of dict result rows
    cols: list of column headings, if None uses the result column names
    includeheader: if True writes the header row
    titlecaseheader: if True title cases the header row
    renameheader: A comma separated list of find=replace values to rewrite column headers
    """
    if rows is None or len(rows) == 0: return ""
    lines = []
    def writerow(row):
        line = []
        for r in row:
            line.append("\"%s\"" % r)
        lines.append(",".join(line))
    if cols is None:
        cols = []
        for k in rows[0].keys():
            cols.append(k)
        cols = sorted(cols)
    if includeheader:
        outputcols = cols
        if titlecaseheader: 
            outputcols = [ c.title() for c in cols ]
        if renameheader != "":
            rout = []
            for c in outputcols: # can rewrite cols we just titlecased
                match = False
                for rh in renameheader.split(","):
                    find, replace = rh.split("=")
                    if c == find:
                        rout.append(replace)
                        match = True
                        break
                if not match:
                    rout.append(c)
            outputcols = rout
        writerow(outputcols)
    for r in rows:
        rd = []
        for c in cols:
            if is_currency(c):
                rd.append(asm3.i18n.format_currency_no_symbol(l, r[c]))
            elif is_date(r[c]):
                timeportion = "00:00:00"
                dateportion = ""
                try:
                    dateportion = asm3.i18n.python2display(l, r[c])
                    timeportion = asm3.i18n.format_time(r[c])
                except:
                    pass # Don't stop the show for bad dates/times
                if timeportion != "00:00:00": # include time if non-midnight
                    dateportion = "%s %s" % (dateportion, timeportion)
                rd.append(dateportion)
            elif is_str(r[c]):
                rd.append(r[c].replace("\"", "''")) # Escape any double quotes in strings
            else:
                rd.append(r[c])
        writerow(rd)
    # Manually include a UTF-8 BOM to prevent Excel mangling files
    return ("\ufeff" + "\n".join(lines)).encode("utf-8")

def fix_relative_document_uris(dbo, s):
    """
    Switches the relative uris used in s (str) for absolute
    ones to the service so that documents will work outside of 
    the ASM UI.
    """
    def qsp(q, k):
        """ returns the value of key k from querystring q """
        kp = q.find(k + "=")
        ke = q.find("&", kp)
        if ke == -1: ke = len(q)
        if kp != -1 and ke != -1: return q[q.find("=",kp)+1:ke]
        return ""

    def url(method, params):
        account = ""
        if MULTIPLE_DATABASES: account = "account=%s&" % dbo.database
        return "%s/service?method=%s&%s%s" % (BASE_URL, method, account, params)

    p = ImgSrcHTMLParser()
    p.feed(s)
    for l in p.links:
        if l.startswith("image?"):
            mode = qsp(l, "mode")
            u = ""
            if mode == "nopic":
                u = url("extra_image", "title=nopic.jpg")
            elif mode == "animal":
                u = url("animal_image", "animalid=%s" % qsp(l, "id"))
            elif mode == "animalthumb":
                u = url("animal_thumbnail", "animalid=%s" % qsp(l, "id"))
            elif mode == "dbfs":
                u = url("dbfs_image", "title=%s" % qsp(l, "id"))
            elif mode == "media":
                u = url("media_image", "mediaid=%s" % qsp(l, "id"))
            s = s.replace(l, u)
            s = s.replace(l.replace("&", "&amp;"), u) # HTMLParser can fix &amp; back to &, breaking previous replace
            asm3.al.debug("translate '%s' to '%s'" % (l, u), "utils.fix_relative_document_uris", dbo)
        elif not l.startswith("http") and not l.startswith("data:") and not l.startswith("//"):
            s = s.replace(l, "") # cannot use this type of url
            asm3.al.debug("strip invalid url '%s'" % l, "utils.fix_relative_document_uris", dbo)
    return s

def generator2str(fn, *args):
    """ Iterates a generator function, passing args and returning the output as a buffer """
    out = stringio()
    for x in fn(*args):
        out.write(x)
    return out.getvalue()

def generator2file(outfile, fn, *args):
    """ Iterates a generator function, passing args and writing to outfile """
    with open(outfile, "w") as f:
        for x in fn(*args):
            f.write(x)

def substitute_tags(searchin, tags, use_xml_escaping = True, opener = "&lt;&lt;", closer = "&gt;&gt;"):
    """
    Substitutes the dictionary of tags in "tags" for any found
    in "searchin". opener and closer denote the start of a tag,
    if use_xml_escaping is set to true, then tags are XML escaped when
    output and opener/closer are escaped.
    """
    if not use_xml_escaping:
        opener = opener.replace("&lt;", "<").replace("&gt;", ">")
        closer = closer.replace("&lt;", "<").replace("&gt;", ">")

    s = searchin
    sp = s.find(opener)
    while sp != -1:
        ep = s.find(closer, sp + len(opener))
        if ep != -1:
            matchtag = s[sp + len(opener):ep].upper()
            newval = ""
            if matchtag in tags:
                newval = tags[matchtag]
                if newval is not None:
                    newval = str(newval)
                    if use_xml_escaping and not newval.lower().startswith("<img"):
                        newval = newval.replace("&", "&amp;")
                        newval = newval.replace("<", "&lt;")
                        newval = newval.replace(">", "&gt;")
            s = s[0:sp] + str(newval) + s[ep + len(closer):]
            sp = s.find(opener, sp)
        else:
            # No end marker for this tag, stop processing
            break
    return s

def md5_hash_hex(s):
    """
    Returns an md5 hash of a string
    """
    m = hashlib.md5()
    m.update(str2bytes(s))
    s = m.hexdigest()
    return s

def get_asm_news(dbo):
    """ Retrieves the latest asm news from the server """
    try:
        s = get_url(URL_NEWS)["response"]
        asm3.al.debug("Retrieved ASM news, got %d bytes" % len(s), "utils.get_asm_news", dbo)
        return s
    except Exception as err:
        asm3.al.error("Failed reading ASM news: %s" % err, "utils.get_asm_news", dbo)

def get_url(url, headers = {}, cookies = {}, timeout = None, params = None):
    """
    Retrieves a URL as text
    headers: dict of HTTP headers
    cookies: dict of cookies
    timeout: timeout value in seconds as a float
    params: dict of querystring elements
    """
    # requests timeout is seconds/float, but some may call this with integer ms instead so convert
    if timeout is not None and timeout > 1000: timeout = timeout / 1000.0
    r = requests.get(url, headers = headers, cookies=cookies, timeout=timeout, params=params)
    return { "cookies": r.cookies, "headers": r.headers, "response": r.text, "status": r.status_code, "requestheaders": r.request.headers, "requestbody": r.request.body }

def get_image_url(url, headers = {}, cookies = {}, timeout = None):
    """
    Retrives an image from a URL as bytes string in response
    """
    # requests timeout is seconds/float, but some may call this with integer ms instead so convert
    if timeout is not None and timeout > 1000: timeout = timeout / 1000.0
    r = requests.get(url, headers = headers, cookies=cookies, timeout=timeout, stream=True)
    b = bytesio()
    for chunk in r:
        b.write(chunk) # default from requests is 128 byte chunks
    return { "cookies": r.cookies, "headers": r.headers, "response": b.getvalue(), "status": r.status_code, "requestheaders": r.request.headers, "requestbody": r.request.body }

def post_data(url, data, contenttype = "", httpmethod = "", headers = {}):
    """
    Posts data (str or bytes) to a URL as the body
    httpmethod: POST by default.
    Returns dict of requestheaders (dict), requestbody (bytes), headers (str), response (str) and status (int)
    """
    try:
        if contenttype != "": headers["Content-Type"] = contenttype
        if isinstance(data, str): data = str2bytes(data)
        req = urllib2.Request(url, data, headers)
        if httpmethod != "": req.get_method = lambda: httpmethod
        resp = urllib2.urlopen(req)
        return { "requestheaders": headers, "requestbody": data, "headers": resp.info().as_string(), "response": bytes2str(resp.read()), "status": resp.getcode() }
    except urllib2.HTTPError as e:
        return { "requestheaders": headers, "requestbody": data, "headers": e.info().as_string(), "response": bytes2str(e.read()), "status": e.getcode() }

def post_form(url, fields, headers = {}, cookies = {}):
    """
    Does a form post
    url: The http url to post to
    fields: A map of { name: value } elements
    headers: A map of { name: value } headers
    return value is the http headers (a map) and server's response as a string
    """
    r = requests.post(url, data=fields, headers=headers, cookies=cookies)
    return { "cookies": r.cookies, "headers": r.headers, "response": r.text, "status": r.status_code, "requestheaders": r.request.headers, "requestbody": r.request.body }

def post_multipart(url, fields = None, files = None, headers = {}, cookies = {}):
    """
    Does a multipart form post
    url: The http url to post to
    files: A map of { name: (name, data, mime) }
    fields: A map of { name: value } elements
    headers: A map of { name: value } headers
    return value is the http headers (a map) and server's response as a string
    """
    r = requests.post(url, files=files, data=fields, headers=headers, cookies=cookies)
    return { 
        "cookies": r.cookies, 
        "headers": r.headers, 
        "response": r.text, 
        "status": r.status_code, 
        "redirects": len(r.history), 
        "requestheaders": r.request.headers, 
        "requestbody": r.request.body 
    }

def post_json(url, json, headers = {}):
    """
    Posts a JSON document to a URL. json can be str or bytes
    """
    return post_data(url, json, contenttype="application/json", headers=headers)

def patch_json(url, json, headers = {}):
    """
    Posts a JSON document to a URL with the PATCH HTTP method. json can be str or bytes
    """
    return post_data(url, json, contenttype="application/json", httpmethod="PATCH", headers=headers)

def post_xml(url, xml, headers = {}):
    """
    Posts an XML document to a URL. xml can be str or bytes.
    """
    return post_data(url, xml, contenttype="text/xml", headers=headers)

def urlencode(d):
    """
    URL encodes a dictionary of key/pair values.
    """
    return urllib.parse.urlencode(d)

def zip_extract(zipfilename, filename):
    """
    Reads zipfile zipfilename and extracts filename, returning its contents as a bytes string.
    """
    with open(zipfilename, "rb") as zff:
        zf = zipfile.ZipFile(zff, "r")
        content = zf.open(filename).read()
        return content

def zip_replace(zipfilename, filename, content):
    """
    Reads zipfilename, then replaces filename with content (bytes string) and returns the new zip file as a bytes string.
    """
    with open(zipfilename, "rb") as zff:
        zf = zipfile.ZipFile(zff, "r")
        zo = bytesio()
        zfo = zipfile.ZipFile(zo, "w", zipfile.ZIP_DEFLATED)
        for f in zf.namelist():
            if f == filename:
                zfo.writestr(f, content)
            else:
                zfo.writestr(f, zf.open(f).read())
        zf.close()
        zfo.close()
        return zo.getvalue()

def read_text_file(name):
    """
    Reads a utf-8 text file and returns the result as a unicode str.
    """
    with open(name, 'r', encoding='utf-8') as f:
        text = f.read()
    return text

def write_text_file(name, data):
    """
    Writes a text file (expects data to be a unicode str).
    """
    with open(name, 'w', encoding='utf-8') as f:
        f.write(data)
        f.flush()

def read_binary_file(name):
    """
    Reads a binary file and returns the result as bytes
    """
    with open(name, "rb") as f:
        return f.read()

def write_binary_file(name, data):
    """
    Writes a binary file (expects data = bytes)
    """
    with open(name, "wb") as f:
        f.write(data)

def pdf_count_pages(filedata):
    """
    Given a PDF in filedata (bytes string), returns the number of pages.
    """
    if type(filedata) != bytes: return 0 # If we aren't given a bytes string we can't do anything
    patterns = [ b"/Type/Page", b"/Type /Page" ]
    pages = 0
    for p in patterns:
        pages += filedata.count(p)
    return pages

def html_to_text(htmldata):
    """
    Converts HTML content to plain text, returning the text as a str
    """
    p = PlainTextWriterHTMLParser()
    p.feed(htmldata)
    return "".join(p.s)

def html_to_pdf(dbo, htmldata):
    """
    Converts HTML content to PDF and returns the PDF file data as bytes.
    """
    if HTML_TO_PDF == "pisa" or htmldata.find("pdf renderer pisa") != -1:
        return html_to_pdf_pisa(dbo, htmldata)
    else:
        return html_to_pdf_cmd(dbo, htmldata)

def html_to_pdf_cmd(dbo, htmldata):
    """
    Converts HTML content to PDF and returns the PDF file data as bytes.
    Uses the command line tool specified in HTML_TO_PDF (which is typically wkhtmltopdf)
    """
    # Allow orientation and papersize to be set
    # with directives in the document source - eg: <!-- pdf orientation landscape, pdf papersize letter -->
    orientation = "portrait"
    # Sort out page size arguments
    papersize = "--page-size a4"
    if htmldata.find("pdf orientation landscape") != -1: orientation = "landscape"
    if htmldata.find("pdf orientation portrait") != -1: orientation = "portrait"
    if htmldata.find("pdf papersize a5") != -1: papersize = "--page-size a5"
    if htmldata.find("pdf papersize a4") != -1: papersize = "--page-size a4"
    if htmldata.find("pdf papersize a3") != -1: papersize = "--page-size a3"
    if htmldata.find("pdf papersize letter") != -1: papersize = "--page-size letter"
    # Eg: <!-- pdf papersize exact 52mmx86mm end -->
    ps = regex_one("pdf papersize exact (.+?) end", htmldata) 
    if ps != "":
        w, h = ps.split("x")
        papersize = "--page-width %s --page-height %s" % (w, h)
    # Zoom - eg: <!-- pdf zoom 130% end -->
    zm = regex_one("pdf zoom (.+?) end", htmldata)
    if zm != "":
        zoom = "<style>\nbody { zoom: %s; }\n</style>\n" % zm
    else:
        zoom = "<style>\nbody { zoom: %s%%; }\n</style>\n" % asm3.configuration.pdf_zoom(dbo) # use the default from config
    # Margins, top/bottom/left/right eg: <!-- pdf margins 2cm 2cm 2cm 2cm end -->
    margins = "--margin-top 1cm"
    mg = regex_one("pdf margins (.+?) end", htmldata)
    if mg != "":
        tm, bm, lm, rm = mg.split(" ")
        margins = "--margin-top %s --margin-bottom %s --margin-left %s --margin-right %s" % (tm, bm, lm, rm)
    header = "<!DOCTYPE HTML>\n<html>\n<head>"
    header += '<meta http-equiv="content-type" content="text/html; charset=utf-8">\n'
    header += zoom
    header += "</head><body>"
    footer = "</body></html>"
    htmldata = htmldata.replace("font-size: xx-small", "font-size: 6pt")
    htmldata = htmldata.replace("font-size: x-small", "font-size: 8pt")
    htmldata = htmldata.replace("font-size: small", "font-size: 10pt")
    htmldata = htmldata.replace("font-size: medium", "font-size: 14pt")
    htmldata = htmldata.replace("font-size: large", "font-size: 18pt")
    htmldata = htmldata.replace("font-size: x-large", "font-size: 24pt")
    htmldata = htmldata.replace("font-size: xx-large", "font-size: 36pt")
    # Remove any img tags with signature:placeholder/user as the src
    htmldata = re.sub(r'<img.*?signature\:.*?\/>', '', htmldata)
    # Remove anything that could be a security risk
    htmldata = re.sub(r'<iframe.*>', '', htmldata, flags=re.I)
    htmldata = re.sub(r'<link.*>', '', htmldata, flags=re.I)
    htmldata = strip_script_tags(htmldata)
    # Fix up any google QR codes where a protocol-less URI has been used
    htmldata = htmldata.replace("\"//chart.googleapis.com", "\"http://chart.googleapis.com")
    # Switch relative document uris to absolute service based calls
    htmldata = fix_relative_document_uris(dbo, htmldata)
    # Use temp files
    inputfile = tempfile.NamedTemporaryFile(suffix=".html", delete=False)
    outputfile = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    inputfile.write(str2bytes(header + htmldata + footer))
    inputfile.flush()
    inputfile.close()
    outputfile.close()
    cmdline = HTML_TO_PDF % { "output": outputfile.name, "input": inputfile.name, "orientation": orientation, "papersize": papersize, "zoom": "", "margins": margins }
    code, output = cmd(cmdline)
    if code > 0:
        asm3.al.error("code %s returned from '%s': %s" % (code, cmdline, output), "utils.html_to_pdf")
        return output
    with open(outputfile.name, "rb") as f:
        pdfdata = f.read()
    os.unlink(inputfile.name)
    os.unlink(outputfile.name)
    return pdfdata

def html_to_pdf_pisa(dbo, htmldata):
    """
    Converts HTML content to PDF and returns the PDF file data as bytes.
    NOTE: wkhtmltopdf is far superior, but this is a pure Python solution and it does work.
    """
    # Allow orientation and papersize to be set
    # with directives in the document source - eg: <!-- pdf orientation landscape, pdf papersize letter -->
    orientation = "portrait"
    # Sort out page size arguments
    papersize = "A4"
    if htmldata.find("pdf orientation landscape") != -1: orientation = "landscape"
    if htmldata.find("pdf orientation portrait") != -1: orientation = "portrait"
    if htmldata.find("pdf papersize a5") != -1: papersize = "A5"
    if htmldata.find("pdf papersize a4") != -1: papersize = "A4"
    if htmldata.find("pdf papersize a3") != -1: papersize = "A3"
    if htmldata.find("pdf papersize letter") != -1: papersize = "letter"
    # Zoom - eg: <!-- pdf zoom 0.5 end -->
    # Not supported in any meaningful way by pisa (not smart scaling)
    # zm = regex_one("pdf zoom (.+?) end", htmldata)
    # Margins, top/bottom/left/right eg: <!-- pdf margins 2cm 2cm 2cm 2cm end -->
    margins = "2cm"
    mg = regex_one("pdf margins (.+?) end", htmldata)
    if mg != "":
        margins = mg
    header = "<!DOCTYPE html>\n<html>\n<head>"
    header += '<style>'
    header += '@page {size: %s %s; margin: %s}' % ( papersize, orientation, margins )
    header += '</style>' 
    header += "</head><body>"
    footer = "</body></html>"
    htmldata = htmldata.replace("font-size: xx-small", "font-size: 6pt")
    htmldata = htmldata.replace("font-size: x-small", "font-size: 8pt")
    htmldata = htmldata.replace("font-size: small", "font-size: 10pt")
    htmldata = htmldata.replace("font-size: medium", "font-size: 14pt")
    htmldata = htmldata.replace("font-size: large", "font-size: 18pt")
    htmldata = htmldata.replace("font-size: x-large", "font-size: 24pt")
    htmldata = htmldata.replace("font-size: xx-large", "font-size: 36pt")
    # Remove any img tags with signature:placeholder/user as the src
    htmldata = re.sub(r'<img.*?signature\:.*?\/>', '', htmldata)
    # Remove anything that could be a security risk
    htmldata = re.sub(r'<iframe.*>', '', htmldata, flags=re.I)
    htmldata = re.sub(r'<link.*>', '', htmldata, flags=re.I)
    htmldata = strip_script_tags(htmldata)
    # Fix up any google QR codes where a protocol-less URI has been used
    htmldata = htmldata.replace("\"//chart.googleapis.com", "\"http://chart.googleapis.com")
    # Switch relative document uris to absolute service based calls
    htmldata = fix_relative_document_uris(dbo, htmldata)
    # Do the conversion
    from xhtml2pdf import pisa
    out = bytesio()
    pdf = pisa.pisaDocument(stringio(header + htmldata + footer), dest=out)
    if pdf.err:
        raise IOError(pdf.err)
    return out.getvalue()

def generate_image_pdf(locale, imagedata):
    """
    Generates a PDF from some imagedata.
    Returns the PDF as a bytes string
    """
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Image
    psize = A4
    if locale == "en": psize = letter
    fin = bytesio(imagedata)
    fout = bytesio()
    doc = SimpleDocTemplate(fout, pagesize=psize, leftMargin = 1 * cm, topMargin = 1 * cm, rightMargin = 0, bottomMargin = 0)
    elements = []
    im = Image(fin)
    if psize == A4:
        im.drawWidth = 19 * cm
        im.drawHeight = 27 * cm
    else:
        im.drawWidth = 19 * cm
        im.drawHeight = 25 * cm
    elements.append(im)
    # Build the PDF
    doc.build(elements)
    return fout.getvalue()

def generate_label_pdf(dbo, locale, records, papersize, units, hpitch, vpitch, width, height, lmargin, tmargin, cols, rows):
    """
    Generates a PDF of labels from the rows given to the measurements provided.
    papersize can be "a4" or "letter"
    units can be "inch" or "cm"
    all units themselves should be floats, cols and rows should be ints
    """
    #from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch, cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

    unit = inch
    if units == "cm":
        unit = cm
    psize = A4
    if papersize == "letter":
        psize = letter

    fontname = "Courier"

    # Most fonts don't include Chinese characters. If this is a locale that needs
    # them, use the GNU unifont (contains one glyph for every character)
    if locale in ( "en_CN", "en_TW", "en_TW2" ):
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        pdfmetrics.registerFont(TTFont('Unifont','unifont.ttf'))
        fontname = "Unifont"

    fout = bytesio()
    doc = SimpleDocTemplate(fout, pagesize=psize, leftMargin = lmargin * unit, topMargin = tmargin * unit, rightMargin = 0, bottomMargin = 0)
    col = 0
    row = 0
    elements = []

    def newData():
        l = []
        for dummy in range(0, rows):
            l.append( [ "" ] * cols )
        return l

    def addToData(rd, datad, cold, rowd):
        # Ref: http://bitboost.com/ref/internal-address-formats/
        template = "%(name)s\n%(address)s\n%(postcode)s %(town)s %(county)s"
        if locale in ( "en", "en_CA", "en_AU", "en_IN", "en_KA", "en_PH", "en_TH", "en_VN", "th" ):
            # US style, city/state/zip on last line
            template = "%(name)s\n%(address)s\n%(town)s %(county)s %(postcode)s"
        elif locale in ( "en_GB", "en_IE", "en_ZA" ):
            # UK style, postcode on last line
            template = "%(name)s\n%(address)s\n%(town)s\n%(county)s\n%(postcode)s"
        elif locale in ( "bs", "bg", "cs", "de", "el", "en_CN", "en_NZ", "es", 
            "es_EC", "en_MX", "es_MX", "fr", "he", "it", "lt", "nb", "nl", "pl", "pt", 
            "ru", "sk", "sl", "sv", "tr" ):
            # European style, postcode precedes city/state on last line
            template = "%(name)s\n%(address)s\n%(postcode)s %(town)s %(county)s"
        ad = template % { "name": rd["OWNERNAME"], "address": rd["OWNERADDRESS"], "town": rd["OWNERTOWN"],
            "county": rd["OWNERCOUNTY"], "postcode": rd["OWNERPOSTCODE"] }
        #al.debug("Adding to data col=%d, row=%d, val=%s" % (cold, rowd, ad))
        datad[rowd][cold] = ad

    def addTable(datad):
        #al.debug("Adding data to table: " + str(datad))
        t = Table(datad, cols * [ hpitch * unit ], rows * [ vpitch * unit ])
        t.hAlign = "LEFT"
        t.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("FONTNAME", (0,0), (-1,-1), fontname)
            ]))
        # If we have more than 8 labels vertically, use a smaller font size
        if rows > 8:
            t.setStyle(TableStyle([
                ("VALIGN", (0,0), (-1,-1), "TOP"),
                ("FONTSIZE", (0,0), (-1,-1), 8),
                ("FONTNAME", (0,0), (-1,-1), fontname)
                ]))
        elements.append(t)

    data = newData()
    asm3.al.debug("creating mailing label PDF from %d rows" % len(records), "utils.generate_label_pdf", dbo)
    for r in records:
        addToData(r, data, col, row)
        # move to next label position
        col += 1
        if col == cols: 
            row += 1
            col = 0
            if row == rows:
                # We've filled the page, create the table and add it
                row = 0
                col = 0
                addTable(data)
                # reset the data for the next page
                data = newData()
                # TODO: Add pagebreak?

    # Add anything pending to the page
    addTable(data)
    # Build the PDF
    doc.build(elements)
    return fout.getvalue()

def replace_url_token(body, url, text):
    """
    Used by email dialogs that want to send a URL in the message. 
    If the token $URL is present in body, then substitute it for url, 
    otherwise append url to the end of the body.
    body: The body to replace $URL in
    url: The the href
    text: The anchor text
    returns the new body
    """
    url_token = "$URL"
    replace_html_string = "<a href=\"%s\">%s</a>"
    append_html_string = "<p><a href=\"%s\">%s</a></p>"
    if url_token in body:
        body = body.replace(url_token, replace_html_string % (url, text))
    else:
        body += "\n" + append_html_string % (url, text)
    return body

def is_valid_email_address(s):
    """ Returns True if s is a valid email address """
    regex = "^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
    return (re.search(regex, s) is not None)

def parse_email_address(s):
    """ Returns a tuple of realname and address from an email """
    if s.find("<") == -1: return ("", s.strip())
    return ( s[0:s.find("<")].strip(), s[s.find("<")+1:].replace(">", "").strip() )

def strip_email_address(s):
    # Just returns the address portion of an email
    return parse_email_address(s)[1]

def send_email(dbo, replyadd, toadd, ccadd = "", bccadd = "", subject = "", body = "", contenttype = "plain", attachments = [], exceptions = True):
    """
    Sends an email.
    fromadd is a single email address
    toadd is a comma/semi-colon separated list of email addresses 
    ccadd is a comma/semi-colon separated list of email addresses
    bccadd is a comma/semi-colon separated list of email addresses
    subject, body are strings
    contenttype is either "plain" or "html"
    attachments: A list of tuples in the form (filename, mimetype, data)
    exceptions: If True, throws exceptions due to sending problems

    returns True on success

    For HTML emails, a plaintext part is converted and added. If the HTML
    does not have html/body tags, they are also added.
    """

    def add_header(msg, header, value):
        """
        Adds a header to the message, expands any HTML entities
        and relies on Python's email.header.Header class to
        handle encoding to UTF-8 and outputting as quoted printable
        where necessary.
        """
        if header in ("From", "To", "Cc", "Bcc", "Bounces-To", "Reply-To"):
            # We cannot support UTF-8/QP encoded addresses because
            # it blows up sSMTP and other mail servers.
            # Instead, only include ascii chars and throw the rest away.
            # We don't use xmlcharref as elsewhere because the HTML entities
            # aren't really human readable and the semi-colons will cause some
            # mail servers to see the address as multiple addresses.
            msg[header] = Header(value.encode("ascii", "replace"))
        elif header in ("DISABLED"):
            # INFO: This code supports using QP-encoded UTF-8 for the realname
            # portion of email addresses in the headers listed above.
            # This condition will never be hit and this code is not active 
            # because too many email providers and servers do not support this.
            h = Header()
            for a in value.split(","):
                if len(str(h)) > 0: h.append(",", "ascii")
                realname, address = parse_email_address(a)
                h.append(realname) # auto uses utf-8 for non-ascii
                h.append(address, "ascii")
            msg[header] = h
        elif header == "Subject":
            # The subject header should be fewer than 78 chars
            # len("Subject: ") == 9, 78 - 9 == 69
            # gmail and some providers hide the subject if it goes over this length
            msg[header] = Header(truncate(value, 69))
        else:
            msg[header] = Header(value)

    # If the email is plain text, but contains HTML escape characters, 
    # switch it to being an html message instead and make sure line 
    # breaks are retained
    if body.find("&#") != -1 and contenttype == "plain":
        contenttype = "html"
        body = body.replace("\n", "<br />")

    # If the message is HTML, but does not contain an HTML tag, assume it's
    # a document fragment and wrap it (this lowers spamassassin scores)
    if body.find("<html") == -1 and contenttype == "html":
        body = "<!DOCTYPE html>\n<html>\n<body>\n%s</body></html>" % body

    # Fix any relative image links in the html message
    if contenttype == "html":
        body = fix_relative_document_uris(dbo, body)

    # Build the from address
    # If we don't have an SMTPOverride, use the sitedef to construct the from address
    # Otherwise, use the reply address
    fromadd = replyadd
    if not asm3.configuration.smtp_override(dbo):
        fromadd = FROM_ADDRESS
        fromadd = fromadd.replace("{organisation}", asm3.configuration.organisation(dbo))
        fromadd = fromadd.replace("{alias}", dbo.alias)
        fromadd = fromadd.replace("{database}", dbo.database)
        fromadd = fromadd.replace(",", "") # commas blow up address parsing

    # Check for any problems in the reply address, such as unclosed address
    if replyadd.find("<") != -1 and replyadd.find(">") == -1:
        replyadd += ">"

    # Construct the mime message
    msg = MIMEMultipart("mixed")
    add_header(msg, "From", fromadd)
    add_header(msg, "To", toadd)
    if ccadd != "": add_header(msg, "Cc", ccadd)
    if bccadd != "" and SMTP_SERVER and SMTP_SERVER["sendmail"]: 
        # sendmail -t processes and removes Bcc header, where SMTP has all recipients (including Bcc) in tolist
        add_header(msg, "Bcc", bccadd) 
    add_header(msg, "Reply-To", replyadd)
    add_header(msg, "Bounces-To", replyadd)
    add_header(msg, "Message-ID", make_msgid())
    add_header(msg, "Date", formatdate())
    add_header(msg, "X-Mailer", "Animal Shelter Manager %s" % asm3.i18n.VERSION)
    add_header(msg, "Subject", subject)

    # Create an alternative part with plain text and html messages
    msgbody = MIMEMultipart("alternative")

    # Attach the plaintext portion
    plaintext = iif(contenttype == "html", html_to_text(body), body)
    msgbody.attach(MIMEText(plaintext, "plain"))

    # Attach the HTML portion if this is an HTML message
    if contenttype == "html":
        msgbody.attach(MIMEText(body, "html"))
    
    # Add the message text
    msg.attach(msgbody)

    # If file attachments have been specified, add them to the message
    if len(attachments) > 0:
        for filename, mimetype, data in attachments:
            if mimetype == "": mimetype = "application/octet-stream"
            left, right = mimetype.split("/")
            part = MIMEBase(left, right)
            part.set_payload( data )
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % filename)
            msg.attach(part)
 
    # Construct the list of to addresses. We strip email addresses so
    # only the you@domain.com portion remains for us to pass to the
    # SMTP server. 
    tolist = [strip_email_address(x) for x in toadd.split(",")]
    if ccadd != "":  tolist += [strip_email_address(x) for x in ccadd.split(",")]
    if bccadd != "": tolist += [strip_email_address(x) for x in bccadd.split(",")]

    replyadd = strip_email_address(replyadd)

    asm3.al.debug("from: %s, reply-to: %s, to: %s, subject: %s, body: %s" % \
        (fromadd, replyadd, str(tolist), subject, body), "utils.send_email", dbo)

    _send_email(msg, fromadd, tolist, dbo, exceptions=exceptions)

def _send_email(msg, fromadd, tolist, dbo=None, exceptions=True):
    """
    Internal function to handle the final transmission of an email message.
    msg: The python message object
    fromadd: The from address "me@me.com"
    tolist: A list of recipient addresses [ "add1@test.com", "add2@test.com" ... ]
    dbo can be None, is only used for logging
    exceptions: If True throws exceptions on error, otherwise returns success boolean
    """
    # Load the server config over default vars
    sendmail = True
    host = ""
    port = 25
    username = ""
    password = ""
    usetls = False
    if SMTP_SERVER is not None:
        if "sendmail" in SMTP_SERVER: sendmail = SMTP_SERVER["sendmail"]
        if "host" in SMTP_SERVER: host = SMTP_SERVER["host"]
        if "port" in SMTP_SERVER: port = SMTP_SERVER["port"]
        if "username" in SMTP_SERVER: username = SMTP_SERVER["username"]
        if "password" in SMTP_SERVER: password = SMTP_SERVER["password"]
        if "usetls" in SMTP_SERVER: usetls = SMTP_SERVER["usetls"]
        if "headers" in SMTP_SERVER: 
            for k, v in SMTP_SERVER["headers"].items():
                msg[k] = Header(v)

    # If we have a dbo and there's an smtp override in the database, use it
    if dbo and asm3.configuration.smtp_override(dbo):
        sendmail = False
        host = asm3.configuration.smtp_server(dbo)
        port = asm3.utils.cint(asm3.configuration.smtp_port(dbo))
        usetls = asm3.configuration.smtp_use_tls(dbo)
        username = asm3.configuration.smtp_username(dbo)
        password = asm3.configuration.smtp_password(dbo)
     
    # Use sendmail or SMTP for the transport depending on config
    if sendmail:
        try:
            p = subprocess.Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdoutdata, stderrdata = p.communicate(str2bytes(msg.as_string()))
            if p.returncode != 0: raise Exception("%s %s" % (stdoutdata, stderrdata))
            return True
        except Exception as err:
            asm3.al.error("sendmail: %s" % str(err), "utils.send_email", dbo)
            if exceptions: raise ASMError(str(err))
            return False
    else:
        try:
            smtp = smtplib.SMTP(host, port)
            if usetls:
                smtp.starttls()
            if password.strip() != "":
                smtp.login(username, password)
            smtp.sendmail(fromadd, tolist, msg.as_string())
            return True
        except Exception as err:
            asm3.al.error("smtp: %s" % str(err), "utils.send_email", dbo)
            if exceptions: raise ASMError(str(err))
            return False

def send_bulk_email(dbo, fromadd, subject, body, rows, contenttype):
    """
    Sends a set of bulk emails asynchronously.
    fromadd is an RFC821 address
    subject and body are strings. Either can contain <<TAGS>>
    rows is a list of dictionaries of tag tokens with real values to substitute
    contenttype is either "plain" or "html"
    """
    def do_send():
        for r in rows:
            ssubject = substitute_tags(subject, r, False, opener = "<<", closer = ">>")
            sbody = substitute_tags(body, r)
            toadd = r["EMAILADDRESS"]
            if toadd is None or toadd.strip() == "": continue
            asm3.al.debug("sending bulk email: to=%s, subject=%s" % (toadd, ssubject), "utils.send_bulk_email", dbo)
            send_email(dbo, fromadd, toadd, "", "", ssubject, sbody, contenttype, exceptions=False)
    thread.start_new_thread(do_send, ())

def send_error_email():
    """
    Used for sending email messages about errors that have occurred.
    """
    tb = sys.exc_info()
    error_name = tb[0]
    error_value = tb[1]
    msg = MIMEMultipart("mixed")
    msg["From"] = Header(ADMIN_EMAIL)
    msg["To"] = Header(ADMIN_EMAIL)
    msg["Subject"] = Header(f"{error_name}: {error_value} ({web.ctx.path})")
    msg.attach(MIMEText(str(web.djangoerror()), "html"))
    _send_email(msg, ADMIN_EMAIL, [ADMIN_EMAIL], exceptions=False)

def send_user_email(dbo, sendinguser, user, subject, body):
    """
    Sends an email to users.
    sendinguser: The username of the person sending the email (we will look up their email)
    user:        can be an individual username, a rolename or the translated 
                 version of (all) or (everyone) to denote all users.
    """
    DEFAULT_EMAIL = "noreply@sheltermanager.com"
    sendinguser = asm3.users.get_users(dbo, sendinguser)
    if len(sendinguser) == 0:
        fromadd = DEFAULT_EMAIL
    else:
        fromadd = sendinguser[0]["EMAILADDRESS"]
        if fromadd is None or fromadd.strip() == "":
            fromadd = DEFAULT_EMAIL
    asm3.al.debug("from: %s (%s), to: %s" % (sendinguser, fromadd, user), "utils.send_user_email", dbo)
    allusers = asm3.users.get_users(dbo)
    for u in allusers:
        # skip if we have no email address - we can't send it.
        if u["EMAILADDRESS"] is None or u["EMAILADDRESS"].strip() == "": continue
        if user == "*":
            send_email(dbo, fromadd, u["EMAILADDRESS"], "", "", subject, body, exceptions=False)
        elif u["USERNAME"] == user:
            send_email(dbo, fromadd, u["EMAILADDRESS"], "", "", subject, body, exceptions=False)
        elif nulltostr(u["ROLES"]).find(user) != -1:
            send_email(dbo, fromadd, u["EMAILADDRESS"], "", "", subject, body, exceptions=False)


