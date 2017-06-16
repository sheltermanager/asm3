#!/usr/bin/python

from base import Database

try:
    import ibm_db_dbi
except:
    pass

class DatabaseDB2(Database):
    type_shorttext = "VARCHAR(1024)" # may be 255
    type_clob = "CLOB"
    type_longtext = "VARCHAR(32K)"

    def connect(self):
        return ibm_db_dbi.connect(self.database, self.username, self.password, self.host)

    def ddl_drop_view(self, name):
        return "BEGIN DECLARE CONTINUE HANDLER FOR SQLSTATE '42704' BEGIN END; EXECUTE IMMEDIATE 'DROP VIEW %s'; END" % name

    def ddl_modify_column(self, table, column, newtype, using = ""):
        return "ALTER TABLE %s ALTER COLUMN %s SET DATA TYPE %s" % (table, column, newtype)

    def escape(self, s):
        answer = []
        for index,char in enumerate(s):
            if char in """&*@[]{}\^:=!-()%+?~|;_""":
                answer.append('\\')
            answer.append(char)
        return ''.join(answer)

    def sql_limit(self, x):
        """ Writes a limit clause to X items """
        return "FETCH FIRST %s ROWS ONLY" % x
    
    def query_explain(self, sql, params=None):
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

    def ddl_add_sequence(self, table, startat):
        return "CREATE SEQUENCE seq_%s START WITH %s" % (table, startat)

    def ddl_drop_sequence(self, table):
        return "BEGIN DECLARE CONTINUE HANDLER FOR SQLSTATE '42704' BEGIN END; EXECUTE IMMEDIATE 'DROP SEQUENCE seq_%s'; END" % table

    def get_id(self, table):
        """ Returns the next ID for a table using sequences
        """
        nextid = self.query_int("SELECT NEXT VALUE FOR seq_%s FROM %s" % (table, table))
        self.update_asm2_primarykey(table, nextid)
        return nextid
