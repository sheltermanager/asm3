l = dbo.locale

# Add IsSupplier column to owner table
add_column(dbo, "owner", "IsSupplier", dbo.type_integer)
add_index(dbo, "owner_IsSupplier", "owner", "IsSupplier")
execute(dbo, "UPDATE owner SET IsSupplier=0")

# Add the product table
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("ProductName", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("Description", dbo.type_longtext, False),
    dbo.ddl_add_table_column("ProductTypeID", dbo.type_integer, False),
    dbo.ddl_add_table_column("SupplierID", dbo.type_integer, False),
    dbo.ddl_add_table_column("UnitTypeID", dbo.type_integer, False),
    dbo.ddl_add_table_column("CustomUnit", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("PurchaseUnitTypeID", dbo.type_integer, False),
    dbo.ddl_add_table_column("CustomPurchaseUnit", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("CostPrice", dbo.type_integer, False),
    dbo.ddl_add_table_column("RetailPrice", dbo.type_integer, False),
    dbo.ddl_add_table_column("UnitRatio", dbo.type_integer, False),
    dbo.ddl_add_table_column("TaxRateID", dbo.type_integer, False),
    dbo.ddl_add_table_column("Barcode", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("PLU", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("RecentBatchNo", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("RecentExpiry", dbo.type_datetime),
    dbo.ddl_add_table_column("GlobalMinimum", dbo.type_integer),
    dbo.ddl_add_table_column("RecordVersion", dbo.type_integer, True),
    dbo.ddl_add_table_column("CreatedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("CreatedDate", dbo.type_datetime, False),
    dbo.ddl_add_table_column("LastChangedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("LastChangedDate", dbo.type_datetime, False),
    dbo.ddl_add_table_column("IsRetired", dbo.type_integer, False)
])

execute(dbo, dbo.ddl_add_table("product", fields) )
add_index(dbo, "product_SupplierID", "product", "SupplierID")
add_index(dbo, "product_ProductName", "product", "ProductName")
add_index(dbo, "product_ProductTypeID", "product", "ProductTypeID")
add_index(dbo, "product_Barcode", "product", "Barcode")
add_index(dbo, "product_PLU", "product", "PLU")

# Add the lkproducttype table
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("ProductTypeName", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("Description", dbo.type_longtext, True),
    dbo.ddl_add_table_column("IsRetired", dbo.type_integer, False)
])
execute(dbo, dbo.ddl_add_table("lkproducttype", fields) )

# Insert "general" into lkproducttype
execute(dbo, "INSERT INTO lkproducttype (ID, ProductTypeName, Description, IsRetired) VALUES (?, ?, ?, ?)", [ 1, _("General", l), "", 0 ])
execute(dbo, "INSERT INTO configuration (ItemName, ItemValue) VALUES (?, ?)", ["StockDefaultProductTypeID", "1"])

# Add the lktaxrate table
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("TaxRateName", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("Description", dbo.type_longtext, False),
    dbo.ddl_add_table_column("TaxRate", dbo.type_float, False),
    dbo.ddl_add_table_column("IsRetired", dbo.type_integer, False)
])
execute(dbo, dbo.ddl_add_table("lktaxrate", fields) )

# Insert notax into lktaxrate
execute(dbo, "INSERT INTO lktaxrate (ID, TaxRateName, Description, TaxRate, IsRetired) VALUES (?, ?, ?, ?, ?)", [ 1, _("Tax Free", l), "", 0, 0 ])
execute(dbo, "INSERT INTO configuration (ItemName, ItemValue) VALUES (?, ?)", ["StockDefaultTaxRateID", "1"])

# Add the lksunittype table
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("UnitName", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("Description", dbo.type_longtext, False),
    dbo.ddl_add_table_column("IsRetired", dbo.type_integer, False)
])
execute(dbo, dbo.ddl_add_table("lksunittype", fields) )

# Populate lksunittype table
execute(dbo, "INSERT INTO lksunittype (ID, UnitName, Description, IsRetired) VALUES (?, ?, ?, ?)", [ 1, _("kg", l), "", 0 ])
execute(dbo, "INSERT INTO lksunittype (ID, UnitName, Description, IsRetired) VALUES (?, ?, ?, ?)", [ 2, _("g", l), "", 0 ])
execute(dbo, "INSERT INTO lksunittype (ID, UnitName, Description, IsRetired) VALUES (?, ?, ?, ?)", [ 3, _("lb", l), "", 0 ])
execute(dbo, "INSERT INTO lksunittype (ID, UnitName, Description, IsRetired) VALUES (?, ?, ?, ?)", [ 4, _("oz", l), "", 0 ])
execute(dbo, "INSERT INTO lksunittype (ID, UnitName, Description, IsRetired) VALUES (?, ?, ?, ?)", [ 5, _("l", l), "", 0 ])
execute(dbo, "INSERT INTO lksunittype (ID, UnitName, Description, IsRetired) VALUES (?, ?, ?, ?)", [ 6, _("ml", l), "", 0 ])

# Adding 'Movement' stockusagetype setting option
nextid = dbo.get_id_max("stockusagetype")
execute(dbo, "INSERT INTO stockusagetype (ID, UsageTypeName, UsageTypeName, IsRetired) VALUES (?, ?, ?, ?)", [ nextid, _("Movement", l), _("A usage type to represent internal stock movements", l), 0 ])
execute(dbo, "INSERT INTO configuration (ItemName, ItemValue) VALUES (?, ?)", ["StockMovementUsageTypeID", str(nextid)])

# Adding ProductID columns to stocklevel table
add_column(dbo, "stocklevel", "ProductID", dbo.type_integer)
add_index(dbo, "stocklevel_ProductID", "stocklevel", "ProductID")

