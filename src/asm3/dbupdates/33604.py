# Add weight field
add_column(dbo, "animal", "Weight", dbo.type_float)
add_index(dbo, "animal_Weight", "animal", "Weight")
# Add followupcomplete fields to animalcontrol
add_column(dbo, "animalcontrol", "FollowupComplete", "INTEGER")
add_column(dbo, "animalcontrol", "FollowupComplete2", "INTEGER")
add_column(dbo, "animalcontrol", "FollowupComplete3", "INTEGER")
add_index(dbo, "animalcontrol_FollowupComplete", "animalcontrol", "FollowupComplete")
add_index(dbo, "animalcontrol_FollowupComplete2", "animalcontrol", "FollowupComplete2")
add_index(dbo, "animalcontrol_FollowupComplete3", "animalcontrol", "FollowupComplete3")
execute(dbo,"UPDATE animalcontrol SET FollowupComplete = 0, FollowupComplete2 = 0, FollowupComplete3 = 0")
execute(dbo,"UPDATE animal SET Weight = 0")