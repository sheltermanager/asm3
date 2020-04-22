
import unittest
import base
import web.utils

import asm3.mobile

class TestMobile(unittest.TestCase):

    def test_page(self):
        fakesession = web.utils.storage(user="test", roles="", superuser=1, mobileapp=False)
        asm3.mobile.page(base.get_dbo(), fakesession, "test")
 

