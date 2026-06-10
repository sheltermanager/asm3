from asm3.dbupdate import add_column, execute

add_column(dbo, "animallost", "LatLong", dbo.type_shorttext)
execute(dbo, "UPDATE animallost SET LatLong = ''")

add_column(dbo, "animalfound", "LatLong", dbo.type_shorttext)
execute(dbo, "UPDATE animalfound SET LatLong = ''")
