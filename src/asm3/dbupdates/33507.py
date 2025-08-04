l = dbo.locale
# Add reservation status
add_column(dbo, "adoption", "ReservationStatusID", "INTEGER")
add_index(dbo, "adoption_ReservationStatusID", "adoption", "ReservationStatusID")
sql = "CREATE TABLE reservationstatus ( ID INTEGER NOT NULL, " \
    "StatusName %(short)s NOT NULL, " \
    "StatusDescription %(long)s )" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
execute(dbo,sql)
execute(dbo,"INSERT INTO reservationstatus VALUES (1, ?, '')", [ _("More Info Needed", l)])
execute(dbo,"INSERT INTO reservationstatus VALUES (2, ?, '')", [ _("Pending Vet Check", l)])
execute(dbo,"INSERT INTO reservationstatus VALUES (3, ?, '')", [ _("Pending Apartment Verification", l)])
execute(dbo,"INSERT INTO reservationstatus VALUES (4, ?, '')", [ _("Pending Home Visit", l)])
execute(dbo,"INSERT INTO reservationstatus VALUES (5, ?, '')", [ _("Pending Adoption", l)])
execute(dbo,"INSERT INTO reservationstatus VALUES (6, ?, '')", [ _("Changed Mind", l)])
execute(dbo,"INSERT INTO reservationstatus VALUES (7, ?, '')", [ _("Denied", l)])
execute(dbo,"INSERT INTO reservationstatus VALUES (8, ?, '')", [ _("Approved", l)])
