# Add asilomar fields for US users
execute(dbo,"ALTER TABLE animal ADD AsilomarIsTransferExternal INTEGER")
execute(dbo,"ALTER TABLE animal ADD AsilomarIntakeCategory INTEGER")
execute(dbo,"ALTER TABLE animal ADD AsilomarOwnerRequestedEuthanasia INTEGER")
execute(dbo,"UPDATE animal SET AsilomarIsTransferExternal = 0, AsilomarIntakeCategory = 0, AsilomarOwnerRequestedEuthanasia = 0")
