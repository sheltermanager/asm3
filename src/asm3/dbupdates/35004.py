from asm3.dbupdate import execute, add_column

# Add the new phone number additional field type
execute(dbo, "INSERT INTO lksfieldtype (ID, FieldType) VALUES (?, ?)", [ 14, _("Telephone", dbo.locale) ])

