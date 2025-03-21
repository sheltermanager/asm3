# Add animal.Adoptable
add_column(dbo, "animal", "Adoptable", dbo.type_integer)
add_index(dbo, "animal_Adoptable", "animal", "Adoptable")
dbo.execute_dbupdate("UPDATE animal SET Adoptable = 0")
# Add onlineform.EmailCoordinator
add_column(dbo, "onlineform", "EmailCoordinator", dbo.type_integer)
execute(dbo,"UPDATE onlineform SET EmailCoordinator = 0")