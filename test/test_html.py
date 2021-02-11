
import datetime, unittest
import base

import asm3.html, asm3.publish

class TestHtml(unittest.TestCase):
 
    def test_escape(self):
        assert asm3.html.escape("'\"><") == "&apos;&quot;&gt;&lt;"

    def test_escape_angle(self):
        assert asm3.html.escape("><") == "&gt;&lt;"

    def test_menu_structure(self):
        assert asm3.html.menu_structure("en", asm3.publish.PUBLISHER_LIST, [], []) is not None

    def test_options(self):
        asm3.html.options_accounts(base.get_dbo())
        asm3.html.options_account_types(base.get_dbo())
        asm3.html.options_additionalfield_links(base.get_dbo())
        asm3.html.options_additionalfield_types(base.get_dbo())
        asm3.html.options_agegroups(base.get_dbo())
        asm3.html.options_animal_flags(base.get_dbo())
        asm3.html.options_animals(base.get_dbo())
        asm3.html.options_animals_on_shelter(base.get_dbo())
        asm3.html.options_animals_on_shelter_foster(base.get_dbo())
        asm3.html.options_animal_types(base.get_dbo())
        asm3.html.options_breeds(base.get_dbo())
        asm3.html.options_coattypes(base.get_dbo())
        asm3.html.options_colours(base.get_dbo())
        asm3.html.options_cost_types(base.get_dbo())
        asm3.html.options_deathreasons(base.get_dbo())
        asm3.html.options_diets(base.get_dbo())
        asm3.html.options_donation_types(base.get_dbo())
        asm3.html.options_donation_frequencies(base.get_dbo())
        asm3.html.options_entryreasons(base.get_dbo())
        asm3.html.options_incident_types(base.get_dbo())
        asm3.html.options_internal_locations(base.get_dbo())
        asm3.html.options_litters(base.get_dbo())
        asm3.html.options_locales()
        asm3.html.options_log_types(base.get_dbo())
        asm3.html.options_medicalprofiles(base.get_dbo())
        asm3.html.options_movement_types(base.get_dbo())
        asm3.html.options_person_flags(base.get_dbo())
        asm3.html.options_people(base.get_dbo())
        asm3.html.options_people_not_homechecked(base.get_dbo())
        asm3.html.options_posneg(base.get_dbo())
        asm3.html.options_species(base.get_dbo())
        asm3.html.options_sexes(base.get_dbo())
        asm3.html.options_sites(base.get_dbo())
        asm3.html.options_sizes(base.get_dbo())
        asm3.html.options_smarttagtypes(base.get_dbo())
        asm3.html.options_urgencies(base.get_dbo())
        asm3.html.options_users(base.get_dbo())
        asm3.html.options_users_and_roles(base.get_dbo())
        asm3.html.options_vaccination_types(base.get_dbo())
        asm3.html.options_voucher_types(base.get_dbo())
        asm3.html.options_yesno(base.get_dbo())
        asm3.html.options_ynun(base.get_dbo())


