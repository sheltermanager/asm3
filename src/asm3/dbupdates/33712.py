# Add ownerdonation Sales Tax/VAT fields
add_column(dbo, "ownerdonation", "IsVAT", "INTEGER")
add_column(dbo, "ownerdonation", "VATRate", dbo.type_float)
add_column(dbo, "ownerdonation", "VATAmount", "INTEGER")
add_index(dbo, "ownerdonation_IsVAT", "ownerdonation", "IsVAT")
execute(dbo,"UPDATE ownerdonation SET IsVAT=0, VATRate=0, VATAmount=0")