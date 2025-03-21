# Add a DisplayIndex and Preview field to onlineformincoming
add_column(dbo, "onlineformincoming", "DisplayIndex", "INTEGER")
add_column(dbo, "onlineformincoming", "Preview", dbo.type_longtext)
