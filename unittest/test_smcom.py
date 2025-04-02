
import unittest
import base

import asm3.smcom

class TestSmcom(unittest.TestCase):

    def test_check_bulk_email(self):
        dbo = base.get_dbo()
        halflimit = int(asm3.smcom.MAX_EMAILS / 2)
        asm3.smcom.clear_emails_sent(dbo)
        asm3.smcom.check_bulk_email(dbo, halflimit)
        self.assertEqual(asm3.smcom.get_emails_sent(dbo), halflimit)
        with self.assertRaises(asm3.smcom.SmcomError):
            asm3.smcom.check_bulk_email(dbo, asm3.smcom.MAX_EMAILS)
    
