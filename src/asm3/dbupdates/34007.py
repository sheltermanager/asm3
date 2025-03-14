# Add missing indexes to DiedOffShelter / NonShelterAnimal
add_index(dbo, "animal_DiedOffShelter", "animal", "DiedOffShelter")
add_index(dbo, "animal_NonShelterAnimal", "animal", "NonShelterAnimal")