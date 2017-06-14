#!/usr/bin/python env

import unittest
import base

import service
import utils

class TestService(unittest.TestCase):

    def test_flood_protect(self):
        service.flood_protect("animal_image", "1.1.1.1", 60)
        try:
            service.flood_protect("animal_image", "1.1.1.1", 60)
            assert False
        except:
            assert True

    def test_sign_document_page(self):
        assert len(service.sign_document_page(base.get_dbo(), 0)) > 0


