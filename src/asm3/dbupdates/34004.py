l = dbo.locale
# Add the TransportTypeID column
add_column(dbo, "animaltransport", "TransportTypeID", "INTEGER")
add_index(dbo, "animaltransport_TransportTypeID", "animaltransport", "TransportTypeID")
execute(dbo,"UPDATE animaltransport SET TransportTypeID = 4") # Vet Visit
# Add the transporttype lookup table
sql = "CREATE TABLE transporttype ( ID INTEGER NOT NULL, " \
    "TransportTypeName %(short)s NOT NULL, " \
    "TransportTypeDescription %(long)s, " \
    "IsRetired INTEGER)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
execute(dbo,sql)
execute(dbo,"INSERT INTO transporttype VALUES (1, '%s', '', 0)" % _("Adoption Event", l))
execute(dbo,"INSERT INTO transporttype VALUES (2, '%s', '', 0)" % _("Foster Transfer", l))
execute(dbo,"INSERT INTO transporttype VALUES (3, '%s', '', 0)" % _("Surrender Pickup", l))
execute(dbo,"INSERT INTO transporttype VALUES (4, '%s', '', 0)" % _("Vet Visit", l))