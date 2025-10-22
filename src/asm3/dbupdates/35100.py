from asm3.dbupdate import execute, add_index

fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("Date", dbo.type_datetime, False),
    dbo.ddl_add_table_column("LogTypeID", dbo.type_integer, False),
    dbo.ddl_add_table_column("LinkType", dbo.type_integer, False),
    dbo.ddl_add_table_column("LinkIDs", dbo.type_longtext, False),
    dbo.ddl_add_table_column("Comments", dbo.type_longtext, False)
]) + dbo.ddl_audit_table_columns()
execute(dbo, dbo.ddl_add_table("logmulti", fields) )

add_index(dbo, "logmulti_LogTypeID", "logmulti", "LogTypeID")
add_index(dbo, "logmulti_LinkType", "logmulti", "LinkType")
