l = dbo.locale
# Add Transport movement type
execute(dbo,"INSERT INTO lksmovementtype (ID, MovementType) VALUES (13, ?)", [ _("Transport", l) ])