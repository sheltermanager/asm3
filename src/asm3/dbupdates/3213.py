try:
    # Make displaylocationname and displaylocationstring denormalised fields
    execute(dbo,"ALTER TABLE animal ADD DisplayLocationName %s" % dbo.type_shorttext)
    execute(dbo,"ALTER TABLE animal ADD DisplayLocationString %s" % dbo.type_shorttext)
except Exception as err:
    asm3.al.error("failed creating animal.DisplayLocationName/String: %s" % str(err), "dbupdate.update_3213", dbo)

# Default the values for them
execute(dbo,"UPDATE animal SET DisplayLocationName = " \
    "CASE " \
    "WHEN animal.Archived = 0 AND animal.ActiveMovementType = 2 THEN " \
    "(SELECT MovementType FROM lksmovementtype WHERE ID=animal.ActiveMovementType) " \
    "WHEN animal.Archived = 0 AND animal.ActiveMovementType = 1 AND animal.HasTrialAdoption = 1 THEN " \
    "(SELECT MovementType FROM lksmovementtype WHERE ID=11) " \
    "WHEN animal.Archived = 1 AND animal.DeceasedDate Is Not Null AND animal.ActiveMovementID = 0 THEN " \
    "(SELECT ReasonName FROM deathreason WHERE ID = animal.PTSReasonID) " \
    "WHEN animal.Archived = 1 AND animal.DeceasedDate Is Not Null AND animal.ActiveMovementID <> 0 THEN " \
    "(SELECT MovementType FROM lksmovementtype WHERE ID=animal.ActiveMovementType) " \
    "WHEN animal.Archived = 1 AND animal.DeceasedDate Is Null AND animal.ActiveMovementID <> 0 THEN " \
    "(SELECT MovementType FROM lksmovementtype WHERE ID=animal.ActiveMovementType) " \
    "ELSE " \
    "(SELECT LocationName FROM internallocation WHERE ID=animal.ShelterLocation) " \
    "END")
execute(dbo,"UPDATE animal SET DisplayLocationString = DisplayLocationName")