# Create animalfiguresannual table to be updated each night
sql = "CREATE TABLE animalfiguresannual ( ID INTEGER NOT NULL, " \
    "Year INTEGER NOT NULL, " \
    "OrderIndex INTEGER NOT NULL, " \
    "Code %s NOT NULL, " \
    "AnimalTypeID INTEGER NOT NULL, " \
    "SpeciesID INTEGER NOT NULL, " \
    "GroupHeading %s NOT NULL, " \
    "Heading %s NOT NULL, " \
    "Bold INTEGER NOT NULL, " \
    "M1 INTEGER NOT NULL, " \
    "M2 INTEGER NOT NULL, " \
    "M3 INTEGER NOT NULL, " \
    "M4 INTEGER NOT NULL, " \
    "M5 INTEGER NOT NULL, " \
    "M6 INTEGER NOT NULL, " \
    "M7 INTEGER NOT NULL, " \
    "M8 INTEGER NOT NULL, " \
    "M9 INTEGER NOT NULL, " \
    "M10 INTEGER NOT NULL, " \
    "M11 INTEGER NOT NULL, " \
    "M12 INTEGER NOT NULL, " \
    "Total INTEGER NOT NULL)" % (dbo.type_shorttext, dbo.type_shorttext, dbo.type_shorttext)
execute(dbo,sql)
add_index(dbo, "animalfiguresannual_ID", "animalfiguresannual", "ID", True)
add_index(dbo, "animalfiguresannual_AnimalTypeID", "animalfiguresannual", "AnimalTypeID")
add_index(dbo, "animalfiguresannual_SpeciesID", "animalfiguresannual", "SpeciesID")
add_index(dbo, "animalfiguresannual_Year", "animalfiguresannual", "Year")