from asm3.dbupdate import add_column, add_index, execute

add_column(dbo, "customreport", "DailyEmailSendAsPDF", dbo.type_integer)
execute(dbo, "UPDATE customreport SET DailyEmailSendAsPDF = 0")
