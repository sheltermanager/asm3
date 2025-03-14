# Add daily email field to reports so they can be emailed to users
add_column(dbo, "customreport", "DailyEmail", dbo.type_longtext)
execute(dbo,"UPDATE customreport SET DailyEmail = ''")