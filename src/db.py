#!/usr/bin/python

import al
import audit
import cachemem
import datetime
import i18n
import sys
import time
import utils
from sitedefs import DB_TYPE, DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD, DB_NAME, DB_HAS_ASM2_PK_TABLE, DB_DECODE_HTML_ENTITIES, DB_EXEC_LOG, DB_EXPLAIN_QUERIES, DB_TIME_QUERIES, DB_TIME_LOG_OVER, DB_TIMEOUT, CACHE_COMMON_QUERIES, MULTIPLE_DATABASES_MAP

try:
    import sqlite3
except:
    pass

try:
    import psycopg2
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
except:
    pass

try:
    import MySQLdb
except:
    pass

class Database(object):
    """
    Object that handles all interactions with the database.
    sitedefs.py supplies the default database connection info.
    This is the base class for all RDBMS provider specific functionality.
    """
    dbtype = DB_TYPE 
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

    type_shorttext = "VARCHAR(1024)"
    type_longtext = "TEXT"
    type_clob = "TEXT"
    type_datetime = "TIMESTAMP"
    type_integer = "INTEGER"
    type_float = "REAL"

    def connect(self):
        """ Virtual: Connect to the database and return the connection """
        pass

    def cursor_open(self):
        """ Returns a tuple containing an open connection and cursor.
            If the dbo object contains an active connection, we'll just use
            that to get a cursor to save time.
        """
        if self.connection is not None:
            c = self.connection
            s = self.connection.cursor()
        else:
            c = self.connect()
            s = c.cursor()
        return c, s

    def cursor_close(self, c, s):
        """ Closes a connection and cursor pair. If self.connection exists, then
            c must be it, so don't close it. Connection caching in this object
            is done by processes called via cron.py as they do not use pooling.
        """
        try:
            s.close()
        except:
            pass
        if self.connection is None:
            try:
                c.close()
            except:
                pass

    def ddl_add_column(self, table, column, coltype):
        return "ALTER TABLE %s ADD %s %s" % (table, column, coltype)

    def ddl_add_index(self, name, table, column, unique = False, partial = False):
        u = ""
        if unique: u = "UNIQUE "
        return "CREATE %sINDEX %s ON %s (%s)" % (u, name, table, column)

    def ddl_add_sequence(self, table, startat):
        return "" # Not all RDBMSes support sequences so don't do anything by default

    def ddl_add_table(self, name, fieldblock):
        return "CREATE TABLE %s (%s)" % (name, fieldblock)

    def ddl_add_table_column(self, name, coltype, nullable = True, pk = False):
        nullstr = "NOT NULL"
        if nullable: nullstr = "NULL"
        pkstr = ""
        if pk: pkstr = " PRIMARY KEY"
        return "%s %s %s%s" % ( name, coltype, nullstr, pkstr )

    def ddl_add_view(self, name, sql):
        return "CREATE VIEW %s AS %s" % (name, sql)

    def ddl_drop_column(self, table, column):
        return "ALTER TABLE %s DROP COLUMN %s" % (table, column)

    def ddl_drop_index(self, name, table):
        return "DROP INDEX %s" % name

    def ddl_drop_sequence(self, table):
        return "" # Not all RDBMSes support sequences so don't do anything by default

    def ddl_drop_view(self, name):
        return "DROP VIEW IF EXISTS %s" % name

    def ddl_modify_column(self, table, column, newtype, using = ""):
        return "" # Not all providers support this

    def encode_str_before_write(self, values):
        """ Fix and encode/decode any string values before storing them in the database.
            string column names with an asterisk will not do XSS escaping.
        """
        for k, v in values.copy().iteritems(): # Work from a copy to prevent iterator problems
            if utils.is_str(v) or utils.is_unicode(v):
                if not DB_DECODE_HTML_ENTITIES:         # Store HTML entities as is
                    v = utils.encode_html(v)            # Turn any unicode chars into HTML entities
                else:
                    v = utils.decode_html(v)            # Turn HTML entities into unicode chars
                if k.find("*") != -1:
                    # If there's an asterisk in the name, remove it so that the
                    # value is stored again below, but without XSS escaping
                    del values[k]
                    k = k.replace("*", "")
                else:
                    # Otherwise, do XSS escaping
                    v = v.replace(">", "&gt;").replace("<", "&lt;")
                values[k] = u"%s" % v
        return values

    def encode_str_after_read(self, v):
        """
        Encodes any string values returned by a query result.
        If v is unicode, encodes it as an ascii str with HTML entities
        If v is already a str, removes any non-ascii chars
        If it is any other type, returns v untouched
        """
        try:
            if v is None: 
                return v
            elif utils.is_unicode(v):
                v = self.unescape(v)
                return v.encode("ascii", "xmlcharrefreplace")
            elif utils.is_str(v):
                v = self.unescape(v)
                return v.decode("ascii", "ignore").encode("ascii", "ignore")
            else:
                return v
        except Exception as err:
            al.error(str(err), "Database.encode_str_after_read", self, sys.exc_info())
            raise err

    def escape(self, s):
        """ Makes a string value safe for database queries
        """
        if s is None: return ""
        # This is historic - ASM2 switched backticks for apostrophes so we do for compatibility
        s = s.replace("'", "`")
        return s

    def execute(self, sql, params=None, override_lock=False):
        """
            Runs the action query given and returns rows affected
            override_lock: if this is set to False and dbo.locked = True,
            we don't do anything. This makes it easy to lock the database
            for writes, but keep databases upto date.
        """
        if not override_lock and self.locked: return 0
        if sql is None or sql.strip() == "": return 0
        try:
            c, s = self.cursor_open()
            if params:
                sql = self.switch_param_placeholder(sql)
                s.execute(sql, params)
            else:
                s.execute(sql)
            rv = s.rowcount
            c.commit()
            self.cursor_close(c, s)
            if DB_EXEC_LOG != "":
                with open(DB_EXEC_LOG.replace("{database}", self.database), "a") as f:
                    f.write("-- %s\n%s;\n" % (nowsql(), sql))
            return rv
        except Exception as err:
            al.error(str(err), "Database.execute", self, sys.exc_info())
            al.error("failing sql: %s" % sql, "Database.execute", self)
            try:
                # An error can leave a connection in unusable state, 
                # rollback any attempted changes.
                c.rollback()
            except:
                pass
            raise err
        finally:
            try:
                self.cursor_close(c, s)
            except:
                pass

    def execute_dbupdate(self, sql, params=None):
        """
        Runs an action query for a dbupdate script (sets override_lock
        to True so we don't forget)
        """
        return self.execute(sql, params=params, override_lock=True)

    def execute_many(self, sql, params=(), override_lock=False):
        """
            Runs the action query given with a list of tuples that contain
            substitution parameters. Eg:
            "INSERT INTO table (field1, field2) VALUES (%s, %s)", [ ( "val1", "val2" ), ( "val3", "val4" ) ]
            Returns rows affected
            override_lock: if this is set to False and dbo.locked = True,
            we don't do anything. This makes it easy to lock the database
            for writes, but keep databases upto date.
        """
        if not override_lock and self.locked: return
        if sql is None or sql.strip() == "": return 0
        try:
            c, s = self.cursor_open()
            sql = self.switch_param_placeholder(sql)
            s.executemany(sql, params)
            rv = s.rowcount
            c.commit()
            self.cursor_close(c, s)
            return rv
        except Exception as err:
            al.error(str(err), "Database.execute_many", self, sys.exc_info())
            al.error("failing sql: %s" % sql, "Database.execute_many", self)
            try:
                # An error can leave a connection in unusable state, 
                # rollback any attempted changes.
                c.rollback()
            except:
                pass
            raise err
        finally:
            try:
                self.cursor_close(c, s)
            except:
                pass

    def get_id(self, table):
        """ Returns the next ID for a table """
        nextid = self.get_id_max(table)
        self.update_asm2_primarykey(table, nextid)
        al.debug("get_id: %s -> %d (max)" % (table, nextid), "Database.get_id", self)
        return nextid

    def get_id_max(self, table):
        """ Returns the next ID for a table using MAX(ID) """
        return query_int(self, "SELECT MAX(ID) FROM %s" % table) + 1

    def get_recordversion(self):
        """
        Returns an integer representation of now for use in the RecordVersion
        column for optimistic locks.
        """
        d = today()
        i = d.hour * 10000
        i += d.minute * 100
        i += d.second
        return i

    def has_structure(self):
        """ Returns True if the current DB has an animal table """
        try:
            self.execute("select count(*) from animal")
            return True
        except:
            return False

    def insert(self, table, values, user="", generateID=True, setRecordVersion=True, writeAudit=True):
        """ Inserts a row into a table.
            table: The table to insert into
            values: A dict of column names with values
            user: The user account performing the insert. If set, adds CreatedBy/Date/LastChangedBy/Date fields
            generateID: If True, sets a value for the ID column
            setRecordVersion: If user is non-blank and this is True, sets RecordVersion
            writeAudit: If True, writes an audit record for the insert
            Returns the ID of the inserted record
        """
        if user != "":
            values["CreatedBy"] = user
            values["LastChangedBy"] = user
            values["CreatedDate"] = self.now()
            values["LastChangedDate"] = self.now()
            if setRecordVersion: values["RecordVersion"] = self.get_recordversion()
        iid = 0
        if generateID:
            iid = self.get_id(table)
        values = self.encode_str_before_write(values)
        sql = "INSERT INTO %s (%s) VALUES (%s)" % ( table, ",".join(values.iterkeys()), ",".join('?'*len(values)) )
        self.execute(sql, values.values())
        if writeAudit and iid != 0:
            audit.create(self, user, table, iid, audit.dump_row(self, table, iid))
        return iid

    def update(self, table, iid, values, user="", setRecordVersion=True, writeAudit=True):
        """ Updates a row in a table.
            table: The table to update
            iid: The value of the ID column in the row to update
            values: A dict of column names with values
            user: The user account performing the update. If set, adds CreatedBy/Date/LastChangedBy/Date fields
            setRecordVersion: If user is non-blank and this is True, sets RecordVersion
            writeAudit: If True, writes an audit record for the update
        """
        if user != "":
            values["CreatedBy"] = user
            values["LastChangedBy"] = user
            values["CreatedDate"] = self.now()
            values["LastChangedDate"] = self.now()
            if setRecordVersion: values["RecordVersion"] = self.get_recordversion()
        values = self.encode_str_before_write(values)
        sql = "UPDATE %s SET %s WHERE ID = %s" % ( table, ",".join( ["%s=?" % x for x in values.iterkeys()] ), iid )
        preaudit = self.query_row(table, iid)
        self.execute(sql, values.values())
        postaudit = self.query_row(table, iid)
        if user != "" and writeAudit: 
            audit.edit(self, user, table, iid, audit.map_diff(preaudit, postaudit))

    def delete(self, table, iid, user="", writeAudit=True):
        """ Deletes row ID=iid from table 
            table: The table to delete from
            iid: The value of the ID column in the row to delete
            user: The user account doing the delete
            writeAudit: If True, writes an audit record for the delete
        """
        self.execute("DELETE FROM %s WHERE ID=%s" % (table, iid))
        if writeAudit and user != "":
            audit.delete(self, user, table, iid, audit.dump_row(self, table, iid))

    def install_stored_procedures(self):
        """ Install any supporting stored procedures (typically for reports) needed for this backend """
        pass

    def now(self):
        return i18n.now(self.timezone)

    def optimistic_check(self, table, tid, version):
        """ Verifies that the record with ID tid in table still has
        RecordVersion = version.
        If not, returns False otherwise True
        If version is a negative number, that overrides the test and returns true (useful for unit tests
        and any other time we would want to disable optimistic locking)
        """
        if version < 0: return True
        return version == self.query_int("SELECT RecordVersion FROM %s WHERE ID = %d" % (table, tid))

    def query(self, sql, params=None, limit=0):
        """ Runs the query given and returns the resultset as a list of dictionaries. 
            All fieldnames are uppercased when returned.
            params: tuple of parameters for the query
            limit: limit results to X rows
        """
        try:
            c, s = self.cursor_open()
            # Add limit clause if set
            if limit > 0:
                sql = "%s %s" % (sql, self.sql_limit(limit))
            # Explain the query if the option is on
            if DB_EXPLAIN_QUERIES:
                esql = "EXPLAIN %s" % sql
                al.debug(esql, "Database.query", self)
                al.debug(self.query_explain(esql), "Database.query", self)
            # Record start time
            start = time.time()
            # Run the query and retrieve all rows
            if params:
                sql = self.switch_param_placeholder(sql)
                s.execute(sql, params)
            else:
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
                    v = self.encode_str_after_read(row[i])
                    rowmap[cols[i]] = v
                l.append(rowmap)
            self.cursor_close(c, s)
            if DB_TIME_QUERIES:
                tt = time.time() - start
                if tt > DB_TIME_LOG_OVER:
                    al.debug("(%0.2f sec) %s" % (tt, sql), "Database.query", self)
            return l
        except Exception as err:
            al.error(str(err), "Database.query", self, sys.exc_info())
            al.error("failing sql: %s" % sql, "Database.query", self)
            raise err
        finally:
            try:
                self.cursor_close(c, s)
            except:
                pass

    def query_cache(self, sql, params=None, age=60, limit=0):
        """
        Runs the query given and caches the result
        for age seconds. If there's already a valid cached
        entry for the query, returns the cached result
        instead.
        If CACHE_COMMON_QUERIES is set to false, just runs the query
        without doing any caching and is equivalent to Database.query()
        """
        if not CACHE_COMMON_QUERIES: return self.query(sql, params=params, limit=limit)
        cache_key = utils.md5_hash("%s:%s:%s" % (self.alias, self.database, sql.replace(" ", "_")))
        results = cachemem.get(cache_key)
        if results is not None:
            return results
        results = self.query(sql, params=params, limit=limit)
        cachemem.put(cache_key, results, age)
        return results

    def query_columns(self, sql, params=None):
        """
            Runs the query given and returns the column names as
            a list in the order they appeared in the query
        """
        try:
            c, s = self.cursor_open()
            # Run the query and retrieve all rows
            if params:
                sql = self.switch_param_placeholder(sql)
                s.execute(sql, params)
            else:
                s.execute(sql)
            c.commit()
            # Build a list of the column names
            cn = []
            for col in s.description:
                cn.append(col[0].upper())
            self.cursor_close(c, s)
            return cn
        except Exception as err:
            al.error(str(err), "Database.query_columns", self, sys.exc_info())
            al.error("failing sql: %s" % sql, "Database.query_columns", self)
            raise err
        finally:
            try:
                self.cursor_close(c, s)
            except:
                pass

    def query_explain(self, sql, params=None):
        """
        Runs an EXPLAIN query
        """
        if not sql.lower().startswith("EXPLAIN "):
            sql = "EXPLAIN %s" % sql
        rows = self.query_tuple(sql, params=params)
        o = []
        for r in rows:
            o.append(r[0])
        return "\n".join(o)

    def query_generator(self, sql, params=None):
        """ Runs the query given and returns the resultset as a list of dictionaries. 
            All fieldnames are uppercased when returned. 
            generator function version that uses a forward cursor.
        """
        try:
            c, s = self.cursor_open()
            # Run the query and retrieve all rows
            if params:
                sql = self.switch_param_placeholder(sql)
                s.execute(sql, params)
            else:
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
                    v = self.encode_str_after_read(row[i])
                    rowmap[cols[i]] = v
                yield rowmap
                row = s.fetchone()
            self.cursor_close(c, s)
        except Exception as err:
            al.error(str(err), "Database.query_generator", self, sys.exc_info())
            al.error("failing sql: %s" % sql, "Database.query_generator", self)
            raise err
        finally:
            try:
                self.cursor_close(c, s)
            except:
                pass

    def query_row(self, table, iid):
        """ Returns the complete table row with ID=iid """
        return self.query("SELECT * FROM %s WHERE ID=%s" % (table, iid))

    def query_to_insert_sql(self, sql, table, escapeCR = ""):
        """
        Generator function that Writes an INSERT query for the list of rows 
        returned by running sql (a list containing dictionaries)
        escapeCR: Turn line feed chars into this character
        """
        fields = []
        donefields = False
        for r in self.query_generator(sql):
            values = []
            for k in sorted(r.iterkeys()):
                if not donefields:
                    fields.append(k)
                v = r[k]
                if v is None:
                    values.append("null")
                elif utils.is_unicode(v) or utils.is_str(v):
                    if escapeCR != "": v = v.replace("\n", escapeCR).replace("\r", "")
                    values.append(ds(v))
                elif type(v) == datetime.datetime:
                    values.append(ddt(v))
                else:
                    values.append(di(v))
            donefields = True
            yield "INSERT INTO %s (%s) VALUES (%s);\n" % (table, ",".join(fields), ",".join(values))

    def query_tuple(self, sql, params=None):
        """ Runs the query given and returns the resultset
            as a tuple of tuples.
        """
        try:
            c, s = self.cursor_open()
            # Run the query and retrieve all rows
            if params:
                sql = self.switch_param_placeholder(sql)
                s.execute(sql, params)
            else:
                s.execute(sql)
            d = s.fetchall()
            c.commit()
            self.cursor_close(c, s)
            return d
        except Exception as err:
            al.error(str(err), "Database.query_tuple", self, sys.exc_info())
            al.error("failing sql: %s" % sql, "Database.query_tuple", self)
            raise err
        finally:
            try:
                self.cursor_close(c, s)
            except:
                pass

    def query_tuple_columns(self, sql, params=None):
        """ Runs the query given and returns the resultset
            as a grid of tuples and a list of columnames
        """
        try:
            c, s = self.cursor_open()
            # Run the query and retrieve all rows
            if params: 
                sql = self.switch_param_placeholder(sql)
                s.execute(sql, params)
            else:
                s.execute(sql)
            d = s.fetchall()
            c.commit()
            # Build a list of the column names
            cn = []
            for col in s.description:
                cn.append(col[0].upper())
            self.cursor_close(c, s)
            return (d, cn)
        except Exception as err:
            al.error(str(err), "Database.query_tuple_columns", self, sys.exc_info())
            al.error("failing sql: %s" % sql, "Database.query_tuple_columns", self)
            raise err
        finally:
            try:
                self.cursor_close(c, s)
            except:
                pass

    def query_int(self, sql, params=None):
        """ Runs a query and returns the first item from the first column as an integer """
        r = self.query_tuple(sql, params=params)
        try:
            v = r[0][0]
            return int(v)
        except:
            return int(0)

    def query_float(self, sql, params=None):
        """ Runs a query and returns the first item from the first column as a float """
        r = self.query_tuple(sql, params=params)
        try:
            v = r[0][0]
            return float(v)
        except:
            return float(0)

    def query_string(self, sql, params=None):
        """ Runs a query and returns the first item from the first column as a string """
        r = self.query_tuple(sql, params=params)
        try:
            v = self.unescape(r[0][0])
            return self.encode_str_after_read(v)
        except:
            return str("")

    def query_date(self, sql, params=None):
        """ Runs a query and returns the first item from the first column as a date """
        r = self.query_tuple(sql, params=params)
        try:
            v = r[0][0]
            return v
        except:
            return None

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

    def sql_char_length(self, item):
        """ Writes a database independent char length """
        return "LENGTH(%s)" % item

    def sql_concat(self, items):
        """ Writes concat for a list of items """
        return " || ".join(items)

    def sql_limit(self, x):
        """ Writes a limit clause to X items """
        return "LIMIT %s" % x

    def switch_param_placeholder(self, sql):
        """ Swaps the ? token in the sql for the usual Python DBAPI placeholder of %s 
            override if your DB driver wants another char.
        """
        return sql.replace("?", "%s")

    def unescape(self, s):
        """ unescapes query values """
        if s is None: return ""
        s = s.replace("`", "'")
        return s

    def update_asm2_primarykey(self, table, nextid):
        """
        Update the ASM2 primary key table.
        """
        if not self.has_asm2_pk_table: return
        try:
            execute(self, "DELETE FROM primarykey WHERE TableName = '%s'" % table)
            execute(self, "INSERT INTO primarykey (TableName, NextID) VALUES ('%s', %d)" % (table, nextid))
        except:
            pass

    def __repr__(self):
        return "Database->locale=%s:dbtype=%s:host=%s:port=%d:db=%s:user=%s:timeout=%s" % ( self.locale, self.dbtype, self.host, self.port, self.database, self.username, self.timeout )

