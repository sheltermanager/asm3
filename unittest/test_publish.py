
import unittest
import base

import asm3.animal
import asm3.configuration
import asm3.publishers
import asm3.utils

class TestPublish(unittest.TestCase):
 
    def setUp(self):
        data = {
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "breed1": "1",
            "breed2": "1", 
            "species": "1",
            "comments": "bio"
        }
        post = asm3.utils.PostedData(data, "en")
        self.nid, self.code = asm3.animal.insert_animal_from_form(base.get_dbo(), post, "test")
        asm3.configuration.cset(base.get_dbo(), "PublisherPresets", "includewithoutimage includewithoutdescription includenonneutered includenonmicrochip excludeunder=1")

    def tearDown(self):
        asm3.animal.delete_animal(base.get_dbo(), "test", self.nid)

    # base
    def test_get_adoption_status(self):
        a = asm3.animal.get_animal(base.get_dbo(), self.nid)
        assert "Adoptable" == asm3.publishers.base.get_adoption_status(base.get_dbo(), a)

    def test_get_animal_data(self):
        assert len(asm3.publishers.base.get_animal_data(base.get_dbo())) > 0

    def test_get_microchip_data(self):
        asm3.publishers.base.get_microchip_data(base.get_dbo(), [ "0", "1", "2", "3", "4", "5", "6", "7", "8", "9" ], "test")


    # html 
    def test_get_adoptable_animals(self):
        assert len(asm3.publishers.html.get_adoptable_animals(base.get_dbo())) > 0

    def test_get_adopted_animals(self):
        asm3.publishers.html.get_adopted_animals(base.get_dbo())

    def test_get_deceased_animals(self):
        asm3.publishers.html.get_deceased_animals(base.get_dbo())

    def test_get_flagged_animals(self):
        asm3.publishers.html.get_flagged_animals(base.get_dbo())

    def test_get_held_animals(self):
        asm3.publishers.html.get_held_animals(base.get_dbo())

    def test_get_animal_view(self):
        assert len(asm3.publishers.html.get_animal_view(base.get_dbo(), self.nid)) > 0

    def test_get_animal_view_adoptable_js(self):
        assert len(asm3.publishers.html.get_animal_view_adoptable_js(base.get_dbo())) > 0

    # adoptapet
    def test_adoptapet(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        assert asm3.publishers.adoptapet.AdoptAPetPublisher(base.get_dbo(), pc).processAnimal(a) is not None

    # akcreunite
    def test_akcreunite(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        assert asm3.publishers.akcreunite.AKCReunitePublisher(base.get_dbo(), pc).processAnimal(a) is not None
        asm3.publishers.akcreunite.AKCReunitePublisher(base.get_dbo(), pc).validate(a)

    # anibase
    def test_anibase(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        assert asm3.publishers.anibaseuk.AnibaseUKPublisher(base.get_dbo(), pc).processAnimal(a) is not None
        asm3.publishers.anibaseuk.AnibaseUKPublisher(base.get_dbo(), pc).validate(a)

    # buddyid
    def test_buddyid(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        assert asm3.publishers.buddyid.BuddyIDPublisher(base.get_dbo(), pc).processAnimal(a, "C00000") is not None
        asm3.publishers.buddyid.BuddyIDPublisher(base.get_dbo(), pc).validate(a)

    # foundanimals
    def test_foundanimals(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        assert asm3.publishers.foundanimals.FoundAnimalsPublisher(base.get_dbo(), pc).processAnimal(a) is not None
        asm3.publishers.foundanimals.FoundAnimalsPublisher(base.get_dbo(), pc).validate(a, -1000)

    # helpinglostpets
    def test_helpinglostpets(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        assert asm3.publishers.helpinglostpets.HelpingLostPetsPublisher(base.get_dbo(), pc).processAnimal(a) is not None

    # homeagain
    def test_homeagain(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        assert asm3.publishers.homeagain.HomeAgainPublisher(base.get_dbo(), pc).processAnimal(a) is not None
        asm3.publishers.homeagain.HomeAgainPublisher(base.get_dbo(), pc).validate(a)

    # maddiesfund
    def test_maddiesfund(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        assert asm3.publishers.maddiesfund.MaddiesFundPublisher(base.get_dbo(), pc).getData(214) is not None
        assert asm3.publishers.maddiesfund.MaddiesFundPublisher(base.get_dbo(), pc).processAnimal(a) is not None

    # petcademy
    def test_petcademy(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        assert asm3.publishers.petcademy.PetcademyPublisher(base.get_dbo(), pc).getData(214) is not None
        assert asm3.publishers.petcademy.PetcademyPublisher(base.get_dbo(), pc).processAnimal(a) is not None

    # petfinder
    def test_petfinder(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        pf = asm3.publishers.petfinder.PetFinderPublisher(base.get_dbo(), pc)
        assert pf.processAnimal(a) is not None
        b = base.get_dbo().query(pf.pfAnimalQuery())[0]
        assert pf.processAnimal(b, status="X") is not None

    # petlink
    def test_petlink(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        assert asm3.publishers.petlink.PetLinkPublisher(base.get_dbo(), pc).processAnimal(a) is not None
        asm3.publishers.petlink.PetLinkPublisher(base.get_dbo(), pc).validate(a, -1000)

    # petrescue
    def test_petrescue(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        assert asm3.publishers.petrescue.PetRescuePublisher(base.get_dbo(), pc).processAnimal(a) is not None

    # petslocateduk
    def test_petslocateduk(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        assert asm3.publishers.petslocateduk.PetsLocatedUKPublisher(base.get_dbo(), pc).processAnimal(a) is not None

    # pettracuk
    def test_pettracuk(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        assert asm3.publishers.pettracuk.PETtracUKPublisher(base.get_dbo(), pc).processAnimal(a) is not None
        asm3.publishers.pettracuk.PETtracUKPublisher(base.get_dbo(), pc).validate(a)

    def test_pettracuk_gen_avid_pdf(self):
        p = asm3.publishers.pettracuk.PETtracUKPublisher(base.get_dbo(), asm3.publishers.base.PublishCriteria())
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

    # rescuegroups
    def test_rescuegroups(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        assert asm3.publishers.rescuegroups.RescueGroupsPublisher(base.get_dbo(), pc).processAnimal(a) is not None

    # sacmetrics
    def test_sacmetrics(self):
        pc = asm3.publishers.base.PublishCriteria()
        asm3.publishers.sacmetrics.SACMetricsPublisher(base.get_dbo(), pc).analyseMonths()
        asm3.publishers.sacmetrics.SACMetricsPublisher(base.get_dbo(), pc).processStats(8, 2022, "canine")

    # savourlife
    def test_savourlife(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        assert asm3.publishers.savourlife.SavourLifePublisher(base.get_dbo(), pc).processAnimal(a) is not None

    # smarttag
    def test_smarttag(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        assert asm3.publishers.smarttag.SmartTagPublisher(base.get_dbo(), pc).processAnimal(a) is not None

    # vetenvoy - redundant and not imported by publish.py any more
    #def test_vetenvoy(self):
    #    pc = asm3.publishers.base.PublishCriteria()
    #    a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
    #    assert asm3.publishers.vetenvoy.VetEnvoyUSMicrochipPublisher(base.get_dbo(), pc, "ve", "ve", "ve", [ "9" ]).processAnimal(a) is not None
    #    asm3.publishers.vetenvoy.VetEnvoyUSMicrochipPublisher(base.get_dbo(), pc, "ve", "ve", "ve", [ "9" ]).validate(a)


