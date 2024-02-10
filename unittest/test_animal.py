
import unittest
import base

import asm3.animal
import asm3.utils

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
        post = asm3.utils.PostedData(data, "en")
        self.nid, self.code = asm3.animal.insert_animal_from_form(base.get_dbo(), post, "test")

    def tearDown(self):
        asm3.animal.delete_animal(base.get_dbo(), "test", self.nid)

    def test_get_animal(self):
        self.assertIsNotNone(asm3.animal.get_animal(base.get_dbo(), self.nid))

    def test_get_animal_entries(self):
        asm3.animal.get_animal_entries(base.get_dbo(), self.nid)

    def test_insert_animal_entry(self):
        self.assertNotEqual(0, asm3.animal.insert_animal_entry(base.get_dbo(), "system", self.nid))

    def test_get_animals_brief(self):
        asm3.animal.get_animals_brief([asm3.animal.get_animal(base.get_dbo(), self.nid),])

    def test_get_animal_find_simple(self):
        self.assertNotEqual(0, len(asm3.animal.get_animal_find_simple(base.get_dbo(), "Testio")))

    def test_get_animal_find_advanced(self):
        self.assertNotEqual(0, len(asm3.animal.get_animal_find_advanced(base.get_dbo(), { "animalname": "Testio" })))

    def test_get_animals_flag(self):
        asm3.animal.get_animals_long_term(base.get_dbo())
        asm3.animal.get_animals_never_vacc(base.get_dbo())
        asm3.animal.get_animals_no_rabies(base.get_dbo())
        asm3.animal.get_animals_not_for_adoption(base.get_dbo())
        asm3.animal.get_animals_not_microchipped(base.get_dbo())
        asm3.animal.get_animals_hold(base.get_dbo())
        asm3.animal.get_animals_hold_today(base.get_dbo())
        asm3.animal.get_animals_quarantine(base.get_dbo())
        asm3.animal.get_animals_recently_deceased(base.get_dbo())

    def test_get_alerts(self):
        self.assertNotEqual(0, len(asm3.animal.get_alerts(base.get_dbo())))

    def test_get_stats(self):
        self.assertNotEqual(0, len(asm3.animal.get_stats(base.get_dbo())))

    def test_calc_fields(self):
        self.assertIsNotNone(asm3.animal.calc_time_on_shelter(base.get_dbo(), self.nid))
        self.assertIsNotNone(asm3.animal.calc_days_on_shelter(base.get_dbo(), self.nid))
        self.assertIsNotNone(asm3.animal.calc_age_group(base.get_dbo(), self.nid))
        self.assertIsNotNone(asm3.animal.calc_age(base.get_dbo(), self.nid))

    def test_get_fields(self):
        self.assertTrue(asm3.animal.get_is_on_shelter(base.get_dbo(), self.nid))
        self.assertTrue(asm3.animal.get_animal_id_and_bonds(base.get_dbo(), self.nid)[0] == self.nid)
        asm3.animal.get_comments(base.get_dbo(), self.nid)
        asm3.animal.get_date_of_birth(base.get_dbo(), self.nid)
        asm3.animal.get_days_on_shelter(base.get_dbo(), self.nid)
        asm3.animal.get_daily_boarding_cost(base.get_dbo(), self.nid)
        asm3.animal.get_deceased_date(base.get_dbo(), self.nid)
        asm3.animal.get_date_brought_in(base.get_dbo(), self.nid)
        asm3.animal.get_display_location(base.get_dbo(), self.nid)
        asm3.animal.get_display_location_noq(base.get_dbo(), self.nid)
        asm3.animal.get_code(base.get_dbo(), self.nid)
        asm3.animal.get_short_code(base.get_dbo(), self.nid)
        asm3.animal.get_shelter_code(base.get_dbo(), self.nid)
        asm3.animal.get_animal_name(base.get_dbo(), self.nid)
        asm3.animal.get_animal_namecode(base.get_dbo(), self.nid)
        self.assertNotEqual(0, len(asm3.animal.get_recent_changes(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.animal.get_shelter_animals(base.get_dbo())))
        self.assertNotEqual(0, asm3.animal.get_number_animals_on_shelter_now(base.get_dbo()))
        self.assertTrue(asm3.animal.get_has_animals(base.get_dbo()))
        self.assertTrue(asm3.animal.get_has_animal_on_shelter(base.get_dbo()))
        asm3.animal.get_animals_owned_by(base.get_dbo(), 1)

    def test_get_animals_namecode(self):
        self.assertNotEqual(0, len(asm3.animal.get_animals_namecode(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.animal.get_animals_on_shelter_namecode(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.animal.get_animals_on_shelter_foster_namecode(base.get_dbo())))

    def test_get_breedname(self):
        self.assertNotEqual(asm3.animal.get_breedname(base.get_dbo(), 1, 2).find("/"), -1)
        self.assertEqual(asm3.animal.get_breedname(base.get_dbo(), 1, 1).find("/"), -1)

    def test_get_costs(self):
        asm3.animal.get_costs(base.get_dbo(), self.nid)

    def test_get_cost_totals(self):
        self.assertNotEqual(0, len(asm3.animal.get_cost_totals(base.get_dbo(), self.nid)))

    def test_get_diets(self):
        asm3.animal.get_diets(base.get_dbo(), self.nid)

    def test_get_links(self):
        asm3.animal.get_links_adoptable(base.get_dbo())
        asm3.animal.get_links_recently_adopted(base.get_dbo())
        asm3.animal.get_links_recently_fostered(base.get_dbo())
        asm3.animal.get_links_recently_changed(base.get_dbo())
        asm3.animal.get_links_recently_entered(base.get_dbo())
        asm3.animal.get_links_longest_on_shelter(base.get_dbo())

    def test_get_active_litters(self):
        asm3.animal.get_active_litters(base.get_dbo())
        asm3.animal.update_active_litters(base.get_dbo())

    def test_get_publish_history(self):
        asm3.animal.get_publish_history(base.get_dbo(), self.nid)

    def test_insert_publish_history(self):
        asm3.animal.insert_publish_history(base.get_dbo(), self.nid, "fakeservice")

    def test_get_satellite_counts(self):
        self.assertNotEqual(0, len(asm3.animal.get_satellite_counts(base.get_dbo(), self.nid)))

    def test_get_random_name(self):
        self.assertNotEqual(asm3.animal.get_random_name(base.get_dbo()), "")

    def test_get_recent_with_name(self):
        self.assertNotEqual(0, len(asm3.animal.get_recent_with_name(base.get_dbo(), "Testio")))

    def test_get_shelterview_animals(self):
        self.assertNotEqual(0, len(asm3.animal.get_shelterview_animals(base.get_dbo())))

    def test_get_signed_requests(self):
        asm3.animal.get_signed_requests(base.get_dbo())

    def test_get_unsigned_requests(self):
        asm3.animal.get_unsigned_requests(base.get_dbo())

    def test_get_timeline(self):
        self.assertNotEqual(0, len(asm3.animal.get_timeline(base.get_dbo())))

    def test_get_units_with_availability(self):
        asm3.animal.get_units_with_availability(base.get_dbo(), 1);

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
        post = asm3.utils.PostedData(data, "en")
        asm3.animal.update_animal_from_form(base.get_dbo(), post, "test")

    def test_update_flags(self):
        asm3.animal.update_flags(base.get_dbo(), "test", self.nid, "courtesy")

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
            "housetrained": "1",
            "movementtype": "-1"
        }
        post = asm3.utils.PostedData(data, "en")
        asm3.animal.update_animals_from_form(base.get_dbo(), "test", post)

    def test_update_deceased_from_form(self):
        asm3.animal.update_deceased_from_form(base.get_dbo(), "test", asm3.utils.PostedData({ "animal": self.nid }, "en"))

    def test_update_location_unit(self):
        asm3.animal.update_location_unit(base.get_dbo(), "test", self.nid, 1)

    def test_clone_animal(self):
        nid = asm3.animal.clone_animal(base.get_dbo(), "test", self.nid)
        self.assertNotEqual(nid, 0)
        asm3.animal.delete_animal(base.get_dbo(), "test", nid)

    def test_clone_from_template(self):
        asm3.animal.clone_from_template(base.get_dbo(), "test", self.nid, base.today(), base.today(), 1, 1, 0)

    def test_merge_animal(self):
        cid = asm3.animal.clone_animal(base.get_dbo(), "test", self.nid)
        self.assertNotEqual(cid, 0)
        asm3.animal.merge_animal(base.get_dbo(), "test", self.nid, cid)

    def test_extra_ids(self):
        a = asm3.animal.get_animal(base.get_dbo(), self.nid)
        asm3.animal.set_extra_id(base.get_dbo(), "user", a, "test", "xxx")
        self.assertEqual("xxx", asm3.animal.get_extra_id(base.get_dbo(), a, "test"))

    def test_update_current_owner(self):
        asm3.animal.update_current_owner(base.get_dbo(), "test", self.nid)

    def test_update_daily_boarding_cost(self):
        asm3.animal.update_daily_boarding_cost(base.get_dbo(), "test", self.nid, 1500)

    def test_update_preferred_web_media_notes(self):
        asm3.animal.update_preferred_web_media_notes(base.get_dbo(), "test", self.nid, "test")

    def test_insert_diet_from_form(self):
        data = {
            "animalid": self.nid,
            "type": "1",
            "startdate": base.today_display()
        }
        post = asm3.utils.PostedData(data, "en")
        nid = asm3.animal.insert_diet_from_form(base.get_dbo(), "test", post)
        asm3.animal.delete_diet(base.get_dbo(), "test", nid)

    def test_update_diet_from_form(self):
        data = {
            "animalid": self.nid,
            "type": "1",
            "startdate": base.today_display()
        }
        post = asm3.utils.PostedData(data, "en")
        asm3.animal.update_diet_from_form(base.get_dbo(), "test", post)

    def test_insert_cost_from_form(self):
        data = {
            "animalid": self.nid,
            "type": "1",
            "costdate": base.today_display(),
            "cost": "2000"
        }
        post = asm3.utils.PostedData(data, "en")
        nid = asm3.animal.insert_cost_from_form(base.get_dbo(), "test", post)
        asm3.animal.delete_cost(base.get_dbo(), "test", nid)

    def test_update_cost_from_form(self):
        data = {
            "animalid": self.nid,
            "type": "1",
            "costdate": base.today_display(),
            "cost": "2000"
        }
        post = asm3.utils.PostedData(data, "en")
        asm3.animal.update_cost_from_form(base.get_dbo(), "test", post)

    def test_insert_litter_from_form(self):
        data = {
            "animal": self.nid,
            "species": "1",
            "startdate": base.today_display(),
            "litterref": "RUBBISH"
        }
        post = asm3.utils.PostedData(data, "en")
        nid = asm3.animal.insert_litter_from_form(base.get_dbo(), "test", post)
        asm3.animal.delete_litter(base.get_dbo(), "test", nid)

    def test_update_litter_from_form(self):
        data = {
            "animal": self.nid,
            "species": "1",
            "startdate": base.today_display(),
            "litterref": "RUBBISH"
        }
        post = asm3.utils.PostedData(data, "en")
        asm3.animal.update_litter_from_form(base.get_dbo(), "test", post)

    def test_update_all_variable_animal_data(self):
        base.execute("DELETE FROM configuration WHERE ItemName LIKE 'VariableAnimalDataUpdated'")
        asm3.animal.update_all_variable_animal_data(base.get_dbo())

    def test_update_foster_variable_animal_data(self):
        asm3.animal.update_foster_variable_animal_data(base.get_dbo())

    def test_update_on_shelter_variable_animal_data(self):
        asm3.animal.update_on_shelter_variable_animal_data(base.get_dbo())

    def test_update_all_animal_statuses(self):
        asm3.animal.update_all_animal_statuses(base.get_dbo())

    def test_update_boarding_animal_statuses(self):
        asm3.animal.update_boarding_animal_statuses(base.get_dbo())

    def test_update_foster_animal_statuses(self):
        asm3.animal.update_foster_animal_statuses(base.get_dbo())

    def test_update_on_shelter_animal_statuses(self):
        asm3.animal.update_on_shelter_animal_statuses(base.get_dbo())

    def test_update_animal_breeds(self):
        asm3.animal.update_animal_breeds(base.get_dbo())

    def test_update_animal_check_bonds(self):
        asm3.animal.update_animal_check_bonds(base.get_dbo(), self.nid)

    def test_is_animal_in_location_filter(self):
        a = asm3.animal.get_animal(base.get_dbo(), self.nid)
        a.siteid = 2 # site test
        self.assertTrue(asm3.animal.is_animal_in_location_filter(a, "", 2, ""))
        self.assertFalse(asm3.animal.is_animal_in_location_filter(a, "", 3, ""))
        a.activemovementtype = None
        a.shelterlocation = 3 # shelter locations
        self.assertTrue(asm3.animal.is_animal_in_location_filter(a, "3", 0, ""))
        self.assertFalse(asm3.animal.is_animal_in_location_filter(a, "4", 0, ""))
        a.activemovementtype = 1 # trials
        self.assertTrue(asm3.animal.is_animal_in_location_filter(a, "-1", 0, ""))
        self.assertFalse(asm3.animal.is_animal_in_location_filter(a, "-2", 0, ""))
        a.activemovementtype = 2 # fosters
        self.assertTrue(asm3.animal.is_animal_in_location_filter(a, "-2", 0, ""))
        self.assertFalse(asm3.animal.is_animal_in_location_filter(a, "-1", 0, ""))
        a.activemovementtype = 8 # retailers
        self.assertTrue(asm3.animal.is_animal_in_location_filter(a, "-8", 0, ""))
        self.assertFalse(asm3.animal.is_animal_in_location_filter(a, "-2", 0, ""))
        a.activemovementtype = None
        a.nonshelteranimal = 1 # nonshelters
        self.assertTrue(asm3.animal.is_animal_in_location_filter(a, "-9", 0, ""))
        self.assertFalse(asm3.animal.is_animal_in_location_filter(a, "-1", 0, ""))
        # visible animals like "my fosters"
        self.assertTrue(asm3.animal.is_animal_in_location_filter(a, "-12", 0, str(self.nid)))
        self.assertFalse(asm3.animal.is_animal_in_location_filter(a, "-12", 0, ""))

    def test_get_number(self):
        self.assertNotEqual(0, asm3.animal.get_number_animals_on_shelter(base.get_dbo(), base.today(), 1))
        asm3.animal.get_number_litters_on_shelter(base.get_dbo(), base.today())
        asm3.animal.get_number_animals_on_foster(base.get_dbo(), base.today(), 1)

    def test_animal_figures(self):
        asm3.animal.update_animal_figures(base.get_dbo())
        asm3.animal.update_animal_figures_annual(base.get_dbo())

    def test_auto_cancel_holds(self):
        asm3.animal.auto_cancel_holds(base.get_dbo())

