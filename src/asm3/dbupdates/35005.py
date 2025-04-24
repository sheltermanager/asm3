from asm3.dbupdate import execute, add_column

add_column(dbo, "animalmedical", "MedicalTypeID", dbo.type_integer)
add_index(dbo, "animalmedical_MedicalTypeID", "animalmedical", "MedicalTypeID")
#execute(dbo, "UPDATE animalmedical SET MedicalTypeID = 1")

# Add the lkmedicaltype table
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("MedicalTypeName", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("Description", dbo.type_longtext, True),
    dbo.ddl_add_table_column("IsRetired", dbo.type_integer, False)
])
execute(dbo, dbo.ddl_add_table("lkmedicaltype", fields) )

execute(dbo, "INSERT INTO lkmedicaltype (ID, MedicaclTypeName, Description, IsRetired) VALUES (?, ?, ?, ?)", [ 1, _("General", l), "", 0 ])

#execute(dbo, "INSERT INTO configuration (ItemName, ItemValue) VALUES (?, ?)", ["StockDefaultProductTypeID", "1"])