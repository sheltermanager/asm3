
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

    def sql_atoi(self, fieldexpr: str) -> str:
        """ Removes all but the numbers from fieldexpr 
            SQLite does not have regexp_replace, but since this call is primarily used for phone number
            comparisons, just strip spaces and remove the following symbols: - ( )
        """
        return "REPLACE(REPLACE(REPLACE(REPLACE(%s, '-', ''), '(', ''), ')', ''), ' ', '')" % fieldexpr
    
    def sql_datediff(self, startdateexpr: str, enddateexpr: str) -> str:
        """
        Returns an expression that calculates the difference between two dates in days.
        enddate should be later than start date.
        """
        return f"julianday({enddateexpr}) - julianday({startdateexpr})"
    
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

