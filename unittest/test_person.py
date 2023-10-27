
import unittest
import base

import asm3.person
import asm3.utils

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
        post = asm3.utils.PostedData(data, "en")
        self.nid = asm3.person.insert_person_from_form(base.get_dbo(), post, "test", geocode=False)

    def tearDown(self):
        asm3.person.delete_person(base.get_dbo(), "test", self.nid)

    def test_get_homechecked(self):
        self.assertEqual(0, len(asm3.person.get_homechecked(base.get_dbo(), self.nid)))

    def test_get_person(self):
        asm3.person.get_person(base.get_dbo(), self.nid)

    def test_get_person_similar(self):
        self.assertNotEqual(0, len(asm3.person.get_person_similar(base.get_dbo(), "", "", "Testing", "Test", "123 street")))
        self.assertEqual(0, len(asm3.person.get_person_similar(base.get_dbo(), "test@test.com", "012345678", "Testing", "Test", "123 street", checkcouple=True, checkmobilehome=True, checkforenames=False, siteid=1)))

    def test_get_person_name(self):
        self.assertNotEqual("", asm3.person.get_person_name(base.get_dbo(), self.nid))

    def test_get_person_name_code(self):
        self.assertNotEqual("", asm3.person.get_person_name_code(base.get_dbo(), self.nid))

    def test_get_staff_volunteers(self):
        asm3.person.get_staff_volunteers(base.get_dbo())

    def test_get_towns(self):
        asm3.person.get_towns(base.get_dbo())

    def test_get_town_to_county(self):
        asm3.person.get_town_to_county(base.get_dbo())

    def test_get_counties(self):
        asm3.person.get_counties(base.get_dbo())

    def test_get_satellite_counts(self):
        asm3.person.get_satellite_counts(base.get_dbo(), self.nid)

    def test_get_reserves_without_homechecks(self):
        asm3.person.get_reserves_without_homechecks(base.get_dbo())

    def test_get_open_adoption_checkout(self):
        asm3.person.get_open_adoption_checkout(base.get_dbo())

    def test_get_overdue_donations(self):
        asm3.person.get_overdue_donations(base.get_dbo())

    def test_get_signed_requests(self):
        asm3.person.get_signed_requests(base.get_dbo())

    def test_get_unsigned_requests(self):
        asm3.person.get_unsigned_requests(base.get_dbo())

    def test_get_links(self):
        asm3.person.get_links(base.get_dbo(), self.nid)

    def test_get_investigation(self):
        asm3.person.get_investigation(base.get_dbo(), self.nid)

    def test_get_person_find_simple(self):
        self.assertNotEqual(0, len(asm3.person.get_person_find_simple(base.get_dbo(), "")))

    def test_get_person_find_advanced(self):
        self.assertNotEqual(0, len(asm3.person.get_person_find_advanced(base.get_dbo(), {})))

    def test_get_rota(self):
        asm3.person.get_rota(base.get_dbo(), base.today(), base.today())

    def test_get_person_rota(self):
        asm3.person.get_person_rota(base.get_dbo(), self.nid)

    def test_extra_ids(self):
        p = asm3.person.get_person(base.get_dbo(), self.nid)
        asm3.person.set_extra_id(base.get_dbo(), "user", p, "test", "xxx")
        self.assertEqual("xxx", asm3.person.get_extra_id(base.get_dbo(), p, "test"))

    def test_calculate_owner_code(self):
        self.assertEqual("TE000005", asm3.person.calculate_owner_code(5, "test"))
        self.assertEqual("XX000100", asm3.person.calculate_owner_code(100, "&#239;Z"))

    def test_calculate_owner_name(self):
        self.assertEqual("Mr R Robert Robertson", asm3.person.calculate_owner_name(base.get_dbo(), 1, "Mr", "R", "Robert", "Robertson",
            "{ownertitle} {ownerinitials} {ownerforenames} {ownersurname}"))
        self.assertEqual("Pets Inc", asm3.person.calculate_owner_name(base.get_dbo(), 2, last="Pets Inc"))
        self.assertEqual("John & Jane Doe", asm3.person.calculate_owner_name(base.get_dbo(), 3, "Mr", "J", "John", "Doe", 
            "", "", "{ownerforenames1} & {ownerforenames2} {ownersurname}", "Mrs", "J", "Jane", "Doe"))

    def test_update_owner_names(self):
        asm3.person.update_owner_names(base.get_dbo())

    def test_update_adopter_flag(self):
        asm3.person.update_adopter_flag(base.get_dbo(), "test", self.nid)

    def test_merge_person_details(self):
        asm3.person.merge_person_details(base.get_dbo(), "test", self.nid, {})

    def test_merge_gdpr_flags(self):
        s = asm3.person.merge_gdpr_flags(base.get_dbo(), "test", self.nid, "email")
        self.assertNotEqual(s.find("email"), -1)

    def test_merge_flags(self):
        s = asm3.person.merge_flags(base.get_dbo(), "test", self.nid, "fosterer")
        self.assertNotEqual(s.find("fosterer"), -1)

    def test_merge_person(self):
        data = {
            "title": "Mr",
            "forenames": "Merge",
            "surname": "Merging",
            "ownertype": "1",
            "address": "456 test street"
        }
        post = asm3.utils.PostedData(data, "en")
        mid = asm3.person.insert_person_from_form(base.get_dbo(), post, "test", geocode=False)
        asm3.person.merge_person(base.get_dbo(), "test", self.nid, mid)

    def test_get_person_embedded(self):
        self.assertIsNotNone(asm3.person.get_person_embedded(base.get_dbo(), self.nid))

    def test_embellish_adoption_warnings(self):
        self.assertIsNotNone(asm3.person.embellish_adoption_warnings(base.get_dbo(), asm3.person.get_person_embedded(base.get_dbo(), self.nid)))
 
    def test_investigation_crud(self):
        data = {
            "personid": str(self.nid),
            "date": base.today_display(),
            "notes": "Test"
        }
        post = asm3.utils.PostedData(data, "en")
        iid = asm3.person.insert_investigation_from_form(base.get_dbo(), "test", post)
        data["investigationid"] = str(iid)
        asm3.person.update_investigation_from_form(base.get_dbo(), "test", post)
        asm3.person.delete_investigation(base.get_dbo(), "test", iid)

    def test_rota_crud(self):
        data = {
            "person": str(self.nid),
            "startdate": base.today_display(),
            "starttime": "00:00",
            "enddate": base.today_display(),
            "endtime": "00:00",
            "type": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        rid = asm3.person.insert_rota_from_form(base.get_dbo(), "test", post)
        data["rotaid"] = str(rid)
        asm3.person.update_rota_from_form(base.get_dbo(), "test", post)
        asm3.person.delete_rota(base.get_dbo(), "test", rid)

    def test_update_pass_homecheck(self):
        asm3.person.update_pass_homecheck(base.get_dbo(), "test", self.nid, "")

    def test_update_check_flags(self):
        asm3.person.update_check_flags(base.get_dbo())

    def test_update_missing_geocodes(self):
        asm3.person.update_missing_geocodes(base.get_dbo())

    def test_update_lookingfor_report(self):
        asm3.person.update_lookingfor_report(base.get_dbo())

    def test_remove_people_only_cancelled_reserve(self):
        asm3.person.remove_people_only_cancelled_reserve(base.get_dbo(), years=1)

    def test_update_anonymise_personal_data(self):
        asm3.person.update_anonymise_personal_data(base.get_dbo(), years=1)

