# Person investigation table
execute(dbo,"CREATE TABLE ownerinvestigation ( ID INTEGER NOT NULL, " \
    "OwnerID INTEGER NOT NULL, Date %s NOT NULL, Notes %s NOT NULL, " \
    "RecordVersion INTEGER, CreatedBy %s, CreatedDate %s, " \
    "LastChangedBy %s, LastChangedDate %s)" % \
    (dbo.type_datetime, dbo.type_longtext, dbo.type_shorttext, dbo.type_datetime, dbo.type_shorttext, dbo.type_datetime))
add_index(dbo, "ownerinvestigation_ID", "ownerinvestigation", "ID", True)
add_index(dbo, "ownerinvestigation_Date", "ownerinvestigation", "Date")