
import unittest
import base

import asm3.animal, asm3.movement
import asm3.utils

class TestMovement(unittest.TestCase):

    def test_get_movements(self):
        asm3.movement.get_movements(base.get_dbo(), 2)
 
    def test_get_active_reservations(self):
        asm3.movement.get_active_reservations(base.get_dbo())

    def test_get_active_transports(self):
        asm3.movement.get_active_transports(base.get_dbo())

    def test_get_recent_adoptions(self):
        asm3.movement.get_recent_adoptions(base.get_dbo())
 
    def test_get_recent_nonfosteradoption(self):
        asm3.movement.get_recent_nonfosteradoption(base.get_dbo())
 
    def test_get_recent_transfers(self):
        asm3.movement.get_recent_transfers(base.get_dbo())
             
    def test_get_recent_unneutered_adoptions(self):
        asm3.movement.get_recent_unneutered_adoptions(base.get_dbo())

    def test_get_trial_adoptions(self):
        asm3.movement.get_trial_adoptions(base.get_dbo())

    def test_get_animal_movements(self):
        asm3.movement.get_animal_movements(base.get_dbo(), 1)

    def test_get_animal_transports(self):
        asm3.movement.get_animal_transports(base.get_dbo(), 1)

    def test_get_person_movements(self):
        asm3.movement.get_person_movements(base.get_dbo(), 1)

    def test_get_transport_two_dates(self):
        asm3.movement.get_transport_two_dates(base.get_dbo(), base.today(), base.today())

    def test_insert_reserve(self):
        data = {
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        aid, code = asm3.animal.insert_animal_from_form(base.get_dbo(), post, "test")
        asm3.movement.insert_reserve(base.get_dbo(), "test", 1, aid, base.today() )

    def test_movement_crud(self):
        data = {
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        aid, code = asm3.animal.insert_animal_from_form(base.get_dbo(), post, "test")
        data = {
            "animal": str(aid),
            "person": 1,
            "movementdate": base.today_display(),
            "type": "1",
        }
        post = asm3.utils.PostedData(data, "en")
        mid = asm3.movement.insert_movement_from_form(base.get_dbo(), "test", post)
        post.data["movementid"] = str(mid)
        asm3.movement.update_movement_from_form(base.get_dbo(), "test", post)
        asm3.movement.delete_movement(base.get_dbo(), "test", mid)
        asm3.animal.delete_animal(base.get_dbo(), "test", aid)

    def test_transport_crud(self):
        data = {
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        aid, code = asm3.animal.insert_animal_from_form(base.get_dbo(), post, "test")
        data = {
            "animal": "1",
            "driver": "1",
            "pickup": "1",
            "dropoff": "1",
            "pickupdate": base.today_display(),
            "dropoffdate": base.today_display(),
            "status": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        tid = asm3.movement.insert_transport_from_form(base.get_dbo(), "test", post)
        post.data["transportid"] = str(tid)
        asm3.movement.update_transport_from_form(base.get_dbo(), "test", post)
        asm3.movement.delete_transport(base.get_dbo(), "test", tid)
        asm3.animal.delete_animal(base.get_dbo(), "test", aid)

    def test_auto_cancel_reservations(self):
        asm3.movement.auto_cancel_reservations(base.get_dbo())

