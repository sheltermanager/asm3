from asm3.dbupdate import add_column, add_index, execute

add_column(dbo, "animal", "IdentichipStatus", dbo.type_integer)
add_column(dbo, "animal", "Identichip2Status", dbo.type_integer)

add_index(dbo, "animal_IdentichipStatus", "animal", "IdentichipStatus")
add_index(dbo, "animal_Identichip2Status", "animal", "Identichip2Status")

execute(dbo, "UPDATE animal SET IdentichipStatus=0, Identichip2Status=0")
execute(dbo, "INSERT INTO configuration (ItemName, ItemValue) VALUES (?, ?)", ["DontShowMicrochipStatus", "Yes"])