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

errors = 0
checked = 0
total = 0

def substitute(sql):
    COMMON_DATE_TOKENS = ( "CURRENT_DATE", "@from", "@to", "@osfrom", "@osto", "@osatdate", "@dt", "@thedate" )
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
        elif token.startswith("SQL"):
            elems = token.split(" ")
            if len(elems) == 3:
                stype = elems[1]
                sparams = elems[2].split(",")
                if stype == "CONCAT":
                    sub = "||".join(sparams)
                elif stype == "INTERVAL":
                    sub = f"datetime({sparams[0]}, '{sparams[1]}{sparams[2]} {sparams[3]}')"
                elif stype == "DATEDIFF":
                    sub = f"julianday({sparams[1]})-julianday({sparams[0]})"
                elif stype == "DAY":
                    sub = f"strftime('%d', {sparams[0]})"
                elif stype == "MONTH":
                    sub = f"strftime('%m', {sparams[0]})"
                elif stype == "YEAR":
                    sub = f"strftime('%y', {sparams[0]})"
        else:
            sub = "0"
        sql = sql[0:i] + sub + sql[end+1:]
        i = sql.find("$", i+1)
    return sql.strip()

_html_parser = None
def validate_html(html):
    """If lxml can properly parse the html, return the lxml representation.
    Otherwise raise."""
    global _html_parser
    from lxml import etree
    from io import StringIO
    if not _html_parser: _html_parser = etree.HTMLParser(recover = False)
    return etree.parse(StringIO(html), _html_parser)

def check_html(h):
    global errors
    def get_section(startpattern, endpattern, nth=1):
        ss = h.find(startpattern)
        es = h.find(endpattern, ss)
        if nth == 2:
            ss = h.find(startpattern, es)
            es = h.find(endpattern, ss)
        if ss == -1: 
            return ""
        if es == -1:
            print(f"missing end tag {endpattern}")
            return ""
        return h[ss + len(startpattern):es]
    def get_groupheadfoot(g):
        gh = g.find("$$HEAD")
        gf = g.find("$$FOOT")
        if gh == -1 or gf == -1:
            print(f"can't find $$HEAD or $$FOOT in group '{g}'")
        return g[gh+6:gf], g[gf+6:]
    header = get_section("$$HEADER", "HEADER$$")
    footer = get_section("$$FOOTER", "FOOTER$$")
    body = get_section("$$BODY", "BODY$$")
    group1 = get_section("$$GROUP", "GROUP$$", 1)
    group2 = get_section("$$GROUP", "GROUP$$", 2)
    group1head = ""
    group1foot = ""
    group2head = ""
    group2foot = ""
    if group1 != "": group1head, group1foot = get_groupheadfoot(group1)
    if group2 != "": group2head, group2foot = get_groupheadfoot(group2)
    doc = f"{header}\n{group1head}\n{group2head}\n{body}\n{group2foot}\n{group1foot}\n{footer}"
    try:
        validate_html(doc)
    except Exception as e:
        errors += 1
        print("\nHTML VALIDATION FAILED: %s" % e)

def parse_reports(data):
    global checked
    global total
    global errors
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
                errors += 1
                print(f"\nQUERY FAILED: {err}\n")
                print(sql)
            if len(html) > 0 and html.find("<") != -1:
                check_html(html)
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
                            errors += 1
                            print(f"\nQUERY FAILED: {err}\n")
                            print(sql)
                        if len(html) > 0 and html.find("<") != -1:
                            check_html(html)

        elif EXECPOSTGRES and dbinfo.find("PostgreSQL") != -1:
            with open("zzz_check.sql", "w") as f:
                f.write(substitute(sql))
            checked += 1
            os.system("scp -q zzz_check.sql root@eur05ddx.sheltermanager.com:/root/")
            os.system("ssh root@eur05ddx.sheltermanager.com \"psql -q -U robin -f zzz_check.sql > /dev/null && rm -f zzz_check.sql\"")
            os.system("rm -f zzz_check.sql")
            if len(html) > 0 and html.find("<") != -1:
                check_html(html)
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

print(f"\nChecked {checked} / {total} reports. {errors} errors.")
