# Make stock levels floating point numbers instead
modify_column(dbo, "stocklevel", "Total", dbo.type_float, "Total::real") 
modify_column(dbo, "stocklevel", "Balance", dbo.type_float, "Balance::real") 
modify_column(dbo, "stockusage", "Quantity", dbo.type_float, "Quantity::real") 