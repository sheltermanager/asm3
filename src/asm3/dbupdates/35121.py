from asm3.dbupdate import add_column, add_index, execute

# add_column(dbo, "clinicinvoiceitem", "ProductID", dbo.type_integer)
# execute(dbo, "UPDATE clinicinvoiceitem SET clinicinvoiceitem = 0")
# add_index(dbo, "clinicinvoiceitem_AdoptionSourceID", "clinicinvoiceitem", "AdoptionSourceID")

add_column(dbo, "clinicinvoiceitem", "StockUsageIDs", dbo.type_integer)
execute(dbo, "UPDATE clinicinvoiceitem SET StockUsageIDs = ''")
# add_index(dbo, "clinicinvoiceitem_AdoptionSourceID", "clinicinvoiceitem", "AdoptionSourceID")
