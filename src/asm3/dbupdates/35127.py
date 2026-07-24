from asm3.dbupdate import execute, add_index

fields = ",".join([
    dbo.ddl_add_table_column("AnimalID", dbo.type_integer, False),
    dbo.ddl_add_table_column("MonthMidPoint", dbo.type_datetime, False),
    dbo.ddl_add_table_column("Month", dbo.type_integer, False),
    dbo.ddl_add_table_column("Year", dbo.type_integer, False),
    dbo.ddl_add_table_column("DaysOnShelter", dbo.type_integer, False)
]) + dbo.ddl_audit_table_columns()
execute(dbo, dbo.ddl_add_table("animalfiguresonshelter", fields) )

add_index(dbo, "animalfiguresonshelter_AnimalID", "animalfiguresonshelter", "AnimalID")
