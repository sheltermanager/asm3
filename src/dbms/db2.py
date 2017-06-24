#!/usr/bin/python
"""
   DB2 and Derby database support for Animal Shelter Manager (ASM)
   
   Notes:
    - if you install DB2/Derby on the same host, nothing further needs to be done. If you
      have you server on a different host you will need to install the Data Server Driver Package
    - when creating your database use the following command:
      create database <database> using codeset UTF-8 territory en PAGESIZE 32768 (16384)
    - DB2 will not insert data >32k using execute statements - you have to use host variables, and
      these are not supported in the Python API. This only affects the Content field in dbfs, so until
      a work around is found, you MUST store dbfs content on disk by setting set DBFS_STORE = "file"
      in sitedefs and specifying the location in DBFS_FILESTORAGE_FOLDER

"""
import al
from base import Database

try:
    import ibm_db_dbi
except:
    pass

class DatabaseDB2(Database):
    type_shorttext = "VARCHAR(1024)"
    type_longtext = "VARCHAR(32000)"
    type_clob = "CLOB"
    type_datetime = "TIMESTAMP"
    type_integer = "INTEGER"
    type_float = "REAL"

    def connect(self):
        return ibm_db_dbi.connect("DSN=%s; HOSTNAME=%s; PORT=%s" %(self.database, self.host, self.port), user=self.username, password=self.password)

    def ddl_add_index(self, name, table, column, unique = False, partial = False):
        u = ""
        if unique: u = "UNIQUE "
        if partial: column = "CHAR(SUBSTR(%s, 1, 255))" % column
        return "CREATE %sINDEX %s ON %s (%s)" % (u, name, table, column)

    def ddl_drop_view(self, name):
        return "BEGIN DECLARE CONTINUE HANDLER FOR SQLSTATE '42704' BEGIN END; EXECUTE IMMEDIATE 'DROP VIEW %s'; END" % name

    def ddl_modify_column(self, table, column, newtype, using = ""):
        return "ALTER TABLE %s ALTER COLUMN %s SET DATA TYPE %s" % (table, column, newtype)

    def ddl_drop_column(self, table, column):
        return "ALTER TABLE %s DROP COLUMN %s CASCADE" % (table, column)

    def escape(self, s):
        esc_chars = "\x00\x1a\\\";"
        answer = []
        for index,char in enumerate(s):
            if char in esc_chars:
                answer.append('\\')
            if char == "'":
                answer.append("'")
            answer.append(char)
        return ''.join(answer)

    def sql_limit(self, x):
        """ Writes a limit clause to X items """
        return "FETCH FIRST %s ROWS ONLY" % x
    
    def query_explain(self, sql, params=None):
        """
        Runs an EXPLAIN query
        """
        if not sql.lower().startswith("EXPLAIN ALL FOR "):
            sql = "EXPLAIN ALL FOR %s" % sql
        rows = self.query_tuple(sql, params=params)
        o = []
        for r in rows:
            o.append(r[0])
        return "\n".join(o)

    def ddl_add_sequence(self, table, startat):
        return "CREATE SEQUENCE seq_%s START WITH %s INCREMENT BY 1 NO CYCLE NO CACHE" % (table, startat)

    def ddl_drop_sequence(self, table):
        return "BEGIN DECLARE CONTINUE HANDLER FOR SQLSTATE '42704' BEGIN END; EXECUTE IMMEDIATE 'DROP SEQUENCE seq_%s'; END" % table

    def get_id(self, table):
        """ Returns the next ID for a table using sequences
        """
        nextid = self.query_int("VALUES NEXT VALUE FOR seq_%s" % table)
        al.debug("get_id: %s -> %d (sequence)" % (table, nextid), "DatabaseDB2.get_id", self)
        self.update_asm2_primarykey(table, nextid)
        return nextid
    
    def switch_param_placeholder(self, sql):
        """ DB2 likes ? so do nothing 
        """
        return sql

