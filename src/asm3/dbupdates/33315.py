# Add size field to waiting list
add_column(dbo, "animalwaitinglist", "Size", "INTEGER")
add_index(dbo, "animalwaitinglist_Size", "animalwaitinglist", "Size")
execute(dbo,"UPDATE animalwaitinglist SET Size = 2")