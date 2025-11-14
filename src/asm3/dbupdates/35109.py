from asm3.dbupdate import add_column

add_column(dbo, "animalvaccination", "BatchExpiryDate", dbo.type_datetime)
