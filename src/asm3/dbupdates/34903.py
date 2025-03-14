# Add extra fields to facilitate invoice tracking to animalcost table
add_column(dbo, "animalcost", "OwnerID", dbo.type_integer)
add_index(dbo, "animalcost_OwnerID", "animalcost", "OwnerID")
add_column(dbo, "animalcost", "InvoiceNumber", dbo.type_shorttext)
add_index(dbo, "animalcost_InvoiceNumber", "animalcost", "InvoiceNumber")