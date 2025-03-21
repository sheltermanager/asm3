# Add media.CreatedDate
add_column(dbo, "media", "CreatedDate", dbo.type_datetime)
add_index(dbo, "media_CreatedDate", "media", "CreatedDate")
execute(dbo,"UPDATE media SET CreatedDate=Date")