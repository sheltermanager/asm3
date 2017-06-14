#!/usr/bin/python

import dbms.hsqldb, dbms.mysql, dbms.postgresql, dbms.sqlite
import i18n
import utils

from sitedefs import DB_DECODE_HTML_ENTITIES, DB_TYPE, MULTIPLE_DATABASES_MAP

def get_database(t = None):
    """ Returns a database object for the current database backend, or type t if supplied """
    m = {
        "HSQLDB":       dbms.hsqldb.DatabaseHSQLDB,
        "MYSQL":        dbms.mysql.DatabaseMySQL,
        "POSTGRESQL":   dbms.postgresql.DatabasePostgreSQL,
        "SQLITE":       dbms.sqlite.DatabaseSQLite3
    }
    if t is None: t = DB_TYPE
    x = m[t]()
    x.dbtype = t
    return x

def get_multiple_database_info(alias):
    """ Gets the Database object for the alias in our map MULTIPLE_DATABASES_MAP. """
    if alias not in MULTIPLE_DATABASES_MAP:
        dbo = get_database()
        dbo.database = "FAIL"
        return dbo
    mapinfo = MULTIPLE_DATABASES_MAP[alias]
    dbo = get_database(mapinfo["dbtype"])
    dbo.alias = alias
    dbo.dbtype = mapinfo["dbtype"]
    dbo.host = mapinfo["host"]
    dbo.port = mapinfo["port"]
    dbo.username = mapinfo["username"]
    dbo.password = mapinfo["password"]
    dbo.database = mapinfo["database"]
    return dbo

# Deprecated compatibility (replace in code with parameterised dbo.X versions)

def query(dbo, sql, limit = 0):
    return dbo.query(sql, limit=limit)

def query_cache(dbo, sql, age = 60, limit = 0):
    return dbo.query_cache(sql, age=age, limit=limit)

def query_columns(dbo, sql):
    return dbo.query_columns(sql)

def query_tuple(dbo, sql):
    return dbo.query_tuple(sql)

def query_tuple_columns(dbo, sql):
    return dbo.query_tuple_columns(sql)

def execute_dbupdate(dbo, sql):
    return dbo.execute_dbupdate(sql)

def execute(dbo, sql, override_lock=False):
    return dbo.execute(sql, override_lock=override_lock)

def get_id(dbo, table):
    return dbo.get_id(table)
 
def query_int(dbo, sql):
    return dbo.query_int(sql)

def query_float(dbo, sql):
    return dbo.query_float(sql)

def query_string(dbo, sql):
    return dbo.query_string(sql)

def query_date(dbo, sql):
    return dbo.query_date(sql)

# ==

# These should be no longer necessary one day when all code is using dbo.insert/update/delete

def ddt(d):
    """ Formats a python date and time as a date for the database """
    if d is None: return "NULL"
    return "'%04d-%02d-%02d %02d:%02d:%02d'" % ( d.year, d.month, d.day, d.hour, d.minute, d.second )

def dd(d):
    """ Formats a python date as a date for the database """
    if d is None: return "NULL"
    return "'%04d-%02d-%02d 00:00:00'" % ( d.year, d.month, d.day )

def ds(s, sanitise_xss = True):
    """ Formats a value as a string for the database """
    if s is None: 
        return u"NULL"
    elif not utils.is_str(s) and not utils.is_unicode(s):
        return u"'%s'" % str(s)
    elif not DB_DECODE_HTML_ENTITIES:
        s = utils.encode_html(s)            # Turn any leftover unicode chars into HTML entities
        s = get_database().escape(s)        # DB/SQL injection safe
        if sanitise_xss: s = escape_xss(s)  # XSS
        return u"'%s'" % s
    else:
        s = utils.decode_html(s)            # Turn HTML entities into unicode symbols
        s = get_database().escape(s)        # DB/SQL injection safe
        if sanitise_xss: s = escape_xss(s)  # XSS
        return u"'%s'" % s

def df(f):
    """ Formats a value as a float for the database """
    if f is None: return "NULL"
    return str(f)

def di(i):
    """ Formats a value as an integer for the database """
    if i is None: return "NULL"
    s = str(i)
    try:
        return str(int(s))
    except:
        return "0"

def escape_xss(s):
    """ Make a value safe from XSS attacks by encoding tag delimiters """
    return s.replace(">", "&gt;").replace("<", "&lt;")

# Calls to methods below should be replaced with "insert" and "update" methods of Database 

def make_insert_sql(table, s):
    """
    Creates insert sql, 'table' is the table name,
    's' is a tuple of tuples containing the field names
    and values, eg:
    
    make_insert_sql("animal", ( ( "ID", di(52) ), ( "AnimalName", ds("Indy") ) ))
    """
    fl = ""
    fv = ""
    for r in s:
        if r is None: break
        if fl != "": 
            fl += ", "
            fv += ", "
        fl += r[0]
        fv += r[1]
    return "INSERT INTO %s (%s) VALUES (%s);" % ( table, fl, fv )

def make_insert_user_sql(dbo, table, username, s, stampRecordVersion = True):
    """
    Creates insert sql for a user, 'table' is the table name,
    username is the name of the user to be stamped in the fields
    's' is a tuple of tuples containing the field names
    and values, eg:
    
    make_insert_user_sql("animal", "jeff", ( ( "ID", di(52) ), ( "AnimalName", ds("Indy") ) ))
    """
    l = list(s)
    l.append(("CreatedBy", ds(username)))
    l.append(("CreatedDate", ddt(i18n.now(dbo.timezone))))
    l.append(("LastChangedBy", ds(username)))
    l.append(("LastChangedDate", ddt(i18n.now(dbo.timezone))))
    if stampRecordVersion: l.append(("RecordVersion", di(dbo.get_recordversion())))
    return make_insert_sql(table, l)

def make_update_sql(table, cond, s):
    """
    Creates update sql, 'table' is the table name,
    's' is a tuple of tuples containing the field names
    and values, 'cond' is the where condition eg:
    
    make_update_sql("animal", "ID = 52", (( "AnimalName", ds("James") )))
    """
    o = "UPDATE %s SET " % table
    first = True
    for r in s:
        if r is None: break
        if not first:
            o += ", "
        first = False
        o += r[0] + "=" + r[1]
    if cond != "":
        o += " WHERE " + cond
    return o

def make_update_user_sql(dbo, table, username, cond, s, stampRecordVersion = True):
    """
    Creates update sql for a given user, 'table' is the table 
    name, username is the username of the user making the change,
    cond is the where condition eg:

    make_update_user_sql("animal", "jeff", "ID = 52", (( "AnimalName", ds("James") )))
    """
    l = list(s)
    l.append(("LastChangedBy", ds(username)))
    l.append(("LastChangedDate", ddt(i18n.now(dbo.timezone))))
    if stampRecordVersion: l.append(("RecordVersion", di(dbo.get_recordversion())))
    return make_update_sql(table, cond, l)


