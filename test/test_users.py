#!/usr/bin/python env

import unittest
#import base

import users

class TestUsers(unittest.TestCase):

    def test_hash_password(self):
        assert users.hash_password("password", "plain") == "plain:password"
        assert users.hash_password("letmein", "md5") == "md5:0d107d09f5bbe40cade3de5c71e9e9b7"
        assert users.hash_password("letmein", "md5java") == "md5java:d107d09f5bbe40cade3de5c71e9e9b7"
        hp = users.hash_password("guest", "pbkdf2")
        assert users.verify_password("guest", hp)

    def test_verify_password(self):
        assert users.verify_password("password", "plain:password")
        assert users.verify_password("guest", "pbkdf2:sha1:kFppt9JrIHxSepxvgaAJyg==:10000:ccefde3e7ba22f81cd54b226b89443c1a89125826f18fa6b")
        assert users.verify_password("letmein", "0d107d09f5bbe40cade3de5c71e9e9b7")
        assert users.verify_password("letmein", "d107d09f5bbe40cade3de5c71e9e9b7")
        assert users.verify_password("letmein", "md5java:d107d09f5bbe40cade3de5c71e9e9b7")
        assert users.verify_password("letmein", "md5:0d107d09f5bbe40cade3de5c71e9e9b7")

