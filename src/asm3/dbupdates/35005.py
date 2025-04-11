from asm3.dbupdate import execute, add_column
# Add the new phone number additional field type
add_column(dbo, "onlineformfield", "ValidationRule", dbo.type_integer)

