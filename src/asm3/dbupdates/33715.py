# Add owner.FosterCapacity field
add_column(dbo, "owner", "FosterCapacity", "INTEGER")
execute(dbo,"UPDATE owner SET FosterCapacity=0")
execute(dbo,"UPDATE owner SET FosterCapacity=1 WHERE IsFosterer=1")