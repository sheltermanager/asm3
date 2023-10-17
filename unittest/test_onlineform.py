
import unittest
import base

import asm3.onlineform
import asm3.utils

class TestOnlineForm(unittest.TestCase):

    nformid = 0
    nfieldid = 0
    collationid = 0

    def setUp(self):
        data = {
            "name": "Test Form",
            "header": "HEADER",
            "footer": "FOOTER"
        }
        post = asm3.utils.PostedData(data, "en")
        self.nformid = asm3.onlineform.insert_onlineform_from_form(base.get_dbo(), "test", post)
        data = {
            "fieldname": "testfield",
            "formid":    str(self.nformid),
            "fieldtype": "1", # TEXT
            "label":     "Test Field",
            "displayindex": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        self.nfieldid = asm3.onlineform.insert_onlineformfield_from_form(base.get_dbo(), "test", post)
        data = {
            "formname":     "Test Form",
            "testfield_%s" % self.nfieldid: "Test Value"
        }
        post = asm3.utils.PostedData(data, "en")
        self.collationid = asm3.onlineform.insert_onlineformincoming_from_form(base.get_dbo(), post, "0.0.0.0", "FAKE UA")
        data = {
            "formname":     "Test Form",
            "surname": "Test",
            "animalname": "UnitTestAnimal",
            "callnotes": "Test",
            "dispatchaddress": "Test",
            "markings": "Test",
            "arealost": "Test",
            "areafound": "Test",
            "pickupdate": "10/10/2021",
            "dropoffdate": "10/10/2021",
            "description": "Test"
        }
        post = asm3.utils.PostedData(data, "en")
        self.createcollationid = asm3.onlineform.insert_onlineformincoming_from_form(base.get_dbo(), post, "0.0.0.0", "FAKE UA")

    def tearDown(self):
        asm3.onlineform.delete_onlineform(base.get_dbo(), "test", self.nformid)
        asm3.onlineform.delete_onlineformincoming(base.get_dbo(), "test", self.collationid)

    def test_get_animal_id_from_field(self):
        asm3.onlineform.get_animal_id_from_field(base.get_dbo(), "Test::Test")

    def test_get_onlineform(self):
        self.assertIsNotNone(asm3.onlineform.get_onlineform(base.get_dbo(), self.nformid))

    def test_get_onlineforms(self):
        self.assertNotEqual(0, len(asm3.onlineform.get_onlineforms(base.get_dbo())))

    def test_get_onlineform_html(self):
        self.assertNotEqual("", asm3.onlineform.get_onlineform_html(base.get_dbo(), self.nformid))

    def test_get_onlineform_json(self):
        self.assertNotEqual("", asm3.onlineform.get_onlineform_json(base.get_dbo(), self.nformid))

    def test_get_onlineform_name(self):
        self.assertNotEqual("", asm3.onlineform.get_onlineform_name(base.get_dbo(), self.nformid))

    def test_get_onlineformfields(self):
        self.assertNotEqual(0, len(asm3.onlineform.get_onlineformfields(base.get_dbo(), self.nformid)))

    def test_get_onlineformincoming_formheader(self):
        asm3.onlineform.get_onlineformincoming_formheader(base.get_dbo(), self.nformid)

    def test_get_onlineformincoming_formfooter(self):
        asm3.onlineform.get_onlineformincoming_formfooter(base.get_dbo(), self.nformid)

    def test_get_onlineformincoming_headers(self):
        self.assertNotEqual(0, len(asm3.onlineform.get_onlineformincoming_headers(base.get_dbo())))

    def test_get_onlineformincoming_detail(self):
        self.assertNotEqual(0, len(asm3.onlineform.get_onlineformincoming_detail(base.get_dbo(), self.collationid)))

    def test_get_onlineformincoming_html(self):
        self.assertNotEqual("", asm3.onlineform.get_onlineformincoming_html(base.get_dbo(), self.collationid))

    def test_get_onlineformincoming_plain(self):
        self.assertNotEqual("", asm3.onlineform.get_onlineformincoming_plain(base.get_dbo(), self.collationid))

    def test_get_onlineformincoming_html_print(self):
        self.assertNotEqual("", asm3.onlineform.get_onlineformincoming_html_print(base.get_dbo(), [self.collationid]))

    def test_get_onlineformincoming_name(self):
        self.assertNotEqual("", asm3.onlineform.get_onlineformincoming_name(base.get_dbo(), self.collationid))

    def test_auto_remove_old_incoming_forms(self):
        asm3.onlineform.auto_remove_old_incoming_forms(base.get_dbo())

    def test_create_animal(self):
        asm3.onlineform.create_animal(base.get_dbo(), "test", self.createcollationid)

    def test_create_animalcontrol(self):
        asm3.onlineform.create_animalcontrol(base.get_dbo(), "test", self.createcollationid)

    def test_create_foundanimal(self):
        asm3.onlineform.create_foundanimal(base.get_dbo(), "test", self.createcollationid)

    def test_create_lostanimal(self):
        asm3.onlineform.create_lostanimal(base.get_dbo(), "test", self.createcollationid)

    def test_create_person(self):
        asm3.onlineform.create_person(base.get_dbo(), "test", self.createcollationid)

    def test_create_transport(self):
        asm3.onlineform.create_transport(base.get_dbo(), "test", self.createcollationid)

    def test_create_waitinglist(self):
        asm3.onlineform.create_waitinglist(base.get_dbo(), "test", self.createcollationid)






