l = dbo.locale
# Add ownerrota table
sql = "CREATE TABLE ownerrota ( ID INTEGER NOT NULL PRIMARY KEY, " \
    "OwnerID INTEGER NOT NULL, " \
    "StartDateTime %(date)s NOT NULL, " \
    "EndDateTime %(date)s NOT NULL, " \
    "RotaTypeID INTEGER NOT NULL, " \
    "Comments %(long)s, " \
    "RecordVersion INTEGER, " \
    "CreatedBy %(short)s, " \
    "CreatedDate %(date)s, " \
    "LastChangedBy %(short)s, " \
    "LastChangedDate %(date)s)" % { "short": dbo.type_shorttext, "long": dbo.type_longtext, "date": dbo.type_datetime }
execute(dbo,sql)
add_index(dbo, "ownerrota_OwnerID", "ownerrota", "OwnerID")
add_index(dbo, "ownerrota_StartDateTime", "ownerrota", "StartDateTime")
add_index(dbo, "ownerrota_EndDateTime", "ownerrota", "EndDateTime")
add_index(dbo, "ownerrota_RotaTypeID", "ownerrota", "RotaTypeID")
# Add lksrotatype table
sql = "CREATE TABLE lksrotatype ( ID INTEGER NOT NULL PRIMARY KEY, " \
    "RotaType %(short)s NOT NULL)" % { "short": dbo.type_shorttext }
execute(dbo,sql)
execute(dbo,"INSERT INTO lksrotatype VALUES (1, ?)", [ _("Shift", l) ])
execute(dbo,"INSERT INTO lksrotatype VALUES (2, ?)", [ _("Vacation", l) ])
execute(dbo,"INSERT INTO lksrotatype VALUES (3, ?)", [_("Leave of absence", l) ])
execute(dbo,"INSERT INTO lksrotatype VALUES (4, ?)", [_("Maternity", l) ])
execute(dbo,"INSERT INTO lksrotatype VALUES (5, ?)", [_("Personal", l) ])
execute(dbo,"INSERT INTO lksrotatype VALUES (6, ?)", [_("Rostered day off", l) ])
execute(dbo,"INSERT INTO lksrotatype VALUES (7, ?)", [_("Sick leave", l) ])
execute(dbo,"INSERT INTO lksrotatype VALUES (8, ?)", [_("Training", l) ])
execute(dbo,"INSERT INTO lksrotatype VALUES (9, ?)", [_("Unavailable", l) ])
