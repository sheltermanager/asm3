#!/usr/bin/python env

import unittest
import base

import lookups

class TestLookups(unittest.TestCase):
 
    def test_message_crud(self):
        mid = lookups.add_message(base.get_dbo(), "test", "", "Test")
        assert lookups.get_messages(base.get_dbo(), "test", "", 0)
        lookups.delete_message(base.get_dbo(), mid)

    def test_insert_update_lookup(self):
        nid = lookups.insert_lookup(base.get_dbo(), "breed", "Test")
        lookups.update_lookup(base.get_dbo(), nid, "breed", "Test")
        lookups.delete_lookup(base.get_dbo(), "breed", nid)
        nid = lookups.insert_lookup(base.get_dbo(), "species", "Test")
        lookups.update_lookup(base.get_dbo(), nid, "species", "Test")
        lookups.delete_lookup(base.get_dbo(), "species", nid)
        nid = lookups.insert_lookup(base.get_dbo(), "vaccinationtype", "Test")
        lookups.update_lookup(base.get_dbo(), nid, "vaccinationtype", "Test")
        lookups.delete_lookup(base.get_dbo(), "vaccinationtype", nid)
             
    def test_get(self):
        assert lookups.get_account_types(base.get_dbo()) > 0
        assert lookups.get_additionalfield_links(base.get_dbo()) > 0
        assert lookups.get_additionalfield_types(base.get_dbo()) > 0
        assert lookups.get_animal_types(base.get_dbo()) > 0
        assert lookups.get_basecolours(base.get_dbo()) > 0
        assert lookups.get_breeds(base.get_dbo()) > 0
        assert lookups.get_breeds_by_species(base.get_dbo()) > 0
        assert lookups.get_citation_types(base.get_dbo()) > 0
        assert lookups.get_coattypes(base.get_dbo()) > 0
        assert lookups.get_costtypes(base.get_dbo()) > 0
        assert lookups.get_deathreasons(base.get_dbo()) > 0
        assert lookups.get_diets(base.get_dbo()) > 0
        assert lookups.get_donation_frequencies(base.get_dbo()) > 0
        assert lookups.get_donation_types(base.get_dbo()) > 0
        assert lookups.get_entryreasons(base.get_dbo()) > 0
        assert lookups.get_incident_completed_types(base.get_dbo()) > 0
        assert lookups.get_incident_types(base.get_dbo()) > 0
        assert lookups.get_internal_locations(base.get_dbo()) > 0
        assert lookups.get_licence_types(base.get_dbo()) > 0
        assert lookups.get_log_types(base.get_dbo()) > 0
        assert lookups.get_movement_types(base.get_dbo()) > 0
        assert lookups.get_payment_types(base.get_dbo()) > 0
        assert lookups.get_person_flags(base.get_dbo()) > 0
        assert lookups.get_posneg(base.get_dbo()) > 0
        assert lookups.get_sexes(base.get_dbo()) > 0
        assert lookups.get_species(base.get_dbo()) > 0
        assert lookups.get_sizes(base.get_dbo()) > 0
        assert lookups.get_trap_types(base.get_dbo()) > 0
        assert lookups.get_urgencies(base.get_dbo()) > 0
        assert lookups.get_test_types(base.get_dbo()) > 0
        assert lookups.get_test_results(base.get_dbo()) > 0
        assert lookups.get_vaccination_types(base.get_dbo()) > 0
        assert lookups.get_voucher_types(base.get_dbo()) > 0
        assert lookups.get_yesno(base.get_dbo()) > 0
        assert lookups.get_ynun(base.get_dbo()) > 0

