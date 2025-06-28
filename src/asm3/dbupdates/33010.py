# Add new additional field types and locations
l = dbo.locale
execute(dbo,"INSERT INTO lksfieldtype (ID, FieldType) VALUES (7, ?)", [ _("Multi-Lookup", l) ])
execute(dbo,"INSERT INTO lksfieldtype (ID, FieldType) VALUES (8, ?)", [ _("Animal", l) ])
execute(dbo,"INSERT INTO lksfieldtype (ID, FieldType) VALUES (9, ?)", [ _("Person", l) ])
execute(dbo,"INSERT INTO lksfieldlink (ID, LinkType) VALUES (9, ?)", [ _("Lost Animal - Additional", l) ])
execute(dbo,"INSERT INTO lksfieldlink (ID, LinkType) VALUES (10, ?)", [ _("Lost Animal - Details", l) ])
execute(dbo,"INSERT INTO lksfieldlink (ID, LinkType) VALUES (11, ?)", [ _("Found Animal - Additional", l) ])
execute(dbo,"INSERT INTO lksfieldlink (ID, LinkType) VALUES (12, ?)", [ _("Found Animal - Details", l) ])
execute(dbo,"INSERT INTO lksfieldlink (ID, LinkType) VALUES (13, ?)", [ _("Waiting List - Additional", l) ])
execute(dbo,"INSERT INTO lksfieldlink (ID, LinkType) VALUES (14, ?)", [ _("Waiting List - Details", l) ])
execute(dbo,"INSERT INTO lksfieldlink (ID, LinkType) VALUES (15, ?)", [ _("Waiting List - Removal", l) ])
