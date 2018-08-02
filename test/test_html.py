#!/usr/bin/python env

import datetime, unittest
#import base

import html, publish

class TestHtml(unittest.TestCase):
 
    def test_escape(self):
        assert html.escape("'\"><") == "&apos;&quot;&gt;&lt;"

    def test_escape_angle(self):
        assert html.escape("><") == "&gt;&lt;"

    def test_menu_structure(self):
        assert html.menu_structure("en", publish.PUBLISHER_LIST, [], []) is not None

