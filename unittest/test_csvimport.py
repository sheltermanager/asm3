
import unittest
import base
import json
import datetime

import asm3.csvimport
import asm3.utils
import asm3.additional

class TestCSVImport(unittest.TestCase):

    minimalanimalcsvdata = (
        {
            'ANIMALNAME': 'TestioCSV',
            'ANIMALDOB': datetime.date(2001, 9, 11)
        },
    )
    complexanimalcsvdata  = (
        {
            'ANIMALCODE': 'V2025001',
            'ANIMALLITTER': 'carrierbaglitter',
            'ANIMALNONSHELTER': 'N',
            'ANIMALNOTFORADOPTION': 'N',
            'ANIMALTRANSFER': 'N',
            'ANIMALFLAGS': 'quarantine',
            'ANIMALNAME': 'TestioCSV',
            'ANIMALIMAGE': 'https://sheltermanager.com/images/bg-hero-pets.png',# To do - could I use a local image here?
            'ANIMALSEX': 'Male',
            'ANIMALTYPE': 'M (Miscellaneous)',
            'ANIMALCOLOR': 'Black',
            'ANIMALCOATTYPE': 'Short',
            'ANIMALBREED1': 'French Bulldog',
            'ANIMALBREED2': 'Great Dane',
            'ANIMALSIZE': 'Medium',
            'ANIMALWEIGHT': '6.9',
            'ANIMALAGE': '2',
            'ANIMALLOCATION': 'Shelter',
            'ANIMALUNIT': '1',# Not sure if this will be recognised on test db, couldn't find any default units.
            'ANIMALJURISDICTION': 'Local',
            'ANIMALPICKUPLOCATION': 'Shelter',
            'ANIMALPICKUPADDRESS': '83 Spring Street',
            'ANIMALSPECIES': 'Dog',
            'ANIMALCRATETRAINED': 'U',
            'ANIMALHOUSETRAINED': 'U',
            'ANIMALENERGYLEVEL': 'U',
            'ANIMALGOODWITHCATS': 'U',
            'ANIMALGOODWITHDOGS': 'U',
            'ANIMALGOODWITHELDERLY': 'U',
            'ANIMALGOODWITHKIDS': 'U',
            'ANIMALGOODONLEAD': 'U',
            'ANIMALDESCRIPTION': 'This animal was created by the csv import unit test.',
            'ANIMALHIDDENDETAILS': 'Do NOT rehome to DN7!',
            'ANIMALMARKINGS': 'Has a white tail.',
            'ANIMALHEALTHPROBLEMS': 'Only has one kidney.',
            'ANIMALWARNING': 'Do NOT rehome to DN7',
            'ANIMALNEUTERED': 'N',
            'ANIMALNEUTEREDDATE': '',
            'ANIMALMICROCHIP': '1234567890',
            'ANIMALMICROCHIPDATE': datetime.date(2001, 9, 11),
            'ANIMALTATTOO': '8OO81E5',
            'ANIMALTATTOODATE': datetime.date(2001, 9, 11),
            'ANIMALDECLAWED': 'N',
            'ANIMALHASSPECIALNEEDS': 'Y',
            'ANIMALENTRYDATE': datetime.date(2024, 9, 11),
            'ANIMALENTRYTIME': '13:00',
            'ANIMALENTRYCATEGORY': 'Biting',
            'ANIMALENTRYTYPE': 'Surrender',
            'ANIMALREASONFORENTRY': 'Ate owners slippers',
            'ANIMALDECEASEDDATE': datetime.date(2024, 9, 11),
            'ANIMALDECEASEDREASON': 'Died',
            'ANIMALDECEASEDNOTES': 'Found dead in bed.',
            'ANIMALEUTHANIZED': 'N',
            'ANIMALADDITIONALCUTENESS': 'Very, very cute',
            'COSTTYPE': 'Board and Food',
            'COSTDATE': datetime.date(2024, 9, 13),
            'COSTAMOUNT': '180',
            'COSTDESCRIPTION': 'This cost was created by the csvimport unit test.',
            'CURRENTVETTITLE': 'Sir',
            'CURRENTVETINITIALS': 'B',
            'CURRENTVETFIRSTNAME': 'Bob',
            'CURRENTVETLASTNAME': 'Hoskins',
            'CURRENTVETADDRESS': '12345 Short Street',
            'CURRENTVETCITY': 'Birmingham',
            'CURRENTVETSTATE': 'Aberdeenshire',
            'CURRENTVETZIPCODE': 'A23 7YU',
            'CURRENTVETJURISDICTION': 'Local',
            'CURRENTVETHOMEPHONE': '01234 456987',
            'CURRENTVETWORKPHONE': '01234 123456',
            'CURRENTVETCELLPHONE': '07754 546879',
            'CURRENTVETEMAIL': 'bob@hoskinsvets.co.uk',
            'CURRENTVETADDITIONALANTLERS': 'Y',
            'DIARYDATE': datetime.date(2001, 9, 11),
            'DIARYFOR': 'Baldrick',
            'DIARYSUBJECT': 'Test diary note from csv import',
            'DIARYNOTE': 'This note was created as part of the CSV import unit test.',
            'LOGDATE': datetime.date(2001, 9, 11),
            'LOGTIME': '13:00',
            'LOGTYPE': 'History',
            'LOGCOMMENTS': 'This log was created by the CSV Import unit test.',
            'MEDICALNAME': 'Test Regimen',
            'MEDICALDOSAGE': '10ml',
            'MEDICALGIVENDATE': datetime.date(2001, 9, 11),
            'MEDICALCOMMENTS': 'This regimen was created by the CSV Import unit test.',
            'MOVEMENTTYPE': '1',
            'MOVEMENTDATE': datetime.date(2020, 9, 11),
            'MOVEMENTRETURNDATE': datetime.date(2023, 9, 11),
            'MOVEMENTCOMMENTS': 'This movement was created by the CSV Import unit test.',
            'ORIGINALOWNERTITLE': 'Sir',
            'ORIGINALOWNERINITIALS': 'B',
            'ORIGINALOWNERFIRSTNAME': 'Bob',
            'ORIGINALOWNERLASTNAME': 'Hoskins',
            'ORIGINALOWNERADDRESS': '86 Orange Street',
            'ORIGINALOWNERCITY': 'Sheffield',
            'ORIGINALOWNERSTATE': 'South Yorkshire',
            'ORIGINALOWNERZIPCODE': 'S9 3HN',
            'ORIGINALOWNERJURISDICTION': 'Local',
            'ORIGINALOWNERHOMEPHONE': '01234 456987',
            'ORIGINALOWNERWORKPHONE': '01234 123456',
            'ORIGINALOWNERCELLPHONE': '07754 546879',
            'ORIGINALOWNEREMAIL': 'bob.hoskinsvets@mail.org',
            'ORIGINALOWNERWARNING': 'This person smells of cheese.',
            'ORIGINALOWNERFLAGS': 'volunteer',
            'ORIGINALOWNERANTLERS': 'Y',
            'TESTTYPE': 'Heartworm',
            'TESTRESULT': 'Unknown',
            'TESTDUEDATE': datetime.date(2023, 9, 11),
            'TESTPERFORMEDDATE': datetime.date(2023, 9, 11),
            'TESTPERFORMEDDATE': datetime.date(2023, 9, 11),
            'TESTCOMMENTS': 'This test was created by the CSV Import unit test.',
            'VACCINATIONTYPE': 'Rabies',
            'VACCINATIONDUEDATE': datetime.date(2023, 9, 11),
            'VACCINATIONGIVENDATE': datetime.date(2023, 9, 11),
            'VACCINATIONEXPIRESDATE': datetime.date(2023, 9, 11),
            'VACCINATIONMANUFACTURER': 'Acme',
            'VACCINATIONBATCHNUMBER': '12345AA',
            'VACCINATIONRABIESTAG': '12345RR',
            'VACCINATIONCOMMENTS': 'This movement was created by the CSV Import unit test.'
        },
    )
    minimalpersoncsvdata = (
        {
            'PERSONNAME': 'Sir Bob Hoskins',
            'PERSONFLAGS': 'banned'
        },
    )
    complexpersoncsvdata = (
        {
            'PERSONCLASS': '1',
            'PERSONNAME': 'Sir Bob Hoskins',
            'PERSONADDRESS': '10 Downing Street',
            'PERSONCITY': 'London',
            'PERSONSTATE': 'Devon',
            'PERSONZIPCODE': 'S9 3HN',
            'PERSONJURISDICTION': 'Local',
            'PERSONHOMEPHONE': '01234 456987',
            'PERSONWORKPHONE': '01234 123456',
            'PERSONCELLPHONE': '07754 546879',
            'PERSONEMAIL': 'bob.hoskinsvets@gmail.com',
            'PERSONGDPRCONTACTOPTIN': 'declined',
            'PERSONMEMBER': 'N',
            'PERSONMEMBERSHIPNUMBER': '8008135',
            'PERSONMEMBERSHIPEXPIRY': datetime.date(2027, 9, 11),
            'PERSONFOSTERER': 'Y',
            'PERSONFOSTERCAPACITY': '1',
            'PERSONDONOR': 'Y',
            'PERSONFLAGS': 'volunteer',
            'PERSONCOMMENTS': 'This record was created by the CSV import unit test.',
            'PERSONWARNING': 'This person has antlers',
            'PERSONMATCHACTIVE': 'Y',
            'PERSONMATCHADDED': datetime.date(2026, 9, 11),
            'PERSONMATCHEXPIRES': datetime.date(2027, 9, 11),
            'PERSONMATCHSEX': 'A',
            'PERSONMATCHSIZE': 'Medium',
            'PERSONMATCHCOLOR': 'Black',
            'PERSONMATCHAGEFROM': '2',
            'PERSONMATCHAGETO': '5',
            'PERSONMATCHTYPE': 'M (Miscellaneous)',
            'PERSONMATCHSPECIES': 'Dog',
            'PERSONMATCHBREED1': 'French Bulldog',
            'PERSONMATCHBREED2': 'Great Dane',
            'PERSONMATCHGOODWITHCATS': '0',
            'PERSONMATCHGOODWITHDOGS': '0',
            'PERSONMATCHGOODWITHCHILDREN': '0',
            'PERSONMATCHHOUSETRAINED': '0',
            'PERSONMATCHCOMMENTSCONTAIN': 'aglet',
            'PERSONADDITIONALANTLERS': 'Y',
            'PERSONIMAGE': 'https://sheltermanager.com/images/bg-hero-pets.png',# To do - could I use a local image here?
            'DIARYDATE': datetime.date(2001, 9, 11),
            'DIARYFOR': 'Baldrick',
            'DIARYSUBJECT': 'Test diary note from csv import',
            'DIARYNOTE': 'This note was created as part of the CSV import unit test.'
            
        },
    )
    minimalincidentcsvdata = (
        {
            'INCIDENTDATE': datetime.date(2001, 9, 11),
            'PERSONNAME': 'Sir Bob Hoskins',
            'INCIDENTNOTES': 'This incident was created as part of the CSV import unit test.'
        },
    )
    complexincidentcsvdata = (
        {
            'INCIDENTDATE': datetime.date(2001, 9, 11),
            'INCIDENTTIME': '13:00',
            'INCIDENTCOMPLETEDDATE': datetime.date(2001, 9, 20),
            'INCIDENTCOMPLETEDTIME': '14:00',
            'INCIDENTCOMPLETEDTYPE': 'Other',
            'INCIDENTRESPONDEDDATE': datetime.date(2001, 9, 15),
            'INCIDENTFOLLOWUPDATE': datetime.date(2001, 9, 16),
            'INCIDENTTYPE': 'Animal defecation',
            'INCIDENTNOTES': 'This incident was created as part of the CSV import unit test.',
            'DISPATCHACO': 'Sir Bob Hoskins',# To do - What happens if this ACO doesn't exist or isn't flagged as ACO?
            'DISPATCHDATE': datetime.date(2001, 9, 14),
            'DISPATCHTIME': '15:00',
            'DISPATCHADDRESS': '13 Baker Street',
            'DISPATCHCITY': 'Manchester',
            'DISPATCHSTATE': 'Somerset',
            'DISPATCHZIPCODE': 'W12 4YU',
            'INCIDENTANIMALSPECIES': 'Dog',
            'INCIDENTANIMALSEX': 'Unknown',
            'INCIDENTANIMALDESCRIPTION': 'Covered in burns.',
            'PERSONNAME': 'Sir Bob Hoskins'
        },
    )
    minimallicensecsvdata = (
        {
            'LICENSENUMBER': '666',
            'PERSONNAME': 'Sir Bob Hoskins',
            'LICENSECOMMENTS': 'This license was created as part of the CSV import unit test.'
        },
    )
    complexlicensecsvdata = (
        {
            'LICENSETYPE': 'Altered Dog - 1 year',
            'LICENSENUMBER': '666',
            'LICENSEFEE': '690',
            'LICENSEISSUEDATE': datetime.date(2001, 9, 14),
            'LICENSEEXPIRESDATE': datetime.date(2005, 9, 14),
            'LICENSECOMMENTS': 'This license was created as part of the CSV import unit test.',
            'PERSONNAME': 'Sir Bob Hoskins'
        },
    )
    minimalstocklevelcsvdata = (
        {
            'STOCKLEVELNAME': 'Plumbus',
            'STOCKLEVELUNITNAME': 'plumbus',
            'STOCKLEVELTOTAL': '1',
            'STOCKLEVELBALANCE': '1',
            'STOCKLEVELCOST': '1',# To do - should this be required??
            'STOCKLEVELUNITPRICE': '1',# To do - should this be required??
            'STOCKLEVELLOW': '0',# To do - should this be required??
            'STOCKLEVELDESCRIPTION': 'This stock level was created as part of the CSV import unit test.'
        },
    )
    complexstocklevelcsvdata = (
        {
            'STOCKLEVELNAME': 'Plumbus',
            'STOCKLEVELDESCRIPTION': 'This stock level was created as part of the CSV import unit test.',
            'STOCKLEVELBARCODE': '1234567',
            'STOCKLEVELLOCATIONNAME': 'Stores',
            'STOCKLEVELLOCATIONNAME': 'Stores',
            'STOCKLEVELUNITNAME': 'plumbus',
            'STOCKLEVELTOTAL': '1',
            'STOCKLEVELBALANCE': '1',
            'STOCKLEVELLOW': '0',
            'STOCKLEVELEXPIRY': datetime.date(2030, 9, 14),
            'STOCKLEVELBATCHNUMBER': 'AA112233',
            'STOCKLEVELCOST': '1',
            'STOCKLEVELUNITPRICE': '1'
        },
    )

    def setUp(self):
        data = {
            "name":   "cuteness",
            "label":  "Cuteness",
            "tooltip": "How cute is this animal?",
            "lookupvalues": "",
            "mandatory": "off",
            "type": "1",
            "link": "0",
            "displayindex": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        self.aafid = asm3.additional.insert_field_from_form(base.get_dbo(), "test", post)

        data = {
            "name":   "antlers",
            "label":  "Antlers",
            "tooltip": "Does this person have antlers?",
            "lookupvalues": "",
            "mandatory": "off",
            "type": "0",
            "link": "1",
            "displayindex": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        self.apfid = asm3.additional.insert_field_from_form(base.get_dbo(), "test", post)

    def tearDown(self):
        mediaids = base.get_dbo().query_list("SELECT media.ID FROM media INNER JOIN animal ON media.LinkID = animal.ID WHERE media.LinkTypeID = 0 AND animal.AnimalName = 'TestioCSV'")
        for mid in mediaids:
            base.execute("DELETE FROM media WHERE ID = %s" % (mid,))

        mediaids = base.get_dbo().query_list("SELECT media.ID FROM media INNER JOIN owner ON media.LinkID = owner.ID WHERE media.LinkTypeID = 3 AND owner.OwnerName = 'Sir Bob Hoskins'")
        for mid in mediaids:
            base.execute("DELETE FROM media WHERE ID = %s" % (mid,))

        base.execute("DELETE FROM animal WHERE AnimalName = 'TestioCSV'")
        base.execute("DELETE FROM diary WHERE Subject = 'Test diary note from csv import'")
        base.execute("DELETE FROM owner WHERE OwnerName = 'Sir Bob Hoskins'")
        base.execute("DELETE FROM owner WHERE OwnerName = 'Baron Barry Gibb'")
        base.execute("DELETE FROM animalcontrol WHERE CallNotes = 'This incident was created as part of the CSV import unit test.'")
        base.execute("DELETE FROM ownerlicence WHERE Comments = 'This license was created as part of the CSV import unit test.'")

        asm3.additional.delete_field(base.get_dbo(), "test", self.aafid)
        asm3.additional.delete_field(base.get_dbo(), "test", self.apfid)

    def test_csvexport_animals(self):
        asm3.csvimport.csvexport_animals(base.get_dbo(), "all")
    
    def test_csvexport_people_all_no_media(self):
        asm3.csvimport.csvexport_people(base.get_dbo(), "all", "", "", "none")
    
    def test_csvexport_people_photo(self):
        asm3.csvimport.csvexport_people(base.get_dbo(), "all", "", "", "photo")
    
    def test_csvexport_people_photos(self):
        asm3.csvimport.csvexport_people(base.get_dbo(), "all", "", "", "photos")
    
    def test_simple_animal_import(self):
        rows = self.minimalanimalcsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_complex_animal_import(self):
        rows = self.complexanimalcsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_simple_person_import(self):
        rows = self.minimalpersoncsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_complex_person_import(self):
        rows = self.complexpersoncsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_simple_incident_import(self):
        rows = self.minimalincidentcsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_complex_incident_import(self):
        rows = self.complexincidentcsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_simple_license_import(self):
        rows = self.minimallicensecsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_complex_license_import(self):
        rows = self.complexlicensecsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_simple_stocklevel_import(self):
        rows = self.minimalstocklevelcsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_complex_stocklevel_import(self):
        rows = self.complexstocklevelcsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])

    def test_csvimport(self):
        csvdata = "ANIMALNAME,ANIMALSEX,ANIMALAGE,PERSONNAME,INCIDENTDATE,DIARYDATE,DIARYFOR,DIARYSUBJECT,DIARYNOTE\n" \
            "\"TestioCSV\",\"Male\",\"2\",\"Sir Bob Hoskins\",\"2001-09-11\",\"2020-01-20\",\"Baldrick\",\"Test diary note from csv import\",\"This note was created as part of the CSV import unit test.\"\n" \
            "\"\",\"\",\"\",\"Sir Bob Hoskins\",\"\",\"2020-01-20\",\"Nanny\",\"Test diary note from csv import\",\"This note was created as part of the CSV import unit test.\"\n" \
            "\"\",\"\",\"\",\"Sir Bob Hoskins\",\"2001-09-11\",\"2020-01-20\",\"The Prince\",\"Test diary note from csv import\",\"This note was created as part of the CSV import unit test.\"\n"
        asm3.csvimport.csvimport(base.get_dbo(), csvdata)

        aid = base.get_dbo().query_int("SELECT ID FROM animal WHERE AnimalName = 'TestioCSV' ORDER BY ID DESC LIMIT 1")
        pid = base.get_dbo().query_int("SELECT ID FROM owner WHERE OwnerName = 'Sir Bob Hoskins' ORDER BY ID DESC LIMIT 1")
        
        f = open(base.PATH + "../src/media/reports/nopic.jpg", "rb")
        data = f.read()
        f.close()
        post = asm3.utils.PostedData({ "filename": "image.jpg", "filetype": "image/jpeg", "filedata": "data:image/jpeg;base64,%s" % asm3.utils.base64encode(data) }, "en")
        asm3.media.attach_file_from_form(base.get_dbo(), "test", asm3.media.ANIMAL, aid, asm3.media.MEDIASOURCE_ATTACHFILE, post)

        f = open(base.PATH + "../src/static/images/splash/splash_logo.jpg", "rb")
        data = f.read()
        f.close()

        asm3.media.attach_file_from_form(base.get_dbo(), "test", asm3.media.PERSON, pid, asm3.media.MEDIASOURCE_ATTACHFILE, post)