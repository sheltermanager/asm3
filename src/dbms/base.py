#!/usr/bin/python

import al
import audit
import cachemem
import datetime
import i18n
import sys
import time
import utils

from sitedefs import DB_TYPE, DB_HOST, DB_PORT, DB_USERNAME, DB_PASSWORD, DB_NAME, DB_HAS_ASM2_PK_TABLE, DB_DECODE_HTML_ENTITIES, DB_EXEC_LOG, DB_EXPLAIN_QUERIES, DB_TIME_QUERIES, DB_TIME_LOG_OVER, DB_TIMEOUT, CACHE_COMMON_QUERIES

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
            If available, dbms implementations should override this and use whatever 
            is available in the driver.
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
                    f.write("-- %s\n%s;\n" % (self.now(), sql))
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
        return self.query_int("SELECT MAX(ID) FROM %s" % table) + 1

    def get_recordversion(self):
        """
        Returns an integer representation of now for use in the RecordVersion
        column for optimistic locks.
        """
        d = self.now()
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
            values["ID"] = iid
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
        if writeAudit and user != "":
            audit.delete(self, user, table, iid, audit.dump_row(self, table, iid))
        self.execute("DELETE FROM %s WHERE ID=%s" % (table, iid))

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
        for r in self.query_generator(sql):
            yield self.row_to_insert_sql(table, r, escapeCR)

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

    def row_to_insert_sql(table, r, escapeCR = ""):
        """
        function that Writes an INSERT query for a result row
        """
        fields = []
        donefields = False
        values = []
        for k in sorted(r.iterkeys()):
            if not donefields:
                fields.append(k)
            v = r[k]
            if v is None:
                values.append("null")
            elif utils.is_unicode(v) or utils.is_str(v):
                if escapeCR != "": v = v.replace("\n", escapeCR).replace("\r", "")
                values.append("'%s'" % v)
            elif type(v) == datetime.datetime:
                values.append("'%04d-%02d-%02d %02d:%02d:%02d'" % ( v.year, v.month, v.day, v.hour, v.minute, v.second ))
            else:
                values.append(str(v))
        donefields = True
        return "INSERT INTO %s (%s) VALUES (%s);\n" % (table, ",".join(fields), ",".join(values))

    def split_queries(self, sql):
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

    def sql_date(self, d, wrapParens=True, includeTime=True):
        """ Writes a Python date in SQL form """
        if d is None: return "NULL"
        s = "%04d-%02d-%02d %02d:%02d:%02d" % ( d.year, d.month, d.day, d.hour, d.minute, d.second )
        if not includeTime:
            s = "%04d-%02d-%02d 00:00:00" % ( d.year, d.month, d.day )
        if wrapParens: return "'%s'" % s
        return s

    def sql_now(self, wrapParens=True, includeTime=True):
        """ Writes now as an SQL date """
        return self.sql_date(self.now(), wrapParens=wrapParens, includeTime=includeTime)

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
            self.execute("DELETE FROM primarykey WHERE TableName = ?", [table] )
            self.execute("INSERT INTO primarykey (TableName, NextID) VALUES (?, ?)", (table, nextid))
        except:
            pass

    def __repr__(self):
        return "Database->locale=%s:dbtype=%s:host=%s:port=%d:db=%s:user=%s:timeout=%s" % ( self.locale, self.dbtype, self.host, self.port, self.database, self.username, self.timeout )


