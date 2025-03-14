# Add the publishlog table
sql = "CREATE TABLE publishlog ( ID INTEGER NOT NULL, " \
    "PublishDateTime %(date)s NOT NULL, " \
    "Name %(short)s NOT NULL, " \
    "Success INTEGER NOT NULL, " \
    "Alerts INTEGER NOT NULL, " \
    "LogData %(long)s NOT NULL)" % { "date": dbo.type_datetime, "short": dbo.type_shorttext, "long": dbo.type_longtext }
execute(dbo,sql)
add_index(dbo, "publishlog_PublishDateTime", "publishlog", "PublishDateTime")
add_index(dbo, "publishlog_Name", "publishlog", "Name")
# Remove old publish logs, reports and asm news from the dbfs
execute(dbo,"DELETE FROM dbfs WHERE Path LIKE '/logs%'")
execute(dbo,"DELETE FROM dbfs WHERE Path LIKE '/reports/daily%'")
execute(dbo,"DELETE FROM dbfs WHERE Name LIKE 'asm.news'")