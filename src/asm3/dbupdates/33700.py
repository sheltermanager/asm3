# Add account.CostTypeID
add_column(dbo, "accounts", "CostTypeID", "INTEGER")
add_index(dbo, "accounts_CostTypeID", "accounts", "CostTypeID")
# Add accountstrx.AnimalCostID
add_column(dbo, "accountstrx", "AnimalCostID", "INTEGER")
add_index(dbo, "accountstrx_AnimalCostID", "accountstrx", "AnimalCostID")
# Default values
execute(dbo,"UPDATE accounts SET CostTypeID = 0")
execute(dbo,"UPDATE accountstrx SET AnimalCostID = 0")