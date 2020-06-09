
import unittest
import base

import asm3.animal, asm3.waitinglist
import asm3.utils

class TestWaitingList(unittest.TestCase):
   
    wlid = 0

    def setUp(self):
        data = {
            "dateputon": base.today_display(),
            "description": "Test",
            "species": "1",
            "size": "1",
            "owner": "1",
            "urgency": "5"
        }
        post = asm3.utils.PostedData(data, "en")
        self.wlid = asm3.waitinglist.insert_waitinglist_from_form(base.get_dbo(), post, "test")

    def tearDown(self):
        asm3.waitinglist.delete_waitinglist(base.get_dbo(), "test", self.wlid)

    def test_get_waitinglist_by_id(self):
        asm3.waitinglist.get_waitinglist_by_id(base.get_dbo(), self.wlid)

    def test_get_waitinglist(self):
        asm3.waitinglist.get_waitinglist(base.get_dbo())

    def test_get_waitinglist_find_simple(self):
        asm3.waitinglist.get_waitinglist_find_simple(base.get_dbo(), "Test")

    def test_get_satellite_counts(self):
        assert asm3.waitinglist.get_satellite_counts(base.get_dbo(), self.wlid) is not None

    def test_auto_remove_waitinglist(self):
        asm3.waitinglist.auto_remove_waitinglist(base.get_dbo())

    def test_auto_update_urgencies(self):
        asm3.waitinglist.auto_update_urgencies(base.get_dbo())

    def test_create_animal(self):
        aid = asm3.waitinglist.create_animal(base.get_dbo(), "test", self.wlid)
        assert aid is not None and aid > 0
        asm3.animal.delete_animal(base.get_dbo(), "test", aid)

