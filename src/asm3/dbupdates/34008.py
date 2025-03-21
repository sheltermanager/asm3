# Remove the old asilomar figures report if it exists
execute(dbo,"DELETE FROM customreport WHERE Title = 'Asilomar Figures'")
# Remove the asilomar tables as they're no longer needed
execute(dbo,"DROP TABLE animalfiguresasilomar")
execute(dbo,"DROP TABLE animalfiguresmonthlyasilomar")