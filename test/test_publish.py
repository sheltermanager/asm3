#!/usr/bin/python env

import unittest
import base

import publish

class TestPublish(unittest.TestCase):
 
    def test_gen_avid_pdf(self):
        p = publish.PETtracUKPublisher(base.get_dbo(), publish.PublishCriteria())
        s = p.reregistrationPDF({ "breed": "Labrador" }, "", "Testington Test", "Test Org", "123 Test Street", "Rotherham", "S Yorkshire", "S60 2AH")
        f = open("/tmp/avid_rereg_test.pdf", "wb")
        f.write(s)
        f.flush()
        f.close()

