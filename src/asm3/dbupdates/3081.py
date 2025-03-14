# Remove AdoptionFee field - it was a stupid idea to have with species
# put a defaultcost on donation type instead
drop_column(dbo, "species", "AdoptionFee")
add_column(dbo, "donationtype", "DefaultCost", "INTEGER")