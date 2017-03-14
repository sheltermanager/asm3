#!/usr/bin/python

import al
import cachemem
import datetime
import i18n
import sys
import time
import utils
from sitedefs import DB_TYPE, DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD, DB_NAME, DB_HAS_ASM2_PK_TABLE, DB_PK_STRATEGY, DB_DECODE_HTML_ENTITIES, DB_EXEC_LOG, DB_EXPLAIN_QUERIES, DB_TIME_QUERIES, DB_TIME_LOG_OVER, DB_TIMEOUT, CACHE_COMMON_QUERIES, MULTIPLE_DATABASES_MAP


try:
    import MySQLdb
except:
    pass

try:
    import psycopg2
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
except:
    pass

try:
    import sqlite3
except:
    pass

class DatabaseInfo(object):
    """
    Handles information on connecting to a database.
    Default values are supplied by the sitedefs.py file.
    """
    dbtype = DB_TYPE # MYSQL, POSTGRESQL or SQLITE
    host = DB_HOST
    port = DB_PORT
    username = DB_USERNAME
    password = DB_PASSWORD
    database = DB_NAME
    alias = "" 
    locale = "en"
    timezone = 0
    installpath = ""
    locked = False
    has_asm2_pk_table = DB_HAS_ASM2_PK_TABLE
    is_large_db = False
    timeout = DB_TIMEOUT
    connection = None
    def __repr__(self):
        return "DatabaseInfo->locale=%s:dbtype=%s:host=%s:port=%d:db=%s:user=%s:timeout=%s" % ( self.locale, self.dbtype, self.host, self.port, self.database, self.username, self.timeout )

