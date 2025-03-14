# Add stocklevel.Low
add_column(dbo, "stocklevel", "Low", dbo.type_float)
execute(dbo,"UPDATE stocklevel SET Low=0")
# Add additionalfield.Hidden
add_column(dbo, "additionalfield", "Hidden", dbo.type_integer)
execute(dbo,"UPDATE additionalfield SET Hidden=0")