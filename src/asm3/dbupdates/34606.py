# add location columns to event table
add_column(dbo, "event", "EventOwnerID", dbo.type_integer)
add_column(dbo, "event", "EventAddress", dbo.type_shorttext)
add_column(dbo, "event", "EventTown", dbo.type_shorttext)
add_column(dbo, "event", "EventCounty", dbo.type_shorttext)
add_column(dbo, "event", "EventPostCode", dbo.type_shorttext)
add_column(dbo, "event", "EventCountry", dbo.type_shorttext)
add_index(dbo, "event_EventOwnerID", "event", "EventOwnerID")
add_index(dbo, "event_EventAddress", "event", "EventAddress")