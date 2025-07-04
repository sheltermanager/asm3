from asm3.dbupdate import execute

execute(dbo, "INSERT INTO lksfieldlink (ID, LinkType) VALUES (?, ?)", [31, _("Person - Couple", dbo.locale)])

