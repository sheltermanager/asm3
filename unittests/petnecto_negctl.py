#!/usr/bin/env python3
"""
Negative controls for the Petnecto publisher: breaks one guard at a time in src/asm3/publishers/petnecto.py,
runs unittests.test_petnecto, and demands that the suite fails. The file is restored afterwards, even on a crash.
Run from the repository root:  python3 unittests/petnecto_negctl.py [name-filter]
Needs scripts/unittestdb/base.db (make scripts/unittestdb/base.db), like the rest of the unit tests.
"""
import os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__)) + os.sep + ".." + os.sep
FILE = ROOT + "src/asm3/publishers/petnecto.py"

# [name, [(exact text, replacement), ...], a test name (or a subTest label) that must fail]
TIMEOUT = 600 # seconds for one run of the suite
MUTATIONS = [
    ("redirects are followed with the token", [("allow_redirects = False", "allow_redirects = True")], "test_run_posts_every_animal_with_the_token"),
    ("no timeout on the request", [("timeout = TIMEOUT, ", "")], "test_run_posts_every_animal_with_the_token"),
    ("the token is not redacted", [("    if token: s = s.replace(token, \"[token]\")\n", ""), ("    return re.sub(r\"pnp_[A-Za-z0-9_-]{8,}\", \"[token]\", s)", "    return s")], "test_redact"),
    ("personal data is not stripped from the rows", [("strip_personal_data = True", "strip_personal_data = False")], "test_rows_are_stripped_before_use"),
    ("an owner field is added to what is sent", [("            \"status\":               status\n", "            \"status\":               status, \"owner\": an.CURRENTOWNERNAME\n"), ("        assert tuple(data.keys()) == PETNECTO_FIELDS", "")], "test_process_animal_sends_only_the_listed_fields"),
    ("hidden details are sent as the description (rows not stripped)", [("strip_personal_data = True", "strip_personal_data = False"), ("clean_text(an.WEBSITEMEDIANOTES)", "clean_text(an.HIDDENANIMALDETAILS + an.WEBSITEMEDIANOTES)")], "test_nothing_personal_is_sent"),
    ("the description is sent as written", [("description, removed = clean_text(an.WEBSITEMEDIANOTES)", "description, removed = asm3.utils.nulltostr(an.WEBSITEMEDIANOTES), True")], "test_contact_sentence_removed_from_description"),
    ("tidied text is reported as a removal", [("    return t, t != s and (has_contact(s) or is_orphaned(s))", "    return t, t != s")], "test_clean_text"),
    # the contact strip: each guard against the case that needs it (the label of a subTest in TestContactStrip)
    ("orphans: an address cut out earlier leaves its sentence", [("    return any(r.search(n) for r in ORPHANED_CONTACTS)", "    return False")], "C1 a leftover from an earlier email strip"),
    ("sentences: a full stop inside an address ends a sentence", [("            if j >= n or line[j].isspace():", "            if True:")], "C1 the same sentence with the address still in it"),
    ("detect: phone numbers are not looked for", [("    return any(r.search(n) for r in CONTACT_DETAILS)", "    return any(r.search(n) for r in CONTACT_DETAILS[:2] + CONTACT_DETAILS[5:])")], "C4 a North American phone with +1"),
    ("detect: 'at ... dot' addresses are not looked for", [("    return any(r.search(n) for r in CONTACT_DETAILS)", "    return any(r.search(n) for r in CONTACT_DETAILS[:1] + CONTACT_DETAILS[2:])")], "C3 an address written with at and dot"),
    ("detect: handles are not looked for", [("    return any(r.search(n) for r in CONTACT_DETAILS)", "    return any(r.search(n) for r in CONTACT_DETAILS[:5] + CONTACT_DETAILS[6:])")], "C6 a social handle"),
    ("detect: full-width characters are read as they are", [("    n = unicodedata.normalize(\"NFKC\", s)\n    return any(r.search(n) for r in CONTACT_DETAILS)", "    n = s\n    return any(r.search(n) for r in CONTACT_DETAILS)")], "C4 a full-width Japanese phone number"),
    ("lead-in: 'Questions?' is left pointing at nothing", [("        if len(kept) > 0 and is_lead_in(kept[-1]): kept.pop()\n", "")], "C8 the lead-in before a dropped sentence goes"),
    ("lead-in: a line-long lead-in stays", [("elif len(out) > 0 and is_lead_in(out[-1]): out.pop()", "elif False: out.pop()")], "C8 paragraphs stay apart"),
    ("aside: a bracketed detail takes the whole sentence", [("        if aside is not None:\n            kept.append(aside)\n            continue\n", "")], "C7 a bracketed aside keeps the sentence"),
    ("bounds: the 'at ... dot' pattern repeats without limit", [("(?:\" + _DOT + _LNH + r\"{1,63}){0,3}\" + _DOT", "(?:\\s*\" + _DOT + r\"?\\s*[\\w.-]+)*\" + _DOT")], "H1 hostile input does not make the patterns backtrack"),
    ("a number split across sentences is sent", [("    if has_contact(t): t = \"\"\n", "")], "H4 a number split across two sentences"),
    ("a refused token does not stop the run", [("                    fatal = True\n                    break\n                elif status == 429:", "                elif status == 429:")], "test_a_refused_token_stops_the_run_at_once_and_is_never_logged"),
    ("the token reaches the log", [("AbstractPublisher.logError(self, redact(msg, self.token), None)", "AbstractPublisher.logError(self, msg + ' ' + self.token, None)"), ("AbstractPublisher.log(self, redact(msg, self.token))", "AbstractPublisher.log(self, msg)")], "test_a_refused_token_stops_the_run_at_once_and_is_never_logged"),
    ("animals that left are put on hold, never removed", [("if an.DECEASEDDATE is not None or an.ACTIVEMOVEMENTDATE is not None: status = \"removed\"", "pass")], "test_adopted_animal_is_taken_down_once"),
    ("the same take-down is sent every run", [("                if an.LASTSTATUS == status: continue\n", "")], "test_adopted_animal_is_taken_down_once"),
    ("a 404 on take-down is an error", [("if st == 200 or st == 404:", "if st == 200:")], "test_takedown_of_an_animal_petnecto_never_had_is_not_an_error"),
    ("an unsent animal is hidden by the no-change shortcut", [("        return any(an.ID not in ok for an in animals)", "        return False")], "test_an_animal_never_sent_is_sent_even_when_nothing_changed"),
    ("a failed animal is not retried", [("in (\"\", \"None\")", "!= \"zzz\"")], "test_a_rejected_animal_is_retried_and_does_not_stop_the_others"),
    ("plain http to anywhere is accepted", [("        if not private: return \"The Petnecto URL must use https:// (plain http is only accepted for hosts on a private network)\"\n", "")], "test_base_url_problem"),
    ("the token shape is not checked", [("        if not TOKEN_RE.match(self.token):", "        if False:")], "test_bad_configuration_sends_nothing"),
    ("the shelter id shape is not checked", [("        if not SHELTER_ID_RE.match(shelterid):", "        if False:")], "test_bad_configuration_sends_nothing"),
    ("an empty service address still sends", [("        if baseurl == \"\":", "        if False:")], "test_bad_configuration_sends_nothing"),
    ("unreachable never gives up", [("                    if failures >= MAX_CONSECUTIVE_FAILURES:\n                        self.setLastError(\"Petnecto could not be reached", "                    if False:\n                        self.setLastError(\"Petnecto could not be reached")], "test_unreachable_stops_after_three_failures"),
    ("rate limiting does not stop the run", [("                    fatal = True\n                    break\n                elif status == 599:", "                elif status == 599:")], "test_rate_limited_waits_once_then_stops_the_run"),
    ("a 429 is not waited for", [("        if status == 429 and retryafter.strip().isdigit() and 0 < int(retryafter) <= MAX_RETRY_WAIT:", "        if False:")], "test_rate_limited_once_carries_on"),
    ("any wait is accepted", [("0 < int(retryafter) <= MAX_RETRY_WAIT", "0 < int(retryafter)")], "test_a_long_retry_after_is_not_waited_for"),
    ("the code is taken from the rewritten row", [("self.cleanCode(self.rawcodes.get(an.ID, an.SHELTERCODE))", "self.cleanCode(an.SHELTERCODE)")], "test_a_code_with_a_slash_and_space_is_the_same_for_upload_and_take_down"),
    ("the code is not made URL safe in the take-down", [("                code = self.cleanCode(an.SHELTERCODE)\n", "                code = asm3.utils.nulltostr(an.SHELTERCODE)\n")], "test_a_code_with_a_slash_and_space_is_the_same_for_upload_and_take_down"),
    ("not registered with the scheduler", [("self.initLog(\"petnecto\", \"Petnecto Publisher\")", "self.initLog(\"petnectoX\", \"Petnecto Publisher\")")], "test_run_posts_every_animal_with_the_token"),
]

