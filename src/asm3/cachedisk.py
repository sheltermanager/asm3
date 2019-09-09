
"""
Implements a python disk cache in a similar way to memcache,
uses md5sums of the key as filenames.
"""

import asm3.al

import hashlib
import os
import sys
import time

from asm3.sitedefs import DISK_CACHE

if sys.version_info[0] > 2: # PYTHON3
    import pickle
else:
    import cPickle as pickle

def _getfilename(key):
    """
    Calculates the filename from the key
    (md5 hash)
    """
    if not os.path.exists(DISK_CACHE):
        os.mkdir(DISK_CACHE)
    m = hashlib.md5()
    if sys.version_info[0] > 2 and isinstance(key, str): # PYTHON3
        key = key.encode("utf-8")
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
        asm3.al.error(str(err), "cachedisk.delete")

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
        with open(fname, "r") as f:
            o = pickle.load(f)

        # Has the entry expired?
        if o["expires"] < time.time():
            delete(key)
            return None

        return o["value"]
    except Exception as err:
        asm3.al.error(str(err), "cachedisk.get")
        return None

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
        with open(fname, "w") as f:
            pickle.dump(o, f)

    except Exception as err:
        asm3.al.error(str(err), "cachedisk.put")

def touch(key, ttlremaining = 0, newttl = 0):
    """
    Retrieves a value from our disk cache and updates its ttl if there is less than ttlremaining until expiry.
    This can be used to make our timed expiry cache into a sort of hybrid with LRU.
    Returns None if the value is not found or has expired.
    """
    f = None
    try:
        fname = _getfilename(key)

        # No cache entry found, bail
        if not os.path.exists(fname): return None

        # Pull the entry out
        with open(fname, "r") as f:
            o = pickle.load(f)

        # Has the entry expired?
        now = time.time()
        if o["expires"] < now:
            delete(key)
            return None

        # Is there less than ttlremaining to expiry? If so update it to newttl
        if o["expires"] - now < ttlremaining:
            o["expires"] = now + newttl
            with open(fname, "w") as f:
                pickle.dump(o, f)

        return o["value"]
    except Exception as err:
        asm3.al.error(str(err), "cachedisk.touch")
        return None

def remove_expired():
    """
    Runs through the cache and deletes any files that have expired.
    To make this process quick, we look at the raw file content to 
    extract the expires value.
    If the Python pickle format ever changes, this might mess us up.
    """
    if DISK_CACHE == "": return
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
        else:
            ep = chunk.find("\n", sp)
            expires = float(chunk[sp+1:ep])
            if time.time() > expires:
                os.unlink(fpath)

