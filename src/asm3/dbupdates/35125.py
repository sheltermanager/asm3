from asm3.dbupdate import add_column, execute

add_column(dbo, "onlineform", "Renderer", dbo.type_integer)
execute(dbo, "UPDATE onlineform SET Renderer = 0")
