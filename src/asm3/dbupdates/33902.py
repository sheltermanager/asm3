# Add asm3.onlineform.EmailSubmitter field
add_column(dbo, "onlineform", "EmailSubmitter", "INTEGER")
execute(dbo,"UPDATE onlineform SET EmailSubmitter = 1")