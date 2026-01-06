# Add the animalrole table
fields = ",".join([
    dbo.ddl_add_table_column("AnimalID", dbo.type_integer, False),
    dbo.ddl_add_table_column("RoleID", dbo.type_integer, False),
    dbo.ddl_add_table_column("CanView", dbo.type_integer, False),
    dbo.ddl_add_table_column("CanEdit", dbo.type_integer, False)
])
execute(dbo, dbo.ddl_add_table("animalrole", fields) )
add_index(dbo, "animalrole_AnimalIDRoleID", "animalrole", "AnimalID,RoleID", unique=True)