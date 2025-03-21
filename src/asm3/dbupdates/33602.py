# Add animalfiguresannual.EntryReasonID
add_column(dbo, "animalfiguresannual", "EntryReasonID", "INTEGER")
add_index(dbo, "animalfiguresannual_EntryReasonID", "animalfiguresannual", "EntryReasonID")