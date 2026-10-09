from asm3.dbupdate import add_column, add_index, execute

add_column(dbo, "onlineform", "EmailSubmissionLimitDays", dbo.type_integer)
execute(dbo, "UPDATE onlineform SET EmailSubmissionLimitDays = 0")
add_index(dbo, "onlineform_EmailSubmissionLimitDays", "onlineform", "EmailSubmissionLimitDays")
