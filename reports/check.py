#!/usr/bin/env python3

""" 
    Checks all the queries in a report file.  
    Uses the scheme as the SQL checker in reports.py

    Will only execute queries for reports of db type Any or SQLite and
    skip MYSQL/PostgreSQL specific queries.

    environment variables that can be set prior to running:

    SHOWNONEXEC=1 - show non-SQLite queries so they can be copied/pasted
    FORCENONEXEC=1 - force running of non-SQLite queries against SQLite anyway
    EXECPOSTGRES=1 - ssh to our dev db on eur04 to execute PostgreSQL queries

"""

import os, sys, re
import web

web.config.debug = False
db = web.database( dbn = "sqlite", db = "../scripts/schema/schema.db" )

SHOWNONEXEC = "SHOWNONEXEC" in os.environ and os.environ["SHOWNONEXEC"]
FORCENONEXEC = "FORCENONEXEC" in os.environ and os.environ["FORCENONEXEC"]
EXECPOSTGRES = "EXECPOSTGRES" in os.environ and os.environ["EXECPOSTGRES"]

checked = 0
total = 0

def substitute(sql):
    COMMON_DATE_TOKENS = ( "CURRENT_DATE", "@from", "@to", "@dt", "@thedate" )
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
        token = sql[i+1:end]
        sub = ""
        if token.startswith("VAR"):
            # VAR tags don't need a substitution
            sub = ""
        elif token == "@year":
            sub = "2001"
        elif token.startswith("ASK DATE") or token.startswith("CURRENT_DATE") or token in COMMON_DATE_TOKENS:
            sub = "2001-01-01"
        else:
            sub = "0"
        sql = sql[0:i] + sub + sql[end+1:]
        i = sql.find("$", i+1)
    return sql.strip()

def parse_reports(data):
    global checked
    global total
    reports = data.split("&&&")
    for rep in reports:
        total += 1
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
        elif dbinfo.find("Any") != -1 or dbinfo.find("SQLite") != -1 or FORCENONEXEC:
            try:
                checked += 1
                db.query(substitute(sql))
            except Exception as err:
                print(f"\nQUERY FAILED: {err}\n")
                print(sql)
            if subreports:
                elem=0
                name = ""
                sql = ""
                html = ""
                for rep in subreports.split("+++"):
                    if elem == 0: name = rep.strip()
                    if elem == 1: sql = rep.strip()
                    if elem == 2: html = rep.strip()
                    elem += 1
                    if elem == 3: 
                        total += 1
                        elem = 0
                        # process subreport
                        print(f"------------ {name}")
                        try:
                            checked += 1
                            db.query(substitute(sql))
                        except Exception as err:
                            print(f"\nQUERY FAILED: {err}\n")
                            print(sql)
        elif EXECPOSTGRES and dbinfo.find("PostgreSQL") != -1:
            with open("zzz_check.sql", "w") as f:
                f.write(substitute(sql))
            checked += 1
            os.system("scp -q zzz_check.sql root@eur05ddx.sheltermanager.com:/root/")
            os.system("ssh root@eur05ddx.sheltermanager.com \"psql -q -U robin -f zzz_check.sql > /dev/null && rm -f zzz_check.sql\"")
            os.system("rm -f zzz_check.sql")
        else:
            if SHOWNONEXEC:
                print(f"Cannot execute query for {dbinfo}, copy and paste query below:\n")
                print(substitute(sql))
            else:
                print("         [ skip non-SQLite query ]")


for f in sys.argv:
    if not f.endswith("check.py") and os.path.exists(f):
        print(f"==== {f}")
        with open(f, "r") as h:
            parse_reports(h.read())

print(f"\nChecked {checked} / {total} queries.")
