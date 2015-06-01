#!/usr/bin/python

"""
Implements a python disk cache in a similar way to memcache,
uses keys as filenames.
"""

import cPickle as pickle
import os
import time
from sitedefs import DISK_CACHE

def _getfilename(key):
    notallowed = [ "!", "\"", "$", "%", "^", "&", "*", "(", ")", "-", "/", "\\", "'", "@", ":", ";", ",", ".", "?" ]
    for s in notallowed:
        key = key.replace(s, "_")
    fname = "%s/%s" % (DISK_CACHE, key)
    return fname

def delete(key):
    """
    Removes a value from our disk cache.
    """
    fname = _getfilename(key)
    os.unlink(fname)

def get(key):
    """
    Retrieves a value from our disk cache. Returns None if the
    value is not found or has expired.
    """

    fname = _getfilename(key)
    
    # No cache entry found, bail
    if not os.path.exists(fname): return None

    # Pull the entry out
    f = open(fname, "r")
    o = pickle.load(f)
    f.close()

    # Has the entry expired?
    if o["expires"] < int(time.time()):
        delete(key)
        return None

    return o["value"]

def put(key, value, ttl):
    """
    Stores a value in our disk cache with a time to live of ttl. The value
    will be removed if it is accessed past the ttl.
    """

    fname = _getfilename(key)

    o = {
        "expires": int(time.time()) + ttl,
        "value": value
    }

    # Write the entry
    f = open(fname, "w")
    pickle.dump(o, f)
    f.close()

def reap():
    """
    Removes any dead or stale entries from the disk cache.
    """
    # TODO:

