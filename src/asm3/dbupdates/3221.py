# More short fields
fields = [ "activeuser.UserName", "customreport.Title", "customreport.Category" ]
for f in fields:
    table, field = f.split(".")
    modify_column(dbo, table, field, dbo.type_shorttext)
