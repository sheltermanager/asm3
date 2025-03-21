# Add extra audit fields to media table to match other tables
# (CreatedDate already existed from update 34402)
add_column(dbo, "media", "CreatedBy", dbo.type_shorttext)
add_column(dbo, "media", "LastChangedBy", dbo.type_shorttext)
add_column(dbo, "media", "LastChangedDate", dbo.type_datetime)
# Add MediaSource column to identify where media came from
add_column(dbo, "media", "MediaSource", dbo.type_integer)
add_index(dbo, "media_MediaSource", "media", "MediaSource")
# 0 = attach file, 4 = online form, 5 = document template
dbo.execute_dbupdate("UPDATE media SET MediaSource = CASE " \
    "WHEN SignatureHash LIKE 'online%' THEN 4 " \
    "WHEN MediaName LIKE '%.html' THEN 5 " \
    "ELSE 0 END")
# Add MediaFlags column to allow users to tag media
add_column(dbo, "media", "MediaFlags", dbo.type_shorttext)
add_index(dbo, "media_MediaFlags", "media", "MediaFlags")
dbo.execute_dbupdate("UPDATE media SET MediaFlags = ''")
# Add lkmediaflags table
fields = ",".join([
    dbo.ddl_add_table_column("ID", dbo.type_integer, False, pk=True),
    dbo.ddl_add_table_column("Flag", dbo.type_shorttext, False),
    dbo.ddl_add_table_column("IsRetired", dbo.type_integer, True)
])
execute(dbo, dbo.ddl_add_table("lkmediaflags", fields) )
