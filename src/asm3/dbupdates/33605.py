# Add accounts archived flag
add_column(dbo, "accounts", "Archived", "INTEGER")
add_index(dbo, "accounts_Archived", "accounts", "ARCHIVED")
execute(dbo,"UPDATE accounts SET Archived = 0")