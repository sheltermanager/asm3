from asm3.dbupdate import add_column, add_index, execute

add_column(dbo, "onlineform", "SubmitterReplyAddress", dbo.type_longtext)
execute(dbo, "UPDATE onlineform SET SubmitterReplyAddress = ''")
