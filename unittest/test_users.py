
import unittest
import base

import asm3.users

class TestUsers(unittest.TestCase):

    def test_hash_password(self):
        self.assertEqual(asm3.users.hash_password("password", "plain"), "plain:password")
        self.assertEqual(asm3.users.hash_password("letmein", "md5"),  "md5:0d107d09f5bbe40cade3de5c71e9e9b7")
        self.assertEqual(asm3.users.hash_password("letmein", "md5java"), "md5java:d107d09f5bbe40cade3de5c71e9e9b7")
        hp = asm3.users.hash_password("guest", "pbkdf2")
        self.assertTrue(asm3.users.verify_password("guest", hp))

    def test_verify_password(self):
        self.assertTrue(asm3.users.verify_password("password", "plain:password"))
        self.assertTrue(asm3.users.verify_password("guest", "pbkdf2:sha1:kFppt9JrIHxSepxvgaAJyg==:10000:ccefde3e7ba22f81cd54b226b89443c1a89125826f18fa6b"))
        self.assertTrue(asm3.users.verify_password("letmein", "0d107d09f5bbe40cade3de5c71e9e9b7"))
        self.assertTrue(asm3.users.verify_password("letmein", "d107d09f5bbe40cade3de5c71e9e9b7"))
        self.assertTrue(asm3.users.verify_password("letmein", "md5java:d107d09f5bbe40cade3de5c71e9e9b7"))
        self.assertTrue(asm3.users.verify_password("letmein", "md5:0d107d09f5bbe40cade3de5c71e9e9b7"))

