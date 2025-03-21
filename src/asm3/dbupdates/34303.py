# Add lkstransportstatus
l = dbo.locale
sql = "CREATE TABLE lkstransportstatus ( ID INTEGER NOT NULL PRIMARY KEY, " \
    "Name %(short)s NOT NULL)" % { "short": dbo.type_shorttext }
execute(dbo,sql)
execute(dbo,"INSERT INTO lkstransportstatus VALUES (1, ?)", [ _("New", l) ])
execute(dbo,"INSERT INTO lkstransportstatus VALUES (2, ?)", [ _("Confirmed", l) ])
execute(dbo,"INSERT INTO lkstransportstatus VALUES (3, ?)", [ _("Hold", l) ])
execute(dbo,"INSERT INTO lkstransportstatus VALUES (4, ?)", [ _("Scheduled", l) ])
execute(dbo,"INSERT INTO lkstransportstatus VALUES (10, ?)", [ _("Cancelled", l) ])
execute(dbo,"INSERT INTO lkstransportstatus VALUES (11, ?)", [ _("Completed", l) ])