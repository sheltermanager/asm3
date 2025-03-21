# Add default quicklinks
execute(dbo,"DELETE FROM configuration WHERE ItemName Like 'QuicklinksID'")
execute(dbo,"INSERT INTO configuration VALUES ('%s', '%s')" % ( "QuicklinksID", "35,25,33,31,34,19,20"))
