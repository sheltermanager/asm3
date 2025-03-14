# Create animalfigures table to be updated each night
sql = "CREATE TABLE animalfigures ( ID INTEGER NOT NULL, " \
    "Month INTEGER NOT NULL, " \
    "Year INTEGER NOT NULL, " \
    "OrderIndex INTEGER NOT NULL, " \
    "Code %s NOT NULL, " \
    "AnimalTypeID INTEGER NOT NULL, " \
    "SpeciesID INTEGER NOT NULL, " \
    "MaxDaysInMonth INTEGER NOT NULL, " \
    "Heading %s NOT NULL, " \
    "Bold INTEGER NOT NULL, " \
    "D1 INTEGER NOT NULL, " \
    "D2 INTEGER NOT NULL, " \
    "D3 INTEGER NOT NULL, " \
    "D4 INTEGER NOT NULL, " \
    "D5 INTEGER NOT NULL, " \
    "D6 INTEGER NOT NULL, " \
    "D7 INTEGER NOT NULL, " \
    "D8 INTEGER NOT NULL, " \
    "D9 INTEGER NOT NULL, " \
    "D10 INTEGER NOT NULL, " \
    "D11 INTEGER NOT NULL, " \
    "D12 INTEGER NOT NULL, " \
    "D13 INTEGER NOT NULL, " \
    "D14 INTEGER NOT NULL, " \
    "D15 INTEGER NOT NULL, " \
    "D16 INTEGER NOT NULL, " \
    "D17 INTEGER NOT NULL, " \
    "D18 INTEGER NOT NULL, " \
    "D19 INTEGER NOT NULL, " \
    "D20 INTEGER NOT NULL, " \
    "D21 INTEGER NOT NULL, " \
    "D22 INTEGER NOT NULL, " \
    "D23 INTEGER NOT NULL, " \
    "D24 INTEGER NOT NULL, " \
    "D25 INTEGER NOT NULL, " \
    "D26 INTEGER NOT NULL, " \
    "D27 INTEGER NOT NULL, " \
    "D28 INTEGER NOT NULL, " \
    "D29 INTEGER NOT NULL, " \
    "D30 INTEGER NOT NULL, " \
    "D31 INTEGER NOT NULL, " \
    "AVG %s NOT NULL)" % (dbo.type_shorttext, dbo.type_shorttext, dbo.type_float)
execute(dbo,sql)
execute(dbo,"CREATE UNIQUE INDEX animalfigures_ID ON animalfigures(ID)")
add_index(dbo, "animalfigures_AnimalTypeID", "animalfigures", "AnimalTypeID")
add_index(dbo, "animalfigures_SpeciesID", "animalfigures", "SpeciesID")
add_index(dbo, "animalfigures_Month", "animalfigures", "Month")
add_index(dbo, "animalfigures_Year", "animalfigures", "Year")
