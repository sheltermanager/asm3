# Add NeuteredByVetID
add_column(dbo, "animal", "NeuteredByVetID", dbo.type_integer)
add_index(dbo, "animal_NeuteredByVetID", "animal", "NeuteredByVetID")
execute(dbo,"UPDATE animal SET NeuteredByVetID = 0")