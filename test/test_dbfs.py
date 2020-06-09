
import unittest
import base

import asm3.dbfs

class TestDBFS(unittest.TestCase):

    def setUp(self):
        asm3.dbfs.put_string_filepath(base.get_dbo(), "/reports/nopic.jpg", b"fake_jpg_image_data")

    def tearDown(self):
        asm3.dbfs.delete_filepath(base.get_dbo(), "/reports/nopic.jpg")

    def test_create_path(self):
        asm3.dbfs.create_path(base.get_dbo(), "/", "test")
        asm3.dbfs.delete_path(base.get_dbo(), "test")
        asm3.dbfs.delete(base.get_dbo(), "test")
        asm3.dbfs.delete_filepath(base.get_dbo(), "/test")

    def test_get_string_filepath(self):
        assert len(asm3.dbfs.get_string_filepath(base.get_dbo(), "/reports/nopic.jpg")) > 0

    def test_get_string(self):
        assert len(asm3.dbfs.get_string(base.get_dbo(), "nopic.jpg", "/reports")) > 0

    def test_put_string_filepath(self):
        content = b"123test"
        asm3.dbfs.put_string_filepath(base.get_dbo(), "/reports/test.txt", content)
        assert content == asm3.dbfs.get_string_filepath(base.get_dbo(), "/reports/test.txt")
        asm3.dbfs.delete_filepath(base.get_dbo(), "/reports/test.txt")

    def test_file_exists(self):
        content = b"123test"
        asm3.dbfs.put_string_filepath(base.get_dbo(), "/reports/test.txt", content)
        assert asm3.dbfs.file_exists(base.get_dbo(), "test.txt")

    def test_list_contents(self):
        assert len(asm3.dbfs.list_contents(base.get_dbo(), "/reports")) > 0

    def test_get_document_repository(self):
        asm3.dbfs.get_document_repository(base.get_dbo())

    def test_upload_document_repository(self):
        asm3.dbfs.upload_document_repository(base.get_dbo(), "", "testdr.txt", b"content")
        assert asm3.dbfs.get_string_filepath(base.get_dbo(), "/document_repository/testdr.txt") == b"content"

    def test_get_report_images(self):
        assert len(asm3.dbfs.get_report_images(base.get_dbo())) > 0

    def test_delete_orphaned_media(self):
        asm3.dbfs.delete_orphaned_media(base.get_dbo())

    def test_switch_storage(self):
        asm3.dbfs.switch_storage(base.get_dbo())


