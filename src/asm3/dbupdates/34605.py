l = dbo.locale
# add sponsor flag column, and sponsor/vet as additional field types
add_column(dbo, "owner", "IsSponsor", dbo.type_integer)
add_index(dbo, "owner_IsSponsor", "owner", "IsSponsor")
execute(dbo,"UPDATE owner SET IsSponsor=0")
execute(dbo,"INSERT INTO lksfieldtype (ID, FieldType) VALUES (11, ?)", [ _("Sponsor", l) ])
execute(dbo,"INSERT INTO lksfieldtype (ID, FieldType) VALUES (12, ?)", [ _("Vet", l) ])
