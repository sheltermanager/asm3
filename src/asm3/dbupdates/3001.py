execute(dbo,"DELETE FROM configuration WHERE ItemName LIKE 'MappingService%'")
execute(dbo,"INSERT INTO configuration VALUES (?, ?)", ( "MappingServiceLinkURL", "http://maps.google.com/maps?q={0}" ))
execute(dbo,"INSERT INTO configuration VALUES (?, ?)", ( "MappingServiceEmbeddedURL", "https://maps.googleapis.com/maps/api/staticmap?center={0}&size=250x250&maptype=roadmap&sensor=false"))
if 0 == dbo.query_int("SELECT COUNT(ItemName) FROM configuration WHERE ItemName LIKE 'SystemTheme'"):
    execute(dbo,"INSERT INTO configuration VALUES (?, ?)", ( "SystemTheme", "asm" ))
if 0 == dbo.query_int("SELECT COUNT(ItemName) FROM configuration WHERE ItemName LIKE 'Timezone'"):
    execute(dbo,"INSERT INTO configuration VALUES (?,?)", ( "Timezone", "0" ))
