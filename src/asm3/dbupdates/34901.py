# Add animallocation.PrevAnimalLocationID
add_column(dbo, "animallocation", "PrevAnimalLocationID", dbo.type_integer)
add_index(dbo, "animallocation_PrevAnimalLocationID", "animallocation", "PrevAnimalLocationID")
# Default the previous location record to 0
execute(dbo,"UPDATE animallocation SET PrevAnimalLocationID = 0")
# Calculate the previous location record for each existing location record
batch = []
rows = dbo.query("SELECT ID, AnimalID, FromLocationID, ToLocationID, FromUnit, ToUnit FROM animallocation ORDER BY Date DESC")
for i, r in enumerate(rows):
    # Iterate the rows after this one, which will have lower dates because we ordered date desc
    for x in range(i, len(rows)):
        # If this is the row previous to this one (ie. moved from this one to the current row r)
        # then set the PrevAnimalLocationID
        if rows[x].ANIMALID == r.ANIMALID and rows[x].TOLOCATIONID == r.FROMLOCATIONID and rows[x].TOUNIT == r.FROMUNIT:
            batch.append( (rows[x].ID, r.ID) )
            break
# Run the batch update
dbo.execute_many("UPDATE animallocation SET PrevAnimalLocationID=? WHERE ID=?", batch, override_lock=True)