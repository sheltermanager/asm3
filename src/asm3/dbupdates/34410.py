# Add owner.ExtraIDs
add_column(dbo, "owner", "ExtraIDs", dbo.type_shorttext)
add_index(dbo, "owner_ExtraIDs", "owner", "ExtraIDs")
execute(dbo,"UPDATE owner SET ExtraIDs = ''")
