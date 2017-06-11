#!/usr/bin/python env

import unittest
import base

import financial
import utils

class TestFinancial(unittest.TestCase):

    def test_get_account_code(self):
        financial.get_account_code(base.get_dbo(), 0)

    def test_get_account_codes(self):
        assert len(financial.get_account_codes(base.get_dbo())) > 0

    def test_get_account_edit_roles(self):
        firstac = financial.get_accounts(base.get_dbo())[0]
        financial.get_account_edit_roles(base.get_dbo(), firstac["ID"])

    def test_get_account_id(self):
        firstcode = financial.get_accounts(base.get_dbo())[0]["CODE"]
        assert 0 != financial.get_account_id(base.get_dbo(), firstcode)

    def test_get_accounts(self):
        assert len(financial.get_accounts(base.get_dbo())) > 0

    def test_get_balance_to_date(self):
        firstac = financial.get_accounts(base.get_dbo())[0]
        financial.get_balance_to_date(base.get_dbo(), firstac["ID"], base.today())

    def test_get_balance_fromto_date(self):
        firstac = financial.get_accounts(base.get_dbo())[0]
        financial.get_balance_fromto_date(base.get_dbo(), firstac["ID"], base.today(), base.today())

    def test_get_transactions(self):
        firstac = financial.get_accounts(base.get_dbo())[0]
        financial.get_transactions(base.get_dbo(), firstac["ID"], base.today(), base.today(), financial.BOTH)

    def test_get_movement_donation(self):
        assert financial.get_movement_donation(base.get_dbo(), 1) is None

    def test_get_donations(self):
        financial.get_donations(base.get_dbo())

    def test_get_donations_due_two_dates(self):
        financial.get_donations_due_two_dates(base.get_dbo(), '2014-01-01', '2014-01-31')

    def test_get_animal_donations(self):
        financial.get_animal_donations(base.get_dbo(), 0)

    def test_get_person_donations(self):
        financial.get_person_donations(base.get_dbo(), 0)

    def test_get_incident_citations(self):
        financial.get_incident_citations(base.get_dbo(), 0)

    def test_get_person_citations(self):
        financial.get_person_citations(base.get_dbo(), 0)

    def test_get_unpaid_fines(self):
        financial.get_unpaid_fines(base.get_dbo())

    def test_get_animal_licences(self):
        financial.get_animal_licences(base.get_dbo(), 0)

    def test_get_person_licences(self):
        financial.get_person_licences(base.get_dbo(), 0)

    def test_get_recent_licences(self):
        financial.get_recent_licences(base.get_dbo())

    def test_get_licence_find_simple(self):
        financial.get_licence_find_simple(base.get_dbo(), "")

    def test_get_licence(self):
        financial.get_licence(base.get_dbo(), 1)

    def test_get_licenses(self):
        financial.get_licences(base.get_dbo())

    def test_get_vouchers(self):
        financial.get_vouchers(base.get_dbo(), 0)

    def test_receive_donation(self):
        data = {
            "person": "1",
            "animal": "1",
            "type":   "1",
            "payment": "1",
            "frequency": "0",
            "amount": "1000",
            "due": base.today_display()
        }
        post = utils.PostedData(data, "en")
        did = financial.insert_donation_from_form(base.get_dbo(), "test", post)
        financial.update_donation_from_form(base.get_dbo(), "test", post)
        financial.receive_donation(base.get_dbo(), "test", did)
        financial.delete_donation(base.get_dbo(), "test", did)

    def test_insert_account_from_donationtype(self):
        aid = financial.insert_account_from_donationtype(base.get_dbo(), 1, "Test", "Test")
        financial.delete_account(base.get_dbo(), "test", aid)

    def test_account_crud(self):
        base.execute("DELETE FROM accounts WHERE Code LIKE 'Test%'")
        data = {
            "code": "Testio",
            "type": "1",
            "donationtype": "1",
            "description": "Test"
        }
        post = utils.PostedData(data, "en")
        aid = financial.insert_account_from_form(base.get_dbo(), "test", post)
        data["accountid"] = aid
        financial.update_account_from_form(base.get_dbo(), "test", post)
        financial.delete_account(base.get_dbo(), "test", aid)

    def test_accounttrx_crud(self):
        data = {
            "trxdate": base.today_display(),
            "deposit": "1000",
            "withdrawal": "0",
            "accountid": "1",
            "otheraccount": "Income::Donation",
            "description": "Test"
        }
        post = utils.PostedData(data, "en")
        tid = financial.insert_trx_from_form(base.get_dbo(), "test", post)
        financial.update_trx_from_form(base.get_dbo(), "test", post)
        financial.delete_trx(base.get_dbo(), "test", tid)

    def test_voucher_crud(self):
        data = {
            "personid": "1",
            "type": "1",
            "issued": base.today_display(),
            "expires": base.today_display(),
            "amount": "1000"
        }
        post = utils.PostedData(data, "en")
        vid = financial.insert_voucher_from_form(base.get_dbo(), "test", post)
        financial.update_voucher_from_form(base.get_dbo(), "test", post)
        financial.delete_voucher(base.get_dbo(), "test", vid)

    def test_citation_crud(self):
        data = {
            "person": "1",
            "incident": "1",
            "type": "1",
            "citationdate": base.today_display(),
            "fineamount": "1000",
            "finedue": base.today_display()
        }
        post = utils.PostedData(data, "en")
        cid = financial.insert_citation_from_form(base.get_dbo(), "test", post)
        financial.update_citation_from_form(base.get_dbo(), "test", post)
        financial.delete_citation(base.get_dbo(), "test", cid)

    def test_licence_crud(self):
        base.execute("DELETE FROM ownerlicence WHERE LicenceNumber = 'LICENCE'")
        data = {
            "person": "1",
            "animal": "1",
            "type": "1",
            "number": "LICENCE",
            "fee": "1000",
            "issuedate": base.today_display(),
            "expirydate": base.today_display()
        }
        post = utils.PostedData(data, "en")
        lid = financial.insert_licence_from_form(base.get_dbo(), "test", post)
        data["licenceid"] = str(lid)
        financial.update_licence_from_form(base.get_dbo(), "test", post)
        financial.delete_licence(base.get_dbo(), "test", lid)

    def test_giftaid_spreadsheet(self):
        financial.giftaid_spreadsheet(base.get_dbo(), "%s/../src/" % base.PATH, base.today(), base.today())


