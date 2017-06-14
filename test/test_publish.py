#!/usr/bin/python env

import unittest
import base

import animal
import configuration
import publish
import publishers
import utils

class TestPublish(unittest.TestCase):
 
    def setUp(self):
        data = {
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1",
            "comments": "bio"
        }
        post = utils.PostedData(data, "en")
        self.nid, self.code = animal.insert_animal_from_form(base.get_dbo(), post, "test")
        configuration.cset(base.get_dbo(), "PublisherPresets", "includewithoutimage includewithoutdescription includenonneutered excludeunder=1")

    def tearDown(self):
        animal.delete_animal(base.get_dbo(), "test", self.nid)

    def test_get_adoption_status(self):
        a = animal.get_animal(base.get_dbo(), self.nid)
        assert "Adoptable" == publish.get_adoption_status(base.get_dbo(), a)

    def test_get_animal_data(self):
        assert len(publishers.base.get_animal_data(base.get_dbo())) > 0

    def test_get_animal_view(self):
        assert len(publish.get_animal_view(base.get_dbo(), self.nid)) > 0

    def test_get_animal_view_adoptable_js(self):
        assert len(publish.get_animal_view_adoptable_js(base.get_dbo())) > 0

    def test_gen_avid_pdf(self):
        p = publishers.pettracuk.PETtracUKPublisher(base.get_dbo(), publishers.base.PublishCriteria())
        fields = {
            "orgpostcode": "S60 2AH",
            "orgname": "Rob's Humane",
            "orgserial": "983498",
            "orgpassword": "password",
            "version": "1.1",
            "microchip": "977000000000001",
            "implantdate": "20160215",
            "prefix": "Mr",
            "surname": "Testington",
            "firstname": "Test",
            "address1": "123 Test Street",
            "city": "Testville",
            "county": "Testshire",
            "postcode": "TE1 ST1",
            "telhome": "0114 29392302",
            "telwork": "0113 20983823",
            "telmobile": "07544 239382",
            "telalternative": "",
            "email": "test@test.com",
            "petname": "Rover",
            "petgender": "M",
            "petdob": "20140112",
            "petspecies": "Dog",
            "petbreed": "Labrador",
            "petneutered": "true",
            "petcolour": "Black",
            "selfreg": "true", 
            "test": "false"
        }
        s = p.reregistrationPDF(fields, "", "Testington Test", "Test Org", "123 Test Street", "Rotherham", "S Yorkshire", "S60 2AH")
        f = open("/tmp/avid_rereg_test.pdf", "wb")
        f.write(s)
        f.flush()
        f.close()

