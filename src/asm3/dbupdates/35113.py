from asm3.dbupdate import add_column, add_index, execute

add_column(dbo, "accountstrx", "OwnerID", dbo.type_integer)
execute(dbo, "UPDATE accountstrx SET OwnerID = 0")
add_index(dbo, "accountstrx_OwnerID", "accountstrx", "OwnerID")