class DatabaseHSQLDB(Database):
    type_shorttext = "VARCHAR(1024)"
    type_longtext = "VARCHAR(2000000)"
    type_clob = "VARCHAR(2000000)"
    type_datetime = "TIMESTAMP"
    type_integer = "INTEGER"
    type_float = "DOUBLE"
   
    def connect(self):
        # We can't connect to HSQL databases from Python. This class exists
        # for dumping data in HSQLDB format.
        pass

    def ddl_add_table(self, name, fieldblock):
        return "DROP TABLE %s IF EXISTS;\nCREATE MEMORY TABLE %s (%s)" % (name, name, fieldblock)

    def ddl_add_table_column(self, name, coltype, nullable = True, pk = False):
        nullstr = "NOT NULL"
        if nullable: nullstr = "NULL"
        pkstr = ""
        if pk: pkstr = " PRIMARY KEY"
        name = name.upper()
        return "%s %s %s%s" % ( name, coltype, nullstr, pkstr )

class DatabaseMySQL(Database):
    type_shorttext = "VARCHAR(255)" # This is a fudge due to indexing problems above 767 chars on multi-byte sets
    type_longtext = "LONGTEXT"
    type_clob = "LONGTEXT"
    type_datetime = "DATETIME"
    type_integer = "INTEGER"
    type_float = "DOUBLE"

    def connect(self):
        if self.password != "":
            return MySQLdb.connect(host=self.host, port=self.port, user=self.username, passwd=self.password, db=self.database, charset="utf8", use_unicode=True)
        else:
            return MySQLdb.connect(host=self.host, port=self.port, user=self.username, db=self.database, charset="utf8", use_unicode=True)

    def cursor_open(self):
        """ Overridden to apply timeout """
        c, s = Database.cursor_open(self)
        if self.timeout > 0: 
            s.execute("SET SESSION max_execution_time=%d" % self.timeout)
        return c, s

    def ddl_add_index(self, name, table, column, unique = False, partial = False):
        u = ""
        if unique: u = "UNIQUE "
        if partial: column = "%s(255)" % column
        return "CREATE %sINDEX %s ON %s (%s)" % (u, name, table, column)

    def ddl_drop_index(self, name, table):
        return "DROP INDEX %s ON %s" % (name, table)

    def ddl_modify_column(self, table, column, newtype, using = ""):
        return "ALTER TABLE %s MODIFY %s %s" % (table, column, newtype)

    def escape(self, s):
        """ Makes a string value safe for database queries
        """
        if s is None: return ""
        if utils.is_str(s):
            s = MySQLdb.escape_string(s)
        elif utils.is_unicode(s):
            # Encode the string as UTF-8 for MySQL escape_string 
            # then decode it back into unicode before continuing
            s = s.encode("utf-8")
            s = MySQLdb.escape_string(s)
            s = s.decode("utf-8")
        return s

    def sql_concat(self, items):
        """ Writes concat for a list of items """
        return "CONCAT(" + ",".join(items) + ")"

