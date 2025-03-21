# add customreport.Revision
add_column(dbo, "customreport", "Revision", dbo.type_integer)
execute(dbo,"UPDATE customreport SET Revision=0")