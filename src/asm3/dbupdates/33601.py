# Add animaltransport table
sql = "CREATE TABLE animaltransport ( ID INTEGER NOT NULL PRIMARY KEY, " \
    "AnimalID INTEGER NOT NULL, " \
    "DriverOwnerID INTEGER NOT NULL, " \
    "PickupOwnerID INTEGER NOT NULL, " \
    "DropoffOwnerID INTEGER NOT NULL, " \
    "PickupDateTime %(date)s NOT NULL, " \
    "DropoffDateTime %(date)s NOT NULL, " \
    "Status INTEGER NOT NULL, " \
    "Miles INTEGER, " \
    "Cost INTEGER NOT NULL, " \
    "CostPaidDate %(date)s NULL, " \
    "Comments %(long)s, " \
    "RecordVersion INTEGER, " \
    "CreatedBy %(short)s, " \
    "CreatedDate %(date)s, " \
    "LastChangedBy %(short)s, " \
    "LastChangedDate %(date)s)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
execute(dbo,sql)
add_index(dbo, "animaltransport_AnimalID", "animaltransport", "AnimalID")
add_index(dbo, "animaltransport_DriverOwnerID", "animaltransport", "DriverOwnerID")
add_index(dbo, "animaltransport_PickupOwnerID", "animaltransport", "PickupOwnerID")
add_index(dbo, "animaltransport_DropoffOwnerID", "animaltransport", "DropoffOwnerID")
add_index(dbo, "animaltransport_PickupDateTime", "animaltransport", "PickupDateTime")
add_index(dbo, "animaltransport_DropoffDateTime", "animaltransport", "DropoffDateTime")
add_index(dbo, "animaltransport_Status", "animaltransport", "Status")
# Add the IsDriver column
add_column(dbo, "owner", "IsDriver", "INTEGER")
# Convert any existing transport movements to the new format
tr = dbo.query("SELECT * FROM adoption WHERE MovementType = 13")
tid = 1
for m in tr:
    try:
        execute(dbo,"INSERT INTO animaltransport (ID, AnimalID, DriverOwnerID, PickupOwnerID, DropoffOwnerID, " \
        "PickupDateTime, DropoffDateTime, Status, Miles, Cost, Comments, RecordVersion, CreatedBy, " \
        "CreatedDate, LastChangedBy, LastChangedDate) VALUES ( " \
        "?, ?, 0, 0, 0, ?, ?, 3, 0, 0, ?, 1, 'update', ?, 'update', ?) ", \
        ( tid, m["ANIMALID"], m["MOVEMENTDATE"], m["MOVEMENTDATE"], m["COMMENTS"], 
            m["CREATEDDATE"], m["LASTCHANGEDDATE"] ) )
        tid += 1
    except Exception as err:
        asm3.al.error("failed creating animaltransport row %s: %s" % (tid, str(err)), "dbupdate.update_33601", dbo)
# Remove old transport records and the type
execute(dbo,"DELETE FROM adoption WHERE MovementType = 13")
execute(dbo,"DELETE FROM lksmovementtype WHERE ID = 13")
