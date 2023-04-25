#!/usr/bin/env python3

""" 
    Checks all the queries in a report file.  
    Uses the scheme as the SQL checker in reports.py

    Will only execute queries for reports of db type Any or SQLite and
    skip MYSQL/PostgreSQL specific queries.

    If you run this command with environment variable SHOWNONEXEC=1 
    then it will show the queries it can't execute so they can be copied
    and pasted into a database console or SQL interface.


"""

import os, sys, re
import web

web.config.debug = False
db = web.database( dbn = "sqlite", db = "../scripts/schema/schema.db" )

def check(sql, showonly=False):
    COMMON_DATE_TOKENS = ( "$CURRENT_DATE", "$@from", "$@to", "$@thedate" )
    # Clean up and substitute some tags
    sql = sql.replace("$USER$", "dummy")
    # Subtitute CONST tokens
    for name, value in re.findall(r"\$CONST (.+?)\=(.+?)\$", sql):
        sql = sql.replace("$%s$" % name, value) # replace all tokens with the constant value
        sql = sql.replace("$CONST %s=%s$" % (name, value), "") # remove the constant declaration
    i = sql.find("$")
    while (i != -1):
        end = sql.find("$", i+1)
        if end == -1:
            print(f"\nERROR: Unclosed $ token found at position {i}")
            break
        token = sql[i:end]
        sub = ""
        if token.startswith("$VAR"):
            # VAR tags don't need a substitution
            sub = ""
        elif token.startswith("$ASK DATE") or token in COMMON_DATE_TOKENS:
            sub = "2001-01-01"
        else:
            sub = "0"
        sql = sql[0:i] + sub + sql[end+1:]
        i = sql.find("$", i+1)
    sql = sql.strip()
    try:
        if not showonly:
            db.query(sql)
        else:
            print(sql)
    except Exception as err:
        print(f"\nQUERY FAILED: {err}\n")
        print(sql)

def parse_reports(data):
    reports = data.split("&&&")
    for rep in reports:
        b = rep.split("###")
        name = b[0].strip()
        category = b[1].strip()
        dbinfo = b[2].strip()
        desc = b[3].strip()
        locale = b[4].strip()
        sql = b[5].strip()
        html = b[6].strip()
        subreports = ""
        if len(b) > 7: subreports = b[7].strip()
        print(f"-------- {category}/{name} [{dbinfo}]")
        if len(sql) <= 3:
            print("         [ skip old ASM2 built-in ]")
        elif dbinfo.find("Any") != -1 or dbinfo.find("SQLite") != -1:
            check(sql)
        else:
            if "SHOWNONEXEC" in os.environ and os.environ["SHOWNONEXEC"]:
                print(f"Cannot execute query for {dbinfo}, copy and paste query below:\n")
                check(sql, True) 
            else:
                print("         [ skip non-SQLite query ]")

for f in sys.argv:
    if not f.endswith("check.py") and os.path.exists(f):
        print(f"==== {f}")
        with open(f, "r") as h:
            parse_reports(h.read())


