#!/usr/bin/python env

import unittest
import base

import animalname
import utils

class TestAnimalName(unittest.TestCase):

    def test_get_random_name(self):
        assert "" != animalname.get_random_name()

