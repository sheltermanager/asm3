
import os, sys, datetime, time

PATH = os.path.dirname(os.path.abspath(__file__)) + os.sep
DB_PATH = f"{PATH}../scripts/unittestdb"

sys.path.append(PATH)
sys.path.append(PATH + "../src")

import asm3.db

def get_dbo():
    dbo = asm3.db.get_dbo("SQLITE")
    dbo.database = f"{DB_PATH}/test.db"
    dbo.installpath = f"{PATH}../src/"
    return dbo

def execute(sql):
    get_dbo().execute(sql)

def query(sql):
    return get_dbo().query(sql)

def now():
    return datetime.datetime.today()

def now_display():
    return time.strftime("%m/%d/%Y %H:%M:%S", now().timetuple())

def today():
    return datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

def today_display():
    return time.strftime("%m/%d/%Y", today().timetuple())


