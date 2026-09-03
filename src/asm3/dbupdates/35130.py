# Add permission to change animal roles where permission to change animals is granted
sql = f"UPDATE role SET SecurityMap = {dbo.sql_concat(("SecurityMap", "'car *'"))} WHERE {dbo.sql_concat(("'*'", "SecurityMap"))} LIKE '%*ca %'"
dbo.execute(sql)


# Add permission to change person roles where permission to change people is granted
sql = f"UPDATE role SET SecurityMap = {dbo.sql_concat(("SecurityMap", "'cor *'"))} WHERE {dbo.sql_concat(("'*'", "SecurityMap"))} LIKE '%*co %'"
dbo.execute(sql)

# Add permission to change incident roles where permission to change incidents is granted
sql = f"UPDATE role SET SecurityMap = {dbo.sql_concat(("SecurityMap", "'cacir *'"))} WHERE {dbo.sql_concat(("'*'", "SecurityMap"))} LIKE '%*caci %'"
dbo.execute(sql)
