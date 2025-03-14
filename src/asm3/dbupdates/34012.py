# Add diarytaskdetail.OrderIndex
add_column(dbo, "diarytaskdetail", "OrderIndex", "INTEGER")
execute(dbo,"UPDATE diarytaskdetail SET OrderIndex = ID")