class DatabasePostgreSQL(Database):
    type_shorttext = "VARCHAR(1024)"
    type_longtext = "TEXT"
    type_clob = "TEXT"
    type_datetime = "TIMESTAMP"
    type_integer = "INTEGER"
    type_float = "REAL"
    
    def connect(self):
        c = psycopg2.connect(host=self.host, port=self.port, user=self.username, password=self.password, database=self.database)
        c.set_client_encoding("UTF8")
        return c

    def cursor_open(self):
        """ Overridden to apply timeout """
        c, s = Database.cursor_open(self)
        if self.timeout > 0:
            s.execute("SET statement_timeout=%d" % self.timeout)
        return c, s

    def ddl_add_index(self, name, table, column, unique = False, partial = False):
        u = ""
        if unique: u = "UNIQUE "
        if partial: column = "left(%s,255)" % column
        return "CREATE %sINDEX %s ON %s (%s)" % (u, name, table, column)

    def ddl_add_sequence(self, table, startat):
        return "CREATE SEQUENCE seq_%s START %s" % (table, startat)

    def ddl_drop_column(self, table, column):
        return "ALTER TABLE %s DROP COLUMN %s CASCADE" % (table, column)

    def ddl_drop_sequence(self, table):
        return "DROP SEQUENCE IF EXISTS seq_%s" % table

    def ddl_modify_column(self, table, column, newtype, using = ""):
        if using != "": using = " USING %s" % using # if cast is required to change type, eg: (colname::integer)
        return "ALTER TABLE %s ALTER %s TYPE %s%s" % (table, column, newtype, using)

    def escape(self, s):
        """ Makes a string value safe for database queries
        """
        if s is None: return ""
        s = s.replace("'", "`")
        s = psycopg2.extensions.adapt(s).adapted
        return s

    def get_id(self, table):
        """ Returns the next ID for a table using Postgres sequences
        """
        nextid = query_int(self, "SELECT nextval('seq_%s')" % table)
        self.update_asm2_primarykey(table, nextid)
        al.debug("get_id: %s -> %d (sequence)" % (table, nextid), "DatabasePostgreSQL.get_id", self)
        return nextid

    def install_stored_procedures(self):
        """ Extra PG report procedures to cast a value to date and integer while ignoring errors """
        execute_dbupdate(self, \
            "CREATE OR REPLACE FUNCTION asm_to_date(p_date TEXT, p_format TEXT, OUT r_date DATE)\n" \
            "LANGUAGE plpgsql\n" \
            "AS $$\n" \
            "BEGIN\n" \
            "r_date = TO_DATE(p_date, p_format);\n" \
            "EXCEPTION\n" \
            "WHEN OTHERS THEN r_date = NULL;\n" \
            "END;\n" \
            "$$")
        execute_dbupdate(self, \
            "CREATE OR REPLACE FUNCTION asm_to_integer(p_int TEXT, OUT r_int INTEGER)\n" \
            "LANGUAGE plpgsql\n" \
            "AS $$\n" \
            "BEGIN\n" \
            "r_int = p_int::integer;\n" \
            "EXCEPTION\n" \
            "WHEN OTHERS THEN r_int = 0;\n" \
            "END;\n" \
            "$$")

    def sql_char_length(self, item):
        """ Writes a char length """
        return "char_length(%s)" % item

