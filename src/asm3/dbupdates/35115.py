from asm3.dbupdate import execute

dbo = dbo
l = dbo.locale

## Add fluids to lksmedicaltype

execute(dbo, "INSERT INTO lksmedicaltype (ID, MedicalTypeName, Description, ForceSingleUse, IsRetired) VALUES (?, ?, ?, ?, ?)", [ 30, _("Fluids", l), "", 0, 0 ])