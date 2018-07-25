#!/usr/bin/python

import dbms.hsqldb, dbms.mysql, dbms.postgresql, dbms.sqlite, dbms.db2

from sitedefs import DB_TYPE, MULTIPLE_DATABASES_MAP

def get_database(t = None):
    """ Returns a database object for the current database backend, or type t if supplied """
    m = {
        "HSQLDB":       dbms.hsqldb.DatabaseHSQLDB,
        "MYSQL":        dbms.mysql.DatabaseMySQL,
        "POSTGRESQL":   dbms.postgresql.DatabasePostgreSQL,
        "SQLITE":       dbms.sqlite.DatabaseSQLite3,
        "DB2":          dbms.db2.DatabaseDB2
    }
    if t is None: t = DB_TYPE
    x = m[t]()
    x.dbtype = t
    return x

def get_multiple_database_info(alias):
    """ Gets the Database object for the alias in our map MULTIPLE_DATABASES_MAP. """
    if alias not in MULTIPLE_DATABASES_MAP:
        dbo = get_database()
        dbo.database = "FAIL"
        return dbo
    mapinfo = MULTIPLE_DATABASES_MAP[alias]
    dbo = get_database(mapinfo["dbtype"])
    dbo.alias = alias
    dbo.dbtype = mapinfo["dbtype"]
    dbo.host = mapinfo["host"]
    dbo.port = mapinfo["port"]
    dbo.username = mapinfo["username"]
    dbo.password = mapinfo["password"]
    dbo.database = mapinfo["database"]
    return dbo


