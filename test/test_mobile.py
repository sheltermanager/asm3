#!/usr/bin/python env

import unittest
import base
import web.utils

import mobile

class TestMobile(unittest.TestCase):

    def test_page(self):
        fakesession = web.utils.storage(user="test", roles="", superuser=1, mobileapp=False)
        mobile.page(base.get_dbo(), fakesession, "test")
 

