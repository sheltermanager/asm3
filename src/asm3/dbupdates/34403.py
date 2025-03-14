# Add onlineformfield.VisibleIf
add_column(dbo, "onlineformfield", "VisibleIf", dbo.type_shorttext)
execute(dbo,"UPDATE onlineformfield SET VisibleIf=''")