def main():
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    original = open(FILE).read()
    shutil.copy(FILE, FILE + ".orig")
    bad = 0
    ran = 0
    try:
        for name, edits, test in MUTATIONS:
            if only and only not in name: continue
            s = original
            missing = False
            for a, b in edits:
                if a not in s:
                    missing = True
                    break
                s = s.replace(a, b, 1)
            if missing:
                print("BROKEN  %s: the text to mutate was not found" % name)
                bad += 1
                continue
            ran += 1
            open(FILE, "w").write(s)
            shutil.copy(ROOT + "scripts/unittestdb/base.db", ROOT + "scripts/unittestdb/test.db")
            try:
                r = subprocess.run([sys.executable, "-m", "unittest", "unittests.test_petnecto"], cwd = ROOT, capture_output = True, text = True, timeout = TIMEOUT)
            except subprocess.TimeoutExpired:
                # a runaway pattern can hang the suite: that counts as caught only for the test that guards against it
                caught = test.startswith("H1")
                print("%s  %s (timed out)" % ("CAUGHT" if caught else "MISSED", name))
                if not caught: bad += 1
                continue
            out = r.stdout + r.stderr
            failed = [ l for l in out.split("\n") if l.startswith(("FAIL:", "ERROR:")) ]
            caught = r.returncode != 0 and any(test in l for l in failed)
            print("%s  %s%s" % ("CAUGHT" if caught else "MISSED", name, "" if caught else "   (wanted %s to fail; failed: %s)" % (test, "; ".join(failed)[:200])))
            if not caught: bad += 1
    finally:
        open(FILE, "w").write(original)
        os.unlink(FILE + ".orig")
    print("\n%d mutations run, %d not caught" % (ran, bad))
    sys.exit(1 if bad else 0)

main()
