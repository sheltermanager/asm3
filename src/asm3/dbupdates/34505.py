# add extra row for Selective to good with
l = dbo.locale
execute(dbo,"INSERT INTO lksynun VALUES (3, ?)", [ _("Selective", l) ])