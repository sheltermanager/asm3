#!/usr/bin/python env

import unittest
import base

import animal, movement
import utils

class TestMovement(unittest.TestCase):

    def test_get_movements(self):
        movement.get_movements(base.get_dbo(), 2)
 
    def test_get_active_reservations(self):
        movement.get_active_reservations(base.get_dbo())

    def test_get_active_transports(self):
        movement.get_active_transports(base.get_dbo())

    def test_get_recent_adoptions(self):
        movement.get_recent_adoptions(base.get_dbo())
 
    def test_get_recent_nonfosteradoption(self):
        movement.get_recent_nonfosteradoption(base.get_dbo())
 
    def test_get_recent_transfers(self):
        movement.get_recent_transfers(base.get_dbo())
             
    def test_get_recent_unneutered_adoptions(self):
        movement.get_recent_unneutered_adoptions(base.get_dbo())

    def test_get_trial_adoptions(self):
        movement.get_trial_adoptions(base.get_dbo())

    def test_get_animal_movements(self):
        movement.get_animal_movements(base.get_dbo(), 1)

    def test_get_animal_transports(self):
        movement.get_animal_transports(base.get_dbo(), 1)

    def test_get_person_movements(self):
        movement.get_person_movements(base.get_dbo(), 1)

    def test_get_transport_two_dates(self):
        movement.get_transport_two_dates(base.get_dbo(), base.today(), base.today())

    def test_movement_crud(self):
        data = {
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1"
        }
        post = utils.PostedData(data, "en")
        aid, code = animal.insert_animal_from_form(base.get_dbo(), post, "test")
        data = {
            "animal": str(aid),
            "person": 1,
            "movementdate": base.today_display(),
            "type": "1",
        }
        post = utils.PostedData(data, "en")
        mid = movement.insert_movement_from_form(base.get_dbo(), "test", post)
        post.data["movementid"] = str(mid)
        movement.update_movement_from_form(base.get_dbo(), "test", post)
        movement.delete_movement(base.get_dbo(), "test", mid)
        animal.delete_animal(base.get_dbo(), "test", aid)

    def test_transport_crud(self):
        data = {
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1"
        }
        post = utils.PostedData(data, "en")
        aid, code = animal.insert_animal_from_form(base.get_dbo(), post, "test")
        data = {
            "animal": "1",
            "driver": "1",
            "pickup": "1",
            "dropoff": "1",
            "pickupdate": base.today_display(),
            "dropoffdate": base.today_display(),
            "status": "1"
        }
        post = utils.PostedData(data, "en")
        tid = movement.insert_transport_from_form(base.get_dbo(), "test", post)
        post.data["transportid"] = str(tid)
        movement.update_transport_from_form(base.get_dbo(), "test", post)
        movement.delete_transport(base.get_dbo(), "test", tid)
        animal.delete_animal(base.get_dbo(), "test", aid)

    def test_auto_cancel_reservations(self):
        movement.auto_cancel_reservations(base.get_dbo())

