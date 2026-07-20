from asm3.dbupdate import execute

execute(dbo, "INSERT INTO lksfieldlink (ID, LinkType) VALUES (?, ?)", [32, _("Animal in Event", dbo.locale)])
