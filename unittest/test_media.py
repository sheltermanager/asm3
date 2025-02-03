
import unittest
import base, base64

import asm3.animal, asm3.media
import asm3.utils

class TestMedia(unittest.TestCase):

    def test_attach_file_from_form(self):
        data = {
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        nid, code = asm3.animal.insert_animal_from_form(base.get_dbo(), post, "test")
        f = open(base.PATH + "../src/media/reports/nopic.jpg", "rb")
        data = f.read()
        f.close()
        post = asm3.utils.PostedData({ "filename": "image.jpg", "filetype": "image/jpeg", "filedata": "data:image/jpeg;base64,%s" % asm3.utils.base64encode(data) }, "en")
        asm3.media.attach_file_from_form(base.get_dbo(), "test", asm3.media.ANIMAL, nid, asm3.media.MEDIASOURCE_ATTACHFILE, post)
        asm3.animal.delete_animal(base.get_dbo(), "test", nid)
 
    def test_remove_expired_media(self):
        asm3.media.remove_expired_media(base.get_dbo(), years=1)

    def test_remove_media_after_exit(self):
        asm3.media.remove_media_after_exit(base.get_dbo(), years=1)

    def test_get_media_export(self):
        asm3.media.get_media_export(base.get_dbo())

    def test_replace_doc_image(self):
        content = asm3.utils.str2bytes('<h1>Test</h1><p><img src="findme.jpg"></p>')
        mid = asm3.media.create_document_media(base.get_dbo(), "test", asm3.media.ANIMAL, 1, "test", content)
        asm3.media.replace_doc_image(base.get_dbo(), "findme.jpg", "replace.jpg")
        lm, mn, mt, content = asm3.media.get_media_file_data(base.get_dbo(), mid)
        self.assertTrue( content.find(b'replace') != -1)
