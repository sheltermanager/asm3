
import unittest
import base, base64

import asm3.template
import asm3.utils

class TestTemplate(unittest.TestCase):

    def test_get_html_template(self):
        self.assertNotEqual("", asm3.template.get_html_template(base.get_dbo(), "animalview")[0])

    def test_get_html_templates(self):
        self.assertNotEqual(0, len(asm3.template.get_html_templates(base.get_dbo())))

    def test_get_html_template_names(self):
        self.assertNotEqual(0, len(asm3.template.get_html_template_names(base.get_dbo())))

    def test_update_html_template(self):
        asm3.template.update_html_template(base.get_dbo(), "test", "testtemplate", "head", "body", "foot")
        self.assertNotEqual("", asm3.template.get_html_template(base.get_dbo(), "testtemplate")[0])

    def test_delete_html_template(self):
        asm3.template.update_html_template(base.get_dbo(), "test", "testtemplate", "head", "body", "foot")
        asm3.template.delete_html_template(base.get_dbo(), "test", "testtemplate")
        self.assertEqual("", asm3.template.get_html_template(base.get_dbo(), "testtemplate")[0])

    def test_get_document_templates(self):
        self.assertNotEqual(0, len(asm3.template.get_document_templates(base.get_dbo())))

    def test_get_document_templates_defaults(self):
        self.assertNotEqual(0, len(asm3.template.get_document_templates_defaults(base.get_dbo())))

    def test_get_document_template_content(self):
        nid = asm3.template.create_document_template(base.get_dbo(), "test", asm3.utils.uuid_b64())
        self.assertNotEqual("", asm3.template.get_document_template_content(base.get_dbo(), nid))

    def test_get_document_template_name(self):
        nid = asm3.template.create_document_template(base.get_dbo(), "test", asm3.utils.uuid_b64())
        self.assertNotEqual("", asm3.template.get_document_template_name(base.get_dbo(), nid))

    def test_create_document_template(self):
        nid = asm3.template.create_document_template(base.get_dbo(), "test", asm3.utils.uuid_b64())
        self.assertNotEqual(nid, 0)

    def test_clone_document_template(self):
        nid = asm3.template.clone_document_template(base.get_dbo(), "test", 1, asm3.utils.uuid_b64())
        self.assertNotEqual(nid, 0)

    def test_delete_document_template(self):
        nid = asm3.template.create_document_template(base.get_dbo(), "test", asm3.utils.uuid_b64())
        asm3.template.delete_document_template(base.get_dbo(), "test", nid)
        self.assertEqual("", asm3.template.get_document_template_name(base.get_dbo(), nid))

    def test_rename_document_template(self):
        firstname = asm3.utils.uuid_b64()
        secondname = asm3.utils.uuid_b64()
        nid = asm3.template.create_document_template(base.get_dbo(), "test", firstname)
        asm3.template.rename_document_template(base.get_dbo(), "test", nid, secondname)
        self.assertEqual(asm3.template.get_document_template_name(base.get_dbo(), nid), secondname + ".html")

    def test_update_document_template_content(self):
        nid = asm3.template.create_document_template(base.get_dbo(), "test", asm3.utils.uuid_b64())
        asm3.template.update_document_template_content(base.get_dbo(), "test", nid, b"<xx>")
        rv = asm3.template.get_document_template_content(base.get_dbo(), nid)
        self.assertEqual(rv, b"<xx>")


