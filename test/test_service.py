#!/usr/bin/python env

import unittest
import base

import asm3.service

class TestService(unittest.TestCase):

    def test_flood_protect(self):
        asm3.service.flood_protect("animal_image", "1.1.1.1", 60)
        try:
            asm3.service.flood_protect("animal_image", "1.1.1.1", 60)
            assert False
        except:
            assert True

    def test_sign_document_page(self):
        assert len(asm3.service.sign_document_page(base.get_dbo(), 0)) > 0


