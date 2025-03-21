# Add customreport.DailyEmailFrequency
add_column(dbo, "customreport", "DailyEmailFrequency", "INTEGER")
execute(dbo,"UPDATE customreport SET DailyEmailFrequency = 0")