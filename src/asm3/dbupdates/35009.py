from asm3.dbupdate import execute, add_column, add_index

add_column(dbo, "onlineform", "InternalUse", dbo.type_integer)
add_index(dbo, "onlineform_InternalUse", "onlineform", "InternalUse")
execute(dbo, "UPDATE onlineform SET InternalUse = 0")
