l = dbo.locale
# Add animal.EntryTypeID and lksentrytype
add_column(dbo, "animal", "EntryTypeID", dbo.type_integer)
add_index(dbo, "animal_EntryTypeID", "animal", "EntryTypeID")
add_column(dbo, "animalentry", "EntryTypeID", dbo.type_integer)
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("EntryTypeName", dbo.type_shorttext, False),
])
execute(dbo, dbo.ddl_add_table("lksentrytype", fields) )
execute(dbo,"INSERT INTO lksentrytype VALUES (1, ?)", [ _("Surrender", l) ])
execute(dbo,"INSERT INTO lksentrytype VALUES (2, ?)", [ _("Stray", l) ])
execute(dbo,"INSERT INTO lksentrytype VALUES (3, ?)", [ _("Transfer In", l) ])
execute(dbo,"INSERT INTO lksentrytype VALUES (4, ?)", [ _("TNR", l) ])
execute(dbo,"INSERT INTO lksentrytype VALUES (5, ?)", [ _("Born in care", l) ])
execute(dbo,"INSERT INTO lksentrytype VALUES (6, ?)", [ _("Wildlife", l) ])
execute(dbo,"INSERT INTO lksentrytype VALUES (7, ?)", [ _("Seized", l) ])
execute(dbo,"INSERT INTO lksentrytype VALUES (8, ?)", [ _("Abandoned", l) ])
# Set the default value for animal.EntryTypeID based on existing data
strayid = dbo.query_int("SELECT ID FROM entryreason WHERE LOWER(ReasonName) LIKE '%stray%'")
tnrid = dbo.query_int("SELECT ID FROM entryreason WHERE LOWER(ReasonName) LIKE '%tnr%'")
execute(dbo,"UPDATE animal SET EntryTypeID = 0")
execute(dbo,"UPDATE animalentry SET EntryTypeID = 0")
execute(dbo,"UPDATE animal SET EntryTypeID=3 WHERE IsTransfer=1")
execute(dbo,"UPDATE animal SET EntryTypeID=7 WHERE CrueltyCase=1")
if strayid > 0: execute(dbo,"UPDATE animal SET EntryTypeID=2 WHERE EntryReasonID=%s AND NonShelterAnimal=0 AND EntryTypeID=0" % strayid)
if tnrid > 0: execute(dbo,"UPDATE animal SET EntryTypeID=4 WHERE EntryReasonID=%s AND NonShelterAnimal=0 AND EntryTypeID=0" % tnrid)
execute(dbo,"UPDATE animal SET EntryTypeID=5 WHERE DateBroughtIn=DateOfBirth AND NonShelterAnimal=0 AND EntryTypeID=0")
execute(dbo,"UPDATE animal SET EntryTypeID=1 WHERE NonShelterAnimal=0 AND EntryTypeID=0")
