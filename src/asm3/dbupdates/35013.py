from asm3.dbupdate import execute

execute(dbo, "INSERT INTO lksfieldtype (ID, FieldType) VALUES (?, ?)", [15, _("Number - Incrementing", dbo.locale)])
#execute(dbo,"CREATE TABLE additionalincrement ( ID INTEGER NOT NULL )")