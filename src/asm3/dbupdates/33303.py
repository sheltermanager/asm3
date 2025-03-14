# Add new incident link types
l = dbo.locale
execute(dbo,"INSERT INTO lksloglink (ID, LinkType) VALUES (%d, '%s')" % (6, _("Incident", l)))
execute(dbo,"INSERT INTO lksmedialink (ID, LinkType) VALUES (%d, '%s')" % (6, _("Incident", l)))
execute(dbo,"INSERT INTO lksdiarylink (ID, LinkType) VALUES (%d, '%s')" % (7, _("Incident", l)))
execute(dbo,"INSERT INTO lksfieldlink VALUES (16, '%s')" % _("Incident - Details", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (17, '%s')" % _("Incident - Dispatch", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (18, '%s')" % _("Incident - Owner", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (19, '%s')" % _("Incident - Citation", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (20, '%s')" % _("Incident - Additional", l))