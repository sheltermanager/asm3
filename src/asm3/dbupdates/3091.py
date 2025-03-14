# Reinstated map url in 3005 did not use SSL for embedded link
execute(dbo,"DELETE FROM configuration WHERE ItemName LIKE 'MappingService%'")
execute(dbo,"INSERT INTO configuration VALUES ('%s', '%s')" % ( "MappingServiceLinkURL", "http://maps.google.com/maps?q={0}" ))
execute(dbo,"INSERT INTO configuration VALUES ('%s', '%s')" % ( "MappingServiceEmbeddedURL", "https://maps.googleapis.com/maps/api/staticmap?center={0}&size=250x250&maptype=roadmap&sensor=false"))
# Add ExcludeFromPublish field to media
add_column(dbo, "media", "ExcludeFromPublish", "INTEGER")
execute(dbo,"UPDATE media SET ExcludeFromPublish = 0")