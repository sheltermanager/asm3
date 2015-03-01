#!/usr/bin/python env

import unittest
import base

import csvimport

class TestCSVImport(unittest.TestCase):

    def tearDown(self):
        base.execute("DELETE FROM animal WHERE AnimalName = 'TestioCSV'")

    def test_csvimport(self):
        csvdata = "ANIMALNAME,ANIMALSEX,ANIMALAGE\n\"TestioCSV\",\"Male\",\"2\"\n"
        csvimport.csvimport(base.get_dbo(), csvdata)

