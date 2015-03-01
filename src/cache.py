#!/usr/bin/python

from sitedefs import MEMCACHED_SERVER

# Shared memcache client for the module
memcache_client = None

def available():
    return MEMCACHED_SERVER != ""

def _get_mc():
    """
    Returns a memcache client
    """
    import memcache
    mc = memcache.Client([MEMCACHED_SERVER], debug=0)
    return mc

def get(key):
    """
    Retrieves a cache value. Returns None if
    the value isn't set
    """
    global memcache_client
    try:
        if memcache_client is None: memcache_client = _get_mc()
        return memcache_client.get(key)
    except:
        memcache_client = _get_mc()
        return memcache_client.get(key)

def put(key, value, ttl):
    """
    Sets a cache value with a ttl in seconds
    """
    global memcache_client
    try:
        if memcache_client is None: memcache_client = _get_mc()
        return memcache_client.set(key, value, time = ttl )
    except:
        memcache_client = _get_mc()
        return memcache_client.set(key, value, time = ttl )

def increment(key):
    """
    Increments a cache value and returns it or
    None if the value doesn't exist.
    """
    global memcache_client
    try:
        if memcache_client is None: memcache_client = _get_mc()
        return memcache_client.incr(key)
    except:
        memcache_client = _get_mc()
        return memcache_client.incr(key)

def delete(key):
    """
    Deletes a cache value.
    """
    global memcache_client
    try:
        if memcache_client is None: memcache_client = _get_mc()
        return memcache_client.delete(key)
    except:
        memcache_client = _get_mc()
        return memcache_client.delete(key)


