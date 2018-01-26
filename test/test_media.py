#!/usr/bin/python env

import unittest
import base, base64

import animal, media
import utils

class TestMedia(unittest.TestCase):

    def test_attach_file_from_form(self):
        data = {
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1"
        }
        post = utils.PostedData(data, "en")
        nid, code = animal.insert_animal_from_form(base.get_dbo(), post, "test")
        f = open(base.PATH + "../src/media/reports/nopic.jpg", "rb")
        data = f.read()
        f.close()
        post = utils.PostedData({ "filename": "image.jpg", "filetype": "image/jpeg", "filedata": "data:image/jpeg;base64," + base64.b64encode(data) }, "en")
        media.attach_file_from_form(base.get_dbo(), "test", media.ANIMAL, nid, post)
        animal.delete_animal(base.get_dbo(), "test", nid)
 
    def test_remove_expired_media(self):
        media.remove_expired_media(base.get_dbo())

