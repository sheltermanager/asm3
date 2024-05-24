
import unittest
import base

import asm3.animalcontrol
import asm3.utils

class TestAnimalControl(unittest.TestCase):
   
    nid = 0

    def setUp(self):
        self.nid = asm3.animalcontrol.insert_animalcontrol(base.get_dbo(), "test")

    def tearDown(self):
        base.execute("DELETE FROM animalcontrol WHERE ID = %d" % self.nid)

    def test_get_animalcontrol(self):
        self.assertNotEqual(0, len(asm3.animalcontrol.get_animalcontrol(base.get_dbo(), self.nid)))

    def test_get_animalcontrol_animals(self):
        asm3.animalcontrol.get_animalcontrol_animals(base.get_dbo(), self.nid)

    def test_get_animalcontrol_for_animal(self):
        asm3.animalcontrol.get_animalcontrol_for_animal(base.get_dbo(), 0)

    def test_get_followup_two_dates(self):
        asm3.animalcontrol.get_followup_two_dates(base.get_dbo(), base.today(), base.today())

    def test_get_animalcontrol_find_simple(self):
        asm3.animalcontrol.get_animalcontrol_find_simple(base.get_dbo(), "test", "user")

    def test_get_animalcontrol_find_advanced(self):
        self.assertNotEqual(0, len(asm3.animalcontrol.get_animalcontrol_find_advanced(base.get_dbo(), { "number": str(self.nid) }, "user")))

    def test_get_animalcontrol_satellite_counts(self):
        asm3.animalcontrol.get_animalcontrol_satellite_counts(base.get_dbo(), self.nid)

    def test_get_active_traploans(self):
        asm3.animalcontrol.get_active_traploans(base.get_dbo())

    def test_get_person_traploans(self):
        asm3.animalcontrol.get_person_traploans(base.get_dbo(), 0)

    def test_get_traploan_two_dates(self):
        asm3.animalcontrol.get_traploan_two_dates(base.get_dbo(), base.today(), base.today())

    def test_update_animalcontrol_completenow(self):
        asm3.animalcontrol.update_animalcontrol_completenow(base.get_dbo(), 1, "test", 1)

    def test_update_animalcontrol_dispatchnow(self):
        asm3.animalcontrol.update_animalcontrol_dispatchnow(base.get_dbo(), 1, "test")

    def test_update_animalcontrol_respondnow(self):
        asm3.animalcontrol.update_animalcontrol_respondnow(base.get_dbo(), 1, "test")

    def test_insert_animalcontrol_from_form(self):
        data = {
            "incidentdate":   "01/01/2014",
            "incidenttime":   "00:00:00"
        }
        post = asm3.utils.PostedData(data, "en")
        nid = asm3.animalcontrol.insert_animalcontrol_from_form(base.get_dbo(), post, "test", geocode=False)
        asm3.animalcontrol.delete_animalcontrol(base.get_dbo(), "test", nid)

    def test_update_animalcontrol_from_form(self):
        data = {
            "incidentdate":   "01/01/2014",
            "incidenttime":   "00:00:00"
        }
        post = asm3.utils.PostedData(data, "en")
        asm3.animalcontrol.update_animalcontrol_from_form(base.get_dbo(), post, "test", geocode=False)

    def test_clone_animalcontrol(self):
        self.assertNotEqual(0, asm3.animalcontrol.clone_animalcontrol(base.get_dbo(), "test", self.nid))

    def test_insert_traploan_from_form(self):
        data = {
            "person":   "1",
            "type":     "1",
            "loandate": "01/01/2014"
        }
        post = asm3.utils.PostedData(data, "en")
        tid = asm3.animalcontrol.insert_traploan_from_form(base.get_dbo(), "test", post)
        asm3.animalcontrol.delete_traploan(base.get_dbo(), "test", tid)

    def test_update_traploan_from_form(self):
        data = {
            "person":   "2",
            "type":     "2",
            "loandate": "01/01/2014"
        }
        post = asm3.utils.PostedData(data, "en")
        asm3.animalcontrol.update_traploan_from_form(base.get_dbo(), "test", post)

    def test_update_dispatch_latlong(self):
        asm3.animalcontrol.update_dispatch_latlong(base.get_dbo(), self.nid, "54,52")

