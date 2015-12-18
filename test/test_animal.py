#!/usr/bin/python env

import unittest
import base

import animal
import utils

class TestAnimal(unittest.TestCase):
   
    nid = 0

    def setUp(self):
        data = {
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1"
        }
        post = utils.PostedData(data, "en")
        self.nid, self.code = animal.insert_animal_from_form(base.get_dbo(), post, "test")

    def tearDown(self):
        animal.delete_animal(base.get_dbo(), "test", self.nid)

    def test_get_animal(self):
        assert animal.get_animal(base.get_dbo(), self.nid) is not None

    def test_get_animals_brief(self):
        assert animal.get_animals_brief([animal.get_animal(base.get_dbo(), self.nid),])

    def test_get_animal_find_simple(self):
        assert len(animal.get_animal_find_simple(base.get_dbo(), "Testio")) > 0

    def test_get_animal_find_advanced(self):
        assert len(animal.get_animal_find_advanced(base.get_dbo(), { "animalname": "Testio" })) > 0

    def test_get_animals_flag(self):
        animal.get_animals_long_term(base.get_dbo())
        animal.get_animals_not_for_adoption(base.get_dbo())
        animal.get_animals_not_microchipped(base.get_dbo())
        animal.get_animals_hold(base.get_dbo())
        animal.get_animals_quarantine(base.get_dbo())
        animal.get_animals_recently_deceased(base.get_dbo())

    def test_get_alerts(self):
        assert len(animal.get_alerts(base.get_dbo())) > 0

    def test_get_stats(self):
        assert len(animal.get_stats(base.get_dbo())) > 0

    def test_calc_fields(self):
        assert animal.calc_most_recent_entry(base.get_dbo(), self.nid) is not None
        assert animal.calc_time_on_shelter(base.get_dbo(), self.nid) is not None
        assert animal.calc_days_on_shelter(base.get_dbo(), self.nid) is not None
        assert animal.calc_age_group(base.get_dbo(), self.nid) is not None
        assert animal.calc_age(base.get_dbo(), self.nid) is not None

    def test_get_fields(self):
        animal.get_latest_movement(base.get_dbo(), self.nid)
        assert True == animal.get_is_on_shelter(base.get_dbo(), self.nid)
        animal.get_comments(base.get_dbo(), self.nid)
        animal.get_date_of_birth(base.get_dbo(), self.nid)
        animal.get_days_on_shelter(base.get_dbo(), self.nid)
        animal.get_daily_boarding_cost(base.get_dbo(), self.nid)
        animal.get_deceased_date(base.get_dbo(), self.nid)
        animal.get_date_brought_in(base.get_dbo(), self.nid)
        animal.get_display_location(base.get_dbo(), self.nid)
        animal.get_display_location_noq(base.get_dbo(), self.nid)
        animal.get_code(base.get_dbo(), self.nid)
        animal.get_short_code(base.get_dbo(), self.nid)
        animal.get_shelter_code(base.get_dbo(), self.nid)
        animal.get_animal_namecode(base.get_dbo(), self.nid)
        assert animal.get_number_animals_on_shelter_now(base.get_dbo()) > 0
        assert True == animal.get_has_animals(base.get_dbo())
        assert True == animal.get_has_animal_on_shelter(base.get_dbo())
        animal.get_preferred_web_media_name(base.get_dbo(), self.nid)

    def test_get_animals_namecode(self):
        assert len(animal.get_animals_namecode(base.get_dbo())) > 0
        assert len(animal.get_animals_on_shelter_namecode(base.get_dbo())) > 0
        assert len(animal.get_animals_on_shelter_foster_namecode(base.get_dbo())) > 0

    def test_get_breedname(self):
        assert animal.get_breedname(base.get_dbo(), 1, 2).find("/") != -1
        assert animal.get_breedname(base.get_dbo(), 1, 1).find("/") == -1

    def test_get_costs(self):
        animal.get_costs(base.get_dbo(), self.nid)

    def test_get_cost_totals(self):
        assert len(animal.get_cost_totals(base.get_dbo(), self.nid)) > 0

    def test_get_diets(self):
        animal.get_diets(base.get_dbo(), self.nid)

    def test_get_links(self):
        animal.get_links_recently_adopted(base.get_dbo())
        animal.get_links_recently_fostered(base.get_dbo())
        animal.get_links_recently_changed(base.get_dbo())
        animal.get_links_recently_entered(base.get_dbo())
        animal.get_links_longest_on_shelter(base.get_dbo())

    def test_get_active_litters(self):
        animal.get_active_litters(base.get_dbo())
        animal.update_active_litters(base.get_dbo())

    def test_get_publish_history(self):
        animal.get_publish_history(base.get_dbo(), self.nid)

    def test_insert_publish_history(self):
        animal.insert_publish_history(base.get_dbo(), self.nid, "fakeservice")

    def test_get_satellite_counts(self):
        assert len(animal.get_satellite_counts(base.get_dbo(), self.nid)) > 0

    def test_get_random_name(self):
        assert animal.get_random_name(base.get_dbo()) != ""

    def test_get_recent_with_name(self):
        assert len(animal.get_recent_with_name(base.get_dbo(), "Testio")) > 0

    def test_get_shelterview_animals(self):
        assert len(animal.get_shelterview_animals(base.get_dbo())) > 0

    def test_get_units_with_availability(self):
        animal.get_units_with_availability(base.get_dbo(), 1);

    def test_update_animal_from_form(self):
        data = {
            "id": self.nid,
            "datebroughtin": base.today_display(),
            "dateofbirth": base.today_display(),
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1",
            "sheltercode": "ICHANGED",
            "recordversion": "-1"
        }
        post = utils.PostedData(data, "en")
        animal.update_animal_from_form(base.get_dbo(), post, "test")

    def test_update_animals_from_form(self):
        data = {
            "animals": str(self.nid),
            "litterid": "000",
            "animaltype": "1",
            "location": "1",
            "fee": "1000",
            "notforadoption": "0",
            "goodwithcats": "1",
            "goodwithdogs": "1",
            "goodwithkids": "1",
            "housetrained": "1"
        }
        post = utils.PostedData(data, "en")
        animal.update_animals_from_form(base.get_dbo(), post, "test")

    def test_update_deceased_from_form(self):
        animal.update_deceased_from_form(base.get_dbo(), "test", utils.PostedData({ "animal": self.nid }, "en"))

    def test_update_location_unit(self):
        animal.update_location_unit(base.get_dbo(), "test", self.nid, 1)

    def test_clone_animal(self):
        nid = animal.clone_animal(base.get_dbo(), "test", self.nid)
        assert nid != 0
        animal.delete_animal(base.get_dbo(), "test", nid)

    def test_update_daily_boarding_cost(self):
        animal.update_daily_boarding_cost(base.get_dbo(), "test", self.nid, 1500)

    def test_update_preferred_web_media_notes(self):
        animal.update_preferred_web_media_notes(base.get_dbo(), "test", self.nid, "test")

    def test_insert_diet_from_form(self):
        data = {
            "animalid": self.nid,
            "type": "1",
            "startdate": base.today_display()
        }
        post = utils.PostedData(data, "en")
        nid = animal.insert_diet_from_form(base.get_dbo(), "test", post)
        animal.delete_diet(base.get_dbo(), "test", nid)

    def test_update_diet_from_form(self):
        data = {
            "animalid": self.nid,
            "type": "1",
            "startdate": base.today_display()
        }
        post = utils.PostedData(data, "en")
        animal.update_diet_from_form(base.get_dbo(), "test", post)

    def test_insert_cost_from_form(self):
        data = {
            "animalid": self.nid,
            "type": "1",
            "costdate": base.today_display(),
            "cost": "2000"
        }
        post = utils.PostedData(data, "en")
        nid = animal.insert_cost_from_form(base.get_dbo(), "test", post)
        animal.delete_cost(base.get_dbo(), "test", nid)

    def test_update_cost_from_form(self):
        data = {
            "animalid": self.nid,
            "type": "1",
            "costdate": base.today_display(),
            "cost": "2000"
        }
        post = utils.PostedData(data, "en")
        animal.update_cost_from_form(base.get_dbo(), "test", post)

    def test_insert_litter_from_form(self):
        data = {
            "animal": self.nid,
            "species": "1",
            "startdate": base.today_display(),
            "litterref": "RUBBISH"
        }
        post = utils.PostedData(data, "en")
        nid = animal.insert_litter_from_form(base.get_dbo(), "test", post)
        animal.delete_litter(base.get_dbo(), "test", nid)

    def test_update_litter_from_form(self):
        data = {
            "animal": self.nid,
            "species": "1",
            "startdate": base.today_display(),
            "litterref": "RUBBISH"
        }
        post = utils.PostedData(data, "en")
        animal.update_litter_from_form(base.get_dbo(), "test", post)

    def test_update_all_variable_animal_data(self):
        base.execute("DELETE FROM configuration WHERE ItemName LIKE 'VariableAnimalDataUpdated'")
        animal.update_all_variable_animal_data(base.get_dbo())

    def test_update_all_animal_statuses(self):
        animal.update_all_animal_statuses(base.get_dbo())

    def test_update_foster_animal_statuses(self):
        animal.update_foster_animal_statuses(base.get_dbo())

    def test_update_on_shelter_animal_statuses(self):
        animal.update_on_shelter_animal_statuses(base.get_dbo())

    def test_update_animal_check_bonds(self):
        animal.update_animal_check_bonds(base.get_dbo(), self.nid)

    def test_get_number(self):
        assert animal.get_number_animals_on_shelter(base.get_dbo(), base.today(), 1) > 0
        animal.get_number_litters_on_shelter(base.get_dbo(), base.today())
        animal.get_number_animals_on_foster(base.get_dbo(), base.today(), 1)

    def test_animal_figures(self):
        animal.update_animal_figures(base.get_dbo())
        animal.update_animal_figures_annual(base.get_dbo())
        animal.update_animal_figures_asilomar(base.get_dbo())
        animal.update_animal_figures_monthly_asilomar(base.get_dbo())

    def test_auto_cancel_holds(self):
        animal.auto_cancel_holds(base.get_dbo())

