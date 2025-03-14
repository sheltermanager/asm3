# Add animaltest.AdministeringVetID
add_column(dbo, "animaltest", "AdministeringVetID", "INTEGER")
add_index(dbo, "animaltest_AdministeringVetID", "animaltest", "AdministeringVetID")
dbo.execute_dbupdate("UPDATE animaltest SET AdministeringVetID = 0")