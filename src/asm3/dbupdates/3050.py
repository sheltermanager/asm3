# Add default cost for vaccinations
add_column(dbo, "vaccinationtype", "DefaultCost", "INTEGER")
# Add default adoption fee per species
add_column(dbo, "species", "AdoptionFee", "INTEGER")