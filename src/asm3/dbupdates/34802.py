# Switching to use primarykey/cache combo for receipt numbers and online forms, and
# possibly for future PK depending on performance. Clear any old junk out.
execute(dbo,"DELETE FROM primarykey")