#!/usr/bin/env python3

# Read the schema from a SQLite database and output it as static
# JSON data for use by code complete within the application.

import web, json

db = web.database( dbn = "sqlite", db = "scripts/schema/schema.db" )

VIEWS = [ "adoption", "animal", "animalcontrol", "animalfound", "animallost", "animalmedicaltreatment", 
    "animaltest", "animalvaccination", "animalwaitinglist", "owner", "ownercitation", "ownerdonation", 
    "ownerlicence", "ownertraploan", "ownervoucher" ]

tables = {}
for table in db.query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    tname = table.name
    cols = {}
    for col in db.query("pragma table_info(%s)" % tname):
        cname = col.name
        cols[cname] = ""
    tables[tname] = cols

for v in VIEWS:
    cols = {}
    for col in db.query("pragma table_info(v_%s)" % v):
        cname = col.name
        cols[cname] = ""
    tables["v_%s" % v] = cols

print("schema=%s;" % json.dumps(tables))
