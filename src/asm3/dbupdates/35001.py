from asm3.dbupdate import execute, add_column
dbo = dbo

# Add the new goodwith fields to looking for
add_column(dbo, "owner", "MatchCrateTrained", dbo.type_integer)
add_column(dbo, "owner", "MatchGoodWithElderly", dbo.type_integer)
add_column(dbo, "owner", "MatchGoodTraveller", dbo.type_integer)
add_column(dbo, "owner", "MatchGoodOnLead", dbo.type_integer)
add_column(dbo, "owner", "MatchEnergyLevel", dbo.type_integer)
execute(dbo, "UPDATE owner SET MatchCrateTrained=-1, MatchGoodWithElderly=-1, MatchGoodTraveller=-1, MatchGoodOnLead=-1, MatchEnergyLevel=-1")

