l = dbo.locale
# New additional field types to indicate location
execute(dbo,"UPDATE lksfieldlink SET LinkType = '%s' WHERE ID = 0" % _("Animal - Additional", l))
execute(dbo,"UPDATE lksfieldlink SET LinkType = '%s' WHERE ID = 1" % _("Person - Additional", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (2, '%s')" % _("Animal - Details", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (3, '%s')" % _("Animal - Notes", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (4, '%s')" % _("Animal - Entry", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (5, '%s')" % _("Animal - Health and Identification", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (6, '%s')" % _("Animal - Death", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (7, '%s')" % _("Person - Name and Address", l))
execute(dbo,"INSERT INTO lksfieldlink VALUES (8, '%s')" % _("Person - Type", l))