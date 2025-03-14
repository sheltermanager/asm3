# add animalentry table
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("AnimalID", dbo.type_integer, False),
    dbo.ddl_add_table_column("ShelterCode", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("ShortCode", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("EntryDate", dbo.type_datetime, False),
    dbo.ddl_add_table_column("EntryReasonID", dbo.type_integer, False),
    dbo.ddl_add_table_column("AdoptionCoordinatorID", dbo.type_integer, True),
    dbo.ddl_add_table_column("BroughtInByOwnerID", dbo.type_integer, True),
    dbo.ddl_add_table_column("OriginalOwnerID", dbo.type_integer, True),
    dbo.ddl_add_table_column("AsilomarIntakeCategory", dbo.type_integer, True),
    dbo.ddl_add_table_column("JurisdictionID", dbo.type_integer, True),
    dbo.ddl_add_table_column("IsTransfer", dbo.type_integer, False),
    dbo.ddl_add_table_column("AsilomarIsTransferExternal", dbo.type_integer, True),
    dbo.ddl_add_table_column("HoldUntilDate", dbo.type_datetime, True),
    dbo.ddl_add_table_column("IsPickup", dbo.type_integer, False),
    dbo.ddl_add_table_column("PickupLocationID", dbo.type_integer, True),
    dbo.ddl_add_table_column("PickupAddress", dbo.type_shorttext, True),
    dbo.ddl_add_table_column("ReasonNO", dbo.type_longtext, True),
    dbo.ddl_add_table_column("ReasonForEntry", dbo.type_longtext, True),
    dbo.ddl_add_table_column("RecordVersion", dbo.type_integer, False),
    dbo.ddl_add_table_column("CreatedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("CreatedDate", dbo.type_datetime, False),
    dbo.ddl_add_table_column("LastChangedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("LastChangedDate", dbo.type_datetime, False)
])
execute(dbo, dbo.ddl_add_table("animalentry", fields) )
execute(dbo, dbo.ddl_add_index("animalentry_AnimalID", "animalentry", "AnimalID") )