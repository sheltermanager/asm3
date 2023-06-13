
import asm3.al
from .base import Database

try:
    import psycopg2
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
except:
    pass

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
        if self.timeout > 0: s.execute("SET LOCAL statement_timeout=%d" % self.timeout)
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

    def ddl_drop_notnull(self, table, column, existingtype):
        return "ALTER TABLE %s ALTER COLUMN %s DROP NOT NULL" % (table, column)

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
        nextid = self.query_int("SELECT nextval('seq_%s')" % table)
        self.update_asm2_primarykey(table, nextid)
        asm3.al.debug("get_id: %s -> %d (sequence)" % (table, nextid), "DatabasePostgreSQL.get_id", self)
        return nextid

    def install_stored_procedures(self):
        """ Extra PG report procedures to cast a value to date and integer while ignoring errors """
        self.execute_dbupdate(\
            "CREATE OR REPLACE FUNCTION asm_to_date(p_date TEXT, p_format TEXT, OUT r_date DATE)\n" \
            "LANGUAGE plpgsql\n" \
            "AS $$\n" \
            "BEGIN\n" \
            "r_date = TO_DATE(p_date, p_format);\n" \
            "EXCEPTION\n" \
            "WHEN OTHERS THEN r_date = NULL;\n" \
            "END;\n" \
            "$$")
        self.execute_dbupdate(\
            "CREATE OR REPLACE FUNCTION asm_to_integer(p_int TEXT, OUT r_int INTEGER)\n" \
            "LANGUAGE plpgsql\n" \
            "AS $$\n" \
            "BEGIN\n" \
            "r_int = p_int::integer;\n" \
            "EXCEPTION\n" \
            "WHEN OTHERS THEN r_int = 0;\n" \
            "END;\n" \
            "$$")
        self.execute_dbupdate(\
            "CREATE OR REPLACE FUNCTION asm_to_float(p_float TEXT, OUT r_float REAL)\n" \
            "LANGUAGE plpgsql\n" \
            "AS $$\n" \
            "BEGIN\n" \
            "r_float = p_float::real;\n" \
            "EXCEPTION\n" \
            "WHEN OTHERS THEN r_float = 0.0;\n" \
            "END;\n" \
            "$$")

    def sql_cast(self, expr, newtype):
        """ Writes a database independent cast for expr to newtype """
        return "%s::%s" % (expr, newtype)

    def sql_char_length(self, item):
        """ Writes a char length """
        return "char_length(%s)" % item

    def sql_ilike(self, expr1, expr2 = "?"):
        return "%s ILIKE %s" % (expr1, expr2)

    def sql_regexp_replace(self, fieldexpr, pattern="?", replacestr="?"):
        """ Writes a regexp replace expression that replaces characters matching pattern with replacestr """
        if pattern != "?": pattern = "'%s'" % pattern
        if replacestr != "?": replacestr = "'%s'" % self.escape(replacestr)
        return "REGEXP_REPLACE(%s, %s, %s, 'g')" % (fieldexpr, pattern, replacestr)

    def sql_substring(self, fieldexpr, pos, chars):
        """ SQL substring function from pos for chars """
        return "SUBSTRING(%s FROM %s TO %s)" % (fieldexpr, pos, chars)

    def sql_zero_pad_left(self, fieldexpr, digits):
        """ Writes a function that zero pads an expression with zeroes to digits """
        return "TO_CHAR(%s, 'FM%s')" % (fieldexpr, "0"*digits)

    def vacuum(self, tablename=""):
        self.execute("VACUUM %s" % tablename)

