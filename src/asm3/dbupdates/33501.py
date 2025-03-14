l = dbo.locale
add_column(dbo, "animal", "IsPickup", "INTEGER")
add_column(dbo, "animal", "PickupLocationID", "INTEGER")
add_index(dbo, "animal_PickupLocationID", "animal", "PickupLocationID")
sql = "CREATE TABLE pickuplocation ( ID INTEGER NOT NULL, " \
    "LocationName %(short)s NOT NULL, " \
    "LocationDescription %(long)s )" % { "short": dbo.type_shorttext, "long": dbo.type_longtext }
execute(dbo,sql)
execute(dbo,"INSERT INTO pickuplocation VALUES (1, '%s', '')" % _("Shelter", l))