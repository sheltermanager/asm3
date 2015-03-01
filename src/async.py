#!/usr/bin/python

"""
Module for helping run tasks asynchronously and updating/getting progress.
Only allows one async task per database to be run at a time.
"""

import cache

lc = {}

def get(dbo, k):
    if cache.available():
        return cache.get("%s.%s" % (dbo.database, k))
    else:
        global lc
        if lc.has_key(k):
            return lc[k]
        return None

def put(dbo, k, v):
    if cache.available():
        cache.put("%s.%s" % (dbo.database, k), v, 3600)
    else:
        global lc
        lc[k] = v

def is_task_running(dbo):
    name = get(dbo, "taskname")
    v = get(dbo, "taskval")
    if v is not None and v == 100:
        return False
    if name is not None and name != "":
        return True
    return False

def reset(dbo):
    put(dbo, "taskname", "")
    put(dbo, "taskmax", 0)
    put(dbo, "taskval", 0)
    put(dbo, "taskcancel", False)
    # tasklasterror deliberately not cleared

def get_task_name(dbo):
    v = get(dbo, "taskname")
    if v is None or v == "":
        return "NONE"
    return v

def set_task_name(dbo, v):
    put(dbo, "taskname", v)

def get_progress_max(dbo):
    return get(dbo, "taskmax")
   
def set_progress_max(dbo, progressmax):
    put(dbo, "taskmax", progressmax)

def get_progress_value(dbo):
    return get(dbo, "taskval")

def get_progress_percent(dbo):
    m = get_progress_max(dbo)
    v = get_progress_value(dbo)
    if m is not None and v is not None and m != 0:
        return int((float(v) / float(m)) * 100)
    return 0

def set_progress_value(dbo, v):
    return put(dbo, "taskval", v)

def increment_progress_value(dbo):
    v = get_progress_value(dbo)
    if v is not None: 
        v += 1
        set_progress_value(dbo, v)

def get_cancel(dbo):
    v = get(dbo, "taskcancel")
    if v is None: return False
    return v

def set_cancel(dbo, v):
    put(dbo, "taskcancel", v)

def get_last_error(dbo):
    v = get(dbo, "tasklasterror")
    if v is None: return ""
    return v

def set_last_error(dbo, e):
    put(dbo, "tasklasterror", e)


