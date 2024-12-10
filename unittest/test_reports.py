
import unittest
import base
import web062 as web

import asm3.reports
import asm3.utils

TEST_QUERY = "SELECT * FROM lksmovementtype"

class TestReports(unittest.TestCase):

    nid = 0

    def setUp(self):
        data = {
            "title":    "Test Report",
            "category": "Test",
            "sql":      TEST_QUERY,
            "html":     "$$HEADER HEADER$$ $$BODY <p>$ID</p> BODY$$ $$FOOTER FOOTER$$"
        }
        post = asm3.utils.PostedData(data, "en")
        self.nid = asm3.reports.insert_report_from_form(base.get_dbo(), "test", post)

    def tearDown(self):
        asm3.reports.delete_report(base.get_dbo(), "test", self.nid)

    def test_get_all_report_titles(self):
       self.assertNotEqual(0, len(asm3.reports.get_all_report_titles(base.get_dbo())))

    def test_get_available_reports(self):
        self.assertNotEqual(0, len(asm3.reports.get_available_reports(base.get_dbo())))

    def test_get_available_mailmerges(self):
        asm3.reports.get_available_mailmerges(base.get_dbo())

    def test_getters(self):
        fakesession = web.utils.storage(user="test", roles="", locale="en", dbo=base.get_dbo(), superuser=1, mobileapp=False)
        self.assertNotEqual("", asm3.reports.get_report_header(base.get_dbo(), "Test Report", "test"))
        self.assertNotEqual("", asm3.reports.get_report_footer(base.get_dbo(), "Test Report", "test"))
        self.assertNotEqual(0, len(asm3.reports.get_categories(base.get_dbo())))
        self.assertEqual("Test Report", asm3.reports.get_title(base.get_dbo(), self.nid))
        self.assertEqual(self.nid, asm3.reports.get_id(base.get_dbo(), "Test Report"))
        self.assertFalse(asm3.reports.is_mailmerge(base.get_dbo(), self.nid))
        self.assertTrue(asm3.reports.check_view_permission(fakesession, self.nid))
        asm3.reports.check_sql(base.get_dbo(), "test", TEST_QUERY)
        self.assertTrue(asm3.reports.is_valid_query(TEST_QUERY))
        self.assertNotEqual("", asm3.reports.generate_html(base.get_dbo(), "test", TEST_QUERY))
        self.assertNotEqual("", asm3.reports.get_reports_menu(base.get_dbo()))
        asm3.reports.get_mailmerges_menu(base.get_dbo())

    def test_email_daily_reports(self):
        asm3.reports.email_daily_reports(base.get_dbo())

    def test_execute(self):
        asm3.reports.execute(base.get_dbo(), self.nid)

    def test_smcom_reports(self):
        asm3.reports.install_recommended_smcom_reports(base.get_dbo(), "test") # Calls get_reports to do the install

    
