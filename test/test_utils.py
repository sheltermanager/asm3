#!/usr/bin/python env

import datetime, unittest
import base

import asm3.utils

class TestUtils(unittest.TestCase):
 
    def test_json_handler(self):
        assert asm3.utils.json({ "v": None}).find("null") != -1
        assert asm3.utils.json({ "d": datetime.datetime(2014, 1, 1, 1, 1, 1) }).find("2014-01-01T01:01:01") != -1
        assert asm3.utils.json({ "t": datetime.timedelta(days = 1) }).find("00:00:00") != -1

    def test_send_email(self):
        asm3.utils.send_email( base.get_dbo(), "tests@example.com", "example@example.com", subject="Test", body="Test suite", exceptions=False )

