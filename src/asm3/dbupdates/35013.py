from asm3.dbupdate import add_column, execute

add_column(dbo, "animallocation", "MovementID", dbo.type_integer)
add_column(dbo, "animallocation", "IsDeath", dbo.type_integer)

execute(dbo, "UPDATE animallocation SET MovementID = 0")
execute(dbo, "UPDATE animallocation SET IsDeath = 0")
