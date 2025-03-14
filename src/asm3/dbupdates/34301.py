# Add onlineformfield.SpeciesID
add_column(dbo, "onlineformfield", "SpeciesID", dbo.type_integer)
execute(dbo,"UPDATE onlineformfield SET SpeciesID = -1")