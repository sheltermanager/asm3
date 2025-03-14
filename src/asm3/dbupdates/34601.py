# Add cost per treatment fields
add_column(dbo, "animalmedical", "CostPerTreatment", dbo.type_integer)
add_column(dbo, "medicalprofile", "CostPerTreatment", dbo.type_integer)
execute(dbo,"UPDATE animalmedical SET CostPerTreatment=0")
execute(dbo,"UPDATE medicalprofile SET CostPerTreatment=0")