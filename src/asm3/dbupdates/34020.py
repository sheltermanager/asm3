# Add IsNotForRegistration
add_column(dbo, "animal", "IsNotForRegistration", dbo.type_integer)
execute(dbo,"UPDATE animal SET IsNotForRegistration = 0")