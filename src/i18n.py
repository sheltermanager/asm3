#!/usr/bin/python

import datetime
import json
import time

VERSION = "37u [Fri 18 Sep 14:26:24 BST 2015]"
BUILD = "09181426"

DMY = ( "%d/%m/%Y", "%d/%m/%y" )
MDY = ( "%m/%d/%Y", "%m/%d/%y" )
YMD = ( "%Y/%m/%d", "%y/%m/%d" )
DOLLAR = "$"
EURO = "&#x20ac;"
POUND = "&pound;"
YEN = "&yen;"
CURRENCY_PREFIX = "p"
CURRENCY_SUFFIX = "s"

def PLURAL_ENGLISH(n):
    """ gettext plural function for English/Latin languages """
    if n == 1: return 0
    return 1

def PLURAL_HUNGARIAN(n):
    """ gettext style plural function for Hungarian 
        Hungarian always uses the singular unless the element appears
        by itself (which it never does for the purposes of ngettext)
        so always return the singular
    """
    return 0

def PLURAL_POLISH(n):
    """ gettext style plural function for Polish """
    if n == 1: return 0
    if n % 10 >= 2 and n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20): return 1
    return 2

def PLURAL_SLAVIC(n):
    """ gettext style plural function for Slavic languages,
        Russian, Ukrainian, Belarusian, Serbian, Croatian
    """
    if n % 10 == 1 and n % 100 != 11: return 0
    if n % 10 >= 2 and n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20): return 1
    return 2

