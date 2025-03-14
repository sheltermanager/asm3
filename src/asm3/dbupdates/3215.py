# Rename DisplayLocationString column to just DisplayLocation and ditch DisplayLocationName - it should be calculated
try:
    add_column(dbo, "animal", "DisplayLocation", dbo.type_shorttext)
except:
    asm3.al.error("failed creating animal.DisplayLocation.", "dbupdate.update_3215", dbo)
try:
    dbo.execute_dbupdate("UPDATE animal SET DisplayLocation = DisplayLocationString")
except:
    asm3.al.error("failed copying DisplayLocationString->DisplayLocation", "dbupdate.update_3215", dbo)
try:
    drop_column(dbo, "animal", "DisplayLocationName")
    drop_column(dbo, "animal", "DisplayLocationString")
except:
    asm3.al.error("failed removing DisplayLocationName and DisplayLocationString", "dbupdate.update_3215", dbo)