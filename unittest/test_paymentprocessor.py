import json

import unittest
import base

import asm3.financial
import asm3.paymentprocessor.base
import asm3.paymentprocessor.paypal
import asm3.utils

class TestPaypalPaymentProcessor(unittest.TestCase):
    personid = 0
    dueid = 0
    recid = 0
    sample_ipn_paypal = "mc_gross=326.70&settle_amount=266.74&protection_eligibility=Ineligible" \
        "&payer_id=DL2252JB928MN&tax=56.70&payment_date=05%3A46%3A17+Apr+20%2C+2020+PDT" \
        "&payment_status=Completed&charset=windows-1252&first_name=REDACTED&mc_fee=9.82" \
        "&exchange_rate=0.841767&notify_version=3.9&custom=&settle_currency=GBP&" \
        "payer_status=verified&business=paypal%40sheltermanager.com&quantity=1&" \
        "verify_sign=AxuJg3SvqhecqsoBYe3sJqW7LIr9AIjZFuKqzVvyTuB9FbWIuFOwXI5Q&" \
        "payer_email=r.edacted%40gmail.com&txn_id=2VE88146H0920340B&" \
        "payment_type=instant&payer_business_name=Best.shelter&last_name=REDACTED&" \
        "receiver_email=paypal%40sheltermanager.com&payment_fee=&shipping_discount=0.00&" \
        "insurance_amount=0.00&receiver_id=FV7MZN3X9Y3NC&txn_type=web_accept&" \
        "item_name=sheltermanager.com+12+month+hosting++ac1234&discount=0.00&" \
        "mc_currency=EUR&item_number=T0420124547632NS&residence_country=CZ&" \
        "shipping_method=Default&transaction_subject=&payment_gross=&ipn_track_id=c350d6ae80290"

    def setUp(self):
        """ Creates a person and a received/due payment for them """
        self.paypal = asm3.paymentprocessor.paypal.PayPal(base.get_dbo())
        data = {
            "title": "Mr",
            "forenames": "Test",
            "surname": "Testing",
            "ownertype": "1",
            "address": "123 test street"
        }
        post = asm3.utils.PostedData(data, "en")
        self.personid = asm3.person.insert_person_from_form(base.get_dbo(), post, "test", geocode=False)
        data = {
            "person": str(self.personid),
            "animal": "1",
            "type":   "1",
            "payment": "1",
            "frequency": "0",
            "amount": "1000",
            "due": base.today_display()
        }
        post = asm3.utils.PostedData(data, "en")
        self.dueid = asm3.financial.insert_donation_from_form(base.get_dbo(), "test", post)
        data = {
            "person": str(self.personid),
            "animal": "1",
            "type":   "1",
            "payment": "1",
            "frequency": "0",
            "amount": "1000",
            "received": base.today_display()
        }
        post = asm3.utils.PostedData(data, "en")
        self.recid = asm3.financial.insert_donation_from_form(base.get_dbo(), "test", post)

    def tearDown(self):
        asm3.financial.delete_donation(base.get_dbo(), "test", self.dueid)
        asm3.financial.delete_donation(base.get_dbo(), "test", self.recid)
        asm3.person.delete_person(base.get_dbo(), "test", self.personid)

    def test_paypal_ipn_incomplete(self):
        ipndata = self.sample_ipn_paypal.replace("payment_status=Completed", "payment_status=Pending")
        with self.assertRaises(asm3.paymentprocessor.paypal.IncompleteStatusError):
            self.paypal.receive(ipndata, validate_ipn=False)

    def test_paypal_ipn_badpayref(self):
        ipndata = self.sample_ipn_paypal.replace("item_number=T0420124547632NS", "item_number=BAD")
        with self.assertRaises(asm3.paymentprocessor.base.PayRefError):
            self.paypal.receive(ipndata, validate_ipn=False)

    def test_paypal_ipn_invalidpayref(self):
        ownercode = base.get_dbo().query_string("SELECT ownercode FROM owner WHERE ID=?", [self.personid])
        payref = ownercode + "-" + "WONTEXIST"
        ipndata = self.sample_ipn_paypal.replace("item_number=T0420124547632NS", "item_number=" + payref)
        with self.assertRaises(asm3.paymentprocessor.base.PayRefError):
            self.paypal.receive(ipndata, validate_ipn=False)

    def test_paypal_ipn_alreadyreceived(self):
        ownercode = base.get_dbo().query_string("SELECT ownercode FROM owner WHERE ID=?", [self.personid])
        recnum = base.get_dbo().query_string("SELECT receiptnumber FROM ownerdonation WHERE ID=?", [self.recid])
        payref = ownercode + "-" + recnum
        ipndata = self.sample_ipn_paypal.replace("item_number=T0420124547632NS", "item_number=" + payref)
        with self.assertRaises(asm3.paymentprocessor.base.AlreadyReceivedError):
            self.paypal.receive(ipndata, validate_ipn=False)

    def test_paypal_ipn_success(self):
        ownercode = base.get_dbo().query_string("SELECT ownercode FROM owner WHERE ID=?", [self.personid])
        recnum = base.get_dbo().query_string("SELECT receiptnumber FROM ownerdonation WHERE ID=?", [self.dueid])
        payref = ownercode + "-" + recnum
        ipndata = self.sample_ipn_paypal.replace("item_number=T0420124547632NS", "item_number=" + payref)
        self.paypal.receive(ipndata, validate_ipn=False)
        self.assertEqual(982, base.get_dbo().query_int("select fee from ownerdonation where id=?", [self.dueid]))

