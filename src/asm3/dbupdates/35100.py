from asm3.dbupdate import execute, add_index

fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("LogTypeID", dbo.type_integer, False),
    dbo.ddl_add_table_column("LinkTypeID", dbo.type_integer, False),
    dbo.ddl_add_table_column("LinkIDs", dbo.type_longtext, False),
    dbo.ddl_add_table_column("LogMessage", dbo.type_longtext, False)
])
execute(dbo, dbo.ddl_add_table("logmulti", fields) )

add_index(dbo, "logmulti_LogTypeID", "logmulti", "LogTypeID")
add_index(dbo, "logmulti_LinkTypeID", "logmulti", "LinkTypeID")