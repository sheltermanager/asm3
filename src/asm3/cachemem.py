#!/usr/bin/python

from asm3.sitedefs import MEMCACHED_SERVER

import asm3.al
import time

def get(key):
    """
    Retrieves a cache value. Returns None if
    the value isn't set
    """
    if _memcache_available(): return _memcache_get(key)
    return _dict_get(key)

def put(key, value, ttl):
    """
    Sets a cache value with a ttl in seconds
    """
    if _memcache_available(): return _memcache_put(key, value, ttl)
    return _dict_put(key, value, ttl)

def increment(key):
    """
    Increments a cache value and returns it or
    None if the value doesn't exist.
    """
    if _memcache_available(): return _memcache_increment(key)
    return _dict_increment(key)

def delete(key):
    """
    Deletes a cache value.
    """
    if _memcache_available(): return _memcache_delete(key)
    return _dict_delete(key)

# ==============================================
# Dict implementation of memory cache
# ==============================================
dict_client = {}

def _dict_get(key):
    global dict_client
    if key not in dict_client: return None
    v = dict_client[key]
    # return the value if we're within ttl
    if time.time() < v[0]: return v[1]
    # remove the item as it's out of ttl
    _dict_delete(key)
    return None

def _dict_put(key, value, ttl):
    global dict_client
    dict_client[key] = [time.time() + ttl, value]

def _dict_increment(key):
    global dict_client
    v = _dict_get(key)
    if v is None: return None
    dict_client[key][1] += 1
    return v

def _dict_delete(key):
    global dict_client
    try:
        del dict_client[key]
    except KeyError:
        pass

# ==============================================
# Memcache implementation of memory cache
# ==============================================
memcache_client = None

def _get_mc():
    """
    Returns a memcache client
    """
    import memcache
    mc = memcache.Client([MEMCACHED_SERVER], debug=1) # causes any errors to be pumped out to stderr and picked up my mod_wsgi
    return mc

def _memcache_available():
    return MEMCACHED_SERVER != ""

def _memcache_get(key):
    global memcache_client
    if memcache_client is None: memcache_client = _get_mc()
    return memcache_client.get(key)

def _memcache_put(key, value, ttl):
    global memcache_client
    if memcache_client is None: memcache_client = _get_mc()
    rv = memcache_client.set(key, value, time = ttl )
    if not rv: asm3.al.error("failed writing value to memcache (ttl=%s,key=%s,val=%s)" % (ttl, key, value), "cachemem.memcache_put")
    return rv

def _memcache_increment(key):
    global memcache_client
    if memcache_client is None: memcache_client = _get_mc()
    return memcache_client.incr(key)

def _memcache_delete(key):
    global memcache_client
    if memcache_client is None: memcache_client = _get_mc()
    return memcache_client.delete(key)


