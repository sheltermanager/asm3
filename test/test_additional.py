
import unittest
import base

import asm3.additional
import asm3.utils

class TestAdditional(unittest.TestCase):
 
    nid = 0

    def setUp(self):
        data = {
            "name":   "addname",
            "label":  "addlabel",
            "tooltip": "addtooltip",
            "lookupvalues": "",
            "mandatory": "off",
            "type": "0",
            "link": "0",
            "displayindex": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        self.nid = asm3.additional.insert_field_from_form(base.get_dbo(), "test", post)

    def tearDown(self):
        asm3.additional.delete_field(base.get_dbo(), "test", self.nid)
 
    def test_clause_for_linktype(self):
        assert "0" in asm3.additional.clause_for_linktype("animal")

    def test_get_additional_fields(self):
        asm3.additional.get_additional_fields(base.get_dbo(), 1, "animal")

    def test_get_additional_fields_ids(self):
        asm3.additional.get_additional_fields_ids(base.get_dbo(), [], "animal")

    def test_get_field_definitions(self):
        assert len(asm3.additional.get_field_definitions(base.get_dbo(), "animal")) > 0

    def test_get_fields(self):
        assert len(asm3.additional.get_fields(base.get_dbo())) > 0

    def test_insert_field_from_form(self):
        data = {
            "name":   "addname",
            "label":  "addlabel",
            "tooltip": "addtooltip",
            "lookupvalues": "",
            "mandatory": "off",
            "type": "0",
            "link": "0",
            "displayindex": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        nid = asm3.additional.insert_field_from_form(base.get_dbo(), "test", post)
        asm3.additional.delete_field(base.get_dbo(), "test", nid)

    def test_update_field_from_form(self):
        data = {
            "id": self.nid,
            "name":   "chgname",
            "label":  "chglabel",
            "tooltip": "chgtooltip",
            "lookupvalues": "",
            "mandatory": "off",
            "type": "0",
            "link": "0",
            "displayindex": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        asm3.additional.update_field_from_form(base.get_dbo(), "test", post)

    def test_save_values_for_link(self):
        asm3.additional.save_values_for_link(base.get_dbo(), asm3.utils.PostedData({}, "en"), "test", 0, "animal")

    def test_merge_values_for_link(self):
        asm3.additional.merge_values_for_link(base.get_dbo(), asm3.utils.PostedData({}, "en"), "test", 0, "animal")

