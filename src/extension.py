#!/usr/bin/python

import smcom

def route(dbo, when, caller, post):
    """ 
    routes any extension calls. 
    when:    "before" or "after"
    method:  the calling method name - eg: insert_animal_from_form
    post:    any posted values sent to the caller so they can be
             passed to the plugin method.
    return value: True to continue or False to cancel whatever the 
             default behaviour is (only applies to before) -or 
             raise an exception.
    """
    target = when + "_" + caller
    method = globals().get(target)
    if method:
        return method(dbo, post)
    if smcom.active():
        return smcom.route_customer_extension(dbo, when, caller, post)
    else:
        return True

"""
def before_insert_animal_from_form(dbo, post):
    # Example extension method, does nothing. post could have
    # extra validation checks here, etc.
    return True
"""

