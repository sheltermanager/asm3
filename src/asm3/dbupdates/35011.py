from asm3.dbupdate import execute

fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("ClinicInvoiceItemName", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("ClinicInvoiceItemDescription", dbo.type_longtext, True),
    dbo.ddl_add_table_column("DefaultCost", dbo.type_integer, False),
    dbo.ddl_add_table_column("IsRetired", dbo.type_integer, False)
])
execute(dbo, dbo.ddl_add_table("lkclinicinvoiceitems", fields) )