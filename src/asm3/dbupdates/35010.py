from asm3.dbupdate import add_column, execute

add_column(dbo, "additionalfield", "SpeciesIDs", dbo.type_shorttext)
execute(dbo, "UPDATE additionalfield SET SpeciesIDs = ''")

