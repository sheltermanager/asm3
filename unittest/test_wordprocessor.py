
import unittest
import base
import asm3.animal
import asm3.template
import asm3.utils
import asm3.wordprocessor

class TestTemplate(unittest.TestCase):

    def setUp(self):
        # Remove Test Template(s)
        tid = base.get_dbo().query_int("SELECT ID FROM templatedocument WHERE Name = ?", ["Test_Template.html",])
        #print("\ntid = " + tid)
        asm3.template.delete_document_template(base.get_dbo(), "test", tid)
        
        # Create an animal
        data = {
            "animalname": "Testio",
            "estimatedage": "1",
            "animaltype": "1",
            "entryreason": "1",
            "species": "1",
            "datebroughtin": "01/11/1985"
        }
        post = asm3.utils.PostedData(data, "en")
        self.aid = asm3.animal.insert_animal_from_form(base.get_dbo(), post, "test")[0]

        # Create a person
        data = {
            "title": "Mr",
            "forenames": "Unit",
            "surname": "Testing",
            "ownertype": "1",
            "address": "123 test street"
        }
        post = asm3.utils.PostedData(data, "en")
        self.oid = asm3.person.insert_person_from_form(base.get_dbo(), post, "test", geocode=False)

        # Create a movement
        data = {
            "animal": str(self.aid),
            "person": str(self.oid),
            "movementdate": "05/11/1985",
            "type": "1",
        }
        post = asm3.utils.PostedData(data, "en")
        self.mid = asm3.movement.insert_movement_from_form(base.get_dbo(), "test", post)
    
    def tearDown(self):
        asm3.movement.delete_movement(base.get_dbo(), "test", self.mid)
        asm3.animal.delete_animal(base.get_dbo(), "test", self.aid)
        asm3.person.delete_person(base.get_dbo(), "test", self.oid)
        

    def test_generate_animal_doc(self):
        # Create an animal template
        templatecontent = b"<h1>Animal Test Template</h1>" \
        b"<p>Animal Name: &lt;&lt;AnimalName&gt;&gt;</p>" \
        b"<p>Person Name: &lt;&lt;OwnerName&gt;&gt;</p>"
        tid = asm3.template.create_document_template(base.get_dbo(), "test", "Test_Template", ".html", templatecontent)

        output = asm3.wordprocessor.generate_animal_doc(base.get_dbo(), tid, self.aid, "test")
        expectedoutput = "<h1>Animal Test Template</h1>" \
        "<p>Animal Name: Testio</p>" \
        "<p>Person Name: Mr Unit Testing</p>"

        self.assertEqual(output, expectedoutput, "Animal document output differs from expectation.")

        asm3.template.delete_document_template(base.get_dbo(), "test", tid)
    
    def test_generate_animalcontrol_doc(self):
        # Create an animalcontrol template
        templatecontent = b"<h1>Animal Control Test Template</h1>" \
        b"<p>Incident Date: &lt;&lt;IncidentDate&gt;&gt;</p>" \
        b"<p>Incident Time: &lt;&lt;IncidentTime&gt;&gt;</p>"
        tid = asm3.template.create_document_template(base.get_dbo(), "test", "Test_Template", ".html", templatecontent)

        # Creating incident
        data = {
            "incidentdate":   "01/01/2014",
            "incidenttime":   "00:00:00"
        }
        post = asm3.utils.PostedData(data, "en")
        iid = asm3.animalcontrol.insert_animalcontrol_from_form(base.get_dbo(), post, "test", geocode=False)
        
        output = asm3.wordprocessor.generate_animalcontrol_doc(base.get_dbo(), tid, iid, "test")
        expectedoutput = "<h1>Animal Control Test Template</h1>" \
        "<p>Incident Date: 01/01/2014</p>" \
        "<p>Incident Time: 00:00</p>"

        self.assertEqual(output, expectedoutput, "Animal control document output differs from expectation.")

        asm3.animalcontrol.delete_animalcontrol(base.get_dbo(), "test", iid)
    
    def test_generate_boarding_doc(self):
        # Create an boarding template
        templatecontent = b"<h1>Boarding Test Template</h1>" \
        b"<p>From Date: &lt;&lt;BoardingFromDate&gt;&gt;</p>" \
        b"<p>To Date: &lt;&lt;BoardingToDate&gt;&gt;</p>"
        tid = asm3.template.create_document_template(base.get_dbo(), "test", "Test_Template", ".html", templatecontent)

        # Create a boarding record
        data = {
            "person": str(self.oid),
            "animal": str(self.aid),
            "type": "1",
            "indate": "01/01/2014",
            "outdate": "08/01/2014",
            "dailyfee": "1000"
        }
        post = asm3.utils.PostedData(data, "en")
        bid = asm3.financial.insert_boarding_from_form(base.get_dbo(), "test", post)

        output = asm3.wordprocessor.generate_boarding_doc(base.get_dbo(), tid, bid, "test")
        expectedoutput = "<h1>Boarding Test Template</h1>" \
        "<p>From Date: 01/01/2014</p>" \
        "<p>To Date: 08/01/2014</p>"

        self.assertEqual(output, expectedoutput, "Boarding document output differs from expectation.")

        asm3.financial.delete_boarding(base.get_dbo(), "test", bid)
    
    def test_generate_clinic_doc(self):
        # Create an boarding template
        templatecontent = b"<h1>Clinic Appointment Test Template</h1>" \
        b"<p>Appointment Date: &lt;&lt;AppointmentDate&gt;&gt;</p>" \
        b"<p>Appointment Time: &lt;&lt;AppointmentTime&gt;&gt;</p>" \
        b"<p>Invoice Total: &lt;&lt;InvoiceTotal&gt;&gt;</p>"
        tid = asm3.template.create_document_template(base.get_dbo(), "test", "Test_Template", ".html", templatecontent)

        # Creating a clinic appointment
        data = {
            "animal": str(self.aid),
            "person": str(self.oid),
            "apptdate": "11/09/2024",
            "appttime": "12:00:00",
            "status": "1",
        }
        post = asm3.utils.PostedData(data, "en")
        caid = asm3.clinic.insert_appointment_from_form(base.get_dbo(), "test", post)

        # Create a clinic invoice
        data = {
            "appointmentid": str(caid),
            "description": "foo",
            "amount": "50"
        }
        post = asm3.utils.PostedData(data, "en")
        ciid = asm3.clinic.insert_invoice_from_form(base.get_dbo(), "test", post)

        output = asm3.wordprocessor.generate_clinic_doc(base.get_dbo(), tid, caid, "test")
        expectedoutput = "<h1>Clinic Appointment Test Template</h1>" \
        "<p>Appointment Date: 11/09/2024</p>" \
        "<p>Appointment Time: 12:00</p>" \
        "<p>Invoice Total: 0.50</p>"

        self.assertEqual(output, expectedoutput, "Clinic document output differs from expectation.")
        
        asm3.clinic.delete_invoice(base.get_dbo(), "test", ciid)
        asm3.clinic.delete_appointment(base.get_dbo(), "test", caid)
    
    def test_generate_person_doc(self):
        # Create an person template
        templatecontent = b"<h1>Person Test Template</h1>" \
        b"<p>Person Name: &lt;&lt;Name&gt;&gt;</p>"
        tid = asm3.template.create_document_template(base.get_dbo(), "test", "Test_Template", ".html", templatecontent)

        output = asm3.wordprocessor.generate_person_doc(base.get_dbo(), tid, self.oid, "test")
        expectedoutput = "<h1>Person Test Template</h1>" \
        "<p>Person Name: Mr Unit Testing</p>"

        self.assertEqual(output, expectedoutput, "Person document output differs from expectation.")

        asm3.template.delete_document_template(base.get_dbo(), "test", tid)
    
    def test_generate_donation_doc(self):
        # Create a payment template
        templatecontent = b"<h1>Payment Test Template</h1>" \
        b"<p>Person Name: &lt;&lt;Name&gt;&gt;</p>" \
        b"<p>Animal Name: &lt;&lt;AnimalName&gt;&gt;</p>" \
        b"<p>Payment Date: &lt;&lt;PaymentDate&gt;&gt;</p>" \
        b"<p>Payment Amount: &lt;&lt;PaymentGross&gt;&gt;</p>"
        tid = asm3.template.create_document_template(base.get_dbo(), "test", "Test_Template", ".html", templatecontent)

        # Create person only donation
        data = {
            "person": str(self.oid),
            "animal": "0",
            "type":   "1",
            "payment": "1",
            "frequency": "0",
            "amount": "1000",
            "due": "01/02/2025",
            "received": "01/02/2025"
        }
        post = asm3.utils.PostedData(data, "en")
        did1 = asm3.financial.insert_donation_from_form(base.get_dbo(), "test", post)

        # Create person/animal donation
        data = {
            "person": str(self.oid),
            "animal": str(self.aid),
            "type":   "1",
            "payment": "1",
            "frequency": "0",
            "amount": "1000",
            "due": "01/02/2025",
            "received": "01/02/2025"
        }
        post = asm3.utils.PostedData(data, "en")
        did2 = asm3.financial.insert_donation_from_form(base.get_dbo(), "test", post)

        donationids = [did1,]

        output = asm3.wordprocessor.generate_donation_doc(base.get_dbo(), tid, donationids, "test")
        expectedoutput = "<h1>Payment Test Template</h1>" \
        "<p>Person Name: Mr Unit Testing</p>" \
        "<p>Animal Name: </p>" \
        "<p>Payment Date: 01/02/2025</p>" \
        "<p>Payment Amount: 10.00</p>"

        self.assertEqual(output, expectedoutput, "Payment document (person only) output differs from expectation.")

        donationids = [did2,]
        asm3.financial.delete_donation(base.get_dbo(), "test", did1)
        
        output = asm3.wordprocessor.generate_donation_doc(base.get_dbo(), tid, donationids, "test")
        expectedoutput = "<h1>Payment Test Template</h1>" \
        "<p>Person Name: Mr Unit Testing</p>" \
        "<p>Animal Name: Testio</p>" \
        "<p>Payment Date: 01/02/2025</p>" \
        "<p>Payment Amount: 10.00</p>"

        self.assertEqual(output, expectedoutput, "Payment document (animal linked) output differs from expectation.")

        asm3.financial.delete_donation(base.get_dbo(), "test", did2)
        asm3.template.delete_document_template(base.get_dbo(), "test", tid)
    
    def test_generate_foundanimal_doc(self):
        # Create a found animal template
        templatecontent = b"<h1>Found Animal Test Template</h1>" \
        b"<p>Person Name: &lt;&lt;Name&gt;&gt;</p>" \
        b"<p>Date Found: &lt;&lt;DateFound&gt;&gt;</p>"
        tid = asm3.template.create_document_template(base.get_dbo(), "test", "Test_Template", ".html", templatecontent)

        # Create a found animal record
        data = {
            "datefound": "11/09/2001",
            "datereported": "11/09/2001",
            "owner": str(self.oid),
            "species": "1", 
            "sex": "1",
            "breed": "1",
            "colour": "1",
            "markings": "Test",
            "areafound": "Test",
            "areapostcode": "Test"
        }
        post = asm3.utils.PostedData(data, "en")
        faid = asm3.lostfound.insert_foundanimal_from_form(base.get_dbo(), post, "test")
        
        output = asm3.wordprocessor.generate_foundanimal_doc(base.get_dbo(), tid, faid, "test")
        expectedoutput = "<h1>Found Animal Test Template</h1>" \
        "<p>Person Name: Mr Unit Testing</p>" \
        "<p>Date Found: 11/09/2001</p>"

        self.assertEqual(output, expectedoutput, "Found animal output differs from expectation.")

        asm3.lostfound.delete_foundanimal(base.get_dbo(), "test", faid)

        asm3.template.delete_document_template(base.get_dbo(), "test", tid)
    
    def test_generate_lostanimal_doc(self):
        # Create a lost animal template
        templatecontent = b"<h1>Lost Animal Test Template</h1>" \
        b"<p>Person Name: &lt;&lt;Name&gt;&gt;</p>" \
        b"<p>Date Lost: &lt;&lt;DateLost&gt;&gt;</p>"
        tid = asm3.template.create_document_template(base.get_dbo(), "test", "Test_Template", ".html", templatecontent)

        # Create a lost animal record
        data = {
            "datelost": "11/09/2001",
            "datereported": "11/09/2001",
            "owner": str(self.oid),
            "species": "1", 
            "sex": "1",
            "breed": "1",
            "colour": "1",
            "markings": "Test",
            "areafound": "Test",
            "areapostcode": "Test"
        }
        post = asm3.utils.PostedData(data, "en")
        laid = asm3.lostfound.insert_lostanimal_from_form(base.get_dbo(), post, "test")
        
        output = asm3.wordprocessor.generate_lostanimal_doc(base.get_dbo(), tid, laid, "test")
        expectedoutput = "<h1>Lost Animal Test Template</h1>" \
        "<p>Person Name: Mr Unit Testing</p>" \
        "<p>Date Lost: 11/09/2001</p>"

        self.assertEqual(output, expectedoutput, "Lost animal output differs from expectation.")
        asm3.lostfound.delete_lostanimal(base.get_dbo(), "test", laid)
        asm3.template.delete_document_template(base.get_dbo(), "test", tid)
    
    def test_generate_license_doc(self):
        # Create a licence template
        templatecontent = b"<h1>Licence Test Template</h1>" \
        b"<p>Person Name: &lt;&lt;Name&gt;&gt;</p>" \
        b"<p>Animal Name: &lt;&lt;AnimalName&gt;&gt;</p>" \
        b"<p>Expires: &lt;&lt;LicenceExpires&gt;&gt;</p>"
        tid = asm3.template.create_document_template(base.get_dbo(), "test", "Test_Template", ".html", templatecontent)

        # Create a licence record
        data = {
            "person": str(self.oid),
            "animal": str(self.aid),
            "type": "1",
            "number": "TESTLICENSE",
            "fee": "1000",
            "issuedate": "01/12/2024",
            "expirydate": "01/12/2025"
        }
        post = asm3.utils.PostedData(data, "en")
        lid = asm3.financial.insert_licence_from_form(base.get_dbo(), "test", post)

        output = asm3.wordprocessor.generate_licence_doc(base.get_dbo(), tid, lid, "test")
        expectedoutput = "<h1>Licence Test Template</h1>" \
        "<p>Person Name: Mr Unit Testing</p>" \
        "<p>Animal Name: Testio</p>" \
        "<p>Expires: 01/12/2025</p>"

        self.assertEqual(output, expectedoutput, "Licence output differs from expectation.")
        asm3.financial.delete_licence(base.get_dbo(), "test", lid)
        asm3.template.delete_document_template(base.get_dbo(), "test", tid)
    
    def test_generate_medical_doc(self):
        # Create a medical template
        templatecontent = b"<h1>Medical Test Template</h1>" \
        b"<p>Animal Name: &lt;&lt;AnimalName&gt;&gt;</p>"
        tid = asm3.template.create_document_template(base.get_dbo(), "test", "Test_Template", ".html", templatecontent)

        # Create a medical regim record
        data = {
            "animal": str(self.aid),
            "startdate": "01/04/2023",
            "treatmentname": "Test",
            "dosage": "Test",
            "timingrule": "1",
            "timingrulenofrequencies": "1",
            "timingrulefrequency": "1",
            "totalnumberoftreatments": "1",
            "treatmentrule": "1",
            "singlemulti": "1"
        }
        post = asm3.utils.PostedData(data, "en")   
        mid = asm3.medical.insert_regimen_from_form(base.get_dbo(), "test", post)

        output = asm3.wordprocessor.generate_medical_doc(base.get_dbo(), tid, [mid,], "test")
        expectedoutput = "<h1>Medical Test Template</h1>" \
        "<p>Animal Name: Testio</p>"

        self.assertEqual(output, expectedoutput, "Medical output differs from expectation.")
        asm3.medical.delete_regimen(base.get_dbo(), "test", mid)
        asm3.template.delete_document_template(base.get_dbo(), "test", tid)
    
    def test_generate_movement_doc(self):
        # Create a movement template
        templatecontent = b"<h1>Movement Test Template</h1>" \
        b"<p>Animal Name: &lt;&lt;AnimalName&gt;&gt;</p>" \
        b"<p>Adopter Name: &lt;&lt;Name&gt;&gt;</p>" \
        b"<p>Movement Date: &lt;&lt;MovementDate&gt;&gt;</p>"
        tid = asm3.template.create_document_template(base.get_dbo(), "test", "Test_Template", ".html", templatecontent)

        output = asm3.wordprocessor.generate_movement_doc(base.get_dbo(), tid, self.mid, "test")
        expectedoutput = "<h1>Movement Test Template</h1>" \
        "<p>Animal Name: Testio</p>" \
        "<p>Adopter Name: Mr Unit Testing</p>" \
        "<p>Movement Date: 05/11/1985</p>"

        self.assertEqual(output, expectedoutput, "Movement output differs from expectation.")

        asm3.template.delete_document_template(base.get_dbo(), "test", tid)
    
    def test_generate_transport_doc(self):
        # Create a transport template
        templatecontent = b"<h1>Transport Test Template</h1>" \
        b"<p>Animal Name: &lt;&lt;TransportAnimalName&gt;&gt;</p>" \
        b"<p>Driver Name: &lt;&lt;TransportDriverName&gt;&gt;</p>" \
        b"<p>Pickup Date: &lt;&lt;TransportPickupDate&gt;&gt;</p>"
        tid = asm3.template.create_document_template(base.get_dbo(), "test", "Test_Template", ".html", templatecontent)

        # Create a transport record
        data = {
            "animal": str(self.aid),
            "driver": str(self.oid),
            "pickup": str(self.oid),
            "dropoff": str(self.oid),
            "pickupdate": "05/03/2024",
            "dropoffdate": "06/03/2024",
            "status": "1"
        }
        post = asm3.utils.PostedData(data, "en")
        trid = asm3.movement.insert_transport_from_form(base.get_dbo(), "test", post)

        output = asm3.wordprocessor.generate_transport_doc(base.get_dbo(), tid, [trid,], "test")
        expectedoutput = "<h1>Transport Test Template</h1>" \
        "<p>Animal Name: Testio</p>" \
        "<p>Driver Name: Mr Unit Testing</p>" \
        "<p>Pickup Date: 05/03/2024</p>"

        self.assertEqual(output, expectedoutput, "Transport output differs from expectation.")

        asm3.movement.delete_transport(base.get_dbo(), "test", trid)
        asm3.template.delete_document_template(base.get_dbo(), "test", tid)
    
    def test_generate_voucher_doc(self):
        # Create a voucher template
        templatecontent = b"<h1>Voucher Test Template</h1>" \
        b"<p>Person Name: &lt;&lt;Name&gt;&gt;</p>" \
        b"<p>Animal Name: &lt;&lt;AnimalName&gt;&gt;</p>" \
        b"<p>Voucher Code: &lt;&lt;VoucherCode&gt;&gt;</p>"
        tid = asm3.template.create_document_template(base.get_dbo(), "test", "Test_Template", ".html", templatecontent)

        # Create a voucher record
        data = {
            "person": str(self.oid),
            "animal": str(self.aid),
            "type": "1",
            "issued": "01/03/2024",
            "expires": "01/03/2025",
            "amount": "1000",
            "vouchercode": "b00b135"
        }
        post = asm3.utils.PostedData(data, "en")
        vid = asm3.financial.insert_voucher_from_form(base.get_dbo(), "test", post)

        output = asm3.wordprocessor.generate_voucher_doc(base.get_dbo(), tid, vid, "test")
        expectedoutput = "<h1>Voucher Test Template</h1>" \
        "<p>Person Name: Mr Unit Testing</p>" \
        "<p>Animal Name: Testio</p>" \
        "<p>Voucher Code: b00b135</p>"

        self.assertEqual(output, expectedoutput, "Voucher output differs from expectation.")

        asm3.financial.delete_voucher(base.get_dbo(), "test", vid)
        asm3.template.delete_document_template(base.get_dbo(), "test", tid)
    
    def test_generate_waitinglist_doc(self):
        # Create a waiting list template
        templatecontent = b"<h1>Waiting List Test Template</h1>" \
        b"<p>Person Name: &lt;&lt;Name&gt;&gt;</p>" \
        b"<p>Animal Name: &lt;&lt;AnimalName&gt;&gt;</p>"
        tid = asm3.template.create_document_template(base.get_dbo(), "test", "Test_Template", ".html", templatecontent)

        # Creating waiting list record
        data = {
            "dateputon": "11/06/2000",
            "description": "Test",
            "species": "1",
            "size": "1",
            "owner": str(self.oid),
            "urgency": "5",
            "animalname": "Terry"
        }
        post = asm3.utils.PostedData(data, "en")
        wid = asm3.waitinglist.insert_waitinglist_from_form(base.get_dbo(), post, "test")

        output = asm3.wordprocessor.generate_waitinglist_doc(base.get_dbo(), tid, wid, "test")
        expectedoutput = "<h1>Waiting List Test Template</h1>" \
        "<p>Person Name: Mr Unit Testing</p>" \
        "<p>Animal Name: Terry</p>"

        self.assertEqual(output, expectedoutput, "Voucher output differs from expectation.")

        asm3.waitinglist.delete_waitinglist(base.get_dbo(), "test", wid)
        asm3.template.delete_document_template(base.get_dbo(), "test", tid)

