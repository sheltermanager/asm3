
import unittest
import base

import asm3.service

class TestService(unittest.TestCase):

    def test_flood_protect(self):
        asm3.service.flood_protect("online_form_post", "1.1.1.1")
        with self.assertRaises(asm3.utils.ASMError):
            asm3.service.flood_protect("online_form_post", "1.1.1.1")

    def test_safe_cache_key(self):
        s = asm3.service.safe_cache_key("animal_image", "?animalid=52&cache=bust")
        assert s.find("cache") == -1

    def test_sign_document_page(self):
        assert len(asm3.service.sign_document_page(base.get_dbo(), 0, "test@example.com")) > 0


