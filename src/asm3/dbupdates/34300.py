# Add animal.ExtraIDs
add_column(dbo, "animal", "ExtraIDs", dbo.type_shorttext)
add_index(dbo, "animal_ExtraIDs", "animal", "ExtraIDs")
execute(dbo,"UPDATE animal SET ExtraIDs = ''")