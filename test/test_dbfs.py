#!/usr/bin/python env

import unittest
import base

import dbfs
#import utils

class TestDBFS(unittest.TestCase):

    def test_create_path(self):
        dbfs.create_path(base.get_dbo(), "/", "test")
        dbfs.delete_path(base.get_dbo(), "test")
        dbfs.delete(base.get_dbo(), "test")
        dbfs.delete_filepath(base.get_dbo(), "/test")

    def test_get_string_filepath(self):
        assert len(dbfs.get_string_filepath(base.get_dbo(), "/reports/nopic.jpg")) > 0

    def test_get_string(self):
        assert len(dbfs.get_string(base.get_dbo(), "nopic.jpg", "/reports")) > 0

    def test_put_string_filepath(self):
        content = "123test"
        dbfs.put_string_filepath(base.get_dbo(), "/reports/test.txt", content)
        assert content == dbfs.get_string_filepath(base.get_dbo(), "/reports/test.txt")
        dbfs.delete_filepath(base.get_dbo(), "/reports/test.txt")

    def test_file_exists(self):
        assert dbfs.file_exists(base.get_dbo(), "nopic.jpg")

    def test_list_contents(self):
        assert len(dbfs.list_contents(base.get_dbo(), "/reports")) > 0

    def test_get_nopic(self):
        assert len(dbfs.get_nopic(base.get_dbo())) > 0

    def test_get_document_templates(self):
        assert len(dbfs.get_document_templates(base.get_dbo())) > 0

    def test_get_html_document_templates(self):
        assert len(dbfs.get_html_document_templates(base.get_dbo())) > 0

    def test_get_odt_document_templates(self):
        dbfs.get_html_publisher_templates(base.get_dbo())

    def test_get_html_publisher_templates_files(self):
        assert len(dbfs.get_html_publisher_templates_files(base.get_dbo())) > 0

    def test_update_html_publisher_template(self):
        dbfs.update_html_publisher_template(base.get_dbo(), "test", "test", "HEADER", "BODY", "FOOTER")
        assert "test" in dbfs.get_html_publisher_templates(base.get_dbo())
        dbfs.delete_html_publisher_template(base.get_dbo(), "test", "test")

    def test_get_publish_logs(self):
        dbfs.get_publish_logs(base.get_dbo())

    def test_get_publish_alerts(self):
        dbfs.get_publish_alerts(base.get_dbo())

    def test_delete_old_publish_logs(self):
        dbfs.delete_old_publish_logs(base.get_dbo())

    def test_create_html_template(self):
        dbfsid = dbfs.create_document_template(base.get_dbo(), "test", ".html", "<p>TEST</p>")
        assert "test.html" == dbfs.get_name_for_id(base.get_dbo(), dbfsid)
        dbfsid2 = dbfs.clone_document_template(base.get_dbo(), dbfsid, "test2")
        assert "test2.html" == dbfs.get_name_for_id(base.get_dbo(), dbfsid2)
        dbfs.delete_id(base.get_dbo(), dbfsid)
        dbfs.delete_id(base.get_dbo(), dbfsid2)

    def test_get_document_repository(self):
        dbfs.get_document_repository(base.get_dbo())

    def test_get_report_images(self):
        assert len(dbfs.get_report_images(base.get_dbo())) > 0

    def test_get_asm_news(self):
        assert "" != dbfs.get_asm_news(base.get_dbo())


