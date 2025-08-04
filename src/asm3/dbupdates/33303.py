# Add new incident link types
l = dbo.locale
execute(dbo,"INSERT INTO lksloglink (ID, LinkType) VALUES (?, ?)", [ 6, _("Incident", l) ])
execute(dbo,"INSERT INTO lksmedialink (ID, LinkType) VALUES (?, ?)", [ 6, _("Incident", l) ])
execute(dbo,"INSERT INTO lksdiarylink (ID, LinkType) VALUES (?, ?)", [ 7, _("Incident", l) ])
execute(dbo,"INSERT INTO lksfieldlink VALUES (16, ?)", [ _("Incident - Details", l) ])
execute(dbo,"INSERT INTO lksfieldlink VALUES (17, ?)", [ _("Incident - Dispatch", l) ])
execute(dbo,"INSERT INTO lksfieldlink VALUES (18, ?)", [ _("Incident - Owner", l) ])
execute(dbo,"INSERT INTO lksfieldlink VALUES (19, ?)", [ _("Incident - Citation", l) ])
execute(dbo,"INSERT INTO lksfieldlink VALUES (20, ?)", [ _("Incident - Additional", l) ])
