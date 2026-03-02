from asm3.dbupdate import execute

dbo = dbo
l = dbo.locale

# Add fluids and grooming to lksmedicaltype

execute(dbo, "INSERT INTO lksmedicaltype (ID, MedicalTypeName, Description, ForceSingleUse, IsRetired) VALUES (?, ?, ?, ?, ?)", [ 30, _("Fluids", l), "", 0, 0 ])
execute(dbo, "INSERT INTO lksmedicaltype (ID, MedicalTypeName, Description, ForceSingleUse, IsRetired) VALUES (?, ?, ?, ?, ?)", [ 31, _("Grooming", l), "", 0, 0 ])
