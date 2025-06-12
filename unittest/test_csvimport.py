
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
            'ANIMALIMAGE': 'https://sheltermanager.com/images/bg-hero-pets.png',
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
            'ANIMALUNIT': '1',
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
            'VACCINATIONCOMMENTS': 'This vaccination was created by the CSV Import unit test.'
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
            'PERSONMATCHGOODWITHCATS': 'Yes',
            'PERSONMATCHGOODWITHDOGS': 'No',
            'PERSONMATCHGOODWITHCHILDREN': '0',
            'PERSONMATCHHOUSETRAINED': '0',
            'PERSONMATCHCOMMENTSCONTAIN': 'aglet',
            'PERSONADDITIONALANTLERS': 'Y',
            'PERSONIMAGE': 'https://sheltermanager.com/images/bg-hero-pets.png',
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
            'DISPATCHACO': 'Sir Bob Hoskins',
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
        base.execute("DELETE FROM stocklevel WHERE Description = 'This stock level was created as part of the CSV import unit test.'")
        base.execute("DELETE FROM animalcost WHERE Description = 'This cost was created by the csvimport unit test.'")
        base.execute("DELETE FROM log WHERE Comments = 'This log was created by the CSV Import unit test.'")
        base.execute("DELETE FROM animalmedical WHERE Comments = 'This regimen was created by the CSV Import unit test.'")
        base.execute("DELETE FROM adoption WHERE Comments = 'This movement was created by the CSV Import unit test.'")
        base.execute("DELETE FROM animaltest WHERE Comments = 'This test was created by the CSV Import unit test.'")
        base.execute("DELETE FROM animalvaccination WHERE Comments = 'This vaccination was created by the CSV Import unit test.'")
        base.execute("DELETE FROM species WHERE SpeciesName = 'Unicorn'")
        base.execute("DELETE FROM jurisdiction WHERE JurisdictionName = 'Atlantis'")

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
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "test", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_complex_animal_import(self):
        rows = self.complexanimalcsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "test", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_complex_animal_import_missing_lookups_insert_on(self):
        rows = self.complexanimalcsvdata
        rows[0]['ANIMALSPECIES'] = 'Unicorn'
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "test", True, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
        result = base.query("SELECT ID FROM species WHERE SpeciesName = '%s'" % 'Unicorn')
        self.assertEqual(1, len(result))
    
    def test_complex_animal_import_missing_lookups_insert_off(self):
        rows = self.complexanimalcsvdata
        rows[0]['ANIMALSPECIES'] = 'Unicorn'
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "test", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
        result = base.query("SELECT ID FROM species WHERE SpeciesName = '%s'" % 'Unicorn')
        self.assertEqual(0, len(result))
    
    def test_complex_animal_import_image_data(self):
        rows = self.complexanimalcsvdata
        rows[0]['ANIMALIMAGE'] = imagedata,
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "test", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
        result = base.query("SELECT ID FROM species WHERE SpeciesName = '%s'" % 'Unicorn')
        self.assertEqual(0, len(result))
    
    def test_simple_person_import(self):
        rows = self.minimalpersoncsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "test", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_complex_person_import(self):
        rows = self.complexpersoncsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "test", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_complex_person_import_missing_lookups_insert_on(self):
        rows = self.complexpersoncsvdata
        rows[0]['PERSONJURISDICTION'] = 'Atlantis'
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "test", True, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
        result = base.query("SELECT ID FROM jurisdiction WHERE JurisdictionName = '%s'" % 'Atlantis')
    
    def test_complex_person_import_missing_lookups_insert_off(self):
        rows = self.complexpersoncsvdata
        rows[0]['PERSONJURISDICTION'] = 'Atlantis'
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "test", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
        result = base.query("SELECT ID FROM jurisdiction WHERE JurisdictionName = '%s'" % 'Atlantis')
    
    def test_simple_incident_import(self):
        rows = self.minimalincidentcsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "test", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_complex_incident_import(self):
        rows = self.complexincidentcsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "test", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_simple_license_import(self):
        rows = self.minimallicensecsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "test", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_complex_license_import(self):
        rows = self.complexlicensecsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "test", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_simple_stocklevel_import(self):
        rows = self.minimalstocklevelcsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "test", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])
    
    def test_complex_stocklevel_import(self):
        rows = self.complexstocklevelcsvdata
        csvdata = asm3.utils.csv(base.get_dbo().locale, rows)
        result = asm3.csvimport.csvimport(base.get_dbo(), csvdata, "utf-8-sig", "test", False, False, True, False, False, False, True)
        self.assertEqual(0, len(json.loads(result)['errors']))
        self.assertEqual(1, json.loads(result)['success'])

imagedata = 'data:image/jpeg;base64,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'