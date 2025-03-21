# Add exclude from bulk email field to owner
add_column(dbo, "owner", "ExcludeFromBulkEmail", "INTEGER")
execute(dbo,"UPDATE owner SET ExcludeFromBulkEmail = 0")