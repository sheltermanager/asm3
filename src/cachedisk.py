#!/usr/bin/python

"""
Implements a python disk cache in a similar way to memcache,
uses md5sums of the key as filenames.
"""

import al
import cPickle as pickle
import hashlib
import os
import time
from sitedefs import DISK_CACHE

def _getfilename(key):
    """
    Calculates the filename from the key
    (md5 hash)
    """
    if not os.path.exists(DISK_CACHE):
        os.mkdir(DISK_CACHE)
    m = hashlib.md5()
    m.update(key)
    fname = "%s%s%s" % (DISK_CACHE, os.path.sep, m.hexdigest())
    return fname

def delete(key):
    """
    Removes a value from our disk cache.
    """
    try:
        fname = _getfilename(key)
        os.unlink(fname)
    except Exception as err:
        al.error(str(err), "cachedisk.delete")

def get(key):
    """
    Retrieves a value from our disk cache. Returns None if the
    value is not found or has expired.
    """
    f = None
    try:
        fname = _getfilename(key)

        # No cache entry found, bail
        if not os.path.exists(fname): return None

        # Pull the entry out
        f = open(fname, "r")
        o = pickle.load(f)

        # Has the entry expired?
        if o["expires"] < time.time():
            delete(key)
            return None

        return o["value"]
    except Exception as err:
        al.error(str(err), "cachedisk.get")
        return None
    finally:
        try:
            f.close()
        except:
            pass

def put(key, value, ttl):
    """
    Stores a value in our disk cache with a time to live of ttl. The value
    will be removed if it is accessed past the ttl.
    """
    f = None
    try:
        fname = _getfilename(key)

        o = {
            "expires": time.time() + ttl,
            "value": value
        }

        # Write the entry
        f = open(fname, "w")
        pickle.dump(o, f)

    except Exception as err:
        al.error(str(err), "cachedisk.put")
    finally:
        try:
            f.close()
        except:
            pass


def remove_expired():
    """
    Runs through the cache and deletes any files that have expired.
    To make this process quick, we look at the raw file content to 
    extract the expires value.
    If the Python pickle format ever changes, this might mess us up.
    """
    for fname in os.listdir(DISK_CACHE):
        if fname.startswith("."): continue
        fpath = "%s/%s" % (DISK_CACHE, fname)
        chunk = ""
        with open(fpath, "rb") as f:
            chunk = f.read(75)
        # Look for our float expiry time
        sp = chunk.find("F")
        if sp == -1: 
            # If we didn't find it, remove the file anyway - we don't know what this is
            os.unlink(fpath)
        ep = chunk.find("\n", sp)
        expires = float(chunk[sp+1:ep])
        if time.time() > expires:
            os.unlink(fpath)

