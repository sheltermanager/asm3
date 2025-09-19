from asm3.dbupdate import add_column, add_index, execute
l = dbo.locale

add_column(dbo, "diary", "ColourSchemeID", dbo.type_integer)
execute(dbo, "UPDATE diary SET ColourSchemeID = 0")

add_column(dbo, "diarytaskdetail", "ColourSchemeID", dbo.type_integer)
execute(dbo, "UPDATE diarytaskdetail SET ColourSchemeID = 1")