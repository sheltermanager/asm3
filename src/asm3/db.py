
import asm3.dbms.hsqldb, asm3.dbms.mysql, asm3.dbms.postgresql, asm3.dbms.sqlite, asm3.dbms.db2
import asm3.smcom 

from asm3.sitedefs import DB_TYPE, MULTIPLE_DATABASES, MULTIPLE_DATABASES_MAP, MULTIPLE_DATABASES_TYPE
from asm3.typehints import Database

ERROR_VALUES = ( "FAIL", "DISABLED", "WRONGSERVER" )

def get_dbo(t: str = None) -> Database:
    """ Returns a dbo object for the current database backend, or type t if supplied """
    m = {
        "HSQLDB":       asm3.dbms.hsqldb.DatabaseHSQLDB,
        "MYSQL":        asm3.dbms.mysql.DatabaseMySQL,
        "POSTGRESQL":   asm3.dbms.postgresql.DatabasePostgreSQL,
        "SQLITE":       asm3.dbms.sqlite.DatabaseSQLite3,
        "DB2":          asm3.dbms.db2.DatabaseDB2
    }
    if t is None: t = DB_TYPE
    x = m[t]()
    x.dbtype = t
    return x

def get_database(alias: str = "") -> Database:
    """ Gets the current database connection. Requires an alias/db for multiple/smcom """
    if MULTIPLE_DATABASES:
        if MULTIPLE_DATABASES_TYPE == "smcom":
            # Is this sheltermanager.com? If so, we need to get the
            # database connection info (dbo) before we can login.
            dbo = asm3.smcom.get_database_info(alias)
        else:
            # Look up the database info from our map
            dbo  = _get_multiple_database_info(alias)
    else:
        dbo = get_dbo()
    return dbo

def _get_multiple_database_info(alias: str) -> Database:
    """ Gets the Database object for the alias in our map MULTIPLE_DATABASES_MAP. """
    if alias not in MULTIPLE_DATABASES_MAP:
        dbo = get_database()
        dbo.database = "FAIL"
        return dbo
    mapinfo = MULTIPLE_DATABASES_MAP[alias]
    dbo = get_dbo(mapinfo["dbtype"])
    dbo.alias = alias
    dbo.dbtype = mapinfo["dbtype"]
    dbo.host = mapinfo["host"]
    dbo.port = mapinfo["port"]
    dbo.username = mapinfo["username"]
    dbo.password = mapinfo["password"]
    dbo.database = mapinfo["database"]
    return dbo


