# Add ReturnedByOwnerID
add_column(dbo, "adoption", "ReturnedByOwnerID", dbo.type_integer)
add_index(dbo, "adoption_ReturnedByOwnerID", "adoption", "ReturnedByOwnerID")
execute(dbo,"UPDATE adoption SET ReturnedByOwnerID = 0")