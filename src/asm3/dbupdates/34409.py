# Add animalvaccination.RabiesTag
add_column(dbo, "animalvaccination", "RabiesTag", dbo.type_shorttext)
add_index(dbo, "animalvaccination_RabiesTag", "animalvaccination", "RabiesTag")
execute(dbo,"UPDATE animalvaccination SET RabiesTag='' WHERE RabiesTag Is Null")