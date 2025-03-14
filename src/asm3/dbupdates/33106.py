# Add MatchColour
add_column(dbo, "owner", "MatchColour", "INTEGER")
execute(dbo,"UPDATE owner SET MatchColour = -1")