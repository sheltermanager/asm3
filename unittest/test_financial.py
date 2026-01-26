
import unittest
import base

import asm3.financial
import asm3.utils

class TestFinancial(unittest.TestCase):
    
    def test_apply_regular_debits(self):
        base.execute("DELETE FROM accounts WHERE Code LIKE 'Test%'")
        base.execute("DELETE FROM regulardebit WHERE Comments = 'Just some test data'")

        data = {
            "code": "Testiofromo",
            "type": "5",
            "donationtype": "0",
            "description": "Test from account"
        }
        post = asm3.utils.PostedData(data, "en")
        faid = asm3.financial.insert_account_from_form(base.get_dbo(), "test", post)

        data = {
            "code": "Testioto",
            "type": "8",
            "donationtype": "0",
            "description": "Test to account"
        }
        post = asm3.utils.PostedData(data, "en")
        taid = asm3.financial.insert_account_from_form(base.get_dbo(), "test", post)

        data = {
            "person": "0",
            "startdate": "01/01/2025",
            "enddate": "",
            "amount": "500",
            "fromaccount": str(faid),
            "toaccount": str(taid),
            "period": "1",
            "weekday": "0",
            "dayofmonth": "1",
            "month": "1",
            "comments": "Just some test data"
        }
        post = asm3.utils.PostedData(data, "en")
        rdid = asm3.financial.insert_regulardebit_from_form(base.get_dbo(), "test", post)

        trxs = asm3.financial.create_trx_from_regular_debits(base.get_dbo(), "test")

        self.assertEqual(1, len(trxs))
        
        asm3.financial.delete_regulardebit(base.get_dbo(), "test", rdid)

        currentweekday = int(base.get_dbo().today().strftime("%w"))
        if currentweekday == 6:
            weekday = 0
        else:
            weekday = currentweekday + 1

        data = {
            "person": "0",
            "startdate": "01/01/2025",
            "enddate": "",
            "amount": "500",
            "fromaccount": str(faid),
            "toaccount": str(taid),
            "period": "7",
            "weekday": str(weekday),
            "dayofmonth": "1",
            "month": "1",
            "comments": "Just some test data"
        }
        post = asm3.utils.PostedData(data, "en")
        rdid = asm3.financial.insert_regulardebit_from_form(base.get_dbo(), "test", post)

        trxs = asm3.financial.create_trx_from_regular_debits(base.get_dbo(), "test")

        self.assertEqual(0, len(trxs))

        asm3.financial.delete_regulardebit(base.get_dbo(), "test", rdid)

        currentmonth = base.get_dbo().today().month
        currentdayofmonth = base.get_dbo().today().day

        data = {
            "person": "0",
            "startdate": "01/01/2025",
            "enddate": "",
            "amount": "500",
            "fromaccount": str(faid),
            "toaccount": str(taid),
            "period": "365",
            "weekday": "0",
            "dayofmonth": str(currentdayofmonth),
            "month": str(currentmonth),
            "comments": "Just some test data"
        }
        post = asm3.utils.PostedData(data, "en")
        rdid = asm3.financial.insert_regulardebit_from_form(base.get_dbo(), "test", post)

        trxs = asm3.financial.create_trx_from_regular_debits(base.get_dbo(), "test")

        self.assertEqual(1, len(trxs))

        asm3.financial.delete_regulardebit(base.get_dbo(), "test", rdid)

        if currentmonth == 12:
            currentmonth = 1
        else:
            currentmonth = currentmonth + 1

        data = {
            "person": "0",
            "startdate": "01/01/2025",
            "enddate": "",
            "amount": "500",
            "fromaccount": str(faid),
            "toaccount": str(taid),
            "period": "365",
            "weekday": "0",
            "dayofmonth": str(currentdayofmonth),
            "month": str(currentmonth),
            "comments": "Just some test data"
        }
        post = asm3.utils.PostedData(data, "en")
        rdid = asm3.financial.insert_regulardebit_from_form(base.get_dbo(), "test", post)

        trxs = asm3.financial.create_trx_from_regular_debits(base.get_dbo(), "test")

        self.assertEqual(0, len(trxs))

        base.execute("DELETE FROM accounts WHERE Code LIKE 'Test%'")
        base.execute("DELETE FROM regulardebit WHERE Comments = 'Just some test data'")
        base.execute("DELETE FROM accountstrx WHERE CreatedBy = 'test'")

    def test_get_account_code(self):
        asm3.financial.get_account_code(base.get_dbo(), 0)

    def test_get_account_codes(self):
        self.assertNotEqual(0, len(asm3.financial.get_account_codes(base.get_dbo())))

    def test_get_account_edit_roles(self):
        firstac = asm3.financial.get_accounts(base.get_dbo())[0]
        asm3.financial.get_account_edit_roles(base.get_dbo(), firstac["ID"])

    def test_get_account_id(self):
        firstcode = asm3.financial.get_accounts(base.get_dbo())[0]["CODE"]
        self.assertNotEqual(0, asm3.financial.get_account_id(base.get_dbo(), firstcode))

    def test_get_accounts(self):
        self.assertNotEqual(0, len(asm3.financial.get_accounts(base.get_dbo())))

    def test_get_balance_to_date(self):
        firstac = asm3.financial.get_accounts(base.get_dbo())[0]
        asm3.financial.get_balance_to_date(base.get_dbo(), firstac["ID"], base.today())

    def test_get_balance_fromto_date(self):
        firstac = asm3.financial.get_accounts(base.get_dbo())[0]
        asm3.financial.get_balance_fromto_date(base.get_dbo(), firstac["ID"], base.today(), base.today())

    def test_get_transactions(self):
        firstac = asm3.financial.get_accounts(base.get_dbo())[0]
        asm3.financial.get_transactions(base.get_dbo(), firstac["ID"], base.today(), base.today(), asm3.financial.BOTH)

    def test_get_movement_donation(self):
        self.assertIsNone(asm3.financial.get_movement_donation(base.get_dbo(), 1))

    def test_get_boarding(self):
        asm3.financial.get_boarding(base.get_dbo(), "active")
        asm3.financial.get_boarding(base.get_dbo(), "m90")
        asm3.financial.get_boarding(base.get_dbo(), "p90")

    def test_get_boarding_due_two_dates(self):
        asm3.financial.get_boarding_due_two_dates(base.get_dbo(), base.today(), base.today())

    def test_get_donations(self):
        asm3.financial.get_donations(base.get_dbo())

    def test_get_donations_due_two_dates(self):
        asm3.financial.get_donations_due_two_dates(base.get_dbo(), base.today(), base.today())

    def test_get_animal_donations(self):
        asm3.financial.get_animal_donations(base.get_dbo(), 0)

    def test_get_person_donations(self):
        asm3.financial.get_person_donations(base.get_dbo(), 0)

    def test_get_incident_citations(self):
        asm3.financial.get_incident_citations(base.get_dbo(), 0)

    def test_get_person_citations(self):
        asm3.financial.get_person_citations(base.get_dbo(), 0)

    def test_get_unpaid_fines(self):
        asm3.financial.get_unpaid_fines(base.get_dbo())

    def test_get_animal_licences(self):
        asm3.financial.get_animal_licences(base.get_dbo(), 0)

    def test_get_person_licences(self):
        asm3.financial.get_person_licences(base.get_dbo(), 0)

    def test_get_recent_licences(self):
        asm3.financial.get_recent_licences(base.get_dbo())

    def test_get_licence_find_simple(self):
        asm3.financial.get_licence_find_simple(base.get_dbo(), "")

    def test_get_licence(self):
        asm3.financial.get_licence(base.get_dbo(), 1)

    def test_get_licences(self):
        asm3.financial.get_licences(base.get_dbo())

    def test_get_vouchers(self):
        asm3.financial.get_vouchers(base.get_dbo())

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
        post = asm3.utils.PostedData(data, "en")
        did = asm3.financial.insert_donation_from_form(base.get_dbo(), "test", post)
        asm3.financial.update_donation_from_form(base.get_dbo(), "test", post)
        asm3.financial.receive_donation(base.get_dbo(), "test", did)
        asm3.financial.delete_donation(base.get_dbo(), "test", did)

    def test_insert_account_from_costtype(self):
        aid = asm3.financial.insert_account_from_costtype(base.get_dbo(), "Test", "Test")
        asm3.financial.delete_account(base.get_dbo(), "test", aid)

    def test_insert_account_from_donationtype(self):
        aid = asm3.financial.insert_account_from_donationtype(base.get_dbo(), "Test", "Test")
        asm3.financial.delete_account(base.get_dbo(), "test", aid)

    def test_account_crud(self):
        base.execute("DELETE FROM accounts WHERE Code LIKE 'Test%'")
        data = {
            "code": "Testio",
            "type": "1",
            "donationtype": "1",
            "description": "Test"
        }
        post = asm3.utils.PostedData(data, "en")
        aid = asm3.financial.insert_account_from_form(base.get_dbo(), "test", post)
        data["accountid"] = aid
        asm3.financial.update_account_from_form(base.get_dbo(), "test", post)
        asm3.financial.delete_account(base.get_dbo(), "test", aid)

    def test_accounttrx_crud(self):
        data = {
            "trxdate": base.today_display(),
            "deposit": "1000",
            "withdrawal": "0",
            "accountid": "1",
            "otheraccount": "Income::Donation",
            "description": "Test"
        }
        post = asm3.utils.PostedData(data, "en")
        tid = asm3.financial.insert_trx_from_form(base.get_dbo(), "test", post)
        asm3.financial.update_trx_from_form(base.get_dbo(), "test", post)
        asm3.financial.delete_trx(base.get_dbo(), "test", tid)

    def test_voucher_crud(self):
        data = {
            "person": "1",
            "type": "1",
            "issued": base.today_display(),
            "expires": base.today_display(),
            "amount": "1000"
        }
        post = asm3.utils.PostedData(data, "en")
        vid = asm3.financial.insert_voucher_from_form(base.get_dbo(), "test", post)
        asm3.financial.update_voucher_from_form(base.get_dbo(), "test", post)
        asm3.financial.delete_voucher(base.get_dbo(), "test", vid)

    def test_boarding_crud(self):
        data = {
            "person": "1",
            "animal": "1",
            "type": "1",
            "indate": base.today_display(),
            "outdate": base.today_display(),
            "dailyfee": "1000"
        }
        post = asm3.utils.PostedData(data, "en")
        bid = asm3.financial.insert_boarding_from_form(base.get_dbo(), "test", post)
        asm3.financial.update_boarding_from_form(base.get_dbo(), "test", post)
        asm3.financial.delete_boarding(base.get_dbo(), "test", bid)

    def test_citation_crud(self):
        data = {
            "person": "1",
            "incident": "1",
            "type": "1",
            "citationdate": base.today_display(),
            "fineamount": "1000",
            "finedue": base.today_display()
        }
        post = asm3.utils.PostedData(data, "en")
        cid = asm3.financial.insert_citation_from_form(base.get_dbo(), "test", post)
        asm3.financial.update_citation_from_form(base.get_dbo(), "test", post)
        asm3.financial.delete_citation(base.get_dbo(), "test", cid)

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
        post = asm3.utils.PostedData(data, "en")
        lid = asm3.financial.insert_licence_from_form(base.get_dbo(), "test", post)
        data["licenceid"] = str(lid)
        asm3.financial.update_licence_from_form(base.get_dbo(), "test", post)
        asm3.financial.delete_licence(base.get_dbo(), "test", lid)

    def test_renew_licence_payref(self):
        data = {
            "person": "1",
            "animal": "1",
            "type": "1",
            "number": "LICENCE",
            "fee": "1000",
            "issuedate": base.today_display(),
            "expirydate": base.today_display()
        }
        post = asm3.utils.PostedData(data, "en")
        lid = asm3.financial.insert_licence_from_form(base.get_dbo(), "test", post)
        base.execute(f"UPDATE ownerlicence SET PaymentReference='PAYREF' WHERE ID={lid}")
        asm3.financial.renew_licence_payref(base.get_dbo(), "PAYREF")
        asm3.financial.delete_licence(base.get_dbo(), "test", lid)

    def test_giftaid_spreadsheet(self):
        asm3.financial.giftaid_spreadsheet(base.get_dbo(), "%s/../src/" % base.PATH, base.today(), base.today())

    def test_update_location_boarding_today(self):
        asm3.financial.update_location_boarding_today(base.get_dbo())
