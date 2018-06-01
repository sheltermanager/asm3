#!/usr/bin/python env

import unittest
import base

import animal, medical
import utils

class TestMedical(unittest.TestCase):

    def test_calendar_event_calls(self):
        medical.get_vaccinations_two_dates(base.get_dbo(), base.today(), base.today())
        medical.get_vaccinations_expiring_two_dates(base.get_dbo(), base.today(), base.today())
        medical.get_tests_two_dates(base.get_dbo(), base.today(), base.today())
        medical.get_treatments_two_dates(base.get_dbo(), base.today(), base.today())

    def test_get_vaccinations(self):
        medical.get_vaccinations(base.get_dbo(), 1)

    def test_get_vaccinated(self):
        medical.get_vaccinated(base.get_dbo(), 1)

    def test_get_batch_for_vaccination_types(self):
        medical.get_batch_for_vaccination_types(base.get_dbo())

    def test_get_regimens(self):
        medical.get_regimens(base.get_dbo(), 1)

    def test_get_regimens_treatments(self):
        medical.get_regimens_treatments(base.get_dbo(), 1)

    def test_get_medical_export(self):
        medical.get_medical_export(base.get_dbo())

    def test_get_profiles(self):
        medical.get_profiles(base.get_dbo())

    def test_get_tests(self):
        medical.get_tests(base.get_dbo(), 1)

    def test_get_vaccinations_outstanding(self):
        medical.get_vaccinations_outstanding(base.get_dbo())

    def test_get_vacc_manufacturers(self):
        medical.get_vacc_manufacturers(base.get_dbo())

    def test_get_tests_outstanding(self):
        medical.get_tests_outstanding(base.get_dbo())

    def test_get_treatments_outstanding(self):
        medical.get_treatments_outstanding(base.get_dbo())

    def test_update_test_today(self):
        medical.update_test_today(base.get_dbo(), "test", 0, 0)

    def test_update_vaccination_today(self):
        medical.update_vaccination_today(base.get_dbo(), "test", 0)

    def test_calculate_given_remaining(self):
        medical.calculate_given_remaining(base.get_dbo(), 0)
       
    def test_regimen_crud(self):
        data = {
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1"
        }
        post = utils.PostedData(data, "en")
        aid, code = animal.insert_animal_from_form(base.get_dbo(), post, "test")
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
        post = utils.PostedData(data, "en")   
        mid = medical.insert_regimen_from_form(base.get_dbo(), "test", post)
        medical.update_regimen_from_form(base.get_dbo(), "test", post)
        medical.delete_regimen(base.get_dbo(), "test", mid)
        animal.delete_animal(base.get_dbo(), "test", aid)

    def test_vaccination_crud(self):
        data = {
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1"
        }
        post = utils.PostedData(data, "en")
        aid, code = animal.insert_animal_from_form(base.get_dbo(), post, "test")
        data = {
            "animal": str(aid),
            "required": base.today_display(),
            "type": "1"
        }
        post = utils.PostedData(data, "en")
        vid = medical.insert_vaccination_from_form(base.get_dbo(), "test", post)
        medical.update_vaccination_from_form(base.get_dbo(), "test", post)
        medical.delete_regimen(base.get_dbo(), "test", vid)
        animal.delete_animal(base.get_dbo(), "test", aid)

    def test_test_crud(self):
        data = {
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1"
        }
        post = utils.PostedData(data, "en")
        aid, code = animal.insert_animal_from_form(base.get_dbo(), post, "test")
        data = {
            "animal": str(aid),
            "required": base.today_display(),
            "type": "1",
            "result": "1"
        }
        post = utils.PostedData(data, "en")
        tid = medical.insert_test_from_form(base.get_dbo(), "test", post)
        post.data["testid"] = str(tid)
        medical.update_test_from_form(base.get_dbo(), "test", post)
        medical.delete_test(base.get_dbo(), "test", tid)
        animal.delete_animal(base.get_dbo(), "test", aid)

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
        post = utils.PostedData(data, "en")   
        mid = medical.insert_profile_from_form(base.get_dbo(), "test", post)
        medical.update_profile_from_form(base.get_dbo(), "test", post)
        medical.delete_profile(base.get_dbo(), "test", mid)

