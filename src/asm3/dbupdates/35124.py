from asm3.dbupdate import add_column, execute

add_column(dbo, "animallost", "AreaLatLong", dbo.type_shorttext)
execute(dbo, "UPDATE animallost SET AreaLatLong = ''")

add_column(dbo, "animalfound", "AreaLatLong", dbo.type_shorttext)
execute(dbo, "UPDATE animalfound SET AreaLatLong = ''")
