# Add animal.PickupAddress, animalvaccination.AdministeringVetID and animalmedicaltreatment.AdministeringVetID
add_column(dbo, "animal", "PickupAddress", dbo.type_shorttext)
add_column(dbo, "animalmedicaltreatment", "AdministeringVetID", "INTEGER")
add_column(dbo, "animalvaccination", "AdministeringVetID", "INTEGER")
add_index(dbo, "animal_PickupAddress", "animal", "PickupAddress")
add_index(dbo, "animalmedicaltreatment_AdministeringVetID", "animalmedicaltreatment", "AdministeringVetID")
add_index(dbo, "animalvaccination_AdministeringVetID", "animalvaccination", "AdministeringVetID")
execute(dbo,"UPDATE animal SET PickupAddress = ''")
execute(dbo,"UPDATE animalmedicaltreatment SET AdministeringVetID = 0")
execute(dbo,"UPDATE animalvaccination SET AdministeringVetID = 0")