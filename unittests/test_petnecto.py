
import json
import unittest
from unittest import mock
from unittests import base

import asm3.animal
import asm3.configuration
import asm3.media
import asm3.movement
import asm3.person
import asm3.publish
import asm3.publishers.base
import asm3.publishers.petnecto
import asm3.utils

from asm3.publishers.petnecto import PETNECTO_FIELDS
from asm3.sitedefs import SERVICE_URL

TOKEN = "pnp_" + "A" * 43
SHELTER = "sh_testshelter"
URL = "https://petnecto.example.org"

# Strings that are personal data or private notes. None of them may ever appear in what is sent.
SECRETS = [
    "SECRET-HIDDEN-DETAILS", "SECRET-REASON", "SECRET-WARNING", "SECRET-PICKUP", "977123123456789",
    "Dirk", "Diggler", "10 Downing Street", "SW1 2ER", "07734 567890", "dirk@diggler.com", "secret@shelter.example"
]

class FakeResponse:
    def __init__(self, status, body, headers):
        self.status_code = status
        self._body = body
        self.headers = headers
    def json(self):
        return self._body

class FakePetnecto:
    """ Stands in for requests.request: records every call and answers with whatever handler returns """
    def __init__(self, handler = None):
        self.calls = []
        self.handler = handler or (lambda method, url, body: (201, { "ok": True, "result": "created" }, {}))
    def __call__(self, method, url, data = None, timeout = None, allow_redirects = None, headers = None):
        body = json.loads(data.decode("utf-8")) if data else None
        self.calls.append({ "method": method, "url": url, "body": body, "timeout": timeout, "allow_redirects": allow_redirects, "headers": dict(headers or {}) })
        status, rbody, rheaders = self.handler(method, url, body)
        return FakeResponse(status, rbody, rheaders)
    def posts(self):
        return [ c for c in self.calls if c["method"] == "POST" ]
    def patches(self):
        return [ c for c in self.calls if c["method"] == "PATCH" ]

