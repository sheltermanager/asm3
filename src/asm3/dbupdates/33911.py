# NB: 33910 was broken so moved to 33911 and fixed
# Cannot usually modify a column that a view depends on in Postgres
if dbo.dbtype == "POSTGRESQL": dbo.execute_dbupdate("DROP VIEW v_animalwaitinglist")
# Extend animalasm3.waitinglist.AnimalDescription
modify_column(dbo, "animalwaitinglist", "AnimalDescription", dbo.type_longtext)