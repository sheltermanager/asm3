l = dbo.locale
# Add the new mediatype field to media and create the link table
execute(dbo,"ALTER TABLE media ADD MediaType INTEGER")
execute(dbo,"ALTER TABLE media ADD WebsiteVideo INTEGER")
execute(dbo,"UPDATE media SET MediaType = 0, WebsiteVideo = 0")
execute(dbo,"CREATE TABLE lksmediatype ( ID INTEGER NOT NULL, MediaType %s NOT NULL )" % ( dbo.type_shorttext))
execute(dbo,"CREATE UNIQUE INDEX lksmediatype_ID ON lksmediatype(ID)")
execute(dbo,"INSERT INTO lksmediatype (ID, MediaType) VALUES (%d, '%s')" % (0, _("File", l)))
execute(dbo,"INSERT INTO lksmediatype (ID, MediaType) VALUES (%d, '%s')" % (1, _("Document Link", l)))
execute(dbo,"INSERT INTO lksmediatype (ID, MediaType) VALUES (%d, '%s')" % (2, _("Video Link", l)))