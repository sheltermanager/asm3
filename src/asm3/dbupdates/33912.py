# Add EmailConfirmationMessage
add_column(dbo, "onlineform", "EmailMessage", dbo.type_longtext)
execute(dbo,"UPDATE onlineform SET EmailMessage = ''")