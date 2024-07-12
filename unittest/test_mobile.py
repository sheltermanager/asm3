
import unittest
import base
import web.utils

import asm3.mobile

class TestMobile(unittest.TestCase):

    def test_page(self):
        fakesession = web.utils.storage(user="test", siteid=0, staffid=0, session=web.utils.storage(roles="", superuser=1, securitymap="", mobileapp=False), lf=None)
        asm3.mobile.page(base.get_dbo(), fakesession, "test")
 

