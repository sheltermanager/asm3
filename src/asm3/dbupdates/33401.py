# Add OwnerType and IsDeceased flags to owner
add_column(dbo, "owner", "OwnerType", "INTEGER")
add_column(dbo, "owner", "IsDeceased", "INTEGER")
execute(dbo,"UPDATE owner SET OwnerType = 1")
execute(dbo,"UPDATE owner SET OwnerType = 2 WHERE IsShelter = 1")
execute(dbo,"UPDATE owner SET IsDeceased = 0")