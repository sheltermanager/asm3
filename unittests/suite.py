#!/usr/bin/env python3

import sys, os
sys.path.append(os.getcwd()) # Add root onto path so that unittests package is visible

import unittest
from unittests import base

import unittests.test_additional
import unittests.test_animalcontrol
import unittests.test_animalname
import unittests.test_animal
import unittests.test_automail
import unittests.test_checkmicrochip
import unittests.test_clinic
import unittests.test_csvimport
import unittests.test_dbfs
import unittests.test_dbupdate
import unittests.test_diary
import unittests.test_event
import unittests.test_financial
import unittests.test_geo
import unittests.test_html
import unittests.test_log
import unittests.test_lookups
import unittests.test_lostfound
import unittests.test_media
import unittests.test_medical
import unittests.test_movement
import unittests.test_onlineform
import unittests.test_paymentprocessor
import unittests.test_person
import unittests.test_publish
import unittests.test_reports
import unittests.test_search
import unittests.test_service
import unittests.test_stock
import unittests.test_template
import unittests.test_users
import unittests.test_utils
import unittests.test_waitinglist

def lt(modname):
    return unittest.TestLoader().loadTestsFromModule(modname)

def send_email(body):
    """
    Sends an email.
    """
    import email.utils
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from subprocess import Popen, PIPE
    msg = MIMEMultipart("alternative")
    msg["From"] = "error@sheltermanager.com"
    msg["To"] = "error@sheltermanager.com"
    msg["Message-ID"] = email.utils.make_msgid()
    msg["Date"] = email.utils.formatdate()
    msg["Subject"] = "Unit Test Errors"
    msg["Auto-Submitted"] = "auto-generated"
    # Attach the plaintext message
    msg.attach(MIMEText(body, "plain"))
    # Send the email
    p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
    p.communicate(msg.as_string().encode("utf-8"))
    
def execute(fullsuite, emailerrors = False):
    s = unittest.TestSuite(fullsuite)
    runner = unittest.TextTestRunner(failfast=True)
    result = runner.run(s)
    if not result.wasSuccessful():
        body = []
        body.append("FAILURES:")
        for test, trace in result.failures:
            body.append(f"{test}: {trace}")
        body.append("ERRORS:")
        for test, trace in result.errors:
            body.append(f"{test}: {trace}")
        m = "\n\n".join(body)
        send_email(f"Unit test failure:\n\n{result}\n\n{m}")

fullsuite = [
    lt(unittests.test_additional),
    lt(unittests.test_animalcontrol),
    lt(unittests.test_animalname),
    lt(unittests.test_animal),
    lt(unittests.test_automail),
    lt(unittests.test_checkmicrochip),
    lt(unittests.test_clinic),
    lt(unittests.test_csvimport),
    lt(unittests.test_dbfs),
    lt(unittests.test_dbupdate),
    lt(unittests.test_diary),
    lt(unittests.test_event),
    lt(unittests.test_financial),
    lt(unittests.test_geo),
    lt(unittests.test_html),
    lt(unittests.test_log),
    lt(unittests.test_lookups),
    lt(unittests.test_lostfound),
    lt(unittests.test_media),
    lt(unittests.test_medical),
    lt(unittests.test_movement),
    lt(unittests.test_onlineform),
    lt(unittests.test_paymentprocessor),
    lt(unittests.test_person),
    lt(unittests.test_publish),
    lt(unittests.test_reports),
    lt(unittests.test_search),
    lt(unittests.test_service),
    lt(unittests.test_stock),
    lt(unittests.test_template),
    lt(unittests.test_users),
    lt(unittests.test_utils),
    lt(unittests.test_waitinglist)
]

# Running a single suite of tests
# fullsuite = [ lt(test_animal) ]

if __name__ == "__main__":
    emailerrors = False
    import sys
    for i in sys.argv:
        if i == "emailerrors":
            emailerrors = True
    execute(fullsuite, emailerrors)
    

