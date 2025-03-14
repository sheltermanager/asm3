# Create animal flags table
sql = "CREATE TABLE lkanimalflags ( ID INTEGER NOT NULL, " \
    "Flag %s NOT NULL)" % dbo.type_shorttext
execute(dbo,sql)
# Add additionalflags field to animal
add_column(dbo, "animal", "AdditionalFlags", dbo.type_longtext)
# Add IsCourtesy to animal
add_column(dbo, "animal", "IsCourtesy", "INTEGER")
execute(dbo,"UPDATE animal SET IsCourtesy=0, AdditionalFlags=''")