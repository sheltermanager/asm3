# Add extra payment fields
add_column(dbo, "ownerdonation", "Quantity", "INTEGER")
add_column(dbo, "ownerdonation", "UnitPrice", "INTEGER")
add_column(dbo, "ownerdonation", "ChequeNumber", dbo.type_shorttext)
add_index(dbo, "ownerdonation_ChequeNumber", "ownerdonation", "ChequeNumber")
execute(dbo,"UPDATE ownerdonation SET Quantity = 1, UnitPrice = Donation, ChequeNumber = ''")