#!/usr/bin/python env

import unittest
import base

import service
import utils

class TestService(unittest.TestCase):

    def test_adoptable_animals(self):
        data = {
            "username": "user",
            "password": "letmein",
            "method": "xml_adoptable_animals"
        }
        post = utils.PostedData(data, "en")
        service.handler(post, base.PATH, "127.0.0.1", "sheltermanager.com", "")
        data["method"] = "json_adoptable_animals"
        service.handler(post, base.PATH, "127.0.0.1", "sheltermanager.com", "")

    def test_recent_adoptions(self):
        data = {
            "username": "user",
            "password": "letmein",
            "method": "xml_recent_adoptions"
        }
        post = utils.PostedData(data, "en")
        service.handler(post, base.PATH, "127.0.0.1", "sheltermanager.com", "")
        data["method"] = "json_recent_adoptions"
        service.handler(post, base.PATH, "127.0.0.1", "sheltermanager.com", "")

    def test_shelter_animals(self):
        data = {
            "username": "user",
            "password": "letmein",
            "method": "xml_shelter_animals"
        }
        post = utils.PostedData(data, "en")
        service.handler(post, base.PATH, "127.0.0.1", "sheltermanager.com", "")
        data["method"] = "json_shelter_animals"
        service.handler(post, base.PATH, "127.0.0.1", "sheltermanager.com", "")
        data["method"] = "jsonp_shelter_animals"
        service.handler(post, base.PATH, "127.0.0.1", "sheltermanager.com", "")