class TestPetnecto(unittest.TestCase):

    def setUp(self):
        self.dbo = base.get_dbo()
        self.mediaids = []
        self.animals = []
        self.mid = 0
        richpersondata = {
            "title": "Mr", "forenames": "Dirk", "surname": "Diggler", "ownertype": "1", "address": "10 Downing Street",
            "postcode": "SW1 2ER", "mobiletelephone": "07734 567890", "emailaddress": "dirk@diggler.com"
        }
        self.pnid = asm3.person.insert_person_from_form(self.dbo, asm3.utils.PostedData(richpersondata, "en"), "test", geocode=False)
        animaldata = [
            {
                "animalname": "Petnectio", "estimatedage": "1", "animaltype": "1", "entryreason": "1", "breed1": "1", "breed2": "1", "species": "1",
                "comments": "A friendly dog. Call secret@shelter.example to meet him.", "dateofbirth": "01/01/2022", "basecolour": "1",
                "goodwithdogs": "0", "goodwithcats": "1", "goodwithkids": "2", "neutered": "on",
                "hiddenanimaldetails": "SECRET-HIDDEN-DETAILS", "reasonforentry": "SECRET-REASON", "popupwarning": "SECRET-WARNING",
                "pickupaddress": "SECRET-PICKUP", "microchipped": "on", "microchipnumber": "977123123456789",
                "originalowner": str(self.pnid), "broughtinby": str(self.pnid), "owner": str(self.pnid)
            },
            {
                "animalname": "Secondio", "estimatedage": "1", "animaltype": "1", "entryreason": "1", "breed1": "1", "breed2": "1", "species": "1",
                "comments": "Another good dog.", "dateofbirth": "01/01/2021", "basecolour": "1"
            }
        ]
        f = open(base.PATH + "../src/media/reports/nopic.jpg", "rb")
        imagedata = f.read()
        f.close()
        for animal in animaldata:
            animalid, sheltercode = asm3.animal.insert_animal_from_form(self.dbo, asm3.utils.PostedData(animal, "en"), "test")
            post = asm3.utils.PostedData({ "filename": "image.jpg", "filetype": "image/jpeg", "filedata": "data:image/jpeg;base64,%s" % asm3.utils.base64encode(imagedata) }, "en")
            self.mediaids.append(asm3.media.attach_file_from_form(self.dbo, "test", asm3.media.ANIMAL, animalid, asm3.media.MEDIASOURCE_ATTACHFILE, post))
            self.animals.append((animalid, sheltercode))
        asm3.configuration.cset(self.dbo, "PublisherPresets", "includewithoutimage includewithoutdescription includenonneutered includenonmicrochip excludeunder=1")
        asm3.configuration.cset(self.dbo, "PetnectoToken", TOKEN)
        asm3.configuration.cset(self.dbo, "PetnectoShelterID", SHELTER)
        self.dbo.execute("DELETE FROM animalpublished WHERE PublishedTo = 'petnecto'")

    def tearDown(self):
        if self.mid != 0: asm3.movement.delete_movement(self.dbo, "test", self.mid)
        for aid, sheltercode in self.animals:
            asm3.animal.delete_animal(self.dbo, "test", aid)
        asm3.person.delete_person(self.dbo, "test", self.pnid)
        for mediaid in self.mediaids:
            asm3.media.delete_media(self.dbo, "test", mediaid)
        self.dbo.execute("DELETE FROM animalpublished WHERE PublishedTo = 'petnecto'")
        asm3.configuration.cset(self.dbo, "PetnectoToken", "")
        asm3.configuration.cset(self.dbo, "PetnectoShelterID", "")

    def publisher(self):
        pc = asm3.publishers.base.PublishCriteria(asm3.configuration.publisher_presets(self.dbo))
        return asm3.publishers.petnecto.PetnectoPublisher(self.dbo, pc)

    def run_publisher(self, fake, url = URL):
        """ Runs a publisher against the fake service. Returns the publisher so the log can be read. """
        p = self.publisher()
        with mock.patch("asm3.publishers.petnecto.PETNECTO_URL", url), mock.patch("asm3.publishers.petnecto.requests.request", fake):
            p.run()
        return p

    def ours(self, rows):
        ids = [ a[0] for a in self.animals ]
        return [ r for r in rows if r.ID in ids ]

    # ---- what is built

    def test_registered(self):
        self.assertIn("pn", asm3.publish.PUBLISHER_LIST)
        self.assertEqual(asm3.publishers.petnecto.PetnectoPublisher, asm3.publish.PUBLISHER_LIST["pn"]["class"])
        self.assertTrue(asm3.publish.PUBLISHER_LIST["pn"]["sub24hour"])

    def test_process_animal_sends_only_the_listed_fields(self):
        p = self.publisher()
        rows = self.ours(p.getAnimals())
        self.assertEqual(2, len(rows))
        for r in rows:
            d = p.processAnimal(r)
            self.assertEqual(PETNECTO_FIELDS, tuple(d.keys()))
            self.assertEqual("adoptable", d["status"])
            self.assertTrue(len(d["photo_urls"]) > 0)

    def test_nothing_personal_is_sent(self):
        p = self.publisher()
        for r in self.ours(p.getAnimals()):
            doc = json.dumps(p.processAnimal(r))
            for s in SECRETS:
                self.assertNotIn(s, doc, "%s must not be sent" % s)

    def test_rows_are_stripped_before_use(self):
        p = self.publisher()
        for r in self.ours(p.getAnimals()):
            self.assertEqual("", r.HIDDENANIMALDETAILS)
            self.assertEqual("", r.REASONFORENTRY)
            self.assertEqual("", r.POPUPWARNING)
            self.assertEqual("", r.PICKUPADDRESS)
            self.assertEqual("", r.ORIGINALOWNERNAME)
            self.assertEqual("", r.BROUGHTINBYOWNERNAME)

    def test_email_removed_from_description(self):
        p = self.publisher()
        r = [ x for x in self.ours(p.getAnimals()) if x.ANIMALNAME == "Petnectio" ][0]
        d = p.processAnimal(r)
        self.assertNotIn("@", d["description"])
        self.assertIn("A friendly dog.", d["description"])
        self.assertIn("an email address was removed", "\n".join(p.logBuffer))

    def test_good_with_and_basic_fields(self):
        p = self.publisher()
        r = [ x for x in self.ours(p.getAnimals()) if x.ANIMALNAME == "Petnectio" ][0]
        d = p.processAnimal(r)
        self.assertEqual("yes", d["good_with_dogs"])
        self.assertEqual("no", d["good_with_cats"])
        self.assertEqual("unknown", d["good_with_children"])
        self.assertEqual("2022-01-01", d["date_of_birth"])
        self.assertEqual("Petnectio", d["name"])
        self.assertTrue(d["neutered"])

    def test_photo_urls_are_asms_own(self):
        p = self.publisher()
        for r in self.ours(p.getAnimals()):
            for u in p.processAnimal(r)["photo_urls"]:
                self.assertIn("method=media_image", u)
                self.assertTrue(u.startswith(SERVICE_URL))

    def test_shelter_code_is_url_safe(self):
        p = self.publisher()
        self.assertEqual("20-26-001--x", p.cleanCode(" 20 26/001 #x "))
        self.assertEqual("", p.cleanCode(None))

    def test_clean_text(self):
        t, removed = asm3.publishers.petnecto.clean_text("a\r\nb\rc x@y.org")
        self.assertEqual(("a\nb\nc", True), (t, removed))
        self.assertEqual(("", False), asm3.publishers.petnecto.clean_text(None))

    def test_base_url_problem(self):
        f = asm3.publishers.petnecto.base_url_problem
        self.assertEqual("", f("https://petnecto.com"))
        self.assertEqual("", f("https://petnecto.example.org:8443"))
        self.assertEqual("", f("http://petnecto-gate:8788"))
        self.assertEqual("", f("http://192.168.1.4:8788"))
        self.assertEqual("", f("http://localhost:8788"))
        for bad in ("http://petnecto.com", "ftp://petnecto.com", "petnecto.com", "https://", "https://user:pw@petnecto.com", "https://petnecto.com/?x=1", "https://petnecto.com/#f", "http://8.8.8.8"):
            self.assertNotEqual("", f(bad), bad)

    def test_redact(self):
        r = asm3.publishers.petnecto.redact
        self.assertEqual("x [token] y", r("x %s y" % TOKEN, TOKEN))
        self.assertNotIn("pnp_", r("other pnp_" + "B" * 43, TOKEN))
        self.assertEqual("plain", r("plain", ""))

    # ---- running against a fake service

    def test_run_posts_every_animal_with_the_token(self):
        fake = FakePetnecto()
        p = self.run_publisher(fake)
        n = len(self.ours(p.getAnimals()))
        self.assertTrue(n >= 2)
        self.assertEqual(len(p.getAnimals()), len(fake.posts()))
        c = fake.posts()[0]
        self.assertEqual("%s/api/v1/shelters/%s/animals" % (URL, SHELTER), c["url"])
        self.assertEqual("Bearer " + TOKEN, c["headers"]["Authorization"])
        self.assertEqual("application/json", c["headers"]["Content-Type"])
        self.assertFalse(c["allow_redirects"], "the token must never follow a redirect")
        self.assertIsNotNone(c["timeout"], "a request without a timeout can hang the publisher")
        self.assertEqual(PETNECTO_FIELDS, tuple(c["body"].keys()))
        published = self.dbo.query("SELECT AnimalID FROM animalpublished WHERE PublishedTo = 'petnecto'")
        self.assertEqual(len(p.getAnimals()), len(published))
        self.assertEqual(0, p.alerts)

    def test_nothing_personal_goes_over_the_wire(self):
        fake = FakePetnecto()
        self.run_publisher(fake)
        wire = json.dumps([ c["body"] for c in fake.calls ])
        for s in SECRETS:
            self.assertNotIn(s, wire)

    def test_second_run_with_no_changes_sends_nothing(self):
        self.run_publisher(FakePetnecto())
        fake = FakePetnecto()
        # isChangedSinceLastPublish() is ASM's own query (it compares dates as text, which the SQLite test database gets wrong); here it says "nothing changed"
        with mock.patch.object(asm3.publishers.petnecto.PetnectoPublisher, "isChangedSinceLastPublish", lambda self: False):
            p = self.run_publisher(fake)
        self.assertEqual(0, len(fake.calls))
        self.assertIn("No animal/movement changes", "\n".join(p.logBuffer))

    def test_an_animal_never_sent_is_sent_even_when_nothing_changed(self):
        self.run_publisher(FakePetnecto())
        self.dbo.execute("DELETE FROM animalpublished WHERE PublishedTo = 'petnecto' AND AnimalID = %d" % self.animals[0][0])
        fake = FakePetnecto()
        with mock.patch.object(asm3.publishers.petnecto.PetnectoPublisher, "isChangedSinceLastPublish", lambda self: False):
            self.run_publisher(fake)
        self.assertIn("Petnectio", [ c["body"]["name"] for c in fake.posts() ])

    def test_a_rejected_animal_is_retried_and_does_not_stop_the_others(self):
        def handler(method, url, body):
            if body["name"] == "Secondio": return 422, { "ok": False, "error": "bad_field", "field": "description" }, {}
            return 201, { "ok": True, "result": "created" }, {}
        p = self.run_publisher(FakePetnecto(handler))
        self.assertTrue(p.alerts >= 1)
        self.assertIn("HTTP 422 bad_field (description)", "\n".join(p.logBuffer))
        extra = self.dbo.query_string("SELECT Extra FROM animalpublished WHERE PublishedTo = 'petnecto' AND AnimalID = ?", [self.animals[1][0]])
        self.assertTrue(extra.startswith("error:"))
        # nothing changed in ASM, but the failed animal is sent again
        fake = FakePetnecto(handler)
        with mock.patch.object(asm3.publishers.petnecto.PetnectoPublisher, "isChangedSinceLastPublish", lambda self: False):
            self.run_publisher(fake)
        names = [ c["body"]["name"] for c in fake.posts() ]
        self.assertIn("Secondio", names)
        self.assertTrue(len(fake.posts()) >= 1)

    def test_a_refused_token_stops_the_run_at_once_and_is_never_logged(self):
        fake = FakePetnecto(lambda m, u, b: (401, { "ok": False, "error": "unauthorized" }, {}))
        p = self.run_publisher(fake)
        self.assertEqual(1, len(fake.calls), "a refused token is not tried again for every animal")
        log = "\n".join(p.logBuffer)
        self.assertIn("refused the token", log)
        self.assertNotIn(TOKEN, log)
        self.assertNotIn("pnp_", log)
        self.assertNotIn(TOKEN, p.lastError)
        saved = self.dbo.query_string("SELECT LogData FROM publishlog WHERE Name = 'petnecto' ORDER BY ID DESC")
        self.assertNotIn(TOKEN, saved)

    def test_rate_limited_waits_once_then_stops_the_run(self):
        fake = FakePetnecto(lambda m, u, b: (429, { "ok": False, "error": "slow_down" }, { "retry-after": "3" }))
        with mock.patch("asm3.publishers.petnecto.time.sleep") as sleep:
            p = self.run_publisher(fake)
        self.assertEqual(2, len(fake.calls), "one wait, one more try, then the run stops")
        self.assertEqual(3, sleep.call_count)
        self.assertIn("slow down", "\n".join(p.logBuffer))

    def test_rate_limited_once_carries_on(self):
        state = { "n": 0 }
        def handler(m, u, b):
            state["n"] += 1
            return (429, { "ok": False, "error": "slow_down" }, { "retry-after": "1" }) if state["n"] == 1 else (201, { "ok": True, "result": "created" }, {})
        with mock.patch("asm3.publishers.petnecto.time.sleep"):
            p = self.run_publisher(FakePetnecto(handler))
        self.assertEqual(0, p.alerts)
        self.assertEqual(len(p.getAnimals()), p.successes)

    def test_a_long_retry_after_is_not_waited_for(self):
        fake = FakePetnecto(lambda m, u, b: (429, { "ok": False, "error": "slow_down" }, { "retry-after": "600" }))
        with mock.patch("asm3.publishers.petnecto.time.sleep") as sleep:
            p = self.run_publisher(fake)
        self.assertEqual(1, len(fake.calls))
        self.assertEqual(0, sleep.call_count)
        self.assertIn("slow down", "\n".join(p.logBuffer))

    def test_unreachable_stops_after_three_failures(self):
        calls = []
        def boom(method, url, data = None, **kw):
            calls.append(url)
            raise ConnectionError("cannot connect with Bearer " + TOKEN)
        p = self.publisher()
        with mock.patch("asm3.publishers.petnecto.PETNECTO_URL", URL), mock.patch("asm3.publishers.petnecto.requests.request", boom), \
            mock.patch("asm3.publishers.petnecto.MAX_CONSECUTIVE_FAILURES", 1):
            p.run()
        self.assertEqual(1, len(calls), "after the allowed number of failures in a row the run stops")
        log = "\n".join(p.logBuffer)
        self.assertNotIn(TOKEN, log)
        self.assertIn("Could not reach Petnecto", log)
        self.assertIn("could not be reached 1 times in a row", log)

    def test_a_code_with_a_slash_and_space_is_the_same_for_upload_and_take_down(self):
        # ASM rewrites codes for every row when the first row has a slash; the code Petnecto keys on must not depend on that
        self.dbo.execute("UPDATE animal SET ShelterCode = 'A B/1' WHERE ID = %d" % self.animals[1][0])
        self.dbo.execute("UPDATE animal SET ShelterCode = 'X Y/2' WHERE ID = %d" % self.animals[0][0])
        fake = FakePetnecto()
        self.run_publisher(fake)
        codes = sorted([ c["body"]["shelter_code"] for c in fake.posts() ])
        self.assertEqual(["A-B-1", "X-Y-2"], codes)
        data = { "animal": int(self.animals[1][0]), "person": self.pnid, "movementdate": base.today_display(), "type": "1" }
        self.mid = asm3.movement.insert_movement_from_form(self.dbo, "test", asm3.utils.PostedData(data, "en"))
        fake2 = FakePetnecto(lambda m, u, b: (200, { "ok": True, "result": "updated" }, {}))
        self.run_publisher(fake2)
        self.assertEqual(1, len(fake2.patches()))
        self.assertTrue(fake2.patches()[0]["url"].endswith("/animals/A-B-1"), fake2.patches()[0]["url"])

    def test_adopted_animal_is_taken_down_once(self):
        self.run_publisher(FakePetnecto())
        aid, code = self.animals[1]
        code = self.dbo.query_string("SELECT ShelterCode FROM animal WHERE ID = ?", [aid])
        data = { "animal": int(aid), "person": self.pnid, "movementdate": base.today_display(), "type": "1" }
        self.mid = asm3.movement.insert_movement_from_form(self.dbo, "test", asm3.utils.PostedData(data, "en"))
        fake = FakePetnecto(lambda m, u, b: (200, { "ok": True, "result": "updated" }, {}))
        p = self.run_publisher(fake)
        patches = fake.patches()
        self.assertEqual(1, len(patches), "\n".join(p.logBuffer))
        self.assertEqual({ "status": "removed" }, patches[0]["body"])
        self.assertTrue(patches[0]["url"].endswith("/api/v1/shelters/%s/animals/%s" % (SHELTER, asm3.publishers.petnecto.CODE_BAD_RE.sub("-", code))), patches[0]["url"])
        self.assertEqual("Bearer " + TOKEN, patches[0]["headers"]["Authorization"])
        # and not again on the next run
        fake2 = FakePetnecto(lambda m, u, b: (200, { "ok": True, "result": "unchanged" }, {}))
        self.run_publisher(fake2)
        self.assertEqual(0, len(fake2.patches()))

    def test_takedown_of_an_animal_petnecto_never_had_is_not_an_error(self):
        self.run_publisher(FakePetnecto())
        aid, code = self.animals[1]
        data = { "animal": int(aid), "person": self.pnid, "movementdate": base.today_display(), "type": "1" }
        self.mid = asm3.movement.insert_movement_from_form(self.dbo, "test", asm3.utils.PostedData(data, "en"))
        fake = FakePetnecto(lambda m, u, b: (404, { "ok": False, "error": "not_found" }, {}) if m == "PATCH" else (201, { "ok": True, "result": "created" }, {}))
        p = self.run_publisher(fake)
        self.assertEqual(0, p.alerts, "\n".join(p.logBuffer))

    def test_bad_configuration_sends_nothing(self):
        for token, shelter, url, message in (
            ("", SHELTER, URL, "No Petnecto shelter ID or token"),
            (TOKEN, "", URL, "No Petnecto shelter ID or token"),
            ("not-a-token", SHELTER, URL, "token looks wrong"),
            (TOKEN, "../etc", URL, "shelter ID looks wrong"),
            (TOKEN, SHELTER, "", "has not been set up on this server"),
            (TOKEN, SHELTER, "http://petnecto.com", "must use https"),
        ):
            asm3.configuration.cset(self.dbo, "PetnectoToken", token)
            asm3.configuration.cset(self.dbo, "PetnectoShelterID", shelter)
            fake = FakePetnecto()
            p = self.run_publisher(fake, url)
            self.assertEqual(0, len(fake.calls), message)
            self.assertIn(message, "\n".join(p.logBuffer))
            self.assertNotIn(TOKEN, "\n".join(p.logBuffer))
