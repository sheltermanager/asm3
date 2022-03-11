
"""
Implements a python disk cache in a similar way to memcache,
uses md5sums of the key as filenames.
"""

import asm3.al

import fcntl
import hashlib
import os
import pickle
import re
import threading
import time

from asm3.sitedefs import DISK_CACHE

def _sanitise_path(path):
    """
    Make sure the path we've been given is safe to use, it should only
    contain letters and numbers
    """
    return re.sub(r'[\W_]+', '', path)

def _is_hex(s):
    try:
        int(s, 16)
        return True
    except:
        return False

threadlock = threading.Lock()

def _lrunpickle(fname):
    """ Reads a file and returns the unpickled contents, using flock to lock the file """
    with threadlock:
        with open(fname, "rb") as fd:
            fcntl.flock(fd, fcntl.LOCK_EX)
            return pickle.load(fd)

def _lwpickle(fname, o):
    """ Pickles and writes o to fname, using flock to lock the file """
    with threadlock:
        with open(fname, "wb") as fd:
            fcntl.flock(fd, fcntl.LOCK_EX)
            pickle.dump(o, fd)

def _getfilename(key, path, mkpath=False):
    """
    Calculates the filename from the key
    (md5 hash)
    If mkpath is True, creates any missing path directories.
    """
    # Is the key already a hash? ie. 32 or 40 chars and hex?
    # If so, don't waste time hashing it again.
    if (len(key) == 32 or len(key) == 40) and _is_hex(key):
        pass
    else:
        m = hashlib.md5()
        if isinstance(key, str): key = key.encode("utf-8") # turn str keys into bytes
        m.update(key)
        key = m.hexdigest()
    if not os.path.exists(DISK_CACHE):
        os.mkdir(DISK_CACHE)
    if path != "":
        path = _sanitise_path(path)
        path = os.path.join(DISK_CACHE, path)
        if mkpath and not os.path.exists(path):
            os.mkdir(path)
    else:
        path = DISK_CACHE
    fname = os.path.join(path, key)
    return fname

def delete(key, path):
    """
    Removes a value from our disk cache.
    """
    try:
        fname = _getfilename(key, path)
        os.unlink(fname)
    except Exception as err:
        asm3.al.error(str(err), "cachedisk.delete")

def exists(key, path):
    """
    Returns true if a key exists in the cache (does not unpack and check expiry)
    """
    fname = _getfilename(key, path)
    return os.path.exists(fname)

def increment(key, path, ttl):
    """
    Retrieves a value from our disk cache, increments it and returns the value
    """
    v = get(key, path, int)
    v += 1
    put(key, path, v, ttl)
    return v

def get(key, path, expectedtype=None):
    """
    Retrieves a value from our disk cache. Returns None if the
    value is not found or has expired.
    expectedtype: A type if one is expected. This was added due to an MD5 collision
    that caused an image to be read as a config dictionary, which wiped out someone's
    config and caused all the database updates to be re-run.
    """
    try:
        fname = _getfilename(key, path)

        # No cache entry found, bail
        if not os.path.exists(fname): return None

        # Pull the entry out
        o = _lrunpickle(fname)

        # Has the entry expired?
        if o["expires"] < time.time():
            delete(key, path)
            return None

        # Is the value of the type we're expecting?
        if expectedtype is not None and type(o["value"]) != expectedtype:
            return None

        return o["value"]
    except Exception as err:
        asm3.al.error("%s/%s: %s" % (path, key, err), "cachedisk.get")

def put(key, path, value, ttl):
    """
    Stores a value in our disk cache with a time to live of ttl. The value
    will be removed if it is accessed past the ttl.
    """
    try:
        fname = _getfilename(key, path, mkpath=True)

        o = {
            "expires": time.time() + ttl,
            "value": value
        }

        # Write the entry
        _lwpickle(fname, o)
    except Exception as err:
        asm3.al.error("%s/%s: %s" % (path, key, err), "cachedisk.put")

def touch(key, path, newttl = 0):
    """
    Retrieves a value from our disk cache and resets its ttl.
    This can be used to make our timed expiry cache into a sort of hybrid with LRU.
    Returns None if the value is not found or has expired.
    """
    try:
        fname = _getfilename(key, path)

        # No cache entry found, bail
        if not os.path.exists(fname): return None

        # Pull the entry out
        with open(fname, "rb") as f:
            o = pickle.load(f)

        # Has the entry expired?
        now = time.time()
        if o["expires"] < now:
            delete(key, path)
            return None

        # Reset the ttl
        o["expires"] = now + newttl
        with open(fname, "wb") as f:
            pickle.dump(o, f)

        return o["value"]
    except Exception as err:
        asm3.al.error("%s/%s: %s" % (path, key, err), "cachedisk.touch")

def remove_expired(path):
    """
    Runs through the cache and deletes any files that have expired
    for cache/path
    """
    if DISK_CACHE == "": return
    cache_path = os.path.join(DISK_CACHE, path)
    checked = 0
    removed = 0
    for root, dummy, files in os.walk(cache_path):
        for name in files:
            if name.startswith("."): continue
            checked += 1
            try:
                fpath = os.path.join(root, name)
                with open(fpath, "rb") as f:
                    o = pickle.load(f)
                if o["expires"] < time.time():
                    os.unlink(fpath)
                    removed += 1
            except:
                # Move to the next entry if there are problems
                pass
    asm3.al.debug("removed %s expired disk cache entries for '%s' (%s checked)" % (removed, path, checked), "cachedisk.remove_expired")
