if asm3.smcom.active():
    # sheltermanager.com only: calculate media file sizes for existing databases
    # ===
    # Reapply update 34015 where necessary as it was botched on some smcom databases
    execute(dbo,"UPDATE media SET DBFSID = (SELECT MAX(ID) FROM dbfs WHERE Name LIKE media.MediaName) WHERE DBFSID Is Null OR DBFSID = 0")
    execute(dbo,"UPDATE media SET DBFSID = 0 WHERE DBFSID Is Null")
    # Remove any _scaled component of names from both media and dbfs
    execute(dbo,"UPDATE media SET MediaName = %s WHERE MediaName LIKE '%%_scaled%%'" % dbo.sql_replace("MediaName", "_scaled", ""))
    execute(dbo,"UPDATE dbfs SET Name = %s WHERE Name LIKE '%%_scaled%%'" % dbo.sql_replace("Name", "_scaled", ""))
    # Read the file size of all media files that are not set and update the media table
    batch = []
    for r in dbo.query("SELECT ID, DBFSID, MediaName FROM media WHERE (MediaSize Is Null OR MediaSize = 0) AND (DBFSID Is Not Null AND DBFSID > 0)"):
        ext = r.medianame[r.medianame.rfind("."):]
        fname = "/root/media/%s/%s%s" % (dbo.name(), r.dbfsid, ext)
        try:
            fsize = os.path.getsize(fname)
            batch.append( (fsize, r.id) )
        except:
            pass # Ignore attempts to read non-existent files
    dbo.execute_many("UPDATE media SET MediaSize = ? WHERE ID = ?", batch, override_lock=True) 