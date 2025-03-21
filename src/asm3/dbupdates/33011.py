# Add donationpayment table and data
l = dbo.locale
sql = "CREATE TABLE donationpayment (ID INTEGER NOT NULL PRIMARY KEY, " \
    "PaymentName %(short)s NOT NULL, " \
    "PaymentDescription %(long)s ) " % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
execute(dbo,sql)
execute(dbo,"INSERT INTO donationpayment (ID, PaymentName) VALUES (1, '" + _("Cash", l) + "')")
execute(dbo,"INSERT INTO donationpayment (ID, PaymentName) VALUES (2, '" + _("Check", l) + "')")
execute(dbo,"INSERT INTO donationpayment (ID, PaymentName) VALUES (3, '" + _("Credit Card", l) + "')")
execute(dbo,"INSERT INTO donationpayment (ID, PaymentName) VALUES (4, '" + _("Debit Card", l) + "')")
# Add donationpaymentid field to donations
execute(dbo,"ALTER TABLE ownerdonation ADD DonationPaymentID INTEGER")
execute(dbo,"UPDATE ownerdonation SET DonationPaymentID = 1")
