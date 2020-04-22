
import unittest
import base

import asm3.animal
import asm3.diary
import asm3.utils

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
        post = asm3.utils.PostedData(data, "en")
        self.nid = asm3.diary.insert_diary_from_form(base.get_dbo(), "test", 0, 0, post)

    def tearDown(self):
        asm3.diary.delete_diary(base.get_dbo(), "test", self.nid)
 
    def test_get_between_two_dates(self):
        asm3.diary.get_between_two_dates(base.get_dbo(), "user", base.today(), base.today())

    def test_get_uncompleted_upto_today(self):
        asm3.diary.get_uncompleted_upto_today(base.get_dbo(), "user")

    def test_get_completed_upto_today(self):
        asm3.diary.get_completed_upto_today(base.get_dbo(), "user")

    def test_get_all_upto_today(self):
        assert len(asm3.diary.get_all_upto_today(base.get_dbo(), "user")) > 0

    def test_get_future(self):
        asm3.diary.get_future(base.get_dbo(), "user")

    def test_complete_diary_note(self):
        asm3.diary.complete_diary_note(base.get_dbo(), "user", self.nid)

    def test_complete_diary_notes_for_animal(self):
        asm3.diary.complete_diary_notes_for_animal(base.get_dbo(), "user", 1)

    def test_rediarise_diary_note(self):
        asm3.diary.rediarise_diary_note(base.get_dbo(), "user", self.nid, base.today())

    def test_get_animal_tasks(self):
        asm3.diary.get_animal_tasks(base.get_dbo())

    def test_get_person_tasks(self):
        asm3.diary.get_person_tasks(base.get_dbo())

    def test_get_diarytasks(self):
        asm3.diary.get_diarytasks(base.get_dbo())

    def test_get_diarytask_name(self):
        asm3.diary.get_diarytask_name(base.get_dbo(), 0)

    def test_get_diarytask_details(self):
        asm3.diary.get_diarytask_details(base.get_dbo(), 0)

    def test_get_diary(self):
        assert asm3.diary.get_diary(base.get_dbo(), self.nid) is not None

    def test_get_diaries(self):
        asm3.diary.get_diaries(base.get_dbo(), 0, 0)

    def test_update_diary_from_form(self):
        data = {
            "diaryid":     str(self.nid),
            "diarydate":   base.today_display(),
            "diarytime":   "09:00",
            "diaryfor":    "user",
            "subject":     "Test",
            "note":        "TestNote"
        }
        post = asm3.utils.PostedData(data, "en")
        asm3.diary.update_diary_from_form(base.get_dbo(), "test", post)

    def test_execute_diary_task(self):
        data = {
            "animalname": "TestioDiary",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        animalid, code = asm3.animal.insert_animal_from_form(base.get_dbo(), post, "test")
        data = {
            "name": "Test",
            "type": "0"
        }
        post = asm3.utils.PostedData(data, "en")
        headid = asm3.diary.insert_diarytaskhead_from_form(base.get_dbo(), "test", post)
        asm3.diary.update_diarytaskhead_from_form(base.get_dbo(), "test", post)
        data = {
            "taskid": str(headid),
            "daypivot": "1",
            "whofor":   "user",
            "subject":  "Testtask",
            "note":     "Testtasknote"
        }
        post = asm3.utils.PostedData(data, "en")
        asm3.diary.insert_diarytaskdetail_from_form(base.get_dbo(), "test", post)
        asm3.diary.update_diarytaskdetail_from_form(base.get_dbo(), "test", post)
        asm3.diary.execute_diary_task(base.get_dbo(), "test", asm3.diary.ANIMAL, headid, animalid, base.today())
        asm3.diary.delete_diarytask(base.get_dbo(), "test", headid)
        asm3.animal.delete_animal(base.get_dbo(), "test", animalid)


