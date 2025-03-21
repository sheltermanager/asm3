# Add users.DisableLogin
add_column(dbo, "users", "DisableLogin", "INTEGER")
execute(dbo,"UPDATE users SET DisableLogin = 0")