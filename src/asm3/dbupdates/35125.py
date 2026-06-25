from asm3.dbupdate import add_column, execute

add_column(dbo, "onlineform", "BootstrapStyle", dbo.type_integer)
execute(dbo, "UPDATE onlineform SET BootstrapStyle = 0")
