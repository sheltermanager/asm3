from asm3.dbupdate import execute

execute(dbo, "INSERT INTO lksfieldlink (LinkType) VALUES (?)", [_("Person - Couple", dbo.locale),])

