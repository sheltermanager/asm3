l = dbo.locale
# add DOA entry type
execute(dbo,"INSERT INTO lksentrytype (ID, EntryTypeName) VALUES (9, ?)", [ _("Dead on arrival", l) ])
