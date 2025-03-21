# Add ShelterLocationUnit
add_column(dbo, "animal", "ShelterLocationUnit", dbo.type_shorttext)
execute(dbo,"UPDATE animal SET ShelterLocationUnit = ''")