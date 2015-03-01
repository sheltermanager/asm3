#!/usr/bin/python env

import unittest
import base

import additional
import utils

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
        post = utils.PostedData(data, "en")
        self.nid = additional.insert_field_from_form(base.get_dbo(), "test", post)

    def tearDown(self):
        additional.delete_field(base.get_dbo(), "test", self.nid)
 
    def test_clause_for_linktype(self):
        assert "0" in additional.clause_for_linktype("animal")

    def test_get_additional_fields(self):
        additional.get_additional_fields(base.get_dbo(), 1, "animal")

    def test_get_additional_fields_ids(self):
        additional.get_additional_fields_ids(base.get_dbo(), [], "animal")

    def test_get_field_definitions(self):
        assert len(additional.get_field_definitions(base.get_dbo(), "animal")) > 0

    def test_get_fields(self):
        assert len(additional.get_fields(base.get_dbo())) > 0

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
        post = utils.PostedData(data, "en")
        nid = additional.insert_field_from_form(base.get_dbo(), "test", post)
        additional.delete_field(base.get_dbo(), "test", nid)

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
        post = utils.PostedData(data, "en")
        additional.update_field_from_form(base.get_dbo(), "test", post)

    def test_delete_values_for_link(self):
        additional.delete_values_for_link(base.get_dbo(), 0, "animal")

    def test_save_values_for_link(self):
        additional.save_values_for_link(base.get_dbo(), utils.PostedData({}, "en"), 0, "animal")

