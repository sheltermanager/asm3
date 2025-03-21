# Add animaltransport.TransportReference
add_column(dbo, "animaltransport", "TransportReference", dbo.type_shorttext)
add_index(dbo, "animaltransport_TransportReference", "animaltransport", "TransportReference")
execute(dbo,"UPDATE animaltransport SET TransportReference=''")