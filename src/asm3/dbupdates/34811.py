l = dbo.locale
# Add new fields to animalwaitinglist
add_column(dbo, "animalwaitinglist", "BreedID", dbo.type_integer)
add_column(dbo, "animalwaitinglist", "DateOfBirth", dbo.type_datetime)
add_column(dbo, "animalwaitinglist", "Sex", dbo.type_integer)
add_column(dbo, "animalwaitinglist", "Neutered", dbo.type_integer)
add_column(dbo, "animalwaitinglist", "MicrochipNumber", dbo.type_shorttext)
add_column(dbo, "animalwaitinglist", "AnimalName", dbo.type_shorttext)
add_column(dbo, "animalwaitinglist", "WaitingListRemovalID", dbo.type_integer)
add_index(dbo, "animalwaitinglist_AnimalName", "animalwaitinglist", "AnimalName")
add_index(dbo, "animalwaitinglist_MicrochipNumber", "animalwaitinglist", "MicrochipNumber")
dbo.execute_dbupdate("UPDATE animalwaitinglist SET BreedID=0, Sex=2, Neutered=0, MicrochipNumber='', AnimalName='', WaitingListRemovalID=0")
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("RemovalName", dbo.type_shorttext, False)
])
execute(dbo, dbo.ddl_add_table("lkwaitinglistremoval", fields) )
execute(dbo,"INSERT INTO lkwaitinglistremoval VALUES (1, ?)", [ _("Entered shelter", l) ])
execute(dbo,"INSERT INTO lkwaitinglistremoval VALUES (2, ?)", [ _("Owner kept", l) ])
execute(dbo,"INSERT INTO lkwaitinglistremoval VALUES (3, ?)", [ _("Owner took to another shelter", l) ])
execute(dbo,"INSERT INTO lkwaitinglistremoval VALUES (4, ?)", [ _("Unknown", l) ])