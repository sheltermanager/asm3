
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

    def test_generate_image_pdf(self):
        with open("%s/static/images/splash/splash_logo.jpg" % base.get_dbo().installpath, "rb") as f:
            asm3.utils.generate_image_pdf("en", f.read())

    def test_generate_label_pdf(self):
        rows = [ { "OWNERNAME": "test", "OWNERADDRESS": "test", "OWNERCOUNTY": "test", "OWNERTOWN": "test", "OWNERPOSTCODE": "test" } ]
        asm3.utils.generate_label_pdf(base.get_dbo(), "en", rows, "A4", "cm", 1.0, 1.0, 5.0, 5.0, 0, 0, 2, 3)

    def test_csv(self):
        data = [ { "FIELD1": "VAL1&#2019;", "FIELD2": "Test" }, { "FIELD1": "MORE&#euro;", "FIELD2": "OK" } ]
        c = asm3.utils.csv("en", data)
        assert isinstance(c, bytes)
        assert c.find(b"\"FIELD1") != -1

    def test_csv_parse(self):
        data = u"FIELD1,FIELD2\n\"£,quoted\njunk\",field2"
        rows = asm3.utils.csv_parse(data)
        assert len(rows) == 1
        assert rows[0]["FIELD1"].find("quoted") != -1
        assert len(rows[0]) == 2

    def test_html_to_text(self):
        data = "<!DOCTYPE html>" \
            "<html><body><p>Unordered</p><ul><li>item 1</li><li>item 2</li></ul>" \
            "<p>Ordered</p><ol><li>item 1</li><li>item 2</li></ol>" \
            "<div>Nested <span>span content</span></div>" \
            "<div><p>Nested div content</p></div>" \
            "<table>" \
            "<tr><td><p>cell</p><p>1</p></td><td>cell 2</td><td>cell 3</td></tr>" \
            "<tr><td>cell 4</td><td>cell 5</td><td>cell 6</td></tr>" \
            "</table></body></html>"
        plain = asm3.utils.html_to_text(data)
        assert plain.find("* item 1") != -1
        assert plain.find("1. item 1") != -1
        assert plain.find("cell 1") != -1

