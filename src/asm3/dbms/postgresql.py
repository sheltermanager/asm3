
import asm3.al
from .base import Database
from asm3.typehints import Any, Tuple

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
    
    def connect(self) -> Any:
        c = psycopg2.connect(host=self.host, port=self.port, user=self.username, password=self.password, database=self.database)
        c.set_client_encoding("UTF8")
        return c

    def cursor_open(self) -> Tuple[Any, Any]:
        """ Overridden to apply timeout """
        c, s = Database.cursor_open(self)
        if self.timeout > 0: s.execute("SET statement_timeout=%d" % self.timeout)
        return c, s

    def ddl_add_index(self, name: str, table: str, column: str, unique: bool = False, partial: bool = False) -> str:
        u = ""
        if unique: u = "UNIQUE "
        if partial: column = "left(%s,255)" % column
        return "CREATE %sINDEX %s ON %s (%s)" % (u, name, table, column)

    def ddl_add_sequence(self, table: str, startat: int) -> str:
        return "CREATE SEQUENCE seq_%s START %s" % (table, startat)

    def ddl_drop_column(self, table: str, column: str) -> str:
        return "ALTER TABLE %s DROP COLUMN %s CASCADE" % (table, column)

    def ddl_drop_notnull(self, table: str, column: str, existingtype: str) -> str:
        return "ALTER TABLE %s ALTER COLUMN %s DROP NOT NULL" % (table, column)

    def ddl_drop_sequence(self, table: str) -> str:
        return "DROP SEQUENCE IF EXISTS seq_%s" % table

    def ddl_modify_column(self, table: str, column: str, newtype: str, using: str = "") -> str:
        if using != "": using = " USING %s" % using # if cast is required to change type, eg: (colname::integer)
        return "ALTER TABLE %s ALTER %s TYPE %s%s" % (table, column, newtype, using)

    def escape(self, s: str) -> str:
        """ Makes a string value safe for database queries
        """
        if s is None: return ""
        s = s.replace("'", "`")
        s = psycopg2.extensions.adapt(s).adapted
        return s

    def get_id(self, table: str) -> int:
        """ Returns the next ID for a table using Postgres sequences
        """
        nextid = self.query_int("SELECT nextval('seq_%s')" % table)
        # No point copying the sequence to the pk table like we used to
        # self.update_primarykey(table, nextid) 
        asm3.al.debug("get_id: %s -> %d (sequence)" % (table, nextid), "DatabasePostgreSQL.get_id", self)
        return nextid

    def install_stored_procedures(self) -> None:
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
        
    def sql_age(self, date1: str, date2: str) -> str:
        """ Writes an age diff function, date1 should be later than date2 """
        return f"age({date1}, {date2})::varchar"

    def sql_cast(self, expr: str, newtype: str) -> str:
        """ Writes a database independent cast for expr to newtype """
        return "%s::%s" % (expr, newtype)

    def sql_char_length(self, item: str) -> str:
        """ Writes a char length """
        return "char_length(%s)" % item
    
    def sql_datediff(self, date1: str, date2: str) -> str:
        """
        Returns an expression that calculates the difference between two dates in days.
        date1 should be > date2
        """
        return f"EXTRACT(DAY FROM {date1} - {date2})::integer"
    
    def sql_datetochar(self, fieldexpr: str, formatstr: str) -> str:
        """ Writes an expression that formats a date, valid format tokens YYYY MM DD HH NN SS """
        return f"TO_CHAR({fieldexpr}, '{formatstr}')"
    
    def sql_datexday(self, dateexpr: str) -> str:
        """
        Returns an expression that extracts the day from a date.
        """
        return f"EXTRACT (DAY FROM {dateexpr})::integer"

    def sql_datexmonth(self, dateexpr: str) -> str:
        """
        Returns an expression that extracts the month from a date.
        """
        return f"EXTRACT (MONTH FROM {dateexpr})::integer"

    def sql_datexyear(self, dateexpr: str) -> str:
        """
        Returns an expression that extracts the year from a date.
        """
        return f"EXTRACT (YEAR FROM {dateexpr})::integer"
    
    def sql_datexweekday(self, dateexpr: str) -> str:
        """
        Returns an expression that extracts the week day from a date.
        """
        return f"TO_CHAR({dateexpr}, 'DAY')"

    def sql_ilike(self, expr1: str, expr2: str = "?") -> str:
        return "%s ILIKE %s" % (expr1, expr2)
    
    def sql_interval(self, columnname: str, number: int, sign: str = "+", units: str = "months") -> str:
        """
        Used to add or a subtract a period to/from a date column 
        """
        return f"{columnname} {sign} INTERVAL '{number} {units}'"
    
    def sql_md5(self, s: str) -> str:
        """ 
        Writes an MD5 function for expression s.
        PostgreSQL's MD5 function will only accept strings, so if there is no string literal
        component to the expression given, assume it is a column name and cast it to text
        """
        if s.find("'") == -1: s += "::text"
        return "MD5(%s)" % s

    def sql_regexp_replace(self, fieldexpr: str, pattern: str = "?", replacestr: str = "?") -> str:
        """ Writes a regexp replace expression that replaces characters matching pattern with replacestr """
        if pattern != "?": pattern = "'%s'" % pattern
        if replacestr != "?": replacestr = "'%s'" % self.escape(replacestr)
        return "REGEXP_REPLACE(%s, %s, %s, 'g')" % (fieldexpr, pattern, replacestr)

    def sql_substring(self, fieldexpr: str, pos: int, chars: int) -> str:
        """ SQL substring function from pos for chars """
        return "SUBSTRING(%s FROM %s TO %s)" % (fieldexpr, pos, chars)

    def sql_zero_pad_left(self, fieldexpr: str, digits: int) -> str:
        """ Writes a function that zero pads an expression with zeroes to digits """
        return "TO_CHAR(%s, 'FM%s')" % (fieldexpr, "0"*digits)

    def vacuum(self, tablename: str = "") -> None:
        self.execute("VACUUM %s" % tablename)

