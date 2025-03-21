l = dbo.locale
# Add reservation status
add_column(dbo, "adoption", "ReservationStatusID", "INTEGER")
add_index(dbo, "adoption_ReservationStatusID", "adoption", "ReservationStatusID")
sql = "CREATE TABLE reservationstatus ( ID INTEGER NOT NULL, " \
    "StatusName %(short)s NOT NULL, " \
    "StatusDescription %(long)s )" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
execute(dbo,sql)
execute(dbo,"INSERT INTO reservationstatus VALUES (1, '%s', '')" % _("More Info Needed", l))
execute(dbo,"INSERT INTO reservationstatus VALUES (2, '%s', '')" % _("Pending Vet Check", l))
execute(dbo,"INSERT INTO reservationstatus VALUES (3, '%s', '')" % _("Pending Apartment Verification", l))
execute(dbo,"INSERT INTO reservationstatus VALUES (4, '%s', '')" % _("Pending Home Visit", l))
execute(dbo,"INSERT INTO reservationstatus VALUES (5, '%s', '')" % _("Pending Adoption", l))
execute(dbo,"INSERT INTO reservationstatus VALUES (6, '%s', '')" % _("Changed Mind", l))
execute(dbo,"INSERT INTO reservationstatus VALUES (7, '%s', '')" % _("Denied", l))
execute(dbo,"INSERT INTO reservationstatus VALUES (8, '%s', '')" % _("Approved", l))
