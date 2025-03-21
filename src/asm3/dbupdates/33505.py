# Add daily email hour field to reports
add_column(dbo, "customreport", "DailyEmailHour", "INTEGER")
execute(dbo,"UPDATE customreport SET DailyEmailHour = -1")