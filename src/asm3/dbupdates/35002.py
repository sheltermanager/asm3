from asm3.dbupdate import execute, add_column

# Add the new goodwith fields to looking for
add_column(dbo, "animalcontrol", "FollowupACO", dbo.type_shorttext)
add_column(dbo, "animalcontrol", "FollowupACO2", dbo.type_shorttext)
add_column(dbo, "animalcontrol", "FollowupACO3", dbo.type_shorttext)
execute(dbo, "UPDATE animalcontrol SET FollowupACO='', FollowupACO2='', FollowupACO3=''")

