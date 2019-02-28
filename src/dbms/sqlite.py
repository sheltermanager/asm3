#!/usr/bin/python

from base import Database

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
   
    def connect(self):
        return sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

    def sql_greatest(self, items):
        """ SQLite does not have a GREATEST() function, MAX() should be used instead """
        return "MAX(%s)" % ",".join(items)

    def switch_param_placeholder(self, sql):
        return sql # SQLite3 driver wants ? placeholders rather than usual %s so leave as is
