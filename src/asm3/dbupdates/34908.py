# Add stocklevel.Barcode
add_column(dbo, "stocklevel", "Barcode", dbo.type_shorttext)
add_index(dbo, "stocklevel_Barcode", "stocklevel", "Barcode")
execute(dbo, "UPDATE stocklevel SET Barcode=''")
