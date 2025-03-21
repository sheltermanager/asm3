# Add animal links table
fields = ",".join([
    dbo.ddl_add_table_column("AnimalControlID", dbo.type_integer, False),
    dbo.ddl_add_table_column("AnimalID", dbo.type_integer, False)
])
execute(dbo, dbo.ddl_add_table("animalcontrolanimal", fields) )
execute(dbo, dbo.ddl_add_index("animalcontrolanimal_AnimalControlIDAnimalID", "animalcontrolanimal", "AnimalControlID,AnimalID", True) )
# Copy the existing links from animalcontrol.AnimalID
for ac in dbo.query("SELECT ID, AnimalID FROM animalcontrol WHERE AnimalID Is Not Null AND AnimalID <> 0"):
    dbo.execute_dbupdate("INSERT INTO animalcontrolanimal (AnimalControlID, AnimalID) VALUES (%d, %d)" % (ac["ID"], ac["ANIMALID"]))
# Remove the animalid field from animalcontrol
if column_exists(dbo, "animalcontrol", "AnimalID"):
    drop_index(dbo, "animalcontrol_AnimalID", "animalcontrol")
    drop_column(dbo, "animalcontrol", "AnimalID")