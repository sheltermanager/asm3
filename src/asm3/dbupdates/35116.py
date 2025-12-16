from asm3.dbupdate import execute

fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("OwnerID", dbo.type_integer, True),
    dbo.ddl_add_table_column("StartDate", dbo.type_datetime, False),
    dbo.ddl_add_table_column("EndDate", dbo.type_integer, True),
    dbo.ddl_add_table_column("Amount", dbo.type_integer, False),
    dbo.ddl_add_table_column("FromAccount", dbo.type_integer, False),
    dbo.ddl_add_table_column("ToAccount", dbo.type_integer, False),
    dbo.ddl_add_table_column("Period", dbo.type_integer, False),
    dbo.ddl_add_table_column("Weekday", dbo.type_integer, True),
    dbo.ddl_add_table_column("DayOfMonth", dbo.type_integer, True),
    dbo.ddl_add_table_column("Month", dbo.type_integer, True),
    dbo.ddl_add_table_column("Comments", dbo.type_longtext, True),
]) + dbo.ddl_audit_table_columns()
execute(dbo, dbo.ddl_add_table("regulardebit", fields) )