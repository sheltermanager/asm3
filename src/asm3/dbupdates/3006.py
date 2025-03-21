# Add ForName field to messages
add_column(dbo, "messages", "ForName", dbo.type_shorttext)
execute(dbo,"UPDATE messages SET ForName = '*'")