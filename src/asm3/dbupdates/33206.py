# Add cost paid date fields
add_column(dbo, "animalcost", "CostPaidDate", dbo.type_datetime)
add_column(dbo, "animalmedical", "CostPaidDate", dbo.type_datetime)
add_column(dbo, "animaltest", "CostPaidDate", dbo.type_datetime)
add_column(dbo, "animalvaccination", "CostPaidDate", dbo.type_datetime)
add_index(dbo, "animalcost_CostPaidDate", "animalcost", "CostPaidDate")
add_index(dbo, "animalmedical_CostPaidDate", "animalmedical", "CostPaidDate")
add_index(dbo, "animaltest_CostPaidDate", "animaltest", "CostPaidDate")
add_index(dbo, "animalvaccination_CostPaidDate", "animalvaccination", "CostPaidDate")