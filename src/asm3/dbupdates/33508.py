# Increase the size of the onlineformfield tooltip as it was short text by mistake
modify_column(dbo, "onlineformfield", "Tooltip", dbo.type_longtext)