class DatabaseSQLite3(Database):
    type_shorttext = "VARCHAR(1024)"
    type_longtext = "TEXT"
    type_clob = "TEXT"
    type_datetime = "TIMESTAMP"
    type_integer = "INTEGER"
    type_float = "REAL"
   
    def connect(self):
        return sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

def get_database(t = None):
    """ Returns a database object for the current database backend, or type t if supplied """
    m = {
        "HSQLDB": DatabaseHSQLDB,
        "MYSQL": DatabaseMySQL,
        "POSTGRESQL": DatabasePostgreSQL,
        "SQLITE": DatabaseSQLite3
    }
    if t is None: t = DB_TYPE
    return m[t]()

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

# old stuff to write out/port ---

def today():
    """ Returns today as a python date """
    return datetime.datetime.today()

def todaysql():
    """ Returns today as an SQL date """
    return dd(today())

def nowsql():
    """ Returns current time as an SQL date """
    return ddt(today())

def python2db(d):
    """ Formats a python date as a date for the database """
    if d is None: return "NULL"
    return "%d-%02d-%02d" % ( d.year, d.month, d.day )

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
            elif utils.is_unicode(v) or utils.is_str(v):
                if escapeCR != "": v = v.replace("\n", escapeCR).replace("\r", "")
                values.append(ds(v))
            elif utils.is_date(v):
                values.append(ddt(v))
            else:
                values.append(di(v))
        donefields = True
        l.append("INSERT INTO %s (%s) VALUES (%s);\n" % (table, ",".join(fields), ",".join(values)))
    return l

