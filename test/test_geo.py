#!/usr/bin/python env

import unittest
import base

import geo

class TestGeo(unittest.TestCase):
 
    def test_get_lat_long(self):
        assert geo.get_lat_long(base.get_dbo(), "109 Greystones Road", "Rotherham", "South Yorkshire", "S60 2AH", "England") is not None

