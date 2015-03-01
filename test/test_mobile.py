#!/usr/bin/python env

import unittest
import base

import mobile

class FakeSession:
    user = "test"
    roles = ""
    superuser = 1

class TestMobile(unittest.TestCase):

    def test_page(self):
        mobile.page(base.get_dbo(), FakeSession(), "test")
 

