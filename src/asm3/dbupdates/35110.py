from asm3.dbupdate import add_column, add_index, execute

add_column(dbo, "diary", "DiaryEndDateTime", dbo.type_datetime)
