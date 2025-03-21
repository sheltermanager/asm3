# Create animalfiguresasilomar table to be updated each night
# for US shelters with the option on
sql = "CREATE TABLE animalfiguresasilomar ( ID INTEGER NOT NULL, " \
    "Year INTEGER NOT NULL, " \
    "OrderIndex INTEGER NOT NULL, " \
    "Code %s NOT NULL, " \
    "Heading %s NOT NULL, " \
    "Bold INTEGER NOT NULL, " \
    "Cat INTEGER NOT NULL, " \
    "Dog INTEGER NOT NULL, " \
    "Total INTEGER NOT NULL)" % (dbo.type_shorttext, dbo.type_shorttext)
execute(dbo,sql)
add_index(dbo, "animalfiguresasilomar_ID", "animalfiguresasilomar", "ID", True)
add_index(dbo, "animalfiguresasilomar_Year", "animalfiguresasilomar", "Year")