from asm3.dbupdate import execute

fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("StartDate", dbo.type_datetime, False),
    dbo.ddl_add_table_column("EndDate", dbo.type_integer, True),
    dbo.ddl_add_table_column("Period", dbo.type_integer, False)
]) + dbo.ddl_audit_table_columns()
execute(dbo, dbo.ddl_add_table("regulardebit", fields) )