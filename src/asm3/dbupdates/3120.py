# This stuff only applies to MySQL databases - we have to import a lot of these
# and if they were created by ASM3 they don't quite match our 2870 upgrade schemas
# as I accidentally had createdby/lastchangedby fields in 3 tables that shouldn't
# have been there and there was a typo in the lastpublishedp911 field (missing the p)
if dbo.dbtype == "MYSQL": 
    
    if column_exists(dbo, "diarytaskdetail", "createdby"):
        drop_column(dbo, "diarytaskdetail", "createdby")
        drop_column(dbo, "diarytaskdetail", "createddate")
        drop_column(dbo, "diarytaskdetail", "lastchangedby")
        drop_column(dbo, "diarytaskdetail", "lastchangeddate")
    if column_exists(dbo, "diarytaskhead", "createdby"):
        drop_column(dbo, "diarytaskhead", "createdby")
        drop_column(dbo, "diarytaskhead", "createddate")
        drop_column(dbo, "diarytaskhead", "lastchangedby")
        drop_column(dbo, "diarytaskhead", "lastchangeddate")
    if column_exists(dbo, "media", "createdby"):
        drop_column(dbo, "media", "createdby")
        drop_column(dbo, "media", "createddate")
        drop_column(dbo, "media", "lastchangedby")
        drop_column(dbo, "media", "lastchangeddate")
    if column_exists(dbo, "media", "lastpublished911"):
        execute(dbo,"ALTER TABLE media CHANGE COLUMN lastpublished911 lastpublishedp911 DATETIME")
