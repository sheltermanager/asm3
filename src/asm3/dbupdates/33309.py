# Create animalfiguresmonthlyasilomar table to be updated each night
# for US shelters with the option on
sql = "CREATE TABLE animalfiguresmonthlyasilomar ( ID INTEGER NOT NULL, " \
    "Month INTEGER NOT NULL, " \
    "Year INTEGER NOT NULL, " \
    "OrderIndex INTEGER NOT NULL, " \
    "Code %s NOT NULL, " \
    "Heading %s NOT NULL, " \
    "Bold INTEGER NOT NULL, " \
    "Cat INTEGER NOT NULL, " \
    "Dog INTEGER NOT NULL, " \
    "Total INTEGER NOT NULL)" % (dbo.type_shorttext, dbo.type_shorttext)
execute(dbo,sql)
add_index(dbo, "animalfiguresmonthlyasilomar_ID", "animalfiguresmonthlyasilomar", "ID", True)
add_index(dbo, "animalfiguresmonthlyasilomar_Year", "animalfiguresmonthlyasilomar", "Year")
add_index(dbo, "animalfiguresmonthlyasilomar_Month", "animalfiguresmonthlyasilomar", "Month")