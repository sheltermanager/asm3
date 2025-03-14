# Add IsHold and IsQuarantine fields
add_column(dbo, "animal", "IsHold", "INTEGER")
add_column(dbo, "animal", "IsQuarantine", "INTEGER")
execute(dbo,"UPDATE animal SET IsHold = 0, IsQuarantine = 0")