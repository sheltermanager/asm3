# Add RetainUntil to expire media on a set date
add_column(dbo, "media", "RetainUntil", dbo.type_datetime)
add_index(dbo, "media_RetainUntil", "media", "RetainUntil")
add_index(dbo, "media_Date", "media", "Date") # seemed to be missing previously
