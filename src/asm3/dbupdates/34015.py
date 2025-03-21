# Add new MediaSize and DBFSID columns
add_column(dbo, "media", "MediaSize", dbo.type_integer)
add_column(dbo, "media", "DBFSID", dbo.type_integer)
add_index(dbo, "media_DBFSID", "media", "DBFSID")
# Set sizes to 0 they'll be updated by another process later 
execute(dbo,"UPDATE media SET MediaSize = 0")
# Find the right DBFS element for each media item
execute(dbo,"UPDATE media SET DBFSID = (SELECT MAX(ID) FROM dbfs WHERE Name LIKE media.MediaName) WHERE MediaType=0")
execute(dbo,"UPDATE media SET DBFSID = 0 WHERE DBFSID Is Null")
# Remove any _scaled component of names from both media and dbfs
execute(dbo,"UPDATE media SET MediaName = %s WHERE MediaName LIKE '%%_scaled%%'" % dbo.sql_replace("MediaName", "_scaled", ""))
execute(dbo,"UPDATE dbfs SET Name = %s WHERE Name LIKE '%%_scaled%%'" % dbo.sql_replace("Name", "_scaled", ""))
