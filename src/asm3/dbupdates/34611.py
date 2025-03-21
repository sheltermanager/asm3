# add eventanimal.Comments
add_column(dbo, "eventanimal", "Comments", dbo.type_longtext)
execute(dbo,dbo.ddl_drop_notnull("eventanimal", "ArrivalDate", dbo.type_datetime))