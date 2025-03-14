# Add SiteID to people and incidents
add_column(dbo, "owner", "SiteID", "INTEGER")
add_index(dbo, "owner_SiteID", "owner", "SiteID")
add_column(dbo, "animalcontrol", "SiteID", "INTEGER")
add_index(dbo, "animalcontrol_SiteID", "animalcontrol", "SiteID")
execute(dbo,"UPDATE owner SET SiteID = 0")
execute(dbo,"UPDATE animalcontrol SET SiteID = 0")