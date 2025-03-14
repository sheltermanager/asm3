# Add onlineform.EmailFosterer
add_column(dbo, "onlineform", "EmailFosterer", dbo.type_integer)
execute(dbo,"UPDATE onlineform SET EmailFosterer = 0")