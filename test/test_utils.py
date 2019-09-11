#!/usr/bin/python env

import datetime, unittest
import base

import asm3.utils

class TestUtils(unittest.TestCase):
 
    def test_json_handler(self):
        assert asm3.utils.json({ "v": None}).find("null") != -1
        assert asm3.utils.json({ "d": datetime.datetime(2014, 1, 1, 1, 1, 1) }).find("2014-01-01T01:01:01") != -1
        assert asm3.utils.json({ "t": datetime.timedelta(days = 1) }).find("00:00:00") != -1

    def test_send_email(self):
        asm3.utils.send_email( base.get_dbo(), "tests@example.com", "example@example.com", subject="Test", body="Test suite", exceptions=False )


    def test_generate_label_pdf(self):
        rows = [ { "OWNERNAME": "test", "OWNERADDRESS": "test", "OWNERCOUNTY": "test", "OWNERTOWN": "test", "OWNERPOSTCODE": "test" } ]
        asm3.utils.generate_label_pdf(base.get_dbo(), "en", rows, "A4", "cm", 1.0, 1.0, 5.0, 5.0, 0, 0, 2, 3)

    def test_csv(self):
        data = [ { "FIELD1": "VAL1&#63;", "FIELD2": "Test" }, { "FIELD1": "MORE&#euro;", "FIELD2": "OK" } ]
        c = asm3.utils.csv("en", data)
        assert isinstance(c, bytes)
        assert c.startswith(b"\"FIELD1")
