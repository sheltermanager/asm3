from asm3.dbupdate import add_column, add_index, execute

fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("Date", dbo.type_datetime, False),
    dbo.ddl_add_table_column("Balance", dbo.type_integer, False),
    dbo.ddl_add_table_column("RecordVersion", dbo.type_integer, True),
    dbo.ddl_add_table_column("CreatedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("CreatedDate", dbo.type_datetime, False),
    dbo.ddl_add_table_column("LastChangedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("LastChangedDate", dbo.type_datetime, False)
])
execute(dbo, dbo.ddl_add_table("salesreceipt", fields) )

fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("SalesReceiptID", dbo.type_integer, False),
    dbo.ddl_add_table_column("ProductID", dbo.type_integer, False),
    dbo.ddl_add_table_column("StockUsageID", dbo.type_integer, False),
    dbo.ddl_add_table_column("TaxRate", dbo.type_integer, False),
    dbo.ddl_add_table_column("Price", dbo.type_integer, False),
    dbo.ddl_add_table_column("Description", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("RecordVersion", dbo.type_integer, True),
    dbo.ddl_add_table_column("CreatedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("CreatedDate", dbo.type_datetime, False),
    dbo.ddl_add_table_column("LastChangedBy", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("LastChangedDate", dbo.type_datetime, False)
])
execute(dbo, dbo.ddl_add_table("salesreceiptdetail", fields) )