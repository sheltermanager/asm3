# Add testtype.RescheduleDays
add_column(dbo, "testtype", "RescheduleDays", dbo.type_integer)
execute(dbo,"UPDATE testtype SET RescheduleDays = 0 WHERE RescheduleDays Is Null")