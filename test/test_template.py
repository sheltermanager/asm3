#!/usr/bin/python env

import unittest
import base, base64

import asm3.template

class TestTemplate(unittest.TestCase):

    def test_get_html_template(self):
        assert asm3.template.get_html_template(base.get_dbo(), "animalview")[0] != ""

    def test_get_html_templates(self):
        assert len(asm3.template.get_html_templates(base.get_dbo())) > 0

    def test_get_html_template_names(self):
        assert len(asm3.template.get_html_template_names(base.get_dbo())) > 0

    def test_update_html_template(self):
        asm3.template.update_html_template(base.get_dbo(), "test", "testtemplate", "head", "body", "foot")
        assert asm3.template.get_html_template(base.get_dbo(), "testtemplate")[0] != ""

    def test_delete_html_template(self):
        asm3.template.update_html_template(base.get_dbo(), "test", "testtemplate", "head", "body", "foot")
        asm3.template.delete_html_template(base.get_dbo(), "test", "testtemplate")
        assert asm3.template.get_html_template(base.get_dbo(), "testtemplate")[0] == ""

    def test_get_document_templates(self):
        assert len(asm3.template.get_document_templates(base.get_dbo())) > 0

    def test_get_document_template_content(self):
        assert asm3.template.get_document_template_content(base.get_dbo(), 1) != ""

    def test_get_document_template_name(self):
        assert asm3.template.get_document_template_name(base.get_dbo(), 1) != ""

    def test_create_document_template(self):
        nid = asm3.template.create_document_template(base.get_dbo(), "test", "testdoc")
        assert nid != 0

    def test_clone_document_template(self):
        nid = asm3.template.clone_document_template(base.get_dbo(), "test", 1, "testdoc2")
        assert nid != 0

    def test_delete_document_template(self):
        nid = asm3.template.create_document_template(base.get_dbo(), "test", "testdoc3")
        asm3.template.delete_document_template(base.get_dbo(), "test", nid)
        assert asm3.template.get_document_template_name(base.get_dbo(), nid) == ""

    def test_rename_document_template(self):
        nid = asm3.template.create_document_template(base.get_dbo(), "test", "testdoc4")
        asm3.template.rename_document_template(base.get_dbo(), "test", nid, "testdoc5")
        assert asm3.template.get_document_template_name(base.get_dbo(), nid) == "testdoc5.html"

    def test_update_document_template_content(self):
        nid = asm3.template.create_document_template(base.get_dbo(), "test", "testdoc6")
        asm3.template.update_document_template_content(base.get_dbo(), nid, "<xx>")
        assert asm3.template.get_document_template_content(base.get_dbo(), nid) == "<xx>"


