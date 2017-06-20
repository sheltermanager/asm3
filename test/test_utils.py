#!/usr/bin/python env

import datetime, unittest
#import base

import utils

class TestUtils(unittest.TestCase):
 
    def test_json_handler(self):
        assert utils.json({ "v": None}).find("null") != -1
        assert utils.json({ "d": datetime.datetime(2014, 01, 01, 01, 01, 01) }).find("2014-01-01T01:01:01") != -1
        assert utils.json({ "t": datetime.timedelta(days = 1) }).find("00:00:00") != -1


