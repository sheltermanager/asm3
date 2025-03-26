from asm3.dbupdate import execute, add_column
dbo = dbo
# Add the new goodwith fields to looking for
add_column(dbo, "media", "SignatureIP", dbo.type_shorttext)
add_column(dbo, "media", "SignatureDevice", dbo.type_shorttext)
add_column(dbo, "media", "SignatureDate", dbo.type_datetime)

