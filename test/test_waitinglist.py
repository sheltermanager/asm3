#!/usr/bin/python env

import unittest
import base

import animal, waitinglist
import utils

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
        post = utils.PostedData(data, "en")
        self.wlid = waitinglist.insert_waitinglist_from_form(base.get_dbo(), post, "test")

    def tearDown(self):
        waitinglist.delete_waitinglist(base.get_dbo(), "test", self.wlid)

    def test_get_waitinglist_by_id(self):
        assert waitinglist.get_waitinglist_by_id(base.get_dbo(), self.wlid) is not None

    def test_get_waitinglist(self):
        assert len(waitinglist.get_waitinglist(base.get_dbo())) > 0

    def test_get_waitinglist_find_simple(self):
        assert len(waitinglist.get_waitinglist_find_simple(base.get_dbo(), "Test")) > 0

    def test_get_satellite_counts(self):
        assert waitinglist.get_satellite_counts(base.get_dbo(), self.wlid) is not None

    def test_auto_remove_waitinglist(self):
        waitinglist.auto_remove_waitinglist(base.get_dbo())

    def test_auto_update_urgencies(self):
        waitinglist.auto_update_urgencies(base.get_dbo())

    def test_create_animal(self):
        aid = waitinglist.create_animal(base.get_dbo(), "test", self.wlid)
        assert aid is not None and aid > 0
        animal.delete_animal(base.get_dbo(), "test", aid)

