fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("AnimalID", dbo.type_integer, False),
    dbo.ddl_add_table_column("OwnerID", dbo.type_integer, True),
    dbo.ddl_add_table_column("InDateTime", dbo.type_datetime, False),
    dbo.ddl_add_table_column("OutDateTime", dbo.type_datetime, False),
    dbo.ddl_add_table_column("Days", dbo.type_integer, True),
    dbo.ddl_add_table_column("DailyFee", dbo.type_integer, True),
    dbo.ddl_add_table_column("ShelterLocation", dbo.type_integer, False),
    dbo.ddl_add_table_column("ShelterLocationUnit", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("Comments", dbo.type_longtext, True),
    dbo.ddl_add_table_column("RecordVersion", dbo.type_integer, False),
    dbo.ddl_add_table_column("CreatedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("CreatedDate", dbo.type_datetime, False),
    dbo.ddl_add_table_column("LastChangedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("LastChangedDate", dbo.type_datetime, False)
])
execute(dbo, dbo.ddl_add_table("animalboarding", fields) )
execute(dbo, dbo.ddl_add_index("animalboarding_AnimalID", "animalboarding", "AnimalID") )
execute(dbo, dbo.ddl_add_index("animalboarding_OwnerID", "animalboarding", "OwnerID") )
execute(dbo, dbo.ddl_add_index("animalboarding_InDateTime", "animalboarding", "InDateTime") )
execute(dbo, dbo.ddl_add_index("animalboarding_OutDateTime", "animalboarding", "OutDateTime") )