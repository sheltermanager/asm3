
import unittest
import base

import asm3.event

import datetime

class TestEvent(unittest.TestCase):
   
    nid = 0

    def setUp(self):
        data = {
            "startdate": "01/01/2023", 
            "enddate": "01/01/2023",
            "eventname": "Testio",
            "ownerid": "1",
            "address": "123 Test",
            "town": "Testton",
            "county": "Testshire",
            "postcode": "TS1 1PQ",
            "country": ""
        }
        post = asm3.utils.PostedData(data, "en")
        self.nid = asm3.event.insert_event_from_form(base.get_dbo(), post, "test")

    def tearDown(self):
        asm3.event.delete_event(base.get_dbo(), "test", self.nid)

    def test_update_event_from_form(self):
        data = {
            "id": self.nid,
            "startdate": "01/01/2023", 
            "enddate": "01/01/2023",
            "address": "256 Test",
            "recordversion": "-1"
        }
        post = asm3.utils.PostedData(data, "en")
        asm3.event.update_event_from_form(base.get_dbo(), post, "test")

    def test_get_event(self):
        assert asm3.event.get_event(base.get_dbo(), self.nid) is not None

    def test_get_event_date(self):
        assert len(asm3.event.get_event_date(base.get_dbo(), datetime.datetime(2023, 1, 1, 0, 0, 0))) > 0

    def test_get_event_find_advanced(self):
        assert len(asm3.event.get_event_find_advanced(base.get_dbo(), { "name": "Testio" })) > 0


