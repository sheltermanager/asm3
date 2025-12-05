from asm3.dbupdate import add_column, add_index, execute
add_column(dbo, "adoption", "AdoptionSourceID", dbo.type_integer)
execute(dbo, "UPDATE adoption SET AdoptionSourceID = 0")
add_index(dbo, "adoption_AdoptionSourceID", "adoption", "AdoptionSourceID")
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("SourceName", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("Description", dbo.type_longtext, False),
    dbo.ddl_add_table_column("IsRetired", dbo.type_integer, True)
])
execute(dbo, dbo.ddl_add_table("lkadoptionsource", fields) )



dbo.execute("INSERT INTO lkadoptionsource (ID, SourceName, Description, IsRetired) VALUES (?, ?, ?, ?)", [1, _("AdoptAPet.com"), "", 0] )
dbo.execute("INSERT INTO lkadoptionsource (ID, SourceName, Description, IsRetired) VALUES (?, ?, ?, ?)", [2, _("Meta"), "", 0] )
dbo.execute("INSERT INTO lkadoptionsource (ID, SourceName, Description, IsRetired) VALUES (?, ?, ?, ?)", [3, _("Newspaper"), "", 0] )
dbo.execute("INSERT INTO lkadoptionsource (ID, SourceName, Description, IsRetired) VALUES (?, ?, ?, ?)", [4, _("PetFinder"), "", 0] )
dbo.execute("INSERT INTO lkadoptionsource (ID, SourceName, Description, IsRetired) VALUES (?, ?, ?, ?)", [5, _("Word of Mouth"), "", 0] )