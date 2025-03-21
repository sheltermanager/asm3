# Add adoption coordinator
add_column(dbo, "animal", "AdoptionCoordinatorID", "INTEGER")
add_index(dbo, "animal_AdoptionCoordinatorID", "animal", "AdoptionCoordinatorID")
execute(dbo,"UPDATE animal SET AdoptionCoordinatorID = 0")