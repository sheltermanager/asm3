
import unittest
import base

import asm3.animal, asm3.medical
import asm3.utils

class TestMedical(unittest.TestCase):

    def test_calendar_event_calls(self):
        asm3.medical.get_vaccinations_two_dates(base.get_dbo(), base.today(), base.today())
        asm3.medical.get_vaccinations_expiring_two_dates(base.get_dbo(), base.today(), base.today())
        asm3.medical.get_tests_two_dates(base.get_dbo(), base.today(), base.today())
        asm3.medical.get_treatments_two_dates(base.get_dbo(), base.today(), base.today())

    def test_get_vaccinations(self):
        asm3.medical.get_vaccinations(base.get_dbo(), 1)

    def test_get_vaccinated(self):
        asm3.medical.get_vaccinated(base.get_dbo(), 1)

    def test_get_batch_for_vaccination_types(self):
        asm3.medical.get_batch_for_vaccination_types(base.get_dbo())

    def test_get_regimen_id(self):
        asm3.medical.get_regimen_id(base.get_dbo(), 1)

    def test_get_regimens(self):
        asm3.medical.get_regimens(base.get_dbo(), 1)

    def test_get_regimens_ids(self):
        asm3.medical.get_regimens_ids(base.get_dbo(), [1])

    def test_get_regimens_treatments(self):
        asm3.medical.get_regimens_treatments(base.get_dbo(), 1)

    def test_get_medical_export(self):
        asm3.medical.get_medical_export(base.get_dbo())

    def test_get_profiles(self):
        asm3.medical.get_profiles(base.get_dbo())

    def test_get_tests(self):
        asm3.medical.get_tests(base.get_dbo(), 1)

    def test_get_vaccinations_outstanding(self):
        asm3.medical.get_vaccinations_outstanding(base.get_dbo(), offset="m31")
        asm3.medical.get_vaccinations_outstanding(base.get_dbo(), offset="p31")
        asm3.medical.get_vaccinations_outstanding(base.get_dbo(), offset="xm31")
        asm3.medical.get_vaccinations_outstanding(base.get_dbo(), offset="xp31")
        asm3.medical.get_vaccinations_outstanding(base.get_dbo(), offset="g7")

    def test_get_vacc_manufacturers(self):
        asm3.medical.get_vacc_manufacturers(base.get_dbo())

    def test_get_tests_outstanding(self):
        asm3.medical.get_tests_outstanding(base.get_dbo(), offset="m31")
        asm3.medical.get_tests_outstanding(base.get_dbo(), offset="p31")
        asm3.medical.get_tests_outstanding(base.get_dbo(), offset="g7")

    def test_get_treatments_outstanding(self):
        asm3.medical.get_treatments_outstanding(base.get_dbo(), offset="m31")
        asm3.medical.get_treatments_outstanding(base.get_dbo(), offset="p31")
        asm3.medical.get_treatments_outstanding(base.get_dbo(), offset="g7")

    def test_get_combined_due(self):
        asm3.medical.get_combined_due(base.get_dbo(), 0, None, None)

    def test_update_test_today(self):
        asm3.medical.update_test_today(base.get_dbo(), "test", 0, 0)

    def test_update_vaccination_today(self):
        asm3.medical.update_vaccination_today(base.get_dbo(), "test", 0)

    def test_calculate_given_remaining(self):
        asm3.medical.calculate_given_remaining(base.get_dbo(), 0)
       
    def test_regimen_crud(self):
        data = {
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        aid, code = asm3.animal.insert_animal_from_form(base.get_dbo(), post, "test")
        data = {
            "startdate": base.today_display(),
            "treatmentname": "Test",
            "dosage": "Test",
            "timingrule": "1",
            "timingrulenofrequencies": "1",
            "timingrulefrequency": "1",
            "totalnumberoftreatments": "1",
            "treatmentrule": "1",
            "singlemulti": "1"
        }
        post = asm3.utils.PostedData(data, "en")   
        mid = asm3.medical.insert_regimen_from_form(base.get_dbo(), "test", post)
        asm3.medical.update_regimen_from_form(base.get_dbo(), "test", post)
        asm3.medical.delete_regimen(base.get_dbo(), "test", mid)
        asm3.animal.delete_animal(base.get_dbo(), "test", aid)

    def test_vaccination_crud(self):
        data = {
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        aid, code = asm3.animal.insert_animal_from_form(base.get_dbo(), post, "test")
        data = {
            "animal": str(aid),
            "required": base.today_display(),
            "type": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        vid = asm3.medical.insert_vaccination_from_form(base.get_dbo(), "test", post)
        asm3.medical.update_vaccination_from_form(base.get_dbo(), "test", post)
        asm3.medical.delete_regimen(base.get_dbo(), "test", vid)
        asm3.animal.delete_animal(base.get_dbo(), "test", aid)

    def test_test_crud(self):
        data = {
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        aid, code = asm3.animal.insert_animal_from_form(base.get_dbo(), post, "test")
        data = {
            "animal": str(aid),
            "required": base.today_display(),
            "type": "1",
            "result": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        tid = asm3.medical.insert_test_from_form(base.get_dbo(), "test", post)
        post.data["testid"] = str(tid)
        asm3.medical.update_test_from_form(base.get_dbo(), "test", post)
        asm3.medical.delete_test(base.get_dbo(), "test", tid)
        asm3.animal.delete_animal(base.get_dbo(), "test", aid)

    def test_profile_crud(self):
        data = {
            "profilename": "Test", 
            "treatmentname": "Test",
            "dosage": "Test",
            "timingrule": "1",
            "timingrulenofrequencies": "1",
            "timingrulefrequency": "1",
            "totalnumberoftreatments": "1",
            "treatmentrule": "1",
            "singlemulti": "1"
        }
        post = asm3.utils.PostedData(data, "en")   
        mid = asm3.medical.insert_profile_from_form(base.get_dbo(), "test", post)
        asm3.medical.update_profile_from_form(base.get_dbo(), "test", post)
        asm3.medical.delete_profile(base.get_dbo(), "test", mid)

