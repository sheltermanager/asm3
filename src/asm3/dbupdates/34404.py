# Add animal.OwnerID
add_column(dbo, "animal", "OwnerID", dbo.type_integer)
add_index(dbo, "animal_OwnerID", "animal", "OwnerID")
# Set currentownerid for non-shelter animals
execute(dbo,"UPDATE animal SET OwnerID = OriginalOwnerID WHERE NonShelterAnimal=1")
# Set currentownerid for animals with an active exit movement
execute(dbo,"UPDATE animal SET OwnerID = " \
    "(SELECT OwnerID FROM adoption WHERE ID = animal.ActiveMovementID) " \
    "WHERE Archived = 1 AND ActiveMovementType IN (1, 3, 5)")
# Remove nulls
execute(dbo,"UPDATE animal SET OwnerID = 0 WHERE OwnerID Is Null")