from asm3.dbupdate import add_column, add_index

add_column(dbo, "animal", "IdentichipStatus", dbo.type_integer)
add_column(dbo, "animal", "Identichip2Status", dbo.type_integer)

add_index(dbo, "animal_IdentichipStatus", "animal", "IdentichipStatus")
add_index(dbo, "animal_Identichip2Status", "animal", "Identichip2Status")