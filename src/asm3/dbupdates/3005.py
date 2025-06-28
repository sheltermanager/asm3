# 3004 was broken and deleted the mapping service by accident, so we reinstate it
execute(dbo,"DELETE FROM configuration WHERE ItemName LIKE 'MappingService%'")
execute(dbo,"INSERT INTO configuration VALUES (?, ?)", ( "MappingServiceLinkURL", "http://maps.google.com/maps?q={0}" ))
execute(dbo,"INSERT INTO configuration VALUES (?, ?)", ( "MappingServiceEmbeddedURL", "https://maps.googleapis.com/maps/api/staticmap?center={0}&size=250x250&maptype=roadmap&sensor=false"))
# Set default search sort to last changed/relevance
execute(dbo,"DELETE FROM configuration WHERE ItemName LIKE 'RecordSearchLimit' OR ItemName Like 'SearchSort'")
execute(dbo,"INSERT INTO configuration VALUES (?, ?)", ( "RecordSearchLimit", "1000" ))
execute(dbo,"INSERT INTO configuration VALUES (?, ?)", ( "SearchSort", "3" ))
