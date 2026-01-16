from asm3.dbupdate import execute

# Fix for incorrect column type in update 35108
execute(dbo.ddl_modify_column("animalcondition", "EndDateTime", dbo.type_datetime))
