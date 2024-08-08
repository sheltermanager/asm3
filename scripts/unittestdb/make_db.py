#!/usr/bin/env python3

import os, sys

PATH = os.path.dirname(os.path.abspath(__file__)) + os.sep
SRC_PATH = PATH + "../../src/"
DB_PATH = PATH + "../../scripts/unittestdb/base.db"

sys.path.append(PATH)
sys.path.append(SRC_PATH)

import asm3.db

try:
    # remove existing schema database first
    os.unlink(DB_PATH)
except:
    pass

# Create new schema database
dbo = asm3.db.get_dbo("SQLITE")
dbo.database = DB_PATH
dbo.installpath = SRC_PATH
asm3.dbupdate.install(dbo)

