from asm3.dbupdate import add_column, add_index, execute

add_column(dbo, "customreport", "SendAsPDF", dbo.type_integer)
add_index(dbo, "customreport_SendAsPDF", "customreport", "SendAsPDF")
execute(dbo, "UPDATE customreport SET SendAsPDF = 0")
