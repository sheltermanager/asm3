# Set initial value for those flags
execute(dbo,"UPDATE adoption SET IsPermanentFoster = 0 WHERE IsPermanentFoster Is Null")
execute(dbo,"UPDATE animal SET HasPermanentFoster = 0 WHERE HasPermanentFoster Is Null")