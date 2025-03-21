# Add IsRetired to animal and person flags
add_column(dbo, "lkanimalflags", "IsRetired", dbo.type_integer)
add_column(dbo, "lkownerflags", "IsRetired", dbo.type_integer)
execute(dbo,"UPDATE lkanimalflags SET IsRetired=0")
execute(dbo,"UPDATE lkownerflags SET IsRetired=0")