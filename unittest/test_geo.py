
import unittest
import base

import asm3.geo

class TestGeo(unittest.TestCase):
 
    def test_get_lat_long(self):
        self.assertIsNotNone(asm3.geo.get_lat_long(base.get_dbo(), "109 Greystones Road", "Rotherham", "South Yorkshire", "S60 2AH", "England"))

