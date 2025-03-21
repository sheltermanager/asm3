l = dbo.locale
# Add IsPermanentFoster and HasPermanentFoster fields
add_column(dbo, "adoption", "IsPermanentFoster", "INTEGER")
add_column(dbo, "animal", "HasPermanentFoster", "INTEGER")
# Add Permanent Foster movement type
execute(dbo,"INSERT INTO lksmovementtype (ID, MovementType) VALUES (12, ?)",  [ _("Permanent Foster", l)] )
