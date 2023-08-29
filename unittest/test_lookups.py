
import unittest
import base

import asm3.lookups

class TestLookups(unittest.TestCase):
 
    def test_message_crud(self):
        mid = asm3.lookups.add_message(base.get_dbo(), "test", "", "Test")
        self.assertNotEqual(0, len(asm3.lookups.get_messages(base.get_dbo(), "test", "", 0)))
        asm3.lookups.delete_message(base.get_dbo(), mid)

    def test_insert_update_lookup(self):
        nid = asm3.lookups.insert_lookup(base.get_dbo(), "test", "breed", "Test")
        asm3.lookups.update_lookup(base.get_dbo(), "test", nid, "breed", "Test")
        asm3.lookups.delete_lookup(base.get_dbo(), "test", "breed", nid)
        nid = asm3.lookups.insert_lookup(base.get_dbo(), "test", "species", "Test")
        asm3.lookups.update_lookup(base.get_dbo(), "test", nid, "species", "Test")
        asm3.lookups.delete_lookup(base.get_dbo(), "test", "species", nid)
        nid = asm3.lookups.insert_lookup(base.get_dbo(), "test", "vaccinationtype", "Test")
        asm3.lookups.update_lookup(base.get_dbo(), "test", nid, "vaccinationtype", "Test")
        asm3.lookups.delete_lookup(base.get_dbo(), "test", "vaccinationtype", nid)
             
    def test_get(self):
        self.assertNotEqual(0, len(asm3.lookups.get_account_types(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_additionalfield_links(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_additionalfield_types(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_animal_types(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_basecolours(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_breeds(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_breeds_by_species(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_citation_types(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_coattypes(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_costtypes(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_deathreasons(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_diets(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_donation_frequencies(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_donation_types(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_entryreasons(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_incident_completed_types(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_incident_types(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_internal_locations(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_licence_types(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_log_types(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_movement_types(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_payment_methods(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_posneg(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_sexes(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_species(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_sizes(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_trap_types(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_urgencies(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_test_types(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_test_results(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_transport_statuses(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_transport_types(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_vaccination_types(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_voucher_types(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_yesno(base.get_dbo())))
        self.assertNotEqual(0, len(asm3.lookups.get_ynun(base.get_dbo())))
        asm3.lookups.get_animal_flags(base.get_dbo())
        asm3.lookups.get_person_flags(base.get_dbo())

