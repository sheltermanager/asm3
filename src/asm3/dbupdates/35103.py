from asm3.dbupdate import execute

# Add the new autocomplete additional field type
execute(dbo, "INSERT INTO lksfieldtype (ID, FieldType) VALUES (?, ?)", [ 16, _("Autocomplete", dbo.locale) ])
