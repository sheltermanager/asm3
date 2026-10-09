from asm3.dbupdate import add_column, add_index

add_column(dbo, "animal", "Weight1", dbo.type_float)
add_column(dbo, "animal", "Weight2", dbo.type_float)

add_index(dbo, "animal_Weight1", "animal", "Weight1")
add_index(dbo, "animal_Weight2", "animal", "Weight2")