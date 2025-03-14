add_column(dbo, "owner", "PopupWarning", dbo.type_longtext)
add_column(dbo, "owner", "IsDangerous", dbo.type_integer)
execute(dbo,"UPDATE owner SET PopupWarning = '', IsDangerous = 0")