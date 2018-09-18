#!/usr/bin/python env

import unittest
import base

import person
import utils

class TestPerson(unittest.TestCase):
   
    nid = 0

    def setUp(self):
        data = {
            "title": "Mr",
            "forenames": "Test",
            "surname": "Testing",
            "ownertype": "1",
            "address": "123 test street"
        }
        post = utils.PostedData(data, "en")
        self.nid = person.insert_person_from_form(base.get_dbo(), post, "test", geocode=False)

    def tearDown(self):
        person.delete_person(base.get_dbo(), "test", self.nid)

    def test_get_homechecked(self):
        assert 0 == len(person.get_homechecked(base.get_dbo(), self.nid))

    def test_get_person(self):
        person.get_person(base.get_dbo(), self.nid)

    def test_get_person_similar(self):
        assert len(person.get_person_similar(base.get_dbo(), "", "Testing", "Test", "123 street")) > 0

    def test_get_person_name(self):
        assert "" != person.get_person_name(base.get_dbo(), self.nid)

    def test_get_person_name_code(self):
        assert "" != person.get_person_name_code(base.get_dbo(), self.nid)

    def test_get_staff_volunteers(self):
        person.get_staff_volunteers(base.get_dbo())

    def test_get_towns(self):
        person.get_towns(base.get_dbo())

    def test_get_town_to_county(self):
        person.get_town_to_county(base.get_dbo())

    def test_get_counties(self):
        person.get_counties(base.get_dbo())

    def test_get_satellite_counts(self):
        person.get_satellite_counts(base.get_dbo(), self.nid)

    def test_get_reserves_without_homechecks(self):
        person.get_reserves_without_homechecks(base.get_dbo())

    def test_get_overdue_donations(self):
        person.get_overdue_donations(base.get_dbo())

    def test_get_links(self):
        person.get_links(base.get_dbo(), self.nid)

    def test_get_investigation(self):
        person.get_investigation(base.get_dbo(), self.nid)

    def test_get_rota(self):
        person.get_rota(base.get_dbo(), base.today(), base.today())

    def test_get_person_rota(self):
        person.get_person_rota(base.get_dbo(), self.nid)

    def test_update_owner_names(self):
        person.update_owner_names(base.get_dbo())
 
    def test_get_person_find_simple(self):
        assert len(person.get_person_find_simple(base.get_dbo(), "Test", "user")) > 0

    def test_get_person_find_advanced(self):
        assert len(person.get_person_find_advanced(base.get_dbo(), { "name": "Test" }, "user")) > 0

    def test_investigation_crud(self):
        data = {
            "personid": str(self.nid),
            "date": base.today_display(),
            "notes": "Test"
        }
        post = utils.PostedData(data, "en")
        iid = person.insert_investigation_from_form(base.get_dbo(), "test", post)
        data["investigationid"] = str(iid)
        person.update_investigation_from_form(base.get_dbo(), "test", post)
        person.delete_investigation(base.get_dbo(), "test", iid)

    def test_rota_crud(self):
        data = {
            "person": str(self.nid),
            "startdate": base.today_display(),
            "starttime": "00:00",
            "enddate": base.today_display(),
            "endtime": "00:00",
            "type": "1"
        }
        post = utils.PostedData(data, "en")
        rid = person.insert_rota_from_form(base.get_dbo(), "test", post)
        data["rotaid"] = str(rid)
        person.update_rota_from_form(base.get_dbo(), "test", post)
        person.delete_rota(base.get_dbo(), "test", rid)

    def test_update_pass_homecheck(self):
        person.update_pass_homecheck(base.get_dbo(), "test", self.nid, "")

    def test_update_missing_geocodes(self):
        person.update_missing_geocodes(base.get_dbo())

    def test_update_lookingfor_report(self):
        person.update_lookingfor_report(base.get_dbo())

    def test_update_anonymise_personal_data(self):
        person.update_anonymise_personal_data(base.get_dbo(), 1)

