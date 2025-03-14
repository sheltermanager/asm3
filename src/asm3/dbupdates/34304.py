# Add new ownervoucher columns
add_column(dbo, "ownervoucher", "AnimalID", dbo.type_integer)
add_column(dbo, "ownervoucher", "DatePresented", dbo.type_datetime)
add_column(dbo, "ownervoucher", "VoucherCode", dbo.type_shorttext)
add_index(dbo, "ownervoucher_AnimalID", "ownervoucher", "AnimalID")
add_index(dbo, "ownervoucher_DatePresented", "ownervoucher", "DatePresented")
add_index(dbo, "ownervoucher_VoucherCode", "ownervoucher", "VoucherCode")
# Set the default vouchercode to ID padded to 6 digits
execute(dbo,"UPDATE ownervoucher SET VoucherCode = %s" % dbo.sql_zero_pad_left("ID", 6))