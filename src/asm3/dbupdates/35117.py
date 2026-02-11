from asm3.dbupdate import execute

execute(dbo, "INSERT INTO lksconditiontype (ID, ConditionTypeName, Description, IsRetired) VALUES (?, ?, ?, ?)", [6, _("Heart"), "", 0] )
execute(dbo, "INSERT INTO lksconditiontype (ID, ConditionTypeName, Description, IsRetired) VALUES (?, ?, ?, ?)", [7, _("Endocrine"), "", 0] )
execute(dbo, "INSERT INTO lksconditiontype (ID, ConditionTypeName, Description, IsRetired) VALUES (?, ?, ?, ?)", [8, _("Cancer"), "", 0] )
execute(dbo, "INSERT INTO lksconditiontype (ID, ConditionTypeName, Description, IsRetired) VALUES (?, ?, ?, ?)", [9, _("Oral"), "", 0] )
execute(dbo, "INSERT INTO lksconditiontype (ID, ConditionTypeName, Description, IsRetired) VALUES (?, ?, ?, ?)", [10, _("Bone"), "", 0] )
