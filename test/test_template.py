#!/usr/bin/python env

import unittest
import base, base64

import template
import utils

class TestTemplate(unittest.TestCase):

    def test_get_html_template(self):
        assert template.get_html_template(base.get_dbo(), "animalview")[0] != ""

    def test_get_html_templates(self):
        assert len(template.get_html_templates(base.get_dbo())) > 0

    def test_get_html_template_names(self):
        assert len(template.get_html_template_names(base.get_dbo())) > 0

    def test_update_html_template(self):
        template.update_html_template(base.get_dbo(), "test", "testtemplate", "head", "body", "foot")
        assert template.get_html_template(base.get_dbo(), "testtemplate")[0] != ""

    def test_delete_html_template(self):
        template.update_html_template(base.get_dbo(), "test", "testtemplate", "head", "body", "foot")
        template.delete_html_template(base.get_dbo(), "test", "testtemplate")
        assert template.get_html_template(base.get_dbo(), "testtemplate")[0] == ""

    def test_get_document_templates(self):
        assert len(template.get_document_templates(base.get_dbo())) > 0

    def test_get_document_template_content(self):
        assert template.get_document_template_content(base.get_dbo(), 1) != ""

    def test_get_document_template_name(self):
        assert template.get_document_template_name(base.get_dbo(), 1) != ""

    def test_create_document_template(self):
        nid = template.create_document_template(base.get_dbo(), "test", "testdoc")
        assert nid != 0

    def test_clone_document_template(self):
        nid = template.clone_document_template(base.get_dbo(), "test", 1, "testdoc2")
        assert nid != 0

    def test_delete_document_template(self):
        nid = template.create_document_template(base.get_dbo(), "test", "testdoc3")
        template.delete_document_template(base.get_dbo(), "test", nid)
        assert template.get_document_template_name(base.get_dbo(), nid) == ""

    def test_rename_document_template(self):
        nid = template.create_document_template(base.get_dbo(), "test", "testdoc4")
        template.rename_document_template(base.get_dbo(), "test", nid, "testdoc5")
        assert template.get_document_template_name(base.get_dbo(), nid) == "testdoc5.html"

    def test_update_document_template_content(self):
        nid = template.create_document_template(base.get_dbo(), "test", "testdoc6")
        template.update_document_template_content(base.get_dbo(), nid, "<xx>")
        assert template.get_document_template_content(base.get_dbo(), nid) == "<xx>"


