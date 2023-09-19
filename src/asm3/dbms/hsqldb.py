
from .base import Database

class DatabaseHSQLDB(Database):
    type_shorttext = "VARCHAR(1024)"
    type_longtext = "VARCHAR(2000000)"
    type_clob = "VARCHAR(2000000)"
    type_datetime = "TIMESTAMP"
    type_integer = "INTEGER"
    type_float = "DOUBLE"
   
    def connect(self) -> None:
        # We can't connect to HSQL databases from Python. This class exists
        # for dumping data in HSQLDB format.
        pass

    def ddl_add_table(self, name: str, fieldblock: str) -> str:
        return "DROP TABLE %s IF EXISTS;\nCREATE MEMORY TABLE %s (%s)" % (name, name, fieldblock)

    def ddl_add_table_column(self, name: str, coltype: str, nullable: bool = True, pk: bool = False) -> str:
        nullstr = "NOT NULL"
        if nullable: nullstr = "NULL"
        pkstr = ""
        if pk: pkstr = " PRIMARY KEY"
        name = name.upper()
        return "%s %s %s%s" % ( name, coltype, nullstr, pkstr )

