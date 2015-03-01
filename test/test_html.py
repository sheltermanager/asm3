#!/usr/bin/python env

import datetime, unittest
#import base

import html

class TestHtml(unittest.TestCase):
 
    def test_json_handler(self):
        assert html.json({ "v": None}).find("null") != -1
        assert html.json({ "d": datetime.datetime(2014, 01, 01, 01, 01, 01) }).find("2014-01-01T01:01:01") != -1
        assert html.json({ "t": datetime.timedelta(days = 1) }).find("00:00:00") != -1

    def test_escape(self):
        assert html.escape("'\"><") == "&apos;&quot;&gt;&lt;"

    def test_escape_angle(self):
        assert html.escape("><") == "&gt;&lt;"

    def test_json_menu(self):
        assert html.json_menu("en", [], []) is not None

