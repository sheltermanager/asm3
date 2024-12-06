
import asm3.utils
from .base import Database
from asm3.typehints import Any, List, Tuple

try:
    import MySQLdb
except:
    pass

class DatabaseMySQL(Database):
    type_shorttext = "VARCHAR(255)" # This is a fudge due to indexing problems above 767 chars on multi-byte sets
    type_longtext = "LONGTEXT"
    type_clob = "LONGTEXT"
    type_datetime = "DATETIME"
    type_integer = "INTEGER"
    type_float = "DOUBLE"

    def connect(self) -> Any:
        if self.password != "":
            return MySQLdb.connect(host=self.host, port=self.port, user=self.username, passwd=self.password, db=self.database, charset="utf8", use_unicode=True)
        else:
            return MySQLdb.connect(host=self.host, port=self.port, user=self.username, db=self.database, charset="utf8", use_unicode=True)

    def cursor_open(self) -> Tuple[Any, Any]:
        """ Overridden to apply timeout """
        c, s = Database.cursor_open(self)
        if self.timeout > 0: 
            s.execute("SET SESSION max_execution_time=%d" % self.timeout)
        return c, s

    def ddl_add_index(self, name: str, table: str, column: str, unique: bool = False, partial: bool = False) -> str:
        """ Overridden to allow partial index support """
        u = ""
        if unique: u = "UNIQUE "
        if partial: column = "%s(255)" % column
        return "CREATE %sINDEX %s ON %s (%s)" % (u, name, table, column)
    
    def ddl_drop_index(self, name: str, table: str) -> str:
        return "DROP INDEX %s ON %s" % (name, table)

    def ddl_drop_notnull(self, table: str, column: str, existingtype: str) -> str:
        return "ALTER TABLE %s MODIFY %s %s NULL" % (table, column, existingtype)

    def ddl_modify_column(self, table: str, column: str, newtype: str, using: str = "") -> str:
        return "ALTER TABLE %s MODIFY %s %s" % (table, column, newtype)

    def escape(self, s: str) -> str:
        """ Makes a string value safe for database queries
        """
        if s is None: return ""
        if asm3.utils.is_str(s):
            s = MySQLdb.escape_string(s)
            s = asm3.utils.bytes2str(s) # MySQLdb.escape_string can return bytes on python3
        elif asm3.utils.is_unicode(s):
            # Encode the string as UTF-8 for MySQL escape_string 
            # then decode it back into unicode before continuing
            s = s.encode("utf-8")
            s = MySQLdb.escape_string(s)
            s = s.decode("utf-8")
        # This is historic - ASM2 switched backticks for apostrophes so we do for compatibility
        s = s.replace("'", "`")
        return s
        
    def sql_age(self, date1: str, date2: str) -> str:
        """ Writes an age diff function, date1 should be later than date2 """
        return f"CONCAT(DATEDIFF({date1}, {date2}), ' days')"

    def sql_concat(self, items: List[str]) -> str:
        """ Writes concat for a list of items """
        return "CONCAT(" + ",".join(items) + ")"

    def sql_cast_char(self, expr: str) -> str:
        """ Writes a database independent cast for expr to a char """
        return self.sql_cast(expr, "CHAR")
    
    def sql_datediff(self, date1: str, date2: str) -> str:
        """
        Returns an expression that calculates the difference between two dates in days.
        date1 should be > date2
        """
        return f"DATEDIFF({date1}, {date2})"
    
    def sql_datexday(self, dateexpr: str) -> str:
        """
        Returns an expression that extracts the day from a date.
        """
        return f"DAY({dateexpr})"

    def sql_datexmonth(self, dateexpr: str) -> str:
        """
        Returns an expression that extracts the month from a date.
        """
        return f"MONTH({dateexpr})"

    def sql_datexyear(self, dateexpr: str) -> str:
        """
        Returns an expression that extracts the year from a date.
        """
        return f"YEAR({dateexpr})"
    
    def sql_datexweekday(self, dateexpr: str) -> str:
        """
        Returns an expression that extracts the week day from a date.
        """
        return f"DAYOFWEEK({dateexpr})"
    
    def sql_interval(self, columnname: str, number: int, sign: str = "+", units: str = "months") -> str:
        """
        Used to add or a subtract a period to/from a date column 
        """
        return f"{columnname} {sign} INTERVAL {number} {units}"
    
    def sql_regexp_replace(self, fieldexpr: str, pattern: str = "?", replacestr: str = "?") -> str:
        """ Writes a regexp replace expression that replaces characters matching pattern with replacestr """
        if pattern != "?": pattern = "'%s'" % pattern
        if replacestr != "?": replacestr = "'%s'" % self.escape(replacestr)
        return "REGEXP_REPLACE(%s, %s, %s)" % (fieldexpr, pattern, replacestr)

    def sql_zero_pad_left(self, fieldexpr: str, digits: int) -> str:
        """ Writes a function that zero pads an expression with zeroes to digits """
        return "LPAD(%s, %s, '0')" % (fieldexpr, digits)

    def vacuum(self, tablename: str = "") -> None:
        self.execute("OPTIMIZE TABLE %s" % tablename)

