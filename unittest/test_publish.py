
import unittest
import base

import asm3.animal
import asm3.configuration
import asm3.publishers
import asm3.publishers.html
import asm3.publishers.adoptapet
import asm3.publishers.akcreunite
import asm3.publishers.anibaseuk
import asm3.publishers.buddyid
import asm3.publishers.foundanimals
import asm3.publishers.homeagain
import asm3.publishers.maddiesfund
import asm3.publishers.mypetuk
import asm3.publishers.petcademy
import asm3.publishers.petfbi
import asm3.publishers.petfinder
import asm3.publishers.petlink
import asm3.publishers.petrescue
import asm3.publishers.petslocateduk
import asm3.publishers.pettracuk
import asm3.publishers.rescuegroups
import asm3.publishers.sacmetrics
import asm3.publishers.savourlife
import asm3.publishers.smarttag
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
        self.assertEqual("Adoptable", asm3.publishers.base.get_adoption_status(base.get_dbo(), a))

    def test_get_animal_data(self):
        self.assertNotEqual(0, len(asm3.publishers.base.get_animal_data(base.get_dbo())))

    def test_get_microchip_data(self):
        asm3.publishers.base.get_microchip_data(base.get_dbo(), [ "0", "1", "2", "3", "4", "5", "6", "7", "8", "9" ], "test")


    # html 
    def test_get_adoptable_animals(self):
        self.assertNotEqual(0, len(asm3.publishers.html.get_adoptable_animals(base.get_dbo())))

    def test_get_adopted_animals(self):
        asm3.publishers.html.get_adopted_animals(base.get_dbo())

    def test_get_deceased_animals(self):
        asm3.publishers.html.get_deceased_animals(base.get_dbo())

    def test_get_flagged_animals(self):
        asm3.publishers.html.get_flagged_animals(base.get_dbo())

    def test_get_held_animals(self):
        asm3.publishers.html.get_held_animals(base.get_dbo())

    def test_get_stray_animals(self):
        asm3.publishers.html.get_stray_animals(base.get_dbo())

    def test_get_animal_view(self):
        self.assertNotEqual(0, len(asm3.publishers.html.get_animal_view(base.get_dbo(), self.nid)))

    def test_get_animal_view_adoptable_js(self):
        self.assertNotEqual(0, len(asm3.publishers.html.get_animal_view_adoptable_js(base.get_dbo())))

    # adoptapet
    def test_adoptapet(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        self.assertIsNotNone(asm3.publishers.adoptapet.AdoptAPetPublisher(base.get_dbo(), pc).processAnimal(a))

    # akcreunite
    def test_akcreunite(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        self.assertIsNotNone(asm3.publishers.akcreunite.AKCReunitePublisher(base.get_dbo(), pc).processAnimal(a))
        asm3.publishers.akcreunite.AKCReunitePublisher(base.get_dbo(), pc).validate(a)

    # anibase
    def test_anibase(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        self.assertIsNotNone(asm3.publishers.anibaseuk.AnibaseUKPublisher(base.get_dbo(), pc).processAnimal(a))
        asm3.publishers.anibaseuk.AnibaseUKPublisher(base.get_dbo(), pc).validate(a)

    # buddyid
    def test_buddyid(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        self.assertIsNotNone(asm3.publishers.buddyid.BuddyIDPublisher(base.get_dbo(), pc).processAnimal(a, "C00000"))
        asm3.publishers.buddyid.BuddyIDPublisher(base.get_dbo(), pc).validate(a)

    # findpet
    def test_findpet(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        self.assertIsNotNone(asm3.publishers.findpet.FindPetPublisher(base.get_dbo(), pc).processReport(a, "fakeorg"))
        self.assertIsNotNone(asm3.publishers.findpet.FindPetPublisher(base.get_dbo(), pc).processTransfer(a))
        asm3.publishers.findpet.FindPetPublisher(base.get_dbo(), pc).validate(a)

    # foundanimals
    def test_foundanimals(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        self.assertIsNotNone(asm3.publishers.foundanimals.FoundAnimalsPublisher(base.get_dbo(), pc).processAnimal(a))
        asm3.publishers.foundanimals.FoundAnimalsPublisher(base.get_dbo(), pc).validate(a, -1000)

    # homeagain
    def test_homeagain(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        self.assertIsNotNone(asm3.publishers.homeagain.HomeAgainPublisher(base.get_dbo(), pc).processAnimal(a))
        asm3.publishers.homeagain.HomeAgainPublisher(base.get_dbo(), pc).validate(a)

    # maddiesfund
    def test_maddiesfund(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        self.assertIsNotNone(asm3.publishers.maddiesfund.MaddiesFundPublisher(base.get_dbo(), pc).getData(214))
        self.assertIsNotNone(asm3.publishers.maddiesfund.MaddiesFundPublisher(base.get_dbo(), pc).processAnimal(a))

    # mypetuk
    def test_mypetuk(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        self.assertIsNotNone(asm3.publishers.mypetuk.MyPetUKPublisher(base.get_dbo(), pc).processAnimal(a))
        asm3.publishers.mypetuk.MyPetUKPublisher(base.get_dbo(), pc).validate(a)

    # petcademy
    def test_petcademy(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        self.assertIsNotNone(asm3.publishers.petcademy.PetcademyPublisher(base.get_dbo(), pc).getData(214))
        self.assertIsNotNone(asm3.publishers.petcademy.PetcademyPublisher(base.get_dbo(), pc).processAnimal(a))

    # petfbi
    def test_petfbi(self):
        pc = asm3.publishers.base.PublishCriteria()
        fbi = asm3.publishers.petfbi.PetFBIPublisher(base.get_dbo(), pc)
        fbi.fbiGetFound()
        fbi.fbiGetStrayHold()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        self.assertIsNotNone(asm3.publishers.petfbi.PetFBIPublisher(base.get_dbo(), pc).processAnimal(a))

    # petfinder
    def test_petfinder(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        pf = asm3.publishers.petfinder.PetFinderPublisher(base.get_dbo(), pc)
        cikv = asm3.dbms.base.ResultRow()
        cikv["ID"] = 1
        pf.pfUpdateCacheInvalidationKeys([cikv])
        self.assertIsNotNone(pf.processAnimal(a))
        b = base.get_dbo().query(pf.pfAnimalQuery())[0]
        self.assertIsNotNone(pf.processAnimal(b, status="X"))

    # petlink
    def test_petlink(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        self.assertIsNotNone(asm3.publishers.petlink.PetLinkPublisher(base.get_dbo(), pc).processAnimal(a))
        asm3.publishers.petlink.PetLinkPublisher(base.get_dbo(), pc).validate(a, -1000)

    # petrescue
    def test_petrescue(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        pr = asm3.publishers.petrescue.PetRescuePublisher(base.get_dbo(), pc)
        pr.load_breeds()
        self.assertIsNotNone(pr.breeds)
        self.assertTrue(len(pr.breeds["Dog"]) > 0)
        self.assertIsNotNone(pr.processAnimal(a))

    # petslocateduk
    def test_petslocateduk(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        self.assertIsNotNone(asm3.publishers.petslocateduk.PetsLocatedUKPublisher(base.get_dbo(), pc).processAnimal(a))

    # pettracuk
    def test_pettracuk(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        self.assertIsNotNone(asm3.publishers.pettracuk.PETtracUKPublisher(base.get_dbo(), pc).processAnimal(a))
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
        self.assertIsNotNone(asm3.publishers.rescuegroups.RescueGroupsPublisher(base.get_dbo(), pc).processAnimal(a))

    # sacmetrics
    def test_sacmetrics(self):
        pc = asm3.publishers.base.PublishCriteria()
        asm3.publishers.sacmetrics.SACMetricsPublisher(base.get_dbo(), pc).analyseMonths()
        asm3.publishers.sacmetrics.SACMetricsPublisher(base.get_dbo(), pc).processStats(8, 2022, "canine")

    # savourlife
    def test_savourlife(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        self.assertIsNotNone(asm3.publishers.savourlife.SavourLifePublisher(base.get_dbo(), pc).processAnimal(a))

    # smarttag
    def test_smarttag(self):
        pc = asm3.publishers.base.PublishCriteria()
        a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
        self.assertIsNotNone(asm3.publishers.smarttag.SmartTagPublisher(base.get_dbo(), pc).processAnimal(a))

    # vetenvoy - redundant and not imported by publish.py any more
    #def test_vetenvoy(self):
    #    pc = asm3.publishers.base.PublishCriteria()
    #    a = asm3.publishers.base.get_animal_data(base.get_dbo())[0]
    #    assert asm3.publishers.vetenvoy.VetEnvoyUSMicrochipPublisher(base.get_dbo(), pc, "ve", "ve", "ve", [ "9" ]).processAnimal(a) is not None
    #    asm3.publishers.vetenvoy.VetEnvoyUSMicrochipPublisher(base.get_dbo(), pc, "ve", "ve", "ve", [ "9" ]).validate(a)