def connection(dbo):
    """
        Creates a connection to the database and returns it
    """
    try:
        if dbo.dbtype == "MYSQL": 
            if dbo.password != "":
                return MySQLdb.connect(host=dbo.host, port=dbo.port, user=dbo.username, passwd=dbo.password, db=dbo.database, charset="utf8", use_unicode=True)
            else:
                return MySQLdb.connect(host=dbo.host, port=dbo.port, user=dbo.username, db=dbo.database, charset="utf8", use_unicode=True)
        if dbo.dbtype == "POSTGRESQL": 
            c = psycopg2.connect(host=dbo.host, port=dbo.port, user=dbo.username, password=dbo.password, database=dbo.database)
            c.set_client_encoding("UTF8")
            return c
        if dbo.dbtype == "SQLITE":
            return sqlite3.connect(dbo.database, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    except Exception as err:
        al.error(str(err), "db.connection", dbo, sys.exc_info())

def connect_cursor_open(dbo):
    """
    Returns a tuple containing an open connection and cursor.
    If the dbo object contains an active connection, we'll just use
    that to get a cursor.
    """
    if dbo.connection is not None:
        c = dbo.connection
        s = dbo.connection.cursor()
    else:
        c = connection(dbo)
        s = c.cursor()
    # if timeout is non-zero, set it
    if dbo.dbtype == "POSTGRESQL" and dbo.timeout > 0:
        s.execute("SET statement_timeout=%d" % dbo.timeout)
    if dbo.dbtype == "MYSQL" and dbo.timeout > 0:
        s.execute("SET SESSION max_execution_time=%d" % dbo.timeout)
    return c, s

def connect_cursor_close(dbo, c, s):
    """
    Closes a connection and cursor pair. If dbo.connection exists, then
    c must be it, so don't close it.
    """
    try:
        s.close()
    except:
        pass
    if dbo.connection is None:
        try:
            c.close()
        except:
            pass

def query(dbo, sql):
    """ Runs the query given and returns the resultset as a list of dictionaries. 
        All fieldnames are uppercased when returned.
    """
    try:
        c, s = connect_cursor_open(dbo)
        # Explain the query if the option is on
        if DB_EXPLAIN_QUERIES:
            esql = "EXPLAIN %s" % sql
            al.debug(esql, "db.query", dbo)
            al.debug(query_explain(dbo, esql), "db.query", dbo)
        # Record start time
        start = time.time()
        # Run the query and retrieve all rows
        s.execute(sql)
        c.commit()
        d = s.fetchall()
        l = []
        cols = []
        # Get the list of column names
        for i in s.description:
            cols.append(i[0].upper())
        for row in d:
            # Intialise a map for each row
            rowmap = {}
            for i in range(0, len(row)):
                v = encode_str(dbo, row[i])
                rowmap[cols[i]] = v
            l.append(rowmap)
        connect_cursor_close(dbo, c, s)
        if DB_TIME_QUERIES:
            tt = time.time() - start
            if tt > DB_TIME_LOG_OVER:
                al.debug("(%0.2f sec) %s" % (tt, sql), "db.query", dbo)
        return l
    except Exception as err:
        al.error(str(err), "db.query", dbo, sys.exc_info())
        raise err
    finally:
        try:
            connect_cursor_close(dbo, c, s)
        except:
            pass

def query_cache(dbo, sql, age = 60):
    """
    Runs the query given and caches the result
    for age seconds. If there's already a valid cached
    entry for the query, returns the cached result
    instead.
    If CACHE_COMMON_QUERIES is set to false, just runs the query
    without doing any caching and is equivalent to db.query()
    """
    if not CACHE_COMMON_QUERIES: return query(dbo, sql)
    cache_key = utils.md5_hash("%s:%s:%s" % (dbo.alias, dbo.database, sql.replace(" ", "_")))
    results = cachemem.get(cache_key)
    if results is not None:
        return results
    results = query(dbo, sql)
    cachemem.put(cache_key, results, age)
    return results

def query_columns(dbo, sql):
    """
        Runs the query given and returns the column names as
        a list in the order they appeared in the query
    """
    try:
        c, s = connect_cursor_open(dbo)
        # Run the query and retrieve all rows
        s.execute(sql)
        c.commit()
        # Build a list of the column names
        cn = []
        for col in s.description:
            cn.append(col[0].upper())
        connect_cursor_close(dbo, c, s)
        return cn
    except Exception as err:
        al.error(str(err), "db.query_columns", dbo, sys.exc_info())
        raise err
    finally:
        try:
            connect_cursor_close(dbo, c, s)
        except:
            pass

def query_generator(dbo, sql):
    """ Runs the query given and returns the resultset as a list of dictionaries. 
        All fieldnames are uppercased when returned. 
        generator function version that uses a forward cursor.
    """
    try:
        c, s = connect_cursor_open(dbo)
        # Run the query and retrieve all rows
        s.execute(sql)
        c.commit()
        cols = []
        # Get the list of column names
        for i in s.description:
            cols.append(i[0].upper())
        row = s.fetchone()
        while row:
            # Intialise a map for each row
            rowmap = {}
            for i in range(0, len(row)):
                v = encode_str(dbo, row[i])
                rowmap[cols[i]] = v
            yield rowmap
            row = s.fetchone()
        connect_cursor_close(dbo, c, s)
    except Exception as err:
        al.error(str(err), "db.query", dbo, sys.exc_info())
        raise err
    finally:
        try:
            connect_cursor_close(dbo, c, s)
        except:
            pass

def query_to_insert_sql(dbo, sql, table, escapeCR = ""):
    """
    Generator function that Writes an INSERT query for the list of rows 
    returned by running sql (a list containing dictionaries)
    """
    fields = []
    donefields = False
    for r in query_generator(dbo, sql):
        values = []
        for k in sorted(r.iterkeys()):
            if not donefields:
                fields.append(k)
            v = r[k]
            if v is None:
                values.append("null")
            elif type(v) == unicode or type(v) == str:
                if escapeCR != "": v = v.replace("\n", escapeCR).replace("\r", "")
                values.append(ds(v))
            elif type(v) == datetime.datetime:
                values.append(ddt(v))
            else:
                values.append(di(v))
        donefields = True
        yield "INSERT INTO %s (%s) VALUES (%s);\n" % (table, ",".join(fields), ",".join(values))

def query_explain(dbo, sql):
    """
    Runs an EXPLAIN query
    """
    if not sql.lower().startswith("EXPLAIN "):
        sql = "EXPLAIN %s" % sql
    rows = query_tuple(dbo, sql)
    o = []
    for r in rows:
        o.append(r[0])
    return "\n".join(o)

def query_tuple(dbo, sql):
    """
        Runs the query given and returns the resultset
        as a grid of tuples
    """
    try:
        c, s = connect_cursor_open(dbo)
        # Run the query and retrieve all rows
        s.execute(sql)
        d = s.fetchall()
        c.commit()
        connect_cursor_close(dbo, c, s)
        return d
    except Exception as err:
        al.error(str(err), "db.query_tuple", dbo, sys.exc_info())
        raise err
    finally:
        try:
            connect_cursor_close(dbo, c, s)
        except:
            pass

def query_tuple_columns(dbo, sql):
    """
        Runs the query given and returns the resultset
        as a grid of tuples and a list of columnames
    """
    try:
        c, s = connect_cursor_open(dbo)
        # Run the query and retrieve all rows
        s.execute(sql)
        d = s.fetchall()
        c.commit()
        # Build a list of the column names
        cn = []
        for col in s.description:
            cn.append(col[0].upper())
        connect_cursor_close(dbo, c, s)
        return (d, cn)
    except Exception as err:
        al.error(str(err), "db.query_tuple_columns", dbo, sys.exc_info())
        raise err
    finally:
        try:
            connect_cursor_close(dbo, c, s)
        except:
            pass

def execute_dbupdate(dbo, sql):
    """
    Runs an action query for a dbupdate script (sets override_lock
    to True so we don't forget)
    """
    return execute(dbo, sql, True)

def execute(dbo, sql, override_lock = False):
    """
        Runs the action query given and returns rows affected
        override_lock: if this is set to False and dbo.locked = True,
        we don't do anything. This makes it easy to lock the database
        for writes, but keep databases upto date.
    """
    if not override_lock and dbo.locked: return 0
    try:
        c, s = connect_cursor_open(dbo)
        s.execute(sql)
        rv = s.rowcount
        c.commit()
        connect_cursor_close(dbo, c, s)
        if DB_EXEC_LOG != "":
            with open(DB_EXEC_LOG.replace("{database}", dbo.database), "a") as f:
                f.write("-- %s\n%s;\n" % (nowsql(), sql))
        return rv
    except Exception as err:
        al.error(str(err), "db.execute", dbo, sys.exc_info())
        try:
            # An error can leave a connection in unusable state, 
            # rollback any attempted changes.
            c.rollback()
        except:
            pass
        raise err
    finally:
        try:
            connect_cursor_close(dbo, c, s)
        except:
            pass

def execute_many(dbo, sql, params, override_lock = False):
    """
        Runs the action query given with a list of tuples that contain
        substitution parameters. Eg:
        "INSERT INTO table (field1, field2) VALUES (%s, %s)", [ ( "val1", "val2" ), ( "val3", "val4" ) ]
        Returns rows affected
        override_lock: if this is set to False and dbo.locked = True,
        we don't do anything. This makes it easy to lock the database
        for writes, but keep databases upto date.
    """
    if not override_lock and dbo.locked: return
    try:
        c, s = connect_cursor_open(dbo)
        s.executemany(sql, params)
        rv = s.rowcount
        c.commit()
        connect_cursor_close(dbo, c, s)
        return rv
    except Exception as err:
        al.error(str(err), "db.execute_many", dbo, sys.exc_info())
        try:
            # An error can leave a connection in unusable state, 
            # rollback any attempted changes.
            c.rollback()
        except:
            pass
        raise err
    finally:
        try:
            connect_cursor_close(dbo, c, s)
        except:
            pass

def is_number(x):
    return isinstance(x, (int, float, complex))

def has_structure(dbo):
    try:
        execute(dbo, "select count(*) from animal")
        return True
    except:
        return False

def _get_id_set_asm2_primarykey(dbo, table, nextid):
    """
    Update the ASM2 primary key table.
    """
    try:
        affected = execute(dbo, "UPDATE primarykey SET NextID = %d WHERE TableName = '%s'" % (nextid, table))
        if affected == 0: 
            execute(dbo, "INSERT INTO primarykey (TableName, NextID) VALUES ('%s', %d)" % (table, nextid))
    except:
        pass

def _get_id_max(dbo, table):
    return query_int(dbo, "SELECT MAX(ID) FROM %s" % table) + 1

def _get_id_cache(dbo, table):
    cache_key = "db:%s:as:%s:tb:%s" % (dbo.database, dbo.alias, table)
    nextid = cachemem.increment(cache_key)
    if nextid is None: 
        nextid = query_int(dbo, "SELECT MAX(ID) FROM %s" % table) + 1
        cachemem.put(cache_key, nextid, 600)
    return nextid

def _get_id_postgres_seq(dbo, table):
    return query_int(dbo, "SELECT nextval('seq_%s')" % table)

def get_id(dbo, table):
    """
    Returns the next ID in sequence for a table according to a number
    of different strategies.
    max:   Do SELECT MAX(ID)+1 FROM TABLE
    cache: Use an in-memory cache to track PK values (initialised by SELECT MAX)
    pseq:  Use PostgreSQL sequences
    If the database has an ASM2 primary key table, it will be updated
        with the next pk value.
    """
    strategy = ""
    nextid = 0
    if DB_PK_STRATEGY == "max" or dbo.has_asm2_pk_table:
        nextid = _get_id_max(dbo, table)
        strategy = "max"
    elif DB_PK_STRATEGY == "cache":
        nextid = _get_id_cache(dbo, table)
        strategy = "cache"
    elif DB_PK_STRATEGY == "pseq" and dbo.dbtype == "POSTGRESQL":
        nextid = _get_id_postgres_seq(dbo, table)
        strategy = "pseq"
    else:
        raise Exception("No valid PK strategy found")
    if dbo.has_asm2_pk_table: 
        _get_id_set_asm2_primarykey(dbo, table, nextid + 1)
        strategy += " asm2pk"
    al.debug("get_id: %s -> %d (%s)" % (table, nextid, strategy), "db.get_id", dbo)
    return nextid

def get_multiple_database_info(alias):
    """
    Gets the database info for the alias from our configured map.
    """
    dbo = DatabaseInfo()
    if alias not in MULTIPLE_DATABASES_MAP:
        dbo.database = "FAIL"
        return dbo
    mapinfo = MULTIPLE_DATABASES_MAP[alias]
    dbo.alias = alias
    dbo.dbtype = mapinfo["dbtype"]
    dbo.host = mapinfo["host"]
    dbo.port = mapinfo["port"]
    dbo.username = mapinfo["username"]
    dbo.password = mapinfo["password"]
    dbo.database = mapinfo["database"]
    return dbo
  
def query_int(dbo, sql):
    r = query_tuple(dbo, sql)
    try:
        v = r[0][0]
        return int(v)
    except:
        return int(0)

def query_float(dbo, sql):
    r = query_tuple(dbo, sql)
    try:
        v = r[0][0]
        return float(v)
    except:
        return float(0)

def query_string(dbo, sql):
    r = query_tuple(dbo, sql)
    try :
        v = unescape(r[0][0])
        return encode_str(dbo, v)
    except:
        return str("")

def query_date(dbo, sql):
    r = query_tuple(dbo, sql)
    try:
        v = r[0][0]
        return v
    except:
        return None

def encode_str(dbo, v):
    """
    Returns v from a query result.
    If v is unicode, encodes it as an ascii str with XML entities
    If v is already a str, removes any non-ascii chars
    If it is any other type, returns v untouched
    """
    try:
        if v is None: 
            return v
        elif type(v) == unicode:
            v = unescape(v)
            return v.encode("ascii", "xmlcharrefreplace")
        elif type(v) == str:
            v = unescape(v)
            return v.decode("ascii", "ignore").encode("ascii", "ignore")
        else:
            return v
    except Exception as err:
        al.error(str(err), "db.encode_str", dbo, sys.exc_info())
        raise err

def split_queries(sql):
    """
    Splits semi-colon separated queries in a single
    string into a list and returns them for execution.
    """
    queries = []
    x = 0
    instr = False
    while x <= len(sql):
        q = sql[x:x+1]
        if q == "'":
            instr = not instr
        if x == len(sql):
            queries.append(sql[0:x].strip())
            break
        if q == ";" and not instr:
            queries.append(sql[0:x].strip())
            sql = sql[x+1:]
            x = 0
            continue
        x += 1
    return queries

def today():
    """ Returns today as a python date """
    return datetime.datetime.today()

def todaysql():
    """ Returns today as an SQL date """
    return dd(today())

def nowsql():
    """ Returns today as an SQL date """
    return ddt(today())

def python2db(d):
    """ Formats a python date as a date for the database """
    if d is None: return "NULL"
    return "%d-%02d-%02d" % ( d.year, d.month, d.day )

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
    elif type(s) != str and type(s) != unicode:
        return u"'%s'" % str(s)
    elif not DB_DECODE_HTML_ENTITIES:
        s = utils.encode_html(s)            # Turn any leftover unicode chars into HTML entities
        s = escape(s)                       # DB/SQL injection safe
        if sanitise_xss: s = escape_xss(s)  # XSS
        return u"'%s'" % s
    else:
        s = utils.decode_html(s)            # Turn HTML entities into unicode symbols
        s = escape(s)                       # DB/SQL Injection safe
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

def concat(dbo, items):
    """ Writes a database independent concat """
    if dbo.dbtype == "MYSQL":
        return "CONCAT(" + ",".join(items) + ")"
    elif dbo.dbtype == "POSTGRESQL" or dbo.dbtype == "SQLITE":
        return " || ".join(items)

def char_length(dbo, item):
    """ Writes a database independent char length """
    if dbo.dbtype == "MYSQL":
        return "LENGTH(%s)" % item
    elif dbo.dbtype == "POSTGRESQL":
        return "char_length(%s)" % item
    elif dbo.dbtype == "SQLITE":
        return "length(%s)" % item

def check_recordversion(dbo, table, tid, version):
    """
    Verifies that the record with ID tid in table still has
    RecordVersion = version.
    If not, returns False otherwise True
    If version is a negative number, that overrides the test and returns true (useful for unit tests
    and any other time we would want to disable optimistic locking)
    """
    if version < 0: return True
    return version == query_int(dbo, "SELECT RecordVersion FROM %s WHERE ID = %d" % (table, tid))

def escape(s):
    """ Makes a value safe for database queries
    """
    if s is None: return ""
    
    # This is historic - ASM2 switched backtick for apostrophes, so we retain
    # it for compatibility as lots of data relies on it now
    s = s.replace("'", "`")

    # Use the database driver's own value escaping technique
    # to encode backslashes/other disallowed items and mitigate 
    # SQL injection encoding attacks.
    # This is a stopgap measure as we should be using parameterised queries.
    if DB_TYPE == "POSTGRESQL": 
        s = psycopg2.extensions.adapt(s).adapted
    elif DB_TYPE == "MYSQL":
        if type(s) == str:
            s = MySQLdb.escape_string(s)
        elif type(s) == unicode:
            # Encode the string as UTF-8 for MySQL escape_string 
            # then decode it back into unicode before continuing
            s = s.encode("utf-8")
            s = MySQLdb.escape_string(s)
            s = s.decode("utf-8")
    return s

def escape_xss(s):
    """ Make a value safe from XSS attacks by encoding tag delimiters """
    return s.replace(">", "&gt;").replace("<", "&lt;")

def unescape(s):
    """ unescapes query values """
    if s is None: return ""
    s = s.replace("`", "'")
    return s

def recordversion():
    """
    Returns an integer representation of now.
    """
    d = today()
    i = d.hour * 10000
    i += d.minute * 100
    i += d.second
    return i

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
    if stampRecordVersion: l.append(("RecordVersion", di(recordversion())))
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
    if stampRecordVersion: l.append(("RecordVersion", di(recordversion())))
    return make_update_sql(table, cond, l)

def rows_to_insert_sql(table, rows, escapeCR = ""):
    """
    function that Writes an INSERT query for a list of rows (a list containing dictionaries)
    """
    l = []
    fields = []
    donefields = False
    for r in rows:
        values = []
        for k in sorted(r.iterkeys()):
            if not donefields:
                fields.append(k)
            v = r[k]
            if v is None:
                values.append("null")
            elif type(v) == unicode or type(v) == str:
                if escapeCR != "": v = v.replace("\n", escapeCR).replace("\r", "")
                values.append(ds(v))
            elif type(v) == datetime.datetime:
                values.append(ddt(v))
            else:
                values.append(di(v))
        donefields = True
        l.append("INSERT INTO %s (%s) VALUES (%s);\n" % (table, ",".join(fields), ",".join(values)))
    return l

