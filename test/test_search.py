#!/usr/bin/python env

import unittest
import base, base64
import web.utils

import search
import utils

class TestSearch(unittest.TestCase):

    def test_search(self):
        fakesession = web.utils.storage(user="test", roles="", superuser=1, locationfilter="", siteid=0)
        search.search(base.get_dbo(), fakesession, "test")
        keywords = [ "os", "notforadoption", "notmicrochipped", "hold", "quarantine", "deceased", 
            "forpublish", "people", "vets", "retailers", "staff", "fosterers", "volunteers", "shelters",
            "aco", "homechecked", "homecheckers", "members", "donors", "reservenohomecheck",
            "overduedonations", "activelost", "activefound" ]
        for k in keywords:
            search.search(base.get_dbo(), fakesession, k)

