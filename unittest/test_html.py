
import datetime, unittest
import base

import asm3.html, asm3.publish

class TestHtml(unittest.TestCase):
 
    def test_escape(self):
        self.assertEqual(asm3.html.escape("'\"><"), "&apos;&quot;&gt;&lt;")

    def test_escape_angle(self):
        self.assertEqual(asm3.html.escape("><"), "&gt;&lt;")

    def test_menu_structure(self):
        self.assertIsNotNone(asm3.html.menu_structure("en", asm3.publish.PUBLISHER_LIST, [], []))

    def test_json_animalfindcolumns(self):
        self.assertIsNotNone(asm3.html.json_animalfindcolumns(base.get_dbo()))

    def test_json_personfindcolumns(self):
        self.assertIsNotNone(asm3.html.json_personfindcolumns(base.get_dbo()))

    def test_json_eventfindcolumns(self):
        self.assertIsNotNone(asm3.html.json_eventfindcolumns(base.get_dbo()))

    def test_json_incidentfindcolumns(self):
        self.assertIsNotNone(asm3.html.json_incidentfindcolumns(base.get_dbo()))

    def test_json_foundanimalfindcolumns(self):
        self.assertIsNotNone(asm3.html.json_foundanimalfindcolumns(base.get_dbo()))

    def test_json_lookup_tables(self):
        self.assertNotEqual(len(asm3.html.json_lookup_tables("en")), len(asm3.html.json_lookup_tables("es")))

    def test_json_lostanimalfindcolumns(self):
        self.assertIsNotNone(asm3.html.json_lostanimalfindcolumns(base.get_dbo()))

    def test_json_waitinglistcolumns(self):
        self.assertIsNotNone(asm3.html.json_waitinglistcolumns(base.get_dbo()))

    def test_qr_animal_img_record_src(self):
        self.assertIsNotNone(asm3.html.qr_animal_img_record_src(1))

    def test_qr_animal_img_share_src(self):
        self.assertIsNotNone(asm3.html.qr_animal_img_share_src(base.get_dbo(), 1))


