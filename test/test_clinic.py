#!/usr/bin/python env

import unittest
import base

import clinic
import utils

class TestClinic(unittest.TestCase):
 
    anid = 0
    inid = 0

    def setUp(self):
        data = {
            "animal": "1",
            "person": "1",
            "apptdate": base.today_display(),
            "appttime": "12:00:00",
            "status": "1",
        }
        post = utils.PostedData(data, "en")
        self.anid = clinic.insert_appointment_from_form(base.get_dbo(), "test", post)
        data = {
            "appointmentid": str(self.anid),
            "description": "foo",
            "amount": "50"
        }
        post = utils.PostedData(data, "en")
        self.inid = clinic.insert_invoice_from_form(base.get_dbo(), "test", post)

    def tearDown(self):
        clinic.delete_invoice(base.get_dbo(), "test", self.inid)
        clinic.delete_appointment(base.get_dbo(), "test", self.anid)

    def test_get_appointment(self):
        assert clinic.get_appointment(base.get_dbo(), self.anid) is not None

    def test_get_appointments_today(self):
        assert len(clinic.get_appointments_today(base.get_dbo())) > 0

    def test_get_invoice_items(self):
        assert len(clinic.get_invoice_items(base.get_dbo(), self.anid)) > 0

    def test_appointment_crud(self):
        data = {
            "animal": "2",
            "person": "2",
            "apptdate": base.today_display(),
            "appttime": "08:00:00",
            "status": "2",
        }
        post = utils.PostedData(data, "en")
        nid = clinic.insert_appointment_from_form(base.get_dbo(), "test", post)
        data["appointmentid"] = nid
        clinic.update_appointment_from_form(base.get_dbo(), "test", post)
        clinic.delete_appointment(base.get_dbo(), "test", nid)

    def test_invoice_crud(self):
        data = {
            "appointmentid": self.anid,
            "description": "bar",
            "amount": "1500"
        }
        post = utils.PostedData(data, "en")
        nid = clinic.insert_invoice_from_form(base.get_dbo(), "test", post)
        data["itemid"] = nid
        clinic.update_invoice_from_form(base.get_dbo(), "test", post)
        clinic.delete_invoice(base.get_dbo(), "test", nid)

    def test_updates(self):
        clinic.update_appointment_to_waiting(base.get_dbo(), "test", self.anid, base.today())
        clinic.update_appointment_to_with_vet(base.get_dbo(), "test", self.anid, base.today())
        clinic.update_appointment_to_complete(base.get_dbo(), "test", self.anid, base.today())

    def test_auto_update_statuses(self):
        clinic.auto_update_statuses(base.get_dbo())

