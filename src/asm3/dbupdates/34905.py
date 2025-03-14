# Add the ownerrole table
fields = ",".join([
    dbo.ddl_add_table_column("OwnerID", dbo.type_integer, False),
    dbo.ddl_add_table_column("RoleID", dbo.type_integer, False),
    dbo.ddl_add_table_column("CanView", dbo.type_integer, False),
    dbo.ddl_add_table_column("CanEdit", dbo.type_integer, False)
])
execute(dbo, dbo.ddl_add_table("ownerrole", fields) )
add_index(dbo, "ownerrole_OwnerIDRoleID", "ownerrole", "OwnerID,RoleID", unique=True)