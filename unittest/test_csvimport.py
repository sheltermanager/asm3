
import unittest
import base

import asm3.csvimport

class TestCSVImport(unittest.TestCase):

    def tearDown(self):
        base.execute("DELETE FROM animal WHERE AnimalName = 'TestioCSV'")

    def test_csvimport(self):
        csvdata = "ANIMALNAME,ANIMALSEX,ANIMALAGE\n\"TestioCSV\",\"Male\",\"2\"\n"
        asm3.csvimport.csvimport(base.get_dbo(), csvdata)

    def test_csvexport_animals(self):
        asm3.csvimport.csvexport_animals(base.get_dbo(), "all")

