from asm3.dbupdate import execute, add_index

fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("Date", dbo.type_datetime, False),
    dbo.ddl_add_table_column("LogTypeID", dbo.type_integer, False),
    dbo.ddl_add_table_column("LinkType", dbo.type_integer, False),
    dbo.ddl_add_table_column("LinkIDs", dbo.type_longtext, False),
    dbo.ddl_add_table_column("Comments", dbo.type_longtext, False),
    dbo.ddl_add_table_column("RecordVersion", dbo.type_integer, True),
    dbo.ddl_add_table_column("CreatedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("CreatedDate", dbo.type_datetime, False),
    dbo.ddl_add_table_column("LastChangedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("LastChangedDate", dbo.type_datetime, False)
])
execute(dbo, dbo.ddl_add_table("logmulti", fields) )

add_index(dbo, "logmulti_LogTypeID", "logmulti", "LogTypeID")
add_index(dbo, "logmulti_LinkType", "logmulti", "LinkType")