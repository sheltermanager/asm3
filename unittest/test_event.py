
import unittest
import base

import asm3.event

import datetime

class TestEvent(unittest.TestCase):
   
    nid = 0
    eaid = 0

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
        data = {
            "eventid":  str(self.nid),
            "animalid": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        self.eaid = asm3.event.insert_event_animal(base.get_dbo(), "test", post)

    def tearDown(self):
        asm3.event.delete_event(base.get_dbo(), "test", self.nid)
        asm3.event.delete_event_animal(base.get_dbo(), "test", self.eaid)

    def test_update_event_from_form(self):
        data = {
            "id": str(self.nid),
            "startdate": "01/01/2023", 
            "enddate": "01/01/2023",
            "address": "256 Test",
            "recordversion": "-1"
        }
        post = asm3.utils.PostedData(data, "en")
        asm3.event.update_event_from_form(base.get_dbo(), post, "test")

    def test_get_animals_by_event(self):
        asm3.event.get_animals_by_event(base.get_dbo(), self.nid, "all")
        asm3.event.get_animals_by_event(base.get_dbo(), self.nid, "arrived")
        asm3.event.get_animals_by_event(base.get_dbo(), self.nid, "noshow")
        asm3.event.get_animals_by_event(base.get_dbo(), self.nid, "neednewfoster")
        asm3.event.get_animals_by_event(base.get_dbo(), self.nid, "dontneednewfoster")
        asm3.event.get_animals_by_event(base.get_dbo(), self.nid, "adopted")
        asm3.event.get_animals_by_event(base.get_dbo(), self.nid, "notadopted")

    def test_get_event(self):
        assert asm3.event.get_event(base.get_dbo(), self.nid) is not None

    def test_get_events_by_animal(self):
        asm3.event.get_events_by_animal(base.get_dbo(), 1)

    def test_get_events_by_date(self):
        assert len(asm3.event.get_events_by_date(base.get_dbo(), datetime.datetime(2023, 1, 1, 0, 0, 0))) > 0

    def test_get_event_find_advanced(self):
        assert len(asm3.event.get_event_find_advanced(base.get_dbo(), { "name": "Testio" })) > 0

    def test_update_event_animal(self):
        data = {
            "eventanimalid": str(self.eaid),
            "animal":        "1",
            "arrivaldate":   "01/01/2023",
            "arrivaltime":   "00:00:00",
            "comments":      ""
        }
        post = asm3.utils.PostedData(data, "en")
        asm3.event.update_event_animal(base.get_dbo(), "test", post)

    def test_update_event_animal_arrived(self):
        asm3.event.update_event_animal_arrived(base.get_dbo(), "test", self.eaid)

    def test_end_active_foster(self):
        asm3.event.end_active_foster(base.get_dbo(), "test", self.eaid)


