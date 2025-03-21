# Add extra vaccination fields and some missing indexes
add_column(dbo, "animalvaccination", "DateExpires", dbo.type_datetime)
add_column(dbo, "animalvaccination", "BatchNumber", dbo.type_shorttext)
add_column(dbo, "animalvaccination", "Manufacturer", dbo.type_shorttext)
add_index(dbo, "animalvaccination_DateExpires", "animalvaccination", "DateExpires")
add_index(dbo, "animalvaccination_DateRequired", "animalvaccination", "DateRequired")
add_index(dbo, "animalvaccination_Manufacturer", "animalvaccination", "Manufacturer")
add_index(dbo, "animaltest_DateRequired", "animaltest", "DateRequired")