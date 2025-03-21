execute(dbo,"DELETE FROM configuration WHERE ItemName LIKE 'MappingService%'")
execute(dbo,"INSERT INTO configuration VALUES ('%s', '%s')" % ( "MappingServiceLinkURL", "http://maps.google.com/maps?q={0}" ))
execute(dbo,"INSERT INTO configuration VALUES ('%s', '%s')" % ( "MappingServiceEmbeddedURL", "https://maps.googleapis.com/maps/api/staticmap?center={0}&size=250x250&maptype=roadmap&sensor=false"))
if 0 == dbo.query_int("SELECT COUNT(ItemName) FROM configuration WHERE ItemName LIKE 'SystemTheme'"):
    execute(dbo,"DELETE FROM configuration WHERE ItemName LIKE 'SystemTheme'")
    execute(dbo,"INSERT INTO configuration VALUES ('%s', '%s')" % ( "SystemTheme", "smoothness" ))
if 0 == dbo.query_int("SELECT COUNT(ItemName) FROM configuration WHERE ItemName LIKE 'Timezone'"):
    execute(dbo,"DELETE FROM configuration WHERE ItemName LIKE 'Timezone'")
    execute(dbo,"INSERT INTO configuration VALUES ('%s', '%s')" % ( "Timezone", "0" ))