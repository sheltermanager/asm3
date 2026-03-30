#!/usr/bin/env python3

import unittest
import base

import test_additional
import test_animalcontrol
import test_animalname
import test_animal
import test_automail
import test_checkmicrochip
import test_clinic
import test_csvimport
import test_dbfs
import test_dbupdate
import test_diary
import test_event
import test_financial
import test_geo
import test_html
import test_log
import test_lookups
import test_lostfound
import test_media
import test_medical
import test_movement
import test_onlineform
import test_paymentprocessor
import test_person
import test_publish
import test_reports
import test_search
import test_service
import test_stock
import test_template
import test_users
import test_utils
import test_waitinglist

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
    runner = unittest.TextTestRunner()
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
    lt(test_additional),
    lt(test_animalcontrol),
    lt(test_animalname),
    lt(test_animal),
    lt(test_automail),
    lt(test_checkmicrochip),
    lt(test_clinic),
    lt(test_csvimport),
    lt(test_dbfs),
    lt(test_dbupdate),
    lt(test_diary),
    lt(test_event),
    lt(test_financial),
    lt(test_geo),
    lt(test_html),
    lt(test_log),
    lt(test_lookups),
    lt(test_lostfound),
    lt(test_media),
    lt(test_medical),
    lt(test_movement),
    lt(test_onlineform),
    lt(test_paymentprocessor),
    lt(test_person),
    lt(test_publish),
    lt(test_reports),
    lt(test_search),
    lt(test_service),
    lt(test_stock),
    lt(test_template),
    lt(test_users),
    lt(test_utils),
    lt(test_waitinglist)
]

# Running a single suite of tests
# fullsuite = [ lt(test_financial) ]

if __name__ == "__main__":
    emailerrors = False
    import sys
    for i in sys.argv:
        if i == "emailerrors":
            emailerrors = True
    execute(fullsuite, emailerrors)
    

