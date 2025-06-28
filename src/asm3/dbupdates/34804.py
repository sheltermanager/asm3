l = dbo.locale
# add adoption coordinator as additional field types
execute(dbo,"INSERT INTO lksfieldtype (ID, FieldType) VALUES (13, ?)", [ _("Adoption Coordinator", l) ] )
