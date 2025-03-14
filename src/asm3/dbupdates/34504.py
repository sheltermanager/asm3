# add onlineform.AutoProcess
add_column(dbo, "onlineform", "AutoProcess", dbo.type_integer)
execute(dbo,"UPDATE onlineform SET AutoProcess=0")
