# add eventid column to movements
add_column(dbo, "adoption", "EventID", dbo.type_integer)
add_index(dbo, "adoption_EventID", "adoption", "EventID")