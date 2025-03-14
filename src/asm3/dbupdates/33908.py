# Add site table
sql = "CREATE TABLE site (ID INTEGER NOT NULL PRIMARY KEY, " \
    "SiteName %s NOT NULL)" % dbo.type_shorttext
execute(dbo,sql)
execute(dbo,"INSERT INTO site VALUES (1, 'main')")
# Add internallocation.SiteID
add_column(dbo, "internallocation", "SiteID", "INTEGER")
execute(dbo,"UPDATE internallocation SET SiteID = 1")
# Add users.SiteID
add_column(dbo, "users", "SiteID", "INTEGER")
execute(dbo,"UPDATE users SET SiteID = 0")