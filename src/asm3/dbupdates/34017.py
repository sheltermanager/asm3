# Add extra microchip fields
add_column(dbo, "animal", "Identichip2Number", dbo.type_shorttext)
add_column(dbo, "animal", "Identichip2Date", dbo.type_datetime)
add_index(dbo, "animal_Identichip2Number", "animal", "Identichip2Number")