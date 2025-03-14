# Add an index on additional.linkid for performance
add_index(dbo, "additional_LinkID", "additional", "LinkID")