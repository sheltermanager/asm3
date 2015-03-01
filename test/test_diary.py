#!/usr/bin/python env

import unittest
import base

import animal
import diary
import utils

class TestDiary(unittest.TestCase):
 
    nid = 0

    def setUp(self):
        data = {
            "diarydate":   base.today_display(),
            "diarytime":   "09:00",
            "diaryfor":    "user",
            "subject":     "Test",
            "note":        "TestNote"
        }
        post = utils.PostedData(data, "en")
        self.nid = diary.insert_diary_from_form(base.get_dbo(), "test", 0, 0, post)

    def tearDown(self):
        diary.delete_diary(base.get_dbo(), "test", self.nid)
 
    def test_get_between_two_dates(self):
        diary.get_between_two_dates(base.get_dbo(), "user", "2014-01-01", "2014-01-31")

    def test_get_uncompleted_upto_today(self):
        diary.get_uncompleted_upto_today(base.get_dbo(), "user")

    def test_get_completed_upto_today(self):
        diary.get_completed_upto_today(base.get_dbo(), "user")

    def test_get_all_upto_today(self):
        assert len(diary.get_all_upto_today(base.get_dbo(), "user")) > 0

    def test_get_future(self):
        diary.get_future(base.get_dbo(), "user")

    def test_complete_diary_note(self):
        diary.complete_diary_note(base.get_dbo(), "user", self.nid)

    def test_rediarise_diary_note(self):
        diary.rediarise_diary_note(base.get_dbo(), "user", self.nid, base.today())

    def test_get_animal_tasks(self):
        diary.get_animal_tasks(base.get_dbo())

    def test_get_person_tasks(self):
        diary.get_person_tasks(base.get_dbo())

    def test_get_diarytasks(self):
        diary.get_diarytasks(base.get_dbo())

    def test_get_diarytask_name(self):
        diary.get_diarytask_name(base.get_dbo(), 0)

    def test_get_diarytask_details(self):
        diary.get_diarytask_details(base.get_dbo(), 0)

    def test_get_diary(self):
        assert diary.get_diary(base.get_dbo(), self.nid) is not None

    def test_get_diaries(self):
        diary.get_diaries(base.get_dbo(), 0, 0)

    def test_update_diary_from_form(self):
        data = {
            "diarydate":   base.today_display(),
            "diarytime":   "09:00",
            "diaryfor":    "user",
            "subject":     "Test",
            "note":        "TestNote"
        }
        post = utils.PostedData(data, "en")
        diary.update_diary_from_form(base.get_dbo(), "test", post)

    def test_execute_diary_task(self):
        data = {
            "animalname": "TestioDiary",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1"
        }
        post = utils.PostedData(data, "en")
        animalid, code = animal.insert_animal_from_form(base.get_dbo(), post, "test")
        data = {
            "name": "Test",
            "type": "0"
        }
        post = utils.PostedData(data, "en")
        headid = diary.insert_diarytaskhead_from_form(base.get_dbo(), "test", post)
        diary.update_diarytaskhead_from_form(base.get_dbo(), "test", post)
        data = {
            "taskid": str(headid),
            "daypivot": "1",
            "whofor":   "user",
            "subject":  "Testtask",
            "note":     "Testtasknote"
        }
        post = utils.PostedData(data, "en")
        diary.insert_diarytaskdetail_from_form(base.get_dbo(), "test", post)
        diary.update_diarytaskdetail_from_form(base.get_dbo(), "test", post)
        diary.execute_diary_task(base.get_dbo(), "test", diary.ANIMAL, headid, animalid, base.today())
        diary.delete_diarytask(base.get_dbo(), "test", headid)
        animal.delete_animal(base.get_dbo(), "test", animalid)


