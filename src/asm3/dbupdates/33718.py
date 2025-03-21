# Add TotalTimeOnShelter, TotalDaysOnShelter
add_column(dbo, "animal", "TotalDaysOnShelter", "INTEGER")
add_column(dbo, "animal", "TotalTimeOnShelter", dbo.type_shorttext)
execute(dbo,"UPDATE animal SET TotalDaysOnShelter=0, TotalTimeOnShelter=''")