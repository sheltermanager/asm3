# Add owner.IsAdoptionCoordinator
add_column(dbo, "owner", "IsAdoptionCoordinator", "INTEGER")
execute(dbo,"UPDATE owner SET IsAdoptionCoordinator = 0")