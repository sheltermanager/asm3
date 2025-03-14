# Add owner.OwnerCountry, animaltransport.PickupCountry, animaltransport.DropoffCountry
add_column(dbo, "owner", "OwnerCountry", dbo.type_shorttext)
add_index(dbo, "owner_OwnerCountry", "owner", "OwnerCountry")
add_column(dbo, "animaltransport", "PickupCountry", dbo.type_shorttext)
add_column(dbo, "animaltransport", "DropoffCountry", dbo.type_shorttext)
execute(dbo,"UPDATE owner SET OwnerCountry=''")
execute(dbo,"UPDATE animaltransport SET PickupCountry='', DropoffCountry=''")