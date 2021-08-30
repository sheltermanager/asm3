
import unittest
import base

import asm3.dbupdate

class TestDBUpdate(unittest.TestCase):

    def test_diagnostic(self):
        asm3.dbupdate.diagnostic(base.get_dbo())

    def test_replace_html_entities(self):
        asm3.dbupdate.replace_html_entities(base.get_dbo())


