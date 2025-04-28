from asm3.dbupdate import execute, add_column, add_index

dbo = dbo
l = dbo.locale

add_column(dbo, "animalmedical", "MedicalTypeID", dbo.type_integer)
add_index(dbo, "animalmedical_MedicalTypeID", "animalmedical", "MedicalTypeID")

add_column(dbo, "medicalprofile", "MedicalTypeID", dbo.type_integer)
add_index(dbo, "medicalprofile_MedicalTypeID", "medicalprofile", "MedicalTypeID")

#execute(dbo, "UPDATE animalmedical SET MedicalTypeID = 1")

# Add the lkmedicaltype table
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("MedicalTypeName", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("Description", dbo.type_longtext, True),
    dbo.ddl_add_table_column("ForceSingleUse", dbo.type_integer, False),
    dbo.ddl_add_table_column("IsRetired", dbo.type_integer, False)
])
execute(dbo, dbo.ddl_add_table("lksmedicaltype", fields) )

execute(dbo, "INSERT INTO lksmedicaltype (ID, MedicalTypeName, Description, ForceSingleUse, IsRetired) VALUES (?, ?, ?, ?, ?)", [ 1, _("Allergy treatment", l), "", 0, 0 ])
execute(dbo, "INSERT INTO lksmedicaltype (ID, MedicalTypeName, Description, ForceSingleUse, IsRetired) VALUES (?, ?, ?, ?, ?)", [ 2, _("Examination", l), "", 1, 0 ])
execute(dbo, "INSERT INTO lksmedicaltype (ID, MedicalTypeName, Description, ForceSingleUse, IsRetired) VALUES (?, ?, ?, ?, ?)", [ 3, _("Flea treatment", l), "", 0, 0 ])
execute(dbo, "INSERT INTO lksmedicaltype (ID, MedicalTypeName, Description, ForceSingleUse, IsRetired) VALUES (?, ?, ?, ?, ?)", [ 4, _("Pain relief", l), "", 0, 0 ])
execute(dbo, "INSERT INTO lksmedicaltype (ID, MedicalTypeName, Description, ForceSingleUse, IsRetired) VALUES (?, ?, ?, ?, ?)", [ 5, _("Skin treatment", l), "", 0, 0 ])
execute(dbo, "INSERT INTO lksmedicaltype (ID, MedicalTypeName, Description, ForceSingleUse, IsRetired) VALUES (?, ?, ?, ?, ?)", [ 6, _("Surgery", l), "", 1, 0 ])
execute(dbo, "INSERT INTO lksmedicaltype (ID, MedicalTypeName, Description, ForceSingleUse, IsRetired) VALUES (?, ?, ?, ?, ?)", [ 7, _("Wormer", l), "", 0, 0 ])

#execute(dbo, "INSERT INTO configuration (ItemName, ItemValue) VALUES (?, ?)", ["StockDefaultProductTypeID", "1"])