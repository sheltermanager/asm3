
import unittest
import base

import asm3.log
import asm3.utils

class TestLog(unittest.TestCase):
 
    nid = 0

    def setUp(self):
        self.nid = asm3.log.add_log(base.get_dbo(), "test", 0, 1, 1, "Test")

    def tearDown(self):
        asm3.log.delete_log(base.get_dbo(), "test", self.nid)

    def test_get_logs(self):
        assert len(asm3.log.get_logs(base.get_dbo(), 0, 1)) > 0

    def test_crud(self):
        data = {
            "logdate": base.today_display(),
            "type": "1", 
            "entry": "Test entry"
        }
        post = asm3.utils.PostedData(data, "en")
        nid = asm3.log.insert_log_from_form(base.get_dbo(), "test", 0, 1, post)
        asm3.log.update_log_from_form(base.get_dbo(), "test", post)
        asm3.log.delete_log(base.get_dbo(), "test", nid)

