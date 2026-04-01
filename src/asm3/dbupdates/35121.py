from asm3.dbupdate import add_column, add_index, execute

add_column(dbo, "clinicinvoiceitem", "StockUsageIDs", dbo.type_integer)
execute(dbo, "UPDATE clinicinvoiceitem SET StockUsageIDs = ''")
