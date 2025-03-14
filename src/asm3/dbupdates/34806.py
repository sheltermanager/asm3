# Add IncidentCode column
add_column(dbo, "animalcontrol", "IncidentCode", dbo.type_shorttext)
add_index(dbo, "animalcontrol_IncidentCode", "animalcontrol", "IncidentCode")
batch = []
for r in dbo.query("SELECT ID FROM animalcontrol"):
    batch.append([ asm3.utils.padleft(r.ID, 6), r.ID ])
dbo.execute_many("UPDATE animalcontrol SET IncidentCode = ? WHERE ID = ?", batch, override_lock=True) 