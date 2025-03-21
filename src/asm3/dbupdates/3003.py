# Extend the length of configuration items
modify_column(dbo, "configuration", "ItemValue", dbo.type_longtext)