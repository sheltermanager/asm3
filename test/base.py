#!/usr/bin/python env

import os, sys, datetime, time

PATH = os.path.dirname(os.path.abspath(__file__)) + os.sep
sys.path.append(PATH)
sys.path.append(PATH + "../src")

import db

def get_dbo():
    dbo = db.DatabaseInfo()
    dbo.dbtype = "MYSQL"
    dbo.database = "asmunittest"
    return dbo

def execute(sql):
    db.execute(get_dbo(), sql)

def today():
    return datetime.datetime.today()

def today_display():
    return time.strftime("%m/%d/%Y", datetime.datetime.today().timetuple())

