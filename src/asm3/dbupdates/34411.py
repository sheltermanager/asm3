# Add animal.PopupWarning
add_column(dbo, "animal", "PopupWarning", dbo.type_longtext)
execute(dbo,"UPDATE animal SET PopupWarning = ''")