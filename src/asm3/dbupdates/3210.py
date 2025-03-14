# Anyone using MySQL who created their database with the db
# initialiser here will have some short columns as CLOB
# wasn't mapped properly
if dbo.dbtype == "MYSQL":
    execute(dbo,"ALTER TABLE dbfs MODIFY Content LONGTEXT")
    execute(dbo,"ALTER TABLE media MODIFY MediaNotes LONGTEXT NOT NULL")
    execute(dbo,"ALTER TABLE log MODIFY Comments LONGTEXT NOT NULL")