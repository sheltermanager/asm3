
import unittest
import base

import asm3.service

class TestService(unittest.TestCase):

    def test_flood_protect(self):
        asm3.service.flood_protect("online_form_post", "1.1.1.1")
        with self.assertRaises(asm3.utils.ASMError):
            asm3.service.flood_protect("online_form_post", "1.1.1.1")

    def test_safe_cache_key(self):
        s = asm3.service.safe_cache_key("animal_image", "?animalid=52&cache=bust")
        self.assertEqual(-1, s.find("cache"))

    def test_sign_document_page(self):
        self.assertNotEqual(0, len(asm3.service.sign_document_page(base.get_dbo(), 0, "test@example.com")))

    def test_handler(self):
        TESTS = [
            "?method=animal_image&animalid=1",
            "?method=animal_thumbnail&animalid=1",
            "?method=animal_view&animalid=1&template=animalview&utemplate=animalview",
            "?method=animal_view_adoptable_js",
            #"?method=dbfs_image&title=logo.jpg",
            #"?method=extra_image&title=logo.jpg",
            "?method=media_image&mediaid=1",
            "?method=html_adoptable_animals",
            "?method=html_deceased_animals",
            "?method=html_events",
            "?method=html_flagged_animals",
            "?method=html_held_animals",
            "?method=html_permfoster_animals",
            "?method=html_stray_animals",
            "?method=json_adoptable_animal&animalid=1&username=user&password=letmein",
            "?method=json_adoptable_animals_xp",
            "?method=json_adoptable_animals&username=user&password=letmein",
            "?method=jsonp_adoptable_animals&username=user&password=letmein",
            "?method=xml_adoptable_animal",
            "?method=xml_adoptable_animals&username=user&password=letmein",
            "?method=json_adopted_animals&username=user&password=letmein",
            "?method=xml_adopted_animals&username=user&password=letmein",
            "?method=json_found_animals&username=user&password=letmein",
            "?method=jsonp_found_animals&username=user&password=letmein",
            "?method=xml_found_animals&username=user&password=letmein",
            "?method=json_held_animals&username=user&password=letmein",
            "?method=xml_held_animals&username=user&password=letmein",
            "?method=jsonp_held_animals&username=user&password=letmein",
            "?method=json_lost_animals&username=user&password=letmein",
            "?method=jsonp_lost_animals&username=user&password=letmein",
            "?method=xml_lost_animals&username=user&password=letmein",
            "?method=json_recent_adoptions&username=user&password=letmein",
            "?method=jsonp_recent_adoptions&username=user&password=letmein",
            "?method=xml_recent_adoptions&username=user&password=letmein",
            "?method=jsonp_recent_changes&username=user&password=letmein",
            "?method=json_recent_changes&username=user&password=letmein",
            "?method=xml_recent_changes&username=user&password=letmein",
            "?method=jsonp_shelter_animals&username=user&password=letmein",
            "?method=json_shelter_animals&username=user&password=letmein",
            "?method=xml_shelter_animals&username=user&password=letmein",
            "?method=json_stray_animals&username=user&password=letmein",
            "?method=xml_stray_animals&username=user&password=letmein",
            "?method=rss_timeline&username=user&password=letmein",
            "?method=online_form_html&formid=1&username=user&password=letmein",
            "?method=online_form_json&formid=1&username=user&password=letmein"
        ]
        dbo = base.get_dbo()
        for q in TESTS:
            items = q[1:].split("&")
            d = {}
            for i in items:
                k, v = i.split("=")
                d[k] = v
            asm3.service.handler(asm3.utils.PostedData(d, dbo.locale), dbo.installpath, "1.1.1.1", "", "Mozilla",  q)
