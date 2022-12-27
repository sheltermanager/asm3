#!/usr/bin/env python3

# Read the schema from a SQLite database and output it as static
# JSON data for use by code complete within the application.

import web, json

web.config.debug = False
db = web.database( dbn = "sqlite", db = "scripts/schema/schema.db" )

VIEWS = [ "adoption", "animal", "animalcontrol", "animalfound", "animallost", 
    "animalmedicalcombined", "animalmedicaltreatment", "animaltest", "animalvaccination", 
    "animalwaitinglist", "owner", "ownercitation", "ownerdonation", 
    "ownerlicence", "ownertraploan", "ownervoucher" ]

tables = {}
for table in db.query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    tname = table.name
    cols = []
    for col in db.query("pragma table_info(%s)" % tname):
        cols.append(col.name)
    tables[tname] = cols

for v in VIEWS:
    cols = []
    for col in db.query("pragma table_info(v_%s)" % v):
        cols.append(col.name)
    tables["v_%s" % v] = cols

print("schema=%s;" % json.dumps(tables))
