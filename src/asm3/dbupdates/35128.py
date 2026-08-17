from asm3.dbupdate import execute, add_index

fields = ",".join([
    dbo.ddl_add_table_column("OnlineFormID", dbo.type_integer, False),
    dbo.ddl_add_table_column("RoleID", dbo.type_integer, False),
    dbo.ddl_add_table_column("CanView", dbo.type_integer, False),
    dbo.ddl_add_table_column("CanEdit", dbo.type_integer, True)
])
execute(dbo, dbo.ddl_add_table("onlineformrole", fields))

add_index(dbo, "onlineformrole_OnlineFormID", "onlineformrole", "OnlineFormID")
add_index(dbo, "onlineformrole_RoleID", "onlineformrole", "RoleID")
