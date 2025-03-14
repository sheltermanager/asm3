# Add ownerdonation.ReceiptNumber
add_column(dbo, "ownerdonation", "ReceiptNumber", dbo.type_shorttext)
add_index(dbo, "ownerdonation_ReceiptNumber", "ownerdonation", "ReceiptNumber")
# Use ID to prepopulate existing records
execute(dbo,"UPDATE ownerdonation SET ReceiptNumber = %s" % dbo.sql_zero_pad_left("ID", 8))