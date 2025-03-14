# Add animallocation table
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("AnimalID", dbo.type_integer, False),
    dbo.ddl_add_table_column("Date", dbo.type_datetime, False),
    dbo.ddl_add_table_column("FromLocationID", dbo.type_integer, False),
    dbo.ddl_add_table_column("FromUnit", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("ToLocationID", dbo.type_integer, False),
    dbo.ddl_add_table_column("ToUnit", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("MovedBy", dbo.type_shorttext, False), # 2024-08-01 changed By to MovedBy as it breaks the update path for MySQL
    dbo.ddl_add_table_column("Description", dbo.type_shorttext, False)
])
execute(dbo, dbo.ddl_add_table("animallocation", fields) )
add_index(dbo, "animallocation_AnimalID", "animallocation", "AnimalID") 
add_index(dbo, "animallocation_FromLocationID", "animallocation", "FromLocationID") 
add_index(dbo, "animallocation_ToLocationID", "animallocation", "ToLocationID") 