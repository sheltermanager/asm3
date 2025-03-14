# Add missing LostArea and FoundArea fields due to broken schema
if not column_exists(dbo, "animallostfoundmatch", "LostArea"):
    add_column(dbo, "animallostfoundmatch", "LostArea", dbo.type_shorttext)
if not column_exists(dbo, "animallostfoundmatch", "FoundArea"):
    add_column(dbo, "animallostfoundmatch", "FoundArea", dbo.type_shorttext)