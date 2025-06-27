from asm3.dbupdate import execute

execute(dbo, "CREATE TABLE lkclinicinvoiceitems (ID %(int)s NOT NULL PRIMARY KEY, ClinicInvoiceItemName %(short)s, ClinicInvoiceItemDescription %(long)s, DefaultCost %(int)s, IsRetired %(int)s)" % { "int": dbo.type_integer, "short": dbo.type_shorttext, "long": dbo.type_longtext })

