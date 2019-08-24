#!/usr/bin/python env

import datetime, unittest

import asm3.html, asm3.publish

class TestHtml(unittest.TestCase):
 
    def test_escape(self):
        assert asm3.html.escape("'\"><") == "&apos;&quot;&gt;&lt;"

    def test_escape_angle(self):
        assert asm3.html.escape("><") == "&gt;&lt;"

    def test_menu_structure(self):
        assert asm3.html.menu_structure("en", asm3.publish.PUBLISHER_LIST, [], []) is not None

