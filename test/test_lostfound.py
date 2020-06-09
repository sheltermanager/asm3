
import unittest
import base

import asm3.animal, asm3.lostfound, asm3.waitinglist
import asm3.utils

class TestLostFound(unittest.TestCase):
   
    laid = 0
    faid = 0

    def setUp(self):
        data = {
            "datelost": base.today_display(),
            "datereported": base.today_display(),
            "owner": "1",
            "species": "1", 
            "sex": "1",
            "breed": "1",
            "colour": "1",
            "markings": "Test",
            "arealost": "Test",
            "areapostcode": "Test"
        }
        post = asm3.utils.PostedData(data, "en")
        self.laid = asm3.lostfound.insert_lostanimal_from_form(base.get_dbo(), post, "test")
        data = {
            "datefound": base.today_display(),
            "datereported": base.today_display(),
            "owner": "1",
            "species": "1", 
            "sex": "1",
            "breed": "1",
            "colour": "1",
            "markings": "Test",
            "areafound": "Test",
            "areapostcode": "Test"
        }
        post = asm3.utils.PostedData(data, "en")
        self.faid = asm3.lostfound.insert_foundanimal_from_form(base.get_dbo(), post, "test")

    def tearDown(self):
        asm3.lostfound.delete_lostanimal(base.get_dbo(), "test", self.laid)
        asm3.lostfound.delete_foundanimal(base.get_dbo(), "test", self.faid)

    def test_get_lostanimal(self):
        assert asm3.lostfound.get_lostanimal(base.get_dbo(), self.laid) is not None

    def test_get_foundanimal(self):
        assert asm3.lostfound.get_foundanimal(base.get_dbo(), self.faid) is not None

    def test_get_lostanimal_find_simple(self):
        assert len(asm3.lostfound.get_lostanimal_find_simple(base.get_dbo(), "Test")) > 0

    def test_get_foundanimal_find_simple(self):
        assert len(asm3.lostfound.get_foundanimal_find_simple(base.get_dbo(), "Test")) > 0

    def test_get_lostanimal_find_advanced(self):
        assert len(asm3.lostfound.get_lostanimal_find_advanced(base.get_dbo(), { "area": "Test" })) > 0

    def test_get_foundanimal_find_advanced(self):
        assert len(asm3.lostfound.get_foundanimal_find_advanced(base.get_dbo(), { "area": "Test" })) > 0

    def test_get_lostanimal_last_days(self):
        assert len(asm3.lostfound.get_lostanimal_last_days(base.get_dbo())) > 0

    def test_get_foundanimal_last_days(self):
        assert len(asm3.lostfound.get_foundanimal_last_days(base.get_dbo())) > 0

    def test_get_lostanimal_satellite_counts(self):
        assert len(asm3.lostfound.get_lostanimal_satellite_counts(base.get_dbo(), self.laid)) > 0

    def test_get_foundanimal_satellite_counts(self):
        assert len(asm3.lostfound.get_foundanimal_satellite_counts(base.get_dbo(), self.faid)) > 0

    def test_update_match_report(self):
        asm3.lostfound.update_match_report(base.get_dbo())

    def test_get_lost_person_name(self):
        asm3.lostfound.get_lost_person_name(base.get_dbo(), self.laid)

    def test_get_found_person_name(self):
        asm3.lostfound.get_found_person_name(base.get_dbo(), self.faid)

    def test_create_animal_from_found(self):
        aid = asm3.lostfound.create_animal_from_found(base.get_dbo(), "test", self.faid)
        asm3.animal.delete_animal(base.get_dbo(), "test", aid)
       
    def test_create_waitinglist_from_found(self):
        aid = asm3.lostfound.create_waitinglist_from_found(base.get_dbo(), "test", self.faid)
        asm3.waitinglist.delete_waitinglist(base.get_dbo(), "test", aid)

