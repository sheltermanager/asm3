# Add additionalfield.NewRecord
add_column(dbo, "additionalfield", "NewRecord", dbo.type_integer)
execute(dbo,"UPDATE additionalfield SET NewRecord = Mandatory")