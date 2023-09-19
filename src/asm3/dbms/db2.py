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
import asm3.al
from .base import Database
from asm3.typehints import Any, Dict

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

    def check_reorg(self) -> None:
        for row in self.query("SELECT TABNAME from SYSIBMADM.ADMINTABINFO where REORG_PENDING='Y'"):
            self.execute("CALL SYSPROC.ADMIN_CMD('REORG TABLE %s')" % (row.tabname), params=None, override_lock=True)
        return

    def connect(self) -> Any:
        return ibm_db_dbi.connect("DSN=%s; HOSTNAME=%s; PORT=%s" % (self.database, self.host, self.port), user=self.username, password=self.password)

    def ddl_add_index(self, name: str, table: str, column: str, unique: bool = False, partial: bool = False) -> str:
        u = ""
        if unique: u = "UNIQUE "
        if partial: column = "CHAR(SUBSTR(%s, 1, 255))" % column
        return "CREATE %sINDEX %s ON %s (%s)" % (u, name, table, column)

    def ddl_add_sequence(self, table: str, startat: int) -> str:
        return "CREATE SEQUENCE seq_%s START WITH %s INCREMENT BY 1 NO CYCLE NO CACHE" % (table, startat)

    def ddl_drop_view(self, name: str) -> str:
        return "BEGIN DECLARE CONTINUE HANDLER FOR SQLSTATE '42704' BEGIN END; EXECUTE IMMEDIATE 'DROP VIEW %s'; END" % name

    def ddl_drop_column(self, table: str, column: str) -> str:
        return "ALTER TABLE %s DROP COLUMN %s CASCADE" % (table, column)

    def ddl_drop_sequence(self, table: str) -> str:
        return "BEGIN DECLARE CONTINUE HANDLER FOR SQLSTATE '42704' BEGIN END; EXECUTE IMMEDIATE 'DROP SEQUENCE seq_%s'; END" % table

    def ddl_modify_column(self, table: str, column: str, newtype: str, using: str = "") -> str:
        return "ALTER TABLE %s ALTER COLUMN %s SET DATA TYPE %s" % (table, column, newtype)

    def escape(self, s: str) -> str:
        esc_chars = "\x00\x1a\\\";"
        answer = []
        for index,char in enumerate(s):
            if char in esc_chars:
                answer.append('\\')
            if char == "'":
                answer.append("'")
            answer.append(char)
        return ''.join(answer)

    def execute_dbupdate(self, sql: str, params: Dict = None) -> int:
        rv = self.execute(sql, params=params, override_lock=True)
        if rv > 0:
            self.check_reorg()
        return rv

    def get_id(self, table: str) -> int:
        """ Returns the next ID for a table using sequences
        """
        nextid = self.query_int("VALUES NEXT VALUE FOR seq_%s" % table)
        asm3.al.debug("get_id: %s -> %d (sequence)" % (table, nextid), "DatabaseDB2.get_id", self)
        self.update_asm2_primarykey(table, nextid)
        return nextid

    def query_explain(self, sql: str, params: Dict = None) -> str:
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

    def sql_cast_char(self, expr: str) -> str:
        """ Writes a database independent cast for expr to a char """
        return "CHAR(%s)" % (expr)
    
    def sql_limit(self, x: int) -> str:
        """ Writes a limit clause to X items """
        return "FETCH FIRST %s ROWS ONLY" % x

    def switch_param_placeholder(self, sql: str) -> str:
        """ DB2 likes ? so do nothing """
        return sql
