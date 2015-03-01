#!/usr/bin/python env

import unittest
import base, base64

import search
import utils

class FakeSession:
    user = "test"
    roles = ""
    superuser = 1

class TestSearch(unittest.TestCase):

    def test_search(self):
        search.search(base.get_dbo(), FakeSession(), "test")
        keywords = [ "os", "notforadoption", "notmicrochipped", "hold", "quarantine", "deceased", 
            "forpublish", "people", "vets", "retailers", "staff", "fosterers", "volunteers", "shelters",
            "aco", "homechecked", "homecheckers", "members", "donors", "reservenohomecheck",
            "overduedonations", "activelost", "activefound" ]
        for k in keywords:
            search.search(base.get_dbo(), FakeSession(), k)

