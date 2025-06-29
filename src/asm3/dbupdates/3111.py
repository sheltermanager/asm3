l = dbo.locale
# New additional field types to indicate location
execute(dbo,"UPDATE lksfieldlink SET LinkType = ? WHERE ID = 0", [ _("Animal - Additional", l) ])
execute(dbo,"UPDATE lksfieldlink SET LinkType = ? WHERE ID = 1", [ _("Person - Additional", l) ])
execute(dbo,"INSERT INTO lksfieldlink VALUES (2, ?)", [ _("Animal - Details", l) ])
execute(dbo,"INSERT INTO lksfieldlink VALUES (3, ?)", [ _("Animal - Notes", l) ])
execute(dbo,"INSERT INTO lksfieldlink VALUES (4, ?)", [ _("Animal - Entry", l) ])
execute(dbo,"INSERT INTO lksfieldlink VALUES (5, ?)", [ _("Animal - Health and Identification", l) ])
execute(dbo,"INSERT INTO lksfieldlink VALUES (6, ?)", [ _("Animal - Death", l) ])
execute(dbo,"INSERT INTO lksfieldlink VALUES (7, ?)", [ _("Person - Name and Address", l) ])
execute(dbo,"INSERT INTO lksfieldlink VALUES (8, ?)", [ _("Person - Type", l) ])
