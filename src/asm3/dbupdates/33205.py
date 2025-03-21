# Add mandatory column to online form fields
add_column(dbo, "onlineformfield", "Mandatory", "INTEGER")
execute(dbo,"UPDATE onlineformfield SET Mandatory = 0")
