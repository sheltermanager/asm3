# Add lksynunk
l = dbo.locale
sql = "CREATE TABLE lksynunk ( ID INTEGER NOT NULL PRIMARY KEY, " \
    "Name %(short)s NOT NULL)" % { "short": dbo.type_shorttext }
execute(dbo,sql)
execute(dbo,"INSERT INTO lksynunk VALUES (0, ?)", [ _("Yes", l) ])
execute(dbo,"INSERT INTO lksynunk VALUES (1, ?)", [ _("No", l) ])
execute(dbo,"INSERT INTO lksynunk VALUES (2, ?)", [ _("Unknown", l) ])
execute(dbo,"INSERT INTO lksynunk VALUES (5, ?)", [ _("Over 5", l) ])
execute(dbo,"INSERT INTO lksynunk VALUES (12, ?)", [ _("Over 12", l) ])