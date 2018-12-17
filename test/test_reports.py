#!/usr/bin/python env

import unittest
import base

import reports
import utils
import web

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
        post = utils.PostedData(data, "en")
        self.nid = reports.insert_report_from_form(base.get_dbo(), "test", post)

    def tearDown(self):
        reports.delete_report(base.get_dbo(), "test", self.nid)

    def test_get_all_report_titles(self):
        assert len(reports.get_all_report_titles(base.get_dbo())) > 0

    def test_get_available_reports(self):
        assert len(reports.get_available_reports(base.get_dbo())) > 0

    def test_get_available_mailmerges(self):
        reports.get_available_mailmerges(base.get_dbo())

    def test_getters(self):
        fakesession = web.utils.storage(user="test", roles="", locale="en", dbo=base.get_dbo(), superuser=1, mobileapp=False)
        assert "" != reports.get_report_header(base.get_dbo(), "Test Report", "test")
        assert "" != reports.get_report_footer(base.get_dbo(), "Test Report", "test")
        assert len(reports.get_categories(base.get_dbo())) > 0
        assert "Test Report" ==reports.get_title(base.get_dbo(), self.nid)
        assert self.nid == reports.get_id(base.get_dbo(), "Test Report")
        assert False == reports.is_mailmerge(base.get_dbo(), self.nid)
        assert True == reports.check_view_permission(fakesession, self.nid)
        reports.check_sql(base.get_dbo(), "test", TEST_QUERY)
        assert True == reports.is_valid_query(TEST_QUERY)
        assert "" != reports.generate_html(base.get_dbo(), "test", TEST_QUERY)
        assert "" != reports.get_reports_menu(base.get_dbo())
        reports.get_mailmerges_menu(base.get_dbo())

    def test_email_daily_reports(self):
        reports.email_daily_reports(base.get_dbo())

    def test_execute(self):
        reports.execute(base.get_dbo(), self.nid)

    def test_smcom_reports(self):
        reports.install_smcom_reports(base.get_dbo(), "test", [1]) # Calls get_reports to do the install

    
