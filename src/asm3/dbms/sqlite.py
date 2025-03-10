
from .base import Database
from asm3.typehints import Any, List

try:
    import sqlite3
except:
    pass

class DatabaseSQLite3(Database):
    type_shorttext = "VARCHAR(1024)"
    type_longtext = "TEXT"
    type_clob = "TEXT"
    type_datetime = "TIMESTAMP"
    type_integer = "INTEGER"
    type_float = "REAL"
   
    def connect(self) -> Any:
        return sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

    def name(self) -> str:
        """ Returns the database name. Strip the path from SQLite databases """
        n = self.database
        if n.rfind("/") != -1: n = n[n.rfind("/")+1:]
        return n.replace(".", "")
    
    def sql_age(self, date1: str, date2: str) -> str:
        """ Writes an age diff function, date1 should be later than date2 """
        return f"julianday({date1}) - julianday({date2}) || ' days'"

    def sql_atoi(self, fieldexpr: str) -> str:
        """ Removes all but the numbers from fieldexpr 
            SQLite does not have regexp_replace, but since this call is primarily used for phone number
            comparisons, just strip spaces and remove the following symbols: - ( )
        """
        return "REPLACE(REPLACE(REPLACE(REPLACE(%s, '-', ''), '(', ''), ')', ''), ' ', '')" % fieldexpr
    
    def sql_datediff(self, date1: str, date2: str) -> str:
        """
        Returns an expression that calculates the difference between two dates in days.
        date1 should be > date2
        """
        return f"julianday({date1}) - julianday({date2})"
    
    def sql_datetochar(self, fieldexpr: str, formatstr: str) -> str:
        """ Writes an expression that formats a date, valid format tokens YYYY MM DD HH NN SS """
        formatstr = formatstr.replace("YYYY", "%Y")
        formatstr = formatstr.replace("MM", "%m")
        formatstr = formatstr.replace("DD", "%d")
        formatstr = formatstr.replace("HH", "%H")
        formatstr = formatstr.replace("NN", "%M")
        formatstr = formatstr.replace("SS", "%S")
        return f"strftime('{formatstr}', {fieldexpr})"

    def sql_datexhour(self, dateexpr: str) -> str:
        """
        Returns an expression that extracts the hour from a datetime.
        """
        return f"strftime('%H', {dateexpr})"

    def sql_datexminute(self, dateexpr: str) -> str:
        """
        Returns an expression that extracts the minute from a datetime.
        """
        return f"strftime('%M', {dateexpr})"
    
    def sql_datexday(self, dateexpr: str) -> str:
        """
        Returns an expression that extracts the day from a date.
        """
        return f"strftime('%d', {dateexpr})"

    def sql_datexmonth(self, dateexpr: str) -> str:
        """
        Returns an expression that extracts the month from a date.
        """
        return f"strftime('%m', {dateexpr})"

    def sql_datexyear(self, dateexpr: str) -> str:
        """
        Returns an expression that extracts the year from a date.
        """
        return f"strftime('%Y', {dateexpr})"
    
    def sql_datexweekday(self, dateexpr: str) -> str:
        """
        Returns an expression that extracts the week day from a date.
        """
        return f"strftime('%w', {dateexpr})"

    def sql_greatest(self, items: List[str]) -> str:
        """ SQLite does not have a GREATEST() function, MAX() should be used instead """
        return "MAX(%s)" % ",".join(items)

    def sql_interval(self, columnname: str, number: int, sign: str = "+", units: str = "months") -> str:
        """
        Used to add or a subtract a period to/from a date columndef  
        SQLite does not support INTERVAL and uses its own built in datetime() function.
        """
        return f"datetime({columnname}, '{sign}{number} {units}')"
    
    def sql_md5(self, s: str) -> str:
        """ 
        Writes an MD5 function for expression s
        SQLite does not support MD5, so we use hex() instead. It should still work as long as
        the values you put into it were unique (same as a hash), it's just not secure or 
        unpredictable any more but given that SQLite is really intended for dev more than
        anything it should not matter.
        """
        print("WARNING: SQLite does not have MD5() function, hex() is not secure but will work")
        return "hex(%s)" % s

    def sql_regexp_replace(self, fieldexpr: str, pattern: str = "?", replacestr: str = "?") -> str:
        """ SQLite does not have a regexp replace function. Do nothing but at least warn the user. """
        print("WARNING: SQLite cannot regexp_replace('%s', '%s', '%s')"% (fieldexpr, pattern, replacestr))
        return fieldexpr

    def switch_param_placeholder(self, sql: str) -> str:
        return sql # SQLite3 driver wants ? placeholders rather than usual %s so leave as is

    def vacuum(self, tablename: str = "") -> None:
        self.execute("VACUUM") # sqlite3 vacuum does the whole file and cannot accept a table argument

