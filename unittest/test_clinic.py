
import unittest
import base

import datetime

import asm3.clinic
import asm3.financial
import asm3.utils

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
        post = asm3.utils.PostedData(data, "en")
        self.anid = asm3.clinic.insert_appointment_from_form(base.get_dbo(), "test", post)
        data = {
            "appointmentid": str(self.anid),
            "description": "foo",
            "amount": "50"
        }
        post = asm3.utils.PostedData(data, "en")
        self.inid = asm3.clinic.insert_invoice_from_form(base.get_dbo(), "test", post)

    def tearDown(self):
        asm3.clinic.delete_invoice(base.get_dbo(), "test", self.inid)
        asm3.clinic.delete_appointment(base.get_dbo(), "test", self.anid)

    def test_get_animal_appointments(self):
        assert len(asm3.clinic.get_animal_appointments(base.get_dbo(), 1)) > 0

    def test_get_animal_appointments_due(self):
        asm3.clinic.get_animal_appointments_due(base.get_dbo(), 1, base.today(), base.today() + datetime.timedelta(days=7))

    def test_get_person_appointments(self):
        assert len(asm3.clinic.get_person_appointments(base.get_dbo(), 1)) > 0

    def test_get_appointment(self):
        assert asm3.clinic.get_appointment(base.get_dbo(), self.anid) is not None

    def test_get_appointments_today(self):
        assert len(asm3.clinic.get_appointments_today(base.get_dbo())) > 0

    def test_get_appointments_two_dates(self):
        asm3.clinic.get_appointments_two_dates(base.get_dbo(), "2001-01-01", "2020-01-01")

    def test_get_appointments_tabs(self):
        asm3.clinic.get_animal_appointments(base.get_dbo(), 1)
        asm3.clinic.get_person_appointments(base.get_dbo(), 1)

    def test_get_invoice_items(self):
        assert len(asm3.clinic.get_invoice_items(base.get_dbo(), self.anid)) > 0

    def test_appointment_crud(self):
        data = {
            "animal": "2",
            "person": "2",
            "apptdate": base.today_display(),
            "appttime": "08:00:00",
            "status": "2",
        }
        post = asm3.utils.PostedData(data, "en")
        nid = asm3.clinic.insert_appointment_from_form(base.get_dbo(), "test", post)
        data["appointmentid"] = nid
        asm3.clinic.update_appointment_from_form(base.get_dbo(), "test", post)
        asm3.clinic.delete_appointment(base.get_dbo(), "test", nid)

    def test_invoice_crud(self):
        data = {
            "appointmentid": self.anid,
            "description": "bar",
            "amount": "1500"
        }
        post = asm3.utils.PostedData(data, "en")
        nid = asm3.clinic.insert_invoice_from_form(base.get_dbo(), "test", post)
        data["itemid"] = nid
        asm3.clinic.update_invoice_from_form(base.get_dbo(), "test", post)
        asm3.clinic.delete_invoice(base.get_dbo(), "test", nid)

    def test_updates(self):
        asm3.clinic.update_appointment_to_waiting(base.get_dbo(), "test", self.anid, base.today())
        asm3.clinic.update_appointment_to_with_vet(base.get_dbo(), "test", self.anid, base.today())
        asm3.clinic.update_appointment_to_complete(base.get_dbo(), "test", self.anid, base.today())

    def test_auto_update_statuses(self):
        asm3.clinic.auto_update_statuses(base.get_dbo())

