# Add deletion table
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False),
    dbo.ddl_add_table_column("TableName", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("DeletedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("Date", dbo.type_datetime, False),
    dbo.ddl_add_table_column("IDList", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("RestoreSQL", dbo.type_longtext, False) ])
execute(dbo, dbo.ddl_add_table("deletion", fields) )
execute(dbo, dbo.ddl_add_index("deletion_IDTablename", "deletion", "ID,Tablename") )