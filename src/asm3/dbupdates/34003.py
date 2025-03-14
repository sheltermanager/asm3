# Add indexes to animal and owner created for find animal/person
add_index(dbo, "animal_CreatedBy", "animal", "CreatedBy")
add_index(dbo, "animal_CreatedDate", "animal", "CreatedDate")
add_index(dbo, "owner_CreatedBy", "owner", "CreatedBy")
add_index(dbo, "owner_CreatedDate", "owner", "CreatedDate")