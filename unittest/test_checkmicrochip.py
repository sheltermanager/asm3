
import unittest
import base

import asm3.checkmicrochip

class TestAutomail(unittest.TestCase):

    def test_en(self):
        asm3.checkmicrochip.check(base.get_dbo(), "en", "999999999999999")

    def test_en_AU(self):
        asm3.checkmicrochip.check(base.get_dbo(), "en_AU", "999999999999999")

    def test_en_GB(self):
        asm3.checkmicrochip.check(base.get_dbo(), "en_GB", "999999999999999")
