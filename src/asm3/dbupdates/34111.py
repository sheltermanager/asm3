# Add animalvaccination.GivenBy
add_column(dbo, "animalvaccination", "GivenBy", dbo.type_shorttext)
add_index(dbo, "animalvaccination_GivenBy", "animalvaccination", "GivenBy")
execute(dbo,"UPDATE animalvaccination SET GivenBy = LastChangedBy WHERE DateOfVaccination Is Not Null")