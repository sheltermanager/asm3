# Add a new time additional field type
l = dbo.locale
execute(dbo,"INSERT INTO lksfieldtype (ID, FieldType) VALUES (10, ?)", [ _("Time", l) ])