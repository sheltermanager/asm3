from asm3.dbupdate import add_column, execute

add_column(dbo, "onlineform", "SetMediaFlags", dbo.type_shorttext)
add_column(dbo, "onlineformincoming", "MediaFlags", dbo.type_shorttext)
execute(dbo, "UPDATE onlineform SET SetMediaFlags = ''")
execute(dbo, "UPDATE onlineformincoming SET MediaFlags = ''")