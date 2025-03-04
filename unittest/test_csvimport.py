
import unittest
import base

import asm3.csvimport

class TestCSVImport(unittest.TestCase):

    def tearDown(self):
        mediaids = base.get_dbo().query_list("SELECT media.ID FROM media INNER JOIN animal ON media.LinkID = animal.ID WHERE media.LinkTypeID = 0 AND animal.AnimalName = 'TestioCSV'")
        for mid in mediaids:
            base.execute("DELETE FROM media WHERE ID = %s" % (mid,))

        mediaids = base.get_dbo().query_list("SELECT media.ID FROM media INNER JOIN owner ON media.LinkID = owner.ID WHERE media.LinkTypeID = 3 AND owner.OwnerName = 'Sir Bob Hoskins'")
        for mid in mediaids:
            base.execute("DELETE FROM media WHERE ID = %s" % (mid,))

        base.execute("DELETE FROM animal WHERE AnimalName = 'TestioCSV'")
        base.execute("DELETE FROM diary WHERE Subject = 'Test diary note from csv import'")
        base.execute("DELETE FROM owner WHERE OwnerName = 'Sir Bob Hoskins'")

    def test_csvimport(self):
        csvdata = "ANIMALNAME,ANIMALSEX,ANIMALAGE,PERSONNAME,INCIDENTDATE,DIARYDATE,DIARYFOR,DIARYSUBJECT,DIARYNOTE\n" \
            "\"TestioCSV\",\"Male\",\"2\",\"Sir Bob Hoskins\",\"2001-09-11\",\"2020-01-20\",\"Baldrick\",\"Test diary note from csv import\",\"This note was created as part of the CSV import unit test.\"\n" \
            "\"\",\"\",\"\",\"Sir Bob Hoskins\",\"\",\"2020-01-20\",\"Nanny\",\"Test diary note from csv import\",\"This note was created as part of the CSV import unit test.\"\n" \
            "\"\",\"\",\"\",\"Sir Bob Hoskins\",\"2001-09-11\",\"2020-01-20\",\"The Prince\",\"Test diary note from csv import\",\"This note was created as part of the CSV import unit test.\"\n"
        asm3.csvimport.csvimport(base.get_dbo(), csvdata)

        aid = base.get_dbo().query_int("SELECT ID FROM animal WHERE AnimalName = 'TestioCSV' ORDER BY ID DESC LIMIT 1")
        pid = base.get_dbo().query_int("SELECT ID FROM owner WHERE OwnerName = 'Sir Bob Hoskins' ORDER BY ID DESC LIMIT 1")
        
        f = open(base.PATH + "../src/media/reports/nopic.jpg", "rb")
        data = f.read()
        f.close()
        post = asm3.utils.PostedData({ "filename": "image.jpg", "filetype": "image/jpeg", "filedata": "data:image/jpeg;base64,%s" % asm3.utils.base64encode(data) }, "en")
        asm3.media.attach_file_from_form(base.get_dbo(), "test", asm3.media.ANIMAL, aid, asm3.media.MEDIASOURCE_ATTACHFILE, post)
        asm3.media.attach_file_from_form(base.get_dbo(), "test", asm3.media.PERSON, pid, asm3.media.MEDIASOURCE_ATTACHFILE, post)

    def test_csvexport_animals(self):
        asm3.csvimport.csvexport_animals(base.get_dbo(), "all")
    
    def test_csvexport_people_all_no_media(self):
        asm3.csvimport.csvexport_people(base.get_dbo(), "all", "", "", "none")
    
    def test_csvexport_people_photo(self):
        asm3.csvimport.csvexport_people(base.get_dbo(), "all", "", "", "photo")