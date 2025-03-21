# Add asm3.dbfs.URL field and index
add_column(dbo, "dbfs", "URL", dbo.type_shorttext)
add_index(dbo, "dbfs_URL", "dbfs", "URL")
execute(dbo,"UPDATE dbfs SET URL = 'base64:'")