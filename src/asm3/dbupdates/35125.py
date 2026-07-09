from asm3.dbupdate import add_column, execute

add_column(dbo, "onlineform", "FormRenderer", dbo.type_integer)
execute(dbo, "UPDATE onlineform SET FormRenderer = 0")
