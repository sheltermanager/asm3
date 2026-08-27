from asm3.dbupdate import execute, add_column, add_index

fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("SourceName", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("Description", dbo.type_longtext, True),
    dbo.ddl_add_table_column("IsRetired", dbo.type_integer, True)
])
execute(dbo, dbo.ddl_add_table("lkwaitinglisttype", fields) )
execute(dbo, "INSERT INTO lkwaitinglisttype (ID, SourceName) VALUES (1, ?)", [_("Animal in Event", dbo.locale),])

add_column(dbo, "animalwaitinglist", "WaitingListTypeID", dbo.type_integer)
execute(dbo, "UPDATE onlineform SET EmailSubmissionLimitDays = 1")
