# Add TNR movement type
l = dbo.locale
execute(dbo,"INSERT INTO lksmovementtype (ID, MovementType) VALUES (13, ?)", [ _("TNR", l) ])