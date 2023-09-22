
import unittest
import base

import asm3.automail

class TestAutomail(unittest.TestCase):

    def test_adopter_followup_query(self):
        asm3.automail._adopter_followup_query(base.get_dbo(), base.today())

    def test_clinic_reminder_query(self):
        asm3.automail._clinic_reminder_query(base.get_dbo(), base.today())

    def test_fosterer_weekly_activefosterers(self):
        asm3.automail._fosterer_weekly_activefosterers(base.get_dbo())

    def test_fosterer_weekly_animals(self):
        asm3.automail._fosterer_weekly_animals(base.get_dbo(), 1)

    def test_licence_reminder_query(self):
        asm3.automail._licence_reminder_query(base.get_dbo(), base.today())