# Maps of locale to currency/date format
locale_maps = {
    "en":       ( MDY, DOLLAR, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "en_GB":    ( DMY, POUND, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "en_AU":    ( DMY, DOLLAR, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "en_BH":    ( MDY, "BD", PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "en_CA":    ( MDY, DOLLAR, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "en_CN":    ( YMD, YEN, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "en_CY":    ( DMY, EURO, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "en_KW":    ( DMY, "KD", PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "en_KY":    ( DMY, DOLLAR, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "en_IE":    ( DMY, EURO, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "en_IN":    ( DMY, "Rs.", PLURAL_ENGLISH, CURRENCY_PREFIX, 2),
    "en_LU":    ( DMY, EURO, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "en_MX":    ( DMY, DOLLAR, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "en_PH":    ( DMY, "&#x20b1;", PLURAL_ENGLISH, CURRENCY_PREFIX, 2),
    "en_QA":    ( DMY, "QR", PLURAL_ENGLISH, CURRENCY_PREFIX, 2),
    "en_NZ":    ( DMY, DOLLAR, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "en_TH":    ( DMY, "&#x0e3f;", PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "en_TW":    ( DMY, DOLLAR, PLURAL_ENGLISH, CURRENCY_PREFIX, 0 ),
    "en_VN":    ( DMY, "&#8363;", PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "en_ZA":    ( YMD, "R", PLURAL_ENGLISH, CURRENCY_PREFIX, 2),
    "bg":       ( DMY, "&#x043b;&#x0432;", PLURAL_ENGLISH, CURRENCY_SUFFIX, 2),
    "bs":       ( DMY, "KM", PLURAL_ENGLISH, CURRENCY_PREFIX, 2),
    "cs":       ( YMD, "&#x004b;&#x010d;", PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "de":       ( DMY, EURO, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "de_LU":    ( DMY, EURO, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "de_AT":    ( DMY, EURO, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "el":       ( DMY, EURO, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "es":       ( DMY, EURO, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "es_EC":    ( DMY, DOLLAR, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "es_MX":    ( DMY, DOLLAR, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "et":       ( DMY, "kr", PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "fr":       ( DMY, EURO, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "fr_LU":    ( DMY, EURO, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "fr_CA":    ( MDY, DOLLAR, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "he":       ( DMY, "&#x20aa;", PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "hu":       ( DMY, "Ft",  PLURAL_HUNGARIAN, CURRENCY_PREFIX, 2), 
    "it":       ( DMY, EURO, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "lt":       ( YMD, EURO, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "nb":       ( DMY, "kr", PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "nl":       ( DMY, EURO, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "pl":       ( DMY, "&#x007a;&#x0142;", PLURAL_POLISH, CURRENCY_PREFIX, 2 ),
    "pt":       ( DMY, EURO, PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "ru":       ( DMY, "&#1056;&#1059;&#1041;.", PLURAL_SLAVIC, CURRENCY_PREFIX, 2 ),
    "sk":       ( DMY, EURO, PLURAL_SLAVIC, CURRENCY_PREFIX, 2 ),
    "sl":       ( DMY, EURO, PLURAL_SLAVIC, CURRENCY_PREFIX, 2 ),
    "sv":       ( DMY, "kr", PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "th":       ( DMY, "&#x0e3f;", PLURAL_ENGLISH, CURRENCY_PREFIX, 2 ),
    "tr":       ( DMY, "TL", PLURAL_ENGLISH, CURRENCY_PREFIX, 2 )
}

def _(english, locale = "en"):
    return translate(english, locale)

def real_locale(locale = "en"):
    # Treat some locales as pointers to other locales with out the
    # need for a full translation:
    # Our core English locales (with actual differences) are:
    #   en    (US)
    #   en_AU (AUS)
    #   en_GB (UK)
    if locale in ("en_CY", "en_IE", "en_IN", "en_LU", "en_NZ", "en_PH", "en_TH", "en_TW", "en_VN", "en_ZA"):
        locale = "en_GB"
    if locale in ("en_CA", "en_KY", "en_KW", "en_BH", "en_MX"):
        locale = "en"
    if locale in ("en_NZ",):
        locale = "en_AU"
    # French locales
    if locale in ("fr_CA", "fr_LU"):
        locale = "fr"
    # German locales
    if locale in ("de_AT", "de_LU"):
        locale = "de"
    # Spanish locales
    if locale in ("es_EC", "es_MX"):
        locale = "es"
    return locale

def translate(english, locale = "en"):
    """
    Returns a translation string for an English phrase in
    the locale given.
    """
    locale = real_locale(locale)

    # If we're dealing with English, then just
    # return the English phrase. I hate that I'm doing
    # this, but I'm going with the accepted standard of
    # US English being default even though we invented
    # the bloody language.
    if locale == "en":
        return english

    # Otherwise, look up the phrase in the correct
    # module for our locale (modules are large
    # val dictionaries containing an english string as
    # the key - we generate them automatically 
    # from po files and they're all prefixed with
    # locale_). The python manual says we were safe
    # to do this as importing is a non-operation for
    # already imported modules
    try:
        lang = __import__("locale_" + locale)
    except:
        # The module doesn't exist for the locale, fall
        # back to plain English translation
        return english

    # If the string isn't in our locale dictionary, fall back to English
    if not lang.val.has_key(english): return english

    # If the value hasn't been translated, fall back to English
    s = lang.val[english]
    if s is None or s == "" or s.startswith("??") or s.startswith("(??"):
        return english
    else:
        return lang.val[english]

def ntranslate(number, translations, locale = "en"):
    """ Translates a phrase that deals with a number of something
        so the correct plural can be used. 
        number: The number of items
        translations: A list of already translated strings for each plural form
        locale: The locale the strings are in (which plural function to use)
    """
    try:
        pluralfun = locale_maps[locale][2]
        text = translations[pluralfun(number)]
        text = text.replace("{plural0}", str(number))
        text = text.replace("{plural1}", str(number))
        text = text.replace("{plural2}", str(number))
        text = text.replace("{plural3}", str(number))
        text = text.replace("{plural4}", str(number))
        return text
    except Exception,e:
        return e

def get_version():
    """
    Returns the version of ASM
    """
    return VERSION

def get_version_number():
    """
    Returns the version number of ASM
    """
    return VERSION[0:VERSION.find(" ")]

def get_display_date_format(locale, digitsinyear = 4):
    """
    Returns the display date format for a locale
    """
    if digitsinyear == 4:
        return locale_maps[locale][0][0]
    else:
        return locale_maps[locale][0][1]

def get_currency_symbol(locale):
    """
    Returns the currency symbol for a locale
    """
    return locale_maps[locale][1]

def get_currency_dp(locale):
    """
    Returns the number of decimal places for a locale when
    displaying currency
    """
    return locale_maps[locale][4]

def get_currency_prefix(locale):
    """
    Returns "p" if the currency symbol goes at the beginning, or "s" for the end
    when displaying.
    """
    return locale_maps[locale][3]

def format_currency(locale, value):
    """
    Formats a currency value to the correct number of 
    decimal places and returns it as a string
    """
    if value is None: value = 0
    i = 0
    f = 0.0
    try:
        i = int(value)
        f = float(i)
    except:
        pass
    f = f / 100
    negative = False
    if f < 0: 
        negative = True
        f = abs(f)
    fstr = "%d"
    if get_currency_dp(locale) > 0:
        fstr = "%0." + str(get_currency_dp(locale)) + "f" 
    if negative:
        if locale_maps[locale][3] == CURRENCY_PREFIX:
            return "(" + get_currency_symbol(locale) + (fstr % f) + ")"
        else:
            return "(" + (fstr % f) + get_currency_symbol(locale) + ")"
    else:
        if locale_maps[locale][3] == CURRENCY_PREFIX:
            return get_currency_symbol(locale) + fstr % f
        else:
            return fstr % f + get_currency_symbol(locale)

def format_currency_no_symbol(locale, value):
    """
    Formats a currency value to the correct number of 
    decimal places and returns it as a string
    """
    if value is None: value = 0
    i = int(value)
    f = float(i)
    f = f / 100
    negative = False
    if f < 0: 
        negative = True
        f = abs(f)
    fstr = "%0." + str(get_currency_dp(locale)) + "f" 
    if negative:
        return "(" + (fstr % f) + ")"
    else:
        return fstr % f

def format_time(d):
    return time.strftime("%H:%M:%S", d.timetuple())

def format_time_now(offset = 0):
    return format_time(now(offset))

def http_date(dt):
    """
    Formats a UTC python date/time in HTTP (RFC1123) format
    """
    weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
             "Oct", "Nov", "Dec"][dt.month - 1]
    return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
        dt.year, dt.hour, dt.minute, dt.second)

def python2display(locale, d):
    """
    Formats a python date as a display string. 'd' is
    a Python date, return value is a display string.
    """
    if d is None: return ""
    try:
        return time.strftime(get_display_date_format(locale), d.timetuple())
    except:
        return ""

def python2unix(d):
    """
    Converts a python date to unix.
    """
    try:
        return time.mktime(d.timetuple())
    except:
        return 0

def format_date(dateformat, d):
    """
    Formats a python date to the format given (strftime rules)
    """
    if d is None: return ""
    try:
        return time.strftime(dateformat, d.timetuple())
    except:
        return ""

def display2python(locale, d):
    """
    Parses a display string back to python format. Can cope with
    2 or 4 digit years.
    'd' is a string. return value is the date or None if it
    could not be parsed
    """
    try:
        return datetime.datetime.strptime(d, get_display_date_format(locale, 2))
    except:
        try:
            return datetime.datetime.strptime(d, get_display_date_format(locale, 4))
        except:
            return None

def parse_date(dateformat, d):
    """
    Parses a python date from the dateformat given
    """
    try:
        return datetime.datetime.strptime(d, dateformat)
    except:
        return None

def yes_no(l, condition):
    if condition:
        return _("Yes", l)
    else:
        return _("No", l)

def yes_no_unknown(l, v):
    if v == 0: return _("Yes", l)
    elif v == 1: return _("No", l)
    else: return _("Unknown", l)

def yes_no_unknown_blank(l, v):
    if v == 0: return _("Yes", l)
    elif v == 1: return _("No", l)
    else: return ""

def adjust_hour(hour, offset = 0):
    """
    Given an hour as an integer, applies the offset to get
    a new hour.
    """
    d = datetime.datetime.now()
    d = datetime.datetime(d.year, d.month, d.day, hour, 0, 0)
    if offset < 0:
        d -= datetime.timedelta(hours = abs(offset))
    else:
        d += datetime.timedelta(hours = offset)
    return d.hour

def add_months(date, months = 1):
    """
    Adds calendar months to a date, returning a new datetime
    """
    newmonth = ((( date.month - 1) + months ) % 12 ) + 1
    newyear  = date.year + ((( date.month - 1) + months ) // 12 )
    try:
        return datetime.datetime( newyear, newmonth, date.day )
    except:
        return datetime.datetime( newyear, newmonth, 28 )

def add_years(date, years = 1.0):
    """
    Adds years to a date, returning a new datetime
    """
    if date is None: return None
    return date + datetime.timedelta(days = int(years * 365))

def add_days(date, nodays = 1):
    """
    Adds days to a date, returning a new datetime
    """
    if date is None: return None
    return date + datetime.timedelta(days = nodays)

def subtract_days(date, nodays = 1):
    """
    Subtract days from date, returning a new datetime
    """
    if date is None: return None
    return date - datetime.timedelta(days = nodays)

def subtract_years(date, years = 1.0):
    """
    Subtracts years from date, returning a new datetime
    """
    if date is None: return None
    return date - datetime.timedelta(days = int(years * 365))

def subtract_months(date, months = 1):
    """
    Subtracts months from a date. Will not work after 11 months.
    """
    def subtract_one_month(t):
        one_day = datetime.timedelta(days=1)
        one_month_earlier = t - one_day
        while one_month_earlier.month == t.month or one_month_earlier.day > t.day:
            one_month_earlier -= one_day
        return one_month_earlier
    for dummy in xrange(0, months):
        date = subtract_one_month(date)
    return date
    #year, month = divmod(months, 12)
    #if date.month <= month:
    #    year = date.year - 1
    #    month = date.month - month + 12
    #else:
    #    year = date.year 
    #    month = date.month - month
    #return date.replace(year = year, month = month)

def monday_of_week(date):
    """
    Returns the monday of the current week of date.
    """
    if date is None: return None
    while True:
        if date.weekday() == 0:
            return date
        date = subtract_days(date, 1)

def sunday_of_week(date):
    """
    Returns the sunday of the current week of date.
    """
    if date is None: return None
    while True:
        if date.weekday() == 6:
            return date
        date = add_days(date, 1)

def first_of_month(date):
    """
    Returns the first of the current month of date.
    """
    return date.replace(day = 1)

def first_of_year(date):
    """
    Returns the first of the current year.
    """
    return date.replace(day = 1, month = 1)

def last_of_month(date):
    """
    Returns the last of the current month of date.
    """
    date = add_months(date, 1)
    date = first_of_month(date)
    return subtract_days(date, 1)

def last_of_year(date):
    """
    Returns the last of the current year of date.
    """
    date = add_years(date, 1)
    date = first_of_year(date)
    return subtract_days(date, 1)

def after(date1, date2):
    """
    returns true if date1 is after date2
    """
    return date_diff_days(date1, date2) < 0

def date_diff_days(date1, date2):
    """
    Returns the difference in days between two dates. It's
    assumed that date2 > date1. We aren't using subtraction
    for timedeltas because it doesn't seem to work correctly
    when subtracting date from datetime (and some items
    in the database come through as date). Instead, we convert
    to unix time to calculate.
    (datetime) date1
    (datetime) date2
    """
    if date1 is None or date2 == None: return 0
    try:
        ux1 = time.mktime(date1.timetuple())
        ux2 = time.mktime(date2.timetuple())
        delta = int((ux2 - ux1) / 60 / 60 / 24)
        return delta
    except:
        print "Invalid date: %s or %s" % ( date1, date2 )
        return 0

def date_diff(l, date1, date2):
    """
    Returns a string representing the difference between two
    dates. Eg: 6 weeks, 5 months.
    It is expected that date2 > date1
    (datetime) date1
    (datetime) date2
    """
    days = int(date_diff_days(date1, date2))
    if days < 0: days = 0
    weeks = int(days / 7)
    months = int(days / 30.5)
    years = int(days / 365)
   
    # If it's less than a week, show as days
    if days < 7:
        return ntranslate(days, [ _("{plural0} day.", l), _("{plural1} days.", l), _("{plural2} days.", l), _("{plural3} days.")], l)
    # If it's 16 weeks or less, show as weeks
    elif weeks <= 16:
        return ntranslate(weeks, [ _("{plural0} week.", l), _("{plural1} weeks.", l), _("{plural2} weeks.", l), _("{plural3} weeks.")], l)
    # If it's a year or less, show as months
    elif weeks <= 52:
        return ntranslate(months, [ _("{plural0} month.", l), _("{plural1} months.", l), _("{plural2} months.", l), _("{plural3} months.")], l)
    else:
        # Show as years and months
        months = int((days % 365) / 30.5)
        return ntranslate(years, [ _("{plural0} year.", l), _("{plural1} years.", l), _("{plural2} years.", l), _("{plural3} years.")], l).replace(".", "") + \
            " " + ntranslate(months, [ _("{plural0} month.", l), _("{plural1} months.", l), _("{plural2} months.", l), _("{plural3} months.")], l)

def now(offset = 0):
    """
    Returns a python date representing now
    offset: A UTC offset to apply in hours
    """
    if offset < 0:
        return datetime.datetime.now() - datetime.timedelta(hours = abs(offset))
    else:
        return datetime.datetime.now() + datetime.timedelta(hours = offset)

def today():
    """
    Returns a python datetime set to today, but with time information at midnight.
    """
    d = datetime.datetime.now()
    return datetime.datetime(d.year, d.month, d.day)

def i18nstringsjs(l):
    """
    Returns a javascript format file containing the language file
    """
    langs = "{}"
    try:
        lang = __import__("locale_" + real_locale(l))
        langs = json.dumps(lang.val)
    except:
        pass
    s = "i18n_lang = " + langs + ";\n";
    s += """
(function($) {
    _ = function(key) {
        try {
            var v = key;
            if (i18n_lang.hasOwnProperty(key)) {
                if ($.trim(i18n_lang[key]) != "" && i18n_lang[key].indexOf("??") != 0 && i18n_lang[key].indexOf("(??") != 0) {
                    v = i18n_lang[key];
                }
                else {
                    v = key;
                }
            }
            else {
                v = key;
            }
            return $("<div></div>").html(v).text();
        }
        catch (err) {
            return "[error]";
        }
    };
}) (jQuery);\n"""
    return s