class TestSquarePaymentProcessor(unittest.TestCase):
    personid = 0
    dueid = 0
    recid = 0

    sample_square_payload = { 
        "merchant_id": "MLQNJB9HG03CY",
        "type": "payment.updated",
        "event_id": "573e54aa-8312-3c15-a5d3-4ea37c97e505",
        "created_at": "2025-01-28T14:50:21.366Z",
        "data": {
            "type": "payment", 
            "id": "x4oOdklFChBnLz7ZwCLZQUCGnFcZY",
            "object": {
                "payment": {
                    "amount_money": {
                        "amount": 5000,
                        "currency": "GBP"
                    },
                    "application_details": {
                        "application_id": "sandbox-sq0idb-lky4CaPAWmDnHY3YtYxINg",
                        "square_product": "ECOMMERCE_API"
                    },
                    "capabilities": ["EDIT_AMOUNT_UP", "EDIT_AMOUNT_DOWN", "EDIT_TIP_AMOUNT_UP", "EDIT_TIP_AMOUNT_DOWN" ],
                    "created_at": "2025-01-28T14:50:20.056Z",
                    "external_details": {
                        "source": "Developer Control Panel",
                        "type": "CARD"
                    },
                    "id": "x4oOdklFChBnLz7ZwCLZQUCGnFcZY",
                    "location_id": "LQQNMQC474MTG",
                    "note": "/home/adam-spencer/workspace/asmtestdb.db-SP000002-00000003",
                    "order_id": "xbzRl03PO4FBycmN0ZjtajW2x5CZY",
                    "receipt_number": "x4oO",
                    "receipt_url": "https://squareupsandbox.com/receipt/preview/x4oOdklFChBnLz7ZwCLZQUCGnFcZY",
                    "source_type": "EXTERNAL",
                    "status": "COMPLETED",
                    "total_money": {
                        "amount": 5000, "currency": "GBP"
                    },
                    "updated_at": "2025-01-28T14:50:20.164Z",
                    "version": 1
                }
            }
        }
    }

    def setUp(self):
        """ Creates a person and a received/due payment for them """
        self.square = asm3.paymentprocessor.square.Square(base.get_dbo())
        data = {
            "title": "Mr",
            "forenames": "Test",
            "surname": "Testing",
            "ownertype": "1",
            "address": "123 test street"
        }
        post = asm3.utils.PostedData(data, "en")
        self.personid = asm3.person.insert_person_from_form(base.get_dbo(), post, "test", geocode=False)
        data = {
            "person": str(self.personid),
            "animal": "1",
            "type":   "1",
            "payment": "1",
            "frequency": "0",
            "amount": "1000",
            "due": base.today_display()
        }
        post = asm3.utils.PostedData(data, "en")
        self.dueid = asm3.financial.insert_donation_from_form(base.get_dbo(), "test", post)
        data = {
            "person": str(self.personid),
            "animal": "1",
            "type":   "1",
            "payment": "1",
            "frequency": "0",
            "amount": "1000",
            "received": base.today_display()
        }
        post = asm3.utils.PostedData(data, "en")
        self.recid = asm3.financial.insert_donation_from_form(base.get_dbo(), "test", post)

    def tearDown(self):
        asm3.financial.delete_donation(base.get_dbo(), "test", self.dueid)
        asm3.financial.delete_donation(base.get_dbo(), "test", self.recid)
        asm3.person.delete_person(base.get_dbo(), "test", self.personid)
    
    def test_square_ipn_success(self):
        ownercode = base.get_dbo().query_string("SELECT ownercode FROM owner WHERE ID=?", [self.personid])
        recnum = base.get_dbo().query_string("SELECT receiptnumber FROM ownerdonation WHERE ID=?", [self.dueid])
        payref = ownercode + "-" + recnum
        self.sample_square_payload["data"]["object"]["payment"]["note"] = payref
        self.sample_square_payload = json.dumps(self.sample_square_payload)
        self.square.receive(self.sample_square_payload)
        self.assertEqual(1000, base.get_dbo().query_int("select donation from ownerdonation where id=?", [self.dueid]))

