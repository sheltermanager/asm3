# rename animallocation.By to animallocation.MovedBy (By is a MySQL reserved word)
if column_exists(dbo, "animallocation", "By"):
    add_column(dbo, "animallocation", "MovedBy", dbo.type_shorttext)
    dbo.execute_dbupdate("UPDATE animallocation SET MovedBy=By")
    drop_column(dbo, "animallocation", "By")