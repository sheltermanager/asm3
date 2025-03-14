add_column(dbo, "onlineform", "RetainFor", dbo.type_integer)
execute(dbo,"UPDATE onlineform SET RetainFor=0")