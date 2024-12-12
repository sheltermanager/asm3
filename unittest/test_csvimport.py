
import unittest
import base

import asm3.csvimport

class TestCSVImport(unittest.TestCase):

    def tearDown(self):
        base.execute("DELETE FROM animal WHERE AnimalName = 'TestioCSV'")
        base.execute("DELETE FROM diary WHERE Subject = 'Test diary note from csv import'")
        base.execute("DELETE FROM owner WHERE OwnerName = 'Sir Bob Hoskins'")

    def test_csvimport(self):
        csvdata = "ANIMALNAME,ANIMALSEX,ANIMALAGE,PERSONNAME,INCIDENTDATE,DIARYDATE,DIARYFOR,DIARYSUBJECT,DIARYNOTE\n" \
            "\"TestioCSV\",\"Male\",\"2\",\"Sir Bob Hoskins\",\"2001-09-11\",\"2020-01-20\",\"Baldrick\",\"Test diary note from csv import\",\"This note was created as part of the CSV import unit test.\"\n" \
            "\"\",\"\",\"\",\"Sir Bob Hoskins\",\"\",\"2020-01-20\",\"Nanny\",\"Test diary note from csv import\",\"This note was created as part of the CSV import unit test.\"\n" \
            "\"\",\"\",\"\",\"Sir Bob Hoskins\",\"2001-09-11\",\"2020-01-20\",\"The Prince\",\"Test diary note from csv import\",\"This note was created as part of the CSV import unit test.\"\n"
        asm3.csvimport.csvimport(base.get_dbo(), csvdata)

    def test_csvexport_animals(self):
        asm3.csvimport.csvexport_animals(base.get_dbo(), "all")

