# Add ownerdonation.Fee
add_column(dbo, "ownerdonation", "Fee", dbo.type_integer)
execute(dbo,"UPDATE ownerdonation SET Fee = 0")