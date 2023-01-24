
import os, sys, datetime, time

PATH = os.path.dirname(os.path.abspath(__file__)) + os.sep
sys.path.append(PATH)
sys.path.append(PATH + "../src")

HOME = os.environ["HOME"]
DB_PATH = f"{HOME}/tmp/asmunittest.db"

import asm3.db

def reset_db():
    try:
        os.unlink(DB_PATH)
    except:
        pass

def get_dbo():
    dbo = asm3.db.get_dbo("SQLITE")
    dbo.database = DB_PATH
    dbo.installpath = "%s/../src/" % PATH
    return dbo

def execute(sql):
    get_dbo().execute(sql)

def today():
    return datetime.datetime.today()

def today_display():
    return time.strftime("%m/%d/%Y", datetime.datetime.today().timetuple())

