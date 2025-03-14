# Add vaccinationtype.RescheduleDays
add_column(dbo, "vaccinationtype", "RescheduleDays", dbo.type_integer)
execute(dbo,"UPDATE vaccinationtype SET RescheduleDays = 0 WHERE RescheduleDays Is Null")
# Add animallost.MicrochipNumber and animalfound.MicrochipNumber
add_column(dbo, "animallost", "MicrochipNumber", dbo.type_shorttext)
add_column(dbo, "animalfound", "MicrochipNumber", dbo.type_shorttext)
add_index(dbo, "animallost_MicrochipNumber", "animallost", "MicrochipNumber")
add_index(dbo, "animalfound_MicrochipNumber", "animalfound", "MicrochipNumber")
# Add animallostfoundmatch.LostMicrochipNumber/FoundMicrochipNumber
add_column(dbo, "animallostfoundmatch", "LostMicrochipNumber", dbo.type_shorttext)
add_column(dbo, "animallostfoundmatch", "FoundMicrochipNumber", dbo.type_shorttext)