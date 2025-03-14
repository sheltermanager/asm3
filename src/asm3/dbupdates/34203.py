# Add donationtype.IsVAT
add_column(dbo, "donationtype", "IsVAT", dbo.type_integer)
execute(dbo,"UPDATE donationtype SET IsVAT = 0")