
import unittest
import base

import asm3.animalname

class TestAnimalName(unittest.TestCase):

    def test_get_random_name(self):
        assert "" != asm3.animalname.get_random_name()

