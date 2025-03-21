# Add ownervoucher.VetID
add_column(dbo, "ownervoucher", "VetID", dbo.type_integer)
add_index(dbo, "ownervoucher_VetID", "ownervoucher", "VetID")