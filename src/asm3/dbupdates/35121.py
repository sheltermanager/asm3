from asm3.dbupdate import add_column, add_index, execute
add_column(dbo, "onlineform", "LogTypeID", dbo.type_integer)
add_index(dbo, "onlineform_LogTypeID", "onlineform", "LogTypeID")
execute(dbo, "UPDATE onlineform SET LogTypeID = 0")

add_column(dbo, "onlineformincoming", "FormID", dbo.type_integer)
add_index(dbo, "onlineformincoming_FormID", "onlineformincoming", "FormID")
execute(dbo, "UPDATE onlineformincoming SET FormID = 0")
