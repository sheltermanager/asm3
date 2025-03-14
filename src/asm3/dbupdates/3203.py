l = dbo.locale
# Add Trial Adoption movement type
execute(dbo,"INSERT INTO lksmovementtype (ID, MovementType) VALUES (11, ?)", [ _("Trial Adoption", l) ] )