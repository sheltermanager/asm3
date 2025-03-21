# Add PurchasePrice/SalePrice fields to stocklevel
add_column(dbo, "stocklevel", "Cost", "INTEGER")
add_column(dbo, "stocklevel", "UnitPrice", "INTEGER")
execute(dbo,"UPDATE stocklevel SET Cost = 0, UnitPrice = 0")