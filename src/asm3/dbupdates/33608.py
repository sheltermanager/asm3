# Add pickuplocationid to incidents
add_column(dbo, "animalcontrol", "PickupLocationID", "INTEGER")
add_index(dbo, "animalcontrol_PickupLocationID", "animalcontrol", "PickupLocationID")
execute(dbo,"UPDATE animalcontrol SET PickupLocationID = 0")